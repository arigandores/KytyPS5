"""port_sc146.py - session 146 step 0 (HPP-386): builds C:/kyty/s146/sc146.py from C:/kyty/s145/sc145.py by anchored
replacements (each anchor must occur exactly once).  Profile 145 keeps the code of sc145 (every new behaviour sits behind
FORM146); profile 146 is the module default.  Writes LF bytes, ASCII only.  Prints the sha256 of source and target."""
import hashlib
import sys

SRC = 'C:/kyty/s145/sc145.py'
DST = 'C:/kyty/s146/sc146.py'
t = open(SRC, 'rb').read().decode('ascii')
assert '\r' not in t
R = []


def rep(old, new, count=1):
    n = t.count(old)
    if n != count:
        print('ANCHOR %d != %d: %r' % (n, count, old[:120]))
        sys.exit(1)
    R.append(old[:60])
    return t.replace(old, new)


# ---- 1. header
t = rep('#!/usr/bin/env python3\n"""sc145.py - the scorer of the SCENE_OK series sc145', '''#!/usr/bin/env python3
"""sc146.py - the scorer of the SCENE_OK series sc146 (session 146 step 0, HPP-386; ROADMAP "SESSION 122" item 309 (k), (l)(1)-(7),
item 300 (b)(4), item 281 (g), item 295; brief docs/next-session-146.md): the port of sc145.py with NO change of its constants
(item 309 (l)(4)).  Profiles: 146 (the default), 145 (P145: prints exactly what sc145.py printed - the regression on the 33 logs
of s145, --regress145), 144, 143, 142 (as in sc145.py).
Session 146 (item 309 (l)(2)), 35 tags in this order, one call each, all on the INSTALLED track F shipment binary dac02fb9:
  w146_00          the control W on Sky Garden (underwater_aerial_garden) in the form of item 300 (b)(4): --vulkan-validation
                   true, precache by default (no KYTY_PIPELINE_PRECACHE), VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, no
                   VK_LAYER_MESSAGE_ID_FILTER; a letter term of its stop (beside the terms of sc145): a line "DualSrcBlend:
                   supported=1 enabled=1" before the first GuestOut line (item 300 (b)(4)); with the warm-up V i146_v of step 0
                   (score_i146_v.txt) it is printed as the Sky Garden line of item 300 (d) - information for the lead;
  r146_01..r146_03 V of the re-check of an accepted SCENE_OK (item 300 (g), 309 (l)(2)): hoover_beach, sponge_dirty_bath,
                   timestop_casino - a V only; its row "RECHECK <level>: PASSES / REMOVES SCENE_OK / PENDING_SHEET" reads the V
                   rows of SCENE_OK (item 221 (g)(3)) and the lead's sheet row;
  r146_04          the second hold V of bonus_path_maker_mix (p of B40) - a V only; its row prints the K2 frames of the hold;
  v146_NN/w146_NN  NN = 05..19, V then W of the 15 never-entered scene levels of the list of step 0 (step0/lvl146.py, accepted
                   by the lead): robot_builder_next, interactive_credit_00, non_interactive_credit, ending_boss_after_credit,
                   collectible_viewer, hub_crashsite_diorama, diorama_controller_skin, diorama_astro_skin, diorama_zoo,
                   fragile_battle_1, voxel_challenge_1, armadillo_challenge_1, fragile_battle_2, voxel_challenge_2,
                   fragile_battle_3; the V are COLD first entries (census, pools); SCENE_OK by the pair of one session on
                   dac02fb9 (no pair with a W of 9235a7ac).  The W of a pair is NOT called when its V is NOT_ENTERED (item 309
                   (k)(1)): the chain writes skipped_<w>.txt, the tag reads "SKIPPED_V_NOT_ENTERED" (not an attempt, not made).
Changes of profile 146 (FORM146), every one a data row unless named a form or a stop term:
  build            dac02fb9 (BUILD_SHA) in the admission of every tag;
  W form           item 300 (b)(4), 281 (g): no KYTY_PIPELINE_PRECACHE in the json env of a W (the admission row "W form on the
                   shipment binary"); the "PipelinePrecache: N recipes ->" lines of a W are a data row (not the admission row of
                   profile 144-145: the precache by default runs in every W);
  DualSrcBlend     the "DualSrcBlend: supported=S enabled=E" lines of every W and whether one "supported=1 enabled=1" lies before
                   the first GuestOut line (no GuestOut line: any such line) - a data row of every W (item 309 (l)(4)); a letter
                   term of the control stop (item 300 (b)(4)); beside it the reading of item 281 (g) ("none -> the tag FAIL")
                   is printed as the variant [I], not in the verdict;
  stubs (F13)      the lines "Unresolved import stub called" in the log and in the emulator stdout (the printf form);
  asserts (F14)    the lines with "ASSERT:" and with "user_msg_param" (log and stdout); != 0 - a row of the close in register F;
  tile events      D-4 of s145 (the auditor's tile rule, AUDIT145 s1.4: a 4x4 grid of 240x135 px tiles of the gray frame, a tile
                   event at frame i when the tile means t1 = |f[i]-f[i-1]| > 4, t2 = |f[i+1]-f[i]| > 4 and tb = |f[i+1]-f[i-1]|
                   < 0.35 min(t1, t2); threshold 4) - read from tiles_<V>.txt of tiles146.py (the chain), per V;
  stop rules       item 273 (k)(4) unchanged; the three-V rule reads every made V of SEQ (re-check, second hold and census V) in
                   order; --stop-check reads runs146/<tag>.score.json (item 309 (k)(2)) when its log sha256 = the "enter_scene
                   end" line of step2/times.txt, else the log (the source is printed on its own line);
  --skip-w <w>     rc 0 "SKIPPED_V_NOT_ENTERED" when the V of the pair is NOT_ENTERED (from its score.json, else its log); rc 1
                   otherwise (the W runs).
Usage (profile 146; ASCII output; logs read in binary chunks):
    python sc146.py --tag <tag> | --summary [--sheet viewed|not-viewed] [--sheet-tags ...] | --stop-check <tag> | --skip-w <w>
    python sc146.py --check-seal | --calib | --check1b | --regress145
Session 145 header (carried; profile 145):
sc145.py - the scorer of the SCENE_OK series sc145''')

