# S2a (HPP-312), Session Auditor. Own recount of the lead's fact p.241(a):
# "12 of 13 PRIO window frames (c142_02 n 332-337, c142_09 n 182-187) are B1b frames".
# Binary streaming; shares no code with C:/kyty/s288/s0/*.py, s1/*.py, lead/*.py, f287/*.py.
# Usage: python prio_s2a.py <log> <level name> [<log> <level name> ...]
import sys, re, hashlib

RE_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+) ')
RE_KV = re.compile(rb' ([a-z_0-9]+)=(-?\d+)')
RE_US = re.compile(rb'(\d+) ?us')
WINDOW = 599          # rows after the first scene frame (reading of sc142 / p.221(v))
T100 = 100000


def kv(line, key):
    m = re.search(rb'[ :]' + key + rb'=(-?\d+)', line)
    return int(m.group(1)) if m else None


def scan(path, level):
    h = hashlib.sha256()
    frames = []   # dict per main FrameTrace row
    ev = []       # (lineno, kind, us, text)
    start_line = None
    lvl = level.encode()
    nlines = 0
    found_level = None
    with open(path, 'rb') as f:
        for i, line in enumerate(f, 1):
            h.update(line)
            nlines = i
            if b'FrameTrace' in line:
                m = RE_FT.search(line)
                if m:
                    frames.append({'line': i, 'n': int(m.group(1)), 'dt': int(m.group(2)),
                                   'draws': kv(line, rb'draws'), 'cpu_gpu': kv(line, rb'cpu_gpu_us'),
                                   'prio_us': kv(line, rb'prio_us'), 'x': {}})
                elif b'FrameTrace-x:' in line and frames:
                    for k in (rb'skc_ap_skip', rb'skc_held_inc', rb'skc_held', rb'skc_bad'):
                        v = kv(line, k)
                        if v is not None:
                            frames[-1]['x'][k.decode()] = v
                continue
            if b'PriorityStall' in line:
                us = None
                m = re.search(rb'(\d+) ?us', line)
                if m:
                    us = int(m.group(1))
                m2 = re.search(rb'us=(\d+)', line)
                if m2:
                    us = int(m2.group(1))
                ev.append((i, 'PRIO', us, line.rstrip(b'\r\n').decode('utf-8', 'replace')[:220]))
            elif b'BvhLoopCapTrip' in line:
                ev.append((i, 'BVH', None, line.rstrip(b'\r\n').decode('utf-8', 'replace')[:220]))
            elif b'pipeline cache: saved' in line or b'PipelinePrecache: saved' in line:
                ev.append((i, 'PCW', None, line.rstrip(b'\r\n').decode('utf-8', 'replace')[:160]))
            elif b'Level has started: ' in line and start_line is None:
                tail = line.split(b'Level has started: ', 1)[1].strip()
                if tail and (level == '*' or lvl in tail):
                    start_line = i
                    found_level = tail.decode('utf-8', 'replace')
    return h.hexdigest(), nlines, frames, ev, start_line, found_level


