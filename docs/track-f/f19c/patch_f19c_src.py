# F19c (HPP-547, ROADMAP s122 item 451(c)-(d)): KYTY_FIX_B24 (member A of F19a s5.1: guest pad output through a slot and
# the PadOutput thread) and the stand KYTY_TEST_HIDLOSS (detach / hold / sleep) - patch of src/libs/controller.h,
# src/libs/controller.cpp, src/graphics/presentation/window/window.cpp and CMakeLists.txt (target b24_pad_stand).
# Anchors are whole lines (or whole blocks of lines); every anchor must match exactly once. LF in, LF out (write_bytes).
# Usage: python patch_f19c_src.py <repo root>
import sys

ROOT = sys.argv[1].rstrip('/\\') + '/'


def load(rel):
    b = open(ROOT + rel, 'rb').read()
    assert b'\r' not in b, rel + ': CR found'
    return b.decode('utf-8')


def save(rel, text):
    open(ROOT + rel, 'wb').write(text.encode('utf-8'))


def once(text, old, rel):
    n = text.count(old)
    assert n == 1, '%s: anchor found %d times: %r' % (rel, n, old[:80])


def insert_after(text, anchor_lines, new, rel):
    old = anchor_lines + '\n'
    once(text, old, rel)
    return text.replace(old, old + new, 1)


def insert_before(text, anchor_lines, new, rel):
    old = anchor_lines + '\n'
    once(text, old, rel)
    return text.replace(old, new + old, 1)


def replace_block(text, old, new, rel):
    once(text, old, rel)
    return text.replace(old, new, 1)


# ---------------------------------------------------------------- controller.h
rel = 'src/libs/controller.h'
t = load(rel)
t = insert_after(t, 'void ResetInputState();', r'''// Track F, F19c (ROADMAP s122 item 451(d)): KYTY_FIX_B24 is on (read once in Initialize).
bool FixB24On();
// Track F, F19c stand KYTY_TEST_HIDLOSS (item 451(c), F19a s6.1): pad output counters of the stand window.
// TestHidLossWindow(true) zeroes them and starts counting, TestHidLossWindow(false) stops counting; outside the window a
// pad output call does one relaxed load of a static flag and nothing else.
struct HidLossPadStats {
	uint64_t pad_vib         = 0;
	uint64_t pad_led         = 0;
	uint64_t pad_trig        = 0;
	uint64_t pad_wait_max_us = 0;
	uint64_t po_applied      = 0;
	uint64_t po_wait_max_us  = 0;
	uint64_t guest_sdl       = 0;
};
void            TestHidLossWindow(bool open);
HidLossPadStats TestHidLossPadStats();
''', rel)
save(rel, t)

# ---------------------------------------------------------------- controller.cpp
rel = 'src/libs/controller.cpp'
t = load(rel)
t = insert_after(t, '#include "common/emulatorConfig.h"', '#include "common/envFlag.h"\n', rel)
t = insert_after(t, '#include <mutex>', '#include <condition_variable>\n#include <string>\n#include <thread>\n', rel)

