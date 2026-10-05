# FS7a (HPP-565, ROADMAP s122 items 467(g)(1), 487(g)(1)): mechanical members of the shipping binary FS7 after the build -
# sha256 of build/ and install/ exe, version and translation signature from build/kytyGitVersion.h, strings in the exe,
# file set of the source diff against the base FS6a 3904522d (= union of the files of the four commits), patch-id of each
# cherry-pick against its original, "binary contains" by item 380(b) (git cherry -v <wt HEAD> <c> <c>^), ancestors.
# Writes files_expected.txt, files_actual.txt, diffstat_vs_3904522d.txt, fs7a_vs_3904522d.diff, fs7a_vs_b47033cb.diff,
# cherry.out.txt, kytyGitVersion_fs7.h, verify_fs7a.out.txt. LF output. Last line ALL OK or FAILED <n>.
import hashlib, os, re, shutil, subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
D = 'C:/kyty/f287/fs7a'
BASE = '3904522d'
SIG = '26ce5fc78ea3b20be537c7696be041f5e97d9e58'
CODE = 'ec6c4c83'
PICKS = ['10a4800b', '9c726d74', '919c1a19', CODE]
CONTAINS = ['10a4800b', '9c726d74', '919c1a19', CODE, 'a86a5ad0', '17eb924e']
OTHER = ['4e72289e', '68602c4f', '17adaf80', '1833ee28', 'c3eb8fe8', 'c1732d1a',
         '082d1612', 'f98e842c', 'fcaf141b', '741e3312', 'c9b4268e', '365cc3c2']
NL = chr(10)
out = []
nbad = 0


def w(s):
    out.append(s)
    print(s)


def check(name, ok, detail=''):
    global nbad
    nbad += 0 if ok else 1
    w('%s %s %s' % ('PASS' if ok else 'FAIL', name, detail))


def git(*a, cwd=REPO, inp=None):
    p = subprocess.run([G, '-C', cwd, *a], capture_output=True, input=inp)
    if p.returncode != 0:
        raise SystemExit('git %s: %s' % (' '.join(a), p.stderr.decode('utf-8', 'replace')))
    return p.stdout


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def save(name, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    open(os.path.join(D, name), 'wb').write(data.replace(b'\r\n', b'\n'))


head = git('rev-parse', 'HEAD', cwd=D + '/wt').decode().strip()
w('# wt HEAD ' + head)
check('wt clean', git('status', '--short', cwd=D + '/wt').strip() == b'')

# 1. binary
e1, e2 = D + '/build/kyty_emulator.exe', D + '/build/install/kyty_emulator.exe'
s1, s2 = sha(e1), sha(e2)
check('build exe = install exe', s1 == s2, s2)
copy = 'C:/kyty/f287/bin/kyty_emulator_%s.exe' % s2[:8]
if not os.path.exists(copy):
    shutil.copy2(e2, copy)
check('pinned copy sha', sha(copy) == s2, copy)
inst = 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'
w('installed (not touched) sha256 ' + sha(inst))

# 2. version header and signature
vh = open(D + '/build/kytyGitVersion.h', 'rb').read()
save('kytyGitVersion_fs7.h', vh)
vt = vh.decode('utf-8', 'replace')
for line in vt.replace('\r\n', NL).split(NL):
    if '#define' in line:
        w('   ' + line.strip())
m = re.search(r'KYTY_SHADER_SOURCE_HASH\s+"([0-9a-f]+)"', vt)
check('signature = 26ce5fc7 (base)', bool(m) and m.group(1) == SIG, m.group(1) if m else 'none')
m2 = re.search(r'KYTY_GIT_REVISION\s+"([0-9a-f]+)"', vt)
check('KYTY_GIT_REVISION = wt HEAD', bool(m2) and head.startswith(m2.group(1)[:7]), m2.group(1) if m2 else 'none')
exe = open(e2, 'rb').read()
check('signature in exe once', exe.count(SIG.encode()) == 1, str(exe.count(SIG.encode())))
for s in ['FixF8: mode=', 'FixB24: mode=', 'FixB4: mode=', 'KYTY_FIX_F8', 'KYTY_FIX_B24', 'KYTY_FIX_F19', 'KYTY_PVAR_HOLD',
          'KYTY_DIAG_F5', 'KYTY_FIX_F26', 'KYTY_FIX_F5CMU']:
    w('   exe count %-18s %d' % (s, exe.count(s.encode())))
check('exe has FixF8 and FixB24 lines', exe.count(b'FixF8: mode=') == 1 and exe.count(b'FixB24: mode=') == 1)
check('exe has no F19/PVAR_HOLD/DIAG_F5/F26/F5CMU', all(exe.count(s) == 0 for s in
      [b'KYTY_FIX_F19', b'KYTY_PVAR_HOLD', b'KYTY_DIAG_F5', b'KYTY_FIX_F26', b'KYTY_FIX_F5CMU']))

# 3. files of the diff against the base = union of the four commits
exp = set()
for c in PICKS:
    exp |= set(git('diff-tree', '--no-commit-id', '--name-only', '-r', c).decode().split())
act = set(git('diff', '--name-only', BASE, head).decode().split())
save('files_expected.txt', NL.join(sorted(exp)) + NL)
save('files_actual.txt', NL.join(sorted(act)) + NL)
check('diff files vs %s = union of %s' % (BASE, ' '.join(PICKS)), exp == act,
      'expected %d actual %d; extra %s missing %s' % (len(exp), len(act), sorted(act - exp), sorted(exp - act)))
save('diffstat_vs_3904522d.txt', git('diff', '--stat=200', BASE, head))
save('fs7a_vs_3904522d.diff', git('diff', BASE, head))
parent = git('rev-parse', head + '^').decode().strip()
save('fs7a_vs_%s.diff' % parent[:8], git('diff', parent, head))
w('   parent of wt HEAD ' + parent)


# 4. patch-id of each pick in the wt chain = its original
def pid(c):
    d = git('show', c)
    return git('patch-id', '--stable', inp=d).decode().split()[0] if d else ''


chain = git('rev-list', '--reverse', BASE + '..' + head).decode().split()
check('wt chain length 4', len(chain) == 4, ' '.join(x[:8] for x in chain))
for orig, new in zip(PICKS, chain):
    a, b = pid(orig), pid(new)
    check('patch-id %s = %s' % (orig, new[:8]), a == b, a[:8])

# 5. contains (item 380(b)) and ancestors
lines = []
for c in CONTAINS + OTHER:
    r = git('cherry', '-v', head, c, c + '^').decode().strip()
    lines.append(c + ' ' + r)
save('cherry.out.txt', NL.join(lines) + NL)
for c, l in zip(CONTAINS + OTHER, lines):
    w('   cherry ' + l[:130])
for c, l in zip(CONTAINS, lines):
    check('contains %s' % c, l.split()[1] == '-')
for anc in ['3904522d', '4d9e8ab7', '0e72bc19', '3d0e46da', '4414e235']:
    r = subprocess.run([G, '-C', REPO, 'merge-base', '--is-ancestor', anc, head]).returncode
    check('ancestor %s' % anc, r == 0)

w('ALL OK' if nbad == 0 else 'FAILED %d' % nbad)
save('verify_fs7a.out.txt', NL.join(out) + NL)
sys.exit(0 if nbad == 0 else 1)
