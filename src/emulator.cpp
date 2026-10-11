#include "emulator.h"


#include "common/abi.h"
#include "common/assert.h"
#include "common/diagB32.h"
#include "common/emulatorConfig.h"
#include "common/file.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "common/singleton.h"
#include "common/stringUtils.h"
#include "common/subsystems.h"
#include "common/systemInfo.h"
#include "common/threads.h"
#include "graphics/presentation/window.h"
#include "graphics/host_gpu/renderer/pipeline/fixF20.h"
#include "kernel/fileSystem.h"
#include "kernel/memory.h"
#include "kernel/pthread.h"
#include "kytyGitVersion.h"
#include "libs/agc.h"
#include "libs/audio.h"
#include "libs/controller.h"
#include "libs/libSaveData.h"
#include "libs/libs.h"
#include "libs/network.h"
#include "loader/gamePatchFile.h"
#include "loader/runtimeLinker.h"
#include "loader/systemContent.h"
#include "loader/timer.h"

#include <atomic>
#include <cstdlib>
#include <chrono>
#include <cstdio>
#include <string>
#include <filesystem>
#include <thread>

namespace Emulator {

// Track F, F33c (HPP-744; ROADMAP s122 item 675(d)(1), (v)(3)-(5)): stand KYTY_TEST_EXITFATAL=<arm>:<seed>, edition 3
// (edition 1 - F33a 5f48cc3e, test binary only; edition 2 - F33c e5979953; edition 3 - F33c2 HPP-748, item 681(v)(1):
// the arm CN and the event nested_fatal); off when unset or empty. The process runs the real Init (the Graphics
// lifecycle is replaced by an entry with the same null emergency callback - no window, no GPU), the real at_quick_exit
// registration, KYTY_FIX_F21 as read by Run and the mounts of Run; it loads no ELF and runs no guest code. One injector
// thread (Common::Thread, as guest_thread of Execute; role "guest") raises a fatal with EXIT_IF - the path of a guest
// fatal: DbgReport -> Log::WriteFatal -> EmergencyShutdownActive -> EXIT_HALT -> DbgExit(321). The observer is
// Common::Subsystems::SetEmergencyHook (called on the F21 path of EmergencyShutdownActive only: armed stand or
// KYTY_FIX_F21=1). pos = seed % 13: 0..11 - the entries counted from the end, 12 - after the loop, before clear.
//   P2 - the main thread ends the process by std::quick_exit(0) (the exit of Execute); at position pos of its walk it
//        releases the injector and waits <= 2 s for the injector's entry into EmergencyShutdownActive, then goes on;
//   R2 - as P2 without the wait;
//   G  - reverse order: the injector raises its fatal first (50 ms after the start); at position pos of its walk it
//        releases the main thread and waits <= 2 s for the main thread's entry; the main thread, released, calls
//        std::quick_exit(0) (control - the main thread entered while the injector's walk was in progress);
//   C  - control: no exit on the main thread, the injector raises the fatal 50 ms after the start;
//   N  - control: std::quick_exit(0) without a fatal;
//   H  - the main thread ends the process by std::quick_exit(0); at position pos of its walk it releases the injector
//        and sleeps 15 s inside the walk (> T of KYTY_FIX_F21) - the positive control of the wait limit;
//   HG - reference arm of F33c (not a member of item 675(d)(1)): as G, but at position pos of its walk the injector (the
//        owner) releases the main thread and sleeps 15 s inside the walk; the main thread enters through quick_exit
//        while it holds the CRT exit lock - the wait limit of the thread that ends the process;
//   CN - edition 3 (F33c2, item 681(v)(1)): as C (the injector raises a fatal 50 ms after the start, the main thread
//        never exits), and inside the injector's own walk, right before the first emergency callback it reaches, the
//        injector raises a second fatal (EXIT_IF) - a fatal inside an emergency callback of the owner (the form of
//        the F33d probe probe_cn.py; once per process; line "ExitFatal: nested_fatal"). pos is printed, not used.
// Every event is one stderr line "ExitFatal: ..." (fwrite + fflush) with t_us (steady clock from Parse) and, where the
// driver needs the wall time, e_us (system clock, microseconds since the epoch).
namespace ExitFatalStand {

enum class Arm { Off, P2, R2, G, C, N, H, HG, CN };

static constexpr size_t   kPositions   = 13;
static constexpr uint64_t kPeerWaitUs  = 2000000;
static constexpr uint32_t kHoldMs      = 15000;
static constexpr uint64_t kMainGoCapUs = 5000000;

static Arm               g_arm  = Arm::Off;
static uint32_t          g_seed = 0;
static size_t            g_pos  = 0;
static std::atomic<bool> g_go {false};      // the injector may raise its fatal (P2, R2, H)
static std::atomic<bool> g_go_main {false}; // the main thread may call quick_exit (G, HG)
static std::atomic<bool> g_inject {false};
static std::atomic<int>  g_main_walk {0};
static std::atomic<int>  g_guest_walk {0};
static std::atomic<int>  g_main_entered {0};
static std::atomic<int>  g_guest_entered {0};
static std::atomic<int>  g_walk_seq {0};
static std::atomic<int>  g_triggered {0};
static std::atomic<int>  g_nested_fatal {0}; // CN: the second fatal was raised (once per process)
static thread_local int  t_seq   = 0;
static thread_local int  t_cbs   = 0;
static thread_local int  t_depth = 0;

static std::chrono::steady_clock::time_point g_t0;

struct GraphicsPlaceholder {
	static constexpr const char* name = "Graphics (KYTY_TEST_EXITFATAL placeholder: no window, no GPU)";
	static void initialize() {}
	static void shutdown() {}
};

static bool Armed() {
	return g_arm != Arm::Off;
}

static uint64_t NowUs() {
	return static_cast<uint64_t>(
	    std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - g_t0).count());
}

static uint64_t EpochUs() {
	return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::microseconds>(
	                                 std::chrono::system_clock::now().time_since_epoch())
	                                 .count());
}

