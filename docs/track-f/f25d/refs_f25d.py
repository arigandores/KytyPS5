# F25d (HPP-667): the anchors of the report - <commit>:<path>:<line> with the anchor line and the next one (rule 24(1)),
# read from git objects (not the working tree). Prints ALL OK if every anchor is found exactly once.
import subprocess, sys
G = 'C:/Program Files/Git/cmd/git.exe'
R = 'C:/kyty/KytyPS5'
REFS = [
    ('35b454c6', 'src/common/diagB32.h', 'constexpr uint32_t kHist          = 4096;      // per-slot history ring: 4096 samples x 5 ms = 20.48 s (F25 C1)'),
    ('35b454c6', 'src/common/diagB32.h', 'constexpr uint32_t kWaitRing      = 65536;     // F25 C2'),
    ('35b454c6', 'src/common/diagB32.h', 'constexpr uint32_t kOthersCap     = 256;       // RC2: the cap applies only to the non-mandatory -t lines (F25 C5g)'),
    ('35b454c6', 'src/common/diagB32.h', 'constexpr uint32_t kMustCap       = 256;       // a mandatory -t line beyond this is cut and counted in lines_cut (F25 C5b)'),
    ('35b454c6', 'src/common/diagB32.h', 'constexpr uint32_t kWLinesCap     = 4096;      // F25 C5a'),
    ('35b454c6', 'src/common/diagB32.h', '#define KYTY_DIAG_B32_F25 1'),
    ('35b454c6', 'src/common/diagB32.h', '\tuint64_t hist_exh     = 0;'),
    ('35b454c6', 'src/common/diagB32.h', '\tuint64_t cover_us     = 0;'),
    ('35b454c6', 'src/common/diagB32.h', 'BenchOut CloseWindowBench(const BenchIn& in);'),
    ('35b454c6', 'src/common/diagB32.cpp', '\t\tfor (const size_t j: snaps) {'),
    ('35b454c6', 'src/common/diagB32.cpp', 'class RowIndex {'),
    ('35b454c6', 'src/common/diagB32.cpp', '\tstd::vector<char> in_must(r.waits.size(), 0);'),
    ('35b454c6', 'src/common/diagB32.cpp', '\t       " cover_us=%llu flip_ns=%llu\\n", // F25d (items 596(v) C4, 599(b)(11) C6): flip_ns - the FrameStats::NowNs scale, last'),
    ('35b454c6', 'src/common/diagB32.cpp', '\t       " ring_hold=%llu ring_hold_w=%llu hist_exh=%llu hist_exh_w=%llu w_cut_w=%llu others_cut_w=%llu\\n",'),
    ('35b454c6', 'src/common/diagB32.cpp', '\tbase.hist_exh  = hist_exh;   // F25d C3'),
    ('35b454c6', 'src/common/diagB32.cpp', '\t\tm_c.hist_exh++;  // F25d (item 596(v), C3): the same event, its own counter'),
    ('35b454c6', 'src/common/diagB32.cpp', '\tr.cover_us     = times.empty() ? 0 : (flip_ns - times.front()) / 1000u; // F25d (item 596(v), C4)'),
    ('35b454c6', 'src/common/diagB32.cpp', '\t\tstd::vector<std::pair<int32_t, uint64_t>> keys;'),
    ('35b454c6', 'src/common/diagB32.cpp', 'BenchOut CloseWindowBench(const BenchIn& in) {'),
    ('35b454c6', 'src/common/diagB32.cpp', '\tg_reg  = new Core::Registry;'),
    ('35b454c6', 'src/common/frameStats.cpp', 'uint64_t NowNs() {'),
    ('35b454c6', 'src/common/frameStats.cpp', '\t\treturn static_cast<uint64_t>(static_cast<double>(__rdtsc()) / cycles_per_ns);'),
    ('35b454c6', 'src/common/frameStats.cpp', 'double TscCyclesPerNs() {'),
    ('35b454c6', 'src/common/frameStats.cpp', '\t\twhile (Qpc() - q0 < f / 50) {'),
    ('35b454c6', 'tests/DiagB32Tests.cpp', '\tconstexpr uint32_t kN = kWaitRing + 904; // F25d RC9: was 5000 at kWaitRing 4096'),
    ('35b454c6', 'tests/DiagB32Tests.cpp', '\t\tCHECK(c.w_cut == (kWLinesCap + 17) - kWLinesCap);'),
    ('35b454c6', 'tests/DiagB32Tests.cpp', '\t\tconstexpr int kMust = static_cast<int>(kMustCap) + 4;'),
    ('35b454c6', 'tests/DiagB32Tests.cpp', 'static void TestF25CloseTime() {'),
]
ok = True
for c, p, a in REFS:
    lines = subprocess.run([G, '-C', R, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    hits = [i for i, l in enumerate(lines) if l == a]
    if len(hits) != 1:
        print('MISS %d %s:%s %r' % (len(hits), c, p, a)); ok = False; continue
    i = hits[0]
    print('`%s:%s:%d` (якорь «%s»; +1 — «%s»)' % (c, p, i + 1, a.strip(), lines[i + 1].strip()))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
