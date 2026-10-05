# FS8b (HPP-572, Red Team, ROADMAP s122 items 471(g)(2), 523(d), 527(d)): own git checks of the FS8 source.
# Independent of the FS8a scripts: the chain is rebuilt here in a temporary index (GIT_INDEX_FILE) from d6ee2dc8,
# the worktree is never touched. Output: review_git.out.txt (stdout).
import hashlib
import os
import subprocess
import sys
import tempfile

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
WT = 'C:/kyty/f287/fs8a/wt'
BASE = 'd6ee2dc8'
HEAD = '302347b4'
T5E = '5e78640e'
ok = True


def git(*a, cwd=REPO, env=None, inp=None, check=True):
    r = subprocess.run([G, *a], cwd=cwd, env=env, input=inp, capture_output=True)
    if check and r.returncode != 0:
        print('GIT FAIL', a, r.stderr.decode('utf-8', 'replace'))
        sys.exit(2)
    return r.stdout


def s(b):
    return b.decode('utf-8', 'replace').strip()


def say(name, cond, extra=''):
    global ok
    ok &= bool(cond)
    print('%-60s %s %s' % (name, 'OK' if cond else 'FAIL', extra))


print('== worktree')
print('HEAD', s(git('rev-parse', 'HEAD', cwd=WT)))
st = s(git('status', '--short', '--ignore-submodules=all', cwd=WT))
say('wt status --short empty', st == '', repr(st[:200]))
full_head = s(git('rev-parse', HEAD))
print('log', s(git('log', '--format=%h %s', BASE + '..' + HEAD)).replace('\n', '\n    '))

print('== (e\')(1) names d6ee2dc8..HEAD')
names = s(git('diff', '--name-only', BASE, HEAD)).splitlines()
for n in names:
    print('   ', n)
want = {'CMakeLists.txt', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
        'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp',
        'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.h',
        'tests/ShaderRecompilerComputeTests.cpp', 'tests/shaderCfgTests.cpp'}
say('(e\')(1) exactly 6 paths, docs 0', set(names) == want and len(names) == 6)

print('== commits and their files')
commits = {'fcaf141b': None, '082d1612': None, 'ff953d4f': None, 'f98e842c': None, 'e46f55d4': None, '7719d0f2': None}
for c in commits:
    fl = s(git('show', '--format=', '--name-only', c)).splitlines()
    commits[c] = fl
    print(' ', c, s(git('log', '-1', '--format=%s', c))[:90])
    for f in fl:
        print('     ', f)
src_union = set()
for c in ('082d1612', 'f98e842c', 'e46f55d4'):
    src_union |= {f for f in commits[c] if not f.startswith('tests/') and not f.startswith('docs/')}
src_names = {n for n in names if not n.startswith('tests/')}
say('src+CMake paths == union of 082d1612,f98e842c,e46f55d4 (non-test)', src_names == src_union, sorted(src_union))

print('== own chain in a temporary index from', BASE)
tmpd = tempfile.mkdtemp()
idx = os.path.join(tmpd, 'index')
env = dict(os.environ, GIT_INDEX_FILE=idx)
git('read-tree', BASE, env=env)


def apply(c, paths=None, exclude=None):
    args = ['show', '--format=', '--binary', c]
    if paths:
        args += ['--'] + paths
    patch = git(*args)
    a = ['apply', '--cached', '--3way', '--whitespace=nowarn']
    r = subprocess.run([G, *a], cwd=REPO, env=env, input=patch, capture_output=True)
    print('  apply %s %s rc=%d %s' % (c, paths or '', r.returncode, s(r.stderr)[:300].replace('\n', ' | ')))
    return r.returncode == 0


chain_ok = True
chain_ok &= apply('fcaf141b')
chain_ok &= apply('082d1612')
chain_ok &= apply('ff953d4f', ['tests/shaderCfgTests.cpp'])
chain_ok &= apply('f98e842c')
chain_ok &= apply('e46f55d4')
t_before_7719 = s(git('write-tree', env=env))
chain_ok &= apply('7719d0f2')
t_own = s(git('write-tree', env=env))
t_head = s(git('rev-parse', HEAD + '^{tree}'))
print('  own tree', t_own, 'HEAD tree', t_head, 'own tree before 7719d0f2', t_before_7719)
say('own chain applies without conflicts', chain_ok)
say('own chain tree == HEAD^{tree}', t_own == t_head)
t_0f78 = s(git('rev-parse', '0f78a522^{tree}', check=False)) if True else ''
print('  0f78a522^{tree}', t_0f78)
say('own tree before 7719d0f2 == 0f78a522^{tree}', t_before_7719 == t_0f78)

print('== (e\')(2) src+CMake diff vs 5e78640e')
d1 = git('diff', BASE, HEAD, '--', 'src', 'CMakeLists.txt')
d2 = git('diff', BASE, T5E, '--', 'src', 'CMakeLists.txt')
h1, h2 = hashlib.sha256(d1).hexdigest(), hashlib.sha256(d2).hexdigest()
print('  sha256 d6ee..HEAD', h1)
print('  sha256 d6ee..5e78', h2)
say('(e\')(2) equal', h1 == h2)
# src diff == concatenated effect of the 3 commits applied alone (no tests, no docs) on the base
git('read-tree', BASE, env=env)
only_ok = True
for c in ('082d1612', 'f98e842c', 'e46f55d4'):
    only_ok &= apply(c, ['src', 'CMakeLists.txt'])
