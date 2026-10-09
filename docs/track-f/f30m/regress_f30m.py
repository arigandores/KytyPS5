"""Track F link F30m (HPP-723; ROADMAP s122 item 655 (e)(5)): the reader f30m_read.py on real logs - the F30f series on the binary T
(3bc7ada7, no T2 fields rts_bad_r .. rts_bad_l): s1 c3 / c4 / v and s9 c4 (C:/kyty/f287/f30f/log_<tag>.txt; the F30f reader rows in
C:/kyty/f287/f30f/runs/<tag>/read.json are the reference numbers).
  (1) default fields: every T line lacks the 8 bit counters -> NOT_ADMITTED, the RC4 row NO (missing field, not 0), no sums;
  (2) --legacy-fields (regression only): the process sums of the shared fields = the F30f rows exactly; read as a c5 tag the c4 log has
      (D1) NO (mode 4, not 5), 'PB item 6 dropped' NO (rts_xb_pass > 0 - PB item 6 applied at =4), (D7) NO (binary T, not T2);
  (3) the cy kinds on the F30f logs of s1 with the scene cy pointed at Sky Garden in this process only (SCENES patched here, never in a
      tag): f30_cy_c3 on f30_s1_c3 - (K) YES, (K') YES, 40 lines; f30_cy_v on f30_s1_v - (gamma) NO (rts_xb_ser 0, the F30f observation),
      (C1) YES, (V) YES, (O) YES; f30_cy_c4 on f30_s1_c4 - K_B'' NO (sum 0), RC2 (a) YES.
  (4) item 659 (g): the real log of f30_s1_c5 (T2, C:/kyty/f287/f30m/log_f30_s1_c5.txt, read in place with its own side files) - the parse
      member YES under the prefix tolerance 4 (max chk_b/pb deviation 2, one line with deviation >= 2; process sums exact).
First output line: suite <name> sha256 <sha> target f30m_read.py sha256 <sha>.  Ends with ALL OK.  ASCII only.
usage: python regress_f30m.py"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f30m_read as R  # noqa: E402

FX = os.path.join(HERE, 'fx', 'reg')
F30F = 'C:/kyty/f287/f30f'
TAGS = ('f30_s1_c3', 'f30_s1_c4', 'f30_s1_v', 'f30_s9_c4')
SHARED = ('rts_n', 'rts_skip', 'rts_pa', 'rts_pb', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx', 'rts_race',
          'rts_refuse', 'rts_xthr', 'rts_acqw', 'rts_ovf', 'rts_lost', 'rts_xb_ids', 'rts_xb_live', 'rts_xb_meta', 'rts_xb_ser',
          'rts_xb_bound', 'rts_xb_pass')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def mkdir(tag, level, with_side):
    d = os.path.join(FX, tag)
    os.makedirs(d, exist_ok=True)
    src = os.path.join(F30F, 'log_%s.txt' % tag)
    dst = os.path.join(d, 'log.txt')
    if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
        shutil.copyfile(src, dst)
    open(os.path.join(d, 'level.txt'), 'w').write(level + '\n')
    shutil.copyfile(R.KREF_PATH, os.path.join(d, 'kref.tsv'))
    if with_side:
        shutil.copyfile(os.path.join(F30F, '%s.json' % tag), os.path.join(d, 'es.json'))
    return d


def main():
    print('suite regress_f30m.py sha256 %s target f30m_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(R.__file__)))
    ok = True
    n = 0
    nf = 0

    def chk(what, cond):
        nonlocal ok, n, nf
        n += 1
        ok &= bool(cond)
        nf += 0 if cond else 1
        print('%s %s' % ('PASS' if cond else 'FAIL', what))

    ref = {}
    for t in TAGS:
        print('log %s sha256 %s' % (t, sha(os.path.join(F30F, 'log_%s.txt' % t))))
        ref[t] = json.load(open(os.path.join(F30F, 'runs', t, 'read.json'), encoding='utf-8'))
    lv = 'underwater_aerial_garden'
    d = dict((t, mkdir(t, lv, True)) for t in TAGS)
    # (1) default fields
    for t in TAGS:
        as_tag = 'f30_s1_c5' if t != 'f30_s9_c4' else 'f30_s9_c5'
        r = R.read_tag(as_tag, R.paths(as_tag, d[t]))
        rc4 = [b for a, b in r['admission'] if a.startswith('RC4 (F30f)')]
        chk('%s as %s default: NOT_ADMITTED, RC4 row NO, no sums (%s %s proc rts_chk %s)' % (t, as_tag, r['status'], rc4, r['proc']['rts_chk']),
            r['status'] == 'NOT_ADMITTED' and rc4 == [False] and r['proc']['rts_chk'] == 0)
    # (2) legacy fields: shared sums = F30f rows
    for t in TAGS:
        as_tag = 'f30_s1_c5' if t != 'f30_s9_c4' else 'f30_s9_c5'
        r = R.read_tag(as_tag, R.paths(as_tag, d[t]), legacy=True)
        diff = [(k, r['proc'][k], ref[t]['proc'][k]) for k in SHARED if r['proc'][k] != ref[t]['proc'][k]]
        chk('%s legacy: process sums of the 22 shared fields = the F30f row (diff %s)' % (t, diff[:3]), not diff)
        wd = [(k, r['win'][k], ref[t]['win'][k]) for k in SHARED if r['win'][k] != ref[t]['win'][k]]
        chk('%s legacy: window sums = the F30f row (diff %s)' % (t, wd[:3]), not wd)
        chk('%s legacy: RtSkipVerify lines %d = F30f %d' % (t, r['verify_lines'], ref[t]['verify_lines']), r['verify_lines'] == ref[t]['verify_lines'])
        adm = dict((a.split(' ')[0] + ' ' + a.split(' ')[1], b) for a, b in r['admission'])
        if t.endswith('_c4'):
            chk('%s legacy as c5: (D1) NO (mode 4), PB item 6 NO (xb_pass %d > 0), (D7) NO (T, not T2)' % (t, r['proc']['rts_xb_pass']),
                adm.get('(D1) exactly') is False and adm.get('PB item') is False and adm.get('(D7) RC3') is False and r['proc']['rts_xb_pass'] > 0)
            chk('%s legacy as c5: NOT_ADMITTED and an instrument STOP row' % t, r['status'] == 'NOT_ADMITTED' and any('instrument member' in z for z in r['stop']))
    # (3) the cy kinds on the s1 logs, SCENES patched in this process only
    R.SCENES['cy'] = (lv, 300, None)
    r = R.read_tag('f30_cy_c3', R.paths('f30_cy_c3', d['f30_s1_c3']), legacy=True)
    mem = dict((a.split(' ')[0], b) for a, b in r['members'])
    chk("cy_c3 on f30_s1_c3: (K) YES, (K') YES, race YES, 40 lines (%s, %d)" % (mem, r['verify_lines']),
        mem.get('(K)') is True and mem.get("(K')") is True and mem.get('race:') is True and r['verify_lines'] == 40)
    chk('cy_c3 on f30_s1_c3: rts_bad %d = F30f 3 411 459' % r['proc']['rts_bad'], r['proc']['rts_bad'] == 3411459)
    r = R.read_tag('f30_cy_v', R.paths('f30_cy_v', d['f30_s1_v']), legacy=True)
    mem = dict((a.split(' ')[0], b) for a, b in r['members'])
    chk('cy_v on f30_s1_v: (gamma) NO (xb_ser %d), (C1) YES (win chk_b %d), (V) YES, (O) YES (%s)' % (r['proc']['rts_xb_ser'], r['win']['rts_chk_b'], mem),
        mem.get('(gamma)') is False and r['proc']['rts_xb_ser'] == 0 and mem.get('(C1)') is True and mem.get('(V)') is True and mem.get('(O)') is True)
    chk('cy_v on f30_s1_v: window chk_b 40 014 265 = F30f (%d)' % r['win']['rts_chk_b'], r['win']['rts_chk_b'] == 40014265)
    r = R.read_tag('f30_cy_c4', R.paths('f30_cy_c4', d['f30_s1_c4']), legacy=True)
    adm = dict((a.split(' ')[0] + ' ' + a.split(' ')[1], b) for a, b in r['admission'])
    chk("cy_c4 on f30_s1_c4: K_B'' NO (sum %d), RC2 (a) YES" % r['kb2']['sum7'], r['members'][0][1] is False and r['kb2']['sum7'] == 0
        and adm.get('RC2 (a)') is True)
    # (4) item 659 (g): the real log of f30_s1_c5 on T2 - parse YES under the tolerance 4
    rr = R.read_tag('f30_s1_c5', R.paths('f30_s1_c5'))
    pm = [b for a, b in rr['admission'] if a.startswith('parse')]
    md, d2 = rr['ref'].get('prefix_maxdev') or {}, rr['ref'].get('prefix_dev2') or {}
    print('log f30_s1_c5 sha256 %s' % sha(os.path.join(HERE, 'log_f30_s1_c5.txt')))
    chk('f30_s1_c5 real log: parse YES (%s), max chk_b/pb deviation 2 (%s), lines with deviation >= 2: chk_b/pb 1 (%s), sums chk = pa = chk_b = pb'
        ' = 17 474 336 (%s)' % (pm, md.get('chkb_pb'), d2.get('chkb_pb'), rr['proc']['rts_chk']),
        pm == [True] and md.get('chkb_pb') == 2 and d2.get('chkb_pb') == 1 and rr['proc']['rts_chk'] == rr['proc']['rts_pa']
        == rr['proc']['rts_chk_b'] == rr['proc']['rts_pb'] == 17474336)
    print('checks %d failed %d' % (n, nf))
    if ok:
        print('ALL OK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
