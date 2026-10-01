"""Session 144 step 0 (HPP-330): build sc144.py from C:/kyty/s143/sc143.py by exact replacements (each old text must occur
exactly once).  ASCII only, LF."""
import sys

SRC = 'C:/kyty/s143/sc143.py'
DST = 'C:/kyty/s144/sc144.py'
t = open(SRC, 'rb').read().decode('ascii')
assert '\r' not in t

HEAD = r'''#!/usr/bin/env python3
"""sc144.py - the scorer of the SCENE_OK series sc144 (session 144 step 0, HPP-330; ROADMAP "SESSION 122" item 254 (e),
(k)(1)-(7); brief docs/next-session-144.md): the port of sc143.py (session 143 step 0 HPP-297, link 1b HPP-321) with the
reading of sc143.py after items 242, 246 and NO change of its constants.  Profiles: 144 (the default), 143 (P143: prints
exactly what sc143.py printed - the regression on the 20 logs of s143, --regress143) and 142 (P142: --regress142).
Session 144 (item 254 (k)(1)-(2)), 33 tags in this order, one call each:
  w144_00          the control W on Sky Garden (underwater_aerial_garden); it is no SCENE_OK pair (Sky Garden has its
                   SCENE_OK of s142) - its rows decide the control stop of item 254 (k)(4);
  w144_01..w144_08 the W of the eight sc143 levels whose V rows passed (spring_punch_sky_aztec, booster_construction,
                   mini_astro_clock_tower, path_maker_mana_tree, spring_punch_monster_cave, gulliver_island,
                   booster_magic_lamp, rocket_space_station); the V of each pair is v143_NN of SESSION 143 (v143_01..06,
                   v143_09, v143_10), read from C:/kyty/s143 with the chain name go143a, the seal pred/02_sc143.md (its
                   sha256 now) and the log sha256 against C:/kyty/s143/step2/times.txt (item 254 (e): the cross-session
                   pair); its sheet row is "viewed" by item 254 (a) whatever --sheet says;
  v144_NN/w144_NN  NN = 09..20, V then W per level: rocket_hourglass, pot_treasure_cave, bumper_enemy_snowy_canyon,
                   big_hand_pirate_island, timestop_casino, ice_iceberg, sponge_dirty_bath, hoover_beach,
                   volcano_mountain, voxel_world, enemy_gorilla, mini_giants_garden (last).  These V are REPEATED
                   entries (item 254 (k)(2)): the census (map rows, forms B5 / B5a / B33) of this profile reads them only
                   and is printed with the mark "repeated entry", apart from the cold entries of s142 / s143.
The W form (item 254 (e)): every W runs with --vulkan-validation true AND KYTY_PIPELINE_PRECACHE=0.  The scorer checks it
by a positive control in the admission of every tag of profile 144: a W needs KYTY_PIPELINE_PRECACHE=0 in its json env
and NO line "PipelinePrecache: <N> recipes ->" in its log and emulator stdout (the stdout is the executor's addition);
a V needs no KYTY_PIPELINE_PRECACHE in its env and >= 1 such line in its log.  A violation fails the admission of the tag
(the tag FAILs: rc 1 of --tag, its SCENE_OK NO).  Note: a W stopped DURING the startup precache has no such line either
(the w143 logs) - the env term is what tells the form there.
Stop rules (item 254 (k)(4)), --stop-check <tag> rc 5:
  control  the control W w144_00 was made and stopped: by the letter a death marker (log, stdout, hold_exit / ENDED /
           exited) or a [Vulkan][E] line; the executor's reading stops on ANY failing W row of SCENE_OK or of its
           admission (the W form is item 254 (k)(7): "the cost of a form error is a stop after one tag"), on a missing
           log and on an attempt without json - both readings are printed, the gate uses the executor's (a stop is a
           question to the lead, never a run);
  W        two W in a row (the made W tags of SEQ, control included, V in between ignored) with the same stop key: the
           key of a W stopped before the first line carrying "GuestOut" = "<class> <kind>" of its first death marker in
           the order of item 224 (a)(1) among the log markers before that line (no such line in the log: every marker,
           then hold_exit / ENDED / exited); a W without such a stop (it reached the game, or stopped without a marker)
           has no key and breaks the run;
  V        three census V in a row NOT_ENTERED with one marker (item 221 (g)(4), as sc143).
  --stop-check reads the control W, the last two made W and the last three made census V before the tag (an earlier
  stop refused the call right after it, and the order rule of go144a.sh refuses every later call).
"Frame with a skipped draw" = the number of DISTINCT frame= ids of the "AsyncPipelines: skipped draw" lines (debt D-7).
Usage (profile 144; ASCII output; logs read in binary chunks):
    python sc144.py --tag <tag>                                 score one run (json in runs144/<tag>.score.json)
    python sc144.py --summary [--sheet viewed|not-viewed] [--sheet-tags v144_09,...]
    python sc144.py --stop-check <tag>                          rc 5 when a stop rule of item 254 (k)(4) stands
    python sc144.py --check-seal                                every sha line of pred/01_sc144.md against its file
    python sc144.py --calib | --check1b                         as sc143.py
    python sc144.py --regress143                                profile 143 on the 20 s143 logs against summary143_viewed.txt
    python sc144.py --regress142                                profile 142 on the 12 s142 logs against summary142_viewed.txt
Session 143 header (carried; profile 143):
sc143.py - the scorer of the SCENE_OK series sc143 (session 143 step 0, HPP-297;'''

