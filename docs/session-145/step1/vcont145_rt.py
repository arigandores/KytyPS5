# Red Team s145 step 1: own recount of the video continuity row (B38) on two V of s143 (v143_07, v143_08), own code.
# (1) the method of the seal (end anchor, gap > 60 ms, margin 12 ms) coded anew; (2) a sensitivity read: the anchor offset
# that maximizes rows with a record within 8 ms, searched +-0.5 s around the end anchor; (3) checks the anchor needs:
# n continuity of FrameTrace rows, idx field 2 = field 1 + 1, local alignment quality in the first 600 rows after the scene.
import re, bisect, hashlib, sys
RX = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RXD = re.compile(rb' draws=(\d+)')
START = b'GuestOut: Level has started: '
TAGS = (('v143_07', 'spring_punch_monster_cave'), ('v143_08', 'pot_treasure_cave'))
LV = {}
def rows_of(path):
    rows = []; entry = None; h = hashlib.sha256(); off = 0; tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(1 << 26)
            h.update(b)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            if entry is None:
                i = whole.find(START)
                if i >= 0:
                    e = whole.find(b'\n', i)
                    entry = (off + i, whole[i + len(START):e].strip().decode('latin1'))
            for m in RX.finditer(whole):
                d = RXD.search(m.group(3))
                rows.append((int(m.group(1)), int(m.group(2)), int(d.group(1)) if d else -1, off + m.start()))
            off += len(whole)
            if not b:
                break
    return rows, entry, h.hexdigest()
def count(rows, it, fn, shift):
    ends = []; c = 0.0
    for r in reversed(rows):
        ends.append(it[-1] - c + shift); c += r[1] / 1e6
    ends.reverse()
    after = 0; gaps = 0; longest = None; before = 0
    for i in range(len(it) - 1):
        g = it[i + 1] - it[i]
        if g > 0.060:
            lo = bisect.bisect_right(ends, it[i] + 0.012); hi = bisect.bisect_left(ends, it[i + 1] - 0.012)
            ns = [rows[k][0] for k in range(lo, hi)]
            a = [n for n in ns if n > fn]
            before += len(ns) - len(a)
            if a:
                gaps += 1; after += len(a)
                if longest is None or len(ns) > longest[0]:
                    longest = (len(ns), ns[0], ns[-1], round(g, 3), i)
    near = 0
    for e in ends:
        k = bisect.bisect_left(it, e)
        d = min(abs(it[k] - e) if k < len(it) else 9, abs(it[k - 1] - e) if k > 0 else 9)
        near += d <= 0.008
    return after, gaps, longest, before, near, ends
for tag, lv in TAGS:
    rows, entry, sha = rows_of('C:/kyty/s143/log_%s.txt' % tag)
    raw = open('C:/kyty/s143/rec_%s.mp4.idx' % tag, 'rb').read()
    ls = [x.split() for x in raw.splitlines() if len(x.split()) >= 3]
    it = [float(x[2]) for x in ls]
    f2 = sum(1 for x in ls if int(x[1]) != int(x[0]) + 1)
    print('%s log sha256 %s idx sha256 %s rows %d records %d; idx rows with field2 != field1+1: %d; entry %s' % (
        tag, sha, hashlib.sha256(raw).hexdigest(), len(rows), len(it), f2, entry))
    ngap = [(a[0], b[0]) for a, b in zip(rows, rows[1:]) if b[0] != a[0] + 1]
    print('  FrameTrace n breaks: %d %s' % (len(ngap), ngap[:5]))
    after_entry = [r for r in rows if entry and r[3] > entry[0]]
    fs = next((r for r in after_entry if r[2] >= 100), None)
    fn = fs[0] if fs else None
    print('  first scene frame n %s (draws %s)' % (fn, fs[2] if fs else None))
    a, g, lg, bf, near, ends = count(rows, it, fn, 0.0)
    print('  END ANCHOR: after first scene frame %d rows in %d gaps; longest %s; at/before %d; rows within 8 ms of a record %d of %d' % (a, g, lg, bf, near, len(rows)))
    fi = next(i for i, r in enumerate(rows) if r[0] == fn)
    loc = rows[fi:fi + 600]; le = ends[fi:fi + 600]
    ln = 0
    for e in le:
        k = bisect.bisect_left(it, e)
        d = min(abs(it[k] - e) if k < len(it) else 9, abs(it[k - 1] - e) if k > 0 else 9)
        ln += d <= 0.008
    print('  local alignment, 600 rows from the first scene frame: within 8 ms %d of %d' % (ln, len(le)))
    best = None
    for s in range(-500, 501, 2):
        r = count(rows, it, fn, s / 1000.0)
        if best is None or r[4] > best[1][4]:
            best = (s, r)
    s, r = best
    print('  BEST OFFSET %+d ms (rows within 8 ms %d): after first scene frame %d rows in %d gaps; longest %s' % (s, r[4], r[0], r[1], r[2]))
    for s in (-20, -10, 10, 20):
        r = count(rows, it, fn, s / 1000.0)
        print('  offset %+d ms: after %d in %d gaps longest %s' % (s, r[0], r[1], r[2]))
    sys.stdout.flush()
