// Track F, F25l (HPP-679, Red Team): probes of the F25k code (KYTY_FIX_B36) - not a product test, not committed to the
// product tree. The parent runs each probe in a child process of this executable and reads the child's log and side file.
//  * stand0_two  - KYTY_FIX_B36=0, KYTY_TEST_LOGSTALL=1:2000:1: two writing threads A and B (a line every ~1 ms);
//                  the max latency of each Log::Write. A real file-system stall holds the sink: both threads wait.
//  * busy_exit   - KYTY_FIX_B36=1, no stand: <k> producer threads write continuously (a line every <gap_us> us, spin);
//                  after 1 s the main thread calls EXIT. The time EXIT -> process end and drain_timeouts / sync_lines.
//  * busy_quick  - the same with std::quick_exit (the exit drain of Log::Shutdown via at_quick_exit).
//  * idle_exit   - the control: no producers, EXIT after 1 s.

#include "common/assert.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/subsystems.h"

#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fmt/format.h>
#include <fstream>
#include <string>
#include <thread>
#include <vector>

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <process.h>
#include <windows.h>

namespace {

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

void SpinUs(uint64_t us) {
	const auto t0 = NowUs();
	while (NowUs() - t0 < us) {
	}
}

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

int Child(const std::string& mode, const std::string& path, int k, int gap_us) {
	SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
	_set_abort_behavior(0, _WRITE_ABORT_MSG | _CALL_REPORTFAULT);
	ChildLog log(path);
	if (mode == "stand0_two") {
		std::atomic<bool>     stop {false};
		std::atomic<uint64_t> max_us[2] {{0}, {0}};
		std::vector<std::thread> threads;
		for (int t = 0; t < 2; t++) {
			threads.emplace_back([&, t] {
				int i = 0;
				while (!stop) {
					const auto t0 = NowUs();
					Log::Write(fmt::format("T{} {}\n", t, i++));
					const auto d = NowUs() - t0;
					if (d > max_us[t]) {
						max_us[t] = d;
					}
					SpinUs(1000);
				}
			});
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(4500));
		stop = true;
		for (auto& th: threads) {
			th.join();
		}
		WriteSide(path, fmt::format("maxlat_A_us={} maxlat_B_us={} async={}\n", max_us[0].load(), max_us[1].load(),
		                            Log::AsyncEnabled() ? 1 : 0));
		return 0;
	}
	if (mode == "busy_exit" || mode == "busy_quick" || mode == "idle_exit") {
		std::atomic<bool> stop {false};
		std::vector<std::thread> threads;
		const int n_threads = mode == "idle_exit" ? 0 : k;
		for (int t = 0; t < n_threads; t++) {
			threads.emplace_back([&, t] {
				int i = 0;
				while (!stop) {
					Log::Write(fmt::format("P{} {} producer line of a realistic length for the probe\n", t, i++));
					SpinUs(static_cast<uint64_t>(gap_us));
				}
			});
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(1000));
		const auto t_exit = NowUs();
		WriteSide(path, fmt::format("t_exit_us={}\n", t_exit));
		if (mode == "busy_quick") {
			at_quick_exit(Common::Subsystems::EmergencyShutdownActive);
			Log::Write("F25L-MARKER busy_quick\n");
			std::quick_exit(7);
		}
		EXIT("F25L-MARKER %s\n", mode.c_str());
	}
	std::printf("unknown child mode %s\n", mode.c_str());
	return 98;
}

std::string g_exe;
std::string g_dir;

uint64_t Field(const std::string& text, const char* key) {
	const auto p = text.find(key);
	if (p == std::string::npos) {
		return UINT64_MAX;
	}
	return std::strtoull(text.c_str() + p + std::strlen(key), nullptr, 10);
}

uint64_t Spawn(const char* mode, const std::string& path, int k, int gap_us, const char* fix, const char* stall) {
	_putenv_s("KYTY_FIX_B36", fix != nullptr ? fix : "");
	_putenv_s("KYTY_TEST_LOGSTALL", stall != nullptr ? stall : "");
	_putenv_s("KYTY_FRAME_TRACE", "");
	std::error_code ec;
	std::filesystem::remove(path, ec);
	std::filesystem::remove(path + ".res", ec);
	const auto  ks     = std::to_string(k);
	const auto  gs     = std::to_string(gap_us);
	const char* argv[] = {g_exe.c_str(), "--child", mode, path.c_str(), ks.c_str(), gs.c_str(), nullptr};
	const auto  rc     = _spawnv(_P_WAIT, g_exe.c_str(), argv);
	const auto  t_end  = NowUs();
	_putenv_s("KYTY_FIX_B36", "");
	_putenv_s("KYTY_TEST_LOGSTALL", "");
	std::printf("  child %s k=%d gap_us=%d fix=%s stall=%s rc=%lld\n", mode, k, gap_us, fix != nullptr ? fix : "-",
	            stall != nullptr ? stall : "-", static_cast<long long>(rc));
	return t_end;
}

void ExitProbe(const char* mode, int k, int gap_us, const char* tag) {
	const auto path  = g_dir + "/" + tag + ".txt";
	const auto t_end = Spawn(mode, path, k, gap_us, "1", nullptr);
	const auto res   = ReadFile(path + ".res");
	const auto text  = ReadFile(path);
	const auto t_ex  = Field(res, "t_exit_us=");
	std::printf("RESULT %s mode=%s k=%d gap_us=%d exit_to_end_ms=%llu drain_timeouts=%llu sync_lines=%llu lines=%llu "
	            "marker=%d summary=%d\n",
	            tag, mode, k, gap_us,
	            static_cast<unsigned long long>(t_ex != UINT64_MAX && t_end > t_ex ? (t_end - t_ex) / 1000u : 0),
	            static_cast<unsigned long long>(Field(text, " drain_timeouts=")),
	            static_cast<unsigned long long>(Field(text, " sync_lines=")),
	            static_cast<unsigned long long>(Field(text, " lines=")),
	            text.find("F25L-MARKER") != std::string::npos ? 1 : 0,
	            text.find("LogAsync: full_waits=") != std::string::npos ? 1 : 0);
	std::fflush(stdout);
}

} // namespace

