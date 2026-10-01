"""Appends the F5c times lines and the FACTS section (stage 1: harness and seal) - run in a command that checks the lock first."""
import hashlib
import os
import subprocess
import sys

NOW = sys.argv[1]
WIN = sys.argv[2]
R = 'C:/kyty/f287/f5c'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def mt(p):
    import datetime
    return datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


names = ['f5c_read.py', 'test_f5c_read.py', 'test_f5c_read.out.txt', 'go_f5c.sh', 'win_f5c.py', 'next_f5c.sh', 'wait_f5c.sh',
         'test_go_f5c.py', 'test_go_f5c.out.txt', 'mk_seal_f5c.py', 'pred/f5c.md', 'enter_scene.py']
T = []
T.append('%s F5c (HPP-357, Harness Engineer): wake on lead comment a1549b19 (p.285(v), KytyPS5 44ed7663); lock no, STOP no; '
         'blockers HPP-342/356/367 done (API 14:52Z); binary C:/kyty/f287/bin/kyty_emulator_6f495a65.exe sha256 '
         '6f495a65388a90a0381c9170f224777e84cb07d657115ad2a8662fa0bae168dd = p.285(b) (own sha256sum 14:52:17Z by date -u of that command)' % NOW)
for n in names:
    T.append('%s F5c file %s sha256 %s (event: written, mtime %s)' % (NOW, n, sha(os.path.join(R, n)), mt(os.path.join(R, n))))
T.append('%s F5c suites: test_f5c_read.py 69 checks ALL OK (out sha256 %s); test_go_f5c.py 65 checks ALL OK (out sha256 %s)' % (
    NOW, sha(R + '/test_f5c_read.out.txt'), sha(R + '/test_go_f5c.out.txt')))
T.append('%s F5c seal pred/f5c.md sha256 %s = copy C:/kyty/f287/pred/f5c.md sha256 %s (event: written %s); check-seal OK; DRY rc 0' % (
    NOW, sha(R + '/pred/f5c.md'), sha('C:/kyty/f287/pred/f5c.md'), mt(R + '/pred/f5c.md')))
T.append('%s F5c lock window: %s' % (NOW, WIN))
T.append('%s F5c process note: f5c_read.py and test_f5c_read.py written by the Write tool directly into f5c/ (14:58-15:01Z by mtime) '
         'without a lock check in the same command (lock absent at 14:55:47Z and 15:02Z checks); later files via scratch + copy under a lock check' % NOW)
open('C:/kyty/f287/times.txt', 'a', encoding='utf-8').write('\n'.join(T) + '\n')
F = '''
## F5c (`HPP-357`, Harness Engineer), этап 1 — харнесс и печать, {now}: прогонов нет, окно замка закрыто

- Вход: комментарий лида `a1549b19` — п. 285(в) (KytyPS5 `44ed7663`): F5b2 PASS, бинарь F5c `6f495a65`, в печать N2 и N1, приватность —
  `git grep -P -f C:/kyty/scrub/checks.txt`. Блокеры `HPP-342`, `HPP-356`, `HPP-367` — `done` (API 14:52Z). Бинарь
  `C:/kyty/f287/bin/kyty_emulator_6f495a65.exe` — sha256 `6f495a65388a90a0381c9170f224777e84cb07d657115ad2a8662fa0bae168dd` своей сверкой = п. 285(б).
- Харнесс `C:/kyty/f287/f5c/`: `go_f5c.sh` (порт `go_f4c2.sh`: один замок на 4 тега, копия и возврат `_ShaderCache`/`GLCache`/`9235a7ac` в ловушке
  выхода, ожидание простоя и один повтор отказа BUSY), `win_f5c.py` (окно замка), `f5c_read.py` (ридер букв п. 273(е)(3)(а)–(г), окно п. 278(в),
  RC3 п. 280(е), N1/N2 п. 285(в)), `next_f5c.sh`/`wait_f5c.sh`, `enter_scene.py` (файл с. 143 с корнем `f287/f5c`), инструменты F4c без правки.
- Наборы: `test_f5c_read.py` — 69 проверок `ALL OK` (вывод `test_f5c_read.out.txt` sha256 `{tr}`); `test_go_f5c.py` — 65 проверок `ALL OK`
  (вывод `test_go_f5c.out.txt` sha256 `{tg}`). Мутантов нет (описание звена).
- Печать `pred/f5c.md` sha256 `{seal}` (копия `C:/kyty/f287/pred/f5c.md` равна): п. 273(е), 278(в), 280(е), 285(в) дословно (`9bfb26bc`), строка вызова
  `go_f5c call: PLWAIT=540 bash C:/kyty/f287/f5c/go_f5c.sh series`, 23 строки `seal:`; `--check-seal` OK, DRY rc 0. Порядок (а) → (б) → (в) → (г).
- Варианты исполнителя (печать §2–§3, вопросы лиду §5): окно замка уступает идущим `HPP-350`, `HPP-352`, `HPP-364`, `HPP-370`; «`end` позже
  `restore` + 2 с» — Σ`dt` лога, рядом `ms=`; окно видео — якорь концов `.idx`, рядом «наибольший разрыв»; N1 — записи `.idx` с временем ≥ `end`.
- Окно замка {now}: `{win}`.
- Процесс: `f5c_read.py` и `test_f5c_read.py` записаны инструментом Write прямо в `f5c/` без проверки замка в той же команде (замка не было при
  проверках 14:55:47Z и 15:02Z) — нарушение общего правила 27 по букве, названо; дальше — запись в рабочую папку прогона и копия командой с
  проверкой замка.
- Следующее действие: `bash C:/kyty/f287/f5c/next_f5c.sh` при открытом окне (после `HPP-350` и `HPP-370`), затем `wait_f5c.sh` до `DONE`; таблица
  исходов — этап 2 этого раздела.
'''.format(now=NOW, tr=sha(R + '/test_f5c_read.out.txt'), tg=sha(R + '/test_go_f5c.out.txt'), seal=sha(R + '/pred/f5c.md'), win=WIN)
open('C:/kyty/f287/FACTS.md', 'a', encoding='utf-8').write(F)
print('ok %d times lines' % len(T))
