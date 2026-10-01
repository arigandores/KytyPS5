# Печать звена F4c трека F — доказательные прогоны Б35 (`pred/f4c.md`)

Звено F4c (`HPP-337`, Harness Engineer). Первая запись — 2026-10-01T12:13:17Z (mtime; под замком P10 `gop8.sh pr_C`, взятым 12:12:32Z, —
нарушение общего правила 27, строка `times.txt`); правка §3 под букву `f4c_read.py` — вне замка после 12:20:06Z. ДО первого прогона серии F4c. Основание — `ROADMAP.md`
«СЕССИЯ 122» п. 254(ж)(2)–(3) (`d3a8d951`), **п. 262** (`4c45777b`, ответы лида на В1–В4 F4c и RC1–RC4 F4b), п. 268(в) (бинарь `c9a5e198`),
п. 270(д), п. 271 (`e2275b68`: F4b2 PASS, RC 0; (г) — наблюдения к F4c как данные), п. 272(в) (`16e506f7`: форма W и печать F4c не меняются).
Пункты после п. 272 к моменту печати: нет (перечитано перед печатью, HEAD KytyPS5 `16e506f7`). Без мутантов (описание звена). Харнесс
закоммичен `2031ef31` (пробуждение 4). После печати `go_f4c.sh`, `f4c_read.py`, `win_f4c.py`, наборы фикстур и все файлы §5 не меняются:
`go_f4c.sh` проверяет каждую строку `seal:` вызовом `f4c_read.py --check-seal` перед замком; `<tag>.json` каждого прогона несёт sha256 этой
печати (`--pred`). Путь: печать лежит в `C:/kyty/f287/f4c/pred/f4c.md` (харнесс читает `pred/f4c.md` от своей папки, как F2c
`f2c/pred/01_f2c.md`); байт-в-байт копия — `C:/kyty/f287/pred/f4c.md` (путь п. 262(ж)); sha обеих — строкой `times.txt`.

## 1. Критерий — буква п. 254(ж)(2) (`d3a8d951:docs/ROADMAP.md`, якорь «(ж) **Итерация F4 трека F = Б35»)

> (2) **«FIXED» — все:** (а) W Sky Garden с валидацией и precache по умолчанию на файле рецептов с записью № 1592, `KYTY_FIX_DUALSRC=1`:
> строка `GuestOut` есть, удержание ≥ 310 с, 0 `[Vulkan][E]`, 0 маркеров смерти; (б) контроль `=0`, тот же вход — остановка тем же текстом
> до `GuestOut`; (в) W `mini_giants_garden` `=1` с precache по умолчанию — удержание ≥ 310 с, 0 `[Vulkan][E]`; (г) V `mini_giants_garden`
> `=1` без валидации — удержание ≥ 330 с, видео ≥ 3 000 кадров, 0 глитчей, лист лида, без новых K1/K2 против `c142_04`; (д)
> `shader_cfg_tests` — прежний список падений (127/1, Б11). Новая ошибка валидации на (а)/(в) — новая строка реестра, F4 не FIXED.

Член (д) — у F4a2/F4b2 (тесты сборки), серией F4c не прогоняется; лист (г) смотрит лид (F4d). Константы п. 254(ж)(2) и п. 262 исполнитель
не менял.

Добавки п. 262: (д) — контроли допуска (ниже, §3); (е) — порядок (б) → (а) → (в) → (г), (б) без остановки тем же текстом до `GuestOut` —
стоп серии до (а), `NOT EVALUABLE`; удержание — Σ `dt_us` показанных кадров после первого кадра сцены (п. 221(в)); харнесс W `--hold 310`,
V `--hold 330`; кэши `_ShaderCache/PPSA21564` и `GLCache` (`GLRESTORE=1`) — копия до и возврат после вместе с `9235a7ac`; первая строка
новой ошибки валидации ≤ 300 знаков — в FACTS. П. 271(г): строка `DualSrcBlend: skip` того же PS при наличии `patched` провалом допуска не
считается; `KYTY_SHADER_CACHE` харнесс не ставит.

## 2. Что прогоняется

