"""Session 113: derive shn113.py (scorer of pred/02_shn113.md, the ABBA of knob `bdanarrow`: today's bdanarrow=0 in
arm 0 against the candidate bdanarrow=1 in arm 1, OLD regime), its fixtures test_shn113.py and its mutation harness
mut_shn113.py from session 112's net112.py (the SEALED copy in C:/kyty/s112: PRED_SHA / PRED_BYTES are set back to
None here, the executor fills them when pred/02 is sealed), test_net112.py and mut_net112.py (sha256 of all three
pinned below; the copies carried into C:/kyty/s113 were path-rewritten by a port and are NOT the sources).  Copied and
edited, not imported - the same method as make_net112.py: every edit is an anchored replace that must match exactly
once (`rep`); a replaced section is the text between two anchors that each occur exactly once, its old text asserted
to occur exactly once too (`span`); a docstring is an exact split on its delimiters with its first and last text
asserted; anchors that must survive unchanged are asserted (`keep`).  Output bytes are LF / utf-8, written in binary,
so two runs give the same bytes (the sha256 of each output is printed).
    python make_shn113.py
"""
import hashlib

S112 = 'C:/kyty/s112/'
OUT = 'C:/kyty/s106_stage/'
PINS = {'net112.py': '745b157581a5b6e2b53490b8f6be3f8f0c11792f278ce419cd6239b3bc05c137',
        'test_net112.py': '956397b425843131bbd5a09edafc0df54348e3990c5b9e01e03c4f9153ff36f6',
        'mut_net112.py': '08d91193d5a03bd07df659b177d8618a53a7fad2f0dbb81f29a9b61754dc1a10'}


class Src:
    def __init__(self, name):
        raw = open(S112 + name, 'rb').read()
        got = hashlib.sha256(raw).hexdigest()
        if got != PINS[name]:
            raise SystemExit('source %s sha256 %s, pinned %s' % (name, got, PINS[name]))
        self.name = name
        self.text = raw.decode('utf-8')
        if chr(13) in self.text:
            raise SystemExit('source %s carries CR bytes' % name)

    def rep(self, old, new, count=1):
        n = self.text.count(old)
        if n != count:
            raise SystemExit('%s: anchor found %d times (want %d): %r' % (self.name, n, count, old[:90]))
        self.text = self.text.replace(old, new)

    def keep(self, old, count=1):
        n = self.text.count(old)
        if n != count:
            raise SystemExit('%s: kept anchor found %d times (want %d): %r' % (self.name, n, count, old[:90]))

    def span(self, start, end, new):
        """replace the text from `start` (included) to `end` (excluded); both anchors unique, end after start."""
        for a in (start, end):
            if self.text.count(a) != 1:
                raise SystemExit('%s: span anchor found %d times: %r' % (self.name, self.text.count(a), a[:90]))
        i, j = self.text.index(start), self.text.index(end)
        if j <= i:
            raise SystemExit('%s: span end before start: %r' % (self.name, end[:90]))
        self.rep(self.text[i:j], new)

    def docstring(self, first, last, new):
        head, old_doc, rest = self.text.split('"""', 2)
        if head != '' or not old_doc.startswith(first) or not old_doc.endswith(last):
            raise SystemExit('%s: the source docstring is not the pinned one' % self.name)
        self.text = '"""' + new + '"""' + rest

    def write(self, dst, stale=(), fresh=()):
        body = self.text.split('"""', 2)[2]          # the code after the module docstring (which names its source)
        for s in stale:
            if s in body:
                raise SystemExit('%s: stale text left: %r' % (dst, s))
        for f in fresh:
            if f not in body:
                raise SystemExit('%s: expected text missing: %r' % (dst, f))
        data = self.text.encode('utf-8')
        with open(OUT + dst, 'wb') as handle:
            handle.write(data)
        print('written %s%s %d bytes sha256 %s' % (OUT, dst, len(data), hashlib.sha256(data).hexdigest()))


# =====================================================================================================================
# shn113.py from net112.py
# =====================================================================================================================
s = Src('net112.py')
s.docstring('Session 112, the ABBA `net112`: what knob `daslot=1`',
            'pair stats\nand the summary only).\n',
            '''Session 113, the ABBA `shn113`: knob `bdanarrow` (KYTY_BDA_NARROW_STAMPS) - a buffer registration marks only its own
BDA region stamps stale (1) instead of invalidating every region stamp (0, today: in the OLD regime, a start state of
most runs in which the buffer GC evicts and re-creates buffers ~1.2 times a frame, PrepareBda re-walks ~1 016 extra
4-MiB regions a frame).  Arm 0 = today `dawalk=1 dawalklead=1 bdanarrow=0`; arm 1 = the candidate `dawalk=1
dawalklead=1 bdanarrow=1`.  Shipping configuration otherwise (compute precache on; knobs cspfree=1, daslot=1 and
daguard=1 by default in BOTH arms), sealed to pred/02_shn113.md.  Derived from session 112's net112.py (copied, not
imported; make_shn113.py) for the build 94362eae, whose FrameTrace-x rows add bda_ginv_reg, bda_ginv_map, bda_rinv,
bda_nskip, bda_nwould, bda_nmiss, bda_nxthr and bgc_evict after da_guard_yield (all in the schema; bda_scan, on the
FrameTrace-draw row, joins it); predictions P1-P7, report only, each printed with HIT / MISS.

    python C:/kyty/s113/shn113.py shn113 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s113/shn113.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Estimator (as in net112.py; the executor's decision after session 110, ROADMAP s0.1 item 1): the MAIN estimator is
rows 10..89 of each 90-frame block (KEEP_LO, KEEP_HI = 10, 90).  The rule S1/S2, the pair statistics, BANDS,
WORK_SPLIT, AREA_SELECTED, the arm levels, the arming totals, the quoted size and the predictions read it.  The
session-110 window, rows 60..88 (SECONDARY_LO, SECONDARY_HI = 60, 89), is computed with its own selection and printed
as `secondary` (pair statistics and the S1/S2 values it would give); no admission or decision term reads it.  Pairing:
whole ABBA quartets, the others excluded as edge blocks.

Rule (ROADMAP s0.1, the session-113 records, item 3): d = arm 1 - arm 0 (candidate minus today).  SHIP bdanarrow=1 as
the new default only if the run is ADMITTED - including SYNC_COMPILE: over all rows from frame 2100, sum cs_sync_new
of arm 1 <= that of arm 0 + 2 - and S1 d mean dt_us (main estimator) <= SHIP_US = -100 and S2 d mean + 2SE < 0, and
the video pass vsn113 (gate file gates_narrow1.txt = gates_base.txt + bdanarrow=1, pinned, >= 3000 frames, 0
one-frame glitches) reads PASS; otherwise KEEP bdanarrow=0.  Whenever a pair exists, the quoted size - d mean dt_us
(arm 1 - arm 0) with its 2SE on the main estimator, labelled SIZE_LABEL - is reported (out['reported']['quoted_size']
and the summary); it decides nothing.  Arming (under control ARMING): the walk checks (unchanged); REGIME_OLD_ARM0
(arm-0 level of bda_scan >= REGIME_OLD_SCAN = 500: the run is in the OLD regime - a NEW run is not admitted and the
chain repeats once as shn113b); NARROW_ARMED_ARM1 (arm-1 level of bda_nskip >= 1); NARROW_DARK_ARM0 (arm-0 kept
rows: sum bda_nskip = 0); NARROW_SCAN_ARM1 (arm-1 level of bda_scan <= NARROW_SCAN_MAX = 200); NO_CHECK (sum
bda_nwould = 0 and sum bda_nmiss = 0 over all rows: knob 2 never on); NO_XTHR (sum bda_nxthr = 0 over all rows);
DEFAULTS_ON (cspfree_hit and da_q_free levels >= 1 in both arms, sum cspfree_bad = 0 and sum da_slot_bad = 0 over
all rows); INSTRUMENTS_DARK.  d cpu_net_us is reported, never deciding: no admission or decision term reads it
(derived(), block_means(), pair stats and the summary only).
''')

# ---- constants ---------------------------------------------------------------------------------------------------
s.rep("PRODUCTION_ROOT = 'C:/kyty/s112'", "PRODUCTION_ROOT = 'C:/kyty/s113'")
s.rep("PRED = 'C:/kyty/s112/pred/02_net112.md'", "PRED = 'C:/kyty/s113/pred/02_shn113.md'")
# the sealed copy's values go back to None: the executor fills them when pred/02 is sealed (make_net112's draft form)
s.rep("PRED_SHA = 'f5269a7b4f3968157d0ee6a4acbdce580dbb4d0d708958a795e9a51c86fd7651'   # pred/02_net112.md sealed",
      "PRED_SHA = None          # filled by the executor when pred/02 is sealed")
s.rep("PRED_BYTES = 4280       # pred/02_net112.md sealed",
      "PRED_BYTES = None        # filled by the executor when pred/02 is sealed")
s.rep("BINARY_SHA = 'b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7'",
      "BINARY_SHA = '94362eae5e28fa68c6a9d5ed921510a1fb1caa2868b0aa220099ba333df4da92'")
s.rep("GATES_FILE = 'C:/kyty/s112/gates_base.txt'", "GATES_FILE = 'C:/kyty/s113/gates_base.txt'")
s.keep("GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'")
s.keep("PERIOD, START, FIRST_FRAME = 90, 1800, 2100")
s.keep("KEEP_LO, KEEP_HI = 10, 90                  # MAIN estimator: in-block rows 10..89 (decision after session 110)")
s.keep("SECONDARY_LO, SECONDARY_HI = 60, 89        # the session-110 window, rows 60..88: printed, never deciding")
s.keep("MIN_PAIRS = 60")
s.keep("HOLD_S = 600")
s.rep("ARMS = ('dawalk=1 dawalklead=1 daslot=1 daguard=1', 'dawalk=1 dawalklead=1 daslot=0 daguard=0')",
      "ARMS = ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=1')")
s.keep("SCHEDULE = '90+1800:%s|%s' % ARMS")
s.rep("TAG_RE = r'net112b?(?:_entry1)?'", "TAG_RE = r'shn113b?(?:_entry1)?'")
s.rep("SHIP_US = 0.0             # on d mean dt_us = arm 1 - arm 0: the revert bar (ROADMAP, decision after session 111)\n"
      "GAIN_LABEL = (\"session 111's gain against the pre-session profile (arm 0 - arm 1 = -(d mean dt_us), main \"\n"
      "              'estimator; negative: daslot=1 faster)')\n",
      "SHIP_US = -100.0          # on d mean dt_us = arm 1 - arm 0 (ROADMAP, decision after session 104; s113 item 3)\n"
      "SIZE_LABEL = 'bdanarrow=1 against bdanarrow=0 of build 94362eae, OLD regime, main estimator'\n"
      "REGIME_OLD_SCAN = 500     # arm-0 level of bda_scan at or above it: the run is in the OLD regime (s113 item 3)\n"
      "NARROW_SCAN_MAX = 200     # arm-1 level of bda_scan at or below it: the narrow stamps took (s113 item 3)\n")
s.keep("VIDEO_MIN_FRAMES = 3000")
s.keep("ID_TOL = 0.01")
s.keep("AREA_SPLIT_PCT, AREA_MATCH_PCT, AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8")
# the draw row's bda_scan (the region walks of PrepareBda, videoOut.cpp FrameTrace-draw) joins the schema, and every
# FrameTrace-x row of the 94362eae build carries the eight session-113 counters after da_guard_yield (patch_s113.py,
# knob "bdanarrow"): into the schema
s.rep("""    'da_late': 'draw', 'da_stale': 'draw', 'da_stale_old': 'draw', 'da_busy': 'draw',
""", """    'da_late': 'draw', 'da_stale': 'draw', 'da_stale_old': 'draw', 'da_busy': 'draw',
    'bda_scan': 'draw',
""")
s.rep("""    'da_q_noguard': 'x', 'da_guard_yield': 'x',
}""", """    'da_q_noguard': 'x', 'da_guard_yield': 'x',
    'bda_ginv_reg': 'x', 'bda_ginv_map': 'x', 'bda_rinv': 'x', 'bda_nskip': 'x', 'bda_nwould': 'x', 'bda_nmiss': 'x',
    'bda_nxthr': 'x', 'bgc_evict': 'x',
}""")
s.keep("SYNC_SLACK = 2")
s.keep("""FATAL = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
         b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:',
         b'AsyncPipelines: skipped draw')""")
s.keep("""ENV_EXPECTED = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1',""")
s.rep("size into net112.py (only --draft runs without a seal)", "size into shn113.py (only --draft runs without a seal)")

# ---- ratio() served only N1 / N2: gone with them -----------------------------------------------------------------
s.rep("""def ratio(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def new_counts():""", """def new_counts():""")

# ---- statistics / selection / protocol: kept verbatim ------------------------------------------------------------------
s.keep("    sd = statistics.stdev(values)")
s.keep("    return statistics.median(values) if values else None")
s.keep("        kept = expected[lo:hi]")
s.keep("        if (a.get('hold_s') or 0) < HOLD_S - 5:")
s.keep("        if a0['n'] < min_flips or a1['n'] < min_flips:")

# ---- arming: the session-112 SLOT_* / NOGUARD_* / SLOT_NO_BAD terms -> the session-113 terms; DEFAULTS_ON + daslot ----
s.rep('    """pred/02 (the lead105 walk arming plus SLOT_ARMED_ARM0, SLOT_DARK_ARM1, NOGUARD_ARMED_ARM1, NOGUARD_DARK_ARM0,\n'
      '    SLOT_NO_BAD and DEFAULTS_ON)."""',
      '    """pred/02 (the lead105 walk arming plus REGIME_OLD_ARM0, NARROW_ARMED_ARM1, NARROW_DARK_ARM0, NARROW_SCAN_ARM1,\n'
      '    NO_CHECK, NO_XTHR and DEFAULTS_ON)."""')
