"""F14f (HPP-506): Red Team's own source mutants of the F14e code in the F14f worktree C:/kyty/f287/f14f/wt.
Each mutant replaces exact whole lines (LF file; CR stripped before the search and restored if present) and must match
exactly once; 'restore' puts the file back with git checkout.
  M1  =1 branch keeps the old predicate (the example of the task: '=1 without the change of the predicate')
  M2  O1 merge not called at =1
  M3  =0 branch (else) uses the new rule
  M4  ':fixf19' token never added to the translation cache variant
  M5  the =1 rule ignores a null T# (null descriptor manual at =1)
  M6  O1 merge 'and' instead of 'or' (a table is manual only if every member is)
Usage: python f14f_mut.py apply <M> | python f14f_mut.py restore
"""
import subprocess
import sys

WT = 'C:/kyty/f287/f14f/wt'
RM = 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp'
TC = 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp'
G = 'C:/Program Files/Git/cmd/git.exe'

MUT = {
    'M1': (RM, ['\t\t\t\timage.manual_depth_compare =',
                '\t\t\t\t    FixF19ManualDepthCompare(format, NullImageDescriptor(descriptor));'],
           ['\t\t\t\timage.manual_depth_compare = !NullImageDescriptor(descriptor) &&',
            '\t\t\t\t                             format != Prospero::BufferFormat::k32Float;']),
    'M2': (RM, ['\t\tFixF19MergeIndirectTables(next_specialization.images);'],
           ['\t\t(void)next_specialization;']),
    'M3': (RM, ['\t\t\t\timage.manual_depth_compare = !NullImageDescriptor(descriptor) &&',
                '\t\t\t\t                             format != Prospero::BufferFormat::k32Float;'],
           ['\t\t\t\timage.manual_depth_compare =',
            '\t\t\t\t    FixF19ManualDepthCompare(format, NullImageDescriptor(descriptor));']),
    'M4': (TC, ['\t                            (ShaderRecompiler::IR::FixF19Enabled() ? ":fixf19" : "");'],
           ['\t                            (ShaderRecompiler::IR::FixF19Enabled() ? "" : "");']),
    'M5': (RM, ['\treturn !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;'],
           ['\treturn FindGuestDepthFormatPolicy(format) == nullptr;']),
    'M6': (RM, ['\t\tbool manual = false;',
                '\t\tfor (const auto& image: images) {',
                '\t\t\tmanual = manual || (image.indirect_root == root && image.manual_depth_compare);'],
           ['\t\tbool manual = true;',
            '\t\tfor (const auto& image: images) {',
            '\t\t\tmanual = manual && (image.indirect_root != root || image.manual_depth_compare);']),
}


def main():
    if sys.argv[1] == 'restore':
        subprocess.run([G, '-C', WT, 'checkout', '--', RM, TC], check=True)
        st = subprocess.run([G, '-C', WT, 'status', '--porcelain', '--ignore-submodules=all'], capture_output=True,
                            text=True).stdout
        print('restored; status lines', len(st.splitlines()))
        return
    m = sys.argv[2]
    path, old, new = MUT[m]
    p = WT + '/' + path
    raw = open(p, 'rb').read()
    crlf = b'\r\n' in raw
    lines = raw.replace(b'\r\n', b'\n').decode('utf-8').split('\n')
    n = len(old)
    hits = [i for i in range(len(lines) - n + 1) if lines[i:i + n] == old]
    if len(hits) != 1:
        sys.exit('%s: anchor hits %d (need 1)' % (m, len(hits)))
    i = hits[0]
    if m == 'M1' and lines[i - 1].strip() != '// depth (k16UNorm joins k32Float), shader comparison for the rest.':
        sys.exit('M1: not the =1 branch')
    if m == 'M3' and lines[i - 1].strip() != '} else {':
        sys.exit('M3: not the else branch')
    lines[i:i + n] = new
    out = '\n'.join(lines).encode('utf-8')
    if crlf:
        out = out.replace(b'\n', b'\r\n')
    open(p, 'wb').write(out)
    print('%s applied at %s:%d (crlf %s)' % (m, path, i + 1, crlf))


if __name__ == '__main__':
    main()
