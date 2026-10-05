# FS8e (`HPP-575`, Harness Engineer): прогрев `fs8_i` на установленном FS8 `2c9b69b9` — печать до тега

Трек F, восьмой бинарь отгрузки FS8 установлен FS8d (п. 544(в), 545: 2026-10-05 11:39:58Z). Разделы 0–4 — печать (до тега; после неё цепочка,
ридер и правило чтения не меняются); раздел 5 — отчёт тега (строки ридера и исход прогрева; приёмка — стадия review лида).

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1)

- Задание — п. 471(г)(5): `a6a250ce:docs/ROADMAP.md:22625` (якорь «   (5) **FS8e (Harness Engineer, под замком; `blocked` на FS8d):** прогрев
  `fs8_i` — V Sky»; +1 — «   (6) Бинарь любого трека, устанавливаемый после FS8, обязан содержать»).
- Откат — п. 544(г): `ce44b4b3:docs/ROADMAP.md:23171` (якорь «   (г) **Откат FS8 (текст Н2 п. 530(г); заменяет «или `KYTY_FIX_F19=0`» п. 471(г)(4)):**»;
  +1 — «   (д) **Пересмотр Ф22 (п. 415(е), 471(е)) — решение лида»): копия `C:/kyty/f287/bin/kyty_emulator_8df61c00.exe` (FS7) по sha256;
  `KYTY_FIX_F19=0` не используется.
- Чужие звенья и опознание — п. 545(г) `41a8265c:docs/ROADMAP.md:23182` (якорь «   (г) **Чужие звенья:** печати и звенья прогонов после этого
  пункта»; +1 — «   (д) **Ответ пользователю** — комментарием в `HPP-287`»); опознание FS8 — sha256 `2c9b69b9…` и строка версии `…-1889-g302347b4`
  в файле бинаря, в логе — ревизия `302347b`; `SDL_REVISION` признаком не служит (Н1 п. 530(г), 545(в)); комментарий лида `1e1fded8` в `HPP-575`.
- Образец харнесса — FS5e (`docs/track-f/fs5e.md`, `go_fs5e.sh`, `fs5e_read.py`) и форма `fs8_v` FS8c (`docs/track-f/fs8c.md` §3–4, печать
  `247da29a`, `fs8c_read.py` sha256 ниже = строке печати FS8c).

## 1. Бинарь и кэши

- Бинарь тега — **установленный** `ps5 em/kyty_emulator.exe` = FS8 `2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b`: сверка до
  замка (иной — отказ), внутри замка (`installed_before.txt`) и перед `enter_scene.py` (`installed_sha.txt`); ничего не копируется на место
  `kyty_emulator.exe`, кроме отката при `FAIL`.
- Кэши (`_ShaderCache`, `_PipelineCache`, `_SaveData`, GLCache драйвера) **не копируются, не возвращаются и не удаляются** (п. 471(г)(5));
  манифест sha256 до тега и после прогона и `cmp` — справка (рост ожидаем). Каталог `variant_fixb26_fixb1b_fixf10_fixf19` до тега — строка
  `cold.txt` (на момент печати отсутствует); после тега — `warm.txt` (число файлов, размер и sha256 `pipelines.bin`).
- Окружение — умолчания FS8: цепочка снимает все `KYTY_*` и `VK_LAYER_*`; позиционно — только `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`
  (`enter_scene.py` = FS8c с корнем `fs8e`: строки 1 и 94).

## 2. Форма тега и правило чтения (ридер `fs8e_read.py`; функции разбора — импорт `fs8c_read.py` FS8c без изменения)

- Форма = `fs8_v` FS8c: `enter_scene.py fs8_i --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install
  --require-idle --gates-file gates_default.txt --pred pred/fs8e_seal.md --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`.
- **Члены** (определения — `fs8c.md` §4, вид `v`; 14): (1) бинарь — установленный до тега = бинарь тега = json `binary_sha256` = `2c9b69b9`;
  (2) строка версии `…-1889-g302347b4` в файле установленного бинаря (Н1); (3) каждый текст ревизии лога и stdout = `302347b` (Н1); (4) каждая
  строка `Shader translation cache:` кончается `variant_fixb26_fixb1b_fixf10_fixf19` (≥ 1 строки); (5) `FixB4: mode=1` до первой `GuestOut`;
  (6) `FixF8: mode=1` до первой `GuestOut` (буква п. 471(г)(3)); (7) вход (`GuestOut: Level has started: underwater_aerial_garden`);
  (8) удержание ≥ 300 с (Σ`dt` после первого кадра сцены, `draws` ≥ 100); (9) процесс дожил до конца удержания (`outcome ok`, `hold_exit`
  пуст, `hold_s` ≥ 330); (10) 0 маркеров смерти (лог и stdout); (11) записей индекса видео ≥ 3 000; (12) `s51_vidglitch.py 4 6` — 0
  одно-кадровых глитчей; (13) лист лида сделан; (14) **тёплая форма после тега**: `variant_fixb26_fixb1b_fixf10_fixf19/pipelines.bin` есть,
  размер > 0 (цель прогрева; член исполнителя по букве «прогрев», форма FS5e).
- **Справка** (вердикт не задаёт): холодная форма до тега; кадры ≥ 1 с после первого кадра сцены (холодный вход; у `fs8_v` — строка отчёта, не
  гейт); `FixB24: mode=1` до первой `GuestOut`; `FixF8` по чтению п. 518(в)(4); `AsyncPipelines: skipped draw`.
