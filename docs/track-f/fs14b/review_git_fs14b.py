# FS14b (HPP-813, Red Team, ROADMAP s122 items 710(g)(2), 712(g)(2), 717): git members of the FS14 review, own code
# (new file; the form of my review_git_fs13b.py).
# Own clean worktree C:/kyty/f287/fs14b/wt (HEAD eb7e8b91 = FS14). Base FS13 ea6c6e9e. F40a2 tag worktree 7c38e497,
# F44a tag worktree e148f54c (both on FS12 730ed40a).
# Worktree commits (cherry-pick -x): b50e90e8 <- 5c21c387 (F24 code), cd422a94 <- e3aa4b4d (stand ed. 2),
# 6eb0f1a1 <- 57f9e528 (init_owner, flap fields), 76c1058f <- c8836f14 (FS14a F24 default), c5eb48b0 <- 15c9d2f2 (F29 code
# and stand), eb7e8b91 <- 78e45af3 (FS14a F29 default).
# R1  diff FS14 vs base FS13: path set; src/ = files of the three F40 commits + faultManager.cpp/.h + FS14a commits only;
#     outside src/: CMakeLists.txt (+6 = stand target f29_fault_stand only), tests/F29FaultStand.cpp, docs/track-f/f44a/*;
#     each worktree commit has the patch-id of its main original; the six-commit chain parents are exact.
# R2  src/ FS14 vs F40a2 worktree 7c38e497: paths = fileSystem.cpp (FS13), joyPump.cpp/.h (FS14a F24 default),
#     faultManager.cpp/.h (15c9d2f2 + 78e45af3); per path the diff equals the diff of exactly those commits; every other src
#     blob equal; the src tree of 7c38e497 = src of 6eb0f1a1 with fileSystem.cpp of FS12 (i.e. F40a2 code = FS14 F40 code).
# R2b src/ FS14 vs F44a worktree e148f54c: paths = faultManager.cpp/.h (78e45af3 only), F40 files (F40 commits + FS14a F24
#     default), fileSystem.cpp (FS13); faultManager diff e148f54c..FS14 == diff c5eb48b0..eb7e8b91.
# R3  "contains": git cherry '-' or ancestor for 12 commits; negative controls.
# R4  untouched fixes: every src file of the base naming the knob of F25 F21 B12 F27(B36) B13 B33(S_PCW) F10 F16(SVAL) F19
#     B42 B4 F8 B24 S-replay P-var has the same blob in FS14, except files of the F40 / F29 commits; in those every -/+ line
#     of the diff base..FS14 is checked not to name another knob or Fix<X> symbol other than F24 / F29 / B24 (B24 lines
#     printed for the eye: PadOutput and FixB24On must be unchanged).
# R5  src/graphics/shader/** paths 0; KYTY_SHADER_SOURCE_HASH of own build = 9177b426...; version ends -geb7e8b91.
# R6  =0 / default reading: the only changes of FS14a commits are the knob reading expressions + comments (printed).
import glob, re, subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/f287/fs14b/wt'
FS14, BASE, F40A2, F44A, FS12 = 'eb7e8b91', 'ea6c6e9e', '7c38e497', 'e148f54c', '730ed40a'
CHAIN = [('b50e90e8', '5c21c387'), ('cd422a94', 'e3aa4b4d'), ('6eb0f1a1', '57f9e528'), ('76c1058f', 'c8836f14'),
         ('c5eb48b0', '15c9d2f2'), ('eb7e8b91', '78e45af3')]
F40_SRC = {'src/graphics/presentation/window/hostInput.cpp', 'src/graphics/presentation/window/joyPump.cpp',
           'src/graphics/presentation/window/joyPump.h', 'src/graphics/presentation/window/vulkanWindow.cpp',
           'src/graphics/presentation/window/window.cpp', 'src/libs/controller.cpp'}
