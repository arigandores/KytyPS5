"""Session 113 (ROADMAP 0.1 "СЕССИЯ 113" items 1-3, recorded first): knob "bdanarrow" - the BDA region stamps are
invalidated per buffer on registration instead of globally.

Unconditionally (so any switch of the knob is safe): ChangeRegister<insert> marks the stamps of the new buffer's regions
stale (generation 0).  PrepareBda reads the knob once: 0 = today (a registration-epoch move bumps the global stamp
generation); 1 = only a guest-map move bumps it (the registration already marked its own regions); 2 = 0 plus a check -
every region that knob 1 would have skipped (write stamp unmoved, not marked, scanned since the last map invalidation)
and whose dirty ranges overlap a registered buffer counts in bda_nmiss.

    python C:/kyty/s106_stage/patch_s113.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/common/gates.h'] = [
    ("""	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	DrawAheadGuard,   // KYTY_DRAW_AHEAD_GUARD,   file name "daguard" (0 no guards at daslot 0, 1 guards)
""",
     """	DrawAheadGuard,   // KYTY_DRAW_AHEAD_GUARD,   file name "daguard" (0 no guards at daslot 0, 1 guards)
	// Session 113: the scope of the BDA region-stamp invalidation in PrepareBda.  0 = a buffer registration moves the
	// global stamp generation (every tracking region is walked again - the OLD regime's ~1 016 extra region walks a
	// frame while the buffer GC runs); 1 = a registration marks only its own regions (always done, whatever the knob),
	// the global generation moves only with the guest map; 2 = 0 plus a check of what 1 would skip (bda_nwould,
	// bda_nmiss).  Read once per PrepareBda call, so it CAN be a schedule arm; a switch is safe at any moment.
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	BdaNarrowStamps,  // KYTY_BDA_NARROW_STAMPS,  file name "bdanarrow" (0 global, 1 per buffer, 2 global + check)
"""),
]

EDITS['src/common/gates.cpp'] = [
    ("""    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_DRAW_AHEAD_GUARD", "daguard", 1, 1},
""",
     """    {"KYTY_DRAW_AHEAD_GUARD", "daguard", 1, 1},
    // Session 113: BDA region stamps invalidated per registered buffer (1) instead of globally (0); 2 = 0 + a
    // check of what 1 would skip. Read once per PrepareBda call, so it CAN be a schedule arm.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_BDA_NARROW_STAMPS", "bdanarrow", 0, 2},
"""),
]

EDITS['src/common/frameStats.h'] = [
    ("""	DaQueueNoGuard,          // da_q_noguard
	DaGuardYield,            // da_guard_yield
	Count
};
""",
     """	DaQueueNoGuard,          // da_q_noguard
	DaGuardYield,            // da_guard_yield
	// Session 113, knob "bdanarrow": global BDA stamp invalidations by cause (a buffer registration / the guest map),
	// regions marked stale by a registration, registration moves whose global invalidation knob 1 skipped, and at
	// knob 2 the regions knob 1 would have skipped and those among them whose dirty ranges overlap a registered buffer
	// (an upper bound on a missed synchronization - must read 0); registrations marked on a thread other than the one
	// that scans; buffers the buffer GC evicted.  Raw counts.
	BdaGlobalInvReg,         // bda_ginv_reg
	BdaGlobalInvMap,         // bda_ginv_map
	BdaRegionInv,            // bda_rinv
	BdaNarrowSkip,           // bda_nskip
	BdaNarrowWould,          // bda_nwould
	BdaNarrowMiss,           // bda_nmiss
	BdaNarrowXthread,        // bda_nxthr
	BufGcEvict,              // bgc_evict
	Count
};
"""),
]

EDITS['src/graphics/presentation/videoOut.cpp'] = [
    ("""				    {"da_guard_yield", FS::Counter::DaGuardYield, false},
				};
""",
     """				    {"da_guard_yield", FS::Counter::DaGuardYield, false},
				    {"bda_ginv_reg", FS::Counter::BdaGlobalInvReg, false},
				    {"bda_ginv_map", FS::Counter::BdaGlobalInvMap, false},
				    {"bda_rinv", FS::Counter::BdaRegionInv, false},
				    {"bda_nskip", FS::Counter::BdaNarrowSkip, false},
				    {"bda_nwould", FS::Counter::BdaNarrowWould, false},
				    {"bda_nmiss", FS::Counter::BdaNarrowMiss, false},
				    {"bda_nxthr", FS::Counter::BdaNarrowXthread, false},
				    {"bgc_evict", FS::Counter::BufGcEvict, false},
				};
