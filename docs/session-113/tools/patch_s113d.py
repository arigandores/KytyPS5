"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 17 (recorded first): the GC-trigger measurement arm.
KYTY_BUFFER_GC_TRIGGER_SHIFT_MB (MEASUREMENT ONLY, not a gate, read once in the BufferCache constructor, default 0 = as
today) lowers the buffer-GC trigger by N MiB (not below 1 GiB); the critical threshold and the texture cache are not
touched.  A log line BufferGc: budget= trigger= critical= shift_mb= is always printed when memory usage is reported.

    python C:/kyty/s106_stage/patch_s113d.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/graphics/host_gpu/renderer/cache/bufferCache.cpp'] = [
    ("""	m_trigger_gc_memory  = static_cast<uint64_t>(std::max<int64_t>(expected, GiB));
	m_critical_gc_memory = static_cast<uint64_t>(std::max<int64_t>(critical, 2 * GiB));
}
""",
     """	// Session 113 (ROADMAP item 17), MEASUREMENT ONLY: KYTY_BUFFER_GC_TRIGGER_SHIFT_MB lowers the buffer-GC trigger by
	// N MiB (never below 1 GiB) so a run is put in the OLD BDA regime (usage above the trigger, the GC evicting idle
	// buffers) on purpose; the critical threshold and the texture cache keep today's values.  Read once per process.
	uint64_t shift_mb = 0;
	if (const char* shift = std::getenv("KYTY_BUFFER_GC_TRIGGER_SHIFT_MB"); shift != nullptr) {
		shift_mb = std::strtoull(shift, nullptr, 10);
	}
	const auto shifted = expected - static_cast<int64_t>(std::min<uint64_t>(shift_mb, 1ull << 30u)) * (GiB / 1024);
	m_trigger_gc_memory  = static_cast<uint64_t>(std::max<int64_t>(shifted, GiB));
	m_critical_gc_memory = static_cast<uint64_t>(std::max<int64_t>(critical, 2 * GiB));
	LOGF("BufferGc: budget=%llu trigger=%llu critical=%llu shift_mb=%llu\\n", static_cast<unsigned long long>(budget),
	     static_cast<unsigned long long>(m_trigger_gc_memory), static_cast<unsigned long long>(m_critical_gc_memory),
	     static_cast<unsigned long long>(shift_mb));
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
            assert old.endswith('\n') and (text.startswith(old) or ('\n' + old) in text), (rel, 'anchor not whole lines')
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
