# F28a (HPP-698): check of the <commit>:<path>:<line> references of f28a.md (general rule 24(1)): each anchor is a WHOLE
# line (stripped) that occurs exactly once in the file at the commit, the +1 control is the next line (stripped); the
# script prints the reference with the line number found.  Exit 0 and ALL OK when every reference holds.
import subprocess, sys

REPO = 'C:/kyty/KytyPS5'
FS10 = 'dc5d4712'
P = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp'
M = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp'
F = 'src/graphics/host_gpu/renderer/cache/faultManager.cpp'
C = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
REFS = [
    ('R1', FS10, P, 'constexpr uint64_t BvhLoopCapDefaultHash = 0x380bb9d636390baeull;',
     'constexpr uint32_t BvhLoopCapDefault     = 65536;'),
    ('R2', FS10, P, 'if (const char* value = std::getenv("KYTY_BVH_LOOP_CAP"); value != nullptr) {',
     'result.cap = static_cast<uint32_t>(std::strtoul(value, nullptr, 10));'),
    ('R3', FS10, P, 'const int  cap_slot = BvhLoopCap() != 0 ? BvhLoopCapSlot(program.shader_hash) : -1;',
     'if (cap_slot >= 0 && state.program.dispatcher_fallback) {'),
    ('R4', FS10, P, 'state.builder.AddFunction(spv::OpUGreaterThan, TypeBool(state), over, next,',
     'ConstantU32(state, guards.limit));'),
    ('R5', FS10, P, 'state.builder.AddFunction(spv::OpBranchConditional, over, abort_label, after_label);',
     'EmitLabel(state, abort_label);'),
    ('R6', FS10, P, 'EmitLoopCapNear(ctx.state); // no-op unless KYTY_BVH_LOOP_CAP covers the program',
     'EmitReturnTail(ctx);'),
    ('R7', FS10, P, 'for (const auto variable: loop_guards.declared) {', 'state.builder.AddFunction(spv::OpVariable,'),
    ('R8', FS10, P, 'const auto ballot = ctx.Ballot(info.condition);', 'const auto low    = ctx.state.builder.AllocateId();'),
    ('R9', FS10, M, 'void EmitLoopCapTrip(EmitterState& state, uint32_t budget) {', 'if (state.fault_buffer_variable == 0) {'),
    ('R10', FS10, M, 'FaultElementPointer(state, ConstantU32(state, word)),', 'ConstantU32(state, spv::ScopeDevice),'),
    ('R11', FS10, M, 'const auto beyond = Binary(state, spv::OpUGreaterThan, TypeBool(state), spent,',
     'ConstantU32(state, state.loop_cap_limit >> 4));'),
    ('R12', FS10, F, 'LoopTripOffset + LoopTripBytes),',
     'm_download_buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,'),
    ('R13', FS10, F, 'const bool trips       = LoopCap::BvhLoopCap() != 0;',
     'const auto trip_offset = m_current_area * LoopTripBytes;'),
    ('R14', FS10, F, 'if ((trip_delta != 0 || near_delta != 0) && m_trip_lines < 64) {', 'm_trip_lines++;'),
    ('R15', FS10, 'src/graphics/host_gpu/renderer/renderContext.cpp', 'if (m_fault_process_pending) {',
     'm_fault_process_pending = false;'),
    ('R16', FS10, C, 'LOGF("ShaderFirstUse: hash=%016" PRIx64 " stage=%u words=%zu ud=%zu host_us=%" PRIu64 "\\n",',
     'params.hash, static_cast<uint32_t>(stage), params.code.size(), params.user_data.size(), HostMicros());'),
    ('R17', FS10, C, 'LOGF("AsyncCompute: prefetch hash=0x%016" PRIx64 " id=%" PRIu64 " queued\\n", params.hash, program.id);',
     '}'),
    ('R18', FS10, C, 'prepared = pretranslation.Take(params.code, params.hash, input_info,',
     'static_cast<uint32_t>(params.user_data.size()));'),
    ('R19', FS10, 'src/graphics/host_gpu/renderer/masterSemaphore.cpp',
     'diagnostic ? uint64_t {2000000000} : UINT64_MAX);', 'if (diagnostic && result == vk::Result::eTimeout) {'),
    ('R20', FS10, 'src/graphics/host_gpu/renderer/masterSemaphore.cpp',
     'const auto result  = m_graphics.device.getSemaphoreCounterValue(m_semaphore, &counter);',
     'if (result == vk::Result::eErrorDeviceLost) {'),
    ('R21', FS10, 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
     'const std::string variant = ShaderRecompiler::Spirv::Emitter::BvhLoopCapSignatureToken() +',
     '(ShaderRecompiler::Spirv::Emitter::BdaLeanEnabled() ? ":bdalean" : "") +'),
    ('R23', FS10, P, 'LOGF("BvhLoopCap: shader=0x%016" PRIx64 " loops=%zu cap=%u slot=%d\\n", program.shader_hash,',
     'loop_guards.variables.size(), BvhLoopCap(), cap_slot);'),
    ('R24', FS10, F, 'LOGF("BvhLoopCapTrip: trips=+%u total=%u near=+%u near_total=%u max_spent=%u "',
     '"cap=%u slot0=%u slot1=%u\\n",'),
    ('R25', FS10, 'src/graphics/host_gpu/renderer/pipeline/computePretranslation.h',
     'LOGF("CsPretranslate: miss hash=%016" PRIx64 " reason=%s\\n", hash, reason);', 'return std::nullopt;'),
    ('R22', '1833ee28', 'tests/shaderCfgTests.cpp',
     'if (const char *recompile = std::getenv("KYTY_RECOMPILE"); recompile != nullptr) {',
     '// Offline recompilation: KYTY_RECOMPILE="<gcn.bin>;<cache.bin>;<out.spv>[;<permutation>]"'),
]


def main():
    ok = True
    for rid, commit, path, anchor, plus1 in REFS:
        text = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
        lines = [l.strip() for l in text.decode('utf-8').splitlines()]
        hits = [i for i, l in enumerate(lines) if l == anchor]
        good = len(hits) == 1
        nxt = lines[hits[0] + 1] if good and hits[0] + 1 < len(lines) else None
        if good and plus1 is not None:
            good = nxt == plus1
        ok &= good
        print('%-4s %s %s:%s:%s  anchor x%d  +1 %s' % (rid, 'OK ' if good else 'BAD', commit, path,
                                                    hits[0] + 1 if hits else '?', len(hits),
                                                    'ok' if plus1 is None or nxt == plus1 else repr(nxt)))
        if plus1 is None and good:
            print('      +1 (printed, not fixed): %s' % nxt)
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
