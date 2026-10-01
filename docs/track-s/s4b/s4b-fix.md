
## S4b — правка `RX_SHADER` (метка с пробелом), перепись 13 `RX_*`, печать `pred/03_s.md`, пересчёт `c1_0` (Harness Engineer, `HPP-349`, п. 265)

**Итог.** Дефект [c] п. 265(а) исправлен: `RX_SHADER` читает метку с пробелом (`(\S+)` → `(.+?)`); перепись 13 выражений на
`log_c1_0.txt` и четырёх логах `sw_*` — других расхождений класса нет; регрессия `--regress` байт в байт; `sw_*` байт в байт, кроме строки 13
(имя строки допуска печати); мутанты 271 из 271; печать `C:/kyty/s288/pred/03_s.md` sha256
`f5814e16a436b8b2f96dfe1f713f4027be2590f54d7a7c7b2567d64ed81cbca7` (`--check-seal` PASS); пересчёт `c1_0` — плечо PASS, ворота холода
`cold`. Игры, замка и сборок нет.

- **Правка (п. 265(в)(1)):** `sc_s.py` строка `RX_SHADER` — группа метки `(.+?)` (форма `LOGF` — `4fc501f4:src/graphics/host_gpu/renderer/
  pipeline/pipelineCache.cpp:3916`, `"AvTrace: shader %s hash=0x%016" …`, метка `ShaderRecompiler VS`). Скрипт правки — `s4b/patch_s4b.py`
  (якоря по одному вхождению, LF).
- **Фикстуры (п. 265(в)(2)), `test_sc_s.py` раздел 12:** S4b-1 — строка 232419 `log_c1_0.txt` байт в байт (literal из лога, sha лога
  сверен скриптом правки); S4b-2 — метка из одного слова; S4b-3 — порядок веток на реальных строках 232401 (`shader-emit`), 232417
  (`shader-cache save`), 232418 (`shader-spec`) + `shader-cache load`: в `s['sh']` — только строка `AvTrace: shader `; S4b-4 — T-плечо
  с реальными строками: T-3 1/1, ворота `cold`; S4b-5…7 — допуск плеч печати 02 (вариант V13); S4b-6 — `--json-out` (V14); A9 — имена
  печатей. Вывод `s4b/test_sc_s.out.txt` sha256 `6a42ed26d3d4c7db4f31c8bc91f3a90200f7803ea5c84af1798e54f120d3a4ba` — **319 проверок, `ALL OK`**. Прочие наборы:
  `test_go_s` 34 `ALL OK`, `test_cachex_s` 36 `ALL OK`, унаследованный `test_sc142` 217 `ALL OK` (`s4b/*.out.txt`, sha — в печати 03 §6).
- **Перепись 13 `RX_*` (п. 265(в)(3)), `s4b/census_rx.py`, вывод печати 02 `s4b/census_p02.out.txt`, печати 03 `s4b/census_s03.out.txt`;
  на `log_c1_0.txt` (строк формы / совпадений печати 03; форма — префикс, по которому скорер выбирает строку):**

  | выражение | ссылка `LOGF` | строк формы | совпало (02 → 03) |
  |---|---|---:|---:|
  | `RX_SKIP` | `4fc501f4:src/graphics/host_gpu/renderer/renderDraw.cpp:4439` | 4 | 4 → 4 |
  | `RX_HASH` (ShaderRegister) | `4fc501f4:…/pipeline/pipelineCache.cpp:6028` | 1 636 | 1 636 → 1 636 |
  | `RX_HASH` (ShaderFirstUse) | `4fc501f4:…/pipeline/pipelineCache.cpp:3516` | 248 | 248 → 248 |
  | `RX_DSAVE` | `4fc501f4:…/pipeline/pipelineCache.cpp:4806` (`PipelineCacheLog`) | 2 | 2 → 2 |
  | `RX_RSAVE` | `4fc501f4:…/pipeline/pipelineCache.cpp:5963` | 2 | 2 → 2 |
  | `RX_QUEUED` | `4fc501f4:…/pipeline/pipelineCache.cpp:6425` | 1 | 1 → 1 |
  | `RX_CREATED` | `4fc501f4:…/pipeline/pipelineCache.cpp:6431` | 1 | 1 → 1 |
  | `RX_READY` | `4fc501f4:…/pipeline/pipelineCache.cpp:6050` (`PipelineCacheLog`) | 1 | 1 → 1 |
  | `RX_WAITED` | `4fc501f4:src/graphics/presentation/window/window.cpp:1025` | 1 | 1 → 1 |
  | `RX_LOADED` | `4fc501f4:…/pipeline/pipelineCache.cpp:4647` (`PipelineCacheLog`) | 1 | 1 → 1 |
  | **`RX_SHADER`** | `4fc501f4:…/pipeline/pipelineCache.cpp:3916` | **17** | **0 → 17** |
  | `RX_VSPS` | `4fc501f4:…/pipeline/pipelineCache.cpp:5356`, `:5394`, `:6312` (gfx; строки cs без `vs=`) | 1 697 | 1 697 → 1 697 |
  | `RX_PCWOV` | нет в `4fc501f4`; `2ce6326e:…/pipeline/pipelineCache.cpp:6252` (S5c) | 0 | 0 → 0 — **форма на реальном логе не проверена** (долг печати 04) |
  | `RX_QUEUED_ANY` | `4fc501f4:…/pipeline/pipelineCache.cpp:6425` (`match`) | 1 | 1 → 1 |

  Строк формы не в начале строки (перемешанная запись потоков) — 0 у всех. Строки `shader-cache` / `shader-spec` / `shader-emit` — по 17,
  `RX_SHADER` к ним не применяется (ветка `AvTrace: shader ` с пробелом) и их не берёт. Логи `sw_m1`, `sw_m2`, `sw_m3`, `sw_t1`: у всех
  выражений строк формы = совпадений; строк `AvTrace: shader ` — 0. Другого расхождения того же класса нет; иных правок разбора нет.
