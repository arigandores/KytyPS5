# F6a (HPP-372): AudioPropagation imports of eboot.elf: jmprela index -> GOT slot -> NID -> name (hash of names found in the
# eboot strings), PLT stub, call sites. No game, no emulator. usage: f6a_elf.py [dis]
import sys, struct, re, hashlib, base64, collections
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
SUF = bytes.fromhex('518D64A635DED8C1E6B039B1C3E55230')
def nid(name):
    d = hashlib.sha1(name.encode() + SUF).digest()[:8]
    return base64.b64encode(struct.pack('>Q', struct.unpack('<Q', d)[0]), b'+-').decode().rstrip('=')
elf = Elf('C:/kyty/eboot.elf'); e = elf.data
print('eboot.elf sha256 %s size %d' % (hashlib.sha256(e).hexdigest(), len(e)))
# dynamic
dyn = [p for p in range(1)]
phoff = struct.unpack('<Q', e[32:40])[0]; phnum = struct.unpack('<H', e[56:58])[0]
tags = collections.OrderedDict(); mods = {}; libs = {}
for i in range(phnum):
    t, fl, off, va, pa, fs, ms, al = struct.unpack('<IIQQQQQQ', e[phoff + 56 * i: phoff + 56 * i + 56])
    if t == 2:
        for j in range(0, fs, 16):
            tg, v = struct.unpack('<QQ', e[off + j: off + j + 16])
            if tg == 0: break
            if tg == 0x61000049: libs[v >> 48] = v & 0xffffffff
            elif tg == 0x61000045: mods[v >> 48] = v & 0xffffffff
            else: tags.setdefault(tg, v)
JMPREL, PLTRELSZ, SYMTAB, STRTAB, PLTGOT = tags[0x17], tags[0x2], tags[0x6], tags[0x5], tags[0x3]
print('DT_JMPREL 0x%x DT_PLTRELSZ 0x%x (%d entries) DT_SYMTAB 0x%x DT_STRTAB 0x%x DT_PLTGOT 0x%x' % (JMPREL, PLTRELSZ, PLTRELSZ // 24, SYMTAB, STRTAB, PLTGOT))
def b64id(s):
    al = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-'
    v = 0
    for ch in s: v = v * 64 + al.index(ch)
    return v
libname = {k: elf.cstr(STRTAB + v).decode() for k, v in libs.items()}
# names from eboot strings
names = sorted(set(m.group(0).decode() for m in re.finditer(rb'sceAudioPropagation[A-Za-z0-9]+', e)))
by_nid = {nid(n): n for n in names}
print('names sceAudioPropagation* in eboot strings: %d' % len(names))
IMPL = {}
src = open('C:/kyty/KytyPS5/src/libs/libAudio.cpp', encoding='utf-8', errors='replace').read()
for m in re.finditer(r'LIB_FUNC\("([^"]+)",\s*LibAudioPropagation::(\w+)\)', src): IMPL[m.group(1)] = m.group(2)
print('emulator LIB_FUNC AudioPropagation: %d' % len(IMPL))
rows = []
for i in range(PLTRELSZ // 24):
    r_off, r_info, r_add = struct.unpack('<QQq', elf.read(JMPREL + 24 * i, 24))
    sym = r_info >> 32
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack('<IBBHQQ', elf.read(SYMTAB + 24 * sym, 24))
    s = elf.cstr(STRTAB + st_name).decode()
    p = s.split('#')
    if len(p) == 3 and libname.get(b64id(p[1]), '') == 'libSceAudioPropagation':
        rows.append((i, r_off, p[0], s))
print('jmprela entries of library libSceAudioPropagation: %d' % len(rows))
# PLT stubs: ff 25 disp32 -> slot
code = [(v, o, fs) for v, o, fs in elf.code_segments()]
slot2stub = {}
slots = {r[1] for r in rows}
for v, o, fs in code:
    seg = e[o:o + fs]
    for m in re.finditer(rb'\xff\x25', seg):
        i = m.start()
        t = v + i + 6 + struct.unpack('<i', seg[i + 2:i + 6])[0]
        if t in slots: slot2stub.setdefault(t, []).append(v + i)
stub2row = {}
for r in rows:
    for st in slot2stub.get(r[1], []): stub2row[st] = r
# call sites: e8 rel32 / e9 rel32 to a stub
calls = collections.defaultdict(list)
for v, o, fs in code:
    seg = e[o:o + fs]
    for m in re.finditer(rb'[\xe8\xe9]', seg):
        i = m.start()
        if i + 5 > fs: continue
        t = v + i + 5 + struct.unpack('<i', seg[i + 1:i + 5])[0]
        if t in stub2row: calls[stub2row[t][0]].append((v + i, seg[i]))
LOGCNT = {'b-dYXrjSNZU': 2, 'WXMhENV2NcA': 295, 'd84otraxt2s': 365, 'G+QLTfyLMYk': 362}
n_named = 0
print('idx   slot        nid          name                                              emulator        stub        c142_03  call sites')
for i, slot, n, s in rows:
    nm = by_nid.get(n, '?')
    n_named += nm != '?'
    print('%4d  0x%x  %-11s  %-48s  %-14s  %s  %7s  %s' % (i, slot, n, nm, 'HLE' if n in IMPL else 'unresolved', ','.join('0x%x' % x for x in slot2stub.get(slot, [])), LOGCNT.get(n, 0) if n not in IMPL else '-',
          ' '.join('0x%x%s' % (a, '' if op == 0xe8 else '(jmp)') for a, op in calls[i])))
print('named by hash: %d of %d; HLE: %d; unresolved: %d' % (n_named, len(rows), sum(1 for r in rows if r[2] in IMPL), sum(1 for r in rows if r[2] not in IMPL)))
assert all(by_nid.get(k) for k in LOGCNT), 'a called NID has no name'
for k in LOGCNT: print('CALLED %s = %s' % (k, by_nid[k]))
for n in names:
    if nid(n) not in {r[2] for r in rows}: print('string without import: %s %s' % (n, nid(n)))
if len(sys.argv) > 1 and sys.argv[1] == 'sites':
    for i, slot, n, s in rows:
        for a, op in calls[i]: print('SITE %x %s' % (a, by_nid.get(n, n)))