R = []


def rep(old, new):
    R.append((old, new))


rep('#!/usr/bin/env python3\n"""sc143.py - the scorer of the SCENE_OK series sc143 (session 143 step 0, HPP-297;', HEAD)

rep(r'''ROOT = 'C:/kyty/s143'
PRED_PATH = 'C:/kyty/s143/pred/02_sc143.md'
CHAIN = 'go143a'
RUNS = 'runs143'
SCORER = 'sc143.py'
EXTRA = True
BUILD_SHA = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
LEVELS = ('spring_punch_sky_aztec', 'booster_construction', 'mini_astro_clock_tower', 'path_maker_mana_tree',
          'spring_punch_monster_cave', 'gulliver_island', 'rocket_hourglass', 'pot_treasure_cave', 'booster_magic_lamp',
          'rocket_space_station')
PAIRS = tuple(('v143_%02d' % (i + 1), 'w143_%02d' % (i + 1), lv) for i, lv in enumerate(LEVELS))
CENSUS = tuple((v, lv) for v, _, lv in PAIRS)
SEQ = tuple(t for v, w, _ in PAIRS for t in (v, w))
V_TAGS = tuple(v for v, _, _ in PAIRS)
W_TAGS = tuple(w for _, w, _ in PAIRS)
SEALED_NAMES = ('go143a.sh', 'sc143.py', 'test_sc143.py', 'mut_sc143.py', 'enter_scene.py',
                'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py',
                'test_go143a.py', 'fgcpu143.py', 'test_fgcpu143.py', 'C:/kyty/scripts/s51_vidglitch.py',
                'cachemf143.py', 'lockcheck143.py', 'test_tools143.py', 'step2/next_one.sh', 'step2/call_one.sh',
                'step2/wait_one.sh')
CACHE_ROOTS = ('shader', 'pipeline', 'glcache')
VSTOP = 'VALIDATION_STOP'
SKY = 'underwater_aerial_garden'
''', r'''ROOT = 'C:/kyty/s144'
PRED_PATH = 'C:/kyty/s144/pred/01_sc144.md'
CHAIN = 'go144a'
RUNS = 'runs144'
SCORER = 'sc144.py'
EXTRA = True
FORM144 = True
BUILD_SHA = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
SKY = 'underwater_aerial_garden'
LEVELS143 = ('spring_punch_sky_aztec', 'booster_construction', 'mini_astro_clock_tower', 'path_maker_mana_tree',
             'spring_punch_monster_cave', 'gulliver_island', 'rocket_hourglass', 'pot_treasure_cave', 'booster_magic_lamp',
             'rocket_space_station')
OLD143 = (('v143_01', 'spring_punch_sky_aztec'), ('v143_02', 'booster_construction'), ('v143_03', 'mini_astro_clock_tower'),
          ('v143_04', 'path_maker_mana_tree'), ('v143_05', 'spring_punch_monster_cave'), ('v143_06', 'gulliver_island'),
          ('v143_09', 'booster_magic_lamp'), ('v143_10', 'rocket_space_station'))
NEW144 = ('rocket_hourglass', 'pot_treasure_cave', 'bumper_enemy_snowy_canyon', 'big_hand_pirate_island', 'timestop_casino',
          'ice_iceberg', 'sponge_dirty_bath', 'hoover_beach', 'volcano_mountain', 'voxel_world', 'enemy_gorilla',
          'mini_giants_garden')
CONTROL = ('w144_00', SKY)
PAIRS = tuple((v, 'w144_%02d' % (i + 1), lv) for i, (v, lv) in enumerate(OLD143)) + tuple(
    ('v144_%02d' % (i + 9), 'w144_%02d' % (i + 9), lv) for i, lv in enumerate(NEW144))
LEVELS = tuple(lv for _, _, lv in PAIRS)
CENSUS = tuple((v, lv) for v, _, lv in PAIRS[len(OLD143):])
SEQ = (CONTROL[0],) + tuple(w for _, w, _ in PAIRS[:len(OLD143)]) + tuple(
    t for v, w, _ in PAIRS[len(OLD143):] for t in (v, w))
V_TAGS = tuple(v for v, _, _ in PAIRS)
W_TAGS = (CONTROL[0],) + tuple(w for _, w, _ in PAIRS)
ROOT143 = 'C:/kyty/s143'
PRED143 = 'C:/kyty/s143/pred/02_sc143.md'
XSRC = dict((v, dict(root=ROOT143, chain='go143a', pred=PRED143)) for v, _ in OLD143)
XSHEET = tuple(v for v, _ in OLD143)
SEALED_NAMES = ('go144a.sh', 'sc144.py', 'test_sc144.py', 'mut_sc144.py', 'enter_scene.py',
                'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py',
                'test_go144a.py', 'fgcpu144.py', 'test_fgcpu144.py', 'C:/kyty/scripts/s51_vidglitch.py',
                'cachemf144.py', 'lockcheck144.py', 'test_tools144.py', 'step2/next_one.sh', 'step2/call_one.sh',
                'step2/wait_one.sh', 'step2/apichk144.py', 'C:/kyty/s143/step2/times.txt', 'C:/kyty/s143/pred/02_sc143.md')
SEALED143 = ('go143a.sh', 'sc143.py', 'test_sc143.py', 'mut_sc143.py', 'enter_scene.py',
             'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py',
             'test_go143a.py', 'fgcpu143.py', 'test_fgcpu143.py', 'C:/kyty/scripts/s51_vidglitch.py',
             'cachemf143.py', 'lockcheck143.py', 'test_tools143.py', 'step2/next_one.sh', 'step2/call_one.sh',
             'step2/wait_one.sh')
CACHE_ROOTS = ('shader', 'pipeline', 'glcache')
VSTOP = 'VALIDATION_STOP'
W_STOP_RUN = 2
NUMW = {5: 'five', 6: 'six'}
PAIRS143 = tuple(('v143_%02d' % (i + 1), 'w143_%02d' % (i + 1), lv) for i, lv in enumerate(LEVELS143))
P143 = dict(ROOT=ROOT143, PRED_PATH=PRED143, CHAIN='go143a', RUNS='runs143', SCORER='sc143.py', EXTRA=True, FORM144=False,
            LEVELS=LEVELS143, PAIRS=PAIRS143, CENSUS=tuple((v, lv) for v, _, lv in PAIRS143),
            SEQ=tuple(t for v, w, _ in PAIRS143 for t in (v, w)), V_TAGS=tuple(v for v, _, _ in PAIRS143),
            W_TAGS=tuple(w for _, w, _ in PAIRS143), SEALED_NAMES=SEALED143, CONTROL=None, XSRC={}, XSHEET=(), HALF=5)
REGRESS143_FILE = 'C:/kyty/s143/step4/summary143_viewed.txt'
REGRESS143_B33 = ('v143_02', 'v143_07', 'v143_08', 'v143_09')
''')

