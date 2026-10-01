# F0 (HPP-289): what is logged inside the interval of a given frame (between the previous FrameTrace: line and its own)
import re, collections, sys
NUM = re.compile(rb'0x[0-9a-fA-F]+|\b[0-9a-f]{16}\b|\d+')
TARGETS = {
    'C:/kyty/s129/log_ack129.txt': [337656],
    'C:/kyty/s130/log_ack130.txt': [347229],
    'C:/kyty/s130/log_s12s130.txt': [346996],
    'C:/kyty/s130/log_s3s130.txt': [473319],
    'C:/kyty/s131/log_lw3s131.txt': [325377],
    'C:/kyty/s131/log_lw4s131.txt': [332368],
    'C:/kyty/s131/log_lw5s131.txt': [346682],
    'C:/kyty/s135/log_rs135.txt': [1082583],
    'C:/kyty/s122/log_ednn122.txt': [],
}
SKIP = (b'FrameTrace', b'Read ', b'Open:', b'Close:', b'KernelFstat', b'path = ', b'\t')
for f, tg in TARGETS.items():
    tg = sorted(tg)
    if not tg:
        continue
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
