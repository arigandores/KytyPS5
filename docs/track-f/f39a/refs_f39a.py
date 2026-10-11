# F39a (HPP-767): map of the report links <commit>:<path>:<line> - every link has an anchor (substring of the line) and a
# +1 control (start of the next line). build: resolve lines from anchors (first match after the 'after' anchor, if any)
# and write refs_f39a.tsv; check: re-read every link from git and compare; last line ALL OK.
# Emulator: KytyPS5 FS12 730ed40a; SDL2: submodule 3rdparty/SDL2 at 4b69833b (2.33.0).
# Usage: python refs_f39a.py build <out.tsv> | python refs_f39a.py check <refs.tsv>
import os, subprocess, sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
REPO = {'emu': ('C:/kyty/KytyPS5', '730ed40a'), 'sdl': ('C:/kyty/KytyPS5/3rdparty/SDL2', '4b69833b')}
W = 'src/graphics/presentation/window/window.cpp'
C = 'src/libs/controller.cpp'
H = 'src/graphics/presentation/window/hostInput.cpp'
E = 'src/events/SDL_events.c'
J = 'src/joystick/SDL_joystick.c'
# key, repo, path, anchor, after-anchor (or '')
REFS = [
    ('w_add_open', 'emu', W, 'auto* pad = SDL_GameControllerOpen(f.id);', ''),
    ('w_add_sensor', 'emu', W, 'SDL_GameControllerSetSensorEnabled(pad, sensor, SDL_TRUE) != 0', ''),
    ('w_add_connect', 'emu', W, 'Controller::Connect(id);', 'auto* pad = SDL_GameControllerOpen(f.id);'),
    ('w_removed_log', 'emu', W, 'LOGF("Controller %d: removed', ''),
    ('w_removed_disc', 'emu', W, 'Controller::Disconnect(f.id);', ''),
    ('w_removed_close', 'emu', W, 'SDL_GameControllerClose(SDL_GameControllerFromInstanceID(f.id));', ''),
    ('w_drain', 'emu', W, 'void WindowContext::DrainMainThreadTasks() {', ''),
    ('w_late', 'emu', W, 'LOGF("MainTaskLate: us=', ''),
    ('w_run_drain', 'emu', W, 'DrainMainThreadTasks();', 'void WindowContext::Run() {'),
    ('w_run_wait', 'emu', W, 'if (!HostInputWaitEvent(&loop.event)) {', ''),
    ('w_run_process', 'emu', W, 'ProcessEvent(timer.GetTimeS());', ''),
    ('w_hint_rumble', 'emu', W, 'SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI_PS4_RUMBLE, "1");', ''),
    ('w_init', 'emu', W, 'if (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {', ''),
    ('w_prep_poll', 'emu', W, 'while (SDL_PollEvent(&g_window->loop.event)) {', ''),
    ('w_prep_removed', 'emu', W, 'g_window->loop.event.type == SDL_CONTROLLERDEVICEREMOVED) {', ''),
    ('w_hold_lock', 'emu', W, 'SDL_LockJoysticks();', 'case TestHidLossMode::Hold:'),
    ('w_hold_unlock', 'emu', W, 'SDL_UnlockJoysticks();', 'case TestHidLossMode::Hold:'),
    ('w_stat', 'emu', W, 'LOGF("TestHidLoss: stat mode=%s', ''),
    ('w_attach_virtual', 'emu', W, 'const int index = SDL_JoystickAttachVirtualEx(&desc);', ''),
    ('w_vp_desc_effect', 'emu', W, 'desc.SendEffect = TestHidLossVpSendEffect;', ''),
    ('w_probe_post', 'emu', W, 'if (!TestHidLossPost([posted_ns] {', ''),
    ('w_title_post', 'emu', W, 'PostToMainThread([this] {', 'if (title_async) {'),
    ('w_title_wait', 'emu', W, 'RunOnMainThread([this, text = std::move(text)] { SDL_SetWindowTitle(window, text.c_str()); });', ''),
    ('w_runon_wait', 'emu', W, 'main_task_done.Wait(&main_task_mutex);', ''),
    ('w_key_case', 'emu', W, 'GameEventKeyboard(game, key);', ''),
    ('w_f7', 'emu', W, 'event->key.keysym.sym == SDLK_F7) {', ''),
    ('w_ctl_button', 'emu', W, 'Controller::SetButton(f.id, button, f.down);', ''),
    ('w_shutdown_em', 'emu', W, 'Controller::EmergencyShutdown();', 'void WindowShutdown() {'),
    ('h_wait', 'emu', H, 'if (SDL_WaitEvent(event) == 0) {', ''),
    ('h_wait_to', 'emu', H, 'if (SDL_WaitEventTimeout(event, timeout_ms) != 0) {', ''),
    ('c_b24_read', 'emu', C, 'const char* value = std::getenv("KYTY_FIX_B24");', ''),
    ('c_po_apply_lock', 'emu', C, 'SDL_LockJoysticks();', 'void PadOutput::ApplyVibration('),
    ('c_connect_sdl', 'emu', C, 'auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(id));', 'void GameController::Connect(int id) {'),
    ('c_connect_lock', 'emu', C, 'Common::LockGuard lock(m_mutex);', 'void GameController::Connect(int id) {'),
    ('c_em_po_stop', 'emu', C, 'g_pad_output->Stop();', 'void EmergencyShutdown() {'),
    ('c_em_release', 'emu', C, 'g_controller->ReleaseHostPads();', 'void EmergencyShutdown() {'),
    ('c_release_lock', 'emu', C, 'Common::LockGuard lock(m_mutex);', 'void GameController::ReleaseHostPads() {'),
    ('c_release_delay', 'emu', C, 'SDL_Delay(RELEASE_FLUSH_MS);', ''),
    ('c_release_close', 'emu', C, 'SDL_GameControllerClose(pad);', 'SDL_Delay(RELEASE_FLUSH_MS);'),
    ('g_titleasync', 'emu', 'src/common/gates.cpp', '{"KYTY_TITLE_ASYNC", "titleasync", 1, 1},', ''),
    ('s_apple_only', 'emu', 'src/graphics/presentation/window/swapchain.cpp', 'm_window.RunOnMainThread([this] { m_window.RecreateSurface(); });', ''),
    ('i_hostkey', 'emu', 'src/graphics/presentation/window/inputScript.cpp', 'HostInputKey(action.key_code, true);', ''),
    # SDL2 4b69833b
    ('e_update_flag', 'sdl', E, 'static SDL_bool SDL_update_joysticks = SDL_TRUE;', ''),
    ('e_pump_video', 'sdl', E, '_this->PumpEvents(_this);', 'static void SDL_PumpEventsInternal('),
    ('e_pump_joy_if', 'sdl', E, 'if (SDL_update_joysticks) {', 'static void SDL_PumpEventsInternal('),
    ('e_pump_joy', 'sdl', E, 'SDL_JoystickUpdate();', 'static void SDL_PumpEventsInternal('),
    ('e_poll_guard', 'sdl', E, 'if (SDL_WasInit(SDL_INIT_JOYSTICK) && SDL_update_joysticks) {', 'static Sint16 SDL_events_get_polling_interval('),
    ('e_poll_num', 'sdl', E, 'if (SDL_NumJoysticks() > 0) {', 'static Sint16 SDL_events_get_polling_interval('),
    ('e_wakeup', 'sdl', E, 'SDL_SendWakeupEvent();', 'if (used > 0 && action == SDL_ADDEVENT) {'),
    ('e_hint_read', 'sdl', E, 'SDL_CalculateShouldUpdateJoysticks(SDL_GetHintBoolean(SDL_HINT_AUTO_UPDATE_JOYSTICKS, SDL_TRUE));', ''),
    ('e_hint_cb', 'sdl', E, 'SDL_AddHintCallback(SDL_HINT_AUTO_UPDATE_JOYSTICKS, SDL_AutoUpdateJoysticksChanged, NULL);', ''),
    ('h_events_warn', 'sdl', 'include/SDL_events.h', '* **WARNING**: This should only be run in the thread that initialized the', ''),
    ('h_lock_doc', 'sdl', 'include/SDL_joystick.h', '* Locking for multi-threaded access to the joystick API', ''),
    ('h_lock_doc2', 'sdl', 'include/SDL_joystick.h', '* If you are using the joystick API or handling events from multiple threads', ''),
    ('h_lock_doc3', 'sdl', 'include/SDL_joystick.h', '* and game controller events will not be delivered.', ''),
    ('h_update_doc', 'sdl', 'include/SDL_joystick.h', '* This is called automatically by the event loop if any joystick events are', ''),
    ('h_vj_update', 'sdl', 'include/SDL_joystick.h', 'void (SDLCALL *Update)(void *userdata);', ''),
    ('h_hint_auto', 'sdl', 'include/SDL_hints.h', '* - "0": You\'ll call SDL_JoystickUpdate() manually', ''),
    ('h_hint_auto_rt', 'sdl', 'include/SDL_hints.h', '#define SDL_HINT_AUTO_UPDATE_JOYSTICKS  "SDL_AUTO_UPDATE_JOYSTICKS"', ''),
    ('h_hint_raw', 'sdl', 'include/SDL_hints.h', '* - "0": RAWINPUT drivers are not used (the default)', ''),
    ('h_hint_thread', 'sdl', 'include/SDL_hints.h', '#define SDL_HINT_JOYSTICK_THREAD "SDL_JOYSTICK_THREAD"', ''),
    ('j_lock', 'sdl', J, 'void SDL_LockJoysticks(void)', ''),
    ('j_lock_mutex', 'sdl', J, 'SDL_LockMutex(SDL_joystick_lock);', 'void SDL_LockJoysticks(void)'),
    ('j_numjoy', 'sdl', J, 'int SDL_NumJoysticks(void)', ''),
    ('j_close', 'sdl', J, 'void SDL_JoystickClose(SDL_Joystick *joystick)', ''),
    ('j_close_drv', 'sdl', J, 'joystick->driver->Close(joystick);', 'void SDL_JoystickClose(SDL_Joystick *joystick)'),
    ('j_update', 'sdl', J, 'void SDL_JoystickUpdate(void)', ''),
    ('j_update_lock', 'sdl', J, 'SDL_LockJoysticks();', 'void SDL_JoystickUpdate(void)'),
    ('j_update_hidapi', 'sdl', J, 'HIDAPI_UpdateDevices();', 'void SDL_JoystickUpdate(void)'),
    ('j_update_drv', 'sdl', J, 'joystick->driver->Update(joystick);', 'void SDL_JoystickUpdate(void)'),
    ('j_update_detect', 'sdl', J, 'SDL_joystick_drivers[i]->Detect();', 'void SDL_JoystickUpdate(void)'),
    ('j_update_unlock', 'sdl', J, 'SDL_UnlockJoysticks();', 'SDL_joystick_drivers[i]->Detect();'),
    ('gc_from_id_lock', 'sdl', 'src/joystick/SDL_gamecontroller.c', 'SDL_LockJoysticks();', 'SDL_GameController *SDL_GameControllerFromInstanceID(SDL_JoystickID joyid)'),
    ('gc_close', 'sdl', 'src/joystick/SDL_gamecontroller.c', 'void SDL_GameControllerClose(SDL_GameController *gamecontroller)', ''),
    ('gc_close_lock', 'sdl', 'src/joystick/SDL_gamecontroller.c', 'SDL_LockJoysticks();', 'void SDL_GameControllerClose(SDL_GameController *gamecontroller)'),
    ('vj_update_cb', 'sdl', 'src/joystick/virtual/SDL_virtualjoystick.c', 'hwdata->desc.Update(hwdata->desc.userdata);', ''),
    ('hd_wndproc_cnt', 'sdl', 'src/hidapi/SDL_hidapi.c', '++SDL_HIDAPI_discovery.m_unDeviceChangeCounter;', 'static LRESULT CALLBACK ControllerWndProc('),
    ('hd_window', 'sdl', 'src/hidapi/SDL_hidapi.c', 'SDL_HIDAPI_discovery.m_hwndMsg = CreateWindowExA(0, "SDL_HIDAPI_DEVICE_DETECTION"', ''),
    ('hd_if0', 'sdl', 'src/hidapi/SDL_hidapi.c', '#if 0 /* just let the usual SDL_PumpEvents loop dispatch these, fixing bug 4286. --ryan. */', ''),
    ('hd_if0_cmt', 'sdl', 'src/hidapi/SDL_hidapi.c', '/* We\'ll only get messages on the same thread that created the window */', ''),
    ('hd_count', 'sdl', 'src/hidapi/SDL_hidapi.c', 'Uint32 SDL_hid_device_change_count(void)', ''),
    ('hd_count_upd', 'sdl', 'src/hidapi/SDL_hidapi.c', 'HIDAPI_UpdateDiscovery();', 'Uint32 SDL_hid_device_change_count(void)'),
    ('wj_cm_cb', 'sdl', 'src/joystick/windows/SDL_windowsjoystick.c', 's_bWindowsDeviceChanged = SDL_TRUE;', 'static DWORD CALLBACK SDL_DeviceNotificationFunc('),
    ('wj_timer_flag', 'sdl', 'src/joystick/windows/SDL_windowsjoystick.c', 's_bWindowsDeviceChanged = SDL_TRUE;', 'case WM_TIMER:'),
    ('wj_cm_reg', 'sdl', 'src/joystick/windows/SDL_windowsjoystick.c', 'SDL_CreateDeviceNotificationFunc();', 'static int WINDOWS_JoystickInit(void)'),
    ('wj_thread_hint', 'sdl', 'src/joystick/windows/SDL_windowsjoystick.c', 's_bJoystickThread = SDL_GetHintBoolean(SDL_HINT_JOYSTICK_THREAD, SDL_FALSE);', ''),
    ('wj_detect_flag', 'sdl', 'src/joystick/windows/SDL_windowsjoystick.c', 'if (!s_bWindowsDeviceChanged) {', 'void WINDOWS_JoystickDetect(void)'),
    ('wj_dinput_detect', 'sdl', 'src/joystick/windows/SDL_windowsjoystick.c', 'SDL_DINPUT_JoystickDetect(&pCurList);', ''),
    ('wj_xinput_detect', 'sdl', 'src/joystick/windows/SDL_windowsjoystick.c', 'SDL_XINPUT_JoystickDetect(&pCurList);', ''),
    ('di_minute', 'sdl', 'src/joystick/windows/SDL_dinputjoystick.c', '/* In some environments, IDirectInput8_Initialize / _EnumDevices can take a minute even with no controllers. */', ''),
    ('di_coinit', 'sdl', 'src/joystick/windows/SDL_dinputjoystick.c', 'result = WIN_CoInitialize();', 'int SDL_DINPUT_JoystickInit(void)'),
    ('di_cocreate', 'sdl', 'src/joystick/windows/SDL_dinputjoystick.c', 'result = CoCreateInstance(&CLSID_DirectInput8, NULL, CLSCTX_INPROC_SERVER,', ''),
    ('di_enum', 'sdl', 'src/joystick/windows/SDL_dinputjoystick.c', 'IDirectInput8_EnumDevices(dinput, DI8DEVCLASS_GAMECTRL, EnumJoystickDetectCallback, pContext, DIEDFL_ATTACHEDONLY);', ''),
    ('ri_default', 'sdl', 'src/joystick/windows/SDL_rawinputjoystick.c', 'if (!SDL_GetHintBoolean(SDL_HINT_JOYSTICK_RAWINPUT, SDL_FALSE)) {', ''),
    ('hid_close_wait', 'sdl', 'src/hidapi/windows/hid.c', 'GetOverlappedResult(dev->device_handle, &dev->ol, &bytes_read, TRUE/*wait*/);', ''),
    ('hj_rumble_wait', 'sdl', 'src/joystick/hidapi/SDL_hidapijoystick.c', 'while (SDL_AtomicGet(&device->rumble_pending) > 0) {', ''),
    ('we_keydown', 'sdl', 'src/video/windows/SDL_windowsevents.c', 'case WM_KEYDOWN:', 'LRESULT CALLBACK\nWIN_WindowProc'),
    ('we_keydown_send', 'sdl', 'src/video/windows/SDL_windowsevents.c', 'SDL_SendKeyboardKey(SDL_PRESSED, code);', 'case WM_KEYDOWN:'),
    ('we_vk_f13', 'sdl', 'src/video/windows/SDL_windowsevents.c', 'case VK_F13:', ''),
    ('we_pump_peek', 'sdl', 'src/video/windows/SDL_windowsevents.c', 'while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {', 'void WIN_PumpEvents(_THIS)'),
    ('we_wait_msg', 'sdl', 'src/video/windows/SDL_windowsevents.c', 'ret = MsgWaitForMultipleObjects(0, NULL, FALSE, dwMilliseconds, QS_ALLINPUT);', ''),
    ('we_wakeup', 'sdl', 'src/video/windows/SDL_windowsevents.c', 'PostMessage(data->hwnd, data->videodata->_SDL_WAKEUP, 0, 0);', ''),
    ('kb_nofocus', 'sdl', 'src/events/SDL_keyboard.c', '/* Drop events that don\'t change state */', 'static int SDL_SendKeyboardKeyInternal('),
    ('sdl_helper', 'sdl', 'src/SDL.c', 'if (SDL_HelperWindowCreate() < 0) {', ''),
]


