# Red Team s145 step 1: where in the hold the F6 lines of the s144 W stand (the only in-hold sign of the validation layer
# reporting).  Per W log: presented time (sum dt_us of FrameTrace rows) after the entry line at the first F6 line, the last F6
# line, the limit line and the last row; the longest stretch of presented time after the entry line without an F6 line.
import re, sys, os, glob, hashlib
LOCK = 'C:/kyty/SEALED_RUN.lock'
RX = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)|(and this write is unused\.)|(this will be the last time reporting it)|(GuestOut: Level has started: )')
for p in sorted(glob.glob('C:/kyty/s144/log_w144_*.txt')):
    if p.endswith('_a1.txt'):
        continue
    if os.path.exists(LOCK):
        print('LOCK appeared - abort'); sys.exit(3)
    t = 0; entered = False; first = last = lim = None; lastf = 0.0; gap = (0.0, 0.0, 0.0); rows = 0; h = hashlib.sha256(); tail = b''
    with open(p, 'rb') as f:
        while True:
            b = f.read(1 << 26)
            h.update(b)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            for m in RX.finditer(whole):
                if m.group(1):
                    if entered:
                        t += int(m.group(2)); rows += 1
                elif m.group(3):
                    if entered:
                        s = t / 1e6
                        if first is None: first = s
                        if s - lastf > gap[0]: gap = (s - lastf, lastf, s)
                        last = s; lastf = s
                elif m.group(4):
                    lim = t / 1e6 if entered else -1
                elif m.group(5):
                    if not entered:
                        entered = True; t = 0
            if not b:
                break
    end = t / 1e6
    if entered and end - lastf > gap[0] and lim is None:
        gap = (end - lastf, lastf, end)
    print('%s sha %s: presented after entry %.1f s (%d rows); F6 first %s last %s; limit line at %s; longest stretch without F6 %.1f s (%.1f..%.1f)' % (
        os.path.basename(p), h.hexdigest()[:16], end, rows, None if first is None else '%.1f' % first,
        None if last is None else '%.1f' % last, None if lim is None else '%.1f' % lim, gap[0], gap[1], gap[2]))
    sys.stdout.flush()
