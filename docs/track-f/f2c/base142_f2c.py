import glob
import os
import sys
sys.path.insert(0, 'C:/kyty/f287/f2c')
import f2c_b26 as F  # noqa: E402

h96, h5 = F.load_hashes()
print('f2c_b26.py regression on the 12 s142 logs (9235a7ac, no knob) read as =0')
bad = 0
for p in sorted(glob.glob('C:/kyty/s142/log_*.txt')):
    r = F.scan(p, h96, h5)
    o = F.judge(r, '0', h5)
    if o['verdict_letter'] != 'CONTROL RETURNS' or o['reopen_any']:
        bad += 1
    print('%s %s profile %d/%d/%d f3 %d knob %s letter %d variant %d reopen %s deaths %d phi %d precache %d -> %s' % (
        os.path.basename(p), r['sha256'][:8], o['n21'], o['n0c'], o['ne3'], o['nf3'], o['knob'], o['letter5'],
        o['variant5'], o['reopen'], o['deaths'], o['phi'], r['precache_lines'], o['verdict_letter']))
print('logs not CONTROL RETURNS or with reopen: %d' % bad)
print('ALL OK' if bad == 0 else 'SOME FAILED')