def show(repo, path):
    root, commit = REPO[repo]
    r = subprocess.run(['git', '-C', root, 'show', commit + ':' + path], capture_output=True)
    if r.returncode != 0:
        raise SystemExit('git show failed ' + repo + ' ' + path)
    return r.stdout.decode('utf-8', 'replace').replace(chr(13), '').split(chr(10))


def resolve(lines, anchor, after):
    start = 0
    if after:
        if chr(10) in after:  # multi-line 'after': last part only
            after = after.split(chr(10))[-1]
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
    if mode == 'build':
        rows = []
        for key, repo, p, anchor, after in REFS:
            lines = cache.setdefault((repo, p), show(repo, p))
            n = resolve(lines, anchor, after)
            if n is None:
                print('NOT FOUND', key)
                sys.exit(1)
            plus1 = lines[n].strip()[:40] if n < len(lines) else ''
            rows.append((key, REPO[repo][1], p, str(n), anchor, plus1))
            print(key, REPO[repo][1] + ':' + p + ':' + str(n))
        with open(path, 'w', encoding='utf-8', newline=chr(10)) as o:
            for r in rows:
                o.write(chr(9).join(r) + chr(10))
        print('rows', len(rows))
        return
    if mode == 'text':  # every <commit>:<path>:<line> of the report (and the short ':<line>' after it) is in the table
        import re
        table = set()
        for l in open(sys.argv[3], encoding='utf-8'):
            if l.strip():
                k, c, p, n = l.split(chr(9))[:4]
                table.add((c, p, n))
        text = open(path, encoding='utf-8').read()
        rx = re.compile(r'`(?:(730ed40a|4b69833b):([^`:]+):|:)(\d+)`')
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
    rev = {v[1]: k for k, v in REPO.items()}
    for key, commit, p, n, anchor, plus1 in rows:
        lines = cache.setdefault((commit, p), show(rev[commit], p))
        i = int(n)
        ok = anchor in lines[i - 1] and (plus1 == '' or (i < len(lines) and lines[i].strip().startswith(plus1)))
        if not ok:
            bad += 1
            print('BAD', key, commit, p, n)
    print('links', len(rows), 'bad', bad)
    print('ALL OK' if bad == 0 and len(rows) == len(REFS) else 'FAIL')


if __name__ == '__main__':
    main()
