# F13b: decode the PS constant block of the final pass (EID 1247 and EID 80 of f13_rd) as float/hex rows of 16 bytes.
import struct
for fn in ['rd/buf_e1247_ps_204_67063936.bin', 'rd/buf_e80_ps_204_67014528.bin']:
    d = open('C:/kyty/f287/f13b/' + fn, 'rb').read()
    f = struct.unpack('<%df' % (len(d) // 4), d)
    u = struct.unpack('<%dI' % (len(d) // 4), d)
    print(fn, len(d), 'bytes')
    for i in range(0, len(f), 4):
        print('  off %3d:' % (i * 4), ' '.join('%12.6g' % x for x in f[i:i + 4]), ' | ', ' '.join('%08x' % x for x in u[i:i + 4]))
