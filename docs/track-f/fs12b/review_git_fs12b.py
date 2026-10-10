# FS12b (HPP-751, Red Team, ROADMAP s122 item 683(g)(2)): own git checks of the FS12 source (worktree FS12a HEAD 730ed40a)
# against the base FS11 ee9632be, the main commits and the worktree of F33c (HEAD 0c57cfed, binary 2b393af8 accepted by F33d).
# A port of my FS11b review_git_fs11b.py; independent of verify_fs12a.py. A temporary index (GIT_INDEX_FILE) is used for the
# tree checks; no worktree is touched. Prints ALL OK at the end only if every member holds and every negative control
# discriminates.
import os
import re
import subprocess
import sys
import tempfile

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
BASE = 'ee9632be'
FS12 = '730ed40a'
F33C = '0c57cfed'
# main commit -> its copy in the FS12 worktree chain (order of the cherry-picks of FS12a)
CHAIN = [('227e1b36', '17c71ea6'), ('e5979953', '25861288'), ('5237fdff', '9aaea58c'), ('cbfe8375', '730ed40a')]
# main commit -> its copy in the F33c worktree chain
F33C_CHAIN = [('227e1b36', 'b536c419'), ('e5979953', '0c57cfed')]
ok = True


def git(*a, env=None, inp=None):
    r = subprocess.run([G, '-C', REPO] + list(a), capture_output=True, env=env, input=inp)
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')


def out(*a):
    return git(*a)[1]


def pm_lines(d):
    return sorted(l for l in d.split('\n') if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---'))


def changed_lines(c):
    return pm_lines(out('diff', '--ignore-cr-at-eol', '-U0', c + '^', c))


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + name + (' - ' + detail if detail else ''))


print('== G1 chains')
log = out('log', '--format=%h %p', '-5', FS12).split('\n')
print('\n'.join(log))
chain = [l.split()[0][:8] for l in log if l]
check('G1 FS12 chain = 730ed40a <- 9aaea58c <- 25861288 <- 17c71ea6 <- ee9632be',
      chain == ['730ed40a', '9aaea58c', '25861288', '17c71ea6', 'ee9632be'], str(chain))
log2 = out('log', '--format=%h %p', '-3', F33C).split('\n')
chain2 = [l.split()[0][:8] for l in log2 if l]
check('G1 F33c chain = 0c57cfed <- b536c419 <- ee9632be', chain2 == ['0c57cfed', 'b536c419', 'ee9632be'], str(chain2))

print('== G2 contains (sorted changed lines equal; git cherry)')
for m, c in CHAIN + F33C_CHAIN:
    a, b = changed_lines(m), changed_lines(c)
    check('G2 lines %s == copy %s' % (m, c), a == b, '%d / %d' % (len(a), len(b)))
for m in ['227e1b36', 'e5979953', '5237fdff', 'cbfe8375', 'c94c49e0', '726e751e', 'cb022252', '73a6e411', '0db3b3eb']:
    rc = git('merge-base', '--is-ancestor', m, FS12)[0]
    ch = out('cherry', FS12, m, m + '^').strip()
    how = 'ancestor' if rc == 0 else 'cherry ' + ch[:1]
    check('G2 %s contained in 730ed40a (ancestor or git cherry -)' % m, how in ('ancestor', 'cherry -'), how)
# negative controls: the rule says "no" where it must
ch = out('cherry', FS12, '5f48cc3e', '5f48cc3e^').strip()
check('G2 negative control: stand edition 1 5f48cc3e - git cherry + in FS12 and not an ancestor',
      ch.startswith('+') and git('merge-base', '--is-ancestor', '5f48cc3e', FS12)[0] != 0, ch[:12])
ch = out('cherry', BASE, '227e1b36', '227e1b36^').strip()
check('G2 negative control: 227e1b36 - git cherry + in the base ee9632be', ch.startswith('+'), ch[:12])
neg1 = changed_lines('5237fdff') == changed_lines('25861288')
check('G2 negative control: 5237fdff vs the copy of e5979953 differs', not neg1)
x = changed_lines('227e1b36')
y = list(changed_lines('17c71ea6'))
y[0] = ('-' if y[0][0] == '+' else '+') + y[0][1:]
check('G2 negative control: one flipped line differs', x != sorted(y))

print('== G3 tree: base + four main diffs = FS12 tree (temporary index)')
tmpd = tempfile.mkdtemp(prefix='fs12b_idx_')


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


