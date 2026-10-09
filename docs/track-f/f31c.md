# F31c (`HPP-731`, Harness Engineer): серия воспроизведения Б25 `b25m_01`…`b25m_36` — `mini_giants_garden` на установленном FS11 `ea51ae80` — печать до первого тега

Трек F, Б25 (п. 667(г)–(е)). Разделы 0–8 — печать (до первого тега; после неё цепочка, ридер и правила чтения не меняются); раздел 9 —
отчёт серии (строки ридера, без вердикта; чтение — F31d лида по п. 667(ж)). Метки: [c] — код/лог прочитан или пересчитан, [I] — вывод,
[U] — неизвестно. Время — UTC.

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1; проверка — `refs_f31c.py`, 15/15, отрицательный контроль сдвигом 15/15, `ALL OK`)

- Задание — п. 667: `afb501a5:docs/ROADMAP.md:24191` (якорь «667. **Звено F31b трека F»; +1 — «   (а) **Приёмка F31a сделана п. 666**»);
  N и засчёт описи — `afb501a5:docs/ROADMAP.md:24195` (якорь «   (г) **N и засчёт описи»; +1 — «   (д) **Форма серии F31c»); форма —
  `afb501a5:docs/ROADMAP.md:24196` (якорь «   (д) **Форма серии F31c»; +1 — «   (е) **Остановка серии.**»); остановка —
  `afb501a5:docs/ROADMAP.md:24197` (якорь «   (е) **Остановка серии.**»; +1 — «   (ж) **Правило чтения F31d»); чтение лида —
  `afb501a5:docs/ROADMAP.md:24198` (якорь «   (ж) **Правило чтения F31d»; +1 — «   (з) **Звенья.**»); не заявляется —
  `afb501a5:docs/ROADMAP.md:24202` (якорь «   (л) **Не заявляется:**»; +1 — пустая строка, конец пункта).
- Форма серии F26c (детектор, кэши, определения) — п. 630(г) `afb501a5:docs/ROADMAP.md:23866` (якорь «   (г) **Форма серии F26c»; +1 —
  «   (д) **Остановка серии.**»); шлюз 1,5 / 4 и строки нагрузки — п. 632(в) `afb501a5:docs/ROADMAP.md:23885` (якорь «   (в) **Форма.**»;
  +1 — «   (г) **Чтение F26d»).
- Члены «дисплей ON» и «темп сцены» — п. 620(г) `afb501a5:docs/ROADMAP.md:23786` (якорь «   (г) **Решение 3»; +1 — «   (д) **Долги и
  прошлые серии.**»), их перенос в новый харнесс трека F — п. 620(д) `afb501a5:docs/ROADMAP.md:23787` (якорь «   (д) **Долги и прошлые
  серии.**»; +1 — «   (е) **Звенья.** `HPP-680`»); побудка дисплея — п. 623(в) `afb501a5:docs/ROADMAP.md:23815` (якорь «   (в) **Прямое
  указание пользователя»; +1 — «   (г) **Отступление исполнителя**»).
- Форма серии под замком — п. 634 `afb501a5:docs/ROADMAP.md:23897` (якорь «634. **Прямое указание пользователя в `HPP-697`»; +1 —
  «   (а) **Отменяется для серий»); линтер — п. 661(б) `afb501a5:docs/ROADMAP.md:24141` (якорь «   (б) **Линтер** `form634_check.py`»;
  +1 — «   (в) **Harness Engineer — каждая серия»), обязанность Harness Engineer — п. 661(в) `afb501a5:docs/ROADMAP.md:24142` (якорь
  «   (в) **Harness Engineer — каждая серия под зам»; +1 — «   (г) **F30m (`HPP-723`), остаток.**»).
- Форма V-тега FS11c — `24f62694:docs/track-f/fs11c/go_fs11c.sh:43` (якорь «  fs11_v) UF=""; SD=300; H=330; TO=480; REC="--r»; +1 —
  «  fs11_w) UF=""; SD=100; H=310; TO=900; »); среда `fs11_v` — константы `enter_scene.py` (`KYTY_FRAME_TRACE=lite`,
  `KYTY_GPU_HANG_ABORT_S=8`, `KYTY_GATE_FILE`, `KYTY_SAMPLE_GATE`, `KYTY_QUEUE_TRACE=1`, `KYTY_GUEST_ARGS`) плюс `KYTY_GPU_CLOCK_PIN=1`,
  `KYTY_GPU_MARKERS=0` [c].
