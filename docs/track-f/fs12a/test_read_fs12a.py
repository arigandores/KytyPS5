"""FS12a (HPP-750): fixtures of read_fs12a.py - a good synthetic run set gives 'MEMBERS ALL YES'; one fixture per member
(spoiled one field of one trial) gives 'MEMBERS NOT ALL'. Last line 'ALL OK'.
    python test_read_fs12a.py"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import read_fs12a as R  # noqa: E402

FIELDS = ['fix', 'arm', 'seed', 'pos', 'cfg_fix', 'rc', 'rc_hex', 'dur_s', 'hang', 'control', 'enters', 'walks',
          'walks_cb', 'nested', 'main_cbs', 'guest_cbs', 'second', 'cut', 'expired', 'reenter', 'done_seen',
          'wait_done', 'expired_seen', 'trig_waited_us', 'h_dt_s', 'fatal_text', 'abort', 'crash', 'k1', 'leftover',
          'nested_fatal', 'utc']
BASE = {k: '0' for k in FIELDS}
BASE.update({'pos': '1', 'rc_hex': '', 'trig_waited_us': '', 'h_dt_s': '', 'control': '', 'utc': 'x'})
GOOD = {
    ('d', 'P2'): dict(rc='0', dur_s='0.300', walks='1', control='1', cfg_fix='1'),
    ('d', 'C'): dict(rc='321', dur_s='0.160', walks='1', nested='0', reenter='1', cfg_fix='1'),
    ('d', 'CN'): dict(rc='321', dur_s='0.160', walks='1', nested='0', reenter='2', cut='1', nested_fatal='1', k1='1',
                      cfg_fix='1'),
    ('d', 'H'): dict(rc='321', dur_s='15.1', walks='1', control='1', expired='1', cut='1', k1='1', h_dt_s='15.0',
                     cfg_fix='1'),
    ('d', 'HG'): dict(rc='0', dur_s='12.4', walks='1', control='1', expired='1', cut='1', k1='1', h_dt_s='12.010',
                      cfg_fix='1'),
    ('0', 'P2'): dict(rc='0', dur_s='0.300', walks='2', control='1', cfg_fix='0'),
}


def build(d, spoil=None):
    for fix, arm, N in R.PLAN:
        rows = []
        for s in range(1, N + 1):
            r = dict(BASE)
            r.update({'fix': fix, 'arm': arm, 'seed': str(s)})
            r.update(GOOD[(fix, arm)])
            if fix == '0' and s == 3:
                r['second'] = '1'
            rows.append(r)
        mode = '1' if fix == 'd' else '0'
        nolog = None
        if spoil and spoil[0] == (fix, arm):
            key, val = spoil[1], spoil[2]
            if key == '_drop':
                rows = rows[:-1]
            elif key == '_nolog':
                nolog = 1
            elif key == '_all':
                for r in rows:
                    r.update(val)
            else:
                rows[0][key] = val
        os.makedirs('%s/fix%s/%s' % (d, fix, arm), exist_ok=True)
        with open('%s/fix%s/stand_%s.tsv' % (d, fix, arm), 'w', encoding='utf-8', newline='') as f:
            f.write('\t'.join(FIELDS) + '\n')
            for r in rows:
                f.write('\t'.join(r[k] for k in FIELDS) + '\n')
        for r in rows:
            text = 'x\nFixF21: mode=%s wait_ms=12000\ny\n' % mode
            if nolog and r['seed'] == '1':
                text = 'x\n'
            open('%s/fix%s/%s/%s.log' % (d, fix, arm, r['seed']), 'w', encoding='utf-8').write(text)


CASES = [
    ('good', None, True),
    ('P2 control', (('d', 'P2'), 'control', '0'), False),
    ('P2 second', (('d', 'P2'), 'second', '1'), False),
    ('P2 cut', (('d', 'P2'), 'cut', '1'), False),
    ('P2 seed missing', (('d', 'P2'), '_drop', None), False),
    ('C done_seen', (('d', 'C'), 'done_seen', '1'), False),
    ('C reenter 0', (('d', 'C'), 'reenter', '0'), False),
    ('C walks 2', (('d', 'C'), 'walks', '2'), False),
    ('C rc 0', (('d', 'C'), 'rc', '0'), False),
    ('CN reenter 1', (('d', 'CN'), 'reenter', '1'), False),
    ('CN dur 7', (('d', 'CN'), 'dur_s', '7.0'), False),
    ('CN expired_seen', (('d', 'CN'), 'expired_seen', '1'), False),
    ('CN nested', (('d', 'CN'), 'nested', '1'), False),
    ('CN nested_fatal 0', (('d', 'CN'), 'nested_fatal', '0'), False),
    ('H expired 0', (('d', 'H'), 'expired', '0'), False),
    ('H rc 5', (('d', 'H'), 'rc', '5'), False),
    ('H hang', (('d', 'H'), 'hang', '1'), False),
    ('H order', (('d', 'H'), 'control', '0'), False),
    ('H rc 0 ok', (('d', 'H'), 'rc', '0'), True),
    ('HG rc 321', (('d', 'HG'), 'rc', '321'), False),
    ('HG dt 15', (('d', 'HG'), 'h_dt_s', '15.100'), False),
    ('HG dt 11.9', (('d', 'HG'), 'h_dt_s', '11.900'), False),
    ('HG second', (('d', 'HG'), 'second', '1'), False),
    ('HG expired 0', (('d', 'HG'), 'expired', '0'), False),
    ('=0 P2 second 0', (('0', 'P2'), '_all', {'second': '0'}), False),
    ('=0 P2 expired', (('0', 'P2'), 'expired', '1'), False),
    ('default cfg_fix 0', (('d', 'C'), 'cfg_fix', '0'), False),
    ('=0 cfg_fix 1', (('0', 'P2'), 'cfg_fix', '1'), False),
    ('default no mode line', (('d', 'HG'), '_nolog', None), False),
    ('leftover', (('d', 'P2'), 'leftover', '1'), False),
]

ok = True
for name, spoil, want in CASES:
    d = tempfile.mkdtemp()
    try:
        build(d, spoil)
        _, got = R.read(d)
    finally:
        shutil.rmtree(d)
    good = got == want
    ok &= good
    print('%-24s want %-5s got %-5s %s' % (name, want, got, 'ok' if good else 'FAIL'))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
