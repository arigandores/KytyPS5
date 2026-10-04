# F23f (HPP-592, ROADMAP s122 item 498(g)(2)(v)): WORKTREE-ONLY diagnostic patch, stage 3 (after the F23a stages
# patch_f23a_wt.py + patch_f23a_wt2.py, copied with WT = C:/kyty/f287/f23f/wt; worktree on 4d9e8ab7 = source of the
# installed S12 adb0c82f). Never committed to main; main src/ is not changed; default behaviour unchanged (the hook
# pointer is null unless KYTY_F23A_SELDIAG is set in the offline KYTY_RECOMPILE mode of shader_cfg_tests).
#  (1) spirvEmitterProgram.cpp: Spirv::Emitter::g_f23f_defs (null by default) receives every (IR inst -> SPIR-V result id)
#      pair that ValueEmitContext::Result / Define put into their own map; no instruction of the module is changed.
#  (2) tests/shaderCfgTests.cpp: KYTY_F23A_SELDIAG items also carry the SPIR-V ids of the select ("sid") and of its
#      condition / new / old operands ("cid", "nid", "oid"; -1 = immediate or not defined); form-A items are always
#      printed (the 60000-character cap applies to the other items only).
# Anchors are whole lines (or exact unique substrings for the item format); CR is stripped and restored.
import sys

WT = 'C:/kyty/f287/f23f/wt/'


def load(rel):
    raw = open(WT + rel, 'rb').read()
    crlf = b'\r\n' in raw
    return raw.decode('utf-8').replace('\r\n', '\n'), crlf


def save(rel, text, crlf):
    if crlf:
        text = text.replace('\n', '\r\n')
    open(WT + rel, 'wb').write(text.encode('utf-8'))


def line_edit(text, anchor, mode, new):
    lines = text.split('\n')
    idx = [i for i, l in enumerate(lines) if l == anchor]
    if len(idx) != 1:
        print('ANCHOR FAIL', repr(anchor), len(idx))
        sys.exit(1)
    i = idx[0]
    block = new.split('\n')
    if mode == 'after':
        lines[i + 1:i + 1] = block
    elif mode == 'before':
        lines[i:i] = block
    elif mode == 'replace':
        lines[i:i + 1] = block
    return '\n'.join(lines)


def sub_once(text, old, new):
    n = text.count(old)
    if n != 1:
        print('SUBSTRING FAIL', repr(old[:80]), n)
        sys.exit(1)
    return text.replace(old, new)


# (1) emitter hook
rel = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp'
t, c = load(rel)
t = line_edit(t, 'namespace Libs::Graphics::ShaderRecompiler::Spirv::Emitter {', 'after',
              '// F23f (HPP-592) worktree-only diagnostic (not in main): IR inst -> SPIR-V id, filled only when non-null.\n'
              'std::unordered_map<const IR::Inst*, uint32_t>* g_f23f_defs = nullptr;')
t = line_edit(t, '	definitions.emplace(&inst, id);', 'after',
              '	if (g_f23f_defs != nullptr) {\n		(*g_f23f_defs)[&inst] = id;\n	}')
t = line_edit(t, '	definitions.emplace(&inst, value);', 'after',
              '	if (g_f23f_defs != nullptr) {\n		(*g_f23f_defs)[&inst] = value;\n	}')
save(rel, t, c)
print('patched', rel)

# (2) tests: extern, id helpers, item fields, hook set/reset around TranslateProgram
rel = 'tests/shaderCfgTests.cpp'
t, c = load(rel)
DECL = r'''// F23f (HPP-592) worktree-only diagnostic (not in main).
namespace Libs::Graphics::ShaderRecompiler::Spirv::Emitter {
extern std::unordered_map<const IR::Inst*, uint32_t>* g_f23f_defs;
} // namespace Libs::Graphics::ShaderRecompiler::Spirv::Emitter

namespace {
std::unordered_map<const Libs::Graphics::ShaderRecompiler::IR::Inst*, uint32_t> g_f23f_def_map;

long long F23fId(const Libs::Graphics::ShaderRecompiler::IR::Inst* inst) {
  const auto it = g_f23f_def_map.find(inst);
  return it == g_f23f_def_map.end() ? -1ll : static_cast<long long>(it->second);
}

long long F23fIdV(Libs::Graphics::ShaderRecompiler::IR::Value v) {
  v = v.Resolve();
  if (v.IsImmediate()) { return -1ll; }
  const auto* inst = v.TryInstruction();
  return inst == nullptr ? -1ll : F23fId(inst);
}
} // namespace
'''
t = line_edit(t, '// F23a (HPP-578) worktree-only diagnostic (not in main).', 'before', DECL)
t = sub_once(t, '      if (items.size() < 60000) {', '      if (items.size() < 60000 || a) {')
t = sub_once(t, r'''\"A\":{},\"B\":{}}}",''', r'''\"A\":{},\"B\":{},\"sid\":{},\"cid\":{},\"nid\":{},\"oid\":{}}}",''')
t = sub_once(t, '                             a ? 1 : 0, bl ? 1 : 0);',
             '                             a ? 1 : 0, bl ? 1 : 0, F23fId(&inst), F23fIdV(inst.Arg(0)), F23fIdV(inst.Arg(1)),\n'
             '                             F23fIdV(inst.Arg(2)));')
t = sub_once(t, '''    if (f23a_seldiag != nullptr) {
      ShaderRecompiler::Frontend::g_f23a_exec_selects = &f23a_created;
      ShaderRecompiler::Frontend::g_f23a_initial_exec = {};
    }''', '''    if (f23a_seldiag != nullptr) {
      ShaderRecompiler::Frontend::g_f23a_exec_selects = &f23a_created;
      ShaderRecompiler::Frontend::g_f23a_initial_exec = {};
      g_f23f_def_map.clear();
      ShaderRecompiler::Spirv::Emitter::g_f23f_defs = &g_f23f_def_map;
    }''')
t = sub_once(t, '''    if (f23a_seldiag != nullptr) {
      ShaderRecompiler::Frontend::g_f23a_exec_selects = nullptr;''', '''    if (f23a_seldiag != nullptr) {
      ShaderRecompiler::Spirv::Emitter::g_f23f_defs = nullptr;
      ShaderRecompiler::Frontend::g_f23a_exec_selects = nullptr;''')
save(rel, t, c)
print('patched', rel)
print('ALL OK')
