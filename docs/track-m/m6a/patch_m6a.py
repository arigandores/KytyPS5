"""M6a (HPP-848, ROADMAP s122 item 767(i), (v), (z)): measurement-only knob KYTY_DIAG_M5W2 and the signature lines
without a knob. Usage: python patch_m6a.py <repo root>   (the worktree C:/kyty/m657/m6a/wt or C:/kyty/KytyPS5).
Whole-line anchors, each must occur exactly once; CR is stripped before the search and restored after (the files are LF
in git); writes with write_bytes. Lock and STOP checked first. Prints one line per edit and ALL OK / FAIL."""
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/m657/STOP'):
    print('LOCK or STOP')
    sys.exit(3)

ROOT = sys.argv[1]
SRC = os.path.join(ROOT, 'src')
DRAFT = 'C:/kyty/m657/m6a/draft'
NL = chr(10)
ok = True


def lines_of(block):
    return block.split(NL)


def edit(rel, pairs):
    """pairs: (anchor block, replacement block); the anchor block is a list of whole lines that must occur once."""
    global ok
    path = os.path.join(SRC, rel)
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = NL + raw.decode('utf-8').replace('\r\n', NL)
    for anchor, repl in pairs:
        a = NL.join(anchor)
        n = text.count(NL + a + NL)
        if n != 1:
            print('FAIL %s anchor x%d: %s' % (rel, n, anchor[0][:70]))
            ok = False
            continue
        text = text.replace(NL + a + NL, NL + NL.join(repl) + NL, 1)
        print('OK   %s: %s' % (rel, anchor[0].strip()[:70]))
    text = text[1:]
    out = text.replace(NL, '\r\n') if crlf else text
    open(path, 'wb').write(out.encode('utf-8'))


def add_file(rel, draft):
    path = os.path.join(SRC, rel)
    if os.path.exists(path):
        print('FAIL %s exists' % rel)
        return False
    data = open(os.path.join(DRAFT, draft), 'rb').read().replace(b'\r\n', b'\n')
    open(path, 'wb').write(data)
    print('OK   new %s (%d bytes)' % (rel, len(data)))
    return True


ok &= add_file('libs/diagM5W2.h', 'diagM5W2.h')
ok &= add_file('libs/diagM5W2.cpp', 'diagM5W2.cpp')

INC = '#include "libs/diagM5W2.h" // Track M, M6a (KYTY_DIAG_M5W2)'
TAG = 'Track M, M6a (HPP-848, ROADMAP s122 item 767(i))'

# ---------------------------------------------------------------- T125 libAudio2.cpp
edit('libs/libAudio2.cpp', [
    (['#include "libs/audio_internal.h"'], ['#include "libs/audio_internal.h"', INC]),
    (['\tg_audioout2_port_mutex.Lock();',
      '\tfor (const auto& state: g_audioout2_ports) {',
      '\t\tif (state.used && state.context == ctx && state.audio_handle > 0 &&',
      '\t\t    state.pcm_data != nullptr && params.size() < AudioInternal::OUT_PORTS_MAX) {'],
     ['\tg_audioout2_port_mutex.Lock();',
      '\t// ' + TAG + ', T125: measurement only - at this queued push every port',
      '\t// of the context with PCM (object ports and the others, the live control), object ports without PCM; no decision.',
      '\tif (DiagM5W2::On()) [[unlikely]] {',
      '\t\tfor (const auto& state: g_audioout2_ports) {',
      '\t\t\tif (!state.used || state.context != ctx) {',
      '\t\t\t\tcontinue;',
      '\t\t\t}',
      '\t\t\tconst bool object_port = audioout2_port_type_is_object(state.port_type);',
      '\t\t\tif (state.pcm_data != nullptr) {',
      '\t\t\t\tDiagM5W2::NoteAudioPort(object_port, state.pcm_data, state.data_format, state.samples_num);',
      '\t\t\t} else if (object_port) {',
      '\t\t\t\tDiagM5W2::NoteAudioObjectNoPcm();',
      '\t\t\t}',
      '\t\t}',
      '\t}',
      '\tfor (const auto& state: g_audioout2_ports) {',
      '\t\tif (state.used && state.context == ctx && state.audio_handle > 0 &&',
      '\t\t    state.pcm_data != nullptr && params.size() < AudioInternal::OUT_PORTS_MAX) {']),
    (['\tg_audioout2_port_mutex.Unlock();',
      '',
      '\tif (params.empty()) {',
      '\t\treturn;',
      '\t}'],
     ['\tg_audioout2_port_mutex.Unlock();',
      '\tif (DiagM5W2::On()) [[unlikely]] {',
      '\t\tDiagM5W2::NoteAudioPush(); // M6a: the periodic "M5W2Stat:" line every 4096 queued pushes',
      '\t}',
      '',
      '\tif (params.empty()) {',
      '\t\treturn;',
      '\t}']),
])