static void Line(const std::string& text) {
	std::fwrite(text.data(), 1, text.size(), stderr);
	std::fflush(stderr);
}

static bool IsMain() {
	return Common::Thread::IsMainThread();
}

static const char* Role() {
	return IsMain() ? "main" : "guest";
}

static const char* ArmName() {
	switch (g_arm) {
		case Arm::P2: return "P2";
		case Arm::R2: return "R2";
		case Arm::G: return "G";
		case Arm::C: return "C";
		case Arm::N: return "N";
		case Arm::H: return "H";
		case Arm::HG: return "HG";
		case Arm::CN: return "CN";
		default: return "off";
	}
}

static void Hook(int event, size_t index, size_t size);

// Main thread, before Init and before KYTY_FIX_F21 is read: parse and, armed, set the observer.
static void Parse() {
	const char* value = std::getenv("KYTY_TEST_EXITFATAL");
	if (value == nullptr || value[0] == '\0') {
		return;
	}
	char     arm[4] = {};
	unsigned seed   = 0;
	Arm      parsed = Arm::Off;
	if (std::sscanf(value, "%3[A-Z0-9]:%u", arm, &seed) == 2) {
		const std::string name(arm);
		parsed = name == "P2"  ? Arm::P2
		         : name == "R2" ? Arm::R2
		         : name == "G"  ? Arm::G
		         : name == "C"  ? Arm::C
		         : name == "N"  ? Arm::N
		         : name == "H"  ? Arm::H
		         : name == "HG" ? Arm::HG
		         : name == "CN" ? Arm::CN
		                        : Arm::Off;
	}
	if (parsed == Arm::Off) {
		std::fprintf(stderr, "KYTY_TEST_EXITFATAL: bad value '%s' (<P2|R2|G|C|N|H|HG|CN>:<seed>), stand off\n", value);
		return;
	}
	g_arm  = parsed;
	g_seed = seed;
	g_pos  = seed % kPositions;
	g_t0   = std::chrono::steady_clock::now();
	Common::Subsystems::SetEmergencyHook(Hook);
}

