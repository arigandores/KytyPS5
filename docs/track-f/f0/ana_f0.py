# F0 (HPP-289): analysis of the sweep for the register. Reads agg_f0.json + seg pickles (per-log signature counts).
import os, re, json, pickle, hashlib, collections

OUT = 'C:/kyty/f287/f0'
SEG = OUT + '/seg'
SEG_BYTES = 256 << 20
recs = json.load(open(OUT + '/agg_f0.json', encoding='utf-8'))
uniq = [r for r in recs if not r['dup_of']]


def sigs_of(r):
    md = hashlib.md5(r['path'].encode('utf-8')).hexdigest()
    n = 1 if r['size'] <= SEG_BYTES else (r['size'] + SEG_BYTES - 1) // SEG_BYTES
    d = {}
    off = 0
    for i in range(n):
        x = pickle.load(open('%s/%s_%d.pkl' % (SEG, md, i), 'rb'))
        for k, v in x['sigs'].items():
            e = d.get(k)
            if e is None:
                d[k] = [v[0], v[1] + off, v[2]]
            else:
                e[0] += v[0]
        off += x['lines']
    return d


def band(s):
    if s is None:
        return 'none'
    return '<50' if s < 50 else '50-102' if s < 103 else '103-112' if s < 113 else '113-127' if s < 128 else '128-141' if s < 142 else '142+'


BANDS = ['none', '<50', '50-102', '103-112', '113-127', '128-141', '142+']
tag = lambda r: r['path'].replace('C:/kyty/', '')
cache = OUT + '/logsigs_f0.pkl'
if os.path.exists(cache):
    LS = pickle.load(open(cache, 'rb'))
else:
    LS = {r['path']: sigs_of(r) for r in uniq}
    pickle.dump(LS, open(cache, 'wb'), protocol=4)

print('unique logs', len(uniq), {b: sum(1 for r in uniq if band(r['session']) == b) for b in BANDS})
print('with a non-empty level start:', sum(1 for r in uniq if r['levels']), ' with FrameTrace:', sum(1 for r in uniq if r['ft']))
lv = collections.Counter()
lv128 = collections.Counter()
for r in uniq:
    for L in r['levels']:
        lv[L] += 1
        if r['session'] is not None and r['session'] >= 128:
            lv128[L] += 1
print('(0) levels started (unique logs):', dict(lv))
print('    on s128+:', dict(lv128))

print()
print('(1) opcode profile per log (OPCODE_NI lines by family/opcode)')
prof = collections.Counter()
profex = {}
for r in uniq:
    p = tuple(sorted((k.decode('latin1').replace('OPCODE_NI ', ''), v[0]) for k, v in LS[r['path']].items() if k.startswith(b'OPCODE_NI')))
    if p:
        prof[p] += 1
        profex.setdefault(p, []).append(r)
for p, n in prof.most_common():
    ss = [x['session'] for x in profex[p] if x['session'] is not None]
    print('  ', n, 'logs; sessions', (min(ss), max(ss)) if ss else '-', '; s128+:', sum(1 for s in ss if s >= 128), '|', p, '| e.g.', tag(profex[p][-1]))
print('   logs with FrameTrace and no OPCODE_NI line, s113+:', [tag(r) for r in uniq if r['ft'] and r['session'] and r['session'] >= 113 and not any(k.startswith(b'OPCODE_NI') for k in LS[r['path']])][:40])


def table(title, pred, show=12, minsess=0):
    print()
    print(title)
    by = collections.defaultdict(list)
    for r in uniq:
        hits = [(k, v) for k, v in LS[r['path']].items() if pred(k)]
        if hits:
            by[band(r['session'])].append((r, hits))
    print('   logs by band:', {b: len(by[b]) for b in BANDS if by[b]}, ' denominators:', {b: sum(1 for r in uniq if band(r['session']) == b) for b in BANDS})
    for b in BANDS:
        for r, hits in by[b][:show] if b not in ('113-127', '128-141', '142+') else by[b]:
            if r['session'] is not None and r['session'] < minsess:
                continue
            print('     [%s] %s lv=%s | %s' % (b, tag(r), ','.join(r['levels']) or '-', '; '.join('%dx@%d %s' % (v[0], v[1], v[2].decode('latin1')[:150].strip()) for k, v in hits[:3])))
    return by


