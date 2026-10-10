#include "common/subsystems.h"

#include "common/envFlag.h"
#include "common/logging/log.h"
#include "common/threads.h"

#include <atomic>
#include <chrono>
#include <cinttypes>
#include <cstdio>
#include <thread>

namespace Common {

static Subsystems* g_active_subsystems = nullptr;

// Track F, F33c (HPP-744; ROADMAP s122 item 675(g)): KYTY_FIX_F21. The three flags below are written by InitFixF21 and
// SetEmergencyHook on the main thread before any other thread starts (the creation of every later thread orders them
// before its reads) and never after; g_f21_path = g_fix_f21 || g_f21_hook != nullptr - the one check of the FS11 path.
// At =1: g_f21_owner - Thread::GetThreadIdUnique of the first thread that entered EmergencyShutdownActive (0 - none;
// the id is >= 1 and never reused), g_f21_done - "the owner's walk is done" (store release after the walk, load acquire
// by the waiting threads), t_f21_expired - this thread's wait expired once, its later entries return at once.
static bool                  g_fix_f21  = false;
static EmergencyHook         g_f21_hook = nullptr;
static bool                  g_f21_path = false;
static std::atomic<uint64_t> g_f21_owner {0};
static std::atomic<bool>     g_f21_done {false};
static thread_local bool     t_f21_expired = false;

Subsystems::Subsystems(bool print): m_print(print) {
	m_active.reserve(16);
	g_active_subsystems = this;
}

Subsystems::~Subsystems() {
	Destroy();
	if (g_active_subsystems == this) {
		g_active_subsystems = nullptr;
	}
}

void Subsystems::Destroy() {
	for (auto it = m_active.rbegin(); it != m_active.rend(); ++it) {
		if (it->shutdown != nullptr) {
			it->shutdown();
		}
	}
	m_active.clear();
}

void Subsystems::EmergencyShutdown() {
	for (auto it = m_active.rbegin(); it != m_active.rend(); ++it) {
		if (it->emergency_shutdown != nullptr) {
			it->emergency_shutdown();
		}
	}
	m_active.clear();
}

void Subsystems::EmergencyShutdownActive() {
	if (g_f21_path) [[unlikely]] { // F33c: KYTY_FIX_F21=1 or the stand KYTY_TEST_EXITFATAL armed
		EmergencyShutdownActiveF21();
		return;
	}
	if (g_active_subsystems != nullptr) {
		g_active_subsystems->EmergencyShutdown();
	}
}

// F33c: KYTY_FIX_F21 (the flags - at the top of this file).
void Subsystems::InitFixF21() {
	g_fix_f21  = EnvFlagOn("KYTY_FIX_F21"); // unset, "", 0/false/off/no - OFF (the form of FS4a)
	g_f21_path = g_fix_f21 || g_f21_hook != nullptr;
}

void Subsystems::LogFixF21() {
	LOGF("FixF21: mode=%d wait_ms=%u\n", g_fix_f21 ? 1 : 0, kFixF21WaitMs);
}

bool Subsystems::FixF21On() {
	return g_fix_f21;
}

void Subsystems::SetEmergencyHook(EmergencyHook hook) {
	g_f21_hook = hook;
	g_f21_path = g_fix_f21 || g_f21_hook != nullptr;
}

// The FS11 loop of EmergencyShutdown with the observer calls (hook may be nullptr - then it is that loop).
void Subsystems::EmergencyWalkF21(EmergencyHook hook) {
	if (hook != nullptr) {
		hook(kEmergencyWalkBegin, 0, m_active.size());
	}
	size_t pos = 0;
	for (auto it = m_active.rbegin(); it != m_active.rend(); ++it, ++pos) {
		if (hook != nullptr) {
			hook(kEmergencyBeforeEntry, pos, 0);
		}
		if (it->emergency_shutdown != nullptr) {
			if (hook != nullptr) {
				hook(kEmergencyBeforeCallback, pos, 0);
			}
			it->emergency_shutdown();
		}
	}
	if (hook != nullptr) {
		hook(kEmergencyAfterLoop, pos, 0);
	}
	m_active.clear();
	if (hook != nullptr) {
		hook(kEmergencyAfterClear, pos, 0);
	}
}

// Every exit of this function is a return to the caller (DbgReport, DbgExit, at_quick_exit, KytyClose); no lock is
// taken, no logger call is made on the waiting path (the line is fprintf + fflush of stderr).
void Subsystems::EmergencyShutdownActiveF21() {
	const auto hook = g_f21_hook;
	if (hook != nullptr) {
		hook(kEmergencyEnter, 0, 0);
	}
	auto* active = g_active_subsystems;
	if (active == nullptr) {
		return;
	}
	if (!g_fix_f21) {
		// KYTY_FIX_F21=0 with the stand armed: the FS11 sequence - every entry walks - observed.
		active->EmergencyWalkF21(hook);
		return;
	}
	const auto self  = static_cast<uint64_t>(Thread::GetThreadIdUnique());
	uint64_t   owner = 0;
	if (g_f21_owner.compare_exchange_strong(owner, self, std::memory_order_acq_rel, std::memory_order_acquire)) {
		active->EmergencyWalkF21(hook);
		g_f21_done.store(true, std::memory_order_release);
		return;
	}
	if (owner == self) {
		// Re-entry of the owner thread (DbgExit after DbgReport, a fatal inside an emergency callback): no nested walk.
		if (hook != nullptr) {
			hook(kEmergencyReenter, 0, 0);
		}
		return;
	}
	if (g_f21_done.load(std::memory_order_acquire)) {
		if (hook != nullptr) {
			hook(kEmergencyDoneSeen, 0, 0);
		}
		return;
	}
	if (t_f21_expired) {
		if (hook != nullptr) {
			hook(kEmergencyExpiredSeen, 0, 0);
		}
		return;
	}
	if (hook != nullptr) {
		hook(kEmergencyWaitBegin, 0, 0);
	}
	const auto start = std::chrono::steady_clock::now();
	const auto limit = start + std::chrono::milliseconds(kFixF21WaitMs);
	for (;;) {
		const bool done = g_f21_done.load(std::memory_order_acquire);
		const auto now  = std::chrono::steady_clock::now();
		const auto waited_us =
		    static_cast<size_t>(std::chrono::duration_cast<std::chrono::microseconds>(now - start).count());
		if (done) {
			if (hook != nullptr) {
				hook(kEmergencyWaitDone, waited_us, 0);
			}
			return;
		}
		if (now >= limit) {
			t_f21_expired = true;
			std::fprintf(stderr, "FixF21: wait_expired tid=%" PRIu64 " waited_ms=%" PRIu64 "\n", self,
			             static_cast<uint64_t>(waited_us / 1000u));
			std::fflush(stderr);
			if (hook != nullptr) {
				hook(kEmergencyWaitExpired, waited_us, 0);
			}
			return;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
	}
}

} // namespace Common
