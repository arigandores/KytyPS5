"""Session 112: derive net112.py (scorer of pred/02_net112.md, the ABBA of today's default `daslot=1 daguard=1` against
the pre-session profile `daslot=0 daguard=0`), its fixtures test_net112.py and its mutation harness mut_net112.py from
session 111's shp111.py (the SEALED copy: PRED_SHA / PRED_BYTES are set back to None here, the executor fills them when
pred/02 is sealed), test_shp111.py and mut_shp111.py (sha256 of all three pinned below).  Copied and edited, not
imported - the same method as make_shp111.py: every edit is an anchored replace that must match exactly once
(`rep`); a replaced section is the text between two anchors that each occur exactly once, its old text asserted to
occur exactly once too (`span`); a docstring is an exact split on its delimiters with its first and last text asserted;
anchors that must survive unchanged are asserted (`keep`).  Output bytes are LF / utf-8, written in binary, so two runs
give the same bytes (the sha256 of each output is printed).
    python make_net112.py
"""
import hashlib

S111 = 'C:/kyty/s111/'
OUT = 'C:/kyty/s106_stage/'
PINS = {'shp111.py': '79dd24e60a3d93d44aa87a43b54eeac1f57de415bd8871746e4614ad934b248f',
        'test_shp111.py': '4b0b7aebc81e33b314a615ebe95a742f3d8a4c012ae38d01008729423688b370',
        'mut_shp111.py': 'afd6147e4592124e00d44f109c699c1b54b694066ef672fc2dc125e88de551b2'}


class Src:
    def __init__(self, name):
        raw = open(S111 + name, 'rb').read()
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
# net112.py from shp111.py
# =====================================================================================================================
s = Src('shp111.py')
s.docstring('Session 111, the SHIP run of knob `daslot` (QueueDrawAhead',
            'decision term reads it (derived(), block_means(), pair\nstats and the summary only).\n',
            '''Session 112, the ABBA `net112`: what knob `daslot=1` (session 111's default - QueueDrawAhead, the walker thread's
M1 queueing, off PipelineCache::m_mutex) gains against the pre-session profile.  Arm 0 = today's shipped default
`dawalk=1 dawalklead=1 daslot=1 daguard=1`; arm 1 = the candidate `dawalk=1 dawalklead=1 daslot=0 daguard=0` (knob
daguard=0 at daslot=0 skips the session-111 slot guards inside the m_mutex hold: the session-110 walker hold; audit111
MAJOR-1).  Shipping configuration otherwise (compute precache on, knob cspfree=1 by default in BOTH arms), sealed to
pred/02_net112.md.  Derived from session 111's shp111.py (copied, not imported; make_net112.py) for the build
b47b58a9, whose FrameTrace-x rows add da_q_noguard and da_guard_yield after da_chk_bad (both in the schema);
predictions N1-N7, report only, each printed with HIT / MISS.

    python C:/kyty/s112/net112.py net112 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s112/net112.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Estimator (as in shp111.py; the executor's decision after session 110, ROADMAP s0.1 item 1): the MAIN estimator is
rows 10..89 of each 90-frame block (KEEP_LO, KEEP_HI = 10, 90).  The rule S1/S2, the pair statistics, BANDS,
WORK_SPLIT, AREA_SELECTED, the arm levels, the arming totals, the quoted size and the predictions read it.  The
session-110 window, rows 60..88 (SECONDARY_LO, SECONDARY_HI = 60, 89), is computed with its own selection and printed
as `secondary` (pair statistics and the S1/S2 values it would give); no admission or decision term reads it.  Pairing:
whole ABBA quartets, the others excluded as edge blocks.

Rule (ROADMAP s0.1, the executor's decision after session 111 item 1; session-112 records items 1-4): the default
stays daslot=1 unless daslot=1 is worse than the candidate with 2SE excluding 0.  d = arm 1 - arm 0 (candidate minus
today).  "Ship" in the code's names means shipping the candidate, i.e. REVERTING the default to daslot=0 daguard=0,
which happens only if the run is ADMITTED - including SYNC_COMPILE: over all rows from frame 2100, sum cs_sync_new of
arm 1 <= that of arm 0 + 2 - and S1 d mean dt_us (main estimator) <= SHIP_US = 0 and S2 d mean + 2SE < 0, and the
video pass vnet112 (gate file gates_guard0.txt = gates_base.txt + daslot=0 daguard=0, pinned, >= 3000 frames, 0
one-frame glitches) reads PASS; otherwise KEEP daslot=1.  At this bar S2 implies S1 (S1 never fails alone).  Whenever
a pair exists, the quoted size of session 111's gain against the pre-session profile, -(d mean dt_us) = arm 0 - arm 1
with its 2SE on the main estimator, is reported (out['reported']['s111_gain_vs_pre_session'] and the summary); it
decides nothing.  Arming (under control ARMING): the walk checks (unchanged); SLOT_ARMED_ARM0 (arm-0 level of
da_q_free >= 1); SLOT_DARK_ARM1 (arm-1 kept rows: sum da_q_free = 0); NOGUARD_ARMED_ARM1 (arm-1 level of da_q_noguard
>= 1); NOGUARD_DARK_ARM0 (arm-0 kept rows: sum da_q_noguard = 0); SLOT_NO_BAD (sum da_slot_bad = 0 over all rows);
DEFAULTS_ON (cspfree_hit level >= 1 in both arms and sum cspfree_bad = 0 over all rows); INSTRUMENTS_DARK.  d
cpu_net_us is reported, never deciding: no admission or decision term reads it (derived(), block_means(), pair stats
and the summary only).
''')

# ---- constants ---------------------------------------------------------------------------------------------------
s.rep("PRODUCTION_ROOT = 'C:/kyty/s111'", "PRODUCTION_ROOT = 'C:/kyty/s112'")
s.rep("PRED = 'C:/kyty/s111/pred/03_shp111.md'", "PRED = 'C:/kyty/s112/pred/02_net112.md'")
# the sealed copy's values go back to None: the executor fills them when pred/02 is sealed (make_shp111's draft form)
s.rep("PRED_SHA = '594e2402c8022dcd0a71ab111cb58f355400b51a261600a48c74eea044125f3f'   # pred/03_shp111.md sealed",
      "PRED_SHA = None          # filled by the executor when pred/02 is sealed")
s.rep("PRED_BYTES = 3604       # pred/03_shp111.md sealed",
      "PRED_BYTES = None        # filled by the executor when pred/02 is sealed")
s.rep("BINARY_SHA = 'c8235c902e08d00782d0cff23528361d194a501ad1899344ca8302c742372a86'",
      "BINARY_SHA = 'b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7'")
s.rep("GATES_FILE = 'C:/kyty/s111/gates_base.txt'", "GATES_FILE = 'C:/kyty/s112/gates_base.txt'")
s.keep("GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'")
s.keep("PERIOD, START, FIRST_FRAME = 90, 1800, 2100")
s.keep("KEEP_LO, KEEP_HI = 10, 90                  # MAIN estimator: in-block rows 10..89 (decision after session 110)")
s.keep("SECONDARY_LO, SECONDARY_HI = 60, 89        # the session-110 window, rows 60..88: printed, never deciding")
s.keep("MIN_PAIRS = 60")
s.keep("HOLD_S = 600")
s.rep("ARMS = ('dawalk=1 dawalklead=1 daslot=0', 'dawalk=1 dawalklead=1 daslot=1')",
      "ARMS = ('dawalk=1 dawalklead=1 daslot=1 daguard=1', 'dawalk=1 dawalklead=1 daslot=0 daguard=0')")
s.keep("SCHEDULE = '90+1800:%s|%s' % ARMS")
s.rep("TAG_RE = r'shp111b?(?:_entry1)?'", "TAG_RE = r'net112b?(?:_entry1)?'")
s.rep("SHIP_US = -100.0          # on d mean dt_us (ROADMAP, decision after session 104)\n",
      "SHIP_US = 0.0             # on d mean dt_us = arm 1 - arm 0: the revert bar (ROADMAP, decision after session 111)\n"
      "GAIN_LABEL = (\"session 111's gain against the pre-session profile (arm 0 - arm 1 = -(d mean dt_us), main \"\n"
      "              'estimator; negative: daslot=1 faster)')\n")
s.keep("VIDEO_MIN_FRAMES = 3000")
s.keep("ID_TOL = 0.01")
s.keep("AREA_SPLIT_PCT, AREA_MATCH_PCT, AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8")
# every FrameTrace-x row of the b47b58a9 build carries the two session-112 counters after da_chk_bad (patch_s112.py,
# "Session 112, knob "daguard"": da_q_noguard, da_guard_yield): into the schema
s.rep("""    'da_q_free': 'x', 'da_chk_ok': 'x', 'da_chk_bad': 'x',
}""", """    'da_q_free': 'x', 'da_chk_ok': 'x', 'da_chk_bad': 'x',
    'da_q_noguard': 'x', 'da_guard_yield': 'x',
}""")
s.keep("SYNC_SLACK = 2")
s.keep("""FATAL = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
         b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:',
         b'AsyncPipelines: skipped draw')""")
s.keep("""ENV_EXPECTED = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1',""")
s.rep("size into shp111.py (only --draft runs without a seal)", "size into net112.py (only --draft runs without a seal)")

# ---- a ratio helper for N1 / N2 (after rel()) ------------------------------------------------------------------------
s.rep("""    return a / b - 1.0


def new_counts():""", """    return a / b - 1.0


def ratio(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def new_counts():""")

# ---- statistics / selection / protocol: kept verbatim ------------------------------------------------------------------
s.keep("    sd = statistics.stdev(values)")
s.keep("    return statistics.median(values) if values else None")
s.keep("        kept = expected[lo:hi]")
s.keep("        if (a.get('hold_s') or 0) < HOLD_S - 5:")
s.keep("        if a0['n'] < min_flips or a1['n'] < min_flips:")

# ---- arming: SLOT_DARK_ARM0 / SLOT_ARMED_ARM1 -> SLOT_ARMED_ARM0, SLOT_DARK_ARM1, NOGUARD_ARMED_ARM1, NOGUARD_DARK_ARM0
s.rep('    """pred/03 (the lead105 walk arming plus SLOT_DARK_ARM0, SLOT_ARMED_ARM1, SLOT_NO_BAD and DEFAULTS_ON)."""',
      '    """pred/02 (the lead105 walk arming plus SLOT_ARMED_ARM0, SLOT_DARK_ARM1, NOGUARD_ARMED_ARM1, NOGUARD_DARK_ARM0,\n'
      '    SLOT_NO_BAD and DEFAULTS_ON)."""')
