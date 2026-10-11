# FS15b (HPP-821, Red Team, ROADMAP s122 items 730(g)(2), 732): git members of the FS15 review, own code (new file; the form
# of my review_git_fs14b.py).
# Own clean worktree C:/kyty/f287/fs15b/wt (HEAD 6beb3b73 = FS15). Base FS14 eb7e8b91. F42a2 tag worktree 5ccb1d31 (on FS12
# 730ed40a: 23ff0c41 <- a6342c98, adcd0eba <- a9d6fd1c, 5ccb1d31 <- 82570fd2).
# Worktree commits (cherry-pick -x): b1179dab <- a6342c98 (F20 code), 95e39a17 <- a9d6fd1c (stand ed. 1),
# 91b74d09 <- 82570fd2 (CreateCachedModule out of the anonymous namespace, getters, stand ed. 2), 6beb3b73 <- 38fc76c1 (FS15a).
# R1  diff FS15 vs base FS14: src/ = the six files of a6342c98 / 82570fd2 / 38fc76c1; outside src/ only the two test files of
#     a9d6fd1c / 82570fd2 (CMakeLists.txt untouched); chain parents exact; patch-id of each = its main original.
# R2  src/ FS15 vs F42a2 worktree 5ccb1d31: paths = src paths of FS12 -> FS14 (730ed40a..eb7e8b91, the FS13 and FS14 commits)
#     + fixF20.cpp/.h; per FS13/FS14 path the diff = diff 730ed40a -> eb7e8b91; fixF20 diff = 38fc76c1; every other src blob
#     equal; F42a2 chain patch-ids = originals (the F42a2 tag code = the F42 code of FS15).
# R3  "contains": ancestor or git cherry '-' for the 15 commits of item 730(g)(1); controls.
# R4  untouched rows: every src file of the base naming the knob of F24 F29 F25 F21 B12 F27(B36) B13 B33(S_PCW) F10 F16(SVAL)
#     F19 B42 B4 F8 B24 S-replay P-var has the same blob in FS15 except the F42 files; in the F42 files every -/+ line of
#     base..FS15 names no other knob / Fix symbol (filter with fixtures); faultManager.cpp/.h (F29 ParseFaultArea) same blob.
# R5  src/graphics/shader/** 0; KYTY_SHADER_SOURCE_HASH of own build = 9177b426...; version ends -g6beb3b73; own
#     kytyGitVersion.h signature = the FS15a copy.
# R6  38fc76c1 changes only the knob reading (code lines printed).
# R7  =0 by code: every FixF20::Apply call outside fixF20.* is guarded by 'FixF20::Mode() == 1 &&' in the same expression;
#     PrintStat("exit") only under 'if (Mode() == 1)'; PrintStat("periodic") only inside Apply.
import glob, re, subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/f287/fs15b/wt'
FS15, BASE, F42A2, FS12 = '6beb3b73', 'eb7e8b91', '5ccb1d31', '730ed40a'
CHAIN = [('b1179dab', 'a6342c98'), ('95e39a17', 'a9d6fd1c'), ('91b74d09', '82570fd2'), ('6beb3b73', '38fc76c1')]
CHAIN42 = [('23ff0c41', 'a6342c98'), ('adcd0eba', 'a9d6fd1c'), ('5ccb1d31', '82570fd2')]
PIPE = 'src/graphics/host_gpu/renderer/pipeline/'
FIXF20 = {PIPE + 'fixF20.cpp', PIPE + 'fixF20.h'}
F42_SRC = {'src/emulator.cpp', PIPE + 'pipelineCache.cpp', PIPE + 'pipelineCache.h', PIPE + 'shaders.cpp'} | FIXF20
TESTS = ['tests/ShaderRecompilerComputeTests.cpp', 'tests/shaderCfgTests.cpp']
FM = {'src/graphics/host_gpu/renderer/cache/faultManager.cpp', 'src/graphics/host_gpu/renderer/cache/faultManager.h'}
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
    s = git('show', c)
    return git('patch-id', '--stable', inp=s.encode('utf-8')).split()[0] if s else ''


# R1
paths = git('diff', '--name-only', BASE, FS15).split()
src = sorted(p for p in paths if p.startswith('src/'))
print('R1 paths', len(paths), 'src', src)
check('R1 src/ == six files of a6342c98/82570fd2/38fc76c1', set(src) == F42_SRC)
union = set()
for _, m in CHAIN:
    union |= set(git('show', '--name-only', '--format=', m).split())
check('R1 src/ == src paths of the four main commits', set(src) == {p for p in union if p.startswith('src/')})
other = sorted(p for p in paths if not p.startswith('src/'))
check('R1 outside src/: only the two test files', other == sorted(TESTS), str(other))
par = BASE
for w, m in CHAIN:
    p = git('rev-parse', w + '^').strip()[:8]
    check('R1 chain %s parent %s' % (w, par), p == par[:8], p)
    pw, pm = pid(w), pid(m)
    check('R1 patch-id %s == %s (main)' % (w, m), pw and pw == pm, pw[:12])
    par = w
check('R1 FS15 tip == 6beb3b73', git('rev-parse', 'HEAD').strip()[:8] == FS15)

