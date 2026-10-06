# S18c2 — тег `s18_w2`: W с перестройкой S-replay под слоем валидации (Harness Engineer, `HPP-654`, п. 586(г)–(д))

Вердикта нет — его выносит S18d (`HPP-645`). Ниже — члены печати и числа.

## Печать и аппарат

- Печать: `docs/track-s/s18c2.md` (KytyPS5 `efeef344`). Запечатанная копия `C:/kyty/s288/s18c2/pred/s18c2_seal.md`, sha256
  `7149848230b1962aaed3aa3d462d71b95e91b8188c6dddf793ae31aa0eedfbbd`, `checkseal: SEAL: PASS` (18:30:45Z). Поле `prereg` прогона совпадает.
- Ридер `s18c2_read.py` (sha256 `5fb98401…9f684`). Он грузит запечатанный `s18c_read.py` S18c (`16570bed…6693`) без изменений и добавляет группу `W2`.
- Наборы:
  - `test_s18c2_read.py` — 96 проверок, `ALL OK`; вывод `test_s18c2_read.out.txt` sha256 `0e519fce…3ec4d8`;
  - `test_tools_s18c2.py` — 72 проверки, `ALL OK`; вывод `test_tools_s18c2.out.txt` sha256 `82569690…b39dd`.
- `mutlib` v4.1, полный зачётный прогон `--control --no-memo`: 54 из 54 убиты, контроли 3 из 3 выжили, стена 10,6 с.
  Вывод `mut_s18c2_read.run.txt` sha256 `689dbf14…343724`.

## Тег

| | |
|---|---|
| бинарь тега | S18a2 `b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a` (`binary_sha256` и `installed_sha.txt`) |
| установленный до / после | FS8 `2c9b69b9…` / FS8 `2c9b69b9…` |
| манифест возврата кэшей | `manifest cmp EQUAL files 4785 listsha e2e7e822…` |
| вход | `cat_full`: папки `variant_fixb26_fixb1b_fixf10_fixf19` нет; `replay/` = `replay_known` по манифесту `c644e3ad` (3 файла), побайтно |
| окружение | `KYTY_SHADER_SEED=0`; `KYTY_S_REPLAY` не задан; без `KYTY_S_REPLAY_TEST` |
| форма W | `--vulkan-validation true`, precache по умолчанию, `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000`, без фильтра |
| уровень | `underwater_aerial_garden`; вход за 45,2 с; удержание 310,0 с; закрытие 4,1 с, код 0 |
| лог | `log_s18_w2.txt` sha256 `bd9fef2374a6131e6d93fe8a0c0713e1da84c4b857b1b3cb1c0e5a34b440c4c9` |
| вывод ридера | `runs/s18_w2/read.txt` sha256 `303e09161e67a691978da744534fc7917580164d8f14347587fcb96f61be78ed`, `READING MEMBERS_PASS` |

## Члены п. 586(г) (ридер, группа `W2`)

| член | значение | ✓ |
|---|---|---|
| (1) строка `ShaderReplay: rebuild records=` | 1 строка | ✓ |
| (1) строк `rebuild skipped` нет | 0 | ✓ |
| (1) строк `ShaderSeed: installed` нет (лог / stdout) | 0 / 0 | ✓ |
| (2) `prepared / records` ≥ 0,90 | 3079 / 3079 = 1,0 | ✓ |
| (2) `prepared + rejected + pending = records` | 3079 + 0 + 0 = 3079 | ✓ |
| (2) `pipelines_bin=written` | `written` | ✓ |
| (3) 0 `[Vulkan][E]` | 0 | ✓ |
| (3) строк лимита слоя 0 | 0 | ✓ |
| (3) положительный контроль: `[Vulkan][W]` > 0 и `DualSrcBlend: supported=1 enabled=1` до первой `GuestOut` | `[Vulkan][W]` 901 513; `DualSrcBlend` в строке 78, первая `GuestOut` в строке 3 450 684 | ✓ |
| (3) не `VALIDATION_STOP` | E 0, исход `ok`, удержание 310,0 с | ✓ |
| (4) вход уровня | `Level has started: underwater_aerial_garden`, строка 3 667 399 | ✓ |
| (4) процесс жил до конца удержания 310 с | исход `ok`, `hold_exit` нет | ✓ |
| (4) 0 маркеров смерти (лог, stdout) | 0 | ✓ |

