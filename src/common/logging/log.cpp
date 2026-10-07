
#include "common/logging/log.h"
#include "common/diagB32.h" // Track F, F20j3 (KYTY_DIAG_B32, ROADMAP s122 item 574(g))

#include "common/frameStats.h"

#include "common/assert.h"
#include "common/emulatorConfig.h"
#include "common/envFlag.h"
#include "common/stringUtils.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <filesystem>
#include <fmt/format.h>
#include <memory>
#include <mutex>
#include <spdlog/formatter.h>
#include <spdlog/logger.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/null_sink.h>
#include <spdlog/sinks/stdout_sinks.h>
#include <string>
#include <string_view>
#include <thread>

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h> // F25k: SetThreadDescription of the writer thread
#endif

namespace {

class RawFormatter final: public spdlog::formatter {
public:
	void format(const spdlog::details::log_msg& msg, spdlog::memory_buf_t& dest) override {
		const std::string_view payload(msg.payload.data(), msg.payload.size());
		dest.append(payload.data(), payload.data() + payload.size());
	}

	std::unique_ptr<spdlog::formatter> clone() const override {
		return std::make_unique<RawFormatter>();
	}
};

std::shared_ptr<spdlog::logger> MakeLogger(std::string name, spdlog::sink_ptr sink) {
	sink->set_formatter(std::make_unique<RawFormatter>());

	auto logger = std::make_shared<spdlog::logger>(std::move(name), std::move(sink));
	logger->set_level(spdlog::level::trace);
	return logger;
}

std::shared_ptr<spdlog::logger> MakeFileLogger(std::string                  name,
                                               const std::filesystem::path& path) {
	const auto parent = path.parent_path();
	if (!parent.empty()) {
		std::filesystem::create_directories(parent);
	}

	auto sink =
	    std::make_shared<spdlog::sinks::basic_file_sink_mt>(Common::PathToString(path), true);
	return MakeLogger(std::move(name), std::move(sink));
}

static bool HasStyle(fmt::text_style style) {
	return style != fmt::text_style {};
}

void WriteStdout(std::string_view text, fmt::text_style style = {}) {
	if (HasStyle(style)) {
		fmt::print(stdout, style, "{}", text);
	} else {
		std::fwrite(text.data(), 1, text.size(), stdout);
	}
	std::fflush(stdout);
}

} // namespace

