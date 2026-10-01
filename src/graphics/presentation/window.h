#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_WINDOW_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_WINDOW_H_

#include "common/abi.h"
#include "common/common.h"

namespace Libs::Graphics {

class Presenter;

[[nodiscard]] Presenter& WindowInit(uint32_t width, uint32_t height);
void                     WindowRun();
// Pumps window events while preparing known pipelines; false if the user closes the window.
[[nodiscard]] bool       WindowPrepareShaders();
void                     WindowShutdown();
// Track F, F5 (ROADMAP s122 item 273(e)(2), MEASUREMENT ONLY): the stand KYTY_TEST_MINIMIZE - fed the game's log text.
void                     WindowTestMinimizeNoteGuestText(const char* text, size_t size);

} // namespace Libs::Graphics

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_WINDOW_H_ */
