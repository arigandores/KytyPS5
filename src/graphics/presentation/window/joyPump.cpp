#include "graphics/presentation/window/joyPump.h"

#include "common/common.h" // KYTY_PLATFORM

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX // before the first <windows.h> (SDL_syswm.h includes it too)
#endif
#include <windows.h> // MsgWaitForMultipleObjectsEx, PeekMessage of JoyPump's own thread; the stand probes
#endif

#include "SDL.h"
#include "SDL_error.h"
#include "SDL_gamecontroller.h"
#include "SDL_joystick.h"
#include "SDL_syswm.h"
#include "SDL_thread.h"
#include "common/envFlag.h"
#include "common/logging/log.h"
#include "libs/controller.h"

#include <atomic>
#include <chrono>
#include <cinttypes>
#include <condition_variable>
#include <deque>
#include <mutex>
#include <set>
#include <thread>
#include <algorithm>
#include <utility>
#include <vector>

namespace Libs::Graphics::JoyPump {

namespace {

constexpr uint32_t JP_OPEN_MS          = 1;       // wait with an open pad (SDL EVENT_POLL_INTERVAL_MS)
constexpr uint32_t JP_IDLE_MS          = 250;     // wait without (lead decision, item 692(v)(2))
constexpr uint32_t T_JP_MS             = 2000;    // stop limit (item 692(v)(6))
constexpr uint64_t PUMP_UPDATE_LONG_US = 1000000; // "FixF24: pump_update_long" from 1 s
constexpr uint32_t LINE_LIMIT          = 32;

// Written once by ReadKnob on the main thread; read by any thread (the emergency sequence may run on a thread created
// before WindowCreate - PadOutput, haptics), hence atomic.
std::atomic<bool> g_enabled {false};

uint64_t NowUs() {
	return static_cast<uint64_t>(
	    std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());
}

void AtomicMax(std::atomic<uint64_t>& value, uint64_t sample) {
	uint64_t current = value.load(std::memory_order_relaxed);
	while (sample > current && !value.compare_exchange_weak(current, sample, std::memory_order_relaxed)) {
	}
}

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
// F40a2 (RC1 of F40b, ROADMAP s122 item 696(b)(1)): the OS thread that owns the first message-only window of class cls
// of this process (FindWindowExW(HWND_MESSAGE) by class, GetWindowThreadProcessId, own process id only - any process on
// SDL2 has windows of the same classes); 0 - none found.
uint64_t OwnerOfMessageWindow(const wchar_t* cls) {
	const DWORD self = GetCurrentProcessId();
	HWND        hwnd = nullptr;
	for (int i = 0; i < 4096; i++) {
		hwnd = FindWindowExW(HWND_MESSAGE, hwnd, cls, nullptr);
		if (hwnd == nullptr) {
			return 0;
		}
		DWORD       pid = 0;
		const DWORD tid = GetWindowThreadProcessId(hwnd, &pid);
		if (pid == self) {
			return tid;
		}
	}
	return 0;
}
#endif

// F40a2 (RC1 of F40b): on JoyPump after a successful SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER), before the main thread
// resumes. hid - SDL_HIDAPI_DEVICE_DETECTION (HIDAPI discovery), helper - SDLHelperWindowInputCatcher (SDL helper window,
// DirectInput cooperative level), msg - Message (Windows joystick driver device notification); pump - this thread, main -
// the thread that called Start; all are OS thread ids (GetCurrentThreadId), comparable with the window owners.
void LogInitOwner(uint64_t main_os_tid) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	const uint64_t hid    = OwnerOfMessageWindow(L"SDL_HIDAPI_DEVICE_DETECTION");
	const uint64_t helper = OwnerOfMessageWindow(L"SDLHelperWindowInputCatcher");
	const uint64_t msg    = OwnerOfMessageWindow(L"Message");
	const uint64_t pump   = GetCurrentThreadId();
#else
	const uint64_t hid    = 0;
	const uint64_t helper = 0;
	const uint64_t msg    = 0;
	const uint64_t pump   = 0;
#endif
	LOGF("FixF24: init_owner hid=%" PRIu64 " helper=%" PRIu64 " msg=%" PRIu64 " pump=%" PRIu64 " main=%" PRIu64 "\n", hid,
	     helper, msg, pump, main_os_tid);
}

bool LineAllowed(std::atomic<uint32_t>& counter) {
	return counter.fetch_add(1, std::memory_order_relaxed) < LINE_LIMIT;
}

class Pump {
public:
	Pump() = default;

	KYTY_CLASS_NO_COPY(Pump);

