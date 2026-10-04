# F19a (HPP-543): the 'large_motor = ' lines (argument print of PadSetVibration, src/libs/controller.cpp:1119) of one log
# against the frame lines: total, per-frame rate, and the lines around the largest timestamp gap of the log.
# Usage: python vib_f19a.py <log> [<line_lo> <line_hi>]
import re, sys
path = sys.argv[1]
lo = int(sys.argv[2]) if len(sys.argv) > 2 else None
hi = int(sys.argv[3]) if len(sys.argv) > 3 else None
FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
vib = []          # (line, frames_before)
nz = 0
frames = 0
trig = 0
for i, l in enumerate(open(path, 'rb'), 1):
    if l.startswith(b'FrameTrace: n='):
        frames += 1
    elif b'large_motor = ' in l:
        vib.append((i, frames))
        if not l.rstrip().endswith(b'= 0'):
            nz += 1
    elif b'PadSetTriggerEffect' in l or b'trigger effect' in l.lower():
        trig += 1
print('log', path.replace('C:/kyty/', ''), 'frames', frames, 'large_motor lines', len(vib), 'non-zero large', nz, 'trigger lines', trig)
if vib:
    f0 = vib[0][1]
    per = {}
    for ln, fr in vib:
        per[fr] = per.get(fr, 0) + 1
    span = vib[-1][1] - f0 + 1
    print('first at line', vib[0][0], 'frame', f0, '; last at line', vib[-1][0], 'frame', vib[-1][1],
          '; frames in the span with >= 1 call: %d of %d' % (len(per), span))
    gaps = sorted(((vib[k + 1][1] - vib[k][1], vib[k][0], vib[k + 1][0], vib[k][1], vib[k + 1][1]) for k in range(len(vib) - 1)), reverse=True)[:5]
    print('largest gaps between consecutive calls, in frames: (frames, line_from, line_to, frame_from, frame_to)')
    for g in gaps:
        print('  ', g)
    if lo is not None:
        print('calls with line in [%d, %d]:' % (lo, hi), [v for v in vib if lo <= v[0] <= hi])