s.span("    # Session 112: arm 0 (today's default daslot=1 daguard=1) queues off m_mutex (da_q_free level >= 1) and never\n",
       "    dark = all(kept_total(rows, sel, arms, a, k) == 0 for a in (0, 1) for k in DARK_KEYS)\n",
       """    # Session 113: the run is in the OLD regime (arm-0 level of bda_scan >= REGIME_OLD_SCAN; a NEW run is not
    # admitted - the chain repeats once as shn113b); knob 1 skips registration invalidations in arm 1 (bda_nskip level
    # >= 1) and never in arm 0 (no bda_nskip over its kept rows); arm 1 walks few regions (bda_scan level <=
    # NARROW_SCAN_MAX); knob 2's check never ran (no bda_nwould / bda_nmiss over all rows) and no registration was
    # marked on a thread other than the scanning one (no bda_nxthr over all rows).  A missing level fails its check.
    scan = [lev[a].get('bda_scan') for a in (0, 1)]
    checks['REGIME_OLD_ARM0'] = scan[0] is not None and scan[0] >= REGIME_OLD_SCAN
    checks['NARROW_ARMED_ARM1'] = bool((lev[1].get('bda_nskip') or 0) >= 1)
    nskip0 = kept_total(rows, sel, arms, 0, 'bda_nskip')
    checks['NARROW_DARK_ARM0'] = nskip0 == 0
    checks['NARROW_SCAN_ARM1'] = scan[1] is not None and scan[1] <= NARROW_SCAN_MAX
    would = sum(r.get('bda_nwould', 0) for r in rows.values())
    miss = sum(r.get('bda_nmiss', 0) for r in rows.values())
    checks['NO_CHECK'] = would == 0 and miss == 0
    xthr = sum(r.get('bda_nxthr', 0) for r in rows.values())
    checks['NO_XTHR'] = xthr == 0
    # The shipping configuration in BOTH arms: knob cspfree on by default (session 110) - hitting (level >= 1 in each
    # arm) and never disagreeing (over all rows) - and knob daslot=1 by default (session 111) - queueing off m_mutex
    # (da_q_free level >= 1 in each arm) and never disagreeing on a slot key (da_slot_bad over all rows).
    hits = [lev[a].get('cspfree_hit') for a in (0, 1)]
    free_bad = sum(r.get('cspfree_bad', 0) for r in rows.values())
    qfree = [lev[a].get('da_q_free') for a in (0, 1)]
    slot_bad = sum(r.get('da_slot_bad', 0) for r in rows.values())
    checks['DEFAULTS_ON'] = bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0
                                 and (qfree[0] or 0) >= 1 and (qfree[1] or 0) >= 1 and slot_bad == 0)
""")
s.keep("    checks['INSTRUMENTS_DARK'] = dark")
s.rep("""            'slot_arm1_kept': {'da_q_free': free1}, 'noguard_arm0_kept': {'da_q_noguard': noguard0},
            'da_slot_bad_all_rows': bad,
            'cspfree_hit_levels': hits, 'cspfree_bad_all_rows': free_bad}
""", """            'bda_scan_levels': scan, 'narrow_arm0_kept': {'bda_nskip': nskip0},
            'bda_nwould_all_rows': would, 'bda_nmiss_all_rows': miss, 'bda_nxthr_all_rows': xthr,
            'cspfree_hit_levels': hits, 'cspfree_bad_all_rows': free_bad, 'da_q_free_levels': qfree,
            'da_slot_bad_all_rows': slot_bad}
""")

# ---- video: vnet112 -> vsn113 (the nine checks; the gate-text check names the candidate's knob) -----------------------
s.rep('    """pred/02 video pass vnet112 (pinned; gate file gates_guard0.txt = gates_base.txt + daslot=0 daguard=0).\n'
      '    Returns (state, detail): state in PASS / FAIL / ABSENT."""',
      '    """pred/02 video pass vsn113 (pinned; gate file gates_narrow1.txt = gates_base.txt + bdanarrow=1).  Returns\n'
      '    (state, detail): state in PASS / FAIL / ABSENT."""')
s.rep("""        'daguard_0_in_gate_text': ' dawalk=1 ' in gates and ' daslot=0 ' in gates and ' daguard=0 ' in gates,""",
      """        'bdanarrow_1_in_gate_text': ' dawalk=1 ' in gates and ' bdanarrow=1 ' in gates,""")
s.keep("        'frames': frames is not None and frames >= VIDEO_MIN_FRAMES,")

# ---- the rule: S1 at the bar -100 (its session-111 name back), S2 unchanged; the quoted size ---------------------------
s.rep('''    """S1 / S2 of the rule to ship the candidate (arm 1: revert the default) on one estimator's d dt_us statistics."""
    return {
        'S1_dt_le_0': dt['mean'] is not None and dt['mean'] <= SHIP_US,''',
      '''    """S1 / S2 of the ship rule on one estimator's d dt_us statistics."""
    return {
        'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,''')
s.span('def s111_gain(dt):', 'def secondary(rows, arms, geo):', '''def quoted_size(dt):
    """The quoted size (pred/02): d mean dt_us = arm 1 - arm 0 with its 2SE, from one estimator's d dt_us statistics
    (us a flip; negative: bdanarrow=1 faster), labelled SIZE_LABEL.  Report only: no admission or decision term reads
    it."""
    return {'mean': dt['mean'], 'two_se': 2 * dt['se'] if dt['se'] is not None else None, 'n': dt['n'],
            'label': SIZE_LABEL}


''')

# ---- evaluate() ---------------------------------------------------------------------------------------------------
s.rep("out = {'scorer': 'net112.py',", "out = {'scorer': 'shn113.py',")
s.keep("    # Session 108 guard, kept verbatim (pred/02): the dispatch-time compile guard over ALL rows from the first\n")
s.keep("    controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK")
s.keep("    rules = ship_rules(dt)")
s.rep("""    for k in ('da_q_free', 'da_q_noguard', 'da_guard_busy', 'da_guard_yield', 'da_q_taking', 'da_hint_defer',
              'da_hint_torn'):
        out['reported'][k + '_levels'] = [lev[0].get(k), lev[1].get(k)]
    # The quoted size (pred/02 s4), main estimator, report only.
    out['reported']['s111_gain_vs_pre_session'] = s111_gain(dt)
""", """    for k in ('bda_scan', 'bda_nskip', 'bda_ginv_reg', 'bda_ginv_map', 'bda_rinv', 'bgc_evict', 'da_q_free',
              'da_q_noguard', 'da_guard_busy', 'da_guard_yield'):
        out['reported'][k + '_levels'] = [lev[0].get(k), lev[1].get(k)]
    # The quoted size (pred/02), main estimator, report only.
    out['reported']['quoted_size'] = quoted_size(dt)
""")

# ---- predictions N1-N7 -> P1-P7 (pred/02_shn113) --------------------------------------------------------------------
s.rep("""    add('N1', 'arm-1 walker time per QueueDrawAhead call (level da_queue_us / level da_qcall) in [0.90, 1.12] us',
        ratio(lev[1].get('da_queue_us'), lev[1].get('da_qcall')), 0.90, 1.12)
    add('N2', 'arm-0 walker time per QueueDrawAhead call (level da_queue_us / level da_qcall) in [1.00, 1.30] us',
        ratio(lev[0].get('da_queue_us'), lev[0].get('da_qcall')), 1.00, 1.30)
    add('N3', 'd mean dt_us (arm 1 - arm 0, main estimator, rows 10..89) in [0, 300] us',
        stats['dt_us']['mean'], 0, 300)
    add('N4', "d mean dt_us (main estimator) >= +100 us (session 111's gain against the pre-session profile is at "
        'least 100 us) - medium-low confidence', stats['dt_us']['mean'], 100, None)
    add('N5', 'arm-1 da_q_noguard level in [800, 1400] a flip (every QueueDrawAhead call without the guards)',
        lev[1].get('da_q_noguard'), 800, 1400)
    add('N6', 'arm-0 da_q_free level in [800, 1400] a flip (every QueueDrawAhead call off m_mutex)',
        lev[0].get('da_q_free'), 800, 1400)
    add('N7', 'd da_miss in [-40, +40] a flip', stats['da_miss']['mean'], -40, 40)""",
      """    add('P1', 'arm-0 bda_scan level in [800, 1400] a flip (the OLD regime: every region walked again once a frame)',
        lev[0].get('bda_scan'), 800, 1400)
    add('P2', 'arm-1 bda_scan level in [30, 200] a flip (the narrow stamps: the moved regions only)',
        lev[1].get('bda_scan'), 30, 200)
    add('P3', 'd mean dt_us (arm 1 - arm 0, main estimator, rows 10..89) in [-1500, +200] us',
        stats['dt_us']['mean'], -1500, 200)
    add('P4', 'd mean dt_us (main estimator) <= -100 us (the ship bar) - the discriminating prediction, low '
        'confidence', stats['dt_us']['mean'], None, -100)
    add('P5', 'd gpu_busy_us in [-150, +150] a flip', stats['gpu_busy_us']['mean'], -150, 150)
    add('P6', 'arm-1 bda_nskip level in [0.5, 3] a flip (the registration invalidations knob 1 skipped)',
        lev[1].get('bda_nskip'), 0.5, 3)
    add('P7', 'd da_miss in [-40, +40] a flip', stats['da_miss']['mean'], -40, 40)""")
s.keep("    return v is not None and (lo is None or v >= lo) and (hi is None or v <= hi)")

# ---- verdict texts -------------------------------------------------------------------------------------------------
s.rep("v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP daslot=1 (run not admitted)'",
      "v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP bdanarrow=0 (run not admitted)'")
s.rep("v = 'KEEP daslot=1 (revert rule S1-S2 on mean dt not met)'",
      "v = 'KEEP bdanarrow=0 (ship rule S1-S2 on mean dt not met)'")
s.rep("v = 'REVERT to daslot=0 daguard=0 as the new default (a new build: its video pass is owed)'",
      "v = 'SHIP bdanarrow=1 as the new default (a new build: its video pass is owed)'")
s.rep("v = 'REVERT_PENDING_VIDEO (S1-S2 met; nothing changes until vnet112 is read)'",
      "v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vsn113 is read)'")
s.rep("v = 'KEEP daslot=1 (video pass failed)'", "v = 'KEEP bdanarrow=0 (video pass failed)'")
s.rep("""                                  'read from the secondary 60-88 window; a gain against a different build; that '
                                  'arm 1 is the session-110 code byte for byte; additivity')""",
      """                                  'read from the secondary 60-88 window; a gain in the NEW regime or in scenes not '
                                  'measured (the size is an OLD-regime size); that bdanarrow=1 is safe beyond this '
                                  'run; additivity')""")

# ---- summary (report only) -------------------------------------------------------------------------------------------
s.rep("lines = ['net112.py %s status=%s seal=%s'", "lines = ['shn113.py %s status=%s seal=%s'")
s.rep("""        lines.append('  daslot arm-1 kept totals %s  daguard arm-0 kept totals %s  da_slot_bad over all rows %s  '
                     'cspfree_hit levels %s  cspfree_bad over all rows %s'
                     % (a.get('slot_arm1_kept'), a.get('noguard_arm0_kept'), a.get('da_slot_bad_all_rows'),
                        a.get('cspfree_hit_levels'), a.get('cspfree_bad_all_rows')))""",
      """        lines.append('  bdanarrow: bda_scan levels %s  bda_nskip arm-0 kept totals %s  bda_nwould / bda_nmiss / '
                     'bda_nxthr over all rows %s / %s / %s'
                     % (a.get('bda_scan_levels'), a.get('narrow_arm0_kept'), a.get('bda_nwould_all_rows'),
                        a.get('bda_nmiss_all_rows'), a.get('bda_nxthr_all_rows')))
        lines.append('  defaults: cspfree_hit levels %s  cspfree_bad over all rows %s  da_q_free levels %s  '
                     'da_slot_bad over all rows %s'
                     % (a.get('cspfree_hit_levels'), a.get('cspfree_bad_all_rows'), a.get('da_q_free_levels'),
                        a.get('da_slot_bad_all_rows')))""")
s.rep("""                  'da_guard_busy', 'da_guard_yield', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'cspfree_hit',
                  'cspf_have', 'cspf_new'):""",
      """                  'da_guard_busy', 'da_guard_yield', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'cspfree_hit',
                  'cspf_have', 'cspf_new', 'bda_scan', 'bda_nskip', 'bda_ginv_reg', 'bda_ginv_map', 'bda_rinv',
                  'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict'):""")
s.rep("""    gain = (out.get('reported') or {}).get('s111_gain_vs_pre_session')
    if gain:
        lines.append('  quoted size: %s = %s us a flip, 2SE %s, n %d'
                     % (gain['label'], fmt(gain['mean']), fmt(gain['two_se']), gain['n']))
""", """    size = (out.get('reported') or {}).get('quoted_size')
    if size:
        lines.append('  quoted size: d mean dt_us (arm 1 - arm 0) = %s us a flip, 2SE %s, n %d - %s'
                     % (fmt(size['mean']), fmt(size['two_se']), size['n'], size['label']))
""")

# ---- main() ----------------------------------------------------------------------------------------------------------
s.rep("print('tag %r is not a pred/02 tag (net112, net112b, optional _entry1)' % o.tag)",
      "print('tag %r is not a pred/02 tag (shn113, shn113b, optional _entry1)' % o.tag)")
s.keep("        result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)")

