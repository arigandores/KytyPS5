# -*- coding: utf-8 -*-
"""s128 audit (HPP-125): status paragraph into ps5 em CLAUDE.md and AGENTS.md (byte-identical after), HANDOFF entry.
Whole-line anchors, each counted exactly once; LF; write_bytes."""
from pathlib import Path

D = Path('C:/kyty/KytyPS5/ps5 em')
STATUS = ('Дата: 2026-09-28. **Сессия 128 — АУДИТ (шаг 9, `HPP-125`): ПЕРЕСЧЁТ Δ, БАЗЫ И СТРАЖЕЙ ДОЗЫ `pd128` CONFIRMED ДО '
          'ЦИФРЫ; 0 MAJOR / 3 MINOR, ВЕРДИКТ `K14_OPEN` СТОИТ.** Запечатанный `pd128` (ABBA `protceil=0|2`, доза на месте '
          'вызова, сборка `45d36512`, печать `5342cddd`, скорер `60f128da`, ADMITTED): свой парсер аудита (блоки по '
          '`GateArm:`, окно 10..88 п. 55(б)) даёт **Δ `dt_us` +1 016,8 ± 140,8, поправленный +1 023,8 ± 118,2 мкс (42 пары '
          'NEW)** ⇒ низ +876,1 ≥ +500; доставка дозы 1,0075; база плеча 0 **31 700,6 мкс** (52,58 %, NEW, `45d36512` — с 50,36 % '
          '`98d98eee` не сравнивать, время установленной `9235a7ac` не мерено). Отгрузка `rtskip=1` (`9235a7ac`, видео `shp128`: '
          'Σ`rts_skip` 16,99 млн, 0 глитчей) пересчитана. Протокол по UTC (п. 87–96 до действий, печать до прогона, один полный '
          '`mutlib` + добор п. 96(б), бюджет 28,7 из 30 мин, в окне `pd128` — ни одного чужого рана) — чисто. MINOR: пересчёт лида '
          'п. 95(а) не воспроизводится названным файлом (числа верны, происхождение — нет); отказ значения 1 в цепочке без '
          '`--only`/вопроса; OLD (0 пар) не в списке долгов скорера. **НЕ доказано:** что Δ — выигрыш механизма (калибровка, '
          'линейность [I], ожидание на замках [U]), что перенос вооружения окупится (`protceil=1` вешает GPU), OLD, другие '
          'сцены. Аудит — `C:/kyty/s128/audit128/AUDIT128.md` (git `docs/session-128/audit/`). Закрытие — `HPP-126`.\n')
ANCHOR = 'Дата: 2026-09-28. **Сессия 127 ЗАКРЫТА: `RTSKIP_GAIN`'

HAND = ('Дата: 2026-09-28. **Сессия 128 — аудит (шаг 9, `HPP-125`; источник истины — `docs/local-session-128.md`, раздел '
        'Step 9).** Цепочка `HPP-116`…`HPP-124` и вставки `HPP-127`…`HPP-129`: отгрузка `rtskip=1` (коммит `4fc501f4`, '
        'установлена `9235a7ac`, видео `shp128`); ручка `protceil` — значение 1 (коммиты `55841100`+`252b0c76`) повесило GPU '
        'в 2 из 2 дымов, поворот п. 93 на дозу (значение 2, `04ae3390`, сборка `45d36512`), дым `s4s128`, печать '
        '`pred/01_pd128.md`, запечатанный `pd128`. Пересчёт аудита своим парсером — CONFIRMED до цифры: Δ `dt_us` +1 016,8 ± '
        '140,8 / поправленный +1 023,8 ± 118,2 мкс (42 пары NEW) ⇒ `K14_OPEN`; база плеча 0 31 700,6 мкс (NEW, `45d36512`). '
        '0 MAJOR, 3 MINOR (происхождение пересчёта лида п. 95(а); отказ значения 1 без `--only`; OLD не в долгах скорера), '
        'вердикт не меняется. Не доказаны: Δ как выигрыш механизма, окупаемость переноса вооружения, OLD, другие сцены, время '
        'установленной `9235a7ac`. Закрытие — `HPP-126` (лид).\n\n')
H_ANCHOR = 'Дата: 2026-09-28. **Сессия 127 ЗАКРЫТА (`HPP-113`, лид;'


def patch_status(name):
    p = D / name
    t = p.read_bytes().decode('utf-8')
    assert chr(13) not in t, name
    lines = t.split(chr(10))
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert len(idx) == 1, (name, idx)
    assert 'Сессия 128 — АУДИТ' not in t, name
    lines.insert(idx[0], STATUS.rstrip(chr(10)))
    lines.insert(idx[0] + 1, '')
    p.write_bytes(chr(10).join(lines).encode('utf-8'))


assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()
for n in ('CLAUDE.md', 'AGENTS.md'):
    patch_status(n)
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()

p = D / 'HANDOFF.md'
t = p.read_bytes().decode('utf-8')
assert chr(13) not in t
assert 'Сессия 128 — аудит' not in t
lines = t.split(chr(10))
idx = [i for i, l in enumerate(lines) if l.startswith(H_ANCHOR)]
assert len(idx) == 1, idx
i = idx[0]
assert lines[i + 1] == '', repr(lines[i + 1])
lines.insert(i + 2, HAND.rstrip(chr(10)))
lines.insert(i + 3, '')
p.write_bytes(chr(10).join(lines).encode('utf-8'))
print('ok')
