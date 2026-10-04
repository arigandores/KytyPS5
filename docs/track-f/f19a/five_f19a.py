# F19a (HPP-543, ROADMAP s122 item 441(z)(2)): the five logs with 'MainTaskLate: us=' >= 1 s on s. 113+
# (ctl114a, ctl114b, boot115a, boot115c, edes122).  Stream read ('.xz' through 'xz -dc'), binary, whole lines.
# Per log it prints:
#   sha256 of the stored file, lines, first/last timestamp
#   every 'MainTaskLate:' line: line number, last timestamp at or before it (ms), frames seen, us
#   every 'FrameTrace: n=' line with dt_us >= 1 000 000: line number, ts, n, dt_us
#   the largest gaps between consecutive log timestamps (top 3), with the line numbers on both sides
#   every line with one of the EV literals (controller / window / haptics / stall-tool lines), capped
#   CTX lines of context before and after each MainTaskLate line with us >= 1 000 000
# Usage: python five_f19a.py <out.txt> <tag>=<path> ...
import collections, hashlib, re, subprocess, sys

out = open(sys.argv[1], 'w', encoding='utf-8', newline='\n')
TS = re.compile(rb'\[\d+\]\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]')
FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
MTL = re.compile(rb'MainTaskLate: us=(\d+)')
EV = (b'Controller', b'Haptics:', b'Window ', b'Event: ', b'PrepareHold', b'PrepareMainPresent', b'ShaderPreparation: startup wait',
      b'MainStall', b'MainThreadWait', b'FlipHold', b'Level has started: ', b'Recovering Vulkan swapchain', b'titleasync',
      b'TitleAsync', b'GpuHangAbort', b'device lost', b'HostInput', b'Joystick', b'Gamepad', b'pad ')
EV_CAP = 120
CTX = 8


def p(*a):
    out.write(' '.join(str(x) for x in a) + '\n')


def stream(path):
    if path.endswith('.xz'):
        pr = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE)
        return pr, pr.stdout
    return None, open(path, 'rb')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


for arg in sys.argv[2:]:
    tag, path = arg.split('=', 1)
    p('=' * 20, tag, path)
    p('sha256', sha(path))
    pr, f = stream(path)
    ln = 0
    ts = None
    ts_first = None
    ts_line = 0
    frames = 0
    ft_sum = 0
    gaps = []
    late = []
    slow = []
    ev = []
    ev_over = 0
    evn = collections.Counter()
    ring = collections.deque(maxlen=CTX)
    after = []          # [remaining, list]
    ctxs = []
    for raw in f:
        ln += 1
        line = raw.rstrip(b'\r\n')
        m = TS.search(line[:40])
        if m:
            t = ((int(m.group(1)) * 60 + int(m.group(2))) * 60 + int(m.group(3))) * 1000 + int(m.group(4))
            if ts is not None and t - ts >= 500:
                gaps.append((t - ts, ts_line, ts, ln, t))
            if ts_first is None:
                ts_first = t
            ts, ts_line = t, ln
        for a in after:
            if a[0] > 0:
                a[1].append((ln, line[:200]))
                a[0] -= 1
        if b'FrameTrace: n=' in line:
            m = FT.search(line)
            if m:
                frames += 1
                d = int(m.group(2))
                ft_sum += d
                if d >= 1000000:
                    slow.append((ln, ts, int(m.group(1)), d, ft_sum - d))
        if b'MainTaskLate: us=' in line:
            m = MTL.search(line)
            us = int(m.group(1))
            late.append((ln, ts, frames, us))
            if us >= 1000000:
                a = [CTX, []]
                after.append(a)
                ctxs.append((ln, us, list(ring), a[1]))
        for lit in EV:
            if lit in line and b'FrameTrace' not in line:
                evn[lit.decode()] += 1
                if len(ev) < EV_CAP:
                    ev.append((ln, ts, frames, line[:220]))
                else:
                    ev_over += 1
                break
        ring.append((ln, line[:200]))
    if pr:
        pr.wait()
    p('lines', ln, 'ts_first_ms', ts_first, 'ts_last_ms', ts, 'frames', frames, 'ft_sum_us', ft_sum)
    p('-- MainTaskLate lines:', len(late), '(>= 1 s:', sum(1 for x in late if x[3] >= 1000000), ')')
    for x in late:
        p('   line %d ts_ms %s frames %d us %d' % x)
    p('-- FrameTrace dt_us >= 1 s:', len(slow))
    for x in slow:
        p('   line %d ts_ms %s n %d dt_us %d ft_us_before %d' % x)
    gaps.sort(reverse=True)
    p('-- timestamp gaps >= 500 ms:', len(gaps), 'top 5:')
    for g in gaps[:5]:
        p('   gap_ms %d from line %d ts %d to line %d ts %d' % g)
    p('-- EV lines by literal:', dict(evn), 'over cap', ev_over)
    for x in ev:
        p('   line %d ts_ms %s frames %d | %s' % (x[0], x[1], x[2], x[3].decode('utf-8', 'replace')))
    for c in ctxs:
        p('-- context of MainTaskLate line %d us %d' % (c[0], c[1]))
        for l, s in c[2]:
            p('   - %d | %s' % (l, s.decode('utf-8', 'replace')))
        for l, s in c[3]:
            p('   + %d | %s' % (l, s.decode('utf-8', 'replace')))
    out.flush()
out.close()
print('done')
