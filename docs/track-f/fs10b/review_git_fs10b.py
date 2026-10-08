# FS10b (HPP-685, Red Team, ROADMAP s122 item 624(e)(2)): own git checks of the FS10 source (worktree FS10a dc5d4712).
# Members, named before the run:
#  G1 chain: dc5d4712 -> 1a7eaff8 -> 64a1fa40 -> 7bc87bc8 -> a42f50b1 -> 11164d72 (FS9); T2 0c8fcba2 -> 2afd998c -> 83eae9c6 ->
#     e9520c36 -> 929b6073 ... 554eaafa -> 11164d72.
#  G2 "contains": for each main commit X of (a8ee1b05, b4ee756a, 0e4b2f5a, 5064c5bb, 7f34b1e2) the sorted changed lines (+/-)
#     of X equal those of its FS10 copy and of its T2 copy (T2 has no FS10a). Negative controls: X against another copy;
#     X against its copy with one changed line flipped.
#  G3 tree A: temp index = 11164d72 + git apply --cached of the five main diffs (full context; a file whose hunks do not
#     apply - git apply --3way, the merge of cherry-pick, printed as '3way fallback') == dc5d4712^{tree}. (First form with
#     -U0 --unidiff-zero placed the insertions of log.cpp one line off - the base has no diagB32.h include line - and
#     gave another tree; G4 keeps the -U0 form, judged by the tree equality.)
#     Negative control: without 7f34b1e2 != .
#  G4 tree B (path =1 of FS10 = path =1 of T2 minus KYTY_DIAG_B32): temp index = T2 0c8fcba2 + reverse apply of the diff
#     11164d72..929b6073 (the five KYTY_DIAG_B32 commits) + apply of 7f34b1e2 == dc5d4712^{tree}. Negative control:
#     without 7f34b1e2 != ; and without the reverse step != .
#  G5 diff FS10 vs base: names = union of the files of the five commits; base lines removed = 0 (only insertions);
#     no path under src/graphics/shader/.
#  G6 symbol: KYTY_DIAG_B32 / DiagB32 / diagB32 in dc5d4712 src/ tests/ CMakeLists.txt - only comment lines; file
#     src/common/diagB32.h absent.
#  G7 the places of the F25k / F25k2 code that touched KYTY_DIAG_B32 in T2: (a) a line of the T2 copy of a commit that
#     names DiagB32/diagB32/DIAG_B32/b32; (b) a hunk of the T2 copy whose context holds such a line; (c) the lines of the
#     T2 -> FS10 diff in the files of the four commits, grouped by hunk. Printed, not judged by the script.
#  G8 fixes untouched: Ф10 1833ee28 c3eb8fe8, Ф16 68602c4f 17adaf80, Б42 4e72289e, Б33 c1732d1a, Б4 a86a5ad0 17eb924e,
#     Ф8 10a4800b ec6c4c83, Б24 9c726d74 919c1a19, Ф19 082d1612 f98e842c e46f55d4 7719d0f2, Б13 21db93d1 11164d72,
#     P-var 4414e235, S-replay 0005e11f: ancestors of dc5d4712; files of these commits intersect the FS10 diff files -> for
#     those files FS10 removes 0 base lines (G5).
import os
import subprocess
import sys
import tempfile

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
BASE, FS10, T2, DIAG_TOP = '11164d72', 'dc5d4712', '0c8fcba2', '929b6073'
MAIN = ['a8ee1b05', 'b4ee756a', '0e4b2f5a', '5064c5bb', '7f34b1e2']
FSC = {'a8ee1b05': 'a42f50b1', 'b4ee756a': '7bc87bc8', '0e4b2f5a': '64a1fa40', '5064c5bb': '1a7eaff8', '7f34b1e2': 'dc5d4712'}
T2C = {'a8ee1b05': 'e9520c36', 'b4ee756a': '83eae9c6', '0e4b2f5a': '2afd998c', '5064c5bb': '0c8fcba2'}
ok = True


def git(*a, inp=None, env=None, check=True):
    r = subprocess.run([G, '-C', REPO, *a], input=inp, capture_output=True, env=env)
    if check and r.returncode != 0:
        raise SystemExit('git %s failed: %s' % (' '.join(a), r.stderr.decode('utf-8', 'replace')))
    return r


def out(*a):
    return git(*a).stdout.decode('utf-8', 'replace').strip()


def member(name, cond, text=''):
    global ok
    print('%s %s %s' % ('OK  ' if cond else 'FAIL', name, text))
    ok &= bool(cond)


