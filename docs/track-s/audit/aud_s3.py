# Session Auditor, track S link S11a (HPP-493): independent recount of the S10 readings (ROADMAP item 408 (b)-(e)).
# Own parser and own derivations; does not import sc_s.py / sc_s9.py / sc142.py.  Logs are read as a binary stream.
import sys, os, re, json, hashlib, subprocess, statistics
from multiprocessing import Pool

ROOT = 'C:/kyty/s288/s10'
OUT = 'C:/kyty/s288/s11a'
LEVEL = {'pi_w1': 'underwater_aerial_garden', 'pi_r1': 'underwater_aerial_garden', 'pi_w0': 'underwater_aerial_garden',
         'pi_r0': 'underwater_aerial_garden', 'c5_0': 'shuriken_ninja_castle', 't2_1': 'hero_kratos', 't2_cs0': 'hero_kratos',
         't2_2': 'hero_drake', 't2_3': 'voxel_challenge_3', 't2_4': 'armadillo_challenge_2', 't2_5': 'fragile_battle_4',
         't2_6': 'voxel_challenge_4', 't2_7': 'fragile_battle_5', 'u_1': 'underwater_aerial_garden', 'u_2': 'hoover_beach',
         'u_3': 'robot_builder_next', 'u_4': 'interactive_credit_00', 'u_5': 'fragile_battle_1'}
TAGS = list(LEVEL)
DRAWS_SCENE = 100
MS100 = 100000
S1 = 1000000

re_ft = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) ')
re_draws = re.compile(rb' draws=(\d+)')
re_cg = re.compile(rb' cpu_gpu_us=(\d+)')
re_fx = re.compile(rb'^FrameTrace-x: n=(\d+) ')
re_aps = re.compile(rb' skc_ap_skip=(\d+)')
re_hinc = re.compile(rb' skc_held_inc=(\d+)')
re_hk = re.compile(rb' skc_held=(\d+)')
re_skip = re.compile(rb'frame=(\d+) vs=0x([0-9a-fA-F]+) ps=0x([0-9a-fA-F]+)')
re_us = re.compile(rb' us=(\d+)')
re_wus = re.compile(rb' waited_us=(\d+)')
re_shader = re.compile(rb'^AvTrace: shader (.+?) hash=0x([0-9a-fA-F]+) translate_us=(\d+) compile_us=(\d+)')
re_hash = re.compile(rb' hash=(?:0x)?([0-9a-fA-F]+)')
re_host = re.compile(rb' host_us=(\d+)')
re_saved = re.compile(rb'^Vulkan pipeline cache: saved (\d+) bytes')
re_loaded = re.compile(rb'^Vulkan pipeline cache: loaded (\d+) bytes')
re_rsave = re.compile(rb'^PipelinePrecache: saved (\d+) recipes')
re_queued = re.compile(rb'^PipelinePrecache: (\d+) recipes -> (\d+) graphics \+ (\d+) compute pipelines queued')
re_created = re.compile(rb'^PipelinePrecache: all pipelines created, (\d+) ms')
re_waited = re.compile(rb'^ShaderPreparation: startup wait finished in (\d+) ms')
re_elapsed = re.compile(rb' elapsed_ms=(\d+)')
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')


def h16(b):
    return b.decode().lower().rjust(16, '0')