s.write('shn113.py',
        stale=('net112', 'C:/kyty/s112', 'b47b58a9', 'daguard_0_in_gate_text', 'SLOT_ARMED_ARM0', 'SLOT_DARK_ARM1',
               'NOGUARD_', 'SLOT_NO_BAD', 'slot_arm1_kept', 'noguard_arm0_kept', 's111_gain', 'GAIN_LABEL',
               "'N1'", "'N2'", "'N3'", "'N4'", "'N5'", "'N6'", "'N7'", 'S1_dt_le_0', 'SHIP_US = 0.0', 'REVERT',
               'def ratio(', 'ratio(lev', 'f5269a7b', 'daguard=0', 'a gain against a different build'),
        fresh=("'P1'", "'P2'", "'P3'", "'P4'", "'P5'", "'P6'", "'P7'", "'scorer': 'shn113.py'", 'vsn113',
               'REGIME_OLD_ARM0', 'NARROW_ARMED_ARM1', 'NARROW_DARK_ARM0', 'NARROW_SCAN_ARM1', "checks['NO_CHECK']",
               "checks['NO_XTHR']", 'bdanarrow_1_in_gate_text', "'bda_scan': 'draw'", "'bgc_evict': 'x'",
               'SHIP_US = -100.0', "'S1_dt_le_-100'", 'def quoted_size(', 'PRED_SHA = None', 'PRED_BYTES = None',
               'REGIME_OLD_SCAN = 500', 'NARROW_SCAN_MAX = 200', 'a gain in the NEW regime', 'SIZE_LABEL'))

# =====================================================================================================================
# test_shn113.py from test_net112.py
# =====================================================================================================================
t = Src('test_net112.py')
t.docstring('Session 112: fixtures for net112.py (the ABBA of today',
            '    python test_net112.py <net112.py> [<fixture dir>]\n',
            '''Session 113: fixtures for shn113.py (the ABBA of knob bdanarrow: today's bdanarrow=0 against the candidate
bdanarrow=1, OLD regime) in NON-draft mode, derived from session 112's test_net112.py by make_shn113.py (same coverage,
adapted: tag shn113, video vsn113, the arms, the 94362eae counters bda_ginv_reg / bda_ginv_map / bda_rinv / bda_nskip /
bda_nwould / bda_nmiss / bda_nxthr / bgc_evict (FrameTrace-x) and bda_scan (FrameTrace-draw), arming REGIME_OLD_ARM0 /
NARROW_ARMED_ARM1 / NARROW_DARK_ARM0 / NARROW_SCAN_ARM1 / NO_CHECK / NO_XTHR and DEFAULTS_ON with its daslot=1 parts,
the ship bar SHIP_US = -100, the quoted size, predictions P1-P7).  Rule (decision after 107, item 2): every decision
term and every admission term gets a fixture where ONLY it fails, plus every verdict branch.  Each case asserts the
exact failing set (failed_controls) AND the exact failing sub-lists: rules, video checks, arming sub-checks (by name,
under control:ARMING), area-mirror criteria where relevant, and the exact protocol error list.  Terms that cannot fail
alone by construction are asserted as exact sets, with the scorer lines that couple them cited at the case.  The seal
check is pointed at a throwaway file and GATES_FILE at a sha-checked copy of gates_base.txt (from C:/kyty/s113, else
C:/kyty/s112 - the same bytes, GATES_SHA asserted); everything else is the scorer's own code.  IDENTITY exists only in
main(): main() is driven in-process with EXE / PRODUCTION_ROOT pointed at fixtures.  CONSTANTS compares every sealed
constant except PRED_SHA / PRED_BYTES, which it only requires to be both None (the draft) or a 64-hex sha256 and a
positive size (the sealed copy), so the sealed scorer stays green on this suite (audit111 MINOR-5).

The window rows the fixtures edit are HARD-CODED here (MAIN = 10..89, SEC = 60..88), never read from the scorer, so a
mutant of the scorer's window cannot move its own fixtures.  The estimator cases (all noise-free, exact values):
  KEEP_edge        arm-1 row 9 +29 000, rows 10 and 89 -8 000: main -350 exactly, secondary -150 exactly (kills
                   KEEP_LO 9 / 11, KEEP_HI 89, the slice shifted down one row).
  SEC_edge         arm-1 rows 59 and 89 +29 000, rows 60 and 88 -2 900: secondary -350 exactly, main +502.5 exactly
                   (KEEP by the main estimator; the secondary would pass - it never decides).
  EST_rows0_9      arm-1 rows 0..9 +29 000 (the audit110 hitch shape): main and secondary -150 exactly (a full-block
                   estimator would read +3 072).
  EST_rows10_59    arm-1 rows 10..59 +800: main +350 exactly (KEEP), secondary -150 exactly (would pass).
  EST_rows10_59_ship  d 0, arm-1 rows 10..59 -400: main -250 exactly (SHIP pending), secondary 0 (would fail both).
  PENDING          the noisy base fixture: main and secondary d mean / SE recounted from the log here, independently
                   of the scorer (1e-9 relative), and they differ; the quoted size is the main d mean with 2 x its SE.
Killers of the session-109 survivors kept: SE_exact (sample SD), LEVEL_median (median block levels: dt, bda_scan in
both arms, bda_nskip), FATAL_waitslow_log / _so.  Plus CONSTANTS (the sealed identity and the two windows), full-text
refusals / pending verdict, tag acceptance (shn113b, shn113_entry1, shn113b_entry1 reach evaluate()) and refusal of
the others (session 112's tags and the video tags included), the draft-only --secondary.  Threshold edges (audit111
MINOR-10: a fixture on each side of every tolerance): the bar (S1_edge -100 and S1_edge_in -100.5 pending; S1_only
-99.5: S1 fails alone, S2 holds; S2_edge_zero: d 0 with SE 0, S2 fails on its edge), the regime (arm-0 bda_scan level 500 passes, 499 fails), the narrow scan (arm-1
bda_scan level 200 passes, 201 fails), the narrow arming (arm-1 bda_nskip level 1 passes, 0.9875 fails), the defaults'
levels (cspfree_hit and da_q_free level 1 pass in both arms, 0.9875 fails in either), the dark and all-rows totals
(NARROW_DARK0_one, NO_CHECK_*, NO_XTHR*, DEFAULTS_slot_bad*, DEFAULTS_bad*: a total of 1 fails, the good run's 0
passes), each per-arm term's lag case (values outside rows 10..89 do not count) and missing level, the attempt hold
(595 s passes, 594 fails), the area mirror's minimum block (8 flips count, 7 do not), the walk identity (0.9 % passes,
1.1 % fails), the video floor (3 000 frames pass, 2 999 fail), and the P1-P7 bands with exact values at and just
outside every edge.
    python test_shn113.py <shn113.py> [<fixture dir>]
''')
t.rep("BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s106_stage/net112/fx')",
      "BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s106_stage/shn113/fx')")
t.rep("spec = importlib.util.spec_from_file_location('net112', SRC)",
      "spec = importlib.util.spec_from_file_location('shn113', SRC)")
t.rep("seal.write_text('fixture seal 112 net', encoding='utf-8')", "seal.write_text('fixture seal 113 shn', encoding='utf-8')")
t.rep("else Path('C:/kyty/s111/gates_base.txt')", "else Path('C:/kyty/s112/gates_base.txt')")
t.rep("TAG = 'net112'", "TAG = 'shn113'")

# ---- make(): the arms of this design (bdanarrow=0 in arm 0, bdanarrow=1 in arm 1; daslot=1 in both) ---------------
t.rep("""         qfree0=1080, qfree1=0, ng0=0, ng1=1080, qq0=1296, qq1=1080, qcall=1080, gb0=1, gb1=2, sync0=1, sync1=1,
         pins=1, pin_mode=1, recs=2, fatal=None,
""", """         qfree0=1080, qfree1=1080, scan0=1068, scan1=52, nskip0=0, nskip1=1, gpu1=12700, gb0=1, gb1=2, sync0=1,
         sync1=1, pins=1, pin_mode=1, recs=2, fatal=None,
""")
t.rep("""    (default noise; the same random draws are taken either way).  The shipping configuration: cspfree on in BOTH
    arms (look/hit per arm).  Arm 0 (today, daslot=1 daguard=1): da_q_free = qfree0 (= da_qcall 1080: every call off
    m_mutex), da_q_noguard = ng0; arm 1 (the candidate, daslot=0 daguard=0): da_q_free = qfree1, da_q_noguard = ng1
    (every call without the guards); the rows before the schedule are arm 0.  da_queue_us qq0 / qq1 and da_qcall
    qcall (both arms): walker us per call 1.2 / 1.0 by default; da_guard_busy gb0 / gb1.\"\"\"""",
      """    (default noise; the same random draws are taken either way).  The shipping configuration in BOTH arms: cspfree
    on (look/hit per arm), daslot=1 (da_q_free qfree0 / qfree1 = da_qcall 1080: every call off m_mutex), daguard=1
    (da_q_noguard 0).  The OLD regime: bda_scan scan0 (arm 0, today: every region walked again once a frame) / scan1
    (arm 1, bdanarrow=1); bda_nskip nskip0 / nskip1 (the registration invalidations knob 1 skipped: 0 in arm 0, 1 a
    flip in arm 1); bda_ginv_reg 1 / 0 a flip, bda_rinv 3 and bgc_evict 1 in both arms; knob 2 off (bda_nwould =
    bda_nmiss = 0), bda_nxthr 0.  gpu_busy_us 12 700 (arm 0) / gpu1 (arm 1); the rows before the schedule are arm 0;
    da_guard_busy gb0 / gb1.\"\"\"""")
t.rep("""            'main': {'n': n, 'dt_us': dt, 'draws': draws, 'dispatches': 268, 'gpu_busy_us': 12700,""",
      """            'main': {'n': n, 'dt_us': dt, 'draws': draws, 'dispatches': 268, 'gpu_busy_us': gpu1 if arm else 12700,""")
t.rep("""                     'da_queue_us': qq1 if arm else qq0, 'da_take_us': 2800, 'da_hit': 8350, 'da_miss': 300,
                     'da_late': 6,
                     'da_stale': 0, 'da_stale_old': 0, 'da_busy': 0},
""", """                     'da_queue_us': 1100, 'da_take_us': 2800, 'da_hit': 8350, 'da_miss': 300, 'da_late': 6,
                     'da_stale': 0, 'da_stale_old': 0, 'da_busy': 0, 'bda_scan': scan1 if arm else scan0},
""")
t.rep("""                  'da_wdepth': 17, 'da_qcall': qcall, 'mw_n': 0,""", """                  'da_wdepth': 17, 'da_qcall': 1080, 'mw_n': 0,""")
t.rep("""                  'da_q_noguard': ng1 if arm else ng0, 'da_guard_yield': 0},
""", """                  'da_q_noguard': 0, 'da_guard_yield': 0, 'bda_ginv_reg': 0 if arm else 1, 'bda_ginv_map': 0,
                  'bda_rinv': 3, 'bda_nskip': nskip1 if arm else nskip0, 'bda_nwould': 0, 'bda_nmiss': 0,
                  'bda_nxthr': 0, 'bgc_evict': 1},
""")

# ---- video(): vsn113, the candidate's gate text -------------------------------------------------------------------
t.rep("""def video(d, frames=3990, glitches=0, gate='daslot=0 daguard=0', pin='1', binary=None, tag='v', rec=True,
          env_extra=None, attempts=None, gates=None):""",
      """def video(d, frames=3990, glitches=0, gate='bdanarrow=1', pin='1', binary=None, tag='v', rec=True, env_extra=None,
          attempts=None, gates=None):""")
t.rep("""    vm = d / ('vnet112_%s.json' % tag)
    vr = d / ('vnet112_%s_glitch.txt' % tag)""", """    vm = d / ('vsn113_%s.json' % tag)
    vr = d / ('vsn113_%s_glitch.txt' % tag)""")
t.rep('"""Drive net112.main() in-process;', '"""Drive shn113.main() in-process;')

# ---- verdicts, rules, bands, messages, counters --------------------------------------------------------------------
t.span("KEEP_NA = 'KEEP daslot=1 (run not admitted)'", "good = make('good')", """KEEP_NA = 'KEEP bdanarrow=0 (run not admitted)'
KEEP_BAR = 'KEEP bdanarrow=0 (ship rule S1-S2 on mean dt not met)'
KEEP_VID = 'KEEP bdanarrow=0 (video pass failed)'
SHIP = 'SHIP bdanarrow=1 as the new default (a new build: its video pass is owed)'
PENDING = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vsn113 is read)'
ARMING = {'control:ARMING'}
BOTH_RULES = ['S1_dt_le_-100', 'S2_dt_2se_excludes_0']
PRED_BANDS = {'P1': [800, 1400], 'P2': [30, 200], 'P3': [-1500, 200], 'P4': [None, -100], 'P5': [-150, 150],
              'P6': [0.5, 3], 'P7': [-40, 40]}
# the quoted size's label, written out here (not read from mod.SIZE_LABEL: a changed label must fail)
SIZE_LABEL = 'bdanarrow=1 against bdanarrow=0 of build 94362eae, OLD regime, main estimator'
# the scorer's markers, written out here (not read from mod.FATAL: a dropped marker must still have its case)
FATAL_TEXTS = ('--- Error ---', '--- Fatal Error ---', '--- std::terminate ---', '--- abort() ---', 'ErrorDeviceLost',
               'Unhandled exception:', 'GpuWaitSlow:', 'AsyncPipelines: skipped draw')
WAITSLOW = 'GpuWaitSlow: tick=51234 waited 2000 ms submit_backlog=0 acopy=12/12/12 acopy_pending=0'
TAG_MSG = "tag %r is not a pred/02 tag (shn113, shn113b, optional _entry1)"
NEW_COUNTERS = ('da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_slot_bad', 'da_q_free',
                'da_chk_ok', 'da_chk_bad', 'da_q_noguard', 'da_guard_yield', 'bda_ginv_reg', 'bda_ginv_map', 'bda_rinv',
                'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict')

""")
t.keep('''    """the seven keys, their sealed bands, the given exact values, and the given hit / miss sets."""''')

