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
//
// F19c2 (HPP-559, ROADMAP s122 item 460(v)(2), (4)) - two more cases; driver docs/track-f/f19c2/run_stand_f19c2.py:
//   dd   - KYTY_FIX_B24=1, RC1 of the F19d review: X holds SDL_LockJoysticks DD_HOLD_MS; one PadSetVibration puts
//          PadOutput into its application (it waits for the lock); DD_WRITE_MS later two threads released by one barrier
//          call Controller::EmergencyShutdown at the same time; "both_returned=1" when both came back; then
//          Controller::Shutdown (a third EmergencyShutdown and the deletes). One cycle per process.
//   trig - the trigger effect path (N2 of F19d): the virtual pad has vendor_id 0x054C / product_id 0x0CE6 (pad_type is
//          the SDL_GameControllerGetType value, pad_type_ps5 whether it is SDL_CONTROLLER_TYPE_PS5); X holds the lock
//          HOLD_MS, Y calls PadSetTriggerEffect with effect A then effect B Y_DELAY_MS after X has it (walls); after the
//          unlock - the SendEffect count, and the last payload compared with the payload of B sent again with the lock
//          free (A sent again too: the two payloads must differ). "sent=" is in the PadTriggerEffect: lines.
// A crash of a stand process (std::terminate, abort) prints terminate=1 / abort=1 and exits 3 without a dialog.
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
#include <csignal>
#include <cstring>
#include <exception>
#include <mutex>
#include <random>
#include <string>
#include <thread>
#include <vector>

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
// F19c2: the last SendEffect payload of the virtual pad; vendor / product of the next attach (0 - as F19c).
std::mutex           g_effect_mutex;
std::vector<uint8_t> g_effect_last;
Uint16               g_vp_vendor  = 0;
Uint16               g_vp_product = 0;
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

