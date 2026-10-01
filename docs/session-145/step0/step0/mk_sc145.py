"""Session 145 step 0 (HPP-350): build C:/kyty/s145/sc145.py from C:/kyty/s144/sc144.py by exact replacements (each anchor
must occur exactly once).  The constants of sc144 are not changed; profile 144 (P144) keeps every value of the sc144 module so
--regress144 prints what sc144.py printed; the new rows of item 273 (k)(2)-(3) are guarded by FORM145.  ASCII only, LF."""
import sys

t = open('C:/kyty/s144/sc144.py', 'rb').read().decode('ascii')
assert '\r' not in t
R = []


def rep(old, new):
    R.append((old, new))


HEAD = '''"""sc145.py - the scorer of the SCENE_OK series sc145 (session 145 step 0, HPP-350; ROADMAP "SESSION 122" item 273 (k)(1)-(7);
brief docs/next-session-145.md): the port of sc144.py (session 144 step 0, HPP-330) with NO change of its constants and
three new rows (item 273 (k)(2)-(3)).  Profiles: 145 (the default), 144 (P144: prints exactly what sc144.py printed - the
regression on the 33 logs of s144 and the 8 V of s143, --regress144), 143 (--regress143) and 142 (--regress142).
Session 145 (item 273 (k)(1)), 34 tags in this order, one call each:
  w145_00          the control W on Sky Garden (underwater_aerial_garden); no SCENE_OK pair - its rows decide the control
                   stop of item 254 (k)(4) and the layer limit of item 273 (k)(2) (0 limit lines required);
  w145_01          the W repeat of rocket_hourglass; the V of its pair is v144_09 of SESSION 144, read from C:/kyty/s144 with
                   the chain name go144a, the seal pred/01_sc144.md (its sha256 now) and the log sha256 against
                   C:/kyty/s144/step2/times.txt; its sheet row is "viewed" by item 273 (a) whatever --sheet says;
  v145_NN/w145_NN  NN = 02..17, V then W per level, COLD first entries of never-entered levels: small_pot_lava,
                   spin_drill_natural_cave, enemy_taco, jack_in_the_box, final_shooting, picup_light, enemy_snake,
                   light_gadget_graveyard, shuriken_ninja_castle, final_stage, mini_rocket_chain, enemy_chameleon,
                   bonus_path_maker_mix, enemy_bird, cymbal_party_land, enemy_final.  The census (map rows, forms B5 / B5a /
                   B33) reads these V; they go into the cold pools (item 273 (k)(2)).
The W form (item 254 (e), 273 (k)(2)): --vulkan-validation true, KYTY_PIPELINE_PRECACHE=0 and the filter of ONE message,
VK_LAYER_MESSAGE_ID_FILTER=Undefined-Value-ShaderOutputNotConsumed-DynamicRendering (the F6 warning "... it writes to
[Output variable, Location N, "out_mrt_N"] but there is no VkRenderingInfo::pColorAttachments[N] and this write is unused.",
the one message on which 13 W of s144 reached the duplicate limit - step0/f6scan145.out.txt; its VUID string by the layer
binary - step0/vuid145.out.txt).  Admission rows of profile 145: a W needs exactly that value in its json env, a V needs no
such variable.
New rows of profile 145 (item 273 (k)(2)-(3)):
  window event     the numbers of lines "Window <id> minimized", "restored", "resized", "size changed", "lost keyboard
                   focus" and "Recovering Vulkan swapchain" (log and emulator stdout); a tag with a "minimized" or a
                   "Recovering Vulkan swapchain" line fails the admission row "window event": it is NOT read as an outcome
                   of the level; --stop-check stops before the next tag (the made tag right before), question to the lead;
  video continuity B38, the method of AUDIT144 s1.3 (vidcont144.py): the FrameTrace rows after the first scene frame that end
                   strictly inside a gap of the .idx records > 60 ms (margin 12 ms; both streams anchored at their ends) and
                   the longest run - data next to SCENE_OK, not a gate;
  layer limit      the number of the layer's lines "this will be the last time reporting it" per W (log and stdout): 0 is
                   required in the control W (a letter term of its stop); elsewhere != 0 marks "layer truncated", the
                   outcome stands by the letter.
--regress144 (item 273 (k)(5)): profile 144 on the 33 logs of s144 and the 8 V of s143 must print
C:/kyty/s144/step4/summary144_viewed.txt byte for byte; the new rows on the same logs are printed apart and checked against
the facts of s144 (window event only w144_09; layer limit lines in 13 W, 0 in w144_00; continuity = vidcont144.out.txt).
Usage (profile 145; ASCII output; logs read in binary chunks):
    python sc145.py --tag <tag> | --summary [--sheet viewed|not-viewed] [--sheet-tags ...] | --stop-check <tag>
    python sc145.py --check-seal | --calib | --check1b | --regress144 | --regress143 | --regress142
Session 144 header (carried; profile 144):
sc144.py - the scorer'''
rep('"""sc144.py - the scorer', HEAD)

