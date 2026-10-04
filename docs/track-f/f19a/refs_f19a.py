# F19a (HPP-543): references of f19a.md (general rule 24(1)): <commit>:<path>:<line> with an anchor and the +1 control.
#   python refs_f19a.py gen   <code_commit> <sdl_commit> <doc_commit> <out.tsv>
#       resolves SPEC (path, line, anchor): the anchor must stand in that line (line 0 - the only line of the file that
#       holds the anchor is taken); writes repo-key, commit, path, line, anchor, +1 text (stripped, first 60 chars)
#   python refs_f19a.py check <refs.tsv> <report.md>
#       re-reads every row from git ('git show <commit>:<path>'), checks the anchor in the line and the +1 text in the
#       next line; then checks that every 'name.ext:<line>' written in the report is a row of the table (by file name
#       and line).  Prints 'refs N of N', 'report refs M of M', 'ALL OK'.
import re, subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = {'K': 'C:/kyty/KytyPS5', 'S': 'C:/kyty/KytyPS5/3rdparty/SDL2'}
W = 'src/graphics/presentation/window/window.cpp'
HI = 'src/graphics/presentation/window/hostInput.cpp'
SWP = 'src/graphics/presentation/window/swapchain.cpp'
C = 'src/libs/controller.cpp'
CH = 'src/libs/controller.h'
EV = 'src/events/SDL_events.c'
J = 'src/joystick/SDL_joystick.c'
G = 'src/joystick/SDL_gamecontroller.c'
HJ = 'src/joystick/hidapi/SDL_hidapijoystick.c'
P5 = 'src/joystick/hidapi/SDL_hidapi_ps5.c'
RB = 'src/joystick/hidapi/SDL_hidapi_rumble.c'
HID = 'src/hidapi/windows/hid.c'
HA = 'src/hidapi/SDL_hidapi.c'
WJ = 'src/joystick/windows/SDL_windowsjoystick.c'
VJ = 'src/joystick/virtual/SDL_virtualjoystick.c'
HN = 'include/SDL_hints.h'
JH = 'include/SDL_joystick.h'
# (repo key, commit key, path, line, anchor)
SPEC = [
    ('K', 'DOC', 'docs/ROADMAP.md', 22379, '441. **Звено F18b трека F (`HPP-536`, лид): F18a (`HPP-535`) ПРИНЯТ'),
    ('K', 'DOC', 'docs/ROADMAP.md', 22393, '(з) **Следующая итерация очереди F — F19 = Б24'),
    ('K', 'DOC', 'docs/track-f/register.md', 0, '| Б24 | K2 (на удержании) | дефект | остановка главного потока 23,8 с'),
    ('K', 'DOC', 'docs/track-f/register.md', 0, '| Б24 (поправка к §4, §48) |'),
    # emulator: the event handler and the main loop
    ('K', 'CODE', W, 344, '#ifdef KYTY_DBG_INPUT'),
    ('K', 'CODE', W, 360, 'auto* pad = SDL_GameControllerOpen(f.id);'),
    ('K', 'CODE', W, 375, 'Controller::Connect(id);'),
    ('K', 'CODE', W, 378, 'if (f.removed) {'),
    ('K', 'CODE', W, 380, 'SDL_GameControllerClose(SDL_GameControllerFromInstanceID(f.id));'),
    ('K', 'CODE', W, 749, 'case SDL_CONTROLLERDEVICEREMOVED:'),
    ('K', 'CODE', W, 799, 'void WindowContext::PostToMainThread(std::function<void()> task) {'),
    ('K', 'CODE', W, 829, 'if (age >= 50000000ull) {'),
    ('K', 'CODE', W, 831, 'if (late_logged.fetch_add(1, std::memory_order_relaxed) < 32) {'),
    ('K', 'CODE', W, 854, 'DrainMainThreadTasks();'),
    ('K', 'CODE', W, 863, 'if (!HostInputWaitEvent(&loop.event)) {'),
    ('K', 'CODE', W, 878, 'SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI_PS4_RUMBLE, "1");'),
    ('K', 'CODE', W, 884, 'if (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {'),
    ('K', 'CODE', W, 993, 'while (SDL_PollEvent(&g_window->loop.event)) {'),
    ('K', 'CODE', W, 1003, 'g_window->loop.event.type == SDL_CONTROLLERDEVICEREMOVED) {'),
    ('K', 'CODE', W, 1019, 'SDL_Delay(16);'),
    ('K', 'CODE', W, 1035, 'Controller::EmergencyShutdown();'),
    ('K', 'CODE', W, 1047, 'void WindowTestMinimizeNoteGuestText(const char* text, size_t size) {'),
    ('K', 'CODE', W, 1239, 'PostToMainThread([ms] { std::this_thread::sleep_for(std::chrono::milliseconds(ms)); });'),
    ('K', 'CODE', W, 1267, 'RunOnMainThread([this, text = std::move(text)] { SDL_SetWindowTitle(window, text.c_str()); });'),
    ('K', 'CODE', SWP, 632, 'm_window.RunOnMainThread([this] { m_window.RecreateSurface(); });'),
    ('K', 'CODE', HI, 424, 'if (SDL_WaitEvent(event) == 0) {'),
    ('K', 'CODE', HI, 432, 'if (SDL_WaitEventTimeout(event, timeout_ms) != 0) {'),
    # emulator: the pad
    ('K', 'CODE', CH, 19, 'constexpr int HOST_INPUT_CONTROLLER_ID = -1000;'),
    ('K', 'CODE', C, 31, 'constexpr uint32_t RUMBLE_DURATION_MS = 0xffff;'),
    ('K', 'CODE', C, 32, 'constexpr uint32_t RELEASE_FLUSH_MS   = 50;'),
    ('K', 'CODE', C, 145, 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {'),
    ('K', 'CODE', C, 461, 'g_controller->Connect(HOST_INPUT_CONTROLLER_ID);'),
    ('K', 'CODE', C, 493, 'void GameController::Disconnect(int id) {'),
    ('K', 'CODE', C, 500, 'LOGF("Controller: disconnect of unknown id %d ignored\\n", id);'),
    ('K', 'CODE', C, 509, 'void GameController::CheckActive() {'),
    ('K', 'CODE', C, 739, 'void GameController::ReleaseHostPads() {'),
    ('K', 'CODE', C, 763, 'SDL_Delay(RELEASE_FLUSH_MS);'),
    ('K', 'CODE', C, 765, 'SDL_GameControllerClose(pad);'),
    ('K', 'CODE', C, 772, 'void GameController::SetVibration(uint8_t large_motor, uint8_t small_motor) {'),
    ('K', 'CODE', C, 775, 'if (m_active_id == HOST_INPUT_CONTROLLER_ID) {'),
    ('K', 'CODE', C, 778, 'auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));'),
    ('K', 'CODE', C, 785, 'if (SDL_GameControllerRumble(pad, large, small, RUMBLE_DURATION_MS) != 0) {'),
    ('K', 'CODE', C, 790, 'void GameController::SetLightBar(uint8_t r, uint8_t g, uint8_t b) {'),
    ('K', 'CODE', C, 792, 'if (auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));'),
    ('K', 'CODE', C, 794, '(void)SDL_GameControllerSetLED(pad, r, g, b);'),
    ('K', 'CODE', C, 821, 'Common::LockGuard lock(m_mutex);'),
    ('K', 'CODE', C, 822, 'auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));'),
    ('K', 'CODE', C, 824, '*sent = SDL_GameControllerSendEffect(pad, &effect, sizeof(effect)) == 0;'),
    ('K', 'CODE', C, 839, 'void GameController::ReadState(ControllerState* state, bool* flag, int* count) {'),
    ('K', 'CODE', C, 844, 'Common::LockGuard lock(m_mutex);'),
    ('K', 'CODE', C, 858, 'Common::LockGuard lock(m_mutex);'),
    ('K', 'CODE', C, 1119, 'LOGF("\\t large_motor = %d\\n"'),
    ('K', 'CODE', C, 1123, 'g_controller->SetVibration(param->large_motor, param->small_motor);'),
    # SDL2: the pump and the joystick update
    ('S', 'SDL', EV, 41, '#define ENUMERATION_POLL_INTERVAL_MS 3000'),
    ('S', 'SDL', EV, 44, '#define EVENT_POLL_INTERVAL_MS 1'),
    ('S', 'SDL', EV, 922, 'if (SDL_update_joysticks) {'),
    ('S', 'SDL', EV, 1006, 'SDL_PumpEventsInternal(SDL_TRUE);'),
    ('S', 'SDL', EV, 968, 'if (SDL_NumJoysticks() > 0) {'),
    ('S', 'SDL', EV, 1062, 'int SDL_WaitEvent(SDL_Event *event)'),
    ('S', 'SDL', EV, 1077, 'SDL_PumpEventsInternal(SDL_TRUE);'),
    ('S', 'SDL', EV, 1326, 'SDL_CalculateShouldUpdateJoysticks(SDL_GetHintBoolean(SDL_HINT_AUTO_UPDATE_JOYSTICKS, SDL_TRUE));'),
    ('S', 'SDL', J, 920, 'int SDL_JoystickAttachVirtualEx(const SDL_VirtualJoystickDesc *desc)'),
    ('S', 'SDL', J, 934, 'int SDL_JoystickDetachVirtual(int device_index)'),
    ('S', 'SDL', J, 1406, 'int SDL_JoystickRumble(SDL_Joystick *joystick, Uint16 low_frequency_rumble, Uint16 high_frequency_rumble, Uint32 duration_ms)'),
    ('S', 'SDL', J, 1410, 'SDL_LockJoysticks();'),
    ('S', 'SDL', J, 1414, 'if (low_frequency_rumble == joystick->low_frequency_rumble &&'),
    ('S', 'SDL', J, 1578, 'void SDL_JoystickClose(SDL_Joystick *joystick)'),
    ('S', 'SDL', J, 1601, 'joystick->driver->Close(joystick);'),
    ('S', 'SDL', J, 1890, 'void SDL_PrivateJoystickRemoved(SDL_JoystickID device_instance)'),
    ('S', 'SDL', J, 2167, 'void SDL_JoystickUpdate(void)'),
    ('S', 'SDL', J, 2177, 'SDL_LockJoysticks();'),
    ('S', 'SDL', J, 2185, 'HIDAPI_UpdateDevices();'),
    ('S', 'SDL', J, 2193, 'joystick->driver->Update(joystick);'),
    ('S', 'SDL', J, 2225, 'SDL_joystick_drivers[i]->Detect();'),
    ('S', 'SDL', J, 2228, 'SDL_UnlockJoysticks();'),
    ('S', 'SDL', G, 382, 'case SDL_JOYDEVICEREMOVED:'),
    ('S', 'SDL', G, 397, 'deviceevent.type = SDL_CONTROLLERDEVICEREMOVED;'),
    ('S', 'SDL', G, 2849, 'SDL_GameController *SDL_GameControllerFromInstanceID(SDL_JoystickID joyid)'),
    ('S', 'SDL', G, 2853, 'SDL_LockJoysticks();'),
    ('S', 'SDL', G, 3030, 'void SDL_GameControllerClose(SDL_GameController *gamecontroller)'),
    # SDL2: the HIDAPI joystick driver
    ('S', 'SDL', HJ, 405, 'static void HIDAPI_CleanupDeviceDriver(SDL_HIDAPI_Device *device)'),
    ('S', 'SDL', HJ, 419, 'SDL_LockMutex(device->dev_lock);'),
    ('S', 'SDL', HJ, 422, 'SDL_hid_close(device->dev);'),
    ('S', 'SDL', HJ, 520, 'dev = SDL_hid_open_path(device->path, 0);'),
    ('S', 'SDL', HJ, 583, 'SDL_HIDAPI_change_count = 0;'),
    ('S', 'SDL', HJ, 837, 'void HIDAPI_JoystickDisconnected(SDL_HIDAPI_Device *device, SDL_JoystickID joystickID)'),
    ('S', 'SDL', HJ, 871, 'SDL_HIDAPI_change_count = 0;'),
    ('S', 'SDL', HJ, 998, 'while (SDL_AtomicGet(&device->rumble_pending) > 0) {'),
    ('S', 'SDL', HJ, 1114, 'devs = SDL_hid_enumerate(0, 0);'),
    ('S', 'SDL', HJ, 1323, 'static void HIDAPI_JoystickDetect(void)'),
    ('S', 'SDL', HJ, 1327, 'if (SDL_HIDAPI_change_count != count) {'),
    ('S', 'SDL', HJ, 1350, 'if (SDL_TryLockMutex(device->dev_lock) == 0) {'),
    ('S', 'SDL', HJ, 1352, 'device->driver->UpdateDevice(device);'),
    ('S', 'SDL', HJ, 1609, 'if (SDL_AtomicGet(&device->rumble_pending) > 0) {'),
    ('S', 'SDL', P5, 44, '#define BLUETOOTH_DISCONNECT_TIMEOUT_MS 500'),
    ('S', 'SDL', P5, 416, 'if (ReadFeatureReport(device->dev, k_EPS5FeatureReportIdSerialNumber, data, sizeof(data)) >= 7) {'),
    ('S', 'SDL', P5, 792, 'SDL_HIDAPI_SendRumbleAndUnlock(device, data, sizeof(data));'),
    ('S', 'SDL', P5, 1031, 'if (SDL_HIDAPI_SendRumbleAndUnlock(device, data, report_size) != report_size) {'),
    ('S', 'SDL', P5, 1446, 'while ((size = SDL_hid_read_timeout(device->dev, data, sizeof(data), 0)) > 0) {'),
    ('S', 'SDL', P5, 1531, 'HIDAPI_JoystickDisconnected(device, device->joysticks[0]);'),
    ('S', 'SDL', RB, 82, 'SDL_LockMutex(request->device->dev_lock);'),
    ('S', 'SDL', RB, 87, 'SDL_hid_write(request->device->dev, request->data, request->size);'),
    # SDL2: hidapi for Windows
    ('S', 'SDL', HID, 57, '#define HID_WRITE_TIMEOUT_MILLISECONDS 500'),
    ('S', 'SDL', HID, 364, 'hid_enumerate(unsigned short vendor_id, unsigned short product_id)'),
    ('S', 'SDL', HID, 480, 'write_handle = open_device(device_interface_detail_data->DevicePath, TRUE, FALSE);'),
    ('S', 'SDL', HID, 492, 'HidD_GetAttributes(write_handle, &attrib);'),
    ('S', 'SDL', HID, 569, 'hidp_res = HidD_GetSerialNumberString(write_handle, wstr, sizeof(wstr));'),
    ('S', 'SDL', HID, 576, 'hidp_res = HidD_GetManufacturerString(write_handle, wstr, sizeof(wstr));'),
    ('S', 'SDL', HID, 583, 'hidp_res = HidD_GetProductString(write_handle, wstr, sizeof(wstr));'),
    ('S', 'SDL', HID, 796, 'res = WaitForSingleObject(dev->write_ol.hEvent, milliseconds);'),
    ('S', 'SDL', HID, 853, 'res = WaitForSingleObject(ev, milliseconds >= 0 ? milliseconds : INFINITE);'),
    ('S', 'SDL', HID, 950, 'res = GetOverlappedResult(dev->device_handle, &ol, &bytes_returned, TRUE/*wait*/);'),
    ('S', 'SDL', HID, 978, 'GetOverlappedResult(dev->device_handle, &dev->ol, &bytes_read, TRUE/*wait*/);'),
    ('S', 'SDL', HA, 381, 'if (SDL_ThreadID() == SDL_HIDAPI_discovery.m_nThreadID) {'),
    ('S', 'SDL', HA, 1226, 'Uint32 SDL_hid_device_change_count(void)'),
    ('S', 'SDL', HA, 1327, 'raw_devs = PLATFORM_hid_enumerate(vendor_id, product_id);'),
    # SDL2: the Windows joystick driver and the hint
    ('S', 'SDL', WJ, 357, 'static int SDLCALL SDL_JoystickThread(void *_data)'),
    ('S', 'SDL', WJ, 493, 's_bJoystickThread = SDL_GetHintBoolean(SDL_HINT_JOYSTICK_THREAD, SDL_FALSE);'),
    ('S', 'SDL', WJ, 529, 'void WINDOWS_JoystickDetect(void)'),
    ('S', 'SDL', WJ, 534, 'if (!s_bWindowsDeviceChanged) {'),
    ('S', 'SDL', WJ, 548, 'SDL_DINPUT_JoystickDetect(&pCurList);'),
    ('S', 'SDL', WJ, 551, 'SDL_XINPUT_JoystickDetect(&pCurList);'),
    ('S', 'SDL', 'src/joystick/windows/SDL_windows_gaming_input.c', 445, 'SDL_LockJoysticks();'),
    ('S', 'SDL', 'src/joystick/windows/SDL_windows_gaming_input.c', 589, 'SDL_LockJoysticks();'),
    ('S', 'SDL', HN, 332, '#define SDL_HINT_AUTO_UPDATE_JOYSTICKS  "SDL_AUTO_UPDATE_JOYSTICKS"'),
    ('S', 'SDL', HN, 1319, '#define SDL_HINT_JOYSTICK_THREAD "SDL_JOYSTICK_THREAD"'),
    # SDL2: the virtual joystick
    ('S', 'SDL', JH, 424, 'extern DECLSPEC int SDLCALL SDL_JoystickAttachVirtualEx(const SDL_VirtualJoystickDesc *desc);'),
    ('S', 'SDL', JH, 435, 'extern DECLSPEC int SDLCALL SDL_JoystickDetachVirtual(int device_index);'),
    ('S', 'SDL', VJ, 240, 'SDL_PrivateJoystickAdded(hwdata->instance_id);'),
    ('S', 'SDL', VJ, 256, 'SDL_PrivateJoystickRemoved(instance_id);'),
    ('S', 'SDL', VJ, 432, 'result = hwdata->desc.Rumble(hwdata->desc.userdata, low_frequency_rumble, high_frequency_rumble);'),
    ('S', 'SDL', VJ, 494, 'result = hwdata->desc.SetLED(hwdata->desc.userdata, red, green, blue);'),
    ('S', 'SDL', VJ, 561, 'static void VIRTUAL_JoystickClose(SDL_Joystick *joystick)'),
    ('S', 'SDL', VJ, 581, 'static SDL_bool VIRTUAL_JoystickGetGamepadMapping(int device_index, SDL_GamepadMapping *out)'),
    ('S', 'SDL', 'include/SDL_version.h', 60, '#define SDL_MINOR_VERSION   33'),
]
cache = {}


def lines(rk, commit, path):
    key = (rk, commit, path)
    if key not in cache:
        o = subprocess.run([GIT, '-C', REPO[rk], 'show', commit + ':' + path], capture_output=True)
        cache[key] = o.stdout.decode('utf-8', 'replace').split('\n')
    return cache[key]


def gen(code, sdl, doc, out):
    com = {'CODE': code, 'SDL': sdl, 'DOC': doc}
    rows, bad = [], 0
    for rk, ck, path, line, anchor in SPEC:
        L = lines(rk, com[ck], path)
        if line == 0:
            hits = [i + 1 for i, s in enumerate(L) if anchor in s]
            if len(hits) != 1:
                print('FAIL search %s: %d hits for %r' % (path, len(hits), anchor[:60]))
                bad += 1
                continue
            line = hits[0]
        a = L[line - 1] if line - 1 < len(L) else ''
        if anchor not in a:
            near = [i + 1 for i, s in enumerate(L) if anchor in s]
            print('FAIL %s:%d anchor not in line; lines with the anchor: %s' % (path, line, near[:6]))
            bad += 1
            continue
        b = (L[line] if line < len(L) else '').strip()[:60]
        rows.append('\t'.join([rk, com[ck], path, str(line), anchor, b]))
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(rows) + '\n')
    print('rows %d of %d' % (len(rows), len(SPEC)))
    print('GEN OK' if bad == 0 else 'GEN FAILED')
    return 1 if bad else 0


def check(tsv, report):
    rows = [l.rstrip('\n').split('\t') for l in open(tsv, encoding='utf-8') if l.strip()]
    ok = 0
    names = set()
    for rk, commit, path, line, anchor, plus1 in rows:
        line = int(line)
        L = lines(rk, commit, path)
        a = L[line - 1] if line - 1 < len(L) else ''
        b = L[line] if line < len(L) else ''
        good = anchor in a and b.strip()[:60] == plus1
        ok += good
        if not good:
            print('FAIL %s:%s:%d' % (commit, path, line))
        names.add((path.rsplit('/', 1)[1], line))
    print('refs %d of %d' % (ok, len(rows)))
    text = open(report, encoding='utf-8').read()
    cited = set((m.group(1), int(m.group(2))) for m in re.finditer(r'([A-Za-z0-9_]+\.(?:cpp|c|h|md)):(\d+)', text))
    miss = sorted(c for c in cited if c not in names)
    for c in miss:
        print('NOT IN TABLE %s:%d' % c)
    print('report refs %d of %d' % (len(cited) - len(miss), len(cited)))
    good = ok == len(rows) and not miss
    print('ALL OK' if good else 'FAILED')
    return 0 if good else 1


if sys.argv[1] == 'gen':
    sys.exit(gen(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
sys.exit(check(sys.argv[2], sys.argv[3]))
