# -*- coding: utf-8 -*-
# HPP-255 audit (s137): documents of the audit - CLAUDE.md (== AGENTS.md) status paragraph; HANDOFF.md entry; FACTS.md Step 5
# section appended. Anchors are whole lines; each must match once. Writes LF with write_bytes. Port of audit136/patch_docs_audit136.py.
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/ps5 em')


def rd(p):
    b = p.read_bytes().decode('utf-8')
    assert '\r' not in b, str(p) + ' has CR'
    return b


# ---------- CLAUDE.md == AGENTS.md ----------
t = rd(ROOT / 'CLAUDE.md')
assert t == rd(ROOT / 'AGENTS.md')
anchor = 'Дата: 2026-09-30. **Сессия 136 ЗАКРЫТА: `kp136`'
assert t.count(anchor) == 1
assert 'Сессия 137 — АУДИТ' not in t
para = ('Дата: 2026-09-30. **Сессия 137 — АУДИТ (шаг 5, `HPP-255`): `kp137` ПЕРЕСЧИТАН СВОИМ ПАРСЕРОМ — CONFIRMED ДО ДЕСЯТОЙ; `kp137` — '
        '`NOT_RESOLVED` (NEW 301 ПАРА ИЗ 8 ВЫЗОВОВ, OLD 0 — `DEBT`); ПАКЕТ `bindlean` ПРИПАРКОВАН ПО ПРАВИЛУ, ЗАПИСАННОМУ ДО ДАННЫХ; '
        '0 MAJOR / 3 MINOR (1 НОВЫЙ).** Свой парсер `audit137/recount137.py` (без общего кода со скорером `kp137.py` и разборщиком '
        '`smk137.py`; фикстуры 21 `ALL OK`, отрицательный контроль 7/7): Δ`dt_us` −75,1 ± 75,3, поправленный (β 7,7545) −108,5 ± 74,1 ⇒ '
        '`NOT_RESOLVED`; Q Кохрана p 0,560 / 0,566, DRS не смешан; база плеча 0 34 740,2 мкс (47,98 % строкой; `05431dad` с инструментами — '
        'не курс, не время `9235a7ac`); ряды до десятой (Δ`bl_buf_us` −182,1 ± 12,8, Δ`mh_bind_us` −200,8 ± 29,2, Δĉ −1,327 ± 0,132, '
        'с ĉ −257,0 ± 18,9 рядом с сырым −318,2 ± 17,9). Д12: β без блоков пары 0 7,7513 ⇒ −108,5 ± 74,1, тот же вердикт; без пар 0 и 1 — '
        '−99,8 ± 74,8. Теги корректности своим кодом: (б) `s4cs137` MET (исход (1)), (в) `kk137` MET — но в OLD: Д11′ — Σ`bln_chk` на NEW-строках '
        '2 560 055 из 90 214 559 (2,84 %); (д) `s6s137` не прочитано (195 < 500 NEW-строк). Калибровка 12 логов с. 136 — PASS 12/12, '
        '`rt1_probe` воспроизведён 31/31. Протокол п. 190–198: решения ≤ коммитов 8/8, печать 35/35 sha, одна попытка ×11, журнал — 8 × '
        '`printed_delta=no` до чтения, файлов в интервалах замка 0 (по mtime), установлена `9235a7ac`. MINOR: (1) одиночный разрыв IF5a '
        '`kp137g` (n 6723, d −65) нигде не напечатан — новый; (2) запись под замком шага 3 (п. 197(б)(4)); (3) `--only` до фикстуры (п. 195(г)). '
        'Д10 дополнен: база `kp137` ниже `kp136` на 937,7 мкс при тождественном пути 0 [I]. «Процесс» — 5 пунктов. Документ — '
        '`docs/session-137/audit/AUDIT137.md` (git KytyPS5), `C:/kyty/s137/audit137/`.\n\n')
t = t.replace(anchor, para + anchor)
(ROOT / 'CLAUDE.md').write_bytes(t.encode('utf-8'))
(ROOT / 'AGENTS.md').write_bytes(t.encode('utf-8'))

# ---------- HANDOFF.md ----------
h = rd(ROOT / 'HANDOFF.md')
assert 'Сессия 137 — аудит' not in h
if not h.endswith('\n'):
    h += '\n'
h += ('\nДата: 2026-09-30. **Сессия 137 — аудит (шаг 5, `HPP-255`; источник истины — `docs/local-session-137.md`, раздел Step 5; '
      'документ — `docs/session-137/audit/AUDIT137.md`).** `kp137` (8 вызовов × 300 с, `05431dad`, ABBA `bindlean=0|1`) пересчитан своим '
      'парсером — CONFIRMED до десятой: NEW 301 пара (пара 0 каждого вызова не читается), OLD 0 — `DEBT`; Δ`dt_us` −75,1 ± 75,3, '
      'поправленный −108,5 ± 74,1 ⇒ `NOT_RESOLVED`; вето нет (Q p 0,560 / 0,566; DRS 2 007,78 / 2 007,72); база плеча 0 34 740,2 мкс. '
      'Д12: β без блоков пары 0 — тот же вердикт. Теги корректности: (б) MET, (в) MET в OLD (NEW — 2,84 % сверок, Д11′), (д) не прочитано. '
      'Калибровка IF5 и положительный контроль `rt1_probe` воспроизведены своим кодом. Протокол п. 190–198 чист, кроме **0 MAJOR / 3 MINOR** '
      '(разрыв IF5a `kp137g` не напечатан — новый; запись под замком шага 3; `--only` до фикстуры звена 2а). Долги Д11′, Д12 исполнены, Д13 '
      'новый, Д10 дополнен (дрейф базы 937,7 мкс [I]); «Процесс» 5 пунктов. Отгружено ничего; пакет `bindlean` припаркован (п. 198). '
      '60 FPS не обещается.\n')
(ROOT / 'HANDOFF.md').write_bytes(h.encode('utf-8'))

# ---------- FACTS.md Step 5 ----------
F = Path('C:/kyty/s137/FACTS.md')
f = rd(F)
assert '## Step 5 ' not in f
add = rd(Path('C:/kyty/s137/audit137/facts_step5.md'))
if not f.endswith('\n'):
    f += '\n'
F.write_bytes((f + add).encode('utf-8'))
print('patched CLAUDE.md == AGENTS.md, HANDOFF.md, FACTS.md Step 5')
