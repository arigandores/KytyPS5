# F26a (HPP-688): find instructions with a given memory displacement (store/load) in a code window; prints with capstone
# usage: f26a_disp.py <eboot.elf> <disp-hex> <lo-hex> <hi-hex> [store]
import sys, struct, re
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import *
from capstone.x86 import *
elf = Elf(sys.argv[1]); e = elf.data
disp = int(sys.argv[2], 16); lo = int(sys.argv[3], 16); hi = int(sys.argv[4], 16)
store_only = len(sys.argv) > 5
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
code = elf.read(lo, hi - lo)
pat = re.escape(struct.pack('<i', disp))
seen = set()
for m in re.finditer(pat, code):
    i = m.start()
    for back in range(2, 9):
        a = lo + i - back
        if a in seen: continue
        try:
            ins = next(md.disasm(elf.read(a, 16), a))
        except StopIteration:
            continue
        if ins.address + ins.size <= lo + i: continue
        ok = False
        for k, op in enumerate(ins.operands):
            if op.type == CS_OP_MEM and op.mem.disp == disp and op.mem.base != X86_REG_RIP:
                if store_only and k != 0: continue
                ok = True
        if ok:
            seen.add(a)
            print('%8x  %-8s %s' % (ins.address, ins.mnemonic, ins.op_str))
            break
