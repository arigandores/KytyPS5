# F40a2 (HPP-785): map of the report links <commit>:<path>:<line> - copy of the F40a refs_f40a.py with its own table.
# Every link has an anchor (substring of the line) and a +1 control (start of the next line). build: resolve lines from
# anchors (first match after the 'after' anchor, if any) and write the .tsv; check: re-read every link from git and
# compare; text: every <commit>:<path>:<line> of the report (and the short ':<line>' after it) is in the table.
# Emulator: KytyPS5 main 57f9e528 (F40a2 code + stand), e3aa4b4d (F40a); SDL2: submodule 3rdparty/SDL2 at 4b69833b.
# Usage: python refs_f40a2.py build <out.tsv> | check <refs.tsv> | text <report.md> <refs.tsv>
import os, re, subprocess, sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
EMU = 'C:/kyty/KytyPS5'
SDL = ('C:/kyty/KytyPS5/3rdparty/SDL2', '4b69833b')
JP = 'src/graphics/presentation/window/joyPump.cpp'
JH = 'src/graphics/presentation/window/joyPump.h'
W = 'src/graphics/presentation/window/window.cpp'
N = '57f9e528'
# key, commit ('sdl' - SDL2 4b69833b), path, anchor, after-anchor (or '')
REFS = [
    ('j_owner_fn', N, JP, 'uint64_t OwnerOfMessageWindow(const wchar_t* cls) {', ''),
    ('j_owner_find', N, JP, 'hwnd = FindWindowExW(HWND_MESSAGE, hwnd, cls, nullptr);', ''),
    ('j_owner_tid', N, JP, 'const DWORD tid = GetWindowThreadProcessId(hwnd, &pid);', ''),
    ('j_owner_pid', N, JP, 'if (pid == self) {', ''),
    ('j_log_fn', N, JP, 'void LogInitOwner(uint64_t main_os_tid) {', ''),
    ('j_cls_hid', N, JP, 'OwnerOfMessageWindow(L"SDL_HIDAPI_DEVICE_DETECTION");', ''),
    ('j_cls_helper', N, JP, 'OwnerOfMessageWindow(L"SDLHelperWindowInputCatcher");', ''),
    ('j_cls_msg', N, JP, 'OwnerOfMessageWindow(L"Message");', ''),
    ('j_pump_tid', N, JP, 'const uint64_t pump   = GetCurrentThreadId();', ''),
    ('j_line', N, JP, 'LOGF("FixF24: init_owner hid=', ''),
    ('j_main_field', N, JP, 'uint64_t                m_main_os_tid = 0;', ''),
    ('j_main_set', N, JP, 'm_main_os_tid = GetCurrentThreadId();', ''),
    ('j_thread_new', N, JP, 'm_thread = std::thread([this, main_tid] { ThreadMain(main_tid); });', ''),
    ('j_init_tid_line', N, JP, 'LOGF("FixF24: init tid=', ''),
    ('j_init', N, JP, 'const bool ok = SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER) == 0;', ''),
    ('j_owner_call', N, JP, 'LogInitOwner(m_main_os_tid);', ''),
    ('j_init_done', N, JP, 'm_init_done = true;', ''),
    ('j_notify', N, JP, 'm_cv.notify_all();', 'm_init_error = SDL_GetError();'),
    ('j_scan_fields', N, JP, 'std::atomic<bool> m_stand_scan_on {false};', ''),
    ('j_mark_call', N, JP, 'StandScanMark(); // F40a2', ''),
    ('j_scan_call', N, JP, 'ScanAndOpen();', 'StandScanMark(); // F40a2'),
    ('j_scan_fn', N, JP, 'void Pump::ScanAndOpen() {', ''),
    ('j_scan_lock', N, JP, 'SDL_LockJoysticks();', 'void Pump::ScanAndOpen() {'),
    ('j_mark_fn', N, JP, 'void Pump::StandScanMark() {', ''),
    ('j_begin', N, JP, 'void StandScanGapBegin() {', ''),
    ('j_end', N, JP, 'uint64_t StandScanGapEnd() {', ''),
    ('j_end_off', N, JP, 'p.m_stand_scan_on.store(false, std::memory_order_relaxed);', ''),
    ('j_delay', N, JP, 'if (delay_us != 0 && NowUs() < m_tasks.front().posted_us + delay_us) {', ''),
    ('h_decl', N, JH, 'void     StandScanGapBegin();', ''),
    ('w_probe_ms', N, W, 'constexpr uint32_t TEST_HIDLOSS_PROBE_MS           = 20;', ''),
    ('w_delay_ms', N, W, 'constexpr uint32_t TEST_HIDLOSS_FLAP_TASK_DELAY_MS = 50;', ''),
    ('w_comment', N, W, '// F40a2 (HPP-785, ROADMAP s122 item 696(b)(2), RC2 of F40b)', ''),
    ('w_detach_field', N, W, 'std::atomic<uint64_t>  flap_detach_us[TEST_HIDLOSS_FLAP_N] {};', ''),
    ('w_gap_field', N, W, 'std::atomic<uint64_t>  jp_scan_gap_max_us {0};', ''),
    ('w_life', N, W, 'uint64_t life_min_us = 0;', ''),
    ('w_life_if', N, W, 'if (attach_us != 0 && detach_us >= attach_us) {', ''),
    ('w_fmt', N, W, '"open_failed=%llu open_lat_max_us=%llu flap_life_min_us=', ''),
    ('w_attach_us', N, W, 'g_test_hidloss2.flap_attach_us[slot].store(TestHidLossNowUs(), std::memory_order_relaxed);', ''),
    ('w_attach_call', N, W, 'const int            index = SDL_JoystickAttachVirtualEx(&desc);', 'static SDL_JoystickID TestHidLossFlapAttach('),
    ('w_detach_fn', N, W, 'static void TestHidLossFlapDetach(uint32_t slot, SDL_JoystickID id) {', ''),
    ('w_detach_lock', N, W, 'SDL_LockJoysticks();', 'static void TestHidLossFlapDetach(uint32_t slot, SDL_JoystickID id) {'),
    ('w_detach_us', N, W, 'const uint64_t detach_us = TestHidLossNowUs(); // F40a2', ''),
    ('w_detach_call', N, W, 'if (SDL_JoystickDetachVirtual(i) == 0 && slot < TEST_HIDLOSS_FLAP_N) {', ''),
    ('w_begin_call', N, W, 'JoyPump::StandScanGapBegin();', ''),
    ('w_attach_step', N, W, 'flap_ids[flap_k] = TestHidLossFlapAttach(flap_k);', ''),
    ('w_detach_step', N, W, 'TestHidLossFlapDetach(flap_k - 2, flap_ids[flap_k - 2]);', ''),
    ('w_end_call', N, W, 'e.jp_scan_gap_max_us.store(JoyPump::StandScanGapEnd()', ''),
    ('w_delay_set', N, W, 'JoyPump::StandTaskDelayMs(TEST_HIDLOSS_FLAP_TASK_DELAY_MS);', ''),
    ('w_initvideo', N, W, 'if (SDL_InitSubSystem(SDL_INIT_VIDEO) < 0) {', ''),
    ('w_main_tid', N, W, 'const auto main_tid = static_cast<uint64_t>(SDL_ThreadID());', ''),
    ('w_start', N, W, 'if (!JoyPump::Start(main_tid, &error)) {', ''),
    # SDL2 4b69833b
    ('sdl_init_helper', 'sdl', 'src/SDL.c', 'if (SDL_HelperWindowCreate() < 0) {', ''),
    ('sdl_init_gc_joy', 'sdl', 'src/SDL.c', 'if (!SDL_PrivateInitOrIncrSubsystem(SDL_INIT_JOYSTICK)) {', ''),
    ('sdl_helper_class', 'sdl', 'src/video/windows/SDL_windowswindow.c', 'static const TCHAR *SDL_HelperWindowClassName = TEXT("SDLHelperWindowInputCatcher");', ''),
    ('sdl_helper_once', 'sdl', 'src/video/windows/SDL_windowswindow.c', 'if (SDL_HelperWindow != NULL) {', ''),
    ('sdl_helper_create', 'sdl', 'src/video/windows/SDL_windowswindow.c', 'SDL_HelperWindow = CreateWindowEx(0, SDL_HelperWindowClassName,', ''),
    ('sdl_helper_parent', 'sdl', 'src/video/windows/SDL_windowswindow.c', 'CW_USEDEFAULT, HWND_MESSAGE, NULL,', 'SDL_HelperWindow = CreateWindowEx(0, SDL_HelperWindowClassName,'),
    ('hid_window', 'sdl', 'src/hidapi/SDL_hidapi.c', 'SDL_HIDAPI_discovery.m_hwndMsg = CreateWindowExA(0, "SDL_HIDAPI_DEVICE_DETECTION"', ''),
    ('win_notif_window', 'sdl', 'src/joystick/windows/SDL_windowsjoystick.c', 'data->messageWindow = CreateWindowEx(0, TEXT("Message"), NULL, 0, 0, 0, 0, 0, HWND_MESSAGE, NULL, NULL, NULL);', ''),
    ('thr_id', 'sdl', 'src/thread/windows/SDL_systhread.c', 'return (SDL_threadID)GetCurrentThreadId();', ''),
]