i0 = t.index("ROOT = 'C:/kyty/s144'\n")
i1 = t.index('SEALED143 = (')
OLDC = t[i0:i1]
NEWC = '''ROOT = 'C:/kyty/s145'
PRED_PATH = 'C:/kyty/s145/pred/01_sc145.md'
CHAIN = 'go145a'
RUNS = 'runs145'
SCORER = 'sc145.py'
EXTRA = True
FORM144 = True
FORM145 = True
REPEAT = False
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
OLD144 = (('v144_09', 'rocket_hourglass'),)
NEW145 = ('small_pot_lava', 'spin_drill_natural_cave', 'enemy_taco', 'jack_in_the_box', 'final_shooting', 'picup_light',
          'enemy_snake', 'light_gadget_graveyard', 'shuriken_ninja_castle', 'final_stage', 'mini_rocket_chain',
          'enemy_chameleon', 'bonus_path_maker_mix', 'enemy_bird', 'cymbal_party_land', 'enemy_final')
VKFILTER = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
CONTROL = ('w145_00', SKY)
PAIRS = tuple((v, 'w145_%02d' % (i + 1), lv) for i, (v, lv) in enumerate(OLD144)) + tuple(
    ('v145_%02d' % (i + 2), 'w145_%02d' % (i + 2), lv) for i, lv in enumerate(NEW145))
LEVELS = tuple(lv for _, _, lv in PAIRS)
CENSUS = tuple((v, lv) for v, _, lv in PAIRS[len(OLD144):])
SEQ = (CONTROL[0],) + tuple(w for _, w, _ in PAIRS[:len(OLD144)]) + tuple(
    t for v, w, _ in PAIRS[len(OLD144):] for t in (v, w))
V_TAGS = tuple(v for v, _, _ in PAIRS)
W_TAGS = (CONTROL[0],) + tuple(w for _, w, _ in PAIRS)
ROOT143 = 'C:/kyty/s143'
PRED143 = 'C:/kyty/s143/pred/02_sc143.md'
ROOT144 = 'C:/kyty/s144'
PRED144 = 'C:/kyty/s144/pred/01_sc144.md'
XSRC = dict((v, dict(root=ROOT144, chain='go144a', pred=PRED144)) for v, _ in OLD144)
XSHEET = tuple(v for v, _ in OLD144)
XSHEET_NOTE = ' (item 273 (a): viewed at the close of s144)'
SEALED_NAMES = ('go145a.sh', 'sc145.py', 'test_sc145.py', 'mut_sc145.py', 'enter_scene.py',
                'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py',
                'test_go145a.py', 'fgcpu145.py', 'test_fgcpu145.py', 'C:/kyty/scripts/s51_vidglitch.py',
                'cachemf145.py', 'lockcheck145.py', 'test_tools145.py', 'step2/next_one.sh', 'step2/call_one.sh',
                'step2/wait_one.sh', 'step2/pre_one.sh', 'step2/apichk145.py', 'step2/gate145.py', 'step2/test_gate145.py',
                'C:/kyty/s144/step2/times.txt', 'C:/kyty/s144/pred/01_sc144.md')
SEALED144 = ('go144a.sh', 'sc144.py', 'test_sc144.py', 'mut_sc144.py', 'enter_scene.py',
             'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py',
             'test_go144a.py', 'fgcpu144.py', 'test_fgcpu144.py', 'C:/kyty/scripts/s51_vidglitch.py',
             'cachemf144.py', 'lockcheck144.py', 'test_tools144.py', 'step2/next_one.sh', 'step2/call_one.sh',
             'step2/wait_one.sh', 'step2/apichk144.py', 'C:/kyty/s143/step2/times.txt', 'C:/kyty/s143/pred/02_sc143.md')
CONTROL144 = ('w144_00', SKY)
PAIRS144 = tuple((v, 'w144_%02d' % (i + 1), lv) for i, (v, lv) in enumerate(OLD143)) + tuple(
    ('v144_%02d' % (i + 9), 'w144_%02d' % (i + 9), lv) for i, lv in enumerate(NEW144))
P144 = dict(ROOT=ROOT144, PRED_PATH=PRED144, CHAIN='go144a', RUNS='runs144', SCORER='sc144.py', EXTRA=True, FORM144=True,
            FORM145=False, REPEAT=True, LEVELS=tuple(lv for _, _, lv in PAIRS144),
            PAIRS=PAIRS144, CENSUS=tuple((v, lv) for v, _, lv in PAIRS144[len(OLD143):]),
            SEQ=(CONTROL144[0],) + tuple(w for _, w, _ in PAIRS144[:len(OLD143)]) + tuple(
                t for v, w, _ in PAIRS144[len(OLD143):] for t in (v, w)),
            V_TAGS=tuple(v for v, _, _ in PAIRS144), W_TAGS=(CONTROL144[0],) + tuple(w for _, w, _ in PAIRS144),
            SEALED_NAMES=SEALED144, CONTROL=CONTROL144,
            XSRC=dict((v, dict(root=ROOT143, chain='go143a', pred=PRED143)) for v, _ in OLD143),
            XSHEET=tuple(v for v, _ in OLD143), XSHEET_NOTE=' (item 254 (a): viewed at the close of s143)', HALF=6)
REGRESS144_FILE = 'C:/kyty/s144/step4/summary144_viewed.txt'
VCONT144_FILE = 'C:/kyty/KytyPS5/docs/session-144/audit/vidcont144.out.txt'
REGRESS144_WINEV = ('w144_09',)
REGRESS144_LIMIT = ('w144_02', 'w144_05', 'w144_06', 'w144_07', 'w144_08', 'w144_10', 'w144_11', 'w144_12', 'w144_13',
                    'w144_14', 'w144_15', 'w144_16', 'w144_17')
'''
rep(OLDC, NEWC)
rep("W_TAGS=tuple(w for _, w, _ in PAIRS143), SEALED_NAMES=SEALED143, CONTROL=None, XSRC={}, XSHEET=(), HALF=5)",
    "W_TAGS=tuple(w for _, w, _ in PAIRS143), SEALED_NAMES=SEALED143, CONTROL=None, XSRC={}, XSHEET=(), HALF=5,\n"
    "            FORM145=False, REPEAT=True, XSHEET_NOTE='')")
