"""FS13c (HPP-789): regression of fs13c_read.py on real artefacts of the nearest forms (read-only):
  f25_v  (F38c, binary 5a14a111 = F38a, KYTY_FIX_F25=1, installed FS12 46892c20)   read as fs13_v
  fs12_v (FS12c, binary 46892c20 = FS12, installed FS11)                         read as fs13_v
  fs12_w (FS12c, binary 46892c20, installed FS11)                                read as fs13_w
  fs12_z (FS12c, binary 46892c20, KYTY_FIX_F21=0, installed FS11)                read as fs13_z
Expected: admission FAILS exactly on the binary / install members (the seal of each source is given, so prereg holds) and on the env (named
below), nothing else; the members read on the same log (members() called directly): f25_v - every member of both groups YES (the path =1
of F25 with the other FS12 defaults - the closest positive control of the letter); fs12_v / fs12_w - every member YES except
'FixF25: mode=1' (no line on FS12); fs12_z - every member YES except 'FixF25: mode=0' (no line on FS12).  Last line ALL OK.  ASCII only.
Port of C:/kyty/f287/fs12c/regress_fs12c.py.
usage: python regress_fs13c.py [<fs13c_read.py>]"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fs13c_read.py')
_spec = importlib.util.spec_from_file_location('fs13c_read_r', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_fs13c.py sha256 %s target fs13c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))


def paths(root, tag, seal, binp):
    D = root + '/runs/' + tag
    return dict(installed_before=D + '/installed_before.txt', installed_after=D + '/installed_after.txt', manifest_cmp=D + '/manifest_cmp.txt',
                glitch=D + '/glitch.txt', installed_sha=D + '/installed_sha.txt', level=D + '/level.txt', sheet=D + '/sheet.txt',
                log=root + '/log_%s.txt' % tag, stdout=root + '/stdout_%s.txt' % tag, run=root + '/%s.json' % tag,
                idx=root + '/rec_%s.mp4.idx' % tag, seal=seal, bin=binp)


F12 = ('C:/kyty/f287/fs12c', 'C:/kyty/f287/fs12c/pred/fs12c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_46892c20.exe')
CASES = [
    ('fs13_v', paths('C:/kyty/f287/f38c', 'f25_v', 'C:/kyty/f287/f38c/pred/f38c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_5a14a111.exe'),
     ('json binary_sha256', 'installed during the tag', 'env = the form'), 'extra KYTY_FIX_F25=1', None),
    ('fs13_v', paths(F12[0], 'fs12_v', F12[1], F12[2]),
     ('json binary_sha256', 'installed during the tag', 'installed before = after'), None, 'FixF25: mode=1'),
    ('fs13_w', paths(F12[0], 'fs12_w', F12[1], F12[2]),
     ('json binary_sha256', 'installed during the tag', 'installed before = after'), None, 'FixF25: mode=1'),
    ('fs13_z', paths(F12[0], 'fs12_z', F12[1], F12[2]),
     ('json binary_sha256', 'installed during the tag', 'installed before = after', 'env = the form'), 'missing KYTY_FIX_F25',
     'FixF25: mode=0'),
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
    fr = r['f25_rows']
    print('  members as expected: %s; F25 rows read failed twice %s / %s, direct read failed %s / %s; close_rc %s close_s %s quit_ln %s' % (
        c, fr['read_failed_twice_log'], fr['read_failed_twice_stdout'], fr['direct_read_failed_log'], fr['direct_read_failed_stdout'],
        r['exit']['close_rc'], r['exit']['close_s'], r['exit']['quit_ln']))
    ok &= c and x['stand'] == 0 and so['stand'] == 0
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
