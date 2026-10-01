#!/usr/bin/env python3
# S1 (Red Team, HPP-295): independent recount of S0 attribution on sc142 logs.
# No code shared with C:/kyty/s288/s0/*.py. Streams each log in binary mode.
import sys, re, json, hashlib, collections

TAGS = ['v142', 'w142'] + ['c142_%02d' % i for i in range(1, 11)]
RX_KV = re.compile(rb'([a-z_0-9]+)=(-?\d+)')
RX_SKIP = re.compile(rb'AsyncPipelines: skipped draw \S+ frame=(\d+) vs=0x([0-9a-f]+) ps=0x([0-9a-f]+) pending=(\d+)')
RX_HELD = re.compile(rb'AsyncPipelines: flip (\d+) held')
RX_PRIO = re.compile(rb'PriorityStall: .*?us=(\d+)')
RX_LVL = re.compile(rb'GuestOut: Level has started: (\S+)')
RX_CSP = re.compile(rb'CsPretranslate: (ready|skipped|miss|hit)\b')


def kv(line):
    return {k.decode(): int(v) for k, v in RX_KV.findall(line)}


def scan(path):
    rows = []          # main FrameTrace rows in order
    x = {}             # n -> FrameTrace-x fields
    dr = {}            # n -> FrameTrace-draw fields
    skips = []         # (lineno, frame, vs, ps, pending, group_index)
    held_lines = []    # flip ids
    prio_next = collections.defaultdict(int)  # group index (next main row) -> sum us
    prio_lines = 0
    lvl = []           # (lineno, name, rows_so_far)
    csp = collections.Counter()
    csp_after_lvl = collections.Counter()
    h = hashlib.sha256()
    named_lvl_seen = False
    with open(path, 'rb') as f:
        for ln, line in enumerate(f, 1):
            h.update(line)
            if line.startswith(b'FrameTrace: n=') or b'] FrameTrace: n=' in line[:80]:
                d = kv(line[line.find(b'FrameTrace: n='):])
                d['_ln'] = ln
                rows.append(d)
                continue
            if b'FrameTrace-x: n=' in line:
                d = kv(line[line.find(b'FrameTrace-x: n='):])
                x[d['n']] = d
                continue
            if b'FrameTrace-draw: n=' in line:
                d = kv(line[line.find(b'FrameTrace-draw: n='):])
                dr[d['n']] = d
                continue
            if b'AsyncPipelines: ' in line:
                m = RX_SKIP.search(line)
                if m:
                    skips.append((ln, int(m.group(1)), m.group(2).decode(), m.group(3).decode(), int(m.group(4)), len(rows)))
                    continue
                m = RX_HELD.search(line)
                if m:
                    held_lines.append(int(m.group(1)))
                    continue
            if b'PriorityStall:' in line:
                m = RX_PRIO.search(line)
                if m:
                    prio_next[len(rows)] += int(m.group(1))
                    prio_lines += 1
                continue
            if b'GuestOut: Level has started:' in line:
                m = RX_LVL.search(line)
                lvl.append((ln, m.group(1).decode() if m else '', len(rows)))
                if m:
                    named_lvl_seen = True
                continue
            if b'CsPretranslate: ' in line:
                m = RX_CSP.search(line)
                if m:
                    csp[m.group(1).decode()] += 1
                    if named_lvl_seen:
                        csp_after_lvl[m.group(1).decode()] += 1
    return dict(rows=rows, x=x, dr=dr, skips=skips, held_lines=held_lines, prio_next=prio_next,
                prio_lines=prio_lines, lvl=lvl, csp=csp, csp_after_lvl=csp_after_lvl, sha=h.hexdigest())


