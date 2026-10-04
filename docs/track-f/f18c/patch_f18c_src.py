# F18c (HPP-539, ROADMAP s122 item 441(v)-(g)): KYTY_FIX_F8 (one owner of the SDL audio subsystem), the stand
# KYTY_TEST_AUDIOLOSS=<s>[:retry] and the AudioStat counters, plus the CMake target f8_audio_stand (item 441(d)(1)).
# Every anchor is a run of whole lines that must occur exactly once; CR kept as found; output LF/CRLF as the input.
# Usage: python patch_f18c_src.py <repo root>
import sys

root = sys.argv[1]


def load(rel):
    data = open(root + '/' + rel, 'rb').read()
    crlf = b'\r\n' in data
    return data.replace(b'\r\n', b'\n').decode('utf-8').split('\n'), crlf


def save(rel, lines, crlf):
    out = '\n'.join(lines).encode('utf-8')
    if crlf:
        out = out.replace(b'\n', b'\r\n')
    open(root + '/' + rel, 'wb').write(out)


def find(lines, anchor, rel):
    hits = [i for i in range(len(lines) - len(anchor) + 1) if lines[i:i + len(anchor)] == anchor]
    if len(hits) != 1:
        print('ANCHOR hits', len(hits), rel, anchor[0])
        sys.exit(1)
    return hits[0]


def replace(lines, anchor, new, rel):
    i = find(lines, anchor, rel)
    lines[i:i + len(anchor)] = new
    return i


def insert_after(lines, anchor, add, rel):
    i = find(lines, anchor, rel) + len(anchor)
    lines[i:i] = add
    return i


TAB = '\t'

# ---------------------------------------------------------------- audio_internal.h
rel = 'src/libs/audio_internal.h'
L, c = load(rel)
insert_after(L, ['uint32_t AudioOutOutputs(const OutputParam* params, uint32_t num, bool blocking = true);'], [
    '',
    '// Track F, F8 (ROADMAP s122 item 441(v)): the emulator call sites of SDL_InitSubSystem / SDL_QuitSubSystem with',
    '// SDL_INIT_AUDIO (AudioOut ports, AudioIn ports, pad haptics). KYTY_FIX_F8 unset or 0: the same SDL calls as before',
    '// (each init counted). KYTY_FIX_F8=1: init goes through SdlAudioAcquire, quit does nothing - the SDL reference count of',
    '// the audio subsystem stays 1 for the life of the process. Read once per process; "FixF8: mode=1" once at 1.',
    'int  SdlAudioSubsystemInit();',
    'void SdlAudioSubsystemQuit();',
    '// SDL_InitSubSystem(SDL_INIT_AUDIO) at most once successfully per process (own mutex; a failure is not remembered).',
    'int SdlAudioAcquire();',
    '// Counters of item 441(g): real SDL_InitSubSystem(SDL_INIT_AUDIO) calls of the emulator (both modes) and',
    '// SdlAudioAcquire calls; AudioStatForce makes every output port print its AudioStat line on its next push.',
    'uint64_t SdlAudioInitCalls();',
    'uint64_t SdlAudioAcquireCalls();',
    'void     AudioStatForce();',
], rel)
save(rel, L, c)
print('PATCH OK', rel)

# ---------------------------------------------------------------- audio.cpp
rel = 'src/libs/audio.cpp'
L, c = load(rel)
replace(L, [TAB + 'static bool            QueueSdlAudio(PortOut* port, const void* data, bool blocking);'],
        [TAB + 'static bool            QueueSdlAudio(PortOut* port, int port_id, const void* data, bool blocking);'], rel)

