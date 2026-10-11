"""F38c (HPP-765): regression of f38c_read.py on the real artefacts of the nearest form (read-only):
  fs12_v (FS12c, binary FS12 46892c20, no KYTY_FIX_*, installed FS11 ea51ae80)   read as f25_v
Expected: admission FAILS exactly on 4 members - json binary_sha256, installed during the tag, installed before = after (FS11, not FS12),
env (missing KYTY_FIX_F25) - and nothing else (the seal of the source is given, so prereg holds; no KYTY_TEST_*, 0 ExitFatal: lines); the
members read on the same log (members() called directly): every member of both groups YES except 'FixF25: mode=1' (no line in FS12 -
a live member); the F25 rows of the FS12 log ('FixF25: read failed twice' 0 - no such line in FS12; 'KernelRead: direct read failed' -
printed).  Last line ALL OK.  ASCII only.
usage: python regress_f38c.py [<f38c_read.py>]"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f38c_read.py')
_spec = importlib.util.spec_from_file_location('f38c_read_r', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_f38c.py sha256 %s target f38c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
root = 'C:/kyty/f287/fs12c'
D = root + '/runs/fs12_v'
p = dict(installed_before=D + '/installed_before.txt', installed_after=D + '/installed_after.txt', manifest_cmp=D + '/manifest_cmp.txt',
         glitch=D + '/glitch.txt', installed_sha=D + '/installed_sha.txt', level=D + '/level.txt', sheet=D + '/sheet.txt',
         log=root + '/log_fs12_v.txt', stdout=root + '/stdout_fs12_v.txt', run=root + '/fs12_v.json', idx=root + '/rec_fs12_v.mp4.idx',
         seal=root + '/pred/fs12c_seal.md', bin='C:/kyty/f287/bin/kyty_emulator_46892c20.exe')
want = ('json binary_sha256', 'installed during the tag', 'installed before = after', 'env = the form')
ok = True
r = R.read_tag('f25_v', p)
bad = [a for a, b in r['admission'] if not b]
print('f25_v (from log_fs12_v.txt): admission failed members %d' % len(bad))
for a in bad:
    print('  NO %s' % a)
c = r['status'] == 'NOT_ADMITTED' and len(bad) == len(want) and all(any(a.startswith(w) for a in bad) for w in want)
c = c and any('missing KYTY_FIX_F25' in a for a in bad) and any('ea51ae80' in a for a in bad)
print('  admission as expected: %s' % c)
ok &= c
x = R.scan(p['log'])
att = json.load(open(p['run']))['attempts'][-1]
idx_n = sum(1 for _ in open(p['idx'], 'rb'))
mg = R.RX_GL.search(open(p['glitch']).read())
gl = int(mg.group(1)) if mg else None
so = R.stdout_scan(p['stdout'])
m, f, info = R.members(x, att, idx_n, gl, 'sheet', so)
for a, b in m + f:
    print('  [%s] %s' % ('YES' if b else 'NO', a[:150]))
mno = [a for a, b in m + f if not b]
c = len(mno) == 1 and mno[0].startswith('FixF25: mode=1') and len(m) == 8 and len(f) == 11
print('  members as expected (only FixF25: mode=1 NO): %s' % c)
ok &= c
fr = r['f25_rows']
print('  F25 rows of the FS12 log: read failed twice log %s stdout %s; direct read failed log %s stdout %s; FixF25 mode lines %s' % (
    fr['read_failed_twice_log'], fr['read_failed_twice_stdout'], fr['direct_read_failed_log'], fr['direct_read_failed_stdout'],
    fr['f25_mode_lines']))
c = fr['read_failed_twice_log'] == 0 and fr['read_failed_twice_stdout'] == 0 and fr['f25_mode_lines'] == 0
print('  F25 rows as expected (no FixF25 line in FS12): %s; ExitFatal: log %d stdout %s; close_rc %s close_s %s' % (
    c, x['stand'], so['stand'], r['exit']['close_rc'], r['exit']['close_s']))
ok &= c and x['stand'] == 0 and so['stand'] == 0
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
