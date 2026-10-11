"""FS14c (HPP-814): regression of fs14c_read.py on real artefacts of the nearest forms (read-only):
  f24_n1 (F40c, binary ddf0ca91 = F40a2 on FS12, KYTY_FIX_F24=1, installed FS13 abab2196)   read as fs14_v
  f29_v  (F44c, binary d760708d = F44a on FS12, KYTY_FIX_F29=1, installed FS13 abab2196)    read as fs14_v
  fs13_v (FS13c, binary abab2196 = FS13, installed FS12)                                  read as fs14_v
  fs13_w (FS13c, binary abab2196, installed FS12)                                         read as fs14_w
  fs13_z (FS13c, binary abab2196, KYTY_FIX_F25=0, installed FS12)                         read as fs14_z
Expected: admission FAILS exactly on the binary / install members (the seal of each source is given, so prereg holds) and on the env (named
below), nothing else; the members read on the same log (members() called directly) fail exactly on the named set: f24_n1 - FixF25: mode=1
(no line on FS12) and FixF29: mode=1 (no line before F44a) - every F24 member YES (the path =1 of F24: the closest positive control of the
F24 letter); f29_v - the four F24 members (no line before F40a) and FixF25: mode=1 - FixF29: mode=1 YES (positive control of the F29
letter); fs13_v / fs13_w - the F24 and F29 members only (FixF25 YES); fs13_z - FixF24: mode=0 and FixF29: mode=0 only (other FixF24 /
FixF29 lines 0 - YES).  Last line ALL OK.  ASCII only.  Port of C:/kyty/f287/fs13c/regress_fs13c.py.
usage: python regress_fs14c.py [<fs14c_read.py>]"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fs14c_read.py')
_spec = importlib.util.spec_from_file_location('fs14c_read_r', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_fs14c.py sha256 %s target fs14c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
_SCAN = R.scan
_MEMO = {}


def _scan_once(path):
    # one pass per log: read_tag and members() below read the same scan (the reader is not changed)
    if path not in _MEMO:
        _MEMO[path] = _SCAN(path)
    return _MEMO[path]


R.scan = _scan_once


def paths(root, tag, seal, binp):
    D = root + '/runs/' + tag
    return dict(installed_before=D + '/installed_before.txt', installed_after=D + '/installed_after.txt', manifest_cmp=D + '/manifest_cmp.txt',
                glitch=D + '/glitch.txt', installed_sha=D + '/installed_sha.txt', level=D + '/level.txt', sheet=D + '/sheet.txt',
                log=root + '/log_%s.txt' % tag, stdout=root + '/stdout_%s.txt' % tag, run=root + '/%s.json' % tag,
                idx=root + '/rec_%s.mp4.idx' % tag, seal=seal, bin=binp)


F13 = ('C:/kyty/f287/fs13c', 'C:/kyty/f287/fs13c/pred/fs13c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_abab2196.exe')
B2 = ('json binary_sha256', 'installed during the tag')
B3 = B2 + ('installed before = after',)
F24V = ('FixF24: mode=1 b24=1', 'FixF24: init before', 'FixF24: init_owner exactly 1', 'FixF24: init_owner hid =')
CASES = [
    ('fs14_v', paths('C:/kyty/f287/f40c', 'f24_n1', 'C:/kyty/f287/f40c/pred/f40c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_ddf0ca91.exe'),
     B2 + ('env = the form',), 'extra KYTY_FIX_F24=1', ('FixF25: mode=1', 'FixF29: mode=1')),
    ('fs14_v', paths('C:/kyty/f287/f44c', 'f29_v', 'C:/kyty/f287/f44c/pred/f44c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_d760708d.exe'),
     B2 + ('env = the form',), 'extra KYTY_FIX_F29=1', F24V + ('FixF25: mode=1',)),
    ('fs14_v', paths(F13[0], 'fs13_v', F13[1], F13[2]), B3, None, F24V + ('FixF29: mode=1',)),
    ('fs14_w', paths(F13[0], 'fs13_w', F13[1], F13[2]), B3, None, ('FixF24: mode=1 b24=1', 'FixF29: mode=1')),
    ('fs14_z', paths(F13[0], 'fs13_z', F13[1], F13[2]), B3 + ('env = the form',), 'missing KYTY_FIX_F24',
     ('FixF24: mode=0 b24=1', 'FixF29: mode=0')),
]
ok = True
for tag, p, want, envword, fails in CASES:
    r = R.read_tag(tag, p)
    bad = [a for a, b in r['admission'] if not b]
    print('%s (from %s): admission failed members %d' % (tag, os.path.basename(p['log']), len(bad)))
    for a in bad:
        print('  NO %s' % a)
    c = r['status'] == 'NOT_ADMITTED' and len(bad) == len(want) and all(any(a.startswith(w) for a in bad) for w in want)
    if envword:
        c = c and any(envword in a for a in bad)
    print('  admission as expected: %s' % c)
    ok &= c
    x = R.scan(p['log'])
    att = json.load(open(p['run']))['attempts'][-1]
    idx_n = sum(1 for _ in open(p['idx'], 'rb')) if os.path.exists(p['idx']) else None
    gt = open(p['glitch']).read() if os.path.exists(p['glitch']) else ''
    mg = R.RX_GL.search(gt)
    gl = int(mg.group(1)) if mg else None
    so = R.stdout_scan(p['stdout'])
    m, f, info = R.members(r['kind'], x, att, idx_n, gl, 'sheet', so)
    for a, b in m + f:
        print('  [%s] %s' % ('YES' if b else 'NO', a[:150]))
    mno = [a for a, b in m + f if not b]
    c = len(mno) == len(fails) and all(any(a.startswith(w) for a in mno) for w in fails)
    f24, f29, fr = r['f24_rows'], r['f29_rows'], r['f25_rows']
    print('  members as expected: %s (failed %d, want %d); F24 rows pump_update_long %s open failed %s Controller %s pump_stop_expired %s / %s; '
          'F29 rows overflow %s / %s accessed %s / %s; F25 rows %s / %s, %s / %s; close_rc %s close_s %s quit_ln %s' % (
              c, len(mno), len(fails), f24['pump_update_long'], f24['open_failed'], f24['controller_lines'], f24['pump_stop_expired_log'],
              f24['pump_stop_expired_stdout'], f29['overflow_log'], f29['overflow_stdout'], f29['accessed_log'], f29['accessed_stdout'],
              fr['read_failed_twice_log'], fr['read_failed_twice_stdout'], fr['direct_read_failed_log'], fr['direct_read_failed_stdout'],
              r['exit']['close_rc'], r['exit']['close_s'], r['exit']['quit_ln']))
    ok &= c and x['stand'] == 0 and so['stand'] == 0 and x['hidloss'] == 0
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
