# F25l2 (HPP-683): the <commit>:<path>:<line> references of f25l2-review.md - anchor line and +1 line read from git objects.
# Usage: python refs_f25l2.py <commit>   (prints ALL OK or FAILED)
import subprocess, sys
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
L = 'src/common/logging/log.cpp'
V = 'src/graphics/presentation/videoOut.cpp'
REFS = [
    (L, 149, 'static std::mutex&       g_stand_mutex = *new std::mutex;', 'static std::atomic<uint64_t> g_pending_bytes {0};'),
    (L, 158, 'static thread_local bool        t_sink_owner = false;', ''),
    (L, 163, 'struct SinkOwner {', 'SinkOwner(): prev(t_sink_owner) { t_sink_owner = true; }'),
    (L, 228, 'static std::string StandLineField(std::string_view text) {', 'std::string out(text.substr(0, 40));'),
    (L, 273, 'if (t_sink_owner && g_test_owner_fault.exchange(false)) [[unlikely]] {', '*static_cast<volatile int*>(nullptr) = 1;'),
    (L, 412, 'if (!t_writer && !t_sink_owner && s.pending != 0 && s.pending + n > s.limit) {', 'const auto t0 = NowNs();'),
    (L, 447, 'if (t_writer || t_in_queue || t_sink_owner) {', 'return;'),
    (L, 471, 'SinkOwner       owner;', 'uint64_t        written = 0;'),
    (L, 500, 'SinkOwner       owner;', 'if (const auto logger = GetLoggerLocked()) {'),
    (L, 509, 'if (t_writer || t_in_queue || t_sink_owner) {', 'return;'),
    (L, 548, 'static void PrinterMain() {', 'Async::SetThreadName(L"LongFramePrinter");'),
    (L, 563, 'void LongFrameRecord(uint64_t n, uint64_t dt_us, uint64_t t_ms) {', 'if (!LongFrame::g_on) {'),
    (L, 589, 'if (!Async::t_sink_owner) {', 'std::lock_guard stand(Async::g_stand_mutex);'),
    (L, 603, 'static void SetupLogger() {', 'std::lock_guard lock(g_logger_mutex);'),
    (L, 641, 'if (Async::t_sink_owner) {', 'return false;'),
    (L, 644, 'const auto logger = GetLogger();', 'if (logger == nullptr) {'),
    (L, 648, 'std::lock_guard  stand(Async::g_stand_mutex);', 'Async::SinkOwner owner;'),
    (L, 650, 'Async::StandPoint(logger, text);', '// The old write of WriteImpl, unchanged.'),
    (L, 675, 'if (Async::g_hooks) [[unlikely]] {', 'if (HookWrite(text, style)) {'),
    (L, 751, 'LongFrame::g_on = Common::EnvFlagOn("KYTY_LONGFRAME");', 'if (LongFrame::g_on) {'),
    (L, 754, 'std::thread(LongFrame::PrinterMain).detach();', '}'),
    (L, 767, 'SetupLogger();', 'InitAsync();'),
    (L, 852, 'const auto t0 = Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;', 'WriteImpl(text);'),
    (V, 1366, 'Log::LongFrameRecord(r.cfg->flip_status.count, (now_ns - long_frame_prev_ns) / 1000u, now_ns / 1000000u);', '}'),
    ('src/emulator.cpp', 148, 'subsystems.Initialize<Log::Lifecycle>();', ''),
]
c = sys.argv[1]
bad = 0
cache = {}
for path, n, a, b in REFS:
    if path not in cache:
        cache[path] = subprocess.run([GIT, '-C', REPO, 'show', c + ':' + path], capture_output=True).stdout.decode('utf-8', 'replace').split('\n')
    lines = cache[path]
    ok = n - 1 < len(lines) and a in lines[n - 1] and (b == '' or (n < len(lines) and b in lines[n]))
    print('%s %s:%s:%d' % ('ok  ' if ok else 'MISS', c, path, n))
    bad += 0 if ok else 1
print('refs %d miss %d' % (len(REFS), bad))
print('ALL OK' if bad == 0 else 'FAILED')
