#include "graphics/presentation/window.h"

#include "SDL.h"
#include "SDL_error.h"
#include "SDL_events.h"
#include "SDL_filesystem.h"
#include "SDL_gamecontroller.h"
#include "SDL_hints.h"
#include "SDL_joystick.h"
#include "SDL_keyboard.h"
#include "SDL_keycode.h"
#include "SDL_mouse.h"
#include "SDL_pixels.h"
#include "SDL_rwops.h"
#include "SDL_stdinc.h"
#include "SDL_surface.h"
#include "SDL_thread.h"
#include "SDL_touch.h"
#include "SDL_video.h"
#include "SDL_vulkan.h"
#include "common/diagB32.h"
#include "common/assert.h"
#include "common/common.h"
#include "common/emulatorConfig.h"
#include "common/envFlag.h"
#include "common/file.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "common/systemInfo.h"
#include "common/threads.h"
#include "common/timer.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "graphics/presentation/renderDoc.h"
#include "graphics/presentation/presenter.h"
#include "graphics/presentation/systemOverlay.h"
#include "graphics/presentation/window/hostInput.h"
#include "graphics/presentation/window/joyPump.h"
#include "graphics/presentation/window/testMinimizeLine.h"
#include "graphics/presentation/window/windowInternal.h"
#include "kytyGitVersion.h"
#include "libs/controller.h"
#include "loader/systemContent.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <cmath>
#include <cstring>
#include <thread>
#include <utility>
#include <fmt/format.h>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <vulkan/vk_platform.h>

#define STB_IMAGE_IMPLEMENTATION
#define STBI_NO_SIMD
#include "stb_image.h"

// IWYU pragma: no_include <intrin.h>

#define KYTY_ENABLE_DEBUG_PRINTF
// Input event logging is opt-in through the KYTY_DBG_INPUT build definition.

namespace Libs::Graphics {

struct EventKeyboard {
	bool     down;
	bool     up;
	bool     pressed;
	bool     released;
	bool     repeat;
	int      scan_code;
	int      key_code;
	uint16_t mod;
	double   timestamp_seconds;
};

static uint32_t ControllerButtonToPadButton(int button) {
	switch (button) {
		case SDL_CONTROLLER_BUTTON_A: return Controller::PAD_BUTTON_CROSS;
		case SDL_CONTROLLER_BUTTON_B: return Controller::PAD_BUTTON_CIRCLE;
		case SDL_CONTROLLER_BUTTON_X: return Controller::PAD_BUTTON_SQUARE;
		case SDL_CONTROLLER_BUTTON_Y: return Controller::PAD_BUTTON_TRIANGLE;
		case SDL_CONTROLLER_BUTTON_START: return Controller::PAD_BUTTON_OPTIONS;
		case SDL_CONTROLLER_BUTTON_LEFTSTICK: return Controller::PAD_BUTTON_L3;
		case SDL_CONTROLLER_BUTTON_RIGHTSTICK: return Controller::PAD_BUTTON_R3;
		case SDL_CONTROLLER_BUTTON_LEFTSHOULDER: return Controller::PAD_BUTTON_L1;
		case SDL_CONTROLLER_BUTTON_RIGHTSHOULDER: return Controller::PAD_BUTTON_R1;
		case SDL_CONTROLLER_BUTTON_DPAD_UP: return Controller::PAD_BUTTON_UP;
		case SDL_CONTROLLER_BUTTON_DPAD_DOWN: return Controller::PAD_BUTTON_DOWN;
		case SDL_CONTROLLER_BUTTON_DPAD_LEFT: return Controller::PAD_BUTTON_LEFT;
		case SDL_CONTROLLER_BUTTON_DPAD_RIGHT: return Controller::PAD_BUTTON_RIGHT;
		case SDL_CONTROLLER_BUTTON_TOUCHPAD: return Controller::PAD_BUTTON_TOUCH_PAD;
		default: return 0;
	}
}

static Controller::Axis ControllerAxisFromSdl(int axis_id) {
	switch (axis_id) {
		case SDL_CONTROLLER_AXIS_LEFTX: return Controller::Axis::LeftX;
		case SDL_CONTROLLER_AXIS_LEFTY: return Controller::Axis::LeftY;
		case SDL_CONTROLLER_AXIS_RIGHTX: return Controller::Axis::RightX;
		case SDL_CONTROLLER_AXIS_RIGHTY: return Controller::Axis::RightY;
		case SDL_CONTROLLER_AXIS_TRIGGERLEFT: return Controller::Axis::TriggerLeft;
		case SDL_CONTROLLER_AXIS_TRIGGERRIGHT: return Controller::Axis::TriggerRight;
		default: return Controller::Axis::AxisMax;
	}
}

static bool ControllerAxisIsTrigger(int axis_id) {
	return axis_id == SDL_CONTROLLER_AXIS_TRIGGERLEFT ||
	       axis_id == SDL_CONTROLLER_AXIS_TRIGGERRIGHT;
}

static int ControllerAxisValueFromSdl(int axis_id, int axis_value) {
	return ControllerAxisIsTrigger(axis_id)
	           ? Controller::controller_get_axis(0, SDL_JOYSTICK_AXIS_MAX, axis_value)
	           : Controller::controller_get_axis(SDL_JOYSTICK_AXIS_MIN, SDL_JOYSTICK_AXIS_MAX,
	                                             axis_value);
}

struct EventMouse {
	bool   down;
	bool   up;
	bool   left;
	bool   middle;
	bool   right;
	bool   x1;
	bool   x2;
	bool   touch;
	bool   pressed;
	bool   released;
	int    num_of_clicks;
	bool   wheel;
	int    x;
	int    y;
	bool   motion;
	int    motion_x;
	int    motion_y;
	double timestamp_seconds;
};

struct EventFinger {
	bool   down;
	bool   up;
	bool   motion;
	int    touch_id;
	int    finger_id;
	float  x;
	float  y;
	float  dx;
	float  dy;
	float  pressure;
	double timestamp_seconds;
};

struct EventController {
	int    id;
	int    button;
	int    axis_id;
	int    axis_value;
	bool   down;
	bool   up;
	bool   added;
	bool   removed;
	bool   remapped;
	bool   axis;
	bool   pressed;
	bool   released;
	double timestamp_seconds;
};

enum class DisplayOrientation {
	Unknown,   /* The display orientation can't be determined */
	Landscape, /* The display is in landscape mode, with the right side up, relative to portrait
	              mode */
	LandscapeFlipped, /* The display is in landscape mode, with the left side up, relative to
	                     portrait mode */
	Portrait,         /* The display is in portrait mode */
	PortraitFlipped,  /* The display is in portrait mode, upside down */

