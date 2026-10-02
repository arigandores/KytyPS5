# FS2c (HPP-383): writes pred/01_fs2.md - the seal of the FS2c series (ROADMAP p.298(g)-(d), p.327(g), p.329(a)-(b), p.295(b), p.296(b),
# (d), p.273(e)(3), p.287(v)(5), p.294(b), p.306(g)).  The text of p.298(g)-(d), p.327(g) and p.329(b) is copied verbatim from git
# (KytyPS5 COMMIT:docs/ROADMAP.md); every sealed file gets one 'seal: <sha256> <name>' line.  UTF-8, LF.
#   usage: python mk_seal_fs2.py <UTC when> <COMMIT>
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/f287/fs2c'
sys.path.insert(0, HERE)
import fs2_read as R  # noqa: E402

GIT = 'C:/Program Files/Git/cmd/git.exe'
when, COMMIT = sys.argv[1], sys.argv[2]
road = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'show', '%s:docs/ROADMAP.md' % COMMIT], capture_output=True,
                      check=True).stdout.decode('utf-8').split('\n')


def item(n):
    return next(k for k, l in enumerate(road) if l.startswith('%d. **' % n))


def sub(n, start, stop=None):
    i = item(n)
    a = next(k for k in range(i, len(road)) if road[k].lstrip().startswith(start))
    if stop is None:
        return a, a
    b = next(k for k in range(a + 1, len(road)) if road[k].lstrip().startswith(stop))
    return a, b


def anchor(k):
    return road[k].strip()[:40]


def ref(k):
    return '`%s:docs/ROADMAP.md:%d` «%s» (контроль +1 — %d «%s»)' % (COMMIT, k + 1, anchor(k), k + 2, anchor(k + 1))


g0, g1 = sub(298, '(г) **Регрессия FS2c', '(е) **Звенья')
d0, _ = sub(298, '(д) **Установка FS2')
q0, q1 = sub(327, '(г) **Отгрузка — FS2', '(д) **Реестр**')
r0, r1 = sub(329, '(б) **RC1 — Принято.**', '(в) **Замечания')
w0, _ = sub(295, '(б) **RC1 — решение (A).**')
b0, _ = sub(296, '(б) **Член (б) — решение лида.**')
p0, _ = sub(296, '(д) **Процесс:**')
f0, _ = sub(273, '(е) **Итерация F5 трека F = Б37')
f3 = next(k for k in range(f0, len(road)) if '(3) **«FIXED» — все:**' in road[k])
v5 = next(k for k in range(item(287), len(road)) if road[k].lstrip().startswith('(5) **Входы под замком на копии бинаря F6c'))
a0, _ = sub(294, '(б) **RC1 — Принято, член критерия F6')
e0, _ = sub(306, '(г) **Ответы на В1–В2 F6e**')
z0, _ = sub(273, '(з) **Аудит (п. 272) и «Процесс»')
c0, _ = sub(329, '(а) **Члены задания:**')
k0, _ = sub(322, '(г) **Порядок замка после с. 146:**')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def path(n):
    return n if n.startswith('C:/') else os.path.join(HERE, n)