# ---- size_exact / pred_good / const_check ---------------------------------------------------------------------------
t.span("def gain_exact(o, mean, two_se):", "# ---- the sealed identity", '''def size_exact(o, mean, two_se):
    """the quoted size in the result (exact) and its summary line (label and format written out here)."""
    size = o['reported']['quoted_size']
    line = ('  quoted size: d mean dt_us (arm 1 - arm 0) = %.1f us a flip, 2SE %.1f, n 110 - %s'
            % (mean, two_se, SIZE_LABEL))
    return (size == {'mean': mean, 'two_se': two_se, 'n': 110, 'label': SIZE_LABEL}
            and line in mod.summary(o).split(NL))


def pred_good(o):
    """P1-P7 of the good fixture: the seven keys, their sealed bands, the fixture's exact values (P1 1 068, P2 52, P5 0,
    P6 1, P7 0; P3 / P4 the main d mean, a SHIP here), all seven hit; the scorer's name in the result and in the summary
    header; both estimators recounted from the log here (1e-9 relative), the secondary's own selection (block 3
    excluded as an edge block there, nothing excluded in the main one), and the two summary lines naming the windows;
    the quoted size = the main d mean with 2 x its SE (result and summary line); the reported and arming bda_scan /
    bda_nskip levels; the area mirror's 110 block pairs; the added must-not-be-claimed item; P4's sealed confidence."""
    dt = main_dt(o)
    m_main, se_main, n_main = recount(good, MAIN)
    m_sec, se_sec, n_sec = recount(good, SEC)
    lines = mod.summary(o).split(NL)
    return (pred_values(o, P1=1068.0, P2=52.0, P3=dt, P4=dt, P5=0.0, P6=1.0, P7=0.0, hits=list(PRED_BANDS))
            and o['scorer'] == 'shn113.py' and lines[0].startswith('shn113.py shn113 status=ADMITTED')
            and o['pair_stats']['dt_us']['n'] == n_main == 110 and close(dt, m_main)
            and close(o['pair_stats']['dt_us']['se'], se_main)
            and o['secondary']['pair_stats']['dt_us']['n'] == n_sec == 110 and close(sec_dt(o), m_sec)
            and close(o['secondary']['pair_stats']['dt_us']['se'], se_sec) and abs(m_main - m_sec) > 1.0
            and o['secondary']['window'] == [60, 89] and o['secondary']['deciding'] is False
            and o['geometry']['keep'] == [10, 90] and o['geometry']['secondary'] == [60, 89]
            and o['selection']['excluded_edge_blocks'] == [] and o['secondary']['excluded_edge_blocks'] == [3]
            and '  main estimator (decides): rows 10..89 of each block' in lines
            and '  secondary estimator (rows 60..88, never deciding): pairs 110, blocks 220, excluded [3]' in lines
            and size_exact(o, dt, 2 * o['pair_stats']['dt_us']['se']) and dt < -100
            and o['reported']['bda_scan_levels'] == [1068.0, 52.0] and o['reported']['bda_nskip_levels'] == [0.0, 1.0]
            and o['arming']['bda_scan_levels'] == [1068.0, 52.0] and o['arming']['da_q_free_levels'] == [1080.0, 1080.0]
            and o['area_verdict_mirror']['pairs'] == 110
            and 'a gain in the NEW regime' in o['must_not_be_claimed']
            and o['predictions']['P4']['text'].endswith('the discriminating prediction, low confidence'))


def const_check():
    want = {'PRODUCTION_ROOT': 'C:/kyty/s113', 'PRED': 'C:/kyty/s113/pred/02_shn113.md',
            'BINARY_SHA': '94362eae5e28fa68c6a9d5ed921510a1fb1caa2868b0aa220099ba333df4da92',
            'GATES_FILE': 'C:/kyty/s113/gates_base.txt',
            'GATES_SHA': '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf',
            'ARMS': ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=1'),
            'SCHEDULE': '90+1800:dawalk=1 dawalklead=1 bdanarrow=0|dawalk=1 dawalklead=1 bdanarrow=1',
            'TAG_RE': r'shn113b?(?:_entry1)?', 'KEEP_LO': 10, 'KEEP_HI': 90, 'SECONDARY_LO': 60,
            'SECONDARY_HI': 89}
    bad = sorted(k for k in want if ORIG[k] != want[k])
    # PRED_SHA / PRED_BYTES are never compared with a value (audit111 MINOR-5: the executor fills them when pred/02 is
    # sealed, and the sealed copy must stay green here): both None (the draft) or a sha256 and a size (the sealed copy)
    sha, size = ORIG['PRED_SHA'], ORIG['PRED_BYTES']
    sealed = (isinstance(sha, str) and re.fullmatch('[0-9a-f]{64}', sha) is not None and type(size) is int
              and size > 0)
    if not (sealed or (sha is None and size is None)):
        bad.append('PRED_SHA/PRED_BYTES')
    return None, None, 'CONSTANTS OK' if not bad else 'CONSTANTS DIFFER %s' % bad


''')

# ---- verdict branches and the decision terms at the bar -100 -----------------------------------------------------------
t.span("# ---- verdict branches ----", "# ---- the estimator: the main window's edges",
       """# ---- verdict branches -------------------------------------------------------------------------------------------
case('SHIP', run_eval(good, *video(good, tag='ok')), SHIP)
case('PENDING', run_eval(good), PENDING, check=pred_good)
case('DRAFT', run_eval(good, draft=True), 'DRAFT (no verdict)', check=lambda o: o['status'] == 'DRAFT')
# KEEP by the bar = S1_S2_positive / S2_only / S1_only / SE_exact / SEC_edge / EST_rows10_59 / PRED_*; KEEP by a
# failed video = V_*; KEEP not admitted = every admission case

# ---- decision terms ---------------------------------------------------------------------------------------------
# A positive d mean fails both S1 (d mean <= SHIP_US = -100) and S2 (d mean + 2 SE < 0): ship_rules() returns the
# two terms of one dict; both listed.  P3 (up to +200) still hits, P4 misses.
case('S1_S2_positive', run_eval(make('s1', d_dt=60, noise=80)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: (0 < main_dt(o) < 100 and o['predictions']['P3']['hit']
                      and not o['predictions']['P4']['hit']))
# S2 alone: the d mean below the bar, its 2SE across 0
case('S2_only', run_eval(make('s2', d_dt=-150, noise=300, block_noise=1500)), KEEP_BAR,
     rules=['S2_dt_2se_excludes_0'], check=lambda o: main_dt(o) <= -100)
# the bar's edge, noise-free (every pair delta equal, SE 0): d mean dt exactly -100 - S1 holds (<= -100), S2 holds
# (-100 + 2 * 0 < 0): pending (kills S1 strict and a bar moved to -101); P4 hits on its bound ...
case('S1_edge', run_eval(make('s1edge', d_dt=-100, noise=0)), PENDING,
     check=lambda o: (main_dt(o) == -100.0 and o['pair_stats']['dt_us']['sd'] == 0.0
                      and pred_values(o, P3=-100.0, P4=-100.0, hits=list(PRED_BANDS))))
# ... -100.5 (arm-1 frames with an even number -1 us: 40 of the 80 main-window rows of each block): both hold,
# pending ...
case('S1_edge_in', run_eval(make('s1edgein', d_dt=-100, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and n % 2 == 0, edits={'main': {'dt_us': 30900 - 1}}))), PENDING,
    check=lambda o: main_dt(o) == -100.5 and o['pair_stats']['dt_us']['sd'] == 0.0)
# ... and -99.5 (+1 us on those rows): S1 fails ALONE - S2 still holds (-99.5 + 2 * 0 < 0) (kills a bar moved to -99,
# S1 dropped and a verdict on S2 alone); P4 misses
case('S1_only', run_eval(make('s1only', d_dt=-100, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and n % 2 == 0, edits={'main': {'dt_us': 30900 + 1}}))), KEEP_BAR,
    rules=['S1_dt_le_-100'],
    check=lambda o: (main_dt(o) == -99.5 and o['pair_stats']['dt_us']['sd'] == 0.0
                     and pred_values(o, P3=-99.5, P4=-99.5, hits=['P1', 'P2', 'P3', 'P5', 'P6', 'P7'])))

""")

# ---- the estimator cases: verdicts at the bar -100 ---------------------------------------------------------------------
t.keep("case('KEEP_edge', run_eval(make('keepedge', noise=0, row=setter(")
t.keep("case('SEC_edge', run_eval(make('secedge', noise=0, row=setter(")
t.keep("case('EST_rows0_9', run_eval(make('estrows0', noise=0, row=setter(")
t.rep("""                     and pred_values(o, N3=350.0, N4=350.0, hits=['N1', 'N2', 'N4', 'N5', 'N6', 'N7'])))""",
      """                     and pred_values(o, P3=350.0, P4=350.0, hits=['P1', 'P2', 'P5', 'P6', 'P7'])))""")
t.rep("""# the other direction: d 0, arm-1 rows 10..59 -400 us: main -250 exactly (REVERT pending); the secondary reads 0
# exactly: it would pass S1 (0 <= 0) and FAIL S2 (0 + 2 * 0 is not < 0).
case('EST_rows10_59_rev', run_eval(make('estrows10s', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None and 10 <= i < 60,
    edits={'main': {'dt_us': 31000 - 400}}))), PENDING,
    check=lambda o: (main_dt(o) == -250.0 and sec_dt(o) == 0.0 and sec_rules(o) == ['S2_dt_2se_excludes_0']
                     and '  secondary would FAIL S2_dt_2se_excludes_0 (not deciding)' in mod.summary(o).split(NL)
                     and '  secondary would PASS S1_dt_le_0 (not deciding)' in mod.summary(o).split(NL)))""",
      """# the other direction: d 0, arm-1 rows 10..59 -400 us: main -250 exactly (SHIP pending); the secondary reads 0
# exactly and would FAIL both rules (0 > -100; 0 + 2 * 0 is not < 0).
case('EST_rows10_59_ship', run_eval(make('estrows10s', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None and 10 <= i < 60,
    edits={'main': {'dt_us': 31000 - 400}}))), PENDING,
    check=lambda o: (main_dt(o) == -250.0 and sec_dt(o) == 0.0 and sec_rules(o) == BOTH_RULES
                     and '  secondary would FAIL S1_dt_le_-100 (not deciding)' in mod.summary(o).split(NL)
                     and '  secondary would FAIL S2_dt_2se_excludes_0 (not deciding)' in mod.summary(o).split(NL)))""")
t.keep("assert SE_MEAN + 2 * SE_SAMPLE > 0 > SE_MEAN + 2 * SE_POP, 'SE_exact no longer straddles the S2 edge'")

# ---- LEVEL_median on the levels the arming and P1 / P2 / P6 read -------------------------------------------------------
t.span("# noise-free; block 12 (arm 0) and block 9 (arm 1) +2 900 us on every row, block 16",
       "# ---- the reported, never deciding d cpu_net_us",
       """# noise-free; block 12 (arm 0) and block 9 (arm 1) +2 900 us on every row, block 16 (arm 0) and block 17 (arm 1)
# bda_scan 50 000, block 21 (arm 1) bda_nskip 20 000: medians 31 000 / 30 850 / 1 068 / 52 / 1 exactly (means:
# 31 026.4 / 30 876.4 / 1 512.8 / 506.1 / 182.8 - P1, P2 and P6 would miss and NARROW_SCAN_ARM1 would fail); the two
# dt outliers sit in different pairs with opposite signs, so d mean dt stays -150.
case('LEVEL_median', run_eval(make('levmed', noise=0, row=both(
    setter(pick=lambda n, b, a, i: i is not None and b in (9, 12),
           edits={'main': {'dt_us': lambda n, b, a, i: 31000 - 150 * a + 2900}}),
    setter(pick=lambda n, b, a, i: i is not None and b in (16, 17), edits={'draw': {'bda_scan': 50000}}),
    setter(pick=lambda n, b, a, i: i is not None and b == 21, edits={'x': {'bda_nskip': 20000}})))), PENDING,
    check=lambda o: (o['levels']['arm0']['dt_us'] == 31000.0 and o['levels']['arm1']['dt_us'] == 30850.0
                     and o['levels']['arm0']['bda_scan'] == 1068.0 and o['levels']['arm1']['bda_scan'] == 52.0
                     and o['levels']['arm1']['bda_nskip'] == 1.0 and main_dt(o) == -150.0
                     and pred_values(o, P1=1068.0, P2=52.0, P6=1.0, hits=list(PRED_BANDS))))

""")
t.keep("case('CPU_NET_spin', run_eval(make('cpunet', spin1=80, cpu_noise=0)), PENDING,")

