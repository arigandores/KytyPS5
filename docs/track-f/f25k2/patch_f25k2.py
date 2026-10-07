# F25k2 (HPP-682, ROADMAP s122 item 616(b)(1)-(3), (v)): RC1, RC2, RC4 of the review F25l (5e57aea8:docs/track-f/f25l-review.md
# section 4) in KYTY_FIX_B36 / the stand KYTY_TEST_LOGSTALL / the measure KYTY_LONGFRAME, and the tests.
# Usage: python patch_f25k2.py <repo root>   (the F25k2 worktree or C:/kyty/KytyPS5). Anchors are whole lines; every
# anchor must occur exactly once; the files are read and written as LF bytes (CR stripped before the search and put back
# if the file had CRLF).
import sys

ROOT = sys.argv[1].rstrip('/')


def load(rel):
    b = open(ROOT + '/' + rel, 'rb').read()
    crlf = b'\r\n' in b
    return b.replace(b'\r\n', b'\n').decode('utf-8'), crlf


def save(rel, text, crlf):
    b = text.encode('utf-8')
    if crlf:
        b = b.replace(b'\n', b'\r\n')
    open(ROOT + '/' + rel, 'wb').write(b)


def lines_block(text, block):
    # block: whole lines (ends with a newline); must start at a line start
    n = 0
    pos = 0
    while True:
        i = text.find(block, pos)
        if i < 0:
            break
        if i == 0 or text[i - 1] == '\n':
            n += 1
        pos = i + 1
    return n


def replace(text, old, new, what):
    n = lines_block(text, old)
    if n != 1:
        raise SystemExit('anchor %s: %d occurrences' % (what, n))
    return text.replace(old, new, 1)


# ------------------------------------------------------------------------------------------------------------ log.cpp
rel = 'src/common/logging/log.cpp'
t, crlf = load(rel)

t = replace(t, r'''// after Log::Initialize, <k> times (3 by default) at least 5 s apart.
namespace Async {
''', r'''// after Log::Initialize, <k> times (3 by default) at least 5 s apart.
// F25k2 (HPP-682; ROADMAP s122 item 616(b)(1)-(3), RC1, RC2, RC4 of F25l): at =0 with the stand armed the old write runs
// under one per-process stand lock, the stand's sleep inside it before the write (the sleep holds the write as a real
// delay of the file holds the lock of basic_file_sink_mt: every writing thread waits); t_sink_owner marks a thread that
// holds g_sink_mutex or the stand lock outside the writer - a drain on it returns at once (the process dies, as at =0);
// the KYTY_LONGFRAME records go to a static array, a thread off the frame path prints them (namespace LongFrame).
namespace Async {
''', 'async header')

t = replace(t, r'''static std::mutex&       g_sink_mutex = *new std::mutex; // the writer's batch; a timed-out drain writes its rest after it
''', r'''static std::mutex&       g_sink_mutex = *new std::mutex; // the writer's batch; a timed-out drain writes its rest after it
static std::mutex&       g_stand_mutex = *new std::mutex; // F25k2 RC1: =0, the stand armed - the old write, the sleep inside
''', 'stand mutex')

t = replace(t, r'''static thread_local std::string t_nested;           // lines of an exception handler that interrupted this thread's push
''', r'''static thread_local std::string t_nested;           // lines of an exception handler that interrupted this thread's push
static thread_local bool        t_sink_owner = false; // F25k2 RC4: holds g_sink_mutex or g_stand_mutex outside the writer

// F25k2 (RC4): t_sink_owner for the life of a sink lock held outside the writer - the synchronous tail of Drain,
// WriteSummary, the =0 write of the stand. Declared after the lock: cleared before the lock is released, on every exit of
// the scope (also an exception); the previous value is restored.
struct SinkOwner {
	SinkOwner(): prev(t_sink_owner) { t_sink_owner = true; }
	~SinkOwner() { t_sink_owner = prev; }
	SinkOwner(const SinkOwner&)            = delete;
	SinkOwner& operator=(const SinkOwner&) = delete;
	bool prev;
};

static std::atomic<bool> g_test_owner_fault {false}; // log_async_tests only (Testing::FaultInNextOwnerWrite, RC4)
''', 'tls owner')

