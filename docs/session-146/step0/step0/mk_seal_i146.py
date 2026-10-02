"""mk_seal_i146.py - writes C:/kyty/s146/pred/00_i146.md, the seal of the install and warm-up call of session 146 step 0 (HPP-386)
BEFORE the call.  The sha256 lines are computed now from the files.  Writes UTF-8 with LF."""
import hashlib
import os
import subprocess

ROOT = 'C:/kyty/s146'
FILES = ('go146i.sh', 'i146_read.py', 'test_i146.py', 'C:/kyty/f287/fsc/fs_read.py', 'C:/kyty/s142/sc142.py', 'enter_scene.py',
         'launch_run.py', 'run_safety99.py', 'idle142.py', 'procload.py', 'sheet142.py', 'sheetpair_f3d.py', 'shalist_f2c.py',
         'cachemf146.py', 'fgcpu146.py', 'gates_default.txt', 'C:/kyty/scripts/s51_vidglitch.py',
         'C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe', 'C:/kyty/s128/kyty_emulator_9235a7ac.exe', 'C:/kyty/f287/fsc/rec_fs_b.mp4')


def sha(p):
    h = hashlib.sha256()
    with open(p if p.startswith('C:/') else os.path.join(ROOT, p), 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


utc = subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], capture_output=True, text=True).stdout.strip()
L = []
L.append('# Печать 00 шага 0 с. 146 — установка `dac02fb9` и прогрев `i146_v` (`pred/00_i146.md`)')
L.append('')
L.append('Шаг 0 с. 146 (`HPP-386`, Harness Engineer). Записана %s (UTC по `date -u`) ДО вызова `go146i.sh`. Основание — `ROADMAP.md` «СЕССИЯ 122»' % utc)
L.append('п. 300(б)(1)–(3) (установка шагом 0 с. 146: копия, sha256 до и после, закреплённая копия, кэши не трогаются, прогрев V Sky Garden в форме')
L.append('п. 221(г)(3), лист против `fs_b`) и п. 309(л)(1) (провал прогрева — откат копией `C:/kyty/s128/kyty_emulator_9235a7ac.exe` и вопрос лиду);')
L.append('п. 310 прочитан (последний пункт на момент записи — 310, KytyPS5 `23d64824`). Печать серии `sc146` — отдельно, `pred/01_sc146.md`.')
L.append('')
L.append('## Правило прогрева (читает `i146_read.py`; константы — пунктов, исполнитель их не меняет)')
L.append('')
L.append('- Допуск (из `fs_read.py` FSc без изменения): одна попытка; `-lvl underwater_aerial_garden`; бинарь в json = `dac02fb9…`; ни одна `KYTY_FIX_*`,')
L.append('  `KYTY_PIPELINE_PRECACHE`, `KYTY_GPU_CHECKPOINTS` не заданы; `KYTY_GPU_CLOCK_PIN=1`; видео `rec_i146_v.mp4`; `--vulkan-validation false`;')
L.append('  контроль ручки: строка `Shader translation cache:` кончается `variant_fixb26_fixb1b`; событие окна — `WINDOW EVENT`.')
L.append('- Буква п. 221(г)(3), половина V: Σ`dt` после первого кадра сцены ≥ 300 с; ≥ 3 000 показанных кадров после первого кадра сцены;')
L.append('  `s51_vidglitch.py 4 6` — 0 глитчей; 0 маркеров смерти; 0 кадров `dt` ≥ 1 с после первого кадра сцены; лист-пара против `fs_b`')
L.append('  (`sheetpair_i146_v.png`) есть — его просматривает лид (строка приёмки шага 0).')
L.append('- Члены исполнителя [I] (печатаются, вердикт не задают): 0 строк `BvhLoopCapTrip:`; кадров видео ≥ строк после первого кадра сцены − 100;')
L.append('  смены сцены нет; игра жива в конце удержания.')
L.append('- `WARMUP VERDICT i146_v: PASS` и rc 0 `enter_scene.py` — установка остаётся. Иначе — откат внутри замка копией `9235a7ac` с проверкой')
L.append('  sha256 (строка `times.txt`), rc 6, вопрос лиду. Отказ BUSY до старта эмулятора — не попытка: один повтор после ожидания простоя;')
L.append('  второй — откат, rc 4. Кэши не копируются, не возвращаются и не удаляются: манифест трёх кэшей, список `GLCache` и список каталогов')
L.append('  вариантов `PPSA21564` — строками `step0/times.txt` до замка и после прогона.')
L.append('')
L.append('## Вызов (ровно одна строка; другой `PLWAIT` — отказ rc 1)')
L.append('')
L.append('go146i call: PLWAIT=540 bash C:/kyty/s146/go146i.sh install')
L.append('')
L.append('## sha256 (проверяет `i146_read.py --check-seal` перед замком)')
L.append('')
for f in FILES:
    L.append('seal: %s %s' % (sha(f), f))
L.append('')
os.makedirs(ROOT + '/pred', exist_ok=True)
with open(ROOT + '/pred/00_i146.md', 'wb') as f:
    f.write(('\n'.join(L)).encode('utf-8'))
print('pred/00_i146.md written %s sha256 %s' % (utc, sha('pred/00_i146.md')))
