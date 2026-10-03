"""F11f (HPP-468, ROADMAP s122 item 376 (z); port of F10e manifest_f10e.py): manifest sha256 of every file of the caches before the tag and after their return.
usage: python manifest_f11f.py <out.tsv> <label>=<dir> [<label>=<dir> ...]
       python manifest_f11f.py --cmp <before.tsv> <after.tsv>
Manifest: one line per regular file '<label>\t<path relative to the dir, forward slashes>\t<size>\t<sha256>', sorted; a missing dir is the
line '<label>\t<MISSING>\t0\t-'.  Prints 'manifest <out> files <n> bytes <b> listsha <sha256 of the tsv bytes>'.
--cmp prints 'manifest cmp EQUAL files <n> listsha <sha>' when the two tsv are byte-equal, else 'manifest cmp DIFFER' with the counts of
lines only before / only after and the first 5 of each; exit 0 EQUAL, 1 DIFFER.  ASCII output only (paths are ASCII-escaped)."""
import hashlib, os, sys


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def manifest(pairs):
    lines = []
    for pair in pairs:
        label, d = pair.split('=', 1)
        if not os.path.isdir(d):
            lines.append('%s\t<MISSING>\t0\t-' % label)
            continue
        for root, dirs, files in os.walk(d):
            dirs.sort()
            for fn in sorted(files):
                p = os.path.join(root, fn)
                if not os.path.isfile(p) or os.path.islink(p):
                    continue
                rel = os.path.relpath(p, d).replace(os.sep, '/')
                lines.append('%s\t%s\t%d\t%s' % (label, rel, os.path.getsize(p), sha_file(p)))
    lines.sort()
    return lines


def asc(s):
    return s.encode('ascii', 'backslashreplace').decode('ascii')


def main(argv):
    if argv and argv[0] == '--cmp':
        a = open(argv[1], 'rb').read()
        b = open(argv[2], 'rb').read()
        if a == b:
            n = len([x for x in a.split(b'\n') if x])
            print('manifest cmp EQUAL files %d listsha %s' % (n, hashlib.sha256(a).hexdigest()))
            return 0
        la = set(a.decode('utf-8').split('\n')) - {''}
        lb = set(b.decode('utf-8').split('\n')) - {''}
        oa, ob = sorted(la - lb), sorted(lb - la)
        print('manifest cmp DIFFER only-before %d only-after %d' % (len(oa), len(ob)))
        for x in oa[:5]:
            print('  before-only %s' % asc(x))
        for x in ob[:5]:
            print('  after-only %s' % asc(x))
        return 1
    if len(argv) < 2:
        print(__doc__.split('\n')[1])
        return 2
    out = argv[0]
    lines = manifest(argv[1:])
    data = ('\n'.join(lines) + '\n').encode('utf-8')
    with open(out, 'wb') as f:
        f.write(data)
    nbytes = sum(int(x.split('\t')[2]) for x in lines)
    print('manifest %s files %d bytes %d listsha %s' % (asc(out), len(lines), nbytes, hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
