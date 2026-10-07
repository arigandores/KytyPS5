# FS9b (HPP-672, Red Team, ROADMAP s122 item 604(d)(2)): own git checks of the FS9 source.
# Independent of the FS9a scripts (verify_fs9a.py, resolve_fs9a.py): the chain is rebuilt here in a temporary index
# (GIT_INDEX_FILE) from the base 0005e11f; the FS9a worktree is never touched. Output: review_git.out.txt (stdout).
import os
import re
import subprocess
import sys
import tempfile

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
WT = 'C:/kyty/f287/fs9a/wt'
BASE = '0005e11f'
HEAD = '11164d72'
F24A = '1570d110'
F24C = '21f8ca76'
FS9A = 'e4e5701a'
DIAG = '2cde5ef2'   # the only main commit in BASE..FS9A touching regionManager.h besides F24A/F24C/FS9A (git log)
RM = 'src/graphics/host_gpu/regionManager.h'
ok = True


def git(*a, cwd=REPO, env=None, inp=None, check=True):
    r = subprocess.run([G, *a], cwd=cwd, env=env, input=inp, capture_output=True)
    if check and r.returncode != 0:
        print('GIT FAIL', a, r.stderr.decode('utf-8', 'replace'))
        sys.exit(2)
    return r


def out(*a, **k):
    return git(*a, **k).stdout.decode('utf-8', 'replace').strip()


def say(name, cond, extra=''):
    global ok
    ok &= bool(cond)
    print('%-72s %s %s' % (name, 'OK' if cond else 'FAIL', extra))


print('== chain and worktree')
print(out('log', '--format=%h %p %s', '-4', HEAD).replace('\n', '\n    ')[:2000])
par = out('rev-list', '--parents', '-n', '3', HEAD).splitlines()
say('chain 11164d72 <- 21db93d1 <- 0107f69e <- 0005e11f',
    [p.split()[1][:8] for p in par] == ['21db93d1', '0107f69e', '0005e11f'], str([p[:17] for p in par]))
say('wt HEAD = 11164d72', out('rev-parse', 'HEAD', cwd=WT).startswith('11164d72'))
st = out('status', '--short', '--ignore-submodules=all', cwd=WT)
say('wt status --short empty', st == '', repr(st[:200]))
for c, src in (('0107f69e', F24A), ('21db93d1', F24C), ('11164d72', FS9A)):
    m = out('log', '-1', '--format=%B', c)
    say('%s message carries "cherry picked from commit %s"' % (c, src), ('cherry picked from commit ' + out('rev-parse', src)) in m)

print('== names BASE..HEAD')
names = out('diff', '--name-only', BASE, HEAD).splitlines()
for n in names:
    print('   ', n)
union = set()
for c in (F24A, F24C, FS9A):
    union |= set(out('show', '--format=', '--name-only', c).splitlines())
print('   union of the three commits:', sorted(union))
say('diff names = union of files of 1570d110, 21f8ca76, e4e5701a', set(names) == union)
say('no path under src/graphics/shader/', not any(n.startswith('src/graphics/shader/') for n in names))

print('== own rebuild in a temporary index')
tmp = tempfile.mkdtemp(prefix='fs9b_idx_')
env = dict(os.environ, GIT_INDEX_FILE=os.path.join(tmp, 'index'))
git('read-tree', BASE, env=env)


def apply(commit, exclude=None):
    args = ['format-patch', '-1', '--stdout', commit]
    p = git(*args).stdout
    if exclude:
        # drop the per-file blocks of excluded paths: diff -- with pathspec instead of format-patch
        files = [f for f in out('show', '--format=', '--name-only', commit).splitlines() if f not in exclude]
        p = git('diff', '--binary', commit + '^', commit, '--', *files).stdout
    r = git('apply', '--cached', '--whitespace=nowarn', '-', env=env, inp=p, check=False)
    return r.returncode, r.stderr.decode('utf-8', 'replace').strip()


rc, err = apply(F24A)
say('apply 1570d110 on 0005e11f cleanly', rc == 0, err[:300])
t1 = out('write-tree', env=env)
say('tree after 1570d110 = 0107f69e^{tree}', t1 == out('rev-parse', '0107f69e^{tree}'), t1[:12])

rc, err = apply(F24C)
print('   apply 21f8ca76 whole (expected to fail on regionManager.h context line):', rc, err[:300].replace('\n', ' | '))
say('21f8ca76 whole does not apply (the conflict FS9a names exists)', rc != 0)
rc, err = apply(F24C, exclude={RM})
say('apply 21f8ca76 without regionManager.h cleanly', rc == 0, err[:300])
rc, err = apply(FS9A, exclude={RM})
say('apply e4e5701a without regionManager.h cleanly', rc == 0, err[:300])

