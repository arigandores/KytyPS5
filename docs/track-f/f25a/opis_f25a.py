"""Track F link F25a (HPP-660; ROADMAP s122 item 593 (d)(2)(i)): inventory of every hold of pot_treasure_cave (B36) and
bonus_path_maker_mix (B40) on the course-line binaries since 9235a7ac.  Offline, read-only.  ASCII only.

    python opis_f25a.py [--out <txt>] [--json <json>]

Scene, first scene frame, interval, dump lines, hold, hold frame and attribution are those of the F20c/F20e reader
(e8ea0a57:docs/track-f/f20l3/f20e_read.py, scan() and attr(), letter variant) with the level name as a parameter.
Added (this link): frames >= 1 s anywhere after the level line; every 'PriorityStall:' line with the frame it falls into;
the time of a frame from the level line (sum of dt_us of every FrameTrace after the level line - the domain of the lead
recount of item 593 (a)); the top normalised interval line kinds of a frame >= 1 s; cache manifests before / after.
"""
import hashlib
import json
import lzma
import math
import os
import re
import sys

LOGS = (  # tag, log, json, cache dir, form ; found by the search of item 'search' in f25a.md s1 (all tag json under C:/kyty)
    ('v143_08', 'C:/kyty/s143/log_v143_08.txt', 'C:/kyty/s143/v143_08.json', 'C:/kyty/s143/runs143', 'V'),
    ('v144_10', 'C:/kyty/s144/log_v144_10.txt', 'C:/kyty/s144/v144_10.json', 'C:/kyty/s144/runs144', 'V'),
    ('v145_14', 'C:/kyty/s145/log_v145_14.txt', 'C:/kyty/s145/v145_14.json', 'C:/kyty/s145/runs145', 'V'),
    ('r146_04', 'C:/kyty/s146/log_r146_04.txt', 'C:/kyty/s146/r146_04.json', 'C:/kyty/s146/runs146', 'V'),
    ('w143_08', 'C:/kyty/s143/log_w143_08.txt', 'C:/kyty/s143/w143_08.json', 'C:/kyty/s143/runs143', 'W'),
    ('w144_10', 'C:/kyty/s144/log_w144_10.txt', 'C:/kyty/s144/w144_10.json', 'C:/kyty/s144/runs144', 'W'),
    ('w145_14', 'C:/kyty/s145/log_w145_14.txt', 'C:/kyty/s145/w145_14.json', 'C:/kyty/s145/runs145', 'W'),
)
COURSE = ('9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987', 'adb0c82f', '9325446c', '8df61c00',
          '2c9b69b9', 'b3cee576')
PRE_S12 = ('9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987')
SLOW_US = 100000
K1S_US = 1000000
WIN_US = 10000000
HOLD_US = 300000000
FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
DRAWS = re.compile(rb' draws=(\d+)')
GCN = re.compile(rb'[0-9a-fA-F]+: [A-Z]_')
US_EQ = re.compile(rb' us=(\d+)')
PS = re.compile(rb'PriorityStall: tick=(\d+) unsub=(\d+) us=(\d+) site=(\S+)')
LVL = b'Level has started:'
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
NORM = re.compile(rb'(0x[0-9a-fA-F]+|[0-9a-fA-F]{8,}|\d+)')


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def new_iv():
    return dict(ir=0, gcn=0, pcs=0, trip=0, prio=0, prio_us=0, lines=0, skipped=0, kinds={})


