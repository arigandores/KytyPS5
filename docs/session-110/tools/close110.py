"""Session 110 close: SEALS110 (+ audit addendum), FACTS §7 and the size correction, ROADMAP (items 6-7 corrected, item
8, addition, decision after 110, cycle line, §7 rows), the gates.cpp comment (comment only), next-session-111 note,
game contexts and HANDOFF.  One-shot; LF writes."""
import hashlib
from pathlib import Path

S110 = Path('C:/kyty/s110')
RM = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
GAME = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def edit(path, pairs):
    s = Path(path).read_bytes().decode('utf-8').replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (str(path), a[:80])
        s = s.replace(a, b)
    Path(path).write_bytes(s.encode('utf-8'))


audit = S110 / 'pred' / '04_audit110.md'
with open(S110 / 'SEALS110.txt', 'ab') as f:
    f.write(('%s *pred/04_audit110.md\n' % sha(audit)).encode('ascii'))
A = sha(audit)[:8]

edit(S110 / 'FACTS.md', [
    ("# Session 110 — SHIPPED `cspfree=1`: the walker's compute prefetch takes no lock on a (source, specialization) hit — Δ mean frame −418.7 µs at the pin; the duration guard passes",
     "# Session 110 — SHIPPED `cspfree=1`: the walker's compute prefetch takes no lock on a (source, specialization) hit — Δ mean frame ≈ −200 µs at the pin (pooled, full block; the sealed window read −418.7); the duration guard passes"),
    ("""   2.7× `frm109`'s −154.1 — to the audit). Video `vsh110` (pinned, `cspfree=1` in the gate text): 4 008 frames, 0
   glitches ⇒ SHIP.""", """   2.7× `frm109`'s −154.1). Video `vsh110` (pinned, `cspfree=1` in the gate text): 4 008 frames, 0 glitches ⇒ SHIP.
   **Size corrected by the audit (§7 item 1):** the sealed window (frames 60–88 of each block) caught arm-independent
   ~48 ms hitches mostly in arm-0 tails; over the full block `shp110` −233.1 (2·SE 56.6) and `frm109` −171.3 (2·SE
   70.3) agree; **pooled −202 ± 45 µs ≈ +0.65 % game speed at the pin**. SHIP holds under every window. Seal 02's
   predictions: L1–L4 HIT, **L5 MISS** (D_B/D_A 0.556)."""),
    ("""**Measured.** At the pin in Sky Garden, `cspfree=1` shortens the mean frame by 418.7 µs (t −6.19) in the ship run
(154.1 µs in session 109's measurement of the same arms); with the compute precache off it does not lengthen
dispatch-time stalls (D 10.9 vs 19.6 ms). **Not measured.** The gain without the pin; why the two runs differ 2.7×.""",
     """**Measured.** At the pin in Sky Garden, `cspfree=1` shortens the mean frame by ≈ 200 µs (pooled over `shp110` and
`frm109`, full block, −202 ± 45); with the compute precache off it adds +0.33 ms of post-load stall per 150 s entry and
the duration rule passed (the rule is dominated by one arm-independent startup race — weak, audit §7 item 2); with the
precache on there are 0 stalls. **Not measured.** The gain without the pin."""),
    ("AUDIT_PLACEHOLDER\n", ("One agent, three lenses, sealed as `pred/04_audit110.md` (`%s…`). **Recount CONFIRMED**, **Protocol HOLDS**, "
                            "**Code NOT REFUTED**. Findings: (1) **MAJOR** — the size −418.7 is inflated by the estimator's window "
                            "(frames 60–88): full block −233.1 / −171.3, pooled −202 ± 45 µs; SHIP holds under every window — "
                            "quote ≈ −200 µs; future seals pre-register the full block; (2) **MAJOR** — the D/M duration rule is "
                            "dominated by one arm-independent startup race (shader 497, frame 3) and fails 12 %% of the time "
                            "with no effect; the conclusion stands (post-load +0.33 ms per entry; 0 stalls with the precache on); "
                            "(3) MINOR — seal 02's predictions unscored (L5 MISS), L5's band set after `stl110`'s numbers were "
                            "seen; `check110.py` gaps (pin mode 2, `cspf_have`, env) — none changes a verdict; `cspfree` code "
                            "debts perf-only. Report: `C:/kyty/s110/audit110/AUDIT110.md`.\n") % A),
])

