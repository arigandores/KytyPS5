# F23a (HPP-578, ROADMAP s122 item 483(e)): WORKTREE-ONLY diagnostic patch for the offline census of B7/B8.
# Applied to C:/kyty/f287/f23a/wt (main dd7c6b33, src = c31f91b6). Never committed to main; main src/ is not changed.
#  (1) Translate.cpp: when Frontend::g_f23a_exec_selects != nullptr, every "exec ? new : old" VGPR-write select created
#      by WriteRawU32 (non-DPP branch) is recorded and marked with flags F23A_MARK; the initial EXEC value is recorded.
#      With the pointer null (default, and in every non-diagnostic run) the code path is the main one.
#  (2) Control.cpp: KYTY_F23A_NOWQMFOLD set => the S_WQM fold of the pixel initial EXEC is skipped (positive control
#      of the B8 detector on the reference PS 0xe197e307a5f2cb39 only).
#  (3) tests/shaderCfgTests.cpp: KYTY_F23A_DECODE (real decoder over a list of raw code files) and
#      KYTY_F23A_SELDIAG (census of surviving exec selects after TranslateProgram inside KYTY_RECOMPILE).
# Anchors are whole lines; CR is stripped before matching and restored; output is LF when the input was LF.
import sys

WT = 'C:/kyty/f287/f23a/wt/'


def patch(rel, edits):
    path = WT + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    lines = text.split('\n')
    for anchor, mode, new in edits:
        idx = [i for i, l in enumerate(lines) if l == anchor]
        if len(idx) != 1:
            print('ANCHOR FAIL', rel, repr(anchor), len(idx))
            sys.exit(1)
        i = idx[0]
        block = new.split('\n')
        if mode == 'after':
            lines[i + 1:i + 1] = block
        elif mode == 'before':
            lines[i:i] = block
        elif mode == 'replace':
            lines[i:i + 1] = block
    out = '\n'.join(lines)
    if crlf:
        out = out.replace('\n', '\r\n')
    open(path, 'wb').write(out.encode('utf-8'))
    print('patched', rel, 'edits', len(edits), 'crlf', crlf)


TR_GLOBALS = r'''
// F23a (HPP-578) worktree-only diagnostic (not in main): census of "exec ? new : old" VGPR-write selects.
std::vector<const IR::Inst*>* g_f23a_exec_selects = nullptr;
IR::Value                     g_f23a_initial_exec;
constexpr uint64_t            F23A_MARK = 0xF23A0000F23A0001ull;'''

TR_SELECT = r'''				value = ir.Select(ir.GetExec(), value, old);
				if (g_f23a_exec_selects != nullptr) {
					if (auto* f23a_inst = IR::Value(value).TryInstruction(); f23a_inst != nullptr &&
					    (f23a_inst->GetOpcode() == IR::ValueOpcode::SelectU32 ||
					     f23a_inst->GetOpcode() == IR::ValueOpcode::SelectF32)) {
						f23a_inst->SetFlags<uint64_t>(F23A_MARK);
						g_f23a_exec_selects->push_back(f23a_inst);
					}
				}'''

TR_INIT = r'''		entry_ir.SetExec(initial_exec);
		g_f23a_initial_exec = IR::Value(initial_exec);'''

CT_FOLD = r'''	if (std::getenv("KYTY_F23A_NOWQMFOLD") == nullptr &&
	    (wide || program.wave_size == 32u) && program.stage == ShaderType::Pixel &&'''

