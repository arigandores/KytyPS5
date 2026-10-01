# cmp144.py - Session Auditor, s144 step 3 (HPP-333): own recount (aud144.json) against the scorer outputs
# runs144/<tag>.score.json (33 tags) and runs143/<tag>.score.json (the eight V of the cross-session pairs), field by field;
# own SCENE_OK reading per pair; the W form; the window / swapchain chain of w144_09 and the census of "minimized" lines
# over the logs of s142-s144 (ROADMAP item 270 (g)(1), (2)). No code shared with sc144.py / gate144.py.
import json, re, sys

A = {(r['root'][-4:], r['tag']): r for r in json.load(open('C:/kyty/s144/step3/aud144.json'))}
S144 = 'C:/kyty/s144'
S143 = 'C:/kyty/s143'
W8 = [1, 2, 3, 4, 5, 6, 9, 10]      # v143_NN paired with w144_01..08
tags = ['w144_00'] + ['w144_%02d' % i for i in range(1, 9)]
for i in range(9, 21):
    tags += ['v144_%02d' % i, 'w144_%02d' % i]
diffs = 0
fields = 0


def cmpf(tag, name, mine, theirs):
    global diffs, fields
    fields += 1
    if mine != theirs:
        diffs += 1
        print('DIFF %s %s: mine %r scorer %r' % (tag, name, mine, theirs))


def compare(key, t, score_path, prof144):
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
    cmpf(t, 'first', L.get('first'), D['first'])
    cmpf(t, 'window', L.get('window', 0), D['window'])
    cmpf(t, 'hold', L.get('hold', 0), D['hold'])
    cmpf(t, 'frames_after_first', L.get('frames_after_first', 0), D['frames_after_first'])
    cmpf(t, 'dt_after_entry_us', L.get('sum_dt_after_entry_us', 0), D['dt_after_entry_us'])
    cmpf(t, 'dt_after_first_us', L.get('sum_dt_after_first_us', 0), D['dt_after_first_us'])
    cmpf(t, 'n_gaps', L.get('n_gaps', 0), D['n_gaps'])
    cmpf(t, 'dt_median_us', L.get('dt_median_us'), D['dt_median_us'])
    cmpf(t, 'dt_max_us', L.get('dt_max_us'), D['dt_max_us'])
    cmpf(t, 'k2', L.get('k2', []) or [], D['k2'])
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
            print('NOTE %s k3h120 readings differ (both lists hold the scorer list or one of them does)' % t)
    cmpf(t, 'cut120_pos', L.get('cut120_pos'), D['cut120_pos'])
    cmpf(t, 'scene changes', [x[1] for x in L.get('scene_changes', [])], [x[0] if isinstance(x, list) else x for x in D.get('other_starts', [])])
    vx = D.get('vx') or {}
    if L.get('first') is not None:
        cmpf(t, 'vx frames_after_first', (L.get('vx') or {}).get('frames'), vx.get('frames_after_first'))
        cmpf(t, 'vx dt_after_first_us', (L.get('vx') or {}).get('dt_us'), vx.get('dt_after_first_us'))
    else:
        fields += 2
    sk = L.get('skip', {})
    cmpf(t, 'skip lines', sk.get('lines', 0), S['skip']['lines'])
    if prof144:
        cmpf(t, 'skip frames (distinct frame= ids, D-7)', sk.get('frames_by_id', 0), S['skip']['frames'])
    else:
        fields += 1
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
    if S['marks']:
        lm = [m for m in S['marks'] if m.get('src') == 'log']
        cmpf(t, 'first death marker position in the log', L['marks'][0][0] if L.get('marks') else None, lm[0]['pos'] if lm else None)
    else:
        fields += 1
    if prof144:
        pc = S.get('precache') or {}
        cmpf(t, 'precache log ("N recipes ->" lines)', L.get('recipes_arrow_lines', 0), pc.get('log'))
        cmpf(t, 'precache stdout ("N recipes ->" lines)', es.get('recipes_arrow_lines', 0) if es.get('present') else 0, pc.get('stdout'))
        cmpf(t, 'precache any ("PipelinePrecache:" lines, log + stdout)', L.get('raw', {}).get('PipelinePrecache:#n', 0) + esc.get('PipelinePrecache:', 0), pc.get('any'))
        cmpf(t, 'first GuestOut position', L.get('first_pos', {}).get('GuestOut'), S.get('guestout'))
    else:
        fields += 4
    js = a['json']
    att = (js.get('attempts') or [{}])[0] if isinstance(js, dict) else {}
    cmpf(t, 'json attempt level', att.get('level'), S.get('att_level'))
    cmpf(t, 'json guest_args', js.get('guest_args') if isinstance(js, dict) else None, S.get('guest_args'))
    cmpf(t, 'json hold_s', att.get('hold_s'), S.get('hold_s'))
    cmpf(t, 'json hold_exit', att.get('hold_exit'), S.get('hold_exit'))
    cmpf(t, 'json attempt outcome', att.get('outcome'), S.get('attempt_outcome'))
    cmpf(t, 'json ft_tail', att.get('ft_tail'), S.get('ft_tail'))
    isw = t.startswith('w')
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
    print('ROW %s %s rows %s first %s shown %.1f s / %s frames K2 %s K3w %d K3h %d skip %s/%s(id)/%s(interval) prio %d/%s bvh %s vkE %d+%d '
          'recipes-> %s/%s ShaderSeed %s/%s PipelinePrecache: %s/%s marks %s hold_s %s hold_exit %s outcome %s|%s' % (
              t, a['level'], L.get('rows_total'), L.get('first'), L.get('sum_dt_after_first_us', 0) / 1e6, L.get('frames_after_first', 0),
              L.get('k2', []), len(L.get('k3w', [])), len(L.get('k3h', [])), sk.get('lines'), sk.get('frames_by_id'), sk.get('frames_by_interval'),
              pr.get('over', 0), pr.get('max', 0), L.get('raw', {}).get('BvhLoopCapTrip:#n', 0), vke_log, vke_out,
              L.get('recipes_arrow_lines'), es.get('recipes_arrow_lines') if es.get('present') else None,
              L.get('raw', {}).get('ShaderSeed:#n'), esc.get('ShaderSeed:'),
              L.get('raw', {}).get('PipelinePrecache:#n'), esc.get('PipelinePrecache:'),
              mm, att.get('hold_s'), att.get('hold_exit'), S['outcome'], S.get('outcome120')))
    return S