F29_SRC = {'src/graphics/host_gpu/renderer/cache/faultManager.cpp', 'src/graphics/host_gpu/renderer/cache/faultManager.h'}
FS = 'src/kernel/fileSystem.cpp'
JP = {'src/graphics/presentation/window/joyPump.cpp', 'src/graphics/presentation/window/joyPump.h'}
ok = True


def git(*a, inp=None):
    return subprocess.run([G, '-C', WT] + list(a), capture_output=True, input=inp).stdout.decode('utf-8', 'replace')


def check(name, cond, info=''):
    global ok
    ok &= bool(cond)
    print('%-4s %s %s' % ('ok' if cond else 'FAIL', name, info))


def blob(c, p):
    return git('rev-parse', '%s:%s' % (c, p)).strip()


def pid(c):
    return git('patch-id', '--stable', inp=git('show', c).encode('utf-8')).split()[0] if git('show', c) else ''


# R1
paths = git('diff', '--name-only', BASE, FS14).split()
src = sorted(p for p in paths if p.startswith('src/'))
print('R1 paths', len(paths), 'src', src)
check('R1 src/ == F40 files + faultManager.cpp/.h', set(src) == F40_SRC | F29_SRC)
other = sorted(p for p in paths if not p.startswith('src/'))
check('R1 outside src/: CMakeLists.txt, tests/F29FaultStand.cpp, docs/track-f/f44a/*',
      [p for p in other if not p.startswith('docs/track-f/f44a/')] == ['CMakeLists.txt', 'tests/F29FaultStand.cpp'], str(other))
cm = git('diff', '-U0', BASE, FS14, '--', 'CMakeLists.txt').splitlines()
plus = [l for l in cm if l.startswith('+') and not l.startswith('+++')]
minus = [l for l in cm if l.startswith('-') and not l.startswith('---')]
code_plus = [l for l in plus if l[1:].strip() and not l[1:].lstrip().startswith('#')]
print('R1 CMakeLists +%d -%d code+ %s' % (len(plus), len(minus), code_plus))
check('R1 CMakeLists only the f29_fault_stand target', len(minus) == 0 and code_plus and all('f29_fault_stand' in l or 'F29FaultStand' in l for l in code_plus))
check('R1 CMakeLists = 15c9d2f2 CMake diff', git('diff', 'c5eb48b0^', 'c5eb48b0', '--', 'CMakeLists.txt').split('\n')[2:] == git('diff', BASE, FS14, '--', 'CMakeLists.txt').split('\n')[2:])
par = BASE
for w, m in CHAIN:
    p = git('rev-parse', w + '^').strip()[:8]
    check('R1 chain %s parent %s' % (w, par), p == par[:8], p)
    pw, pm = pid(w), pid(m)
    check('R1 patch-id %s == %s (main)' % (w, m), pw and pw == pm, pw[:12])
    par = w
check('R1 FS14 tip == eb7e8b91', git('rev-parse', 'HEAD').strip()[:8] == FS14)

# R2
p2 = sorted(git('diff', '--name-only', F40A2, FS14, '--', 'src/').split())
print('R2 src paths F40a2 wt -> FS14', p2)
check('R2 paths == fileSystem.cpp + joyPump.cpp/.h + faultManager.cpp/.h', set(p2) == {FS} | JP | F29_SRC)
check('R2 fileSystem.cpp diff == FS13 diff (FS12 -> FS13)', git('diff', F40A2, FS14, '--', FS) == git('diff', FS12, BASE, '--', FS) != '')
check('R2 joyPump diff == FS14a F24 default commit 76c1058f', git('diff', F40A2, FS14, '--', *sorted(JP)) == git('diff', '6eb0f1a1', '76c1058f', '--', *sorted(JP)) != '')
check('R2 faultManager diff == 15c9d2f2 + 78e45af3 (c5eb48b0^ .. eb7e8b91)', git('diff', F40A2, FS14, '--', *sorted(F29_SRC)) == git('diff', '76c1058f', FS14, '--', *sorted(F29_SRC)) != '')
for p in sorted(F40_SRC - JP):
    check('R2 %s blob F40a2 wt == FS14' % p, blob(F40A2, p) == blob(FS14, p))
