# F25e (HPP-668, Red Team): check of the <commit>:<path>:<line> references of docs/track-f/f25e-review.md - the anchor is
# the whole stripped line, +1 is the whole stripped next line (general rule 24(1)). Usage:
#   python refs_f25e.py            -> prints one line per reference and ALL OK / FAILED
#   python refs_f25e.py --neg      -> the same references read at f2307b02 (F20j4) for the F25 files: must print FAILED
import subprocess
import sys

REFS = [
    ('35b454c6', 'src/common/diagB32.h', 61,
     'constexpr uint32_t kHist          = 4096;      // per-slot history ring: 4096 samples x 5 ms = 20.48 s (F25 C1)',
     'constexpr uint32_t kWaitRing      = 65536;     // F25 C2'),
    ('35b454c6', 'src/common/diagB32.cpp', 188,
     'g.i2_ok               = period_ns > 0 && static_cast<uint64_t>(n) >= window / (2 * period_ns);',
     'return g;'),
    ('35b454c6', 'src/common/diagB32.cpp', 210, 'return std::max(begin_ns + kPeriodNs, now_ns);', '}'),
    ('35b454c6', 'src/common/diagB32.cpp', 230, 'for (const size_t j: snaps) {',
     'const auto d = t[i] > kq_t[j] ? t[i] - kq_t[j] : kq_t[j] - t[i];'),
    ('35b454c6', 'src/common/diagB32.cpp', 383, 'WaitRec r;',
     'r.start_ns     = x.start.load(std::memory_order_relaxed);'),
    ('35b454c6', 'src/common/diagB32.cpp', 428, 'if (m_pos[static_cast<size_t>(s)] < 0) {',
     'm_pos[static_cast<size_t>(s)] = static_cast<int32_t>(i);'),
    ('35b454c6', 'src/common/diagB32.cpp', 473,
     'if (in_must[i] == 0 && std::find(set.begin(), set.end(), r.waits[i].slot1) != set.end()) {',
     'in_must[i] = 1;'),
    ('35b454c6', 'src/common/diagB32.cpp', 493, 'std::vector<size_t> out = must;', '*cut                    = 0;'),
    ('35b454c6', 'src/common/diagB32.cpp', 1296, '::Log::Write(best->text);', '}'),
    ('35b454c6', 'src/common/diagB32.cpp', 1789,
     'm_c.hist_exh++;  // F25d (item 596(v), C3): the same event, its own counter', '}'),
    ('35b454c6', 'src/common/diagB32.cpp', 1813,
     'r.cover_us     = times.empty() ? 0 : (flip_ns - times.front()) / 1000u; // F25d (item 596(v), C4)',
     'r.kstate       = g_kstate.load(std::memory_order_relaxed);'),
    ('35b454c6', 'src/common/diagB32.cpp', 1877, 'w.open     = 1;', 'r.waits.push_back(w);'),
    ('35b454c6', 'src/common/diagB32.cpp', 1894, 'r.waits.erase(std::remove_if(r.waits.begin(), r.waits.end(),',
     '[&](const Core::WaitRec& o) {'),
    ('35b454c6', 'src/common/diagB32.cpp', 2108, 'if (!g_on) {', 'return;'),
    ('35b454c6', 'src/graphics/presentation/videoOut.cpp', 1281, 'm_mutex.Lock();',
     'if (m_requests.empty() || m_requests.front().id != r.id ||'),
    ('35b454c6', 'src/graphics/presentation/videoOut.cpp', 1293,
     'Common::DiagB32::OnFlip(r.cfg->flip_status.count, r.id, r.reserve_host_ns);', '}'),
    ('24ce64ea', 'docs/track-f/f20l3/b32_read.py', 125,
     "ZERO_W = ('slot_full_w', 'torn_w', 'ring_drop_w', 'sgap_bad_w', 'lines_cut_w', 'req_miss_w', 'sub_miss_w')",
     "DRIVER = ('present', 'acquire', 'qsubmit', 'semwait')"),
    ('24ce64ea', 'docs/track-f/f20l3/b32_read.py', 596,
     "res['zero_w_sum'] = dict((k, sum(num((d['x'] or {}).get(k), 0) or 0 for d in diag.values())) for k in ZERO_W)",
     'lastx = None'),
    ('24ce64ea', 'docs/track-f/f20l3/b32_read.py', 1003, "bad = any((r.get('zero_w_sum') or {}).values())",
     'nz += 1 if bad else 0'),
]

neg = '--neg' in sys.argv
ok = True
cache = {}
for commit, path, line, anchor, nxt in REFS:
    if neg and path.startswith('src/common/diagB32'):
        commit = 'f2307b02'
    key = (commit, path)
    if key not in cache:
        r = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', commit + ':' + path], capture_output=True)
        cache[key] = r.stdout.decode('utf-8', 'replace').split('\n')
    t = cache[key]
    a = t[line - 1].strip() if line - 1 < len(t) else None
    b = t[line].strip() if line < len(t) else None
    good = a == anchor and b == nxt
    ok &= good
    print('%s %s:%s:%d' % ('ok  ' if good else 'FAIL', commit, path, line))
print('%d references' % len(REFS))
print('ALL OK' if ok else 'FAILED')