SC = {}
for t in tags:
    SC[t] = compare(('s144', t), t, '%s/runs144/%s.score.json' % (S144, t), True)
n144 = fields
print('FIELDS s144 compared %d over %d logs; DIFFS so far %d' % (fields, len(tags), diffs))
for i in W8:
    t = 'v143_%02d' % i
    SC[t] = compare(('s143', t), t, '%s/runs143/%s.score.json' % (S143, t), False)
print('FIELDS compared %d over %d logs (33 of s144 + 8 V of s143); DIFFS %d' % (fields, len(tags) + 8, diffs))

# the W form (item 254 (e), 266 (b)): env of the json, lines of the log and of the emulator stdout
okform = True
for t in tags:
    a = A[('s144', t)]
    L = a['log']
    es = a['emu_stdout']
    esc = (es.get('count') or {}) if es.get('present') else {}
    env = a['json'].get('env', {})
    cl = a['json'].get('cmdline', [])
    val = [cl[k + 1] for k, x in enumerate(cl[:-1]) if x == '--vulkan-validation']
    seed = (L.get('raw', {}).get('ShaderSeed:#n', 0), esc.get('ShaderSeed:', 0))
    pp = (L.get('raw', {}).get('PipelinePrecache:#n', 0), esc.get('PipelinePrecache:', 0))
    if t.startswith('w'):
        good = env.get('KYTY_PIPELINE_PRECACHE') == '0' and val[-1:] == ['true'] and L.get('recipes_arrow_lines') == 0 and seed == (0, 0) and pp == (0, 0) \
            and 'KYTY_REC' not in env and L['count'].get('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features', 0) >= 1
    else:
        good = 'KYTY_PIPELINE_PRECACHE' not in env and val[-1:] == ['false'] and L.get('recipes_arrow_lines', 0) >= 1 and seed[0] >= 1 and 'KYTY_REC' in env
    okform &= good
    print('FORM %s env KYTY_PIPELINE_PRECACHE=%r validation args %s KYTY_REC %s; "N recipes ->" log %s; ShaderSeed: log/stdout %s; PipelinePrecache: log/stdout %s; '
          'valfeat %s; binary %s; prereg %s -> %s' % (
              t, env.get('KYTY_PIPELINE_PRECACHE'), val, 'KYTY_REC' in env, L.get('recipes_arrow_lines'), seed, pp,
              L['count'].get('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features'),
              str(a['json'].get('binary_sha256'))[:8], str((a['json'].get('prereg') or {}).get('sha256'))[:8], 'ok' if good else 'VIOLATED'))
print('W FORM own reading over 33 tags: %s' % ('ALL OK' if okform else 'VIOLATIONS'))

