# M3a (трек M, `HPP-842`): серия M3 на MS1 — отчёт

Звено Harness Engineer. Основание — `ROADMAP.md` п. 756(г)(3)–(7), 760(б), 761(д)–(е), 763(в), 764. Печать `pred.md` sha256
`f731a3ff8639b5720a969f29e0c84e90b18b54f3a2b39b7fcc5f595f7afdf1f5`, закрыта 2026-10-12 12:23:16 UTC до первого тега. После печати харнесс,
ридер и инструменты гейтов не менялись. Добавлены только `pairs_m3a.py` (сборка пар листов по допущенным тегам с учётом повтора `_r1`;
читает лишь `read.json` и листы) и `report_m3a.py` (таблица отчёта) — ни один член и ни одно слово они не решают. Вердикта по темам нет:
чтение G1–G7 и решение по каждой теме — M3b (лид). Пометки: [c] — проверено, [I] — вывод, [U] — неизвестно. Время — UTC, строки
`times.txt`.

## 0. Итог (строки для M3b)

| Гейт | Строка | Источник |
|---|---|---|
| Серия | 25 тегов печати допущены, у всех члены ALL YES и группа «форма FS15» ALL YES; плеч темы нет — ни одного машинного провала [c] | §1, `table.txt` |
| G3 холодный вход | `m3_i` (MS1, первый вход, каталог `…_mw1_33` создан): 0 кадров ≥ 1 с, видео 10 239 кадров, 0 глитчей, лист сделан; вход за 65,5 с (тёплый V — 18,9 с) | `runs/m3_i/read.txt` |
| G4 сцены | 6 уровней × (W, V MS1, V FS15): у W 0 `[Vulkan][E]` при живом положительном контроле (`[Vulkan][W]` 516 546–1 932 947), `DualSrcBlend` до `GuestOut`; у V 0 смертей, 0 кадров ≥ 1 с, видео 9 810–20 256 кадров, 0 глитчей; пары листов — `pairs/pair_<L>.png`, **читает лид** | §1, §3 |
| G5 скорость | Δ (конец A, буква) = **+0,68 %** ≤ +1,0 % ⇒ слово `NOT_WORSE`; конец B +0,68 %; 2SE по SE плеч 0,34 %; разброс внутри плеч A 1,68 %, B 0,85 % | `g5.out.txt` |
| G6 патч | `m3_g6`: G1′ скорость по часам игры **1,0037** (SPEED_OK, T6 0,9993), ХРАПОВИК **NONE** (кадров ≥ 3 вблэнков 1,17 % против 6,83 % у X), R2 OK ⇒ `G6 PASS` | `g6.out.txt` |
| G7 журналы | `grep_sig_m1a2.py`: фатальных совпадений 0 (MS1 и FS15); свидетели `witness.tsv`: потерь 0 на 6 уровнях; свип F48a: 21 строка-кандидат — все прочитаны в §5 [I: ни одна не сигнатура K1–K4] | §5 |
| T231 баннер | `pairs/banner_t231.png`: сверху `m3_sg_v_r1` (T231=1) — крупная надпись «SKY GARDEN», снизу `m3_sg_t2310` (T231=0) — надпись мельче; полосы сдвинуты по времени примерно на 1 с [I: отличие видно; читает лид] | §3 |
| Возврат | после каждого тега установлен FS15 `bfac84be` (sha256 сверен 25 + 3 раза), живые кэши = K0 (`manifest cmp EQUAL` до и после каждого тега; после последнего тега `KSET EQUAL4` 4 774 файлов против `k0.tsv`) | `times.txt` |

## 1. Помехи и повторы

- `m3_sg_v` (13:56–14:03) — `NOT_ADMITTED`: событие окна (`Window 1 minimized`, `Recovering Vulkan swapchain`, 3 × `lost keyboard focus`) —
  пользователь работал за машиной. По п. 764 это помеха; повтор `m3_sg_v_r1` (18:41–18:48) допущен. K1 после помехи оставлен (п. 764),
  `k1.tsv` sha256 `46765422…` записан строкой `times.txt`.