# ---------------------------------------------------------------- exit line emulator.cpp
EXIT_OLD = '\tLibs::Graphics::FixF20::PrintExitStat(); // Track F, F42a: "FixF20Stat: when=exit" (KYTY_FIX_F20=1 only)'
EXIT_NEW = '\tLibs::DiagM5W2::PrintExitStat(); // Track M, M6a: "M5W2Stat: when=exit" (KYTY_DIAG_M5W2=1 only)'
edit('emulator.cpp', [
    (['#include "graphics/host_gpu/renderer/pipeline/fixF20.h"'],
     ['#include "graphics/host_gpu/renderer/pipeline/fixF20.h"', INC]),
])
# The two exit lines are not unique: both get the M6a line after them.
path = os.path.join(SRC, 'emulator.cpp')
t = open(path, 'rb').read().decode('utf-8')
TAB = chr(9)
n = t.count(NL + EXIT_OLD + NL) + t.count(NL + TAB + EXIT_OLD + NL)
if n == 2:
    t = t.replace(NL + TAB + EXIT_OLD + NL, NL + TAB + EXIT_OLD + NL + TAB + EXIT_NEW + NL)
    t = t.replace(NL + EXIT_OLD + NL, NL + EXIT_OLD + NL + EXIT_NEW + NL)
    open(path, 'wb').write(t.encode('utf-8'))
    print('OK   emulator.cpp: exit line x2')
else:
    print('FAIL emulator.cpp exit anchor x%d' % n)
    ok = False

# ---------------------------------------------------------------- T313 + T179, T188 textureCache.cpp
edit('graphics/host_gpu/renderer/cache/textureCache.cpp', [
    (['#include "graphics/host_gpu/renderer/cache/textureCache.h"'],
     ['#include "graphics/host_gpu/renderer/cache/textureCache.h"', INC]),
    (['\tClearImage(command, selected, image.backing.format,',
      '\t           {aspect, 0, image.info.resources.levels, 0, image.info.TransferLayers()}, clear);',
      '\tg_last_clear_outcome = "ok";'],
     ['\t// ' + TAG + ', T313 + T179: measurement only - an accepted colour DWORD',
      '\t// fill by vk::Format and whether our decode differs from upstream 57c97ebd8 / 89792a3bc; no decision.',
      '\tif (aspect == vk::ImageAspectFlagBits::eColor && DiagM5W2::On()) [[unlikely]] {',
      '\t\tDiagM5W2::NoteClearDword(static_cast<uint32_t>(image.info.pixel_format), packed_clear);',
      '\t}',
      '\tClearImage(command, selected, image.backing.format,',
      '\t           {aspect, 0, image.info.resources.levels, 0, image.info.TransferLayers()}, clear);',
      '\tg_last_clear_outcome = "ok";']),
    (['void TextureCache::InvalidateMemoryFromGPU(uint64_t address, uint64_t size) {',
      '\tif (!GuestRange {address, size}.Valid()) {',
      '\t\treturn;',
      '\t}',
      '\tstd::scoped_lock lock {m_lock};'],
     ['void TextureCache::InvalidateMemoryFromGPU(uint64_t address, uint64_t size) {',
      '\tif (!GuestRange {address, size}.Valid()) {',
      '\t\treturn;',
      '\t}',
      '\tstd::scoped_lock lock {m_lock};',
      '\t// ' + TAG + ', T188: measurement only - the call, then every image the',
      '\t// loop below invalidates (IsGpuModified, the write covers the image or not, at its base or not); no decision.',
      '\tconst bool diag_m5w2 = DiagM5W2::On();',
      '\tif (diag_m5w2) [[unlikely]] {',
      '\t\tDiagM5W2::NoteInvalidateCall();',
      '\t}']),
    (['\t\tTraceWatchedImage("gpu-invalidate", image, address, size);'],
     ['\t\tTraceWatchedImage("gpu-invalidate", image, address, size);',
      '\t\tif (diag_m5w2) [[unlikely]] {',
      '\t\t\tDiagM5W2::NoteInvalidateImage(image.IsGpuModified(), image.info.data.address, image.info.data.size, address,',
      '\t\t\t                              size);',
      '\t\t}']),
])

