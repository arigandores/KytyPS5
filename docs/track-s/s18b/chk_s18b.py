import subprocess, sys, collections
R = 'C:/kyty/KytyPS5'
PAIRS = [('283a6ef9', '2dd9f902'), ('29542308', '6c4903a8'), ('a2fee0d9', '60f6c006'),
         ('9635cb0f', 'a139a145'), ('9238a182', 'b738443b'), ('5bd93ea1', '4fbea82e'),
         ('fe4b227a', '62ff7b5b')]
BASE, HEAD = '302347b4', '62ff7b5b'
CODE = ('src/', 'tests/', 'CMakeLists.txt')

def git(*a, inp=None):
    return subprocess.run(['git', '-C', R] + list(a), input=inp, capture_output=True, check=True).stdout

def pid(diff):
    out = git('patch-id', '--stable', inp=diff).decode().split()
    return out[0] if out else '-'

def files(c):
    return [l for l in git('diff-tree', '--no-commit-id', '--name-only', '-r', c).decode().split('\n') if l]

def pm(c, f):
    d = git('show', '--format=', c, '--', f).decode('utf-8', 'replace').split('\n')
    p = collections.Counter(l for l in d if l.startswith('+') and not l.startswith('+++'))
    m = collections.Counter(l for l in d if l.startswith('-') and not l.startswith('---'))
    return p, m

ok = True
print('pair\tsrc\tpick\twhole_pid\tcode_pid\tfiles_eq\tpm_eq_all\tsrc_vs_pick')
for src, pk in PAIRS:
    fs, fp = files(src), files(pk)
    w = pid(git('show', src)) == pid(git('show', pk))
    cs = [f for f in fs if f.startswith(CODE)]
    cp = [f for f in fp if f.startswith(CODE)]
    c = cs == cp and pid(git('show', src, '--', *cs)) == pid(git('show', pk, '--', *cp)) if cs else True
    pmeq = all(pm(src, f) == pm(pk, f) for f in cs)
    # tree difference source commit vs pick commit on code files touched
    st = git('diff', '--numstat', src, pk, '--', *cs).decode().strip().replace('\n', '; ') if cs else ''
    print(f'{src}->{pk}\t{w}\t{c}\t{cs == cp}\t{pmeq}\t[{st}]')
    ok &= c and pmeq and cs == cp
# whole range: paths changed by base..head must be subset of paths touched by sources
rng = set(l for l in git('diff', '--name-only', BASE, HEAD).decode().split('\n') if l)
srcf = set()
for s, _ in PAIRS:
    srcf |= set(files(s))
extra = rng - srcf
print('range paths', len(rng), 'not in sources', sorted(extra))
ok &= not extra
# diff base..head vs concatenation: numstat head vs main fe4b227a on range code paths
cp = sorted(f for f in rng if f.startswith(CODE))
print('code paths in range:', cp)
print('numstat fe4b227a..HEAD on range code paths:')
print(git('diff', '--numstat', 'fe4b227a', HEAD, '--', *cp).decode())
print('removed-vs-main lines:')
for l in git('diff', '-U0', 'fe4b227a', HEAD, '--', *cp).decode('utf-8', 'replace').split('\n'):
    if l.startswith(('+', '-', '@@')) and not l.startswith(('+++', '---')):
        print('  ', l[:160])
# K1(7) signature list: files in CMake signature list changed in range?
print('ALL OK' if ok else 'FAIL')
