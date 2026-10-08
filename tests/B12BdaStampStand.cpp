// Track F, B12 stand without the game (F29a HPP-699, ROADMAP s122 item 638(g)(2)): the "bdastamp" hole - a 4 MiB tracking
// region covered by two mapped guest ranges is walked by the incremental BDA scan only for the lower range.
//
// Tracker: the REAL code - MemoryTracker (src/graphics/host_gpu/memoryTracker.h/.cpp) with RegionManager, on real memory:
// the announcement of a CPU write is MemoryTracker::MarkRegionAsCpuModified (ChangeState<Cpu, true>, the order of the
// knob KYTY_FIX_B13 of the code); the collect is MemoryTracker::CollectCpuModifiedRanges / CollectCpuModifiedRangesStamped;
// the consumption of a synchronized piece is MemoryTracker::ForEachUploadRange (is_written false), the read-only upload
// that BufferCache::SynchronizeBuffer makes; the stamp is MemoryTracker::RegionWriteStamp; the mapped set is the real
// RangeSet (src/graphics/host_gpu/rangeSet.h); the gates and the knob are the real reads (Common::Gates).
//
// Reader: a model, statement by statement and in their order, of
//   RenderContext::PrepareBda          (src/graphics/host_gpu/renderer/renderContext.cpp) - Prepare() below;
//   BufferCache::SynchronizeBuffersInRange   (src/graphics/host_gpu/renderer/cache/bufferCache.cpp) - InRange();
//   BufferCache::SynchronizeBuffersByRegion  (same file, gate "bdastamp")                         - ByRegion();
//   BufferCache::SynchronizeBuffersOfDirtyRanges (same file, gate "protbatch2" off by default)     - OfDirtyRanges();
//   BufferCache::MarkBdaRegions, BufferCache::DirtyRangesTouchBuffers                              - same names;
//   BufferCache::ChangeRegister<true> (the registration epoch and MarkBdaRegions)                   - Register().
// Left out of the model (no effect on what is collected): FrameStats counters and timers, gate "bdabitscheck" (off by
// default; the stand refuses to run with it on), the per-buffer Vulkan upload of SynchronizeBuffer.
//
// Layouts (R = the tracking region at BASE; one buffer = one mapped range unless said otherwise; sizes in 64 KiB):
//   hole   M1 = [R, R+64K) with buffer B1 = M1;  M2 = [R+1M, R+1M+64K) with buffer B2 = M2 (one region, gap 960 KiB)
//   nob1   the ranges of hole; only B2 is registered (the walk of M1 is bounded to no buffer and does not reach R)
//   split  M1, B1 as hole; M2 = B2 = [R+4M+1M, ...): the next region
//   touch  M1 = [R, R+1M) with B1 = [R, R+64K); M2, B2 as hole: M1 and M2 touch and the RangeSet merges them
// Write: upper - every iteration announces one page of B2; lower - one page of B1 (the forced negative control: the same
// layout, the same passes, only the written range differs).
//
// One iteration: announce the page (the real ChangeState<Cpu, true>), run <passes> calls of Prepare(); the page is
// "lost" when no pass synchronized it (model detector: no OfDirtyRanges piece covered it) and "dirty" when the tracker
// still holds it CPU-dirty after the passes (real detector: MemoryTracker::IsRegionCpuModified). A lost page is then
// consumed outside the model (counted as reset) so that every iteration starts with B1 and B2 clean.
//
// Track F, F29c (HPP-702, ROADMAP s122 item 639(e)(1)): the branch KYTY_FIX_B12=1 of the model is a statement-by-statement
// copy of the code change (BufferCache::BeginBdaPass / EndBdaPass, the revisit and walked_pass of
// SynchronizeBuffersByRegion, the pass around the ForEach of PrepareBda); the knob is the code's own read
// (Libs::Graphics::FixB12Enabled). The optional fifth argument hook=<upper|lower> announces one more page - of B2 / B1 -
// between the walks of the first and the second mapped range of the FIRST pass of every iteration (stand-only
// instrument, not a statement of the code; it fires only in a pass that walks); write=none announces no page before
// the passes (hook only). Counted per pass: revisits (rewalk) and the pieces among them that touch a registered
// buffer (rwd); per iteration: scans and revisits in the passes after the first (late_*), and the minimum and
// maximum of revisits over the passes that scanned at least one region (rw_min / rw_max; scan_passes of them).
//
// Usage: b12_bdastamp_stand <hole|nob1|split|touch> <upper|lower|none> <passes> <iters> [hook=<upper|lower>]
// Knobs of the code under test are read from the environment as the emulator reads them: KYTY_BDA_REGION_STAMPS
// (gate "bdastamp", default on), KYTY_BDA_WRITE_BITS (gate "bdabits", default off), KYTY_BDA_NARROW_STAMPS (knob
// "bdanarrow", default 0), KYTY_FIX_B13 (default 1), KYTY_BDA_EPOCH_CACHE, KYTY_BDA_DIRTY_RANGES (default on).
// Output: one line "B12 layout=... write=... passes=... iters=<n> lost=<n> dirty=<n> ..." and exit 0; exit 2 on bad
// arguments or setup.
#include "common/gates.h"
#include "common/virtualMemory.h"
#include "graphics/host_gpu/memoryTracker.h"
#include "graphics/host_gpu/pageManager.h"
#include "graphics/host_gpu/rangeSet.h"

