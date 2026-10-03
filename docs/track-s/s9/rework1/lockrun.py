"""lockrun.py - track S link S9 (HPP-431), general rule 27: runs a command, polls C:/kyty/SEALED_RUN.lock and C:/kyty/s288/STOP
every 0.5 s and kills the whole process tree when either appears (rc 5 lock / 4 stop).  The output goes to the file given.
    python lockrun.py <out file> <command ...>
"""
import os
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'


def main():
    out, cmd = sys.argv[1], sys.argv[2:]
    if os.path.exists(LOCK):
        print('LOCKED before the start')
        return 5
    if os.path.exists(STOP):
        print('STOP before the start')
        return 4
    t0 = time.time()
    with open(out, 'wb') as f:
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
        while p.poll() is None:
            hit = 5 if os.path.exists(LOCK) else (4 if os.path.exists(STOP) else 0)
            if hit:
                subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)], capture_output=True)
                p.wait()
                print('KILLED by %s after %.1f s' % ('the lock' if hit == 5 else 'the stop file', time.time() - t0))
                return hit
            time.sleep(0.5)
    print('rc %d wall %.1f s' % (p.returncode, time.time() - t0))
    return p.returncode


if __name__ == '__main__':
    sys.exit(main())
