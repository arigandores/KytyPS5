#!/usr/bin/env python3
# F40b2 (HPP-786, Red Team): copy of the F40b refs_f40b.py with the rows of f40b2-review.md - links
# <commit>:<path>:<line>, anchor (substring of the line) and control +1 (the next line, stripped, starts with NEXT;
# NEXT '' - the next line is blank).
#   python refs_f40b2.py check            - every row
#   python refs_f40b2.py text <review.md> - every link of the text is a row
#   python refs_f40b2.py find <commit> <path> <substring> - line numbers (helper)
import re
import subprocess
import sys

KYTY = 'C:/kyty/KytyPS5'
SDL = 'C:/kyty/KytyPS5/3rdparty/SDL2'
JP = 'src/graphics/presentation/window/joyPump.cpp'
WN = 'src/graphics/presentation/window/window.cpp'
T = '7c38e497'
S = '4b69833b'

ROWS = [
    (T, JP, 38, r'constexpr uint32_t JP_OPEN_MS          = 1;', r'constexpr uint32_t JP_IDLE_MS'),
    (T, JP, 39, r'constexpr uint32_t JP_IDLE_MS          = 250;', r'constexpr uint32_t T_JP_MS'),
    (T, JP, 63, r'uint64_t OwnerOfMessageWindow(const wchar_t* cls) {', r'const DWORD self = GetCurrentProcessId();'),
    (T, JP, 73, r'if (pid == self) {', r'return tid;'),
    (T, JP, 85, r'void LogInitOwner(uint64_t main_os_tid) {', r'#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS'),
    (T, JP, 87, r'OwnerOfMessageWindow(L"SDL_HIDAPI_DEVICE_DETECTION");', r'const uint64_t helper = OwnerOfMessageWindow('),
    (T, JP, 88, r'OwnerOfMessageWindow(L"SDLHelperWindowInputCatcher");', r'const uint64_t msg    = OwnerOfMessageWindow('),
    (T, JP, 89, r'OwnerOfMessageWindow(L"Message");', r'const uint64_t pump   = GetCurrentThreadId();'),
    (T, JP, 184, r'm_main_os_tid = GetCurrentThreadId();', r'#endif'),
    (T, JP, 205, r'const bool ok = SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER) == 0;', r'if (ok) {'),
    (T, JP, 207, r'LogInitOwner(m_main_os_tid);', r'}'),
    (T, JP, 211, r'm_init_done = true;', r'm_init_ok   = ok;'),
    (T, JP, 249, r'StandScanMark();', r'ScanAndOpen();'),
    (T, JP, 254, r'Wait(m_open_pads.load(std::memory_order_relaxed) > 0 ? JP_OPEN_MS : JP_IDLE_MS);', r'}'),
    (T, JP, 393, r'void Pump::StandScanMark() {', r'if (!m_stand_scan_on.load(std::memory_order_relaxed)) {'),
    (T, JP, 399, r'|| now < m_stand_scan_last_us) {', r'return; // the window ended'),
    (T, JP, 473, r'void NoteAddEvent(int index) {', r'if (LineAllowed(g_add_lines)) {'),
    (T, JP, 513, r'void StandScanGapBegin() {', r'if (!Enabled()) {'),
    (T, JP, 524, r'uint64_t StandScanGapEnd() {', r'if (!Enabled()) {'),
    (T, JP, 535, r'now > p.m_stand_scan_last_us ? now - p.m_stand_scan_last_us : 0);', r'}'),
    (T, WN, 392, r'JoyPump::NoteAddEvent(f.id);', r'} else if (f.added) {'),
    (T, WN, 936, r'if (SDL_InitSubSystem(SDL_INIT_VIDEO) < 0) {', r'EXIT('),
    (T, WN, 940, r'if (!JoyPump::Start(main_tid, &error)) {', r'EXIT('),
    (T, WN, 1145, r'constexpr uint32_t TEST_HIDLOSS_PROBE_MS           = 20;', r'constexpr double   TEST_HIDLOSS_PRE2_S'),
    (T, WN, 1155, r'constexpr uint32_t TEST_HIDLOSS_FLAP_TASK_DELAY_MS = 50;', r'constexpr uint32_t TEST_HIDLOSS_RING'),
    (T, WN, 1452, r'if (attach_us != 0 && detach_us >= attach_us) {', r'const uint64_t life_us = detach_us - attach_us;'),
    (T, WN, 1564, r'g_test_hidloss2.flap_attach_us[slot].store(TestHidLossNowUs(), std::memory_order_relaxed);',
     r'const int            index = SDL_JoystickAttachVirtualEx(&desc);'),
    (T, WN, 1583, r'g_test_hidloss2.flap_detach_us[slot].store(detach_us, std::memory_order_relaxed);', r'}'),
    (T, WN, 1605, r'if (!TestHidLossPost([] { TestHidLossAttach(true); })) {', r'return;'),
    (T, WN, 1668, r'JoyPump::StandScanGapBegin();', r'}'),
    (T, WN, 1680, r'e.jp_scan_gap_max_us.store(JoyPump::StandScanGapEnd(), std::memory_order_relaxed);',
     r'const uint64_t done_us = TestHidLossNowUs();'),
    (T, WN, 1729, r'std::this_thread::sleep_for(std::chrono::milliseconds(TEST_HIDLOSS_PROBE_MS));', r'}'),
    (S, 'src/SDL.c', 229, r'if (flags & (SDL_INIT_HAPTIC | SDL_INIT_JOYSTICK)) {', r'if (SDL_HelperWindowCreate() < 0) {'),
    (S, 'src/SDL.c', 335, r'if (!SDL_PrivateInitOrIncrSubsystem(SDL_INIT_JOYSTICK)) {', r'goto quit_and_error;'),
    (S, 'src/joystick/hidapi/SDL_hidapijoystick.c', 625, r'SDL_HIDAPI_change_count = SDL_hid_device_change_count();',
     r'HIDAPI_UpdateDeviceList();'),
    (S, 'src/hidapi/SDL_hidapi.c', 240, r'CreateWindowExA(0, "SDL_HIDAPI_DEVICE_DETECTION"', r''),
    (S, 'src/hidapi/SDL_hidapi.c', 365, r'HIDAPI_InitializeDiscovery();', r'}'),
    (S, 'src/timer/windows/SDL_systimer.c', 54, r'timeBeginPeriod(timer_period);', r'}'),
]


