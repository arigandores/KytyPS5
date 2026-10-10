# F32d (HPP-742, ROADMAP p.673(z)(3)(2)): attribution of every frame >= 100 ms on the hold of a course-line log without
# validation (frames_f32d.json; run form - meta_f32d.json) to one class, by the rules below (fixed before the classified table
# was read; precedents named per rule).  First rule that fires is the class ('attr'); every rule that fires is listed ('also').
#   B5      a mark of first use in the frame interval: SPIR-V dump lines ('%'), GCN disassembly lines, 'AsyncPipelines: skipped
#           draw', 'AsyncPipelines: flip <n> held' (the F20a interval marks; the F27d exclusion list 'translation / skipped draw /
#           held').  Sub-form: 'cold' when the entry window had such lines (tr_win > 0), else 'hold' (first use on the hold of an
#           entry with a warm window).
#   B33     a 'Vulkan pipeline cache: saved ... (<us> us)' line in the interval with us >= 0.5 x (dt_us - 16 667) (the write can
#           cover at least half of the excess over one vblank; F27a save window).  Fires after B5 (F27d: a save frame with
#           translation / skipped draw / held is not B33 evidence).  'reopen' = the frame also has no B5 mark and the run form
#           is the default one (no INSTR, no B5F, no patch / poke) - the B33 reopening condition of p.637 (register s89:1352).
#   PAUSE   'Pause: true', 'lost keyboard focus' or 'Event: will_enter_background' in the interval (emulator pause by the Space
#           key / background, window.cpp SetPause; F20a for the user recording).  Not in the p.673(z)(3)(2) list - printed apart.
#   INSTR   the run form carries an instrument: RenderDoc ('RenderDoc: API ... bound' head line or KYTY_RD_* env),
#           '--shader-validation true', a diagnostic / trace knob (KYTY_AV_TRACE, KYTY_SHADER_REGISTER_TRACE, KYTY_IMAGE_WATCH,
#           KYTY_DUMP_*, KYTY_CLEAR_TRACE, KYTY_IMAGE_LIFETIME_TRACE, KYTY_DIAG_*, KYTY_PRINT_NAMES, KYTY_SYNC_*), a stand
#           (KYTY_TEST_*, KYTY_POKE - guest code poke of track P).  The harness form (KYTY_FRAME_TRACE, KYTY_QUEUE_TRACE,
#           KYTY_GPU_CLOCK_PIN, KYTY_GPU_MARKERS, KYTY_GATE_FILE, KYTY_SAMPLE_GATE, KYTY_GPU_HANG_ABORT_S, KYTY_REC,
#           KYTY_GUEST_ARGS, KYTY_KEYS) is not an instrument (it is the form of every V tag of the course).
#   B5F     the run form is a cold / collection form of track S: KYTY_PIPELINE_PRECACHE=0 or KYTY_PIPELINE_SALT (salted cold
#           form, F27c), KYTY_S_REPLAY in {1, 2} (capture), KYTY_CACHE_MODE=prepare-cold (form U), a catalog collection arm
#           (path /s288/s13/log_k_ or /s288/s15/log_k_, F32a s3.5).
#   HOST    a 'DiagB32:' line in the interval with other_us >= 0.4562 x ncpu x dt_us (HOST_LOAD of F20l / F25f, theta_load of
#           the F20l2 seal).  Without DiagB32 lines host load is not recorded per frame - the rule cannot fire.
#   B32     level underwater_aerial_garden or intro_next (the B32 form of the register, s76:1203 / s88:1344).
#   NONE    not attributed.
# Order: B5, B33, PAUSE, INSTR, B5F, HOST, B32, NONE.  'warm' = no first-use line in the entry from the level start up to the
# frame (tr_win == 0 and tr_hold_before == 0).  'patch' = KYTY_GAME_PATCH in the env, 'GamePatch' head or the user recording
# with a patch sha in times.txt (printed, not a class).
# Usage: python classify_f32d.py <frames_f32d.json> <meta_f32d.json> <out.tsv>
import os, re, sys, json, collections

TAB = chr(9)
NL = chr(10)
VBLANK = 16667
THETA_LOAD = 0.4562
DIAG_KEYS = ('KYTY_AV_TRACE', 'KYTY_SHADER_REGISTER_TRACE', 'KYTY_IMAGE_WATCH', 'KYTY_CLEAR_TRACE', 'KYTY_IMAGE_LIFETIME_TRACE',
             'KYTY_PRINT_NAMES', 'KYTY_POKE')
DIAG_PREFIX = ('KYTY_DIAG_', 'KYTY_TEST_', 'KYTY_DUMP_', 'KYTY_SYNC_', 'KYTY_RD_')
B32_LEVELS = ('underwater_aerial_garden', 'intro_next')
RE_KV = re.compile(r'(\w+)=(-?\d+)')


def env_of(meta):
    env = (meta or {}).get('env') or {}
    if isinstance(env, list):
        env = dict(x.split('=', 1) for x in env if '=' in x)
    return env


def flags_of(meta):
    cmd = (meta or {}).get('cmdline') or []
    if isinstance(cmd, str):
        cmd = cmd.split()
    return {cmd[i]: cmd[i + 1] for i in range(len(cmd) - 1) if cmd[i].startswith('--')}