# ---- predictions P1-P7 ---------------------------------------------------------------------------------------------
t.span("# ---- predictions N1-N7 (report only", "# ---- video checks, each alone",
       """# ---- predictions P1-P7 (report only: the verdict never reads them) ------------------------------------------------
# Every band exactly at and just outside each edge, noise-free.  The good run (a SHIP pending) is inside all seven;
# PRED_inside is the predicted run (d -300), inside all seven too.
case('PRED_inside', run_eval(make('predin', d_dt=-300, noise=0)), PENDING,
     check=lambda o: (pred_values(o, P1=1068.0, P2=52.0, P3=-300.0, P4=-300.0, P5=0.0, P6=1.0, P7=0.0,
                                  hits=list(PRED_BANDS)) and size_exact(o, -300.0, 0.0)))
# on the lower edges: P1 800, P2 30, P3 -1 500 (P4 holds), P5 -150, P7 -40 - all hit (P6's lower edge lies below the
# arming level 1: PRED_P6_lo below)
case('PRED_edges_lo', run_eval(make('prededgelo', d_dt=-1500, noise=0, scan0=800, scan1=30, gpu1=12550,
                                    row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_miss': 260}}))),
     PENDING, check=lambda o: pred_values(o, P1=800.0, P2=30.0, P3=-1500.0, P4=-1500.0, P5=-150.0, P6=1.0,
                                          P7=-40.0, hits=list(PRED_BANDS)))
# just below them: 799, 29, -1 501, -151, -41 - all miss but P4 and P6
case('PRED_misses_lo', run_eval(make('predmisslo', d_dt=-1501, noise=0, scan0=799, scan1=29, gpu1=12549,
                                     row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_miss': 259}}))),
     PENDING, check=lambda o: pred_values(o, P1=799.0, P2=29.0, P3=-1501.0, P4=-1501.0, P5=-151.0, P6=1.0,
                                          P7=-41.0, hits=['P4', 'P6']))
# on the upper edges: P1 1 400, P2 200 (= NARROW_SCAN_MAX: admitted), P3 +200, P5 +150, P6 3, P7 +40 - all hit but
# P4 (d +200 fails S1 and S2)
case('PRED_edges_hi', run_eval(make('prededgehi', d_dt=200, noise=0, scan0=1400, scan1=200, gpu1=12850, nskip1=3,
                                    row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_miss': 340}}))),
     KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, P1=1400.0, P2=200.0, P3=200.0, P4=200.0, P5=150.0, P6=3.0, P7=40.0,
                                 hits=['P1', 'P2', 'P3', 'P5', 'P6', 'P7']))
# just above them: 1 401, 201 (above NARROW_SCAN_MAX: not admitted, NARROW_SCAN_ARM1 alone - the predictions are still
# computed), +201, +151, 3.0125 (row 50 of each arm-1 block 4, the others 3), +41 - all miss
case('PRED_misses_hi', run_eval(make('predmisshi', d_dt=201, noise=0, scan0=1401, scan1=201, gpu1=12851, nskip1=3,
                                     row=setter(pick=lambda n, b, a, i: a == 1,
                                                edits={'draw': {'da_miss': 341},
                                                       'x': {'bda_nskip': lambda n, b, a, i: 4 if i == 50 else 3}}))),
     KEEP_NA, fails=ARMING, arming=['NARROW_SCAN_ARM1'], rules=BOTH_RULES,
     check=lambda o: pred_values(o, P1=1401.0, P2=201.0, P3=201.0, P4=201.0, P5=151.0, P6=241 / 80, P7=41.0,
                                 hits=[]))
# d exactly 0 with SE 0: S2 fails on its own edge (0 + 2 * 0 is not < 0; kills S2 read as <= 0), S1 fails too; P3
# hits (inside [-1 500, +200]), P4 misses
case('S2_edge_zero', run_eval(make('s2edgezero', d_dt=0, noise=0)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, P3=0.0, P4=0.0, hits=['P1', 'P2', 'P3', 'P5', 'P6', 'P7']))
# P4's only bound: d mean -100 hits (S1_edge), -99 misses
case('PRED_P4_out', run_eval(make('predp4out', d_dt=-99, noise=0)), KEEP_BAR, rules=['S1_dt_le_-100'],
     check=lambda o: pred_values(o, P3=-99.0, P4=-99.0, hits=['P1', 'P2', 'P3', 'P5', 'P6', 'P7']))
# P6's lower edge lies below the arming level (NARROW_ARMED_ARM1: level >= 1), so both of its fixtures are not
# admitted, NARROW_ARMED_ARM1 alone: level 0.5 (the odd main-window rows of each arm-1 block 1, the others 0) hits ...
case('PRED_P6_lo', run_eval(make('predp6lo', noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1, edits={'x': {'bda_nskip': lambda n, b, a, i: 1 if i % 2 == 1 else 0}}))),
    KEEP_NA, fails=ARMING, arming=['NARROW_ARMED_ARM1'],
    check=lambda o: pred_values(o, P6=0.5, hits=list(PRED_BANDS)))
# ... 0.4875 (39 of the 80 main-window rows 1) misses
case('PRED_P6_lo_out', run_eval(make('predp6loout', noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1,
    edits={'x': {'bda_nskip': lambda n, b, a, i: 1 if i % 2 == 1 and i != 11 else 0}}))),
    KEEP_NA, fails=ARMING, arming=['NARROW_ARMED_ARM1'],
    check=lambda o: pred_values(o, P6=39 / 80, hits=['P1', 'P2', 'P3', 'P4', 'P5', 'P7']))

""")

# ---- video checks: the gate text names the candidate's knob; the frame floor's edge ----------------------------------
t.rep("case('V_frames_3000', run_eval(good, *video(good, frames=3000, tag='f3')), REVERT)",
      "case('V_frames_3000', run_eval(good, *video(good, frames=3000, tag='f3')), SHIP)")
t.span("# the gate text: today's default (the arm-0 text) instead of the candidate", "case('V_pin',",
       """# the gate text: today's value (the arm-0 text) instead of the candidate, knob 2, no bdanarrow at all, dawalk=0
case('V_gate', run_eval(good, *video(good, gate='bdanarrow=0', tag='gt')), KEEP_VID,
     vfail=['bdanarrow_1_in_gate_text'])
case('V_gate_mode2', run_eval(good, *video(good, gate='bdanarrow=2', tag='g2')), KEEP_VID,
     vfail=['bdanarrow_1_in_gate_text'])
case('V_gate_none', run_eval(good, *video(good, gate='daslot=1', tag='gn')), KEEP_VID,
     vfail=['bdanarrow_1_in_gate_text'])
case('V_gate_dawalk', run_eval(good, *video(good, gates=gates_text.replace('dawalk=1', 'dawalk=0'), tag='gd')),
     KEEP_VID, vfail=['bdanarrow_1_in_gate_text'])
""")
t.rep("case('V_missing', run_eval(good, str(good / 'no_such_vnet112.json'),",
      "case('V_missing', run_eval(good, str(good / 'no_such_vsn113.json'),")

# ---- integrity: the schema's eighteen x counters and the draw row's bda_scan, the recording path ---------------------
t.rep("# ... and the b47b58a9 build's ten daslot / daguard counters (session 111's eight, session 112's two), each alone",
      "# ... and the 94362eae build's eighteen x counters (session 111's eight daslot, session 112's two daguard, session\n"
      "# 113's eight bdanarrow), each alone")
t.rep("""case('FIELD_ORIGIN_slot', run_eval(make('originslot', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                 edits={'main': {'da_q_free': 0}}))),
     KEEP_NA, fails={'integrity:FIELD_ORIGIN'},
     check=lambda o: o['field_origin_defects'] == {'da_q_free': ['main', 'x']})
""", """case('FIELD_ORIGIN_slot', run_eval(make('originslot', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                 edits={'main': {'da_q_free': 0}}))),
     KEEP_NA, fails={'integrity:FIELD_ORIGIN'},
     check=lambda o: o['field_origin_defects'] == {'da_q_free': ['main', 'x']})
# the draw row's bda_scan: alone missing on one row, then printed on the x row too
case('SCHEMA_bda_scan', run_eval(make('schema_bda_scan', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                    edits={'draw': {'bda_scan': None}}))),
     KEEP_NA, fails={'integrity:SCHEMA'}, check=lambda o: o['schema_missing_fields'] == ['bda_scan'])
case('FIELD_ORIGIN_scan', run_eval(make('originscan', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                 edits={'x': {'bda_scan': 0}}))),
     KEEP_NA, fails={'integrity:FIELD_ORIGIN'},
     check=lambda o: o['field_origin_defects'] == {'bda_scan': ['draw', 'x']})
""")
t.rep("append=['Recording: C:/kyty/s112/rec_net112.mp4 960x540']", "append=['Recording: C:/kyty/s113/rec_shn113.mp4 960x540']")