	bool Start(uint64_t main_tid, std::string* error);
	void Post(std::function<void()> task);
	void Stop();
	[[nodiscard]] bool Exited() const {
		return !m_started.load(std::memory_order_acquire) || m_exited.load(std::memory_order_acquire);
	}
	[[nodiscard]] int OpenPads() const { return m_open_pads.load(std::memory_order_relaxed); }
	void              Close(int instance_id);

	// Stand.
	std::atomic<bool>     m_stand_window {false};
	std::atomic<uint64_t> m_stand_update_max_us {0};
	std::atomic<uint64_t> m_stand_tasks {0};
	std::atomic<uint64_t> m_stand_open_failed {0};
	std::atomic<uint32_t> m_stand_task_delay_ms {0};
	// Flap arm scan gap (F40a2, RC2 of F40b): m_stand_scan_last_us and m_stand_scan_gap_max_us are guarded by
	// m_stand_scan_mutex; m_stand_scan_on - one relaxed load per JoyPump scan when the stand is off.
	std::atomic<bool> m_stand_scan_on {false};
	std::mutex        m_stand_scan_mutex;
	uint64_t          m_stand_scan_last_us    = 0;
	uint64_t          m_stand_scan_gap_max_us = 0;
	void              StandScanMark();

private:
	struct Task {
		uint64_t              posted_us = 0;
		std::function<void()> fn;
	};

	void ThreadMain(uint64_t main_tid);
	void Loop();
	void RunTasks();
	void PumpMessages();
	void Wait(uint32_t timeout_ms);
	void Wake();
	void ScanAndOpen();
	void OpenOne(SDL_GameController* pad);
	[[nodiscard]] bool Stopping() const { return m_stop.load(std::memory_order_acquire); }

	// Guarded by m_mutex: m_thread (moved out once by Stop), m_tasks, m_init_*, m_signal (non-Windows wait).
	std::mutex              m_mutex;
	std::condition_variable m_cv; // init done, thread end, non-Windows wake
	std::thread             m_thread;
	std::deque<Task>        m_tasks;
	bool                    m_init_done = false;
	bool                    m_init_ok   = false;
	std::string             m_init_error;
#if KYTY_PLATFORM != KYTY_PLATFORM_WINDOWS
	bool m_signal = false;
#endif
	std::atomic<bool>       m_started {false};
	std::atomic<bool>       m_exited {false};
	std::atomic<bool>       m_stop {false};
	std::atomic<int>        m_open_pads {0};
	uint64_t                m_main_os_tid = 0; // written by Start before the thread, read by JoyPump
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	HANDLE m_event = nullptr; // auto-reset: a task or the stop; created by Start before the thread
#endif
	// JoyPump thread only: instance ids already handled by the scan (opened or not).
	std::set<SDL_JoystickID> m_seen;
	std::atomic<uint32_t>    m_open_failed_lines {0};
	std::atomic<uint32_t>    m_long_lines {0};
};

// Never destroyed: no joinable std::thread at static destruction (a normal exit() after an expired stop).
Pump& P() {
	static auto* pump = new Pump;
	return *pump;
}

bool Pump::Start(uint64_t main_tid, std::string* error) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	m_event = CreateEventW(nullptr, FALSE, FALSE, nullptr);
	m_main_os_tid = GetCurrentThreadId(); // F40a2 (RC1 of F40b): the main thread, OS id
#endif
	{
		std::lock_guard lock(m_mutex);
		m_started.store(true, std::memory_order_release);
		m_thread = std::thread([this, main_tid] { ThreadMain(main_tid); });
	}
	std::unique_lock lock(m_mutex);
	m_cv.wait(lock, [this] { return m_init_done; });
	if (!m_init_ok && error != nullptr) {
		*error = m_init_error;
	}
	return m_init_ok;
}

void Pump::ThreadMain(uint64_t main_tid) {
	const auto pump_tid = static_cast<uint64_t>(SDL_ThreadID());
	SDL_ClearError();
	// Item 692(v)(1): the line is written by the thread that runs the initialization, with its id at the call.
	LOGF("FixF24: init tid=%" PRIu64 " pump tid=%" PRIu64 " main tid=%" PRIu64 "\n", static_cast<uint64_t>(SDL_ThreadID()),
	     pump_tid, main_tid);
	const bool ok = SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER) == 0;
	if (ok) {
		LogInitOwner(m_main_os_tid); // F40a2 (RC1 of F40b): before the main thread resumes
	}
	{
		std::lock_guard lock(m_mutex);
		m_init_done = true;
		m_init_ok   = ok;
		if (!ok) {
			m_init_error = SDL_GetError();
		}
	}
	m_cv.notify_all();
	if (ok) {
		Loop();
	}
	{
		std::lock_guard lock(m_mutex);
		m_exited.store(true, std::memory_order_release);
	}
	m_cv.notify_all();
}