- Не попытки (эмулятор не запускался, кэши не тронуты): `m3_sg_v.nostart_130520` и `m3_mg_w.nostart_200354` — отказ `idle142`
  (ГП занят на 20 % и 24 %); `m3_sg_v.busy_130733`, `m3_sg_v.busy_131650`, `m3_sg_v_r1.busy_142139` — `procload` (программа пользователя
  `<app>` ≈ 3,9–5 с CPU в секунду).
- Ожидание программ пользователя: 13:00–13:48, 14:04–18:30 и 20:02–20:57 UTC. Пока они шли, тегов не было. Как путь пробуждения стоял
  монитор задачи (`external_service host-idle`, +60 мин).
- Замок брался 28 раз, отпускался 28 раз (`runs/lock.log`: первый — 2026-10-12 12:24:11, последний — 2026-10-13 01:32:55).

## 2. Кэши (RC-M1, п. 761(д))

- K0 снят `m3_i`: `k0/k0.tsv` sha256 `016dc55ca35f041a…` — 4 868 файлов, 1 318 828 127 байт = живые кэши до серии [c].
- Перед каждым тегом после `m3_i` живые кэши четырёх папок эмулятора = K0 (`KSET EQUAL4`) — 24 из 24 допущенных тегов [c `k0_cmp.txt`].
- Плечи FS15 (`m3_<L>_f`, `m3_g5_a1`, `m3_g5_a2`) шли на K0; плечи MS1 — на K1 (`manifest cmp EQUAL` копии K1 с `k1.tsv` перед каждым
  тегом). Итоговый K1 — `k1/k1.tsv` sha256 `5d5692982938baa9…`. Каталоги `k0/`, `k1/`, `k1.prev/` хранятся до приёмки M3b.
- **Текст отката M4 (п. 761(д)(3), дословно):** «ручки `KYTY_M_*=0` на бинаре MS1 — холодный каталог, общий с FS15; возврат к копии FS15
  `bfac84be` после этого тоже холоден до прогрева». Плечо «все `KYTY_M_*=0`» в серии не назначалось — каталог FS15 не тронут [c].
- **Н1 (п. 761(е)):** серия `KYTY_SHADER_CACHE=0` не ставила; строка `MWave1: mask=0x33` есть во всех 16 допущенных тегах MS1 при умолчаниях, у
  плеча `m3_sg_t2310` маска тоже `0x33` (T231 — тема HLE, маску транслятора не меняет).

## 3. Пары листов и баннер (для M3b)

`pairs.out.txt` sha256 `ebc5c21efb19d6a1…`. Пары — слева лист V MS1, справа лист V FS15 того же уровня: `pair_sg.png` (`m3_sg_v_r1` /
`m3_sg_f`), `pair_hb.png`, `pair_mg.png`, `pair_ac.png`, `pair_f1.png`, `pair_f2.png`. Харнесс отличий не выносит, их читает лид.
Строки HLE по логам: `MT272: mode=1` и `MT231: mode=1` во всех тегах MS1 при умолчаниях; `MT265:` нет ни в одном теге (путь AMPR не
вызывался [c лога]); `MTexOffset:` — 0 строк (T306 в MS1 не входит).

## 4. G5 — строки

| Плечо | Бинарь | mean `dt`, мкс | n | SE | FPS | скорость 16 667 / mean |
|---|---|---|---|---|---|---|
| `m3_g5_a1` | FS15 | 32 341,08 | 9 407 | 57,2 | 30,92 | 0,5154 |
| `m3_g5_b1` | MS1 | 32 696,65 | 9 303 | 53,6 | 30,58 | 0,5097 |
| `m3_g5_b2` | MS1 | 32 976,99 | 9 224 | 55,6 | 30,32 | 0,5054 |
| `m3_g5_a2` | FS15 | 32 888,87 | 9 241 | 57,0 | 30,41 | 0,5068 |

Δ = (Σ B − Σ A) / Σ A = (65 673,64 − 65 229,95) / 65 229,95 = **+0,680 %** (конец A); конец B — +0,677 %. Порог печати +1,0 % ⇒
`NOT_WORSE`. Внутри плеч дрейф: A1 → A2 +1,68 %, B1 → B2 +0,85 % — по порядку тегов, ABBA снимает линейный дрейф [I]. Дрейф A больше Δ:
одна ABBA не различает Δ в 0,7 % от шума серии [I]; 2SE по SE кадров (0,34 %) занижено автокорреляцией. Ступень вблэнка: при среднем
≈ 32,7 мс (≈ 2 вблэнка) Δ в 0,7 % кадр через ступень не переводит. 60 FPS не обещается.

