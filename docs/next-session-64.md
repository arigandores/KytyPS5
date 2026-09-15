# Промпт для следующей сессии (сессия 64)

Ты — оркестратор. Пользовательля за компом нету, него
(пустыня, сборки, тесты, ревью), делаешь сам, а зовёшь только для в самом конце сессии для Sky Garden — довести игру до
сцены и отпустить ввод (свип стартует сам: `sky_auto.py`). Цель — **60 FPS в Sky Garden**. Сейчас
30,0 FPS (с `recpin`): CPU потока GuestGpu 31,2–31,6 мс, GPU 14,4–15,4 мс, ~4 840 draw,
6,37–6,44 мкс CPU на draw.

## 0. Что прочитать первым (сам)

`docs/parallel-draw-path.md` §0 (итог сессии 63), §0a (62), §0b (61), §5 (трек C: M2, этапы
C1–C4, жёсткие правила для воркеров); `docs/local-session-63.md` (§2 профиль, §3 сайты);
`docs/local-session-59.md` §6 (числа M2); начало `docs/cpu-hot-path-map.md`; блок сессии 63 в
`CLAUDE.md`/`HANDOFF.md` папки эмулятора.

## 1. Решено измерениями — не переоткрывать

- **Публикация кольца записи закрыта.** `recpin` включён (−2,3…−3,6 %); после него остаток
  ≈1,4 % (`EndRecord` 1,1 % + дренажи 0,3 %) — порог протокола. `recimg`/`recup`/`recpubn` поверх
  `recpin` ниже порога — 0. Общий механизм для остатка прямых записей — потолок 0,7 %, черновик
  `C:/kyty/s63/patch_recgen.py` (гейт `recgen`, 8 сайтов) не применять без нового потолка.
- Сессии 57–62: `progmemo` 1, `rtfast` 1, `dawalk` 0, `armdefer` 0, `dawitptr`/`daqpre` 0, B9,
  загрузки пакетом, свидетель M1 по эпохам, memo копий констант — потолком.
- Профиль после `recpin` (`C:/kyty/s63/prof_sky63a_prof_pin.txt`): `PrepareBindings` 6,5 %,
  `ProtectMappedUnlocked` 4,9 %, `GetGraphicsPrograms` 3,7 %, `ExecutePreparedDraw` 3,7 %,
  `VerifyWitness` 3,6 %, `TryReadBacking` 3,3 %, `CommitBindings` 3,2 %, `AheadTake` 3,1 %,
  спин-лок трекера 2,4 %, `QueueAheadSource` 2,0 % — все статьи с закрытыми потолками.
- Зависание первого входа после сборки: 0 из 3 за сессии 62–63; правило «первый вход
  прогревочный» — предосторожность; при зависании `KYTY_GPU_CHECKPOINTS=1 KYTY_GPU_HANG_ABORT_S=0`.

## 2. Работы сессии

Единственный пункт плана с потолком выше порога — **M2** (`docs/parallel-draw-path.md` §5.3):
разрешение привязок ≈20 % потока (≈6,3 мс из 31,5); при КПД M1 (45 %) ≈3 мс → 33 FPS, при 100 %
→ 37 FPS. Подготовка C1 (приватизация скрэтча: `DrawScratch`, `DescriptorHeap`, `lookup_key`,
атомики, сегмент stream-ring на поток) и C2 (снять `friend class RenderExecutor` с кэша текстур,
явный API `Image`, clock-LRU с атомарным тиком — единственный пункт с собственным выигрышем:
212 тыс. касаний на кадр) дают ≈0 сами по себе и занимают две сессии. **Перед началом — спросить
пользователя**, стоит ли тратить две сессии ради ≈3 мс при бюджете 16,6 мс, или искать другой
рычаг (например, сокращение числа draw/привязок на стороне трансляции PM4, или GPU-сторона:
14,4–15,4 мс GPU тоже близки к бюджету 16,6 мс и станут стеной сразу после CPU).

Если M2: сессия 64 = C1 + C2 с самопроверками (`KYTY_REUSE_BINDINGS=0` — существующий fallback),
замер C2 (clock-LRU) в Sky Garden одним свипом; C3/C4 — следующие сессии.

## 3. Методика

Как в сессиях 57–63: фазы по 500 present, A B A B, три повтора, порог ±1,4 %, решение по полосам
`bands.py`, потолок счётчиком до реализации. Первая база свипа — прогревочная (в `sky63a` она на
3,9 % ниже остальных). Gate-файл: имена, отсутствующие в файле, сохраняют состояние — A/B только
явными `имя=1/0`. Свипы не длиннее ~25 фаз, смотреть `cores`. Семплер на пустыне — явный
`KYTY_SAMPLE_GPU=1`.

## 4. Прогоны и инструменты

Скопировать из `C:/kyty/s63/` в `C:/kyty/s64/` и поменять `root`: `launch_run.py`, `measure_run.py`,
`summary3.py`, `bands.py`, `launch_play.py`, `sky_auto.py`, `sky_sweep.py`, `samples_phase.py`,
`direct_sites.py`, `patchlib.py`, `g.py`. Вход в сцену: `launch_play.py <tag> "drawahead=1
asyncsubmit=1 imgrecycle=1 dathreads=4 …" KYTY_PIPELINE_CACHE=0 KYTY_QUEUE_TRACE=1`, затем
`sky_auto.py <pid> <tag> <phases.json> 500` — свип стартует после 90 кадров ≥ 3 000 draw; после
свипа `_run_stdout.txt` копировать вручную (`launch_play.py` держит файл открытым).

## 5. Правила

Патч-скрипты через `patchlib.py` (`PATCH_DRY=1`; C-строки с `\n` — только файлом через Write);
счётчики — в конец enum `frameStats.h` + `named[]` в `videoOut.cpp`; гейты — `common/gates.*`,
умолчание только по замеру. Сборка `cmd //c "C:\kyty\build_local.cmd"` — не параллельно с
замером; тесты `cmd //c "C:\kyty\s52\build_tests.cmd"` + пять бинарей (+ `memory_tracker_tests`
с `KYTY_ARM_DEFER=1`). Перед коммитом `python C:/kyty/normalize_eol.py`. В конце — коммит без
спроса, push нет; обновить `HANDOFF.md`, `CLAUDE.md`, `AGENTS.md`, отчёт и docs. Игру лишний раз
не запускать; stream-кольцо с CPU не читать (BAR-память).
