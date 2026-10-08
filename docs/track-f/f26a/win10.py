import sys, subprocess, re, collections
# usage: win10.py <xz> <out prefix> <assert line> <assert time HH:MM:SS.fff> [window s]
path, outp, aline, atime = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
win = float(sys.argv[5]) if len(sys.argv) > 5 else 10.0
def tsec(s):
    h, m, r = s.split(':')
    return int(h) * 3600 + int(m) * 60 + float(r)
T = tsec(atime)
hdr = re.compile(rb'^\[(\d+)\]\[(\d\d:\d\d:\d\d\.\d\d\d)\] (\S+)')
kw = re.compile(rb'(?i)stub|unresolved|error|fail|assert|not implemented|warning|warn|denied|exception|timeout|lost|abort|EIO|ENOMEM|out of|too many|overflow|Level has started|Level|retry|GamePatch|PriorityStall|MainTaskLate')
p = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE, bufsize=1 << 20)
n = 0
cur = 0.0
inwin = False
funcs = collections.Counter()
functh = collections.Counter()
kwl = []
levels = []
frames = []
others = collections.Counter()
for line in p.stdout:
    n += 1
    m = hdr.match(line)
    if m:
        cur = tsec(m.group(2).decode())
        if not inwin and cur >= T - win:
            inwin = True
            first = n
    if b'Level has started' in line or b'LevelContextFiber' in line:
        levels.append((n, cur, line.rstrip()[:200]))
    if inwin and n <= aline + 10:
        if m:
            funcs[m.group(3)] += 1
            functh[(m.group(1), m.group(3))] += 1
        elif line.startswith(b'FrameTrace: n='):
            frames.append(line.rstrip()[:400])
        elif not line.startswith(b'\t') and not line.startswith(b'FrameTrace') and not line.startswith(b'AvTrace'):
            key = re.sub(rb'0x[0-9a-fA-F]+|\d+', b'#', line.strip())[:120]
            others[key] += 1
        if kw.search(line) and not line.startswith(b'FrameTrace'):
            kwl.append((n, cur, line.rstrip()[:300]))
    if n > aline + 10:
        break
p.kill()
with open(outp + '_win.txt', 'wb') as f:
    f.write(b'window %.1fs before %s, first line %d, assert line %d\n' % (win, atime.encode(), first, aline))
    f.write(b'== levels (whole log up to assert)\n')
    for k, t, l in levels:
        f.write(b'%d %.3f %s\n' % (k, t, l))
    f.write(b'== HLE calls by name in window\n')
    for k, v in funcs.most_common():
        f.write(b'%7d %s\n' % (v, k))
    f.write(b'== HLE calls by thread,name\n')
    for (th, k), v in sorted(functh.items(), key=lambda x: (int(x[0][0]), -x[1])):
        f.write(b'%4s %7d %s\n' % (th, v, k))
    f.write(b'== other non-tab lines (normalized)\n')
    for k, v in others.most_common(80):
        f.write(b'%7d %s\n' % (v, k))
    f.write(b'== keyword lines\n')
    for k, t, l in kwl[-300:]:
        f.write(b'%d %.3f %s\n' % (k, t, l))
    f.write(b'== FrameTrace in window (%d)\n' % len(frames))
    for l in frames:
        f.write(l + b'\n')
print('done', n)