rep("FORM144=False, LEVELS=tuple(lv for _, lv in CENSUS142), CONTROL=None, XSRC={}, XSHEET=(), HALF=5)",
    "FORM144=False, LEVELS=tuple(lv for _, lv in CENSUS142), CONTROL=None, XSRC={}, XSHEET=(), HALF=5,\n"
    "            FORM145=False, REPEAT=True, XSHEET_NOTE='')")
rep("HALF = 6\n", "HALF = 8\n")
rep("RX_PRECACHE = re.compile(rb'PipelinePrecache: \\d+ recipes ->')\n",
    "RX_PRECACHE = re.compile(rb'PipelinePrecache: \\d+ recipes ->')\n"
    "M_LIMIT = b'this will be the last time reporting it'\n"
    "M_F6 = b'and this write is unused.'\n"
    "M_REC = b'Recovering Vulkan swapchain'\n"
    "RX_WIN = re.compile(rb'Window \\d+ (minimized|restored|resized|size changed|lost keyboard focus)\\b')\n"
    "RX_VKT = re.compile(rb'\\[Vulkan\\]\\[\\w\\]\\[(\\d+)\\]')\n"
    "WIN_KEYS = ('minimized', 'restored', 'resized', 'size changed', 'lost keyboard focus')\n"
    "VC_GAP = 0.060\n"
    "VC_MARG = 0.012\n")
