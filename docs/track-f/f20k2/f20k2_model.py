# F20k2 (HPP-634): independent model of the KYTY_DIAG_B32 sampler schedule as coded in 61b410bf (= main 18dd03a6):
# diagB32.cpp KqSchedule::Due/Done/NewWindow (:180-195), NextBegin (:197), Sampler::Sample (m_t = time after the
# kernel query, m_cost = whole sample incl. query), Sampler::CloseWindow (window (start, flip], carried = query time of
# samples with m_t > flip), Sampler::Run (ProcessFlips before and after each sample, absolute period).
# Not a copy of tests/DiagB32Tests.cpp SimWindow: flips can land INSIDE a sample (the query straddles the flip), the
# boundary work of every flip (ProcessFlips: M5Snapshot, M1, Drain, CloseWindow) costs BND ms [I] and goes into the
# new window (m_win_extra_ns), the sample phase is swept 0..P, the steady regime has 6 normal 33 ms windows and one
# long window before the measured one (last_kq_ns from a real query). M5Refresh (once per 1 s, 14 ms median) is NOT
# modelled - item 552(e)(3), printed by F20l from m5r_us.
# Output: per K and dt the worst case over phases of dt - instr (INSTR_MADE if < 100 ms, item 550(g)(1)), samples vs
# floor(dt / 10 ms) (I2'), kq_n, and whether the window has its own snapshot (kq_t inside the window).
import math, sys
P = 5.0        # ms, kPeriodNs
BASE = 0.05    # ms, a sample without the kernel query [I] (= f20k_model.py)
BND = 0.5      # ms, boundary work per flip [I]
AFTER = 40.0   # ms, kKernelAfterNs
DIV = 10       # kKqBudgetDiv

def run(flips, K, phase, t_end):
    # flips: sorted flip times (ms). Returns samples [(begin, t0, cost, q, kq_t)], extra per window start index.
    st = {'win_start': 0.0, 'win_kq': 0.0, 'last': 0.0}
    samples = []
    extra = {}          # flip index -> boundary ms added to the window that flip opens
    fi = 0              # next unprocessed flip
    now = phase

    def process(now):
        nonlocal fi
        t = now
        while fi < len(flips) and flips[fi] <= t:
            f = flips[fi]
            carried = sum(s[3] for s in samples if s[1] > f)
            st['win_start'] = f
            st['win_kq'] = carried
            extra[fi] = extra.get(fi, 0.0) + BND
            t += BND
            fi += 1
        return t

    begin = now
    while begin < t_end:
        begin = process(begin)               # ProcessFlips before the sample
        q = 0.0
        ws = st['win_start']
        if ws != 0.0 or True:
            due = (begin >= ws + AFTER) and ((st['win_kq'] + st['last']) * DIV <= begin - ws)
            if fi == 0 and ws == 0.0:
                due = False                  # win_start == 0: no flip yet
            if due:
                q = K
                st['win_kq'] += K
                st['last'] = K
        t0 = begin + q
        cost = q + BASE
        samples.append((begin, t0, cost, q, begin + q / 2 if q else None))
        after = process(begin + cost)        # ProcessFlips after the sample
        begin = max(begin + P, after)        # NextBegin
    return samples, extra

def measure(dt, K, phase, regime):
    if regime == 'first':
        flips = [10.0, 10.0 + dt]            # the measured window is the first one with a query; last = 0
        widx = 1
    else:
        flips = [10.0]
        t = 10.0 + 250.0                     # one long window -> a real query sets last = K
        flips.append(t)
        for _ in range(6):
            t += 33.3
            flips.append(t)
        flips.append(t + dt)
        widx = len(flips) - 1
    s, e = run(flips, K, phase, flips[-1] + 60.0)
    a, b = flips[widx - 1], flips[widx]
    win = [x for x in s if a < x[1] <= b]
    instr = sum(x[2] for x in win) + e.get(widx - 1, 0.0)
    kq_n = sum(1 for x in win if x[3])
    own = any(x[4] is not None and a < x[4] <= b for x in win)
    n = len(win)
    need = math.floor(dt / (2 * P))
    return n, need, kq_n, own, instr

out = []
out.append('K_ms dt_ms regime worst_dt_minus_instr max_instr min_samples need i2_all kq_n_range own_snapshot_any INSTR_MADE_any')
viol = []
for K in (3.2, 10.7, 13.3, 20.0):
    for dt in (100, 105, 110, 115, 116, 120, 130, 150, 200, 240, 300):
        for regime in ('first', 'steady'):
            rows = [measure(dt, K, ph / 10.0, regime) for ph in range(0, 50, 5)]
            worst = min(dt - r[4] for r in rows)
            mx = max(r[4] for r in rows)
            mins = min(r[0] for r in rows)
            need = rows[0][1]
            i2 = all(r[0] >= r[1] for r in rows)
            kqs = sorted(set(r[2] for r in rows))
            own = any(r[3] for r in rows)
            made = worst < 100.0
            out.append('%5.1f %4d %-6s %7.2f %7.2f %3d %3d %d %s %d %d' % (K, dt, regime, worst, mx, mins, need, i2,
                                                                          kqs, own, made))
            if K <= 13.3 and dt > 115 and made:
                viol.append('INSTR_MADE K=%.1f dt=%d %s' % (K, dt, regime))
            if dt >= 100 and not i2:
                viol.append('I2 K=%.1f dt=%d %s' % (K, dt, regime))
for v in viol:
    out.append('VIOLATION ' + v)
out.append('criterion item 552(d): INSTR_MADE only at dt <= 115 ms for K <= 13.3 ms; I2\' from 100 ms: ' +
           ('ALL OK' if not viol else 'FAILED (%d)' % len(viol)))
sys.stdout.write('\n'.join(out) + '\n')