Бинарь правки — `C:/kyty/f287/bin/kyty_emulator_c9a5e198.exe`, sha256 `c9a5e1986e254132f776f0c7f1c9446d0bdc862e199bbbc1d57aedf17d4c9f9b`
(п. 268(в), приёмка F4b2 п. 271(а)); стенд **A** (п. 262(в)): до замка в бинаре есть строка подписи трансляции
`699c1e4b7db359067b461e029b913c4b6e78dc90` и строка `DualSrcBlend: patched`, иначе rc 1. Ставится ОДИН раз внутри замка на всю серию; в
ловушке выхода — возврат `C:/kyty/s128/kyty_emulator_9235a7ac.exe` (sha256 `9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7`,
проверка sha, до 3 попыток). Файл рецептов на момент печати — `_ShaderCache/PPSA21564/pipelines.bin` sha256 `1886cd73…` (подпись
`KytySC3:699c1e4b…`, запись № 1592 SRC1_ALPHA / ONE_MINUS_SRC1_ALPHA, PS `5514e10f1a60df83` — разбор `recipes_f4c_before.out.txt`); перед
каждым тегом харнесс разбирает файл заново (`recipes143.py` → `runs/recipes_<tag>.json`, строка `times.txt` со счётом и числом
dual-source записей). Вход — `-lvl <уровень>` (`KYTY_GUEST_ARGS`), файл гейтов пустой, позиционно `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`;
`KYTY_GPU_CHECKPOINTS`, `KYTY_FIX_B26`, `KYTY_S_PCW`, `KYTY_PIPELINE_PRECACHE`, `KYTY_SHADER_CACHE` не передаются (precache по умолчанию во
всех тегах — предмет проверки, форма п. 254(е) не применяется); `--attempts 1` (неудача — данные, повтора нет), `--stable-draws 300`,
`--require-idle`, `--no-install`. Порядок — ровно этот (стенд A):

| тег | член | окружение | удержание харнесса | буква удержания |
|---|---|---|---|---|
| `f4c_b` | (б) контроль W Sky Garden `underwater_aerial_garden` | `KYTY_FIX_DUALSRC=0`, `--vulkan-validation true`, `VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin`, `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000`, без видео | `--hold 310 --timeout 600` (ожидается остановка до входа, rc 1) | — |
| `f4c_a` | (а) W Sky Garden | то же, `KYTY_FIX_DUALSRC=1` | `--hold 310 --timeout 600` | Σ `dt_us` после первого кадра сцены ≥ 310 с |
| `f4c_v` | (в) W `mini_giants_garden` | то же, `KYTY_FIX_DUALSRC=1` | `--hold 310 --timeout 600` | Σ `dt_us` после первого кадра сцены ≥ 310 с |
| `f4c_g` | (г) V `mini_giants_garden` | `KYTY_FIX_DUALSRC=1`, без валидации, видео `KYTY_REC` (`--rec`) | `--hold 330 --timeout 480` | Σ `dt_us` после первого кадра сцены ≥ 330 с |

**Пре-проверка (п. 262(г)):** перед (б) и (а) в файле рецептов должна быть запись с SRC1-фактором (`f4c_read.py --pre-check <tag>`), иначе
стоп серии до тега, `NOT EVALUABLE`, вопрос лиду.

**Остановка серии (`f4c_read.py --stop-check`):** (б) без остановки тем же текстом до `GuestOut` (п. 262(е)); любой `NOT EVALUABLE` или
`NOT ADMITTED` (вариант исполнителя — вопрос 3 пробуждения 4, ответа нет: печатается как вариант исполнителя); тег без лога или json;
маркер смерти без строки `[Vulkan][E]` (первое воспроизведение K1/K2 — вопрос лиду). Остановка валидацией в (а)/(в) — данные, серия идёт
дальше. Стоп-файл `C:/kyty/f287/STOP` — до всего, перед замком и перед каждым тегом.

**Окно замка (п. 228(в), 268(д), 270(д), 271(д), 272(д); вариант исполнителя для очереди P > F):** в той же команде, что замок, сразу перед
ним — файла замка нет, стоп-файла нет; по ответу API (`win_f4c.py`, строка `times.txt` с ответом) `HPP-333` и `HPP-347` — `done` без
`executionRunId`, `HPP-328` (P10) — не `todo`/`in_progress` и без прогона; иначе BUSY rc 4. Начатая серия не прерывается; цепочка сессии
и трек P ждут `lock released`.

**Кэши (п. 228(в), п. 262(е)).** Внутри замка до установки: список содержимого `_ShaderCache/PPSA21564` (корень, вариантные папки,
`pipelines.bin`) и его копия — списки равны (строка `times.txt`); манифест `cachemf143.py`; список и копия `GLCache`
(`%LOCALAPPDATA%/NVIDIA/GLCache`). После серии в ловушке выхода: кэш прогона ПЕРЕНОСИТСЯ в `cache_run/<UTC>/` (сохраняется), копия
возвращается, список обязан совпасть со списком до серии; `GLRESTORE=1` — `GLCache` прогона переносится в `glcache_run/<UTC>/`, копия
возвращается, список обязан совпасть. Несовпадение любого возврата — rc 1 и стоп-файл `C:/kyty/f287/STOP` (стоп треку F), комментарий в
`HPP-337`.

