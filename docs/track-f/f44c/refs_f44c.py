"""F44c (HPP-793): check of the references <commit>:<path>:<line> of the seal docs/track-f/f44c.md section 0 (general rule 24(1)): the
line contains the anchor, the next line contains the +1 control ('<EOF>' - the line is the last of the file); negative control - every
reference shifted by one line must FAIL.  Reads git objects only (git show).  Last line ALL OK.  ASCII output.  Port of refs_f38c.py.
usage: python refs_f44c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('d0bfaf1f', 'docs/ROADMAP.md', 24603, '698. **\u0417\u0432\u0435\u043d\u043e F43b \u0442\u0440\u0435\u043a\u0430 F (`HPP-784`, \u043b\u0438\u0434; \u043f\u0440\u0438\u0451\u043c\u043a\u0430 F43a `HPP-783`)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F43a \u2713**'),
    ('d0bfaf1f', 'docs/ROADMAP.md', 24613, '(4) **\u0422\u0435\u0433 \u043f\u043e\u0434 \u0437\u0430\u043c\u043a\u043e\u043c \u2014 \xab\u043d\u0435\u0442 \u0432\u0440\u0435\u0434\u0430\xbb** (F44c;',
     '**\u0427\u0442\u0435\u043d\u0438\u0435:** (1)\u2013(4) \u0432\u0441\u0435 \u2713 \u2014 **\u042429 `FIXED`**'),
    ('d0bfaf1f', 'docs/ROADMAP.md', 24623, '(\u043c) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u043f\u0440\u043e\u0445\u043e\u0434 \u0441 \u2265 1 024 \u0431\u0438\u0442\u0430\u043c\u0438 \u0431\u044b\u0432\u0430\u0435\u0442 \u0432 \u0438\u0433\u0440\u0435',
     ''),
    ('d0bfaf1f', 'docs/ROADMAP.md', 24637, '701. **\u0417\u0432\u0435\u043d\u043e F44a \u0442\u0440\u0435\u043a\u0430 F (`HPP-791`, Emu Engineer)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F44a \u2713.**'),
    ('d0bfaf1f', 'docs/ROADMAP.md', 24688, '707. **\u0417\u0432\u0435\u043d\u043e F44b \u0442\u0440\u0435\u043a\u0430 F (`HPP-792`, Red Team)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F44b \u2713.**'),
    ('d0bfaf1f', 'docs/ROADMAP.md', 24691, '(\u0432) **\u0417\u0432\u0435\u043d\u044c\u044f.** F44b `HPP-792` \u2014 approve',
     '(\u0433) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u042429 \u0438\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d'),
    ('15c9d2f2', 'src/graphics/host_gpu/renderer/cache/faultManager.cpp', 43, '"KYTY_FIX_F29"',
     'return enabled;'),
    ('15c9d2f2', 'src/graphics/host_gpu/renderer/cache/faultManager.cpp', 57, 'LOGF("FixF29: overflow pass=%',
     'pass.area, parse.raw, parse.count, total'),
    ('15c9d2f2', 'src/graphics/host_gpu/renderer/cache/faultManager.cpp', 79, 'LOGF("FixF29: mode=%d',
     ''),
    ('15c9d2f2', 'src/graphics/host_gpu/renderer/cache/faultManager.cpp', 250, 'LOGF("Accessed non-GPU cached memory at 0x%016"',
     '},'),
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