// Inside a walk at position pos, on the thread whose walk triggers (main for P2, R2, H; the injector for G, HG).
static void Trigger(size_t pos) {
	if (g_triggered.exchange(1) != 0) {
		return;
	}
	const auto t_trig = NowUs();
	uint64_t   waited = 0;
	switch (g_arm) {
		case Arm::P2:
			g_go.store(true);
			while (g_guest_entered.load() == 0 && NowUs() - t_trig < kPeerWaitUs) {
				std::this_thread::yield();
			}
			waited = NowUs() - t_trig;
			break;
		case Arm::R2: g_go.store(true); break;
		case Arm::G:
			g_go_main.store(true);
			while (g_main_entered.load() == 0 && NowUs() - t_trig < kPeerWaitUs) {
				std::this_thread::yield();
			}
			waited = NowUs() - t_trig;
			break;
		case Arm::H: g_go.store(true); break;
		case Arm::HG: g_go_main.store(true); break;
		default: break;
	}
	Line(fmt::format("ExitFatal: trigger role={} pos={} waited_us={} main_entered={} guest_entered={} t_us={}\n",
	                 Role(), pos, waited, g_main_entered.load(), g_guest_entered.load(), NowUs()));
	if (g_arm == Arm::H || g_arm == Arm::HG) {
		Line(fmt::format("ExitFatal: hold_begin role={} pos={} ms={} t_us={} e_us={}\n", Role(), pos, kHoldMs, NowUs(),
		                 EpochUs()));
		Common::Thread::Sleep(kHoldMs);
		Line(fmt::format("ExitFatal: hold_end role={} pos={} t_us={}\n", Role(), pos, NowUs()));
	}
}

static bool TriggerHere() {
	if (g_arm == Arm::P2 || g_arm == Arm::R2 || g_arm == Arm::H) {
		return IsMain();
	}
	if (g_arm == Arm::G || g_arm == Arm::HG) {
		return !IsMain();
	}
	return false;
}

static void Hook(int event, size_t index, size_t size) {
	const bool main = IsMain();
	switch (event) {
		case Common::kEmergencyEnter: {
			(main ? g_main_entered : g_guest_entered).store(1);
			Line(fmt::format("ExitFatal: enter role={} tid={} main_walk={} guest_walk={} t_us={} e_us={}\n", Role(),
			                 Common::Thread::GetThreadIdUnique(), g_main_walk.load(), g_guest_walk.load(), NowUs(),
			                 EpochUs()));
			break;
		}
		case Common::kEmergencyWalkBegin: {
			const int nested = t_depth > 0 ? 1 : 0;
			t_depth++;
			t_seq = g_walk_seq.fetch_add(1) + 1;
			t_cbs = 0;
			(main ? g_main_walk : g_guest_walk).store(1);
			Line(fmt::format("ExitFatal: walk_begin seq={} role={} size={} nested={} t_us={}\n", t_seq, Role(), size,
			                 nested, NowUs()));
			break;
		}
		case Common::kEmergencyBeforeEntry:
			if (index == g_pos && TriggerHere()) {
				Trigger(index);
			}
			break;
		case Common::kEmergencyBeforeCallback:
			t_cbs++;
			Line(fmt::format("ExitFatal: cb seq={} role={} pos={} t_us={}\n", t_seq, Role(), index, NowUs()));
			if (g_arm == Arm::CN && !main && g_nested_fatal.exchange(1) == 0) {
				// CN: a fatal inside the owner's emergency callback (the callback of this entry is not reached).
				Line(fmt::format("ExitFatal: nested_fatal role={} seq={} pos={} t_us={}\n", Role(), t_seq, index,
				                 NowUs()));
				EXIT_IF(g_arm == Arm::CN);
			}
			break;
		case Common::kEmergencyAfterLoop:
			if (g_pos == kPositions - 1 && TriggerHere()) {
				Trigger(index);
			}
			break;
		case Common::kEmergencyAfterClear:
			Line(fmt::format("ExitFatal: walk_end seq={} role={} callbacks={} t_us={} e_us={}\n", t_seq, Role(), t_cbs,
			                 NowUs(), EpochUs()));
			(main ? g_main_walk : g_guest_walk).store(0);
			t_depth--;
			break;
		case Common::kEmergencyReenter:
			Line(fmt::format("ExitFatal: reenter role={} t_us={}\n", Role(), NowUs()));
			break;
		case Common::kEmergencyDoneSeen:
			Line(fmt::format("ExitFatal: done_seen role={} t_us={}\n", Role(), NowUs()));
			break;
		case Common::kEmergencyWaitBegin:
			Line(fmt::format("ExitFatal: wait_begin role={} t_us={} e_us={}\n", Role(), NowUs(), EpochUs()));
			break;
		case Common::kEmergencyWaitDone:
			Line(fmt::format("ExitFatal: wait_done role={} waited_us={} t_us={}\n", Role(), index, NowUs()));
			break;
		case Common::kEmergencyWaitExpired:
			Line(fmt::format("ExitFatal: wait_expired role={} waited_us={} t_us={} e_us={}\n", Role(), index, NowUs(),
			                 EpochUs()));
			break;
		case Common::kEmergencyExpiredSeen:
			Line(fmt::format("ExitFatal: expired_seen role={} t_us={}\n", Role(), NowUs()));
			break;
		default: break;
	}
}

