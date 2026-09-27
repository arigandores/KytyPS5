"""Independent recount of the sealed skipceil ABBA runs of session 123 (audit, step 9, HPP-32).

Written by the Session Auditor from the TEXT of pred/01_skc123.md only; shares no code with skc123.py, smk123.py or
ref123.py (none is imported or read). Usage: python recount123.py <log> [--boot N] [--seed S]
"""
import math
import random
import re
import sys

FIELD = re.compile(rb'(\w+)=(-?\d+)')
KINDS = (b'FrameTrace: ', b'FrameTrace-draw: ', b'FrameTrace-x: ')
START, PERIOD = 1800, 90
W0, W1 = 10, 87          # window positions (seal: 10..87)


def parse(path):
    rows = {k: {} for k in KINDS}
    dup = {k: 0 for k in KINDS}
    arms = []
    first_gatearm_line = None
    order_x = []          # n of every -x row in log order (for "after first GateArm" sums)
    with open(path, 'rb') as f:
        for ln, line in enumerate(f):
            if line.startswith(b'GateArm:'):
                d = dict((k.decode(), v.decode()) for k, v in re.findall(rb'(\w+)=(\S+)', line))
                arms.append(d)
                if first_gatearm_line is None:
                    first_gatearm_line = ln
                continue
            for k in KINDS:
                if line.startswith(k):
                    d = {a.decode(): int(b) for a, b in FIELD.findall(line)}
                    n = d.get('n')
                    if n is None:
                        break
                    if n in rows[k]:
                        dup[k] += 1
                    rows[k][n] = d
                    if k == b'FrameTrace-x: ':
                        order_x.append((ln, n, d))
                    break
    return rows, dup, arms, first_gatearm_line, order_x


def mean(a):
    return sum(a) / len(a)


def se2(a):
    m = mean(a)
    v = sum((x - m) ** 2 for x in a) / (len(a) - 1)
    return 2 * math.sqrt(v / len(a))


