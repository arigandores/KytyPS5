import re
# F11g lead recount (ROADMAP p.389(a)): last DiagBvhNodes lanes= line per F11f tag, identity lanes = sum t, BvhLoopCapTrip count.
for t in ['d11_sg', 'd11_ef', 'd11_vw', 'd11_bh']:
    last = None; n = 0; mode = 0; cap = 0; lvl = 0
    with open(f'C:/kyty/f287/f11f/log_{t}.txt', 'rb') as f:
        for l in f:
            if b'DiagBvhNodes:' in l:
                if b'lanes=' in l: last = l; n += 1
                elif b'mode=1' in l: mode += 1
            elif b'BvhLoopCapTrip:' in l: cap += 1
            elif b'Level has started:' in l: lvl += 1
    print(t, 'lanes_lines', n, 'mode_lines', mode, 'BvhLoopCapTrip', cap, 'level_lines', lvl)
    if last is None:
        print('  no lanes= line'); continue
    d = dict(re.findall(r'(\w+)=(\S+)', last.decode('utf-8', 'replace').strip()))
    print('  ', {k: d.get(k) for k in ['lanes', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 'size_viol', 'b_tri', 'b_box', 'b_t7', 'traps', 'trap_lanes']})
    t0, t1, t2, t3 = [int(d[k]) for k in ['t0', 't1', 't2', 't3']]
    print('   sum_ok', int(d['lanes']) == sum(int(d['t%d' % i]) for i in range(8)), 't0==2*t2', t0 == 2 * t2, '2*t1==3*t2', 2 * t1 == 3 * t2, 't1==t3', t1 == t3)
