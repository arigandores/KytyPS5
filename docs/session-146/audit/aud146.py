# aud146.py - Session Auditor, s146 step 3 (HPP-389). Own recount of the sc146 outputs from the logs.
# Independent of sc146.py / gate146.py: no import, no shared code (a port of the auditor's own aud145.py).
# Rules by the letter of pred/02_sc146.md s.1-2, 5 and ROADMAP s122 items 221 (v)-(g), 224, 242, 273 (k), 295 (b), (g),
# 300 (b)(4), 309 (l)(4), 316. New data rows: stubs (F13), asserts (F14), DualSrcBlend. Reads the logs through mmap, binary mode.
# READ ONLY for the session files; writes only <out.json> and stdout.
# Usage: python aud146.py <out.json> [--workers N]
import sys, re, json, hashlib, mmap, os, bisect, statistics
from multiprocessing import Pool

S146 = 'C:/kyty/s146'
RL = ['hoover_beach', 'sponge_dirty_bath', 'timestop_casino', 'bonus_path_maker_mix']
LV = ['robot_builder_next', 'interactive_credit_00', 'non_interactive_credit', 'ending_boss_after_credit', 'collectible_viewer',
      'hub_crashsite_diorama', 'diorama_controller_skin', 'diorama_astro_skin', 'diorama_zoo', 'fragile_battle_1', 'voxel_challenge_1',
      'armadillo_challenge_1', 'fragile_battle_2', 'voxel_challenge_2', 'fragile_battle_3']
FT = b'FrameTrace: n='
LVL = b'GuestOut: Level has started: '
DEATH = [b'GpuHangAbort:', b'ErrorDeviceLost', b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---']
RAW = [b'PipelinePrecache:', b'Vulkan pipeline cache:', b'ShaderSeed:', b'BvhLoopCapTrip:', b'StartLevel ']
COUNT = [b'[Vulkan][E]', b'[Vulkan][', b'[Vulkan][W][2]', b'[Vulkan][E][2]', b'[Vulkan][W][1]', b'no validation layer:',
         b'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features', b'opcode is not implemented',
         b'=== Stubbed function', b'GuestOut', b'last time reporting it', b'ShaderOutputNotConsumed', b'and this write is unused',
         b'Recovering Vulkan swapchain', b'eErrorOutOfDateKHR', b'eSuboptimalKHR', b'Unresolved import stub called', b'ASSERT:',
         b'user_msg_param', b'DualSrcBlend:', b'VK_LAYER_KHRONOS_validation', b'VK_EXT_validation_features', b'VK_EXT_debug_utils']
RDUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
KINDS = ['shown', 'hidden', 'exposed', 'moved to', 'resized', 'size changed', 'minimized', 'maximized', 'restored',
         'gained keyboard focus', 'lost keyboard focus', 'closed', 'got unknown event']
RWIN = re.compile(rb'Window \d+ (shown|hidden|exposed|moved to|resized|size changed|minimized|maximized|restored|gained keyboard focus|'
                  rb'lost keyboard focus|closed|got unknown event)')
RMOUSE = re.compile(rb'Mouse (entered|left) window \d+')
RN = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
RD = re.compile(rb' draws=(\d+)')
RF = re.compile(rb'frame=(\d+)')
RUS = re.compile(rb' us=(\d+)')
RREC = re.compile(rb'PipelinePrecache: \d+ recipes ->')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 22), b''):
            h.update(c)
    return h.hexdigest()


def positions(mm, key):
    out = []
    p = mm.find(key)
    while p != -1:
        out.append(p)
        p = mm.find(key, p + 1)
    return out


def count(mm, key):
    n = 0
    first = last = None
    p = mm.find(key)
    while p != -1:
        if first is None:
            first = p
        last = p
        n += 1
        p = mm.find(key, p + len(key))
    return n, first, last


def line_at(mm, p, cap=600):
    a = mm.rfind(b'\n', 0, p) + 1
    e = mm.find(b'\n', p)
    if e == -1:
        e = len(mm)
    return a, mm[a:min(e, a + cap)]


def win_kinds(buf_iter):
    c = {k: 0 for k in KINDS}
    c['Mouse entered window'] = 0
    c['Mouse left window'] = 0
    for ln in buf_iter:
        m = RWIN.search(ln)
        if m:
            c[m.group(1).decode()] += 1
        m = RMOUSE.search(ln)
        if m:
            c['Mouse %s window' % m.group(1).decode()] += 1
    return c


