"""F44c (HPP-793): regression of f44c_read.py on the real artefacts of the nearest form (read-only), two sources:
  fs12_v (FS12c, binary FS12 46892c20, no KYTY_FIX_*, installed FS11 ea51ae80)               read as f29_v
  f25_v  (F38c, binary F38a 5a14a111, KYTY_FIX_F25=1, installed FS12 46892c20)               read as f29_v
Expected for each: admission FAILS exactly on 4 members - json binary_sha256, installed during the tag, installed before = after (not
FS13), env (missing KYTY_FIX_F29; f25_v also extra KYTY_FIX_F25) - and nothing else (the seal of the source is given, so prereg holds; no
KYTY_TEST_*, 0 ExitFatal: lines); the members read on the same log (members() called directly): every member of both groups YES except
'FixF29: mode=1' (no line in FS12 / F38a - a live member); the F29 rows ('FixF29: overflow' 0 - no such line before F44a; 'Accessed
non-GPU cached memory' - printed, log and stdout).  Last line ALL OK.  ASCII only.
usage: python regress_f44c.py [<f44c_read.py>]"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f44c_read.py')
_spec = importlib.util.spec_from_file_location('f44c_read_r', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_f44c.py sha256 %s target f44c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
SOURCES = (
    ('fs12_v', 'C:/kyty/f287/fs12c', 'pred/fs12c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_46892c20.exe', 'ea51ae80', None),
    ('f25_v', 'C:/kyty/f287/f38c', 'pred/f38c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_5a14a111.exe', '46892c20', 'extra KYTY_FIX_F25=1'),
)
want = ('json binary_sha256', 'installed during the tag', 'installed before = after', 'env = the form')
ok = True
for tag, root, seal, binp, inst, extra in SOURCES:
    D = root + '/runs/' + tag
    p = dict(installed_before=D + '/installed_before.txt', installed_after=D + '/installed_after.txt', manifest_cmp=D + '/manifest_cmp.txt',
             glitch=D + '/glitch.txt', installed_sha=D + '/installed_sha.txt', level=D + '/level.txt', sheet=D + '/sheet.txt',
             log=root + '/log_%s.txt' % tag, stdout=root + '/stdout_%s.txt' % tag, run=root + '/%s.json' % tag,
             idx=root + '/rec_%s.mp4.idx' % tag, seal=root + '/' + seal, bin=binp)
    r = R.read_tag('f29_v', p)
    bad = [a for a, b in r['admission'] if not b]
    print('f29_v (from log_%s.txt): admission failed members %d' % (tag, len(bad)))
    for a in bad:
        print('  NO %s' % a)
    c = r['status'] == 'NOT_ADMITTED' and len(bad) == len(want) and all(any(a.startswith(w) for a in bad) for w in want)
    c = c and any('missing KYTY_FIX_F29' in a for a in bad) and any(inst in a for a in bad)
    if extra:
        c = c and any(extra in a for a in bad)
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
    c = len(mno) == 1 and mno[0].startswith('FixF29: mode=1') and len(m) == 8 and len(f) == 11
    print('  members as expected (only FixF29: mode=1 NO): %s' % c)
    ok &= c
    fr = r['f29_rows']
    print('  F29 rows of the %s log: FixF29: overflow log %s stdout %s; Accessed non-GPU cached memory log %s stdout %s; FixF29 mode lines %s'
          % (tag, fr['overflow_log'], fr['overflow_stdout'], fr['accessed_log'], fr['accessed_stdout'], fr['f29_mode_lines']))
    print('  first accessed line: %s' % fr['accessed_first'])
    c = fr['overflow_log'] == 0 and fr['overflow_stdout'] == 0 and fr['f29_mode_lines'] == 0 and fr['accessed_log'] is not None
    print('  F29 rows as expected (no FixF29 line before F44a): %s; ExitFatal: log %d stdout %s; close_rc %s close_s %s' % (
        c, x['stand'], so['stand'], r['exit']['close_rc'], r['exit']['close_s']))
    ok &= c and x['stand'] == 0 and so['stand'] == 0
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
