"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 5 (a), recorded first: the knob-2 check of "bdanarrow" separates races
from misses.  After the dirty ranges of a region knob 1 would skip are collected, the region's write stamp is read
again: unchanged = a real miss (bda_nmiss, first 40 logged as `BdaNarrowMiss:`), moved = a guest write that raced the
check (bda_nrace) - knob 1 would walk that region on its next pass, because its stamp moved.

    python C:/kyty/s106_stage/patch_s113b.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/common/frameStats.h'] = [
    ("""	BufGcEvict,              // bgc_evict
	Count
};
""",
     """	BufGcEvict,              // bgc_evict
	// Session 113 (pre-run audit): knob-2 regions whose dirty ranges overlapped a registered buffer but whose write stamp
	// moved while the check collected them - a guest write racing the check, not a miss of knob 1.  Raw count.
	BdaNarrowRace,           // bda_nrace
	Count
};
"""),
]

EDITS['src/graphics/presentation/videoOut.cpp'] = [
    ("""				    {"bgc_evict", FS::Counter::BufGcEvict, false},
				};
""",
     """				    {"bgc_evict", FS::Counter::BufGcEvict, false},
				    {"bda_nrace", FS::Counter::BdaNarrowRace, false},
				};
"""),
]

EDITS['src/graphics/host_gpu/renderer/cache/bufferCache.h'] = [
    ("""	// Knob 2 of "bdanarrow": whether the dirty ranges just collected overlap any registered buffer.
	bool DirtyRangesTouchBuffers();
""",
     """	// Knob 2 of "bdanarrow": whether the dirty ranges just collected overlap any registered buffer (the first overlap
	// is returned through the optional pointers, for the miss log).
	bool DirtyRangesTouchBuffers(uint64_t* range_address = nullptr, uint64_t* range_size = nullptr,
	                             uint64_t* buffer_address = nullptr, uint64_t* buffer_size = nullptr);
"""),
]

BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
EDITS[BC] = [
    ("""bool BufferCache::DirtyRangesTouchBuffers() {
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
""",
     """bool BufferCache::DirtyRangesTouchBuffers(uint64_t* range_address, uint64_t* range_size, uint64_t* buffer_address,
                                          uint64_t* buffer_size) {
	for (const auto& range: m_bda_dirty_ranges) {
		auto it = m_buffers.upper_bound(range.address);
		if (it != m_buffers.begin()) {
			--it;
		}
		for (; it != m_buffers.end() && it->first < range.End(); ++it) {
			const auto& buffer = m_slot_buffers[it->second];
			if (std::max(buffer.CpuAddress(), range.address) <
			    std::min(buffer.CpuAddress() + buffer.Size(), range.End())) {
				if (range_address != nullptr) {
					*range_address  = range.address;
					*range_size     = range.End() - range.address;
					*buffer_address = buffer.CpuAddress();
					*buffer_size    = buffer.Size();
				}
				return true;
			}
		}
	}
	return false;
}
"""),
    ("""		if (narrow_would_skip) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowWould, 1);
			if (DirtyRangesTouchBuffers()) {
				Common::FrameStats::Add(Common::FrameStats::Counter::BdaNarrowMiss, 1);
			}
		}
""",
     """		if (narrow_would_skip) {
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