static void Injector(void* /*arg*/) {
	if (g_arm == Arm::C || g_arm == Arm::G || g_arm == Arm::HG || g_arm == Arm::CN) {
		Common::Thread::Sleep(50);
	} else {
		while (!g_go.load()) {
			std::this_thread::yield();
		}
	}
	Line(fmt::format("ExitFatal: inject role={} main_walk={} t_us={}\n", Role(), g_main_walk.load(), NowUs()));
	g_inject.store(true);
	EXIT_IF(g_inject.load());
	Line("ExitFatal: inject returned\n");
}

[[noreturn]] static void Run() {
	Line(fmt::format("ExitFatal: config arm={} seed={} pos={} positions={} fix={} wait_ms={} t_us={} e_us={}\n",
	                 ArmName(), g_seed, g_pos, kPositions, Common::Subsystems::FixF21On() ? 1 : 0,
	                 Common::Subsystems::kFixF21WaitMs, NowUs(), EpochUs()));
	LOGF("ExitFatal: config arm=%s seed=%u pos=%u\n", ArmName(), g_seed, static_cast<unsigned>(g_pos));
	auto* injector = new Common::Thread(Injector, nullptr); // never joined or destroyed - as guest_thread under quick_exit
	(void)injector;
	if (g_arm == Arm::C || g_arm == Arm::CN) {
		for (;;) {
			Common::Thread::Sleep(1000);
		}
	}
	if (g_arm == Arm::G || g_arm == Arm::HG) {
		const auto t_wait = NowUs();
		while (!g_go_main.load() && NowUs() - t_wait < kMainGoCapUs) {
			std::this_thread::yield();
		}
	} else {
		Common::Thread::Sleep(50);
	}
	Line(fmt::format("ExitFatal: quick_exit t_us={}\n", NowUs()));
	std::quick_exit(0);
}

} // namespace ExitFatalStand

static void SetCacheTestEnvironment(const char* key, const char* value) {
	// SDL_setenv updates SDL's private environment on Windows; cache switches use std::getenv.
#if defined(_WIN32)
	EXIT_IF(_putenv_s(key, value) != 0);
#else
	EXIT_IF(setenv(key, value, 1) != 0);
#endif
}

static void PrintSystemInfo() {
	const Common::SystemInfo info = Common::GetSystemInfo();

#if defined(__APPLE__)
	static constexpr auto platform_name = "macOS";
#elif KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	static constexpr auto platform_name = "Windows";
#elif KYTY_PLATFORM == KYTY_PLATFORM_LINUX
	static constexpr auto platform_name = "Linux";
#else
	static constexpr auto platform_name = "Unknown";
#endif

	LOGF("Build\n"
	     "  version: %s\n\n"
	     "Host\n"
	     "  os:      %s\n"
	     "  cpu:     %s\n"
	     "  threads: %u\n\n",
	     KYTY_BUILD_LABEL, platform_name, info.ProcessorName.c_str(),
	     std::thread::hardware_concurrency());
}

static void KytyClose() {
	auto* rt = Common::Singleton<Loader::RuntimeLinker>::Instance();

	rt->Clear();

	LOGF("done!\n");

	Common::Subsystems::EmergencyShutdownActive();
}

static void MountOrCreateDir(const std::filesystem::path& dir, const std::string& point) {
	if (!Common::File::IsDirectoryExisting(dir)) {
		Common::File::CreateDirectories(dir);
	}

	EXIT_NOT_IMPLEMENTED(!Common::File::IsDirectoryExisting(dir));

	Libs::LibKernel::FileSystem::Mount(dir, point);
	auto dir_text = Common::PathToString(dir);
	LOGF("Mounted %s -> %s\n", point.c_str(), dir_text.c_str());
}