t = insert_after(t, 'static_assert(sizeof(DualSenseEffects) == 32);', r'''
// Track F, F19c stand KYTY_TEST_HIDLOSS (ROADMAP s122 item 451(c), F19a s6.1): pad output counters of the stand window,
// opened and closed by the stand in window.cpp (TestHidLossWindow). Outside the window - always when the stand is unset -
// a guest pad output call does one relaxed load of g_hidloss_window and nothing else; no guest state is written.
static std::atomic<bool> g_hidloss_window {false};

struct HidLossCounters {
	std::atomic<uint64_t> pad_vib {0};
	std::atomic<uint64_t> pad_led {0};
	std::atomic<uint64_t> pad_trig {0};
	std::atomic<uint64_t> pad_wait_max_us {0};
	std::atomic<uint64_t> po_applied {0};
	std::atomic<uint64_t> po_wait_max_us {0};
	std::atomic<uint64_t> guest_sdl {0};
};

static HidLossCounters g_hidloss;

static uint64_t PadNowUs() {
	return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::microseconds>(
	                                 std::chrono::steady_clock::now().time_since_epoch())
	                                 .count());
}

static void PadAtomicMax(std::atomic<uint64_t>& value, uint64_t sample) {
	uint64_t current = value.load(std::memory_order_relaxed);
	while (sample > current && !value.compare_exchange_weak(current, sample, std::memory_order_relaxed)) {
	}
}

// One guest pad output call (SetVibration, SetLightBar, SetTriggerEffect) inside the stand window: counts the entry, the
// wall from entry to return (pad_wait_max_us) and every SDL call the function makes itself (guest_sdl).
class PadCallProbe {
public:
	explicit PadCallProbe(std::atomic<uint64_t>& kind): m_on(g_hidloss_window.load(std::memory_order_relaxed)) {
		if (m_on) {
			kind.fetch_add(1, std::memory_order_relaxed);
			m_start_us = PadNowUs();
		}
	}
	~PadCallProbe() {
		if (m_on) {
			PadAtomicMax(g_hidloss.pad_wait_max_us, PadNowUs() - m_start_us);
		}
	}

	KYTY_CLASS_NO_COPY(PadCallProbe);

	void Sdl() {
		if (m_on) {
			g_hidloss.guest_sdl.fetch_add(1, std::memory_order_relaxed);
		}
	}

private:
	bool     m_on;
	uint64_t m_start_us = 0;
};

void TestHidLossWindow(bool open) {
	if (open) {
		for (auto* counter: {&g_hidloss.pad_vib, &g_hidloss.pad_led, &g_hidloss.pad_trig, &g_hidloss.pad_wait_max_us,
		                     &g_hidloss.po_applied, &g_hidloss.po_wait_max_us, &g_hidloss.guest_sdl}) {
			counter->store(0, std::memory_order_relaxed);
		}
	}
	g_hidloss_window.store(open, std::memory_order_release);
}

HidLossPadStats TestHidLossPadStats() {
	HidLossPadStats stats;
	stats.pad_vib         = g_hidloss.pad_vib.load(std::memory_order_relaxed);
	stats.pad_led         = g_hidloss.pad_led.load(std::memory_order_relaxed);
	stats.pad_trig        = g_hidloss.pad_trig.load(std::memory_order_relaxed);
	stats.pad_wait_max_us = g_hidloss.pad_wait_max_us.load(std::memory_order_relaxed);
	stats.po_applied      = g_hidloss.po_applied.load(std::memory_order_relaxed);
	stats.po_wait_max_us  = g_hidloss.po_wait_max_us.load(std::memory_order_relaxed);
	stats.guest_sdl       = g_hidloss.guest_sdl.load(std::memory_order_relaxed);
	return stats;
}

// Track F, F19c (ROADMAP s122 item 451(d), member A of F19a s5.1): KYTY_FIX_B24 - unset, empty, 0/false/off/no: off
// (Common::EnvFlagOn). Written once by Initialize before the guest threads exist, only read afterwards. At 1 the guest's
// SetVibration, SetLightBar and SetTriggerEffect call no SDL: each puts the latest value of its kind into a slot of
// PadOutput under the slot's own short mutex (not GameController::m_mutex; a new value overwrites the old one, every
// kind has a generation counter) and wakes the one PadOutput thread of the process. PadOutput makes the same SDL calls
// as the path at 0, without GameController::m_mutex, for its copy of the active pad id, which CheckActive writes under
// GameController::m_mutex. The pad lookup and the call run under SDL_LockJoysticks (the lock every one of these SDL
// calls takes anyway; it is recursive), so a pad closed meanwhile by the removal handler (SDL_GameControllerClose takes
// the same lock) is never touched. PadOutput is stopped and joined by EmergencyShutdown before ReleaseHostPads.
static bool g_fix_b24 = false;

bool FixB24On() {
	return g_fix_b24;
}

class PadOutput {
public:
	PadOutput() = default;
	~PadOutput() { Stop(); }

	KYTY_CLASS_NO_COPY(PadOutput);

	void Start();
	void Stop();
	void SetActive(int id, bool ps5);
	void PostVibration(uint8_t large_motor, uint8_t small_motor);
	void PostLightBar(uint8_t r, uint8_t g, uint8_t b);
	// Returns the copy of "the active pad is a PS5 pad" - the *sent of SetTriggerEffect at KYTY_FIX_B24=1.
	bool PostTriggerEffect(const DualSenseEffects& effect);

private:
	void        Loop();
	static void ApplyVibration(int id, uint8_t large_motor, uint8_t small_motor);
	static void ApplyLightBar(int id, uint8_t r, uint8_t g, uint8_t b);
	static void ApplyTriggerEffect(int id, const DualSenseEffects& effect);

	// Everything below is guarded by m_mutex; m_thread is touched only by Start and Stop.
	std::mutex              m_mutex;
	std::condition_variable m_cv;
	std::thread             m_thread;
	bool                    m_stop          = false;
	int                     m_active_id     = -1;
	bool                    m_active_ps5    = false;
	uint64_t                m_vibration_gen = 0;
	uint64_t                m_light_bar_gen = 0;
	uint64_t                m_effect_gen    = 0;
	uint8_t                 m_vibration[2]  = {};
	uint8_t                 m_light_bar[3]  = {};
	DualSenseEffects        m_effect {};
};

static PadOutput* g_pad_output = nullptr;

void PadOutput::Start() {
	m_thread = std::thread([this] { Loop(); });
}

void PadOutput::Stop() {
	{
		std::lock_guard lock(m_mutex);
		m_stop = true;
	}
	m_cv.notify_all();
	if (m_thread.joinable()) {
		if (m_thread.get_id() == std::this_thread::get_id()) {
			m_thread.detach();
		} else {
			m_thread.join();
		}
	}
}

void PadOutput::SetActive(int id, bool ps5) {
	std::lock_guard lock(m_mutex);
	m_active_id  = id;
	m_active_ps5 = ps5;
}

void PadOutput::PostVibration(uint8_t large_motor, uint8_t small_motor) {
	{
		std::lock_guard lock(m_mutex);
		m_vibration[0] = large_motor;
		m_vibration[1] = small_motor;
		m_vibration_gen++;
	}
	m_cv.notify_one();
}

void PadOutput::PostLightBar(uint8_t r, uint8_t g, uint8_t b) {
	{
		std::lock_guard lock(m_mutex);
		m_light_bar[0] = r;
		m_light_bar[1] = g;
		m_light_bar[2] = b;
		m_light_bar_gen++;
	}
	m_cv.notify_one();
}

bool PadOutput::PostTriggerEffect(const DualSenseEffects& effect) {
	bool ps5 = false;
	{
		std::lock_guard lock(m_mutex);
		m_effect = effect;
		m_effect_gen++;
		ps5 = m_active_ps5;
	}
	m_cv.notify_one();
	return ps5;
}

// One application of a slot on the PadOutput thread; inside the stand window counts it and its wall.
template <typename Apply>
static void PadOutputApply(Apply&& apply) {
	const bool     on       = g_hidloss_window.load(std::memory_order_relaxed);
	const uint64_t start_us = on ? PadNowUs() : 0;
	apply();
	if (on) {
		g_hidloss.po_applied.fetch_add(1, std::memory_order_relaxed);
		PadAtomicMax(g_hidloss.po_wait_max_us, PadNowUs() - start_us);
	}
}

void PadOutput::Loop() {
	uint64_t vibration_done = 0;
	uint64_t light_bar_done = 0;
	uint64_t effect_done    = 0;

	std::unique_lock lock(m_mutex);
	for (;;) {
		m_cv.wait(lock, [&] {
			return m_stop || m_vibration_gen != vibration_done || m_light_bar_gen != light_bar_done ||
			       m_effect_gen != effect_done;
		});
		if (m_stop) {
			return;
		}
		const int              id        = m_active_id;
		const bool             vibration = m_vibration_gen != vibration_done;
		const bool             light_bar = m_light_bar_gen != light_bar_done;
		const bool             effect    = m_effect_gen != effect_done;
		const uint8_t          motor[2]  = {m_vibration[0], m_vibration[1]};
		const uint8_t          color[3]  = {m_light_bar[0], m_light_bar[1], m_light_bar[2]};
		const DualSenseEffects effects   = m_effect;
		vibration_done                   = m_vibration_gen;
		light_bar_done                   = m_light_bar_gen;
		effect_done                      = m_effect_gen;
		lock.unlock();

		if (vibration) {
			PadOutputApply([&] { ApplyVibration(id, motor[0], motor[1]); });
		}
		if (light_bar) {
			PadOutputApply([&] { ApplyLightBar(id, color[0], color[1], color[2]); });
		}
		if (effect) {
			PadOutputApply([&] { ApplyTriggerEffect(id, effects); });
		}

		lock.lock();
	}
}

// The SDL calls of GameController::SetVibration at KYTY_FIX_B24=0, for the given pad id, under SDL_LockJoysticks.
void PadOutput::ApplyVibration(int id, uint8_t large_motor, uint8_t small_motor) {
	if (id == HOST_INPUT_CONTROLLER_ID) {
		return;
	}
	bool        failed = false;
	std::string error;
	SDL_LockJoysticks();
	if (auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(id)); pad != nullptr) {
		const auto large = static_cast<uint16_t>(large_motor * 0x101U);
		const auto small = static_cast<uint16_t>(small_motor * 0x101U);
		if (SDL_GameControllerRumble(pad, large, small, RUMBLE_DURATION_MS) != 0) {
			failed = true;
			error  = SDL_GetError();
		}
	}
	SDL_UnlockJoysticks();
	if (failed) {
		LOGF("\t rumble failed: %s\n", error.c_str());
	}
}

// The SDL calls of GameController::SetLightBar at KYTY_FIX_B24=0.
void PadOutput::ApplyLightBar(int id, uint8_t r, uint8_t g, uint8_t b) {
	SDL_LockJoysticks();
	if (auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(id)); pad != nullptr) {
		(void)SDL_GameControllerSetLED(pad, r, g, b);
	}
	SDL_UnlockJoysticks();
}

// The SDL calls of GameController::SetTriggerEffect at KYTY_FIX_B24=0.
void PadOutput::ApplyTriggerEffect(int id, const DualSenseEffects& effect) {
	SDL_LockJoysticks();
	auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(id));
	if (pad != nullptr && SDL_GameControllerGetType(pad) == SDL_CONTROLLER_TYPE_PS5) {
		(void)SDL_GameControllerSendEffect(pad, &effect, sizeof(effect));
	}
	SDL_UnlockJoysticks();
}
''', rel)