// RC4 (s0.4): the stop flag is checked before every task, after every SDL_JoystickUpdate and before every Controller
// call of the scan; once it is up nothing else runs and the function returns.
void Pump::Loop() {
	for (;;) {
		RunTasks();
		if (Stopping()) {
			return;
		}
		PumpMessages();
		const uint64_t start_us = NowUs();
		SDL_JoystickUpdate();
		const uint64_t wall_us = NowUs() - start_us;
		if (Stopping()) {
			return;
		}
		if (m_stand_window.load(std::memory_order_relaxed)) {
			AtomicMax(m_stand_update_max_us, wall_us);
		}
		if (wall_us >= PUMP_UPDATE_LONG_US && LineAllowed(m_long_lines)) {
			LOGF("FixF24: pump_update_long us=%" PRIu64 "\n", wall_us);
		}
		StandScanMark(); // F40a2 (RC2 of F40b): the start of the scan, stand only
		ScanAndOpen();
		if (Stopping()) {
			return;
		}
		Wait(m_open_pads.load(std::memory_order_relaxed) > 0 ? JP_OPEN_MS : JP_IDLE_MS);
	}
}

void Pump::RunTasks() {
	for (;;) {
		if (Stopping()) {
			return;
		}
		std::function<void()> fn;
		{
			std::lock_guard lock(m_mutex);
			if (m_tasks.empty()) {
				return;
			}
			const uint64_t delay_us = static_cast<uint64_t>(m_stand_task_delay_ms.load(std::memory_order_relaxed)) * 1000;
			if (delay_us != 0 && NowUs() < m_tasks.front().posted_us + delay_us) {
				return; // stand flap arm: the head is not due yet (the wait of this loop is 1 ms with a pad open)
			}
			fn = std::move(m_tasks.front().fn);
			m_tasks.pop_front();
		}
		fn();
		if (m_stand_window.load(std::memory_order_relaxed)) {
			m_stand_tasks.fetch_add(1, std::memory_order_relaxed);
		}
	}
}

// The messages of JoyPump's own thread: the windows of the joystick drivers created here (HIDAPI detection, Windows
// device notification and its timers, the SDL helper window) and the COM apartment of this thread (s0.1).
void Pump::PumpMessages() {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	MSG msg {};
	while (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE) != 0) {
		TranslateMessage(&msg);
		DispatchMessageW(&msg);
	}
#endif
}

void Pump::Wait(uint32_t timeout_ms) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	(void)MsgWaitForMultipleObjectsEx(1, &m_event, timeout_ms, QS_ALLINPUT, MWMO_INPUTAVAILABLE);
#else
	std::unique_lock lock(m_mutex);
	m_cv.wait_for(lock, std::chrono::milliseconds(timeout_ms), [this] { return m_signal; });
	m_signal = false;
#endif
}

void Pump::Wake() {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	if (m_event != nullptr) {
		SetEvent(m_event);
	}
#else
	{
		std::lock_guard lock(m_mutex);
		m_signal = true;
	}
	m_cv.notify_all();
#endif
}

void Pump::Post(std::function<void()> task) {
	{
		std::lock_guard lock(m_mutex);
		if (!m_started.load(std::memory_order_acquire) || Stopping()) {
			return;
		}
		m_tasks.push_back(Task {NowUs(), std::move(task)});
	}
	Wake();
}

// RC2 (s0.4): opening by instance id after JoyPump's own SDL_JoystickUpdate. The index is used under SDL_LockJoysticks
// only (the list cannot change meanwhile); Controller::Connect runs outside the lock (lock order m_mutex -> joystick lock
// of ReleaseHostPads and of the KYTY_FIX_B24=0 guest path).
void Pump::ScanAndOpen() {
	std::vector<SDL_GameController*> opened;
	SDL_LockJoysticks();
	const int count = SDL_NumJoysticks();
	for (int index = 0; index < count; index++) {
		const SDL_JoystickID id = SDL_JoystickGetDeviceInstanceID(index);
		if (id < 0 || !m_seen.insert(id).second) {
			continue;
		}
		if (SDL_IsGameController(index) != SDL_TRUE) {
			continue; // the same set as the SDL_CONTROLLERDEVICEADDED events of the FS12 path
		}
		auto* pad = SDL_GameControllerOpen(index);
		if (pad == nullptr) {
			if (m_stand_window.load(std::memory_order_relaxed)) {
				m_stand_open_failed.fetch_add(1, std::memory_order_relaxed);
			}
			if (LineAllowed(m_open_failed_lines)) {
				LOGF("FixF24: open failed instance=%d error=\"%s\"\n", static_cast<int>(id), SDL_GetError());
			}
			continue;
		}
		m_open_pads.fetch_add(1, std::memory_order_relaxed);
		opened.push_back(pad);
	}
	SDL_UnlockJoysticks();
	for (auto* pad: opened) {
		if (Stopping()) {
			return;
		}
		OpenOne(pad);
	}
}

