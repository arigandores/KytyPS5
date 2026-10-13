# M6a3 (`HPP-856`, трек M, волна 2) — запасное чтение объектного PCM с проверкой ОС и правки стенда `KYTY_DIAG_M5W2`

Звено Emu Engineer по `ROADMAP.md` п. 772(в), (г), (д) (KytyPS5 `ae6f2e09`); основание — отзыв M6b2 `docs/track-m/m6b2/review.md`
(`eb751ec1`) RC2 и П2; вход — worktree `C:/kyty/m657/m6a/wt` HEAD `97198ce9`, `main` (код M6a2 `fce6480f`). Дата 2026-10-13 UTC;
время событий — `times.txt` (строки `date -u`). **Игра не запускалась; бинарь теста не установлен; ГП-кейсы `dl_cases.txt` не
запускались; сборки `--parallel 2`, приоритет Idle (п. 760).** Замка `C:/kyty/SEALED_RUN.lock` не было ни перед одной командой; серий
звена прогонов не шло (API в начале: `in_progress` — только `HPP-856`; прогон M7a `HPP-852` к этому времени принят лидом, п. 773).
Метки: [c] — проверено, [I] — вывод, [U] — неизвестно. **Код в игре не проверен — WIP до тегов M6c.**

## 1. Итог

| что | значение |
|---|---|
| коммит worktree | **`3d227024`** на `97198ce9` (= MS1 `ed94b13d` + M6a + M6a2 + M6a3), worktree `C:/kyty/m657/m6a/wt` |
| код в `main` | **`534d75af`** (`git cherry-pick -n 3d227024` на `69a32f85`; строки `+`/`−` = коммиту worktree, 190 = 190, `patch-id` `a41876a6` = `a41876a6`, `main_vs_wt.out.txt` `ALL OK`) |
| бинарь теста | `kyty_emulator.exe` **sha256 `2179005bc42e42133e92d4a4c9cc0a2f33b3670f0263a6ca67c2c3804ac7e43f`**, строка версии `KytyPS5-2026-09-15-6a2987a-1936-g3d2270241`; закреплённая копия **`C:/kyty/m657/bin/kyty_emulator_2179005b.exe`**; **не установлен** |
| подпись трансляции | `KYTY_SHADER_SOURCE_HASH` = **`8dcf31779bbcb7c6e605653a138dae162f645a46` = MS1** [c `kytyGitVersion.h` сборки]; изменены только `src/libs/diagM5W2.{h,cpp}` и `tests/MWave2DiagStand.cpp` — вне `src/graphics/shader/**` и `SHADER_CACHE_EXTRA_FILES` |
| `check_gate_order.py` | `GATE ORDER: clean` (гейтов и ручек нет; `C:/kyty/s136/step3/check_gate_order.py --src` worktree) |
| строки бинаря | `ao_obj_vq=%` ×1 (в `23f3c4e7` ×0), `inv_part_src=%` ×1, `ao_obj_unread=%` ×1, `M5W2Stat: when=%s` ×1, `g3d2270241` ×1, `8dcf31779bbc` ×1 (`binary_m6a3.out.txt`) |
| `shader_cfg_tests` | 135 тестов, **0 падений** (`failed names 0`; 5 строк со словом `failed` — те же, что у M6a2); 374 модуля SPIR-V **байт в байт = M6a2** (`tests_spv_cmp.out.txt`) |
| стенд | `run_stand_m6a3.py` **`ALL OK`** на сборке worktree и на сборке `main` (`wtmain` @ `534d75af`); `pure` **132 из 132**, `audio` **5 из 5** при `=1` и `=0` |
| мутанты | **23 из 23 членов пойманы** (4 названных п. 772 + 4 своих + 15 мутантов M6a2 на новом коде), пробный `state_unchecked` выжил (ожидаемо, §4); контроль восстановленного дерева `ALL OK`; исходники worktree после мутантов = до (sha256 трёх файлов) |
| сборка `main` | `wtmain` @ `534d75af`: стенд и `kyty_emulator` собраны (проверка компиляции; в `main` есть M7a T306 — подпись этой сборки не MS1, бинарь не используется) |