# Initialize: KYTY_FIX_B24 is read once, PadOutput is created before the first Connect (CheckActive writes its copy).
t = insert_after(t, '\tEXIT_IF(g_controller != nullptr);\n', r'''	// Track F, F19c (ROADMAP s122 item 451(d)): KYTY_FIX_B24, read once here - before the guest threads exist.
	g_fix_b24 = Common::EnvFlagOn("KYTY_FIX_B24");
	if (g_fix_b24) {
		LOGF("FixB24: mode=1\n");
		g_pad_output = new PadOutput;
		g_pad_output->Start();
	}
''', rel)

t = insert_after(t, '\tdelete g_haptics;\n\tg_haptics = nullptr;', '\tdelete g_pad_output;\n\tg_pad_output = nullptr;\n', rel)

t = insert_before(t, '\tif (g_controller != nullptr) {\n\t\tg_controller->ReleaseHostPads();', r'''	// Track F, F19c (item 451(d)): PadOutput is stopped and joined before the host pads are released.
	if (g_pad_output != nullptr) {
		g_pad_output->Stop();
	}
''', rel)

t = insert_after(t, '\tm_orientation[3] = 1.0f;\n\tm_gyro_timestamp = 0;', r'''	if (g_pad_output != nullptr) {
		// Track F, F19c (item 451(d)): the PadOutput copy of the active pad id and of "the active pad is a PS5 pad"
		// (KYTY_FIX_B24=1 only; the caller holds m_mutex; no SDL call here - the type was read by Connect).
		g_pad_output->SetActive(m_active_id,
		                        std::find(m_ps5_ids.begin(), m_ps5_ids.end(), m_active_id) != m_ps5_ids.end());
	}
''', rel)

