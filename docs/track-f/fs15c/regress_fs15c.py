"""FS15c (HPP-822): regression of fs15c_read.py on real artefacts of the nearest forms (read-only):
  fs14_v (FS14c, binary 013e1974 = FS14, installed FS13 abab2196)                       read as fs15_v
  fs14_w (FS14c, binary 013e1974, installed FS13)                                       read as fs15_w
  fs14_z (FS14c, binary 013e1974, KYTY_FIX_F24=0 KYTY_FIX_F29=0, installed FS13)        read as fs15_z
  f20_v  (F42c, binary 1994a0ce = F42a2 on FS12, KYTY_FIX_F20=1, installed FS14 013e1974) read as fs15_v
  f20_w  (F42c, binary 1994a0ce, KYTY_FIX_F20=1, installed FS14 013e1974)                 read as fs15_w
Expected: admission FAILS exactly on the binary / install members (the seal of each source is given, so prereg holds) and on the env (named
below), nothing else; the members read on the same log (members() called directly) fail exactly on the named set: fs14_v - FixF20: mode=1
and the four FixF20Stat exit members (no line before F42a); fs14_w - FixF20: mode=1 and the three exit members; fs14_z - FixF20: mode=0
only (no line; '0 FixF20Stat: lines' YES); f20_v - the four F24 members, FixF25: mode=1 and FixF29: mode=1 (no lines on FS12) - every
FixF20 member YES (the path =1 of F20 on the same code: the closest positive control of the F20 letter); f20_w - FixF24: mode=1 b24=1
(letter) and FixF29 / FixF25 (form) - FixF20 and the three exit members YES.  The rows of the preparation screen, 'all pipelines created'
and the driver blob are printed.  Last line ALL OK.  ASCII only.  Port of C:/kyty/f287/fs14c/regress_fs14c.py.
usage: python regress_fs15c.py [<fs15c_read.py>]"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fs15c_read.py')
_spec = importlib.util.spec_from_file_location('fs15c_read_r', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_fs15c.py sha256 %s target fs15c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
_SCAN = R.scan
_MEMO = {}


def _scan_once(path):
    # one pass per log: read_tag and members() below read the same scan (the reader is not changed)
    if path not in _MEMO:
        _MEMO[path] = _SCAN(path)
    return _MEMO[path]


R.scan = _scan_once


def paths(root, tag, seal, binp, cb, ca):
    D = root + '/runs/' + tag
    return dict(installed_before=D + '/installed_before.txt', installed_after=D + '/installed_after.txt', manifest_cmp=D + '/manifest_cmp.txt',
                glitch=D + '/glitch.txt', installed_sha=D + '/installed_sha.txt', level=D + '/level.txt', sheet=D + '/sheet.txt',
                log=root + '/log_%s.txt' % tag, stdout=root + '/stdout_%s.txt' % tag, run=root + '/%s.json' % tag,
                idx=root + '/rec_%s.mp4.idx' % tag, seal=seal, bin=binp, cache_before=D + '/' + cb, cache_after=D + '/' + ca)


F14 = ('C:/kyty/f287/fs14c', 'C:/kyty/f287/fs14c/pred/fs14c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_013e1974.exe', 'manifest_before.tsv',
       'manifest_run.tsv')
F42 = ('C:/kyty/f287/f42c', 'C:/kyty/f287/f42c/pred/f42c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_1994a0ce.exe', 'cache_before.tsv',
       'cache_after.tsv')
B2 = ('json binary_sha256', 'installed during the tag')
B3 = B2 + ('installed before = after',)
EX4 = ('FixF20Stat: when=exit line after', 'FixF20Stat exit line: unmatched', 'FixF20Stat exit line: modules_bound', 'FixF20Stat exit line: rewritten')
F24V = ('FixF24: mode=1 b24=1', 'FixF24: init before', 'FixF24: init_owner exactly 1', 'FixF24: init_owner hid =')
CASES = [
    ('fs15_v', paths(F14[0], 'fs14_v', *F14[1:]), B3, None, ('FixF20: mode=1',) + EX4, ()),
    ('fs15_w', paths(F14[0], 'fs14_w', *F14[1:]), B3, None, ('FixF20: mode=1',) + EX4[:3], ()),
    ('fs15_z', paths(F14[0], 'fs14_z', *F14[1:]), B3 + ('env = the form',), 'missing KYTY_FIX_F20', ('FixF20: mode=0',), ()),
    ('fs15_v', paths(F42[0], 'f20_v', *F42[1:]), B2 + ('env = the form',), 'extra KYTY_FIX_F20=1', F24V + ('FixF25: mode=1', 'FixF29: mode=1'),
     ('FixF20: mode=1',) + EX4),
    ('fs15_w', paths(F42[0], 'f20_w', *F42[1:]), B2 + ('env = the form',), 'extra KYTY_FIX_F20=1', ('FixF24: mode=1 b24=1', 'FixF29: mode=1',
                                                                                                   'FixF25: mode=1'),
     ('FixF20: mode=1',) + EX4[:3]),
]
ok = True
for tag, p, want, envword, fails, yes in CASES:
    r = R.read_tag(tag, p)
    bad = [a for a, b in r['admission'] if not b]
    print('%s (from %s): admission failed members %d' % (tag, os.path.basename(p['log']), len(bad)))
    for a in bad:
        print('  NO %s' % a[:160])
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
    cy = all(any(a.startswith(w) and b for a, b in m + f) for w in yes)
    f2 = r['f20_rows']
    print('  members as expected: %s (failed %d, want %d); named YES %s; F20 rows: prep %s, all pipelines created %s, _PipelineCache %s -> %s, '
          'FixF20Stat lines %s exit %s; close_rc %s close_s %s quit_ln %s' % (
              c, len(mno), len(fails), cy, f2['prep_ms'], f2['all_pipelines_created_ms'], f2['blob_pipelinecache_before'],
              f2['blob_pipelinecache_after'], f2['f20stat_lines'], json.dumps(f2['f20stat_exit'], sort_keys=True), r['exit']['close_rc'],
              r['exit']['close_s'], r['exit']['quit_ln']))
    ok &= c and cy and x['stand'] == 0 and so['stand'] == 0 and x['hidloss'] == 0
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
