# F0 (HPP-289): aggregate the sweep segments -> per-log records (agg_f0.json) and the signature table (sig_f0.tsv).
import os, re, sys, json, pickle, hashlib, collections

OUT = 'C:/kyty/f287/f0'
SEG = OUT + '/seg'
FIX = re.compile(r'/(fx_|work_|mut|test_|fixt)')
SEG_BYTES = 256 << 20
TAB = chr(9)


def session_of(p):
    m = re.match(r'C:/kyty/s(\d+)([^/]*)/(.*)$', p)
    if m:
        s = int(m.group(1))
        if m.group(2) == '_stage':
            d = re.findall(r'(1[01]\d)(?!\d)', m.group(3))
            return int(d[-1]) if d else 106
        return s
    if p.startswith('C:/kyty/KytyPS5/ps5 em/'):
        return 143  # current emulator folder log (after s142 runs / track P, F)
    b = os.path.basename(p)
    d = re.findall(r'_s(\d+)(?=[_.a-z])', b)
    if d:
        return int(d[-1])
    return None


def frames(events, validation):
    # p.218(g) / p.221(v): first scene frame = first FrameTrace with draws >= 100 after a non-empty level start;
    # its dt is outside the entry window; window = 599 following frames; then hold. Validation logs: dt rule not applied.
    res = []
    cur = None
    quit_seen = False
    lastF_dt = {}
    for e in events:
        if e[0] == 'L':
            if e[2]:
                cur = {'level': e[2], 'line': e[1], 'first_n': None, 'idx': 0, 'k2': [], 'k3w': 0, 'k3h': 0, 'k3h_ex': [],
                       'max_w': 0, 'max_h': 0, 'frames': 0, 'sum_us': 0, 'after_quit': 0, 'k3w_ex': [], 'p_w': 0, 'p_h': 0, 'pf_w': 0, 'pf_h': 0, 'pend': 0}
                res.append(cur)
        elif e[0] == 'Q':
            quit_seen = True
        elif e[0] == 'P':
            if cur is not None and cur['first_n'] is not None and e[2] > 50000:
                cur['pend'] += 1
        elif e[0] == 'F':
            if cur is None:
                continue
            n, dt, draws = e[2], e[3], e[4]
            if cur['first_n'] is None:
                if draws >= 100:
                    cur['first_n'] = n
                continue
            if quit_seen:
                cur['after_quit'] += 1
                continue
            cur['idx'] += 1
            cur['frames'] += 1
            cur['sum_us'] += dt
            w = cur['idx'] <= 599
            if w:
                cur['max_w'] = max(cur['max_w'], dt)
            else:
                cur['max_h'] = max(cur['max_h'], dt)
            if cur['pend']:
                cur['p_w' if w else 'p_h'] += cur['pend']
                if dt >= 100000:
                    cur['pf_w' if w else 'pf_h'] += cur['pend']
                cur['pend'] = 0
            if dt >= 1000000:
                if len(cur['k2']) < 20:
                    cur['k2'].append((n, dt, 'w' if w else 'h', e[1]))
            elif dt >= 100000:
                if w:
                    cur['k3w'] += 1
                    if len(cur['k3w_ex']) < 10:
                        cur['k3w_ex'].append((n, dt, e[1]))
                else:
                    cur['k3h'] += 1
                    if len(cur['k3h_ex']) < 10:
                        cur['k3h_ex'].append((n, dt, e[1]))
    return res


def prio_vs_frames(events):
    # for every PriorityStall > 50 ms: dt of the next FrameTrace line after it (the frame that contains the wait)
    out = [0, 0, 0]  # stalls >50ms, of them next frame dt>=100ms, of them next frame dt>=1s
    pend = 0
    for e in events:
        if e[0] == 'P':
            if e[2] > 50000:
                pend += 1
        elif e[0] == 'F' and pend:
            out[0] += pend
            if e[3] >= 100000:
                out[1] += pend
            if e[3] >= 1000000:
                out[2] += pend
            pend = 0
    out[0] += pend
    return out


