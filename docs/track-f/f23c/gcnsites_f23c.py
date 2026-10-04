"""F23c (HPP-587): guest-side sites of the reference PS 0xe197e307a5f2cb39 - MIMG instructions (raw words and RDNA2 fields:
word1 vaddr [7:0], vdata [15:8], srsrc [20:16]*4, ssamp [25:21]*4; NSA dwords hold the further address VGPRs byte by byte)
found by the instruction walk of F23a (gcn_f23a.walk). The field names are ISA [I]; the raw words are [c].
Output: gcnsites_f23c.out.txt"""
import struct
import sys

sys.path.insert(0, 'C:/kyty/KytyPS5/docs/track-f/f23a')
import gcn_f23a  # noqa: E402

G = 'C:/kyty/s288/s4/gcn/g_1/ps_e197e307a5f2cb39.bin'
data = open(G, 'rb').read()
words = list(struct.unpack('<%dI' % (len(data) // 4), data))
ins, status = gcn_f23a.walk(words)
lines = ['reference PS %s: %d words, walk %s, %d instructions' % (G, len(words), status, len(ins))]
for pc, fam, op, size, ex in ins:
    raw = ' '.join('%08x' % w for w in words[pc:pc + size])
    if fam == 'MIMG':
        w1 = words[pc + 1]
        addrs = [w1 & 0xff]
        for k in range(2, size):
            w = words[pc + k]
            addrs += [(w >> s) & 0xff for s in (0, 8, 16, 24)]
        lines.append('pc %3d MIMG op 0x%02x dmask 0x%x vdata v%d vaddr %s srsrc s[%d] ssamp s[%d]  raw %s' % (
            pc, op, (words[pc] >> 8) & 0xf, (w1 >> 8) & 0xff, ','.join('v%d' % a for a in addrs), ((w1 >> 16) & 0x1f) * 4,
            ((w1 >> 21) & 0x1f) * 4, raw))
    elif fam == 'SOP1' and op in (0x09, 0x0a):
        lines.append('pc %3d SOP1 op 0x%02x (S_WQM_B32/B64 [I]) sdst %d  raw %s' % (pc, op, ex.get('sdst', -1), raw))
open('C:/kyty/f287/f23c/gcnsites_f23c.out.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
