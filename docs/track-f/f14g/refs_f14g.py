"""Track F link F14g (HPP-507): check of the references of the seal docs/track-f/f14g.md section 0 (general rule 24(1)): every
<commit>:<path>:<line> - the line starts with the anchor and the next line contains the +1 text.  Prints one line per reference and ALL OK.
Run in C:/kyty/KytyPS5.  ASCII output only (the anchors are compared as UTF-8, printed as their sha256 prefix)."""
import hashlib, subprocess, sys

REFS = [
    ('19f7b753', 'docs/ROADMAP.md', 21621, '409. **Звено F14d трека F (`HPP-490`, лид): F14c (`HPP-489`) ПРИНЯТ',
     'ручного сравнения глубины — `magFilter = minFilter = LINEAR`'),
    ('19f7b753', 'docs/ROADMAP.md', 21696, '   (4) **Положительный контроль в игре — снимок бинаря правки при `=1` и структурное чтение**',
     '`docs/track-f/f14c/rd_cmp_f14c.py` офлайн): тег `f19_rd`'),
    ('19f7b753', 'docs/ROADMAP.md', 21703, '   (5) **Прогоны под замком — «нет вреда»** (F14g; бинарь —',
     '`31cbfee8` — sha256 до и после каждого тега'),
    ('19f7b753', 'docs/ROADMAP.md', 22412, '   (д) **F14g (`HPP-507`) — без изменений по существу; поправки к тексту задания:**',
     '(е) **Долги (правило п. 324(и)(5)):**'),
    ('2251af73', 'docs/track-f/f12f.md', 203, '| k03 | +9 | 1 624 | 69 | **3** | `rdsd` |', '| k04 | +12 |'),
    ('2251af73', 'docs/track-f/f12f.md', 40, '**Решение формы (вариант исполнителя рядом с буквой «кадр по `KYTY_RD_LEVEL_FRAME`»):**',
     'уровня `KYTY_RD_LEVEL_FRAME=3,6,9,12,15,18,21,24,27,33,40,50`'),
    ('1c40a04a', 'docs/track-f/f14c/rd_cmp_f14c.py', 1, '# Track F link F14c (HPP-489; ROADMAP s122 item 400(v)(1), member (0) of F14a section 4): '
     'qrenderdoc --python rd_cmp_f14c.py', '# RD_CAP=<capture> RD_OUT=<file>.  NO REPLAY'),
]
ok = True
for c, p, n, a, b in REFS:
    r = subprocess.run(['git', 'show', '%s:%s' % (c, p)], capture_output=True)
    L = r.stdout.decode('utf-8').split('\n')
    good = r.returncode == 0 and len(L) > n and L[n - 1].startswith(a) and b in L[n]
    ok &= good
    print('%s %s:%s:%d anchor %s plus1 %s' % ('OK  ' if good else 'FAIL', c, p, n, hashlib.sha256(a.encode()).hexdigest()[:12],
                                              hashlib.sha256(b.encode()).hexdigest()[:12]))
print('refs %d' % len(REFS))
print('ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
