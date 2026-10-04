import sys, re, collections
marks = [b'MaterializeBoundTargetDccClears', b'adopted pending DCC', b'stale pending DCC', b'metadata fill', b'compute image clear', b'FixB42', b'Level has started', b'MetaClearTrace', b'BufferFillTrace', b'DCC clear', b'DccClear', b'Cmask', b'CMASK', b'DiagF5: mode', b'PendingDcc', b'FastClear', b'fast clear', b'DMA fill', b'DmaFill', b'TrackDcc']
out = open(sys.argv[2], 'wb')
cnt = collections.Counter(); first = collections.defaultdict(list)
with open(sys.argv[1], 'rb') as f:
    for n, line in enumerate(f):
        for m in marks:
            if m in line:
                cnt[m] += 1
                if len(first[m]) < 40:
                    first[m].append((n, line.rstrip()[:400]))
                break
for m in marks:
    out.write(b'== ' + m + b' count=' + str(cnt[m]).encode() + b'\n')
    for n, l in first[m]:
        out.write(str(n).encode() + b': ' + l + b'\n')
