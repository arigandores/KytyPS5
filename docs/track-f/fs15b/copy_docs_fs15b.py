# FS15b (HPP-821, Red Team): copies the link files to docs/track-f/fs15b/ (LF) with the home directory replaced by <HOME>.
import os, sys

d = 'C:/kyty/KytyPS5/docs/track-f/fs15b'
os.makedirs(d, exist_ok=True)
os.chdir('C:/kyty/f287/fs15b')
user = os.environ.get('USERNAME', '')
BS = chr(92)
files = ['review_git_fs15b.py', 'review_git.out.txt', 'knobs_fs15b.py', 'knobs_6beb3b73.out.txt', 'knobs_91b74d09.out.txt',
         'knobs_eb7e8b91.out.txt', 'pediff3.py', 'pediff3r_fs15b.py', 'pediff3r_emu.out.txt', 'pediff3r_neg.out.txt',
         'strings.out.txt', 'sha_fs15b.txt', 'gate_order_wt.out.txt', 'mk_wt_fs15b.sh', 'build_fs15b.cmd', 'bstep.sh', 'sstep.sh',
         'api_chk.sh', 'watch_fs15b.py', 'mk_wt.log', 'build_cfg.log', 'build_ver.log', 'build_emu.log', 'facts_fs15b.py',
         'facts_fs15b.tmpl.md', 'copy_docs_fs15b.py']
pats = []
if user:
    for sep in ('/', BS, BS + BS):
        for root in ('C:', 'c:'):
            for us in ('Users', 'users'):
                for u in (user, user.lower()):
                    pats.append((root + sep + us + sep + u).encode())
hits = 0
left = []
for f in files:
    b = open(f, 'rb').read().replace(b'\r\n', b'\n')
    for p in pats:
        n = b.count(p)
        if n:
            hits += n
            b = b.replace(p, b'<HOME>')
    if user and user.lower().encode() in b.lower():
        left.append(f)
    open(os.path.join(d, f), 'wb').write(b)
r = open('fs15b-review.md', 'rb').read().replace(b'\r\n', b'\n')
open('C:/kyty/KytyPS5/docs/track-f/fs15b-review.md', 'wb').write(r)
print('copied', len(files), 'home replaced', hits, 'user left in', left)
sys.exit(1 if left else 0)