	DisplayEventOrientation = 0xF0
};

struct EventDisplay {
	DisplayOrientation orientation;
};

constexpr uint32_t KYTY_SDL_BUTTON_LMASK  = SDL_BUTTON_LMASK;  // NOLINT(hicpp-signed-bitwise)
constexpr uint32_t KYTY_SDL_BUTTON_MMASK  = SDL_BUTTON_MMASK;  // NOLINT(hicpp-signed-bitwise)
constexpr uint32_t KYTY_SDL_BUTTON_RMASK  = SDL_BUTTON_RMASK;  // NOLINT(hicpp-signed-bitwise)
constexpr uint32_t KYTY_SDL_BUTTON_X1MASK = SDL_BUTTON_X1MASK; // NOLINT(hicpp-signed-bitwise)
constexpr uint32_t KYTY_SDL_BUTTON_X2MASK = SDL_BUTTON_X2MASK; // NOLINT(hicpp-signed-bitwise)

namespace {

std::unique_ptr<WindowContext> g_window;

} // namespace

constexpr const char* KYTY_SDL_WINDOW_CAPTION = "Game";
constexpr int KYTY_SDL_WINDOWPOS_CENTERED = SDL_WINDOWPOS_CENTERED; /*NOLINT(hicpp-signed-bitwise)*/

static void SetPause(WindowLoopState& game, bool flag) {
	LOGF("Pause: %s\n", flag ? "true" : "false");

	game.paused.store(flag, std::memory_order_release);
}

static void GameEventQuit(WindowLoopState& game) {
	LOGF("Event: quit\n");

	game.need_exit = true;
}

static void GameEventTerminate(WindowLoopState& game) {
	LOGF("Event: terminate\n");

	game.need_exit = true;
}

static void ToggleDesktopFullscreen() {
	if (g_window == nullptr || g_window->window == nullptr) {
		return;
	}

	const auto flags = static_cast<uint32_t>(SDL_GetWindowFlags(g_window->window));
	const bool fullscreen =
	    (flags & static_cast<uint32_t>(SDL_WINDOW_FULLSCREEN_DESKTOP)) != 0u;
	const auto mode =
	    fullscreen ? 0u : static_cast<uint32_t>(SDL_WINDOW_FULLSCREEN_DESKTOP);
	if (SDL_SetWindowFullscreen(g_window->window, mode) != 0) {
		LOGF("Toggle fullscreen failed: %s\n", SDL_GetError());
	}
}

static void GameEventKeyboard(WindowLoopState& game, const EventKeyboard& key) {
	static SDL_Keycode fullscreen_key = SDLK_UNKNOWN;

#ifdef KYTY_DBG_INPUT
	LOGF("Key: time = %.04f, %s%s, %s%s, %s, scan = %d, key = %d, mod = %04" PRIx16 "\n",
	     key.timestamp_seconds, (key.down ? "down" : ""), (key.up ? "up" : ""),
	     (key.pressed ? "pressed" : ""), (key.released ? "released" : ""),
	     (key.repeat ? "repeat" : ""), key.scan_code, key.key_code, key.mod);
#endif

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS || KYTY_PLATFORM == KYTY_PLATFORM_LINUX
	if (key.down) {
		switch (key.key_code) {
			case SDLK_SPACE: SetPause(game, !game.paused.load(std::memory_order_acquire)); break;
			case SDLK_F1:
				if (!key.repeat) {
					RenderDocRequestCapture();
				}
				break;
			case SDLK_F11:
				if (!key.repeat) {
					ToggleDesktopFullscreen();
				}
				break;
			case SDLK_RETURN:
			case SDLK_KP_ENTER:
				if (!key.repeat && (key.mod & KMOD_ALT) != 0) {
					ToggleDesktopFullscreen();
					fullscreen_key = key.key_code;
				}
				break;
			default: break;
		}
	}

#endif

	const bool fullscreen_key_event =
	    fullscreen_key != SDLK_UNKNOWN && key.key_code == fullscreen_key;
	if (fullscreen_key_event && key.up) {
		fullscreen_key = SDLK_UNKNOWN;
	}
	if ((key.down || key.up) && !key.repeat && !fullscreen_key_event) {
		HostInputKey(key.key_code, key.down);
	}
}

static void GameEventMouse([[maybe_unused]] const EventMouse& mb) {
#ifdef KYTY_DBG_INPUT
	if (mb.wheel) {
		LOGF("Mouse wheel: time = %.04f, %s[%d, %d]\n", mb.timestamp_seconds,
		     (mb.touch ? "touch, " : ""), mb.x, mb.y);
	} else if (mb.motion) {
		LOGF("Mouse motion: time = %.04f, %s%s%s%s%s%s, [%d, %d], (%d, %d)\n", mb.timestamp_seconds,
		     (mb.left ? "left" : ""), (mb.middle ? "middle" : ""), (mb.right ? "right" : ""),
		     (mb.x1 ? "x1" : ""), (mb.x2 ? "x2" : ""), (mb.touch ? "_touch" : ""), mb.x, mb.y,
		     mb.motion_x, mb.motion_y);
	} else {
		LOGF("Mouse click: time = %.04f, %d, %s%s%s%s%s%s, %s%s, %s%s, [%d, %d]\n",
		     mb.timestamp_seconds, mb.num_of_clicks, (mb.left ? "left" : ""),
		     (mb.middle ? "middle" : ""), (mb.right ? "right" : ""), (mb.x1 ? "x1" : ""),
		     (mb.x2 ? "x2" : ""), (mb.touch ? "_touch" : ""), (mb.down ? "down" : ""),
		     (mb.up ? "up" : ""), (mb.pressed ? "pressed" : ""), (mb.released ? "released" : ""),
		     mb.x, mb.y);
	}
#endif

	if (mb.down || mb.up) {
		uint8_t mouse_button = 0;
		if (mb.left) {
			mouse_button = SDL_BUTTON_LEFT;
		} else if (mb.middle) {
			mouse_button = SDL_BUTTON_MIDDLE;
		} else if (mb.right) {
			mouse_button = SDL_BUTTON_RIGHT;
		} else if (mb.x1) {
			mouse_button = SDL_BUTTON_X1;
		} else if (mb.x2) {
			mouse_button = SDL_BUTTON_X2;
		}

		HostInputMouseButton(mouse_button, mb.down);
	}
}

static void GameEventFinger([[maybe_unused]] const EventFinger& f) {
#ifdef KYTY_DBG_INPUT
	if (f.motion) {
		LOGF("Finger motion: time = %.04f, %d, %d, (x,y) = [%f, %f], (dx,dy) = [%f, %f], pressure "
		     "= %f\n",
		     f.timestamp_seconds, f.touch_id, f.finger_id, f.x, f.y, f.dx, f.dy, f.pressure);
	} else {
		LOGF("Finger press: time = %.04f, %d, %d, %s%s, (x,y) = [%f, %f], (dx,dy) = [%f, %f], "
		     "pressure = %f\n",
		     f.timestamp_seconds, f.touch_id, f.finger_id, (f.down ? "down" : ""),
		     (f.up ? "up" : ""), f.x, f.y, f.dx, f.dy, f.pressure);
	}
#endif
}

// Track F, F19c stand KYTY_TEST_HIDLOSS (ROADMAP s122 item 451(c), F19a s6.1): counters of the stand window - main
// thread probes, removal events, callbacks of the virtual pad. Counted only while window is set (from fire - 1 s to the
// stat line); the stand itself is next to WindowTestMinimizeNoteGuestText.
struct TestHidLossCounters {
	std::atomic<bool>     window {false};
	std::atomic<uint64_t> main_late_max_us {0};
	std::atomic<uint64_t> probes_posted {0};
	std::atomic<uint64_t> probes_run {0};
	std::atomic<uint64_t> removed {0};
	std::atomic<uint64_t> vp_rumble {0};
	std::atomic<uint64_t> vp_led {0};
	std::atomic<uint64_t> vp_effect {0};
};

static TestHidLossCounters g_test_hidloss;

static void TestHidLossCount(std::atomic<uint64_t>& counter) {
	if (g_test_hidloss.window.load(std::memory_order_relaxed)) {
		counter.fetch_add(1, std::memory_order_relaxed);
	}
}

// Track F, F40a stand KYTY_TEST_HIDLOSS edition 2: the keyboard and pad probes, seen first by ProcessEvent (defined
// with the stand, after WindowShutdown).
static bool TestHidLossIntercept(const SDL_Event& event);

static void GameEventController([[maybe_unused]] const EventController& f) {
	EXIT_NOT_IMPLEMENTED(f.remapped);

#ifdef KYTY_DBG_INPUT
	if (f.added || f.removed) {
		LOGF("Controller %s: %d, time = %.04f\n", (f.added ? "added" : "removed"), f.id,
		     f.timestamp_seconds);
	} else if (f.axis) {
		LOGF("Controller axis: %d, axis = %d, value = %d, time = %.04f\n", f.id, f.axis_id,
		     f.axis_value, f.timestamp_seconds);
	} else {
		LOGF("Controller button: "
		     "%d, %s%s, %s%s, button = %d, time = %.04f\n",
		     f.id, (f.down ? "down" : ""), (f.up ? "up" : ""), (f.pressed ? "pressed" : ""),
		     (f.released ? "released" : ""), f.button, f.timestamp_seconds);
	}
#endif

	if (f.added && JoyPump::Enabled()) {
		// Track F, F40a (KYTY_FIX_F24=1, RC2): JoyPump opens new pads by instance id after its own SDL_JoystickUpdate
		// (docs/track-f/f40a.md s0.4); the add event of the main thread is only logged.
		JoyPump::NoteAddEvent(f.id);
	} else if (f.added) {
		auto* pad = SDL_GameControllerOpen(f.id);
		EXIT_NOT_IMPLEMENTED(pad == nullptr);
		int id = SDL_JoystickInstanceID(SDL_GameControllerGetJoystick(pad));
		for (const auto sensor: {SDL_SENSOR_ACCEL, SDL_SENSOR_GYRO}) {
			if (SDL_GameControllerHasSensor(pad, sensor) == SDL_TRUE &&
			    SDL_GameControllerSetSensorEnabled(pad, sensor, SDL_TRUE) != 0) {
				LOGF("Controller %d: sensor %d enable failed: %s\n", id, static_cast<int>(sensor),
				     SDL_GetError());
			}
		}
		LOGF("Controller %d: \"%s\" type=%d accel=%d gyro=%d path=%s\n", id,
		     SDL_GameControllerName(pad), static_cast<int>(SDL_GameControllerGetType(pad)),
		     SDL_GameControllerIsSensorEnabled(pad, SDL_SENSOR_ACCEL) == SDL_TRUE ? 1 : 0,
		     SDL_GameControllerIsSensorEnabled(pad, SDL_SENSOR_GYRO) == SDL_TRUE ? 1 : 0,
		     SDL_GameControllerPath(pad) != nullptr ? SDL_GameControllerPath(pad) : "");
		Controller::Connect(id);
	}

	if (f.removed) {
		// Track F, F19c (ROADMAP s122 item 451(c)): printed always - without it a pad lost on the host leaves no line in
		// the log (the print above is a build option); one line on a rare event, nothing the guest sees.
		LOGF("Controller %d: removed\n", f.id);
		TestHidLossCount(g_test_hidloss.removed);
		Controller::Disconnect(f.id);
		if (JoyPump::Enabled()) {
			JoyPump::PostClose(f.id); // Track F, F40a: the close is a JoyPump task (s0.4)
		} else {
			SDL_GameControllerClose(SDL_GameControllerFromInstanceID(f.id));
		}
	}

	if (f.down || f.up) {
		const auto button = ControllerButtonToPadButton(f.button);
		if (button != 0) {
			Controller::SetButton(f.id, button, f.down);
		}
	}

	if (f.axis) {
		const auto axis = ControllerAxisFromSdl(f.axis_id);
		if (axis != Controller::Axis::AxisMax) {
			Controller::SetAxis(f.id, axis,
			                    ControllerAxisValueFromSdl(f.axis_id, f.axis_value));
		}
	}
}

static void GameEventLowMemory() {
	LOGF("Event: low_memory\n");
}

static void GameEventWillEnterBackground(WindowLoopState& game) {
	LOGF("Event: will_enter_background\n");

	SetPause(game, true);
}

static void GameEventDidEnterBackground() {
	LOGF("Event: did_enter_background\n");
}

static void GameEventWillEnterForeground() {
	LOGF("Event: will_enter_foreground\n");
}

static void GameEventDidEnterForeground(WindowLoopState& game) {
	LOGF("Event: did_enter_foreground\n");

	SetPause(game, false);
}

void WindowContext::Resize(uint32_t new_width, uint32_t new_height) {
	EXIT_IF(new_width == 0 || new_height == 0);
	Common::LockGuard lock(mutex);
	graphic_ctx.screen_width  = new_width;
	graphic_ctx.screen_height = new_height;
}

void WindowContext::ProcessWindowEvent(const SDL_WindowEvent& event) {
	const auto& window_event = event;
	switch (window_event.event) {
		case SDL_WINDOWEVENT_SHOWN:
			LOGF("Window %" PRIu32 " shown\n", window_event.windowID);
			break;

		case SDL_WINDOWEVENT_HIDDEN:
			LOGF("Window %" PRIu32 " hidden\n", window_event.windowID);
			break;

		case SDL_WINDOWEVENT_EXPOSED:
			LOGF("Window %" PRIu32 " exposed\n", window_event.windowID);
			break;

		case SDL_WINDOWEVENT_MOVED:
			LOGF("Window %" PRIu32 " moved to %" PRId32 ",%" PRId32 "\n", window_event.windowID,
			     window_event.data1, window_event.data2);
			break;

		case SDL_WINDOWEVENT_RESIZED:
			LOGF("Window %" PRIu32 " resized to %" PRId32 "x%" PRId32 "\n", window_event.windowID,
			     window_event.data1, window_event.data2);

			LOGF("m: %d\n", static_cast<int>(SDL_ThreadID()));
			Resize(window_event.data1, window_event.data2);

			break;

		case SDL_WINDOWEVENT_SIZE_CHANGED:
			LOGF("Window %" PRIu32 " size changed to %" PRId32 "x%" PRId32 "\n",
			     window_event.windowID, window_event.data1, window_event.data2);

			LOGF("m: %d\n", static_cast<int>(SDL_ThreadID()));
			Resize(window_event.data1, window_event.data2);

			break;

		case SDL_WINDOWEVENT_MINIMIZED:
			LOGF("Window %" PRIu32 " minimized\n", window_event.windowID);
			break;
		case SDL_WINDOWEVENT_MAXIMIZED:
			LOGF("Window %" PRIu32 " maximized\n", window_event.windowID);
			break;
		case SDL_WINDOWEVENT_RESTORED:
			LOGF("Window %" PRIu32 " restored\n", window_event.windowID);
			break;
		case SDL_WINDOWEVENT_ENTER:
			LOGF("Mouse entered window %" PRIu32 "\n", window_event.windowID);
			break;
		case SDL_WINDOWEVENT_LEAVE:
			LOGF("Mouse left window %" PRIu32 "\n", window_event.windowID);
			break;
		case SDL_WINDOWEVENT_FOCUS_GAINED:
			LOGF("Window %" PRIu32 " gained keyboard focus\n", window_event.windowID);
			break;
		case SDL_WINDOWEVENT_FOCUS_LOST:
			LOGF("Window %" PRIu32 " lost keyboard focus\n", window_event.windowID);
			break;
		case SDL_WINDOWEVENT_CLOSE:
			LOGF("Window %" PRIu32 " closed\n", window_event.windowID);
			break;
		default:
			LOGF("Window %" PRIu32 " got unknown event %" PRIu8 "\n", window_event.windowID,
			     window_event.event);
			break;
	}
}

void WindowContext::ProcessDisplayEvent(const SDL_DisplayEvent& display) {
	bool sdl = false;

	switch (display.event) {
		case SDL_DISPLAYEVENT_ORIENTATION: sdl = true; [[fallthrough]];
		case static_cast<Uint8>(DisplayOrientation::DisplayEventOrientation): {
			LOGF("Display %" PRIu32 "[%s] changed orientation to %d - ", display.display,
			     sdl ? "SDL" : "Kyty", static_cast<int>(display.data1));

			switch (display.data1) {
				case SDL_ORIENTATION_UNKNOWN: LOGF("UNKNOWN\n"); break;
				case SDL_ORIENTATION_LANDSCAPE: LOGF("LANDSCAPE\n"); break;
				case SDL_ORIENTATION_LANDSCAPE_FLIPPED: LOGF("LANDSCAPE_FLIPPED\n"); break;
				case SDL_ORIENTATION_PORTRAIT: LOGF("PORTRAIT\n"); break;
				case SDL_ORIENTATION_PORTRAIT_FLIPPED: LOGF("PORTRAIT_FLIPPED\n"); break;
				default: LOGF("???\n");
			}

			break;
		}
		default:
			LOGF("Display %" PRIu32 " got unknown event 0x%" PRIx8 "\n", display.display,
			     display.event);
			break;
	}
}

void WindowContext::ProcessEvent(double time_s) {
	auto& game  = loop;
	auto* event = &game.event;
	EXIT_IF(SDL_GetEventState(SDL_DISPLAYEVENT) != SDL_ENABLE);
	if (TestHidLossIntercept(*event)) [[unlikely]] { // Track F, F40a stand edition 2 probes (one relaxed load when off)
		return;
	}
	if ((event->type == SDL_KEYDOWN || event->type == SDL_KEYUP) &&
	    event->key.keysym.sym == SDLK_F7) {
		if (event->type == SDL_KEYDOWN && event->key.repeat == 0) {
			HostInputToggleMouseToJoystick();
		}
		return;
	}
	if (ProcessSystemOverlayInput(*event)) {
		return;
	}

	switch (event->type) {
		case SDL_QUIT: GameEventQuit(game); break;

		case SDL_APP_TERMINATING: GameEventTerminate(game); break;

		case SDL_APP_LOWMEMORY: GameEventLowMemory(); break;

		case SDL_APP_WILLENTERBACKGROUND: GameEventWillEnterBackground(game); break;

		case SDL_APP_DIDENTERBACKGROUND: GameEventDidEnterBackground(); break;

		case SDL_APP_WILLENTERFOREGROUND: GameEventWillEnterForeground(); break;

		case SDL_APP_DIDENTERFOREGROUND: GameEventDidEnterForeground(game); break;

		case SDL_KEYDOWN:
		case SDL_KEYUP: {
			EventKeyboard key {};

			key.down              = (event->type == SDL_KEYDOWN);
			key.up                = (event->type == SDL_KEYUP);
			key.pressed           = (event->key.state == SDL_PRESSED);
			key.released          = (event->key.state == SDL_RELEASED);
			key.repeat            = (event->key.repeat != 0u);
			key.scan_code         = event->key.keysym.scancode;
			key.key_code          = event->key.keysym.sym;
			key.mod               = event->key.keysym.mod;
			key.timestamp_seconds = time_s;

			GameEventKeyboard(game, key);

			break;
		}

		case SDL_WINDOWEVENT: ProcessWindowEvent(event->window); break;

		case SDL_DISPLAYEVENT: ProcessDisplayEvent(event->display); break;

		case SDL_MOUSEBUTTONDOWN:
		case SDL_MOUSEBUTTONUP: {
			EventMouse mb {};

			mb.down              = (event->button.type == SDL_MOUSEBUTTONDOWN);
			mb.up                = (event->button.type == SDL_MOUSEBUTTONUP);
			mb.left              = (event->button.button == SDL_BUTTON_LEFT);
			mb.middle            = (event->button.button == SDL_BUTTON_MIDDLE);
			mb.right             = (event->button.button == SDL_BUTTON_RIGHT);
			mb.x1                = (event->button.button == SDL_BUTTON_X1);
			mb.x2                = (event->button.button == SDL_BUTTON_X2);
			mb.touch             = (event->button.which == SDL_TOUCH_MOUSEID);
			mb.pressed           = (event->button.state == SDL_PRESSED);
			mb.released          = (event->button.state == SDL_RELEASED);
			mb.num_of_clicks     = event->button.clicks;
			mb.wheel             = false;
			mb.x                 = event->button.x;
			mb.y                 = event->button.y;
			mb.motion            = false;
			mb.motion_x          = 0;
			mb.motion_y          = 0;
			mb.timestamp_seconds = time_s;

			GameEventMouse(mb);

			break;
		}

		case SDL_MOUSEWHEEL: {
			EventMouse mb {};

			mb.down              = false;
			mb.up                = false;
			mb.left              = false;
			mb.middle            = false;
			mb.right             = false;
			mb.x1                = false;
			mb.x2                = false;
			mb.touch             = (event->wheel.which == SDL_TOUCH_MOUSEID);
			mb.pressed           = false;
			mb.released          = false;
			mb.num_of_clicks     = 0;
			mb.wheel             = true;
			mb.x                 = event->wheel.x;
			mb.y                 = event->wheel.y;
			mb.motion            = false;
			mb.motion_x          = 0;
			mb.motion_y          = 0;
			mb.timestamp_seconds = time_s;

			GameEventMouse(mb);

			break;
		}

		case SDL_MOUSEMOTION: {
			EventMouse mb {};

			mb.down              = false;
			mb.up                = false;
			mb.left              = ((event->motion.state & KYTY_SDL_BUTTON_LMASK) != 0u);
			mb.middle            = ((event->motion.state & KYTY_SDL_BUTTON_MMASK) != 0u);
			mb.right             = ((event->motion.state & KYTY_SDL_BUTTON_RMASK) != 0u);
			mb.x1                = ((event->motion.state & KYTY_SDL_BUTTON_X1MASK) != 0u);
			mb.x2                = ((event->motion.state & KYTY_SDL_BUTTON_X2MASK) != 0u);
			mb.touch             = (event->motion.which == SDL_TOUCH_MOUSEID);
			mb.pressed           = false;
			mb.released          = false;
			mb.num_of_clicks     = 0;
			mb.wheel             = false;
			mb.x                 = event->motion.x;
			mb.y                 = event->motion.y;
			mb.motion            = true;
			mb.motion_x          = event->motion.xrel;
			mb.motion_y          = event->motion.yrel;
			mb.timestamp_seconds = time_s;

			GameEventMouse(mb);

			break;
		}

		case SDL_FINGERMOTION:
		case SDL_FINGERDOWN:
		case SDL_FINGERUP: {
			EventFinger f {};

			f.down              = (event->tfinger.type == SDL_FINGERDOWN);
			f.up                = (event->tfinger.type == SDL_FINGERUP);
			f.motion            = (event->tfinger.type == SDL_FINGERMOTION);
			f.finger_id         = static_cast<int>(event->tfinger.fingerId);
			f.touch_id          = static_cast<int>(event->tfinger.touchId);
			f.x                 = event->tfinger.x;
			f.y                 = event->tfinger.y;
			f.dx                = event->tfinger.dx;
			f.dy                = event->tfinger.dy;
			f.pressure          = event->tfinger.pressure;
			f.timestamp_seconds = time_s;

			GameEventFinger(f);

			break;
		}

		case SDL_CONTROLLERAXISMOTION: {
			EventController c {};

			c.id                = event->caxis.which;
			c.button            = SDL_CONTROLLER_BUTTON_INVALID;
			c.axis_id           = event->caxis.axis;
			c.axis_value        = event->caxis.value;
			c.down              = false;
			c.up                = false;
			c.added             = false;
			c.removed           = false;
			c.remapped          = false;
			c.axis              = true;
			c.pressed           = false;
			c.released          = false;
			c.timestamp_seconds = time_s;

			GameEventController(c);

			break;
		}

		case SDL_CONTROLLERBUTTONDOWN:
		case SDL_CONTROLLERBUTTONUP: {
			EventController c {};

			c.id                = event->cbutton.which;
			c.button            = event->cbutton.button;
			c.axis_id           = SDL_CONTROLLER_AXIS_INVALID;
			c.axis_value        = 0;
			c.down              = (event->cbutton.type == SDL_CONTROLLERBUTTONDOWN);
			c.up                = (event->cbutton.type == SDL_CONTROLLERBUTTONUP);
			c.added             = false;
			c.removed           = false;
			c.remapped          = false;
			c.axis              = false;
			c.pressed           = (event->cbutton.state == SDL_PRESSED);
			c.released          = (event->cbutton.state == SDL_RELEASED);
			c.timestamp_seconds = time_s;

			GameEventController(c);

			break;
		}

		case SDL_CONTROLLERSENSORUPDATE:
			if (event->csensor.sensor == SDL_SENSOR_ACCEL || event->csensor.sensor == SDL_SENSOR_GYRO) {
				Controller::SetMotionSensor(event->csensor.which,
				                            event->csensor.sensor == SDL_SENSOR_ACCEL
				                                ? Controller::MotionSensor::Accelerometer
				                                : Controller::MotionSensor::Gyroscope,
				                            event->csensor.data, event->csensor.timestamp_us);
			}
			break;

		case SDL_CONTROLLERTOUCHPADDOWN:
		case SDL_CONTROLLERTOUCHPADMOTION:
		case SDL_CONTROLLERTOUCHPADUP:
			if (event->ctouchpad.touchpad == 0) {
				Controller::SetTouchPad(event->ctouchpad.which, event->ctouchpad.finger,
				                        event->ctouchpad.type != SDL_CONTROLLERTOUCHPADUP,
				                        event->ctouchpad.x, event->ctouchpad.y);
			}
			break;

		case SDL_CONTROLLERDEVICEADDED:
		case SDL_CONTROLLERDEVICEREMOVED:
		case SDL_CONTROLLERDEVICEREMAPPED: {
			EventController c {};

			c.id                = event->cdevice.which;
			c.button            = SDL_CONTROLLER_BUTTON_INVALID;
			c.axis_id           = SDL_CONTROLLER_AXIS_INVALID;
			c.axis_value        = 0;
			c.down              = false;
			c.up                = false;
			c.added             = (event->cdevice.type == SDL_CONTROLLERDEVICEADDED);
			c.removed           = (event->cdevice.type == SDL_CONTROLLERDEVICEREMOVED);
			c.remapped          = (event->cdevice.type == SDL_CONTROLLERDEVICEREMAPPED);
			c.axis              = false;
			c.pressed           = false;
			c.released          = false;
			c.timestamp_seconds = time_s;

			GameEventController(c);

			break;
		}
	}
}

void WindowContext::RunOnMainThread(std::function<void()> task) {
	if (Common::Thread::IsMainThread()) {
		task();
		return;
	}

	uint64_t ticket = 0;
	{
		Common::LockGuard lock(main_task_mutex);
		main_tasks.push_back(std::move(task));
		main_task_enqueue_ns.push_back(Common::FrameStats::NowNs());
		ticket = ++main_tasks_queued;
	}

	// Wake the main loop in case it is blocked in SDL_WaitEvent.
	SDL_Event event {};
	event.type = SDL_USEREVENT;
	SDL_PushEvent(&event);

	Common::LockGuard lock(main_task_mutex);
	// Track F, F20j3 (KYTY_DIAG_B32 W:main_task, item 574(g)(1)): the caller waits for the main thread to run its task.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && main_tasks_run < ticket) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::MainTask, &main_task_done, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Main), 0);
	}
	while (main_tasks_run < ticket) {
		main_task_done.Wait(&main_task_mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(main_task_done.B32Waker(b32.SinceNs()), false);
	}
}

void WindowContext::PostToMainThread(std::function<void()> task) {
	{
		Common::LockGuard lock(main_task_mutex);
		main_tasks.push_back(std::move(task));
		main_task_enqueue_ns.push_back(Common::FrameStats::NowNs());
		++main_tasks_queued;
	}
	// Wake the main loop in case it is blocked in SDL_WaitEvent.
	SDL_Event event {};
	event.type = SDL_USEREVENT;
	SDL_PushEvent(&event);
}

void WindowContext::DrainMainThreadTasks() {
	std::vector<std::function<void()>> tasks;
	std::vector<uint64_t>              enqueued;
	{
		Common::LockGuard lock(main_task_mutex);
		tasks.swap(main_tasks);
		enqueued.swap(main_task_enqueue_ns);
	}
	if (tasks.empty()) {
		return;
	}
	for (size_t i = 0; i < tasks.size(); i++) {
		// Session 114 (ROADMAP item 4): the queue-to-run age - a busy main thread stays visible at titleasync 1.
		if (i < enqueued.size()) {
			const auto age = Common::FrameStats::NowNs() - enqueued[i];
			Common::FrameStats::Add(Common::FrameStats::Counter::MainTaskAgeNs, age);
			Common::FrameStats::Add(Common::FrameStats::Counter::MainTaskN, 1);
			if (age >= 50000000ull) {
				static std::atomic<uint32_t> late_logged {0};
				if (late_logged.fetch_add(1, std::memory_order_relaxed) < 32) {
					LOGF("MainTaskLate: us=%llu\n", static_cast<unsigned long long>(age / 1000));
				}
			}
		}
		tasks[i]();
	}
	Common::LockGuard lock(main_task_mutex);
	main_tasks_run += tasks.size();
	main_task_done.SignalAll();
}

void WindowContext::Run() {
	Common::Timer timer;
	timer.Start();

	loop.event     = {};
	loop.need_exit = false;
	loop.paused.store(false, std::memory_order_release);
	// Session 114 (ROADMAP item 4, review C1): from here on UpdateTitle may take the async title path.
	main_loop_running.store(true, std::memory_order_release);

	while (!loop.need_exit) {
		DrainMainThreadTasks();
		if (loop.paused.load(std::memory_order_acquire)) {
			if (!timer.IsPaused()) {
				timer.Pause();
			}
		} else if (timer.IsPaused()) {
			timer.Resume();
		}

		// Track F, F20j3 (KYTY_DIAG_B32 W:main_idle, item 574(g)(1)): the main thread waits for an SDL event.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::MainIdle, &loop, 0, 0);
		}
		const bool b32_event = HostInputWaitEvent(&loop.event);
		b32.End(0, false);
		if (!b32_event) {
			continue;
		}
		ProcessEvent(timer.GetTimeS());
	}
}

