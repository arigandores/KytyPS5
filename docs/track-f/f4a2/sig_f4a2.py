# F4a2 (HPP-346, p.262(v)): find working-tree bytes of the 4fc501f4 signature set that give KYTY_SHADER_SOURCE_HASH
# 699c1e4b (the signature of 9235a7ac and of the recipe file). Model of generate_version.cmake: SHA1 of the
# concatenation "<sha1 of file bytes>\n" over the sorted file list (src/graphics/shader/**/*.{cpp,h,inc} + 3 extra).
# Each file's bytes: blob of 4fc501f4 as LF or CRLF. Files unchanged since 4fc501f4 take the form of the current
# main working tree (if it is one of the two); files changed since are enumerated over both forms.
# Usage: sig_f4a2.py [--write <worktree root>]   (--write: write the found bytes into that tree's files)
import hashlib, subprocess, sys, os, re, itertools
REPO = 'C:/kyty/KytyPS5'
BASE = '4fc501f4'
TARGET = '699c1e4b7db359067b461e029b913c4b6e78dc90'
EXTRA = ['src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 'src/graphics/guest_gpu/gpu_format.h',
         'src/graphics/guest_gpu/gpu_defs.h']


def git(*a):
    return subprocess.run(['git', '-C', REPO] + list(a), capture_output=True, check=True).stdout


def files_at(rev):
    out = git('ls-tree', '-r', '--name-only', rev, 'src/graphics/shader').decode().split('\n')
    return sorted([f for f in out if f and os.path.splitext(f)[1] in ('.cpp', '.h', '.inc')] + EXTRA)


def blob(rev, f):
    r = subprocess.run(['git', '-C', REPO, 'show', rev + ':' + f], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def crlf(x):
    return re.sub(rb'(?<!\r)\n', b'\r\n', x)


def sig(byts):
    d = ''.join(hashlib.sha1(b).hexdigest() + '\n' for b in byts)
    return hashlib.sha1(d.encode()).hexdigest()


fs = files_at(BASE)
print('files', len(fs))
fixed, var = {}, []
amb = 0
for f in fs:
    b4 = blob(BASE, f)
    bh = blob('HEAD', f)
    wt = open(REPO + '/' + f, 'rb').read() if os.path.exists(REPO + '/' + f) else None
    if b4 == bh and wt is not None and wt in (b4, crlf(b4)):
        fixed[f] = wt
    else:
        var.append(f)
        if b4 == bh:
            amb += 1
print('unchanged with known form', len(fixed), 'of which CRLF', sum(1 for f in fixed if fixed[f] != blob(BASE, f)))
print('enumerated (changed since %s or unknown form)' % BASE, len(var), 'unknown-form unchanged', amb)
for f in var:
    print('  var', f)
print('LF model', sig([blob(BASE, f) for f in fs]))
print('CRLF model', sig([crlf(blob(BASE, f)) for f in fs]))
found = None
if len(var) <= 20:
    forms = {f: (blob(BASE, f), crlf(blob(BASE, f))) for f in var}
    for combo in itertools.product((0, 1), repeat=len(var)):
        m = dict(fixed)
        for f, c in zip(var, combo):
            m[f] = forms[f][c]
        s = sig([m[f] for f in fs])
        if s == TARGET:
            found = (combo, m)
            print('FOUND', TARGET, 'combo', ''.join('C' if c else 'L' for c in combo))
            break
    if found is None:
        print('NOT FOUND over', 2 ** len(var), 'combinations')
else:
    print('too many variable files to enumerate')
if found and len(sys.argv) > 2 and sys.argv[1] == '--write':
    root = sys.argv[2]
    changed = 0
    for f in fs:
        p = root + '/' + f
        cur = open(p, 'rb').read()
        if cur != found[1][f]:
            open(p, 'wb').write(found[1][f])
            changed += 1
    print('wrote', changed, 'files under', root)
    print('tree signature now', sig([open(root + '/' + f, 'rb').read() for f in fs]))
