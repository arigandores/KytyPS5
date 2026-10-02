# cmp146.py - Session Auditor, s146 step 3 (HPP-389): own recount (aud146.json) against the scorer outputs
# runs146/<tag>.score.json (35 made tags), field by field; own outcome class by the letter of the seal; own SCENE_OK reading
# per pair (15 levels); own RECHECK reading (r146_01..03) and the B40 second hold (r146_04); the W form of items 300 (b)(4)
# and 295 (b)(1)-(4); the DualSrcBlend control; stubs (F13) / asserts (F14); window lines; forms B5 / B5a / B33 of the 15
# cold entries; the warm-up i146_v. No code shared with sc146.py / gate146.py (a port of the auditor's own cmp145.py).
import json, re, os

S146 = 'C:/kyty/s146'
A = {r['tag']: r for r in json.load(open(S146 + '/step3/aud146.json'))}
RL = ['hoover_beach', 'sponge_dirty_bath', 'timestop_casino', 'bonus_path_maker_mix']
LV = ['robot_builder_next', 'interactive_credit_00', 'non_interactive_credit', 'ending_boss_after_credit', 'collectible_viewer',
      'hub_crashsite_diorama', 'diorama_controller_skin', 'diorama_astro_skin', 'diorama_zoo', 'fragile_battle_1', 'voxel_challenge_1',
      'armadillo_challenge_1', 'fragile_battle_2', 'voxel_challenge_2', 'fragile_battle_3']
order = ['w146_00'] + ['r146_%02d' % i for i in range(1, 5)]
for i in range(5, 20):
    order += ['v146_%02d' % i, 'w146_%02d' % i]
made = [t for t in order if os.path.isfile('%s/runs146/%s.score.json' % (S146, t))]
notmade = [t for t in order if t not in made]
diffs = 0
fields = 0
notes = 0


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


def isw(t):
    return t.startswith('w')


def own_outcome(a, t):
    """Own outcome class by the letter printed in the seal (items 221 (g)(2), 223 (a), 224 (a)); W is not judged by dt."""
    L = a['log']
    es = a['emu_stdout']
    js = a['json']
    att = (js.get('attempts') or [{}])[0] if isinstance(js, dict) else {}
    if L.get('entry_pos') is None:
        return 'NOT_ENTERED'
    lm = L.get('marks') or []
    sm = (es.get('marks') or []) if es.get('present') else []
    k2 = [] if isw(t) else (L.get('k2') or [])
    ch = L.get('scene_changes') or []
    if ch:
        cp = ch[0][0]
        if [m for m in lm if m[0] < cp]:
            return 'STOPPED'
        return 'K2' if k2 else 'NOT_EVALUABLE'
    if lm or sm:
        return 'STOPPED'
    if att.get('hold_exit') is not None or (a['es_stdout'].get('ended') or 0):
        return 'K1'
    if k2 or (att.get('ft_tail') == 0 and att.get('hold_s') is not None):
        return 'K2'
    if L.get('first') is None or att.get('outcome') != 'ok' or (att.get('hold_s') or 0) < 120:
        return 'NOT_EVALUABLE'
    return 'HOLDS_120' if L.get('sum_dt_after_entry_us', 0) >= 120000000 else 'NOT_EVALUABLE'


