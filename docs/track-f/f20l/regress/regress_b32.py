"""F20l (HPP-631): regression of b32_read.read_log on F20e logs (KYTY_DIAG_B32 absent): RC13 equal, every hold frame NO_SAMPLES, K_I by the
F20e reading.  usage: python regress/regress_b32.py <log> ...  ASCII only."""
import os
import sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import b32_read as R  # noqa: E402
ok = True
print('suite regress_b32.py target b32_read.py sha256 %s' % R.sha_file(os.path.join(HERE, 'b32_read.py')))
for p in sys.argv[1:]:
    r = R.read_log(p, None, None, os.path.join(HERE, 'regress'))
    cl = sorted(set(x['cls'] for x in r['frames']))
    good = r['rc13_equal'] and r['diag_lines'] == 0 and all(x['cls'] == 'NO_SAMPLES' for x in r['frames']) and r['sig'] == [R.SIG_FS8]
    ok &= good
    print('%s rc13 %s stripped %d hold %s P_I %d K_I %d frames %s classes %s sig %s dir %s u5_med %s u5_slow70 %s b5 %s %s' % (
        os.path.basename(p), r['rc13_equal'], r['rc13_stripped'], r['hold'], r['P_I'], r['K_I'], [(x['n'], x['dt_us'], x['attr']) for x in r['frames']],
        cl, [s[:8] for s in r['sig']], r['variant_dir'], r['u5_med_dt'], r['u5_slow70'], r['u5_b5_n'], 'OK' if good else 'BAD'))
print('REGRESS %s' % ('PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