## 5. G7 — строки

- Свип F48a (`g7_sweep.out.txt`, `g7_agg.out.txt` sha256 `1188d529…`): 26 логов (MS1 18, FS15 8), сегментов 92, отсутствующих 0;
  сигнатур MS1 152, FS15 42, база F0 820. Кандидатов (сигнатура лога MS1, которой нет ни в F0, ни в логах FS15 серии) — 21:
  - 2 — `CsPretranslate: skipped … TranslationBudget.h … budget exceeded` и `… ResourceTracking.cpp … shader resource tracking` с путём
    исходников worktree MS1 (`m2d\wt`). Те же две строки у FS15 с путём `fs15a\wt` идут строкой «FS15-ONLY» — сигнатура отличается
    только путём сборки [c]. Строка `CsPretranslate: skipped` — не фатал (п. 757(в)).
  - 18 — строки гостя `GuestOut:` (`File Open/Close …crash…`, `Play/Stop/Finished: …crash_landing…`, `Model Attribute … not found in
    "veg_grass_blade_hexa_a~cave…"`) — только в `m3_g6`, единственном теге серии с вводом (`keys:` формы F). Те же строки есть в логах P24
    той же формы: `log_iv_5` и `log_ia_A3` — по 137 строк [c]. Это вывод игры по сюжету ввода, не эмулятора [I].
  - 1 — `LogAsync: stall us=110996…156880` ×3 в `m3_ac_v`: запись приёмника лога ≥ 100 мс (строка писателя Ф27, `0e4b2f5a`,
    `log.cpp` `kStallNs`); прежде встречалась в стендах `fs10_f1`, `fs10_s1`, `b36_*`. Кадров ≥ 1 с у `m3_ac_v` 0 [c]. Задержка записи
    на диск [U причины].
- `grep_sig_m1a2.py`: MS1 36 файлов, FS15 16 файлов — фатальных совпадений 0, «themes with fatal hits: []» в обоих
  (`grep_ms1.out.txt` `7e2e310a…`, `grep_fs15.out.txt` `0eefb9ac…`).
- Свидетели (`g7_wit.out.txt` `3d60dc5b…`): на каждом из 6 уровней 27 ключей в логе FS15, 27 — в логе V MS1, потерь 0. У `sg` сравнивался
  лог `m3_sg_v` — тег-помеха, но лог MS1.

## 6. Правило п. 760 и сброс драйвера

ГП-наборы тестов в звене не запускались, сборок не было. `C:/kyty/m657/dl_cases.txt` (sha256 `75271d5f…`) — одна строка:
`FlatVirtualAddressRebasesGuestAllocation` (кейс 224 `shader_recompiler_compute_tests`) — `EXCLUDED_DL` с обеих сторон, в этом звене не
исполнялся. В логах и stdout игры строк `ErrorDeviceLost` и `device lost` — 0 во всех тегах (член смерти ридера) [c].

## 7. Файлы и sha256 (`C:/kyty/m657/m3a/`)

`pred.md` `f731a3ff…`, `test_m3a.out.txt` `ce9343ca…` (80 проверок, `ALL OK`), `g6_regress.out.txt` `315e3e85…` (`ALL OK`),
`g5.out.txt` `cda46307…`, `g6.out.txt` `1bfbbdda…`, `g7_sweep.out.txt` `0915442d…`, `g7_agg.out.txt` `1188d529…`, `g7_grep.out.txt`
`09e74c6d…`, `g7_wit.out.txt` `3d60dc5b…`, `pairs.out.txt` `ebc5c21e…`, `table.txt` `149d2b55…`; листы и пары — `runs/<тег>/sheet_<тег>.png`,
`pairs/*.png`; видео — `rec_<тег>.mp4`; логи — `log_<тег>.txt`, `stdout_<тег>.txt`. Игровые логи, видео и кэши в git не идут.

## 8. Не заявляется

