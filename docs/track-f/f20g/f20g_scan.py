import sys, os, re, json, time
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
FT = re.compile(rb'FrameTrace: n=(\d+) ')
KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(\d+)')
KV2 = re.compile(rb'([A-Za-z0-9_+.-]+)=(\d+)/(\d+)')
TH = re.compile(rb'\[(\d+)\]\[(\d+):(\d+):(\d+)\.(\d+)\] (\S+)')
LVL = b'Level has started: underwater_aerial_garden'
CORE = ('dt_us', 'lat_us', 'cpu_main_us', 'cpu_gpu_us', 'cpu_present_us', 'cpu_proc_us', 'gpu_busy_us', 'semwait_us', 'prio_us', 'draws', 'submits')
def ms(m):
    return ((int(m.group(2)) * 60 + int(m.group(3))) * 60 + int(m.group(4))) * 1000 + int(m.group(5))
def scan(path, targets, W=14):
    want = set()
    for t in targets:
        want.update(range(t - W, t + W + 1))
    last = max(targets) + W
    frames = {}
    allft = []
    calls = {}
    tidfunc = {}
    kinds, th, raw, nl = {}, [], [], 0
    lastcall, prevstart = {}, {}
    rec = None
    ln = 0
    scene_ln = None
    with open(path, 'rb') as f:
        for line in f:
            ln += 1
            if (ln & 0x3ffff) == 0 and (os.path.exists(LOCK) or os.path.exists(STOP)):
                print('ABORT lock/stop at line', ln)
                sys.exit(3)
            if line.startswith(b'FrameTrace'):
                if line.startswith(b'FrameTrace: n='):
                    n = int(FT.match(line).group(1))
                    if scene_ln is not None:
                        d0 = dict((k.decode(), int(v)) for k, v in KV.findall(line))
                        allft.append([d0.get(k, -1) for k in ('n',) + CORE])
                        if n in want:
                            rec = dict(n=n, ln=ln, ft=d0, iv_lines=nl, kinds=kinds, th=th, prev=dict(prevstart), raw=raw)
                            frames[n] = rec
                        else:
                            rec = None
                    kinds, th, raw, nl = {}, [], [], 0
                    prevstart = dict(lastcall)
                    if n > last and scene_ln is not None:
                        break
                    continue
                if rec is not None:
                    c = line.find(b':')
                    tp = line[11:c].decode('ascii', 'replace')
                    if b' n=' in line[:24]:
                        for k, v in KV.findall(line):
                            rec['ft'][tp + '.' + k.decode()] = int(v)
                    elif tp in ('wait', 'submit', 'pm4'):
                        for k, a, b in KV2.findall(line):
                            rec['ft'][tp + '.' + k.decode() + '_us'] = int(a)
                            rec['ft'][tp + '.' + k.decode() + '_n'] = int(b)
                continue
            if scene_ln is None and LVL in line:
                scene_ln = ln
            nl += 1
            if line[:1] == b'[':
                m = TH.match(line)
                if m:
                    tid = int(m.group(1)); t = ms(m); fn = m.group(6).decode('ascii', 'replace')
                    lastcall[tid] = t
                    key = '%d %s' % (tid, fn)
                    tidfunc[key] = tidfunc.get(key, 0) + 1
                    if scene_ln is not None:
                        calls.setdefault(tid, []).append(t)
                    th.append([tid, t, fn])
                    k = 'T:' + fn
                    kinds[k] = kinds.get(k, 0) + 1
                    continue
            s = line.strip()
            if line[:1] in (bytes([9]), b' '):
                i = s.find(b'=')
                k = 'a:' + (s[:i].strip().decode('ascii', 'replace') if i > 0 else s[:16].decode('ascii', 'replace'))
            else:
                j = len(s)
                for ch in (b':', b' ', b'('):
                    x = s.find(ch)
                    if 0 < x < j:
                        j = x
                k = 'L:' + s[:j][:40].decode('ascii', 'replace')
                if len(raw) < 60:
                    raw.append(s[:240].decode('ascii', 'replace'))
            kinds[k] = kinds.get(k, 0) + 1
    return dict(path=path, targets=targets, lines_read=ln, scene_ln=scene_ln, frames=frames, allft_cols=('n',) + CORE, allft=allft,
                calls=dict((str(k), v) for k, v in calls.items()), tidfunc=tidfunc)
if __name__ == '__main__':
    tag, path = sys.argv[1], sys.argv[2]
    targets = [int(x) for x in sys.argv[3].split(',')]
    t0 = time.time()
    r = scan(path, targets)
    out = 'C:/kyty/f287/f20g/scan_%s.json' % tag
    json.dump(r, open(out, 'w'))
    print(tag, 'lines', r['lines_read'], 'frames', len(r['frames']), 'allft', len(r['allft']), 'sec %.1f' % (time.time() - t0))
