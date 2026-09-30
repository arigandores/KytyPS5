# cmp142.py - compare own recount (rc/<tag>.json of aud142.py) with the scorer outputs runs142/<tag>.score.json, <tag>.json and glitch files
import json, re, sys
TAGS = ['v142', 'w142'] + ['c142_%02d' % i for i in range(1, 11)]
S = 'C:/kyty/s142/'
bad = 0; lines = []
def chk(tag, what, mine, theirs):
    global bad
    ok = mine == theirs
    bad += 0 if ok else 1
    lines.append('%-8s %-26s %-6s mine=%s scorer=%s' % (tag, what, 'OK' if ok else 'DIFF', mine, theirs))
k5a = 0; k5 = []
for t in TAGS:
    a = json.load(open(S + 'step3/rc/%s.json' % t))
    s = json.load(open(S + 'runs142/%s.score.json' % t))
    j = json.load(open(S + '%s.json' % t))
    d = s['derive']
    chk(t, 'log sha256', a['log_sha256'], s['log_sha'])
    chk(t, 'entered', a['entry_line'] is not None, d['entered'])
    chk(t, 'first scene (n,dt,draws)', [a['first_scene']['n'], a['first_scene']['dt_us'], a['first_scene']['draws']], d['first'])
    chk(t, 'window/hold len', [a['win_len'], a['hold_len']], [d['window'], d['hold']])
    chk(t, 'K2 frames', [x[:2] for x in a['K2']], [list(x[:2]) for x in d['k2']])
    chk(t, 'K3 window', [x[:2] for x in a['K3_win']], d['k3w'])
    chk(t, 'K3 hold', [x[:2] for x in a['K3_hold']], d['k3h'])
    chk(t, 'sum dt after entry', a['sum_dt_after_entry_us'], d['dt_after_entry_us'])
    chk(t, 'sum dt after first', a['sum_dt_after_first_us'], d['dt_after_first_us'])
    chk(t, 'frames after first', a['frames_after_first'], d['frames_after_first'])
    chk(t, 'median(round half)/max dt', [int(a['median_dt'] + 0.5), a['max_dt']], [d['dt_median_us'], d['dt_max_us']])
    if a['median_dt'] != int(a['median_dt']): lines.append('%-8s info: median of an even count %.1f (scorer prints it rounded)' % (t, a['median_dt']))
    chk(t, 'n gaps', a['n_gaps'], d['n_gaps'])
    chk(t, 'FrameTrace rows all', a['rows_all'], s['rows_total'])
    chk(t, 'torn', a['torn'], s['torn'])
    chk(t, 'scene changes', a['scene_changes'], d['other_starts'])
    em = a['emu_stdout'] or {}
    mk = len(a['marks_log']) + len(em.get('marks', []))
    chk(t, 'death markers (log+emu)', mk, len(s['marks']))
    chk(t, '[Vulkan][E] log+emu', a['vk_log']['E'] + em.get('vkE', 0), s['vke'])
    chk(t, 'val no/feat/any', [a['vk_log']['nolayer'] + em.get('nolayer', 0), a['vk_log']['valfeat'] + em.get('valfeat', 0), a['vk_log']['any'] + em.get('vkany', 0)], [s['val']['noval'], s['val']['valfeat'], s['val']['vkany']])
    chk(t, 'skipped draw lines/frame= ids', [a['skipped_lines'], a['skipped_ids']], [s['skip']['lines'], s['skip']['frames']])
    lines.append('%-8s info: skipped draw by row position (own reading) %d frames' % (t, a['skipped_frames']))
    chk(t, 'opcode not impl lines', a['opc'], s['ops']['total'])
    chk(t, 'bvh', a['bvh'], s['bvh'])
    es = a['es_stdout'] or {}
    att = j['attempts'][-1]
    chk(t, 'ENDED lines', es.get('ended', 0) > 0, s['ended'])
    chk(t, 'attempt ok/hold_s/ft_tail', [att['outcome'], att['hold_s'], att['ft_tail'], att['hold_exit']], [s['attempt_outcome'], s['hold_s'], s['ft_tail'], s['hold_exit']])
    # own outcome by the letter of pred/02 s.2
    if a['entry_line'] is None: oc = 'NOT_ENTERED'
    elif mk: oc = 'MARKER'
    elif att['hold_exit'] or es.get('ended'): oc = 'K1'
    elif a['K2'] or att['ft_tail'] == 0: oc = 'K2'
    elif att['outcome'] != 'ok' or (att['hold_s'] or 0) < 120: oc = 'NOT_EVALUABLE'
    elif a['sum_dt_after_entry_us'] >= 120000000: oc = 'HOLDS_120'
    else: oc = 'NOT_EVALUABLE'
    chk(t, 'outcome', oc, s['outcome'])
    if t.startswith('c142'):
        if a['K2']: k5a += 1
        if a['K3_win'] or [x for x in a['K2'] if x[2] == 'window']: k5.append(t)
    lines.append('%-8s info: first-frame ts %s, K3 window with ts %s, window last ts %s, sum after first %.1f s' % (t, a['first_scene']['ts'], a['K3_win'], a['win_last_ts'], a['sum_dt_after_first_us'] / 1e6))
lines.append('census: B5a (K2 frame after the first scene frame) %d/10; B5 (frame >= 100 ms in the entry window) %d/10 %s; first five %d/5, last five %d/5' % (
    k5a, len(k5), k5, len([x for x in k5 if int(x[-2:]) <= 5]), len([x for x in k5 if int(x[-2:]) > 5])))
lines.append('DIFF count %d -> %s' % (bad, 'CONFIRMED' if bad == 0 else 'DIVERGES'))
open(S + 'step3/rc/cmp142.out.txt', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(l for l in lines if 'DIFF' in l or 'info' in l or 'census' in l))
