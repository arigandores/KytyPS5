// Track F, B13 stand without the game (F24a HPP-658, ROADMAP s122 item 593(d)(1)): the order of the two epochs that
// RegionManager::ChangeState<Cpu, true> publishes (src/graphics/host_gpu/regionManager.h, the global CPU epoch and the
// region epoch) against the lock-free "skip this region" decision of the BDA preparation.
//
// Writer: the REAL code - MemoryTracker::MarkRegionAsCpuModified -> RegionManager::ChangeState<Cpu, true> under the real
// region lock, on a page of real memory. The test-build hook KYTY_B13_TEST_HOOK(point) of regionManager.h calls Hook()
// below: point 1 - between the two epoch stores, point 2 - after both, before BdaNoteRegionWrite. The CMake target
// b13_epoch_stand builds the order of the code, b13_epoch_stand_swap (KYTY_TEST_B13_SWAP) the reversed order.
//
// Reader: a model of the two places that decide without the region lock, in their order, on the real tracker reads:
//   RenderContext::PrepareBda (src/graphics/host_gpu/renderer/renderContext.cpp): g = CpuWriteEpoch(); a hit when g is
//     the epoch stored by the last scan (registration and map epochs are constant here); after the scan the epoch read
//     BEFORE the scan is stored;
//   BufferCache::SynchronizeBuffersByRegion (src/graphics/host_gpu/renderer/cache/bufferCache.cpp, gate "bdastamp", on
//     by default): with gate "bdabits" (off by default) a clear bit of BdaTakeRegionWrite skips the region; otherwise
//     RegionWriteStamp(index) equal to the stored stamp skips it; otherwise the stamp is stored and the region is
//     collected under its lock (CollectCpuModifiedRanges).
// One region, inside one registered buffer; a "scan" is the collect of that region.
//
// Usage: b13_epoch_stand <mode> <point> <bits> <iters>
//   mode forced - the writer stops at the hook point; the reader makes call R1 while the writer is stopped there (it
//                 decides lock-free, then releases the writer, then - if it scans - waits for the region lock), then
//                 call R2 after the writer returned. Lost = neither R1 nor R2 scanned the region after the announcement.
//   mode free   - the writer and the reader start together; at the hook point the writer yields to the OS with
//                 probability 1/4 (SwitchToThread); R1 runs after a random pause of 0..4095 YieldProcessor, R2 after
//                 the writer returned.
//   mode before - control: the announcement completes before R1 (no hook action).
//   mode after  - control: R1 completes before the announcement, R2 after it.
//   point 1 or 2, bits 0 or 1 (the reader with or without the bdabits map).
// Every iteration starts from the state of a completed scan with nothing announced since (Reader::Resync).
// Output: one line "B13 build=<code|swap> mode=... point=... bits=... iters=<n> lost=<n> r1=... r2=..." and exit 0;
// "STALL <where>" and exit 3 when a wait does not end in 10 s.
#include "common/gates.h"
#include "common/virtualMemory.h"
#include "graphics/host_gpu/memoryTracker.h"
#include "graphics/host_gpu/pageManager.h"

#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <thread>
#include <vector>

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#undef min
#undef max

#if !defined(KYTY_TEST_B13_HOOK)
#error "b13_epoch_stand needs KYTY_TEST_B13_HOOK"
#endif

namespace {

std::atomic<int>      g_armed_point {0}; // the hook point that acts, 0 = none
std::atomic<uint32_t> g_writer_tid {0};
std::atomic<int>      g_phase {0}; // forced: 0 - before, 1 - writer stopped at the hook, 2 - reader decided
std::atomic<bool>     g_free {false};
std::atomic<uint64_t> g_cmd {0};  // iteration the writer is to announce
std::atomic<uint64_t> g_done {0}; // iteration the writer has announced
std::atomic<bool>     g_quit {false};
thread_local uint32_t t_rng = 0x9e3779b9u;

uint32_t Rng() {
	t_rng ^= t_rng << 13u;
	t_rng ^= t_rng >> 17u;
	t_rng ^= t_rng << 5u;
	return t_rng;
}

template <typename Pred>
void SpinUntil(Pred&& pred, const char* where) {
	uint32_t   spins = 0;
	const auto t0    = std::chrono::steady_clock::now();
	while (!pred()) {
		if (++spins % 4096u == 0) {
			if (std::chrono::steady_clock::now() - t0 > std::chrono::seconds(10)) {
				std::printf("STALL %s\n", where);
				std::fflush(stdout);
				std::_Exit(3);
			}
		}
		YieldProcessor();
	}
}

} // namespace

