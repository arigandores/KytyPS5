"""Session 122 step 3b (HPP-15), ROADMAP s122 item 18 (c): the HEADROOM reading by the measured property of the run's
own base arm instead of the level name.  Edits map122.py, test_map122.py, mut_map122.py in place (LF, write_bytes);
every anchor must occur exactly once, else nothing is written."""
from pathlib import Path

NL = chr(10)
R = Path('C:/kyty/s122')


def apply(path, edits):
    src = path.read_bytes().decode('utf-8')
    assert chr(13) not in src, path
    for old, new in edits:
        c = src.count(old)
        assert c == 1, (path.name, c, old[:80])
        src = src.replace(old, new)
    return src


SC = R / 'map122.py'
sc = apply(SC, [
    # the docstring reading paragraph
    ("Reading (ROADMAP s122 item 17 (d)): on a HEADROOM_LEVELS scene (intro_next: 99.34 % of its frames are one vblank) the\n"
     "slope measures HEADROOM - how much work the frame absorbs before it falls to the next step - and is never quoted as\n"
     "speed: the verdict line says `reading=HEADROOM` and the game-speed line is withheld.  Every verdict line carries the\n",
     "Reading (ROADMAP s122 items 17 (d), 18 (c)): the scene is HEADROOM by the MEASURED property of this run, never by its\n"
     "level name - over the window rows (positions 10..88) of the base-arm (burn=0) blocks of the population pairs (after\n"
     "the outlier drops), the share of frames with dt_us < HEADROOM_DT_US (25 000, midway between one and two vblanks) is\n"
     ">= HEADROOM_SHARE (0.95).  There the slope measures HEADROOM - how much work the frame absorbs before it falls to the\n"
     "next step - and is never quoted as speed: the verdict line says `reading=HEADROOM` and the game-speed line is\n"
     "withheld.  No base-arm window row in the population => `reading=NOT_EVALUABLE` (never HEADROOM) and the game-speed\n"
     "line is withheld as well; otherwise `reading=SPEED`.  Every verdict line carries the\n"),
    ("HEADROOM_LEVELS = ('intro_next',)               # item 17 (d): the slope there is headroom, never speed\n",
     "HEADROOM_DT_US = 25000   # item 18 (c): a frame is 'one vblank' when dt_us < 25 000 (midway between 1 and 2 vblanks)\n"
     "HEADROOM_SHARE = 0.95    # item 18 (c): HEADROOM when >= 0.95 of the base-arm window frames are one vblank\n"),
    # the reading functions, before speed()
    ("def speed(dt):\n",
     "def reading_of(dts):\n"
     "    \"\"\"(reading, share, frames) of the base-arm window dt_us values (ROADMAP s122 item 18 (c)): HEADROOM when the\n"
     "    share of dt_us < HEADROOM_DT_US is >= HEADROOM_SHARE, SPEED otherwise; no value => NOT_EVALUABLE (never\n"
     "    HEADROOM).\"\"\"\n"
     "    if not dts:\n"
     "        return 'NOT_EVALUABLE', None, 0\n"
     "    share = sum(1 for d in dts if d < HEADROOM_DT_US) / float(len(dts))\n"
     "    return ('HEADROOM' if share >= HEADROOM_SHARE else 'SPEED'), share, len(dts)\n"
     "\n"
     "\n"
     "def headroom_of(done, pairs):\n"
     "    \"\"\"The reading of this run from the window rows (positions KEEP) of the base-arm blocks of the population pairs.\"\"\"\n"
     "    return reading_of([r['dt_us'] for pr in pairs for b in pr if done[b]['arm'] == ARM_A for r in done[b]['win']])\n"
     "\n"
     "\n"
     "def speed(dt):\n"),
    ("    speeds = dict(A=speed(dt['A']), B=speed(dt['B']))\n",
     "    reading, fast_share, fast_frames = headroom_of(done, pairs)\n"
     "    speeds = dict(A=speed(dt['A']), B=speed(dt['B']))\n"),
    ("               reading='HEADROOM' if res['level'] in HEADROOM_LEVELS else 'SPEED',\n",
     "               reading=reading, headroom=dict(share=fast_share, frames=fast_frames, dt_us=HEADROOM_DT_US,\n"
     "                                              threshold=HEADROOM_SHARE),\n"),
    # the report
    ("    if res['reading'] == 'HEADROOM':\n"
     "        out.append('game speed: NOT QUOTED - on this scene the slope measures HEADROOM before the next vblank step, '\n"
     "                   'not speed (ROADMAP s122 item 17 (d))')\n"
     "    else:\n",
     "    hr = res['headroom']\n"
     "    out.append('reading %s: base-arm window share of dt_us < %d = %s over %d frames (HEADROOM at >= %s; ROADMAP s122 '\n"
     "               'item 18 (c))' % (res['reading'], hr['dt_us'], fmt(hr['share'], 4), hr['frames'],\n"
     "                                 fmt(hr['threshold'], 2)))\n"
     "    if res['reading'] == 'HEADROOM':\n"
     "        out.append('game speed: NOT QUOTED - on this scene the slope measures HEADROOM before the next vblank step, '\n"
     "                   'not speed (ROADMAP s122 items 17 (d), 18 (c))')\n"
     "    elif res['reading'] != 'SPEED':\n"
     "        out.append('game speed: NOT QUOTED - the reading is NOT EVALUABLE (no base-arm window row in the '\n"
     "                   'population)')\n"
     "    else:\n"),
    ("                 'never a speed (ROADMAP s122 item 17 (d)).')\n",
     "                 'never a speed (ROADMAP s122 items 17 (d), 18 (c)).')\n"),
])

