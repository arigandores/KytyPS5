# FS13b (HPP-788, Red Team, ROADMAP s122 item 697(g)(2)): git members of the FS13 review, own code.
# Worktree C:/kyty/f287/fs13b/wt (HEAD ea6c6e9e = FS13). Base FS12 730ed40a. F38a worktree HEAD 531d6488 (code d7a30e55 = e9dd8604).
# R1  diff FS13 vs base: path set; outside tests/ and docs/ only CMakeLists.txt (+5 stand target lines) and src/kernel/fileSystem.cpp.
# R2  src/ of FS13 vs F38a worktree 531d6488 = exactly the FS13a commit diff (0861c391..ea6c6e9e); src/ of 0861c391 = src/ of 531d6488.
# R3  "contains": ancestor or git cherry '-' for e9dd8604 cbfe8375 227e1b36 c94c49e0 726e751e cb022252; negative controls.
# R4  untouched fixes: every src file of the base naming the knob of F21 B12 F27(B36) B13 B33(S_PCW) F10 F16(SVAL) F19 B42 B4 F8 B24
#     S-replay P-var(PVAR, GAME_PATCH) has the same blob in FS13, except fileSystem.cpp: there every -/+ line of the diff is checked
#     not to name another knob or Fix<X> symbol.
# R5  src/graphics/shader/** paths in the diff: 0; KYTY_SHADER_SOURCE_HASH of own build = 9177b426...
# R6  =0 path text check: every added code line in KernelRead/KernelPread/ReadGuestWithRetry either is under
#     'if (read_failed_twice && FixF25Enabled())' / 'if (fix_f25_eio)' or is a declaration / the flag write (listed for the eye).
import re, subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/f287/fs13b/wt'
FS13, BASE, F38A, PRE = 'ea6c6e9e', '730ed40a', '531d6488', '0861c391'
ok = True


