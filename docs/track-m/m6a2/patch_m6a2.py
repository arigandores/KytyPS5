"""Track M, M6a2 (HPP-854, ROADMAP s122 item 770(b)-(e)): edits of the measurement-only knob KYTY_DIAG_M5W2 after
review M6b (RC1, RC2, member 769(g)(2), note P1). Usage: patch_m6a2.py <source root> (the M6a worktree or main).
Anchors are whole lines (each old block must occur exactly once); CRLF files keep CRLF; output written as bytes.
"""
import sys

NL = chr(10)


def load(path):
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', NL)
    return text, crlf


def save(path, text, crlf):
    data = text.replace(NL, '\r\n') if crlf else text
    open(path, 'wb').write(data.encode('utf-8'))


def block(lines):
    return NL.join(lines) + NL


def apply(root, rel, edits):
    path = root + '/' + rel
    text, crlf = load(path)
    for old, new in edits:
        o = block(old)
        n = block(new)
        cnt = text.count(o)
        if cnt != 1:
            print('ANCHOR FAIL %s count=%d first line: %s' % (rel, cnt, old[0]))
            sys.exit(1)
        # whole-line anchor: preceded by start or newline
        i = text.index(o)
        if i != 0 and text[i - 1] != NL:
            print('ANCHOR NOT AT LINE START %s: %s' % (rel, old[0]))
            sys.exit(1)
        text = text.replace(o, n)
    save(path, text, crlf)
    print('patched %s (%d edits, crlf=%d)' % (rel, len(edits), 1 if crlf else 0))


T = chr(9)


def t(n, s):
    return T * n + s


# ---------------------------------------------------------------- diagM5W2.h
H_EDITS = [
    ([
        '//   T021 (imageView.cpp, FindView - a created view): minlod_views - views with min_lod > 0, minlod_div - of them',
        '//     base_level > 0 and min_lod > (level_count - 1) * 256 (our clamp level_count - 1 differs from the absolute one);',
    ], [
        '//   T021 (imageView.cpp, FindView - a created view): minlod_views - views with min_lod > 0, minlod_div - of them',
        '//     base_level > 0 and min_lod > (level_count - 1) * 256 (reference since M6a2); minlod_div_x (M6a2, ROADMAP s122',
        '//     item 770(b), the divergence field of rule 767(k)) - base_level > 0 and min_lod > 256 * max(base_level,',
        '//     level_count - 1): our lowest readable level differs from the absolute minLod only there;',
        '//   M6a2 (item 770(v)): clr_dw_div8 - accepted fills of class (a3) of M5a (reference, not part of clr_dw_div):',
        '//     R8Unorm with W != (W & 0xff) * 0x01010101, R8G8Unorm with (W & 0xffff) != (W >> 16);',
        '//   M6a2 (item 770(g)): at =1 the grain of an OBJECT port is read only through a copy by',
        '//     Libs::LibKernel::Memory::TryReadBacking; a refused copy is ao_obj_unread (counted in ao_obj_push, never in',
        '//     ao_obj_nz); the other ports keep the raw read (the output path reads them raw already);',
        '//   M6a2 (item 770(d)): inv_part_src - the pairs of inv_part with coverage tested against SourceRange() (size =',
        '//     source_size or info.data.size) instead of info.data (reference);',
    ]),
    ([
        '// True if our decode of (vk_format, word) differs from upstream 57c97ebd8 / 89792a3bc (pure).',
        'bool ClearDwordDiverges(uint32_t vk_format, uint32_t word);',
    ], [
        '// True if our decode of (vk_format, word) differs from upstream 57c97ebd8 / 89792a3bc (pure).',
        'bool ClearDwordDiverges(uint32_t vk_format, uint32_t word);',
        '// M6a2: true for class (a3) of M5a - R8Unorm without a repeated byte, R8G8Unorm with lo != hi (pure).',
        'bool ClearDwordDiverges8(uint32_t vk_format, uint32_t word);',
    ]),
    ([
        '// True if base_level > 0 and min_lod > (level_count - 1) * 256 (pure; min_lod > 0 assumed).',
        'bool MinLodDiverges(uint32_t min_lod, uint32_t base_level, uint32_t level_count);',
    ], [
        '// True if base_level > 0 and min_lod > (level_count - 1) * 256 (pure; min_lod > 0 assumed).',
        'bool MinLodDiverges(uint32_t min_lod, uint32_t base_level, uint32_t level_count);',
        '// M6a2: true if base_level > 0 and min_lod > 256 * max(base_level, level_count - 1) (pure; level_count 0 - false).',
        'bool MinLodDivergesExact(uint32_t min_lod, uint32_t base_level, uint32_t level_count);',
    ]),
    ([
        '// T188: one InvalidateMemoryFromGPU call with a valid range; then one call per colour image it overlaps.',
        'void NoteInvalidateCall();',
        'void NoteInvalidateImage(bool gpu_modified, uint64_t image_address, uint64_t image_size, uint64_t address,',
        '                         uint64_t size);',
    ], [
        '// T188: one InvalidateMemoryFromGPU call with a valid range; then one call per colour image it overlaps.',
        '// source_size - SourceRange().size of the image (its address is image_address).',
        'void NoteInvalidateCall();',
        'void NoteInvalidateImage(bool gpu_modified, uint64_t image_address, uint64_t image_size, uint64_t source_size,',
        '                         uint64_t address, uint64_t size);',
    ]),
    ([
        t(1, 'uint64_t pushes;'),
        '};',
        'Totals Read();',
    ], [
        t(1, 'uint64_t pushes;'),
        t(1, 'uint64_t minlod_div_x;  // M6a2'),
        t(1, 'uint64_t clr_dw_div8;   // M6a2'),
        t(1, 'uint64_t ao_obj_unread; // M6a2'),
        t(1, 'uint64_t inv_part_src;  // M6a2'),
        '};',
        'Totals Read();',
    ]),
]

