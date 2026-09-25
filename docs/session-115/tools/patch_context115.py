"""Session 115 close: the game-folder context files CLAUDE.md = AGENTS.md - state, the session-115 entry (the session-111
entry leaves: four sessions kept), the environment variables of session 115; HANDOFF line."""
from pathlib import Path

DIR = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')
src = (DIR / 'CLAUDE.md').read_bytes().decode('utf-8')
crlf = '\r\n' in src
s = src.replace('\r\n', '\n')

a = s.index('**СОСТОЯНИЕ (2026-09-25): ЦИКЛ СЕССИЙ ИДЁТ**')
b = s.index('Дата: 2026-09-25. **Сессия114:')
STATE = """**СОСТОЯНИЕ (2026-09-25, вечер): ЦИКЛ СЕССИЙ ИДЁТ** (пользователь, /loop: сессии подряд, вопросов не задавать; игру
запускать можно; push — нет). **Сессия 115 закрыта** (аудит: вердикт печати подтверждён, MAJOR P1 — прогон `mutlib` рядом
с запечатанной цепочкой), следующая — `docs/next-session-116.md`: `mutlib` v4.1 (безопасный выборочный режим), затем
чистая разбивка фаз и трек скорости. Установлена сборка **`d3a981a2…`** (`7c73f26`: исправление кольца записи
презентации + **`titleasync=1`**); закреплённая копия `C:/kyty/s115/kyty_emulator_d3a981a2.exe`. **Мутанты — `mutlib` v4
(замороженная копия `docs/session-115/mutlib_v4/mutlib.py`, `b666df35`), только ПОЛНЫЕ прогоны `--control --no-memo
--work-dir C:/kyty/s1NN/work*`; `--changed-from` запрещён до v4.1.** Запечатанная цепочка: замок `C:/kyty/SEALED_RUN.lock`,
шлюз `procload.py`, **отказ, пока жив любой процесс с `mutlib.py`; агенты с тяжёлыми задачами останавливаются перед
цепочкой; два тяжёлых задания не одновременно**; состояние цикла — `C:/kyty/LOOP_STATE.md`. Правила с. 106–115 действуют:
решение до действия (и любое изменение запущенного воркфлоу), запечатанное следствие после исхода не отменяется,
фикстуры на каждый член/край, генераторы — якоря целыми строками, главный оценщик ABBA — кадры 10–89 блока, режим BDA —
по счёту `bda_scan`, уровни разных режимов не сравниваются. **Скорость игры = 16 667 / mean `dt_us`. 60 FPS не обещать.**

Дата: 2026-09-25. **Сессия115: ПАДЕНИЕ СТАРТА `commandRecorder.cpp:326` ИСПРАВЛЕНО И ПРОВЕРЕНО ПЕЧАТЬЮ; `titleasync=1`
ОТГРУЖЕН; `mutlib` v3 ПРИНЯТ, v4 — ПОЛНАЯ ПЕЧАТЬ ~20 МИН ВМЕСТО ~70.** Исправление (`503a8bf`): главный поток больше не
презентует в `WindowPrepareShaders` (оверлей подготовки рисует поток `VideoOut`), до главного цикла `UpdateTitle` не ждёт.
Печать 01 `chk115` PASS: загрузка с удержанием 10 с — 607/606 презентаций потоком презентации, 0 главным; контроль с
`KYTY_PREPARE_MAIN_PRESENT=1` падает на `:326`; видео `vid115` 3 894 кадра, 0 глитчей. Долг F2 замерен: мьютекс флипа
2,4 мс на флип, GuestGpu не ждал — не трек скорости. `mutlib`: v3 (дыры корректности) принят, приёмка 3 ч 54 мин
заблокировала сессию (моя ошибка планирования); v4 (5 ускорений: отбор, общие фикстуры, ранний выход, PyPy, профиль) —
полный `ttl114b` 20,3 мин, `net112` 14 мин, вердикты равны; выборочный путь `--changed-from` небезопасен (ревью MAJOR-1) —
запрещён до v4.1; PyPy не быстрее. Источник истины — `C:/kyty/s115/FACTS.md`, в git `docs/local-session-115.md`.

"""
s = s[:a] + STATE + s[b:]