rep("import argparse\nimport hashlib\n", "import argparse\nimport bisect\nimport hashlib\n")
rep("               guestout=None, precache=0, precache_any=0)\n",
    "               guestout=None, precache=0, precache_any=0, win=dict((k, 0) for k in WIN_KEYS), rec=0, limit=0, f6=0,\n"
    "               vkval=0)\n")
rep("            res['precache_any'] += whole.count(M_PRECACHE)\n",
    "            res['precache_any'] += whole.count(M_PRECACHE)\n"
    "            res['rec'] += whole.count(M_REC)\n"
    "            res['limit'] += whole.count(M_LIMIT)\n"
    "            res['f6'] += whole.count(M_F6)\n"
    "            for m in RX_WIN.finditer(whole):\n"
    "                res['win'][m.group(1).decode()] += 1\n"
    "            for m in RX_VKT.finditer(whole):\n"
    "                if int(m.group(1)) & 2:\n"
    "                    res['vkval'] += 1\n")
rep("""    if FORM144:
        pc = env.get('KYTY_PIPELINE_PRECACHE')
        if is_w:
            add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc == '0', pc)
        else:
            add('V shipped defaults: no KYTY_PIPELINE_PRECACHE in the env (item 254 (k)(2))', pc is None, pc)
    return rows
""", """    if FORM144:
        pc = env.get('KYTY_PIPELINE_PRECACHE')
        if is_w:
            add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc == '0', pc)
        else:
            add('V shipped defaults: no KYTY_PIPELINE_PRECACHE in the env (item 254 (k)(2))', pc is None, pc)
    if FORM145:
        fl = env.get('VK_LAYER_MESSAGE_ID_FILTER')
        if is_w:
            add('W filter: VK_LAYER_MESSAGE_ID_FILTER = %s, one id (item 273 (k)(2))' % VKFILTER, fl == VKFILTER, fl)
        else:
            add('V shipped defaults: no VK_LAYER_MESSAGE_ID_FILTER in the env (item 273 (k)(2))', fl is None, fl)
    return rows
""")
rep("""    r['val'] = validation(log, std)
""", """    r['val'] = validation(log, std)
    r['win'] = dict((k, sum(sc['win'][k] for sc in (log, std) if sc is not None)) for k in WIN_KEYS)
    r['win']['recovering'] = sum(sc['rec'] for sc in (log, std) if sc is not None)
    r['winev'] = r['win']['minimized'] > 0 or r['win']['recovering'] > 0
    r['limit'] = None if log is None else log['limit'] + (std['limit'] if std is not None else 0)
    r['f6'] = sum(sc['f6'] for sc in (log, std) if sc is not None)
    r['vkval'] = sum(sc['vkval'] for sc in (log, std) if sc is not None)
    if FORM145:
        r['admit'].append(('window event: no "Window <id> minimized" and no "Recovering Vulkan swapchain" line (item 273 '
                           '(k)(3))', not r['winev'], 'minimized %d, Recovering %d' % (r['win']['minimized'],
                                                                                      r['win']['recovering'])))
""")
rep("""    r['idx'] = idx_count(os.path.join(root, 'rec_%s.mp4.idx' % tag))
""", """    r['idx'] = idx_count(os.path.join(root, 'rec_%s.mp4.idx' % tag))
    r['vcont'] = vcont(log['rows'] if log is not None else [], idx_times(os.path.join(root, 'rec_%s.mp4.idx' % tag)),
                       d['first'][0] if d['first'] is not None else None) if tag in V_TAGS else None
""")
rep('''def sheet_state(root, tag, chain=None):''', '''def idx_times(path):
    """B38 (item 273 (k)(3)): the times (the third field, s) of the records of rec_<tag>.mp4.idx (lines of >= 3 fields, as
    idx_count reads them); None without the file."""
    if not os.path.isfile(path):
        return None
    out = []
    with open(path, 'rb') as f:
        for line in f:
            x = line.split()
            if len(x) >= 3:
                try:
                    out.append(float(x[2]))
                except ValueError:
                    pass
    return out


def vcont(rows, it, fn):
    """B38 (item 273 (k)(3); the method of AUDIT144 s1.3, vidcont144.py): the FrameTrace rows and the .idx records are put
    on one clock anchored at their ends (the last record = the end of the last row; a row ends where the dt of the rows
    after it, summed back from the last record, puts it); inside every gap of the records > VC_GAP the rows that END strictly
    inside it (margin VC_MARG) are presented frames without a video record.  None without rows, records or a first scene
    frame (its n is fn); else dict(after = such rows after the first scene frame, gaps = the gaps holding them, before = such
    rows at or before it, longest = (rows, first n, last n, gap s, record index) of the gap with the most rows among the
    gaps holding rows after it, or None)."""
    if not rows or not it or fn is None:
        return None
    ends = []
    c = 0.0
    for r in reversed(rows):
        ends.append(it[-1] - c)
        c += r[1] / 1e6
    ends.reverse()
    after = []
    before = 0
    for i in range(len(it) - 1):
        g = it[i + 1] - it[i]
        if g > VC_GAP:
            lo = bisect.bisect_right(ends, it[i] + VC_MARG)
            hi = bisect.bisect_left(ends, it[i + 1] - VC_MARG)
            if hi > lo:
                ns = [rows[k][0] for k in range(lo, hi)]
                before += sum(1 for n in ns if n <= fn)
                if ns[-1] > fn:
                    after.append((i, g, ns))
    worst = max(after, key=lambda x: len(x[2])) if after else None
    return dict(after=sum(sum(1 for n in ns if n > fn) for _, _, ns in after), gaps=len(after), before=before,
                longest=(len(worst[2]), worst[2][0], worst[2][-1], round(worst[1], 3), worst[0]) if worst else None)


def fmt_vcont(vc):
    if vc is None:
        return 'n/a (no video index, no FrameTrace row or no first scene frame)'
    lg = vc['longest']
    return ('FrameTrace rows after the first scene frame ending inside a .idx gap > 60 ms: %d in %d gaps; longest run %s; '
            'at or before the first scene frame %d' % (vc['after'], vc['gaps'], 'none' if lg is None else
                                                       '%d rows n %d..%d (gap %.3f s after record %d)' % lg, vc['before']))


def fmt_win(w):
    return ('minimized %d, restored %d, resized %d, size changed %d, lost keyboard focus %d, Recovering Vulkan swapchain %d'
            % tuple(w[k] for k in WIN_KEYS + ('recovering',)))


def sheet_state(root, tag, chain=None):''')
rep("""    if e.get('vke'):
        letter.append('[Vulkan][E] %d' % e['vke'])
""", """    if e.get('vke'):
        letter.append('[Vulkan][E] %d' % e['vke'])
    if FORM145 and e.get('limit'):
        letter.append('layer limit lines %d (item 273 (k)(2): 0 required in the control W)' % e['limit'])
""")
rep("""    lines.append('STOP RULE before %s: %s' % (tag, ('STOP ' + ','.join(tv)) if sv else 'not met'))
    stop = stop or sv
    return stop, lines
""", """    lines.append('STOP RULE before %s: %s' % (tag, ('STOP ' + ','.join(tv)) if sv else 'not met'))
    stop = stop or sv
    if FORM145:
        mt = [t for t in before if made(t, root)]
        p = mt[-1] if mt else None
        e = entry_of(p, root, pred_sha) if p is not None else None
        ev = e is not None and e['winev']
        lines.append('STOP RULE WINDOW EVENT before %s (item 273 (k)(3)-(4): the made tag right before with a "minimized" or '
                     '"Recovering Vulkan swapchain" line; question to the lead about a repeat): %s' % (
                         tag, ('STOP %s (%s)' % (p, fmt_win(e['win']))) if ev else (
                             'not met (%s: %s)' % (p, fmt_win(e['win'])) if e is not None else 'not met (%s)' % (
                                 'no json of %s' % p if p is not None else 'no tag made'))))
        stop = stop or ev
    return stop, lines
""")
rep("""    if r['log_present']:
        op = r['ops']
""", """    if FORM145:
        o.append('  window events (item 273 (k)(3)): %s -> %s' % (fmt_win(r['win']), (
            'WINDOW EVENT: not an outcome of the level (admission row "window event" fails); the gate stops the series, '
            'question to the lead about a repeat') if r['winev'] else 'no event'))
        if r['tag'] in W_TAGS:
            ctrl = CONTROL is not None and r['tag'] == CONTROL[0]
            o.append('  layer limit lines ("this will be the last time reporting it", item 273 (k)(2)): %s%s' % (
                r['limit'], (' - control W: 0 required -> %s' % ('PASS' if r['limit'] == 0 else 'FAIL')) if ctrl else (
                    ' - LAYER TRUNCATED (the outcome stands by the letter)' if r['limit'] else '')))
            o.append('  message filter (item 273 (k)(2)): lines of the filtered F6 text ("... and this write is unused.") %d; '
                     '[Vulkan][ lines of the validation type (bit 2) %d (info, not in the verdict)' % (r['f6'], r['vkval']))
        else:
            o.append('  video continuity (B38, item 273 (k)(3), the method of AUDIT144 s1.3; data next to SCENE_OK, not a '
                     'gate): %s' % fmt_vcont(r['vcont']))
    if r['log_present']:
        op = r['ops']
""")
rep("""        ' (item 254 (a): viewed at the close of s143)' if vt in XSHEET else '')))""",
    """        XSHEET_NOTE if vt in XSHEET else '')))""")