t = replace(t, r'''static void StandPoint(const std::shared_ptr<spdlog::logger>& logger) {
''', r'''// F25k2 (RC1): the "line=" field - the first <= 40 bytes of the line that took the sleep; a non-printable byte, '"' and '\'
// are written as '?'.
static std::string StandLineField(std::string_view text) {
	std::string out(text.substr(0, 40));
	for (auto& c: out) {
		const auto u = static_cast<unsigned char>(c);
		if (u < 0x20u || u >= 0x7fu || c == '"' || c == '\\') {
			c = '?';
		}
	}
	return out;
}

static void StandPoint(const std::shared_ptr<spdlog::logger>& logger, std::string_view text) {
''', 'standpoint sig')

t = replace(t, r'''		const auto line = fmt::format("TestLogStall: i={} sleep_ms={} slept_us={} t0_ms={} t1_ms={} on={} tid={} role={}\n",
		                              i + 1, g_stand.sleep_ms, (t1 - t0) / 1000u, t0 / 1000000u, t1 / 1000000u,
		                              t_writer ? "writer" : "caller", OsTid(), RoleName());
''', r'''		const auto line =
		    fmt::format("TestLogStall: i={} sleep_ms={} slept_us={} t0_ms={} t1_ms={} on={} tid={} role={} line=\"{}\"\n",
		                i + 1, g_stand.sleep_ms, (t1 - t0) / 1000u, t0 / 1000000u, t1 / 1000000u,
		                t_writer ? "writer" : "caller", OsTid(), RoleName(), StandLineField(text));
''', 'standpoint line')

t = replace(t, r'''	const auto t0 = NowNs();
	StandPoint(logger);
	logger->log(spdlog::level::info, spdlog::string_view_t(line.data(), line.size()));
''', r'''	const auto t0 = NowNs();
	StandPoint(logger, line);
	if (t_sink_owner && g_test_owner_fault.exchange(false)) [[unlikely]] {
		*static_cast<volatile int*>(nullptr) = 1; // log_async_tests die_owner (RC4): a fault inside a write under the sink lock
	}
	logger->log(spdlog::level::info, spdlog::string_view_t(line.data(), line.size()));
''', 'sinkwrite')

t = replace(t, r'''static void WriterMain() {
	t_writer = true;
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	// The thread name "LogWriter" for the KYTY_DIAG_B32 thread rows (looked up as diagB32.cpp does for DiagB32M5).
	using SetThreadDescriptionFn = HRESULT(WINAPI*)(HANDLE, PCWSTR);
	if (HMODULE k32 = GetModuleHandleW(L"kernel32.dll"); k32 != nullptr) {
		if (auto set_fn = reinterpret_cast<SetThreadDescriptionFn>(
		        reinterpret_cast<void*>(GetProcAddress(k32, "SetThreadDescription")));
		    set_fn != nullptr) {
			set_fn(GetCurrentThread(), L"LogWriter");
		}
	}
#endif
''', r'''// The thread name for the KYTY_DIAG_B32 thread rows (looked up as diagB32.cpp does for DiagB32M5).
static void SetThreadName([[maybe_unused]] const wchar_t* name) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	using SetThreadDescriptionFn = HRESULT(WINAPI*)(HANDLE, PCWSTR);
	if (HMODULE k32 = GetModuleHandleW(L"kernel32.dll"); k32 != nullptr) {
		if (auto set_fn = reinterpret_cast<SetThreadDescriptionFn>(
		        reinterpret_cast<void*>(GetProcAddress(k32, "SetThreadDescription")));
		    set_fn != nullptr) {
			set_fn(GetCurrentThread(), name);
		}
	}
#endif
}

static void WriterMain() {
	t_writer = true;
	SetThreadName(L"LogWriter");
''', 'writermain name')

t = replace(t, r'''			if (!t_writer && s.pending != 0 && s.pending + n > s.limit) {
''', r'''			// Not the writer, and not a thread that holds the sink lock (F25k2 RC4: an exception handler on it would wait
			// for space the writer cannot make).
			if (!t_writer && !t_sink_owner && s.pending != 0 && s.pending + n > s.limit) {
''', 'enqueue full')

