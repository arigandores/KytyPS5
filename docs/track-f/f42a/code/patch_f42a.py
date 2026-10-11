"""F42a (HPP-779, ROADMAP s122 item 694(v)-(g)): KYTY_FIX_F20 (default 0) - code and stand patch, applied to a source
root (the main checkout or the FS12a worktree). Whole-line anchors, each must occur exactly the given number of times;
CR is stripped before the search and put back when the file had CRLF; LF write (write_bytes).
Usage: python patch_f42a.py <root> <code dir with fixF20.h, fixF20.cpp, *.inc>"""
import os
import shutil
import sys

ROOT, CODE = sys.argv[1], sys.argv[2]
P = 'src/graphics/host_gpu/renderer/pipeline/'


def inc(name):
    return open(os.path.join(CODE, name), encoding='utf-8').read().replace('\r\n', '\n')


def edit(path, pairs):
    full = os.path.join(ROOT, path)
    raw = open(full, 'rb').read().decode('utf-8')
    crlf = '\r\n' in raw
    text = raw.replace('\r\n', '\n')
    for old, new, count in pairs:
        n = text.count(old)
        if n != count:
            raise SystemExit('ANCHOR %s: %d occurrences, expected %d:\n%s' % (path, n, count, old[:200]))
        if not old.endswith('\n') or not (old.startswith('\n') or text.startswith(old) or ('\n' + old) in text):
            raise SystemExit('ANCHOR %s: not whole lines:\n%s' % (path, old[:200]))
        text = text.replace(old, new)
    if crlf:
        text = text.replace('\n', '\r\n')
    open(full, 'wb').write(text.encode('utf-8'))
    print('patched', path, len(pairs))


# --- new files -------------------------------------------------------------------------------------------------------
for name in ('fixF20.h', 'fixF20.cpp'):
    shutil.copyfile(os.path.join(CODE, name), os.path.join(ROOT, P + name))
    print('copied', P + name)

# --- pipelineCache.cpp -------------------------------------------------------------------------------------------------
edit(P + 'pipelineCache.cpp', [
    ('#include "graphics/host_gpu/renderer/pipeline/shaderReplay.h"\n',
     '#include "graphics/host_gpu/renderer/pipeline/shaderReplay.h"\n'
     '#include "graphics/host_gpu/renderer/pipeline/fixF20.h" // Track F, F42a (KYTY_FIX_F20)\n', 1),
    ('// Salt only the module passed to Vulkan, including modules loaded from translation/seed caches.\n'
     '// The saved translation stays unchanged; a new salt gives a fresh driver compilation experiment.\n'
     'vk::ShaderModule CreateCachedModule(vk::Device device, const std::vector<uint32_t>& source) {\n'
     '\tstd::vector<uint32_t> salted;\n',
     '// Track F, F42a (HPP-779, ROADMAP s122 item 694(v)(5)): the program has the FaultBuffer binding in the translator\'s\n'
     '// layout. Read before AdoptDmaLayout - KYTY_DMA_LAYOUT=1 adds the binding in memory without a module variable.\n'
     'bool FixF20Bound(const ShaderRecompiler::IR::BindingLayout& layout) {\n'
     '\treturn std::ranges::any_of(layout.descriptors, [](const auto& b) {\n'
     '\t\treturn b.kind == ShaderRecompiler::IR::DescriptorBindingKind::FaultBuffer;\n'
     '\t});\n'
     '}\n'
     '\n'
     '// Salt only the module passed to Vulkan, including modules loaded from translation/seed caches.\n'
     '// The saved translation stays unchanged; a new salt gives a fresh driver compilation experiment.\n'
     '// Track F, F42a (HPP-779, ROADMAP s122 item 694(v)(1)): at KYTY_FIX_F20=1 the fault bitmap writes of the module become\n'
     '// OpAtomicOr (FixF20::Apply, fixF20.h) before the salt; at 0 Apply is not called and `source` is the translation.\n'
     'vk::ShaderModule CreateCachedModule(vk::Device device, const std::vector<uint32_t>& translation, bool fault_bound) {\n'
     '\tstd::vector<uint32_t> fixed;\n'
     '\tconst bool            fix_f20 = FixF20::Mode() == 1 && FixF20::Apply(translation, fault_bound, fixed);\n'
     '\tconst auto&           source  = fix_f20 ? fixed : translation;\n'
     '\tstd::vector<uint32_t> salted;\n', 1),
    ('\t\tconst auto module_begin = HostMicros();\n'
     '\t\tconst auto module = CreateCachedModule(device, result.spirv);\n',
     '\t\tconst bool fault_bound  = FixF20Bound(result.program.bindings); // Track F, F42a: before AdoptDmaLayout\n'
     '\t\tconst auto module_begin = HostMicros();\n'
     '\t\tconst auto module       = CreateCachedModule(device, result.spirv, fault_bound);\n', 1),
    ('\n\t\t\tconst auto module = CreateCachedModule(device, p.spirv);\n',
     '\n\t\t\tconst bool fault_bound = FixF20Bound(p.program.bindings); // Track F, F42a: before AdoptDmaLayout\n'
     '\t\t\tconst auto module      = CreateCachedModule(device, p.spirv, fault_bound);\n', 1),
    ('\n\t\t\t\tconst auto module = CreateCachedModule(device, p.spirv);\n',
     '\n\t\t\t\tconst bool fault_bound = FixF20Bound(p.program.bindings); // Track F, F42a: before AdoptDmaLayout\n'
     '\t\t\t\tconst auto module      = CreateCachedModule(device, p.spirv, fault_bound);\n', 1),
    ('\n\t\t    .handle         = {.id = ++next_shader_id, .module = module},\n',
     '\n\t\t    .handle         = {.id = ++next_shader_id, .module = module, .fault_bound = fault_bound},\n', 1),
    ('\n\t\t\t    .handle         = {.id = ++next_shader_id, .module = module},\n',
     '\n\t\t\t    .handle         = {.id = ++next_shader_id, .module = module, .fault_bound = fault_bound},\n', 1),
    ('\n\t\t\t\t    .handle         = {.id = ++next_shader_id, .module = module},\n',
     '\n\t\t\t\t    .handle         = {.id = ++next_shader_id, .module = module, .fault_bound = fault_bound},\n', 1),
    ('\tReplayInit(); // track S, S17a: returns at once at KYTY_S_REPLAY=0\n',
     '\tReplayInit(); // track S, S17a: returns at once at KYTY_S_REPLAY=0\n'
     '\t(void)FixF20::Mode(); // Track F, F42a: "FixF20: mode=<0|1>" once, before the precache creates modules\n', 1),
])

