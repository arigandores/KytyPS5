# -*- coding: utf-8 -*-
# HPP-240 audit (s136): documents of the audit - CLAUDE.md (== AGENTS.md) status paragraph, the HPP-227 answer fact, the
# platform trap 11 line; HANDOFF.md entry; docs/platform-traps.md trap 11. Anchors are whole lines; each must match once.
# Writes LF with write_bytes.
import re
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/ps5 em')


def rd(p):
    b = (ROOT / p).read_bytes().decode('utf-8')
    assert '\r' not in b, p + ' has CR'
    return b


def wr(p, t):
    (ROOT / p).write_bytes(t.encode('utf-8'))


# ---------- CLAUDE.md ----------
t = rd('CLAUDE.md')
# the status line of the lead about HPP-227 is NOT edited (doc_split_check counts an edited line as lost); the answer
# 'A' of First agent is stated in the audit paragraph below (MINOR-4) and is a debt of the s136 closure.
anchor = 'Дата: 2026-09-30. **Сессия 135 ЗАКРЫТА: ПЕРЕПИСЬ `rs135`'
assert t.count(anchor) == 1
para = ('Дата: 2026-09-30. **Сессия 136 — АУДИТ (шаг 8, `HPP-240`): `kp136` И СТРОКА УБИЙСТВА `s1s136` ПЕРЕСЧИТАНЫ СВОИМ ПАРСЕРОМ — '
        'CONFIRMED ДО ДЕСЯТОЙ; `kp136` — `NOT_RESOLVED` (NEW 37 ПАР, OLD 0 — `DEBT`); УСЛОВИЯ (б) И (в) П. 176(е)(3) НЕ ПРОЧИТАНЫ '
        '(`INSTRUMENT_FAIL` НА ОДИНОЧНОМ РАЗРЫВЕ СНИМКА, K = 32) — ПАКЕТ НЕ КОРРЕКТЕН, НЕ ОТГРУЖАЕТСЯ; 0 MAJOR / 5 MINOR.** '
        'Свой парсер `audit136/recount136.py` (без общего кода со скорером; фикстуры 18 `ALL OK`, край окна 9/10/88/89, отрицательный '
        'контроль падает): `kp136` — 76 `GateArm`, 75 полных (37 / 38), окно 10–88 (п. 55(б)), Δ`dt_us` −68,4 ± 254,8, поправленный '
        '(β 8,2724) −100,1 ± 224,4 ⇒ `NOT_RESOLVED`; база плеча 0 35 677,9 мкс (46,72 %, сборка `03ce7a92` с инструментами — не время '
        '`9235a7ac`, со строками 131–135 не сравнивается); ряды до десятой (Δ`bl_buf_us` −199,3 ± 39,5, сырой сетевой −343,7 ± 51,0, '
        'Δĉ −1,276 ± 0,176, с ĉ −285,1 ± 48,9); `s1s136` — снижение `bl_buf_us` 212,6 (SE 34,7, 23 NEW-пары) ⇒ `NOT_KILLED`. Условия '
        'п. 176(е)(3) по своим логам: (а), (г) (0 глитчей `kv136`), (д) (по п. 184(б), 1 145 NEW-строк), (е), (ж) — выполнены; (б) — '
        '`s4s136`/`s4bs136` `bln_bad` 0, `s4cs136` `bln_bad` 3 930 078 и `bln_sbad` 338, но IF5b 73 на одной строке — не прочитано; '
        '(в) `kk136` — IF5c 61 на одной строке — не прочитано. **Вслух:** в `kp136` тот же ряд снижения `bl_buf_us` — 199,3 (< 200; ряд, '
        'не чтение п. 176(г)). Протокол: решения ≤ коммитов ≤ действий 13 / 13, скорер после печати не менялся, одна попытка на '
        'каждом из 12 тегов, установлена `9235a7ac`. MINOR: (1) замок п. 25(ж) — сборка и тесты 5а под замком `s5s136`, запись 5в″ под '
        'замком `kp136`; (2) бюджет мутантов 1 977,1 из 1 800 с; (3) (д) по правилу после данных (вслух в п. 184); (4) ответ First agent '
        '«A» по `HPP-227` не записан в `ROADMAP.md`; (5) K = 32 IF5 без калибровки на объёме `bindlean`. Долги Д1–Д9, «Процесс» — '
        '5 пунктов (в т. ч. ловушка платформы 11 — обёртка `git`). Отгружено ничего, сессий без отгрузки — 8 (129–136). Документ — '
        '`docs/session-136/audit/AUDIT136.md` (git KytyPS5), `C:/kyty/s136/audit136/`.\n\n')
