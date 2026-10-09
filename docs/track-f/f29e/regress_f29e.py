"""F29e (HPP-704): the members of f29e_read.py on the real logs of the same forms on FS10 abfded5e (FS10c: fs10_v, fs10_w) - a regression
of the parsers, not a reading of F29c.  FS10 has no FixB12 code: expected fs10_v -> b12_v NOT ALL YES with exactly the FixB12 member NO,
fs10_w -> b12_w the same; FixB12Stat lines 0 in both; every other member YES (the numbers equal the FS10c table: hold 334.3 s, 0 frames
>= 1 s, video 10 279 records / 0 glitches; [Vulkan][E] 0, [Vulkan][W] 922 165).  ASCII only.
usage: python regress_f29e.py"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f29e_read as R  # noqa: E402

S = 'C:/kyty/f287/fs10c'
CASES = [('fs10_v', 'b12_v'), ('fs10_w', 'b12_w')]
RX_GL = re.compile(r'one-frame glitches: (\d+)')
ok = True
print('regress f29e_read.py sha256 %s' % R.sha_file(R.__file__))
for tag, base in CASES:
    log = os.path.join(S, 'log_%s.txt' % tag)
    run = json.load(open(os.path.join(S, '%s.json' % tag), encoding='utf-8'))
    att = run['attempts'][-1]
    x = R.scan(log)
    idx = os.path.join(S, 'rec_%s.mp4.idx' % tag)
    idx_n = sum(1 for _ in open(idx, 'rb')) if os.path.exists(idx) else None
    gt = R.text(os.path.join(S, 'runs', tag, 'glitch.txt')) or ''
    mg = RX_GL.search(gt)
    gl = int(mg.group(1)) if mg else None
    sheet = 'sheet' if base == 'b12_v' else None
    m, info = R.members(base, x, att, idx_n, gl, sheet, R.stdout_death(os.path.join(S, 'stdout_%s.txt' % tag)))
    no = [a for a, b in m if not b]
    st = R.stat_row(x)
    good = len(no) == 1 and no[0].startswith('FixB12: mode=1') and st['lines'] == 0 and st['bad'] == 0
    if base == 'b12_v':
        good = good and info['hold_s'] == 334.3 and info['frames_ge1s'] == 0 and idx_n == 10279 and gl == 0
    else:
        good = good and x['vke'] == 0 and x['vkw'] == 922165
    ok &= good
    print('%s as %s: members NO %s; FixB12Stat lines %d bad %d -> %s' % (tag, base, [a[:60] for a in no], st['lines'], st['bad'],
                                                                         'as expected' if good else 'UNEXPECTED'))
    print('  info %s' % json.dumps(info, sort_keys=True, default=list)[:400])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
