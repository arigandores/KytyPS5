// Track F, F8 stand without the game (F18c HPP-539, ROADMAP s122 item 441(d)(1)): the SDL2 reference count of the audio
// subsystem against the emulator call sites of src/libs/audio.cpp (SdlAudioSubsystemInit, SdlAudioAcquire - linked from
// the emulator sources of this build, not copied). SDL2 is 3rdparty/SDL2 of the same build; the audio driver comes from
// SDL_AUDIODRIVER, which must be "dummy" or "disk" (the stand refuses any other value before its first SDL call, so the
// host sound devices are never opened). KYTY_FIX_F8 (read by audio.cpp once per process) selects the site path.
// Separate CMake target f8_audio_stand (EXCLUDE_FROM_ALL, no add_test - not in the default ctest set); the driver is
// docs/track-f/f18c/run_stand_f18c.py, which decides PASS/FAIL from the printed values.
//
// Usage: f8_audio_stand <mode> <ndev> [<name prefix>]
//   ndev output devices are opened as the AudioOut site C1 does (SdlAudioSubsystemInit, SDL_OpenAudioDevice with a
//   queue, unpaused); device k is opened by the name "<prefix><k>.raw" when a prefix is given (driver "disk": the name is
//   the output file), by the default device otherwise (driver "dummy" has one output device only: SDL_dummyaudio.c:55,
//   SDL_audio.c:1367).
//   i   - 300 calls of SdlAudioSubsystemInit (the pad haptics site C2 without a pad), after each call one
//         SDL_QueueAudio per device. Lines "call <k> fail <n>" for every call with n > 0 failing devices.
//   ii  - 10 000 calls of SdlAudioAcquire, after each call one SDL_QueueAudio per device.
//   iii - 2 threads x 5 000 calls of SdlAudioAcquire started together on a cold subsystem, then the devices are opened
//         and one SDL_QueueAudio per device is made.
// Output: "key=value" lines; "END" last. Exit 0 unless the arguments are bad (2) or the driver is refused (3).
#define SDL_MAIN_HANDLED
#include "SDL.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "libs/audio_internal.h"

#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <vector>

namespace {

namespace AudioInternal = Libs::Audio::AudioInternal;

std::vector<SDL_AudioDeviceID> g_devices;
std::vector<uint8_t>           g_pcm(512, 0); // 128 frames of s16 stereo silence
std::string                    g_first_error;

int OpenDevices(int ndev, const char* prefix) {
	int opened = 0;
	for (int k = 0; k < ndev; k++) {
		if (AudioInternal::SdlAudioSubsystemInit() < 0) {
			std::printf("open_init_failed=%d error=\"%s\"\n", k, SDL_GetError());
			continue;
		}
		SDL_AudioSpec desired {};
		desired.freq     = 48000;
		desired.format   = AUDIO_S16SYS;
		desired.channels = 2;
		desired.samples  = 1024;
		desired.callback = nullptr;
		SDL_AudioSpec     obtained {};
		const std::string name = prefix != nullptr ? std::string(prefix) + std::to_string(k) + ".raw" : std::string();
		const SDL_AudioDeviceID dev =
		    SDL_OpenAudioDevice(prefix != nullptr ? name.c_str() : nullptr, 0, &desired, &obtained, SDL_AUDIO_ALLOW_ANY_CHANGE);
		if (dev == 0) {
			std::printf("open_failed=%d error=\"%s\"\n", k, SDL_GetError());
			continue;
		}
		SDL_PauseAudioDevice(dev, 0);
		g_devices.push_back(dev);
		opened++;
	}
	std::printf("devices_opened=%d\n", opened);
	for (const auto dev: g_devices) {
		std::printf("device=%u\n", static_cast<uint32_t>(dev));
	}
	return opened;
}

// One SDL_QueueAudio per device; returns the number of failing devices and keeps the first error text.
int QueueAll() {
	int failed = 0;
	for (const auto dev: g_devices) {
		if (SDL_QueueAudio(dev, g_pcm.data(), static_cast<Uint32>(g_pcm.size())) < 0) {
			if (g_first_error.empty()) {
				g_first_error = SDL_GetError();
			}
			failed++;
		} else {
			SDL_ClearQueuedAudio(dev);
		}
	}
	return failed;
}

void PrintCounters() {
	std::printf("init_calls=%llu\n", static_cast<unsigned long long>(AudioInternal::SdlAudioInitCalls()));
	std::printf("acq=%llu\n", static_cast<unsigned long long>(AudioInternal::SdlAudioAcquireCalls()));
	std::printf("was_init=%u\n", static_cast<unsigned>(SDL_WasInit(SDL_INIT_AUDIO)));
	const char* driver = SDL_GetCurrentAudioDriver();
	std::printf("driver=%s\n", driver != nullptr ? driver : "(none)");
}

} // namespace

