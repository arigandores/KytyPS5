"""F23c (HPP-587): copy the link files C:/kyty/f287/f23c/ -> KytyPS5 docs/track-f/f23c/ (no worktree, build tree, textures,
binaries) and the report -> docs/track-f/f23c.md."""
import os
import shutil

src = 'C:/kyty/f287/f23c/'
dst = 'C:/kyty/KytyPS5/docs/track-f/f23c/'
skip_dirs = {'wt', 'build', '__pycache__'}
n = 0
tot = 0
for d, dirs, fs in os.walk(src):
    dirs[:] = [x for x in dirs if x not in skip_dirs]
    rel = os.path.relpath(d, src).replace(chr(92), '/')
    for f in fs:
        if f.endswith(('.r8', '.exe', '.tmp', '.obj', '.pdb', '.lib', '.exp', '.bin')) or f == 'f23c.md':
            continue
        p = os.path.join(d, f)
        q = os.path.join(dst, f) if rel == '.' else os.path.join(dst, rel, f)
        os.makedirs(os.path.dirname(q), exist_ok=True)
        shutil.copyfile(p, q)
        n += 1
        tot += os.path.getsize(p)
shutil.copyfile(src + 'f23c.md', 'C:/kyty/KytyPS5/docs/track-f/f23c.md')
print('copied', n, 'files', tot, 'bytes')
