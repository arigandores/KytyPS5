import re, sys, statistics, json
path, stable = sys.argv[1], int(sys.argv[2])
R = re.compile(rb'^FrameTrace-draw: n=(\d+).* bda_scan=(\d+) ')
BN = re.compile(rb' buf_new=(\d+)')
allv = []; post = []; pre = []; bn_all = 0; xrows = 0
with open(path, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace-x: n='):
            xrows += 1
            continue
        if not line.startswith(b'FrameTrace-draw: n='):
            continue
        m = R.match(line)
        if not m: continue
        n, s = int(m.group(1)), int(m.group(2))
        allv.append(s)
        (post if n >= stable else pre).append(s)
        b = BN.search(line)
        if b: bn_all += int(b.group(1))
exc = [max(0, s - 52) for s in allv]
print('xrows', xrows, 'draw rows', len(allv), 'pre', len(pre), 'post', len(post))
print('median post', statistics.median(post), 'mean post', round(statistics.mean(post), 1))
print('mean all', round(statistics.mean(allv), 1), 'mean(max(0,scan-52)) all rows', round(sum(exc) / xrows, 1),
      'post-only', round(sum(max(0, s - 52) for s in post) / len(post), 1))
print('pre sum excess', sum(max(0, s - 52) for s in pre), 'pre max', max(pre) if pre else None)
print('k-est all rows (excess/1032)', round(sum(exc) / xrows / 1032, 3), 'buf_new per row', round(bn_all / xrows, 3))
