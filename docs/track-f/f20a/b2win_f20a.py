# F20a (HPP-551): the game moment of B2 in scene coordinates.  On the tool builds of sessions 129-131 the B2 frame stands
# at idx 775..777 (frames after the first scene frame of Sky Garden; n 949..954 at first_n 172..177).  For every given
# log: the frames idx IDX0..IDX1 after the first scene frame of the first Sky Garden scene - the largest dt_us, and every
# 'PriorityStall:' line of that range with the dt_us of the frame whose interval holds it, the number of IR-dump lines
# ('%...') and of 'Vulkan pipeline cache: saved' lines of the same interval.  Reads the log up to idx IDX1 only.
# Usage: python b2win_f20a.py <out.txt> <tag=path> ...
import lzma, re, sys

IDX0, IDX1 = 700, 900
FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
DRAWS = re.compile(rb' draws=(\d+)')
US = re.compile(rb' us=(\d+)')
out = open(sys.argv[1], 'w', encoding='utf-8', newline='\n')


def emit(s):
    out.write(s + '\n')
    print(s)


emit('range idx %d..%d after the first scene frame; B2 moment of the tool builds: idx 775..777' % (IDX0, IDX1))
for a in sys.argv[2:]:
    tag, path = a.split('=', 1)
    f = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    in_sg = False
    first_n = None
    idx = 0
    prio, ir, pcs = [], 0, 0
    rows = []
    stalls = []
    for line in f:
        if line.startswith(b'FrameTrace: n='):
            m = FT.match(line)
            if not m or not in_sg:
                prio, ir, pcs = [], 0, 0
                continue
            n, dt = int(m.group(1)), int(m.group(2))
            if first_n is None:
                d = DRAWS.search(line)
                if d and int(d.group(1)) >= 100:
                    first_n = n
            else:
                idx += 1
                if IDX0 <= idx <= IDX1:
                    rows.append((idx, n, dt))
                    for u in prio:
                        stalls.append((idx, n, dt, u, ir, pcs))
                if idx > IDX1:
                    break
            prio, ir, pcs = [], 0, 0
        elif b'Level has started:' in line:
            name = line.split(b'Level has started:', 1)[1].strip()
            if name:
                if in_sg:
                    break
                in_sg = name == b'underwater_aerial_garden'
        elif in_sg and first_n is not None:
            if line.startswith(b'PriorityStall:'):
                u = US.search(line)
                prio.append(int(u.group(1)) if u else -1)
            elif line.lstrip()[:1] == b'%':
                ir += 1
            elif b'Vulkan pipeline cache: saved' in line:
                pcs += 1
    f.close()
    if not rows:
        emit('%s: first_n %s, no frame in the range' % (tag, first_n))
        continue
    mx = max(rows, key=lambda r: r[2])
    b2 = [r for r in rows if 770 <= r[0] <= 782]
    mb = max(b2, key=lambda r: r[2]) if b2 else None
    emit('%s: first_n %d; frames in the range %d; max dt_us %d at idx %d (n %d); max at idx 770..782: %s; frames >= 50 ms: %s' % (
        tag, first_n, len(rows), mx[2], mx[0], mx[1], ('%d at idx %d (n %d)' % (mb[2], mb[0], mb[1])) if mb else '-',
        [(r[0], r[1], r[2]) for r in rows if r[2] >= 50000]))
    for s in stalls:
        emit('    PriorityStall: idx %d n %d frame dt_us %d stall us %d; IR lines %d, cache saves %d in the interval' % s)
    if not stalls:
        emit('    PriorityStall: none in the range')
out.close()
