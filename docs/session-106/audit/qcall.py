import re, statistics, sys
for t in ('vdb106', 'vid106'):
    q = []; dts = []
    for line in open('C:/kyty/s106/log_%s.txt' % t, 'rb'):
        if line.startswith(b'FrameTrace-x:'):
            m = re.search(rb' da_qcall=(\d+)', line)
            if m: q.append(int(m.group(1)))
        elif line.startswith(b'FrameTrace: '):
            dts.append(int(re.search(rb' dt_us=(\d+)', line).group(1)))
        elif b'dabatch' in line and len(line) < 300:
            print(t, 'LINE', line[:200])
    tail = q[len(q)//3:]
    print(t, 'rows', len(q), 'da_qcall median(last 2/3)', statistics.median(tail), 'min', min(tail), 'max', max(tail), 'frames', len(dts))
