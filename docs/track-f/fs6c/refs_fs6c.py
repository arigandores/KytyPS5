"""FS6c (HPP-557): the map of the references of the seal docs/track-f/fs6c.md (general rule 24(1): commit:path:line, anchor, control +1).
Each line of the commit must start with the anchor and the next line with the +1 text.  ASCII output only; ends with ALL OK.
usage: python refs_fs6c.py   (run in C:/kyty/KytyPS5)"""
import hashlib, os, subprocess, sys

REPO = 'C:/kyty/KytyPS5'
print('suite refs_fs6c.py sha256 %s' % hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest())
REFS = [
    ('item 454', 'e898ddf1', 'docs/ROADMAP.md', 22495, '454. **\u0417\u0432\u0435\u043d\u043e F15f',
     '   (\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439 \u043f\u043e \u0447\u043b\u0435\u043d\u0430\u043c \u043f. 412(\u0433).**'),
    ('item 454 (g)(3)', 'e898ddf1', 'docs/ROADMAP.md', 22502, '   (3) **FS6c (Harness Engineer',
     '   - `fs6_v` \u2014 \u0444\u043e\u0440\u043c\u0430 `b4_v`'),
    ('item 461', 'e898ddf1', 'docs/ROADMAP.md', 22547, '461. **\u0417\u0432\u0435\u043d\u043e FS6a',
     '   (\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. FS6a \u2713**'),
    ('item 461 (g)', 'e898ddf1', 'docs/ROADMAP.md', 22551, '   (\u0433) **\u041d1 \u043f. 454(\u0432) \u0434\u043b\u044f FS6',
     '   (\u0434) **\u0414\u043e\u043b\u0433\u0438 (\u043f. 324(\u0438)(5)):**'),
    ('item 463 (d)', 'e898ddf1', 'docs/ROADMAP.md', 22571, '   (\u0434) **\u0414\u043e\u043b\u0433\u0438 F18e',
     '   (\u0435) **\u0417\u0432\u0435\u043d\u044c\u044f:** F18e'),
    ('item 473 (b)(2)', 'e898ddf1', 'docs/ROADMAP.md', 22636, '      (2) Harness Engineer \u0432\u043e \u0432\u0441\u0435\u0445 \u0437\u0432\u0435\u043d\u044c\u044f\u0445 \u0441\u0435\u0440\u0438\u0439',
     '      (3) \u0421\u0431\u043e\u0440\u043a\u0430 \u0438 \u0441\u0442\u0435\u043d\u0434 FS6b'),
    ('item 476', 'e898ddf1', 'docs/ROADMAP.md', 22653, '476. **\u0417\u0432\u0435\u043d\u043e FS6b',
     '   (\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439: FS6b \u2713**'),
    ('F15e seal section 3', 'd5d0076a', 'docs/track-f/f15e.md', 43, '## 3. \u0424\u043e\u0440\u043c\u0430 \u0442\u0435\u0433\u0430', ''),
]
bad = 0
for name, c, path, ln, anchor, plus1 in REFS:
    t = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (c, path)], capture_output=True).stdout.decode('utf-8').split('\n')
    a = len(t) >= ln and t[ln - 1].startswith(anchor)
    b = len(t) > ln and (t[ln].startswith(plus1) if plus1 else t[ln].strip() == '')
    print('%s %s %s:%s:%d anchor %s +1 %s' % ('OK' if a and b else 'BAD', name, c, path, ln, 'OK' if a else 'BAD', 'OK' if b else 'BAD'))
    bad += not (a and b)
print('refs %d bad %d' % (len(REFS), bad))
if bad:
    sys.exit(1)
print('ALL OK')