static void WindowCreate(WindowContext& context) {
	EXIT_IF(context.window != nullptr);
	EXIT_IF(context.graphic_ctx.screen_width == 0);
	EXIT_IF(context.graphic_ctx.screen_height == 0);

	int width  = static_cast<int>(context.graphic_ctx.screen_width);
	int height = static_cast<int>(context.graphic_ctx.screen_height);

	SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI_PS4_RUMBLE, "1");
	SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI_PS5_RUMBLE, "1");
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	SDL_SetHint(SDL_HINT_WINDOWS_DPI_SCALING, "0");
#endif

	// Track F, F40a (HPP-770, ROADMAP s122 item 692(v)): KYTY_FIX_F24, read once here before the SDL init. At 1 the main
	// thread initializes only the video subsystem and waits while JoyPump initializes the game controllers - every
	// joystick window, timer and COM apartment belongs to JoyPump (variant B, docs/track-f/f40a.md s0.1).
	JoyPump::ReadKnob();
	if (JoyPump::Enabled()) {
		const auto main_tid = static_cast<uint64_t>(SDL_ThreadID());
		SDL_SetHint(SDL_HINT_AUTO_UPDATE_JOYSTICKS, "0");
		if (SDL_InitSubSystem(SDL_INIT_VIDEO) < 0) {
			EXIT("%s\n", SDL_GetError());
		}
		std::string error;
		if (!JoyPump::Start(main_tid, &error)) {
			EXIT("%s\n", error.c_str());
		}
	} else if (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {
		EXIT("%s\n", SDL_GetError());
	}
	HostInputInit();
	InitializeSystemOverlayInput();

	LOGF("WindowCreate(): width = %d, height = %d\n", width, height);

	uint32_t window_flags = WindowContext::InitialWindowFlags(Config::FullscreenEnabled());
#if defined(__APPLE__)
	// SDL loads Vulkan while creating a Vulkan window, so select the bundled
	// MoltenVK loader before calling SDL_CreateWindow. Keep an explicit user
	// override, and fall back to SDL's normal loader search when no bundle is present.
	if (std::getenv("SDL_VULKAN_LIBRARY") == nullptr) {
		if (char* base_path = SDL_GetBasePath(); base_path != nullptr) {
			const std::string base_path_str = base_path;
			SDL_free(base_path);
			std::string moltenvk_path = base_path_str + "libMoltenVK.dylib";
			if (!Common::File::IsFileExisting(moltenvk_path)) {
				moltenvk_path = base_path_str + "../Frameworks/libMoltenVK.dylib";
			}
			if (Common::File::IsFileExisting(moltenvk_path) &&
			    SDL_setenv("SDL_VULKAN_LIBRARY", moltenvk_path.c_str(), 0) == 0) {
				LOGF("Vulkan loader: %s\n", moltenvk_path.c_str());
			}
		}
	}

	// macOS 26 window chrome (CoreUI asset decode, SwiftUI titlebar) has been observed
	// throwing NSExceptions under Rosetta during the first CATransaction commit. A
	// borderless window skips that machinery entirely.
	if (Common::EnvFlagOn("KYTY_BORDERLESS")) {
		window_flags |= static_cast<uint32_t>(SDL_WINDOW_BORDERLESS);
	}
#endif
	context.window = SDL_CreateWindow(KYTY_SDL_WINDOW_CAPTION, KYTY_SDL_WINDOWPOS_CENTERED,
	                                  KYTY_SDL_WINDOWPOS_CENTERED, width, height, window_flags);

	if (context.window == nullptr) {
		EXIT("%s\n", SDL_GetError());
	}

	SDL_SetWindowResizable(context.window, SDL_FALSE);
	context.UpdateIcon();
}

