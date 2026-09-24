# Indication of the per-slot protocol's constant cost (audit 111): per-call walker time in QueueDrawAhead and per-hit
# take time on GuestGpu, across every run with the same scene/harness (rows n >= 2100). Reads runsum.txt.
import re
L = open('C:/kyty/s111/audit111/runsum.txt', encoding='utf-8').read().splitlines()
build = {'shp110': 'b3f7a2c9 pre', 'vid110': '072861c8 pre', 'obs111': '072861c8 pre',
         'vds111': 'c8235c90 post', 'vds111b': 'c8235c90 post', 'shp111': 'c8235c90 post', 'vss111': 'c8235c90 post',
         'vid111': '0c8a13f2 post'}
note = {('shp110', '0'): 'cspfree=0 (600 s ABBA, BDA NEW)', ('shp110', '1'): 'cspfree=1 (600 s ABBA, BDA NEW)',
        ('vid110', '0'): 'defaults, recording, BDA OLD', ('obs111', '0'): 'plkstat=1, BDA NEW',
        ('vds111', '0'): 'daslot=2 (smemocheck off by defect), BDA OLD', ('vds111b', '0'): 'daslot=2 + smemocheck=1, BDA OLD',
        ('shp111', '0'): 'daslot=0 + guards (600 s ABBA arm 0), BDA OLD', ('shp111', '1'): 'daslot=1 (arm 1), BDA OLD',
        ('vss111', '0'): 'daslot=1 gate, recording, BDA OLD', ('vid111', '0'): 'daslot=1 default, recording, BDA OLD'}
print('%-8s %-4s %-14s %10s %10s %9s %10s %10s %9s  %s' % ('run', 'arm', 'build', 'da_queue', 'da_qcall', 'us/call',
                                                              'da_take', 'da_hit', 'us/hit', 'config'))
for l in L:
    m = re.match(r'(\S+)\s+arm(-?\d+)\s+rows\s+(\d+)\s+(.*)', l)
    if not m: continue
    tag, arm = m.group(1), m.group(2)
    kv = dict(re.findall(r'(\w+)=([-\d.]+)', m.group(4)))
    q, c, t, h = (float(kv[k]) for k in ('da_queue_us', 'da_qcall', 'da_take_us', 'da_hit'))
    print('%-8s %-4s %-14s %10.1f %10.1f %9.3f %10.1f %10.1f %9.4f  %s' % (tag, arm, build[tag], q, c, q / c, t, h, t / h,
                                                                          note.get((tag, arm), '')))
