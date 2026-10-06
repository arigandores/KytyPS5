"""F20l3 (HPP-655; port of the F20l2 file): regression of b32_read.read_log on logs without KYTY_DIAG_B32: two warm F20e logs (RC13 equal,
every hold frame NO_SAMPLES, K_I by the F20e reading, warm precache line) and the cold FS8e prewarm log log_fs8_i.txt (the PK-A domain of
item 591 (v)(2) is not empty on a cold entry; 'PipelinePrecache: no ... yet' present, no recipes line).  The expectation of each log is
named in WANT before the run.  usage: python regress/regress_b32.py <log> ...  ASCII only."""
import os
import sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import b32_read as R  # noqa: E402
# name -> (cold, pk_a3 non-empty)
WANT = {'log_f20_v35.txt': (False, False), 'log_f20_v32.txt': (False, None), 'log_fs8_i.txt': (True, True)}
ok = True
print('suite regress_b32.py target b32_read.py sha256 %s' % R.sha_file(os.path.join(HERE, 'b32_read.py')))
for p in sys.argv[1:]:
    r = R.read_log(p, 0.4562, None, os.path.join(HERE, 'regress'))
    cl = sorted(set(x['cls'] for x in r['frames']))
    cold, pk = WANT.get(os.path.basename(p), (None, None))
    good = r['rc13_equal'] and r['diag_lines'] == 0 and all(x['cls'] == 'NO_SAMPLES' for x in r['frames']) and r['sig'] == [R.SIG_FS8]
    good &= all(x['cls'] == 'NO_SAMPLES' and not x['armed'] for x in r['pk_a3'])
    if cold is not None:
        good &= (r['precache_no'] >= 1 and r['precache_recipes'] == 0) if cold else (r['precache_no'] == 0 and r['precache_recipes'] >= 1)
    if pk is not None:
        good &= bool(r['pk_a3']) == pk
    ok &= good
    print('%s rc13 %s stripped %d hold %s P_I %d K_I %d frames %s classes %s sig %s dir %s u5_med %s u5_slow70 %s b5 %s | PK-A cold domain %d '
          'armed %d member %s first %s; out by instr %d; pre-scene >= 100 ms %s; precache no %d recipes %d; seed other %s %s' % (
              os.path.basename(p), r['rc13_equal'], r['rc13_stripped'], r['hold'], r['P_I'], r['K_I'],
              [(x['n'], x['dt_us'], x['attr']) for x in r['frames']][:6], cl, [s[:8] for s in r['sig']], r['variant_dir'], r['u5_med_dt'],
              r['u5_slow70'], r['u5_b5_n'], len(r['pk_a3']), r['pk_a3_armed'], r['pk_a3_member'],
              [(x['n'], x['dt_us'], x['t_s']) for x in r['pk_a3'][:5]], len(r['pk_a3_instr']), [tuple(x) for x in r['pre_scene_slow'][:5]],
              r['precache_no'], r['precache_recipes'], r['seed_other'], 'OK' if good else 'BAD'))
print('REGRESS %s' % ('PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
