"""Read-only: load-phase (frames 150..400) counter sums per log, to look for what differs at level
load between runs that end OLD and runs that end NEW.

usage: python loadphase.py <label>=<log> ...
"""
import re
import sys

KV = re.compile(rb'(\w+)=(\d+)')
MAIN = ('draws', 'dt_us', 'faults', 'downloads')
DRAW = ('buf_new', 'img_new', 'img_free', 'img_up', 'img_up_kb', 'img_rec_put', 'img_rec_hit', 'img_imp', 'img_defer', 'img_defer_kb', 'img_pend')
LO, HI = 150, 400


def main():
    for arg in sys.argv[1:]:
        label, path = arg.split('=', 1)
        sums = {k: 0 for k in MAIN + DRAW}
        first_big = None
        peak = (0, 0)
        with open(path, 'rb') as f:
            for line in f:
                if line.startswith(b'FrameTrace: n='):
                    kv = dict(KV.findall(line))
                    n = int(kv[b'n'])
                    if LO <= n <= HI:
                        for k in MAIN:
                            sums[k] += int(kv.get(k.encode(), b'0'))
                        if first_big is None and int(kv.get(b'draws', b'0')) > 1000:
                            first_big = n
                    if n > HI:
                        break
                elif line.startswith(b'FrameTrace-draw:'):
                    kv = dict(KV.findall(line))
                    n = int(kv[b'n'])
                    if LO <= n <= HI:
                        for k in DRAW:
                            sums[k] += int(kv.get(k.encode(), b'0'))
                        if int(kv.get(b'buf_new', b'0')) > peak[1]:
                            peak = (n, int(kv[b'buf_new']))
        print('%-10s first>1000draws=%s buf_new_peak=%s ' % (label, first_big, peak) +
              ' '.join('%s=%d' % (k, v) for k, v in sums.items()))


if __name__ == '__main__':
    main()