rep(r'''            SEALED_NAMES=('go142a.sh', 'sc142.py', 'test_sc142.py', 'mut_sc142.py', 'enter_scene.py',
                          'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt',
                          'sheet142.py', 'test_go142a.py', 'C:/kyty/scripts/s51_vidglitch.py'))
''', r'''            SEALED_NAMES=('go142a.sh', 'sc142.py', 'test_sc142.py', 'mut_sc142.py', 'enter_scene.py',
                          'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt',
                          'sheet142.py', 'test_go142a.py', 'C:/kyty/scripts/s51_vidglitch.py'),
            FORM144=False, LEVELS=tuple(lv for _, lv in CENSUS142), CONTROL=None, XSRC={}, XSHEET=(), HALF=5)
''')

rep('HALF = 5\n', 'HALF = 6\n')

rep(r'''M_ENDED = b'WARNING: the game ENDED inside the hold'
''', r'''M_ENDED = b'WARNING: the game ENDED inside the hold'
M_GUEST = b'GuestOut'
M_PRECACHE = b'PipelinePrecache:'
RX_PRECACHE = re.compile(rb'PipelinePrecache: \d+ recipes ->')
''')

rep(r'''def level_of(tag):
    for v, w, lv in PAIRS:''', r'''def level_of(tag):
    if CONTROL is not None and tag == CONTROL[0]:
        return CONTROL[1]
    for v, w, lv in PAIRS:''')