def parse(path):
    P = dict(rows=[], x={}, skips=[], starts=[], pipe=[], sh=[], load=[], prio=[], dsave=[], dload=[], disabled=0, rsave=[],
             queued=None, created_ms=None, ready=0, waited_ms=None, prog_max=None, prog_n=0, reg={}, first={}, seed=0, csp={},
             bvh=[], death=0, vke=0, gamepatch=0, pcw_wait=0, lines=0, skip_nof=0, spcw=[])
    h = hashlib.sha256()
    rows = P['rows']
    with open(path, 'rb') as f:
        for line in f:
            h.update(line)
            P['lines'] += 1
            ln = P['lines']
            g = len(rows)
            c = line[:2]
            if c == b'Fr':
                m = re_ft.match(line)
                if m:
                    d = re_draws.search(line)
                    cg = re_cg.search(line)
                    rows.append((int(m.group(1)), int(m.group(2)), int(d.group(1)) if d else -1, int(cg.group(1)) if cg else 0, ln))
                    continue
                m = re_fx.match(line)
                if m:
                    a = re_aps.search(line); b = re_hinc.search(line); k = re_hk.search(line)
                    P['x'][int(m.group(1))] = (int(a.group(1)) if a else None, int(b.group(1)) if b else None,
                                               int(k.group(1)) if k else None)
                continue
            if c == b'As':
                if line.startswith(b'AsyncPipelines: skipped draw'):
                    m = re_skip.search(line)
                    if m:
                        P['skips'].append((g, int(m.group(1)), h16(m.group(2)), h16(m.group(3)), ln))
                    else:
                        P['skip_nof'] += 1
                        P['skips'].append((g, None, None, None, ln))
                continue
            if c == b'Av':
                if line.startswith(b'AvTrace: pipeline '):
                    body = line.rstrip()
                    kind = 'gfx' if body.startswith(b'AvTrace: pipeline gfx') else 'cs'
                    w = re_wus.search(body)
                    u = re_us.search(body)
                    toks = body.split(b' ')
                    if w:
                        sub = 'waited'; us = int(w.group(1))
                    else:
                        us = int(u.group(1)) if u else 0
                        if b'async' in toks:
                            sub = 'async'
                        elif toks[-1] == b'precache':
                            sub = 'precache'
                        elif b'sync' in toks:
                            sub = 'sync'
                        else:
                            sub = 'none'
                    P['pipe'].append((g, kind, sub, us, ln, u is not None, b'precache' in body))
                elif line.startswith(b'AvTrace: shader '):
                    m = re_shader.match(line)
                    if m:
                        P['sh'].append((g, h16(m.group(2)), int(m.group(3)) + int(m.group(4)), ln))
                elif line.startswith(b'AvTrace: shader-cache load'):
                    u = re_us.search(line)
                    P['load'].append((g, int(u.group(1)) if u else 0))
                elif line.startswith(b'AvTrace: pcw overlap wait'):
                    P['pcw_wait'] += 1
                continue
            if c == b'Pr':
                if line.startswith(b'PriorityStall:'):
                    u = re_us.search(line)
                    P['prio'].append((g, int(u.group(1)) if u else -1))
                continue
            if c == b'Pi':
                m = re_rsave.match(line)
                if m:
                    P['rsave'].append((g, int(m.group(1)), ln)); continue
                m = re_queued.match(line)
                if m and P['queued'] is None:
                    P['queued'] = (int(m.group(1)), int(m.group(2)), int(m.group(3))); continue
                m = re_created.match(line)
                if m and P['created_ms'] is None:
                    P['created_ms'] = int(m.group(1))
                continue
            if c == b'Vu':
                m = re_saved.match(line)
                if m:
                    P['dsave'].append((g, int(m.group(1)), ln)); continue
                m = re_loaded.match(line)
                if m:
                    P['dload'].append(int(m.group(1))); continue
                if line.startswith(b'Vulkan pipeline cache: disabled'):
                    P['disabled'] += 1
                continue
            if c == b'Sh':
                if line.startswith(b'ShaderRegister:'):
                    m = re_hash.search(line); t = re_host.search(line)
                    if m and t:
                        k = h16(m.group(1)); v = int(t.group(1))
                        if k not in P['reg'] or v < P['reg'][k]:
                            P['reg'][k] = v
                elif line.startswith(b'ShaderFirstUse:'):
                    m = re_hash.search(line); t = re_host.search(line)
                    if m and t:
                        k = h16(m.group(1))
                        if k not in P['first']:
                            P['first'][k] = int(t.group(1))
                elif line.startswith(b'ShaderPreparation: ready'):
                    P['ready'] += 1
                elif line.startswith(b'ShaderPreparation: startup wait finished'):
                    m = re_waited.match(line)
                    if m and P['waited_ms'] is None:
                        P['waited_ms'] = int(m.group(1))
                elif line.startswith(b'ShaderPreparation: progress '):
                    P['prog_n'] += 1
                    m = re_elapsed.search(line)
                    if m and (P['prog_max'] is None or int(m.group(1)) > P['prog_max']):
                        P['prog_max'] = int(m.group(1))
                elif line.startswith(b'ShaderSeed: installed'):
                    P['seed'] += 1
                continue
            if c == b'S-':
                if line.startswith(b'S-pcw:'):
                    P['spcw'].append(line.strip().decode('latin1'))
                continue
            if c == b'Cs':
                if line.startswith(b'CsPretranslate: '):
                    w = line[16:].split(b' ', 1)[0].strip().decode('latin1')
                    P['csp'][w] = P['csp'].get(w, 0) + 1
                continue
            if c == b'Bv':
                if line.startswith(b'BvhLoopCapTrip:'):
                    P['bvh'].append(g)
                continue
            if c == b'Gu':
                if line.startswith(b'GuestOut: Level has started:'):
                    P['starts'].append((g, line.split(b'Level has started:', 1)[1].strip().decode('latin1'), ln))
                continue
            if c == b'Ga':
                if line.startswith(b'GamePatch:'):
                    P['gamepatch'] += 1
                continue
            if b'[Vulkan][E]' in line:
                P['vke'] += 1
            for d in DEATH:
                if d in line:
                    P['death'] += 1
    P['sha256'] = h.hexdigest()
    return P