all4 = [m for m, _ in CHAIN]
t4 = build_tree(all4)
t_fs12 = out('rev-parse', FS12 + '^{tree}').strip()
check('G3 base + 227e1b36 e5979953 5237fdff cbfe8375 == 730ed40a^{tree}', t4 == t_fs12, '%s / %s' % (t4, t_fs12))
t3 = build_tree(all4[:3])
t_9 = out('rev-parse', '9aaea58c^{tree}').strip()
check('G3 without cbfe8375 == 9aaea58c^{tree}', t3 == t_9, '%s / %s' % (t3, t_9))
check('G3 negative control: without cbfe8375 != 730ed40a^{tree}', t3 != t_fs12)
t2 = build_tree(all4[:2])
t_f = out('rev-parse', F33C + '^{tree}').strip()
check('G3 base + 227e1b36 e5979953 == F33c worktree 0c57cfed^{tree}', t2 == t_f, '%s / %s' % (t2, t_f))

print('== G4 default path of FS12 = path =1 of 2b393af8 (src/ of the F33c worktree + 5237fdff + FS12a only)')
names = sorted(out('diff', '--name-only', F33C, FS12, '--', 'src/').split())
allowed = sorted(set(out('show', '--name-only', '--format=', '5237fdff').split()) | set(out('show', '--name-only', '--format=', 'cbfe8375').split()))
check('G4 diff 0c57cfed..730ed40a -- src/ paths == files of 5237fdff + cbfe8375', names == allowed, '%s / %s' % (names, allowed))
l4 = pm_lines(out('diff', '--ignore-cr-at-eol', '-U0', F33C, FS12, '--', 'src/'))
exp4 = sorted(changed_lines('5237fdff') + changed_lines('cbfe8375'))
check('G4 changed lines of 0c57cfed..730ed40a in src/ == lines of 5237fdff + cbfe8375 (multiset)', l4 == exp4, '%d / %d' % (len(l4), len(exp4)))
l4n = pm_lines(out('diff', '--ignore-cr-at-eol', '-U0', F33C, '9aaea58c', '--', 'src/'))
check('G4 negative control: without FS12a the lines differ (== lines of 5237fdff only)', l4n == changed_lines('5237fdff') and l4n != exp4,
      '%d' % len(l4n))
ctrl = out('diff', '--name-only', F33C, '25861288', '--', '.').split()
check('G4 control: 0c57cfed..25861288 is empty (same source at step 2 of both chains)', ctrl == [], str(ctrl))
other = out('diff', '--name-only', F33C, FS12, '--', '.', ':(exclude)src/').split()
check('G4 outside src/: no path differs between 0c57cfed and 730ed40a', other == [], str(other))
cbf = out('diff', '-U0', 'cbfe8375^', 'cbfe8375', '--', 'src/')
code_pm = [l for l in pm_lines(cbf) if not l[1:].strip().startswith('//')]
print('   cbfe8375 code (non-comment) +/- lines:')
for l in code_pm:
    print('     ', l.strip())
# try 1 counted lines, not statements (the new initialiser is two lines: getenv + expression) - a defect of my check, FS12b times.txt
code_rm = [l[1:].strip() for l in code_pm if l.startswith('-')]
code_add = [l[1:].strip() for l in code_pm if l.startswith('+')]
check('G4 cbfe8375 code: removes one line (the EnvFlagOn initialiser of g_fix_f21), adds the getenv line + the ON-IF-UNSET initialiser; the rest comments',
      len(code_rm) == 1 and code_rm[0].startswith('g_fix_f21  = EnvFlagOn("KYTY_FIX_F21");') and
      code_add == ['const char* value = std::getenv("KYTY_FIX_F21");', "g_fix_f21  = value == nullptr || value[0] == '\\0' || EnvValueOn(value);"],
      str(code_rm) + ' / ' + str(code_add))

print('== G5 diff FS12 vs base')
n5 = sorted(out('diff', '--name-only', BASE, FS12).split())
union = set()
for m, _ in CHAIN:
    union |= set(out('show', '--name-only', '--format=', m).split())