rep(r'''               prio=[], bvh=[], vke=[], quit=None, ended=[], bytes=0, torn=0, noval=0, valfeat=0, vkany=0)
''', r'''               prio=[], bvh=[], vke=[], quit=None, ended=[], bytes=0, torn=0, noval=0, valfeat=0, vkany=0,
               guestout=None, precache=0, precache_any=0)
''')

rep(r'''            res['vkany'] += whole.count(M_VKANY)
''', r'''            res['vkany'] += whole.count(M_VKANY)
            res['precache'] += len(RX_PRECACHE.findall(whole))
            res['precache_any'] += whole.count(M_PRECACHE)
            if res['guestout'] is None:
                gi = whole.find(M_GUEST)
                if gi >= 0:
                    res['guestout'] = base + _line(whole, gi)[0]
''')

rep(r'''def sheet_state(root, tag):''', r'''def sheet_state(root, tag, chain=None):''')
rep(r'''        rs = re.compile(r'%s %s sheet rc \S+ sheet_%s\.png sha256 ([0-9a-f]{64})' % (CHAIN, tag, tag))
''', r'''        rs = re.compile(r'%s %s sheet rc \S+ sheet_%s\.png sha256 ([0-9a-f]{64})' % (chain or CHAIN, tag, tag))
''')
rep(r'''                        % (CHAIN, tag, tag, tag))
''', r'''                        % (chain or CHAIN, tag, tag, tag))
''')

rep('def admit(tag, js, pred_sha):\n', 'def admit(tag, js, pred_sha, pred_path=None):\n')
rep(r'''        and (pr.get('path') or '').replace('\\', '/') == PRED_PATH, (pr.get('sha256') or '')[:8])
    add('no pipeline-cache retry', not any(a.get('pipeline_cache_off') for a in at), '')
    return rows
''', r'''        and (pr.get('path') or '').replace('\\', '/') == (pred_path or PRED_PATH), (pr.get('sha256') or '')[:8])
    add('no pipeline-cache retry', not any(a.get('pipeline_cache_off') for a in at), '')
    if FORM144:
        pc = env.get('KYTY_PIPELINE_PRECACHE')
        if is_w:
            add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc == '0', pc)
        else:
            add('V shipped defaults: no KYTY_PIPELINE_PRECACHE in the env (item 254 (k)(2))', pc is None, pc)
    return rows
''')

rep('def build(tag, lv, js, log, std, es, root, pred_sha):\n',
    'def build(tag, lv, js, log, std, es, root, pred_sha, pred_path=None, chain=None):\n')
rep("             admit=admit(tag, js, pred_sha), guest_args=js.get('guest_args'))\n",
    "             admit=admit(tag, js, pred_sha, pred_path), guest_args=js.get('guest_args'))\n")
rep("    r['times_log_sha'] = times_log_sha(root, tag) if EXTRA else None\n",
    "    r['times_log_sha'] = times_log_sha(root, tag, chain) if EXTRA else None\n")
rep(r'''    r['rows_total'] = len(log['rows']) if log is not None else 0
''', r'''    if FORM144:
        pl = log['precache'] if log is not None else None
        ps = std['precache'] if std is not None else 0
        r['precache'] = dict(log=pl, stdout=ps, any=None if log is None else log['precache_any'] + (
            std['precache_any'] if std is not None else 0))
        if tag in W_TAGS:
            r['admit'].append(('W form: no "PipelinePrecache: N recipes ->" line in the log (item 254 (e))', pl == 0,
                               'log %s' % pl))
        else:
            r['admit'].append(('V positive control: >= 1 "PipelinePrecache: N recipes ->" line in the log (item 254 (e))',
                               pl is not None and pl >= 1, 'log %s' % pl))
        r['guestout'] = log['guestout'] if log is not None else None
        r['wkey'] = None
    r['rows_total'] = len(log['rows']) if log is not None else 0
''')
rep("    r['sheet'] = sheet_state(root, tag) if tag in V_TAGS else None\n",
    "    r['sheet'] = sheet_state(root, tag, chain) if tag in V_TAGS else None\n")
rep(r'''    r['outcome120'] = outcome120(r) if EXTRA and tag not in W_TAGS else None
    return r
''', r'''    r['outcome120'] = outcome120(r) if EXTRA and tag not in W_TAGS else None
    if FORM144 and tag in W_TAGS:
        r['wkey'] = w_stop_key(r)
    return r
''')