def main():
    files = []
    for l in open(OUT + '/loglist_f0.tsv', encoding='utf-8'):
        p, s, m = l.rstrip().split(TAB)
        s = int(s)
        if FIX.search(p) or s == 0:
            continue
        files.append((p, s, int(m)))
    # the emulator folder keeps the last two runs (_kyty.txt, _kyty.prev.txt): put them last so that a copy in s*/ is the canonical one
    files.sort(key=lambda x: (x[0].startswith('C:/kyty/KytyPS5/'), x[0]))
    recs = []
    sigtab = {}
    seen_sha = {}
    missing = 0
    for p, s, mt in files:
        md = hashlib.md5(p.encode('utf-8')).hexdigest()
        nseg = 1 if s <= SEG_BYTES else (s + SEG_BYTES - 1) // SEG_BYTES
        sigs = {}
        events = []
        args = []
        met = collections.Counter()
        sites = collections.Counter()
        off = 0
        sha = None
        ok = True
        for i in range(nseg):
            fn = '%s/%s_%d.pkl' % (SEG, md, i)
            if not os.path.exists(fn):
                ok = False
                break
            r = pickle.load(open(fn, 'rb'))
            for k, v in r['sigs'].items():
                e = sigs.get(k)
                if e is None:
                    sigs[k] = [v[0], v[1] + off, v[2]]
                else:
                    e[0] += v[0]
            for x in r['events']:
                events.append((x[0], x[1] + off) + tuple(x[2:]))
            args += r['args']
            for k, v in r['met'].items():
                if k == 'prio_sites':
                    sites.update(v)
                elif k in ('prio_max', 'late_max', 'trip_max'):
                    met[k] = max(met[k], v)
                else:
                    met[k] += v
            off += r['lines']
            if r['sha256']:
                sha = r['sha256']
        if ok and nseg > 1:
            fn = '%s/%s_sha.pkl' % (SEG, md)
            if os.path.exists(fn):
                sha = pickle.load(open(fn, 'rb'))['sha256']
            else:
                ok = False
        if not ok:
            missing += 1
            continue
        dup = sha in seen_sha
        if not dup:
            seen_sha[sha] = p
        vkw = sum(v[0] for k, v in sigs.items() if k.startswith(b'[Vulkan][W]'))
        vke = sum(v[0] for k, v in sigs.items() if k.startswith(b'[Vulkan][E]'))
        validation = vkw >= 100
        lv = frames(events, validation)
        lvl_arg = None
        for i, a in enumerate(args):
            if a.strip().endswith('= -lvl') and i + 1 < len(args):
                lvl_arg = args[i + 1].split('= ', 1)[-1].strip()
        levels = []
        for x in lv:
            if x['level'] not in levels:
                levels.append(x['level'])
        rec = {'path': p, 'size': s, 'mtime': mt, 'sha256': sha, 'dup_of': seen_sha[sha] if dup else None, 'lines': off,
               'session': session_of(p), 'levels': levels, 'lvl_arg': lvl_arg, 'validation': validation, 'vk_w': vkw, 'vk_e': vke,
               'met': dict(met), 'prio_sites': dict(sites), 'scenes': lv, 'prio_frames': prio_vs_frames(events),
               'ft': sum(1 for e in events if e[0] == 'F'), 'quit': any(e[0] == 'Q' for e in events), 'nsig': len(sigs)}
        recs.append(rec)
        if dup:
            continue
        for k, v in sigs.items():
            t = sigtab.get(k)
            if t is None:
                t = sigtab[k] = {'logs': 0, 'lines': 0, 'sess': [], 'ex': None, 'levels': collections.Counter(), 'none': 0}
            t['logs'] += 1
            t['lines'] += v[0]
            if rec['session'] is None:
                t['none'] += 1
            else:
                t['sess'].append(rec['session'])
            for L in (levels or ['(no level start)']):
                t['levels'][L] += 1
            # example: prefer the latest session
            sx = rec['session'] if rec['session'] is not None else -1
            if t['ex'] is None or sx >= t['ex'][0]:
                t['ex'] = (sx, p, v[1], sha, v[2].decode('latin1'))
    json.dump(recs, open(OUT + '/agg_f0.json', 'w', encoding='utf-8'), ensure_ascii=False)
    uniq = [r for r in recs if not r['dup_of']]
    print('logs in scope', len(files), 'aggregated', len(recs), 'missing', missing, 'unique sha', len(uniq), 'dups', len(recs) - len(uniq))
    print('bytes', sum(r['size'] for r in recs), 'lines', sum(r['lines'] for r in recs))
    c = collections.Counter(('none' if r['session'] is None else ('<50' if r['session'] < 50 else '50-112' if r['session'] < 113 else '113-127' if r['session'] < 128 else '128-141' if r['session'] < 142 else '142+')) for r in uniq)
    print('unique logs by session band', dict(c))
    print('distinct signatures', len(sigtab))
    with open(OUT + '/sig_f0.tsv', 'w', encoding='utf-8', newline=chr(10)) as o:
        o.write(TAB.join(['logs', 'lines', 'first_s', 'last_s', 'logs_s128plus', 'logs_s142plus', 'logs_no_session', 'levels', 'example_path:line', 'sha256', 'signature', 'example_text']) + chr(10))
        for k, t in sorted(sigtab.items(), key=lambda kv: (-kv[1]['logs'], kv[0])):
            ss = t['sess']
            lv = ','.join('%s:%d' % (a, b) for a, b in t['levels'].most_common(30))
            o.write(TAB.join([str(t['logs']), str(t['lines']), str(min(ss)) if ss else '-', str(max(ss)) if ss else '-',
                              str(sum(1 for x in ss if x >= 128)), str(sum(1 for x in ss if x >= 142)), str(t['none']), lv,
                              '%s:%d' % (t['ex'][1], t['ex'][2]), t['ex'][3], k.decode('latin1').replace(TAB, ' '),
                              t['ex'][4].replace(TAB, ' ').replace(chr(13), '')[:300]]) + chr(10))


main()
