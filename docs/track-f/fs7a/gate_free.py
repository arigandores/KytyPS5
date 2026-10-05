# F19c2: exit 0 if no gate process (an argument ends with procload.py, the api_chk.sh form), else 1 and the pids.
import os, sys, psutil
NEEDLE = 'procload' + '.py'
hits = []
for p in psutil.process_iter(['pid']):
    if p.info['pid'] == os.getpid():
        continue
    try:
        cl = p.cmdline()
    except (psutil.Error, OSError):
        continue
    if any(a.replace(chr(92), '/').endswith('/' + NEEDLE) or a == NEEDLE for a in cl):
        hits.append(p.info['pid'])
print('gate pids', hits)
sys.exit(1 if hits else 0)