# ---- arming: the session-113 terms, each alone, with both threshold edges, the lag case and the missing level ------
t.span("# SLOT_ARMED_ARM0: today's default arm queues under m_mutex (da_qcall still 1 080: the knob, not the call count; N6\n",
       "# DEFAULTS_ON: cspfree off in arm 0 (no lookup, no hit) ...\n",
       """# REGIME_OLD_ARM0: the run in the NEW regime (arm-0 bda_scan level 52, as arm 1's; P1 misses) ...
case('REGIME_OLD0', run_eval(make('regime0', scan0=52)), KEEP_NA, fails=ARMING, arming=['REGIME_OLD_ARM0'],
     check=lambda o: o['arming']['bda_scan_levels'] == [52.0, 52.0] and not o['predictions']['P1']['hit'])
# ... at the threshold: level 500 passes ...
case('REGIME_OLD0_edge', run_eval(make('regime0edge', scan0=500)), PENDING,
     check=lambda o: o['arming']['bda_scan_levels'] == [500.0, 52.0])
# ... 499 fails ...
case('REGIME_OLD0_out', run_eval(make('regime0out', scan0=499)), KEEP_NA, fails=ARMING, arming=['REGIME_OLD_ARM0'],
     check=lambda o: o['arming']['bda_scan_levels'] == [499.0, 52.0])
# ... OLD only outside the main window (rows 0..9 of the arm-0 blocks 1 068, rows 10..89 499 - a full-block level
# would read 562.2): the level reads the main window only ...
case('REGIME_OLD0_lag', run_eval(make('regime0lag', row=setter(
    pick=lambda n, b, a, i: a == 0 and i is not None,
    edits={'draw': {'bda_scan': lambda n, b, a, i: 499 if i in MAIN else 1068}}))),
    KEEP_NA, fails=ARMING, arming=['REGIME_OLD_ARM0'], check=lambda o: o['levels']['arm0']['bda_scan'] == 499.0)
# ... and a missing level (bda_scan dropped on one main-window row of every arm-0 block: no arm-0 block mean carries
# it) fails too, with SCHEMA
case('REGIME_OLD0_none', run_eval(make('regime0none', row=setter(
    pick=lambda n, b, a, i: a == 0 and i == 50, edits={'draw': {'bda_scan': None}}))),
    KEEP_NA, fails={'integrity:SCHEMA', 'control:ARMING'}, arming=['REGIME_OLD_ARM0'],
    check=lambda o: o['arming']['bda_scan_levels'] == [None, 52.0])
# NARROW_ARMED_ARM1: the candidate arm skips no registration invalidation (bda_nskip 0; P6 misses) ...
case('NARROW_ARMED1', run_eval(make('narmed1', nskip1=0)), KEEP_NA, fails=ARMING, arming=['NARROW_ARMED_ARM1'],
     check=lambda o: o['levels']['arm1']['bda_nskip'] == 0.0 and not o['predictions']['P6']['hit'])
# ... at the level edge: 1 (the good run's) passes; 79 of the 80 main-window rows of each arm-1 block 1, row 50 0 -
# level 0.9875 - fails ...
case('NARROW_ARMED1_out', run_eval(make('narmed1out', row=setter(
    pick=lambda n, b, a, i: a == 1 and i == 50, edits={'x': {'bda_nskip': 0}}))),
    KEEP_NA, fails=ARMING, arming=['NARROW_ARMED_ARM1'], check=lambda o: o['levels']['arm1']['bda_nskip'] == 79 / 80)
# ... only outside the main window (rows 0..9 of the arm-1 blocks 9, rows 10..89 0 - a full-block level would read
# 1.0): the level reads the main window only
case('NARROW_ARMED1_lag', run_eval(make('narmed1lag', row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None,
    edits={'x': {'bda_nskip': lambda n, b, a, i: 0 if i in MAIN else 9}}))),
    KEEP_NA, fails=ARMING, arming=['NARROW_ARMED_ARM1'], check=lambda o: o['levels']['arm1']['bda_nskip'] == 0.0)
# NARROW_DARK_ARM0: today's arm skipping registration invalidations on every main-window row (5 a flip) ...
case('NARROW_DARK0', run_eval(make('ndark0', nskip0=5)), KEEP_NA, fails=ARMING, arming=['NARROW_DARK_ARM0'],
     check=lambda o: o['arming']['narrow_arm0_kept']['bda_nskip'] == 5 * 80 * 110)
# ... on ONE main-window row of block 4 (arm 0), value 1: a kept total of 1 fails - no tolerance (the good run's 0
# passes) ...
case('NARROW_DARK0_one', run_eval(make('ndark0one', row=setter(pick=lambda n, b, a, i: b == 4 and i == 50,
                                                               edits={'x': {'bda_nskip': 1}}))),
     KEEP_NA, fails=ARMING, arming=['NARROW_DARK_ARM0'],
     check=lambda o: o['arming']['narrow_arm0_kept']['bda_nskip'] == 1)
# ... but not rows 0..9 of an arm-0 block (the counters of the flips that straddle the arm change): pending
case('NARROW_DARK0_lag', run_eval(make('ndark0lag', row=setter(
    pick=lambda n, b, a, i: a == 0 and out_main(i), edits={'x': {'bda_nskip': 400}}))), PENDING,
    check=lambda o: (o['arming']['narrow_arm0_kept']['bda_nskip'] == 0
                     and o['levels']['arm0']['bda_nskip'] == 0.0))
# NARROW_SCAN_ARM1: the candidate arm still walks every region (bda_scan 1 068, as arm 0's; P2 misses) ...
case('NARROW_SCAN1', run_eval(make('nscan1', scan1=1068)), KEEP_NA, fails=ARMING, arming=['NARROW_SCAN_ARM1'],
     check=lambda o: o['arming']['bda_scan_levels'] == [1068.0, 1068.0] and not o['predictions']['P2']['hit'])
# ... at the ceiling: level 200 passes ...
case('NARROW_SCAN1_edge', run_eval(make('nscan1edge', scan1=200)), PENDING,
     check=lambda o: o['arming']['bda_scan_levels'] == [1068.0, 200.0])
# ... 201 fails ...
case('NARROW_SCAN1_out', run_eval(make('nscan1out', scan1=201)), KEEP_NA, fails=ARMING, arming=['NARROW_SCAN_ARM1'],
     check=lambda o: o['arming']['bda_scan_levels'] == [1068.0, 201.0])
# ... the flips that straddle the arm change (rows 0..9 of the arm-1 blocks 1 068, rows 10..89 200 - a full-block
# level would read 296.4): pending ...
case('NARROW_SCAN1_lag', run_eval(make('nscan1lag', row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None,
    edits={'draw': {'bda_scan': lambda n, b, a, i: 200 if i in MAIN else 1068}}))), PENDING,
    check=lambda o: o['levels']['arm1']['bda_scan'] == 200.0)
# ... and a missing level (bda_scan dropped on one main-window row of every arm-1 block) fails too, with SCHEMA
case('NARROW_SCAN1_none', run_eval(make('nscan1none', row=setter(
    pick=lambda n, b, a, i: a == 1 and i == 50, edits={'draw': {'bda_scan': None}}))),
    KEEP_NA, fails={'integrity:SCHEMA', 'control:ARMING'}, arming=['NARROW_SCAN_ARM1'],
    check=lambda o: o['arming']['bda_scan_levels'] == [1068.0, None])
# NO_CHECK: knob 2's check on one pre-schedule row (outside every kept block: the check reads ALL rows), value 1 - no
# tolerance - bda_nwould ...
case('NO_CHECK_would', run_eval(make('nchkwould', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                             edits={'x': {'bda_nwould': 1}}))),
     KEEP_NA, fails=ARMING, arming=['NO_CHECK'], check=lambda o: o['arming']['bda_nwould_all_rows'] == 1)
# ... bda_nmiss ...
case('NO_CHECK_miss', run_eval(make('nchkmiss', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                           edits={'x': {'bda_nmiss': 1}}))),
     KEEP_NA, fails=ARMING, arming=['NO_CHECK'], check=lambda o: o['arming']['bda_nmiss_all_rows'] == 1)
# ... and on a kept arm-1 row
case('NO_CHECK_kept', run_eval(make('nchkkept', row=setter(pick=lambda n, b, a, i: b == 5 and i == 70,
                                                           edits={'x': {'bda_nwould': 2, 'bda_nmiss': 1}}))),
     KEEP_NA, fails=ARMING, arming=['NO_CHECK'],
     check=lambda o: o['arming']['bda_nwould_all_rows'] == 2 and o['arming']['bda_nmiss_all_rows'] == 1)
# NO_XTHR: one registration marked off the scanning thread on a pre-schedule row, value 1 ...
case('NO_XTHR', run_eval(make('nxthr', row=setter(pick=lambda n, b, a, i: n == 1750, edits={'x': {'bda_nxthr': 1}}))),
     KEEP_NA, fails=ARMING, arming=['NO_XTHR'], check=lambda o: o['arming']['bda_nxthr_all_rows'] == 1)
# ... and on a kept arm-0 row
case('NO_XTHR_kept', run_eval(make('nxthrk', row=setter(pick=lambda n, b, a, i: b == 4 and i == 70,
                                                        edits={'x': {'bda_nxthr': 2}}))),
     KEEP_NA, fails=ARMING, arming=['NO_XTHR'], check=lambda o: o['arming']['bda_nxthr_all_rows'] == 2)
# the level edges: arm-1 bda_nskip 1 (the good run's), da_q_free 1 and cspfree_hit 1 in both arms - every arming check
# holds (P6 hits)
case('ARMED_edge', run_eval(make('armededge', qfree0=1, qfree1=1, hit0=1, hit1=1)), PENDING,
     check=lambda o: (o['levels']['arm1']['bda_nskip'] == 1.0 and o['arming']['da_q_free_levels'] == [1.0, 1.0]
                      and o['arming']['cspfree_hit_levels'] == [1.0, 1.0]
                      and pred_values(o, P6=1.0, hits=list(PRED_BANDS))))
""")
t.keep("case('DEFAULTS_arm0', run_eval(make('defarm0', look0=0, hit0=0)), KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'],")
t.rep("""case('DEFAULTS_bad_kept', run_eval(make('defbadk', row=setter(pick=lambda n, b, a, i: b == 4 and i == 70,
                                                              edits={'x': {'cspfree_bad': 3}}))),
     KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'], check=lambda o: o['arming']['cspfree_bad_all_rows'] == 3)
""", """case('DEFAULTS_bad_kept', run_eval(make('defbadk', row=setter(pick=lambda n, b, a, i: b == 4 and i == 70,
                                                              edits={'x': {'cspfree_bad': 3}}))),
     KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'], check=lambda o: o['arming']['cspfree_bad_all_rows'] == 3)
# ... daslot=1 off in one arm (no QueueDrawAhead call off m_mutex, da_qcall still 1 080), arm 0 ...
case('DEFAULTS_qfree0', run_eval(make('defqfree0', qfree0=0)), KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'],
     check=lambda o: o['arming']['da_q_free_levels'] == [0.0, 1080.0] and o['levels']['arm0']['da_qcall'] == 1080.0)
# ... arm 1 ...
case('DEFAULTS_qfree1', run_eval(make('defqfree1', qfree1=0)), KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'],
     check=lambda o: o['arming']['da_q_free_levels'] == [1080.0, 0.0] and o['levels']['arm1']['da_qcall'] == 1080.0)
for a in (0, 1):
    # ... the level edges in each arm (1 passes: ARMED_edge): cspfree_hit, then da_q_free, 1 on 79 of the 80
    # main-window rows (row 50 0) - level 0.9875 fails ...
    case('DEFAULTS_hit_out%d' % a, run_eval(make('defhitout%d' % a, hit0=1, hit1=1, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a and i == 50, edits={'x': {'cspfree_hit': 0}}))),
        KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'],
        check=lambda o, a=a: o['arming']['cspfree_hit_levels'][a] == 79 / 80)
    case('DEFAULTS_qfree_out%d' % a, run_eval(make('defqfreeout%d' % a, qfree0=1, qfree1=1, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a and i == 50, edits={'x': {'da_q_free': 0}}))),
        KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'],
        check=lambda o, a=a: o['arming']['da_q_free_levels'][a] == 79 / 80)
    # ... and da_q_free only outside the main window (rows 0..9 1 080, rows 10..89 0): the level reads the main window
    case('DEFAULTS_qfree_lag%d' % a, run_eval(make('defqfreelag%d' % a, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a and i is not None,
        edits={'x': {'da_q_free': lambda n, b, arm, i: 0 if i in MAIN else 1080}}))),
        KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'], check=lambda o, a=a: o['arming']['da_q_free_levels'][a] == 0.0)
# ... one knob-2 slot-key disagreement on a pre-schedule row (outside every kept block: ALL rows are read) ...
case('DEFAULTS_slot_bad', run_eval(make('defslotbad', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                 edits={'x': {'da_slot_bad': 1}}))),
     KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'], check=lambda o: o['arming']['da_slot_bad_all_rows'] == 1)
# ... and on a kept arm-1 row
case('DEFAULTS_slot_bad_kept', run_eval(make('defslotbadk', row=setter(pick=lambda n, b, a, i: b == 5 and i == 70,
                                                                       edits={'x': {'da_slot_bad': 2}}))),
     KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'], check=lambda o: o['arming']['da_slot_bad_all_rows'] == 2)
""")

# ---- protocol: kept verbatim ---------------------------------------------------------------------------------------
t.keep("case('P_att_hold_edge', run_eval(variant(good, 'p_ahold595', meta_set(attempts=[dict(ATT, hold_s=595)]))), PENDING)")

# ---- main(): identity, refusals, tags ------------------------------------------------------------------------------
t.rep("fake_exe.write_bytes(b'not the b47b58a9 build')", "fake_exe.write_bytes(b'not the 94362eae build')")
t.rep("'PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and size into net112.py (only --draft runs '",
      "'PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and size into shn113.py (only --draft runs '")
t.rep("""# the tag pattern: net112 with the optional b and _entry1 reaches evaluate() (no files under that tag here: INPUTS,
# protocol and IDENTITY fail, rc 1 - not the refusal's rc 2) ...
for t in ('net112b', 'net112_entry1', 'net112b_entry1'):""",
      """# the tag pattern: shn113 with the optional b and _entry1 reaches evaluate() (no files under that tag here: INPUTS,
# protocol and IDENTITY fail, rc 1 - not the refusal's rc 2) ...
for t in ('shn113b', 'shn113_entry1', 'shn113b_entry1'):""")
t.rep("""# ... and every other tag is refused with the full message, session 111's tags and the video tags included
for t in ('net113', 'net111', 'shp111', 'shp111b', 'shp111_entry1', 'vnet112', 'vss111', 'net112c', 'xnet112'):""",
      """# ... and every other tag is refused with the full message, session 112's tags and the video tags included
for t in ('shn114', 'shn112', 'net112', 'net112b', 'net112_entry1', 'vsn113', 'vbn113', 'vnet112', 'shn113c',
          'xshn113'):""")

# ---- the report lines ----------------------------------------------------------------------------------------------
t.rep("""    if c['name'] in ('PENDING', 'S2_only', 'S1_edge', 'S1_edge_in', 'S1_edge_out', 'SE_exact', 'KEEP_edge',
                     'SEC_edge', 'EST_rows0_9', 'EST_rows10_59', 'EST_rows10_59_rev', 'LEVEL_median'):""",
      """    if c['name'] in ('PENDING', 'S2_only', 'S1_edge', 'S1_edge_in', 'S1_only', 'SE_exact', 'KEEP_edge',
                     'SEC_edge', 'EST_rows0_9', 'EST_rows10_59', 'EST_rows10_59_ship', 'LEVEL_median'):""")
t.rep("""        print('   LEVEL case: dt arm0 %s arm1 %s, da_q_free arm0 %s, da_q_noguard arm1 %s, da_queue_us arm1 %s'
              % ((lv.get('arm0') or {}).get('dt_us'), (lv.get('arm1') or {}).get('dt_us'),
                 (lv.get('arm0') or {}).get('da_q_free'), (lv.get('arm1') or {}).get('da_q_noguard'),
                 (lv.get('arm1') or {}).get('da_queue_us')))""",
      """        print('   LEVEL case: dt arm0 %s arm1 %s, bda_scan arm0 %s arm1 %s, bda_nskip arm1 %s'
              % ((lv.get('arm0') or {}).get('dt_us'), (lv.get('arm1') or {}).get('dt_us'),
                 (lv.get('arm0') or {}).get('bda_scan'), (lv.get('arm1') or {}).get('bda_scan'),
                 (lv.get('arm1') or {}).get('bda_nskip')))""")

t.write('test_shn113.py',
        stale=("'N1'", "'N7'", 'vnet112_', 'daguard_0_in_gate_text', 'SLOT_ARMED_ARM0', 'SLOT_DARK_ARM1', 'NOGUARD_',
               'S1_dt_le_0', "TAG = 'net112'", 'b47b58a9', 's106_stage/net112', 'REVERT', 'slot_arm1_kept',
               'EST_rows10_59_rev', 'gain_exact', 'GAIN_LABEL', 's111_gain', "'da_qcall': qcall", 'qcall=', 'ng1=',
               'qq1=',
               "'S1_edge_out'", 'a gain against a different build'),
        fresh=("TAG = 'shn113'", 'REGIME_OLD0_edge', 'REGIME_OLD0_lag', 'REGIME_OLD0_none', 'NARROW_ARMED1_out',
               'NARROW_DARK0_one', 'NARROW_SCAN1_out', 'NARROW_SCAN1_lag', 'NO_CHECK_would', 'NO_XTHR_kept',
               'DEFAULTS_qfree_lag', 'DEFAULTS_slot_bad_kept', 'S1_only', 'PRED_P6_lo_out', 'SCHEMA_bda_scan',
               'P_att_hold_edge', 'AREA_min_flips_below', 'WALK_IDENT_edge_out', 'V_frames_2999', 'def size_exact(',
               "'bda_nskip': nskip1 if arm else nskip0",
               "'SCHEDULE': '90+1800:dawalk=1 dawalklead=1 bdanarrow=0|"))

# =====================================================================================================================
# mut_shn113.py from mut_net112.py
# =====================================================================================================================
m = Src('mut_net112.py')
m.docstring('Session 112: mutation check of net112.py against test_net112.py, derived',
            '    python mut_net112.py [<workers>]\n',
            '''Session 113: mutation check of shn113.py against test_shn113.py, derived from session 112's mut_net112.py by
make_shn113.py.  Each mutant disables or weakens ONE admission / decision term, verdict branch, prediction, schema
entry, marker, sealed constant, estimator window, threshold or refusal of main() (anchored replace, asserted to match
exactly once).  Included: every mutant of mut_net112.py that still applies (ported: the bar 0 -> -100 with its edges,
the video gate text, the sealed constants, tags and texts re-anchored on shn113, DEFAULTS_ON re-anchored on its
session-113 expression), and the session-113 changes: REGIME_OLD_ARM0, NARROW_ARMED_ARM1, NARROW_DARK_ARM0,
NARROW_SCAN_ARM1, NO_CHECK, NO_XTHR and DEFAULTS_ON's daslot parts (off, arm swapped, threshold and constant edges,
lag / all-rows reads, missing levels, one clause dropped), the eight new FrameTrace-x counters and bda_scan in the
schema, P1-P7, the quoted size and the claim.  Dropped with the code they mutated (no anchor left): the SLOT_* /
NOGUARD_* / SLOT_NO_BAD mutants of session 112 (the slot-bad sum now lives in DEFAULTS_ON and has its own mutants),
N1-N7 with PRED_ratio_inverted (ratio() is gone), and the GAIN_* mutants (replaced by SIZE_*).  Each mutant runs the
full fixture suite in its own fixture directory (C:/kyty/s106_stage/shn113/fx_mut/w<k>, removed at the end); a mutant
is KILLED when the suite does not print ALL OK.  The unmutated scorer runs first in the same harness and must print ALL
OK.
    python mut_shn113.py [<workers>]
''')
m.rep("""HERE = Path('C:/kyty/s106_stage')
SCORER = HERE / 'net112.py'
TEST = HERE / 'test_net112.py'
MUT = HERE / 'net112' / 'mutants'
FX = HERE / 'net112' / 'fx_mut'""", """HERE = Path('C:/kyty/s106_stage')
SCORER = HERE / 'shn113.py'
TEST = HERE / 'test_shn113.py'
MUT = HERE / 'shn113' / 'mutants'
FX = HERE / 'shn113' / 'fx_mut'""")
m.rep("# ==== ported from mut_shp111.py (itself from mut_shp110.py) ====",
      "# ==== ported from mut_net112.py (itself from mut_shp111.py / mut_shp110.py) ====")
