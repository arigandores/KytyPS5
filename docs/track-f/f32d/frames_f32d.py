# F32d (HPP-742, ROADMAP p.673(z)(3)(2)): every frame >= 100 ms on the hold of a course-line log (binaries from FS2 on,
# docs/track-f/f32a/binmap.tsv) without validation - the population of rep_f32a.py (3) on the merged input (F32a delta + the
# 36 out-of-mask logs) - with the marks of its interval, for the attribution in classify_f32d.py.
# Frame rule = docs/track-f/f0/agg_f0.py frames() (loaded unchanged, text before 'def main'); its k3h_ex / k2 lists are capped,
# so the frames are listed again here by the same rule and the per-entry counts are checked against frames() (identity I1:
# listed K3 hold = frames()['k3h'], listed K2 hold = len of frames()['k2'] with 'h'; a mismatch is FAILED).
# Interval of frame n = the lines after the previous main 'FrameTrace: n=' line up to its own line (the F20a interval).
# Marks (the F20a sweep_f20a.py interval() set plus the save, pause and DiagB32 lines): ir ('%' lines - SPIR-V dump of a new
# translation), gcn (GCN disassembly lines), skip ('AsyncPipelines: skipped draw'), held ('AsyncPipelines: flip <n> held
# (incomplete frame)', videoOut.cpp), skipceil ('SkipCeil: flip <n> held'), cs_miss ('CsPretranslate: miss'),
# pcs ('Vulkan pipeline cache: saved ... (<us> us)'), prio ('PriorityStall:' us=), mtl ('MainTaskLate:' us=), win
# ('Window '/'Event: '/'Pause'/'Mouse ' lines), pause_on ('Pause: true'), logasync ('LogAsync: stall'), diagb32
# ('DiagB32:' lines, raw, <= 3), top normalized lines.  Per entry: translation lines (ir + gcn + skip) in the entry window
# (level start .. idx 599) and in the hold before the frame.  Per log: head lines (RenderDoc, Diag*, Test*, GamePatch,
# ShaderReplay, LogAsync, Knob/Gate, FrameTrace mode) of the first 8 MiB.
# Usage: python frames_f32d.py <merged_out> <binmap.tsv> <out.json>       (exit 3 lock, 4 STOP; read-only on logs)
import os, re, sys, json, lzma, pickle, hashlib, collections, multiprocessing

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
AGG_F0 = os.environ.get('F32A_AGG_F0_PY', 'C:/kyty/KytyPS5/docs/track-f/f0/agg_f0.py')
SEG_BYTES = 256 << 20
NL = b'\n'
FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
GCN = re.compile(rb'[0-9a-fA-F]+: [A-Z]_')
NUM = re.compile(rb'0x[0-9a-fA-F]+|\b[0-9a-f]{16}\b|\d+')
US_PAR = re.compile(rb'\((\d+) us')
US_EQ = re.compile(rb' us=(\d+)')
TS = re.compile(rb'^\[\d+\]\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]')
WINP = (b'Window ', b'Event: ', b'Pause', b'Mouse ', b'Recovering Vulkan swapchain')
HEADRE = re.compile(rb'^(?:RenderDoc|Diag[A-Za-z0-9]+:|Test[A-Za-z0-9]+:|GamePatch|ShaderReplay|LogAsync|Knob|Gate|FrameTrace: mode|'
                    rb'PrepareHold|MainStallTest|S-pcw|Poke|PVar|Pvar|AudioSync)[^\n]*', re.M)


def gate():
    if os.path.exists(STOP):
        os._exit(4)
    if os.path.exists(LOCK):
        os._exit(3)


def load_frames():
    src = open(AGG_F0, encoding='utf-8').read().split(chr(10) + 'def main')[0]
    ns = {}
    exec(compile(src, AGG_F0, 'exec'), ns)
    return ns['frames']


def events_of(seg, r):
    md = hashlib.md5(r['path'].encode('utf-8')).hexdigest()
    whole = r['kind'] == 'xz' or r['size'] <= SEG_BYTES
    nseg = 1 if whole else (r['size'] + SEG_BYTES - 1) // SEG_BYTES
    ev, off, vkw = [], 0, 0
    for i in range(nseg):
        s = pickle.load(open('%s/%s_%d.pkl' % (seg, md, i), 'rb'))
        for x in s['events']:
            ev.append((x[0], x[1] + off) + tuple(x[2:]))
        vkw += sum(v[0] for k, v in s['sigs'].items() if k.startswith(b'[Vulkan][W]'))
        off += s['lines']
    return ev, vkw >= 100