namespace Log {

static bool                            g_initialized = false;
static Direction                       g_direction   = Direction::Console;
static std::filesystem::path           g_output_file;
static Common::DiagB32::TrackedMutex<std::mutex>                      g_logger_mutex; // Track F, F20j3 (KYTY_DIAG_B32 W:emu_mutex, ROADMAP s122 item 574(g)(1))
static std::shared_ptr<spdlog::logger> g_logger;

// Track F, F25k (HPP-678; ROADMAP s122 item 613(v)(1)-(6)): KYTY_FIX_B36=1 - the file sink is written by one writer
// thread. Log::Write / WriteImpl copy the ready line into an in-memory queue under a short lock (no I/O, no other
// lock); the writer takes the queue and writes the lines in the order they were queued; the queue is drained on every
// death and exit path (WriteFatal, Shutdown - reached by EmergencyShutdownActive from DbgExit / DbgReport / at_quick_exit
// / atexit, DrainForExit before the _Exit sites, the unresolved branch of the exception filter). Only the File direction
// is moved (the console direction and every WriteStdout stay as they were). KYTY_FIX_B36=0: the one check of g_hooks
// below is the only difference - the file is byte for byte the old one. KYTY_TEST_LOGSTALL=<s>:<ms>[:<k>] - the stand:
// a sleep of <ms> inside the write of the sink (on the calling thread at =0, on the writer at =1) from the <s>-th second
// after Log::Initialize, <k> times (3 by default) at least 5 s apart.
// F25k2 (HPP-682; ROADMAP s122 item 616(b)(1)-(3), RC1, RC2, RC4 of F25l): at =0 with the stand armed the old write runs
// under one per-process stand lock, the stand's sleep inside it before the write (the sleep holds the write as a real
// delay of the file holds the lock of basic_file_sink_mt: every writing thread waits); t_sink_owner marks a thread that
// holds g_sink_mutex or the stand lock outside the writer - a drain on it returns at once (the process dies, as at =0);
// the KYTY_LONGFRAME records go to a static array, a thread off the frame path prints them (namespace LongFrame).
namespace Async {

constexpr uint64_t kDefaultLimitBytes = uint64_t {256} << 20u;
constexpr uint64_t kStallNs           = 100000000u;  // a sink write >= 100 ms - a "LogAsync: stall" line
constexpr uint32_t kStallLines        = 256;
constexpr uint64_t kDrainNs           = 5000000000u; // the drain waits for the writer <= 5 s, then writes the rest itself
constexpr uint64_t kFlushEveryNs      = 100000000u;  // the idle writer flushes the sink at most every 100 ms
constexpr uint64_t kStandGapNs        = 5000000000u;

static bool g_hooks = false; // g_on or the stand armed: the only check the =0 path adds (WriteImpl, WriteFatal, Flush)
static bool g_on    = false; // KYTY_FIX_B36=1 and the File direction (Log::Initialize, before any other thread logs)

struct State {
	std::mutex              mu; // the queue only: held for a push, a swap or a flag, never across a sink write
	std::condition_variable cv_writer;
	std::condition_variable cv_space;
	std::condition_variable cv_idle;
	std::deque<std::string> q;
	uint64_t                pending        = 0; // bytes accepted and not yet written (queue + the writer's batch)
	uint64_t                limit          = kDefaultLimitBytes;
	bool                    busy           = false; // the writer is writing a batch or flushing
	bool                    dirty          = false; // written since the last sink flush
	bool                    flush_req      = false;
	bool                    writer_waiting = false;
	bool                    stop           = false;
	bool                    closed         = false; // after the exit drain lines are dropped (as g_logger.reset() did)
	uint32_t                drain_waiters  = 0;
	uint64_t                full_waits     = 0;
	uint64_t                full_wait_ns   = 0;
	uint64_t                lines          = 0;
	uint64_t                bytes          = 0;
	uint64_t                max_pending    = 0;
	uint64_t                sync_lines     = 0; // written by a drain that timed out
	uint64_t                drain_timeouts = 0;
};

// Never destroyed: the exit paths run while static destructors may already be running (atexit) or not at all.
static State&            g_state = *new State;
static std::mutex&       g_sink_mutex = *new std::mutex; // the writer's batch; a timed-out drain writes its rest after it
static std::mutex&       g_stand_mutex = *new std::mutex; // F25k2 RC1: =0, the stand armed - the old write, the sleep inside
static std::atomic<uint64_t> g_pending_bytes {0};        // the "queued_bytes" of the stall line (read by the writer)
static std::atomic<uint64_t> g_stalls {0};
static std::atomic<uint64_t> g_stall_cut {0};
static std::atomic<bool>     g_summary_done {false};

static thread_local bool        t_writer   = false;
static thread_local bool        t_in_queue = false; // this thread holds g_state.mu (an exception handler on it must not lock)
static thread_local std::string t_nested;           // lines of an exception handler that interrupted this thread's push
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

struct Stand {
	bool                  armed     = false;
	uint64_t              at_ns     = 0;
	uint32_t              sleep_ms  = 0;
	uint32_t              k         = 3;
	std::atomic<uint64_t> next_ns {0};
	std::atomic<uint32_t> done {0};
};
static Stand& g_stand = *new Stand;

static uint64_t NowNs() {
	return Common::FrameStats::NowNs();
}

static void ParseStand(uint64_t init_ns) {
	const char* value = std::getenv("KYTY_TEST_LOGSTALL");
	if (value == nullptr || value[0] == '\0') {
		return;
	}
	unsigned at_s = 0;
	unsigned ms   = 0;
	unsigned k    = 3;
	const int n   = std::sscanf(value, "%u:%u:%u", &at_s, &ms, &k);
	if (n < 2 || ms == 0 || k == 0) {
		std::fprintf(stderr, "KYTY_TEST_LOGSTALL: bad value '%s' (<s>:<ms>[:<k>]), stand off\n", value);
		return;
	}
	g_stand.at_ns    = init_ns + uint64_t {at_s} * 1000000000u;
	g_stand.sleep_ms = ms;
	g_stand.k        = k;
	g_stand.next_ns.store(g_stand.at_ns, std::memory_order_relaxed);
	g_stand.armed = true;
}

// The stand point: right before a write of the sink, on the thread that writes it. One thread claims each sleep.
static const char* RoleName() {
	switch (Common::FrameStats::CurrentRole()) {
		case Common::FrameStats::ThreadRole::Main: return "Main";
		case Common::FrameStats::ThreadRole::Gpu: return "Gpu";
		case Common::FrameStats::ThreadRole::Present: return "Present";
		case Common::FrameStats::ThreadRole::Record: return "Record";
		default: return "other";
	}
}

static uint32_t OsTid() {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	return static_cast<uint32_t>(GetCurrentThreadId());
#else
	return 0;
#endif
}

// F25k2 (RC1): the "line=" field - the first <= 40 bytes of the line that took the sleep; a non-printable byte, '"' and '\'
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
	if (!g_stand.armed) {
		return;
	}
	const uint32_t i = g_stand.done.load(std::memory_order_acquire);
	if (i >= g_stand.k) {
		return;
	}
	uint64_t next = g_stand.next_ns.load(std::memory_order_acquire);
	const auto t0 = NowNs();
	if (t0 < next || next == UINT64_MAX) {
		return;
	}
	if (!g_stand.next_ns.compare_exchange_strong(next, UINT64_MAX, std::memory_order_acq_rel)) {
		return;
	}
	std::this_thread::sleep_for(std::chrono::milliseconds(g_stand.sleep_ms));
	const auto t1 = NowNs();
	g_stand.done.store(i + 1, std::memory_order_release);
	g_stand.next_ns.store(t1 + kStandGapNs, std::memory_order_release);
	if (logger != nullptr) {
		const auto line =
		    fmt::format("TestLogStall: i={} sleep_ms={} slept_us={} t0_ms={} t1_ms={} on={} tid={} role={} line=\"{}\"\n",
		                i + 1, g_stand.sleep_ms, (t1 - t0) / 1000u, t0 / 1000000u, t1 / 1000000u,
		                t_writer ? "writer" : "caller", OsTid(), RoleName(), StandLineField(text));
		logger->log(spdlog::level::info, spdlog::string_view_t(line.data(), line.size()));
	}
}

// A write of the sink by the writer (or by a timed-out drain): measured, the stand's sleep inside; >= 100 ms - a stall
// line.
static void SinkWrite(const std::shared_ptr<spdlog::logger>& logger, const std::string& line) {
	const auto t0 = NowNs();
	StandPoint(logger, line);
	if (t_sink_owner && g_test_owner_fault.exchange(false)) [[unlikely]] {
		*static_cast<volatile int*>(nullptr) = 1; // log_async_tests die_owner (RC4): a fault inside a write under the sink lock
	}
	logger->log(spdlog::level::info, spdlog::string_view_t(line.data(), line.size()));
	const auto ns = NowNs() - t0;
	const auto left = g_pending_bytes.fetch_sub(line.size(), std::memory_order_relaxed) - line.size();
	if (ns >= kStallNs) {
		if (g_stalls.fetch_add(1, std::memory_order_relaxed) < kStallLines) {
			const auto text = fmt::format("LogAsync: stall us={} queued_bytes={} t_ms={}\n", ns / 1000u, left,
			                              NowNs() / 1000000u);
			logger->log(spdlog::level::info, spdlog::string_view_t(text.data(), text.size()));
		} else {
			g_stall_cut.fetch_add(1, std::memory_order_relaxed);
		}
	}
}

static void SinkFlush(const std::shared_ptr<spdlog::logger>& logger) {
	const auto t0 = NowNs();
	logger->flush();
	const auto ns = NowNs() - t0;
	if (ns >= kStallNs) {
		if (g_stalls.fetch_add(1, std::memory_order_relaxed) < kStallLines) {
			const auto text = fmt::format("LogAsync: stall us={} queued_bytes={} t_ms={} flush=1\n", ns / 1000u,
			                              g_pending_bytes.load(std::memory_order_relaxed), NowNs() / 1000000u);
			logger->log(spdlog::level::info, spdlog::string_view_t(text.data(), text.size()));
		} else {
			g_stall_cut.fetch_add(1, std::memory_order_relaxed);
		}
	}
}

static std::shared_ptr<spdlog::logger> GetLoggerLocked();

// The thread name for the KYTY_DIAG_B32 thread rows (looked up as diagB32.cpp does for DiagB32M5).
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
	auto&                   s = g_state;
	std::deque<std::string> batch;
	uint64_t                last_flush = NowNs();
	std::unique_lock        lock(s.mu);
	for (;;) {
		if (!s.q.empty()) {
			batch.swap(s.q);
			s.busy = true;
			lock.unlock();
			uint64_t written = 0;
			{
				std::lock_guard sink(g_sink_mutex);
				const auto      logger = GetLoggerLocked();
				for (const auto& line: batch) {
					if (logger != nullptr) {
						SinkWrite(logger, line);
					} else {
						g_pending_bytes.fetch_sub(line.size(), std::memory_order_relaxed);
					}
					written += line.size();
				}
			}
			batch.clear();
			lock.lock();
			s.pending -= written;
			s.busy  = false;
			s.dirty = true;
			s.cv_space.notify_all();
			continue;
		}
		const auto now = NowNs();
		if (s.dirty && (s.flush_req || s.drain_waiters != 0 || s.stop || now - last_flush >= kFlushEveryNs)) {
			s.flush_req = false;
			s.busy      = true;
			lock.unlock();
			{
				std::lock_guard sink(g_sink_mutex);
				if (const auto logger = GetLoggerLocked()) {
					SinkFlush(logger);
				}
			}
			last_flush = NowNs();
			lock.lock();
			s.busy  = false;
			s.dirty = false;
			continue;
		}
		s.flush_req = false;
		s.cv_idle.notify_all();
		if (s.stop) {
			break;
		}
		s.writer_waiting = true;
		if (s.dirty) {
			s.cv_writer.wait_for(lock, std::chrono::nanoseconds(kFlushEveryNs - (now - last_flush)));
		} else {
			s.cv_writer.wait(lock);
		}
		s.writer_waiting = false;
	}
}