edit(RM, [
    ("""6. **`shp110` (печать `pred/03_shp110.md`, `4f02d284`, 600 с, пин, 96 пар, ДОПУЩЕН) — SHIP: Δ среднего `dt` −418,7 мкс
   (2·SE 135,3, t −6,19)**;""", """6. **`shp110` (печать `pred/03_shp110.md`, `4f02d284`, 600 с, пин, 96 пар, ДОПУЩЕН) — SHIP: Δ среднего `dt` −418,7 мкс
   (2·SE 135,3, t −6,19) в запечатанном окне; РАЗМЕР ПОПРАВЛЕН АУДИТОМ (п. 8): ≈ −200 мкс**;"""),
    ("""   `cspfree_bad` 0, `cs_sync_new`/`cs_sync_wait` 0 — `check110.py` (`2efd7414`) PASS.** Долг §6 закрыт.
""", """   `cspfree_bad` 0, `cs_sync_new`/`cs_sync_wait` 0 — `check110.py` (`2efd7414`) PASS.** Долг §6 закрыт.
8. **Итог сессии 110 и аудит** (одна агент-линза на три стороны, печать `C:/kyty/s110/pred/04_audit110.md`, `{A}…`):
   пересчёт CONFIRMED, протокол HOLDS (в окнах прогонов — только `ScheduleWakeup`), код NOT REFUTED. **MAJOR 1 — размер
   −418,7 завышен окном оценщика** (кадры 60–88 блока поймали не зависящие от плеча рывки ~48 мс в хвостах плеча 0: 21
   против 5); по полному блоку `shp110` −233,1 (2·SE 56,6) и `frm109` −171,3 (2·SE 70,3) согласуются; **пул 192 пар −202
   ± 45 мкс ≈ +0,65 % скорости игры при пине**; SHIP устойчив при любом окне. **MAJOR 2 — правило D/M слабое:** его
   определяет одна не зависящая от плеча стартовая гонка шейдера 497 (кадр 3), при нулевом эффекте оно проваливается
   в 12 % случаев; вывод стоит (после загрузки +0,33 мс на вход; с precache — 0 рывков). MINOR: предсказания печати 02
   не оценивались (L5 MISS), полоса L5 выставлена после чисел `stl110`; пробелы `check110.py`; долги кода `cspfree` —
   только производительность.

**Дополнение сессии 110: ОТГРУЖЕН `cspfree=1` — префетч compute на потоке обхода не берёт `PipelineCache::m_mutex` при
попадании в память «источник + специализация»; Δ среднего кадра ≈ −200 мкс при пине (пул `shp110`+`frm109` по полному
блоку, −202 ± 45; ≈ +0,65 % скорости игры)**; страж по длительности рывков пройден; сборка `072861c8…`, видео чистые.
Итоги — `docs/local-session-110.md`.

**РЕШЕНИЕ ИСПОЛНИТЕЛЯ ПОСЛЕ С. 110 (записано до действия; основание — аудит `pred/04`).**
1. **Главный оценщик будущих ABBA — ПОЛНЫЙ блок** (или кадры 10–89) вместо окна 60–88; окно 60–88 печатается как
   второстепенное. Правило отгрузки (планка Δ`dt` ≤ −100 мкс при 2·SE < 0) применяется к главному оценщику.
2. **Будущие стражи по длительности** исключают стартовый интервал до первой строки `FrameTrace-x` из решающей суммы
   (он печатается отдельно) и ограничивают послезагрузочную часть отдельно.
3. **Сессия 111:** наблюдение конкуренции при новых умолчаниях (`plkstat=1`), затем `daslot` (тег 1) по
   `design109.md` §A; план `docs/next-session-111.md`.
4. Размеры прошлых отгрузок (`dawalk` −265,9, `dabatch` −169,3) получены тем же оконным оценщиком — не переоцениваются,
   но цитируются с этой оговоркой.
""".replace('{A}', A)),
    ("""длительности в с. 110. 60 FPS — направление без маршрута с живой оценкой.""",
     """длительности в с. 110. **`cspfree=1` отгружен в с. 110: ≈ −200 мкс при пине** (пул по полному блоку; окно 60–88 дало
−418,7 — завышено). 60 FPS — направление без маршрута с живой оценкой."""),
    ("""| **префетч compute под `PipelineCache::m_mutex` на потоке обхода** — в установившейся сцене `cspf_have` 266/266, `cspf_new` 0 (`obs107`): чистое удержание 342 мкс/кадр; память по user SGPR закрыта (`cspmemo`, VERIFY FAIL, 44 % попаданий). С. 108: `cspfam=4` — Δ`dt` −141,8 мкс, откат стражем. **С. 109: семейство закрыто (v2 FAIL 34/12); `cspfree` — проверка чиста, Δ`dt` −154,1 мкс (`frm109`), страж по числу событий FAIL (17/7)** | страж по длительности рывков, затем ABBA отгрузки (решение после с. 109) | **106 → 110** |""",
     """| ~~**префетч compute под `PipelineCache::m_mutex` на потоке обхода**~~ **ЗАКРЫТ в с. 110: `cspfree=1` отгружен (≈ −200 мкс при пине, пул по полному блоку; страж по длительности PASS)** | — | **106 → 110** |
| долги кода `cspfree` при отгрузке: повторная сверка зеркала эпохи после материализации без замка; «null source» отдельно от «moved»; один `PipelineCache` на процесс | при следующей правке с прогоном проверки | **110** |
| оконный оценщик (кадры 60–88) ловит не зависящие от плеча рывки: главный оценщик — полный блок (решение после с. 110) | в следующих производных скорерах | **110** |"""),
])

