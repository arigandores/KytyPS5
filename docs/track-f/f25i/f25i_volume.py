#!/usr/bin/env python3
# F25i (HPP-676): log volume of a run by source - bytes and lines of FrameTrace*/FlipHold (harness form KYTY_FRAME_TRACE),
# DiagB32* (KYTY_DIAG_B32), guest PRINT_NAME headers, tab argument dumps, other; and the raw lines of the segments
# FrameTrace n-1 .. n for the frames given (to name what each thread wrote during the stall).
# usage: f25i_volume.py <log> [<n> ...]
import re
import sys

HDR = re.compile(rb'^\[\d+\]\[')


def kind(line):
    if line.startswith(b'FrameTrace') or line.startswith(b'FlipHold'):
        return 'frametrace'
    if line.startswith(b'DiagB32'):
        return 'diagb32'
    if HDR.match(line):
        return 'guest_hdr'
    if line.startswith(b'\t'):
        return 'tab_arg'
    return 'other'


def main():
    log = sys.argv[1]
    want = set(int(x) for x in sys.argv[2:])
    by = {}
    seg = []
    cur_n = None
    with open(log, 'rb') as f:
        for line in f:
            k = kind(line)
            b, c = by.get(k, (0, 0))
            by[k] = (b + len(line), c + 1)
            if line.startswith(b'FrameTrace: n='):
                n = int(re.match(rb'FrameTrace: n=(\d+)', line).group(1))
                if cur_n is not None and cur_n + 1 in want:
                    print('--- segment FrameTrace n=%d .. n=%d: %d lines (non-FrameTrace shown)' % (cur_n, n, len(seg)))
                    for s in seg:
                        if not s.startswith(b'FrameTrace'):
                            print('   ' + s.decode('latin-1').rstrip()[:160])
                seg = []
                cur_n = n
            seg.append(line)
    tot = sum(b for b, c in by.values())
    print('log %s total bytes %d' % (log, tot))
    for k, (b, c) in sorted(by.items(), key=lambda x: -x[1][0]):
        print('  %-11s bytes %12d (%.4f) lines %10d' % (k, b, b / tot if tot else 0, c))


if __name__ == '__main__':
    main()
