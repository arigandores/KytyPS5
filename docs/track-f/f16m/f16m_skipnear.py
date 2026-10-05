"""Track F link F16m (HPP-585; ROADMAP s122 item 502 (v)): a REFERENCE for F16n, outside the seal (the reader and the pair are not changed):
for every DiagF5Ev line of the pair arms, the lines 'AsyncPipelines: skipped draw ... frame=<f>' and 'BindFloor: skipped draw ... frame=<f>'
of both arm logs (a) with f in [gpu - 1, gpu + 3] of the event (item 502 (v), same numbering of frame and gpu - [I] of the lead, F16n checks
by code), and (b) on the log stretch between the DiagF5 frame lines around the event line (the fallback of item 502 (v)).  No verdict.
usage: python f16m_skipnear.py [--log0 <a> --log1 <b>]     ASCII only."""
import re, sys

G = 'C:/kyty/f287/f16m'
RX_SKIP = re.compile(rb'(AsyncPipelines|BindFloor): skipped draw \S* ?frame=(\d+)')
RX_EV = re.compile(rb'DiagF5Ev: (cmask_fce(?:_nohit)?) n=(\d+)(?: b42=\w+)? present=(\d+) gpu=(\d+)')


def scan(path):
    ev, skips, f5 = [], [], []
    with open(path, 'rb') as f:
        for ln, raw in enumerate(f, 1):
            if b'skipped draw' in raw:
                m = RX_SKIP.search(raw)
                if m:
                    skips.append((ln, m.group(1).decode(), int(m.group(2))))
            elif b'DiagF5Ev: ' in raw:
                m = RX_EV.search(raw)
                if m:
                    ev.append((ln, m.group(1).decode(), int(m.group(2)), int(m.group(3)), int(m.group(4))))
            elif b'DiagF5: frame=' in raw:
                f5.append(ln)
    return ev, skips, f5


def around(f5, ln):
    lo = max([x for x in f5 if x < ln] + [0])
    hi = min([x for x in f5 if x > ln] + [10 ** 12])
    return lo, hi


def main(argv):
    logs = [argv[argv.index('--log0') + 1] if '--log0' in argv else G + '/log_f5cmu_0.txt',
            argv[argv.index('--log1') + 1] if '--log1' in argv else G + '/log_f5cmu_1.txt']
    data = [scan(p) for p in logs]
    for a, (ev, skips, f5) in enumerate(data):
        print('ARM %d log %s: events %d, skipped draw lines %d (AsyncPipelines %d, BindFloor %d), DiagF5 frame lines %d' % (
            a, logs[a], len(ev), len(skips), len([s for s in skips if s[1] == 'AsyncPipelines']),
            len([s for s in skips if s[1] == 'BindFloor']), len(f5)))
        for ln, kind, n, present, gpu in ev:
            near = [[s for s in data[b][1] if gpu - 1 <= s[2] <= gpu + 3] for b in (0, 1)]
            lo, hi = around(f5, ln)
            stretch = [s for s in skips if lo < s[0] < hi]
            print('  EVENT arm%d %s n=%d present=%d gpu=%d line=%d: skips with frame in [gpu-1, gpu+3]: arm0 %d %s arm1 %d %s; '
                  'skips of this arm between DiagF5 lines %d..%d: %d' % (
                      a, kind, n, present, gpu, ln, len(near[0]), [s[2] for s in near[0]][:6], len(near[1]),
                      [s[2] for s in near[1]][:6], lo, hi if hi < 10 ** 12 else -1, len(stretch)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
