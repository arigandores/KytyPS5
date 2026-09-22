"""Session 102: update the game context (CLAUDE.md, mirrored byte-identically to AGENTS.md) and HANDOFF.md."""
import pathlib
import shutil

GAME = pathlib.Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')
C = GAME / 'CLAUDE.md'
A = GAME / 'AGENTS.md'
H = GAME / 'HANDOFF.md'
raw = C.read_bytes()
crlf = b'\r\n' in raw
t = raw.decode('utf-8').replace('\r\n', '\n')


def once(s):
    n = t.count(s)
    assert n == 1, (s[:70], n)


# 1. Status block for session 102, above the session-101 decisions.
a1 = '**РЕШЕНИЯ ПОЛЬЗОВАТЕЛЯ ПОСЛЕ СЕССИИ 101 — ЗАПИСАНЫ ДО ПРИМЕНЕНИЯ**'
once(a1)
s102 = '''**ПОСЛЕ СЕССИИ 102: M5 ИЗМЕРЕН И G НЕ ЗАКРЫЛ; ВОПРОС ПО G — ПОЛЬЗОВАТЕЛЮ, ОТВЕТ ЗАПИСАТЬ В ROADMAP ДО
ДЕЙСТВИЯ** (`ROADMAP.md` §5 п. 5): (а) закрыть G по букве правила (BDA-путь нынешнего эмиттера +42 % на
десяти верхних шейдерах, порог +6 %) или (б) держать G живым за предпосылкой перестройки BDA-эмиттера и
перемерить M5′. План — `docs/next-session-103.md` (сначала решение, затем ограничитель циклов BVH вместе с
15 отложенными проверками «наличия» в дереве транслятора). **60 FPS не обещать.**

Дата: 2026-09-23. **Сессия102: M5 ИЗМЕРЕН — BDA-ПУТЬ НЫНЕШНЕГО ЭМИТТЕРА +42 %, НО M5 G НЕ ЗАКРЫВАЕТ
(АУДИТ); ФИКС `KYTY_GPU_CHECKPOINTS` ПРИНЯТ; `dabatch` ЗАКРЫТА НА ПИЛОТЕ.** Стенд без старых захватов
невозможен (транслятор на 13 коммитов новее) — снят свежий захват с новым хост-ключом `KYTY_DMA_LAYOUT=1`
и гейтом `bdaall=1`; варианты — в тестовом рекомпиляторе (`KYTY_RECOMPILE_BDA=1` V2 / `=2` V2s; хэш
транслятора `2db9065a` не тронут, кэш тёплый). Десять верхних шейдеров Sky Garden, пять рук, R = 20,
все контроли PASS, два независимых пересчёта: **X = V2/A = +42,0 %** (ДИ 41,2…42,4), **Y = V2/V2s =
+33,2 %**, **L = V1/A = +2,1 %** (строгая составляющая). Скорер печатал `CLOSE-machinery`; **аудит (5 линз,
2 REFUTED) снял это как лицензию** (`C:/kyty/s102/pred/08_audit_addendum.md`, `ee7e3397…`): дополнение
`pred/02`, сменившее состав вердикта, **не записано в ROADMAP первым — третий раз подряд**, а V2 несёт
неоценённую машинерию (запись в буфер сбоев в каждом PS-варианте — вероятно, теряется ранний тест
глубины; двойное чтение таблицы страниц). **G жив и не лицензирован.** Код: `common/envFlag.h` — 75
проверок «наличия» теперь читают ЗНАЧЕНИЕ (`=0`, `false`, `off`, `no`, пусто — выкл); свидетель
`ckpt102_entry1` 6/6: при `KYTY_GPU_CHECKPOINTS=0` `rec_n` 0 → 11 254, `gpu_busy` 48,8 → 12,5 мс; 15 мест в
`src/graphics/shader/**` отложены. Ручка `dabatch`: цена вызова 0,078 мкс ⇒ экономия 9,5 мкс/флип при 1024
против порога 60 ⇒ закрыта, умолчание 64. Ограничитель BVH не построен. Прогоны: `ckpt102` — зависон
входа, `ckpt102_entry1`, `dab102a`, `m5cap102` — сбой старта `commandRecorder.cpp:326` под `--rd`,
`m5cap102b` — захват. Бинарь **`346ba4f6…`** (23 834 624 Б), установлен. Источник истины —
`C:/kyty/s102/FACTS.md` (читать §9), в git `docs/local-session-102.md`. Ускорения нет. **60 FPS не обещать.**

'''
t = t.replace(a1, s102 + a1)

