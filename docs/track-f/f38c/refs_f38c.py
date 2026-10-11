"""F38c (HPP-765): check of the references <commit>:<path>:<line> of the seal docs/track-f/f38c.md section 0 (general rule 24(1)): the
line contains the anchor, the next line contains the +1 control ('<EOF>' - the line is the last of the file); negative control - every
reference shifted by one line must FAIL.  Reads git objects only (git show).  Last line ALL OK.  ASCII output.
usage: python refs_f38c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('d946a338', 'docs/ROADMAP.md', 24464, '691. **\u0417\u0432\u0435\u043d\u043e F37b \u0442\u0440\u0435\u043a\u0430 F (`HPP-762`, \u043b\u0438\u0434; \u043f\u0440\u0438\u0451\u043c\u043a\u0430 F37a `HPP-761`)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F37a \u2713**'),
    ('d946a338', 'docs/ROADMAP.md', 24474, '(4) **\u0422\u0435\u0433 \u043f\u043e\u0434 \u0437\u0430\u043c\u043a\u043e\u043c \u2014 \xab\u043d\u0435\u0442 \u0432\u0440\u0435\u0434\u0430\xbb** (F38c;',
     '**\u0427\u0442\u0435\u043d\u0438\u0435:** (1)\u2013(4) \u0432\u0441\u0435 \u2713'),
    ('d946a338', 'docs/ROADMAP.md', 24482, '(\u043c) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u0434\u0432\u043e\u0439\u043d\u043e\u0439 \u043e\u0442\u043a\u0430\u0437 \u0447\u0442\u0435\u043d\u0438\u044f',
     '692. **\u0417\u0432\u0435\u043d\u043e F39c \u0442\u0440\u0435\u043a\u0430 F'),
    ('d946a338', 'docs/ROADMAP.md', 24574, '695. **\u0417\u0432\u0435\u043d\u043e F38b2 \u0442\u0440\u0435\u043a\u0430 F (`HPP-778`, review \u043b\u0438\u0434\u0430)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F38b2 \u2713**'),
    ('d946a338', 'docs/ROADMAP.md', 24578, '(\u0433) **\u0417\u0432\u0435\u043d\u044c\u044f.** `HPP-778` F38b2',
     '(\u0434) **\u0410\u043f\u0440\u0438\u043e\u0440 \u043b\u0438\u0434\u0430 [I]:**'),
    ('531d6488', 'src/kernel/fileSystem.cpp', 127, 'static const bool enabled = Common::EnvFlagOn("KYTY_FIX_F25");',
     'return enabled;'),
    ('531d6488', 'src/kernel/fileSystem.cpp', 135, 'LOGF("FixF25: read failed twice d=%d size=%',
     '}'),
    ('531d6488', 'src/kernel/fileSystem.cpp', 426, 'LOGF("FixF25: mode=%d',
     '}'),
    ('531d6488', 'src/kernel/fileSystem.cpp', 793, 'LOGF("KernelRead: direct read failed, dst=0x%016"',
     ': reading through a host buffer'),
    ('730ed40a', 'src/common/subsystems.cpp', 80, 'LOGF("FixF21: mode=%d wait_ms=%u',
     '}'),
    ('730ed40a', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 604, 'LOGF("FixB12: mode=%d',
     '}'),
]
CACHE = {}


def lines(c, p):
    k = (c, p)
    if k not in CACHE:
        out = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8')
        CACHE[k] = out.split('\n')
        if CACHE[k] and CACHE[k][-1] == '':
            CACHE[k].pop()
    return CACHE[k]


def ok_ref(c, p, n, a, b):
    L = lines(c, p)
    if n < 1 or n > len(L) or a not in L[n - 1]:
        return False
    if b == '<EOF>':
        return n == len(L)
    return n < len(L) and b in L[n]


good = True
for c, p, n, a, b in REFS:
    r = ok_ref(c, p, n, a, b)
    print('%s %s:%s:%d' % ('OK' if r else 'NOT OK', c, p, n))
    good &= r
neg = True
for c, p, n, a, b in REFS:
    r = ok_ref(c, p, n + 1, a, b)
    print('shift %s %s:%s:%d' % ('OK (BAD)' if r else 'NOT OK', c, p, n + 1))
    neg &= not r
print('refs %d, ok %s, every shift fails %s' % (len(REFS), good, neg))
print('ALL OK' if good and neg else 'FAILED')
sys.exit(0 if good and neg else 1)
