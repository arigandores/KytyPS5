# F33a (HPP-736; ROADMAP s122 item 673(z)(1)): stand KYTY_TEST_EXITFATAL in the clean FS11 worktree
# C:/kyty/f287/f33a/wt (ee9632be). Test binary only - this patch does NOT go to main.
# Anchors are whole lines; CR is removed before the search and restored if the file had it; output is written as bytes.
import sys

WT = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f33a/wt'


def load(path):
    raw = open(path, 'rb').read().decode('utf-8')
    crlf = '\r\n' in raw
    return raw.replace('\r\n', '\n'), crlf


def save(path, text, crlf):
    if crlf:
        text = text.replace('\n', '\r\n')
    open(path, 'wb').write(text.encode('utf-8'))


def insert_after(text, anchor, block, path):
    lines = text.split('\n')
    hits = [i for i, l in enumerate(lines) if l == anchor]
    if len(hits) != 1:
        raise SystemExit('anchor %r: %d hits in %s' % (anchor, len(hits), path))
    i = hits[0]
    return '\n'.join(lines[:i + 1] + block.split('\n') + lines[i + 1:])


def insert_before(text, anchor, block, path):
    lines = text.split('\n')
    hits = [i for i, l in enumerate(lines) if l == anchor]
    if len(hits) != 1:
        raise SystemExit('anchor %r: %d hits in %s' % (anchor, len(hits), path))
    i = hits[0]
    return '\n'.join(lines[:i] + block.split('\n') + lines[i:])


def replace_block(text, old, new, path):
    if text.count(old) != 1:
        raise SystemExit('block: %d hits in %s' % (text.count(old), path))
    return text.replace(old, new)


# ---------------------------------------------------------------- subsystems.h
p = WT + '/src/common/subsystems.h'
t, c = load(p)
t = insert_after(t, '#include <vector>', '#include <cstddef>', p)
t = insert_after(t, 'namespace Common {', r'''
// Track F, F33a (HPP-736; ROADMAP s122 item 673(z)(1)) stand KYTY_TEST_EXITFATAL - test binary only, NOT in main: an
// observer of EmergencyShutdown; nullptr (always, unless the stand set it) - never called. event 0 - walk begin
// (size = m_active.size()), 1 - before the entry <index> (counted from the end), 4 - right before that entry's emergency
// callback, 2 - after the loop, before clear (index = entries walked), 3 - after clear.
using EmergencyWalkHook = void (*)(int event, size_t index, size_t size);
inline EmergencyWalkHook g_emergency_walk_hook = nullptr;''', p)
save(p, t, c)

# ---------------------------------------------------------------- subsystems.cpp
p = WT + '/src/common/subsystems.cpp'
t, c = load(p)
old = r'''void Subsystems::EmergencyShutdown() {
	for (auto it = m_active.rbegin(); it != m_active.rend(); ++it) {
		if (it->emergency_shutdown != nullptr) {
			it->emergency_shutdown();
		}
	}
	m_active.clear();
}'''
new = r'''void Subsystems::EmergencyShutdown() {
	// F33a stand (KYTY_TEST_EXITFATAL, test binary only): the hook is read once; nullptr - the loop is the FS11 loop.
	const auto hook = g_emergency_walk_hook;
	if (hook != nullptr) {
		hook(0, 0, m_active.size());
	}
	size_t pos = 0;
	for (auto it = m_active.rbegin(); it != m_active.rend(); ++it, ++pos) {
		if (hook != nullptr) {
			hook(1, pos, 0);
		}
		if (it->emergency_shutdown != nullptr) {
			if (hook != nullptr) {
				hook(4, pos, 0);
			}
			it->emergency_shutdown();
		}
	}
	if (hook != nullptr) {
		hook(2, pos, 0);
	}
	m_active.clear();
	if (hook != nullptr) {
		hook(3, pos, 0);
	}
}'''
t = replace_block(t, old, new, p)
save(p, t, c)

