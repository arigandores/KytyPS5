"""Session 109 close: next-session-110 debt line, the game contexts (CLAUDE.md = AGENTS.md) and HANDOFF.  LF writes."""
from pathlib import Path

GAME = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')


def rd(p):
    return Path(p).read_bytes().decode('utf-8').replace('\r\n', '\n')


def wr(p, s):
    Path(p).write_bytes(s.encode('utf-8'))


# next-session-110: the gpu_busy debt is identified now
n = rd('C:/kyty/KytyPS5/docs/next-session-110.md')
a = """`gpu_busy_us` +70–90 µs when the prefetch hold goes (cause [U]; GPU time is not the bottleneck at 12.6 of 31 ms, but
understand it before shipping)."""
b = """`gpu_busy_us` +70–90 µs when the prefetch hold goes — identified by the session-109 audit [I]: ~2 more buffer uploads
a flip land inside render passes and split them (`sync_up_kb` +250 KiB); a lever of its own (census of the causes
first). The 10 surviving mutants of the session-109 audit get their fixtures in the next derived scorers."""
assert n.count(a) == 1
wr('C:/kyty/KytyPS5/docs/next-session-110.md', n.replace(a, b))

c = rd(GAME / 'CLAUDE.md')
lines = c.split('\n')


def block(prefix):
    i = next(k for k, l in enumerate(lines) if l.startswith(prefix))
    j = i
    while j < len(lines) and lines[j].strip():
        j += 1
    return i, j


state = """**СОСТОЯНИЕ (2026-09-24): ЦИКЛ СЕССИЙ ИДЁТ** (пользователь, /loop: сессии подряд до «стоп», вопросов не задавать,
после исчерпания лимитов продолжать; push — нет). Хартбит — cron в беседе (:17 и :47); во время запечатанного
прогона он не делает ни одного вызова инструментов; все цепочки прогонов держат замок `C:/kyty/SEALED_RUN.lock`;
состояние для хартбита — `C:/kyty/LOOP_STATE.md`. **Сессия 109 закрыта**, следующая — `docs/next-session-110.md`
(страж `cspfree` по ДЛИТЕЛЬНОСТИ рывков, затем ABBA отгрузки; код `daslot`). Решения после с. 106–109 (`ROADMAP.md`
§0.1) действуют: фикстуры — на каждый член и ветку, мутанты убиваются; страж обязан иметь экспозицию (precache compute
выкл) и мерить длительность, а не число событий. **Скорость игры = 16 667 / mean `dt_us`. 60 FPS не обещать.**"""
i, j = block('**СОСТОЯНИЕ (2026-09-23)')
lines[i:j] = state.split('\n')

s109 = """Дата: 2026-09-24. **Сессия109: УСКОРЕНИЯ НЕТ; ПРОПУСК ПРЕФЕТЧА ПО СЕМЕЙСТВУ ЗАКРЫТ; РУЧКА `cspfree` ПРОВЕРЕНА
(0 РАСХОЖДЕНИЙ) И ДАЁТ Δ СРЕДНЕГО КАДРА −154 МКС ПРИ ПИНЕ, НО СТРАЖ ПО ЧИСЛУ РЫВКОВ НЕ ПРОЙДЕН — НЕ ОТГРУЖЕНА.**
`cspfam` v2 (`bc7d66f`, счётчик созданий пайплайнов в штампах): `ent109` (8 входов ABBA, precache compute выкл) —
FAIL 34 против 12 ⇒ ключ семейства не определяет перестановку, закрыто. `cspfree` (`5770106`, сборка **`2f593229…`**
установлена, умолчание 0): память на поток «запись источника + материализованная специализация → id с пайплайном»,
`MaterializeResources` без замка; `vfy109` GO (0 bad на 2,06 млн, доля попаданий 1,0); `ent109b` FAIL 17 против 7
(ожидания недостроенных 12 против 3; p ≈ 0,03); `frm109` (измерение, печать 04) — Δ`dt` −154,1 мкс (2·SE 121,2).
Аудит (печать `pred/05_audit109.md` `fd27a2f8`): пересчёт CONFIRMED, протокол HOLDS, код NOT REFUTED; предсказания
печати 04 (M4 MISS) не оценивались скорером — исправлено; **рост `gpu_busy_us` +70…90 мкс = ~2 загрузки буферов
посреди прохода на флип**. Источник истины — `C:/kyty/s109/FACTS.md`, в git `docs/local-session-109.md`."""
k = next(x for x, l in enumerate(lines) if l.startswith('Дата: 2026-09-23. **Сессия108:'))
lines[k:k] = s109.split('\n') + ['']
i, j = block('Дата: 2026-09-23. **Сессия105:')
del lines[i:j + 1]

