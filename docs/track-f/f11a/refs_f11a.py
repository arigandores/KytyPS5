# F11a (HPP-455): check of the reference map of docs/track-f/f11a.md (general rule 24(1)): every <commit>:<path>:<line>
# carries its anchor at that line and the control text at line + 1 (substring after stripping). Ends with ALL OK.
import os
import subprocess
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
C = 'df2b3179'
S = 'src/graphics/shader/recompiler/'
REFS = [
    (C, S + 'backend/spirv/spirvEmitterMemory.cpp', 2210, 'const auto node_type = Binary(state, OpBitwiseAnd, u32t, node_lo, U(7u));',
     'const auto node_off  = Binary(state, OpBitwiseAnd, u32t, node_lo, U(~7u));'),
    (C, S + 'backend/spirv/spirvEmitterMemory.cpp', 2232, 'const auto is_tri   = Binary(state, OpULessThan, boolt, node_type, U(2u));',
     'const auto is_tri1  = ieq(node_type, U(1u));'),
    (C, S + 'backend/spirv/spirvEmitterMemory.cpp', 2424, 'return branch(is_tri, triangle_node, invalid_node);', '});'),
    (C, S + 'backend/spirv/spirvEmitterMemory.cpp', 2141, 'const auto desc0  = arg(12);', 'const auto desc1  = arg(13);'),
    (C, S + 'backend/spirv/spirvEmitterMemory.cpp', 2381, 'const Vec3 tri_a = vsel(is_tri1, v1, v0);', 'const Vec3 tri_b = vsel(is_tri1, v3, v1);'),
    (C, S + 'backend/spirv/spirvEmitterMemory.cpp', 2144, 'const bool node64 = !inst.Arg(1).IsImmediate() || inst.Arg(1).U32() != 0u;', ''),
    (C, S + 'backend/spirv/spirvEmitterMemory.cpp', 1939, 'void EmitLoopCapTrip(EmitterState& state, uint32_t budget) {',
     'if (state.fault_buffer_variable == 0) {'),
    (C, S + 'backend/spirv/spirvEmitterMemory.cpp', 2209, '// --- Node address: type in bits [2:0], 64-byte offset in [31:3]; (base >> 3) + ptr, << 3.',
     'const auto node_type = Binary(state, OpBitwiseAnd, u32t, node_lo, U(7u));'),
    (C, S + 'frontend/translate/Memory.cpp', 839, 'const IR::U32 desc0 = GetResourceDword(memory.resource, 0);',
     'const IR::U32 desc1 = GetResourceDword(memory.resource, 1);'),
    (C, S + 'frontend/translate/Memory.cpp', 888, 'const IR::U1 is_box32 = ir.IEqual(node_type, U32C(5u));',
     'const IR::U1 is_tri   = ir.ULessThan(node_type, U32C(2u));'),
    (C, S + 'frontend/translate/Memory.cpp', 851, 'static const bool native_bvh = [] {', 'const char* value = std::getenv("KYTY_BVH_NATIVE");'),
    (C, S + 'frontend/translate/Memory.cpp', 714, 'static const bool stub = Common::EnvFlagOn("KYTY_BVH_STUB");', 'if (stub) {'),
    (C, S + 'frontend/translate/Scalar.cpp', 239, 'case O::S_TRAP: EmitControlNop(); return true;',
     'case O::S_WAITCNT_DEPCTR: EmitWaitcnt(); return true;'),
    (C, S + 'frontend/decode/ScalarAluOps.cpp', 81, '{0x0du, Opcode::S_BITCMP1_B32}', ''),
    (C, S + 'ir/opcodes/ValueOpcodes.inc', 299, '// Appended last: translation-cache plans store opcode numbers.',
     '// RDNA2 IMAGE_BVH_INTERSECT_RAY: node_lo, node_hi, extent, origin xyz, dir xyz, inv_dir xyz,'),
    (C, S + 'ir/passes/ResourceTracking.cpp', 905, 'if (op == ValueOpcode::BvhIntersectRay) {', 'm_info.uses_dma = true;'),
    (C, S + 'backend/spirv/SpirvEmitter.h', 38, 'inline constexpr uint32_t LoopTripWordBase = 1u << 21;',
     'inline constexpr uint32_t LoopTripWords    = 16;'),
    (C, S + 'backend/spirv/SpirvEmitter.h', 40, 'inline constexpr uint32_t LoopTripSlots    = 8;', ''),
    (C, S + 'backend/spirv/spirvEmitterModule.cpp', 766, 'state.builder.RequireCapability(spv::CapabilityGroupNonUniformBallot);', ''),
    (C, S + 'frontend/decode/ShaderDecoder.cpp', 344, 'bool FixB1BEnabled() {', 'static const bool enabled = [] {'),
    (C, 'src/graphics/host_gpu/renderer/cache/faultManager.cpp', 40, 'LoopTripOffset + LoopTripBytes),',
     'm_download_buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,'),
    (C, 'src/graphics/host_gpu/renderer/cache/faultManager.cpp', 152, 'const bool trips       = LoopCap::BvhLoopCap() != 0;',
     'const auto trip_offset = m_current_area * LoopTripBytes;'),
    (C, 'src/graphics/host_gpu/renderer/cache/faultManager.cpp', 93, 'm_fault_buffer.Fill(LoopTripOffset, LoopTripBytes, 0);', ''),
    (C, 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 578,
     'const std::string variant = ShaderRecompiler::Spirv::Emitter::BvhLoopCapSignatureToken() +',
     '(ShaderRecompiler::Spirv::Emitter::BdaLeanEnabled() ? ":bdalean" : "") +'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 572,
     'gets its own signature token AND its own directory - file names do not carry the', ''),
    (C, 'src/generate_version.cmake', 56, 'string(SHA1 KYTY_SHADER_SOURCE_HASH "${SHADER_DIGESTS}")', 'endif()'),
    ('18d9c792', 'docs/ROADMAP.md', 20029, '369. **Звено F10b трека F (`HPP-446`, лид): F10a (`HPP-445`) принят',
     '`KYTY_FIX_SVAL` (умолчание 0) с критерием «ИСПРАВЛЕНО Ф16» ниже; звенья F10c'),
    ('a922ffed', 'docs/ROADMAP.md', 20147,
     '**Поправка состава F11a (член (4), добавляется этим пунктом; F11a ещё `blocked`, не начат):** для 8 диспатчей EID 3399–3455 снимка',
     '`C:/kyty/f287/f7a/enemy_final_600.rdc` (`181cb236…`) — хэши CS и есть ли в их коде `IMAGE_BVH_INTERSECT_RAY` [c]; хэши — из уже снятых выходов'),
    ('9e60a8a5', 'docs/track-f/register.md', 390, '| Ф10 | K4 | наблюдение (путь достижим после Ф9 [I], исполнение [U])',
     '| Б9а | K4 | дефект (путь исполняется [c])'),
]
ok = True
out = []
for commit, path, line, anchor, nxt in REFS:
    r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True)
    if r.returncode != 0:
        out.append('FAIL %s:%s git show rc %d' % (commit, path, r.returncode))
        ok = False
        continue
    L = r.stdout.decode('utf-8', 'replace').replace(chr(13), '').split(chr(10))
    a = L[line - 1].strip() if line - 1 < len(L) else ''
    b = L[line].strip() if line < len(L) else ''
    good = anchor in a and (nxt in b)
    ok &= good
    out.append('%s %s:%s:%d' % ('OK  ' if good else 'FAIL', commit, path, line))
out.append('refs %d' % len(REFS))
out.append('ALL OK' if ok else 'FAIL')
text = chr(10).join(out) + chr(10)
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
open('C:/kyty/f287/f11a/refs_f11a.out.txt', 'wb').write(text.encode('utf-8'))
sys.stdout.write(text)
sys.exit(0 if ok else 1)
