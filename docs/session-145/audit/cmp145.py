# cmp145.py - Session Auditor, s145 step 3 (HPP-353): own recount (aud145.json) against the scorer outputs
# runs145/<tag>.score.json (33 made tags) and C:/kyty/s144/runs144/v144_09.score.json (the V of the cross-session pair),
# field by field; own SCENE_OK reading per pair (17 levels); the W form of items 254 (e) and 295 (b)(1)-(4); window lines;
# forms B5 / B5a / B33 of the cold entries. No code shared with sc145.py / gate145.py.
import json, re, os

A = {(r['root'][-4:], r['tag']): r for r in json.load(open('C:/kyty/s145/step3/aud145.json'))}
S145 = 'C:/kyty/s145'
S144 = 'C:/kyty/s144'
LV = ['small_pot_lava', 'spin_drill_natural_cave', 'enemy_taco', 'jack_in_the_box', 'final_shooting', 'picup_light', 'enemy_snake',
      'light_gadget_graveyard', 'shuriken_ninja_castle', 'final_stage', 'mini_rocket_chain', 'enemy_chameleon', 'bonus_path_maker_mix',
      'enemy_bird', 'cymbal_party_land', 'enemy_final']
order = ['w145_00', 'w145_01']
for i in range(2, 18):
    order += ['v145_%02d' % i, 'w145_%02d' % i]
made = [t for t in order if os.path.isfile('%s/runs145/%s.score.json' % (S145, t))]
notmade = [t for t in order if t not in made]
diffs = 0
fields = 0


def cmpf(tag, name, mine, theirs):
    global diffs, fields
    fields += 1
    if mine != theirs:
        diffs += 1
        print('DIFF %s %s: mine %r scorer %r' % (tag, name, mine, theirs))


def kinds_sum(a):
    L = a['log']
    es = a['emu_stdout']
    out = dict(L.get('win_kinds') or {})
    if es.get('present'):
        for k, v in es['win_kinds'].items():
            out[k] = out.get(k, 0) + v
    return out