s.rep("""    # Session 111: the daslot knob dark in arm 0 (no QueueDrawAhead call without m_mutex over the kept rows), armed
    # in arm 1 (level >= 1), and no knob-2 slot-key disagreement anywhere (over all rows; knob 1 never verifies,
    # so a non-zero sum means a wrong build or knob).
    free0 = kept_total(rows, sel, arms, 0, 'da_q_free')
    checks['SLOT_DARK_ARM0'] = free0 == 0
    checks['SLOT_ARMED_ARM1'] = bool((lev[1].get('da_q_free') or 0) >= 1)
    bad = sum(r.get('da_slot_bad', 0) for r in rows.values())
""", """    # Session 112: arm 0 (today's default daslot=1 daguard=1) queues off m_mutex (da_q_free level >= 1) and never
    # without the slot guards (no da_q_noguard over its kept rows); arm 1 (the candidate daslot=0 daguard=0) queues
    # without the guards (da_q_noguard level >= 1) and never off m_mutex (no da_q_free over its kept rows).  And no
    # knob-2 slot-key disagreement anywhere (over all rows; knob 1 never verifies, so a non-zero sum means a wrong build
    # or knob).
    checks['SLOT_ARMED_ARM0'] = bool((lev[0].get('da_q_free') or 0) >= 1)
    free1 = kept_total(rows, sel, arms, 1, 'da_q_free')
    checks['SLOT_DARK_ARM1'] = free1 == 0
    checks['NOGUARD_ARMED_ARM1'] = bool((lev[1].get('da_q_noguard') or 0) >= 1)
    noguard0 = kept_total(rows, sel, arms, 0, 'da_q_noguard')
    checks['NOGUARD_DARK_ARM0'] = noguard0 == 0
    bad = sum(r.get('da_slot_bad', 0) for r in rows.values())
""")
s.keep("    checks['SLOT_NO_BAD'] = bad == 0")
s.keep("    checks['DEFAULTS_ON'] = bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0)")
s.keep("    checks['INSTRUMENTS_DARK'] = dark")
s.rep("""            'slot_arm0_kept': {'da_q_free': free0}, 'da_slot_bad_all_rows': bad,
""", """            'slot_arm1_kept': {'da_q_free': free1}, 'noguard_arm0_kept': {'da_q_noguard': noguard0},
            'da_slot_bad_all_rows': bad,
""")

# ---- video: vss111 -> vnet112 (the nine checks; the gate-text check names the candidate's two knobs) -----------------
s.rep('    """pred/03 video pass vss111 (pinned; gate file gates_slot1.txt = gates_base.txt + daslot=1).  Returns\n'
      '    (state, detail): state in PASS / FAIL / ABSENT."""',
      '    """pred/02 video pass vnet112 (pinned; gate file gates_guard0.txt = gates_base.txt + daslot=0 daguard=0).\n'
      '    Returns (state, detail): state in PASS / FAIL / ABSENT."""')
s.rep("""        'daslot_1_in_gate_text': ' dawalk=1 ' in gates and ' daslot=1 ' in gates,""",
      """        'daguard_0_in_gate_text': ' dawalk=1 ' in gates and ' daslot=0 ' in gates and ' daguard=0 ' in gates,""")
s.keep("        'frames': frames is not None and frames >= VIDEO_MIN_FRAMES,")

# ---- the rule: S1 at the bar 0 (renamed), S2 unchanged; the quoted size ------------------------------------------------
s.rep('''    """S1 / S2 of the ship rule on one estimator's d dt_us statistics."""
    return {
        'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,''',
      '''    """S1 / S2 of the rule to ship the candidate (arm 1: revert the default) on one estimator's d dt_us statistics."""
    return {
        'S1_dt_le_0': dt['mean'] is not None and dt['mean'] <= SHIP_US,''')
s.rep('''def secondary(rows, arms, geo):''', '''def s111_gain(dt):
    """The quoted size (pred/02 s4): session 111's gain against the pre-session profile = arm 0 - arm 1 = -(d mean
    dt_us), with its 2SE, from one estimator's d dt_us statistics (us a flip; negative: today's daslot=1 faster).
    Report only: no admission or decision term reads it."""
    mean = -dt['mean'] if dt['mean'] is not None else None
    return {'mean': mean, 'two_se': 2 * dt['se'] if dt['se'] is not None else None, 'n': dt['n'],
            'label': GAIN_LABEL}


def secondary(rows, arms, geo):''')

# ---- evaluate() ---------------------------------------------------------------------------------------------------
s.rep("out = {'scorer': 'shp111.py',", "out = {'scorer': 'net112.py',")
s.rep("    # Session 108 guard, kept verbatim (pred/03): the dispatch-time compile guard over ALL rows from the first\n",
      "    # Session 108 guard, kept verbatim (pred/02): the dispatch-time compile guard over ALL rows from the first\n")
s.keep("    controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK")
s.keep("    rules = ship_rules(dt)")
s.rep("""    for k in ('da_q_free', 'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn'):
        out['reported'][k + '_levels'] = [lev[0].get(k), lev[1].get(k)]
""", """    for k in ('da_q_free', 'da_q_noguard', 'da_guard_busy', 'da_guard_yield', 'da_q_taking', 'da_hint_defer',
              'da_hint_torn'):
        out['reported'][k + '_levels'] = [lev[0].get(k), lev[1].get(k)]
    # The quoted size (pred/02 s4), main estimator, report only.
    out['reported']['s111_gain_vs_pre_session'] = s111_gain(dt)
""")

# ---- predictions K1-K6 -> N1-N7 (pred/02_net112) --------------------------------------------------------------------
s.rep("""    add('K1', 'arm-1 da_q_free level in [800, 1400] a flip (every QueueDrawAhead call off m_mutex)',
        lev[1].get('da_q_free'), 800, 1400)
    add('K2', 'arm-0 da_q_free level = 0 (the knob dark)', lev[0].get('da_q_free'), 0, 0)
    add('K3', 'd mean dt_us (main estimator, rows 10..89) in [-400, 0] us', stats['dt_us']['mean'], -400, 0)
    add('K4', 'd mean dt_us (main estimator) <= -100 us (the ship bar) - the discriminating prediction, '
        'medium-low confidence', stats['dt_us']['mean'], None, SHIP_US)
    add('K5', 'd da_miss in [-40, +40] a flip', stats['da_miss']['mean'], -40, 40)
    add('K6', 'arm-1 da_guard_busy level <= 5 a flip', lev[1].get('da_guard_busy'), None, 5)""",
      """    add('N1', 'arm-1 walker time per QueueDrawAhead call (level da_queue_us / level da_qcall) in [0.90, 1.12] us',
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
    add('N7', 'd da_miss in [-40, +40] a flip', stats['da_miss']['mean'], -40, 40)""")
s.keep("    return v is not None and (lo is None or v >= lo) and (hi is None or v <= hi)")

# ---- verdict texts -------------------------------------------------------------------------------------------------
s.rep("v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP daslot=0 (run not admitted)'",
      "v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP daslot=1 (run not admitted)'")
s.rep("v = 'KEEP daslot=0 (ship rule S1-S2 on mean dt not met)'",
      "v = 'KEEP daslot=1 (revert rule S1-S2 on mean dt not met)'")
s.rep("v = 'SHIP daslot=1 as the new default (a new build: its video pass is owed, ROADMAP 6)'",
      "v = 'REVERT to daslot=0 daguard=0 as the new default (a new build: its video pass is owed)'")
s.rep("v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vss111 is read)'",
      "v = 'REVERT_PENDING_VIDEO (S1-S2 met; nothing changes until vnet112 is read)'")
s.rep("v = 'KEEP daslot=0 (video pass failed)'", "v = 'KEEP daslot=1 (video pass failed)'")
s.rep("""                                  'read from the secondary 60-88 window')""",
      """                                  'read from the secondary 60-88 window; a gain against a different build; that '
                                  'arm 1 is the session-110 code byte for byte; additivity')""")

# ---- summary (report only) -------------------------------------------------------------------------------------------
s.rep("lines = ['shp111.py %s status=%s seal=%s'", "lines = ['net112.py %s status=%s seal=%s'")
s.rep("""        lines.append('  daslot arm-0 kept totals %s  da_slot_bad over all rows %s  cspfree_hit levels %s  '
                     'cspfree_bad over all rows %s'
                     % (a.get('slot_arm0_kept'), a.get('da_slot_bad_all_rows'), a.get('cspfree_hit_levels'),
                        a.get('cspfree_bad_all_rows')))""",
      """        lines.append('  daslot arm-1 kept totals %s  daguard arm-0 kept totals %s  da_slot_bad over all rows %s  '
                     'cspfree_hit levels %s  cspfree_bad over all rows %s'
                     % (a.get('slot_arm1_kept'), a.get('noguard_arm0_kept'), a.get('da_slot_bad_all_rows'),
                        a.get('cspfree_hit_levels'), a.get('cspfree_bad_all_rows')))""")
s.rep("""                  'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth', 'da_qcall', 'da_q_free',
                  'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'cspfree_hit', 'cspf_have',
                  'cspf_new'):""",
      """                  'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth', 'da_qcall', 'da_q_free', 'da_q_noguard',
                  'da_guard_busy', 'da_guard_yield', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'cspfree_hit',
                  'cspf_have', 'cspf_new'):""")
s.rep("""    sec = out.get('secondary')
    if sec:
""", """    gain = (out.get('reported') or {}).get('s111_gain_vs_pre_session')
    if gain:
        lines.append('  quoted size: %s = %s us a flip, 2SE %s, n %d'
                     % (gain['label'], fmt(gain['mean']), fmt(gain['two_se']), gain['n']))
    sec = out.get('secondary')
    if sec:
""")

# ---- main() ----------------------------------------------------------------------------------------------------------
s.rep("print('tag %r is not a pred/03 tag (shp111, shp111b, optional _entry1)' % o.tag)",
      "print('tag %r is not a pred/02 tag (net112, net112b, optional _entry1)' % o.tag)")
s.keep("        result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)")

s.write('net112.py',
        stale=('shp111', 'vss111', 'pred/03', 'C:/kyty/s111', 'c8235c90', 'daslot_1_in_gate_text', 'SLOT_DARK_ARM0',
               'SLOT_ARMED_ARM1', 'slot_arm0_kept', "'K1'", "'K2'", "'K3'", "'K4'", "'K5'", "'K6'", 'S1_dt_le_-100',
               'SHIP_US = -100.0', 'gates_slot1', 'SHIP daslot=1', 'KEEP daslot=0', '594e2402'),
        fresh=("'N1'", "'N2'", "'N3'", "'N4'", "'N5'", "'N6'", "'N7'", "'scorer': 'net112.py'", 'vnet112',
               'SLOT_ARMED_ARM0', 'SLOT_DARK_ARM1', 'NOGUARD_ARMED_ARM1', 'NOGUARD_DARK_ARM0', 'daguard_0_in_gate_text',
               "'da_q_noguard': 'x'", "'da_guard_yield': 'x'", 'SHIP_US = 0.0', "'S1_dt_le_0'", 'def s111_gain(',
               'def ratio(', "PRED_SHA = None", "PRED_BYTES = None", 'a gain against a different build'))

