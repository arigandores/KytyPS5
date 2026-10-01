# vidcont144.py - Session Auditor, s144 step 3 (HPP-333), debt D-4, continuity of the video against the presented frames.
# The coverage row of the seal counts frames (video >= FrameTrace rows - 100). This script asks WHICH presented frames have no
# record: the recorder index rec_<tag>.mp4.idx carries the time of every recorded present; the FrameTrace rows carry dt_us.
# Both streams are put on one clock by anchoring their ends (the last record ~ the end of the last row); inside every idx gap
# >= GAP the FrameTrace rows that END strictly inside the gap (margin MARG) are presented frames without a video record.
# No scorer code. READ ONLY. Usage: python vidcont144.py
import re, json, mmap, bisect
from multiprocessing import Pool

A = {(r['root'][-4:], r['tag']): r for r in json.load(open('C:/kyty/s144/step3/aud144.json'))}
TAGS = [('s144', 'C:/kyty/s144', 'v144_%02d' % i) for i in range(9, 21)] + [('s143', 'C:/kyty/s143', 'v143_%02d' % i) for i in range(1, 11)] + \
       [('s142', 'C:/kyty/s142', 'v142')]
RN = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
GAP = 0.060     # an idx gap longer than this is examined (a 60 fps present is 0.0167 s, a 30 fps one 0.033 s)
MARG = 0.012    # a row end closer than this to a gap edge is taken as the record at that edge


def job(a):
    ses, root, tag = a
    rows = []
    with open('%s/log_%s.txt' % (root, tag), 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        p = mm.find(b'FrameTrace: n=')
        while p != -1:
            m = RN.match(mm[p:p + 60])
            if m:
                rows.append((int(m.group(1)), int(m.group(2))))
            p = mm.find(b'FrameTrace: n=', p + 1)
        mm.close()
    ls = [x.split() for x in open('%s/rec_%s.mp4.idx' % (root, tag), 'rb').read().decode('ascii', 'replace').splitlines() if x.strip()]
    it = [float(x[2]) for x in ls]
    # row end times on the idx clock, anchored at the ends
    ends = []
    c = 0.0
    for n, dt in reversed(rows):
        ends.append(it[-1] - c)
        c += dt / 1e6
    ends.reverse()
    miss = []      # (gap start index, gap seconds, [n of the rows ending inside])
    for i in range(len(it) - 1):
        g = it[i + 1] - it[i]
        if g > GAP:
            lo = bisect.bisect_right(ends, it[i] + MARG)
            hi = bisect.bisect_left(ends, it[i + 1] - MARG)
            if hi > lo:
                miss.append((i, g, [rows[k][0] for k in range(lo, hi)], sum(rows[k][1] for k in range(lo, hi)) / 1e6))
    # anchor check: how many row ends have a record within 8 ms (an alignment quality figure)
    near = 0
    for e in ends:
        k = bisect.bisect_left(it, e)
        d = min(abs(it[k] - e) if k < len(it) else 9, abs(it[k - 1] - e) if k > 0 else 9)
        near += 1 if d <= 0.008 else 0
    return ses, tag, rows, len(it), it[-1] - it[0], miss, near


def main():
    with Pool(8) as pool:
        res = pool.map(job, TAGS, chunksize=1)
    for ses, tag, rows, nrec, span, miss, near in res:
        L = A[(ses, tag)]['log']
        first = L.get('first')
        fn = first[0] if first else None
        after = [(i, g, ns, s) for i, g, ns, s in miss if fn is not None and ns[-1] > fn]
        tot_after = sum(len([n for n in ns if n > fn]) for i, g, ns, s in after)
        tot_before = sum(len([n for n in ns if fn is None or n <= fn]) for i, g, ns, s in miss)
        worst = max(after, key=lambda x: len(x[2])) if after else None
        runs = sorted(after, key=lambda x: -len(x[2]))[:4]
        print('VCONT %s %s: rows %d, records %d (records - rows %+d), rows with a record within 8 ms %d (%.1f %%); first scene frame n %s; '
              'presented frames WITHOUT a video record: before / at the first scene frame %d, after it %d in %d gaps; longest run after it: %s; top runs %s' % (
                  ses, tag, len(rows), nrec, nrec - len(rows), near, 100.0 * near / len(rows), fn, tot_before, tot_after, len(after),
                  ('%d rows n %d..%d over %.3f s of dt (idx gap %.3f s after record %d)' % (len(worst[2]), worst[2][0], worst[2][-1], worst[3], worst[1], worst[0])) if worst else 'none',
                  [(len(x[2]), x[2][0], x[2][-1], round(x[1], 3)) for x in runs]))
    print('ALL DONE')


if __name__ == '__main__':
    main()
