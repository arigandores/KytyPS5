# F40a2 (HPP-785, ROADMAP s122 item 696(b)(1), (b)(2), (b)(4)): RC1 of F40b - the line "FixF24: init_owner" (OS owner
# threads of the SDL joystick windows of this process, =1 only, after a successful init on JoyPump); RC2 of F40b - stand
# edition 2, flap arm: flap_life_min_us / flap_life_max_us (detach - attach per slot) and jp_scan_gap_max_us (the longest
# stretch from just before the first attach to just after the last detach without a ScanAndOpen start of JoyPump).
# Whole-line anchors, each exactly once; CRLF-aware (strips \r, writes the file's own EOL back), bytes written by
# write_bytes. The anchors of mut_f40b.py (F40b) are not touched. Usage: python patch_f40a2.py <tree root>
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
JP = 'src/graphics/presentation/window/joyPump.cpp'
JH = 'src/graphics/presentation/window/joyPump.h'
WN = 'src/graphics/presentation/window/window.cpp'

OWNER_FN = r'''#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
// F40a2 (RC1 of F40b, ROADMAP s122 item 696(b)(1)): the OS thread that owns the first message-only window of class cls
// of this process (FindWindowExW(HWND_MESSAGE) by class, GetWindowThreadProcessId, own process id only - any process on
// SDL2 has windows of the same classes); 0 - none found.
uint64_t OwnerOfMessageWindow(const wchar_t* cls) {
	const DWORD self = GetCurrentProcessId();
	HWND        hwnd = nullptr;
	for (int i = 0; i < 4096; i++) {
		hwnd = FindWindowExW(HWND_MESSAGE, hwnd, cls, nullptr);
		if (hwnd == nullptr) {
			return 0;
		}
		DWORD       pid = 0;
		const DWORD tid = GetWindowThreadProcessId(hwnd, &pid);
		if (pid == self) {
			return tid;
		}
	}
	return 0;
}
#endif

// F40a2 (RC1 of F40b): on JoyPump after a successful SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER), before the main thread
// resumes. hid - SDL_HIDAPI_DEVICE_DETECTION (HIDAPI discovery), helper - SDLHelperWindowInputCatcher (SDL helper window,
// DirectInput cooperative level), msg - Message (Windows joystick driver device notification); pump - this thread, main -
// the thread that called Start; all are OS thread ids (GetCurrentThreadId), comparable with the window owners.
void LogInitOwner(uint64_t main_os_tid) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	const uint64_t hid    = OwnerOfMessageWindow(L"SDL_HIDAPI_DEVICE_DETECTION");
	const uint64_t helper = OwnerOfMessageWindow(L"SDLHelperWindowInputCatcher");
	const uint64_t msg    = OwnerOfMessageWindow(L"Message");
	const uint64_t pump   = GetCurrentThreadId();
#else
	const uint64_t hid    = 0;
	const uint64_t helper = 0;
	const uint64_t msg    = 0;
	const uint64_t pump   = 0;
#endif
	LOGF("FixF24: init_owner hid=%" PRIu64 " helper=%" PRIu64 " msg=%" PRIu64 " pump=%" PRIu64 " main=%" PRIu64 "\n", hid,
	     helper, msg, pump, main_os_tid);
}
'''.split('\n')

SCAN_FN = r'''// Stand flap arm (F40a2, RC2 of F40b): a ScanAndOpen start of JoyPump inside [StandScanGapBegin; StandScanGapEnd].
void Pump::StandScanMark() {
	if (!m_stand_scan_on.load(std::memory_order_relaxed)) {
		return;
	}
	const uint64_t now = NowUs();
	std::lock_guard lock(m_stand_scan_mutex);
	if (!m_stand_scan_on.load(std::memory_order_relaxed) || now < m_stand_scan_last_us) {
		return; // the window ended (or restarted) between the load and the lock
	}
	m_stand_scan_gap_max_us = std::max(m_stand_scan_gap_max_us, now - m_stand_scan_last_us);
	m_stand_scan_last_us    = now;
}

'''.split('\n')[:-1]

