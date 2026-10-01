# Трек F, звено F4a (`HPP-335`, Emu Engineer) — правка Б35 под `KYTY_FIX_DUALSRC`

Решение и критерий — `ROADMAP.md` «СЕССИЯ 122» п. 254(ж) (KytyPS5 `d3a8d951`), строка Б35 — п. 254(г)(1), реестр
`docs/track-f/register.md` §10 (`522d2ec7`). Время — `C:/kyty/f287/times.txt` (строки «F4a …», 05:00:03Z — 05:1xZ UTC). Игра не
запускалась; замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` не было ни на одной проверке (первая строка каждой команды);
установленная `9235a7ac` не тронута (sha256 `ps5 em/kyty_emulator.exe` = `9235a7ac…` после сборки). Файлы — `C:/kyty/f287/f4a/`,
копия — `docs/track-f/f4a/`.

**Статус: WIP** — собрано, НЕ установлено, дыма нет; дальше F4b (код-ревью Red Team), F4c (прогоны Harness Engineer).

## Главное

1. **Ответ п. 254(ж)(1) «только чтение» — НЕТ [c]:** PS `5514e10f1a60df83` записи № 1592 НЕ пишет выход с декорацией `Index 1`.
   Он пишет два выхода `out_mrt_0` (`Location 0`) и `out_mrt_1` (`Location 1`) и `gl_FragDepth`; `OpDecorate … Index` в модуле — 0.
   Источник — SPIR-V в кэше трансляции `ps5 em/_ShaderCache/PPSA21564/ps_5514e10f1a60df83_9b732ff0184ad6c1.bin` (единственный файл этого
   PS; подпись `KytySC3:699c1e4b…:robust:ftz:cbank` — трансляция `9235a7ac`; sha256 `39182e00…`; 1 модуль Fragment, 15 185 слов),
   разбор `spv_index.py` → `spv_index.out.txt`. По коду [c]: эмиттер SPIR-V не ставит `DecorationIndex` нигде в `src/` (выходы MRT —
   `HEAD:src/graphics/shader/recompiler/backend/spirv/spirvEmitterModule.cpp:675–685`, только `DecorationLocation = binding.location`).
   Запись № 1592 (`C:/kyty/s143/step3/recipes143.out.txt:3`): `color_count 1`, вложение 0 — RGB `SRC1_ALPHA` / `ONE_MINUS_SRC1_ALPHA`,
   альфа `ONE` / `ZERO`, PS `#0`.
   **По букве п. 254(ж)(1) — вопрос лиду, без кода** (ниже, «Вопрос лиду»). Правка п. 1 сделана, потому что она приказана отдельным
   пунктом, по умолчанию 0 и даёт строку `supported` для F4c; её одной для «FIXED» по моему чтению недостаточно [I].
2. **Поддержка устройством — ЕСТЬ [c]** (`vulkaninfoSDK.exe` SDK 1.4.357, без игры; выдержка `vulkaninfo_excerpt.txt`): `dualSrcBlend = true`,
   `maxFragmentDualSrcAttachments = 1`, драйвер 616.56, API 1.4.351. «ТУПИК стенда» не наступает; ожидаемая строка при `=1` —
   `DualSrcBlend: supported=1 enabled=1` [I до F4c].
3. **Правка** (коммит `1713a8be`, 1 файл, +13 строк): `HEAD:src/graphics/presentation/window/vulkanWindow.cpp:659–671`, сразу после
   `device_features.shaderInt64 = VK_TRUE;` (`4fc501f4:…/vulkanWindow.cpp:658`; файл между `4fc501f4` и `522d2ec7` не менялся):
   `dual_src_supported = supported_features2.features.dualSrcBlend == VK_TRUE` (структура уже заполнена `getFeatures2`, `:583`);
   `dual_src_enabled = dual_src_supported && Common::EnvFlagOn("KYTY_FIX_DUALSRC")`; при `enabled` — `device_features.dualSrcBlend = VK_TRUE`;
   строка `LOGF("DualSrcBlend: supported=%d enabled=%d\n", …)`.
   - **Ручка:** `Common::EnvFlagOn` (`src/common/envFlag.h`): не задана, `""`, `0`, `false`, `off`, `no` — ВЫКЛ; иначе ВКЛ. Не гейт
     и не `Knob` — таблицы `gates.h/.cpp` не тронуты.
   - **`=0` (по умолчанию):** `device_features` байт в байт прежние (`dualSrcBlend` = 0 от `vk::PhysicalDeviceFeatures device_features {}`);
     единственное отличие от прежнего — одна новая строка лога `DualSrcBlend: supported=1 enabled=0` (её требует п. 254(ж)(1); нужна
     контролю (б)).
   - **Один раз:** `VulkanCreateDevice` — `static`, единственный вызов `HEAD:…/vulkanWindow.cpp:1237` из `WindowContext::CreateVulkan()`
     (`:975`); строка печатается до `createDevice`, т. е. и при неудаче создания устройства.
   - **Состояние:** нового TLS, поля, счётчика нет; две локальные `const bool` в блоке `{}` и одно поле локальной `device_features`,
     живущей до `createDevice` в той же функции — состояние вызов не переживает.
   - **Подпись кэша трансляции НЕ меняется [c]:** подпись = `KYTY_SHADER_SOURCE_HASH` (SHA1 файлов `src/graphics/shader/**` и трёх
     дополнительных — `CMakeLists.txt:156`: `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`) + токены режимов
     (`shaderTranslationCache.cpp:576–594`); `vulkanWindow.cpp` в этот набор не входит, ручка токена не добавляет. Сборка до и после
     правки — `KYTY_SHADER_SOURCE_HASH "846a041a…"` (как у F2a `5821482a`). Файл рецептов `pipelines.bin` правка не трогает.
     **Предупреждение для F4c:** `846a041a…` ≠ `699c1e4b…` установленной `9235a7ac` — из-за коммитов треков после `4fc501f4` (F2a и др.),
     не этой правки: кэш трансляции у бинаря F4a холодный при любом значении ручки, каталог кэша общий с установленной сборкой (при
     `KYTY_FIX_B26=0`; при умолчании `KYTY_FIX_B26=1` — `variant_fixb26`) — копия и возврат кэшей по п. 228(в) обязательны.
