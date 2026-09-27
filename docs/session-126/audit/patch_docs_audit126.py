# -*- coding: utf-8 -*-
"""s126 audit (HPP-91): status paragraph into ps5 em CLAUDE.md and AGENTS.md (byte-identical after), HANDOFF entry.
Whole-line anchors, each counted exactly once; LF; write_bytes."""
from pathlib import Path

D = Path('C:/kyty/KytyPS5/ps5 em')
STATUS = ('Дата: 2026-09-28. **Сессия 126 — АУДИТ (шаг 8, `HPP-91`): ПЕРЕСЧЁТ R_K3⁺ И БАЗЫ CONFIRMED ДО ЦИФРЫ; 0 MAJOR / '
          '4 MINOR, ВЕРДИКТ `K3_NOT_CLOSED` СТОИТ.** Запечатанный `k3c126` (сборка `14bead6f`, печать `d7b0a54e`, скорер '
          '`2bf8ac77`, ADMITTED): свой парсер аудита (блоки по `GateArm:`, окно 10..88 п. 55(б)) даёт **R_K3⁺ = 2 096,9 мкс, '
          'NEW** (⟨T0+T13+T13x⟩ 2 076,8 + 2·10,07; 43 блока C) ≥ 500 — K3 тестом убийства не закрыт; база п. 62(ж)(5) '
          '**32 067,2 мкс** (плечо B, NEW, `14bead6f`; 52,0 % — не сравнивать с 50,9 % OLD с. 125). Протокол по времени '
          '(п. 62–75 до действий, печать до прогона, один полный `mutlib`, в окне прогона — ни одного чужого рана агента) — '
          'чисто. MINOR: раннер цепочки в FACTS назван sha первого (незачётного) прогона; `procload` дыма под замком '
          '`adm126`; строка K3 таблицы курса п. 62(е) «≤ 1 550» устарела с п. 63(в); FACTS без шагов 1–4/3а. **НЕ доказано:** '
          'что K3 жив (R_K3⁺ — верх с ценой инструмента), OLD, полнота источников инвалидации (для прототипа — корректность), '
          'K7, база на `d3a981a2`. Аудит — `C:/kyty/s126/audit126/AUDIT126.md` (git `docs/session-126/audit/`). Закрытие — '
          '`HPP-92`.\n')
ANCHOR = 'Дата: 2026-09-27. **Сессия 125 ЗАКРЫТА: A-WALKER — УСЛОВИЕ УБИЙСТВА 1 НЕ ОПРОВЕРГНУТО ТОЛЬКО ДЛЯ A1, A6 НЕ ИЗМЕРЕН, ДОЛГ ПРИПАРКОВ'

HAND = ('Дата: 2026-09-28. **Сессия 126 — аудит (шаг 8, `HPP-91`; источник истины — `docs/local-session-126.md`, раздел '
        'Step 8).** Цепочка `HPP-83`…`HPP-90` и вставки `HPP-94`/`HPP-97`: харнесс, проект K3 ред. 1–2, отзыв и ревью кода '
        'Red Team, ручка `rk3cen` (сборка `14bead6f`), дым, печать `pred/01_k3c126.md`, запечатанный `k3c126`. Пересчёт '
        'аудита своим парсером — CONFIRMED до цифры: R_K3⁺ = 2 096,9 мкс NEW (43 блока C) ⇒ `K3_NOT_CLOSED`; база плеча B '
        '32 067,2 мкс (NEW, `14bead6f`). 0 MAJOR, 4 MINOR, вердикт не меняется. Не доказаны: жизнь K3 (граница верхняя), OLD, '
        'полнота источников инвалидации, K7, база на `d3a981a2`. Закрытие сессии — `HPP-92` (лид).\n\n')
H_ANCHOR = 'Дата: 2026-09-27. **Сессия 125 ЗАКРЫТА (`HPP-78`, лид; `ROADMAP.md` «СЕССИЯ 122» п. 62; источник истины'


def patch_status(name):
    p = D / name
    t = p.read_bytes().decode('utf-8')
    assert '\r' not in t, name
    lines = t.split('\n')
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert len(idx) == 1, (name, idx)
    assert 'Сессия 126 — АУДИТ' not in t, name
    lines.insert(idx[0], STATUS.rstrip('\n'))
    lines.insert(idx[0] + 1, '')
    p.write_bytes('\n'.join(lines).encode('utf-8'))


for n in ('CLAUDE.md', 'AGENTS.md'):
    patch_status(n)
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()

p = D / 'HANDOFF.md'
t = p.read_bytes().decode('utf-8')
assert '\r' not in t
assert 'Сессия 126 — аудит' not in t
lines = t.split('\n')
idx = [i for i, l in enumerate(lines) if l.startswith(H_ANCHOR)]
assert len(idx) == 1, idx
i = idx[0]
assert lines[i + 1] == '', repr(lines[i + 1])
lines.insert(i + 2, HAND.rstrip('\n'))
lines.insert(i + 3, '')
p.write_bytes('\n'.join(lines).encode('utf-8'))
print('ok')