#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iterator>
#include <map>
#include <vector>

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#undef min
#undef max

// The two kernel calls of pageManager.cpp, as tests/B13EpochStand.cpp provides them: data pages only, no guest stacks;
// the host protection change is VirtualProtect.
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
using Libs::Graphics::RangeSet;
using Libs::Graphics::TRACKER_REGION_SIZE;

constexpr uint64_t BASE = 0x0000000240000000ull; // a 4 MiB tracking region (index 0x900)
constexpr uint64_t KIB  = 1024;
constexpr uint64_t MIB  = 1024 * KIB;

struct Buf {
	uint64_t address = 0;
	uint64_t size    = 0;
};

// BufferCache: the fields and the functions of the BDA scan.
struct Cache {
	explicit Cache(MemoryTracker& t): tracker(t) {}
	MemoryTracker&          tracker;
	std::map<uint64_t, Buf> buffers;       // m_buffers (CPU address -> buffer)
	std::vector<GuestRange> dirty_ranges;  // m_bda_dirty_ranges
	struct BdaRegionStamp {
		MemoryTracker::RegionStamp stamp;
		uint64_t                   generation = 0;
		uint64_t                   walked_pass = 0; // F29c: KYTY_FIX_B12=1 only
	};
	std::vector<BdaRegionStamp> region_stamps;          // m_bda_region_stamps
	uint64_t                    stamp_generation   = 1; // m_bda_stamp_generation
	uint64_t                    map_generation     = 1; // m_bda_map_generation
	uint64_t                    bits_generation    = 0; // m_bda_bits_generation
	bool                        narrow_check       = false;
	uint64_t                    registration_epoch = 1; // m_registration_epoch
	uint64_t                    bda_pass           = 0;     // m_bda_pass (F29c)
	bool                        bda_pass_open      = false; // m_bda_pass_open (F29c)
	uint64_t                    rewalk = 0, rwd = 0;         // m_b12_rewalk, m_b12_rwd (F29c)
	// stand counters
	uint64_t              scanned = 0, skipped = 0, bit_skipped = 0, nwould = 0, nmiss = 0, nrace = 0, syncs = 0;
	std::vector<GuestRange> synced; // pieces synchronized since the last clear (model detector)

	void Register(uint64_t address, uint64_t size) {
		++registration_epoch; // ChangeRegister: ++m_registration_epoch
		buffers.emplace(address, Buf {address, size});
		MarkBdaRegions(address, size); // ChangeRegister<true>: MarkBdaRegions(buffer.CpuAddress(), buffer.Size())
	}

