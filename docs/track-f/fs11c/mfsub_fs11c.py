"""Track F link FS11c (HPP-716; ROADMAP s122 item 606 (v)(3)): after the GLCache merge return of a tag that saw a user VM - every line of
the manifest before is in the manifest after (nothing lost or changed), and the lines only after are GLCache files (user files kept).
usage: python mfsub_fs11c.py <before.tsv> <after.tsv>   rc 0 'SUBSET OK extra <n>' / rc 1 'SUBSET FAIL ...'.  ASCII only."""
import sys


def main(argv):
    a = set(open(argv[0], 'rb').read().decode('utf-8').split('\n')) - {''}
    b = set(open(argv[1], 'rb').read().decode('utf-8').split('\n')) - {''}
    lost = sorted(a - b)
    extra = sorted(b - a)
    bad = [x for x in extra if not x.startswith('GLCache\t')]
    if lost or bad:
        print('SUBSET FAIL lost %d extra-not-GLCache %d' % (len(lost), len(bad)))
        for x in (lost + bad)[:5]:
            print('  %s' % x.encode('ascii', 'backslashreplace').decode('ascii'))
        return 1
    print('SUBSET OK extra %d' % len(extra))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