t = replace(t, r'''// dropped. Not on the writer (it holds the sink) and not inside this thread's own push (an exception handler there).
static void Drain(bool close) {
	auto& s = g_state;
	if (t_writer || t_in_queue) {
		return;
	}
''', r'''// dropped. Not on the writer (it holds the sink), not inside this thread's own push (an exception handler there) and not
// on a thread that holds the sink lock outside the writer (F25k2 RC4: a fault inside the synchronous tail below or inside
// WriteSummary - the drain of the exception filter would wait 5 s and lock g_sink_mutex again on the same thread).
static void Drain(bool close) {
	auto& s = g_state;
	if (t_writer || t_in_queue || t_sink_owner) {
		return;
	}
''', 'drain guard')

t = replace(t, r'''	if (!rest.empty()) {
		std::lock_guard sink(g_sink_mutex);
		uint64_t        written = 0;
''', r'''	if (!rest.empty()) {
		std::lock_guard sink(g_sink_mutex);
		SinkOwner       owner;
		uint64_t        written = 0;
''', 'drain owner')

t = replace(t, r'''	std::lock_guard sink(g_sink_mutex);
	if (const auto logger = GetLoggerLocked()) {
		logger->log(spdlog::level::info, spdlog::string_view_t(text.data(), text.size()));
		logger->flush();
	}
}
''', r'''	std::lock_guard sink(g_sink_mutex);
	SinkOwner       owner;
	if (const auto logger = GetLoggerLocked()) {
		logger->log(spdlog::level::info, spdlog::string_view_t(text.data(), text.size()));
		logger->flush();
	}
}
''', 'summary owner')

t = replace(t, r'''static void ExitDrain() {
	if (t_writer || t_in_queue) {
		return;
	}
''', r'''static void ExitDrain() {
	if (t_writer || t_in_queue || t_sink_owner) {
		return;
	}
''', 'exitdrain guard')

t = replace(t, r'''} // namespace Async

void Flush() {
''', r'''} // namespace Async

// Track F, F25k2 (KYTY_LONGFRAME=1; RC2 of F25l, ROADMAP s122 item 616(b)(2)): the measure of a long flip without log I/O
// on the frame path. The Present thread (one producer: FlipQueue::Flip under FlipQueue::m_mutex) fills a slot of a static
// array (no allocation, no I/O, no lock) and publishes it by an atomic counter (release); a printer thread off the frame
// path polls the counter every 250 ms and writes the "LongFrame:" lines (the form of F25k) by Log::Write: it takes no lock
// of the emulator, only those of the log (g_logger_mutex; the queue at =1; the stand lock and the sink at =0). The thread
// exists only with KYTY_LONGFRAME on. Records of the last <= 250 ms before the exit (and a print in progress) may not
// reach the file; after Log::Shutdown the printer stops.
namespace LongFrame {

constexpr uint32_t kCap    = 4096;
constexpr uint32_t kPollMs = 250;

struct Rec {
	uint64_t n;
	uint64_t dt_us;
	uint64_t t_ms;
	uint32_t log_async;
};

static Rec                   g_recs[kCap];
static std::atomic<uint32_t> g_published {0};
static std::atomic<bool>     g_stop {false};
static std::atomic<bool>     g_started {false};
static bool                  g_on = false; // KYTY_LONGFRAME (Log::Initialize, before any other thread)

static void PrinterMain() {
	Async::SetThreadName(L"LongFramePrinter");
	uint32_t printed = 0;
	while (printed < kCap && !g_stop.load(std::memory_order_relaxed)) {
		std::this_thread::sleep_for(std::chrono::milliseconds(kPollMs));
		const uint32_t published = g_published.load(std::memory_order_acquire);
		for (; printed < published && !g_stop.load(std::memory_order_relaxed); printed++) {
			const auto& r = g_recs[printed];
			Write(fmt::format("LongFrame: n={} dt_us={} log_async={} t_ms={}\n", r.n, r.dt_us, r.log_async, r.t_ms));
		}
	}
}

} // namespace LongFrame

void LongFrameRecord(uint64_t n, uint64_t dt_us, uint64_t t_ms) {
	if (!LongFrame::g_on) {
		return;
	}
	const uint32_t i = LongFrame::g_published.load(std::memory_order_relaxed); // one producer at a time (the caller's lock)
	if (i >= LongFrame::kCap) {
		return;
	}
	LongFrame::g_recs[i] = {n, dt_us, t_ms, Async::g_on ? 1u : 0u};
	LongFrame::g_published.store(i + 1, std::memory_order_release);
}

void Flush() {
''', 'longframe')