uint32_t WindowContext::InitialWindowFlags(bool fullscreen) noexcept {
	auto flags = static_cast<uint32_t>(SDL_WINDOW_VULKAN);
	if (fullscreen) {
		flags |= static_cast<uint32_t>(SDL_WINDOW_FULLSCREEN_DESKTOP);
	}
	return flags;
}

Presenter& WindowInit(uint32_t width, uint32_t height) {
	EXIT_NOT_IMPLEMENTED(!Common::Thread::IsMainThread());
	EXIT_IF(g_window != nullptr);

	auto window = std::make_unique<WindowContext>();

	window->graphic_ctx.screen_width  = width;
	window->graphic_ctx.screen_height = height;

	WindowCreate(*window);
	window->CreateVulkan();
	auto& presenter = *window->presenter;
	g_window        = std::move(window);
	return presenter;
}

void WindowRun() {
	KYTY_PROFILER_THREAD("Thread_Window");
	EXIT_IF(g_window == nullptr);

	g_window->Run();
	g_window->render_context->GetPipelineCache().Save();
}

bool WindowPrepareShaders() {
	EXIT_IF(g_window == nullptr);
	if (const char* value = std::getenv("KYTY_SHADER_PREPARE"); value != nullptr && value[0] == '0') {
		LOGF("ShaderPreparation: startup wait disabled\n");
		return true;
	}
	auto& cache = g_window->render_context->GetPipelineCache();
	const auto started = SDL_GetTicks64();
	// Session 114 (ROADMAP item 10, MEASUREMENT ONLY): KYTY_PREPARE_HOLD_MS keeps presenting the preparation screen from
	// the main thread for at least N ms after the wait started - the stress for the startup park (review C1).
	static const uint64_t hold_ms = [] {
		const char* value = std::getenv("KYTY_PREPARE_HOLD_MS");
		return value != nullptr ? static_cast<uint64_t>(std::strtoull(value, nullptr, 10)) : uint64_t {0};
	}();
	if (hold_ms != 0) {
		LOGF("PrepareHold: ms=%llu\n", static_cast<unsigned long long>(hold_ms));
	}
	// Session 115 (ROADMAP item 1): the VideoOut present thread presents the preparation overlay (the overlay makes
	// NeedsSystemOverlayRefresh true), so the presentation record ring keeps one producer.  KYTY_PREPARE_MAIN_PRESENT=1
	// (MEASUREMENT ONLY, read once) restores the old main-thread present - the positive control of the ring owner check.
	static const bool main_present = [] {
		const char* value = std::getenv("KYTY_PREPARE_MAIN_PRESENT");
		return value != nullptr && value[0] == '1' && value[1] == '\0';
	}();
	if (main_present) {
		LOGF("PrepareMainPresent: mode 1\n");
	}
	uint64_t last_log = 0;
	while (true) {
		const auto status = cache.GetPreparationStatus();
		if (!status.active && SDL_GetTicks64() - started >= hold_ms) break;
		while (SDL_PollEvent(&g_window->loop.event)) {
			// Keep window/controller lifecycle events, but don't forward game button presses.
			if (g_window->loop.event.type == SDL_QUIT ||
			    (g_window->loop.event.type == SDL_WINDOWEVENT &&
			     g_window->loop.event.window.event == SDL_WINDOWEVENT_CLOSE)) {
				SetShaderPreparationOverlay(false);
				// Track S, S17a2 (ROADMAP s122 item 532(b)): the caller ends the process by std::quick_exit; a rebuild
				// running in this start is stopped and waited for first (S18a2, item 576(g); nothing without a rebuild).
				cache.ReplayCloseStop();
				return false;
			}
			if (g_window->loop.event.type == SDL_WINDOWEVENT || g_window->loop.event.type == SDL_DISPLAYEVENT ||
			    g_window->loop.event.type == SDL_CONTROLLERDEVICEADDED ||
			    g_window->loop.event.type == SDL_CONTROLLERDEVICEREMOVED) {
				g_window->ProcessEvent(0);
			}
		}
		SetShaderPreparationOverlay(true, status.completed, status.total);
		if (main_present) {
			auto& frame = g_window->presenter->PrepareBlankFrame(
			    g_window->graphic_ctx.screen_width, g_window->graphic_ctx.screen_height, true);
			g_window->presenter->Present(frame);
		}
		const auto now = SDL_GetTicks64();
		if (last_log == 0 || now - last_log >= 1000) {
			LOGF("ShaderPreparation: progress %u/%u skipped=%u elapsed_ms=%" PRIu64 "\n",
			     status.completed, status.total, status.skipped, now - started);
			last_log = now;
		}
		SDL_Delay(16);
	}
	// This joins the producer, not just the currently queued jobs (the queue can temporarily empty).
	cache.FinishPreparation();
	SetShaderPreparationOverlay(false);
	uint64_t presents_main  = 0;
	uint64_t presents_other = 0;
	ShaderPreparationPresents(presents_main, presents_other);
	LOGF("ShaderPreparation: startup wait finished in %" PRIu64 " ms presents_other=%" PRIu64 " presents_main=%" PRIu64
	     "\n",
	     SDL_GetTicks64() - started, presents_other, presents_main);
	return true;
}

void WindowShutdown() {
	if (g_window != nullptr) {
		Controller::EmergencyShutdown();
		g_window.reset();
	}
}

