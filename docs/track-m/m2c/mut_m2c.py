"""M2c (HPP-840, ROADMAP s122 item 756(v)(1)(iv), (v)(2)(ii); task member (3)): Red Team's own mutants, one per theme
(two for T234), other than the executor's (M2a mutant_m2a.py: the fix reverted / no sign extension / no round-even /
mask 3 -> 31; M2b mutant_m2b.py: full / part reverts). All mutants live in ONE build of the worktree C:/kyty/m657/m2c/wt
(main 666a434a + the measurement patch of the test file), each switched on only by M2C_MUT=<name> at run time, so the
heavy LTO link runs once per target (item 760(b)(4)); with M2C_MUT unset the build behaves as main.
  patch   - insert the mutants (whole-line anchors, each exactly once; files are LF)
  restore - git checkout of the patched source files; prints the worktree status
Mutants (what the mutant does at KYTY_M_<theme>=1):
  t234_tie  - DS_MIN_F32 ties select the old value (OpULessThan instead of OpULessThanEqual)
  t234_snan - a signalling NaN source is not quieted
  t233_thr  - legacy/fused split at raw opcode 0x20 instead of 0x2b (V_MADMK/MADAK_F32 0x20/0x21 become fused)
  t306_mask - the offset written under ANY lane mask is taken as constant (the exec equality check dropped)
  t032_2bit - two-bit channels of signed formats are encoded as signed
  t203_zero - at S2[1:0] = 0 the high dword is ORed in (the shift-0 guard dropped)
  t256_u    - export mode 8 extracts the 16-bit lanes unsigned
  t265_size - a new ID is registered without its size
              (EQUIVALENT for the stand: GetFileSize falls back to the host path - replaced by t265_path)
  t265_path - a new ID is registered without its host path (stand build 2)
  t272_swap - the state of trigger i is computed from the travel of the other trigger
  t231_lim  - the glyph raster limit is 200 instead of 4096
"""
import subprocess
import sys

WT = 'C:/kyty/m657/m2c/wt/'
GIT = 'C:/Program Files/Git/cmd/git.exe'
HELPER = ('static bool M2cMut(const char* n) { const char* e = std::getenv("M2C_MUT"); if (e == nullptr) return false; '
          'while (*e != 0 && *e == *n) { e++; n++; } return *e == 0 && *n == 0; } // M2c mutant (HPP-840), never committed')
INCLUDE = '#include <cstdlib> // M2c mutant (HPP-840), never committed'

