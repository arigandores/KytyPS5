"""Session 142 step 0: copy the step's files into C:/kyty/KytyPS5/docs/session-142/step0/ (byte copies, LF kept) and scan the
copies (launch_run.py stays local: a private expression hits it; its sha is in the seal) (and the whole KytyPS5 tree by git grep) with the private expressions of C:/kyty/scrub/checks.txt.  The expressions
are never printed; only their numbers and hit counts.  ASCII output."""
import hashlib
import os
import re
import shutil
import subprocess

SRC = 'C:/kyty/s142'
DST = 'C:/kyty/KytyPS5/docs/session-142/step0'
GIT = 'C:/Program Files/Git/cmd/git.exe'
FILES = ['go142a.sh', 'sc142.py', 'test_sc142.py', 'mut_sc142.py', 'test_go142a.py', 'sheet142.py', 'enter_scene.py',
         'idle142.py', 'procload.py', 'run_safety99.py', 'gates_default.txt', 'pred/01_sc142.md', 'FACTS.md',
         'mut_sc142.txt', 'mut_sc142.add.txt', 'mut_run.log', 'mut_run.add.log',
         'step0/times.txt', 'step0/calib142.out.txt', 'step0/test_sc142.out.txt', 'step0/test_go142a.out.txt',
         'step0/checkseal142.out.txt', 'step0/dry142.out.txt', 'step0/addonly142.py', 'step0/addonly142.out.txt',
         'step0/mkseal142.py', 'step0/pred_template.md', 'step0/togit142.py', 'step0/v1/test_sc142.py',
         'step0/toolcheck/glitch_eatl122.txt']
exprs = [l.strip() for l in open('C:/kyty/scrub/checks.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
rx = []
for e in exprs:
    try:
        rx.append(re.compile(e, re.I))
    except re.error:
        rx.append(re.compile(re.escape(e), re.I))
hits = 0
for f in FILES:
    s = os.path.join(SRC, f)
    d = os.path.join(DST, f)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copyfile(s, d)
    text = open(d, 'rb').read().decode('utf-8', 'replace')
    for i, r in enumerate(rx, 1):
        n = len(r.findall(text))
        if n:
            hits += n
            print('HIT expr #%d in %s: %d' % (i, f, n))
    print('copied %s sha256 %s' % (f, hashlib.sha256(open(d, 'rb').read()).hexdigest()[:16]))
print('copies %d, private hits in the copies %d' % (len(FILES), hits))
tree = 0
for i, e in enumerate(exprs, 1):
    out = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'grep', '-I', '-i', '-l', '-E', e], capture_output=True)
    n = len([l for l in out.stdout.decode('utf-8', 'replace').split('\n') if l.strip()])
    if n:
        tree += 1
        print('tree expr #%d: %d file(s)' % (i, n))
print('tree expressions with hits %d of %d' % (tree, len(exprs)))
