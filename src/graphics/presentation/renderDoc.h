#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_RENDERDOC_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_RENDERDOC_H_

namespace Libs::Graphics {

class RenderContext;

void RenderDocInit();
void RenderDocRequestCapture();
// The game's log text passes through here (libc fwrite): "Level has started: <KYTY_RD_LEVEL>"
// arms the level-relative trigger KYTY_RD_LEVEL_FRAME (see DebugAutoRenderDocCapture).
void RenderDocNoteGuestText(const char* text, size_t size);
bool RenderDocLevelStarted();
// Called by the presentation thread after releasing video-out locks.
void RenderDocOnGuestFlip(RenderContext& renderer);
// Called for every guest draw/dispatch: a capture only counts flips between which the GuestGpu
// thread actually submitted work (the game keeps 2-3 flips queued; draining them back to back
// produced captures with nothing but the flip blits).
void RenderDocNoteGpuWork();

} // namespace Libs::Graphics

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_RENDERDOC_H_ */
