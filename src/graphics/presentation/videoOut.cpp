#include "graphics/presentation/videoOut.h"

#include "common/abi.h"
#include "common/diagB32.h"
#include "common/assert.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/common.h"
#include "common/emulatorConfig.h"
#include "common/envFlag.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "common/stringUtils.h"
#include "common/threads.h"
#include "common/timer.h"
#include "graphics/guest_gpu/gpu_defs.h"
#include "graphics/guest_gpu/graphicsRun.h"
#include "graphics/guest_gpu/tile.h"
#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"
#include "graphics/host_gpu/renderer/diagF5.h"
#include "graphics/host_gpu/renderer/image/imageInfo.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/presentation/presenter.h"
#include "graphics/presentation/renderDoc.h"
#include "kernel/pthread.h"
#include "kernel/pvar.h"
#include "libs/errno.h"
#include "libs/libs.h"

#include <algorithm>
#include <array>
#include <string>
#include <list>
#include <thread>
#include <vector>

namespace Libs::Graphics {
struct GraphicContext;
} // namespace Libs::Graphics

namespace Libs::VideoOut {

LIB_NAME("VideoOut", "VideoOut");

namespace EventQueue = LibKernel::EventQueue;

constexpr int      VIDEO_OUT_EVENT_FLIP                                 = 0;
constexpr int      VIDEO_OUT_EVENT_VBLANK                               = 1;
constexpr int      VIDEO_OUT_EVENT_PRE_VBLANK_START                     = 2;
constexpr int      VIDEO_OUT_EVENT_SET_MODE                             = 8;
constexpr int      VIDEO_OUT_TRUE                                       = 1;
constexpr int      VIDEO_OUT_FALSE                                      = 0;
constexpr int      VIDEO_OUT_BUS_TYPE_MAIN                              = 0;
constexpr int      VIDEO_OUT_BUS_TYPE_OVERLAY                           = 1;
constexpr int      VIDEO_OUT_BUS_TYPE_SUB                               = 2;
constexpr int      VIDEO_OUT_FLIP_MODE_VSYNC                            = 1;
constexpr int      VIDEO_OUT_FLIP_MODE_VSYNC_MULTI                      = 4;
constexpr int      VIDEO_OUT_BUFFER_INDEX_BLACK                         = -2;
constexpr int      VIDEO_OUT_BUFFER_INDEX_BLANK                         = -1;
constexpr int      VIDEO_OUT_BUFFER_NUM_MAX                             = 16;
constexpr size_t   VIDEO_OUT_FLIP_QUEUE_CAPACITY                        = 16;
constexpr int      VIDEO_OUT_BUFFER_ATTRIBUTE_NUM_MAX                   = 4;
constexpr uint64_t VIDEO_OUT_OUTPUT_MODE_DEFAULT                        = 0x0000000000000001ULL;
constexpr uint64_t VIDEO_OUT_OUTPUT_MODE_119_88HZ                       = 0x000000000000000FULL;
constexpr uint64_t VIDEO_OUT_REFRESH_RATE_59_94HZ                       = 3;
constexpr uint64_t VIDEO_OUT_REFRESH_RATE_119_88HZ                      = 13;
constexpr int      VIDEO_OUT_BUFFER_ATTRIBUTE_CATEGORY_UNCOMPRESSED     = 0;
constexpr int      VIDEO_OUT_BUFFER_ATTRIBUTE_CATEGORY_COMPRESSED       = 1;
constexpr uint64_t VIDEO_OUT_BUFFER_ATTRIBUTE_OPTION_STRICT_COLORIMETRY = 8;

enum class VideoOutEventKind : uintptr_t {
	Flip           = VIDEO_OUT_EVENT_FLIP,
	Vblank         = VIDEO_OUT_EVENT_VBLANK,
	PreVblankStart = VIDEO_OUT_EVENT_PRE_VBLANK_START,
	OutputMode     = VIDEO_OUT_EVENT_SET_MODE,
};

enum class FlipRequestSource { Cpu, GpuEop };

struct VideoOutEventState;

struct VideoOutEventRegistration {
	EventQueue::KernelEqueue            handle = EventQueue::KERNEL_EQUEUE_INVALID;
	std::shared_ptr<VideoOutEventState> state;
	uint64_t                            generation = 0;
	VideoOutEventKind                   kind       = VideoOutEventKind::Flip;
};

using VideoOutEventRegistrationRef = std::shared_ptr<VideoOutEventRegistration>;
using VideoOutEventQueues          = std::vector<VideoOutEventRegistrationRef>;

struct VideoOutEventState {
	Common::Mutex       mutex;
	VideoOutEventQueues flip;
	VideoOutEventQueues pre_vblank;
	VideoOutEventQueues vblank;
	VideoOutEventQueues output_mode;
};

struct VideoOutBufferAttribute2 {
	uint32_t reserved0;
	uint32_t tiling_mode;
	uint32_t aspect_ratio;
	uint32_t width;
	uint32_t height;
	uint32_t pitch_in_pixel;
	uint64_t option;
	uint64_t pixel_format;
	uint64_t dcc_cb_register_clear_color;
	uint32_t dcc_control;
	uint32_t pad0;
	uint64_t reserved1[3];
};

// PS5 layout
struct VideoOutFlipStatus {
	uint64_t count                    = 0;
	uint64_t processTime              = 0;
	uint64_t reserved0                = 0;
	int64_t  flipArg                  = 0;
	uint64_t reserved1                = 0;
	uint64_t processTimeCounter       = 0;
	int32_t  gcQueueNum               = 0;
	int32_t  flipPendingNum           = 0;
	int32_t  currentBuffer            = 0;
	uint32_t reserved2                = 0;
	uint64_t submitProcessTimeCounter = 0;
	uint64_t reserved3[7]             = {};
};

// PS5 layout
struct VideoOutVblankStatus {
	uint64_t count              = 0;
	uint64_t processTime        = 0;
	uint64_t reserved           = 0;
	uint64_t processTimeCounter = 0;
	uint8_t  flags              = 0;
	uint8_t  phase              = 0;
	uint8_t  pad1[6]            = {};
};

struct VideoOutOutputStatus {
	uint32_t resolution   = 0;
	uint32_t dynamicRange = 0;
	uint64_t refreshRate  = 0;
	uint64_t flags        = 0;
	uint64_t reserved[3]  = {};
};

struct VideoOutOutputOptions {
	uint32_t internalData[16] = {};
};

struct VideoOutColorSettings {
	float    gamma       = 1.0f;
	uint32_t reserved[3] = {};
};

struct VideoOutBuffers {
	const void* data;
	const void* metadata;
	const void* reserved[2];
};

struct VideoOutBuffer {
	int      group_index      = -1;
	uint64_t data_address     = 0;
	uint64_t metadata_address = 0;

	[[nodiscard]] bool Occupied() const noexcept { return group_index >= 0; }
};

struct BufferAttributeGroup {
	VideoOutBufferAttribute2 attribute {};
	int                      category = VIDEO_OUT_BUFFER_ATTRIBUTE_CATEGORY_UNCOMPRESSED;
	bool                     occupied = false;

	[[nodiscard]] Graphics::ImageInfo ImageInfo(const VideoOutBuffer& buffer) const;
};

struct VideoOutConfig {
	Common::Mutex                       mutex;
	Common::CondVar                     vblank_cond;
	std::shared_ptr<VideoOutEventState> events      = std::make_shared<VideoOutEventState>();
	uint32_t                            width       = 0;
	uint32_t                            height      = 0;
	uint64_t                            generation  = 0;
	bool                                opened      = false;
	bool                                closing     = false;
	int                                 flip_rate   = 0;
	uint64_t                            pace_last_base_us = 0;
	double                              pace_ema_us       = 0.0;
	double                              pace_speed        = 1.0;
	uint64_t                            output_mode = VIDEO_OUT_OUTPUT_MODE_DEFAULT;
	float                               gamma       = 1.0f;
	VideoOutFlipStatus                  flip_status;
	VideoOutVblankStatus                pre_vblank_status;
	VideoOutVblankStatus                vblank_status;
	std::array<VideoOutBuffer, VIDEO_OUT_BUFFER_NUM_MAX>                 buffers;
	std::array<BufferAttributeGroup, VIDEO_OUT_BUFFER_ATTRIBUTE_NUM_MAX> groups;
};

class FlipQueue {
public:
	explicit FlipQueue(Graphics::Presenter& presenter): m_presenter(presenter) {
		EXIT_NOT_IMPLEMENTED(!Common::Thread::IsMainThread());
	}
	~FlipQueue();
	KYTY_CLASS_NO_COPY(FlipQueue);

	bool Reserve(VideoOutConfig& cfg, int index, int64_t flip_arg, FlipRequestSource source,
	             uint64_t& request_id);
	void Cancel(VideoOutConfig& cfg);
	void Prepare(uint64_t request_id, Graphics::CommandBuffer& buffer);
	void Complete(uint64_t request_id);
	void WaitForSubmitSlot();
	void MarkIncomplete(uint64_t request_id);
	[[nodiscard]] bool MarkSkipCeil(uint64_t request_id);
	bool Flip(uint32_t micros);
	void GetFlipStatus(VideoOutConfig& cfg, VideoOutFlipStatus& out);
	void Wait(VideoOutConfig& cfg, int index);

private:
	enum class RequestState { Reserved, Recording, Ready, Presenting };

	struct Request {
		uint64_t                    id;
		VideoOutConfig*             cfg;
		uint64_t                    generation;
		int                         index;
		int64_t                     flip_arg;
		uint64_t                    submit_ptc;
		uint64_t                    reserve_host_ns;
		FlipRequestSource           source;
		RequestState                state;
		Graphics::Presenter::Frame* frame;
		bool                        incomplete = false;
		bool                        skip_ceil  = false; // Session 123, knob "skipceil" = 1: held whatever KYTY_ASYNC_HOLD_FRAME
	};

	Graphics::Presenter& m_presenter;
	Common::Mutex        m_mutex;
	Common::CondVar      m_submit_cond_var;
	Common::CondVar      m_submit_slot_cond_var;
	Common::CondVar      m_done_cond_var;
	std::list<Request>   m_requests;
	std::list<Request>   m_cpu_requests;
	std::list<Request>   m_cancelled_requests;
	bool                 m_processing      = false;
	uint64_t             m_next_request_id = 1;
};

struct VideoOutDriver::Impl {
public:
	static constexpr std::array VIDEO_OUT_BUSES {
	    VIDEO_OUT_BUS_TYPE_MAIN, VIDEO_OUT_BUS_TYPE_OVERLAY, VIDEO_OUT_BUS_TYPE_SUB};
	static constexpr int VIDEO_OUT_NUM_MAX = VIDEO_OUT_BUSES.size() + 1;

	Impl(uint32_t width, uint32_t height, Graphics::Presenter& presenter)
	    : m_renderer(presenter.Renderer()), m_presenter(presenter), m_flip_queue(presenter) {
		EXIT_NOT_IMPLEMENTED(!Common::Thread::IsMainThread());
		Init(width, height);
		m_present_thread = std::jthread([this](std::stop_token token) { PresentThread(token); });
	}
	~Impl();
	KYTY_CLASS_NO_COPY(Impl);

	int             Open(int bus_type, int index);
	bool            Close(int handle);
	VideoOutConfig* Get(int handle);
	VideoOutConfig* Get(int handle, uint64_t& generation);
	bool            IsOpened(int handle);

	void                     Init(uint32_t width, uint32_t height);
	FlipQueue&               GetFlipQueue() { return m_flip_queue; }
	Graphics::RenderContext& Renderer() const noexcept { return m_renderer; }

	void VblankBegin();
	void VblankEnd();
	void PresentThread(std::stop_token token);

private:
	Common::Mutex            m_mutex;
	VideoOutConfig           m_video_out_ctx[VIDEO_OUT_NUM_MAX];
	Graphics::RenderContext& m_renderer;
	Graphics::Presenter&     m_presenter;
	FlipQueue                m_flip_queue;
	std::jthread             m_present_thread;
};

static std::unique_ptr<VideoOutDriver> g_video_out_driver;

static VideoOutDriver::Impl& DriverState() {
	EXIT_IF(g_video_out_driver == nullptr);
	return g_video_out_driver->State();
}

static uintptr_t VideoOutEventId(VideoOutEventKind kind) {
	return static_cast<uintptr_t>(kind);
}

static VideoOutEventQueues& VideoOutEventQueuesFor(VideoOutEventState& state,
                                                   VideoOutEventKind   kind) {
	switch (kind) {
		case VideoOutEventKind::Flip: return state.flip;
		case VideoOutEventKind::Vblank: return state.vblank;
		case VideoOutEventKind::PreVblankStart: return state.pre_vblank;
		case VideoOutEventKind::OutputMode: return state.output_mode;
	}
	EXIT("unsupported video-out event kind\n");
	return state.flip;
}

static intptr_t MakeVideoOutEventData(intptr_t current_data, void* trigger_data) {
	const uint64_t old_data = static_cast<uint64_t>(current_data);
	uint64_t       counter  = (old_data >> 12u) & 0xfu;
	if (counter != 0xfu) {
		counter++;
	}

	const uint64_t time    = LibKernel::KernelReadTsc() & 0xfffu;
	const uint64_t payload = static_cast<uint64_t>(reinterpret_cast<intptr_t>(trigger_data));

	return static_cast<intptr_t>(time | (counter << 12u) |
	                             ((payload & 0x0000ffffffffffffULL) << 16u));
}

static void ResetVideoOutEvent(EventQueue::KernelEqueueEvent* event) {
	EXIT_IF(event == nullptr);
	event->triggered    = false;
	event->event.fflags = 0;
	event->event.data   = 0;
}

static void TriggerVideoOutEvent(EventQueue::KernelEqueueEvent* event, void* trigger_data) {
	EXIT_IF(event == nullptr);

	auto triggered_event = event->event;
	triggered_event.fflags =
	    triggered_event.fflags < 0xfu ? triggered_event.fflags + 1u : triggered_event.fflags;
	triggered_event.data = MakeVideoOutEventData(triggered_event.data, trigger_data);
	if (event->triggered) {
		event->pending_events.push_back(triggered_event);
		return;
	}
	event->event     = triggered_event;
	event->triggered = true;
}

static void RemoveVideoOutEventQueue(EventQueue::KernelEqueue       eq,
                                     EventQueue::KernelEqueueEvent* event) {
	if (event == nullptr || event->filter.data == nullptr) {
		return;
	}

	auto* registration = static_cast<VideoOutEventRegistration*>(event->filter.data);
	auto  state        = registration->state;
	if (registration->handle != eq || !state) {
		return;
	}
	auto&             queues = VideoOutEventQueuesFor(*state, registration->kind);
	Common::LockGuard lock(state->mutex);
	const auto        entry =
	    std::find_if(queues.begin(), queues.end(), [registration](const auto& candidate) {
		    return candidate.get() == registration;
	    });
	if (entry != queues.end()) {
		queues.erase(entry);
	}
}

static void TriggerVideoOutEvents(VideoOutConfig& video_out, VideoOutEventKind kind,
                                  void* trigger_data) {
	VideoOutEventQueues queues;
	{
		Common::LockGuard lock(video_out.events->mutex);
		queues = VideoOutEventQueuesFor(*video_out.events, kind);
	}
	for (const auto& registration: queues) {
		if (!registration || registration->generation != video_out.generation) {
			continue;
		}
		const auto result =
		    EventQueue::KernelTriggerEvent(registration->handle, VideoOutEventId(kind),
		                                   EventQueue::KERNEL_EVFILT_VIDEO_OUT, trigger_data);
		EXIT_NOT_IMPLEMENTED(result != OK && result != LibKernel::KERNEL_ERROR_EBADF &&
		                     result != LibKernel::KERNEL_ERROR_ENOENT);
	}
}

static void DeleteVideoOutEvents(const VideoOutEventQueues& queues, VideoOutEventKind kind) {
	for (const auto& registration: queues) {
		if (!registration) {
			continue;
		}
		const auto result = EventQueue::KernelDeleteEvent(
		    registration->handle, VideoOutEventId(kind), EventQueue::KERNEL_EVFILT_VIDEO_OUT);
		EXIT_NOT_IMPLEMENTED(result != OK && result != LibKernel::KERNEL_ERROR_EBADF &&
		                     result != LibKernel::KERNEL_ERROR_ENOENT);
	}
}

static int RegisterVideoOutEvent(int handle, EventQueue::KernelEqueue eq, VideoOutEventKind kind,
                                 void* udata) {
	uint64_t generation = 0;
	auto*    video_out  = DriverState().Get(handle, generation);
	if (video_out == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	Common::LockGuard lock(video_out->mutex);
	if (!video_out->opened || video_out->closing || video_out->generation != generation) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}
	if (kind == VideoOutEventKind::OutputMode) {
		LOGF("\t eq     = 0x%016" PRIx64 "\n"
		     "\t handle = %d\n"
		     "\t udata  = 0x%016" PRIx64 "\n",
		     static_cast<uint64_t>(eq), handle, reinterpret_cast<uint64_t>(udata));
	}
	if (eq == EventQueue::KERNEL_EQUEUE_INVALID) {
		return VIDEO_OUT_ERROR_INVALID_EVENT_QUEUE;
	}
	if (!EventQueue::KernelPinEqueue(eq)) {
		return VIDEO_OUT_ERROR_INVALID_EVENT_QUEUE;
	}
	auto        event_state         = video_out->events;
	auto&       queues              = VideoOutEventQueuesFor(*event_state, kind);
	const bool  initially_triggered = kind == VideoOutEventKind::OutputMode;
	void* const initial_trigger_data =
	    initially_triggered ? reinterpret_cast<void*>(video_out->output_mode) : nullptr;

	EventQueue::KernelEqueueEvent event {};
	event.triggered    = initially_triggered;
	event.event.ident  = VideoOutEventId(kind);
	event.event.filter = EventQueue::KERNEL_EVFILT_VIDEO_OUT;
	event.event.udata  = udata;
	event.event.fflags = initially_triggered ? 1u : 0u;
	event.event.data   = initially_triggered ? MakeVideoOutEventData(0, initial_trigger_data) : 0;
	event.filter.delete_event_func = RemoveVideoOutEventQueue;
	event.filter.reset_func        = ResetVideoOutEvent;
	event.filter.trigger_func      = TriggerVideoOutEvent;

	VideoOutEventRegistrationRef registration;
	bool                         add_queue = false;
	{
		Common::LockGuard event_lock(event_state->mutex);
		const auto        existing =
		    std::find_if(queues.begin(), queues.end(), [&](const auto& candidate) {
			    return candidate->handle == eq && candidate->generation == generation;
		    });
		if (existing != queues.end()) {
			registration = *existing;
		} else {
			registration = std::make_shared<VideoOutEventRegistration>(VideoOutEventRegistration {
			    .handle = eq, .state = event_state, .generation = generation, .kind = kind});
			queues.push_back(registration);
			add_queue = true;
		}
	}
	event.filter.data  = registration.get();
	event.filter.owner = registration;
	const int result   = EventQueue::KernelAddEvent(eq, event);
	if (result != OK && add_queue) {
		Common::LockGuard event_lock(event_state->mutex);
		const auto        added = std::find(queues.begin(), queues.end(), registration);
		if (added != queues.end()) {
			queues.erase(added);
		}
	}
	return result == LibKernel::KERNEL_ERROR_EBADF ? VIDEO_OUT_ERROR_INVALID_EVENT_QUEUE : result;
}

static int DeleteVideoOutEvent(int handle, EventQueue::KernelEqueue eq, VideoOutEventKind kind) {
	uint64_t generation = 0;
	auto*    video_out  = DriverState().Get(handle, generation);
	if (video_out == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}
	Common::LockGuard lock(video_out->mutex);
	if (!video_out->opened || video_out->closing || video_out->generation != generation) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}
	if (!EventQueue::KernelPinEqueue(eq)) {
		return VIDEO_OUT_ERROR_INVALID_EVENT_QUEUE;
	}
	const int result = EventQueue::KernelDeleteEvent(eq, VideoOutEventId(kind),
	                                                 EventQueue::KERNEL_EVFILT_VIDEO_OUT);
	if (result == LibKernel::KERNEL_ERROR_EBADF) {
		return VIDEO_OUT_ERROR_INVALID_EVENT_QUEUE;
	}
	return result == LibKernel::KERNEL_ERROR_ENOENT ? OK : result;
}

static bool IsFlipDueLocked(const VideoOutConfig& cfg, uint64_t generation) {
	if (!cfg.opened || cfg.closing || cfg.generation != generation) {
		return false;
	}
	const int interval = cfg.flip_rate + 1;

	return interval <= 1 || (cfg.vblank_status.count % static_cast<uint64_t>(interval)) == 0;
}

static bool IsValidBufferIndex(int index) {
	return index >= VIDEO_OUT_BUFFER_INDEX_BLACK && index < VIDEO_OUT_BUFFER_NUM_MAX;
}

static bool IsSpecialBufferIndex(int index) {
	return index == VIDEO_OUT_BUFFER_INDEX_BLANK || index == VIDEO_OUT_BUFFER_INDEX_BLACK;
}

static bool IsValidFlipMode(int mode) {
	return mode >= VIDEO_OUT_FLIP_MODE_VSYNC && mode <= VIDEO_OUT_FLIP_MODE_VSYNC_MULTI;
}

static int ReserveFlipRequest(VideoOutDriver::Impl& driver, int handle, int index, int flip_mode,
                              int64_t flip_arg, FlipRequestSource source, uint64_t& request_id) {
	auto* video_out = driver.Get(handle);
	if (video_out == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}
	if (!IsValidFlipMode(flip_mode)) {
		return VIDEO_OUT_ERROR_INVALID_VALUE;
	}
	if (!IsValidBufferIndex(index)) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}

	// Session 114 (ROADMAP item 2): the present thread holds this mutex for a whole present; time a blocking wait.
	if (!video_out->mutex.TryLock()) {
		const auto wait_t0 = Common::FrameStats::NowNs();
		video_out->mutex.Lock();
		Common::FrameStats::Add(Common::FrameStats::Counter::FlipReserveWaitNs, Common::FrameStats::NowNs() - wait_t0);
		Common::FrameStats::Add(Common::FrameStats::Counter::FlipReserveWaitN, 1);
	}
	struct ReserveUnlock {
		Common::Mutex& mutex;
		~ReserveUnlock() { mutex.Unlock(); }
	} lock {video_out->mutex};
	if (video_out->closing ||
	    (!IsSpecialBufferIndex(index) && !video_out->buffers[index].Occupied())) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}
	if (!driver.GetFlipQueue().Reserve(*video_out, index, flip_arg, source, request_id)) {
		return VIDEO_OUT_ERROR_FLIP_QUEUE_FULL;
	}
	if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (M2 flip request): who requested this flip (flip_tid)
		Common::DiagB32::NoteFlipRequest(request_id, source == FlipRequestSource::Cpu);
	}
	return OK;
}

Graphics::ImageInfo BufferAttributeGroup::ImageInfo(const VideoOutBuffer& buffer) const {
	const auto compression = Graphics::ClassifyVideoOutCompression(
	    category == VIDEO_OUT_BUFFER_ATTRIBUTE_CATEGORY_COMPRESSED, buffer.metadata_address,
	    attribute.dcc_control, attribute.dcc_cb_register_clear_color);
	if (attribute.reserved0 != 0 || attribute.aspect_ratio != 0 || attribute.width == 0 ||
	    attribute.height == 0 || attribute.width > 16384 || attribute.height > 16384 ||
	    attribute.pitch_in_pixel != 0 ||
	    (attribute.option != 0 &&
	     attribute.option != VIDEO_OUT_BUFFER_ATTRIBUTE_OPTION_STRICT_COLORIMETRY) ||
	    attribute.tiling_mode != 0 || attribute.pad0 != 0 || attribute.reserved1[0] != 0 ||
	    attribute.reserved1[1] != 0 || attribute.reserved1[2] != 0 || buffer.data_address == 0 ||
	    compression == Graphics::VideoOutCompression::Unsupported) {
		EXIT("unsupported or invalid video-out surface attributes\n");
	}
	Graphics::VideoOutPixelFormatInfo pixel_format {};
	if (!Graphics::DecodeVideoOutPixelFormat(attribute.pixel_format, pixel_format)) {
		EXIT("unsupported video-out pixel format: 0x%016" PRIx64 "\n", attribute.pixel_format);
	}
	const auto tile_mode = Graphics::Prospero::TileMode::kRenderTarget;
	const auto pitch =
	    Graphics::TileGetTexturePitch(pixel_format.guest_format, attribute.width, tile_mode);
	Graphics::TileSizeAlign total {};
	Graphics::TileGetTextureTotalSize(pixel_format.guest_format, attribute.width, attribute.height,
	                                  1, 1, tile_mode, false, total);
	if (total.size == 0 || total.align != 65536 ||
	    (buffer.data_address & (total.align - 1u)) != 0) {
		EXIT("invalid video-out surface footprint or alignment\n");
	}
	Graphics::ImageInfo info {};
	info.data            = {buffer.data_address, total.size};
	info.pixel_format    = pixel_format.format;
	info.guest_format    = pixel_format.guest_format;
	info.type            = Graphics::Prospero::ImageType::kColor2D;
	info.extent          = {attribute.width, attribute.height, 1};
	info.resources       = {1, 1};
	info.pitch           = pitch;
	info.bytes_per_block = pixel_format.bytes_per_element;
	info.samples         = 1;
	info.tile_mode       = tile_mode;
	info.bgra16          = pixel_format.bgra16;
	info.mip_layout[0]   = {0, total.size, pitch, attribute.height};
	if (compression != Graphics::VideoOutCompression::Uncompressed) {
		info.metadata.range       = {buffer.metadata_address, 0};
		info.metadata.kind        = Graphics::ImageMetadataKind::Dcc;
		info.metadata.control     = attribute.dcc_control;
		info.metadata.compression = compression;
	}
	Graphics::ImageOps::Validate(info);
	if (!Graphics::IsSupportedVideoOutFormat(info)) {
		EXIT("unsupported normalized video-out format\n");
	}
	return info;
}

VideoOutDriver::VideoOutDriver(uint32_t width, uint32_t height, Graphics::Presenter& presenter)
    : m_impl(std::make_unique<Impl>(width, height, presenter)) {}

VideoOutDriver::~VideoOutDriver() = default;

VideoOutDriver::Impl& VideoOutDriver::State() noexcept {
	return *m_impl;
}

VideoOutDriver& VideoOutInit(uint32_t width, uint32_t height, Graphics::Presenter& presenter) {
	EXIT_IF(g_video_out_driver != nullptr);
	g_video_out_driver = std::make_unique<VideoOutDriver>(width, height, presenter);
	return *g_video_out_driver;
}

void VideoOutShutdown() {
	g_video_out_driver.reset();
}

VideoOutDriver::Impl::~Impl() {
	if (m_present_thread.joinable()) {
		m_present_thread.request_stop();
		m_present_thread.join();
	}
	for (int handle = 1; handle < VIDEO_OUT_NUM_MAX; handle++) {
		(void)Close(handle);
	}
}

void VideoOutDriver::Impl::Init(uint32_t width, uint32_t height) {
	for (auto& ctx: m_video_out_ctx) {
		ctx.width  = width;
		ctx.height = height;
	}
}

int VideoOutDriver::Impl::Open(int bus_type, int index) {
	const auto bus = std::find(VIDEO_OUT_BUSES.begin(), VIDEO_OUT_BUSES.end(), bus_type);
	if (bus == VIDEO_OUT_BUSES.end()) {
		return VIDEO_OUT_ERROR_INVALID_VALUE;
	}
	EXIT_NOT_IMPLEMENTED(index != 0);
	Common::LockGuard lock(m_mutex);

	const int handle = static_cast<int>(bus - VIDEO_OUT_BUSES.begin()) + 1;
	if (m_video_out_ctx[handle].opened) {
		return VIDEO_OUT_ERROR_RESOURCE_BUSY;
	}
	auto&             config = m_video_out_ctx[handle];
	Common::LockGuard config_lock(config.mutex);

	{
		Common::LockGuard event_lock(config.events->mutex);
		EXIT_IF(!config.events->flip.empty());
		EXIT_IF(!config.events->pre_vblank.empty());
		EXIT_IF(!config.events->vblank.empty());
		EXIT_IF(!config.events->output_mode.empty());
	}
	EXIT_IF(config.flip_rate != 0);
	for (const auto& buffer: config.buffers) {
		EXIT_IF(buffer.Occupied());
	}
	for (const auto& group: config.groups) {
		EXIT_IF(group.occupied);
	}

	config.closing = false;
	config.opened  = true;
	if (++config.generation == 0) {
		EXIT("video-out port generation wrapped\n");
	}
	config.output_mode               = VIDEO_OUT_OUTPUT_MODE_DEFAULT;
	config.flip_status               = VideoOutFlipStatus();
	config.flip_status.flipArg       = -1;
	config.flip_status.currentBuffer = -1;
	config.flip_status.count         = 0;
	config.pre_vblank_status         = VideoOutVblankStatus();
	config.vblank_status             = VideoOutVblankStatus();

	return handle;
}

bool VideoOutDriver::Impl::Close(int handle) {
	Common::LockGuard lock(m_mutex);

	if (handle <= 0 || handle >= VIDEO_OUT_NUM_MAX || !m_video_out_ctx[handle].opened) {
		return false;
	}

	auto&               config = m_video_out_ctx[handle];
	VideoOutEventQueues flip_events;
	VideoOutEventQueues pre_vblank_events;
	VideoOutEventQueues vblank_events;
	VideoOutEventQueues output_mode_events;
	{
		Common::LockGuard config_lock(config.mutex);
		if (config.closing) {
			return false;
		}
		config.opened  = false;
		config.closing = true;
		if (++config.generation == 0) {
			EXIT("video-out port generation wrapped\n");
		}
		{
			Common::LockGuard event_lock(config.events->mutex);
			flip_events        = std::move(config.events->flip);
			pre_vblank_events  = std::move(config.events->pre_vblank);
			vblank_events      = std::move(config.events->vblank);
			output_mode_events = std::move(config.events->output_mode);
		}
		config.flip_rate = 0;

		for (const auto& buffer: config.buffers) {
			if (buffer.Occupied() &&
			    (buffer.group_index >= VIDEO_OUT_BUFFER_ATTRIBUTE_NUM_MAX ||
			     buffer.data_address == 0 || !config.groups[buffer.group_index].occupied)) {
				EXIT("inconsistent registered video-out buffer state\n");
			}
		}
		for (auto& buffer: config.buffers) {
			buffer = VideoOutBuffer {};
		}
		for (auto& group: config.groups) {
			group = BufferAttributeGroup {};
		}
		config.vblank_cond.SignalAll();
	}

	m_flip_queue.Cancel(config);
	DeleteVideoOutEvents(flip_events, VideoOutEventKind::Flip);
	DeleteVideoOutEvents(pre_vblank_events, VideoOutEventKind::PreVblankStart);
	DeleteVideoOutEvents(vblank_events, VideoOutEventKind::Vblank);
	DeleteVideoOutEvents(output_mode_events, VideoOutEventKind::OutputMode);
	return true;
}

VideoOutConfig* VideoOutDriver::Impl::Get(int handle) {
	Common::LockGuard lock(m_mutex);
	if (handle <= 0 || handle >= VIDEO_OUT_NUM_MAX || !m_video_out_ctx[handle].opened) {
		return nullptr;
	}

	return m_video_out_ctx + handle;
}

VideoOutConfig* VideoOutDriver::Impl::Get(int handle, uint64_t& generation) {
	Common::LockGuard lock(m_mutex);
	if (handle <= 0 || handle >= VIDEO_OUT_NUM_MAX || !m_video_out_ctx[handle].opened) {
		return nullptr;
	}

	auto*             config = m_video_out_ctx + handle;
	Common::LockGuard config_lock(config->mutex);
	if (!config->opened || config->closing) {
		return nullptr;
	}
	generation = config->generation;
	return config;
}