insert_after(L, ['namespace AudioInternal {', ''], [
    '// Track F, F8 (ROADMAP s122 item 441(v)): SDL2 counts the users of a subsystem in a Uint8 (SDL.c:119); every',
    '// SDL_InitSubSystem(SDL_INIT_AUDIO) without a matching quit adds 1, the 256th wraps the count to 0 and the next init',
    '// runs SDL_AudioInit, which closes every open device (SDL_audio.c:966) while the ports keep their ids.',
    'static std::mutex            g_sdl_audio_mutex;',
    'static bool                  g_sdl_audio_acquired = false; // Guarded by g_sdl_audio_mutex.',
    'static std::atomic<uint64_t> g_sdl_audio_init_calls {0};',
    'static std::atomic<uint64_t> g_sdl_audio_acq_calls {0};',
    'static std::atomic<uint32_t> g_audio_stat_gen {0};',
    '',
    'static bool FixF8Enabled() {',
    TAB + 'static const bool enabled = [] {',
    TAB + TAB + 'const bool on = Common::EnvValueOn(std::getenv("KYTY_FIX_F8"));',
    TAB + TAB + 'if (on) {',
    TAB + TAB + TAB + 'LOGF("FixF8: mode=1\\n");',
    TAB + TAB + '}',
    TAB + TAB + 'return on;',
    TAB + '}();',
    TAB + 'return enabled;',
    '}',
    '',
    'int SdlAudioAcquire() {',
    TAB + 'g_sdl_audio_acq_calls.fetch_add(1, std::memory_order_relaxed);',
    TAB + 'std::lock_guard<std::mutex> lock(g_sdl_audio_mutex);',
    TAB + 'if (g_sdl_audio_acquired) {',
    TAB + TAB + 'return 0;',
    TAB + '}',
    TAB + 'g_sdl_audio_init_calls.fetch_add(1, std::memory_order_relaxed);',
    TAB + 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {',
    TAB + TAB + 'return -1;',
    TAB + '}',
    TAB + 'g_sdl_audio_acquired = true;',
    TAB + 'return 0;',
    '}',
    '',
    'int SdlAudioSubsystemInit() {',
    TAB + 'if (FixF8Enabled()) {',
    TAB + TAB + 'return SdlAudioAcquire();',
    TAB + '}',
    TAB + 'g_sdl_audio_init_calls.fetch_add(1, std::memory_order_relaxed);',
    TAB + 'return SDL_InitSubSystem(SDL_INIT_AUDIO);',
    '}',
    '',
    'void SdlAudioSubsystemQuit() {',
    TAB + 'if (FixF8Enabled()) {',
    TAB + TAB + 'return;',
    TAB + '}',
    TAB + 'SDL_QuitSubSystem(SDL_INIT_AUDIO);',
    '}',
    '',
    'uint64_t SdlAudioInitCalls() {',
    TAB + 'return g_sdl_audio_init_calls.load(std::memory_order_relaxed);',
    '}',
    '',
    'uint64_t SdlAudioAcquireCalls() {',
    TAB + 'return g_sdl_audio_acq_calls.load(std::memory_order_relaxed);',
    '}',
    '',
    'void AudioStatForce() {',
    TAB + 'g_audio_stat_gen.fetch_add(1, std::memory_order_relaxed);',
    '}',
    '',
    '// AudioStat (item 441(g)): with KYTY_AV_TRACE=1 or the stand KYTY_TEST_AUDIOLOSS on, one line per output port with a',
    '// device, at most once a second of process time and on the next push after AudioStatForce. Counters only grow.',
    'struct AudioStatPort {',
    TAB + 'std::atomic<uint64_t> pushes {0};',
    TAB + 'std::atomic<uint64_t> q_fail {0};',
    TAB + 'std::atomic<uint64_t> last_us {0};',
    TAB + 'std::atomic<uint32_t> gen {0};',
    '};',
    '',
    'static AudioStatPort g_audio_stat[OUT_PORTS_MAX];',
    '',
    'static void AudioStatPush(int port_id, SDL_AudioDeviceID dev, bool failed) {',
    TAB + 'if (port_id < 0 || port_id >= OUT_PORTS_MAX) {',
    TAB + TAB + 'return;',
    TAB + '}',
    TAB + 'auto&          s      = g_audio_stat[port_id];',
    TAB + 'const uint64_t pushes = s.pushes.fetch_add(1, std::memory_order_relaxed) + 1;',
    TAB + 'const uint64_t q_fail = failed ? s.q_fail.fetch_add(1, std::memory_order_relaxed) + 1',
    TAB + '                               : s.q_fail.load(std::memory_order_relaxed);',
    TAB + 'const uint64_t now    = LibKernel::KernelGetProcessTime();',
    TAB + 'const uint32_t gen    = g_audio_stat_gen.load(std::memory_order_relaxed);',
    TAB + 'uint64_t       last   = s.last_us.load(std::memory_order_relaxed);',
    TAB + 'if (s.gen.load(std::memory_order_relaxed) == gen && last != 0 && now < last + 1000000) {',
    TAB + TAB + 'return;',
    TAB + '}',
    TAB + '// One printer per interval: a concurrent push of the same port that lost the exchange stays silent.',
    TAB + 'if (!s.last_us.compare_exchange_strong(last, now != 0 ? now : 1, std::memory_order_relaxed)) {',
    TAB + TAB + 'return;',
    TAB + '}',
    TAB + 's.gen.store(gen, std::memory_order_relaxed);',
    TAB + 'LOGF("AudioStat: t_us=%" PRIu64 " port=%d dev=%u status=%d queued=%u pushes=%" PRIu64 " q_fail=%" PRIu64',
    TAB + '     " init_calls=%" PRIu64 " acq=%" PRIu64 "\\n",',
    TAB + '     now, port_id, static_cast<uint32_t>(dev), static_cast<int>(SDL_GetAudioDeviceStatus(dev)),',
    TAB + '     SDL_GetQueuedAudioSize(dev), pushes, q_fail, SdlAudioInitCalls(), SdlAudioAcquireCalls());',
    '}',
    '',
], rel)

# C1 (item 441(v)): AudioOut port open.
replace(L, [TAB + 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {',
            TAB + TAB + 'LOGF("AudioOut: SDL audio init failed: %s\\n", SDL_GetError());'],
        [TAB + 'if (AudioInternal::SdlAudioSubsystemInit() < 0) {',
         TAB + TAB + 'LOGF("AudioOut: SDL audio init failed: %s\\n", SDL_GetError());'], rel)

replace(L, ['bool Audio::QueueSdlAudio(PortOut* port, const void* data, bool blocking) {'],
        ['bool Audio::QueueSdlAudio(PortOut* port, int port_id, const void* data, bool blocking) {'], rel)

insert_after(L, [TAB + 'static const bool av_trace = Common::EnvFlagOn("KYTY_AV_TRACE");'], [
    TAB + 'static const bool audio_stat = av_trace || Controller::TestAudioLossOn();',
], rel)

replace(L, [TAB + 'if (SDL_QueueAudio(port->audio_device, queue_data, queue_size) < 0) {',
            TAB + TAB + 'LOGF("AudioOut: SDL_QueueAudio failed: %s\\n", SDL_GetError());',
            TAB + TAB + 'return false;',
            TAB + '}'],
        [TAB + 'if (SDL_QueueAudio(port->audio_device, queue_data, queue_size) < 0) {',
         TAB + TAB + 'LOGF("AudioOut: SDL_QueueAudio failed: %s\\n", SDL_GetError());',
         TAB + TAB + 'if (audio_stat) {',
         TAB + TAB + TAB + 'AudioInternal::AudioStatPush(port_id, port->audio_device, true);',
         TAB + TAB + '}',
         TAB + TAB + 'return false;',
         TAB + '}',
         TAB + 'if (audio_stat) {',
         TAB + TAB + 'AudioInternal::AudioStatPush(port_id, port->audio_device, false);',
         TAB + '}'], rel)

replace(L, [TAB + TAB + 'QueueSdlAudio(&port, params[i].data, blocking);'],
        [TAB + TAB + 'QueueSdlAudio(&port, params[i].handle.GetId(), params[i].data, blocking);'], rel)

# C3 (item 441(v)): AudioIn port open, and the two quits of the input port.
replace(L, [TAB + 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {',
            TAB + TAB + 'LOGF("AudioIn: SDL init failed: %s\\n", SDL_GetError());'],
        [TAB + 'if (AudioInternal::SdlAudioSubsystemInit() < 0) {',
         TAB + TAB + 'LOGF("AudioIn: SDL init failed: %s\\n", SDL_GetError());'], rel)
replace(L, [TAB + TAB + 'LOGF("AudioIn: cannot open \'%s\': %s; using silence\\n", name.c_str(), SDL_GetError());',
            TAB + TAB + 'SDL_QuitSubSystem(SDL_INIT_AUDIO);'],
        [TAB + TAB + 'LOGF("AudioIn: cannot open \'%s\': %s; using silence\\n", name.c_str(), SDL_GetError());',
         TAB + TAB + 'AudioInternal::SdlAudioSubsystemQuit();'], rel)
replace(L, [TAB + TAB + 'SDL_CloseAudioDevice(port->audio_device);',
            TAB + TAB + 'SDL_QuitSubSystem(SDL_INIT_AUDIO);'],
        [TAB + TAB + 'SDL_CloseAudioDevice(port->audio_device);',
         TAB + TAB + 'AudioInternal::SdlAudioSubsystemQuit();'], rel)
save(rel, L, c)
print('PATCH OK', rel)

# ---------------------------------------------------------------- controller.h
rel = 'src/libs/controller.h'
L, c = load(rel)
insert_after(L, ['void PushHapticsPcm(const void* pcm, uint32_t frames, uint32_t channels, bool is_float,',
                 '                    uint32_t freq);'], [
    '// Track F, F8 stand (ROADMAP s122 item 441(g)): KYTY_TEST_AUDIOLOSS is set and valid (read once in Initialize).',
    'bool TestAudioLossOn();',
], rel)
save(rel, L, c)
print('PATCH OK', rel)

# ---------------------------------------------------------------- controller.cpp
rel = 'src/libs/controller.cpp'
L, c = load(rel)
insert_after(L, ['#include "kernel/pthread.h"'], ['#include "libs/audio_internal.h"'], rel)
insert_after(L, ['#include <chrono>'], ['#include <cinttypes>'], rel)

replace(L, [TAB + 'static uint64_t NowUs();',
            TAB + 'bool            OpenLocked();',
            TAB + 'void            CloseLocked();'],
        [TAB + 'static uint64_t NowUs();',
         TAB + 'bool            OpenLocked();',
         TAB + 'void            CloseLocked();',
         TAB + 'uint64_t        TestAudioLossRetryUsLocked();',
         '',
         TAB + '// Stand KYTY_TEST_AUDIOLOSS (item 441(g)), guarded by m_mutex.',
         TAB + 'enum class TestState { Idle, Armed, Firing, DonePending, Done };',
         TAB + 'static constexpr uint32_t TEST_ATTEMPTS = 300;',
         TAB + 'TestState                 m_test_state    = TestState::Idle;',
         TAB + 'uint64_t                  m_test_armed_us = 0;',
         TAB + 'uint32_t                  m_test_attempts = 0;'], rel)

insert_after(L, ['static HapticsOutput* g_haptics = nullptr;'], [
    '',
    '// Track F, F8 stand (ROADMAP s122 item 441(g)): KYTY_TEST_AUDIOLOSS=<s>[:retry] - stand only, off when unset. Armed on',
    '// the first push to the vibration port with no pad device; <s> seconds of process time later the retry interval of',
    '// the pad device open (RETRY_US) is 0 for exactly 300 attempts (every push is an attempt), then RETRY_US again: the',
    '// same site and thread as the natural path, faster. Written once by HapticsOutput::Start (Controller::Initialize,',
    '// before the guest threads exist), read only afterwards.',
    'struct TestAudioLossConfig {',
    TAB + 'bool     on       = false;',
    TAB + 'uint64_t delay_us = 0;',
    '};',
    '',
    'static TestAudioLossConfig g_test_audioloss;',
    '',
    'static void ReadTestAudioLoss() {',
    TAB + 'const char* value = std::getenv("KYTY_TEST_AUDIOLOSS");',
    TAB + 'if (value == nullptr || value[0] == \'\\0\') {',
    TAB + TAB + 'return;',
    TAB + '}',
    TAB + 'char*        end     = nullptr;',
    TAB + 'const double delay_s = std::strtod(value, &end);',
    TAB + 'const bool   ok      = value[0] >= \'0\' && value[0] <= \'9\' && end != value && std::isfinite(delay_s) &&',
    TAB + '                     delay_s <= 86400.0 && (end[0] == \'\\0\' || std::strcmp(end, ":retry") == 0);',
    TAB + 'if (!ok) {',
    TAB + TAB + 'LOGF("TestAudioLoss: config invalid value=\\"%s\\" (expected <s>[:retry]), stand off\\n", value);',
    TAB + TAB + 'return;',
    TAB + '}',
    TAB + 'g_test_audioloss.on       = true;',
    TAB + 'g_test_audioloss.delay_us = static_cast<uint64_t>(delay_s * 1000000.0);',
    TAB + 'LOGF("TestAudioLoss: config on delay_s=%g mode=retry\\n", delay_s);',
    '}',
    '',
    'bool TestAudioLossOn() {',
    TAB + 'return g_test_audioloss.on;',
    '}',
], rel)

replace(L, ['void HapticsOutput::Start() {',
            TAB + 'if (const char* value = std::getenv("KYTY_HAPTICS"); value != nullptr && value[0] == \'0\') {'],
        ['void HapticsOutput::Start() {',
         TAB + 'ReadTestAudioLoss();',
         TAB + 'if (const char* value = std::getenv("KYTY_HAPTICS"); value != nullptr && value[0] == \'0\') {'], rel)

# C2 (item 441(v)): pad haptics device open.
replace(L, ['bool HapticsOutput::OpenLocked() {',
            TAB + 'if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {',
            TAB + TAB + 'return false;',
            TAB + '}'],
        ['bool HapticsOutput::OpenLocked() {',
         TAB + 'if (Audio::AudioInternal::SdlAudioSubsystemInit() < 0) {',
         TAB + TAB + 'return false;',
         TAB + '}'], rel)

insert_after(L, ['void HapticsOutput::CloseLocked() {',
                 TAB + 'if (m_device != 0) {',
                 TAB + TAB + 'SDL_ClearQueuedAudio(m_device);',
                 TAB + TAB + 'SDL_CloseAudioDevice(m_device);',
                 TAB + TAB + 'm_device = 0;',
                 TAB + '}',
                 '}'], [
    '',
    '// Stand step of one push with no pad device; the caller holds m_mutex. Returns the retry interval for this push. In',
    '// Firing every call is an attempt: with a zero interval the check in Push never returns before OpenLocked.',
    'uint64_t HapticsOutput::TestAudioLossRetryUsLocked() {',
    TAB + 'const uint64_t t = LibKernel::KernelGetProcessTime();',
    TAB + 'switch (m_test_state) {',
    TAB + TAB + 'case TestState::Idle:',
    TAB + TAB + TAB + 'm_test_state    = TestState::Armed;',
    TAB + TAB + TAB + 'm_test_armed_us = t;',
    TAB + TAB + TAB + 'LOGF("TestAudioLoss: armed t_us=%" PRIu64 "\\n", t);',
    TAB + TAB + TAB + 'return RETRY_US;',
    TAB + TAB + 'case TestState::Armed:',
    TAB + TAB + TAB + 'if (t - m_test_armed_us < g_test_audioloss.delay_us) {',
    TAB + TAB + TAB + TAB + 'return RETRY_US;',
    TAB + TAB + TAB + '}',
    TAB + TAB + TAB + 'm_test_state = TestState::Firing;',
    TAB + TAB + TAB + 'LOGF("TestAudioLoss: fire t_us=%" PRIu64 "\\n", t);',
    TAB + TAB + TAB + 'Audio::AudioInternal::AudioStatForce();',
    TAB + TAB + TAB + '[[fallthrough]];',
    TAB + TAB + 'case TestState::Firing:',
    TAB + TAB + TAB + 'if (++m_test_attempts == TEST_ATTEMPTS) {',
    TAB + TAB + TAB + TAB + 'm_test_state = TestState::DonePending;',
    TAB + TAB + TAB + '}',
    TAB + TAB + TAB + 'return 0;',
    TAB + TAB + 'case TestState::DonePending:',
    TAB + TAB + TAB + '// Logged on the push after the 300th attempt, so the line follows its SDL call.',
    TAB + TAB + TAB + 'm_test_state = TestState::Done;',
    TAB + TAB + TAB + 'LOGF("TestAudioLoss: done attempts=%u t_us=%" PRIu64 "\\n", m_test_attempts, t);',
    TAB + TAB + TAB + 'Audio::AudioInternal::AudioStatForce();',
    TAB + TAB + TAB + 'return RETRY_US;',
    TAB + TAB + 'case TestState::Done: break;',
    TAB + '}',
    TAB + 'return RETRY_US;',
    '}',
], rel)

replace(L, [TAB + TAB + 'const auto now = NowUs();',
            TAB + TAB + 'if (m_retry_us != 0 && now - m_retry_us < RETRY_US) {',
            TAB + TAB + TAB + 'return;',
            TAB + TAB + '}'],
        [TAB + TAB + 'const auto     now      = NowUs();',
         TAB + TAB + 'const uint64_t retry_us = g_test_audioloss.on ? TestAudioLossRetryUsLocked() : RETRY_US;',
         TAB + TAB + 'if (m_retry_us != 0 && now - m_retry_us < retry_us) {',
         TAB + TAB + TAB + 'return;',
         TAB + TAB + '}'], rel)
save(rel, L, c)
print('PATCH OK', rel)

# ---------------------------------------------------------------- CMakeLists.txt
rel = 'CMakeLists.txt'
L, c = load(rel)
insert_after(L, ['add_kyty_full_emulator_test(audio_propagation_tests', TAB + '"${KYTY_TESTS_DIR}/AudioPropagationTests.cpp")'], [
    '',
    '# Track F, F8 SDL audio subsystem stand (F18c; ROADMAP s122 item 441(d)(1)): run by docs/track-f/f18c/run_stand_f18c.py,',
    '# not by ctest.',
    'add_kyty_full_emulator_test(f8_audio_stand',
    TAB + '"${KYTY_TESTS_DIR}/F8AudioStand.cpp")',
], rel)
save(rel, L, c)
print('PATCH OK', rel)
print('ALL PATCHED')