# ---- 2. module constants of profile 146
t = rep('''ROOT = 'C:/kyty/s145'
PRED_PATH = 'C:/kyty/s145/pred/03_sc145.md'
CHAIN = 'go145a'
RUNS = 'runs145'
SCORER = 'sc145.py'
EXTRA = True
FORM144 = True
FORM145 = True
REPEAT = False
BUILD_SHA = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
''', '''ROOT = 'C:/kyty/s145'
PRED_PATH = 'C:/kyty/s145/pred/03_sc145.md'
CHAIN = 'go145a'
RUNS = 'runs145'
SCORER = 'sc145.py'
EXTRA = True
FORM144 = True
FORM145 = True
FORM146 = False
REPEAT = False
BUILD145 = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
BUILD146 = 'dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e'
BUILD_SHA = BUILD145
RECHECK = ()
''')

t = rep('''                'C:/kyty/s144/runs144/cache_w144_20.after.json')
SEALED144 = (''', '''                'C:/kyty/s144/runs144/cache_w144_20.after.json')
P145 = dict(ROOT=ROOT, PRED_PATH=PRED_PATH, CHAIN=CHAIN, RUNS=RUNS, SCORER=SCORER, EXTRA=EXTRA, FORM144=FORM144,
            FORM145=FORM145, FORM146=FORM146, REPEAT=REPEAT, BUILD_SHA=BUILD_SHA, RECHECK=RECHECK, LEVELS=LEVELS, PAIRS=PAIRS,
            CENSUS=CENSUS, SEQ=SEQ, V_TAGS=V_TAGS, W_TAGS=W_TAGS, SEALED_NAMES=SEALED_NAMES, CONTROL=CONTROL, XSRC=XSRC,
            XSHEET=XSHEET, XSHEET_NOTE=XSHEET_NOTE)
REGRESS145_FILE = 'C:/kyty/s145/step4/summary145_viewed.txt'
REGRESS145_SHEET = ('v145_02', 'v145_03', 'v145_04', 'v145_05', 'v145_07', 'v145_08', 'v145_09', 'v145_10', 'v145_11',
                    'v145_12', 'v145_13', 'v145_14', 'v145_15', 'v145_16')
NEW146 = ('robot_builder_next', 'interactive_credit_00', 'non_interactive_credit', 'ending_boss_after_credit',
          'collectible_viewer', 'hub_crashsite_diorama', 'diorama_controller_skin', 'diorama_astro_skin', 'diorama_zoo',
          'fragile_battle_1', 'voxel_challenge_1', 'armadillo_challenge_1', 'fragile_battle_2', 'voxel_challenge_2',
          'fragile_battle_3')
RECHECK146 = (('r146_01', 'hoover_beach'), ('r146_02', 'sponge_dirty_bath'), ('r146_03', 'timestop_casino'),
              ('r146_04', 'bonus_path_maker_mix'))
B40_TAG = 'r146_04'
B40_FIRST = 'v145_14'
WARMUP = ('i146_v', 'score_i146_v.txt')
CONTROL146 = ('w146_00', SKY)
PAIRS146 = tuple(('v146_%02d' % (i + 5), 'w146_%02d' % (i + 5), lv) for i, lv in enumerate(NEW146))
SEALED146 = ('go146a.sh', 'sc146.py', 'test_sc146.py', 'mut_sc146.py', 'enter_scene.py', 'idle142.py', 'procload.py',
             'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py', 'fgcpu146.py', 'cachemf146.py',
             'lockcheck146.py', 'tiles146.py', 'test_tools146.py', 'C:/kyty/scripts/s51_vidglitch.py', 'step2/next_one.sh',
             'step2/call_one.sh', 'step2/wait_one.sh', 'step2/pre_one.sh', 'step2/apichk146.py', 'step2/gate146.py',
             'step2/test_gate146.py', 'runs146/cache_i146_v.after.json', 'score_i146_v.txt', 'pred/00_i146.md',
             'step0/lvl146.py', 'step0/lvl146.out.txt', 'test_go146a.py', 'test_fgcpu146.py')
P146 = dict(ROOT='C:/kyty/s146', PRED_PATH='C:/kyty/s146/pred/01_sc146.md', CHAIN='go146a', RUNS='runs146',
            SCORER='sc146.py', EXTRA=True, FORM144=True, FORM145=True, FORM146=True, REPEAT=False, BUILD_SHA=BUILD146,
            RECHECK=RECHECK146, LEVELS=tuple(lv for _, _, lv in PAIRS146), PAIRS=PAIRS146,
            CENSUS=tuple((v, lv) for v, _, lv in PAIRS146),
            SEQ=(CONTROL146[0],) + tuple(r for r, _ in RECHECK146) + tuple(x for v, w, _ in PAIRS146 for x in (v, w)),
            V_TAGS=tuple(r for r, _ in RECHECK146) + tuple(v for v, _, _ in PAIRS146),
            W_TAGS=(CONTROL146[0],) + tuple(w for _, w, _ in PAIRS146), SEALED_NAMES=SEALED146, CONTROL=CONTROL146, XSRC={},
            XSHEET=(), XSHEET_NOTE='', HALF=8)
SEALED144 = (''')