table('(2a) --- Fatal Error ---', lambda k: k.startswith(b'--- Fatal Error'), minsess=103)
table('(2b) --- Error ---', lambda k: k.startswith(b'--- Error ---'), minsess=103)
table('(2c) Error: condition', lambda k: k.startswith(b'Error: condition') or k.startswith(b'Assertion failed'), show=40)
table('(2d) GpuHangAbort', lambda k: k.startswith(b'GpuHangAbort'), minsess=103)
table('(2e) ErrorDeviceLost', lambda k: b'ErrorDeviceLost' in k, show=40)
table('(2f) Unhandled host exception / too many objects', lambda k: k.startswith(b'Unhandled host exception') or b'too many objects' in k, show=40)
table('(2g) [Vulkan][E]', lambda k: k.startswith(b'[Vulkan][E]'), show=40)
table('(2h) Stubbed function / stub called', lambda k: b'Stubbed function' in k or k.startswith(b'Unresolved import stub called'), show=40)
table('(2i) BvhLoopCapTrip', lambda k: k.startswith(b'BvhLoopCapTrip'), show=40)
table('(2j) KernelRead direct read failed', lambda k: k.startswith(b'KernelRead: direct'), show=3, minsess=113)
table('(2k) CsStall kind=wait', lambda k: k.startswith(b'CsStall: kind=wait'), show=3, minsess=128)
table('(2l) LossWin overflow / TextureCache failed / failed to create image', lambda k: k.startswith(b'LossWin') or k.startswith(b'TextureCache: failed') or k.startswith(b'failed to create'), show=40)
table('(2m) hold_exit / game ENDED', lambda k: b'hold_exit' in k or b'game ENDED' in k, show=40)
table('(2n) AudioOut SDL_QueueAudio failed', lambda k: k.startswith(b'AudioOut: SDL_QueueAudio failed'), show=3, minsess=100)
table('(2o) Controller disconnect', lambda k: k.startswith(b'Controller:'), show=40)

print()
print('(3) frames after the first scene frame, logs without validation (vk_w < 100); K2 = dt >= 1 s, K3 = 100 ms <= dt < 1 s')
rows = collections.defaultdict(lambda: collections.Counter())
k2list = []
k3hold = []
for r in uniq:
    if r['validation'] or r['session'] is None:
        continue
    for s in r['scenes']:
        if s['first_n'] is None:
            continue
        key = (band(r['session']), s['level'])
        c = rows[key]
        c['entries'] += 1
        kw = [x for x in s['k2'] if x[2] == 'w']
        kh = [x for x in s['k2'] if x[2] == 'h']
        if kw:
            c['k2w_logs'] += 1
        if kh:
            c['k2h_logs'] += 1
        if s['k3w']:
            c['k3w_logs'] += 1
        if s['k3h']:
            c['k3h_logs'] += 1
        if (kw or kh) and r['session'] >= 113:
            k2list.append((r, s))
        if s['k3h'] and r['session'] >= 128:
            k3hold.append((r, s))
print('   band | level | entries | logs K2 window | logs K2 hold | logs K3 window | logs K3 hold')
for key in sorted(rows, key=lambda k: (BANDS.index(k[0]), k[1])):
    c = rows[key]
    if BANDS.index(key[0]) >= 3:
        print('   %s | %s | %d | %d | %d | %d | %d' % (key[0], key[1], c['entries'], c['k2w_logs'], c['k2h_logs'], c['k3w_logs'], c['k3h_logs']))
print('   K2 frames, s113+:')
for r, s in k2list:
    print('     ', tag(r), s['level'], 'first_n', s['first_n'], 'k2', s['k2'][:4], 'late_max', r['met'].get('late_max'), 'sha', r['sha256'][:8])
print('   K3 on hold, s128+:')
for r, s in k3hold:
    print('     ', tag(r), s['level'], 'first_n', s['first_n'], 'k3h', s['k3h'], s['k3h_ex'][:6], 'frames', s['frames'], 'sha', r['sha256'][:8])

