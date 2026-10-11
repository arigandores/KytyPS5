# F44b (HPP-792): copy of docs/track-f/f43a/wait_f43a.py (form of ROADMAP p.698(e)).
# F43a: wait (<= LIMIT s) until there is neither the lock nor any process whose command line names the gate script,
# for CLEAR consecutive seconds. The gate name is built at run time so that this process does not match other watchers.
import os, sys, time, psutil
LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 560
CLEAR = 20
NEEDLE = 'procload' + '.py'
own = os.getpid()
t0 = time.time()
clear = 0
hits = []
while time.time() - t0 < LIMIT:
    hits = [p.info['pid'] for p in psutil.process_iter(['pid', 'cmdline'])
            if p.info['pid'] != own and NEEDLE in ' '.join(p.info['cmdline'] or [])]
    busy = os.path.exists('C:/kyty/SEALED_RUN.lock') or bool(hits)
    clear = 0 if busy else clear + 2
    if clear >= CLEAR:
        break
    time.sleep(2)
print(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'clear', clear >= CLEAR, 'hits', hits,
      'lock', os.path.exists('C:/kyty/SEALED_RUN.lock'))
sys.exit(0 if clear >= CLEAR else 1)
