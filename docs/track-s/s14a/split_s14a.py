# S14a (HPP-502): cost split of the T2 entry events into translation and pipeline creation, registration lead, and the
# share of shaders whose translation inputs are draw-only.  Input: extracts x_<tag>.txt (xt.py) of the S10 logs.
# No game, no code.  Output: plain text table; every number is [c] of the named log lines.
import sys, os, re, math, statistics
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
D = 'C:/kyty/s288/s14a/'
LV = [('t2_1', 'hero_kratos'), ('t2_2', 'hero_drake'), ('t2_4', 'armadillo_challenge_2'), ('t2_5', 'fragile_battle_4'),
      ('t2_7', 'fragile_battle_5'), ('t2_cs0', 'hero_kratos')]
FRAME_US = 16667
WAIT_US = 4000      # AsyncPipelineWaitUs default
r_reg = re.compile(r'^ShaderRegister: hash=([0-9a-f]+) type=(\d+) size=(\d+) scratch=(\d+) code=([0-9a-f]+) header=([0-9a-f]+) host_us=(\d+)(.*)$')
r_fu = re.compile(r'^ShaderFirstUse: hash=([0-9a-f]+) stage=(\d+) words=(\d+) ud=(\d+) host_us=(\d+)')
r_sh = re.compile(r'^AvTrace: shader ShaderRecompiler (\w+) hash=0x([0-9a-f]+) translate_us=(\d+) compile_us=(\d+) permutations=(\d+)')
r_spec = re.compile(r'^AvTrace: shader-spec ShaderRecompiler (\w+) hash=0x([0-9a-f]+) perm=(\d+)(.*)$')
r_emit = re.compile(r'^AvTrace: shader-emit (\w+) hash=0x([0-9a-f]+) emit_us=(\d+) validate_us=(\d+) module_us=(\d+) words=(\d+)')
r_pipe = re.compile(r'^AvTrace: pipeline gfx vs=(\d+) ps=(\d+) us=(\d+) total=(\d+)(.*)$')
r_skip = re.compile(r'^AsyncPipelines: skipped draw (\w+) frame=(\d+) vs=0x([0-9a-f]+) ps=0x([0-9a-f]+) pending=(\d+)')
r_held = re.compile(r'^AsyncPipelines: flip (\d+) held')
r_ft = re.compile(r'^FrameTrace: n=(\d+) dt_us=(\d+)')
r_flip = re.compile(r'^AvTrace: flip n=(\d+) t=(\d+) host=(\d+)')
r_load = re.compile(r'^AvTrace: shader-cache load hash=0x([0-9a-f]+)')
out = []
P = out.append
tot = dict(series=0, obs=0, model=0, model_lo=0, tr_wall=0, cr_sum=0, hold_wall=0)
allsh = []
for tag, lv in LV:
    reg = {}      # hash -> list of (line, host_us, type, regs text)
    fu = {}       # hash -> (line, host_us, stage)
    ent = None
    cur = []      # lines of the current group (until the next FrameTrace row)
    groups = []   # dict per FrameTrace row
    loads = set()
    nreg_b = nreg_a = 0
    with open(D + 'x_%s.txt' % tag, 'rb') as f:
        for raw in f:
            ln, b = raw.rstrip(b'\n').split(b'\t', 1)
            ln = int(ln); s = b.decode('latin1')
            if ent is None and s.startswith('GuestOut: Level has started: ' + lv):
                ent = ln
            m = r_reg.match(s)
            if m:
                reg.setdefault(m.group(1), []).append((ln, int(m.group(7)), int(m.group(2)), m.group(8)))
                if ent: nreg_a += 1
                else: nreg_b += 1
                continue
            m = r_fu.match(s)
            if m:
                fu.setdefault(m.group(1), (ln, int(m.group(5)), int(m.group(2))))
                continue
            m = r_load.match(s)
            if m: loads.add(m.group(1))
            m = r_ft.match(s)
            if m:
                groups.append(dict(n=int(m.group(1)), dt=int(m.group(2)), line=ln, after=ent is not None, ev=cur))
                cur = []
                continue
            cur.append((ln, s))
    P('== %s %s: entry line %s; ShaderRegister lines %d before / %d after entry, distinct hashes %d; ShaderFirstUse hashes %d'
      % (tag, lv, ent, nreg_b, nreg_a, len(reg), len(fu)))
    # per group facts after the entry
    rows = []
    for g in groups:
        if not g['after'] and not any(l > (ent or 0) for l, _ in g['ev']): continue
        d = dict(n=g['n'], dt=g['dt'], sh=[], pipes=[], skips=0, skip_pairs=set(), held=False, flip=None, rsave=0, dsave=0, spec={}, emit={})
        for l, s in g['ev']:
            if ent is None or l < ent: continue
            m = r_sh.match(s)
            if m: d['sh'].append((m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), int(m.group(5)), l)); continue
            m = r_spec.match(s)
            if m:
                t = m.group(4); d['spec'][(m.group(2), int(m.group(3)))] = (t.count(' b:'), t.count(' i:')); continue
            m = r_emit.match(s)
            if m: d['emit'][m.group(2)] = (int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6))); continue
            m = r_pipe.match(s)
            if m:
                t = m.group(5)
                if 'precache' in t: continue
                w = re.search(r'wait_us=(\d+)', t)
                d['pipes'].append((int(m.group(1)), int(m.group(2)), int(m.group(3)), 'async' in t, int(w.group(1)) if w else None, l)); continue
            m = r_skip.match(s)
            if m: d['skips'] += 1; d['skip_pairs'].add((m.group(3), m.group(4))); continue
            if r_held.match(s): d['held'] = True; continue
            m = r_flip.match(s)
            if m: d['flip'] = int(m.group(3)); continue
            if s.startswith('PipelinePrecache: saved'): d['rsave'] += 1
            if s.startswith('Vulkan pipeline cache: saved'): d['dsave'] += 1
        rows.append(d)
    # shaders translated after the entry
    P('  shaders translated after the entry (AvTrace: shader): stage hash translate_us compile_us perm | spec b/i | emit_us module_us | frame n | reg lines, type, first reg before entry?, lead_us = FirstUse - min Register, lead_last = FirstUse - last Register before it')
    nsh = 0
    for d in rows:
        for st, h, tr, co, pm, l in d['sh']:
            nsh += 1
            rg = reg.get(h, []); f = fu.get(h)
            lead = lead_last = None
            if rg and f:
                lead = f[1] - min(x[1] for x in rg)
                prev = [x[1] for x in rg if x[1] <= f[1]]
                lead_last = f[1] - max(prev) if prev else None
            sp = d['spec'].get((h, pm)); em = d['emit'].get(h)
            allsh.append(dict(tag=tag, st=st, h=h, tr=tr, co=co, pm=pm, sp=sp, nreg=len(rg), lead=lead, lead_last=lead_last,
                              regbefore=bool(rg) and min(x[0] for x in rg) < ent, n=d['n'], types=sorted(set(x[2] for x in rg)),
                              regsets=len(set(x[3] for x in rg))))
            P('    %s %s tr %d co %d perm %d | spec %s | emit %s | n %d | reg %d types %s distinct reg texts %d before-entry %s lead %s lead_last %s'
              % (st, h, tr, co, pm, sp, em, d['n'], len(rg), sorted(set(x[2] for x in rg)), len(set(x[3] for x in rg)),
                 bool(rg) and min(x[0] for x in rg) < ent, lead, lead_last))
    # bursts: maximal runs of groups with a skipped draw or a held flip (gap of <= 1 clean group joins)
    bursts = []; curb = None; gap = 0
    for i, d in enumerate(rows):
        hit = d['skips'] > 0 or d['held']
        if hit:
            if curb is None: curb = [i, i]
            else: curb[1] = i
            gap = 0
        elif curb is not None:
            gap += 1
            if gap > 1: bursts.append(curb); curb = None
    if curb is not None: bursts.append(curb)
    P('  bursts (runs of frames with a skipped draw or a logged held flip; a gap of 1 clean frame joins):')
    for a, b in bursts:
        fr = rows[a:b + 1]
        hit = [d for d in fr if d['skips'] > 0 or d['held']]
        # translation of the burst: shader lines of the frames a .. b (GuestGpu thread, wall)
        tr = sum(x[2] + x[3] for d in fr for x in d['sh'])
        trn = sum(len(d['sh']) for d in fr)
        # creations: async pipeline lines ending in frames a .. b+1
        fr2 = rows[a:min(b + 2, len(rows))]
        asy = [p for d in fr2 for p in d['pipes'] if p[3]]
        syn = [p for d in fr2 for p in d['pipes'] if not p[3]]
        cs = sum(p[2] for p in asy)
        lat = [p[2] + (p[4] or 0) for p in asy]
        big = [p for p in asy if p[2] > WAIT_US]
        wall_hit = sum(d['dt'] for d in hit)
        wall_all = sum(d['dt'] for d in fr)
        # model: translation moved off the frame, creations unchanged and still queued at first use:
        #   frames lost >= ceil(max latency / 16 667) when any creation exceeds the 4 ms wait (lower bound 1 frame)
        mx = max(lat) if lat else 0
        model = int(math.ceil(mx / float(FRAME_US))) if big else 0
        model_lo = 1 if big else 0
        pairs = set()
        for d in fr: pairs |= d['skip_pairs']
        tot['series'] += 1; tot['obs'] += len(hit); tot['model'] += model; tot['model_lo'] += model_lo
        tot['tr_wall'] += tr; tot['cr_sum'] += cs; tot['hold_wall'] += wall_hit
        P('    n %d..%d: frames with skip/held %d (skip lines %d, distinct vs/ps pairs %d), wall of those frames %d us (all frames of the run %d us); '
          'translation+module wall %d us (%d shaders); async creations %d sum_us %d max_us %d max(wait+us) %d, of them us > %d: %d; sync %d sum_us %d; '
          'recipe saves %d driver saves %d; model "translation removed, creation as is": frames lost %d (lower bound %d)'
          % (fr[0]['n'], fr[-1]['n'], len(hit), sum(d['skips'] for d in fr), len(pairs), wall_hit, wall_all, tr, trn, len(asy), cs,
             max([p[2] for p in asy] or [0]), mx, WAIT_US, len(big), len(syn), sum(p[2] for p in syn),
             sum(d['rsave'] for d in fr2), sum(d['dsave'] for d in fr2), model, model_lo))
    # frames >= 100 ms after the entry
    P('  frames dt >= 100 ms after the entry: %s' % [(d['n'], d['dt'], 'held' if d['held'] else '', d['skips']) for d in rows if d['dt'] >= 100000])
    P('  shaders translated after the entry: %d; async creations after the entry %d (sum_us %d), with us > %d: %d'
      % (nsh, sum(1 for d in rows for p in d['pipes'] if p[3]), sum(p[2] for d in rows for p in d['pipes'] if p[3]), WAIT_US,
         sum(1 for d in rows for p in d['pipes'] if p[3] and p[2] > WAIT_US)))
