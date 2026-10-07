// Track F, F25k (HPP-678; ROADMAP s122 item 613(g)(1)): tests of KYTY_FIX_B36 (the async log writer) without the game.
// The parent runs each case in a child process of this executable (Log::Initialize reads KYTY_FIX_B36 and
// KYTY_TEST_LOGSTALL once per process) and reads the child's log file:
//  * seq0_0 / seq0_1 - a fixed sequence (plain, styled, console+log, a 100 KiB line, bytes 1..255, no trailing newline)
//    at =0 and =1; the =0 file equals the expected bytes; the =1 file equals them without the "LogAsync:" lines. The
//    same child mode built from the code before F25k (no KYTY_LOG_ASYNC_TESTS) writes the reference file - the run
//    script compares it to the =0 file byte for byte (sha256);
//  * order - 8 threads; phase A under a test lock (the call order is the global sequence: the file must hold 0..N-1
//    in order), phase B free (per thread increasing); the writer stalled by the stand to force batching;
//  * full - the queue limit 1 MiB, the writer asleep 2 s, 4 MiB of lines: the producer waits (full_waits >= 1,
//    full_wait_us >= 1 000 000), no line lost, the order kept;
//  * latency_1 / latency_0 - the stand sleeps 2 s inside a sink write: at =1 (on the writer) the longest Log::Write of
//    a writing thread < 50 ms, a write from a vectored exception handler returns < 50 ms and its line is in the file,
//    a "LogAsync: stall us=" line >= 1 900 000; at =0 (on the caller, the negative control) the longest Log::Write
//    >= 1 900 ms;
//  * die_* - the child writes N lines with the writer asleep in the stand and dies: EXIT (WriteFatal + DbgExit),
//    EXIT_IF (DbgReport), std::quick_exit (at_quick_exit -> EmergencyShutdownActive), abort() (AbortReport),
//    Log::DrainForExit + std::_Exit (the _Exit sites), an unresolved access violation (the host exception filter ->
//    Log::DrainForFault), EXIT with the writer asleep 8 s (> the 5 s drain - the rest written by the dying thread);
//    the file holds the N lines in order and the marker. die_kill (the negative control of the reader): the same
//    with TerminateProcess and no drain - lines must be missing.
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
// Prints one line per case and "ALL OK". Target log_async_tests (not in ctest), run by docs/track-f/f25k/run_tests_f25k.py.

#include "common/assert.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#ifdef KYTY_LOG_ASYNC_TESTS
#include "common/hostException.h"
#endif

#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fmt/format.h>
#include <fstream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <process.h>
#include <windows.h>

