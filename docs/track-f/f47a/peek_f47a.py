# F47a (HPP-802): print lines around the first "Level has started:" of a log (binary read, stops early).
# Usage: python peek_f47a.py <log> [before] [after]
import sys
from collections import deque

log = sys.argv[1]
nb = int(sys.argv[2]) if len(sys.argv) > 2 else 6
na = int(sys.argv[3]) if len(sys.argv) > 3 else 6
prev = deque(maxlen=nb)
after = -1
with open(log, 'rb') as f:
    for line in f:
        if after >= 0:
            if b'FrameTrace' in line or b'Level' in line or b'present' in line:
                sys.stdout.write(line.decode('utf-8', 'replace'))
                after += 1
            if after >= na:
                break
            continue
        if b'Level has started:' in line:
            for p in prev:
                sys.stdout.write(p.decode('utf-8', 'replace'))
            sys.stdout.write('>>> ' + line.decode('utf-8', 'replace'))
            after = 0
            continue
        if b'FrameTrace' in line or b'present' in line:
            prev.append(line)