## 3. Правило чтения (п. 254(ж)(2), 262(д)–(е), 271(г))

Чтение — `f4c_read.py --tag <tag>` (импорт `C:/kyty/s142/sc142.py` после проверки sha256 `1ce612cdd036e2382ce5c5aae6bd25836062830dc0952da8512a9f2a74bb38c3`
без правки). **Вердикт записи — строка `F4C VERDICT <tag> letter: …`**; порядок: `NOT ADMITTED` → `NOT EVALUABLE` → буква п. 254(ж)(2)
(`PASS`/`FAIL`; у (б) — `STOP SAME TEXT`/`NOT EVALUABLE`). Строка `F4C EXECUTOR MEMBERS <tag> [I]` вердикт не задаёт (п. 258(д)).

- **Допуск (иначе `NOT ADMITTED`):** одна попытка; `-lvl` уровня тега; sha256 бинаря в json = `c9a5e198…`; `KYTY_FIX_DUALSRC` ровно `0` у
  (б), `1` у (а), (в), (г); `KYTY_GPU_CLOCK_PIN=1`; нет `KYTY_GPU_CHECKPOINTS`, `KYTY_FIX_B26`, `KYTY_S_PCW`, `KYTY_PIPELINE_PRECACHE`;
  видео только у (г); `--vulkan-validation true` только у W, активность валидации по трём признакам п. 224 (0 «нет слоя», ≥ 1
  `validation_features`, ≥ 1 `[Vulkan][`); файл рецептов перед тегом разобран (`runs/recipes_<tag>.json`). Sha печати пишется в json
  (`--pred`), чтение его не сверяет — сверка печати только `--check-seal` перед замком.
- **Контроли п. 262(д) — члены допуска (иначе `NOT EVALUABLE`, не FAIL):**
  - все теги: ровно одна строка `DualSrcBlend: supported=1 enabled=<плечо>` и она до первой `GuestOut` (у (б) — до остановки);
  - (а), (в): ≥ 1 строка `DualSrcBlend: patched ps=5514e10f1a60df83` до первой `GuestOut`; одна строка `PipelinePrecache: N recipes ->`
    с N = счёту файла рецептов, разобранного перед тегом; нет строк `stale recipes` и `no … yet`; в файле перед тегом есть запись
    dual-source. **Вариант исполнителя (вопрос 1 пробуждения 4, ответа нет):** если первая `[Vulkan][E]` стоит раньше любой строки
    `N recipes ->`, контроль этой строки «не применим» — остановка валидацией внутри precache читается FAIL буквы (новая строка реестра),
    а не `NOT EVALUABLE`; строка `skip` того же PS при наличии `patched` провалом не считается (п. 271(г));
  - (б): 0 строк `DualSrcBlend: patched`; нет `stale recipes`; запись dual-source в файле перед тегом есть.
- **(б) `f4c_b`:** `STOP SAME TEXT` — до первой `GuestOut` есть `[Vulkan][E]` с текстом `srcColorBlendFactor (VK_BLEND_FACTOR_SRC1_ALPHA)
  is a dual-source blend factor, but dualSrcBlend feature was not enabled` (текст `w143_01`/`w143_10`; константа `STOP_TEXT` чтения) и
  вход уровня не состоялся; иначе `NOT EVALUABLE` и стоп серии.
- **(а) `f4c_a`:** PASS — вход, строка `GuestOut` есть, нет смены сцены, выход удержания без ошибки (`hold_exit` пуст), Σ `dt_us` после
  первого кадра сцены ≥ 310 с, 0 `[Vulkan][E]` (лог и stdout), 0 маркеров смерти (`sc142.markers`), строка `DualSrcBlend: supported=1
  enabled=1`; иначе FAIL (Σ < 310 при прочих выполненных — тоже FAIL буквы «удержание ≥ 310 с»; `hold_s` json — справка рядом).
- **(в) `f4c_v`:** PASS — вход, нет смены сцены, `hold_exit` пуст, Σ `dt_us` после первого кадра сцены ≥ 310 с, 0 `[Vulkan][E]`; маркеры
  смерти — член исполнителя [I].