rep('def times_log_sha(root, tag):\n', 'def times_log_sha(root, tag, chain=None):\n')
rep(r'''    rx = re.compile(r'%s %s enter_scene end rc \S+ log_%s\.txt sha256 ([0-9a-f]{64})' % (CHAIN, tag, tag))
''', r'''    rx = re.compile(r'%s %s enter_scene end rc \S+ log_%s\.txt sha256 ([0-9a-f]{64})' % (chain or CHAIN, tag, tag))
''')

rep(r'''    """Everything the scorer reads about one run; None when the run was not made (no <tag>.json)."""
    lv = level_of(tag)
    jp = os.path.join(root, '%s.json' % tag)
''', r'''    """Everything the scorer reads about one run; None when the run was not made (no <tag>.json).  A V of another
    session (XSRC, profile 144: the v143_NN of the cross-session pairs, item 254 (e)) is read from ITS root with ITS seal
    (the sha256 of that seal now) and ITS chain name (the log and sheet sha lines of its step2/times.txt)."""
    lv = level_of(tag)
    x = XSRC.get(tag)
    pred_path = chain = None
    if x is not None:
        root, pred_path, chain = x['root'], x['pred'], x['chain']
        pred_sha = sha_file(pred_path) if os.path.isfile(pred_path) else None
    jp = os.path.join(root, '%s.json' % tag)
''')
rep('    return build(tag, lv, js, log, std, es, root, pred_sha)\n',
    '    return build(tag, lv, js, log, std, es, root, pred_sha, pred_path, chain)\n')

rep(r'''            'enter_scene end line of step2/times.txt)' % (vt, wt, want),
''', r'''            'enter_scene end line of step2/times.txt%s)' % (vt, wt, want, ' of its own session; item 254 (e)' if FORM144
                                                             else ''),
''')
rep(r'''    rows.append(('sheet of V viewed by the lead (filled by the close)', sheet == 'viewed', sheet or 'UNSET'))
''', r'''    rows.append(('sheet of V viewed by the lead (filled by the close)', sheet == 'viewed', (sheet or 'UNSET') + (
        ' (item 254 (a): viewed at the close of s143)' if vt in XSHEET else '')))
''')