	void MarkBdaRegions(uint64_t vaddr, uint64_t size) {
		if (region_stamps.empty() || size == 0) {
			return;
		}
		const auto first = vaddr / TRACKER_REGION_SIZE;
		const auto last  = std::min<uint64_t>((vaddr + size - 1) / TRACKER_REGION_SIZE, region_stamps.size() - 1);
		for (auto index = first; index <= last; index++) {
			region_stamps[index].generation = 0;
		}
	}

	bool DirtyRangesTouchBuffers() {
		for (const auto& range: dirty_ranges) {
			auto it = buffers.upper_bound(range.address);
			if (it != buffers.begin()) {
				--it;
			}
			for (; it != buffers.end() && it->first < range.End(); ++it) {
				const auto& buffer = it->second;
				if (std::max(buffer.address, range.address) < std::min(buffer.address + buffer.size, range.End())) {
					return true;
				}
			}
		}
		return false;
	}

	// SynchronizeBuffer(buffer, start, size, false, false): the read-only upload consumes the CPU-dirty bits.
	void Synchronize(uint64_t start, uint64_t size) {
		syncs++;
		synced.push_back({start, size});
		(void)tracker.ForEachUploadRange(start, size, false, [](uint64_t, uint64_t) noexcept {}, []() noexcept {});
	}

	void OfDirtyRanges() {
		if (dirty_ranges.empty()) {
			return;
		}
		for (const auto& range: dirty_ranges) {
			auto it = buffers.upper_bound(range.address);
			if (it != buffers.begin()) --it;
			for (; it != buffers.end() && it->first < range.End(); ++it) {
				const auto& buffer = it->second;
				const auto  start  = std::max(buffer.address, range.address);
				const auto  finish = std::min(buffer.address + buffer.size, range.End());
				if (start < finish) {
					Synchronize(start, finish - start);
				}
			}
		}
	}

	void BeginBdaPass() {
		bda_pass++;
		bda_pass_open = true;
	}

	void EndBdaPass() {
		bda_pass_open = false; // the FixB12Stat: line of the code only prints; not modelled
	}

	void ByRegion(uint64_t scan_begin, uint64_t scan_end) {
		if (region_stamps.empty()) {
			region_stamps.resize(MemoryTracker::RegionCount());
		}
		const bool use_bits = Common::Gates::Enabled(Common::Gates::Gate::BdaWriteBits) &&
		                      bits_generation == stamp_generation;
		bits_generation = stamp_generation;
		const bool b12_pass = bda_pass_open;
		for (auto cursor = scan_begin; cursor < scan_end;) {
			const auto index = cursor / TRACKER_REGION_SIZE;
			const auto bytes = std::min(scan_end - cursor, TRACKER_REGION_SIZE - cursor % TRACKER_REGION_SIZE);
			if (b12_pass && region_stamps[index].walked_pass == bda_pass) {
				tracker.CollectCpuModifiedRanges(cursor, bytes, dirty_ranges);
				rewalk++;
				if (DirtyRangesTouchBuffers()) {
					rwd++;
				}
				OfDirtyRanges();
				cursor += bytes;
				continue;
			}
			const bool bit_clear = use_bits && !Libs::Graphics::BdaTakeRegionWrite(index);
			if (bit_clear && region_stamps[index].generation == stamp_generation) {
				bit_skipped++;
				skipped++;
				cursor += bytes;
				continue;
			}
			const auto stamp = tracker.RegionWriteStamp(index);
			auto&      seen  = region_stamps[index];
			if (seen.generation == stamp_generation && seen.stamp == stamp) {
				skipped++;
				cursor += bytes;
				continue;
			}
			const auto prev = seen;
			seen            = {stamp, stamp_generation};
			if (b12_pass) {
				seen.walked_pass = bda_pass;
			}
			scanned++;
			if (narrow_check) {
				const auto locked = tracker.CollectCpuModifiedRangesStamped(cursor, bytes, dirty_ranges);
				if (prev.generation != 0 && prev.generation >= map_generation) {
					if (prev.stamp == locked) {
						nwould++;
						if (DirtyRangesTouchBuffers()) {
							nmiss++;
						}
					} else if (prev.stamp == stamp) {
						nrace++;
					}
				}
			} else {
				tracker.CollectCpuModifiedRanges(cursor, bytes, dirty_ranges);
			}
			OfDirtyRanges();
			cursor += bytes;
		}
	}