# =====================================================================================================================
# test_net112.py from test_shp111.py
# =====================================================================================================================
t = Src('test_shp111.py')
t.docstring('Session 111: fixtures for shp111.py (the SHIP run of knob `daslot`',
            '    python test_shp111.py <shp111.py> [<fixture dir>]\n',
            '''Session 112: fixtures for net112.py (the ABBA of today's default daslot=1 daguard=1 against the pre-session profile
daslot=0 daguard=0) in NON-draft mode, derived from session 111's test_shp111.py by make_net112.py (same coverage,
adapted: tag net112, video vnet112, the arms, the b47b58a9 counters da_q_noguard / da_guard_yield, arming
SLOT_ARMED_ARM0 / SLOT_DARK_ARM1 / NOGUARD_ARMED_ARM1 / NOGUARD_DARK_ARM0, the revert bar SHIP_US = 0, the quoted size
of session 111's gain, predictions N1-N7).  Rule (decision after 107, item 2): every decision term and every admission
term gets a fixture where ONLY it fails, plus every verdict branch.  Each case asserts the exact failing set
(failed_controls) AND the exact failing sub-lists: rules, video checks, arming sub-checks (by name, under
control:ARMING), area-mirror criteria where relevant, and the exact protocol error list.  Terms that cannot fail alone
by construction (now also S1: at the bar 0, S2 implies it) are asserted as exact sets, with the scorer lines that
couple them cited at the case.  The seal check is pointed at a throwaway file and GATES_FILE at a sha-checked copy of
gates_base.txt (C:/kyty/s112 need not hold it yet: the copy comes from it when it does, else from C:/kyty/s111 - the
same bytes, GATES_SHA asserted); everything else is the scorer's own code.  IDENTITY exists only in main(): main() is
driven in-process with EXE / PRODUCTION_ROOT pointed at fixtures.  CONSTANTS compares every sealed constant except
PRED_SHA / PRED_BYTES, which it only requires to be both None (the draft) or a 64-hex sha256 and a positive size (the
sealed copy), so the sealed scorer stays green on this suite (audit111 MINOR-5).

The window rows the fixtures edit are HARD-CODED here (MAIN = 10..89, SEC = 60..88), never read from the scorer, so a
mutant of the scorer's window cannot move its own fixtures.  The estimator cases (all noise-free, exact values):
  KEEP_edge        arm-1 row 9 +29 000, rows 10 and 89 -8 000: main -350 exactly, secondary -150 exactly (kills
                   KEEP_LO 9 / 11, KEEP_HI 89, the slice shifted down one row).
  SEC_edge         arm-1 rows 59 and 89 +29 000, rows 60 and 88 -2 900: secondary -350 exactly, main +502.5 exactly
                   (KEEP by the main estimator; the secondary would pass - it never decides).
  EST_rows0_9      arm-1 rows 0..9 +29 000 (the audit110 hitch shape): main and secondary -150 exactly (a full-block
                   estimator would read +3 072).
  EST_rows10_59    arm-1 rows 10..59 +800: main +350 exactly (KEEP), secondary -150 exactly (would pass).
  EST_rows10_59_rev  d 0, arm-1 rows 10..59 -400: main -250 exactly (REVERT pending), secondary 0 (would fail S2).
  PENDING          the noisy base fixture: main and secondary d mean / SE recounted from the log here, independently
                   of the scorer (1e-9 relative), and they differ; the quoted size is -(main d mean) with 2 x its SE.
Killers of the session-109 survivors kept: SE_exact (sample SD), LEVEL_median (median block levels: dt, da_q_free,
da_q_noguard, da_queue_us), FATAL_waitslow_log / _so.  Plus CONSTANTS (the sealed identity and the two windows),
full-text refusals / pending verdict, tag acceptance (net112b, net112_entry1, net112b_entry1 reach evaluate()) and
refusal of the others (session 111's included), the draft-only --secondary.  Threshold edges (audit111 MINOR-10: a
fixture on each side of every tolerance): the bar (S1_edge 0: S2 alone fails; S1_edge_in -0.5 pending; S1_edge_out
+0.5 both fail), the dark totals (SLOT_DARK1_one / NOGUARD_DARK0_one: a total of 1 fails, the good run's 0 passes),
the arming levels (ARMED_edge: 1 passes; *_sparse 0.33 fails), the attempt hold (595 s passes, 594 fails), the area
mirror's minimum block (8 flips count, 7 do not), the walk identity (0.9 % passes, 1.1 % fails), the video floor
(3 000 frames pass, 2 999 fail), and the N1-N7 bands with exact values at, inside and just outside every edge.
    python test_net112.py <net112.py> [<fixture dir>]
''')
t.rep("import random\nimport shutil\n", "import random\nimport re\nimport shutil\n")
t.rep("BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s106_stage/shp111/fx')",
      "BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s106_stage/net112/fx')")
t.rep("spec = importlib.util.spec_from_file_location('shp111', SRC)",
      "spec = importlib.util.spec_from_file_location('net112', SRC)")
t.rep("seal.write_text('fixture seal 111 shp', encoding='utf-8')", "seal.write_text('fixture seal 112 net', encoding='utf-8')")
t.rep("else Path('C:/kyty/s110/gates_base.txt')", "else Path('C:/kyty/s111/gates_base.txt')")
t.rep("TAG = 'shp111'", "TAG = 'net112'")

# ---- make(): the arms of this design (today's default in arm 0, the candidate in arm 1) ------------------------------
t.rep("""         qfree0=0, qfree1=1080, gb0=1, gb1=2, sync0=1, sync1=1, pins=1, pin_mode=1, recs=2, fatal=None,
""", """         qfree0=1080, qfree1=0, ng0=0, ng1=1080, qq0=1296, qq1=1080, qcall=1080, gb0=1, gb1=2, sync0=1, sync1=1,
         pins=1, pin_mode=1, recs=2, fatal=None,
""")
t.rep("""    (default noise; the same random draws are taken either way).  The shipping configuration: cspfree on in BOTH
    arms (look/hit per arm), da_q_free = qfree1 in arm 1 (= da_qcall 1080: every call off m_mutex), qfree0 in arm 0
    and before the schedule; da_guard_busy gb0 / gb1.\"\"\"""",
      """    (default noise; the same random draws are taken either way).  The shipping configuration: cspfree on in BOTH
    arms (look/hit per arm).  Arm 0 (today, daslot=1 daguard=1): da_q_free = qfree0 (= da_qcall 1080: every call off
    m_mutex), da_q_noguard = ng0; arm 1 (the candidate, daslot=0 daguard=0): da_q_free = qfree1, da_q_noguard = ng1
    (every call without the guards); the rows before the schedule are arm 0.  da_queue_us qq0 / qq1 and da_qcall
    qcall (both arms): walker us per call 1.2 / 1.0 by default; da_guard_busy gb0 / gb1.\"\"\"""")
t.rep("""                     'da_queue_us': 1100, 'da_take_us': 2800, 'da_hit': 8350, 'da_miss': 300, 'da_late': 6,
""", """                     'da_queue_us': qq1 if arm else qq0, 'da_take_us': 2800, 'da_hit': 8350, 'da_miss': 300,
                     'da_late': 6,
""")
t.rep("""                  'da_wdepth': 17, 'da_qcall': 1080, 'mw_n': 0,""", """                  'da_wdepth': 17, 'da_qcall': qcall, 'mw_n': 0,""")
t.rep("""                  'da_slot_bad': 0, 'da_q_free': qfree1 if arm else qfree0, 'da_chk_ok': 0, 'da_chk_bad': 0},
""", """                  'da_slot_bad': 0, 'da_q_free': qfree1 if arm else qfree0, 'da_chk_ok': 0, 'da_chk_bad': 0,
                  'da_q_noguard': ng1 if arm else ng0, 'da_guard_yield': 0},
""")

# ---- video(): vnet112, the candidate's gate text -------------------------------------------------------------------
t.rep("""def video(d, frames=3990, glitches=0, gate='daslot=1', pin='1', binary=None, tag='v', rec=True, env_extra=None,
          attempts=None, gates=None):""",
      """def video(d, frames=3990, glitches=0, gate='daslot=0 daguard=0', pin='1', binary=None, tag='v', rec=True,
          env_extra=None, attempts=None, gates=None):""")
t.rep("""    vm = d / ('vss111_%s.json' % tag)
    vr = d / ('vss111_%s_glitch.txt' % tag)""", """    vm = d / ('vnet112_%s.json' % tag)
    vr = d / ('vnet112_%s_glitch.txt' % tag)""")
t.rep('"""Drive shp111.main() in-process;', '"""Drive net112.main() in-process;')

# ---- verdicts, rules, bands, messages, counters --------------------------------------------------------------------
t.span("KEEP_NA = 'KEEP daslot=0 (run not admitted)'", "good = make('good')", """KEEP_NA = 'KEEP daslot=1 (run not admitted)'
KEEP_BAR = 'KEEP daslot=1 (revert rule S1-S2 on mean dt not met)'
KEEP_VID = 'KEEP daslot=1 (video pass failed)'
REVERT = 'REVERT to daslot=0 daguard=0 as the new default (a new build: its video pass is owed)'
PENDING = 'REVERT_PENDING_VIDEO (S1-S2 met; nothing changes until vnet112 is read)'
ARMING = {'control:ARMING'}
BOTH_RULES = ['S1_dt_le_0', 'S2_dt_2se_excludes_0']
PRED_BANDS = {'N1': [0.90, 1.12], 'N2': [1.00, 1.30], 'N3': [0, 300], 'N4': [100, None], 'N5': [800, 1400],
              'N6': [800, 1400], 'N7': [-40, 40]}
# the quoted size's label, written out here (not read from mod.GAIN_LABEL: a changed label must fail)
GAIN_LABEL = ("session 111's gain against the pre-session profile (arm 0 - arm 1 = -(d mean dt_us), main estimator; "
              'negative: daslot=1 faster)')
# the scorer's markers, written out here (not read from mod.FATAL: a dropped marker must still have its case)
FATAL_TEXTS = ('--- Error ---', '--- Fatal Error ---', '--- std::terminate ---', '--- abort() ---', 'ErrorDeviceLost',
               'Unhandled exception:', 'GpuWaitSlow:', 'AsyncPipelines: skipped draw')
WAITSLOW = 'GpuWaitSlow: tick=51234 waited 2000 ms submit_backlog=0 acopy=12/12/12 acopy_pending=0'
TAG_MSG = "tag %r is not a pred/02 tag (net112, net112b, optional _entry1)"
NEW_COUNTERS = ('da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_slot_bad', 'da_q_free',
                'da_chk_ok', 'da_chk_bad', 'da_q_noguard', 'da_guard_yield')

""")
t.rep('''    """the six keys, their sealed bands, the given exact values, and the given hit / miss sets."""''',
      '''    """the seven keys, their sealed bands, the given exact values, and the given hit / miss sets."""''')

