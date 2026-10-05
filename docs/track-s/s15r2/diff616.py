"""diff616.py - S15r2 (HPP-616), Red Team: own diffs and seal sha checks, no game, read only under C:/kyty (writes only argv[1]).
(1) seal 14 -> 15 -> 16: the lines that differ after the name substitution 14_s/14b_s -> 16_s/16b_s;
(2) the 5 renamed scripts: seal-15 originals (s15a3/orig, checked against the seal: lines of seal 15) vs disk, after the same
    substitution - every remaining differing line;
(3) every seal: line of seal 16 against the disk; the seal: lines 14 -> 16 that changed;
(4) enter_scene_s15.py of seal 14 (s15a2/orig) vs disk: the differing lines.
    python diff616.py <out dir>
"""
import difflib
import hashlib
import pathlib
import sys

R = pathlib.Path('C:/kyty/s288')
OUT = pathlib.Path(sys.argv[1])


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def lines(p):
    return pathlib.Path(p).read_bytes().decode('ascii').split('\n')


def sub(t):
    return t.replace('pred/14b_s.md', 'pred/16b_s.md').replace('pred/14_s.md', 'pred/16_s.md')


def show(tag, a, b, width=200):
    n = 0
    for op in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op[0] == 'equal':
            continue
        n += 1
        print('%s hunk %d %s a[%d:%d] b[%d:%d]' % (tag, n, op[0], op[1] + 1, op[2], op[3] + 1, op[4]))
        for x in a[op[1]:op[2]]:
            print('   - ' + x[:width])
        for x in b[op[3]:op[4]]:
            print('   + ' + x[:width])
    print('%s: %d hunks' % (tag, n))
    return n


s14, s15, s16 = (lines(R / 'pred' / n) for n in ('14_s.md', '15_s.md', '16_s.md'))
print('seal sha256 14 %s 15 %s 16 %s; lines %d %d %d' % (sha(R / 'pred/14_s.md'), sha(R / 'pred/15_s.md'), sha(R / 'pred/16_s.md'),
                                                         len(s14), len(s15), len(s16)))
print('==== (1a) seal 14 -> 15, raw')
show('14->15', s14, s15)
print('==== (1b) seal 15 -> 16 after the substitution 14 -> 16 in 15')
show('15sub->16', [sub(x) for x in s15], s16)
print('==== (1c) names 14_s / 14b_s / 15_s / 15b_s left in seal 16')
for i, x in enumerate(s16):
    for nm in ('14_s.md', '14b_s.md', '15_s.md', '15b_s.md'):
        if nm in x:
            print('  16:%d %s: %s' % (i + 1, nm, x[:220]))
print('==== (3) seal: lines')


def seals(ls):
    d = {}
    for x in ls:
        if x.startswith('seal: '):
            h, p = x[6:].split(' ', 1)
            d[p] = h
    return d


d14, d15, d16 = seals(s14), seals(s15), seals(s16)
print('seal: lines 14 %d 15 %d 16 %d; same path sets %s' % (len(d14), len(d15), len(d16), set(d14) == set(d15) == set(d16)))
bad = 0
for p, h in sorted(d16.items()):
    disk = sha(R / p) if (R / p).exists() else 'MISSING'
    if disk != h:
        bad += 1
        print('  BAD 16 %s: seal %s disk %s' % (p, h[:16], disk[:16]))
    if d14.get(p) != h:
        print('  changed 14 -> 16: %s %s -> %s (15 %s)' % (p, d14.get(p, '-')[:16], h[:16], d15.get(p, '-')[:16]))
print('seal 16 vs disk: %d of %d differ' % (bad, len(d16)))
print('==== (2) the 5 renamed scripts: seal-15 originals vs disk')
for f in ('sc_s15.py', 'go_s15.sh', 'test_sc_s15.py', 'test_go_s15.py', 'mut_sc_s15.py'):
    o = R / 's15a3' / 'orig' / f
    print('%s: orig %s (seal 15 line %s) disk %s (seal 16 line %s)' % (
        f, sha(o)[:16], d15.get('s15/' + f, '-')[:16], sha(R / 's15' / f)[:16], d16.get('s15/' + f, '-')[:16]))
    show(f + ' orig(sub)->disk', [sub(x) for x in lines(o)], lines(R / 's15' / f), 170)
print('==== (4) enter_scene_s15.py seal 14 (s15a2/orig) -> disk')
eo = R / 's15a2' / 'orig' / 'enter_scene_s15.py'
print('orig %s (seal 14 line %s) disk %s' % (sha(eo)[:16], d14.get('s15/enter_scene_s15.py', '-')[:16],
                                            sha(R / 's15/enter_scene_s15.py')[:16]))
show('enter orig->disk', lines(eo), lines(R / 's15/enter_scene_s15.py'), 160)
