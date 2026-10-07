# F25k (HPP-678): the anchors of the report - <commit>:<path>:<line> with the anchor line and the next one (rule 24(1)),
# read from git objects (not the working tree); copy of the f25d/refs_f25d.py form with an expected count per anchor.
# Usage: python refs_f25k.py [commit]  (default 0e4b2f5a - the last F25k commit in main; 2afd998c - binary T; the negative
# control: 7d901aee, the parent - every F25k anchor must miss and the script must print FAILED).
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
R = 'C:/kyty/KytyPS5'
C = sys.argv[1] if len(sys.argv) > 1 else '0e4b2f5a'
L = 'src/common/logging/log.cpp'
REFS = [
    # (path, anchor line, expected count)
    (L, 'constexpr uint64_t kDefaultLimitBytes = uint64_t {256} << 20u;', 1),
    (L, 'static bool g_hooks = false; // g_on or the stand armed: the only check the =0 path adds (WriteImpl, WriteFatal, Flush)', 1),
    (L, 'static bool g_on    = false; // KYTY_FIX_B36=1 and the File direction (Log::Initialize, before any other thread logs)', 1),
    (L, 'static void ParseStand(uint64_t init_ns) {', 1),
    (L, 'static void StandPoint(const std::shared_ptr<spdlog::logger>& logger) {', 1),
    (L, 'static void SinkWrite(const std::shared_ptr<spdlog::logger>& logger, const std::string& line) {', 1),
    (L, '\t\t\tconst auto text = fmt::format("LogAsync: stall us={} queued_bytes={} t_ms={}\\n", ns / 1000u, left,', 1),
    (L, 'static void WriterMain() {', 1),
    (L, '\t\t\tset_fn(GetCurrentThread(), L"LogWriter");', 1),
    (L, '\t\t\t\tstd::lock_guard sink(g_sink_mutex);', 2),
    (L, 'static void Enqueue(std::string_view text) {', 1),
    (L, '\t\tt_nested.append(text.data(), text.size());', 1),
    (L, '\t\t\tstd::unique_lock lock(s.mu);', 1),
    (L, '\t\t\t\ts.cv_space.wait(lock, [&] { return s.closed || s.pending == 0 || s.pending + n <= s.limit; });', 1),
    (L, 'static void Drain(bool close) {', 1),
    (L, '\t\tconst auto done = s.cv_idle.wait_for(lock, std::chrono::nanoseconds(kDrainNs),', 1),
    (L, 'static void WriteSummary() {', 1),
    (L, 'static void ExitDrain() {', 1),
    (L, 'static void Start(uint64_t limit) {', 1),
    (L, 'void Flush() {', 1),
    (L, 'static bool HookWrite(std::string_view text) {', 1),
    (L, '\t\tif (HookWrite(text)) {', 1),
    (L, '\t\t\tAsync::Drain(false); // F25k: the fatal text and everything before it are in the file before the caller dies', 1),
    (L, 'static void InitAsync() {', 1),
    (L, '\t\t\tAsync::ExitDrain(); // F25k: queue -> file, writer stopped, the summary line', 1),
    (L, 'void DrainForExit() noexcept {', 1),
    (L, 'void DrainForFault() noexcept {', 1),
    ('src/common/logging/log.h', 'void      DrainForExit() noexcept;', 1),
    ('src/common/hostException.cpp', '\t\tLog::DrainForFault();', 1),
    ('src/graphics/host_gpu/pageManager.cpp', '\tLog::DrainForExit(); // Track F, F25k (KYTY_FIX_B36): the async log queue to the file; no-op at =0', 2),
    ('src/common/parallelCopy.cpp', '\t\t\tLog::DrainForExit(); // Track F, F25k (KYTY_FIX_B36): the async log queue to the file; no-op at =0', 1),
    ('src/graphics/presentation/videoOut.cpp', '\t\tstatic const bool long_frame = Common::EnvFlagOn("KYTY_LONGFRAME");', 1),
    ('src/graphics/presentation/videoOut.cpp', '\t\t\t\tLOGF("LongFrame: n=%" PRIu64 " dt_us=%llu log_async=%d t_ms=%llu\\n", r.cfg->flip_status.count,', 1),
    ('src/graphics/presentation/videoOut.cpp', '\t\tcur.host_ns = FS::NowNs();', 1),
    ('src/graphics/presentation/videoOut.cpp', '\t\t\t     static_cast<unsigned long long>((cur.host_ns - prev.host_ns) / 1000u),', 1),
    ('src/graphics/presentation/videoOut.cpp', '\tr.cfg->flip_status.count++;', 1),
    ('src/common/assert.cpp', 'static int DbgReport(const char* title, std::string_view text, const char* file, int line) {', 1),
    ('src/common/assert.cpp', 'void DbgExit(int status) {', 1),
    ('src/common/assert.cpp', '\t\tLog::WriteFatal(BuildFatalReport("--- abort() ---", "SIGABRT", "abort", 0));', 1),
    ('src/emulator.cpp', '\tint ok = atexit(KytyClose);', 1),
    ('src/emulator.cpp', '\tok = at_quick_exit(Common::Subsystems::EmergencyShutdownActive);', 1),
    ('src/emulator.cpp', '\tLibs::Graphics::WindowRun();', 1),
    ('src/emulator.cpp', '\tsubsystems.Initialize<Log::Lifecycle>();', 1),
    ('src/graphics/host_gpu/renderer/masterSemaphore.cpp', '\t\t\t\tEXIT("GPU stopped completing submissions\\n");', 1),
    ('CMakeLists.txt', 'add_executable(log_async_tests EXCLUDE_FROM_ALL', 1),
    ('tests/LogAsyncTests.cpp', 'void TestDeath() {', 1),
    ('tests/LogAsyncTests.cpp', 'void TestLatency() {', 1),
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
