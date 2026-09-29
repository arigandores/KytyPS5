# -*- coding: utf-8 -*-
"""s131 audit (HPP-173): Step 10 appended to C:/kyty/s131/FACTS.md; status paragraph into ps5 em CLAUDE.md and AGENTS.md
(byte-identical after) above the s130 closure paragraph; HANDOFF entry at the end. Whole-line anchors, each counted exactly
once; LF; write_bytes. Port of audit130/patch_docs_audit130.py."""
from pathlib import Path

A = Path('C:/kyty/s131/audit131')
F = Path('C:/kyty/s131/FACTS.md')
D = Path('C:/kyty/KytyPS5/ps5 em')

STATUS = ('Дата: 2026-09-29. **Сессия 131 — АУДИТ (шаг 10, `HPP-173`): ОБА ЧТЕНИЯ ПЕРЕСЧИТАНЫ СВОИМ ПАРСЕРОМ — CONFIRMED; '
          '0 MAJOR / 2 MINOR; L — `NOT_RESOLVED` (`ARMCOPY_INCORRECT` СТОИТ), K16 — `K16_OPEN` (КАЛИБРОВКА, НЕ ВЫИГРЫШ).** '
          'L п. 123(ж)(5): ΣH = 0 при `armcopy=2` в `lw1s131`/`lw2s131`/`lw5s131` (20 921 строка плеча 2) — классифицировать '
          'нечего; живость, И-L1…И-L5 построчно, контроли (`lw3` Σ`lw_p8` 26 577, `lw4` Σ`lw_c3x` 4 461, `lw6` Σ`lw_open` 46 651, '
          'CR, CD), стражи — чисто; оба чтения (окно 10–88 п. 55(б)) — тот же исход. `dd131` (сборка `d19a4f8a`, NEW 41 пара): '
          'Δ `dt_us` +1 990,8 ± 179,5, поправленный +2 043,4 ± 146,8, низ +1 811,3 ≥ +500 ⇒ `K16_OPEN`; OLD — 0 пар (`DEBT`); '
          'доставка дозы 1,01146; база 32 438,4 мкс = 51,38 % (с инструментом `mutsite=1 plkstat=1`; с 53,36 % не сравнивается). '
          'Протокол п. 123–133 чист: время решений `date -u` не позже коммита, печать до прогона, 47/47 sha печати, вызов по печати, '
          'одна попытка, замок до `procload`, чужой нагрузки нет, мутанты 1 347 из 1 800 с. MINOR: И-L7 по блокам нарушен в 10 из '
          '201 блока `lw2s131` (FACTS назвал его истинным по сумме лога) — пометки без штампа снятия [U]; шаг 0п расширил объём до '
          'решения лида. «Процесс» — 4 пункта (P(0) редкого события до данных: у L ≈ 0,04–0,11 [I]; `git commit --only`; допуск '
          'мутантов по прогнозу; вопросы приватности 0п). **НЕ доказано:** потеря или Р8 в `armcopy`; влияние `lwin=1` на частоту H; '
          'OLD; снимаемость переписи; время `9235a7ac`. Аудит — `C:/kyty/s131/audit131/AUDIT131.md` (git `docs/session-131/audit/`). '
          'Закрытие — `HPP-174`.\n')
ANCHOR = 'Дата: 2026-09-29. **Сессия 130 ЗАКРЫТА: `armcopy` — `ARMCOPY_INCORRECT`'

HAND = ('Дата: 2026-09-29. **Сессия 131 — аудит (шаг 10, `HPP-173`; источник истины — `docs/local-session-131.md`, раздел '
        'Step 10; документ — `docs/session-131/audit/AUDIT131.md`).** Пересчёт своим парсером — CONFIRMED: чтение L п. 123(ж)(5) '
        '`NOT_RESOLVED` (ΣH = 0 при 2 в `lw1`/`lw2`/`lw5`; контроли живы, тождества и стражи чисты) до единицы; `dd131` `K16_OPEN` '
        'до цифры (NEW 41 пара, +1 990,8 ± 179,5 / +2 043,4 ± 146,8, R 1,01146, база 32 438,4 мкс = 51,38 % на `d19a4f8a` с '
        'инструментом). Протокол п. 123–133 чист. 0 MAJOR, 2 MINOR (И-L7 по блокам нарушен в 10/201 блоках `lw2s131`; расширение '
        'шага 0п до решения), вердикты не меняются. «Процесс» — 4 пункта. Не доказаны: потеря/Р8 в `armcopy`, влияние `lwin`, OLD, '
        'снимаемость переписи. Закрытие — `HPP-174` (лид).\n')


def patch_claude(name):
    p = D / name
    t = p.read_bytes().decode('utf-8')
    assert chr(13) not in t, name
    assert 'Сессия 131 — АУДИТ' not in t, name
    lines = t.split(chr(10))
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert len(idx) == 1, (name, idx)
    lines.insert(idx[0], STATUS.rstrip(chr(10)))
    lines.insert(idx[0] + 1, '')
    p.write_bytes(chr(10).join(lines).encode('utf-8'))


ft = F.read_bytes().decode('utf-8')
assert chr(13) not in ft and ft.endswith(chr(10))
assert '## Step 10' not in ft
sec = (A / 'facts_step10.md').read_bytes().decode('utf-8')
assert chr(13) not in sec
F.write_bytes((ft + sec).encode('utf-8'))

assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()
for n in ('CLAUDE.md', 'AGENTS.md'):
    patch_claude(n)
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()

p = D / 'HANDOFF.md'
t = p.read_bytes().decode('utf-8')
assert chr(13) not in t
assert 'Сессия 131 — аудит' not in t
t = t.rstrip(chr(10)) + chr(10) + chr(10) + HAND
p.write_bytes(t.encode('utf-8'))
print('ok')