# --- pipelineCache.h ---------------------------------------------------------------------------------------------------
edit(P + 'pipelineCache.h', [
    ('\tconst std::vector<uint32_t>* spirv = nullptr;\n',
     '\tconst std::vector<uint32_t>* spirv = nullptr;\n'
     '\t// Track F, F42a (HPP-779, ROADMAP s122 item 694(v)(5)): the translator\'s layout of the program has the FaultBuffer\n'
     '\t// binding - set with `module` at the three module sites of ProgramCache, read by the dual-source variant at\n'
     '\t// KYTY_FIX_F20=1.\n'
     '\tbool fault_bound = false;\n', 1),
])

# --- shaders.cpp -------------------------------------------------------------------------------------------------------
edit(P + 'shaders.cpp', [
    ('#include "graphics/host_gpu/renderer/pipeline/dualSrcBlend.h"\n',
     '#include "graphics/host_gpu/renderer/pipeline/dualSrcBlend.h"\n'
     '#include "graphics/host_gpu/renderer/pipeline/fixF20.h"\n', 1),
    ('\tconst auto module = CompileSPV(words, graphics.device);\n'
     '\tif (DualSourceFirstLine(ps_hash, true)) {\n',
     '\t// Track F, F42a (HPP-779, ROADMAP s122 item 694(v)(1)): at KYTY_FIX_F20=1 the fault bitmap writes of the variant\n'
     '\t// become OpAtomicOr as in CreateCachedModule (the binding flag comes with the handle); at 0 Apply is not called.\n'
     '\tstd::vector<uint32_t> fixed;\n'
     '\tconst bool            fix_f20 = FixF20::Mode() == 1 && FixF20::Apply(words, pixel_program.fault_bound, fixed);\n'
     '\tconst auto            module  = CompileSPV(fix_f20 ? fixed : words, graphics.device);\n'
     '\tif (DualSourceFirstLine(ps_hash, true)) {\n', 1),
])

