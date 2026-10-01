"""Session 145 link 1b (HPP-379, ROADMAP s122 item 295 (d)): the alignment of sc145.vquality on v143_07 and v143_08 (s143)
against the own recount of the review (step1/vcont145_rt.out.txt: within 8 ms 16990 of 17129 / 17948 of 19059; 600 rows from
the first scene frame 463 / 320; best offset -4 ms (16994 / 19042); counts 135 -> 133 / 17 -> 17).  ASCII.
usage: vq_rt.py <out.txt>"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location('sc145_vq', 'C:/kyty/s145/sc145.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
REV = {'v143_07': (16990, 17129, 463, -4, 16994, 135, 133), 'v143_08': (17948, 19059, 320, -4, 19042, 17, 17)}
old = S.profile(S.P143)
out = []
try:
    for tag in ('v143_07', 'v143_08'):
        lv = S.level_of(tag)
        sc = S.scan('C:/kyty/s143/log_%s.txt' % tag)
        d = S.derive(sc, lv)
        it = S.idx_times('C:/kyty/s143/rec_%s.mp4.idx' % tag)
        q = S.vquality(sc['rows'], it, d['first'][0])
        r = REV[tag]
        same = (q['near'], q['rows'], q['near600f'], q['shift'], q['near_best'], q['after0'], q['after_best']) == r
        out.append('VQ %s (level %s, log sha %s): %s; review (within 8 ms, rows, 600 from the first scene frame, best shift, rows '
                   'at it, count 0, count best) %s -> %s' % (tag, lv, sc['sha256'][:16], S.fmt_vq(q), r,
                                                              'EQUAL' if same else 'DIFFERENT'))
finally:
    S.profile(old)
open(sys.argv[1], 'w', encoding='ascii', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out))
