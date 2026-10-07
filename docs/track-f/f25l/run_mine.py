# F25l (HPP-679): the F25k tests (t1, t1b) rerun by Red Team into its own folder; the binaries of the F25k build.
import hashlib, os, subprocess, sys
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
B = 'C:/kyty/f287/f25k/build'
OUT = 'C:/kyty/f287/f25l/tests_mine'
REFEXE = 'C:/kyty/f287/f25k/ref/log_async_tests_ref.exe'
def guard():
    if os.path.exists(LOCK): print('HALT lock'); sys.exit(5)
    if os.path.exists(STOP): print('HALT stop'); sys.exit(4)
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
os.makedirs(OUT, exist_ok=True)
for exe in (B + '/log_async_tests.exe', REFEXE):
    print('sha256', sha(exe), exe)
guard()
r = subprocess.run([B + '/log_async_tests.exe', OUT], capture_output=True, text=True, env=env, errors='replace')
open(OUT + '/log_async_tests.log', 'w', encoding='utf-8', newline='\n').write(r.stdout + r.stderr)
print(r.stdout)
last = r.stdout.splitlines()[-1] if r.stdout else ''
t1 = r.returncode == 0 and last == 'ALL OK'
guard()
ref_txt = OUT + '/seq0_ref.txt'
if os.path.exists(ref_txt): os.remove(ref_txt)
r2 = subprocess.run([REFEXE, '--child', 'seq0', ref_txt], capture_output=True, text=True, env=env)
h = {k: sha(OUT + '/' + k + '.txt') for k in ('seq0_ref', 'seq0_0', 'seq0_u', 'seq0_1')}
t1b = r2.returncode == 0 and h['seq0_ref'] == h['seq0_0'] == h['seq0_u'] and h['seq0_1'] != h['seq0_0']
for k, v in h.items(): print('seq', k, v)
for f in ('lat0', 'lat1', 'full'):
    print(f, open(OUT + '/' + f + '.txt.res').read().strip())
print('t1', 'ok' if t1 else 'FAIL', 't1b', 'ok' if t1b else 'FAIL')
print('ALL OK' if t1 and t1b else 'FAILED')