namespace Libs::Graphics::B13Test {

void Hook(int point) noexcept {
	if (g_armed_point.load(std::memory_order_acquire) != point ||
	    GetCurrentThreadId() != g_writer_tid.load(std::memory_order_relaxed)) {
		return;
	}
	if (g_free.load(std::memory_order_relaxed)) {
		if (Rng() % 4u == 0) {
			SwitchToThread();
		}
		return;
	}
	g_phase.store(1, std::memory_order_release);
	// The reader decides without any lock this thread holds, so this wait ends.
	SpinUntil([] { return g_phase.load(std::memory_order_acquire) == 2; }, "hook");
}

} // namespace Libs::Graphics::B13Test

// The two kernel calls of pageManager.cpp, as tests/MemoryTrackerTests.cpp provides them: data pages only, no guest
// stacks; the host protection change is VirtualProtect.
namespace Libs::LibKernel::Memory {

bool OverlapsGuestStack(uint64_t, uint64_t) {
	return false;
}

bool ProtectGuestHostMemory(uint64_t vaddr, uint64_t size, Common::VirtualMemory::Mode mode) {
	DWORD protection = PAGE_NOACCESS;
	if (mode == Common::VirtualMemory::Mode::Read) {
		protection = PAGE_READONLY;
	} else if (mode == Common::VirtualMemory::Mode::ReadWrite) {
		protection = PAGE_READWRITE;
	}
	DWORD old_protection = 0;
	return VirtualProtect(reinterpret_cast<void*>(vaddr), size, protection, &old_protection) != 0;
}

} // namespace Libs::LibKernel::Memory

namespace {

using Libs::Graphics::GuestRange;
using Libs::Graphics::MemoryTracker;
using Libs::Graphics::PageManager;

enum Outcome { Hit = 0, SkipBit = 1, SkipStamp = 2, Scan = 3 };
const char* const OUTCOME_NAMES[] = {"hit", "skip_bit", "skip_stamp", "scan"};

struct Reader {
	MemoryTracker&             tracker;
	uint64_t                   index   = 0;
	uint64_t                   address = 0;
	uint64_t                   bytes   = 0;
	bool                       bits    = false;
	uint64_t                   cached_g = 0; // RenderContext::m_bda_cpu_epoch
	MemoryTracker::RegionStamp seen {};      // BufferCache::m_bda_region_stamps[index].stamp
	uint32_t                   seen_gen = 0; // ... .generation
	static constexpr uint32_t  GEN      = 1; // m_bda_stamp_generation (no registration, no map change here)
	std::vector<GuestRange>    ranges;

	template <typename Decided>
	Outcome Prepare(Decided&& on_decided) {
		const auto g = tracker.CpuWriteEpoch(); // PrepareBda: cpu_epoch, read before the scan
		if (g == cached_g) {
			on_decided();
			return Hit; // PrepareBda: bda_cached
		}
		Outcome outcome;
		const bool bit_clear = bits && !Libs::Graphics::BdaTakeRegionWrite(index);
		if (bit_clear && seen_gen == GEN) {
			on_decided();
			outcome = SkipBit;
		} else {
			const auto stamp = tracker.RegionWriteStamp(index);
			if (seen_gen == GEN && seen == stamp) {
				on_decided();
				outcome = SkipStamp;
			} else {
				seen     = stamp;
				seen_gen = GEN;
				on_decided(); // the collect below takes the region lock - the writer may hold it until released
				tracker.CollectCpuModifiedRanges(address, bytes, ranges);
				outcome = Scan;
			}
		}
		cached_g = g; // PrepareBda: the epoch from BEFORE the scan
		return outcome;
	}

	// The state of a completed scan with nothing announced since.
	void Resync() {
		cached_g = tracker.CpuWriteEpoch();
		seen     = tracker.RegionWriteStamp(index);
		seen_gen = GEN;
		(void)Libs::Graphics::BdaTakeRegionWrite(index);
	}
};

} // namespace

