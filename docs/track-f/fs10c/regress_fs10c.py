"""FS10c (HPP-686): the members of fs10c_read.py on the real logs of the same forms on T2 / FS9 (F25m, FS9c) - a regression of the parsers,
not a reading of FS10.  Expected: b36_s1_r1 -> fs10_s1 members ALL YES; b36_s0_r1 -> fs10_s0 ALL YES; b36_f1 -> fs10_f1 ALL YES (DiagB32
lines exist there - only the members are computed); b36_v -> fs10_v ALL YES; b36_w -> fs10_w ALL YES; fs9_v (FS9: no LogAsync) -> fs10_v
NOT ALL YES with exactly the LogAsync members NO.  The level of the pot logs is set by the module constant SKY.  ASCII only.
usage: python regress_fs10c.py"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fs10c_read as R  # noqa: E402

M = 'C:/kyty/f287/f25m'
S = 'C:/kyty/f287/fs9c'
CASES = [
    ('b36_s1_r1', 'fs10_s1', 'pot_treasure_cave', M, True, None),
    ('b36_s0_r1', 'fs10_s0', 'pot_treasure_cave', M, True, None),
    ('b36_f1', 'fs10_f1', 'pot_treasure_cave', M, True, None),
    ('b36_v', 'fs10_v', 'underwater_aerial_garden', M, True, None),
    ('b36_w', 'fs10_w', 'underwater_aerial_garden', M, True, None),
    ('fs9_v', 'fs10_v', 'underwater_aerial_garden', S, False, ['LogAsync: mode=1', 'summary LogAsync', 'drain_timeouts 0']),
]
RX_GL = re.compile(r'one-frame glitches: (\d+)')
ok = True
print('regress fs10c_read.py sha256 %s' % R.sha_file(R.__file__))
for tag, base, lvl, d, want_all, want_no in CASES:
    R.SKY = lvl
    log = os.path.join(d, 'log_%s.txt' % tag)
    run = json.load(open(os.path.join(d, '%s.json' % tag), encoding='utf-8'))
    att = run['attempts'][-1]
    x = R.scan(log)
    idx = os.path.join(d, 'rec_%s.mp4.idx' % tag)
    idx_n = sum(1 for _ in open(idx, 'rb')) if os.path.exists(idx) else None
    gt = R.text(os.path.join(d, 'runs', tag, 'glitch.txt')) or ''
    mg = RX_GL.search(gt)
    gl = int(mg.group(1)) if mg else None
    sheet = 'sheet' if base == 'fs10_v' else None
    adm = R.stand_admission(x, R.kind_of(base)) if R.kind_of(base).startswith('stand') else []
    m, info = R.members(base, x, att, idx_n, gl, sheet, R.stdout_death(os.path.join(d, 'stdout_%s.txt' % tag)))
    no = [a for a, b in m if not b]
    allyes = not no
    good = (allyes == want_all) and all(b for a, b in adm)
    if want_no is not None:
        good = good and len(no) == len(want_no) and all(any(a.startswith(w) for a in no) for w in want_no)
    ok &= good
    print('%s as %s: stand admission %s; members %s; NO %s -> %s' % (tag, base, [b for a, b in adm], 'ALL YES' if allyes else 'NOT ALL YES',
                                                                   [a[:50] for a in no], 'as expected' if good else 'UNEXPECTED'))
    print('  info %s' % json.dumps(info, sort_keys=True, default=list)[:400])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