def form4(env):
    return 'W form: limit=%s filter=%s' % (env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'), env.get('VK_LAYER_MESSAGE_ID_FILTER', 'none'))


def compare(key, t, score_path, new):
    global fields
    a = A[key]
    L = a['log']
    S = json.load(open(score_path, encoding='utf-8'))
    D = S['derive']
    c = L.get('count', {})
    es = a['emu_stdout']
    esc = (es.get('count') or {}) if es.get('present') else {}
    cmpf(t, 'log sha256 = score log_sha', L['sha256'], S['log_sha'])
    cmpf(t, 'log sha256 = times_log_sha', L['sha256'], S['times_log_sha'])
    cmpf(t, 'rows_total', L.get('rows_total'), S['rows_total'])
    cmpf(t, 'torn', L.get('torn'), S['torn'])
    cmpf(t, 'entered', L.get('entry_pos') is not None, D['entered'])
    cmpf(t, 'entry_pos', L.get('entry_pos'), D.get('entry_pos'))
    cmpf(t, 'first', L.get('first'), D.get('first'))
    cmpf(t, 'window', L.get('window', 0), D.get('window', 0))
    cmpf(t, 'hold', L.get('hold', 0), D.get('hold', 0))
    cmpf(t, 'frames_after_first', L.get('frames_after_first', 0), D.get('frames_after_first', 0))
    cmpf(t, 'dt_after_entry_us', L.get('sum_dt_after_entry_us', 0), D.get('dt_after_entry_us', 0))
    cmpf(t, 'dt_after_first_us', L.get('sum_dt_after_first_us', 0), D.get('dt_after_first_us', 0))
    cmpf(t, 'n_gaps', L.get('n_gaps', 0), D.get('n_gaps', 0))
    md, sd = L.get('dt_median_us'), D.get('dt_median_us')
    if md is not None and sd is not None and md != sd and L.get('dt_median_high_us') == sd:
        fields += 1
        print('NOTE %s dt_median_us form: mine (mean of the two middle values) %r, own upper median %r = scorer %r' % (t, md, L.get('dt_median_high_us'), sd))
    else:
        cmpf(t, 'dt_median_us', md, sd)
    cmpf(t, 'dt_max_us', L.get('dt_max_us'), D.get('dt_max_us'))
    cmpf(t, 'k2', L.get('k2', []) or [], D.get('k2', []))
    cmpf(t, 'k3w', L.get('k3w', []), D.get('k3w', []))
    cmpf(t, 'k3h', L.get('k3h', []), D.get('k3h', []))
    k2s = [x[:2] for x in D.get('k2_120', [])]
    if L.get('k2_120_incl', []) != k2s and L.get('k2_120_excl', []) != k2s:
        cmpf(t, 'k2_120 (neither reading)', [L.get('k2_120_excl'), L.get('k2_120_incl')], k2s)
    else:
        fields += 1
    k3s = D.get('k3h120', [])
    if L.get('k3h120_incl', []) != k3s and L.get('k3h120_excl', []) != k3s:
        cmpf(t, 'k3h120 (neither reading)', [len(L.get('k3h120_excl', [])), len(L.get('k3h120_incl', []))], len(k3s))
    else:
        fields += 1
    cmpf(t, 'cut120_pos', L.get('cut120_pos'), D.get('cut120_pos'))
    cmpf(t, 'scene changes', [x[1] for x in L.get('scene_changes', [])], [x[0] if isinstance(x, list) else x for x in D.get('other_starts', [])])
    vx = D.get('vx') or {}
    if L.get('first') is not None:
        cmpf(t, 'vx frames_after_first', (L.get('vx') or {}).get('frames'), vx.get('frames_after_first'))
        cmpf(t, 'vx dt_after_first_us', (L.get('vx') or {}).get('dt_us'), vx.get('dt_after_first_us'))
    else:
        fields += 2
    sk = L.get('skip', {})
    cmpf(t, 'skip lines', sk.get('lines', 0), S['skip']['lines'])
    cmpf(t, 'skip frames (distinct frame= ids)', sk.get('frames_by_id', 0), S['skip']['frames'])
    pr = L.get('prio', {})
    cmpf(t, 'prio lines', pr.get('lines', 0), S['prio']['lines'])
    cmpf(t, 'prio over 50000', pr.get('over', 0), S['prio']['over'])
    cmpf(t, 'prio max', pr.get('max', 0), S['prio']['max'])
    cmpf(t, 'bvh', L.get('raw', {}).get('BvhLoopCapTrip:#n', 0), S['bvh'])
    vke_log = c.get('[Vulkan][E]', 0)
    vke_out = esc.get('[Vulkan][E]', 0)
    cmpf(t, 'vke (log + emulator stdout)', vke_log + vke_out, S['vke'])
    cmpf(t, 'ops total', c.get('opcode is not implemented', 0), S['ops']['total'])
    cmpf(t, 'stubs', c.get('=== Stubbed function', 0), len(S['stubs']))
    cmpf(t, 'val vkany (log + stdout)', c.get('[Vulkan][', 0) + esc.get('[Vulkan][', 0), S['val']['vkany'])
    cmpf(t, 'val valfeat (log)', c.get('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features', 0), S['val']['valfeat'])
    cmpf(t, 'val noval (log)', c.get('no validation layer:', 0), S['val']['noval'])
    mm = sorted([m[1] for m in L.get('marks', [])] + [m[1] for m in (es.get('marks') or [])])
    cmpf(t, 'death markers (log + stdout kinds)', mm, sorted(m['kind'] for m in S['marks']))
    pc = S.get('precache') or {}
    cmpf(t, 'precache log ("N recipes ->" lines)', L.get('recipes_arrow_lines', 0), pc.get('log'))
    cmpf(t, 'precache stdout ("N recipes ->" lines)', es.get('recipes_arrow_lines', 0) if es.get('present') else 0, pc.get('stdout'))
    cmpf(t, 'precache any ("PipelinePrecache:" lines, log + stdout)', L.get('raw', {}).get('PipelinePrecache:#n', 0) + esc.get('PipelinePrecache:', 0), pc.get('any'))
    cmpf(t, 'first GuestOut position', L.get('first_pos', {}).get('GuestOut'), S.get('guestout'))
    js = a['json']
    att = (js.get('attempts') or [{}])[0] if isinstance(js, dict) else {}
    cmpf(t, 'json attempt level', att.get('level'), S.get('att_level'))
    cmpf(t, 'json guest_args', js.get('guest_args') if isinstance(js, dict) else None, S.get('guest_args'))
    cmpf(t, 'json hold_s', att.get('hold_s'), S.get('hold_s'))
    cmpf(t, 'json hold_exit', att.get('hold_exit'), S.get('hold_exit'))
    cmpf(t, 'json attempt outcome', att.get('outcome'), S.get('attempt_outcome'))
    cmpf(t, 'json ft_tail', att.get('ft_tail'), S.get('ft_tail'))
    isw = t.startswith('w')
    if new:
        # rows of items 273 (k)(2)-(3) and 295 (b), (g)
        cmpf(t, 'layer limit lines (log + stdout)', c.get('last time reporting it', 0) + esc.get('last time reporting it', 0), S['limit'])
        w2 = c.get('[Vulkan][W][2]', 0) + c.get('[Vulkan][E][2]', 0) + esc.get('[Vulkan][W][2]', 0) + esc.get('[Vulkan][E][2]', 0)
        cmpf(t, 'validation-layer lines [W][2] + [E][2] (log + stdout) = vk2', w2, S['vk2'])
        cmpf(t, 'F6 text lines ("and this write is unused", log + stdout) = f6', c.get('and this write is unused', 0) + esc.get('and this write is unused', 0), S['f6'])
        held_m = L.get('size') is not None and not mm and att.get('hold_exit') is None and att.get('outcome') == 'ok' and not (a['es_stdout'].get('ended') or 0)
        cmpf(t, 'held', held_m, S['held'][0])
        if isw:
            cmpf(t, 'layer_end_us (item 295 (b)(3))', L.get('layer_end_us'), S['layer_end'])
            cmpf(t, 'form line (item 295 (b)(4))', form4(js.get('env', {})), S['form4'][1])
            cmpf(t, 'form line passes', form4(js.get('env', {})) == 'W form: limit=100000000 filter=none' and 'VK_LAYER_MESSAGE_ID_FILTER' not in js.get('env', {}), S['form4'][0])
        else:
            fields += 3
        ks = kinds_sum(a)
        cmpf(t, 'window lines by kind (log + emulator stdout)', ks, S['winall'])
        rec = c.get('Recovering Vulkan swapchain', 0) + esc.get('Recovering Vulkan swapchain', 0)
        cmpf(t, 'window event (minimized or Recovering)', bool(ks.get('minimized') or rec), S['winev'])
        mine_near = [[x[0], x[1], x[2], x[3], x[4] is not None] for x in (L.get('winnear') or [])]
        their_near = [[x[0], x[1], x[2], x[3], x[4] is not None] for x in (S.get('winnear') or [])]
        cmpf(t, 'K2 / K3 frames with the nearest window line (present or none)', mine_near, their_near)
    if L.get('entry_pos') is None:
        mine_out = 'NOT_ENTERED'
    elif L.get('n_marks') or (es.get('marks') if es.get('present') else None):
        mine_out = 'STOPPED'
    elif (L.get('k2') and not isw):
        mine_out = 'K2'
    else:
        mine_out = 'HOLDS'
    their = S['outcome']
    cmpf(t, 'outcome class', mine_out, 'HOLDS' if their.startswith('HOLDS') else ('STOPPED' if their == 'VALIDATION_STOP' else their))
    print('ROW %s %s rows %s first %s shown %.1f s / %s frames K2 %s K3w %d K3h %d skip %s/%s(id) prio %d/%s bvh %s vkE %d+%d '
          'recipes-> %s/%s limit %s [W][2]+[E][2] %s layer_end_us %s winkinds %s marks %s hold_s %s hold_exit %s outcome %s|%s' % (
              t, a['level'], L.get('rows_total'), L.get('first'), L.get('sum_dt_after_first_us', 0) / 1e6, L.get('frames_after_first', 0),
              L.get('k2', []), len(L.get('k3w', [])), len(L.get('k3h', [])), sk.get('lines'), sk.get('frames_by_id'),
              pr.get('over', 0), pr.get('max', 0), L.get('raw', {}).get('BvhLoopCapTrip:#n', 0), vke_log, vke_out,
              L.get('recipes_arrow_lines'), es.get('recipes_arrow_lines') if es.get('present') else None,
              c.get('last time reporting it', 0), c.get('[Vulkan][W][2]', 0) + c.get('[Vulkan][E][2]', 0), L.get('layer_end_us'),
              {k: v for k, v in kinds_sum(a).items() if v}, mm, att.get('hold_s'), att.get('hold_exit'), S['outcome'], S.get('outcome120')))
    return S


SC = {}
for t in made:
    SC[t] = compare(('s145', t), t, '%s/runs145/%s.score.json' % (S145, t), True)
print('FIELDS s145 compared %d over %d logs; DIFFS so far %d; not made (no score json): %s' % (fields, len(made), diffs, notmade))
SC['v144_09'] = compare(('s144', 'v144_09'), 'v144_09', '%s/runs144/v144_09.score.json' % S144, False)
print('FIELDS compared %d over %d logs (%d of s145 + v144_09 of s144); DIFFS %d' % (fields, len(made) + 1, len(made), diffs))

# not made tags: what is on the disk
for t in notmade:
    a = A[('s145', t)]
    print('NOTMADE %s: log %s; json %s; attempt file %s; emulator stdout %s; enter_scene stdout %s' % (
        t, a['log'].get('error', 'present'), 'error' if 'error' in a['json'] else 'present', a['attempt_file'],
        a['emu_stdout'].get('present'), a['es_stdout'].get('present')))

# the form of every made tag: env of the json, command line, lines of the log and of the emulator stdout
okform = True
for t in made:
    a = A[('s145', t)]
    L = a['log']
    es = a['emu_stdout']
    esc = (es.get('count') or {}) if es.get('present') else {}
    env = a['json'].get('env', {})
    cl = a['json'].get('cmdline', [])
    val = [cl[k + 1] for k, x in enumerate(cl[:-1]) if x == '--vulkan-validation']
    seed = (L.get('raw', {}).get('ShaderSeed:#n', 0), esc.get('ShaderSeed:', 0))
    pp = (L.get('raw', {}).get('PipelinePrecache:#n', 0), esc.get('PipelinePrecache:', 0))
    c = L['count']
    if t.startswith('w'):
        good = env.get('KYTY_PIPELINE_PRECACHE') == '0' and val[-1:] == ['true'] and L.get('recipes_arrow_lines') == 0 and seed == (0, 0) and pp == (0, 0) \
            and 'KYTY_REC' not in env and c.get('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features', 0) >= 1 \
            and env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT') == '100000000' and 'VK_LAYER_MESSAGE_ID_FILTER' not in env \
            and c.get('last time reporting it', 0) == 0 and (c.get('[Vulkan][W][2]', 0) + c.get('[Vulkan][E][2]', 0)) >= 1 \
            and L.get('layer_end_us') is not None and L['layer_end_us'] <= 10000000
    else:
        good = 'KYTY_PIPELINE_PRECACHE' not in env and val[-1:] == ['false'] and L.get('recipes_arrow_lines', 0) >= 1 and seed[0] >= 1 and 'KYTY_REC' in env \
            and 'VK_LAYER_MESSAGE_ID_FILTER' not in env and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT' not in env
    okform &= good
    print('FORM %s env KYTY_PIPELINE_PRECACHE=%r limit=%r filter key %s validation args %s KYTY_REC %s; "N recipes ->" log %s; ShaderSeed: log/stdout %s; '
          'PipelinePrecache: log/stdout %s; valfeat %s; limit lines %s; [W][2]+[E][2] %s; [W][1] %s; layer_end_us %s; binary %s; prereg %s; attempts %d -> %s' % (
              t, env.get('KYTY_PIPELINE_PRECACHE'), env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'), 'VK_LAYER_MESSAGE_ID_FILTER' in env, val, 'KYTY_REC' in env,
              L.get('recipes_arrow_lines'), seed, pp, c.get('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features'),
              c.get('last time reporting it'), c.get('[Vulkan][W][2]', 0) + c.get('[Vulkan][E][2]', 0), c.get('[Vulkan][W][1]'), L.get('layer_end_us'),
              str(a['json'].get('binary_sha256'))[:8], str((a['json'].get('prereg') or {}).get('sha256'))[:8], len(a['json'].get('attempts') or []),
              'ok' if good else 'VIOLATED'))
print('FORM own reading over %d made tags (items 254 (e), 295 (b)(1)-(4)): %s' % (len(made), 'ALL OK' if okform else 'VIOLATIONS'))

# own SCENE_OK reading per pair (rows that the log, the json and the attempt decide; video rows - vid145.py; sheet row - the close)
pairs = [('s144', 'v144_09', 's145', 'w145_01')] + [('s145', 'v145_%02d' % i, 's145', 'w145_%02d' % i) for i in range(2, 18)]
own = {}
for vr, vt, wr, wt in pairs:
    va, wa = A[(vr, vt)], A[(wr, wt)]
    v, w = va['log'], wa['log']
    vj = (va['json'].get('attempts') or [{}])[0] if 'error' not in va['json'] else {}
    wj = (wa['json'].get('attempts') or [{}])[0] if 'error' not in wa['json'] else {}
    ves, wes = va['emu_stdout'], wa['emu_stdout']
    vf, wf = [], []
    if 'error' in v:
        vf.append('V no log')
    else:
        if va['json'].get('guest_args') != '-lvl ' + va['level'] or vj.get('level') != va['level']: vf.append('V level / guest args mismatch')
        if v.get('entry_pos') is None: vf.append('V not entered')
        if v.get('first') is None: vf.append('V no first scene frame')
        if v.get('scene_changes'): vf.append('V scene change')
        if not (vj.get('outcome') == 'ok' and (vj.get('hold_s') or 0) >= 330 and vj.get('hold_exit') is None): vf.append('V attempt %r / hold_s %r / hold_exit %r' % (vj.get('outcome'), vj.get('hold_s'), vj.get('hold_exit')))
        if v.get('n_marks') or (ves.get('marks') if ves.get('present') else None): vf.append('V death markers')
        if v.get('k2'): vf.append('V frame >= 1 s %r' % (v['k2'],))
        if v.get('n_gaps'): vf.append('V n gaps')
        if v.get('sum_dt_after_first_us', 0) < 300000000: vf.append('V shown < 300 s')
        if v.get('frames_after_first', 0) < 3000: vf.append('V < 3000 frames')
        if (v.get('win_kinds') or {}).get('minimized') or v['count'].get('Recovering Vulkan swapchain'): vf.append('V window event')
    if 'error' in w:
        wf.append('W no log (tag not made / aborted)')
    else:
        wenv = wa['json'].get('env', {})
        wc = w['count']
        if wa['json'].get('guest_args') != '-lvl ' + wa['level'] or wj.get('level') != wa['level'] or va['level'] != wa['level']: wf.append('W level / guest args mismatch')
        if w.get('entry_pos') is None: wf.append('W not entered')
        if w.get('scene_changes'): wf.append('W scene change')
        nm = (w.get('n_marks') or 0) + (len(wes.get('marks') or []) if wes.get('present') else 0)
        if nm or wj.get('hold_exit') is not None or wj.get('outcome') != 'ok': wf.append('W death markers %d / hold_exit %r / attempt %r' % (nm, wj.get('hold_exit'), wj.get('outcome')))
        ve = wc.get('[Vulkan][E]', 0) + ((wes.get('count') or {}).get('[Vulkan][E]', 0) if wes.get('present') else 0)
        if ve: wf.append('W [Vulkan][E] %d' % ve)
        if not (wj.get('ft_tail') or 0) > 0: wf.append('W ft_tail %r' % wj.get('ft_tail'))
        if not ((wj.get('hold_s') or 0) >= 300): wf.append('W hold_s %r' % wj.get('hold_s'))
        if wenv.get('KYTY_PIPELINE_PRECACHE') != '0' or w.get('recipes_arrow_lines'): wf.append('W form 254 (e)')
        if wc.get('last time reporting it', 0): wf.append('W 295(b)(1) limit lines %d' % wc['last time reporting it'])
        if wc.get('[Vulkan][W][2]', 0) + wc.get('[Vulkan][E][2]', 0) < 1: wf.append('W 295(b)(2) no validation-layer line')
        if w.get('layer_end_us') is None or w['layer_end_us'] > 10000000: wf.append('W 295(b)(3) layer_end_us %r' % w.get('layer_end_us'))
        if form4(wenv) != 'W form: limit=100000000 filter=none' or 'VK_LAYER_MESSAGE_ID_FILTER' in wenv: wf.append('W 295(b)(4) %s' % form4(wenv))
        if (w.get('win_kinds') or {}).get('minimized') or wc.get('Recovering Vulkan swapchain'): wf.append('W window event')
    verdict = 'NO' if (vf or wf) else 'LOG ROWS PASS (video rows: vid145.py; sheet row: the close)'
    own[va['level']] = verdict
    print('SCENE_OK own %s %s/%s: %s (V: %s; W: %s)' % (va['level'], vt, wt, verdict, '; '.join(vf) or 'log rows pass', '; '.join(wf) or 'log rows pass'))
summ = open(S145 + '/step2/summary145.txt', encoding='utf-8', errors='replace').read().splitlines()
sm = {}
for ln in summ:
    m = re.match(r'SCENE_OK (\S+): (YES|NO|PENDING_SHEET)$', ln)
    if m:
        sm[m.group(1)] = m.group(2)
agree = sum(1 for k, v in own.items() if (v == 'NO') == (sm.get(k) == 'NO'))
print('SCENE_OK own against the summary: levels %d, NO in mine %d %s, NO in the summary %d %s, agreement on NO / not NO %d of %d' % (
    len(own), sum(1 for v in own.values() if v == 'NO'), [k for k, v in own.items() if v == 'NO'],
    sum(1 for v in sm.values() if v == 'NO'), [k for k, v in sm.items() if v == 'NO'], agree, len(own)))
for ln in summ:
    if re.match(r'(SCENE_OK LEVELS|FORM |FORMS |CENSUS|STOP RULE|K2 ON THE HOLD|CONTROL W|W FORM|WINDOW EVENTS|LAYER LIMIT|VIDEO CONTINUITY)', ln):
        print('SUMMARY| ' + ln[:900])

# forms of the 16 cold entries, own lists (letter: denominators 16; entered 15)
vt = ['v145_%02d' % i for i in range(2, 18)]
def lg(t): return A[('s145', t)]['log']
b5 = [t for t in vt if lg(t).get('k3w') or any(x[2] == 'entry' for x in (lg(t).get('k2') or []))]
b5a = [t for t in vt if lg(t).get('k2')]
b5a120 = [t for t in vt if lg(t).get('k2_120_incl')]
b33 = [t for t in vt if lg(t).get('k3h')]
b33_120 = [t for t in vt if lg(t).get('k3h120_incl')]
ent = [t for t in vt if lg(t).get('entry_pos') is not None]
print('FORMS own (cold first entries, 16 V; entered %d): B5 %d %s; B5a %d %s; B5a variant 120 s %d %s; B33 %d %s; B33 variant 120 s %d %s' % (
    len(ent), len(b5), b5, len(b5a), b5a, len(b5a120), b5a120, len(b33), b33, len(b33_120), b33_120))
first8, last8 = vt[:8], vt[8:]
print('FORMS own second reading: first 8 B5a %d B5 %d; last 8 B5a %d B5 %d' % (
    sum(1 for t in first8 if t in b5a), sum(1 for t in first8 if t in b5), sum(1 for t in last8 if t in b5a), sum(1 for t in last8 if t in b5)))
pre = ['v145_%02d' % i for i in range(2, 7)]
print('FORMS own over the V before the cache break by the letter (v145_02..06): B5a %d, B5a 120 s %d, B5 %d, B33 %d (120 s %d)' % (
    sum(1 for t in pre if t in b5a), sum(1 for t in pre if t in b5a120), sum(1 for t in pre if t in b5), sum(1 for t in pre if t in b33), sum(1 for t in pre if t in b33_120)))

# v145_06 (final_shooting): the entry lines of the log; the aborted w145_06 (reference, not data of W)
for key in (('s145', 'v145_06'), ('s145', 'abort_w145_06')):
    a = A[key]
    L = a['log']
    print('ENTRY %s sha %s: "Level has started:" lines %s; StartLevel lines %s; rows %s; death markers %s; [Vulkan][E] %s; [W][2] %s; window kinds %s' % (
        key[1], L['sha256'][:16], [(p, nm) for p, nm in L.get('starts', [])], [(x[0], x[1][-70:]) for x in L['raw'].get('StartLevel ', [])][:4],
        L.get('rows_total'), L.get('n_marks'), L['count'].get('[Vulkan][E]'), L['count'].get('[Vulkan][W][2]'), {k: v for k, v in (L.get('win_kinds') or {}).items() if v}))
a1 = A.get(('s145', 'v145_06_a1'))
if a1:
    print('COPY log_v145_06_a1.txt sha %s = log_v145_06.txt sha %s: %s' % (a1['log']['sha256'][:16], A[('s145', 'v145_06')]['log']['sha256'][:16], a1['log']['sha256'] == A[('s145', 'v145_06')]['log']['sha256']))

# every tag: K2 / K3 frames with a window line within 2 s (own), W frames >= 1 s (data, W is not judged by dt)
for t in made:
    L = lg(t)
    nn = [x for x in (L.get('winnear') or []) if x[4]]
    k2 = L.get('k2') or []
    if nn or (k2 and t.startswith('w')):
        print('WINNEAR %s: K2/K3 frames %d, with a window line within 2 s %d %s; frames >= 1 s %s' % (
            t, len(L.get('winnear') or []), len(nn), [(x[0], x[2], x[3], x[4][1][-28:], round(x[4][0] / 1e6, 3)) for x in nn[:3]], k2))
print('ALL DONE')
