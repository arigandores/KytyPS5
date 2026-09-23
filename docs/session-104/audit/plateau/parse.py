"""Parse FrameTrace main/draw/submit lines of a log into a pickle (audit104/plateau)."""
import os, re, sys, pickle
RE = re.compile(rb'([A-Za-z_][A-Za-z_0-9\-]*)=(-?\d+)(?:/(\d+))?')
MAIN = ('dt_us', 'lat_us', 'cpu_gpu_us', 'cpu_main_us', 'cpu_present_us', 'cpu_proc_us', 'draws',
        'gpu_busy_us', 'semwait_us', 'semwaits', 'semwait_gpu_us', 'arm', 'blk', 'submits', 'submit_us',
        'wrm_stalls', 'downloads')
DRAW = ('spin_gpu_us', 'spin_us', 'rec_n', 'hostread_wait_us', 'acopy_wait_us', 'pb_wait_us')
OUT = 'C:/kyty/s104/audit104/plateau/cache'


def parse(path):
    os.makedirs(OUT, exist_ok=True)
    key = os.path.join(OUT, path.replace(':', '').replace('/', '_').replace('\\', '_') + '.pkl')
    if os.path.exists(key) and os.path.getmtime(key) > os.path.getmtime(path):
        return pickle.load(open(key, 'rb'))
    rows = {}
    order = []
    gate = []
    with open(path, 'rb') as f:
        for raw in f:
            if raw.startswith(b'GateArm:'):
                gate.append(raw[:300])
                continue
            if not raw.startswith(b'FrameTrace'):
                continue
            if raw.startswith(b'FrameTrace: '):
                t = {k.decode(): int(v) for k, v, _ in RE.findall(raw[12:])}
                if 'n' not in t:
                    continue
                r = rows.setdefault(t['n'], {'n': t['n']})
                for k in MAIN:
                    if k in t:
                        r[k] = t[k]
                order.append(t['n'])
            elif raw.startswith(b'FrameTrace-draw: '):
                t = {k.decode(): int(v) for k, v, _ in RE.findall(raw[17:])}
                if 'n' not in t:
                    continue
                r = rows.setdefault(t['n'], {'n': t['n']})
                for k in DRAW:
                    if k in t:
                        r[k] = t[k]
            elif raw.startswith(b'FrameTrace-submit: '):
                # no n= on this line: attach to last main row
                if order:
                    m = re.search(rb'wait-flip-done=(\d+)/(\d+)', raw)
                    if m:
                        r = rows[order[-1]]
                        r['wfd_us'] = int(m.group(1))
                        r['wfd_n'] = int(m.group(2))
            elif raw.startswith(b'FrameTrace-wait: '):
                if order:
                    tot = 0
                    for k, v, c in RE.findall(raw[17:]):
                        tot += int(v)
                    rows[order[-1]]['wait_line_us'] = tot
    res = {'rows': rows, 'order': order, 'gate': gate}
    pickle.dump(res, open(key, 'wb'))
    return res


if __name__ == '__main__':
    for p in sys.argv[1:]:
        r = parse(p)
        print(p, len(r['rows']), len(r['gate']))
