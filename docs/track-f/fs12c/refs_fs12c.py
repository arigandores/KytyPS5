"""FS12c (HPP-752): check of the references <commit>:<path>:<line> of the seal docs/track-f/fs12c.md section 0 (general rule 24(1)): the
line contains the anchor, the next line contains the +1 control ('<EOF>' - the line is the last of the file); negative control - every
reference shifted by one line must FAIL.  Reads git objects only (git show).  Last line ALL OK.  ASCII output.
usage: python refs_fs12c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('cae9775d', 'docs/ROADMAP.md', 24376, '683. **\u0417\u0432\u0435\u043d\u043e F33f \u0442\u0440\u0435\u043a\u0430 F (`HPP-747`, \u043b\u0438\u0434)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439.**'),
    ('cae9775d', 'docs/ROADMAP.md', 24380, '(\u0433) **\u041e\u0442\u0433\u0440\u0443\u0437\u043a\u0430 FS12 \u2014 \u043a\u043e\u043d\u0441\u0442\u0430\u043d\u0442\u044b \u043b\u0438\u0434\u0430.**',
     '(\u0434) **\u041d\u0430\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u044f'),
    ('cae9775d', 'docs/ROADMAP.md', 24385, '(\u0438) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u043f. 675(\u0437)',
     '684. **\u0424\u0430\u043a\u0442 \u043f. 683(\u0436)'),
    ('cae9775d', 'docs/ROADMAP.md', 24406, '686. **\u0417\u0432\u0435\u043d\u043e FS12b \u0442\u0440\u0435\u043a\u0430 F (`HPP-751`, Red Team)',
     '(\u0430) **\u041d1 \u2014 \u043d\u0435 \u0438\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e'),
    ('cae9775d', 'docs/ROADMAP.md', 24409, '(\u0432) **\u041d3 \u2014 \u0447\u043b\u0435\u043d \u0444\u043e\u0440\u043c\u044b FS12c', '<EOF>'),
    ('730ed40a', 'src/common/subsystems.cpp', 74, 'const char* value = std::getenv("KYTY_FIX_F21");',
     "g_fix_f21  = value == nullptr || value[0] == '\\0' || EnvValueOn(value);"),
    ('730ed40a', 'src/common/subsystems.cpp', 80, 'LOGF("FixF21: mode=%d wait_ms=%u', '}'),
    ('730ed40a', 'src/common/subsystems.cpp', 178, 'std::fprintf(stderr, "FixF21: wait_expired tid=', 'waited_us / 1000u'),
    ('730ed40a', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 604, 'LOGF("FixB12: mode=%d', '}'),
    ('730ed40a', 'src/graphics/presentation/window/vulkanWindow.cpp', 672, 'LOGF("DualSrcBlend: supported=%d enabled=%d', 'dual_src_enabled ? 1 : 0'),
    ('730ed40a', 'src/emulator.cpp', 67, '// Every event is one stderr line "ExitFatal: ..."', 'driver needs the wall time'),
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