def compare(t, score_path):
    global fields, notes
    a = A[t]
    L = a['log']
    S = json.load(open(score_path, encoding='utf-8'))
    D = S['derive']
    c = L.get('count', {})
    es = a['emu_stdout']
    esc = (es.get('count') or {}) if es.get('present') else {}
    cmpf(t, 'log sha256 = score log_sha', L['sha256'], S['log_sha'])
    cmpf(t, 'log sha256 = times_log_sha', L['sha256'], S['times_log_sha'])
    cmpf(t, 'level', a['level'], S['level'])
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
        notes += 1
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
    cmpf(t, 'change_pos', (L.get('scene_changes') or [[None]])[0][0], D.get('change_pos'))
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
    cmpf(t, 'stubs (=== Stubbed function)', c.get('=== Stubbed function', 0), len(S['stubs']))
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
    cmpf(t, 'tail_stall', att.get('ft_tail') == 0 and att.get('hold_s') is not None, S.get('tail_stall'))
    # rows of items 273 (k)(2)-(3) and 295 (b), (g)
    cmpf(t, 'layer limit lines (log + stdout)', c.get('last time reporting it', 0) + esc.get('last time reporting it', 0), S['limit'])
    w2 = c.get('[Vulkan][W][2]', 0) + c.get('[Vulkan][E][2]', 0) + esc.get('[Vulkan][W][2]', 0) + esc.get('[Vulkan][E][2]', 0)
    cmpf(t, 'validation-layer lines [W][2] + [E][2] (log + stdout) = vk2', w2, S['vk2'])
    cmpf(t, 'F6 text lines ("and this write is unused", log + stdout) = f6', c.get('and this write is unused', 0) + esc.get('and this write is unused', 0), S['f6'])
    held_m = L.get('size') is not None and not mm and att.get('hold_exit') is None and att.get('outcome') == 'ok' and not (a['es_stdout'].get('ended') or 0)
    cmpf(t, 'held', held_m, S['held'][0])
    if isw(t):
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
    # new data rows of profile 146 (item 309 (l)(4))
    sc = S.get('stubcall') or {}
    cmpf(t, 'stubcall log (Unresolved import stub called)', c.get('Unresolved import stub called', 0), sc.get('log'))
    cmpf(t, 'stubcall stdout', esc.get('Unresolved import stub called', 0), sc.get('stdout'))
    asr = S.get('asserts') or {}
    cmpf(t, 'ASSERT: log', c.get('ASSERT:', 0), asr.get('log'))
    cmpf(t, 'ASSERT: stdout', esc.get('ASSERT:', 0), asr.get('stdout'))
    cmpf(t, 'user_msg_param log', c.get('user_msg_param', 0), asr.get('ump_log'))
    cmpf(t, 'user_msg_param stdout', esc.get('user_msg_param', 0), asr.get('ump_stdout'))
    cmpf(t, 'DualSrcBlend lines (supported, enabled)', [list(x[1:]) for x in (L.get('dual') or [])], [list(x) for x in (S.get('dual') or [])])
    cmpf(t, 'DualSrcBlend 1/1 before the first GuestOut', L.get('dual_pre'), S.get('dual_pre'))
    cmpf(t, 'DualSrcBlend control present', (L.get('dual_pre') or 0) >= 1, S.get('dual_ok'))
    mine_out = own_outcome(a, t)
    their = S['outcome']
    cmpf(t, 'outcome class', mine_out, 'STOPPED' if their in ('K1', 'VALIDATION_STOP') and S['marks'] else their)
    print('ROW %s %s rows %s first %s shown %.1f s / %s frames K2 %s K3w %d K3h %d skip %s/%s(id) prio %d/%s bvh %s vkE %d+%d '
          'recipes-> %s/%s limit %s [W][2]+[E][2] %s layer_end_us %s winkinds %s marks %s hold_s %s hold_exit %s attempt %s changes %s '
          'stubcall %s/%s dual_pre %s outcome mine %s scorer %s|%s' % (
              t, a['level'], L.get('rows_total'), L.get('first'), L.get('sum_dt_after_first_us', 0) / 1e6, L.get('frames_after_first', 0),
              L.get('k2', []), len(L.get('k3w', [])), len(L.get('k3h', [])), sk.get('lines'), sk.get('frames_by_id'),
              pr.get('over', 0), pr.get('max', 0), L.get('raw', {}).get('BvhLoopCapTrip:#n', 0), vke_log, vke_out,
              L.get('recipes_arrow_lines'), es.get('recipes_arrow_lines') if es.get('present') else None,
              c.get('last time reporting it', 0), c.get('[Vulkan][W][2]', 0) + c.get('[Vulkan][E][2]', 0), L.get('layer_end_us'),
              {k: v for k, v in kinds_sum(a).items() if v}, mm, att.get('hold_s'), att.get('hold_exit'), att.get('outcome'),
              [x[1] for x in (L.get('scene_changes') or [])], c.get('Unresolved import stub called', 0), esc.get('Unresolved import stub called', 0),
              L.get('dual_pre'), mine_out, S['outcome'], S.get('outcome120')))
    return S


SC = {}
for t in made:
    SC[t] = compare(t, '%s/runs146/%s.score.json' % (S146, t))
print('FIELDS compared %d over %d logs; DIFFS %d; form notes (median) %d; not made (no score json): %s' % (fields, len(made), diffs, notes, notmade))

