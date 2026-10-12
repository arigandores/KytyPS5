# Track F link F47i (HPP-826; ROADMAP s122 item 740 (v)(3), 742 (e), 744 (g)-(d)): copy of the F47d (HPP-809) file mfsub_f47d.py with the names moved (f47d -> f47i, F47D -> F47I, F47d -> F47i, HPP-809 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 702 (g)): copy of the F44c (HPP-793) file mfsub_f44c.py with the names moved (f44c -> f47i, F44C -> F47I, F44c -> F47i, HPP-793 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 698 (d)(4)): copy of the F38c (HPP-765) file mfsub_f38c.py with the names moved (f38c -> f47i, F38C -> F47I, F38c -> F47i, HPP-765 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 691 (d)(4)): copy of the FS12c (HPP-752) file mfsub_fs12c.py with the names moved (fs12c -> f47i, FS12C -> F47I, FS12c -> F47i, HPP-752 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file mfsub_f33e.py with the names moved (f33e -> f47i, F33E -> F47I, F33e -> F47i, HPP-746 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file mfsub_f34c.py with the names moved (f34c -> f47i, F34C -> F47I, F34c -> F47i, HPP-740 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 673 (z)(2), 674, 676): copy of the FS11c (HPP-716) file mfsub_fs11c.py with the names moved (fs11c -> f47i, FS11C -> F47I, HPP-716 -> HPP-826); no change of meaning.
"""Track F link FS11c (HPP-826; ROADMAP s122 item 606 (v)(3)): after the GLCache merge return of a tag that saw a user VM - every line of
the manifest before is in the manifest after (nothing lost or changed), and the lines only after are GLCache files (user files kept).
usage: python mfsub_f47i.py <before.tsv> <after.tsv>   rc 0 'SUBSET OK extra <n>' / rc 1 'SUBSET FAIL ...'.  ASCII only."""
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