def scan(path, level):
    f = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    lv = level.encode()
    r = dict(level_line=None, first_n=None, ended_by=None, frames=[], prio=[], death=[], lvl_names=[], quit=False)
    state = 0
    cur = new_iv()
    sum_scene = 0
    sum_lvl = 0
    ln = 0
    for line in f:
        ln += 1
        if line.startswith(b'FrameTrace: n='):
            m = FT.match(line)
            if m:
                n, dt = int(m.group(1)), int(m.group(2))
                if state == 1:
                    if r['first_n'] is None:
                        d = DRAWS.search(line)
                        if d and int(d.group(1)) >= 100:
                            r['first_n'] = n
                            r['first_t_lvl'] = sum_lvl
                    else:
                        fr = dict(idx=len(r['frames']) + 1, n=n, dt=dt, t_scene=sum_scene, t_lvl=sum_lvl, ir=cur['ir'], gcn=cur['gcn'],
                                  pcs=cur['pcs'], trip=cur['trip'], prio=cur['prio'], prio_us=cur['prio_us'], lines=cur['lines'],
                                  skipped=cur['skipped'])
                        if dt >= K1S_US:
                            fr['kinds'] = sorted(cur['kinds'].items(), key=lambda kv: -kv[1])[:12]
                        if dt >= SLOW_US or fr['prio']:
                            r['frames'].append(fr)
                        else:
                            r['frames'].append(dict(idx=fr['idx'], n=n, dt=dt, t_scene=sum_scene, t_lvl=sum_lvl, small=1))
                        sum_scene += dt
                    sum_lvl += dt
                cur = new_iv()
                continue
        if state == 1:
            cur['lines'] += 1
        if b'---' in line or b'Unhandled' in line or b'GpuHang' in line or b'DeviceLost' in line:
            for d in DEATH:
                if d in line and len(r['death']) < 20:
                    r['death'].append([d.decode(), ln])
        i = line.find(LVL)
        if i != -1:
            name = line[i + len(LVL):].strip()
            if name:
                r['lvl_names'].append(name.decode('ascii', 'replace'))
                if state == 1:
                    state = 2
                    r['ended_by'] = 'level'
                elif state == 0 and name == lv:
                    state = 1
                    r['level_line'] = ln
            continue
        if line.startswith(b'Event: quit'):
            r['quit'] = True
            if state == 1:
                state = 2
                r['ended_by'] = 'quit'
            continue
        t = line.strip()
        if not t:
            continue
        if state == 1 and t[:1] != b'%' and not (line[:1] != b'\t' and GCN.match(t)):
            k = NORM.sub(b'#', t[:48]).decode('ascii', 'replace')
            cur['kinds'][k] = cur['kinds'].get(k, 0) + 1
        if t[:1] == b'%':
            cur['ir'] += 1
        elif line[:1] != b'\t' and GCN.match(t):
            cur['gcn'] += 1
        elif b'Vulkan pipeline cache: saved' in t:
            cur['pcs'] += 1
        elif t.startswith(b'BvhLoopCapTrip:'):
            cur['trip'] += 1
        elif t.startswith(b'PriorityStall:'):
            cur['prio'] += 1
            u = US_EQ.search(t)
            if u:
                cur['prio_us'] = max(cur['prio_us'], int(u.group(1)))
            m = PS.match(t)
            if m and state == 1:
                r['prio'].append(dict(us=int(m.group(3)), unsub=int(m.group(2)), site=m.group(4).decode(), line=ln,
                                      next_frame_idx=len(r['frames']) + 1, t_scene=sum_scene))
        elif t.startswith(b'AsyncPipelines: skipped draw'):
            cur['skipped'] += 1
    f.close()
    r['lines'] = ln
    r['scene_us'] = sum_scene
    r['lvl_us'] = sum_lvl
    return r


def attr(fr, binary):
    """F20c / F20e letter variant: cache save (before adb0c82f) -> B33; BvhLoopCapTrip -> B1b; dump -> B5; PriorityStall only
    -> 'prio only'; else 'nothing'.  Unattributed = 'nothing' + 'prio only'."""
    if fr['pcs'] and binary[:8] in PRE_S12:
        return 'B33'
    if fr['trip']:
        return 'B1b'
    if fr['ir'] or fr['gcn']:
        return 'B5'
    if fr['prio']:
        return 'prio only'
    return 'nothing'


def cp(k, n, lo):
    """Clopper-Pearson bound, two-sided 95 % (ana_f20a.py / f20e_read.py)."""
    if n == 0:
        return float('nan')
    if lo and k == 0:
        return 0.0
    if not lo and k == n:
        return 1.0
    a = 0.025

    def cdf(p, kk):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, kk + 1))
    x, y = 0.0, 1.0
    for _ in range(60):
        m = (x + y) / 2
        if lo:
            if 1 - cdf(m, k - 1) < a:
                x = m
            else:
                y = m
        else:
            if cdf(m, k) > a:
                x = m
            else:
                y = m
    return (x + y) / 2


def cache_diff(cdir, tag):
    try:
        a = json.load(open('%s/cache_%s.before.json' % (cdir, tag), encoding='utf-8'))
        b = json.load(open('%s/cache_%s.after.json' % (cdir, tag), encoding='utf-8'))
    except Exception:
        return None
    fa = dict(((x[0], x[1]), x[4]) for x in a['files'])
    fb = dict(((x[0], x[1]), x[4]) for x in b['files'])
    add = sorted(k for k in fb if k not in fa)
    rem = sorted(k for k in fa if k not in fb)
    chg = sorted(k for k in fa if k in fb and fa[k] != fb[k])
    kinds = {}
    for k in add + chg:
        kinds[k[0]] = kinds.get(k[0], 0) + 1
    return dict(before=len(fa), after=len(fb), added=len(add), removed=len(rem), changed=len(chg), kinds=kinds)


