# Track F, F16d2 (HPP-569, ROADMAP s122 item 470(v)(1)-(2), form (a)): the line DiagF5: / DiagF6: from one consistent
# snapshot. The flip tick (PresentThread, videoOut.cpp) only publishes a request; the copy of the counters and the line
# are made by Service() on the GuestGpu thread at the top of the GuestGpu::ThreadRun loop (graphicsRun.cpp), outside
# every window "parent added, children not yet" of the sites. Plus the test site's window hook.
# Usage: python patch_f16d2_src.py <repository root>. Whole-line / whole-block anchors, each must match exactly once;
# CR is stripped before the search and restored when the file had it; files are written with write_bytes.
import sys

ROOT = sys.argv[1].rstrip('/') + '/'
NL = chr(10)


def block(*lines):
    return NL.join(lines) + NL


def patch(path, edits):
    raw = open(ROOT + path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', NL)
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            print('ANCHOR', n, path, repr(old[:90]))
            sys.exit(1)
        text = text.replace(old, new)
    if crlf:
        text = text.replace(NL, '\r\n')
    open(ROOT + path, 'wb').write(text.encode('utf-8'))
    print('patched', path, len(edits), 'edits')


H = 'src/graphics/host_gpu/renderer/diagF5.h'
C = 'src/graphics/host_gpu/renderer/diagF5.cpp'
G = 'src/graphics/guest_gpu/graphicsRun.cpp'
V = 'src/graphics/presentation/videoOut.cpp'

patch(H, [
    (block(
        '// The line "DiagF5: mode=1" / "DiagF6: mode=1" is printed once at device creation; "DiagF5: frame=<n> <name>=<value> ..."',
        '// (all counters) on a flip tick when a counter grew since the last line and >= 2 s passed (item 427(e)).'),
     block(
        '// The line "DiagF5: mode=1" / "DiagF6: mode=1" is printed once at device creation; "DiagF5: frame=<n> <name>=<value> ..."',
        '// (all counters) when a counter grew since the last line and >= 2 s passed (item 427(e)). Track F, F16d2 (HPP-569,',
        '// item 470(v)(1), form (a)): the flip tick (PresentThread) only publishes a request (frame, clock) and reads no counter;',
        '// the counters are copied once and the line is printed by Service() on the GuestGpu thread at the top of the',
        '// GuestGpu::ThreadRun loop, where no window "parent added, children not yet" of a site is open (graphicsRun.cpp) - the',
        '// line is one consistent snapshot.')),
    (block(
        '// The flip tick: prints the line when On(), a counter grew since the last line and >= 2000 ms passed since it (the',
        '// first line: at the first tick with a growth). TickAt takes the clock as an argument (test site); Tick reads it.',
        'bool Tick(uint32_t frame);',
        'bool TickAt(uint32_t frame, uint64_t now_ms);',
        '[[nodiscard]] std::string FormatLine(uint32_t frame);'),
     block(
        '// The flip tick (PresentThread): when On(), publishes the request for a line - the frame and the clock - and reads no',
        '// counter; true when published (a newer request replaces one not served yet). TickAt takes the clock as an argument',
        '// (test site); Tick reads it.',
        'bool Tick(uint32_t frame);',
        'bool TickAt(uint32_t frame, uint64_t now_ms);',
        '// Track F, F16d2: the line. Called on the GuestGpu thread outside every window (GuestGpu::ThreadRun, graphicsRun.cpp):',
        '// takes the pending request, copies all counters once and prints the line from the copy when On(), a counter grew',
        '// since the last line and >= 2000 ms (request clock) passed since it (the first line: at the first request with a',
        '// growth); true when it printed.',
        'bool Service();',
        '[[nodiscard]] std::string FormatLine(uint32_t frame);',
        '// Test site: the number of lines Service printed and the last of them.',
        '[[nodiscard]] uint64_t    Lines();',
        '[[nodiscard]] std::string LastLine();',
        '// Test site only (nullptr in the emulator): called on the site\'s thread right after each counter increment of Add',
        '// (`set` 5) and of DiagF6::NoteDraw (`set` 6) - inside a window of the site.',
        'using WindowHook = void (*)(uint32_t set, uint32_t counter);',
        'void SetWindowHook(WindowHook hook);')),
    (block(
        'bool                      LogMode();',
        'bool                      Tick(uint32_t frame);',
        'bool                      TickAt(uint32_t frame, uint64_t now_ms);',
        '[[nodiscard]] std::string FormatLine(uint32_t frame);'),
     block(
        'bool                      LogMode();',
        'bool                      Tick(uint32_t frame);',
        'bool                      TickAt(uint32_t frame, uint64_t now_ms);',
        'bool                      Service(); // Track F, F16d2: as DiagF5::Service',
        '[[nodiscard]] std::string FormatLine(uint32_t frame);',
        '[[nodiscard]] uint64_t    Lines();',
        '[[nodiscard]] std::string LastLine();')),
])

patch(C, [
    (block(
        '// Track F, F16d (HPP-521): see diagF5.h. Nothing here is reachable with both knobs off except On() (a static read once)',
        '// and the early returns of LogMode / Tick / NoteDraw.'),
     block(
        '// Track F, F16d (HPP-521): see diagF5.h. Nothing here is reachable with both knobs off except On() (a static read once)',
        '// and the early returns of LogMode / Tick / Service / NoteDraw (F16d2: Service is not even called - graphicsRun.cpp).')),
    (block(
        'template <typename CounterEnum>',
        'struct DiagSet {',
        '	static constexpr uint32_t                         N = static_cast<uint32_t>(CounterEnum::Count);',
        '	std::array<std::atomic<uint64_t>, N>              counters {};',
        '	std::atomic<bool>                                 mode_logged {false};',
        '	std::mutex                                        print_mutex;',
        '	uint64_t                                          last_sum   = 0;',
        '	uint64_t                                          last_ms    = 0;',
        '	bool                                              printed    = false;',
        '};'),
     block(
        'template <typename CounterEnum>',
        'struct DiagSet {',
        '	static constexpr uint32_t                         N = static_cast<uint32_t>(CounterEnum::Count);',
        '	std::array<std::atomic<uint64_t>, N>              counters {};',
        '	std::atomic<bool>                                 mode_logged {false};',
        '	// Track F, F16d2: the request of the flip tick (PresentThread -> GuestGpu); the mutex is held only to write or take',
        '	// it, never while the counters are copied - the vblank waits at most for one take.',
        '	std::mutex                                        request_mutex;',
        '	bool                                              has_request   = false;',
        '	uint32_t                                          request_frame = 0;',
        '	uint64_t                                          request_ms    = 0;',
        '	// The state of the line: written only by Service (GuestGpu thread) under print_mutex; read by the test site.',
        '	std::mutex                                        print_mutex;',
        '	uint64_t                                          last_sum   = 0;',
        '	uint64_t                                          last_ms    = 0;',
        '	bool                                              printed    = false;',
        '	uint64_t                                          lines      = 0;',
        '	std::string                                       last_line;',
        '};',
        '',
        '// Track F, F16d2: the test site\'s window hook (nullptr in the emulator; diagF5.h).',
        'DiagF5::WindowHook g_window_hook = nullptr;',
        '',
        'template <typename CounterEnum>',
        'using Snapshot = std::array<uint64_t, DiagSet<CounterEnum>::N>;')),
    (block(
        'template <typename CounterEnum>',
        'std::string FormatSet(const char* tag, DiagSet<CounterEnum>& set, const char* const* names, uint32_t frame) {',
        '	std::string line = fmt::format("{}: frame={}", tag, frame);',
        '	for (uint32_t i = 0; i < DiagSet<CounterEnum>::N; i++) {',
        '		line += fmt::format(" {}={}", names[i], set.counters[i].load(std::memory_order_relaxed));',
        '	}',
        '	return line;',
        '}',
        '',
        '// The flip tick (item 427(e)): a line of all counters when one grew since the last line and >= 2000 ms passed since it.',
        'template <typename CounterEnum>',
        'bool TickSet(bool on, const char* tag, DiagSet<CounterEnum>& set, const char* const* names, uint32_t frame,',
        '             uint64_t now_ms) {',
        '	if (!on) {',
        '		return false;',
        '	}',
        '	std::scoped_lock lock {set.print_mutex};',
        '	uint64_t         sum = 0;',
        '	for (const auto& counter: set.counters) {',
        '		sum += counter.load(std::memory_order_relaxed);',
        '	}',
        '	if (sum == set.last_sum || (set.printed && now_ms - set.last_ms < 2000u)) {',
        '		return false;',
        '	}',
        '	const auto line = FormatSet(tag, set, names, frame);',
        '	LOGF("%s\\n", line.c_str());',
        '	set.last_sum = sum;',
        '	set.last_ms  = now_ms;',
        '	set.printed  = true;',
        '	return true;',
        '}'),
     block(
        '// One copy of all counters (relaxed loads in index order). Track F, F16d2: called only by Service on the GuestGpu',
        '// thread (and by the test site), so it sees exactly the increments of the windows already closed on that thread.',
        'template <typename CounterEnum>',
        'Snapshot<CounterEnum> CopySet(const DiagSet<CounterEnum>& set) {',
        '	Snapshot<CounterEnum> snapshot {};',
        '	for (uint32_t i = 0; i < DiagSet<CounterEnum>::N; i++) {',
        '		snapshot[i] = set.counters[i].load(std::memory_order_relaxed);',
        '	}',
        '	return snapshot;',
        '}',
        '',
        'template <typename CounterEnum>',
        'std::string FormatSet(const char* tag, const Snapshot<CounterEnum>& snapshot, const char* const* names, uint32_t frame) {',
        '	std::string line = fmt::format("{}: frame={}", tag, frame);',
        '	for (uint32_t i = 0; i < DiagSet<CounterEnum>::N; i++) {',
        '		line += fmt::format(" {}={}", names[i], snapshot[i]);',
        '	}',
        '	return line;',
        '}',
        '',
        '// The flip tick (PresentThread; item 470(v)(1), form (a)): publishes the request only - no counter is read here.',
        'template <typename CounterEnum>',
        'bool PublishSet(bool on, DiagSet<CounterEnum>& set, uint32_t frame, uint64_t now_ms) {',
        '	if (!on) {',
        '		return false;',
        '	}',
        '	std::scoped_lock lock {set.request_mutex};',
        '	set.request_frame = frame;',
        '	set.request_ms    = now_ms;',
        '	set.has_request   = true;',
        '	return true;',
        '}',
        '',
        '// The line (item 427(e)) on the GuestGpu thread outside every window: the pending request, one copy of all counters,',
        '// then the condition "a counter grew since the last line and >= 2000 ms passed since it" and the line - both from that',
        '// copy.',
        'template <typename CounterEnum>',
        'bool ServiceSet(bool on, const char* tag, DiagSet<CounterEnum>& set, const char* const* names) {',
        '	if (!on) {',
        '		return false;',
        '	}',
        '	uint32_t frame  = 0;',
        '	uint64_t now_ms = 0;',
        '	{',
        '		std::scoped_lock lock {set.request_mutex};',
        '		if (!set.has_request) {',
        '			return false;',
        '		}',
        '		frame           = set.request_frame;',
        '		now_ms          = set.request_ms;',
        '		set.has_request = false;',
        '	}',
        '	std::scoped_lock lock {set.print_mutex};',
        '	const auto       snapshot = CopySet(set);',
        '	uint64_t         sum      = 0;',
        '	for (const auto value: snapshot) {',
        '		sum += value;',
        '	}',
        '	if (sum == set.last_sum || (set.printed && now_ms - set.last_ms < 2000u)) {',
        '		return false;',
        '	}',
        '	auto line = FormatSet<CounterEnum>(tag, snapshot, names, frame);',
        '	LOGF("%s\\n", line.c_str());',
        '	set.last_sum  = sum;',
        '	set.last_ms   = now_ms;',
        '	set.printed   = true;',
        '	set.last_line = std::move(line);',
        '	set.lines++;',
        '	return true;',
        '}',
        '',
        'template <typename CounterEnum>',
        'uint64_t LinesSet(DiagSet<CounterEnum>& set) {',
        '	std::scoped_lock lock {set.print_mutex};',
        '	return set.lines;',
        '}',
        '',
        'template <typename CounterEnum>',
        'std::string LastLineSet(DiagSet<CounterEnum>& set) {',
        '	std::scoped_lock lock {set.print_mutex};',
        '	return set.last_line;',
        '}')),
    (block(
        'void Add(Counter counter) {',
        '	F5().counters[static_cast<uint32_t>(counter)].fetch_add(1, std::memory_order_relaxed);',
        '}'),
     block(
        'void Add(Counter counter) {',
        '	const auto index = static_cast<uint32_t>(counter);',
        '	F5().counters[index].fetch_add(1, std::memory_order_relaxed);',
        '	if (g_window_hook != nullptr) [[unlikely]] {',
        '		g_window_hook(5, index); // Track F, F16d2: the test site\'s tick inside the window (nullptr in the emulator)',
        '	}',
        '}')),
    (block(
        'bool TickAt(uint32_t frame, uint64_t now_ms) {',
        '	return TickSet(On(), "DiagF5", F5(), F5Names, frame, now_ms);',
        '}',
        '',
        'std::string FormatLine(uint32_t frame) {',
        '	return FormatSet("DiagF5", F5(), F5Names, frame);',
        '}'),
     block(
        'bool TickAt(uint32_t frame, uint64_t now_ms) {',
        '	return PublishSet(On(), F5(), frame, now_ms);',
        '}',
        '',
        'bool Service() {',
        '	return ServiceSet(On(), "DiagF5", F5(), F5Names);',
        '}',
        '',
        'std::string FormatLine(uint32_t frame) {',
        '	return FormatSet<Counter>("DiagF5", CopySet(F5()), F5Names, frame);',
        '}',
        '',
        'uint64_t Lines() {',
        '	return LinesSet(F5());',
        '}',
        '',
        'std::string LastLine() {',
        '	return LastLineSet(F5());',
        '}',
        '',
        'void SetWindowHook(WindowHook hook) {',
        '	g_window_hook = hook;',
        '}')),
    (block(
        'bool TickAt(uint32_t frame, uint64_t now_ms) {',
        '	return TickSet(On(), "DiagF6", F6(), F6Names, frame, now_ms);',
        '}',
        '',
        'std::string FormatLine(uint32_t frame) {',
        '	return FormatSet("DiagF6", F6(), F6Names, frame);',
        '}'),
     block(
        'bool TickAt(uint32_t frame, uint64_t now_ms) {',
        '	return PublishSet(On(), F6(), frame, now_ms);',
        '}',
        '',
        'bool Service() {',
        '	return ServiceSet(On(), "DiagF6", F6(), F6Names);',
        '}',
        '',
        'std::string FormatLine(uint32_t frame) {',
        '	return FormatSet<Counter>("DiagF6", CopySet(F6()), F6Names, frame);',
        '}',
        '',
        'uint64_t Lines() {',
        '	return LinesSet(F6());',
        '}',
        '',
        'std::string LastLine() {',
        '	return LastLineSet(F6());',
        '}')),
    (block(
        '		if (add[i] != 0) {',
        '			set.counters[i].fetch_add(add[i], std::memory_order_relaxed);',
        '		}'),
     block(
        '		if (add[i] != 0) {',
        '			set.counters[i].fetch_add(add[i], std::memory_order_relaxed);',
        '			if (g_window_hook != nullptr) [[unlikely]] {',
        '				g_window_hook(6, i); // Track F, F16d2: the test site\'s tick inside the window (nullptr in the emulator)',
        '			}',
        '		}')),
])

patch(G, [
    (block(
        '#include "graphics/host_gpu/renderer/commandRecorder.h"',
        '#include "graphics/host_gpu/renderer/gpuCheckpoints.h"'),
     block(
        '#include "graphics/host_gpu/renderer/commandRecorder.h"',
        '#include "graphics/host_gpu/renderer/diagF5.h"',
        '#include "graphics/host_gpu/renderer/gpuCheckpoints.h"')),
    (block(
        '	Common::SkipCeil::t_gpu = true;',
        '	Common::SkipCeil::t_w3  = false;',
        '',
        '	for (;;) {',
        '		Submission                   submission;'),
     block(
        '	Common::SkipCeil::t_gpu = true;',
        '	Common::SkipCeil::t_w3  = false;',
        '	// Track F, F16d2 (KYTY_DIAG_F5 / KYTY_DIAG_F6, HPP-569, ROADMAP s122 item 470(v)(1), form (a)): the lines DiagF5: /',
        '	// DiagF6: are copied and printed HERE, at the top of the loop, from the request the flip tick published (videoOut.cpp).',
        '	// No command, submission slice or m4baton range of this thread runs at this point, and every window "parent added,',
        '	// children not yet" of a site opens and closes inside one call of a site function made from the loop body below (or',
        '	// on the relay while this thread is parked in BatonRelayRun) - so the copy is one consistent snapshot. Knobs off: two',
        '	// On() reads once per thread start and one test of a local per iteration; no call, no atomic operation.',
        '	const bool diag_f56 = DiagF5::On() || DiagF6::On();',
        '',
        '	for (;;) {',
        '		if (diag_f56) [[unlikely]] {',
        '			(void)DiagF5::Service();',
        '			(void)DiagF6::Service();',
        '		}',
        '		Submission                   submission;')),
])

patch(V, [
    (block(
        '	// Track F, F16d (KYTY_DIAG_F5 / KYTY_DIAG_F6, item 427(e)): the flip tick - a line on growth, at most every 2 s.'),
     block(
        '	// Track F, F16d (KYTY_DIAG_F5 / KYTY_DIAG_F6, item 427(e)): the flip tick - a line on growth, at most every 2 s.',
        '	// F16d2 (item 470(v)(1), form (a)): the tick only publishes the request; the line is copied and printed on the',
        '	// GuestGpu thread outside every window of the sites (GuestGpu::ThreadRun, graphicsRun.cpp).')),
])
print('ALL OK')
