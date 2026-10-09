# FS11b (HPP-715, Red Team, ROADMAP s122 items 647(d)(2), 650(v)): own git checks of the FS11 source (worktree FS11a HEAD ee9632be)
# against the base FS10 dc5d4712, the main commits and the worktree of F29c edition 2 (HEAD 673b780a, binary cabbd818).
# Independent of verify_fs11a.py. A temporary index (GIT_INDEX_FILE) is used for the tree checks; no worktree is touched.
# Prints ALL OK at the end only if every member holds and every negative control discriminates.
import collections
import os
import re
import subprocess
import sys
import tempfile

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
BASE = 'dc5d4712'
FS11 = 'ee9632be'
F29C2 = '673b780a'
# main commit -> its copy in the FS11 worktree chain (order of the cherry-picks of FS11a)
CHAIN = [('73a6e411', 'edebaad9'), ('c94c49e0', '2a371d92'), ('726e751e', 'dab16a57'), ('0db3b3eb', 'eded064e'),
         ('cb022252', 'ee9632be')]
# main commit -> its copy in the F29c edition 2 worktree chain
F29C_CHAIN = [('73a6e411', '8c36ef5c'), ('c94c49e0', '61be23e1'), ('726e751e', '673b780a')]
ok = True


def git(*a, env=None, inp=None):
    r = subprocess.run([G, '-C', REPO] + list(a), capture_output=True, env=env, input=inp)
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')


def out(*a):
    return git(*a)[1]


def changed_lines(c):
    d = out('diff', '--ignore-cr-at-eol', '-U0', c + '^', c)
    res = []
    for line in d.split('\n'):
        if line.startswith('+++') or line.startswith('---'):
            continue
        if line.startswith('+') or line.startswith('-'):
            res.append(line)
    return sorted(res)


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + name + (' - ' + detail if detail else ''))


print('== G1 chains')
log = out('log', '--format=%h %p', '-6', FS11).split('\n')
print('\n'.join(log))
chain = [l.split()[0][:8] for l in log if l]
check('G1 FS11 chain = ee9632be <- eded064e <- dab16a57 <- 2a371d92 <- edebaad9 <- dc5d4712',
      chain == ['ee9632be', 'eded064e', 'dab16a57', '2a371d92', 'edebaad9', 'dc5d4712'], str(chain))
log2 = out('log', '--format=%h %p', '-4', F29C2).split('\n')
chain2 = [l.split()[0][:8] for l in log2 if l]
check('G1 F29c2 chain = 673b780a <- 61be23e1 <- 8c36ef5c <- dc5d4712', chain2 == ['673b780a', '61be23e1', '8c36ef5c', 'dc5d4712'],
      str(chain2))

print('== G2 contains (sorted changed lines equal; git cherry)')
for m, c in CHAIN + F29C_CHAIN:
    a, b = changed_lines(m), changed_lines(c)
    check('G2 lines %s == copy %s' % (m, c), a == b, '%d / %d' % (len(a), len(b)))
for m, c in CHAIN:
    ch = out('cherry', FS11, m, m + '^').strip()
    check('G2 git cherry %s %s -> -' % (FS11, m), ch.startswith('-'), ch[:12])
# negative controls: another commit's copy; one flipped line
neg1 = changed_lines('726e751e') == changed_lines('2a371d92')
check('G2 negative control 726e751e vs copy of c94c49e0 differs', not neg1)
x = changed_lines('c94c49e0')
y = list(changed_lines('2a371d92'))
y[0] = ('-' if y[0][0] == '+' else '+') + y[0][1:]
check('G2 negative control one flipped line differs', x != sorted(y))

print('== G3 tree: base + five main diffs = FS11 tree (temporary index)')
tmpd = tempfile.mkdtemp(prefix='fs11b_idx_')


def build_tree(commits):
    env = dict(os.environ)
    env['GIT_INDEX_FILE'] = os.path.join(tmpd, 'idx_%d' % len(commits))
    git('read-tree', BASE, env=env)
    for c in commits:
        patch = subprocess.run([G, '-C', REPO, 'diff', '--binary', '--full-index', c + '^', c], capture_output=True).stdout
        rc, so, se = git('apply', '--cached', '--3way', '-', env=env, inp=patch)
        if rc != 0:
            print('   apply', c, 'rc', rc, se.strip()[:300])
            return None
    return git('write-tree', env=env)[1].strip()


all5 = [m for m, _ in CHAIN]
t5 = build_tree(all5)
t_fs11 = out('rev-parse', FS11 + '^{tree}').strip()
check('G3 base + 73a6e411 c94c49e0 726e751e 0db3b3eb cb022252 == ee9632be^{tree}', t5 == t_fs11, '%s / %s' % (t5, t_fs11))
t4 = build_tree(all5[:4])
t_e = out('rev-parse', 'eded064e^{tree}').strip()
check('G3 without cb022252 == eded064e^{tree}', t4 == t_e, '%s / %s' % (t4, t_e))
check('G3 negative control: without cb022252 != ee9632be^{tree}', t4 != t_fs11)

