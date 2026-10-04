# F23a (HPP-578) STAGE 2 of the worktree-only diagnostic patch (after patch_f23a_wt.py): the decode mode
# (KYTY_F23A_DECODE) reads list lines "F|<path>" as merged-stage front programs (they end at S_SETPC_B64 s[6:7]) and
# decodes them with Decoder::DecodeFrontProgram, as ShaderRecompiler.cpp does for them; other lines - DecodeProgram.
p = 'C:/kyty/f287/f23a/wt/tests/shaderCfgTests.cpp'
s = open(p, encoding='utf-8').read()
old = '''    std::vector<uint32_t> code;
    {
      FILE* f = std::fopen(paths[i].c_str(), "rb");'''
new = '''    std::vector<uint32_t> code;
    const bool front = paths[i].rfind("F|", 0) == 0;
    if (front) { paths[i] = paths[i].substr(2); }
    {
      FILE* f = std::fopen(paths[i].c_str(), "rb");'''
assert s.count(old) == 1, ('a', s.count(old))
s = s.replace(old, new)
old = '''    std::fprintf(out, "P %zu %s words=%zu\\n", i, paths[i].c_str(), code.size());
    std::fflush(out);
    Decoder::Program program;
    Decoder::DecodeProgram(std::span<const uint32_t>{code}, program);'''
new = '''    std::fprintf(out, "P %zu %s words=%zu front=%d\\n", i, paths[i].c_str(), code.size(), front ? 1 : 0);
    std::fflush(out);
    Decoder::Program program;
    if (front) {
      program = Decoder::DecodeFrontProgram(std::span<const uint32_t>{code});
    } else {
      Decoder::DecodeProgram(std::span<const uint32_t>{code}, program);
    }'''
assert s.count(old) == 1, ('b', s.count(old))
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('stage 2 patched')