# the older profiles set the keys new in 146 to the values of 145 (they ran on 9235a7ac without FORM146)
t = rep('''REGRESS_FILE = 'C:/kyty/s142/step4/summary142_viewed.txt'
''', '''REGRESS_FILE = 'C:/kyty/s142/step4/summary142_viewed.txt'
for _p in (P144, P143, P142):
    _p.update(FORM146=False, BUILD_SHA=BUILD145, RECHECK=())
''')

# HALF of profile 145 is the module default, set where it is defined
t = rep('''HALF = 8
''', '''HALF = 8
P145['HALF'] = HALF
''')

# ---- 3. markers of the new data rows
t = rep('''M_REC = b'Recovering Vulkan swapchain'
''', '''M_REC = b'Recovering Vulkan swapchain'
M_STUBCALL = b'Unresolved import stub called'
M_ASSERT = b'ASSERT:'
M_UMP = b'user_msg_param'
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\\d+) enabled=(\\d+)')
RX_TILES = re.compile(r'^TILES (\\S+) sha256 ([0-9a-f]{64}): frames (\\d+); tile events T4 (\\d+), T12 (\\d+); events (.*)$')
''')

# ---- 4. scan: the new counters (read in every profile, printed only in 146)
t = rep('''               vkval=0, vk2=0, vk2_last=None, winall=dict((k, 0) for k in WIN_ALL), winpos=[])''',
        '''               vkval=0, vk2=0, vk2_last=None, winall=dict((k, 0) for k in WIN_ALL), winpos=[], stubcall=0, asserts=0,
               ump=0, dual=[])''')
t = rep('''            res['f6'] += whole.count(M_F6)
''', '''            res['f6'] += whole.count(M_F6)
            res['stubcall'] += whole.count(M_STUBCALL)
            res['asserts'] += whole.count(M_ASSERT)
            res['ump'] += whole.count(M_UMP)
            for m in RX_DUAL.finditer(whole):
                res['dual'].append((base + m.start(), (int(m.group(1)), int(m.group(2)))))
''')

# ---- 5. level_of: the V-only tags of 146
t = rep('''    for t, lv in CENSUS:
        if t == tag:
            return lv
    return None
''', '''    for t, lv in CENSUS:
        if t == tag:
            return lv
    for t, lv in RECHECK:
        if t == tag:
            return lv
    return None
''')

# ---- 6. admission: the W form on the shipment binary
t = rep('''        if is_w:
            add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc == '0', pc)
''', '''        if is_w and FORM146:
            add('W form on the shipment binary: no KYTY_PIPELINE_PRECACHE in the env (precache by default; item 300 (b)(4), '
                '281 (g))', pc is None, pc)
        elif is_w:
            add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc == '0', pc)
''')
t = rep('''        if tag in W_TAGS:
            r['admit'].append(('W form: no "PipelinePrecache: N recipes ->" line in the log (item 254 (e))', pl == 0,
                               'log %s' % pl))
''', '''        if tag in W_TAGS and FORM146:
            pass
        elif tag in W_TAGS:
            r['admit'].append(('W form: no "PipelinePrecache: N recipes ->" line in the log (item 254 (e))', pl == 0,
                               'log %s' % pl))
''')

# ---- 7. build: the data rows of 146
t = rep('''    r['outcome'], r['outcome_vx'], r['key'], r['reason'] = outcome(r)
''', '''    if FORM146:
        r['stubcall'] = dict(log=log['stubcall'] if log is not None else None, stdout=std['stubcall'] if std is not None else None)
        r['asserts'] = dict(log=log['asserts'] if log is not None else None, stdout=std['asserts'] if std is not None else None,
                            ump_log=log['ump'] if log is not None else None, ump_stdout=std['ump'] if std is not None else None)
        gp = log['guestout'] if log is not None else None
        r['dual'] = [list(v) for _, v in log['dual']] if log is not None else []
        r['dual_pre'] = sum(1 for p, v in log['dual'] if v == (1, 1) and (gp is None or p < gp)) if log is not None else 0
        r['dual_ok'] = r['dual_pre'] >= 1
        r['tiles'] = read_tiles(root, tag) if tag in V_TAGS else None
    r['outcome'], r['outcome_vx'], r['key'], r['reason'] = outcome(r)
''')