bool VideoOutDriver::Impl::IsOpened(int handle) {
	Common::LockGuard lock(m_mutex);

	return handle > 0 && handle < VIDEO_OUT_NUM_MAX && m_video_out_ctx[handle].opened;
}

void VideoOutDriver::Impl::VblankBegin() {
	Common::LockGuard lock(m_mutex);

	for (int i = 1; i < VIDEO_OUT_NUM_MAX; i++) {
		auto& ctx = m_video_out_ctx[i];
		if (ctx.opened) {
			ctx.mutex.Lock();
			ctx.pre_vblank_status.count++;
			ctx.pre_vblank_status.processTime        = LibKernel::KernelGetProcessTime();
			ctx.pre_vblank_status.reserved           = LibKernel::KernelReadTsc();
			ctx.pre_vblank_status.processTimeCounter = LibKernel::KernelGetProcessTimeCounter();

			TriggerVideoOutEvents(ctx, VideoOutEventKind::PreVblankStart,
			                      reinterpret_cast<void*>(ctx.pre_vblank_status.count));
			ctx.mutex.Unlock();
		}
	}
}

void VideoOutDriver::Impl::VblankEnd() {
	Common::LockGuard lock(m_mutex);

	bool pvar_published = false;
	for (int i = 1; i < VIDEO_OUT_NUM_MAX; i++) {
		auto& ctx = m_video_out_ctx[i];
		if (ctx.opened) {
			ctx.mutex.Lock();
			ctx.vblank_status.count++;
			// Track P, KYTY_PVAR=2 (kernel/pvar.h): the vblank count of the first opened handle for the M0 writer.
			if (!pvar_published && LibKernel::PVar::Publishing()) {
				LibKernel::PVar::PublishVblank(ctx.vblank_status.count);
				pvar_published = true;
			}
			ctx.vblank_status.processTime        = LibKernel::KernelGetProcessTime();
			ctx.vblank_status.reserved           = LibKernel::KernelReadTsc();
			ctx.vblank_status.processTimeCounter = LibKernel::KernelGetProcessTimeCounter();

			TriggerVideoOutEvents(ctx, VideoOutEventKind::Vblank,
			                      reinterpret_cast<void*>(ctx.vblank_status.count));
			ctx.vblank_cond.SignalAll();
			ctx.mutex.Unlock();
		}
	}
}

void VideoOutDriver::Impl::PresentThread(std::stop_token token) {
	Common::FrameStats::RegisterCurrentThread(Common::FrameStats::ThreadRole::Present);
	const auto frequency = Common::Timer::QueryPerformanceFrequency();
	EXIT_IF(frequency == 0);

	int64_t total_wait = 0;
	while (!token.stop_requested()) {
		const auto sleep_begin = Common::Timer::QueryPerformanceCounter();
		if (total_wait > 0) {
			const auto remaining_us =
			    (static_cast<uint64_t>(total_wait) * 1000000u + frequency - 1) / frequency;
			// Track F, F20j3 (KYTY_DIAG_B32 W:vo_pace, item 574(g)(1)): the present thread's own vblank pacing sleep.
			Common::DiagB32::Mark b32;
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::VoPace, this, 0, remaining_us);
			}
			Common::Thread::SleepMicro(static_cast<uint32_t>(
			    std::clamp<uint64_t>(remaining_us, 1, std::numeric_limits<uint32_t>::max())));
			b32.End(0, false);
		}
		if (token.stop_requested()) {
			break;
		}
		const auto frame_begin = Common::Timer::QueryPerformanceCounter();
		total_wait -= static_cast<int64_t>(frame_begin - sleep_begin);

		const auto refresh = std::max(Config::GetVblankFrequency(), 1u);
		const auto period  = std::max(frequency / refresh, uint64_t {1});

		if (m_presenter.IsGuestPaused()) {
			if (auto* frame = m_presenter.PrepareLastFrame(); frame != nullptr) {
				m_presenter.Present(*frame, true);
			}
			const auto frame_end = Common::Timer::QueryPerformanceCounter();
			total_wait +=
			    static_cast<int64_t>(period) - static_cast<int64_t>(frame_end - frame_begin);
			continue;
		}

		VblankBegin();
		bool presented = m_flip_queue.Flip(0);
		if (!presented && m_presenter.NeedsSystemOverlayRefresh()) {
			if (auto* frame = m_presenter.PrepareLastFrame(); frame != nullptr) {
				m_presenter.Present(*frame, true);
				presented = true;
			} else {
				uint32_t width  = 0;
				uint32_t height = 0;
				{
					Common::LockGuard lock(m_mutex);
					width  = m_video_out_ctx[0].width;
					height = m_video_out_ctx[0].height;
				}
				auto& blank = m_presenter.PrepareBlankFrame(width, height, true);
				m_presenter.Present(blank);
				presented = true;
			}
		}
		if (!presented && total_wait < 0) {
			bool     any_open = false;
			uint32_t width    = 0;
			uint32_t height   = 0;
			{
				Common::LockGuard lock(m_mutex);
				width  = m_video_out_ctx[0].width;
				height = m_video_out_ctx[0].height;
				for (int handle = 1; handle < VIDEO_OUT_NUM_MAX; handle++) {
					any_open |= m_video_out_ctx[handle].opened;
				}
			}
			if (!any_open) {
				auto& blank = m_presenter.PrepareBlankFrame(width, height, true);
				m_presenter.Present(blank);
			}
		}
		VblankEnd();

		const auto frame_end = Common::Timer::QueryPerformanceCounter();
		total_wait += static_cast<int64_t>(period) - static_cast<int64_t>(frame_end - frame_begin);
	}
}

bool FlipQueue::Reserve(VideoOutConfig& cfg, int index, int64_t flip_arg, FlipRequestSource source,
                        uint64_t& request_id) {
	Common::LockGuard lock(m_mutex);

	if (m_requests.size() + m_cpu_requests.size() >= VIDEO_OUT_FLIP_QUEUE_CAPACITY) {
		return false;
	}
	auto& pending = source == FlipRequestSource::GpuEop ? m_requests : m_cpu_requests;

	Request r {};
	r.id         = m_next_request_id++;
	r.cfg        = &cfg;
	r.generation = cfg.generation;
	r.index      = index;
	r.flip_arg   = flip_arg;
	r.submit_ptc = LibKernel::KernelGetProcessTimeCounter();
	r.reserve_host_ns = Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;
	r.source     = source;
	r.state      = RequestState::Reserved;

	pending.push_back(r);
	request_id = r.id;

	cfg.flip_status.flipPendingNum = static_cast<int>(m_requests.size() + m_cpu_requests.size());
	cfg.flip_status.submitProcessTimeCounter = r.submit_ptc;
	if (source == FlipRequestSource::GpuEop) {
		cfg.flip_status.gcQueueNum++;
	}

	return true;
}

FlipQueue::~FlipQueue() {
	for (auto* queue: {&m_requests, &m_cpu_requests, &m_cancelled_requests}) {
		for (auto& request: *queue) {
			if (request.frame != nullptr) {
				m_presenter.Discard(*request.frame);
			}
		}
	}
}

void FlipQueue::Cancel(VideoOutConfig& cfg) {
	std::vector<Graphics::Presenter::Frame*> frames;
	m_mutex.Lock();
	// Track F, F20j3 (KYTY_DIAG_B32 W:flip_cancel, item 574(a)(4)): Close waits for the present of its front request.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && m_processing && !m_requests.empty() && m_requests.front().cfg == &cfg) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::FlipCancel, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);
	}
	while (m_processing && !m_requests.empty() && m_requests.front().cfg == &cfg) {
		m_done_cond_var.Wait(&m_mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(m_done_cond_var.B32Waker(b32.SinceNs()), false);
	}
	for (auto* queue: {&m_requests, &m_cpu_requests}) {
		for (auto it = queue->begin(); it != queue->end();) {
			if (it->cfg != &cfg) {
				++it;
				continue;
			}
			if (it->state == RequestState::Reserved || it->state == RequestState::Recording) {
				auto cancelled = it++;
				m_cancelled_requests.splice(m_cancelled_requests.end(), *queue, cancelled);
				continue;
			}
			if (it->state == RequestState::Presenting) {
				EXIT("video-out cancellation retained a presenting request\n");
			}
			if (it->frame != nullptr) {
				frames.push_back(it->frame);
			}
			it = queue->erase(it);
		}
	}
	m_done_cond_var.SignalAll();
	m_submit_slot_cond_var.SignalAll();
	m_submit_cond_var.SignalAll();
	m_mutex.Unlock();
	for (auto* frame: frames) {
		m_presenter.Discard(*frame);
	}
	Common::LockGuard lock(cfg.mutex);
	cfg.flip_status.flipPendingNum = 0;
	cfg.flip_status.gcQueueNum     = 0;
}

void FlipQueue::Prepare(uint64_t request_id, Graphics::CommandBuffer& buffer) {
	VideoOutConfig* cfg        = nullptr;
	uint64_t        generation = 0;
	int             index      = 0;
	{
		Common::LockGuard lock(m_mutex);
		auto request = std::find_if(m_requests.begin(), m_requests.end(),
		                            [request_id](const auto& r) { return r.id == request_id; });
		if (request == m_requests.end()) {
			auto pending = std::find_if(m_cpu_requests.begin(), m_cpu_requests.end(),
			                            [request_id](const auto& r) { return r.id == request_id; });
			if (pending == m_cpu_requests.end()) {
				auto cancelled =
				    std::find_if(m_cancelled_requests.begin(), m_cancelled_requests.end(),
				                 [request_id](const auto& r) { return r.id == request_id; });
				if (cancelled == m_cancelled_requests.end() ||
				    cancelled->state != RequestState::Reserved) {
					EXIT("cannot prepare video-out request id=%" PRIu64 "\n", request_id);
				}
				cancelled->state = RequestState::Recording;
				return;
			}
			request = m_requests.insert(m_requests.end(), *pending);
			m_cpu_requests.erase(pending);
		}
		if (request->state != RequestState::Reserved) {
			EXIT("cannot prepare video-out request id=%" PRIu64 "\n", request_id);
		}
		request->state = RequestState::Recording;
		cfg            = request->cfg;
		generation     = request->generation;
		index          = request->index;
	}

	const bool          special = IsSpecialBufferIndex(index);
	Graphics::ImageInfo source_info;
	uint32_t            width   = 0;
	uint32_t            height  = 0;
	bool                current = false;
	{
		Common::LockGuard lock(cfg->mutex);
		current = cfg->opened && !cfg->closing && cfg->generation == generation;
		if (current) {
			if (special) {
				width  = cfg->width;
				height = cfg->height;
			} else {
				const auto& surface = cfg->buffers[index];
				if (!surface.Occupied()) {
					EXIT("cannot prepare flip from an unregistered surface, id=%" PRIu64
					     " index=%d\n",
					     request_id, index);
				}
				if (surface.group_index >= VIDEO_OUT_BUFFER_ATTRIBUTE_NUM_MAX ||
				    !cfg->groups[surface.group_index].occupied) {
					EXIT("video-out surface references an unavailable attribute group, id=%" PRIu64
					     " index=%d group=%d\n",
					     request_id, index, surface.group_index);
				}
				source_info = cfg->groups[surface.group_index].ImageInfo(surface);
			}
		}
	}
	if (!current) {
		Common::LockGuard lock(m_mutex);
		const auto        request =
		    std::find_if(m_requests.begin(), m_requests.end(),
		                 [request_id](const auto& r) { return r.id == request_id; });
		if (request != m_requests.end()) {
			m_cancelled_requests.splice(m_cancelled_requests.end(), m_requests, request);
		}
		return;
	}
	Graphics::Presenter::Frame* frame = nullptr;
	if (special) {
		frame = &m_presenter.PrepareBlankFrame(width, height, index == VIDEO_OUT_BUFFER_INDEX_BLACK,
		                                       &buffer);
	} else {
		frame = &m_presenter.PrepareFrame(buffer, source_info);
	}

	Common::LockGuard lock(m_mutex);
	Request*          prepared = nullptr;
	if (const auto request =
	        std::find_if(m_requests.begin(), m_requests.end(),
	                     [request_id](const auto& r) { return r.id == request_id; });
	    request != m_requests.end()) {
		prepared = &*request;
	} else if (const auto cancelled =
	               std::find_if(m_cancelled_requests.begin(), m_cancelled_requests.end(),
	                            [request_id](const auto& r) { return r.id == request_id; });
	           cancelled != m_cancelled_requests.end()) {
		prepared = &*cancelled;
	}
	if (prepared == nullptr || prepared->state != RequestState::Recording ||
	    prepared->frame != nullptr) {
		EXIT("video-out request changed while recording, id=%" PRIu64 "\n", request_id);
	}
	prepared->frame = frame;
}

void FlipQueue::Complete(uint64_t request_id) {
	m_mutex.Lock();
	auto request = std::find_if(m_requests.begin(), m_requests.end(),
	                            [request_id](const auto& r) { return r.id == request_id; });
	if (request != m_requests.end()) {
		if (request->state != RequestState::Recording || request->frame == nullptr) {
			m_mutex.Unlock();
			EXIT("completed GPU flip has no prepared recording, id=%" PRIu64 "\n", request_id);
		}
		request->state = RequestState::Ready;
		m_submit_cond_var.Signal();
		m_mutex.Unlock();
		return;
	}
	auto cancelled = std::find_if(m_cancelled_requests.begin(), m_cancelled_requests.end(),
	                              [request_id](const auto& r) { return r.id == request_id; });
	if (cancelled == m_cancelled_requests.end() || cancelled->state != RequestState::Recording) {
		m_mutex.Unlock();
		EXIT("completed GPU flip has no prepared recording, id=%" PRIu64 "\n", request_id);
	}
	auto* frame = cancelled->frame;
	m_cancelled_requests.erase(cancelled);
	m_done_cond_var.SignalAll();
	m_mutex.Unlock();
	if (frame != nullptr) {
		m_presenter.Discard(*frame);
	}
}

void FlipQueue::MarkIncomplete(uint64_t request_id) {
	Common::LockGuard lock(m_mutex);
	for (auto& request: m_requests) {
		if (request.id == request_id) {
			request.incomplete = true;
			return;
		}
	}
}

// Session 123, knob "skipceil" = 1 (MEASUREMENT ONLY, design123.md s.1.5 [RC14/M1]): false when the request was not
// found (already cancelled or gone) - skc_mark_miss.
bool FlipQueue::MarkSkipCeil(uint64_t request_id) {
	Common::LockGuard lock(m_mutex);
	for (auto& request: m_requests) {
		if (request.id == request_id) {
			request.skip_ceil = true;
			return true;
		}
	}
	return false;
}

void FlipQueue::WaitForSubmitSlot() {
	Common::LockGuard lock(m_mutex);
	// Track F, F20j3 (KYTY_DIAG_B32 W:flip_slot, item 574(a)(4)): GuestGpu waits for the present thread to free a slot.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && m_requests.size() + m_cpu_requests.size() >= VIDEO_OUT_FLIP_QUEUE_CAPACITY) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::FlipSlot, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);
	}
	while (m_requests.size() + m_cpu_requests.size() >= VIDEO_OUT_FLIP_QUEUE_CAPACITY) {
		if (m_requests.empty()) {
			EXIT("video-out queue is saturated by CPU flips queued behind the current EOP\n");
		}
		m_submit_slot_cond_var.Wait(&m_mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(m_submit_slot_cond_var.B32Waker(b32.SinceNs()), false);
	}
}

void FlipQueue::Wait(VideoOutConfig& cfg, int index) {
	Common::LockGuard lock(m_mutex);

	auto has_request = [this, &cfg, index] {
		auto matches = [&cfg, index](const auto& r) { return r.cfg == &cfg && r.index == index; };
		return std::any_of(m_requests.begin(), m_requests.end(), matches) ||
		       std::any_of(m_cpu_requests.begin(), m_cpu_requests.end(), matches);
	};
	// Track F, F20j3 (KYTY_DIAG_B32 W:flip_done, item 574(a)(4)): WaitFlipDone waits until the request is presented.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && has_request()) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::FlipDone, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);
	}
	while (has_request()) {
		m_done_cond_var.Wait(&m_mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(m_done_cond_var.B32Waker(b32.SinceNs()), false);
	}
}