def root_of(commit):
    return SDL[0] if commit == SDL[1] else EMU


def show(commit, path):
    r = subprocess.run(['git', '-C', root_of(commit), 'show', commit + ':' + path], capture_output=True)
    if r.returncode != 0:
        raise SystemExit('git show failed ' + commit + ' ' + path)
    return r.stdout.decode('utf-8', 'replace').replace(chr(13), '').split(chr(10))


def resolve(lines, anchor, after):
    start = 0
    if after:
        hits = [i for i, l in enumerate(lines) if after in l]
        if not hits:
            return None
        start = hits[0]
    for i in range(start, len(lines)):
        if anchor in lines[i]:
            return i + 1
    return None


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        sys.exit(3)
    mode, path = sys.argv[1], sys.argv[2]
    cache = {}
    rows_in = [(k, SDL[1] if c == 'sdl' else c, p, a, f) for k, c, p, a, f in REFS]
    if mode == 'build':
        rows = []
        for key, commit, p, anchor, after in rows_in:
            lines = cache.setdefault((commit, p), show(commit, p))
            n = resolve(lines, anchor, after)
            if n is None:
                print('NOT FOUND', key)
                sys.exit(1)
            plus1 = lines[n].strip()[:40] if n < len(lines) else ''
            rows.append((key, commit, p, str(n), anchor, plus1))
            print(key, commit + ':' + p + ':' + str(n))
        with open(path, 'w', encoding='utf-8', newline=chr(10)) as o:
            for r in rows:
                o.write(chr(9).join(r) + chr(10))
        print('rows', len(rows))
        return
    if mode == 'text':
        table = set()
        for l in open(sys.argv[3], encoding='utf-8'):
            if l.strip():
                k, c, p, n = l.split(chr(9))[:4]
                table.add((c, p, n))
        commits = sorted(set(c for c, _, _ in table))
        text = open(path, encoding='utf-8').read()
        rx = re.compile(r'`(?:(' + '|'.join(commits) + r'):([^`:]+):|:)(\d+)`')
        last, seen, miss = None, 0, 0
        for m in rx.finditer(text):
            if m.group(1):
                last = (m.group(1), m.group(2))
            if last is None:
                continue
            seen += 1
            if (last[0], last[1], m.group(3)) not in table:
                miss += 1
                print('MISSING', last[0] + ':' + last[1] + ':' + m.group(3))
        print('text links', seen, 'missing', miss)
        print('ALL OK' if miss == 0 and seen > 0 else 'FAIL')
        return
    bad = 0
    rows = [l.rstrip(chr(10)).split(chr(9)) for l in open(path, encoding='utf-8') if l.strip()]
    for key, commit, p, n, anchor, plus1 in rows:
        lines = cache.setdefault((commit, p), show(commit, p))
        i = int(n)
        ok = anchor in lines[i - 1] and (plus1 == '' or (i < len(lines) and lines[i].strip().startswith(plus1)))
        if not ok:
            bad += 1
            print('BAD', key, commit, p, n)
    print('links', len(rows), 'bad', bad)
    print('ALL OK' if bad == 0 and len(rows) == len(rows_in) else 'FAIL')


if __name__ == '__main__':
    main()
