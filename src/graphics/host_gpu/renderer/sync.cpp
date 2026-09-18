#include "graphics/host_gpu/renderer/sync.h"

#include "common/assert.h"
#include "common/common.h"
#include "common/frameStats.h"
#include "common/logging/log.h"
#include "common/threads.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/presentation/videoOut.h"
#include "kernel/eventQueue.h"
#include "kernel/pthread.h"
#include "libs/errno.h"

#include <cstdlib>
#include <cstring>
#include <limits>

namespace Libs::Graphics::Sync {

constexpr uint64_t GRAPHICS_REFERENCE_CLOCK_FREQUENCY = 100000000;

bool ScaleReferenceClock(uint64_t host_ticks, uint64_t host_frequency, uint64_t& value) {
	if (host_frequency == 0) {
		return false;
	}

	const auto     whole_seconds = host_ticks / host_frequency;
	const auto     remainder     = host_ticks % host_frequency;
	constexpr auto MAX_VALUE     = std::numeric_limits<uint64_t>::max();
	if (whole_seconds > MAX_VALUE / GRAPHICS_REFERENCE_CLOCK_FREQUENCY ||
	    remainder > MAX_VALUE / GRAPHICS_REFERENCE_CLOCK_FREQUENCY) {
		return false;
	}

	const auto whole_value      = whole_seconds * GRAPHICS_REFERENCE_CLOCK_FREQUENCY;
	const auto fractional_value = (remainder * GRAPHICS_REFERENCE_CLOCK_FREQUENCY) / host_frequency;
	if (whole_value > MAX_VALUE - fractional_value) {
		return false;
	}
	value = whole_value + fractional_value;
	return true;
}

// Session 91, MEASUREMENT ONLY (PLAN s91 section 0 A, route P).  The game's dynamic resolution
// is PREDICTED (pred/02_pin.md) to budget against the GPU timestamps this function produces,
// which are the pacer-scaled TSC read at PM4 parse on the GuestGpu thread - so a CPU-side knob
// can move the DRS rung.  KYTY_GPU_CLOCK_PIN changes the rate of THIS clock only (freezes stay
// excluded; CPU clocks, flip and vblank stamps keep the pacer):
//   1 = the pacer speed is dropped: every guest GPU span grows by 1/speed (~2x); the rung is
//       predicted to stay on its lowest step;
//   2 = POSITIVE CONTROL: the scaled clock at half rate; spans shrink 2x; the rung is predicted
//       to climb.
// Read ONCE per process: switching mid-run would break the clock's monotonicity, so it can
// never be a schedule arm.  Arming is proved by VALUE: gclk_adv / gclk_sadv (the guest
// clock's advance over the scaled clock's between consecutive reads on one thread) is 1/speed
// at 1 and 0.5 at 2; gclk_back counts backward steps.  None of the three is Added at 0.
static uint32_t GpuClockPinMode() {
	static const uint32_t mode = [] {
		const char*    value = std::getenv("KYTY_GPU_CLOCK_PIN");
		const int      v     = value != nullptr ? std::atoi(value) : 0;
		const uint32_t m     = (v == 1 || v == 2) ? static_cast<uint32_t>(v) : 0u;
		if (m != 0) {
			LOGF("GpuClockPin: mode %u - the guest GPU clock %s (KYTY_GPU_CLOCK_PIN)" "\n", m,
			     m == 1 ? "ignores the pacer speed" : "runs at half the scaled rate");
		}
		return m;
	}();
	return mode;
}

uint64_t ReadReferenceClock() {
	const auto     host_frequency = LibKernel::KernelGetTscFrequency();
	const uint32_t pin            = GpuClockPinMode();
	const auto     scaled_ticks   = LibKernel::KernelReadTsc();
	const auto     host_ticks     = pin == 1   ? LibKernel::KernelReadTscBase()
	                                : pin == 2 ? scaled_ticks / 2
	                                           : scaled_ticks;
	Common::FrameStats::Add(Common::FrameStats::Counter::GpuClockReads, 1);
	if (pin != 0) {
		Common::FrameStats::Add(Common::FrameStats::Counter::GpuClockPinnedReads, 1);
		thread_local uint64_t t_last_host   = 0;
		thread_local uint64_t t_last_scaled = 0;
		if (t_last_host != 0) {
			if (host_ticks < t_last_host) {
				Common::FrameStats::Add(Common::FrameStats::Counter::GpuClockBackward, 1);
			} else if (scaled_ticks >= t_last_scaled) {
				Common::FrameStats::Add(Common::FrameStats::Counter::GpuClockAdvance, host_ticks - t_last_host);
				Common::FrameStats::Add(Common::FrameStats::Counter::GpuClockScaledAdvance, scaled_ticks - t_last_scaled);
			}
		}
		t_last_host   = host_ticks;
		t_last_scaled = scaled_ticks;
	}
	uint64_t value = 0;
	if (!ScaleReferenceClock(host_ticks, host_frequency, value)) {
		EXIT("cannot scale host clock, ticks=0x%016" PRIx64 " frequency=%" PRIu64 "\n", host_ticks,
		     host_frequency);
	}
	return value;
}

enum class EndOfPipeWriteSize : uint32_t { Dword = 4, Qword = 8 };
enum class EndOfPipeWriteAction { Write, WriteBack, Interrupt, InterruptWriteBack };

static CommandBufferDebugOp DebugOperation(EndOfPipeWriteAction action) {
	switch (action) {
		case EndOfPipeWriteAction::Write: return CommandBufferDebugOp::EopWrite;
		case EndOfPipeWriteAction::WriteBack:
		case EndOfPipeWriteAction::InterruptWriteBack: return CommandBufferDebugOp::EopWriteBack;
		case EndOfPipeWriteAction::Interrupt: return CommandBufferDebugOp::EopInterrupt;
	}
	EXIT("unsupported end-of-pipe write action\n");
	return CommandBufferDebugOp::Unknown;
}

static bool TriggersInterrupt(EndOfPipeWriteAction action) {
	return action == EndOfPipeWriteAction::Interrupt ||
	       action == EndOfPipeWriteAction::InterruptWriteBack;
}

static void RecordEndOfPipeWrite(uint64_t submit_id, CommandBuffer& buffer, uint64_t destination,
                                 uint64_t value, EndOfPipeWriteSize size,
                                 EndOfPipeWriteAction action, int interrupt_event_id = 0,
                                 uint32_t context_id = 0) {
	EXIT_IF(destination == 0);
	buffer.NoteHandleUse();

	const auto width      = static_cast<uint32_t>(size);
	const auto value_low  = static_cast<uint32_t>(value);
	const auto value_high = static_cast<uint32_t>(value >> 32u);
	const auto operation  = static_cast<uint32_t>(DebugOperation(action));
	if (TriggersInterrupt(action)) {
		buffer.SetDebugInfo(operation, submit_id, width, context_id, value_low, value_high,
		                    destination);
		TriggerEopEventAtEndOfPipe(buffer, interrupt_event_id, context_id);
	} else {
		buffer.SetDebugInfo(operation, submit_id, width, value_low, value_high, 0, destination);
	}
}

void WriteAtEndOfPipe32(uint64_t submit_id, CommandBuffer& buffer, uint32_t* dst_gpu_addr,
                        uint32_t value) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), value,
	                     EndOfPipeWriteSize::Dword, EndOfPipeWriteAction::Write);
}