"""),
]

EDITS['src/graphics/host_gpu/renderer/cache/bufferCache.h'] = [
    ("#include <span>" + chr(10), "#include <span>" + chr(10) + "#include <thread>" + chr(10)),
    ("""	void               InvalidateBdaRegionStamps() noexcept { m_bda_stamp_generation++; }
""",
     """	void               InvalidateBdaRegionStamps() noexcept { m_bda_stamp_generation++; }
	// Session 113, knob "bdanarrow": PrepareBda records a guest-map invalidation (the generation after it) - regions
	// scanned since then are what knob 1 keeps - and whether this pass checks what knob 1 would skip (knob 2).
	void               NoteBdaMapInvalidation() noexcept { m_bda_map_generation = m_bda_stamp_generation; }
	void               SetBdaNarrowCheck(bool check) noexcept { m_bda_narrow_check = check; }
"""),
    ("""	uint64_t                                           m_bda_stamp_generation = 1;
""",
     """	uint64_t                                           m_bda_stamp_generation = 1;
	// Session 113, knob "bdanarrow": see NoteBdaMapInvalidation / MarkBdaRegions; the scanning thread, for the
	// same-thread check of the marks.
	uint64_t                                           m_bda_map_generation = 1;
	bool                                               m_bda_narrow_check   = false;
	std::thread::id                                    m_bda_scan_thread {};
	// Marks the stamps of the tracking regions of [vaddr, vaddr + size) stale (a buffer was registered there).
	void MarkBdaRegions(uint64_t vaddr, uint64_t size);
	// Knob 2 of "bdanarrow": whether the dirty ranges just collected overlap any registered buffer.
	bool DirtyRangesTouchBuffers();
"""),
]

BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
EDITS[BC] = [
    ("""		WriteDataBuffer(m_bda_pagetable_buffer, pages.first * sizeof(vk::DeviceAddress),
		                addresses.data(), addresses.size() * sizeof(vk::DeviceAddress));
	} else {
""",
     """		WriteDataBuffer(m_bda_pagetable_buffer, pages.first * sizeof(vk::DeviceAddress),
		                addresses.data(), addresses.size() * sizeof(vk::DeviceAddress));
		// Session 113, knob "bdanarrow": whatever the knob, the new buffer's own regions are walked again by the next
		// BDA scan - the only regions a registration can make relevant (a region whose write stamp did not move got
		// no new dirty page, and the dirty pages an earlier scan left alone belonged to no registered buffer).
		MarkBdaRegions(buffer.CpuAddress(), buffer.Size());
	} else {
"""),
    ("""		} else {
			m_memory_tracker.UntrackMemory(buffer.CpuAddress(), buffer.Size());
			DeleteBuffer(id);
		}
		return ++retire_count == limit;
""",
     """		} else {
			m_memory_tracker.UntrackMemory(buffer.CpuAddress(), buffer.Size());
			Common::FrameStats::Add(Common::FrameStats::Counter::BufGcEvict, 1);
			DeleteBuffer(id);
		}
		return ++retire_count == limit;
"""),
    ("""		m_memory_tracker.UntrackMemory(buffer.CpuAddress(), buffer.Size());
		Unregister(id);
		m_slot_buffers.erase(id);
	}
}
""",
     """		m_memory_tracker.UntrackMemory(buffer.CpuAddress(), buffer.Size());
		Common::FrameStats::Add(Common::FrameStats::Counter::BufGcEvict, 1);
		Unregister(id);
		m_slot_buffers.erase(id);
	}
}
"""),
    ("""// Incremental variant (gate "bdastamp"): only regions that announced a CPU write since the last
