# F47a (HPP-802): time line of one recording. Log: FrameTrace n and cumulative dt_us (time since the first FrameTrace row);
# the first NAMED "Level has started: <name>" line -> n_start (next FrameTrace row) and T_start. Video: <mp4>.idx rows
# "<video frame> <present> <t s since the first recorded present>". Assumption [I, printed]: t of the video and the
# cumulative dt of FrameTrace share the origin within a few frames; the phase is printed both ways (presents after the
# present nearest T_start, and seconds after T_start).
# Usage: python tl_f47a.py <log> <idx> [--frames a-b] [--json out.json]
import bisect, json, re, sys

RX = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) ')


def read_log(path):
    ns, ts = [], []
    t = 0.0
    n_start = None
    name = ''
    pend = False
    with open(path, 'rb') as f:
        for line in f:
            m = RX.match(line)
            if m:
                t += int(m.group(2)) / 1e6
                ns.append(int(m.group(1)))
                ts.append(t)
                if pend:
                    n_start = int(m.group(1))
                    pend = False
                continue
            if n_start is None and not pend and b'Level has started:' in line:
                text = line.split(b'Level has started:', 1)[1].strip()
                if text:
                    name = text.decode('utf-8', 'replace')
                    pend = True
    return ns, ts, n_start, name


def read_idx(path):
    rows = []
    for ln in open(path, encoding='ascii'):
        p = ln.split()
        if len(p) >= 3:
            rows.append((int(p[0]), int(p[1]), float(p[2])))
    return rows


def main():
    logp, idxp = sys.argv[1], sys.argv[2]
    fr = None
    if '--frames' in sys.argv:
        a, b = sys.argv[sys.argv.index('--frames') + 1].split('-')
        fr = (int(a), int(b))
    ns, ts, n_start, name = read_log(logp)
    idx = read_idx(idxp)
    i0 = ns.index(n_start) if n_start in ns else None
    T0 = ts[i0] if i0 is not None else None
    vt = [r[2] for r in idx]
    j0 = min(range(len(idx)), key=lambda j: abs(vt[j] - T0)) if T0 is not None else None
    out = {'log': logp, 'idx': idxp, 'name': name, 'n_start': n_start, 'T_start_s': T0,
           'ft_rows': len(ns), 'ft_last_n': ns[-1] if ns else None, 'ft_last_t': ts[-1] if ts else None,
           'video_frames': len(idx), 'video_last_t': vt[-1] if vt else None,
           'start_video_frame': idx[j0][0] if j0 is not None else None,
           'start_present': idx[j0][1] if j0 is not None else None}
    print(json.dumps(out))
    if fr:
        print('vf\tpresent\tt_video\tdpresent_from_start\tdt_from_start_s\tn_est\tdn_from_start')
        for vf, pr, t in idx:
            if fr[0] <= vf <= fr[1]:
                k = bisect.bisect_left(ts, t)
                k = min(k, len(ns) - 1)
                n_est = ns[k]
                print('%d\t%d\t%.3f\t%d\t%.3f\t%d\t%d' % (vf, pr, t, pr - out['start_present'], t - T0, n_est,
                                                          n_est - n_start))
    if '--json' in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)


main()
