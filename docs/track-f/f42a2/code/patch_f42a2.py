# F42a2 (HPP-805, ROADMAP s122 item 705(b)(1)-(4)): stand edition 2 of row F20 - arm E (E-W, E-X) through the emulator's
# CreateCachedModule. Edits (whole-line anchors, each must match exactly once; LF in, LF out, CR refused):
#  - pipelineCache.cpp: CreateCachedModule leaves the anonymous namespace (namespace closed before its comment, reopened
#    after its closing brace); the body is not touched;
#  - pipelineCache.h: its declaration;
#  - fixF20.h / fixF20.cpp: getters Calls(), Rewritten() of the FixF20Stat totals (added lines only);
#  - tests/ShaderRecompilerComputeTests.cpp: VulkanHarness::SetExternalModule + Dispatch uses it; stand arms E-W, E-X.
# Usage: python patch_f42a2.py <repo root>
import sys

ROOT = sys.argv[1].rstrip('/') + '/'
NL = chr(10)


def load(path):
    data = open(ROOT + path, 'rb').read()
    if b'\r' in data:
        raise SystemExit('CR in ' + path)
    return data.decode('utf-8').split(NL)


def save(path, lines):
    open(ROOT + path, 'wb').write(NL.join(lines).encode('utf-8'))


def find(lines, anchor, start=0):
    hits = [i for i in range(start, len(lines)) if lines[i] == anchor]
    if len(hits) != 1:
        raise SystemExit('anchor %r: %d hits' % (anchor, len(hits)))
    return hits[0]


def find_block(lines, block):
    hits = [i for i in range(len(lines) - len(block) + 1) if lines[i:i + len(block)] == block]
    if len(hits) != 1:
        raise SystemExit('block %r: %d hits' % (block[0], len(hits)))
    return hits[0]


done = []

# ---------------------------------------------------------------- pipelineCache.cpp
P = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
L = load(P)
i = find(L, '// Salt only the module passed to Vulkan, including modules loaded from translation/seed caches.')
L[i:i] = [
    '} // namespace',
    '',
    '// Track F, F42a2 (HPP-805, ROADMAP s122 item 705(b)(1)): CreateCachedModule is outside the anonymous namespace - declared',
    '// in pipelineCache.h for the stand arm E (shader_recompiler_compute_tests --f20-stand); its body is unchanged.',
]
f = find(L, 'vk::ShaderModule CreateCachedModule(vk::Device device, const std::vector<uint32_t>& translation, bool fault_bound) {')
r = find(L, '\treturn CompileSPV(*words, device);', f)
if L[r + 1] != '}' or L[r + 2] != '':
    raise SystemExit('end of CreateCachedModule')
L[r + 2:r + 2] = ['', 'namespace {']
save(P, L)
done.append(P)

# ---------------------------------------------------------------- pipelineCache.h
P = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.h'
L = load(P)
i = find(L, 'void LogPipelineTrace(const char* phase, uint64_t vertex_program_id, uint64_t pixel_program_id);')
L[i:i] = [
    '// Track F, F42a2 (HPP-805, ROADMAP s122 item 705(b)(1)): the Vulkan module of a translation as the emulator creates it at',
    '// places 1-3 (FixF20 at KYTY_FIX_F20=1, the KYTY_PIPELINE_SALT salt, CompileSPV); pipelineCache.cpp.',
    'vk::ShaderModule CreateCachedModule(vk::Device device, const std::vector<uint32_t>& translation, bool fault_bound);',
]
save(P, L)
done.append(P)

# ---------------------------------------------------------------- fixF20.h
P = 'src/graphics/host_gpu/renderer/pipeline/fixF20.h'
L = load(P)
i = find(L, 'void PrintExitStat();')
L[i + 1:i + 1] = [
    '',
    '// Track F, F42a2 (HPP-805, ROADMAP s122 item 705(b)(1)): the totals calls and rewritten of the "FixF20Stat:" line, read',
    '// by the stand arm E (the log of the test process is silent; at 0 there is no line).',
    'uint64_t Calls();',
    'uint64_t Rewritten();',
]
save(P, L)
done.append(P)

# ---------------------------------------------------------------- fixF20.cpp
P = 'src/graphics/host_gpu/renderer/pipeline/fixF20.cpp'
L = load(P)
i = find(L, '} // namespace Libs::Graphics::FixF20')
L[i:i] = [
    '// Track F, F42a2 (HPP-805, ROADMAP s122 item 705(b)(1)): getters for the stand arm E.',
    'uint64_t Calls() {',
    '\treturn g_calls.load();',
    '}',
    '',
    'uint64_t Rewritten() {',
    '\treturn g_rewritten.load();',
    '}',
    '',
]
save(P, L)
done.append(P)