- **Регрессия (п. 265(в)(4)):** `--regress` печати 03 — `REGRESSION: ALL OK`, вывод байт в байт = `s3b/regress_s.out.txt` печати 02
  (`8ab6f0c43b0a523fd9d6b87d7db8f873bc402fc12797d9f03c672e96dea8d817`), расхождений 0. Скорер печати 03 на `sw_*`
  (`s4b/reg/score_sw_*.s03.txt`, json — `s4b/reg/*.s03.json`; `s4b/reg_sw_s4b.py` → `s4b/reg_sw.out.txt` `SW REGRESSION: ALL OK`): у каждого
  из четырёх ровно одна строка отличается — строка 13 `PASS admit prereg = the seal now (829ac684)` → `PASS admit prereg = the seal of its
  run 02_s.md (item 265 (g)) (829ac684)` (строка печати, вариант V13); в json — только эта строка `admit`. Файлы печати 02
  (`s4/score_sw_*.txt`, `s4/runs_s/*.score.json`) не переписаны.
- **Мутанты (п. 265(в)(5)):** `mutlib` v4.1, зачётный полный `--control --no-memo --workers 12 --work-dir/--cache-dir C:/kyty/s288/s4b/...`:
  **271 из 271 убиты**, контроли 3 из 3, стена **365,0 с** при прогнозе ≈ 355 с (верх 718 с) (`s4b/mut_sc_s.txt` sha256
  `689f7a7a9f633396a2b1a1bc8c2c1d5d565e0ee3930ff1785bafeb0f3e2e6bae`). Новые: `rx_shader_label` (`(.+?)` → `(\S+)`, убит S4b-1),
  `rx_shader_label2` (`(\S+ \S+)`, убит S4b-2), `prev_name`, `prev_route`, `prev_pin`, `prev_main`, `prev_tags`, `prev_sha`, `pred_03`,
  `pred_s6_04`, `json_out`; `ad_pred` перенесён на новый якорь. **Сумма стены всех прогонов мутантов звена — 365,0 с** (один прогон).
- **Печать (п. 265(в)(6)):** `C:/kyty/s288/pred/03_s.md` sha256 `f5814e16a436b8b2f96dfe1f713f4027be2590f54d7a7c7b2567d64ed81cbca7` (`s4b/mkseal_s03.py`):
  §0 — правки п. 265 и таблица переписи; §1 — константы печати 02 дословно; §2 — 26 строк вызова S4 после `c1_0` (`c2_0` … `g_3_2`) и их
  планы DRY=2; §3 — планы S6 без вызова (печать 04); §4 — вызов пересчёта `c1_0`; §5 — 20 строк `seal:`; §6 — доказательства; §7 —
  варианты V1–V15; §8 — не заявляется. `sc_s.py --check-seal` — `SEAL: PASS`, `BAD` 0 (`s4b/checkseal_03.out.txt`). `go_s.sh` — только
  пути печатей (`s4` → `pred/03_s.md`, `s6` → `pred/04_s.md`, две строки комментария); `test_go_s.py` — те же имена.