# ---------------------------------------------------------------- T021 imageView.cpp
edit('graphics/host_gpu/renderer/image/imageView.cpp', [
    (['#include "graphics/host_gpu/renderer/image/image.h"'],
     ['#include "graphics/host_gpu/renderer/image/image.h"', INC]),
    (['\tviews.push_back({normalized, view});'],
     ['\t// ' + TAG + ', T021: measurement only - a created view with min_lod > 0',
      '\t// and whether the clamp level_count - 1 above cut an absolute minLod (base_level > 0); no decision.',
      '\tif (DiagM5W2::On()) [[unlikely]] {',
      '\t\tDiagM5W2::NoteMinLodView(normalized.min_lod, normalized.base_level, normalized.level_count);',
      '\t}',
      '\tviews.push_back({normalized, view});']),
])

# ---------------------------------------------------------------- T258 descriptors.cpp
edit('graphics/host_gpu/renderer/pipeline/descriptors.cpp', [
    (['#include "graphics/host_gpu/renderer/shadowResolve.h"'],
     ['#include "graphics/host_gpu/renderer/shadowResolve.h"', INC]),
    (['\tconst Common::B2Reuse::Entry* reuse_hit = b2r_hit != nullptr ? b2r_hit : bln_hit_p; // knob "bindlean" (s.3.2)'],
     ['\t// ' + TAG + ', T258: measurement only - a raw read binding (neither',
      '\t// written nor formatted) and whether an image of the GPU (base == address, SafeToDownload) lies at its base: the',
      '\t// buffer is then read without the image content (ObtainBuffer syncs from images only for texel buffers); no decision.',
      '\tif (!resource.written && !resource.formatted && DiagM5W2::On()) [[unlikely]] {',
      '\t\tDiagM5W2::NoteRawRead(static_cast<bool>(context.GetTextureCache().FindImageFromRange(address, size)));',
      '\t}',
      '\tconst Common::B2Reuse::Entry* reuse_hit = b2r_hit != nullptr ? b2r_hit : bln_hit_p; // knob "bindlean" (s.3.2)']),
])

# ---------------------------------------------------------------- T031 guestPrintf.cpp (no knob, once per process)
edit('libs/guestPrintf.cpp', [
    (['#include <cmath>'], ['#include <atomic>', '#include <cmath>']),
    (['\t\t\t\tprecision      = prec > 0 ? static_cast<unsigned int>(prec) : 0U;'],
     ['\t\t\t\tprecision      = prec > 0 ? static_cast<unsigned int>(prec) : 0U;',
      '\t\t\t\t// Track M, M6a (HPP-848, ROADMAP s122 item 767(v), T031): signature line without a knob, once per',
      '\t\t\t\t// process - a negative "*" precision (C11: as if omitted; here precision 0). No decision changes.',
      '\t\t\t\tif (prec < 0) {',
      '\t\t\t\t\tstatic std::atomic<bool> negative_precision_logged {false};',
      '\t\t\t\t\tif (!negative_precision_logged.exchange(true)) {',
      '\t\t\t\t\t\tLOGF("GuestPrintf: negative precision prec=%d\\n", prec);',
      '\t\t\t\t\t}',
      '\t\t\t\t}']),
])

