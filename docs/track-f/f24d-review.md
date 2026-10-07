# F24d (`HPP-663`, Red Team) — ревью кода `KYTY_FIX_B13` и стенда Б13

**Вердикт: PASS.** Требуемых правок (RC) — 0. Наблюдений без сценария отказа — 5 (Н1–Н5, §9), ни одно не член и не блокер F24e.

Вход: задание — `ROADMAP.md` п. 595(ж) (KytyPS5 `1e46c4bd`, якорь «595. **Звено F24b трека F (`HPP-659`, лид): F24a (`HPP-658`) ПРИНЯТ»), правка — п. 595(д), критерий — п. 595(е); приёмка F24c — п. 601 (KytyPS5 `a750ae57`, якорь «601. **Звено F24c трека F (`HPP-662`, Emu Engineer; приёмка лида на стадии review)»), переданное F24d — п. 601(в)(1)–(4); код — `21f8ca76` (`main`); отчёт F24c — `496b018f:docs/track-f/f24c.md`, файлы `docs/track-f/f24c/`; бинарь F24c — `C:/kyty/f287/bin/kyty_emulator_91f155b7.exe` (sha256 `91f155b7…2e3f`, worktree `fbae3a68` = `0005e11f` + `ebf5484f` + `fbae3a68`). Чтение начато 2026-10-07T03:41:59Z (`date -u`), после коммита `a750ae57` (03:41:31Z). Игру не запускал; установленный `kyty_emulator.exe` (`b3cee576…305a` до и после), `C:/kyty/build/install` и кэши не трогал. Файлы — `C:/kyty/f287/f24d/`, в git — `docs/track-f/f24d/`. Время событий — `C:/kyty/f287/f24d/times.txt` (строки в момент события).

## 1. Сводка по списку п. 595(ж) и п. 601(в)

| # | член ревью | чем проверено | итог |
|---|---|---|---|
| 1 | `=0` по коду прежний (ветка `else` дословна) | свой скрипт `else_check_f24d.py`: блок родителя `21f8ca76^` (строки 233–260) против `else` правки (строки 278–305) — 28 / 28 строк, кодовые строки сдвинуты ровно на один таб, строки препроцессора не тронуты, расхождений 0 (`else_check.out.txt` — `ELSE VERBATIM OK`); `git diff -w 21f8ca76^ 21f8ca76` — удалённых строк 0 | ✓ |
| 2 | одно чтение ручки | `21f8ca76:src/graphics/host_gpu/regionManager.h:51`–`:52`: `static const bool` в `inline`-функции с внешним связыванием — один экземпляр на программу, потокобезопасная инициализация; `Common::EnvValueOn` (нет / `""` / `0` / `false` / `off` / `no` — ВЫКЛ) = п. 595(д); первый вызов — конструктор `MemoryTracker` до первого региона (`21f8ca76:src/graphics/host_gpu/memoryTracker.cpp:18`); порваться внутри операции не может (значение не меняется после инициализации) | ✓ |
| 3 | охват — только `ChangeState<Cpu, true>` | дифф `21f8ca76`: `regionManager.h` — только блок `if constexpr (source == DirtySource::Cpu && enable)` (ветка `if (FixB13Enabled())`, `21f8ca76:src/graphics/host_gpu/regionManager.h:246`), объявление ручки и комментарий хуков; путь `armdefer` (`21f8ca76:src/graphics/host_gpu/regionManager.h:496`) и создание региона не тронуты; `memoryTracker.cpp` — строка лога; `tests/B13EpochStand.cpp` — стенд. Других файлов нет (3 файла, 88 / 27) | ✓ |
| 4 | член (е)(0) своим чтением | §2 | ✓ (вывод F24c верен; опись неполна — Н1) |
| 5 | довод порядка памяти | §3 | ✓ |
| 6 | модель читателя стенда = коду построчно (закрывает п. 595(б)(2)) | §4 | ✓ |
| 7 | подпись трансляции не меняется | §5 | ✓ |
| 8 | свой прогон стенда | §6: `=1` — каждое плечо 10⁵ (принудительные и контроли) / 10⁶ (свободные), пропусков 0; `=0` принудительное точки 1 — 10⁵ из 10⁵ | ✓ |
| 9 | сборка из чистого worktree, sha256 = копии F24c или причина | §7: sha256 своей сборки `579e7951…` ≠ `91f155b7…`; причина названа классификатором — каталог сборки и метки, `.text` 0 | ✓ (причина названа) |
| 10 | свой мутант ловится членом (е)(1) | §8: `g1st` (глобальная первой) и `bitlast` (бит после глобальной) — оба ловятся | ✓ |
| 11 | п. 601(в)(2) — цена чтения локального static | §9 Н3 | наблюдение |
| 12 | п. 601(в)(3) — свободное плечо `=1` точки 13 | §6: прогнано, 0 / 0 из 10⁶ | справка |
| 13 | п. 601(в)(4) — имя макроса в заголовке стенда | §9 Н4 | наблюдение |

