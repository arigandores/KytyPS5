#ifndef EMULATOR_SRC_GRAPHICS_PRESENTATION_SYSTEMOVERLAY_H_
#define EMULATOR_SRC_GRAPHICS_PRESENTATION_SYSTEMOVERLAY_H_

#include "common/common.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <memory>

union SDL_Event;

namespace Libs::Graphics {

struct GraphicContext;

struct SystemOverlayVisualState {
	bool     active;
	uint64_t revision;
};

void                     InitializeSystemOverlayInput();
void                     ShutdownSystemOverlayInput();
bool                     ProcessSystemOverlayInput(const SDL_Event& event);
SystemOverlayVisualState GetSystemOverlayVisualState() noexcept;

// Startup-only screen, set and rendered on the main thread before guest execution.
void SetShaderPreparationOverlay(bool active, uint32_t completed = 0, uint32_t total = 0);
bool ShaderPreparationOverlayActive() noexcept;

class SystemOverlay final {
public:
	explicit SystemOverlay(GraphicContext& graphics);
	~SystemOverlay();
	KYTY_CLASS_NO_COPY(SystemOverlay);

	[[nodiscard]] bool PrepareFrame(vk::Extent2D extent, vk::Format format, uint32_t image_count);
	void               Record(vk::CommandBuffer command, vk::ImageView target);
	void               ReleaseVulkan();

private:
	struct Impl;
	std::unique_ptr<Impl> m_impl;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_PRESENTATION_SYSTEMOVERLAY_H_