# ---------------------------------------------------------------- T309 libAmpr.cpp (no knob, limit 20 each)
edit('libs/libAmpr.cpp', [
    (['#include <array>'], ['#include <array>', '#include <atomic>', '#include <cinttypes>']),
    (['static bool EnsureCommandBufferRecordSpace(uint64_t command_buffer, CommandBufferState* state,',
      '                                           uint64_t record_size) {',
      '\tif (state == nullptr || record_size == 0 ||',
      '\t    !ValidateCommandBufferHeader(command_buffer, state) || state->buffer == 0 ||',
      '\t    record_size > state->size || state->write_offset > state->size - record_size) {',
      '\t\treturn false;',
      '\t}',
      '',
      '\treturn ValidateCommandBufferBacking(state);',
      '}'],
     ['// Track M, M6a (HPP-848, ROADMAP s122 item 767(z), T309): signature lines without a knob, at most 20 each per',
      '// process - a refused record (EnsureCommandBufferRecordSpace) and a refused WriteAddress (AppendWriteAddressRecord)',
      '// returned false / EBUSY without a line before. No decision changes.',
      'static void LogRecordSpaceRefused(const char* why, uint64_t command_buffer, const CommandBufferState* state,',
      '                                  uint64_t record_size) {',
      '\tstatic std::atomic<uint32_t> logged {0};',
      '\tconst uint32_t n = logged.fetch_add(1, std::memory_order_relaxed) + 1;',
      '\tif (n > 20) {',
      '\t\treturn;',
      '\t}',
      '\tLOGF("AmprRecordSpace: refused why=%s cb=0x%016" PRIx64 " record_size=0x%" PRIx64 " write_offset=0x%" PRIx64',
      '\t     " size=0x%" PRIx64 " n=%u\\n",',
      '\t     why, command_buffer, record_size, state != nullptr ? state->write_offset : 0,',
      '\t     state != nullptr ? state->size : 0, n);',
      '}',
      '',
      'static void LogWriteAddressRefused(const char* why, uint64_t command_buffer, uint64_t record_size, uint64_t address,',
      '                                   uint64_t value) {',
      '\tstatic std::atomic<uint32_t> logged {0};',
      '\tconst uint32_t n = logged.fetch_add(1, std::memory_order_relaxed) + 1;',
      '\tif (n > 20) {',
      '\t\treturn;',
      '\t}',
      '\tLOGF("AmprWriteAddress: refused why=%s cb=0x%016" PRIx64 " record_size=0x%" PRIx64 " address=0x%016" PRIx64',
      '\t     " value=0x%016" PRIx64 " n=%u\\n",',
      '\t     why, command_buffer, record_size, address, value, n);',
      '}',
      '',
      '// M6a: the same tests in the same order as before (short-circuit kept), the failed one named.',
      'static bool EnsureCommandBufferRecordSpace(uint64_t command_buffer, CommandBufferState* state,',
      '                                           uint64_t record_size) {',
      '\tconst char* why = nullptr;',
      '\tif (state == nullptr || record_size == 0) {',
      '\t\twhy = "arg";',
      '\t} else if (!ValidateCommandBufferHeader(command_buffer, state)) {',
      '\t\twhy = "header";',
      '\t} else if (state->buffer == 0) {',
      '\t\twhy = "buffer";',
      '\t} else if (record_size > state->size || state->write_offset > state->size - record_size) {',
      '\t\twhy = "space";',
      '\t} else if (!ValidateCommandBufferBacking(state)) {',
      '\t\twhy = "backing";',
      '\t}',
      '\tif (why != nullptr) {',
      '\t\tLogRecordSpaceRefused(why, command_buffer, state, record_size);',
      '\t\treturn false;',
      '\t}',
      '\treturn true;',
      '}']),
    (['static bool AppendWriteAddressRecord(uint64_t command_buffer, uint64_t address, uint64_t value,',
      '                                     uint64_t record_size = 0x20) {',
      '\tstd::scoped_lock      lock(g_command_buffer_mutex);',
      '\tCommandBufferIterator it;',
      '\tif (!GetOrCreateCommandBufferStateLocked(command_buffer, &it)) {',
      '\t\treturn false;',
      '\t}',
      '',
      '\tauto& state = it->second;',
      '\tif (!EnsureCommandBufferRecordSpace(command_buffer, &state, record_size)) {',
      '\t\treturn false;',
      '\t}',
      '',
      '\tconst auto record_offset = state.write_offset;',
      '\tstd::memset(reinterpret_cast<void*>(state.buffer + record_offset), 0,'],
     ['static bool AppendWriteAddressRecord(uint64_t command_buffer, uint64_t address, uint64_t value,',
      '                                     uint64_t record_size = 0x20) {',
      '\tstd::scoped_lock      lock(g_command_buffer_mutex);',
      '\tCommandBufferIterator it;',
      '\tif (!GetOrCreateCommandBufferStateLocked(command_buffer, &it)) {',
      '\t\tLogWriteAddressRefused("state", command_buffer, record_size, address, value); // M6a, T309',
      '\t\treturn false;',
      '\t}',
      '',
      '\tauto& state = it->second;',
      '\tif (!EnsureCommandBufferRecordSpace(command_buffer, &state, record_size)) {',
      '\t\tLogWriteAddressRefused("ensure", command_buffer, record_size, address, value); // M6a, T309',
      '\t\treturn false;',
      '\t}',
      '',
      '\tconst auto record_offset = state.write_offset;',
      '\tstd::memset(reinterpret_cast<void*>(state.buffer + record_offset), 0,']),
])