# the form of every made tag: env of the json, command line, lines of the log and of the emulator stdout
okform = True
for t in made:
    a = A[t]
    L = a['log']
    es = a['emu_stdout']
    esc = (es.get('count') or {}) if es.get('present') else {}
    env = a['json'].get('env', {})
    cl = a['json'].get('cmdline', [])
    val = [cl[k + 1] for k, x in enumerate(cl[:-1]) if x == '--vulkan-validation']
    seed = (L.get('raw', {}).get('ShaderSeed:#n', 0), esc.get('ShaderSeed:', 0))
    pp = (L.get('raw', {}).get('PipelinePrecache:#n', 0), esc.get('PipelinePrecache:', 0))
    c = L['count']
    base = 'KYTY_PIPELINE_PRECACHE' not in env and 'VK_LAYER_MESSAGE_ID_FILTER' not in env and env.get('KYTY_GPU_CLOCK_PIN') == '1' \
        and env.get('KYTY_GPU_MARKERS') == '0' and 'KYTY_GPU_CHECKPOINTS' not in env and len(a['json'].get('attempts') or []) == 1 \
        and str(a['json'].get('binary_sha256', '')).startswith('dac02fb9') and not [k for k in env if k.startswith('KYTY_FIX_') or k.startswith('KYTY_PVAR') or k.startswith('KYTY_POKE')]
    if isw(t):
        good = base and val[-1:] == ['true'] and 'KYTY_REC' not in env and env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT') == '100000000' \
            and c.get('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features', 0) >= 1 and L.get('recipes_arrow_lines', 0) >= 1
    else:
        good = base and val[-1:] == ['false'] and L.get('recipes_arrow_lines', 0) >= 1 and 'KYTY_REC' in env and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT' not in env
    okform &= bool(good)
    print('FORM %s env KYTY_PIPELINE_PRECACHE key %s limit=%r filter key %s validation args %s KYTY_REC %s; "N recipes ->" log %s; ShaderSeed: log/stdout %s; '
          'PipelinePrecache: log/stdout %s; valfeat %s; layer header lines KHRONOS %s / validation_features %s / debug_utils %s; limit lines %s; [W][2]+[E][2] %s; '
          '[W][1] %s; layer_end_us %s; binary %s; prereg %s; attempts %d; KYTY_* env keys %s -> %s' % (
              t, 'KYTY_PIPELINE_PRECACHE' in env, env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'), 'VK_LAYER_MESSAGE_ID_FILTER' in env, val, 'KYTY_REC' in env,
              L.get('recipes_arrow_lines'), seed, pp, c.get('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features'),
              c.get('VK_LAYER_KHRONOS_validation'), c.get('VK_EXT_validation_features'), c.get('VK_EXT_debug_utils'),
              c.get('last time reporting it'), c.get('[Vulkan][W][2]', 0) + c.get('[Vulkan][E][2]', 0), c.get('[Vulkan][W][1]'), L.get('layer_end_us'),
              str(a['json'].get('binary_sha256'))[:8], str((a['json'].get('prereg') or {}).get('sha256'))[:8], len(a['json'].get('attempts') or []),
              sorted(k for k in env if k.startswith('KYTY_')), 'ok' if good else 'VIOLATED'))
print('FORM own reading over %d made tags (seal s.1; items 300 (b)(4), 309 (l)(3)): %s' % (len(made), 'ALL OK' if okform else 'VIOLATIONS'))


def v_fail(va):
    v = va['log']
    vj = (va['json'].get('attempts') or [{}])[0] if 'error' not in va['json'] else {}
    ves = va['emu_stdout']
    vf = []
    if 'error' in v:
        return ['V no log']
    if va['json'].get('guest_args') != '-lvl ' + va['level'] or vj.get('level') != va['level']: vf.append('V level / guest args mismatch')
    if v.get('entry_pos') is None: vf.append('V not entered')
    if v.get('first') is None: vf.append('V no first scene frame')
    if v.get('scene_changes'): vf.append('V scene change %s' % [x[1] for x in v['scene_changes']])
    if not (vj.get('outcome') == 'ok' and (vj.get('hold_s') or 0) >= 330 and vj.get('hold_exit') is None): vf.append('V attempt %r / hold_s %r / hold_exit %r' % (vj.get('outcome'), vj.get('hold_s'), vj.get('hold_exit')))
    if v.get('n_marks') or (ves.get('marks') if ves.get('present') else None): vf.append('V death markers')
    if v.get('k2'): vf.append('V frame >= 1 s %r' % (v['k2'],))
    if v.get('n_gaps'): vf.append('V n gaps')
    if v.get('sum_dt_after_first_us', 0) < 300000000: vf.append('V shown %.1f s < 300 s' % (v.get('sum_dt_after_first_us', 0) / 1e6))
    if v.get('frames_after_first', 0) < 3000: vf.append('V < 3000 frames')
    if (v.get('win_kinds') or {}).get('minimized') or v['count'].get('Recovering Vulkan swapchain'): vf.append('V window event')
    return vf


