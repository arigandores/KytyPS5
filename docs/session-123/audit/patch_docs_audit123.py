# -*- coding: utf-8 -*-
"""Audit 123 (HPP-32): status paragraph into ps5 em CLAUDE.md and AGENTS.md (kept byte-identical) and a HANDOFF entry.
Anchors are whole lines, each found exactly once; LF, write_bytes."""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/ps5 em')
CL_ANCHOR = 'Дата: 2026-09-27. **Сессия 122 ЗАКРЫТА: КАРТА УЗКИХ МЕСТ ЧЕРЕЗ ПРОЖИГ (`burn`) — ПОЛНАЯ ПО СЦЕНАМ, ЧАСТИЧНАЯ ПО'
CL_PARA = ('Дата: 2026-09-27. **Сессия 123 — АУДИТ (шаг 9, `HPP-32`): ПЕРЕСЧЁТ CONFIRMED, 1 MAJOR / 6 MINOR, НИ ОДИН ВЕРДИКТ '
           'НЕ МЕНЯЕТСЯ.** Запечатанные ABBA `skipceil=0|1` на `e4bb66ca` (печать `pred/01_skc123.md` `e6bf581f`): опора `sky123` '
           '(Sky Garden, BDA **OLD**) Δ`dt_us` 11 384,3 ± 132,7 мкс (51 пара), `ght123` (OLD, как `ght122`) 8 076,7 ± 77,0 (71) — '
           'CEILING_MEASURED, потолок грубой ручки, НЕ выигрыш. MAJOR-1: тик рутины «Сторож цикла» (ран лида, `chain_check.py '
           '--repair`, запись `HPP-54`) прошёл ВНУТРИ замка `ght123` — нарушение п. 25(ж); текст рутины всё ещё разрешает проверку '
           'во время запечатанного прогона; без задетых пар Δ 8 051,7 ± 69,8. MINOR: полосы G10 без строки ROADMAP, база G8(2) '
           '`ght122` в печати раньше п. 39(в), черновой полный `mutlib`, `procload --wait-s 1800` > 600 с, GPU 6–7 % перед '
           '`sky123`, нет архива `--out`. НЕ доказано: потолок в режиме NEW; у `ght123` плечо 1 упёрлось в вблэнк (est B 16 672,7) '
           '— «60 кадров/с» там не частота игры; критичность GuestGpu. Аудит — `C:/kyty/s123/audit123/AUDIT123.md` (git '
           '`docs/session-123/audit/`). Закрытие — `HPP-33`.')
HO_ANCHOR_PREFIX = 'Дата: 2026-09-27. **Сессия 122 — закрыта (шаг 6, `HPP-9`, лид;'
HO_ENTRY = ('Дата: 2026-09-27. **Сессия 123 — аудит (шаг 9, `HPP-32`; источник истины — `docs/local-session-123.md`, раздел '
            'Step 9).** Цепочка `HPP-23`…`HPP-31`: харнесс, проект `skipceil` (4 редакции, 3 круга Red Team), код `bb45007` '
            '(сборка `e4bb66ca`), дымы Д1/Д2/Д4, печать `pred/01_skc123.md`, запечатанные ABBA `sky123`/`ght123` — оба '
            'CEILING_MEASURED (11 384,3 ± 132,7 и 8 076,7 ± 77,0 мкс, BDA OLD). Пересчёт аудита своим парсером — CONFIRMED до '
            'цифры. 1 MAJOR (тик рутины-сторожа внутри замка `ght123`, п. 25(ж); сдвиг Δ без задетых пар −25 мкс) и 6 MINOR, '
            'вердикты не меняются. Не доказаны: выигрыш, потолок в NEW, критичность GuestGpu; у `ght123` плечо 1 упёрлось в '
            'вблэнк. Закрытие сессии — `HPP-33` (лид).')


def patch(path, anchor_prefix, new_line, before):
    raw = path.read_bytes().decode('utf-8')
    crlf = '\r\n' in raw
    text = raw.replace('\r\n', '\n')
    assert new_line not in text, 'already patched: %s' % path
    lines = text.split('\n')
    idx = [i for i, l in enumerate(lines) if l.startswith(anchor_prefix)]
    assert len(idx) == 1, (path, idx)
    i = idx[0]
    if before:
        lines[i:i] = [new_line, '']
    else:
        lines[i + 1:i + 1] = ['', new_line]
    out = '\n'.join(lines)
    if crlf:
        out = out.replace('\n', '\r\n')
    path.write_bytes(out.encode('utf-8'))


for name in ('CLAUDE.md', 'AGENTS.md'):
    patch(ROOT / name, CL_ANCHOR, CL_PARA, before=True)
patch(ROOT / 'HANDOFF.md', HO_ANCHOR_PREFIX, HO_ENTRY, before=False)
a = (ROOT / 'CLAUDE.md').read_bytes()
b = (ROOT / 'AGENTS.md').read_bytes()
assert a == b, 'CLAUDE.md != AGENTS.md'
print('patched; CLAUDE.md == AGENTS.md', len(a))