# ---------------------------------------------------------------- T023 agc.cpp (no knob, limit 20)
edit('libs/agc.cpp', [
    (['\tKYTY_SYSV_ABI bool ReserveDW(uint32_t num_dw) {',
      '\t\tuint32_t remaining = GetAvailableSizeDW();'],
     ['\tKYTY_SYSV_ABI bool ReserveDW(uint32_t num_dw) {',
      '\t\t// Track M, M6a (HPP-848, ROADMAP s122 item 767(z), T023): signature line without a knob, at most 20 per',
      '\t\t// process - a zero cursor or cursor_down < cursor_up on entry (the states where our GetAvailableSizeDW and',
      '\t\t// upstream 49b2eedd1 decide differently). No decision changes.',
      '\t\tif (cursor_up == nullptr || cursor_down == nullptr || cursor_down < cursor_up) [[unlikely]] {',
      '\t\t\tstatic std::atomic<uint32_t> cursor_state_logged {0};',
      '\t\t\tconst uint32_t                n = cursor_state_logged.fetch_add(1, std::memory_order_relaxed) + 1;',
      '\t\t\tif (n <= 20) {',
      '\t\t\t\tconst char* cls = cursor_up == nullptr ? (cursor_down == nullptr ? "both0" : "up0")',
      '\t\t\t\t                                        : (cursor_down == nullptr ? "down0" : "down_lt_up");',
      '\t\t\t\tLOGF("AgcReserveDW: cursor state class=%s up=0x%016" PRIx64 " down=0x%016" PRIx64 " reserved_dw=%" PRIu32',
      '\t\t\t\t     " num_dw=%" PRIu32 " callback=%d n=%u\\n",',
      '\t\t\t\t     cls, reinterpret_cast<uint64_t>(cursor_up), reinterpret_cast<uint64_t>(cursor_down), reserved_dw,',
      '\t\t\t\t     num_dw, callback != nullptr ? 1 : 0, n);',
      '\t\t\t}',
      '\t\t}',
      '\t\tuint32_t remaining = GetAvailableSizeDW();']),
])

print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
