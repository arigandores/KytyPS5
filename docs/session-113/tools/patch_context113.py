"""Session 113 close: the state paragraph, the session-113 entry and the session-113 env-var bullet of the context files
(CLAUDE.md = AGENTS.md in the game folder), replaced between asserted markers."""
from pathlib import Path

ROOT = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')

STATE = """**СОСТОЯНИЕ (2026-09-24): ЦИКЛ СЕССИЙ ИДЁТ** (пользователь, /loop: сессии подряд до «стоп», вопросов не задавать; push —
нет). **Сессия 113 закрыта** (аудит без MAJOR), следующая — `docs/next-session-114.md`: сначала рывок 3 с (ожидание
неподанного тика), затем `mutlib` v3, затем следующий трек скорости. Установлена сборка **`1678d3f4…`** (видео `vid113`
PASS); закреплённая копия `C:/kyty/s113/kyty_emulator_1678d3f4.exe`. Все цепочки прогонов держат замок
`C:/kyty/SEALED_RUN.lock`; во время запечатанного прогона — ни агентов, ни сборок, ни мутантов; состояние цикла —
`C:/kyty/LOOP_STATE.md`. Решения после с. 106–113 (`ROADMAP.md` §0.1) действуют: фикстуры на каждый член, ветку, край
порога и полосы; мутанты — `mutlib` v2 на запечатанной копии (производные скореры `--control --no-memo`); генераторы —
якоря целыми строками; главный оценщик ABBA — кадры 10–89 блока; **уровни из разных режимов BDA не сравниваются**.
**Скорость игры = 16 667 / mean `dt_us`. 60 FPS не обещать.**

"""

ENTRY = """Дата: 2026-09-24. **Сессия113: РЕЖИМ BDA ОБЪЯСНЁН; `bdanarrow=1` ПРОВЕРЕН И НЕ ОТГРУЖЕН — −83,2 ± 68,0 МКС ПРИ ПИНЕ В
ПРИНУДИТЕЛЬНОМ OLD (ПЛАНКА −100 НЕ ВЗЯТА); `mutlib` v2; ОДИН РЫВОК 3 С — ОЖИДАНИЕ НЕПОДАННОГО ТИКА.** Механизм: регистрация
буфера сбрасывала штампы всех ~1 016 регионов BDA, а сборщик буферов выселяет/создаёт буферы, пока занятая device-local
память выше порога из конструктора (9 296 МиБ) — это OLD (сегодня 1 вход из 7). Ручка **`bdanarrow`** (0/1/2, умолчание 0),
точная проверка режима 2 (`56a4b4f`), переменная **`KYTY_BUFFER_GC_TRIGGER_SHIFT_MB`** (только измерение, `967d1aa`) для
принудительного OLD. Проверка `vbn113m` (печать 01f): GO — 11,8 млн регионов, 0 промахов. ABBA `shn113` (печать 02, 600 с):
KEEP, Δ`dt` −83,2 ± 68,0. Рывок `vbn113k` (печать 01e NOT_ADMITTED): поток вне ролей ждал тик записываемого буфера 2,975 с,
GPU простаивал; инструмент `623009f` (`prio_unsub`/`prio_stall`/`gw_idle_prio`, строки `PriorityStall:`/`GpuIdlePrio:`).
Сборка **`1678d3f4…`** установлена, видео `vid113` 3 976 кадров, 0 глитчей. Аудит (`C:/kyty/s113/audit113/final/`): пересчёт
CONFIRMED, протокол HOLDS, код NOT REFUTED, 11 MINOR поправок (ROADMAP п. 22). Источник истины — `C:/kyty/s113/FACTS.md`,
в git `docs/local-session-113.md`.

"""