# ---------------------------------------------------------------- tests/ShaderRecompilerComputeTests.cpp
P = 'tests/ShaderRecompilerComputeTests.cpp'
L = load(P)

# VulkanHarness: setter, Dispatch uses the external module, member.
i = find(L, '  void Dispatch(const TestCase &test, const CompiledShader &compiled,')
L[i:i] = [
    '  // Track F, F42a2 (HPP-805, ROADMAP s122 item 705(b)(1)): the stand arm E dispatches a module created by the emulator',
    '  // (Libs::Graphics::CreateCachedModule). While set, Dispatch binds it in place of the module it creates from',
    '  // compiled.spirv (that one is still created and destroyed); the caller destroys the external module.',
    '  void SetExternalModule(vk::ShaderModule module) { m_external_module = module; }',
    '',
]
b = find_block(L, [
    '    vk::ShaderModule module = nullptr;',
    '    RequireVk(test.name, "SPIR-V module",',
    '              m_device.createShaderModule(&module_info, nullptr, &module),',
    '              "vkCreateShaderModule");',
])
L[b + 4:b + 4] = [
    '    const vk::ShaderModule own_module = module; // Track F, F42a2: SetExternalModule',
    '    if (m_external_module != nullptr) {',
    '      module = m_external_module;',
    '    }',
]
d = find(L, '    m_device.destroyShaderModule(module, nullptr);', b)
L[d] = '    m_device.destroyShaderModule(own_module, nullptr);'
i = find(L, '  Buffer m_fault_readback; // Track F, F42a: host copy of m_fault_buffer (ReadFaultBuffer)')
L[i + 1:i + 1] = ['  vk::ShaderModule m_external_module = nullptr; // Track F, F42a2: SetExternalModule (stand arm E)']

# Stand: comment, arms, helpers.
i = find(L, '// the order of the four arms in every round).')
L[i + 1:i + 1] = [
    '// Edition 2 (Track F, F42a2 HPP-805, ROADMAP s122 item 705(b)(1)): arms E-W and E-X - the programs of W and X, the',
    '// module created by the emulator for places 1-3 - Libs::Graphics::CreateCachedModule(device, translation, true): the',
    '// knob is FixF20::Mode() of the process (the stand reads nothing for it), KYTY_PIPELINE_SALT must be unset; the calls /',
    '// rewritten of FixF20 around it and in total are printed ("F20Stand: emu", "F20Stand: emu_stat"). Six arms per round.',
]
i = find(L, 'enum class F20Arm : u32 { W, X, S, N };')
L[i] = 'enum class F20Arm : u32 { W, X, S, N, EW, EX };'
L[i + 1:i + 1] = ['constexpr u32 F20Arms = 6u; // Track F, F42a2: edition 2']
i = find(L, '  case F20Arm::N: return "N";')
L[i + 1:i + 1] = ['  case F20Arm::EW: return "E-W";', '  case F20Arm::EX: return "E-X";']
i = find(L, 'u32 F20Invocations(F20Arm arm) {')
L[i:i] = [
    '// Track F, F42a2: the arm E-W / E-X runs the program of W / X; its module comes from CreateCachedModule.',
    'F20Arm F20Program(F20Arm arm) { return arm == F20Arm::EW ? F20Arm::W : arm == F20Arm::EX ? F20Arm::X : arm; }',
    'bool F20Emu(F20Arm arm) { return arm == F20Arm::EW || arm == F20Arm::EX; }',
    '',
]
i = find(L, 'u32 F20Invocations(F20Arm arm) {')
L[i + 1:i + 1] = ['  arm = F20Program(arm);']
i = find(L, 'u32 F20RelativePage(F20Arm arm, u32 gid) {')
L[i + 1:i + 1] = ['  arm = F20Program(arm);']
i = find(L, 'TestCase F20StandCase(F20Arm arm) {')
L[i + 1:i + 1] = ['  const F20Arm name_arm = arm;', '  arm = F20Program(arm);']
i = find(L, '  test.name = arm == F20Arm::X ? "F20StandX" : arm == F20Arm::S ? "F20StandS" : arm == F20Arm::N ? "F20StandN" : "F20StandW";')
L[i] = ('  test.name = name_arm == F20Arm::EW ? "F20StandEW" : name_arm == F20Arm::EX ? "F20StandEX" : arm == F20Arm::X ? '
        '"F20StandX" : arm == F20Arm::S ? "F20StandS" : arm == F20Arm::N ? "F20StandN" : "F20StandW";')

