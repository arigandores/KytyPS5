# M6b3 (`HPP-857`, трек M, волна 2) — враждебное ревью правок M6a3 в коде измерения `KYTY_DIAG_M5W2`

**Вердикт: `PASS` — RC 0. Код п. 772(в), (г) верен, мутанты (в) и `r8_low16` ловятся стендом (свой прогон), `main` = worktree, набор
подписи не тронут, при `=0` путь T125 не меняется, новых замков эмулятора на запасном пути нет. Бинарь для M6c `HPP-850` —
`C:/kyty/m657/bin/kyty_emulator_2179005b.exe`, sha256 `2179005bc42e42133e92d4a4c9cc0a2f33b3670f0263a6ca67c2c3804ac7e43f`.**

Звено Red Team по `ROADMAP.md` п. 772(д) и п. 774 (KytyPS5 `ae6f2e09`, `3522823d`); вход — код `534d75af` (`main`), worktree
`C:/kyty/m657/m6a/wt` HEAD `3d227024` на `97198ce9`, бинарь теста `2179005b`, отчёт `docs/track-m/m6a3/report.md` (`dbd8518a`). Чтение
начато 2026-10-13T04:41Z, после пункта 774 (04:38Z). Замка `C:/kyty/SEALED_RUN.lock` не было ни перед одной командой; серий звена прогонов
не шло (API: `in_progress` — `HPP-857` и `HPP-853` M7b, ревью). Игра не запускалась, ГП-кейсы `dl_cases.txt` не запускались; сборки — только
цель стенда скриптами M6a (`--parallel 2`, Idle). Время событий — `times.txt`. Метки: [c] — проверено, [I] — вывод, [U] — неизвестно.

## 1. Что пересчитано самим

