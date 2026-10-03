"""Track F link F12f (HPP-480): manual sensitivity check of f12f_read.py (form of F11f section 7: each edit of the reader must drop
fixtures of test_f12f_read.py).  Prints one line per edit: '<fails> <edit>' and 'SENS ALL OK' if every edit drops >= 1 fixture.
ASCII only."""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BS = chr(92)
src = open(os.path.join(HERE, 'f12f_read.py'), encoding='ascii').read()
MUTS = [
    ("res['hold_us'] >= HOLD_MIN_US", "res['hold_us'] > HOLD_MIN_US"),
    ("s.replace('/', '" + BS + BS + "').endswith('" + BS + BS + "' + DIR_FIX)", "('_fixf10' in s)"),
    ("not any('_fixf10' in s for s in stc)", "True"),
    ("if dt >= K2_US:", "if dt > K2_US:"),
    ("(res['idx_records'] or 0) >= VIDEO_MIN", "(res['idx_records'] or 0) > VIDEO_MIN"),
    ("nm >= 1))", "True))"),
    ("not res['gamepatch']", "True"),
    ("res['vkw'] > 0", "True"),
    ("sha_b == WANT", "True"),
    ("len(res['rdcs']) == (res['rdc_n'] or 0)", "True"),
]
ok = True
for a, b in MUTS:
    if src.count(a) < 1:
        print('MISSING %s' % a)
        ok = False
        continue
    d = tempfile.mkdtemp(prefix='f12f_sens_')
    open(os.path.join(d, 'f12f_read.py'), 'w', newline='\n').write(src.replace(a, b))
    shutil.copy(os.path.join(HERE, 'test_f12f_read.py'), d)
    p = subprocess.run([sys.executable, os.path.join(d, 'test_f12f_read.py')], capture_output=True, text=True)
    nf = len([x for x in p.stdout.split('\n') if x.startswith('FAIL')])
    print('%d %s' % (nf, a[:70]))
    ok &= nf >= 1
    shutil.rmtree(d, ignore_errors=True)
print('SENS ALL OK' if ok else 'SENS SOME UNDETECTED')