GAME = 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'
DAC = 'dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e'
assert sha(GAME) == DAC and sha('C:/kyty/s146/kyty_emulator_dac02fb9.exe') == DAC, 'installed or pinned build is not dac02fb9'
assert sha('C:/kyty/f287/bin/kyty_emulator_bbad499c.exe') == R.BIN_SHA
OUTS = ('test_fs2_read.out.txt', 'test_go_fs2.out.txt', 'runs/stoprule_ref.out.txt')
L = []
A = L.append
A('# Печать 01 звена FS2c трека F — регрессия второго бинаря отгрузки FS2 (`pred/01_fs2.md`)')
A('')
A('Звено FS2c (`HPP-383`, Harness Engineer). Записана %s (UTC по `date -u`) ДО первого прогона серии. Основание — `ROADMAP.md` «СЕССИЯ 122»' % when)
A('(KytyPS5 `%s`, HEAD на момент печати):' % COMMIT)
A('')
A('- **п. 298(г)** — %s; **п. 298(д)** — %s;' % (ref(g0), ref(d0)))
A('- **п. 327(г)** (члены Б9а печати FS2c) — %s;' % ref(q0))
A('- **п. 329(а)–(б)** (бинарь FS2 `bbad499c`, откат FS2) — %s; %s;' % (ref(c0), ref(r0)))
A('- **п. 295(б)** (форма W, члены допуска (1)–(4)) — %s;' % ref(w0))
A('- **п. 296(б)** (буква члена (б): VUID следующей строкой) — %s; **п. 296(д)** (эталон с фикстурой) — %s;' % (ref(b0), ref(p0)))
A('- **п. 273(е)(3)** (буквы (а), (б), (в) Б37) — %s;' % ref(f3))
A('- **п. 287(в)(5)** (члены входа `=1` на `timestop_casino`) — %s; **п. 294(б)** — %s; **п. 306(г)** В1 (И10) — %s;' % (ref(v5), ref(a0), ref(e0)))
A('- **п. 273(з)** (событие окна) — %s; **п. 322(г)** (очередь замка P > F > S) — %s.' % (ref(z0), ref(k0)))
A('')
A('Пункты после выдачи звена, прочитанные перед печатью: п. 327 (члены Б9а — комментарий лида `caffb0db`, выписка')
A('`C:/kyty/f287/fs2c/members_b9a_p327g.md`), п. 328 (чистка диска — папки `f287`, `s144`, `s146` не трогаются), п. 329 (FS2b принят; RC1 меняет')
A('строку отката FS2d, печать FS2c не меняется). Объём звена меняет только п. 327(г). Мутантов нет (задание звена их не называет; как F5c, F6e).')
A('После печати `fs2_read.py`, `go_fs2.sh`, `win_fs2.py` и наборы не меняются; изменение — новая печать.')
A('')
A('## 1. Буква (дословно из git)')
A('')
A('```')
L.extend(road[g0:d0 + 2])
A('```')
A('')
A('```')
L.extend(road[q0:q1])
A('```')
A('')
A('```')
L.extend(road[r0:r1])
A('```')
A('')
A('## 2. Бинарь, установленная сборка, кэши, окно замка')
A('')
A('- Бинарь — только копия FS2a `C:/kyty/f287/bin/kyty_emulator_bbad499c.exe`, sha256 `%s` (п. 329(а)); сверка копии и' % R.BIN_SHA)
A('  установленного файла перед КАЖДЫМ тегом (п. 286(б)); строки в бинаре до замка: `FixMinimize: on`, `FixB9a: on`, `TestMinimize: armed`,')
A('  `SwapchainZeroExtent: begin`, `AudioPropagation: calls`, подпись трансляции `56189185…` (= FS: кэш варианта общий). Пересборки нет.')
A('- Установленная сборка к моменту серии — `dac02fb9…` (п. 300(б), шаг 0 с. 146; закреплённая копия `C:/kyty/s146/kyty_emulator_dac02fb9.exe`),')
A('  sha256 сверен этой печатью (`%s`); серия ставит FS2 один раз и возвращает **`dac02fb9`** по sha в ловушке EXIT' % DAC)
A('  (задание: «возврат `9235a7ac` (или бинаря, установленного к моменту серии, — строкой)» — строка: возвращается `dac02fb9`).')
A('- Кэши (п. 228(в)): `_ShaderCache/PPSA21564` (корень, каталоги вариантов, `pipelines.bin`) — копия до установки, списки содержимого и каталогов')
A('  вариантов, манифест подписей; GLCache — копия и манифест `cachemf146.py`; `_PipelineCache` — копия и список (**член исполнителя [I]**, как FSc).')
A('  EXIT: кэш прогона переносится в `*_run/<UTC>/`, копия возвращается, списки = до серии; иначе `RESTORE FAILED` и файл `C:/kyty/f287/STOP`.')
A('- Окно замка (`win_fs2.py`, строка `times.txt` с ответом API прямо перед замком): `HPP-382`, `HPP-381` — `done`; `HPP-370`, `HPP-377` — `done`')
A('  или `in_review`; `HPP-393` (P21, трек P — раньше F, п. 322(г)) — не `todo`/`in_progress`; у всех `executionRunId` пуст. Шлюз: `procload.py`')
A('  (вывод через маску `<app>`, п. 324(и)), имя-шлюз, CPU < 15 %, `idle142` (ожидание до 300 с, один повтор отказа BUSY `enter_scene.py`,')
A('  п. 279(в)), свободно на `C:` ≥ 60 ГБ (**член исполнителя [I]**, по п. 295(в) с. 145: W без фильтра пишет лог до ≈ 1,7 ГБ).')
A('')
A('## 3. Теги (по порядку, по одной попытке; `-lvl`, `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`, `KYTY_GPU_CHECKPOINTS` не передаётся)')
A('')
A('| тег | уровень | форма | окружение сверх умолчаний | удержание (стена) |')
A('|---|---|---|---|---|')
A('| `fs2_w` | `underwater_aerial_garden` | W п. 295(б): `--vulkan-validation true`, precache по умолчанию | `VK_LAYER_PATH`, `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000`, `KYTY_TEST_MINIMIZE=60:10`; ни одной `KYTY_FIX_*`; без `VK_LAYER_MESSAGE_ID_FILTER` | 310 с, `--stable-draws 300 --timeout 600` |')
A('| `fs2_w0` | `underwater_aerial_garden` | то же | то же + `KYTY_FIX_MINIMIZE=0` | 310 с (ожидается остановка) |')
A('| `fs2_v` | `underwater_aerial_garden` | V: без валидации, `KYTY_REC` | `KYTY_TEST_MINIMIZE=60:10` | 330 с, `--stable-draws 300 --timeout 480` |')
A('| `fs2_tw` | `timestop_casino` | прогрев: без видео, **не читается** | — | 60 с, `--stable-draws 100 --timeout 480` |')
A('| `fs2_t` | `timestop_casino` | V F6e: без валидации, `KYTY_REC`, `FrameTrace` | — | 125 с (читается Σ`dt` ≥ 120 с), `--stable-draws 100` |')
A('| `fs2_tr` | `timestop_casino` | как `fs2_t` — только если ридер `fs2_t` сказал `repeat-k3: fs2_tr` | — | 125 с |')
A('')
A('После `fs2_v`, `fs2_t`, `fs2_tr`: `s51_vidglitch.py rec_<тег>.mp4 4 6` и лист `sheet142.py` → `sheet_<тег>.png` (лиду: `sheet_fs2_v.png`;')
A('`sheet_fs2_t.png` против `C:/kyty/f287/f6e/sheet_f6e_a2.png`). Скорер — `fs2_read.py --tag <тег> --json runs/<тег>.read.json` → `score_<тег>.txt`;')
A('сводка — `fs2_read.py --summary` → `summary_fs2.txt`.')
A('')
A('## 4. Члены и вердикт тега (`fs2_read.py`)')
A('')
A('Порядок вердикта: `NOT ADMITTED` (форма прогона) → `INVALID` (`FixB9a: on` ≠ 1 на `fs2_w`, `fs2_v`, `fs2_t`: ошибка формы тега, п. 327(г)(1)) →')
A('`NOT EVALUABLE` (контроли стенда и плеча; событие окна вне стенда — п. 273(з)) / `WINDOW EVENT` (`fs2_t`) → буква.')
A('')
A('**Допуск (все теги):** одна попытка; бинарь json = `bbad499c…`; `-lvl <уровень>`; `KYTY_FIX_*` в окружении json — ровно `{}` (у `fs2_w0` —')
A('`{KYTY_FIX_MINIMIZE: 0}`); `KYTY_TEST_MINIMIZE=60:10` у стендовых тегов, не задана у `timestop_casino`; не заданы `KYTY_PIPELINE_PRECACHE`,')
A('`KYTY_GPU_CHECKPOINTS`, `KYTY_PRINT_NAMES`, `KYTY_S_PCW`, `KYTY_PVAR`, `KYTY_GATE_SCHEDULE*`, `KYTY_BVH_*`, `KYTY_SHADER_CACHE`; `KYTY_GPU_CLOCK_PIN=1`;')
A('видео `rec_<тег>.mp4` у V/T и нет у W; `--vulkan-validation` true у W, false у V/T; И10 (п. 306(г) В1) — precache по умолчанию по строкам лога.')
A('У W ещё: `VK_LAYER_PATH`; **п. 295(б)(4)** строка `W form: limit=100000000 filter=none` из окружения json и нет ключа `VK_LAYER_MESSAGE_ID_FILTER`;')
A('слой активен (п. 224); на **удержанном** W (нет маркера смерти, нет `hold_exit`, исход `ok`): **(1)** строк лимита слоя 0 (лог и stdout); **(2)** ≥ 1')
A('строки `[Vulkan][W][2]`/`[Vulkan][E][2]` (лог и stdout); **(3)** последняя такая строка лога — не раньше **10 с** показанного времени (Σ`dt_us` строк')
A('`FrameTrace` удержания после её байта) до последней строки `FrameTrace`; на неудержанном W (1)–(3) — `n/a` (п. 295(б): «читаются на удержанном W»).')
A('')
A('**Контроли стенда (F5c `f5c_read.py`, те же имена; провал — `NOT EVALUABLE`, стоп серии):** одна строка `TestMinimize: config on delay_s=60.000')
A('dur_s=10.000`; одна `armed`; строка входа перед `armed` несёт имя уровня (N2 п. 285(в)); одна `minimize` после `armed`; у `fs2_w`/`fs2_v` одна')
A('`restore` после `minimize`; ≥ 1 `Window 1 minimized`; первый кадр сцены до `minimize`; у `fs2_w0` — `FixMinimize: on` 0 и нет строк `SwapchainZeroExtent`;')
A('у `fs2_v` — `FixMinimize: on` ровно 1 (положительный контроль умолчания плеча V); **событие окна вне стенда (п. 273(з))** — строка')
A('`Window <id> minimized` или `Recovering Vulkan swapchain` вне окна «`TestMinimize: minimize` … max(`restore`, `SwapchainZeroExtent: end`) + 2 с»')
A('по часам лога (Σ`dt`); без `restore` — до конца лога.')
A('')
A('**`fs2_w` — PASS, если все** (буква (а) п. 273(е)(3) в формулировке F5c + п. 298(г)(1) + п. 327(г)(1)): вошёл; нет смены сцены; нет `hold_exit`;')
A('ровно одна `Window 1 minimized`; строки `SwapchainZeroExtent: begin`/`end`; `[Vulkan][E]` 0 (лог и stdout); маркеров смерти 0; Σ`dt` после первого')
A('кадра сцены ≥ 310 с; после `restore` ≥ 1 000 строк `FrameTrace`; `end` не позже `restore` + 2 с (п. 278(в), часы лога); **`DualSrcBlend:')
A('supported=1 enabled=1`** — ≥ 1 строка, все строки `1/1`, первая до первой `GuestOut` (п. 300(б)(4)); **`FixMinimize: on`** ровно 1; Б9а: `ASSERT:` 0 в')
A('логе и stdout, `user_msg_param` 0 (лог), строк `Unresolved import stub called` с `[AudioPropagation_v1]` 0 (лог); иначе FAIL.')
A('')
A('**`fs2_w0` — STOP / NO STOP (п. 298(г)(2)):** строка `[Vulkan][E]` с `imageExtent (width = 0, height = 0)` после якоря и')
A('`VUID-VkSwapchainCreateInfoKHR-imageExtent-01689` в той же строке или в одной из 3 следующих. **Якорь** — первая строка `TestMinimize: minimize`;')
A('в логе **без строки стенда** — первая `Window 1 minimized` (**прочтение исполнителя [I]**, вопрос В1 ниже). На самом `fs2_w0` контроль стенда требует')
A('ровно одну `TestMinimize: minimize`, поэтому якорь там — буквы.')
A('')
A('**`fs2_v` — PASS, если все** (буква (в) п. 273(е)(3) в формулировке F5c + п. 327(г)(1)): вошёл; нет смены сцены; нет `hold_exit`; Σ`dt` ≥ 330 с;')
A('видео ≥ 3 000 кадров; лист есть; 0 глитчей `s51_vidglitch 4 6` вне окна «`minimize` … `end` + 2 с» (окно лога на часах `.idx` по привязке концов);')
A('непрерывность `.idx` после `end` — номера present строго растут (N1 п. 285(в)); K1/K2 вне окна 0; `begin`/`end` есть; `end` не позже `restore` + 2 с;')
A('Б9а — как у `fs2_w`; иначе FAIL.')
A('')
A('**`fs2_t` / `fs2_tr` (п. 327(г)(2): члены п. 287(в)(5) для `=1` дословно и п. 294(б)):** FAIL — любая строка `Unresolved import stub called [` (лог,')
A('любая библиотека); маркер смерти; кадр ≥ 1 с после первого кадра сцены; смена сцены; видео < 3 000 кадров или ≠ 0 глитчей; нет листа; `ASSERT:` в логе')
A('или stdout; `user_msg_param` (лог) > **0** (В2); частота `SourceCreate` на удержании ≥ 0,1 на кадр; контроль пробуждения (`SourceSetAttributes` ≥ 1 или')
A('`SourceRender` ≥ 1 на последней строке счётчика) не выполнен. `NOT EVALUABLE` — не вошёл / нет первого кадра сцены; Σ`dt` < 120 с; частота не')
A('читается по букве. Иначе: K3 удержания (кадры ≥ 100 мс, окно входа 600 кадров не считается) ≤ **1** — PASS; > 1 — `K3 OVER` → один повтор `fs2_tr`,')
A('**решает повтор** (PASS повтора — PASS; иначе FAIL); повтор не снимает прочих членов (п. 294(б)). Механика и формулы — `f6e_read.py` (импорт по')
A('sha `%s…`): `frequency`, `wake`, `k3_within`, `stub_profile`.' % R.F6E_SHA[:16])
A('')
A('**Члены исполнителя [I] (печатаются отдельной строкой, вердикта не задают, п. 258(д)):** одна строка `begin` и одна `end` (`fs2_w`); в stdout')
A('`user_msg_param` 0 и строк заглушки `[AudioPropagation_v1]` 0 (`fs2_w`, `fs2_v`, `fs2_t`); два прочтения «`end` позже `restore` + 2 с» (часы лога и')
A('`ms=`) совпадают; два окна видео (привязка концов и наибольший разрыв `.idx`) дают один счёт глитчей; у `fs2_w0` эмулятор кончился')
A('(`hold_exit` / `exited` / маркер смерти). Справка: последняя строка `AudioPropagation: calls`, строки окон по видам, `AsyncPipelines: skipped draw`.')
A('')
A('## 5. Прочтения исполнителя [I] и вопросы лиду (до ответа — по этой печати)')
A('')
A('- **В1 (якорь правила остановки на эталоне `log_w144_09.txt`).** Буква: «после `TestMinimize: minimize`»; в `log_w144_09.txt` строки стенда нет')
A('  (окно свернули извне, пересчёт лида `f5c_chk.out.txt`: `minimize -1`), а п. 298(г)(2) требует STOP на нём. Прочтение: в логе без строки стенда')
A('  якорь — первая `Window 1 minimized`. На `fs2_w0` не действует (контроль стенда). Фикстуры: оба эталона — STOP (§7).')
A('- **В2 (`user_msg_param` у `fs2_t`).** П. 294(б): «не больше, чем у контроля `=0` того же уровня этой серии»; в FS2c контроля нет (п. 327(г)(2)).')
A('  Предел — 0: у `f6e_c1` (серия 2 F6e) 0 строк [c, фикстура], база свидетелей 0 (п. 294(а)); оба прочтения дают 0.')
A('- **В3 (`FixB9a: on` ≠ 1).** «Ошибка формы тега» — `INVALID`, стоп серии и вопрос лиду; повтора формы нет (п. 327(г) его не называет, при пустом')
A('  окружении повтор дал бы тот же бинарь); в сводке Б9а (1) — `NOT EVALUABLE`, не FAIL.')
A('- **В4 (`FixMinimize: on` у `fs2_v`).** Положительный контроль умолчания плеча V — контроль (`NOT EVALUABLE`), как у F5c; у `fs2_w` — член (FAIL).')
A('- Прочее [I]: `_PipelineCache` возвращается (как FSc); свободно ≥ 60 ГБ до замка; прогрев `fs2_tw` — стоп при rc ≠ 0 или строке смерти/окна (как')
A('  `f6e_w1`); `fs2_w0`: rc ≠ 0 — данные (остановка ожидается).')
A('')
A('## 6. Вердикт серии и правила остановки')
A('')
A('`FS2 SERIES VERDICT` = **PASS**, если `fs2_w` PASS, `fs2_w0` STOP, `fs2_v` PASS и `timestop_casino` (`fs2_t`/`fs2_tr`) PASS; **FAIL**, если хоть один')
A('из них FAIL / NO STOP или член Б9а провален; иначе `NOT EVALUABLE`. Строка п. 327(г)(3): Б9а (1) (`fs2_w`, `fs2_v`) и (2) (`timestop_casino`) —')
A('провал любого → «**FS2d не устанавливает FS2**». Вердикт, лист `sheet_fs2_v.png` и сравнение `sheet_fs2_t.png` — лиду (FS2d `HPP-384`).')
A('**Стоп серии** (`fs2_read.py --stop-check`, позже идущие теги не запускаются, вопрос лиду): нет чтения; `NOT ADMITTED`; `NOT EVALUABLE`; `INVALID`;')
A('`WINDOW EVENT`; маркер смерти без `[Vulkan][E]` (`fs2_w`, `fs2_v`, `fs2_t`); `enter_scene` rc ≠ 0 вне `fs2_w0` и вне остановки валидацией; прогрев —')
A('rc ≠ 0 / строки смерти или окна; BUSY перед тегом после ожидания и одного повтора. FAIL члена и NO STOP — данные, серия идёт.')
A('Прогноз окна замка [I]: ≈ 30–35 мин (W ≈ 7, W0 ≈ 2, V ≈ 7, прогрев ≈ 3, T ≈ 4, копии и возврат кэшей).')
A('')
A('## 7. Фикстуры (последний вывод каждого набора)')
A('')
for o in OUTS:
    with open(path(o), 'rb') as f:
        t = f.read().decode('ascii').strip().split('\n')
    A('- `%s` sha256 `%s` — первая строка: `%s`; итог: `%s` / `%s`' % (o, sha(path(o)), t[0][:200], t[-2][:120] if len(t) > 1 else '', t[-1][:120]))
A('')
A('Эталоны п. 298(г)(2) / п. 296(д) — `runs/stoprule_ref.out.txt` (`fs2_read.py --stop-rule`): обе строки — `STOP` (иначе печать не принимается).')
A('')
A('## 8. Строки печати')
A('')
for n in R.SEALED:
    A('seal: %s %s' % (sha(path(n)), n))
A('')
A('go_fs2 call: PLWAIT=540 bash C:/kyty/f287/fs2c/go_fs2.sh series')
A('')
A('## 9. Не заявляется')
A('')
A('Что без правки свёрнутое окно никогда не ведёт к крэшу; корректность любой сцены и проходимость до конца; что звук верен; что FS2 годен к установке до')
A('приёмки FS2d; ни одно число — не выигрыш; 60 FPS не обещаются.')
open(os.path.join(HERE, 'pred', '01_fs2.md'), 'wb').write(('\n'.join(L) + '\n').encode('utf-8'))
print('pred/01_fs2.md sha256 %s lines %d' % (sha(os.path.join(HERE, 'pred', '01_fs2.md')), len(L)))
