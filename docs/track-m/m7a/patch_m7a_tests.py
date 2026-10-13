"""Track M, M7a (HPP-852, ROADMAP s122 item 767(g)): tests/shaderCfgTests.cpp - TestMWave1T306OffsetWriteMask extended
(forms same / other / full / lit, fallback counter, ConstOffset pair), new T306ConstOffsetOf and TestMWave1T306EbootPrograms
(text of t306_tests.cpp.txt beside this script), RUN line, and KYTY_RECOMPILE_T306=1 lines in the KYTY_RECOMPILE mode.
Usage: python patch_m7a_tests.py <tree>. LF only; every anchor must match once. Refuses under the lock."""
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3')
    sys.exit(3)
ROOT = sys.argv[1].rstrip('/') + '/'
HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
F = 'tests/shaderCfgTests.cpp'
NL = chr(10)
BS = chr(92)

raw = open(ROOT + F, 'rb').read()
if b'\r' in raw:
    raise SystemExit('CR in ' + F)
text = raw.decode('utf-8')
new_block = open(HERE + '/t306_tests.cpp.txt', 'rb').read().decode('utf-8')
if '\r' in new_block:
    raise SystemExit('CR in t306_tests.cpp.txt')

start = 'void TestMWave1T306OffsetWriteMask() {' + NL
end = 'void TestNewShaderRecompilerCfgStraightLine() {' + NL
assert text.count(start) == 1 and text.count(end) == 1
i, j = text.index(start), text.index(end)
assert i < j
old_block = text[i:j]
assert old_block.count('probe full-mask (no check)') == 1, 'unexpected old test body'
text = text[:i] + new_block + text[j:]

run_old = '  RUN(TestMWave1T306OffsetWriteMask);' + NL
assert text.count(run_old) == 1
text = text.replace(run_old, run_old + '  RUN(TestMWave1T306EbootPrograms);' + NL)

comp_old = (
    '    auto compiled = ShaderRecompiler::CompileProgram(' + NL +
    '        std::move(translated), options, specialization,' + NL +
    '        stored.program.bindings.push_data_start_dword);' + NL +
    '    const auto t2 = std::chrono::steady_clock::now();' + NL)
comp_new = (
    '    // Track M, M7a (HPP-852, ROADMAP s122 item 767(g)(1)): KYTY_RECOMPILE_T306=1 - one line per emitted' + NL +
    '    // IMAGE_SAMPLE_*_O with ConstOffset (pc, offset read from the SPIR-V words) and the MTexOffset lines of this compile.' + NL +
    '    const bool t306_probe = std::getenv("KYTY_RECOMPILE_T306") != nullptr;' + NL +
    '    const auto t306_before = ShaderRecompiler::Spirv::Emitter::MTexOffsetFallbacks();' + NL +
    '    if (t306_probe) {' + NL +
    '      ShaderRecompiler::Spirv::Emitter::MTexOffsetRecording(true);' + NL +
    '    }' + NL +
    comp_old +
    '    if (t306_probe) {' + NL +
    '      const auto t306_records = ShaderRecompiler::Spirv::Emitter::MTexOffsetTakeRecords();' + NL +
    '      ShaderRecompiler::Spirv::Emitter::MTexOffsetRecording(false);' + NL +
    '      const auto t306_after = ShaderRecompiler::Spirv::Emitter::MTexOffsetFallbacks();' + NL +
    '      for (const auto &record : t306_records) {' + NL +
    '        std::array<int32_t, 3> xyz{};' + NL +
    '        uint32_t components = 0;' + NL +
    '        const bool readable = T306ConstOffsetOf(compiled.spirv, record.sample_id, record.offset_id, xyz, components);' + NL +
    '        std::printf("recompile-t306: hash=%016llx pc=0x%x x=%d y=%d z=%d components=%u path=%s' + BS + 'n",' + NL +
    '                    static_cast<unsigned long long>(record.shader_hash), record.pc, xyz[0], xyz[1], xyz[2], components,' + NL +
    '                    readable ? "const" : "unreadable");' + NL +
    '      }' + NL +
    '      std::printf("recompile-t306-fallback: nonconstant=%u cube=%u range=%u records=%zu' + BS + 'n",' + NL +
    '                  t306_after.nonconstant - t306_before.nonconstant, t306_after.cube - t306_before.cube,' + NL +
    '                  t306_after.range - t306_before.range, t306_records.size());' + NL +
    '    }' + NL)
assert text.count(comp_old) == 1
text = text.replace(comp_old, comp_new)
open(ROOT + F, 'wb').write(text.encode('utf-8'))
print('patched', F)