bool FlipQueue::Flip(uint32_t micros) {
	KYTY_PROFILER_BLOCK("FlipQueue::Flip");

	m_mutex.Lock();
	if (m_requests.empty()) {
		// Track F, F20j3 (KYTY_DIAG_B32 W:flip_req, item 574(a)(4)): the present thread waits for a flip request; peer -
		// GuestGpu (it supplies the GPU flip requests), waker - the last m_submit_cond_var signaller (Complete).
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::FlipReq, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), micros);
		}
		const bool b32_got = m_submit_cond_var.WaitFor(&m_mutex, micros);
		if (b32.Active()) [[unlikely]] {
			b32.End(m_submit_cond_var.B32Waker(b32.SinceNs()), !b32_got);
		}

		if (m_requests.empty()) {
			m_mutex.Unlock();
			return false;
		}
	}
	if (m_processing) {
		EXIT("video-out flip queue processing is already active\n");
	}
	if (m_requests.front().state != RequestState::Ready) {
		m_mutex.Unlock();
		return false;
	}
	m_processing = true;
	auto r       = m_requests.front();
	m_mutex.Unlock();

	r.cfg->mutex.Lock();
	// Session 114 (ROADMAP item 4): the hold of VideoOutConfig::mutex by phase - GuestGpu's ReserveFlipRequest waits on it.
	const uint64_t hold_t0    = Common::FrameStats::NowNs();
	uint64_t       present_ns = 0;
	uint64_t       poll_ns    = 0;
	if (!IsFlipDueLocked(*r.cfg, r.generation)) {
		r.cfg->mutex.Unlock();
		Common::LockGuard queue_lock(m_mutex);
		m_processing = false;
		m_done_cond_var.SignalAll();
		return false;
	}

	m_mutex.Lock();
	if (m_requests.empty() || m_requests.front().id != r.id ||
	    m_requests.front().state != RequestState::Ready || !m_processing) {
		EXIT("video-out request changed before presentation, id=%" PRIu64 "\n", r.id);
	}
	m_requests.front().state = RequestState::Presenting;
	m_mutex.Unlock();

	static const bool hold_incomplete = [] {
		const char* value = std::getenv("KYTY_ASYNC_HOLD_FRAME");
		return value == nullptr || value[0] != '0';
	}();
	// Session 123, knob "skipceil" = 1 (MEASUREMENT ONLY, design123.md s.1.5): the flip of a skipped frame is held
	// whatever KYTY_ASYNC_HOLD_FRAME says.  skc_held / skc_held_inc / skc_pres_* are added HERE, on the present thread,
	// before the FrameTrace snapshot of this same Flip call (below), so they land on the line of this flip.
	if ((r.incomplete && hold_incomplete) || r.skip_ceil) {
		if (r.skip_ceil) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcHeld, 1);
			static std::atomic<uint32_t> skc_logged {0};
			if (skc_logged.fetch_add(1, std::memory_order_relaxed) < 8) {
				LOGF("SkipCeil: flip %" PRIu64 " held\n", r.id);
			}
		} else {
			// Keep the previously presented image on screen instead of a frame with missing draws.
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcHeldInc, 1);
			static std::atomic<uint32_t> held {0};
			if (held.fetch_add(1, std::memory_order_relaxed) < 64) {
				LOGF("AsyncPipelines: flip %" PRIu64 " held (incomplete frame)\n", r.id);
			}
		}
		if (!r.skip_ceil && !r.incomplete) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcBad, 1); // held without a reason
		}
		m_presenter.Discard(*r.frame);
	} else {
		if (r.skip_ceil) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcBad, 1); // a skipceil request presented
		}
		const uint64_t present_t0 = Common::FrameStats::NowNs();
		// Track F, F20j (KYTY_DIAG_B32 M3 H:present; stand KYTY_TEST_B32 mode present sleeps inside the mark): one flag.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_present_site) [[unlikely]] {
			if (Common::DiagB32::g_on) {
				b32.BeginH(Common::DiagB32::Call::Present);
			}
			Common::DiagB32::TestPresentPoint();
		}
		m_presenter.Present(*r.frame);
		b32.End(0, false);
		present_ns = Common::FrameStats::NowNs() - present_t0;
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcPresNs, present_ns); // Session 123, S_live ([RC12/O12])
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcPresN, 1);
	}
	Graphics::RenderDocOnGuestFlip(m_presenter.Renderer());

	m_mutex.Lock();
	if (m_requests.empty() || m_requests.front().id != r.id ||
	    m_requests.front().state != RequestState::Presenting) {
		EXIT("video-out flip queue changed while processing its front request\n");
	}
	m_requests.pop_front();

	r.cfg->flip_status.count++;
	// Track F, F20j (KYTY_DIAG_B32): the window boundary for the B32 sampler (n = FrameTrace: n= of this flip); the
	// reports the sampler has closed are printed here, under FlipQueue::m_mutex and VideoOutConfig::mutex (F20j2, RC6 of
	// F20k: the print time goes into instr_us of the window open during the print).
	if (Common::DiagB32::g_on) [[unlikely]] {
		Common::DiagB32::OnFlip(r.cfg->flip_status.count, r.id, r.reserve_host_ns);
	}
	// Track P, KYTY_PVAR=2 (kernel/pvar.h): the key n of the PVar line (= FrameTrace: n= of this flip).
	if (LibKernel::PVar::Publishing()) {
		LibKernel::PVar::PublishFlip(r.cfg->flip_status.count);
	}
	Graphics::GpuTimeProfiler::SetFrame(static_cast<uint32_t>(r.cfg->flip_status.count));
	// Track F, F16d (KYTY_DIAG_F5 / KYTY_DIAG_F6, item 427(e)): the flip tick - a line on growth, at most every 2 s.
	// F16d2 (item 470(v)(1), form (a)): the tick only publishes the request; the line is copied and printed on the
	// GuestGpu thread outside every window of the sites (GuestGpu::ThreadRun, graphicsRun.cpp).
	Graphics::DiagF5::Tick(static_cast<uint32_t>(r.cfg->flip_status.count));
	Graphics::DiagF6::Tick(static_cast<uint32_t>(r.cfg->flip_status.count));
	const uint64_t poll_t0 = Common::FrameStats::NowNs();
	Common::Gates::Poll(static_cast<uint32_t>(r.cfg->flip_status.count));
	poll_ns = Common::FrameStats::NowNs() - poll_t0;
	// Session 122, knob "burn": the frame key, after Poll (a thread that loads it also sees the knob Poll published).
	Common::FrameStats::BurnPublishFrame(static_cast<uint32_t>(r.cfg->flip_status.count));
	Common::FrameStats::SetLean(Common::Gates::Enabled(Common::Gates::Gate::FrameStatsLean));
	r.cfg->flip_status.processTime              = LibKernel::KernelGetProcessTime();
	r.cfg->flip_status.processTimeCounter       = LibKernel::KernelGetProcessTimeCounter();
	r.cfg->flip_status.submitProcessTimeCounter = r.submit_ptc;
	r.cfg->flip_status.flipArg                  = r.flip_arg;
	r.cfg->flip_status.currentBuffer            = r.index;
	r.cfg->flip_status.flipPendingNum = static_cast<int>(m_requests.size() + m_cpu_requests.size());
	{
		// Emulation speed from the presented frame pace (unscaled guest time, freezes excluded):
		// a fixed-step game advances one target interval per flip, so speed = target / actual.
		const auto base_us = LibKernel::KernelGetBaseTimeUs();
		auto&      cfg     = *r.cfg;
		if (cfg.pace_last_base_us != 0 && base_us > cfg.pace_last_base_us) {
			const double target_us = 1000000.0 * static_cast<double>(cfg.flip_rate + 1) /
			                         static_cast<double>(std::max(Config::GetVblankFrequency(), 1u));
			const double interval_us = std::clamp(static_cast<double>(base_us - cfg.pace_last_base_us),
			                                      target_us * 0.5, target_us * 8.0);
			cfg.pace_ema_us = cfg.pace_ema_us == 0.0 ? interval_us : cfg.pace_ema_us + 0.08 * (interval_us - cfg.pace_ema_us);
			double speed    = std::clamp(target_us / cfg.pace_ema_us, 0.2, 1.0);
			if (speed > 0.97) {
				speed = 1.0;
			}
			cfg.pace_speed = speed;
			LibKernel::KernelSetGuestSpeed(speed);
		}
		cfg.pace_last_base_us = base_us;
	}
	{
		static const bool av_trace = Common::EnvFlagOn("KYTY_AV_TRACE");
		if (av_trace) {
			const auto host_frequency = Common::Timer::QueryPerformanceFrequency();
			const auto host_counter   = Common::Timer::QueryPerformanceCounter();
			const auto host_us        = host_frequency != 0
			                                ? (host_counter / host_frequency) * 1000000u +
			                                      ((host_counter % host_frequency) * 1000000u) / host_frequency
			                                : 0u;
			LOGF("AvTrace: flip n=%" PRIu64 " t=%" PRIu64 " host=%" PRIu64 " arg=%" PRId64 " vblank=%" PRIu64
			     " pending=%d base=%" PRIu64 " speed=%.3f\n",
			     r.cfg->flip_status.count, r.cfg->flip_status.processTime, host_us, r.flip_arg,
			     r.cfg->vblank_status.count, r.cfg->flip_status.flipPendingNum, r.cfg->pace_last_base_us,
			     r.cfg->pace_speed);
		}
	}
	// Track F, F25k (KYTY_LONGFRAME=1, ROADMAP s122 item 613(v)(7); measurement only, default 0): a flip >= 100 ms after the
	// previous one - a "LongFrame:" line (at most 4 096), without KYTY_FRAME_TRACE. The clock and the point are those of
	// dt_us of the "FrameTrace:" line below: Common::FrameStats::NowNs on this Present thread after flip_status.count++,
	// under m_mutex. t_ms - the same clock, for the t0_ms / t1_ms of the stand's "TestLogStall:" line. F25k2 (RC2 of F25l,
	// ROADMAP s122 item 616(b)(2)): no log write on this thread - Log::LongFrameRecord stores the record (at most 4 096) in a
	// static array, a thread off the frame path prints the line.
	{
		static const bool long_frame = Common::EnvFlagOn("KYTY_LONGFRAME");
		if (long_frame) [[unlikely]] {
			static uint64_t long_frame_prev_ns = 0;
			const uint64_t  now_ns             = Common::FrameStats::NowNs();
			if (long_frame_prev_ns != 0 && now_ns - long_frame_prev_ns >= 100000000u) {
				Log::LongFrameRecord(r.cfg->flip_status.count, (now_ns - long_frame_prev_ns) / 1000u, now_ns / 1000000u);
			}
			long_frame_prev_ns = now_ns;
		}
	}
	if (Common::FrameStats::Enabled()) {
		namespace FS = Common::FrameStats;
		struct Snapshot {
			uint64_t                                                   host_ns = 0;
			std::array<uint64_t, static_cast<size_t>(FS::Counter::Count)>    c {};
			std::array<uint64_t, static_cast<size_t>(FS::ThreadRole::Count)> cpu {};
			uint64_t                                                   proc = 0;
		};
		static Snapshot prev;
		Snapshot        cur;
		if (r.cfg->flip_status.count % 300 == 0) {
			Graphics::VulkanLogMemoryStats();
		}
		cur.host_ns = FS::NowNs();
		FS::NoteFrame(r.cfg->flip_status.count + 1);
		for (size_t i = 0; i < cur.c.size(); i++) {
			cur.c[i] = FS::Read(static_cast<FS::Counter>(i));
		}
		// Session 130, ac_cbad attribution (docs/session-130/cbad130.md rev 2 s.6.1, 6.1'; I0): the content group read again
		// as one consistent snapshot, in the reverse of the writer's order with an acquire fence after each read - only when
		// a value of the group or of ac_cls_* read by the loop above moved (none moves at 0/1: no new read there). Accepted
		// when m + e = cbad, sum(ac_cbm_*) = m and sum(ac_cbe_*) = e (ac_cbm_host_d is not a term); after 1000 attempts the
		// last read is taken and an ArmCopyClass: TORN line written. Session 131, knob "lwin" (lw131.md rev 1 s.7.3 with
		// ROADMAP s122 item 127(b)): the lw_* group right after ac_cbad_e and BEFORE the reasons (the writer adds it after them),
		// so a class read brings its reason and a torn attempt fails the same sums; the acceptance is unchanged.
		{
			using C = FS::Counter;
			static constexpr std::array<C, 29> group {C::AcCbad,      C::AcCbadM,     C::AcCbadE,   C::LwCdp,       C::LwCdx,
			                                          C::LwCrp,       C::LwCrx,       C::LwC3p,     C::LwC3x,       C::LwP8,
			                                          C::LwX,         C::LwXmk,       C::LwP8sync,  C::LwXnc,       C::LwOpen,
			                                          C::AcCbmNosnap, C::AcCbmBad,    C::AcCbmLeft, C::AcCbmStale,  C::AcCbmRemark,
			                                          C::AcCbmNew,    C::AcCbmPend,   C::AcCbmHostD, C::AcCbmHost,  C::AcCbeRo,
			                                          C::AcCbeNa,     C::AcCbeOth,    C::AcCdiff,   C::AcCmpPages};
			static constexpr std::array<C, 4>  cls_rows {C::AcClsN, C::AcClsNs, C::AcClsWaitNs, C::AcClsVq};
			bool moved = false;
			for (const auto counter: group) {
				moved = moved || cur.c[static_cast<size_t>(counter)] != prev.c[static_cast<size_t>(counter)];
			}
			for (const auto counter: cls_rows) {
				moved = moved || cur.c[static_cast<size_t>(counter)] != prev.c[static_cast<size_t>(counter)];
			}
			if (moved) {
				std::array<uint64_t, group.size()> v {};
				bool                               consistent = false;
				// The terms by name (the lw_* group moved every index of session 130).
				const auto at = [&](C counter) {
					for (size_t k = 0; k < group.size(); k++) {
						if (group[k] == counter) {
							return v[k];
						}
					}
					return uint64_t {0};
				};
				for (uint32_t attempt = 0; attempt < 1000 && !consistent; attempt++) {
					for (size_t k = 0; k < group.size(); k++) {
						v[k] = FS::Read(group[k]);
						std::atomic_thread_fence(std::memory_order_acquire);
					}
					const auto cbm = at(C::AcCbmNosnap) + at(C::AcCbmBad) + at(C::AcCbmLeft) + at(C::AcCbmStale) +
					                 at(C::AcCbmRemark) + at(C::AcCbmNew) + at(C::AcCbmPend) + at(C::AcCbmHost);
					const auto cbe = at(C::AcCbeRo) + at(C::AcCbeNa) + at(C::AcCbeOth);
					consistent     = at(C::AcCbadM) + at(C::AcCbadE) == at(C::AcCbad) && cbm == at(C::AcCbadM) &&
					             cbe == at(C::AcCbadE);
				}
				for (size_t k = 0; k < group.size(); k++) {
					cur.c[static_cast<size_t>(group[k])] = v[k];
				}
				if (!consistent) {
					static std::atomic<uint32_t> torn {0};
					if (torn.fetch_add(1, std::memory_order_relaxed) < 40) {
						LOGF("ArmCopyClass: TORN n=%" PRIu64 " c=%llu m=%llu e=%llu\n", r.cfg->flip_status.count,
						     static_cast<unsigned long long>(v[0]), static_cast<unsigned long long>(v[1]),
						     static_cast<unsigned long long>(v[2]));
					}
				}
			}
		}
		for (size_t i = 0; i < cur.cpu.size(); i++) {
			cur.cpu[i] = FS::ThreadCpuNs(static_cast<FS::ThreadRole>(i));
		}
		cur.proc = FS::ProcessCpuNs();
		if (prev.host_ns != 0) {
			const auto d = [&](FS::Counter counter) {
				const auto i = static_cast<size_t>(counter);
				return static_cast<unsigned long long>(cur.c[i] - prev.c[i]);
			};
			const auto dus = [&](FS::Counter counter) { return d(counter) / 1000u; };
			const auto cpu = [&](FS::ThreadRole role) {
				const auto i = static_cast<size_t>(role);
				return static_cast<unsigned long long>((cur.cpu[i] - prev.cpu[i]) / 1000u);
			};
			const auto lat_us = r.reserve_host_ns != 0 && cur.host_ns > r.reserve_host_ns
			                        ? (cur.host_ns - r.reserve_host_ns) / 1000u
			                        : 0u;
			LOGF("FrameTrace: n=%" PRIu64 " dt_us=%llu lat_us=%llu gpu_proc=%llu gpu_idle=%llu"
			     " gpu_blocked=%llu submits=%llu submit_us=%llu semwaits=%llu semwait_us=%llu"
			     " downloads=%llu download_us=%llu draws=%llu draw_us=%llu dispatches=%llu"
			     " dispatch_us=%llu faults=%llu fault_us=%llu wrm_stalls=%llu gpu_busy_us=%llu"
			     " gpu_n=%llu cpu_main_us=%llu cpu_gpu_us=%llu cpu_present_us=%llu"
			     " cpu_proc_us=%llu faults_gpu=%llu fault_gpu_us=%llu semwait_gpu_us=%llu"
			     " prios=%llu prio_us=%llu dmas=%llu dma_us=%llu"
			     " arm=%u blk=%u rt_w=%u rt_h=%u vp_w=%u vp_h=%u rk3_c5_max_ns=%u rts_chain_max=%u ai_enq_nmax=%u" "\n",
			     r.cfg->flip_status.count,
			     static_cast<unsigned long long>((cur.host_ns - prev.host_ns) / 1000u),
			     static_cast<unsigned long long>(lat_us), dus(FS::Counter::GpuThreadProcessNs),
			     dus(FS::Counter::GpuThreadIdleNs), dus(FS::Counter::GpuThreadBlockedNs),
			     d(FS::Counter::Submits), dus(FS::Counter::SubmitNs), d(FS::Counter::SemWaits),
			     dus(FS::Counter::SemWaitNs), d(FS::Counter::Downloads),
			     dus(FS::Counter::DownloadNs), d(FS::Counter::Draws), dus(FS::Counter::DrawNs),
			     d(FS::Counter::Dispatches), dus(FS::Counter::DispatchNs), d(FS::Counter::Faults),
			     dus(FS::Counter::FaultNs), d(FS::Counter::WaitRegMemStalls),
			     dus(FS::Counter::GpuBusyNs), d(FS::Counter::GpuMeasured),
			     cpu(FS::ThreadRole::Main), cpu(FS::ThreadRole::Gpu), cpu(FS::ThreadRole::Present),
			     static_cast<unsigned long long>((cur.proc - prev.proc) / 1000u),
			     d(FS::Counter::FaultsGpu), dus(FS::Counter::FaultGpuNs),
			     dus(FS::Counter::SemWaitGpuNs), d(FS::Counter::PriorityWaits),
			     dus(FS::Counter::PriorityWaitNs), d(FS::Counter::Dmas), dus(FS::Counter::DmaNs),
			     // The arm of the interval this line reports: Gates::Poll above ran before it and
			     // already moved the schedule on, so the reported arm is the previous one.
			     Common::Gates::ReportedArm(), Common::Gates::ReportedBlock(),
			     FS::TakeMax(FS::Gauge::RtWidth), FS::TakeMax(FS::Gauge::RtHeight),
			     FS::TakeMax(FS::Gauge::VpWidth), FS::TakeMax(FS::Gauge::VpHeight),
			     FS::TakeMax(FS::Gauge::Rk3C5Max),     // Session 126, knob "rk3cen" ([RC4])
			     FS::TakeMax(FS::Gauge::RtsChainMax), // Session 127, knob "rtskip" ([RC1])
			     FS::TakeMax(FS::Gauge::AiEnqNmax));  // Session 130, knob "acinline" (RC2)
			LOGF("FrameTrace-draw: n=%" PRIu64 " logs=%llu log_us=%llu log_gpu_us=%llu d_pop=%llu"
			     " d_check=%llu d_rt=%llu d_prog=%llu d_bind=%llu d_vb=%llu d_acq=%llu d_pipe=%llu"
			     " d_commit=%llu d_emit=%llu c_pop=%llu c_prog=%llu c_pipe=%llu c_bind=%llu"
			     " c_commit=%llu c_emit=%llu p_prep=%llu p_key=%llu p_mat=%llu p_perm=%llu"
			     " p_reads=%llu p_creads=%llu m_eval=%llu m_asm=%llu m_spec=%llu m_insts=%llu"
			     " m_fail=%llu memo_hit=%llu memo_miss=%llu m_read_us=%llu m_wide=%llu b_tex=%llu"
			     " b_texn=%llu b_view=%llu b_viewn=%llu b_buf=%llu b_smp=%llu"
			     " bb_find=%llu bb_obtain=%llu bb_sync=%llu bb_upload=%llu bb_n=%llu tex_hits=%llu"
			     " rt_hits=%llu ob_us=%llu ob_n=%llu sync_ups=%llu spin_us=%llu spins=%llu"
			     " spin_gpu_us=%llu gbar=%llu ibar=%llu swbar=%llu rp_begin=%llu pops=%llu pop_us=%llu"
			     " gbar_skip=%llu faults_main=%llu fault_main_us=%llu img_new=%llu img_free=%llu"
			     " img_up=%llu img_up_kb=%llu img_up_us=%llu img_init_us=%llu img_copy_us=%llu cb_copy=%llu cb_copy_gpu=%llu cb_copy_kb=%llu acopy_wait_us=%llu acopy_waits=%llu"
			     " prot_us=%llu prot_pages=%llu protw_us=%llu protw_pages=%llu prot_drain_us=%llu prot_drains=%llu"
			     " prot_calls=%llu prot_ro=%llu prot_ro_pages=%llu prot_na=%llu prot_na_pages=%llu prot_rw_us=%llu prot_rw_pages=%llu prot_mask_us=%llu prot_mask=%llu prot_gpu_us=%llu prot_gpu=%llu prot_gpu_pages=%llu buf_new=%llu buf_new_us=%llu acopy_gpu_waits=%llu img_imp=%llu img_imp_kb=%llu img_imp_pieces=%llu hostread_waits=%llu hostread_wait_us=%llu img_detile=%llu img_regions=%llu"
			     " img_defer=%llu img_defer_kb=%llu img_pend=%llu img_pend_kb=%llu img_minlod=%llu"
			     " bda_us=%llu bda_n=%llu srt_miss=%llu clamp_miss=%llu"
			     " smemo_hit=%llu smemo_miss=%llu smemo_stale=%llu smemo_skip=%llu"
			     " smemo_reads=%llu bufepoch=%llu"
			     " bda_scan=%llu bda_skip=%llu bda_bskip=%llu bda_bit_bad=%llu"
			     " bpage_hit=%llu bpage_miss=%llu"
			     " m_nodes=%llu m_nodes_need=%llu m_rnodes=%llu m_rnodes_need=%llu"
			     " m_srcs=%llu m_srcs_off=%llu"
			     " da_draws=%llu da_ready=%llu da_walks=%llu da_walk_us=%llu"
			     " da_q=%llu da_nohint=%llu da_present=%llu da_busy=%llu da_done=%llu da_fail=%llu"
			     " da_work_us=%llu da_hit=%llu da_stale=%llu da_late=%llu da_miss=%llu da_words=%llu"
			     " da_noplan=%llu da_flip=%llu da_refresh=%llu da_stale_old=%llu da_predicted=%llu"
			     " da_move=%llu da_take_us=%llu da_queue_us=%llu da_words_clean=%llu"
			     " img_ins_us=%llu img_free_us=%llu img_ovl_us=%llu"
			     " as_n=%llu as_us=%llu as_lock_us=%llu as_drain=%llu as_drain_us=%llu"
			     " img_rec_hit=%llu img_rec_put=%llu"
			     " rec_n=%llu rec_kb=%llu rec_direct=%llu rec_direct_us=%llu"
			     " rec_drain=%llu rec_drain_us=%llu rec_full=%llu rec_full_us=%llu"
			     " rec_work_us=%llu rec_idle_us=%llu cpu_record_us=%llu"
			     " tf_free=%llu tf_lock=%llu tf_bad=%llu"
			     " pmap_hit=%llu pmap_miss=%llu prot_held_us=%llu"
			     " gds_bar=%llu gds_skip=%llu img_ww_skip=%llu"
			     " swbar_loc=%llu swbar_flush=%llu ds_alloc=%llu"
			     " swdefer_ok=%llu swdefer_no=%llu swdefer_n=%llu"
			     " da_runs=%llu da_probe=%llu"
			     "\n",
			     r.cfg->flip_status.count, d(FS::Counter::Logs), dus(FS::Counter::LogNs),
			     dus(FS::Counter::LogGpuNs), dus(FS::Counter::DrawPopNs), dus(FS::Counter::DrawCheckNs),
			     dus(FS::Counter::DrawTargetsNs), dus(FS::Counter::DrawProgramsNs),
			     dus(FS::Counter::DrawBindingsNs), dus(FS::Counter::DrawVertexNs),
			     dus(FS::Counter::DrawAcquireRtNs), dus(FS::Counter::DrawPipelineNs),
			     dus(FS::Counter::DrawCommitNs), dus(FS::Counter::DrawEmitNs),
			     dus(FS::Counter::DispatchPopNs), dus(FS::Counter::DispatchProgramNs),
			     dus(FS::Counter::DispatchPipelineNs), dus(FS::Counter::DispatchBindingsNs),
			     dus(FS::Counter::DispatchCommitNs), dus(FS::Counter::DispatchEmitNs),
			     dus(FS::Counter::ProgPrepareNs), dus(FS::Counter::ProgKeyNs),
			     dus(FS::Counter::ProgMaterializeNs), dus(FS::Counter::ProgPermNs),
			     d(FS::Counter::ProgReads), d(FS::Counter::ProgCleanReads),
			     dus(FS::Counter::MatEvalNs), dus(FS::Counter::MatAssembleNs),
			     dus(FS::Counter::MatSpecNs), d(FS::Counter::MatEvalInsts),
			     d(FS::Counter::MatFailures), d(FS::Counter::MatMemoHits),
			     d(FS::Counter::MatMemoMisses), dus(FS::Counter::MatReadNs),
			     d(FS::Counter::MatEvalWide), dus(FS::Counter::BindResolveTexNs),
			     d(FS::Counter::BindResolveTex), dus(FS::Counter::BindFindTexNs),
			     d(FS::Counter::BindFindTex), dus(FS::Counter::BindBuffersNs),
			     dus(FS::Counter::BindSamplersNs), dus(FS::Counter::BindBufFindNs),
			     dus(FS::Counter::BindBufObtainNs), dus(FS::Counter::BindBufSyncNs),
			     dus(FS::Counter::BindBufUploadNs), d(FS::Counter::BindBufN),
			     d(FS::Counter::BindTexMemoHits), d(FS::Counter::RtMemoHits),
			     dus(FS::Counter::ObtainBufNs), d(FS::Counter::ObtainBufs),
			     d(FS::Counter::SyncBufUploads), dus(FS::Counter::LockSpinNs),
			     d(FS::Counter::LockSpins), dus(FS::Counter::LockSpinGpuNs),
			     d(FS::Counter::GlobalBarriers), d(FS::Counter::ImageBarriers),
			     d(FS::Counter::ShaderWriteBarriers), d(FS::Counter::RenderPassBegins),
			     d(FS::Counter::PendingOps), dus(FS::Counter::PendingOpsNs),
			     d(FS::Counter::GlobalBarriersSkipped), d(FS::Counter::FaultsMain),
			     dus(FS::Counter::FaultMainNs), d(FS::Counter::ImgInserts), d(FS::Counter::ImgFrees),
			     d(FS::Counter::ImgUploads), d(FS::Counter::ImgUploadBytes) / 1024u,
			     dus(FS::Counter::ImgUploadNs), dus(FS::Counter::ImgInitNs),
			     dus(FS::Counter::ImgCopyNs), d(FS::Counter::CbankCopyCpu), d(FS::Counter::CbankCopyGpu),
			     d(FS::Counter::CbankCopyBytes) / 1024u, dus(FS::Counter::AsyncCopyWaitNs),
			     d(FS::Counter::AsyncCopyWaits), dus(FS::Counter::ProtectNs),
			     d(FS::Counter::ProtectPages), dus(FS::Counter::ProtectWorkerNs),
			     d(FS::Counter::ProtectWorkerPages), dus(FS::Counter::ProtectDrainNs),
			     d(FS::Counter::ProtectDrains), d(FS::Counter::ProtectCalls),
			     d(FS::Counter::ProtectRoCalls), d(FS::Counter::ProtectRoPages),
			     d(FS::Counter::ProtectNaCalls), d(FS::Counter::ProtectNaPages),
			     dus(FS::Counter::ProtectRwNs), d(FS::Counter::ProtectRwPages),
			     dus(FS::Counter::ProtectMaskedNs), d(FS::Counter::ProtectMaskedCalls),
			     dus(FS::Counter::ProtectGpuNs), d(FS::Counter::ProtectGpuCalls),
			     d(FS::Counter::ProtectGpuPages), d(FS::Counter::BufCreates),
			     dus(FS::Counter::BufCreateNs), d(FS::Counter::AsyncCopyGpuWaits),
			     d(FS::Counter::ImgImports), d(FS::Counter::ImgImportBytes) / 1024u,
			     d(FS::Counter::ImgImportPieces), d(FS::Counter::HostReadWaits),
			     dus(FS::Counter::HostReadWaitNs), d(FS::Counter::ImgDetileDispatches),
			     d(FS::Counter::ImgCopyRegions), d(FS::Counter::ImgDeferred),
			     d(FS::Counter::ImgDeferredBytes) / 1024u, d(FS::Counter::ImgPendingUploads),
			     d(FS::Counter::ImgPendingBytes) / 1024u, d(FS::Counter::ImgMinLodViews),
			     dus(FS::Counter::BdaPrepareNs), d(FS::Counter::BdaPrepares),
			     d(FS::Counter::SrtPageMisses), d(FS::Counter::ClampMemoMisses),
			     d(FS::Counter::SrtMemoHits), d(FS::Counter::SrtMemoMisses),
			     d(FS::Counter::SrtMemoStale), d(FS::Counter::SrtMemoSkips),
			     d(FS::Counter::SrtMemoReads), d(FS::Counter::BufEpochHits),
			     d(FS::Counter::BdaRegionsScanned), d(FS::Counter::BdaRegionsSkipped),
			     d(FS::Counter::BdaRegionsBitSkipped), d(FS::Counter::BdaBitMismatches),
			     d(FS::Counter::BackingPageHits), d(FS::Counter::BackingPageMisses),
			     d(FS::Counter::MatNodes), d(FS::Counter::MatNodesNeeded),
			     d(FS::Counter::MatReadNodes), d(FS::Counter::MatReadNodesNeeded),
			     d(FS::Counter::MatSources), d(FS::Counter::MatSourcesOff),
			     d(FS::Counter::DrawAheadSeen), d(FS::Counter::DrawAheadReady),
			     d(FS::Counter::DrawAheadWalks), dus(FS::Counter::DrawAheadNs),
			     d(FS::Counter::DrawAheadQueued), d(FS::Counter::DrawAheadNoHint),
			     d(FS::Counter::DrawAheadPresent), d(FS::Counter::DrawAheadBusy),
			     d(FS::Counter::DrawAheadDone), d(FS::Counter::DrawAheadFailed),
			     dus(FS::Counter::DrawAheadWorkerNs), d(FS::Counter::DrawAheadHits),
			     d(FS::Counter::DrawAheadStale), d(FS::Counter::DrawAheadLate),
			     d(FS::Counter::DrawAheadMisses), d(FS::Counter::DrawAheadWords),
			     d(FS::Counter::DrawAheadNoPlan), d(FS::Counter::DrawAheadHintFlip),
			     d(FS::Counter::DrawAheadRefresh), d(FS::Counter::DrawAheadStaleOld),
			     d(FS::Counter::DrawAheadPredicted), d(FS::Counter::DrawAheadMoves),
			     dus(FS::Counter::DrawAheadTakeNs), dus(FS::Counter::DrawAheadQueueNs),
			     d(FS::Counter::DrawAheadCleanWords), dus(FS::Counter::ImgInsertNs),
			     dus(FS::Counter::ImgFreeNs), dus(FS::Counter::ImgOverlapNs),
			     d(FS::Counter::AsyncSubmits), dus(FS::Counter::AsyncSubmitNs),
			     dus(FS::Counter::AsyncSubmitLockNs),
			     d(FS::Counter::AsyncSubmitDrains), dus(FS::Counter::AsyncSubmitDrainNs),
			     d(FS::Counter::ImgRecycleHits), d(FS::Counter::ImgRecyclePuts),
			     d(FS::Counter::RecordPackets), d(FS::Counter::RecordBytes) / 1024u,
			     d(FS::Counter::RecordDirect), dus(FS::Counter::RecordDirectNs),
			     d(FS::Counter::RecordDrains), dus(FS::Counter::RecordDrainNs),
			     d(FS::Counter::RecordFull), dus(FS::Counter::RecordFullNs),
			     dus(FS::Counter::RecordWorkNs), dus(FS::Counter::RecordIdleNs),
			     cpu(FS::ThreadRole::Record),
			     d(FS::Counter::TrackFreeHits), d(FS::Counter::TrackFreeLocked),
			     d(FS::Counter::TrackFreeMismatch), d(FS::Counter::ProtectMapHits),
			     d(FS::Counter::ProtectMapMisses), dus(FS::Counter::ProtectHeldNs),
			     d(FS::Counter::GdsBarriers), d(FS::Counter::GdsBarriersSkipped),
			     d(FS::Counter::ImageWriteBarriersSkipped),
			     d(FS::Counter::ShaderWriteBarriersLocal),
			     d(FS::Counter::ShaderWriteBarriersFlushed),
			     d(FS::Counter::DescriptorAllocations),
			     d(FS::Counter::ShaderWriteBarriersDeferrable),
			     d(FS::Counter::ShaderWriteBarriersPlain),
			     d(FS::Counter::ShaderWriteBarriersDeferred),
			     d(FS::Counter::DrawAheadRuns), d(FS::Counter::DrawAheadProbes));
			{
				// Why render passes ended this frame (end_*), and how many of those ends were followed
				// by a pass on the same targets (restart_*), per RenderPassEnd reason.
				static constexpr std::array<const char*, 15> rp_names {
				    "state",    "target",   "binding",  "gds",   "shader_write",
				    "dispatch", "buf_upload", "buf_copy", "img_upload", "tiler",
				    "clear",    "sanitize", "download", "submit", "other"};
				static_assert(static_cast<size_t>(FS::Counter::RpRestartState) -
				                  static_cast<size_t>(FS::Counter::RpEndState) ==
				              rp_names.size());
				static_assert(static_cast<size_t>(FS::Counter::RpRestartOther) -
				                  static_cast<size_t>(FS::Counter::RpRestartState) + 1 ==
				              rp_names.size());
				const auto         rp_end     = static_cast<size_t>(FS::Counter::RpEndState);
				const auto         rp_restart = static_cast<size_t>(FS::Counter::RpRestartState);
				unsigned long long rp_ends    = 0;
				unsigned long long rp_starts  = 0;
				std::string        end_text;
				std::string        restart_text;
				for (size_t i = 0; i < rp_names.size(); i++) {
					const auto ends     = d(static_cast<FS::Counter>(rp_end + i));
					const auto restarts = d(static_cast<FS::Counter>(rp_restart + i));
					rp_ends += ends;
					rp_starts += restarts;
					end_text += std::string(" end_") + rp_names[i] + "=" + std::to_string(ends);
					restart_text +=
					    std::string(" restart_") + rp_names[i] + "=" + std::to_string(restarts);
				}
				LOGF("FrameTrace-rp: n=%" PRIu64 " ends=%llu restarts=%llu%s%s" "\n",
				     r.cfg->flip_status.count, rp_ends, rp_starts, end_text.c_str(),
				     restart_text.c_str());
			}
			{
				// Counters added from session 56 on, by name.
				struct NamedCounter {
					const char* name;
					FS::Counter counter;
					bool        micros;
				};
				static constexpr NamedCounter named[] = {
				    {"ds_ring_new", FS::Counter::DescriptorRingSets, false},
				    {"ds_ring_grow", FS::Counter::DescriptorRingGrows, false},
				    {"ds_ring_n", FS::Counter::DescriptorRingIssued, false},
				    {"rec_pack", FS::Counter::RecordPackDraws, false},
				    {"rec_pack_cs", FS::Counter::RecordPackDispatches, false},
				    {"rec_bind", FS::Counter::RecordPackBinds, false},
				    // A byte counter through the micros column: kB (1000 bytes).
				    {"rec_pack_kb", FS::Counter::RecordPackBytes, true},
				    {"rec_direct_busy", FS::Counter::RecordDirectBusy, false},
				    {"rec_spin_us", FS::Counter::RecordSpinNs, true},
				    {"rec_sleep", FS::Counter::RecordSleeps, false},
				    {"prot_spin_us", FS::Counter::ProtectSpinNs, true},
				    {"prot_spin_calls", FS::Counter::ProtectSpinCalls, false},
				    {"prot_spin_pages", FS::Counter::ProtectSpinPages, false},
				    {"prot_spin_gpu_us", FS::Counter::ProtectSpinGpuNs, true},
				    {"prot_spin_gpu_calls", FS::Counter::ProtectSpinGpuCalls, false},
				    {"prot_spin_gpu_pages", FS::Counter::ProtectSpinGpuPages, false},
				    {"sync_noop", FS::Counter::SyncNoop, false},
				    {"sf_skip", FS::Counter::SyncFreeSkips, false},
				    {"sf_bad", FS::Counter::SyncFreeMismatch, false},
				    {"tex_inval", FS::Counter::TexInvalidations, false},
				    {"tex_inval_empty", FS::Counter::TexInvalidateEmpty, false},
				    {"tex_hint_zero", FS::Counter::TexHintZero, false},
				    {"pb_pages", FS::Counter::BatchPages, false},
				    {"pb_flush", FS::Counter::BatchFlushes, false},
				    {"pb_runs", FS::Counter::BatchRuns, false},
				    {"pb_kb", FS::Counter::BatchKb, false},
				    {"pb_merged", FS::Counter::BatchMerged, false},
				    {"pb_wait_us", FS::Counter::ApplyWaitNs, true},
				    {"pb_wait_gpu_us", FS::Counter::ApplyWaitGpuNs, true},
				    {"pb_inval_flush", FS::Counter::BatchInvalidateFlushes, false},
				    {"pb_refault", FS::Counter::BatchRefault, false},
				    {"pb_stuck", FS::Counter::BatchStuck, false},
				    {"pb_check", FS::Counter::BatchChecks, false},
				    {"pb_bad", FS::Counter::BatchCheckBad, false},
				    {"pb_bad_rw", FS::Counter::BatchCheckBadRw, false},
				    {"da_req", FS::Counter::DrawAheadRequests, false},
				    {"da_fan", FS::Counter::DrawAheadFan, false},
				    {"da_fan_canon", FS::Counter::DrawAheadFanCanon, false},
				    {"da_unused", FS::Counter::DrawAheadUnused, false},
				    {"da_unused_ps", FS::Counter::DrawAheadUnusedPixel, false},
				    {"da_mesh_vs", FS::Counter::DrawAheadMeshStages, false},
				    {"da_px_off", FS::Counter::DrawAheadPixelOff, false},
				    {"da_classes", FS::Counter::DrawAheadClasses, false},
				    {"da_class_join", FS::Counter::DrawAheadClassShared, false},
				    {"da_class_us", FS::Counter::DrawAheadClassNs, true},
				    {"da_clone", FS::Counter::DrawAheadClones, false},
				    {"da_ccd_x", FS::Counter::DrawAheadCrossCcd, false},
				    {"texlru_n", FS::Counter::TexLruTouches, false},
				    {"texlru_rep", FS::Counter::TexLruRepeats, false},
				    {"texfast_ok", FS::Counter::TexFastOk, false},
				    {"texfast_no", FS::Counter::TexFastNo, false},
				    {"texfast_no_stamp", FS::Counter::TexFastNoStamp, false},
				    {"texfast_no_state", FS::Counter::TexFastNoState, false},
				    {"texfast_rec", FS::Counter::TexFastRecord, false},
				    {"texfast_bad", FS::Counter::TexFastBad, false},
				    {"texmemo_empty", FS::Counter::TexMemoEmpty, false},
				    {"texmemo_collide", FS::Counter::TexMemoCollide, false},
				    {"texmemo_stale", FS::Counter::TexMemoStale, false},
				    {"texmemo_key_miss", FS::Counter::TexMemoKeyMisses, false},
				    {"clamp_miss_epoch", FS::Counter::ClampMissEpoch, false},
				    {"clamp_miss_key", FS::Counter::ClampMissKey, false},
				    {"clampvma_miss", FS::Counter::ClampVmaMisses, false},
				    {"smp_miss", FS::Counter::SamplerMemoMisses, false},
				    // Session 57, A2/A3 (page protection).
				    {"pb_skip_would", FS::Counter::ApplySkipWould, false},
				    {"pb_skip_would_wait_us", FS::Counter::ApplySkipWouldWaitNs, true},
				    {"pb_skip_would_wait_gpu_us", FS::Counter::ApplySkipWouldWaitGpuNs, true},
				    {"pb_skip", FS::Counter::ApplySkips, false},
				    {"pb_skip_blk_rw", FS::Counter::ApplySkipBlockRw, false},
				    {"pb_skip_blk_ro", FS::Counter::ApplySkipBlockRo, false},
				    {"pb_wait_sync_us", FS::Counter::ApplyWaitSyncNs, true},
				    {"pb_wait_scope_us", FS::Counter::ApplyWaitScopeNs, true},
				    {"pb_wait_range_us", FS::Counter::ApplyWaitRangeNs, true},
				    {"pb_wait_worker_us", FS::Counter::ApplyWaitWorkerNs, true},
				    {"pb_sync_noprot", FS::Counter::ApplySyncNoProtect, false},
				    {"pb_sync_noprot_wait_us", FS::Counter::ApplySyncNoProtectWaitNs, true},
				    {"pb_inflight_bad", FS::Counter::ApplyInflightBad, false},
				    {"fw_n", FS::Counter::FaultWrites, false},
				    {"fw_win_same", FS::Counter::FaultWinSame, false},
				    {"fw_win_recent", FS::Counter::FaultWinRecent, false},
				    {"fw_seq", FS::Counter::FaultWinSeq, false},
				    {"fw_win_armed", FS::Counter::FaultWinArmed, false},
				    {"fw_widened", FS::Counter::FaultWidened, false},
				    {"fw_refault", FS::Counter::FaultRefault, false},
				    // A byte counter through the micros column: kB (1000 bytes).
				    {"sync_up_kb", FS::Counter::SyncBufUploadBytes, true},
				    // Session 57, A4 (record publish).
				    {"rec_pub", FS::Counter::RecordPublishes, false},
				    {"rec_staged", FS::Counter::RecordStaged, false},
				    {"rec_pub_forced", FS::Counter::RecordForcedPublishes, false},
				    {"rec_wake", FS::Counter::RecordWakes, false},
				    {"rec_drain_lock", FS::Counter::RecordDrainLocks, false},
				    {"rec_tail_rd", FS::Counter::RecordTailReads, false},
				    {"rec_ccd_n", FS::Counter::RecordCcdChecks, false},
				    {"rec_ccd_x", FS::Counter::RecordCrossCcd, false},
				    {"rec_sleep_gpu", FS::Counter::RecordSleepsGpu, false},
				    {"rec_spin_gpu_us", FS::Counter::RecordSpinNsGpu, true},
				    {"rec_fpwb", FS::Counter::RecordFlushBuffers, false},
				    // Session 57, A1 (sticky pages).
				    {"stk_flt", FS::Counter::StickyFaults, false},
				    {"stk_flt_rep", FS::Counter::StickyFaultRepeat, false},
				    {"stk_flt_same", FS::Counter::StickyFaultRepeatSame, false},
				    {"stk_flt_rep_gpu", FS::Counter::StickyFaultRepeatGpu, false},
				    {"stk_flt_rep_img", FS::Counter::StickyFaultRepeatImg, false},
				    {"stk_arm", FS::Counter::StickyArmPages, false},
				    {"stk_arm_hot", FS::Counter::StickyArmHot, false},
				    {"stk_arm_hot_bda", FS::Counter::StickyArmHotBda, false},
				    {"stk_arm_hot_img", FS::Counter::StickyArmHotImg, false},
				    {"stk_hot", FS::Counter::StickyHotPages, false},
				    {"stk_cand", FS::Counter::StickyCandidates, false},
				    {"stk_vp_save", FS::Counter::StickySavedCalls, false},
				    {"stk_chk_est", FS::Counter::StickyCheckEstimate, false},
				    {"stk_stream_hot", FS::Counter::StickyStreamHot, false},
				    // Session 57, E1/E2/E9 (draw statistics).
				    {"dp_between_hard", FS::Counter::DrawBetweenHard, false},
				    {"dp_n", FS::Counter::DrawStatDraws, false},
				    {"dp_pure", FS::Counter::DrawStatPure, false},
				    {"dp_fast", FS::Counter::DrawStatFast, false},
				    {"dp_clean", FS::Counter::DrawStatClean, false},
				    {"dp_img_new", FS::Counter::DrawDirtyImgNew, false},
				    {"dp_img_up", FS::Counter::DrawDirtyImgUp, false},
				    {"dp_meta", FS::Counter::DrawDirtyMeta, false},
				    {"dp_prot", FS::Counter::DrawDirtyProt, false},
				    {"dp_buf_new", FS::Counter::DrawDirtyBufNew, false},
				    {"dp_buf_up", FS::Counter::DrawDirtyBufUp, false},
				    {"dp_gpu_write", FS::Counter::DrawDirtyGpuWrite, false},
				    {"dp_obj_new", FS::Counter::DrawDirtyObjNew, false},
				    {"dp_sync", FS::Counter::DrawDirtySync, false},
				    {"dp_tex_slow", FS::Counter::DrawDirtyTexSlow, false},
				    {"dp_buf_slow", FS::Counter::DrawDirtyBufSlow, false},
				    {"dp_lru", FS::Counter::DrawDirtyLru, false},
				    {"dp_memo", FS::Counter::DrawDirtyMemo, false},
				    {"dp_m1", FS::Counter::DrawDirtyM1, false},
				    {"dp_stream_wrap", FS::Counter::DrawDirtyStream, false},
				    {"dp_bar", FS::Counter::DrawDirtyBarrier, false},
				    {"dp_tail_hard", FS::Counter::DrawTailHard, false},
				    {"dp_t_img_up", FS::Counter::DrawTailImgUp, false},
				    {"dp_t_meta", FS::Counter::DrawTailMeta, false},
				    {"dp_t_prot", FS::Counter::DrawTailProt, false},
				    {"dp_t_sync", FS::Counter::DrawTailSync, false},
				    {"dp_t_bar", FS::Counter::DrawTailBarrier, false},
				    {"dp_stream_maps", FS::Counter::DrawStreamMaps, false},
				    {"dp_runs_1", FS::Counter::DrawPureRuns1, false},
				    {"dp_runs_2", FS::Counter::DrawPureRuns2, false},
				    {"dp_runs_4", FS::Counter::DrawPureRuns4, false},
				    {"dp_runs_8", FS::Counter::DrawPureRuns8, false},
				    {"dp_runs_16", FS::Counter::DrawPureRuns16, false},
				    {"dp_runs_32", FS::Counter::DrawPureRuns32, false},
				    {"dp_runs_64", FS::Counter::DrawPureRuns64, false},
				    {"dp_rd_1", FS::Counter::DrawPureRunDraws1, false},
				    {"dp_rd_2", FS::Counter::DrawPureRunDraws2, false},
				    {"dp_rd_4", FS::Counter::DrawPureRunDraws4, false},
				    {"dp_rd_8", FS::Counter::DrawPureRunDraws8, false},
				    {"dp_rd_16", FS::Counter::DrawPureRunDraws16, false},
				    {"dp_rd_32", FS::Counter::DrawPureRunDraws32, false},
				    {"dp_rd_64", FS::Counter::DrawPureRunDraws64, false},
				    {"hb_runs_1", FS::Counter::EdgeRuns1, false},
				    {"hb_runs_2", FS::Counter::EdgeRuns2, false},
				    {"hb_runs_4", FS::Counter::EdgeRuns4, false},
				    {"hb_runs_8", FS::Counter::EdgeRuns8, false},
				    {"hb_runs_16", FS::Counter::EdgeRuns16, false},
				    {"hb_runs_32", FS::Counter::EdgeRuns32, false},
				    {"hb_runs_64", FS::Counter::EdgeRuns64, false},
				    {"hb_rd_1", FS::Counter::EdgeRunDraws1, false},
				    {"hb_rd_2", FS::Counter::EdgeRunDraws2, false},
				    {"hb_rd_4", FS::Counter::EdgeRunDraws4, false},
				    {"hb_rd_8", FS::Counter::EdgeRunDraws8, false},
				    {"hb_rd_16", FS::Counter::EdgeRunDraws16, false},
				    {"hb_rd_32", FS::Counter::EdgeRunDraws32, false},
				    {"hb_rd_64", FS::Counter::EdgeRunDraws64, false},
				    {"hb_cut_pass", FS::Counter::EdgeCutPass, false},
				    {"hb_cut_cs", FS::Counter::EdgeCutDispatch, false},
				    {"hb_cut_bar", FS::Counter::EdgeCutBarrier, false},
				    {"hb_cut_up", FS::Counter::EdgeCutUpload, false},
				    {"hb_cut_sub", FS::Counter::EdgeCutSubmit, false},
				    {"e9_n", FS::Counter::E9Sets, false},
				    {"e9_push", FS::Counter::E9Push, false},
				    {"e9_adj", FS::Counter::E9Adjacent, false},
				    {"e9_seen", FS::Counter::E9Seen, false},
				    {"e9_img", FS::Counter::E9SameImages, false},
				    {"e9_buf", FS::Counter::E9SameBuffers, false},
				    {"e9_bufr", FS::Counter::E9SameBufferRanges, false},
				    {"e9_base", FS::Counter::E9SameBase, false},
				    {"e9_full", FS::Counter::E9SameFull, false},
				    {"e9_adj_base", FS::Counter::E9AdjacentBase, false},
				    {"e9_bufs", FS::Counter::E9BufferInfos, false},
				    {"e9_stream", FS::Counter::E9StreamInfos, false},
				    {"e9_rd_1", FS::Counter::E9RunDraws1, false},
				    {"e9_rd_2", FS::Counter::E9RunDraws2, false},
				    {"e9_rd_4", FS::Counter::E9RunDraws4, false},
				    {"e9_rd_8", FS::Counter::E9RunDraws8, false},
				    {"e9_rd_16", FS::Counter::E9RunDraws16, false},
				    {"e9_rd_32", FS::Counter::E9RunDraws32, false},
				    {"e9_rd_64", FS::Counter::E9RunDraws64, false},
				    // Session 58, B9 (dynamic offsets).
				    {"e9_dyn_ok", FS::Counter::E9DynOk, false},
				    {"e9_dyn_over", FS::Counter::E9DynOver, false},
				    {"e9_dyn_cap", FS::Counter::E9DynCapped, false},
				    {"e9_dyn_lay", FS::Counter::E9DynLayoutOver, false},
				    {"e9_dyn_n1", FS::Counter::E9DynNeed1, false},
				    {"e9_dyn_n2", FS::Counter::E9DynNeed2, false},
				    {"e9_dyn_n4", FS::Counter::E9DynNeed4, false},
				    {"e9_dyn_n8", FS::Counter::E9DynNeed8, false},
				    {"e9_dyn_nmore", FS::Counter::E9DynNeedMore, false},
				    {"e9_dyn_limit", FS::Counter::E9DynLimit, false},
				    {"e9_dyn_ulimit", FS::Counter::E9DynLimitUniform, false},
				    // Session 57, A6/A7 and track B.
				    {"snap_keep_copy", FS::Counter::SnapKeepCopies, false},
				    {"snap_keep_grow", FS::Counter::SnapKeepGrows, false},
				    {"buflru_n", FS::Counter::BufLruTouches, false},
				    {"buflru_rep", FS::Counter::BufLruRepeats, false},
				    // Session 58, B4 follow-up (snapshot copies).
				    {"snap_cp_b", FS::Counter::SnapCopyBytes, false},
				    {"snap_cp_same_b", FS::Counter::SnapCopySameBytes, false},
				    {"snap_cp_vec", FS::Counter::SnapCopyVectors, false},
				    {"snap_cp_same_vec", FS::Counter::SnapCopySameVectors, false},
				    {"snap_cp_eq", FS::Counter::SnapCopyUnchanged, false},
				    {"snap_last_cp", FS::Counter::SnapLastUseCopies, false},
				    {"snap_last_b", FS::Counter::SnapLastUseBytes, false},
				    // Session 58, M2 step 1 (buffer request memo).
				    {"bfast_hit", FS::Counter::BufFastOk, false},
				    {"bfast_miss", FS::Counter::BufFastNo, false},
				    {"bfast_stale", FS::Counter::BufFastStale, false},
				    {"bfast_skip", FS::Counter::BufFastSkip, false},
				    {"bfast_bad", FS::Counter::BufFastBad, false},
				    // Session 58, A3 phase 2 (gate "protbatch2").
				    {"pb2_pass", FS::Counter::PassPasses, false},
				    {"pb2_sync", FS::Counter::PassSyncs, false},
				    {"pb2_reg", FS::Counter::PassRegions, false},
				    {"pb2_vp", FS::Counter::PassProtectCalls, false},
				    {"pb2_vp_pages", FS::Counter::PassProtectPages, false},
				    {"pb2_vp_adj", FS::Counter::PassProtectAdjacent, false},
				    {"pb2_vp_near", FS::Counter::PassProtectNear, false},
				    {"pb2_gap", FS::Counter::PassGapRuns, false},
				    {"pb2_gap_pages", FS::Counter::PassGapPages, false},
				    {"pb2_up", FS::Counter::PassUploads, false},
				    // Session 83, W1: the division of bda_us.
				    {"bda_hit", FS::Counter::BdaPrepareHits, false},
				    {"bda_rng", FS::Counter::BdaRanges, false},
				    {"bda_rng_e", FS::Counter::BdaRangesEmpty, false},
				    {"bda_drng", FS::Counter::BdaDirtyRanges, false},
				    // Session 83: the arming proof of knob "mutwide".
				    {"mw_n", FS::Counter::MutWideScopes, false},
				    // Session 83, gate "bindpack" and its self-check.
				    {"tnull_hit", FS::Counter::NullTexHits, false},
				    {"tnull_miss", FS::Counter::NullTexMisses, false},
				    {"bp_mask", FS::Counter::BindKindMasks, false},
				    {"bp_bad", FS::Counter::BindPackBad, false},
				    // Session 84, gate "bdalap": what PrepareBda actually costs.
				    {"bda_probe_us", FS::Counter::BdaProbeNs, true},
				    {"bda_scan_us", FS::Counter::BdaScanNs, true},
				    {"bda_lap_n", FS::Counter::BdaLaps, false},
				    // Session 84, gate "bindpack", the package's fourth item.
				    {"bp_dsc", FS::Counter::BindPackDescSets, false},
				    {"bp_local_make", FS::Counter::BindPackLocalMake, false},
				    {"bp_local_skip", FS::Counter::BindPackLocalSkip, false},
				    // Session 84, gate "slotstat": the route-C per-slot census.
				    {"sl_stage_n", FS::Counter::SlotStages, false},
				    {"sl_stage_all", FS::Counter::SlotStagesAll, false},
				    {"sl_img_n", FS::Counter::SlotImages, false},
				    {"sl_img_same", FS::Counter::SlotImagesSame, false},
				    {"sl_img_view", FS::Counter::SlotImagesView, false},
				    {"sl_smp_n", FS::Counter::SlotSamplers, false},
				    {"sl_smp_same", FS::Counter::SlotSamplersSame, false},
				    {"sl_buf_n", FS::Counter::SlotBuffers, false},
				    {"sl_buf_same", FS::Counter::SlotBuffersSame, false},
				    {"sl_buf_ring", FS::Counter::SlotBuffersRing, false},
				    {"sl_over", FS::Counter::SlotOverflow, false},
				    // Session 83, gate "plkstat": PipelineCache::m_mutex, site by site.
				    {"pl_prog_wait_us", FS::Counter::PipeLockProgWaitNs, true},
				    {"pl_prog_hold_us", FS::Counter::PipeLockProgHoldNs, true},
				    {"pl_prog_n", FS::Counter::PipeLockProgN, false},
				    {"pl_pipe_wait_us", FS::Counter::PipeLockPipeWaitNs, true},
				    {"pl_pipe_hold_us", FS::Counter::PipeLockPipeHoldNs, true},
				    {"pl_pipe_n", FS::Counter::PipeLockPipeN, false},
				    {"pl_cs_wait_us", FS::Counter::PipeLockCsWaitNs, true},
				    {"pl_cs_hold_us", FS::Counter::PipeLockCsHoldNs, true},
				    {"pl_cs_n", FS::Counter::PipeLockCsN, false},
				    // Session 59, B9 ceiling (gate "drawstat").
				    {"cb_pool_n", FS::Counter::CommitPoolSets, false},
				    {"cb_pool_tr_us", FS::Counter::CommitPoolTransitNs, true},
				    {"cb_pool_wr_us", FS::Counter::CommitPoolWriteNs, true},
				    {"cb_pool_em_us", FS::Counter::CommitPoolEmitNs, true},
				    {"cb_push_n", FS::Counter::CommitPushSets, false},
				    {"cb_push_tr_us", FS::Counter::CommitPushTransitNs, true},
				    {"cb_push_wr_us", FS::Counter::CommitPushWriteNs, true},
				    {"cb_push_em_us", FS::Counter::CommitPushEmitNs, true},
				    // Session 59, gate "dawalk".
				    {"da_wjobs", FS::Counter::DrawAheadWalkJobs, false},
				    {"da_wlag_us", FS::Counter::DrawAheadWalkLagNs, true},
				    {"da_wdepth", FS::Counter::DrawAheadWalkDepth, false},
				    {"da_wskip", FS::Counter::DrawAheadWalkSkipped, false},
				    {"da_wdrop", FS::Counter::DrawAheadWalkDropped, false},
				    // Session 59, gate "rtfast".
				    {"rt_fast_ok", FS::Counter::RtFastOk, false},
				    {"rt_fast_no", FS::Counter::RtFastNo, false},
				    {"rt_fast_stale", FS::Counter::RtFastStale, false},
				    {"rt_fast_rec", FS::Counter::RtFastRecord, false},
				    {"rt_fast_stencil", FS::Counter::RtFastStencil, false},
				    // Session 60, B3 (gate "progmemo").
				    {"pmemo_hit", FS::Counter::ProgMemoHit, false},
				    {"pmemo_miss", FS::Counter::ProgMemoMiss, false},
				    {"pmemo_stale", FS::Counter::ProgMemoStale, false},
				    {"pmemo_bad", FS::Counter::ProgMemoBad, false},
				    {"pmemo_eq_vs", FS::Counter::ProgMemoEqVs, false},
				    {"pmemo_eq_ps", FS::Counter::ProgMemoEqPs, false},
				    {"pmemo_pipe", FS::Counter::ProgMemoPipe, false},
				    {"pmemo_chk_us", FS::Counter::ProgMemoCheckNs, true},
				    // Session 60, item 4 (gate "armdefer").
				    {"arm_req", FS::Counter::ArmRequestPages, false},
				    {"arm_settled", FS::Counter::ArmSettledPages, false},
				    {"arm_wait", FS::Counter::ArmWaitPages, false},
				    {"arm_flush", FS::Counter::ArmSyncFlushes, false},
				    {"arm_noflush", FS::Counter::ArmFlushSkips, false},
				    {"arm_bad", FS::Counter::ArmBad, false},
				    // Session 61 ceilings (items 2 and 3).
				    {"up_series", FS::Counter::SyncBufUploadSeries, false},
				    {"da_ep_same", FS::Counter::DrawAheadEpochSame, false},
				    {"da_ep_moved", FS::Counter::DrawAheadEpochMoved, false},
				    {"da_ep_regions", FS::Counter::DrawAheadEpochRegions, false},
				    {"da_stale_r1", FS::Counter::DrawAheadStaleFirst, false},
				    {"da_stale_ep_same", FS::Counter::DrawAheadStaleEpochSame, false},
				    {"rec_throttle", FS::Counter::RecordThrottled, false},
				    {"da_unchecked", FS::Counter::DrawAheadUnchecked, false},
				    {"da_direct", FS::Counter::DrawAheadDirect, false},
				    {"da_direct_no", FS::Counter::DrawAheadDirectNo, false},
				    // Session 62 ceilings (item 3).
				    {"ob_stream", FS::Counter::ObtainStreamCopies, false},
				    {"ob_stream_kb", FS::Counter::ObtainStreamBytes, true},
				    {"cb_same", FS::Counter::CbSame, false},
				    {"cb_diff", FS::Counter::CbDiff, false},
				    {"cb_new", FS::Counter::CbNew, false},
				    {"cb_same_ep", FS::Counter::CbSameEpoch, false},
				    {"cb_diff_ep", FS::Counter::CbDiffEpoch, false},
				    {"cb_same_ring", FS::Counter::CbSameRing, false},
				    {"cb_stat_us", FS::Counter::CbStatNs, true},
				    {"ob_stream_us", FS::Counter::ObtainStreamNs, true},
				    {"cb_copy_us", FS::Counter::CbankCopyNs, true},
				    {"rec_img", FS::Counter::RecordImageBarrierPackets, false},
				    {"rec_up", FS::Counter::RecordUploadPackets, false},
				    // Session 64, E4/E6 (shadow resolution).
				    {"sh_jobs", FS::Counter::ShadowJobs, false},
				    {"sh_drop", FS::Counter::ShadowDropped, false},
				    {"sh_over", FS::Counter::ShadowOver, false},
				    {"sh_img", FS::Counter::ShadowImages, false},
				    {"sh_img_gone", FS::Counter::ShadowImgGone, false},
				    {"sh_img_stale", FS::Counter::ShadowImgStale, false},
				    {"sh_img_slow", FS::Counter::ShadowImgSlow, false},
				    {"sh_img_view", FS::Counter::ShadowImgView, false},
				    {"sh_img_fast", FS::Counter::ShadowImgFast, false},
				    {"sh_buf", FS::Counter::ShadowBuffers, false},
				    {"sh_buf_none", FS::Counter::ShadowBufNone, false},
				    {"sh_buf_fast", FS::Counter::ShadowBufFast, false},
				    {"sh_buf_epoch", FS::Counter::ShadowBufEpoch, false},
				    {"sh_buf_stream", FS::Counter::ShadowBufStream, false},
				    {"sh_buf_slow", FS::Counter::ShadowBufSlow, false},
				    {"sh_buf_new", FS::Counter::ShadowBufNew, false},
				    {"sh_us", FS::Counter::ShadowWorkerNs, true},
				    {"sh_inline_us", FS::Counter::ShadowInlineNs, true},
				    {"sh_push_us", FS::Counter::ShadowPushNs, true},
				    {"sh_lock_us", FS::Counter::ShadowLockNs, true},
				    {"sh_trk_us", FS::Counter::ShadowTrackerNs, true},
				    {"sh_wake", FS::Counter::ShadowWakes, false},
				    // Session 67 watchdog (see the FrameTrace main line for the maxima).
				    {"rt_att", FS::Counter::RtAttachments, false},
				    {"rt_kpx", FS::Counter::RtPixelsK, false},
				    {"vp_kpx", FS::Counter::VpPixelsK, false},
				    // Session 68: occlusion ceiling, the serial floor A, and the relay.
				    {"occ_dump", FS::Counter::OcclusionDumps, false},
				    {"a_mut_us", FS::Counter::MutateNs, true},
				    {"a_mut_n", FS::Counter::MutateIntervals, false},
				    {"a_hold_us", FS::Counter::LockHoldNs, true},
				    {"a_hold_n", FS::Counter::LockHolds, false},
				    {"a_wait_us", FS::Counter::LockWaitNs, true},
				    {"bat_ranges", FS::Counter::BatonRanges, false},
				    {"bat_work_us", FS::Counter::BatonWorkNs, true},
				    {"bat_work_draws", FS::Counter::BatonWorkDraws, false},
				    {"bat_self_us", FS::Counter::BatonSelfNs, true},
				    {"bat_self_draws", FS::Counter::BatonSelfDraws, false},
				    {"bat_self_ranges", FS::Counter::BatonSelfRanges, false},
				    {"bat_park_us", FS::Counter::BatonParkNs, true},
				    {"bat_wake_us", FS::Counter::BatonWakeNs, true},
				    {"bat_drop", FS::Counter::BatonDropped, false},
				    {"px_on_n", FS::Counter::PxOnDraws, false},
				    {"bk_hit", FS::Counter::BindKeyHit, false},
				    {"bk_miss", FS::Counter::BindKeyMiss, false},
				    {"bk_draw_hit", FS::Counter::BindKeyDrawHit, false},
				    {"bk_draw_miss", FS::Counter::BindKeyDrawMiss, false},
				    {"bk_hit_us", FS::Counter::BindKeyHitNs, true},
				    {"bk_miss_us", FS::Counter::BindKeyMissNs, true},
				    {"px_on_bind_us", FS::Counter::PxOnBindNs, true},
				    {"px_off_n", FS::Counter::PxOffDraws, false},
				    {"px_off_bind_us", FS::Counter::PxOffBindNs, true},
				    // Session 69, gate "mutsite": the phases of the render-mutex hold.
				    {"mh_n", FS::Counter::HoldEntries, false},
				    {"mh_draws", FS::Counter::HoldDraws, false},
				    {"mh_pro_us", FS::Counter::HoldPrologueNs, true},
				    {"mh_rt_us", FS::Counter::HoldTargetsNs, true},
				    {"mh_prog_us", FS::Counter::HoldProgramsNs, true},
				    {"mh_bind_us", FS::Counter::HoldBindingsNs, true},
				    {"mh_emit_us", FS::Counter::HoldEmitNs, true},
				    {"mh_tail_us", FS::Counter::HoldTailNs, true},
				    {"mh_disp_n", FS::Counter::HoldDispatches, false},
				    {"mh_disp_us", FS::Counter::HoldDispatchNs, true},
				    {"mh_pres_n", FS::Counter::HoldPresents, false},
				    {"mh_pres_us", FS::Counter::HoldPresentNs, true},
				    {"mh_pres_wait_us", FS::Counter::HoldPresentWaitNs, true},
				    // Session 69, gate "imgskip": img_skip + img_up == the baseline img_up.
				    {"img_skip", FS::Counter::ImgSkipped, false},
				    // KiB already, so micros = false: the "micros" path divides by 1000 and would put
				    // this on a different scale from img_up_kb, which is bytes / 1024.
				    {"img_skip_kb", FS::Counter::ImgSkippedKb, false},
				    // Session 70: the four outcomes of ClearImageFromBuffer. KiB counters are KiB
				    // already, so micros = false for them too.
				    {"clr_ok", FS::Counter::ClearConsumed, false},
				    {"clr_ok_kb", FS::Counter::ClearConsumedKb, false},
				    {"clr_ambig", FS::Counter::ClearAmbiguous, false},
				    {"clr_ambig_kb", FS::Counter::ClearAmbiguousKb, false},
				    {"clr_none", FS::Counter::ClearNoMatch, false},
				    {"clr_none_kb", FS::Counter::ClearNoMatchKb, false},
				    {"clr_decode", FS::Counter::ClearDecodeFail, false},
				    {"clr_over", FS::Counter::ClearOverlapOnly, false},
				    // Session 71. Every row below is micros = false: rpa_kpx / rpa_dkpx /
				    // rpa_re_kpx are units of 1024 pixels and the c3_*_kb rows are KiB, both
				    // accumulated at the increment site. The micros column divides by 1000 and
				    // would put them on a different scale from rt_kpx and img_up_kb - that was
				    // the session-69 img_skip_kb defect.
				    // G-area: the per-pass census (context.cpp, renderDraw.cpp).
				    {"rpa_slot", FS::Counter::PassSlots, false},
				    {"rpa_att", FS::Counter::PassAttachments, false},
				    {"rpa_kpx", FS::Counter::PassPixelsK, false},
				    {"rpa_dep", FS::Counter::PassDepth, false},
				    {"rpa_dkpx", FS::Counter::PassDepthPixelsK, false},
				    {"rpa_lay", FS::Counter::PassLayered, false},
				    {"rpa_re_kpx", FS::Counter::PassRestartPixelsK, false},
				    {"rpa_a0", FS::Counter::PassShape0, false},
				    {"rpa_a1", FS::Counter::PassShape1, false},
				    {"rpa_a2", FS::Counter::PassShape2, false},
				    {"rpa_a3", FS::Counter::PassShape3, false},
				    {"rpa_a4", FS::Counter::PassShape4, false},
				    {"rpa_a5", FS::Counter::PassShape5, false},
				    {"rpa_a6", FS::Counter::PassShape6, false},
				    {"rpa_a7", FS::Counter::PassShape7, false},
				    {"rpa_a8", FS::Counter::PassShape8, false},
				    {"rpa_e0", FS::Counter::PassExtent0, false},
				    {"rpa_e1", FS::Counter::PassExtent1, false},
				    {"rpa_e2", FS::Counter::PassExtent2, false},
				    {"rpa_e3", FS::Counter::PassExtent3, false},
				    {"rpa_e4", FS::Counter::PassExtent4, false},
				    {"rpa_e5", FS::Counter::PassExtent5, false},
				    {"rpa_e6", FS::Counter::PassExtent6, false},
				    {"rpa_e7", FS::Counter::PassExtent7, false},
				    {"rpd_a0", FS::Counter::PassDraw0, false},
				    {"rpd_a1", FS::Counter::PassDraw1, false},
				    {"rpd_a2", FS::Counter::PassDraw2, false},
				    {"rpd_a3", FS::Counter::PassDraw3, false},
				    {"rpd_a4", FS::Counter::PassDraw4, false},
				    {"rpd_a5", FS::Counter::PassDraw5, false},
				    {"rpd_a6", FS::Counter::PassDraw6, false},
				    {"rpd_a7", FS::Counter::PassDraw7, false},
				    {"rpd_a8", FS::Counter::PassDraw8, false},
				    // G-wit: the M1 witness population (pipelineCache.cpp).
				    {"da_runs_clean", FS::Counter::DrawAheadCleanRuns, false},
				    {"da_singles", FS::Counter::DrawAheadSingles, false},
				    {"da_probe_q", FS::Counter::DrawAheadQueueProbes, false},
				    // Session 72: the knob "dawitloop" ceiling (measurement only, never shipped).
				    {"da_loop_skip", FS::Counter::DrawAheadLoopSkip, false},
				    // Session 72, C1: the achievable half of the 836.5 us copy phase
				    // (textureCache.cpp). c1_si_dt is the cell a fused detile would remove.
				    {"c1_si_dt", FS::Counter::C1StorageDetile, false},
				    {"c1_si_dt_kb", FS::Counter::C1StorageDetileKb, false},
				    {"c1_si_dt_cp_kb", FS::Counter::C1StorageDetileCopyKb, false},
				    {"c1_si_nd", FS::Counter::C1StorageDirect, false},
				    {"c1_si_nd_kb", FS::Counter::C1StorageDirectKb, false},
				    {"c1_si_nd_cp_kb", FS::Counter::C1StorageDirectCopyKb, false},
				    {"c1_ns_dt", FS::Counter::C1NoStorageDetile, false},
				    {"c1_ns_dt_kb", FS::Counter::C1NoStorageDetileKb, false},
				    {"c1_ns_dt_cp_kb", FS::Counter::C1NoStorageDetileCopyKb, false},
				    {"c1_ns_nd", FS::Counter::C1NoStorageDirect, false},
				    {"c1_ns_nd_kb", FS::Counter::C1NoStorageDirectKb, false},
				    {"c1_ns_nd_cp_kb", FS::Counter::C1NoStorageDirectCopyKb, false},
				    // Session 72: the passes the census cannot see, and the area it understates.
				    {"rpa_alias", FS::Counter::PassAliasClear, false},
				    {"rpa_alias_kpx", FS::Counter::PassAliasClearKpx, false},
				    {"rpa_blit", FS::Counter::PassBlitMsDepth, false},
				    {"rpa_ovl", FS::Counter::PassOverlay, false},
				    {"rpa_tkpx", FS::Counter::PassTrueColorPixelsK, false},
				    {"rpa_mix", FS::Counter::PassMixedExtents, false},
				    {"da_cl_fb", FS::Counter::DrawAheadCleanFallback, false},
				    {"da_cl_fb_w", FS::Counter::DrawAheadCleanFallbackWords, false},
				    {"da_cl_look", FS::Counter::DrawAheadCleanLookup, false},
				    {"da_cl_miss", FS::Counter::DrawAheadCleanMiss, false},
				    {"da_cl_fail", FS::Counter::DrawAheadCleanFail, false},
				    {"da_cl_live", FS::Counter::DrawAheadCleanLive, false},
				    {"tgm_call", FS::Counter::TexGpuModifiedCalls, false},
				    {"tgm_hint", FS::Counter::TexGpuModifiedHint, false},
				    {"dg_img", FS::Counter::GpuDirtyGenImage, false},
				    {"dg_img_cl", FS::Counter::GpuDirtyGenImageClr, false},
				    {"dg_buf", FS::Counter::GpuDirtyGenBuffer, false},
				    {"dg_buf_all", FS::Counter::GpuDirtyGenBufferAll, false},
				    {"da_cl_pmiss", FS::Counter::DrawAheadCleanProbeMiss, false},
				    {"da_cl_pdrop", FS::Counter::DrawAheadCleanProbeDrop, false},
				    {"da_cl_drop", FS::Counter::DrawAheadCleanDrop, false},
				    {"da_cl_bad", FS::Counter::DrawAheadCleanBad, false},
				    {"rng_total", FS::Counter::BatonRangesTotal, false},
				    {"rng_inpass", FS::Counter::BatonRangesInPass, false},
				    {"cram_write", FS::Counter::ConstRamWrites, false},
				    {"c1_fz_ok", FS::Counter::C1FuseReady, false},
				    {"c1_fz_ok_kb", FS::Counter::C1FuseReadyKb, false},
				    {"c1_fz_ok_cp_kb", FS::Counter::C1FuseReadyCopyKb, false},
				    {"c1_fz_swap", FS::Counter::C1FuseSwap, false},
				    {"c1_fz_shape", FS::Counter::C1FuseShape, false},
				    {"c1_fz_fmt", FS::Counter::C1FuseFormat, false},
				    {"c1_fuse", FS::Counter::C1Fused, false},
				    {"c1_fuse_kb", FS::Counter::C1FusedKb, false},
				    {"pf_l1", FS::Counter::PrefetchHintL1Takes, false},
				    {"da_pf_b", FS::Counter::DrawAheadPrefetchBytes, false},
				    {"da_pf_cap_b", FS::Counter::DrawAheadPrefetchCapBytes, false},
				    {"slc_total", FS::Counter::SliceTotal, false},
				    {"slc_inpass", FS::Counter::SliceInPass, false},
				    {"slc_resume", FS::Counter::SliceResume, false},
				    {"slc_cp_same", FS::Counter::SliceSameProcessor, false},
				    {"slc_newcb", FS::Counter::SliceNewBuffer, false},
				    {"slc_d0", FS::Counter::SliceDraws0, false},
				    {"slc_d1", FS::Counter::SliceDraws1, false},
				    {"slc_d2", FS::Counter::SliceDraws2, false},
				    {"slc_d3", FS::Counter::SliceDraws3, false},
				    {"slc_d4", FS::Counter::SliceDraws4, false},
				    // The gate "swlocal" predicate census (renderDraw.cpp).
				    {"swloc_ok", FS::Counter::ShaderWriteLocalEligible, false},
				    {"swloc_mesh", FS::Counter::ShaderWriteLocalMeshBlocked, false},
				    {"swloc_vtx", FS::Counter::ShaderWriteLocalStageBlocked, false},
				    {"swloc_shut", FS::Counter::ShaderWriteLocalClosed, false},
				    // ... and where its closer would migrate to (context.cpp).
				    {"swmig_state", FS::Counter::SwMigState, false},
				    {"swmig_tt", FS::Counter::SwMigTargetTransit, false},
				    {"swmig_bt", FS::Counter::SwMigBindingTransit, false},
				    {"swmig_gds", FS::Counter::SwMigGds, false},
				    {"swmig_sw", FS::Counter::SwMigShaderWrite, false},
				    {"swmig_disp", FS::Counter::SwMigDispatch, false},
				    {"swmig_bup", FS::Counter::SwMigBufferUpload, false},
				    {"swmig_bcp", FS::Counter::SwMigBufferCopy, false},
				    {"swmig_iup", FS::Counter::SwMigImageUpload, false},
				    {"swmig_tiler", FS::Counter::SwMigTiler, false},
				    {"swmig_clr", FS::Counter::SwMigClear, false},
				    {"swmig_san", FS::Counter::SwMigSanitize, false},
				    {"swmig_dl", FS::Counter::SwMigDownload, false},
				    {"swmig_sub", FS::Counter::SwMigSubmit, false},
				    {"swmig_oth", FS::Counter::SwMigOther, false},
				    // G-img3 / C3: guest clear registers and upload attribution (textureCache.cpp).
				    {"c3_ct", FS::Counter::C3ColorAcquires, false},
				    {"c3_ct_fc", FS::Counter::C3ColorRegFastClear, false},
				    {"c3_ct_dcc", FS::Counter::C3ColorRegDcc, false},
				    {"c3_ct_key", FS::Counter::C3ColorRegDccKey, false},
				    {"c3_ct_kind", FS::Counter::C3ColorMetaKind, false},
				    {"c3_ct_drop", FS::Counter::C3ColorRegDropped, false},
				    {"c3_ct_fill", FS::Counter::C3ColorFillPending, false},
				    {"c3_ct_pop", FS::Counter::C3ColorPop, false},
				    {"c3_ct_pop_kb", FS::Counter::C3ColorPopKb, false},
				    {"c3_ct_canc", FS::Counter::C3ColorCancelled, false},
				    {"c3_ct_canc_kb", FS::Counter::C3ColorCancelledKb, false},
				    {"c3_dt", FS::Counter::C3DepthAcquires, false},
				    {"c3_pop", FS::Counter::C3Population, false},
				    {"c3_pop_kb", FS::Counter::C3PopulationKb, false},
				    {"c3_ct_up", FS::Counter::C3ColorUploads, false},
				    {"c3_ct_up_kb", FS::Counter::C3ColorUploadsKb, false},
				    {"c3_ct_up_reg", FS::Counter::C3ColorUploadsReg, false},
				    {"c3_ct_up_reg_kb", FS::Counter::C3ColorUploadsRegKb, false},
				    {"c3_ct_up_fill", FS::Counter::C3ColorUploadsFill, false},
				    {"c3_ct_up_fill_kb", FS::Counter::C3ColorUploadsFillKb, false},
				    {"c3_dt_up", FS::Counter::C3DepthUploads, false},
				    {"c3_dt_up_kb", FS::Counter::C3DepthUploadsKb, false},
				    {"c3_dt_up_reg", FS::Counter::C3DepthUploadsReg, false},
				    {"c3_dt_up_reg_kb", FS::Counter::C3DepthUploadsRegKb, false},
				    {"c3_st_up", FS::Counter::C3StorageUploads, false},
				    {"c3_st_up_kb", FS::Counter::C3StorageUploadsKb, false},
				    {"c3_smp_up", FS::Counter::C3SampledUploads, false},
				    {"c3_smp_up_kb", FS::Counter::C3SampledUploadsKb, false},
				    {"c3_clr_up", FS::Counter::C3ClearUploads, false},
				    {"c3_clr_up_kb", FS::Counter::C3ClearUploadsKb, false},
				    {"c3_oth_up", FS::Counter::C3OtherUploads, false},
				    {"c3_oth_up_kb", FS::Counter::C3OtherUploadsKb, false},
				    // Session 85, gate "bindlap": the per-slot price of the binding phase.
				    {"bl_stage_n", FS::Counter::BindLapStages, false},
				    {"bl_prep_us", FS::Counter::BindLapPrepareNs, true},
				    {"bl_prep_n", FS::Counter::BindLapPrepares, false},
				    {"bl_img_us", FS::Counter::BindLapImageNs, true},
				    {"bl_img_n", FS::Counter::BindLapImages, false},
				    {"bl_buf_us", FS::Counter::BindLapBufferNs, true},
				    {"bl_buf_n", FS::Counter::BindLapBuffers, false},
				    {"bl_tr_us", FS::Counter::BindLapTransitNs, true},
				    {"bl_wr_us", FS::Counter::BindLapWriteNs, true},
				    {"bl_em_us", FS::Counter::BindLapEmitNs, true},
				    {"bl_cmt_n", FS::Counter::BindLapCommits, false},
				    // Session 86, D3: bl_prep_us split by resource kind.
				    {"bl_res_us", FS::Counter::BindLapResolveNs, true},
				    {"bl_res_n", FS::Counter::BindLapResolves, false},
				    {"bl_smp_us", FS::Counter::BindLapSamplerNs, true},
				    {"bl_smp_n", FS::Counter::BindLapSamplers, false},
				    {"bl_sd_us", FS::Counter::BindLapDataNs, true},
				    // Session 85, gate "bdasplit": the division of the scan half of PrepareBda.
				    {"bda_bound_us", FS::Counter::BdaSplitBoundNs, true},
				    {"bda_bound_n", FS::Counter::BdaSplitBounds, false},
				    {"bda_walk_us", FS::Counter::BdaSplitWalkNs, true},
				    {"bda_walk_n", FS::Counter::BdaSplitWalks, false},
				    {"bda_collect_us", FS::Counter::BdaSplitCollectNs, true},
				    {"bda_up_us", FS::Counter::BdaSplitUploadNs, true},
				    {"bda_up_n", FS::Counter::BdaSplitUploads, false},
				    {"bda_first_us", FS::Counter::BdaSplitFirstNs, true},
				    {"bda_first_n", FS::Counter::BdaSplitFirsts, false},
				    {"bda_late_us", FS::Counter::BdaSplitLateNs, true},
				    {"bda_late_n", FS::Counter::BdaSplitLates, false},
				    // Session 85, gate "slotstat": the three biases of the census, measured.
				    {"sl_shader_chg", FS::Counter::SlotShaderChanges, false},
				    {"sl_img_same_sh", FS::Counter::SlotImagesSameShader, false},
				    {"sl_smp_same_sh", FS::Counter::SlotSamplersSameShader, false},
				    {"sl_buf_same_sh", FS::Counter::SlotBuffersSameShader, false},
				    {"sl_stage_all_sh", FS::Counter::SlotStagesAllShader, false},
				    {"sl_buf_null", FS::Counter::SlotBuffersNull, false},
				    {"sl_img_null", FS::Counter::SlotImagesNull, false},
				    // Session 86: route C's last idea, the per-stage duplicate census.
				    {"sl_img_dup", FS::Counter::SlotImageDups, false},
				    {"sl_img_dupv", FS::Counter::SlotImageDupViews, false},
				    {"sl_img_dstage", FS::Counter::SlotImageDupStages, false},
				    {"sl_img_sq", FS::Counter::SlotImageSq, false},
				    {"sl_img_elem", FS::Counter::SlotImageElements, false},
				    {"sl_smp_elem", FS::Counter::SlotSamplerElements, false},
				    {"sl_bad", FS::Counter::SlotBad, false},
				    // Session 85, gate "bindpack2" (PLAN_82_bind.md item 6a) and its self-check.
				    {"be_fast", FS::Counter::BufEpochFastHits, false},
				    {"be_race", FS::Counter::BufEpochFastRaces, false},
				    {"bp2_bad", FS::Counter::BufEpochFastBad, false},
				    // Session 86, gate "proglap": what mh_prog_us is, under lite.
				    {"pg_pre_us", FS::Counter::ProgLapPreNs, true},
				    {"pg_n", FS::Counter::ProgLapCalls, false},
				    {"pg_key_us", FS::Counter::ProgLapKeyNs, true},
				    {"pg_key_n", FS::Counter::ProgLapKeys, false},
				    {"pg_key_hit_us", FS::Counter::ProgLapKeyHitNs, true},
				    {"pg_key_hit_n", FS::Counter::ProgLapKeyHits, false},
				    {"pg_get_us", FS::Counter::ProgLapGetNs, true},
				    {"pg_get_n", FS::Counter::ProgLapGets, false},
				    {"pg_cold_n", FS::Counter::ProgLapCold, false},
				    {"pg_compile_n", FS::Counter::ProgLapCompiles, false},
				    {"pg_perm", FS::Counter::ProgLapPerms, false},
				    // Session 86, gate "drawmerge": route D4, consecutive-draw mergeability.
				    {"dm_n", FS::Counter::DrawMergeDraws, false},
				    {"dm_pipe", FS::Counter::DrawMergePipe, false},
				    {"dm_same", FS::Counter::DrawMergeSame, false},
				    {"dm_push", FS::Counter::DrawMergePush, false},
				    {"dm_buf1", FS::Counter::DrawMergeBuf1, false},
				    {"dm_no", FS::Counter::DrawMergeNo, false},
				    {"dm_same_nr", FS::Counter::DrawMergeSameNr, false},
				    {"dm_push_nr", FS::Counter::DrawMergePushNr, false},
				    {"dm_buf1_nr", FS::Counter::DrawMergeBuf1Nr, false},
				    {"dm_ring", FS::Counter::DrawMergeRing, false},
				    {"dm_bufn", FS::Counter::DrawMergeBufSlots, false},
				    {"dm_img_d", FS::Counter::DrawMergeImageDiffs, false},
				    {"dm_smp_d", FS::Counter::DrawMergeSamplerDiffs, false},
				    {"dm_buf_d", FS::Counter::DrawMergeBufferDiffs, false},
				    {"dm_mesh", FS::Counter::DrawMergeMesh, false},
				    {"dm_over", FS::Counter::DrawMergeOver, false},
				    {"dm_bad", FS::Counter::DrawMergeBad, false},
				    // Session 87, gate "bindalt": the sampled halves of the image loop.
				    {"bl_rsv_us", FS::Counter::BindAltResolveNs, true},
				    {"bl_rsv_n", FS::Counter::BindAltResolves, false},
				    {"bl_rsv0_us", FS::Counter::BindAltResolve0Ns, true},
				    {"bl_rsv0_n", FS::Counter::BindAltResolve0s, false},
				    // Session 87, gate "proglap" extended: the five phases of the block session 86
				    // measured as a residual.
				    {"pg_loc_us", FS::Counter::ProgLapLocalNs, true},
				    {"pg_ahead_us", FS::Counter::ProgLapAheadNs, true},
				    {"pg_ahead_n", FS::Counter::ProgLapAheads, false},
				    {"pg_memo_us", FS::Counter::ProgLapMemoNs, true},
				    {"pg_memo_n", FS::Counter::ProgLapMemos, false},
				    {"pg_mat_us", FS::Counter::ProgLapMatNs, true},
				    {"pg_mat_n", FS::Counter::ProgLapMats, false},
				    {"pg_pm_us", FS::Counter::ProgLapPermPhaseNs, true},
				    {"pg_pm_n", FS::Counter::ProgLapPermPhases, false},
				    // Session 88, knob "bindwit": the witness share of a memo-hit resolve.
				    {"bl_wit_us", FS::Counter::BindWitNs, true},
				    {"bl_wit_n", FS::Counter::BindWits, false},
				    {"bl_wnh_us", FS::Counter::BindWitMissNs, true},
				    {"bl_wnh_n", FS::Counter::BindWitMisses, false},
				    {"bl_wit0_us", FS::Counter::BindWit0Ns, true},
				    {"bl_wit0_n", FS::Counter::BindWit0s, false},
				    // Session 89, gate "takelap": the six phases of AheadTake and their two
				    // populations.  The tail is derived by the readout, not printed.
				    {"da_t_key_us", FS::Counter::TakeLapKeyNs, true},
				    {"da_t_prb_us", FS::Counter::TakeLapProbeNs, true},
				    {"da_t_pfa_us", FS::Counter::TakeLapPrefetchNs, true},
				    {"da_t_pfb_us", FS::Counter::TakeLapPrefetchRunNs, true},
				    {"da_t_ver_us", FS::Counter::TakeLapVerifyNs, true},
				    {"da_t_cpy_us", FS::Counter::TakeLapTakeNs, true},
				    {"da_t_n", FS::Counter::TakeLapCalls, false},
				    {"da_t_hit_n", FS::Counter::TakeLapReady, false},
				    // Session 89, section 3.3: the search half of the permutation phase.  From this
				    // binary on, pg_pm_us is the TAKE alone; the old quantity is pg_pmf_us + pg_pm_us.
				    {"pg_pmf_us", FS::Counter::ProgLapPermFindNs, true},
				    // Session 90, knob "bufimp": the guest-memory import for buffer uploads.  Every
				    // one of these reads EXACTLY 0 while the knob is 0, and that is the arming proof.
				    {"bi_try", FS::Counter::BufImportTries, false},
				    {"bi_ok", FS::Counter::BufImportTakes, false},
				    {"bi_b", FS::Counter::BufImportBytes, false},
				    {"bi_reg", FS::Counter::BufImportRegions, false},
				    {"bi_split", FS::Counter::BufImportSplits, false},
				    {"bi_noback", FS::Counter::BufImportNoBacking, false},
				    {"bi_nochunk", FS::Counter::BufImportNoChunk, false},
				    {"bi_bad", FS::Counter::BufImportBad, false},
				    {"bi_us", FS::Counter::BufImportResolveNs, true},
				    // Session 90, section 3.2: the two halves of the find_if predicate.
				    {"pg_pmp_us", FS::Counter::ProgLapPmPushNs, true},
				    {"pg_pms_us", FS::Counter::ProgLapPmSpecNs, true},
				    {"pg_pmp_no", FS::Counter::ProgLapPmPushNo, false},
				    // Session 90: the arming proof of bufimp = 2.  0 in the census arm, == bi_ok in the
				    // import arm.
				    {"bi_cp", FS::Counter::BufImportCopies, false},
				    // Session 91: the guest GPU clock pin.  gclk_pin is EXACTLY 0 without KYTY_GPU_CLOCK_PIN.
				    {"gclk_n", FS::Counter::GpuClockReads, false},
				    {"gclk_pin", FS::Counter::GpuClockPinnedReads, false},
				    {"gclk_adv", FS::Counter::GpuClockAdvance, false},
				    {"gclk_sadv", FS::Counter::GpuClockScaledAdvance, false},
				    {"gclk_back", FS::Counter::GpuClockBackward, false},
				    // Session 91: the upload memcpy split.  *_b are RAW BYTES (micros = false), not kB.
				    {"stg_pool_n", FS::Counter::StagingPoolCopies, false},
				    {"stg_pool_b", FS::Counter::StagingPoolBytes, false},
				    {"stg_pool_ns", FS::Counter::StagingPoolNs, false},
				    {"stg_in_n", FS::Counter::StagingInlineCopies, false},
				    {"stg_inbig_n", FS::Counter::StagingInlineBigCopies, false},
				    {"stg_in_b", FS::Counter::StagingInlineBytes, false},
				    {"stg_in_gpu_b", FS::Counter::StagingInlineGpuBytes, false},
				    {"stg_in_ns", FS::Counter::StagingInlineNs, false},
				    {"up_tmp_n", FS::Counter::UploadTempCopies, false},
				    {"up_tmp_b", FS::Counter::UploadTempBytes, false},
				    {"stg_img_pool_b", FS::Counter::StagingImgPoolBytes, false},
				    {"stg_img_in_b", FS::Counter::StagingImgInlineBytes, false},
				    {"bi_reg_small", FS::Counter::BufImportSmallRegions, false},
				    {"bi_b_small", FS::Counter::BufImportSmallBytes, false},
				    // Session 91: host-read waits, lite-live (hostread_wait_us is not: TimingsEnabled).
				    {"hr_free", FS::Counter::HostReadFree, false},
				    {"hr_gpuw", FS::Counter::HostReadGpuWaits, false},
				    {"hr_gpuw_us", FS::Counter::HostReadGpuWaitNs, true},
				    {"hr_forced", FS::Counter::HostReadForced, false},
				    {"hr_forced_us", FS::Counter::HostReadForcedNs, true},
				    {"hr_sync", FS::Counter::HostReadSync, false},
				    {"hr_sync_us", FS::Counter::HostReadSyncNs, true},
				    {"hr_call_us", FS::Counter::HostReadCallNs, true},
				    // Session 92, gate "stglap": the split of stg_pool_ns.  Times are RAW ns (micros =
				    // false), like stg_pool_ns itself.  All six read 0 unless the gate is armed.
				    {"stg_res_ns", FS::Counter::StagingResolveNs, false},
				    {"stg_lock_ns", FS::Counter::StagingLockNs, false},
				    {"stg_wake_ns", FS::Counter::StagingWakeNs, false},
				    {"stg_q", FS::Counter::StagingQueueDepth, false},
				    {"stg_up_n", FS::Counter::StagingUploadCalls, false},
				    {"stg_chunks", FS::Counter::StagingChunks, false},
				    // Session 92b, gate "stglap": stg_wake_ns split by the branch that took it, and
				    // the price of knob "copywake" = 2.  RAW ns (micros = false), like stg_wake_ns.
				    // stg_wake1_ns + stg_waken_ns == stg_wake_ns by construction.
				    {"stg_wake1_ns", FS::Counter::StagingWakeOneNs, false},
				    {"stg_wake1_n", FS::Counter::StagingWakeOneCalls, false},
				    {"stg_waken_ns", FS::Counter::StagingWakeManyNs, false},
				    {"stg_waken_n", FS::Counter::StagingWakeManyCalls, false},
				    {"stg_spin_ns", FS::Counter::StagingSpinNs, false},
				    {"stg_spin_hit", FS::Counter::StagingSpinHits, false},
				    // Session 93, gate "bdacap": the BDA ceiling census of buffer descriptor
				    // slots.  bc_null + bc_fmt + bc_cb + bc_ring + bc_ok == bb_n (control A2).
				    // Bytes are RAW BYTES and times are RAW ns (micros = false), like stg_*.
				    // All ten read 0 unless the gate is armed.
				    {"bc_null", FS::Counter::BdaCapNull, false},
				    {"bc_fmt", FS::Counter::BdaCapFormatted, false},
				    {"bc_cb", FS::Counter::BdaCapConstBank, false},
				    {"bc_ring", FS::Counter::BdaCapRing, false},
				    {"bc_ok", FS::Counter::BdaCapOk, false},
				    {"bc_ok_b", FS::Counter::BdaCapOkBytes, false},
				    {"bc_ok_ns", FS::Counter::BdaCapOkNs, false},
				    {"bc_all_ns", FS::Counter::BdaCapAllNs, false},
				    {"bc_dma", FS::Counter::BdaCapDmaDraws, false},
				    {"dm_buf1_ok", FS::Counter::DrawMergeBuf1Ok, false},
				    // Session 94: bc_cb_ns (gate bdacap), mc_* (gate mergecost), bda_all_n (gate
				    // bdaall).  Times are RAW ns (micros = false).  All read 0 unless armed.
				    {"bc_cb_ns", FS::Counter::BdaCapConstBankNs, false},
				    {"mc_n", FS::Counter::MergeCostDraws, false},
				    {"mc_pre_ns", FS::Counter::MergeCostPreNs, false},
				    {"mc_post_ns", FS::Counter::MergeCostPostNs, false},
				    {"mc_dm_ns", FS::Counter::MergeCostCensusNs, false},
				    {"mc_sig_ns", FS::Counter::MergeCostSigNs, false},
				    {"mc_sig", FS::Counter::MergeCostSigDraws, false},
				    {"mc_bad", FS::Counter::MergeCostBad, false},
				    {"mc_okslot", FS::Counter::MergeCostOkSlots, false},
				    {"mc_p", FS::Counter::MergeCostSame, false},
				    {"mc_p_pipe", FS::Counter::MergeCostSamePipe, false},
				    {"mc_p_eq", FS::Counter::MergeCostSameEqPipe, false},
				    {"mc_ok", FS::Counter::MergeCostOkDraws, false},
				    {"mc_p_ok", FS::Counter::MergeCostSameOk, false},
				    {"mc_pre_p_ns", FS::Counter::MergeCostPrePNs, false},
				    {"mc_post_p_ns", FS::Counter::MergeCostPostPNs, false},
				    {"mc_pre_ok_ns", FS::Counter::MergeCostPreOkNs, false},
				    {"mc_post_ok_ns", FS::Counter::MergeCostPostOkNs, false},
				    {"mc_tr_ns", FS::Counter::MergeCostTransitNs, false},
				    {"mc_wr_ns", FS::Counter::MergeCostWriteNs, false},
				    {"mc_em_ns", FS::Counter::MergeCostEmitNs, false},
				    {"mc_tr_p_ns", FS::Counter::MergeCostTransitPNs, false},
				    {"mc_wr_p_ns", FS::Counter::MergeCostWritePNs, false},
				    {"mc_em_p_ns", FS::Counter::MergeCostEmitPNs, false},
				    {"mc_d_first", FS::Counter::MergeCostDiffFirst, false},
				    {"mc_d_shape", FS::Counter::MergeCostDiffShape, false},
				    {"mc_d_img", FS::Counter::MergeCostDiffImage, false},
				    {"mc_d_smp", FS::Counter::MergeCostDiffSampler, false},
				    {"mc_d_ring", FS::Counter::MergeCostDiffRing, false},
				    {"mc_d_buf", FS::Counter::MergeCostDiffBuffer, false},
				    {"mc_d_srt", FS::Counter::MergeCostDiffSrt, false},
				    {"mc_d_fix", FS::Counter::MergeCostDiffFixed, false},
				    {"mc_d_rs", FS::Counter::MergeCostDiffRingSrtOnly, false},
				    {"bda_all_n", FS::Counter::BdaAllCalls, false},
				    {"mc_d_cb", FS::Counter::MergeCostDiffCb, false},
				    {"mc_has_ring", FS::Counter::MergeCostHasRing, false},
				    {"mc_has_srt", FS::Counter::MergeCostHasSrt, false},
				    {"mc_p_push", FS::Counter::MergeCostSamePush, false},
				    {"mc_post_pok_ns", FS::Counter::MergeCostPostPOkNs, false},
				    {"mc_mask_ok", FS::Counter::MergeCostMaskOk, false},
				    {"mc_mask_x", FS::Counter::MergeCostMaskOther, false},
				    {"mc_wslot", FS::Counter::MergeCostWrittenSlots, false},
				    {"mc_pkt", FS::Counter::MergeCostPacket, false},
				    {"bc_ok_w", FS::Counter::BdaCapOkWritten, false},
				    {"bc_ok_w_ns", FS::Counter::BdaCapOkWrittenNs, false},
				    {"bda_all_disp", FS::Counter::BdaAllDispatch, false},
				    {"bda_all_skip", FS::Counter::BdaAllNoCandidate, false},
				    {"fbp_n", FS::Counter::FaultProcN, false},
				    {"fbp_ns", FS::Counter::FaultProcNs, false},
				    {"fr_n", FS::Counter::FrameRepDraws, false},
				    {"fr_id1", FS::Counter::FrameRepId1, false},
				    {"fr_id2", FS::Counter::FrameRepId2, false},
				    {"fr_id3", FS::Counter::FrameRepId3, false},
				    {"fr_pay1", FS::Counter::FrameRepPay1, false},
				    {"fr_full1", FS::Counter::FrameRepFull1, false},
				    {"fr_full2", FS::Counter::FrameRepFull2, false},
				    {"fr_full3", FS::Counter::FrameRepFull3, false},
				    {"fr_id_ns", FS::Counter::FrameRepIdNs, false},
				    {"fr_pay_ns", FS::Counter::FrameRepPayNs, false},
				    {"fr_full_ns", FS::Counter::FrameRepFullNs, false},
				    {"fr_all_ns", FS::Counter::FrameRepAllNs, false},
				    {"fr_ring", FS::Counter::FrameRepRing, false},
				    {"fr_sig_ns", FS::Counter::FrameRepSigNs, false},
				    {"fr_pre_ns", FS::Counter::FrameRepPreNs, false},
				    {"fr_pay_b", FS::Counter::FrameRepPayBytes, false},
				    {"fr_pay_n", FS::Counter::FrameRepPayN, false},
				    {"fr_bad", FS::Counter::FrameRepBad, false},
				    {"fr_over", FS::Counter::FrameRepOverflow, false},
				    {"fr_id1r", FS::Counter::FrameRepIdR1, false},
				    {"fr_id2r", FS::Counter::FrameRepIdR2, false},
				    {"fr_id3r", FS::Counter::FrameRepIdR3, false},
				    {"fr_idr_ns", FS::Counter::FrameRepIdRNs, false},
				    {"fr_id1m", FS::Counter::FrameRepIdM1, false},
				    {"fr_idm_ns", FS::Counter::FrameRepIdMNs, false},
				    {"fr_okring", FS::Counter::FrameRepOkRing, false},
				    {"fr_okslot", FS::Counter::FrameRepOkSlots, false},
				    {"fr_img", FS::Counter::FrameRepImgN, false},
				    {"fr_buf", FS::Counter::FrameRepBufN, false},
				    {"pl_proc_ns", FS::Counter::PathProcNs, false},
				    {"pl_proc_n", FS::Counter::PathProcN, false},
				    {"pl_look_ns", FS::Counter::PathLookNs, false},
				    {"pl_look_n", FS::Counter::PathLookN, false},
				    {"pl_pref_ns", FS::Counter::PathPrefNs, false},
				    {"pl_pref_n", FS::Counter::PathPrefN, false},
				    {"pl_eop_ns", FS::Counter::PathEopNs, false},
				    {"pl_eop_n", FS::Counter::PathEopN, false},
				    {"pl_bar_ns", FS::Counter::PathBarNs, false},
				    {"pl_bar_n", FS::Counter::PathBarN, false},
				    {"pl_sub_ns", FS::Counter::PathSubNs, false},
				    {"pl_sub_n", FS::Counter::PathSubN, false},
				    {"pl_gc_ns", FS::Counter::PathGcNs, false},
				    {"pl_gc_n", FS::Counter::PathGcN, false},
				    {"pl_cmd_ns", FS::Counter::PathCmdNs, false},
				    {"pl_cmd_n", FS::Counter::PathCmdN, false},
				    {"pl_em_vtx_ns", FS::Counter::PathEmVtxNs, false},
				    {"pl_em_rt_ns", FS::Counter::PathEmRtNs, false},
				    {"pl_em_pipe_ns", FS::Counter::PathEmPipeNs, false},
				    {"pl_em_com_ns", FS::Counter::PathEmComNs, false},
				    {"pl_em_rec_ns", FS::Counter::PathEmRecNs, false},
				    {"pl_em_rest_ns", FS::Counter::PathEmRestNs, false},
				    {"pl_em_n", FS::Counter::PathEmN, false},
				    {"be_n", FS::Counter::BdaEveryCalls, false},
				    {"be_ns", FS::Counter::BdaEveryNs, false},
				    {"bf_n", FS::Counter::BindFloorDraws, false},
				    {"bf_disp", FS::Counter::BindFloorDispatch, false},
				    {"bf_push", FS::Counter::BindFloorPush, false},
				    {"bf_pool", FS::Counter::BindFloorPool, false},
				    {"bf_img", FS::Counter::BindFloorImages, false},
				    {"bf_buf", FS::Counter::BindFloorBuffers, false},
				    {"bf_smp", FS::Counter::BindFloorSamplers, false},
				    {"bf_null_tr", FS::Counter::BindFloorNullTrans, false},
				    {"bf_mat", FS::Counter::BindFloorMat, false},
				    {"bf_reuse", FS::Counter::BindFloorReuse, false},
				    {"bf_live_ahead", FS::Counter::BindFloorLiveAhead, false},
				    {"bf_live_mat", FS::Counter::BindFloorLiveMat, false},
				    {"bf_live_memo", FS::Counter::BindFloorLiveMemo, false},
				    {"bf_burn_ns", FS::Counter::BindFloorBurnNs, false},
				    {"bf_burn_cpu_ns", FS::Counter::BindFloorBurnCpuNs, false},
				    {"bf_burn_cpu_n", FS::Counter::BindFloorBurnCpuN, false},
				    {"bf_burn_cpu_bad", FS::Counter::BindFloorBurnCpuBad, false},
				    {"bf_burn_probe_ns", FS::Counter::BindFloorBurnProbeNs, false},
				    {"bf_skip", FS::Counter::BindFloorSkips, false},
				    {"bf_dlskip", FS::Counter::BindFloorDlSkip, false},
				    {"bf_dlskip_kb", FS::Counter::BindFloorDlSkipKb, false},
				    {"bf_gc_hold", FS::Counter::BindFloorGcHold, false},
				    {"bf_igc_checks", FS::Counter::BindFloorImgGcChecks, false},
				    {"bf_igc_hold", FS::Counter::BindFloorImgGcHold, false},
				    {"bf_igc_bad", FS::Counter::BindFloorImgGcBad, false},
				    {"bf_igc_critical", FS::Counter::BindFloorImgGcCritical, false},
				    {"bf_igc_evict", FS::Counter::BindFloorImgGcEvict, false},
				    {"bf_edge", FS::Counter::BindFloorEdges, false},
				    {"bf_bgc_hold", FS::Counter::BindFloorBufGcHold, false},
				    {"bf_ndesc", FS::Counter::BindFloorNullDescs, false},
				    {"bf_xover", FS::Counter::BindFloorXover, false},
				    {"bf_xover_acb", FS::Counter::BindFloorXoverAcb, false},
				    {"bf_mixed", FS::Counter::BindFloorMixed, false},
				    {"bf_defer", FS::Counter::BindFloorDefer, false},
				    {"bf_defer_force", FS::Counter::BindFloorDeferForce, false},
				    {"bf_trig_fire", FS::Counter::BindFloorTrigFire, false},
				    {"bf_trig_wait", FS::Counter::BindFloorTrigWait, false},
				    {"bf_trig_fb", FS::Counter::BindFloorTrigFb, false},
				    {"bf_clr_skip", FS::Counter::BindFloorClrSkip, false},
				    {"gm_ops", FS::Counter::GpuMarkerOps, false},
				    {"gm_ok", FS::Counter::GpuMarkerOk, false},
				    {"gm_bad", FS::Counter::GpuMarkerBad, false},
				    {"gm_unsup", FS::Counter::GpuMarkerUnsup, false},
				    {"gm_live", FS::Counter::GpuMarkerLive, false},
				    {"gm_live_top", FS::Counter::GpuMarkerLiveTop, false},
				    {"bf_skip_drop", FS::Counter::BindFloorSkipDrop, false},
				    // Session 100: clear shortcuts actually taken (both arms, no gate).
				    {"clr_taken_meta", FS::Counter::ClearShortcutMeta, false},
				    {"clr_taken_img", FS::Counter::ClearShortcutImage, false},
				    // Session 100, gate "blmove": the moved-mark census.  Raw ns / counts.
				    {"blm_s0_ns", FS::Counter::BindLapMoveSpan0Ns, false},
				    {"blm_s0_n", FS::Counter::BindLapMoveSpan0N, false},
				    {"blm_s1_ns", FS::Counter::BindLapMoveSpan1Ns, false},
				    {"blm_s1_n", FS::Counter::BindLapMoveSpan1N, false},
				    {"blm_img0", FS::Counter::BindLapMoveImages0, false},
				    {"blm_img1", FS::Counter::BindLapMoveImages1, false},
				    {"blm_smp0", FS::Counter::BindLapMoveSamplers0, false},
				    {"blm_smp1", FS::Counter::BindLapMoveSamplers1, false},
				    // Session 101, gate "cbmove": the moved-mark census of CommitBindings.
				    // Raw ns / counts.
				    {"cm_s0_ns", FS::Counter::CommitLapMoveStage0Ns, false},
				    {"cm_s0_n", FS::Counter::CommitLapMoveStage0N, false},
				    {"cm_s1_ns", FS::Counter::CommitLapMoveStage1Ns, false},
				    {"cm_s1_n", FS::Counter::CommitLapMoveStage1N, false},
				    {"cm_i0", FS::Counter::CommitLapMoveImages0, false},
				    {"cm_i1", FS::Counter::CommitLapMoveImages1, false},
				    {"cm_b0", FS::Counter::CommitLapMoveBindings0, false},
				    {"cm_b1", FS::Counter::CommitLapMoveBindings1, false},
				    {"cm_e0_ns", FS::Counter::CommitLapMoveEmit0Ns, false},
				    {"cm_e0_n", FS::Counter::CommitLapMoveEmit0N, false},
				    {"cm_e1_ns", FS::Counter::CommitLapMoveEmit1Ns, false},
				    {"cm_e1_n", FS::Counter::CommitLapMoveEmit1N, false},
				    {"cm_w0", FS::Counter::CommitLapMoveWrites0, false},
				    {"cm_w1", FS::Counter::CommitLapMoveWrites1, false},
				    {"cm_c0", FS::Counter::CommitLapMoveDesc0, false},
				    {"cm_c1", FS::Counter::CommitLapMoveDesc1, false},
				    // Session 102, knob "dabatch": QueueDrawAhead calls, its arming proof.  Raw count.
				    {"da_qcall", FS::Counter::DrawAheadQueueCalls, false},
				    // Session 103, KYTY_BVH_LOOP_CAP: capped BVH invocations that tripped / came
				    // near the cap (1/16).  Raw counts.
				    {"bl_trip", FS::Counter::LoopCapTrips, false},
				    {"bl_near", FS::Counter::LoopCapNear, false},
				    // Session 105, knob "ctxtick" >= 2: the route-A M3.1 checks.  Raw counts.
				    {"ctx_chk_n", FS::Counter::CtxCheckN, false},
				    {"ctx_chk_bad", FS::Counter::CtxCheckBad, false},
				    {"ctx_midsub", FS::Counter::CtxMidSubmit, false},
				    {"ctx_rec_block", FS::Counter::CtxRecordBlock, false},
				    // Session 106, KYTY_GPU_WALL=1: the GuestGpu thread's wall by region.  Raw ns/counts.
				    {"gw_idle_ns", FS::Counter::GpuWallIdleNs, false},
				    {"gw_idle_n", FS::Counter::GpuWallIdleN, false},
				    {"gw_blk_ns", FS::Counter::GpuWallBlockedNs, false},
				    {"gw_blk_n", FS::Counter::GpuWallBlockedN, false},
				    {"gw_flip_ns", FS::Counter::GpuWallFlipNs, false},
				    {"gw_flip_n", FS::Counter::GpuWallFlipN, false},
				    {"gw_proc_ns", FS::Counter::GpuWallProcNs, false},
				    {"gw_proc_n", FS::Counter::GpuWallProcN, false},
				    {"gw_cmd_ns", FS::Counter::GpuWallCmdNs, false},
				    {"gw_cmd_n", FS::Counter::GpuWallCmdN, false},
				    // Session 107, gate "plkstat": contended m_mutex acquisitions of GuestGpu and the
				    // walker's holds; knob "cspmemo": the compute-prefetch memo.  Raw ns / counts.
				    {"pl_cont_n", FS::Counter::PipeLockContN, false},
				    {"pl_cont_wall_ns", FS::Counter::PipeLockContWallNs, false},
				    {"pl_cont_cpu_ns", FS::Counter::PipeLockContCpuNs, false},
				    {"pl_cont_h0_n", FS::Counter::PipeLockContH0N, false},
				    {"pl_cont_h0_ns", FS::Counter::PipeLockContH0Ns, false},
				    {"pl_cont_h1_n", FS::Counter::PipeLockContH1N, false},
				    {"pl_cont_h1_ns", FS::Counter::PipeLockContH1Ns, false},
				    {"pl_cont_h2_n", FS::Counter::PipeLockContH2N, false},
				    {"pl_cont_h2_ns", FS::Counter::PipeLockContH2Ns, false},
				    {"pl_cont_h3_n", FS::Counter::PipeLockContH3N, false},
				    {"pl_cont_h3_ns", FS::Counter::PipeLockContH3Ns, false},
				    {"pl_wq_hold_ns", FS::Counter::PipeLockWalkQueueHoldNs, false},
				    {"pl_wq_hold_n", FS::Counter::PipeLockWalkQueueHoldN, false},
				    {"pl_wp_hold_ns", FS::Counter::PipeLockWalkPrefHoldNs, false},
				    {"pl_wp_hold_n", FS::Counter::PipeLockWalkPrefHoldN, false},
				    {"cspm_look", FS::Counter::CspMemoLook, false},
				    {"cspm_would", FS::Counter::CspMemoWould, false},
				    {"cspm_skip", FS::Counter::CspMemoSkip, false},
				    {"cspm_bad", FS::Counter::CspMemoBad, false},
				    {"cspm_store", FS::Counter::CspMemoStore, false},
				    {"cspm_clear", FS::Counter::CspMemoClear, false},
				    {"cspf_have", FS::Counter::CspPrefHave, false},
				    {"cspf_new", FS::Counter::CspPrefNew, false},
				    // Session 108: knob "cspfam" and the dispatch-time compile guard.  Raw counts.
				    {"cspfam_look", FS::Counter::CspFamLook, false},
				    {"cspfam_skip", FS::Counter::CspFamSkip, false},
				    {"cs_sync_new", FS::Counter::CsSyncNew, false},
				    {"cs_sync_wait", FS::Counter::CsSyncWait, false},
				    // Session 109: knob "cspfam" v2, family-table clears.  Raw count.
				    {"cspfam_clr", FS::Counter::CspFamClear, false},
				    // Session 109: knob "cspfree".  Raw counts.
				    {"cspfree_look", FS::Counter::CspFreeLook, false},
				    {"cspfree_hit", FS::Counter::CspFreeHit, false},
				    {"cspfree_src_miss", FS::Counter::CspFreeSrcMiss, false},
				    {"cspfree_spec_miss", FS::Counter::CspFreeSpecMiss, false},
				    {"cspfree_mat_fail", FS::Counter::CspFreeMatFail, false},
				    {"cspfree_clr", FS::Counter::CspFreeClear, false},
				    {"cspfree_store", FS::Counter::CspFreeStore, false},
				    {"cspfree_bad", FS::Counter::CspFreeBad, false},
				    {"cspfree_moved", FS::Counter::CspFreeMoved, false},
				    // Session 110: stall duration on the dispatch.  Raw us.
				    {"cs_sync_new_us", FS::Counter::CsSyncNewUs, false},
				    {"cs_sync_wait_us", FS::Counter::CsSyncWaitUs, false},
				    // Session 111: knob "daslot".  Raw counts.
				    {"da_guard_busy", FS::Counter::DaGuardBusy, false},
				    {"da_q_taking", FS::Counter::DaQueueTaking, false},
				    {"da_hint_defer", FS::Counter::DaHintDefer, false},
				    {"da_hint_torn", FS::Counter::DaHintTorn, false},
				    {"da_slot_bad", FS::Counter::DaSlotBad, false},
				    {"da_q_free", FS::Counter::DaQueueFree, false},
				    {"da_chk_ok", FS::Counter::DaCheckOk, false},
				    {"da_chk_bad", FS::Counter::DaCheckBad, false},
				    {"da_q_noguard", FS::Counter::DaQueueNoGuard, false},
				    {"da_guard_yield", FS::Counter::DaGuardYield, false},
				    {"bda_ginv_reg", FS::Counter::BdaGlobalInvReg, false},
				    {"bda_ginv_map", FS::Counter::BdaGlobalInvMap, false},
				    {"bda_rinv", FS::Counter::BdaRegionInv, false},
				    {"bda_nskip", FS::Counter::BdaNarrowSkip, false},
				    {"bda_nwould", FS::Counter::BdaNarrowWould, false},
				    {"bda_nmiss", FS::Counter::BdaNarrowMiss, false},
				    {"bda_nxthr", FS::Counter::BdaNarrowXthread, false},
				    {"bgc_evict", FS::Counter::BufGcEvict, false},
				    {"bda_nrace", FS::Counter::BdaNarrowRace, false},
				    {"prio_unsub", FS::Counter::PrioUnsub, false},
				    {"prio_stall", FS::Counter::PrioStall, false},
				    {"gw_idle_prio", FS::Counter::GpuIdlePrio, false},
				    {"pres_title_ns", FS::Counter::PresTitleNs, false},
				    {"pres_title_n", FS::Counter::PresTitleN, false},
				    {"flip_rsv_wait_ns", FS::Counter::FlipReserveWaitNs, false},
				    {"flip_rsv_wait_n", FS::Counter::FlipReserveWaitN, false},
				    {"flip_hold_ns", FS::Counter::FlipHoldNs, false},
				    {"flip_hold_n", FS::Counter::FlipHoldN, false},
				    {"mt_age_ns", FS::Counter::MainTaskAgeNs, false},
				    {"mt_n", FS::Counter::MainTaskN, false},
				    {"present_overlap", FS::Counter::PresentOverlap, false},
				    {"spine_n", FS::Counter::SpineN, false},
				    {"spine_ns", FS::Counter::SpineNs, false},
				    {"spine_pk", FS::Counter::SpinePackets, false},
				    {"spine_el", FS::Counter::SpineElements, false},
				    {"spine_ib", FS::Counter::SpineIb, false},
				    {"spine_cf_br", FS::Counter::SpineCfBranch, false},
				    {"spine_cf_cond", FS::Counter::SpineCfCond, false},
				    {"spine_cf_pred", FS::Counter::SpineCfPred, false},
				    {"spine_cf_predw", FS::Counter::SpineCfPredWait, false},
				    {"spine_cf_ind", FS::Counter::SpineCfIndirect, false},
				    {"spine_abort", FS::Counter::SpineAbort, false},
				    {"spine_cmp", FS::Counter::SpineCmp, false},
				    {"spine_bad", FS::Counter::SpineBad, false},
				    {"spine_misal", FS::Counter::SpineMisalign, false},
				    {"spine_pad", FS::Counter::SpinePad, false},
				    {"spine_lost", FS::Counter::SpineLost, false},
				    {"spine_chk_ns", FS::Counter::SpineCheckNs, false},
				    {"spine_unc", FS::Counter::SpineUncertain, false},
				    {"carry_cmp", FS::Counter::CarryCmp, false},
				    {"carry_bad", FS::Counter::CarryBad, false},
				    {"carry_skip", FS::Counter::CarrySkip, false},
				    {"sc_frames", FS::Counter::ScFrames, false},
				    {"sc_el", FS::Counter::ScElements, false},
				    {"sc_runs", FS::Counter::ScRuns, false},
				    {"k3_max", FS::Counter::K3MaxRun, false},
				    {"k3_h0", FS::Counter::K3Hist0, false},
				    {"k3_h1", FS::Counter::K3Hist1, false},
				    {"k3_h2", FS::Counter::K3Hist2, false},
				    {"k3_h3", FS::Counter::K3Hist3, false},
				    {"k3_h4", FS::Counter::K3Hist4, false},
				    {"k4_w2_n", FS::Counter::K4W2N, false},
				    {"k4_w2_any", FS::Counter::K4W2Any, false},
				    {"k4_w2_dep", FS::Counter::K4W2Dep, false},
				    {"k4_w2_fmax", FS::Counter::K4W2Fmax, false},
				    {"k4_w4_n", FS::Counter::K4W4N, false},
				    {"k4_w4_any", FS::Counter::K4W4Any, false},
				    {"k4_w4_dep", FS::Counter::K4W4Dep, false},
				    {"k4_w4_fmax", FS::Counter::K4W4Fmax, false},
				    {"k4_nocut", FS::Counter::K4NoCut, false},
				    {"sc_img", FS::Counter::ScImages, false},
				    {"sc_ns", FS::Counter::ScNs, false},
				    {"r1_hn", FS::Counter::R1HitN, false},
				    {"r1_mn", FS::Counter::R1MissN, false},
				    {"r1_sn", FS::Counter::R1StaleN, false},
				    {"r1_hit_ns", FS::Counter::R1HitNs, false},
				    {"r1_hit_t", FS::Counter::R1HitTimed, false},
				    {"r1_miss_ns", FS::Counter::R1MissNs, false},
				    {"r1_nost", FS::Counter::R1NoStoreN, false},
				    {"r1_nost_ns", FS::Counter::R1NoStoreNs, false},
				    {"r1_rb_ns", FS::Counter::R1RbNs, false},
				    {"r1_rb_n", FS::Counter::R1RbN, false},
				    {"r1_rbf_ns", FS::Counter::R1RbfNs, false},
				    {"r1_rbf_n", FS::Counter::R1RbfN, false},
				    {"r1_mp", FS::Counter::R1MissPost, false},
				    {"r1_mp_ns", FS::Counter::R1MissPostNs, false},
				    {"r1_w4_q", FS::Counter::R1W4Pre, false},
				    {"r1_w4_qns", FS::Counter::R1W4PreNs, false},
				    {"r1_w4_p", FS::Counter::R1W4Post, false},
				    {"r1_w4_pns", FS::Counter::R1W4PostNs, false},
				    {"r1_w4_lose", FS::Counter::R1W4Lose, false},
				    {"r1_w4_bad", FS::Counter::R1W4Bad, false},
				    {"r1_w4_rb", FS::Counter::R1W4Rb, false},
				    {"r1_w4_rbns", FS::Counter::R1W4RbNs, false},
				    {"r1_w4_pb_ns", FS::Counter::R1W4ProbeNs, false},
				    {"r1_w8_q", FS::Counter::R1W8Pre, false},
				    {"r1_w8_qns", FS::Counter::R1W8PreNs, false},
				    {"r1_w8_p", FS::Counter::R1W8Post, false},
				    {"r1_w8_pns", FS::Counter::R1W8PostNs, false},
				    {"r1_w8_lose", FS::Counter::R1W8Lose, false},
				    {"r1_w8_bad", FS::Counter::R1W8Bad, false},
				    {"r1_w8_rb", FS::Counter::R1W8Rb, false},
				    {"r1_w8_rbns", FS::Counter::R1W8RbNs, false},
				    {"r1_w8_pb_ns", FS::Counter::R1W8ProbeNs, false},
				    {"r1_d16_q", FS::Counter::R1D16Pre, false},
				    {"r1_d16_qns", FS::Counter::R1D16PreNs, false},
				    {"r1_d16_p", FS::Counter::R1D16Post, false},
				    {"r1_d16_pns", FS::Counter::R1D16PostNs, false},
				    {"r1_d16_bad", FS::Counter::R1D16Bad, false},
				    {"r1_d16_rb", FS::Counter::R1D16Rb, false},
				    {"r1_d16_rbns", FS::Counter::R1D16RbNs, false},
				    {"r1_w1_q", FS::Counter::R1W1Pre, false},
				    {"r1_w1_qns", FS::Counter::R1W1PreNs, false},
				    {"r1_w1_p", FS::Counter::R1W1Post, false},
				    {"r1_w1_pns", FS::Counter::R1W1PostNs, false},
				    {"r1_w1_lose", FS::Counter::R1W1Lose, false},
				    {"r1_w1_bad", FS::Counter::R1W1Bad, false},
				    {"r1_w1_rb", FS::Counter::R1W1Rb, false},
				    {"r1_w1_rbns", FS::Counter::R1W1RbNs, false},
				    {"r1_pb0_ns", FS::Counter::R1Probe0Ns, false},
				    {"r1_pb_n", FS::Counter::R1ProbeN, false},
				    {"r1_am_n", FS::Counter::R1AfterMissN, false},
				    {"r1_ham_ns", FS::Counter::R1HitAfterMissNs, false},
				    {"r1_ham_t", FS::Counter::R1HitAfterMissTimed, false},
				    {"r1_sstale", FS::Counter::R1ShadowStale, false},
				    {"r1_cold", FS::Counter::R1Cold, false},
				    {"r1_reset", FS::Counter::R1Reset, false},
				    {"r1_tagx", FS::Counter::R1TagAlias, false},
				    {"r1_incl", FS::Counter::R1Incl, false},
				    {"r1_xthr", FS::Counter::R1CrossThread, false},
				    {"r1_self_h_ns", FS::Counter::R1SelfHitNs, false},
				    {"r1_self_h_n", FS::Counter::R1SelfHitN, false},
				    {"r1_self_m_ns", FS::Counter::R1SelfMissNs, false},
				    {"r1_self_m_n", FS::Counter::R1SelfMissN, false},
				    {"r1_self_s_ns", FS::Counter::R1SelfStaleNs, false},
				    {"r1_self_s_n", FS::Counter::R1SelfStaleN, false},
				    {"r2_stg", FS::Counter::R2Stages, false},
				    {"r2_noimg", FS::Counter::R2NoImage, false},
				    {"r2_big", FS::Counter::R2Big, false},
				    {"r2_odd", FS::Counter::R2Odd, false},
				    {"r2_prog", FS::Counter::R2SameProgram, false},
				    {"r2_rep", FS::Counter::R2Repeat, false},
				    {"r2_cl", FS::Counter::R2Clean, false},
				    {"r2_mx", FS::Counter::R2Mixed, false},
				    {"r2_cl_ns", FS::Counter::R2CleanNs, false},
				    {"r2_mx_ns", FS::Counter::R2MixedNs, false},
				    {"r2_ot_ns", FS::Counter::R2OtherNs, false},
				    {"r2_cl_sl", FS::Counter::R2CleanSlots, false},
				    {"r2_cl_nul", FS::Counter::R2CleanNull, false},
				    {"r2_mx_sl", FS::Counter::R2MixedSlots, false},
				    {"r2_mx_eq", FS::Counter::R2MixedEqual, false},
				    {"r2_ot_sl", FS::Counter::R2OtherSlots, false},
				    {"r2_s_cl_ns", FS::Counter::R2SampledCleanNs, false},
				    {"r2_s_cl_sl", FS::Counter::R2SampledCleanSlots, false},
				    {"r2_s_cl_nul", FS::Counter::R2SampledCleanNull, false},
				    {"r2_s_mx_ns", FS::Counter::R2SampledMixedNs, false},
				    {"r2_s_mx_sl", FS::Counter::R2SampledMixedSlots, false},
				    {"r2_s_ot_ns", FS::Counter::R2SampledOtherNs, false},
				    {"r2_s_ot_sl", FS::Counter::R2SampledOtherSlots, false},
				    {"r2_sl_eq", FS::Counter::R2SlotSame, false},
				    {"r2_sl_hit", FS::Counter::R2SlotHit, false},
				    {"r2_cl_lod", FS::Counter::R2CleanLod, false},
				    {"r2_cl_dcc", FS::Counter::R2CleanDcc, false},
				    {"r2_cl_bc", FS::Counter::R2CleanBc, false},
				    {"r2_cl_tick", FS::Counter::R2CleanTick, false},
				    {"r2_cl_meta", FS::Counter::R2CleanMeta, false},
				    {"r2_bad", FS::Counter::R2Bad, false},
				    {"r2_bad_key", FS::Counter::R2BadKey, false},
				    {"r2_div", FS::Counter::R2Diverge, false},
				    {"r2_nul_ns", FS::Counter::R2NullNs, false},
				    {"r2_nul_n", FS::Counter::R2Nulls, false},
				    {"r2_wr_ns", FS::Counter::R2WitRepNs, false},
				    {"r2_wr_n", FS::Counter::R2WitReps, false},
				    {"r2_wo_ns", FS::Counter::R2WitOthNs, false},
				    {"r2_wo_n", FS::Counter::R2WitOths, false},
				    {"r2_st_ns", FS::Counter::R2StoreNs, false},
				    {"r2_st_n", FS::Counter::R2Stores, false},
				    {"r2_rm_ns", FS::Counter::R2ReplayNs, false},
				    {"r2_rm_sl", FS::Counter::R2ReplaySlots, false},
				    {"r2_rm_n", FS::Counter::R2Replays, false},
				    // Session 120, gate "spcen" (spcen.md, design120.md section 4): raw ns / raw counts.
				    {"sp_ser_n", FS::Counter::ImageStateSerialBumps, false},
				    {"sp_ser_val", FS::Counter::ImageStateSerialValue, false},
				    {"sp_rt_n", FS::Counter::SpRtDraws, false},
				    {"sp_rt_would", FS::Counter::SpRtWould, false},
				    {"sp_rt_wg", FS::Counter::SpRtWouldGlobal, false},
				    {"sp_rt_tgt", FS::Counter::SpRtTargets, false},
				    {"pl_em_spchk_ns", FS::Counter::PathEmSpChkNs, false},
				    {"sp_rt_chkh_ns", FS::Counter::SpRtChkHitNs, false},
				    {"pl_em_rt_hit_ns", FS::Counter::PathEmRtHitNs, false},
				    {"pl_em_rt_hitg_ns", FS::Counter::PathEmRtHitGNs, false},
				    {"pl_em_sppost_ns", FS::Counter::PathEmSpPostNs, false},
				    {"sp_rt_rep_ns", FS::Counter::SpRtRepNs, false},
				    {"sp_rt_rep_att", FS::Counter::SpRtRepAtt, false},
				    {"sp_rt_rep_kpx", FS::Counter::SpRtRepKpx, false},
				    {"sp_rt_rec", FS::Counter::SpRtRecords, false},
				    {"sp_rt_rec_ns", FS::Counter::SpRtRecNs, false},
				    {"sp_rt_bad", FS::Counter::SpRtBad, false},
				    {"sp_rt_race", FS::Counter::SpRtRace, false},
				    {"sp_rt_rst", FS::Counter::SpRtRestart, false},
				    {"sp_rt_nt", FS::Counter::SpRtUntimed, false},
				    {"sp_rt_x_memo", FS::Counter::SpRtMissMemo, false},
				    {"sp_rt_x_cfg", FS::Counter::SpRtMissCfg, false},
				    {"sp_rt_x_dclr", FS::Counter::SpRtMissDepthClear, false},
				    {"sp_rt_x_meta", FS::Counter::SpRtMissMeta, false},
				    {"sp_rt_x_ids", FS::Counter::SpRtMissIds, false},
				    {"sp_rt_x_live", FS::Counter::SpRtMissLive, false},
				    {"sp_rt_x_ser", FS::Counter::SpRtMissSerial, false},
				    {"sp_rt_x_bound", FS::Counter::SpRtMissBound, false},
				    {"sp_rt_x_dsmp", FS::Counter::SpRtMissDepthSampled, false},
				    {"sp_rt_x_pass", FS::Counter::SpRtMissPass, false},
				    {"sp_tr_n", FS::Counter::SpTrStages, false},
				    {"sp_tr_slots", FS::Counter::SpTrSlots, false},
				    {"sp_tr_would", FS::Counter::SpTrWould, false},
				    {"sp_tr_wg", FS::Counter::SpTrWouldGlobal, false},
				    {"sp_tr_wslots", FS::Counter::SpTrWouldSlots, false},
				    {"sp_tr_loop_ns", FS::Counter::SpTrLoopNs, false},
				    {"bl_tr_hit_ns", FS::Counter::BindLapTrHitNs, false},
				    {"bl_tr_hitg_ns", FS::Counter::BindLapTrHitGNs, false},
				    {"sp_tr_chk_ns", FS::Counter::SpTrChkNs, false},
				    {"sp_tr_chkh_ns", FS::Counter::SpTrChkHitNs, false},
				    {"sp_tr_post_ns", FS::Counter::SpTrPostNs, false},
				    {"sp_tr_rep_ns", FS::Counter::SpTrRepNs, false},
				    {"sp_tr_rec", FS::Counter::SpTrRecords, false},
				    {"sp_tr_rec_ns", FS::Counter::SpTrRecNs, false},
				    {"sp_tr_bad", FS::Counter::SpTrBad, false},
				    {"sp_tr_dcc", FS::Counter::SpTrDcc, false},
				    {"sp_tr_x_big", FS::Counter::SpTrMissBig, false},
				    {"sp_tr_x_memo", FS::Counter::SpTrMissMemo, false},
				    {"sp_tr_x_meta", FS::Counter::SpTrMissMeta, false},
				    {"sp_tr_x_shape", FS::Counter::SpTrMissShape, false},
				    {"sp_tr_x_ser", FS::Counter::SpTrMissSerial, false},
				    {"sp_tr_x_flags", FS::Counter::SpTrMissFlags, false},
				    {"tm8_fill", FS::Counter::Tm8Fill, false},
				    {"tm8_evict", FS::Counter::Tm8Evict, false},
				    {"tm8_evict_view", FS::Counter::Tm8EvictView, false},
				    {"tm8_alias", FS::Counter::Tm8Alias, false},
				    {"tm8_inval", FS::Counter::Tm8Inval, false},
				    {"tm8_mode", FS::Counter::Tm8Mode, false},
				    {"tm8_renorm", FS::Counter::Tm8Renorm, false},
				    {"tm8_x2", FS::Counter::Tm8WithMemo2, false},
				    {"tm8_cenoff", FS::Counter::Tm8CensusOff, false},
				    {"tm8_look", FS::Counter::Tm8Look, false},
				    {"tm8_hit", FS::Counter::Tm8Hit, false},
				    {"tm8_miss", FS::Counter::Tm8Miss, false},
				    {"tm8_stale", FS::Counter::Tm8Stale, false},
				    {"tm8_gain", FS::Counter::Tm8Gain, false},
				    {"tm8_vchk", FS::Counter::Tm8Check, false},
				    {"tm8_bad", FS::Counter::Tm8Bad, false},
				    {"tm8_vctl", FS::Counter::Tm8CtlCheck, false},
				    {"tm8_vctl_bad", FS::Counter::Tm8CtlBad, false},
				    {"tm8_relive", FS::Counter::Tm8Relive, false},
				    {"tm8_inject", FS::Counter::Tm8Inject, false},
				    {"tm8_inject_miss", FS::Counter::Tm8InjectMiss, false},
				    {"tm8_dlose", FS::Counter::Tm8DirectLose, false},
				    {"tm8_ddiff", FS::Counter::Tm8DirectDiff, false},
				    {"tm8_dcc_chg", FS::Counter::Tm8DccChange, false},
				    {"tm8_rbchk", FS::Counter::Tm8RbCheck, false},
				    {"tm8_rbbad", FS::Counter::Tm8RbBad, false},
				    {"tm8_rbinject", FS::Counter::Tm8RbInject, false},
				    {"tm8_rbinject_miss", FS::Counter::Tm8RbInjectMiss, false},
				    {"tm8_pb0_ns", FS::Counter::Tm8Probe0Ns, false},
				    {"tm8_pb_ns", FS::Counter::Tm8ProbeNs, false},
				    {"tm8_pb_n", FS::Counter::Tm8ProbeN, false},
				    {"burn_g_ns", FS::Counter::BurnGNs, false},
				    {"burn_g_n", FS::Counter::BurnGN, false},
				    {"burn_g_cpu_ns", FS::Counter::BurnGCpuNs, false},
				    {"burn_g_cpu_w", FS::Counter::BurnGCpuW, false},
				    {"burn_g_seen", FS::Counter::BurnGSeen, false},
				    {"burn_r_ns", FS::Counter::BurnRNs, false},
				    {"burn_r_n", FS::Counter::BurnRN, false},
				    {"burn_r_q", FS::Counter::BurnRQ, false},
				    {"burn_r_cpu_ns", FS::Counter::BurnRCpuNs, false},
				    {"burn_r_cpu_w", FS::Counter::BurnRCpuW, false},
				    {"burn_r_seen", FS::Counter::BurnRSeen, false},
				    {"burn_m_ns", FS::Counter::BurnMNs, false},
				    {"burn_m_n", FS::Counter::BurnMN, false},
				    {"burn_m_q", FS::Counter::BurnMQ, false},
				    {"burn_m_cpu_ns", FS::Counter::BurnMCpuNs, false},
				    {"burn_m_cpu_w", FS::Counter::BurnMCpuW, false},
				    {"burn_m_seen", FS::Counter::BurnMSeen, false},
				    {"burn_m0_seen", FS::Counter::BurnM0Seen, false},
				    {"burn_t_ns", FS::Counter::BurnTNs, false},
				    {"burn_t_n", FS::Counter::BurnTN, false},
				    {"burn_t_cpu_ns", FS::Counter::BurnTCpuNs, false},
				    {"burn_t_cpu_w", FS::Counter::BurnTCpuW, false},
				    {"burn_t_seen", FS::Counter::BurnTSeen, false},
				    {"burn_s_seen", FS::Counter::BurnSSeen, false},
				    {"burn_s_main", FS::Counter::BurnSMain, false},
				    {"burn_p_ns", FS::Counter::BurnPNs, false},
				    {"burn_p_n", FS::Counter::BurnPN, false},
				    {"burn_p_cpu_ns", FS::Counter::BurnPCpuNs, false},
				    {"burn_p_cpu_w", FS::Counter::BurnPCpuW, false},
				    {"burn_p_seen", FS::Counter::BurnPSeen, false},
				    {"burn_late", FS::Counter::BurnLate, false},
				    {"burn_cpu_bad", FS::Counter::BurnCpuBad, false},
				    // Session 123, knob "skipceil" (design123.md s.4): 7 S_live + 17 ceiling + 59 census, raw.
				    {"skc_gf", FS::Counter::SkcGf, false},
				    {"skc_held_inc", FS::Counter::SkcHeldInc, false},
				    {"skc_ap_skip", FS::Counter::SkcApSkip, false},
				    {"skc_pres_ns", FS::Counter::SkcPresNs, false},
				    {"skc_pres_n", FS::Counter::SkcPresN, false},
				    {"skc_gc_crit", FS::Counter::SkcGcCrit, false},
				    {"skc_bgc_crit", FS::Counter::SkcBgcCrit, false},
				    {"skc_on", FS::Counter::SkcOn, false},
				    {"skc_edge", FS::Counter::SkcEdge, false},
				    {"skc_refuse", FS::Counter::SkcRefuse, false},
				    {"skc_skipf", FS::Counter::SkcSkipF, false},
				    {"skc_sd", FS::Counter::SkcSd, false},
				    {"skc_skipd", FS::Counter::SkcSkipD, false},
				    {"skc_keepd", FS::Counter::SkcKeepD, false},
				    {"skc_zerod", FS::Counter::SkcZeroD, false},
				    {"skc_mark", FS::Counter::SkcMark, false},
				    {"skc_mark_miss", FS::Counter::SkcMarkMiss, false},
				    {"skc_held", FS::Counter::SkcHeld, false},
				    {"skc_bad", FS::Counter::SkcBad, false},
				    {"skc_xthr", FS::Counter::SkcXthr, false},
				    {"skc_cpuflip", FS::Counter::SkcCpuFlip, false},
				    {"skc_gds", FS::Counter::SkcGds, false},
				    {"skc_gc_hold", FS::Counter::SkcGcHold, false},
				    {"skc_bgc_hold", FS::Counter::SkcBgcHold, false},
				    {"skc_c_f", FS::Counter::SkcCF, false},
				    {"skc_c_df", FS::Counter::SkcCDf, false},
				    {"skc_c_dd", FS::Counter::SkcCDd, false},
				    {"skc_c_dp", FS::Counter::SkcCDp, false},
				    {"skc_w_db", FS::Counter::SkcWDb, false},
				    {"skc_w_db_kb", FS::Counter::SkcWDbKb, false},
				    {"skc_w_di", FS::Counter::SkcWDi, false},
				    {"skc_w_t", FS::Counter::SkcWT, false},
				    {"skc_w_k", FS::Counter::SkcWK, false},
				    {"skc_w_maybe", FS::Counter::SkcWMaybe, false},
				    {"skc_w_xthr", FS::Counter::SkcWXthr, false},
				    {"skc_r_g", FS::Counter::SkcRG, false},
				    {"skc_r_g_d", FS::Counter::SkcRGD, false},
				    {"skc_r_g_t", FS::Counter::SkcRGT, false},
				    {"skc_r_g_d_kb", FS::Counter::SkcRGDKb, false},
				    {"skc_r_c", FS::Counter::SkcRC, false},
				    {"skc_r_c_d", FS::Counter::SkcRCD, false},
				    {"skc_r_c_t", FS::Counter::SkcRCT, false},
				    {"skc_rc_all", FS::Counter::SkcRcAll, false},
				    {"skc_rc_wrm_d", FS::Counter::SkcRcWrmD, false},
				    {"skc_rc_wrm_t", FS::Counter::SkcRcWrmT, false},
				    {"skc_rc_cond_d", FS::Counter::SkcRcCondD, false},
				    {"skc_rc_cond_t", FS::Counter::SkcRcCondT, false},
				    {"skc_rc_pred_d", FS::Counter::SkcRcPredD, false},
				    {"skc_rc_pred_t", FS::Counter::SkcRcPredT, false},
				    {"skc_rc_icnt_d", FS::Counter::SkcRcIcntD, false},
				    {"skc_rc_icnt_t", FS::Counter::SkcRcIcntT, false},
				    {"skc_rc_iarg_d", FS::Counter::SkcRcIargD, false},
				    {"skc_rc_iarg_t", FS::Counter::SkcRcIargT, false},
				    {"skc_rc_dind_d", FS::Counter::SkcRcDindD, false},
				    {"skc_rc_dind_t", FS::Counter::SkcRcDindT, false},
				    {"skc_r_p", FS::Counter::SkcRP, false},
				    {"skc_r_p_d", FS::Counter::SkcRPD, false},
				    {"skc_r_p_t", FS::Counter::SkcRPT, false},
				    {"skc_r_m_d", FS::Counter::SkcRMD, false},
				    {"skc_r_m_t", FS::Counter::SkcRMT, false},
				    {"skc_r_i_d", FS::Counter::SkcRID, false},
				    {"skc_r_i_t", FS::Counter::SkcRIT, false},
				    {"skc_c_gdsd", FS::Counter::SkcCGdsd, false},
				    {"skc_r_gds", FS::Counter::SkcRGds, false},
				    {"skc_x0_cs", FS::Counter::SkcX0Cs, false},
				    {"skc_x0_keep", FS::Counter::SkcX0Keep, false},
				    {"skc_x0_dma", FS::Counter::SkcX0Dma, false},
				    {"skc_x1_rd", FS::Counter::SkcX1Rd, false},
				    {"skc_x1_draw", FS::Counter::SkcX1Draw, false},
				    {"skc_x1_cs", FS::Counter::SkcX1Cs, false},
				    {"skc_x1_pass", FS::Counter::SkcX1Pass, false},
				    {"skc_x1_img", FS::Counter::SkcX1Img, false},
				    {"skc_x1_wd", FS::Counter::SkcX1Wd, false},
				    {"skc_x1_wp", FS::Counter::SkcX1Wp, false},
				    {"skc_x1_buf", FS::Counter::SkcX1Buf, false},
				    {"skc_x1_dma", FS::Counter::SkcX1Dma, false},
				    {"skc_x1_att", FS::Counter::SkcX1Att, false},
				    {"skc_x2_rd", FS::Counter::SkcX2Rd, false},
				    {"skc_xt_rd", FS::Counter::SkcXtRd, false},
				    {"skc_ia", FS::Counter::SkcIa, false},
				    {"skc_ia_d", FS::Counter::SkcIaD, false},
				    {"skc_ia_t", FS::Counter::SkcIaT, false},
				    {"skc_dma_all", FS::Counter::SkcDmaAll, false},
				    {"skc_lod_n", FS::Counter::SkcLodN, false},
				    {"skc_lod_d", FS::Counter::SkcLodD, false},
				    {"skc_lod_all", FS::Counter::SkcLodAll, false},
				    {"skc_erase_cmd", FS::Counter::SkcEraseCmd, false},
				    {"skc_lod_smp0", FS::Counter::SkcLodSmp0, false},
				    {"skc_lod_smp1", FS::Counter::SkcLodSmp1, false},
				    {"skc_lod_pmiss", FS::Counter::SkcLodPmiss, false},
				    {"skc_lod_pbad", FS::Counter::SkcLodPbad, false},
				    {"skc_lod_noanc", FS::Counter::SkcLodNoanc, false},
				    // Session 124, knob "skipceil" (design124.md rev 2 s.8): 1 mode 2' + 63 graph + 13 time, raw.
				    {"skc_lod_dkeep", FS::Counter::SkcLodDkeep, false},
				    {"skc3_f", FS::Counter::Skc3F, false},
				    {"skc3_open2", FS::Counter::Skc3Open2, false},
				    {"skc3_pollf", FS::Counter::Skc3Pollf, false},
				    {"skc3_d", FS::Counter::Skc3D, false},
				    {"skc3_d_empty", FS::Counter::Skc3DEmpty, false},
				    {"skc3_nodes", FS::Counter::Skc3Nodes, false},
				    {"skc3_wr", FS::Counter::Skc3Wr, false},
				    {"skc3_ed", FS::Counter::Skc3Ed, false},
				    {"skc3_need_l", FS::Counter::Skc3NeedL, false},
				    {"skc3_free_l", FS::Counter::Skc3FreeL, false},
				    {"skc3_free_l_empty", FS::Counter::Skc3FreeLEmpty, false},
				    {"skc3_need_b", FS::Counter::Skc3NeedB, false},
				    {"skc3_free_b", FS::Counter::Skc3FreeB, false},
				    {"skc3_need_lp", FS::Counter::Skc3NeedLp, false},
				    {"skc3_need_ld", FS::Counter::Skc3NeedLd, false},
				    {"skc3_need_lu", FS::Counter::Skc3NeedLu, false},
				    {"skc3_need_lw", FS::Counter::Skc3NeedLw, false},
				    {"skc3_need_lt", FS::Counter::Skc3NeedLt, false},
				    {"skc3_cl_cpu", FS::Counter::Skc3ClCpu, false},
				    {"skc3_cl_cp", FS::Counter::Skc3ClCp, false},
				    {"skc3_cl_gds", FS::Counter::Skc3ClGds, false},
				    {"skc3_cl_poll", FS::Counter::Skc3ClPoll, false},
				    {"skc3_cl_next", FS::Counter::Skc3ClNext, false},
				    {"skc3_cl_flip", FS::Counter::Skc3ClFlip, false},
				    {"skc3_via_w1", FS::Counter::Skc3ViaW1, false},
				    {"skc3_via_w2", FS::Counter::Skc3ViaW2, false},
				    {"skc3_via_w3", FS::Counter::Skc3ViaW3, false},
				    {"skc3_via_m", FS::Counter::Skc3ViaM, false},
				    {"skc3_nocause", FS::Counter::Skc3Nocause, false},
				    {"skc3_lnb", FS::Counter::Skc3Lnb, false},
				    {"skc3_lsup", FS::Counter::Skc3Lsup, false},
				    {"skc3_s_cpu", FS::Counter::Skc3SCpu, false},
				    {"skc3_s_cp", FS::Counter::Skc3SCp, false},
				    {"skc3_s_gds", FS::Counter::Skc3SGds, false},
				    {"skc3_s_next", FS::Counter::Skc3SNext, false},
				    {"skc3_s_flip", FS::Counter::Skc3SFlip, false},
				    {"skc3_s_flipx", FS::Counter::Skc3SFlipx, false},
				    {"skc3_s_pref", FS::Counter::Skc3SPref, false},
				    {"skc3_s_pend", FS::Counter::Skc3SPend, false},
				    {"skc3_s_xmm", FS::Counter::Skc3SXmm, false},
				    {"skc3_sub_drop", FS::Counter::Skc3SubDrop, false},
				    {"skc3_att_unk", FS::Counter::Skc3AttUnk, false},
				    {"skc3_gds_unk", FS::Counter::Skc3GdsUnk, false},
				    {"skc3_dma_ep", FS::Counter::Skc3DmaEp, false},
				    {"skc3_dma_cut", FS::Counter::Skc3DmaCut, false},
				    {"skc3_lazy_n", FS::Counter::Skc3LazyN, false},
				    {"skc3_lazy_in", FS::Counter::Skc3LazyIn, false},
				    {"skc3_w3_nw", FS::Counter::Skc3W3Nw, false},
				    {"skc3_mclr_n", FS::Counter::Skc3MclrN, false},
				    {"skc3_mclr", FS::Counter::Skc3Mclr, false},
				    {"skc3_mclr_pend", FS::Counter::Skc3MclrPend, false},
				    {"skc3_cl_late", FS::Counter::Skc3ClLate, false},
				    {"skc3_cl_late_nw", FS::Counter::Skc3ClLateNw, false},
				    {"skc3_cpw_n", FS::Counter::Skc3CpwN, false},
				    {"skc3_cpw_hit", FS::Counter::Skc3CpwHit, false},
				    {"skc3_sync_img", FS::Counter::Skc3SyncImg, false},
				    {"skc3_m_gds", FS::Counter::Skc3MGds, false},
				    {"skc3_w2d", FS::Counter::Skc3W2d, false},
				    {"skc3_pc_n", FS::Counter::Skc3PcN, false},
				    {"skc3_pc_bad", FS::Counter::Skc3PcBad, false},
				    {"skc3_x1c_n", FS::Counter::Skc3X1cN, false},
				    {"skc3_x1c_sub", FS::Counter::Skc3X1cSub, false},
				    {"skc3_x1c_clr", FS::Counter::Skc3X1cClr, false},
				    {"skc3_x1c_bad", FS::Counter::Skc3X1cBad, false},
				    {"skc3_x1c_ovr", FS::Counter::Skc3X1cOvr, false},
				    {"skc3_x1c_chk", FS::Counter::Skc3X1cChk, false},
				    {"skc3_xthr", FS::Counter::Skc3Xthr, false},
				    {"skc3_bad", FS::Counter::Skc3Bad, false},
				    {"skc3_orphan", FS::Counter::Skc3Orphan, false},
				    {"skc3_wd_ns", FS::Counter::Skc3WdNs, false},
				    {"skc3_pd_n", FS::Counter::Skc3PdN, false},
				    {"skc3_wfree_l_ns", FS::Counter::Skc3WfreeLNs, false},
				    {"skc3_pfree_l_n", FS::Counter::Skc3PfreeLN, false},
				    {"skc3_wfree_b_ns", FS::Counter::Skc3WfreeBNs, false},
				    {"skc3_pfree_b_n", FS::Counter::Skc3PfreeBN, false},
				    {"skc3_gc_ns", FS::Counter::Skc3GcNs, false},
				    {"skc3_gc_pn", FS::Counter::Skc3GcPn, false},
				    {"skc3_gc_n", FS::Counter::Skc3GcN, false},
				    {"skc3_fr_ns", FS::Counter::Skc3FrNs, false},
				    {"skc3_fr_pn", FS::Counter::Skc3FrPn, false},
				    {"skc3_cal_ns", FS::Counter::Skc3CalNs, false},
				    {"skc3_cal_n", FS::Counter::Skc3CalN, false},
				    {"skc3_tin_ns", FS::Counter::Skc3TinNs, false},
				    {"skc3_tin_n", FS::Counter::Skc3TinN, false},
				    // Session 126, knob "rk3cen" (design126.md rev 2 s.4.5): 39 counters, raw.
				    {"rk3_n", FS::Counter::Rk3N, false},
				    {"rk3_rec0", FS::Counter::Rk3Rec0, false},
				    {"rk3_xw", FS::Counter::Rk3Xw, false},
				    {"rk3_w", FS::Counter::Rk3W, false},
				    {"rk3_wi", FS::Counter::Rk3Wi, false},
				    {"rk3_xid", FS::Counter::Rk3Xid, false},
				    {"rk3_xw_irr", FS::Counter::Rk3XwIrr, false},
				    {"rk3_xctx", FS::Counter::Rk3Xctx, false},
				    {"rk3_dclr", FS::Counter::Rk3Dclr, false},
				    {"rk3_r_dclr", FS::Counter::Rk3RDclr, false},
				    {"rk3_slow", FS::Counter::Rk3Slow, false},
				    {"rk3_r_slow", FS::Counter::Rk3RSlow, false},
				    {"rk3_wr_set", FS::Counter::Rk3WrSet, false},
				    {"rk3_wr_obj", FS::Counter::Rk3WrObj, false},
				    {"rk3_ovf", FS::Counter::Rk3Ovf, false},
				    {"rk3_c4_n", FS::Counter::Rk3C4N, false},
				    {"rk3_rt_ns", FS::Counter::Rk3RtNs, false},
				    {"rk3_rt_r_ns", FS::Counter::Rk3RtRNs, false},
				    {"rk3_rt_w_ns", FS::Counter::Rk3RtWNs, false},
				    {"rk3_rt_rec0_ns", FS::Counter::Rk3RtRec0Ns, false},
				    {"rk3_rt_r1_ns", FS::Counter::Rk3RtR1Ns, false},
				    {"rk3_res_ns", FS::Counter::Rk3ResNs, false},
				    {"rk3_res_r_ns", FS::Counter::Rk3ResRNs, false},
				    {"rk3_res_r1_ns", FS::Counter::Rk3ResR1Ns, false},
				    {"rk3_res_x_ns", FS::Counter::Rk3ResXNs, false},
				    {"rk3_res_x_n", FS::Counter::Rk3ResXN, false},
				    {"pl_em_rk3_ns", FS::Counter::PathEmRk3Ns, false},
				    {"rk3_sp_view_ns", FS::Counter::Rk3SpViewNs, false},
				    {"rk3_sp_tr_ns", FS::Counter::Rk3SpTrNs, false},
				    {"rk3_sp_dm_ns", FS::Counter::Rk3SpDmNs, false},
				    {"rk3_sp_n", FS::Counter::Rk3SpN, false},
				    {"rk3_v", FS::Counter::Rk3V, false},
				    {"rk3_vw", FS::Counter::Rk3Vw, false},
				    {"rk3_wmiss", FS::Counter::Rk3Wmiss, false},
				    {"rk3_rt_v_ns", FS::Counter::Rk3RtVNs, false},
				    {"rk3_res_v_ns", FS::Counter::Rk3ResVNs, false},
				    {"rk3_nt", FS::Counter::Rk3Nt, false},
				    {"rk3_xthr", FS::Counter::Rk3Xthr, false},
				    {"rk3_acqw", FS::Counter::Rk3Acqw, false},
				    // Session 127, knob "rtskip" (design127.md rev 2 s.7.1): raw counts.
				    {"rts_n", FS::Counter::RtsN, false},
				    {"rts_skip", FS::Counter::RtsSkip, false},
				    {"rts_xa_rec", FS::Counter::RtsXaRec, false},
				    {"rts_xa_cfg", FS::Counter::RtsXaCfg, false},
				    {"rts_xa_reg", FS::Counter::RtsXaReg, false},
				    {"rts_xa_arg", FS::Counter::RtsXaArg, false},
				    {"rts_xa_unh", FS::Counter::RtsXaUnh, false},
				    {"rts_xa_memo", FS::Counter::RtsXaMemo, false},
				    {"rts_xa_img", FS::Counter::RtsXaImg, false},
				    {"rts_xb_ids", FS::Counter::RtsXbIds, false},
				    {"rts_xb_live", FS::Counter::RtsXbLive, false},
				    {"rts_xb_meta", FS::Counter::RtsXbMeta, false},
				    {"rts_xb_ser", FS::Counter::RtsXbSer, false},
				    {"rts_xb_bound", FS::Counter::RtsXbBound, false},
				    {"rts_xb_pass", FS::Counter::RtsXbPass, false},
				    {"rts_rec_x", FS::Counter::RtsRecX, false},
				    {"rts_ovf", FS::Counter::RtsOvf, false},
				    {"rts_refuse", FS::Counter::RtsRefuse, false},
				    {"rts_xthr", FS::Counter::RtsXthr, false},
				    {"rts_acqw", FS::Counter::RtsAcqw, false},
				    {"rts_pa", FS::Counter::RtsPa, false},
				    {"rts_pb", FS::Counter::RtsPb, false},
				    {"rts_chk", FS::Counter::RtsChk, false},
				    {"rts_chk_b", FS::Counter::RtsChkB, false},
				    {"rts_chain2", FS::Counter::RtsChain2, false},
				    {"rts_bad", FS::Counter::RtsBad, false},
				    {"rts_bad_noreg", FS::Counter::RtsBadNoreg, false},
				    {"rts_race", FS::Counter::RtsRace, false},
				    {"rts_rec", FS::Counter::RtsRec, false},
				    {"rts_wr", FS::Counter::RtsWr, false},
				    {"rts_wr_obj", FS::Counter::RtsWrObj, false},
				    {"rts_lost", FS::Counter::RtsLost, false},
				    {"rts_early", FS::Counter::RtsEarly, false},
				    // Session 128, knob "protceil" (design128.md s.7.1, ROADMAP s122 item 89(zh)); pc_u_live after the loop.
				    {"prot_gpu_ro_ns", FS::Counter::ProtGpuRoNs, false},
				    {"prot_gpu_ro_n", FS::Counter::ProtGpuRoN, false},
				    {"prot_gpu_ro_pages", FS::Counter::ProtGpuRoPages, false},
				    {"prot_gpu_na_ns", FS::Counter::ProtGpuNaNs, false},
				    {"prot_gpu_na_n", FS::Counter::ProtGpuNaN, false},
				    {"prot_gpu_rw_ns", FS::Counter::ProtGpuRwNs, false},
				    {"prot_gpu_rw_n", FS::Counter::ProtGpuRwN, false},
				    {"pc_op0", FS::Counter::PcOp0, false},
				    {"pc_op1", FS::Counter::PcOp1, false},
				    {"pc_refuse", FS::Counter::PcRefuse, false},
				    {"pc_offthr", FS::Counter::PcOffThr, false},
				    {"pc_elig_ns", FS::Counter::PcEligNs, false},
				    {"pc_elig_n", FS::Counter::PcEligN, false},
				    {"pc_elig_pages", FS::Counter::PcEligPages, false},
				    {"pc_elig_scope_n", FS::Counter::PcEligScopeN, false},
				    {"pc_elig_rng_n", FS::Counter::PcEligRngN, false},
				    {"pc_skip_n", FS::Counter::PcSkipN, false},
				    {"pc_skip_pages", FS::Counter::PcSkipPages, false},
				    {"pc_skip_scope_n", FS::Counter::PcSkipScopeN, false},
				    {"pc_skip_rng_n", FS::Counter::PcSkipRngN, false},
				    {"pc_u_set", FS::Counter::PcUSet, false},
				    {"pc_u_clr", FS::Counter::PcUClr, false},
				    {"pc_rearm_n", FS::Counter::PcRearmN, false},
				    {"pc_rearm_runs", FS::Counter::PcRearmRuns, false},
				    {"pc_rearm_pages", FS::Counter::PcRearmPages, false},
				    {"pc_rearm_ns", FS::Counter::PcRearmNs, false},
				    {"pc_rearm_decl", FS::Counter::PcRearmDecl, false},
				    {"pc_rearm_pend", FS::Counter::PcRearmPend, false},
				    {"pc_rearm_odd", FS::Counter::PcRearmOdd, false},
				    {"pc_vfy_u", FS::Counter::PcVfyU, false},
				    {"pc_vfy_u_na", FS::Counter::PcVfyUNa, false},
				    {"pc_vfy_u_ro", FS::Counter::PcVfyURo, false},
				    // Value 2 of "protceil" (ROADMAP s122 item 93(g)(1)).
				    {"pc_dose_n", FS::Counter::PcDoseN, false},
				    {"pc_dose_ns", FS::Counter::PcDoseNs, false},
				    // Session 129, knob "armcopy" (design129.md rev 2 s.9.1): raw counts / ns / pages.
				    {"ac_op0", FS::Counter::AcOp0, false},
				    {"ac_n", FS::Counter::AcN, false},
				    {"ac_refuse", FS::Counter::AcRefuse, false},
				    {"ac_offthr", FS::Counter::AcOffThr, false},
				    {"ac_jobs", FS::Counter::AcJobs, false},
				    {"ac_chunks", FS::Counter::AcChunks, false},
				    {"ac_moved_n", FS::Counter::AcMovedN, false},
				    {"ac_moved_ns", FS::Counter::AcMovedNs, false},
				    {"ac_moved_pages", FS::Counter::AcMovedPages, false},
				    {"ac_kept_n", FS::Counter::AcKeptN, false},
				    {"ac_kept_ns", FS::Counter::AcKeptNs, false},
				    {"ac_kept_inl_n", FS::Counter::AcKeptInlN, false},
				    {"ac_kept_inl_ns", FS::Counter::AcKeptInlNs, false},
				    {"ac_kept_gap_n", FS::Counter::AcKeptGapN, false},
				    {"ac_kept_gap_ns", FS::Counter::AcKeptGapNs, false},
				    {"ac_kept_full_n", FS::Counter::AcKeptFullN, false},
				    {"ac_kept_full_ns", FS::Counter::AcKeptFullNs, false},
				    {"ac_kept_tmp_n", FS::Counter::AcKeptTmpN, false},
				    {"ac_kept_tmp_ns", FS::Counter::AcKeptTmpNs, false},
				    {"ac_kept_wr_n", FS::Counter::AcKeptWrN, false},
				    {"ac_kept_wr_ns", FS::Counter::AcKeptWrNs, false},
				    {"ac_kept_help_n", FS::Counter::AcKeptHelpN, false},
				    {"ac_kept_help_ns", FS::Counter::AcKeptHelpNs, false},
				    {"ac_job_other_n", FS::Counter::AcJobOtherN, false},
				    {"ac_job_nowork", FS::Counter::AcJobNowork, false},
				    {"ac_job_wait_ns", FS::Counter::AcJobWaitNs, false},
				    {"ac_chk", FS::Counter::AcChk, false},
				    {"ac_bad", FS::Counter::AcBad, false},
				    {"ac_chk_ns", FS::Counter::AcChkNs, false},
				    {"ac_jleft", FS::Counter::AcJleft, false},
				    {"ac_jremark", FS::Counter::AcJremark, false},
				    {"ac_gchk", FS::Counter::AcGchk, false},
				    {"ac_gbad", FS::Counter::AcGbad, false},
				    {"ac_gchk_ns", FS::Counter::AcGchkNs, false},
				    {"ac_gjleft", FS::Counter::AcGjleft, false},
				    {"ac_orphan", FS::Counter::AcOrphan, false},
				    {"ac_cmp_pages", FS::Counter::AcCmpPages, false},
				    {"ac_cdiff", FS::Counter::AcCdiff, false},
				    {"ac_cbad", FS::Counter::AcCbad, false},
				    {"ac_jstale", FS::Counter::AcJstale, false},
				    // Session 130, knob "acinline" (design130.md rev 2 s.9.1): raw counts / ns / bytes / pages.
				    {"ai_n", FS::Counter::AiN, false},
				    {"ai_idle", FS::Counter::AiIdle, false},
				    {"ai_cand", FS::Counter::AiCand, false},
				    {"ai_enq_items", FS::Counter::AiEnqItems, false},
				    {"ai_jobs", FS::Counter::AiJobs, false},
				    {"ai_op_ns", FS::Counter::AiOpNs, false},
				    {"ai_op_n", FS::Counter::AiOpN, false},
				    {"ai_kept_big_n", FS::Counter::AiKeptBigN, false},
				    {"ai_kept_big_ns", FS::Counter::AiKeptBigNs, false},
				    {"ai_copy_nowin", FS::Counter::AiCopyNowin, false},
				    {"ai_copy_nomap", FS::Counter::AiCopyNomap, false},
				    {"ai_b", FS::Counter::AiB, false},
				    {"ai_pages", FS::Counter::AiPages, false},
				    {"ai_enq", FS::Counter::AiEnq, false},
				    {"ai_enq_ns", FS::Counter::AiEnqNs, false},
				    {"ai_moved_n", FS::Counter::AiMovedN, false},
				    {"ai_moved_ns", FS::Counter::AiMovedNs, false},
				    {"ai_moved_pages", FS::Counter::AiMovedPages, false},
				    {"ai_help_n", FS::Counter::AiHelpN, false},
				    {"ai_help_ns", FS::Counter::AiHelpNs, false},
				    {"ai_kept_n", FS::Counter::AiKeptN, false},
				    {"ai_kept_ns", FS::Counter::AiKeptNs, false},
				    {"ai_kept_nowin_n", FS::Counter::AiKeptNowinN, false},
				    {"ai_kept_nowin_ns", FS::Counter::AiKeptNowinNs, false},
				    {"ai_kept_nomap_n", FS::Counter::AiKeptNomapN, false},
				    {"ai_kept_nomap_ns", FS::Counter::AiKeptNomapNs, false},
				    {"ai_nowork", FS::Counter::AiNowork, false},
				    {"ai_job_wait_ns", FS::Counter::AiJobWaitNs, false},
				    {"ai_chk", FS::Counter::AiChk, false},
				    {"ai_bad", FS::Counter::AiBad, false},
				    {"ai_jleft", FS::Counter::AiJleft, false},
				    {"ai_jstale", FS::Counter::AiJstale, false},
				    {"ai_cmp_pages", FS::Counter::AiCmpPages, false},
				    {"ai_cbad", FS::Counter::AiCbad, false},
				    // Session 130, ac_cbad attribution (cbad130.md rev 2 s.5.1): raw, live at 2/3/4 only.
				    {"ac_cbad_m", FS::Counter::AcCbadM, false},
				    {"ac_cbad_e", FS::Counter::AcCbadE, false},
				    {"ac_cbm_nosnap", FS::Counter::AcCbmNosnap, false},
				    {"ac_cbm_bad", FS::Counter::AcCbmBad, false},
				    {"ac_cbm_left", FS::Counter::AcCbmLeft, false},
				    {"ac_cbm_stale", FS::Counter::AcCbmStale, false},
				    {"ac_cbm_remark", FS::Counter::AcCbmRemark, false},
				    {"ac_cbm_new", FS::Counter::AcCbmNew, false},
				    {"ac_cbm_pend", FS::Counter::AcCbmPend, false},
				    {"ac_cbm_host", FS::Counter::AcCbmHost, false},
				    {"ac_cbe_ro", FS::Counter::AcCbeRo, false},
				    {"ac_cbe_na", FS::Counter::AcCbeNa, false},
				    {"ac_cbe_oth", FS::Counter::AcCbeOth, false},
				    {"ac_cls_n", FS::Counter::AcClsN, false},
				    {"ac_cls_ns", FS::Counter::AcClsNs, false},
				    {"ac_cls_wait_ns", FS::Counter::AcClsWaitNs, false},
				    {"ac_cls_vq", FS::Counter::AcClsVq, false},
				    {"ac_cbm_host_d", FS::Counter::AcCbmHostD, false},
				    // Session 131, knob "lwin" (lw131.md rev 1 s.7.1 with ROADMAP s122 item 126(b), (g)): raw pages / counts / ns.
				    {"lw_p8", FS::Counter::LwP8, false},
				    {"lw_x", FS::Counter::LwX, false},
				    {"lw_open", FS::Counter::LwOpen, false},
				    {"lw_xnc", FS::Counter::LwXnc, false},
				    {"lw_p8sync", FS::Counter::LwP8sync, false},
				    {"lw_xmk", FS::Counter::LwXmk, false},
				    {"lw_c3x", FS::Counter::LwC3x, false},
				    {"lw_c3p", FS::Counter::LwC3p, false},
				    {"lw_crx", FS::Counter::LwCrx, false},
				    {"lw_crp", FS::Counter::LwCrp, false},
				    {"lw_cdx", FS::Counter::LwCdx, false},
				    {"lw_cdp", FS::Counter::LwCdp, false},
				    {"lw_late", FS::Counter::LwLate, false},
				    {"lw_poll_n", FS::Counter::LwPollN, false},
				    {"lw_poll_ns", FS::Counter::LwPollNs, false},
				    {"lw_stamp_n", FS::Counter::LwStampN, false},
				    {"lw_stamp_pages", FS::Counter::LwStampPages, false},
				    {"lw_mark_pages", FS::Counter::LwMarkPages, false},
				    {"lw_sync_pages", FS::Counter::LwSyncPages, false},
				    {"lw_spin_n", FS::Counter::LwSpinN, false},
				    {"lw_spin_ns", FS::Counter::LwSpinNs, false},
				    {"lw_ovf", FS::Counter::LwOvf, false},
				    // Session 131, knob "dispceil" (dd131.md rev 1 s.7 with ROADMAP s122 items 124(g), 125(b), (v)): raw ns / counts.
				    {"dc_n", FS::Counter::DcN, false},
				    {"dc_dose_n", FS::Counter::DcDoseN, false},
				    {"dc_offthr", FS::Counter::DcOffthr, false},
				    {"dc_dose_ns", FS::Counter::DcDoseNs, false},
				    {"dc_tgt_ns", FS::Counter::DcTgtNs, false},
				    {"dc_refuse", FS::Counter::DcRefuse, false},
				    {"dc_early_n", FS::Counter::DcEarlyN, false},
				    {"dc_bda_n", FS::Counter::DcBdaN, false},
				    {"dc_ind_n", FS::Counter::DcIndN, false},
				    {"dc_prot_n", FS::Counter::DcProtN, false},
				    {"dc_ph_pro_ns", FS::Counter::DcPhProNs, false},
				    {"dc_ph_prog_ns", FS::Counter::DcPhProgNs, false},
				    {"dc_ph_pre_ns", FS::Counter::DcPhPreNs, false},
				    {"dc_ph_pipe_ns", FS::Counter::DcPhPipeNs, false},
				    {"dc_ph_prep_ns", FS::Counter::DcPhPrepNs, false},
				    {"dc_ph_bda_ns", FS::Counter::DcPhBdaNs, false},
				    {"dc_ph_img_ns", FS::Counter::DcPhImgNs, false},
				    {"dc_ph_buf_ns", FS::Counter::DcPhBufNs, false},
				    {"dc_ph_ind_ns", FS::Counter::DcPhIndNs, false},
				    {"dc_ph_com_ns", FS::Counter::DcPhComNs, false},
				    {"dc_ph_emit_ns", FS::Counter::DcPhEmitNs, false},
				    {"dc_ph_tail_ns", FS::Counter::DcPhTailNs, false},
				    {"dc_ph_early_ns", FS::Counter::DcPhEarlyNs, false},
				    {"dc_prot_ns", FS::Counter::DcProtNs, false},
				    // Session 133, knob "rbcen" (design133.md rev 2 s.6): raw ns / counts; rb_b2_kb is bytes / 1000 like
				    // ob_stream_kb (B8).
				    {"rb_refuse", FS::Counter::RbRefuse, false},
				    {"rb_head_ns", FS::Counter::RbHeadNs, false},
				    {"rb_stage_ns", FS::Counter::RbStageNs, false},
				    {"rb_find_ns", FS::Counter::RbFindNs, false},
				    {"rb_find_n", FS::Counter::RbFindN, false},
				    {"rb_bda_ns", FS::Counter::RbBdaNs, false},
				    {"rb_bda_n", FS::Counter::RbBdaN, false},
				    {"rb_bda_scan_n", FS::Counter::RbBdaScanN, false},
				    {"rb_rt_ns", FS::Counter::RbRtNs, false},
				    {"rb_tail_ns", FS::Counter::RbTailNs, false},
				    {"rb_xprep_ns", FS::Counter::RbXprepNs, false},
				    {"rb_ximg_ns", FS::Counter::RbXimgNs, false},
				    {"rb_xbuf_ns", FS::Counter::RbXbufNs, false},
				    {"rb_stream_ns", FS::Counter::RbStreamNs, false},
				    {"rb_stream_n", FS::Counter::RbStreamN, false},
				    {"rb_cbank_ns", FS::Counter::RbCbankNs, false},
				    {"rb_cbank_n", FS::Counter::RbCbankN, false},
				    {"rb_epoch_ns", FS::Counter::RbEpochNs, false},
				    {"rb_epoch_n", FS::Counter::RbEpochN, false},
				    {"rb_slow_ns", FS::Counter::RbSlowNs, false},
				    {"rb_slow_n", FS::Counter::RbSlowN, false},
				    {"rb_samp_n", FS::Counter::RbSampN, false},
				    {"rb_cal_ns", FS::Counter::RbCalNs, false},
				    {"rb_cal_n", FS::Counter::RbCalN, false},
				    {"rb_bpro_ns", FS::Counter::RbBproNs, false},
				    {"rb_nupload_ns", FS::Counter::RbNuploadNs, false},
				    {"rb_sync_up_ns", FS::Counter::RbSyncUpNs, false},
				    {"rb_sync_wait_ns", FS::Counter::RbSyncWaitNs, false},
				    {"rb_cls_bad", FS::Counter::RbClsBad, false},
				    {"rb_b2_n", FS::Counter::RbB2N, false},
				    {"rb_b2_would", FS::Counter::RbB2Would, false},
				    {"rb_b2_kb", FS::Counter::RbB2Kb, true},
				    {"rb_b2_chk", FS::Counter::RbB2Chk, false},
				    {"rb_b2_diff", FS::Counter::RbB2Diff, false},
				    {"rb_b2_xchk", FS::Counter::RbB2Xchk, false},
				    {"rb_b2_xdiff", FS::Counter::RbB2Xdiff, false},
				    {"rb_b2_evict", FS::Counter::RbB2Evict, false},
				    {"rb_b2_shovf", FS::Counter::RbB2Shovf, false},
				    {"rb_b2_rst_sub", FS::Counter::RbB2RstSub, false},
				    {"rb_b2_rst_host", FS::Counter::RbB2RstHost, false},
				    {"rb_b2_rst_wait", FS::Counter::RbB2RstWait, false},
				    {"rb_b2_rst_rel", FS::Counter::RbB2RstRel, false},
				    {"rb_b2_rst_wr", FS::Counter::RbB2RstWr, false},
				    {"rb_b2_rst_cond", FS::Counter::RbB2RstCond, false},
				    {"rb_b2_rst_emu", FS::Counter::RbB2RstEmu, false},
				    {"rb_b2_rst_gpuw", FS::Counter::RbB2RstGpuw, false},
				    {"rb_b2_rst_imgw", FS::Counter::RbB2RstImgw, false},
				    {"rb_b2_rst_ring", FS::Counter::RbB2RstRing, false},
				    // Session 134, knob "b2reuse" (design134.md rev 1 s.8.1, ROADMAP s122 items 151(d)(1), 153(v), 154(b)).
				    {"b2r_n", FS::Counter::B2rN, false},
				    {"b2r_hit", FS::Counter::B2rHit, false},
				    {"b2r_chk", FS::Counter::B2rChk, false},
				    {"b2r_bad", FS::Counter::B2rBad, false},
				    {"b2r_path", FS::Counter::B2rPath, false},
				    {"b2r_hit_draw", FS::Counter::B2rHitDraw, false},
				    {"b2r_hit_x", FS::Counter::B2rHitX, false},
				    {"b2r_miss_new", FS::Counter::B2rMissNew, false},
				    {"b2r_miss_gen", FS::Counter::B2rMissGen, false},
				    {"b2r_miss_evict", FS::Counter::B2rMissEvict, false},
				    {"b2r_miss_kind", FS::Counter::B2rMissKind, false},
				    {"b2r_refuse", FS::Counter::B2rRefuse, false},
				    {"b2r_rst_cpu", FS::Counter::B2rRstCpu, false},
				    {"b2r_rst_cpuw", FS::Counter::B2rRstCpuw, false},
				    {"b2r_wrapcur", FS::Counter::B2rWrapcur, false},
				    {"b2r_nomap", FS::Counter::B2rNomap, false}, // ROADMAP s122 item 158(b)(3), CR1
				    // Session 135, knob "rbslow" (design135.md rev 2 s.15 item 4, ROADMAP s122 items 166(b), 167(v), 168(b)).
				    {"rs_find_ns", FS::Counter::RsFindNs, false},
				    {"rs_find_n", FS::Counter::RsFindN, false},
				    {"rs_touch_ns", FS::Counter::RsTouchNs, false},
				    {"rs_sync_ns", FS::Counter::RsSyncNs, false},
				    {"rs_wr_ns", FS::Counter::RsWrNs, false},
				    {"rs_wr_n", FS::Counter::RsWrN, false},
				    {"rs_rem_ns", FS::Counter::RsRemNs, false},
				    {"rs_sync_n", FS::Counter::RsSyncN, false},
				    {"rs_sync_noop_n", FS::Counter::RsSyncNoopN, false},
				    {"rs_sync_kb", FS::Counter::RsSyncKb, true},
				    {"rs_ro_n", FS::Counter::RsRoN, false},
				    {"rs_bf_n", FS::Counter::RsBfN, false},
				    {"rs_bf_would", FS::Counter::RsBfWould, false},
				    {"rs_bf_diff", FS::Counter::RsBfDiff, false},
				    {"rs_bfw_ns", FS::Counter::RsBfwNs, false},
				    {"rs_refuse", FS::Counter::RsRefuse, false},
				    {"rs_head_ns", FS::Counter::RsHeadNs, false},
				    {"rs_tail_ns", FS::Counter::RsTailNs, false},
				    {"rs_cen_ns", FS::Counter::RsCenNs, false},
				    {"rs_bf_xchk", FS::Counter::RsBfXchk, false},
				    {"rs_bf_xdiff", FS::Counter::RsBfXdiff, false},
				    {"rs_bf_strm", FS::Counter::RsBfStrm, false},
				    {"rs_disc_n", FS::Counter::RsDiscN, false},
				    {"rs_bfw_k", FS::Counter::RsBfwK, false},
				    {"rs_bf_race", FS::Counter::RsBfRace, false},
				    // Session 136, knob "bindlean" (design136.md rev 1 s.9.1, item 178(g)): pieces, micros=false.
				    {"bln_n", FS::Counter::BlnN, false},
				    {"bln_hit", FS::Counter::BlnHit, false},
				    {"bln_miss_new", FS::Counter::BlnMissNew, false},
				    {"bln_miss_gen", FS::Counter::BlnMissGen, false},
				    {"bln_miss_evict", FS::Counter::BlnMissEvict, false},
				    {"bln_miss_kind", FS::Counter::BlnMissKind, false},
				    {"bln_chk", FS::Counter::BlnChk, false},
				    {"bln_bad", FS::Counter::BlnBad, false},
				    {"bln_path", FS::Counter::BlnPath, false},
				    {"bln_nomap", FS::Counter::BlnNomap, false},
				    {"bln_pchk", FS::Counter::BlnPchk, false},
				    {"bln_pbad", FS::Counter::BlnPbad, false},
				    {"bln_skip", FS::Counter::BlnSkip, false},
				    {"bln_skip_a", FS::Counter::BlnSkipA, false},
				    {"bln_skip_b", FS::Counter::BlnSkipB, false},
				    {"bln_sbad", FS::Counter::BlnSbad, false},
				    {"bln_srace", FS::Counter::BlnSrace, false},
				    {"bln_sctl", FS::Counter::BlnSctl, false},
				    {"bln_refuse", FS::Counter::BlnRefuse, false},
				    {"bln_rst_cpu", FS::Counter::BlnRstCpu, false},
				    {"bln_rst_cpuw", FS::Counter::BlnRstCpuw, false},
				    {"bln_srace_a", FS::Counter::BlnSraceA, false},
				    {"pvar_w", FS::Counter::PvarW, false},
				    {"pvar_k", FS::Counter::PvarK, false},
				    {"pvar_kraw", FS::Counter::PvarKraw, false},
				    {"pvar_lost", FS::Counter::PvarLost, false},
				    {"pvar_over", FS::Counter::PvarOver, false},
				    {"pvar_chg", FS::Counter::PvarChg, false},
				    {"pvar_inupd", FS::Counter::PvarInupd, false},
				    {"pvar_tear", FS::Counter::PvarTear, false},
				    {"pvar_tail", FS::Counter::PvarTail, false},
				    {"pvar_foreign", FS::Counter::PvarForeign, false},
				    {"pvar_bad", FS::Counter::PvarBad, false},
				};
				std::string text;
				for (const auto& counter: named) {
					text += ' ';
					text += counter.name;
					text += '=';
					text += std::to_string(counter.micros ? dus(counter.counter) : d(counter.counter));
				}
				// Session 128, knob "protceil" (item 89(zh)): the live U bits at the end of the line, a running total.
				text += " pc_u_live=";
				text += std::to_string(static_cast<unsigned long long>(cur.c[static_cast<size_t>(FS::Counter::PcULive)]));
				LOGF("FrameTrace-x: n=%" PRIu64 "%s" "\n", r.cfg->flip_status.count, text.c_str());
				// Session 130, ac_cbad attribution (cbad130.md rev 2 s.5.4, C9): the address histogram every 300 flips while the
				// running ac_cbad (read above - no new read) is not 0.
				if (cur.c[static_cast<size_t>(FS::Counter::AcCbad)] != 0 && r.cfg->flip_status.count % 300 == 0) {
					FS::AcHistLog(r.cfg->flip_status.count);
				}
			}
			for (uint32_t table = 0; table < static_cast<uint32_t>(FS::Table::Count); table++) {
				static std::array<std::array<FS::SiteRow, 160>, static_cast<size_t>(FS::Table::Count)>
				    prev_sites {};
				std::array<FS::SiteRow, 160> rows {};
				const auto                  n = FS::ReadSites(static_cast<FS::Table>(table), rows.data(), rows.size());
				static constexpr std::array<const char*, static_cast<size_t>(FS::Table::Count)>
				            table_names {"FrameTrace-wait:", "FrameTrace-submit:", "FrameTrace-pm4:",
				                         "FrameTrace-pops:", "FrameTrace-direct:"};
				std::string line = table_names[table];
				if (n == 0) {
					continue;
				}
				for (size_t i = 0; i < n; i++) {
					auto& p = prev_sites[table][i];
					if (p.name != rows[i].name) {
						p = {rows[i].name, 0, 0};
					}
					const auto dn = rows[i].ns - p.ns;
					const auto dc = rows[i].count - p.count;
					if (dc != 0) {
						line += " " + std::string(rows[i].name) + "=" + std::to_string(dn / 1000u) + "/" +
						        std::to_string(dc);
					}
					p = rows[i];
				}
				LOGF("%s" "\n", line.c_str());
			}
		}
		prev = cur;
	}
	if (r.source == FlipRequestSource::GpuEop && r.cfg->flip_status.gcQueueNum > 0) {
		r.cfg->flip_status.gcQueueNum--;
	}
	TriggerVideoOutEvents(*r.cfg, VideoOutEventKind::Flip, reinterpret_cast<void*>(r.flip_arg));

	m_processing = false;
	m_done_cond_var.SignalAll();
	m_submit_slot_cond_var.Signal();
	m_mutex.Unlock();
	{
		const uint64_t hold_ns = Common::FrameStats::NowNs() - hold_t0;
		Common::FrameStats::Add(Common::FrameStats::Counter::FlipHoldNs, hold_ns);
		Common::FrameStats::Add(Common::FrameStats::Counter::FlipHoldN, 1);
		if (hold_ns >= 50000000ull) {
			static std::atomic<uint32_t> hold_logged {0};
			if (hold_logged.fetch_add(1, std::memory_order_relaxed) < 32) {
				const uint64_t named = present_ns + poll_ns;
				LOGF("FlipHold: us=%llu present_us=%llu poll_us=%llu other_us=%llu flip=%llu\n",
				     static_cast<unsigned long long>(hold_ns / 1000), static_cast<unsigned long long>(present_ns / 1000),
				     static_cast<unsigned long long>(poll_ns / 1000),
				     static_cast<unsigned long long>((hold_ns > named ? hold_ns - named : 0) / 1000),
				     static_cast<unsigned long long>(r.cfg->flip_status.count));
			}
		}
	}
	r.cfg->mutex.Unlock();

	Graphics::RenderDocOnGuestFlip(m_presenter.Renderer());

	if (Config::GraphicsDebugDumpEnabled() &&
	    Config::GetPrintfDirection() != Config::LogDirection::Silent) {
		LOGF("Flip done: %d\n", r.index);
	}

	return true;
}