void WriteAtEndOfPipeGds32(uint64_t submit_id, CommandBuffer& buffer, uint32_t* dst_gpu_addr,
                           uint32_t dw_offset, uint32_t dw_num) {
	EXIT_IF(dst_gpu_addr == nullptr);
	buffer.NoteHandleUse();
	buffer.SetDebugInfo(static_cast<uint32_t>(CommandBufferDebugOp::EopWrite), submit_id,
	                    dw_offset, dw_num, 0, 0, reinterpret_cast<uint64_t>(dst_gpu_addr));
}

void WriteAtEndOfPipe64(uint64_t submit_id, CommandBuffer& buffer, uint64_t* dst_gpu_addr,
                        uint64_t value) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), value,
	                     EndOfPipeWriteSize::Qword, EndOfPipeWriteAction::Write);
}

void WriteAtEndOfPipeClockCounter(uint64_t submit_id, CommandBuffer& buffer, uint64_t* dst_gpu_addr,
                                  uint64_t value) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), 0,
	                     EndOfPipeWriteSize::Qword, EndOfPipeWriteAction::Write);

	LOGV_COLOR(Log::Color::BrightGreen,
	           "EndOfPipe Signal!!! [0x%016" PRIx64 "] <- Clock: 0x%016" PRIx64 "\n",
	           reinterpret_cast<uint64_t>(dst_gpu_addr), value);
}

void WriteAtEndOfPipeClockCounterWithWriteBack(uint64_t submit_id, CommandBuffer& buffer,
                                               uint64_t* dst_gpu_addr, uint64_t value) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), 0,
	                     EndOfPipeWriteSize::Qword, EndOfPipeWriteAction::WriteBack);

	LOGV_COLOR(Log::Color::BrightGreen,
	           "EndOfPipe Signal!!! [0x%016" PRIx64 "] <- Clock: 0x%016" PRIx64 "\n",
	           reinterpret_cast<uint64_t>(dst_gpu_addr), value);
}