- Порт харнесса — `C:/kyty/f287/f26c` (F26c, `HPP-692`, печать 3); ридер — порт `f26c_read.py`.

## 1. Бинарь (п. 667(д)(1))

- **Установленный FS11** `ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce` [c sha до печати, 2026-10-09 ≈ 17:44Z: `C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe`
  = закреплённой копии `C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe`]. Цепочка бинарь **не ставит**.
- Члены: полный sha256 установленного бинаря — до замка (иначе вызов не стартует), под замком до тега (`installed_before.txt`) и после тега
  (`installed_after.txt`, иначе `RETURN_FAILED`, замок держится); `binary_sha256` каждого `<tag>.json` = FS11 (ридер: иначе класс `HARNESS`).
  Sha перед первым тегом — строка вызова `base`; после последнего — строка вызова `return`.

## 2. Форма тега `b25m_NN` (п. 667(д)(2)–(3))

- Вызов: `enter_scene.py <tag> --level mini_giants_garden --attempts 1 --stable-draws 500 --timeout 60 --no-install --require-idle
  --gates-file gates_default.txt --pred pred/f31c_seal.md --entry-at-level --hold 300 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`; переменные
  `KYTY_*` и `VK_LAYER_*` шелла снимаются до вызова; ручки — позиционно.
- Среда тега (= `fs11_v` без `KYTY_REC`): `KYTY_FRAME_TRACE=lite`, `KYTY_GPU_HANG_ABORT_S=8`, `KYTY_GATE_FILE` (пустой текст,
  `gates_default.txt`, 0 байт), `KYTY_SAMPLE_GATE`, `KYTY_QUEUE_TRACE=1`, `KYTY_GUEST_ARGS=-lvl mini_giants_garden`, `KYTY_GPU_CLOCK_PIN=1`,
  `KYTY_GPU_MARKERS=0`. Без `KYTY_REC`, `KYTY_GAME_PATCH`, `KYTY_FIX_*`, `KYTY_TEST_*`; аргументы эмулятора — фиксированные `enter_scene.py`
  (`--vulkan-validation false`, без RenderDoc); `KYTY_GPU_CHECKPOINTS` не передаётся.
- **Вход и удержание.** `--entry-at-level` (F26c): вход — строка `GuestOut: Level has started: mini_giants_garden` после `LevelDocument
  Loaded: mini_giants_garden`; `--hold 300` считается от неё. `--timeout 60` — от старта процесса до строки входа; нет строки за 60 с ⇒
  процесс убивается по своему PID — помеха (п. 667(е)(2)).
- **Форма п. 634 / 660 / 661.** Первая исполняемая строка `launch_f31c.sh` и `go_f31c.sh` — `python "C:/kyty/KytyPS5/ps5
  em/docs/form634_check.py" --series C:/kyty/f287/f31c || exit 10`. Блоков тегов и окна нет; в запускателе — только дисплей, очередь
  замка и запуск; **одна** проверка сторожа (`guard_f31c.py scan`) и сеанса (`hold_f31c.py check`) на вызов — сразу после взятия замка, до
  манифеста; находка — замок отпускается, файлы не тронуты, вызов — помеха, повтор следующей командой. Наблюдение во время тега
  (`guard_f31c.py watch`, `hold_f31c.py watch`) — как F26c.
- Дисплей (п. 620(г)(1), 623(в)): `dispstate.py` — побудка до замка, удержание запроса дисплея на время тега, строка после `lock released`.
- Шлюз — `procload.py --max-rate 1.5 --max-total 4` и строки нагрузки хоста до/после тега (`hostload_f31c.py`) — **вариант исполнителя**:
  форма п. 632(в) серии того же детектора; слой `CLEAN` / `HOST_LOAD` — строка, не член.
- Проверка живого прогона (`runchk_f31c.py`, п. 587(ж)), очередь замка P > F > S (`queue_f31c.py`, п. 322(г)).

## 3. Кэши (п. 667(д)(4))

