# -*- coding: utf-8 -*-
"""Session 122 audit: independent recount of the sealed burn ABBAs (step 4, HPP-7).

Written by the Session Auditor from the log format and the TEXT of pred/01_map122.md only.
Shares no code with map122.py (not imported, not copied). Reads C:/kyty/s122/log_<tag>.txt.

Rules re-derived from the seal:
  * blocks come from `GateArm:` lines only (frame=F, arm=a); a row n belongs to block k when F_k < n <= F_k + period;
    position = n - F_k - 1 (established from the data, see OFFSET: the row n = F still carries the outgoing arm's
    burn counter and `arm=` field, the first row of the new arm is F + 1); the estimator window is positions 10..88; a row counts only with draws > 300;
  * a block is complete when the next GateArm line exists and every window position 10..88 has a main row;
  * pairs are (2k, 2k+1) with both blocks complete; per pair Delta = mean_B(dt) - mean_A(dt);
    2SE = 2 * stdev(n-1) / sqrt(pairs); s = Delta / 2000;
  * zone: SUPERLINEAR s-2SE>1; CRITICAL s-2SE>0.5 and s+2SE>=1; NOT_CRITICAL s+2SE<0.3; else NOT_RESOLVED;
  * outlier: any row of a block (positions 0..period-1) with dt_us >= 500000 drops the pair;
  * HEADROOM: share of A-arm window rows (population pairs) with dt_us < 25000 >= 0.95.
Usage: python recount122.py <tag> [<tag> ...]   (prints one JSON object per tag and a summary line)
"""
import json
import math
import re
import sys

ROOT = 'C:/kyty/s122/'
DOSE_US = 2000.0
KV = re.compile(rb'(?<![A-Za-z0-9_])([A-Za-z0-9_]+)=(-?\d+)')
GATE = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
LO, HI = 10, 88
OFFSET = 1  # row n of block k at position p: n = F_k + OFFSET + p (measured: first burnt row after an A->B switch is F+1)


def kv(line):
    return {k.decode(): int(v) for k, v in KV.findall(line)}


def mean(xs):
    return sum(xs) / len(xs)