## 2. Правка (имя поля — п. 772(в))

**`diagM5W2.cpp`, `NoteAudioPort`, объектная ветка (только при `=1`, место вызова — прежнее `libAudio2.cpp` под `if (DiagM5W2::On())`):**
отказ `TryReadBacking` → `OsReadable(pcm, bytes)`; да — `std::memcpy` в буфер копии (сырое чтение, как у портов шин) и `Bump(g_ao_obj_vq)`,
дальше тот же `PcmHasNonzero` по копии (в `ao_obj_nz` — по содержимому; `ao_obj_push` уже посчитан); нет — `ao_obj_unread`, возврат.
Предел `MAX_GRAIN_BYTES` (4 МиБ) — до обоих чтений, как в M6a2.

**`OsReadable(addr, size)`** (безымянное пространство имён `diagM5W2.cpp`): `addr` ≠ 0, `size` ≠ 0, без переполнения; цикл `VirtualQuery` по
регионам одинаковых атрибутов от `addr` до `addr + size` (каждая страница диапазона лежит в одном из пройденных регионов): `State` =
`MEM_COMMIT`; `Protect` без `PAGE_GUARD` и `PAGE_NOACCESS`; базовая защита (`Protect & 0xff`) — одна из `PAGE_READONLY`, `PAGE_READWRITE`,
`PAGE_WRITECOPY`, `PAGE_EXECUTE_READ`, `PAGE_EXECUTE_READWRITE`, `PAGE_EXECUTE_WRITECOPY` (модификаторы `PAGE_NOCACHE`/`PAGE_WRITECOMBINE`
чтения не запрещают); иначе — нет. Замков эмулятора не берёт; вне Windows — всегда нет (запасного чтения нет). Окно между ответом ОС
и чтением — класс сырого чтения шин, принятый п. 769(г)(2) (п. 772(в)); `VirtualQuery` гонку с освобождением не исключает (п. 772(е)).

**`ao_obj_vq`** — дописано в конец `M5W2Stat:` после `inv_part_src` (`… ao_obj_unread= inv_part_src= ao_obj_vq=`); поле `Totals::ao_obj_vq`
— последнее; прежние имена и порядок полей не менялись; `M5W2Clr:` не тронута. Комментарий шапки `diagM5W2.h` — абзац M6a3.

## 3. Стенд (`tests/MWave2DiagStand.cpp`, драйвер `run_stand_m6a3.py`)

Новые случаи `pure` (поля — дельты одного вызова):

| случай | память | `ao_obj_push` | `ao_obj_nz` | `ao_obj_unread` | `ao_obj_vq` |
|---|---|---|---|---|---|
| `ao_obj_vq_nz` | частная фиксация (`AllocateRuntimeMemory` → `Commit` → `MappingType::Private`), ненулевой отсчёт | 1 | 1 | 0 | 1 |
| `ao_obj_vq_zero` | частная фиксация, нули | 1 | 0 | 0 | 1 |
| `ao_obj_unread` (M6a2) | `0x1000` | 1 | 0 | 1 | 0 |
| `ao_obj_noaccess` | страница хоста `MEM_COMMIT`, `PAGE_NOACCESS` | 1 | 0 | 1 | 0 |
| `ao_obj_guard` | страница хоста `PAGE_READWRITE \| PAGE_GUARD` | 1 | 0 | 1 | 0 |
| `ao_obj_span` | 16 байт: 8 на зафиксированной `PAGE_READWRITE`, 8 на следующей — только `MEM_RESERVE` | 1 | 0 | 1 | 0 |
| `ao_obj_nz_float` … `ao_obj_zero_int16` (M6a2) | хранилище (`KernelMapNamedFlexibleMemory`, читает `TryReadBacking`) | 1 | по содержимому | 0 | **0** |
| `ao_bus_nz` | хост (порт шины) | 0 | 0 | 0 | 0 |
| `clr_r8_hi_div8` (п. 772(г), П2 M6b2) | — | `clr_dw` 1, `clr_dw_div` 0, **`clr_dw_div8` 1** на `R8Unorm` `0x34121212` | | | |

