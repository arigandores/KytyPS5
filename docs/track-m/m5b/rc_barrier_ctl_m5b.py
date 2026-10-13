"""M5b: positive control of rc_barrier_m5b - programs with s_barrier, store-then-barrier, barrier-then-buffer-load. Read-only."""
import os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc_tr_m5b.py'), encoding='utf-8').read()
src = src[:src.index('progs = sorted(')]
ns = {}
exec(compile(src, 'rc_tr_m5b', 'exec'), ns)
D = 'C:/kyty/f287/f23a/eboot_text/'
nb = 0; nsb = 0; nbl = 0
for fn in sorted(os.listdir(D)):
    b = open(D + fn, 'rb').read()
    words = [int.from_bytes(b[i:i + 4], 'little') for i in range(0, len(b) // 4 * 4, 4)]
    st = 0; hb = False; bl = False
    for pc, fam, w, w1, s, i in ns['walk'](words):
        if fam == 'SOPP' and i['op'] == 0x0a:
            hb = True
            if st == 1:
                st = 2
        if fam == 'MUBUF' and (0x04 <= i['op'] <= 0x07 or 0x18 <= i['op'] <= 0x1f):
            st = max(st, 1)
        if fam == 'MUBUF' and hb and (i['op'] <= 0x03 or 0x08 <= i['op'] <= 0x0f):
            bl = True
    nb += hb; nsb += (st == 2); nbl += bl
print('programs with s_barrier', nb, 'store-then-barrier', nsb, 'barrier-then-buffer-load', nbl)
