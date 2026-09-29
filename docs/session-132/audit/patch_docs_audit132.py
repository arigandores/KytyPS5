# -*- coding: utf-8 -*-
"""HPP-187: status paragraph of the s132 audit into ps5 em CLAUDE.md == AGENTS.md (above the s131 close paragraph) and a
HANDOFF.md entry at the end. Bytes, line endings kept; every anchor must match exactly once."""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/ps5 em')
PARA = ('Дата: 2026-09-29. **Сессия 132 — АУДИТ (шаг 9, `HPP-187`): ЗАПЕЧАТАННОГО ПРОГОНА НЕТ (ОБА ОТБОРА — «НИ ОДИН НЕ ПРОХОДИТ»); '
        'ЧИСЛА ОТБОРОВ ПЕРЕСЧИТАНЫ СВОИМ ПАРСЕРОМ — CONFIRMED; 0 MAJOR / 4 MINOR; K16 И K5 ПРИПАРКОВАНЫ, НЕ ЗАКРЫТЫ; 4 СЕССИИ БЕЗ '
        'ОТГРУЗКИ.** Шаг 1 (`dd131` плечо 0, 41 блок / 3 239 строк, окно 10–88): `bda` 896,8, `buf` 506,6, `dc_prot` 655,7; '
        '`dc_ph_bda` ~ `dc_prot` наклон 1,1516 / свободный 141,7 / корр 0,923; RO 1 480,5 нс/вызов + 205,84 нс/стр.; `dc_bda_n` ≡ 4 — '
        'до десятой. Шаг 1K (`spk118` M 40 / 3 160, `cen120` M 38 / 3 002): `pl_em_com` 2 375,6 = `bl_tr` 966,5 + `bl_wr` 659,0 + '
        '`bl_em` 479,7 + 270,5; поток записи ждёт 90,1 % кадра (в `dd131` — 89,5 %); `mh_bind` 10 968,5, неразделено 1 770,8 — до '
        'десятой. Протокол п. 135–139: время решений ≤ коммитов, действия после решений; игры, печати и замка не было; мутанты '
        '1 273,4 из 1 800 с. MINOR: (1) прогон мутантов цепочки и работа по ручке после п. 136(б) — пункт не дошёл до звена; (2) звено '
        '1K через 48 мин, `HPP-186` отменён без комментария и держал аудит; (3) «≈ 19 промахов» = `bda_n − bda_hit − dc_bda_n` (по '
        'тексту 23,2), «GuestGpu 0 [c]» = «≈ 0»; (4) 108 вместо 107 проверок в сдаче шага 0. Приватность HEAD обоих деревьев '
        '(`git grep -P -a`, 25 шаблонов) — блокирующих 0. «Процесс» — 5 пунктов (перечитывать ROADMAP перед дорогим действием; '
        'приёмка со звеньями — в том же хартбите; счёт из последнего вывода; отбор — на закрытии предыдущей сессии; перепись '
        'приватности — по всему дереву). База курса без новой точки — 51,38 % с инструментом. Источник истины — '
        '`C:/kyty/s132/FACTS.md` (Step 9), в git `docs/local-session-132.md`; аудит — `docs/session-132/audit/AUDIT132.md`.')
ANCHOR = 'Дата: 2026-09-29. **Сессия 131 ЗАКРЫТА: L — `NOT_RESOLVED`'
HENTRY = ('Дата: 2026-09-29. **Сессия 132 — аудит (шаг 9, `HPP-187`; источник истины — `docs/local-session-132.md`, раздел Step 9; '
          'документ — `docs/session-132/audit/AUDIT132.md`).** Запечатанного прогона нет: оба отбора (K16 — п. 136, K5 — п. 139) '
          'дали «ни один кандидат не проходит п. 134(ж)(1)–(4)». Числа отборов пересчитаны своим парсером — CONFIRMED до десятой '
          '(`dd131` плечо 0: `bda` 896,8, наклон `bda` ~ `dc_prot` 1,1516, RO 1 480,5 нс/вызов + 205,84 нс/стр.; `spk118` M: '
          '`pl_em_com` 2 375,6 = 966,5 + 659,0 + 479,7 + 270,5, поток записи ждёт 90,1 %, `mh_bind` неразделено 1 770,8). Протокол '
          'п. 135–139 чист, кроме MINOR-1 (прогон мутантов цепочки после п. 136(б), 1 273,4 с). 0 MAJOR / 4 MINOR; «Процесс» — 5 '
          'пунктов. K16 и K5 припаркованы; база 51,38 % без новой точки; сессий без отгрузки — 4 (129–132).')


def patch(path, fn):
    b = path.read_bytes()
    crlf = b.count(b'\r\n')
    nl = '\r\n' if crlf and crlf == b.count(b'\n') else '\n'
    t = b.decode('utf-8').replace('\r\n', '\n')
    t2 = fn(t)
    out = t2.replace('\n', nl).encode('utf-8')
    path.write_bytes(out)
    return nl == '\r\n'


def ins_para(t):
    assert t.count(ANCHOR) == 1, t.count(ANCHOR)
    assert 'Сессия 132 — АУДИТ' not in t
    return t.replace(ANCHOR, PARA + '\n\n' + ANCHOR)


def add_entry(t):
    assert 'Сессия 132 — аудит' not in t
    return t.rstrip('\n') + '\n\n' + HENTRY + '\n'


for name in ('CLAUDE.md', 'AGENTS.md'):
    print(name, 'crlf' if patch(ROOT / name, ins_para) else 'lf')
print('HANDOFF.md', 'crlf' if patch(ROOT / 'HANDOFF.md', add_entry) else 'lf')
a, c = (ROOT / 'AGENTS.md').read_bytes(), (ROOT / 'CLAUDE.md').read_bytes()
assert a == c, 'CLAUDE.md != AGENTS.md'
print('CLAUDE.md == AGENTS.md', len(a))