edit('C:/kyty/KytyPS5/src/common/gates.cpp', [
    ("""    // Read once per prefetch call, so it CAN be a schedule arm. Session 110: default 1 after the
    // duration guard (pred/02_stl110b.md: PASS) and the sealed ship ABBA (pred/03_shp110.md: d mean dt
    // -418.7 us, 2SE 135.3; video clean).""", """    // Read once per prefetch call, so it CAN be a schedule arm. Session 110: default 1 after the
    // duration guard (pred/02_stl110b.md: PASS) and the sealed ship ABBA (pred/03_shp110.md: bar met,
    // video clean); size ~ -200 us a frame at the pin (pooled full-block estimate, audit pred/04)."""),
])
edit('C:/kyty/KytyPS5/docs/next-session-111.md', [
    ("""cspfree=1`. Shipped in session 110: `cspfree=1` — Δ mean `dt` −418.7 µs in its ship ABBA (2·SE 135.3; −154.1 in session
109's measurement of the same arms).""", """cspfree=1`. Shipped in session 110: `cspfree=1` — Δ mean frame ≈ −200 µs at the pin (pooled full-block estimate of
the ship run and session 109's measurement, −202 ± 45; the sealed 60–88 window read −418.7 — inflated, audit)."""),
    ("""5. Effect sizes vary between 600 s runs of the same arms (−154 vs −419 µs for `cspfree`): quote the ship run with its
   CI and do not add gains.""", """5. The main estimator of every new ABBA seal is the FULL block (or frames 10–89); the 60–88 window is printed as
   secondary (it caught arm-independent ~48 ms hitches in session 110). Do not add gains."""),
])

# game contexts and HANDOFF
c = (GAME / 'CLAUDE.md').read_bytes().decode('utf-8').replace('\r\n', '\n')
lines = c.split('\n')


def block(prefix):
    i = next(k for k, l in enumerate(lines) if l.startswith(prefix))
    j = i
    while j < len(lines) and lines[j].strip():
        j += 1
    return i, j


