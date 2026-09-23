"""Session 104: corrections from the claims lens on the final texts."""
F = {
    'road': 'C:/kyty/KytyPS5/docs/ROADMAP.md',
    'facts': 'C:/kyty/s104/FACTS.md',
    'plan': 'C:/kyty/KytyPS5/docs/next-session-105.md',
    'claude': 'C:/Users/<user>/OneDrive/Desktop/ps5 em/CLAUDE.md',
    'handoff': 'C:/Users/<user>/OneDrive/Desktop/ps5 em/HANDOFF.md',
}
T = {k: open(p, encoding='utf-8').read() for k, p in F.items()}


def rep(k, old, new, cnt=1):
    n = T[k].count(old)
    assert n == cnt, (k, old[:90], n)
    T[k] = T[k].replace(old, new)


# ---- ROADMAP §0.1 items 1-2: strike the withdrawn claims inline, correct the numbers
rep('road', '''1. **Плато вблэнка НЕ держит СРЕДНЮЮ частоту — поправка к §4.** Флипы копятся в очереди ёмкостью 16
   (`videoOut.cpp:59`, `WaitForSubmitSlot` не блокирует GuestGpu, пока она не полна), поэтому тик вблэнка
   квантует отдельные интервалы, а среднее идёт за работой GuestGpu: в установившихся окнах прошлых сессий
   Sky Garden средний `dt_us` 30,7…31,9 мс при 10–16 % интервалов в один вблэнк (`dab102a` 31,43 мс,
   `ckpt102_entry1` 31,83, `pl96a` 31,14; средняя треть прогона), пустыня 20,1…25,4 мс (`sky61d`, `sky60`,
   `sky63a`: смеси 1/2/3 вблэнков); в `vid103` GuestGpu занят 97,3 % стены (`cpu_gpu_us/dt_us`). **Экономия CPU
   GuestGpu переходит в скорость игры почти один к одному (коэффициент ≈ 0,97–0,98), без порога 33,3 мс.**''',
    '''1. **Плато вблэнка НЕ держит СРЕДНЮЮ частоту — поправка к §4.** ~~Флипы копятся в очереди ёмкостью 16
   (`videoOut.cpp:59`, `WaitForSubmitSlot` не блокирует GuestGpu, пока она не полна)~~ (механизм отозван
   аудитом, см. поправку ниже), поэтому тик вблэнка
   квантует отдельные интервалы, а среднее идёт за работой GuestGpu: в установившихся окнах прошлых сессий
   Sky Garden средний `dt_us` **31,15…31,83 мс при 9,7–13,5 %** интервалов в один вблэнк (`dab102a` 31,43 мс,
   `ckpt102_entry1` 31,83, `pl96a` 31,15; средняя треть прогона; пересчёт аудита), ~~пустыня 20,1…25,4 мс (`sky61d`, `sky60`,
   `sky63a`: смеси 1/2/3 вблэнков)~~ (отозвано: окна — смесь фазы 60 FPS и сцены); в `vid103` GuestGpu занят 97,3 % стены (`cpu_gpu_us/dt_us`). **Экономия CPU
   GuestGpu переходит в скорость игры ~~почти один к одному (коэффициент ≈ 0,97–0,98)~~ (отозвано: 0,58 в `dwk104`, 1,02 в `sh104` — мерить Δ`dt`), без порога 33,3 мс.**''')
rep('road', '''   стены (`vid103`), и нет механизма, по которому выпуск флипа вне тика этот простой снимает (GuestGpu не
   ждёт флипов). Гейт `vrrflip` НЕ строится.''', '''   стены (`vid103`), и нет механизма, по которому выпуск флипа вне тика этот простой снимает ~~(GuestGpu не
   ждёт флипов)~~ (отозвано: ждёт через `R_WAIT_FLIP_DONE`, но с запасом). Гейт `vrrflip` НЕ строится.''')