def changed(diff_text):
    lines = []
    for ln in diff_text.split('\n'):
        if ln.startswith('+++') or ln.startswith('---'):
            continue
        if ln.startswith('+') or ln.startswith('-'):
            lines.append(ln)
    return sorted(lines)


def cdiff(c):
    return git('diff', c + '^', c).stdout.decode('utf-8', 'replace')


# G1
def chain(top, n):
    return out('log', '--format=%h', '-n', str(n), top).split()


c1 = chain(FS10, 6)
member('G1 FS10 chain', c1 == ['dc5d4712', '1a7eaff8', '64a1fa40', '7bc87bc8', 'a42f50b1', '11164d72'], ' '.join(c1))
c2 = chain(T2, 10)
member('G1 T2 chain', c2 == ['0c8fcba2', '2afd998c', '83eae9c6', 'e9520c36', '929b6073', '62fd092a', '5836f6d7', '22f645e1',
                             '653ee365', '554eaafa'] and out('rev-parse', '554eaafa^')[:8] == '11164d72', ' '.join(c2))

# G2
for x in MAIN:
    m = changed(cdiff(x))
    f = changed(cdiff(FSC[x]))
    member('G2 %s == FS10 %s' % (x, FSC[x]), m == f, '(%d lines)' % len(m))
    if x in T2C:
        t = changed(cdiff(T2C[x]))
        member('G2 %s == T2 %s' % (x, T2C[x]), m == t, '(%d lines)' % len(t))
neg = changed(cdiff('5064c5bb')) != changed(cdiff('a42f50b1'))
member('G2 negative control 5064c5bb vs a42f50b1 differs', neg)
mm = changed(cdiff('b4ee756a'))
mm2 = list(mm)
mm2[0] = ('-' if mm2[0][0] == '+' else '+') + mm2[0][1:]
member('G2 negative control flipped line differs', sorted(mm2) != changed(cdiff('7bc87bc8')))
print('git cherry %s (+ = patch-id differs):' % FS10)
for x in MAIN:
    print('   ', out('cherry', FS10, x, x + '^') or '(empty)')


# G3 / G4 in a temp index
def tree_of(start, steps, mode3=False):
    fd, idx = tempfile.mkstemp(prefix='fs10b_idx_')
    os.close(fd)
    os.remove(idx)
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    try:
        git('read-tree', start, env=env)
        for kind, a, b in steps:
            # Full context first; if it does not apply (the context of a hunk holds a KYTY_DIAG_B32 line of the other
            # base), the -U0 diff with --unidiff-zero, per file. The result is judged only by the tree equality.
            d = git('diff', '--binary', a, b).stdout
            args = ['apply', '--cached'] + (['-R'] if kind == 'R' else [])
            r = git(*args, inp=d, env=env, check=False)
            if r.returncode != 0:
                for fn in out('diff', '--name-only', a, b).split():
                    d1 = git('diff', '--binary', a, b, '--', fn).stdout
                    r = git(*args, inp=d1, env=env, check=False)
                    if r.returncode == 0:
                        continue
                    if mode3:
                        r = git(*args, '--3way', inp=d1, env=env, check=False)
                        tag = '3way'
                    else:
                        d0 = git('diff', '-U0', '--binary', a, b, '--', fn).stdout
                        r = git(*args, '--unidiff-zero', inp=d0, env=env, check=False)
                        tag = 'U0'
                    if r.returncode != 0:
                        return 'APPLY-FAIL %s %s..%s %s: %s' % (kind, a, b, fn, r.stderr.decode('utf-8', 'replace').strip()[:300])
                    print('    %s fallback: %s %s..%s %s' % (tag, kind, a, b, fn))
        return git('write-tree', env=env).stdout.decode().strip()
    finally:
        if os.path.exists(idx):
            os.remove(idx)


want = out('rev-parse', FS10 + '^{tree}')
print('FS10 tree', want)
ta = tree_of(BASE, [('F', x + '^', x) for x in MAIN], mode3=True)
member('G3 base + five main diffs == FS10 tree', ta == want, ta)
tan = tree_of(BASE, [('F', x + '^', x) for x in MAIN[:4]], mode3=True)
member('G3 negative control without 7f34b1e2 differs', tan != want, tan)
tb = tree_of(T2, [('R', BASE, DIAG_TOP), ('F', '7f34b1e2^', '7f34b1e2')])
member('G4 T2 - KYTY_DIAG_B32 (11164d72..929b6073 reversed) + 7f34b1e2 == FS10 tree', tb == want, tb)
tbn = tree_of(T2, [('R', BASE, DIAG_TOP)])
member('G4 negative control without 7f34b1e2 differs', tbn != want, tbn)
member('G4 negative control without the reverse step differs', out('rev-parse', T2 + '^{tree}') != want)
# T2 minus KYTY_DIAG_B32 == the FS10a parent tree (1a7eaff8): the four commits on the two bases agree tree for tree
member('G4 T2 - KYTY_DIAG_B32 == 1a7eaff8 tree', tbn == out('rev-parse', '1a7eaff8^{tree}'), tbn)