def w_fail(wa, level):
    w = wa['log']
    wj = (wa['json'].get('attempts') or [{}])[0] if 'error' not in wa['json'] else {}
    wes = wa['emu_stdout']
    wf = []
    if 'error' in w:
        return ['W no log (tag not made)']
    wenv = wa['json'].get('env', {})
    wc = w['count']
    if wa['json'].get('guest_args') != '-lvl ' + wa['level'] or wj.get('level') != wa['level'] or level != wa['level']: wf.append('W level / guest args mismatch')
    if w.get('entry_pos') is None: wf.append('W not entered')
    if w.get('scene_changes'): wf.append('W scene change %s' % [x[1] for x in w['scene_changes']])
    nm = (w.get('n_marks') or 0) + (len(wes.get('marks') or []) if wes.get('present') else 0)
    if nm or wj.get('hold_exit') is not None or wj.get('outcome') != 'ok': wf.append('W death markers %d / hold_exit %r / attempt %r' % (nm, wj.get('hold_exit'), wj.get('outcome')))
    ve = wc.get('[Vulkan][E]', 0) + ((wes.get('count') or {}).get('[Vulkan][E]', 0) if wes.get('present') else 0)
    if ve: wf.append('W [Vulkan][E] %d' % ve)
    if not (wj.get('ft_tail') or 0) > 0: wf.append('W ft_tail %r' % wj.get('ft_tail'))
    if not ((wj.get('hold_s') or 0) >= 300): wf.append('W hold_s %r' % wj.get('hold_s'))
    if 'KYTY_PIPELINE_PRECACHE' in wenv: wf.append('W form 300 (b)(4): KYTY_PIPELINE_PRECACHE in the env')
    if wc.get('last time reporting it', 0): wf.append('W 295(b)(1) limit lines %d' % wc['last time reporting it'])
    if wc.get('[Vulkan][W][2]', 0) + wc.get('[Vulkan][E][2]', 0) < 1: wf.append('W 295(b)(2) no validation-layer line')
    if w.get('layer_end_us') is None or w['layer_end_us'] > 10000000: wf.append('W 295(b)(3) layer_end_us %r' % w.get('layer_end_us'))
    if form4(wenv) != 'W form: limit=100000000 filter=none' or 'VK_LAYER_MESSAGE_ID_FILTER' in wenv: wf.append('W 295(b)(4) %s' % form4(wenv))
    if (w.get('win_kinds') or {}).get('minimized') or wc.get('Recovering Vulkan swapchain'): wf.append('W window event')
    return wf


# own SCENE_OK reading per pair (rows that the log, the json and the attempt decide; video rows - vid146.py; sheet row - the close)
own = {}
for i, lv in enumerate(LV, 5):
    vt, wt = 'v146_%02d' % i, 'w146_%02d' % i
    vf, wf = v_fail(A[vt]), w_fail(A[wt], lv)
    verdict = 'NO' if (vf or wf) else 'LOG ROWS PASS (video rows: vid146.py; sheet row: the close)'
    own[lv] = verdict
    print('SCENE_OK own %s %s/%s: %s (V: %s; W: %s)' % (lv, vt, wt, verdict, '; '.join(vf) or 'log rows pass', '; '.join(wf) or 'log rows pass'))
summ = open(S146 + '/step2/summary146.txt', encoding='utf-8', errors='replace').read().splitlines()
sm = {}
rk = {}
for ln in summ:
    m = re.match(r'SCENE_OK (\S+): (YES|NO|PENDING_SHEET)$', ln)
    if m:
        sm[m.group(1)] = m.group(2)
    m = re.match(r'RECHECK (\S+) \((r146_\d\d);.*\): (PASSES|REMOVES SCENE_OK|PENDING_SHEET)$', ln)
    if m:
        rk[m.group(2)] = m.group(3)
