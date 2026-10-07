// Track F, B27 stand without the game (F24a HPP-658, ROADMAP s122 item 593(d)(1)): the slot protocol of the draw
// lookahead at knob "daslot" 1 (KYTY_DRAW_AHEAD_SLOT, the default): the producer (QueueAheadSource, serialised by
// ahead_queue_mutex, both probe slots under GuardSlot), the draw (AheadTake, TryGuardSlot, Ready -> Taking under the
// guard, the result read without it) and the workers (AheadRun: Queued -> Running by compare-exchange, Ready/Failed
// published, the guard never taken) - src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp.
//
// What is the code here and what is a model: the guard primitives between the VERBATIM markers are a copy of the text of
// pipelineCache.cpp (docs/track-f/f24a/check_b27_copy.py compares it with the file at a commit); the struct ProgramCache
// that owns the slot table is private to that file and needs the whole shader pipeline, so the transitions are a model
// that follows its lines in their order (the line numbers of 707e0d7d are given at each step). Keys and results are
// integers built so that a torn or foreign key or result is visible (Key()).
//
// Threads: 2 producers (one at a time, like ahead_queue_mutex), 2 draws (the game has one, GuestGpu; two is a superset),
// 4 workers - 8. In each window of the protocol a thread gives its quantum away (SwitchToThread) with probability 1/16.
// Invariants (each failure counted):
//   I1 - one guard holder: the owner word set right after the guard is taken is free, and still ours before UnguardSlot;
//   I2 - a worker that claimed a Queued slot reads a whole key (no producer writes it while Running);
//   I3 - a draw that moved a Ready slot to Taking reads the result of the key it matched, and the key did not move;
//   I4 - a Taking slot is still Taking when its draw publishes it;
//   I5 - a Running slot is still Running when its worker publishes it.
// Usage: b27_daslot_stand <inject> <takes per draw thread> <seed>
//   inject none | draw_noguard (the draw takes the slot without TryGuardSlot) | producer_noguard (the producer probes and
//   writes without GuardSlot) - the last two are the positive controls (an introduced race).
// Output: one line "B27 inject=... threads=8 takes=<n> hits=<n> late=<n> I1=<n> I2=<n> I3=<n> I4=<n> I5=<n> ..." and
// exit 0; "STALL" and exit 3 when the run does not end in 300 s.
#include "common/frameStats.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>
#include <vector>

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#undef min
#undef max

namespace {

enum AheadState : uint8_t { AheadEmpty, AheadQueued, AheadRunning, AheadReady, AheadFailed, AheadTaking };

constexpr uint32_t USER_MAX = 8;

struct AheadSlot {
	std::atomic<uint8_t> state {AheadEmpty};
	std::atomic<uint8_t> guard {0};
	uint8_t              taken = 0;
	// key (producer, under the slot guard)
	uint64_t                         fingerprint = 0;
	uint64_t                         shader_base = 0;
	uint64_t                         generation  = 0;
	uint64_t                         walk        = 0;
	uint32_t                         uses        = 0;
	uint32_t                         count       = 0;
	std::array<uint32_t, USER_MAX>   user_data {};
	// result (worker, published by the state)
	uint64_t result_tag = 0;
	uint64_t result_key = 0;
	// stand only: I1
	std::atomic<uint32_t> owner {0};

