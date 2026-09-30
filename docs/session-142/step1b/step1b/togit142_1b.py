"""Link 1b (HPP-282): copy the link's files into C:/kyty/KytyPS5/docs/session-142/step1b/ (byte copies) and scan the copies
with the private expressions of C:/kyty/scrub/checks.txt (never printed; numbers and hit counts only), then the whole KytyPS5
tree by git grep.  ASCII output."""
import hashlib
import os
import re
import shutil
import subprocess

SRC = 'C:/kyty/s142'
DST = 'C:/kyty/KytyPS5/docs/session-142/step1b'
GIT = 'C:/Program Files/Git/cmd/git.exe'
FILES = ['sc142.py', 'go142a.sh', 'test_sc142.py', 'test_go142a.py', 'mut_sc142.py', 'pred/02_sc142.md', 'pred/01_sc142.md',
         'FACTS.md', 'mut_sc142_1b.txt', 'mut_sc142_1b.add.txt', 'mut_run1b.log', 'mut_run1b.add.log',
         'step1b/times.txt', 'step1b/facts_step1b.md', 'step1b/test_sc142.out.txt', 'step1b/test_go142a.out.txt',
         'step1b/calib142_1b.out.txt', 'step1b/check1b.out.txt', 'step1b/checkseal02.out.txt', 'step1b/mkseal02.out.txt',
         'step1b/dry02.out.txt', 'step1b/addonly142_1b.py', 'step1b/addonly142_1b.out.txt', 'step1b/v1/test_sc142.py',
         'step1b/v0/sc142.py', 'step1b/v0/go142a.sh', 'step1b/v0/01_sc142.md', 'step1b/mk_pred02.py',
         'step1b/pred02_template.md', 'step1b/mk_mut1b.py', 'step1b/mut_new.py', 'step1b/fx1b_block.py',
         'step1b/patch_test1b.py', 'step1b/togit142_1b.py']
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
    out = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'grep', '-I', '-i', '-c', '-E', e], capture_output=True, text=True,
                         encoding='utf-8', errors='replace').stdout
    n = sum(int(x.rsplit(':', 1)[1]) for x in out.splitlines() if ':' in x)
    tree += n
    if n:
        print('TREE HIT expr #%d: %d lines' % (i, n))
print('git grep over the tree: %d hit lines' % tree)