static void Enqueue(std::string_view text) {
	if (t_in_queue) {
		// An exception handler interrupted this thread inside its own push: no lock, the line follows the pushed one.
		t_nested.append(text.data(), text.size());
		return;
	}
	auto&       s = g_state;
	std::string line(text);
	for (;;) {
		const uint64_t n      = line.size();
		bool           notify = false;
		{
			std::unique_lock lock(s.mu);
			// t_in_queue is set while this thread holds s.mu; the guard clears it on every exit of the scope (also an
			// exception of push_back), before the lock is released (declared after it).
			struct InQueue {
				InQueue() { t_in_queue = true; }
				~InQueue() { t_in_queue = false; }
				InQueue(const InQueue&)            = delete;
				InQueue& operator=(const InQueue&) = delete;
			} in_queue;
			if (s.closed) {
				return;
			}
			// Not the writer, and not a thread that holds the sink lock (F25k2 RC4: an exception handler on it would wait
			// for space the writer cannot make).
			if (!t_writer && !t_sink_owner && s.pending != 0 && s.pending + n > s.limit) {
				const auto t0 = NowNs();
				s.full_waits++;
				s.cv_space.wait(lock, [&] { return s.closed || s.pending == 0 || s.pending + n <= s.limit; });
				s.full_wait_ns += NowNs() - t0;
				if (s.closed) {
					return;
				}
			}
			s.q.push_back(std::move(line));
			s.pending += n;
			g_pending_bytes.fetch_add(n, std::memory_order_relaxed);
			s.max_pending = std::max(s.max_pending, s.pending);
			s.lines++;
			s.bytes += n;
			notify = s.writer_waiting;
		}
		if (notify) {
			s.cv_writer.notify_one();
		}
		if (t_nested.empty()) {
			return;
		}
		line.clear();
		line.swap(t_nested);
	}
}

