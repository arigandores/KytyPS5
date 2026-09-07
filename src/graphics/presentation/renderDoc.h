#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_RENDERDOC_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_RENDERDOC_H_

namespace Libs::Graphics {

void RenderDocInit();
void RenderDocRequestCapture();
// The game's log text passes through here (libc fwrite): "Level has started: <KYTY_RD_LEVEL>"
// arms the level-relative trigger KYTY_RD_LEVEL_FRAME (see DebugAutoRenderDocCapture).
void RenderDocNoteGuestText(const char* text, size_t size);
bool RenderDocLevelStarted();
void RenderDocStartCapture();
void RenderDocEndCapture();
void RenderDocOnGuestFlip();

[[nodiscard]] bool RenderDocCaptureRequested();
[[nodiscard]] bool RenderDocCaptureInProgress();

} // namespace Libs::Graphics

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_RENDERDOC_H_ */