# ---- 8. control: the DualSrcBlend letter term
t = rep('''    if FORM145 and e.get('limit'):
        letter.append('layer limit lines %d (item 273 (k)(2): 0 required in the control W)' % e['limit'])
''', '''    if FORM145 and e.get('limit'):
        letter.append('layer limit lines %d (item 273 (k)(2): 0 required in the control W)' % e['limit'])
    if FORM146 and not e.get('dual_ok'):
        letter.append('no line "DualSrcBlend: supported=1 enabled=1" before the first GuestOut line (item 300 (b)(4))')
''')

# ---- 9. stop rules: the source of every tag (json of item 309 (k)(2) or the log), the V order of 146
t = rep('''def stop_check144(tag, root, pred_sha):
    """Item 254 (k)(4) before the call of tag: (stop, lines).  Reads the control W, the last W_STOP_RUN made W and the
    last STOP_RUN made census V before the tag."""
    before = list(SEQ[:SEQ.index(tag)])
    lines = []
    stop = False
    c = CONTROL[0]
    if c in before:
        e = entry_of(c, root, pred_sha)
''', '''def entry_src(t, root, pred_sha, src):
    """Item 309 (k)(2): the reading of a made tag for the stop rules - from runs<NNN>/<t>.score.json (the dump of --tag) when
    src is 'json' and the json's log_sha = the last "enter_scene end" line of step2/times.txt; else from the log (entry_of).
    Returns (entry or None, source word)."""
    if src == 'json':
        p = os.path.join(root, RUNS, '%s.score.json' % t)
        why = 'no score.json'
        if os.path.isfile(p):
            try:
                e = json.load(open(p, encoding='utf-8'))
            except ValueError:
                e = None
                why = 'score.json broken'
            if isinstance(e, dict):
                ts = times_log_sha(root, t)
                if e.get('log_sha') is not None and e.get('log_sha') == ts:
                    return e, 'json'
                why = 'score.json log sha %s != times.txt %s' % ((e.get('log_sha') or '-')[:16], (ts or '-')[:16])
        return entry_of(t, root, pred_sha), 'log (%s)' % why
    return entry_of(t, root, pred_sha), 'log'


def stop_check144(tag, root, pred_sha, src='log'):
    """Item 254 (k)(4) before the call of tag: (stop, lines).  Reads the control W, the last W_STOP_RUN made W and the
    last STOP_RUN made census V before the tag (profile 146: every made V of SEQ; the source of each reading by src)."""
    before = list(SEQ[:SEQ.index(tag)])
    lines = []
    stop = False
    srcs = []

    def entry_of(t, root, pred_sha):
        e, w = entry_src(t, root, pred_sha, src)
        srcs.append('%s %s' % (t, w))
        return e
    c = CONTROL[0]
    if c in before:
        e = entry_of(c, root, pred_sha)
''')
t = rep('''    vs = [t for t, _ in CENSUS if t in before and made(t, root)]
    oc = []
    for t in vs[-STOP_RUN:]:''', '''    vs = [t for t, _ in CENSUS if t in before and made(t, root)]
    if FORM146:
        vs = [t for t in before if t in V_TAGS and made(t, root)]
    oc = []
    for t in vs[-STOP_RUN:]:''')
t = rep('''        stop = stop or ev
    return stop, lines
''', '''        stop = stop or ev
    if FORM146:
        lines.append('STOP CHECK SOURCES before %s (item 309 (k)(2)): %s' % (tag, '; '.join(srcs) or 'none'))
    return stop, lines
''')

# ---- 10. fmt_entry: the data rows of 146 (appended at the end of the tag)
t = rep('''        o.append('  sheet and video sha256 (item 224 (a)(5)): sheet size %d sha %s (times.txt %s); rec sha %s (times.txt %s); '
                 'match %s' % (sh['size'], sh['sha'], sh['times_sha'], sh['rec_sha'], sh['times_rec_sha'],
                               'yes' if sh['ok'] else 'NO'))
    return o
''', '''        o.append('  sheet and video sha256 (item 224 (a)(5)): sheet size %d sha %s (times.txt %s); rec sha %s (times.txt %s); '
                 'match %s' % (sh['size'], sh['sha'], sh['times_sha'], sh['rec_sha'], sh['times_rec_sha'],
                               'yes' if sh['ok'] else 'NO'))
    if FORM146:
        o.extend(fmt146(r))
    return o


def fmt146(r):
    """The data rows of profile 146 (item 309 (l)(4); not gates) of one tag."""
    o = []
    s, a = r['stubcall'], r['asserts']
    o.append('  stubs (F13, item 309 (l)(4); data): "Unresolved import stub called" lines log %s, stdout %s' % (s['log'], s['stdout']))
    o.append('  asserts (F14, item 309 (l)(4); data): "ASSERT:" lines log %s, stdout %s; "user_msg_param" lines log %s, stdout %s%s' % (
        a['log'], a['stdout'], a['ump_log'], a['ump_stdout'],
        ' - != 0: a row of the close in register F' if any(a[k] for k in a) else ''))
    if r['tag'] in W_TAGS:
        pc = r.get('precache') or {}
        o.append('  W precache by default (item 300 (b)(4); data): "PipelinePrecache: N recipes ->" lines log %s, stdout %s' % (
            pc.get('log'), pc.get('stdout')))
        o.append('  W DualSrcBlend control (item 309 (l)(4) data row; item 300 (b)(4) a letter term of the control stop): lines %s; '
                 'supported=1 enabled=1 before the first GuestOut line (at %s): %d -> %s; variant [I] of item 281 (g) ("none -> '
                 'the tag FAIL"; not in the verdict): %s' % (
                     r['dual'] or 'none', r.get('guestout'), r['dual_pre'], 'present' if r['dual_ok'] else 'ABSENT',
                     'pass' if r['dual_ok'] else 'FAIL'))
    if r['tag'] in V_TAGS:
        o.append('  tile events (D-4, the auditor tile rule of AUDIT145 s1.4, threshold 4; data): %s' % fmt_tiles(r['tiles']))
    return o


def read_tiles(root, tag):
    """tiles_<tag>.txt of tiles146.py: dict(video, sha, frames, t4, t12, events (text)) or None."""
    p = os.path.join(root, 'tiles_%s.txt' % tag)
    if not os.path.isfile(p):
        return None
    for line in open(p, 'r', encoding='ascii', errors='replace'):
        m = RX_TILES.match(line.rstrip('\\n'))
        if m:
            return dict(video=m.group(1), sha=m.group(2), frames=int(m.group(3)), t4=int(m.group(4)), t12=int(m.group(5)),
                        events=m.group(6))
    return None


def fmt_tiles(x):
    if x is None:
        return 'n/a (no tiles_<tag>.txt)'
    return 'frames %d; frames with a tile event T4 %d, T12 %d; events (frame, row, col, t1, t2, back, tiles) %s' % (
        x['frames'], x['t4'], x['t12'], x['events'][:400])
''')

