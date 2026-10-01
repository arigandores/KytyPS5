# aud144.py - Session Auditor, s144 step 3 (HPP-333). Own recount of the sc144 outputs and the window / swapchain lines of the logs.
# Independent of sc144.py / sc143.py / gate144.py: no import, no shared code. Rules by the letter of pred/01_sc144.md s.2-4,
# pred/02_sc143.md s.2-3 and ROADMAP s122 items 221 (v)-(g), 224, 242, 254 (e), (k), 266. Reads the logs through mmap in binary
# mode, never whole text. READ ONLY for the session files; writes only <out.json> and stdout.
# Usage: python aud144.py <out.json> [--workers N]
import sys, re, json, hashlib, mmap, os, bisect, statistics
from multiprocessing import Pool

S144 = 'C:/kyty/s144'
S143 = 'C:/kyty/s143'
S142 = 'C:/kyty/s142'
L143 = ['spring_punch_sky_aztec', 'booster_construction', 'mini_astro_clock_tower', 'path_maker_mana_tree',
        'spring_punch_monster_cave', 'gulliver_island', 'rocket_hourglass', 'pot_treasure_cave', 'booster_magic_lamp',
        'rocket_space_station']
W8 = ['spring_punch_sky_aztec', 'booster_construction', 'mini_astro_clock_tower', 'path_maker_mana_tree',
      'spring_punch_monster_cave', 'gulliver_island', 'booster_magic_lamp', 'rocket_space_station']
P12 = ['rocket_hourglass', 'pot_treasure_cave', 'bumper_enemy_snowy_canyon', 'big_hand_pirate_island', 'timestop_casino',
       'ice_iceberg', 'sponge_dirty_bath', 'hoover_beach', 'volcano_mountain', 'voxel_world', 'enemy_gorilla',
       'mini_giants_garden']