t = t.replace(anchor, para + anchor)

old_trap = [l for l in t.split('\n') if l.startswith('  Новая (с. 133): (10) истёкшая сессия OAuth раннера ACP')]
assert len(old_trap) == 1
line = old_trap[0]
t = t.replace(line, line + '\n  Новая (с. 136): (11) обёртка `git` Paperclip в PATH теряет `GIT_AUTHOR_*` (`empty ident name`), из PowerShell '
              'отказывает молча — коммитить `C:/Program Files/Git/cmd/git.exe` с `GIT_AUTHOR_*`/`GIT_COMMITTER_*` и `--only` (шаг 5а′ с. 136).')
wr('CLAUDE.md', t)
wr('AGENTS.md', t)

# ---------- docs/platform-traps.md ----------
p = rd('docs/platform-traps.md')
trap = ('- **Ловушка платформы 11 (2026-09-30, с. 136 шаг 5а′ `HPP-245`, аудит `HPP-240`): обёртка `git` Paperclip в PATH.** В PATH '
        'прогона агента первой стоит обёртка `…/paperclip-github-runtime/…/git`. Она не передаёт `GIT_AUTHOR_*` и `-c user.*` — '
        '`git commit` падает `fatal: empty ident name`; из PowerShell отказывает молча (код возврата пуст, коммита нет). В шаге 5а′ '
        'так пропали три попытки коммита (08:52:45, 08:52:52, 08:53:03 UTC); коммит `ae8f30e5` сделан настоящим '
        '`C:/Program Files/Git/cmd/git.exe` с теми же `GIT_AUTHOR_*`/`GIT_COMMITTER_*` и `--only` (08:53:21 UTC). Правило: коммит '
        'агента — полным путём к `git.exe` (или проверить `command -v git` в том же вызове) и проверить `git log -1` после коммита.\n')
if not p.endswith('\n'):
    p += '\n'
p += trap
wr('docs/platform-traps.md', p)

# ---------- HANDOFF.md ----------
h = rd('HANDOFF.md')
if not h.endswith('\n'):
    h += '\n'
h += ('\nДата: 2026-09-30. **Сессия 136 — аудит (шаг 8, `HPP-240`; источник истины — `docs/local-session-136.md`, раздел Step 8; '
      'документ — `docs/session-136/audit/AUDIT136.md`).** `kp136` пересчитан своим парсером — CONFIRMED до десятой: 76 `GateArm`, 75 '
      'полных блоков (37 / 38), окно 10–88 (п. 55(б)), NEW 37 пар: Δ`dt_us` −68,4 ± 254,8, поправленный −100,1 ± 224,4 ⇒ '
      '`NOT_RESOLVED`; OLD 0 пар — `DEBT`; база плеча 0 35 677,9 мкс (сборка `03ce7a92` с инструментами; не время `9235a7ac`). Строка '
      'убийства `s1s136` — 212,6 (SE 34,7, 23 NEW-пары) ⇒ `NOT_KILLED` — CONFIRMED; в `kp136` тот же ряд — 199,3 ± 39,5 (ряд). Условия '
      'п. 176(е)(3): (а), (г), (д) (по п. 184(б)), (е), (ж), (з), (и) выполнены; (б) и (в) не прочитаны — `INSTRUMENT_FAIL` на одиночных '
      'разрывах снимка (IF5b 73 на `s4cs136`, IF5c 61 на `kk136`; K = 32) ⇒ пакет не корректен, не отгружается. Протокол п. 175–189: '
      'решения ≤ коммитов ≤ действий 13 / 13, скорер после печати не менялся, одна попытка на 12 тегах, установлена `9235a7ac`. '
      '**0 MAJOR / 5 MINOR** (замок п. 25(ж) в звеньях 5а и 5в″; бюджет мутантов 1 977,1 / 1 800 с; (д) по правилу после данных; '
      'ответ First agent «A» по `HPP-227` не записан в `ROADMAP.md`; K = 32 без калибровки). Долги Д1–Д9; «Процесс» 5 пунктов; ловушка '
      'платформы 11 (обёртка `git`) — в `docs/platform-traps.md`. Отгружено ничего, 8 сессий без отгрузки (129–136). 60 FPS не обещается.\n')
wr('HANDOFF.md', h)
print('patched CLAUDE.md == AGENTS.md, docs/platform-traps.md, HANDOFF.md')
