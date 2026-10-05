# F20k (HPP-630): model of the KYTY_DIAG_B32 sampler schedule in one window as coded in 13993e3c (diagB32.cpp
# Sampler::Run - relative timer re-armed after Sample; Sample - KernelQuery in every sample >= 40 ms after the
# previous flip; m_cost = whole Sample wall). For a kernel-query cost K: instr_us, dt - instr (INSTR_MADE if < 100 ms,
# item 550(g)(1)), samples vs floor(dt / 10 ms) (I2', item 550(v) RC12). Sample phase 0 at the flip (best case).
import math
P = 5.0; BASE = 0.05  # ms; BASE - a sample without the kernel query [I]
def window(dt, K):
    t = P; n = 0; instr = 0.0
    while t <= dt:
        c = BASE + (K if t >= 40.0 else 0.0)
        n += 1; instr += c
        t += c + P
    return n, instr
print('K_ms dt_ms samples need_I2 i2_ok instr_ms dt_minus_instr INSTR_MADE')
for K in (3.2, 10.7, 13.3):
    for dt in (115, 150, 197, 217, 229, 300):
        n, instr = window(dt, K)
        need = math.floor(dt / (2 * P))
        print('%5.1f %5d %3d %3d %d %6.1f %6.1f %s' % (K, dt, n, need, n >= need, instr, dt - instr, dt - instr < 100))
for K in (3.2, 10.7, 13.3):
    lo = next(d for d in range(100, 2000) if d - window(d, K)[1] >= 100)
    bad = [d for d in range(100, 600) if window(d, K)[0] < math.floor(d / (2 * P))]
    print('K=%.1f: INSTR_MADE for every dt < %d ms; I2 fails first at dt=%s ms' % (K, lo, bad[0] if bad else '-'))