t = replace(t, r'''			std::lock_guard lock(Async::g_state.mu);
			Async::g_state.flush_req = true;
			Async::g_state.cv_writer.notify_one();
			return;
		}
	}
	if (g_logger != nullptr) {
		g_logger->flush();
	}
}
''', r'''			std::lock_guard lock(Async::g_state.mu);
			Async::g_state.flush_req = true;
			Async::g_state.cv_writer.notify_one();
			return;
		}
		// F25k2 (RC1): =0 with the stand armed - the flush waits for the stand's sleep, as a real delay of the file makes
		// it wait for the lock of the sink (not on a thread that already holds the stand lock).
		if (!Async::t_sink_owner) {
			std::lock_guard stand(Async::g_stand_mutex);
			Async::SinkOwner owner;
			if (g_logger != nullptr) {
				g_logger->flush();
			}
			return;
		}
	}
	if (g_logger != nullptr) {
		g_logger->flush();
	}
}
''', 'flush stand')

t = replace(t, r'''// KYTY_FIX_B36 / KYTY_TEST_LOGSTALL (F25k): true - the line is taken (queued); false - the old path writes it (the
// stand point, if armed, has run on this thread right before the old write).
static bool HookWrite(std::string_view text) {
	if (Async::g_on) {
		Async::Enqueue(text);
		return true;
	}
	if (const auto logger = GetLogger()) {
		Async::StandPoint(logger);
	}
	return false;
}
''', r'''// KYTY_FIX_B36 / KYTY_TEST_LOGSTALL (F25k, F25k2): true - the line is taken: queued at =1; at =0 with the stand armed
// written here by the old write under the stand lock, the stand's sleep inside it right before the write (RC1 of F25l:
// the sleep holds the write, every writing thread waits for it); false - the old path writes it (a thread that already
// holds the stand lock: an exception handler interrupted its write).
static bool HookWrite(std::string_view text, fmt::text_style style) {
	if (Async::g_on) {
		Async::Enqueue(text);
		return true;
	}
	if (Async::t_sink_owner) {
		return false;
	}
	const auto logger = GetLogger(); // before the stand lock: g_logger_mutex is never taken under it
	if (logger == nullptr) {
		return true; // the old path writes nothing either
	}
	std::lock_guard  stand(Async::g_stand_mutex);
	Async::SinkOwner owner;
	Async::StandPoint(logger, text);
	// The old write of WriteImpl, unchanged.
	if (g_direction == Direction::Console && HasStyle(style)) {
		const auto styled = fmt::format(style, "{}", text);
		logger->log(spdlog::level::info, spdlog::string_view_t(styled.data(), styled.size()));
	} else {
		logger->log(spdlog::level::info, spdlog::string_view_t(text.data(), text.size()));
	}
	return true;
}
''', 'hookwrite')

t = replace(t, r'''		if (HookWrite(text)) {
''', r'''		if (HookWrite(text, style)) {
''', 'hookwrite call')

t = replace(t, r'''	if (Async::g_stand.armed) {
		Write(fmt::format("TestLogStall: config at_ms={} sleep_ms={} k={} gap_ms={} on={}\n",
		                  Async::g_stand.at_ns / 1000000u, Async::g_stand.sleep_ms, Async::g_stand.k,
		                  Async::kStandGapNs / 1000000u, Async::g_on ? "writer" : "caller"));
	}
}
''', r'''	if (Async::g_stand.armed) {
		Write(fmt::format("TestLogStall: config at_ms={} sleep_ms={} k={} gap_ms={} on={}\n",
		                  Async::g_stand.at_ns / 1000000u, Async::g_stand.sleep_ms, Async::g_stand.k,
		                  Async::kStandGapNs / 1000000u, Async::g_on ? "writer" : "caller"));
	}
	// F25k2 (RC2): the printer thread of KYTY_LONGFRAME - only with the measure on.
	LongFrame::g_on = Common::EnvFlagOn("KYTY_LONGFRAME");
	if (LongFrame::g_on) {
		LongFrame::g_started.store(true);
		std::thread(LongFrame::PrinterMain).detach();
	}
}
''', 'initasync longframe')

