#ifndef EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_SCREENSHOT_H_
#define EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_SCREENSHOT_H_

#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/cache/streamBuffer.h"

#include <memory>
#include <string>

namespace Libs::Graphics {

class CommandBuffer;
class CommandScheduler;

// Screenshot of the presented frame taken inside the emulator, independent of the window state
// (minimized, covered). Requests: a file "_screenshot.req" in the working directory (its first
// line, if any, is the output path; default "_shot_<present>.png"; the file is deleted), or
// KYTY_SHOT_TIMES=<s>[,<s>...] seconds since the first present. The frame image is copied to a
// host buffer with the present commands, the present is waited for, and the pixels are written
// as PNG (downscaled by an integer factor to at most 1920 wide).
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
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_SCREENSHOT_H_