# 2. Keep four sessions: drop the session-98 paragraph (it is in HANDOFF.md already).
b = t.index('Дата: 2026-09-19. **Сессия 98: МАРШРУТ E, M3 — ЧИСЛО ПОЛУЧЕНО')
e = t.index('**Фиксация после сессии 39 (2026-09-10):**')
assert b < e
t = t[:b] + t[e:]

# 3. The environment-variable list.
a3 = '- Сто первая сессия (**ни одного отгруженного умолчания; один новый гейт — ТОЛЬКО ИЗМЕРЕНИЕ**):'
once(a3)
env = '''- Сто вторая сессия (**одна правка реального пути; ни одного сдвинутого умолчания поведения**):
  **`common/envFlag.h`** — `Common::EnvValueOn(v)` / `EnvFlagOn(name)`: не задано, пусто, `0`, `false`,
  `off`, `no` (регистр не важен, точное совпадение, без обрезки пробелов) = ВЫКЛ, всё прочее = ВКЛ.
  **75 переключателей, проверявшихся по НАЛИЧИЮ, теперь читают ЗНАЧЕНИЕ** (28 файлов): среди них
  `KYTY_GPU_CHECKPOINTS` (при `=0` в логе `Vulkan: GPU checkpoints off (KYTY_GPU_CHECKPOINTS=0)`, `nv` — как
  раньше, только NV), `KYTY_FRAME_TRACE`/`KYTY_AV_TRACE` (`=0` теперь выключает, `lite` — lite),
  `KYTY_GPU_TIME`, `KYTY_SYNC_SUBMIT`, `KYTY_SYNC_DISPATCH`, `KYTY_INDIRECT_DRAW_CPU`, все `*_TRACE`,
  `KYTY_PIPELINE_STATS`, `KYTY_SKIP_TAIL_MIP_STORAGE`, `KYTY_NO_INDIRECT_SANITIZE` (инверсный),
  `KYTY_TRACE_CS`, `KYTY_PRINT_NAMES`. **Правило для бинарей ≥ `346ba4f6…`; на старых `=0` по-прежнему
  ВКЛЮЧАЕТ.** **15 мест в `src/graphics/shader/**` НЕ переведены** (иначе кэш трансляции холодный):
  `KYTY_SRT_VERIFY`, `KYTY_BVH_STUB`, `KYTY_SAMPLE_LOD0`, `KYTY_VTX_TRACE`, `KYTY_CFG_TRACE`,
  `KYTY_VEC_CONST_TRACE`, `KYTY_SCALAR_GROUP_TRACE`, `KYTY_KNOWN_VALUES_TRACE`, `KYTY_SRT_NATIVE_*`,
  `KYTY_SRT_PLAN_STATS`, два `KYTY_AV_TRACE` в `ShaderRecompiler.cpp` — там `=0` всё ещё ВКЛ.
  **Ручка `dabatch`** (`KYTY_DRAW_AHEAD_BATCH`, умолчание **64** = прежняя константа, 0 = один вызов на
  обход): запросов опережения M1 на вызов `PipelineCache::QueueDrawAhead`, читается раз на обход
  (`WalkComputeDispatches`), поэтому может быть плечом расписания; вектор `requests` стал `thread_local`.
  Счётчик **`da_qcall`** (`FrameTrace-x`, сырые штуки) — вызовы `QueueDrawAhead` (≈ 134 на флип при 64).
  **ЗАКРЫТА пилотом `dab102a`**: цена вызова 0,078 мкс. `dabatch` — 36-е имя вне `gates_base.txt`;
  `gates.cpp` даёт 135 записей (111 + 24).
  **`KYTY_DMA_LAYOUT=1`** (хост, ТОЛЬКО ИЗМЕРЕНИЕ, раз на процесс, включается только точным `1`):
  каждой программе в памяти добавляются привязки таблицы страниц BDA и буфера сбоев (46/47 + 51·группа),
  чтобы в захвате RenderDoc любой PS/CS можно было заменить BDA-вариантом; в кэш трансляции не пишется
  (снимается перед записью); лог `DmaLayout: mode 1` и до 64 строк `DmaLayout: inject stage= hash=`.
  **Не для хронометража игры** (две лишние привязки могут перевести конвейер с push-дескрипторов на пул).
  Тестовый рекомпилятор (`shader_cfg_tests.exe`, путь `KYTY_RECOMPILE`): **`KYTY_RECOMPILE_BDA=1`** —
  вариант V2 (read-only буферные и константные загрузки через таблицу страниц BDA, V# во время исполнения,
  границы по `num_records`, по 32 бита); **`=2`** — V2s (та же гранулярность через исходные дескрипторы);
  строки `bda-rewrite:` / `bda-rewrite-detail:` / `recompile-identity: … identical=`;
  `KYTY_RECOMPILE_BDA_TRACE=1` — каждая переведённая загрузка. **Исправлен разбор статического ключа PS
  в `KYTY_RECOMPILE`** (`wave_size` на индексе 2): раньше A пиксельного шейдера НЕ совпадал с модулем игры.
  `enter_scene.py --emu-arg=<флаг>` (писать `--emu-arg=--rd`, не через пробел) — флаги эмулятору.
  Харнесс `C:/kyty/s102`: стенд M5 (`M5_RUNBOOK.md`, `m5_recompile.py`, `m5_sass_full.py`, `rd_m5_find.py`,
  `m5_plan.py`, `rd_m5_equal.py`, `rd_m5_bench.py`, `m5_run.py`, `m5_102.py` + `test_m5_102.py`),
  `ckpt102.py`, `dab102.py`, `accept102.sh`. **Ловушки:** `gates_base.txt` пинит `recordthread=1`, поэтому
  `KYTY_RECORD_THREAD=0` из окружения перекрывается на следующем командном буфере; под `--rd` один раз
  упал старт на `commandRecorder.cpp:326` (не диагностировано); `EventGPUDuration` RenderDoc по событиям
  не аддитивен (30–54 % отсчётов PS равны 0); `nvidia-smi --query-compute-apps` на WDDM показывает `[N/A]`
  у всех — проверка «ничего больше на GPU» по нему не работает.
'''
t = t.replace(a3, env + a3)