t = replace(t, r'''void Shutdown() {
	if (Async::g_hooks) [[unlikely]] {
''', r'''void Shutdown() {
	if (LongFrame::g_on) [[unlikely]] {
		LongFrame::g_stop.store(true); // F25k2 (RC2): the printer writes nothing after the log is shut down
	}
	if (Async::g_hooks) [[unlikely]] {
''', 'shutdown longframe')

t = replace(t, r'''void Testing::SetAsyncLimit(uint64_t bytes) {
	std::lock_guard lock(Async::g_state.mu);
	Async::g_state.limit = bytes;
}
''', r'''void Testing::SetAsyncLimit(uint64_t bytes) {
	std::lock_guard lock(Async::g_state.mu);
	Async::g_state.limit = bytes;
}

void Testing::FaultInNextOwnerWrite() {
	Async::g_test_owner_fault.store(true);
}

bool Testing::LongFramePrinterStarted() {
	return LongFrame::g_started.load();
}
''', 'testing')

save(rel, t, crlf)
print('patched', rel)

# -------------------------------------------------------------------------------------------------------------- log.h
rel = 'src/common/logging/log.h'
t, crlf = load(rel)
t = replace(t, r'''// KYTY_FIX_B36=1 in effect (the File direction): the "log_async" field of the "LongFrame:" line.
bool      AsyncEnabled();
namespace Testing {
// log_async_tests only: the 256 MiB limit of the queue replaced.
void SetAsyncLimit(uint64_t bytes);
} // namespace Testing
''', r'''// KYTY_FIX_B36=1 in effect (the File direction): the "log_async" field of the "LongFrame:" line.
bool      AsyncEnabled();
// Track F, F25k2 (KYTY_LONGFRAME=1; RC2 of F25l, ROADMAP s122 item 616(b)(2)): one record of a flip >= 100 ms - stored in a
// static array without log I/O on the calling thread; a printer thread off the frame path writes the "LongFrame:" line.
// One producer at a time (FlipQueue::Flip under FlipQueue::m_mutex); at most 4 096 records. No-op without KYTY_LONGFRAME.
void      LongFrameRecord(uint64_t n, uint64_t dt_us, uint64_t t_ms);
namespace Testing {
// log_async_tests only: the 256 MiB limit of the queue replaced.
void SetAsyncLimit(uint64_t bytes);
// log_async_tests only (F25k2, RC4): the next sink write by a thread that holds the sink lock outside the writer faults.
void FaultInNextOwnerWrite();
// log_async_tests only (F25k2, RC2): the printer thread of KYTY_LONGFRAME was created.
bool LongFramePrinterStarted();
} // namespace Testing
''', 'log.h')
save(rel, t, crlf)
print('patched', rel)

# --------------------------------------------------------------------------------------------------------- videoOut.cpp
rel = 'src/graphics/presentation/videoOut.cpp'
t, crlf = load(rel)
t = replace(t, r'''	// under m_mutex. t_ms - the same clock, for the t0_ms / t1_ms of the stand's "TestLogStall:" line.
	{
		static const bool long_frame = Common::EnvFlagOn("KYTY_LONGFRAME");
		if (long_frame) [[unlikely]] {
			static uint64_t long_frame_prev_ns = 0;
			static uint32_t long_frame_lines   = 0;
			const uint64_t  now_ns             = Common::FrameStats::NowNs();
			if (long_frame_prev_ns != 0 && now_ns - long_frame_prev_ns >= 100000000u && long_frame_lines < 4096) {
				long_frame_lines++;
				LOGF("LongFrame: n=%" PRIu64 " dt_us=%llu log_async=%d t_ms=%llu\n", r.cfg->flip_status.count,
				     static_cast<unsigned long long>((now_ns - long_frame_prev_ns) / 1000u), Log::AsyncEnabled() ? 1 : 0,
				     static_cast<unsigned long long>(now_ns / 1000000u));
			}
			long_frame_prev_ns = now_ns;
		}
	}
''', r'''	// under m_mutex. t_ms - the same clock, for the t0_ms / t1_ms of the stand's "TestLogStall:" line. F25k2 (RC2 of F25l,
	// ROADMAP s122 item 616(b)(2)): no log write on this thread - Log::LongFrameRecord stores the record (at most 4 096) in a
	// static array, a thread off the frame path prints the line.
	{
		static const bool long_frame = Common::EnvFlagOn("KYTY_LONGFRAME");
		if (long_frame) [[unlikely]] {
			static uint64_t long_frame_prev_ns = 0;
			const uint64_t  now_ns             = Common::FrameStats::NowNs();
			if (long_frame_prev_ns != 0 && now_ns - long_frame_prev_ns >= 100000000u) {
				Log::LongFrameRecord(r.cfg->flip_status.count, (now_ns - long_frame_prev_ns) / 1000u, now_ns / 1000000u);
			}
			long_frame_prev_ns = now_ns;
		}
	}
''', 'videoOut longframe')
save(rel, t, crlf)
print('patched', rel)

