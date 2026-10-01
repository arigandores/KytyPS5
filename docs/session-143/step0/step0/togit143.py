"""Session 143 step 0 (HPP-297): copy the step's files into C:/kyty/KytyPS5/docs/session-142/step0/ (byte copies, LF kept) and scan the
copies (launch_run.py stays local: a private expression hits it; its sha is in the seal; the CPU smoke step0/smoke stays local: it names the processes of the machine) (and the whole KytyPS5 tree by git grep) with the private expressions of C:/kyty/scrub/checks.txt.  The expressions
are never printed; only their numbers and hit counts.  ASCII output."""
import hashlib
import os
import re
import shutil
import subprocess

SRC = 'C:/kyty/s143'
DST = 'C:/kyty/KytyPS5/docs/session-143/step0'
GIT = 'C:/Program Files/Git/cmd/git.exe'
FILES = ['go143a.sh', 'sc143.py', 'test_sc143.py', 'mut_sc143.py', 'test_go143a.py', 'fgcpu143.py', 'test_fgcpu143.py',
         'sheet142.py', 'enter_scene.py', 'idle142.py', 'procload.py', 'run_safety99.py', 'gates_default.txt', 'pred/01_sc143.md',
         'FACTS.md', 'mut_sc143.txt', 'mut_run.log', 'step0/times.txt', 'step0/regress142.out.txt', 'step0/calib143.out.txt',
         'step0/check1b143.out.txt', 'step0/test_sc143.out.txt', 'step0/test_go143a.out.txt', 'step0/test_fgcpu143.out.txt',
         'step0/checkseal143.out.txt', 'step0/dry143.out.txt', 'step0/mkseal143.out.txt', 'step0/partB.py.txt',
         'step0/asm_test143.py', 'step0/mk_mut143.py', 'step0/mkseal143.py', 'step0/togit143.py', 'step0/v1/test_sc143.py']
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
