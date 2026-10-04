// Track F, B24 stand without the game (F19c HPP-547, ROADMAP s122 item 451(e)(1)): the guest pad output of
// src/libs/controller.cpp (GameController through PadSetVibration / PadSetLightBar / PadSetTriggerEffect - linked from
// the emulator sources of this build, not copied) against the SDL joystick lock. The pad is an SDL virtual pad
// (SDL_JoystickAttachVirtualEx, game controller type), opened as a game controller and connected the way the emulator's
// controller add event does it (window.cpp GameEventController: SDL_GameControllerOpen, Controller::Connect; removal:
// Controller::Disconnect, SDL_GameControllerClose). SDL2 is 3rdparty/SDL2 of the same build; the host joystick drivers are
// switched off by hints before SDL_InitSubSystem (HIDAPI, RawInput, WGI, XInput, DirectInput), so no host input device
// is opened - the line num_joysticks_at_init (0 expected) checks it. KYTY_FIX_B24 (read by controller.cpp once per
// process in Controller::Initialize) selects the path. Separate CMake target b24_pad_stand (EXCLUDE_FROM_ALL, no
// add_test - not in the default ctest set); the driver is docs/track-f/f19c/run_stand_f19c.py, which runs one process per
// case and decides PASS/FAIL from the printed values.
//
// Usage: b24_pad_stand <case>
//   i   - thread X holds SDL_LockJoysticks 3000 ms; 200 ms after X has it, thread Y calls PadSetVibration with new
//         values: wall_vib_us.
//   ii  - the same, thread Y calls PadSetVibration, PadSetLightBar, PadSetTriggerEffect (walls) and two more
//         PadSetVibration with new values; after X unlocks - the time until the virtual pad's Rumble callback holds the
//         last written value (latency_us), and that value again 300 ms later.
//   iii - 2 threads x 10 000 PadSetVibration with random values while the main thread attaches and detaches the virtual
//         pad and handles the add / remove events as the emulator does; every value the Rumble callback receives must
//         have been written (or be 0/0); then, with the pad attached and connected, one more value is written and must be
//         the last one the callback receives (latency_us, and again 300 ms later).
// Every case: the pad output counters of controller.cpp are counted (TestHidLossWindow) and printed; at the end
// Controller::EmergencyShutdown (PadOutput stop and join, ReleaseHostPads). Output: "key=value" lines; "END" last.
// Exit 0 unless the arguments are bad (2) or SDL fails to start (4).
#define SDL_MAIN_HANDLED
#include "SDL.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "libs/controller.h"

#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <string>
#include <thread>

namespace Libs::Controller {

// The guest parameter layouts of src/libs/controller.cpp (the header declares them only); the same definitions.
struct PadLightBarParam {
	uint8_t r;
	uint8_t g;
	uint8_t b;
	uint8_t reserve;
};

struct PadVibrationParam {
	uint8_t large_motor;
	uint8_t small_motor;
};

struct PadTriggerEffectCommand {
	uint32_t mode;
	uint8_t  reserve[4];
	uint8_t  data[48];
};

struct PadTriggerEffectParam {
	uint8_t                 trigger_mask;
	uint8_t                 reserve[7];
	PadTriggerEffectCommand command[2];
};

static_assert(sizeof(PadTriggerEffectCommand) == 56);
static_assert(sizeof(PadTriggerEffectParam) == 120);

} // namespace Libs::Controller

namespace {

namespace Controller = Libs::Controller;

constexpr int      PAD_HANDLE      = 1;
constexpr uint32_t HOLD_MS         = 3000;
constexpr uint32_t Y_DELAY_MS      = 200;
constexpr uint8_t  FINAL_LARGE     = 0xAB;
constexpr uint8_t  FINAL_SMALL     = 0xCD;
constexpr int      WRITES          = 10000;
constexpr int      WRITE_SPIN_US   = 50;

uint64_t NowUs() {
	return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::microseconds>(
	                                 std::chrono::steady_clock::now().time_since_epoch())
	                                 .count());
}

// Rumble callback state of the virtual pad: the last value as (low << 16) | high in SDL units, its time, counts.
std::atomic<uint32_t> g_rumble_last {0xffffffffu};
std::atomic<uint64_t> g_rumble_calls {0};
std::atomic<uint64_t> g_rumble_bad {0};
std::atomic<uint64_t> g_led_calls {0};
std::atomic<uint64_t> g_effect_calls {0};
// Values written by the stand (case iii): index large << 8 | small.
std::atomic<bool> g_written[65536];

