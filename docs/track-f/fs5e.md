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