// Track F, F19c (ROADMAP s122 item 451(c), F19a s4): KYTY_TEST_HIDLOSS=<s>[:<mode>] - stand only, off when unset or
// empty, read once per process (first guest log write; form of KYTY_TEST_MINIMIZE). Modes: detach (default), hold,
// sleep; any other value - line "TestHidLoss: config invalid ...", stand off. Armed by the game's first level entry line
// (TestMinimizeIsLevelEntry). At armed + max(0, <s> - PRE_S) the main thread attaches the virtual pad "KYTY test pad"
// (SDL_JoystickAttachVirtualEx: game controller type, 6 axes, 15 buttons; its Rumble, SetLED and SendEffect callbacks only
// count) - the emulator then opens it through the usual controller add event. At armed + <s> the main thread runs
// "fire": detach - SDL_JoystickDetachVirtual of the virtual pad; hold - SDL_LockJoysticks, HOLD_MS of sleep,
// SDL_UnlockJoysticks; sleep - HOLD_MS of sleep without the lock. In hold and sleep the virtual pad stays attached until
// the process ends. From fire - 1 s to done + 2 s the stand thread posts an empty main thread task every PROBE_MS that
// records its age (main_late_max_us); after done + 2 s it posts the task that closes the counting window and prints the
// line "TestHidLoss: stat ..." (main thread tasks run in posting order: every probe posted before it has run). t_us -
// Common::FrameStats::NowNs() / 1000. The stand thread is detached; a process that ends inside the window prints no stat.
//
// Track F, F40a (HPP-770, ROADMAP s122 item 692(g)(1), edition 2; docs/track-f/f40a.md s0.5-s0.6): new modes upd, flap,
// exit, pad; detach runs on the edition 2 thread (attach at fire - PRE_S and fire on the main thread as before, plus the
// probes below and the line "TestHidLoss: f24 ..."); hold and sleep are edition 1 unchanged; no cls (s0.5). Edition 2:
//  - attach (main thread): also SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1 (SDL drops a pad press without focus), the
//    HWND of the window, and from then on ProcessEvent sees first (and does not pass on) every VK_F13 key event and every
//    button A event of the virtual pad; upd, exit, pad, flap attach at fire - PRE2_S;
//  - keyboard / window / main probes (all edition 2 modes but pad), from fire - 1 s to done + 2 s: every IN_MS a
//    WM_KEYDOWN / WM_KEYUP pair of VK_F13 posted to the window (in_posted; the k-th KEYDOWN seen by ProcessEvent is the
//    k-th posted: in_seen, in_lat_max_us, in_pre_lat_max_us for those posted before fire), IsHungAppWindow every PROBE_MS
//    (hung_ms - the sum of the probe intervals that ended hung), the main thread probe tasks of edition 1; JoyPump counts
//    its update wall and tasks (JoyPump::StandWindow);
//  - pad probe (upd, pad), from fire - 20 s to fire - 1 s: button 0 (A) of the virtual pad pressed and released every
//    IN_MS by SDL_JoystickSetVirtualButton on the stand thread (the event is born in the next Update of the updating
//    thread); pad_posted, pad_seen, pad_lat_p99_us, pad_lat_max_us;
//  - upd: at fire the next Update callback of the virtual pad - inside SDL_JoystickUpdate under the joystick lock, on the
//    updating thread (main at KYTY_FIX_F24=0, JoyPump at 1) - sleeps HOLD_UPD_MS and prints "done" (upd_on_main,
//    upd_slept_us);
//  - exit: upd, then at fire + 0.5 s a JoyPump task (prints "TestHidLoss: jp_task ran") and at fire + 1 s SDL_QUIT;
//  - pad: from fire - 21 s to fire the title is not posted (UpdateTitle); fire only ends the window, done = fire;
//  - flap: from fire, FLAP_N pads "KYTY flap pad" attached one per probe step (PROBE_MS) from the stand thread, each
//    detached two steps later; JoyPump tasks run no earlier than FLAP_TASK_DELAY_MS after their post (a pad lives 2 steps,
//    less than the delay: a task opening by the event index can never open its own pad); attached - successful attaches,
//    opened - pads whose Update callback ran (SDL_JoystickOpen runs one Update), open_lat_max_us - attach to first Update.
// F40a2 (HPP-785, ROADMAP s122 item 696(b)(2), RC2 of F40b): the line "TestHidLoss: f24" ends with flap_life_min_us,
// flap_life_max_us (detach - attach of the flap slots that were attached and detached; both times taken under the
// joystick lock, attach before SDL_JoystickAttachVirtualEx, detach before SDL_JoystickDetachVirtual) and
// jp_scan_gap_max_us (JoyPump::StandScanGapBegin just before the first attach .. StandScanGapEnd just after the last
// detach: the longest stretch without a ScanAndOpen start of JoyPump; 0 at KYTY_FIX_F24=0); 0 in other modes.
constexpr double   TEST_HIDLOSS_PRE_S              = 10.0;
constexpr uint32_t TEST_HIDLOSS_HOLD_MS            = 3000;
constexpr uint32_t TEST_HIDLOSS_PROBE_MS           = 20;
constexpr double   TEST_HIDLOSS_PRE2_S             = 25.0;
constexpr uint32_t TEST_HIDLOSS_HOLD_UPD_MS        = 8000;
constexpr uint32_t TEST_HIDLOSS_IN_MS              = 100;
constexpr double   TEST_HIDLOSS_PAD_FROM_S         = 20.0;
constexpr double   TEST_HIDLOSS_PAD_TO_S           = 1.0;
constexpr double   TEST_HIDLOSS_TITLE_OFF_S        = 21.0;
constexpr double   TEST_HIDLOSS_EXIT_TASK_S        = 0.5;
constexpr double   TEST_HIDLOSS_EXIT_QUIT_S        = 1.0;
constexpr uint32_t TEST_HIDLOSS_FLAP_N             = 60;
constexpr uint32_t TEST_HIDLOSS_FLAP_TASK_DELAY_MS = 50;
constexpr uint32_t TEST_HIDLOSS_RING               = 4096;

enum class TestHidLossMode { Detach, Hold, Sleep, Upd, Flap, Exit, Pad };

struct TestHidLossConfig {
	bool            on      = false;
	double          delay_s = 0.0;
	TestHidLossMode mode    = TestHidLossMode::Detach;
};

static const char* TestHidLossModeName(TestHidLossMode mode) {
	switch (mode) {
		case TestHidLossMode::Detach: return "detach";
		case TestHidLossMode::Hold: return "hold";
		case TestHidLossMode::Sleep: return "sleep";
		case TestHidLossMode::Upd: return "upd";
		case TestHidLossMode::Flap: return "flap";
		case TestHidLossMode::Exit: return "exit";
		case TestHidLossMode::Pad: return "pad";
	}
	return "?";
}

static bool TestHidLossEdition2(TestHidLossMode mode) {
	return mode != TestHidLossMode::Hold && mode != TestHidLossMode::Sleep;
}

static TestHidLossConfig TestHidLossReadConfig() {
	TestHidLossConfig c;
	const char*       value = std::getenv("KYTY_TEST_HIDLOSS");
	if (value == nullptr || value[0] == '\0') {
		return c;
	}
	char*        end     = nullptr;
	const double delay_s = std::strtod(value, &end);
	bool ok = value[0] >= '0' && value[0] <= '9' && end != value && std::isfinite(delay_s) && delay_s <= 86400.0;
	auto mode = TestHidLossMode::Detach;
	if (ok && end[0] != '\0') {
		if (std::strcmp(end, ":detach") == 0) {
			mode = TestHidLossMode::Detach;
		} else if (std::strcmp(end, ":hold") == 0) {
			mode = TestHidLossMode::Hold;
		} else if (std::strcmp(end, ":sleep") == 0) {
			mode = TestHidLossMode::Sleep;
		} else if (std::strcmp(end, ":upd") == 0) {
			mode = TestHidLossMode::Upd;
		} else if (std::strcmp(end, ":flap") == 0) {
			mode = TestHidLossMode::Flap;
		} else if (std::strcmp(end, ":exit") == 0) {
			mode = TestHidLossMode::Exit;
		} else if (std::strcmp(end, ":pad") == 0) {
			mode = TestHidLossMode::Pad;
		} else {
			ok = false;
		}
	}
	if (!ok) {
		LOGF("TestHidLoss: config invalid value=\"%s\" (expected <s>[:detach|hold|sleep|upd|flap|exit|pad]), stand off\n",
		     value);
		return c;
	}
	c.on      = true;
	c.delay_s = delay_s;
	c.mode    = mode;
	LOGF("TestHidLoss: config on delay_s=%g mode=%s hold_ms=%u edition=%d hold_upd_ms=%u in_ms=%u probe_ms=%u fix_f24=%d\n",
	     delay_s, TestHidLossModeName(mode), TEST_HIDLOSS_HOLD_MS, TestHidLossEdition2(mode) ? 2 : 1,
	     TEST_HIDLOSS_HOLD_UPD_MS, TEST_HIDLOSS_IN_MS, TEST_HIDLOSS_PROBE_MS, JoyPump::Enabled() ? 1 : 0);
	return c;
}

static uint64_t TestHidLossNowUs() {
	return Common::FrameStats::NowNs() / 1000;
}

// Instance id of the attached virtual pad (-1: none); written by the main thread, read by the main thread and (pad probe)
// the stand thread.
static std::atomic<SDL_JoystickID> g_test_hidloss_vp {-1};
// t_us of the "done" line, 0 until fire has finished; written by the main thread (detach) or the updating thread (upd),
// read by the stand thread.
static std::atomic<uint64_t> g_test_hidloss_done_us {0};

// Edition 2 state. Atomics are written by the stand thread / the updating thread and read by the main thread; the
// fields after "main thread only" are touched by ProcessEvent and the stat task only.
struct TestHidLossEd2 {
	std::atomic<bool>      probes {false};    // ProcessEvent intercepts VK_F13 and the virtual pad's button A
	std::atomic<bool>      title_off {false}; // UpdateTitle posts nothing (mode pad)
	std::atomic<uintptr_t> hwnd {0};
	std::atomic<bool>      upd_armed {false};
	std::atomic<uint64_t>  upd_on_main {0};
	std::atomic<uint64_t>  upd_slept_us {0};
	std::atomic<uint64_t>  fire_us {0};
	std::atomic<uint64_t>  in_posted {0};
	std::atomic<uint64_t>  in_post_fail {0};
	std::atomic<uint64_t>  in_post_us[TEST_HIDLOSS_RING] {};
	std::atomic<uint64_t>  pad_posted {0};
	std::atomic<uint64_t>  pad_post_us[TEST_HIDLOSS_RING] {};
	std::atomic<uint64_t>  hung_ms {0};
	std::atomic<uint64_t>  flap_attached {0};
	std::atomic<uint64_t>  flap_attach_us[TEST_HIDLOSS_FLAP_N] {};
	std::atomic<uint64_t>  flap_open_us[TEST_HIDLOSS_FLAP_N] {};
	std::atomic<uint64_t>  flap_detach_us[TEST_HIDLOSS_FLAP_N] {}; // F40a2: 0 - not detached
	std::atomic<uint64_t>  jp_scan_gap_max_us {0};                 // F40a2
	// Main thread only.
	uint64_t              in_seen           = 0;
	uint64_t              in_lat_max_us     = 0;
	uint64_t              in_pre_lat_max_us = 0;
	uint64_t              pad_seen          = 0;
	std::vector<uint64_t> pad_lat_us;
};

static TestHidLossEd2 g_test_hidloss2;

// Main thread, first thing of ProcessEvent (after the display event check); one relaxed load when the stand is off.
static bool TestHidLossIntercept(const SDL_Event& event) {
	auto& e = g_test_hidloss2;
	if (!e.probes.load(std::memory_order_relaxed)) {
		return false;
	}
	if ((event.type == SDL_KEYDOWN || event.type == SDL_KEYUP) && event.key.keysym.sym == SDLK_F13) {
		if (event.type == SDL_KEYDOWN) {
			const uint64_t k = e.in_seen++;
			if (k < e.in_posted.load(std::memory_order_acquire)) {
				const uint64_t posted_us = e.in_post_us[k % TEST_HIDLOSS_RING].load(std::memory_order_relaxed);
				const uint64_t lat_us    = TestHidLossNowUs() - posted_us;
				e.in_lat_max_us          = std::max(e.in_lat_max_us, lat_us);
				if (posted_us < e.fire_us.load(std::memory_order_relaxed)) {
					e.in_pre_lat_max_us = std::max(e.in_pre_lat_max_us, lat_us);
				}
			}
		}
		return true;
	}
	if ((event.type == SDL_CONTROLLERBUTTONDOWN || event.type == SDL_CONTROLLERBUTTONUP) &&
	    event.cbutton.which == g_test_hidloss_vp.load(std::memory_order_relaxed) &&
	    event.cbutton.button == SDL_CONTROLLER_BUTTON_A) {
		const uint64_t k = e.pad_seen++;
		if (k < e.pad_posted.load(std::memory_order_acquire)) {
			e.pad_lat_us.push_back(TestHidLossNowUs() -
			                       e.pad_post_us[k % TEST_HIDLOSS_RING].load(std::memory_order_relaxed));
		}
		return true;
	}
	return false;
}

static bool TestHidLossTitleOff() {
	return g_test_hidloss2.title_off.load(std::memory_order_relaxed);
}

static int SDLCALL TestHidLossVpRumble(void* /*userdata*/, Uint16 /*low*/, Uint16 /*high*/) {
	TestHidLossCount(g_test_hidloss.vp_rumble);
	return 0;
}

static int SDLCALL TestHidLossVpSetLed(void* /*userdata*/, Uint8 /*red*/, Uint8 /*green*/, Uint8 /*blue*/) {
	TestHidLossCount(g_test_hidloss.vp_led);
	return 0;
}