def last_flag(cmd, flag):
    v = None
    for i, a in enumerate(cmd or []):
        if a == flag:
            v = cmd[i + 1] if i + 1 < len(cmd) else ''
    return v


def one(tag, log, js, cdir, form):
    j = json.load(open(js, encoding='utf-8'))
    binary = j.get('binary_sha256') or ''
    ga = j.get('guest_args') or (j.get('env') or {}).get('KYTY_GUEST_ARGS') or ''
    level = ga.split()[-1]
    cmd = j.get('cmdline') or []
    r = scan(log, level)
    fr = [x for x in r['frames'] if 'small' not in x]
    hold = r['scene_us'] >= HOLD_US
    hf = [x for x in fr if x['dt'] >= SLOW_US and x['t_scene'] >= WIN_US]
    for x in hf:
        x['attr'] = attr(x, binary)
    k1s = [x for x in fr if x['dt'] >= K1S_US]
    allfr = r['frames']
    dump_scene = sum(x.get('ir', 0) + x.get('gcn', 0) for x in fr)
    out = dict(tag=tag, form=form, log=log, log_sha256=sha_file(log), json=js, binary=binary, course=binary[:8] in COURSE, level=level,
               env=sorted(k for k in (j.get('env') or {})), validation=last_flag(cmd, '--vulkan-validation'),
               shader_validation=last_flag(cmd, '--shader-validation'), rd='--rd' in cmd, hold_s_json=j.get('hold_s'),
               level_line=r['level_line'], first_n=r['first_n'], first_t_lvl_s=round(r.get('first_t_lvl', 0) / 1e6, 3),
               ended_by=r['ended_by'], quit=r['quit'], lvl_names=r['lvl_names'][:6], frames=len(allfr),
               scene_s=round(r['scene_us'] / 1e6, 3), hold=hold, death=r['death'], dump_lines_scene=dump_scene,
               dump_frames_scene=sum(1 for x in fr if x.get('ir', 0) + x.get('gcn', 0)),
               k1s=[dict(n=x['n'], idx=x['idx'], dt=x['dt'], t_scene_s=round(x['t_scene'] / 1e6, 3), t_lvl_s=round(x['t_lvl'] / 1e6, 3),
                         ir=x['ir'], gcn=x['gcn'], pcs=x['pcs'], trip=x['trip'], prio=x['prio'], prio_us=x['prio_us'], lines=x['lines'],
                         skipped=x['skipped'], attr=attr(x, binary), kinds=x.get('kinds')) for x in k1s],
               hold_frames=[dict(n=x['n'], idx=x['idx'], dt=x['dt'], t_scene_s=round(x['t_scene'] / 1e6, 3), ir=x['ir'], gcn=x['gcn'],
                                 pcs=x['pcs'], trip=x['trip'], prio=x['prio'], prio_us=x['prio_us'], lines=x['lines'], attr=x['attr'])
                            for x in hf],
               prio=r['prio'], cache=cache_diff(cdir, tag))
    # neighbours of every frame >= 1 s (idx -3..+3) and frames >= 70 ms on the hold (U5(2) form of item 550 (zh))
    by_idx = dict((x['idx'], x) for x in allfr)
    out['k1s_neigh'] = [[(by_idx[i]['n'], by_idx[i]['dt']) for i in range(x['idx'] - 3, x['idx'] + 4) if i in by_idx] for x in k1s]
    out['k70_hold'] = sum(1 for x in allfr if x['dt'] >= 70000 and x['t_scene'] >= WIN_US)
    dts = sorted(x['dt'] for x in allfr if x['t_scene'] >= WIN_US)
    out['hold_dt_median'] = dts[len(dts) // 2] if dts else None
    return out


def main(argv):
    import multiprocessing
    with multiprocessing.Pool(len(LOGS)) as pool:
        res = pool.starmap(one, LOGS)
    lines = ['F25a inventory (opis_f25a.py sha256 %s)' % sha_file(os.path.abspath(__file__))]
    for o in res:
        lines.append('')
        lines.append('TAG %s form %s level %s binary %s course %s val %s shval %s rd %s hold_s(json) %s' % (
            o['tag'], o['form'], o['level'], o['binary'][:8], o['course'], o['validation'], o['shader_validation'], o['rd'], o['hold_s_json']))
        lines.append('  log %s sha256 %s' % (o['log'], o['log_sha256']))
        lines.append('  env keys %s' % o['env'])
        lines.append('  level line %s first scene n %s (t from level line %.3f s) ended %s quit %s levels %s' % (
            o['level_line'], o['first_n'], o['first_t_lvl_s'], o['ended_by'], o['quit'], o['lvl_names']))
        lines.append('  scene %.3f s over %d frames; hold %s; hold dt median %s; frames >= 70 ms on hold %d; death %s' % (
            o['scene_s'], o['frames'], o['hold'], o['hold_dt_median'], o['k70_hold'], o['death']))
        lines.append('  dump lines in scene %d in %d frames; cache manifest %s' % (o['dump_lines_scene'], o['dump_frames_scene'], o['cache']))
        lines.append('  FRAMES >= 1 s after the first scene frame: %d' % len(o['k1s']))
        for x, nb in zip(o['k1s'], o['k1s_neigh']):
            lines.append('    K2 n %d idx %d dt_us %d t_scene %.3f s t_lvl %.3f s | ir %d gcn %d pcs %d trip %d prio %d/%d lines %d skipped %d | %s' % (
                x['n'], x['idx'], x['dt'], x['t_scene_s'], x['t_lvl_s'], x['ir'], x['gcn'], x['pcs'], x['trip'], x['prio'], x['prio_us'],
                x['lines'], x['skipped'], x['attr']))
            lines.append('      neighbours (n, dt_us) idx-3..+3: %s' % nb)
            lines.append('      interval kinds: %s' % x['kinds'])
        lines.append('  HOLD FRAMES >= 100 ms at >= 10 s: %d; unattributed (nothing + prio only) %d' % (
            len(o['hold_frames']), sum(1 for x in o['hold_frames'] if x['attr'] in ('nothing', 'prio only'))))
        for x in o['hold_frames'][:60]:
            lines.append('    n %d idx %d dt_us %d t %.3f s | ir %d gcn %d pcs %d trip %d prio %d/%d lines %d | %s' % (
                x['n'], x['idx'], x['dt'], x['t_scene_s'], x['ir'], x['gcn'], x['pcs'], x['trip'], x['prio'], x['prio_us'], x['lines'],
                x['attr']))
        lines.append('  PriorityStall lines in the scene: %d (>= 50 ms %d); max %s us' % (
            len(o['prio']), sum(1 for p in o['prio'] if p['us'] >= 50000), max([p['us'] for p in o['prio']] or [0])))
        for p in sorted(o['prio'], key=lambda p: -p['us'])[:12]:
            lines.append('    us %d unsub %d site %s frame idx %d t %.3f s' % (p['us'], p['unsub'], p['site'], p['next_frame_idx'],
                                                                         p['t_scene'] / 1e6))
    # p by level: V holds on course binaries without validation, rd, shader validation
    lines.append('')
    for lv in ('pot_treasure_cave', 'bonus_path_maker_mix'):
        vs = [o for o in res if o['level'] == lv and o['form'] == 'V' and o['course'] and o['validation'] == 'false' and not o['rd']
              and o['hold']]
        k = sum(1 for o in vs if any(x['t_scene_s'] >= 10 for x in o['k1s']))
        k100 = sum(1 for o in vs if any(x['attr'] in ('nothing', 'prio only') for x in o['hold_frames']))
        n = len(vs)
        lines.append('P %s: V holds %d (%s); with a frame >= 1 s at >= 10 s %d -> p %.3f, 95 %% CP [%.3f; %.3f]; with an unattributed '
                     'frame >= 100 ms at >= 10 s %d' % (lv, n, [o['tag'] for o in vs], k, k / n if n else float('nan'), cp(k, n, True),
                                                        cp(k, n, False), k100))
        ws = [o for o in res if o['level'] == lv and o['form'] == 'W' and o['hold']]
        kw = sum(1 for o in ws if any(x['t_scene_s'] >= 10 for x in o['k1s']))
        lines.append('  reference W (validation) holds %d (%s); with a frame >= 1 s at >= 10 s %d' % (len(ws), [o['tag'] for o in ws], kw))
    vs = [o for o in res if o['form'] == 'V' and o['course'] and o['validation'] == 'false' and o['hold']]
    k = sum(1 for o in vs if any(x['t_scene_s'] >= 10 for x in o['k1s']))
    lines.append('P both levels: V holds %d; with a frame >= 1 s at >= 10 s %d -> p %.3f, 95 %% CP [%.3f; %.3f]' % (
        len(vs), k, k / len(vs), cp(k, len(vs), True), cp(k, len(vs), False)))
    txt = '\n'.join(lines) + '\n'
    if '--out' in argv:
        open(argv[argv.index('--out') + 1], 'w', encoding='ascii', errors='replace', newline='\n').write(txt)
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, indent=1, sort_keys=True)
    sys.stdout.write(txt)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