int main(int argc, char** argv) {
	if (argc != 5) {
		std::printf("usage: b13_epoch_stand <forced|free|before|after> <1|2> <0|1> <iters>\n");
		return 2;
	}
	const char*    mode  = argv[1];
	const int      point = std::atoi(argv[2]);
	const bool     bits  = std::atoi(argv[3]) != 0;
	const uint64_t iters = std::strtoull(argv[4], nullptr, 10);
	const bool     forced = std::strcmp(mode, "forced") == 0;
	const bool     free_mode = std::strcmp(mode, "free") == 0;
	const bool     before = std::strcmp(mode, "before") == 0;
	const bool     after  = std::strcmp(mode, "after") == 0;
	if ((!forced && !free_mode && !before && !after) || (point != 1 && point != 2) || iters == 0) {
		std::printf("bad arguments\n");
		return 2;
	}

	PageManager   page_manager;
	MemoryTracker tracker(page_manager);
	const auto    page = page_manager.GetPageSize();
	constexpr uintptr_t base = 0x0000000200010000ull; // inside one 4 MiB tracking region
	auto* memory = static_cast<uint8_t*>(
	    VirtualAlloc(reinterpret_cast<void*>(base), page * 2, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE));
	if (memory != reinterpret_cast<void*>(base)) {
		std::printf("fixed VirtualAlloc failed\n");
		return 2;
	}
	const auto address = reinterpret_cast<uint64_t>(memory);
	tracker.MarkRegionAsCpuModified(address, page); // creates the region (its first host protection change)

	Reader reader {tracker};
	reader.index   = address / Libs::Graphics::TRACKER_REGION_SIZE;
	reader.address = address;
	reader.bytes   = page;
	reader.bits    = bits;

	g_free.store(free_mode, std::memory_order_relaxed);
	std::thread writer([&] {
		g_writer_tid.store(GetCurrentThreadId(), std::memory_order_release);
		uint64_t last = 0;
		for (;;) {
			uint64_t cmd = 0;
			SpinUntil([&] {
				cmd = g_cmd.load(std::memory_order_acquire);
				return cmd != last || g_quit.load(std::memory_order_acquire);
			}, "writer idle");
			if (cmd == last) {
				return;
			}
			last = cmd;
			tracker.MarkRegionAsCpuModified(address, page); // the real ChangeState<Cpu, true>
			g_done.store(cmd, std::memory_order_release);
		}
	});
	SpinUntil([] { return g_writer_tid.load(std::memory_order_acquire) != 0; }, "writer start");

	uint64_t lost   = 0;
	uint64_t r1[4]  = {};
	uint64_t r2[4]  = {};
	const auto announce_and_wait = [&](uint64_t id) {
		g_cmd.store(id, std::memory_order_release);
		SpinUntil([&] { return g_done.load(std::memory_order_acquire) == id; }, "writer done");
	};
	for (uint64_t i = 1; i <= iters; i++) {
		reader.Resync();
		Outcome first  = Hit;
		Outcome second = Hit;
		if (forced) {
			g_phase.store(0, std::memory_order_relaxed);
			g_armed_point.store(point, std::memory_order_release);
			g_cmd.store(i, std::memory_order_release);
			SpinUntil([] { return g_phase.load(std::memory_order_acquire) == 1; }, "window");
			first = reader.Prepare([] { g_phase.store(2, std::memory_order_release); });
			SpinUntil([&] { return g_done.load(std::memory_order_acquire) == i; }, "writer done");
			g_armed_point.store(0, std::memory_order_release);
			second = reader.Prepare([] {});
		} else if (free_mode) {
			g_armed_point.store(point, std::memory_order_release);
			g_cmd.store(i, std::memory_order_release);
			// A random start of R1 (0..4095 pauses) so that it lands anywhere in the writer's call, not always before it.
			for (uint32_t pause = Rng() % 4096u; pause != 0; pause--) {
				YieldProcessor();
			}
			first = reader.Prepare([] {});
			SpinUntil([&] { return g_done.load(std::memory_order_acquire) == i; }, "writer done");
			second = reader.Prepare([] {});
		} else if (before) {
			g_armed_point.store(0, std::memory_order_release);
			announce_and_wait(i);
			first  = reader.Prepare([] {});
			second = reader.Prepare([] {});
		} else {
			g_armed_point.store(0, std::memory_order_release);
			first = reader.Prepare([] {});
			announce_and_wait(i);
			second = reader.Prepare([] {});
		}
		r1[first]++;
		r2[second]++;
		if (first != Scan && second != Scan) {
			lost++;
		}
	}
	g_quit.store(true, std::memory_order_release);
	writer.join();

#if defined(KYTY_TEST_B13_SWAP)
	const char* build = "swap";
#else
	const char* build = "code";
#endif
	std::printf("B13 build=%s mode=%s point=%d bits=%d iters=%llu lost=%llu r1=%s:%llu,%s:%llu,%s:%llu,%s:%llu "
	            "r2=%s:%llu,%s:%llu,%s:%llu,%s:%llu gate_bdastamp=%d gate_bdabits=%d\n",
	            build, mode, point, bits ? 1 : 0, static_cast<unsigned long long>(iters),
	            static_cast<unsigned long long>(lost), OUTCOME_NAMES[0], static_cast<unsigned long long>(r1[0]),
	            OUTCOME_NAMES[1], static_cast<unsigned long long>(r1[1]), OUTCOME_NAMES[2],
	            static_cast<unsigned long long>(r1[2]), OUTCOME_NAMES[3], static_cast<unsigned long long>(r1[3]),
	            OUTCOME_NAMES[0], static_cast<unsigned long long>(r2[0]), OUTCOME_NAMES[1],
	            static_cast<unsigned long long>(r2[1]), OUTCOME_NAMES[2], static_cast<unsigned long long>(r2[2]),
	            OUTCOME_NAMES[3], static_cast<unsigned long long>(r2[3]),
	            Common::Gates::Enabled(Common::Gates::Gate::BdaRegionStamps) ? 1 : 0,
	            Common::Gates::Enabled(Common::Gates::Gate::BdaWriteBits) ? 1 : 0);
	std::fflush(stdout);
	return 0;
}