t_src = s(git('write-tree', env=env))
d3 = git('diff', BASE, t_src, '--', 'src', 'CMakeLists.txt')
say('src+CMake of HEAD == base + src/CMake parts of 082d1612,f98e842c,e46f55d4 only', only_ok and d3 == d1,
    hashlib.sha256(d3).hexdigest()[:16])

print('== (e\')(3)\'\' names 5e78640e..HEAD and patch-id')
n3 = s(git('diff', '--name-only', T5E, HEAD)).splitlines()
non_docs = [n for n in n3 if not n.startswith('docs/track-s/s14j')]
print('  paths', len(n3), 'non s14j:', non_docs)
say('(e\')(3)\'\' only docs/track-s/s14j* and tests/shaderCfgTests.cpp', non_docs == ['tests/shaderCfgTests.cpp'])


def pid(patch):
    r = subprocess.run([G, 'patch-id', '--stable'], cwd=REPO, input=patch, capture_output=True)
    return s(r.stdout).split(' ')[0]


p_a = pid(git('diff', T5E, HEAD, '--', 'tests/shaderCfgTests.cpp'))
p_b = pid(git('show', '7719d0f2'))
print('  patch-id 5e78..HEAD tests/shaderCfgTests.cpp', p_a)
print('  patch-id 7719d0f2                         ', p_b)
say('patch-id equal', p_a == p_b and p_a != '')

print('== 523(d) added lines of tests/shaderCfgTests.cpp vs base')


def added(patch):
    out = []
    for ln in patch.decode('utf-8', 'replace').splitlines():
        if ln.startswith('+') and not ln.startswith('+++'):
            out.append(ln[1:])
    return out


def removed(patch):
    out = []
    for ln in patch.decode('utf-8', 'replace').splitlines():
        if ln.startswith('-') and not ln.startswith('---'):
            out.append(ln[1:])
    return out


tot_add = added(git('diff', BASE, HEAD, '--', 'tests/shaderCfgTests.cpp'))
tot_rem = removed(git('diff', BASE, HEAD, '--', 'tests/shaderCfgTests.cpp'))
pool = []
for c in ('fcaf141b', '082d1612', 'ff953d4f', 'f98e842c', '7719d0f2'):
    pool += added(git('show', '--format=', c, '--', 'tests/shaderCfgTests.cpp'))
pool_set = set(pool)
extra = [l for l in tot_add if l not in pool_set]
print('  added lines', len(tot_add), 'removed', len(tot_rem), 'not from the 5 commits:', len(extra))
for l in extra[:20]:
    print('    EXTRA +', l[:150])
say('added lines of tests/shaderCfgTests.cpp all from fcaf141b,082d1612,ff953d4f,f98e842c,7719d0f2', not extra)
rpool = set()
for c in ('fcaf141b', '082d1612', 'ff953d4f', 'f98e842c', '7719d0f2'):
    rpool |= set(removed(git('show', '--format=', c, '--', 'tests/shaderCfgTests.cpp')))
rextra = [l for l in tot_rem if l not in rpool]
say('removed lines all removed by one of the 5 commits', not rextra, len(rextra))
for l in rextra[:10]:
    print('    EXTRA -', l[:150])
# ShaderRecompilerComputeTests.cpp: only f98e842c / 082d1612
ta = added(git('diff', BASE, HEAD, '--', 'tests/ShaderRecompilerComputeTests.cpp'))
tp = set()
for c in ('082d1612', 'f98e842c', 'e46f55d4'):
    tp |= set(added(git('show', '--format=', c, '--', 'tests/ShaderRecompilerComputeTests.cpp')))
say('tests/ShaderRecompilerComputeTests.cpp added lines from 082d1612/f98e842c', all(l in tp for l in ta), len(ta))

print('== contains (p.380(b)): git cherry HEAD X X^')
for c in ('082d1612', 'f98e842c', 'e46f55d4', '10a4800b', 'ec6c4c83', '9c726d74', '919c1a19', 'fcaf141b', '7719d0f2',
          'a86a5ad0', '17eb924e', 'c1732d1a', 'c3eb8fe8', '1833ee28', '68602c4f', '17adaf80', '4e72289e'):
    anc = subprocess.run([G, 'merge-base', '--is-ancestor', c, HEAD], cwd=REPO).returncode == 0
    ch = s(git('cherry', HEAD, c, c + '^'))
    mark = ch[:1] if ch else ''
    print('  %s ancestor=%s cherry=%s' % (c, anc, ch[:60]))
    say('contains ' + c, anc or mark == '-')
for c in ('ff953d4f', '741e3312', 'c9b4268e', '381aa80a', '365cc3c2'):
    anc = subprocess.run([G, 'merge-base', '--is-ancestor', c, HEAD], cwd=REPO).returncode == 0
    ch = s(git('cherry', HEAD, c, c + '^', check=False))
    print('  (not expected) %s ancestor=%s cherry=%s' % (c, anc, ch[:60]))
for c in ('d6ee2dc8', '3904522d', '4d9e8ab7', '0e72bc19', '3d0e46da', '4414e235', 'd515b901'):
    anc = subprocess.run([G, 'merge-base', '--is-ancestor', c, HEAD], cwd=REPO).returncode == 0
    say('ancestor ' + c, anc)

print('ALL OK' if ok else 'FAILED')
