# FS5e (`HPP-513`, Harness Engineer): прогрев `fs5_i` на установленном FS5 `631ff987` — печать до тега

Трек F, пятый бинарь отгрузки FS5 установлен FS5d (п. 424(д), 426: 2026-10-04 08:34:30Z). Разделы 0–4 — печать (до тега; после неё цепочка,
ридер и правило чтения не меняются); раздел 5 — отчёт тега (строки ридера и исход прогрева; приёмка — стадия review лида пунктом-фактом).

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1)

- Задание — п. 410(г)(5): `7de178f9:docs/ROADMAP.md:21801` (якорь «   (5) **FS5e (Harness Engineer, под замком, после FS5d):** прогрев `fs5_i` —
  V Sky Garden формы `fs5_v` на установленном FS5, **кэши после тега не»; +1 — «   возвращаются** (каталог `_fixf10` у пользователя тёплый на Sky
  Garden; форма п. 300(б), Н2 F12b); члены `fs5_v`; провал — откат копией по (4) и пункт»).
- Откат — п. 424(е): копия `C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe` по sha256; холод — п. 424(ж) (FS5e греет только Sky Garden);
  установка — п. 426(а) (KytyPS5 `aaaac744`); признак серии — п. 425(г) (FS5e — серия).
- Образец харнесса — FS5c (`docs/track-f/fs5c.md`, печать `c734466d`): `go_fs5c.sh`, `fs5c_read.py` (sha256 ниже), форма `fs5_v`.

## 1. Бинарь и кэши

- Бинарь тега — **установленный** `ps5 em/kyty_emulator.exe` = FS5 `631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17`: сверка до
  замка (иной — отказ), внутри замка (`installed_before.txt`) и перед `enter_scene.py` (`installed_sha.txt`); ничего не копируется на место
  `kyty_emulator.exe`, кроме отката при `FAIL`.
- Кэши (`_ShaderCache`, `_PipelineCache`, `_SaveData`, GLCache драйвера) **не копируются, не возвращаются и не удаляются** (п. 410(г)(5));
  манифест sha256 до тега и после прогона и `cmp` — справка (рост ожидаем). Каталог `variant_fixb26_fixb1b_fixf10` до тега — строка `cold.txt`
  (на момент печати отсутствует; если появится — строка «warm form before», тег не отказывает, ридер печатает справку холода `NO`); после
  тега — `warm.txt` (число файлов, размер и sha256 `pipelines.bin`).
- Окружение — умолчания FS5: цепочка снимает все `KYTY_*` и `VK_LAYER_*`; позиционно — только `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`
  (`enter_scene.py` = FS5c с корнем `fs5/fs5e`: строки 1 и 86).

## 2. Форма тега и правило чтения (ридер `fs5e_read.py`; функции разбора — импорт `fs5c_read.py` FS5c без изменения)

- Форма = `fs5_v` FS5c: `enter_scene.py fs5_i --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install
  --require-idle --gates-file gates_default.txt --pred pred/fs5e_seal.md --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`.
- **Члены** (определения — `fs5c.md` §4, вид `v`): (1) бинарь — установленный до тега = бинарь тега = `631ff987`; (2) каждая строка
  `Shader translation cache:` кончается `variant_fixb26_fixb1b_fixf10`; (3) вход (`GuestOut: Level has started: underwater_aerial_garden`);
  (4) удержание ≥ 300 с (Σ`dt` после первого кадра сцены, `draws` ≥ 100); (5) нет конца процесса до таймаута; (6) 0 маркеров смерти (лог и
  stdout); (7) записей индекса видео ≥ 3 000; (8) `s51_vidglitch.py 4 6` — 0 одно-кадровых глитчей; (9) лист лида сделан; (10) **тёплая форма
  после тега**: `variant_fixb26_fixb1b_fixf10/pipelines.bin` есть, размер > 0 (цель прогрева; член исполнителя по букве «каталог тёплый»).
- **Справка** (вердикт не задаёт): ревизия `0e72bc1`; холодная форма до тега; кадры ≥ 1 с после первого кадра сцены (у `fs5_v` — строка
  отчёта, не гейт); `FixSval: mode=1 ubo_std_layout=1` до первой `GuestOut`; 0 `SPIR-V validation failed`; `AsyncPipelines: skipped draw`.
