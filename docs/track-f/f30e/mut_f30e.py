# F30e (HPP-710, Red Team): the mutants of ROADMAP s122 item 643(v) (m1, m2, m3) against the static members C1-C8 of
# docs/track-f/f30d/code_f30d.py - each mutant is applied to the text of 585d997d and the members run on it.
# Usage: python mut_f30e.py <path to code_f30d.py>.  Expected: base PASS, every mutant FAILED by >= 1 member.
import subprocess, sys
CODE = open(sys.argv[1], encoding='utf-8').read().split('# Report links')[0]
G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
def real(c, p):
    return subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True, check=True).stdout.decode('utf-8')
MUT = {
 'base': [],
 'm1_pb2': [('\t\tif (!gate) {\n\t\t\treturn C::RtsXbLive;\n\t\t}\n', '\t\tif (!gate && t_rts != 4) {\n\t\t\treturn C::RtsXbLive;\n\t\t}\n')],
 'm1_pb5': [('\t\t\tif (img[i]->binding.is_bound != rec->t[i].is_bound) {', '\t\t\tif (t_rts != 4 && img[i]->binding.is_bound != rec->t[i].is_bound) {')],
 'm2_b': [('\tif (t_rts == 1 && pb_ok) {', '\tif ((t_rts == 1 || t_rts == 4) && pb_ok) {')],
 'm2_a': [('\tif (t_rts == 1 && t_rts_pa) {', '\tif ((t_rts == 1 || t_rts == 4) && t_rts_pa) {')],
 'm3': [('\tif ((bits & 0x030u) != 0) {', '\tif ((bits & 0x3f0u) != 0) {')],
}
res = {}
for name, edits in MUT.items():
    src = real('585d997d', RD)
    for a, b in edits:
        assert src.count(a) == 1, (name, a)
        src = src.replace(a, b)
    def show(c, p, src=src):
        if c == 'M' and p == RD:
            return src.split('\n')
        return real('585d997d' if c == 'M' else '585d997d~1', p).split('\n')
    def git(*a):
        if a[0] == 'diff':
            return subprocess.run([G, '-C', REPO, 'diff', '--name-only', '585d997d~1', '585d997d'], capture_output=True, check=True).stdout.decode('utf-8')
        raise RuntimeError(a)
    g = {'__name__': 'm'}
    code = CODE.replace('for c in sys.argv[1:]:', "for c in ['M']:").replace('def show(c, p):', 'def _show_unused(c, p):').replace('def git(*a):', 'def _git_unused(*a):')
    g.update({'show': show, 'git': git})
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, 'code_f30d', 'exec'), g)
    fails = [l for l in buf.getvalue().split('\n') if l.startswith('FAIL')]
    res[name] = fails
    print(name, 'PASS' if not fails else 'FAILED by ' + '; '.join(f[5:40] for f in fails))
ok = not res['base'] and all(res[k] for k in res if k != 'base')
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
