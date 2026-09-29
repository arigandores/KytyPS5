# -*- coding: utf-8 -*-
"""HPP-199: s133 audit paragraph into ps5 em CLAUDE.md == AGENTS.md (above the s132 close paragraph), a one-line platform trap 10
in the same files, the full trap 10 text at the end of docs/platform-traps.md and a HANDOFF.md entry at the end. Bytes and line
endings kept; every anchor must match exactly once."""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/ps5 em')
PARA = ('Дата: 2026-09-29. **Сессия 133 — АУДИТ (шаг 8, `HPP-199`): `bc133` ПЕРЕСЧИТАН СВОИМ ПАРСЕРОМ — CONFIRMED ДО ДЕСЯТОЙ; '
        'ИСХОД `B2_PASSES` (КАНДИДАТ (1) ОТБОРА С. 134, НЕ ВЫИГРЫШ); 0 MAJOR / 3 MINOR.** 84 `GateArm:`, полных 83 (41 / 42), окно '
        '10–88: плечо 1 `mh_bind` 12 223,1 ± 38,8, L 1 133,0 (ВЕРХНЯЯ граница снимаемого B2), R1 578,3 (4,73 %), R2 602,2 (13,30 %, '
        'вне ±5 %); плечо 2 would/n 0,64658, diff/chk 0 / 2 341 357, контроль xdiff/xchk 0,02753 (`ALIVE`); Δ `dt_us` плеча 2 − плеча 1 '
        '+370,1 ± 181,2 — цена значения 2. Ответ на вопрос п. 149(в): нулевую долю расхождения гонка RC5 не объясняет (граница 95 % '
        '1,3·10⁻⁶), но корректность B2 и неизменность выбора пути копии она не доказывает. Протокол п. 141–149 чист: решения ≤ коммитов, '
        'мутанты 738,0 из 1 800 с (+ зачётный 755,0 с), одна попытка, установлена `9235a7ac`. MINOR: (1) строка времени шага 4 не '
        'такая, как измерено; (2) R2 вне ±5 % не назван вопросом закрытия в п. 149(в); (3) в FACTS шага 5г названо стороннее '
        'приложение (в git не попало). Ряд аудита для отбора с. 134: доля повтора 0,647 — доля КОПИЙ; повторы — 0,285 КБ на копию '
        'против 0,944 КБ; доля времени повторов в L не мерена. «Процесс» — 5 пунктов (простой 2 ч 12 мин на истёкшей сессии OAuth — '
        'ловушка 10; 2 ч 25 мин — машина пользователя занята). Приватность HEAD обоих деревьев — блокирующих 0. Источник истины — '
        '`C:/kyty/s133/FACTS.md` (Step 8), в git `docs/local-session-133.md`; аудит — `docs/session-133/audit/AUDIT133.md`.')
ANCHOR = 'Дата: 2026-09-29. **Сессия 132 ЗАКРЫТА: ЗАПЕЧАТАННОГО ПРОГОНА НЕТ'
TRAP_ANCHOR = '  (9) Python с кириллицей в выводе — `export PYTHONIOENCODING=utf-8` (консоль cp1250, с. 130 p7).\n'
TRAP_LINE = ('  Новая (с. 133): (10) истёкшая сессия OAuth раннера ACP — прогон агента падает до первого действия (комментарий '
             '`terminal access failure`), звено стоит без работы до повтора задания (простой 2 ч 12 мин, аудит с. 133).\n')
TRAP_FULL = ('- **Ловушка платформы 10 (2026-09-29, с. 133, аудит `HPP-199`): истёкшая сессия OAuth раннера ACP.** Прогон агента '
             'падает до первого действия, а платформа пишет в звено комментарий «ACP agent reported a terminal access failure. '
             'Failed to authenticate: OAuth session expired and could not be refreshed». Звено остаётся в прежнем статусе и '
             'выглядит живым, но работы нет и само оно не просыпается. В с. 133 так упали 8 прогонов в 6 звеньях: `HPP-201` ×3 '
             '(14:51:56, 14:52:42, 14:53:39 UTC), `HPP-193`, `HPP-194`, `HPP-195`, `HPP-196`, `HPP-197` — по одному. Работа '
             'стояла 14:51–17:03 UTC (2 ч 12 мин), пока лид не повторил задание комментарием в 17:03:05. Признак — строка '
             '`terminal access failure` в комментариях звена без отчёта агента после неё. Правило обработки — решение лида '
             '(аудит с. 133, «Процесс» п. 1).\n')
HENTRY = ('Дата: 2026-09-29. **Сессия 133 — аудит (шаг 8, `HPP-199`; источник истины — `docs/local-session-133.md`, раздел Step 8; '
          'документ — `docs/session-133/audit/AUDIT133.md`).** `bc133` пересчитан своим парсером — CONFIRMED до десятой, доли до '
          'цифры (плечо 1: `mh_bind` 12 223,1, L 1 133,0, R1 4,73 %, R2 13,30 %; плечо 2: would/n 0,64658, diff 0 / 2 341 357, '
          'контроль 0,02753), исход `B2_PASSES` — кандидат (1) отбора с. 134, не выигрыш. Протокол п. 141–149 чист; 0 MAJOR / 3 MINOR '
          '(время шага 4 не из `date -u`; R2 не назван вопросом закрытия; стороннее приложение в FACTS шага 5г — в git не попало). '
          'Ответ на вопрос п. 149(в): нуль расхождения гонкой RC5 не объясняется, корректности B2 не доказывает. Ряд для отбора '
          'с. 134: доля повтора — доля копий (повторы мелкие: 0,285 КБ против 0,944 КБ), доля времени в L не мерена. Новая ловушка '
          'платформы 10 (истёкшая сессия OAuth раннера, простой 2 ч 12 мин). «Процесс» — 5 пунктов.')


def patch(path, fn):
    b = path.read_bytes()
    crlf = b.count(b'\r\n')
    nl = '\r\n' if crlf and crlf == b.count(b'\n') else '\n'
    t = b.decode('utf-8').replace('\r\n', '\n')
    out = fn(t).replace('\n', nl).encode('utf-8')
    path.write_bytes(out)
    return nl == '\r\n'


def ins_para(t):
    assert t.count(ANCHOR) == 1, t.count(ANCHOR)
    assert t.count(TRAP_ANCHOR) == 1, t.count(TRAP_ANCHOR)
    assert 'Сессия 133 — АУДИТ' not in t and '(10) истёкшая сессия OAuth' not in t
    t = t.replace(ANCHOR, PARA + '\n\n' + ANCHOR)
    return t.replace(TRAP_ANCHOR, TRAP_ANCHOR + TRAP_LINE)


def add_trap(t):
    assert 'Ловушка платформы 10' not in t
    return t.rstrip('\n') + '\n' + TRAP_FULL


def add_entry(t):
    assert 'Сессия 133 — аудит' not in t
    return t.rstrip('\n') + '\n\n' + HENTRY + '\n'


for name in ('CLAUDE.md', 'AGENTS.md'):
    print(name, 'crlf' if patch(ROOT / name, ins_para) else 'lf')
print('platform-traps.md', 'crlf' if patch(ROOT / 'docs' / 'platform-traps.md', add_trap) else 'lf')
print('HANDOFF.md', 'crlf' if patch(ROOT / 'HANDOFF.md', add_entry) else 'lf')
a, c = (ROOT / 'AGENTS.md').read_bytes(), (ROOT / 'CLAUDE.md').read_bytes()
assert a == c, 'CLAUDE.md != AGENTS.md'
print('CLAUDE.md == AGENTS.md', len(a))