# F20StandMain.
m = find(L, 'int F20StandMain() {')
i = find(L, '  const bool fix = Common::EnvFlagOn("KYTY_FIX_F20");', m)
L[i + 1:i + 1] = [
    '  // Track F, F42a2 (ROADMAP s122 item 705(b)(1)): the arm E reads no knob itself - CreateCachedModule reads',
    '  // FixF20::Mode() of the process; its value is printed next to `fix` (the edition 1 arms). The salt changes the module.',
    '  const int emu_mode = Libs::Graphics::FixF20::Mode();',
    '  if (const char *salt = std::getenv("KYTY_PIPELINE_SALT"); salt != nullptr && salt[0] != 0) {',
    '    std::fprintf(stderr, "F20Stand: KYTY_PIPELINE_SALT is set - unset it (item 705(b)(1))\\n");',
    '    return 2;',
    '  }',
]
i = find(L, '    u32 rounds_with_loss = 0;', m)
L[i + 1:i + 1] = [
    '    vk::ShaderModule emu_module = nullptr; // Track F, F42a2: arm E only',
    '    uint64_t emu_calls = 0;',
    '    uint64_t emu_rewritten = 0;',
]
i = find(L, '  std::array<ArmData, 4> arms;', m)
L[i] = '  std::array<ArmData, F20Arms> arms;'
i = find(L, '  for (u32 a = 0; a < 4u; a++) {', m)
L[i] = '  for (u32 a = 0; a < F20Arms; a++) {'
i = find(L, '    if (fix && d.stats.rewritten != 0) {', m)
L[i] = '    if (fix && d.stats.rewritten != 0 && !F20Emu(d.arm)) { // arm E: the words stay the translation (stats - form line)'
i = find(L, '    d.compiled.spirv = std::move(words);', m)
L[i + 1:i + 1] = [
    '    if (F20Emu(d.arm)) {',
    '      // The module of the arm E: CreateCachedModule of the emulator, translation = the translator\'s words of the arm,',
    '      // the FaultBuffer binding flag true; FixF20 calls / rewritten of the process before and after the call.',
    '      const uint64_t calls0 = Libs::Graphics::FixF20::Calls();',
    '      const uint64_t rewritten0 = Libs::Graphics::FixF20::Rewritten();',
    '      d.emu_module = Libs::Graphics::CreateCachedModule(vulkan.Device(), d.compiled.spirv, true);',
    '      d.emu_calls = Libs::Graphics::FixF20::Calls() - calls0;',
    '      d.emu_rewritten = Libs::Graphics::FixF20::Rewritten() - rewritten0;',
    '      std::printf("F20Stand: emu mode=%d emu_mode=%d arm=%s bound_flag=1 calls=%llu rewritten=%llu module=%d\\n",',
    '                  fix ? 1 : 0, emu_mode, F20ArmName(d.arm), static_cast<unsigned long long>(d.emu_calls),',
    '                  static_cast<unsigned long long>(d.emu_rewritten), d.emu_module != nullptr ? 1 : 0);',
    '    }',
]
i = find(L, '    std::array<u32, 4> order{0, 1, 2, 3};', m)
L[i] = '    std::array<u32, F20Arms> order{0, 1, 2, 3, 4, 5};'
i = find(L, '    for (u32 i = 3; i > 0; i--) {', m)
L[i] = '    for (u32 i = F20Arms - 1u; i > 0; i--) {'
i = find(L, '    for (u32 position = 0; position < 4u; position++) {', m)
L[i] = '    for (u32 position = 0; position < F20Arms; position++) {'
i = find(L, '      vulkan.Dispatch(d.test, d.compiled, buffer);', m)
L[i:i + 1] = [
    '      vulkan.SetExternalModule(d.emu_module); // nullptr for W, X, S, N',
    '      vulkan.Dispatch(d.test, d.compiled, buffer);',
    '      vulkan.SetExternalModule(nullptr);',
]
i = find(L, '  std::printf("F20Stand: done\\n");', m)
L[i:i] = [
    '  std::printf("F20Stand: emu_stat mode=%d emu_mode=%d calls=%llu rewritten=%llu\\n", fix ? 1 : 0, emu_mode,',
    '              static_cast<unsigned long long>(Libs::Graphics::FixF20::Calls()),',
    '              static_cast<unsigned long long>(Libs::Graphics::FixF20::Rewritten()));',
    '  for (const auto &d : arms) {',
    '    if (d.emu_module != nullptr) {',
    '      vulkan.Device().destroyShaderModule(d.emu_module, nullptr);',
    '    }',
    '  }',
]
save(P, L)
done.append(P)

for p in done:
    print('patched', p)
print('PATCH OK')
