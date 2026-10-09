# FS11b (`HPP-715`, Red Team): ревью бинаря отгрузки FS11 `ea51ae80` — **PASS**

**Вердикт: PASS.** Требуемых изменений кода (RC) нет, звено FS11a2 не нужно. Замечаний без RC — 3 (Н1–Н3, §7); у каждого есть сценарий отказа и владелец.
Бинарь FS11 `ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce` идёт в FS11c без изменений. **Член Н3 п. 647(г): 262 144 региона, прирост
4 194 304 байт (4 МиБ) — меньше 64 МиБ, вопрос лиду не нужен.**

Решение лида — `4801601d:docs/ROADMAP.md` п. 647 (якорь «647. **Звено F29f трека F (`HPP-705`, лид)»), подпункт (д)(2) — FS11b; (д)(1) — члены FS11a; (в) — вывод;
(г) — Н3; (и) — не заявляется; чтение члена «дифф вне `tests/`» — `c4bb0dfa:docs/ROADMAP.md` п. 650(в) (якорь «650. **Звено FS11a трека F (`HPP-714`, Emu Engineer)»);
образец — FS10b п. 624(е)(2), отчёт `docs/track-f/fs10b-review.md`. Вход: отчёт FS11a `984a7f52:docs/track-f/fs11a.md`, код `main` `cb022252`, worktree FS11a HEAD
`ee9632be`; приёмка FS11a лидом — п. 650 (`c4bb0dfa`, 01:03:00Z). Начало работы — 01:03:37Z (после `c4bb0dfa`; снятие блока платформой `issue_blockers_resolved`);
п. 647, 650 и 624(е) (по отчёту FS10b) прочитаны целиком до первой команды проверки. Игра не запускалась; установленный `kyty_emulator.exe` — FS10 `abfded5e…` (звено его
не трогало), `C:/kyty/build/install` и кэши не тронуты. Замка и `C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой). Звено Harness Engineer
`HPP-711` (F30f) было `in_progress` с `executionRunId` (строки `FS11b API check` в `C:/kyty/f287/times.txt`; папка серии `C:/kyty/f287/f30f/runs` была пуста) — все шаги
дольше нескольких секунд (worktree, configure, сборки, стенд) шли под сторожем `watch_fs11b.py` (п. 431(в)(1)); сторож не срабатывал. Время — UTC по `date -u`, события —
строки `FS11b` в `C:/kyty/f287/times.txt`. Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.

## Итог по членам п. 647(д)(2)

| Член | Итог | Чем |
|---|---|---|
| путь `KYTY_FIX_B12=0` на FS11 по коду = база FS10 | ✓ [c] (поведение BDA); отличия вне поведения названы — Н1 | §1.1: при `=0` `BeginBdaPass`/`EndBdaPass` не зовутся, `m_bda_pass_open` = `false` всегда ⇒ `b12_pass` = `false`, все ветки F29c в `SynchronizeBuffersByRegion` мёртвы; FS11 против базы удаляет 0 строк (G5); стенд — 25 плеч `fix_b12=0` в форме `default` воспроизводят потерю (`MEMBERS ALL OK` требует `lost ≥ 1`) |
| путь по умолчанию = путь `=1` бинаря `cabbd818`, принятый F29d (дифф `src/` против `673b780a` — только FS11a) | ✓ [c] | G4: `673b780a..ee9632be -- src/` — один путь `regionManager.h`, изменённые строки = строкам `cb022252` (11/11); контроль `673b780a..eded064e -- src/` пуст; вне `src/` — только `tests/B12BdaStampStand.cpp` (+30/−9, `0db3b3eb`); строка версии в `cabbd818…` — `…-1908-g673b780a`; стенд своей сборки: умолчание = явная `=1` по всем полям 72 плеч |
| дифф FS11 против базы — только (д)(1) (в чтении п. 650(в)) | ✓ [c] | G5: 8 путей = объединению файлов `73a6e411`, `c94c49e0`, `726e751e`, `0db3b3eb`, `cb022252`; +807 / −0; вне `tests/` сверх файлов `c94c49e0`/`726e751e`/FS11a — только `CMakeLists.txt`: один ханк, 11 добавленных строк, удалённых 0, блок `add_executable(b12_bdastamp_stand EXCLUDE_FROM_ALL …)`, `kyty_emulator` не назван; путей `src/graphics/shader/` 0; G3: база + пять диффов `main` = `ee9632be^{tree}` `d5ecdce2…` |
| Ф27, Б13, Б33, Ф10, Ф16, Ф19, Б42, Б4, Ф8, Б24, S-replay, P-var не тронуты | ✓ [c] | G8: 25 коммитов фиксов содержатся в FS11 (предок или `git cherry` `-` — форма FS10b G8; ветки отгрузки несут фиксы cherry-pick'ом); FS11 не удаляет ни одной строки базы (G5) — пересечения файлов (`CMakeLists.txt`; `regionManager.h` у Б13; `videoOut.cpp` у Ф27) — только добавления; `shaderReplay.cpp` базы = FS11 (`KYTY_S_REPLAY` = 3); F30d `585d997d` не предок; `KYTY_DIAG_B32`, `rts_bad_` в диффе 0 |
| своя сборка из чистого worktree и sha | sha **не равен**, причина названа ✓ [c] | §5: свой `4b8252c0…` ≠ `ea51ae80…`; `.text` 0 различающихся байт; 2 228 байт объяснены классами `pediff3r` (каталог сборки 139, метка/GUID 12, `?A0x` 1 435 + строки `?A0x` в `.data` 642); отрицательный контроль — сборка `eded064e` (FS11 без умолчания, та же длина пути) — `UNEXPLAINED`, `.text` 9 901 612 байт; нулевой — `ea51ae80` против себя 0 байт |
| таблица умолчаний | ✓ [c] | §3: ON-IF-UNSET — 16 = 15 FS10b + `KYTY_FIX_B12`, `missing [] extra []`; на `eded064e` и `dc5d4712` — `missing ['KYTY_FIX_B12']`; UNDECIDED — те же 6 имён, что у FS10b |
| член «содержит» | ✓ [c] | G2: отсортированные изменённые строки равны у пяти переносов FS11 (464, 250, 95, 39, 11) и у трёх переносов F29c издания 2 (464, 250, 95); `git cherry ee9632be` — `-` у всех пяти; отрицательные контроли (чужая копия; одна перевёрнутая строка) различают |
| **член Н3 (п. 647(г))** | 262 144 региона; прирост **4 194 304 Б** (6 291 456 → 10 485 760 Б); ≤ 64 МиБ ✓ [c] | §6 |

## 1. Код

### 1.1. Путь `=0` (`ee9632be`)

- **Чтение** — `ee9632be:src/graphics/host_gpu/regionManager.h:70` (якорь «`const char* value = std::getenv("KYTY_FIX_B12");`»; +1 —
  «`return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);`») — форма FS4a `17adaf80` / FS10a; статическая локальная, одно чтение на процесс.
  Читателей ручки — два вызова `FixB12Enabled()` (конструктор `BufferCache`, `RenderContext::PrepareBda`), ручка в `src/` нигде больше не читается [c `git grep`].
- **`=0`:** `PrepareBda` не зовёт `BeginBdaPass`/`EndBdaPass` (`ee9632be:src/graphics/host_gpu/renderer/renderContext.cpp:382`, якорь «`const bool fix_b12 =
  FixB12Enabled();`»; +1 — «`if (fix_b12) {`»). `m_bda_pass_open` пишется только в них ⇒ всегда `false`; `b12_pass` (`ee9632be:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3471`,
  якорь «`const bool b12_pass = m_bda_pass_open;`»; +1 — «`for (auto cursor = scan_begin; cursor < scan_end;) {`») = `false` ⇒ две ветки повторного/позднего визита и
  три записи `walked_pass`/`skipped_pass` не исполняются; остальной код функции — строки базы (дифф удаляет 0 строк). Строк `FixB12Stat:` при `=0` нет (`EndBdaPass` не зовётся).
- Отличия `=0` от базы вне поведения скана — Н1.
- **Откат `KYTY_FIX_B12=0`** — правка вне `src/graphics/shader/**`: подпись трансляции `9177b4267de1fb8bac7d1113afd8733210addfac` у своей сборки (`build/kytyGitVersion.h`) и
  в обоих exe — откат ручкой кэши не холодит [c].

### 1.2. Путь по умолчанию = путь `=1` `cabbd818`

`cabbd818` (`C:/kyty/f287/bin/kyty_emulator_cabbd818.exe`, sha256 `cabbd818397a8a29…`) — сборка worktree F29c издания 2 (HEAD `673b780a` = `dc5d4712` + `8c36ef5c`
(`73a6e411`) + `61be23e1` (`c94c49e0`) + `673b780a` (`726e751e`), G1, G2); строки версии в exe — `…-1908-g673b780a` и `…-1907-g61be23e1` (вторая — `SDL_REVISION`
времени configure, класс 2c `pediff3r`). FS11 = та же база + те же три переноса (строки равны, G2) + `0db3b3eb` (только стенд) + `cb022252`. G4: в `src/` FS11 и `673b780a`
отличаются только строками `cb022252` в `regionManager.h`, которые при не заданной ручке дают то же значение `on` = 1, что `=1` у `cabbd818`. Наблюдаемо — стенд своей
сборки: форма `default` (плечи «1» без переменной) = форма `explicit` (`KYTY_FIX_B12=1`) по всем полям 72 плеч и = выводу FS11a `stand/out_default.txt` [c `stand/cmp.out.txt`].
Машинный код пути `=1` FS11 и `cabbd818` не сравнивался (разные деревья: стенд `0db3b3eb`, строки FS11a) — не заявляется.

## 2. Дифф и история (`review_git_fs11b.py`, вывод `review_git.out.txt`, `ALL OK`)

Своя проверка — во временном индексе (`GIT_INDEX_FILE`); worktree FS11a и скрипты FS11a (`verify_fs11a.py`) не использовались.
- **G1** цепочки: `ee9632be` ← `eded064e` ← `dab16a57` ← `2a371d92` ← `edebaad9` ← `dc5d4712`; `673b780a` ← `61be23e1` ← `8c36ef5c` ← `dc5d4712`. Мой worktree на
  `ee9632be` — `status --short` 0, CR в `src/` 0 из 458 (`mk_wt.log`).
- **G2** «содержит» — см. таблицу.
- **G3** база + пять диффов `main` (`git apply --cached --3way`) = `ee9632be^{tree}` `d5ecdce2…`; без `cb022252` = `eded064e^{tree}` `b6eb5842…` ≠ `ee9632be^{tree}`.
- **G4** — §1.2.
- **G5** — см. таблицу; добавленные строки `CMakeLists.txt` напечатаны в выводе целиком.
- **G8** — см. таблицу; первая форма члена («предок») дала `FAIL` у 16 коммитов `main` (Ф10, Ф16, Б42, Б33, Б4, Ф8, Б24, Ф19 — в ветку отгрузки они пришли cherry-pick'ом,
  как и в FS10); форма заменена на форму FS10b G8 («предок или `git cherry` `-`») до чтения итога (строка `times.txt` 01:13Z) — дефект моего первого скрипта, не FS11.

## 3. Таблица умолчаний (`knobs_fs11b.py`, `knobs_ee9632be.out.txt`, `knobs_eded064e.out.txt`, `knobs_dc5d4712.out.txt`)

ON-IF-UNSET на `ee9632be`: `KYTY_FIX_B12`, `B13`, `B1B`, `B24`, `B26`, `B36`, `B4`, `B42`, `B9A`, `DUALSRC`, `F10`, `F19`, `F8`, `MINIMIZE`, `SVAL`, `KYTY_S_PCW` — 16 =
ожидаемому (`missing [] extra []`). На `eded064e` (до FS11a) и `dc5d4712` — `missing ['KYTY_FIX_B12']` (член различает); на `eded064e` `KYTY_FIX_B12` в UNDECIDED
(`EnvValueOn` без `== nullptr ||`). UNDECIDED на `ee9632be`: `KYTY_AUDIO_SYNC`, `KYTY_DUMP_GCN`, `KYTY_POKE`, `KYTY_PVAR`, `KYTY_S_PCW_FORCE_MS`, `KYTY_S_REPLAY` — как FS10b;
`shaderReplay.cpp` FS11 = базе (`ParseMode`: не задана или `""` → 3).

## 4. Свой стенд (справка, не член п. 647(д)(2))

`b12_bdastamp_stand.exe` своей сборки (`7a940011…`; у FS11a `2116221a…` — другой каталог сборки), раннер — копия `run_stand_fs11a.py` (= `run_f29c3.py` = мой `run_f29d.py`
F29d + плечо B12-9b + форма `default`; `run_stand_fs11a_copy.py`, sha256 в `stand_sha.txt`), 10 000 итераций, под сторожем 01:15:03–01:15:20Z. `default` — `MEMBERS ALL OK`;
`explicit` — `MEMBERS ALL OK`; 72 плеча: 47 `fix_b12=1`, 25 `fix_b12=0`; `default` = `explicit` = FS11a `default` по всем полям [c `stand/cmp.out.txt`].
Плечи `_f1` (`KYTY_FIX_B13=1`, умолчание FS9+) входят в матрицу — сочетание с Б13 покрыто стендом.

## 5. Своя сборка

Worktree `C:/kyty/f287/fs11b/wt` — `git worktree add --detach` на `ee9632be` (`mk_wt_fs11b.sh` — копия `mk_wt_fs10b.sh`). Сборка — свой каталог (длина пути = `fs11a`),
своя конфигурация; флаги — `build_fs11b.cmd` = `build_fs10b.cmd` с путями `fs11b` (Release, clang-cl, LTO). Configure 01:05:00–01:05:51Z, эмулятор 01:05:53–01:06:49Z,
версия и досборка 01:06:55–01:07:02Z.

| файл | sha256 | строка версии в exe |
|---|---|---|
| FS11a `ea51ae80` | `ea51ae80521e8300…` | `KytyPS5-2026-09-15-6a2987a-1910-gee9632be` |
| своя | `4b8252c034c2dcf929e321918fbed3c5e88324dcb89bbe0c52b5a582e3ca8d0e` | та же |
| отрицательный контроль `eded064e` (`C:/kyty/f287/fs11n`, та же длина пути) | `1eb73f3df5e0f911…` | — |

`pediff3r_fs11b.py` = `pediff3r_fs10b.py` с одним изменённым путём; классы названы в FS8b до чтения контроля.

| пара | итог |
|---|---|
| своя против `ea51ae80` (`pediff3r_emu.out.txt`) | 2 228 байт: метка/GUID 12, каталог сборки 139, `?A0x` 1 435, строки `?A0x` в `.data` (класс 2b) 642; `.text` 0; `EXPLAINED` |
| `ea51ae80` против себя (`pediff3r_self.out.txt`) | 0 байт, `EXPLAINED` |
| `eded064e` против своей (`pediff3r_neg.out.txt`) и против `ea51ae80` (`pediff3r_neg_a.out.txt`) | `UNEXPLAINED`, `.text` 9 901 612 байт (смена выражения в инлайновой `FixB12Enabled` под LTO сдвигает раскладку кода) |

## 6. Член Н3 — регионы `m_bda_region_stamps` и прирост памяти

- **Число регионов по коду:** вектор заполняется лениво один раз — `resize(MemoryTracker::RegionCount())` при первом инкрементальном скане
  (`ee9632be:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:3458`, якорь «`m_bda_region_stamps.resize(MemoryTracker::RegionCount());`»; +1 — «`}`»);
  `RegionCount()` = `REGION_COUNT` = `TRACKER_ADDRESS_SIZE / TRACKER_REGION_SIZE` (`ee9632be:src/graphics/host_gpu/memoryTracker.h:411`, якорь
  «`static constexpr size_t REGION_COUNT = TRACKER_ADDRESS_SIZE / TRACKER_REGION_SIZE;`»; +1 — «`inline static thread_local const MemoryTracker* s_upload_owner = nullptr;`»)
  = 2^40 / 4 МиБ (`ee9632be:src/graphics/host_gpu/regionDefinitions.h:13`, якорь «`constexpr uint64_t TRACKER_REGION_SIZE  = 4ull * 1024ull * 1024ull;`»; +1 —
  «`constexpr uint64_t TRACKER_ADDRESS_SIZE = 1ull << 40u;`») = **262 144**. Экземпляр `BufferCache` в эмуляторе один (член `RenderContext`, который создаётся
  `std::make_unique<RenderContext>(graphic_ctx)` в `src/graphics/presentation/window/vulkanWindow.cpp`, одно место [c `grep`]).
- **Размер записи:** `BdaRegionStamp` (`ee9632be:src/graphics/host_gpu/renderer/cache/bufferCache.h:380`, якорь «`struct BdaRegionStamp {`»; +1 —
  «`MemoryTracker::RegionStamp stamp;`») — база: `RegionStamp {const void*, uint64_t}` + `generation` = 24 Б; FS11: + `walked_pass`, `skipped_pass` (`uint64_t`) = 40 Б.
  Проба `h3_size.cpp` (раскладки, переписанные из обоих деревьев, clang-cl x64): `REGION_COUNT 262144 sizeof base 24 fs11 40 bytes base 6291456 fs11 10485760 growth 4194304`
  [c `h3_size.out.txt`; проба повторяет раскладку, а не берёт заголовок — проверяет выравнивание, не код].
- **Прирост: 4 194 304 Б (4 МиБ)**, вектор 6 → 10 МиБ, заполнен нулями при `resize` (страницы закоммичены) [I]. Порог вопроса лиду (> 64 МиБ) не достигнут. Прирост есть **и
  при `=0`** — структура одна для обоих режимов (Н1).

## 7. Замечания без RC

- **Н1 (откат `KYTY_FIX_B12=0`; владелец — лид, FS11c `fs11_z`, FS11d).** Путь `=0` FS11 равен базе по поведению скана BDA [c §1.1], но не по процессу: (а) строка
  `FixB12: mode=0` в логе (у базы строки нет); (б) запись `BdaRegionStamp` 40 Б вместо 24 — +4 МиБ и при `=0`; (в) три счётчика `BdaB12*` вставлены в `enum Counter`
  в середину (индексы 1193–1195), индексы всех счётчиков после `BdaNarrowRace` сдвинуты на 3 — имена в строке кадра те же (таблица `videoOut.cpp` по именам) [c].
  Сценарий отказа: читатель отката, ждущий «`=0` — байт в байт FS10» (память процесса, лог без строки `FixB12:`, сырой дамп счётчиков по номеру), видит отличие и
  объявляет откат неисправным, или, наоборот, считает `=0` полным возвратом памяти. Правка не нужна: полный возврат — только копия `abfded5e` (п. 647(д)(4)); член
  `fs11_z` п. 647(д)(3) (`FixB12: mode=0`, `FixB12Stat:` 0) с этим согласован.
- **Н2 (читатели счётчиков `bda_b12_*`; владелец — Harness Engineer FS11c, лид).** Счётчики `BdaB12Rewalk`/`Rwd`/`Lskip` имеют индексы ≥ `Counter::LogNs` (25) — при гейте
  `FrameStatsLean` они не считаются (`ee9632be:src/common/frameStats.cpp:195`, якорь «`: lean     ? static_cast<uint32_t>(Counter::LogNs)`»; +1 —
  «`: static_cast<uint32_t>(Counter::Count);`») [c кода; включён ли гейт в форме харнесса FS11c — U]. Сценарий отказа: читатель берёт 0 в колонке `bda_b12_rewalk` строки
  кадра за «повторных визитов не было». Правка не нужна: свидетель — строка `FixB12Stat:` (лог, не FrameStats), как в п. 647(д)(3); колонки — только справкой.
- **Н3 (член «содержит» у следующих бинарей отгрузки; владелец — лид и ревьюер следующего бинаря, п. 647(д)(5)).** Фиксы, пришедшие в ветки отгрузки cherry-pick'ом,
  не являются предками FS11 (16 из 25 коммитов G8) — проверка «предок» без `git cherry` даёт ложный `FAIL` (мой первый прогон G8). Правка не нужна: проверять «предок или
  `git cherry` `-`», изменёнными строками или деревом (G2/G3), как в FS10b Н2.

## Чек-лист кода (агент Red Team)

- Хронометрируемых строк правка FS11a не добавляет (чтение — один раз, статическая локальная; инициализация потокобезопасна по C++11).
- Гонки: значение `on` пишется один раз при инициализации статической; `m_bda_pass*` — только под мьютексом рендера `PrepareBda` (как в ревью F29d; код F29c FS11a не трогает).
- Ручка не рвётся внутри операции: одно значение на процесс. Ранние возвраты: лямбда — один выход.
- Новых инвариантов `*_bad` нет. Правка вне `src/graphics/shader/**` — подпись трансляции не меняется (`9177b426…`), каталог варианта прежний; сказано в п. 647.
- Кадр стека: лямбда без локальных буферов. Патч FS11a — LF (CR в `src/` моего worktree 0 из 458).
- Инструмент ревью ничего не меняет в прогоне игры: игра не запускалась; стенд — отдельные процессы своей сборки.

## Ссылки

Ссылки `<коммит>:<путь>:<строка>` этого отчёта проверены скриптом `refs_fs11b.py`: `REFS 9 ALL OK`, отрицательный контроль (сдвиг +1 не совпадает ни у одной) — сработал.

## Ход

- 01:03:37Z старт (проверка замка); 01:03:52Z API (`HPP-711` `in_progress`, серия ещё без тегов); 01:04:41Z папка звена; 01:04:49Z worktree; 01:05:00–01:07:02Z своя сборка;
  01:07:19–01:09:17Z worktree и сборка контроля `eded064e`; `pediff3r`; `review_git_fs11b.py` (две формы G8 — §2); сканер умолчаний; проба Н3; 01:14:47–01:15:20Z стенд;
  строки exe; ссылки; отчёт.

## Файлы

`C:/kyty/f287/fs11b/`, копии в `docs/track-f/fs11b/` (текст — LF): `review_git_fs11b.py`, `review_git.out.txt`, `mk_wt_fs11b.sh`, `mk_wt.log`, `mk_wt_fs11n.sh`, `mk_wt_n.log`,
`build_fs11b.cmd`, `build_fs11n.cmd`, `bstep.sh`, `bstepn.sh`, `api_chk.sh`, `watch_fs11b.py`, `pediff3.py` (копия FS10b), `pediff3r_fs11b.py`, `pediff3r_*.out.txt`,
`sha_fs11b.txt`, `knobs_fs11b.py`, `knobs_*.out.txt`, `strings_fs11b.out.txt`, `h3_size.cpp`, `h3.cmd`, `h3_size.out.txt`, `run_stand_fs11a_copy.py`, `stand_sha.txt`,
`stand/out_default.txt`, `stand/out_explicit.txt`, `stand/cmp.out.txt`, `refs_fs11b.py`, `refs_fs11b.out.txt`, `build_*.log` (кроме логов configure — в них путь профиля
пользователя, только локально), `facts_fs11b.py`, `facts_fs11b.tmpl.md`. Бинари своей сборки и контроля — только локально (`C:/kyty/f287/fs11b/build`, `C:/kyty/f287/fs11n/`).

## Не заявляется

П. 647(и) и п. 650(д) целиком; в частности: что FS11 работает в игре (до FS11c) и что он установлен (до FS11d); что Б12 проявляется в игре, с какой частотой и видно ли это
на картинке; что ветка повторного визита проверена в игре; что путь `=1` FS11 по машинному коду равен пути `cabbd818`; что машинный код пути `=0` равен базе; что откат
`=0` возвращает память базы (не возвращает — Н1); что сборка детерминирована при другом каталоге; что набор тестов полон; что реестр полон; ни одно число — не выигрыш;
60 FPS не обещаются; цель (B) не меняется.