rep('road', '''   16 ни при чём. Среднее свободно, потому что у этого ожидания есть запас, пока работа кадра больше ~20 мс
   (пиковый `lat_us` 19,7–20,3 мс).''', '''   16 ни при чём. Среднее свободно, потому что у этого ожидания есть запас, пока работа кадра больше ~20 мс
   [I] (пиковый `lat_us` 19,6–20,3 мс в установившихся окнах; выбросы 21,6–25,4 мс).''')
rep('road', '''   напрямую.** **V закрыт только в этом режиме:** при работе кадра < ~20 мс двойной буфер начинает держать
   GuestGpu, и выпуск флипа вне тика снова имеет смысл — это касается конечной цели маршрута A (21–26 мс).''',
    '''   напрямую.** **V закрыт только в этом режиме:** при работе кадра < ~20 мс двойной буфер, по-видимому [I],
   начинает держать GuestGpu, и выпуск флипа вне тика снова может иметь смысл — это касается конечной цели
   маршрута A (21–26 мс); не измерено.''')
# item 7: session-60 numbers
rep('road', '''   GuestGpu (есть с с. 59, умолчание 0; в с. 59–60 мерился без ABBA и без пина: −0,3…−1,4 % CPU/дров при
   разрешении ±1,4 %).''', '''   GuestGpu (есть с с. 59, умолчание 0; в с. 59–60 мерился без ABBA и без пина: при `dawalklead=2` −0,3…−1,4 %
   CPU/дров, при `dawalklead=1` +2,4 / −0,4 / −1,6 %, разрешение ±1,4 % — поправка линзы заявлений).''')
# item 8(a): gates_base done since
rep('road', '''   Видео-проход новой сборки — долг §6, до конца сессии. `gates_base.txt` харнесса пинит `dawalk=0` — в порте
   с. 105 пин сменить на 1 (хэш `gates_base.txt` меняется; до этого любой прогон по `gates_base.txt` идёт со
   старым значением).''', '''   Видео-проход новой сборки — долг §6, до конца сессии. `gates_base.txt` харнесса пинит `dawalk=0` — в порте
   с. 105 пин сменить на 1 (хэш `gates_base.txt` меняется; до этого любой прогон по `gates_base.txt` идёт со
   старым значением). **Сделано в той же сессии после записи (05:07, раньше, чем записано здесь):** пин
   `dawalk=1` правкой одного байта (1 092 Б / 99 имён, sha256 `303a7849…`), `gates_base.json` тоже переписан;
   архивные скореры `a104.py`/`dwk104.py` пинят `GATES_SHA` `00c116dc…` и IDENTITY установленного exe, поэтому
   принятые прогоны ими больше не переоцениваются.''')
# addition: +0.8 % qualifier
rep('road', '''`dwk104` (печать `pred/03`): Δ`cpu_net` −458,5 мкс, **Δ среднего `dt` −265,9 мкс ⇒ ≈ +0,8 % скорости игры в Sky
Garden**;''', '''`dwk104` (печать `pred/03`): Δ`cpu_net` −458,5 мкс, **Δ среднего `dt` −265,9 мкс ⇒ ≈ +0,8 % скорости игры в Sky
Garden** (ABBA при пине GPU-часов; на обычной настройке без пина, где ступень DRS свободна, не проверено);''')
# decision after 104: session-60 numbers and the bar's power
rep('road', '''при `dawalk=1` (с. 60: при 2 `da_late` 0,0 и `da_miss` 206 против 8,0 и 263–302 при 1 — может вернуть часть''',
    '''при `dawalk=1` (с. 60, средние фаз `log_sky60`, без ABBA: при 2 `da_late` 0,00 и `da_miss` 202 против 7,8–8,3 и
309–315 при 1 — может вернуть часть''')
rep('road', '''`dt` ≤ −100 мкс при 2·SE, не накрывающем 0, работа и площадь в контролях, видео-проход; Δ`cpu_net` —
сопутствующая мера.''', '''`dt` ≤ −100 мкс при 2·SE, не накрывающем 0, работа и площадь в контролях, видео-проход; Δ`cpu_net` —
сопутствующая мера. Мощность: при SD пары Δ`dt` ≈ 549 мкс (`dwk104`) прогон 600 с даёт 2·SE ≈ 115 мкс, то есть
действующая планка ≈ −115 мкс; более слабый эффект требует более длинного прогона.''')
# §4 note
rep('road', '''идёт за работой (Sky Garden 30,7…31,9 мс в прошлых прогонах; §0.1, решения с. 104). Ниже ~20 мс двойной буфер
держит GuestGpu, и текст ниже снова верен.''', '''идёт за работой (Sky Garden 31,15…31,83 мс в прошлых прогонах; §0.1, решения с. 104). Ниже ~20 мс двойной буфер,
по-видимому [I, не измерено], держит GuestGpu, и текст ниже снова становится верен.''')
# §7 V row
rep('road', '''**переоткрывается, если работа кадра упадёт ниже ~20 мс** | — | **103 → 104** |''',
    '''**вероятно [I] переоткрывается, если работа кадра упадёт ниже ~20 мс** | — | **103 → 104** |''')
