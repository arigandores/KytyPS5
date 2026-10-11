# F44c (HPP-793): general rule 30 window - wait (<= LIMIT s) until the foreign lock disappears, then (within 20 s of the release) run ONE
# work command with a hard limit of 55 s.  The gate name is not in this command line.  ASCII only.
# usage: python win_f44c.py <limit s> <bash command>
import os, subprocess, sys, time
LIMIT = float(sys.argv[1])
CMD = sys.argv[2]
L = 'C:/kyty/SEALED_RUN.lock'
t0 = time.time()
seen = os.path.exists(L)
while time.time() - t0 < LIMIT:
    if not os.path.exists(L):
        break
    time.sleep(1)
if os.path.exists(L):
    print('still locked after %.0f s' % LIMIT)
    sys.exit(3)
if os.path.exists('C:/kyty/f287/STOP'):
    print('STOP file')
    sys.exit(4)
ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
print('window open %s (lock seen at start %s)' % (ts, seen))
sys.stdout.flush()
try:
    r = subprocess.run(['C:/Program Files/Git/bin/bash.exe', '-c', CMD], timeout=55)
    rc = r.returncode
except subprocess.TimeoutExpired:
    rc = 'TIMEOUT55'
print('window work rc %s end %s' % (rc, time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
