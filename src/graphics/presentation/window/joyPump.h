#ifndef KYTY_GRAPHICS_PRESENTATION_WINDOW_JOY_PUMP_H_
#define KYTY_GRAPHICS_PRESENTATION_WINDOW_JOY_PUMP_H_

#include <cstdint>
#include <functional>
#include <string>

struct SDL_Window;

// Track F, F40a (HPP-770; ROADMAP s122 item 692(v)): KYTY_FIX_F24 - variant B of F39a s1 (docs/track-f/f40a.md s0).
// At 0 (default 1 since FS14a - ReadKnob below): nothing here runs except ReadKnob, Enabled (false) and Exited (true);
// the SDL init, the event wait and the
// pad open / close stay on the main thread as in FS12. At 1: SDL_HINT_AUTO_UPDATE_JOYSTICKS is 0, the main thread
// initializes only the video subsystem and waits while the JoyPump thread runs SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER)
// (every window, timer and COM apartment of the joystick drivers belongs to JoyPump), then JoyPump loops: queued tasks
// -> the messages of its own thread -> SDL_JoystickUpdate -> opening of new pads by instance id -> wait for a task, a
// message or the timeout (1 ms with an open pad, JP_IDLE_MS = 250 ms without). The main thread makes no joystick or
// game controller API call (the stand KYTY_TEST_HIDLOSS excepted).
namespace Libs::Graphics::JoyPump {

// Main thread, WindowCreate, before any SDL_InitSubSystem: reads KYTY_FIX_F24 once (track F, FS14a, HPP-812, ROADMAP s122
// item 710(g)(1): default 1 - unset or "" = ON, 0/false/off/no = OFF, any other value as EnvValueOn) and
// prints "FixF24: mode=<0|1> b24=<0|1>". Later calls do nothing.
void ReadKnob();
bool Enabled();
// =1 only: starts JoyPump and waits for its SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER); false and the SDL error text on
// failure (the caller exits as on the FS12 path).
bool Start(uint64_t main_tid, std::string* error);
// Pads opened by JoyPump and not yet closed (written by JoyPump only).
int OpenPads();
// Main thread, removal event at =1: Controller::Disconnect is done by the caller; this queues the close of the pad.
void PostClose(int instance_id);
// Main thread, add event at =1: the event is only logged ("FixF24: add event index=<i>", at most 32 lines).
void NoteAddEvent(int index);
// FIFO task of JoyPump; dropped after the stop or before the start.
void Post(std::function<void()> task);
// RC4 (docs/track-f/f40a.md s0.4): raises the stop flag, wakes JoyPump and waits at most T_JP = 2 s for its end; on
// expiry prints "FixF24: pump_stop_expired" and detaches the thread. Any thread, any number of times; a call from
// JoyPump itself only raises the flag.
void Stop();
// True when JoyPump was never started or its thread function has returned.
bool Exited();

// Stand KYTY_TEST_HIDLOSS edition 2 (window.cpp). StandWindow(true) zeroes and starts the counters, (false) stops them.
struct StandStats {
	uint64_t update_max_us = 0; // the longest SDL_JoystickUpdate of JoyPump in the window
	uint64_t tasks         = 0; // JoyPump tasks run in the window
	uint64_t open_failed   = 0; // SDL_GameControllerOpen == nullptr on JoyPump in the window
};
void       StandWindow(bool open);
StandStats StandRead();
// Flap arm: a task runs no earlier than its post time + ms (0 - off); the scan and the opening are not delayed.
void StandTaskDelayMs(uint32_t ms);
// Flap arm (F40a2, RC2 of F40b): the longest stretch of [Begin; End] without a ScanAndOpen start of JoyPump, us;
// stand thread; no-ops and 0 at KYTY_FIX_F24=0.
void     StandScanGapBegin();
uint64_t StandScanGapEnd();
// Win32 helpers of the stand probes (no-ops elsewhere): the HWND of the SDL window (main thread), a key message pair of
// VK_F13 (scan code 0x64) posted to it, IsHungAppWindow.
uintptr_t StandWindowHandle(SDL_Window* window);
bool      StandPostKey(uintptr_t hwnd, bool down);
bool      StandIsHung(uintptr_t hwnd);

} // namespace Libs::Graphics::JoyPump

#endif /* KYTY_GRAPHICS_PRESENTATION_WINDOW_JOY_PUMP_H_ */