# ---------------------------------------------------------------------------------------------------- LogAsyncTests.cpp
rel = 'tests/LogAsyncTests.cpp'
t, crlf = load(rel)
t = replace(t, r'''//    with TerminateProcess and no drain - lines must be missing.
''', r'''//    with TerminateProcess and no drain - lines must be missing.
// F25k2 (HPP-682; ROADMAP s122 item 616(b)(1)-(3), (v)):
//  * latency_0 (RC1): at =0 the stand's sleep holds the write - the second writer (the exception handler) waits too
//    (veh_us >= 1 400 000); the "TestLogStall:" line carries line="..." (the line that took the sleep);
//  * longframe_0 / longframe_1 (RC2): with KYTY_LONGFRAME=1 Log::LongFrameRecord does not wait while the stand holds the
//    write (=0) or the writer (=1) - the longest record < 50 ms; the printer thread writes the "LongFrame:" lines (4 100
//    records -> 4 096 lines, in order, the fields as recorded); longframe_off - without the measure the printer thread is
//    not created and no line is written;
//  * die_owner (RC4): the dying thread faults inside a write under the sink lock (the synchronous tail of a timed-out
//    drain of EXIT): the drain of the exception filter returns at once - the child dies (0xC0000005) within 10 s. The
//    parent kills a child alive after 40 s ("hung"). Run with "--case die_owner" on a build without the RC4 guard - the
//    positive control (run_tests_f25k2.py t5).
''', 'tests header')

t = replace(t, r'''			max_us = std::max(max_us, NowUs() - t0);
		}
		WriteSide(path, fmt::format("maxlat_us={}\n", max_us));
		return 0;
	}
''', r'''			max_us = std::max(max_us, NowUs() - t0);
		}
		WriteSide(path, fmt::format("maxlat_us={}\n", max_us));
		return 0;
	}
	if (mode == "longframe") {
		// F25k2 (RC2): records while the stand sleeps (from the 1st second for 2 s) - the recorder does not wait.
		std::atomic<bool> stop {false};
		std::thread       writer([&] {
            int i = 0;
            while (!stop) {
                Log::Write(fmt::format("W {}\n", i++));
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
		});
		std::this_thread::sleep_for(std::chrono::milliseconds(1500));
		uint64_t max_us = 0;
		for (int i = 0; i < n; i++) {
			const auto t0 = NowUs();
			Log::LongFrameRecord(static_cast<uint64_t>(i), 100000u + static_cast<uint64_t>(i), 1000u + static_cast<uint64_t>(i));
			max_us = std::max(max_us, NowUs() - t0);
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(3000));
		stop = true;
		writer.join();
		WriteSide(path, fmt::format("rec_max_us={} printer={} async={}\n", max_us,
		                            Log::Testing::LongFramePrinterStarted() ? 1 : 0, Log::AsyncEnabled() ? 1 : 0));
		return 0;
	}
''', 'child longframe')