static int SDLCALL TestHidLossVpSendEffect(void* /*userdata*/, const void* /*data*/, int /*size*/) {
	TestHidLossCount(g_test_hidloss.vp_effect);
	return 0;
}

// Edition 2, upd: inside SDL_JoystickUpdate under the joystick lock, on the updating thread. One relaxed load when not
// armed.
static void SDLCALL TestHidLossVpUpdate(void* /*userdata*/) {
	auto& e = g_test_hidloss2;
	if (!e.upd_armed.load(std::memory_order_relaxed) || !e.upd_armed.exchange(false, std::memory_order_acq_rel)) {
		return;
	}
	const bool     on_main = Common::Thread::IsMainThread();
	const uint64_t start   = TestHidLossNowUs();
	std::this_thread::sleep_for(std::chrono::milliseconds(TEST_HIDLOSS_HOLD_UPD_MS));
	const uint64_t done_us = TestHidLossNowUs();
	e.upd_on_main.store(on_main ? 1 : 0, std::memory_order_relaxed);
	e.upd_slept_us.store(done_us - start, std::memory_order_relaxed);
	LOGF("TestHidLoss: done t_us=%" PRIu64 " upd_on_main=%d\n", done_us, on_main ? 1 : 0);
	g_test_hidloss_done_us.store(done_us, std::memory_order_release);
}

// Edition 2, flap: the first Update of a flap pad (SDL_JoystickOpen runs one) marks it opened.
static void SDLCALL TestHidLossFlapUpdate(void* userdata) {
	const auto slot = static_cast<uint32_t>(reinterpret_cast<uintptr_t>(userdata));
	if (slot < TEST_HIDLOSS_FLAP_N) {
		uint64_t expected = 0;
		g_test_hidloss2.flap_open_us[slot].compare_exchange_strong(expected, TestHidLossNowUs(), std::memory_order_relaxed);
	}
}

// Main thread.
static void TestHidLossAttach(bool edition2) {
	SDL_VirtualJoystickDesc desc {};
	desc.version    = SDL_VIRTUAL_JOYSTICK_DESC_VERSION;
	desc.type       = SDL_JOYSTICK_TYPE_GAMECONTROLLER;
	desc.naxes      = 6;
	desc.nbuttons   = 15;
	desc.name       = "KYTY test pad";
	desc.Rumble     = TestHidLossVpRumble;
	desc.SetLED     = TestHidLossVpSetLed;
	desc.SendEffect = TestHidLossVpSendEffect;
	if (edition2) {
		desc.Update = TestHidLossVpUpdate;
		SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");
		if (g_window != nullptr) {
			g_test_hidloss2.hwnd.store(JoyPump::StandWindowHandle(g_window->window), std::memory_order_relaxed);
		}
	}
	const int index = SDL_JoystickAttachVirtualEx(&desc);
	if (index < 0) {
		LOGF("TestHidLoss: attach failed error=\"%s\" t_us=%" PRIu64 "\n", SDL_GetError(), TestHidLossNowUs());
		return;
	}
	g_test_hidloss_vp.store(SDL_JoystickGetDeviceInstanceID(index), std::memory_order_relaxed);
	if (edition2) {
		g_test_hidloss2.probes.store(true, std::memory_order_release);
	}
	LOGF("TestHidLoss: attach index=%d t_us=%" PRIu64 " hwnd=%d\n", index, TestHidLossNowUs(),
	     g_test_hidloss2.hwnd.load(std::memory_order_relaxed) != 0 ? 1 : 0);
}

// Main thread.
static void TestHidLossFire(TestHidLossMode mode) {
	LOGF("TestHidLoss: fire mode=%s t_us=%" PRIu64 "\n", TestHidLossModeName(mode), TestHidLossNowUs());
	switch (mode) {
		case TestHidLossMode::Detach: {
			const SDL_JoystickID vp    = g_test_hidloss_vp.load(std::memory_order_relaxed);
			int                  index = -1;
			for (int i = 0; vp >= 0 && i < SDL_NumJoysticks(); i++) {
				if (SDL_JoystickGetDeviceInstanceID(i) == vp) {
					index = i;
					break;
				}
			}
			if (index < 0 || SDL_JoystickDetachVirtual(index) != 0) {
				LOGF("TestHidLoss: detach failed index=%d error=\"%s\"\n", index, SDL_GetError());
			}
			break;
		}
		case TestHidLossMode::Hold:
			SDL_LockJoysticks();
			SDL_Delay(TEST_HIDLOSS_HOLD_MS);
			SDL_UnlockJoysticks();
			break;
		case TestHidLossMode::Sleep: SDL_Delay(TEST_HIDLOSS_HOLD_MS); break;
		default: break; // edition 2 modes other than detach fire on the stand thread
	}
	const uint64_t done_us = TestHidLossNowUs();
	LOGF("TestHidLoss: done t_us=%" PRIu64 "\n", done_us);
	g_test_hidloss_done_us.store(done_us, std::memory_order_release);
}

// Main thread.
static void TestHidLossStat(TestHidLossMode mode) {
	g_test_hidloss.window.store(false, std::memory_order_relaxed);
	Controller::TestHidLossWindow(false);
	const auto pad = Controller::TestHidLossPadStats();
	const auto get = [](const std::atomic<uint64_t>& value) {
		return static_cast<unsigned long long>(value.load(std::memory_order_relaxed));
	};
	const auto u = [](uint64_t value) { return static_cast<unsigned long long>(value); };
	LOGF("TestHidLoss: stat mode=%s main_late_max_us=%llu probes_posted=%llu probes_run=%llu pad_calls=%llu pad_vib=%llu "
	     "pad_led=%llu pad_trig=%llu pad_wait_max_us=%llu po_applied=%llu po_wait_max_us=%llu guest_sdl=%llu removed=%llu "
	     "vp_rumble=%llu vp_led=%llu vp_effect=%llu\n",
	     TestHidLossModeName(mode), get(g_test_hidloss.main_late_max_us), get(g_test_hidloss.probes_posted),
	     get(g_test_hidloss.probes_run), u(pad.pad_vib + pad.pad_led + pad.pad_trig), u(pad.pad_vib), u(pad.pad_led),
	     u(pad.pad_trig), u(pad.pad_wait_max_us), u(pad.po_applied), u(pad.po_wait_max_us), u(pad.guest_sdl),
	     get(g_test_hidloss.removed), get(g_test_hidloss.vp_rumble), get(g_test_hidloss.vp_led),
	     get(g_test_hidloss.vp_effect));
	if (!TestHidLossEdition2(mode)) {
		return;
	}
	auto& e = g_test_hidloss2;
	e.probes.store(false, std::memory_order_relaxed);
	const auto jp = JoyPump::StandRead();
	JoyPump::StandWindow(false);
	auto lat = e.pad_lat_us;
	std::sort(lat.begin(), lat.end());
	const uint64_t p99     = lat.empty() ? 0 : lat[(lat.size() * 99 + 99) / 100 - 1];
	const uint64_t lat_max = lat.empty() ? 0 : lat.back();
	uint64_t       opened  = 0;
	uint64_t       open_lat_max_us = 0;
	const uint64_t attached        = e.flap_attached.load(std::memory_order_relaxed);
	for (uint32_t i = 0; i < TEST_HIDLOSS_FLAP_N && i < attached; i++) {
		const uint64_t open_us = e.flap_open_us[i].load(std::memory_order_relaxed);
		if (open_us != 0) {
			opened++;
			open_lat_max_us = std::max(open_lat_max_us, open_us - e.flap_attach_us[i].load(std::memory_order_relaxed));
		}
	}
	uint64_t life_min_us = 0;
	uint64_t life_max_us = 0;
	uint64_t life_n      = 0;
	for (uint32_t i = 0; i < TEST_HIDLOSS_FLAP_N; i++) {
		const uint64_t attach_us = e.flap_attach_us[i].load(std::memory_order_relaxed);
		const uint64_t detach_us = e.flap_detach_us[i].load(std::memory_order_relaxed);
		if (attach_us != 0 && detach_us >= attach_us) {
			const uint64_t life_us = detach_us - attach_us;
			life_min_us             = life_n == 0 ? life_us : std::min(life_min_us, life_us);
			life_max_us             = std::max(life_max_us, life_us);
			life_n++;
		}
	}
	LOGF("TestHidLoss: f24 mode=%s fix=%d upd_on_main=%llu upd_slept_us=%llu main_late_max_us=%llu in_posted=%llu "
	     "in_seen=%llu in_post_fail=%llu in_lat_max_us=%llu in_pre_lat_max_us=%llu hung_ms=%llu jp_update_max_us=%llu "
	     "jp_tasks=%llu pad_posted=%llu pad_seen=%llu pad_lat_p99_us=%llu pad_lat_max_us=%llu attached=%llu opened=%llu "
	     "open_failed=%llu open_lat_max_us=%llu flap_life_min_us=%llu flap_life_max_us=%llu jp_scan_gap_max_us=%llu\n",
	     TestHidLossModeName(mode), JoyPump::Enabled() ? 1 : 0, get(e.upd_on_main), get(e.upd_slept_us),
	     get(g_test_hidloss.main_late_max_us), get(e.in_posted), u(e.in_seen), get(e.in_post_fail), u(e.in_lat_max_us),
	     u(e.in_pre_lat_max_us), get(e.hung_ms), u(jp.update_max_us), u(jp.tasks), get(e.pad_posted), u(e.pad_seen),
	     u(p99), u(lat_max), u(attached), u(opened), u(jp.open_failed), u(open_lat_max_us), u(life_min_us), u(life_max_us),
	     get(e.jp_scan_gap_max_us));
}

static bool TestHidLossPost(std::function<void()> task) {
	auto* context = g_window.get();
	if (context == nullptr) {
		return false;
	}
	context->PostToMainThread(std::move(task));
	return true;
}

// The stand thread (detached).
static void TestHidLossRun(TestHidLossConfig cfg, uint64_t armed_us) {
	const auto at = [armed_us](double s) { return armed_us + static_cast<uint64_t>((s > 0.0 ? s : 0.0) * 1000000.0); };
	const auto sleep_until = [](uint64_t t_us) {
		const uint64_t now = TestHidLossNowUs();
		if (t_us > now) {
			std::this_thread::sleep_for(std::chrono::microseconds(t_us - now));
		}
	};
	sleep_until(at(cfg.delay_s - TEST_HIDLOSS_PRE_S));
	if (!TestHidLossPost([] { TestHidLossAttach(false); })) {
		return;
	}
	sleep_until(at(cfg.delay_s - 1.0));
	Controller::TestHidLossWindow(true);
	g_test_hidloss.window.store(true, std::memory_order_release);
	const uint64_t fire_us = at(cfg.delay_s);
	bool           fired   = false;
	for (;;) {
		const uint64_t now = TestHidLossNowUs();
		if (!fired && now >= fire_us) {
			if (!TestHidLossPost([mode = cfg.mode] { TestHidLossFire(mode); })) {
				return;
			}
			fired = true;
		}
		const uint64_t done_us = g_test_hidloss_done_us.load(std::memory_order_acquire);
		if (done_us != 0 && now >= done_us + 2000000) {
			break;
		}
		g_test_hidloss.probes_posted.fetch_add(1, std::memory_order_relaxed);
		const uint64_t posted_ns = Common::FrameStats::NowNs();
		if (!TestHidLossPost([posted_ns] {
			    const uint64_t age_us = (Common::FrameStats::NowNs() - posted_ns) / 1000;
			    uint64_t current = g_test_hidloss.main_late_max_us.load(std::memory_order_relaxed);
			    while (age_us > current && !g_test_hidloss.main_late_max_us.compare_exchange_weak(
			                                   current, age_us, std::memory_order_relaxed)) {
			    }
			    g_test_hidloss.probes_run.fetch_add(1, std::memory_order_relaxed);
		    })) {
			return;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(TEST_HIDLOSS_PROBE_MS));
	}
	TestHidLossPost([mode = cfg.mode] { TestHidLossStat(mode); });
}