def report(path, level):
    sha, nlines, frames, ev, start_line, level = scan(path, level)
    print('=' * 100)
    print('log', path)
    print('sha256', sha, 'lines', nlines, 'FrameTrace rows', len(frames))
    print('entry line (Level has started: %s)' % level, start_line)
    # contiguity of n
    gaps = sum(1 for a, b in zip(frames, frames[1:]) if b['n'] != a['n'] + 1)
    print('n gaps', gaps)
    first = None
    for idx, fr in enumerate(frames):
        if start_line is not None and fr['line'] > start_line and (fr['draws'] or 0) >= 100:
            first = idx
            break
    print('first scene frame n', frames[first]['n'], 'line', frames[first]['line'], 'dt', frames[first]['dt'])
    # events by both group conventions
    lines = [fr['line'] for fr in frames]
    import bisect
    nxt = {}   # frame idx -> events (event belongs to the next main row after it)
    prv = {}   # frame idx -> events (event belongs to the last main row before it)
    for e in ev:
        j = bisect.bisect_left(lines, e[0])     # first main row with line > event line
        if j < len(frames):
            nxt.setdefault(j, []).append(e)
        if j - 1 >= 0:
            prv.setdefault(j - 1, []).append(e)
    print('events total: PRIO', sum(1 for e in ev if e[1] == 'PRIO'), 'BVH', sum(1 for e in ev if e[1] == 'BVH'),
          'PCW', sum(1 for e in ev if e[1] == 'PCW'))
    for e in ev:
        if e[1] in ('PRIO', 'BVH'):
            j = bisect.bisect_left(lines, e[0])
            nn = frames[j]['n'] if j < len(frames) else None
            pn = frames[j - 1]['n'] if j >= 1 else None
            print('  ev line %d %s us=%s next_n=%s prev_n=%s | %s' % (e[0], e[1], e[2], nn, pn, e[3]))
    print('-- frames dt >= 100000 us after the first scene frame (window = %d rows after it, then hold)' % WINDOW)
    print('part n line dt cpu_gpu prio_us(lite) | NEXT: prio_n prio_us_sum bvh_n pcw_n | PREV: prio_n prio_us_sum bvh_n pcw_n | skip held | class_next class_prev')
    tot = {'win': 0, 'hold': 0}
    cls_cnt = {}
    rows = []
    for idx in range(first + 1, len(frames)):
        fr = frames[idx]
        if fr['dt'] < T100:
            continue
        part = 'win' if idx - first <= WINDOW else 'hold'
        tot[part] += 1

        def agg(d):
            es = d.get(idx, [])
            p = [e for e in es if e[1] == 'PRIO']
            return (len(p), sum((e[2] or 0) for e in p), sum(1 for e in es if e[1] == 'BVH'), sum(1 for e in es if e[1] == 'PCW'))
        a = agg(nxt)
        b = agg(prv)

        def cls(t):
            # S0 rule 1.5: PRIO if sum(PriorityStall us) >= dt/2 and cpu_gpu_us < dt/2; GPUTHR if cpu_gpu_us >= dt/2; else WAIT
            if t[1] * 2 >= fr['dt'] and (fr['cpu_gpu'] or 0) * 2 < fr['dt']:
                return 'PRIO'
            if (fr['cpu_gpu'] or 0) * 2 >= fr['dt']:
                return 'GPUTHR'
            return 'WAIT'
        ca, cb = cls(a), cls(b)
        cls_cnt[(part, ca, cb)] = cls_cnt.get((part, ca, cb), 0) + 1
        rows.append((part, fr['n'], ca, cb, a, b, fr['dt']))
        print(part, fr['n'], fr['line'], fr['dt'], fr['cpu_gpu'], fr['prio_us'], '|', a[0], a[1], a[2], a[3], '|', b[0], b[1], b[2], b[3], '|',
              fr['x'].get('skc_ap_skip'), fr['x'].get('skc_held_inc'), '|', ca, cb)
    print('frames >= 100 ms: window', tot['win'], 'hold', tot['hold'])
    for k in sorted(cls_cnt):
        print('  class (part, next-convention, prev-convention)', k, cls_cnt[k])
    return rows


if __name__ == '__main__':
    a = sys.argv[1:]
    allrows = {}
    for k in range(0, len(a), 2):
        allrows[a[k]] = report(a[k], a[k + 1])
    print('=' * 100)
    print('SUMMARY (window frames, class PRIO under the S0 convention = event belongs to the next main row)')
    for p, rows in allrows.items():
        w = [r for r in rows if r[0] == 'win' and r[2] == 'PRIO']
        print(p)
        print('  PRIO(next) window frames n:', [r[1] for r in w])
        print('  of them with >=1 BvhLoopCapTrip line in the group (next):', [r[1] for r in w if r[4][2] > 0])
        print('  of them with >=1 BvhLoopCapTrip line in the group (prev):', [r[1] for r in w if r[5][2] > 0])
        print('  of them with BvhLoopCapTrip in next OR prev group:', [r[1] for r in w if r[4][2] > 0 or r[5][2] > 0])
        print('  of them PRIO under both conventions:', [r[1] for r in w if r[3] == 'PRIO'])
        print('  dt:', [r[6] for r in w])