agree = sum(1 for k, v in own.items() if (v == 'NO') == (sm.get(k) == 'NO'))
print('SCENE_OK own against the summary: levels %d, NO in mine %d %s, NO in the summary %d %s, agreement on NO / not NO %d of %d' % (
    len(own), sum(1 for v in own.values() if v == 'NO'), [k for k, v in own.items() if v == 'NO'],
    sum(1 for v in sm.values() if v == 'NO'), [k for k, v in sm.items() if v == 'NO'], agree, len(own)))

# own RECHECK reading (r146_01..03): the V rows of item 221 (g)(3) on dac02fb9
ragree = 0
for i in range(1, 4):
    t = 'r146_%02d' % i
    vf = v_fail(A[t])
    mine = 'REMOVES SCENE_OK' if vf else 'LOG ROWS PASS'
    ok = (mine == 'REMOVES SCENE_OK') == (rk.get(t) == 'REMOVES SCENE_OK')
    ragree += ok
    print('RECHECK own %s %s: %s (%s); summary %s; agree %s' % (t, A[t]['level'], mine, '; '.join(vf) or 'log rows pass', rk.get(t), ok))
print('RECHECK own against the summary: agreement %d of 3' % ragree)
a4 = A['r146_04']
L4 = a4['log']
print('B40 own r146_04 %s: entered %s, first %s, K2 %s, K3w %d, K3h %d, shown after the first scene frame %.1f s, frames %d, V rows failing: %s' % (
    a4['level'], L4.get('entry_pos') is not None, L4.get('first'), L4.get('k2'), len(L4.get('k3w', [])), len(L4.get('k3h', [])),
    L4.get('sum_dt_after_first_us', 0) / 1e6, L4.get('frames_after_first', 0), v_fail(a4) or 'none'))
for ln in summ:
    if re.match(r'(SCENE_OK LEVELS|RECHECK |B40 |SKY GARDEN|FORM |FORMS |CENSUS made|STOP RULE|K2 ON THE HOLD|CONTROL W|W FORM|WINDOW EVENTS|LAYER LIMIT|VIDEO CONTINUITY \(|DATA asserts|SKIPPED_V)', ln):
        print('SUMMARY| ' + ln[:900])

# control W own reading (item 300 (b)(4)): letter terms of its stop
w0 = A['w146_00']
wf0 = w_fail(w0, 'underwater_aerial_garden')
print('CONTROL W own w146_00: rows failing %s; DualSrcBlend 1/1 before the first GuestOut %s (dual at %s, GuestOut at %s); -> %s' % (
    wf0 or 'none', w0['log'].get('dual_pre'), [x[0] for x in w0['log'].get('dual') or []], w0['log']['first_pos'].get('GuestOut'),
    'PASS' if not wf0 and (w0['log'].get('dual_pre') or 0) >= 1 else 'STOP'))

# the 16 W: 295 (b) rows own
for t in [x for x in made if isw(x)]:
    L = A[t]['log']
    c = L['count']
    att = (A[t]['json'].get('attempts') or [{}])[0]
    held = att.get('outcome') == 'ok' and att.get('hold_exit') is None and not L.get('n_marks')
    w2 = c.get('[Vulkan][W][2]', 0) + c.get('[Vulkan][E][2]', 0)
    b = []
    if c.get('last time reporting it', 0): b.append('(b)(1)')
    if held and w2 < 1: b.append('(b)(2)')
    if held and (L.get('layer_end_us') is None or L['layer_end_us'] > 10000000): b.append('(b)(3)')
    if form4(A[t]['json'].get('env', {})) != 'W form: limit=100000000 filter=none': b.append('(b)(4)')
    print('W295 own %s: held %s (attempt %s, hold_s %s); limit lines %d; layer lines %d; layer_end_us %s; rows after the last layer line %s; failing %s; [Vulkan][E] %d; shown after the first scene frame %.1f s' % (
        t, held, att.get('outcome'), att.get('hold_s'), c.get('last time reporting it', 0), w2, L.get('layer_end_us'), L.get('layer_rows_after'), ','.join(b) or 'none',
        c.get('[Vulkan][E]', 0), L.get('sum_dt_after_first_us', 0) / 1e6))