- **Папки серии:** `_ShaderCache/PPSA21564` (с `pipelines.bin`, каталогом варианта и `replay/`), `_ShaderSeeds/PPSA21564` — буква пункта;
  плюс `_PipelineCache` (блоб драйвера) и `_SaveData` — **вариант исполнителя** (как F26c).
- **База:** вызов `go_f31c.sh base` под замком до первого тега — манифест sha256 `base/base.tsv` и копии `base/copy_*`, член — манифест
  копий = базе (`EQUAL`).
- **Внутри серии кэши не возвращаются.** Член каждого тега: манифест до тега (под замком) = манифесту после предыдущего вызова
  (`state_last.tsv`); отличие ⇒ тег не стартует, `SERIES_STOP`, вопрос лиду. Отличие «до / после тега» — строка отчёта, не член.
- **Возврат:** вызов `go_f31c.sh return` под замком после последнего тега или после остановки: манифест конца = `state_last.tsv` (иначе
  `RETURN_HELD`, вопрос лиду), затем `rm` + `cp -a` копий базы, член — манифест после = `base.tsv` (`EQUAL`), установленный бинарь = FS11;
  провал — `RETURN_FAILED`, замок держится.
- GLCache драйвера — не копируется, не возвращается, не в манифесте (вариант исполнителя, как F26c). Процесс или сеанс пользователя во время
  тега — помеха и `SERIES_STOP` (вопрос лиду: кэши серии могли получить файлы пользователя).

## 4. Детектор и положительный контроль (п. 667(д)(5))

- Детектор — любая строка лога или stdout тега с одной из трёх подстрок: `There are too many objects/batches`,
  `command_buffer_writer.ppr.cpp`, `pc=0x00000009004a020e`.
- Положительный контроль до первого тега [c]: `fx_sweep_f26a.py` (копия F26c без изменений) — `ALL OK` (`fx_sweep_f26a.out.txt`: с. 59 E 1
  S1 2 S3 1, строка 627 192; с. 42 E 1 S1 1 S3 1, строка 4 407 364); ридер `f31c_read.py` — класс `DETECTOR` на трёх логах: оба лога
  п. 630(г)(5) (первая строка 627 190 / 4 407 362 — `ASSERT:` за две строки до текста) и `C:/kyty/f287/f30m/log_f30_s3_c5.txt` (строки
  3/3/3, первая — 985 555) — фикстуры `test_f31c_read.py`.

## 5. Ридер и засчёт (`f31c_read.py`; фикстуры `test_f31c_read.py` — 89 проверок, `ALL OK`)

- Проход по строкам лога тега (и stdout): детектор; первая строка входа `Level has started: mini_giants_garden`; кадры `FrameTrace: n=…
  dt_us=…` после неё до следующей `Level has started:` — число, Σ `dt`, максимум (определения F26a §3); на логе `s18_e2` — 19 929 кадров,
  332,6 с = F31a `ft_mgg.out.txt` [c фикстуры]; маркеры смерти — `Unhandled exception:`, `--- Fatal Error ---`, `--- Error ---`,
  `GpuHangAbort:`, `ErrorDeviceLost`, `Unhandled host exception`; `entry_s` — `attempts[0].started_s` json.
- **Классы тега (п. 667(е)):** `DETECTOR` — строка детектора (что бы ещё ни было) ⇒ стоп серии (е)(1); `HARNESS` — нет json, бинарь ≠ FS11
  или форма ≠ раздела 2 ⇒ стоп, вопрос лиду; `INTERFERENCE` — нет строки входа, `entry_s` нет или > 60 с, маркер смерти (иной маркер,
  `--- Error ---` / `Unhandled host exception` без детектора), Σ `dt` < 290 с, дисплей не ON после `lock released` ⇒ в N не идёт, серия
  продолжается (е)(2); `TEMPO` — засчитываемый тег с членом «темп сцены» не PASS ⇒ стоп, вопрос лиду (п. 620(г)(2), (д)); `COUNTED` —
  строка входа, `entry_s` ≤ 60, Σ `dt` ≥ 290 000 000 мкс, 0 маркеров смерти, бинарь и форма раздела 2, дисплей ON, темп PASS.
