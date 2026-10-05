# F20k (HPP-630): FrameTrace dt_us distribution in F20e / F20c logs - are there windows longer than the history ring
# (512 x 5 ms = 2.56 s) or of 100..230 ms (INSTR_MADE band at the measured kernel-query cost)?  Measurement only.
import re, sys
rx = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
lv = b'Level has started:'
for path in sys.argv[1:]:
    big = []; n100 = 0; n100_230 = 0; nmax = 0; lvl_n = None; last_n = 0; total = 0
    with open(path, 'rb') as f:
        for line in f:
            if lv in line and lvl_n is None:
                lvl_n = last_n
            m = rx.search(line)
            if not m:
                continue
            n = int(m.group(1)); dt = int(m.group(2)); last_n = n; total += 1
            if dt >= 100000:
                n100 += 1
                if dt < 230000:
                    n100_230 += 1
            if dt >= 2560000:
                big.append((n, dt))
            nmax = max(nmax, dt)
    print('%s frames=%d level_started_after_n=%s dt>=100ms=%d of_them_100..230ms=%d max_dt_us=%d dt>=2.56s=%s' % (
        path.split('/')[-1], total, lvl_n, n100, n100_230, nmax, big[:6]))
