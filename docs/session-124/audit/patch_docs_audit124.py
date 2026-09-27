# -*- coding: utf-8 -*-
"""Audit 124 (HPP-64): status paragraph into ps5 em CLAUDE.md and AGENTS.md (kept byte-identical) and a HANDOFF entry.
Anchors are whole-line prefixes, each found exactly once; LF, write_bytes."""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/ps5 em')
CL_ANCHOR = 'Дата: 2026-09-27. **Сессия 123 ЗАКРЫТА: ПОТОЛОК ПРОПУСКА КАДРОВ ИЗМЕРЕН (CEILING_MEASURED, ТОЛЬКО BDA OLD), ТРЕК ОТКРЫТ'
CL_PARA = ('Дата: 2026-09-27. **Сессия 124 — АУДИТ (шаг 9, `HPP-64`): ПЕРЕСЧЁТ CONFIRMED, 1 MAJOR / 2 MINOR, ВЕРДИКТ ПЕЧАТИ '
           'НЕ МЕНЯЕТСЯ.** Запечатанная перепись замыкания `cen124` (`skipceil=3`, сборка `b185f002`, печать `pred/01_cen124.md` '
           '`410ff61d`, Sky Garden, BDA **OLD** во всех 73 блоках): `f_x^{L+}` = `f_t^L(3τ⁺)` 0,01086 (по числу draw 0,00386), '
           'τ⁺ 18,716 нс, M⁺ = W₀⁺ · q⁺ = 32 609,2 · 0,5; **U = 177,1 мкс < 500 — FRAME_SKIP_CLOSED_BY_CENSUS** для версий, '
           'решающих по операциям и целым окнам привязок, при A3 (E [I]) и A4. Свой парсер аудита воспроизвёл все числа до '
           'цифры; исход сменился бы только при τ_true ≥ 104 нс. MAJOR-1: окно множителя W₀⁺ в печати — позиции 10..87, а '
           'п. 50(в) требует «10–88», и п. 54 подписал число как «10–88» (на 10..88 U 177,0; вердикт тот же). MINOR: второй '
           'полный `mutlib` разрешён п. 54(а) после обоих прогонов; отчёт шага 8 цитирует p50 τ̂ вместо max τ̂ = 460 нс (страж '
           '< 1 000). Замок эксклюзивен (в окне только ран Harness Engineer). НЕ доказано: выигрыш и прогноз (U — не '
           'экономия); удержание флипа (U_p⁺ 790,7 > 500 — НЕ закрыто); E, A4, A5; лишние рёбра (RC6); режим NEW; другие '
           'сцены. Аудит — `C:/kyty/s124/audit124/AUDIT124.md` (git `docs/session-124/audit/`). Закрытие — `HPP-65`.')
HO_ANCHOR_PREFIX = 'Дата: 2026-09-27. **Сессия 123 — закрыта (шаг 10, `HPP-33`, лид;'
HO_ENTRY = ('Дата: 2026-09-27. **Сессия 124 — аудит (шаг 9, `HPP-64`; источник истины — `docs/local-session-124.md`, раздел '
            'Step 9).** Цепочка `HPP-55`…`HPP-63` и вставки `HPP-66`…`HPP-71`: харнесс, проект `design124` rev 2 (14 RC Red '
            'Team), код режимов 2′/3 `skipceil` (три круга код-ревью, проба τ в контексте; сборка `b185f002`), дымы '
            '`s1s124`/`s2s124`/`s4s124`/`s6s124`, печать `pred/01_cen124.md`, запечатанная перепись `cen124` — '
            'FRAME_SKIP_CLOSED_BY_CENSUS, U = 177,1 мкс < 500 (BDA OLD; `f_x^{L+}` 0,01086). Пересчёт аудита своим парсером — '
            'CONFIRMED до цифры. 1 MAJOR (окно множителя W₀⁺ 10..87 против «10–88» п. 50(в); U на 10..88 — 177,0) и 2 MINOR, '
            'вердикт не меняется. Не доказаны: выигрыш, удержание флипа (U_p⁺ 790,7 > 500), допущения A3–A5, режим NEW, другие '
            'сцены. Закрытие сессии — `HPP-65` (лид).')


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