def form_of(path, meta, heads):
    env = env_of(meta)
    fl = flags_of(meta)
    instr = []
    if any(h.startswith('RenderDoc: API') for h in heads):
        instr.append('--rd (RenderDoc bound)')
    for k, v in sorted(env.items()):
        if k in DIAG_KEYS or k.startswith(DIAG_PREFIX):
            if v not in ('', '0'):
                instr.append('%s=%s' % (k, v[:24]))
    if fl.get('--shader-validation') == 'true':
        instr.append('--shader-validation true')
    if fl.get('--vulkan-validation') == 'true':
        instr.append('--vulkan-validation true')
    b5f = []
    if env.get('KYTY_PIPELINE_PRECACHE') == '0':
        b5f.append('KYTY_PIPELINE_PRECACHE=0')
    if env.get('KYTY_PIPELINE_SALT'):
        b5f.append('KYTY_PIPELINE_SALT')
    if env.get('KYTY_S_REPLAY') in ('1', '2'):
        b5f.append('KYTY_S_REPLAY=' + env['KYTY_S_REPLAY'])
    if env.get('KYTY_CACHE_MODE') == 'prepare-cold':
        b5f.append('KYTY_CACHE_MODE=prepare-cold')
    if '/s288/s13/log_k_' in path or '/s288/s15/log_k_' in path:
        b5f.append('catalog collection arm k_')
    patch = bool(env.get('KYTY_GAME_PATCH')) or any(h.startswith('GamePatch') for h in heads) or \
        ('patch sha256' in ((meta or {}).get('times') or ''))
    knobs = sorted('%s=%s' % (k, v[:16]) for k, v in env.items()
                   if k.startswith('KYTY_') and k not in ('KYTY_FRAME_TRACE', 'KYTY_QUEUE_TRACE', 'KYTY_GPU_CLOCK_PIN',
                                                         'KYTY_GPU_MARKERS', 'KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE',
                                                         'KYTY_GPU_HANG_ABORT_S', 'KYTY_REC', 'KYTY_GUEST_ARGS', 'KYTY_KEYS',
                                                         'KYTY_GAME_PATCH'))
    return {'instr': instr, 'b5f': b5f, 'patch': patch, 'knobs': knobs, 'keys': bool(env.get('KYTY_KEYS'))}


def host_load(iv, dt):
    for x in iv.get('diagb32', []):
        kv = dict((k, int(v)) for k, v in RE_KV.findall(x))
        if 'other_us' in kv and 'ncpu' in kv and kv['other_us'] >= THETA_LOAD * kv['ncpu'] * dt:
            return 'other_us=%d ncpu=%d' % (kv['other_us'], kv['ncpu'])
    return None


def classify(row, form):
    iv = row['iv']
    dt = row['dt_us']
    fires = []
    tr = iv['ir'] + iv['gcn'] + iv['skip'] + iv.get('held', 0)
    if tr:
        fires.append(('B5', '%s: ir %d gcn %d skipped_draw %d held %d' % ('cold' if row['tr_win'] > 0 else 'hold', iv['ir'],
                                                                           iv['gcn'], iv['skip'], iv.get('held', 0))))
    big = [p for p in iv['pcs'] if p[1] >= 0.5 * (dt - VBLANK)]
    if big:
        default_form = not form['instr'] and not form['b5f'] and not form['patch'] and \
            not any(k.startswith('KYTY_POKE') for k in form['knobs'])
        fires.append(('B33', 'save %d us at line %d%s' % (big[0][1], big[0][0], ' reopen' if (not tr and default_form) else '')))
    if iv['pause_on'] or any(('lost keyboard focus' in x) or ('will_enter_background' in x) for x in iv['win_ex']):
        fires.append(('PAUSE', '; '.join(x for x in iv['win_ex'] if ('Pause' in x or 'focus' in x or 'background' in x))[:160]))
    if form['instr']:
        fires.append(('INSTR', ', '.join(form['instr'])))
    if form['b5f']:
        fires.append(('B5F', ', '.join(form['b5f'])))
    h = host_load(iv, dt)
    if h:
        fires.append(('HOST', h))
    if row['level'] in B32_LEVELS:
        fires.append(('B32', row['level']))
    if not fires:
        fires.append(('NONE', ''))
    return fires


def main():
    d = json.load(open(sys.argv[1], encoding='utf-8'))
    meta = json.load(open(sys.argv[2], encoding='utf-8'))
    out = sys.argv[3]
    forms = {p: form_of(p, meta.get(p), h) for p, h in d['heads'].items()}
    cnt = collections.Counter()
    cnt_cls = collections.Counter()
    rows = sorted(d['rows'], key=lambda r: (r['path'], r['line']))
    hdr = ['level', 'build', 'tag', 'n', 'dt_us', 'cls', 'idx', 'warm', 'attr', 'basis', 'also', 'patch', 'knobs', 'prio_max_us',
           'path:line']
    lines = [TAB.join(hdr)]
    for r in rows:
        f = forms[r['path']]
        fires = classify(r, f)
        warm = r['tr_win'] == 0 and r['tr_hold_before'] == 0
        tag = r['path'].split('/')[-1] if not r['path'].endswith('/log.txt') else r['path'].split('/')[-2]
        tag = tag.replace('log_', '').replace('.txt', '')
        lines.append(TAB.join([r['level'], r['build'], tag, str(r['n']), str(r['dt_us']), r['cls'], str(r['idx']),
                               'warm' if warm else 'not_warm', fires[0][0], fires[0][1], ','.join(x[0] for x in fires[1:]),
                               'patch' if f['patch'] else '', ' '.join(f['knobs'])[:120], str(r['iv']['prio_max']),
                               '%s:%d' % (r['path'], r['line'])]))
        cnt[fires[0][0]] += 1
        cnt_cls[(r['cls'], fires[0][0])] += 1
    with open(out, 'w', encoding='utf-8', newline=NL) as o:
        o.write(NL.join(lines) + NL)
    print('frames', len(rows), 'by attr', dict(sorted(cnt.items())), 'by cls/attr', dict(sorted(cnt_cls.items())))
    return rows, forms


if __name__ == '__main__':
    main()
