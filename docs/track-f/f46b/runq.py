# Track F, F46b (HPP-799): run one step under the watchdog watch_f46b.py when neither the lock nor a gate process
# (argv ending with the gate script; its name is assembled at run time, item 698(e)) is there; a step the watchdog
# refuses (8) or kills by the gate process (7) is repeated after the next free moment. Gives up after `budget` seconds.
#   python runq.py <budget s> <tag> -- <command> [args...]
# Exit: the step's code; 3 - the lock (nothing more runs, rule 27); 9 - the budget ran out before a clean run.
import os
import subprocess
import sys
import time

import psutil

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
NAME = 'procload' + '.py'
HERE = os.path.dirname(os.path.abspath(__file__))


def gate_alive():
    own = os.getpid()
    for p in psutil.process_iter(['pid', 'cmdline']):
        if p.info['pid'] == own:
            continue
        for a in p.info['cmdline'] or []:
            a = a.replace(chr(92), '/')
            if a == NAME or a.endswith('/' + NAME):
                return True
    return False


def main():
    budget = float(sys.argv[1])
    tag = sys.argv[2]
    cmd = sys.argv[sys.argv.index('--') + 1:]
    t0 = time.time()
    tries = 0
    while time.time() - t0 < budget:
        if os.path.exists(LOCK) or os.path.exists(STOP):
            print('runq: lock or STOP - stop')
            return 3
        if gate_alive():
            time.sleep(2)
            continue
        tries += 1
        left = max(30, int(budget - (time.time() - t0)))
        rc = subprocess.run([sys.executable, os.path.join(HERE, 'watch_f46b.py'), '--limit', str(left), '--tag',
                             '%s try %d' % (tag, tries), '--'] + cmd).returncode
        print('runq: %s try %d rc=%d' % (tag, tries, rc))
        if rc in (7, 8):
            continue
        return rc
    print('runq: budget out')
    return 9


if __name__ == '__main__':
    sys.exit(main())