check('G5 paths == union of the four commits', n5 == sorted(union), str(n5))
check('G5 all paths under src/ (no tests/, no CMakeLists.txt)', all(p.startswith('src/') for p in n5))
check('G5 no path under src/graphics/shader/', not any(p.startswith('src/graphics/shader/') for p in n5))
d5 = out('diff', '--ignore-cr-at-eol', '-U0', BASE, FS12)
removed = [l for l in pm_lines(d5) if l.startswith('-')]
added = [l for l in pm_lines(d5) if l.startswith('+')]
print('   +%d -%d; removed base lines:' % (len(added), len(removed)))
for l in removed:
    print('     ', l.strip())
check('G5 the only removed base line is the Graphics lifecycle Initialize, re-added inside the stand branch',
      [l[1:].strip() for l in removed] == ['subsystems.Initialize<Libs::Graphics::Lifecycle>();'] and
      any(l[1:].strip() == 'subsystems.Initialize<Libs::Graphics::Lifecycle>();' for l in added))  # try 1 stripped '-<TAB>' wrong
lsum = sorted(sum([changed_lines(m) for m, _ in CHAIN], []))
# the four diffs add then remove/replace some of their own lines; the tree equality (G3) is the strong form, this prints sizes
print('   lines of the four commits: %d; lines of base..FS12: %d (own lines replaced inside the chain cancel)' % (len(lsum), len(added) + len(removed)))

print('== G6 hunks of base..FS12 that touch base function bodies (eye check of the =0 path)')
d6 = out('diff', '--ignore-cr-at-eol', '-U1', '-W', BASE, FS12, '--', 'src/emulator.cpp', 'src/common/subsystems.cpp')
for h in re.split(r'(?m)^(?=@@ )', d6):
    if not h.startswith('@@'):
        continue
    body = h.split('\n')
    head = body[0]
    ctx = [l for l in body[1:] if l.startswith(' ')]
    pls = [l for l in body[1:] if l.startswith('+')]
    if len(pls) > 40:
        print('   %s : +%d lines (new code block, not printed)' % (head[:120], len(pls)))
        continue
    print('   ' + head[:160])
    for l in body[1:]:
        if l.startswith('+') or l.startswith('-'):
            print('     ' + l[:160])

print('== G8 shipped fixes untouched: contained in FS12 (ancestor or cherry -); FS12 removes one base line only (G5)')
FIXES = {'Ф10': ['1833ee28', 'c3eb8fe8'], 'Ф16': ['68602c4f', '17adaf80'], 'Б42': ['4e72289e'], 'Б33': ['c1732d1a'],
         'Б4': ['a86a5ad0', '17eb924e'], 'Ф8': ['10a4800b', 'ec6c4c83'], 'Б24': ['9c726d74', '919c1a19'],
         'Ф19': ['082d1612', 'f98e842c', 'e46f55d4', '7719d0f2'], 'Б13': ['21db93d1', '11164d72'], 'P-var': ['4414e235'],
         'S-replay': ['0005e11f'], 'Ф27': ['a42f50b1', '7bc87bc8', '64a1fa40', '1a7eaff8', 'dc5d4712'],
         'Б12': ['73a6e411', 'c94c49e0', '726e751e', '0db3b3eb', 'cb022252', 'ee9632be']}
n5set = set(n5)
for k, cs in FIXES.items():
    for c in cs:
        rc = git('merge-base', '--is-ancestor', c, FS12)[0]
        how = 'ancestor' if rc == 0 else ('cherry ' + out('cherry', FS12, c, c + '^').strip()[:1])
        fs = sorted(set(out('show', '--name-only', '--format=', c).split()) & n5set)
        check('G8 %s %s contained in 730ed40a (ancestor or cherry -)' % (k, c), how in ('ancestor', 'cherry -'),
              how + ('; files met by the FS12 diff: %s' % fs if fs else ''))
for c in ['585d997d', '5f48cc3e']:
    rc = git('merge-base', '--is-ancestor', c, FS12)[0]
    check('G8 %s NOT an ancestor of 730ed40a' % c, rc != 0)
dd = out('diff', BASE, FS12, '--', 'src/')
check('G8 no KYTY_DIAG_B32 / rts_bad_ in the FS12 diff', 'KYTY_DIAG_B32' not in dd and 'rts_bad_' not in dd)
check('G8 shaderReplay.cpp blob base == FS12',
      out('rev-parse', BASE + ':src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp') ==
      out('rev-parse', FS12 + ':src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'))
fixfiles = set()
for k, cs in FIXES.items():
    for c in cs:
        fixfiles |= set(out('show', '--name-only', '--format=', c).split())
print('   files of the FS12 diff also touched by shipped fixes:', sorted(fixfiles & n5set))

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