FT = b'FrameTrace: n='
LVL = b'GuestOut: Level has started: '
DEATH = [b'GpuHangAbort:', b'ErrorDeviceLost', b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---']
RAW = [b'PipelinePrecache:', b'Vulkan pipeline cache:', b'ShaderSeed:', b'ShaderPreparation:', b'BvhLoopCapTrip:']
COUNT = [b'[Vulkan][E]', b'[Vulkan][', b'no validation layer:',
         b'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features', b'opcode is not implemented',
         b'=== Stubbed function', b'GuestOut', b'vkCreateComputePipelines begin', b'vkCreateGraphicsPipelines begin']
# window / swapchain lines of the emulator (4fc501f4 window.cpp:428-495, swapchain.cpp:353-358, 592-607, 727-739, 945)
WIN = [b'Window 1 ', b'minimized', b'restored', b'maximized', b'size changed to', b'resized to', b'keyboard focus',
       b'Mouse entered window', b'Mouse left window', b'Recovering Vulkan swapchain', b'eErrorOutOfDateKHR', b'eSuboptimalKHR',
       b'eErrorSurfaceLostKHR', b'vkAcquireNextImageKHR returned', b'vkQueuePresentKHR returned',
       b'Vulkan presentation retry exhausted', b'vkCreateSwapchainKHR', b'Event: ']
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


def line_at(mm, p, cap=600):
    a = mm.rfind(b'\n', 0, p) + 1
    e = mm.find(b'\n', p)
    if e == -1:
        e = len(mm)
    return a, mm[a:min(e, a + cap)]


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
            cnt = {}
            first_pos = {}
            for k in COUNT:
                ps = positions(mm, k)
                cnt[k.decode()] = len(ps)
                first_pos[k.decode()] = ps[0] if ps else None
                if k == b'[Vulkan][E]':
                    R['vke_lines'] = [line_at(mm, p, 400)[1].decode('ascii', 'replace') for p in ps[:3]]
                    R['vke_pos'] = ps[:5]
            R['count'] = cnt
            R['first_pos'] = first_pos
            # skipped draws: lines, distinct frame= ids (the reading of the seal, debt D-7), FrameTrace intervals (own first reading)
            sk = positions(mm, b'AsyncPipelines: skipped draw')
            ids = set()
            noid = 0
            for p in sk:
                a, ln = line_at(mm, p, 400)
                m = RF.search(ln)
                if m:
                    ids.add(int(m.group(1)))
                else:
                    noid += 1
            R['skip'] = {'lines': len(sk), 'frames_by_id': len(ids), 'lines_without_id': noid,
                         'frames_by_interval': len(set(bisect.bisect_left(rp, p) for p in sk))}
            # PriorityStall
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
                raw[k.decode()] = ls[:60]
                raw[k.decode() + '#n'] = len(ls)
            R['raw'] = raw
            R['recipes_arrow_lines'] = len(RREC.findall(mm))
            ep = next((p for p, nm in starts if nm == level), None) if level else None
            R['entry_pos'] = ep

            def ctx(p):
                # the last FrameTrace row before byte p; presented time after the entry line up to it
                k = bisect.bisect_left(rp, p)
                if k == 0:
                    return {'rows_before': 0}
                last = rows[k - 1]
                out = {'rows_before': k, 'last_n': last[1], 'rows_after': len(rows) - k}
                if ep is not None:
                    out['dt_after_entry_us'] = sum(r[2] for r in rows[:k] if r[0] > ep)
                return out

            win = {}
            for k in WIN:
                ps = positions(mm, k)
                ev = []
                for p in ps[:40]:
                    a, ln = line_at(mm, p, 240)
                    c = ctx(p)
                    c.update({'key_pos': p, 'line_start': a, 'line': ln.decode('ascii', 'replace').rstrip('\r')})
                    ev.append(c)
                win[k.decode()] = {'n': len(ps), 'events': ev}
            R['win'] = win
            if ep is not None:
                ch = [p for p, nm in starts if p > ep]
                cut = ch[0] if ch else None
                R['scene_changes'] = [(p, nm) for p, nm in starts if p > ep]
                after = [r for r in rows if r[0] > ep and (cut is None or r[0] < cut)]
                R['sum_dt_after_entry_us'] = sum(r[2] for r in after)
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
                    # variant vx: rows before the first "Event: quit" line and without the last row of the log (second reading; run 1 dropped the last row before quit)
                    q = mm.find(b'Event: quit')
                    pv2 = [r for r in post if (q == -1 or r[0] < q) and r[0] != rows[-1][0]]
                    R['quit_pos'] = q if q != -1 else None
                    R['vx'] = {'frames': len(pv2), 'dt_us': sum(r[2] for r in pv2)}
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
    out['win'] = {k.decode(): data.count(k) for k in WIN}
    out['ended'] = data.count(b'the game ENDED inside the hold')
    return out


def job(a):
    tag, level, root, logname = a
    R = {'tag': tag, 'level': level, 'root': root}
    try:
        R['log'] = scan_log('%s/%s' % (root, logname), level)
    except OSError as e:
        R['log'] = {'error': repr(e)}
    R['emu_stdout'] = scan_small('%s/stdout_%s.txt' % (root, tag))
    R['es_stdout'] = scan_small('%s/%s.stdout.txt' % (root, tag))
    try:
        R['json'] = json.load(open('%s/%s.json' % (root, tag), encoding='utf-8'))
    except (OSError, ValueError) as e:
        R['json'] = {'error': repr(e)}
    return R


def main():
    outp = sys.argv[1]
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 8
    jobs = [('w144_00', 'underwater_aerial_garden', S144)]
    for i, lv in enumerate(W8, 1):
        jobs.append(('w144_%02d' % i, lv, S144))
    for i, lv in enumerate(P12, 9):
        jobs.append(('v144_%02d' % i, lv, S144))
        jobs.append(('w144_%02d' % i, lv, S144))
    for i, lv in enumerate(L143, 1):
        jobs.append(('v143_%02d' % i, lv, S143))
        jobs.append(('w143_%02d' % i, lv, S143))
    jobs.append(('v142', 'underwater_aerial_garden', S142))
    jobs.append(('w142', 'underwater_aerial_garden', S142))
    for i in range(1, 11):
        jobs.append(('c142_%02d' % i, None, S142))
    jobs = [(t, lv, root, 'log_%s.txt' % t) for t, lv, root in jobs]
    known = set((root, ln) for _, _, root, ln in jobs)
    # every other log_*.txt of the three session roots (root directory only): scanned for the window lines too
    for root in (S142, S143, S144):
        for f in sorted(os.listdir(root)):
            if re.match(r'log_.*\.txt$', f) and (root, f) not in known:
                jobs.append((f[4:-4], None, root, f))
    with Pool(workers) as pool:
        res = pool.map(job, jobs, chunksize=1)
    json.dump(res, open(outp, 'w', encoding='ascii'), ensure_ascii=True, indent=1)
    for r in res:
        L = r['log']
        w = L.get('win', {})
        print(r['tag'], r['root'][-4:], L.get('sha256', '')[:16], 'size', L.get('size'), 'rows', L.get('rows_total'),
              'entry', L.get('entry_pos') is not None, 'first', L.get('first'), 'k2', L.get('k2'),
              'vkE', (L.get('count') or {}).get('[Vulkan][E]'), 'marks', L.get('n_marks'),
              'minimized', (w.get('minimized') or {}).get('n'), 'recover', (w.get('Recovering Vulkan swapchain') or {}).get('n'))
    print('LOGS %d' % len(res))
    print('ALL DONE')


if __name__ == '__main__':
    main()