uint32_t Packed(uint8_t large, uint8_t small_motor) {
	return (static_cast<uint32_t>(large * 0x101U) << 16) | static_cast<uint32_t>(small_motor * 0x101U);
}

int SDLCALL VpRumble(void* /*userdata*/, Uint16 low, Uint16 high) {
	const uint8_t large = static_cast<uint8_t>(low >> 8);
	const uint8_t small_motor = static_cast<uint8_t>(high >> 8);
	const bool    exact = low == large * 0x101U && high == small_motor * 0x101U;
	if (!exact || !(g_written[(large << 8) | small_motor].load() || (low == 0 && high == 0))) {
		g_rumble_bad.fetch_add(1);
	}
	g_rumble_last.store((static_cast<uint32_t>(low) << 16) | high);
	g_rumble_calls.fetch_add(1);
	return 0;
}

int SDLCALL VpSetLed(void* /*userdata*/, Uint8 /*red*/, Uint8 /*green*/, Uint8 /*blue*/) {
	g_led_calls.fetch_add(1);
	return 0;
}

int SDLCALL VpSendEffect(void* /*userdata*/, const void* /*data*/, int /*size*/) {
	g_effect_calls.fetch_add(1);
	return 0;
}

SDL_JoystickID g_vp_instance  = -1; // main thread only
int            g_connected_id = -1; // main thread only
int            g_adds         = 0;
int            g_removes      = 0;
int            g_attaches     = 0;
int            g_detaches     = 0;

bool Attach() {
	SDL_VirtualJoystickDesc desc {};
	desc.version    = SDL_VIRTUAL_JOYSTICK_DESC_VERSION;
	desc.type       = SDL_JOYSTICK_TYPE_GAMECONTROLLER;
	desc.naxes      = 6;
	desc.nbuttons   = 15;
	desc.name       = "KYTY test pad";
	desc.Rumble     = VpRumble;
	desc.SetLED     = VpSetLed;
	desc.SendEffect = VpSendEffect;
	const int index = SDL_JoystickAttachVirtualEx(&desc);
	if (index < 0) {
		std::printf("attach_failed=\"%s\"\n", SDL_GetError());
		return false;
	}
	g_vp_instance = SDL_JoystickGetDeviceInstanceID(index);
	g_attaches++;
	return true;
}

bool Detach() {
	for (int i = 0; g_vp_instance >= 0 && i < SDL_NumJoysticks(); i++) {
		if (SDL_JoystickGetDeviceInstanceID(i) == g_vp_instance) {
			if (SDL_JoystickDetachVirtual(i) != 0) {
				std::printf("detach_failed=\"%s\"\n", SDL_GetError());
				return false;
			}
			g_vp_instance = -1;
			g_detaches++;
			return true;
		}
	}
	return false;
}

// The controller events, handled as window.cpp GameEventController does.
void Pump() {
	SDL_Event e;
	while (SDL_PollEvent(&e) != 0) {
		if (e.type == SDL_CONTROLLERDEVICEADDED) {
			auto* pad = SDL_GameControllerOpen(e.cdevice.which);
			if (pad == nullptr) {
				std::printf("open_failed=\"%s\"\n", SDL_GetError());
				continue;
			}
			const int id = SDL_JoystickInstanceID(SDL_GameControllerGetJoystick(pad));
			Controller::Connect(id);
			g_connected_id = id;
			g_adds++;
		} else if (e.type == SDL_CONTROLLERDEVICEREMOVED) {
			Controller::Disconnect(e.cdevice.which);
			SDL_GameControllerClose(SDL_GameControllerFromInstanceID(e.cdevice.which));
			if (g_connected_id == e.cdevice.which) {
				g_connected_id = -1;
			}
			g_removes++;
		}
	}
}