int SDLCALL VpSendEffect(void* /*userdata*/, const void* data, int size) {
	{
		std::lock_guard lock(g_effect_mutex);
		const auto*     bytes = static_cast<const uint8_t*>(data);
		g_effect_last.assign(bytes, bytes + (size > 0 ? size : 0));
	}
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
	desc.vendor_id  = g_vp_vendor;
	desc.product_id = g_vp_product;
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

// F19c2: a crash is counted by the driver - a marker line and exit 3, no dialog (the std::terminate handler is per
// thread in the MSVC runtime: every stand thread that calls into controller.cpp sets it).
[[noreturn]] void OnTerminate() {
	std::printf("terminate=1\n");
	std::fflush(stdout);
	std::_Exit(3);
}

void OnAbort(int /*sig*/) {
	std::printf("abort=1\n");
	std::fflush(stdout);
	std::_Exit(3);
}

void InstallCrashMarkers() {
#ifdef _MSC_VER
	_set_abort_behavior(0, _WRITE_ABORT_MSG | _CALL_REPORTFAULT);
#endif
	std::signal(SIGABRT, OnAbort);
	std::set_terminate(OnTerminate);
}

constexpr uint32_t DD_HOLD_MS  = 300;
constexpr uint32_t DD_WRITE_MS = 20;

// Case dd (F19c2, item 460(v)(2)).
void DoubleShutdownCase() {
	std::atomic<bool>     locked {false};
	std::atomic<uint64_t> unlock_us {0};
	std::thread           x([&] {
		std::set_terminate(OnTerminate);
		SDL_LockJoysticks();
		locked.store(true);
		std::this_thread::sleep_for(std::chrono::milliseconds(DD_HOLD_MS));
		unlock_us.store(NowUs());
		SDL_UnlockJoysticks();
	});
	while (!locked.load()) {
		std::this_thread::yield();
	}
	Vibrate(0x12, 0x34);
	std::this_thread::sleep_for(std::chrono::milliseconds(DD_WRITE_MS));
	std::atomic<int>  ready {0};
	std::atomic<bool> go {false};
	uint64_t          start[2] = {};
	uint64_t          done[2]  = {};
	const auto        caller   = [&](int k) {
		std::set_terminate(OnTerminate);
		ready.fetch_add(1);
		while (!go.load()) {
		}
		start[k] = NowUs();
		Controller::EmergencyShutdown();
		done[k] = NowUs();
	};
	std::thread a(caller, 0);
	std::thread b(caller, 1);
	while (ready.load() != 2) {
		std::this_thread::yield();
	}
	go.store(true);
	a.join();
	b.join();
	x.join();
	std::printf("both_returned=1\n");
	const uint64_t first = start[0] < start[1] ? start[0] : start[1];
	const uint64_t last  = start[0] < start[1] ? start[1] : start[0];
	std::printf("call_a_wall_us=%llu\ncall_b_wall_us=%llu\nstart_skew_us=%llu\ncalls_started_before_unlock=%d\n",
				static_cast<unsigned long long>(done[0] - start[0]), static_cast<unsigned long long>(done[1] - start[1]),
				static_cast<unsigned long long>(last - first), last < unlock_us.load() ? 1 : 0);
}

std::vector<uint8_t> EffectLast() {
	std::lock_guard lock(g_effect_mutex);
	return g_effect_last;
}

// Waits up to 1 s for the SendEffect count to reach n; returns the time it was seen (0 if never).
uint64_t WaitEffects(uint64_t n) {
	const uint64_t t0 = NowUs();
	while (NowUs() - t0 < 1000000) {
		if (g_effect_calls.load() >= n) {
			return NowUs();
		}
		std::this_thread::sleep_for(std::chrono::microseconds(200));
	}
	return 0;
}

// Effect A - left trigger, effect B - right trigger (mode 1, as case ii): different payloads.
Controller::PadTriggerEffectParam TriggerParam(bool right) {
	Controller::PadTriggerEffectParam p {};
	const int                         k = right ? 1 : 0;
	p.trigger_mask                      = right ? 0x02 : 0x01;
	p.command[k].mode                   = 1;
	p.command[k].data[0]                = right ? 3 : 2;
	p.command[k].data[1]                = right ? 7 : 5;
	return p;
}

// Case trig (F19c2, item 460(v)(4)).
void TriggerCase() {
	auto* pad = SDL_GameControllerFromInstanceID(g_connected_id);
	const int type = pad != nullptr ? static_cast<int>(SDL_GameControllerGetType(pad)) : -1;
	std::printf("pad_vendor=0x%04x\npad_product=0x%04x\npad_type=%d\npad_type_ps5=%d\n",
				pad != nullptr ? SDL_GameControllerGetVendor(pad) : 0, pad != nullptr ? SDL_GameControllerGetProduct(pad) : 0,
				type, type == static_cast<int>(SDL_CONTROLLER_TYPE_PS5) ? 1 : 0);
	const auto a_param = TriggerParam(false);
	const auto b_param = TriggerParam(true);
	std::atomic<bool>     locked {false};
	std::atomic<uint64_t> unlock_us {0};
	std::atomic<uint64_t> calls_before_unlock {0};
	std::thread           x([&] {
		SDL_LockJoysticks();
		locked.store(true);
		std::this_thread::sleep_for(std::chrono::milliseconds(HOLD_MS));
		calls_before_unlock.store(g_effect_calls.load());
		unlock_us.store(NowUs());
		SDL_UnlockJoysticks();
	});
	while (!locked.load()) {
		std::this_thread::yield();
	}
	std::this_thread::sleep_for(std::chrono::milliseconds(Y_DELAY_MS));
	uint64_t wall_a = 0;
	uint64_t wall_b = 0;
	bool     ok_a   = false;
	bool     ok_b   = false;
	std::thread y([&] {
		std::set_terminate(OnTerminate);
		uint64_t t0 = NowUs();
		ok_a        = Controller::PadSetTriggerEffect(PAD_HANDLE, &a_param) == 0;
		wall_a      = NowUs() - t0;
		t0          = NowUs();
		ok_b        = Controller::PadSetTriggerEffect(PAD_HANDLE, &b_param) == 0;
		wall_b      = NowUs() - t0;
	});
	y.join();
	const uint64_t y_done_us = NowUs();
	x.join();
	const uint64_t seen = WaitEffects(1);
	std::this_thread::sleep_for(std::chrono::milliseconds(300));
	const uint64_t             calls_after = g_effect_calls.load();
	const std::vector<uint8_t> last        = EffectLast();
	// The payloads of A and B with the lock free (the reference for "last applied = last written").
	Controller::PadTriggerEffectParam ref = a_param;
	Controller::PadSetTriggerEffect(PAD_HANDLE, &ref);
	const bool                 seen_a = WaitEffects(calls_after + 1) != 0;
	const std::vector<uint8_t> pa     = EffectLast();
	ref                               = b_param;
	Controller::PadSetTriggerEffect(PAD_HANDLE, &ref);
	const bool                 seen_b = WaitEffects(calls_after + 2) != 0;
	const std::vector<uint8_t> pb     = EffectLast();
	std::printf("wall_trig_a_us=%llu\nwall_trig_b_us=%llu\ntrig_ok=%d\ny_done_before_unlock=%d\n",
				static_cast<unsigned long long>(wall_a), static_cast<unsigned long long>(wall_b), ok_a && ok_b ? 1 : 0,
				y_done_us < unlock_us.load() ? 1 : 0);
	std::printf("effect_calls_before_unlock=%llu\neffect_calls_after_unlock=%llu\neffect_latency_us=%lld\n",
				static_cast<unsigned long long>(calls_before_unlock.load()), static_cast<unsigned long long>(calls_after),
				seen == 0 ? -1LL : static_cast<long long>(seen - unlock_us.load()));
	std::printf("ref_seen=%d\npayload_size=%d\nlast_eq_b=%d\na_ne_b=%d\n", seen_a && seen_b ? 1 : 0,
				static_cast<int>(last.size()), !last.empty() && last == pb ? 1 : 0, pa != pb ? 1 : 0);
}

} // namespace

int main(int argc, char** argv) {
	if (argc != 2 || (std::strcmp(argv[1], "i") != 0 && std::strcmp(argv[1], "ii") != 0 && std::strcmp(argv[1], "iii") != 0 &&
					  std::strcmp(argv[1], "dd") != 0 && std::strcmp(argv[1], "trig") != 0)) {
		std::fprintf(stderr, "usage: b24_pad_stand i|ii|iii|dd|trig\n");
		return 2;
	}
	const std::string mode = argv[1];
	InstallCrashMarkers();

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

	if (mode == "trig") {
		g_vp_vendor  = 0x054C;
		g_vp_product = 0x0CE6;
	}
	const bool connected = AttachConnected();
	std::printf("connected=%d\n", connected ? 1 : 0);
	if (connected) {
		if (mode == "iii") {
			ChurnCase();
		} else if (mode == "dd") {
			DoubleShutdownCase();
		} else if (mode == "trig") {
			TriggerCase();
		} else {
			HoldCase(mode == "ii");
		}
	}
	Controller::TestHidLossWindow(false);
	PrintStats();
	if (mode == "dd") {
		// F19c2: the two emergency exits already ran - the normal teardown (a third EmergencyShutdown, the deletes).
		Controller::Shutdown();
	} else {
		Controller::EmergencyShutdown();
	}
	std::printf("shutdown_ok=1\n");
	Log::Flush();
	std::printf("END\n");
	std::fflush(stdout);
	// No SDL_Quit and no subsystem teardown, as the emulator.
	std::_Exit(0);
}
