# S2a (HPP-312): for the 12 B1b frames - is there a row with skc_ap_skip > 0 (= "skipped draw" lines, identity T-1)
# in the groups i-2..i+1? Under p.241(v)(3)-(4) such a frame is classed SHADER before PRIO (on a T arm).
import re
RE_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) ')
RE_SK = re.compile(rb' skc_ap_skip=(\d+)')
RE_HI = re.compile(rb' skc_held_inc=(\d+)')
for tag, lo, hi in (('c142_02', 332, 337), ('c142_09', 182, 187)):
    rows = {}
    cur = None
    with open('C:/kyty/s142/log_%s.txt' % tag, 'rb') as f:
        for l in f:
            if l.startswith(b'FrameTrace: '):
                m = RE_FT.match(l)
                cur = int(m.group(1)) if m else None
                if cur is not None:
                    rows[cur] = [int(m.group(2)), 0, 0]
                if cur is not None and cur > hi + 2:
                    break
            elif l.startswith(b'FrameTrace-x: ') and cur is not None:
                a = RE_SK.search(l); b = RE_HI.search(l)
                rows[cur][1] = int(a.group(1)) if a else 0
                rows[cur][2] = int(b.group(1)) if b else 0
    n_sh = 0
    for n in range(lo - 2, hi + 2):
        print(tag, 'n', n, 'dt', rows[n][0], 'skip', rows[n][1], 'held_inc', rows[n][2])
    for n in range(lo, hi + 1):
        g = [k for k in (n - 2, n - 1, n, n + 1) if rows[k][1] > 0]
        n_sh += 1 if g else 0
        print(tag, 'B1b frame', n, 'rows with skipped draw in i-2..i+1:', g, '-> SHADER by p.241(v)(4) second clause' if g else '-> not by this clause')
    print(tag, 'B1b frames that the second clause of (v)(4) would class SHADER:', n_sh, 'of', hi - lo + 1)
