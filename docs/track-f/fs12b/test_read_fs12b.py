# FS12b (HPP-751, Red Team): fixtures of read_fs12b.py - one passing synthetic run dir, then one broken field per member
# (each must turn MEMBERS ALL YES into NOT ALL at exactly that member). Prints ALL OK at the end.
import copy
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import read_fs12b as R

FIELDS = ['fix', 'arm', 'seed', 'pos', 'cfg_fix', 'rc', 'rc_hex', 'dur_s', 'hang', 'control', 'enters', 'walks', 'walks_cb',
          'nested', 'main_cbs', 'guest_cbs', 'second', 'cut', 'expired', 'reenter', 'done_seen', 'wait_done', 'expired_seen',
          'trig_waited_us', 'h_dt_s', 'fatal_text', 'abort', 'crash', 'k1', 'leftover', 'nested_fatal', 'utc']
BASE = {k: '0' for k in FIELDS}
BASE.update({'dur_s': '0.3', 'h_dt_s': '', 'trig_waited_us': '', 'rc_hex': '', 'utc': 'x', 'pos': '1'})


def gen():
    d = {}
    d[('d', 'P2')] = [dict(BASE, fix='d', arm='P2', seed=str(s), cfg_fix='1', rc='321', control='1', walks='1') for s in range(200)]
    d[('d', 'H')] = [dict(BASE, fix='d', arm='H', seed=str(s), cfg_fix='1', rc='0', expired='1', control='1') for s in range(20)]
    d[('d', 'CN')] = [dict(BASE, fix='d', arm='CN', seed=str(s), cfg_fix='1', rc='321', walks='1', reenter='2', nested_fatal='1')
                      for s in range(20)]
    d[('0', 'P2')] = [dict(BASE, fix='0', arm='P2', seed=str(s), cfg_fix='0', rc='321', second='1' if s == 3 else '0') for s in range(20)]
    return d


def write(root, d, modes=None):
    for (fix, arm), rs in d.items():
        od = '%s/fix%s/%s' % (root, fix, arm)
        os.makedirs(od, exist_ok=True)
        with open('%s/fix%s/stand_%s.tsv' % (root, fix, arm), 'w', encoding='utf-8', newline='') as f:
            f.write('\t'.join(FIELDS) + '\n')
            for r in rs:
                f.write('\t'.join(r[k] for k in FIELDS) + '\n')
        for r in rs:
            m = (modes or {}).get((fix, arm, r['seed']), 'FixF21: mode=%s wait_ms=12000' % ('1' if fix == 'd' else '0'))
            open('%s/%s.log' % (od, r['seed']), 'w', encoding='utf-8').write('x\n' + m + '\nend\n')


def run(d, modes=None):
    t = tempfile.mkdtemp(prefix='fx12b_')
    try:
        write(t, d, modes)
        return R.read(t)
    finally:
        shutil.rmtree(t)


ok = True
res = run(gen())
good = all(g for _, g, _ in res)
print('fixture pass:', 'ALL YES' if good else [n for n, g, _ in res if not g])
ok &= good
cases = [
    ('P2 N 199', lambda d: d[('d', 'P2')].pop(), 'P2 N >= 200'),
    ('H N 19', lambda d: d[('d', 'H')].pop(), 'H N >= 20'),
    ('CN N 19', lambda d: d[('d', 'CN')].pop(), 'CN N >= 20'),
    ('P2 cfg_fix 0', lambda d: d[('d', 'P2')][5].update(cfg_fix='0'), 'P2 cfg_fix'),
    ('P2 leftover 1', lambda d: d[('d', 'P2')][5].update(leftover='1'), 'P2 cfg_fix'),
    ('P2 second', lambda d: d[('d', 'P2')][7].update(second='1'), 'P2 second'),
    ('P2 crash', lambda d: d[('d', 'P2')][7].update(crash='1'), 'P2 second'),
    ('P2 hang', lambda d: d[('d', 'P2')][7].update(hang='1'), 'P2 second'),
    ('P2 cut', lambda d: d[('d', 'P2')][7].update(cut='1'), 'P2 second'),
    ('P2 expired', lambda d: d[('d', 'P2')][7].update(expired='1'), 'P2 second'),
    ('P2 control 0', lambda d: [r.update(control='0') for r in d[('d', 'P2')]], 'P2 second'),
    ('H expired 0', lambda d: d[('d', 'H')][2].update(expired='0'), 'H expired'),
    ('H second', lambda d: d[('d', 'H')][2].update(second='1'), 'H expired'),
    ('H cut', lambda d: d[('d', 'H')][2].update(cut='1'), 'H expired'),
    ('CN walks 2', lambda d: d[('d', 'CN')][1].update(walks='2'), 'CN walks'),
    ('CN nested 1', lambda d: d[('d', 'CN')][1].update(nested='1'), 'CN walks'),
    ('CN reenter 1', lambda d: d[('d', 'CN')][1].update(reenter='1'), 'CN walks'),
    ('CN expired 1', lambda d: d[('d', 'CN')][1].update(expired='1'), 'CN walks'),
    ('CN expired_seen 1', lambda d: d[('d', 'CN')][1].update(expired_seen='1'), 'CN walks'),
    ('CN rc 0', lambda d: d[('d', 'CN')][1].update(rc='0'), 'CN walks'),
    ('CN dur 6.0', lambda d: d[('d', 'CN')][1].update(dur_s='6.0'), 'CN walks'),
    ('CN nested_fatal 0', lambda d: d[('d', 'CN')][1].update(nested_fatal='0'), 'CN walks'),
    ('ctl0 second 0', lambda d: d[('0', 'P2')][3].update(second='0'), 'control =0'),
    ('ctl0 cfg 1', lambda d: d[('0', 'P2')][4].update(cfg_fix='1'), 'control =0'),
]
for name, mut, expect in cases:
    d = gen()
    mut(d)
    res = run(d)
    failed = [n for n, g, _ in res if not g]
    hit = len(failed) == 1 and failed[0].startswith(expect)
    print(('ok   ' if hit else 'FAIL ') + name + ' -> ' + str(failed))
    ok &= hit
# mode line cases
for name, key, line, expect in [('P2 mode=0 line', ('d', 'P2', '9'), 'FixF21: mode=0 wait_ms=12000', 'P2 cfg_fix'),
                                ('CN no mode line', ('d', 'CN', '4'), 'nothing', 'CN cfg_fix'),
                                ('ctl0 mode=1', ('0', 'P2', '2'), 'FixF21: mode=1 wait_ms=12000', 'control =0')]:
    res = run(gen(), {key: line})
    failed = [n for n, g, _ in res if not g]
    hit = len(failed) == 1 and failed[0].startswith(expect)
    print(('ok   ' if hit else 'FAIL ') + name + ' -> ' + str(failed))
    ok &= hit
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