	[[nodiscard]] bool Matches(uint64_t key_fingerprint, uint64_t base, uint64_t key_generation, uint32_t key_count,
	                           const uint32_t* key_user_data) const {
		return fingerprint == key_fingerprint && shader_base == base && generation == key_generation && count == key_count &&
		       std::equal(key_user_data, key_user_data + key_count, user_data.begin());
	}
};

struct Guards {
	// BEGIN VERBATIM pipelineCache.cpp
	// Slot guards: the draw gives up after a bounded spin (a miss); the producer waits.
	static bool TryGuardSlot(AheadSlot& slot) {
		for (int spin = 0; spin < 64; spin++) {
			if (slot.guard.load(std::memory_order_relaxed) == 0 &&
			    slot.guard.exchange(1, std::memory_order_acquire) == 0) {
				return true;
			}
			YieldProcessor();
		}
		return false;
	}
	// Session 112: the producer spins, and after 256 spins gives its quantum away (the guard holder - a draw - may
	// have been preempted inside its few-instruction window); da_guard_yield counts those.
	static void GuardSlot(AheadSlot& slot) {
		uint32_t spin = 0;
		while (slot.guard.load(std::memory_order_relaxed) != 0 || slot.guard.exchange(1, std::memory_order_acquire) != 0) {
			if (++spin < 256) {
				YieldProcessor();
			} else {
				spin = 0;
				Common::FrameStats::Add(Common::FrameStats::Counter::DaGuardYield, 1);
				SwitchToThread();
			}
		}
	}
	static void UnguardSlot(AheadSlot& slot) {
		slot.guard.store(0, std::memory_order_release);
	}
	// END VERBATIM pipelineCache.cpp
};

constexpr size_t   SLOT_COUNT = 64; // the game has 32768; a small table makes every probe pair contended
constexpr uint64_t GENERATION = 1;
constexpr uint32_t KEY_SPACE  = 160;

std::atomic<uint64_t> g_fail[6];
std::atomic<uint64_t> g_takes {0};
std::atomic<uint64_t> g_hits {0};
std::atomic<uint64_t> g_late {0};
std::atomic<uint64_t> g_misses {0};
std::atomic<uint64_t> g_runs {0};
std::atomic<uint64_t> g_queued {0};
std::atomic<uint64_t> g_yields {0};
std::atomic<bool>     g_stop {false};
std::atomic<uint64_t> g_walk_published {1}; // the newest walk a producer finished (draws take keys of recent walks)

int g_inject = 0; // 0 none, 1 draw_noguard, 2 producer_noguard

std::array<AheadSlot, SLOT_COUNT> g_slots;
std::mutex                        g_queue_mutex; // ahead_queue_mutex
uint64_t                          g_ahead_walk  = 0;
uint64_t                          g_ahead_fresh = 0;
std::mutex                        g_ring_mutex; // ahead_mutex
std::condition_variable           g_ring_cv;
std::vector<uint32_t>             g_ring;
size_t                            g_ring_head = 0;

thread_local uint64_t t_rng = 0;
thread_local uint32_t t_me  = 0;

uint64_t Rng() {
	t_rng ^= t_rng << 13u;
	t_rng ^= t_rng >> 7u;
	t_rng ^= t_rng << 17u;
	return t_rng;
}

uint64_t Mix(uint64_t value) {
	value += 0x9e3779b97f4a7c15ull;
	value = (value ^ (value >> 30u)) * 0xbf58476d1ce4e5b9ull;
	value = (value ^ (value >> 27u)) * 0x94d049bb133111ebull;
	return value ^ (value >> 31u);
}

// A window of the protocol: give the quantum away with probability 1/16.
void Window() {
	if ((Rng() & 15u) == 0) {
		g_yields.fetch_add(1, std::memory_order_relaxed);
		SwitchToThread();
	}
}

void Fail(int invariant) {
	g_fail[invariant].fetch_add(1, std::memory_order_relaxed);
}

struct Key {
	uint64_t fingerprint = 0;
	uint64_t base        = 0;
	uint32_t count       = 0;
	uint32_t user[USER_MAX] {};
	explicit Key(uint64_t k) {
		fingerprint = Mix(k) | 1u;
		base        = (k + 1) << 8u;
		count       = 1u + static_cast<uint32_t>(k % USER_MAX);
		for (uint32_t i = 0; i < USER_MAX; i++) {
			user[i] = static_cast<uint32_t>(Mix(k ^ (uint64_t {i} << 32u)));
		}
	}
};

uint64_t KeyHash(const Key& key) {
	return Mix(key.fingerprint ^ key.base);
}

uint64_t ResultTag(uint64_t k) {
	return Mix(k * 0x51ed27ull + 7u);
}

// Owner word of I1, right after a guard was taken and right before it is released.
void Own(AheadSlot& slot) {
	uint32_t expected = 0;
	if (!slot.owner.compare_exchange_strong(expected, t_me, std::memory_order_acq_rel)) {
		Fail(1);
	}
}
void Disown(AheadSlot& slot) {
	uint32_t expected = t_me;
	if (!slot.owner.compare_exchange_strong(expected, 0, std::memory_order_acq_rel)) {
		Fail(1);
	}
}

// QueueAheadSource (707e0d7d:...pipelineCache.cpp:2813-2935), under g_queue_mutex.
void QueueSource(uint64_t k, uint32_t uses, std::vector<uint32_t>& batch) {
	const Key  key(k);
	const auto hash       = KeyHash(key);
	const bool guarded    = g_inject != 2;
	auto&      first      = g_slots[hash & (SLOT_COUNT - 1)];
	auto&      second     = g_slots[(hash + 1) & (SLOT_COUNT - 1)];
	auto&      low        = &first < &second ? first : second;
	auto&      high       = &first < &second ? second : first;
	AheadSlot* victim      = nullptr;
	uint32_t   victim_rank = UINT32_MAX;
	if (guarded) { // PairGuard (:2828-2846)
		Guards::GuardSlot(low);
		Own(low);
		Guards::GuardSlot(high);
		Own(high);
	}
	const auto release = [&] {
		if (guarded) {
			Disown(high);
			Guards::UnguardSlot(high);
			Disown(low);
			Guards::UnguardSlot(low);
		}
	};
	Window();
	for (size_t probe = 0; probe < 2; probe++) { // :2847
		auto&      slot  = g_slots[(hash + probe) & (SLOT_COUNT - 1)];
		const auto state = slot.state.load(std::memory_order_acquire);
		if (state == AheadTaking) { // :2851
			if (slot.Matches(key.fingerprint, key.base, GENERATION, key.count, key.user)) {
				release();
				return;
			}
			continue;
		}
		if (state != AheadEmpty && slot.Matches(key.fingerprint, key.base, GENERATION, key.count, key.user)) { // :2860
			if (slot.walk >= g_ahead_fresh) {
				slot.walk = std::max(slot.walk, g_ahead_walk);
				slot.uses += uses;
			} else if (state == AheadReady || state == AheadFailed) { // :2869
				slot.walk = g_ahead_walk;
				slot.uses = uses;
				Window();
				slot.state.store(AheadQueued, std::memory_order_release);
				slot.taken = 0;
				batch.push_back(static_cast<uint32_t>(&slot - g_slots.data()));
			} else {
				slot.walk = g_ahead_walk;
				slot.uses = uses;
			}
			release();
			return;
		}
		uint32_t rank = UINT32_MAX; // :2892
		if (state == AheadEmpty || state == AheadFailed) {
			rank = 0;
		} else if (slot.walk < g_ahead_fresh && state == AheadReady) {
			rank = 1;
		} else if (slot.walk < g_ahead_fresh && state == AheadQueued) {
			rank = 2;
		}
		if (rank < victim_rank) {
			victim      = &slot;
			victim_rank = rank;
		}
	}
	if (victim != nullptr && victim_rank == 2) { // :2905
		auto expected = static_cast<uint8_t>(AheadQueued);
		if (!victim->state.compare_exchange_strong(expected, AheadEmpty, std::memory_order_acq_rel)) {
			victim = nullptr;
		}
	}
	if (victim == nullptr) { // :2911
		release();
		return;
	}
	victim->fingerprint = key.fingerprint; // :2915-2922
	victim->shader_base = key.base;
	victim->generation  = GENERATION;
	victim->walk        = g_ahead_walk;
	victim->uses        = uses;
	victim->count       = key.count;
	for (uint32_t i = 0; i < key.count; i++) {
		victim->user_data[i] = key.user[i];
		if (i == key.count / 2) {
			Window(); // the middle of the key
		}
	}
	victim->taken = 0;
	victim->state.store(AheadQueued, std::memory_order_release); // :2933
	batch.push_back(static_cast<uint32_t>(victim - g_slots.data()));
	release();
}

void Producer(uint32_t me, uint64_t seed) {
	t_me  = me;
	t_rng = seed * 0x2545f4914f6cdd1dull + me;
	std::vector<uint32_t> batch;
	while (!g_stop.load(std::memory_order_acquire)) {
		batch.clear();
		{
			std::lock_guard queue_lock(g_queue_mutex); // QueueAhead (:2945)
			const uint64_t  walk = ++g_ahead_walk;
			g_ahead_fresh        = walk > 2 ? walk - 2 : 0; // the processing walk lags behind
			const uint64_t window_base = walk * 3u; // the keys of this walk; the draws pick from the same window
			for (int request = 0; request < 16; request++) {
				const uint64_t k = (window_base + Rng() % 48u) % KEY_SPACE;
				QueueSource(k, 1u + static_cast<uint32_t>(Rng() % 3u), batch);
			}
			g_walk_published.store(walk, std::memory_order_release);
		}
		if (!batch.empty()) { // :3110-3134
			{
				std::lock_guard lock(g_ring_mutex);
				g_ring.insert(g_ring.end(), batch.begin(), batch.end());
				g_queued.fetch_add(batch.size(), std::memory_order_relaxed);
			}
			g_ring_cv.notify_all();
		}
		if ((Rng() & 3u) == 0) {
			SwitchToThread();
		}
	}
}

// AheadRun (:3204-3249): claim Queued -> Running, read the key, write the result, publish Ready.
void Worker(uint32_t me, uint64_t seed) {
	t_me  = me;
	t_rng = seed * 0x9e3779b97f4a7c15ull + me;
	for (;;) {
		uint32_t index = 0;
		{
			std::unique_lock lock(g_ring_mutex);
			g_ring_cv.wait_for(lock, std::chrono::milliseconds(2),
			                   [] { return g_ring_head < g_ring.size() || g_stop.load(std::memory_order_acquire); });
			if (g_ring_head >= g_ring.size()) {
				if (g_stop.load(std::memory_order_acquire)) {
					return;
				}
				continue;
			}
			index = g_ring[g_ring_head++];
			if (g_ring_head > 4096 && g_ring_head * 2 > g_ring.size()) {
				g_ring.erase(g_ring.begin(), g_ring.begin() + static_cast<std::ptrdiff_t>(g_ring_head));
				g_ring_head = 0;
			}
		}
		auto& slot     = g_slots[index];
		auto  expected = static_cast<uint8_t>(AheadQueued);
		if (!slot.state.compare_exchange_strong(expected, AheadRunning, std::memory_order_acq_rel)) {
			continue; // cancelled, or claimed through an older queue entry
		}
		g_runs.fetch_add(1, std::memory_order_relaxed);
		Window();
		// I2: the whole key, as MaterializeResources reads it (slot.user_data, slot.count, slot.shader_base).
		const uint64_t k = (slot.shader_base >> 8u) - 1u;
		bool           whole = k < KEY_SPACE;
		if (whole) {
			const Key key(k);
			whole = slot.fingerprint == key.fingerprint && slot.count == key.count;
			for (uint32_t i = 0; whole && i < key.count; i++) {
				Window();
				whole = slot.user_data[i] == key.user[i];
			}
		}
		if (!whole) {
			Fail(2);
		}
		slot.result_key = k;
		Window();
		slot.result_tag = ResultTag(k);
		if (slot.state.load(std::memory_order_acquire) != AheadRunning) { // I5
			Fail(5);
		}
		slot.state.store(whole ? AheadReady : AheadFailed, std::memory_order_release); // :3249
	}
}

// AheadTake (:3311-3572), the guarded part and the publication of the Taking slot.
void Draw(uint32_t me, uint64_t seed, uint64_t takes) {
	t_me  = me;
	t_rng = seed * 0xd1b54a32d192ed03ull + me;
	const bool guarded = g_inject != 1;
	for (uint64_t take = 0; take < takes; take++) {
		g_takes.fetch_add(1, std::memory_order_relaxed);
		const uint64_t walk = g_walk_published.load(std::memory_order_acquire);
		const uint64_t k    = (walk * 3u + Rng() % 48u) % KEY_SPACE; // a key of a recent walk
		const Key      key(k);
		const auto     hash = KeyHash(key);
		bool           done = false;
		for (size_t probe = 0; probe < 2 && !done; probe++) { // :3352
			auto& slot = g_slots[(hash + probe) & (SLOT_COUNT - 1)];
			if (guarded) {
				if (!Guards::TryGuardSlot(slot)) { // :3358
					continue;
				}
				Own(slot);
			}
			const auto unguard = [&] {
				if (guarded) {
					Disown(slot);
					Guards::UnguardSlot(slot);
				}
			};
			Window();
			if (!slot.Matches(key.fingerprint, key.base, GENERATION, key.count, key.user)) { // :3362
				unguard();
				continue;
			}
			auto state = slot.state.load(std::memory_order_acquire);
			if (state == AheadQueued) { // :3368
				if (slot.uses > 1) {
					slot.uses--;
				} else {
					auto expected = static_cast<uint8_t>(AheadQueued);
					slot.state.compare_exchange_strong(expected, AheadEmpty, std::memory_order_acq_rel);
				}
				unguard();
				g_late.fetch_add(1, std::memory_order_relaxed);
				done = true;
				break;
			}
			if (state == AheadRunning) { // :3380
				slot.uses -= slot.uses != 0 ? 1u : 0u;
				unguard();
				g_late.fetch_add(1, std::memory_order_relaxed);
				done = true;
				break;
			}
			if (state != AheadReady) { // :3386
				unguard();
				break;
			}
			Window();
			slot.state.store(AheadTaking, std::memory_order_relaxed); // :3406
			unguard();
			// Taking: the result is read without the guard (:3408-3571).
			Window();
			const bool key_same = slot.Matches(key.fingerprint, key.base, GENERATION, key.count, key.user);
			const bool result_ok = slot.result_key == k && slot.result_tag == ResultTag(k);
			if (!key_same || !result_ok) { // I3
				Fail(3);
			}
			Window();
			if (slot.state.load(std::memory_order_acquire) != AheadTaking) { // I4
				Fail(4);
			}
			if (slot.uses > 1) { // :3512-3516
				slot.uses--;
				slot.taken = 1;
				slot.state.store(AheadReady, std::memory_order_release);
			} else { // :3557-3561
				slot.uses  = 0;
				slot.taken = 1;
				slot.state.store(AheadEmpty, std::memory_order_release);
			}
			g_hits.fetch_add(1, std::memory_order_relaxed);
			done = true;
		}
		if (!done) {
			g_misses.fetch_add(1, std::memory_order_relaxed);
		}
	}
}

} // namespace

