"""F46c (HPP-800): the reader f46c_read.py and the frame table of f46c_vid.py on REAL files of earlier tags (read only):
  fs12_v (FS12c, FS12 46892c20, no KYTY_DIAG_F5 / KYTY_DCC_TRACE) as f26s_0: NOT_ADMITTED (binary, installed, env, no DiagF5 lines -
      identity, keys not found as dcc_stale lines); the 4 'stale pending' lines after the entry parse with fill / size = FS12 keys (4 of 4),
      14 before the entry (F45a scan_f45a.txt), 0 skipped draw.
  f26_1 of F16q (binary 7e4ded19, enemy_final, older line formats) as f26s_1: NOT_ADMITTED (level, binary); DiagF5 lines unparsable
      (two counters fewer than F46a) - the identity member says it; FixF26 member YES.
  f29_v of F44c (Sky Garden video, 10 113 frames): frames table - size 960x540, M max < 500 on every frame (natural Sky Garden pixels do
      not pass the detector), entry-screen frames counted.
Prints rows and ALL OK when every expectation holds.  ASCII only.
usage: python regress_f46c.py"""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


R = load('f46c_read')
V = load('f46c_vid')
print('regress_f46c.py sha256 %s reader %s vid %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'f46c_read.py')),
                                                      sha(os.path.join(HERE, 'f46c_vid.py'))))
ok = True


def row(name, cond, info=''):
    global ok
    ok &= bool(cond)
    print('%-4s %s %s' % ('ok' if cond else 'FAIL', name, info))


def paths(d, tag, js, log, so, idx):
    p = dict((nm, os.path.join(d, 'runs', tag, nm + '.txt')) for nm in ('installed_before', 'installed_after', 'manifest_cmp', 'glitch',
                                                                         'installed_sha', 'level', 'sheet'))
    p.update(log=log, stdout=so, run=js, idx=idx, seal=os.path.join(d, 'pred', 'none.md'), bin='C:/kyty/f287/bin/none.exe')
    return p


F = 'C:/kyty/f287/fs12c'
r = R.read_tag('f26s_0', paths(F, 'fs12_v', F + '/fs12_v.json', F + '/log_fs12_v.txt', F + '/stdout_fs12_v.txt', F + '/rec_fs12_v.mp4.idx'))
ev = r['events']
row('fs12_v as f26s_0: NOT_ADMITTED', r['status'] == 'NOT_ADMITTED', r['failed'][:3])
row('fs12_v: stale lines before / after the entry = 14 / 4', r['rows']['stale_lines_before'] == 14 and r['rows']['stale_lines_after'] == 4,
    (r['rows']['stale_lines_before'], r['rows']['stale_lines_after']))
row('fs12_v: each S key has 1 stale line after the entry with fill / size = FS12 keys', all(e['stale_lines'] == 1 and e['stale_fill_size_ok']
                                                                                          for e in ev), [(e['label'], e['stale_lines']) for e in ev])
row('fs12_v: keys not found as dcc_stale lines (no KYTY_DIAG_F5)', not any(e['found'] for e in ev))
row('fs12_v: 0 skipped draw member YES', any(a.startswith("702 (g)(4): 0 'skipped draw'") and b for a, b in r['admission']))
row('fs12_v: hold >= 300 s member YES', any(a.startswith('702 (g)(4): hold >= 300') and b for a, b in r['admission']), r['info']['hold_s'])
row('fs12_v: env differs (KYTY_FIX_F26 / DIAG / DCC_TRACE missing)', any(a.startswith('env =') and not b for a, b in r['admission']))
Q = 'C:/kyty/f287/f16q'
r = R.read_tag('f26s_1', paths(Q, 'f26_1', Q + '/f26_1.json', Q + '/log_f26_1.txt', Q + '/stdout_f26_1.txt', Q + '/rec_f26_1.mp4.idx'))
row('f16q f26_1 as f26s_1: NOT_ADMITTED, entry line absent (enemy_final)', r['status'] == 'NOT_ADMITTED' and
    any(a.startswith('entry line') and not b for a, b in r['admission']))
row('f16q f26_1: FixF26 member YES', any("'FixF26: mode=1'" in a and b for a, b in r['admission']))
row('f16q f26_1: identity member NO (DiagF5 lines of the older binary unparsable)', any(a.startswith('702 (g)(4): identity: every DiagF5') and not b
                                                                                    for a, b in r['admission']))
t = V.frames_table('C:/kyty/f287/f44c/rec_f29_v.mp4', 'C:/kyty/f287/f44c/rec_f29_v.mp4.idx')
ms = [x[1] for x in t['rows']]
row('f29_v frames: size 960x540, rows = idx records', tuple(t['size']) == (960, 540) and len(t['rows']) == t['idx_records'], (t['size'], len(t['rows'])))
row('f29_v frames: M max < 500 (natural Sky Garden)', max(ms) < 500, 'M max %d, frames M > 0: %d, entry-screen frames %d' % (
    max(ms), sum(1 for m in ms if m > 0), sum(1 for x in t['rows'] if x[2] <= 5)))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
