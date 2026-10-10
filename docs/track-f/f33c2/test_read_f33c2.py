"""F33c2 (HPP-748): fixtures of read_f33c2.py - one fixture per member of CN at =1 (item 681(v)(1)), the stand control
nested_fatal, done_seen of C at =1 (681(v)(2)), the old C and P2 members, =0 C, =0 CN reference, leftover, =0
wait_expired. Last line 'ALL OK'.
    python test_read_f33c2.py"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import read_f33c2 as R  # noqa: E402

FIELDS = ['fix', 'arm', 'seed', 'pos', 'cfg_fix', 'rc', 'rc_hex', 'dur_s', 'hang', 'control', 'enters', 'walks',
          'walks_cb', 'nested', 'main_cbs', 'guest_cbs', 'second', 'cut', 'expired', 'reenter', 'done_seen',
          'wait_done', 'expired_seen', 'trig_waited_us', 'h_dt_s', 'fatal_text', 'abort', 'crash', 'k1', 'leftover',
          'nested_fatal', 'utc']

BASE = {k: '0' for k in FIELDS}
BASE.update({'pos': '1', 'cfg_fix': '1', 'rc_hex': '', 'trig_waited_us': '', 'h_dt_s': '', 'control': '', 'utc': 'x'})
GOOD = {
    ('1', 'CN'): dict(rc='321', dur_s='0.160', walks='1', nested='0', reenter='2', cut='1', nested_fatal='1', k1='1'),
    ('1', 'C'): dict(rc='321', dur_s='0.160', walks='1', nested='0', reenter='1'),
    ('1', 'P2'): dict(rc='0', dur_s='0.300', walks='1', control='1'),
    ('0', 'CN'): dict(rc='321', dur_s='0.160', walks='3', nested='2', nested_fatal='1', cfg_fix='0', k1='1'),
    ('0', 'C'): dict(rc='321', dur_s='0.160', walks='2', reenter='0', cfg_fix='0'),
}


def row(fix, arm, seed, **over):
    r = dict(BASE)
    r.update({'fix': fix, 'arm': arm, 'seed': str(seed)})
    r.update(GOOD[(fix, arm)])
    r.update(over)
    return r


def write(d, fix, arm, rows):
    os.makedirs('%s/fix%s' % (d, fix), exist_ok=True)
    with open('%s/fix%s/stand_%s.tsv' % (d, fix, arm), 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(FIELDS) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[k]) for k in FIELDS) + '\n')


def run_case(fix, arm, bad=None, expect=True, name=''):
    d = tempfile.mkdtemp(prefix='f33c2fx_')
    try:
        rows = [row(fix, arm, s) for s in range(1, 4)]
        if bad is not None:
            rows[1] = row(fix, arm, 2, **bad)
        write(d, fix, arm, rows)
        lines, ok = R.read(d)
        good = ok == expect
        print('%-4s %-40s expect %s got %s' % ('ok' if good else 'FAIL', name, expect, ok))
        if not good:
            for line in lines:
                print('     ', line)
        return good
    finally:
        shutil.rmtree(d, ignore_errors=True)


cases = [
    ('1', 'CN', None, True, 'CN =1 good'),
    ('1', 'CN', dict(walks='2'), False, 'CN =1 walks 2'),
    ('1', 'CN', dict(walks='0'), False, 'CN =1 walks 0'),
    ('1', 'CN', dict(nested='1'), False, 'CN =1 nested 1'),
    ('1', 'CN', dict(reenter='1'), False, 'CN =1 reenter 1 (< 2)'),
    ('1', 'CN', dict(reenter='3'), True, 'CN =1 reenter 3 (>= 2)'),
    ('1', 'CN', dict(expired='1'), False, 'CN =1 expired 1'),
    ('1', 'CN', dict(expired_seen='1'), False, 'CN =1 expired_seen 1'),
    ('1', 'CN', dict(rc='0'), False, 'CN =1 rc 0'),
    ('1', 'CN', dict(rc=''), False, 'CN =1 rc empty (timeout)'),
    ('1', 'CN', dict(hang='1'), False, 'CN =1 hang 1'),
    ('1', 'CN', dict(crash='1'), False, 'CN =1 crash 1'),
    ('1', 'CN', dict(dur_s='6.000'), False, 'CN =1 dur 6.000 (not < 6)'),
    ('1', 'CN', dict(dur_s='5.999'), True, 'CN =1 dur 5.999'),
    ('1', 'CN', dict(dur_s='12.170'), False, 'CN =1 dur 12.17 (m4b form)'),
    ('1', 'CN', dict(nested_fatal='0'), False, 'CN =1 stand control nested_fatal 0'),
    ('1', 'CN', dict(leftover='1'), False, 'CN =1 leftover 1'),
    ('1', 'C', None, True, 'C =1 good'),
    ('1', 'C', dict(done_seen='1'), False, 'C =1 done_seen 1'),
    ('1', 'C', dict(walks='2'), False, 'C =1 walks 2'),
    ('1', 'C', dict(rc='0'), False, 'C =1 rc 0'),
    ('1', 'C', dict(reenter='0'), False, 'C =1 reenter 0'),
    ('1', 'C', dict(nested='1'), False, 'C =1 nested 1'),
    ('1', 'C', dict(second='1'), False, 'C =1 second 1'),
    ('1', 'C', dict(cut='1'), False, 'C =1 cut 1'),
    ('1', 'C', dict(expired='1'), False, 'C =1 expired 1'),
    ('1', 'C', dict(hang='1'), False, 'C =1 hang 1'),
    ('1', 'C', dict(crash='1'), False, 'C =1 crash 1'),
    ('1', 'P2', None, True, 'P2 =1 good'),
    ('1', 'P2', dict(control='0'), False, 'P2 =1 control 0'),
    ('1', 'P2', dict(second='1'), False, 'P2 =1 second 1'),
    ('1', 'P2', dict(cut='1'), False, 'P2 =1 cut 1'),
    ('1', 'P2', dict(expired='1'), False, 'P2 =1 expired 1'),
    ('1', 'P2', dict(crash='1'), False, 'P2 =1 crash 1'),
    ('1', 'P2', dict(hang='1'), False, 'P2 =1 hang 1'),
    ('0', 'CN', None, True, 'CN =0 reference'),
    ('0', 'CN', dict(walks='1', nested='0'), True, 'CN =0 reference does not gate'),
    ('0', 'CN', dict(expired='1'), False, 'CN =0 wait_expired line'),
    ('0', 'C', None, True, 'C =0 good'),
    ('0', 'C', dict(k1='1'), False, 'C =0 k1 1'),
    ('0', 'C', dict(expired='1', k1='1'), False, 'C =0 wait_expired line'),
]
ok = all([run_case(*c) for c in cases])
print('cases', len(cases))
print('ALL OK' if ok else 'FIXTURES FAILED')
sys.exit(0 if ok else 1)