Случаи `ao_obj_vq_*` — положительный контроль довода RC1 M6b2: `TryReadBacking` отвергает частную фиксацию [c стенда: при снятом
запасном пути `ao_obj_unread` 1, `ao_obj_vq` 0 — мутант `fallback_off`]. `audio`: **push 5** — первый объектный порт на частной фиксации
с ненулевой гранулой: при `=1` `d_obj_push 1 d_obj_nz 1 d_obj_vq 1 d_obj_unread 0`, при `=0` все дельты 0; push 4 (`0x1000`) — процесс
жив при `=0` и `=1` [c]. Глубина очереди контекста стенда — 8 (`patch_m6a3_b.py`: при умолчании 4 пятый неблокирующий Push отвергается
`0x80260008` — первый прогон стенда, `times.txt`). Итог строки `M5W2Stat: when=stand`: `ao_obj_push=10 ao_obj_nz=3 … clr_dw=13 …
clr_dw_div8=3 ao_obj_unread=4 inv_part_src=2 ao_obj_vq=2`, строка кончается на `inv_part_src= ao_obj_vq=` (член драйвера);
`M5W2Clr fmt=9` — `clr_dw=3 clr_dw_div=0 clr_dw_div8=2`. `printf`, `ampr`, `agc` — без изменений.

Порядок правки стенда: `patch_m6a3.py` (код + стенд) → прогон 1 (`pure` 128 из 128, драйвер ждал 120 — ошибка счёта драйвера;
push 5 — отказ очереди) → `patch_m6a3_b.py` (глубина 8), прогон 2 `ALL OK` → `patch_m6a3_c.py` (случай `ao_obj_span`, свой член
до мутантов) → прогон 3 `ALL OK`. Все три скрипта применены к worktree; `main` получил итог одним `cherry-pick`.

## 4. Мутанты (`mut_m6a3.py`, метод `mut_m6a2.py`: одна точная подстановка, сборка цели стенда, драйвер, возврат байт в байт)

| мутант | что | итог |
|---|---|---|
| `fallback_off` (п. 772(в)) | запасной путь снят (`if (true)` вместо проверки ОС) | CAUGHT — `ao_obj_vq_*`: `ao_obj_unread` 1, `ao_obj_vq` 0; audio push 5 |
| `os_check_off` (п. 772(в)) | проверка ОС снята (`if (false)`) — сырое чтение всегда | CAUGHT — `pure` умер `0xC0000005` на `0x1000` |
| `c_ao_obj_vq` (п. 772(в)) | `ao_obj_vq` не растёт | CAUGHT |
| `r8_low16` (п. 772(г)) | правило R8 по младшим 16 битам | CAUGHT — случай `0x34121212` |
| `prot_unchecked` (свой) | проверка `PAGE_GUARD`/`PAGE_NOACCESS` снята | CAUGHT — `pure` умер (страница `PAGE_GUARD`, `0x80000001`) |
| `guard_ignored` (свой) | `PAGE_GUARD` не исключается | CAUGHT — `pure` умер `0x80000001` |
| `first_region_only` (свой) | проверяется только первый регион | CAUGHT — `pure` умер `0xC0000005` (`ao_obj_span`) |
| `c_ao_obj_unread_fb` (свой) | отказ проверки ОС не считается | CAUGHT |
| `state_unchecked` (проба, не член) | снята проверка `State` = `MEM_COMMIT` | SURVIVED — ожидаемо: у `MEM_FREE` защита `PAGE_NOACCESS`, у `MEM_RESERVE` — 0, обе отвергаются проверкой защиты [I по описанию `VirtualQuery`]; проверка `State` оставлена по букве п. 772(в) |
| 15 мутантов M6a2 | `x_eq_div`, `c_minlod_div_x`, `c_clr_dw_div8`, `c_clr_fmt_div8`, `r8_never`, `r8_always`, `rg8_never`, `rg8_always`, `obj_raw_read`, `c_ao_obj_push`, `c_ao_obj_nz`, `c_ao_bus_push`, `c_ao_bus_nz`, `c_inv_part_src`, `src_eq_data` (якоря объектной ветки — на форме M6a3; `c_ao_obj_unread` M6a2 = `c_ao_obj_unread_fb`) | 15 CAUGHT |