## 2. Член (е)(0) своим чтением

Писатель при `=1` (`21f8ca76:src/graphics/host_gpu/regionManager.h:257` → `21f8ca76:src/graphics/host_gpu/regionManager.h:262` → `21f8ca76:src/graphics/host_gpu/regionManager.h:266`): биты CPU-dirty → `m_epoch` (release RMW) → бит `bdabits` (release RMW) → `m_cpu_epoch` (release RMW) → сброс `B2Reuse` → `UpdateProtection`, всё под замком региона. Новое против `=0`: достижимо «регион `r+1` (и бит) при глобальной `E`», недостижимо «глобальная `E+1` при регионе `r` или чистом бите» (§3).

Все места чтения эпох я перечислил своим `git grep` по `21f8ca76` (`RangeWriteEpoch(`, `CpuWriteEpoch(`, `RegionWriteStamp(`, `UploadEpoch(`, `Epoch()`): 37 строк. Опись F24c (R1–R8) покрывает решения; не названы четыре места — все читатели одной эпохи региона, измерение или чтение под замком:

| место | что | вывод при `=1` |
|---|---|---|
| `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:1798` | `RsPost` (`rbslow`, измерение) — одно чтение `RangeWriteEpoch` | эпоха региона двигается раньше — только раньше видна «запись», безопасная сторона; решения нет |
| `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:1863` | `ShadowProbe` (`buffast`, тень) — свой стол по `RangeWriteEpoch` | как R4/R5 F24c |
| `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:2911` | `F5IdRangeWriteEpoch` (`KYTY_DIAG_F5ID`, умолчание 0; вызовы — `descriptors.cpp`, `textureCache.cpp`) | измерение, решения нет |
| `707e0d7d:src/graphics/host_gpu/memoryTracker.cpp:250` | `CollectCpuModifiedRangesStamped` — штамп под замком региона | писатель публикует всё под тем же замком — чтение видит всё или ничего при обоих значениях |

Единственный читатель, сочетающий две эпохи и решающий без замка, — `PrepareBda` + `SynchronizeBuffersByRegion` (R8 F24c); `bindlean` 2/3 (`rwe` до `gwe`, `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:1798` и строки 1589–1590 там же) читает две эпохи в обратном R8 порядке, но `gwe` только печатается (`moved_g`), гейт по умолчанию 0 — решения нет; при `=1` пара «`rwe` новая, `gwe` старая» становится возможна, это меняет только классификацию счётчиков `bln_srace`/`bln_sbad` (как сказано в R7 F24c). Читателя, которого порядок `=1` ломает, я не нашёл. Вывод F24c (е)(0) подтверждаю; неполнота описи — Н1.

## 3. Порядок памяти

