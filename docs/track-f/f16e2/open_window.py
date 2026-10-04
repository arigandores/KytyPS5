# F16e2 (HPP-570, Red Team; ROADMAP s122 item 481(b)(1)): wait for the running series tag (lock seen, then gone and no
# process whose argv ends with procload.py), then create C:/kyty/f287/FS6B_WINDOW with the line "F16e2 HPP-570 <UTC>"
# in the same step that checks the lock and procload.py are absent; one times.txt line. Budget argv[1] seconds.
# Exit 0 - window opened; 2 - budget spent (no file written); 4 - STOP.
import os
import sys
import time

import psutil

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
FW = 'C:/kyty/f287/FS6B_WINDOW'
TIMES = 'C:/kyty/f287/times.txt'


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def gate():
    me = os.getpid()
    n = 0
    for p in psutil.process_iter(['pid', 'cmdline']):
        if p.info['pid'] == me:
            continue
        for a in (p.info['cmdline'] or []):
            a = str(a).replace(chr(92), '/')
            if a.endswith('/procload.py') or a == 'procload.py':
                n += 1
                break
    return n


def main():
    budget = float(sys.argv[1])
    t0 = time.monotonic()
    seen_lock = None
    while time.monotonic() - t0 < budget:
        if os.path.exists(STOP):
            print('STOP', utc())
            return 4
        lock = os.path.exists(LOCK)
        if lock and not seen_lock:
            seen_lock = utc()
            print('lock seen', seen_lock, flush=True)
        if seen_lock and not lock:
            g = gate()
            if g == 0 and not os.path.exists(LOCK):
                stamp = utc()
                with open(FW, 'w', encoding='utf-8', newline='\n') as f:
                    f.write('F16e2 HPP-570 %s\n' % stamp)
                with open(TIMES, 'a', encoding='utf-8', newline='\n') as f:
                    f.write('%s F16e2 window 1 opened (item 481(b)(1)): FS6B_WINDOW written after the lock release of the '
                            'running series tag (lock seen %s); lock absent, procload.py processes 0\n' % (stamp, seen_lock))
                print('window opened', stamp, flush=True)
                return 0
        time.sleep(1)
    print('budget spent', utc(), 'lock seen', seen_lock)
    return 2


sys.exit(main())