- **Кадр ≥ 1 с — не помеха (п. 667(е)(3)):** число кадров ≥ 1 с после входа и до него — строки ридера и отчёта. Края фикстур: Σ ровно
  290 000 000 — `COUNTED`, 289 999 999 — помеха; кадр 1 000 000 и 3 700 000 мкс — `COUNTED` (строка 1); `entry_s` 60,0 — `COUNTED`, 60,1 —
  помеха.
- **Темп сцены** — `tempo_f31c.py` (копия `tempo_f26c.py`), форма не W: средний `dt` `FrameTrace` после строки уровня < 100 000 мкс; член
  читается только у тега, иначе засчитанного (вариант исполнителя F26c).
- Таблица `f31c_read.py --table`: строка `SERIES tags … counted … interference … detector … harness … tempo …; N = 5 inventory + k = … of
  41; lock <s> s of 14400; state GOING | COMPLETE | DETECTOR_STOP | HARNESS_STOP | TEMPO_STOP | INTERFERENCE_STOP | LOCK_BUDGET_STOP`.

## 6. Опись (п. 667(г)) — перепроверка до первого тега (`inv_f31c.py`, `inv_f31c.out.txt`)

| Лог | Бинарь | sha256 лога | Строка входа | Кадров | Σ `dt`, с (лид) | max `dt`, мкс | `--- Error ---` | `Unhandled host exception` | Детектор | Итог |
|---|---|---|---|---|---|---|---|---|---|---|
| `C:/kyty/s144/log_v144_20.txt` | `9235a7ac` | `ea7e3094…` | 215 919 | 19 864 | 332,7 (332,7) | 162 163 | 0 | 0 | 0/0/0 | PASS |
| `C:/kyty/f287/fsc/log_fs_g.txt` | `dac02fb9` | `775332c0…` | 213 961 | 19 917 | 332,7 (332,7) | 172 573 | 0 | 0 | 0/0/0 | PASS |
| `C:/kyty/s288/s15/log_k_13.txt` | `2c9b69b9` | `0c455660…` | 212 963 | 18 128 | 302,5 (302,5) | 330 985 | 0 | 0 | 0/0/0 | PASS |
| `C:/kyty/s288/s18c/log_s18_c13.txt` | `b3cee576` | `2b49d085…` | 339 916 | 19 938 | 336,8 (336,8) | 3 715 370 | 0 | 0 | 0/0/0 | PASS |
| `C:/kyty/s288/s18c/log_s18_e2.txt` | `b3cee576` | `cf9b7dbf…` | 227 500 | 19 929 | 332,6 (332,6) | 193 550 | 0 | 0 | 0/0/0 | PASS |

Итог: **5 из 5 PASS, тегов замены 0 ⇒ серия — 36 тегов, итог правила — 41 вход.** Маркеров смерти в пяти логах 0; кадр ≥ 1 с — 1 (`s18_c13`,
3,7 с; строка, п. 667(е)(3)). Полные sha256 — `inv_f31c.out.txt`.

## 7. Остановка, очередь, бюджет (п. 667(е))

- После каждого тега `post_f31c.sh` (вне замка): темп, ридер, таблица; состояние ≠ `GOING` ⇒ файл `SERIES_STOP`, следующий тег не стартует.
  `DETECTOR_STOP` ⇒ лог и `<tag>.json` сохраняются, вызов `return`, отчёт. `INTERFERENCE_STOP` (5 помех) / `LOCK_BUDGET_STOP` / `HARNESS_STOP`
  / `TEMPO_STOP` ⇒ вопрос лиду комментарием в `HPP-731` с упоминанием и строкой в корне `HPP-287`; возврат кэшей — по ответу.
  `COMPLETE` (36 засчитанных) ⇒ вызов `return`, отчёт.
- **Теги — только `b25m_01`…`b25m_36`** (скрипты другие имена не принимают); при помехах засчитанных к концу < 36 — вопрос лиду; теги сверх
  36 без пункта лида не запускаются.