# ---- 11. summary: skipped W, the census header of 146, the lines of 146
t = rep('''        elif t in nojs:
            out.append('TAG %s: ATTEMPT MADE, NO JSON (instrument)' % t)
        else:
            out.append('TAG %s: not made' % t)
    for t in XSRC:''', '''        elif t in nojs:
            out.append('TAG %s: ATTEMPT MADE, NO JSON (instrument)' % t)
        elif FORM146 and skipped(t, root):
            out.append('TAG %s: SKIPPED_V_NOT_ENTERED (item 309 (k)(1): the V of its pair is NOT_ENTERED; not an attempt)' % t)
        else:
            out.append('TAG %s: not made' % t)
    for t in XSRC:''')
t = rep('''    if EXTRA:
        out.append('SCENE_OK LEVELS: YES %d, PENDING_SHEET %d, NO %d of %d' % (
            words.count('YES'), words.count('PENDING_SHEET'), words.count('NO'), len(PAIRS)))
''', '''    if EXTRA:
        out.append('SCENE_OK LEVELS: YES %d, PENDING_SHEET %d, NO %d of %d' % (
            words.count('YES'), words.count('PENDING_SHEET'), words.count('NO'), len(PAIRS)))
    if FORM146:
        out.extend(summary146(root, ents, sheet, sheet_tags))
''')
t = rep('''        out.append('W FORM (item 254 (e)): V with the "PipelinePrecache: N recipes ->" line and no KYTY_PIPELINE_PRECACHE '
                   '%d of %d made; W with KYTY_PIPELINE_PRECACHE=0 and no such line in the log %d of %d made; violated: %s; '
                   'executor member [I] (item 258 (d), not in the verdict; a hit is a question to the lead): W with the line '
                   'in the emulator stdout: %s' % (len(vm) - len(vbad), len(vm), len(wm) - len(wbad), len(wm),
                                                    ','.join(vbad + wbad) or 'none', ','.join(wstd) or 'none'))
''', '''        if FORM146:
            wln = [t for t in wm if (ents[t].get('precache') or {}).get('log')]
            out.append('W FORM (item 300 (b)(4), 281 (g)): V with the "PipelinePrecache: N recipes ->" line and no '
                       'KYTY_PIPELINE_PRECACHE %d of %d made; W without KYTY_PIPELINE_PRECACHE (precache by default) %d of %d '
                       'made; violated: %s; data: W with the precache line in the log %s' % (
                           len(vm) - len(vbad), len(vm), len(wm) - len(wbad), len(wm), ','.join(vbad + wbad) or 'none',
                           ','.join(wln) or 'none'))
        else:
            out.append('W FORM (item 254 (e)): V with the "PipelinePrecache: N recipes ->" line and no KYTY_PIPELINE_PRECACHE '
                       '%d of %d made; W with KYTY_PIPELINE_PRECACHE=0 and no such line in the log %d of %d made; violated: %s; '
                       'executor member [I] (item 258 (d), not in the verdict; a hit is a question to the lead): W with the line '
                       'in the emulator stdout: %s' % (len(vm) - len(vbad), len(vm), len(wm) - len(wbad), len(wm),
                                                        ','.join(vbad + wbad) or 'none', ','.join(wstd) or 'none'))
''')
t = rep('''    if FORM145:
        out.append('CENSUS = the V tags %s..%s, COLD first entries of never-entered levels (item 273 (k)(1)-(2)): the map '
                   'rows and the forms B5 / B5a / B33 below go into the cold pools' % (CENSUS[0][0], CENSUS[-1][0]))
''', '''    if FORM146:
        out.append('CENSUS = the V tags %s..%s, COLD first entries of never-entered levels on dac02fb9 (item 309 (l)(2)-(3)): '
                   'the map rows and the forms B5 / B5a / B33 below go into the cold pools; the re-check and second-hold V '
                   'are outside the census' % (CENSUS[0][0], CENSUS[-1][0]))
    elif FORM145:
        out.append('CENSUS = the V tags %s..%s, COLD first entries of never-entered levels (item 273 (k)(1)-(2)): the map '
                   'rows and the forms B5 / B5a / B33 below go into the cold pools' % (CENSUS[0][0], CENSUS[-1][0]))
''')