// The FS12 add block (window.cpp GameEventController) after SDL_GameControllerOpen, on JoyPump; the same line text.
void Pump::OpenOne(SDL_GameController* pad) {
	const int id = SDL_JoystickInstanceID(SDL_GameControllerGetJoystick(pad));
	for (const auto sensor: {SDL_SENSOR_ACCEL, SDL_SENSOR_GYRO}) {
		if (SDL_GameControllerHasSensor(pad, sensor) == SDL_TRUE &&
		    SDL_GameControllerSetSensorEnabled(pad, sensor, SDL_TRUE) != 0) {
			LOGF("Controller %d: sensor %d enable failed: %s\n", id, static_cast<int>(sensor), SDL_GetError());
		}
	}
	LOGF("Controller %d: \"%s\" type=%d accel=%d gyro=%d path=%s\n", id, SDL_GameControllerName(pad),
	     static_cast<int>(SDL_GameControllerGetType(pad)),
	     SDL_GameControllerIsSensorEnabled(pad, SDL_SENSOR_ACCEL) == SDL_TRUE ? 1 : 0,
	     SDL_GameControllerIsSensorEnabled(pad, SDL_SENSOR_GYRO) == SDL_TRUE ? 1 : 0,
	     SDL_GameControllerPath(pad) != nullptr ? SDL_GameControllerPath(pad) : "");
	if (Stopping()) {
		return;
	}
	Controller::Connect(id);
	// A removal posted by another thread (the stand, a WGI callback) after the scan released the lock may already have
	// been handled by the main thread before this Connect: the pad is gone - undo the Connect here (s0.4).
	if (SDL_GameControllerGetAttached(pad) != SDL_TRUE && !Stopping()) {
		Controller::Disconnect(id);
	}
}

// Stand flap arm (F40a2, RC2 of F40b): a ScanAndOpen start of JoyPump inside [StandScanGapBegin; StandScanGapEnd].
void Pump::StandScanMark() {
	if (!m_stand_scan_on.load(std::memory_order_relaxed)) {
		return;
	}
	const uint64_t now = NowUs();
	std::lock_guard lock(m_stand_scan_mutex);
	if (!m_stand_scan_on.load(std::memory_order_relaxed) || now < m_stand_scan_last_us) {
		return; // the window ended (or restarted) between the load and the lock
	}
	m_stand_scan_gap_max_us = std::max(m_stand_scan_gap_max_us, now - m_stand_scan_last_us);
	m_stand_scan_last_us    = now;
}

// JoyPump task posted by the main thread's removal handler (Controller::Disconnect is done there).
void Pump::Close(int instance_id) {
	auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(instance_id));
	if (pad != nullptr) {
		SDL_GameControllerClose(pad);
		m_open_pads.fetch_sub(1, std::memory_order_relaxed);
	}
}

void Pump::Stop() {
	m_stop.store(true, std::memory_order_seq_cst);
	Wake();
	std::thread thread;
	{
		std::lock_guard lock(m_mutex);
		thread = std::move(m_thread);
	}
	if (!thread.joinable()) {
		return; // never started, or another call owns the thread
	}
	if (thread.get_id() == std::this_thread::get_id()) {
		thread.detach(); // the emergency sequence runs on JoyPump itself: the flag is enough
		return;
	}
	bool exited = false;
	{
		std::unique_lock lock(m_mutex);
		exited = m_cv.wait_for(lock, std::chrono::milliseconds(T_JP_MS),
		                       [this] { return m_exited.load(std::memory_order_acquire); });
	}
	if (exited) {
		thread.join();
		return;
	}
	LOGF("FixF24: pump_stop_expired t_jp_ms=%u\n", T_JP_MS);
	thread.detach();
}

std::atomic<uint32_t> g_add_lines {0};

} // namespace

