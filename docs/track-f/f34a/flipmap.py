"""F34a: map log events to guest flip count (number of 'flipPendingNum' lines so far) and InputScript presents.

usage: flipmap.py <log> [regex-of-events]
Prints: for each InputScript press/release and each event line (GuestOut Level/SubLevel/StartLevel/sequence words,
RenderDoc), the cumulative count of flipPendingNum lines (guest SubmitFlip blocks) and the line number.
Calibration: present (from InputScript) minus flip count at the same line -> offset; printed per InputScript line.
"""
import lzma, re, sys

f = sys.argv[1]
ev = re.compile(sys.argv[2].encode() if len(sys.argv) > 2 else
                rb'Level has started: \S|StartLevel|SubLevelLocator|Playing:|RenderDoc[^\r\n]*(captur|Captur)|'
                rb'LoadLevelResources|Sequence|sequence|Cutscene|cutscene|Event: quit')
rin = re.compile(rb'InputScript: (press|release) (\S+) at ([0-9.]+) s \(present (\d+)\)')
op = lzma.open if f.endswith('.xz') else open
flips = 0
last = None
with op(f, 'rb') as h:
    for i, l in enumerate(h):
        if b'flipPendingNum' in l:
            flips += 1
            continue
        m = rin.search(l)
        if m:
            p = int(m.group(4))
            print('IN  line=%d flips=%d present=%d off=%d %s %s t=%s' % (i + 1, flips, p, p - flips,
                  m.group(1).decode(), m.group(2).decode(), m.group(3).decode()))
            continue
        if ev.search(l):
            s = l[:200].decode('utf-8', 'replace').strip()
            k = re.sub(r'[0-9]+', '#', s)
            if k == last:
                continue
            last = k
            print('EV  line=%d flips=%d %s' % (i + 1, flips, s))
print('END flips=%d lines=%d' % (flips, i + 1))