- **Бюджет замка ≤ 4 ч (п. 667(е)(4)):** сумма времени замка всех вызовов серии по `runs/lock.log` (база, теги, отказы под замком); ≥ 14 400 с
  до 36 засчитанных ⇒ `LOCK_BUDGET_STOP` после текущего тега, вопрос лиду. Оценка [I]: ≈ 12 с до входа + 300 с удержания + закрытие
  5–40 с + манифест двух проходов 10–20 с ⇒ ≈ 330–375 с на тег, 36 тегов ≈ 3,3–3,8 ч; оценки программы врут в 2–20 раз.
- Запуск — `launch_f31c.sh <tag>` (только запускает отсоединённый вызов), ожидание — `wait_f31c.sh` ≤ 540 с отдельными командами до строки
  `rc=`; перед вызовом — `chk_f31c.sh` (STOP, замок, комментарии звена, очередь; строка `times.txt`). Внешнего `timeout` нет.
  `C:/kyty/f287/STOP`, чужой замок, комментарий-стоп — общие правила 26, 27, 30.

## 8. Не заявляется

П. 667(л): что Б25 — дефект эмулятора или игры; что assert вызван или не вызван T2 / `=5`; что Б25 воспроизводится или не воспроизводится на
FS11; что p̂ = 1/14 верна; что `-lvl mini_giants_garden` эквивалентен естественному входу; что `mini_giants_garden` теряет `SCENE_OK`; ни одно
число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется. Отчёт серии вердикта не пишет.

## Строки form634 и seal

- Линтер `form634_check.py` sha256 `f100a063fbc0063266a6443bac9b68f17e832fddd29456ccb475e7b1e76a4ded` (п. 661(б)).
- `form634_check.py --series C:/kyty/f287/f31c` — `ALL OK` (`form634_series.out.txt`); `--text docs/track-f/f31c.md` — `ALL OK` (`form634_text.out.txt`, прогон по этому файлу после вставки строк).
- Наборы: `test_f31c_read.py` 89 проверок `ALL OK`, `test_tools_f31c.py` `ALL OK`, `fx_sweep_f26a.py` `ALL OK`, `refs_f31c.py` 15/15 `ALL OK`, `inv_f31c.py` 5 из 5 `ALL OK` (sha выводов — строки seal ниже).

Строки seal (sha256 файлов цепочки на момент печати, 2026-10-09T17:51:48Z; `SHA256SUMS_seal.txt`):

```
seal: 1f5394b23fcdd39c450767e9de5efaa573d082acc4cdff39507c8d7e09227740 go_f31c.sh
seal: e8eb859ae264ae426da75e665f8caa527006b0721a0af030adfec8f6f021021b launch_f31c.sh
seal: 802028e89801090aa44d72f0c03292e998141d3e5a571a9f649ded719ebb643a wait_f31c.sh
seal: 96a39cb158a2788eb8448ee029c62508cc9dead1e4bf40f877505751b51f47a9 post_f31c.sh
seal: c42ac9006c56e2be585e2c5f0ce375fa0fdcfecce8b04c08bac0609614c814f3 chk_f31c.sh
seal: 3e4e2b41349f36081a7d50d2066cfc6e7f0a848a57978d8d46c7789c949bdf78 enter_scene.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 run_safety99.py
seal: 330997b89ac7f86e2a8f8e5a4f889603bec3b777b7d91906b607c23f0f8305e1 f31c_read.py
seal: ba809a6181744b732477a0f3748971f385a6f31ec04d3f121b6822d6a13c8662 hostload_f31c.py
seal: e0ceab012b4a28e96e13815d0803e69c2a30bdb42e65adf49899465efa7b8edd test_f31c_read.py
seal: df05a1622f70a96be68d0c4357286831b2cf8f1d5186c6bcd50c80edea6898e2 test_tools_f31c.py
seal: 0312b02548b48bb9e6d291b2d198264012a62b587e009210a19f9207d934bde3 tempo_f31c.py
seal: f39ad298065f7879eb5508175c66b3951c2d9ed289b0e488db4a4bdb98c88c42 guard_f31c.py
seal: 8f1756df4224a8c36f5ab783c7737fc49271ef26e36fc817edf979adfa022572 hold_f31c.py
seal: 2512dd43a24a9f293bd192fdbf944a4ae392af5696bcdc44b4f14a9d407da0bd queue_f31c.py
seal: 15bee3568c8173840cc5efe2dc75e21a5d8b28bbb44535954d807d910e8a9b2b runchk_f31c.py
seal: 7e170d76c211be36e56f8a630679e59f508e6abc9d5b6fdf879673ebbfa36200 dispstate.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 idle142.py
seal: 392caca1562fb543abde98a4358a7d64acf43eed96c70a37b22abdda94b699f8 launch_run.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 procload.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb manifest_fs4c.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 gates_default.txt
seal: d058309c4ea589e699375f82a073abaa2688d5afc360bef3f76032beafb21b6f sweep_f26a.py
seal: 352f17009b0d5319cbf53befa9c3b4c4d89ecdda358b965c2c581c8e6290a3bb fx_sweep_f26a.py
seal: 3af17d92aa12c8a79395566a153d473096782b101e40973b41c548f954b417fe refs_f31c.py
seal: eda40758981ffa51bb3a4e216c7d00954f083867c062d082c490eadbb376b64b inv_f31c.py
seal: 05f0cac63f64824b2302fecee2742e2d2628374a756039e681345b100d15158e test_f31c_read.out.txt
seal: e8c787d68c770dfaae04fd30247ab48d6c57aaa3a89bf47817bc27e86803aca5 test_tools_f31c.out.txt
seal: fa6166b2e168432421aaefae194406af25ec30e408529a48ceb55bd365159cb3 fx_sweep_f26a.out.txt
seal: d9ae7fd216d2a74616c0f28f5101923f87731ddebbe5f54c7957746612bb2f88 refs_f31c.out.txt
seal: cb90b3136676f0f111ac8e319e1278581580c2e198b09031466c98940af521f8 inv_f31c.out.txt
seal: 2acbfcd779dbf6cffdeba7db76b4ca891e5b6ff5ff859030a3f1a9699f9bd6ab form634_series.out.txt
```