m.rep("""mutant('S1_off', "'S1_dt_le_0': dt['mean'] is not None and dt['mean'] <= SHIP_US,", "'S1_dt_le_0': True,")""",
      """mutant('S1_off', "'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,", "'S1_dt_le_-100': True,")""")
m.keep("""mutant('S1_bar_+50', "dt['mean'] <= SHIP_US,", "dt['mean'] <= SHIP_US + 50,")""")
m.span('GATE = "\' dawalk=1 \' in gates and \' daslot=0 \' in gates and \' daguard=0 \' in gates,"', "mutant('VIDEO_pin_off',",
       """GATE = "' dawalk=1 ' in gates and ' bdanarrow=1 ' in gates,"
mutant('VIDEO_gate_narrow_off', GATE, "' dawalk=1 ' in gates,")
mutant('VIDEO_gate_dawalk_off', GATE, "' bdanarrow=1 ' in gates,")
mutant('VIDEO_gate_is_arm0', GATE, "' dawalk=1 ' in gates and ' bdanarrow=0 ' in gates,")
mutant('VIDEO_gate_any_mode', GATE, "' dawalk=1 ' in gates and ' bdanarrow=' in gates,")
mutant('VIDEO_gate_is_net112', GATE, "' dawalk=1 ' in gates and ' daslot=0 ' in gates and ' daguard=0 ' in gates,")
""")
m.rep("""mutant('SHIP_bar_-1', 'SHIP_US = 0.0', 'SHIP_US = -1.0')
mutant('SHIP_bar_+1', 'SHIP_US = 0.0', 'SHIP_US = 1.0')""",
      """mutant('SHIP_bar_-99', 'SHIP_US = -100.0', 'SHIP_US = -99.0')
mutant('SHIP_bar_-101', 'SHIP_US = -100.0', 'SHIP_US = -101.0')""")
m.keep("mutant('MAIN_lo_9', NL + 'KEEP_LO, KEEP_HI = 10, 90', NL + 'KEEP_LO, KEEP_HI = 9, 90')")
m.keep("mutant('SEC_swap_into_predictions', \"out['predictions'] = predictions(stats, lev, arm)\",")

