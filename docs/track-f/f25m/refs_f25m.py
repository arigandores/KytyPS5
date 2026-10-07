"""F25m (HPP-680; form of F25f refs_f25f.py): every '<commit>:<path>:<line>' reference of the seal body with its anchor and +1 control
(general rule 24(1)): the anchor must be a substring of the line, the +1 text a substring of the next line.  The table is ROWS below and is
printed into refs_f25m.tsv.  --neg corrupts every anchor (its last character) - every reference must then fail.  ASCII output; ends with
ALL OK / FAILED (NEG CONTROL OK with --neg).
usage: python refs_f25m.py [--neg]"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
ROWS = [
    ('bac79f88', 'docs/ROADMAP.md', 23723, '613. **Звено F25j трека F (`HPP-677`, лид)', '(а) **Приёмка строкой. F25h ✓**'),
    ('bac79f88', 'docs/ROADMAP.md', 23734, '615. **Звено F25k трека F (`HPP-678`, Emu Engineer', '(а) **Приёмка строкой. F25k ✓.**'),
    ('bac79f88', 'docs/ROADMAP.md', 23746, '616. **Звено F25l трека F (`HPP-679`, Red Team', '(а) **Приёмка строкой. F25l ✓.**'),
    ('bac79f88', 'docs/ROADMAP.md', 23759, '618. **Звено F25k2 трека F (`HPP-682`, Emu Engineer', '(а) **Приёмка строкой. F25k2 ✓.**'),
    ('bac79f88', 'docs/ROADMAP.md', 23771, '619. **Звено F25l2 трека F (`HPP-683`, Red Team', '(а) **Приёмка строкой. F25l2 ✓.**'),
    ('0c8fcba2', 'src/common/logging/log.cpp', 261,
     'fmt::format("TestLogStall: i={} sleep_ms={} slept_us={} t0_ms={} t1_ms={} on={} tid={} role={} line=\\"{}\\"\\n",',
     'i + 1, g_stand.sleep_ms, (t1 - t0) / 1000u, t0 / 1000000u, t1 / 1000000u,'),
    ('0c8fcba2', 'src/common/logging/log.cpp', 281,
     'const auto text = fmt::format("LogAsync: stall us={} queued_bytes={} t_ms={}\\n", ns / 1000u, left,', 'NowNs() / 1000000u);'),
    ('0c8fcba2', 'src/common/logging/log.cpp', 494,
     'text = fmt::format("LogAsync: full_waits={} full_wait_us={} stalls={} stall_cut={} lines={} bytes={} "',
     '"max_queued_bytes={} sync_lines={} drain_timeouts={}\\n",'),
    ('0c8fcba2', 'src/common/logging/log.cpp', 556,
     'Write(fmt::format("LongFrame: n={} dt_us={} log_async={} t_ms={}\\n", r.n, r.dt_us, r.log_async, r.t_ms));', '}'),
    ('0c8fcba2', 'src/common/logging/log.cpp', 739,
     'Write(fmt::format("LogAsync: mode=1 limit_bytes={} drain_ms={} stall_ms={} flush_ms={}\\n",',
     'Async::kDefaultLimitBytes, Async::kDrainNs / 1000000u, Async::kStallNs / 1000000u,'),
    ('0c8fcba2', 'src/common/logging/log.cpp', 746,
     'Write(fmt::format("TestLogStall: config at_ms={} sleep_ms={} k={} gap_ms={} on={}\\n",',
     'Async::g_stand.at_ns / 1000000u, Async::g_stand.sleep_ms, Async::g_stand.k,'),
    ('0c8fcba2', 'src/graphics/presentation/videoOut.cpp', 1360,
     'Log::LongFrameRecord(r.cfg->flip_status.count, (now_ns - long_frame_prev_ns) / 1000u, now_ns / 1000000u);', '}'),
    ('0c8fcba2', 'src/graphics/presentation/videoOut.cpp', 3614,
     'if (hold_logged.fetch_add(1, std::memory_order_relaxed) < 32) {', 'const uint64_t named = present_ns + poll_ns;'),
    ('0c8fcba2', 'src/graphics/presentation/videoOut.cpp', 3616,
     'LOGF("FlipHold: us=%llu present_us=%llu poll_us=%llu other_us=%llu flip=%llu\\n",',
     'static_cast<unsigned long long>(hold_ns / 1000), static_cast<unsigned long long>(present_ns / 1000),'),
]


def show(commit, path):
    p = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True)
    return p.stdout.decode('utf-8', 'replace').replace('\r\n', '\n').split('\n') if p.returncode == 0 else None


def asc(s):
    return s.encode('ascii', 'backslashreplace').decode('ascii')


def main(argv):
    neg = '--neg' in argv
    print('suite refs_f25m.py sha256 %s target %d references (%s)' % (hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
                                                                     len(ROWS), 'negative control' if neg else 'direct'))
    cache = {}
    bad = 0
    tsv = []
    for c, p, n, a, b in ROWS:
        key = (c, p)
        if key not in cache:
            cache[key] = show(c, p)
        lines = cache[key]
        if neg:
            a = a[:-1] + ('#' if a[-1] != '#' else '%')
        okl = lines is not None and n - 1 < len(lines) and a in lines[n - 1]
        ok1 = lines is not None and n < len(lines) and b in lines[n]
        st = 'OK' if okl and ok1 else 'MISS'
        bad += st != 'OK'
        print('%s %s:%s:%d anchor %s +1 %s' % (st, c, p, n, 'ok' if okl else 'no', 'ok' if ok1 else 'no'))
        tsv.append('%s\t%s\t%d\t%s\t%s\t%s' % (c, p, n, asc(a), asc(b), st))
    if not neg:
        open(os.path.join(HERE, 'refs_f25m.tsv'), 'w', encoding='ascii', newline='\n').write('\n'.join(tsv) + '\n')
    print('refs %d bad %d' % (len(ROWS), bad))
    if neg:
        print('NEG CONTROL OK' if bad == len(ROWS) else 'NEG CONTROL FAILED')
        return 0 if bad == len(ROWS) else 1
    print('ALL OK' if bad == 0 else 'FAILED')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
