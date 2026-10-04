"""Track F link FS5c (HPP-511): manual sensitivity check of fs5c_read.py (form of F12f sens_f12f.py: each edit of the reader must drop
fixtures of test_fs5c_read.py).  Prints one line per edit: '<fails> <edit>' and 'SENS ALL OK' if every edit drops >= 1 fixture.
ASCII only."""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BS = chr(92)
src = open(os.path.join(HERE, 'fs5c_read.py'), encoding='ascii').read()
MUTS = [
    ("res['hold_us'] >= HOLD_MIN_US", "res['hold_us'] > HOLD_MIN_US"),
    ("s.replace('/', '" + BS + BS + "').endswith('" + BS + BS + "' + DIR_FIX)", "('_fixf10' in s)"),
    ("if dt >= K2_US:", "if dt > K2_US:"),
    ("(res['idx_records'] or 0) >= VIDEO_MIN", "(res['idx_records'] or 0) > VIDEO_MIN"),
    ("not res['gamepatch']", "True"),
    ("res['vkw'] > 0", "True"),
    ("sha_b == WANT", "True"),
    ("sha_a == WANT", "True"),
    ("('R1: 0 lines SPIR-V validation failed (member)', nfail == 0)", "('R1: 0 lines SPIR-V validation failed (member)', True)"),
    ("nfail = res['fail_log'] + res['fail_stdout']", "nfail = res['fail_log']"),
    ("all(m == 1 and u == 1 for _, m, u in r['fs'])", "True"),
    ("(r['guest_first'] is None or r['fs'][0][0] < r['guest_first'])", "True"),
    ("and DIR_FIX in pf)", ")"),
    ("res['manifest_ref_ok']))", "True))"),
]
ok = True
for a, b in MUTS:
    if src.count(a) < 1:
        print('MISSING %s' % a)
        ok = False
        continue
    d = tempfile.mkdtemp(prefix='fs5c_sens_')
    open(os.path.join(d, 'fs5c_read.py'), 'w', newline='\n').write(src.replace(a, b))
    shutil.copy(os.path.join(HERE, 'test_fs5c_read.py'), d)
    p = subprocess.run([sys.executable, os.path.join(d, 'test_fs5c_read.py')], capture_output=True, text=True)
    nf = len([x for x in p.stdout.split('\n') if x.startswith('FAIL')])
    print('%d %s' % (nf, a[:70]))
    ok &= nf >= 1
    shutil.rmtree(d, ignore_errors=True)
print('SENS ALL OK' if ok else 'SENS SOME UNDETECTED')
