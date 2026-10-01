"""mk_seal_f5c.py - writes the F5c seal C:/kyty/f287/f5c/pred/f5c.md (and a byte copy C:/kyty/f287/pred/f5c.md) with the
verbatim ROADMAP items 273(e), 278(v), 280(e), 285(v) of the KytyPS5 commit given, the sha lines of the sealed files, the call
line.  Prints ASCII only.  usage: python mk_seal_f5c.py <commit> <utc>"""
import hashlib
import os
import re
import subprocess
import sys

COMMIT, UTC = sys.argv[1], sys.argv[2]
ROOT = 'C:/kyty/f287/f5c'
GIT = 'C:/Program Files/Git/cmd/git.exe'
t = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'show', '%s:docs/ROADMAP.md' % COMMIT], capture_output=True).stdout.decode('utf-8')


def item(n):
    m = re.search(r'\n%d\. ' % n, t)
    m2 = re.search(r'\n\d{3}\. ', t[m.start() + 5:])
    return t[m.start() + 1:m.start() + 5 + m2.start()]


def sub(n, letter, nxt):
    s = item(n)
    a = s.index('   (%s) ' % letter)
    b = s.index('   (%s) ' % nxt, a)
    return s[a:b].rstrip('\n')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


e273 = sub(273, 'е', 'ж')
v278 = sub(278, 'в', 'г')
e280 = sub(280, 'е', 'ж')
v285 = sub(285, 'в', 'г')
SEALED = ['go_f5c.sh', 'f5c_read.py', 'test_f5c_read.py', 'test_f5c_read.out.txt', 'win_f5c.py', 'test_go_f5c.py',
          'test_go_f5c.out.txt', 'next_f5c.sh', 'wait_f5c.sh', 'shalist_f2c.py', 'enter_scene.py', 'launch_run.py',
          'run_safety99.py', 'idle142.py', 'procload.py', 'sheet142.py', 'cachemf143.py', 'fgcpu143.py', 'gates_default.txt',
          'C:/kyty/s142/sc142.py', 'C:/kyty/scripts/s51_vidglitch.py', 'C:/kyty/f287/bin/kyty_emulator_6f495a65.exe',
          'C:/kyty/s128/kyty_emulator_9235a7ac.exe']
seal_lines = []
for n in SEALED:
    p = n if n.startswith('C:/') else os.path.join(ROOT, n)
    seal_lines.append('seal: %s %s' % (sha(p), n))