t = replace(t, r'''		} else if (mode == "die_kill") {
''', r'''		} else if (mode == "die_owner") {
			// F25k2 (RC4): the writer asleep 6 s in the stand; another thread keeps writing; EXIT -> WriteFatal -> the drain
			// times out after 5 s and writes its rest under g_sink_mutex on this thread - the first write of it faults.
			Common::HostException::InstallHandler(UnresolvedHandler);
			std::thread([] {
				for (int i = 0;; i++) {
					Log::Write(fmt::format("B {}\n", i));
					std::this_thread::sleep_for(std::chrono::milliseconds(1));
				}
			}).detach();
			Log::Testing::FaultInNextOwnerWrite();
			EXIT("F25K2-MARKER die_owner\n");
		} else if (mode == "die_kill") {
''', 'child die_owner')

t = replace(t, r'''std::string Path(const char* name) {
''', r'''// F25k2 (RC4): the child is killed after limit_ms; *secs - its run time; returns -2 if it was killed (hung).
int SpawnTimed(const char* mode, const std::string& path, int n, const char* fix, const char* stall, DWORD limit_ms,
               double* secs) {
	_putenv_s("KYTY_FIX_B36", fix != nullptr ? fix : "");
	_putenv_s("KYTY_TEST_LOGSTALL", stall != nullptr ? stall : "");
	_putenv_s("KYTY_FRAME_TRACE", "");
	std::error_code ec;
	std::filesystem::remove(path, ec);
	const auto  ns     = std::to_string(n);
	const char* argv[] = {g_exe.c_str(), "--child", mode, path.c_str(), ns.c_str(), nullptr};
	const auto  t0     = NowUs();
	const auto  h      = _spawnv(_P_NOWAIT, g_exe.c_str(), argv);
	int         rc     = -1;
	if (h != -1) {
		const auto handle = reinterpret_cast<HANDLE>(h);
		if (WaitForSingleObject(handle, limit_ms) == WAIT_TIMEOUT) {
			TerminateProcess(handle, 9);
			WaitForSingleObject(handle, INFINITE);
			rc = -2;
		} else {
			DWORD code = 0;
			GetExitCodeProcess(handle, &code);
			rc = static_cast<int>(code);
		}
		CloseHandle(handle);
	}
	*secs = static_cast<double>(NowUs() - t0) / 1e6;
	std::printf("  child %s fix=%s stall=%s rc=%d (0x%08x) %.1f s%s\n", mode, fix != nullptr ? fix : "-",
	            stall != nullptr ? stall : "-", rc, static_cast<unsigned>(rc), *secs, rc == -2 ? " HUNG (killed)" : "");
	std::fflush(stdout);
	_putenv_s("KYTY_FIX_B36", "");
	_putenv_s("KYTY_TEST_LOGSTALL", "");
	return rc;
}

std::string Path(const char* name) {
''', 'spawntimed')

t = replace(t, r'''		CHECK(Field(res, "async=") == 1);
		CHECK(maxlat < 50000);
		CHECK(fault < 50000);
''', r'''		CHECK(Field(res, "async=") == 1);
		CHECK(maxlat < 50000);
		CHECK(fault < 50000);
		CHECK(Field(res, "veh_us=") < 50000);
		CHECK(text.find(" line=\"") != std::string::npos);
''', 'latency_1 checks')