Что любая тема даёт видимое отличие (баннер T231 — отличие на листе, чтение M3b); что MS1 корректен вне шести уровней; что Δ G5
отличим от дрейфа серии; что одна V G6 равна двум V п. 342; что строки-кандидаты G7 — не дефекты на других уровнях; ни одно число — не
выигрыш; 60 FPS не обещается.

---

## Приложение: таблица ридера (`report_m3a.py`)

### 1. Теги (последний допущенный из `<тег>`, `_r1`, `_r2`)

| тег | допущен | бинарь | уровень | форма | члены | форма FS15 | кадров ≥ 1 с | глитчей | видео | удержание, с | mean dt (+30 с, конец A), мкс | MWave1 | [Vulkan][E] / [W] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `m3_i` | да | ms1 | underwater_aerial_garden | v | ALL YES | ALL YES | 0 | 0 | 10239 | 334.1 | 33615.09 | 0x33 | 0 / 0 |
| `m3_sg_w` | да | ms1 | underwater_aerial_garden | w | ALL YES | ALL YES | 0 | None | None | 324.4 | 134833.13 | 0x33 | 0 / 871868 |
| `m3_sg_v_r1` | да | ms1 | underwater_aerial_garden | v | ALL YES | ALL YES | 0 | 0 | 10241 | 334.2 | 33479.5 | 0x33 | 0 / 0 |
| `m3_sg_f` | да | fs15 | underwater_aerial_garden | v | ALL YES | ALL YES | 0 | 0 | 9810 | 334.1 | 34481.87 | - | 0 / 0 |
| `m3_hb_w` | да | ms1 | hoover_beach | w | ALL YES | ALL YES | 0 | None | None | 313.6 | 45460.19 | 0x33 | 0 / 1932947 |
| `m3_hb_v` | да | ms1 | hoover_beach | v | ALL YES | ALL YES | 0 | 0 | 19808 | 332.1 | 16990.64 | 0x33 | 0 / 0 |
| `m3_hb_f` | да | fs15 | hoover_beach | v | ALL YES | ALL YES | 0 | 0 | 18937 | 331.9 | 17752.08 | - | 0 / 0 |
| `m3_mg_w` | да | ms1 | mini_giants_garden | w | ALL YES | ALL YES | 0 | None | None | 316.2 | 54262.11 | 0x33 | 0 / 917422 |
| `m3_mg_v` | да | ms1 | mini_giants_garden | v | ALL YES | ALL YES | 0 | 0 | 20256 | 331.9 | 16671.77 | 0x33 | 0 / 0 |
| `m3_mg_f` | да | fs15 | mini_giants_garden | v | ALL YES | ALL YES | 0 | 0 | 20204 | 332.1 | 16779.15 | - | 0 / 0 |
| `m3_ac_w` | да | ms1 | armadillo_challenge_1 | w | ALL YES | ALL YES | 0 | None | None | 314.8 | 37131.36 | 0x33 | 0 / 516546 |
| `m3_ac_v` | да | ms1 | armadillo_challenge_1 | v | ALL YES | ALL YES | 0 | 0 | 19983 | 332.1 | 16731.2 | 0x33 | 0 / 0 |
| `m3_ac_f` | да | fs15 | armadillo_challenge_1 | v | ALL YES | ALL YES | 0 | 0 | 20079 | 332.4 | 16668.94 | - | 0 / 0 |
| `m3_f1_w` | да | ms1 | fragile_battle_1 | w | ALL YES | ALL YES | 0 | None | None | 315.4 | 43851.94 | 0x33 | 0 / 1332171 |
| `m3_f1_v` | да | ms1 | fragile_battle_1 | v | ALL YES | ALL YES | 0 | 0 | 19959 | 332.1 | 16832.42 | 0x33 | 0 / 0 |
| `m3_f1_f` | да | fs15 | fragile_battle_1 | v | ALL YES | ALL YES | 0 | 0 | 19984 | 332.2 | 16799.61 | - | 0 / 0 |
| `m3_f2_w` | да | ms1 | fragile_battle_2 | w | ALL YES | ALL YES | 0 | None | None | 316.1 | 46991.05 | 0x33 | 0 / 999872 |
| `m3_f2_v` | да | ms1 | fragile_battle_2 | v | ALL YES | ALL YES | 0 | 0 | 19465 | 332.0 | 17282.26 | 0x33 | 0 / 0 |
| `m3_f2_f` | да | fs15 | fragile_battle_2 | v | ALL YES | ALL YES | 0 | 0 | 19782 | 332.3 | 17002.68 | - | 0 / 0 |
| `m3_sg_t2310` | да | ms1 | underwater_aerial_garden | v | ALL YES | ALL YES | 0 | 0 | 10361 | 334.2 | 32836.08 | 0x33 | 0 / 0 |
| `m3_g5_a1` | да | fs15 | underwater_aerial_garden | v | ALL YES | ALL YES | 0 | 0 | 10568 | 334.2 | 32341.08 | - | 0 / 0 |
| `m3_g5_b1` | да | ms1 | underwater_aerial_garden | v | ALL YES | ALL YES | 0 | 0 | 10337 | 334.2 | 32696.65 | 0x33 | 0 / 0 |
| `m3_g5_b2` | да | ms1 | underwater_aerial_garden | v | ALL YES | ALL YES | 0 | 0 | 10245 | 334.2 | 32976.99 | 0x33 | 0 / 0 |
| `m3_g5_a2` | да | fs15 | underwater_aerial_garden | v | ALL YES | ALL YES | 0 | 0 | 10266 | 333.9 | 32888.87 | - | 0 / 0 |
| `m3_g6` | да | ms1 | underwater_aerial_garden | v | ALL YES | ALL YES | 0 | 0 | 14013 | 334.0 | 23491.32 | 0x33 | 0 / 0 |