int main(int argc, char** argv) {
	if (argc != 4) {
		std::printf("usage: b27_daslot_stand <none|draw_noguard|producer_noguard> <takes per draw thread> <seed>\n");
		return 2;
	}
	if (std::strcmp(argv[1], "none") == 0) {
		g_inject = 0;
	} else if (std::strcmp(argv[1], "draw_noguard") == 0) {
		g_inject = 1;
	} else if (std::strcmp(argv[1], "producer_noguard") == 0) {
		g_inject = 2;
	} else {
		std::printf("bad inject\n");
		return 2;
	}
	const uint64_t takes = std::strtoull(argv[2], nullptr, 10);
	const uint64_t seed  = std::strtoull(argv[3], nullptr, 10) | 1u;
	if (takes == 0) {
		std::printf("bad takes\n");
		return 2;
	}
	const auto t0 = std::chrono::steady_clock::now();
	std::thread watchdog([t0] {
		while (!g_stop.load(std::memory_order_acquire)) {
			std::this_thread::sleep_for(std::chrono::milliseconds(100));
			if (std::chrono::steady_clock::now() - t0 > std::chrono::seconds(300)) {
				std::printf("STALL\n");
				std::fflush(stdout);
				std::_Exit(3);
			}
		}
	});
	std::vector<std::thread> producers;
	std::vector<std::thread> workers;
	std::vector<std::thread> draws;
	for (uint32_t i = 0; i < 2; i++) {
		producers.emplace_back(Producer, 1 + i, seed);
	}
	for (uint32_t i = 0; i < 4; i++) {
		workers.emplace_back(Worker, 11 + i, seed);
	}
	for (uint32_t i = 0; i < 2; i++) {
		draws.emplace_back(Draw, 21 + i, seed, takes);
	}
	for (auto& thread: draws) {
		thread.join();
	}
	g_stop.store(true, std::memory_order_release);
	g_ring_cv.notify_all();
	for (auto& thread: producers) {
		thread.join();
	}
	for (auto& thread: workers) {
		thread.join();
	}
	watchdog.join();
	const auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0).count();
	std::printf("B27 inject=%s threads=8 takes=%llu hits=%llu late=%llu misses=%llu runs=%llu queued=%llu yields=%llu "
	            "I1=%llu I2=%llu I3=%llu I4=%llu I5=%llu ms=%lld\n",
	            argv[1], static_cast<unsigned long long>(g_takes.load()), static_cast<unsigned long long>(g_hits.load()),
	            static_cast<unsigned long long>(g_late.load()), static_cast<unsigned long long>(g_misses.load()),
	            static_cast<unsigned long long>(g_runs.load()), static_cast<unsigned long long>(g_queued.load()),
	            static_cast<unsigned long long>(g_yields.load()), static_cast<unsigned long long>(g_fail[1].load()),
	            static_cast<unsigned long long>(g_fail[2].load()), static_cast<unsigned long long>(g_fail[3].load()),
	            static_cast<unsigned long long>(g_fail[4].load()), static_cast<unsigned long long>(g_fail[5].load()),
	            static_cast<long long>(ms));
	std::fflush(stdout);
	return 0;
}
