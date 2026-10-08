# F26a (HPP-688): find direct call/jmp rel32 (and jcc rel32) to target addresses in eboot.elf code segments
import sys, struct, re
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
elf = Elf(sys.argv[1]); e = elf.data
tg = [int(x, 16) for x in sys.argv[2:]]
for v, off, fs in elf.code_segments():
    code = e[off:off + fs]
    for pat, ln, kind in ((rb'\xe8', 5, 'call'), (rb'\xe9', 5, 'jmp'), (rb'\x0f[\x80-\x8f]', 6, 'jcc')):
        for m in re.finditer(pat, code):
            i = m.start()
            disp = struct.unpack('<i', code[i + ln - 4:i + ln])[0]
            t = v + i + ln + disp
            if t in tg:
                print('%s at 0x%x -> 0x%x' % (kind, v + i, t))
