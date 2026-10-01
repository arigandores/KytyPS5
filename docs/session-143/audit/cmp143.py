# cmp143.py - Session Auditor, s143 step 3 (HPP-300): own recount (aud143.json) against the scorer outputs
# runs143/<tag>.score.json, field by field; provenance timeline of the recipe counts. No code shared with sc143.py.
import json, re, sys
A = {r['tag']: r for r in json.load(open('C:/kyty/s143/step3/aud143.json'))}
ROOT = 'C:/kyty/s143'
tags = []
for i in range(1, 11):
    tags += ['v143_%02d' % i, 'w143_%02d' % i]
diffs = 0
fields = 0
def cmpf(tag, name, mine, theirs):
    global diffs, fields
    fields += 1
    if mine != theirs:
        diffs += 1
        print('DIFF %s %s: mine %r scorer %r' % (tag, name, mine, theirs))
def prio(lines):
    vals = []
    for pos, t in lines:
        m = re.findall('([0-9]+) ?us', t) + re.findall('us=([0-9]+)', t)
        if m:
            vals.append(max(int(x) for x in m))
    return vals
shown = False
for t in tags:
    a = A[t]
    L = a['log']
    S = json.load(open('%s/runs143/%s.score.json' % (ROOT, t)))
    D = S['derive']
    c = L.get('count', {})
    es = a['emu_stdout']
    cmpf(t, 'log sha256 = score log_sha', L['sha256'], S['log_sha'])
    cmpf(t, 'log sha256 = times_log_sha', L['sha256'], S['times_log_sha'])
    cmpf(t, 'rows_total', L.get('rows_total'), S['rows_total'])
    cmpf(t, 'torn', L.get('torn'), S['torn'])
    cmpf(t, 'entered', L.get('entry_pos') is not None, D['entered'])
    cmpf(t, 'first', L.get('first'), D['first'])
    cmpf(t, 'window', L.get('window', 0), D['window'])
    cmpf(t, 'hold', L.get('hold', 0), D['hold'])
    cmpf(t, 'frames_after_first', L.get('frames_after_first', 0), D['frames_after_first'])
    cmpf(t, 'dt_after_entry_us', L.get('sum_dt_after_entry_us', 0), D['dt_after_entry_us'])
    cmpf(t, 'dt_after_first_us', L.get('sum_dt_after_first_us', 0), D['dt_after_first_us'])
    cmpf(t, 'n_gaps', L.get('n_gaps', 0), D['n_gaps'])
    cmpf(t, 'dt_median_us', L.get('dt_median_us'), D['dt_median_us'])
    cmpf(t, 'dt_max_us', L.get('dt_max_us'), D['dt_max_us'])
    cmpf(t, 'k2', L.get('k2', []), D['k2'])
    cmpf(t, 'k3w', L.get('k3w', []), D['k3w'])
    cmpf(t, 'k3h', L.get('k3h', []), D['k3h'])
    k2s = [x[:2] for x in D['k2_120']]
    if L.get('k2_120_incl', []) != k2s and L.get('k2_120_excl', []) != k2s:
        cmpf(t, 'k2_120 (neither reading)', [L.get('k2_120_excl'), L.get('k2_120_incl')], k2s)
    else:
        fields += 1
        if L.get('k2_120_incl', []) != L.get('k2_120_excl', []):
            print('NOTE %s k2_120 readings differ: excl %r incl %r scorer %r' % (t, L.get('k2_120_excl'), L.get('k2_120_incl'), k2s))
    k3s = D['k3h120']
    if L.get('k3h120_incl', []) != k3s and L.get('k3h120_excl', []) != k3s:
        cmpf(t, 'k3h120 (neither reading)', [L.get('k3h120_excl'), L.get('k3h120_incl')], k3s)
    else:
        fields += 1
        if L.get('k3h120_incl', []) != L.get('k3h120_excl', []):
            print('NOTE %s k3h120 readings differ: excl %r incl %r scorer %r' % (t, L.get('k3h120_excl'), L.get('k3h120_incl'), k3s))
    cmpf(t, 'cut120_pos', L.get('cut120_pos'), D['cut120_pos'])
    cmpf(t, 'skip lines', c.get('AsyncPipelines: skipped draw', 0), S['skip']['lines'])
    cmpf(t, 'skip frames', L.get('skip_frames', 0), S['skip']['frames'])
    pl = L.get('raw', {}).get('PriorityStall:', [])
    pv = prio(pl)
    if pl and not shown:
        print('SAMPLE PriorityStall line:', pl[0][1][:300])
        shown = True
    cmpf(t, 'prio lines', L.get('raw', {}).get('PriorityStall:#n', 0), S['prio']['lines'])
    cmpf(t, 'prio over 50000', sum(1 for v in pv if v > 50000), S['prio']['over'])
    cmpf(t, 'prio max', max(pv) if pv else 0, S['prio']['max'])
    cmpf(t, 'bvh', L.get('raw', {}).get('BvhLoopCapTrip:#n', 0), S['bvh'])
    vke_log = c.get('[Vulkan][E]', 0)
    vke_out = (es.get('count') or {}).get('[Vulkan][E]', 0) if es.get('present') else 0
    cmpf(t, 'vke (log + emulator stdout)', vke_log + vke_out, S['vke'])
    cmpf(t, 'ops total', c.get('opcode is not implemented', 0), S['ops']['total'])
    cmpf(t, 'stubs', c.get('=== Stubbed function', 0), len(S['stubs']))
    vany = c.get('[Vulkan][', 0) + ((es.get('count') or {}).get('[Vulkan][', 0) if es.get('present') else 0)
    cmpf(t, 'val vkany (log + stdout)', vany, S['val']['vkany'])
    cmpf(t, 'val valfeat (log)', c.get('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features', 0), S['val']['valfeat'])
    cmpf(t, 'val noval (log)', c.get('no validation layer:', 0), S['val']['noval'])
    mm = sorted([m[1] for m in L.get('marks', [])] + [m[1] for m in (es.get('marks') or [])])
    cmpf(t, 'death markers (log + stdout kinds)', mm, sorted(m['kind'] for m in S['marks']))
    mine_out = 'NOT_ENTERED' if L.get('entry_pos') is None else ('K2' if L.get('k2') else 'HOLDS')
    their = S['outcome']
    cmpf(t, 'outcome class', mine_out, 'HOLDS' if their.startswith('HOLDS') else their)
    print('ROW %s rows %s first %s shown %.1f s / %s frames K2 %s K3w %d K3h %d skipF %s prio %d/%s bvh %s vkE %d+%d GuestOut %s cs %s marks %s outcome %s|%s' % (
        t, L.get('rows_total'), L.get('first'), L.get('sum_dt_after_first_us', 0) / 1e6, L.get('frames_after_first', 0),
        L.get('k2', []), len(L.get('k3w', [])), len(L.get('k3h', [])), L.get('skip_frames'),
        sum(1 for v in pv if v > 50000), max(pv) if pv else 0, L.get('raw', {}).get('BvhLoopCapTrip:#n', 0), vke_log, vke_out,
        c.get('GuestOut'), c.get('vkCreateComputePipelines begin'), mm, S['outcome'], S.get('outcome120')))