# G5
names = set(out('diff', '--name-only', BASE, FS10).split())
union = set()
for x in MAIN:
    union |= set(out('diff', '--name-only', x + '^', x).split())
member('G5 names == union of the five commits', names == union, '%d paths: %s' % (len(names), ' '.join(sorted(names))))
ns = out('diff', '--numstat', BASE, FS10)
dels = sum(int(l.split()[1]) for l in ns.splitlines())
adds = sum(int(l.split()[0]) for l in ns.splitlines())
member('G5 base lines removed by FS10 == 0', dels == 0, '(+%d -%d)' % (adds, dels))
member('G5 no path under src/graphics/shader/', not any(n.startswith('src/graphics/shader/') for n in names))

# G6
r = git('grep', '-n', '-E', 'KYTY_DIAG_B32|DiagB32|diagB32', FS10, '--', 'src', 'tests', 'CMakeLists.txt', check=False)
hits = [h for h in r.stdout.decode('utf-8', 'replace').splitlines() if h]
code_hits = []
for h in hits:
    text = h.split(':', 3)[3].strip()
    if not text.startswith('//'):
        code_hits.append(h)
for h in hits:
    print('   G6 hit:', h[:200])
member('G6 KYTY_DIAG_B32 symbols in FS10 - only comment lines', not code_hits, '%d hits, %d not comment' % (len(hits), len(code_hits)))
r = git('cat-file', '-e', FS10 + ':src/common/diagB32.h', check=False)
member('G6 src/common/diagB32.h absent in FS10', r.returncode != 0)

# G7
KEYS = ('DiagB32', 'diagB32', 'DIAG_B32', 'b32')
print('G7 (a)/(b): T2 copies of the four commits - changed lines naming B32 / hunks with B32 context:')
for x in MAIN[:4]:
    d = cdiff(T2C[x])
    fname = None
    hunk = None
    for ln in d.split('\n'):
        if ln.startswith('+++ '):
            fname = ln[6:]
        elif ln.startswith('@@'):
            hunk = ln.split('@@')[1].strip()
        elif ln[:1] in '+-' and not ln.startswith('---') and any(k in ln for k in KEYS):
            print('   (a) %s %s %s | %s' % (T2C[x], fname, hunk, ln[:150]))
        elif ln[:1] == ' ' and any(k in ln for k in KEYS):
            print('   (b) %s %s %s | ctx %s' % (T2C[x], fname, hunk, ln[:150]))
files4 = set()
for x in MAIN[:4]:
    files4 |= set(out('diff', '--name-only', x + '^', x).split())
print('G7 (c): T2 -> FS10 diff in the files of the four commits, hunks:')
d = git('diff', '-U0', T2, FS10, '--', *sorted(files4)).stdout.decode('utf-8', 'replace')
fname = None
for ln in d.split('\n'):
    if ln.startswith('+++ '):
        fname = ln[6:]
    elif ln.startswith('@@'):
        print('   %s %s' % (fname, ln.split('@@')[1].strip()))

# G8
FIX = ['1833ee28', 'c3eb8fe8', '68602c4f', '17adaf80', '4e72289e', 'c1732d1a', 'a86a5ad0', '17eb924e', '10a4800b', 'ec6c4c83',
       '9c726d74', '919c1a19', '082d1612', 'f98e842c', 'e46f55d4', '7719d0f2', '21db93d1', '11164d72', '4414e235', '0005e11f']
bad = []
inter = {}
for c in FIX:
    if git('merge-base', '--is-ancestor', c, FS10, check=False).returncode != 0:
        r2 = out('cherry', FS10, c, c + '^')
        if not r2.startswith('-'):
            bad.append(c)
    fs = set(out('diff', '--name-only', c + '^', c).split()) & names
    if fs:
        inter[c] = sorted(fs)
member('G8 fix commits ancestors of FS10 (or cherry -)', not bad, 'not contained: %s' % bad)
print('   G8 fix commits whose files meet the FS10 diff:', inter or 'none', '(FS10 removes 0 base lines - G5)')
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