void FlipQueue::GetFlipStatus(VideoOutConfig& cfg, VideoOutFlipStatus& out) {
	Common::LockGuard lock(cfg.mutex);

	out = cfg.flip_status;
}

KYTY_SYSV_ABI int VideoOutOpen(int user_id, int bus_type, int index, const void* param) {
	PRINT_NAME();

	EXIT_NOT_IMPLEMENTED(user_id != 255 && user_id != 0);
	LOGF("\t param = 0x%016" PRIx64 "\n", reinterpret_cast<uint64_t>(param));

	return DriverState().Open(bus_type, index);
}

KYTY_SYSV_ABI int VideoOutClose(int handle) {
	PRINT_NAME();

	return DriverState().Close(handle) ? OK : VIDEO_OUT_ERROR_INVALID_HANDLE;
}

KYTY_SYSV_ABI void VideoOutSetBufferAttribute2(VideoOutBufferAttribute2* attribute,
                                               uint64_t pixel_format, uint32_t tiling_mode,
                                               uint32_t width, uint32_t height, uint64_t option,
                                               uint32_t dcc_control,
                                               uint64_t dcc_cb_register_clear_color) {
	PRINT_NAME();

	EXIT_NOT_IMPLEMENTED(attribute == nullptr);

	LOGF("\t pixel_format                = %016" PRIx64 "\n"
	     "\t tiling_mode                 = %" PRIu32 "\n"
	     "\t width                       = %" PRIu32 "\n"
	     "\t height                      = %" PRIu32 "\n"
	     "\t option                      = %016" PRIx64 "\n"
	     "\t dcc_control                 = %08" PRIx32 "\n"
	     "\t dcc_cb_register_clear_color = %016" PRIx64 "\n",
	     pixel_format, tiling_mode, width, height, option, dcc_control,
	     dcc_cb_register_clear_color);

	memset(attribute, 0, sizeof(VideoOutBufferAttribute2));

	attribute->tiling_mode                 = tiling_mode;
	attribute->aspect_ratio                = 0;
	attribute->width                       = width;
	attribute->height                      = height;
	attribute->pitch_in_pixel              = 0;
	attribute->option                      = option;
	attribute->pixel_format                = pixel_format;
	attribute->dcc_cb_register_clear_color = dcc_cb_register_clear_color;
	attribute->dcc_control                 = dcc_control;
}

