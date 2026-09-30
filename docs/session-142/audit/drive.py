# run aud142.py over a jobs file, N in parallel (subprocess; no shared code with sc142.py)
import sys, subprocess
jobs = [l.split() for l in open(sys.argv[1]) if l.strip()]
N = int(sys.argv[2])
out = open(sys.argv[3], 'w')
running = []
rcs = []
while jobs or running:
    while jobs and len(running) < N:
        j = jobs.pop(0)
        running.append((j, subprocess.Popen([sys.executable, 'C:/kyty/s142/step3/aud142.py'] + j, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)))
    j, p = running.pop(0)
    o, _ = p.communicate()
    out.write(o.decode('ascii', 'replace'))
    rcs.append((j[1], p.returncode))
out.close()
print(rcs)
sys.exit(0 if all(r == 0 for _, r in rcs) else 1)
