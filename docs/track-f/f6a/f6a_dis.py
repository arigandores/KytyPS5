# F6a (HPP-372): disassembly of the functions around AudioPropagation call sites of eboot.elf (capstone), with names of PLT
# targets and strings of rip-relative lea. usage: f6a_dis.py <site-hex> [before-bytes-limit] [after-instructions]
import sys, struct, re, hashlib, base64
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import *
from capstone.x86 import *
elf = Elf('C:/kyty/eboot.elf'); e = elf.data
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
STUBS = {}
for l in open('C:/kyty/f287/f6a/f6a_elf.out.txt', encoding='utf-8'):
    p = l.split()
    if len(p) >= 6 and p[0].isdigit() and p[1].startswith('0x'):
        STUBS[int(p[5].split(',')[0], 16)] = p[3] if p[3] != '?' else p[2]
def func_start(site, limit=0x3000):
    o = elf.off(site)
    best = None
    for k in range(1, limit):
        a = o - k
        if e[a:a + 4] == b'\x55\x48\x89\xe5' and e[a - 1] in (0xcc, 0x90, 0xc3, 0x00) or (e[a:a + 4] == b'\x55\x48\x89\xe5' and e[a - 2:a] in (b'\x0f\x0b',)) or (e[a:a+4] == b'\x55\x48\x89\xe5' and (site - k) % 16 == 0):
            best = site - k; break
    return best
def dis(site, after=60):
    st = func_start(site)
    print('=== site 0x%x function start 0x%x (site +0x%x)' % (site, st, site - st))
    passed = 0; n = 0
    for ins in md.disasm(elf.read(st, site - st + 0x1800), st):
        note = ''
        if ins.mnemonic in ('call', 'jmp') and ins.operands[0].type == CS_OP_IMM:
            t = ins.operands[0].imm
            if t in STUBS: note = '   ; ' + STUBS[t]
        for op in ins.operands:
            if op.type == CS_OP_MEM and op.mem.base == X86_REG_RIP:
                t = ins.address + ins.size + op.mem.disp
                note += '   ; ->0x%x' % t
                if ins.mnemonic == 'lea':
                    s = elf.cstr(t, 120)
                    if s and len(s) >= 4 and all(32 <= c < 127 for c in s[:40]): note += ' "%s"' % s.decode('latin1')
        mark = '>>' if ins.address == site else '  '
        print('%s %8x  %-10s %s%s' % (mark, ins.address, ins.mnemonic, ins.op_str, note))
        if ins.address >= site: passed += 1
        if passed > after: break
        if passed and ins.mnemonic == 'ret' and passed > 8: 
            n += 1
            if n >= 2: break
for a in sys.argv[1:]:
    if ':' in a:
        s, af = a.split(':'); dis(int(s, 16), int(af))
    else: dis(int(a, 16))