KYTY_SYSV_ABI int VideoOutSetFlipRate(int handle, int rate) {
	PRINT_NAME();

	LOGF("\trate = %d\n", rate);

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	if (rate < 0 || rate > 2) {
		return VIDEO_OUT_ERROR_INVALID_VALUE;
	}

	Common::LockGuard lock(ctx->mutex);
	ctx->flip_rate = rate;
	// Session 123 (ROADMAP s122 item 29(b)): the flip interval of the game, unconditionally, at most 16 lines.
	static std::atomic<uint32_t> rate_logged {0};
	if (rate_logged.fetch_add(1, std::memory_order_relaxed) < 16) {
		LOGF("VideoOutFlipRate: rate=%d\n", rate);
	}

	return OK;
}

KYTY_SYSV_ABI int VideoOutDeleteFlipEvent(EventQueue::KernelEqueue eq, int handle) {
	PRINT_NAME();
	return DeleteVideoOutEvent(handle, eq, VideoOutEventKind::Flip);
}

KYTY_SYSV_ABI int VideoOutAddFlipEvent(EventQueue::KernelEqueue eq, int handle, void* udata) {
	PRINT_NAME();
	return RegisterVideoOutEvent(handle, eq, VideoOutEventKind::Flip, udata);
}

KYTY_SYSV_ABI int VideoOutDeleteVblankEvent(EventQueue::KernelEqueue eq, int handle) {
	PRINT_NAME();
	return DeleteVideoOutEvent(handle, eq, VideoOutEventKind::Vblank);
}

