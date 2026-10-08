# F26a (HPP-688): disassemble the whole function containing an address (start = after int3/ret padding with push rbp; mov rbp,rsp)
# usage: f26a_fn.py <eboot.elf> <addr-hex> [max-bytes]
import sys
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import *
from capstone.x86 import *
elf = Elf(sys.argv[1]); e = elf.data
site = int(sys.argv[2], 16); mx = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x3000
o = elf.off(site); st = None
for k in range(0, 0x8000):
    a = o - k
    if e[a:a + 4] == b'\x55\x48\x89\xe5' and e[a - 1] in (0xcc, 0xc3):
        st = site - k; break
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
print('function start 0x%x (site 0x%x = +0x%x)' % (st, site, site - st))
for ins in md.disasm(elf.read(st, mx), st):
    note = ''
    for op in ins.operands:
        if op.type == CS_OP_MEM and op.mem.base == X86_REG_RIP:
            t = ins.address + ins.size + op.mem.disp
            note += '   ; ->0x%x' % t
            if ins.mnemonic == 'lea':
                s = elf.cstr(t, 120)
                if s and len(s) >= 3 and all(32 <= c < 127 for c in s[:40]): note += ' "%s"' % s.decode('latin1')
    print('%s %8x  %-8s %s%s' % ('>>' if ins.address == site else '  ', ins.address, ins.mnemonic, ins.op_str, note))
    if ins.mnemonic == 'int3' and ins.address > site: break