Итог: **23 из 23 членов**, контроль `ALL OK` (`mut_m6a3.out.txt`; пробный прогон четырёх названных — `mut_m6a3_b1.out.txt`). Скрипт
собран `mk_mut.py` из `mut_m6a2.py` и дополнен режимом партий (`--only a,b,c <part>`) одной правкой до прогона; итоговый файл — в `sha256.txt`.

## 5. Состояние и его жизненный цикл (правило с. 134)

- Новый счётчик `g_ao_obj_vq` (`diagM5W2.cpp:52`) — `relaxed`-атомик, растёт только в `NoteAudioPort` (`:188`), не сбрасывается (сумма за
  процесс), читается `Read` (`:310`) и `PrintStat`.
- Новых TLS нет. Буфер `thread_local std::vector<uint8_t> copy` (`:175`, M6a2) запасной путь только перезаписывает (`memcpy` `bytes` байт,
  `:187`) после того же `copy.resize(bytes)`; при отказе проверки ОС (`:183`–`:185`) возврат до чтения копии. Выходы `NoteAudioPort`:
  `bytes == 0` (`:173`), `bytes > MAX_GRAIN_BYTES` (`:178`), отказ проверки ОС (`:185`), конец объектной ветки (`:193`), конец ветки шин
  — ни один не оставляет состояния, кроме буфера и счётчиков.
- `OsReadable` (`:79`) — чистая функция без состояния и без замков; `VirtualQuery` — системный вызов чтения карты памяти процесса.
  Под ней на месте вызова держится только `g_audioout2_port_mutex` (как и для `TryReadBacking`); замков эмулятора не добавлено.
- При `=0` новых действий нет: вызов `NoteAudioPort` только под `On()` [c стенда `audio` при `=0` — все дельты 0, процесс жив].
- Стенд: `PrivateAlloc`, `HostPage`, `HostSpan` (`tests/MWave2DiagStand.cpp:199`, `:231`, `:214`) выделяют память один раз на случай и не
  освобождают (процесс стенда кончается `_Exit`).

## 6. Что M6a3 НЕ доказывает

- где игра держит PCM объектных портов и что он читаем любым путём; что `VirtualQuery` исключает гонку с освобождением памяти (п. 772(е));
- что запасное чтение безопасно для страниц, которые игра защищает сама с иными флагами, кроме названных (проверяются только флаги ОС);
- что любое поле M6 ≥ 1 в игре; что модели M5a верны железу; ни одно число — не выигрыш; 60 FPS не обещаются.

## 7. Файлы (`docs/track-m/m6a3/`)

| файл | что |
|---|---|
| `patch_m6a3.py`, `patch_m6a3_b.py`, `patch_m6a3_c.py` / `patch_wt*.out.txt` | правки (якоря целыми строками), все `ALL OK` |
| `run_stand_m6a3.py`, `mk_driver.py`, `mk_mut.py` | драйвер стенда (из `run_stand_m6a2.py`) и его генераторы |
| `stand_wt.out.txt`, `stand_main.out.txt`, `stand_wt/`, `stand_main/` | прогоны стенда на сборках worktree и `main` |
| `mut_m6a3.py` / `mut_m6a3.out.txt`, `mut_m6a3_b1.out.txt`, `wt_before_mut.sha` | мутанты; sha256 исходников до мутантов |
| `gate_order_wt.out.txt` | `check_gate_order.py` |
| `tests.out.txt`, `tests_failed_lines.txt`, `tests_spv_cmp.out.txt` | `shader_cfg_tests` и сверка SPIR-V с M6a2 |
| `binary_m6a3.out.txt`, `main_vs_wt.out.txt` | строки бинаря и подпись; сверка `main` с worktree |
| `commit_msg_m6a3.txt`, `times.txt`, `sha256.txt` | сообщение коммита; время событий; sha256 файлов и бинаря |