# ---------------------------------------------------------------- emulator.cpp
p = WT + '/src/emulator.cpp'
t, c = load(p)
t = insert_before(t, '#include <cstdlib>', '#include <atomic>', p)
t = insert_after(t, 'namespace Emulator {', r'''
// Track F, F33a (HPP-736; ROADMAP s122 item 673(z)(1)): stand KYTY_TEST_EXITFATAL=<arm>:<seed> - test binary only, NOT in
// main; off when unset. The process runs the real Init (the Graphics lifecycle is replaced by an entry with the same null
// emergency callback - no window, no GPU), the real at_quick_exit registration and the mounts of Run, loads no ELF and
// runs no guest code. One injector thread (Common::Thread, as guest_thread of Execute) raises a fatal with EXIT_IF - the
// path of a guest fatal: DbgReport -> Log::WriteFatal -> EmergencyShutdownActive -> EXIT_HALT -> DbgExit(321).
//   P - the main thread ends the process by std::quick_exit(0) (the exit of Execute); right before position
//       pos = seed % 13 of its emergency walk (0..11 - the entries counted from the end, 12 - after the loop, before
//       clear) it releases the injector and waits <= 2 s for the injector's own walk to begin, then continues;
//   R - as P without the wait;
//   C - control: no exit on the main thread, the injector raises the fatal 50 ms after the start (one walk expected);
//   N - control: std::quick_exit(0) without a fatal (one walk expected).
// Every event is one stderr line "ExitFatal: ..." (fwrite + fflush). The observer is Common::g_emergency_walk_hook of
// common/subsystems.h (nullptr while the stand is off).
namespace ExitFatalStand {

enum class Arm { Off, P, R, C, N };

static constexpr size_t kPositions = 13;

static Arm               g_arm  = Arm::Off;
static uint32_t          g_seed = 0;
static size_t            g_pos  = 0;
static std::atomic<bool> g_go {false};
static std::atomic<bool> g_inject {false};
static std::atomic<int>  g_main_walk {0};
static std::atomic<int>  g_main_pos {-1};
static std::atomic<int>  g_guest_walk_begun {0};
static std::atomic<int>  g_walk_seq {0};
static thread_local int  t_seq = 0;
static thread_local int  t_cbs = 0;

static std::chrono::steady_clock::time_point g_t0;

struct GraphicsPlaceholder {
	static constexpr const char* name = "Graphics (KYTY_TEST_EXITFATAL placeholder: no window, no GPU)";
	static void initialize() {}
	static void shutdown() {}
};

static uint64_t NowUs() {
	return static_cast<uint64_t>(
	    std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - g_t0).count());
}

static void Line(const std::string& text) {
	std::fwrite(text.data(), 1, text.size(), stderr);
	std::fflush(stderr);
}

static const char* Role() {
	return Common::Thread::IsMainThread() ? "main" : "guest";
}

static const char* ArmName() {
	switch (g_arm) {
		case Arm::P: return "P";
		case Arm::R: return "R";
		case Arm::C: return "C";
		case Arm::N: return "N";
		default: return "off";
	}
}

static void Parse() {
	const char* value = std::getenv("KYTY_TEST_EXITFATAL");
	if (value == nullptr || value[0] == '\0') {
		return;
	}
	char     arm  = 0;
	unsigned seed = 0;
	if (std::sscanf(value, "%c:%u", &arm, &seed) != 2 || (arm != 'P' && arm != 'R' && arm != 'C' && arm != 'N')) {
		std::fprintf(stderr, "KYTY_TEST_EXITFATAL: bad value '%s' (<P|R|C|N>:<seed>), stand off\n", value);
		return;
	}
	g_arm  = (arm == 'P' ? Arm::P : arm == 'R' ? Arm::R : arm == 'C' ? Arm::C : Arm::N);
	g_seed = seed;
	g_pos  = seed % kPositions;
	g_t0   = std::chrono::steady_clock::now();
}

// On the main thread, inside its walk: release the injector; P - wait <= 2 s for the injector's walk to begin.
static void Trigger(size_t pos) {
	g_go.store(true);
	const auto t_trig = NowUs();
	uint64_t   waited = 0;
	if (g_arm == Arm::P) {
		while (g_guest_walk_begun.load() == 0 && NowUs() - t_trig < 2000000u) {
			std::this_thread::yield();
		}
		waited = NowUs() - t_trig;
	}
	Line(fmt::format("ExitFatal: trigger pos={} waited_us={} guest_walk_begun={} t_us={}\n", pos, waited,
	                 g_guest_walk_begun.load(), NowUs()));
}

static void Hook(int event, size_t index, size_t size) {
	const bool main = Common::Thread::IsMainThread();
	switch (event) {
		case 0: {
			t_seq                = g_walk_seq.fetch_add(1) + 1;
			t_cbs                = 0;
			const int main_walk  = g_main_walk.load();
			if (main) {
				g_main_walk.store(1);
			} else {
				g_guest_walk_begun.store(1);
			}
			Line(fmt::format("ExitFatal: walk_begin seq={} role={} size={} main_walk={} main_pos={} in_window={} t_us={}\n",
			                 t_seq, Role(), size, main_walk, g_main_pos.load(), (!main && main_walk == 1) ? 1 : 0,
			                 NowUs()));
			break;
		}
		case 1:
			if (main) {
				g_main_pos.store(static_cast<int>(index));
				if ((g_arm == Arm::P || g_arm == Arm::R) && index == g_pos && !g_go.load()) {
					Trigger(index);
				}
			}
			break;
		case 4:
			t_cbs++;
			Line(fmt::format("ExitFatal: cb seq={} role={} pos={} t_us={}\n", t_seq, Role(), index, NowUs()));
			break;
		case 2:
			if (main) {
				g_main_pos.store(static_cast<int>(kPositions - 1));
				if ((g_arm == Arm::P || g_arm == Arm::R) && g_pos == kPositions - 1 && !g_go.load()) {
					Trigger(index);
				}
			}
			break;
		case 3:
			Line(fmt::format("ExitFatal: walk_end seq={} role={} callbacks={} t_us={}\n", t_seq, Role(), t_cbs, NowUs()));
			if (main) {
				g_main_walk.store(0);
			}
			break;
		default: break;
	}
}

static void Injector(void* /*arg*/) {
	if (g_arm == Arm::C) {
		Common::Thread::Sleep(50);
	} else {
		while (!g_go.load()) {
			std::this_thread::yield();
		}
	}
	Line(fmt::format("ExitFatal: inject role={} main_walk={} main_pos={} t_us={}\n", Role(), g_main_walk.load(),
	                 g_main_pos.load(), NowUs()));
	g_inject.store(true);
	EXIT_IF(g_inject.load());
	Line("ExitFatal: inject returned\n");
}

[[noreturn]] static void Run() {
	Common::g_emergency_walk_hook = Hook;
	Line(fmt::format("ExitFatal: config arm={} seed={} pos={} positions={} t_us={}\n", ArmName(), g_seed, g_pos,
	                 kPositions, NowUs()));
	LOGF("ExitFatal: config arm=%s seed=%u pos=%u\n", ArmName(), g_seed, static_cast<unsigned>(g_pos));
	auto* injector = new Common::Thread(Injector, nullptr); // never joined or destroyed - as guest_thread under quick_exit
	(void)injector;
	if (g_arm == Arm::C) {
		for (;;) {
			Common::Thread::Sleep(1000);
		}
	}
	Common::Thread::Sleep(50);
	Line(fmt::format("ExitFatal: quick_exit t_us={}\n", NowUs()));
	std::quick_exit(0);
}

} // namespace ExitFatalStand''', p)
old = '\tsubsystems.Initialize<Libs::Graphics::Lifecycle>();'
new = r'''	if (ExitFatalStand::g_arm == ExitFatalStand::Arm::Off) {
		subsystems.Initialize<Libs::Graphics::Lifecycle>();
	} else {
		subsystems.Initialize<ExitFatalStand::GraphicsPlaceholder>();
	}'''
t = replace_block(t, old, new, p)
t = insert_before(t, '\tCommon::Subsystems subsystems(true);', '\tExitFatalStand::Parse();', p)
t = insert_after(t, '\tMountSandboxDirs();', r'''
	if (ExitFatalStand::g_arm != ExitFatalStand::Arm::Off) {
		ExitFatalStand::Run();
	}''', p)
save(p, t, c)
print('PATCH OK')
