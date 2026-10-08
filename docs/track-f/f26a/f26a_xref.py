# F26a (HPP-688): find strings of the B25 assert in eboot.elf and rip-relative xrefs to them (lea/mov) in code segments
import sys, struct, re
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import *
from capstone.x86 import *
elf = Elf(sys.argv[1]); e = elf.data
targets = [b'There are too many objects/batches', b'command_buffer_writer.ppr.cpp', b'command_buffer_writer']
strs = {}
for t in targets:
    for m in re.finditer(re.escape(t), e):
        o = m.start()
        # back to string start
        s = o
        while s > 0 and e[s - 1] != 0 and o - s < 400: s -= 1
        # map file offset -> vaddr
        for v, off, fs, ms, fl in elf.loads:
            if off <= s < off + fs:
                va = v + (s - off); strs[va] = e[s:e.find(b'\0', s)][:200]
for va, s in sorted(strs.items()):
    print('str 0x%x %r' % (va, s))
# scan code for rip-relative references (disp32) to these addresses: brute force over code bytes for lea r64,[rip+disp]
want = set(strs)
for v, off, fs in elf.code_segments():
    code = e[off:off + fs]
    # lea: REX.W(48/4c) 8d modrm(00 reg 101) disp32
    for m in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]', code):
        i = m.start()
        disp = struct.unpack('<i', code[i + 3:i + 7])[0]
        tgt = v + i + 7 + disp
        if tgt in want:
            print('xref lea at 0x%x -> 0x%x %r' % (v + i, tgt, strs[tgt][:60]))
