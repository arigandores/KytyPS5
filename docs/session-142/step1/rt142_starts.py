# Red Team s142 step 1: every "GuestOut: Level has started:" line (name, byte offset) in the calibration logs and s6s137.
import sys
LOGS = ('C:/kyty/s122/log_eatl122.txt', 'C:/kyty/s122/log_edes122.txt', 'C:/kyty/s122/log_atl122.txt',
        'C:/kyty/s122/log_ednn122.txt', 'C:/kyty/s122/log_eght122.txt', 'C:/kyty/s137/log_s6s137.txt')
M = b'GuestOut: Level has started: '
for p in LOGS:
    found = []
    off = 0
    with open(p, 'rb') as f:
        for line in f:
            i = line.find(M)
            if i >= 0:
                found.append((line[i + len(M):].strip().decode('latin1'), off))
            off += len(line)
    print(p, len(found), found)