	void InRange(uint64_t vaddr, uint64_t size) {
		static const bool dirty = [] {
			const auto* value = std::getenv("KYTY_BDA_DIRTY_RANGES");
			return value == nullptr || value[0] != '0';
		}();
		if (dirty) {
			const auto end   = vaddr + size;
			auto       first = buffers.upper_bound(vaddr);
			if (first != buffers.begin()) {
				const auto  previous = std::prev(first);
				const auto& buffer   = previous->second;
				if (buffer.address + buffer.size > vaddr) first = previous;
			}
			if (first == buffers.end() || first->first >= end) {
				return;
			}
			const auto  last        = std::prev(buffers.lower_bound(end));
			const auto& last_buffer = last->second;
			const auto  scan_begin  = std::max(vaddr, first->first);
			const auto  scan_end    = std::min(end, last_buffer.address + last_buffer.size);
			if (Common::Gates::Enabled(Common::Gates::Gate::BdaRegionStamps)) {
				ByRegion(scan_begin, scan_end);
				return;
			}
			tracker.CollectCpuModifiedRanges(scan_begin, scan_end - scan_begin, dirty_ranges);
			OfDirtyRanges();
			return;
		}
		const auto end = vaddr + size;
		auto       it  = buffers.upper_bound(vaddr);
		if (it != buffers.begin()) {
			--it;
		}
		for (; it != buffers.end() && it->first < end; ++it) {
			const auto& buffer = it->second;
			const auto  start  = std::max(buffer.address, vaddr);
			const auto  finish = std::min(buffer.address + buffer.size, end);
			if (start < finish) {
				Synchronize(start, finish - start);
			}
		}
	}
};

// RenderContext: the guest map and PrepareBda.
struct Context {
	explicit Context(Cache& c): cache(c) {}
	Cache&   cache;
	RangeSet mapped_ranges;
	uint64_t mapping_epoch          = 1;
	uint64_t bda_cpu_epoch          = 0;
	uint64_t bda_registration_epoch = 0;
	uint64_t bda_mapping_epoch      = 0;
	uint64_t hits = 0, calls = 0, ginv_map = 0, ginv_reg = 0, nskip = 0;
	// Stand-only instrument (F29c): called once after the walk of the first mapped range of a walking pass, then disarmed.
	void (*hook)(void*) = nullptr;
	void* hook_arg      = nullptr;

	void Map(uint64_t vaddr, uint64_t size) {
		mapped_ranges.Add(vaddr, size);
		++mapping_epoch;
	}

	void Prepare() {
		calls++;
		static const bool reuse = [] {
			const auto* value = std::getenv("KYTY_BDA_EPOCH_CACHE");
			return value == nullptr || value[0] != '0';
		}();
		const auto cpu_epoch          = cache.tracker.CpuWriteEpoch();
		const auto registration_epoch = cache.registration_epoch;
		const bool bda_cached         = reuse && cpu_epoch == bda_cpu_epoch &&
		                        registration_epoch == bda_registration_epoch && mapping_epoch == bda_mapping_epoch;
		if (bda_cached) {
			hits++;
			return;
		}
		const auto narrow  = Common::Gates::Value(Common::Gates::Knob::BdaNarrowStamps);
		cache.narrow_check = narrow == 2;
		if (mapping_epoch != bda_mapping_epoch) {
			cache.stamp_generation++;                      // InvalidateBdaRegionStamps
			cache.map_generation = cache.stamp_generation; // NoteBdaMapInvalidation
			ginv_map++;
		} else if (registration_epoch != bda_registration_epoch) {
			if (narrow == 1) {
				nskip++;
			} else {
				cache.stamp_generation++;
				ginv_reg++;
			}
		}
		const bool fix_b12 = Libs::Graphics::FixB12Enabled();
		if (fix_b12) {
			cache.BeginBdaPass();
		}
		mapped_ranges.ForEach([this](uint64_t start, uint64_t end) {
			cache.InRange(start, end - start);
			if (hook != nullptr) { // stand-only: between the first and the second range
				auto* fire = hook;
				hook       = nullptr;
				fire(hook_arg);
			}
		});
		if (fix_b12) {
			cache.EndBdaPass();
		}
		bda_cpu_epoch          = cpu_epoch;
		bda_registration_epoch = registration_epoch;
		bda_mapping_epoch      = mapping_epoch;
	}
};