// Attach and pump until the pad is connected (Controller::Connect done); false after 2 s.
bool AttachConnected() {
	if (g_vp_instance < 0 && !Attach()) {
		return false;
	}
	const uint64_t t0 = NowUs();
	while (NowUs() - t0 < 2000000) {
		Pump();
		if (g_connected_id >= 0 && g_connected_id == g_vp_instance) {
			return true;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
	}
	return false;
}

void Vibrate(uint8_t large, uint8_t small_motor) {
	g_written[(large << 8) | small_motor].store(true);
	Controller::PadVibrationParam p {large, small_motor};
	Controller::PadSetVibration(PAD_HANDLE, &p);
}

// Waits up to 1 s for the Rumble callback to hold the value; returns the time it was seen (0 if never).
uint64_t WaitRumble(uint32_t value) {
	const uint64_t t0 = NowUs();
	while (NowUs() - t0 < 1000000) {
		if (g_rumble_last.load() == value) {
			return NowUs();
		}
		std::this_thread::sleep_for(std::chrono::microseconds(200));
	}
	return 0;
}

void SpinUs(int us) {
	const uint64_t t0 = NowUs();
	while (NowUs() - t0 < static_cast<uint64_t>(us)) {
	}
}

void PrintStats() {
	const auto s = Controller::TestHidLossPadStats();
	std::printf("pad_vib=%llu\npad_led=%llu\npad_trig=%llu\npad_wait_max_us=%llu\npo_applied=%llu\npo_wait_max_us=%llu\n"
	            "guest_sdl=%llu\n",
	            static_cast<unsigned long long>(s.pad_vib), static_cast<unsigned long long>(s.pad_led),
	            static_cast<unsigned long long>(s.pad_trig), static_cast<unsigned long long>(s.pad_wait_max_us),
	            static_cast<unsigned long long>(s.po_applied), static_cast<unsigned long long>(s.po_wait_max_us),
	            static_cast<unsigned long long>(s.guest_sdl));
	std::printf("rumble_calls=%llu\nrumble_bad=%llu\nled_calls=%llu\neffect_calls=%llu\n",
	            static_cast<unsigned long long>(g_rumble_calls.load()), static_cast<unsigned long long>(g_rumble_bad.load()),
	            static_cast<unsigned long long>(g_led_calls.load()), static_cast<unsigned long long>(g_effect_calls.load()));
}

// Cases i and ii: X holds the joystick lock HOLD_MS, Y makes the guest calls Y_DELAY_MS after X has the lock.
void HoldCase(bool all_kinds) {
	std::atomic<bool> locked {false};
	std::atomic<uint64_t> unlock_us {0};
	std::thread x([&] {
		SDL_LockJoysticks();
		locked.store(true);
		std::this_thread::sleep_for(std::chrono::milliseconds(HOLD_MS));
		unlock_us.store(NowUs());
		SDL_UnlockJoysticks();
	});
	while (!locked.load()) {
		std::this_thread::yield();
	}
	std::this_thread::sleep_for(std::chrono::milliseconds(Y_DELAY_MS));
	uint64_t wall_vib = 0;
	uint64_t wall_led = 0;
	uint64_t wall_trig = 0;
	bool     trig_ok = false;
	uint32_t last = 0;
	std::thread y([&] {
		uint64_t t0 = NowUs();
		Vibrate(0x11, 0x22);
		wall_vib = NowUs() - t0;
		last     = Packed(0x11, 0x22);
		if (!all_kinds) {
			return;
		}
		Controller::PadLightBarParam led {10, 20, 30, 0};
		t0 = NowUs();
		Controller::PadSetLightBar(PAD_HANDLE, &led);
		wall_led = NowUs() - t0;
		Controller::PadTriggerEffectParam trig {};
		trig.trigger_mask       = 0x01;
		trig.command[0].mode    = 1;
		trig.command[0].data[0] = 2;
		trig.command[0].data[1] = 5;
		t0 = NowUs();
		trig_ok   = Controller::PadSetTriggerEffect(PAD_HANDLE, &trig) == 0;
		wall_trig = NowUs() - t0;
		Vibrate(0x33, 0x44);
		Vibrate(0x55, 0x66);
		last = Packed(0x55, 0x66);
	});
	y.join();
	const uint64_t y_done_us = NowUs();
	x.join();
	std::printf("wall_vib_us=%llu\n", static_cast<unsigned long long>(wall_vib));
	if (all_kinds) {
		std::printf("wall_led_us=%llu\nwall_trig_us=%llu\ntrig_ok=%d\n", static_cast<unsigned long long>(wall_led),
		            static_cast<unsigned long long>(wall_trig), trig_ok ? 1 : 0);
		std::printf("y_done_before_unlock=%d\n", y_done_us < unlock_us.load() ? 1 : 0);
		const uint64_t seen = WaitRumble(last);
		std::printf("latency_us=%lld\n", seen == 0 ? -1LL : static_cast<long long>(seen - unlock_us.load()));
		std::this_thread::sleep_for(std::chrono::milliseconds(300));
		std::printf("last_after_300ms_ok=%d\n", g_rumble_last.load() == last ? 1 : 0);
	}
}

void ChurnCase() {
	std::atomic<int>  running {2};
	std::atomic<bool> go {false};
	std::atomic<int>  writes {0};
	const auto        writer = [&](uint32_t seed) {
		std::mt19937 rng(seed);
		while (!go.load()) {
			std::this_thread::yield();
		}
		for (int n = 0; n < WRITES; n++) {
			uint8_t large = 0;
			uint8_t small_motor = 0;
			do {
				const uint32_t r = rng();
				large       = static_cast<uint8_t>(r);
				small_motor = static_cast<uint8_t>(r >> 8);
			} while (large == FINAL_LARGE && small_motor == FINAL_SMALL);
			Vibrate(large, small_motor);
			writes.fetch_add(1);
			SpinUs(WRITE_SPIN_US);
		}
		running.fetch_sub(1);
	};
	std::thread a(writer, 1u);
	std::thread b(writer, 2u);
	go.store(true);
	int cycles = 0;
	while (running.load() != 0) {
		if (g_vp_instance >= 0) {
			Detach();
		} else {
			Attach();
		}
		Pump();
		cycles++;
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
	}
	a.join();
	b.join();
	std::printf("writes=%d\nchurn_cycles=%d\n", writes.load(), cycles);
	const bool connected = AttachConnected();
	std::printf("final_connected=%d\n", connected ? 1 : 0);
	std::this_thread::sleep_for(std::chrono::milliseconds(200));
	const uint64_t t0 = NowUs();
	Vibrate(FINAL_LARGE, FINAL_SMALL);
	const uint64_t seen = WaitRumble(Packed(FINAL_LARGE, FINAL_SMALL));
	std::printf("latency_us=%lld\n", seen == 0 ? -1LL : static_cast<long long>(seen - t0));
	std::this_thread::sleep_for(std::chrono::milliseconds(300));
	std::printf("last_after_300ms_ok=%d\n", g_rumble_last.load() == Packed(FINAL_LARGE, FINAL_SMALL) ? 1 : 0);
	std::printf("attaches=%d\ndetaches=%d\nadds=%d\nremoves=%d\n", g_attaches, g_detaches, g_adds, g_removes);
}

} // namespace