def stdout_counts(path):
    r = dict(shaders=0, prepare_cold=0)
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            for line in f:
                if line.startswith(b'Shaders: VS'):
                    r['shaders'] += 1
                elif line.startswith(b'Cache test mode: prepare-cold'):
                    r['prepare_cold'] += 1
    return r


def derive(tag, P, so, js):
    level = LEVEL[tag]
    rows = P['rows']
    N = len(rows)
    R = dict(tag=tag, level=level, sha256=P['sha256'], rows=N, lines=P['lines'], death=P['death'], vke=P['vke'],
             gamepatch=P['gamepatch'], seed_installed=P['seed'], prepare_cold=so['prepare_cold'], stdout_shaders=so['shaders'],
             saves=len(P['dsave']), last_saved=P['dsave'][-1][1] if P['dsave'] else None, loaded=P['dload'],
             disabled=P['disabled'], created_ms=P['created_ms'], waited_ms=P['waited_ms'], prog_n=P['prog_n'],
             prog_max=P['prog_max'], skip_lines=len(P['skips']), skip_nof=P['skip_nof'], bvh_lines=len(P['bvh']),
             csp=P['csp'], pcw_wait=P['pcw_wait'], spcw=sorted(set(P['spcw'])))
    ap = lambda i: (P['x'].get(rows[i][0]) or (None, None, None))[0] or 0
    hi = lambda i: (P['x'].get(rows[i][0]) or (None, None, None))[1] or 0
    # whole-log identities
    R['t1_whole'] = (sum(ap(i) for i in range(N)), len(P['skips']))
    R['t6_whole'] = (len(set(e[1] for e in P['skips'] if e[1] is not None)), sum(hi(i) for i in range(N)))
    # in-game creations (item 355 (d)): AvTrace: pipeline lines without the word precache, with a us field
    cre = [e for e in P['pipe'] if not e[6] and e[5]]
    R['create_n'] = len(cre)
    R['create_med'] = statistics.median([e[3] for e in cre]) if cre else None
    R['create_nous'] = sum(1 for e in P['pipe'] if not e[6] and not e[5])
    # entry
    ent = [k for k, e in enumerate(P['starts']) if e[1] == level]
    if not ent:
        R['entered'] = False
        return R
    R['entered'] = True
    eg, _, el = P['starts'][ent[0]]
    nxt = P['starts'][ent[0] + 1:]
    end = nxt[0][0] if nxt else N
    fi = next((i for i in range(eg, end) if rows[i][2] >= DRAWS_SCENE), None)
    R['entry_line'] = el
    R['scene_end_row'] = end
    if fi is None:
        R['first'] = None
        return R
    f0 = rows[fi][0]
    R['first'] = (f0, rows[fi][1])
    R['dt_after_first_us'] = sum(rows[i][1] for i in range(fi + 1, end))
    # item 404 domain identities
    R['t1_dom'] = (sum(ap(i) for i in range(N) if rows[i][0] >= f0), sum(1 for e in P['skips'] if e[1] is not None and e[1] >= f0))
    R['t6_dom'] = (len(set(e[1] for e in P['skips'] if e[1] is not None and e[1] >= f0)), sum(hi(i) for i in range(N) if rows[i][0] >= f0))
    # skip lines read by members outside the item 404 domain
    R['skip_after_entry'] = sum(1 for e in P['skips'] if e[4] > el)
    R['skip_after_entry_before_f0'] = sum(1 for e in P['skips'] if e[4] > el and (e[1] is None or e[1] < f0))
    R['skip_groups_fi_m1_fi'] = sum(1 for e in P['skips'] if fi - 1 <= e[0] <= fi)
    R['skip_groups_fi_m1_fi_below_f0'] = sum(1 for e in P['skips'] if fi - 1 <= e[0] <= fi and (e[1] is None or e[1] < f0))
    R['skip_lines_before_f0'] = sum(1 for e in P['skips'] if e[1] is not None and e[1] < f0)
    R['skips_group_after_fi'] = sum(1 for e in P['skips'] if e[0] > fi)
    R['skip_frames_dom_distinct'] = R['t6_dom'][0]
    # frame counts after the first scene frame
    R['skip_rows'] = sum(1 for i in range(fi + 1, end) if ap(i) > 0)
    R['held'] = sum(hi(i) for i in range(fi + 1, end)) + (hi(fi) if hi(fi) > 0 else 0)
    R['dt100_all'] = sum(1 for i in range(fi + 1, end) if rows[i][1] >= MS100)
    R['presented100'] = sum(1 for i in range(fi + 1, end) if rows[i][1] >= MS100 and hi(i) == 0)
    R['dt1s_all'] = sum(1 for i in range(fi + 1, end) if rows[i][1] >= S1)
    # T-3 / T-4
    pre = sum(1 for e in P['pipe'] if e[2] == 'precache')
    q = P['queued']
    R['t3'] = (len(P['sh']), so['shaders'])
    R['t4'] = (pre, (q[1] + q[2]) if q else None)
    attr_ok = R['t3'][0] == R['t3'][1] and ((q is not None and pre == q[1] + q[2]) or (tag == 'c5_0' and q is None and pre == 0))
    R['attr_ok'] = attr_ok
    # PREP: each line to the row with the largest dt among rows g-1 .. g+2 (earliest on a tie)
    prep = {}

    def put(g, us):
        best = None
        for i in range(g - 1, g + 3):
            if 0 <= i < N and (best is None or rows[i][1] > rows[best][1]):
                best = i
        if best is not None:
            prep[best] = prep.get(best, 0) + us
    for g, _, us, _ in P['sh']:
        put(g, us)
    for g, kind, sub, us, _, _, _ in P['pipe']:
        if (kind == 'gfx' and sub == 'none') or (kind == 'cs' and sub == 'sync') or sub == 'waited':
            put(g, us)
    for g, us in P['load']:
        put(g, us)
    skip_g = set(e[0] for e in P['skips'])
    async_gfx_g = set(e[0] for e in P['pipe'] if e[1] == 'gfx' and e[2] == 'async')
    save_g = set(e[0] for e in P['dsave']) | set(e[0] for e in P['rsave'])
    prio_by_g = {}
    for g, us in P['prio']:
        if us > 0:
            prio_by_g[g] = prio_by_g.get(g, 0) + us

    def cls(i):
        dt, cg = rows[i][1], rows[i][3]
        p = prep.get(i, 0)
        pcw = i in save_g or (i + 1) in save_g
        shader = attr_ok and (dt - p < MS100 or any(k in skip_g for k in range(i - 2, i + 2)) or any(k in async_gfx_g for k in range(i - 2, i + 2)))
        idle = cg * 2 < dt
        prio = prio_by_g.get(i, 0) * 2 >= dt and prio_by_g.get(i + 1, 0) * 2 >= dt and idle
        if pcw:
            c = 'PCW'
        elif shader:
            c = 'SHADER'
        elif prio:
            c = 'PRIO'
        elif cg * 2 >= dt:
            c = 'GPUTHR'
        else:
            c = 'WAIT'
        return c, shader, p
    # held series (reading 1: with the first scene frame when it is held)
    lo = fi if hi(fi) > 0 else fi + 1
    ser = []
    i = lo
    while i < end:
        if hi(i) > 0:
            j = i
            while j < end and hi(j) > 0:
                j += 1
            close = j if j < end else None
            idx = list(range(i, j)) + ([close] if close is not None else [])
            gap = sum(rows[k][1] for k in idx)
            sub = sum(rows[k][1] for k in idx if rows[k][1] >= MS100 and cls(k)[0] == 'PRIO')
            asy = [e for e in P['pipe'] if idx[0] <= e[0] <= idx[-1] and e[1] == 'gfx' and e[2] == 'async']
            ser.append(dict(a=i, b=j, n0=rows[i][0], n1=rows[j - 1][0], flips=j - i, gap=gap, gap_pipe=gap - sub,
                            async_us=sum(e[3] for e in asy), async_n=len(asy)))
            i = j
        else:
            i += 1
    R['series'] = [dict((k, v) for k, v in x.items() if k not in ('a', 'b')) for x in ser]
    longs = []
    for i in range(fi + 1, end):
        if rows[i][1] >= MS100:
            c, shd, p = cls(i)
            longs.append(dict(i=i, n=rows[i][0], dt=rows[i][1], cls=c, shader=shd, prep=p, held=hi(i) > 0,
                              bvh=sum(1 for g in P['bvh'] if i - 1 <= g <= i)))
    R['long'] = [dict((k, v) for k, v in x.items() if k != 'i') for x in longs]
    if attr_ok:
        counted = lambda x: x['shader'] or x['cls'] == 'PCW'
        R['att100'] = sum(1 for x in longs if counted(x) and not x['held']) + sum(1 for x in ser if x['gap_pipe'] >= MS100)
        R['att100_rows'] = sum(1 for x in longs if counted(x) and not x['held'])
        R['att100_series'] = sum(1 for x in ser if x['gap_pipe'] >= MS100)
        R['att_pcw100'] = sum(1 for x in longs if x['cls'] == 'PCW' and not x['held'])
        R['att1s'] = sum(1 for x in longs if counted(x) and not x['held'] and x['dt'] >= S1) + sum(1 for x in ser if x['gap_pipe'] >= S1)
        un = [x for x in longs if not x['held'] and not counted(x)]
        R['unatt100'] = dict(n=len(un), WAIT=sum(1 for x in un if x['cls'] == 'WAIT'), GPUTHR=sum(1 for x in un if x['cls'] == 'GPUTHR'),
                             PRIO=sum(1 for x in un if x['cls'] == 'PRIO'), rows=[(x['n'], x['dt'], x['cls']) for x in un],
                             series=sum(1 for x in ser if x['gap'] >= MS100 and x['gap_pipe'] < MS100))
        # S-early
        lead = dict((k, P['first'][k] - P['reg'][k]) for k in P['first'] if k in P['reg'])
        ev = []
        for x in longs:
            if x['shader']:
                i = x['i']
                hs = set(e[1] for e in P['sh'] if i - 2 <= e[0] <= i + 1)
                ls = [lead[k] for k in hs if k in lead]
                asy = sum(e[3] for e in P['pipe'] if i - 2 <= e[0] <= i + 1 and e[2] == 'async')
                ev.append(dict(kind='frame', n=x['n'], held=x['held'], lead=min(ls) if ls else None, cost=x['prep'] + asy, cost_prep=x['prep']))
        for x in ser:
            if x['gap_pipe'] >= MS100:
                hs = set()
                for e in P['skips']:
                    if x['a'] <= e[0] <= x['b'] and e[2]:
                        hs.add(e[2]); hs.add(e[3])
                ls = [lead[k] for k in hs if k in lead]
                ev.append(dict(kind='series', n=x['n0'], n1=x['n1'], lead=min(ls) if ls else None, cost=x['async_us'], cost_prep=x['async_us']))
        R['early'] = ev
    # cold gate, item 241 (v)(7) / item 362 (b)
    rec_end = max([e[1] for e in P['rsave']] + [q[0] if q else 0])
    rec_before = max([e[1] for e in P['rsave'] if e[2] < el] + [q[0] if q else 0])
    R['gate'] = dict(perm_after=sum(1 for e in P['sh'] if e[3] > el), rec_new_after=rec_end - rec_before,
                     skip_after=R['skip_after_entry'], create_after=sum(1 for e in cre if e[4] > el))
    R['gate']['cold_letter'] = bool(attr_ok and R['gate']['perm_after'] >= 1 and R['gate']['rec_new_after'] >= 1 and R['gate']['skip_after'] >= 1)
    at = ((js or {}).get('attempts') or [{}])[0]
    R['prep_created_s'] = at.get('prep_created_s')
    R['prep_ready_s'] = at.get('prep_ready_s')
    return R