# ---- 12. the summary lines of 146, regress145, skip-w, helpers - before cache_manifest
t = rep('''def cache_manifest(root, tag, when):''', '''def skipped(t, root):
    """Item 309 (k)(1): the chain's marker skipped_<w>.txt of a W not called because its V is NOT_ENTERED."""
    return os.path.isfile(os.path.join(root, 'skipped_%s.txt' % t))


def pair_v(w):
    for v, w2, _ in PAIRS:
        if w2 == w:
            return v
    return None


def skip_w(w, root, pred_sha, src='json'):
    """Item 309 (k)(1): (skip, line) - skip the W when the V of its pair is NOT_ENTERED (from its score.json, else its log)."""
    v = pair_v(w)
    if v is None:
        return False, 'RUN %s: no pair V (not a pair W)' % w
    e, s = entry_src(v, root, pred_sha, src)
    if e is None:
        return False, 'RUN %s: its V %s has no reading (%s)' % (w, v, s)
    if e['outcome'] == 'NOT_ENTERED':
        return True, 'SKIPPED_V_NOT_ENTERED %s: its V %s outcome NOT_ENTERED (%s; item 309 (k)(1))' % (w, v, s)
    return False, 'RUN %s: its V %s outcome %s (%s)' % (w, v, e['outcome'], s)


def summary146(root, ents, sheet, sheet_tags):
    """The summary lines of profile 146 (item 309 (l)(2)-(4), item 300 (d))."""
    out = []
    for rt, lv in RECHECK:
        e = ents.get(rt)
        if rt == B40_TAG:
            if e is None:
                out.append('B40 SECOND HOLD %s (%s; item 309 (e)(2), (l)(2)): not made' % (lv, rt))
                continue
            d = e['derive']
            out.append('B40 SECOND HOLD %s (%s; item 309 (e)(2), (l)(2); data for p of B40): entered %s, outcome %s (%s); '
                       'K2 frames after the first scene frame %s; tail stall %s; presented after the first scene frame %.1f s; '
                       'the first hold %s had K2 n 7249 (item 309 (v))' % (
                           lv, rt, 'yes' if d['entered'] else 'NO', e['outcome'], e['reason'], d['k2'] or 'none',
                           'yes' if e['tail_stall'] else 'no', d['dt_after_first_us'] / 1e6, B40_FIRST))
            continue
        sh = sheet if (sheet_tags is None or rt in sheet_tags) else None
        if e is None:
            out.append('RECHECK %s (%s; item 300 (g), 309 (l)(2)): not made' % (lv, rt))
            continue
        _, rows = scene_ok(e, None, sh, (rt, None, lv))
        vr = [x for x in rows if x[0].startswith('V ') and 'are the pair of one level' not in x[0]
              and not x[0].startswith('V sheet file')]
        vr.append(('V guest args -lvl %s, json level %s, sha256 of the log read = the enter_scene end line of step2/times.txt'
                   % (lv, lv), e['guest_args'] == '-lvl %s' % lv and e['att_level'] == lv and e['log_sha'] is not None
                   and e['log_sha'] == e['times_log_sha'], '%s, %s, %s / %s' % (e['guest_args'], e['att_level'],
                                                                              (e['log_sha'] or '-')[:16],
                                                                              (e['times_log_sha'] or '-')[:16])))
        machine = all(x[1] for x in vr)
        file_ok = e['sheet'] is not None and e['sheet']['ok']
        if not machine:
            word = 'REMOVES SCENE_OK'
        elif sh == 'viewed':
            word = 'PASSES' if file_ok else 'REMOVES SCENE_OK'
        elif sh == 'not-viewed':
            word = 'REMOVES SCENE_OK'
        else:
            word = 'PENDING_SHEET'
        out.append('RECHECK %s (%s; item 300 (g), 309 (l)(2): the V rows of item 221 (g)(3) on dac02fb9 and the sheet row): %s' % (
            lv, rt, word))
        for name, ok, det in vr:
            out.append('  %-4s %s (%s)' % ('PASS' if ok else 'FAIL', name, det))
        out.append('  %-4s V sheet file sheet_%s.png and rec sha = step2/times.txt (%s)' % ('PASS' if file_ok else 'FAIL', rt,
                                                                                          'see the tag'))
        out.append('  %-4s sheet of V viewed by the lead (%s)' % ('PASS' if sh == 'viewed' else 'FAIL', sh or 'UNSET'))
    c = CONTROL[0]
    ce = ents.get(c)
    wl = os.path.join(root, WARMUP[1])
    wv = None
    if os.path.isfile(wl):
        for line in open(wl, 'r', encoding='ascii', errors='replace'):
            if line.startswith('WARMUP VERDICT'):
                wv = line.strip()
    out.append('SKY GARDEN ON dac02fb9 (item 300 (d); information for the lead, not a SCENE_OK word of this scorer): warm-up V %s '
               '%s (%s sha256 %s); control W %s %s' % (
                   WARMUP[0], wv or 'no WARMUP VERDICT line', WARMUP[1], sha_file(wl)[:16] if os.path.isfile(wl) else '-', c,
                   'not made' if ce is None else ('STOP' if control_state(ce)[0] else 'PASS')))
    made_e = [t for t in SEQ if ents.get(t) is not None]
    out.append('DATA stubs (F13; "Unresolved import stub called" log/stdout): %s' % (
        '; '.join('%s %s/%s' % (t, ents[t]['stubcall']['log'], ents[t]['stubcall']['stdout']) for t in made_e) or 'none'))
    aa = [t for t in made_e if any(ents[t]['asserts'][k] for k in ents[t]['asserts'])]
    out.append('DATA asserts (F14; "ASSERT:" / "user_msg_param" lines, log and stdout): tags with != 0 (a row of the close in '
               'register F): %s' % ('; '.join('%s ASSERT %s/%s user_msg_param %s/%s' % (
                   t, ents[t]['asserts']['log'], ents[t]['asserts']['stdout'], ents[t]['asserts']['ump_log'],
                   ents[t]['asserts']['ump_stdout']) for t in aa) or 'none'))
    vt = [t for t in V_TAGS if ents.get(t) is not None]
    out.append('DATA tile events (D-4, T 4; frames with an event per V; the frames go to the lead as triples): %s' % (
        '; '.join('%s %s' % (t, 'n/a' if ents[t]['tiles'] is None else ents[t]['tiles']['t4']) for t in vt) or 'none'))
    wt = [t for t in W_TAGS if ents.get(t) is not None]
    out.append('DATA DualSrcBlend control per W (supported=1 enabled=1 before the first GuestOut): %s' % (
        '; '.join('%s %s' % (t, 'present' if ents[t]['dual_ok'] else 'ABSENT') for t in wt) or 'none'))
    sk = [w for _, w, _ in PAIRS if ents.get(w) is None and skipped(w, root)]
    out.append('SKIPPED_V_NOT_ENTERED (item 309 (k)(1); W not called, not attempts): %s' % (','.join(sk) or 'none'))
    return out


def regress145(expect=REGRESS145_FILE):
    """Item 309 (l)(6): profile 145 on the 33 logs of s145; the summary with the sheet row viewed for the 14 V of item 309 (a)
    must equal the lead's file byte for byte (CRLF); the stop-check of every tag of s145 from the score.json (item 309 (k)(2))
    must print the same decision lines as from the log.  The rows of profile 146 on the same logs are printed apart (NEW146).
    Returns (ok, lines)."""
    old = profile(P145)
    g = globals()
    o_scan, o_entry = g['scan'], g['entry_of']
    m_scan, m_entry = {}, {}

    def scan_m(path):
        if path not in m_scan:
            m_scan[path] = o_scan(path)
        return m_scan[path]

    def entry_m(tag, root=None, pred_sha=None):
        k = (tag, root, pred_sha)
        if k not in m_entry:
            m_entry[k] = o_entry(tag, root, pred_sha)
        return m_entry[k]
    g['scan'], g['entry_of'] = scan_m, entry_m
    try:
        pred_sha = sha_file(PRED_PATH) if os.path.isfile(PRED_PATH) else None
        out, ents, _ = summary(ROOT, pred_sha, 'viewed', list(REGRESS145_SHEET))
        sc_lines = []
        sc_same = 0
        sc_n = 0
        for tg in SEQ[1:]:
            s1, l1 = stop_check144(tg, ROOT, pred_sha, 'log')
            s2, l2 = stop_check144(tg, ROOT, pred_sha, 'json')
            sc_n += 1
            eq = s1 == s2 and l1 == l2
            sc_same += eq
            if not eq:
                sc_lines.append('STOPCHECK %s log %s / json %s: lines differ %s' % (tg, s1, s2, [
                    (x, y) for x, y in zip(l1, l2) if x != y][:2]))
        roots = list(SEQ) + list(XSRC)
        new146 = []
        for tg in roots:
            e = ents.get(tg)
            if e is None:
                new146.append('NEW146 %s: no json' % tg)
                continue
            rt = XSRC[tg]['root'] if tg in XSRC else ROOT
            log = scan(os.path.join(rt, 'log_%s.txt' % tg))
            sp = os.path.join(rt, 'stdout_%s.txt' % tg)
            std = scan(sp) if os.path.isfile(sp) else None
            gp = log['guestout']
            dpre = sum(1 for p, v in log['dual'] if v == (1, 1) and (gp is None or p < gp))
            new146.append('NEW146 %s: stubs log %d stdout %s; ASSERT: log %d stdout %s; user_msg_param log %d stdout %s; '
                          'DualSrcBlend lines %d, supported=1 enabled=1 before the first GuestOut %d' % (
                              tg, log['stubcall'], std['stubcall'] if std else None, log['asserts'],
                              std['asserts'] if std else None, log['ump'], std['ump'] if std else None, len(log['dual']), dpre))
        n_xsrc = len(XSRC)
    finally:
        g['scan'], g['entry_of'] = o_scan, o_entry
        profile(old)
    lines = []
    raw = open(expect, 'rb').read() if os.path.isfile(expect) else b''
    new = ('\\r\\n'.join(out) + '\\r\\n').encode('ascii', 'replace')
    a = raw.decode('ascii', 'replace').replace('\\r\\n', '\\n').split('\\n')
    if a and a[-1] == '':
        a = a[:-1]
    diff = [(i + 1, a[i] if i < len(a) else '<none>', out[i] if i < len(out) else '<none>')
            for i in range(max(len(a), len(out))) if (a[i] if i < len(a) else None) != (out[i] if i < len(out) else None)]
    same = raw == new and bool(raw)
    lines.append('REGRESS145 expected %s sha256 %s lines %d; new lines %d sha256 %s; byte-identical %s; differing lines %d'
                 % (expect, hashlib.sha256(raw).hexdigest(), len(a), len(out), hashlib.sha256(new).hexdigest(),
                    'yes' if same else 'NO', len(diff)))
    for i, x, y in diff[:40]:
        lines.append('DIFF line %d expected: %s' % (i, x))
        lines.append('DIFF line %d new:      %s' % (i, y))
    lines.extend(sc_lines)
    sc_ok = sc_n == len(roots) - 1 - n_xsrc and sc_same == sc_n
    lines.append('REGRESS145 stop-check from score.json = from the log (item 309 (k)(2)): %d of %d tags equal -> %s' % (
        sc_same, sc_n, 'PASS' if sc_ok else 'FAIL'))
    lines.append('NEW146 ROWS of profile 146 on the same logs (data rows; not in the regression file):')
    lines.extend(new146)
    ok = same and sc_ok
    lines.append('REGRESS145: %s' % ('PASS' if ok else 'FAIL'))
    return ok, lines


def cache_manifest(root, tag, when):''')

