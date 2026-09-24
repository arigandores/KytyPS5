#!/usr/bin/env python3
"""hist113.py -- histogram of per-flip bda_scan (steady rows) for a few logs, to see its quantization.

  python hist113.py <log> [<log> ...] [--bin 50]
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census113 as C  # noqa: E402


def main(argv):
    b = 50
    logs = []
    i = 0
    while i < len(argv):
        if argv[i] == '--bin':
            b = int(argv[i + 1]); i += 2; continue
        logs.append(argv[i]); i += 1
    idx = C.json_index()
    for p in logs:
        meta = C.find_meta(p, idx)
        status, segs, mk = C.read_log(p)
        rows = segs[-1] if segs else []
        vals = [r.get('bda_scan') for r in rows if r.get('n', 0) > meta['stable'] and r.get('bda_scan') is not None]
        h = collections.Counter((v // b) * b for v in vals)
        tot = len(vals)
        print('== %s steady=%d' % (p, tot))
        print('   ' + '  '.join('%d:%.3f' % (k, c / tot) for k, c in sorted(h.items()) if c / tot >= 0.002))
        # exact values of the most common
        e = collections.Counter(vals)
        print('   top exact: ' + ' '.join('%d:%d' % kv for kv in e.most_common(12)))


if __name__ == '__main__':
    main(sys.argv[1:])