# own SCENE_OK reading per pair (pred/02_sc143.md s.3 rows that the log, the json and the attempt decide; video rows - vid144.py)
P12 = list(range(9, 21))
pairs = [('s143', 'v143_%02d' % v, 's144', 'w144_%02d' % w) for w, v in enumerate(W8, 1)] + [('s144', 'v144_%02d' % i, 's144', 'w144_%02d' % i) for i in P12]
own = {}
for vr, vt, wr, wt in pairs:
    va, wa = A[(vr, vt)], A[(wr, wt)]
    v, w = va['log'], wa['log']
    vj = (va['json'].get('attempts') or [{}])[0]
    wj = (wa['json'].get('attempts') or [{}])[0]
    ves, wes = va['emu_stdout'], wa['emu_stdout']
    vf, wf = [], []
    if va['level'] != wa['level'] or vj.get('level') != va['level'] or wj.get('level') != wa['level'] \
            or va['json'].get('guest_args') != '-lvl ' + va['level'] or wa['json'].get('guest_args') != '-lvl ' + wa['level']:
        vf.append('pair: level / guest args mismatch')
    if v.get('entry_pos') is None: vf.append('V not entered')
    if v.get('first') is None: vf.append('V no first scene frame')
    if v.get('scene_changes'): vf.append('V scene change')
    if not ves.get('present'): vf.append('V no emulator stdout')
    if not (vj.get('outcome') == 'ok' and (vj.get('hold_s') or 0) >= 330 and vj.get('hold_exit') is None): vf.append('V attempt / hold_s %r / hold_exit %r' % (vj.get('hold_s'), vj.get('hold_exit')))
    if v.get('n_marks') or (ves.get('marks') if ves.get('present') else None): vf.append('V death markers')
    if v.get('k2'): vf.append('V frame >= 1 s %r' % (v['k2'],))
    if v.get('n_gaps'): vf.append('V n gaps')
    if v.get('sum_dt_after_first_us', 0) < 300000000: vf.append('V shown < 300 s')
    if v.get('frames_after_first', 0) < 3000: vf.append('V < 3000 frames')
    if w.get('entry_pos') is None: wf.append('W not entered')
    if w.get('scene_changes'): wf.append('W scene change')
    if not wes.get('present'): wf.append('W no emulator stdout')
    nm = (w.get('n_marks') or 0) + (len(wes.get('marks') or []) if wes.get('present') else 0)
    if nm or wj.get('hold_exit') is not None or wj.get('outcome') != 'ok': wf.append('W death markers %d / hold_exit %r / attempt %r' % (nm, wj.get('hold_exit'), wj.get('outcome')))
    ve = w.get('count', {}).get('[Vulkan][E]', 0) + ((wes.get('count') or {}).get('[Vulkan][E]', 0) if wes.get('present') else 0)
    if ve: wf.append('W [Vulkan][E] %d' % ve)
    if not (wj.get('ft_tail') or 0) > 0: wf.append('W ft_tail %r' % wj.get('ft_tail'))
    if not (wj.get('outcome') == 'ok' and (wj.get('hold_s') or 0) >= 300 and wj.get('hold_exit') is None): wf.append('W hold not reached (hold_s %r)' % wj.get('hold_s'))
    verdict = 'NO' if (vf or wf) else 'LOG ROWS PASS (video rows: vid144.py; sheet row: the close)'
    own[va['level']] = verdict
    print('SCENE_OK own %s %s/%s: %s (V: %s; W: %s)' % (va['level'], vt, wt, verdict, '; '.join(vf) or 'log rows pass', '; '.join(wf) or 'log rows pass'))
summ = open(S144 + '/step2/summary144.txt', encoding='utf-8', errors='replace').read().splitlines()
sm = {}
for ln in summ:
    m = re.match(r'SCENE_OK (\S+): (YES|NO|PENDING_SHEET)$', ln)
    if m:
        sm[m.group(1)] = m.group(2)
agree = sum(1 for k, v in own.items() if (v == 'NO') == (sm.get(k) == 'NO'))
print('SCENE_OK own against the summary: levels %d, NO in mine %d, NO in the summary %d, agreement on NO / not NO %d of %d' % (
    len(own), sum(1 for v in own.values() if v == 'NO'), sum(1 for v in sm.values() if v == 'NO'), agree, len(own)))
for ln in summ:
    if re.match(r'(SCENE_OK LEVELS|FORM |FORMS |CENSUS|STOP RULE|K2 ON THE HOLD|CONTROL W|W FORM)', ln):
        print('SUMMARY| ' + ln[:330])

# forms of the 12 repeated entries, own lists
b5 = [t for t in tags if t.startswith('v') and A[('s144', t)]['log'].get('k3w') or (t.startswith('v') and any(x[2] == 'entry' for x in (A[('s144', t)]['log'].get('k2') or [])))]
b5a = [t for t in tags if t.startswith('v') and A[('s144', t)]['log'].get('k2')]
b33 = [t for t in tags if t.startswith('v') and A[('s144', t)]['log'].get('k3h')]
print('FORMS own (repeated entries, 12 V): B5 (frame >= 100 ms in the entry window) %d %s; B5a (frame >= 1 s) %d %s; B33 (K3 on the hold) %d %s' % (
    len(b5), b5, len(b5a), b5a, len(b33), b33))

