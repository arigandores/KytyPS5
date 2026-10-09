"""FS11c (HPP-716): the members of fs11c_read.py on real logs of the same forms - a regression of the parsers, not a reading of FS11.
  b12_v (F29e, cabbd818 at KYTY_FIX_B12=1) as fs11_v: every member YES (FixB12: mode=1 line 718, FixB12Stat: 34 lines, hold 334.2 s, 0
      frames >= 1 s, video 10 622 records / 0 glitches);
  b12_w (F29e) as fs11_w: every member YES ([Vulkan][E] 0, [Vulkan][W] 908 268);
  b12_v as fs11_z: NO exactly in 'FixB12: mode=0' (mode=1) and 'FixB12Stat: lines 0' (34 lines);
  fs10_v (FS10c, abfded5e - no FixB12 code) as fs11_z: NO exactly in 'FixB12: mode=0' (the line is absent); FixB12Stat lines 0 - YES.
ASCII only.  usage: python regress_fs11c.py"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fs11c_read as R  # noqa: E402

RX_GL = re.compile(r'one-frame glitches: (\d+)')
CASES = [('C:/kyty/f287/f29e', 'b12_v', 'fs11_v', []),
         ('C:/kyty/f287/f29e', 'b12_w', 'fs11_w', []),
         ('C:/kyty/f287/f29e', 'b12_v', 'fs11_z', ['FixB12: mode=0', 'FixB12Stat: lines 0']),
         ('C:/kyty/f287/fs10c', 'fs10_v', 'fs11_z', ['FixB12: mode=0'])]
ok = True
print('regress fs11c_read.py sha256 %s' % R.sha_file(R.__file__))
memo = {}
for S, tag, base, want_no in CASES:
    log = os.path.join(S, 'log_%s.txt' % tag)
    if log not in memo:
        memo[log] = R.scan(log)
    x = memo[log]
    run = json.load(open(os.path.join(S, '%s.json' % tag), encoding='utf-8'))
    att = run['attempts'][-1]
    idx = os.path.join(S, 'rec_%s.mp4.idx' % tag)
    idx_n = sum(1 for _ in open(idx, 'rb')) if os.path.exists(idx) else None
    gt = R.text(os.path.join(S, 'runs', tag, 'glitch.txt')) or ''
    mg = RX_GL.search(gt)
    gl = int(mg.group(1)) if mg else None
    sheet = 'sheet' if base != 'fs11_w' else None
    m, info = R.members(base, x, att, idx_n, gl, sheet, R.stdout_death(os.path.join(S, 'stdout_%s.txt' % tag)))
    no = [a for a, b in m if not b]
    good = len(no) == len(want_no) and all(any(a.startswith(w) for a in no) for w in want_no)
    st = R.stat_row(x)
    if tag == 'b12_v':
        good = good and st['lines'] == 34 and st['bad'] == 0 and x['b12'] == [(1, 718)]
    if tag == 'b12_v' and base == 'fs11_v':
        good = good and info['hold_s'] == 334.2 and info['frames_ge1s'] == 0 and idx_n == 10622 and gl == 0
    if tag == 'b12_w':
        good = good and x['vke'] == 0 and x['vkw'] == 908268 and st['lines'] == 33
    if tag == 'fs10_v':
        good = good and st['lines'] == 0 and x['b12'] == []
    ok &= good
    print('%s (%s) as %s: members NO %s; FixB12 %s; FixB12Stat lines %d bad %d -> %s' % (
        tag, S.rsplit('/', 1)[-1], base, [a[:50] for a in no], x['b12'][:2], st['lines'], st['bad'], 'as expected' if good else 'UNEXPECTED'))
    print('  info %s' % json.dumps(info, sort_keys=True, default=list)[:300])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