## Перестройка под слоем (числа лога)

- `ShaderReplay: mode=3 … compat=ok generation=46 corrupt=0 sources=727 specs=1218 pipes=3079 test=none`.
- `rebuild records=3079 prepared=3079 rejected=0 pending=0` (все `rej_*` = 0); `translate_ms=15461`, `wall_ms=17797`;
  `perms_new=1218`, `perms_cached=4656`, `rb_push_moved=0`, `rb_spec_changed=79`, `groups_same_pc=0`, `group_sources=727`, `pipelines_bin=written`.
- `rebuild-src records=727 prepared=727 rejected=0`. `rebuild-spec records=1218 prepared=1218 rejected=0`.
- `hits rb_used=454 rb_marked=1218 cap_skip=0 at=save`.
- Папка `_fixf19` после прогона (до возврата): 728 файлов, 727 трансляций. `pipelines.bin` — 34 901 497 байт, sha256 `fa953db6…df404`.
  Тот же sha дала и прерванная попытка 1.

## Справка

- Экран подготовки — 13 411 мс (строка 3 442 591).
- Кадров ≥ 1 с от первого кадра сцены — 0, от строки входа — 0 (под слоем, справка).
- Строк окна (`minimized`, `Recovering Vulkan swapchain`) 0, `skipped draw` 0, `GamePatch` 0.
- Каталог трансляции — `variant_fixb26_fixb1b_fixf10_fixf19`. Подпись — `KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:…:fixf19`.

## Ход и помехи (`C:/kyty/s288/s18c2/times.txt`)

1. **Попытка 1, 18:46:21Z–18:47:07Z — помеха окна, не исход уровня.** Прогон `18bc3ef2` оператор доски отменил в 18:41:50Z.
   Его команда окна простоя и отсоединённый вызов тега продолжили работу.
   - Эмулятор прожил 27 с, код выхода 0. Перестройка под слоем прошла: `records=3079 prepared=3079 rejected=0 pending=0`, `translate_ms=13708`, 0 `[Vulkan][E]`.
   - Затем в логе: `Window 1 gained keyboard focus`, `Mouse entered window 1`, `Mouse left window 1`, `ShaderReplay: close stop requested precache_active=1`.
     Окно закрыли на экране подготовки, строки `Level has started` нет. Страж пользовательских процессов: `user process seen: no`.
   - Возврат: FS8 до = после, `manifest cmp EQUAL`.
   - По п. 273(з) — один повтор тем же именем. Файлы попытки — `C:/kyty/s288/s18c2/old/s18_w2_a1win/`, лог sha256 `5bb09fdf…ffa92b`.
2. **Новый блок пользователя (общее правило 33).** Блок закрыт строкой `CLOSE user_window_close_s18_w2_a1` в 19:04:03Z.
   - Проверка той же секунды не засчитана: страж считает CLEAN строго после CLOSE. Проверки — 19:14:23Z (PENDING) и 19:24:41Z (OPEN).
3. **Окно простоя GPU п. 585(в) в 19:29:38Z — FAIL** (медиана 6, максимум 8). По п. (3) задания у W окно — по выбору исполнителя.
   **Решение исполнителя:** повтор запущен без окна; допуск `enter_scene --require-idle` остался (`pre_run`: медиана GPU 0, выборки 0, 0, 0, 4, 0 — отказа нет).
4. **Повтор**, замок 19:29:51Z–19:36:24Z: `MEMBERS_PASS`. Ожидания чужого замка не было, прочих серий в API не было.

## Не заявляется

- Что S-replay даёт тёплый первый вход пользователя до приёмки S18d.
- Что перестройка верна при любой будущей смене подписи.
- Что каталог повтора верен вне 19 сцен.
- Что 0 `[Vulkan][E]` под слоем доказывает верность картинки (видео у W нет).
- Ни одно число не выигрыш.
