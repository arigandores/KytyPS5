import os
import sys

D = sys.argv[1]
R = '04d5ac8a'
RM = 'docs/ROADMAP.md'
refs = [
    (R, RM, 24533, '694. **Звено F41c трека F (`HPP-776`, лид;', '(а) **Приёмка строкой. F41a ✓**'),
    (R, RM, 24560, '(6) **Теги под замком — «нет вреда» и первый запуск** (F42c;', '- `f20_v` — первый запуск `=1`'),
    (R, RM, 24573, '(к) **Не заявляется:** что бит теряется в игре', '695. **Звено F38b2 трека F'),
    (R, RM, 24668, '705. **Звено F42b трека F (`HPP-780`, review лида)', '(а) **Приёмка строкой. F42b ✓**'),
    (R, RM, 24678, '(в) **Замечания Н1–Н4 (правило п. 324(и)(5)).** Н1 — член печати F42c', '(г) **Звенья.** `HPP-780` F42b'),
    (R, RM, 24734, '713. **Звено F42a2 трека F (`HPP-805`, Emu Engineer)', '(а) **Приёмка строкой. F42a2 ✓.**'),
    (R, RM, 24738, '(г) **Звенья.** F42a2 `HPP-805` — approve', '(д) **Не заявляется:** что код F42a/F42a2'),
    (R, RM, 24773, '719. **Звено F42b2 трека F (`HPP-806`, Red Team;', '(а) **Приёмка строкой. F42b2 ✓**'),
    (R, RM, 24778, '(д) **Звенья.** F42b2 `HPP-806` — принят', '(е) **Не заявляется:** что Ф20 исправлен'),
    ('5ccb1d31', 'src/graphics/host_gpu/renderer/pipeline/fixF20.cpp', 26, 'LOGF("FixF20Stat: when=%s calls=%', '" rewritten=%" PRIu64 " unmatched=%'),
    ('5ccb1d31', 'src/graphics/host_gpu/renderer/pipeline/fixF20.cpp', 37, 'LOGF("FixF20: mode=%d', 'return value;'),
    ('5ccb1d31', 'src/emulator.cpp', 489, 'FixF20::PrintExitStat();', 'std::quick_exit(0);'),
    ('5ccb1d31', 'src/emulator.cpp', 500, 'FixF20::PrintExitStat();', 'std::quick_exit(0);'),
    ('5ccb1d31', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 4861, '(void)FixF20::Mode();', 'InitializeDriverCache();'),
    ('5ccb1d31', 'src/graphics/presentation/window/window.cpp', 1058, 'LOGF("ShaderPreparation: startup wait finished in %', '"\\n",'),
    ('5ccb1d31', 'src/common/subsystems.cpp', 80, 'LOGF("FixF21: mode=%d wait_ms=%u', '}'),
    ('5ccb1d31', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 604, 'LOGF("FixB12: mode=%d', '}'),
]


def lit(s):
    out = []
    for c in s:
        if c in "'\\":
            out.append('\\' + c)
        elif 32 <= ord(c) < 127:
            out.append(c)
        else:
            out.append('\\u%04x' % ord(c))
    return "'" + ''.join(out) + "'"


body = '''"""F42c (HPP-781): check of the references <commit>:<path>:<line> of the seal pred/f42c_seal.md section 0 (general rule 24(1)): the
line contains the anchor, the next line contains the +1 control; negative control - every reference shifted by one line must FAIL.  Reads
git objects only (git show).  Last line ALL OK.  ASCII output.  Port of refs_f44c.py.
usage: python refs_f42c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
REFS = [
'''
for c, p, n, a, b in refs:
    body += "    ('%s', '%s', %d, %s,\n     %s),\n" % (c, p, n, lit(a), lit(b))
tail = open('C:/kyty/f287/f44c/refs_f44c.py').read()
tail = tail[tail.index(']\nCACHE = {}'):]
body += tail
assert all(ord(c) < 128 for c in body)
open(os.path.join(D, 'refs_f42c.py'), 'w', newline='\n').write(body)
print('written', len(refs))