TS = R / 'test_map122.py'
ts = apply(TS, [
    ("    'des122':  dict(level='intro_next', burn=102000),   # the headroom scene (ROADMAP s122 item 17 (d))\n}",
     "    'des122':  dict(level='intro_next', burn=102000),   # item 18 (c): read by its base arm, not by this name\n}"),
    ("# ------------------------------------------------------------------ ROADMAP s122 item 17 (d): headroom, not speed\n"
     "case('headroom_intro_next', dict(OK, verdict='CRITICAL', reading='HEADROOM', level='intro_next',\n"
     "                                 lines_has=['game speed: NOT QUOTED - on this scene the slope measures HEADROOM',\n"
     "                                            'pairs=4 bda=NEW reading=HEADROOM'],\n"
     "                                 lines_not=['game speed (16 667'],\n"
     "                                 last_has=['HEADROOM: the slope here is the work the frame absorbs before it falls to '\n"
     "                                           'the next vblank step, never a speed']),\n"
     "     tag='des122', level='intro_next')\n",
     "# ------------------------------------------------------------------ ROADMAP s122 items 17 (d), 18 (c): headroom by the\n"
     "# measured share of one-vblank frames (dt_us < 25 000) in the base-arm window, never by the level name\n"
     "FAST = lambda base, slow=(): (lambda n, b, arm, i: {} if n <= START else\n"
     "                              {'dt_us': (25000 if (b, i) in slow else base) + (DELTA if arm == 1 else 0)})\n"
     "A_WIN = [(b, i) for b in range(BLOCKS) if arm_of(b) == 0 for i in range(KEEP[0], KEEP[1])]   # 316 base frames\n"
     "HR_LINES = ['game speed: NOT QUOTED - on this scene the slope measures HEADROOM', 'pairs=4 bda=NEW reading=HEADROOM']\n"
     "case('headroom_by_base_arm', dict(OK, verdict='CRITICAL', reading='HEADROOM', level='intro_next',\n"
     "                                  headroom__share=1.0, headroom__frames=4 * WIN,\n"
     "                                  lines_has=HR_LINES + ['reading HEADROOM: base-arm window share of dt_us < 25000 = '\n"
     "                                                        '1.0000 over 316 frames (HEADROOM at >= 0.95; ROADMAP s122 '\n"
     "                                                        'item 18 (c))'],\n"
     "                                  lines_not=['game speed (16 667'],\n"
     "                                  last_has=['HEADROOM: the slope here is the work the frame absorbs before it falls '\n"
     "                                            'to the next vblank step, never a speed']),\n"
     "     tag='des122', level='intro_next', main=FAST(16800))\n"
     "case('headroom_not_by_name_intro_next', dict(OK, verdict='CRITICAL', reading='SPEED', headroom__share=0.0,\n"
     "                                             lines_has=['game speed (16 667', 'reading=SPEED'],\n"
     "                                             lines_not=['NOT QUOTED'], last_not=['HEADROOM']),\n"
     "     tag='des122', level='intro_next')\n"
     "case('headroom_not_by_name_sky', dict(OK, verdict='CRITICAL', reading='HEADROOM', lines_has=HR_LINES),\n"
     "     main=FAST(16800))\n"
     "# 316 base frames: 15 slow => 301/316 = 0.9525 HEADROOM, 16 slow => 300/316 = 0.9494 SPEED; fast = 24 999\n"
     "case('headroom_edge_15_slow', dict(OK, reading='HEADROOM', headroom__share=301 / 316.0),\n"
     "     main=FAST(24999, A_WIN[:15]))\n"
     "case('headroom_edge_16_slow', dict(OK, reading='SPEED', headroom__share=300 / 316.0,\n"
     "                                   lines_has=['game speed (16 667']),\n"
     "     main=FAST(24999, A_WIN[:16]))\n"
     "# base 24 000 (fast), armed 26 000 (every B frame slow): only the base arm classifies\n"
     "case('headroom_b_arm_slow_ignored', dict(OK, verdict='CRITICAL', reading='HEADROOM', headroom__share=1.0),\n"
     "     main=FAST(24000))\n"
     "case('headroom_outside_window_ignored', dict(OK, verdict='CRITICAL', reading='HEADROOM', headroom__share=1.0),\n"
     "     main=lambda n, b, arm, i: {} if n <= START else\n"
     "     {'dt_us': (40000 if (arm == 0 and not KEEP[0] <= i < KEEP[1]) else 16800) + (DELTA if arm == 1 else 0)})\n"
     "case('headroom_dropped_pair_ignored', dict(OK, verdict='CRITICAL', reading='HEADROOM', pairs=3, dropped_pairs=1,\n"
     "                                           headroom__frames=3 * WIN, headroom__share=1.0),\n"
     "     main=lambda n, b, arm, i: {} if n <= START else\n"
     "     {'dt_us': (600000 if (b, i) == (1, 50) else 40000 if b == 0 else 16800) + (DELTA if arm == 1 else 0)},\n"
     "     min_pairs=3)\n"
     "case('headroom_no_base_arm', dict(admission='ADMITTED', verdict='NOT_EVALUABLE', reading='NOT_EVALUABLE', pairs=0,\n"
     "                                  headroom__share=None, headroom__frames=0,\n"
     "                                  lines_has=['game speed: NOT QUOTED - the reading is NOT EVALUABLE',\n"
     "                                             'reading=NOT_EVALUABLE', 'reading NOT_EVALUABLE: base-arm window share '\n"
     "                                             'of dt_us < 25000 = - over 0 frames'],\n"
     "                                  lines_not=['game speed (16 667', 'reading=HEADROOM']),\n"
     "     main=FAST(16800), drop=tuple(('main', F(b, 40)) for b in range(BLOCKS) if arm_of(b) == 0))\n"
     "check('reading_of_edges', tuple(mod.reading_of(d)[:2] for d in (\n"
     "    [24999] * 950 + [25000] * 50, [24999] * 949 + [25000] * 51, [25000] * 1000, [24999] * 1000, [])),\n"
     "    (('HEADROOM', 0.95), ('SPEED', 0.949), ('SPEED', 0.0), ('HEADROOM', 1.0), ('NOT_EVALUABLE', None)))\n"
     "check('reading_of_frames', (mod.reading_of([1, 2, 3])[2], mod.reading_of([])[2]), (3, 0))\n"
     "check('headroom_constants', (mod.HEADROOM_DT_US, mod.HEADROOM_SHARE), (25000, 0.95))\n"),
])