# ---- 13. main: --skip-w, --regress145, the stop-check source
t = rep('''    ap.add_argument('--regress144', action='store_true')
''', '''    ap.add_argument('--regress144', action='store_true')
    ap.add_argument('--regress145', action='store_true')
    ap.add_argument('--skip-w')
''')
t = rep('''    if a.regress144:
        ok, lines = regress144()
        print('\\n'.join(lines))
        return 0 if ok else 1
''', '''    if a.regress144:
        ok, lines = regress144()
        print('\\n'.join(lines))
        return 0 if ok else 1
    if a.regress145:
        ok, lines = regress145()
        print('\\n'.join(lines))
        return 0 if ok else 1
''')
t = rep('''        if FORM144:
            stop, lines = stop_check144(a.stop_check, root, pred_sha)
''', '''        if FORM144:
            stop, lines = stop_check144(a.stop_check, root, pred_sha, 'json' if FORM146 else 'log')
''')
t = rep('''    if a.tag:
        if a.tag not in SEQ:''', '''    if a.skip_w:
        if a.skip_w not in W_TAGS or pair_v(a.skip_w) is None:
            print('usage: --skip-w takes a W of a pair: %s' % a.skip_w)
            return 2
        sk, line = skip_w(a.skip_w, root, pred_sha)
        print(line)
        return 0 if sk else 1
    if a.tag:
        if a.tag not in SEQ:''')
