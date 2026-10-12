"""M1a2 (HPP-837, ROADMAP p.756(b)(1)): offline whole-game evidence for T226 and the LDS part of T185 (new theme T314).
For every AMDGPU ELF inside eboot.bin (method of docs/track-f/f23a/gcn_f23a.py eboot_programs: e_machine 0xE0, key =
XXH3-64 of .shader_text) read section .shader_header (AGC Shader header, layout = b3dc9c67:src/graphics/shader/shader.h
struct Shader: num_sh_registers at byte 92, register pairs (offset, value)) and take the SH register pair with offset
0x213 = COMPUTE_PGM_RSRC2 (b3dc9c67:src/graphics/guest_gpu/pm4.h:925); LDS_SIZE = bits [23:15] (pm4.h:940-941); bytes =
LDS_SIZE * 128 dwords * 4 (b3dc9c67:src/graphics/shader/shader.cpp:850). A program is CS if the pair 0x213 is present.
The pairs start at byte 32 + (64-bit field sh_registers at byte 32) - the pointer is relative to its own field [c: with
this base all 5 698 headers give num_sh pairs with offsets < 0x400; CS headers (type byte 90 = 0) give 0x20C/0x20D
COMPUTE_PGM_LO/HI, 0x212/0x213 RSRC1/RSRC2, 0x207-0x209 NUM_THREAD_X/Y/Z].
Read-only; exit 3 under C:/kyty/SEALED_RUN.lock, exit 4 under C:/kyty/m657/STOP.
Usage: python lds_m1a2.py [limit_bytes=49152] -> prints histogram and ALL OK; TSV to stdout file given by env LDS_OUT."""
import collections, mmap, os, struct, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP present - exit 4'); sys.exit(4)
import xxhash
GAME = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/'
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 49152
MAGIC = bytes([0x7F, 0x45, 0x4C, 0x46, 2, 1, 1])
f = open(GAME + 'eboot.bin', 'rb')
mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
progs = {}
n_elf = 0
bad = collections.Counter()
e = mm.find(MAGIC)
while e != -1:
    if struct.unpack_from('<H', mm, e + 18)[0] == 0xE0:
        shoff = struct.unpack_from('<Q', mm, e + 0x28)[0]
        shentsize, shnum, shstrndx = struct.unpack_from('<HHH', mm, e + 0x3A)
        secs = [struct.unpack_from('<IIQQQQ', mm, e + shoff + k * shentsize) for k in range(shnum)]
        stroff = e + secs[shstrndx][4]
        sec = {}
        for name, typ, fl, addr, off, size in secs:
            end = mm.find(bytes([0]), stroff + name)
            sec[bytes(mm[stroff + name:end])] = bytes(mm[e + off:e + off + size])
        code, hdr = sec.get(b'.shader_text'), sec.get(b'.shader_header')
        if code is None or hdr is None:
            bad['no_section'] += 1
        else:
            n_elf += 1
            h = '%016x' % xxhash.xxh3_64_intdigest(code)
            w = struct.unpack_from('<%dI' % (len(hdr) // 4), hdr)
            num_sh = hdr[92]
            base = 32 + struct.unpack_from('<Q', hdr, 32)[0]
            found = [struct.unpack_from('<II', hdr, base + 8 * i) for i in range(num_sh)] if base + 8 * num_sh <= len(hdr) else None
            if found is None or any(o >= 0x400 for o, v in found):
                bad['sh_block'] += 1
                found = None
            elif hdr[90] == 0 and not any(o == 0x213 for o, v in found):
                bad['cs_type_without_rsrc2'] += 1
            elif hdr[90] != 0 and any(o == 0x213 for o, v in found):
                bad['rsrc2_in_non_cs_type'] += 1
            rsrc2 = [v for o, v in (found or []) if o == 0x213]
            lds = ((rsrc2[0] >> 15) & 0x1FF) * 128 * 4 if rsrc2 else None
            progs.setdefault(h, set()).add(lds)
    e = mm.find(MAGIC, e + 1)
multi = sum(1 for v in progs.values() if len(v - {None}) > 1)
cs = {h: max(v - {None}) for h, v in progs.items() if v - {None}}
hist = collections.Counter(cs.values())
over = sorted(h for h, v in cs.items() if v > LIMIT)
print('elf', n_elf, 'unique programs', len(progs), 'CS (pair 0x213)', len(cs), 'non-CS', len(progs) - len(cs))
print('LDS bytes histogram (CS):', ' '.join('%d:%d' % (k, hist[k]) for k in sorted(hist)))
print('max LDS bytes', max(cs.values()) if cs else None, 'limit', LIMIT, 'CS over limit', len(over), ' '.join(over[:20]))
print('same code in ELFs with different LDS (max taken):', multi)
print('anomalies', dict(bad))
out = os.environ.get('LDS_OUT')
if out:
    with open(out, 'w', encoding='utf-8', newline='\n') as g:
        g.write('hash\tlds_bytes\n')
        for h in sorted(cs):
            g.write('%s\t%d\n' % (h, cs[h]))
ok = len(progs) == 5698 and not bad
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