// Edition 2, the stand thread: one keyboard probe pair (the time and the count first - the main thread may see the
// KEYDOWN before PostMessage returns).
static void TestHidLossKeyProbe() {
	auto&          e    = g_test_hidloss2;
	const uintptr_t hwnd = e.hwnd.load(std::memory_order_relaxed);
	const uint64_t k    = e.in_posted.load(std::memory_order_relaxed);
	e.in_post_us[k % TEST_HIDLOSS_RING].store(TestHidLossNowUs(), std::memory_order_relaxed);
	e.in_posted.store(k + 1, std::memory_order_release);
	if (!JoyPump::StandPostKey(hwnd, true) || !JoyPump::StandPostKey(hwnd, false)) {
		e.in_post_fail.fetch_add(1, std::memory_order_relaxed);
	}
}

// Edition 2, the stand thread: one pad probe transition. Under the joystick lock the event cannot be born (it is born in
// Update, which takes the lock) before the time and the count are stored.
static void TestHidLossPadProbe(bool down) {
	auto& e = g_test_hidloss2;
	SDL_LockJoysticks();
	if (auto* joy = SDL_JoystickFromInstanceID(g_test_hidloss_vp.load(std::memory_order_relaxed)); joy != nullptr) {
		const uint64_t k = e.pad_posted.load(std::memory_order_relaxed);
		e.pad_post_us[k % TEST_HIDLOSS_RING].store(TestHidLossNowUs(), std::memory_order_relaxed);
		e.pad_posted.store(k + 1, std::memory_order_release);
		(void)SDL_JoystickSetVirtualButton(joy, 0, down ? SDL_PRESSED : SDL_RELEASED);
	}
	SDL_UnlockJoysticks();
}

// Edition 2, flap: attach / detach from the stand thread (the joystick lock makes index and instance id agree).
static SDL_JoystickID TestHidLossFlapAttach(uint32_t slot) {
	SDL_VirtualJoystickDesc desc {};
	desc.version  = SDL_VIRTUAL_JOYSTICK_DESC_VERSION;
	desc.type     = SDL_JOYSTICK_TYPE_GAMECONTROLLER;
	desc.naxes    = 6;
	desc.nbuttons = 15;
	desc.name     = "KYTY flap pad";
	desc.userdata = reinterpret_cast<void*>(static_cast<uintptr_t>(slot));
	desc.Update   = TestHidLossFlapUpdate;
	SDL_LockJoysticks();
	g_test_hidloss2.flap_attach_us[slot].store(TestHidLossNowUs(), std::memory_order_relaxed);
	const int            index = SDL_JoystickAttachVirtualEx(&desc);
	const SDL_JoystickID id    = index >= 0 ? SDL_JoystickGetDeviceInstanceID(index) : -1;
	SDL_UnlockJoysticks();
	if (id < 0) {
		LOGF("TestHidLoss: flap attach failed slot=%u error=\"%s\"\n", slot, SDL_GetError());
	}
	return id;
}

static void TestHidLossFlapDetach(uint32_t slot, SDL_JoystickID id) {
	if (id < 0) {
		return;
	}
	SDL_LockJoysticks();
	for (int i = 0; i < SDL_NumJoysticks(); i++) {
		if (SDL_JoystickGetDeviceInstanceID(i) == id) {
			const uint64_t detach_us = TestHidLossNowUs(); // F40a2: under the lock, before the detach
			if (SDL_JoystickDetachVirtual(i) == 0 && slot < TEST_HIDLOSS_FLAP_N) {
				g_test_hidloss2.flap_detach_us[slot].store(detach_us, std::memory_order_relaxed);
			}
			break;
		}
	}
	SDL_UnlockJoysticks();
}

// The stand thread of edition 2 (detached).
static void TestHidLossRun2(TestHidLossConfig cfg, uint64_t armed_us) {
	auto&      e  = g_test_hidloss2;
	const auto at = [armed_us](double s) { return armed_us + static_cast<uint64_t>((s > 0.0 ? s : 0.0) * 1000000.0); };
	const auto sleep_until = [](uint64_t t_us) {
		const uint64_t now = TestHidLossNowUs();
		if (t_us > now) {
			std::this_thread::sleep_for(std::chrono::microseconds(t_us - now));
		}
	};
	const auto mode    = cfg.mode;
	const auto fire_us = at(cfg.delay_s);
	e.fire_us.store(fire_us, std::memory_order_relaxed);
	sleep_until(at(cfg.delay_s - (mode == TestHidLossMode::Detach ? TEST_HIDLOSS_PRE_S : TEST_HIDLOSS_PRE2_S)));
	if (!TestHidLossPost([] { TestHidLossAttach(true); })) {
		return;
	}
	if (mode == TestHidLossMode::Upd || mode == TestHidLossMode::Pad) {
		if (mode == TestHidLossMode::Pad) {
			sleep_until(at(cfg.delay_s - TEST_HIDLOSS_TITLE_OFF_S));
			e.title_off.store(true, std::memory_order_relaxed);
			LOGF("TestHidLoss: title off t_us=%" PRIu64 "\n", TestHidLossNowUs());
		}
		sleep_until(at(cfg.delay_s - TEST_HIDLOSS_PAD_FROM_S));
		const uint64_t until = at(cfg.delay_s - TEST_HIDLOSS_PAD_TO_S);
		LOGF("TestHidLoss: pad probe start t_us=%" PRIu64 "\n", TestHidLossNowUs());
		while (TestHidLossNowUs() < until) {
			TestHidLossPadProbe(true);
			std::this_thread::sleep_for(std::chrono::milliseconds(TEST_HIDLOSS_IN_MS / 2));
			TestHidLossPadProbe(false);
			std::this_thread::sleep_for(std::chrono::milliseconds(TEST_HIDLOSS_IN_MS / 2));
		}
		LOGF("TestHidLoss: pad probe end t_us=%" PRIu64 " posted=%" PRIu64 "\n", TestHidLossNowUs(),
		     e.pad_posted.load(std::memory_order_relaxed));
	}
	if (mode == TestHidLossMode::Pad) {
		sleep_until(fire_us);
		LOGF("TestHidLoss: fire mode=pad t_us=%" PRIu64 "\n", TestHidLossNowUs());
		e.title_off.store(false, std::memory_order_relaxed);
		const uint64_t done_us = TestHidLossNowUs();
		LOGF("TestHidLoss: done t_us=%" PRIu64 "\n", done_us);
		g_test_hidloss_done_us.store(done_us, std::memory_order_release);
		sleep_until(done_us + 2000000);
		TestHidLossPost([mode] { TestHidLossStat(mode); });
		return;
	}
	sleep_until(at(cfg.delay_s - 1.0));
	Controller::TestHidLossWindow(true);
	JoyPump::StandWindow(true);
	g_test_hidloss.window.store(true, std::memory_order_release);
	bool           fired     = false;
	bool           exit_task = false;
	bool           exit_quit = false;
	uint32_t       flap_k    = 0;
	SDL_JoystickID flap_ids[TEST_HIDLOSS_FLAP_N] {};
	uint64_t       iter      = 0;
	uint64_t       hung_prev = 0;
	for (;;) {
		const uint64_t now = TestHidLossNowUs();
		if (!fired && now >= fire_us) {
			fired = true;
			if (mode == TestHidLossMode::Detach) {
				if (!TestHidLossPost([mode] { TestHidLossFire(mode); })) {
					return;
				}
			} else {
				LOGF("TestHidLoss: fire mode=%s t_us=%" PRIu64 "\n", TestHidLossModeName(mode), now);
				if (mode == TestHidLossMode::Flap) {
					JoyPump::StandTaskDelayMs(TEST_HIDLOSS_FLAP_TASK_DELAY_MS);
				} else {
					e.upd_armed.store(true, std::memory_order_release);
				}
			}
		}
		if (fired && mode == TestHidLossMode::Flap && flap_k < TEST_HIDLOSS_FLAP_N + 2) {
			if (flap_k < TEST_HIDLOSS_FLAP_N) {
				if (flap_k == 0) {
					JoyPump::StandScanGapBegin(); // F40a2 (RC2 of F40b): just before the first attach
				}
				flap_ids[flap_k] = TestHidLossFlapAttach(flap_k);
				if (flap_ids[flap_k] >= 0) {
					e.flap_attached.fetch_add(1, std::memory_order_relaxed);
				}
			}
			if (flap_k >= 2) {
				TestHidLossFlapDetach(flap_k - 2, flap_ids[flap_k - 2]);
			}
			flap_k++;
			if (flap_k == TEST_HIDLOSS_FLAP_N + 2) {
				e.jp_scan_gap_max_us.store(JoyPump::StandScanGapEnd(), std::memory_order_relaxed); // F40a2: after the last detach
				const uint64_t done_us = TestHidLossNowUs();
				LOGF("TestHidLoss: done t_us=%" PRIu64 " flap_attached=%" PRIu64 "\n", done_us,
				     e.flap_attached.load(std::memory_order_relaxed));
				g_test_hidloss_done_us.store(done_us, std::memory_order_release);
			}
		}
		if (fired && mode == TestHidLossMode::Flap && flap_k == TEST_HIDLOSS_FLAP_N + 2 &&
		    now >= g_test_hidloss_done_us.load(std::memory_order_acquire) + 1000000) {
			JoyPump::StandTaskDelayMs(0); // the delayed closes of the last pads run before the stat
		}
		if (fired && mode == TestHidLossMode::Exit) {
			if (!exit_task && now >= fire_us + static_cast<uint64_t>(TEST_HIDLOSS_EXIT_TASK_S * 1000000.0)) {
				exit_task = true;
				LOGF("TestHidLoss: jp_task posted t_us=%" PRIu64 "\n", now);
				JoyPump::Post([] { LOGF("TestHidLoss: jp_task ran t_us=%" PRIu64 "\n", TestHidLossNowUs()); });
			}
			if (!exit_quit && now >= fire_us + static_cast<uint64_t>(TEST_HIDLOSS_EXIT_QUIT_S * 1000000.0)) {
				exit_quit = true;
				LOGF("TestHidLoss: quit posted t_us=%" PRIu64 "\n", now);
				SDL_Event quit {};
				quit.type = SDL_QUIT;
				SDL_PushEvent(&quit);
			}
		}
		const uint64_t done_us = g_test_hidloss_done_us.load(std::memory_order_acquire);
		if (done_us != 0 && now >= done_us + 2000000) {
			break;
		}
		g_test_hidloss.probes_posted.fetch_add(1, std::memory_order_relaxed);
		const uint64_t posted_ns = Common::FrameStats::NowNs();
		if (!TestHidLossPost([posted_ns] {
			    const uint64_t age_us = (Common::FrameStats::NowNs() - posted_ns) / 1000;
			    uint64_t current = g_test_hidloss.main_late_max_us.load(std::memory_order_relaxed);
			    while (age_us > current && !g_test_hidloss.main_late_max_us.compare_exchange_weak(
			                                   current, age_us, std::memory_order_relaxed)) {
			    }
			    g_test_hidloss.probes_run.fetch_add(1, std::memory_order_relaxed);
		    })) {
			return;
		}
		const uint64_t hung_now = TestHidLossNowUs();
		if (JoyPump::StandIsHung(e.hwnd.load(std::memory_order_relaxed)) && hung_prev != 0) {
			e.hung_ms.fetch_add((hung_now - hung_prev) / 1000, std::memory_order_relaxed);
		}
		hung_prev = hung_now;
		if (iter++ % (TEST_HIDLOSS_IN_MS / TEST_HIDLOSS_PROBE_MS) == 0) {
			TestHidLossKeyProbe();
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(TEST_HIDLOSS_PROBE_MS));
	}
	TestHidLossPost([mode] { TestHidLossStat(mode); });
}

