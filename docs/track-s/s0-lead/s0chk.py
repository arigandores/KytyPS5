# Lead recount for S0 acceptance (HPP-294). Independent parser; streams logs in binary mode.
import re, sys, json
from multiprocessing import Pool

RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) ')
RX_DRAWS = re.compile(rb' draws=(\d+) ')
RX_CG = re.compile(rb' cpu_gpu_us=(\d+) ')
RX_X = re.compile(rb'^FrameTrace-x: n=(\d+) ')
RX_SK = re.compile(rb' skc_ap_skip=(\d+)')
RX_HI = re.compile(rb' skc_held_inc=(\d+)')
RX_BAD = re.compile(rb' skc_bad=(\d+)')
RX_PS = re.compile(rb'^PriorityStall: .* us=(\d+) ')

def one(tag):
    p = 'C:/kyty/s142/log_%s.txt' % tag
    rows = []  # dict n, dt, draws, cg, prio, sk, hi, bad, line
    started = False
    prio = 0
    skiplines = 0
    byn = {}
    with open(p, 'rb') as f:
        for i, l in enumerate(f, 1):
            if not started:
                if b'GuestOut: Level has started:' in l:
                    started = True
                continue
            if l.startswith(b'PriorityStall:'):
                m = RX_PS.match(l)
                if m: prio += int(m.group(1))
                continue
            if l.startswith(b'AsyncPipelines: skipped draw'):
                skiplines += 1
                continue
            if l.startswith(b'FrameTrace: '):
                m = RX_FT.match(l)
                if not m: continue
                d = RX_DRAWS.search(l); c = RX_CG.search(l)
                r = dict(n=int(m.group(1)), dt=int(m.group(2)), draws=int(d.group(1)) if d else -1,
                         cg=int(c.group(1)) if c else -1, prio=prio, sk=None, hi=None, bad=None, line=i)
                prio = 0
                rows.append(r); byn[r['n']] = r
                continue
            if l.startswith(b'FrameTrace-x: '):
                m = RX_X.match(l)
                r = byn.get(int(m.group(1)))
                if r is not None:
                    a = RX_SK.search(l); b = RX_HI.search(l); c = RX_BAD.search(l)
                    r['sk'] = int(a.group(1)) if a else None
                    r['hi'] = int(b.group(1)) if b else None
                    r['bad'] = int(c.group(1)) if c else None
    # first scene frame
    k0 = next(k for k, r in enumerate(rows) if r['draws'] >= 100)
    after = rows[k0:]  # includes first frame
    win = rows[k0 + 1:k0 + 600]
    hold = rows[k0 + 600:]
    def cnt(part, key):
        return sum(1 for r in part if (r[key] or 0) > 0)
    res = dict(tag=tag, first_n=rows[k0]['n'], first_held=(rows[k0]['hi'] or 0) > 0,
               win_skip=cnt(win, 'sk'), win_held=cnt(win, 'hi'), hold_skip=cnt(hold, 'sk'), hold_held=cnt(hold, 'hi'),
               win_ge100=sum(1 for r in win if r['dt'] >= 100000), hold_ge100=sum(1 for r in hold if r['dt'] >= 100000),
               bad=sum(r['bad'] or 0 for r in rows), skipped_draws_after=sum(r['sk'] or 0 for r in after),
               missing_x=sum(1 for r in rows if r['hi'] is None))
    # series of held rows from first scene frame (inclusive), visible gap
    ser = []
    k = 0
    while k < len(after):
        if (after[k]['hi'] or 0) > 0:
            j = k
            while j < len(after) and (after[j]['hi'] or 0) > 0: j += 1
            gap = sum(r['dt'] for r in after[k:j]) + (after[j]['dt'] if j < len(after) else 0)
            ser.append((after[k]['n'], j - k, gap))
            k = j + 1
        else:
            k += 1
    res['series'] = len(ser)
    res['gap_ge100'] = sum(1 for s in ser if s[2] >= 100000)
    res['gap_ge1s'] = [s for s in ser if s[2] >= 1000000]
    res['max_gap'] = max([s[2] for s in ser], default=0)
    # PRIO classification of dt>=100ms frames (window+hold)
    cls = dict(PRIO=0, GPUTHR=0, WAIT=0)
    for r in win + hold:
        if r['dt'] < 100000: continue
        if r['prio'] * 2 >= r['dt'] and r['cg'] * 2 < r['dt']: cls['PRIO'] += 1
        elif r['cg'] * 2 >= r['dt']: cls['GPUTHR'] += 1
        else: cls['WAIT'] += 1
    res['cls'] = cls
    res['max_dt'] = max(r['dt'] for r in win + hold)
    return res

if __name__ == '__main__':
    tags = ['c142_%02d' % i for i in range(1, 11)]
    with Pool(5) as pool:
        out = pool.map(one, tags)
    tot = {}
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
        for key in ('win_skip', 'win_held', 'hold_skip', 'hold_held', 'win_ge100', 'hold_ge100', 'series', 'gap_ge100', 'bad', 'missing_x', 'skipped_draws_after'):
            tot[key] = tot.get(key, 0) + r[key]
        for c, v in r['cls'].items(): tot[c] = tot.get(c, 0) + v
    tot['gap_ge1s'] = sum(len(r['gap_ge1s']) for r in out)
    tot['first_held'] = sum(1 for r in out if r['first_held'])
    print('TOTAL', json.dumps(tot))
