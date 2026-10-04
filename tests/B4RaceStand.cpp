// Track F, B4 stand without the game (F15a HPP-491, ROADMAP s122 item 400(d)(2); moved to tests/ by F15c HPP-514,
// item 412(v), (g)(1)-(3)): the exit race of FileSystem::EmergencyShutdown (src/kernel/fileSystem.cpp, called by the
// at_quick_exit handler of src/emulator.cpp on the main thread) against a guest-like thread inside KernelOpen.
// One process = one trial, as in the game: EmergencyShutdown runs once per process while the opener keeps running.
// KYTY_FIX_B4 (read by fileSystem.cpp) selects the code under test: 0 - CloseAll, 1 - the B4 fix; unset or "" - the
// default of fileSystem.cpp (1 since FS6a, ROADMAP s122 item 454(g)(1)).
// Separate CMake target b4_race_stand (EXCLUDE_FROM_ALL, no add_test - not in the default ctest set); the driver is
// docs/track-f/f15c/run_stand_f15c.py.
//
// Usage: b4_race_stand <mode> <seed>
//   mode A - opener loops KernelOpen on a missing path (failure branch: CreateDescriptor, GetFile, DeleteDescriptor);
//            the main thread calls EmergencyShutdown once at a random point.
//   mode B - opener loops KernelOpen on an existing file + KernelFstat + KernelClose (the witness pattern of
//            C:/kyty/s131/log_dds131.txt; KernelRead is left out - it needs the GPU memory context).
//   mode C - control: the same loop as A, EmergencyShutdown only after the opener has stopped and joined.
//   mode D - data arm (item 412(g)(2)): a guest-like thread creates /data/d_<seed>.bin on a writable mount (the
//            directory stand_data under the current directory), writes 64 KiB of the seed pattern with KernelWrite in
//            seed-sized chunks, calls KernelFstat and then waits without KernelClose; the main thread calls
//            EmergencyShutdown and _Exit(0). The driver compares the file with the pattern after the process ends.
//            Pattern byte i: (i * 131 + seed * 17 + (i >> 8)) & 0xFF.
//   mode L - log line check (item 412(g)(3)): log to the console, FileSystem::Initialize, exit 0; the driver reads
//            the line "FixB4: mode=<0|1>" from stdout.
// Output: one line - "FATAL <file>:<line> iters=<n>" (fatal intercepted on the opener thread, process ends with
// _Exit(77)), "CLEAN iters=<n> after=<n>" (exit 0), "DATA <bytes> fstat=<size>" (mode D, _Exit(0)) or
// "LOGCHECK" (mode L). Any other end (access violation, abort) is seen by the driver from the exit code.
#include "common/assert.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "kernel/fileSystem.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <random>
#include <string>
#include <string_view>
#include <thread>
#include <vector>

namespace {

namespace FileSystem = Libs::LibKernel::FileSystem;

constexpr size_t D_SIZE = 65536;

std::atomic<uint64_t> g_iters {0};
std::atomic<bool>     g_stop {false};
std::atomic<int>      g_data_state {0}; // mode D: 0 - running, 1 - written and fstat done, -1 - failed

void OnFatal(const char* file, int line, std::string_view /*text*/) {
	std::printf("FATAL %s:%d iters=%llu\n", file, line,
	            static_cast<unsigned long long>(g_iters.load()));
	std::fflush(stdout);
	std::_Exit(77);
}

void Opener(char mode) {
	Common::ScopedFatalInterceptor intercept(OnFatal);
	FileSystem::FileStat st {};
	while (!g_stop.load(std::memory_order_acquire)) {
		if (mode == 'B') {
			const int fd = FileSystem::KernelOpen("/app0/stand_file.bin", 0, 0);
			if (fd >= 3) {
				// KernelRead is not used: it calls Memory::InvalidateMemory, which needs the GPU context
				// (memory.cpp:78 EXIT_IF without it; F15a smoke seeds 1001-1003). The witness log also has
				// KernelFstat between Open and Close.
				FileSystem::KernelFstat(fd, &st);
				FileSystem::KernelClose(fd);
			}
		} else {
			FileSystem::KernelOpen("/app0/missing_file.gnfp", 0, 0);
		}
		g_iters.fetch_add(1, std::memory_order_release);
	}
}

uint8_t PatternByte(size_t i, uint32_t seed) {
	return static_cast<uint8_t>((i * 131u + seed * 17u + (i >> 8u)) & 0xFFu);
}

int64_t g_fstat_size = -1;

void Writer(uint32_t seed) {
	Common::ScopedFatalInterceptor intercept(OnFatal);
	const std::string path = "/data/d_" + std::to_string(seed) + ".bin";
	// O_WRONLY | O_CREAT | O_TRUNC (fileSystem.cpp KernelOpen: access 0x3, creat 0x200, trunc 0x400).
	const int fd = FileSystem::KernelOpen(path.c_str(), 0x1 | 0x200 | 0x400, 0666);
	if (fd < 3) {
		g_data_state.store(-1, std::memory_order_release);
		return;
	}
	std::vector<uint8_t> data(D_SIZE);
	for (size_t i = 0; i < D_SIZE; i++) {
		data[i] = PatternByte(i, seed);
	}
	// Chunk size from the seed: 1 KiB .. 16 KiB.
	std::mt19937 rng(seed);
	size_t       pos = 0;
	while (pos < D_SIZE) {
		const size_t chunk = std::min<size_t>(D_SIZE - pos, 1024u * (1u + rng() % 16u));
		if (FileSystem::KernelWrite(fd, data.data() + pos, chunk) != static_cast<int64_t>(chunk)) {
			g_data_state.store(-1, std::memory_order_release);
			return;
		}
		pos += chunk;
	}
	FileSystem::FileStat st {};
	if (FileSystem::KernelFstat(fd, &st) != 0) {
		g_data_state.store(-1, std::memory_order_release);
		return;
	}
	g_fstat_size = st.st_size;
	g_data_state.store(1, std::memory_order_release);
	// No KernelClose: the guest is not stopped in the game; the process ends under this thread.
	while (true) {
		std::this_thread::sleep_for(std::chrono::seconds(1));
	}
}

} // namespace

