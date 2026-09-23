# Independent recount of the ABBA runs (auditor, session 104). Own code; reads only the pickles
# written by parse_log.py (which reads the raw logs).
import pickle, statistics as st, math, re, sys, json

R = 'C:/kyty/s104/audit104/recount/'
PERIOD, START, FIRST, LO, HI = 90, 1800, 2100, 60, 88   # HI inclusive


def load(tag):
    d = pickle.load(open(R + tag + '.pkl', 'rb'))
    rows = {}
    conflicts = 0
    for n, kinds in d['rows'].items():
        m = {}
        for kind in ('main', 'draw', 'x'):
            for k, v in kinds.get(kind, {}).items():
                if k in m and k != 'n' and m[k] != v:
                    conflicts += 1
                    m[k + '@' + kind] = v
                    continue
                m.setdefault(k, v)
        m['_kinds'] = tuple(sorted(kinds))
        rows[n] = m
    d['merged'] = rows
    d['conflicts'] = conflicts
    return d


def gate_table(d):
    g = {}
    rx = re.compile(r'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
    bad = 0
    for line in d['gate']:
        m = rx.match(line)
        if not m:
            bad += 1
            continue
        arm, arms, blk, frame, period, abba, text = m.groups()
        g[int(blk)] = (int(arm), int(frame), int(period), int(abba), text.strip())
    return g, bad


def derive(r):
    x = dict(r)
    if 'cpu_gpu_us' in r and 'spin_gpu_us' in r:
        x['cpu_net_us'] = r['cpu_gpu_us'] - r['spin_gpu_us']
    if 'da_walk_us' in r and 'da_queue_us' in r:
        x['spine_us'] = r['da_walk_us'] - r['da_queue_us']
    if 'pl_pref_ns' in r and 'da_queue_us' in r:
        x['spine_pref_us'] = r['pl_pref_ns'] / 1000.0 - r['da_queue_us']
    for k in list(r):
        if k.startswith('pl_') and k.endswith('_ns'):
            x[k[:-3] + '_usx'] = r[k] / 1000.0
    if all(k in r for k in ('pl_em_n', 'pl_prog_n', 'pl_pipe_n', 'pl_cs_n', 'a_mut_n')):
        x['t_in'] = 5 * r['pl_em_n'] + 3 * (r['pl_prog_n'] + r['pl_pipe_n'] + r['pl_cs_n']) + r['a_mut_n']
    if all(k in r for k in ('mh_n', 'mh_disp_n', 'bda_n')):
        x['mw_expect'] = 2 * r['mh_n'] + r['mh_disp_n'] + r['bda_n']
    if all(k in r for k in ('rt_kpx', 'rt_att')) and r['rt_att']:
        x['area'] = r['rt_kpx'] / r['rt_att']
    return x


def select(d, lo=LO, hi=HI, first=FIRST):
    rows = d['merged']
    g, gbad = gate_table(d)
    # blocks by the main line's blk= token (independent of n arithmetic)
    byblk = {}
    for n, r in rows.items():
        if 'blk' in r and 'arm' in r:
            byblk.setdefault(r['blk'], []).append(n)
    info = {'gate_bad': gbad, 'gate_blocks': len(g)}
    elig = {}
    arm_of = {}
    notes = []
    for b in sorted(g):
        arm, frame, period, abba, text = g[b]
        if frame != START + PERIOD * b or period != PERIOD or abba != 1:
            notes.append(('gatearm_mismatch', b, frame, period, abba))
        arm_of[b] = arm
        ns = sorted(byblk.get(b, []))
        if len(ns) != PERIOD or ns != list(range(ns[0], ns[0] + PERIOD)):
            notes.append(('incomplete', b, len(ns)))
            continue
        if ns[0] != START + 1 + PERIOD * b:
            notes.append(('n_offset', b, ns[0]))
        if any(rows[n]['arm'] != arm for n in ns):
            notes.append(('row_arm_mismatch', b))
        kept = ns[lo:hi + 1]
        if min(kept) < first:
            continue
        elig[b] = kept
    pairs = []
    excl = []
    top = max(g) if g else -1
    for q in range(0, top + 1, 4):
        quart = [q, q + 1, q + 2, q + 3]
        if all(b in elig for b in quart):
            # ABBA check: arms must be A B B A
            if [arm_of[b] for b in quart] != [0, 1, 1, 0]:
                notes.append(('not_abba', q, [arm_of[b] for b in quart]))
            pairs += [(q, q + 1), (q + 2, q + 3)]
        else:
            excl += [b for b in quart if b in elig]
    info['notes'] = notes
    info['excluded'] = excl
    return elig, arm_of, pairs, info


def block_mean(d, ns, key):
    vals = []
    for n in ns:
        x = derive(d['merged'][n])
        if key not in x:
            return None
        vals.append(x[key])
    return sum(vals) / len(vals)


def analyse(d, keys, lo=LO, hi=HI):
    elig, arm_of, pairs, info = select(d, lo, hi)
    used = sorted({b for p in pairs for b in p})
    out = {'pairs': len(pairs), 'blocks': len(used), 'excluded': info['excluded'], 'notes': info['notes']}
    lev = {}
    dif = {}
    for key in keys:
        bm = {b: block_mean(d, elig[b], key) for b in used}
        if any(v is None for v in bm.values()):
            lev[key] = None
            continue
        lev[key] = tuple(st.median([bm[b] for b in used if arm_of[b] == a]) for a in (0, 1))
        diffs = []
        for p in pairs:
            b1 = [b for b in p if arm_of[b] == 1][0]
            b0 = [b for b in p if arm_of[b] == 0][0]
            diffs.append(bm[b1] - bm[b0])
        m = sum(diffs) / len(diffs)
        sd = st.stdev(diffs) if len(diffs) > 1 else float('nan')
        se = sd / math.sqrt(len(diffs))
        dif[key] = (m, 2 * se, m / se if se else float('nan'), len(diffs), sd)
    out['levels'] = lev
    out['diffs'] = dif
    out['elig'] = elig
    out['arm_of'] = arm_of
    out['used'] = used
    out['pairlist'] = pairs
    return out


def kept_sum(d, res, arm, key):
    s = 0
    for b in res['used']:
        if res['arm_of'][b] != arm:
            continue
        for n in res['elig'][b]:
            x = derive(d['merged'][n])
            if key not in x:
                return None
            s += x[key]
    return s


def retained_mean(d, res, arm, key):
    v = []
    for b in res['used']:
        if res['arm_of'][b] != arm:
            continue
        for n in res['elig'][b]:
            v.append(d['merged'][n][key])
    return sum(v) / len(v)


def fmt(t):
    return ' '.join('%.4f' % v if isinstance(v, float) else str(v) for v in t)


if __name__ == '__main__':
    tag = sys.argv[1]
    keys = sys.argv[2].split(',')
    d = load(tag)
    res = analyse(d, keys)
    print(tag, 'conflicts', d['conflicts'], 'pairs', res['pairs'], 'blocks', res['blocks'],
          'excluded', res['excluded'], 'notes', res['notes'][:10])
    for k in keys:
        print('  %-16s level0/1 %s   d %s' % (k, res['levels'][k] and fmt(res['levels'][k]),
                                           res['diffs'].get(k) and fmt(res['diffs'][k])))
