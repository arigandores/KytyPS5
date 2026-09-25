"""Independent light recount of K5 raw sums and K1 (arm 0 kept frames) from log_spn117.txt (audit, read-only)."""
import re
from collections import defaultdict

LOG = 'C:/kyty/s117/log_spn117.txt'
RE_MAIN = re.compile(rb'^FrameTrace: n=(\d+) .* arm=(\d+) blk=(\d+)')
RE_X = re.compile(rb'^FrameTrace-x: n=(\d+) ')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
main = {}
x = {}
k5 = defaultdict(int)
lines = defaultdict(int)
xdup = 0
with open(LOG, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: n='):
            m = RE_MAIN.match(line)
            if m:
                n = int(m.group(1))
                d = dict(FIELD.findall(line))
                main[n] = (int(m.group(2)), int(m.group(3)), int(d.get(b'dt_us', b'0')))
        elif line.startswith(b'FrameTrace-x: n='):
            n = int(RE_X.match(line).group(1))
            d = {k.decode(): int(v) for k, v in FIELD.findall(line)}
            if n > 1800:
                for k in ('spine_bad', 'spine_misal', 'cram_write', 'spine_lost', 'spine_abort', 'spine_pad'):
                    k5[k] += d.get(k, 0)
            if n in x:
                xdup += 1
            x[n] = d
        elif line.startswith((b'SpineMismatch:', b'SpineMisalign:', b'SpineAbort:', b'SpineLost')):
            lines[line[:14]] += 1
print('K5 raw sums over x lines n>1800:', dict(k5), 'diag lines:', dict(lines), 'x dups:', xdup)
# K1: arm 0, kept frames 10..89 of each block (position = n - (1800 + 90*blk)), try both 0- and 1-based positions
for base in (0, 1):
    acc = defaultdict(list)
    for n, (arm, blk, dt) in main.items():
        if n <= 1800 or n not in x:
            continue
        pos = n - (1800 + 90 * blk) - base
        if 10 <= pos <= 89:
            acc[arm].append((x[n].get('spine_ns', 0) / 1000.0, x[n].get('spine_cmp', 0), x[n].get('spine_el', 0), dt,
                             x[n].get('da_walk_us', 0)))
    for arm in sorted(acc):
        v = acc[arm]
        k = len(v)
        print('base', base, 'arm', arm, 'kept', k, 'spine_us %.1f' % (sum(a[0] for a in v) / k),
              'cmp/frame %.4f' % (sum(a[1] for a in v) / k), 'el/frame %.1f' % (sum(a[2] for a in v) / k),
              'dt %.1f' % (sum(a[3] for a in v) / k), 'cmp/el %.5f' % (sum(a[1] for a in v) / max(1, sum(a[2] for a in v))))