def main():
    path = sys.argv[1]
    nboot = 20000
    if '--boot' in sys.argv:
        nboot = int(sys.argv[sys.argv.index('--boot') + 1])
    rows, dup, arms, fgl, order_x = parse(path)
    M, D, X = (rows[k] for k in KINDS)
    print('file', path)
    print('rows main/draw/x', len(M), len(D), len(X), 'dups', list(dup.values()))
    print('GateArm lines', len(arms), 'texts', sorted(set(a['text'] for a in arms)))
    # schedule check
    for b, a in enumerate(arms):
        exp_arm = [0, 1, 1, 0][b % 4]
        if int(a['block']) != b or int(a['frame']) != START + PERIOD * b or int(a['arm']) != exp_arm \
                or a['text'] != 'skipceil=%d' % exp_arm:
            print('SCHEDULE MISMATCH at', b, a)
    nblocks = len(arms)

    def frames(b, lo=0, hi=89):
        return [START + 1 + PERIOD * b + p for p in range(lo, hi + 1)]

    def complete(b):
        arm = int(arms[b]['arm'])
        for n in frames(b, W0, W1):
            if n not in M or n not in D or n not in X:
                return False
            if M[n].get('arm') != arm or M[n].get('blk') != b:
                return False
        return True

    comp = [complete(b) for b in range(nblocks)]
    print('blocks', nblocks, 'complete', sum(comp))

    def outlier(b):
        return any(M.get(n, {}).get('dt_us', 0) >= 500000 for n in frames(b))

    pairs = []
    dropped = 0
    for k in range(nblocks // 2):
        b0, b1 = 2 * k, 2 * k + 1
        if not (comp[b0] and comp[b1]):
            continue
        if outlier(b0) or outlier(b1):
            dropped += 1
            continue
        pairs.append((b0, b1))
    print('complete pairs', len(pairs) + dropped, 'dropped', dropped, 'population', len(pairs))

    def est(b, strat=True, lo=W0, hi=W1):
        ns = frames(b, lo, hi)
        dts = [M[n]['dt_us'] for n in ns]
        if int(arms[b]['arm']) == 0 or not strat:
            return mean(dts)
        h = [M[n]['dt_us'] for n in ns if X[n]['skc_held'] >= 1]
        o = [M[n]['dt_us'] for n in ns if X[n]['skc_held'] < 1]
        return 0.5 * mean(h) + 0.5 * mean(o), len(h), len(o)

    ds, e0s, e1s, simple, cls = [], [], [], [], []
    for b0, b1 in pairs:
        a0 = b0 if int(arms[b0]['arm']) == 0 else b1
        a1 = b1 if a0 == b0 else b0
        e0 = est(a0)
        e1, nh, no = est(a1)
        ds.append(e0 - e1)
        e0s.append(e0)
        e1s.append(e1)
        simple.append(e0 - est(a1, strat=False))
        cls.append((nh, no))
    Dm, S2 = mean(ds), se2(ds)
    print('DELTA est(0)-est(1) = %.1f +- %.1f us (2SE), pairs %d' % (Dm, S2, len(ds)))
    print('  est A %.1f  est B %.1f' % (mean(e0s), mean(e1s)))
    print('  Delta-2SE %.1f  Delta+2SE %.1f' % (Dm - S2, Dm + S2))
    verdict = 'CLOSED' if Dm + S2 < 500 else ('CEILING_MEASURED' if Dm - S2 >= 500 else 'NOT_RESOLVED')
    print('  reading:', verdict)
    print('  simple arm-1 mean Delta %.1f +- %.1f' % (mean(simple), se2(simple)))
    print('  classes held/other min %d/%d max %d/%d' % (min(c[0] for c in cls), min(c[1] for c in cls),
                                                         max(c[0] for c in cls), max(c[1] for c in cls)))
    # sensitivity: window 10..88 (programme rule), simple estimator both arms
    alt = []
    for b0, b1 in pairs:
        a0 = b0 if int(arms[b0]['arm']) == 0 else b1
        a1 = b1 if a0 == b0 else b0
        if all(n in M for n in frames(a0, 10, 88) + frames(a1, 10, 88)):
            alt.append(est(a0, lo=10, hi=88) - est(a1, strat=False, lo=10, hi=88))
    print('  sensitivity window 10..88 simple: %.1f +- %.1f (%d pairs)' % (mean(alt), se2(alt), len(alt)))
    # bootstrap over pairs
    rnd = random.Random(12345)
    bs = sorted(mean([ds[rnd.randrange(len(ds))] for _ in ds]) for _ in range(nboot))
    print('  bootstrap 95%% [%.1f, %.1f]' % (bs[int(0.025 * nboot)], bs[int(0.975 * nboot)]))
    # median-of-pairs
    sd = sorted(ds)
    print('  median pair d %.1f, min %.1f, max %.1f' % (sd[len(sd) // 2], sd[0], sd[-1]))

    def pairdiff(field, src, per='sum'):
        out = []
        for b0, b1 in pairs:
            a0 = b0 if int(arms[b0]['arm']) == 0 else b1
            a1 = b1 if a0 == b0 else b0
            v0 = mean([src[n][field] for n in frames(a0, W0, W1)])
            v1 = mean([src[n][field] for n in frames(a1, W0, W1)])
            out.append(v1 - v0)
        return mean(out), se2(out)

    print('d cpu_gpu_us (1-0) %.1f +- %.1f' % pairdiff('cpu_gpu_us', M))
    print('d draws (1-0) %.1f +- %.1f' % pairdiff('draws', M))
    print('d gw_proc_ns/1000 (1-0) %.1f +- %.1f' % tuple(v / 1000 for v in pairdiff('gw_proc_ns', X)))
    print('d gw_flip_ns/1000 (1-0) %.1f +- %.1f' % tuple(v / 1000 for v in pairdiff('gw_flip_ns', X)))
    print('d gw_idle_ns/1000 (1-0) %.1f +- %.1f' % tuple(v / 1000 for v in pairdiff('gw_idle_ns', X)))
    # draw-adjusted
    adj = []
    for b0, b1 in pairs:
        a0 = b0 if int(arms[b0]['arm']) == 0 else b1
        a1 = b1 if a0 == b0 else b0
        dr0 = mean([M[n]['draws'] for n in frames(a0, W0, W1)])
        dr1 = mean([M[n]['draws'] for n in frames(a1, W0, W1)])
        adj.append(est(a0) * dr1 / dr0 - est(a1)[0])
    print('draw-adjusted Delta %.1f +- %.1f' % (mean(adj), se2(adj)))
    # BDA regime per arm-0 block
    bda0, bda1 = [], []
    for b0, b1 in pairs:
        for b in (b0, b1):
            v = mean([D[n]['bda_scan'] for n in frames(b, W0, W1)])
            (bda0 if int(arms[b]['arm']) == 0 else bda1).append(v)
    print('bda_scan arm0 blocks min %.1f max %.1f mean %.1f | arm1 mean %.1f' % (min(bda0), max(bda0), mean(bda0),
                                                                              mean(bda1)))
    # G8 DRS sums
    sums = {0: [0, 0], 1: [0, 0]}
    for b0, b1 in pairs:
        for b in (b0, b1):
            a = int(arms[b]['arm'])
            for n in frames(b, W0, W1):
                sums[a][0] += X[n]['rt_kpx']
                sums[a][1] += X[n]['rt_att']
    r0 = sums[0][0] / sums[0][1]
    r1 = sums[1][0] / sums[1][1]
    print('G8 ratio0 %.6f ratio1 %.6f ratio-1 %.5f' % (r0, r1, r1 / r0 - 1))
    # G7 zero invariants over every -x row; K16 after first GateArm
    for f in ('skc_bad', 'skc_xthr', 'skc_refuse', 'skc_mark_miss'):
        print('sum', f, sum(d.get(f, 0) for _, _, d in order_x))
    for f in ('skc_lod_pmiss', 'skc_lod_noanc', 'skc_lod_pbad'):
        print('sum after GateArm', f, sum(d.get(f, 0) for ln, _, d in order_x if ln > fgl))
    mk = sum(d.get('skc_mark', 0) for _, _, d in order_x)
    hd = sum(d.get('skc_held', 0) for _, _, d in order_x)
    print('sum mark %d held %d skipf %d' % (mk, hd, sum(d.get('skc_skipf', 0) for _, _, d in order_x)))
    # arm-0 cleanliness: skc_held / skc_skipf in arm-0 windows
    bad0 = 0
    for b0, b1 in pairs:
        for b in (b0, b1):
            if int(arms[b]['arm']) == 0:
                bad0 += sum(X[n]['skc_held'] + X[n]['skc_skipf'] + X[n]['skc_sd'] for n in frames(b, W0, W1))
    print('arm-0 windows sum held+skipf+sd', bad0)
    # T5 held fraction per arm-1 block and adjacency
    fr, adjc = [], 0
    for b0, b1 in pairs:
        for b in (b0, b1):
            if int(arms[b]['arm']) == 1:
                hs = [X[n]['skc_held'] >= 1 for n in frames(b, W0, W1)]
                fr.append(sum(hs) / 78)
                adjc = max(adjc, sum(1 for i in range(77) if hs[i] and hs[i + 1]))
    print('T5 held fraction min %.3f max %.3f, max adjacent held %d' % (min(fr), max(fr), adjc))
    # G2 largest dt after frame 1800, gap
    after = [(M[n]['dt_us'], n) for n in M if n > START]
    print('largest dt_us after 1800', max(after))
    ns = sorted(M)
    miss = [(ns[i], ns[i + 1]) for i in range(len(ns) - 1) if ns[i + 1] - ns[i] != 1 and ns[i] > START]
    print('holes in main n after 1800', miss[:5], len(miss))
    print('last main n', ns[-1])


if __name__ == '__main__':
    main()
