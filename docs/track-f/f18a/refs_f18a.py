# F18a (HPP-535): check of the references of f18a.md (general rule 24(1)): <commit>:<path>:<line> with an anchor and the
# +1 control line.  Emulator code - repository C:/kyty/KytyPS5 at <code_commit>; SDL2 - the submodule 3rdparty/SDL2 at
# <sdl_commit>.  Usage: python refs_f18a.py <code_commit> <sdl_commit>   (prints 'N of N' and 'ALL OK')
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
SDLREPO = REPO + '/3rdparty/SDL2'
CODE = sys.argv[1]
SDL = sys.argv[2]
DOC = '66da0c76'
A = 'src/libs/audio.cpp'
C = 'src/libs/controller.cpp'
A2 = 'src/libs/libAudio2.cpp'
W = 'src/graphics/presentation/window/window.cpp'
S = 'src/SDL.c'
SA = 'src/audio/SDL_audio.c'
SW = 'src/audio/wasapi/SDL_wasapi.c'
REFS = [
    (REPO, DOC, 'docs/ROADMAP.md', 22306, '433. **Звено F17b трека F (`HPP-526`, лид): F17a (`HPP-525`) ПРИНЯТ', '(а) **Приёмка строкой. F17a ✓**'),
    (REPO, DOC, 'docs/ROADMAP.md', 22312, '(е) **Следующая итерация очереди F — F18 = Ф8', '(ж) **Таблица строк K1–K4 без исхода'),
    (REPO, DOC, 'docs/track-f/register.md', 175, '| Ф8 | K4 | наблюдение (последняя с. 105) |', '| Б22 | K5 |'),
    # the output port and the queue
    (REPO, CODE, A, 212, 'SDL_AudioDeviceID audio_device = 0;', 'SDL_AudioSpec     audio_spec   = {};'),
    (REPO, CODE, A, 258, 'static std::vector<SDL_AudioDeviceID> g_frozen_devices;', ''),
    (REPO, CODE, A, 265, 'SDL_PauseAudioDevice(device, frozen ? 1 : 0);', ''),
    (REPO, CODE, A, 378, 'static bool        resolved = false;', ''),
    (REPO, CODE, A, 435, 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {', 'LOGF("AudioOut: SDL audio init failed'),
    (REPO, CODE, A, 451, 'port->audio_device =', 'SDL_OpenAudioDevice(device, 0, &desired, &obtained, SDL_AUDIO_ALLOW_ANY_CHANGE);'),
    (REPO, CODE, A, 461, 'LOGF("AudioOut: opened SDL device', ''),
    (REPO, CODE, A, 470, 'if (port->audio_device != 0 && SDL_WasInit(SDL_INIT_AUDIO) != 0) {', 'AudioUnregisterDevice(port->audio_device);'),
    (REPO, CODE, A, 476, 'port->audio_device = 0;', ''),
    (REPO, CODE, A, 555, 'if (port->audio_device == 0 || data == nullptr) {', 'return false;'),
    (REPO, CODE, A, 613, 'const auto        av_queued_before = SDL_GetQueuedAudioSize(port->audio_device);', ''),
    (REPO, CODE, A, 625, 'while (SDL_GetQueuedAudioSize(port->audio_device) > min_queued_size) {', ''),
    (REPO, CODE, A, 640, 'if (SDL_QueueAudio(port->audio_device, queue_data, queue_size) < 0) {',
     'LOGF("AudioOut: SDL_QueueAudio failed: %s\\n", SDL_GetError());'),
    (REPO, CODE, A, 698, 'if (type != AUDIO_OUT_PORT_TYPE_VIBRATION) {', 'OpenSdlDevice(&port);'),
    (REPO, CODE, A, 718, 'CloseSdlDevice(&port);', ''),
    (REPO, CODE, A, 738, 'm_out_ports[handle.GetId()].used && m_out_ports[handle.GetId()].audio_device != 0);', ''),
    (REPO, CODE, A, 778, 'uint32_t Audio::AudioOutOutputs(OutputParam* params, uint32_t num, bool blocking) {', ''),
    (REPO, CODE, A, 797, 'if (m_out_ports[params[i].handle.GetId()].audio_device != 0) {', 'any_port_has_device = true;'),
    (REPO, CODE, A, 806, 'if (blocking && max_wait_time != 0 && !any_port_has_device) {', 'Common::Thread::SleepMicro(max_wait_time);'),
    (REPO, CODE, A, 814, 'Controller::PushHapticsPcm(params[i].data, port.samples_num,', ''),
    (REPO, CODE, A, 818, 'QueueSdlAudio(&port, params[i].data, blocking);', ''),
    # the input port
    (REPO, CODE, A, 829, 'const auto& name = Config::GetAudioInputDevice();', 'if (name.empty()) {'),
    (REPO, CODE, A, 833, 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {', 'LOGF("AudioIn: SDL init failed'),
    (REPO, CODE, A, 846, 'SDL_QuitSubSystem(SDL_INIT_AUDIO);', ''),
    (REPO, CODE, A, 854, 'SDL_CloseAudioDevice(port->audio_device);', 'SDL_QuitSubSystem(SDL_INIT_AUDIO);'),
    (REPO, CODE, A, 962, 'failed = SDL_GetAudioDeviceStatus(snapshot.audio_device) != SDL_AUDIO_PLAYING;', ''),
    (REPO, CODE, A, 983, 'LOGF("AudioIn: capture stopped; using silence\\n");', 'CloseSdlDevice(&port);'),
    # the pad haptics
    (REPO, CODE, C, 102, 'static constexpr uint64_t RETRY_US = 3000000;', ''),
    (REPO, CODE, C, 128, 'if (const char* value = std::getenv("KYTY_HAPTICS"); value != nullptr && value[0] == \'0\') {', ''),
    (REPO, CODE, C, 145, 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {', 'return false;'),
    (REPO, CODE, C, 160, 'm_device = SDL_OpenAudioDevice(name, 0, &want, &have, 0);', ''),
    (REPO, CODE, C, 170, 'return false;', '}'),
    (REPO, CODE, C, 176, 'SDL_CloseAudioDevice(m_device);', 'm_device = 0;'),
    (REPO, CODE, C, 183, 'if (pcm == nullptr || frames == 0 || channels == 0 || freq != FREQ) {', ''),
    (REPO, CODE, C, 191, 'if (m_device == 0) {', ''),
    (REPO, CODE, C, 194, 'if (m_retry_us != 0 && now - m_retry_us < RETRY_US) {', 'return;'),
    (REPO, CODE, C, 198, 'if (!OpenLocked()) {', 'return;'),
    (REPO, CODE, C, 228, 'if (SDL_QueueAudio(m_device, m_buffer.data(),', ''),
    (REPO, CODE, C, 231, 'CloseLocked();', ''),
    (REPO, CODE, C, 929, 'if (g_haptics != nullptr) {', 'g_haptics->Push(pcm, frames, channels, is_float, freq);'),
    # the AudioOut2 push
    (REPO, CODE, A2, 349, 'state.pcm_data != nullptr && AudioInternal::AudioOutHasDevice(state.audio_handle)) {', ''),
    (REPO, CODE, A2, 525, 'const bool use_device_clock =', 'blocking != 0 && audioout2_context_has_queueable_device(ctx);'),
    (REPO, CODE, A2, 532, 'if (state->queued < state->queue_depth || use_device_clock) {', ''),
    # the other SDL subsystem calls and the event loop
    (REPO, CODE, W, 542, 'case SDL_QUIT: GameEventQuit(game); break;', ''),
    (REPO, CODE, W, 748, 'case SDL_CONTROLLERDEVICEADDED:', 'case SDL_CONTROLLERDEVICEREMOVED:'),
    (REPO, CODE, W, 884, 'if (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {', ''),
    (REPO, CODE, W, 1047, 'void WindowTestMinimizeNoteGuestText(const char* text, size_t size) {', ''),
    (REPO, CODE, 'src/graphics/presentation/window/vulkanWindow.cpp', 1320, 'SDL_QuitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER);', ''),
    (REPO, CODE, 'src/launcher/src/configurationEditDialog.cpp', 176, 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) == 0) {', ''),
    (REPO, CODE, 'src/launcher/src/configurationEditDialog.cpp', 186, 'SDL_QuitSubSystem(SDL_INIT_AUDIO);', ''),
    (REPO, CODE, 'CMakeLists.txt', 369, 'set(kyty_emulator_link_libraries common Vulkan::Headers spirv-tools-opt spirv-tools SDL2-static', ''),
    (REPO, CODE, '3rdparty/CMakeLists.txt', 31, 'set(SDL_SHARED OFF CACHE BOOL "" FORCE)', 'add_subdirectory(SDL2)'),
    # SDL2: the subsystem reference counter
    (SDLREPO, SDL, S, 119, 'static Uint8 SDL_SubsystemRefCount[32];', ''),
    (SDLREPO, SDL, S, 125, 'SDL_assert((subsystem_index < 0) || (SDL_SubsystemRefCount[subsystem_index] < 255));', ''),
    (SDLREPO, SDL, S, 127, '++SDL_SubsystemRefCount[subsystem_index];', ''),
    (SDLREPO, SDL, S, 145, 'return ((subsystem_index >= 0) && (SDL_SubsystemRefCount[subsystem_index] == 0)) ? SDL_TRUE : SDL_FALSE;', ''),
    (SDLREPO, SDL, S, 152, 'if ((subsystem_index >= 0) && (SDL_SubsystemRefCount[subsystem_index] == 0)) {', 'return SDL_FALSE;'),
    (SDLREPO, SDL, S, 159, 'return (((subsystem_index >= 0) && (SDL_SubsystemRefCount[subsystem_index] == 1)) || SDL_bInMainQuit)', ''),
    (SDLREPO, SDL, S, 292, 'if (SDL_PrivateShouldInitSubsystem(SDL_INIT_AUDIO)) {', ''),
    (SDLREPO, SDL, S, 298, 'if (SDL_AudioInit(NULL) < 0) {', ''),
    (SDLREPO, SDL, S, 302, 'SDL_PrivateSubsystemRefCountIncr(SDL_INIT_AUDIO);', ''),
    (SDLREPO, SDL, S, 444, 'if (SDL_PrivateShouldQuitSubsystem(SDL_INIT_AUDIO)) {', 'SDL_AudioQuit();'),
    (SDLREPO, SDL, S, 492, 'return SDL_SubsystemRefCount[subsystem_index] ? flags : 0;', ''),
    # SDL2: device ids, the queue, the disconnect, the mixer thread
    (SDLREPO, SDL, SA, 41, 'static SDL_AudioDevice *open_devices[16];', ''),
    (SDLREPO, SDL, SA, 231, 'if ((id >= SDL_arraysize(open_devices)) || (open_devices[id] == NULL)) {', 'SDL_SetError("Invalid audio device ID");'),
    (SDLREPO, SDL, SA, 467, 'void SDL_OpenedAudioDeviceDisconnected(SDL_AudioDevice *device)', ''),
    (SDLREPO, SDL, SA, 482, 'SDL_AtomicSet(&device->enabled, 0);', ''),
    (SDLREPO, SDL, SA, 486, 'if (SDL_GetEventState(SDL_AUDIODEVICEREMOVED) == SDL_ENABLE) {', ''),
    (SDLREPO, SDL, SA, 592, 'SDL_AudioDevice *device = get_audio_device(devid);', ''),
    (SDLREPO, SDL, SA, 595, 'if (!device) {', 'return -1; /* get_audio_device() will have set the error state */'),
    (SDLREPO, SDL, SA, 605, 'rc = SDL_WriteToDataQueue(device->buffer_queue, data, len);', ''),
    (SDLREPO, SDL, SA, 635, 'if (!device) {', 'return 0;'),
    (SDLREPO, SDL, SA, 705, 'if (!device->stream && SDL_AtomicGet(&device->enabled)) {', ''),
    (SDLREPO, SDL, SA, 737, 'callback(udata, data, data_len);', ''),
    (SDLREPO, SDL, SA, 785, 'delay = ((device->spec.samples * 1000) / device->spec.freq);', 'SDL_Delay(delay);'),
    (SDLREPO, SDL, SA, 966, 'if (SDL_GetCurrentAudioDriver()) {', 'SDL_AudioQuit(); /* shutdown driver if already running. */'),
    (SDLREPO, SDL, SA, 970, 'SDL_zeroa(open_devices);', ''),
    (SDLREPO, SDL, SA, 1224, 'open_devices[device->id - 1] = NULL;', ''),
    (SDLREPO, SDL, SA, 1528, 'for (id = min_id - 1; id < SDL_arraysize(open_devices); id++) {', ''),
    (SDLREPO, SDL, SA, 1622, 'if (device && SDL_AtomicGet(&device->enabled)) {', ''),
    (SDLREPO, SDL, SA, 1682, 'close_audio_device(get_audio_device(devid));', ''),
    (SDLREPO, SDL, SA, 1698, 'for (i = 0; i < SDL_arraysize(open_devices); i++) {', 'close_audio_device(open_devices[i]);'),
    # SDL2: WASAPI device loss
    (SDLREPO, SDL, SW, 64, 'if (err == AUDCLNT_E_DEVICE_INVALIDATED) {', 'this->hidden->device_lost = SDL_TRUE;'),
    (SDLREPO, SDL, SW, 139, 'if (this->hidden->default_device_generation) {', ''),
    (SDLREPO, SDL, SW, 148, 'if (WASAPI_ActivateDevice(this, SDL_TRUE) == -1) {', 'SDL_OpenedAudioDeviceDisconnected(this);'),
    (SDLREPO, SDL, SW, 173, 'if (generation != newgen) {', ''),
    # SDL2: assertion level and version
    (SDLREPO, SDL, 'include/SDL_assert.h', 40, '#define SDL_ASSERT_LEVEL 1', ''),
    (SDLREPO, SDL, 'include/SDL_assert.h', 173, '#   define SDL_assert(condition) SDL_disabled_assert(condition)', ''),
    (SDLREPO, SDL, 'include/SDL_version.h', 60, '#define SDL_MINOR_VERSION   33', '#define SDL_PATCHLEVEL      0'),
    (SDLREPO, SDL, 'CMakeLists.txt', 565, 'if(SDL_ASSERTIONS MATCHES "^(auto|)$")', ''),
]
cache = {}
ok = 0
for repo, commit, path, line, anchor, plus1 in REFS:
    key = (repo, commit, path)
    if key not in cache:
        o = subprocess.run([GIT, '-C', repo, 'show', commit + ':' + path], capture_output=True)
        cache[key] = o.stdout.decode('utf-8', 'replace').split('\n')
    L = cache[key]
    a = L[line - 1] if line - 1 < len(L) else ''
    b = L[line] if line < len(L) else ''
    good = anchor in a and (plus1 == '' or plus1 in b)
    ok += good
    if not good:
        print('FAIL %s:%s:%d' % (commit, path, line))
        print('   line: ' + a.strip()[:160])
        print('   +1  : ' + b.strip()[:160])
print('%d of %d' % (ok, len(REFS)))
print('ALL OK' if ok == len(REFS) else 'FAILED')