# stale A statements
rep('road', '''| A — параллельная запись по слайсам | **20,8 мс = 30 FPS** | `S` больше всего бюджета кадра 60 FPS (с. 83, K2) |''',
    '''| A — параллельная запись по слайсам | **20,8 мс = 30 FPS** (с. 104: «= 30 FPS» верно для табло одного интервала, не для среднего — §4; для «максимума FPS» A переоткрыт и прошёл этап 1, G = 5,7 мс) | `S` больше всего бюджета кадра 60 FPS (с. 83, K2) |''')
rep('road', '''### A. Параллельная запись по слайсам — **ЗАКРЫТ** критерием отмены K2 (сессия 83)''',
    '''### A. Параллельная запись по слайсам — **ЗАКРЫТ** критерием отмены K2 (сессия 83) для 60 FPS; **для «максимума FPS» переоткрыт в с. 104 и идёт этапами (§0.1, решения с. 104, п. 6 и 8)**''')

# ---- FACTS
rep('facts', '''(the audit: those short entries include unsettled early frames — steady windows have ≤ 1.3 % three-vblank
and 9–14 % one-vblank frames).''', '''(the audit: those short entries include unsettled early frames — steady windows of runs without recording or
instruments have ≤ 1.3 % three-vblank and 9–14 % one-vblank frames; with recording `vid103` has 7.2 %, and the
instrumented `sh104` middle third 5.1 %).''')
rep('facts', '''   **≈ +0.8 % game speed in Sky Garden, from Δdt** (−265.9 µs of ~32 ms).''',
    '''   **≈ +0.8 % game speed in Sky Garden, from Δdt** (−265.9 µs of 32 162; ABBA with the GPU clock pinned — on
   the default unpinned setup, where the DRS step moves, not tested).''')
rep('facts', '''   names and would change the harness composition — disclosed in `pred/04`).''',
    '''   names and would change the harness composition — disclosed in `pred/04`); `gates_base.json` was rewritten
   too, and the archived scorers pin `GATES_SHA` `00c116dc…` as well as the installed exe, so they no longer
   admit this session's runs.''')
rep('facts', '''   also had the (then) incompatible seed and one 212.9 ms hitch. Load could only push it slower; the
   reading stands.''', '''   also had the (then) incompatible seed, 21 `AsyncPipelines: skipped draw` and one held flip (the
   marker that made `mut104` INVALID; `pred/01` has no such control) and one 212.9 ms hitch. Load could
   only push it slower; the reading stands.''')
rep('facts', '''sessions 59–60 it was measured without ABBA or clock pin (−0.3…−1.4 % CPU a draw, inside ±1.4 %
resolution) and left 0.''', '''sessions 59–60 it was measured without ABBA or clock pin (with `dawalklead=2` −0.3…−1.4 % CPU a draw,
with lead 1 +2.4 / −0.4 / −1.6 %, inside ±1.4 % resolution) and left 0.''')
rep('facts', '''off-CPU time under `dawalk=1`; the plateau statement below ~20 ms of work (there the double buffer binds);''',
    '''off-CPU time under `dawalk=1`; the plateau statement below ~20 ms of work (there the double buffer probably
binds [I]); the gain on the unpinned default setup;''')