NEWFUN = r'''def w_stop_key(r):
    """Item 254 (k)(4): the stop key of a W stopped before the first line carrying "GuestOut" - "<class> <kind>" of its
    first death marker in the order of item 224 (a)(1) among the log markers before that line (no such line in the log:
    every marker of the log and the stdout, then hold_exit / ENDED / exited); None when the W did not stop there (it
    reached the game, or stopped without a marker) or has no log."""
    if not r['log_present']:
        return None
    g = r.get('guestout')
    ms = [m for m in r['marks'] if g is None or (m['src'] == 'log' and m['pos'] < g)]
    if ms:
        return '%s %s' % (ms[0]['cls'], ms[0]['kind'])
    if g is None and (r['ended'] or r['exited']):
        return 'K1 hold_exit / ENDED / exited'
    return None


def stop_check_w(keys):
    """Item 254 (k)(4): two W in a row (the made W tags of SEQ in order) with one stop key -> stop.  keys: [(tag, key)];
    a W without a key (or an attempt without json) breaks the run; returns (stop, tags)."""
    run = []
    for tag, key in keys:
        if key is None:
            run = []
            continue
        if run and run[-1][1] != key:
            run = []
        run.append((tag, key))
        if len(run) >= W_STOP_RUN:
            return True, [t for t, _ in run[-W_STOP_RUN:]]
    return False, []


def control_state(e, no_json=False):
    """Item 254 (k)(4): the control W.  Returns (gate stop, letter stop, reasons of the letter, reasons of the executor).
    The letter: a death marker (log, stdout, hold_exit / ENDED / exited) or a [Vulkan][E] line.  The executor's reading
    (the gate): the letter, or any failing W row of SCENE_OK or of its admission (the W form: item 254 (k)(7)), or a
    missing log, or an attempt made without json."""
    if e is None:
        if no_json:
            return True, False, [], ['attempt made without json (instrument)']
        return False, False, [], []
    letter = []
    if e['marks']:
        letter.append('death marker %s' % ';'.join('%s %s' % (m['cls'], m['kind']) for m in e['marks']))
    if e['ended'] or e['exited']:
        letter.append('hold_exit / ENDED / exited')
    if e.get('vke'):
        letter.append('[Vulkan][E] %d' % e['vke'])
    rows = [x for x in scene_ok(None, e, None, (None, e['tag'], e['level']))[1] if x[0].startswith('W ')]
    execu = ['%s (%s)' % (x[0], x[2]) for x in rows if not x[1]]
    if not e['log_present']:
        execu.append('log missing')
    return bool(letter) or bool(execu), bool(letter), letter, execu


def made(t, root):
    """A call of the tag was made: its json or its attempt marker exists."""
    return os.path.isfile(os.path.join(root, '%s.json' % t)) or attempt_marker(t, root)


def stop_check144(tag, root, pred_sha):
    """Item 254 (k)(4) before the call of tag: (stop, lines).  Reads the control W, the last W_STOP_RUN made W and the
    last STOP_RUN made census V before the tag."""
    before = list(SEQ[:SEQ.index(tag)])
    lines = []
    stop = False
    c = CONTROL[0]
    if c in before:
        e = entry_of(c, root, pred_sha)
        gate, let, lr, xr = control_state(e, e is None and attempt_marker(c, root))
        lines.append('STOP RULE CONTROL before %s: %s; letter %s (%s); executor reading [I] (the gate) %s (%s)' % (
            tag, 'STOP' if gate else ('not made' if e is None else 'not met'), 'stop' if let else 'pass',
            '; '.join(lr) or 'none',
            'stop' if gate else 'pass', '; '.join(xr) or 'none'))
        stop = stop or gate
    ws = [t for t in before if t in W_TAGS and made(t, root)]
    keys = []
    for t in ws[-W_STOP_RUN:]:
        e = entry_of(t, root, pred_sha)
        keys.append((t, e['wkey'] if e is not None else None))
    sw, tw = stop_check_w(keys)
    lines.append('STOP RULE W before %s (two W in a row stopped before the first GuestOut line with one key): %s; keys %s'
                 % (tag, ('STOP ' + ','.join(tw)) if sw else 'not met', ', '.join('%s %s' % k for k in keys) or 'none'))
    stop = stop or sw
    vs = [t for t, _ in CENSUS if t in before and made(t, root)]
    oc = []
    for t in vs[-STOP_RUN:]:
        e = entry_of(t, root, pred_sha)
        oc.append((t, e['outcome'], e['key']) if e is not None else (t, 'ATTEMPT_NO_JSON', None))
    sv, tv = stop_check(oc)
    lines.append('STOP RULE before %s: %s' % (tag, ('STOP ' + ','.join(tv)) if sv else 'not met'))
    stop = stop or sv
    return stop, lines


def fmt_entry(r):
'''
rep('def fmt_entry(r):\n', NEWFUN)

rep(r'''        o.append('  AsyncPipelines skipped draw: %d lines, %d frames (counted, not fatal)' % (r['skip']['lines'],
                                                                                         r['skip']['frames']))
''', r'''        o.append('  AsyncPipelines skipped draw: %d lines, %d frames (%scounted, not fatal)' % (
            r['skip']['lines'], r['skip']['frames'], 'distinct frame= ids, debt D-7; ' if FORM144 else ''))
''')
rep(r'''             % (vl['noval'], vl['valfeat'], vl['vkany'], 'yes' if vl['ok'] else 'no'))
''', r'''             % (vl['noval'], vl['valfeat'], vl['vkany'], 'yes' if vl['ok'] else 'no'))
    if FORM144:
        pc = r.get('precache') or {}
        o.append('  precache form (item 254 (e)): "PipelinePrecache: N recipes ->" lines log %s; executor member [I] (item '
                 '258 (d), not in the verdict): the same line in the emulator stdout %s, any "PipelinePrecache:" line %s' % (
                     pc.get('log'), pc.get('stdout'), pc.get('any')))
        if r['tag'] in W_TAGS:
            o.append('  W stop before the first GuestOut line (item 254 (k)(4)): first GuestOut at %s; stop key %s' % (
                r.get('guestout'), r.get('wkey') or 'none'))
''')

