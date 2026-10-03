"""Track F, link F10c (HPP-451), ROADMAP s122 item 369(b): KYTY_FIX_SVAL (default OFF).

Usage: python patch_f10c.py <repo root>   (C:/kyty/KytyPS5 or the F10c worktree)
Three files, anchors are whole lines, each must match exactly once; LF kept (CR stripped before the search and
put back if the file had CRLF). Prints one line per edit and ALL OK.
"""
import sys

ROOT = sys.argv[1].rstrip('/')
ok = True


def patch(rel, edits):
    global ok
    path = ROOT + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.replace(b'\r\n', b'\n').decode('utf-8')
    lines = text.split('\n')
    for name, anchor, where, new in edits:
        idx = [i for i, l in enumerate(lines) if l == anchor]
        if len(idx) != 1:
            print('FAIL %s %s: anchor found %d times' % (rel, name, len(idx)))
            ok = False
            continue
        i = idx[0]
        if where == 'after':
            lines[i + 1:i + 1] = new
        elif where == 'before':
            lines[i:i] = new
        elif where == 'after2':
            if lines[i + 1] != T + 'EXIT_NOT_IMPLEMENTED(!Common::Thread::IsMainThread());':
                print('FAIL %s %s: line after the anchor is %r' % (rel, name, lines[i + 1]))
                ok = False
                continue
            lines[i + 2:i + 2] = new
        elif where == 'replace':
            lines[i:i + 1] = new
        print('%s %s: %s line %d' % (rel, name, where, i + 1))
    out = '\n'.join(lines).encode('utf-8')
    if crlf:
        out = out.replace(b'\n', b'\r\n')
    open(path, 'wb').write(out)


T = '\t'

patch('src/graphics/host_gpu/graphicContext.h', [
    ('field', T + 'uint32_t                           max_fragment_dual_src_attachments     = 0;', 'after', [
        T + '// Track F, F10c (HPP-451, ROADMAP s122 item 369(b), row F16): uniformBufferStandardLayout as enabled on the device',
        T + '// (set in VulkanCreateDevice next to features12); PipelineCache copies it for ValidateShaderSpirv (KYTY_FIX_SVAL=1).',
        T + 'bool                               uniform_buffer_standard_layout_enabled = false;',
    ]),
])

patch('src/graphics/presentation/window/vulkanWindow.cpp', [
    ('enable', T + 'features12.uniformBufferStandardLayout = supported_features12.uniformBufferStandardLayout;', 'after', [
        T + '// Track F, F10c (HPP-451, ROADMAP s122 item 369(b)): the value enabled here, for the SPIR-V check (KYTY_FIX_SVAL=1).',
        T + 'graphics.uniform_buffer_standard_layout_enabled = features12.uniformBufferStandardLayout == VK_TRUE;',
    ]),
])

patch('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    ('helpers', 'bool ValidateShaderSpirv(const char* label, uint64_t shader_hash,', 'before', [
        '// Track F, F10c (HPP-451, ROADMAP s122 item 369(b), row F16): KYTY_FIX_SVAL (default OFF: unset, "", 0/false/off/no = OFF,',
        '// as Common::EnvValueOn; read once). ON: ValidateShaderSpirv validates with spvtools::ValidatorOptions where',
        '// SetUniformBufferStandardLayout(true) is set if and only if the device enabled uniformBufferStandardLayout',
        '// (g_fix_sval_ubo_std_layout: stored by the PipelineCache constructor from GraphicContext before its workers start and',
        '// before any translation), and logs "FixSvalStat: validated=<n> rejected=<m>" on every 256th check (n - checks made,',
        '// m - checks rejected). OFF: the old call tools.Validate(spirv) without options, no counters, no line.',
        'bool FixSvalEnabled() {',
        T + 'static const bool enabled = Common::EnvValueOn(std::getenv("KYTY_FIX_SVAL"));',
        T + 'return enabled;',
        '}',
        '',
        'std::atomic<bool> g_fix_sval_ubo_std_layout {false};',
        '',
    ]),
    ('validate', T + 'if (tools.Validate(spirv)) {', 'replace', [
        T + '// Track F, F10c (KYTY_FIX_SVAL, see FixSvalEnabled): ON - the options of the device; OFF - the old call.',
        T + 'bool valid = false;',
        T + 'if (FixSvalEnabled()) {',
        T + T + 'spvtools::ValidatorOptions options;',
        T + T + 'if (g_fix_sval_ubo_std_layout.load(std::memory_order_acquire)) {',
        T + T + T + 'options.SetUniformBufferStandardLayout(true);',
        T + T + '}',
        T + T + 'valid = tools.Validate(spirv.data(), spirv.size(), options);',
        T + T + 'static std::atomic<uint64_t> validated {0};',
        T + T + 'static std::atomic<uint64_t> rejected {0};',
        T + T + 'if (!valid) {',
        T + T + T + 'rejected.fetch_add(1, std::memory_order_relaxed);',
        T + T + '}',
        T + T + 'const uint64_t checks = validated.fetch_add(1, std::memory_order_relaxed) + 1;',
        T + T + 'if (checks % 256u == 0) {',
        T + T + T + 'LOGF("FixSvalStat: validated=%" PRIu64 " rejected=%" PRIu64 "\\n", checks,',
        T + T + T + '     rejected.load(std::memory_order_relaxed));',
        T + T + '}',
        T + '} else {',
        T + T + 'valid = tools.Validate(spirv);',
        T + '}',
        T + 'if (valid) {',
    ]),
    ('ctor', '    : m_graphics(graphics), m_program_cache(std::make_unique<ProgramCache>(graphics.device)) {', 'after2', [
        T + '// Track F, F10c (HPP-451, ROADMAP s122 item 369(b)): the device value for ValidateShaderSpirv, stored before',
        T + '// StartWorkers / StartPrecache below; CompilePermutation (the only caller) runs only through this object.',
        T + 'g_fix_sval_ubo_std_layout.store(graphics.uniform_buffer_standard_layout_enabled, std::memory_order_release);',
        T + 'LOGF("FixSval: mode=%d ubo_std_layout=%d\\n", FixSvalEnabled() ? 1 : 0,',
        T + '     graphics.uniform_buffer_standard_layout_enabled ? 1 : 0);',
    ]),
])
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
