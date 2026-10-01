# F1b (Red Team): are the 473 SWAPPC s[14:15] words and the 39 aligned SETPC words inside the 101 B26 shader blobs?
import numpy as np, csv
eb = open('C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin', 'rb').read()
a = np.frombuffer(eb[: len(eb) // 4 * 4], dtype='<u4')
rows = list(csv.DictReader(open('C:/kyty/f287/f1a/b26_shaders.tsv', encoding='utf-8'), delimiter='\t'))
iv = sorted((int(r['eboot_offset'], 16), int(r['eboot_offset'], 16) + 4 * int(r['code_words']), r['hash']) for r in rows)
def owner(off):
    for s, e, h in iv:
        if s <= off < e:
            return h
    return None
m = (a >> 23) == 0x17D
op = (a >> 8) & 0xff
for name, sel in (('SWAPPC s[14:15],s[14:15]', a == 0xBE8E210E), ('SETPC any', m & (op == 0x20))):
    idx = np.nonzero(sel)[0]
    inside = [(int(i) * 4, owner(int(i) * 4)) for i in idx]
    n_in = sum(1 for o, h in inside if h)
    print(name, 'total', len(idx), 'inside B26 blobs', n_in, 'outside', len(idx) - n_in)
    for o, h in inside:
        if not h:
            # nearest blob
            near = min(iv, key=lambda t: min(abs(o - t[0]), abs(o - t[1])))
            print('   outside: off=0x%x word=0x%08x nearest blob %s [0x%x,0x%x)' % (o, a[o // 4], near[2], near[0], near[1]))
print('ALL OK')
