"""F44c (HPP-793): generator of refs_f44c.py - finds each anchor line (unique) at the commit and its +1 control, writes refs_f44c.py
(ASCII, \\u escapes).  usage: python gen_refs_f44c.py <roadmap commit> <out refs_f44c.py>"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
RC = sys.argv[1]
OUT = sys.argv[2]
FM = 'src/graphics/host_gpu/renderer/cache/faultManager.cpp'
SPEC = [
    (RC, 'docs/ROADMAP.md', '698. **Звено F43b трека F (`HPP-784`, лид; приёмка F43a `HPP-783`)', '(а) **Приёмка строкой. F43a ✓**'),
    (RC, 'docs/ROADMAP.md', '(4) **Тег под замком — «нет вреда»** (F44c;', '**Чтение:** (1)–(4) все ✓ — **Ф29 `FIXED`**'),
    (RC, 'docs/ROADMAP.md', '(м) **Не заявляется:** что проход с ≥ 1 024 битами бывает в игре', ''),
    (RC, 'docs/ROADMAP.md', '701. **Звено F44a трека F (`HPP-791`, Emu Engineer)', '(а) **Приёмка строкой. F44a ✓.**'),
    (RC, 'docs/ROADMAP.md', '707. **Звено F44b трека F (`HPP-792`, Red Team)', '(а) **Приёмка строкой. F44b ✓.**'),
    (RC, 'docs/ROADMAP.md', '(в) **Звенья.** F44b `HPP-792` — approve', '(г) **Не заявляется:** что Ф29 исправлен'),
    ('15c9d2f2', FM, '"KYTY_FIX_F29"', None),
    ('15c9d2f2', FM, 'LOGF("FixF29: overflow pass=%', None),
    ('15c9d2f2', FM, 'LOGF("FixF29: mode=%d', None),
    ('15c9d2f2', FM, 'LOGF("Accessed non-GPU cached memory at 0x%016"', None),
    ('730ed40a', 'src/common/subsystems.cpp', 'LOGF("FixF21: mode=%d wait_ms=%u', None),
    ('730ed40a', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 'LOGF("FixB12: mode=%d', None),
]
refs = []
for c, p, a, b in SPEC:
    L = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    hit = [i for i, l in enumerate(L) if a in l]
    assert len(hit) == 1, (c, p, a, len(hit))
    n = hit[0] + 1
    if b is None:
        b = L[n].strip()[:40]
    else:
        assert (b in L[n]) if b else (L[n].strip() == ''), (c, p, a, L[n][:80])
    refs.append((c, p, n, a, b))
    print('%s:%s:%d' % (c, p, n))
src = open(OUT + '.tmpl', encoding='ascii').read()
body = ''.join('    (%s, %s, %d, %s,\n     %s),\n' % (ascii(c), ascii(p), n, ascii(a), ascii(b)) for c, p, n, a, b in refs)
open(OUT, 'w', encoding='ascii', newline='\n').write(src.replace('@REFS@\n', body))
print('written %s refs %d' % (OUT, len(refs)))
