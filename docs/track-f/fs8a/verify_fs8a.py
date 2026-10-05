"""FS8a (HPP-571, ROADMAP s122 items 471(g)(1)(a), (e), (zh), 523(g)): members of the FS8 worktree by git and files.

(a)  H1 of item 469(v): every file of SHADER_CACHE_EXTRA_FILES (CMakeLists.txt of the worktree, ${KYTY_SOURCE_DIR} =
     <wt>/src by `set(KYTY_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")`) exists in the worktree.
(e') item 523(g): (1) git diff --name-only BASE HEAD - the paths; docs/ paths 0; (2) sha256 of
     `git diff BASE HEAD -- src CMakeLists.txt` and of `git diff BASE 5e78640e -- src CMakeLists.txt`, equal;
     (3) HEAD^{tree} vs 5e78640e and `git diff --name-only 5e78640e HEAD`.
(zh') item 380(b) with 487(g)(6) and 523(g): "contains" = ancestor of HEAD or `git cherry HEAD <c> <c>^` gives '-'.
     tests/shaderCfgTests.cpp contains every added line of ff953d4f (multiset of '+' lines of its diff of that file).
Usage: python verify_fs8a.py
"""
import collections
import hashlib
import os
import re
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/f287/fs8a/wt'
BASE = 'd6ee2dc8'
TREE_1B = '5e78640e'


def git(*a, check=True):
    p = subprocess.run([G, '-C', WT, *a], capture_output=True)
    if check and p.returncode != 0:
        raise SystemExit('git %s: %s' % (' '.join(a), p.stderr.decode()))
    return p.stdout.decode('utf-8', 'replace'), p.returncode


ok = True
print('HEAD', git('rev-parse', 'HEAD')[0].strip(), 'base', git('rev-parse', BASE)[0].strip())

# (a)
cm = open(WT + '/CMakeLists.txt', encoding='utf-8').read()
m = re.search(r'-D SHADER_CACHE_EXTRA_FILES=(\S+)', cm)
files = m.group(1).split('$<SEMICOLON>')
print('(a) SHADER_CACHE_EXTRA_FILES: %d files' % len(files))
for f in files:
    p = f.replace('${KYTY_SOURCE_DIR}', WT + '/src')
    ex = os.path.isfile(p)
    print('    %s exists=%s' % (f, ex))
    ok &= ex
# (e')(1)
names = git('diff', '--name-only', BASE, 'HEAD')[0].split()
docs = [n for n in names if n.startswith('docs/')]
print("(e')(1) paths %d, docs %d:" % (len(names), len(docs)))
for n in names:
    print('    ' + n)
want = {'CMakeLists.txt', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
        'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp',
        'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.h',
        'tests/ShaderRecompilerComputeTests.cpp', 'tests/shaderCfgTests.cpp'}
good = set(names) == want and not docs
print("(e')(1) = the 6 paths of item 523(g), docs 0: %s" % good)
ok &= good
# (e')(2)
d_head = git('diff', BASE, 'HEAD', '--', 'src', 'CMakeLists.txt')[0].encode('utf-8')
d_1b = git('diff', BASE, TREE_1B, '--', 'src', 'CMakeLists.txt')[0].encode('utf-8')
h1, h2 = hashlib.sha256(d_head).hexdigest(), hashlib.sha256(d_1b).hexdigest()
print("(e')(2) sha256 diff BASE..HEAD src+CMakeLists %s; BASE..%s %s; equal %s" % (h1, TREE_1B, h2, h1 == h2))
ok &= h1 == h2
# (e')(3)
t = git('rev-parse', 'HEAD^{tree}')[0].strip()
t1b = git('rev-parse', TREE_1B)[0].strip()
dn = git('diff', '--name-only', TREE_1B, 'HEAD')[0].split()
print("(e')(3) HEAD^{tree} %s vs %s: equal %s; differing paths %d:" % (t, t1b, t == t1b, len(dn)))
for n in dn:
    print('    ' + n)
outside = [n for n in dn if not (n == 'docs/track-s/s14j.md' or n.startswith('docs/track-s/s14j/'))]
print("(e')(3) paths outside docs/track-s/s14j(.md|/): %s" % outside)
# not a gate here: the FS8a test commit 7719d0f2 adds tests/shaderCfgTests.cpp to this list (report, question)
# (zh')
contains = ['082d1612', 'f98e842c', 'e46f55d4', '10a4800b', 'ec6c4c83', '9c726d74', '919c1a19', 'fcaf141b', '7719d0f2']
for c in contains:
    _, rc = git('merge-base', '--is-ancestor', c, 'HEAD', check=False)
    ch = git('cherry', 'HEAD', c, c + '^')[0].strip()
    good = rc == 0 or ch.startswith('-')
    print("(zh') %s ancestor=%s cherry='%s' contains=%s" % (c, rc == 0, ch[:12], good))
    ok &= good
ch = git('cherry', 'HEAD', 'ff953d4f', 'ff953d4f^')[0].strip()
print("(zh') ff953d4f as a whole: cherry='%s' (expected '+': not contained as a commit)" % ch[:12])
plus = collections.Counter()
for line in git('show', '--format=', 'ff953d4f', '--', 'tests/shaderCfgTests.cpp')[0].split('\n'):
    if line.startswith('+') and not line.startswith('+++'):
        plus[line[1:]] += 1
have = collections.Counter(open(WT + '/tests/shaderCfgTests.cpp', encoding='utf-8').read().replace('\r\n', '\n').split('\n'))
missing = [l for l, n in plus.items() if have[l] < n]
print("(zh') tests/shaderCfgTests.cpp contains the added lines of ff953d4f: %d distinct lines, missing %d %s"
      % (len(plus), len(missing), missing[:3]))
ok &= not missing
st = git('status', '--short', '--ignore-submodules=all')[0].strip()
print('worktree status lines: %d' % (len(st.split('\n')) if st else 0))
ok &= not st
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