API_FN = r'''// F40a2 (RC2 of F40b): the stand thread, flap arm. Begin - just before the first attach; End - just after the last
// detach: the longest stretch of the window without a ScanAndOpen start (the edges count: begin to the first start, the
// last start to end). At KYTY_FIX_F24=0 (no JoyPump) both do nothing and End returns 0.
void StandScanGapBegin() {
	if (!Enabled()) {
		return;
	}
	auto&           p = P();
	std::lock_guard lock(p.m_stand_scan_mutex);
	p.m_stand_scan_last_us    = NowUs();
	p.m_stand_scan_gap_max_us = 0;
	p.m_stand_scan_on.store(true, std::memory_order_relaxed);
}

uint64_t StandScanGapEnd() {
	if (!Enabled()) {
		return 0;
	}
	auto&           p = P();
	std::lock_guard lock(p.m_stand_scan_mutex);
	if (!p.m_stand_scan_on.load(std::memory_order_relaxed)) {
		return 0;
	}
	p.m_stand_scan_on.store(false, std::memory_order_relaxed);
	const uint64_t now = NowUs();
	return std::max(p.m_stand_scan_gap_max_us, now > p.m_stand_scan_last_us ? now - p.m_stand_scan_last_us : 0);
}

'''.split('\n')[:-1]

