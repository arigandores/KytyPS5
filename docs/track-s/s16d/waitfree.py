"""S16d (HPP-608): wait until neither the lock C:/kyty/SEALED_RUN.lock nor a live gate process (name built from parts,
so that no command line holds it) exists, polling every 10 s for at most argv[1] seconds; the state must hold for two polls
in a row. Exit 0 free, 1 time up, 4 STOP."""
import os
import sys
import time

import psutil

GATE = 'procload' + '.py'


def gate_alive():
    me = os.getpid()
    for p in psutil.process_iter(['pid', 'cmdline']):
        if p.info['pid'] == me:
            continue
        for a in p.info['cmdline'] or []:
            a = a.replace(chr(92), '/')
            if a == GATE or a.endswith('/' + GATE):
                return True
    return False


def main():
    limit = float(sys.argv[1]) if len(sys.argv) > 1 else 540
    t0 = time.time()
    free_polls = 0
    while time.time() - t0 < limit:
        if os.path.exists('C:/kyty/s288/STOP'):
            print('STOP')
            return 4
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or gate_alive():
            free_polls = 0
        else:
            free_polls += 1
            if free_polls >= 2:
                print('free %s' % time.strftime('%H:%M:%SZ', time.gmtime()))
                return 0
        time.sleep(10)
    print('busy %s' % time.strftime('%H:%M:%SZ', time.gmtime()))
    return 1


if __name__ == '__main__':
    sys.exit(main())