print('== G4 default path of FS11 = path =1 of cabbd818 (src/ of F29c edition 2 worktree + FS11a only)')
names = out('diff', '--name-only', F29C2, FS11, '--', 'src/').split()
check('G4 diff 673b780a..ee9632be -- src/ paths == [regionManager.h]', names == ['src/graphics/host_gpu/regionManager.h'], str(names))
d4 = out('diff', '--ignore-cr-at-eol', '-U0', F29C2, FS11, '--', 'src/')
l4 = sorted(l for l in d4.split('\n') if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---'))
check('G4 changed lines of 673b780a..ee9632be in src/ == lines of cb022252', l4 == changed_lines('cb022252'), '%d / %d' % (len(l4), len(changed_lines('cb022252'))))
neg4 = out('diff', '--name-only', F29C2, 'eded064e', '--', 'src/').split()
check('G4 control: 673b780a..eded064e -- src/ is empty (FS11 without FS11a = cabbd818 source in src/)', neg4 == [], str(neg4))
other = out('diff', '--stat', F29C2, FS11, '--', '.', ':(exclude)src/')
print('   outside src/:', other.strip().replace('\n', ' | '))

print('== G5 diff FS11 vs base')
n5 = sorted(out('diff', '--name-only', BASE, FS11).split())
union = set()
for m, _ in CHAIN:
    union |= set(out('show', '--name-only', '--format=', m).split())
check('G5 paths == union of the five commits', n5 == sorted(union), str(n5))
ns = out('diff', '--numstat', BASE, FS11)
plus = sum(int(l.split()[0]) for l in ns.split('\n') if l.strip())
minus = sum(int(l.split()[1]) for l in ns.split('\n') if l.strip())
check('G5 removed lines vs base == 0', minus == 0, '+%d -%d' % (plus, minus))
check('G5 no path under src/graphics/shader/', not any(p.startswith('src/graphics/shader/') for p in n5))
outside = [p for p in n5 if not p.startswith('tests/')]
fix_files = set()
for m in ['c94c49e0', '726e751e', 'cb022252']:
    fix_files |= set(out('show', '--name-only', '--format=', m).split())
extra = [p for p in outside if p not in fix_files]
check('G5 outside tests/ beyond c94c49e0/726e751e/FS11a files == [CMakeLists.txt] (reading of item 650(v))', extra == ['CMakeLists.txt'], str(extra))
cm = out('diff', '-U0', BASE, FS11, '--', 'CMakeLists.txt')
added = [l[1:] for l in cm.split('\n') if l.startswith('+') and not l.startswith('+++')]
removed = [l for l in cm.split('\n') if l.startswith('-') and not l.startswith('---')]
hunks = re.findall(r'^@@ .*$', cm, re.M)
print('   CMakeLists.txt hunks', len(hunks), 'added', len(added), 'removed', len(removed))
for l in added:
    print('   +', l)
block = '\n'.join(added)
check('G5 CMakeLists.txt: one hunk, only added lines', len(hunks) == 1 and not removed)
check('G5 CMakeLists.txt: block is the b12_bdastamp_stand target with EXCLUDE_FROM_ALL, kyty_emulator not named',
      'add_executable(b12_bdastamp_stand EXCLUDE_FROM_ALL' in block.replace('\t', ' ').replace('  ', ' ') and 'kyty_emulator' not in block)

print('== G8 shipped fixes untouched: contained in FS11 (ancestor or cherry -); FS11 removes no base line (G5)')
FIXES = {'Ф10': ['1833ee28', 'c3eb8fe8'], 'Ф16': ['68602c4f', '17adaf80'], 'Б42': ['4e72289e'], 'Б33': ['c1732d1a'],
         'Б4': ['a86a5ad0', '17eb924e'], 'Ф8': ['10a4800b', 'ec6c4c83'], 'Б24': ['9c726d74', '919c1a19'],
         'Ф19': ['082d1612', 'f98e842c', 'e46f55d4', '7719d0f2'], 'Б13': ['21db93d1', '11164d72'], 'P-var': ['4414e235'],
         'S-replay': ['0005e11f'], 'Ф27': ['a42f50b1', '7bc87bc8', '64a1fa40', '1a7eaff8', 'dc5d4712']}
n5set = set(n5)
for k, cs in FIXES.items():
    for c in cs:
        # the form of FS10b G8: an ancestor, or git cherry '-' (shipping worktrees carry fixes as cherry-picks)
        rc = git('merge-base', '--is-ancestor', c, FS11)[0]
        how = 'ancestor' if rc == 0 else ('cherry ' + out('cherry', FS11, c, c + '^').strip()[:1])
        fs = sorted(set(out('show', '--name-only', '--format=', c).split()) & n5set)
        check('G8 %s %s contained in ee9632be (ancestor or cherry -)' % (k, c), how in ('ancestor', 'cherry -'),
              how + ('; files met by the FS11 diff: %s' % fs if fs else ''))
rc = git('merge-base', '--is-ancestor', '585d997d', FS11)[0]
check('G8 F30d 585d997d NOT an ancestor of ee9632be', rc != 0)
dd = out('diff', BASE, FS11, '--', 'src/')
check('G8 no KYTY_DIAG_B32 / rts_bad_ in the FS11 diff', 'KYTY_DIAG_B32' not in dd and 'rts_bad_' not in dd)
check('G8 shaderReplay.cpp blob base == FS11',
      out('rev-parse', BASE + ':src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp') ==
      out('rev-parse', FS11 + ':src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'))

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
