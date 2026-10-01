# S5d (Red Team): own check of the S6 build tree C:/kyty/s288/wt_s5c against 4fc501f4 + patch.
# (1) every tracked file of the applied tree 142e3f13 (4fc501f4 + pcw_on_4fc501f4.patch): worktree bytes with CR removed == blob;
#     files that differ only by CR are listed; (2) submodules: every file of the gitlink tree in the worktree, blob equal
#     (CR-insensitive count printed), extra files counted; (3) own translator signature of the worktree (generate_version.cmake rule).
import hashlib, os, subprocess, sys
REPO = 'C:/kyty/KytyPS5'; WT = 'C:/kyty/s288/wt_s5c'; TREE = sys.argv[1]
def git(*a, cwd=REPO):
    return subprocess.run(['git', '-C', cwd] + list(a), capture_output=True, check=True).stdout
def blob_sha(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()
ls = git('ls-tree', '-r', '-z', TREE).split(b'\0')
n = same = cr_only = diff = missing = 0; cr_files = []; bad = []; subs = []
for e in ls:
    if not e: continue
    meta, path = e.split(b'\t', 1); mode, typ, sha = meta.split(); path = path.decode()
    if typ == b'commit': subs.append((path, sha.decode())); continue
    n += 1; p = os.path.join(WT, path)
    if not os.path.isfile(p): missing += 1; bad.append('MISSING ' + path); continue
    data = open(p, 'rb').read()
    if blob_sha(data) == sha.decode(): same += 1
    elif blob_sha(data.replace(b'\r\n', b'\n')) == sha.decode(): cr_only += 1; cr_files.append(path)
    else: diff += 1; bad.append('DIFF ' + path)
print('tree', TREE, 'files', n, 'equal', same, 'cr_only', cr_only, 'diff', diff, 'missing', missing)
for b in bad[:20]: print(' ', b)
print('cr_only files:', len(cr_files))
open('C:/kyty/s288/s5d/cr_only_files.txt', 'w').write('\n'.join(sorted(cr_files)) + '\n')
SIGSET = lambda f: (f.startswith('src/graphics/shader/') and os.path.splitext(f)[1] in ('.cpp', '.h', '.inc')) or f in (
    'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 'src/graphics/guest_gpu/gpu_format.h', 'src/graphics/guest_gpu/gpu_defs.h')
print('cr_only in signature set:', sum(1 for f in cr_files if SIGSET(f)), 'outside:', [f for f in cr_files if not SIGSET(f)])
crlf27 = [l.split('\t')[0] for l in open('C:/kyty/s288/s5c/crlf27.txt', encoding='utf-8') if l.strip()]
print('cr_only == crlf27 list:', sorted(cr_files) == sorted(crlf27))
# raw string literals in the CR-only files (the only place CRLF could change compiled bytes)
raw = [f for f in cr_files if b'R"' in open(os.path.join(WT, f), 'rb').read()]
print('cr_only files with R" :', raw)
for path, sha in subs:
    sroot = os.path.join(REPO, path)
    try:
        sl = git('ls-tree', '-r', '-z', sha, cwd=sroot).split(b'\0')
    except subprocess.CalledProcessError:
        print('sub', path, sha[:8], 'CANNOT LIST'); continue
    m = eq = eqcr = df = ms = 0; want = set()
    for e in sl:
        if not e: continue
        meta, p2 = e.split(b'\t', 1); mode, typ, bsha = meta.split(); p2 = p2.decode()
        if typ != b'blob': continue
        m += 1; want.add(p2.replace('/', os.sep)); fp = os.path.join(WT, path, p2)
        if not os.path.isfile(fp): ms += 1; continue
        data = open(fp, 'rb').read()
        if blob_sha(data) == bsha.decode(): eq += 1
        elif blob_sha(data.replace(b'\r\n', b'\n')) == bsha.decode(): eqcr += 1
        else: df += 1
    extra = 0; extras = []
    for d, ds, fs in os.walk(os.path.join(WT, path)):
        if '.git' in ds: ds.remove('.git')
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), os.path.join(WT, path))
            if rel not in want: extra += 1; extras.append(rel)
    print('sub', path, sha[:8], 'files', m, 'equal', eq, 'cr_only', eqcr, 'diff', df, 'missing', ms, 'extra', extra, extras[:3])