t = insert_after(t, '\tuint64_t         m_gyro_timestamp = 0;', r'''	// Track F, F19c (item 451(d)): connected ids whose pad is a PS5 pad (filled at KYTY_FIX_B24=1 only).
	std::vector<int> m_ps5_ids;
''', rel)

t = replace_block(t, r'''void GameController::Connect(int id) {
	Common::LockGuard lock(m_mutex);
''', r'''void GameController::Connect(int id) {
	// Track F, F19c (item 451(d)): at KYTY_FIX_B24=1 the pad type is read here, before m_mutex (Connect runs in
	// Initialize for the host input id and on the main thread right after SDL_GameControllerOpen), so no SDL call is made
	// under m_mutex; CheckActive copies "the active pad is a PS5 pad" from m_ps5_ids.
	bool ps5 = false;
	if (g_fix_b24 && id >= 0) {
		auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(id));
		ps5       = pad != nullptr && SDL_GameControllerGetType(pad) == SDL_CONTROLLER_TYPE_PS5;
	}
	Common::LockGuard lock(m_mutex);
''', rel)
t = insert_after(t, '\tm_connected_ids.push_back(id);', '\tif (ps5) {\n\t\tm_ps5_ids.push_back(id);\n\t}\n', rel)
t = insert_after(t, '\tm_connected_ids.erase(it);', '\tm_ps5_ids.erase(std::remove(m_ps5_ids.begin(), m_ps5_ids.end(), id), m_ps5_ids.end());\n', rel)
t = insert_after(t, '\tm_connected_ids.clear();', '\tm_ps5_ids.clear();\n', rel)

