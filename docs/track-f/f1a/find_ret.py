import numpy as np, collections
EB = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin'
a = np.fromfile(EB, dtype='<u4', count=(251850759 // 4))
sop1 = a[(a >> 23) == 0x17D]
ops = (sop1 >> 8) & 0xff
for op, name in ((0x20, 'setpc'), (0x21, 'swappc'), (0x1f, 'getpc')):
    sel = sop1[ops == op]
    c = collections.Counter(int(x) for x in sel)
    print(name, len(sel), [(hex(k), v) for k, v in c.most_common(8)])