# --- emulator.cpp ------------------------------------------------------------------------------------------------------
edit('src/emulator.cpp', [
    ('#include "graphics/presentation/window.h"\n',
     '#include "graphics/presentation/window.h"\n'
     '#include "graphics/host_gpu/renderer/pipeline/fixF20.h"\n', 1),
    ('\tif (!Libs::Graphics::WindowPrepareShaders()) {\n'
     '\t\tstd::quick_exit(0);\n',
     '\tif (!Libs::Graphics::WindowPrepareShaders()) {\n'
     '\t\tLibs::Graphics::FixF20::PrintExitStat(); // Track F, F42a: "FixF20Stat: when=exit" (KYTY_FIX_F20=1 only)\n'
     '\t\tstd::quick_exit(0);\n', 1),
    ('\tLibs::Graphics::WindowRun();\n'
     '\tstd::quick_exit(0);\n',
     '\tLibs::Graphics::WindowRun();\n'
     '\tLibs::Graphics::FixF20::PrintExitStat(); // Track F, F42a: "FixF20Stat: when=exit" (KYTY_FIX_F20=1 only)\n'
     '\tstd::quick_exit(0);\n', 1),
])

# --- tests/shaderCfgTests.cpp ------------------------------------------------------------------------------------------
edit('tests/shaderCfgTests.cpp', [
    ('#include "spirv-tools/libspirv.hpp"\n',
     '#include "graphics/host_gpu/renderer/pipeline/fixF20.h"\n'
     '#include "spirv-tools/libspirv.hpp"\n', 1),
    ('  if (const char *recompile = std::getenv("KYTY_RECOMPILE"); recompile != nullptr) {\n',
     inc('cfg_f20file.inc') +
     '  if (const char *recompile = std::getenv("KYTY_RECOMPILE"); recompile != nullptr) {\n', 1),
    ('    std::fwrite(compiled.spirv.data(), sizeof(uint32_t), compiled.spirv.size(), out);\n'
     '    std::fclose(out);\n',
     '    std::fwrite(compiled.spirv.data(), sizeof(uint32_t), compiled.spirv.size(), out);\n'
     '    std::fclose(out);\n' + inc('cfg_recompile_f20.inc'), 1),
])

# --- tests/ShaderRecompilerComputeTests.cpp ----------------------------------------------------------------------------
_rc = open(os.path.join(ROOT, 'tests/ShaderRecompilerComputeTests.cpp'), 'rb').read().decode('utf-8')
if '\n#include <bit>' not in _rc.replace('\r\n', '\n'):  # std::popcount of the stand
    edit('tests/ShaderRecompilerComputeTests.cpp', [('#include <algorithm>\n', '#include <algorithm>\n#include <bit>\n', 1)])
edit('tests/ShaderRecompilerComputeTests.cpp', [
    ('#include "spirv-tools/libspirv.hpp"\n',
     '#include "graphics/host_gpu/renderer/pipeline/fixF20.h"\n'
     '#include "common/envFlag.h"\n'
     '#include "spirv-tools/libspirv.hpp"\n', 1),
    ('  void Dispatch(const TestCase &test, const CompiledShader &compiled,\n',
     inc('readback.inc') +
     '  void Dispatch(const TestCase &test, const CompiledShader &compiled,\n', 1),
    ('    const auto usage = vk::BufferUsageFlagBits::eStorageBuffer |\n'
     '                       vk::BufferUsageFlagBits::eTransferDst;\n'
     '    m_bda_pagetable_buffer =\n',
     '    // Track F, F42a: eTransferSrc - ReadFaultBuffer copies m_fault_buffer out.\n'
     '    const auto usage = vk::BufferUsageFlagBits::eStorageBuffer |\n'
     '                       vk::BufferUsageFlagBits::eTransferDst |\n'
     '                       vk::BufferUsageFlagBits::eTransferSrc;\n'
     '    m_bda_pagetable_buffer =\n', 1),
    ('      DestroyBuffer(&m_fault_buffer);\n',
     '      DestroyBuffer(&m_fault_readback); // Track F, F42a\n'
     '      DestroyBuffer(&m_fault_buffer);\n', 1),
    ('  Buffer m_fault_buffer;\n',
     '  Buffer m_fault_buffer;\n'
     '  Buffer m_fault_readback; // Track F, F42a: host copy of m_fault_buffer (ReadFaultBuffer)\n', 1),
    ('void RunGraphicsCase(VulkanHarness *vulkan, const GraphicsCase &test) {\n',
     inc('stand_block.inc') +
     'void RunGraphicsCase(VulkanHarness *vulkan, const GraphicsCase &test) {\n', 1),
    ('  if (argc == 2 && std::strcmp(argv[1], "--reverse-rt-death") == 0) {\n',
     '  if (argc == 2 && std::strcmp(argv[1], "--f20-stand") == 0) {\n'
     '    return F20StandMain(); // Track F, F42a (ROADMAP s122 item 694(g)(1))\n'
     '  }\n'
     '  if (argc == 2 && std::strcmp(argv[1], "--reverse-rt-death") == 0) {\n', 1),
])
print('ALL PATCHED')
