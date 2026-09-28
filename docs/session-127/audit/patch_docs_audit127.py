# -*- coding: utf-8 -*-
"""s127 audit (HPP-112): status paragraph into ps5 em CLAUDE.md and AGENTS.md (byte-identical after), HANDOFF entry.
Whole-line anchors, each counted exactly once; LF; write_bytes."""
from pathlib import Path

D = Path('C:/kyty/KytyPS5/ps5 em')
STATUS = ('Дата: 2026-09-28. **Сессия 127 — АУДИТ (шаг 8, `HPP-112`): ПЕРЕСЧЁТ Δ, БАЗЫ И САМОПРОВЕРКИ CONFIRMED ДО ЦИФРЫ; '
          '0 MAJOR / 4 MINOR, ВЕРДИКТ `RTSKIP_GAIN` СТОИТ.** Запечатанный `k3p127` (ABBA `rtskip=0|1`, сборка `98d98eee`, '
          'печать `d7e20351`, скорер `356b3c83`, ADMITTED): свой парсер аудита (блоки по `GateArm:`, окно 10..88 п. 55(б)) '
          'даёт **Δ `dt_us` −386,4 ± 118,9, поправленный −403,0 ± 134,0 мкс (42 пары NEW)** ⇒ Δ + 2SE ≤ −100 обоими; база '
          'плеча 0 **33 095,6 мкс** (NEW, `98d98eee`; 50,36 % — с 52,0 % `14bead6f` не сравнивать). `k3k127` — `rts_bad` 0 на '
          '8 862 строках (`rts_chk` 39,8 млн); видео 0 глитчей (кадры `ffprobe` = индексам); дымы и валидация `s5`/`s6` '
          'пересчитаны своим кодом. Протокол по UTC (решения п. 76–86 до действий, печать до прогона, один полный `mutlib` + '
          'добор п. 86, в окне прогона — ни одного чужого рана) — чисто. MINOR: время §Step 7 FACTS местное под подписью UTC; '
          'поправка п. 86(в) комментарием; счёт бюджета п. 84(в)(6) с зачётным прогоном; FACTS без шагов 1–4 (третий раз). '
          '**НЕ доказано:** выигрыш против `d3a981a2` (цена ручки при 0 не мерена), OLD, значения на траектории режима 1, '
          'другие сцены, попиксельная картинка. Аудит — `C:/kyty/s127/audit127/AUDIT127.md` (git `docs/session-127/audit/`). '
          'Закрытие — `HPP-113`.\n')
ANCHOR = 'Дата: 2026-09-28. **Сессия 126 ЗАКРЫТА: K3 ТЕСТОМ УБИЙСТВА НЕ ЗАКРЫТ'

HAND = ('Дата: 2026-09-28. **Сессия 127 — аудит (шаг 8, `HPP-112`; источник истины — `docs/local-session-127.md`, раздел '
        'Step 8).** Цепочка `HPP-104`…`HPP-111` и вставки `HPP-114`/`HPP-115`: харнесс, проект K3-прототипа ред. 1–2, отзыв '
        'и ревью кода Red Team, ручка `rtskip` (коммит `defd2c91`, сборка `98d98eee`), дымы `s1s127`…`s6s127`, печать '
        '`pred/01_k3p127.md`, запечатанный `k3p127`, `k3k127`, видео `k3v127`/`k3w127`. Пересчёт аудита своим парсером — '
        'CONFIRMED до цифры: Δ `dt_us` −386,4 ± 118,9 / поправленный −403,0 ± 134,0 мкс (42 пары NEW) ⇒ `RTSKIP_GAIN`; база '
        'плеча 0 33 095,6 мкс (NEW, `98d98eee`); самопроверка `k3k127` чиста. 0 MAJOR, 4 MINOR, вердикт не меняется. Не '
        'доказаны: выигрыш против `d3a981a2`, OLD, значения на траектории режима 1, другие сцены. Закрытие — `HPP-113` '
        '(лид).\n\n')
H_ANCHOR = 'Дата: 2026-09-28. **Сессия 126 ЗАКРЫТА (`HPP-92`, лид; `ROADMAP.md` «СЕССИЯ 122» п. 76; источник истины'


def patch_status(name):
    p = D / name
    t = p.read_bytes().decode('utf-8')
    assert '\r' not in t, name
    lines = t.split('\n')
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert len(idx) == 1, (name, idx)
    assert 'Сессия 127 — АУДИТ' not in t, name
    lines.insert(idx[0], STATUS.rstrip('\n'))
    lines.insert(idx[0] + 1, '')
    p.write_bytes('\n'.join(lines).encode('utf-8'))


assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()
for n in ('CLAUDE.md', 'AGENTS.md'):
    patch_status(n)
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()

p = D / 'HANDOFF.md'
t = p.read_bytes().decode('utf-8')
assert '\r' not in t
assert 'Сессия 127 — аудит' not in t
lines = t.split('\n')
idx = [i for i, l in enumerate(lines) if l.startswith(H_ANCHOR)]
assert len(idx) == 1, idx
i = idx[0]
assert lines[i + 1] == '', repr(lines[i + 1])
lines.insert(i + 2, HAND.rstrip('\n'))
lines.insert(i + 3, '')
p.write_bytes('\n'.join(lines).encode('utf-8'))
print('ok')