out = t.replace('\n', '\r\n') if crlf else t
C.write_bytes(out.encode('utf-8'))
shutil.copyfile(C, A)

# 4. HANDOFF: a short pointer paragraph for sessions 100-102.
h = H.read_bytes()
hcrlf = b'\r\n' in h
add = '''

Дата: 2026-09-23. **Сессии 100–102 (кратко; источники истины — `docs/local-session-100.md`, `-101.md`,
`-102.md`).** С.100: добавка правила M3 измерена, CLOSE первой редакции отозван аудитом, M3 = GAP. С.101:
вычитающая половина M3 измерена на четверть, `KYTY_GPU_CHECKPOINTS=0` оказался ВКЛЮЧАЮЩИМ (проверка
наличия); решения пользователя: M3 — окончательный GAP, M4 снят, A5 = 0,1035. С.102: M5 измерен —
BDA-путь нынешнего эмиттера +42 % на десяти верхних шейдерах Sky Garden (L = +2,1 %), но после аудита M5 G
не закрывает (правило вердикта не записано в ROADMAP первым; неоценённая машинерия V2); `envFlag.h` —
75 переключателей читают значение; `dabatch` закрыта; бинарь `346ba4f6…`; вопрос по G — пользователю.
'''
if hcrlf:
    add = add.replace('\n', '\r\n')
H.write_bytes(h + add.encode('utf-8'))
print('context updated', len(out), 'crlf' if crlf else 'lf')