# R2
par = FS12
for w, m in CHAIN42:
    p = git('rev-parse', w + '^').strip()[:8]
    check('R2 F42a2 chain %s parent %s' % (w, par), p == par[:8], p)
    pw, pm = pid(w), pid(m)
    check('R2 F42a2 patch-id %s == %s (main)' % (w, m), pw and pw == pm, pw[:12])
    par = w
fs1314 = sorted(git('diff', '--name-only', FS12, BASE, '--', 'src/').split())
print('R2 src paths FS12 -> FS14 (FS13 + FS14 commits):', fs1314)
print('R2 commits FS12 .. FS14:')
for l in git('log', '--format=%h %s', FS12 + '..' + BASE).splitlines():
    print('    ', l[:150])
check('R2 FS13/FS14 src paths do not touch F42 files', not (set(fs1314) & F42_SRC))
p2 = sorted(git('diff', '--name-only', F42A2, FS15, '--', 'src/').split())
print('R2 src paths F42a2 wt -> FS15', p2)
check('R2 paths == FS13/FS14 src paths + fixF20.cpp/.h', set(p2) == set(fs1314) | FIXF20)
for p in fs1314:
    d = git('diff', F42A2, FS15, '--', p)
    check('R2 %s diff == FS12 -> FS14 diff' % p, d != '' and d == git('diff', FS12, BASE, '--', p))
d = git('diff', F42A2, FS15, '--', *sorted(FIXF20))
check('R2 fixF20 diff == 91b74d09 -> 6beb3b73', d != '' and d == git('diff', '91b74d09', FS15, '--', *sorted(FIXF20)))
check('R2 fixF20 diff == main 38fc76c1', d == git('diff', '38fc76c1^', '38fc76c1', '--', *sorted(FIXF20)))
for p in sorted(F42_SRC - FIXF20):
    check('R2 %s blob F42a2 wt == FS15' % p, blob(F42A2, p) == blob(FS15, p))
check('R2 F42 files of F42a2 wt == 91b74d09 (FS15 without FS15a)', all(blob(F42A2, p) == blob('91b74d09', p) for p in F42_SRC))
check('R2 negative: diff src/ base FS14 -> FS15 != diff F42a2 wt -> FS15', git('diff', BASE, FS15, '--', 'src/') != git('diff', F42A2, FS15, '--', 'src/'))


# R3
def contains(tip, c):
    if subprocess.run([G, '-C', WT, 'merge-base', '--is-ancestor', c, tip]).returncode == 0:
        return 'ancestor'
    out = git('cherry', tip, c, c + '^').split()
    return 'cherry ' + (' '.join(out[0::2]) if out else '?')


need = ['a6342c98', '82570fd2', '38fc76c1', '5c21c387', '57f9e528', 'c8836f14', '15c9d2f2', '78e45af3', 'e9dd8604',
        '3630f116', '227e1b36', 'cbfe8375', 'c94c49e0', '726e751e', 'cb022252']
for c in need:
    r = contains(FS15, c)
    check('R3 FS15 contains ' + c, r in ('ancestor', 'cherry -'), r)
for tip, c, yes in [(BASE, 'a6342c98', False), (BASE, '82570fd2', False), (BASE, '38fc76c1', False), ('91b74d09', '38fc76c1', False),
                    (FS15, '1398d44d', False), (F42A2, '5c21c387', False), (F42A2, '38fc76c1', False), (FS15, 'a9d6fd1c', True)]:
    r = contains(tip, c)
    check('R3 control %s in %s expect %s' % (c, tip, 'yes' if yes else 'no'), (r in ('ancestor', 'cherry -')) == yes, r)

# R4
knobs = {'F24': ['KYTY_FIX_F24'], 'F29': ['KYTY_FIX_F29'], 'F25': ['KYTY_FIX_F25'], 'F21': ['KYTY_FIX_F21'],
         'B12': ['KYTY_FIX_B12'], 'F27': ['KYTY_FIX_B36'], 'B13': ['KYTY_FIX_B13'], 'B33': ['KYTY_S_PCW'],
         'F10': ['KYTY_FIX_F10'], 'F16': ['KYTY_FIX_SVAL'], 'F19': ['KYTY_FIX_F19'], 'B42': ['KYTY_FIX_B42'],
         'B4': ['KYTY_FIX_B4'], 'F8': ['KYTY_FIX_F8'], 'B24': ['KYTY_FIX_B24'], 'S-replay': ['KYTY_S_REPLAY'],
         'P-var': ['KYTY_PVAR', 'KYTY_GAME_PATCH']}
for row, names in knobs.items():
    files = set()
    for n in names:
        files |= set(git('grep', '-l', n, BASE, '--', 'src/').replace(BASE + ':', '').split())
    diff = sorted(f for f in files if blob(BASE, f) != blob(FS15, f))
    check('R4 %s files %d' % (row, len(files)), len(files) > 0 and set(diff) <= F42_SRC, 'differ ' + str(diff))
