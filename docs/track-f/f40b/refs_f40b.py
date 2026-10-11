#!/usr/bin/env python3
# F40b (HPP-771): links <commit>:<path>:<line> of f40b-review.md - anchor (substring of the line) and control +1
# (the next line, stripped, starts with NEXT; NEXT '' - the next line is blank).
#   python refs_f40b.py check            - every row
#   python refs_f40b.py text <review.md> - every link of the text is a row
#   python refs_f40b.py find <commit> <path> <substring> - line numbers (helper)
import re
import subprocess
import sys

KYTY = 'C:/kyty/KytyPS5'
SDL = 'C:/kyty/KytyPS5/3rdparty/SDL2'
JP = 'src/graphics/presentation/window/joyPump.cpp'
HI = 'src/graphics/presentation/window/hostInput.cpp'
WN = 'src/graphics/presentation/window/window.cpp'
CT = 'src/libs/controller.cpp'
E3 = 'e3aa4b4d'
S = '4b69833b'

ROWS = [
    (E3, JP, 98, r'bool Stopping() const { return m_stop.load(std::memory_order_acquire); }', r''),
    (E3, JP, 140, r'm_cv.wait(lock, [this] { return m_init_done; });', r'if (!m_init_ok && error != nullptr) {'),
    (E3, JP, 148, r'const auto pump_tid = static_cast<uint64_t>(SDL_ThreadID());', r'SDL_ClearError();'),
    (E3, JP, 151, r'LOGF("FixF24: init tid=', r'pump_tid, main_tid);'),
    (E3, JP, 153, r'const bool ok = SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER) == 0;', r'{'),
    (E3, JP, 183, r'SDL_JoystickUpdate();', r'const uint64_t wall_us = NowUs() - start_us;'),
    (E3, JP, 185, r'if (Stopping()) {', r'return;'),
    (E3, JP, 204, r'if (Stopping()) {', r'return;'),
    (E3, JP, 209, r'std::lock_guard lock(m_mutex);', r'if (m_tasks.empty()) {'),
    (E3, JP, 220, r'fn();', r'if (m_stand_window.load(std::memory_order_relaxed)) {'),
    (E3, JP, 241, r'MsgWaitForMultipleObjectsEx(1, &m_event, timeout_ms, QS_ALLINPUT, MWMO_INPUTAVAILABLE);', r'#else'),
    (E3, JP, 279, r'SDL_LockJoysticks();', r'const int count = SDL_NumJoysticks();'),
    (E3, JP, 283, r'if (id < 0 || !m_seen.insert(id).second) {', r'continue;'),
    (E3, JP, 289, r'auto* pad = SDL_GameControllerOpen(index);', r'if (pad == nullptr) {'),
    (E3, JP, 328, r'Controller::Connect(id);', r'// A removal posted by another thread'),
    (E3, JP, 346, r'm_stop.store(true, std::memory_order_seq_cst);', r'Wake();'),
    (E3, JP, 356, r'if (thread.get_id() == std::this_thread::get_id()) {', r'thread.detach();'),
    (E3, JP, 370, r'LOGF("FixF24: pump_stop_expired', r'thread.detach();'),
    (E3, JP, 380, r'if (done.exchange(true)) {', r'return;'),
    (E3, JP, 383, r'g_enabled.store(Common::EnvFlagOn("KYTY_FIX_F24"), std::memory_order_release);', r'LOGF("FixF24: mode='),
    (E3, JP, 403, r'void NoteAddEvent(int index) {', r'if (LineAllowed(g_add_lines)) {'),
    (E3, HI, 430, r'const int bound_ms = JoyPump::OpenPads() > 0 ? 1 : 3000;', r'if (!g_mouse.enabled || SDL_GetKeyboardFocus() == nullptr) {'),
    (E3, HI, 434, r'if (SDL_WaitEventTimeout(event, bound_ms) != 0) {', r'return true;'),
    (E3, HI, 446, r'const int timeout_ms = std::min(PollMouse(SDL_GetTicks64()), bound_ms);', r'SDL_ClearError();'),
    (E3, HI, 458, r'if (JoyPump::Enabled()) {', r'return HostInputWaitEventF24(event);'),
    (E3, WN, 390, r'if (f.added && JoyPump::Enabled()) {', r'// Track F, F40a (KYTY_FIX_F24=1, RC2)'),
    (E3, WN, 420, r'JoyPump::PostClose(f.id);', r'} else {'),
    (E3, WN, 951, r'SDL_SetHint(SDL_HINT_AUTO_UPDATE_JOYSTICKS, "0");', r'if (SDL_InitSubSystem(SDL_INIT_VIDEO) < 0) {'),
    (E3, WN, 956, r'if (!JoyPump::Start(main_tid, &error)) {', r'EXIT('),
    (E3, WN, 959, r'} else if (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {', r'EXIT('),
    (E3, CT, 40, r'constexpr uint32_t RELEASE_FLUSH_MS   = 50;', r''),
    (E3, CT, 859, r'if (Libs::Graphics::JoyPump::Exited()) {', r'delete g_controller;'),
    (E3, CT, 873, r'Libs::Graphics::JoyPump::Stop();', r'}'),
    (E3, CT, 1187, r'SDL_Delay(RELEASE_FLUSH_MS);', r'for (auto* pad: pads) {'),
    (S, 'src/SDL.c', 229, r'if (flags & (SDL_INIT_HAPTIC | SDL_INIT_JOYSTICK)) {', r'if (SDL_HelperWindowCreate() < 0) {'),
    (S, 'src/joystick/hidapi/SDL_hidapijoystick.c', 625, r'SDL_HIDAPI_change_count = SDL_hid_device_change_count();', r'HIDAPI_UpdateDeviceList();'),
    (S, 'src/hidapi/SDL_hidapi.c', 365, r'HIDAPI_InitializeDiscovery();', r'}'),
    (S, 'src/hidapi/SDL_hidapi.c', 240, r'CreateWindowExA(0, "SDL_HIDAPI_DEVICE_DETECTION"', r''),
    (S, 'src/video/windows/SDL_windowswindow.c', 56, r'SDL_HelperWindowClassName = TEXT("SDLHelperWindowInputCatcher");', r'static const TCHAR *SDL_HelperWindowName'),
    (S, 'src/joystick/windows/SDL_windowsjoystick.c', 302, r'data->messageWindow = CreateWindowEx(0, TEXT("Message")', r'if (!data->messageWindow) {'),
    (S, 'src/events/SDL_events.c', 922, r'if (SDL_update_joysticks) {', r'SDL_JoystickUpdate();'),
    (S, 'src/events/SDL_events.c', 967, r'if (SDL_WasInit(SDL_INIT_JOYSTICK) && SDL_update_joysticks) {', r'if (SDL_NumJoysticks() > 0) {'),
    (S, 'src/events/SDL_events.c', 1008, r'status = SDL_PeepEvents(event, 1, SDL_GETEVENT, SDL_FIRSTEVENT, SDL_LASTEVENT);', r'if (status < 0) {'),
    (S, 'src/events/SDL_events.c', 1035, r'SDL_AtomicSetPtr(&_this->wakeup_window, wakeup_window);', r'status = _this->WaitEventTimeout(_this, loop_timeout);'),
    (S, 'src/joystick/SDL_joystick.c', 2177, r'SDL_LockJoysticks();', r''),
    (S, 'src/joystick/SDL_joystick.c', 2193, r'joystick->driver->Update(joystick);', r''),
    (S, 'src/joystick/SDL_joystick.c', 1594, r'if (joystick->rumble_expiration) {', r'SDL_JoystickRumble(joystick, 0, 0, 0);'),
    (S, 'src/joystick/virtual/SDL_virtualjoystick.c', 73, r'hwdata->joystick->hwdata = NULL;', r'hwdata->joystick = NULL;'),
    (S, 'src/joystick/virtual/SDL_virtualjoystick.c', 429, r'if (joystick->hwdata) {', r'joystick_hwdata *hwdata = joystick->hwdata;'),
    (S, 'src/joystick/virtual/SDL_virtualjoystick.c', 437, r'result = SDL_SetError("Rumble failed, device disconnected");', r'}'),
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