C++: три записи писателя — release-RMW (`fetch_add` / `fetch_or`, `21f8ca76:src/graphics/host_gpu/regionDefinitions.h:28`); все записи `m_cpu_epoch` в дереве — `fetch_add` (свой `git grep m_cpu_epoch`: `:266`, `:288`, `:290` и инициализация `{1}`), значит release-последовательность любой из них продолжают только RMW других писателей и не рвёт обычная запись. Читатель: `CpuWriteEpoch` — acquire (`21f8ca76:src/graphics/host_gpu/memoryTracker.h:30`), затем бит — acquire / acq_rel (`21f8ca76:src/graphics/host_gpu/regionDefinitions.h:48`, `:51`) и `Epoch` — acquire (`21f8ca76:src/graphics/host_gpu/regionManager.h:172`). Если обход прочитал значение глобальной эпохи, записанное писателем W или позже в её release-последовательности, он синхронизируется с W; запись `m_epoch` и бит W предшествуют этой записи в порядке программы ⇒ happens-before последующих чтений обхода ⇒ по когерентности чтение-после-записи обход видит эпоху региона `≥ r+1` и поднятый бит (снимает бит только сам поток обхода). Компилятор не может опустить запись `m_epoch` / бита ниже release-RMW глобальной эпохи и не может поднять чтения обхода выше acquire-чтения глобальной. x86: `lock xadd` / `lock or` — полные барьеры, чтения между собой не переставляются (TSO). Довод F24c §1.2 верен.

Граница довода: он опирается на модель памяти и текст исходника [c стандарта и кода], а не на машинный код эмулятора — в бинаре эмулятора хуков нет, в стенде они есть (вызов внешней функции между атомарными операциями — сам по себе барьер компилятора). Стенд поэтому проверяет порядок программы, а не перестановку компилятором — Н2.

## 4. Модель читателя стенда против кода — построчно

Код — `707e0d7d` (места п. 595(ж)); в бинаре `fbae3a68` те же строки — `fbae3a68:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3448`, `fbae3a68:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3472`, `fbae3a68:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3474` (`renderContext.cpp` в `fbae3a68` = `707e0d7d`, `git diff` пуст; отличия `bufferCache.cpp` — только удалённая диагностика `KYTY_DIAG_F5ID` / `F5`, тела `SynchronizeBuffersByRegion` и `PrepareBda` совпадают).

| код (`707e0d7d`) | модель (`21f8ca76:tests/B13EpochStand.cpp`) | совпадает | что упрощено |
|---|---|---|---|
| `707e0d7d:src/graphics/host_gpu/renderer/renderContext.cpp:330` `cpu_epoch = CpuWriteEpoch()` (acquire, до обхода) | `21f8ca76:tests/B13EpochStand.cpp:162` `g = tracker.CpuWriteEpoch()` — то же чтение настоящего трекера | ✓ | — |
| `707e0d7d:src/graphics/host_gpu/renderer/renderContext.cpp:333` попадание кэша трёх эпох | `21f8ca76:tests/B13EpochStand.cpp:163` `g == cached_g` | ✓ | эпохи регистрации и карты постоянны; `reuse` (`KYTY_BDA_EPOCH_CACHE`) — умолчание «вкл.» |
| `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3506` `bit_clear = use_bits && !BdaTakeRegionWrite(index)` | `21f8ca76:tests/B13EpochStand.cpp:168` то же, настоящая `BdaTakeRegionWrite` | ✓ | `use_bits` = параметр `bits` (поколения постоянны; гейт `bdabits` в стенде выключен, но запись бита писателем безусловна) |
| `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3507` пропуск по биту при поколении штампа | `21f8ca76:tests/B13EpochStand.cpp:169` `bit_clear && seen_gen == GEN` | ✓ | самопроверка `bits_check` не моделируется — только читает |
| `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3530` `stamp = RegionWriteStamp(index)` | `21f8ca76:tests/B13EpochStand.cpp:173` то же | ✓ | — |
| `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3532` пропуск по штампу | `21f8ca76:tests/B13EpochStand.cpp:174` `seen_gen == GEN && seen == stamp` | ✓ | — |
| `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3539` `seen = {stamp, generation}` до обхода | `21f8ca76:tests/B13EpochStand.cpp:178` `seen = stamp; seen_gen = GEN` | ✓ | — |
| `707e0d7d:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3571` сбор под замком региона | `21f8ca76:tests/B13EpochStand.cpp:181` `CollectCpuModifiedRanges` | ✓ | ветка `bdanarrow` 2 (`…Stamped`, тоже под замком) не моделируется |
| `707e0d7d:src/graphics/host_gpu/renderer/renderContext.cpp:399` запомнить эпоху, прочитанную ДО обхода | `21f8ca76:tests/B13EpochStand.cpp:185` `cached_g = g` | ✓ | — |

