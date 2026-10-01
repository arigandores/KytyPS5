"""refs143.py - Red Team s143 step 1 (HPP-298): the reference map of review143.md (general rule 24(1)).
Every reference <commit>:<path>:<line> must hold its anchor (a substring of the line); the positive control - the same
reference at <line>+1 - must give NOT OK.  Prints one row per reference and ALL OK / FAIL.  ASCII-safe output."""
import subprocess
import sys

KP = 'C:/kyty/KytyPS5'
PE = 'C:/kyty/KytyPS5/ps5 em'
R = [
    (KP, '20b39318', 'docs/ROADMAP.md', 11777, '**Критерий Б5а:** N ≥ ln 0,05 / ln(1 − p) холодных входов без кадра `dt` ≥ 1 с после'),
    (KP, '20b39318', 'docs/ROADMAP.md', 11803, 'правило `dt` к W не применяется, п. 218(г)'),
    (KP, '20b39318', 'docs/ROADMAP.md', 11931, '(6) **RC6 — живость W:**'),
    (KP, '20b39318', 'docs/ROADMAP.md', 12306, '(д) **p форм на установленной сборке** [c]: **Б5а — 0/10**'),
    (KP, '20b39318', 'docs/ROADMAP.md', 12345, 'удержание ≥ 310 с, без видео'),
    (KP, '20b39318', 'docs/ROADMAP.md', 12352, 'строка `times.txt` с загрузкой CPU посторонних процессов (Д-4:'),
    (KP, '20b39318', 'docs/ROADMAP.md', 12353, 'Между тегами замок свободен; очередь замка'),
    (KP, '20b39318', 'docs/ROADMAP.md', 12669, '(1) `--stable-draws 300` у V и W подтверждается'),
    (KP, '20b39318', 'docs/ROADMAP.md', 12671, '(3) **Б33:** p строки Б33 реестра F от с. 143 — по букве'),
    (KP, '20b39318', 'docs/ROADMAP.md', 12776, '(1) Перед плечом: манифесты `_ShaderCache/PPSA21564`, `_PipelineCache` и `%LOCALAPPDATA%/NVIDIA/GLCache`'),
    (KP, '20b39318', 'docs/ROADMAP.md', 12781, 'возврат кэшей установленной сборки (копия перед первым плечом звена)'),
    (KP, 'a2849aec', 'src/graphics/presentation/window/vulkanWindow.cpp', 912, 'EXIT_COLOR(severity_style, "[Vulkan][%s][%u]: %s'),
    (KP, 'a2849aec', 'src/common/assert.cpp', 46, 'BuildFatalReport("--- Error ---", text, file, line)'),
    (KP, 'a2849aec', 'src/common/assert.cpp', 18, 'return fmt::format("--- Build ---'),
    (KP, '4e39d31c', 'docs/session-143/step0/sc143.py', 123, "CRASH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---')"),
    (KP, '4e39d31c', 'docs/session-143/step0/sc143.py', 306, "k2 = [(r[0], r[1], 'entry' if j < ENTRY_WIN else 'hold')"),
    (KP, '4e39d31c', 'docs/session-143/step0/sc143.py', 563, "if k2 or r['tail_stall']:"),
    (KP, '4e39d31c', 'docs/session-143/step0/sc143.py', 631, "v['tag'] == vt and w['tag'] == wt and v['guest_args'] == want"),
    (KP, '4e39d31c', 'docs/session-143/step0/sc143.py', 758, "b5a = sum(1 for e in ents if e['derive']['k2'])"),
    (KP, '4e39d31c', 'docs/session-143/step0/fgcpu143.py', 44, 'if key not in a or key[1].lower() in IGNORE or key[0] == me:'),
    (KP, '4e39d31c', 'docs/session-143/step0/test_fgcpu143.py', 71, "ok &= case('f3 the newcomer (not alive at --save)"),
    (KP, '4e39d31c', 'docs/session-143/step0/test_fgcpu143.py', 56, "A = {(1, 'chrome'): 10.0"),
    (KP, '4e39d31c', 'docs/session-143/step0/go143a.sh', 124, 'v143_*) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD'),
    (KP, '4e39d31c', 'docs/session-143/step0/go143a.sh', 125, 'w143_*) SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD'),
    (KP, '4e39d31c', 'docs/session-143/step0/go143a.sh', 206, 'shader cache files before the lock $(cachen)'),
    (KP, '4e39d31c', 'docs/session-143/step0/go143a.sh', 234, 'FG=$(python $ROOT/fgcpu143.py --since'),
    (PE, '06699cc', 'CLAUDE.md', 76, 'чужие приложения в тексте не называть'),
]


def line(repo, c, p, n):
    t = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    return t[n - 1] if 0 < n <= len(t) else ''


ok = True
for repo, c, p, n, a in R:
    pre = 'ps5-em@' if repo == PE else ''
    hit = a in line(repo, c, p, n)
    ctl = a in line(repo, c, p, n + 1)
    good = hit and not ctl
    ok &= good
    print('%s %s%s:%s:%d anchor %s; +1 control %s' % ('OK  ' if good else 'FAIL', pre, c, p, n, 'found' if hit else 'MISSING',
                                                     'NOT OK (as required)' if not ctl else 'found (BAD)'))
print('refs %d; %s' % (len(R), 'ALL OK' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
