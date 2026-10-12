# F48b (HPP-831): hold frames >= 100 ms (rule list_hold of frames_f32d.py, re-typed: entry = level line, first scene frame =
# first FrameTrace with draws >= 100, window idx 1..599, hold idx >= 600, frames after 'Event: quit' dropped) on ALL unique logs
# of the F48a sweep (not only the course line), from the F48a segments; validation logs ([Vulkan][W] >= 100) skipped.
# Build column: 'Fork build' sha from the segment args/met if present, else from the log head.
import pickle, glob, hashlib, collections, sys, os, re
LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    sys.exit(3)
SEG = 'C:/kyty/f287/f48a/sw/seg'
paths = [l.split('\t')[0] for l in open('C:/kyty/f287/f48a/sw/loglist_f32a.tsv', encoding='utf-8') if l.strip()]
seen = set(); out = []
for p in paths:
    md = hashlib.md5(p.encode('utf-8')).hexdigest()
    fs = sorted(glob.glob(SEG + '/' + md + '_[0-9]*.pkl'), key=lambda f: int(f.rsplit('_', 1)[1][:-4]))
    ev = []; off = 0; vkw = 0; sha = None; s0 = len(fs)
    for f in fs:
        s = pickle.load(open(f, 'rb'))
        sha = sha or s.get('sha256')
        for x in s['events']:
            ev.append((x[0], x[1] + off) + tuple(x[2:]))
        vkw += sum((v[0] if isinstance(v, (list, tuple)) else v) for k, v in s['sigs'].items() if k.startswith(b'[Vulkan][W]'))
        off += s['lines']
    key = (sha, s0) if sha else p
    if key in seen:
        continue
    seen.add(key)
    if vkw >= 100:
        continue
    fork = '?'
    try:
        with open(p, 'rb') as fh:
            m = re.search(rb'Fork build \S+ ([0-9a-f]{7})', fh.read(1 << 16))
            fork = m.group(1).decode() if m else '-'
    except OSError:
        pass
    cur = None; quit_seen = False
    for e in ev:
        if e[0] == 'L' and e[2]:
            cur = {'level': e[2], 'first': None, 'idx': 0}
        elif e[0] == 'Q':
            quit_seen = True
        elif e[0] == 'F' and cur is not None:
            n, dt, draws = e[2], e[3], e[4]
            if cur['first'] is None:
                if draws >= 100:
                    cur['first'] = n
                continue
            if quit_seen:
                continue
            cur['idx'] += 1
            if cur['idx'] >= 600 and dt >= 100000:
                lv = cur['level'].decode() if isinstance(cur['level'], bytes) else cur['level']
                out.append((fork, lv, n, dt, cur['idx'], e[1], p))
print('unique logs', len(seen), 'hold frames >= 100 ms', len(out))
by = collections.Counter((o[0], o[6].replace('C:/kyty/f287/', '')[:40]) for o in out)
for k, v in sorted(by.items()):
    print(v, k)
with open(sys.argv[1], 'w', encoding='utf-8', newline='\n') as f:
    f.write('fork\tlevel\tn\tdt_us\tidx\tline\tpath\n')
    for o in out:
        f.write('\t'.join(str(x) for x in o) + '\n')
