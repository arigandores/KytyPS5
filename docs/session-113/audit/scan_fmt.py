import re, sys, statistics
path = sys.argv[1]; stable = int(sys.argv[2])
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
kinds = {}
pins = []
marks = []
scans = []
xrows = 0
first_x = first_d = first_m = None
main_ns = []
draw_ns = []
xfields = None
dup = None
with open(path, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace'):
            k = line.split(b':', 1)[0]
            kinds[k] = kinds.get(k, 0) + 1
        if b'GpuClockPin' in line:
            pins.append(line[:160])
        low = line.lower()
        if any(m in low for m in MARKERS):
            if len(marks) < 10: marks.append(line[:200])
        if line.startswith(b'FrameTrace-x: n='):
            xrows += 1
            if xfields is None:
                names = [k for k, v in FIELD.findall(line)]
                xfields = names
                seen = set(); d = [n for n in names if n in seen or seen.add(n)]
                dup = d
        elif line.startswith(b'FrameTrace-draw: n='):
            n = int(re.match(rb'FrameTrace-draw: n=(\d+)', line).group(1))
            if len(draw_ns) < 5: draw_ns.append(n)
            if n >= stable:
                d = dict(FIELD.findall(line[len(b'FrameTrace-draw: n=')+len(str(n)):]))
                if b'bda_scan' in d: scans.append(int(d[b'bda_scan']))
        elif line.startswith(b'FrameTrace: '):
            m = re.search(rb' n=(\d+)', line)
            if m and len(main_ns) < 5: main_ns.append((int(m.group(1)), line[:80]))
print('kinds', kinds)
print('pins', pins)
print('markers', len(marks), marks)
print('xrows', xrows, 'xfields', len(xfields or []), 'dups', dup)
print('draw_ns first', draw_ns, 'main first', main_ns)
print('scan rows', len(scans), 'median', statistics.median(scans) if scans else None)