Порядок решений модели = порядку кода; все чтения модели — настоящие функции трекера и карты бита; писатель — настоящий `MarkRegionAsCpuModified` → `ChangeState<Cpu, true>`. Опущенное (поколения, ветки сброса штампов, `bdanarrow`, многорегионный обход, `m_mapped_ranges_mutex`) не меняет решения о пропуске одного региона внутри зарегистрированного буфера. Вопрос п. 595(б)(2) закрыт: модель = коду в местах решения.

## 5. Подпись трансляции

Правка — `src/graphics/host_gpu/` и `tests/`; набор подписи — `${SHADER_SOURCE_DIR}/*.cpp|*.h|*.inc` плюс `SHADER_CACHE_EXTRA_FILES` (`fbae3a68:src/generate_version.cmake:45`). Строка своей сборки (`buildB/…/version` заголовок): `KYTY_SHADER_SOURCE_HASH "9177b4267de1fb8bac7d1113afd8733210addfac"` = S18 (`9177b426…`, подпись установленного `b3cee576`); `KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-1899-gfbae3a68"` = строке F24c (`binary_f24c.txt`). Каталог варианта не меняется ⇒ прогрева у F24e нет.

## 6. Свой прогон стенда

Своя сборка стенда (`b13_epoch_stand.exe` sha256 `09e314dc…`, worktree `fbae3a68`), свой скрипт `run_stand_f24d.py` (написан заново, не копия F24c). Итог — `stand_own.out.txt`, `ALL OK` (03:48:23–03:51:52Z):

| плечо | итераций | пропусков | R1 / R2 |
|---|---|---|---|
| `=1` forced 11 × `bdabits` 0 / 1 | 10⁵ / 10⁵ | 0 / 0 | R1 hit 10⁵, R2 scan 10⁵ |
| `=1` forced 12 × 0 / 1 | 10⁵ / 10⁵ | 0 / 0 | R1 hit, R2 scan |
| `=1` forced 13 × 0 / 1 | 10⁵ / 10⁵ | 0 / 0 | R1 scan, R2 hit |
| `=1` free 11 × 0 / 1 | 10⁶ / 10⁶ | 0 / 0 | R1 hit 4 047 / 5 944 |
| `=1` free 12 × 0 / 1 | 10⁶ / 10⁶ | 0 / 0 | R1 hit 7 753 / 6 416 |
| `=1` free 13 × 0 / 1 (справка, п. 601(в)(3)) | 10⁶ / 10⁶ | 0 / 0 | R1 hit 4 218 / 5 408 |
| `=1` before / after × 0 / 1 | 10⁵ каждое | 0 | — |
| **`=0` forced 1, `bdabits` 0** | 10⁵ | **10⁵** | R1 skip_stamp 10⁵, R2 hit |
| нет переменной, forced 1, 0 | 10⁵ | 10⁵ (как `=0`) | `FixB13: mode=0` |
| `=0` forced 2, `bdabits` 1 (справка) | 10⁵ | 10⁵ | R1 skip_bit |
| `=0` free 1 × 0 / 1 (справка) | 10⁶ / 10⁶ | 177 / 455 | — |

Каждое плечо: rc 0, строка результата, `fix_b13=` и `FixB13: mode=` по значению ручки. Свой прогон повторяет F24c независимо (у F24c `=0` free 181 / 507 из 10⁶, остальные плечи — те же исходы).