P('== totals over the six arms (t2_cs0 is a repeat of hero_kratos): bursts %d, frames with skip/held observed %d, model frames %d (lower bound %d), '
  'translation wall %d us, creation sum %d us, wall of skip/held frames %d us' % (tot['series'], tot['obs'], tot['model'], tot['model_lo'],
  tot['tr_wall'], tot['cr_sum'], tot['hold_wall']))
five = [x for x in allsh if x['tag'] != 't2_cs0']
P('== shaders translated after the entry, five counted arms: %d' % len(five))
for st in sorted(set(x['st'] for x in five)):
    xs = [x for x in five if x['st'] == st]
    P('  %s: %d; perm == 1: %d, perm > 1: %d; with a non-empty resource specialization (b or i entries): %d; registered (ShaderRegister with the same hash): %d; '
      'registered before the entry line: %d; lead known %d: min %s median %s max %s; lead < translate+compile: %d'
      % (st, len(xs), sum(1 for x in xs if x['pm'] == 1), sum(1 for x in xs if x['pm'] > 1),
         sum(1 for x in xs if x['sp'] and (x['sp'][0] or x['sp'][1])), sum(1 for x in xs if x['nreg']),
         sum(1 for x in xs if x['regbefore']), sum(1 for x in xs if x['lead'] is not None),
         min([x['lead'] for x in xs if x['lead'] is not None] or [None]),
         statistics.median([x['lead'] for x in xs if x['lead'] is not None]) if any(x['lead'] is not None for x in xs) else None,
         max([x['lead'] for x in xs if x['lead'] is not None] or [None]),
         sum(1 for x in xs if x['lead'] is not None and x['lead'] < x['tr'] + x['co'])))
open(D + 'split_s14a.out.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out))