def one(tag):
    P = parse('%s/log_%s.txt' % (ROOT, tag))
    so = stdout_counts('%s/stdout_%s.txt' % (ROOT, tag))
    jp = '%s/%s.json' % (ROOT, tag)
    js = json.load(open(jp, encoding='utf-8')) if os.path.isfile(jp) else None
    R = derive(tag, P, so, js)
    json.dump(R, open('%s/rec_%s.json' % (OUT, tag), 'w', encoding='ascii'), indent=1)
    return tag


def haze(tag):
    """Own implementation of the lead detector by the letter of item 355 (g): crop 300x60 at (660, 60), scale 60x12, mean of
    (max - min) / (max + 1), low = below 0.75 of the median of the frames >= 300, gap <= 3, end - start >= 5."""
    import numpy as np
    v = '%s/rec_%s.mp4' % (ROOT, tag)
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', v, '-vf', 'crop=300:60:660:60,scale=60:12', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    fs = 60 * 12 * 3
    n = len(raw) // fs
    a = np.frombuffer(raw[:n * fs], dtype=np.uint8).reshape(n, 60 * 12, 3).astype(np.float64)
    mx = a.max(axis=2); mn = a.min(axis=2)
    sat = ((mx - mn) / (mx + 1.0)).mean(axis=1)
    med = float(np.median(sat[300:])) if n > 300 else 0.0
    low = [i for i in range(300, n) if sat[i] < med * 0.75]
    runs = []
    for i in low:
        if runs and i - runs[-1][1] <= 3:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    kept = [r for r in runs if r[1] - r[0] >= 5]
    R = dict(tag=tag, frames=n, med=round(med, 4), low=len(low), series=kept, letter=[r for r in kept if r[0] > 1002],
             variant=[r for r in kept if r[1] > 1002], video_sha256=hashlib.sha256(open(v, 'rb').read()).hexdigest(),
             all_runs_after_1002=[r for r in runs if r[1] > 1002])
    json.dump(R, open('%s/haze_%s.json' % (OUT, tag), 'w', encoding='ascii'), indent=1)
    return tag


if __name__ == '__main__':
    if os.path.exists('C:/kyty/SEALED_RUN.lock'):
        print('LOCKED'); sys.exit(5)
    if os.path.exists('C:/kyty/s288/STOP'):
        print('STOP'); sys.exit(4)
    mode = sys.argv[1]
    tags = sys.argv[2:] or (TAGS if mode == 'logs' else ['pi_w1', 'pi_r1', 'pi_w0', 'pi_r0'])
    with Pool(3) as p:
        for t in p.imap_unordered(one if mode == 'logs' else haze, tags):
            print('done', t, flush=True)