## 7. Сборка из чистого worktree

`mk_wt_f24d.sh C:/kyty/f287/f24d/wtB fbae3a68` (копия `mk_wt_f24c.sh`, путь `f24c` → `f24d`): `git status` 0 строк, CR в `src/` 0. Отдельно воспроизвёл перенос: worktree `wtC` от `0005e11f` + `cherry-pick 1570d110` + `cherry-pick 21f8ca76` (один конфликт, разрешён `resolve_wtB_f24c.py` F24c) — дерево `ffbc926e…` = дереву `fbae3a68` (`git diff --stat` пуст; `cherry_repro.out.txt`). Сборка `build_f24d.cmd B` (флаги F24c) — `BUILD OK`, 03:45:40–03:46:27Z.

**sha256 своей сборки `579e7951…64bf` ≠ копии F24c `91f155b7…2e3f`; причина названа:** классификатор `pediff3s_f24d.py` (копия моего FS8b, логика без изменений) — 4 179 байт отличий: 139 — имя каталога сборки `f24d`/`f24c` (строки `__FILE__`, путь PDB), 1 793 — метки анонимных пространств имён `?A0x<hex>` (хэш пути исходника), 12 — метка линковки и GUID RSDS, 2 235 — строки декорированных имён с меткой из 7 цифр вместо 8 (сдвиг на байт, класс (2b)); **`.text` 0, прочих 0, `VERDICT EXPLAINED`** (`pediff3s_emu.out.txt`; обратный порядок — тот же итог). Отрицательный контроль: копия `91f155b7` с одним изменённым байтом `.text` — `VERDICT UNEXPLAINED` (`pediff3s_neg.out.txt`). Сравнение с установленным `b3cee576` классификатором невозможно (размеры файлов разные — другой код) — отказ `assert` (`pediff3_neg_s18.out.txt`), это не контроль. Повторная сборка стенда после мутантов (`git checkout`) — отличие от первой только 2 байта метки линковки (`pediff3s_stand_restore.out.txt`).

## 8. Мутанты (член (е)(1) обязан их ловить)

`mut_f24d.py` меняет только ветку `=1` (якорь — 10 целых строк блока, найден ровно один раз), сборка стенда, прогон `run_stand_f24d.py --mutant` (плечи `=1` как в §6, свободные 10⁵), затем `git checkout` — worktree чист (0 строк).

| мутант | порядок `=1` | пропуски (forced) | член (е)(1) |
|---|---|---|---|
| `g1st` — глобальная первой | `m_cpu_epoch` → т. 11 → `m_epoch` → т. 12 → бит → т. 13 | p11 b0 **10⁵**, p11 b1 **10⁵**, p12 b1 **10⁵**; free p11 20 / 44, p12 b1 52 | **FAIL ⇒ пойман** |
| `bitlast` — бит после глобальной | `m_epoch` → т. 11 → `m_cpu_epoch` → т. 12 → бит → т. 13 | p12 b1 **10⁵**; free p11 b1 1, p12 b1 35, p13 b1 2 | **FAIL ⇒ пойман** |

`bitlast` ловится только плечами `bdabits` 1 — член (е)(1) их содержит; в игре при умолчании гейта `bdabits` (0) порядок бита на решение не влияет (Н5).

## 9. Наблюдения (не RC: сценария отказа нет)