i, j = block('**СОСТОЯНИЕ (2026-09-24)')
lines[i:j] = """**СОСТОЯНИЕ (2026-09-24): ЦИКЛ СЕССИЙ ИДЁТ** (пользователь, /loop: сессии подряд до «стоп», вопросов не задавать,
после исчерпания лимитов продолжать; push — нет). Хартбит — cron в беседе (:17 и :47); во время запечатанного
прогона он не делает ни одного вызова инструментов; все цепочки прогонов держат замок `C:/kyty/SEALED_RUN.lock`;
состояние для хартбита — `C:/kyty/LOOP_STATE.md`. **Сессия 110 закрыта (отгружен `cspfree=1`)**, следующая —
`docs/next-session-111.md` (наблюдение конкуренции, затем `daslot` — очередь M1 вне `m_mutex`). Решения после с.
106–110 (`ROADMAP.md` §0.1) действуют: фикстуры на каждый член и ветку, мутанты убиваются; страж — с экспозицией
(precache compute выкл) и по длительности; **главный оценщик ABBA — полный блок**. **Скорость игры = 16 667 / mean
`dt_us`. 60 FPS не обещать.**""".split('\n')
s110 = """Дата: 2026-09-24. **Сессия110: ОТГРУЖЕН `cspfree=1` — ПРЕФЕТЧ COMPUTE ОБХОДЧИКА НЕ БЕРЁТ `m_mutex` ПРИ ПОПАДАНИИ;
Δ СРЕДНЕГО КАДРА ≈ −200 МКС ПРИ ПИНЕ (≈ +0,65 % СКОРОСТИ ИГРЫ).** Инструмент длительности рывков на диспатче (`3d8af4c`:
`cs_sync_new_us`/`cs_sync_wait_us`, строки `CsStall:`). Страж по длительности: `stl110` NOT_ADMITTED (дефект сверки скорера
— стартовые рывки до первой строки кадра), повтор `stl110b` PASS (D 10,9 против 19,6 мс, самый долгий 1,6 против 12,3 мс).
Отгрузочный ABBA `shp110`: SHIP, окно 60–88 дало −418,7 мкс, аудит (печать `pred/04_audit110.md`): завышено окном, пул по
полному блоку с `frm109` −202 ± 45 мкс. Умолчание `cspfree=1` (`0776f6a`), сборка **`072861c8…`** установлена, видео
`vid110` 4 004 кадра, 0 глитчей. Источник истины — `C:/kyty/s110/FACTS.md`, в git `docs/local-session-110.md`."""
k = next(x for x, l in enumerate(lines) if l.startswith('Дата: 2026-09-24. **Сессия109:'))
lines[k:k] = s110.split('\n') + ['']
i, j = block('Дата: 2026-09-23. **Сессия106:')
del lines[i:j + 1]
env = """- Сто десятая сессия (**одно отгруженное умолчание — ручка `cspfree` 0 → 1**): **`KYTY_CS_PREFETCH_FREE`** / **`cspfree`**
  теперь **по умолчанию 1** (Δ ≈ −200 мкс при пине). Новые счётчики `FrameTrace-x` (сырые мкс, только в трассируемых
  прогонах) **`cs_sync_new_us`**, **`cs_sync_wait_us`** — стена рывка на потоке диспатча в `GetComputePipeline`
  (синхронная компиляция / ожидание недостроенной записи) и строка лога на каждый рывок **`CsStall: kind=new|wait us=<N>
  id=<id> hash=0x<hash>`** (всегда, ≤ 4 096 строк; рывки старта логируются до первой строки `FrameTrace-x`, их счётчики
  не отчитываются). Главная строка `FrameTrace` не менялась. Харнесс `C:/kyty/s110`: `stl110.py`/`stl110b.py`/`shp110.py`
  (+`make_*`, `test_*`, `mut_*`), `check110.py`, `go110*.sh`, копия сборки `kyty_emulator_b3f7a2c9.exe`."""
k = next(x for x, l in enumerate(lines) if l.startswith('- Сто девятая сессия ('))
lines[k:k] = env.split('\n')
text = '\n'.join(lines)
(GAME / 'CLAUDE.md').write_bytes(text.encode('utf-8'))
(GAME / 'AGENTS.md').write_bytes(text.encode('utf-8'))
h = (GAME / 'HANDOFF.md').read_bytes().decode('utf-8').replace('\r\n', '\n')
start = h.index('Дата: 2026-09-24. **Сессия 109 (кратко;')
new = """Дата: 2026-09-24. **Сессия 110 (кратко; источник истины — `C:/kyty/s110/FACTS.md`, план — ROADMAP §0.1 и
`docs/next-session-111.md`).** Отгружен `cspfree=1` (префетч compute обходчика без `PipelineCache::m_mutex` при попадании
в память «источник + специализация»): Δ среднего кадра ≈ −200 мкс при пине (пул по полному блоку; запечатанное окно дало
−418,7 — завышено, аудит). Страж по длительности рывков пройден (`stl110b`). Сборка `072861c8…` установлена, видео чистые.
Аудит: пересчёт CONFIRMED, протокол HOLDS, код NOT REFUTED; главный оценщик будущих ABBA — полный блок.

"""
(GAME / 'HANDOFF.md').write_bytes((h[:start] + new + h[start:]).encode('utf-8'))
print('ok', A)
