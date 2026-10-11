"""FS15c (HPP-822): check of the references <commit>:<path>:<line> of the seal docs/track-f/fs15c.md section 0 (general rule 24(1)): the
line contains the anchor, the next line contains the +1 control ('<EOF>' - the line is the last of the file; '<BLANK>' - the next line is
empty); negative control - every reference shifted by one line must FAIL.  Reads git objects only (git show).  Last line ALL OK.  ASCII
output.  Port of C:/kyty/f287/fs14c/refs_fs14c.py.
usage: python refs_fs15c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
RM = '54e37383'
C = '6beb3b73'
F20 = 'src/graphics/host_gpu/renderer/pipeline/fixF20.cpp'
REFS = [
    (RM, 'docs/ROADMAP.md', 24854, '730. **\u0417\u0432\u0435\u043d\u043e F42d \u0442\u0440\u0435\u043a\u0430 F (`HPP-782`, \u043b\u0438\u0434)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 F42a \u0441\u0442\u0440\u043e\u043a\u043e\u0439'),
    (RM, 'docs/ROADMAP.md', 24859, '(\u0433) **\u041e\u0442\u0433\u0440\u0443\u0437\u043a\u0430 FS15 \u2014 \u043a\u043e\u043d\u0441\u0442\u0430\u043d\u0442\u044b \u043b\u0438\u0434\u0430.**',
     '(\u0434) **\u0420\u0435\u0435\u0441\u0442\u0440 \u00a7125**'),
    (RM, 'docs/ROADMAP.md', 24863, '(\u0437) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u043f. 694(\u043a)',
     '731. **\u0417\u0432\u0435\u043d\u043e F47d'),
    (RM, 'docs/ROADMAP.md', 24873, '732. **\u0417\u0432\u0435\u043d\u043e FS15a \u0442\u0440\u0435\u043a\u0430 F (`HPP-820`, Emu Engineer',
     '(\u0430) **\u041f\u0435\u0440\u0435\u0441\u0447\u0451\u0442 \u043b\u0438\u0434\u0430 [c].**'),
    (RM, 'docs/ROADMAP.md', 24879, '733. **\u0417\u0432\u0435\u043d\u043e FS15b \u0442\u0440\u0435\u043a\u0430 F (`HPP-821`, Red Team',
     '(\u0430) **\u041f\u0435\u0440\u0435\u0441\u0447\u0451\u0442 \u043b\u0438\u0434\u0430 [c'),
    (C, F20, 38, 'const char* env = std::getenv("KYTY_FIX_F20");',
     "const int value = (env == nullptr || env[0] == '\\0' || Common::EnvValueOn(env)) ? 1 : 0;"),
    (C, F20, 40, 'LOGF("FixF20: mode=%d\\n", value);', 'return value;'),
    (C, F20, 26, 'LOGF("FixF20Stat: when=%s calls=%" PRIu64 " modules_bound=%" PRIu64 " modules=%" PRIu64 " sites=%" PRIu64',
     '" rewritten=%" PRIu64 " unmatched=%" PRIu64 "\\n",'),
    (C, F20, 54, 'PrintStat("periodic");', '}'),
    (C, F20, 60, 'if (Mode() == 1) {', 'PrintStat("exit");'),
    (C, 'src/emulator.cpp', 499, 'Libs::Graphics::WindowRun();', 'Libs::Graphics::FixF20::PrintExitStat();'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 7066, 'LOGF("PipelinePrecache: all pipelines created, %"',
     'VulkanLogMemoryStats();'),
    (C, 'src/graphics/presentation/window/window.cpp', 1089, 'LOGF("ShaderPreparation: startup wait finished in %"', '"\\n",'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 4861, '(void)FixF20::Mode();', 'InitializeDriverCache();'),
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
    if b == '<BLANK>':
        return n < len(L) and L[n].strip() == ''
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