// Waits until the writer has written and flushed everything queued (<= 5 s); after the timeout the rest is taken from
// the queue and written on this thread after the writer's current batch. close: the writer stops, later lines are
// dropped. Not on the writer (it holds the sink), not inside this thread's own push (an exception handler there) and not
// on a thread that holds the sink lock outside the writer (F25k2 RC4: a fault inside the synchronous tail below or inside
// WriteSummary - the drain of the exception filter would wait 5 s and lock g_sink_mutex again on the same thread).
static void Drain(bool close) {
	auto& s = g_state;
	if (t_writer || t_in_queue || t_sink_owner) {
		return;
	}
	std::deque<std::string> rest;
	{
		std::unique_lock lock(s.mu);
		s.drain_waiters++;
		s.cv_writer.notify_one();
		const auto done = s.cv_idle.wait_for(lock, std::chrono::nanoseconds(kDrainNs),
		                                     [&] { return s.q.empty() && !s.busy && !s.dirty; });
		s.drain_waiters--;
		if (!done) {
			rest.swap(s.q);
			s.drain_timeouts++;
		}
		if (close) {
			s.closed = true;
			s.stop   = true;
		}
	}
	s.cv_writer.notify_one();
	s.cv_space.notify_all();
	if (!rest.empty()) {
		std::lock_guard sink(g_sink_mutex);
		SinkOwner       owner;
		uint64_t        written = 0;
		if (const auto logger = GetLoggerLocked()) {
			for (const auto& line: rest) {
				SinkWrite(logger, line);
				written += line.size();
			}
			logger->flush();
		}
		std::lock_guard lock(s.mu);
		s.pending -= written;
		s.sync_lines += rest.size();
	}
}

