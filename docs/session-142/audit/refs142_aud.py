# refs142_aud.py - pinned reference map of AUDIT142.md (general rule 24(1)): <commit>:<path>:<line> + anchor; control +1 must be NOT OK
import subprocess, sys
REFS = [
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 11746, '221. **Закрытие с. 141'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 11810, 'замком `C:/kyty/SEALED_RUN.lock` через `procload.py`, по одному, без параллельной работы'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 11842, '222. **Закрытие с. 141 — факт исполнения'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 11849, 'sha256 файлов инструкций (п. 221(ж))'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 11862, '223. **Приёмка шага 0 с. 142'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 11899, '224. **Приёмка шага 1 с. 142'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 11955, '(в) **Второго отзыва Red Team нет**'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 11965, '225. **Приёмка звена 1б с. 142'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 11991, '226. **Трек P'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 12002, 'замок `C:/kyty/SEALED_RUN.lock`; звенья P с игрой идут только после `done` `HPP-279`'),
    ('C:/kyty/KytyPS5', 'd700ee60', 'docs/ROADMAP.md', 12003, 'P (реверс `C:/kyty/eboot.elf`'),
    ('C:/kyty/KytyPS5/ps5 em', 'f1c3339', 'docs/agent-team.md', 34, '**Запечатанный прогон эксклюзивен.**'),
    ('C:/kyty/KytyPS5/ps5 em', 'f1c3339', 'docs/agent-team.md', 35, 'Никакой параллельной работы агентов во время прогона.'),
    ('C:/kyty/KytyPS5/ps5 em', 'f1c3339', 'docs/agent-team.md', 123, '21. **Перед записью, коммитом, сборкой, тестом и прогоном мутантов первая строка команды'),
    ('C:/kyty/KytyPS5/ps5 em', 'f1c3339', 'docs/agent-team.md', 143, '26. **Стоп звену'),
    ('C:/kyty/KytyPS5/ps5 em', 'f1c3339', 'docs/agent-team.md', 182, '**Замок (п. 25(ж)):** пока есть `C:/kyty/SEALED_RUN.lock`, ни один ран'),
    ('C:/kyty/KytyPS5/ps5 em', 'f1c3339', 'docs/agent-team.md', 239, 'либо ставится **настоящий монитор**'),
    ('C:/kyty/KytyPS5/ps5 em', 'f1c3339', 'CLAUDE.md', 248, '(5) прогон и скоринг — на переднем плане, ждать внешнее — только'),
    ('C:/kyty/KytyPS5/ps5 em', 'f1c3339', 'docs/platform-traps.md', 32, 'настоящим монитором (`executionPolicy.monitor`'),
]
ok_all = True
for root, rev, path, line, anchor in REFS:
    txt = subprocess.run(['git', '-C', root, 'show', '%s:%s' % (rev, path)], capture_output=True).stdout.decode('utf-8').split('\n')
    a = anchor in txt[line - 1]
    b = anchor in txt[line] if line < len(txt) else False
    ok_all &= a and not b
    print('%s:%s:%d anchor %s; control +1 %s' % (rev, path, line, 'OK' if a else 'MISSING', 'NOT OK' if not b else 'OK (bad control)'))
print('refs %d, %s' % (len(REFS), 'ALL OK' if ok_all else 'FAIL'))
sys.exit(0 if ok_all else 1)
