"""Track F link F25a (HPP-660): a model of the KYTY_DIAG_B32 window of a long frame - the history ring, Gaps() and the reader
rules (i) HOST_FREEZE / (ii) NO_SAMPLES of b32_read.py - for kHist 512 (F20j4 f2307b02) and the proposed 4096.  ASCII only.

    python win_f25a.py [--out <txt>]

Model (code f2307b02:src/common/diagB32.cpp WindowSamples :235, Gaps :166, CloseWindow :1736-1738): samples every P = 5 ms, the ring
holds the last kHist samples; at the flip the window is (start, flip]; samples of the ring inside the window; exhausted = no ring
sample <= start and the ring is full -> ring_drop++ (a zero invariant of the window, ring_drop_w); sgap_max = the largest gap with
the edges start -> first sample, last sample -> flip; i2 = samples >= window / (2 P).  Reader (e8ea0a57 b32_read.py :30-:33):
(i) HOST_FREEZE if sgap_max >= 0.5 x E (E = dt - median, median 17 000 us - the hold median of the four V of f25a, 16 713..17 813);
(ii) NO_SAMPLES if i2 = 0 or ring_drop_w != 0.  Only (i) and (ii) are modelled - the rest of the rule needs the real thread rows.
The P jitter of the real timer (samples later than 5 ms) makes the ring cover MORE time; the nominal P is the worst case.
"""
import sys

P_US = 5000
MEDIAN_US = 17000


def window(dt_us, k_hist, p_us=P_US):
    # samples at flip - j*P for j = 0..; the ring holds the last k_hist of them
    n_in = dt_us // p_us                       # samples strictly inside (start, flip] at nominal P (flip on a sample)
    held = min(n_in, k_hist)
    exhausted = n_in > k_hist                  # no held sample <= start
    first_gap = dt_us - (held - 1) * p_us if held else dt_us
    sgap_max = max(first_gap, p_us)
    i2 = held >= dt_us // (2 * p_us)
    e = dt_us - MEDIAN_US
    if sgap_max >= 0.5 * e:
        cls = 'HOST_FREEZE (i)'
    elif not i2 or exhausted:
        cls = 'NO_SAMPLES (ii)%s%s' % (' i2=0' if not i2 else '', ' ring_drop_w=1' if exhausted else '')
    else:
        cls = 'readable -> (iii)/(iv)'
    return dict(held=held, covered_us=held * p_us, exhausted=exhausted, sgap_max=sgap_max, i2=i2, cls=cls)


def main(argv):
    out = ['win_f25a: kHist x P = 512 x 5 ms = 2.56 s (F20j4) vs 4096 x 5 ms = 20.48 s (proposed); median %d us' % MEDIAN_US]
    for dt in (150000, 1000000, 1478862, 2333729, 2560000, 2600000, 4624510, 5100000, 5200000, 6614314, 10000000, 20000000, 21000000):
        for k in (512, 4096):
            w = window(dt, k)
            out.append('dt_us %8d kHist %4d: samples held %4d (covers %.2f s of %.2f s) exhausted %d sgap_max_us %8d i2 %d -> %s' % (
                dt, k, w['held'], w['covered_us'] / 1e6, dt / 1e6, w['exhausted'], w['sgap_max'], w['i2'], w['cls']))
    # the two registered K2 frames
    ok = True
    ok &= window(4624510, 512)['cls'].startswith('NO_SAMPLES')
    ok &= window(6614314, 512)['cls'].startswith('HOST_FREEZE')
    ok &= window(4624510, 4096)['cls'].startswith('readable')
    ok &= window(6614314, 4096)['cls'].startswith('readable')
    ok &= window(2333729, 512)['cls'].startswith('readable')
    ok &= window(1000000, 512)['cls'].startswith('readable')
    # edge: exhaustion starts above kHist x P, the false HOST_FREEZE from dt >= 2 x (kHist - 1) x P - median = 5.093 s
    ok &= not window(2560000, 512)['exhausted'] and window(2565000, 512)['exhausted']
    ok &= window(5085000, 512)["cls"].startswith("NO_SAMPLES") and window(5100000, 512)['cls'].startswith('HOST_FREEZE')
    out.append('K2 frames of the register: B36 v143_08 n 14701 6 614 314 us, B40 v145_14 n 7249 4 624 510 us')
    out.append('MODEL CHECKS %s' % ('ALL OK' if ok else 'FAILED'))
    txt = '\n'.join(out) + '\n'
    if '--out' in argv:
        open(argv[argv.index('--out') + 1], 'w', encoding='ascii', newline='\n').write(txt)
    sys.stdout.write(txt)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