# regionManager.h: base file == main file before the diag commit?  then FS9 file must be
# main@FS9A minus the DIAG hunks of this file (reverse-apply DIAG's patch of the file on main's blob).
log_rm = out('log', '--format=%h', BASE + '..' + FS9A, '--', RM).splitlines()
print('   main commits touching regionManager.h in 0005e11f..e4e5701a:', log_rm)
say('they are exactly FS9A, F24C, F24A, DIAG', [x[:8] for x in log_rm] == [FS9A, F24C, F24A, DIAG])
say('regionManager.h: 0005e11f == 2cde5ef2^ (base = main before DIAG)',
    out('rev-parse', BASE + ':' + RM) == out('rev-parse', DIAG + '^:' + RM))
say('regionManager.h: 1570d110^ == 2cde5ef2 (F24A sits right on DIAG for this file)',
    out('rev-parse', F24A + '^:' + RM) == out('rev-parse', DIAG + ':' + RM))
main_blob = git('show', FS9A + ':' + RM).stdout
fs9 = git('show', HEAD + ':' + RM).stdout
# rule: the change main -> FS9 of this file is exactly the reverse of DIAG's change of it (line multisets, no other line)
dd = git('diff', DIAG + '^', DIAG, '--', RM).stdout.decode('utf-8', 'replace').splitlines()
dm = git('diff', FS9A, HEAD, '--', RM).stdout.decode('utf-8', 'replace').splitlines()
d_plus = sorted(l[1:] for l in dd if l.startswith('+') and not l.startswith('+++'))
d_minus = sorted(l[1:] for l in dd if l.startswith('-') and not l.startswith('---'))
m_plus = sorted(l[1:] for l in dm if l.startswith('+') and not l.startswith('+++'))
m_minus = sorted(l[1:] for l in dm if l.startswith('-') and not l.startswith('---'))
print('   2cde5ef2 on regionManager.h: +%d -%d; main->FS9: +%d -%d' % (len(d_plus), len(d_minus), len(m_plus), len(m_minus)))
say('regionManager.h main->FS9 removes exactly the lines 2cde5ef2 added, adds none', m_minus == d_plus and m_plus == d_minus == [])
# own file: delete those lines from main's blob in order (first match after the previous one) and compare
NL = chr(10)
lines = main_blob.decode('utf-8').split(NL)
todel = [l[1:] for l in dd if l.startswith('+') and not l.startswith('+++')]
k = 0
outl = []
for l in lines:
    if k < len(todel) and l == todel[k]:
        k += 1
        continue
    outl.append(l)
mine = NL.join(outl).encode('utf-8')
say('own regionManager.h (main with the 2cde5ef2 lines deleted in order) == 11164d72 byte for byte', k == len(todel) and mine == fs9,
    '%d / %d bytes, deleted %d of %d' % (len(mine), len(fs9), k, len(todel)))
blob = subprocess.run([G, 'hash-object', '-w', '--stdin'], cwd=REPO, input=mine, capture_output=True).stdout.decode().strip()
git('update-index', '--add', '--cacheinfo', '100644,%s,%s' % (blob, RM), env=env)
t3 = out('write-tree', env=env)
say('own tree (base + 1570d110 + 21f8ca76 + e4e5701a, file rule above) = 11164d72^{tree}',
    t3 == out('rev-parse', HEAD + '^{tree}'), t3[:12])
# negative control: same rebuild without FS9A must not equal
git('read-tree', '0107f69e', env=env)
apply(F24C, exclude={RM})
say('negative control: tree without e4e5701a != 11164d72^{tree}', out('write-tree', env=env) != out('rev-parse', HEAD + '^{tree}'))

print('== FS9 files vs main e4e5701a')
for n in names:
    d = git('diff', FS9A, HEAD, '--', n).stdout.decode('utf-8', 'replace')
    plus = [l for l in d.splitlines() if l.startswith('+') and not l.startswith('+++')]
    minus = [l for l in d.splitlines() if l.startswith('-') and not l.startswith('---')]
    # a removed line is a KYTY_DIAG_B32 line (names B32/b32) or a bare closer / blank inside such a block
    diagish = all(('B32' in l or 'b32' in l or 'run by docs/track-f/f20j' in l or l[1:].strip() in ('', ')', '}'))
                  for l in minus) and not plus
    print('   %-45s +%d -%d %s' % (n, len(plus), len(minus), 'only KYTY_DIAG_B32 lines removed' if diagish else ''))
    if minus or plus:
        say('  %s: FS9 = main minus KYTY_DIAG_B32 lines only' % n, diagish)
    else:
        say('  %s: FS9 = main' % n, True)


def code_lines(text):
    """Preprocess for the emulator build (KYTY_TEST_B13_HOOK / KYTY_TEST_B13_SWAP undefined), drop comments."""
    res, stack = [], []
    for raw in text.splitlines():
        l = raw.strip()
        m = re.match(r'#if defined\((KYTY_TEST_B13_\w+)\)', l)
        if m:
            stack.append(False)
            continue
        if l == '#else' and stack:
            stack[-1] = not stack[-1]
            continue
        if l == '#endif' and stack:
            stack.pop()
            continue
        if stack and not all(stack):
            continue
        l = re.sub(r'//.*', '', l).strip()
        if l:
            res.append(l)
    return res


