"""M8c (HPP-860): witness strings of the MS2 binary against MS1 (the text run inline at 2026-10-13T07:3xZ, saved as a file;
output binary_m8c.out.txt). Usage: python binary_m8c.py"""
import hashlib
ms2 = 'C:/kyty/m657/bin/kyty_emulator_c630327b.exe'
ms1 = 'C:/kyty/m657/bin/kyty_emulator_ea35b679.exe'
a = open(ms2, 'rb').read()
b = open(ms1, 'rb').read()
print('ms2', hashlib.sha256(a).hexdigest())
print('ms1', hashlib.sha256(b).hexdigest())
ok = True
for s in [b'MT125: mode=', b'MT125Stat: when=exit', b'MWave1: mask=', b'MT265: mode=', b'MT272: mode=', b'MT231: mode=',
          b'M5W2: mode=', b'MTexOffset:', b'AudioStat:', b'AvTrace:', b'0d2da32ca7ff8b4e4c0fc008726e2c59abe2a8f5',
          b'8dcf31779bbcb7c6e605653a138dae162f645a46', b'KytyPS5-2026-09-15-6a2987a-1940-g3504ecbce']:
    print('%-45s ms2 %d ms1 %d' % (s.decode(), a.count(s), b.count(s)))
c = lambda x, s: x.count(s)
ok &= c(a, b'MT125: mode=') >= 1 and c(b, b'MT125: mode=') == 0
ok &= c(a, b'MT125Stat: when=exit') >= 1 and c(b, b'MT125Stat: when=exit') == 0
for s in (b'MWave1: mask=', b'MT265: mode=', b'MT272: mode=', b'MT231: mode=', b'MTexOffset:', b'AudioStat:', b'AvTrace:'):
    ok &= c(a, s) == c(b, s) >= 1
ok &= c(a, b'M5W2: mode=') >= 1
ok &= c(a, b'0d2da32ca7ff8b4e4c0fc008726e2c59abe2a8f5') >= 1 and c(a, b'8dcf31779bbcb7c6e605653a138dae162f645a46') == 0
print('ALL OK' if ok else 'FAIL')
