"""F14c (HPP-489): report part (2) into docs/track-f/f14c.md. Whole-line anchors; CR stripped and restored; writes bytes."""
import sys

path = 'C:/kyty/KytyPS5/docs/track-f/f14c.md'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
NL = chr(10)


def rep(old, new):
    global text
    n = text.count(old)
    if n != 1:
        raise SystemExit('anchor count %d: %r' % (n, old[:80]))
    text = text.replace(old, new)


rep('**Часть (2), правка теста Б11 — см. §2.**' + NL,
    '**Часть (2), правка теста Б11 [c]: сделана — KytyPS5 `fcaf141b` (только `tests/shaderCfgTests.cpp`, не под (B)); `shader_cfg_tests` из чистого' + NL
    + 'worktree — 127 тестов, 0 падений (база F14a — 2, Б11); отрицательный контроль — 7 из 7 новых проверок падают. См. §2.**' + NL)

old2 = [
    '**Не сделано в этом хартбите:** сборка `shader_cfg_tests` (> 60 с, полная загрузка CPU) по п. 371(е)(2)/400(з) ждёт закрытия звена прогонов',
    'другого трека — S10 `HPP-433` (Harness Engineer, `in_progress` на 17:50:50Z, 18:15:00Z, 18:18:36Z). Готово: скрипт правки `patch_test_b11.py`',
    '(только `tests/shaderCfgTests.cpp`; проверен сухим прогоном на копии `HEAD` — `test_b11.diff`), скрипты worktree и сборки `mk_wt_f14c.sh`,',
    '`build_f14c.cmd`. Правка: лямбда `compile` получает формат образа 0 (по умолчанию `k8UNorm` фикстуры); пробы 3–4 — `k32Float`, ожидания',
]
new2 = [
    'Сборка ждала закрытия S10 `HPP-433` (п. 371(е)(2)/400(з); `in_progress` на 17:50:50Z, 18:15:00Z, 18:18:36Z, `done` на 2026-10-04T06:54:06Z по API);',
    'F12g `HPP-481` к этому времени уже шёл своим прогоном (первым по п. 400(в)). Перед каждой командой дольше 60 с — проверка API: звеньев Harness',
    'Engineer в `in_progress` нет (строки `times.txt`).',
    '',
    '1. **Worktree [c].** `mk_wt_f14c.sh` на `main` `11b9e913`: чистый (0 строк `git status`), CR в `src/` и `tests/` 0; `patch_test_b11.py` дал',
    '   правку, совпадающую с сухим прогоном `test_b11.diff` строка в строку.',
    '2. **Сборка [c].** `build_f14c.cmd configure` + `tests` (Release, флаги `build_local.cmd`, каталог `C:/kyty/f287/f14c/build`): rc 0;',
    '   предупреждений в новых строках нет. `shader_cfg_tests.exe` sha256 `444fb4cd…`, копия `C:/kyty/f287/f14c/bin/shader_cfg_tests_444fb4cd.exe`.',
    '3. **Набор [c].** `KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1`: 127 тестов (`[test]`), строк `ShaderCfgTests: failed` — 0, rc 0 (`tests_run.log`).',
    '   База F14a (`f14a/suite.log`, тот же набор 127): 2 падения — ровно Б11 (`IMAGE_SAMPLE_C`, `IMAGE_SAMPLE_C_LZ`). Дельта: −2, новых падений 0.',
    '4. **Отрицательный контроль [c].** `patch_ctl_b11.py` поверх правки: обе новые пробы ручного пути с `k32Float` (нативный путь) — бинарь',
    '   `shader_cfg_tests_ctl.exe` (`fd44f034…`), фильтр `PixelImageSampleLodSelection`: падают 7 из 7 новых проверок (`tests_ctl.log`), т. е.',
    '   помощники отличают ручной путь от нативного. Контроль снят (`git checkout` + `patch_test_b11.py`, sha256 файла = `a1b30f2f…` до контроля).',
    '5. **Коммит [c].** Тот же файл перенесён в `main` (blob `d4a573b8` = blob worktree) — KytyPS5 `fcaf141b`, только `tests/shaderCfgTests.cpp`',
    '   (+131/−3); `src/` не менялся. GPU-тест `ComparisonDepthTexture` не тронут.',
    '',
    'Правка: лямбда `compile` получает формат образа 0 (по умолчанию `k8UNorm` фикстуры); пробы 3–4 — `k32Float`, ожидания',
]
rep(NL.join(old2) + NL, NL.join(new2) + NL)

rep('  комментариев в звене не было (18:15:00Z).' + NL,
    '  комментариев в звене не было (18:15:00Z).' + NL
    + '- Часть (2), 2026-10-04 (`date -u` в момент события): возобновление 06:55:10Z; worktree 06:55:25Z; сборка 06:55:33Z–06:57:36Z; набор' + NL
    + '  06:57:48Z (< 1 с); контроль 06:58:19Z–06:58:35Z; возврат и перенос в `main` 06:58:46Z; коммит 06:59:01Z. Замок и `STOP` — 0 срабатываний;' + NL
    + '  новых комментариев в звене 0.' + NL)

rep('  `f14c_table.tsv`, `f14c_summary.txt`, `patch_test_b11.py`, `test_b11.diff`, `mk_wt_f14c.sh`, `build_f14c.cmd`. Только локально' + NL,
    '  `f14c_table.tsv`, `f14c_summary.txt`, `patch_test_b11.py`, `test_b11.diff`, `mk_wt_f14c.sh`, `build_f14c.cmd`, часть (2): `patch_ctl_b11.py`,' + NL
    + '  `tests_run.log`, `tests_ctl.log`, `tests_exe.sha256`. Только локально (`C:/kyty/f287/f14c/`): worktree `wt/`, сборка `build/`, бинари `bin/`,' + NL
    + '  логи сборки `build_*.log`. Также только локально' + NL)

out = text.replace('\n', '\r\n') if crlf else text
open(path, 'wb').write(out.encode('utf-8'))
print('report patched')
