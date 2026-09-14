#include "graphics/presentation/videoOut.h"

#include "common/abi.h"
#include "common/assert.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/common.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "common/stringUtils.h"
#include "common/threads.h"
#include "common/timer.h"
#include "graphics/guest_gpu/gpu_defs.h"
#include "graphics/guest_gpu/graphicsRun.h"
#include "graphics/guest_gpu/tile.h"
#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"
#include "graphics/host_gpu/renderer/image/imageInfo.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/presentation/presenter.h"
#include "graphics/presentation/renderDoc.h"
#include "kernel/pthread.h"
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
	static constexpr int VIDEO_OUT_NUM_MAX = 4;

	Impl(uint32_t width, uint32_t height, Graphics::Presenter& presenter)
	    : m_renderer(presenter.Renderer()), m_presenter(presenter), m_flip_queue(presenter) {
		EXIT_NOT_IMPLEMENTED(!Common::Thread::IsMainThread());
		Init(width, height);
		m_present_thread = std::jthread([this](std::stop_token token) { PresentThread(token); });
	}
	~Impl();
	KYTY_CLASS_NO_COPY(Impl);

	int             Open(int bus_type);
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

	Common::LockGuard lock(video_out->mutex);
	if (video_out->closing ||
	    (!IsSpecialBufferIndex(index) && !video_out->buffers[index].Occupied())) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}
	if (!driver.GetFlipQueue().Reserve(*video_out, index, flip_arg, source, request_id)) {
		return VIDEO_OUT_ERROR_FLIP_QUEUE_FULL;
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

int VideoOutDriver::Impl::Open(int bus_type) {
	Common::LockGuard lock(m_mutex);

	const int handle = bus_type + 1;
	if (m_video_out_ctx[handle].opened) {
		return -1;
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

	for (int i = 1; i < VIDEO_OUT_NUM_MAX; i++) {
		auto& ctx = m_video_out_ctx[i];
		if (ctx.opened) {
			ctx.mutex.Lock();
			ctx.vblank_status.count++;
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
			Common::Thread::SleepMicro(static_cast<uint32_t>(
			    std::clamp<uint64_t>(remaining_us, 1, std::numeric_limits<uint32_t>::max())));
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
	while (m_processing && !m_requests.empty() && m_requests.front().cfg == &cfg) {
		m_done_cond_var.Wait(&m_mutex);
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

void FlipQueue::WaitForSubmitSlot() {
	Common::LockGuard lock(m_mutex);
	while (m_requests.size() + m_cpu_requests.size() >= VIDEO_OUT_FLIP_QUEUE_CAPACITY) {
		if (m_requests.empty()) {
			EXIT("video-out queue is saturated by CPU flips queued behind the current EOP\n");
		}
		m_submit_slot_cond_var.Wait(&m_mutex);
	}
}

void FlipQueue::Wait(VideoOutConfig& cfg, int index) {
	Common::LockGuard lock(m_mutex);

	auto has_request = [this, &cfg, index] {
		auto matches = [&cfg, index](const auto& r) { return r.cfg == &cfg && r.index == index; };
		return std::any_of(m_requests.begin(), m_requests.end(), matches) ||
		       std::any_of(m_cpu_requests.begin(), m_cpu_requests.end(), matches);
	};
	while (has_request()) {
		m_done_cond_var.Wait(&m_mutex);
	}
}

bool FlipQueue::Flip(uint32_t micros) {
	KYTY_PROFILER_BLOCK("FlipQueue::Flip");

	m_mutex.Lock();
	if (m_requests.empty()) {
		m_submit_cond_var.WaitFor(&m_mutex, micros);

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
	if (r.incomplete && hold_incomplete) {
		// Keep the previously presented image on screen instead of a frame with missing draws.
		static std::atomic<uint32_t> held {0};
		if (held.fetch_add(1, std::memory_order_relaxed) < 64) {
			LOGF("AsyncPipelines: flip %" PRIu64 " held (incomplete frame)\n", r.id);
		}
		m_presenter.Discard(*r.frame);
	} else {
		m_presenter.Present(*r.frame);
	}
	Graphics::RenderDocOnGuestFlip(m_presenter.Renderer());

	m_mutex.Lock();
	if (m_requests.empty() || m_requests.front().id != r.id ||
	    m_requests.front().state != RequestState::Presenting) {
		EXIT("video-out flip queue changed while processing its front request\n");
	}
	m_requests.pop_front();

	r.cfg->flip_status.count++;
	Graphics::GpuTimeProfiler::SetFrame(static_cast<uint32_t>(r.cfg->flip_status.count));
	Common::Gates::Poll(static_cast<uint32_t>(r.cfg->flip_status.count));
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
		static const bool av_trace = std::getenv("KYTY_AV_TRACE") != nullptr;
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
			     " prios=%llu prio_us=%llu dmas=%llu dma_us=%llu" "\n",
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
			     dus(FS::Counter::PriorityWaitNs), d(FS::Counter::Dmas), dus(FS::Counter::DmaNs));
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
			     " bda_scan=%llu bda_skip=%llu bpage_hit=%llu bpage_miss=%llu"
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
				};
				std::string text;
				for (const auto& counter: named) {
					text += ' ';
					text += counter.name;
					text += '=';
					text += std::to_string(counter.micros ? dus(counter.counter) : d(counter.counter));
				}
				LOGF("FrameTrace-x: n=%" PRIu64 "%s" "\n", r.cfg->flip_status.count, text.c_str());
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
	if (bus_type != VIDEO_OUT_BUS_TYPE_MAIN && bus_type != VIDEO_OUT_BUS_TYPE_OVERLAY &&
	    bus_type != VIDEO_OUT_BUS_TYPE_SUB) {
		return VIDEO_OUT_ERROR_INVALID_VALUE;
	}
	EXIT_NOT_IMPLEMENTED(index != 0);

	LOGF("\t param = 0x%016" PRIx64 "\n", reinterpret_cast<uint64_t>(param));

	int handle = DriverState().Open(bus_type);

	if (handle < 0) {
		return VIDEO_OUT_ERROR_RESOURCE_BUSY;
	}

	return handle;
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

void VideoOutDriver::WaitFlipDone(int handle, int index) {
	auto* ctx = m_impl->Get(handle);
	EXIT_IF(ctx == nullptr);

	EXIT_NOT_IMPLEMENTED(!IsValidBufferIndex(index));
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
	while (ctx->opened && ctx->vblank_status.count == count) {
		ctx->vblank_cond.Wait(&ctx->mutex);
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