- **Н1 (опись (е)(0)).** Таблица R1–R8 F24c не называет четыре читателя одной эпохи региона (§2: `RsPost`, `ShadowProbe`, `F5IdRangeWriteEpoch`, `CollectCpuModifiedRangesStamped`). Все — измерение или чтение под замком; вывод не меняется. Для будущих правок порядка эпох опись строить своим `git grep` по пяти именам, а не по памяти мест.
- **Н2 (что стенд не доказывает).** Хуки стенда — вызовы внешней функции между атомарными записями, т. е. барьеры компилятора; в эмуляторе их нет. Стенд доказывает порядок программы против модели читателя; отсутствие перестановки компилятором в эмуляторе следует из release-семантики (§3) [c стандарта], машинный код эмулятора я не разбирал.
- **Н3 (п. 601(в)(2)).** `FixB13Enabled()` на каждом `ChangeState<Cpu, true>` после первой инициализации — проверка флага потокобезопасного static (clang-cl: чтение TLS-эпохи и сравнение) и загрузка `bool`; путь — обработчик отказа страницы гостя с `VirtualProtect` в том же вызове. Цена на фоне системного вызова не видна [I]; числа не заявляю.
- **Н4 (п. 601(в)(4)).** Заголовок стенда (`tests/B13EpochStand.cpp`, строка 6) называет `KYTY_B13_TEST_HOOK(point)`, в коде — `KYTY_TEST_B13_HOOK` и `B13Test::Hook(point)`. Комментарий, на сборку не влияет (без определения макроса стенд не собирается — `#error`).
- **Н5 (охват в игре).** При умолчаниях гейтов (`bdastamp` 1, `bdabits` 0) решение в игре определяется порядком «эпоха региона / глобальная»; часть правки «бит до глобальной» действует только при `bdabits` 1. Правка верна в обоих режимах; это граница того, что покажут теги F24e.

## 10. Чек-лист кода (агента Red Team)

- Хронометраж: правка не трогает измеряемых строк. ✓
- Гонки: решение без замка — §3; публикация «один раз» строки лога — `atomic<bool>::exchange`; рваного чтения нет (64-битные атомарные). ✓
- Инварианты `*_bad`: новых нет. ✓
- Ранние возвраты: в изменённом блоке их нет; замок региона держится вызывающим на весь `ChangeState`. ✓
- Правки файлом, LF: в worktree CR 0; патч F24c — `patch_f24c.py`. ✓
- Якоря патча целыми строками — у F24c и у моего мутанта (блок из 10 строк, ровно одно совпадение). ✓
- Кадр стека на потоке гостя: новых локальных массивов нет; `static const bool` — не на стеке. ✓
- Инструмент меняет прогон: `KYTY_FIX_B13` читается `EnvValueOn` — `=0` выключает (не по присутствию); хуки — только под `KYTY_TEST_B13_HOOK`. ✓
- Новые гейты: нет (`gates.cpp` не тронут). ✓

## 11. Не заявляется

Что Б13 `FIXED` (до F24e и F24f); что Б13 проявляется в игре, с какой частотой и видна ли на картинке; что бинарь `91f155b7` или моя сборка работают в игре; что правка меняет картинку или время кадра; что числа стенда — частота в игре; что машинный код эмулятора сохраняет порядок (довод — по стандарту, §3); что путь `armdefer` безопасен при включённом гейте; что реестр полон; ни одно число — не выигрыш; 60 FPS не обещаются.

## 12. Файлы (`docs/track-f/f24d/`)

`mk_wt_f24d.sh`, `build_f24d.cmd`, `mk_wtB.out.txt`, `cherry_repro.out.txt`, `pediff3.py`, `pediff3s_f24d.py`, `pediff3_emu.out.txt`, `pediff3_neg_s18.out.txt`, `pediff3s_emu.out.txt`, `pediff3s_rev.out.txt`, `pediff3s_neg.out.txt`, `pediff3s_stand_restore.out.txt`, `run_stand_f24d.py`, `stand_own.out.txt`, `mut_f24d.py`, `mut_g1st.diff`, `mut_bitlast.diff`, `stand_mut_g1st.out.txt`, `stand_mut_bitlast.out.txt`, `runs/` (56 файлов плеч и сводки), `else_check_f24d.py`, `else_check.out.txt`, `refs_f24d.py`, `refs_f24d.tsv`, `refs_f24d.out.txt`, `refs_f24d_negctl.out.txt`, `version_f24d.txt`, `sha256_f24d.txt`, `times.txt`.