# forms of the 15 cold entries, own lists
vt = ['v146_%02d' % i for i in range(5, 20)]
def lg(t): return A[t]['log']
b5 = [t for t in vt if lg(t).get('k3w') or any(x[2] == 'entry' for x in (lg(t).get('k2') or []))]
b5a = [t for t in vt if lg(t).get('k2')]
b5a120 = [t for t in vt if lg(t).get('k2_120_incl')]
b33 = [t for t in vt if lg(t).get('k3h')]
b33_120 = [t for t in vt if lg(t).get('k3h120_incl')]
ent = [t for t in vt if lg(t).get('entry_pos') is not None]
print('FORMS own (cold first entries, 15 V; entered %d): B5 %d %s; B5a %d %s; B5a variant 120 s %d %s; B33 %d %s; B33 variant 120 s %d %s' % (
    len(ent), len(b5), b5, len(b5a), b5a, len(b5a120), b5a120, len(b33), b33, len(b33_120), b33_120))
first8, last7 = vt[:8], vt[8:]
print('FORMS own second reading: first 8 B5a %d B5 %d; last 7 B5a %d B5 %d' % (
    sum(1 for t in first8 if t in b5a), sum(1 for t in first8 if t in b5), sum(1 for t in last7 if t in b5a), sum(1 for t in last7 if t in b5)))

# entry lines of the tags with a scene change or without a stable hold; copies _a1
for t in made:
    L = lg(t)
    att = (A[t]['json'].get('attempts') or [{}])[0]
    if L.get('scene_changes') or att.get('outcome') != 'ok':
        print('ENTRY %s %s: "Level has started:" lines %s; attempt outcome %s hold_s %s ft_tail %s; first %s; rows %s; shown after entry %.1f s / after first %.1f s' % (
            t, A[t]['level'], [(p, nm) for p, nm in L.get('starts', [])], att.get('outcome'), att.get('hold_s'), att.get('ft_tail'), L.get('first'),
            L.get('rows_total'), L.get('sum_dt_after_entry_us', 0) / 1e6, L.get('sum_dt_after_first_us', 0) / 1e6))
for t in sorted(A):
    if t.endswith('_a1'):
        b = t[:-3]
        print('COPY log_%s.txt sha %s = log_%s.txt sha %s: %s' % (t, A[t]['log']['sha256'][:16], b, A[b]['log']['sha256'][:16], A[t]['log']['sha256'] == A[b]['log']['sha256']))
a2 = [f for f in os.listdir(S146) if re.match(r'log_.*_a[2-9][.]txt$', f)]
print('SECOND ATTEMPT logs (log_*_a2.txt and later): %d %s' % (len(a2), a2))

# the warm-up i146_v (step 0): own V rows
ai = A['i146_v']
Li = ai['log']
print('WARMUP own i146_v: sha %s; entered %s; first %s; shown after the first scene frame %.1f s; frames %d; K2 %s; dt max %s; marks %s; bvh %s; skip %s; dual_pre %s; '
      'window kinds %s; recipes-> %s; V rows failing (json = enter_scene json of the tag): %s' % (
          Li['sha256'][:16], Li.get('entry_pos') is not None, Li.get('first'), Li.get('sum_dt_after_first_us', 0) / 1e6, Li.get('frames_after_first', 0), Li.get('k2'),
          Li.get('dt_max_us'), Li.get('n_marks'), Li.get('raw', {}).get('BvhLoopCapTrip:#n'), Li.get('skip'), Li.get('dual_pre'),
          {k: v for k, v in (Li.get('win_kinds') or {}).items() if v}, Li.get('recipes_arrow_lines'), v_fail(ai) or 'none'))

# every tag: K2 / K3 frames with a window line within 2 s (own), W frames >= 1 s (data, W is not judged by dt)
for t in made:
    L = lg(t)
    nn = [x for x in (L.get('winnear') or []) if x[4]]
    k2 = L.get('k2') or []
    if nn or (k2 and isw(t)):
        print('WINNEAR %s: K2/K3 frames %d, with a window line within 2 s %d %s; frames >= 1 s %s' % (
            t, len(L.get('winnear') or []), len(nn), [(x[0], x[2], x[3], x[4][1][-28:], round(x[4][0] / 1e6, 3)) for x in nn[:3]], k2))
print('ALL DONE')
