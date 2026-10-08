"""F26c (HPP-692): check of the references <commit>:<path>:<line> of the seal (general rule 24(1)): the anchor at the line, the +1 control
at the next line; negative control - every reference shifted by +1 must fail.  Prints 'refs n/n' and ALL OK.  ASCII only."""
import subprocess, sys
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('8540f311', 'docs/ROADMAP.md', 23862, '630. **\u0417\u0432\u0435\u043d\u043e F26b', '   (\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F26a'),
    ('8540f311', 'docs/ROADMAP.md', 23865, '   (\u0432) **N \u0438 \u0437\u0430\u0441\u0447\u0451\u0442 \u043e\u043f\u0438\u0441\u0438', '   (\u0433) **\u0424\u043e\u0440\u043c\u0430 \u0441\u0435\u0440\u0438\u0438 F26c'),
    ('8540f311', 'docs/ROADMAP.md', 23866, '   (\u0433) **\u0424\u043e\u0440\u043c\u0430 \u0441\u0435\u0440\u0438\u0438 F26c', '   (\u0434) **\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 \u0441\u0435\u0440\u0438\u0438.**'),
    ('8540f311', 'docs/ROADMAP.md', 23867, '   (\u0434) **\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 \u0441\u0435\u0440\u0438\u0438.**', '   (\u0435) **\u0427\u0442\u0435\u043d\u0438\u0435 F26d'),
    ('8540f311', 'docs/ROADMAP.md', 23868, '   (\u0435) **\u0427\u0442\u0435\u043d\u0438\u0435 F26d', '   (\u0436) **\u0417\u0432\u0435\u043d\u044c\u044f.** F26c'),
    ('8540f311', 'docs/ROADMAP.md', 23871, '   (\u0438) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u0411\u0032\u0035', ''),
    ('8540f311', 'docs/ROADMAP.md', 23857, '   (\u0435) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0438\u0441\u0445\u043e\u0434\u0430 \u0411\u0032\u0035', '   (\u0436) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0438\u0441\u0445\u043e\u0434\u0430 \u0411\u0033\u0030'),
    ('8540f311', 'docs/ROADMAP.md', 23786, '   (\u0433) **\u0420\u0435\u0448\u0435\u043d\u0438\u0435 3', '   (\u0434) **\u0414\u043e\u043b\u0433\u0438 \u0438 \u043f\u0440\u043e\u0448\u043b\u044b\u0435 \u0441\u0435\u0440\u0438\u0438.**'),
    ('8540f311', 'docs/ROADMAP.md', 23787, '   (\u0434) **\u0414\u043e\u043b\u0433\u0438 \u0438 \u043f\u0440\u043e\u0448\u043b\u044b\u0435 \u0441\u0435\u0440\u0438\u0438.**', '   (\u0435) **\u0417\u0432\u0435\u043d\u044c\u044f.** `HPP-680`'),
    ('8540f311', 'docs/ROADMAP.md', 23815, '   (\u0432) **\u041f\u0440\u044f\u043c\u043e\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f', '   (\u0433) **\u041e\u0442\u0441\u0442\u0443\u043f\u043b\u0435\u043d\u0438\u0435 \u0438\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044f**'),
    ('8540f311', 'docs/ROADMAP.md', 23676, '   (\u0432) **\u0420\u0435\u0448\u0435\u043d\u0438\u0435 \u2014 \u0432\u0430\u0440\u0438\u0430\u043d\u0442 (\u0430) \u0441 \u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430\u043c\u0438:**', '      (1) **\u0421\u0435\u0430\u043d\u0441 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f'),
    ('8540f311', 'docs/ROADMAP.md', 23090, '   (\u0432) **\u0420\u0435\u0448\u0435\u043d\u0438\u0435 \u043f\u043e \u0432\u043e\u043f\u0440\u043e\u0441\u0443 \u0437\u0432\u0435\u043d\u0430', '      (1) \u043d\u0438 \u043e\u0434\u0438\u043d \u0441\u043a\u0440\u0438\u043f\u0442 \u0445\u0430\u0440\u043d\u0435\u0441\u0441\u0430'),
    ('e6a39b95', 'docs/track-f/fs10c/go_fs10c.sh', 51, '  fs10_v) UF=""; SD=300; H=330; TO=480; REC="--rec"; KN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;', '  fs10_w) UF=""; SD=100; H=310; TO=900;'),
]


def lines(commit, path, cache={}):
    k = (commit, path)
    if k not in cache:
        cache[k] = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % k], capture_output=True).stdout.decode('utf-8').split('\n')
    return cache[k]


def ok(c, p, n, a, b):
    L = lines(c, p)
    return n - 1 < len(L) and L[n - 1].startswith(a) and (L[n].startswith(b) if b else L[n] == '')


good = 0
for r in REFS:
    g = ok(*r)
    good += g
    print('%s %s:%s:%d' % ('ok  ' if g else 'FAIL', r[0], r[1], r[2]))
neg = sum(not ok(c, p, n + 1, a, b) for c, p, n, a, b in REFS)
print('refs %d/%d; negative control (shift +1) fails %d/%d' % (good, len(REFS), neg, len(REFS)))
print('ALL OK' if good == len(REFS) and neg == len(REFS) else 'FAILED')
sys.exit(0 if good == len(REFS) and neg == len(REFS) else 1)