- **Исход** (строка `WARMUP VERDICT fs5_i:`):
  - `PASS` — все 10 членов `YES` ⇒ установка остаётся, rc 0;
  - `FAIL` — иначе ⇒ **откат внутри замка** копией `31cbfee8` с проверкой sha256 (строка `times.txt`), rc 6, вопрос лиду; откат не удался —
    замок остаётся, файл `RETURN_FAILED`, rc 8;
  - `INTERFERENCE` — строка `Window … minimized`, `Recovering Vulkan swapchain` или `GamePatch:` (п. 273(з)) ⇒ тег не читается как исход;
    установка остаётся (бинарь прошёл FS5c), rc 7, вопрос лиду о повторе — **вариант исполнителя** (буква п. 410(г)(5) помеху не называет);
  - нет строки исхода (ошибка ридера, выход до чтения) — установка остаётся (ничего не менялось), rc 1, вопрос лиду.
- Видео, лист (`sheet142.py`), пара `pair_fs5_i_fs5_v.png` (слева `fs5_i`, справа лист `fs5_v` FS5c) и ридер — **внутри замка** после прогона
  (исход решает откат); лист и пару смотрит лид на стадии review.

## 3. Протокол

- Одна попытка; один тег — один замок (`C:/kyty/SEALED_RUN.lock`, строка «FS5e HPP-513 go_fs5e.sh fs5_i …»); `lock taken|released fs5_i <UTC>` —
  `fs5e/lock.log`; события — строки `C:/kyty/f287/times.txt` в момент события; шлюз `procload.py` через маску `<app>` (`PLWAIT=120`); отказ BUSY
  до замка — не попытка (каталог тега переносится в `runs/fs5_i.busy_*`), повтор — после ожидания простоя.
- Стоп: `C:/kyty/f287/STOP` до замка; живой `kyty_emulator.exe` — отказ; печать проверяется по строкам `seal:` до замка (иной sha — отказ rc 1).
- Запуск — `launch_fs5e.sh fs5_i` (только запускает отсоединённый вызов), ожидание — `wait_fs5e.sh fs5_i` ≤ 540 с отдельными командами.
- Вызов (ровно один): `PLWAIT=120 bash C:/kyty/f287/fs5/fs5e/launch_fs5e.sh fs5_i`.
- Фикстуры ридера — `test_fs5e_read.py`: `checks 59 fails 0`, `ALL OK` (вывод `test_fs5e_read.out.txt`, sha256 ниже); проба на логе `fs5_v` FS5c —
  `probe_fs5_v.txt` (удержание 334,31 с, макс. `dt` 374 813, индекс 10 324 = п. 424(а); члены 1 и 10 — `NO`, как ожидается для тега FS5c).
  Мутантов нет (форма FS5c, F12f).

## 4. sha256 (цепочка проверяет каждую строку до замка)

seal: b15a067752024c216b356d42967e84b31f26cb1f532cb52d6fa5898fb81a0660 go_fs5e.sh
seal: 0908a11735502887a7b34c472b1c968f1766ebc0a7d20e99c65404a1dc1035c7 fs5e_read.py
seal: 8d9fe64e9c9fc22cbbff9f14554d861ad4d1a82e0aa8b27eba5c460083b9a2e3 test_fs5e_read.py
seal: 6bff3ee859a110969e64a3cdc8cc45b530e0b4121e6b0d3a4d697e0397f6274e test_fs5e_read.out.txt
seal: 40c5a0a605cc522cedaeb472997a4a3794e7972109e698a80b017b22ea8478fa launch_fs5e.sh
seal: f92e407fb4f18212679a53beb21412b3acbfe384598dcc93be889d4a60fd4786 wait_fs5e.sh
seal: 367465f958ac8f5e547730767d2a41484013af625b585e442ec3f2a2086a729d enter_scene.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 launch_run.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 run_safety99.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 procload.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 idle142.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d sheet142.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 gates_default.txt
seal: 4e3e04bdfbd721569606ef623104f1b59982c2afb47c01f90b9c956b5eabbca5 C:/kyty/f287/fs5/fs5c/fs5c_read.py
seal: 6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c C:/kyty/scripts/s51_vidglitch.py
seal: 631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17 C:/kyty/f287/bin/kyty_emulator_631ff987.exe
seal: 31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5 C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe
seal: 45f8fcd177da86e9493183e5437962e3656b0fb7a9226d730f47ed661fa635f1 C:/kyty/f287/fs5/fs5c/runs/fs5_v/sheet_fs5_v.png

## 5. Отчёт тега `fs5_i` (после печати `c53ce656`; печать, цепочка и ридер не менялись)

Источник — строки `C:/kyty/f287/times.txt` (UTC по `date -u`, в момент события), `fs5e/lock.log`, `runs/fs5_i/read.txt` (sha256 `472c11f1…`).

