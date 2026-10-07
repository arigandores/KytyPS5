# F25k2 (HPP-682): the anchors of the report docs/track-f/f25k2.md - <commit>:<path>:<line> with the anchor line and the
# next one (rule 24(1)), read from git objects (not the working tree); form of f25k/refs_f25k.py, an expected count per
# anchor. Usage: python refs_f25k2.py [commit]  (default 5064c5bb - the F25k2 commit in main; 0c8fcba2 - binary T2; the
# negative control: 297225af, the parent in main (F25k code) - every F25k2 anchor must miss and the script prints FAILED).
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
R = 'C:/kyty/KytyPS5'
C = sys.argv[1] if len(sys.argv) > 1 else '5064c5bb'
L = 'src/common/logging/log.cpp'
T = 'tests/LogAsyncTests.cpp'
V = 'src/graphics/presentation/videoOut.cpp'
REFS = [
    # (path, anchor line, expected count)
    # RC1
    (L, 'static std::mutex&       g_stand_mutex = *new std::mutex; // F25k2 RC1: =0, the stand armed - the old write, the sleep inside', 1),
    (L, 'static std::string StandLineField(std::string_view text) {', 1),
    (L, 'static void StandPoint(const std::shared_ptr<spdlog::logger>& logger, std::string_view text) {', 1),
    (L, '\t\t    fmt::format("TestLogStall: i={} sleep_ms={} slept_us={} t0_ms={} t1_ms={} on={} tid={} role={} line=\\"{}\\"\\n",', 1),
    (L, 'static bool HookWrite(std::string_view text, fmt::text_style style) {', 1),
    (L, '\tconst auto logger = GetLogger(); // before the stand lock: g_logger_mutex is never taken under it', 1),
    (L, '\tstd::lock_guard  stand(Async::g_stand_mutex);', 1),
    (L, '\tAsync::StandPoint(logger, text);', 1),
    (L, '\t\tif (HookWrite(text, style)) {', 1),
    (L, '\t\t\tstd::lock_guard stand(Async::g_stand_mutex);', 1),
    # RC4
    (L, 'static thread_local bool        t_sink_owner = false; // F25k2 RC4: holds g_sink_mutex or g_stand_mutex outside the writer', 1),
    (L, 'struct SinkOwner {', 1),
    (L, '\tif (t_writer || t_in_queue || t_sink_owner) {', 2),
    (L, '\t\tSinkOwner       owner;', 1),
    (L, '\tSinkOwner       owner;', 1),
    (L, '\tAsync::SinkOwner owner;', 1),
    (L, '\t\t\tif (!t_writer && !t_sink_owner && s.pending != 0 && s.pending + n > s.limit) {', 1),
    (L, '\tif (t_sink_owner && g_test_owner_fault.exchange(false)) [[unlikely]] {', 1),
    (L, 'void Testing::FaultInNextOwnerWrite() {', 1),
    # RC2
    (L, 'namespace LongFrame {', 1),
    (L, 'static Rec                   g_recs[kCap];', 1),
    (L, 'static void PrinterMain() {', 1),
    (L, '\t\t\tWrite(fmt::format("LongFrame: n={} dt_us={} log_async={} t_ms={}\\n", r.n, r.dt_us, r.log_async, r.t_ms));', 1),
    (L, 'void LongFrameRecord(uint64_t n, uint64_t dt_us, uint64_t t_ms) {', 1),
    (L, '\tLongFrame::g_published.store(i + 1, std::memory_order_release);', 1),
    (L, '\tLongFrame::g_on = Common::EnvFlagOn("KYTY_LONGFRAME");', 1),
    (L, '\t\tstd::thread(LongFrame::PrinterMain).detach();', 1),
    (L, '\t\tLongFrame::g_stop.store(true); // F25k2 (RC2): the printer writes nothing after the log is shut down', 1),
    (L, 'static void SetThreadName([[maybe_unused]] const wchar_t* name) {', 1),
    ('src/common/logging/log.h', 'void      LongFrameRecord(uint64_t n, uint64_t dt_us, uint64_t t_ms);', 1),
    (V, '\t\t\t\tLog::LongFrameRecord(r.cfg->flip_status.count, (now_ns - long_frame_prev_ns) / 1000u, now_ns / 1000000u);', 1),
    # tests
    (T, 'void TestLongFrame() {', 1),
    (T, 'void TestDieOwner() {', 1),
    (T, '\t\tCHECK(Field(res, "veh_us=") != UINT64_MAX && Field(res, "veh_us=") >= 1400000);', 1),
    (T, '\t\t} else if (mode == "die_owner") {', 1),
    (T, 'int SpawnTimed(const char* mode, const std::string& path, int n, const char* fix, const char* stall, DWORD limit_ms,', 1),
]
ok = True
for p, a, want in REFS:
    r = subprocess.run([G, '-C', R, 'show', '%s:%s' % (C, p)], capture_output=True)
    lines = r.stdout.decode('utf-8', 'replace').split('\n')
    hits = [i for i, l in enumerate(lines) if l == a]
    if len(hits) != want:
        print('MISS %d/%d %s:%s %r' % (len(hits), want, C, p, a))
        ok = False
        continue
    for i in hits:
        print('`%s:%s:%d` (якорь «%s»; +1 — «%s»)' % (C, p, i + 1, a.strip(), lines[i + 1].strip()))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
