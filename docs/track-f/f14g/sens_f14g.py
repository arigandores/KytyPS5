"""Track F link F14g (HPP-507): manual sensitivity check of f14g_read.py (form of F12f sens_f12f.py: each edit of the reader must drop
fixtures of test_f14g_read.py).  Prints one line per edit: '<fails> <edit>' and 'SENS ALL OK' if every edit drops >= 1 fixture.
ASCII only."""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BS = chr(92)
src = open(os.path.join(HERE, 'f14g_read.py'), encoding='ascii').read()
MUTS = [
    ("res['hold_us'] >= HOLD_MIN_US", "res['hold_us'] > HOLD_MIN_US"),
    ("s.replace('/', '" + BS + BS + "').endswith('" + BS + BS + "' + DIR_FIX)", "('_fixf19' in s)"),
    ("if dt >= K2_US:", "if dt > K2_US:"),
    ("(res['idx_records'] or 0) >= VIDEO_MIN", "(res['idx_records'] or 0) > VIDEO_MIN"),
    ("not res['gamepatch']", "True"),
    ("res['vkw'] > 0", "True"),
    ("sha_b == WANT", "True"),
    ("len(rc) == (res['rdc_n'] or 0)", "True"),
    ("if c['A'] > 0 or c['D'] > 0:", "if c['D'] > 0:"),
    ("if c['A'] > 0 or c['D'] > 0:", "if c['A'] > 0:"),
    ("cen == '1' and cop == LEQ and mag == LIN and mn == LIN", "cen == '1' and cop == LEQ and mag == LIN"),
    ("cen == '1' and cop == LEQ and mag == LIN and mn == LIN", "cen == '1' and mag == LIN and mn == LIN"),
    ("if c['records'] == 0:", "if False:"),
    ("if c['B'] >= 1 and c['C'] == c['B']:", "if c['C'] == c['B']:"),
    ("res['sum_records'] == recs and", "True or"),
    ("if b'06479' in raw:", "if False:"),
    ("if vf == D16:", "if vf in (D16, 'VK_FORMAT_D32_SFLOAT'):"),
    ("k01[0]['letter'] == 'ACTS_IN_FRAME'", "True"),
]
ok = True
for a, b in MUTS:
    if src.count(a) < 1:
        print('MISSING %s' % a)
        ok = False
        continue
    d = tempfile.mkdtemp(prefix='f14g_sens_')
    open(os.path.join(d, 'f14g_read.py'), 'w', newline='\n').write(src.replace(a, b))
    shutil.copy(os.path.join(HERE, 'test_f14g_read.py'), d)
    p = subprocess.run([sys.executable, os.path.join(d, 'test_f14g_read.py')], capture_output=True, text=True)
    nf = len([x for x in p.stdout.split('\n') if x.startswith('FAIL')])
    print('%d %s -> %s' % (nf, a[:60], b[:40]))
    ok &= nf >= 1
    shutil.rmtree(d, ignore_errors=True)
print('SENS ALL OK' if ok else 'SENS SOME UNDETECTED')