def list_hold(events):
    # the agg_f0 frames() rule, every hold frame >= 100 ms listed (no cap); also the previous main FrameTrace line and the
    # line of window end (idx 599) per entry
    res = []
    cur = None
    quit_seen = False
    prev_ft = None
    for e in events:
        if e[0] == 'L':
            if e[2]:
                cur = {'level': e[2], 'line': e[1], 'first_n': None, 'first_line': None, 'idx': 0, 'k3h': [], 'k2h': [],
                       'win_end_line': None, 'frames': 0}
                res.append(cur)
        elif e[0] == 'Q':
            quit_seen = True
        elif e[0] == 'F':
            pl = prev_ft
            prev_ft = e[1]
            if cur is None:
                continue
            n, dt, draws = e[2], e[3], e[4]
            if cur['first_n'] is None:
                if draws >= 100:
                    cur['first_n'] = n
                    cur['first_line'] = e[1]
                continue
            if quit_seen:
                continue
            cur['idx'] += 1
            cur['frames'] += 1
            if cur['idx'] == 599:
                cur['win_end_line'] = e[1]
            if cur['idx'] <= 599:
                continue
            if dt >= 1000000:
                cur['k2h'].append((n, dt, e[1], pl, cur['idx']))
            elif dt >= 100000:
                cur['k3h'].append((n, dt, e[1], pl, cur['idx']))
    return res


def scan_log(job):
    # job: (path, [(start_line_excl, end_line_incl, key)], [(entry_key, level_line, win_end_line)])
    gate()
    path, ivs, ents = job
    want = {}
    for a, b, k in ivs:
        want[k] = {'a': a, 'b': b, 'il': 0, 'ir': 0, 'gcn': 0, 'skip': 0, 'held': 0, 'skipceil': 0, 'cs_miss': 0, 'pcs': [], 'prio_n': 0, 'prio_max': 0,
                   'mtl_n': 0, 'mtl_max': 0, 'win': 0, 'win_ex': [], 'pause_on': 0, 'pause_off': 0, 'logasync': [],
                   'diagb32': [], 'ts_a': None, 'ts_b': None, 'top': collections.Counter()}
    starts = sorted((v['a'], k) for k, v in want.items())
    ent_tr = {k: {'win': 0, 'hold_lines': []} for k, _, _ in ents}
    ent_by_line = sorted(ents, key=lambda x: x[1])
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    head = fh.read(8 << 20)
    heads = sorted(set(m.group(0)[:160].decode('utf-8', 'replace') for m in HEADRE.finditer(head)))
    fh.close()
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    active = []
    si = 0
    cur_ent = None
    ei = 0
    last_ts = None
    i = 0
    try:
        for l in fh:
            i += 1
            if (i & 0xFFFFF) == 0:
                gate()
            while ei < len(ent_by_line) and ent_by_line[ei][1] <= i:
                cur_ent = ent_by_line[ei]
                ei += 1
            while si < len(starts) and starts[si][0] < i:
                active.append(starts[si][1])
                si += 1
            t = l.strip()
            m = TS.match(t)
            if m:
                hh, mi, ss, ms = (int(x) for x in m.groups())
                last_ts = hh * 3600 + mi * 60 + ss + ms / 1000.0
            istr = t[:1] == b'%' or (GCN.match(t) is not None) or t.startswith(b'AsyncPipelines: skipped draw') or \
                (t.startswith(b'AsyncPipelines: flip') and b' held' in t)
            if istr and cur_ent is not None:
                et = ent_tr[cur_ent[0]]
                if cur_ent[2] is None or i <= cur_ent[2]:
                    et['win'] += 1
                else:
                    et['hold_lines'].append(i)
            if not active:
                if si >= len(starts) and ei >= len(ent_by_line):
                    pass
                continue
            done = []
            for k in active:
                w = want[k]
                if i > w['b']:
                    done.append(k)
                    continue
                if w['ts_a'] is None:
                    w['ts_a'] = last_ts
                if i == w['b']:
                    w['ts_b'] = last_ts
                    continue
                w['il'] += 1
                if not t:
                    continue
                if t[:1] == b'%':
                    w['ir'] += 1
                    continue
                if GCN.match(t):
                    w['gcn'] += 1
                    continue
                if t.startswith(b'AsyncPipelines: skipped draw'):
                    w['skip'] += 1
                elif t.startswith(b'AsyncPipelines: flip') and b' held' in t:
                    w['held'] += 1
                elif t.startswith(b'SkipCeil: flip') and b' held' in t:
                    w['skipceil'] += 1
                elif t.startswith(b'CsPretranslate: miss'):
                    w['cs_miss'] += 1
                elif b'Vulkan pipeline cache: saved' in t:
                    mm = US_PAR.search(t)
                    w['pcs'].append((i, int(mm.group(1)) if mm else -1, last_ts))
                elif t.startswith(b'PriorityStall:'):
                    mm = US_EQ.search(t)
                    w['prio_n'] += 1
                    w['prio_max'] = max(w['prio_max'], int(mm.group(1)) if mm else 0)
                elif t.startswith(b'MainTaskLate:'):
                    mm = US_EQ.search(t)
                    w['mtl_n'] += 1
                    w['mtl_max'] = max(w['mtl_max'], int(mm.group(1)) if mm else 0)
                elif t.startswith(WINP):
                    w['win'] += 1
                    if len(w['win_ex']) < 6:
                        w['win_ex'].append('%d:%s' % (i, t[:80].decode('utf-8', 'replace')))
                    if t.startswith(b'Pause: true'):
                        w['pause_on'] += 1
                    elif t.startswith(b'Pause: false'):
                        w['pause_off'] += 1
                elif t.startswith(b'LogAsync: stall'):
                    if len(w['logasync']) < 4:
                        w['logasync'].append('%d:%s' % (i, t[:160].decode('utf-8', 'replace')))
                elif t.startswith(b'DiagB32:'):
                    if len(w['diagb32']) < 3:
                        w['diagb32'].append('%d:%s' % (i, t[:400].decode('utf-8', 'replace')))
                w['top'][NUM.sub(b'X', t)[:70]] += 1
            for k in done:
                active.remove(k)
    finally:
        fh.close()
    for w in want.values():
        w['top'] = [[k.decode('utf-8', 'replace'), v] for k, v in w['top'].most_common(8)]
    return path, want, ent_tr, heads


