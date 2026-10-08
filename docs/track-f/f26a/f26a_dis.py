# F26a (HPP-688): linear disassembly of eboot.elf range with rip-relative notes and lea strings.
# usage: f26a_dis.py <eboot.elf> <start-hex> <end-hex> [mark-hex]
import sys, struct
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import *
from capstone.x86 import *
elf = Elf(sys.argv[1])
st, en = int(sys.argv[2], 16), int(sys.argv[3], 16)
mark = int(sys.argv[4], 16) if len(sys.argv) > 4 else -1
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
for ins in md.disasm(elf.read(st, en - st), st):
    note = ''
    for op in ins.operands:
        if op.type == CS_OP_MEM and op.mem.base == X86_REG_RIP:
            t = ins.address + ins.size + op.mem.disp
            note += '   ; ->0x%x' % t
            if ins.mnemonic == 'lea':
                s = elf.cstr(t, 120)
                if s and len(s) >= 3 and all(32 <= c < 127 for c in s[:40]): note += ' "%s"' % s.decode('latin1')
    print('%s %8x  %-24s %-8s %s%s' % ('>>' if ins.address == mark else '  ', ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str, note))