tr = open(os.path.join(ROOT, 'test_f5c_read.out.txt'), 'rb').read().decode('ascii').splitlines()
tg = open(os.path.join(ROOT, 'test_go_f5c.out.txt'), 'rb').read().decode('ascii').splitlines()
Q = '`'
doc = '''# Печать F5c трека F — доказательные прогоны Б37 (`pred/f5c.md`)

Звено F5c (`HPP-357`, Harness Engineer). Запись — {utc} (по `date -u`, команда с проверкой замка и `STOP` в той же строке), ДО первого
прогона. Основание — `ROADMAP.md` «СЕССИЯ 122» **п. 273(е)** (критерий до кода), **п. 278(в)** (окно), **п. 280(е)** (RC3 F5b), **п. 285(в)**
(бинарь `6f495a65`, N1, N2), п. 228(в) (очередь замка), п. 273(к)(2) (форма W); текст пунктов — KytyPS5 `{commit}` (HEAD к моменту печати;
пункты после п. 285 — 286 (FSb), 287 (F6b: «внутри F — F5c и FSc раньше»), 288 (шаг 0 с. 145) — объём F5c не меняют, перечитаны перед печатью).
Без мутантов (описание звена). После печати харнесс, ридер, наборы и все файлы §6 не меняются: `go_f5c.sh` проверяет каждую строку
`seal:` вызовом `f5c_read.py --check-seal pred/f5c.md` перед замком; `<tag>.json` каждого прогона несёт sha256 этой печати (`--pred`).
Путь: `C:/kyty/f287/f5c/pred/f5c.md` (харнесс читает `pred/f5c.md` от своей папки); байт-в-байт копия — `C:/kyty/f287/pred/f5c.md`; sha
обеих — строкой `C:/kyty/f287/times.txt`.

## 1. Критерий — дословно

### п. 273(е) (`{commit}:docs/ROADMAP.md`)

{e273}

### п. 278(в)

{v278}

### п. 280(е)

{e280}

### п. 285(в)

{v285}

## 2. Прогоны

Бинарь правки — `C:/kyty/f287/bin/kyty_emulator_6f495a65.exe` (sha256 `6f495a65388a90a0381c9170f224777e84cb07d657115ad2a8662fa0bae168dd`;
сверено исполнителем {utc} — равно п. 285(б)); до замка и установки — строки подписи трансляции `699c1e4b…`, `SwapchainZeroExtent: begin`,
`TestMinimize: armed` в бинаре. Установленная `9235a7ac` (закреплённая копия `C:/kyty/s128/kyty_emulator_9235a7ac.exe`) заменяется бинарём
правки один раз внутри замка и возвращается в ловушке выхода той же команды вместе с `_ShaderCache/PPSA21564` (перенос кэша прогона в
`cache_run/<UTC>/`, копия снимка назад, список содержимого = списку до серии) и `GLCache` (`GLRESTORE=1`); несовпадение — rc 1 и
`C:/kyty/f287/STOP`. Списки кэшей до и после, sha — строками `times.txt` (п. 228(в)).

**Одна серия, один замок, одна попытка на тег, порядок (а) → (б) → (в) → (г)** (вариант исполнителя: (а) — главный член; (б) останавливает
эмулятор и пишет только свой лог; (г) с неизвестным исходом — последним). Каждый тег: `-lvl underwater_aerial_garden`, стенд
`KYTY_TEST_MINIMIZE=60:10`, позиционно `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`, `--attempts 1 --no-install --require-idle --stable-draws 300`,
`KYTY_GPU_CHECKPOINTS` не передаётся; `KYTY_FIX_DUALSRC`, `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_S_PCW`, `KYTY_PVAR` не передаются (бинарь
`4fc501f4` + F5 их не читает).

| тег | член | окружение | удержание харнесса | буква удержания |
|---|---|---|---|---|
| `f5c_a` | (а) W | `KYTY_FIX_MINIMIZE=1`, `--vulkan-validation true`, `KYTY_PIPELINE_PRECACHE=0`, `VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin`, `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000`, `VK_LAYER_MESSAGE_ID_FILTER=Undefined-Value-ShaderOutputNotConsumed-DynamicRendering` (идентификатор шага 0 с. 145, п. 288 — подтверждён лидом), без видео | `--hold 310 --timeout 600` | Σ `dt_us` после первого кадра сцены ≥ 310 с |
| `f5c_b` | (б) контроль | то же, `KYTY_FIX_MINIMIZE=0` | `--hold 310 --timeout 600` (эмулятор останавливается сам) | — |
| `f5c_v` | (в) V | `KYTY_FIX_MINIMIZE=1`, без валидации, precache по умолчанию, видео `KYTY_REC` (`--rec`) | `--hold 330 --timeout 480` | Σ `dt_us` после первого кадра сцены ≥ 330 с |
| `f5c_g` | (г) V | `KYTY_FIX_MINIMIZE=0`, без валидации, без видео | `--hold 330 --timeout 480` | — (данные) |

Перед каждым тегом — ожидание простоя `idle142` до 300 с (шаг 15 с) и один повтор отказа BUSY до старта эмулятора (не попытка), как F4c.
После (в) — `s51_vidglitch.py rec_f5c_v.mp4 4 6`, `sheet142.py` → `sheet_f5c_v.png`; sha видео, `.idx`, листа и вывода детектора — строками
`times.txt`.

**Окно замка** (`win_f5c.py`, ответ API — строкой `times.txt` перед замком): `HPP-367`, `HPP-342`, `HPP-337` — `done` без идущего прогона;
`HPP-350` (шаг 0 с. 145), `HPP-352` (серия с. 145), `HPP-364` (P17), `HPP-370` (FSc) — не `todo`/`in_progress` и без идущего прогона
(вариант исполнителя: очередь сессия > P > F > S п. 228(в); уступка идущему `HPP-350` — п. 288(е) считает записи звена сессии под замком
трека F нарушением звена; цена — звено сессии без замка, начавшееся после взятия замка F5c, ждёт ≤ 35 мин). Шлюз `procload` + имена
процессов, CPU < 15, `idle142` — перед замком (как F4c).

## 3. Правило чтения (`f5c_read.py`, sha256 в §6)

Разбор `sc142.py` (sha256 сверяется) не копируется и не меняется; порядок: `NOT ADMITTED` (форма прогона) → `NOT EVALUABLE` (контроли
стенда и плеча) → буква.

**Допуск:** одна попытка; `binary_sha256` = `6f495a65…`; `-lvl underwater_aerial_garden`; `KYTY_FIX_MINIMIZE` = значение тега; `KYTY_TEST_MINIMIZE=60:10`;
посторонние ручки (§2) и `KYTY_GPU_CHECKPOINTS` отсутствуют; `KYTY_GPU_CLOCK_PIN=1`; W — `KYTY_PIPELINE_PRECACHE=0`, фильтр ровно равен
идентификатору, `--vulkan-validation true`, слой активен (п. 224); V — без `KYTY_PIPELINE_PRECACHE` и без фильтра, `--vulkan-validation false`;
видео только у (в).

**Контроли (провал — `NOT EVALUABLE`, вопрос лиду):** ровно одна строка `TestMinimize: config on delay_s=60.000 dur_s=10.000`; ровно одна
`TestMinimize: armed`; **N2 (п. 285(в)):** строка `GuestOut: Level has started:` перед `armed` несёт имя `underwater_aerial_garden` (не пустое) —
опора отсчёта и окон — строка `armed` лога своего тега; сдвиг `armed` против строки входа (байты, строки `FrameTrace`, с по Σ`dt`) и число пустых
строк входа до неё — печатаются (п. 280(в)); ровно одна `TestMinimize: minimize` после `armed`; (а), (в) — ровно одна `TestMinimize: restore`
после `minimize` ((б), (г) — число печатается, процесс может кончиться в эпизоде); строк `FixMinimize: on` — 1 при `=1`, 0 при `=0`; ≥ 1 строки
`Window 1 minimized`; первый кадр сцены (п. 221(в): `draws` ≥ 100 после строки входа) раньше `minimize`; при `=0` — нет строк `SwapchainZeroExtent:`.

**Часы.** Часы лога — Σ`dt_us` строк `FrameTrace` до позиции строки (часы всех удержаний и K2 программы). Окно п. 278(в) в логе — от строки
`TestMinimize: minimize` до первой строки `FrameTrace`, кончающейся ≥ 2 с после строки `SwapchainZeroExtent: end`; без `end` — до конца лога.
«`end` позже `restore` + 2 с» — по часам лога (буква); рядом — **вариант исполнителя** по полю `ms=` строки `end`: (begin − minimize) + `ms` >
(10 + 2) с; расхождение прочтений печатается строкой «THE TWO READINGS DIFFER» — вопрос лиду, буква — часы лога. Окно на видео — часы лога,
положенные на часы `.idx` якорем концов (метод `docs/session-144/audit/vidcont144.py`); рядом — **вариант исполнителя** «наибольший разрыв `.idx`
+ 2 с»; число глитчей вне окна печатается при обоих, расхождение — вопрос лиду, буква — якорное окно.

**Буква.**
- (а) `f5c_a` **PASS**, если все: вошёл; без смены сцены; эмулятор жив до конца удержания; ровно одна строка `Window 1 minimized`; строки
  `SwapchainZeroExtent: begin` и `end` (первая `end` после `begin`); 0 `[Vulkan][E]` (лог + stdout); 0 маркеров смерти (`sc142.markers`);
  Σ`dt` после первого кадра сцены ≥ 310 с; ≥ 1 000 строк `FrameTrace` после `TestMinimize: restore`; `end` не позже `restore` + 2 с; иначе **FAIL**.
  Член исполнителя [I] (не вердикт): ровно одна `begin` и одна `end`.
- (б) `f5c_b` **STOP VUID-01689**, если строка `[Vulkan][E]` с `VUID-VkSwapchainCreateInfoKHR-imageExtent-01689` стоит после `TestMinimize: minimize`
  и эмулятор кончился (`hold_exit` задан или исход `exited`); иначе **NO STOP** (член (б) не выполнен).
- (в) `f5c_v` **PASS**, если все: вошёл; без смены сцены; жив до конца удержания; Σ`dt` ≥ 330 с; видео ≥ 3 000 кадров; лист есть; 0 глитчей
  `s51_vidglitch.py 4 6` вне окна п. 278(в); **N1 (п. 280(е)(1), п. 285(в)):** номера present в `.idx` в записях с временем ≥ времени строки `end`
  строго растут (перестановка или повтор — глитч; число записей после `end` > 0); без K1 (маркеры смерти) и K2 (кадр ≥ 1 с после первого кадра
  сцены) вне окна (маркеры stdout позиции в логе не имеют — считаются вне окна); строки `begin`/`end` и `end` не позже `restore` + 2 с (п. 278(в));
  иначе **FAIL**. Данные рядом (не гейт): нарушения порядка present по всему файлу, последовательность номеров записей, кадры без записи вне
  окна методом `vidcont144` (Б38). `frames_dropped` с видео не сравнивается (п. 280(е)(3)). Лист — для лида; вердикт «лист просмотрен» — F5d.
- (г) `f5c_g` **DATA**: маркеры смерти (вид, класс, источник), последняя строка лога и stdout, код выхода (`hold_exit` / `detail`), строки
  `Recovering Vulkan swapchain`, `retry exhausted`, `[Vulkan][E]`, удержание — класс Б37 по п. 273(е)(3)(г) решает F5d.

Строки событий окна (`Window 1 minimized`, `Recovering Vulkan swapchain`, `restored`, `resized`, `size changed`, `lost keyboard focus`) печатаются
счётом и серию не останавливают (п. 280(е)(2)). Строки лимита слоя («last time reporting it») — счёт, данные.

**Остановка серии** (`f5c_read.py --stop-check` после каждого тега): тег не допущен или без лога; `NOT EVALUABLE`; в (а) или (в) маркер смерти
без строки `[Vulkan][E]` (первое воспроизведение K1/K2 — вопрос лиду). FAIL букв, NO STOP (б), DATA (г) — данные, серия идёт. Стоп-файл
`C:/kyty/f287/STOP` — перед замком и перед каждым тегом.

## 4. Вызов (п. 105(в))

Одна строка вызова; `next_f5c.sh` проверяет `STOP` и замок, пишет строку `times.txt` и запускает её отсоединённо, ожидание — `wait_f5c.sh`
на переднем плане (< 600 с на вызов, повтор до `DONE`):

go_f5c call: PLWAIT=540 bash C:/kyty/f287/f5c/go_f5c.sh series

## 5. Проверки до печати

- `test_f5c_read.py`: {tr_first}; {tr_n}; `{tr_last}` (вывод `test_f5c_read.out.txt`, sha256 в §6).
- `test_go_f5c.py`: {tg_first}; {tg_n}; `{tg_last}` (вывод `test_go_f5c.out.txt`, sha256 в §6).
- Мутантов нет (описание звена). Приватность коммита — `git grep -P -f C:/kyty/scrub/checks.txt` (п. 285(д)).

**Вопросы лиду (до ответа — по букве и вариантам выше):** (1) окно замка уступает идущему `HPP-350`, но не `HPP-351` (отзыв шага 0 с. 145) — так ли;
(2) часы «`end` позже `restore` + 2 с» — Σ`dt` лога, вариант `ms=` рядом; (3) окно видео — якорь концов, вариант «разрыв `.idx`» рядом; (4) N1 — записи с
временем ≥ `end` на якорных часах.

**Не заявляется:** что без правки свёрнутое окно ведёт к крэшу или не ведёт (это — тег (г)); что правка снимает остановку под валидацией до
прочтения (а); что видео после эпизода непрерывно без строки N1; что какая-либо сцена корректна или проходима до конца; ни одно число — не
выигрыш; 60 FPS не обещаются.

## 6. Печать файлов

{seals}
'''.format(utc=UTC, commit=COMMIT, e273=e273, v278=v278, e280=e280, v285=v285, tr_first=Q + tr[0][:60] + '…' + Q,
           tr_n=tr[-2], tr_last=tr[-1], tg_first=Q + tg[0][:60] + '…' + Q, tg_n=tg[-2], tg_last=tg[-1],
           seals='\n'.join(seal_lines))
os.makedirs(os.path.join(ROOT, 'pred'), exist_ok=True)
for p in (os.path.join(ROOT, 'pred', 'f5c.md'), 'C:/kyty/f287/pred/f5c.md'):
    with open(p, 'wb') as f:
        f.write(doc.encode('utf-8'))
print('seal written sha256 %s lines %d seal lines %d' % (sha(os.path.join(ROOT, 'pred', 'f5c.md')), doc.count('\n'), len(seal_lines)))
