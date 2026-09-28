# -*- coding: utf-8 -*-
"""s129 audit (HPP-138): Step 8 section appended to C:/kyty/s129/FACTS.md; status paragraph into ps5 em CLAUDE.md and
AGENTS.md (byte-identical after); HANDOFF entry after the s128 closure entry. Whole-line anchors, each counted exactly
once; LF; write_bytes. Port of audit128/patch_docs_audit128.py."""
from pathlib import Path

A = Path('C:/kyty/s129/audit129')
F = Path('C:/kyty/s129/FACTS.md')
D = Path('C:/kyty/KytyPS5/ps5 em')

STATUS = ('Дата: 2026-09-28. **Сессия 129 — АУДИТ (шаг 8, `HPP-138`): ПЕРЕСЧЁТ Δ, БАЗЫ, ДОЛИ ПЕРЕНЕСЁННОГО И САМОПРОВЕРКИ '
          'CONFIRMED ДО ЦИФРЫ; 0 MAJOR / 2 MINOR, ВЕРДИКТ `ARMCOPY_GAIN` (NEW) СТОИТ.** Запечатанный `ac129` (ABBA '
          '`armcopy=0|1`, сборка `edd17418`, печать `4c53c411`, скорер `c8e06640`, ADMITTED): свой парсер аудита (блоки по '
          '`GateArm:`, окно 10..88 п. 55(б)) даёт **Δ `dt_us` −334,9 ± 144,4, поправленный −361,3 ± 105,1 мкс (44 пары NEW; '
          'OLD — 0 пар, `DEBT`)**; база плеча 0 **31 237,1 мкс** (53,36 %, NEW, `edd17418` при `armcopy=0` — с 52,58 % '
          '`45d36512` не сравнивать); S 0,7416 и страж п. 102(б) 1,66 % — ряды. `ack129` — `SELFCHECK_CLEAN` (Σ`ac_bad`/'
          '`ac_gbad` 0 на 44,7 / 3,9 млн сверок), видео `acv129`/`acw129` — 0 глитчей, дымы шага 5 и валидация пересчитаны. '
          'Протокол по UTC (п. 97–104 до действий, печать до прогона, один полный `mutlib` + добор п. 74(б), бюджет 1 139,8 из '
          '1 800 с, в окне прогонов чужой работы нет) — чисто. MINOR: строка `ArmCopyVerify: LEFT` ветки куска в `ack129` с '
          '`perms=1 rm=1` (16 страниц) не выведена отчётом шага 7 — вопрос `JLEFT_ALL_REMARK` лиду с этим фактом до смены '
          'умолчания; вызов цепочки с `PLWAIT=60` вместо `PLWAIT=0` печати. **НЕ доказано:** выигрыш в OLD, в других сценах и '
          'на сборке отгрузки (F1–F4), отсутствие потерь записей вообще (нуль проверки содержимого — долг п. 104(б)), условие '
          'убийства п. 97(е)(2). Аудит — `C:/kyty/s129/audit129/AUDIT129.md` (git `docs/session-129/audit/`). Закрытие — '
          '`HPP-139`.\n')
ANCHOR = 'Дата: 2026-09-28. **Сессия 128 ЗАКРЫТА: `K14_OPEN`'

HAND = ('Дата: 2026-09-28. **Сессия 129 — аудит (шаг 8, `HPP-138`; источник истины — `docs/local-session-129.md`, раздел '
        'Step 8).** Цепочка `HPP-130`…`HPP-137` и вставка `HPP-140`: проект `armcopy` ред. 1–2, отзыв Red Team (RC1/RC2 MAJOR '
        'проекта, нуль `armcopy=4` п. 99(б)), код `67962c18` (сборка `edd17418`), ревью кода PASS_WITH_FIXES (F1–F4 — долг до '
        'отгрузки), 9 дымов, печать `pred/01_ac129.md`, запечатанный `ac129`, `ack129`, видео. Пересчёт аудита своим парсером — '
        'CONFIRMED до цифры: Δ `dt_us` −334,9 ± 144,4 / поправленный −361,3 ± 105,1 мкс (44 пары NEW) ⇒ `ARMCOPY_GAIN`; база '
        'плеча 0 31 237,1 мкс (NEW, `edd17418`); `ack129` `SELFCHECK_CLEAN`. 0 MAJOR, 2 MINOR (строка `LEFT` `perms=1 rm=1` '
        'в `ack129` не выведена — вопрос лиду; `PLWAIT=60` вместо 0), вердикт не меняется. Не доказаны: OLD, другие сцены, '
        'сборка отгрузки, отсутствие потерь записей вообще, условие п. 97(е)(2). Закрытие — `HPP-139` (лид).\n\n')
H_ANCHOR = 'Дата: 2026-09-28. **Сессия 128 ЗАКРЫТА (`HPP-126`, лид;'


def patch_status(name):
    p = D / name
    t = p.read_bytes().decode('utf-8')
    assert chr(13) not in t, name
    lines = t.split(chr(10))
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert len(idx) == 1, (name, idx)
    assert 'Сессия 129 — АУДИТ' not in t, name
    lines.insert(idx[0], STATUS.rstrip(chr(10)))
    lines.insert(idx[0] + 1, '')
    p.write_bytes(chr(10).join(lines).encode('utf-8'))


# FACTS: append Step 8
ft = F.read_bytes().decode('utf-8')
assert chr(13) not in ft and ft.endswith(chr(10))
assert '## Step 8' not in ft
sec = (A / 'facts_step8.md').read_bytes().decode('utf-8')
assert chr(13) not in sec
F.write_bytes((ft + sec).encode('utf-8'))

assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()
for n in ('CLAUDE.md', 'AGENTS.md'):
    patch_status(n)
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()

p = D / 'HANDOFF.md'
t = p.read_bytes().decode('utf-8')
assert chr(13) not in t
assert 'Сессия 129 — аудит' not in t
lines = t.split(chr(10))
idx = [i for i, l in enumerate(lines) if l.startswith(H_ANCHOR)]
assert len(idx) == 1, idx
i = idx[0]
assert lines[i + 1] == '', repr(lines[i + 1])
lines.insert(i + 2, HAND.rstrip(chr(10)))
lines.insert(i + 3, '')
p.write_bytes(chr(10).join(lines).encode('utf-8'))
print('ok')
