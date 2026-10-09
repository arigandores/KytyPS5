# F31a: line kinds in a window of guest frames of a scene entry - frames (k-W, k] after 'Level has started: <scene>' where
# k = the frame count at hold time T (sum of dt_us).  Kinds: line text with digits and hex replaced, first 48 chars; header
# lines by the function name; parameter lines ('\t ...') by the parameter name.  usage:
#   python win31.py <log> <scene> <T_hold_s> <W_s> <out.txt>
import collections, re, sys
path, scene, T, W, out = sys.argv[1], sys.argv[2].encode(), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
HDR = re.compile(rb'^\[(\d+)\]\[[0-9:.]+\] (\S+)')
norm = lambda b: re.sub(rb'0x[0-9a-fA-F]+|[0-9]+', b'#', b)[:48]
c = collections.Counter()
inscene = False
t = 0.0
lines = 0
with open(path, 'rb') as f:
    for line in f:
        if not inscene:
            if b'Level has started: ' + scene in line:
                inscene = True
            continue
        m = FT.match(line)
        if m:
            t += int(m.group(2)) / 1e6
            if t > T:
                break
            continue
        if t < T - W or line.startswith(b'FrameTrace'):
            continue
        lines += 1
        h = HDR.match(line)
        if h:
            c[b'HDR ' + h.group(2)] += 1
        elif line.startswith(b'\t'):
            c[b'PAR ' + norm(line.strip().split(b'=')[0].split(b':')[0])] += 1
        else:
            c[norm(line.strip())] += 1
with open(out, 'w', encoding='utf-8') as o:
    o.write('%s window hold (%.1f, %.1f] s lines %d\n' % (path, T - W, T, lines))
    for k, v in c.most_common():
        o.write('%7d %s\n' % (v, k.decode('latin1')))
print(path, 'lines', lines, 'kinds', len(c))