def block(text, start_pat, nth=1):
    lines = text.splitlines()
    i = [k for k, l in enumerate(lines) if start_pat in l][nth - 1]
    depth, j = 0, i
    for j in range(i, len(lines)):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth == 0 and j > i:
            break
    return lines[i:j + 1]


print('== else branch (KYTY_FIX_B13=0) vs base, preprocessed for the emulator')
base_t = git('show', BASE + ':' + RM).stdout.decode()
fs9_t = fs9.decode()
bb = block(base_t, 'if constexpr (source == DirtySource::Cpu && enable) {', 2)
fb = block(fs9_t, 'if constexpr (source == DirtySource::Cpu && enable) {', 2)
fbt = '\n'.join(fb)
i_if = next(k for k, l in enumerate(fb) if 'if (FixB13Enabled()) {' in l)
i_else = next(k for k, l in enumerate(fb) if l.strip() == '} else {' and k > i_if)
on_branch = fb[i_if + 1:i_else]
else_branch = fb[i_else + 1:-2]
base_body = bb[1:-1]
cb, ce = code_lines('\n'.join(base_body)), code_lines('\n'.join(else_branch))
for a in ce:
    print('   else|', a)
say('else branch code (emulator preprocessing, no comments) == base block code', cb == ce, '%d / %d lines' % (len(cb), len(ce)))
# comment lines of base that are absent in the else branch
cm_b = [l.strip() for l in base_body if l.strip().startswith('//')]
cm_e = [l.strip() for l in else_branch if l.strip().startswith('//')]
miss = [c for c in cm_b if c not in cm_e]
print('   base comment lines missing in else (F24c changed the first one into "Called with the region lock held..." on its own line):', miss)
say('every base comment line present in else except the merged first line', len(miss) <= 1)
# negative control: the =1 branch must not equal the base code
con = code_lines('\n'.join(on_branch))
say('negative control: =1 branch code != base code', con != cb)
print('   =1 branch code:', con)
# =1 branch = F24c =1 branch
f24c_t = git('show', F24C + ':' + RM).stdout.decode()
f24b = block(f24c_t, 'if constexpr (source == DirtySource::Cpu && enable) {', 2)
say('whole ChangeState<Cpu,true> epoch block of FS9 == block of 21f8ca76 (text)', f24b == fb)
# reader of the knob
fn9 = block(fs9_t, 'inline bool FixB13Enabled() noexcept {')
fn_main = block(git('show', FS9A + ':' + RM).stdout.decode(), 'inline bool FixB13Enabled() noexcept {')
say('FixB13Enabled of FS9 == main e4e5701a', fn9 == fn_main)
print('\n'.join('   ' + l for l in fn9))
uses = out('grep', '-n', '-e', 'KYTY_FIX_B13"', '-e', 'FixB13Enabled()', HEAD, '--', 'src', 'tests').splitlines()
for u in uses:
    print('   use:', u[:160])
raw = [u for u in uses if 'getenv' in u or 'EnvValueOn' in u or 'EnvFlagOn' in u]
say('one raw read of KYTY_FIX_B13 in src/ and tests/ (inside FixB13Enabled)', len(raw) == 1 and RM in raw[0], str(raw))

print('== untouched fixes: their commits are ancestors of the base or patch-equal in it')
anc = ['4414e235', 'd515b901', '3d0e46da', '0e72bc19', '4d9e8ab7', '3904522d', 'd6ee2dc8', '302347b4']
for a in anc:
    r = git('merge-base', '--is-ancestor', a, BASE, check=False)
    say('  %s ancestor of 0005e11f' % a, r.returncode == 0)
cher = {'1833ee28': 'F10', 'c3eb8fe8': 'F10 FS5a', '68602c4f': 'F16', '17adaf80': 'F16 FS4a', '4e72289e': 'B42',
        'c1732d1a': 'B33 S12a', 'a86a5ad0': 'B4', '17eb924e': 'B4', '10a4800b': 'F8', 'ec6c4c83': 'F8 FS7a',
        '9c726d74': 'B24', '919c1a19': 'B24', '082d1612': 'F19', 'f98e842c': 'F19', 'e46f55d4': 'F19 FS8a',
        '7719d0f2': 'F19 tests'}
for c, nm in cher.items():
    r = out('cherry', HEAD, c, c + '^')
    say('  git cherry %s (%s) = "-"' % (c, nm), r.startswith('-'), r[:20])
# S-replay / S18a2 is the base itself; P-var is 4414e235 (ancestor above)
fixfiles = out('diff', '--name-only', BASE, HEAD, '--', 'src').splitlines()
say('src/ files of the diff only memoryTracker.cpp and regionManager.h', sorted(fixfiles) == [
    'src/graphics/host_gpu/memoryTracker.cpp', RM], str(fixfiles))

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