## 8а. Печать 2 (п. 669, до `b25m_02`; 2026-10-09T18:40:22Z)

Ответ лида п. 669 (KytyPS5 `66cffa08`) на вопрос о бюджете замка: проверка сеанса п. 634(б)(1) сразу после замка — ≈ 206 с на тег, замок тега
≈ 541 с, 36 тегов не помещаются в 14 400 с. Дифф печати 2 против печати 1 (`5004ea17`): (1) `f31c_read.py` — `LOCK_BUDGET_S = 23400`
(≤ 6,5 ч суммы замка всех вызовов в `runs/lock.log`; `LOCK_BUDGET_STOP` при ≥ 23 400 с до 36 засчитанных — стоп после текущего тега и пункт
лида); (2) `test_f31c_read.py` — края 23 399 с `GOING`, 23 400 с `LOCK_BUDGET_STOP`, 14 400 с — `GOING`; 90 проверок `ALL OK`. Других правок
цепочки нет: форма тега, проверка сеанса, сторож, шлюз, члены засчёта и помехи п. 667(е)(1)–(3), (5), правило F31d п. 667(ж), FS11,
возврат кэшей — без изменений. Раздел 7: «Бюджет замка ≤ 4 ч» читается «≤ 23 400 с (п. 669(в)(1))». Тег `b25m_01` прошёл под печатью 1
(сумма замка 748 с — бюджет не задет); вызов `b25m_02` 18:12:06Z остановлен шлюзом `procload` до замка (`rc=5`, игра пользователя `<app>`),
не тег. `form634_check.py --series C:/kyty/f287/f31c` — `ALL OK`; `--text` этого файла — `ALL OK` (`form634_text.out.txt`).

```
seal2: f91dd371c0c6e7b0bd355622267b76acdf3c844db74cecc6f1c90c7a938246b5 f31c_read.py
seal2: 0515dfe0d88d316031c64c1087b99fcee4ae65f41492f94d7247f34a32905a6e test_f31c_read.py
seal2: 354a8299d35d64e92b9597b2ff8666e7f1caead11b82a7c74af7b072fd8832b4 test_f31c_read.out.txt
seal2: 2acbfcd779dbf6cffdeba7db76b4ca891e5b6ff5ff859030a3f1a9699f9bd6ab form634_series.out.txt
was:   330997b89ac7f86e2a8f8e5a4f889603bec3b777b7d91906b607c23f0f8305e1 f31c_read.py (seal 1)
```