BULLET = """- Сто тринадцатая сессия (**умолчания поведения не сдвинуты; ручка `bdanarrow` проверена и оставлена 0**): ручка
  **`KYTY_BDA_NARROW_STAMPS`** / **`bdanarrow`** (0..2, **умолчание 0**, ПОСЛЕДНЯЯ строка ручек, читается раз на вызов
  `PrepareBda` — может быть плечом расписания): при любом значении регистрация буфера (`ChangeRegister<insert>`) помечает
  штампы BDA своих регионов; 0 — регистрация ещё и сдвигает глобальное поколение (обход всех регионов — режим OLD); 1 —
  глобальный сброс только при сдвиге эпохи карты гостя; 2 — как 0 плюс ТОЧНАЯ проверка того, что пропустил бы 1 (штамп
  региона читается под тем же замком, что и грязные биты, `MemoryTracker::CollectCpuModifiedRangesStamped`). Счётчики
  `FrameTrace-x` (сырые штуки): `bda_ginv_reg`/`bda_ginv_map`, `bda_rinv`, `bda_nskip`, `bda_nwould`, **`bda_nmiss`**
  (настоящий промах режима 1; строки `BdaNarrowMiss:`, ≤ 40), `bda_nrace` (информация: запись между чтением без замка и
  под замком), `bda_nxthr`, `bgc_evict`. **`KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=<МиБ>`** (ТОЛЬКО ИЗМЕРЕНИЕ, не гейт, раз на
  процесс в конструкторе `BufferCache`, умолчание 0): порог сборщика буферов ниже на N МиБ (не ниже 1 ГиБ; критический
  порог и текстуры не трогаются) — 1024 даёт принудительный OLD; строка **`BufferGc: budget= trigger= critical=
  shift_mb=`** печатается всегда. **Инструмент рывка** (без изменения поведения): приоритетная операция помнит место
  постановки; счётчики `prio_unsub` (ожидания, начатые на неподанном тике — ≈ 5,7/кадр норма), `prio_stall` (> 50 мс;
  строки `PriorityStall: tick= unsub= us= site=`, ≤ 64), `gw_idle_prio` (GuestGpu уходит в ожидание при неподанной
  приоритетной операции; строки `GpuIdlePrio:`, ≤ 32). `bdanarrow` — 43-е имя вне `gates_base.txt`; `gates.cpp` 142 записи
  (111 + 31). Харнесс `C:/kyty/s113`: скореры `vbn113b…f.py`, `shn113.py`, `check113.py` (+`test_*`, `mut_*`, `make_*`),
  цепочки `go113b…h.sh`, `SEALS113.txt`, `audit113*/`; быстрые мутанты — **`mutlib` v2** (`C:/kyty/s106_stage/mutlib/mutlib.py
  --scorer <запечатанный> --test <test_*.py> --mutants <mut_*.py> --control [--no-memo]`, README там же). **Ловушки:**
  якорь генератора — только целые строки (префиксный якорь с. 113 молча закомментировал фикстуру); мутанты, якорящиеся
  на незаполненной печати (`PRED_SHA = None`), гонять на черновике; режим BDA — состояние запуска, OLD можно навязать
  только сдвигом порога.
"""


def replace_between(text, start, end, new):
    i = text.find(start)
    assert i >= 0 and text.count(start) == 1, start[:60]
    j = text.find(end, i)
    assert j > i, end[:60]
    return text[:i] + new + text[j:]


for name in ('CLAUDE.md', 'AGENTS.md'):
    p = ROOT / name
    raw = p.read_bytes().decode('utf-8')
    crlf = '\r\n' in raw
    t = raw.replace('\r\n', '\n')
    t = replace_between(t, '**СОСТОЯНИЕ (2026-09-24): ПАУЗА', 'Дата: 2026-09-24. **Сессия113 (WIP', STATE)
    t = replace_between(t, 'Дата: 2026-09-24. **Сессия113 (WIP', 'Дата: 2026-09-24. **Сессия112:', ENTRY)
    t = replace_between(t, '- Сто тринадцатая сессия (**WIP, пауза', '- Сто двенадцатая сессия', BULLET)
    if crlf:
        t = t.replace('\n', '\r\n')
    p.write_bytes(t.encode('utf-8'))
    print('patched', p)
