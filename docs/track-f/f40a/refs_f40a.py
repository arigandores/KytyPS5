# F40a (HPP-770): map of the report links <commit>:<path>:<line> - copy of the F39a refs_f39a.py with its own table.
# Every link has an anchor (substring of the line) and a +1 control (start of the next line). build: resolve lines from
# anchors (first match after the 'after' anchor, if any) and write the .tsv; check: re-read every link from git and
# compare; text: every <commit>:<path>:<line> of the report (and the short ':<line>' after it) is in the table.
# Emulator: KytyPS5 FS12 730ed40a (and the F40a commits, key prefix 'f'); SDL2: submodule 3rdparty/SDL2 at 4b69833b.
# Usage: python refs_f40a.py build <out.tsv> | check <refs.tsv> | text <report.md> <refs.tsv>
import os, re, subprocess, sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
REPO = {'emu': ('C:/kyty/KytyPS5', '730ed40a'), 'sdl': ('C:/kyty/KytyPS5/3rdparty/SDL2', '4b69833b')}
W = 'src/graphics/presentation/window/window.cpp'
C = 'src/libs/controller.cpp'
H = 'src/graphics/presentation/window/hostInput.cpp'
E = 'src/events/SDL_events.c'
J = 'src/joystick/SDL_joystick.c'
V = 'src/joystick/virtual/SDL_virtualjoystick.c'
WJ = 'src/joystick/windows/SDL_windowsjoystick.c'
# key, repo, path, anchor, after-anchor (or '')
REFS = [
    # emulator FS12 730ed40a
    ('w_hint_rumble', 'emu', W, 'SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI_PS4_RUMBLE, "1");', ''),
    ('w_init', 'emu', W, 'if (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {', ''),
    ('w_hostinit', 'emu', W, 'HostInputInit();', 'if (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {'),
    ('w_add_open', 'emu', W, 'auto* pad = SDL_GameControllerOpen(f.id);', ''),
    ('w_add_exit', 'emu', W, 'EXIT_NOT_IMPLEMENTED(pad == nullptr);', 'auto* pad = SDL_GameControllerOpen(f.id);'),
    ('w_add_connect', 'emu', W, 'Controller::Connect(id);', 'auto* pad = SDL_GameControllerOpen(f.id);'),
    ('w_removed_log', 'emu', W, 'LOGF("Controller %d: removed', ''),
    ('w_removed_disc', 'emu', W, 'Controller::Disconnect(f.id);', ''),
    ('w_removed_close', 'emu', W, 'SDL_GameControllerClose(SDL_GameControllerFromInstanceID(f.id));', ''),
    ('w_run_wait', 'emu', W, 'if (!HostInputWaitEvent(&loop.event)) {', ''),
    ('w_prep_poll', 'emu', W, 'while (SDL_PollEvent(&g_window->loop.event)) {', ''),
    ('w_prep_process', 'emu', W, 'g_window->ProcessEvent(0);', ''),
    ('w_shutdown_em', 'emu', W, 'Controller::EmergencyShutdown();', 'void WindowShutdown() {'),
    ('w_attach_virtual', 'emu', W, 'const int index = SDL_JoystickAttachVirtualEx(&desc);', ''),
    ('w_detach_virtual', 'emu', W, 'if (index < 0 || SDL_JoystickDetachVirtual(index) != 0) {', ''),
    ('w_hold_lock', 'emu', W, 'SDL_LockJoysticks();', 'case TestHidLossMode::Hold:'),
    ('w_title_post', 'emu', W, 'PostToMainThread([this] {', 'if (title_async) {'),
    ('h_wait', 'emu', H, 'if (SDL_WaitEvent(event) == 0) {', ''),
    ('h_wait_to', 'emu', H, 'if (SDL_WaitEventTimeout(event, timeout_ms) != 0) {', ''),
    ('h_mouse_exit', 'emu', H, 'EXIT("%s\\n", SDL_GetError());', 'if (SDL_WaitEventTimeout(event, timeout_ms) != 0) {'),
    ('c_po_start', 'emu', C, 'g_pad_output->Start();', ''),
    ('c_haptics_start', 'emu', C, 'g_haptics->Start();', ''),
    ('c_po_apply_lock', 'emu', C, 'SDL_LockJoysticks();', 'void PadOutput::ApplyVibration('),
    ('c_connect_sdl', 'emu', C, 'auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(id));', 'void GameController::Connect(int id) {'),
    ('c_connect_lock', 'emu', C, 'Common::LockGuard lock(m_mutex);', 'void GameController::Connect(int id) {'),
    ('c_disconnect_lock', 'emu', C, 'Common::LockGuard lock(m_mutex);', 'void GameController::Disconnect(int id) {'),
    ('c_shutdown_delete', 'emu', C, 'delete g_controller;', 'void Shutdown() {'),
    ('c_em_po_stop', 'emu', C, 'g_pad_output->Stop();', 'void EmergencyShutdown() {'),
    ('c_em_release', 'emu', C, 'g_controller->ReleaseHostPads();', 'void EmergencyShutdown() {'),
    ('c_release_lock', 'emu', C, 'Common::LockGuard lock(m_mutex);', 'void GameController::ReleaseHostPads() {'),
    ('c_release_close', 'emu', C, 'SDL_GameControllerClose(pad);', 'SDL_Delay(RELEASE_FLUSH_MS);'),
    ('c_setvib_lock', 'emu', C, 'Common::LockGuard lock(m_mutex);', 'void GameController::SetVibration('),
    ('c_setvib_sdl', 'emu', C, 'if (SDL_GameControllerRumble(pad, large, small, RUMBLE_DURATION_MS) != 0) {', 'void GameController::SetVibration('),
    ('vw_quit', 'emu', 'src/graphics/presentation/window/vulkanWindow.cpp', 'SDL_QuitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER);', ''),
    ('e_init_controller', 'emu', 'src/emulator.cpp', 'subsystems.Initialize<Libs::Controller::Lifecycle>();', ''),
    ('e_init_graphics', 'emu', 'src/emulator.cpp', 'subsystems.Initialize<Libs::Graphics::Lifecycle>();', ''),
    ('e_run_quick', 'emu', 'src/emulator.cpp', 'std::quick_exit(0);', 'Libs::Graphics::WindowRun();'),
    ('e_at_quick', 'emu', 'src/emulator.cpp', 'ok = at_quick_exit(Common::Subsystems::EmergencyShutdownActive);', ''),
    ('agc_window_shutdown', 'emu', 'src/libs/agc.cpp', 'WindowShutdown();', ''),
    ('agc_lifecycle', 'emu', 'src/libs/agc.h', 'static constexpr auto        shutdown   = Libs::Graphics::Shutdown;', ''),
    ('sub_em_loop', 'emu', 'src/common/subsystems.cpp', 'it->emergency_shutdown();', 'void Subsystems::EmergencyShutdown() {'),
    # SDL2 4b69833b
    ('sdl_refcount', 'sdl', 'src/SDL.c', 'static Uint8 SDL_SubsystemRefCount[32];', ''),
    ('sdl_init_helper', 'sdl', 'src/SDL.c', 'if (SDL_HelperWindowCreate() < 0) {', ''),
    ('sdl_init_video', 'sdl', 'src/SDL.c', 'if (SDL_VideoInit(NULL) < 0) {', ''),
    ('sdl_init_joy', 'sdl', 'src/SDL.c', 'if (SDL_JoystickInit() < 0) {', ''),
    ('sdl_init_gc_joy', 'sdl', 'src/SDL.c', 'if (!SDL_PrivateInitOrIncrSubsystem(SDL_INIT_JOYSTICK)) {', ''),
    ('sdl_init_gc', 'sdl', 'src/SDL.c', 'if (SDL_GameControllerInit() < 0) {', ''),
    ('sdl_helper_create', 'sdl', 'src/video/windows/SDL_windowswindow.c', 'SDL_HelperWindow = CreateWindowEx(0, SDL_HelperWindowClassName,', ''),
    ('j_drivers', 'sdl', J, 'static SDL_JoystickDriver *SDL_joystick_drivers[] = {', ''),
    ('j_init_events', 'sdl', J, 'if (SDL_InitSubSystem(SDL_INIT_EVENTS) < 0) {', 'int SDL_JoystickInit(void)'),
    ('j_init_drivers', 'sdl', J, 'if (SDL_joystick_drivers[i]->Init() >= 0) {', ''),
    ('j_open_lock', 'sdl', J, 'SDL_LockJoysticks();', 'SDL_Joystick *SDL_JoystickOpen(int device_index)'),
    ('j_open_update', 'sdl', J, 'driver->Update(joystick);', 'SDL_PrivateJoystickBatteryLevel(joystick, initial_power_level);'),
    ('j_rumble_driver', 'sdl', J, 'retval = joystick->driver->Rumble(joystick, low_frequency_rumble, high_frequency_rumble);', ''),
    ('j_close_rumble', 'sdl', J, 'SDL_JoystickRumble(joystick, 0, 0, 0);', 'if (--joystick->ref_count > 0) {'),
    ('j_close_driver', 'sdl', J, 'joystick->driver->Close(joystick);', ''),
    ('j_ignore', 'sdl', J, 'if (SDL_HasWindows() && SDL_GetKeyboardFocus() == NULL) {', ''),
    ('j_removed_attached', 'sdl', J, 'joystick->attached = SDL_FALSE;', 'void SDL_PrivateJoystickRemoved('),
    ('j_removed_fix', 'sdl', J, 'UpdateEventsForDeviceRemoval(device_index, SDL_CONTROLLERDEVICEADDED);', ''),
    ('j_button_ignore', 'sdl', J, 'if (SDL_PrivateJoystickShouldIgnoreEvent()) {', 'int SDL_PrivateJoystickButton('),
    ('j_update_lock', 'sdl', J, 'SDL_LockJoysticks();', 'void SDL_JoystickUpdate(void)'),
    ('j_update_skip', 'sdl', J, 'if (!joystick->attached) {', 'void SDL_JoystickUpdate(void)'),
    ('j_update_driver', 'sdl', J, 'joystick->driver->Update(joystick);', 'void SDL_JoystickUpdate(void)'),
    ('j_update_expire', 'sdl', J, 'SDL_JoystickRumble(joystick, 0, 0, 0);', 'void SDL_JoystickUpdate(void)'),
    ('j_update_detect', 'sdl', J, 'SDL_joystick_drivers[i]->Detect();', 'void SDL_JoystickUpdate(void)'),
    ('v_append', 'sdl', V, 'last->next = hwdata;', ''),
    ('v_detach_free', 'sdl', V, 'VIRTUAL_FreeHWData(hwdata);', 'int SDL_JoystickDetachVirtualInner(int device_index)'),
    ('v_free_null', 'sdl', V, 'hwdata->joystick->hwdata = NULL;', ''),
    ('v_button_inner', 'sdl', V, 'hwdata->buttons[button] = value;', ''),
    ('v_rumble_check', 'sdl', V, 'if (joystick->hwdata) {', 'static int VIRTUAL_JoystickRumble('),
    ('v_rumble_err', 'sdl', V, 'result = SDL_SetError("Rumble failed, device disconnected");', ''),
    ('v_update_cb', 'sdl', V, 'hwdata->desc.Update(hwdata->desc.userdata);', ''),
    ('v_close', 'sdl', V, 'hwdata->joystick = NULL;', 'static void VIRTUAL_JoystickClose('),
    ('gc_watch_added', 'sdl', 'src/joystick/SDL_gamecontroller.c', 'if (SDL_IsGameController(event->jdevice.which)) {', ''),
    ('gc_watch', 'sdl', 'src/joystick/SDL_gamecontroller.c', 'SDL_AddEventWatch(SDL_GameControllerEventWatcher, NULL);', ''),
    ('gc_init_push', 'sdl', 'src/joystick/SDL_gamecontroller.c', 'deviceevent.cdevice.which = i;', 'int SDL_GameControllerInit(void)'),
    ('ev_calc', 'sdl', E, 'static void SDL_CalculateShouldUpdateJoysticks(SDL_bool hint_value)', ''),
    ('ev_push_wake', 'sdl', E, 'SDL_SendWakeupEvent();', 'if (used > 0 && action == SDL_ADDEVENT) {'),
    ('ev_wake_take', 'sdl', E, 'wakeup_window = (SDL_Window *)SDL_AtomicSetPtr(&_this->wakeup_window, NULL);', ''),
    ('ev_update', 'sdl', E, 'if (SDL_update_joysticks) {', ''),
    ('ev_poll_cond', 'sdl', E, 'if (SDL_WasInit(SDL_INIT_JOYSTICK) && SDL_update_joysticks) {', ''),
    ('ev_poll_1ms', 'sdl', E, 'poll_interval = SDL_min(poll_interval, EVENT_POLL_INTERVAL_MS);', ''),
    ('ev_poll_3s', 'sdl', E, 'poll_interval = SDL_min(poll_interval, ENUMERATION_POLL_INTERVAL_MS);', ''),
    ('ev_peep', 'sdl', E, 'status = SDL_PeepEvents(event, 1, SDL_GETEVENT, SDL_FIRSTEVENT, SDL_LASTEVENT);', 'static int SDL_WaitEventTimeout_Device('),
    ('ev_loop_timeout', 'sdl', E, 'loop_timeout = SDL_min(loop_timeout, poll_interval);', ''),
    ('ev_publish', 'sdl', E, 'SDL_AtomicSetPtr(&_this->wakeup_window, wakeup_window);', ''),
    ('ev_wait_device', 'sdl', E, 'status = _this->WaitEventTimeout(_this, loop_timeout);', ''),
    ('ev_hint_cb', 'sdl', E, 'SDL_AddHintCallback(SDL_HINT_AUTO_UPDATE_JOYSTICKS, SDL_AutoUpdateJoysticksChanged, NULL);', ''),
    ('we_msgwait', 'sdl', 'src/video/windows/SDL_windowsevents.c', 'ret = MsgWaitForMultipleObjects(0, NULL, FALSE, dwMilliseconds, QS_ALLINPUT);', ''),
    ('we_post', 'sdl', 'src/video/windows/SDL_windowsevents.c', 'PostMessage(data->hwnd, data->videodata->_SDL_WAKEUP, 0, 0);', ''),
    ('we_peek', 'sdl', 'src/video/windows/SDL_windowsevents.c', 'while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {', 'void WIN_PumpEvents(_THIS)'),
    ('hid_thread', 'sdl', 'src/hidapi/SDL_hidapi.c', 'SDL_HIDAPI_discovery.m_nThreadID = SDL_ThreadID();', ''),
    ('hid_window', 'sdl', 'src/hidapi/SDL_hidapi.c', 'SDL_HIDAPI_discovery.m_hwndMsg = CreateWindowExA(0, "SDL_HIDAPI_DEVICE_DETECTION"', ''),
    ('hid_if0', 'sdl', 'src/hidapi/SDL_hidapi.c', '#if 0 /* just let the usual SDL_PumpEvents loop dispatch these', ''),
    ('win_init_xinput', 'sdl', WJ, 'if (SDL_XINPUT_JoystickInit() < 0) {', ''),
    ('win_init_dinput', 'sdl', WJ, 'if (SDL_DINPUT_JoystickInit() < 0) {', 'static int WINDOWS_JoystickInit(void)'),
    ('win_thread_hint', 'sdl', WJ, 's_bJoystickThread = SDL_GetHintBoolean(SDL_HINT_JOYSTICK_THREAD, SDL_FALSE);', ''),
    ('win_notif_coinit', 'sdl', WJ, 'data->coinitialized = WIN_CoInitialize();', ''),
    ('win_notif_window', 'sdl', WJ, 'data->messageWindow = CreateWindowEx(0, TEXT("Message"), NULL, 0, 0, 0, 0, 0, HWND_MESSAGE, NULL, NULL, NULL);', ''),
    ('win_timer', 'sdl', WJ, 'SetTimer(hwnd, IDT_SDL_DEVICE_CHANGE_TIMER_1, 300, NULL);', ''),
    ('win_thread_getmsg', 'sdl', WJ, 'lastret = GetMessage(&msg, NULL, 0, 0); /* WM_QUIT causes return value of 0 */', ''),
    ('di_coinit', 'sdl', 'src/joystick/windows/SDL_dinputjoystick.c', 'result = WIN_CoInitialize();', 'int SDL_DINPUT_JoystickInit(void)'),
    ('di_create', 'sdl', 'src/joystick/windows/SDL_dinputjoystick.c', 'result = CoCreateInstance(&CLSID_DirectInput8, NULL, CLSCTX_INPROC_SERVER,', ''),
    ('di_coop', 'sdl', 'src/joystick/windows/SDL_dinputjoystick.c', 'IDirectInputDevice8_SetCooperativeLevel(joystick->hwdata->InputDevice, SDL_HelperWindow,', ''),
    ('wgi_ro', 'sdl', 'src/joystick/windows/SDL_windows_gaming_input.c', 'if (FAILED(WIN_RoInitialize())) {', ''),
    ('win_ro_sta', 'sdl', 'src/core/windows/SDL_windows.c', 'HRESULT hr = RoInitializeFunc(RO_INIT_SINGLETHREADED);', ''),
    ('kb_ime_coinit', 'sdl', 'src/video/windows/SDL_windowskeyboard.c', 'if (SUCCEEDED(WIN_CoInitialize())) {', ''),
]
EXTRA = []  # (key, commit, path, anchor, after) of the F40a commits - filled in the report sections after the code


def show(root, commit, path):
    r = subprocess.run(['git', '-C', root, 'show', commit + ':' + path], capture_output=True)
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
    rows_in = [(k, REPO[r][0], REPO[r][1], p, a, f) for k, r, p, a, f in REFS] + \
              [(k, REPO['emu'][0], c, p, a, f) for k, c, p, a, f in EXTRA]
    if mode == 'build':
        rows = []
        for key, root, commit, p, anchor, after in rows_in:
            lines = cache.setdefault((commit, p), show(root, commit, p))
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
    roots = {REPO['sdl'][1]: REPO['sdl'][0]}
    for key, commit, p, n, anchor, plus1 in rows:
        root = roots.get(commit, REPO['emu'][0])
        lines = cache.setdefault((commit, p), show(root, commit, p))
        i = int(n)
        ok = anchor in lines[i - 1] and (plus1 == '' or (i < len(lines) and lines[i].strip().startswith(plus1)))
        if not ok:
            bad += 1
            print('BAD', key, commit, p, n)
    print('links', len(rows), 'bad', bad)
    print('ALL OK' if bad == 0 and len(rows) == len(rows_in) else 'FAIL')


if __name__ == '__main__':
    main()