// scan are locked and walked.""",
     """void BufferCache::MarkBdaRegions(uint64_t vaddr, uint64_t size) {
	if (m_bda_region_stamps.empty() || size == 0) {
		return; // no region scanned yet: every one is walked by the first scan anyway
	}
	if (m_bda_scan_thread != std::thread::id {} && std::this_thread::get_id() != m_bda_scan_thread) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowXthread, 1);
	}
	const auto first = vaddr / TRACKER_REGION_SIZE;
	const auto last  = std::min<uint64_t>((vaddr + size - 1) / TRACKER_REGION_SIZE, m_bda_region_stamps.size() - 1);
	for (auto index = first; index <= last; index++) {
		m_bda_region_stamps[index].generation = 0; // never the current generation: the next pass walks it
		Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionInv, 1);
	}
}

bool BufferCache::DirtyRangesTouchBuffers() {
	for (const auto& range: m_bda_dirty_ranges) {
		auto it = m_buffers.upper_bound(range.address);
		if (it != m_buffers.begin()) {
			--it;
		}
		for (; it != m_buffers.end() && it->first < range.End(); ++it) {
			const auto& buffer = m_slot_buffers[it->second];
			if (std::max(buffer.CpuAddress(), range.address) <
			    std::min(buffer.CpuAddress() + buffer.Size(), range.End())) {
				return true;
			}
		}
	}
	return false;
}

// Incremental variant (gate "bdastamp"): only regions that announced a CPU write since the last
// scan are locked and walked."""),
    ("""	if (m_bda_region_stamps.empty()) {
		m_bda_region_stamps.resize(MemoryTracker::RegionCount());
	}
	// Gate "bdabits" (session 82)""",
     """	if (m_bda_region_stamps.empty()) {
		m_bda_region_stamps.resize(MemoryTracker::RegionCount());
	}
	m_bda_scan_thread = std::this_thread::get_id();
	// Gate "bdabits" (session 82)"""),
    ("""		seen = {stamp, m_bda_stamp_generation};
		Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsScanned, 1);
		const uint64_t bda_scan_t0 =
		    bda_split && Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;
		m_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);
""",
     """		// Session 113, knob "bdanarrow" 2: knob 1 would have skipped this region - its write stamp did not move, no
		// registration marked it, and it was scanned since the last guest-map invalidation.
		const bool narrow_would_skip = m_bda_narrow_check && seen.generation != 0 &&
		                               seen.generation >= m_bda_map_generation && seen.stamp == stamp;
		seen = {stamp, m_bda_stamp_generation};
		Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsScanned, 1);
		const uint64_t bda_scan_t0 =
		    bda_split && Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;
		m_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);
		if (narrow_would_skip) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowWould, 1);
			if (DirtyRangesTouchBuffers()) {
				Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowMiss, 1);
			}
		}
"""),
]

EDITS['src/graphics/host_gpu/renderer/renderContext.cpp'] = [
    ("""	// A newly registered buffer may cover pages whose dirty bits an earlier scan left alone, and
	// a changed guest map moves bytes between regions: in both cases the per-region witnesses of
	// the incremental scan no longer say anything about the buffers.
	if (registration_epoch != m_bda_registration_epoch || m_mapping_epoch != m_bda_mapping_epoch) {
		m_buffer_cache.InvalidateBdaRegionStamps();
	}
""",
     """	// A newly registered buffer may cover pages whose dirty bits an earlier scan left alone, and
	// a changed guest map moves bytes between regions: in both cases the per-region witnesses of
	// the incremental scan no longer say anything about the buffers.
	// Session 113, knob "bdanarrow" (read once here): a registration always marks its own regions stale
	// (BufferCache::MarkBdaRegions), so at 1 only the guest map bumps the global generation; 0 and 2 bump it for a
	// registration too, and 2 also counts what 1 would have skipped (bda_nwould / bda_nmiss).
	const auto narrow = Common::Gates::Value(Common::Gates::Knob::BdaNarrowStamps);
	m_buffer_cache.SetBdaNarrowCheck(narrow == 2);
	if (m_mapping_epoch != m_bda_mapping_epoch) {
		m_buffer_cache.InvalidateBdaRegionStamps();
		m_buffer_cache.NoteBdaMapInvalidation();
		Common::FrameStats::Add(Common::FrameStats::Counter::BdaGlobalInvMap, 1);
	} else if (registration_epoch != m_bda_registration_epoch) {
		if (narrow == 1) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowSkip, 1);
		} else {
			m_buffer_cache.InvalidateBdaRegionStamps();
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaGlobalInvReg, 1);
		}
	}
"""),
]


def main():
    for rel, pairs in EDITS.items():
        path = ROOT / rel
        raw = path.read_bytes().decode('utf-8')
        crlf = '\r\n' in raw
        text = raw.replace('\r\n', '\n')
        for old, new in pairs:
            n = text.count(old)
            assert n == 1, (rel, n, old[:90])
            text = text.replace(old, new)
        if crlf:
            text = text.replace('\n', '\r\n')
        if not DRY:
            path.write_bytes(text.encode('utf-8'))
        print(('checked ' if DRY else 'patched ') + rel)


if __name__ == '__main__':
    main()