void ReadKnob() {
	static std::atomic<bool> done {false};
	if (done.exchange(true)) {
		return;
	}
	// Track F, FS14a (HPP-812, ROADMAP s122 item 710(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
	// other value as EnvValueOn (the form of FS13a 3630f116 / FS12a cbfe8375).
	const char* value = std::getenv("KYTY_FIX_F24");
	g_enabled.store(value == nullptr || value[0] == '\0' || Common::EnvValueOn(value), std::memory_order_release);
	LOGF("FixF24: mode=%d b24=%d\n", Enabled() ? 1 : 0, Controller::FixB24On() ? 1 : 0);
}

bool Enabled() {
	return g_enabled.load(std::memory_order_acquire);
}

bool Start(uint64_t main_tid, std::string* error) {
	return P().Start(main_tid, error);
}

int OpenPads() {
	return P().OpenPads();
}

void PostClose(int instance_id) {
	P().Post([instance_id] { P().Close(instance_id); });
}

void NoteAddEvent(int index) {
	if (LineAllowed(g_add_lines)) {
		LOGF("FixF24: add event index=%d\n", index);
	}
}

void Post(std::function<void()> task) {
	P().Post(std::move(task));
}

void Stop() {
	P().Stop();
}

bool Exited() {
	return P().Exited();
}

void StandWindow(bool open) {
	auto& p = P();
	if (open) {
		p.m_stand_update_max_us.store(0, std::memory_order_relaxed);
		p.m_stand_tasks.store(0, std::memory_order_relaxed);
		p.m_stand_open_failed.store(0, std::memory_order_relaxed);
	}
	p.m_stand_window.store(open, std::memory_order_release);
}

StandStats StandRead() {
	auto&      p = P();
	StandStats s;
	s.update_max_us = p.m_stand_update_max_us.load(std::memory_order_relaxed);
	s.tasks         = p.m_stand_tasks.load(std::memory_order_relaxed);
	s.open_failed   = p.m_stand_open_failed.load(std::memory_order_relaxed);
	return s;
}

// F40a2 (RC2 of F40b): the stand thread, flap arm. Begin - just before the first attach; End - just after the last
// detach: the longest stretch of the window without a ScanAndOpen start (the edges count: begin to the first start, the
// last start to end). At KYTY_FIX_F24=0 (no JoyPump) both do nothing and End returns 0.
void StandScanGapBegin() {
	if (!Enabled()) {
		return;
	}
	auto&           p = P();
	std::lock_guard lock(p.m_stand_scan_mutex);
	p.m_stand_scan_last_us    = NowUs();
	p.m_stand_scan_gap_max_us = 0;
	p.m_stand_scan_on.store(true, std::memory_order_relaxed);
}

uint64_t StandScanGapEnd() {
	if (!Enabled()) {
		return 0;
	}
	auto&           p = P();
	std::lock_guard lock(p.m_stand_scan_mutex);
	if (!p.m_stand_scan_on.load(std::memory_order_relaxed)) {
		return 0;
	}
	p.m_stand_scan_on.store(false, std::memory_order_relaxed);
	const uint64_t now = NowUs();
	return std::max(p.m_stand_scan_gap_max_us, now > p.m_stand_scan_last_us ? now - p.m_stand_scan_last_us : 0);
}

void StandTaskDelayMs(uint32_t ms) {
	P().m_stand_task_delay_ms.store(ms, std::memory_order_relaxed);
}

uintptr_t StandWindowHandle(SDL_Window* window) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	SDL_SysWMinfo info {};
	SDL_VERSION(&info.version);
	if (window != nullptr && SDL_GetWindowWMInfo(window, &info) == SDL_TRUE) {
		return reinterpret_cast<uintptr_t>(info.info.win.window);
	}
#else
	(void)window;
#endif
	return 0;
}

// lParam of WM_KEYDOWN / WM_KEYUP: repeat 1, scan code 0x64 (SDL maps it to SDL_SCANCODE_F13), up - previous state and
// transition bits.
bool StandPostKey(uintptr_t hwnd, bool down) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	const auto lparam = static_cast<LPARAM>(1u | (0x64u << 16u) | (down ? 0u : ((1u << 30u) | (1u << 31u))));
	return hwnd != 0 && PostMessageW(reinterpret_cast<HWND>(hwnd), down ? WM_KEYDOWN : WM_KEYUP, VK_F13, lparam) != 0;
#else
	(void)hwnd;
	(void)down;
	return false;
#endif
}

bool StandIsHung(uintptr_t hwnd) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	return hwnd != 0 && IsHungAppWindow(reinterpret_cast<HWND>(hwnd)) != 0;
#else
	(void)hwnd;
	return false;
#endif
}

} // namespace Libs::Graphics::JoyPump
