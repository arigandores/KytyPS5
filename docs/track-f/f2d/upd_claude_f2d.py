# F2d: status line of track F in CLAUDE.md == AGENTS.md (ps5-em)
import hashlib
OLD = ('Б1б → K3, F3 = Б1б; звенья `HPP-307` F2a (Emu Engineer), `HPP-308` F3a проект Б1б (Lever Researcher), `HPP-309` F2b (Red Team), '
       '`HPP-310` F2c (Harness Engineer), `HPP-311` F2d приёмка; ')
NEW = ('**F2 и F3a приняты (п. 259, `f8396bed`): Б26б `FIXED`** (счёт трека F, не отгрузка под (B); правило п. 256(а) 5 из 5, буква 4 из 5; '
       'Б26а переоткрытий 0); установка — одним бинарём отгрузки трека F с F3/F4 после аудита с. 144; новые строки Б26в, Б26г, Ф9, Ф10 (реестр §11); '
       '**F3 = Б1б + Ф9** — `IMAGE_BVH_INTERSECT_RAY` читает узлы по `адрес >> 8` (база дескриптора без сдвига 8, [c] кодом, PAL и кодом игры), '
       'критерий п. 259(е) под `KYTY_FIX_B1B`; звенья `HPP-340` F3b (Emu Engineer) → `HPP-341` F3c (Red Team) → `HPP-342` F3d (Harness Engineer, '
       'после `HPP-333`) → `HPP-343` F3e (лид); ')
OLD2 = '`HPP-287` — `blocked` на `HPP-311` и `HPP-338`'
NEW2 = '`HPP-287` — `blocked` на `HPP-343` и `HPP-338`'
for n in ('CLAUDE.md', 'AGENTS.md'):
    p = 'C:/kyty/KytyPS5/ps5 em/' + n
    b = open(p, 'rb').read()
    crlf = b'\r\n' in b
    s = b.decode('utf-8').replace('\r\n', '\n')
    assert s.count(OLD) == 1, (n, 'OLD')
    assert s.count(OLD2) == 1, (n, 'OLD2')
    s = s.replace(OLD, NEW).replace(OLD2, NEW2)
    if crlf:
        s = s.replace('\n', '\r\n')
    open(p, 'wb').write(s.encode('utf-8'))
    print(n, hashlib.sha256(s.encode('utf-8')).hexdigest()[:16], 'crlf' if crlf else 'lf')
