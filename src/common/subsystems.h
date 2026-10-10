#ifndef KYTY_COMMON_SUBSYSTEMS_H_
#define KYTY_COMMON_SUBSYSTEMS_H_

#include "common/common.h"

#include <cstdio>
#include <vector>
#include <cstddef>
#include <cstdint>

namespace Common {

// Track F, F33c (HPP-744; ROADMAP s122 item 675(g), (d)(1)): the observer of the emergency sequence for the stand
// KYTY_TEST_EXITFATAL (src/emulator.cpp); nullptr unless the stand set it with Subsystems::SetEmergencyHook. It is called
// only on the F21 path of EmergencyShutdownActive (KYTY_FIX_F21=1 or the stand armed); the FS11 path never calls it.
// Events: walk begin (size = entries), before the entry <index> (counted from the end), before that entry's emergency
// callback, after the loop (index = entries walked), after clear; and on entry to EmergencyShutdownActive: enter,
// re-entry of the owner thread (returned without a walk), the walk already done (returned), wait begin, wait done
// (index = waited microseconds), wait expired (index = waited microseconds), a later entry of a thread whose wait expired.
enum EmergencyEvent : int {
	kEmergencyWalkBegin      = 0,
	kEmergencyBeforeEntry    = 1,
	kEmergencyAfterLoop      = 2,
	kEmergencyAfterClear     = 3,
	kEmergencyBeforeCallback = 4,
	kEmergencyEnter          = 5,
	kEmergencyReenter        = 6,
	kEmergencyDoneSeen       = 7,
	kEmergencyWaitBegin      = 8,
	kEmergencyWaitDone       = 9,
	kEmergencyWaitExpired    = 10,
	kEmergencyExpiredSeen    = 11,
};
using EmergencyHook = void (*)(int event, size_t index, size_t size);

class Subsystems {
public:
	using Callback = void (*)();

	explicit Subsystems(bool print = false);
	~Subsystems();

	template <typename Lifecycle>
	void Initialize() {
		Lifecycle::initialize();
		m_active.push_back({ShutdownCallback<Lifecycle>(), EmergencyCallback<Lifecycle>()});
		if (m_print) {
			std::printf("Initialized: %s\n", Lifecycle::name);
		}
	}

	void Destroy();
	void EmergencyShutdown();

	static void EmergencyShutdownActive();

	// Track F, F33c (HPP-744; ROADMAP s122 item 675(g)): KYTY_FIX_F21 (default 0). InitFixF21 reads the knob once - on
	// the main thread before any other thread starts (Emulator::Run, before Init); LogFixF21 prints "FixF21: mode=<0|1>"
	// once after Log::Initialize. At =1 EmergencyShutdownActive has one owner: the first thread that enters walks
	// m_active and publishes "the walk is done"; a re-entry of the owner thread returns at once; any other thread does not
	// walk - it waits for "done" at most kFixF21WaitMs and returns. At =0 (and without the stand) EmergencyShutdownActive
	// is the FS11 code plus one check of a static flag. SetEmergencyHook - the stand KYTY_TEST_EXITFATAL only, same
	// thread and time as InitFixF21.
	static constexpr uint32_t kFixF21WaitMs = 12000; // T of item 675(v)(2)
	static void               InitFixF21();
	static void               LogFixF21();
	static bool               FixF21On();
	static void               SetEmergencyHook(EmergencyHook hook);

	KYTY_CLASS_NO_COPY(Subsystems);

private:
	template <typename Lifecycle>
	static consteval Callback ShutdownCallback() {
		if constexpr (requires { Lifecycle::shutdown; }) {
			return Lifecycle::shutdown;
		}
		return nullptr;
	}

	template <typename Lifecycle>
	static consteval Callback EmergencyCallback() {
		if constexpr (requires { Lifecycle::emergency_shutdown; }) {
			return Lifecycle::emergency_shutdown;
		}
		return nullptr;
	}

	// F33c: the F21 path of EmergencyShutdownActive and its walk (the FS11 loop with the observer calls).
	static void EmergencyShutdownActiveF21();
	void        EmergencyWalkF21(EmergencyHook hook);

	struct Entry {
		Callback shutdown;
		Callback emergency_shutdown;
	};

	std::vector<Entry> m_active;
	bool               m_print;
};

} // namespace Common

#endif /* KYTY_COMMON_SUBSYSTEMS_H_ */
