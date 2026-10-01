# Red Team S3r: the S0 1.3 column "skipped draws" - try: lines with group > fi (after the first scene frame), and sum skc_ap_skip after fi.
import sys
sys.path.insert(0, 'C:/kyty/s288/s3r')
import rt_s3r as R
import re, json
for tag in sys.argv[1:]:
    js = json.load(open('C:/kyty/s142/%s.json' % tag, encoding='utf-8'))
    level = js.get('level') or js['guest_args'].split()[-1]
    rows = []; skips = []; starts = []; x = {}
    for line in open('C:/kyty/s142/log_%s.txt' % tag, 'rb'):
        g = len(rows)
        m = R.RX_N.match(line)
        if m:
            dt = R.num(line, b'dt_us')
            if dt is not None:
                rows.append((int(m.group(1)), dt, R.num(line, b'draws') or 0))
            continue
        m = R.RX_XN.match(line)
        if m:
            x[int(m.group(1))] = R.num(line, b'skc_ap_skip') or 0
            continue
        if line.startswith(b'GuestOut: Level has started:'):
            starts.append((g, line.split(b':', 2)[2].strip().decode('latin1')))
        elif line.startswith(b'AsyncPipelines: skipped draw'):
            skips.append(g)
    si = [i for i, (g, nm) in enumerate(starts) if nm == level][0]
    eg = starts[si][0]
    end = starts[si + 1][0] if si + 1 < len(starts) else len(rows)
    fi = next(i for i in range(eg, end) if rows[i][2] >= 100)
    print(tag, 'lines g>fi', sum(1 for g in skips if g > fi), 'lines g>=fi', sum(1 for g in skips if g >= fi),
          'sum ap_skip rows>fi', sum(x.get(rows[i][0], 0) for i in range(fi + 1, end)))
