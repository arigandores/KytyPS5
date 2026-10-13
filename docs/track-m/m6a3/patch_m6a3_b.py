"""Track M, M6a3 (HPP-856): second edit of the stand after the first run - the audio arm pushes 5 times now (push 5 -
private commit), the default queue depth 4 refused push 5 (non-blocking, rc 0x80260008): queue_depth 8.
Whole-line anchor, must match once; CRLF kept. Usage: python patch_m6a3_b.py <tree root>   Last line ALL OK or FAIL."""
import sys

ROOT = sys.argv[1].rstrip('/')
T = chr(9)
NL = chr(10)
path = ROOT + '/tests/MWave2DiagStand.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
old = T + 'cp.num_grains = 256;' + NL
new = (T + 'cp.num_grains = 256;' + NL +
       T + 'cp.queue_depth = 8; // M6a3: 5 non-blocking pushes (the default depth 4 refuses the fifth)' + NL)
n = text.count(old)
if n != 1:
    print('FAILED anchor x%d' % n)
    print('FAIL')
    sys.exit(1)
text = text.replace(old, new, 1)
if crlf:
    text = text.replace('\n', '\r\n')
open(path, 'wb').write(text.encode('utf-8'))
print('ALL OK')