static void WriteSummary() {
	if (g_summary_done.exchange(true)) {
		return;
	}
	auto&       s = g_state;
	std::string text;
	{
		std::lock_guard lock(s.mu);
		text = fmt::format("LogAsync: full_waits={} full_wait_us={} stalls={} stall_cut={} lines={} bytes={} "
		                   "max_queued_bytes={} sync_lines={} drain_timeouts={}\n",
		                   s.full_waits, s.full_wait_ns / 1000u, g_stalls.load(), g_stall_cut.load(), s.lines,
		                   s.bytes, s.max_pending, s.sync_lines, s.drain_timeouts);
	}
	std::lock_guard sink(g_sink_mutex);
	SinkOwner       owner;
	if (const auto logger = GetLoggerLocked()) {
		logger->log(spdlog::level::info, spdlog::string_view_t(text.data(), text.size()));
		logger->flush();
	}
}

// The exit drain: everything queued reaches the file, the writer stops, the summary line is the last one.
static void ExitDrain() {
	if (t_writer || t_in_queue || t_sink_owner) {
		return;
	}
	Drain(true);
	WriteSummary();
}

static void Start(uint64_t limit) {
	g_state.limit = limit;
	std::thread(WriterMain).detach();
}

} // namespace Async

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
	if (Async::g_hooks) [[unlikely]] {
		if (Async::g_on) {
			// KYTY_FIX_B36=1: a request - the writer flushes the sink once the queue is empty (no I/O on this thread).
			if (Async::t_in_queue) {
				return; // an exception handler inside this thread's own push: the writer flushes on its own timer
			}
			std::lock_guard lock(Async::g_state.mu);
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

static void SetupLogger() {
	std::lock_guard lock(g_logger_mutex);
	Flush();
	g_logger.reset();

	switch (g_direction) {
		case Direction::Silent:
			g_logger = MakeLogger("kyty", std::make_shared<spdlog::sinks::null_sink_mt>());
			break;
		case Direction::Console:
			g_logger = MakeLogger("kyty", std::make_shared<spdlog::sinks::stdout_sink_mt>());
			break;
		case Direction::File:
			if (!g_output_file.empty()) {
				g_logger = MakeFileLogger("kyty", g_output_file);
			}
			break;
	}
}

static std::shared_ptr<spdlog::logger> GetLogger() {
	std::lock_guard lock(g_logger_mutex);
	return g_logger;
}

std::shared_ptr<spdlog::logger> Async::GetLoggerLocked() {
	return GetLogger();
}

// KYTY_FIX_B36 / KYTY_TEST_LOGSTALL (F25k, F25k2): true - the line is taken: queued at =1; at =0 with the stand armed
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

static void WriteImpl(std::string_view text, fmt::text_style style = {}) {
	if (text.empty()) {
		return;
	}

	if (!g_initialized) {
		WriteStdout(text, style);
		return;
	}

	if (g_direction == Direction::Silent) {
		return;
	}

	if (Async::g_hooks) [[unlikely]] {
		if (HookWrite(text, style)) {
			return;
		}
	}

	if (auto logger = GetLogger()) {
		if (g_direction == Direction::Console && HasStyle(style)) {
			const auto styled = fmt::format(style, "{}", text);
			logger->log(spdlog::level::info, spdlog::string_view_t(styled.data(), styled.size()));
		} else {
			logger->log(spdlog::level::info, spdlog::string_view_t(text.data(), text.size()));
		}
	}
}

void WriteToConsoleAndLog(std::string_view text) {
	WriteImpl(text);
	if (g_initialized && g_direction != Direction::Console) {
		WriteStdout(text);
	}
	Flush();
}

void WriteFatal(std::string_view text) {
	if (g_direction == Direction::Silent || !g_initialized) {
		WriteStdout(text);
	} else {
		WriteStdout(text);
		WriteImpl(text);
	}
	if (Async::g_hooks) [[unlikely]] {
		if (Async::g_on) {
			Async::Drain(false); // F25k: the fatal text and everything before it are in the file before the caller dies
		}
	}
	Flush();
}

void WriteFatal(fmt::text_style style, std::string_view text) {
	if (g_direction == Direction::Silent || !g_initialized) {
		WriteStdout(text, style);
	} else {
		WriteStdout(text, style);
		WriteImpl(text, style);
	}
	if (Async::g_hooks) [[unlikely]] {
		if (Async::g_on) {
			Async::Drain(false);
		}
	}
	Flush();
}

// F25k: KYTY_FIX_B36 and KYTY_TEST_LOGSTALL are read once, after the sink exists and before any other thread logs
// (Log::Initialize runs on the main thread from Emulator::Init, before the guest and the host threads start).
static void InitAsync() {
	const auto init_ns   = Async::NowNs();
	const bool requested = Common::EnvFlagOn("KYTY_FIX_B36");
	Async::ParseStand(init_ns);
	Async::g_on    = requested && g_direction == Direction::File && g_logger != nullptr;
	Async::g_hooks = Async::g_on || Async::g_stand.armed;
	if (Async::g_on) {
		Async::Start(Async::kDefaultLimitBytes);
		Write(fmt::format("LogAsync: mode=1 limit_bytes={} drain_ms={} stall_ms={} flush_ms={}\n",
		                  Async::kDefaultLimitBytes, Async::kDrainNs / 1000000u, Async::kStallNs / 1000000u,
		                  Async::kFlushEveryNs / 1000000u));
	} else if (requested) {
		Write("LogAsync: mode=0 requested=1 reason=direction\n");
	}
	if (Async::g_stand.armed) {
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

void Initialize() {
	g_initialized = true;
	switch (Config::GetPrintfDirection()) {
		case Config::LogDirection::Silent: g_direction = Direction::Silent; break;
		case Config::LogDirection::Console: g_direction = Direction::Console; break;
		case Config::LogDirection::File: g_direction = Direction::File; break;
	}
	g_output_file =
	    (g_direction == Direction::File ? Config::GetPrintfOutputFile() : std::filesystem::path {});
	SetupLogger();
	InitAsync();
}

void Shutdown() {
	if (LongFrame::g_on) [[unlikely]] {
		LongFrame::g_stop.store(true); // F25k2 (RC2): the printer writes nothing after the log is shut down
	}
	if (Async::g_hooks) [[unlikely]] {
		if (Async::g_on) {
			Async::ExitDrain(); // F25k: queue -> file, writer stopped, the summary line
		}
	}
	Flush();
	std::lock_guard lock(g_logger_mutex);
	g_logger.reset();
}

void DrainForExit() noexcept {
	if (Async::g_hooks) [[unlikely]] {
		if (Async::g_on) {
			try {
				Async::ExitDrain();
			} catch (...) {
			}
		}
	}
}

void DrainForFault() noexcept {
	if (Async::g_hooks) [[unlikely]] {
		if (Async::g_on) {
			try {
				Async::Drain(false);
			} catch (...) {
			}
		}
	}
}

bool AsyncEnabled() {
	return Async::g_on;
}

void Testing::SetAsyncLimit(uint64_t bytes) {
	std::lock_guard lock(Async::g_state.mu);
	Async::g_state.limit = bytes;
}

void Testing::FaultInNextOwnerWrite() {
	Async::g_test_owner_fault.store(true);
}

bool Testing::LongFramePrinterStarted() {
	return LongFrame::g_started.load();
}

Direction GetDirection() {
	EXIT_IF(!g_initialized);
	return g_direction;
}

bool IsSilent() {
	// Before init LOGF must keep writing to stdout, so report non-silent.
	return g_initialized && g_direction == Direction::Silent;
}

bool IsVerbose() {
	static const bool verbose = Common::EnvFlagOn("KYTY_LOG_VERBOSE");
	return !IsSilent() && (verbose || Config::GraphicsDebugDumpEnabled());
}

static void CountWrite(uint64_t t0) {
	namespace FS = Common::FrameStats;
	if (t0 != 0) {
		const auto ns = FS::NowNs() - t0;
		FS::Add(FS::Counter::LogNs, ns);
		FS::Add(FS::Counter::Logs, 1);
		if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
			FS::Add(FS::Counter::LogGpuNs, ns);
		}
	}
}

void Write(std::string_view text) {
	const auto t0 = Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;
	WriteImpl(text);
	CountWrite(t0);
}

void Write(fmt::text_style style, std::string_view text) {
	const auto t0 = Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;
	WriteImpl(text, style);
	CountWrite(t0);
}

} // namespace Log
