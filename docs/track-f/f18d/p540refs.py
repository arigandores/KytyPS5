# F18d (HPP-540): reference map of the review - every <commit>:<path>:<line> with its anchor and the +1 line (rule 24(1)).
import subprocess, sys

REPO = 'C:/kyty/KytyPS5'
SDL = 'C:/kyty/KytyPS5/3rdparty/SDL2'
REFS = [
    (REPO, '10a4800b', 'src/libs/audio.cpp', 291, 'static bool FixF8Enabled() {', 'static const bool enabled = [] {'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 302, 'int SdlAudioAcquire() {', 'g_sdl_audio_acq_calls.fetch_add(1, std::memory_order_relaxed);'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 316, 'int SdlAudioSubsystemInit() {', 'if (FixF8Enabled()) {'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 324, 'void SdlAudioSubsystemQuit() {', 'if (FixF8Enabled()) {'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 354, 'static void AudioStatPush(int port_id, SDL_AudioDeviceID dev, bool failed) {', 'if (port_id < 0 || port_id >= OUT_PORTS_MAX) {'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 532, 'if (AudioInternal::SdlAudioSubsystemInit() < 0) {', 'LOGF("AudioOut: SDL audio init failed: %s\\n", SDL_GetError());'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 710, 'static const bool audio_stat = av_trace || Controller::TestAudioLossOn();', 'const auto        av_queued_before = SDL_GetQueuedAudioSize(port->audio_device);'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 922, 'QueueSdlAudio(&port, params[i].handle.GetId(), params[i].data, blocking);', '}'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 937, 'if (AudioInternal::SdlAudioSubsystemInit() < 0) {', 'LOGF("AudioIn: SDL init failed: %s\\n", SDL_GetError());'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 950, 'AudioInternal::SdlAudioSubsystemQuit();', 'return;'),
    (REPO, '10a4800b', 'src/libs/audio.cpp', 959, 'AudioInternal::SdlAudioSubsystemQuit();', 'port->audio_device = 0;'),
    (REPO, '10a4800b', 'src/libs/controller.cpp', 172, 'ReadTestAudioLoss();', 'if (const char* value = std::getenv("KYTY_HAPTICS"); value != nullptr && value[0] == \'0\') {'),
    (REPO, '10a4800b', 'src/libs/controller.cpp', 190, 'if (Audio::AudioInternal::SdlAudioSubsystemInit() < 0) {', 'return false;'),
    (REPO, '10a4800b', 'src/libs/controller.cpp', 228, 'uint64_t HapticsOutput::TestAudioLossRetryUsLocked() {', 'const uint64_t t = LibKernel::KernelGetProcessTime();'),
    (REPO, '10a4800b', 'src/libs/controller.cpp', 273, 'const uint64_t retry_us = g_test_audioloss.on ? TestAudioLossRetryUsLocked() : RETRY_US;', 'if (m_retry_us != 0 && now - m_retry_us < retry_us) {'),
    (REPO, '10a4800b', 'src/emulator.cpp', 165, 'subsystems.Initialize<Libs::Controller::Lifecycle>();', 'subsystems.Initialize<Libs::Audio::Lifecycle>();'),
    (REPO, '10a4800b', 'src/graphics/presentation/window/window.cpp', 884, 'if (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {', None),
    (REPO, '10a4800b', 'src/launcher/src/configurationEditDialog.cpp', 176, 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) == 0) {', None),
    (REPO, '10a4800b', 'tests/F8AudioStand.cpp', 131, 'if (mode == "iii") {', 'std::atomic<int>  ready {0};'),
    (SDL, '4b69833b', 'src/SDL.c', 292, 'if (SDL_PrivateShouldInitSubsystem(SDL_INIT_AUDIO)) {', '/* audio implies events */'),
    (SDL, '4b69833b', 'src/SDL.c', 302, 'SDL_PrivateSubsystemRefCountIncr(SDL_INIT_AUDIO);', 'flags_initialized |= SDL_INIT_AUDIO;'),
]
ok = 0
for repo, c, path, line, anchor, nxt in REFS:
    t = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (c, path)], capture_output=True).stdout.decode('utf-8', 'replace')
    L = t.split('\n')
    a = L[line - 1].strip() if line - 1 < len(L) else None
    n = L[line].strip() if line < len(L) else None
    good = a == anchor and (nxt is None or n == nxt)
    ok += good
    print('%s %s:%s:%d | %s | +1 %s' % ('OK ' if good else 'BAD', c, path, line, a, n))
print('refs %d of %d' % (ok, len(REFS)))
print('ALL OK' if ok == len(REFS) else 'FAILED')
sys.exit(0 if ok == len(REFS) else 1)
