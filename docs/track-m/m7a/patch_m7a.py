"""Track M, M7a (HPP-852, ROADMAP s122 items 762(b), 762(g), 767(g), 767(l)): repair of the T306 hole and the probe of the
criterion "FIXED T306". Applies exact text substitutions (each must match exactly once) to a source tree given as argv[1]
(worktree C:/kyty/m657/m7a/wt or C:/kyty/KytyPS5). Files are LF; a CR in a touched file is an error.
  - ValueOpcodes.h: IR::MSampleOffsetWrapperFlags - the flags of the SelectU32 the translator hands over for the offset of
    IMAGE_SAMPLE_*_O;
  - Memory.cpp (Translator::IMAGE_SAMPLE): the wrapper carries those flags;
  - spirvEmitterImage.cpp: MResolveSampleOffset takes a SelectU32 as the wrapper only with those flags (a write of the
    offset exposed by the folding of the wrapper under a constant lane mask is no longer read as the wrapper); the
    "MTexOffset: ... previous path" lines are counted by reason; test probe of the emitted ConstOffset;
  - SpirvEmitter.h: the declarations of the counter and of the probe.
Usage: python patch_m7a.py <tree>   Refuses under C:/kyty/SEALED_RUN.lock."""
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3')
    sys.exit(3)
ROOT = sys.argv[1].rstrip('/') + '/'
R = 'src/graphics/shader/recompiler/'
T = chr(9)
NL = chr(10)
BS = chr(92)


def L(*lines):
    return NL.join(lines) + NL


EDITS = []

# 1. ValueOpcodes.h - the flags of the wrapper.
EDITS.append((R + 'ir/opcodes/ValueOpcodes.h', L(
    'static_assert(sizeof(ExportFlags) == sizeof(uint64_t));',
    'static_assert(std::is_trivially_copyable_v<ExportFlags>);',
), L(
    'static_assert(sizeof(ExportFlags) == sizeof(uint64_t));',
    'static_assert(std::is_trivially_copyable_v<ExportFlags>);',
    '',
    '// Track M, M7a (T306, KYTY_M_T306; ROADMAP s122 items 762(b), 767(g)): the flags of the SelectU32(exec of the sample,',
    '// offset dword, 0) that Translator::IMAGE_SAMPLE hands over for the texel offset of IMAGE_SAMPLE_*_O. The emitter',
    '// (MResolveSampleOffset) takes a select as that wrapper only with these flags: under a constant lane mask (the entry',
    '// EXEC of a non-pixel stage, s_mov_b64 exec, -1) constant propagation folds the wrapper away, and the write of the',
    '// offset under another mask, SelectU32(mask, immediate, old), then stood in its place and was read as the wrapper.',
    'inline constexpr uint64_t MSampleOffsetWrapperFlags = 0x0000003630335447ull; // "GT306"',
)))

# 2. Memory.cpp - the wrapper with the flags.
EDITS.append((R + 'frontend/translate/Memory.cpp', L(
    T + T + '// Track M, M2a (T306, upstream 984cfceb; KYTY_M_T306): the offset (address dword 0) seen through the lane mask',
    T + T + '// of this sample - the emitter (MResolveSampleOffset) proves an offset written under the same mask constant.',
    T + T + 'm_offset = ir.Select(ir.GetExec(), IR::U32(ReadRawU32(OffsetOperand(PlainOperand(MemorySourceAt(inst, 0)), 0))),',
    T + T + '                     IR::U32(IR::Value(0u)));',
), L(
    T + T + '// Track M, M2a (T306, upstream 984cfceb; KYTY_M_T306): the offset (address dword 0) seen through the lane mask',
    T + T + '// of this sample - the emitter (MResolveSampleOffset) proves an offset written under the same mask constant.',
    T + T + '// Track M, M7a (ROADMAP s122 item 767(g)): the select carries IR::MSampleOffsetWrapperFlags - the emitter tells',
    T + T + '// it from a write of the offset that constant propagation leaves in its place when the lane mask is constant.',
    T + T + 'm_offset = ir.Emit(IR::ValueOpcode::SelectU32,',
    T + T + '                   {ir.GetExec(), ReadRawU32(OffsetOperand(PlainOperand(MemorySourceAt(inst, 0)), 0)),',
    T + T + '                    IR::Value(0u)},',
    T + T + '                   IR::MSampleOffsetWrapperFlags);',
)))