t = replace(t, r'''	Case("latency_0: =0, the stand sleeps 2 s on the caller - the negative control: a Log::Write waits");
	Spawn("latency", Path("lat0"), 0, "0", "1:2000:1");
	{
		const auto text = ReadFile(Path("lat0"));
		const auto res  = ReadFile(Path("lat0") + ".res");
		std::printf("  %s", res.c_str());
		CHECK(Field(res, "async=") == 0);
		CHECK(Field(res, "maxlat_us=") >= 1900000);
		CHECK(text.find(" on=caller tid=") != std::string::npos);
		CHECK(text.find("LogAsync:") == std::string::npos);
	}
}
''', r'''	Case("latency_0: =0, the stand sleeps 2 s holding the write - the negative control: Log::Write waits, also a second "
	     "writer (F25k2 RC1)");
	Spawn("latency", Path("lat0"), 0, "0", "1:2000:1");
	{
		const auto text = ReadFile(Path("lat0"));
		const auto res  = ReadFile(Path("lat0") + ".res");
		std::printf("  %s", res.c_str());
		CHECK(Field(res, "async=") == 0);
		CHECK(Field(res, "maxlat_us=") >= 1900000);
		CHECK(Field(res, "veh_us=") != UINT64_MAX && Field(res, "veh_us=") >= 1400000);
		CHECK(text.find(" on=caller tid=") != std::string::npos);
		CHECK(text.find(" line=\"W ") != std::string::npos);
		CHECK(text.find("LogAsync:") == std::string::npos);
	}
}

// F25k2 (RC2): the KYTY_LONGFRAME records and their printer.
void TestLongFrame() {
	constexpr int n = 4100;
	for (const char* fix: {"0", "1"}) {
		const auto title = fmt::format("longframe_{}: KYTY_LONGFRAME=1, =" "{}, {} records while the stand holds the write - "
		                               "no wait, 4 096 lines printed off the recording thread", fix, fix, n);
		Case(title.c_str());
		const auto path = Path(std::strcmp(fix, "0") == 0 ? "lf0" : "lf1");
		_putenv_s("KYTY_LONGFRAME", "1");
		Spawn("longframe", path, n, fix, "1:2000:1");
		_putenv_s("KYTY_LONGFRAME", "");
		const auto text  = ReadFile(path);
		const auto res   = ReadFile(path + ".res");
		const auto lines = Lines(text);
		int        next  = 0;
		bool       ok    = true;
		const int  async = std::strcmp(fix, "1") == 0 ? 1 : 0;
		for (const auto& l: lines) {
			if (StartsWith(l, "LongFrame: ")) {
				ok = ok && l == fmt::format("LongFrame: n={} dt_us={} log_async={} t_ms={}", next, 100000 + next, async,
				                            1000 + next);
				next++;
			}
		}
		std::printf("  %s  longframe_lines=%d\n", res.c_str(), next);
		CHECK(Field(res, "printer=") == 1);
		CHECK(Field(res, "async=") == static_cast<uint64_t>(async));
		CHECK(Field(res, "rec_max_us=") < 50000);
		CHECK(ok);
		CHECK(next == 4096);
		CHECK(text.find("TestLogStall: i=1 sleep_ms=2000") != std::string::npos);
	}
	Case("longframe_off: KYTY_LONGFRAME unset - no printer thread, no line");
	Spawn("longframe", Path("lfoff"), 10, "0", nullptr);
	{
		const auto text = ReadFile(Path("lfoff"));
		const auto res  = ReadFile(Path("lfoff") + ".res");
		std::printf("  %s", res.c_str());
		CHECK(Field(res, "printer=") == 0);
		CHECK(text.find("LongFrame:") == std::string::npos);
	}
}

// F25k2 (RC4): a fault inside a write under the sink lock outside the writer - the process dies, does not hang.
void TestDieOwner() {
	Case("die_owner: =1, a fault inside the synchronous tail of a timed-out drain (under g_sink_mutex) - the child dies "
	     "within 10 s (RC4)");
	double     secs = 0;
	const auto rc   = SpawnTimed("die_owner", Path("die_owner"), 1000, "1", "0:6000:1", 40000, &secs);
	CHECK(rc == static_cast<int>(0xC0000005u));
	CHECK(secs <= 10.0);
}
''', 'latency_0 + new tests')

t = replace(t, r'''	g_exe = std::filesystem::absolute(argv[0]).string();
	g_dir = argc >= 2 ? argv[1] : std::filesystem::temp_directory_path().string();
	std::filesystem::create_directories(g_dir);
	TestSeq0();
''', r'''	g_exe = std::filesystem::absolute(argv[0]).string();
	g_dir = argc >= 2 ? argv[1] : std::filesystem::temp_directory_path().string();
	std::filesystem::create_directories(g_dir);
	if (argc >= 4 && std::strcmp(argv[2], "--case") == 0 && std::strcmp(argv[3], "die_owner") == 0) {
		// F25k2: only die_owner (the positive control on a build without the RC4 guard).
		TestDieOwner();
		std::printf("cases=%d failures=%d\n", g_cases, g_fail);
		if (g_fail == 0) {
			std::printf("ALL OK\n");
		}
		return g_fail == 0 ? 0 : 1;
	}
	TestSeq0();
''', 'main case')

t = replace(t, r'''	TestLatency();
	TestDeath();
''', r'''	TestLatency();
	TestLongFrame();
	TestDeath();
	TestDieOwner();
''', 'main calls')
save(rel, t, crlf)
print('patched', rel)
print('PATCH OK')