int main(int argc, char** argv) {
	if (argc != 2 || (std::strcmp(argv[1], "i") != 0 && std::strcmp(argv[1], "ii") != 0 && std::strcmp(argv[1], "iii") != 0)) {
		std::fprintf(stderr, "usage: b24_pad_stand i|ii|iii\n");
		return 2;
	}
	const std::string mode = argv[1];

	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction = Config::LogDirection::Console;
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();

	// Host joystick drivers off: only the virtual driver is left.
	SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI, "0");
	SDL_SetHint(SDL_HINT_JOYSTICK_RAWINPUT, "0");
	SDL_SetHint(SDL_HINT_JOYSTICK_WGI, "0");
	SDL_SetHint(SDL_HINT_XINPUT_ENABLED, "0");
	SDL_SetHint(SDL_HINT_DIRECTINPUT_ENABLED, "0");
	if (SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER) < 0) {
		std::printf("sdl_init_failed=\"%s\"\nEND\n", SDL_GetError());
		std::fflush(stdout);
		return 4;
	}
	std::printf("case=%s\n", mode.c_str());
	std::printf("num_joysticks_at_init=%d\n", SDL_NumJoysticks());

	Controller::Initialize();
	std::printf("fix_b24=%d\n", Controller::FixB24On() ? 1 : 0);
	Controller::TestHidLossWindow(true);

	const bool connected = AttachConnected();
	std::printf("connected=%d\n", connected ? 1 : 0);
	if (connected) {
		if (mode == "iii") {
			ChurnCase();
		} else {
			HoldCase(mode == "ii");
		}
	}
	Controller::TestHidLossWindow(false);
	PrintStats();
	Controller::EmergencyShutdown();
	std::printf("shutdown_ok=1\n");
	Log::Flush();
	std::printf("END\n");
	std::fflush(stdout);
	// No SDL_Quit and no subsystem teardown, as the emulator.
	std::_Exit(0);
}