E = R + 'backend/spirv/spirvEmitterImage.cpp'
# 3. spirvEmitterImage.cpp - includes.
EDITS.append((E, L(
    '#include "graphics/shader/recompiler/frontend/decode/ImageOps.h"',
    '',
    '#include "common/envFlag.h"',
    '#include <cstdlib>',
    '#include <algorithm>',
    '#include <bit>',
), L(
    '#include "graphics/shader/recompiler/frontend/decode/ImageOps.h"',
    '#include "graphics/shader/recompiler/backend/spirv/SpirvEmitter.h"',
    '',
    '#include "common/envFlag.h"',
    '#include <cstdlib>',
    '#include <algorithm>',
    '#include <atomic>',
    '#include <bit>',
    '#include <mutex>',
    '#include <utility>',
    '#include <vector>',
)))
# 4. counters and probe storage, before MSampleConstOffset.
EDITS.append((E, L(
    '// Track M, M2a (T306, upstream 984cfceb; KYTY_M_T306): the ConstOffset operand of a sample on <resource> from the',
), L(
    '// Track M, M7a (T306; ROADMAP s122 item 767(g)(3)): the "MTexOffset: ... previous path" lines counted by reason',
    '// (0 nonconstant, 1 cube, 2 range) in the branch that writes the line, and the test probe of the emitted ConstOffset',
    '// (off unless shader_cfg_tests turns it on; the emulator never does). No knob: a count costs one relaxed increment',
    '// on a path that already writes a log line.',
    'std::atomic<uint32_t>         g_m_tex_offset_fallbacks[3] {};',
    'std::atomic<bool>             g_m_tex_offset_recording {false};',
    'std::mutex                    g_m_tex_offset_mutex;',
    'std::vector<MTexOffsetRecord> g_m_tex_offset_records;',
    '',
    'void MTexOffsetCount(uint32_t reason) {',
    T + 'g_m_tex_offset_fallbacks[reason].fetch_add(1u, std::memory_order_relaxed);',
    '}',
    '',
    '// Track M, M2a (T306, upstream 984cfceb; KYTY_M_T306): the ConstOffset operand of a sample on <resource> from the',
)))
# 5. cube / range line counted.
EDITS.append((E, L(
    T + T + '     image.cube ? "cube" : "range");',
    T + T + 'return 0u;',
), L(
    T + T + '     image.cube ? "cube" : "range");',
    T + T + 'MTexOffsetCount(image.cube ? 1u : 2u);',
    T + T + 'return 0u;',
)))
# 6. MResolveSampleOffset - the wrapper only with its flags.
EDITS.append((E, L(
    '// Track M, M2a (T306; KYTY_M_T306): the packed offset of a sample when it is the same immediate for every lane that',
    '// executes the sample. At =1 the translator hands the offset dword over as SelectU32(exec of the sample, offset, 0)',
    '// (Translator::IMAGE_SAMPLE); the offset is exact when it is an immediate, or that wrapper around an immediate, or',
    '// the wrapper around SelectU32(c, immediate, old) - the VGPR written under the same lane mask c. Anything else (an',
    '// offset written under another mask, a computed offset): false, the previous path.',
), L(
    '// Track M, M2a (T306; KYTY_M_T306): the packed offset of a sample when it is the same immediate for every lane that',
    '// executes the sample. At =1 the translator hands the offset dword over as SelectU32(exec of the sample, offset, 0)',
    '// (Translator::IMAGE_SAMPLE); the offset is exact when it is an immediate, or that wrapper around an immediate, or',
    '// the wrapper around SelectU32(c, immediate, old) - the VGPR written under the same lane mask c. Anything else (an',
    '// offset written under another mask, a computed offset): false, the previous path.',
    '// Track M, M7a (ROADMAP s122 items 762(b), 767(g)): the wrapper is the select with IR::MSampleOffsetWrapperFlags.',
    '// Under a constant lane mask constant propagation folds it to its operand - an immediate (every lane holds it) or',
    '// the write SelectU32(c, immediate, old) of the offset under a narrower mask c, which has no such flags: false.',
)))
EDITS.append((E, L(
    T + 'const auto* wrapper = value.TryInstruction();',
    T + 'if (wrapper == nullptr || wrapper->GetOpcode() != IR::ValueOpcode::SelectU32) {',
    T + T + 'return false;',
    T + '}',
), L(
    T + 'const auto* wrapper = value.TryInstruction();',
    T + 'if (wrapper == nullptr || wrapper->GetOpcode() != IR::ValueOpcode::SelectU32 ||',
    T + '    wrapper->Flags<uint64_t>() != IR::MSampleOffsetWrapperFlags) {',
    T + T + 'return false;',
    T + '}',
)))
# 7. nonconstant line counted.
EDITS.append((E, L(
    T + T + T + T + 'LOGF("MTexOffset: shader=0x%016llx pc=0x%x nonconstant offset, previous path' + BS + 'n",',
    T + T + T + T + '     static_cast<unsigned long long>(state.program.shader_hash),',
    T + T + T + T + '     inst.Flags<IR::MemoryFlags>().pc);',
    T + T + T + '}',
), L(
    T + T + T + T + 'LOGF("MTexOffset: shader=0x%016llx pc=0x%x nonconstant offset, previous path' + BS + 'n",',
    T + T + T + T + '     static_cast<unsigned long long>(state.program.shader_hash),',
    T + T + T + T + '     inst.Flags<IR::MemoryFlags>().pc);',
    T + T + T + T + 'MTexOffsetCount(0u);',
    T + T + T + '}',
)))
# 8. probe record per emitted sample with ConstOffset.
EDITS.append((E, L(
    T + T + T + 'state.builder.AddFunction(opcode, sample_operands);',
    T + T + T + 'return sample;',
), L(
    T + T + T + 'state.builder.AddFunction(opcode, sample_operands);',
    T + T + T + 'if (m_offset != 0u && g_m_tex_offset_recording.load(std::memory_order_relaxed)) [[unlikely]] {',
    T + T + T + T + 'const std::lock_guard lock(g_m_tex_offset_mutex);',
    T + T + T + T + 'g_m_tex_offset_records.push_back(',
    T + T + T + T + '    {state.program.shader_hash, inst.Flags<IR::MemoryFlags>().pc, sample, m_offset});',
    T + T + T + '}',
    T + T + T + 'return sample;',
)))
# 9. public functions at the end of the file.
EDITS.append((E, L(
    T + 'ctx.Fail(inst, "has no image SPIR-V emitter");',
    '}',
    '',
    '} // namespace Libs::Graphics::ShaderRecompiler::Spirv::Emitter',
), L(
    T + 'ctx.Fail(inst, "has no image SPIR-V emitter");',
    '}',
    '',
    'MTexOffsetCounts MTexOffsetFallbacks() {',
    T + 'return {g_m_tex_offset_fallbacks[0].load(std::memory_order_relaxed),',
    T + '        g_m_tex_offset_fallbacks[1].load(std::memory_order_relaxed),',
    T + '        g_m_tex_offset_fallbacks[2].load(std::memory_order_relaxed)};',
    '}',
    '',
    'void MTexOffsetRecording(bool on) {',
    T + 'const std::lock_guard lock(g_m_tex_offset_mutex);',
    T + 'g_m_tex_offset_records.clear();',
    T + 'g_m_tex_offset_recording.store(on, std::memory_order_relaxed);',
    '}',
    '',
    'std::vector<MTexOffsetRecord> MTexOffsetTakeRecords() {',
    T + 'const std::lock_guard lock(g_m_tex_offset_mutex);',
    T + 'return std::exchange(g_m_tex_offset_records, {});',
    '}',
    '',
    '} // namespace Libs::Graphics::ShaderRecompiler::Spirv::Emitter',
)))

