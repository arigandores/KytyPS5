"""F42b (HPP-780, Red Team; ROADMAP s122 item 694(g)(5)): mutants m1-m6 of KYTY_FIX_F20 on the own worktree
C:/kyty/f287/f42b/wt (detached 26283087 = F42a tag tree). Anchors are WHOLE lines (exact match, must occur once) of the
pristine file (git show HEAD:<path>); files are LF (checked: CR 0 in src/); written with write_bytes and ONLY when the
content differs (mtimes of unchanged files kept - a killed build resumes without recompiling). 'revert' = pristine
content written back where it differs.
  m1a  RewriteFaultOr builds the output without replacing anything (stats still say rewritten)      -> stand W/X =1, corpus
  m1b  call sites create the module from the translation even when Apply rewrote (CreateCachedModule and dual-source)
  m2   only the first triple of a module is replaced (stats still count all as rewritten)           -> corpus (4)
  m3   OpAtomicOr with Scope = the module's u32 constant 2 (ScopeWorkgroup) when it exists          -> code review (letter)
  m4   OpAtomicXor (242) instead of OpAtomicOr (241)                                               -> stand X =1
  m5   identification by the name only: the bound flag is not read, no unmatched for a bound module without the name
                                                                                                    -> stand N =1
  m6   Apply is called at KYTY_FIX_F20=0 (both call sites)                                          -> member (2)
Usage: python mut_f42b.py <name> | revert"""
import subprocess
import sys

WT = 'C:/kyty/f287/f42b/wt'
H = 'src/graphics/host_gpu/renderer/pipeline/fixF20.h'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
SH = 'src/graphics/host_gpu/renderer/pipeline/shaders.cpp'
GIT = 'C:/Program Files/Git/cmd/git.exe'

M = {
    'm1a': [(H, ['\t\tif (rewrite[k] != 0) {'],
             ['\t\tif (false && rewrite[k] != 0) { // MUTANT m1a: nothing replaced'])],
    'm1b': [(PC, ['\tconst auto&           source  = fix_f20 ? fixed : translation;'],
             ['\tconst auto&           source  = ((void)fix_f20, translation); // MUTANT m1b']),
            (SH, ['\tconst auto            module  = CompileSPV(fix_f20 ? fixed : words, graphics.device);'],
             ['\tconst auto            module  = CompileSPV(((void)fix_f20, words), graphics.device); // MUTANT m1b'])],
    'm2': [(H, ['\t\t\trewrite[site.k] = 1;'],
            ['\t\t\trewrite[site.k] = stats.rewritten == 0 ? 1 : 0; // MUTANT m2: only the first triple'])],
    'm3': [(H, ['\tstats.named = static_cast<uint32_t>(fault_vars.size());'],
            ['\tuint32_t const_two = 0; // MUTANT m3: ScopeWorkgroup = u32 constant 2 of the module',
             '\tfor (const auto& x: ins) {',
             '\t\tif (x.op == kOpConstant && x.count == 4 && u32_types.contains(in[x.at + 1]) && in[x.at + 3] == 2u &&',
             '\t\t    const_two == 0) {',
             '\t\t\tconst_two = in[x.at + 2];',
             '\t\t}',
             '\t}',
             '\tstats.named = static_cast<uint32_t>(fault_vars.size());']),
           (H, ['\t\t\tout.push_back(const_one);'],
            ['\t\t\tout.push_back(const_two != 0 ? const_two : const_one); // MUTANT m3'])],
    'm4': [(H, ['\tconstexpr uint32_t kOpAtomicOr          = 241u; // OpAtomicOr (242 is OpAtomicXor)'],
            ['\tconstexpr uint32_t kOpAtomicOr          = 242u; // MUTANT m4: OpAtomicXor'])],
    'm5': [(H, ['\tif (!bound) {',
                '\t\tstats.unmatched = stats.named != 0 ? 1u : 0u;',
                '\t\treturn stats;',
                '\t}',
                '\tif (fault_vars.empty()) {',
                '\t\tstats.unmatched = 1;',
                '\t\treturn stats;',
                '\t}'],
            ['\t(void)bound; // MUTANT m5: identification by the name only',
             '\tif (fault_vars.empty()) {',
             '\t\treturn stats;',
             '\t}'])],
    'm6': [(PC, ['\tconst bool            fix_f20 = FixF20::Mode() == 1 && FixF20::Apply(translation, fault_bound, fixed);'],
            ['\tconst bool            fix_f20 = FixF20::Apply(translation, fault_bound, fixed); // MUTANT m6']),
           (SH, ['\tconst bool            fix_f20 = FixF20::Mode() == 1 && FixF20::Apply(words, pixel_program.fault_bound, fixed);'],
            ['\tconst bool            fix_f20 = FixF20::Apply(words, pixel_program.fault_bound, fixed); // MUTANT m6'])],
}


def pristine(path):
    return subprocess.run([GIT, '-C', WT, 'show', 'HEAD:' + path], capture_output=True, check=True).stdout


def write_if_differs(path, data):
    p = WT + '/' + path
    if open(p, 'rb').read() != data:
        open(p, 'wb').write(data)
        return True
    return False


def target_contents(name):
    want = {f: pristine(f) for f in (H, PC, SH)}
    if name == 'revert':
        return want
    for path, old, new in M[name]:
        lines = want[path].decode('utf-8').split('\n')
        hits = [i for i in range(len(lines) - len(old) + 1) if lines[i:i + len(old)] == old]
        if len(hits) != 1:
            raise SystemExit('anchor %s in %s: %d hits' % (old[0][:60], path, len(hits)))
        lines[hits[0]:hits[0] + len(old)] = new
        want[path] = '\n'.join(lines).encode('utf-8')
        print('mutant', name, path, 'line', hits[0] + 1)
    return want


name = sys.argv[1]
for path, data in target_contents(name).items():
    print(path, 'written' if write_if_differs(path, data) else 'unchanged')
st = subprocess.run([GIT, '-C', WT, 'status', '--short', '--ignore-submodules=all'], capture_output=True,
                    text=True).stdout
print('status lines', len(st.splitlines()))