- **Пересчёт `c1_0` (п. 265(в)(7)):** sha лога `49d0a5222ef568553808c8c34989b1a743e860a2bc39fd2c33ee7a8b9032d902` сверен до чтения
  (06:44:20Z); `python sc_s.py --tag c1_0 --json-out C:/kyty/s288/s4/c1_0.s03.json > s4/score_c1_0.s03.txt` rc 0 —
  `s4/score_c1_0.s03.txt` `2e2dd70e3bff5b507a6039584ad662bbf3ab022aa60ed10ecf2121c5bec82252`, `s4/c1_0.s03.json`
  `a29379329931e7155c7318bcaefe4f4775b54511899d543ed5b793a23fc2e735`. Файлы печати 02 (`s4/score_c1_0.txt` `09e7c064…`,
  `s4/runs_s/c1_0.score.json`) сверены `sha256sum -c` после пересчёта — не изменены. **Плечо `c1_0` по печати 03: PASS**; T-3 17/17;
  атрибуция DETERMINED; ворота холода **`cold`** (perm_after 17, рецептов после входа +37, пропусков 4); кадр n 233 dt 113 262 мкс —
  в окне, held, класс SHADER, «partly» (PREP 62 950 мкс: TR 62 637, PL 313); атрибутировано ≥ 100 мс 1 (PCW 0), ≥ 1 с 0; создание
  пайплайнов в игре — медиана 233 мкс при 37 созданиях → `WARM` по п. 241(в)(8) (буква и вариант исполнителя); видео 4 184 кадра,
  0 глитчей. Отличия от вывода печати 02 (`s4b/c1_0_s02_vs_s03.diff.txt`): строка 1 (вердикт FAIL → PASS), 13 (имя строки печати),
  36 (T-3 0/17 → 17/17), 43 (атрибуция), 52–55 (класс и атрибуция кадра 233, атрибутированные, не атрибутированные, ворота), 60
  (S-early) — все, кроме 13, зависят от `s['sh']`. `sc_s.py --allowed c2_0` — `yes (ok)`.

**Варианты исполнителя (вопросы лиду):** **V13** — плечи, сделанные под печатью 02 (`SEAL02_TAGS` = `sw_m1 sw_m2 sw_m3 sw_t1 c1_0`),
допускаются по печати 02 (путь `pred/02_s.md`, sha `829ac684…` закреплён в `SHA_02`; файл с другим sha не допускает ни одно) строкой
«prereg = the seal of its run 02_s.md (item 265 (g))»; без этого пересчёт `c1_0` и любое следующее чтение C1 под печатью 03 падали бы на
строке допуска `prereg` (json плеча несёт печать 02) — это правка механики печати, не разбора; по букве п. 265(в)(3) «иная правка» —
вынесена вопросом, а не стопом, потому что без неё п. 265(в)(6)–(7) неисполнимы. **V14** — `--json-out <путь>` у `--tag` (по умолчанию —
прежний `runs_s/<tag>.score.json`), чтобы п. 265(в)(7) не переписал файлы печати 02. **V15** — выбор `(.+?)` (п. 265(в)(1)).

**sha256 (`C:/kyty/s288/`):** `sc_s.py` `cee4cf1a723457da52b087a6179cf47a8ffe0000ca42e23253ccf7418dc56eb1`; `test_sc_s.py`
`16327a236e3532519f9df2a425394fb2e2871a7be065b32c6b5132aff23ae4a9`; `mut_sc_s.py` `08d597de1b64a9ed5ff5a7ef9968cde313af6ce25a12d1a8fffc3df09c0534d6`;
`go_s.sh` `4a323fb94ce3bbedd313985dd06bfa67f625bceacd5f88fd1f965f2f4c15ee28`; `test_go_s.py`
`059d41d25271bcf26ef88b5f46602976597a9c3331fb953a323910e4577ce070`; без изменений — `cachex_s.py`, `test_cachex_s.py`, `enter_scene.py` и
остальные строки `seal:` (печать 03 §5). Прежние тексты — `s4b/orig/`.

**Время (UTC, `C:/kyty/s288/s4b/times.txt`):** старт 06:28:39Z (замка и `STOP` нет, комментариев звена 0); правка 06:34:20Z; мутанты
06:36:27–06:43:25Z; печать 06:44:11Z; пересчёт `c1_0` 06:44:20–06:44:22Z. Замок `C:/kyty/SEALED_RUN.lock` и `C:/kyty/s288/STOP` не
появлялись (проверка первой строкой каждой команды записи).

**Не заявляется (п. 265(и)):** что `c1_0` холоден или тёпл вне слов скорера печати 03 (ворота трансляции `cold` при `WARM` создании —
данные к чтению S4, п. 265(ж)); что других дефектов чтения в `sc_s.py` нет (перепись — по одному T-логу и четырём логам `sw_*`); что
харнесс исполнит остальной путь S4 без ошибки; что фризы входа вызваны шейдерами; ни одно число — не выигрыш; 60 FPS не обещаются.
