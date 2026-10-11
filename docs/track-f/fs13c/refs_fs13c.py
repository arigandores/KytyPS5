"""FS13c (HPP-789): check of the references <commit>:<path>:<line> of the seal docs/track-f/fs13c.md section 0 (general rule 24(1)): the
line contains the anchor, the next line contains the +1 control ('<EOF>' - the line is the last of the file); negative control - every
reference shifted by one line must FAIL.  Reads git objects only (git show).  Last line ALL OK.  ASCII output.  Port of
C:/kyty/f287/fs12c/refs_fs12c.py.
usage: python refs_fs13c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
REFS = [
    ('d9180ac3', 'docs/ROADMAP.md', 24594, '697. **\u0417\u0432\u0435\u043d\u043e F38d \u0442\u0440\u0435\u043a\u0430 F (`HPP-766`, \u043b\u0438\u0434)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439.**'),
    ('d9180ac3', 'docs/ROADMAP.md', 24598, '(\u0433) **\u041e\u0442\u0433\u0440\u0443\u0437\u043a\u0430 FS13 \u2014 \u043a\u043e\u043d\u0441\u0442\u0430\u043d\u0442\u044b \u043b\u0438\u0434\u0430.**',
     '(\u0434) **\u0420\u0435\u0435\u0441\u0442\u0440 \u00a7116**'),
    ('d9180ac3', 'docs/ROADMAP.md', 24602, '(\u0437) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u043f. 691(\u043c)',
     '698. **\u0417\u0432\u0435\u043d\u043e F43b'),
    ('d9180ac3', 'docs/ROADMAP.md', 24625, '699. **\u0417\u0432\u0435\u043d\u043e FS13b \u0442\u0440\u0435\u043a\u0430 F (`HPP-788`, Red Team)',
     '(\u0430) **\u041d1 \u2014 \u043d\u0435 \u0438\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e, \u0447\u0438\u0442\u0430\u0442\u044c \u0442\u0430\u043a:**'),
    ('d9180ac3', 'docs/ROADMAP.md', 24629, '(\u0433) **\u0417\u0432\u0435\u043d\u044c\u044f.** `HPP-788`',
     '(\u0434) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u043f. 697(\u0437)'),
    ('ea6c6e9e', 'src/kernel/fileSystem.cpp', 130, 'const char* value = std::getenv("KYTY_FIX_F25");',
     "return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);"),
    ('ea6c6e9e', 'src/kernel/fileSystem.cpp', 140, 'LOGF("FixF25: read failed twice d=%d', '}'),
    ('ea6c6e9e', 'src/kernel/fileSystem.cpp', 431, 'LOGF("FixF25: mode=%d\\n", FixF25Enabled() ? 1 : 0);', '}'),
    ('ea6c6e9e', 'src/kernel/fileSystem.cpp', 798, 'LOGF("KernelRead: direct read failed, dst=0x%016"', ': reading through a host buffer'),
    ('ea6c6e9e', 'src/common/subsystems.cpp', 80, 'LOGF("FixF21: mode=%d wait_ms=%u', '}'),
    ('ea6c6e9e', 'src/common/subsystems.cpp', 178, 'std::fprintf(stderr, "FixF21: wait_expired tid=', 'waited_us / 1000u'),
    ('ea6c6e9e', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 604, 'LOGF("FixB12: mode=%d', '}'),
    ('ea6c6e9e', 'src/graphics/presentation/window/vulkanWindow.cpp', 672, 'LOGF("DualSrcBlend: supported=%d enabled=%d', 'dual_src_enabled ? 1 : 0'),
]
CACHE = {}


def lines(c, p):
    k = (c, p)
    if k not in CACHE:
        out = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8')
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