t = replace_block(t, r'''void GameController::SetVibration(uint8_t large_motor, uint8_t small_motor) {
	Common::LockGuard lock(m_mutex);

	if (m_active_id == HOST_INPUT_CONTROLLER_ID) {
		return;
	}
	auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));
	if (pad == nullptr) {
		return;
	}

	const auto large = static_cast<uint16_t>(large_motor * 0x101U);
	const auto small = static_cast<uint16_t>(small_motor * 0x101U);
	if (SDL_GameControllerRumble(pad, large, small, RUMBLE_DURATION_MS) != 0) {
		LOGF("\t rumble failed: %s\n", SDL_GetError());
	}
}

void GameController::SetLightBar(uint8_t r, uint8_t g, uint8_t b) {
	Common::LockGuard lock(m_mutex);
	if (auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));
	    pad != nullptr) {
		(void)SDL_GameControllerSetLED(pad, r, g, b);
	}
}

bool GameController::SetTriggerEffect(const PadTriggerEffectParam& param, bool* sent) {
	*sent = false;
''', r'''void GameController::SetVibration(uint8_t large_motor, uint8_t small_motor) {
	PadCallProbe probe(g_hidloss.pad_vib);
	if (g_fix_b24) {
		// Track F, F19c (item 451(d)): no SDL on the guest thread - the latest value goes to the PadOutput slot.
		g_pad_output->PostVibration(large_motor, small_motor);
		return;
	}

	Common::LockGuard lock(m_mutex);

	if (m_active_id == HOST_INPUT_CONTROLLER_ID) {
		return;
	}
	probe.Sdl();
	auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));
	if (pad == nullptr) {
		return;
	}

	const auto large = static_cast<uint16_t>(large_motor * 0x101U);
	const auto small = static_cast<uint16_t>(small_motor * 0x101U);
	probe.Sdl();
	if (SDL_GameControllerRumble(pad, large, small, RUMBLE_DURATION_MS) != 0) {
		probe.Sdl();
		LOGF("\t rumble failed: %s\n", SDL_GetError());
	}
}

void GameController::SetLightBar(uint8_t r, uint8_t g, uint8_t b) {
	PadCallProbe probe(g_hidloss.pad_led);
	if (g_fix_b24) {
		// Track F, F19c (item 451(d)): no SDL on the guest thread - the latest value goes to the PadOutput slot.
		g_pad_output->PostLightBar(r, g, b);
		return;
	}

	Common::LockGuard lock(m_mutex);
	probe.Sdl();
	if (auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));
	    pad != nullptr) {
		probe.Sdl();
		(void)SDL_GameControllerSetLED(pad, r, g, b);
	}
}

bool GameController::SetTriggerEffect(const PadTriggerEffectParam& param, bool* sent) {
	PadCallProbe probe(g_hidloss.pad_trig);
	*sent = false;
''', rel)