print('FIELDS compared %d over %d logs; DIFFS %d' % (fields, len(tags), diffs))
for i in range(1, 11):
    v = A['v143_%02d' % i]['log']; wl = A['w143_%02d' % i]['log']
    vfail = []; wfail = []
    if v.get('entry_pos') is None: vfail.append('V not entered')
    if v.get('sum_dt_after_first_us', 0) < 300000000: vfail.append('V shown < 300 s')
    if v.get('k2'): vfail.append('V frame >= 1 s %r' % (v['k2'],))
    if v.get('n_marks'): vfail.append('V death markers')
    if v.get('n_gaps'): vfail.append('V n gaps')
    if wl.get('entry_pos') is None: wfail.append('W not entered')
    if wl.get('count', {}).get('[Vulkan][E]', 0): wfail.append('W [Vulkan][E] %d in the log' % wl['count']['[Vulkan][E]'])
    if wl.get('n_marks'): wfail.append('W stop markers %d' % wl['n_marks'])
    if wl.get('sum_dt_after_first_us', 0) < 300000000: wfail.append('W shown < 300 s')
    print('SCENE_OK own %s v/w143_%02d: %s (V: %s; W: %s)' % (A['v143_%02d' % i]['level'], i,
          'NO' if (vfail or wfail) else 'PENDING (video, sheet)', '; '.join(vfail) or 'log rows pass', '; '.join(wfail) or 'log rows pass'))
for ln in open(ROOT + '/step2/summary143.txt', encoding='utf-8', errors='replace').read().splitlines():
    if ln.startswith('SCENE_OK') or ln.startswith('FORM ') or ln.startswith('CENSUS') or ln.startswith('STOP RULE') or ln.startswith('K2 ON THE HOLD'):
        print('SUMMARY| ' + ln[:230])
order = ['v142', 'w142'] + ['c142_%02d' % i for i in range(1, 11)] + tags
spans = []
for t in order:
    L = A[t]['log']
    raw = L.get('raw', {})
    pp = [x[1] for x in raw.get('PipelinePrecache:', [])]
    st = [int(re.search('PipelinePrecache: ([0-9]+) recipes ->', x).group(1)) for x in pp if ' recipes ->' in x]
    sv = [(int(re.search('saved ([0-9]+) recipes', x).group(1)), int(re.search('recipes [(]([0-9]+) bytes', x).group(1))) for x in pp if 'saved ' in x]
    ld = [int(re.search('loaded ([0-9]+) bytes', x[1]).group(1)) for x in raw.get('Vulkan pipeline cache:', []) if 'loaded ' in x[1]]
    allc = any('all pipelines created' in x for x in pp)
    c = L.get('count', {})
    print('TIMELINE %s sha %s starts %s start_recipes %s saved %s all_created %s drv_loaded %s vkE %s cs_begin %s GuestOut %s' % (
        t, L['sha256'][:12], [x[1] for x in L.get('starts', [])], st, sv, allc, ld, c.get('[Vulkan][E]'),
        c.get('vkCreateComputePipelines begin'), c.get('GuestOut')))
    spans.append((t, st[0] if st else None, sv[-1][0] if sv else (st[0] if st else None), sv))
R = json.load(open('C:/kyty/s143/step3/recipes143.json'))
for f in R.get('cur', {}).get('flagged', []):
    k = f['index']
    for t, s0, s1, sv in spans:
        if s0 is not None and s1 is not None and s0 <= k < s1:
            fs = [x for x in sv if x[0] > k]
            print('FLAGGED recipe index %d (0-based) bytes [%d, %d) of cur -> added in run %s (start %d, end %d); first save holding it: %s' % (
                k, f['begin'], f['end'], t, s0, s1, fs[:1]))
print('ALL DONE')
