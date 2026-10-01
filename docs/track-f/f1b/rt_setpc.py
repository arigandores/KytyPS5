# F1b (Red Team): SOP1 PC-control words in eboot.bin and sce_module/* (dword aligned and all 4 byte phases).
# SOP1: [31:23]=0b101111101, SDST[22:16], OP[15:8], SSRC0[7:0]. OP 0x20 SETPC, 0x21 SWAPPC.
import os, collections, numpy as np
root = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app'
paths = [os.path.join(root, 'eboot.bin')]
sm = os.path.join(root, 'sce_module')
if os.path.isdir(sm):
    for dp, dn, fn in os.walk(sm):
        paths += [os.path.join(dp, f) for f in fn]
for p in paths:
    data = open(p, 'rb').read()
    res = collections.Counter()
    for ph in range(4):
        b = data[ph: ph + (len(data) - ph) // 4 * 4]
        a = np.frombuffer(b, dtype='<u4')
        m = (a >> 23) == 0x17D
        op = (a >> 8) & 0xff
        sel = a[m & ((op == 0x20) | (op == 0x21))]
        for w in sel.tolist():
            k = ('SETPC' if ((w >> 8) & 0xff) == 0x20 else 'SWAPPC', 'sdst=%d' % ((w >> 16) & 0x7f), 'ssrc0=%d' % (w & 0xff), 'phase=%d' % ph)
            res[k] += 1
    print(os.path.relpath(p, root), len(data))
    for k, v in sorted(res.items(), key=lambda kv: -kv[1])[:25]:
        print('  ', k, v)
print('ALL OK')