# file -> (helper anchor line, [(old line, new line)])
EDITS = {
    'src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemoryHelpers.cpp': (
        'uint32_t EmitDsFloatAtomicReplacement(EmitterState& state, uint32_t old, uint32_t source,', [
            ('\tstate.builder.AddFunction(max_value ? spv::OpUGreaterThan : spv::OpULessThanEqual,',
             '\tstate.builder.AddFunction(max_value ? spv::OpUGreaterThan : (M2cMut("t234_tie") ? spv::OpULessThan : spv::OpULessThanEqual),'),
            ('\tresult      = EmitSelectValueU32(state, rhs.signaling_nan,',
             '\tif (!M2cMut("t234_snan")) result      = EmitSelectValueU32(state, rhs.signaling_nan,'),
        ]),
    'src/graphics/shader/recompiler/frontend/translate/Vector.cpp': (
        'IR::ValueOpcode LegacyMadOpcode(const Decoder::Instruction& inst) {', [
            ('\tif (inst.opcode != Decoder::Opcode::V_MAD_F32 && (inst.opcode_id & 0xffu) >= 0x2bu) {',
             '\tif (inst.opcode != Decoder::Opcode::V_MAD_F32 && (inst.opcode_id & 0xffu) >= (M2cMut("t233_thr") ? 0x20u : 0x2bu)) {'),
        ]),
    'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp': (
        'bool MImmediateU32(IR::Value value, uint32_t& packed) {', [
            ('\t       write->Arg(0).Resolve() == exec && MImmediateU32(write->Arg(1).Resolve(), packed);',
             '\t       (M2cMut("t306_mask") || write->Arg(0).Resolve() == exec) && MImmediateU32(write->Arg(1).Resolve(), packed);'),
        ]),
    'src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp': (
        'uint32_t MEncodeFormattedStoreComponent(ValueEmitContext& ctx, const Format::BufferFormatInfo& info,', [
            ('\t\tconst bool is_signed = bits != 2u && (info.type == Format::ComponentType::Snorm ||',
             '\t\tconst bool is_signed = (M2cMut("t032_2bit") || bits != 2u) && (info.type == Format::ComponentType::Snorm ||'),
        ]),
    'src/graphics/shader/recompiler/frontend/translate/Integer.cpp': (
        'bool Translator::V_ALIGNBYTE_B32(const Decoder::Instruction& inst) {', [
            ('\t\tconst auto hi_part     = ir.Select(ir.INotEqual(shift, IR::U32(IR::Value(0u))), hi_part_raw,',
             '\t\tconst auto hi_part     = ir.Select(ir.INotEqual(shift, IR::U32(IR::Value(M2cMut("t203_zero") ? 0xffffffffu : 0u))), hi_part_raw,'),
        ]),
    'src/graphics/shader/recompiler/backend/spirv/spirvEmitterFlow.cpp': (
        'uint32_t ExportVector(ValueEmitContext& ctx, uint32_t data, const IR::ExportInfo& exp,', [
            ('\t\t\t\tstate.builder.AddFunction(sint16_raw ? spv::OpBitFieldSExtract : spv::OpBitFieldUExtract,',
             '\t\t\t\tstate.builder.AddFunction((sint16_raw && !M2cMut("t256_u")) ? spv::OpBitFieldSExtract : spv::OpBitFieldUExtract,'),
        ]),
    'src/libs/libAmpr.cpp': (
        'static bool MT265On() {', [
            ('\t\t\t\t\tg_file_sizes.emplace(info.file_id, info.is_dir ? 0 : info.file_size);',
             '\t\t\t\t\tif (!M2cMut("t265_size")) g_file_sizes.emplace(info.file_id, info.is_dir ? 0 : info.file_size);'),
            ('\t\t\t\t\tg_files.emplace(info.file_id, info.host_path);',
             '\t\t\t\t\tif (!M2cMut("t265_path")) g_files.emplace(info.file_id, info.host_path);'),
        ]),
    'src/libs/controller.cpp': (
        'bool MT272On() {', [
            ('\t\t    m_m272_effect.command[i], m_state.axes[static_cast<int>(Controller::Axis::TriggerLeft) + i],',
             '\t\t    m_m272_effect.command[i], m_state.axes[static_cast<int>(Controller::Axis::TriggerLeft) + (M2cMut("t272_swap") ? 1 - i : i)],'),
        ]),
    'src/libs/libFont.cpp': (
        'static bool MT231On() {', [
            ('\t\tconst auto width  = static_cast<uint32_t>(std::clamp(x1 - x0, 0, FONT_GLYPH_MAX_DIM_M231));',
             '\t\tconst auto width  = static_cast<uint32_t>(std::clamp(x1 - x0, 0, (M2cMut("t231_lim") ? 200 : FONT_GLYPH_MAX_DIM_M231)));'),
            ('\t\tconst auto height = static_cast<uint32_t>(std::clamp(y1 - y0, 0, FONT_GLYPH_MAX_DIM_M231));',
             '\t\tconst auto height = static_cast<uint32_t>(std::clamp(y1 - y0, 0, (M2cMut("t231_lim") ? 200 : FONT_GLYPH_MAX_DIM_M231)));'),
        ]),
}


def patch():
    for f, (anchor, edits) in EDITS.items():
        raw = open(WT + f, 'rb').read()
        assert b'\r' not in raw, f
        lines = raw.decode('utf-8').split('\n')
        for old, new in edits:
            idx = [i for i, l in enumerate(lines) if l == old]
            assert len(idx) == 1, (f, old, idx)
            lines[idx[0]] = new
        idx = [i for i, l in enumerate(lines) if l == anchor]
        assert len(idx) == 1, (f, anchor, idx)
        lines.insert(idx[0], HELPER)
        lines.insert(0, INCLUDE)
        open(WT + f, 'wb').write('\n'.join(lines).encode('utf-8'))
        print('patched', f, len(edits))
    print('ALL OK')


def restore():
    subprocess.check_call([GIT, '-C', WT, 'checkout', '--'] + list(EDITS))
    print(subprocess.check_output([GIT, '-C', WT, 'status', '--short']).decode())


if sys.argv[1] == 'patch':
    patch()
else:
    restore()
