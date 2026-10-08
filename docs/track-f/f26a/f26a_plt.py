# F26a (HPP-688): all PLT imports of eboot.elf: stub address -> library, NID, name (emulator LIB_FUNC or sce* string of the
# eboot hashed to NID), HLE or not. usage: f26a_plt.py <eboot.elf> <src dir> <out tsv>
import sys, struct, re, hashlib, base64, collections, os
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
SUF = bytes.fromhex('518D64A635DED8C1E6B039B1C3E55230')
def nid(name):
    d = hashlib.sha1(name.encode() + SUF).digest()[:8]
    return base64.b64encode(struct.pack('>Q', struct.unpack('<Q', d)[0]), b'+-').decode().rstrip('=')
elf = Elf(sys.argv[1]); e = elf.data
phoff = struct.unpack('<Q', e[32:40])[0]; phnum = struct.unpack('<H', e[56:58])[0]
tags = {}; libs = {}
for i in range(phnum):
    t, fl, off, va, pa, fs, ms, al = struct.unpack('<IIQQQQQQ', e[phoff + 56 * i: phoff + 56 * i + 56])
    if t == 2:
        for j in range(0, fs, 16):
            tg, v = struct.unpack('<QQ', e[off + j: off + j + 16])
            if tg == 0: break
            if tg == 0x61000049: libs[v >> 48] = v & 0xffffffff
            else: tags.setdefault(tg, v)
JMPREL, PLTRELSZ, SYMTAB, STRTAB = tags[0x17], tags[0x2], tags[0x6], tags[0x5]
def b64id(s):
    al = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-'
    v = 0
    for ch in s: v = v * 64 + al.index(ch)
    return v
libname = {k: elf.cstr(STRTAB + v).decode() for k, v in libs.items()}
IMPL = {}
for root, ds, fs in os.walk(sys.argv[2]):
    for f in fs:
        if f.endswith('.cpp'):
            src = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
            for m in re.finditer(r'LIB_FUNC\("([^"]+)",\s*([\w:]+)\)', src): IMPL.setdefault(m.group(1), m.group(2))
by_nid = {}
for m in set(re.findall(rb'(?:sce|_)[A-Za-z][A-Za-z0-9_]{3,60}', e)):
    n = m.decode(); by_nid.setdefault(nid(n), n)
rows = {}
for i in range(PLTRELSZ // 24):
    r_off, r_info, r_add = struct.unpack('<QQq', elf.read(JMPREL + 24 * i, 24))
    sym = r_info >> 32
    st_name = struct.unpack('<I', elf.read(SYMTAB + 24 * sym, 4))[0]
    s = elf.cstr(STRTAB + st_name).decode()
    p = s.split('#')
    rows[r_off] = (i, p[0], libname.get(b64id(p[1]), '?') if len(p) == 3 else '?')
out = open(sys.argv[3], 'w', encoding='utf-8')
for v, o, fs in elf.code_segments():
    seg = e[o:o + fs]
    for m in re.finditer(rb'\xff\x25', seg):
        i = m.start()
        t = v + i + 6 + struct.unpack('<i', seg[i + 2:i + 6])[0]
        if t in rows:
            idx, n, lib = rows[t]
            out.write('0x%x\t%d\t%s\t%s\t%s\t%s\n' % (v + i, idx, lib, n, by_nid.get(n, '?'), IMPL.get(n, 'unresolved')))
out.close()
print('imports', len(rows), 'impl', len(IMPL))