rep("""                       % (HOLD_W_HARNESS_S, ('yes' if (w['hold_s'] or 0) >= HOLD_W_HARNESS_S else 'NO (%s)' % w['hold_s'])
                          if w else 'W not made'))
""", """                       % (HOLD_W_HARNESS_S, ('yes' if (w['hold_s'] or 0) >= HOLD_W_HARNESS_S else 'NO (%s)' % w['hold_s'])
                          if w else 'W not made'))
        if FORM145:
            out.append('  info video continuity of V %s (B38, item 273 (k)(3); data, not a gate - "0 glitches" covers the '
                       'frames in the video): %s' % (vt, fmt_vcont(v['vcont']) if v else 'V not made'))
            out.append('  info W %s layer limit lines %s%s; window events V %s, W %s' % (
                wt, w['limit'] if w else 'W not made', ' (layer truncated)' if w and w['limit'] else '',
                'yes' if v and v['winev'] else 'no', 'yes' if w and w['winev'] else 'no'))
""")
rep("""                                                    ','.join(vbad + wbad) or 'none', ','.join(wstd) or 'none'))
""", """                                                    ','.join(vbad + wbad) or 'none', ','.join(wstd) or 'none'))
    if FORM145:
        made_e = [t for t in tuple(SEQ) + tuple(XSRC) if ents.get(t) is not None]
        ev = [t for t in made_e if ents[t]['winev']]
        oth = [t for t in made_e if not ents[t]['winev'] and any(ents[t]['win'][k] for k in WIN_KEYS[1:])]
        out.append('WINDOW EVENTS (item 273 (k)(3)): tags with a "minimized" or "Recovering Vulkan swapchain" line (not an '
                   'outcome of the level; the gate stops the series): %s; tags with only other window lines (restored, '
                   'resized, size changed, lost keyboard focus): %s' % (','.join(ev) or 'none', ','.join(oth) or 'none'))
        c = CONTROL[0]
        ce = ents.get(c)
        lim = [t for t in wm if t != c and ents[t]['limit']]
        out.append('LAYER LIMIT (item 273 (k)(2)): control W %s: %s -> %s; other W with layer limit lines (layer truncated, the '
                   'outcome by the letter): %s' % (c, 'not made' if ce is None else '%s lines' % ce['limit'], 'n/a' if ce is
                                                   None else ('PASS' if ce['limit'] == 0 else 'FAIL (a letter term of the '
                                                                                               'control stop)'),
                                                   ','.join(lim) or 'none'))
        fbad = [t for t in wm if not all(a[1] for a in ents[t]['admit'] if a[0].startswith('W filter'))]
        vfl = [t for t in vm if not all(a[1] for a in ents[t]['admit'] if 'VK_LAYER_MESSAGE_ID_FILTER' in a[0])]
        out.append('W FILTER (item 273 (k)(2)): VK_LAYER_MESSAGE_ID_FILTER=%s in %d of %d made W; V without it %d of %d made; '
                   'violated: %s; lines of the filtered F6 text in the W (info): %s' % (
                       VKFILTER, len(wm) - len(fbad), len(wm), len(vm) - len(vfl), len(vm), ','.join(fbad + vfl) or 'none',
                       ', '.join('%s %d' % (t, ents[t]['f6']) for t in wm) or 'none'))
        vr = [t for t in vm if ents[t]['vcont'] is not None and ents[t]['vcont']['longest'] is not None
              and ents[t]['vcont']['longest'][0] >= 2]
        out.append('VIDEO CONTINUITY (B38, item 273 (k)(3); data, not a gate): V with a run of >= 2 rows without a video record '
                   'after the first scene frame: %s' % (', '.join('%s %d rows' % (t, ents[t]['vcont']['longest'][0])
                                                                   for t in vr) or 'none'))
""")
rep("""    if FORM144:
        out.append('CENSUS = the V tags %s..%s, REPEATED entries""",
    """    if FORM145:
        out.append('CENSUS = the V tags %s..%s, COLD first entries of never-entered levels (item 273 (k)(1)-(2)): the map '
                   'rows and the forms B5 / B5a / B33 below go into the cold pools' % (CENSUS[0][0], CENSUS[-1][0]))
    if FORM144 and REPEAT:
        out.append('CENSUS = the V tags %s..%s, REPEATED entries""")
