"""F25f (HPP-669): regression of f25_read.py on the inventory logs of F25a s1.2 (no DiagB32 lines there): B36 v143_08 (pot_treasure_cave)
and B40 v145_14 (bonus_path_maker_mix) - hold, the K2 frame (n, dt_us), class NO_SAMPLES:key, the form label, the precursors, K / K_I;
v144_10 and r146_04 (second entries) - K 0.  ASCII only; ends with REGRESS PASS / FAIL.
usage: python regress_f25.py"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f25_read as R  # noqa: E402

CASES = (('C:/kyty/s143/log_v143_08.txt', R.POT, dict(K=1, K_I=1, k2=[(14701, 6614314, 'NO_SAMPLES:key', 'FORM_SEM')],
                                                      pre=[14588, 14669])),
         ('C:/kyty/s145/log_v145_14.txt', R.BONUS, dict(K=1, K_I=1, k2=[(7249, 4624510, 'NO_SAMPLES:key', 'FORM_NOFLIP')], pre=[7188, 7216])),
         ('C:/kyty/s144/log_v144_10.txt', R.POT, dict(K=0, K_I=0, k2=[], pre=[])),
         ('C:/kyty/s146/log_r146_04.txt', R.BONUS, dict(K=0, K_I=0, k2=[], pre=[])))


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    print('suite regress_f25.py sha256 %s target f25_read.py sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                          sha(os.path.join(HERE, 'f25_read.py'))))
    ok = True
    tmp = os.path.join(HERE, 'regress_tmp')
    os.makedirs(tmp, exist_ok=True)
    for p, lv, want in CASES:
        if not os.path.exists(p):
            p += '.xz'
        r = R.read_log(p, 0.4562, lv, tmp)
        k2 = [(x['n'], x['dt_us'], x['cls'], x['form']) for x in r['frames'] if x['in_count']]
        pre = [x['n'] for x in r['frames'] if x.get('precursor')]
        good = r['hold'] and r['K'] == want['K'] and r['K_I'] == want['K_I'] and k2 == want['k2'] and pre == want['pre']
        ok &= good
        print('%s %s sha256 %s | hold %s scene %.1f s K %d K_I %d in count %s precursors %s | %s' % (
            'ok' if good else 'MISMATCH', p.replace('C:/kyty/', ''), sha(p)[:16], r['hold'], r['scene_s'], r['K'], r['K_I'], k2, pre, lv))
    os.rmdir(tmp)
    print('REGRESS %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
