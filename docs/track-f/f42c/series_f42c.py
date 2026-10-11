"""Track F link F42c (HPP-781; ROADMAP s122 item 694 (g)(6)): the series form of the caches (seal section 2).  The caches _ShaderCache,
_ShaderSeeds, _PipelineCache and GLCache are copied once before f20_v and returned once by the call f42c_ret; f20_hb and f20_w run 'on the
same caches' (item 694 (g)(6)): the state of the emulator caches before the tag must equal the state after the previous tag of the series.

    python series_f42c.py same <cache_before.tsv> <last_after.tsv>
        compares the lines of the labels _ShaderCache, _ShaderSeeds, _PipelineCache (manifest_fs4c.py tsv form); prints
        'same caches EQUAL files <n>' (exit 0) or 'same caches DIFFER only-before <a> only-after <b>' with the first 5 of each (exit 1);
        a second line - the GLCache row 'GLCache row EQUAL|DIFFER only-before <a> only-after <b>' (never a gate: the driver cache of
        the machine is written by any Vulkan process).  A missing file - 'same caches MISSING <path>' (exit 2).
    python series_f42c.py sizes <tsv>      bytes per label, one line 'sizes <label>=<bytes> ...'
ASCII only."""
import sys

EMU = ('_ShaderCache', '_ShaderSeeds', '_PipelineCache')


def lines(path, labels):
    out = []
    for l in open(path, 'rb').read().decode('ascii', 'replace').splitlines():
        if l.split('\t', 1)[0] in labels:
            out.append(l)
    return out


def diff(a, b):
    sa, sb = set(a), set(b)
    return sorted(sa - sb), sorted(sb - sa)


def main(argv):
    if len(argv) == 3 and argv[0] == 'same':
        import os
        for p in argv[1:]:
            if not os.path.exists(p):
                print('same caches MISSING %s' % p)
                return 2
        a, b = lines(argv[1], EMU), lines(argv[2], EMU)
        ob, oa = diff(a, b)
        if not ob and not oa and a == b:
            print('same caches EQUAL files %d' % len(a))
            rc = 0
        else:
            print('same caches DIFFER only-before %d only-after %d' % (len(ob), len(oa)))
            for l in ob[:5]:
                print('  before-only %s' % l[:200])
            for l in oa[:5]:
                print('  after-only %s' % l[:200])
            rc = 1
        ga, gb = lines(argv[1], ('GLCache',)), lines(argv[2], ('GLCache',))
        gob, goa = diff(ga, gb)
        print('GLCache row %s only-before %d only-after %d (row, not a gate)' % ('EQUAL' if ga == gb else 'DIFFER', len(gob), len(goa)))
        return rc
    if len(argv) == 2 and argv[0] == 'sizes':
        s = {}
        for l in open(argv[1], 'rb').read().decode('ascii', 'replace').splitlines():
            p = l.split('\t')
            if len(p) >= 3:
                try:
                    s[p[0]] = s.get(p[0], 0) + int(p[2])
                except ValueError:
                    pass
        print('sizes ' + ' '.join('%s=%d' % (k, s[k]) for k in sorted(s)))
        return 0
    print('usage: series_f42c.py same <before.tsv> <last_after.tsv> | sizes <tsv>')
    return 9


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
