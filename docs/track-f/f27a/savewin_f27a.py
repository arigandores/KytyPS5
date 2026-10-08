"""F27a (HPP-690, track F): frames that overlap the write window of each driver pipeline cache save on the hold of a Day
and Night entry.  The window is [t - us, t], t = the time of the last timestamped log line before the "Vulkan pipeline
cache: saved ... (<us> us)" line (the line is printed when the write ends); a frame spans from the timestamp before the
previous FrameTrace line to the timestamp before its own FrameTrace line.  Timestamps are the "[tid][HH:MM:SS.fff]" heads
of the PRINT_NAME calls - their density bounds the precision (printed as the gap to the next/previous stamp).
Offline, read-only.  Usage: python savewin_f27a.py tag=log=stable ...  -> prints one row per save on the hold."""
import re
import sys

FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
TS = re.compile(rb'^\[\d+\]\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]')
SV = re.compile(rb'^Vulkan pipeline cache: saved (\d+) bytes .*\((\d+) us\)')


def scan(path):
    frames = []  # (n, dt_us, t_end)
    saves = []   # (line, bytes, us, t_end, last_n)
    last_ts = None
    last_n = None
    with open(path, 'rb') as f:
        for i, l in enumerate(f):
            m = TS.match(l)
            if m:
                h, mi, s, ms = (int(x) for x in m.groups())
                last_ts = h * 3600 + mi * 60 + s + ms / 1000
                continue
            m = FT.match(l)
            if m:
                last_n = int(m.group(1))
                frames.append((last_n, int(m.group(2)), last_ts))
                continue
            m = SV.match(l)
            if m and last_n is not None:
                saves.append((i + 1, int(m.group(1)), int(m.group(2)), last_ts, last_n))
    return frames, saves


def main():
    for arg in sys.argv[1:]:
        tag, path, stable = arg.split('=')
        stable = int(stable)
        frames, saves = scan(path)
        for line, nbytes, us, t_end, last_n in saves:
            if last_n < stable or t_end is None:
                continue
            w0 = t_end - us / 1e6
            over = []
            for k in range(1, len(frames)):
                a = frames[k - 1][2]
                b = frames[k][2]
                if a is None or b is None:
                    continue
                if b >= w0 and a <= t_end + 0.02:
                    over.append(frames[k])
            nxt = [fr for fr in frames if fr[0] > last_n]
            mx = max(over, key=lambda x: x[1]) if over else None
            print('%s save line %d bytes %d us %d interval_of_n %s window [%.3f, %.3f] frames %d..%d max %s ge100 %s' % (
                tag, line, nbytes, us, last_n + 1 if nxt else 'exit', w0, t_end,
                over[0][0] if over else -1, over[-1][0] if over else -1,
                (mx[0], mx[1]) if mx else None, [(x[0], x[1]) for x in over if x[1] >= 100000]))


if __name__ == '__main__':
    main()