check('R2 F40a2 code commits = 6eb0f1a1 in F40 files', all(blob(F40A2, p) == blob('6eb0f1a1', p) for p in F40_SRC))
check('R2 negative: diff src/ base FS13 -> FS14 != diff F40a2 wt -> FS14', git('diff', BASE, FS14, '--', 'src/') != git('diff', F40A2, FS14, '--', 'src/'))

# R2b
p2b = sorted(git('diff', '--name-only', F44A, FS14, '--', 'src/').split())
print('R2b src paths F44a wt -> FS14', p2b)
check('R2b paths == faultManager.cpp/.h + F40 files + fileSystem.cpp', set(p2b) == F29_SRC | F40_SRC | {FS})
check('R2b faultManager diff == 78e45af3 only (c5eb48b0 -> eb7e8b91)', git('diff', F44A, FS14, '--', *sorted(F29_SRC)) == git('diff', 'c5eb48b0', FS14, '--', *sorted(F29_SRC)) != '')
check('R2b F40 files diff == ea6c6e9e -> 76c1058f', git('diff', F44A, FS14, '--', *sorted(F40_SRC)) == git('diff', BASE, '76c1058f', '--', *sorted(F40_SRC)) != '')
check('R2b fileSystem.cpp diff == FS13 diff', git('diff', F44A, FS14, '--', FS) == git('diff', FS12, BASE, '--', FS))
check('R2b F44a code = 15c9d2f2 blobs in faultManager', all(blob(F44A, p) == blob('15c9d2f2', p) for p in F29_SRC))


# R3
def contains(tip, c):
    if subprocess.run([G, '-C', WT, 'merge-base', '--is-ancestor', c, tip]).returncode == 0:
        return 'ancestor'
    out = git('cherry', tip, c, c + '^').split()
    return 'cherry ' + (' '.join(out[0::2]) if out else '?')


need = ['15c9d2f2', '78e45af3', '5c21c387', '57f9e528', 'c8836f14', 'e9dd8604', '3630f116', '227e1b36', 'cbfe8375',
        'c94c49e0', '726e751e', 'cb022252']
for c in need:
    r = contains(FS14, c)
    check('R3 FS14 contains ' + c, r in ('ancestor', 'cherry -'), r)
for tip, c, yes in [(BASE, '5c21c387', False), (BASE, '57f9e528', False), (BASE, 'c8836f14', False), (BASE, '15c9d2f2', False),
                    (BASE, '78e45af3', False), ('76c1058f', '15c9d2f2', False), ('76c1058f', '78e45af3', False),
                    (FS14, 'a6342c98', False), (FS14, 'e3aa4b4d', True)]:
    r = contains(tip, c)
    check('R3 control %s in %s expect %s' % (c, tip, 'yes' if yes else 'no'), (r in ('ancestor', 'cherry -')) == yes, r)

# R4
knobs = {'F25': ['KYTY_FIX_F25'], 'F21': ['KYTY_FIX_F21'], 'B12': ['KYTY_FIX_B12'], 'F27': ['KYTY_FIX_B36'],
         'B13': ['KYTY_FIX_B13'], 'B33': ['KYTY_S_PCW'], 'F10': ['KYTY_FIX_F10'], 'F16': ['KYTY_FIX_SVAL'],
         'F19': ['KYTY_FIX_F19'], 'B42': ['KYTY_FIX_B42'], 'B4': ['KYTY_FIX_B4'], 'F8': ['KYTY_FIX_F8'],
         'B24': ['KYTY_FIX_B24'], 'S-replay': ['KYTY_S_REPLAY'], 'P-var': ['KYTY_PVAR', 'KYTY_GAME_PATCH']}