# 10. SpirvEmitter.h - declarations.
EDITS.append((R + 'backend/spirv/SpirvEmitter.h', L(
    'bool BdaLeanEnabled();',
    '} // namespace Emitter',
), L(
    'bool BdaLeanEnabled();',
    '// Track M, M7a (T306, KYTY_M_T306; ROADMAP s122 item 767(g)(3)): the lines "MTexOffset: ... previous path" written',
    '// so far in this process, by reason (no knob; the emulator only counts). The probe: while recording is on, one',
    '// record per emitted IMAGE_SAMPLE_*_O that carries ConstOffset - shader hash, pc of the instruction (MemoryFlags),',
    '// SPIR-V result id of the sample, id of its ConstOffset constant. MTexOffsetRecording clears the records; tests only.',
    'struct MTexOffsetRecord {',
    T + 'uint64_t shader_hash = 0;',
    T + 'uint32_t pc          = 0;',
    T + 'uint32_t sample_id   = 0;',
    T + 'uint32_t offset_id   = 0;',
    '};',
    'struct MTexOffsetCounts {',
    T + 'uint32_t nonconstant = 0;',
    T + 'uint32_t cube        = 0;',
    T + 'uint32_t range       = 0;',
    '};',
    'MTexOffsetCounts              MTexOffsetFallbacks();',
    'void                          MTexOffsetRecording(bool on);',
    'std::vector<MTexOffsetRecord> MTexOffsetTakeRecords();',
    '} // namespace Emitter',
)))


def main():
    data = {}
    for path, old, new in EDITS:
        if path not in data:
            raw = open(ROOT + path, 'rb').read()
            if b'\r' in raw:
                raise SystemExit('CR in ' + path)
            data[path] = raw.decode('utf-8')
        n = data[path].count(old)
        if n != 1:
            raise SystemExit('anchor count %d in %s: %r' % (n, path, old[:80]))
        data[path] = data[path].replace(old, new)
    for path, text in data.items():
        open(ROOT + path, 'wb').write(text.encode('utf-8'))
        print('patched', path)
    print('edits', len(EDITS), 'files', len(data))


main()