rep("""e['level'], ' (repeated entry)' if FORM144 else '',""",
    """e['level'], ' (repeated entry)' if FORM144 and REPEAT else (' (cold first entry)' if FORM145 else ''),""")
rep('''def calib():''', '''def vcont_audit(path):
    """{(session, tag): (first n, before, after, gaps, longest (rows, n0, n1, record) or None)} of the VCONT lines of
    vidcont144.out.txt (AUDIT144 s1.3); {} without the file."""
    rx = re.compile(r'^VCONT (s14\\d) (\\S+): .*?first scene frame n (\\S+); presented frames WITHOUT a video record: before / '
                    r'at the first scene frame (\\d+), after it (\\d+) in (\\d+) gaps; longest run after it: (none|(\\d+) rows n '
                    r'(\\d+)\\.\\.(\\d+) over \\S+ s of dt \\(idx gap \\S+ s after record (\\d+)\\))')
    out = {}
    if not os.path.isfile(path):
        return out
    for line in open(path, encoding='ascii', errors='replace'):
        m = rx.match(line)
        if m:
            lg = None if m.group(7) == 'none' else (int(m.group(8)), int(m.group(9)), int(m.group(10)), int(m.group(11)))
            out[(m.group(1), m.group(2))] = (m.group(3), int(m.group(4)), int(m.group(5)), int(m.group(6)), lg)
    return out


def regress144(expect=REGRESS144_FILE, vexpect=VCONT144_FILE):
    """Item 273 (k)(5): profile 144 on the 33 logs of s144 and the 8 V of s143; the summary with the sheet row viewed must
    equal the lead's file byte for byte (CRLF, the form sc144.py printed into it).  The new rows of profile 145 on the same
    logs are printed apart and checked against the facts of s144: the window event only in w144_09; layer limit lines in
    the 13 W of REGRESS144_LIMIT and 0 in the control w144_00; the continuity of every V of the profile (20) equal to
    vidcont144.out.txt.
    Returns (ok, lines)."""
    old = profile(P144)
    try:
        pred_sha = sha_file(PRED_PATH) if os.path.isfile(PRED_PATH) else None
        out, ents, _ = summary(ROOT, pred_sha, 'viewed')
        tags = list(SEQ) + list(XSRC)
        wtags = set(W_TAGS)
        ctrl = CONTROL[0]
        nv = len(V_TAGS)
        roots = dict((t, 's143' if t in XSRC else 's144') for t in tags)
    finally:
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
    lines.append('REGRESS144 expected %s sha256 %s lines %d; new lines %d sha256 %s; byte-identical %s; differing lines %d'
                 % (expect, hashlib.sha256(raw).hexdigest(), len(a), len(out), hashlib.sha256(new).hexdigest(),
                    'yes' if same else 'NO', len(diff)))
    for i, x, y in diff[:40]:
        lines.append('DIFF line %d expected: %s' % (i, x))
        lines.append('DIFF line %d new:      %s' % (i, y))
    lines.append('NEW ROWS of profile 145 on the same logs (not in the regression file; item 273 (k)(2)-(3)):')
    va = vcont_audit(vexpect)
    vc_n = vc_eq = 0
    for t in tags:
        e = ents.get(t)
        if e is None:
            lines.append('NEW %s: no json' % t)
            continue
        if t in wtags:
            lines.append('NEW %s W: window %s; layer limit lines %s; F6 text lines %d; [Vulkan][ lines of the validation type '
                         '%d' % (t, fmt_win(e['win']), e['limit'], e['f6'], e['vkval']))
        else:
            vc = e['vcont']
            au = va.get((roots[t], t))
            mine = None if vc is None else (str(e['derive']['first'][0]), vc['before'], vc['after'], vc['gaps'],
                                            None if vc['longest'] is None else vc['longest'][:3] + (vc['longest'][4],))
            vc_n += 1
            eq = au is not None and mine == au
            vc_eq += eq
            lines.append('NEW %s V: window %s; continuity %s; AUDIT144 vidcont144 %s -> %s' % (
                t, fmt_win(e['win']), fmt_vcont(vc), au, 'equal' if eq else 'DIFFERENT'))
    ev = tuple(t for t in tags if ents.get(t) is not None and ents[t]['winev'])
    lim = tuple(t for t in tags if t in wtags and ents.get(t) is not None and ents[t]['limit'])
    c0 = ents.get(ctrl)
    win_ok = ev == REGRESS144_WINEV
    lim_ok = lim == REGRESS144_LIMIT and c0 is not None and c0['limit'] == 0
    vc_ok = vc_n == nv and nv > 0 and vc_eq == vc_n
    lines.append('NEW ROWS window event: tags %s (expected %s, AUDIT144 s2 (2)) -> %s' % (
        ','.join(ev) or 'none', ','.join(REGRESS144_WINEV), 'PASS' if win_ok else 'FAIL'))
    lines.append('NEW ROWS layer limit: W with limit lines %d %s (expected the 13 of step0/f6scan145.out.txt); control %s %s '
                 'lines -> %s' % (len(lim), ','.join(lim) or 'none', ctrl, c0['limit'] if c0 is not None else 'not made',
                                  'PASS' if lim_ok else 'FAIL'))
    lines.append('NEW ROWS continuity: %d of %d V equal to %s (V of the profile %d) -> %s' % (
        vc_eq, vc_n, vexpect, nv, 'PASS' if vc_ok else 'FAIL'))
    ok = same and win_ok and lim_ok and vc_ok
    lines.append('REGRESS144: %s' % ('PASS' if ok else 'FAIL'))
    return ok, lines


def calib():''')
rep("""    ap.add_argument('--regress143', action='store_true')
""", """    ap.add_argument('--regress143', action='store_true')
    ap.add_argument('--regress144', action='store_true')
""")
rep("""    if a.regress143:
        ok, lines = regress143()
        print('\\n'.join(lines))
        return 0 if ok else 1
""", """    if a.regress143:
        ok, lines = regress143()
        print('\\n'.join(lines))
        return 0 if ok else 1
    if a.regress144:
        ok, lines = regress144()
        print('\\n'.join(lines))
        return 0 if ok else 1
""")
rep("""    print('usage: sc144.py --tag T | --summary | --stop-check T | --check-seal | --calib | --check1b | --regress142 | '
          '--regress143')""", """    print('usage: sc145.py --tag T | --summary | --stop-check T | --check-seal | --calib | --check1b | --regress142 | '
          '--regress143 | --regress144')""")
for old, new in R:
    n = t.count(old)
    if n != 1:
        print('ANCHOR COUNT %d: %r' % (n, old[:120]))
        sys.exit(1)
    t = t.replace(old, new)
t.encode('ascii')
open('C:/kyty/s145/sc145.py', 'wb').write(t.encode('ascii'))
print('mk_sc145: %d replacements, %d bytes' % (len(R), len(t)))
