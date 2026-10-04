# F22a (HPP-576; copy of f21a/privchk_f22a.py): privacy check of the files prepared for git (general rule 28; item 433(a)(3): packed files are
# checked unpacked).  Every file of <dir> (and the extra files given) is matched against the privacy list (one regular
# expression per line); '.xz' is unpacked in memory.  With --fix the matches in plain text files are replaced by
# <masked> in place (LF kept).  Prints per-file counts and 'PRIVACY OK' / 'PRIVACY FAIL'.
# Usage: python privchk_f22a.py <privacy list> [--fix] <dir> [file ...]
import lzma, os, re, sys

args = sys.argv[1:]
PRIV = [re.compile(l.strip()) for l in open(args[0], encoding='utf-8') if l.strip()]
fix = '--fix' in args
paths = [a for a in args[1:] if a != '--fix']
files = []
for p in paths:
    if os.path.isdir(p):
        for dp, dn, fn in os.walk(p):
            files += [os.path.join(dp, f) for f in sorted(fn)]
    else:
        files.append(p)
bad = 0
for f in files:
    raw = open(f, 'rb').read()
    packed = f.endswith('.xz')
    text = (lzma.decompress(raw) if packed else raw).decode('utf-8', 'replace')
    n = sum(len(p.findall(text)) for p in PRIV)
    if n and fix and not packed:
        for p in PRIV:
            text = p.sub('<masked>', text)
        open(f, 'wb').write(text.encode('utf-8'))
        print('fixed %d in %s' % (n, f))
        n = sum(len(p.findall(text)) for p in PRIV)
    if n:
        print('MATCH %d in %s' % (n, f))
    bad += n
print('files', len(files), 'PRIVACY OK' if bad == 0 else 'PRIVACY FAIL %d' % bad)
sys.exit(1 if bad else 0)
