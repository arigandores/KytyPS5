"""F42c (HPP-781): check of the references <commit>:<path>:<line> of the seal pred/f42c_seal.md section 0 (general rule 24(1)): the
line contains the anchor, the next line contains the +1 control; negative control - every reference shifted by one line must FAIL.  Reads
git objects only (git show).  Last line ALL OK.  ASCII output.  Port of refs_f44c.py.
usage: python refs_f42c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('04d5ac8a', 'docs/ROADMAP.md', 24533, '694. **\u0417\u0432\u0435\u043d\u043e F41c \u0442\u0440\u0435\u043a\u0430 F (`HPP-776`, \u043b\u0438\u0434;',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F41a \u2713**'),
    ('04d5ac8a', 'docs/ROADMAP.md', 24560, '(6) **\u0422\u0435\u0433\u0438 \u043f\u043e\u0434 \u0437\u0430\u043c\u043a\u043e\u043c \u2014 \u00ab\u043d\u0435\u0442 \u0432\u0440\u0435\u0434\u0430\u00bb \u0438 \u043f\u0435\u0440\u0432\u044b\u0439 \u0437\u0430\u043f\u0443\u0441\u043a** (F42c;',
     '- `f20_v` \u2014 \u043f\u0435\u0440\u0432\u044b\u0439 \u0437\u0430\u043f\u0443\u0441\u043a `=1`'),
    ('04d5ac8a', 'docs/ROADMAP.md', 24573, '(\u043a) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u0431\u0438\u0442 \u0442\u0435\u0440\u044f\u0435\u0442\u0441\u044f \u0432 \u0438\u0433\u0440\u0435',
     '695. **\u0417\u0432\u0435\u043d\u043e F38b2 \u0442\u0440\u0435\u043a\u0430 F'),
    ('04d5ac8a', 'docs/ROADMAP.md', 24668, '705. **\u0417\u0432\u0435\u043d\u043e F42b \u0442\u0440\u0435\u043a\u0430 F (`HPP-780`, review \u043b\u0438\u0434\u0430)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F42b \u2713**'),
    ('04d5ac8a', 'docs/ROADMAP.md', 24678, '(\u0432) **\u0417\u0430\u043c\u0435\u0447\u0430\u043d\u0438\u044f \u041d1\u2013\u041d4 (\u043f\u0440\u0430\u0432\u0438\u043b\u043e \u043f. 324(\u0438)(5)).** \u041d1 \u2014 \u0447\u043b\u0435\u043d \u043f\u0435\u0447\u0430\u0442\u0438 F42c',
     '(\u0433) **\u0417\u0432\u0435\u043d\u044c\u044f.** `HPP-780` F42b'),
    ('04d5ac8a', 'docs/ROADMAP.md', 24734, '713. **\u0417\u0432\u0435\u043d\u043e F42a2 \u0442\u0440\u0435\u043a\u0430 F (`HPP-805`, Emu Engineer)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F42a2 \u2713.**'),
    ('04d5ac8a', 'docs/ROADMAP.md', 24738, '(\u0433) **\u0417\u0432\u0435\u043d\u044c\u044f.** F42a2 `HPP-805` \u2014 approve',
     '(\u0434) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u043a\u043e\u0434 F42a/F42a2'),
    ('04d5ac8a', 'docs/ROADMAP.md', 24773, '719. **\u0417\u0432\u0435\u043d\u043e F42b2 \u0442\u0440\u0435\u043a\u0430 F (`HPP-806`, Red Team;',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F42b2 \u2713**'),
    ('04d5ac8a', 'docs/ROADMAP.md', 24778, '(\u0434) **\u0417\u0432\u0435\u043d\u044c\u044f.** F42b2 `HPP-806` \u2014 \u043f\u0440\u0438\u043d\u044f\u0442',
     '(\u0435) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u042420 \u0438\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d'),
    ('5ccb1d31', 'src/graphics/host_gpu/renderer/pipeline/fixF20.cpp', 26, 'LOGF("FixF20Stat: when=%s calls=%',
     '" rewritten=%" PRIu64 " unmatched=%'),
    ('5ccb1d31', 'src/graphics/host_gpu/renderer/pipeline/fixF20.cpp', 37, 'LOGF("FixF20: mode=%d',
     'return value;'),
    ('5ccb1d31', 'src/emulator.cpp', 489, 'FixF20::PrintExitStat();',
     'std::quick_exit(0);'),
    ('5ccb1d31', 'src/emulator.cpp', 500, 'FixF20::PrintExitStat();',
     'std::quick_exit(0);'),
    ('5ccb1d31', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 4861, '(void)FixF20::Mode();',
     'InitializeDriverCache();'),
    ('5ccb1d31', 'src/graphics/presentation/window/window.cpp', 1058, 'LOGF("ShaderPreparation: startup wait finished in %',
     '"\\n",'),
    ('5ccb1d31', 'src/common/subsystems.cpp', 80, 'LOGF("FixF21: mode=%d wait_ms=%u',
     '}'),
    ('5ccb1d31', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 604, 'LOGF("FixB12: mode=%d',
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