4. **`check_gate_order.py`** (`C:/kyty/s113/check_gate_order.py`, до сборки): `GATE ORDER: clean`, вывод кроме первой строки совпадает
   с выводом F2a (гейты не менялись).
5. **Сборка** `build_local.cmd` на `1713a8be` (метка `1713a8b-dirty`: подмодуль `3rdparty/nlohmann_json` и неотслеживаемые файлы — как
   у прежних сборок): **sha256 `34d293adfc8938b835e029bc7088c1b9dbe687bd372f7f7e2facb1d603c3aae3`**, копия
   `C:/kyty/f287/bin/kyty_emulator_34d293ad.exe`. Строки `DualSrcBlend: supported=` и `KYTY_FIX_DUALSRC` в бинаре — по 1. Бинарь
   содержит и код коммитов после `4fc501f4` (F2a `KYTY_FIX_B26` с умолчанием 1, S5a/S5c `KYTY_S_PCW`, сессии 128–136) — тождество с
   `4fc501f4` при умолчаниях не проверено (то же замечание, что у F2a п. 7).
6. **Тесты** `shader_cfg_tests` (сборка `build_tests.cmd` на том же дереве): при `KYTY_FIX_DUALSRC=0` и `=1` — 127 тестов, падает 1
   (`ShaderCfgTests: failed: pixel IMAGE_SAMPLE_C must use OpImageSampleDrefImplicitLod` и `… IMAGE_SAMPLE_C_LZ must use explicit dref
   lod`, Б11) — списки равны; логи различаются одной строкой `elapsed_ms` (19 против 18); лог `=1` байт в байт равен логу F2a
   `cfgtests_fix1.log` (sha256 `5a60758a…`). Оговорка [c]: тесты не создают устройство через `vulkanWindow.cpp` (вызовов `CreateVulkan`
   / `VulkanCreateDevice` в тестах нет) — равенство списков ручку не проверяет, только отсутствие побочного влияния правки.

## Вопрос лиду (п. 254(ж)(1): «нет — вопрос лиду, без кода»)

Предсказание [I, не измерено]: с `KYTY_FIX_DUALSRC=1` создание пайплайна № 1592 пройдёт (текст остановки W `sc143` —
`vkCreateGraphicsPipelines(): … srcColorBlendFactor (VK_BLEND_FACTOR_SRC1_ALPHA) is a dual-source blend factor, but dualSrcBlend feature
was not enabled.`, `C:/kyty/s143/log_w143_01.txt` — снимается), но:
(1) вход `src1` смешивания по Vulkan берётся из выхода `Location 0 Index 1`, которого у PS нет — значение `SRC1_ALPHA` не определено;
на AMD-железе гостя при dual-source второй источник — экспорт MRT1 [I, внешнее знание о GCN/RDNA], т. е. верная трансляция для этого
пайплайна — `out_mrt_1` как `Location 0 Index 1`;
(2) PS пишет выходы в двух `Location` при `maxFragmentDualSrcAttachments = 1` — слой валидации SDK 1.4.357 несёт проверки
`VUID-vkCmdDraw*-maxFragmentDualSrcAttachments-09239` (строки найдены в `VkLayer_khronos_validation.dll`) — при первом draw этим
пайплайном (по AUDIT143 — в `mini_giants_garden`) вероятна новая ошибка валидации, т. е. по п. 254(ж)(2) «новая строка реестра, F4 не
FIXED» на (в); на (а) Sky Garden, где пайплайн только создаётся precache, — вероятно проходит [I].
Вопрос: (А) вести F4c на этой сборке как есть (проверка (а)/(б) и измерение (в)), или (Б) расширить правку до трансляции — при
`SRC1`-факторах вложения 0 объявлять выход MRT1 как `Location 0 Index 1` (правка `src/graphics/shader/**` — кэш трансляции холодный,
нужен признак смешивания в ключе/специализации PS), критерий — новым пунктом лида. Константы п. 254(ж) исполнитель не меняет.

## Изменённые файлы

`src/graphics/presentation/window/vulkanWindow.cpp` (+13), `docs/track-f/f4a.md`, `docs/track-f/f4a/` (скрипты `patch_f4a.py`,
`spv_index.py`, выводы `spv_index.out.txt`, `gate_order.out.txt`, `cfgtests_dualsrc0.log`, `cfgtests_dualsrc1.log`, `vulkaninfo_excerpt.txt`; копии с окончаниями строк LF — sha256 в тексте относятся к оригиналам в `C:/kyty/f287/f4a/`).

## Не заявляется

Что пайплайн Б35 рисуется верно или неверно; что правка снимает остановку W (не прогонялось); что какая-либо сцена корректна или
проходима до конца; что предсказания [I] выше верны; ни одно число — не выигрыш.