print()
print('(4) PriorityStall > 50 ms and the frame that contains it (next FrameTrace line): logs without validation')
for b in BANDS[4:]:
    L = [r for r in uniq if band(r['session']) == b and not r['validation'] and r['ft'] and r['levels']]
    P = [r for r in L if r['met'].get('prio_gt50', 0)]
    st = sum(r['prio_frames'][0] for r in P)
    f100 = sum(r['prio_frames'][1] for r in P)
    f1s = sum(r['prio_frames'][2] for r in P)
    sites = collections.Counter()
    for r in P:
        sites.update(r['prio_sites'])
    print('   %s: logs with level+FrameTrace %d, with stall>50ms %d; stalls %d, in a frame dt>=100ms %d, dt>=1s %d; max us %s; sites %s' % (
        b, len(L), len(P), st, f100, f1s, max([r['met'].get('prio_max', 0) for r in P] or [0]), dict(sites.most_common(6))))
    W = [0, 0, 0, 0]
    for r in L:
        for s in r['scenes']:
            W[0] += s['p_w']; W[1] += s['pf_w']; W[2] += s['p_h']; W[3] += s['pf_h']
    print('      after the first scene frame: window stalls %d (in frame>=100ms %d), hold stalls %d (in frame>=100ms %d); logs with a hold stall: %d' % (W[0], W[1], W[2], W[3], sum(1 for r in L if any(s['p_h'] for s in r['scenes']))))
    if b == '142+':
        for r in L:
            print('      ', tag(r), r['levels'], 'prio_n', r['met'].get('prio_n', 0), 'max', r['met'].get('prio_max', 0), 'frames>=100ms/1s', r['prio_frames'])

print()
print('(5) AsyncPipelines: skipped draw - logs by band and level (unique logs, any gate)')
c = collections.Counter()
for r in uniq:
    if r['met'].get('skip_n', 0):
        c[(band(r['session']), ','.join(r['levels']) or '-')] += 1
for k in sorted(c, key=lambda k: (BANDS.index(k[0]), k[1])):
    if BANDS.index(k[0]) >= 4:
        print('   ', k, c[k])

print()
print('(6) MainTaskLate >= 1 s, s113+')
for r in uniq:
    if r['met'].get('late_ge1s', 0) and r['session'] and r['session'] >= 113:
        print('   ', tag(r), r['levels'], 'n', r['met']['late_ge1s'], 'max', r['met']['late_max'], 'validation', r['validation'])

print()
print('(7) s142 logs')
for r in uniq:
    if r['session'] == 142:
        s = r['scenes'][-1] if r['scenes'] else None
        m = r['met']
        print('   ', tag(r), r['sha256'][:16], 'lines', r['lines'], 'lvl', r['levels'], 'first_n', s and s['first_n'], 'frames', s and s['frames'], 'sum_s', s and round(s['sum_us'] / 1e6, 1),
              'k2', s and s['k2'], 'k3w/h', s and (s['k3w'], s['k3h']), 'max_w/h', s and (s['max_w'], s['max_h']), 'k3h_ex', s and s['k3h_ex'][:3], 'k3w_ex', s and s['k3w_ex'][:10], 'prio>50 w/h', s and (s['p_w'], s['p_h']), 'in frame>=100ms w/h', s and (s['pf_w'], s['pf_h']),
              '| skip', m.get('skip_n', 0), m.get('skip_frames', 0), 'prio', m.get('prio_n', 0), m.get('prio_max', 0), 'trip', m.get('trip_n', 0), m.get('trip_max', 0),
              'late', m.get('late_n', 0), m.get('late_max', 0), 'vkE', r['vk_e'], 'vkW', r['vk_w'])
print()
print('(8) emulator folder logs:', [(tag(r), r['session'], r['dup_of'], r['levels']) for r in recs if 'ps5 em' in r['path']])
print('(9) overflow of signature cap:', sum(r['met'].get('over', 0) for r in recs), 'lines in', sum(1 for r in recs if r['met'].get('over', 0)), 'logs')
