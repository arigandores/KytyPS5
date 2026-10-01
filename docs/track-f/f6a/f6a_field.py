# F6a (HPP-372): instructions of eboot.elf in [lo,hi) whose memory operand has displacement <disp> (field readers/writers).
# usage: f6a_field.py <lo-hex> <hi-hex> <disp-hex> [...]
import sys, struct, re
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import *
elf = Elf('C:/kyty/eboot.elf'); e = elf.data
md = Cs(CS_ARCH_X86, CS_MODE_64)
lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
seg = elf.read(lo, hi - lo)
for d in sys.argv[3:]:
    pat = struct.pack('<I', int(d, 16))
    print('--- disp 0x%s' % d)
    for m in re.finditer(re.escape(pat), seg):
        k = m.start()
        for back in range(2, 8):
            a = lo + k - back
            ins = next(md.disasm(elf.read(a, 16), a), None)
            if ins and ins.size >= back + 4 and ('0x' + d) in ins.op_str and ins.address + ins.size >= lo + k + 4:
                print('  %x  %s %s' % (a, ins.mnemonic, ins.op_str)); break