namespace {

int g_fail  = 0;
int g_cases = 0;

#define CHECK(cond)                                                                                                    \
	do {                                                                                                               \
		if (!(cond)) {                                                                                                 \
			std::printf("FAIL %s:%d %s\n", __FILE__, __LINE__, #cond);                                                 \
			std::fflush(stdout);                                                                                       \
			g_fail++;                                                                                                  \
		}                                                                                                              \
	} while (false)

uint64_t NowUs() {
	return static_cast<uint64_t>(
	    std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch())
	        .count());
}

std::string ReadFile(const std::string& path) {
	std::ifstream f(path, std::ios::binary);
	return std::string(std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>());
}

void WriteSide(const std::string& path, const std::string& text) {
	std::ofstream f(path + ".res", std::ios::binary);
	f << text;
}

std::vector<std::string> Lines(const std::string& text) {
	std::vector<std::string> out;
	size_t                   pos = 0;
	while (pos < text.size()) {
		const auto e = text.find('\n', pos);
		if (e == std::string::npos) {
			out.push_back(text.substr(pos));
			break;
		}
		out.push_back(text.substr(pos, e - pos));
		pos = e + 1;
	}
	return out;
}

bool StartsWith(const std::string& s, const char* p) {
	return s.rfind(p, 0) == 0;
}

// The fixed sequence of seq0 (the byte-for-byte case): the writes and the expected file bytes.
std::string Seq0(bool write) {
	std::string expected;
	auto        w = [&](const std::string& text) {
        if (write) {
            Log::Write(text);
        }
        expected += text;
	};
	for (int i = 0; i < 1000; i++) {
		w(fmt::format("line {} of the fixed sequence\n", i));
	}
	{
		const std::string text = "styled line (File direction: written plain)\n";
		if (write) {
			Log::Write(Log::Color::BrightRed, text);
		}
		expected += text;
	}
	{
		const std::string text = "console and log\n";
		if (write) {
			Log::WriteToConsoleAndLog(text);
		}
		expected += text;
	}
	w(std::string(100 * 1024, 'x') + "\n");
	{
		std::string bytes;
		for (int b = 1; b < 256; b++) {
			bytes.push_back(static_cast<char>(b));
		}
		bytes.push_back('\n');
		w(bytes);
	}
	if (write) {
		Log::Write(std::string());
	}
	w("no trailing newline");
	w("\nlast\n");
	return expected;
}

// ---------------------------------------------------------------------------------------------------------- the child

struct ChildLog {
	Common::Subsystems subsystems;
	explicit ChildLog(const std::string& path) {
		subsystems.Initialize<Config::Lifecycle>();
		Config::ConfigOptions cfg;
		cfg.printf_direction   = Config::LogDirection::File;
		cfg.printf_output_file = path;
		Config::Load(cfg);
		subsystems.Initialize<Log::Lifecycle>();
	}
};

#ifdef KYTY_LOG_ASYNC_TESTS
std::atomic<uint64_t> g_veh_us {0};
void*                 g_veh_page = nullptr;

LONG CALLBACK TestVeh(EXCEPTION_POINTERS* e) {
	if (e->ExceptionRecord->ExceptionCode != EXCEPTION_ACCESS_VIOLATION || g_veh_page == nullptr) {
		return EXCEPTION_CONTINUE_SEARCH;
	}
	const auto addr = static_cast<uintptr_t>(e->ExceptionRecord->ExceptionInformation[1]);
	const auto page = reinterpret_cast<uintptr_t>(g_veh_page);
	if (addr < page || addr >= page + 4096) {
		return EXCEPTION_CONTINUE_SEARCH;
	}
	const auto t0 = NowUs();
	Log::Write("VEH line: written from a vectored exception handler\n");
	g_veh_us = NowUs() - t0;
	DWORD old = 0;
	VirtualProtect(g_veh_page, 4096, PAGE_READWRITE, &old);
	return EXCEPTION_CONTINUE_EXECUTION;
}

bool UnresolvedHandler(const Common::HostException::ExceptionInfo& /*info*/) {
	return false;
}
#endif

int Child(const std::string& mode, const std::string& path, int n) {
	SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
	_set_abort_behavior(0, _WRITE_ABORT_MSG | _CALL_REPORTFAULT);
	ChildLog log(path);
	if (mode == "seq0") {
		Seq0(true);
		return 0;
	}
#ifdef KYTY_LOG_ASYNC_TESTS
	if (mode == "order") {
		std::mutex            mu;
		uint64_t              seq = 0;
		std::vector<std::thread> threads;
		for (int t = 0; t < 8; t++) {
			threads.emplace_back([&, t] {
				for (int i = 0; i < n; i++) {
					std::lock_guard lock(mu);
					Log::Write(fmt::format("S {} T {}\n", seq++, t));
				}
			});
		}
		for (auto& th: threads) {
			th.join();
		}
		threads.clear();
		for (int t = 0; t < 8; t++) {
			threads.emplace_back([&, t] {
				for (int i = 0; i < n; i++) {
					Log::Write(fmt::format("U {} {}\n", t, i));
				}
			});
		}
		for (auto& th: threads) {
			th.join();
		}
		return 0;
	}
	if (mode == "full") {
		Log::Testing::SetAsyncLimit(uint64_t {1} << 20u);
		const std::string pad(1000, 'p');
		uint64_t          max_us = 0;
		for (int i = 0; i < n; i++) {
			const auto t0 = NowUs();
			Log::Write(fmt::format("F {} {}\n", i, pad));
			max_us = std::max(max_us, NowUs() - t0);
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
	if (mode == "latency") {
		void* handle = AddVectoredExceptionHandler(1, TestVeh);
		g_veh_page   = VirtualAlloc(nullptr, 4096, MEM_RESERVE | MEM_COMMIT, PAGE_NOACCESS);
		std::atomic<bool> stop {false};
		std::atomic<uint64_t> max_us {0};
		std::thread       writer([&] {
            int i = 0;
            while (!stop) {
                const auto t0 = NowUs();
                Log::Write(fmt::format("W {}\n", i++));
                const auto d = NowUs() - t0;
                if (d > max_us) {
                    max_us = d;
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
		});
		// The stand sleeps from the 1st second for 2 s: the access violation 0.5 s into the sleep.
		std::this_thread::sleep_for(std::chrono::milliseconds(1500));
		const auto t0 = NowUs();
		static_cast<volatile char*>(g_veh_page)[0] = 1;
		const auto fault_us = NowUs() - t0;
		std::this_thread::sleep_for(std::chrono::milliseconds(3000));
		stop = true;
		writer.join();
		RemoveVectoredExceptionHandler(handle);
		WriteSide(path, fmt::format("maxlat_us={} fault_us={} veh_us={} async={}\n", max_us.load(), fault_us,
		                            g_veh_us.load(), Log::AsyncEnabled() ? 1 : 0));
		return 0;
	}
	if (mode.rfind("die_", 0) == 0) {
		for (int i = 0; i < n; i++) {
			Log::Write(fmt::format("D {}\n", i));
		}
		if (mode == "die_exit" || mode == "die_exit_long") {
			EXIT("F25K-MARKER %s\n", mode.c_str());
		} else if (mode == "die_exitif") {
			const bool f25k_marker_exit_if = true;
			EXIT_IF(f25k_marker_exit_if);
		} else if (mode == "die_quick") {
			at_quick_exit(Common::Subsystems::EmergencyShutdownActive);
			Log::Write("F25K-MARKER die_quick\n");
			std::quick_exit(7);
		} else if (mode == "die_abort") {
			std::abort();
		} else if (mode == "die_drainexit") {
			Log::Write("F25K-MARKER die_drainexit\n");
			Log::DrainForExit();
			std::_Exit(322);
		} else if (mode == "die_fault") {
			Common::HostException::InstallHandler(UnresolvedHandler);
			Log::Write("F25K-MARKER die_fault\n");
			static_cast<volatile int*>(nullptr)[0] = 1;
		} else if (mode == "die_owner") {
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
			Log::Write("F25K-MARKER die_kill\n");
			TerminateProcess(GetCurrentProcess(), 9);
		}
		return 99;
	}
#endif
	std::printf("unknown child mode %s\n", mode.c_str());
	return 98;
}

// --------------------------------------------------------------------------------------------------------- the parent

#ifdef KYTY_LOG_ASYNC_TESTS
std::string g_exe;
std::string g_dir;

int Spawn(const char* mode, const std::string& path, int n, const char* fix, const char* stall) {
	_putenv_s("KYTY_FIX_B36", fix != nullptr ? fix : "");
	_putenv_s("KYTY_TEST_LOGSTALL", stall != nullptr ? stall : "");
	_putenv_s("KYTY_FRAME_TRACE", "");
	std::error_code ec;
	std::filesystem::remove(path, ec);
	std::filesystem::remove(path + ".res", ec);
	const auto  ns   = std::to_string(n);
	const char* argv[] = {g_exe.c_str(), "--child", mode, path.c_str(), ns.c_str(), nullptr};
	const auto  t0   = NowUs();
	const auto  rc   = _spawnv(_P_WAIT, g_exe.c_str(), argv);
	std::printf("  child %s fix=%s stall=%s rc=%lld (%.1f s)\n", mode, fix != nullptr ? fix : "-",
	            stall != nullptr ? stall : "-", static_cast<long long>(rc), static_cast<double>(NowUs() - t0) / 1e6);
	std::fflush(stdout);
	_putenv_s("KYTY_FIX_B36", "");
	_putenv_s("KYTY_TEST_LOGSTALL", "");
	return static_cast<int>(rc);
}

// F25k2 (RC4): the child is killed after limit_ms; *secs - its run time; returns -2 if it was killed (hung).
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
	return g_dir + "/" + name + ".txt";
}

void Case(const char* name) {
	g_cases++;
	std::printf("[case] %s\n", name);
	std::fflush(stdout);
}

uint64_t Field(const std::string& text, const char* key) {
	const auto p = text.find(key);
	if (p == std::string::npos) {
		return UINT64_MAX;
	}
	return std::strtoull(text.c_str() + p + std::strlen(key), nullptr, 10);
}

std::string WithoutPrefix(const std::string& text, const char* prefix) {
	std::string out;
	size_t      pos = 0;
	while (pos < text.size()) {
		auto e = text.find('\n', pos);
		e      = e == std::string::npos ? text.size() : e + 1;
		if (text.compare(pos, std::strlen(prefix), prefix) != 0) {
			out.append(text, pos, e - pos);
		}
		pos = e;
	}
	return out;
}

void TestSeq0() {
	const auto expected = Seq0(false);
	Case("seq0_0: KYTY_FIX_B36=0 - the file equals the expected bytes");
	Spawn("seq0", Path("seq0_0"), 0, "0", nullptr);
	const auto f0 = ReadFile(Path("seq0_0"));
	CHECK(f0 == expected);
	std::printf("  bytes=%zu expected=%zu\n", f0.size(), expected.size());
	Case("seq0_1: KYTY_FIX_B36=1 - the file without the LogAsync: lines equals the expected bytes");
	Spawn("seq0", Path("seq0_1"), 0, "1", nullptr);
	const auto f1 = ReadFile(Path("seq0_1"));
	CHECK(StartsWith(f1, "LogAsync: mode=1 limit_bytes=268435456"));
	CHECK(f1.find("LogAsync: full_waits=0 ") != std::string::npos);
	CHECK(WithoutPrefix(f1, "LogAsync:") == expected);
	Case("seq0_unset: KYTY_FIX_B36 unset - the file equals the =0 file");
	Spawn("seq0", Path("seq0_u"), 0, nullptr, nullptr);
	CHECK(ReadFile(Path("seq0_u")) == f0);
}

void TestOrder() {
	constexpr int n = 20000;
	Case("order: 8 threads, phase A under a test lock = the global order, phase B per thread; writer stalled");
	Spawn("order", Path("order"), n, "1", "0:300:3");
	const auto lines = Lines(ReadFile(Path("order")));
	uint64_t   next  = 0;
	bool       a_ok  = true;
	std::vector<int64_t> last(8, -1);
	bool                 b_ok = true;
	uint64_t             b    = 0;
	int                  stand = 0;
	for (const auto& l: lines) {
		if (StartsWith(l, "S ")) {
			a_ok = a_ok && std::strtoull(l.c_str() + 2, nullptr, 10) == next;
			next++;
		} else if (StartsWith(l, "U ")) {
			int t = 0;
			long long i = 0;
			std::sscanf(l.c_str(), "U %d %lld", &t, &i);
			b_ok = b_ok && t >= 0 && t < 8 && i == last[t] + 1;
			if (t >= 0 && t < 8) {
				last[t] = i;
			}
			b++;
		} else if (StartsWith(l, "TestLogStall: i=")) {
			stand++;
		}
	}
	std::printf("  A=%llu B=%llu stand_sleeps=%d\n", static_cast<unsigned long long>(next),
	            static_cast<unsigned long long>(b), stand);
	CHECK(a_ok);
	CHECK(next == 8u * n);
	CHECK(b_ok);
	CHECK(b == 8u * n);
	CHECK(stand >= 1);
}

void TestFull() {
	constexpr int n = 4096;
	Case("full: limit 1 MiB, writer asleep 2 s, 4 MiB of lines - waits counted, nothing lost, order kept");
	Spawn("full", Path("full"), n, "1", "0:2000:1");
	const auto text  = ReadFile(Path("full"));
	const auto lines = Lines(text);
	int        next  = 0;
	bool       ok    = true;
	for (const auto& l: lines) {
		if (StartsWith(l, "F ")) {
			ok = ok && std::atoi(l.c_str() + 2) == next;
			next++;
		}
	}
	const auto waits   = Field(text, "LogAsync: full_waits=");
	const auto wait_us = Field(text, " full_wait_us=");
	const auto res     = ReadFile(Path("full") + ".res");
	std::printf("  lines=%d full_waits=%llu full_wait_us=%llu %s", next, static_cast<unsigned long long>(waits),
	            static_cast<unsigned long long>(wait_us), res.c_str());
	CHECK(ok);
	CHECK(next == n);
	CHECK(waits != UINT64_MAX && waits >= 1);
	CHECK(wait_us != UINT64_MAX && wait_us >= 1000000);
}

void TestLatency() {
	Case("latency_1: =1, the stand sleeps 2 s on the writer - callers and an exception handler do not wait");
	Spawn("latency", Path("lat1"), 0, "1", "1:2000:1");
	{
		const auto text = ReadFile(Path("lat1"));
		const auto res  = ReadFile(Path("lat1") + ".res");
		std::printf("  %s", res.c_str());
		const auto maxlat = Field(res, "maxlat_us=");
		const auto fault  = Field(res, "fault_us=");
		const auto stall  = Field(text, "LogAsync: stall us=");
		std::printf("  stall_us=%llu\n", static_cast<unsigned long long>(stall));
		CHECK(Field(res, "async=") == 1);
		CHECK(maxlat < 50000);
		CHECK(fault < 50000);
		CHECK(Field(res, "veh_us=") < 50000);
		CHECK(text.find(" line=\"") != std::string::npos);
		CHECK(text.find("VEH line: written from a vectored exception handler\n") != std::string::npos);
		CHECK(text.find("TestLogStall: i=1 sleep_ms=2000") != std::string::npos);
		CHECK(text.find(" on=writer tid=") != std::string::npos);
		CHECK(stall != UINT64_MAX && stall >= 1900000);
	}
	Case("latency_0: =0, the stand sleeps 2 s holding the write - the negative control: Log::Write waits, also a second "
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

bool DeathFileOk(const std::string& text, int n, const char* marker, int* got) {
	const auto lines = Lines(text);
	int        next  = 0;
	bool       ok    = true;
	for (const auto& l: lines) {
		if (StartsWith(l, "D ")) {
			ok = ok && std::atoi(l.c_str() + 2) == next;
			next++;
		}
	}
	*got = next;
	return ok && next == n && text.find(marker) != std::string::npos;
}

void TestDeath() {
	constexpr int n = 20000;
	struct D {
		const char* mode;
		const char* stall;
		const char* marker;
	};
	const D cases[] = {
	    {"die_exit", "0:1500:1", "F25K-MARKER die_exit"},
	    {"die_exitif", "0:1500:1", "f25k_marker_exit_if"},
	    {"die_quick", "0:1500:1", "F25K-MARKER die_quick"},
	    {"die_abort", "0:1500:1", "--- abort() ---"},
	    {"die_drainexit", "0:1500:1", "F25K-MARKER die_drainexit"},
	    {"die_fault", "0:1500:1", "F25K-MARKER die_fault"},
	    {"die_exit_long", "0:8000:1", "F25K-MARKER die_exit_long"},
	};
	for (const auto& d: cases) {
		const auto title = fmt::format("{}: =1, N={} lines with the writer asleep, then death - N lines and the marker",
		                               d.mode, n);
		Case(title.c_str());
		Spawn(d.mode, Path(d.mode), n, "1", d.stall);
		const auto text = ReadFile(Path(d.mode));
		int        got  = 0;
		const bool ok   = DeathFileOk(text, n, d.marker, &got);
		std::printf("  lines=%d marker=%d summary=%d\n", got, text.find(d.marker) != std::string::npos ? 1 : 0,
		            text.find("LogAsync: full_waits=") != std::string::npos ? 1 : 0);
		CHECK(ok);
		if (std::strcmp(d.mode, "die_exit_long") == 0) {
			// The writer asleep 8 s > the 5 s drain: the timeout branch ran and the dying thread wrote the rest.
			CHECK(Field(text, " drain_timeouts=") != UINT64_MAX && Field(text, " drain_timeouts=") >= 1);
			CHECK(Field(text, " sync_lines=") != UINT64_MAX && Field(text, " sync_lines=") >= 1);
		}
	}
	Case("die_kill: the negative control of the reader - TerminateProcess without a drain loses lines");
	Spawn("die_kill", Path("die_kill"), n, "1", "0:1500:1");
	{
		const auto text = ReadFile(Path("die_kill"));
		int        got  = 0;
		const bool ok   = DeathFileOk(text, n, "F25K-MARKER die_kill", &got);
		std::printf("  lines=%d\n", got);
		CHECK(!ok);
	}
}
#endif

} // namespace

int main(int argc, char** argv) {
	if (argc >= 4 && std::strcmp(argv[1], "--child") == 0) {
		return Child(argv[2], argv[3], argc >= 5 ? std::atoi(argv[4]) : 0);
	}
#ifdef KYTY_LOG_ASYNC_TESTS
	g_exe = std::filesystem::absolute(argv[0]).string();
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
	TestOrder();
	TestFull();
	TestLatency();
	TestLongFrame();
	TestDeath();
	TestDieOwner();
	std::printf("cases=%d failures=%d\n", g_cases, g_fail);
	if (g_fail == 0) {
		std::printf("ALL OK\n");
	}
	return g_fail == 0 ? 0 : 1;
#else
	std::printf("reference build: only --child seq0 <path>\n");
	return 2;
#endif
}
