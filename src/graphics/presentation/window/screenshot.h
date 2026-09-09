#ifndef EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_SCREENSHOT_H_
#define EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_SCREENSHOT_H_

#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/cache/streamBuffer.h"

#include <array>
#include <condition_variable>
#include <deque>
#include <mutex>
#include <thread>
#include <cstdio>
#include <memory>
#include <string>
#include <vector>

namespace Libs::Graphics {

class CommandBuffer;
class CommandScheduler;

// Screenshot of the presented frame taken inside the emulator, independent of the window state
// (minimized, covered). Requests: a file "_screenshot.req" in the working directory (its first
// line, if any, is the output path; default "_shot_<present>.png"; the file is deleted), or
// KYTY_SHOT_TIMES=<s>[,<s>...] seconds since the first present. The frame image is copied to a
// host buffer with the present commands, the present is waited for, and the pixels are written
// as PNG (downscaled by an integer factor to at most 1920 wide).
// Recording: KYTY_REC=<file.mp4> writes every presented frame (960 wide, integer downscale) to an
// ffmpeg process (rawvideo pipe, 60 fps nominal: one video frame per present, independent of the
// wall clock) and <file.mp4>.idx lines "<video frame> <present> <host seconds>". A ring of three
// download buffers keeps the present thread from waiting for the GPU.
class ScreenshotGrabber final {
public:
	ScreenshotGrabber(GraphicContext& graphics, CommandScheduler& scheduler);
	~ScreenshotGrabber();
	KYTY_CLASS_NO_COPY(ScreenshotGrabber);

	// Called once per present: true when this frame should be captured.
	bool Poll();
	// Records the image -> buffer copy (the image must be in TransferSrcOptimal).
	void Record(CommandBuffer& command, const VulkanImage& source);
	// Waits for the submission `tick`, converts and writes the file.
	void Finish(uint64_t tick);

private:
	GraphicContext&         m_graphics;
	CommandScheduler&       m_scheduler;
	std::unique_ptr<Buffer> m_buffer;
	std::string             m_output;
	vk::Format              m_format = vk::Format::eUndefined;
	uint32_t                m_width  = 0;
	uint32_t                m_height = 0;
	uint32_t                m_presents = 0;
	uint32_t                m_shots    = 0;
	double                  m_first_present_s = -1.0;
	std::vector<double>     m_times;
	size_t                  m_next_time = 0;
	bool                    m_pending   = false;
	// Recording state.
	struct RecSlot {
		std::unique_ptr<Buffer> buffer;
		uint64_t                tick    = 0;
		uint32_t                present = 0;
		double                  time_s  = 0.0;
		bool                    pending = false;
		// Geometry of the copy recorded into this slot: the presented image changes size and
		// format between the logo video, menus and the game, and the slot is flushed up to two
		// presents later.
		vk::Format              format  = vk::Format::eUndefined;
		uint32_t                width   = 0;
		uint32_t                height  = 0;
	};
	std::string           m_rec_path;
	FILE*                 m_rec_pipe = nullptr;
	FILE*                 m_rec_index = nullptr;
	std::array<RecSlot, 3> m_rec_slots {};
	uint32_t              m_rec_next    = 0;
	uint32_t              m_rec_flush_next = 0; // oldest slot not yet written to the video
	uint32_t              m_rec_frames  = 0;
	std::vector<uint8_t>  m_rec_rgb;
	bool                  m_rec_frame = false; // this present records a video frame
	// Encoder thread: FlushVideoSlot hands it the raw texels; it converts to RGB and feeds ffmpeg,
	// so the GuestGpu thread pays a memcpy per frame instead of the 2-3 ms conversion.
	struct RecJob {
		std::vector<uint8_t> raw;
		vk::Format           format  = vk::Format::eUndefined;
		uint32_t             width   = 0;
		uint32_t             height  = 0;
		uint32_t             present = 0;
		double               time_s  = 0.0;
	};
	std::mutex              m_rec_mutex;
	std::condition_variable m_rec_cv;
	std::deque<RecJob>      m_rec_queue;
	std::vector<std::vector<uint8_t>> m_rec_free; // recycled raw buffers
	std::thread             m_rec_thread;
	bool                    m_rec_stop = false;
	void EncodeVideoFrame(RecJob& job);
	void RecorderThread();
	bool PollScreenshot();
	void RecordVideoFrame(CommandBuffer& command, const VulkanImage& source);
	void FinishVideoFrame(uint64_t tick);
	void FlushVideoSlot(RecSlot& slot);
	void FlushPendingVideoSlots(bool wait_oldest);
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_SCREENSHOT_H_