Не попытки и помехи (папки `runs/<тег>.<причина>_<время>`): `m3_mg_w.nostart_200354`, `m3_sg_v.busy_130733`, `m3_sg_v.busy_131650`, `m3_sg_v.nostart_130520`, `m3_sg_v_r1.busy_142139`.

### 2. Члены, которые не YES

- нет (у всех допущенных тегов члены и форма FS15 — ALL YES)

### G5 (`g5.out.txt`, sha256 `cda463075cc5b065e4dac49b60847ec9365cf485412184519c89449567d86599`)

```
G5 (item 756 (g)(5)): ABBA m3_g5_a1 m3_g5_b1 m3_g5_b2 m3_g5_a2; limit +1.0 %
MEASURE end A (the letter: to the end of the hold - rows before Event: quit):
MEASURE end B (variant: every row after + 30 s, the exit frames included):
G5 WORD end A NOT_WORSE (delta +0.6802 %); end B NOT_WORSE (delta +0.6773 %)
```

### G6 (`g6.out.txt`, sha256 `1bfbbddae06519f198bcaab13372538cdea76089f4bcf85ac73be6991a978ea3`)

```
g6_m3a: scp24.py sha256 0b38cf7945e2664abac3b1537b9ff64627923f0567be45437677a5d70c34c419
RATCHET base qa_A: frames >= 3 vblanks 6.83 %; segments of 60 s 19.1 % 2.4 % 6.1 % 3.9 % 5.2 % 4.4 %; Delta_L bins -0.0416 0.0728 0.1396 0.0794; band of stage 1 (item 297 (g)) [3.98 %; 7.24 %]: in; stage 1-2 shares pa_A 3.98 %, pa0_A0 5.24 %, pb0_B0 6.02 %, pr_C 15.56 %; spread of one configuration C (pb0_B0 / pr_C) 9.54 p.p. > the threshold 5 p.p.
RATCHET m3_g6: frames >= 3 vblanks 1.17 % vs qa_A 6.83 %: delta -5.67 % (> 5 p.p.: False); segments of 60 s 7.2 % 1.2 % 0.3 % 0.0 % 0.0 % 0.1 %
RATCHET NONE (item 284 (e): one of two - UNDETERMINED, both - DEFECT; item 297 (g): NONE and DEFECT only with qa_A in the band, else UNDETERMINED)
G6 ROWS m3_g6: X ia_A3 (stop-check PASS); config rows of m3_g6 all ok; G1' word TWO_OF_TWO (one V: TWO_OF_TWO reads ONE_OF_ONE); outcome SPEED_OK; speed 1.0037; RATCHET NONE; R2 OK
G6 RATCHET line: RATCHET m3_g6: frames >= 3 vblanks 1.17 % vs qa_A 6.83 %: delta -5.67 % (> 5 p.p.: False); segments of 60 s 7.2 % 1.2 % 0.3 % 0.0 % 0.0 % 0.1 %
G6 PASS (item 756 (g)(6): G1' in [0.95; 1.05] - SPEED_OK, RATCHET NONE)
```