t = rep('''    print('usage: sc145.py --tag T | --summary | --stop-check T | --check-seal | --calib | --check1b | --regress142 | '
          '--regress143 | --regress144')''', '''    print('usage: %s --tag T | --summary | --stop-check T | --skip-w W | --check-seal | --calib | --check1b | --regress142 | '
          '--regress143 | --regress144 | --regress145' % SCORER)''')

# ---- 14. the default profile is 146
t = rep('''

def profile(values):''', '''

def profile(values):''')
t = rep('''if __name__ == '__main__':
    sys.exit(main())''', '''globals().update(P146)
if __name__ == '__main__':
    sys.exit(main())''')
# main's defaults are bound at def time to the profile-145 root and seal: read them at call time
t = rep('''def main(argv=None, root=ROOT, pred=PRED_PATH):''', '''def main(argv=None, root=None, pred=None):
    root = ROOT if root is None else root
    pred = PRED_PATH if pred is None else pred''')
t = rep('''def check_seal(pred=PRED_PATH, root=ROOT, me=None):''', '''def check_seal(pred=None, root=None, me=None):
    pred = PRED_PATH if pred is None else pred
    root = ROOT if root is None else root''')
t = rep('''def entry_of(tag, root=ROOT, pred_sha=None):''', '''def entry_of(tag, root=None, pred_sha=None):''')
t = rep('''    lv = level_of(tag)
    x = XSRC.get(tag)
    pred_path = chain = None''', '''    root = ROOT if root is None else root
    lv = level_of(tag)
    x = XSRC.get(tag)
    pred_path = chain = None''')
t = rep('''def attempt_marker(tag, root=ROOT):''', '''def attempt_marker(tag, root=None):''')
t = rep('''    """Item 224 (a)(8): the chain's marker attempt_<tag>.txt of a made attempt."""
    return''', '''    """Item 224 (a)(8): the chain's marker attempt_<tag>.txt of a made attempt."""
    root = ROOT if root is None else root
    return''')

bad = [i for i, c in enumerate(t) if ord(c) > 127]
if bad:
    print('NON-ASCII at', bad[:5])
    sys.exit(1)
open(DST, 'wb').write(t.encode('ascii'))
print('port_sc146: %d replacements; %s sha256 %s -> %s sha256 %s' % (
    len(R), SRC, hashlib.sha256(open(SRC, 'rb').read()).hexdigest(), DST, hashlib.sha256(t.encode('ascii')).hexdigest()))
print('ALL OK')
