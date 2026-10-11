"""F46c (HPP-800): check of the references <commit>:<path>:<line> of the seal docs/track-f/f46c.md section 0 (general rule 24(1)): the
line contains the anchor, the next line contains the +1 control ('<EOF>' - the line is the last of the file); negative control - every
reference shifted by one line must FAIL.  Reads git objects only (git show).  Last line ALL OK.  ASCII output.  Port of refs_f44c.py.
usage: python refs_f46c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('7df0fe5f', 'docs/ROADMAP.md', 24642, '702. **\u0417\u0432\u0435\u043d\u043e F45c \u0442\u0440\u0435\u043a\u0430 F (`HPP-797`, \u043b\u0438\u0434;', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F45a \u2713** (KytyPS5'),
    ('7df0fe5f', 'docs/ROADMAP.md', 24646, '(\u0433) **\u0424\u043e\u0440\u043c\u0430 \u0441\u0435\u0440\u0438\u0438 F46c (Harness Engineer', '(\u0434) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0447\u0442\u0435\u043d\u0438\u044f F46d (\u043b\u0438\u0434, \u0434\u043e \u0434\u0430\u043d\u043d\u044b'),
    ('7df0fe5f', 'docs/ROADMAP.md', 24647, '(\u0434) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0447\u0442\u0435\u043d\u0438\u044f F46d (\u043b\u0438\u0434, \u0434\u043e \u0434\u0430\u043d\u043d\u044b\u0445).**', '(\u0435) **\u041a\u043e\u0434 F46a (Emu Engineer; \u0442\u043e\u043b\u044c\u043a\u043e \u0438\u0437\u043c'),
    ('7df0fe5f', 'docs/ROADMAP.md', 24653, '(\u043b) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u042426 \u2014 \u0434\u0435\u0444\u0435\u043a\u0442 \u0438\u043b\u0438 \u043d\u0435 \u0434\u0435\u0444\u0435\u043a\u0442; \u0447\u0442\u043e \u043f\u043e\u0442\u0435\u0440\u044f', '<EOF>'),
    ('e6ef47e6', 'docs/ROADMAP.md', 24717, '711. **\u0417\u0432\u0435\u043d\u043e F46b \u0442\u0440\u0435\u043a\u0430 F (`HPP-799`, Red Team)', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F46b \u2713.** \u0427\u043b\u0435\u043d\u044b \u043f'),
    ('e6ef47e6', 'docs/ROADMAP.md', 24719, '(\u0431) **RC1 \u2014 \u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043b\u0438\u0434\u0430: \u0432\u0430\u0440\u0438\u0430\u043d\u0442 (\u0430).** \u041e\u0441\u043d\u043e\u0432\u0430\u043d\u0438\u0435: \u043c\u0435\u0442\u043a\u0443 \u041c1', '(\u0432) **\u041d1\u2013\u041d6.** \u041d1 \u2014 \u0447\u043b\u0435\u043d \u0434\u043e\u043f\u0443\u0441\u043a\u0430 \u043f. 702('),
    ('e6ef47e6', 'docs/ROADMAP.md', 24720, '(\u0432) **\u041d1\u2013\u041d6.** \u041d1', '(\u0433) **\u0417\u0432\u0435\u043d\u044c\u044f.** F46b `HPP-799` \u2014 approve'),
    ('f27c1c09', 'docs/ROADMAP.md', 24740, '714. **\u0412\u043e\u043f\u0440\u043e\u0441 F46c (`HPP-800`', '(\u0430) **\u041e\u0441\u043d\u043e\u0432\u0430\u043d\u0438\u0435.** \u0418\u0437 \u0447\u0435\u0442\u044b\u0440\u0451\u0445 \u0437\u0432\u0435\u043d\u044c\u0435\u0432 \u043f.'),
    ('d18ce225', 'docs/ROADMAP.md', 24753, '716. **\u0412\u043e\u043f\u0440\u043e\u0441 F46c (`HPP-800`', '(\u0430) **\u041e\u0441\u043d\u043e\u0432\u0430\u043d\u0438\u0435.** \u0417\u0430\u043c\u0435\u0440 \u0438\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044f \u043f\u0435\u0440'),
    ('1398d44d', 'src/graphics/host_gpu/renderer/diagF5.cpp', 727, 'auto text = fmt::format("DiagF5Ev: dcc_stale site={} n={} present={}', '"extent={}x{} exact={} fix={}",'),
    ('1398d44d', 'src/graphics/host_gpu/renderer/diagF5.cpp', 774, 'return fmt::format("DiagF5Ev: dcc_stale_apply n={} present={} gpu={}', '"layers=0x{:08x} site={}",'),
    ('1398d44d', 'src/graphics/host_gpu/renderer/diagF5.cpp', 790, 'return fmt::format("DiagF5Ev: f26_first_exec n={} present={} dcc=0x{:016x}', 'line.present, line.dcc, line.image, F26S'),
    ('1398d44d', 'src/graphics/host_gpu/renderer/diagF5.cpp', 837, 'EmitLine(fmt::format("F26Tint: mode={} dcc=0x{:016x}"', 'return true;'),
    ('1398d44d', 'src/graphics/host_gpu/renderer/diagF5.cpp', 611, 'EmitLine("FixF26: mode=1");', 'return true;'),
    ('1398d44d', 'src/graphics/host_gpu/renderer/diagF5.cpp', 227, '"f26_tint_applied",      // Track F, F46a', '"f26_tint_skip",'),
    ('1398d44d', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', 3709, 'LOGF("TextureCache: stale pending DCC fill ignored image=0x%016"', '" dcc=0x%016" PRIx64 " fill=0x%08x size='),
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