- **Помеха** (строки `INTERFERENCE none:`): строка `Window … minimized`, `Recovering Vulkan swapchain` или `GamePatch:` (п. 273(з)); окружение и
  командная строка не формы `fs8_v` (функция `env_admit` FS8c); json `prereg` ≠ sha256 файла печати.
- **Исход** (строка `WARMUP VERDICT fs8_i:`):
  - `PASS` — все 14 членов `YES` ⇒ установка остаётся, rc 0;
  - `FAIL` — иначе (член `NO` или `NOT_DETERMINED`) ⇒ **откат внутри замка** копией FS7 `8df61c00` с проверкой sha256 (строка `times.txt`),
    rc 6, вопрос лиду; откат не удался — замок остаётся, файл `RETURN_FAILED`, rc 8;
  - `INTERFERENCE` — строка помехи `NO` ⇒ тег не читается как исход; установка остаётся (бинарь прошёл FS8c), rc 7, вопрос лиду о повторе —
    **вариант исполнителя** (буква п. 471(г)(5) помеху не называет; форма FS5e);
  - нет строки исхода (ошибка ридера, выход до чтения) — установка остаётся (ничего не менялось), rc 1, вопрос лиду.
- Видео, лист (`sheet142.py`), пара `pair_fs8_i_fs8_v.png` (слева `fs8_i`, справа лист `fs8_v` FS8c) и ридер — **внутри замка** после прогона
  (исход решает откат); лист и пару смотрит лид на стадии review.

## 3. Протокол

- Одна попытка; один тег — один замок (`C:/kyty/SEALED_RUN.lock`, строка «FS8e HPP-575 go_fs8e.sh fs8_i …»); `lock taken|released fs8_i <UTC>` —
  `fs8e/lock.log`; события — строки `C:/kyty/f287/times.txt` в момент события; шлюз `procload.py` через маску `<app>` (`PLWAIT=120`); отказ BUSY
  до замка — не попытка (каталог тега переносится в `runs/fs8_i.busy_*`), повтор — после ожидания простоя.
- Стоп: `C:/kyty/f287/STOP` до замка; живой `kyty_emulator.exe` — отказ; печать проверяется по строкам `seal:` до замка (иной sha — отказ rc 1).
- Запуск — `launch_fs8e.sh fs8_i` (только запускает отсоединённый вызов), ожидание — `wait_fs8e.sh fs8_i` ≤ 540 с отдельными командами.
- Вызов (ровно один): `PLWAIT=120 bash C:/kyty/f287/fs8e/launch_fs8e.sh fs8_i`.
- Фикстуры ридера — `test_fs8e_read.py`: `checks 97 fails 0`, `ALL OK` (вывод `test_fs8e_read.out.txt`, первая строка `suite test_fs8e_read.py
  sha256 834d8eae… target fs8e_read.py sha256 ed4e087d…`); маска `<app>` и корень `enter_scene.py` — `test_enter_scene_mask.py` `ALL OK`
  (m11 — корень `fs8e`); проба на логе `fs8_v` FS8c — `probe_fs8_v.txt`: члены 1 и 14 — `NO` (установленный до тега FS6, `warm.txt` нет), прочие
  12 — `YES`, помех нет ⇒ `FAIL`, как ожидается для тега FS8c. Мутантов нет (форма FS5e, FS8c).

## 4. sha256 (цепочка проверяет каждую строку до замка)

seal: 5e2d03423318491887922b3332836b3e2a2a9f5ff66f3a9445b461dda466fe69 go_fs8e.sh
seal: ed4e087d9a3c9aa86b65843d58b6ca6ed61c38e460164699eca903c76ba6d60f fs8e_read.py
seal: 834d8eaec9a0553d3dd736f75185f8640aed6d45622058a1e7a6097b13309d50 test_fs8e_read.py
seal: 782863b73084eb5f9fbdb0cf94ff248044ee100188b639df30735be866e21f95 test_fs8e_read.out.txt
seal: 5a7cbfe0dce2cfe84bd0a3cedb2ac33c86c607b059080ef647ec0d4d4d94b3d9 launch_fs8e.sh
seal: df2547975bb893f3db5e91de2688a941c9fa590f880e914f5b273eaaf40891fb wait_fs8e.sh
seal: 70acbbf7bada09ad03f75e3cbfe565d4af976148a7a295060210a13a14e54148 enter_scene.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 launch_run.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 run_safety99.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 procload.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 idle142.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d sheet142.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 gates_default.txt
seal: 98a6360ed88adc80a26baa76f029e04096e52ea1056e6d6fcba308be8e490ee2 test_enter_scene_mask.py
seal: 21f22db0784f798fef8ec2302d192261176eea373a7415bac31ef6f2475e2e8f test_enter_scene_mask.out.txt
seal: 5c0b52c2750d5fab0ab39a74d22f4c48346115b30fb36e4b93f20514dd34b008 C:/kyty/f287/fs8c/fs8c_read.py
seal: 6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c C:/kyty/scripts/s51_vidglitch.py
seal: 2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe
seal: 8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7 C:/kyty/f287/bin/kyty_emulator_8df61c00.exe
seal: 3e6a777661abb74cfcb8150d244463b13f51a169c3ee3249582c4448f2cff0c6 C:/kyty/f287/fs8c/runs/fs8_v/sheet_fs8_v.png
seal: d1f740cb62d737e9bca41510a08256ba2b5bf6c4cd755e12dd44fbaa8b101f3c probe_fs8_v.txt
