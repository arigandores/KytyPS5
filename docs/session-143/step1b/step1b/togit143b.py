"""Session 143 link 1b (HPP-321): copy the link's files into C:/kyty/KytyPS5/docs/session-143/step1b/ (byte copies, LF kept)
and scan the copies (and the whole KytyPS5 tree by git grep) with the private expressions of C:/kyty/scrub/checks.txt.  The
CPU smoke step1b/smoke stays local (it names the processes of the machine).  The expressions are never printed; only their
numbers and hit counts.  ASCII output."""
import hashlib
import os
import re
import shutil
import subprocess

SRC = 'C:/kyty/s143'
DST = 'C:/kyty/KytyPS5/docs/session-143/step1b'
GIT = 'C:/Program Files/Git/cmd/git.exe'
FILES = ['go143a.sh', 'sc143.py', 'test_sc143.py', 'mut_sc143.py', 'test_go143a.py', 'fgcpu143.py', 'test_fgcpu143.py',
         'cachemf143.py', 'lockcheck143.py', 'test_tools143.py', 'step2/next_one.sh', 'step2/call_one.sh', 'step2/wait_one.sh',
         'pred/02_sc143.md', 'FACTS.md', 'mut_sc143.txt', 'mut_run.log', 'step1b/times.txt', 'step1b/regress142.out.txt',
         'step1b/calib143.out.txt', 'step1b/check1b143.out.txt', 'step1b/test_sc143.out.txt', 'step1b/test_go143a.out.txt',
         'step1b/test_fgcpu143.out.txt', 'step1b/test_tools143.out.txt', 'step1b/checkseal143.out.txt', 'step1b/dry143.out.txt',
         'step1b/mkseal143b.out.txt', 'step1b/mut_run.aborted1.log', 'step1b/partC.py.txt', 'step1b/patch_test1.py',
         'step1b/patch_test2.py', 'step1b/patch_test3.py', 'step1b/patch_test4.py', 'step1b/patch_go.py',
         'step1b/patch_testgo.py', 'step1b/mk_mut143b.py', 'step1b/mkseal143b.py', 'step1b/togit143b.py',
         'step1b/facts_step1b.md', 'step1b/v1/sc143.py', 'step1b/v1/test_sc143.py', 'step1b/v1/mut_sc143.py']
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