env = """- Сто девятая сессия (**умолчания поведения не сдвинуты; новая ручка — выкл**): **`cspfam` = v2** (с `bc7d66f`;
  умолчание 0): атомарный счётчик созданий compute-пайплайнов `g_compute_creations` (три места вставки в
  `m_compute_pipelines`) в штампах таблицы серий, счётчик `FrameTrace-x` `cspfam_clr`; закрыт (`ent109`). Ручка
  **`cspfree`** (`KYTY_CS_PREFETCH_FREE`, 0..2, **умолчание 0**, ПОСЛЕДНЯЯ строка ручек): префетч compute на потоке
  обхода ищет в памяти на поток (`ProgramCache::PrefetchFree`: `ProgramKey` → запись источника → «специализация → id
  с пайплайном») без `PipelineCache::m_mutex`, материализуя без замка (`MaterializeUnlocked`); 1 — возврат на
  попадании, 2 — проверка (путь под замком всё равно; `cspfree_bad` при равных специализациях и строка
  `CspFreeVerify: MISMATCH`, `cspfree_moved` при разных). Счётчики `cspfree_look/hit/src_miss/spec_miss/mat_fail/clr/
  store/bad/moved` (сырые). `cspfree` — 40-е имя вне `gates_base.txt`; `gates.cpp` 139 записей (111 + 28). **Страж
  первой встречи — только с `KYTY_PIPELINE_PRECACHE=gfx`** (иначе стартовый precache строит всё заранее). Харнесс
  `C:/kyty/s109`: `ent109.py`/`ent109b.py`/`vfy109.py`/`frf109.py`/`frm109.py` (+`make_*`, `test_*`, `mut_*`),
  `go109*.sh`, `gates_free{0,1,2}.txt`, `design109.md` (проект обеих половин удержания обходчика), копии сборок."""
k = next(x for x, l in enumerate(lines) if l.startswith('- Сто восьмая сессия ('))
lines[k:k] = env.split('\n')
text = '\n'.join(lines)
wr(GAME / 'CLAUDE.md', text)
wr(GAME / 'AGENTS.md', text)

h = rd(GAME / 'HANDOFF.md')
start = h.index('Дата: 2026-09-23. **Сессия 108 (кратко;')
new = """Дата: 2026-09-24. **Сессия 109 (кратко; источник истины — `C:/kyty/s109/FACTS.md`, план — ROADMAP §0.1 и
`docs/next-session-110.md`).** Ускорения нет. Пропуск префетча compute по семейству закрыт (v2 — 34 против 12
рывков при выключенном precache compute). Ручка `cspfree` (префетч без замка при попадании в память «источник +
специализация», `5770106`, сборка `2f593229…` установлена, умолчание 0): проверка чиста, Δ среднего кадра −154 мкс при
пине (измерение), но страж по числу рывков не пройден (17 против 7) — в с. 110 страж по длительности. Аудит: пересчёт
CONFIRMED, протокол HOLDS, код NOT REFUTED; рост `gpu_busy_us` при снятии удержания — загрузки буферов посреди прохода.

"""
wr(GAME / 'HANDOFF.md', h[:start] + new + h[start:])
print('ok')