# item 270 (g)(1): the chain of w144_09; (2): census of the window lines over the logs of s142-s144
print('--- item 270 (g)(1): w144_09')
L = A[('s144', 'w144_09')]['log']
W = L['win']
for k in ('Window 1 ', 'minimized', 'restored', 'maximized', 'size changed to', 'resized to', 'keyboard focus', 'Mouse entered window', 'Mouse left window',
          'vkQueuePresentKHR returned', 'vkAcquireNextImageKHR returned', 'eErrorOutOfDateKHR', 'eSuboptimalKHR', 'eErrorSurfaceLostKHR',
          'Recovering Vulkan swapchain', 'Vulkan presentation retry exhausted', 'vkCreateSwapchainKHR', 'Event: '):
    e = W[k]
    print('W09 %-36s n %d %s' % (k, e['n'], '; '.join('@%d(line %d) rows_before %s last_n %s after-entry %.3f s rows_after %s "%s"' % (
        x['key_pos'], x['line_start'], x.get('rows_before'), x.get('last_n'), x.get('dt_after_entry_us', 0) / 1e6, x.get('rows_after'), x['line'][:110]) for x in e['events'][:4])))
mi = W['minimized']['events'][0]
oo = W['eErrorOutOfDateKHR']['events'][0]
rc = W['Recovering Vulkan swapchain']['events'][0]
print('W09 sha256 %s size %d; [Vulkan][E] lines in the log %d at %s: %s' % (L['sha256'], L['size'], L['count']['[Vulkan][E]'], L['vke_pos'], L['vke_lines'][0][:140]))
print('W09 order: minimized line %d < OutOfDate line %d < Recovering line %d < --- Error --- %d < [Vulkan][E] %d: %s' % (
    mi['line_start'], oo['line_start'], rc['line_start'], L['marks'][0][0], L['vke_pos'][0],
    mi['line_start'] < oo['line_start'] < rc['line_start'] < L['marks'][0][0] < L['vke_pos'][0]))
print('W09 bytes: [Vulkan][E] - minimized line start %d; - the " minimized" substring (line start + 8) %d; FrameTrace rows between minimized and the error %d (n %s .. %s); '
      'presented after the entry line: at minimized %.3f s, at OutOfDate %.3f s; log ends %d bytes after [Vulkan][E]' % (
          L['vke_pos'][0] - mi['line_start'], L['vke_pos'][0] - (mi['line_start'] + 8), oo['rows_before'] - mi['rows_before'], mi.get('last_n'), oo.get('last_n'),
          mi.get('dt_after_entry_us', 0) / 1e6, oo.get('dt_after_entry_us', 0) / 1e6, L['size'] - L['vke_pos'][0]))
print('--- item 270 (g)(2): logs of s142-s144')
n = 0
hits = 0
for key in sorted(A, key=lambda k: (k[0], k[1])):
    a = A[key]
    L = a['log']
    if 'win' not in L:
        continue
    n += 1
    W = L['win']
    c = {k: W[k]['n'] for k in ('minimized', 'restored', 'keyboard focus', 'size changed to', 'resized to', 'Recovering Vulkan swapchain', 'eErrorOutOfDateKHR',
                                'eSuboptimalKHR', 'eErrorSurfaceLostKHR', 'Vulkan presentation retry exhausted')}
    wl = sorted(set(re.sub(r'^Window 1 ', '', x['line']) for x in W['Window 1 ']['events']))
    es = a['emu_stdout']
    esm = (es.get('win') or {}).get('minimized', 0) if es.get('present') else None
    flag = c['minimized'] or c['Recovering Vulkan swapchain'] or c['eErrorOutOfDateKHR'] or c['eSuboptimalKHR']
    hits += 1 if c['minimized'] else 0
    print('WINLOG %s %-11s sha %s minimized %d (stdout %s) restored %d focus %d size/resized %d/%d recover %d OutOfDate %d Suboptimal %d SurfaceLost %d retry-exhausted %d '
          '[Vulkan][E] %d; Window lines %d %s%s' % (
              key[0], key[1], L['sha256'][:12], c['minimized'], esm, c['restored'], c['keyboard focus'], c['size changed to'], c['resized to'],
              c['Recovering Vulkan swapchain'], c['eErrorOutOfDateKHR'], c['eSuboptimalKHR'], c['eErrorSurfaceLostKHR'], c['Vulkan presentation retry exhausted'],
              L['count']['[Vulkan][E]'], W['Window 1 ']['n'], wl, '  <== ' if flag else ''))
print('WINLOG total: logs %d; with a "minimized" line %d' % (n, hits))
print('ALL DONE')
