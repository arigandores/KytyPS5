"""Session 142 step 1 (Red Team, HPP-278): append the Step 1 section to C:/kyty/s142/FACTS.md (LF, once), copy the step's
files into C:/kyty/KytyPS5/docs/session-142/step1/ (byte copies) and scan the copies, review142.md and the whole KytyPS5
tree (git grep) with the private expressions of C:/kyty/scrub/checks.txt.  The expressions are never printed; only their
numbers and hit counts.  ASCII output."""
import hashlib
import os
import re
import shutil
import subprocess
import sys

SRC = 'C:/kyty/s142/step1'
DST = 'C:/kyty/KytyPS5/docs/session-142/step1'
REVIEW = 'C:/kyty/KytyPS5/docs/session-142/review142.md'
FACTS = 'C:/kyty/s142/FACTS.md'
SECTION = 'C:/kyty/s142/step1/facts_step1.md'
GIT = 'C:/Program Files/Git/cmd/git.exe'
FILES = ['times.txt', 'refs142_rt.py', 'refs142_rt.out.txt', 'rt142_dl.py', 'rt142_dl.out.txt', 'rt142_ft.py',
         'rt142_ft.out.txt', 'rt142_full.py', 'rt142_full.out.txt', 'rt142_quit.py', 'rt142_quit.out.txt', 'rt142_starts.py',
         'rt142_starts.out.txt', 'rt142_vk.py', 'rt142_vk.out.txt', 'rt_calib.out.txt', 'rt_checkseal.out.txt',
         'rt_test_go142a.out.txt', 'rt_test_sc142.out.txt', 'facts_step1.md', 'togit142_rt.py']

if '--facts' in sys.argv:
    cur = open(FACTS, 'rb').read()
    sec = open(SECTION, 'rb').read()
    if b'## Step 1 ' in cur:
        print('FACTS already has a Step 1 section - not appended')
    else:
        open(FACTS, 'wb').write(cur + (b'' if cur.endswith(b'\n') else b'\n') + b'\n' + sec)
        print('FACTS appended: sha256 %s' % hashlib.sha256(open(FACTS, 'rb').read()).hexdigest())
    sys.exit(0)

exprs = [l.strip() for l in open('C:/kyty/scrub/checks.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
rx = []
for e in exprs:
    try:
        rx.append(re.compile(e, re.I))
    except re.error:
        rx.append(re.compile(re.escape(e), re.I))
os.makedirs(DST, exist_ok=True)
hits = 0
for f in FILES + ['REVIEW']:
    if f == 'REVIEW':
        d = REVIEW
    else:
        d = os.path.join(DST, f)
        shutil.copyfile(os.path.join(SRC, f), d)
    text = open(d, 'rb').read().decode('utf-8', 'replace')
    for i, r in enumerate(rx, 1):
        n = len(r.findall(text))
        if n:
            hits += n
            print('HIT expr #%d in %s: %d' % (i, f, n))
    print('%s %s sha256 %s' % ('checked' if f == 'REVIEW' else 'copied', os.path.basename(d),
                               hashlib.sha256(open(d, 'rb').read()).hexdigest()[:16]))
print('copies %d + review, private hits %d' % (len(FILES), hits))
tree = 0
for i, e in enumerate(exprs, 1):
    out = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'grep', '-I', '-i', '-l', '-E', e], capture_output=True)
    n = len([l for l in out.stdout.decode('utf-8', 'replace').split('\n') if l.strip()])
    if n:
        tree += 1
        print('tree expr #%d: %d file(s)' % (i, n))
print('tree expressions with hits %d of %d' % (tree, len(exprs)))