TS_DECL = r'''
// F23a (HPP-578) worktree-only diagnostic (not in main).
namespace Libs::Graphics::ShaderRecompiler::Frontend {
extern std::vector<const IR::Inst*>* g_f23a_exec_selects;
extern IR::Value                     g_f23a_initial_exec;
} // namespace Libs::Graphics::ShaderRecompiler::Frontend

namespace {

constexpr uint64_t F23A_MARK_T = 0xF23A0000F23A0001ull;

// KYTY_F23A_DECODE="<list>;<out>[;<start>]": real Decoder::DecodeProgram over raw code files (one path per line).
// Per file: "P <i> <path> words=<n>", the UNSUPPORTED instructions "U <InstructionToString>", the VALU histogram
// "H <family>:<opcode_id hex>:<count> ...", then "E <i> inst=<n>". An EXIT inside the decoder ends the process after
// the "P" line; the driver resumes at <i>+1.
int F23aDecodeMain(const char* spec) {
  using namespace Libs::Graphics::ShaderRecompiler;
  std::string s = spec;
  std::vector<std::string> parts;
  size_t pos = 0;
  while (pos <= s.size()) {
    const auto next = s.find(';', pos);
    parts.push_back(s.substr(pos, next == std::string::npos ? std::string::npos : next - pos));
    pos = next == std::string::npos ? s.size() + 1 : next + 1;
  }
  if (parts.size() < 2) {
    std::fprintf(stderr, "KYTY_F23A_DECODE=<list>;<out>[;<start>]\n");
    return 1;
  }
  const size_t start = parts.size() > 2 ? static_cast<size_t>(std::atoll(parts[2].c_str())) : 0u;
  std::vector<std::string> paths;
  {
    FILE* lf = std::fopen(parts[0].c_str(), "rb");
    if (lf == nullptr) { return 1; }
    std::string line;
    int c = 0;
    while ((c = std::fgetc(lf)) != EOF) {
      if (c == '\n') { if (!line.empty()) { paths.push_back(line); } line.clear(); }
      else if (c != '\r') { line.push_back(static_cast<char>(c)); }
    }
    if (!line.empty()) { paths.push_back(line); }
    std::fclose(lf);
  }
  FILE* out = std::fopen(parts[1].c_str(), "ab");
  if (out == nullptr) { return 1; }
  for (size_t i = start; i < paths.size(); i++) {
    std::vector<uint32_t> code;
    {
      FILE* f = std::fopen(paths[i].c_str(), "rb");
      if (f == nullptr) { std::fprintf(out, "X %zu %s open\n", i, paths[i].c_str()); continue; }
      uint32_t word = 0;
      while (std::fread(&word, sizeof(word), 1, f) == 1) { code.push_back(word); }
      std::fclose(f);
    }
    std::fprintf(out, "P %zu %s words=%zu\n", i, paths[i].c_str(), code.size());
    std::fflush(out);
    Decoder::Program program;
    Decoder::DecodeProgram(std::span<const uint32_t>{code}, program);
    std::map<std::pair<std::string, uint32_t>, uint32_t> hist;
    for (const auto& inst : program.instructions) {
      if (inst.opcode == Decoder::Opcode::UNSUPPORTED) {
        std::fprintf(out, "U %s\n", Decoder::InstructionToString(inst).c_str());
      }
      switch (inst.family) {
        case Decoder::Family::VOP1:
        case Decoder::Family::VOP2:
        case Decoder::Family::VOP3:
        case Decoder::Family::VOPC:
        case Decoder::Family::VOP3P:
        case Decoder::Family::VINTRP:
          hist[{std::string(magic_enum::enum_name(inst.family)), inst.opcode_id}]++;
          break;
        default: break;
      }
    }
    std::fprintf(out, "H");
    for (const auto& [k, v] : hist) { std::fprintf(out, " %s:%x:%u", k.first.c_str(), k.second, v); }
    std::fprintf(out, "\nE %zu inst=%zu\n", i, program.instructions.size());
    std::fflush(out);
  }
  std::fclose(out);
  return 0;
}

bool F23aIsSelect(Libs::Graphics::ShaderRecompiler::IR::ValueOpcode op) {
  using Libs::Graphics::ShaderRecompiler::IR::ValueOpcode;
  return op == ValueOpcode::SelectU32 || op == ValueOpcode::SelectF32 || op == ValueOpcode::SelectU1;
}

bool F23aIsImageResult(Libs::Graphics::ShaderRecompiler::IR::ValueOpcode op) {
  using Libs::Graphics::ShaderRecompiler::IR::ValueOpcode;
  return op == ValueOpcode::ImageSampleRaw || op == ValueOpcode::ImageGatherRaw || op == ValueOpcode::ImageRead;
}

bool F23aIsImageOp(Libs::Graphics::ShaderRecompiler::IR::ValueOpcode op) {
  const auto name = Libs::Graphics::ShaderRecompiler::IR::ValueOpcodeName(op);
  return name.rfind("Image", 0) == 0 && op != Libs::Graphics::ShaderRecompiler::IR::ValueOpcode::GetImageResource;
}

bool F23aIsPassThrough(Libs::Graphics::ShaderRecompiler::IR::ValueOpcode op) {
  const auto name = Libs::Graphics::ShaderRecompiler::IR::ValueOpcodeName(op);
  return name == "Identity" || name.rfind("BitCast", 0) == 0 || name.rfind("CompositeExtract", 0) == 0;
}

// The image result instruction that `v` is (through Identity / BitCast / CompositeExtract), or nullptr.
const Libs::Graphics::ShaderRecompiler::IR::Inst* F23aImageSource(Libs::Graphics::ShaderRecompiler::IR::Value v) {
  for (int depth = 0; depth < 8; depth++) {
    v = v.Resolve();
    auto* inst = v.IsImmediate() ? nullptr : v.TryInstruction();
    if (inst == nullptr) { return nullptr; }
    if (F23aIsImageResult(inst->GetOpcode())) { return inst; }
    if (!F23aIsPassThrough(inst->GetOpcode()) || inst->NumArgs() == 0) { return nullptr; }
    v = inst->Arg(0);
  }
  return nullptr;
}

// Image instructions that use `inst` as an operand (directly or through BitCast / Identity / CompositeConstruct /
// MakeImageAddress / Convert), depth <= 4.
void F23aImageUsers(const Libs::Graphics::ShaderRecompiler::IR::Inst* inst, int depth,
                    std::vector<const Libs::Graphics::ShaderRecompiler::IR::Inst*>& out) {
  if (inst == nullptr || depth > 4) { return; }
  for (const auto& use : inst->Uses()) {
    const auto op = use.user->GetOpcode();
    const auto name = Libs::Graphics::ShaderRecompiler::IR::ValueOpcodeName(op);
    if (F23aIsImageOp(op)) {
      out.push_back(use.user);
    } else if (name == "Identity" || name.rfind("BitCast", 0) == 0 || name.rfind("CompositeConstruct", 0) == 0 ||
               name == "MakeImageAddress" || name.rfind("Convert", 0) == 0) {
      F23aImageUsers(use.user, depth + 1, out);
    }
  }
}

// KYTY_F23A_SELDIAG=<out>: one JSON line per translated program - surviving marked exec selects with level (top =
// condition is the initial EXEC), control nesting depth of the IR block (number of blocks h with >= 2 successors such
// that h dominates the block and the block does not post-dominate h) and the driver form (A: new is an image result
// I2, old is an operand of an image instruction I1 placed before I2; B: A and old has a use placed after the select).
void F23aSelDiag(const char* out_path, const Libs::Graphics::ShaderRecompiler::IR::Program& program,
                 const std::vector<const Libs::Graphics::ShaderRecompiler::IR::Inst*>& created, uint64_t hash,
                 uint32_t stage, size_t permutation, const char* gcn_path) {
  using namespace Libs::Graphics::ShaderRecompiler;
  std::unordered_set<const IR::Inst*> marked(created.begin(), created.end());
  const auto& blocks = program.blocks;
  const size_t nb = blocks.size();
  std::unordered_map<const IR::Block*, size_t> bidx;
  for (size_t i = 0; i < nb; i++) { bidx[blocks[i]] = i; }
  std::unordered_map<const IR::Inst*, std::pair<size_t, size_t>> pos;
  for (size_t b = 0; b < nb; b++) {
    size_t k = 0;
    for (const auto& inst : blocks[b]->Instructions()) { pos[&inst] = {b, k++}; }
  }
  // dominators (entry = block 0) and post-dominators (virtual exit after blocks without successors)
  std::vector<std::vector<size_t>> succ(nb), pred(nb);
  for (size_t b = 0; b < nb; b++) {
    for (auto* s : blocks[b]->ImmSuccessors()) {
      const auto it = bidx.find(s);
      if (it != bidx.end()) { succ[b].push_back(it->second); pred[it->second].push_back(b); }
    }
  }
  const size_t words = (nb + 64) / 64;
  auto full = [&]() { return std::vector<uint64_t>(words, ~0ull); };
  std::vector<std::vector<uint64_t>> dom(nb, full()), pdom(nb + 1, std::vector<uint64_t>(words, ~0ull));
  auto setonly = [&](std::vector<uint64_t>& v, size_t i) { std::fill(v.begin(), v.end(), 0ull); v[i / 64] |= 1ull << (i % 64); };
  if (nb > 0) { setonly(dom[0], 0); }
  for (bool changed = true; changed;) {
    changed = false;
    for (size_t b = 1; b < nb; b++) {
      std::vector<uint64_t> nv(words, pred[b].empty() ? 0ull : ~0ull);
      for (auto p : pred[b]) { for (size_t w = 0; w < words; w++) { nv[w] &= dom[p][w]; } }
      nv[b / 64] |= 1ull << (b % 64);
      if (nv != dom[b]) { dom[b] = nv; changed = true; }
    }
  }
  const size_t ex = nb;
  setonly(pdom[ex], ex);
  for (bool changed = true; changed;) {
    changed = false;
    for (size_t bb = nb; bb-- > 0;) {
      std::vector<uint64_t> nv(words, ~0ull);
      if (succ[bb].empty()) { nv = pdom[ex]; }
      for (auto s : succ[bb]) { for (size_t w = 0; w < words; w++) { nv[w] &= pdom[s][w]; } }
      nv[bb / 64] |= 1ull << (bb % 64);
      if (nv != pdom[bb]) { pdom[bb] = nv; changed = true; }
    }
  }
  auto has = [](const std::vector<uint64_t>& v, size_t i) { return ((v[i / 64] >> (i % 64)) & 1ull) != 0; };
  std::vector<int> depth(nb, 0);
  for (size_t b = 0; b < nb; b++) {
    for (size_t h = 0; h < nb; h++) {
      if (h != b && succ[h].size() >= 2 && has(dom[b], h) && !has(pdom[h], b)) { depth[b]++; }
    }
  }
  const IR::Value init = g_f23a_initial_exec_copy();
  std::string items;
  size_t survive = 0, top = 0, nested = 0, form_a = 0, form_b = 0, any_alive_marked = 0;
  for (size_t b = 0; b < nb; b++) {
    for (const auto& inst : blocks[b]->Instructions()) {
      if (!marked.contains(&inst) || inst.Flags<uint64_t>() != F23A_MARK_T) { continue; }
      if (!F23aIsSelect(inst.GetOpcode())) { continue; }
      any_alive_marked++;
      if (!inst.HasUses()) { continue; }
      const auto cond = inst.Arg(0).Resolve();
      if (cond.IsImmediate()) { continue; }
      survive++;
      const bool is_top = !init.IsEmpty() && cond == init.Resolve();
      (is_top ? top : nested)++;
      const auto* i2 = F23aImageSource(inst.Arg(1));
      bool a = false, bl = false;
      const auto oldv = inst.Arg(2).Resolve();
      const auto* old_inst = oldv.IsImmediate() ? nullptr : oldv.TryInstruction();
      if (i2 != nullptr && old_inst != nullptr && pos.contains(i2)) {
        std::vector<const IR::Inst*> users;
        F23aImageUsers(old_inst, 0, users);
        for (const auto* i1 : users) {
          if (i1 != i2 && pos.contains(i1) && pos[i1] < pos[i2]) { a = true; }
        }
        if (a) {
          for (const auto& use : old_inst->Uses()) {
            if (use.user != &inst && pos.contains(use.user) && pos[use.user] > pos[&inst]) { bl = true; }
          }
        }
      }
      form_a += a ? 1 : 0;
      form_b += bl ? 1 : 0;
      if (items.size() < 60000) {
        items += fmt::format("{}{{\"b\":{},\"i\":{},\"lvl\":\"{}\",\"depth\":{},\"new\":\"{}\",\"old\":\"{}\",\"A\":{},\"B\":{}}}",
                             items.empty() ? "" : ",", b, pos[&inst].second, is_top ? "top" : "nested", depth[b],
                             i2 != nullptr ? std::string(IR::ValueOpcodeName(i2->GetOpcode())) : std::string("-"),
                             old_inst != nullptr ? std::string(IR::ValueOpcodeName(old_inst->GetOpcode())) : std::string("imm"),
                             a ? 1 : 0, bl ? 1 : 0);
      }
    }
  }
  int maxdepth = 0;
  for (size_t b = 0; b < nb; b++) { maxdepth = std::max(maxdepth, depth[b]); }
  FILE* out = std::fopen(out_path, "ab");
  if (out == nullptr) { return; }
  std::fprintf(out,
               "{\"gcn\":\"%s\",\"hash\":\"%016llx\",\"stage\":%u,\"perm\":%zu,\"created\":%zu,\"alive_marked\":%zu,"
               "\"survive\":%zu,\"top\":%zu,\"nested\":%zu,\"formA\":%zu,\"formB\":%zu,\"blocks\":%zu,\"maxdepth\":%d,"
               "\"items\":[%s]}\n",
               gcn_path, static_cast<unsigned long long>(hash), stage, permutation, created.size(), any_alive_marked,
               survive, top, nested, form_a, form_b, nb, maxdepth, items.c_str());
  std::fclose(out);
}

} // namespace
'''