### 5.1 Вызовы

| время (UTC) | событие |
|---|---|
| 08:43:30 | вызов 1 `PLWAIT=120 … launch_fs5e.sh fs5_i` → 08:44:57 отказ шлюза BUSY (rc 5, не попытка): `procload: busy [('<app>', 42880, 0.995)]` — процесс — `python sweep_f17a.py` звена F17a `HPP-525` (срезы по 38 с подряд); каталог `runs/fs5_i.busy_084457` |
| 08:45:44 | вызов 2 → 08:47:14 отказ BUSY (rc 5, не попытка), тот же источник (pid 31360); комментарий в `HPP-525` `6ff39c4d` с просьбой приостановить срезы |
| 08:50:23 | вызов 3 (тот же, `PLWAIT=120`) → 08:51:53 `lock taken fs5_i`, шлюз `clean`, строк `seal:` проверено 19 |
| 08:51:58 → 08:58:08 | `enter_scene.py` rc 0: вход за 29,9 с |
| 08:58:36 → 08:59:04 | видео, лист, пара, ридер — внутри замка |
| 08:59:07 | `WARM-UP PASS - the install stays`; `lock released fs5_i` (rc 0) |

Попытка одна (вызов 3); помех прогона нет.

### 5.2 Строки ридера

- Бинарь: установленный до тега внутри замка = бинарь тега = в конце = `631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17` (FS5); ревизия
  `0e72bc1` (лог, строка 121).
- Лог `log_fs5_i.txt` sha256 `0543f233…`, 2 399 015 строк; stdout `bb2551dc…`; видео `rec_fs5_i.mp4` sha256 `7aa35aca…`.
- `Shader translation cache:` — одна строка, `…\variant_fixb26_fixb1b_fixf10`; холод до тега: каталог отсутствовал (08:51:56Z, записей
  `PPSA21564` 1 346), первая строка `PipelinePrecache: no …_fixf10\pipelines.bin yet`.
- Вход — строка 351 926; первый кадр сцены n 365; **удержание 334,41 с**; кадров ≥ 1 с после него **0** (макс. `dt` 459 233 мкс); смены сцены нет;
  конца процесса до таймаута нет (`outcome ok`, `hold_s` 330,1).
- Маркеры смерти 0 (лог и stdout); `FixSval: mode=1 ubo_std_layout=1` строка 79 < первой `GuestOut` 11 892; `SPIR-V validation failed` 0 / 0;
  `AsyncPipelines: skipped draw` 1 996 (справка; у `fs5_v` FS5c — 1 843).
- Окно: событий нет, `Recovering Vulkan swapchain` 0, `GamePatch:` 0.
- Видео: индекс **10 335** записей, `s51_vidglitch.py 4 6` — **0 одно-кадровых глитчей**; лист `sheet_fs5_i.png` (10 335 кадров, шаг 215, 8×6),
  пара `pair_fs5_i_fs5_v.png` (слева `fs5_i`, справа `fs5_v` FS5c) — для лида.
- **Тёплая форма после тега:** `variant_fixb26_fixb1b_fixf10` — 397 файлов, `pipelines.bin` 3 945 014 байт, sha256 `8a7ceb21…` (у состояния
  прогона `fs5_v` FS5c — тот же размер, sha `9d006681…`: справка).
- Манифест (справка, кэши не возвращались): до — 2 924 файла, 863 941 690 байт, listsha `c931d57a…` (= эталон FS5c); после — 3 321 файл,
  920 807 933 байт, listsha `265ba096…`; `DIFFER only-before 3 only-after 400`.
- Члены 10 из 10 `YES`, справка 5 из 5 `YES`, помех нет ⇒ **`WARMUP VERDICT fs5_i: PASS`** — установка FS5 `631ff987` остаётся, отката нет;
  каталог `_fixf10` у пользователя тёплый на Sky Garden.

### 5.3 Отклонения и вопросы

- Отклонений от печати нет. Два отказа BUSY до замка — не попытки (печать §3); вызов не менялся.
- Наблюдение для лида (не вопрос звена): срезы F17a короче 60 с идут подряд и дважды сорвали шлюз серии — буква правила 30 соблюдена, цель
  (п. 371(е)(2)) — нет; после взятия замка F17a ждал по правилу 27 («lock waited 428 s»).
- Не заявляется: что картинка верна; что SPIR-V корректен для устройства; что 0 кадров ≥ 1 с держится на других уровнях; что `skipped draw`
  не виден на картинке; что прочие `SCENE_OK` держатся на FS5; ни одно число — не выигрыш; 60 FPS не обещаются.