# ---- plan 105
rep('plan', '''**Open the report with these numbers:** Sky Garden steady mean `dt_us` ≈ 31.6 ms on the shipped default
(`dwk104` arm `dawalk=1`: 31 618 µs; `cpu_net_us` 30 744);''', '''**Open the report with these numbers:** Sky Garden steady mean `dt_us` ≈ 31.6 ms in the pinned `dwk104` arm
`dawalk=1` (31 618 µs; `cpu_net_us` 30 744; the unpinned default setup is not measured);''')
rep('plan', '''* **Candidate 1: `dawalklead=1|2` with `dawalk=1`.** Session 60 (no ABBA, no pin): lead 2 gave `da_late` 0.0
  and `da_miss` 206 against lead 1's 8.0 and 263–302.''', '''* **Candidate 1: `dawalklead=1|2` with `dawalk=1`.** Session 60 (phase means of `log_sky60`, no ABBA, no pin):
  lead 2 gave `da_late` 0.00 and `da_miss` 202 against lead 1's 7.8–8.3 and 309–315.''')
rep('plan', '''* **Ship bar (recorded after session 104):** Δ mean `dt` ≤ −100 µs with 2·SE excluding 0;''',
    '''* **Ship bar (recorded after session 104):** Δ mean `dt` ≤ −100 µs with 2·SE excluding 0 (at the `dwk104`
  pair SD of 549 µs a 600 s run gives 2·SE ≈ 115 µs, so the effective bar is ≈ −115 µs);''')

# ---- CLAUDE.md
rep('claude', '''(−458 мкс CPU, −266 мкс среднего кадра ≈ +0,8 % скорости игры);''',
    '''(−458 мкс CPU, −266 мкс среднего кадра ≈ +0,8 % скорости игры при пине GPU-часов);''')
rep('claude', '''`R_WAIT_FLIP_DONE` при двух дисплейных буферах, у ожидания запас, пока работа кадра > ~20 мс; маршрут V закрыт в
этом режиме.''', '''`R_WAIT_FLIP_DONE` при двух дисплейных буферах, у ожидания запас, пока работа кадра > ~20 мс [I]; маршрут V закрыт в
этом режиме.''')

# ---- HANDOFF
rep('handoff', '''`docs/next-session-105.md`).** `dawalk=1` отгружен по умолчанию (Δ среднего кадра −265,9 мкс ≈ +0,8 % скорости игры в
Sky Garden; сборка `61ae7347…`); среднее кадра не квантуется вблэнком при работе > ~20 мс (механизм — двойной буфер
`R_WAIT_FLIP_DONE`); маршрут V закрыт в этом режиме; маршрут A прошёл «убить или идти» (G = 5,7 мс); seed шейдеров
пересобран (512 / 638).''', '''`docs/next-session-105.md`).** `dawalk=1` отгружен по умолчанию (Δ среднего кадра −265,9 мкс ≈ +0,8 % скорости игры в
Sky Garden, ABBA при пине GPU-часов; сборка `61ae7347…`; `gates_base.txt` харнесса пинит `dawalk=1`, sha256 `303a7849…`);
в Sky Garden среднее кадра не квантуется вблэнком — ожидание флипа `R_WAIT_FLIP_DONE` (двойной буфер) имеет запас, пока
работа кадра > ~20 мс [I]; маршрут V закрыт в этом режиме; маршрут A прошёл «убить или идти» (G = 5,7 мс); seed шейдеров
пересобран (512 / 638). Раскрыто аудитом (MAJOR): во время экрана `reg104` агент читал файлы.''')

for k, p in F.items():
    open(p, 'w', encoding='utf-8', newline='\n').write(T[k])
import shutil
shutil.copyfile(F['claude'], 'C:/Users/<user>/OneDrive/Desktop/ps5 em/AGENTS.md')
shutil.copyfile(F['facts'], 'C:/kyty/KytyPS5/docs/local-session-104.md')
print('ok')
