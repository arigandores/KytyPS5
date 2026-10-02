"""S7: references <commit>:<path>:<line> with an anchor and the +1 control (general rule 24(1)).
ASCII output only; ends with ALL OK."""
import hashlib
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
P = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
REFS = [
    # (commit, path, line, anchor on the line, anchor on line+1)
    ('4fc501f4', P, 5751, 'void Info(const T& info) {', 'const auto*  base  = reinterpret_cast<const uint8_t*>(&info);'),
    ('4fc501f4', P, 5756, 'std::array<uint8_t, sizeof(T)> bytes {};', 'std::memcpy(bytes.data(), base, off);'),
    ('4fc501f4', P, 6358, 'if (m_compute_pipelines.contains(program.id)) {', 'skipped++;'),
    ('4fc501f4', P, 6276, 'if (m_graphics_pipelines.contains(key)) {', 'skipped++;'),
    ('4fc501f4', P, 6262, 'if (!m_program_cache->Resolve(vs_key, vs_index, vs_loaded ? &vs_entry : nullptr,', 'vs_program, vs_compiled) ||'),
    ('4fc501f4', P, 6425, 'LOGF("PipelinePrecache: %u recipes -> %u graphics + %u compute pipelines queued, %u skipped, "',
     '"%u sources loaded, %s, %" PRIu64 " ms (scratch: %u pipelines, max %u dwords/thread)\\n",'),
    ('4fc501f4', P, 4514, 'if (index >= entry->second.permutations.size()) {', 'return false;'),
    ('4fc501f4', 'src/graphics/shader/shader.h', 0, 'bool               tg_size_en                 = false;', 'ShaderStageRuntime stage;'),
    ('8f6b6be2', P, 5877, 'void Info(const T& info) {', 'const auto*  base  = reinterpret_cast<const uint8_t*>(&info);'),
    ('8f6b6be2', P, 0, 'spvtools::SpirvTools tools(SPV_ENV_VULKAN_1_3);', 'std::string          messages;'),
    ('8f6b6be2', P, 0, 'if (!ValidateShaderSpirv(options.dump_label, options.shader_hash, result.spirv)) {',
     'DumpShaderSpirv(stage_name, options.shader_hash, result.spirv);'),
    ('8f6b6be2', 'src/launcher/include/configuration.h', 98, 'bool                   shader_validation_enabled   = true;',
     'ShaderOptimizationType shader_optimization_type    = ShaderOptimizationType::Performance;'),
    ('8f6b6be2', 'src/graphics/presentation/window/vulkanWindow.cpp', 705,
     'features12.uniformBufferStandardLayout = supported_features12.uniformBufferStandardLayout;',
     'ShaderRecompiler::IR::SetConstBankSupported(features12.uniformBufferStandardLayout == VK_TRUE &&'),
    ('8f6b6be2', 'tests/shaderCfgTests.cpp', 0, '(is_vertex && key.static_state.size() != 8) ||', '(is_pixel && key.static_state.size() < 30)) {'),
    ('8f6b6be2', 'src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp', 0,
     'default: EXIT("unsupported scalar source operand 0x%08x at pc 0x%08x", code, pc);', '}'),
    ('8f6b6be2', 'src/generate_version.cmake', 0, 'file(SHA1 "${SHADER_SOURCE}" SHADER_DIGEST)',
     'string(APPEND SHADER_DIGESTS "${SHADER_DIGEST}\\n")'),
]


def main():
    ok = True
    print('suite refs_s7 sha256', hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
    for c, path, line, a0, a1 in REFS:
        text = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, path)], capture_output=True).stdout
        lines = text.decode('utf-8', 'replace').replace('\r', '').split('\n')
        if line == 0:
            hits = [i + 1 for i, x in enumerate(lines) if x.strip() == a0]
            line = hits[0] if len(hits) == 1 else -len(hits)
        good = line > 0 and lines[line - 1].strip() == a0 and lines[line].strip() == a1
        ok &= good
        print('%s %s:%s:%d %s' % ('OK  ' if good else 'FAIL', c, path, line, a0[:70]))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