int main(int argc, char** argv) {
	if (argc != 3 || std::strlen(argv[1]) != 1 || std::strchr("ABCDL", argv[1][0]) == nullptr) {
		std::fprintf(stderr, "usage: b4_race_stand A|B|C|D|L <seed>\n");
		return 2;
	}
	const char mode = argv[1][0];
	const auto seed = static_cast<uint32_t>(std::strtoul(argv[2], nullptr, 10));

	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction = (mode == 'L' ? Config::LogDirection::Console : Config::LogDirection::Silent);
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();

	if (mode == 'L') {
		FileSystem::Initialize();
		FileSystem::Shutdown();
		std::printf("LOGCHECK\n");
		std::fflush(stdout);
		return 0;
	}

	if (mode == 'D') {
		const auto data_root = std::filesystem::current_path() / "stand_data";
		std::filesystem::create_directories(data_root);
		FileSystem::Initialize();
		FileSystem::Mount(data_root, "/data");
		std::thread writer(Writer, seed);
		writer.detach();
		const auto t0 = std::chrono::steady_clock::now();
		while (g_data_state.load(std::memory_order_acquire) == 0) {
			if (std::chrono::steady_clock::now() - t0 > std::chrono::seconds(20)) {
				std::printf("DATA_TIMEOUT\n");
				std::fflush(stdout);
				std::_Exit(3);
			}
			std::this_thread::yield();
		}
		if (g_data_state.load(std::memory_order_acquire) < 0) {
			std::printf("DATA_FAILED\n");
			std::fflush(stdout);
			std::_Exit(4);
		}
		FileSystem::EmergencyShutdown();
		std::printf("DATA %zu fstat=%lld\n", D_SIZE, static_cast<long long>(g_fstat_size));
		std::fflush(stdout);
		std::_Exit(0);
	}

	const auto root = std::filesystem::current_path() / "stand_app0";
	std::filesystem::create_directories(root);
	{
		std::ofstream f(root / "stand_file.bin", std::ios::binary);
		std::vector<char> data(65536, 'x');
		f.write(data.data(), static_cast<std::streamsize>(data.size()));
	}

	FileSystem::Initialize();
	FileSystem::Mount(root, "/app0");

	std::thread opener(Opener, mode);

	// Warm-up: the opener is in its loop.
	while (g_iters.load(std::memory_order_acquire) < 100) {
		std::this_thread::yield();
	}

	if (mode == 'C') {
		g_stop.store(true, std::memory_order_release);
		opener.join();
		FileSystem::EmergencyShutdown();
		std::printf("CLEAN iters=%llu after=0\n", static_cast<unsigned long long>(g_iters.load()));
		std::fflush(stdout);
		return 0;
	}

	// A random point of the loop: busy wait 0..999 us from the seed.
	std::mt19937 rng(seed);
	const auto   delay = std::chrono::microseconds(rng() % 1000);
	const auto   t0    = std::chrono::steady_clock::now();
	while (std::chrono::steady_clock::now() - t0 < delay) {
	}

	FileSystem::EmergencyShutdown();
	const uint64_t at = g_iters.load(std::memory_order_acquire);

	// Let the opener go on after EmergencyShutdown (the guest is not stopped in the game): 20 more iterations or 2 s.
	const auto t1 = std::chrono::steady_clock::now();
	while (g_iters.load(std::memory_order_acquire) < at + 20 &&
	       std::chrono::steady_clock::now() - t1 < std::chrono::seconds(2)) {
		std::this_thread::yield();
	}
	g_stop.store(true, std::memory_order_release);
	opener.join();

	std::printf("CLEAN iters=%llu after=%llu\n", static_cast<unsigned long long>(g_iters.load()),
	            static_cast<unsigned long long>(g_iters.load() - at));
	std::fflush(stdout);
	return 0;
}
