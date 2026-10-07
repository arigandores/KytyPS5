# F25l2 (HPP-683, Red Team): the F25k2 tests t1-t5 rerun by Red Team on its own build of the T2 source (0c8fcba2, worktree
# C:/kyty/f287/f25l/wt, build C:/kyty/f287/f25l/build, executables copied to C:/kyty/f287/f25l2/bin) into its own folder,
# plus the probe f25l2_probe (stand0_two on T2 and others). t1b reference: the F25k reference executable (code before F25k).
# t4 reference: FS8a fu (as F25k2). Rule 27: lock and STOP before every process.
import hashlib, os, re, subprocess, sys
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
BIN = 'C:/kyty/f287/f25l2/bin'
BUILD = 'C:/kyty/f287/f25l/build'
OUT = 'C:/kyty/f287/f25l2/tests_mine'
REFEXE = 'C:/kyty/f287/f25k/ref/log_async_tests_ref.exe'
REF = 'C:/kyty/f287/fs8a/suite/fu'


def guard():
    if os.path.exists(LOCK):
        print('HALT lock'); sys.exit(5)
    if os.path.exists(STOP):
        print('HALT stop'); sys.exit(4)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def clean_env():
    return {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}


ok = True
os.makedirs(OUT + '/fu/spv', exist_ok=True)
for f in os.listdir(OUT + '/fu/spv'):
    os.remove(OUT + '/fu/spv/' + f)
for exe in ('log_async_tests.exe', 'log_async_tests_rc4off.exe', 'diag_b32_tests.exe', 'shader_cfg_tests.exe', 'f25l2_probe.exe'):
    print('sha256', sha(BIN + '/' + exe)[:16], exe)
print('sha256', sha(REFEXE)[:16], 'ref')

guard()
r = subprocess.run([BIN + '/log_async_tests.exe', OUT], capture_output=True, text=True, env=clean_env(), errors='replace')
open(OUT + '/log_async_tests.log', 'w', encoding='utf-8', newline='\n').write(r.stdout + r.stderr)
last = r.stdout.splitlines()[-1] if r.stdout else ''
t1 = r.returncode == 0 and last == 'ALL OK'
print('t1 log_async_tests rc=%d last=%r cases=%s -> %s' % (r.returncode, last, re.findall(r'cases=(\d+) failures=(\d+)', r.stdout),
                                                         'ok' if t1 else 'FAIL'))
for f in ('lat0', 'lat1', 'lf0', 'lf1', 'lfoff'):
    p = OUT + '/' + f + '.txt.res'
    print('  ', f, open(p).read().strip() if os.path.exists(p) else '-')
for l in r.stdout.splitlines():
    if 'die_owner' in l or 'longframe_lines' in l:
        print('  ', l.strip())
ok &= t1

guard()
ref_txt = OUT + '/seq0_ref.txt'
if os.path.exists(ref_txt):
    os.remove(ref_txt)
r = subprocess.run([REFEXE, '--child', 'seq0', ref_txt], capture_output=True, text=True, env=clean_env())
h = {k: (sha(OUT + '/' + k + '.txt') if os.path.exists(OUT + '/' + k + '.txt') else '-') for k in ('seq0_ref', 'seq0_0', 'seq0_u', 'seq0_1')}
t1b = r.returncode == 0 and h['seq0_ref'] == h['seq0_0'] == h['seq0_u'] and h['seq0_1'] != h['seq0_0']
print('t1b ref %s =0 %s unset %s =1 %s -> %s' % (h['seq0_ref'][:16], h['seq0_0'][:16], h['seq0_u'][:16], h['seq0_1'][:16],
                                                'ok' if t1b else 'FAIL'))
ok &= t1b

guard()
r = subprocess.run([BIN + '/diag_b32_tests.exe'], capture_output=True, text=True, errors='replace', env=clean_env())
open(OUT + '/diag_b32_tests.log', 'w', encoding='utf-8', newline='\n').write(r.stdout + r.stderr)
t2 = r.returncode == 0 and r.stdout.splitlines()[-1:] == ['ALL OK']
print('t2 diag_b32_tests rc=%d -> %s' % (r.returncode, 'ok' if t2 else 'FAIL'))
ok &= t2

guard()
env = clean_env()
env['KYTY_TESTS_CONTINUE'] = '1'
env['KYTY_TESTS_VERBOSE'] = '1'
env['KYTY_TESTS_SPV_DIR'] = OUT + '/fu/spv'
r = subprocess.run([BIN + '/shader_cfg_tests.exe'], capture_output=True, text=True, cwd=BUILD, env=env, errors='replace')
log = r.stdout + r.stderr
open(OUT + '/fu/log.txt', 'w', encoding='utf-8', newline='\n').write(log)
n_tests = len(re.findall(r'^\[test\] ', log, re.M))
n_failed = len(re.findall(r'ShaderCfgTests: failed:', log))
ref_log = open('C:/kyty/f287/f25k2/tests_out/fu/log.txt', encoding='utf-8', errors='replace').read()  # FS8a fu has no log.txt; the F25k2 count (= F25k 133)
ref_tests = len(re.findall(r'^\[test\] ', ref_log, re.M))
t3 = r.returncode == 0 and n_failed == 0 and n_tests > 0 and n_tests == ref_tests
print('t3 shader_cfg_tests rc=%d tests=%d (F25k2 %d) failed_lines=%d -> %s' % (r.returncode, n_tests, ref_tests, n_failed,
                                                                                  'ok' if t3 else 'FAIL'))
ok &= t3
mine = sorted(os.listdir(OUT + '/fu/spv'))
ref = sorted(os.listdir(REF + '/spv'))
diff = [f for f in sorted(set(mine) | set(ref)) if f not in mine or f not in ref or sha(OUT + '/fu/spv/' + f) != sha(REF + '/spv/' + f)]
t4 = len(mine) > 0 and not diff
print('t4 SPIR-V mine %d ref %d differing %d -> %s' % (len(mine), len(ref), len(diff), 'ok' if t4 else 'FAIL'))
ok &= t4

guard()
os.makedirs(OUT + '/pc', exist_ok=True)
r = subprocess.run([BIN + '/log_async_tests_rc4off.exe', OUT + '/pc', '--case', 'die_owner'], capture_output=True, text=True,
                   env=clean_env(), errors='replace')
open(OUT + '/pc_rc4off.log', 'w', encoding='utf-8', newline='\n').write(r.stdout + r.stderr)
m = re.search(r'child die_owner .* rc=(-?\d+) \(0x([0-9a-f]+)\) ([0-9.]+) s( HUNG)?', r.stdout)
secs = float(m.group(3)) if m else -1.0
hung = bool(m and m.group(4))
cxx = 'Exception: code=0xe06d7363' in (r.stdout + r.stderr)
t5 = r.returncode == 1 and m is not None and (hung or secs > 10.0 or cxx)
print('t5 positive control (RC4 guard removed) rc=%d secs=%.1f hung=%s cxx_line=%s -> %s' % (r.returncode, secs, hung, cxx,
                                                                                         'ok' if t5 else 'FAIL'))
ok &= t5

guard()
r = subprocess.run([BIN + '/f25l2_probe.exe', OUT + '/probe'], capture_output=True, text=True, env=clean_env(), errors='replace')
open(OUT + '/probe.out', 'w', encoding='utf-8', newline='\n').write(r.stdout + r.stderr)
print(r.stdout)
print('ALL OK' if ok else 'FAILED')
