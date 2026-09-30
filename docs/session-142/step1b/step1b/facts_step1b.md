
## Step 1b — правки RC1–RC10 в `sc142.py` / `go142a.sh`, фикстуры, калибровка, мутанты, печать `pred/02_sc142.md` (Harness Engineer, `HPP-282`)

Исполнение `ROADMAP.md` «СЕССИЯ 122» п. 224 (коммит KytyPS5 `6a50c978`, прочитан целиком вместе с п. 223 и отзывом
`docs/session-142/review142.md` `8320bc1f`). Начало чтения входа 21:40:39Z (после коммита `6a50c978`). Игры, кода эмулятора, сборок и
замка не было. Время — только `C:/kyty/s142/step1b/times.txt` (UTC по `date -u`).

**Выход (все sha256 — полные в `step1b/times.txt` и §6 печати):**

| что | путь | sha256 | итог |
|---|---|---|---|
| скорер | `C:/kyty/s142/sc142.py` | `1ce612cdd036e2382ce5c5aae6bd25836062830dc0952da8512a9f2a74bb38c3` | правки RC1–RC10 + `--check1b` |
| цепочка | `C:/kyty/s142/go142a.sh` | `d9af55aeb8a33593…` | печать `02`, счёт файлов кэша до замка и после прогона |
| фикстуры скорера | `test_sc142.py` → `step1b/test_sc142.out.txt` | `3a1f19bbacaa865bec3fd5ee715d6a2fdd12aa2b1157022411951c9a142157d8` | **checks: 217, `ALL OK`** (первая строка `suite test_sc142.py sha256 facafac7… target sc142.py sha256 1ce612cd…`) |
| фикстуры цепочки | `test_go142a.py` → `step1b/test_go142a.out.txt` | `8a2b4b88625cba684c8c24edf1285e335dd49d6081a5b518b12814add55041c3` | **checks: 25, `ALL OK`** |
| калибровка заново | `sc142.py --calib` → `step1b/calib142_1b.out.txt` | `461a080c0a62ff7b59c56e9d08e2918b73bb3248ddd4010bb13f45a24218ae9c` | **`CALIB 5 of 5`**, байт в байт = шаг 0 |
| строки проверки п. 224(б)(2) | `sc142.py --check1b` → `step1b/check1b.out.txt` | `1bb561a15a383151f4cdbb75cdf90b3c3164513e659536aa96834c1a7df8e9c3` | **`CHECK1B 3 of 3`**: `s1s128` K2, `s2s128` K2, `s6s137` validation active (0 / 1 / 440 084) |
| мутанты — зачётный полный | `mut_sc142_1b.txt`, лог `mut_run1b.log` | `52705812…` / `0fb4e2fa…` | 245 мутантов: 242 убиты, 3 выжили (`half`, `sk_v_att_ok`, `ma_nojs`), контроли 3/3, `fast on`, стена 410,2 с (прогноз 548 с) |
| «только добавление» | `step1b/addonly142_1b.out.txt` | `9470f8580ba91b299c75305ba1b08e1e43a22e7e746b4218e14c38449ebc58fe` | `ADDONLY: PASS` (y1–y3, 22 строки перед финальной строкой набора; копия набора полного прогона `step1b/v1/test_sc142.py` `b1452fcf…`) |
| добор `--only` | `mut_sc142_1b.add.txt`, лог `mut_run1b.add.log` | `6704f257…` / `3fa8b1f6…` | 3 из 3 убиты, контроли 3/3, стена 56,6 с |
| печать | `C:/kyty/s142/pred/02_sc142.md` | `a42bce68d4c8376712b76eae76e6ce01563f54b5d6e83ff80617694fe54501e9` | 13 строк `seal:`; `--check-seal` → **`SEAL: PASS`** (`step1b/checkseal02.out.txt` `8395a748…`) |
| печать 01 | `pred/01_sc142.md` | до пометки `03ea3294…` (копия `step1b/v0/01_sc142.md`), после `e8f10c91…` | пометка «заменена `02` по п. 224» |

**Стена мутантов с. 142:** шаг 0 117,5 + 25,3 = 142,8 с; звено 1б 410,2 + 56,6 = 466,8 с; **всего 609,6 с ≈ 10,2 мин** из 30 мин.
Мутантов 245 = 157 шага 0 (7 якорей перенесены на новый текст; `oc_k1_marks`, `oc_k2_marks` сняты — порядок «K1 раньше K2» ушёл) + 88
новых. Эквивалентные (доказательства в шапке `mut_sc142.py`): `hold_exit is None` у V и W (при `hold_exit` уже истинно `ended`);
`run[-STOP_RUN:]`.

**RC → фикстура / проверка** (все — `test_sc142.py`, вывод `step1b/test_sc142.out.txt`; мутанты — `mut_sc142_1b.txt`):