int main(int argc, char** argv) {
	if (argc >= 4 && std::strcmp(argv[1], "--child") == 0) {
		return Child(argv[2], argv[3], argc >= 5 ? std::atoi(argv[4]) : 0, argc >= 6 ? std::atoi(argv[5]) : 0);
	}
	g_exe = std::filesystem::absolute(argv[0]).string();
	g_dir = argc >= 2 ? argv[1] : std::filesystem::temp_directory_path().string();
	std::filesystem::create_directories(g_dir);
	{
		const auto path = g_dir + "/stand0_two.txt";
		Spawn("stand0_two", path, 0, 0, "0", "1:2000:1");
		const auto res  = ReadFile(path + ".res");
		const auto text = ReadFile(path);
		const auto p    = text.find("TestLogStall: i=1");
		std::printf("RESULT stand0_two %s  stall_line=%s\n", res.substr(0, res.size() - 1).c_str(),
		            p == std::string::npos ? "-" : text.substr(p, text.find('\n', p) - p).c_str());
		const auto path1 = g_dir + "/stand1_two.txt";
		Spawn("stand0_two", path1, 0, 0, "1", "1:2000:1");
		std::printf("RESULT stand1_two %s\n", ReadFile(path1 + ".res").c_str());
	}
	ExitProbe("idle_exit", 0, 0, "idle_exit");
	ExitProbe("busy_exit", 2, 2000, "busy_exit_2x2000");
	ExitProbe("busy_exit", 4, 500, "busy_exit_4x500");
	ExitProbe("busy_exit", 4, 50, "busy_exit_4x50");
	ExitProbe("busy_quick", 4, 500, "busy_quick_4x500");
	std::printf("PROBE DONE\n");
	return 0;
}
