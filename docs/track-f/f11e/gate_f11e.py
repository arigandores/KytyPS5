# F11e (HPP-467, Red Team): own run of the F11d GPU gate (--diag-bvh-only) with one knob set per call:
#   python gate_f11e.py <tag> <KYTY_DIAG_BVHNODES or unset> <KYTY_BVH_NATIVE>
# Test binary - C:/kyty/f287/f11d/build/shader_recompiler_compute_tests.exe (sha256 checked first); cwd - own folder.
import hashlib, os, re, subprocess, sys
NL = chr(10)
OUT = 'C:/kyty/f287/f11e/own'
EXE = 'C:/kyty/f287/f11d/build/shader_recompiler_compute_tests.exe'
WANT = '6219ff38342680935cd907d4afd4a3391c1f4ee9fcb3753f202b72aba00d45f8'
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('ABORT: lock or STOP')
    sys.exit(3)
tag, diag, nat = sys.argv[1], sys.argv[2], sys.argv[3]
h = hashlib.sha256(open(EXE, 'rb').read()).hexdigest()
if h != WANT:
    print('ABORT: test binary sha', h)
    sys.exit(5)
env = dict(os.environ)
for k in ['KYTY_DIAG_BVHNODES', 'KYTY_BVH_NATIVE', 'KYTY_TEST_LOG_CONSOLE']:
    env.pop(k, None)
if diag != 'unset':
    env['KYTY_DIAG_BVHNODES'] = diag
env['KYTY_BVH_NATIVE'] = nat
env['KYTY_TEST_LOG_CONSOLE'] = '1'
run_dir = OUT + '/gate_cwd'
os.makedirs(run_dir, exist_ok=True)
r = subprocess.run([EXE, '--diag-bvh-only'], env=env, cwd=run_dir, capture_output=True, timeout=55)
txt = (r.stdout + r.stderr).decode('utf-8', 'replace')
open(OUT + '/gate_' + tag + '.txt', 'w', encoding='utf-8', newline='').write(txt)
lines = txt.split(NL)
oks = [l for l in lines if re.match(r'^\[compute\] Diag\S+\s+ok', l)]
fails = [l for l in lines if 'FAIL' in l or 'mismatch' in l.lower()]
diag_lines = [l for l in lines if l.startswith('DiagBvhNodes:')]
fb = [l for l in lines if 'emulator fault buffer bytes=' in l]
cache = [l for l in lines if 'cache dir=' in l]
print('gate', tag, 'diag', diag, 'nat', nat, 'rc', r.returncode, 'ALL_OK', 'ALL OK' in lines or any(l.strip() == 'ALL OK' for l in lines),
      'cases_ok', len(oks), 'fail_lines', len(fails), 'DiagBvhNodes_lines', len(diag_lines))
for l in fb + cache:
    print('  ', l.strip())
for l in fails[:5]:
    print('  FAIL:', l.strip()[:200])
