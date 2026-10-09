"""F31c (HPP-731): check of the references <commit>:<path>:<line> of the seal docs/track-f/f31c.md (general rule 24(1)): the anchor at the
line, the +1 control at the next line (an empty +1 = the line after is empty); negative control - every reference shifted by +1 must fail.
Prints 'refs n/n' and ALL OK.  ASCII only."""
import subprocess, sys
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('afb501a5', 'docs/ROADMAP.md', 24191, '667. **\u0417\u0432\u0435\u043d\u043e F31b \u0442\u0440\u0435\u043a\u0430 F (`HPP-730`, \u043b\u0438\u0434): \u0438\u0441\u0445\u043e', '   (\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 F31a \u0441\u0434\u0435\u043b\u0430\u043d\u0430 \u043f. 666** \u2014'),
    ('afb501a5', 'docs/ROADMAP.md', 24195, '   (\u0433) **N \u0438 \u0437\u0430\u0441\u0447\u0451\u0442 \u043e\u043f\u0438\u0441\u0438 \u2014 \u043f\u043e \u0431\u0443\u043a\u0432\u0435 \u043f. 664(\u043b)(2', '   (\u0434) **\u0424\u043e\u0440\u043c\u0430 \u0441\u0435\u0440\u0438\u0438 F31c (Harness Engin'),
    ('afb501a5', 'docs/ROADMAP.md', 24196, '   (\u0434) **\u0424\u043e\u0440\u043c\u0430 \u0441\u0435\u0440\u0438\u0438 F31c (Harness Engineer, \u043f\u043e\u0434', '   (\u0435) **\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 \u0441\u0435\u0440\u0438\u0438.** (1) \u0421\u0442\u0440\u043e\u043a\u0430 \u0434'),
    ('afb501a5', 'docs/ROADMAP.md', 24197, '   (\u0435) **\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 \u0441\u0435\u0440\u0438\u0438.** (1) \u0421\u0442\u0440\u043e\u043a\u0430 \u0434\u0435\u0442\u0435\u043a\u0442\u043e\u0440\u0430', '   (\u0436) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0447\u0442\u0435\u043d\u0438\u044f F31d (\u043b\u0438\u0434) \u2014 \u0434\u043e '),
    ('afb501a5', 'docs/ROADMAP.md', 24198, '   (\u0436) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0447\u0442\u0435\u043d\u0438\u044f F31d (\u043b\u0438\u0434) \u2014 \u0434\u043e \u0434\u0430\u043d\u043d\u044b\u0445.*', '   (\u0437) **\u0417\u0432\u0435\u043d\u044c\u044f.** `HPP-730` \u2014 `done` \u044d\u0442'),
    ('afb501a5', 'docs/ROADMAP.md', 24202, '   (\u043b) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u041125 \u2014 \u0434\u0435\u0444\u0435\u043a\u0442 \u044d\u043c\u0443\u043b\u044f', ''),
    ('afb501a5', 'docs/ROADMAP.md', 23786, '   (\u0433) **\u0420\u0435\u0448\u0435\u043d\u0438\u0435 3 \u2014 \u043f\u0435\u0447\u0430\u0442\u044c 2 \u0434\u043e \u043f\u0435\u0440\u0432\u043e\u0433\u043e `_r1`.*', '   (\u0434) **\u0414\u043e\u043b\u0433\u0438 \u0438 \u043f\u0440\u043e\u0448\u043b\u044b\u0435 \u0441\u0435\u0440\u0438\u0438.** \u041f\u0440\u043e\u0448\u043b\u044b'),
    ('afb501a5', 'docs/ROADMAP.md', 23787, '   (\u0434) **\u0414\u043e\u043b\u0433\u0438 \u0438 \u043f\u0440\u043e\u0448\u043b\u044b\u0435 \u0441\u0435\u0440\u0438\u0438.** \u041f\u0440\u043e\u0448\u043b\u044b\u0435 \u0441\u0435\u0440\u0438\u0438 ', '   (\u0435) **\u0417\u0432\u0435\u043d\u044c\u044f.** `HPP-680` \u2014 \u043e\u0442\u0432\u0435\u0442 \u043a\u043e\u043c'),
    ('afb501a5', 'docs/ROADMAP.md', 23815, '   (\u0432) **\u041f\u0440\u044f\u043c\u043e\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u2014 \u043f\u043e\u0441\u0442\u043e\u044f\u043d\u043d', '   (\u0433) **\u041e\u0442\u0441\u0442\u0443\u043f\u043b\u0435\u043d\u0438\u0435 \u0438\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044f** (\u0437\u0430\u043f\u0443'),
    ('afb501a5', 'docs/ROADMAP.md', 23885, '   (\u0432) **\u0424\u043e\u0440\u043c\u0430.** (1) \u0428\u043b\u044e\u0437 \u043e\u0441\u0442\u0430\u0432\u0448\u0438\u0445\u0441\u044f \u0442\u0435\u0433\u043e\u0432 F26c', '   (\u0433) **\u0427\u0442\u0435\u043d\u0438\u0435 F26d (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u043f. 630('),
    ('afb501a5', 'docs/ROADMAP.md', 23897, '634. **\u041f\u0440\u044f\u043c\u043e\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u0432 `HPP-697` ', '   (\u0430) **\u041e\u0442\u043c\u0435\u043d\u044f\u0435\u0442\u0441\u044f \u0434\u043b\u044f \u0441\u0435\u0440\u0438\u0439, \u043f\u0435\u0447\u0430\u0442\u044c \u043a\u043e'),
    ('afb501a5', 'docs/ROADMAP.md', 24141, '   (\u0431) **\u041b\u0438\u043d\u0442\u0435\u0440** `form634_check.py` (\u043b\u0438\u0434, \u043a\u043e\u043f\u0438\u044f', '   (\u0432) **Harness Engineer \u2014 \u043a\u0430\u0436\u0434\u0430\u044f \u0441\u0435\u0440\u0438\u044f'),
    ('afb501a5', 'docs/ROADMAP.md', 24142, '   (\u0432) **Harness Engineer \u2014 \u043a\u0430\u0436\u0434\u0430\u044f \u0441\u0435\u0440\u0438\u044f \u043f\u043e\u0434 \u0437\u0430\u043c', '   (\u0433) **F30m (`HPP-723`), \u043e\u0441\u0442\u0430\u0442\u043e\u043a.** \u041a '),
    ('afb501a5', 'docs/ROADMAP.md', 23866, '   (\u0433) **\u0424\u043e\u0440\u043c\u0430 \u0441\u0435\u0440\u0438\u0438 F26c (Harness Engineer, \u043f\u043e\u0434', '   (\u0434) **\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 \u0441\u0435\u0440\u0438\u0438.** (1) \u0421\u0442\u0440\u043e\u043a\u0430 \u0434'),
    ('24f62694', 'docs/track-f/fs11c/go_fs11c.sh', 43, '  fs11_v) UF=""; SD=300; H=330; TO=480; REC="--r', '  fs11_w) UF=""; SD=100; H=310; TO=900; '),
]


def lines(commit, path, cache={}):
    k = (commit, path)
    if k not in cache:
        cache[k] = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % k], capture_output=True).stdout.decode('utf-8').split(chr(10))
    return cache[k]


def ok(c, p, n, a, b):
    L = lines(c, p)
    return n < len(L) and L[n - 1].startswith(a) and (L[n].startswith(b) if b else L[n] == '')


good = 0
for r in REFS:
    g = ok(*r)
    good += g
    print('%s %s:%s:%d' % ('ok  ' if g else 'FAIL', r[0], r[1], r[2]))
neg = sum(not ok(c, p, n + 1, a, b) for c, p, n, a, b in REFS)
print('refs %d/%d; negative control (shift +1) fails %d/%d' % (good, len(REFS), neg, len(REFS)))
print('ALL OK' if good == len(REFS) and neg == len(REFS) else 'FAILED')
sys.exit(0 if good == len(REFS) and neg == len(REFS) else 1)