- **(г) `f4c_g`:** PASS — вход, нет смены сцены, `hold_exit` пуст, Σ `dt_us` после первого кадра сцены ≥ 330 с, видео ≥ 3 000 кадров
  (`FRAMES_V`), `s51_vidglitch.py 4 6` 0 глитчей, лист
  `sheet_f4c_g.png` построен (смотрит лид), без новых K1/K2 против `c142_04` (кадр ≥ 1 с после первого кадра сцены или маркер смерти,
  которых нет в `c142_04`: там маркеров 0, K2 0, Σ `dt` 121,8 с); строка precache, `stale`/`no … yet`, ≥ 1 `patched` 5514 — члены
  исполнителя [I].
- **Новая ошибка валидации на (а)/(в):** первая строка `[Vulkan][E]` ≤ 300 знаков печатается в чтении и идёт в FACTS (новая строка реестра —
  лидом в F4d).
- **Итог серии:** «FIXED» по п. 254(ж)(2) — PASS (а), `STOP SAME TEXT` (б), PASS (в), PASS (г) и лист лида и (д) F4a2; решение — F4d.

## 4. Предсказание [I] (п. 262(е))

(а) PASS; (б) остановка `SRC1_ALPHA … dualSrcBlend feature was not enabled` до `GuestOut`; (в) 0 `[Vulkan][E]` (при неверной переписи —
`VUID-vkCmdDraw*-maxFragmentDualSrcAttachments-09239`); (г) без новых K1/K2. Стена серии ≈ 35–45 мин (4 тега + копии кэшей).

## 5. Строка вызова (п. 105(в))

go_f4c call: PLWAIT=540 bash C:/kyty/f287/f4c/go_f4c.sh series

Вызов — отсоединённо обёрткой (стена серии больше 600 с команды инструмента), ожидание — передним планом по ≤ 560 с в том же хартбите;
второй вызов при идущей серии запрещён (`attempt_<tag>.txt`).

## 6. Печать файлов

seal: 94a42554d43b42dab0741ff55643c880aed340954e12b72b1855de8f912aaac2 go_f4c.sh
seal: 3629be79fd4619caddc1353b863cdab104636039b0752434c0e617f9d20bb282 f4c_read.py
seal: 9447e6c0eecde5e221d20dbdd2dfbffcf826b472a636e4e1bf958cf0209b99f8 test_f4c_read.py
seal: 30bc829cf77c74f233fb56b6a1083c7c21ed48b04b91b0732b0045e6d0f5b804 test_go_f4c.py
seal: a66d5c1e32a94a9bdbef77e77cbc74bb0e185252723a71665a213b9c205c3e06 recipes143.py
seal: a5fe790abf14e7f8febdcf3bf14bb867daa5e57ee0d5aef5eeb7e3413b48274e shalist_f2c.py
seal: c3aba62535296eff5993cb4f1f5e699c090057245534c40c2973d99bfe87e747 win_f4c.py
seal: c00d24e4bc90aab4a57528fd43538de729f55081931a60d794c94f3fd2b24172 enter_scene.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 launch_run.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 run_safety99.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 idle142.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 procload.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d sheet142.py
seal: e196ac063a7e359f8a631bcc8ac1a75304c2497b78ed2d08274644953b358aae cachemf143.py
seal: 95ca04859e4955db3795afeefc150dcb287a3d6ef1aa64d50cddf5812957b535 fgcpu143.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 gates_default.txt
seal: 1ce612cdd036e2382ce5c5aae6bd25836062830dc0952da8512a9f2a74bb38c3 C:/kyty/s142/sc142.py
seal: 6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c C:/kyty/scripts/s51_vidglitch.py

Наборы (последний вывод): `test_f4c_read.py` — 116 проверок `ALL OK`, `test_f4c_read.out.txt` sha256
36c5c20bdcd5a308628c35ab8eb57ebdc30b11eb5c7a704f058ba7bb1ede86a4; `test_go_f4c.py` — 57 проверок `ALL OK`, `test_go_f4c.out.txt` sha256
da1512c1d388312b01132a437b808601cecc7608615235aeb4649e5453ff2fc1; бинарь правки sha256 c9a5e1986e254132f776f0c7f1c9446d0bdc862e199bbbc1d57aedf17d4c9f9b.

## 7. Не заявляется

Что пайплайн Б35 рисуется верно или неверно; что перепись `Location 1` → `Location 0 Index 1` даёт верную картинку; что какая-либо сцена
корректна или проходима до конца; ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.