static void WindowTestHidLossNoteGuestText(const char* text, size_t size) {
	static const TestHidLossConfig cfg = TestHidLossReadConfig();
	static std::atomic<bool>       armed {false};
	if (!cfg.on || text == nullptr || armed.load(std::memory_order_relaxed)) {
		return;
	}
	if (!TestMinimizeIsLevelEntry(std::string_view(text, size)) || armed.exchange(true, std::memory_order_acq_rel)) {
		return;
	}
	const uint64_t armed_us = TestHidLossNowUs();
	LOGF("TestHidLoss: armed t_us=%" PRIu64 "\n", armed_us);
	if (TestHidLossEdition2(cfg.mode)) {
		std::thread([armed_us] { TestHidLossRun2(cfg, armed_us); }).detach();
	} else {
		std::thread([armed_us] { TestHidLossRun(cfg, armed_us); }).detach();
	}
}

// Track F, F5 (ROADMAP s122 item 273(e)(2), MEASUREMENT ONLY): KYTY_TEST_MINIMIZE=<s>:<dur> - <s> seconds after the
// game's first level entry line "Level has started: <level>" with a non-blank level name (F5a2, item 280(v): the
// earlier line with an empty name does not arm; TestMinimizeIsLevelEntry) the emulator minimizes its own window
// (SDL_MinimizeWindow on the main thread)
// and restores it <dur> seconds later (SDL_RestoreWindow); lines "TestMinimize: minimize" / "TestMinimize: restore".
// Unset or empty - nothing (one getenv, then a static flag per guest log write).  The timer is a detached thread that
// sleeps; the SDL calls are posted to the main thread.  A process that ends inside the window never restores it.
void WindowTestMinimizeNoteGuestText(const char* text, size_t size) {
	WindowTestHidLossNoteGuestText(text, size); // Track F, F19c, KYTY_TEST_HIDLOSS (item 451(c))
	if (Common::DiagB32::g_test_on && text != nullptr) [[unlikely]] { // Track F, F20j: KYTY_TEST_B32 arms on the same line
		if (TestMinimizeIsLevelEntry(std::string_view(text, size))) {
			Common::DiagB32::TestArm();
		}
	}
	struct TestMinimize {
		bool   on      = false;
		double delay_s = 0.0;
		double dur_s   = 0.0;
	};
	static const TestMinimize cfg = [] {
		TestMinimize c;
		const char*  value = std::getenv("KYTY_TEST_MINIMIZE");
		if (value == nullptr || value[0] == '\0') {
			return c;
		}
		char* end = nullptr;
		c.delay_s = std::strtod(value, &end);
		if (end != value && end != nullptr && *end == ':') {
			const char* dur = end + 1;
			c.dur_s         = std::strtod(dur, &end);
			c.on            = end != dur && *end == '\0' && c.delay_s >= 0.0 && c.dur_s >= 0.0;
		}
		LOGF("TestMinimize: config %s delay_s=%.3f dur_s=%.3f\n", c.on ? "on" : "invalid", c.delay_s, c.dur_s);
		return c;
	}();
	static std::atomic<bool> armed {false};
	if (!cfg.on || text == nullptr || armed.load(std::memory_order_relaxed)) {
		return;
	}
	if (!TestMinimizeIsLevelEntry(std::string_view(text, size)) ||
	    armed.exchange(true, std::memory_order_acq_rel)) {
		return;
	}
	LOGF("TestMinimize: armed delay_s=%.3f dur_s=%.3f\n", cfg.delay_s, cfg.dur_s);
	std::thread([] {
		const auto post = [](bool minimize) {
			auto* context = g_window.get();
			if (context == nullptr) {
				return;
			}
			context->PostToMainThread([context, minimize] {
				if (context->window == nullptr) {
					return;
				}
				if (minimize) {
					LOGF("TestMinimize: minimize\n");
					SDL_MinimizeWindow(context->window);
				} else {
					LOGF("TestMinimize: restore\n");
					SDL_RestoreWindow(context->window);
				}
			});
		};
		std::this_thread::sleep_for(std::chrono::duration<double>(cfg.delay_s));
		post(true);
		std::this_thread::sleep_for(std::chrono::duration<double>(cfg.dur_s));
		post(false);
	}).detach();
}

static int WindowIconRead(void* user, char* data, int size) {
	auto*    src        = static_cast<Common::File*>(user);
	uint32_t bytes_read = 0;
	src->Read(data, static_cast<uint32_t>(size), &bytes_read);
	return static_cast<int>(bytes_read);
}

static void WindowIconSkip(void* user, int n) {
	auto*          src      = static_cast<Common::File*>(user);
	const uint64_t position = src->Tell();

	if (n >= 0) {
		src->Seek(position + static_cast<uint64_t>(n));
	} else {
		const uint64_t distance = static_cast<uint64_t>(-static_cast<int64_t>(n));
		EXIT_IF(distance > position);
		src->Seek(position - distance);
	}
}

static int WindowIconEof(void* user) {
	auto* src = static_cast<Common::File*>(user);
	return src->IsEOF() ? 1 : 0;
}

struct WindowIcon {
	SDL_Surface* surface = nullptr;
	void*        pixels  = nullptr;

	~WindowIcon() {
		SDL_FreeSurface(surface);
		stbi_image_free(pixels);
	}
};

static void WindowLoadPngIcon(const std::string& path, WindowIcon* icon) {
	Common::File f;
	if (!f.Open(path, Common::File::Mode::Read)) {
		EXIT("Can't open icon file %s\n", path.c_str());
	}

	int width  = 0;
	int height = 0;

	stbi_io_callbacks cb {};
	cb.read = WindowIconRead;
	cb.skip = WindowIconSkip;
	cb.eof  = WindowIconEof;

	icon->pixels = stbi_load_from_callbacks(&cb, &f, &width, &height, nullptr, 4);
	f.Close();

	EXIT_IF(icon->pixels == nullptr);

	icon->surface = SDL_CreateRGBSurfaceWithFormatFrom(icon->pixels, width, height, 32, width * 4,
	                                                   SDL_PIXELFORMAT_RGBA32);
	EXIT_NOT_IMPLEMENTED(icon->surface == nullptr);
}

void WindowContext::UpdateIcon() {
	static WindowIcon icon;
	static bool       icon_loaded = false;

	if (!icon_loaded) {
		std::string icon_path;
		if (Loader::SystemContentGetIconPath(&icon_path)) {
			WindowLoadPngIcon(icon_path, &icon);
		}
		icon_loaded = true;
	}

	if (icon.surface != nullptr) {
		SDL_SetWindowIcon(window, icon.surface);
	}
}

void WindowContext::UpdateTitle() {
	static char title[128];
	static char title_id[12];
	static char app_ver[12];
	static bool has_title = Loader::SystemContentParamSfoGetString("TITLE", title, sizeof(title));
	static bool has_title_id =
	    Loader::SystemContentParamSfoGetString("TITLE_ID", title_id, sizeof(title_id));
	static bool has_app_ver =
	    Loader::SystemContentParamSfoGetString("APP_VER", app_ver, sizeof(app_ver));
	static const std::string processor_name = Common::GetSystemInfo().ProcessorName;
	static uint64_t fps_start   = Common::Timer::QueryPerformanceCounter();
	static uint64_t frame_num   = 0;
	static uint64_t fps_frames  = 0;
	static double   current_fps = 0.0;

#if KYTY_BUILD == KYTY_BUILD_DEBUG
	static constexpr auto build_type = "Debug";
#elif KYTY_BUILD == KYTY_BUILD_RELEASE
	static constexpr auto build_type = "Release";
#else
	static constexpr auto build_type = "Unknown";
#endif

	const auto now       = Common::Timer::QueryPerformanceCounter();
	const auto frequency = Common::Timer::QueryPerformanceFrequency();
	frame_num++;
	fps_frames++;
	if (now - fps_start >= frequency) {
		current_fps = static_cast<double>(fps_frames) * static_cast<double>(frequency) /
		              static_cast<double>(now - fps_start);
		fps_start   = now;
		fps_frames  = 0;
	}

	const auto* device_name = graphic_ctx.GetPhysicalDeviceProperties().deviceName.data();
	auto text = fmt::format(
	    "[{} | {}] {}{}{}{}{}{}[{}] [{}], frame: {}, fps: {:.0f}", KYTY_BUILD_LABEL, build_type,
	    (has_title ? title : ""), (has_title ? ", " : ""), (has_title_id ? title_id : ""),
	    (has_title_id ? ", " : ""), (has_app_ver ? app_ver : ""), (has_app_ver ? " " : ""),
	    device_name, processor_name, frame_num, current_fps);

	// Session 114 (ROADMAP §0.1 "СЕССИЯ 114" item 2): the present thread holds VideoOutConfig::mutex here, so waiting
	// for the SDL main thread (titleasync 0) stops the flip path while the main thread is busy.  KYTY_MAIN_STALL_TEST=
	// <frame>:<ms> (measurement only, read once) queues a sleep on the main thread at one frame: the positive control.
	static const std::pair<uint64_t, uint32_t> stall_test = [] {
		std::pair<uint64_t, uint32_t> v {0, 0};
		if (const char* s = std::getenv("KYTY_MAIN_STALL_TEST"); s != nullptr) {
			char* end = nullptr;
			v.first   = std::strtoull(s, &end, 10);
			if (end != nullptr && *end == ':') {
				v.second = static_cast<uint32_t>(std::strtoul(end + 1, nullptr, 10));
			}
			LOGF("MainStallTest: frame=%llu ms=%u\n", static_cast<unsigned long long>(v.first), v.second);
		}
		return v;
	}();
	if (stall_test.second != 0 && frame_num == stall_test.first) {
		const auto ms = stall_test.second;
		LOGF("MainStallTest: queued frame=%llu ms=%u\n", static_cast<unsigned long long>(frame_num), ms);
		PostToMainThread([ms] { std::this_thread::sleep_for(std::chrono::milliseconds(ms)); });
	}
	// Session 115 (ROADMAP item 1): before the SDL main loop runs the title is always posted - the main thread no longer
	// presents during WindowPrepareShaders, so nothing needs the present thread parked, and a parked present thread
	// could not present the preparation overlay.  Once the loop runs, the knob decides (session 114).
	const bool loop_running = main_loop_running.load(std::memory_order_acquire);
	const bool title_async  = !loop_running || Common::Gates::Value(Common::Gates::Knob::TitleAsync) != 0;
	const auto title_t0    = Common::FrameStats::NowNs();
	if (TestHidLossTitleOff()) [[unlikely]] {
		// Track F, F40a stand KYTY_TEST_HIDLOSS edition 2, mode pad (docs/track-f/f40a.md s0.6): no title post while the
		// pad probe window is open - the main thread is woken by the pad events only.
	} else if (title_async) {
		bool post = false;
		{
			Common::LockGuard lock(title_mutex);
			title_text   = std::move(text);
			post         = !title_queued;
			title_queued = true;
		}
		if (post) {
			PostToMainThread([this] {
				std::string latest;
				{
					Common::LockGuard lock(title_mutex);
					latest       = title_text;
					title_queued = false;
				}
				SDL_SetWindowTitle(window, latest.c_str());
			});
		}
	} else {
		RunOnMainThread([this, text = std::move(text)] { SDL_SetWindowTitle(window, text.c_str()); });
	}
	const auto title_ns = Common::FrameStats::NowNs() - title_t0;
	if (loop_running) {
		Common::FrameStats::Add(Common::FrameStats::Counter::PresTitleNs, title_ns);
		Common::FrameStats::Add(Common::FrameStats::Counter::PresTitleN, 1);
	}
	if (loop_running && title_ns >= 50000000ull) {
		static std::atomic<uint32_t> wait_logged {0};
		if (wait_logged.fetch_add(1, std::memory_order_relaxed) < 32) {
			LOGF("MainThreadWait: us=%llu frame=%llu titleasync=%d\n",
			     static_cast<unsigned long long>(title_ns / 1000), static_cast<unsigned long long>(frame_num),
			     title_async ? 1 : 0);
		}
	}
}

} // namespace Libs::Graphics
