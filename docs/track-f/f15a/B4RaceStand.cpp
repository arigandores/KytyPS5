// Track F, F15a (HPP-491, ROADMAP s122 item 400(d)(2)): B4 stand without the game - the exit race of
// FileSystem::EmergencyShutdown (FileDescriptors::CloseAll, src/kernel/fileSystem.cpp:243, called by the
// at_quick_exit handler src/emulator.cpp:243 on the main thread) against a guest-like thread inside KernelOpen.
// One process = one trial, as in the game: CloseAll runs once per process while the opener keeps running.
// The code of src/ is the current main, not changed; this file and its CMake line live only in the F15a worktree
// and in docs/track-f/f15a/ (not in main).
//
// Usage: b4_race_stand <mode> <seed>
//   mode A - opener loops KernelOpen on a missing path (failure branch: CreateDescriptor :443, GetFile :444,
//            DeleteDescriptor :476); the main thread calls EmergencyShutdown once at a random point.
//   mode B - opener loops KernelOpen on an existing file + KernelFstat + KernelClose (the witness pattern of
//            C:/kyty/s131/log_dds131.txt: open, fstat, read, close of .gnfp files by the streaming thread;
//            KernelRead is left out - it needs the GPU memory context).
//   mode C - control: the same loop as A, EmergencyShutdown only after the opener has stopped and joined.
// Output: one line - "FATAL <file>:<line> iters=<n>" (fatal intercepted on the opener thread, process ends with
// _Exit(77)), or "CLEAN iters=<n> after=<n>" (exit 0). Any other end (access violation, abort) is seen by the
// driver from the exit code.
#include "common/assert.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "kernel/fileSystem.h"

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

std::atomic<uint64_t> g_iters {0};
std::atomic<bool>     g_stop {false};

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
				// (memory.cpp:78 EXIT_IF without it; smoke seeds 1001-1003). The witness log also has
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

} // namespace

int main(int argc, char** argv) {
	if (argc != 3 || std::strlen(argv[1]) != 1 || std::strchr("ABC", argv[1][0]) == nullptr) {
		std::fprintf(stderr, "usage: b4_race_stand A|B|C <seed>\n");
		return 2;
	}
	const char mode = argv[1][0];
	const auto seed = static_cast<uint32_t>(std::strtoul(argv[2], nullptr, 10));

	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction = Config::LogDirection::Silent;
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();

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

	// Let the opener go on after CloseAll (the guest is not stopped in the game): 20 more iterations or 2 s.
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