static void MountSandboxDirs() {
	std::string title_id;
	if (!Loader::SystemContentParamSfoGetString("TITLE_ID", &title_id) || title_id.empty()) {
		title_id = "UNKNOWN";
	}

	MountOrCreateDir("_DownloadData/" + title_id, "/download0");
	MountOrCreateDir("_TempData/" + title_id, "/temp0");
	MountOrCreateDir("_TempData/" + title_id, "/temp");
}

static bool ClearDirectoryContents(const std::filesystem::path& dir) {
	bool ok = true;

	for (const auto& entry: Common::File::GetDirEntries(dir)) {
		if (entry.name == "." || entry.name == "..") {
			continue;
		}

		auto path = dir / entry.name;

		if (entry.is_file) {
			Common::File::RemoveReadonly(path);
			ok = Common::File::DeleteFile(path) && ok;
		} else {
			ok = ClearDirectoryContents(path) && ok;
			ok = Common::File::DeleteDirectory(path) && ok;
		}
	}

	return ok;
}

static void ClearDebugTextureFolder() {
	const std::string debug_texture_folder = "_Textures";

	if (!Common::File::IsDirectoryExisting(debug_texture_folder)) {
		Common::File::CreateDirectories(debug_texture_folder);
		return;
	}

	if (!ClearDirectoryContents(debug_texture_folder)) {
		LOGF_COLOR(Log::Color::BrightYellow, "TextureDump: failed to completely clear %s\n",
		           debug_texture_folder.c_str());
	}
}

static void Init(const Config::ConfigOptions& cfg, const std::filesystem::path& param_json,
                 Common::Subsystems& subsystems) {
	EXIT_IF(!Common::Thread::IsMainThread());

	subsystems.Initialize<Config::Lifecycle>();
	Config::Load(cfg);
	subsystems.Initialize<Log::Lifecycle>();

	if (Common::File::IsFileExisting(param_json)) {
		Loader::SystemContentLoadParamSfo(param_json);
		if (const auto flexible_memory_size = Loader::SystemContentGetFlexibleMemorySize();
		    flexible_memory_size != 0) {
			Libs::LibKernel::Memory::SetFlexibleMemorySize(flexible_memory_size);
		}
	}

	// Initialization order is explicit; destruction is automatic and reversed.
	subsystems.Initialize<Loader::Timer::Lifecycle>();
	subsystems.Initialize<Libs::LibKernel::PthreadLifecycle>();
	subsystems.Initialize<Profiler::Lifecycle>();
	subsystems.Initialize<Libs::Network::Lifecycle>();
	subsystems.Initialize<Libs::LibKernel::Memory::Lifecycle>();
	subsystems.Initialize<Libs::LibKernel::FileSystem::Lifecycle>();
	subsystems.Initialize<Libs::SaveData::Lifecycle>();
	subsystems.Initialize<Libs::Controller::Lifecycle>();
	subsystems.Initialize<Libs::Audio::Lifecycle>();
	if (!ExitFatalStand::Armed()) {
		subsystems.Initialize<Libs::Graphics::Lifecycle>();
	} else {
		subsystems.Initialize<ExitFatalStand::GraphicsPlaceholder>(); // F33c stand: no window, no GPU
	}
}

static void LoadElf(const std::filesystem::path& elf, bool dbg_print_reloc = false,
                    const std::filesystem::path& save_name = {}) {
	auto* rt = Common::Singleton<Loader::RuntimeLinker>::Instance();

	auto* program = rt->LoadProgram(
	    Libs::LibKernel::FileSystem::GetRealFilename(Common::PathToGenericString(elf)));

	if (dbg_print_reloc) {
		program->dbg_print_reloc = true;
	}

	if (!save_name.empty()) {
		rt->SaveProgram(program, Libs::LibKernel::FileSystem::GetRealFilename(
		                             Common::PathToGenericString(save_name)));
	}
}

static void Execute(const std::filesystem::path& game_patch) {
	if (!Libs::Graphics::WindowPrepareShaders()) {
		Libs::Graphics::FixF20::PrintExitStat(); // Track F, F42a: "FixF20Stat: when=exit" (KYTY_FIX_F20=1 only)
		std::quick_exit(0);
	}
	auto           patch_path = game_patch;
	Common::Thread guest_thread(
	    [](void* param) {
		    auto* rt = Common::Singleton<Loader::RuntimeLinker>::Instance();
		    rt->Execute(*static_cast<const std::filesystem::path*>(param));
	    },
	    &patch_path);
	Libs::Graphics::WindowRun();
	Libs::Graphics::FixF20::PrintExitStat(); // Track F, F42a: "FixF20Stat: when=exit" (KYTY_FIX_F20=1 only)
	std::quick_exit(0);
}