def scan_log(path, level):
    R = {'log': path, 'size': os.path.getsize(path), 'sha256': sha(path)}
    if R['size'] == 0:
        return R
    with open(path, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            rows = []  # (pos, n, dt, draws)
            torn = 0
            for p in positions(mm, FT):
                if p > 0 and mm[p - 1] != 10:
                    torn += 1
                e = mm.find(b'\n', p)
                if e == -1:
                    e = len(mm)
                ln = mm[p:e]
                r = RN.match(ln)
                if r:
                    d = RD.search(ln)
                    rows.append((p, int(r.group(1)), int(r.group(2)), int(d.group(1)) if d else None))
            rp = [r[0] for r in rows]
            R['rows_total'] = len(rows)
            R['torn'] = torn
            starts = []
            for p in positions(mm, LVL):
                e = mm.find(b'\n', p)
                starts.append((p, mm[p + len(LVL):e].strip().decode('ascii', 'replace')))
            R['starts'] = starts[:20]
            marks = []
            for k in DEATH:
                for p in positions(mm, k):
                    marks.append((p, k.decode()))
            marks.sort()
            R['marks'] = marks[:40]
            R['n_marks'] = len(marks)
            cnt, first_pos, last_pos = {}, {}, {}
            for k in COUNT:
                n, a, b = count(mm, k)
                cnt[k.decode()] = n
                first_pos[k.decode()] = a
                last_pos[k.decode()] = b
            R['count'] = cnt
            R['first_pos'] = first_pos
            R['last_pos'] = last_pos
            if cnt['[Vulkan][E]']:
                ps = positions(mm, b'[Vulkan][E]')
                R['vke_lines'] = [line_at(mm, p, 400)[1].decode('ascii', 'replace') for p in ps[:3]]
            if cnt['[Vulkan][W][1]']:
                R['loader_line'] = line_at(mm, first_pos['[Vulkan][W][1]'], 80)[1].decode('ascii', 'replace')[:60]
            if cnt['last time reporting it']:
                R['limit_line'] = line_at(mm, first_pos['last time reporting it'], 300)[1].decode('ascii', 'replace')
            # message ids of the validation-layer lines: sample of the first 2000 lines + every [E] line
            ids = {}
            p = mm.find(b'[Vulkan][W][2]')
            k = 0
            while p != -1 and k < 2000:
                a, ln = line_at(mm, p, 260)
                m = re.search(rb'\[Vulkan\]\[W\]\[2\]:?\s*(.{0,90})', ln)
                key = (m.group(1)[:70].decode('ascii', 'replace') if m else '?')
                ids[key] = ids.get(key, 0) + 1
                k += 1
                p = mm.find(b'[Vulkan][W][2]', p + 1)
            R['w2_sample_heads'] = sorted(ids.items(), key=lambda x: -x[1])[:6]
            # skipped draws
            sk = positions(mm, b'AsyncPipelines: skipped draw')
            idset = set()
            for p in sk:
                a, ln = line_at(mm, p, 400)
                m = RF.search(ln)
                if m:
                    idset.add(int(m.group(1)))
            R['skip'] = {'lines': len(sk), 'frames_by_id': len(idset)}
            pv = []
            pl = positions(mm, b'PriorityStall:')
            for p in pl:
                a, ln = line_at(mm, p, 400)
                vals = [int(x) for x in RUS.findall(ln)]
                if vals:
                    pv.append(max(vals))
            R['prio'] = {'lines': len(pl), 'over': sum(1 for v in pv if v > 50000), 'max': max(pv) if pv else 0}
            raw = {}
            for k in RAW:
                ls = []
                for p in positions(mm, k):
                    a, ln = line_at(mm, p, 300)
                    ls.append((a, ln.decode('ascii', 'replace').rstrip('\r')))
                raw[k.decode()] = ls[:30]
                raw[k.decode() + '#n'] = len(ls)
            R['raw'] = raw
            R['recipes_arrow_lines'] = len(RREC.findall(mm))
            R['dual'] = [(m.start(), int(m.group(1)), int(m.group(2))) for m in RDUAL.finditer(mm)]
            gp = first_pos.get('GuestOut')
            R['dual_pre'] = sum(1 for p, s, e in R['dual'] if (s, e) == (1, 1) and (gp is None or p < gp))
            # window lines of the log: every line with "Window <id> <kind>" / "Mouse entered|left window <id>"
            wl = []
            for key in (b'Window ', b'Mouse entered window', b'Mouse left window'):
                for p in positions(mm, key):
                    a, ln = line_at(mm, p, 200)
                    if RWIN.search(ln) or RMOUSE.search(ln):
                        wl.append((a, ln.decode('ascii', 'replace').rstrip('\r')))
            wl = sorted(set(wl))
            R['win_lines'] = wl[:200]
            R['win_kinds'] = win_kinds(x[1].encode('ascii', 'replace') for x in wl)
            ep = next((p for p, nm in starts if nm == level), None) if level else None
            R['entry_pos'] = ep
            if ep is not None:
                ch = [p for p, nm in starts if p > ep]
                cut = ch[0] if ch else None
                R['scene_changes'] = [(p, nm) for p, nm in starts if p > ep]
                after = [r for r in rows if r[0] > ep and (cut is None or r[0] < cut)]
                R['sum_dt_after_entry_us'] = sum(r[2] for r in after)
                # item 295 (b)(3): the last validation-layer line ([W][2] or [E][2]) against the last hold row
                lp = [x for x in (last_pos['[Vulkan][W][2]'], last_pos['[Vulkan][E][2]']) if x is not None]
                if lp and after:
                    q = max(lp)
                    R['layer_end_us'] = sum(r[2] for r in after if r[0] > q)
                    R['layer_last_pos'] = q
                    R['layer_rows_after'] = sum(1 for r in after if r[0] > q)
                else:
                    R['layer_end_us'] = None
                # largest presented-time pause between consecutive validation-layer lines inside the hold: coarse, by FrameTrace rows
                fi = next((k for k, r in enumerate(after) if r[3] is not None and r[3] >= 100), None)
                cum = 0
                cut120 = None
                for k, r in enumerate(after):
                    cum += r[2]
                    if cum > 120000000:
                        cut120 = k
                        break
                R['cut120_pos'] = after[cut120][0] if cut120 is not None else None
                if fi is not None:
                    f0 = after[fi]
                    R['first'] = [f0[1], f0[2], f0[3]]
                    post = after[fi + 1:]
                    wn, hold = post[:599], post[599:]
                    R['window'] = len(wn)
                    R['hold'] = len(hold)
                    R['frames_after_first'] = len(post)
                    R['sum_dt_after_first_us'] = sum(r[2] for r in post)
                    dts = [r[2] for r in post]
                    R['dt_median_us'] = statistics.median(dts) if dts else None
                    R['dt_median_high_us'] = statistics.median_high(dts) if dts else None
                    R['dt_max_us'] = max(dts) if dts else None
                    R['k2'] = [[r[1], r[2], 'entry' if k < 599 else 'hold'] for k, r in enumerate(post) if r[2] >= 1000000]
                    R['k3w'] = [[r[1], r[2]] for r in wn if 100000 <= r[2] < 1000000]
                    R['k3h'] = [[r[1], r[2]] for r in hold if 100000 <= r[2] < 1000000]
                    ns = [r[1] for r in post]
                    R['n_gaps'] = sum(1 for a, b in zip([f0[1]] + ns, ns) if b != a + 1)
                    if cut120 is not None:
                        cp = after[cut120][0]
                        R['k2_120_excl'] = [[r[1], r[2]] for r in post if r[2] >= 1000000 and r[0] < cp]
                        R['k2_120_incl'] = [[r[1], r[2]] for r in post if r[2] >= 1000000 and r[0] <= cp]
                        R['k3h120_excl'] = [[r[1], r[2]] for r in hold if 100000 <= r[2] < 1000000 and r[0] < cp]
                        R['k3h120_incl'] = [[r[1], r[2]] for r in hold if 100000 <= r[2] < 1000000 and r[0] <= cp]
                    else:
                        R['k2_120_excl'] = R['k2_120_incl'] = [[r[1], r[2]] for r in post if r[2] >= 1000000]
                        R['k3h120_excl'] = R['k3h120_incl'] = R['k3h']
                    q = mm.find(b'Event: quit')
                    pv2 = [r for r in post if (q == -1 or r[0] < q) and r[0] != rows[-1][0]]
                    R['quit_pos'] = q if q != -1 else None
                    R['vx'] = {'frames': len(pv2), 'dt_us': sum(r[2] for r in pv2)}
                    # item 295 (g): the window line of the log nearest to every K2 / K3 frame after the first scene frame, +-2 s of
                    # presented time (time of a window line = end of the last FrameTrace row before it, on the clock of all rows)
                    ends = []
                    c = 0
                    for r in rows:
                        c += r[2]
                        ends.append(c)
                    wt = []
                    for a, ln in wl:
                        k = bisect.bisect_left(rp, a)
                        wt.append((ends[k - 1] if k > 0 else 0, ln))
                    near = []
                    for k, r in enumerate(post):
                        if r[2] >= 100000:
                            gi = bisect.bisect_left(rp, r[0])
                            t1 = ends[gi]
                            t0 = t1 - r[2]
                            best = None
                            for t, ln in wt:
                                d = 0 if t0 <= t <= t1 else min(abs(t - t0), abs(t - t1))
                                if d <= 2000000 and (best is None or d < best[0]):
                                    best = (d, ln[-60:])
                            near.append([r[1], r[2], 'K2' if r[2] >= 1000000 else 'K3', 'entry' if k < 599 else 'hold', best])
                    R['winnear'] = near
                else:
                    R['first'] = None
            if rows:
                R['dt_max_all'] = max(rows, key=lambda r: r[2])[1:3]
                R['last_row'] = [rows[-1][0], rows[-1][1]]
        finally:
            mm.close()
    return R


def scan_small(path):
    out = {'path': path, 'present': os.path.isfile(path)}
    if not out['present']:
        return out
    data = open(path, 'rb').read()
    out['sha256'] = hashlib.sha256(data).hexdigest()
    out['size'] = len(data)
    out['marks'] = [(data.find(k), k.decode()) for k in DEATH if k in data]
    out['count'] = {k.decode(): data.count(k) for k in COUNT + [b'PipelinePrecache:', b'ShaderSeed:']}
    out['recipes_arrow_lines'] = len(RREC.findall(data))
    out['dual'] = [(m.start(), int(m.group(1)), int(m.group(2))) for m in RDUAL.finditer(data)]
    out['win_kinds'] = win_kinds(data.splitlines())
    out['ended'] = data.count(b'the game ENDED inside the hold')
    return out


def job(a):
    tag, level, root, logpath = a
    R = {'tag': tag, 'level': level, 'root': root}
    try:
        R['log'] = scan_log(logpath, level)
    except OSError as e:
        R['log'] = {'error': repr(e)}
    R['emu_stdout'] = scan_small('%s/stdout_%s.txt' % (root, tag))
    R['es_stdout'] = scan_small('%s/%s.stdout.txt' % (root, tag))
    try:
        R['json'] = json.load(open('%s/%s.json' % (root, tag), encoding='utf-8'))
    except (OSError, ValueError) as e:
        R['json'] = {'error': repr(e)}
    R['attempt_file'] = os.path.isfile('%s/attempt_%s.txt' % (root, tag))
    return R


def main():
    outp = sys.argv[1]
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 8
    jobs = [('i146_v', 'underwater_aerial_garden', S146), ('w146_00', 'underwater_aerial_garden', S146)]
    for i, lv in enumerate(RL, 1):
        jobs.append(('r146_%02d' % i, lv, S146))
    for i, lv in enumerate(LV, 5):
        jobs.append(('v146_%02d' % i, lv, S146))
        jobs.append(('w146_%02d' % i, lv, S146))
    jobs = [(t, lv, root, '%s/log_%s.txt' % (root, t)) for t, lv, root in jobs]
    known = set(j[3] for j in jobs)
    lvof = {j[0]: j[1] for j in jobs}
    for f in sorted(os.listdir(S146)):
        if re.match(r'log_.*[.]txt$', f) and ('%s/%s' % (S146, f)) not in known:
            t = f[4:-4]
            jobs.append((t, lvof.get(t[:7]), S146, '%s/%s' % (S146, f)))
    with Pool(workers) as pool:
        res = pool.map(job, jobs, chunksize=1)
    json.dump(res, open(outp, 'w', encoding='ascii'), ensure_ascii=True, indent=1)
    for r in res:
        L = r['log']
        d = L.get('dual') or []
        c = L.get('count') or {}
        print(r['tag'], r['root'][-4:], str(L.get('sha256', L.get('error', '')))[:16], 'size', L.get('size'), 'rows', L.get('rows_total'),
              'entry', L.get('entry_pos') is not None, 'first', L.get('first'), 'k2', L.get('k2'), 'vkE', c.get('[Vulkan][E]'),
              'W2', c.get('[Vulkan][W][2]'), 'limit', c.get('last time reporting it'), 'layer_end_us', L.get('layer_end_us'),
              'marks', L.get('n_marks'), 'minimized', (L.get('win_kinds') or {}).get('minimized'), 'recover', c.get('Recovering Vulkan swapchain'),
              'stubcall', c.get('Unresolved import stub called'), 'ASSERT', c.get('ASSERT:'), 'ump', c.get('user_msg_param'),
              'dual', [x[1:] for x in d], 'dual_pre', L.get('dual_pre'), 'changes', [x[1] for x in (L.get('scene_changes') or [])])
    print('LOGS %d' % len(res))
    print('ALL DONE')


if __name__ == '__main__':
    main()