c = s.index('Дата: 2026-09-24. **Сессия111:')
d = s.index('в git `docs/local-session-111.md`.\n\n', c) + len('в git `docs/local-session-111.md`.\n\n')
s = s[:c] + s[d:]

ENV = """- Сто пятнадцатая сессия (**одно отгруженное умолчание — `titleasync` = 1; исправление кольца записи презентации**):
  `WindowPrepareShaders` не презентует с главного потока (оверлей подготовки рисует поток `VideoOut`), до старта главного
  цикла `UpdateTitle` всегда ставит заголовок без ожидания. Строка **`ShaderPreparation: startup wait finished in N ms
  presents_other=P presents_main=M`** (презентации при активном оверлее по потокам). ТОЛЬКО ИЗМЕРЕНИЕ:
  **`KYTY_PREPARE_MAIN_PRESENT=1`** (раз на процесс, строка `PrepareMainPresent: mode 1`) — вернуть старую презентацию
  главного потока, положительный контроль (падение `commandRecorder.cpp:326`); `KYTY_PREPARE_HOLD_MS=<мс>` (с. 114) теперь
  работает без падения. **Нумерация `@present` в `KYTY_KEYS` и кадров `KYTY_REC` сдвинута**: поток `VideoOut` презентует
  экран подготовки до главного цикла. Харнесс `C:/kyty/s115`: `check115.py` (+`make_check115.py` в `s106_stage`, `test_*`,
  `mut_*`), `go115a.sh`, `go115r.sh` (повтор при NOT_ADMITTED), **`procload.py`** (шлюз нагрузки по процессам:
  `--max-rate`, `--max-total`; для замеров времени — 0,5 без суммы), `SEALS115.txt`, `audit115/`. **`mutlib` v4**
  (`C:/kyty/s106_stage/mutlib/mutlib.py`, замороженная `docs/session-115/mutlib_v4/`): новые флаги `--changed-from`
  (ЗАПРЕЩЁН до v4.1), `--no-replay`, `--python`, `--profile-fixtures`, `--cache-dir`; строки отчёта `early exit:`,
  `fixture replay:`. **Ловушки:** `mutlib` без `--work-dir`/`--cache-dir` пишет кеш рядом с собой (в репозиторий);
  `TaskStop` воркфлоу не убивает запущенные агентом цепочки; процессы моих агентов тоже нагрузка для запечатанной цепочки.
"""
e = s.index('- Сто четырнадцатая сессия')
s = s[:e] + ENV + s[e:]

out = s.replace('\n', '\r\n') if crlf else s
for name in ('CLAUDE.md', 'AGENTS.md'):
    (DIR / name).write_bytes(out.encode('utf-8'))

h = DIR / 'HANDOFF.md'
raw = h.read_bytes().decode('utf-8')
nl = '\r\n' if '\r\n' in raw else '\n'
add = ("Дата: 2026-09-25. **Сессия 115 (кратко; источник истины — `docs/local-session-115.md`).** Падение старта "
       "`commandRecorder.cpp:326` при долгой подготовке шейдеров исправлено (главный поток больше не презентует экран "
       "подготовки; его рисует поток `VideoOut`) и проверено печатью `chk115` (удержание 10 с, 607 презентаций потоком "
       "презентации, 0 главным; контроль падает как раньше; видео чистое). `titleasync=1` отгружен. `mutlib` v3 принят, "
       "v4 ускоряет полную печать ×3,5 (~20 мин вместо ~70); выборочный режим — после v4.1. Установлена `d3a981a2…`. "
       "Следующая — `docs/next-session-116.md`. Push не делался.")
raw = raw.rstrip('\r\n') + nl + nl + add + nl
h.write_bytes(raw.encode('utf-8'))
print('ok', len(src), len(out))