void Run(const RunOptions& options) {
	// Track F, F20j: KYTY_DIAG_B32 / KYTY_TEST_B32 are read here once, before any guest thread (RC10).
	Common::DiagB32::Init();
	// Process-local test overrides: no cache files are removed or modified by the cold mode.
	// prepare-cold retains the known shader catalogue but forces fresh driver compilation.
	if (const char* mode = std::getenv("KYTY_CACHE_MODE"); mode != nullptr && mode[0] != 0) {
		const std::string selected(mode);
		if (selected != "cold" && selected != "prepare-cold") {
			EXIT("KYTY_CACHE_MODE must be cold or prepare-cold\n");
		}
		SetCacheTestEnvironment("KYTY_PIPELINE_CACHE", "0");
		if (selected == "cold") {
			SetCacheTestEnvironment("KYTY_SHADER_CACHE", "0");
			SetCacheTestEnvironment("KYTY_SHADER_SEED", "0");
		}
		const auto salt = std::to_string(std::chrono::high_resolution_clock::now().time_since_epoch().count());
		SetCacheTestEnvironment("KYTY_PIPELINE_SALT", salt.c_str());
		std::fprintf(stdout, "Cache test mode: %s (fresh driver namespace %s)\n", selected.c_str(), salt.c_str());
	}
	if (options.app0_dir.empty()) {
		EXIT("app0 directory is required\n");
	}

	if (options.elf.empty()) {
		EXIT("ELF is required\n");
	}

	const auto         param_json = options.app0_dir / "sce_sys" / "param.json";
	// Track F, F33c (KYTY_FIX_F21; ROADMAP s122 item 675(g)): read once here - the main thread, before Init
	// starts any host thread and before the guest threads.
	ExitFatalStand::Parse(); // F33c stand KYTY_TEST_EXITFATAL (off when unset): the observer is set before the knob
	Common::Subsystems::InitFixF21();
	Common::Subsystems subsystems(true);
	Init(options.config, param_json, subsystems);
	Common::Subsystems::LogFixF21(); // F33c: "FixF21: mode=<0|1>" once, after Log::Initialize (Init)

	ClearDebugTextureFolder();

	PrintSystemInfo();
	Common::DiagB32::LogHeader(); // Track F, F20j: "DiagB32: mode=1 ..." / "TestB32: config ..." once
	std::string title_id;
	if (Loader::SystemContentParamSfoGetString("TITLE_ID", &title_id) && !title_id.empty()) {
		Log::WriteToConsoleAndLog(fmt::format("Title ID: {}\n", title_id));
	}

	int ok = atexit(KytyClose);
	EXIT_NOT_IMPLEMENTED(ok != 0);

	// Guest threads are still running, so skip KytyClose() and only flush emergency state.
	ok = at_quick_exit(Common::Subsystems::EmergencyShutdownActive);
	EXIT_NOT_IMPLEMENTED(ok != 0);

	Libs::LibKernel::FileSystem::Mount(options.app0_dir, "/app0");
	Libs::LibKernel::FileSystem::Mount(options.app0_dir, "/hostapp");

	MountSandboxDirs();

	if (ExitFatalStand::Armed()) {
		ExitFatalStand::Run(); // F33c stand: never returns
	}

	// Track P, KYTY_GAME_PATCH (loader/gamePatchFile.h, ROADMAP s122 item 333(d)): the decision before Libs::InitAll,
	// whose registration reads PVar::Mode(); without the variable nothing is called.
	if (const char* game_patch_file = std::getenv("KYTY_GAME_PATCH");
	    game_patch_file != nullptr && game_patch_file[0] != '\0') {
		Loader::GamePatchFile::Load(
		    Libs::LibKernel::FileSystem::GetRealFilename(Common::PathToGenericString(options.elf)));
	}

	auto* rt = Common::Singleton<Loader::RuntimeLinker>::Instance();
	Libs::InitAll(rt->Symbols());

	LoadElf(options.elf);

	Execute(options.game_patch);
}

} // namespace Emulator
