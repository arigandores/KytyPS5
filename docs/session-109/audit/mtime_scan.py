"""Files under C:/kyty (and the emulator folder) modified inside the sealed-run windows (excluding the runs' own outputs)."""
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')


def ts(s):
    return time.mktime(time.strptime('2026-09-23 ' + s, '%Y-%m-%d %H:%M:%S'))


WINDOWS = [('ent109', ts('20:47:02'), ts('21:10:39')), ('vfy109+ent109b', ts('22:42:43'), ts('23:11:56')),
           ('frm109', ts('23:15:34'), ts('23:26:08'))]
ROOTS = ['C:/kyty', 'C:/Users/<user>/OneDrive/Desktop/ps5 em']
SKIP_DIRS = {'.git', 'build', '_ShaderCache', 'node_modules', 'audit109', '_Shaders', '_RenderDoc'}
hits = {w[0]: [] for w in WINDOWS}
for root in ROOTS:
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = os.path.join(dp, f)
            try:
                m = os.stat(p).st_mtime
            except OSError:
                continue
            for name, a, b in WINDOWS:
                if a <= m <= b:
                    hits[name].append((time.strftime('%H:%M:%S', time.localtime(m)), p.replace(os.sep, '/')))
for name, lst in hits.items():
    print('==', name, len(lst))
    for t, p in sorted(lst):
        print('  ', t, p)
