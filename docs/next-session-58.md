# Промпт для следующей сессии (сессия 58)

Ты — оркестратор. Пользователь за компом есть, но его время дорого: всё, что достижимо без него
(пустыня, сборки, тесты, ревью), делаешь сам, а зовёшь только для Sky Garden — довести игру до сцены
и отпустить ввод. Цель — **60 FPS в Sky Garden**. Сейчас ~27 FPS: CPU потока GuestGpu 33–34 мс,
GPU ~15–16 мс, ~5100 draw.

## 0. Что прочитать первым (сам)

`docs/parallel-draw-path.md` §0 (итог сессии 57), `docs/local-session-57.md`, блок сессии 57 в
`CLAUDE.md`/`HANDOFF.md` папки эмулятора, начало `docs/cpu-hot-path-map.md`.

## 1. Решено измерениями — не переоткрывать

- Окно write-fault'а (`faultkb=64`) — главный выигрыш сессии 57; 4096 КиБ хуже 64.
- «Липкие» страницы (A1) закрыты потолком; `applyskip` поверх A3 — 0.
- Вылет при входе в Sky Garden после смены кэша пайплайнов драйвера — не регрессия кода:
  **при `ErrorDeviceLost` на входе сначала `KYTY_PIPELINE_CACHE=0`**.
- При FPS > 25 рисунок кадров игры меняется — сравнивать по нескольким полосам draw (`bands.py`).

## 2. Работы сессии (по отношению выгода/риск)

1. **`VirtualProtect` 6 %** — объединить защиты `SynchronizeBuffersOfDirtyRanges` в один флаш
   (`protbatch` фаза 2); повтор `faultkb=256` против 64 тремя парами.
2. **Гейты записи A4** (`recbatch`, `recrelax`, `recpin`) — три пары в Sky Garden, решение по умолчанию.
3. **`snapkeep` без полной копии** (`ResourceSnapshot::operator=` 2,5 %): swap на последнем использовании,
   копия только изменившихся векторов.
4. **B9 — dynamic offsets для flattened_srt/shader_data**: потолок измерен (49,5 % наборов повторяют
   предыдущий набор своего layout'а). Сначала счётчик: сколько наборов стали бы переиспользуемыми с учётом
   `maxDescriptorSetStorageBuffersDynamic`.
5. **Memo запроса буфера в `ObtainBuffer`** (E1: медленный путь на каждом draw) — первый шаг M2.
6. Если останется время: B3 (эпоха статического состояния программы), B2b; пакет в подписи кэша
   трансляции (B5, B7, B1d) — только с прогревочным входом пользователем.

## 3. Методика (как в сессии 57)

- Фазы по 600 present, A B A B, решение по разности со средним соседних баз, порог ±1,4 %.
- `summary3.py <tag>` и **`bands.py <tag>`** (несколько полос draw); ядра — отношение сумм, а не медиана
  (`GetProcessTimes` тикает по 15,6 мс).
- Гейты записи мерить без `KYTY_GPU_TIME` (`KYTY_GPU_TIME=unset` в `launch_run.py`).
- Мерить потолок счётчиком до реализации.

## 4. Прогоны и инструменты

Скопировать из `C:/kyty/s57/` в `C:/kyty/s58/` и поменять `root`: `launch_run.py`, `measure_run.py`,
`summary3.py`, `bands.py`, `launch_play.py`, `launch_play_exe.py`, `sky_sweep.py`, `samples_phase.py`,
`patchlib.py`. Sky Garden: `python C:/kyty/s58/launch_play.py <tag> "<гейты>"`, пользователь доводит до
сцены, затем `sky_sweep.py <pid> <tag> <phases.json> 600`.

## 5. Правила

Правки — патч-скриптами через `patchlib.py` (`PATCH_DRY=1`); новые счётчики — в конец enum
`frameStats.h` + строка `named[]` в `videoOut.cpp`; гейты — `common/gates.*`, умолчание только по
замеру. Сборка `cmd //c "C:\kyty\build_local.cmd"`, тесты `cmd //c "C:\kyty\s52\build_tests.cmd"` + пять
бинарей. Перед коммитом `python C:/kyty/normalize_eol.py`. В конце — коммит без спроса, push нет;
обновить `HANDOFF.md`, `CLAUDE.md`, `AGENTS.md`, отчёт и docs. Агентам: анализ → патч-скрипт → ревью;
результаты проверять самому.
