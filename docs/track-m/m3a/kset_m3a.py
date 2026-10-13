"""M3a (HPP-842; ROADMAP item 761 (d)(1)): compare two cache manifests of manifest_fs4c.py on a set of labels.
The K0 invariant of the series (seal pred.md section 5): between tags the live caches of the emulator are the copy K0 taken before the
first tag; the gate compares the four emulator labels only (_ShaderCache, _ShaderSeeds, _PipelineCache, _SaveData); GLCache (the driver
cache of the whole user, other programs write it) is a row.
usage: python kset_m3a.py cmp4 <a.tsv> <b.tsv>     exit 0 'KSET EQUAL4 files <n> ...' / 1 'KSET DIFFER4 ...'; the GLCache row after
       python kset_m3a.py relabel <in.tsv> <out.tsv>  (fixtures only) identity copy
ASCII only."""
import sys

EMU4 = ('_ShaderCache', '_ShaderSeeds', '_PipelineCache', '_SaveData')


def load(p):
    out = {}
    for line in open(p, 'rb').read().decode('utf-8', 'replace').split('\n'):
        if not line:
            continue
        lab = line.split('\t', 1)[0]
        out.setdefault(lab, set()).add(line)
    return out


def asc(s):
    return s.encode('ascii', 'backslashreplace').decode('ascii')


def main(argv):
    if len(argv) == 3 and argv[0] == 'cmp4':
        a, b = load(argv[1]), load(argv[2])
        da, db = set(), set()
        n = 0
        for lab in EMU4:
            la, lb = a.get(lab, set()), b.get(lab, set())
            n += len(la)
            da |= la - lb
            db |= lb - la
        ga, gb = a.get('GLCache', set()), b.get('GLCache', set())
        grow = 'GLCache row: only-a %d only-b %d' % (len(ga - gb), len(gb - ga))
        if not da and not db:
            print('KSET EQUAL4 files %d; %s' % (n, grow))
            return 0
        print('KSET DIFFER4 only-a %d only-b %d; %s' % (len(da), len(db), grow))
        for x in sorted(da)[:5]:
            print('  a-only %s' % asc(x)[:200])
        for x in sorted(db)[:5]:
            print('  b-only %s' % asc(x)[:200])
        return 1
    print(__doc__.split('\n')[4])
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
