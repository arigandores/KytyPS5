"""Session 111: derive shp111.py (scorer of pred/03_shp111.md, the SHIP run of knob `daslot`, ABBA daslot=0|1) from
session 110's shp110.py (the unpinned staging copy, sha256 pinned below).  Copied and edited, not imported.  Every
edit is an anchored replace that must match exactly once (the docstring: an exact split on its delimiters with its
first and last text asserted); anchors that must survive unchanged are asserted too.  The estimator change (the MAIN
estimator = rows 10..89 of each block, the session-110 window 60..88 printed as `secondary`) is three new functions
inserted before evaluate() (paired / ship_rules / secondary: the pairing and S1/S2 code moved verbatim) plus anchored
call-site edits.  Output bytes are LF / utf-8, written in binary, so two runs give the same bytes.
    python make_shp111.py [<src shp110.py> [<dst shp111.py>]]
"""
import hashlib
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/shp110/shp110.py'
DST = sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/s106_stage/shp111/shp111.py'
SRC_SHA = '139ad38329225aaededaedd591e0b55d3e679e4d2ab79fd96fc71ebcdbd71e94'
raw = open(SRC, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != SRC_SHA:
    raise SystemExit('source %s sha256 %s, pinned %s' % (SRC, got, SRC_SHA))
text = raw.decode('utf-8')
if chr(13) in text:
    raise SystemExit('source carries CR bytes')


def rep(old, new, count=1):
    global text
    n = text.count(old)
    if n != count:
        raise SystemExit('anchor found %d times (want %d): %r' % (n, count, old[:90]))
    text = text.replace(old, new)


def keep(old, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit('kept anchor found %d times (want %d): %r' % (n, count, old[:90]))


# ---- the module docstring: replaced whole (exact split, first and last text asserted) -----------------------------
head, old_doc, rest = text.split('"""', 2)
if head != '' or not old_doc.startswith('Session 110, the SHIP run of knob `cspfree` (the walker thread') \
        or not old_doc.endswith('decision term reads it (derived(), block_means(), pair stats and the summary only).\n'):
    raise SystemExit('the source docstring is not the pinned one')
NEW_DOC = '''Session 111, the SHIP run of knob `daslot` (QueueDrawAhead - the walker thread's M1 queueing - takes only its own
ahead_queue_mutex, with per-slot guards, instead of PipelineCache::m_mutex; design109 A, ROADMAP s0.1 "session 111"
item 2), ABBA `daslot=0|1` with `dawalk=1 dawalklead=1` in both arms, shipping configuration (compute precache on,
knob cspfree=1 by default in BOTH arms), sealed to pred/03_shp111.md.  Derived from session 110's shp110.py (copied,
not imported; make_shp111.py) for the build c8235c90, whose FrameTrace-x rows add da_guard_busy, da_q_taking,
da_hint_defer, da_hint_torn, da_slot_bad, da_q_free, da_chk_ok and da_chk_bad after cs_sync_wait_us (all in the
schema); predictions K1-K6.

    python C:/kyty/s111/shp111.py shp111 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s111/shp111.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Estimator (the executor's decision after session 110, ROADMAP s0.1 item 1; audit110 MAJOR-1): the MAIN estimator is
rows 10..89 of each 90-frame block (KEEP_LO, KEEP_HI = 10, 90).  The ship rule S1/S2, the pair statistics, BANDS,
WORK_SPLIT, AREA_SELECTED, the arm levels, the arming totals and the predictions read it.  The session-110 window,
rows 60..88 (SECONDARY_LO, SECONDARY_HI = 60, 89), is computed with its own selection exactly as shp110.py did and
printed as `secondary` (pair statistics and the S1/S2 values it would give); no admission or decision term reads it.
Pairing is unchanged: whole ABBA quartets, the others excluded as edge blocks.

Ship rule (ROADMAP, decision after session 104; session 108 items 1-2; decision after session 110 item 1): SHIP
daslot=1 as the new default only if the run is ADMITTED - including SYNC_COMPILE: over all rows from frame 2100, sum
cs_sync_new of arm 1 <= that of arm 0 + 2 - and S1 d mean dt_us (main estimator) <= -100 us and S2 its 2SE excludes
0, and the video pass vss111 (gate file gates_slot1.txt = gates_base.txt + daslot=1, pinned, >= 3000 frames, 0
one-frame glitches) reads PASS.  Arming (under control ARMING): the walk checks (unchanged); SLOT_DARK_ARM0 (arm-0
kept rows: sum da_q_free = 0); SLOT_ARMED_ARM1 (arm-1 level of da_q_free >= 1); SLOT_NO_BAD (sum da_slot_bad = 0 over
all rows); DEFAULTS_ON (cspfree_hit level >= 1 in both arms and sum cspfree_bad = 0 over all rows); INSTRUMENTS_DARK.
d cpu_net_us is reported, never deciding: no admission or decision term reads it (derived(), block_means(), pair
stats and the summary only).
'''
text = '"""' + NEW_DOC + '"""' + rest

# ---- constants ---------------------------------------------------------------------------------------------------
rep("PRODUCTION_ROOT = 'C:/kyty/s110'", "PRODUCTION_ROOT = 'C:/kyty/s111'")
rep("PRED = 'C:/kyty/s110/pred/03_shp110.md'", "PRED = 'C:/kyty/s111/pred/03_shp111.md'")
keep("PRED_SHA = None          # filled by the executor when pred/03 is sealed")
keep("PRED_BYTES = None        # filled by the executor when pred/03 is sealed")
rep("BINARY_SHA = 'b3f7a2c957dd344bfd140fe6d04eb2b95ac9387d01dabf5b7dde42b6765b6a82'",
    "BINARY_SHA = 'c8235c902e08d00782d0cff23528361d194a501ad1899344ca8302c742372a86'")
rep("GATES_FILE = 'C:/kyty/s110/gates_base.txt'", "GATES_FILE = 'C:/kyty/s111/gates_base.txt'")
keep("GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'")
keep("PERIOD, START, FIRST_FRAME = 90, 1800, 2100")
rep("KEEP_LO, KEEP_HI = 60, 89\n",
    "KEEP_LO, KEEP_HI = 10, 90                  # MAIN estimator: in-block rows 10..89 (decision after session 110)\n"
    "SECONDARY_LO, SECONDARY_HI = 60, 89        # the session-110 window, rows 60..88: printed, never deciding\n")
keep("MIN_PAIRS = 60")
keep("HOLD_S = 600")
rep("ARMS = ('dawalk=1 dawalklead=1 cspfree=0', 'dawalk=1 dawalklead=1 cspfree=1')",
    "ARMS = ('dawalk=1 dawalklead=1 daslot=0', 'dawalk=1 dawalklead=1 daslot=1')")
keep("SCHEDULE = '90+1800:%s|%s' % ARMS")
rep("TAG_RE = r'shp110b?(?:_entry1)?'", "TAG_RE = r'shp111b?(?:_entry1)?'")
keep("SHIP_US = -100.0")
keep("VIDEO_MIN_FRAMES = 3000")
# every FrameTrace-x row of the c8235c90 build carries the eight session-111 counters after cs_sync_wait_us
# (videoOut.cpp, "Session 111: knob "daslot".  Raw counts."): into the schema
rep("""    'cs_sync_new_us': 'x', 'cs_sync_wait_us': 'x',
}""", """    'cs_sync_new_us': 'x', 'cs_sync_wait_us': 'x',
    'da_guard_busy': 'x', 'da_q_taking': 'x', 'da_hint_defer': 'x', 'da_hint_torn': 'x', 'da_slot_bad': 'x',
    'da_q_free': 'x', 'da_chk_ok': 'x', 'da_chk_bad': 'x',
}""")
keep("SYNC_SLACK = 2")
keep("""FATAL = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
         b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:',
         b'AsyncPipelines: skipped draw')""")
keep("""ENV_EXPECTED = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1',""")
rep("size into shp110.py (only --draft runs without a seal)", "size into shp111.py (only --draft runs without a seal)")

# ---- statistics / selection: kept verbatim ---------------------------------------------------------------------------
keep("    sd = statistics.stdev(values)")
keep("    return statistics.median(values) if values else None")
keep("        kept = expected[lo:hi]")
keep("        if len(kept) != hi - lo or min(kept) < first:")

# ---- arming: the FREE_* checks -> SLOT_* and DEFAULTS_ON (the walk checks and INSTRUMENTS_DARK unchanged) -----------
rep('    """pred/03 (the lead105 walk arming plus FREE_DARK_ARM0, FREE_ARMED_ARM1 and FREE_NO_BAD)."""',
    '    """pred/03 (the lead105 walk arming plus SLOT_DARK_ARM0, SLOT_ARMED_ARM1, SLOT_NO_BAD and DEFAULTS_ON)."""')
rep("""    # Session 109: the cspfree knob dark in arm 0 (no lookup, no hit over the kept rows), hitting in arm 1 (level
    # >= 1), and no knob-2 disagreement anywhere (over all rows; knob 1 never verifies, so a non-zero sum means a
    # wrong build or knob).
    look0 = kept_total(rows, sel, arms, 0, 'cspfree_look')
    hit0 = kept_total(rows, sel, arms, 0, 'cspfree_hit')
    checks['FREE_DARK_ARM0'] = look0 == 0 and hit0 == 0
    checks['FREE_ARMED_ARM1'] = bool((lev[1].get('cspfree_hit') or 0) >= 1)
    bad = sum(r.get('cspfree_bad', 0) for r in rows.values())
    checks['FREE_NO_BAD'] = bad == 0
""", """    # Session 111: the daslot knob dark in arm 0 (no QueueDrawAhead call without m_mutex over the kept rows), armed
    # in arm 1 (level >= 1), and no knob-2 slot-key disagreement anywhere (over all rows; knob 1 never verifies,
    # so a non-zero sum means a wrong build or knob).
    free0 = kept_total(rows, sel, arms, 0, 'da_q_free')
    checks['SLOT_DARK_ARM0'] = free0 == 0
    checks['SLOT_ARMED_ARM1'] = bool((lev[1].get('da_q_free') or 0) >= 1)
    bad = sum(r.get('da_slot_bad', 0) for r in rows.values())
    checks['SLOT_NO_BAD'] = bad == 0
    # The shipping configuration: knob cspfree on by default (session 110) in BOTH arms - hitting (level >= 1 in
    # each arm) and never disagreeing (over all rows).
    hits = [lev[a].get('cspfree_hit') for a in (0, 1)]
    free_bad = sum(r.get('cspfree_bad', 0) for r in rows.values())
    checks['DEFAULTS_ON'] = bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0)
""")
keep("    checks['INSTRUMENTS_DARK'] = dark")
rep("""            'free_arm0_kept': {'cspfree_look': look0, 'cspfree_hit': hit0}, 'cspfree_bad_all_rows': bad}""",
    """            'slot_arm0_kept': {'da_q_free': free0}, 'da_slot_bad_all_rows': bad,
            'cspfree_hit_levels': hits, 'cspfree_bad_all_rows': free_bad}""")

# ---- video: vsh110 -> vss111 (the nine checks; the gate-text check names daslot) --------------------------------------
rep('    """pred/03 video pass vsh110 (pinned; gate file gates_free1.txt = gates_base.txt + cspfree=1).  Returns\n'
    '    (state, detail): state in PASS / FAIL / ABSENT."""',
    '    """pred/03 video pass vss111 (pinned; gate file gates_slot1.txt = gates_base.txt + daslot=1).  Returns\n'
    '    (state, detail): state in PASS / FAIL / ABSENT."""')
rep("""        'cspfree_1_in_gate_text': ' dawalk=1 ' in gates and ' cspfree=1 ' in gates,""",
    """        'daslot_1_in_gate_text': ' dawalk=1 ' in gates and ' daslot=1 ' in gates,""")

# ---- the estimator helpers: the pairing and S1/S2 code moved verbatim, and the secondary window ---------------------
rep('''def evaluate(root, tag, draft=False, geometry=None, gates_file=GATES_FILE, video_meta=None,
''', '''def paired(means, sel, arms):
    """The ABBA pair deltas (arm-1 block mean - arm-0 block mean) over PAIR_KEYS and their mean / SE."""
    pairs = []
    for left, right in sel['pairs']:
        a0 = left if arms[left] == 0 else right
        a1 = right if a0 == left else left
        d = {k: means[a1][k] - means[a0][k] for k in PAIR_KEYS
             if means[a0].get(k) is not None and means[a1].get(k) is not None}
        pairs.append({'blocks': [left, right], 'arm0_block': a0, 'arm1_block': a1, 'd': d})
    return pairs, {k: mean_t([p['d'].get(k) for p in pairs]) for k in PAIR_KEYS}


def ship_rules(dt):
    """S1 / S2 of the ship rule on one estimator's d dt_us statistics."""
    return {
        'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,
        'S2_dt_2se_excludes_0': (dt['mean'] is not None and dt['se'] is not None
                                 and dt['mean'] + 2 * dt['se'] < 0),
    }


def secondary(rows, arms, geo):
    """The session-110 estimator: rows SECONDARY_LO..SECONDARY_HI-1 of each block with its own selection and pairs,
    as the session-110 scorer computed it.  Printed as `secondary`; no admission or decision term reads it
    (decision after session 110, item 1)."""
    sel = select(rows, arms, geo['period'], geo['start'], geo['first'], geo['secondary'])
    out = {'window': list(geo['secondary']), 'deciding': False, 'pairs': len(sel['pairs']),
           'blocks': len(sel['blocks']), 'excluded_edge_blocks': sel['excluded_edge_blocks']}
    if not sel['pairs']:
        out.update(pair_stats={}, levels={}, rules_not_deciding={})
        return out
    means = {b: block_means(rows, ns) for b, ns in sel['blocks'].items()}
    lev = arm_levels(means, arms)
    _, stats = paired(means, sel, arms)
    out['pair_stats'] = stats
    out['levels'] = {k: [lev[0].get(k), lev[1].get(k)] for k in ('dt_us', 'cpu_net_us')}
    out['rules_not_deciding'] = ship_rules(stats['dt_us'])
    return out


def evaluate(root, tag, draft=False, geometry=None, gates_file=GATES_FILE, video_meta=None,
''')

# ---- evaluate() ---------------------------------------------------------------------------------------------------
rep("    geo = dict(period=PERIOD, start=START, first=FIRST_FRAME, keep=(KEEP_LO, KEEP_HI))\n",
    "    geo = dict(period=PERIOD, start=START, first=FIRST_FRAME, keep=(KEEP_LO, KEEP_HI),\n"
    "               secondary=(SECONDARY_LO, SECONDARY_HI))\n")
rep("out = {'scorer': 'shp110.py',", "out = {'scorer': 'shp111.py',")
rep("           'geometry': dict(geo, keep=list(geo['keep']))}",
    "           'geometry': dict(geo, keep=list(geo['keep']), secondary=list(geo['secondary']))}")
keep("    controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK")
rep("""    pairs = []
    for left, right in sel['pairs']:
        a0 = left if arms[left] == 0 else right
        a1 = right if a0 == left else left
        d = {k: means[a1][k] - means[a0][k] for k in PAIR_KEYS
             if means[a0].get(k) is not None and means[a1].get(k) is not None}
        pairs.append({'blocks': [left, right], 'arm0_block': a0, 'arm1_block': a1, 'd': d})
    out['pairs'] = pairs
    stats = {k: mean_t([p['d'].get(k) for p in pairs]) for k in PAIR_KEYS}
    out['pair_stats'] = stats

    cpu, dt = stats['cpu_net_us'], stats['dt_us']
    rules = {
        'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,
        'S2_dt_2se_excludes_0': (dt['mean'] is not None and dt['se'] is not None
                                 and dt['mean'] + 2 * dt['se'] < 0),
    }
""", """    # The MAIN estimator (rows KEEP_LO..KEEP_HI-1 of each block): the pair statistics every rule reads.
    pairs, stats = paired(means, sel, arms)
    out['pairs'] = pairs
    out['pair_stats'] = stats
    # The session-110 window (rows SECONDARY_LO..SECONDARY_HI-1): its own selection, printed, read by no term.
    out['secondary'] = secondary(rows, arms, geo)

    cpu, dt = stats['cpu_net_us'], stats['dt_us']
    rules = ship_rules(dt)
""")
rep("""    out['reported']['da_wdepth_arm1'] = lev[1].get('da_wdepth')
""", """    out['reported']['da_wdepth_arm1'] = lev[1].get('da_wdepth')
    for k in ('da_q_free', 'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn'):
        out['reported'][k + '_levels'] = [lev[0].get(k), lev[1].get(k)]
""")

# ---- predictions H1-H6 -> K1-K6 (pred/03_shp111) --------------------------------------------------------------------
rep("""    add('H1', 'arm-1 cspfree_hit level in [200, 270] a flip', lev[1].get('cspfree_hit'), 200, 270)
    add('H2', 'arm-1 cspf_have level <= 30 a flip (most prefetches return before the lock)',
        lev[1].get('cspf_have'), None, 30)
    add('H3', 'd mean dt_us in [-300, 0] us', stats['dt_us']['mean'], -300, 0)
    add('H4', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, medium confidence',
        stats['dt_us']['mean'], None, SHIP_US)
    add('H5', 'd da_miss in [-30, +30] a flip', stats['da_miss']['mean'], -30, 30)
    add('H6', 'd gpu_busy_us in [0, +150] us a flip (the mid-pass-upload side effect)',
        stats['gpu_busy_us']['mean'], 0, 150)""",
    """    add('K1', 'arm-1 da_q_free level in [800, 1400] a flip (every QueueDrawAhead call off m_mutex)',
        lev[1].get('da_q_free'), 800, 1400)
    add('K2', 'arm-0 da_q_free level = 0 (the knob dark)', lev[0].get('da_q_free'), 0, 0)
    add('K3', 'd mean dt_us (main estimator, rows 10..89) in [-400, 0] us', stats['dt_us']['mean'], -400, 0)
    add('K4', 'd mean dt_us (main estimator) <= -100 us (the ship bar) - the discriminating prediction, '
        'medium-low confidence', stats['dt_us']['mean'], None, SHIP_US)
    add('K5', 'd da_miss in [-40, +40] a flip', stats['da_miss']['mean'], -40, 40)
    add('K6', 'arm-1 da_guard_busy level <= 5 a flip', lev[1].get('da_guard_busy'), None, 5)""")
keep("    return v is not None and (lo is None or v >= lo) and (hi is None or v <= hi)")

# ---- verdict texts -------------------------------------------------------------------------------------------------
rep("v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP cspfree=0 (run not admitted)'",
    "v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP daslot=0 (run not admitted)'")
rep("v = 'KEEP cspfree=0 (ship rule S1-S2 on mean dt not met)'",
    "v = 'KEEP daslot=0 (ship rule S1-S2 on mean dt not met)'")
rep("v = 'SHIP cspfree=1 as the new default (a new build: its video pass is owed, ROADMAP 6)'",
    "v = 'SHIP daslot=1 as the new default (a new build: its video pass is owed, ROADMAP 6)'")
rep("v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vsh110 is read)'",
    "v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vss111 is read)'")
rep("v = 'KEEP cspfree=0 (video pass failed)'", "v = 'KEEP daslot=0 (video pass failed)'")
rep("""                                  'gain from d cpu_net_us alone; that route A is licensed by this run')""",
    """                                  'gain from d cpu_net_us alone; that route A is licensed by this run; a size '
                                  'read from the secondary 60-88 window')""")

# ---- summary (report only) -------------------------------------------------------------------------------------------
rep("lines = ['shp110.py %s status=%s seal=%s'", "lines = ['shp111.py %s status=%s seal=%s'")
rep("""        lines.append('  cspfree arm-0 kept totals %s  cspfree_bad over all rows %s'
                     % (a.get('free_arm0_kept'), a.get('cspfree_bad_all_rows')))""",
    """        lines.append('  daslot arm-0 kept totals %s  da_slot_bad over all rows %s  cspfree_hit levels %s  '
                     'cspfree_bad over all rows %s'
                     % (a.get('slot_arm0_kept'), a.get('da_slot_bad_all_rows'), a.get('cspfree_hit_levels'),
                        a.get('cspfree_bad_all_rows')))""")
rep("""                  'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth', 'cspfree_look', 'cspfree_hit',
                  'cspfree_spec_miss', 'cspf_have', 'cspf_new'):""",
    """                  'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth', 'da_qcall', 'da_q_free',
                  'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'cspfree_hit', 'cspf_have',
                  'cspf_new'):""")
rep("""    for k in ('cpu_net_us', 'dt_us', 'da_take_us', 'da_miss', 'da_late', 'da_hit', 'da_stale',
              'da_walk_us', 'gpu_busy_us'):
        s = (out.get('pair_stats') or {}).get(k)
        if s and s.get('n'):
            lines.append('  d %-12s mean %s  2SE %s  t %s  n %d'
                         % (k, fmt(s['mean']), fmt(2 * s['se'] if s['se'] else None),
                            fmt(s['t'], 2), s['n']))
""", """    if out.get('pair_stats'):
        keep = (out.get('geometry') or {}).get('keep') or [KEEP_LO, KEEP_HI]
        lines.append('  main estimator (decides): rows %d..%d of each block' % (keep[0], keep[1] - 1))
    for k in ('cpu_net_us', 'dt_us', 'da_take_us', 'da_miss', 'da_late', 'da_hit', 'da_stale',
              'da_walk_us', 'gpu_busy_us'):
        s = (out.get('pair_stats') or {}).get(k)
        if s and s.get('n'):
            lines.append('  d %-12s mean %s  2SE %s  t %s  n %d'
                         % (k, fmt(s['mean']), fmt(2 * s['se'] if s['se'] else None),
                            fmt(s['t'], 2), s['n']))
    sec = out.get('secondary')
    if sec:
        lines.append('  secondary estimator (rows %d..%d, never deciding): pairs %d, blocks %d, excluded %s'
                     % (sec['window'][0], sec['window'][1] - 1, sec['pairs'], sec['blocks'],
                        sec['excluded_edge_blocks']))
        for k in ('cpu_net_us', 'dt_us'):
            s = (sec.get('pair_stats') or {}).get(k)
            if s and s.get('n'):
                lines.append('  secondary d %-12s mean %s  2SE %s  t %s  n %d'
                             % (k, fmt(s['mean']), fmt(2 * s['se'] if s['se'] else None),
                                fmt(s['t'], 2), s['n']))
        for k, v in sorted((sec.get('rules_not_deciding') or {}).items()):
            lines.append('  secondary would %s %s (not deciding)' % ('PASS' if v else 'FAIL', k))
""")

# ---- main() ----------------------------------------------------------------------------------------------------------
rep("""    ap.add_argument('--keep', type=parse_keep)
""", """    ap.add_argument('--keep', type=parse_keep)
    ap.add_argument('--secondary', type=parse_keep)
""")
rep("""                                  ('keep', o.keep)) if v is not None}""",
    """                                  ('keep', o.keep), ('secondary', o.secondary)) if v is not None}""")
rep("print('--period/--start/--first/--keep are --draft only')",
    "print('--period/--start/--first/--keep/--secondary are --draft only')")
rep("print('tag %r is not a pred/03 tag (shp110, shp110b, optional _entry1)' % o.tag)",
    "print('tag %r is not a pred/03 tag (shp111, shp111b, optional _entry1)' % o.tag)")
keep("        result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)")

body = text.split('"""', 2)[2]          # the code after the module docstring (which names its source)
for stale in ('shp110', 'vsh110', 'pred/03_shp110', 's110', 'b3f7a2c957dd', 'gates_free1', 'cspfree=0', 'cspfree=1',
              'cspfree_1_in_gate_text', 'FREE_DARK', 'FREE_ARMED', 'FREE_NO_BAD', 'free_arm0_kept',
              "'H1'", "'H2'", "'H3'", "'H4'", "'H5'", "'H6'", 'KEEP_LO, KEEP_HI = 60, 89'):
    if stale in body:
        raise SystemExit('stale text left: %r' % stale)
for fresh in ("'K1'", "'K6'", 'shp111', 'vss111', 'SLOT_DARK_ARM0', 'SLOT_ARMED_ARM1', 'SLOT_NO_BAD', 'DEFAULTS_ON',
              'daslot_1_in_gate_text', "'da_q_free': 'x'", "'da_chk_bad': 'x'", 'SECONDARY_LO, SECONDARY_HI = 60, 89',
              'KEEP_LO, KEEP_HI = 10, 90', 'def paired(', 'def ship_rules(', 'def secondary(',
              "out['secondary'] = secondary(rows, arms, geo)", 'rules = ship_rules(dt)'):
    if fresh not in body:
        raise SystemExit('expected text missing: %r' % fresh)
data = text.encode('utf-8')
with open(DST, 'wb') as handle:
    handle.write(data)
print('written %s %d bytes sha256 %s' % (DST, len(data), hashlib.sha256(data).hexdigest()))