# ---------------------------------------------------------------- diagM5W2.cpp
C_EDITS = [
    ([
        '#include "common/envFlag.h"',
        '#include "common/logging/log.h"',
        '',
        '#include <array>',
    ], [
        '#include "common/envFlag.h"',
        '#include "common/logging/log.h"',
        '#include "kernel/memory.h"',
        '',
        '#include <algorithm>',
        '#include <array>',
    ]),
    ([
        '#include <vulkan/vulkan.hpp>',
    ], [
        '#include <vector>',
        '#include <vulkan/vulkan.hpp>',
    ]),
    ([
        'std::atomic<uint64_t> g_pushes {0};',
    ], [
        'std::atomic<uint64_t> g_pushes {0};',
        '// M6a2 (ROADMAP s122 item 770(b)-(d)).',
        'std::atomic<uint64_t> g_minlod_div_x {0};',
        'std::atomic<uint64_t> g_clr_dw_div8 {0};',
        'std::atomic<uint64_t> g_ao_obj_unread {0};',
        'std::atomic<uint64_t> g_inv_part_src {0};',
    ]),
    ([
        'std::array<std::atomic<uint64_t>, FMT_ROWS> g_clr_fmt_div {};',
    ], [
        'std::array<std::atomic<uint64_t>, FMT_ROWS> g_clr_fmt_div {};',
        'std::array<std::atomic<uint64_t>, FMT_ROWS> g_clr_fmt_div8 {}; // M6a2',
    ]),
    ([
        'constexpr uint64_t PERIODIC_PUSHES = 4096;',
    ], [
        'constexpr uint64_t PERIODIC_PUSHES = 4096;',
        '',
        '// M6a2: a grain larger than this is not copied (counted ao_obj_unread); a real grain is at most',
        '// samples (<= 1024 for the games seen) * 16 channels * 4 bytes = 64 KiB.',
        'constexpr uint64_t MAX_GRAIN_BYTES = uint64_t {4} << 20u;',
        '',
        '// Bytes of the grain scanned by PcmHasNonzero (the same channels and sample size).',
        'uint64_t GrainBytes(uint32_t data_format, uint32_t samples) {',
        t(1, 'const uint32_t raw_channels = (data_format >> 8u) & 0xffu;'),
        t(1, 'const uint32_t channels     = raw_channels == 0 ? 2u : (raw_channels < 16u ? raw_channels : 16u);'),
        t(1, 'const uint32_t data_type    = data_format & 0x7fu;'),
        t(1, 'return static_cast<uint64_t>(samples) * channels * (data_type == 1 ? 2u : 4u);'),
        '}',
    ]),
    ([
        'void NoteAudioPort(bool object_port, const void* pcm, uint32_t data_format, uint32_t samples) {',
        t(1, 'const bool nz = PcmHasNonzero(pcm, data_format, samples);'),
        t(1, 'if (object_port) {'),
        t(2, 'Bump(g_ao_obj_push);'),
        t(2, 'if (nz) {'),
        t(3, 'Bump(g_ao_obj_nz);'),
        t(2, '}'),
        t(1, '} else {'),
        t(2, 'Bump(g_ao_bus_push);'),
        t(2, 'if (nz) {'),
        t(3, 'Bump(g_ao_bus_nz);'),
        t(2, '}'),
        t(1, '}'),
        '}',
    ], [
        'void NoteAudioPort(bool object_port, const void* pcm, uint32_t data_format, uint32_t samples) {',
        t(1, 'if (object_port) {'),
        t(2, '// M6a2 (ROADMAP s122 item 770(g)): the object grain only through a copy by the guarded reader of guest'),
        t(2, '// memory - a pointer the game left in the port to unmapped memory is counted, not read.'),
        t(2, 'Bump(g_ao_obj_push);'),
        t(2, 'const uint64_t bytes = GrainBytes(data_format, samples);'),
        t(2, 'if (bytes == 0) {'),
        t(3, 'return; // PcmHasNonzero of an empty grain is false'),
        t(2, '}'),
        t(2, 'thread_local std::vector<uint8_t> copy;'),
        t(2, 'if (bytes > MAX_GRAIN_BYTES) {'),
        t(3, 'Bump(g_ao_obj_unread);'),
        t(3, 'return;'),
        t(2, '}'),
        t(2, 'copy.resize(static_cast<size_t>(bytes));'),
        t(2, 'if (!Libs::LibKernel::Memory::TryReadBacking(reinterpret_cast<uint64_t>(pcm), copy.data(), bytes)) {'),
        t(3, 'Bump(g_ao_obj_unread);'),
        t(3, 'return;'),
        t(2, '}'),
        t(2, 'if (PcmHasNonzero(copy.data(), data_format, samples)) {'),
        t(3, 'Bump(g_ao_obj_nz);'),
        t(2, '}'),
        t(2, 'return;'),
        t(1, '}'),
        t(1, 'Bump(g_ao_bus_push);'),
        t(1, 'if (PcmHasNonzero(pcm, data_format, samples)) {'),
        t(2, 'Bump(g_ao_bus_nz);'),
        t(1, '}'),
        '}',
    ]),
    ([
        'void NoteClearDword(uint32_t vk_format, uint32_t word) {',
        t(1, 'const uint32_t row = vk_format < FMT_ROWS - 1 ? vk_format : FMT_ROWS - 1;'),
        t(1, 'const bool     div = ClearDwordDiverges(vk_format, word);'),
        t(1, 'Bump(g_clr_dw);'),
        t(1, 'Bump(g_clr_fmt[row]);'),
        t(1, 'if (div) {'),
        t(2, 'Bump(g_clr_dw_div);'),
        t(2, 'Bump(g_clr_fmt_div[row]);'),
        t(1, '}'),
        '}',
    ], [
        'bool ClearDwordDiverges8(uint32_t vk_format, uint32_t word) {',
        t(1, 'switch (static_cast<vk::Format>(vk_format)) {'),
        t(2, 'case vk::Format::eR8Unorm: return word != (word & 0xffu) * 0x01010101u;'),
        t(2, 'case vk::Format::eR8G8Unorm: return (word & 0xffffu) != (word >> 16u);'),
        t(2, 'default: return false;'),
        t(1, '}'),
        '}',
        '',
        'void NoteClearDword(uint32_t vk_format, uint32_t word) {',
        t(1, 'const uint32_t row  = vk_format < FMT_ROWS - 1 ? vk_format : FMT_ROWS - 1;'),
        t(1, 'const bool     div  = ClearDwordDiverges(vk_format, word);'),
        t(1, 'const bool     div8 = ClearDwordDiverges8(vk_format, word);'),
        t(1, 'Bump(g_clr_dw);'),
        t(1, 'Bump(g_clr_fmt[row]);'),
        t(1, 'if (div) {'),
        t(2, 'Bump(g_clr_dw_div);'),
        t(2, 'Bump(g_clr_fmt_div[row]);'),
        t(1, '}'),
        t(1, 'if (div8) {'),
        t(2, 'Bump(g_clr_dw_div8);'),
        t(2, 'Bump(g_clr_fmt_div8[row]);'),
        t(1, '}'),
        '}',
    ]),
    ([
        'void NoteMinLodView(uint32_t min_lod, uint32_t base_level, uint32_t level_count) {',
        t(1, 'if (min_lod == 0) {'),
        t(2, 'return;'),
        t(1, '}'),
        t(1, 'Bump(g_minlod_views);'),
        t(1, 'if (MinLodDiverges(min_lod, base_level, level_count)) {'),
        t(2, 'Bump(g_minlod_div);'),
        t(1, '}'),
        '}',
    ], [
        'bool MinLodDivergesExact(uint32_t min_lod, uint32_t base_level, uint32_t level_count) {',
        t(1, 'if (base_level == 0 || level_count == 0) {'),
        t(2, 'return false;'),
        t(1, '}'),
        t(1, 'const uint64_t level = std::max<uint64_t>(base_level, level_count - 1u);'),
        t(1, 'return static_cast<uint64_t>(min_lod) > level * 256u;'),
        '}',
        '',
        'void NoteMinLodView(uint32_t min_lod, uint32_t base_level, uint32_t level_count) {',
        t(1, 'if (min_lod == 0) {'),
        t(2, 'return;'),
        t(1, '}'),
        t(1, 'Bump(g_minlod_views);'),
        t(1, 'if (MinLodDiverges(min_lod, base_level, level_count)) {'),
        t(2, 'Bump(g_minlod_div);'),
        t(1, '}'),
        t(1, 'if (MinLodDivergesExact(min_lod, base_level, level_count)) {'),
        t(2, 'Bump(g_minlod_div_x);'),
        t(1, '}'),
        '}',
    ]),
    ([
        'void NoteInvalidateImage(bool gpu_modified, uint64_t image_address, uint64_t image_size, uint64_t address,',
        '                         uint64_t size) {',
        t(1, 'if (!gpu_modified) {'),
        t(2, 'return;'),
        t(1, '}'),
        t(1, 'Bump(g_inv_gpu);'),
        t(1, 'const bool covers = address <= image_address && address + size >= image_address + image_size;'),
    ], [
        'void NoteInvalidateImage(bool gpu_modified, uint64_t image_address, uint64_t image_size, uint64_t source_size,',
        '                         uint64_t address, uint64_t size) {',
        t(1, 'if (!gpu_modified) {'),
        t(2, 'return;'),
        t(1, '}'),
        t(1, 'Bump(g_inv_gpu);'),
        t(1, '// M6a2 (item 770(d)): the same pair, coverage of SourceRange() (the range Image::Overlaps tests).'),
        t(1, 'if (!(address <= image_address && address + size >= image_address + source_size)) {'),
        t(2, 'Bump(g_inv_part_src);'),
        t(1, '}'),
        t(1, 'const bool covers = address <= image_address && address + size >= image_address + image_size;'),
    ]),
    ([
        t(1, '        Load(g_inv_off),     Load(g_raw_rd),       Load(g_raw_rd_gpu),   Load(g_pushes)};'),
    ], [
        t(1, '        Load(g_inv_off),     Load(g_raw_rd),       Load(g_raw_rd_gpu),   Load(g_pushes),'),
        t(1, '        Load(g_minlod_div_x), Load(g_clr_dw_div8), Load(g_ao_obj_unread), Load(g_inv_part_src)};'),
    ]),
    ([
        t(1, '     " raw_rd=%" PRIu64 " raw_rd_gpu=%" PRIu64 "\\n",'),
        t(1, '     when, t.pushes, t.ao_obj_push, t.ao_obj_nz, t.ao_obj_nopcm, t.ao_bus_push, t.ao_bus_nz, t.clr_dw, t.clr_dw_div,'),
        t(1, '     t.minlod_views, t.minlod_div, t.inv_calls, t.inv_part, t.inv_gpu, t.inv_off, t.raw_rd, t.raw_rd_gpu);'),
    ], [
        t(1, '     " raw_rd=%" PRIu64 " raw_rd_gpu=%" PRIu64 " minlod_div_x=%" PRIu64 " clr_dw_div8=%" PRIu64'),
        t(1, '     " ao_obj_unread=%" PRIu64 " inv_part_src=%" PRIu64 "\\n",'),
        t(1, '     when, t.pushes, t.ao_obj_push, t.ao_obj_nz, t.ao_obj_nopcm, t.ao_bus_push, t.ao_bus_nz, t.clr_dw, t.clr_dw_div,'),
        t(1, '     t.minlod_views, t.minlod_div, t.inv_calls, t.inv_part, t.inv_gpu, t.inv_off, t.raw_rd, t.raw_rd_gpu,'),
        t(1, '     t.minlod_div_x, t.clr_dw_div8, t.ao_obj_unread, t.inv_part_src);'),
    ]),
    ([
        t(3, 'LOGF("M5W2Clr: when=%s fmt=%u clr_dw=%" PRIu64 " clr_dw_div=%" PRIu64 "\\n", when, row, n,'),
        t(3, '     Load(g_clr_fmt_div[row]));'),
    ], [
        t(3, 'LOGF("M5W2Clr: when=%s fmt=%u clr_dw=%" PRIu64 " clr_dw_div=%" PRIu64 " clr_dw_div8=%" PRIu64 "\\n", when,'),
        t(3, '     row, n, Load(g_clr_fmt_div[row]), Load(g_clr_fmt_div8[row]));'),
    ]),
]

# ---------------------------------------------------------------- textureCache.cpp (T188 site)
TC_EDITS = [
    ([
        t(3, 'DiagM5W2::NoteInvalidateImage(image.IsGpuModified(), image.info.data.address, image.info.data.size, address,'),
        t(3, '                              size);'),
    ], [
        t(3, 'DiagM5W2::NoteInvalidateImage(image.IsGpuModified(), image.info.data.address, image.info.data.size,'),
        t(3, '                              image.SourceRange().size, address, size); // M6a2: + inv_part_src'),
    ]),
]


def main():
    root = sys.argv[1].rstrip('/')
    apply(root, 'src/libs/diagM5W2.h', H_EDITS)
    apply(root, 'src/libs/diagM5W2.cpp', C_EDITS)
    apply(root, 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', TC_EDITS)
    print('ALL OK')


if __name__ == '__main__':
    main()