TS_MAIN = r'''  EnsureConfigInitialized();
  if (const char *f23a_decode = std::getenv("KYTY_F23A_DECODE"); f23a_decode != nullptr) {
    return F23aDecodeMain(f23a_decode);
  }'''

TS_CALL = r'''    const char *f23a_seldiag = std::getenv("KYTY_F23A_SELDIAG");
    std::vector<const ShaderRecompiler::IR::Inst *> f23a_created;
    if (f23a_seldiag != nullptr) {
      ShaderRecompiler::Frontend::g_f23a_exec_selects = &f23a_created;
      ShaderRecompiler::Frontend::g_f23a_initial_exec = {};
    }
    auto translated = ShaderRecompiler::TranslateProgram(std::span<const uint32_t>{code}, options);
    if (f23a_seldiag != nullptr) {
      ShaderRecompiler::Frontend::g_f23a_exec_selects = nullptr;
      F23aSelDiag(f23a_seldiag, translated.program, f23a_created, key.hash, key.stage, permutation, parts[0].c_str());
    }'''

patch('src/graphics/shader/recompiler/frontend/translate/Translate.cpp', [
    ('namespace Libs::Graphics::ShaderRecompiler::Frontend {', 'after', TR_GLOBALS),
    ('				value = ir.Select(ir.GetExec(), value, old);', 'replace', TR_SELECT),
    ('		entry_ir.SetExec(initial_exec);', 'replace', TR_INIT),
])
patch('src/graphics/shader/recompiler/frontend/translate/Control.cpp', [
    ('#include "common/assert.h"', 'after', '#include <cstdlib>'),
    ('	if ((wide || program.wave_size == 32u) && program.stage == ShaderType::Pixel &&', 'replace', CT_FOLD),
])
# The tests file: the declarations and helpers go before "int main() {" (after the last namespace close), the
# initial-exec accessor (needs the extern declaration) right after them.
patch('tests/shaderCfgTests.cpp', [
    ('int main() {', 'before', TS_DECL.replace('const IR::Value init = g_f23a_initial_exec_copy();',
                                             'const IR::Value init = Frontend::g_f23a_initial_exec;') + '\n'),
])
# EnsureConfigInitialized appears twice (13307 inside another function, 15138 in main): the one of main is found
# by index (first after "int main() {", at most 4 lines below it).
path = WT + 'tests/shaderCfgTests.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
lines = text.split('\n')
mi = [i for i, l in enumerate(lines) if l == 'int main() {']
assert len(mi) == 1
ec = [i for i, l in enumerate(lines) if l == '  EnsureConfigInitialized();' and i > mi[0]]
assert len(ec) == 1 and ec[0] - mi[0] <= 4, (ec, mi)
lines[ec[0]:ec[0] + 1] = TS_MAIN.split('\n')
tc = [i for i, l in enumerate(lines) if l == '    auto translated = ShaderRecompiler::TranslateProgram(std::span<const uint32_t>{code}, options);']
assert len(tc) == 1
lines[tc[0]:tc[0] + 1] = TS_CALL.split('\n')
out = '\n'.join(lines)
if crlf:
    out = out.replace('\n', '\r\n')
open(path, 'wb').write(out.encode('utf-8'))
print('patched tests main/call; crlf', crlf)
for need in ('#include <unordered_set>', '#include <map>', '#include <unordered_map>'):
    print(need, need in text)