int main(int argc, char** argv) {
	if (argc < 3 || argc > 4) {
		std::fprintf(stderr, "usage: f8_audio_stand i|ii|iii <ndev> [<name prefix>]\n");
		return 2;
	}
	const std::string mode   = argv[1];
	const int         ndev   = std::atoi(argv[2]);
	const char*       prefix = argc == 4 ? argv[3] : nullptr;
	if ((mode != "i" && mode != "ii" && mode != "iii") || ndev < 0 || ndev > 8) {
		std::fprintf(stderr, "usage: f8_audio_stand i|ii|iii <ndev> [<name prefix>]\n");
		return 2;
	}
	const char* want = std::getenv("SDL_AUDIODRIVER");
	if (want == nullptr || (std::strcmp(want, "dummy") != 0 && std::strcmp(want, "disk") != 0)) {
		std::printf("REFUSED SDL_AUDIODRIVER=%s (dummy or disk only)\n", want != nullptr ? want : "(unset)");
		std::fflush(stdout);
		return 3;
	}

	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction = Config::LogDirection::Console;
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();

	std::printf("mode=%s ndev=%d sdl_audiodriver=%s\n", mode.c_str(), ndev, want);

	if (mode == "iii") {
		std::atomic<int>  ready {0};
		std::atomic<bool> go {false};
		std::atomic<int>  failed {0};
		const auto        worker = [&]() {
			ready.fetch_add(1);
			while (!go.load(std::memory_order_acquire)) {
			}
			for (int n = 0; n < 5000; n++) {
				if (AudioInternal::SdlAudioAcquire() < 0) {
					failed.fetch_add(1);
				}
			}
		};
		std::thread a(worker);
		std::thread b(worker);
		while (ready.load() != 2) {
			std::this_thread::yield();
		}
		go.store(true, std::memory_order_release);
		a.join();
		b.join();
		std::printf("acquire_failed=%d\n", failed.load());
		std::printf("init_calls_after_threads=%llu\n", static_cast<unsigned long long>(AudioInternal::SdlAudioInitCalls()));
		std::printf("acq_after_threads=%llu\n", static_cast<unsigned long long>(AudioInternal::SdlAudioAcquireCalls()));
		std::printf("was_init_after_threads=%u\n", static_cast<unsigned>(SDL_WasInit(SDL_INIT_AUDIO)));
		OpenDevices(ndev, prefix);
		std::printf("queue_failed_after=%d\n", QueueAll());
	} else {
		OpenDevices(ndev, prefix);
		const int calls        = (mode == "i" ? 300 : 10000);
		int       first_fail   = 0;
		int       fail_at_first = 0;
		int       calls_failed = 0;
		uint64_t  queue_failed = 0;
		int       init_failed  = 0;
		for (int k = 1; k <= calls; k++) {
			const int rc = (mode == "i" ? AudioInternal::SdlAudioSubsystemInit() : AudioInternal::SdlAudioAcquire());
			if (rc < 0) {
				init_failed++;
			}
			const int f = QueueAll();
			if (f > 0) {
				if (first_fail == 0) {
					first_fail    = k;
					fail_at_first = f;
				}
				calls_failed++;
				queue_failed += static_cast<uint64_t>(f);
				if (mode == "i") {
					std::printf("call %d fail %d\n", k, f);
				}
			}
		}
		std::printf("calls=%d\n", calls);
		std::printf("init_failed=%d\n", init_failed);
		std::printf("first_fail_call=%d\n", first_fail);
		std::printf("fail_devices_at_first=%d\n", fail_at_first);
		std::printf("calls_with_fail=%d\n", calls_failed);
		std::printf("queue_failed=%llu\n", static_cast<unsigned long long>(queue_failed));
	}
	std::printf("first_error=\"%s\"\n", g_first_error.c_str());
	PrintCounters();
	Log::Flush();
	std::printf("END\n");
	std::fflush(stdout);
	// No SDL_Quit and no subsystem teardown: the emulator never quits the audio subsystem either.
	std::_Exit(0);
}