def main():
    gate()
    mrg, binmap, outp = sys.argv[1:4]
    course = {}
    for l in open(binmap, encoding='utf-8'):
        x = l.rstrip(chr(10)).split(chr(9))
        if x[0] not in ('9235a7ac', 'dac02fb9'):
            course[x[3]] = x[0]
    frames = load_frames()
    recs = [r for r in json.load(open(mrg + '/agg_f32a.json', encoding='utf-8')) if not r['dup_of'] and not r['in_f0']]
    rows = []
    jobs = []
    ok = True
    tot = collections.Counter()
    for r in recs:
        if r['build'] not in course:
            continue
        ev, val = events_of(mrg + '/seg', r)
        if val:
            continue
        ref = [x for x in frames(ev, False)]
        mine = list_hold(ev)
        if len(ref) != len(mine):
            print('FAILED entries', r['path'], len(ref), len(mine))
            ok = False
            continue
        ivs = []
        ents = []
        for ei, (a, b) in enumerate(zip(ref, mine)):
            ents.append(('%d' % ei, b['line'], b['win_end_line']))
            if a['first_n'] is None:
                continue
            tot['entries'] += 1
            if a['k3h'] != len(b['k3h']) or sum(1 for k in a['k2'] if k[2] == 'h') != len(b['k2h']):
                print('FAILED I1', r['path'], ei, a['k3h'], len(b['k3h']), len(b['k2h']))
                ok = False
            tot['k3h_ref'] += a['k3h']
            tot['k2h_ref'] += sum(1 for k in a['k2'] if k[2] == 'h')
            ekey = '%d' % ei
            for cls, lst in (('K3', b['k3h']), ('K2', b['k2h'])):
                for n, dt, line, pl, idx in lst:
                    key = '%d' % line
                    ivs.append((pl, line, key))
                    rows.append({'path': r['path'], 'build': course[r['build']], 'level': b['level'], 'entry': ei,
                                 'entry_line': b['line'], 'first_n': b['first_n'], 'n': n, 'dt_us': dt, 'line': line,
                                 'prev_line': pl, 'idx': idx, 'cls': cls, 'key': key, 'ekey': ekey})
                    tot['listed_' + cls] += 1
        if ivs:
            jobs.append((r['path'], ivs, ents))
    print('course logs without validation scanned for entries; entries', tot['entries'], 'K3 hold ref', tot['k3h_ref'],
          'listed', tot['listed_K3'], '| K2 hold ref', tot['k2h_ref'], 'listed', tot['listed_K2'], '| logs with frames', len(jobs))
    if tot['k3h_ref'] != tot['listed_K3'] or tot['k2h_ref'] != tot['listed_K2']:
        ok = False
    pool = multiprocessing.Pool(min(12, max(1, len(jobs))))
    res = {}
    for path, want, ent_tr, heads in pool.imap_unordered(scan_log, jobs, chunksize=1):
        res[path] = (want, ent_tr, heads)
    pool.close()
    pool.join()
    logs = {}
    for row in rows:
        want, ent_tr, heads = res[row['path']]
        row['iv'] = want[row['key']]
        et = ent_tr[row['ekey']]
        row['tr_win'] = et['win']
        row['tr_hold_before'] = sum(1 for x in et['hold_lines'] if x < row['line'])
        row['tr_hold_all'] = len(et['hold_lines'])
        logs[row['path']] = heads
    json.dump({'rows': rows, 'heads': logs}, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('rows', len(rows), 'logs', len(logs))
    print('ALL OK' if ok else 'FAILED')


if __name__ == '__main__':
    main()
