# -*- coding: utf-8 -*-
"""s125 audit (HPP-77): status paragraph into ps5 em CLAUDE.md and AGENTS.md (byte-identical after), HANDOFF entry.
Whole-line anchors, each counted exactly once; LF; write_bytes."""
from pathlib import Path

D = Path('C:/kyty/KytyPS5/ps5 em')
STATUS = ('Дата: 2026-09-27. **Сессия 125 — АУДИТ (шаг 5, `HPP-77`): ВЫВОД «A6⁻ НЕ СТРОИТСЯ» CONFIRMED, РЯДЫ [I] DIVERGES; '
          '1 MAJOR / 4 MINOR, ВЕРДИКТ НЕ МЕНЯЕТСЯ.** Шаги 3–4 отменены п. 60(г) по п. 57(д): LB_acc = A1 (≤ 1 мкс по построению) '
          '+ «не построено», печати и прогона нет. Свой парсер аудита: 0 строк времени отправки гостем в 36 логах с. 116–124; '
          'член печати `g2_119` `cpu_net` 30 252,517 и D\\* = 22 122,4 воспроизведены из сырого лога. **MAJOR-1:** '
          '`rows125.py` строит блоки по `blk`, а не по `GateArm:` — «блок 0» забирает кадры загрузки n 12..90; верные ряды '
          '(плечо 0, блоки 4..83, окно 10..88 п. 55(б), 3 160 строк): `dt_us − cpu_net` **917 / 862** мкс (не 1 261 / 1 209), '
          '`cpu_net` 30 295 / 31 495 (не 29 595 / 30 766), занятость GuestGpu 0,971 / 0,974 (не 0,950, медиана не «1,0»); '
          'RC1–RC3 отзыва 2б и решения п. 60 стоят. MINOR: маркер попытки шага 4 — комментарием, не строкой ROADMAP; FACTS не '
          'вёлся после шага 0; RC2 приписывает разброс окнам (окна ≤ 112 мкс, прогоны ≈ 1 200); «медиана 1,0» — округление. '
          'НЕ доказано: LB_acc, величина A6, A2/A5/(c)/налог обходчика, второй сегмент (§4 ред. 2), условие 2, режим OLD. '
          'Аудит — `C:/kyty/s125/audit125/AUDIT125.md` (git `docs/session-125/audit/`). Закрытие — `HPP-78`.\n')
ANCHOR = 'Дата: 2026-09-27. **Сессия 124 ЗАКРЫТА: ПРОПУСК ПЕРЕВОДА DRAW ЗАКРЫТ ПЕРЕПИСЬЮ ЗАМЫКАНИЯ, УДЕРЖАНИЕ ФЛИПА — КОНТРАКТОМ;\n'

HAND = ('Дата: 2026-09-27. **Сессия 125 — аудит (шаг 5, `HPP-77`; источник истины — `docs/local-session-125.md`, раздел '
        'Step 5).** Цепочка `HPP-72`…`HPP-76` и вставки `HPP-79`/`HPP-80`: харнесс бенча (шаг 0), проект LB_acc ред. 1 и 2, '
        'отзывы Red Team (RC1–RC9, RC1–RC11); бенч пола снят п. 57(в), A6⁻ из существующих логов не строится — шаги 3–4 '
        'отменены п. 60(г). Пересчёт аудита своим парсером: вывод «не строится» и члены печати `g2_119` (D\\* = 22 122,4) — '
        'CONFIRMED; ряды [I] ред. 2 / `sources125.md` / RC1–RC3 / п. 60 — DIVERGES (блоки по `blk` забирают кадры загрузки; '
        'верно `dt_us − cpu_net` 917 / 862 мкс, `cpu_net` 30 295 / 31 495). 1 MAJOR и 4 MINOR, вердикт не меняется. Не '
        'доказаны: LB_acc, величина A6, A2/A5/(c), налог обходчика, доступность второго сегмента, условие 2. Закрытие сессии '
        '— `HPP-78` (лид).\n\n')
H_ANCHOR = 'Дата: 2026-09-27. **Сессия 124 ЗАКРЫТА (`HPP-65`, лид; `ROADMAP.md` «СЕССИЯ 122» п. 55; источник истины'


def patch_status(name):
    p = D / name
    t = p.read_bytes().decode('utf-8')
    assert '\r' not in t, name
    assert t.count(ANCHOR) == 1, (name, t.count(ANCHOR))
    assert 'Сессия 125 — АУДИТ' not in t, name
    t = t.replace(ANCHOR, STATUS + '\n' + ANCHOR)
    p.write_bytes(t.encode('utf-8'))


for n in ('CLAUDE.md', 'AGENTS.md'):
    patch_status(n)
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()

p = D / 'HANDOFF.md'
t = p.read_bytes().decode('utf-8')
assert '\r' not in t
lines = t.split('\n')
idx = [i for i, l in enumerate(lines) if l.startswith(H_ANCHOR)]
assert len(idx) == 1, idx
i = idx[0]
assert lines[i + 1] == '', repr(lines[i + 1])
lines.insert(i + 2, HAND.rstrip('\n'))
lines.insert(i + 3, '')
p.write_bytes('\n'.join(lines).encode('utf-8'))
print('ok')