KYTY_SYSV_ABI int VideoOutDeletePreVblankStartEvent(EventQueue::KernelEqueue eq, int handle) {
	PRINT_NAME();
	return DeleteVideoOutEvent(handle, eq, VideoOutEventKind::PreVblankStart);
}

KYTY_SYSV_ABI int VideoOutAddVblankEvent(LibKernel::EventQueue::KernelEqueue eq, int handle,
                                         void* udata) {
	PRINT_NAME();
	return RegisterVideoOutEvent(handle, eq, VideoOutEventKind::Vblank, udata);
}

KYTY_SYSV_ABI int VideoOutAddPreVblankStartEvent(LibKernel::EventQueue::KernelEqueue eq, int handle,
                                                 void* udata) {
	PRINT_NAME();
	return RegisterVideoOutEvent(handle, eq, VideoOutEventKind::PreVblankStart, udata);
}

KYTY_SYSV_ABI int VideoOutAddOutputModeEvent(LibKernel::EventQueue::KernelEqueue eq, int handle,
                                             void* udata) {
	PRINT_NAME();
	return RegisterVideoOutEvent(handle, eq, VideoOutEventKind::OutputMode, udata);
}

KYTY_SYSV_ABI int VideoOutRegisterBuffers2(int handle, int set_index, int buffer_index_start,
                                           const VideoOutBuffers* buffers, int buffer_num,
                                           const VideoOutBufferAttribute2* attribute, int category,
                                           void* option) {
	PRINT_NAME();

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	if (buffers == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	if (attribute == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_OPTION;
	}

	if (set_index < 0 || set_index >= VIDEO_OUT_BUFFER_ATTRIBUTE_NUM_MAX ||
	    buffer_index_start < 0 || buffer_index_start >= VIDEO_OUT_BUFFER_NUM_MAX ||
	    buffer_num < 1 || buffer_num > VIDEO_OUT_BUFFER_NUM_MAX ||
	    buffer_index_start + buffer_num > VIDEO_OUT_BUFFER_NUM_MAX) {
		return VIDEO_OUT_ERROR_INVALID_VALUE;
	}

	LOGF("\t start_index    = %d\n"
	     "\t buffer_num     = %d\n"
	     "\t set_index      = %d\n"
	     "\t pixel_format   = 0x%016" PRIx64 "\n"
	     "\t tiling_mode    = %" PRIu32 "\n"
	     "\t aspect_ratio   = %" PRIu32 "\n"
	     "\t width          = %" PRIu32 "\n"
	     "\t height         = %" PRIu32 "\n"
	     "\t pitch_in_pixel = %" PRIu32 "\n"
	     "\t option         = %" PRIu64 "\n"
	     "\t category       = %d\n",
	     buffer_index_start, buffer_num, set_index, attribute->pixel_format, attribute->tiling_mode,
	     attribute->aspect_ratio, attribute->width, attribute->height, attribute->pitch_in_pixel,
	     attribute->option, category);

	if (option != nullptr) {
		return VIDEO_OUT_ERROR_INVALID_OPTION;
	}
	if (category != VIDEO_OUT_BUFFER_ATTRIBUTE_CATEGORY_UNCOMPRESSED &&
	    category != VIDEO_OUT_BUFFER_ATTRIBUTE_CATEGORY_COMPRESSED) {
		return VIDEO_OUT_ERROR_INVALID_CATEGORY;
	}

	BufferAttributeGroup group {
	    .attribute = *attribute,
	    .category  = category,
	    .occupied  = true,
	};
	std::vector<VideoOutBuffer> registrations;
	registrations.reserve(static_cast<size_t>(buffer_num));

	for (int i = 0; i < buffer_num; i++) {
		LOGF("\t buffers[%d]: data=%p metadata=%p\n", i, buffers[i].data, buffers[i].metadata);
		if (buffers[i].reserved[0] != nullptr || buffers[i].reserved[1] != nullptr) {
			LOGF("\t buffers[%d]: ignoring reserved fields {%p, %p}\n", i, buffers[i].reserved[0],
			     buffers[i].reserved[1]);
		}
		const auto data_address     = reinterpret_cast<uint64_t>(buffers[i].data);
		const auto metadata_address = reinterpret_cast<uint64_t>(buffers[i].metadata);
		registrations.push_back({
		    .group_index      = set_index,
		    .data_address     = data_address,
		    .metadata_address = metadata_address,
		});
		(void)group.ImageInfo(registrations.back());
	}

	Common::LockGuard lock(ctx->mutex);
	if (ctx->closing) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}
	if (ctx->groups[set_index].occupied) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}
	for (int i = 0; i < buffer_num; i++) {
		if (ctx->buffers[buffer_index_start + i].Occupied()) {
			return VIDEO_OUT_ERROR_SLOT_OCCUPIED;
		}
	}

	ctx->groups[set_index] = group;
	for (int i = 0; i < buffer_num; i++) {
		ctx->buffers[buffer_index_start + i] = registrations[static_cast<size_t>(i)];
		const auto& buffer                   = registrations[static_cast<size_t>(i)];
		LOGF("\tbuffers[%d] = %016" PRIx64 " metadata = %016" PRIx64 " dcc = %08" PRIx32 "\n",
		     buffer_index_start + i, buffer.data_address, buffer.metadata_address,
		     attribute->dcc_control);
	}

	return OK;
}

