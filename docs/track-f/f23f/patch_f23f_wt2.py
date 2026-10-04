# F23f (HPP-592) stage 4 of the worktree-only diagnostic patch (after patch_f23f_wt.py): the SPIR-V is emitted by
# CompileProgram, after the F23a census; so the id hook stays set until CompileProgram returns and the census is written a
# second time on compiled.program into "<KYTY_F23A_SELDIAG>.post" (with the ids). The first line (before CompileProgram) is the
# F23a count unchanged; the reader requires the form-A items of both lines to be equal (b, i, depth, new, old).
import sys

p = 'C:/kyty/f287/f23f/wt/tests/shaderCfgTests.cpp'
raw = open(p, 'rb').read()
crlf = b'\r\n' in raw
s = raw.decode('utf-8').replace('\r\n', '\n')


def sub_once(text, old, new):
    n = text.count(old)
    if n != 1:
        print('SUBSTRING FAIL', repr(old[:80]), n)
        sys.exit(1)
    return text.replace(old, new)


s = sub_once(s, '''    if (f23a_seldiag != nullptr) {
      ShaderRecompiler::Spirv::Emitter::g_f23f_defs = nullptr;
      ShaderRecompiler::Frontend::g_f23a_exec_selects = nullptr;''', '''    if (f23a_seldiag != nullptr) {
      ShaderRecompiler::Frontend::g_f23a_exec_selects = nullptr;''')
s = sub_once(s, '''    auto compiled = ShaderRecompiler::CompileProgram(
        std::move(translated), options, specialization,
        stored.program.bindings.push_data_start_dword);
''', '''    auto compiled = ShaderRecompiler::CompileProgram(
        std::move(translated), options, specialization,
        stored.program.bindings.push_data_start_dword);
    if (f23a_seldiag != nullptr) {
      ShaderRecompiler::Spirv::Emitter::g_f23f_defs = nullptr;
      const std::string f23f_post = std::string(f23a_seldiag) + ".post";
      F23aSelDiag(f23f_post.c_str(), compiled.program, f23a_created, key.hash, key.stage, permutation, parts[0].c_str());
    }
''')
if crlf:
    s = s.replace('\n', '\r\n')
open(p, 'wb').write(s.encode('utf-8'))
print('stage 4 patched')
print('ALL OK')