t = replace_block(t, r'''	if (effect.enable_bits == 0) {
		return true;
	}

	Common::LockGuard lock(m_mutex);
	auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));
	if (pad != nullptr && SDL_GameControllerGetType(pad) == SDL_CONTROLLER_TYPE_PS5) {
		*sent = SDL_GameControllerSendEffect(pad, &effect, sizeof(effect)) == 0;
	}
	return true;
}
''', r'''	if (effect.enable_bits == 0) {
		return true;
	}
	if (g_fix_b24) {
		// Track F, F19c (item 451(d)): no SDL on the guest thread - the effect goes to the PadOutput slot; *sent is
		// "the active pad is a PS5 pad and the effect is in the slot".
		*sent = g_pad_output->PostTriggerEffect(effect);
		return true;
	}

	Common::LockGuard lock(m_mutex);
	probe.Sdl();
	auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));
	if (pad != nullptr) {
		probe.Sdl();
	}
	if (pad != nullptr && SDL_GameControllerGetType(pad) == SDL_CONTROLLER_TYPE_PS5) {
		probe.Sdl();
		*sent = SDL_GameControllerSendEffect(pad, &effect, sizeof(effect)) == 0;
	}
	return true;
}
''', rel)
save(rel, t)

# ---------------------------------------------------------------- window.cpp
rel = 'src/graphics/presentation/window/window.cpp'
t = load(rel)
t = insert_after(t, '#include <cstdlib>', '#include <cmath>\n#include <cstring>\n', rel)

t = insert_before(t, 'static void GameEventController([[maybe_unused]] const EventController& f) {', r'''// Track F, F19c stand KYTY_TEST_HIDLOSS (ROADMAP s122 item 451(c), F19a s6.1): counters of the stand window - main
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

''', rel)

t = replace_block(t, r'''	if (f.removed) {
		Controller::Disconnect(f.id);
''', r'''	if (f.removed) {
		// Track F, F19c (ROADMAP s122 item 451(c)): printed always - without it a pad lost on the host leaves no line in
		// the log (the print above is a build option); one line on a rare event, nothing the guest sees.
		LOGF("Controller %d: removed\n", f.id);
		TestHidLossCount(g_test_hidloss.removed);
		Controller::Disconnect(f.id);
''', rel)

