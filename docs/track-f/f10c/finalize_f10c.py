"""F10c (HPP-451): copy the link files into docs/track-f/f10c/ (text with LF), the report to docs/track-f/f10c.md, write
SHA256SUMS_f10c.txt (local originals, binary, tool, synthetic modules) and append the FACTS section. ALL OK at the end."""
import hashlib
import os
import sys

SRC = 'C:/kyty/f287/f10c/'
DOCS = 'C:/kyty/KytyPS5/docs/track-f/'
DST = DOCS + 'f10c/'
FACTS = 'C:/kyty/f287/FACTS.md'
FILES = ['patch_f10c.py', 'patch_wt.out.txt', 'patch_main.out.txt', 'commit_msg_code.txt', 'mk_scripts.py', 'mk_wt_f10c.sh',
         'mk_wt.log', 'build_f10c.cmd', 'lockrun.sh', 'gate_order.out.txt', 'cfgtests_defaults.log', 'extract_body_f10c.py',
         'extract_body_f10c.out.txt', 'sval_body_f10c.inc', 'sval_f10c.cpp', 'build_tool_f10c.cmd', 'build_tool_f10c.out.txt',
         'run_f10c.py', 'run_f10c.out.txt', 'f10c_summary.txt', 'f10c_out.tsv', 'finalize_f10c.py']
LOCAL = ['kyty_emulator_36e2b042.exe', 'sval_f10c.exe', 'f10c_list.tsv', 'sval_f10c_r_unset.stdout.txt', 'sval_f10c_r_0.stdout.txt',
         'sval_f10c_r_1.stdout.txt', 'sval_f10c_r_1u0.stdout.txt'] + ['neg/' + f for f in sorted(os.listdir(SRC + 'neg'))]

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
ok = True
os.makedirs(DST, exist_ok=True)
sums = []
for f in FILES + ['f10c.md'] + LOCAL:
    data = open(SRC + f, 'rb').read()
    sums.append('%s  %s' % (hashlib.sha256(data).hexdigest(), f))
for f in FILES:
    data = open(SRC + f, 'rb').read()
    data = data.replace(b'\r\n', b'\n')
    open(DST + f, 'wb').write(data)
    ok &= open(DST + f, 'rb').read() == data
rep = open(SRC + 'f10c.md', 'rb').read().replace(b'\r\n', b'\n')
open(DOCS + 'f10c.md', 'wb').write(rep)
open(DST + 'SHA256SUMS_f10c.txt', 'wb').write(('\n'.join(sums) + '\n').encode('ascii'))
open(SRC + 'SHA256SUMS_f10c.txt', 'wb').write(('\n'.join(sums) + '\n').encode('ascii'))
ok &= hashlib.sha256(open(SRC + 'kyty_emulator_36e2b042.exe', 'rb').read()).hexdigest() == \
    '36e2b0428e36233ab102aab7cdffc00139d45381f59a7bb51cb6967ce49760ce'

section = '''
## F10c (`HPP-451`, Emu Engineer) — код `KYTY_FIX_SVAL` (Ф16) и офлайн-проверка (2026-10-03, UTC)

- 04:56:19Z — старт по п. 369(б), (в)(1). 04:57:29Z — worktree `C:/kyty/f287/f10c/wt` на `main` `465f0d8e` (Б42 `4e72289e` — предок).
  04:57:49Z — патч `patch_f10c.py`, `ALL OK`; `check_gate_order.py` — `GATE ORDER: clean` (= FS3a).
- 04:58:36Z–04:59:44Z — сборка-проверка (sha256 `33ca820b…`), подпись `56189185`. 05:00:00Z — коммит кода **`68602c4f`** на `main`:
  3 файла, +45/−1 (`graphicContext.h:66`, `vulkanWindow.cpp:707`, `pipelineCache.cpp:1343–1384`, `:4664–4666`).
- 05:00:43Z — пересборка worktree на `68602c4f`. Бинарь **`kyty_emulator_36e2b042.exe`**, sha256 `36e2b0428e36233ab102aab7cdffc00139d45381f59a7bb51cb6967ce49760ce`,
  копия в `C:/kyty/f287/f10c/`, не установлен. `KYTY_SHADER_SOURCE_HASH` = `56189185…` — не изменилась.
- 05:02:09Z — `shader_cfg_tests`: 127 тестов, rc 0, = FS3a (кроме `elapsed_ms` строки 64), падение 1 — Б11.
- 05:03:20Z — тело `pipelineCache.cpp:1343–1399` коммита `68602c4f` извлечено байт в байт (sha256 `cd684f6e…`); от F10a отличается
  только ханком F10c. Инструмент `sval_f10c.exe` (sha256 `d7632a2d…`).
- 05:07:06Z–05:08:04Z — `run_f10c.py`, **`ALL OK`, 25 гейтов PASS**:
  - `=0` (переменной нет и `=0`) — S151 REJECT 151; на 778 из 778 модулей вердикт и текст = F10a; строк `FixSvalStat:` 0;
  - `=1`, устройство 1 — S151 ACCEPT 151, C 51 из 51, (к4) 23 из 23, CS 111 из 111;
  - отрицательный контроль: SDK с опцией принимает все 442 модуля D, поэтому контроль синтетический — 2 модуля (`ArrayStride` 4 → 3: в блоке
    StorageBuffer и в самом uniform-блоке); SDK с опцией и встроенная при `=1` отвергают оба;
  - D 442 при `=1` — ACCEPT 442 (счёт, не гейт; = SDK с опцией);
  - `=1`, устройство 0 — S151 REJECT 151 («тогда и только тогда»);
  - `FixSvalStat:` — ровно на проверках 256/512/768, `validated`/`rejected` точны;
  - фикстура `envFlag` 20 из 20; чтение один раз ✓.
- Чужой замок дважды отменил мою команду только для чтения: около 05:10Z (снят к 05:10:26Z) и около 05:19Z (снят к 05:19:36Z). Под замком
  ничего не запускалось и не писалось.
- Отчёт `docs/track-f/f10c.md`, файлы `docs/track-f/f10c/` (`SHA256SUMS_f10c.txt`). Игра не запускалась (WIP по игре — F10e). Процессов после хартбита нет.
- Не заявляется: что пользователь запускает игру с проверкой шейдеров; что выход 321 наблюдался в игре до R0; что 151 — все такие PS игры;
  что SPIR-V корректен для устройства и картинка верна; что в игре будет ≥ 256 проверок; что Ф10 достижим до прогонов F11.
'''
facts = open(FACTS, 'rb').read().decode('utf-8')
if '## F10c (`HPP-451`' not in facts:
    open(FACTS, 'ab').write(section.encode('utf-8'))
ok &= '## F10c (`HPP-451`' in open(FACTS, 'rb').read().decode('utf-8')
print('copied %d files, sums %d lines' % (len(FILES), len(sums)))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
