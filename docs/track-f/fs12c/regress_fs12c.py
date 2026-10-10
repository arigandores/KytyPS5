"""FS12c (HPP-752): regression of fs12c_read.py on real artefacts of the nearest forms (read-only):
  f21_v  (F33e, binary 2b393af8 = F33c, the path =1 of Ph21 by KYTY_FIX_F21=1)  read as fs12_v
  fs11_w (FS11c, binary ea51ae80, installed FS10)                             read as fs12_w
  fs11_z (FS11c, binary ea51ae80, KYTY_FIX_B12=0, installed FS10)              read as fs12_z
Expected: admission FAILS exactly on the binary / install members (the seal of each source is given, so prereg holds) and on the env (named below), nothing else (in particular the
item 686 (v) members - no KYTY_TEST_*, 0 ExitFatal: lines - hold on all three); the members read on the same log (members() called
directly): f21_v - every member of both groups YES; fs11_w - every member YES except 'FixF21: mode=1' (no line on FS11); fs11_z - every
member YES except 'FixF21: mode=0' (no line on FS11).  Last line ALL OK.  ASCII only.
usage: python regress_fs12c.py [<fs12c_read.py>]"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fs12c_read.py')
_spec = importlib.util.spec_from_file_location('fs12c_read_r', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_fs12c.py sha256 %s target fs12c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))


def paths(root, tag, seal, binp):
    D = root + '/runs/' + tag
    return dict(installed_before=D + '/installed_before.txt', installed_after=D + '/installed_after.txt', manifest_cmp=D + '/manifest_cmp.txt',
                glitch=D + '/glitch.txt', installed_sha=D + '/installed_sha.txt', level=D + '/level.txt', sheet=D + '/sheet.txt',
                log=root + '/log_%s.txt' % tag, stdout=root + '/stdout_%s.txt' % tag, run=root + '/%s.json' % tag,
                idx=root + '/rec_%s.mp4.idx' % tag, seal=seal, bin=binp)


CASES = [
    ('fs12_v', paths('C:/kyty/f287/f33e', 'f21_v', 'C:/kyty/f287/f33e/pred/f33e_seal.md', 'C:/kyty/f287/bin/kyty_emulator_2b393af8.exe'),
     ('json binary_sha256', 'installed during the tag', 'env = the form'), 'extra KYTY_FIX_F21=1', None),
    ('fs12_w', paths('C:/kyty/f287/fs11c', 'fs11_w', 'C:/kyty/f287/fs11c/pred/fs11c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe'),
     ('json binary_sha256', 'installed during the tag', 'installed before = after'), None, 'FixF21: mode=1'),
    ('fs12_z', paths('C:/kyty/f287/fs11c', 'fs11_z', 'C:/kyty/f287/fs11c/pred/fs11c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe'),
     ('json binary_sha256', 'installed during the tag', 'installed before = after', 'env = the form'), 'missing KYTY_FIX_F21',
     'FixF21: mode=0'),
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
    c = (not mno) if fails is None else (len(mno) == 1 and mno[0].startswith(fails))
    print('  members as expected: %s; ExitFatal: log %d stdout %s; close_rc %s close_s %s quit_ln %s' % (
        c, x['stand'], so['stand'], r['exit']['close_rc'], r['exit']['close_s'], r['exit']['quit_ln']))
    ok &= c and x['stand'] == 0 and so['stand'] == 0
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