KYTY_SYSV_ABI int VideoOutSubmitChangeBufferAttribute2(int handle, int set_index,
                                                       const VideoOutBufferAttribute2* attribute,
                                                       void*                           option) {
	PRINT_NAME();

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	if (attribute == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_OPTION;
	}
	if (set_index < 0 || set_index >= VIDEO_OUT_BUFFER_ATTRIBUTE_NUM_MAX) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}

	if (option != nullptr) {
		return VIDEO_OUT_ERROR_INVALID_OPTION;
	}

	Common::LockGuard lock(ctx->mutex);
	const auto&       current = ctx->groups[set_index];
	if (ctx->closing || !current.occupied) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}

	BufferAttributeGroup replacement {
	    .attribute = *attribute,
	    .category  = current.category,
	    .occupied  = true,
	};
	for (const auto& buffer: ctx->buffers) {
		if (buffer.group_index == set_index) {
			(void)replacement.ImageInfo(buffer);
		}
	}
	ctx->groups[set_index] = replacement;

	return OK;
}

KYTY_SYSV_ABI int VideoOutUnregisterBuffers(int handle, int set_index) {
	PRINT_NAME();

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}
	if (set_index < 0 || set_index >= VIDEO_OUT_BUFFER_ATTRIBUTE_NUM_MAX) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}

	Common::LockGuard lock(ctx->mutex);
	if (ctx->closing) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}
	if (!ctx->groups[set_index].occupied) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}
	ctx->groups[set_index] = BufferAttributeGroup {};
	for (auto& buffer: ctx->buffers) {
		if (buffer.group_index == set_index) {
			buffer = VideoOutBuffer {};
		}
	}

	return OK;
}

