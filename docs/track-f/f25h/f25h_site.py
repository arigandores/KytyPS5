#!/usr/bin/env python3
# F25h (HPP-675): for the frames n of table22.txt - which Log::Write sites of the Present thread ran in the tail of
# FlipQueue::Flip of flip n-1 (videoOut.cpp:1281-3590). OnFlip(n-1) prints the closed DiagB32 reports
# (diagB32.cpp:1296) BEFORE the FrameTrace lines of flip n-1 (videoOut.cpp:1442...), so a report printed at flip n-1
# lies in the log between the line "FrameTrace: n=<n-2>" and the line "FrameTrace: n=<n-1>". Prints the DiagB32
# header lines found there (their n and the lines they span) and the FrameTrace lines of flip n-1 with their length.
# usage: f25h_site.py <log> <n> [<n> ...]
import re
import sys

log = sys.argv[1]
targets = [int(x) for x in sys.argv[2:]]
need = set()
for n in targets:
    need.update((n - 2, n - 1))
ft = {}
hdr = []
lens = {}
pat = re.compile(rb'^(FrameTrace(?:-[a-z]+)?): n=(\d+)')
with open(log, 'rb') as f:
    for i, line in enumerate(f, 1):
        m = pat.match(line)
        if m:
            k = int(m.group(2))
            if m.group(1) == b'FrameTrace' and k in need:
                ft[k] = i
            if k in need:
                lens.setdefault(k, []).append((m.group(1).decode(), len(line)))
        elif line.startswith(b'DiagB32: n='):
            hdr.append((i, int(re.match(rb'DiagB32: n=(\d+)', line).group(1))))
for n in targets:
    a, b = ft.get(n - 2), ft.get(n - 1)
    printed = [h for (i, h) in hdr if a is not None and b is not None and a < i < b]
    tl = lens.get(n - 1, [])
    print('n %d: reports printed at flip %d (between FrameTrace n=%d line %s and n=%d line %s): %s; FrameTrace lines of flip %d: %d, bytes %d' % (
        n, n - 1, n - 2, a, n - 1, b, printed if printed else 'none', n - 1, len(tl), sum(x[1] for x in tl)))