# summary
rep(r'''            out.append('TAG %s: not made' % t)
    words = []
    for vt, wt, lv in PAIRS:
        sh = sheet if (sheet_tags is None or vt in sheet_tags) else None
''', r'''            out.append('TAG %s: not made' % t)
    for t in XSRC:
        ents[t] = entry_of(t, root, pred_sha)
        x = XSRC[t]
        if ents[t] is not None:
            out.append('V OF ANOTHER SESSION %s (the pair of item 254 (e); root %s, chain %s, seal %s):' % (
                t, x['root'], x['chain'], x['pred']))
            out.extend(fmt_entry(ents[t]))
        else:
            out.append('TAG %s (V of another session, root %s): NO JSON' % (t, x['root']))
    words = []
    for vt, wt, lv in PAIRS:
        sh = 'viewed' if vt in XSHEET else (sheet if (sheet_tags is None or vt in sheet_tags) else None)
''')
rep(r'''            words.count('YES'), words.count('PENDING_SHEET'), words.count('NO'), len(PAIRS)))
''', r'''            words.count('YES'), words.count('PENDING_SHEET'), words.count('NO'), len(PAIRS)))
    if FORM144:
        c = CONTROL[0]
        gate, let, lr, xr = control_state(ents[c], c in nojs)
        out.append('CONTROL W %s (%s, item 254 (k)(4)): %s; letter (death marker or [Vulkan][E]) %s (%s); executor '
                   'reading [I] (any W row or admission row failing; the gate) %s (%s)' % (
                       c, CONTROL[1], 'not made' if ents[c] is None and c not in nojs else ('STOP' if gate else 'PASS'),
                       'stop' if let else 'pass', '; '.join(lr) or 'none', 'stop' if gate else 'pass',
                       '; '.join(xr) or 'none'))
        vm = [t for t in V_TAGS if ents.get(t) is not None]
        wm = [t for t in W_TAGS if ents.get(t) is not None]
        vbad = [t for t in vm if not all(a[1] for a in ents[t]['admit'] if a[0].startswith(('V positive', 'V shipped')))]
        wbad = [t for t in wm if not all(a[1] for a in ents[t]['admit'] if a[0].startswith('W form'))]
        wstd = [t for t in wm if (ents[t].get('precache') or {}).get('stdout')]
        out.append('W FORM (item 254 (e)): V with the "PipelinePrecache: N recipes ->" line and no KYTY_PIPELINE_PRECACHE '
                   '%d of %d made; W with KYTY_PIPELINE_PRECACHE=0 and no such line in the log %d of %d made; violated: %s; '
                   'executor member [I] (item 258 (d), not in the verdict; a hit is a question to the lead): W with the line '
                   'in the emulator stdout: %s' % (len(vm) - len(vbad), len(vm), len(wm) - len(wbad), len(wm),
                                                    ','.join(vbad + wbad) or 'none', ','.join(wstd) or 'none'))
''')
rep(r'''    out.append('CENSUS made %d of %d (of them attempt made without json %d), admitted %d' % (
''', r'''    if FORM144:
        out.append('CENSUS = the V tags %s..%s, REPEATED entries (item 254 (k)(2)): the map rows and the forms B5 / B5a / B33 '
                   'below are of repeated entries, apart from the cold entries of s142 / s143' % (CENSUS[0][0],
                                                                                                   CENSUS[-1][0]))
    out.append('CENSUS made %d of %d (of them attempt made without json %d), admitted %d' % (
''')
rep(r'''                out.append('    map (A) row %s: outcome on 120 s %s (%s); outcome on the whole V %s (%s)' % (
                    e['level'], e['outcome120'][0], e['outcome120'][1], e['outcome'], e['reason']))
''', r'''                out.append('    map (A) row %s%s: outcome on 120 s %s (%s); outcome on the whole V %s (%s)' % (
                    e['level'], ' (repeated entry)' if FORM144 else '', e['outcome120'][0], e['outcome120'][1],
                    e['outcome'], e['reason']))
''')
rep(r'''    out.append('FORMS second reading by the order (shared caches warm from earlier runs): first five B5a %d/5 B5 %d/5; '
               'last five B5a %d/5 B5 %d/5' % (fa, fb, la, lb))
''', r'''    nf, nl = HALF, len(CENSUS) - HALF
    out.append('FORMS second reading by the order (shared caches warm from earlier runs): first %s B5a %d/%d B5 %d/%d; '
               'last %s B5a %d/%d B5 %d/%d' % (NUMW.get(nf, nf), fa, nf, fb, nf, NUMW.get(nl, nl), la, nl, lb, nl))
''')
rep(r'''    stop, tags = stop_check(oc)
    out.append('STOP RULE (item 221 (g)(4)): %s' % (('STOP ' + ','.join(tags)) if stop else 'not met'))
''', r'''    stop, tags = stop_check(oc)
    if FORM144:
        keys = [(t, ents[t]['wkey'] if ents[t] is not None else None) for t in SEQ
                if t in W_TAGS and (ents[t] is not None or t in nojs)]
        sw, tw = stop_check_w(keys)
        out.append('STOP RULE W (item 254 (k)(4): two W in a row stopped before the first GuestOut line with one key): %s; '
                   'keys %s' % (('STOP ' + ','.join(tw)) if sw else 'not met',
                                ', '.join('%s %s' % k for k in keys if k[1] is not None) or 'none'))
    out.append('STOP RULE (item 221 (g)(4)): %s' % (('STOP ' + ','.join(tags)) if stop else 'not met'))
''')

