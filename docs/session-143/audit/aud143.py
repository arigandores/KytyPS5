# aud143.py - Session Auditor, s143 step 3 (HPP-300). Own recount of the sc143 outputs and the cache lines of the logs.
# Independent of sc143.py / sc142.py: no import, no shared code. Rules by the letter of pred/02_sc143.md s.2-3 and
# ROADMAP s122 items 221 (v)-(g), 224, 231 (i), 242. Reads the logs through mmap in binary mode, never whole text.
# Usage: python aud143.py <out.json> [--workers N]
import sys, re, json, hashlib, mmap, os, bisect, statistics
from multiprocessing import Pool

S143 = 'C:/kyty/s143'
S142 = 'C:/kyty/s142'
LEVELS = ['spring_punch_sky_aztec', 'booster_construction', 'mini_astro_clock_tower', 'path_maker_mana_tree',
          'spring_punch_monster_cave', 'gulliver_island', 'rocket_hourglass', 'pot_treasure_cave', 'booster_magic_lamp',
          'rocket_space_station']
FT = b'FrameTrace: n='
LVL = b'GuestOut: Level has started: '
DEATH = [b'GpuHangAbort:', b'ErrorDeviceLost', b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---']
RAW = [b'PipelinePrecache:', b'Vulkan pipeline cache:', b'ShaderSeed:', b'ShaderPreparation:', b'PriorityStall:',
       b'BvhLoopCapTrip:']
COUNT = [b'[Vulkan][E]', b'[Vulkan][', b'no validation layer:',
         b'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features', b'opcode is not implemented',
         b'=== Stubbed function', b'AsyncPipelines: skipped draw', b'GuestOut', b'vkCreateComputePipelines begin',
         b'vkCreateGraphicsPipelines begin']
RN = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
RD = re.compile(rb' draws=(\d+)')


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
            R['rows_total'] = len(rows)
            R['torn'] = torn
            starts = []
            for p in positions(mm, LVL):
                e = mm.find(b'\n', p)
                starts.append((p, mm[p + len(LVL):e].strip().decode('ascii', 'replace')))
            R['starts'] = [(p, nm) for p, nm in starts][:20]
            marks = []
            for k in DEATH:
                for p in positions(mm, k):
                    marks.append((p, k.decode()))
            marks.sort()
            R['marks'] = marks[:40]
            R['n_marks'] = len(marks)
            cnt = {}
            pos_first = {}
            for k in COUNT:
                ps = positions(mm, k)
                cnt[k.decode()] = len(ps)
                pos_first[k.decode()] = ps[0] if ps else None
                if k == b'AsyncPipelines: skipped draw':
                    rp = [r[0] for r in rows]
                    R['skip_frames'] = len(set(bisect.bisect_left(rp, p) for p in ps))
                if k == b'[Vulkan][E]':
                    R['vke_lines'] = [line_at(mm, p, 400)[1].decode('ascii', 'replace') for p in ps[:3]]
                    R['vke_pos'] = ps[:5]
            R['count'] = cnt
            R['first_pos'] = pos_first
            raw = {}
            for k in RAW:
                ls = []
                for p in positions(mm, k):
                    a, ln = line_at(mm, p, 500)
                    ls.append((a, ln.decode('ascii', 'replace').rstrip('\r')))
                raw[k.decode()] = ls[:400]
                raw[k.decode() + '#n'] = len(ls)
            R['raw'] = raw
            ep = next((p for p, nm in starts if nm == level), None) if level else None
            R['entry_pos'] = ep
            if ep is not None:
                ch = [p for p, nm in starts if p > ep]
                cut = ch[0] if ch else None
                R['scene_changes'] = [(p, nm) for p, nm in starts if p > ep]
                after = [r for r in rows if r[0] > ep and (cut is None or r[0] < cut)]
                R['sum_dt_after_entry_us'] = sum(r[2] for r in after)
                fi = next((k for k, r in enumerate(after) if r[3] is not None and r[3] >= 100), None)
                # the 120 s cut: the first FrameTrace row on which the sum of dt after the entry line exceeded 120 s
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
                    win, hold = post[:599], post[599:]
                    R['window'] = len(win)
                    R['hold'] = len(hold)
                    R['frames_after_first'] = len(post)
                    R['sum_dt_after_first_us'] = sum(r[2] for r in post)
                    dts = [r[2] for r in post]
                    R['dt_median_us'] = statistics.median(dts) if dts else None
                    R['dt_max_us'] = max(dts) if dts else None
                    R['k2'] = [[r[1], r[2], 'entry' if k < 599 else 'hold'] for k, r in enumerate(post) if r[2] >= 1000000]
                    R['k3w'] = [[r[1], r[2]] for r in win if 100000 <= r[2] < 1000000]
                    R['k3h'] = [[r[1], r[2]] for r in hold if 100000 <= r[2] < 1000000]
                    ns = [r[1] for r in post]
                    R['n_gaps'] = sum(1 for a, b in zip([f0[1]] + ns, ns) if b != a + 1)
                    # 120 s readings: rows strictly before the cut row (excl) and up to it (incl)
                    if cut120 is not None:
                        cp = after[cut120][0]
                        R['k2_120_excl'] = [[r[1], r[2]] for r in post if r[2] >= 1000000 and r[0] < cp]
                        R['k2_120_incl'] = [[r[1], r[2]] for r in post if r[2] >= 1000000 and r[0] <= cp]
                        R['k3h120_excl'] = [[r[1], r[2]] for r in hold if 100000 <= r[2] < 1000000 and r[0] < cp]
                        R['k3h120_incl'] = [[r[1], r[2]] for r in hold if 100000 <= r[2] < 1000000 and r[0] <= cp]
                    else:
                        R['k2_120_excl'] = R['k2_120_incl'] = [[r[1], r[2]] for r in post if r[2] >= 1000000]
                        R['k3h120_excl'] = R['k3h120_incl'] = R['k3h']
                else:
                    R['first'] = None
            if rows:
                R['dt_max_all'] = max(rows, key=lambda r: r[2])[1:3]
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
    out['count'] = {k.decode(): data.count(k) for k in COUNT}
    out['ended'] = data.count(b'the game ENDED inside the hold')
    return out


def job(a):
    tag, level, root = a
    R = {'tag': tag, 'level': level}
    try:
        R['log'] = scan_log('%s/log_%s.txt' % (root, tag), level)
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
    jobs = []
    for i, lv in enumerate(LEVELS, 1):
        jobs.append(('v143_%02d' % i, lv, S143))
        jobs.append(('w143_%02d' % i, lv, S143))
    jobs.append(('v142', 'underwater_aerial_garden', S142))
    jobs.append(('w142', 'underwater_aerial_garden', S142))
    for i in range(1, 11):
        jobs.append(('c142_%02d' % i, None, S142))
    with Pool(workers) as pool:
        res = pool.map(job, jobs, chunksize=1)
    json.dump(res, open(outp, 'w', encoding='ascii'), ensure_ascii=True, indent=1)
    for r in res:
        L = r['log']
        print(r['tag'], L.get('sha256', '')[:16], 'rows', L.get('rows_total'), 'entry', L.get('entry_pos') is not None,
              'first', L.get('first'), 'k2', L.get('k2'), 'vkE', (L.get('count') or {}).get('[Vulkan][E]'),
              'marks', L.get('n_marks'))
    print('ALL DONE')


if __name__ == '__main__':
    main()
