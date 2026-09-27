# -*- coding: utf-8 -*-
"""Session 122 audit: one status paragraph in CLAUDE.md == AGENTS.md and one entry in HANDOFF.md (LF, idempotent)."""
from pathlib import Path

D = Path('C:/kyty/KytyPS5/ps5 em')
MARK = 'Сессия 122 — АУДИТ (шаг 5, `HPP-8`)'

PARA = ('Дата: 2026-09-27. **' + MARK + ': ПЕРЕСЧЁТ CONFIRMED, 3 MAJOR / 5 MINOR, НИ ОДИН ВЕРДИКТ НЕ МЕНЯЕТСЯ; ВЫВОД '
        '«МЕЛКАЯ ЭКОНОМИЯ НЕ ВИДНА В FPS ИЗ-ЗА СТУПЕНЬКИ ВБЛЭНКА» ОПРОВЕРГНУТ ДАННЫМИ `sky122`.** Шаг 4 (`HPP-7`, запечатанные '
        'ABBA `burn=0|102000` на пяти сценах): опора `sky122` s 0,902 ± 0,065 и `ght122` (OLD) 0,939 ± 0,039 — НЕ РАЗРЕШЕНО; '
        '`des122`/`atl122`/`dnn122` — HEADROOM, не критичен; плацебо `skyp122r` (OLD) не критичен. Карта полная по сценам, '
        'частичная по потокам (код 1 и плацебо). MAJOR-1: раны агентов (лид, First agent) внутри окон `skyp122`/`skyp122r` '
        '(п. 6). MAJOR-2: на «зажатой» опоре (91,2 % кадров — два вблэнка) доза 2 мс сдвинула СРЕДНИЙ `dt` на 1,80 мс — '
        'квантуется кадр, а не среднее; невидимость прошлых выигрышей — предел шума (2SE ≈ 130–190 мкс), обоснование '
        'пропуска кадров ступенькой недействительно, поправка — новым пунктом ROADMAP при закрытии. MAJOR-3: печать ослабила '
        'стражи принятого проекта (доза ±5 % вместо ±3 %, `burn_late`, покрытие обоих плеч, страж DRS, `KYTY_GPU_WALL=1`) без '
        'строки ROADMAP — строгие стражи проходят, но почему s < 1, по запечатанным прогонам не решается. Аудит — '
        '`C:/kyty/s122/audit122/AUDIT122.md` (git `docs/session-122/audit/`). Закрытие — `HPP-9`.\n\n')

ANCHOR_C = 'Дата: 2026-09-26. **Сессия122 (ИДЁТ, ВОЗОБНОВЛЕНА)'
for name in ('CLAUDE.md', 'AGENTS.md'):
    p = D / name
    s = p.read_bytes().decode('utf-8')
    if MARK in s:
        continue
    assert s.count(ANCHOR_C) == 1, name
    s = s.replace(ANCHOR_C, PARA + ANCHOR_C, 1)
    p.write_bytes(s.encode('utf-8'))
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()

H = D / 'HANDOFF.md'
s = H.read_bytes().decode('utf-8')
ANCHOR_H = 'Дата: 2026-09-26. **Пуш.** По указанию пользователя ветка `merge-upstream`'
ENTRY = ('Дата: 2026-09-27. **Сессия 122 — аудит (шаг 5, `HPP-8`; источник истины — `docs/local-session-122.md`, раздел '
         'Audit).** Сессия возобновлена (п. 6): дымы, печать 01 `map122`, запечатанные ABBA прожига GuestGpu на пяти сценах. '
         'Пересчёт аудита своим парсером — CONFIRMED; опора и `ght122` НЕ РАЗРЕШЕНО (s 0,90 / 0,94), три HEADROOM-сцены и '
         'плацебо — не критичен. 3 MAJOR (раны агентов в окнах плацебо; «ступенька вблэнка» опровергнута средним `dt` '
         '`sky122`; стражи проекта ослаблены печатью без строки ROADMAP) и 5 MINOR, вердикты не меняются. Закрытие сессии — '
         '`HPP-9` (лид).\n\n')
if MARK.split(' (')[0] not in s or 'аудит (шаг 5, `HPP-8`' not in s:
    assert s.count(ANCHOR_H) == 1
    s = s.replace(ANCHOR_H, ENTRY + ANCHOR_H, 1)
    H.write_bytes(s.encode('utf-8'))
print('ok')