# ---- pred_good / gain_exact / const_check ---------------------------------------------------------------------------
t.span("def pred_good(o):", "# ---- the sealed identity", '''def gain_exact(o, mean, two_se):
    """the quoted size in the result (exact) and its summary line (label and format written out here)."""
    g = o['reported']['s111_gain_vs_pre_session']
    line = '  quoted size: %s = %.1f us a flip, 2SE %.1f, n 110' % (GAIN_LABEL, mean, two_se)
    return (g == {'mean': mean, 'two_se': two_se, 'n': 110, 'label': GAIN_LABEL}
            and line in mod.summary(o).split(NL))


def pred_good(o):
    """N1-N7 of the good fixture: the seven keys, their sealed bands, the fixture's exact values (N1 1.0, N2 1.2, N5 /
    N6 1 080, N7 0; N3 / N4 the main d mean, a REVERT here, so both miss), hits N1, N2, N5-N7; the scorer's name in the
    result and in the summary header; both estimators recounted from the log here (1e-9 relative), the secondary's own
    selection (block 3 excluded as an edge block there, nothing excluded in the main one), and the two summary lines
    naming the windows; the quoted size = -(main d mean) with 2 x its SE (result and summary line); the area mirror's
    110 block pairs; the added must-not-be-claimed item."""
    dt = main_dt(o)
    m_main, se_main, n_main = recount(good, MAIN)
    m_sec, se_sec, n_sec = recount(good, SEC)
    lines = mod.summary(o).split(NL)
    return (pred_values(o, N1=1080 / 1080, N2=1296 / 1080, N3=dt, N4=dt, N5=1080, N6=1080, N7=0,
                        hits=['N1', 'N2', 'N5', 'N6', 'N7'])
            and o['scorer'] == 'net112.py' and lines[0].startswith('net112.py net112 status=ADMITTED')
            and o['pair_stats']['dt_us']['n'] == n_main == 110 and close(dt, m_main)
            and close(o['pair_stats']['dt_us']['se'], se_main)
            and o['secondary']['pair_stats']['dt_us']['n'] == n_sec == 110 and close(sec_dt(o), m_sec)
            and close(o['secondary']['pair_stats']['dt_us']['se'], se_sec) and abs(m_main - m_sec) > 1.0
            and o['secondary']['window'] == [60, 89] and o['secondary']['deciding'] is False
            and o['geometry']['keep'] == [10, 90] and o['geometry']['secondary'] == [60, 89]
            and o['selection']['excluded_edge_blocks'] == [] and o['secondary']['excluded_edge_blocks'] == [3]
            and '  main estimator (decides): rows 10..89 of each block' in lines
            and '  secondary estimator (rows 60..88, never deciding): pairs 110, blocks 220, excluded [3]' in lines
            and gain_exact(o, -dt, 2 * o['pair_stats']['dt_us']['se']) and close(-dt, -m_main) and dt < 0
            and o['area_verdict_mirror']['pairs'] == 110
            and 'a gain against a different build' in o['must_not_be_claimed'])


def const_check():
    want = {'PRODUCTION_ROOT': 'C:/kyty/s112', 'PRED': 'C:/kyty/s112/pred/02_net112.md',
            'BINARY_SHA': 'b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7',
            'GATES_FILE': 'C:/kyty/s112/gates_base.txt',
            'GATES_SHA': '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf',
            'ARMS': ('dawalk=1 dawalklead=1 daslot=1 daguard=1', 'dawalk=1 dawalklead=1 daslot=0 daguard=0'),
            'SCHEDULE': '90+1800:dawalk=1 dawalklead=1 daslot=1 daguard=1|dawalk=1 dawalklead=1 daslot=0 daguard=0',
            'TAG_RE': r'net112b?(?:_entry1)?', 'KEEP_LO': 10, 'KEEP_HI': 90, 'SECONDARY_LO': 60,
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

# ---- verdict branches and the decision terms at the bar 0 --------------------------------------------------------------
t.span("# ---- verdict branches ----", "# ---- the estimator: the main window's edges",
       """# ---- verdict branches -------------------------------------------------------------------------------------------
case('REVERT', run_eval(good, *video(good, tag='ok')), REVERT)
case('PENDING', run_eval(good), PENDING, check=pred_good)
case('DRAFT', run_eval(good, draft=True), 'DRAFT (no verdict)', check=lambda o: o['status'] == 'DRAFT')
# KEEP by the bar = S1_S2_positive / S2_only / S1_edge / S1_edge_out / SE_exact / EST_rows10_59 / PRED_*; KEEP by a
# failed video = V_*; KEEP not admitted = every admission case

# ---- decision terms ---------------------------------------------------------------------------------------------
# S1 (d mean <= SHIP_US = 0) cannot fail alone BY CONSTRUCTION: S2 (d mean + 2 SE < 0, with SE >= 0) implies d mean < 0.
# A positive d mean fails both (ship_rules() returns the two terms of one dict; both listed).
case('S1_S2_positive', run_eval(make('s1', d_dt=60, noise=80)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: 0 < main_dt(o) < 100 and o['predictions']['N3']['hit'] and not o['predictions']['N4']['hit'])
case('S2_only', run_eval(make('s2', d_dt=-150, noise=300, block_noise=1500)), KEEP_BAR,
     rules=['S2_dt_2se_excludes_0'])
# the bar's edge, noise-free (every pair delta equal, SE 0): d mean dt exactly 0 - S1 holds (<= 0), S2 fails alone
# (0 + 2 * 0 is not < 0; kills S1 strict and a bar moved to -1) ...
case('S1_edge', run_eval(make('s1edge', d_dt=0, noise=0)), KEEP_BAR, rules=['S2_dt_2se_excludes_0'],
     check=lambda o: (main_dt(o) == 0.0 and o['pair_stats']['dt_us']['sd'] == 0.0
                      and pred_values(o, N3=0.0, N4=0.0, hits=['N1', 'N2', 'N3', 'N5', 'N6', 'N7'])))
# ... -0.5 (arm-1 frames with an even number -1 us: 40 of the 80 main-window rows of each block): both hold, REVERT
# pending (kills a bar moved to -1) ...
case('S1_edge_in', run_eval(make('s1edgein', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and n % 2 == 0, edits={'main': {'dt_us': 31000 - 1}}))), PENDING,
    check=lambda o: main_dt(o) == -0.5 and o['pair_stats']['dt_us']['sd'] == 0.0)
# ... and +0.5 (+1 us on those rows): S1 fails with S2 (kills a bar moved to +1)
case('S1_edge_out', run_eval(make('s1edgeout', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and n % 2 == 0, edits={'main': {'dt_us': 31000 + 1}}))), KEEP_BAR,
    rules=BOTH_RULES, check=lambda o: main_dt(o) == 0.5 and o['pair_stats']['dt_us']['sd'] == 0.0)

""")

# ---- the estimator cases: verdicts at the bar 0 -----------------------------------------------------------------------
t.keep("case('KEEP_edge', run_eval(make('keepedge', noise=0, row=setter(")
t.keep("case('SEC_edge', run_eval(make('secedge', noise=0, row=setter(")
t.keep("case('EST_rows0_9', run_eval(make('estrows0', noise=0, row=setter(")
t.rep("""                     and pred_values(o, K3=350.0, K4=350.0, hits=['K1', 'K2', 'K5', 'K6'])))""",
      """                     and pred_values(o, N3=350.0, N4=350.0, hits=['N1', 'N2', 'N4', 'N5', 'N6', 'N7'])))""")
t.rep("""# the other direction: d 0, arm-1 rows 10..59 -400 us: main -250 exactly (PENDING); the secondary reads 0 exactly and
# would FAIL both rules.
case('EST_rows10_59_ship', run_eval(make('estrows10s', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None and 10 <= i < 60,
    edits={'main': {'dt_us': 31000 - 400}}))), PENDING,
    check=lambda o: (main_dt(o) == -250.0 and sec_dt(o) == 0.0 and sec_rules(o) == BOTH_RULES
                     and '  secondary would FAIL S1_dt_le_-100 (not deciding)' in mod.summary(o).split(NL)))""",
      """# the other direction: d 0, arm-1 rows 10..59 -400 us: main -250 exactly (REVERT pending); the secondary reads 0
# exactly: it would pass S1 (0 <= 0) and FAIL S2 (0 + 2 * 0 is not < 0).
case('EST_rows10_59_rev', run_eval(make('estrows10s', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None and 10 <= i < 60,
    edits={'main': {'dt_us': 31000 - 400}}))), PENDING,
    check=lambda o: (main_dt(o) == -250.0 and sec_dt(o) == 0.0 and sec_rules(o) == ['S2_dt_2se_excludes_0']
                     and '  secondary would FAIL S2_dt_2se_excludes_0 (not deciding)' in mod.summary(o).split(NL)
                     and '  secondary would PASS S1_dt_le_0 (not deciding)' in mod.summary(o).split(NL)))""")
t.keep("assert SE_MEAN + 2 * SE_SAMPLE > 0 > SE_MEAN + 2 * SE_POP, 'SE_exact no longer straddles the S2 edge'")

# ---- LEVEL_median on the levels N1 / N5 / N6 read ---------------------------------------------------------------------
t.span("# noise-free; block 12 (arm 0) and block 9 (arm 1) +2 900 us on every row, block 17",
       "# ---- the reported, never deciding d cpu_net_us",
       """# noise-free; block 12 (arm 0) and block 9 (arm 1) +2 900 us on every row, block 16 (arm 0) da_q_free 50 000, block 17
# (arm 1) da_q_noguard 50 000, block 21 (arm 1) da_queue_us 20 000: medians 31 000 / 30 850 / 1 080 / 1 080 / 1 080
# exactly (means: 31 026.4 / 30 876.4 / 1 524.7 / 1 524.7 / 1 251.6 - N6, N5 and N1 would miss); the two dt outliers
# sit in different pairs with opposite signs, so d mean dt stays -150.
case('LEVEL_median', run_eval(make('levmed', noise=0, row=both(
    setter(pick=lambda n, b, a, i: i is not None and b in (9, 12),
           edits={'main': {'dt_us': lambda n, b, a, i: 31000 - 150 * a + 2900}}),
    setter(pick=lambda n, b, a, i: i is not None and b == 16, edits={'x': {'da_q_free': 50000}}),
    setter(pick=lambda n, b, a, i: i is not None and b == 17, edits={'x': {'da_q_noguard': 50000}}),
    setter(pick=lambda n, b, a, i: i is not None and b == 21, edits={'draw': {'da_queue_us': 20000}})))), PENDING,
    check=lambda o: (o['levels']['arm0']['dt_us'] == 31000.0 and o['levels']['arm1']['dt_us'] == 30850.0
                     and o['levels']['arm0']['da_q_free'] == 1080.0 and o['levels']['arm1']['da_q_noguard'] == 1080.0
                     and o['levels']['arm1']['da_queue_us'] == 1080.0 and main_dt(o) == -150.0
                     and pred_values(o, N1=1080 / 1080, N5=1080.0, N6=1080.0, hits=['N1', 'N2', 'N5', 'N6', 'N7'])))

""")
t.keep("case('CPU_NET_spin', run_eval(make('cpunet', spin1=80, cpu_noise=0)), PENDING,")

# ---- predictions N1-N7 ---------------------------------------------------------------------------------------------
t.span("# ---- predictions K1-K6 (report only", "# ---- video checks, each alone",
       """# ---- predictions N1-N7 (report only: the verdict never reads them) ------------------------------------------------
# Every band exactly at, inside and just outside each edge, noise-free.  da_qcall is 1 000 in the edge fixtures, so the
# walker ratios land on the band literals exactly (900 / 1 000 is the double nearest 0.9, 1 120 / 1 000 the one nearest
# 1.12).  The good run (a REVERT) is inside N1, N2 and N5-N7; PRED_inside is the predicted run, inside all seven.
case('PRED_inside', run_eval(make('predin', d_dt=150, noise=0)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: (pred_values(o, N1=1080 / 1080, N2=1296 / 1080, N3=150.0, N4=150.0, N5=1080.0, N6=1080.0,
                                  N7=0.0, hits=list(PRED_BANDS)) and gain_exact(o, -150.0, 0.0)))
# on the lower edges: N1 0.90, N2 1.00, N3 0 (S2 fails alone), N5 800, N6 800, N7 -40 - all hit but N4
case('PRED_edges_lo', run_eval(make('prededgelo', d_dt=0, noise=0, qcall=1000, qq1=900, qq0=1000, ng1=800,
                                    qfree0=800, row=setter(pick=lambda n, b, a, i: a == 1,
                                                           edits={'draw': {'da_miss': 260}}))),
     KEEP_BAR, rules=['S2_dt_2se_excludes_0'],
     check=lambda o: pred_values(o, N1=900 / 1000, N2=1000 / 1000, N3=0.0, N4=0.0, N5=800.0, N6=800.0, N7=-40.0,
                                 hits=['N1', 'N2', 'N3', 'N5', 'N6', 'N7']))
# just below them: 0.89, 0.99, d -1 (a REVERT pending), 799, 799, -41 - all miss
case('PRED_misses_lo', run_eval(make('predmisslo', d_dt=-1, noise=0, qcall=1000, qq1=890, qq0=990, ng1=799,
                                     qfree0=799, row=setter(pick=lambda n, b, a, i: a == 1,
                                                            edits={'draw': {'da_miss': 259}}))),
     PENDING, check=lambda o: pred_values(o, N1=890 / 1000, N2=990 / 1000, N3=-1.0, N4=-1.0, N5=799.0, N6=799.0,
                                          N7=-41.0, hits=[]))
# on the upper edges: N1 1.12, N2 1.30, N3 +300, N5 1 400, N6 1 400, N7 +40 - all hit (N4 too)
case('PRED_edges_hi', run_eval(make('prededgehi', d_dt=300, noise=0, qcall=1000, qq1=1120, qq0=1300, ng1=1400,
                                    qfree0=1400, row=setter(pick=lambda n, b, a, i: a == 1,
                                                            edits={'draw': {'da_miss': 340}}))),
     KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, N1=1120 / 1000, N2=1300 / 1000, N3=300.0, N4=300.0, N5=1400.0, N6=1400.0,
                                 N7=40.0, hits=list(PRED_BANDS)))
# just above them: 1.13, 1.31, +301, 1 401, 1 401, +41 - all miss but N4
case('PRED_misses_hi', run_eval(make('predmisshi', d_dt=301, noise=0, qcall=1000, qq1=1130, qq0=1310, ng1=1401,
                                     qfree0=1401, row=setter(pick=lambda n, b, a, i: a == 1,
                                                             edits={'draw': {'da_miss': 341}}))),
     KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, N1=1130 / 1000, N2=1310 / 1000, N3=301.0, N4=301.0, N5=1401.0, N6=1401.0,
                                 N7=41.0, hits=['N4']))
# N4's only bound: d mean +100 hits, +99 misses (N3 hits both)
case('PRED_N4_edge', run_eval(make('predn4', d_dt=100, noise=0)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, N3=100.0, N4=100.0, hits=list(PRED_BANDS)))
case('PRED_N4_out', run_eval(make('predn4out', d_dt=99, noise=0)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, N3=99.0, N4=99.0, hits=['N1', 'N2', 'N3', 'N5', 'N6', 'N7']))

""")

# ---- video checks: the gate text names the candidate's two knobs; the frame floor's edge ------------------------------
t.rep("""case('V_frames', run_eval(good, *video(good, frames=2000, tag='fr')), KEEP_VID, vfail=['frames'])
""", """case('V_frames', run_eval(good, *video(good, frames=2000, tag='fr')), KEEP_VID, vfail=['frames'])
# the frame floor's edge: exactly 3 000 frames pass, 2 999 fail
case('V_frames_3000', run_eval(good, *video(good, frames=3000, tag='f3')), REVERT)
case('V_frames_2999', run_eval(good, *video(good, frames=2999, tag='f2')), KEEP_VID, vfail=['frames'])
""")
t.span("case('V_gate', run_eval(good, *video(good, gate='daslot=0', tag='gt'))", "case('V_pin',",
       """# the gate text: today's default (the arm-0 text) instead of the candidate, then each of the three names alone missing
case('V_gate', run_eval(good, *video(good, gate='daslot=1 daguard=1', tag='gt')), KEEP_VID,
     vfail=['daguard_0_in_gate_text'])
case('V_gate_daslot', run_eval(good, *video(good, gate='daguard=0', tag='gs')), KEEP_VID,
     vfail=['daguard_0_in_gate_text'])
case('V_gate_daguard', run_eval(good, *video(good, gate='daslot=0', tag='gc')), KEEP_VID,
     vfail=['daguard_0_in_gate_text'])
case('V_gate_dawalk', run_eval(good, *video(good, gates=gates_text.replace('dawalk=1', 'dawalk=0'), tag='gd')),
     KEEP_VID, vfail=['daguard_0_in_gate_text'])
""")
t.rep("case('V_missing', run_eval(good, str(good / 'no_such_vss111.json'),",
      "case('V_missing', run_eval(good, str(good / 'no_such_vnet112.json'),")

# ---- integrity: the schema's ten daslot / daguard counters, the recording path --------------------------------------
t.rep("# ... and the c8235c90 build's eight daslot counters, each alone",
      "# ... and the b47b58a9 build's ten daslot / daguard counters (session 111's eight, session 112's two), each alone")
t.rep("append=['Recording: C:/kyty/s111/rec_shp111.mp4 960x540']", "append=['Recording: C:/kyty/s112/rec_net112.mp4 960x540']")

# ---- controls: the area mirror's minimum block edge (after AREA) ----------------------------------------------------
t.rep("""case('SYNC', run_eval(make('sync', sync0=1, sync1=4)), KEEP_NA, fails={'control:SYNC_COMPILE'},
""", """

def relabel(k):
    \"\"\"row hook: rows 0..k-1 of block 8 (arm 0) and block 9 (arm 1) - outside every estimator window - report blk 998
    and 999.\"\"\"
    return setter(pick=lambda n, b, a, i: b in (8, 9) and i is not None and i < k,
                  edits={'main': {'blk': lambda n, b, a, i: 990 + b}})


# the area mirror's minimum block size (AREA_MIN_FLIPS 8): the relabelled rows form one more consecutive two-arm block
# pair (998 arm 0, 999 arm 1); with 8 flips each it counts (111 pairs, all matched) ...
case('AREA_min_flips', run_eval(make('amin8', row=relabel(8))), PENDING,
     check=lambda o: (o['area_verdict_mirror']['pairs'] == 111 and o['area_verdict_mirror']['matched'] == 111
                      and o['area_verdict_mirror']['valid'] is True))
# ... with 7 flips each it does not (110, as in the good run)
case('AREA_min_flips_below', run_eval(make('amin7', row=relabel(7))), PENDING,
     check=lambda o: (o['area_verdict_mirror']['pairs'] == 110 and o['area_verdict_mirror']['matched'] == 110
                      and o['area_verdict_mirror']['valid'] is True))
case('SYNC', run_eval(make('sync', sync0=1, sync1=4)), KEEP_NA, fails={'control:SYNC_COMPILE'},
""")

# ---- arming: SLOT_ARMED_ARM0, SLOT_DARK_ARM1, NOGUARD_ARMED_ARM1, NOGUARD_DARK_ARM0 and the level edges -------------
t.span("# SLOT_DARK_ARM0: arm-0 main-window rows with calls off m_mutex (K2 misses, value 5)\n",
       "# SLOT_NO_BAD: one knob-2 slot-key disagreement",
       """# SLOT_ARMED_ARM0: today's default arm queues under m_mutex (da_qcall still 1 080: the knob, not the call count; N6
# misses) ...
case('SLOT_ARMED0', run_eval(make('sarmed0', qfree0=0)), KEEP_NA, fails=ARMING, arming=['SLOT_ARMED_ARM0'],
     check=lambda o: o['levels']['arm0']['da_qcall'] == 1080.0 and o['levels']['arm0']['da_q_free'] == 0.0)
# ... on every third row only: level ~0.33 < 1 ...
case('SLOT_ARMED0_sparse', run_eval(make('sarmed0s', row=setter(
    pick=lambda n, b, a, i: a == 0, edits={'x': {'da_q_free': lambda n, b, a, i: 1 if n % 3 == 0 else 0}}))),
    KEEP_NA, fails=ARMING, arming=['SLOT_ARMED_ARM0'])
# ... only outside the main window (rows 0..9 of the arm-0 blocks): the level reads the main window only
case('SLOT_ARMED0_lag', run_eval(make('sarmed0lag', row=setter(
    pick=lambda n, b, a, i: a == 0 and i is not None,
    edits={'x': {'da_q_free': lambda n, b, a, i: 0 if i in MAIN else 1080}}))),
    KEEP_NA, fails=ARMING, arming=['SLOT_ARMED_ARM0'], check=lambda o: o['levels']['arm0']['da_q_free'] == 0.0)
# SLOT_DARK_ARM1: the candidate arm with calls off m_mutex on every main-window row (5 a flip) ...
case('SLOT_DARK1', run_eval(make('sdark1', qfree1=5)), KEEP_NA, fails=ARMING, arming=['SLOT_DARK_ARM1'],
     check=lambda o: o['arming']['slot_arm1_kept']['da_q_free'] == 5 * 80 * 110)
# ... on ONE main-window row of block 5 (arm 1), value 1: a kept total of 1 fails - no tolerance (the good run's 0
# passes) ...
case('SLOT_DARK1_one', run_eval(make('sdark1one', row=setter(pick=lambda n, b, a, i: b == 5 and i == 50,
                                                             edits={'x': {'da_q_free': 1}}))),
     KEEP_NA, fails=ARMING, arming=['SLOT_DARK_ARM1'],
     check=lambda o: o['arming']['slot_arm1_kept']['da_q_free'] == 1)
# ... but not rows 0..9 of an arm-1 block (the counters of the flips that straddle the arm change): pending
case('SLOT_DARK1_lag', run_eval(make('sdark1lag', row=setter(
    pick=lambda n, b, a, i: a == 1 and out_main(i), edits={'x': {'da_q_free': 400}}))), PENDING,
    check=lambda o: o['arming']['slot_arm1_kept']['da_q_free'] == 0 and o['levels']['arm1']['da_q_free'] == 0.0)
# NOGUARD_ARMED_ARM1: the candidate arm queues with the guards (da_qcall still 1 080; N5 misses) ...
case('NOGUARD_ARMED1', run_eval(make('ngarmed1', ng1=0)), KEEP_NA, fails=ARMING, arming=['NOGUARD_ARMED_ARM1'],
     check=lambda o: o['levels']['arm1']['da_qcall'] == 1080.0 and o['levels']['arm1']['da_q_noguard'] == 0.0)
# ... on every third row only: level ~0.33 < 1 ...
case('NOGUARD_ARMED1_sparse', run_eval(make('ngarmed1s', row=setter(
    pick=lambda n, b, a, i: a == 1, edits={'x': {'da_q_noguard': lambda n, b, a, i: 1 if n % 3 == 0 else 0}}))),
    KEEP_NA, fails=ARMING, arming=['NOGUARD_ARMED_ARM1'])
# ... only outside the main window (rows 0..9 of the arm-1 blocks): the level reads the main window only
case('NOGUARD_ARMED1_lag', run_eval(make('ngarmed1lag', row=setter(
    pick=lambda n, b, a, i: a == 1,
    edits={'x': {'da_q_noguard': lambda n, b, a, i: 0 if i in MAIN else 1080}}))),
    KEEP_NA, fails=ARMING, arming=['NOGUARD_ARMED_ARM1'], check=lambda o: o['levels']['arm1']['da_q_noguard'] == 0.0)
# NOGUARD_DARK_ARM0: today's arm skipping the guards on every main-window row (5 a flip) ...
case('NOGUARD_DARK0', run_eval(make('ngdark0', ng0=5)), KEEP_NA, fails=ARMING, arming=['NOGUARD_DARK_ARM0'],
     check=lambda o: o['arming']['noguard_arm0_kept']['da_q_noguard'] == 5 * 80 * 110)
# ... on ONE main-window row of block 4 (arm 0), value 1: a kept total of 1 fails - no tolerance ...
case('NOGUARD_DARK0_one', run_eval(make('ngdark0one', row=setter(pick=lambda n, b, a, i: b == 4 and i == 50,
                                                                 edits={'x': {'da_q_noguard': 1}}))),
     KEEP_NA, fails=ARMING, arming=['NOGUARD_DARK_ARM0'],
     check=lambda o: o['arming']['noguard_arm0_kept']['da_q_noguard'] == 1)
# ... but not rows 0..9 of an arm-0 block: pending
case('NOGUARD_DARK0_lag', run_eval(make('ngdark0lag', row=setter(
    pick=lambda n, b, a, i: a == 0 and out_main(i), edits={'x': {'da_q_noguard': 400}}))), PENDING,
    check=lambda o: (o['arming']['noguard_arm0_kept']['da_q_noguard'] == 0
                     and o['levels']['arm0']['da_q_noguard'] == 0.0))
# the level edges: arm-0 da_q_free 1, arm-1 da_q_noguard 1, cspfree_hit 1 in both arms - every arming check holds (N5
# and N6 miss)
case('ARMED_edge', run_eval(make('armededge', qfree0=1, ng1=1, hit0=1, hit1=1)), PENDING,
     check=lambda o: (o['levels']['arm0']['da_q_free'] == 1.0 and o['levels']['arm1']['da_q_noguard'] == 1.0
                      and o['arming']['cspfree_hit_levels'] == [1.0, 1.0]
                      and pred_values(o, N5=1.0, N6=1.0, hits=['N1', 'N2', 'N7'])))
""")
t.keep("case('SLOT_NO_BAD', run_eval(make('snobad', row=setter(pick=lambda n, b, a, i: n == 1750,")
t.keep("case('DEFAULTS_arm0', run_eval(make('defarm0', look0=0, hit0=0)), KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'],")
# the walk identity's tolerance (ID_TOL 1 %), before INSTRUMENTS_DARK
t.rep("""# INSTRUMENTS_DARK, every key: one kept row, arm 0 (block 4) for even keys, arm 1 (block 5) for odd ones
""", """# the walk identity's tolerance (1 %): kept skips 0.9 % above jobs + drops pass (both arms) ...
case('WALK_IDENT_edge_in', run_eval(make('widentin', row=setter(
    pick=lambda n, b, a, i: True, edits={'x': {'da_wjobs': 1000, 'da_wskip': 1009}}))), PENDING,
    check=lambda o: abs(o['arming']['skip_over_posts_rel'] - 0.009) < 1e-12)
# ... 1.1 % above fail (arm 1 alone)
case('WALK_IDENT_edge_out', run_eval(make('widentout', row=setter(
    pick=lambda n, b, a, i: a == 1, edits={'x': {'da_wjobs': 1000, 'da_wskip': 1011}}))),
    KEEP_NA, fails=ARMING, arming=['WALK_IDENTITY_ARM1'],
    check=lambda o: abs(o['arming']['skip_over_posts_rel'] - 0.011) < 1e-12)
# INSTRUMENTS_DARK, every key: one kept row, arm 0 (block 4) for even keys, arm 1 (block 5) for odd ones
""")

# ---- protocol: the attempt's hold tolerance edge --------------------------------------------------------------------
t.rep("""# meta hold_s 590 (not 600): DURATION compares with it and still holds (~627 s), only protocol fails
""", """# the attempt's hold tolerance (HOLD_S - 5 = 595 s): 595 passes, 594 fails
case('P_att_hold_edge', run_eval(variant(good, 'p_ahold595', meta_set(attempts=[dict(ATT, hold_s=595)]))), PENDING)
case('P_att_hold_out', run_eval(variant(good, 'p_ahold594', meta_set(attempts=[dict(ATT, hold_s=594)]))), KEEP_NA,
     fails={'protocol'}, errors=['hold_s 594 below 595'])
# meta hold_s 590 (not 600): DURATION compares with it and still holds (~627 s), only protocol fails
""")

# ---- main(): identity, refusals, tags ------------------------------------------------------------------------------
t.rep("fake_exe.write_bytes(b'not the c8235c90 build')", "fake_exe.write_bytes(b'not the b47b58a9 build')")
t.rep("'PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and size into shp111.py (only --draft runs '",
      "'PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and size into net112.py (only --draft runs '")
t.rep("# the generated scorer ships with PRED_SHA = None: it must refuse until the executor pins pred/03 (full message)",
      "# the generated scorer ships with PRED_SHA = None: it must refuse until the executor pins pred/02 (full message)")
t.rep("""# the tag pattern: shp111 with the optional b and _entry1 reaches evaluate() (no files under that tag here: INPUTS,
# protocol and IDENTITY fail, rc 1 - not the refusal's rc 2) ...
for t in ('shp111b', 'shp111_entry1', 'shp111b_entry1'):""",
      """# the tag pattern: net112 with the optional b and _entry1 reaches evaluate() (no files under that tag here: INPUTS,
# protocol and IDENTITY fail, rc 1 - not the refusal's rc 2) ...
for t in ('net112b', 'net112_entry1', 'net112b_entry1'):""")
t.rep("""# ... and every other tag is refused with the full message, the dropped session-110 tags and the video tag included
for t in ('shp112', 'shp110', 'shp110b', 'shp110_entry1', 'vss111', 'vsh110', 'shp111c', 'xshp111'):""",
      """# ... and every other tag is refused with the full message, session 111's tags and the video tags included
for t in ('net113', 'net111', 'shp111', 'shp111b', 'shp111_entry1', 'vnet112', 'vss111', 'net112c', 'xnet112'):""")

# ---- the report lines ----------------------------------------------------------------------------------------------
t.rep("""    if c['name'] in ('PENDING', 'S2_only', 'SE_exact', 'KEEP_edge', 'SEC_edge', 'EST_rows0_9', 'EST_rows10_59',
                     'EST_rows10_59_ship', 'LEVEL_median'):""",
      """    if c['name'] in ('PENDING', 'S2_only', 'S1_edge', 'S1_edge_in', 'S1_edge_out', 'SE_exact', 'KEEP_edge',
                     'SEC_edge', 'EST_rows0_9', 'EST_rows10_59', 'EST_rows10_59_rev', 'LEVEL_median'):""")
t.rep("""        print('   LEVEL case: dt arm0 %s arm1 %s, da_q_free arm1 %s, da_guard_busy arm1 %s'
              % ((lv.get('arm0') or {}).get('dt_us'), (lv.get('arm1') or {}).get('dt_us'),
                 (lv.get('arm1') or {}).get('da_q_free'), (lv.get('arm1') or {}).get('da_guard_busy')))""",
      """        print('   LEVEL case: dt arm0 %s arm1 %s, da_q_free arm0 %s, da_q_noguard arm1 %s, da_queue_us arm1 %s'
              % ((lv.get('arm0') or {}).get('dt_us'), (lv.get('arm1') or {}).get('dt_us'),
                 (lv.get('arm0') or {}).get('da_q_free'), (lv.get('arm1') or {}).get('da_q_noguard'),
                 (lv.get('arm1') or {}).get('da_queue_us')))""")

t.write('test_net112.py',
        stale=("'K1'", "'K6'", 'vss111_', 'daslot_1_in_gate_text', 'SLOT_DARK_ARM0', 'SLOT_ARMED_ARM1', 'S1_dt_le_-100',
               "TAG = 'shp111'", 'c8235c90', 's106_stage/shp111', 'SHIP_PENDING_VIDEO', 'slot_arm0_kept',
               "'PRED_SHA': None", 'EST_rows10_59_ship'),
        fresh=("TAG = 'net112'", 'NOGUARD_DARK0_one', 'SLOT_DARK1_one', 'P_att_hold_edge', 'AREA_min_flips_below',
               'WALK_IDENT_edge_out', 'V_frames_2999', 'PRED_N4_out', "'da_q_noguard': ng1 if arm else ng0",
               'def gain_exact(', "'SCHEDULE': '90+1800:dawalk=1 dawalklead=1 daslot=1 daguard=1|"))

# =====================================================================================================================
# mut_net112.py from mut_shp111.py
# =====================================================================================================================
m = Src('mut_shp111.py')
m.docstring('Session 111: mutation check of shp111.py against test_shp111.py.',
            '    python mut_shp111.py [<workers>]\n',
            '''Session 112: mutation check of net112.py against test_net112.py, derived from session 111's mut_shp111.py by
make_net112.py.  Each mutant disables or weakens ONE admission / decision term, verdict branch, prediction, schema
entry, marker, sealed constant, estimator window, threshold or refusal of main() (anchored replace, asserted to match
exactly once).  Included: every mutant of mut_shp111.py that still applies (ported: SLOT_DARK_ARM0 / SLOT_ARMED_ARM1
replaced by SLOT_ARMED_ARM0 / SLOT_DARK_ARM1, K1-K6 by N1-N7, the ship bar -100 by the revert bar 0, the texts
re-anchored on net112), the twelve shp111 mutants of the session-111 audit (audit111/newmut.py; SCHEMA_no_q_taking is
not repeated: it deletes the same schema entry as SCHEMA_no_da_q_taking), and the session-112 changes: NOGUARD_*, the
bar SHIP_US 0 -> -1 / +1, the video gate text, N1-N7 and their ratio, the two new schema counters, the quoted size, the
added claim, and one mutant per threshold-edge fixture (dark totals, arming levels, hold, area minimum flips, walk
identity, video frames).  Each mutant runs the full fixture suite in its own fixture directory
(C:/kyty/s106_stage/net112/fx_mut/w<k>, removed at the end); a mutant is KILLED when the suite does not print ALL OK.
The unmutated scorer runs first in the same harness and must print ALL OK.
    python mut_net112.py [<workers>]
''')
m.rep("""HERE = Path('C:/kyty/s106_stage/shp111')
SCORER = HERE / 'shp111.py'
TEST = HERE / 'test_shp111.py'
MUT = HERE / 'mutants'
FX = HERE / 'fx_mut'""", """HERE = Path('C:/kyty/s106_stage')
SCORER = HERE / 'net112.py'
TEST = HERE / 'test_net112.py'
MUT = HERE / 'net112' / 'mutants'
FX = HERE / 'net112' / 'fx_mut'""")
m.rep("# ==== ported from mut_shp110.py ====", "# ==== ported from mut_shp111.py (itself from mut_shp110.py) ====")
m.rep("""mutant('S1_off', "'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,", "'S1_dt_le_-100': True,")
mutant('S1_bar_-50', "dt['mean'] <= SHIP_US,", "dt['mean'] <= SHIP_US + 50,")""",
      """mutant('S1_off', "'S1_dt_le_0': dt['mean'] is not None and dt['mean'] <= SHIP_US,", "'S1_dt_le_0': True,")
mutant('S1_bar_+50', "dt['mean'] <= SHIP_US,", "dt['mean'] <= SHIP_US + 50,")""")
m.rep("""mutant('VIDEO_gate_daslot_off', "' dawalk=1 ' in gates and ' daslot=1 ' in gates,", "' dawalk=1 ' in gates,")
mutant('VIDEO_gate_dawalk_off', "' dawalk=1 ' in gates and ' daslot=1 ' in gates,", "' daslot=1 ' in gates,")
mutant('VIDEO_gate_is_cspfree', "' dawalk=1 ' in gates and ' daslot=1 ' in gates,",
       "' dawalk=1 ' in gates and ' cspfree=1 ' in gates,")""",
      """GATE = "' dawalk=1 ' in gates and ' daslot=0 ' in gates and ' daguard=0 ' in gates,"
mutant('VIDEO_gate_daslot_off', GATE, "' dawalk=1 ' in gates and ' daguard=0 ' in gates,")
mutant('VIDEO_gate_daguard_off', GATE, "' dawalk=1 ' in gates and ' daslot=0 ' in gates,")
mutant('VIDEO_gate_dawalk_off', GATE, "' daslot=0 ' in gates and ' daguard=0 ' in gates,")
mutant('VIDEO_gate_is_arm0', GATE, "' dawalk=1 ' in gates and ' daslot=1 ' in gates and ' daguard=1 ' in gates,")
mutant('VIDEO_gate_is_shp111', GATE, "' dawalk=1 ' in gates and ' daslot=1 ' in gates,")""")
m.rep("""mutant('SHIP_bar_-99', 'SHIP_US = -100.0', 'SHIP_US = -99.0')""",
      """mutant('SHIP_bar_-1', 'SHIP_US = 0.0', 'SHIP_US = -1.0')
mutant('SHIP_bar_+1', 'SHIP_US = 0.0', 'SHIP_US = 1.0')""")
m.keep("mutant('MAIN_lo_9', NL + 'KEEP_LO, KEEP_HI = 10, 90', NL + 'KEEP_LO, KEEP_HI = 9, 90')")
m.keep("mutant('SEC_swap_into_predictions', \"out['predictions'] = predictions(stats, lev, arm)\",")

# arming: the SLOT_DARK_ARM0 / SLOT_ARMED_ARM1 mutants -> SLOT_ARMED_ARM0 / SLOT_DARK_ARM1 and NOGUARD_*
m.span("# ---- arming: SLOT_* ----", "mutant('SLOT_NO_BAD_off',",
       """# ---- arming: SLOT_ARMED_ARM0 / SLOT_DARK_ARM1 (session 112: arm 0 is today's daslot=1, arm 1 the candidate) --------
SA0 = "checks['SLOT_ARMED_ARM0'] = bool((lev[0].get('da_q_free') or 0) >= 1)"
mutant('SLOT_ARMED_off', SA0, "checks['SLOT_ARMED_ARM0'] = True")
mutant('SLOT_ARMED_reads_qcall', SA0, "checks['SLOT_ARMED_ARM0'] = bool((lev[0].get('da_qcall') or 0) >= 1)")
mutant('SLOT_ARMED_gt1', SA0, "checks['SLOT_ARMED_ARM0'] = bool((lev[0].get('da_q_free') or 0) > 1)")
mutant('SLOT_ARMED_gt0', SA0, "checks['SLOT_ARMED_ARM0'] = bool((lev[0].get('da_q_free') or 0) > 0)")
mutant('SLOT_ARMED_arm1', SA0, "checks['SLOT_ARMED_ARM0'] = bool((lev[1].get('da_q_free') or 0) >= 1)")
mutant('SLOT_DARK_off', "checks['SLOT_DARK_ARM1'] = free1 == 0", "checks['SLOT_DARK_ARM1'] = True")
mutant('SLOT_DARK_tol5', "checks['SLOT_DARK_ARM1'] = free1 == 0",
       "checks['SLOT_DARK_ARM1'] = free1 is not None and free1 <= 5")          # audit111 survivor, ported to arm 1
mutant('SLOT_DARK_tol1', "checks['SLOT_DARK_ARM1'] = free1 == 0",
       "checks['SLOT_DARK_ARM1'] = free1 is not None and free1 <= 1")
mutant('SLOT_DARK_all_arm1_rows', "free1 = kept_total(rows, sel, arms, 1, 'da_q_free')",
       "free1 = sum(r.get('da_q_free', 0) for r in rows.values() if r.get('arm') == 1)")
mutant('SLOT_DARK_reads_arm0', "free1 = kept_total(rows, sel, arms, 1, 'da_q_free')",
       "free1 = kept_total(rows, sel, arms, 0, 'da_q_free')")
# ---- arming: NOGUARD_ARMED_ARM1 / NOGUARD_DARK_ARM0 ------------------------------------------------------------------
NA1 = "checks['NOGUARD_ARMED_ARM1'] = bool((lev[1].get('da_q_noguard') or 0) >= 1)"
mutant('NOGUARD_ARMED_off', NA1, "checks['NOGUARD_ARMED_ARM1'] = True")
mutant('NOGUARD_ARMED_reads_qcall', NA1, "checks['NOGUARD_ARMED_ARM1'] = bool((lev[1].get('da_qcall') or 0) >= 1)")
mutant('NOGUARD_ARMED_gt1', NA1, "checks['NOGUARD_ARMED_ARM1'] = bool((lev[1].get('da_q_noguard') or 0) > 1)")
mutant('NOGUARD_ARMED_gt0', NA1, "checks['NOGUARD_ARMED_ARM1'] = bool((lev[1].get('da_q_noguard') or 0) > 0)")
mutant('NOGUARD_ARMED_arm0', NA1, "checks['NOGUARD_ARMED_ARM1'] = bool((lev[0].get('da_q_noguard') or 0) >= 1)")
mutant('NOGUARD_DARK_off', "checks['NOGUARD_DARK_ARM0'] = noguard0 == 0", "checks['NOGUARD_DARK_ARM0'] = True")
mutant('NOGUARD_DARK_tol5', "checks['NOGUARD_DARK_ARM0'] = noguard0 == 0",
       "checks['NOGUARD_DARK_ARM0'] = noguard0 is not None and noguard0 <= 5")
mutant('NOGUARD_DARK_tol1', "checks['NOGUARD_DARK_ARM0'] = noguard0 == 0",
       "checks['NOGUARD_DARK_ARM0'] = noguard0 is not None and noguard0 <= 1")
mutant('NOGUARD_DARK_all_arm0_rows', "noguard0 = kept_total(rows, sel, arms, 0, 'da_q_noguard')",
       "noguard0 = sum(r.get('da_q_noguard', 0) for r in rows.values() if r.get('arm') == 0)")
mutant('NOGUARD_DARK_reads_arm1', "noguard0 = kept_total(rows, sel, arms, 0, 'da_q_noguard')",
       "noguard0 = kept_total(rows, sel, arms, 1, 'da_q_noguard')")
""")
m.keep("mutant('DEFAULTS_off',")
m.rep("""# ---- the c8235c90 schema: each new counter out of it, one moved to another line -------------------------------------------
for key in ('da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_slot_bad', 'da_q_free',
            'da_chk_ok', 'da_chk_bad'):
    mutant('SCHEMA_no_%s' % key, "'%s': 'x'," % key, "")
mutant('SCHEMA_q_free_on_draw', "'da_q_free': 'x',", "'da_q_free': 'draw',")""",
      """# ---- the b47b58a9 schema: each daslot / daguard counter out of it, two moved to another line -------------------------------
for key in ('da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_slot_bad', 'da_q_free',
            'da_chk_ok', 'da_chk_bad', 'da_q_noguard', 'da_guard_yield'):
    mutant('SCHEMA_no_%s' % key, "'%s': 'x'," % key, "")
mutant('SCHEMA_q_free_on_draw', "'da_q_free': 'x',", "'da_q_free': 'draw',")
mutant('SCHEMA_noguard_on_draw', "'da_q_noguard': 'x',", "'da_q_noguard': 'draw',")""")
m.span("# ---- the sealed constants ----", "# ---- tags and refusal / verdict texts ----",
       """# ---- the sealed constants ---------------------------------------------------------------------------------------------
mutant('CONST_root_s111', "PRODUCTION_ROOT = 'C:/kyty/s112'", "PRODUCTION_ROOT = 'C:/kyty/s111'")
mutant('CONST_pred_shp111', "PRED = 'C:/kyty/s112/pred/02_net112.md'", "PRED = 'C:/kyty/s111/pred/03_shp111.md'")
# a half-filled seal (CONSTANTS: both None, or a sha256 and a size)
mutant('CONST_pred_sha_prefilled', "PRED_SHA = None          #", "PRED_SHA = '0' * 64     #")
mutant('CONST_pred_bytes_prefilled', "PRED_BYTES = None        #", "PRED_BYTES = 1           #")
mutant('CONST_binary_c8235c90', "BINARY_SHA = 'b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7'",
       "BINARY_SHA = 'c8235c902e08d00782d0cff23528361d194a501ad1899344ca8302c742372a86'")
mutant('CONST_gates_s111', "GATES_FILE = 'C:/kyty/s112/gates_base.txt'", "GATES_FILE = 'C:/kyty/s111/gates_base.txt'")
ARMS_NOW = "ARMS = ('dawalk=1 dawalklead=1 daslot=1 daguard=1', 'dawalk=1 dawalklead=1 daslot=0 daguard=0')"
mutant('CONST_arms_swapped', ARMS_NOW,
       "ARMS = ('dawalk=1 dawalklead=1 daslot=0 daguard=0', 'dawalk=1 dawalklead=1 daslot=1 daguard=1')")
mutant('CONST_arms_shp111', ARMS_NOW, "ARMS = ('dawalk=1 dawalklead=1 daslot=0', 'dawalk=1 dawalklead=1 daslot=1')")
mutant('CONST_arms_no_daguard', ARMS_NOW,
       "ARMS = ('dawalk=1 dawalklead=1 daslot=1', 'dawalk=1 dawalklead=1 daslot=0')")
mutant('CONST_schedule_no_start', "SCHEDULE = '90+1800:%s|%s' % ARMS", "SCHEDULE = '90:%s|%s' % ARMS")
""")
m.span("# ---- tags and refusal / verdict texts ----", "# ---- the ship bar's edge ----",
       """# ---- tags and refusal / verdict texts ---------------------------------------------------------------------------------
TAG_NOW = "TAG_RE = r'net112b?(?:_entry1)?'"
mutant('TAG_accepts_shp111', TAG_NOW, "TAG_RE = r'(?:net112|shp111)b?(?:_entry1)?'")
mutant('TAG_accepts_vnet112', TAG_NOW, "TAG_RE = r'v?net112b?(?:_entry1)?'")
mutant('TAG_no_b', TAG_NOW, "TAG_RE = r'net112(?:_entry1)?'")
mutant('TAG_no_entry1', TAG_NOW, "TAG_RE = r'net112b?'")
mutant('TAG_search', "        if not re.fullmatch(TAG_RE, o.tag):", "        if not re.search(TAG_RE, o.tag):")
mutant('TAG_msg_old', "(net112, net112b, optional _entry1)", "(shp111, shp111b, optional _entry1)")
mutant('GEOM_msg_old', "'--period/--start/--first/--keep/--secondary are --draft only'",
       "'--period/--start/--first/--keep are --draft only'")
mutant('SEAL_msg_old', "size into net112.py (only --draft", "size into shp111.py (only --draft")
mutant('PENDING_text_old', "nothing changes until vnet112 is read", "nothing ships until vss111 is read")
mutant('PENDING_name_old', "'REVERT_PENDING_VIDEO (", "'SHIP_PENDING_VIDEO (")
mutant('VERDICT_na_old', "'KEEP daslot=1 (run not admitted)'", "'KEEP daslot=0 (run not admitted)'")
mutant('VERDICT_bar_old', "'KEEP daslot=1 (revert rule S1-S2 on mean dt not met)'",
       "'KEEP daslot=0 (ship rule S1-S2 on mean dt not met)'")
mutant('VERDICT_revert_old', "'REVERT to daslot=0 daguard=0 as the new default", "'SHIP daslot=1 as the new default")
mutant('VERDICT_video_old', "'KEEP daslot=1 (video pass failed)'", "'KEEP daslot=0 (video pass failed)'")
mutant('SCORER_name_old', "out = {'scorer': 'net112.py',", "out = {'scorer': 'shp111.py',")
mutant('SUMMARY_name_old', "lines = ['net112.py %s status=%s seal=%s'", "lines = ['shp111.py %s status=%s seal=%s'")
""")
m.keep("""mutant('S1_strict', "dt['mean'] <= SHIP_US,", "dt['mean'] < SHIP_US,")""")
m.span("# ---- predictions K1-K6 ----", "MUT.mkdir(exist_ok=True)",
       """# ---- predictions N1-N7 --------------------------------------------------------------------------------------------------
N1 = "ratio(lev[1].get('da_queue_us'), lev[1].get('da_qcall')), 0.90, 1.12)"
N2 = "ratio(lev[0].get('da_queue_us'), lev[0].get('da_qcall')), 1.00, 1.30)"
N3 = "stats['dt_us']['mean'], 0, 300)"
N4 = "stats['dt_us']['mean'], 100, None)"
N5 = "lev[1].get('da_q_noguard'), 800, 1400)"
N6 = "lev[0].get('da_q_free'), 800, 1400)"
N7 = "stats['da_miss']['mean'], -40, 40)"
mutant('PRED_N1_named_K1', "add('N1',", "add('K1',")
mutant('PRED_N1_arm0', N1, "ratio(lev[0].get('da_queue_us'), lev[0].get('da_qcall')), 0.90, 1.12)")
mutant('PRED_N1_reads_take', N1, "ratio(lev[1].get('da_take_us'), lev[1].get('da_qcall')), 0.90, 1.12)")
mutant('PRED_N1_lo_0.89', N1, N1.replace('0.90, 1.12', '0.89, 1.12'))
mutant('PRED_N1_lo_0.91', N1, N1.replace('0.90, 1.12', '0.91, 1.12'))
mutant('PRED_N1_hi_1.11', N1, N1.replace('0.90, 1.12', '0.90, 1.11'))
mutant('PRED_N1_hi_1.13', N1, N1.replace('0.90, 1.12', '0.90, 1.13'))
mutant('PRED_N2_arm1', N2, "ratio(lev[1].get('da_queue_us'), lev[1].get('da_qcall')), 1.00, 1.30)")
mutant('PRED_N2_lo_0.99', N2, N2.replace('1.00, 1.30', '0.99, 1.30'))
mutant('PRED_N2_lo_1.01', N2, N2.replace('1.00, 1.30', '1.01, 1.30'))
mutant('PRED_N2_hi_1.29', N2, N2.replace('1.00, 1.30', '1.00, 1.29'))
mutant('PRED_N2_hi_1.31', N2, N2.replace('1.00, 1.30', '1.00, 1.31'))
mutant('PRED_N3_lo_-1', N3, "stats['dt_us']['mean'], -1, 300)")
mutant('PRED_N3_lo_1', N3, "stats['dt_us']['mean'], 1, 300)")
mutant('PRED_N3_hi_299', N3, "stats['dt_us']['mean'], 0, 299)")
mutant('PRED_N3_hi_301', N3, "stats['dt_us']['mean'], 0, 301)")
mutant('PRED_N4_lo_99', N4, "stats['dt_us']['mean'], 99, None)")
mutant('PRED_N4_lo_101', N4, "stats['dt_us']['mean'], 101, None)")
mutant('PRED_N4_bounded', N4, "stats['dt_us']['mean'], 100, 300)")
mutant('PRED_N4_sign', N4, "-stats['dt_us']['mean'], 100, None)")
mutant('PRED_N5_arm0', N5, "lev[0].get('da_q_noguard'), 800, 1400)")
mutant('PRED_N5_reads_free', N5, "lev[1].get('da_q_free'), 800, 1400)")
mutant('PRED_N5_lo_799', N5, "lev[1].get('da_q_noguard'), 799, 1400)")
mutant('PRED_N5_lo_801', N5, "lev[1].get('da_q_noguard'), 801, 1400)")
mutant('PRED_N5_hi_1399', N5, "lev[1].get('da_q_noguard'), 800, 1399)")
mutant('PRED_N5_hi_1401', N5, "lev[1].get('da_q_noguard'), 800, 1401)")
mutant('PRED_N6_arm1', N6, "lev[1].get('da_q_free'), 800, 1400)")
mutant('PRED_N6_reads_noguard', N6, "lev[0].get('da_q_noguard'), 800, 1400)")
mutant('PRED_N6_lo_799', N6, "lev[0].get('da_q_free'), 799, 1400)")
mutant('PRED_N6_lo_801', N6, "lev[0].get('da_q_free'), 801, 1400)")
mutant('PRED_N6_hi_1399', N6, "lev[0].get('da_q_free'), 800, 1399)")
mutant('PRED_N6_hi_1401', N6, "lev[0].get('da_q_free'), 800, 1401)")
mutant('PRED_N7_reads_late', N7, "stats['da_late']['mean'], -40, 40)")
mutant('PRED_N7_lo_-41', N7, "stats['da_miss']['mean'], -41, 40)")
mutant('PRED_N7_lo_-39', N7, "stats['da_miss']['mean'], -39, 40)")
mutant('PRED_N7_hi_39', N7, "stats['da_miss']['mean'], -40, 39)")
mutant('PRED_N7_hi_41', N7, "stats['da_miss']['mean'], -40, 41)")
mutant('PRED_ratio_inverted', "    return a / b" + NL, "    return b / a" + NL)
mutant('PRED_hit_open_lower', "return v is not None and (lo is None or v >= lo)", "return v is not None and (lo is None or v > lo)")
mutant('PRED_hit_open_upper', "and (hi is None or v <= hi)", "and (hi is None or v < hi)")

# ==== session 112 =====================================================================================================
# ---- the quoted size (report only) and the added claim ------------------------------------------------------------------
mutant('GAIN_sign', "    mean = -dt['mean'] if dt['mean'] is not None else None",
       "    mean = dt['mean'] if dt['mean'] is not None else None")
mutant('GAIN_1se', "'two_se': 2 * dt['se'] if dt['se'] is not None else None",
       "'two_se': 1 * dt['se'] if dt['se'] is not None else None")
mutant('GAIN_secondary', "    out['reported']['s111_gain_vs_pre_session'] = s111_gain(dt)",
       "    out['reported']['s111_gain_vs_pre_session'] = s111_gain(out['secondary']['pair_stats']['dt_us'])")
mutant('GAIN_summary_dropped', "    if gain:" + NL, "    if False:" + NL)
mutant('GAIN_label', "'estimator; negative: daslot=1 faster)')", "'estimator)')")
mutant('CLAIM_dropped', "; a gain against a different build", "")
# ---- the session-111 audit's shp111 mutants (audit111/newmut.py) --------------------------------------------------------
mutant('S2_le0', "and dt['mean'] + 2 * dt['se'] < 0)", "and dt['mean'] + 2 * dt['se'] <= 0)")
mutant('FATAL_no_unhandled', "b'Unhandled exception:', ", "")
mutant('FATAL_no_devicelost', "b'ErrorDeviceLost', ", "")
mutant('FATAL_no_terminate', "b'--- std::terminate ---', ", "")
mutant('BANDS_gpu_wide', "'gpu_busy_us': (10000.0, 16000.0)}", "'gpu_busy_us': (1000.0, 160000.0)}")
mutant('HOLD_tol_50', "if (a.get('hold_s') or 0) < HOLD_S - 5:", "if (a.get('hold_s') or 0) < HOLD_S - 50:")
mutant('AREA_min_flips_0', "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8",
       "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 0")
mutant('ID_TOL_10x', "ID_TOL = 0.01", "ID_TOL = 0.1")
mutant('VIDEO_frames_strict', "'frames': frames is not None and frames >= VIDEO_MIN_FRAMES,",
       "'frames': frames is not None and frames > VIDEO_MIN_FRAMES,")
mutant('DROPS_loose', "checks['WALK_DROPS_ARM%d' % a] = bool(po) and dr is not None and dr / po <= DROP_MAX",
       "checks['WALK_DROPS_ARM%d' % a] = bool(po) and dr is not None and dr / po <= 1.0")
# (SLOT_DARK_tol5 is above, ported to SLOT_DARK_ARM1; SCHEMA_no_q_taking = SCHEMA_no_da_q_taking, not repeated)
# ---- the other side of each threshold-edge fixture ----------------------------------------------------------------------
mutant('HOLD_tol_4', "if (a.get('hold_s') or 0) < HOLD_S - 5:", "if (a.get('hold_s') or 0) < HOLD_S - 4:")
mutant('HOLD_le', "if (a.get('hold_s') or 0) < HOLD_S - 5:", "if (a.get('hold_s') or 0) <= HOLD_S - 5:")
mutant('AREA_min_flips_9', "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8",
       "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 9")
mutant('AREA_min_flips_le', "if a0['n'] < min_flips or a1['n'] < min_flips:",
       "if a0['n'] <= min_flips or a1['n'] <= min_flips:")
mutant('ID_TOL_half', "ID_TOL = 0.01", "ID_TOL = 0.005")
mutant('VIDEO_frames_3001', 'VIDEO_MIN_FRAMES = 3000', 'VIDEO_MIN_FRAMES = 3001')

""")
m.rep("MUT.mkdir(exist_ok=True)", "MUT.mkdir(parents=True, exist_ok=True)")
m.rep("        path = MUT / ('shp111_%s.py' % name)", "        path = MUT / ('net112_%s.py' % name)")
m.write('mut_net112.py',
        stale=('s106_stage/shp111', "'shp111_%s.py'", 'S1_dt_le_-100', 'SHIP_US = -100.0', "add('K2'", 'SLOT_DARK_ARM0',
               'SLOT_ARMED_ARM1', 'daslot_1_in_gate_text', "SCORER = HERE / 'shp111.py'"),
        fresh=("SCORER = HERE / 'net112.py'", "TEST = HERE / 'test_net112.py'", "'net112_%s.py'", 'NOGUARD_DARK_tol1',
               'SHIP_bar_+1', 'PRED_N7_hi_41', 'GAIN_sign', 'HOLD_tol_4', 'VIDEO_frames_3001'))