bool Covered(const std::vector<GuestRange>& pieces, uint64_t address, uint64_t size) {
	for (const auto& piece: pieces) {
		if (piece.address <= address && address + size <= piece.End()) {
			return true;
		}
	}
	return false;
}

} // namespace

int main(int argc, char** argv) {
	if (argc != 5 && argc != 6) {
		std::printf("usage: b12_bdastamp_stand <hole|nob1|split|touch> <upper|lower|none> <passes> <iters> "
		            "[hook=<upper|lower>]\n");
		return 2;
	}
	const char*    layout = argv[1];
	const char*    write  = argv[2];
	const uint64_t passes = std::strtoull(argv[3], nullptr, 10);
	const uint64_t iters  = std::strtoull(argv[4], nullptr, 10);
	const bool     hole   = std::strcmp(layout, "hole") == 0;
	const bool     nob1   = std::strcmp(layout, "nob1") == 0;
	const bool     split  = std::strcmp(layout, "split") == 0;
	const bool     touch  = std::strcmp(layout, "touch") == 0;
	const bool     upper  = std::strcmp(write, "upper") == 0;
	const bool     lower  = std::strcmp(write, "lower") == 0;
	const bool     none   = std::strcmp(write, "none") == 0;
	const char*    hook_s = argc == 6 ? argv[5] : "";
	const bool     h_up   = std::strcmp(hook_s, "hook=upper") == 0;
	const bool     h_low  = std::strcmp(hook_s, "hook=lower") == 0;
	const bool     h_any  = h_up || h_low;
	if ((argc == 6 && !h_any) || (none && !h_any) || (nob1 && h_low)) {
		std::printf("bad arguments\n");
		return 2;
	}
	if ((!hole && !nob1 && !split && !touch) || (!upper && !lower && !none) || (nob1 && lower) || passes == 0 ||
	    iters == 0) {
		std::printf("bad arguments\n");
		return 2;
	}
	if (Common::Gates::Enabled(Common::Gates::Gate::BdaWriteBitsVerify)) {
		std::printf("bad arguments: gate bdabitscheck is not modelled\n");
		return 2;
	}

	PageManager   page_manager;
	MemoryTracker tracker(page_manager);
	const auto    page   = page_manager.GetPageSize();
	auto*         memory = static_cast<uint8_t*>(
        VirtualAlloc(reinterpret_cast<void*>(BASE), 8 * MIB, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE));
	if (memory != reinterpret_cast<void*>(BASE)) {
		std::printf("fixed VirtualAlloc failed\n");
		return 2;
	}

	const uint64_t m1      = BASE;
	const uint64_t m1_size = touch ? 1 * MIB : 64 * KIB;
	const uint64_t m2      = split ? BASE + 4 * MIB + 1 * MIB : BASE + 1 * MIB;
	const uint64_t b_size  = 64 * KIB;

	Cache   cache(tracker);
	Context context(cache);
	context.Map(m1, m1_size);
	context.Map(m2, b_size);
	if (!nob1) {
		cache.Register(m1, b_size);
	}
	cache.Register(m2, b_size);

	uint64_t mapped_count = 0;
	context.mapped_ranges.ForEach([&](uint64_t, uint64_t) { mapped_count++; });
	const bool same_region = (m1 + m1_size - 1) / TRACKER_REGION_SIZE == m2 / TRACKER_REGION_SIZE;

	// Warm-up: the first passes create the regions (every page starts dirty); whatever they leave dirty in B1 and B2 is
	// consumed outside the model so that the first iteration starts clean.
	context.Prepare();
	context.Prepare();
	uint64_t warm_reset = 0;
	for (const auto b: {m1, m2}) {
		if ((b == m1 && nob1) || !tracker.IsRegionCpuModified(b, b_size)) {
			continue;
		}
		warm_reset++;
		(void)tracker.ForEachUploadRange(b, b_size, false, [](uint64_t, uint64_t) noexcept {}, []() noexcept {});
	}
	context.Prepare(); // the witnesses of the clean state

	const uint64_t target      = upper ? m2 : m1;
	const uint64_t h_target    = h_up ? m2 : m1;
	const auto     scanned0    = cache.scanned;
	const auto     skipped0    = cache.skipped;
	const auto     bitskipped0 = cache.bit_skipped;
	const auto     calls0      = context.calls;
	const auto     hits0       = context.hits;
	const auto     nwould0     = cache.nwould;
	const auto     nmiss0      = cache.nmiss;
	uint64_t       lost = 0, dirty = 0, both = 0, reset = 0, clean_before_bad = 0;
	const auto     rewalk0 = cache.rewalk;
	const auto     rwd0    = cache.rwd;
	uint64_t       hlost = 0, hdirty = 0, hboth = 0, hfired = 0, late_scans = 0, late_rewalks = 0;
	uint64_t       scan_passes = 0, rw_min = UINT64_MAX, rw_max = 0;
	struct HookState {
		MemoryTracker* tracker;
		uint64_t       address;
		uint64_t       size;
		size_t         synced_at;
		Cache*         cache;
		bool           fired;
	} hs {&tracker, 0, page, 0, &cache, false};
	for (uint64_t i = 0; i < iters; i++) {
		const uint64_t address = target + (i % (b_size / page)) * page;
		if (!none && tracker.IsRegionCpuModified(address, page)) {
			clean_before_bad++;
		}
		if (!none) {
			tracker.MarkRegionAsCpuModified(address, page); // the real ChangeState<Cpu, true>: a CPU write announced
		}
		cache.synced.clear();
		if (h_any) {
			hs.address = h_target + ((i + 8) % (b_size / page)) * page;
			hs.fired   = false;
			if (tracker.IsRegionCpuModified(hs.address, page)) {
				clean_before_bad++;
			}
			context.hook_arg = &hs;
			context.hook     = [](void* arg) {
				auto* s      = static_cast<HookState*>(arg);
				s->synced_at = s->cache->synced.size();
				s->fired     = true;
				s->tracker->MarkRegionAsCpuModified(s->address, s->size); // the real ChangeState<Cpu, true>
			};
		}
		for (uint64_t p = 0; p < passes; p++) {
			const auto s0 = cache.scanned;
			const auto r0 = cache.rewalk;
			context.Prepare();
			const auto ds = cache.scanned - s0;
			const auto dr = cache.rewalk - r0;
			if (ds != 0) {
				scan_passes++;
				rw_min = std::min(rw_min, dr);
				rw_max = std::max(rw_max, dr);
			}
			if (p != 0) {
				late_scans += ds;
				late_rewalks += dr;
			}
		}
		context.hook = nullptr; // a hook that found no walking pass stays unfired (counted by hook_fired)
		if (h_any) {
			if (hs.fired) {
				hfired++;
				const std::vector<GuestRange> after(cache.synced.begin() + static_cast<std::ptrdiff_t>(hs.synced_at),
				                                    cache.synced.end());
				const bool h_lost  = !Covered(after, hs.address, page);
				const bool h_dirty = tracker.IsRegionCpuModified(hs.address, page);
				hlost += h_lost ? 1 : 0;
				hdirty += h_dirty ? 1 : 0;
				hboth += (h_lost && h_dirty) ? 1 : 0;
			}
			if (tracker.IsRegionCpuModified(hs.address, page)) {
				reset++;
				(void)tracker.ForEachUploadRange(hs.address, page, false, [](uint64_t, uint64_t) noexcept {},
				                                 []() noexcept {});
			}
		}
		if (none) {
			continue;
		}
		const bool is_lost  = !Covered(cache.synced, address, page);
		const bool is_dirty = tracker.IsRegionCpuModified(address, page);
		lost += is_lost ? 1 : 0;
		dirty += is_dirty ? 1 : 0;
		both += (is_lost && is_dirty) ? 1 : 0;
		if (is_dirty) {
			reset++;
			(void)tracker.ForEachUploadRange(address, page, false, [](uint64_t, uint64_t) noexcept {},
			                                 []() noexcept {});
		}
	}

	std::printf("B12 layout=%s write=%s passes=%llu iters=%llu lost=%llu dirty=%llu lost_and_dirty=%llu reset=%llu "
	            "warm_reset=%llu clean_before_bad=%llu mapped_ranges=%llu same_region=%d calls=%llu hits=%llu "
	            "region_scans=%llu region_skips=%llu bit_skips=%llu nwould=%llu nmiss=%llu gate_bdastamp=%d "
	            "gate_bdabits=%d bdanarrow=%u fix_b13=%d page=%llu\n",
	            layout, write, static_cast<unsigned long long>(passes), static_cast<unsigned long long>(iters),
	            static_cast<unsigned long long>(lost), static_cast<unsigned long long>(dirty),
	            static_cast<unsigned long long>(both), static_cast<unsigned long long>(reset),
	            static_cast<unsigned long long>(warm_reset), static_cast<unsigned long long>(clean_before_bad),
	            static_cast<unsigned long long>(mapped_count), same_region ? 1 : 0,
	            static_cast<unsigned long long>(context.calls - calls0),
	            static_cast<unsigned long long>(context.hits - hits0),
	            static_cast<unsigned long long>(cache.scanned - scanned0),
	            static_cast<unsigned long long>(cache.skipped - skipped0),
	            static_cast<unsigned long long>(cache.bit_skipped - bitskipped0),
	            static_cast<unsigned long long>(cache.nwould - nwould0),
	            static_cast<unsigned long long>(cache.nmiss - nmiss0),
	            Common::Gates::Enabled(Common::Gates::Gate::BdaRegionStamps) ? 1 : 0,
	            Common::Gates::Enabled(Common::Gates::Gate::BdaWriteBits) ? 1 : 0,
	            static_cast<unsigned>(Common::Gates::Value(Common::Gates::Knob::BdaNarrowStamps)),
	            Libs::Graphics::FixB13Enabled() ? 1 : 0, static_cast<unsigned long long>(page));
	std::printf("B12c fix_b12=%d hook=%s hook_fired=%llu hlost=%llu hdirty=%llu hlost_and_dirty=%llu rewalk=%llu rwd=%llu "
	            "scan_passes=%llu rw_min=%llu rw_max=%llu late_scans=%llu late_rewalks=%llu\n",
	            Libs::Graphics::FixB12Enabled() ? 1 : 0, h_any ? hook_s + 5 : "none",
	            static_cast<unsigned long long>(hfired), static_cast<unsigned long long>(hlost),
	            static_cast<unsigned long long>(hdirty), static_cast<unsigned long long>(hboth),
	            static_cast<unsigned long long>(cache.rewalk - rewalk0), static_cast<unsigned long long>(cache.rwd - rwd0),
	            static_cast<unsigned long long>(scan_passes),
	            static_cast<unsigned long long>(scan_passes == 0 ? 0 : rw_min), static_cast<unsigned long long>(rw_max),
	            static_cast<unsigned long long>(late_scans), static_cast<unsigned long long>(late_rewalks));
	std::fflush(stdout);
	// The uploads armed write watchers: the tracker drops them before the PageManager is destroyed (its fail-fast on live
	// page state), as tests/MemoryTrackerTests.cpp does.
	tracker.UntrackMemory(BASE, 8 * MIB);
	return 0;
}
