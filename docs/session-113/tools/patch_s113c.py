"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 14 (recorded first): the exact knob-2 check of "bdanarrow".
MemoryTracker::CollectCpuModifiedRangesStamped returns the dirty-range snapshot of one region's piece together with the
region's write stamp read under the SAME region lock (the writer sets the bits and moves the epochs under that lock), so
bits and stamp are one consistent snapshot.  Knob 2 then counts a region knob 1 would skip only if the previous witness's
stamp equals the LOCKED stamp (no write since the last walk); its dirty ranges overlapping a registered buffer are a
real miss.  bda_nrace becomes information: the unlocked stamp matched, the locked one did not (a write in between).
The ordinary walk is unchanged (it still stores the unlocked stamp).

    python C:/kyty/s106_stage/patch_s113c.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/graphics/host_gpu/memoryTracker.h'] = [
    ("""	void CollectCpuModifiedRanges(uint64_t vaddr, uint64_t size, std::vector<GuestRange>& ranges);
""",
     """	void CollectCpuModifiedRanges(uint64_t vaddr, uint64_t size, std::vector<GuestRange>& ranges);
	// Session 113 (knob "bdanarrow" 2): the same snapshot for a piece of ONE tracking region, plus that region's write
	// stamp read under the same region lock - the dirty bits and the stamp are one consistent snapshot.
	RegionStamp CollectCpuModifiedRangesStamped(uint64_t vaddr, uint64_t size, std::vector<GuestRange>& ranges);
"""),
]

EDITS['src/graphics/host_gpu/memoryTracker.cpp'] = [
    ("""void MemoryTracker::MarkRegionAsCpuModified(uint64_t vaddr, uint64_t size) {
""",
     """MemoryTracker::RegionStamp MemoryTracker::CollectCpuModifiedRangesStamped(uint64_t vaddr, uint64_t size,
                                                                          std::vector<GuestRange>& ranges) {
	CheckNotInUploadCallback();
	ValidateRange(vaddr, size);
	ranges.clear();
	const auto index = vaddr / TRACKER_REGION_SIZE;
	EXIT_IF(size == 0 || (vaddr + size - 1) / TRACKER_REGION_SIZE != index);
	const auto end    = vaddr + size;
	const auto append = [&](uint64_t address, uint64_t bytes) noexcept {
		const auto first = std::max(address, vaddr);
		const auto last  = std::min(address + bytes, end);
		if (first >= last) return;
		if (!ranges.empty() && ranges.back().End() == first) {
			ranges.back().size += last - first;
		} else {
			ranges.push_back({first, last - first});
		}
	};
	auto* manager = m_regions[index].load(std::memory_order_acquire);
	if (manager == nullptr) {
		append(vaddr, size);
		return {};
	}
	std::scoped_lock lock(manager->lock);
	manager->ForEachModifiedRange<DirtySource::Cpu, false>(vaddr, size, append);
	return RegionStamp {manager, manager->Epoch()};
}

void MemoryTracker::MarkRegionAsCpuModified(uint64_t vaddr, uint64_t size) {
"""),
]

BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
EDITS[BC] = [
    ("""		// Session 113, knob "bdanarrow" 2: knob 1 would have skipped this region - its write stamp did not move, no
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
			uint64_t range_address = 0, range_size = 0, buffer_address = 0, buffer_size = 0;
			if (DirtyRangesTouchBuffers(&range_address, &range_size, &buffer_address, &buffer_size)) {
				// Session 113 (pre-run audit): the stamp above was read without the region lock and the bits were collected
				// under it, so a guest write announced in between is seen here - but it moved the stamp, and knob 1 would
				// walk this region on its next pass. Read the stamp again: unchanged = a real miss of knob 1.
				if (m_memory_tracker.RegionWriteStamp(index) == stamp) {
					Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowMiss, 1);
					static std::atomic<uint32_t> logged {0};
					if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
						LOGF("BdaNarrowMiss: region=%llu range=0x%llx+0x%llx buffer=0x%llx+0x%llx\\n",
						     static_cast<unsigned long long>(index), static_cast<unsigned long long>(range_address),
						     static_cast<unsigned long long>(range_size), static_cast<unsigned long long>(buffer_address),
						     static_cast<unsigned long long>(buffer_size));
					}
				} else {
					Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowRace, 1);
				}
			}
		}
""",
     """		// Session 113, knob "bdanarrow" 2: the previous witness of this region, before the walk overwrites it.
		const auto prev = seen;
		seen = {stamp, m_bda_stamp_generation};
		Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsScanned, 1);
		const uint64_t bda_scan_t0 =
		    bda_split && Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;
		if (m_bda_narrow_check) {
			// Session 113 (item 14): the dirty bits and the region stamp read under the same region lock. Knob 1 would
			// have skipped this region iff the previous witness was not marked by a registration, is not older than the
			// last guest-map invalidation, and its stamp equals the LOCKED stamp - no write since the last walk - so a
			// dirty range of a registered buffer here is a real miss of knob 1.
			const auto locked = m_memory_tracker.CollectCpuModifiedRangesStamped(cursor, bytes, m_bda_dirty_ranges);
			if (prev.generation != 0 && prev.generation >= m_bda_map_generation) {
				if (prev.stamp == locked) {
					Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowWould, 1);
					uint64_t range_address = 0, range_size = 0, buffer_address = 0, buffer_size = 0;
					if (DirtyRangesTouchBuffers(&range_address, &range_size, &buffer_address, &buffer_size)) {
						Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowMiss, 1);
						static std::atomic<uint32_t> logged {0};
						if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
							LOGF("BdaNarrowMiss: region=%llu range=0x%llx+0x%llx buffer=0x%llx+0x%llx\\n",
							     static_cast<unsigned long long>(index), static_cast<unsigned long long>(range_address),
							     static_cast<unsigned long long>(range_size),
							     static_cast<unsigned long long>(buffer_address),
							     static_cast<unsigned long long>(buffer_size));
						}
					}
				} else if (prev.stamp == stamp) {
					// Information only: the unlocked read matched, the locked one did not - a write landed in between;
					// knob 1 walks this region on its next pass.
					Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowRace, 1);
				}
			}
		} else {
			m_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);
		}
"""),
]

EDITS['src/common/frameStats.h'] = [
    ("""	// Session 113 (pre-run audit): knob-2 regions whose dirty ranges overlapped a registered buffer but whose write stamp
	// moved while the check collected them - a guest write racing the check, not a miss of knob 1.  Raw count.
	BdaNarrowRace,           // bda_nrace""",
     """	// Session 113 (item 14): knob-2 regions whose unlocked stamp matched the previous witness but whose stamp read under
	// the region lock did not - a guest write landed between the two reads (information; knob 1 walks the region on its
	// next pass).  Raw count.
	BdaNarrowRace,           // bda_nrace"""),
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