def analyse(tag, S):
    rows, x = S['rows'], S['x']
    named = [l for l in S['lvl'] if l[1]]
    out = {'tag': tag, 'sha256': S['sha'], 'rows': len(rows), 'lvl_lines': [(a, b) for a, b, _ in S['lvl']]}
    # first scene frame: first main row after the named level line with draws >= 100
    lvl_ln = named[0][0]
    fi = next(i for i, r in enumerate(rows) if r['_ln'] > lvl_ln and r.get('draws', 0) >= 100)
    out['first_n'] = rows[fi]['n']
    out['first_ln'] = rows[fi]['_ln']
    held = lambda i: x.get(rows[i]['n'], {}).get('skc_held_inc', 0) > 0
    skipr = lambda i: x.get(rows[i]['n'], {}).get('skc_ap_skip', 0) > 0
    out['first_held'] = held(fi)
    out['first_dt'] = rows[fi]['dt_us']
    win = range(fi + 1, min(len(rows), fi + 600))
    hold = range(fi + 600, len(rows))
    for name, rg in (('win', win), ('hold', hold)):
        out[name + '_skip'] = sum(1 for i in rg if skipr(i))
        out[name + '_held'] = sum(1 for i in rg if held(i))
        out[name + '_ge100'] = sum(1 for i in rg if rows[i]['dt_us'] >= 100000)
        out[name + '_ge1s'] = sum(1 for i in rg if rows[i]['dt_us'] >= 1000000)
    # completeness
    out['rows_no_x'] = sum(1 for r in rows if r['n'] not in x)
    out['n_gaps'] = sum(1 for a, b in zip(rows, rows[1:]) if b['n'] != a['n'] + 1)
    out['skc_bad_sum'] = sum(v.get('skc_bad', 0) for v in x.values())
    out['skc_held_sum'] = sum(v.get('skc_held', 0) for v in x.values())  # skip-ceil holds (separate counter)
    tot_skip = sum(v.get('skc_ap_skip', 0) for v in x.values())
    tot_held = sum(v.get('skc_held_inc', 0) for v in x.values())
    out['T1'] = (tot_skip, len(S['skips']), tot_skip == len(S['skips']) or len(S['skips']) >= 200000)
    out['T2'] = (tot_held, len(S['held_lines']), min(64, tot_held) == len(S['held_lines']))
    frames = sorted(set(s[1] for s in S['skips']))
    out['distinct_skip_frames'] = len(frames)
    out['T6_distinct_frames_eq_held'] = (len(frames), tot_held, len(frames) == tot_held)
    # flip id N of held lines vs FrameTrace n: is the row n=N flagged held?
    byn = {r['n']: i for i, r in enumerate(rows)}
    ok = sum(1 for N in S['held_lines'] if N in byn and held(byn[N]))
    out['held_line_matches_row'] = (ok, len(S['held_lines']))
    # offset skip frame= minus held flip id (first 64 held lines)
    offs = collections.Counter()
    hl = S['held_lines']
    for fr in frames:
        cands = [fr - N for N in hl if 0 <= fr - N <= 4]
        if cands:
            offs[min(cands)] += 1
    out['skipframe_minus_flip'] = dict(offs)
    # shown_skip under +-2 rule and under exact frame mapping
    viol2 = 0
    for i in range(len(rows)):
        if skipr(i) and not held(i) and not any(held(j) for j in (i + 1, i + 2) if j < len(rows)):
            viol2 += 1
    out['shown_skip_pm2'] = viol2
    # series of held rows after the first scene frame (two readings)
    def series(start):
        res = []
        i = start
        while i < len(rows):
            if held(i):
                j = i
                while j < len(rows) and held(j):
                    j += 1
                gap = sum(rows[k]['dt_us'] for k in range(i, j)) + (rows[j]['dt_us'] if j < len(rows) else 0)
                res.append((rows[i]['n'], j - i, gap, j >= len(rows)))
                i = j + 1
            else:
                i += 1
        return res
    s_after = series(fi + 1)
    s_with = series(fi)
    # decomposition of each series (reading 'after'): PriorityStall us inside the series rows + closing row,
    # dt of rows that are themselves >= 100 ms with PRIO class (PriorityStall >= dt/2 and cpu_gpu < dt/2)
    det = []
    for (n0, ln_, gap, open_) in s_with:
        i0 = byn[n0]
        idx = list(range(i0, i0 + ln_)) + ([i0 + ln_] if i0 + ln_ < len(rows) else [])
        prio = sum(S['prio_next'].get(k, 0) for k in idx)
        prio_rows_dt = 0
        for k in idx:
            dtk = rows[k]['dt_us']; cg = rows[k].get('cpu_gpu_us', 0); p = S['prio_next'].get(k, 0)
            if dtk >= 100000 and p >= dtk / 2 and cg < dtk / 2:
                prio_rows_dt += dtk
        sk = [s for s in S['skips'] if idx[0] <= s[5] <= idx[-1] + 2]
        det.append({'n0': n0, 'flips': ln_, 'gap_us': gap, 'prio_us': prio, 'prio_rows_dt_us': prio_rows_dt,
                    'gap_minus_prio_rows': gap - prio_rows_dt, 'pairs': len(set((s[2], s[3]) for s in sk)),
                    'pending_max': max([s[4] for s in sk], default=0), 'starts_at_first': n0 == rows[fi]['n']})
    out['series_detail'] = det
    out['pairs_after_first'] = len(set((s[2], s[3]) for s in S['skips'] if s[5] > fi))
    out['series_after'] = len(s_after)
    out['gap_ge100_after'] = sum(1 for s in s_after if s[2] >= 100000)
    out['gap_ge1s_after'] = sum(1 for s in s_after if s[2] >= 1000000)
    out['gap_max_after'] = max([s[2] for s in s_after], default=0)
    out['series_with'] = len(s_with)
    out['gap_ge1s_with'] = sum(1 for s in s_with if s[2] >= 1000000)
    out['gap_max_with'] = max([s[2] for s in s_with], default=0)
    out['series_open_at_end'] = sum(1 for s in s_after if s[3])
    out['gap_sum_after'] = sum(s[2] for s in s_after)
    # T-5 partition: series gaps + dt of shown rows not closing a series == sum dt after first frame
    closing = set()
    i = fi + 1
    in_series = set()
    while i < len(rows):
        if held(i):
            j = i
            while j < len(rows) and held(j):
                in_series.add(j); j += 1
            if j < len(rows):
                closing.add(j)
            i = j + 1
        else:
            i += 1
    total_dt = sum(rows[k]['dt_us'] for k in range(fi + 1, len(rows)))
    rest = sum(rows[k]['dt_us'] for k in range(fi + 1, len(rows)) if k not in in_series and k not in closing)
    out['T5'] = (out['gap_sum_after'] + rest, total_dt, out['gap_sum_after'] + rest == total_dt)
    # classes of dt >= 100 ms after first scene frame; PriorityStall assigned to next row (S0) and to previous row (variant)
    cls = collections.Counter(); cls_prev = collections.Counter(); cls_ftprio = collections.Counter()
    frames100 = []
    for i in list(win) + list(hold):
        r = rows[i]
        dt = r['dt_us']
        if dt < 100000:
            continue
        cg = r.get('cpu_gpu_us', 0)
        p_next = S['prio_next'].get(i, 0)
        p_prev = S['prio_next'].get(i + 1, 0)
        p_ft = r.get('prio_us', 0)
        def c(p):
            if p >= dt / 2 and cg < dt / 2:
                return 'PRIO'
            if cg >= dt / 2:
                return 'GPUTHR'
            return 'WAIT'
        cls[c(p_next)] += 1; cls_prev[c(p_prev)] += 1; cls_ftprio[c(p_ft)] += 1
        frames100.append((r['n'], dt, cg, p_next, p_ft, c(p_next), c(p_ft), held(i), skipr(i),
                          S['dr'].get(r['n'], {}).get('img_up_kb', 0), r['_ln']))
    out['cls_next'] = dict(cls); out['cls_prev'] = dict(cls_prev); out['cls_ftprio'] = dict(cls_ftprio)
    out['frames100'] = frames100
    out['max_dt_after'] = max((rows[i]['dt_us'] for i in range(fi + 1, len(rows))), default=0)
    out['prio_lines'] = S['prio_lines']
    out['csp'] = dict(S['csp']); out['csp_after_lvl'] = dict(S['csp_after_lvl'])
    out['skipped_draws'] = len(S['skips'])
    out['pairs'] = len(set((s[2], s[3]) for s in S['skips']))
    return out


def main():
    res = []
    for tag in (sys.argv[1:] or TAGS):
        S = scan('C:/kyty/s142/log_%s.txt' % tag)
        a = analyse(tag, S)
        res.append(a)
        print(json.dumps({k: v for k, v in a.items() if k not in ('frames100', 'series_detail')}, ensure_ascii=False))
        sys.stdout.flush()
    json.dump(res, open('C:/kyty/s288/s1/rt_s1.json', 'w'), ensure_ascii=False, indent=0)


if __name__ == '__main__':
    main()