| что | итог |
|---|---|
| `main` = worktree | `git patch-id --stable`: `534d75af` — `a41876a6`, `3d227024` — `a41876a6`; строки `+`/`−` диффов — sha256 `8a3e935e…` оба; файлы — `src/libs/diagM5W2.{cpp,h}`, `tests/MWave2DiagStand.cpp` оба; блобы `diagM5W2.cpp` и стенда в `534d75af`, `3d227024` и HEAD `main` совпадают; родитель worktree — `97198ce9`; `libAudio2.cpp` в `97198ce9..3d227024` не меняется; worktree и `wtmain` чисты (`main_vs_wt.out.txt`) [c] |
| набор подписи | дифф — вне `src/graphics/shader/**` и `SHADER_CACHE_EXTRA_FILES` (`CMakeLists.txt:156`: `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `imageInfo.h`); `KYTY_SHADER_SOURCE_HASH` в `kytyGitVersion.h` сборки worktree = `8dcf31779bbcb7c6e605653a138dae162f645a46` = MS1; в бинаре строка хэша 1 раз [c] |
| бинарь | `C:/kyty/m657/bin/kyty_emulator_2179005b.exe` sha256 **`2179005bc42e42133e92d4a4c9cc0a2f33b3670f0263a6ca67c2c3804ac7e43f`** = `build/install` = отчёту; строки `ao_obj_vq=%` 1 (в `23f3c4e7` — 0), `inv_part_src=%` 1, `ao_obj_unread=%` 1, `M5W2Stat: when=%s` 1, `g3d2270241` 1 (`g97198ce90` 0); формат конца строки `… inv_part_src=%llu ao_obj_vq=%llu\n` (`binary_m6b3.out.txt`) [c]. Бинарь собран 04:30:04–04:30:33Z после последней правки `diagM5W2.cpp` (mtime 04:29:06Z, восстановление после мутантов автора) и после коммита `3d227024` (04:29:58Z) [c `times.txt` M6a3 и mtime] |
| стенд | свой прогон `run_stand_m6a3.py` на сборке worktree (цель стенда пересобрана мной, 04:43:01Z) и `main` (`buildmain`, сборка без работы — `wtmain` не менялся с 06:34 сборки автора): **`ALL OK`** оба (`pure` 132 из 132, `audio` 5 из 5 при `=1` и `=0`); вывод = выводу автора байт в байт (sha256 `0eb91ab0…` у четырёх файлов). Итог `M5W2Stat: when=stand … ao_obj_unread=4 inv_part_src=2 ao_obj_vq=2`; `audio` push 5: при `=1` `d_obj_vq 1 d_obj_nz 1 d_obj_unread 0`, при `=0` все дельты 0 [c]. Строка `times.txt` 04:42:31Z — прогон на exe автора (мои сборки в 04:42:28Z не запустились из-за кавычек `cmd`); зачётный — 04:43:18Z |
| мутанты | `mut_m6b3.py` (метод `mut_m6b2.py`, своя подстановка): названные п. 772 — `fallback_off`, `os_check_off`, `c_ao_obj_vq`, `r8_low16` — **4 из 4 пойманы**; `r8_low16` — членом `clr_r8_hi_div8 field=clr_dw_div8 delta=0 want=1`; пробы (не члены, все пойманы): `vq_on_unread` (счёт `ao_obj_vq` на отказе), `nz_skip_fb` (нет поиска ненулевого после запасного чтения), `copy_half` (запасное чтение половины гранулы — член `ao_obj_vq_nz` `ao_obj_nz`), `check_one_byte` (проверка ОС одного байта — смерть на `ao_obj_span`); контроль восстановленного дерева `ALL OK`, sha256 `diagM5W2.cpp` до = после, worktree чист (`mut_m6b3.out.txt`) [c] |

## 2. Члены п. 772(в), (г) и п. 772(д)

- **(в) запасной путь — ✓ [c кода].** `OsReadable` вызывается только после отказа `TryReadBacking`, внутри объектной ветки `NoteAudioPort`;
  `NoteAudioPort` зовётся только под `if (DiagM5W2::On())` (`libAudio2.cpp`, M6a; не менялся). Цикл `VirtualQuery` по регионам от `addr` до
  `addr + size` (переход на `BaseAddress + RegionSize`, защита от нероста), `State == MEM_COMMIT`, отказ при `PAGE_GUARD`/`PAGE_NOACCESS`,
  базовая защита `Protect & 0xff` — одна из шести названных; `addr` = 0, `size` = 0 и переполнение — отказ. Предел 4 МиБ — до обоих чтений.
  Сырое чтение — `memcpy` `bytes` байт в тот же буфер копии, затем тот же `PcmHasNonzero` по копии: `ao_obj_vq` ⊂ `ao_obj_push`, в `ao_obj_nz`
  — по содержимому. Форма совпадает с уже существующими проверками эмулятора (`graphicsRun.cpp` `PeekReadable`, `hostMemory.cpp`
  `IsAccessible`), а запасное `memcpy` по гостевому адресу при отказе `TryReadBacking` делает и сам путь загрузки буферов
  (`bufferCache.cpp` `CopyGuestToStaging`: «Not backed guest memory (module image, flexible memory): read the guest view directly») — значит,
  гостевой адрес частной памяти = адрес хоста [c кода].
- **Проба автора `state_unchecked` эквивалентна — согласен [I по описанию `VirtualQuery`]:** у `MEM_RESERVE` `Protect` = 0, у `MEM_FREE` —
  `PAGE_NOACCESS`, обе отвергаются проверкой защиты.
- **`ao_obj_vq` — последнее поле `M5W2Stat:` [c бинаря и кода]**, `Totals::ao_obj_vq` — последнее поле структуры, прежние имена и порядок
  не тронуты, `M5W2Clr:` не тронута.
- **(г) R8 — ✓ [c].** Случай `0x34121212` на `R8Unorm` ⇒ `clr_dw` 1, `clr_dw_div` 0, `clr_dw_div8` 1; код (а3) не менялся (блоб правила тот же,
  дифф его не трогает).
- **Стенд не тавтологичен [c].** Положительный контроль запасного пути — частная фиксация `AllocateRuntimeMemory` (путь `Commit` →
  `MappingType::Private`): при снятом запасном пути (`fallback_off`) там `ao_obj_unread` 1, `ao_obj_vq` 0, т. е. `TryReadBacking` её
  действительно отвергает; нулевой — хранилище (`ao_obj_vq` 0 на четырёх случаях M6a2) и `0x1000`/`PAGE_NOACCESS`/`PAGE_GUARD`/граница
  с зарезервированной страницей (`ao_obj_unread` 1, процесс жив). Сквозной путь `libAudio2` → `NoteAudioPort` — `audio` push 5.
- **Путь при `=0` [c].** Место вызова не менялось; стенд `audio` при `=0` — все дельты 0 на пяти Push, процесс жив.
- **Порядок замков запасного пути [c кода, I о ловушке].** Под `g_audioout2_port_mutex` (место вызова, как в M6a2): `TryReadBacking`
  (медленный путь берёт и отпускает `m_mutex` хранилища до возврата) → `VirtualQuery` (системный вызов, замков эмулятора нет) →
  `memcpy`. Новых замков эмулятора и обратного порядка нет. Единственная дорога к замку эмулятора — исключение на `memcpy`, если защиту
  страницы сменят между ответом ОС и чтением (обработчик исключений эмулятора) — это окно класса п. 769(г)(2), не исключённое п. 772(е).
- **Цена при `=1` [I].** Один `VirtualQuery` на регион гранулы на объектный Push, только при отказе `TryReadBacking`; решений по нему нет.

## 3. Требуемые изменения

Нет (RC 0).

## 4. Примечания (без кода; на решение лида, исход M6c не меняют)

- **П1.** Запасной путь не пробует `TryReadPrtBacking` (путь загрузки буферов пробует его между `TryReadBacking` и сырым чтением). Если PCM
  объектного порта лежит в PRT-памяти, а её гостевой адрес не зафиксирован на хосте, гранула уйдёт в `ao_obj_unread` ⇒ по п. 772(б)(4)
  «не определено» — ложного числа нет, только лишний пункт лида. Где игра держит PCM — [U]. Условие действия: M6c с `ao_obj_unread` ≥ 1 ⇒
  пункт лида о форме чтения называет и PRT.
- **П2.** Стенд проверяет частную фиксацию `AllocateRuntimeMemory` (чтение/запись); образ модуля (`AllocateProgramMemory`,
  `VirtualRangeType::Code`) стендом не проверен — его защиты входят в шесть названных [I], ответ даст `ao_obj_vq`/`ao_obj_unread` тега.
- **П3.** Сборка `kyty_emulator` в `C:/kyty/m657/m6a/build` после мутантов (автора и моих) перекомпилирует `diagM5W2.cpp` из байт-в-байт
  того же источника (менялся mtime); бинарь теста — закреплённая копия, её sha256 выше.

## 5. Что ревью НЕ доказывает

- где игра держит PCM объектных портов и что он читаем любым путём; что `VirtualQuery` исключает гонку с освобождением или сменой защиты
  (п. 772(е)); что любое поле M6 ≥ 1 в игре; что модели M5a верны железу; код игрой не проверялся (WIP до тегов M6c); ни одно число — не
  выигрыш; 60 FPS не обещаются.

## 6. Файлы (`docs/track-m/m6b3/`)

| файл | что |
|---|---|
| `review.md` | этот отзыв |
| `main_vs_wt.out.txt` | patch-id, строки диффов, блобы, родитель, чистота деревьев |
| `binary_m6b3.out.txt` | sha256 и строки бинарей `2179005b`, `build/install`, `23f3c4e7`; хэш подписи сборки |
| `stand_wt.out.txt`, `stand_main.out.txt`, `stand_wt/`, `stand_main/` | свой прогон стенда на сборках worktree и `main` |
| `mut_m6b3.py`, `mut_m6b3.out.txt`, `wt_before_mut.sha` | свои мутанты; sha256 источника до мутантов |
| `times.txt` | время событий (`date -u`) |