void WriteAtEndOfPipeWithWriteBack64(uint64_t submit_id, CommandBuffer& buffer,
                                     uint64_t* dst_gpu_addr, uint64_t value) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), value,
	                     EndOfPipeWriteSize::Qword, EndOfPipeWriteAction::WriteBack);
}

void WriteAtEndOfPipeWithWriteBack32(uint64_t submit_id, CommandBuffer& buffer,
                                     uint32_t* dst_gpu_addr, uint32_t value) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), value,
	                     EndOfPipeWriteSize::Dword, EndOfPipeWriteAction::WriteBack);
}

void WriteAtEndOfPipeWithInterruptWriteBack64(uint64_t submit_id, CommandBuffer& buffer,
                                              uint64_t* dst_gpu_addr, uint64_t value, int event_id,
                                              uint32_t context_id) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), value,
	                     EndOfPipeWriteSize::Qword, EndOfPipeWriteAction::InterruptWriteBack,
	                     event_id, context_id);
}

void WriteAtEndOfPipeWithInterruptWriteBack32(uint64_t submit_id, CommandBuffer& buffer,
                                              uint32_t* dst_gpu_addr, uint32_t value, int event_id,
                                              uint32_t context_id) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), value,
	                     EndOfPipeWriteSize::Dword, EndOfPipeWriteAction::InterruptWriteBack,
	                     event_id, context_id);
}

void WriteAtEndOfPipeWithInterrupt64(uint64_t submit_id, CommandBuffer& buffer,
                                     uint64_t* dst_gpu_addr, uint64_t value, int event_id,
                                     uint32_t context_id) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), value,
	                     EndOfPipeWriteSize::Qword, EndOfPipeWriteAction::Interrupt, event_id,
	                     context_id);
}

void WriteAtEndOfPipeWithInterrupt32(uint64_t submit_id, CommandBuffer& buffer,
                                     uint32_t* dst_gpu_addr, uint32_t value, int event_id,
                                     uint32_t context_id) {
	RecordEndOfPipeWrite(submit_id, buffer, reinterpret_cast<uint64_t>(dst_gpu_addr), value,
	                     EndOfPipeWriteSize::Dword, EndOfPipeWriteAction::Interrupt, event_id,
	                     context_id);
}

uint64_t PrepareVideoOutFlip(CommandBuffer& buffer, int handle, int index, int flip_mode,
                             int64_t flip_arg) {
	for (;;) {
		uint64_t   request_id = 0;
		auto&      video_out  = buffer.GetContext().GetVideoOut();
		const auto result =
		    video_out.SubmitFlipFromGpu(buffer, handle, index, flip_mode, flip_arg, request_id);
		if (result == OK) {
			EXIT_IF(request_id == 0);
			return request_id;
		}
		if (result != VideoOut::VIDEO_OUT_ERROR_FLIP_QUEUE_FULL) {
			EXIT("GPU flip submission failed, result=%d handle=%d index=%d mode=%d arg=%" PRId64
			     "\n",
			     result, handle, index, flip_mode, flip_arg);
		}
		video_out.WaitForSubmitSlot();
	}
}

void WriteAtEndOfPipeWithInterruptWriteBackFlip32(uint64_t submit_id, CommandBuffer& buffer,
                                                  uint32_t* dst_gpu_addr, uint32_t value,
                                                  int handle, int index, int flip_mode,
                                                  int64_t flip_arg, uint64_t request_id,
                                                  int event_id) {
	EXIT_IF(dst_gpu_addr == nullptr);
	buffer.NoteHandleUse();
	buffer.SetDebugInfo(static_cast<uint32_t>(CommandBufferDebugOp::EopWriteBackFlip), submit_id,
	                    static_cast<uint32_t>(handle), static_cast<uint32_t>(index),
	                    static_cast<uint32_t>(flip_mode), value, static_cast<uint64_t>(flip_arg));

	auto& renderer  = buffer.GetContext();
	auto& scheduler = renderer.GetCommandScheduler();
	EXIT_IF(!scheduler.Active() || &buffer != &scheduler.Current());
	scheduler.DeferPriorityOperation([&renderer, event_id, request_id] {
		renderer.GetVideoOut().CompleteFlip(request_id);
		renderer.TriggerInterrupt(event_id, 0);
	});
}