changed = F40_SRC | F29_SRC
for row, names in knobs.items():
    files = set()
    for n in names:
        files |= set(git('grep', '-l', n, BASE, '--', 'src/').replace(BASE + ':', '').split())
    diff = sorted(f for f in files if blob(BASE, f) != blob(FS14, f))
    check('R4 %s files %d' % (row, len(files)), len(files) > 0 and set(diff) <= changed, 'differ ' + str(diff))
# Edition 2 of the filter (the first run printed 25 hits, all F24/F29 own symbols or platform macros - review s R4):
# allowed - the F24/F29/B24 knobs and their Fix* symbols, the stand knob, the non-knob macros KYTY_PLATFORM*,
# KYTY_CLASS_NO_COPY and the include guard of joyPump.h; anything else naming KYTY_* or Fix* is a FAIL.
allow = re.compile(r'KYTY_(FIX_F24|FIX_F29|TEST_HIDLOSS|FIX_B24|PLATFORM\w*|CLASS_NO_COPY|GRAPHICS_PRESENTATION_WINDOW_JOY_PUMP_H_)|Fix(F24|F29|B24)\w*')
other_re = re.compile(r'KYTY_[A-Z0-9_]+|\bFix[A-Z][0-9A-Za-z]*')
fx = {'+\tif (FixF25Enabled()) {': False, '+getenv("KYTY_FIX_B24X")': False, '+KYTY_S_REPLAY': False,
      '+bool FixF29Enabled() {': True, '+#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS': True, '+FixB24On()': True}
check('R4 filter fixtures (3 rejected, 3 allowed)', all(all(allow.fullmatch(m.group(0)) for m in other_re.finditer(l)) == v
                                                     for l, v in fx.items()))
bad, b24 = [], []
for p in sorted(changed):
    for l in git('diff', '-U0', BASE, FS14, '--', p).splitlines():
        if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---'):
            names_ = [m.group(0) for m in other_re.finditer(l)]
            if any(not allow.fullmatch(n) for n in names_):
                bad.append((p, l.strip()[:160]))
            if 'B24' in l or 'PadOutput' in l:
                b24.append((p, l.strip()[:200]))
check('R4 changed lines naming a knob/Fix symbol outside F24/F29/B24/stand/platform macros: 0', not bad, str(len(bad)))
for b in bad:
    print('    ', b)
print('R4 changed lines naming B24 or PadOutput (eye):', len(b24))
for b in b24:
    print('    ', b)

# R5
check('R5 shader paths 0', [p for p in paths if p.startswith('src/graphics/shader/')] == [])
sig = ver = None
for p in glob.glob('C:/kyty/f287/fs14b/build/**/kytyGitVersion.h', recursive=True):
    t = open(p, encoding='utf-8', errors='replace').read()
    m = re.search(r'KYTY_SHADER_SOURCE_HASH\s+"([0-9a-f]+)"', t)
    if m:
        sig = m.group(1)
    m = re.search(r'"(KytyPS5-[^"]+)"', t)
    if m:
        ver = m.group(1)
check('R5 signature of own build == 9177b426...', sig == '9177b4267de1fb8bac7d1113afd8733210addfac', str(sig))
check('R5 version string ends with -geb7e8b91', bool(ver) and ver.endswith('-geb7e8b91'), str(ver))

# R6
for w in ('76c1058f', 'eb7e8b91'):
    d = git('diff', '-U0', w + '^', w, '--', 'src/').splitlines()
    code = [l for l in d if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---')
            and l[1:].strip() and not l[1:].strip().startswith('//')]
    print('R6 %s code lines:' % w)
    for l in code:
        print('    ', l)
    check('R6 %s changes only the knob reading (code lines <= 6, getenv of its knob)' % w,
          len(code) <= 6 and any('getenv("KYTY_FIX_F2' in l for l in code))
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
