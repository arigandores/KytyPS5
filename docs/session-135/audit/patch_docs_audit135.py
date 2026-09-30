# -*- coding: utf-8 -*-
"""HPP-225: s135 audit paragraph into ps5 em CLAUDE.md == AGENTS.md (above the s134 close paragraph) and a HANDOFF.md entry at
the end. Port of audit134/patch_docs_audit134.py (no new platform trap in s135). Bytes and line endings kept; every anchor must
match exactly once."""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/ps5 em')
PARA = ('Дата: 2026-09-30. **Сессия 135 — АУДИТ (шаг 8, `HPP-225`): `rs135` ПЕРЕСЧИТАН СВОИМ ПАРСЕРОМ — CONFIRMED ДО ДЕСЯТОЙ; '
        '(д)(2) `B3_PARKED`, (д)(3) `B2M_NOT_RESOLVED` (NEW 38 ПАР, OLD 0 — `DEBT`); ДЫМЫ `s1s135`…`s3s135` — PASS ПО СВОИМ ЛОГАМ; '
        '1 MAJOR / 3 MINOR; Δĉ ПЛЕЧ −3,79 ± 0,86 НС — «РОСТ ПЯТИ ЧАСТЕЙ» (д)(3) — АРТЕФАКТ КАЛИБРОВКИ, НЕ НАДБАВКА.** `rs135`: 77 '
        '`GateArm:`, полных 76 (38 / 38), окно 10–88 п. 55(б); форма (а) п. 168 — МЕСТО и ЖИВОСТЬ; U3 −53,5 (SE 21,0) < 400 ≤ U3_сырой '
        '721,7 (U3_e 245,0 [I]); расхождение 0 / 32 794 715, сверка доказана (4 907 / 3 060); R1 4,25 %, R2 22,34 %, R3 по букве 48,18 %; '
        'ряды B2 до десятой (L −192,2 ± 20,8, `slow` +827,8 ± 157,7, Δ`rs_sync_n` −0,0650 ± 0,0628). Строки п. 174(в): ĉ плеча 1 10,459 '
        'против 14,245 ⇒ Δĉ −3,786 ± 0,860; без вычета ĉ Δ нс/итерацию `find`/`touch`/`sync`/`wr`/`rem` −0,06 / −0,02 / −1,43 / +0,06 / +0,06 '
        '(ни одна > 0 при 2SE), рост сосредоточен в `head` +5,81 и `tail` +2,74 [I]; сырые ряды B2: L −259,1 ± 15,0, `rb_epoch` +50,0 ± 3,9, '
        '`rb_slow` +195,0 ± 41,8; в 7 из 38 выборок «без одной пары» правило (д)(3) дало бы ложный `B2M_SURCHARGE`. MAJOR-1 — дефект правила '
        '(д)(3) и рядов B2 (ĉ зависит от плеча; вердикт не меняется, запечатанное следствие стоит); MINOR: формула п. 174(в) словами '
        '(двойной вычет Δĉ); Н3 не связывает (Σ`rs_find_n` 323); ввод HID в удержании (кадр 7 445). Протокол п. 165–174 чист (решения ≤ '
        'коммитов 9/9, 53 файла печати, мутанты 505,9 из 1 800 с, одна попытка, `9235a7ac` установлена). Долг Д1 — ĉ по плечам и сырые '
        'ряды `kp134` для чтения п. 165(б). «Процесс» — 4 пункта. Источник истины — `C:/kyty/s135/FACTS.md` (Step 8), в git '
        '`docs/local-session-135.md`; аудит — `docs/session-135/audit/AUDIT135.md`.')
ANCHOR = 'Дата: 2026-09-30. **Сессия 134 ЗАКРЫТА:'
HENTRY = ('Дата: 2026-09-30. **Сессия 135 — аудит (шаг 8, `HPP-225`; источник истины — `docs/local-session-135.md`, раздел Step 8; '
          'документ — `docs/session-135/audit/AUDIT135.md`).** `rs135` пересчитан своим парсером — CONFIRMED до десятой: NEW 38 пар, '
          '(д)(2) `B3_PARKED` (U3 −53,5 < 400 ≤ U3_сырой 721,7), (д)(3) `B2M_NOT_RESOLVED`; OLD — `DEBT`. Дымы `s1s135`…`s3s135` — PASS по '
          'своим логам (V5: классов `[W]` 3 = 3 в `s3s133`). Строки п. 174(в): Δĉ плеч −3,786 ± 0,860 нс; без вычета ĉ пять частей не растут '
          '(|Δ| ≤ 0,06, `sync` −1,43 ± 1,22), рост итерации — в `head`/`tail`; сырые ряды B2: L −259,1, `rb_epoch` +50,0, `rb_slow` +195,0. '
          'Протокол п. 165–174 чист; 1 MAJOR (дефект правила (д)(3) и рядов B2 с ĉ, вердикт не меняется) / 3 MINOR. Не доказано: снимаемость '
          'B3 (U3 между −53,5 и 721,7), механизм надбавки B2, причина зависимости ĉ от плеча, корректность B2, OLD. Долг Д1 — ĉ по плечам '
          '`kp134`. «Процесс» — 4 пункта.')


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
    assert 'Сессия 135 — АУДИТ' not in t
    return t.replace(ANCHOR, PARA + '\n\n' + ANCHOR)


def add_entry(t):
    assert 'Сессия 135 — аудит' not in t
    return t.rstrip('\n') + '\n\n' + HENTRY + '\n'


for name in ('CLAUDE.md', 'AGENTS.md'):
    print(name, 'crlf' if patch(ROOT / name, ins_para) else 'lf')
print('HANDOFF.md', 'crlf' if patch(ROOT / 'HANDOFF.md', add_entry) else 'lf')
a, c = (ROOT / 'AGENTS.md').read_bytes(), (ROOT / 'CLAUDE.md').read_bytes()
assert a == c, 'CLAUDE.md != AGENTS.md'
print('CLAUDE.md == AGENTS.md', len(a))
