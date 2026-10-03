# F11e (HPP-467, Red Team): own checks without the GPU - sha256 of the F11d binaries, strings of the copy, git window M3',
# SPIR-V dump at =0 / unset / =1 against the build without the code (KYTY_BVH_NATIVE 0 and 1). Each step checks the lock.
import hashlib, os, subprocess, sys, glob
NL = chr(10)
OUT = 'C:/kyty/f287/f11e/own'
LOCK = 'C:/kyty/SEALED_RUN.lock'
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
log = []


def P(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    log.append(s)


def save():
    open(OUT + '/own_f11e.out.txt', 'w', encoding='utf-8', newline='').write(NL.join(log) + NL)


def lock():
    if os.path.exists(LOCK) or os.path.exists('C:/kyty/f287/STOP'):
        P('ABORT: lock or STOP appeared')
        save()
        sys.exit(3)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def git(*a, cwd=REPO):
    r = subprocess.run([GIT, '-C', cwd] + list(a), capture_output=True, timeout=30)
    return r.returncode, r.stdout.decode('utf-8', 'replace').strip()


def gitrc(*a):
    return subprocess.run([GIT, '-C', REPO] + list(a), capture_output=True, timeout=30).returncode


os.makedirs(OUT, exist_ok=True)
files = [('copy', 'C:/kyty/f287/bin/kyty_emulator_b97efad4.exe'),
         ('install', 'C:/kyty/f287/f11d/build/install/kyty_emulator.exe'),
         ('build_exe', 'C:/kyty/f287/f11d/build/kyty_emulator.exe'),
         ('tests_diag', 'C:/kyty/f287/f11d/build/shader_recompiler_compute_tests.exe'),
         ('tests_base', 'C:/kyty/f287/f11d/tests_base.exe'),
         ('installed', 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe')]
for k, p in files:
    P('sha256', k, sha(p) if os.path.exists(p) else 'MISSING', p)
data = open(files[0][1], 'rb').read()
for s in [b'c01451b0', b'23f2e9d0a210e47e1f500eba542cd9c2b2c4795d', b'56189185f9e9f9a0ea5174f3f85206e6d099db3d',
          b':diagbvh', b'DiagBvhNodes: mode=1', b'KYTY_DIAG_BVHNODES']:
    P('copy contains', s.decode(), data.count(s))
lock()
P('git parent c01451b0', git('rev-parse', 'c01451b0^'))
P('git parent befeb824', git('rev-parse', 'befeb824^'))
P('git times', git('show', '-s', '--format=%H %cI', 'c01451b0', 'befeb824'))
rc, fp = git('rev-list', '--first-parent', '--reverse', 'eecd671c..HEAD')
L = fp.split(NL)
P('first-parent after eecd671c: n', len(L), 'pos c01451b0', [i for i, x in enumerate(L) if x.startswith('c01451b0')],
  'pos befeb824', [i for i, x in enumerate(L) if x.startswith('befeb824')])
P('git diff --quiet eecd671c befeb824 (whole tree) rc', gitrc('diff', '--quiet', 'eecd671c', 'befeb824'))
sigset = ['src/graphics/shader', 'src/generate_version.cmake',
          'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
          'src/graphics/guest_gpu/gpu_format.h', 'src/graphics/guest_gpu/gpu_defs.h']
P('git diff --quiet eecd671c befeb824 -- sigset rc', gitrc('diff', '--quiet', 'eecd671c', 'befeb824', '--', *sigset))
P('git diff --quiet befeb824 HEAD -- src tests rc', gitrc('diff', '--quiet', 'befeb824', 'HEAD', '--', 'src', 'tests'))
P('git diff --shortstat eecd671c c01451b0', git('diff', '--shortstat', 'eecd671c', 'c01451b0'))
P('git diff --name-only b0a18f9d eecd671c -- src', git('diff', '--name-only', 'b0a18f9d', 'eecd671c', '--', 'src'))
P('git diff --name-only b0a18f9d eecd671c -- tests', git('diff', '--name-only', 'b0a18f9d', 'eecd671c', '--', 'tests'))
for anc in ['4e72289e', '68602c4f', '17adaf80']:
    P('ancestor', anc, 'of c01451b0 rc', gitrc('merge-base', '--is-ancestor', anc, 'c01451b0'))
WT = 'C:/kyty/f287/f11d/wt'
P('wt HEAD', git('rev-parse', 'HEAD', cwd=WT))
rc, st = git('status', '--porcelain', '--ignore-submodules=all', cwd=WT)
P('wt status lines', 0 if not st else len(st.split(NL)))
lock()


def run(exe, env_over, tag):
    lock()
    d = OUT + '/spv_' + tag
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(d + '/*.spv'):
        os.remove(f)
    env = dict(os.environ)
    for k in ['KYTY_DIAG_BVHNODES', 'KYTY_BVH_NATIVE', 'KYTY_TEST_LOG_CONSOLE']:
        env.pop(k, None)
    env.update(env_over)
    env['KYTY_TEST_LOG_CONSOLE'] = '1'
    r = subprocess.run([exe, '--diag-dump-spirv', d], env=env, cwd=OUT, capture_output=True, timeout=40)
    txt = (r.stdout + r.stderr).decode('utf-8', 'replace')
    open(OUT + '/dump_' + tag + '.txt', 'w', encoding='utf-8', newline='').write(txt)
    n = sum(1 for line in txt.split(NL) if 'DiagBvhNodes:' in line)
    m = {os.path.basename(f): sha(f) for f in sorted(glob.glob(d + '/*.spv'))}
    P('run', tag, 'rc', r.returncode, 'ALL_OK', 'ALL OK' in txt, 'files', len(m), 'DiagBvhNodes_lines', n)
    return m


res = {}
for nat in ['0', '1']:
    res['base_nat' + nat] = run(files[4][1], {'KYTY_BVH_NATIVE': nat}, 'base_nat' + nat)
    res['unset_nat' + nat] = run(files[3][1], {'KYTY_BVH_NATIVE': nat}, 'diagunset_nat' + nat)
    res['d0_nat' + nat] = run(files[3][1], {'KYTY_BVH_NATIVE': nat, 'KYTY_DIAG_BVHNODES': '0'}, 'diag0_nat' + nat)
    res['d1_nat' + nat] = run(files[3][1], {'KYTY_BVH_NATIVE': nat, 'KYTY_DIAG_BVHNODES': '1'}, 'diag1_nat' + nat)
ok = True
for nat in ['0', '1']:
    b = res['base_nat' + nat]
    for k in ['unset', 'd0']:
        eq = sum(1 for f in b if res[k + '_nat' + nat].get(f) == b[f])
        P('nat', nat, k, 'equal to base', eq, 'of', len(b))
        ok &= eq == len(b) == 7
    ne = sum(1 for f in b if res['d1_nat' + nat].get(f) != b[f])
    P('nat', nat, 'd1 differs from base', ne, 'of', len(b))
    ok &= ne == len(b) == 7
    ref = {}
    for line in open(REPO + '/docs/track-f/f11d/spv_base_nat' + nat + '.sha256', encoding='utf-8'):
        if line.strip():
            h, f = line.split()
            ref[f.lstrip('*')] = h
    eqr = sum(1 for f in b if ref.get(f) == b[f])
    P('nat', nat, 'own base = F11d spv_base', eqr, 'of', len(b))
    ok &= eqr == 7
P('SPIRV0 ' + ('ALL OK' if ok else 'FAILED'))
save()
