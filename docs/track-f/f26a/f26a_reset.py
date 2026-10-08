# F26a (HPP-688): in a code window, disassemble every function (int3/ret + push rbp; mov rbp,rsp) and report functions
# that store [R+0x10] <- [R+0x00] and [R+0x18] <- [R+0x08] for the same base R (writer reset: front=begin, back=end),
# and functions that call [R+0x20] (overflow callback). usage: f26a_reset.py <eboot.elf> <lo-hex> <hi-hex>
import sys, re
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import *
from capstone.x86 import *
elf = Elf(sys.argv[1]); e = elf.data
lo = int(sys.argv[2], 16); hi = int(sys.argv[3], 16)
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
blob = elf.read(lo, hi - lo)
starts = [lo + m.start() + 1 for m in re.finditer(rb'[\xcc\xc3]\x55\x48\x89\xe5', blob)]
for si, st in enumerate(starts):
    en = starts[si + 1] if si + 1 < len(starts) else hi
    loads = {}  # reg -> (base, disp)
    st10 = set(); st18 = set(); cb = []
    for ins in md.disasm(elf.read(st, en - st), st):
        ops = ins.operands
        if ins.mnemonic == 'mov' and len(ops) == 2:
            d, s = ops
            if d.type == CS_OP_REG and s.type == CS_OP_MEM and s.mem.index == 0:
                loads[d.reg] = (s.mem.base, s.mem.disp)
            elif d.type == CS_OP_MEM and s.type == CS_OP_REG and d.mem.index == 0 and s.reg in loads:
                b, dd = loads[s.reg]
                if b == d.mem.base and dd + 0x10 == d.mem.disp and dd in (0, 8):
                    (st10 if dd == 0 else st18).add((b, ins.address))
        if ins.mnemonic in ('vmovups', 'movups', 'vmovdqu', 'movdqu', 'vmovaps', 'movaps') and len(ops) == 2:
            d, s2 = ops
            if d.type == CS_OP_REG and s2.type == CS_OP_MEM and s2.mem.index == 0:
                loads[d.reg] = (s2.mem.base, s2.mem.disp)
            elif d.type == CS_OP_MEM and s2.type == CS_OP_REG and s2.reg in loads and d.mem.index == 0:
                b, dd = loads[s2.reg]
                if b == d.mem.base and dd == 0 and d.mem.disp == 0x10:
                    st10.add((b, ins.address)); st18.add((b, ins.address))
        if ins.mnemonic == 'call' and ops and ops[0].type == CS_OP_MEM and ops[0].mem.disp == 0x20 and ops[0].mem.index == 0:
            cb.append(ins.address)
    b10 = {b for b, a in st10}; b18 = {b for b, a in st18}
    both = b10 & b18
    if both:
        print('RESET fn 0x%x: %s' % (st, ', '.join('0x%x' % a for b, a in sorted(st10 | st18, key=lambda x: x[1]) if b in both)))
    if cb:
        print('CB    fn 0x%x: calls [R+0x20] at %s' % (st, ', '.join('0x%x' % a for a in cb[:6])))