KYTY_SYSV_ABI int VideoOutSubmitFlip(int handle, int index, int flip_mode, int64_t flip_arg) {
	PRINT_NAME();

	uint64_t  request_id = 0;
	const int result     = ReserveFlipRequest(DriverState(), handle, index, flip_mode, flip_arg,
	                                          FlipRequestSource::Cpu, request_id);
	if (result == VIDEO_OUT_ERROR_INVALID_VALUE) {
		LOGF("\t unsupported flip_mode = %d\n", flip_mode);
	}
	if (result != OK) {
		return result;
	}
	g_video_out_driver->SubmitFlipPreparation(request_id);

	return OK;
}

int VideoOutDriver::SubmitFlipFromGpu(Graphics::CommandBuffer& buffer, int handle, int index,
                                      int flip_mode, int64_t flip_arg, uint64_t& request_id) {
	EXIT_IF(buffer.IsInvalid());

	const int result = ReserveFlipRequest(*m_impl, handle, index, flip_mode, flip_arg,
	                                      FlipRequestSource::GpuEop, request_id);
	if (result != OK) {
		return result;
	}
	m_impl->GetFlipQueue().Prepare(request_id, buffer);

	return OK;
}

void VideoOutDriver::SubmitFlipPreparation(uint64_t request_id) {
	m_impl->Renderer().GetGpu().SubmitFlipPreparation(request_id);
}

void VideoOutDriver::PrepareFlip(uint64_t request_id, Graphics::CommandBuffer& buffer) {
	m_impl->GetFlipQueue().Prepare(request_id, buffer);
}

void VideoOutDriver::CompleteFlip(uint64_t request_id) {
	m_impl->GetFlipQueue().Complete(request_id);
}

void VideoOutDriver::WaitForSubmitSlot() {
	m_impl->GetFlipQueue().WaitForSubmitSlot();
}

void VideoOutDriver::MarkFlipIncomplete(uint64_t request_id) {
	m_impl->GetFlipQueue().MarkIncomplete(request_id);
}

bool VideoOutDriver::MarkFlipSkipCeil(uint64_t request_id) {
	return m_impl->GetFlipQueue().MarkSkipCeil(request_id);
}

void VideoOutDriver::WaitFlipDone(int handle, int index) {
	auto* ctx = m_impl->Get(handle);
	EXIT_IF(ctx == nullptr);

	EXIT_NOT_IMPLEMENTED(!IsValidBufferIndex(index));
	// Session 106, KYTY_GPU_WALL=1: R_WAIT_FLIP_DONE on the GuestGpu thread (gw_flip).
	Common::FrameStats::WallSpan wall(
	    Common::FrameStats::CurrentRole() == Common::FrameStats::ThreadRole::Gpu,
	    Common::FrameStats::Counter::GpuWallFlipNs, Common::FrameStats::Counter::GpuWallFlipN);
	m_impl->GetFlipQueue().Wait(*ctx, index);
}

KYTY_SYSV_ABI int VideoOutGetFlipStatus(int handle, VideoOutFlipStatus* status) {
	PRINT_NAME();

	if (status == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	DriverState().GetFlipQueue().GetFlipStatus(*ctx, *status);

	LOGF("\t count = %" PRIu64 "\n"
	     "\t processTime = %" PRIu64 "\n"
	     "\t processTimeCounter = %" PRIu64 "\n"
	     "\t submitProcessTimeCounter = %" PRIu64 "\n"
	     "\t flipArg = %" PRId64 "\n"
	     "\t gcQueueNum = %d\n"
	     "\t flipPendingNum = %d\n"
	     "\t currentBuffer = %d\n",
	     status->count, status->processTime, status->processTimeCounter,
	     status->submitProcessTimeCounter, status->flipArg, status->gcQueueNum,
	     status->flipPendingNum, status->currentBuffer);

	return OK;
}

KYTY_SYSV_ABI int VideoOutIsFlipPending(int handle) {
	PRINT_NAME();

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	VideoOutFlipStatus status {};
	DriverState().GetFlipQueue().GetFlipStatus(*ctx, status);

	LOGF("\t flipPendingNum = %d\n", status.flipPendingNum);

	return status.flipPendingNum;
}

KYTY_SYSV_ABI int VideoOutGetVblankStatus(int handle, VideoOutVblankStatus* status) {
	PRINT_NAME();

	if (status == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	ctx->mutex.Lock();
	*status = ctx->vblank_status;
	ctx->mutex.Unlock();

	LOGF("\t count = %" PRIu64 "\n"
	     "\t processTime = %" PRIu64 "\n"
	     "\t processTimeCounter = %" PRIu64 "\n",
	     status->count, status->processTime, status->processTimeCounter);

	return OK;
}

KYTY_SYSV_ABI int VideoOutGetEventId(const EventQueue::KernelEvent* ev) {
	PRINT_NAME();

	if (ev == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	if (ev->filter != EventQueue::KERNEL_EVFILT_VIDEO_OUT) {
		return VIDEO_OUT_ERROR_INVALID_EVENT;
	}

	switch (ev->ident) {
		case VIDEO_OUT_EVENT_FLIP:
		case VIDEO_OUT_EVENT_VBLANK:
		case VIDEO_OUT_EVENT_PRE_VBLANK_START:
		case VIDEO_OUT_EVENT_SET_MODE: return static_cast<int>(ev->ident);
		default: return VIDEO_OUT_ERROR_INVALID_EVENT;
	}
}

KYTY_SYSV_ABI int VideoOutGetEventData(const EventQueue::KernelEvent* ev, int64_t* data) {
	PRINT_NAME();

	if (ev == nullptr || data == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	if (ev->filter != EventQueue::KERNEL_EVFILT_VIDEO_OUT) {
		return VIDEO_OUT_ERROR_INVALID_EVENT;
	}

	uint64_t event_data = static_cast<uint64_t>(ev->data) >> 16u;
	if (ev->ident == VIDEO_OUT_EVENT_FLIP &&
	    (static_cast<uint64_t>(ev->data) & 0x8000000000000000ULL) != 0) {
		event_data |= 0xffff000000000000ULL;
	}

	*data = static_cast<int64_t>(event_data);

	return OK;
}

KYTY_SYSV_ABI int VideoOutGetEventCount(const EventQueue::KernelEvent* ev) {
	PRINT_NAME();

	if (ev == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	if (ev->filter != EventQueue::KERNEL_EVFILT_VIDEO_OUT) {
		return VIDEO_OUT_ERROR_INVALID_EVENT;
	}

	return static_cast<int>((static_cast<uint64_t>(ev->data) >> 12u) & 0xfu);
}

KYTY_SYSV_ABI int VideoOutWaitVblank(int handle) {
	PRINT_NAME();

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	Common::LockGuard lock(ctx->mutex);
	const auto        count = ctx->vblank_status.count;
	// Track F, F20j3 (KYTY_DIAG_B32 W:vblank, item 574(a)(4)): the guest waits for the next vblank (VblankEnd of the
	// present thread signals) - a wait the guest asked for (GUEST_SLEEP kind group, item 574(d)).
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && ctx->opened) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::Vblank, ctx, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);
	}
	while (ctx->opened && ctx->vblank_status.count == count) {
		ctx->vblank_cond.Wait(&ctx->mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(ctx->vblank_cond.B32Waker(b32.SinceNs()), false);
	}

	return OK;
}

KYTY_SYSV_ABI int VideoOutGetOutputStatus(int handle, VideoOutOutputStatus* status) {
	PRINT_NAME();

	if (status == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	ctx->mutex.Lock();
	status->resolution   = (ctx->width >= 3840 || ctx->height >= 2160 ? 2u : 1u);
	status->dynamicRange = 1;
	status->refreshRate =
	    (ctx->output_mode == VIDEO_OUT_OUTPUT_MODE_119_88HZ || Config::GetVblankFrequency() >= 119
	         ? VIDEO_OUT_REFRESH_RATE_119_88HZ
	         : VIDEO_OUT_REFRESH_RATE_59_94HZ);
	status->flags       = 0;
	status->reserved[0] = 0;
	status->reserved[1] = 0;
	status->reserved[2] = 0;
	ctx->mutex.Unlock();

	return OK;
}

static int ValidateOutputConfig(int handle, uint64_t mode, const VideoOutOutputOptions* options,
                                void* reserved_ptr, uint64_t reserved) {
	if (!DriverState().IsOpened(handle)) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	if (reserved_ptr != nullptr || reserved != 0) {
		return VIDEO_OUT_ERROR_INVALID_VALUE;
	}

	if (options != nullptr) {
		for (auto v: options->internalData) {
			if (v != 0) {
				return VIDEO_OUT_ERROR_INVALID_OPTION;
			}
		}
	}

	if (mode != VIDEO_OUT_OUTPUT_MODE_DEFAULT && mode != VIDEO_OUT_OUTPUT_MODE_119_88HZ) {
		return VIDEO_OUT_ERROR_UNSUPPORTED_OUTPUT_MODE;
	}

	return OK;
}

KYTY_SYSV_ABI int VideoOutInitializeOutputOptions(VideoOutOutputOptions* options) {
	PRINT_NAME();

	if (options == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	memset(options, 0, sizeof(VideoOutOutputOptions));

	return OK;
}

KYTY_SYSV_ABI int VideoOutIsOutputSupported(int handle, uint64_t mode,
                                            const VideoOutOutputOptions* options,
                                            void* reserved_ptr, uint64_t reserved) {
	PRINT_NAME();

	LOGF("\t mode = 0x%016" PRIx64 "\n", mode);

	int result = ValidateOutputConfig(handle, mode, options, reserved_ptr, reserved);
	if (result != OK) {
		return result;
	}

	if (mode == VIDEO_OUT_OUTPUT_MODE_119_88HZ) {
		return (Config::GetVblankFrequency() >= 119 ? VIDEO_OUT_TRUE : VIDEO_OUT_FALSE);
	}

	return VIDEO_OUT_TRUE;
}

KYTY_SYSV_ABI int VideoOutConfigureOutput(int handle, uint64_t mode,
                                          const VideoOutOutputOptions* options, void* reserved_ptr,
                                          uint64_t reserved) {
	PRINT_NAME();

	LOGF("\t mode = 0x%016" PRIx64 "\n", mode);

	int result = VideoOutIsOutputSupported(handle, mode, options, reserved_ptr, reserved);
	if (result < 0) {
		return result;
	}
	if (result == VIDEO_OUT_FALSE) {
		return VIDEO_OUT_ERROR_UNAVAILABLE_OUTPUT_MODE;
	}

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	ctx->mutex.Lock();
	ctx->output_mode = mode;
	TriggerVideoOutEvents(*ctx, VideoOutEventKind::OutputMode,
	                      reinterpret_cast<void*>(ctx->output_mode));
	ctx->mutex.Unlock();

	return OK;
}

KYTY_SYSV_ABI int VideoOutSetWindowModeMargins(int handle, int top, int bottom) {
	PRINT_NAME();

	[[maybe_unused]] auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	LOGF("\t top    = %d\n"
	     "\t bottom = %d\n",
	     top, bottom);

	return OK;
}

KYTY_SYSV_ABI int VideoOutLatencyControlWaitBeforeInput(int handle) {
	PRINT_NAME();

	[[maybe_unused]] auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	return OK;
}

KYTY_SYSV_ABI int VideoOutLatencyMeasureSetStartPoint(int handle, uint32_t point) {
	PRINT_NAME();

	[[maybe_unused]] auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	LOGF("\t point = %" PRIu32 "\n", point);

	return OK;
}

KYTY_SYSV_ABI int VideoOutColorSettingsSetGamma(VideoOutColorSettings* settings, float gamma) {
	PRINT_NAME();

	if (settings == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	if (gamma < 0.1f || gamma > 2.0f) {
		return VIDEO_OUT_ERROR_INVALID_VALUE;
	}

	settings->gamma = gamma;
	return OK;
}

KYTY_SYSV_ABI int VideoOutAdjustColor(int handle, const VideoOutColorSettings* settings) {
	PRINT_NAME();

	if (settings == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_ADDRESS;
	}

	if (!DriverState().IsOpened(handle)) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}

	auto* ctx = DriverState().Get(handle);
	if (ctx == nullptr) {
		return VIDEO_OUT_ERROR_INVALID_HANDLE;
	}
	ctx->mutex.Lock();
	ctx->gamma = settings->gamma;
	ctx->mutex.Unlock();

	return OK;
}

} // namespace Libs::VideoOut
