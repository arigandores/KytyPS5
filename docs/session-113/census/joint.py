"""Read-only: joint distribution of (full-span rescans k, buf_new) per frame, steady window.

k = round((bda_scan - base) / span), span = (bda_scan + bda_skip) / (bda_n - bda_hit) of the frame,
base = the median bda_scan of frames with buf_new == 0 and bda_scan < 200.
usage: python joint.py <log> [from_frame]
"""
import collections
import re
import statistics as st
import sys

KV = re.compile(rb'(\w+)=(\d+)')


def main():
    path = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 2100
    fr = {}
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace-draw:') or line.startswith(b'FrameTrace-x:'):
                kv = dict(KV.findall(line))
                n = int(kv.get(b'n', b'-1'))
                if n < lo:
                    continue
                d = fr.setdefault(n, {})
                for k in (b'bda_scan', b'bda_skip', b'bda_n', b'buf_new', b'bda_hit', b'bda_drng', b'pb2_pass'):
                    if k in kv:
                        d[k.decode()] = int(kv[k])
    rows = [d for d in fr.values() if all(k in d for k in ('bda_scan', 'bda_skip', 'bda_n', 'buf_new', 'bda_hit'))]
    base = st.median([d['bda_scan'] for d in rows if d['buf_new'] == 0 and d['bda_scan'] < 200] or [0])
    joint = collections.Counter()
    for d in rows:
        calls = d['bda_n'] - d['bda_hit']
        span = (d['bda_scan'] + d['bda_skip']) / calls if calls > 0 else 0
        k = round((d['bda_scan'] - base) / span) if span else -1
        joint[(max(k, 0), min(d['buf_new'], 4))] += 1
    print(path, 'frames', len(rows), 'base', base)
    ks = sorted({k for k, _ in joint})
    print('   k\\buf_new ' + ' '.join('%6s' % b for b in range(5)))
    for k in ks:
        print('   %8d ' % k + ' '.join('%6d' % joint[(k, b)] for b in range(5)))
    # drng per full rescan
    extra = [d['bda_drng'] for d in rows if 'bda_drng' in d and d['bda_scan'] > 500]
    extra0 = [d['bda_drng'] for d in rows if 'bda_drng' in d and d['bda_scan'] < 200]
    if extra and extra0:
        print('   bda_drng median OLD-level %s NEW-level %s' % (st.median(extra), st.median(extra0)))


if __name__ == '__main__':
    main()
