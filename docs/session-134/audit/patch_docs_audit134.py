# -*- coding: utf-8 -*-
"""HPP-211: s134 audit paragraph into ps5 em CLAUDE.md == AGENTS.md (above the s133 close paragraph) and a HANDOFF.md entry at
the end. Port of audit133/patch_docs_audit133.py (no new platform trap in s134). Bytes and line endings kept; every anchor must
match exactly once."""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/ps5 em')
PARA = ('Дата: 2026-09-30. **Сессия 134 — АУДИТ (шаг 9, `HPP-211`): `kp134` ПЕРЕСЧИТАН СВОИМ ПАРСЕРОМ — CONFIRMED ДО ДЕСЯТОЙ; '
        'ЧТЕНИЕ П. 151(д)(5) — `NOT_RESOLVED` (NEW 39 ПАР, OLD 0 — `DEBT`); СТРОКА УБИЙСТВА `s1s134` — CONFIRMED, `NOT_KILLED`; '
        '0 MAJOR / 3 MINOR.** `kp134`: 80 `GateArm:`, полных 79 (39 / 40), окно 10–88 п. 55(б); Δ `dt_us` (плечо `b2reuse=1` − `0`) '
        '+135,5 ± 272,7, поправленный (β 7,5459) +108,9 ± 219,3; min(Δ − 2SE) −137,2 (простой) / −110,4 (поправленный) ≤ −100 ⇒ '
        '`NO_GAIN` недостижим при любой трактовке «наименьшего»; DRS нет; база плеча 0 34 074,8 мкс (48,91 %, с инструментами, с 51,38 % '
        'не сравнивается). Ряды (перепись): снижение L 243,3 ± 14,5 гасится ростом `rb_epoch` + `rb_slow` +267,3 ± 47,0 (сеть +24,1 ± 53,3). '
        '`s1s134`: 23 NEW-пары, снижение L 268,4 (SE 9,1) ≥ 200. Условия п. 151(д)(3) по своим логам: (а) `s2s134`/`s3s134`, (б) `s4s134` '
        '(`b2r_bad` 27 422 345), (е) 0 маркеров в семи прогонах, (ж) `s5s134` (OLD 1 478,1), (и) 31 + 6 + 6 = 43 места — PASS; (в), (г), (д) '
        '— не проверены (V1–V4 `s6s134` только в OLD). Протокол п. 150–164 чист (решения ≤ коммитов, мутанты 1 575,7 из 1 800 с, замок, одна '
        'попытка, `9235a7ac` возвращена). MINOR: (1) правило IF5 п. 162 записано после данных `s1s134` — вердикт не меняется (max |Sₙ| 5/7); '
        '(2) время шага 7 по mtime без обрыва; (3) полный `mutlib` скорера 947,8 с > 900. Мощность: `NO_GAIN` при Δ ≈ 0 требует ≈ 290 пар '
        '(≈ 7,4 удержания по 300 с). «Процесс» — 5 пунктов (построчное равенство счётчиков — повтор п. 146(в); правка с флагом без списка '
        'переходов — 26 мин 48 с цепочки 5а–5г; прогноз `mutlib`; время по mtime; априор P(`NO_GAIN`) 0,6 против ≤ 0,19 по мощности). '
        'Источник истины — `C:/kyty/s134/FACTS.md` (Step 9), в git `docs/local-session-134.md`; аудит — `docs/session-134/audit/AUDIT134.md`.')
ANCHOR = 'Дата: 2026-09-29. **Сессия 133 ЗАКРЫТА: ПЕРЕПИСЬ'
HENTRY = ('Дата: 2026-09-30. **Сессия 134 — аудит (шаг 9, `HPP-211`; источник истины — `docs/local-session-134.md`, раздел Step 9; '
          'документ — `docs/session-134/audit/AUDIT134.md`).** `kp134` пересчитан своим парсером — CONFIRMED до десятой: 39 NEW-пар, '
          'Δ `dt_us` +135,5 ± 272,7 / поправленный +108,9 ± 219,3 ⇒ `NOT_RESOLVED` (OLD — `DEBT`); база плеча 0 34 074,8 мкс (48,91 %, '
          'не сравнивается). Строка убийства `s1s134` — CONFIRMED (268,4, SE 9,1, 23 пары) ⇒ `NOT_KILLED`. Условия п. 151(д)(3) (а), (б), '
          '(е), (ж), (и) подтверждены по своим логам; (в), (г), (д) не проверены. Протокол п. 150–164 чист; 0 MAJOR / 3 MINOR (правило '
          'IF5 после данных; время шага 7 по mtime; `mutlib` 947,8 > 900 с). Не доказано: что B2 ускоряет или замедляет; куда уходит снятое '
          'с L; корректность B2; OLD; мощность — для `NO_GAIN` при Δ ≈ 0 нужно ≈ 290 пар. «Процесс» — 5 пунктов.')


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
    assert 'Сессия 134 — АУДИТ' not in t
    return t.replace(ANCHOR, PARA + '\n\n' + ANCHOR)


def add_entry(t):
    assert 'Сессия 134 — аудит' not in t
    return t.rstrip('\n') + '\n\n' + HENTRY + '\n'


for name in ('CLAUDE.md', 'AGENTS.md'):
    print(name, 'crlf' if patch(ROOT / name, ins_para) else 'lf')
print('HANDOFF.md', 'crlf' if patch(ROOT / 'HANDOFF.md', add_entry) else 'lf')
a, c = (ROOT / 'AGENTS.md').read_bytes(), (ROOT / 'CLAUDE.md').read_bytes()
assert a == c, 'CLAUDE.md != AGENTS.md'
print('CLAUDE.md == AGENTS.md', len(a))