void WriteAtEndOfPipeWithFlip32(uint64_t submit_id, CommandBuffer& buffer, uint32_t* dst_gpu_addr,
                                uint32_t value, int handle, int index, int flip_mode,
                                int64_t flip_arg, uint64_t request_id) {
	EXIT_IF(dst_gpu_addr == nullptr);
	buffer.NoteHandleUse();
	buffer.SetDebugInfo(static_cast<uint32_t>(CommandBufferDebugOp::EopFlip), submit_id,
	                    static_cast<uint32_t>(handle), static_cast<uint32_t>(index),
	                    static_cast<uint32_t>(flip_mode), value, static_cast<uint64_t>(flip_arg));

	auto& renderer  = buffer.GetContext();
	auto& scheduler = renderer.GetCommandScheduler();
	EXIT_IF(!scheduler.Active() || &buffer != &scheduler.Current());
	scheduler.DeferPriorityOperation(
	    [&renderer, request_id] { renderer.GetVideoOut().CompleteFlip(request_id); });
}

void WriteAtEndOfPipeOnlyFlip(uint64_t submit_id, CommandBuffer& buffer, int handle, int index,
                              int flip_mode, int64_t flip_arg, uint64_t request_id) {
	buffer.NoteHandleUse();
	buffer.SetDebugInfo(static_cast<uint32_t>(CommandBufferDebugOp::EopOnlyFlip), submit_id,
	                    static_cast<uint32_t>(handle), static_cast<uint32_t>(index),
	                    static_cast<uint32_t>(flip_mode), 0, static_cast<uint64_t>(flip_arg));

	auto& renderer  = buffer.GetContext();
	auto& scheduler = renderer.GetCommandScheduler();
	EXIT_IF(!scheduler.Active() || &buffer != &scheduler.Current());
	scheduler.DeferPriorityOperation(
	    [&renderer, request_id] { renderer.GetVideoOut().CompleteFlip(request_id); });
}

void TriggerEopEventAtEndOfPipe(CommandBuffer& buffer, int event_id, uint32_t context_id) {
	buffer.NoteHandleUse();
	auto& renderer  = buffer.GetContext();
	auto& scheduler = renderer.GetCommandScheduler();
	EXIT_IF(!scheduler.Active() || &buffer != &scheduler.Current());
	scheduler.DeferPriorityOperation(
	    [&renderer, event_id, context_id] { renderer.TriggerInterrupt(event_id, context_id); });
}

static void InterruptEventResetFunc(LibKernel::EventQueue::KernelEqueueEvent* event) {
	EXIT_IF(event == nullptr);
	event->triggered    = false;
	event->event.fflags = 0;
	event->event.data   = 0;
}

static void InterruptEventTriggerFunc(LibKernel::EventQueue::KernelEqueueEvent* event,
                                      void*                                     trigger_data) {
	EXIT_IF(event == nullptr);

	auto triggered_event = event->event;
	triggered_event.fflags++;
	triggered_event.data = reinterpret_cast<intptr_t>(trigger_data);
	if (event->triggered) {
		event->pending_events.push_back(triggered_event);
	} else {
		event->event     = triggered_event;
		event->triggered = true;
	}
}

int AddEqEvent(RenderContext& renderer, LibKernel::EventQueue::KernelEqueue eq, int id,
               void* udata) {
	LibKernel::EventQueue::KernelEqueueEvent event;
	event.triggered           = false;
	event.event.ident         = static_cast<uintptr_t>(id);
	event.event.filter        = LibKernel::EventQueue::KERNEL_EVFILT_GRAPHICS;
	event.event.udata         = udata;
	event.event.fflags        = 0;
	event.event.data          = id;
	event.filter.reset_func   = InterruptEventResetFunc;
	event.filter.trigger_func = InterruptEventTriggerFunc;

	int result = LibKernel::EventQueue::KernelAddEvent(eq, event);

	if (result == 0) {
		renderer.AddInterruptEq(eq, id);
	}

	return result;
}

int DeleteEqEvent(RenderContext& renderer, LibKernel::EventQueue::KernelEqueue eq, int id) {
	int result = LibKernel::EventQueue::KernelDeleteEvent(
	    eq, static_cast<uintptr_t>(id), LibKernel::EventQueue::KERNEL_EVFILT_GRAPHICS);
	if (result == OK || result == LibKernel::KERNEL_ERROR_ENOENT) {
		renderer.DeleteInterruptEq(eq, id);
	}

	return result;
}

void ReadGds(const Buffer& gds, uint32_t* dst, uint32_t dw_offset, uint32_t dw_size) {
	const auto offset = uint64_t {dw_offset} * sizeof(uint32_t);
	const auto size   = uint64_t {dw_size} * sizeof(uint32_t);
	EXIT_IF(dst == nullptr || offset > gds.Size() || size > gds.Size() - offset ||
	        gds.Mapped().empty());
	std::memcpy(dst, gds.Mapped().data() + offset, static_cast<size_t>(size));
}

} // namespace Libs::Graphics::Sync
