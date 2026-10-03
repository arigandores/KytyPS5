# F9e (HPP-422): one streaming pass over the F9d log - the clear of the T6 surface.
# For every ImageLife create of the T6 surface (960x540 @0x53cc10000, 480x270 @0x538bc0000):
# the six non-tab log lines before it; the fills of the two metadata addresses; CmaskClear lines
# by image; RenderColorTarget / ImageWatchDraw lines at the T6 addresses.
# usage: python scan_f9e.py <log.txt> <out.txt>
import collections
import re
import sys

LOG, OUT = sys.argv[1], sys.argv[2]
T6 = {b'guest=0x000000053cc10000': '960', b'guest=0x0000000538bc0000': '480'}
META = {'960': b'0x0000000571728000', '480': b'0x000000055675f000'}
prev = collections.deque(maxlen=6)
fills = collections.Counter()
fill_lines = collections.defaultdict(list)
cmask = collections.Counter()
rct = []
watch_draw = 0
creates = []
with open(LOG, 'rb') as f:
    for i, l in enumerate(f, 1):
        if l.startswith(b'BufferFillTrace'):
            for k, w in META.items():
                if b'addr=' + w in l:
                    m = re.search(rb'frame=(\d+).*size=(0x[0-9a-f]+) value=(0x[0-9a-f]+) outcome=(\w+)', l)
                    fills[(k, m.group(2).decode(), m.group(3).decode(), m.group(4).decode())] += 1
                    fill_lines[k].append((i, int(m.group(1))))
        elif l.startswith(b'CmaskClear'):
            m = re.search(rb'image=(0x[0-9a-f]+) meta=(0x[0-9a-f]+)', l)
            cmask[(m.group(1).decode(), m.group(2).decode())] += 1
        elif l.startswith(b'ImageWatchDraw'):
            watch_draw += 1
        elif l.startswith(b'RenderColorTarget') and (b'addr=0x053cc10000' in l or b'addr=0x0538bc0000' in l):
            rct.append('%d %s' % (i, l.decode('utf-8', 'replace').rstrip()))
        elif l.startswith(b'ImageLife: event=create'):
            for key, kind in T6.items():
                if key in l:
                    creates.append((i, kind, re.search(rb'frame=(\d+)', l).group(1).decode(),
                                    [p for p in prev]))
        if not l.startswith(b'\t'):
            prev.append((i, l.rstrip()))

with open(OUT, 'w', encoding='utf-8', newline='\n') as o:
    o.write('log %s\n' % LOG)
    o.write('ImageWatchDraw lines: %d\n' % watch_draw)
    o.write('RenderColorTarget at T6 addresses: %d\n' % len(rct))
    for r in rct:
        o.write('  %s\n' % r[:240])
    o.write('fills of the metadata addresses (kind, size, value, outcome): count\n')
    for k, v in sorted(fills.items()):
        o.write('  %s %d\n' % (k, v))
    for k, v in fill_lines.items():
        o.write('  %s frames %s\n' % (k, ' '.join('%d@%d' % (fr, ln) for ln, fr in v)))
    o.write('CmaskClear by (image, meta): count\n')
    for k, v in sorted(cmask.items()):
        o.write('  %s %d\n' % (k, v))
    o.write('T6 creates: line kind frame | fill of META[kind] among the 6 non-tab lines before\n')
    n_fill = 0
    for i, kind, fr, p in creates:
        hits = [ln for ln, s in p if s.startswith(b'BufferFillTrace') and b'addr=' + META[kind] in s]
        n_fill += 1 if hits else 0
        o.write('  %d %s frame=%s fill_before=%s\n' % (i, kind, fr, ','.join(str(h) for h in hits) or '-'))
    o.write('T6 creates %d, with the fill right before %d\n' % (len(creates), n_fill))
    o.write('context (6 non-tab lines before each create):\n')
    for i, kind, fr, p in creates:
        o.write('== %d %s frame=%s\n' % (i, kind, fr))
        for ln, s in p:
            o.write('   %d %s\n' % (ln, s.decode('utf-8', 'replace')[:200]))
print('done', OUT)