### G7 agg (`g7_agg.out.txt`, sha256 `1188d529eaad501eb11afe83784c2ad67bbbc2dcdbf247736994e7fd325ccdd4`)

```
G7 agg: logs MS1 18, FS15 8, missing segments none; F0 baseline 820; signatures MS1 152, FS15 42
G7 candidates 21
```

### G7 grep (`g7_grep.out.txt`, sha256 `09e74c6d98d7b2afaf1e8713aa27acb4f627fd67f99dd32de81887e5d1114390`)

```
G7 grep ms1: 36 files, rc 0, output grep_ms1.out.txt sha256 7e2e310a35900538; last line: themes with fatal hits: []
G7 grep ms1: fatal hits (sum of the theme rows) 0
G7 grep fs15: 16 files, rc 0, output grep_fs15.out.txt sha256 0eefb9ac776ad4f4; last line: themes with fatal hits: []
G7 grep fs15: fatal hits (sum of the theme rows) 0
```

### G7 wit (`g7_wit.out.txt`, sha256 `3d60dc5bff73bdcba5fc613cd0669d3232d4a1fb23634d4fc596dcc45e67eb9b`)

```
G7 wit sg: keys in FS15 27, in MS1 27, LOST 0 []
G7 wit hb: keys in FS15 27, in MS1 27, LOST 0 []
G7 wit mg: keys in FS15 27, in MS1 27, LOST 0 []
G7 wit ac: keys in FS15 27, in MS1 27, LOST 0 []
G7 wit f1: keys in FS15 27, in MS1 27, LOST 0 []
G7 wit f2: keys in FS15 27, in MS1 27, LOST 0 []
G7 witnesses lost 0
```

### Пары листов (`pairs.out.txt`, sha256 `ebc5c21efb19d6a1c319af480368b9dc2380306331b957e013b513977ab0b906`)

```
pair sg: left m3_sg_v_r1 (MS1), right m3_sg_f (FS15) -> pairs/pair_sg.png rc 0 sha256 ef03b440f2a20d3a
pair hb: left m3_hb_v (MS1), right m3_hb_f (FS15) -> pairs/pair_hb.png rc 0 sha256 4bab5cb2e6fefab2
pair mg: left m3_mg_v (MS1), right m3_mg_f (FS15) -> pairs/pair_mg.png rc 0 sha256 0391d8eaa2d23322
pair ac: left m3_ac_v (MS1), right m3_ac_f (FS15) -> pairs/pair_ac.png rc 0 sha256 d04ee72007fa2250
pair f1: left m3_f1_v (MS1), right m3_f1_f (FS15) -> pairs/pair_f1.png rc 0 sha256 723159a08169e6d1
pair f2: left m3_f2_v (MS1), right m3_f2_f (FS15) -> pairs/pair_f2.png rc 0 sha256 d764827e32758033
banner T231: top m3_sg_v_r1 (T231=1), bottom m3_sg_t2310 (T231=0), 19.5-21.5 s every 0.25 s -> pairs/banner_t231.png rc 0 sha256 cfd0c6f411064029
```

### Кэши

- K0 `k0/k0.tsv` sha256 `016dc55ca35f041ab020da402a2d5f70de5e1e499e743de06249b0e1403100cc` (manifest C:/kyty/m657/m3a/k0/k0.tsv files 4868 bytes 1318828127 listsha 016dc55ca35f041ab020da402a2d5f70de5e1e499e743de06249b0e1403100cc).
- K1 `k1/k1.tsv` sha256 `5d5692982938baa9b4142e43c5cde91f10af936105c1a7a43d72b5b4d9f96170` (manifest C:/kyty/m657/m3a/k1.new/k1.tsv files 5603 bytes 1555784988 listsha 5d5692982938baa9b4142e43c5cde91f10af936105c1a7a43d72b5b4d9f96170).