t = insert_before(t, '// Track F, F5 (ROADMAP s122 item 273(e)(2), MEASUREMENT ONLY): KYTY_TEST_MINIMIZE=<s>:<dur> - <s> seconds after the', r'''// Track F, F19c (ROADMAP s122 item 451(c), F19a s4): KYTY_TEST_HIDLOSS=<s>[:<mode>] - stand only, off when unset or
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
constexpr double   TEST_HIDLOSS_PRE_S    = 10.0;
constexpr uint32_t TEST_HIDLOSS_HOLD_MS  = 3000;
constexpr uint32_t TEST_HIDLOSS_PROBE_MS = 20;

enum class TestHidLossMode { Detach, Hold, Sleep };

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
	}
	return "?";
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
		} else {
			ok = false;
		}
	}
	if (!ok) {
		LOGF("TestHidLoss: config invalid value=\"%s\" (expected <s>[:detach|hold|sleep]), stand off\n", value);
		return c;
	}
	c.on      = true;
	c.delay_s = delay_s;
	c.mode    = mode;
	LOGF("TestHidLoss: config on delay_s=%g mode=%s hold_ms=%u\n", delay_s, TestHidLossModeName(mode),
	     TEST_HIDLOSS_HOLD_MS);
	return c;
}

static uint64_t TestHidLossNowUs() {
	return Common::FrameStats::NowNs() / 1000;
}

// Instance id of the attached virtual pad (-1: none); written and read on the main thread only.
static SDL_JoystickID g_test_hidloss_vp = -1;
// t_us of the "done" line, 0 until fire has finished; written by the main thread, read by the stand thread.
static std::atomic<uint64_t> g_test_hidloss_done_us {0};

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

// Main thread.
static void TestHidLossAttach() {
	SDL_VirtualJoystickDesc desc {};
	desc.version    = SDL_VIRTUAL_JOYSTICK_DESC_VERSION;
	desc.type       = SDL_JOYSTICK_TYPE_GAMECONTROLLER;
	desc.naxes      = 6;
	desc.nbuttons   = 15;
	desc.name       = "KYTY test pad";
	desc.Rumble     = TestHidLossVpRumble;
	desc.SetLED     = TestHidLossVpSetLed;
	desc.SendEffect = TestHidLossVpSendEffect;
	const int index = SDL_JoystickAttachVirtualEx(&desc);
	if (index < 0) {
		LOGF("TestHidLoss: attach failed error=\"%s\" t_us=%" PRIu64 "\n", SDL_GetError(), TestHidLossNowUs());
		return;
	}
	g_test_hidloss_vp = SDL_JoystickGetDeviceInstanceID(index);
	LOGF("TestHidLoss: attach index=%d t_us=%" PRIu64 "\n", index, TestHidLossNowUs());
}

// Main thread.
static void TestHidLossFire(TestHidLossMode mode) {
	LOGF("TestHidLoss: fire mode=%s t_us=%" PRIu64 "\n", TestHidLossModeName(mode), TestHidLossNowUs());
	switch (mode) {
		case TestHidLossMode::Detach: {
			int index = -1;
			for (int i = 0; g_test_hidloss_vp >= 0 && i < SDL_NumJoysticks(); i++) {
				if (SDL_JoystickGetDeviceInstanceID(i) == g_test_hidloss_vp) {
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
	if (!TestHidLossPost([] { TestHidLossAttach(); })) {
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
	std::thread([armed_us] { TestHidLossRun(cfg, armed_us); }).detach();
}

''', rel)

# The guest log text reaches the stand through the F5 entry point (libC.cpp fwrite -> WindowTestMinimizeNoteGuestText),
# so no other file changes; the call is the first statement, before the F5 early returns.
t = insert_after(t, 'void WindowTestMinimizeNoteGuestText(const char* text, size_t size) {',
                 '\tWindowTestHidLossNoteGuestText(text, size); // Track F, F19c, KYTY_TEST_HIDLOSS (item 451(c))\n', rel)
save(rel, t)

# ---------------------------------------------------------------- CMakeLists.txt
rel = 'CMakeLists.txt'
t = load(rel)
t = insert_after(t, 'add_kyty_full_emulator_test(shader_cfg_tests "${KYTY_TESTS_DIR}/shaderCfgTests.cpp")', r'''
# Track F, B24 pad output stand (F19c; ROADMAP s122 item 451(e)(1)): run by docs/track-f/f19c/run_stand_f19c.py, not by
# ctest.
add_kyty_full_emulator_test(b24_pad_stand
	"${KYTY_TESTS_DIR}/B24PadStand.cpp")
''', rel)
save(rel, t)
print('PATCH OK')