def show(commit, path):
    repo = SDL if commit == S else KYTY
    out = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
    return out.decode('utf-8').replace('\r\n', '\n').split('\n')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if mode == 'find':
        lines = show(sys.argv[2], sys.argv[3])
        for i, l in enumerate(lines, 1):
            if sys.argv[4] in l:
                print(i, l.strip())
        return
    if mode == 'check':
        bad = 0
        cache = {}
        for (c, p, n, anchor, nxt) in ROWS:
            lines = cache.setdefault((c, p), show(c, p))
            here = lines[n - 1] if n - 1 < len(lines) else ''
            after = lines[n].strip() if n < len(lines) else ''
            ok = anchor in here and (after.startswith(nxt) if nxt else after == '')
            if not ok:
                bad += 1
                print('BAD %s:%s:%d here=%r next=%r' % (c, p, n, here.strip(), after))
        print('links %d bad %d' % (len(ROWS), bad))
        print('ALL OK' if bad == 0 else 'FAIL')
        sys.exit(0 if bad == 0 else 1)
    if mode == 'text':
        text = open(sys.argv[2], encoding='utf-8').read()
        known = {'%s:%s:%d' % (c, p, n) for (c, p, n, _a, _x) in ROWS}
        found = re.findall(r'`([0-9a-f]{8}:[A-Za-z0-9_./-]+:[0-9]+)`', text)
        missing = [f for f in found if f not in known]
        for f in missing:
            print('MISSING', f)
        print('text links %d missing %d' % (len(found), len(missing)))
        print('ALL OK' if not missing else 'FAIL')
        sys.exit(0 if not missing else 1)


if __name__ == '__main__':
    main()