REG143 = r'''def regress143(expect=REGRESS143_FILE):
    """Item 254 (k)(5): profile 143 on the 20 logs of s143; the summary with the sheet row viewed must equal the lead's
    file byte for byte (CRLF, the form the scorer of s143 printed into it), and B33 by the letter must be the four V of
    item 254 (g)(4).  Returns (ok, lines)."""
    old = profile(P143)
    try:
        pred_sha = sha_file(PRED_PATH) if os.path.isfile(PRED_PATH) else None
        out, ents, _ = summary(ROOT, pred_sha, 'viewed')
        adm = [ents[t] for t, _ in CENSUS if ents[t] is not None and all(a[1] for a in ents[t]['admit'])]
        b33, b33v, b33t = form_b33(adm)
    finally:
        profile(old)
    lines = []
    raw = open(expect, 'rb').read() if os.path.isfile(expect) else b''
    new = ('\r\n'.join(out) + '\r\n').encode('ascii', 'replace')
    a = raw.decode('ascii', 'replace').replace('\r\n', '\n').split('\n')
    if a and a[-1] == '':
        a = a[:-1]
    diff = [(i + 1, a[i] if i < len(a) else '<none>', out[i] if i < len(out) else '<none>')
            for i in range(max(len(a), len(out))) if (a[i] if i < len(a) else None) != (out[i] if i < len(out) else None)]
    same = raw == new and bool(raw)
    lines.append('REGRESS143 expected %s sha256 %s lines %d; new lines %d sha256 %s; byte-identical %s; differing lines %d'
                 % (expect, hashlib.sha256(raw).hexdigest(), len(a), len(out), hashlib.sha256(new).hexdigest(),
                    'yes' if same else 'NO', len(diff)))
    for i, x, y in diff[:40]:
        lines.append('DIFF line %d expected: %s' % (i, x))
        lines.append('DIFF line %d new:      %s' % (i, y))
    b33ok = tuple(b33t) == REGRESS143_B33
    lines.append('REGRESS143 B33 (K3 on the hold, item 254 (g)(4)): %d/10 %s (expected %s) -> %s; executor variant 120 s: '
                 '%d/10' % (b33, ','.join(b33t) or 'none', ','.join(REGRESS143_B33), 'PASS' if b33ok else 'FAIL', b33v))
    ok = same and b33ok
    lines.append('REGRESS143: %s' % ('PASS' if ok else 'FAIL'))
    return ok, lines


def calib():
'''
rep('def calib():\n', REG143)

rep(r'''    ap.add_argument('--regress142', action='store_true')
''', r'''    ap.add_argument('--regress142', action='store_true')
    ap.add_argument('--regress143', action='store_true')
''')
rep(r'''    if a.regress142:
        ok, lines = regress142()
        print('\n'.join(lines))
        return 0 if ok else 1
''', r'''    if a.regress142:
        ok, lines = regress142()
        print('\n'.join(lines))
        return 0 if ok else 1
    if a.regress143:
        ok, lines = regress143()
        print('\n'.join(lines))
        return 0 if ok else 1
''')
rep(r'''            print('usage: unknown tag %s' % a.stop_check)
            return 2
''', r'''            print('usage: unknown tag %s' % a.stop_check)
            return 2
        if FORM144:
            stop, lines = stop_check144(a.stop_check, root, pred_sha)
            print('\n'.join(lines))
            return 5 if stop else 0
''')
rep(r'''    print('usage: sc143.py --tag T | --summary | --stop-check T | --check-seal | --calib | --check1b | --regress142')
''', r'''    print('usage: sc144.py --tag T | --summary | --stop-check T | --check-seal | --calib | --check1b | --regress142 | '
          '--regress143')
''')

for old, new in R:
    n = t.count(old)
    if n != 1:
        print('ANCHOR COUNT %d: %r' % (n, old[:120]))
        sys.exit(1)
    t = t.replace(old, new)
t.encode('ascii')
open(DST, 'wb').write(t.encode('ascii'))
print('mk_sc144: %d replacements, %d bytes' % (len(R), len(t)))