EDITS = {
    JP: [
        ('#include <utility>', 'before', ['#include <algorithm>']),
        ('bool LineAllowed(std::atomic<uint32_t>& counter) {', 'before', OWNER_FN),
        ('\tstd::atomic<uint32_t> m_stand_task_delay_ms {0};', 'after',
         ['\t// Flap arm scan gap (F40a2, RC2 of F40b): m_stand_scan_last_us and m_stand_scan_gap_max_us are guarded by',
          '\t// m_stand_scan_mutex; m_stand_scan_on - one relaxed load per JoyPump scan when the stand is off.',
          '\tstd::atomic<bool> m_stand_scan_on {false};',
          '\tstd::mutex        m_stand_scan_mutex;',
          '\tuint64_t          m_stand_scan_last_us    = 0;',
          '\tuint64_t          m_stand_scan_gap_max_us = 0;',
          '\tvoid              StandScanMark();']),
        ('\tstd::atomic<int>        m_open_pads {0};', 'after',
         ['\tuint64_t                m_main_os_tid = 0; // written by Start before the thread, read by JoyPump']),
        ('\tm_event = CreateEventW(nullptr, FALSE, FALSE, nullptr);', 'after',
         ['\tm_main_os_tid = GetCurrentThreadId(); // F40a2 (RC1 of F40b): the main thread, OS id']),
        ('\tconst bool ok = SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER) == 0;', 'after',
         ['\tif (ok) {',
          '\t\tLogInitOwner(m_main_os_tid); // F40a2 (RC1 of F40b): before the main thread resumes',
          '\t}']),
        ('\t\tScanAndOpen();', 'before', ['\t\tStandScanMark(); // F40a2 (RC2 of F40b): the start of the scan, stand only']),
        ('// JoyPump task posted by the main thread\'s removal handler (Controller::Disconnect is done there).', 'before',
         SCAN_FN),
        ('void StandTaskDelayMs(uint32_t ms) {', 'before', API_FN),
    ],
    JH: [
        ('void StandTaskDelayMs(uint32_t ms);', 'after',
         ['// Flap arm (F40a2, RC2 of F40b): the longest stretch of [Begin; End] without a ScanAndOpen start of JoyPump, us;',
          '// stand thread; no-ops and 0 at KYTY_FIX_F24=0.',
          'void     StandScanGapBegin();',
          'uint64_t StandScanGapEnd();']),
    ],
    WN: [
        ('//    opened - pads whose Update callback ran (SDL_JoystickOpen runs one Update), open_lat_max_us - attach to first Update.',
         'after',
         ['// F40a2 (HPP-785, ROADMAP s122 item 696(b)(2), RC2 of F40b): the line "TestHidLoss: f24" ends with flap_life_min_us,',
          '// flap_life_max_us (detach - attach of the flap slots that were attached and detached; both times taken under the',
          '// joystick lock, attach before SDL_JoystickAttachVirtualEx, detach before SDL_JoystickDetachVirtual) and',
          '// jp_scan_gap_max_us (JoyPump::StandScanGapBegin just before the first attach .. StandScanGapEnd just after the last',
          '// detach: the longest stretch without a ScanAndOpen start of JoyPump; 0 at KYTY_FIX_F24=0); 0 in other modes.']),
        ('\tstd::atomic<uint64_t>  flap_open_us[TEST_HIDLOSS_FLAP_N] {};', 'after',
         ['\tstd::atomic<uint64_t>  flap_detach_us[TEST_HIDLOSS_FLAP_N] {}; // F40a2: 0 - not detached',
          '\tstd::atomic<uint64_t>  jp_scan_gap_max_us {0};                 // F40a2']),
        ('\t\t\topen_lat_max_us = std::max(open_lat_max_us, open_us - e.flap_attach_us[i].load(std::memory_order_relaxed));',
         'after',
         ['\t\t}',
          '\t}',
          '\tuint64_t life_min_us = 0;',
          '\tuint64_t life_max_us = 0;',
          '\tuint64_t life_n      = 0;',
          '\tfor (uint32_t i = 0; i < TEST_HIDLOSS_FLAP_N; i++) {',
          '\t\tconst uint64_t attach_us = e.flap_attach_us[i].load(std::memory_order_relaxed);',
          '\t\tconst uint64_t detach_us = e.flap_detach_us[i].load(std::memory_order_relaxed);',
          '\t\tif (attach_us != 0 && detach_us >= attach_us) {',
          '\t\t\tconst uint64_t life_us = detach_us - attach_us;',
          '\t\t\tlife_min_us             = life_n == 0 ? life_us : std::min(life_min_us, life_us);',
          '\t\t\tlife_max_us             = std::max(life_max_us, life_us);',
          '\t\t\tlife_n++;']),
        ('\t     "open_failed=%llu open_lat_max_us=%llu\\n",', 'replace',
         ['\t     "open_failed=%llu open_lat_max_us=%llu flap_life_min_us=%llu flap_life_max_us=%llu jp_scan_gap_max_us=%llu\\n",']),
        ('\t     u(p99), u(lat_max), u(attached), u(opened), u(jp.open_failed), u(open_lat_max_us));', 'replace',
         ['\t     u(p99), u(lat_max), u(attached), u(opened), u(jp.open_failed), u(open_lat_max_us), u(life_min_us), u(life_max_us),',
          '\t     get(e.jp_scan_gap_max_us));']),
        ('static void TestHidLossFlapDetach(SDL_JoystickID id) {', 'replace',
         ['static void TestHidLossFlapDetach(uint32_t slot, SDL_JoystickID id) {']),
        ('\t\t\t(void)SDL_JoystickDetachVirtual(i);', 'replace',
         ['\t\t\tconst uint64_t detach_us = TestHidLossNowUs(); // F40a2: under the lock, before the detach',
          '\t\t\tif (SDL_JoystickDetachVirtual(i) == 0 && slot < TEST_HIDLOSS_FLAP_N) {',
          '\t\t\t\tg_test_hidloss2.flap_detach_us[slot].store(detach_us, std::memory_order_relaxed);',
          '\t\t\t}']),
        ('\t\t\t\tflap_ids[flap_k] = TestHidLossFlapAttach(flap_k);', 'before',
         ['\t\t\t\tif (flap_k == 0) {',
          '\t\t\t\t\tJoyPump::StandScanGapBegin(); // F40a2 (RC2 of F40b): just before the first attach',
          '\t\t\t\t}']),
        ('\t\t\t\tTestHidLossFlapDetach(flap_ids[flap_k - 2]);', 'replace',
         ['\t\t\t\tTestHidLossFlapDetach(flap_k - 2, flap_ids[flap_k - 2]);']),
        ('\t\t\t\tconst uint64_t done_us = TestHidLossNowUs();', 'before',
         ['\t\t\t\te.jp_scan_gap_max_us.store(JoyPump::StandScanGapEnd(), std::memory_order_relaxed); // F40a2: after the last detach']),
    ],
}


def patch(path, edits):
    p = ROOT / path
    text = p.read_bytes().decode('utf-8')
    crlf = '\r\n' in text
    lines = text.replace('\r\n', '\n').split('\n')
    for anchor, op, new in edits:
        idx = [i for i, l in enumerate(lines) if l == anchor]
        if len(idx) != 1:
            raise SystemExit('ANCHOR %s x%d in %s: %r' % (op, len(idx), path, anchor))
        i = idx[0]
        if op == 'replace':
            lines[i:i + 1] = new
        elif op == 'after':
            lines[i + 1:i + 1] = new
        elif op == 'before':
            lines[i:i] = new
        else:
            raise SystemExit('bad op')
    out = '\n'.join(lines)
    if crlf:
        out = out.replace('\n', '\r\n')
    p.write_bytes(out.encode('utf-8'))
    print('patched', path, len(edits), 'edits')


for f, e in EDITS.items():
    patch(f, e)
print('PATCH OK')
