"""Track F link F30q (HPP-727; ROADMAP s122 item 664 (z)(5)): the reader f30q_read.py on a real log - the F30m tag f30_s8_c5 on the
binary T2 (bba692c6; KYTY_RT_SKIP=5, no rts_inj fields; C:/kyty/f287/f30m/log_f30_s8_c5.txt with the side files of
C:/kyty/f287/f30m/runs/f30_s8_c5; the F30m reader row C:/kyty/f287/f30m/runs/f30_s8_c5/read.json is the reference).
  (1) every FrameTrace-x line of the T2 log lacks the 5 names rts_inj, rts_inj_s, rts_inj_race, rts_inj_nos, rts_inj_none -> missing field on
      every line, the RC4 (F30f) row NO, status NOT_ADMITTED (not 0, not ADMITTED);
  (2) read as f30_s8_c6: (D1) NO (one line 'RtSkip: mode 5 ctx_slots=.. groups=.. rec_bytes=..', the strict text of the print place matches
      it with the value 5), (D7) NO (launch sha T2, fork 6fbdcf6), json binary_sha256 row NO;
  (3) the scan of the strict mode line: the T2 log has exactly one 'RtSkip: mode' line and it matches the strict form (mode_any = 1,
      modes = [5]) - the print place text did not change between T2 and T3 (item 665 (v)(5));
  (4) the same log with the 5 names appended as 0 on every FrameTrace-x line (a copy in fx/reg_q, this process only): the parse and
      RC1 (F30l) rows YES, the process sums of the shared fields = the F30m read.json rows exactly, RC1-RC4 (F30p) YES with rts_inj 0 and
      the (inj) row NO with the STOP 'code defect' (rts_inj = rts_inj_none = 0, rts_pb >= 4096 - also RC4 (F30p) NO).
First output line: suite <name> sha256 <sha> target f30q_read.py sha256 <sha>.  Ends with ALL OK.  ASCII only.
usage: python regress_f30q.py"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f30q_read as R  # noqa: E402

M = 'C:/kyty/f287/f30m'
TAG = 'f30_s8_c5'
FX = os.path.join(HERE, 'fx', 'reg_q')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_f30q.py sha256 %s target f30q_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(R.__file__)))
N = [0, 0]
ok = True


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)
    else:
        print('ok   %s' % name)
    return bool(cond)


def paths(log):
    d = os.path.join(M, 'runs', TAG)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in ('installed_before', 'installed_after', 'installed_sha', 'level'))
    p.update(log=log, stdout=os.path.join(M, 'stdout_%s.txt' % TAG), run=os.path.join(M, '%s.json' % TAG), seal=R.SEAL_PATH,
             bin=R.BIN_PATH, kref=R.KREF_PATH)
    return p


def row(r, start):
    for a, b in r['admission']:
        if a.startswith(start):
            return b
    return None


ref = json.load(open(os.path.join(M, 'runs', TAG, 'read.json'), encoding='utf-8'))
log = os.path.join(M, 'log_%s.txt' % TAG)
r = R.read_tag('f30_s8_c6', paths(log))
x = R.scan(log, 'big_hand_pirate_island')
ok &= check('(1) every FrameTrace-x line misses a field: lines %d, missing %d; first missing names %s' % (
    x['x_lines'], x['x_missing'], x['x_missing_names'][:1]), x['x_lines'] > 1500 and x['x_missing'] == x['x_lines']
    and set(x['x_missing_names'][0][1]) <= set(R.INJ5))
ok &= check('(1) RC4 (F30f) row NO, status NOT_ADMITTED', row(r, 'RC4 (F30f)') is False and r['status'] == 'NOT_ADMITTED')
ok &= check('(2) (D1) NO (mode 5), (D7) NO, json binary row NO', row(r, '(D1)') is False and row(r, '(D7)') is False
            and row(r, 'json binary_sha256') is False)
ok &= check('(3) one strict mode line, value 5: mode_any %d, modes %s' % (x['mode_any'], x['modes']), x['mode_any'] == 1
            and [v for v, l in x['modes']] == [5])
shutil.rmtree(FX, ignore_errors=True)
os.makedirs(FX)
lq = os.path.join(FX, 'log.txt')
add = b' rts_inj=0 rts_inj_s=0 rts_inj_race=0 rts_inj_nos=0 rts_inj_none=0'
with open(log, 'rb') as fi, open(lq, 'wb') as fo:
    for line in fi:
        if line.startswith(b'FrameTrace-x: n='):
            line = line.rstrip(b'\r\n') + add + b'\n'
        fo.write(line)
r2 = R.read_tag('f30_s8_c6', paths(lq))
shared = [k for k in ref['proc'] if k in r2['proc']]
diff = [k for k in shared if ref['proc'][k] != r2['proc'][k]]
ok &= check('(4) process sums of %d shared fields = F30m read.json (diff %s)' % (len(shared), diff), len(shared) >= 30 and not diff)
ok &= check('(4) parse YES, RC1 (F30l) YES (close distance %s)' % r2['ref']['close_dist'], row(r2, 'parse') is True and row(r2, 'RC1 (F30l)') is True)
ok &= check('(4) RC1-RC3 (F30p) YES, RC4 (F30p) NO (pb %d >= 4096, inj + none 0)' % r2['at_t']['rts_pb'], row(r2, 'RC1 (F30p') is True
            and row(r2, 'RC2 (F30p') is True and row(r2, 'RC3 (F30p') is True and row(r2, 'RC4 (F30p') is False)
ok &= check('(4) (inj) NO and STOP code defect, K_S NO', row(r2, '(inj)') is False and any('code defect' in s for s in r2['stop'])
            and r2['ks'] is False)
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