MU = R / 'mut_map122.py'
mu = apply(MU, [
    ("    # ---- ROADMAP s122 item 17 (d) / (e): headroom reading, the BDA regime on every verdict line\n"
     "    ('headroom_levels_empty', \"HEADROOM_LEVELS = ('intro_next',)\", 'HEADROOM_LEVELS = ()'),\n"
     "    ('reading_always_speed', \"               reading='HEADROOM' if res['level'] in HEADROOM_LEVELS else 'SPEED',\",\n"
     "     \"               reading='SPEED',\"),\n",
     "    # ---- ROADMAP s122 items 17 (d) / (e), 18 (c): headroom reading by the base arm, the BDA regime on every verdict line\n"
     "    ('hr_dt_24999', 'HEADROOM_DT_US = 25000 ', 'HEADROOM_DT_US = 24999 '),\n"
     "    ('hr_dt_25001', 'HEADROOM_DT_US = 25000 ', 'HEADROOM_DT_US = 25001 '),\n"
     "    ('hr_share_094', 'HEADROOM_SHARE = 0.95 ', 'HEADROOM_SHARE = 0.94 '),\n"
     "    ('hr_share_096', 'HEADROOM_SHARE = 0.95 ', 'HEADROOM_SHARE = 0.96 '),\n"
     "    ('hr_lt_le', '    share = sum(1 for d in dts if d < HEADROOM_DT_US) / float(len(dts))',\n"
     "     '    share = sum(1 for d in dts if d <= HEADROOM_DT_US) / float(len(dts))'),\n"
     "    ('hr_ge_gt', \"    return ('HEADROOM' if share >= HEADROOM_SHARE else 'SPEED'), share, len(dts)\",\n"
     "     \"    return ('HEADROOM' if share > HEADROOM_SHARE else 'SPEED'), share, len(dts)\"),\n"
     "    ('hr_empty_speed', \"        return 'NOT_EVALUABLE', None, 0\", \"        return 'SPEED', None, 0\"),\n"
     "    ('hr_empty_headroom', \"        return 'NOT_EVALUABLE', None, 0\", \"        return 'HEADROOM', None, 0\"),\n"
     "    ('hr_frames_off', \"    return ('HEADROOM' if share >= HEADROOM_SHARE else 'SPEED'), share, len(dts)\",\n"
     "     \"    return ('HEADROOM' if share >= HEADROOM_SHARE else 'SPEED'), share, len(dts) - 1\"),\n"
     "    ('hr_arm_b', \"for pr in pairs for b in pr if done[b]['arm'] == ARM_A for r in done[b]['win']])\",\n"
     "     \"for pr in pairs for b in pr if done[b]['arm'] == ARM_B for r in done[b]['win']])\"),\n"
     "    ('hr_both_arms', \"for pr in pairs for b in pr if done[b]['arm'] == ARM_A for r in done[b]['win']])\",\n"
     "     \"for pr in pairs for b in pr for r in done[b]['win']])\"),\n"
     "    ('hr_all_frames', \"for pr in pairs for b in pr if done[b]['arm'] == ARM_A for r in done[b]['win']])\",\n"
     "     \"for pr in pairs for b in pr if done[b]['arm'] == ARM_A \"\n"
     "     \"for r in [dict(dt_us=parsed_dts[n]) for n in block_frames(b)]])\"),\n"
     "    ('hr_all_blocks', \"    return reading_of([r['dt_us'] for pr in pairs for b in pr if done[b]['arm'] == ARM_A \"\n"
     "     \"for r in done[b]['win']])\",\n"
     "     \"    return reading_of([r['dt_us'] for b in done if done[b]['arm'] == ARM_A for r in done[b]['win']])\"),\n"
     "    ('reading_always_speed', '               reading=reading, headroom=dict(',\n"
     "     \"               reading='SPEED', headroom=dict(\"),\n"
     "    ('reading_by_name', '               reading=reading, headroom=dict(',\n"
     "     \"               reading='HEADROOM' if res['level'] == 'intro_next' else reading, headroom=dict(\"),\n"
     "    ('rep_reading_line', \"               'item 18 (c))' % (res['reading'], hr['dt_us'], fmt(hr['share'], 4), hr['frames'],\",\n"
     "     \"               'item 18 (c))' % (res['reading'], hr['dt_us'], fmt(hr['share'], 3), hr['frames'],\"),\n"
     "    ('rep_speed_on_ne', \"    elif res['reading'] != 'SPEED':\", \"    elif False:\"),\n"),
])
# hr_all_frames needs a name that exists: it mutates to an undefined name on purpose => a crash of the suite kills it;
# replace it by a real, compiling mutant: every window row of the A blocks of ALL complete blocks is hr_all_blocks,
# so drop hr_all_frames here (a NameError mutant is killed trivially and pins nothing).
start = mu.index("    ('hr_all_frames',")
end = mu.index("    ('hr_all_blocks',")
mu = mu[:start] + mu[end:]

for p, s in ((SC, sc), (TS, ts), (MU, mu)):
    p.write_bytes(s.encode('utf-8'))
    print('wrote', p.name, len(s))