# arming: the SLOT_* / NOGUARD_* / SLOT_NO_BAD mutants -> the session-113 terms; DEFAULTS_ON re-anchored + its daslot parts
m.span("# ---- arming: SLOT_ARMED_ARM0 / SLOT_DARK_ARM1 (session 112", "# ---- the b47b58a9 schema:",
       """# ---- arming: REGIME_OLD_ARM0 (session 113; the arm-0 level of bda_scan) ---------------------------------------------
RG = "checks['REGIME_OLD_ARM0'] = scan[0] is not None and scan[0] >= REGIME_OLD_SCAN"
mutant('REGIME_off', RG, "checks['REGIME_OLD_ARM0'] = True")
mutant('REGIME_arm1', RG, "checks['REGIME_OLD_ARM0'] = scan[1] is not None and scan[1] >= REGIME_OLD_SCAN")
mutant('REGIME_gt', RG, "checks['REGIME_OLD_ARM0'] = scan[0] is not None and scan[0] > REGIME_OLD_SCAN")
mutant('REGIME_none_passes', RG, "checks['REGIME_OLD_ARM0'] = scan[0] is None or scan[0] >= REGIME_OLD_SCAN")
mutant('REGIME_all_arm0_rows', RG, "checks['REGIME_OLD_ARM0'] = statistics.fmean(r['bda_scan'] for r in rows.values() "
       "if r.get('arm') == 0 and 'bda_scan' in r) >= REGIME_OLD_SCAN")
mutant('REGIME_499', NL + 'REGIME_OLD_SCAN = 500', NL + 'REGIME_OLD_SCAN = 499')
mutant('REGIME_501', NL + 'REGIME_OLD_SCAN = 500', NL + 'REGIME_OLD_SCAN = 501')
mutant('SCAN_arms_swapped', "    scan = [lev[a].get('bda_scan') for a in (0, 1)]",
       "    scan = [lev[a].get('bda_scan') for a in (1, 0)]")
# ---- arming: NARROW_ARMED_ARM1 / NARROW_DARK_ARM0 (bda_nskip) ----------------------------------------------------------
NA = "checks['NARROW_ARMED_ARM1'] = bool((lev[1].get('bda_nskip') or 0) >= 1)"
mutant('NARROW_ARMED_off', NA, "checks['NARROW_ARMED_ARM1'] = True")
mutant('NARROW_ARMED_arm0', NA, "checks['NARROW_ARMED_ARM1'] = bool((lev[0].get('bda_nskip') or 0) >= 1)")
mutant('NARROW_ARMED_gt1', NA, "checks['NARROW_ARMED_ARM1'] = bool((lev[1].get('bda_nskip') or 0) > 1)")
mutant('NARROW_ARMED_gt0', NA, "checks['NARROW_ARMED_ARM1'] = bool((lev[1].get('bda_nskip') or 0) > 0)")
mutant('NARROW_ARMED_ge_half', NA, "checks['NARROW_ARMED_ARM1'] = bool((lev[1].get('bda_nskip') or 0) >= 0.5)")
mutant('NARROW_ARMED_reads_rinv', NA, "checks['NARROW_ARMED_ARM1'] = bool((lev[1].get('bda_rinv') or 0) >= 1)")
mutant('NARROW_ARMED_all_arm1_rows', NA, "checks['NARROW_ARMED_ARM1'] = sum(r.get('bda_nskip', 0) for r in "
       "rows.values() if r.get('arm') == 1) >= 1")
ND = "checks['NARROW_DARK_ARM0'] = nskip0 == 0"
mutant('NARROW_DARK_off', ND, "checks['NARROW_DARK_ARM0'] = True")
mutant('NARROW_DARK_tol1', ND, "checks['NARROW_DARK_ARM0'] = nskip0 is not None and nskip0 <= 1")
mutant('NARROW_DARK_tol5', ND, "checks['NARROW_DARK_ARM0'] = nskip0 is not None and nskip0 <= 5")
mutant('NARROW_DARK_all_arm0_rows', "nskip0 = kept_total(rows, sel, arms, 0, 'bda_nskip')",
       "nskip0 = sum(r.get('bda_nskip', 0) for r in rows.values() if r.get('arm') == 0)")
mutant('NARROW_DARK_reads_arm1', "nskip0 = kept_total(rows, sel, arms, 0, 'bda_nskip')",
       "nskip0 = kept_total(rows, sel, arms, 1, 'bda_nskip')")
# ---- arming: NARROW_SCAN_ARM1 (the arm-1 level of bda_scan) ------------------------------------------------------------
NS = "checks['NARROW_SCAN_ARM1'] = scan[1] is not None and scan[1] <= NARROW_SCAN_MAX"
mutant('NARROW_SCAN_off', NS, "checks['NARROW_SCAN_ARM1'] = True")
mutant('NARROW_SCAN_arm0', NS, "checks['NARROW_SCAN_ARM1'] = scan[0] is not None and scan[0] <= NARROW_SCAN_MAX")
mutant('NARROW_SCAN_lt', NS, "checks['NARROW_SCAN_ARM1'] = scan[1] is not None and scan[1] < NARROW_SCAN_MAX")
mutant('NARROW_SCAN_none_passes', NS, "checks['NARROW_SCAN_ARM1'] = scan[1] is None or scan[1] <= NARROW_SCAN_MAX")
mutant('NARROW_SCAN_all_arm1_rows', NS, "checks['NARROW_SCAN_ARM1'] = statistics.fmean(r['bda_scan'] for r in "
       "rows.values() if r.get('arm') == 1 and 'bda_scan' in r) <= NARROW_SCAN_MAX")
mutant('NARROW_SCAN_199', NL + 'NARROW_SCAN_MAX = 200', NL + 'NARROW_SCAN_MAX = 199')
mutant('NARROW_SCAN_201', NL + 'NARROW_SCAN_MAX = 200', NL + 'NARROW_SCAN_MAX = 201')
# ---- arming: NO_CHECK / NO_XTHR (sums over ALL rows) -------------------------------------------------------------------
NC = "checks['NO_CHECK'] = would == 0 and miss == 0"
mutant('NO_CHECK_off', NC, "checks['NO_CHECK'] = True")
mutant('NO_CHECK_would_unchecked', NC, "checks['NO_CHECK'] = miss == 0")
mutant('NO_CHECK_miss_unchecked', NC, "checks['NO_CHECK'] = would == 0")
mutant('NO_CHECK_tol1', NC, "checks['NO_CHECK'] = would <= 1 and miss <= 1")
mutant('NO_CHECK_would_kept_only', "would = sum(r.get('bda_nwould', 0) for r in rows.values())",
       "would = sum(rows[n].get('bda_nwould', 0) for n in sel['rows'])")
mutant('NO_CHECK_miss_kept_only', "miss = sum(r.get('bda_nmiss', 0) for r in rows.values())",
       "miss = sum(rows[n].get('bda_nmiss', 0) for n in sel['rows'])")
NX = "checks['NO_XTHR'] = xthr == 0"
mutant('NO_XTHR_off', NX, "checks['NO_XTHR'] = True")
mutant('NO_XTHR_tol1', NX, "checks['NO_XTHR'] = xthr <= 1")
mutant('NO_XTHR_kept_only', "xthr = sum(r.get('bda_nxthr', 0) for r in rows.values())",
       "xthr = sum(rows[n].get('bda_nxthr', 0) for n in sel['rows'])")
# ---- arming: DEFAULTS_ON (cspfree, re-anchored on the session-113 expression; its daslot parts) ------------------------
DF = "bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0" + NL
mutant('DEFAULTS_off', "checks['DEFAULTS_ON'] = bool(", "checks['DEFAULTS_ON'] = True or bool(")
mutant('DEFAULTS_arm0_unchecked', DF, "bool((hits[1] or 0) >= 1 and free_bad == 0" + NL)
mutant('DEFAULTS_arm1_unchecked', DF, "bool((hits[0] or 0) >= 1 and free_bad == 0" + NL)
mutant('DEFAULTS_bad_unchecked', DF, "bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1" + NL)
mutant('DEFAULTS_gt1', DF, "bool((hits[0] or 0) > 1 and (hits[1] or 0) > 1 and free_bad == 0" + NL)
mutant('DEFAULTS_gt0', DF, "bool((hits[0] or 0) > 0 and (hits[1] or 0) > 0 and free_bad == 0" + NL)
mutant('DEFAULTS_reads_look', "hits = [lev[a].get('cspfree_hit') for a in (0, 1)]",
       "hits = [lev[a].get('cspfree_look') for a in (0, 1)]")
mutant('DEFAULTS_bad_kept_only', "free_bad = sum(r.get('cspfree_bad', 0) for r in rows.values())",
       "free_bad = sum(rows[n].get('cspfree_bad', 0) for n in sel['rows'])")
QF = "and (qfree[0] or 0) >= 1 and (qfree[1] or 0) >= 1 and slot_bad == 0)"
mutant('DEFAULTS_qfree0_unchecked', QF, "and (qfree[1] or 0) >= 1 and slot_bad == 0)")
mutant('DEFAULTS_qfree1_unchecked', QF, "and (qfree[0] or 0) >= 1 and slot_bad == 0)")
mutant('DEFAULTS_slot_bad_unchecked', QF, "and (qfree[0] or 0) >= 1 and (qfree[1] or 0) >= 1)")
mutant('DEFAULTS_qfree_gt1', QF, "and (qfree[0] or 0) > 1 and (qfree[1] or 0) > 1 and slot_bad == 0)")
mutant('DEFAULTS_qfree_gt0', QF, "and (qfree[0] or 0) > 0 and (qfree[1] or 0) > 0 and slot_bad == 0)")
QL = "qfree = [lev[a].get('da_q_free') for a in (0, 1)]"
mutant('DEFAULTS_qfree_reads_qcall', QL, "qfree = [lev[a].get('da_qcall') for a in (0, 1)]")
mutant('DEFAULTS_qfree_all_rows', QL,
       "qfree = [sum(r.get('da_q_free', 0) for r in rows.values() if r.get('arm') == a) for a in (0, 1)]")
SB = "slot_bad = sum(r.get('da_slot_bad', 0) for r in rows.values())"
mutant('DEFAULTS_slot_bad_kept_only', SB, "slot_bad = sum(rows[n].get('da_slot_bad', 0) for n in sel['rows'])")
mutant('DEFAULTS_slot_bad_reads_chk', SB, "slot_bad = sum(r.get('da_chk_bad', 0) for r in rows.values())")
""")
m.rep("""# ---- the b47b58a9 schema: each daslot / daguard counter out of it, two moved to another line -------------------------------
for key in ('da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_slot_bad', 'da_q_free',
            'da_chk_ok', 'da_chk_bad', 'da_q_noguard', 'da_guard_yield'):
    mutant('SCHEMA_no_%s' % key, "'%s': 'x'," % key, "")
mutant('SCHEMA_q_free_on_draw', "'da_q_free': 'x',", "'da_q_free': 'draw',")
mutant('SCHEMA_noguard_on_draw', "'da_q_noguard': 'x',", "'da_q_noguard': 'draw',")""",
      """# ---- the 94362eae schema: each daslot / daguard / bdanarrow counter out of it, three moved to another line, bda_scan --
for key in ('da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_slot_bad', 'da_q_free',
            'da_chk_ok', 'da_chk_bad', 'da_q_noguard', 'da_guard_yield', 'bda_ginv_reg', 'bda_ginv_map', 'bda_rinv',
            'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict'):
    mutant('SCHEMA_no_%s' % key, "'%s': 'x'," % key, "")
mutant('SCHEMA_q_free_on_draw', "'da_q_free': 'x',", "'da_q_free': 'draw',")
mutant('SCHEMA_noguard_on_draw', "'da_q_noguard': 'x',", "'da_q_noguard': 'draw',")
mutant('SCHEMA_nskip_on_draw', "'bda_nskip': 'x',", "'bda_nskip': 'draw',")
mutant('SCHEMA_no_bda_scan', "    'bda_scan': 'draw'," + NL, "")
mutant('SCHEMA_scan_on_x', "'bda_scan': 'draw',", "'bda_scan': 'x',")""")
m.span("# ---- the sealed constants ----", "# ---- tags and refusal / verdict texts ----",
       """# ---- the sealed constants ---------------------------------------------------------------------------------------------
mutant('CONST_root_s112', "PRODUCTION_ROOT = 'C:/kyty/s113'", "PRODUCTION_ROOT = 'C:/kyty/s112'")
mutant('CONST_pred_net112', "PRED = 'C:/kyty/s113/pred/02_shn113.md'", "PRED = 'C:/kyty/s112/pred/02_net112.md'")
# a half-filled seal (CONSTANTS: both None, or a sha256 and a size)
mutant('CONST_pred_sha_prefilled', "PRED_SHA = None          #", "PRED_SHA = '0' * 64     #")
mutant('CONST_pred_bytes_prefilled', "PRED_BYTES = None        #", "PRED_BYTES = 1           #")
mutant('CONST_binary_b47b58a9', "BINARY_SHA = '94362eae5e28fa68c6a9d5ed921510a1fb1caa2868b0aa220099ba333df4da92'",
       "BINARY_SHA = 'b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7'")
mutant('CONST_gates_s112', "GATES_FILE = 'C:/kyty/s113/gates_base.txt'", "GATES_FILE = 'C:/kyty/s112/gates_base.txt'")
ARMS_NOW = "ARMS = ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=1')"
mutant('CONST_arms_swapped', ARMS_NOW, "ARMS = ('dawalk=1 dawalklead=1 bdanarrow=1', 'dawalk=1 dawalklead=1 bdanarrow=0')")
mutant('CONST_arms_net112', ARMS_NOW,
       "ARMS = ('dawalk=1 dawalklead=1 daslot=1 daguard=1', 'dawalk=1 dawalklead=1 daslot=0 daguard=0')")
mutant('CONST_arms_mode2', ARMS_NOW, "ARMS = ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=2')")
mutant('CONST_schedule_no_start', "SCHEDULE = '90+1800:%s|%s' % ARMS", "SCHEDULE = '90:%s|%s' % ARMS")
""")
m.span("# ---- tags and refusal / verdict texts ----", "# ---- the ship bar's edge ----",
       """# ---- tags and refusal / verdict texts ---------------------------------------------------------------------------------
TAG_NOW = "TAG_RE = r'shn113b?(?:_entry1)?'"
mutant('TAG_accepts_net112', TAG_NOW, "TAG_RE = r'(?:shn113|net112)b?(?:_entry1)?'")
mutant('TAG_accepts_vsn113', TAG_NOW, "TAG_RE = r'(?:shn113|vsn113)b?(?:_entry1)?'")
mutant('TAG_no_b', TAG_NOW, "TAG_RE = r'shn113(?:_entry1)?'")
mutant('TAG_no_entry1', TAG_NOW, "TAG_RE = r'shn113b?'")
mutant('TAG_search', "        if not re.fullmatch(TAG_RE, o.tag):", "        if not re.search(TAG_RE, o.tag):")
mutant('TAG_msg_old', "(shn113, shn113b, optional _entry1)", "(net112, net112b, optional _entry1)")
mutant('GEOM_msg_old', "'--period/--start/--first/--keep/--secondary are --draft only'",
       "'--period/--start/--first/--keep are --draft only'")
mutant('SEAL_msg_old', "size into shn113.py (only --draft", "size into net112.py (only --draft")
mutant('PENDING_text_old', "nothing ships until vsn113 is read", "nothing changes until vnet112 is read")
mutant('PENDING_name_old', "'SHIP_PENDING_VIDEO (", "'REVERT_PENDING_VIDEO (")
mutant('VERDICT_na_old', "'KEEP bdanarrow=0 (run not admitted)'", "'KEEP daslot=1 (run not admitted)'")
mutant('VERDICT_bar_old', "'KEEP bdanarrow=0 (ship rule S1-S2 on mean dt not met)'",
       "'KEEP daslot=1 (revert rule S1-S2 on mean dt not met)'")
mutant('VERDICT_ship_old', "'SHIP bdanarrow=1 as the new default", "'REVERT to daslot=0 daguard=0 as the new default")
mutant('VERDICT_video_old', "'KEEP bdanarrow=0 (video pass failed)'", "'KEEP daslot=1 (video pass failed)'")
mutant('SCORER_name_old', "out = {'scorer': 'shn113.py',", "out = {'scorer': 'net112.py',")
mutant('SUMMARY_name_old', "lines = ['shn113.py %s status=%s seal=%s'", "lines = ['net112.py %s status=%s seal=%s'")
""")
m.keep("""mutant('S1_strict', "dt['mean'] <= SHIP_US,", "dt['mean'] < SHIP_US,")""")
m.span("# ---- predictions N1-N7 ----", "# ---- the session-111 audit's shp111 mutants",
       """# ---- predictions P1-P7 --------------------------------------------------------------------------------------------------
P1 = "lev[0].get('bda_scan'), 800, 1400)"
P2 = "lev[1].get('bda_scan'), 30, 200)"
P3 = "stats['dt_us']['mean'], -1500, 200)"
P4 = "stats['dt_us']['mean'], None, -100)"
P5 = "stats['gpu_busy_us']['mean'], -150, 150)"
P6 = "lev[1].get('bda_nskip'), 0.5, 3)"
P7 = "stats['da_miss']['mean'], -40, 40)"
mutant('PRED_P1_named_N1', "add('P1',", "add('N1',")
mutant('PRED_P1_arm1', P1, "lev[1].get('bda_scan'), 800, 1400)")
mutant('PRED_P1_lo_799', P1, "lev[0].get('bda_scan'), 799, 1400)")
mutant('PRED_P1_lo_801', P1, "lev[0].get('bda_scan'), 801, 1400)")
mutant('PRED_P1_hi_1399', P1, "lev[0].get('bda_scan'), 800, 1399)")
mutant('PRED_P1_hi_1401', P1, "lev[0].get('bda_scan'), 800, 1401)")
mutant('PRED_P2_arm0', P2, "lev[0].get('bda_scan'), 30, 200)")
mutant('PRED_P2_lo_29', P2, "lev[1].get('bda_scan'), 29, 200)")
mutant('PRED_P2_lo_31', P2, "lev[1].get('bda_scan'), 31, 200)")
mutant('PRED_P2_hi_199', P2, "lev[1].get('bda_scan'), 30, 199)")
mutant('PRED_P2_hi_201', P2, "lev[1].get('bda_scan'), 30, 201)")
mutant('PRED_P3_lo_-1501', P3, "stats['dt_us']['mean'], -1501, 200)")
mutant('PRED_P3_lo_-1499', P3, "stats['dt_us']['mean'], -1499, 200)")
mutant('PRED_P3_hi_199', P3, "stats['dt_us']['mean'], -1500, 199)")
mutant('PRED_P3_hi_201', P3, "stats['dt_us']['mean'], -1500, 201)")
mutant('PRED_P3_hi_0', P3, "stats['dt_us']['mean'], -1500, 0)")          # the band before the executor's change
mutant('PRED_P4_hi_-99', P4, "stats['dt_us']['mean'], None, -99)")
mutant('PRED_P4_hi_-101', P4, "stats['dt_us']['mean'], None, -101)")
mutant('PRED_P4_bounded', P4, "stats['dt_us']['mean'], -300, -100)")
mutant('PRED_P4_sign', P4, "-stats['dt_us']['mean'], None, -100)")
mutant('PRED_P4_text_medium', "the discriminating prediction, low '", "the discriminating prediction, medium '")
mutant('PRED_P5_reads_draws', P5, "stats['draws']['mean'], -150, 150)")
mutant('PRED_P5_lo_-151', P5, "stats['gpu_busy_us']['mean'], -151, 150)")
mutant('PRED_P5_lo_-149', P5, "stats['gpu_busy_us']['mean'], -149, 150)")
mutant('PRED_P5_hi_149', P5, "stats['gpu_busy_us']['mean'], -150, 149)")
mutant('PRED_P5_hi_151', P5, "stats['gpu_busy_us']['mean'], -150, 151)")
mutant('PRED_P6_arm0', P6, "lev[0].get('bda_nskip'), 0.5, 3)")
mutant('PRED_P6_reads_ginv', P6, "lev[1].get('bda_ginv_reg'), 0.5, 3)")
mutant('PRED_P6_lo_0.4', P6, "lev[1].get('bda_nskip'), 0.4, 3)")
mutant('PRED_P6_lo_0.6', P6, "lev[1].get('bda_nskip'), 0.6, 3)")
mutant('PRED_P6_hi_2.9', P6, "lev[1].get('bda_nskip'), 0.5, 2.9)")
mutant('PRED_P6_hi_3.1', P6, "lev[1].get('bda_nskip'), 0.5, 3.1)")
mutant('PRED_P7_reads_late', P7, "stats['da_late']['mean'], -40, 40)")
mutant('PRED_P7_lo_-41', P7, "stats['da_miss']['mean'], -41, 40)")
mutant('PRED_P7_lo_-39', P7, "stats['da_miss']['mean'], -39, 40)")
mutant('PRED_P7_hi_39', P7, "stats['da_miss']['mean'], -40, 39)")
mutant('PRED_P7_hi_41', P7, "stats['da_miss']['mean'], -40, 41)")
mutant('PRED_hit_open_lower', "return v is not None and (lo is None or v >= lo)", "return v is not None and (lo is None or v > lo)")
mutant('PRED_hit_open_upper', "and (hi is None or v <= hi)", "and (hi is None or v < hi)")

# ==== session 113 =====================================================================================================
# ---- the quoted size (report only) and the added claim ------------------------------------------------------------------
mutant('SIZE_sign', "    return {'mean': dt['mean'], 'two_se'",
       "    return {'mean': -dt['mean'] if dt['mean'] is not None else None, 'two_se'")
mutant('SIZE_1se', "'two_se': 2 * dt['se'] if dt['se'] is not None else None",
       "'two_se': 1 * dt['se'] if dt['se'] is not None else None")
mutant('SIZE_secondary', "    out['reported']['quoted_size'] = quoted_size(dt)",
       "    out['reported']['quoted_size'] = quoted_size(out['secondary']['pair_stats']['dt_us'])")
mutant('SIZE_summary_dropped', "    if size:" + NL, "    if False:" + NL)
mutant('SIZE_label', "SIZE_LABEL = 'bdanarrow=1 against bdanarrow=0 of build 94362eae, OLD regime, main estimator'",
       "SIZE_LABEL = 'bdanarrow=1 against bdanarrow=0, main estimator'")
mutant('CLAIM_dropped', "a gain in the NEW regime or", "a gain or")
""")
m.rep("# (SLOT_DARK_tol5 is above, ported to SLOT_DARK_ARM1; SCHEMA_no_q_taking = SCHEMA_no_da_q_taking, not repeated)",
      "# (SLOT_DARK_tol5 went with the SLOT_* terms in session 113; SCHEMA_no_q_taking = SCHEMA_no_da_q_taking, not\n"
      "# repeated)")
m.keep("mutant('VIDEO_frames_3001', 'VIDEO_MIN_FRAMES = 3000', 'VIDEO_MIN_FRAMES = 3001')")
m.rep("        path = MUT / ('net112_%s.py' % name)", "        path = MUT / ('shn113_%s.py' % name)")
m.write('mut_shn113.py',
        stale=('s106_stage/net112', "'net112_%s.py'", "SCORER = HERE / 'net112.py'", 'S1_dt_le_0', 'SHIP_US = 0.0',
               'SA0 =', 'NA1 =', "'SLOT_ARMED_off'", "'NOGUARD_", "'SLOT_NO_BAD_", 'GAIN_', "'PRED_N",
               'PRED_ratio_inverted', 'daguard_0_in_gate_text', 's111_gain', 'b47b58a9 schema'),
        fresh=("SCORER = HERE / 'shn113.py'", "TEST = HERE / 'test_shn113.py'", "'shn113_%s.py'", 'REGIME_none_passes',
               'NARROW_SCAN_201', 'NO_CHECK_tol1', 'NO_XTHR_kept_only', 'DEFAULTS_qfree_gt0', 'SHIP_bar_-99',
               'PRED_P6_hi_3.1', 'SIZE_sign', 'SCHEMA_scan_on_x', 'VIDEO_gate_any_mode', 'HOLD_tol_4'))