check('R4 F29 faultManager.cpp/.h (ParseFaultArea) same blob as FS14', all(blob(BASE, p) == blob(FS15, p) for p in FM))
# Filter: allowed - the F20 knob and its Fix symbols, the stand/test knobs of F20, the include guard of fixF20.h, and two
# existing non-fix knobs named in comments of the F42 code (KYTY_DMA_LAYOUT, KYTY_PIPELINE_SALT - printed for the eye);
# anything else naming KYTY_* or Fix<X> on a -/+ line of the F42 files is a FAIL.
allow = re.compile(r'KYTY_(FIX_F20|TEST_F20\w*|RECOMPILE_F20|GRAPHICS_HOST_GPU_RENDERER_PIPELINE_FIX_F20_H_|DMA_LAYOUT|PIPELINE_SALT)|Fix(F20)\w*')
other_re = re.compile(r'KYTY_[A-Z0-9_]+|\bFix[A-Z][0-9A-Za-z]*')
fx = {'+\tif (FixF25Enabled()) {': False, '+getenv("KYTY_FIX_F24")': False, '+KYTY_S_REPLAY': False,
      '+int FixF20::Mode() {': True, '+// KYTY_DMA_LAYOUT=1 adds': True, '+getenv("KYTY_FIX_F20")': True}
check('R4 filter fixtures (3 rejected, 3 allowed)', all(all(allow.fullmatch(m.group(0)) for m in other_re.finditer(l)) == v
                                                     for l, v in fx.items()))
bad, eye = [], []
for p in sorted(F42_SRC):
    for l in git('diff', '-U0', BASE, FS15, '--', p).splitlines():
        if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---'):
            names_ = [m.group(0) for m in other_re.finditer(l)]
            if any(not allow.fullmatch(n) for n in names_):
                bad.append((p, l.strip()[:160]))
            if any(n in ('KYTY_DMA_LAYOUT', 'KYTY_PIPELINE_SALT') for n in names_):
                eye.append((p, l.strip()[:200]))
check('R4 changed lines of F42 files naming another knob/Fix symbol: 0', not bad, str(len(bad)))
for b in bad:
    print('    ', b)
print('R4 changed lines naming KYTY_DMA_LAYOUT / KYTY_PIPELINE_SALT (eye: comments only):', len(eye))
for b in eye:
    print('    ', b)
check('R4 those lines are comments', all(l.lstrip('+-').strip().startswith('//') for _, l in eye))

# R5
check('R5 shader paths 0', [p for p in paths if p.startswith('src/graphics/shader/')] == [])
sig = ver = None
for p in glob.glob('C:/kyty/f287/fs15b/build/**/kytyGitVersion.h', recursive=True):
    t = open(p, encoding='utf-8', errors='replace').read()
    m = re.search(r'KYTY_SHADER_SOURCE_HASH\s+"([0-9a-f]+)"', t)
    if m:
        sig = m.group(1)
    m = re.search(r'"(KytyPS5-[^"]+)"', t)
    if m:
        ver = m.group(1)
check('R5 signature of own build == 9177b426...', sig == '9177b4267de1fb8bac7d1113afd8733210addfac', str(sig))
check('R5 version string ends with -g6beb3b73', bool(ver) and ver.endswith('-g6beb3b73'), str(ver))
t = open('C:/kyty/KytyPS5/docs/track-f/fs15a/kytyGitVersion_fs15.h', encoding='utf-8', errors='replace').read()
m = re.search(r'KYTY_SHADER_SOURCE_HASH\s+"([0-9a-f]+)"', t)
check('R5 own signature == FS15a kytyGitVersion_fs15.h', bool(m) and m.group(1) == sig, m.group(1) if m else 'none')

# R6
d = git('diff', '-U0', '38fc76c1^', '38fc76c1', '--', 'src/').splitlines()
code = [l for l in d if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---')
        and l[1:].strip() and not l[1:].strip().startswith('//')]
print('R6 38fc76c1 code lines:')
for l in code:
    print('    ', l)
check('R6 38fc76c1 changes only the knob reading (code lines <= 6, getenv of KYTY_FIX_F20)',
      len(code) <= 6 and any('getenv("KYTY_FIX_F20")' in l for l in code))

# R7
calls = []
for h in git('grep', '-n', 'FixF20::Apply(', FS15, '--', 'src/').splitlines():
    _, path, ln, text = h.split(':', 3)
    if path in FIXF20:
        continue
    calls.append((path, ln, text.strip()))
for c in calls:
    print('R7 Apply call', c[0] + ':' + c[1], c[2][:150])
check('R7 Apply calls outside fixF20: 2, each guarded by FixF20::Mode() == 1 &&', len(calls) == 2 and
      all('FixF20::Mode() == 1 && FixF20::Apply(' in c[2] for c in calls))
cpp = git('show', FS15 + ':' + PIPE + 'fixF20.cpp')
m = re.search(r'void PrintExitStat\(\) \{\s*if \(Mode\(\) == 1\) \{\s*PrintStat\("exit"\);\s*\}\s*\}', cpp)
check('R7 PrintExitStat prints only under Mode() == 1', bool(m))
check('R7 PrintStat call sites: exit (guarded) + periodic (inside Apply) only', cpp.count('PrintStat(') == 3)
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