def sd(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def zone(s, se):
    if s - se > 1.0:
        return 'SUPERLINEAR'
    if s - se > 0.5 and s + se >= 1.0:
        return 'CRITICAL'
    if s + se < 0.3:
        return 'NOT_CRITICAL'
    return 'NOT_RESOLVED'


def read(tag):
    gates = []
    main, draw, x = {}, {}, {}
    lines = {'skip': [], 'pin': 0, 'burn_selftest': 0, 'burn_arm': [], 'burn_late': 0, 'burn_rej': 0, 'no_tsc': 0,
             'fatal': []}
    with open(ROOT + 'log_%s.txt' % tag, 'rb') as f:
        for ln in f:
            ln = ln.rstrip(b'\r\n')
            if ln.startswith(b'FrameTrace: n='):
                d = kv(ln)
                main[d['n']] = d
            elif ln.startswith(b'FrameTrace-draw: n='):
                d = kv(ln)
                draw[d['n']] = d
            elif ln.startswith(b'FrameTrace-x: n='):
                d = kv(ln)
                x[d['n']] = d
            elif ln.startswith(b'GateArm:'):
                m = GATE.match(ln)
                gates.append(tuple(int(m.group(i)) for i in range(1, 7)) + (m.group(7).decode(),))
            elif b'AsyncPipelines: skipped draw' in ln:
                lines['skip'].append(ln[:200].decode('latin1'))
            elif ln.startswith(b'GpuClockPin: mode 1'):
                lines['pin'] += 1
            elif ln.startswith(b'Burn: selftest'):
                lines['burn_selftest'] += 1
            elif ln.startswith(b'Burn: arm'):
                lines['burn_arm'].append(ln.decode('latin1'))
            elif ln.startswith(b'BurnLate:'):
                lines['burn_late'] += 1
            elif ln.startswith(b'Burn:') and b'rejected' in ln:
                lines['burn_rej'] += 1
            elif ln.startswith(b'Burn: no calibrated'):
                lines['no_tsc'] += 1
            elif ln.startswith((b'--- Error', b'--- Fatal', b'--- std::terminate', b'--- abort')):
                lines['fatal'].append(ln[:120].decode('latin1'))
    return gates, main, draw, x, lines


def recount(tag):
    gates, main, draw, x, lines = read(tag)
    period = gates[0][4]
    code_b = None
    blocks = []
    for i, g in enumerate(gates):
        arm, arms, blk, frame, per, abba, text = g
        assert per == period and blk == i, (tag, g)
        ended = i + 1 < len(gates)
        win = [n for n in range(frame + OFFSET + LO, frame + OFFSET + HI + 1)]
        have = all(n in main for n in win)
        streams = all(n in draw and n in x for n in win)
        blocks.append(dict(k=i, arm=arm, frame=frame, text=text, complete=ended and have, streams=streams,
                           allrows=[n for n in range(frame + OFFSET, frame + OFFSET + period) if n in main], win=win))
        if arm == 1:
            code_b = int(text.split('=')[1]) // 100000
    # ABBA order check: blocks 0,3,4,7,8,... are A
    abba_ok = all(b['arm'] == (0 if (b['k'] % 4) in (0, 3) else 1) for b in blocks)
    # arm= field of main rows vs GateArm (cross-check only)
    arm_field_mismatch = sum(1 for b in blocks for n in b['allrows'] if main[n].get('arm') != b['arm'])
    pairs, dropped = [], []
    for k in range(0, len(blocks) - 1, 2):
        a, b = blocks[k], blocks[k + 1]
        if not (a['complete'] and b['complete']):
            continue
        out = [(n, main[n]['dt_us']) for bb in (a, b) for n in bb['allrows'] if main[n]['dt_us'] >= 500000]
        if out:
            dropped.append((k, out))
            continue
        pairs.append((a, b) if a['arm'] == 0 else (b, a))
    diffs, adj, ddraw, dcpu, dgpu = [], [], [], [], []
    rows = {0: [], 1: []}
    for A, B in pairs:
        ra = [main[n] for n in A['win'] if main[n]['draws'] > 300]
        rb = [main[n] for n in B['win'] if main[n]['draws'] > 300]
        rows[0] += ra
        rows[1] += rb
        ma, mb = mean([r['dt_us'] for r in ra]), mean([r['dt_us'] for r in rb])
        da, db = mean([r['draws'] for r in ra]), mean([r['draws'] for r in rb])
        diffs.append(mb - ma)
        adj.append(mb - ma * db / da)
        ddraw.append(db - da)
        dcpu.append(mean([r['cpu_gpu_us'] for r in rb]) - mean([r['cpu_gpu_us'] for r in ra]))
        dgpu.append(mean([r['gpu_busy_us'] for r in rb]) - mean([r['gpu_busy_us'] for r in ra]))
    P = len(pairs)
    res = dict(tag=tag, code_b=code_b, gates=len(gates), period=period, abba_ok=abba_ok,
               arm_field_mismatch=arm_field_mismatch, complete=sum(b['complete'] for b in blocks),
               streams_all=all(b['streams'] for b in blocks if b['complete']), pairs=P,
               dropped_pairs=dropped, rows_A=len(rows[0]), rows_B=len(rows[1]))
    if P >= 2:
        d, se = mean(diffs), 2 * sd(diffs) / math.sqrt(P)
        s, sse = d / DOSE_US, se / DOSE_US
        res.update(delta=d, se2=se, s=s, s_se2=sse, lo=s - sse, hi=s + sse, zone=zone(s, sse))
        import random
        rng = random.Random(122)
        boots = sorted(mean([diffs[rng.randrange(P)] for _ in range(P)]) / DOSE_US for _ in range(20000))
        res.update(boot_lo=boots[500], boot_hi=boots[19499], boot_zone_edges=dict(
            p_s_below_0_5=sum(b <= 0.5 for b in boots) / 20000.0, p_s_at_least_1=sum(b >= 1.0 for b in boots) / 20000.0))
        ad, ase = mean(adj), 2 * sd(adj) / math.sqrt(P)
        res.update(adj_delta=ad, adj_s=ad / DOSE_US, adj_s_se2=ase / DOSE_US, adj_zone=zone(ad / DOSE_US, ase / DOSE_US),
                   d_draws=mean(ddraw), d_draws_se2=2 * sd(ddraw) / math.sqrt(P),
                   d_cpu_gpu=mean(dcpu), d_cpu_gpu_se2=2 * sd(dcpu) / math.sqrt(P),
                   d_gpu_busy=mean(dgpu), d_gpu_busy_se2=2 * sd(dgpu) / math.sqrt(P))
        mA = mean([r['dt_us'] for r in rows[0]])
        mB = mean([r['dt_us'] for r in rows[1]])
        res.update(mean_dt_A=mA, mean_dt_B=mB, speed_A=16667 / mA, speed_B=16667 / mB)
        res['headroom_share'] = sum(1 for r in rows[0] if r['dt_us'] < 25000) / len(rows[0])
        res['reading'] = 'HEADROOM' if res['headroom_share'] >= 0.95 else 'SPEED'
        for arm in (0, 1):
            h = {}
            for r in rows[arm]:
                v = int(r['dt_us'] / 16666.7 + 0.5)
                h[v] = h.get(v, 0) + 1
            res['vb_%s' % 'AB'[arm]] = {k: round(100.0 * c / len(rows[arm]), 2) for k, c in sorted(h.items())}
        allr = rows[0] + rows[1]
        h = {}
        for r in allr:
            v = int(r['dt_us'] / 16666.7 + 0.5)
            h[v] = h.get(v, 0) + 1
        res['vb_all'] = {k: round(100.0 * c / len(allr), 2) for k, c in sorted(h.items())}
        # BDA regime per arm (window rows of the population)
        for arm, key in ((0, 'A'), (1, 'B')):
            ns = [n for A, B in pairs for n in (A if arm == 0 else B)['win'] if main[n]['draws'] > 300]
            res['bda_scan_' + key] = mean([draw[n]['bda_scan'] for n in ns])
    # burn counters: over ALL -x rows
    res['burn_cpu_bad_all'] = sum(v.get('burn_cpu_bad', 0) for v in x.values())
    grp = {1: 'g', 2: 'r', 3: 'm', 4: 't', 5: 'r', 6: 'm', 7: 't', 8: 'p'}.get(code_b)
    groups = 'grmtp'
    arm_bad = []
    doses = []
    for b in blocks:
        if not b['complete']:
            continue
        for n in b['win']:
            if n not in x:
                continue
            xv = x[n]
            for gname in groups:
                val = xv.get('burn_%s_ns' % gname, 0)
                if b['arm'] == 0 and val:
                    arm_bad.append((b['k'], n, gname, val))
                if b['arm'] == 1 and gname != grp and val:
                    arm_bad.append((b['k'], n, gname, val))
            if b['arm'] == 1:
                doses.append(xv.get('burn_%s_ns' % grp, 0) / 1000.0)
    res['arming_violations'] = len(arm_bad)
    res['arming_examples'] = arm_bad[:5]
    res['dose_mean_us'] = mean(doses) if doses else None
    res['dose_min_us'] = min(doses) if doses else None
    res['dose_max_us'] = max(doses) if doses else None
    # the position-89 rule: burn seen at position 89 of an A block that precedes a B block, and at position 0..9 of B
    p89, p0 = [], []
    for i, b in enumerate(blocks[:-1]):
        nb = blocks[i + 1]
        if b['arm'] == 0 and nb['arm'] == 1:
            n89 = b['frame'] + OFFSET + 89
            if n89 in x:
                p89.append(x[n89].get('burn_%s_ns' % grp, 0) / 1000.0)
            n0 = nb['frame'] + OFFSET
            if n0 in x:
                p0.append(x[n0].get('burn_%s_ns' % grp, 0) / 1000.0)
    res['A_to_B_pos89_burn_us_mean'] = mean(p89) if p89 else None
    res['A_to_B_newpos0_burn_us_mean'] = mean(p0) if p0 else None
    res['skip_lines'] = len(lines['skip'])
    res['pin_lines'] = lines['pin']
    res['burn_selftest'] = lines['burn_selftest']
    res['burn_arm_lines'] = sorted(set(lines['burn_arm']))
    res['burnlate_lines'] = lines['burn_late']
    res['burn_rejected'] = lines['burn_rej']
    res['fatal'] = lines['fatal']
    res['max_dt_in_blocks'] = max(main[n]['dt_us'] for b in blocks if b['complete'] for n in b['allrows'])
    return res


if __name__ == '__main__':
    out = []
    for t in sys.argv[1:]:
        r = recount(t)
        out.append(r)
        print(json.dumps(r, ensure_ascii=False, default=str))
    print('SUMMARY')
    for r in out:
        if 'delta' in r:
            print('%-9s code %s pairs %d  Delta %+.1f +- %.1f  s %.3f +- %.3f (%.3f..%.3f) %s  adj s %.3f +- %.3f %s  '
                  'reading %s share %.4f  bda A %.1f B %.1f  dose %.1f  viol %d  cpu_bad %d  skip %d  pin %d' % (
                      r['tag'], r['code_b'], r['pairs'], r['delta'], r['se2'], r['s'], r['s_se2'], r['lo'], r['hi'],
                      r['zone'], r['adj_s'], r['adj_s_se2'], r['adj_zone'], r['reading'], r['headroom_share'],
                      r['bda_scan_A'], r['bda_scan_B'], r['dose_mean_us'] or 0, r['arming_violations'],
                      r['burn_cpu_bad_all'], r['skip_lines'], r['pin_lines']))
        else:
            print(r['tag'], 'NOT EVALUABLE pairs', r['pairs'])
