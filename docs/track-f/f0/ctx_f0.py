# F0 (HPP-289): what is logged inside the interval of a given frame (between the previous FrameTrace: line and its own)
import re, collections, sys
NUM = re.compile(rb'0x[0-9a-fA-F]+|\b[0-9a-f]{16}\b|\d+')
TARGETS = {
    'C:/kyty/s142/log_c142_01.txt': [363469, 380442],
    'C:/kyty/s142/log_c142_02.txt': [267075, 269168, 270377, 271604, 273244, 273564, 273882, 557383, 725366],
    'C:/kyty/s142/log_c142_03.txt': [262553, 349499, 399618, 423866],
    'C:/kyty/s142/log_c142_05.txt': [287605, 331180, 373184, 423092],
    'C:/kyty/s142/log_c142_06.txt': [315708, 369564],
    'C:/kyty/s142/log_c142_09.txt': [206324, 206637, 206728, 206818, 206908, 207271, 207363],
    'C:/kyty/s142/log_c142_10.txt': [224047],
    'C:/kyty/s142/log_v142.txt': [236004],
}
SKIP = (b'FrameTrace', b'Read ', b'Open:', b'Close:', b'KernelFstat', b'path = ', b'\t')
for f, tg in TARGETS.items():
    tg = sorted(tg)
    want = set(tg)
    last_ft = 0
    buf = []
    print('==', f.split('/')[-1])
    with open(f, 'rb') as fh:
        for i, line in enumerate(fh, 1):
            if i > tg[-1]:
                break
            if line.startswith(b'FrameTrace: n='):
                if i in want:
                    c = collections.Counter()
                    io = 0
                    for l in buf:
                        if l.startswith(SKIP) or not l.strip():
                            io += 1
                            continue
                        c[NUM.sub(b'X', l.strip())[:70]] += 1
                    m = re.match(rb'FrameTrace: n=(\d+) dt_us=(\d+)', line)
                    d = re.search(rb' draws=(\d+)', line)
                    print('  line', i, 'n', m.group(1).decode(), 'dt_us', m.group(2).decode(), 'draws', d.group(1).decode() if d else '?', '| interval lines', len(buf), 'io/blank', io)
                    for k, v in c.most_common(9):
                        print('       ', v, k.decode('latin1'))
                buf = []
                last_ft = i
            elif not line.startswith(b'FrameTrace'):
                if len(buf) < 200000:
                    buf.append(line)
