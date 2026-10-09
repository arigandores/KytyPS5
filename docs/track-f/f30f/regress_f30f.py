"""Track F link F30f (HPP-711; ROADMAP s122 item 643 (e), item 644 (d)): the reader f30f_read.py on real logs - the fixtures of the reader
on k3k127 (value 2, zero) and s3s127 (value 3 ABBA 0|3, the live control, 40 lines) of session 127 (binary 98d98eee, no F30d fields) and
on the FS10c log fs10_v (value 1).  Numbers against F30a section 2 (sweep_f30a: k3k127 rts_chk 39 814 684, rts_chk_b 39 362 713,
rts_bad 0; s3s127 rts_bad 1 121 276, 40 lines mode=3 reg=1, bits 0x401 x39 and 0x405 x1, rts_bad_noreg 0, rts_race 0).
  (1) default fields: every session 127 line lacks rts_bad_b / rts_bad_rx -> NOT_ADMITTED, the RC4 row NO (missing field, not 0);
  (2) --legacy-fields (regression only): the sums and the members of the kinds v (k3k127) and c3 (s3s127);
  (3) fs10_v (FS10, F30d fields absent) read as a v tag -> NOT_ADMITTED by RC4.
First output line: suite <name> sha256 <sha> target f30f_read.py sha256 <sha>.  Ends with ALL OK.  ASCII only.
usage: python regress_f30f.py"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f30f_read as R  # noqa: E402

FX = os.path.join(HERE, 'fx', 'reg')
LOGS = {'k3k127': 'C:/kyty/s127/log_k3k127.txt.xz', 's3s127': 'C:/kyty/s127/log_s3s127.txt.xz',
        'fs10_v': 'C:/kyty/f287/fs10c/log_fs10_v.txt'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def mkdir(name, src):
    d = os.path.join(FX, name)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, 'log.txt.xz' if src.endswith('.xz') else 'log.txt')
    if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
        shutil.copyfile(src, dst)
    open(os.path.join(d, 'level.txt'), 'w').write('underwater_aerial_garden\n')
    shutil.copyfile(R.KREF_PATH, os.path.join(d, 'kref.tsv'))
    return d


def main():
    print('suite regress_f30f.py sha256 %s target f30f_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(R.__file__)))
    ok = True
    n = 0
    nf = 0

    def chk(what, cond):
        nonlocal ok, n, nf
        n += 1
        ok &= bool(cond)
        nf += 0 if cond else 1
        print('%s %s' % ('PASS' if cond else 'FAIL', what))

    for name in LOGS:
        print('log %s sha256 %s' % (name, sha(LOGS[name])))
    k3 = mkdir('k3k127', LOGS['k3k127'])
    s3 = mkdir('s3s127', LOGS['s3s127'])
    fv = mkdir('fs10_v', LOGS['fs10_v'])
    # (1) default fields
    r = R.read_tag('f30_s1_v', R.paths('f30_s1_v', k3))
    rc4 = [b for a, b in r['admission'] if a.startswith('RC4 ')]
    chk('k3k127 default: NOT_ADMITTED (%s)' % r['status'], r['status'] == 'NOT_ADMITTED')
    chk('k3k127 default: RC4 row NO - missing field (%s)' % rc4, rc4 == [False])
    chk('k3k127 default: no sums from lines with a missing field (proc rts_chk %s)' % r['proc']['rts_chk'], r['proc']['rts_chk'] == 0)
    r = R.read_tag('f30_s1_c3', R.paths('f30_s1_c3', s3))
    rc4 = [b for a, b in r['admission'] if a.startswith('RC4 ')]
    chk('s3s127 default: NOT_ADMITTED, RC4 NO (%s %s)' % (r['status'], rc4), r['status'] == 'NOT_ADMITTED' and rc4 == [False])
    # (2) legacy fields
    r = R.read_tag('f30_s1_v', R.paths('f30_s1_v', k3), legacy=True)
    P, W = r['proc'], r['win']
    print('k3k127 legacy proc %s' % json.dumps(dict((k, P[k]) for k in ('rts_n', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_race'))))
    print('k3k127 legacy win %s bda %s' % (json.dumps(dict((k, W[k]) for k in ('rts_n', 'rts_chk', 'rts_chk_b', 'rts_bad'))),
                                           json.dumps(r['bda'], sort_keys=True)))
    chk('k3k127 legacy: process rts_chk 39 814 684 = F30a (%d)' % P['rts_chk'], P['rts_chk'] == 39814684)
    chk('k3k127 legacy: process rts_chk_b 39 362 713 = F30a (%d)' % P['rts_chk_b'], P['rts_chk_b'] == 39362713)
    chk('k3k127 legacy: process rts_bad 0, RtSkipVerify 0 (%d, %d)' % (P['rts_bad'], r['verify_lines']), P['rts_bad'] == 0 and r['verify_lines'] == 0)
    mem = dict((a.split(' ')[0], b) for a, b in r['members'])
    chk('k3k127 legacy: (C1) YES, (V) YES, race YES (%s)' % mem, mem.get('(C1)') and mem.get('(V)') and mem.get('race:'))
    chk('k3k127 legacy: (O) NO - entry NEW (%s, mean %s)' % (r['bda']['mode'], r['bda']['mean_read']), r['bda']['mode'] == 'NEW' and mem.get('(O)') is False)
    adm = dict((a.split(' ')[0], b) for a, b in r['admission'])
    chk('k3k127 legacy: (D1) one mode 2 YES, (D2) YES, (D3) gate 2 YES, (D4) YES, (D5) YES, (D6) YES (%s)' % dict(
        (k, adm.get(k)) for k in ('(D1)', '(D2)', '(D3)', '(D4)', '(D5)', '(D6)')),
        all(adm.get(k) for k in ('(D1)', '(D2)', '(D3)', '(D4)', '(D5)', '(D6)')))
    chk('k3k127 legacy: (D7) NO - not T (%s)' % adm.get('(D7)'), adm.get('(D7)') is False)
    chk('k3k127 legacy: parse row YES (prefix sums; per-line letter tears: %s)' % [z for z, b in r['admission'] if z.startswith('parse')][0][-70:],
        adm.get('parse') is True)
    chk('k3k127 legacy: kappa ALL %s inside [0.80; 1.25]' % r['kappa']['by']['ALL'], r['kappa']['by']['ALL']['inside'])
    chk('k3k127 legacy: no STOP (%s)' % r['stop'], r['stop'] == [])
    prow = [z for z, b in r['admission'] if z.startswith('parse')][0]
    chk('k3k127 legacy: item 651 (v)(1) - parse PASS with the letter tears 140 / 130, max prefix deviation 1 / 1 (%s)' % prow[-150:],
        adm.get('parse') is True and 'chk!=pa 140, chk_b!=pb 130' in prow and '"chk_pa": 1' in prow and '"chkb_pb": 1' in prow)
    r = R.read_tag('f30_s1_c3', R.paths('f30_s1_c3', s3), legacy=True)
    P = r['proc']
    print('s3s127 legacy proc %s bits %s bda %s' % (json.dumps(dict((k, P[k]) for k in ('rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_race'))),
                                                     r['mm_bits'], r['bda']['mode']))
    chk('s3s127 legacy: process rts_bad 1 121 276 = F30a (%d)' % P['rts_bad'], P['rts_bad'] == 1121276)
    chk('s3s127 legacy: 40 RtSkipVerify lines, bits 0x401 / 0x405 (%d %s)' % (r['verify_lines'], r['mm_bits']),
        r['verify_lines'] == 40 and r['mm_bits'] == ['0x401', '0x405'])
    mem = dict((a.split(' ')[0], b) for a, b in r['members'])
    chk("s3s127 legacy: (K) YES, (K') YES, race YES (%s)" % mem, mem.get('(K)') and mem.get("(K')") and mem.get('race:'))
    adm = dict((a.split(' ')[0], b) for a, b in r['admission'])
    chk('s3s127 legacy: (D3) NO - ABBA gate lines 0 and 3 (%s)' % adm.get('(D3)'), adm.get('(D3)') is False)
    chk('s3s127 legacy: (D1) YES - one mode 3 line (%s)' % adm.get('(D1)'), adm.get('(D1)') is True)
    prow = [z for z, b in r['admission'] if z.startswith('parse')][0]
    chk('s3s127 legacy: parse YES (lines 40 <= min(40, bad)), letter tears 34 / 32 (%s)' % prow[-150:], adm.get('parse') is True
        and 'chk!=pa 34, chk_b!=pb 32' in prow and r['stop'] == [])
    chk('s3s127 legacy: BDA OLD (%s)' % r['bda']['mode'], r['bda']['mode'] == 'OLD')
    # (3) fs10_v
    r = R.read_tag('f30_s1_v', R.paths('f30_s1_v', fv))
    rc4 = [a for a, b in r['admission'] if a.startswith('RC4 ') and not b]
    adm = dict((a.split(' ')[0], b) for a, b in r['admission'])
    chk('fs10_v default: NOT_ADMITTED by RC4 missing field (%s %s)' % (r['status'], rc4[:1]), r['status'] == 'NOT_ADMITTED' and len(rc4) == 1)
    chk('fs10_v default: (D1) NO - mode 1 (%s)' % adm.get('(D1)'), adm.get('(D1)') is False)
    d7 = [z for z, b in r['admission'] if z.startswith('(D7)')][0]
    chk('fs10_v: (D7) NO - log line version: Fork build ... dc5d471, not a1d1d86 (item 649 (zh)) %s' % d7[:200],
        adm.get('(D7)') is False and "['dc5d471']" in d7)
    b42 = r['b42']
    print('fs10_v FixB42 window %s' % json.dumps(b42, sort_keys=True)[:400])
    chk('fs10_v: FixB42 lines read (%d) and window increments >= 0 (%s)' % (b42['lines'], b42['inc']), b42['lines'] > 0 and min(b42['inc'].values()) >= 0)
    print('checks %d failed %d' % (n, nf))
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