def git(*a):
    return subprocess.run([G, '-C', WT] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace').stdout


def check(name, cond, info=''):
    global ok
    ok &= bool(cond)
    print('%-4s %s %s' % ('ok' if cond else 'FAIL', name, info))


# R1
paths = git('diff', '--name-only', BASE, FS13).split()
outside = [p for p in paths if not p.startswith('tests/') and not p.startswith('docs/')]
print('R1 paths', len(paths), 'outside tests/docs', outside)
check('R1 outside tests/docs == {CMakeLists.txt, src/kernel/fileSystem.cpp}', sorted(outside) == ['CMakeLists.txt', 'src/kernel/fileSystem.cpp'])
cm = git('diff', '-U0', BASE, FS13, '--', 'CMakeLists.txt').splitlines()
plus = [l for l in cm if l.startswith('+') and not l.startswith('+++')]
minus = [l for l in cm if l.startswith('-') and not l.startswith('---')]
code_plus = [l for l in plus if l[1:].strip() and not l[1:].lstrip().startswith('#')]
print('R1 CMakeLists +%d -%d code+ %s' % (len(plus), len(minus), code_plus))
check('R1 CMakeLists only the stand target', len(minus) == 0 and len(plus) == 5 and len(code_plus) == 2 and 'f25_read_fail_stand' in code_plus[0] and 'F25ReadFailStand.cpp' in code_plus[1])
docs = [p for p in paths if p.startswith('docs/')]
check('R1 docs paths only docs/track-f/f37a*', all(p.startswith('docs/track-f/f37a') for p in docs), str(len(docs)))
tests = [p for p in paths if p.startswith('tests/')]
check('R1 tests paths only tests/F25ReadFailStand.cpp', tests == ['tests/F25ReadFailStand.cpp'])

# R2
t_f38a = git('rev-parse', F38A + ':src').strip()
t_pre = git('rev-parse', PRE + ':src').strip()
t_d7 = git('rev-parse', 'd7a30e55:src').strip()
print('R2 src trees: F38a wt %s, d7a30e55 %s, FS13 before FS13a %s' % (t_f38a, t_d7, t_pre))
check('R2 src/ FS13 before FS13a == src/ F38a worktree', t_f38a == t_pre == t_d7)
d1 = git('diff', F38A, FS13, '--', 'src/')
d2 = git('diff', PRE, FS13, '--', 'src/')
check('R2 diff src/ F38a wt -> FS13 == FS13a commit diff', d1 == d2 and d1 != '', 'lines %d' % len(d1.splitlines()))
print('R2 FS13a commit paths', git('diff', '--name-only', PRE, FS13).split())
neg = git('diff', BASE, FS13, '--', 'src/')
check('R2 negative: diff src/ base -> FS13 != FS13a diff', neg != d2)

# R3
need = ['e9dd8604', 'cbfe8375', '227e1b36', 'c94c49e0', '726e751e', 'cb022252']


def contains(tip, c, upstream_base=None):
    anc = subprocess.run([G, '-C', WT, 'merge-base', '--is-ancestor', c, tip]).returncode == 0
    if anc:
        return 'ancestor'
    out = git('cherry', tip, c, c + '^').split()  # upstream = tip, head = c, limit = c^ -> exactly the one commit c
    return 'cherry ' + (' '.join(out[0::2]) if out else '?')


for c in need:
    r = contains(FS13, c)
    check('R3 FS13 contains ' + c, r == 'ancestor' or r == 'cherry -', r)
for tip, c, why in [(BASE, 'e9dd8604', 'code F25 not in base'), (BASE, '3630f116', 'FS13a not in base'),
                    ('ee9632be', 'cbfe8375', 'FS12a default not in FS11'), (FS13, '5c21c387', 'code F24 not in FS13'),
                    (FS13, '3630f116', 'positive: FS13a in FS13')]:
    r = contains(tip, c)
    expect_yes = why.startswith('positive')
    got_yes = r == 'ancestor' or r == 'cherry -'
    check('R3 control %s in %s (%s)' % (c, tip, why), got_yes == expect_yes, r)

# R4
knobs = {'F21': ['KYTY_FIX_F21'], 'B12': ['KYTY_FIX_B12'], 'F27': ['KYTY_FIX_B36'], 'B13': ['KYTY_FIX_B13'],
         'B33': ['KYTY_S_PCW'], 'F10': ['KYTY_FIX_F10'], 'F16': ['KYTY_FIX_SVAL'], 'F19': ['KYTY_FIX_F19'],
         'B42': ['KYTY_FIX_B42'], 'B4': ['KYTY_FIX_B4'], 'F8': ['KYTY_FIX_F8'], 'B24': ['KYTY_FIX_B24'],
         'S-replay': ['KYTY_S_REPLAY'], 'P-var': ['KYTY_PVAR', 'KYTY_GAME_PATCH']}
for row, names in knobs.items():
    files = set()
    for n in names:
        files |= set(git('grep', '-l', n, BASE, '--', 'src/').replace(BASE + ':', '').split())
    same = [f for f in files if git('rev-parse', BASE + ':' + f).strip() == git('rev-parse', FS13 + ':' + f).strip()]
    diff = sorted(files - set(same))
    check('R4 %s files %d same blob %d' % (row, len(files), len(same)), len(files) > 0 and (diff == [] or diff == ['src/kernel/fileSystem.cpp']), 'differ ' + str(diff))
fsd = git('diff', '-U0', BASE, FS13, '--', 'src/kernel/fileSystem.cpp').splitlines()
chg = [l for l in fsd if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---')]
bad = [l for l in chg if re.search(r'KYTY_(?!FIX_F25)[A-Z0-9_]+|Fix(?!F25)[A-Z][0-9A-Za-z]*', l)]
print('R4 fileSystem.cpp changed lines', len(chg), 'naming another knob/Fix symbol:', bad)
check('R4 fileSystem.cpp changes name only F25', bad == [] and len(chg) > 0)
cnt_minus = [l for l in chg if l.startswith('-')]
print('R4 fileSystem.cpp removed lines:', cnt_minus)

# R5
sh = [p for p in paths if p.startswith('src/graphics/shader/')]
check('R5 shader paths 0', sh == [])
h = open('C:/kyty/f287/fs13b/build/kytyGitVersion.h', encoding='utf-8', errors='replace').read() if False else None
import glob
hs = glob.glob('C:/kyty/f287/fs13b/build/**/kytyGitVersion.h', recursive=True)
sig = None
for p in hs:
    m = re.search(r'KYTY_SHADER_SOURCE_HASH\s+"([0-9a-f]+)"', open(p, encoding='utf-8', errors='replace').read())
    if m:
        sig = m.group(1)
        print('R5 header', p)
check('R5 signature of own build == 9177b426...', sig == '9177b4267de1fb8bac7d1113afd8733210addfac', str(sig))
ver = None
for p in hs:
    m = re.search(r'"(KytyPS5-[^"]+)"', open(p, encoding='utf-8', errors='replace').read())
    if m:
        ver = m.group(1)
print('R5 version string', ver)
check('R5 version string ends with -gea6c6e9e', bool(ver) and ver.endswith('-gea6c6e9e'))

# R6 (=0 path by text; the eye reads the printed lines)
added = [l[1:] for l in chg if l.startswith('+')]
code = [l for l in added if l.strip() and not l.strip().startswith('//')]
print('R6 added code lines:')
for l in code:
    print('   ', l)
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