| RC | правка скорера / цепочки | фикстуры | проверка на реальном логе / мутанты |
|---|---|---|---|
| RC1 класс исхода по первому маркеру | `markers()` — лог по позиции, затем stdout, затем маркеры попытки; `outcome()` — класс первого; ключ остановки — первый по позиции | n1 (`ErrorDeviceLost`→`Fatal`+`hold_exit` → K2), n2 (`GpuHangAbort`→`Error`+`exited` → K2), n3/n3b (крах раньше → K1), n4/n4b (лог раньше stdout), n4c/n4d (порядок в stdout), n5 (ENDED после лога), n6/n6b (ключ), n7 (печать порядка), n8 (vx), b1–b3 | `--check1b`: `s1s128`, `s2s128` → K2; мутанты `mk_sort`, `mk_order`, `oc_marks_first`, `oc_marks_any`, `oc_change_first` |
| RC2 W «validation active» | `validation()` — 0 `no validation layer:` И ≥ 1 `…VK_EXT_validation_features` И ≥ 1 `[Vulkan][` (лог + stdout, без лога — FAIL); строка допуска W | v0, v1a–v1h | `--check1b`: `s6s137` PASS по трём членам; мутанты `va_*`, `scan_noval/valfeat/vkany`, `m_noval/valfeat/vkany`, `bd_val_*` |
| RC3 длина видео и покрытие | строки V «video ≥ 3000 frames», «video frames ≥ FrameTrace rows in all − 100»; печать кадров видео, записей `.idx`, строк `FrameTrace` всего и после первого кадра (и у переписи; провал покрытия — «glitches not conclusive») | r1, r1b, r2–r2c, r3, r4, r5, r5b, k11b | мутанты `sk_v_video*`, `sk_v_cover`, `bd_cover*`, `cover_up/down`, `idx_*`, `bd_rows_total` |
| RC4 удержания не было | `HOLDS_120` только при `ok` + `hold_s` ≥ 120 + сумма `dt_us` ≥ 120 с, иначе `NOT_EVALUABLE` с причиной; строка V «attempt ok, hold_s ≥ 330, no hold_exit / ENDED»; `o7b` заменена на h1 | h1, h2, h2b, h2c, h3, h4, h5, k6, o7c, y2 | мутанты `oc_stable`, `oc_hold_s*`, `oc_reason_stable`, `hold_census_s_*`, `hold_v_*`, `sk_v_att_*` |
| RC5 лист | строка «sheet file present, non-empty; sha листа и `rec_v142.mp4` = последние строки `step2/times.txt`»; `viewed` без неё — `NO` | s1–s9 | мутанты `sh_*`, `sk_file`, `sk_yes_file` |
| RC6 W `ft_tail` > 0 | строка W «ft_tail > 0» | w1, w2, w3 | мутанты `sk_w_tail`, `sk_w_tail_none` |
| RC7 смена сцены | `derive()` — первая следующая строка `Level has started` режет классификацию; печать имени и n; исход `NOT_EVALUABLE` «scene change», если раньше неё нет маркера лога и кадра K2; строки V/W «no scene change» | q1–q10, q5c | мутанты `der_change_first`, `der_later_gt`, `der_after_cut`, `der_beyond*`, `der_prev`, `oc_change_*`, `sk_v_change`, `sk_w_change` |
| RC8 попытка без json, stdout | «ATTEMPT MADE, NO JSON (instrument)» в `--tag`, сводке, карте (А), «не допущен», серию остановки прерывает; печать stdout эмулятора; строки V/W «emulator stdout present» | j1–j6, y3 | мутанты `am_file`, `su_nojs*`, `st_main_nojs`, `ma_nojs`, `bd_stdout`, `sk_v_stdout`, `sk_w_stdout` |
| RC9 разрывы n | строка V «n gaps after the first scene frame = 0»; печать рваных строк `FrameTrace` | g1, g2, g3 | мутанты `sk_v_gaps`, `scan_torn`, `scan_nft`, `bd_torn`, `m_ft` |
| RC10 кэш, переменные, k первых/последних пяти | печать: «первый вход уровня; общие кэши тёплые…»; §1 — все переменные `enter_scene.py` (`:569–576`); цепочка — `step2/times.txt` «shader cache files before the lock / after the run»; сводка — k первых и последних пяти | f1, f2, f3, y1; `test_go142a` g24, g25 | мутанты `half`, `su_first5`, `der_median`, `der_max` |

**Вопросы и варианты исполнителя (печать §4):** (1) незаполненная строка листа при отсутствующем файле — `PENDING_SHEET` по букве, строка
файла FAIL печатается; (2) попытка без json прерывает серию правила остановки (не «не вошёл»); (3) `hold_s` нет при `ok` —
`NOT_EVALUABLE`; (4) разрывы n у V — только после первого кадра сцены и до смены сцены.

**Таблица времени (из `step1b/times.txt`):** 21:40:39 начало; 21:45:06 копии шага 0 в `step1b/v0`; 21:55:44 прогноз и старт полного
прогона мутантов; 21:57:40 пометка `pred/01`; 22:02:40 конец полного прогона; 22:03:40–22:04:38 добор; 22:05:04–22:05:15 наборы,
калибровка, `--check1b`; 22:05:40 печать `02` и `--check-seal`.

**Не заявляется:** что скорер после правок верен на неизвестных уровнях; что какая-либо сцена корректна, проходима до конца или
`SCENE_OK`; что перепись найдёт или не найдёт дефект; что инвентарь полон; ни одно число прошлых сессий — не выигрыш и не потолок;
60 FPS не обещаются.
