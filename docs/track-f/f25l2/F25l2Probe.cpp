// Track F, F25l2 (HPP-683, Red Team): probes of the F25k2 code (KYTY_FIX_B36 RC1, RC2) - not a product test, not committed
// to the product tree. The parent runs each probe in a child process of this executable and reads the child's side file.
//  * stand0_two   - KYTY_FIX_B36=0, KYTY_TEST_LOGSTALL=1:2000:1: two writing threads A and B (a line every ~1 ms); the max
//                   latency of each Log::Write. After RC1 both wait (the sleep holds the write). The F25l probe, repeated.
//  * stand0_flush - the same stand; thread A writes, thread B only calls Log::Flush() every ~1 ms: B waits (deviation 1).
//  * lf_nostand   - KYTY_FIX_B36=0, no stand, KYTY_LONGFRAME=1: 20 records from a thread holding a lock of its own (the
//                   Present form); the printer prints 20 lines while g_hooks is false (the =0 path without the stand).
//  * lf_stand0    - KYTY_FIX_B36=0, stand 1:2000:1, KYTY_LONGFRAME=1: thread A writes; thread P holds its own mutex (a
//                   stand-in for FlipQueue::m_mutex) and records every ~1 ms through the sleep; P's max time under its
//                   mutex; the printer's lines reach the file.

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

void Bump(std::atomic<uint64_t>& m, uint64_t d) {
	if (d > m) {
		m = d;
	}
}

int Child(const std::string& mode, const std::string& path) {
	SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
	ChildLog log(path);
	if (mode == "stand0_two" || mode == "stand0_flush") {
		std::atomic<bool>        stop {false};
		std::atomic<uint64_t>    max_us[2] {{0}, {0}};
		std::vector<std::thread> threads;
		for (int t = 0; t < 2; t++) {
			threads.emplace_back([&, t] {
				int i = 0;
				while (!stop) {
					const auto t0 = NowUs();
					if (t == 1 && mode == "stand0_flush") {
						Log::Flush();
					} else {
						Log::Write(fmt::format("T{} {}\n", t, i++));
					}
					Bump(max_us[t], NowUs() - t0);
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
	if (mode == "lf_nostand" || mode == "lf_stand0") {
		std::atomic<bool>     stop {false};
		std::atomic<uint64_t> max_p {0};
		std::mutex            flip_mutex;
		std::thread           writer([&] {
            int i = 0;
            while (!stop) {
                Log::Write(fmt::format("A {}\n", i++));
                SpinUs(1000);
            }
		});
		std::thread present([&] {
			for (int i = 0; i < 3000 && !stop; i++) {
				const auto t0 = NowUs();
				{
					std::lock_guard lock(flip_mutex);
					if (mode == "lf_stand0" || i < 20) {
						if (i < 20) {
							Log::LongFrameRecord(static_cast<uint64_t>(i), 100000u + static_cast<uint64_t>(i), 7000u + i);
						}
					}
				}
				Bump(max_p, NowUs() - t0);
				SpinUs(1000);
			}
		});
		std::this_thread::sleep_for(std::chrono::milliseconds(4500));
		stop = true;
		writer.join();
		present.join();
		WriteSide(path, fmt::format("present_max_us={} async={}\n", max_p.load(), Log::AsyncEnabled() ? 1 : 0));
		return 0;
	}
	std::printf("unknown child mode %s\n", mode.c_str());
	return 98;
}

std::string g_exe;
std::string g_dir;

void Spawn(const char* mode, const std::string& path, const char* fix, const char* stall, const char* lf) {
	_putenv_s("KYTY_FIX_B36", fix != nullptr ? fix : "");
	_putenv_s("KYTY_TEST_LOGSTALL", stall != nullptr ? stall : "");
	_putenv_s("KYTY_LONGFRAME", lf != nullptr ? lf : "");
	_putenv_s("KYTY_FRAME_TRACE", "");
	std::error_code ec;
	std::filesystem::remove(path, ec);
	std::filesystem::remove(path + ".res", ec);
	const char* argv[] = {g_exe.c_str(), "--child", mode, path.c_str(), nullptr};
	const auto  rc     = _spawnv(_P_WAIT, g_exe.c_str(), argv);
	_putenv_s("KYTY_FIX_B36", "");
	_putenv_s("KYTY_TEST_LOGSTALL", "");
	_putenv_s("KYTY_LONGFRAME", "");
	std::printf("  child %s fix=%s stall=%s lf=%s rc=%lld\n", mode, fix != nullptr ? fix : "-", stall != nullptr ? stall : "-",
	            lf != nullptr ? lf : "-", static_cast<long long>(rc));
}

std::string FirstLine(const std::string& text, const char* key) {
	const auto p = text.find(key);
	return p == std::string::npos ? std::string("-") : text.substr(p, text.find('\n', p) - p);
}

int Count(const std::string& text, const char* key) {
	int  n = 0;
	auto p = text.find(key);
	while (p != std::string::npos) {
		n++;
		p = text.find(key, p + 1);
	}
	return n;
}

void Run(const char* tag, const char* mode, const char* fix, const char* stall, const char* lf) {
	const auto path = g_dir + "/" + tag + ".txt";
	Spawn(mode, path, fix, stall, lf);
	const auto res  = ReadFile(path + ".res");
	const auto text = ReadFile(path);
	std::printf("RESULT %s %s longframe_lines=%d first_lf=%s stall_line=%s\n", tag,
	            res.empty() ? "-" : res.substr(0, res.size() - 1).c_str(), Count(text, "LongFrame: "),
	            FirstLine(text, "LongFrame: ").c_str(), FirstLine(text, "TestLogStall: i=1").c_str());
	std::fflush(stdout);
}

} // namespace

int main(int argc, char** argv) {
	if (argc >= 4 && std::strcmp(argv[1], "--child") == 0) {
		return Child(argv[2], argv[3]);
	}
	g_exe = std::filesystem::absolute(argv[0]).string();
	g_dir = argc >= 2 ? argv[1] : std::filesystem::temp_directory_path().string();
	std::filesystem::create_directories(g_dir);
	Run("stand0_two", "stand0_two", "0", "1:2000:1", nullptr);
	Run("stand1_two", "stand0_two", "1", "1:2000:1", nullptr);
	Run("stand0_flush", "stand0_flush", "0", "1:2000:1", nullptr);
	Run("lf_nostand", "lf_nostand", "0", nullptr, "1");
	Run("lf_stand0", "lf_stand0", "0", "1:2000:1", "1");
	Run("lf_stand1", "lf_stand0", "1", "1:2000:1", "1");
	std::printf("PROBE DONE\n");
	return 0;
}
