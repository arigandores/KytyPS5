"""Session 114, ROADMAP s0.1 "СЕССИЯ 114 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 5: the ABBA scorer draft ttl114 (knob titleasync,
build 916f6489) derived from session 113's SEALED shn113 files by WHOLE-LINE anchored replacements (each anchor
asserted to end with a newline, to start at a line start and to occur exactly once; the inputs pinned by sha256).
Inputs, read only: C:/kyty/s113/{shn113.py,test_shn113.py,mut_shn113.py}.  Outputs: C:/kyty/s114/ttl114_draft/
{ttl114.py,test_ttl114.py,mut_ttl114.py}.  Byte-reproducible (LF, UTF-8).

Changes to the scorer: the docstring; PRODUCTION_ROOT C:/kyty/s114, PRED pred/02_ttl114.md, PRED_SHA / PRED_BYTES None
(draft), BINARY_SHA 916f6489..., GATES_FILE C:/kyty/s114/gates_base.txt (same bytes, GATES_SHA kept); ARMS
titleasync=0|1; TAG_RE ttl114b?(?:_entry1)?; the rule S1 d mean dt_us <= SHIP_US = +50 and S2 d mean + 2SE <= S2_US =
+200 (rules S1_dt_le_+50, S2_dt_2se_le_+200; before: -100 and < 0); SIZE_LABEL; REGIME_OLD_SCAN / NARROW_SCAN_MAX out,
TITLE_WALL_MAX_NS = 20000 in; the FrameTrace-x schema + pres_title_ns, pres_title_n, flip_rsv_wait_ns,
flip_rsv_wait_n, flip_hold_ns, flip_hold_n, mt_age_ns, mt_n after gw_idle_prio; ENV_EXPECTED without
KYTY_BUFFER_GC_TRIGGER_SHIFT_MB; PAIR_KEYS + flip_rsv_wait_ns; arming: REGIME_OLD_ARM0, NARROW_ARMED_ARM1,
NARROW_DARK_ARM0, NARROW_SCAN_ARM1, NO_CHECK, NO_XTHR out, TITLE_COUNTED and TITLE_ARMED in (new helper
title_wall_ns()); the video check titleasync_1_in_gate_text instead of bdanarrow_1_in_gate_text, the `shifted` check
out; the reported levels (title / reserve wait / hold / main-task instead of the BDA ones) and d flip_rsv_wait_ns;
predictions P1-P7 of item 5; the verdict texts (titleasync, vtt114, ctl114); must_not_be_claimed; the summary lines;
the names in the messages.  The fixtures and the mutants follow (see their docstrings).

    python C:/kyty/s114/ttl114_draft/make_ttl114.py
"""
import hashlib
from pathlib import Path

SRC = Path('C:/kyty/s113')
OUT = Path('C:/kyty/s114/ttl114_draft')
PINS = {'shn113.py': 'c5a582bed08483ca1d0bcb9d6808ed642910eacb23e7535a63b526cc64ee4138',
        'test_shn113.py': 'f7c9ca5378d3eca64f1134b51d12e9e70eccd38725cd34e9df550d37e3329743',
        'mut_shn113.py': 'bc0b66a825d89e59cd1b0e042300260d809d08c7b66c0dfe087551e34349a5ec'}
NAMES = {'shn113.py': 'ttl114.py', 'test_shn113.py': 'test_ttl114.py', 'mut_shn113.py': 'mut_ttl114.py'}
NEW_SHA = '916f64898a5a31c697ad0d823f0795850acc160cf56271b566e8ae330c7c3b2c'
OLD_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'
OLD_LABEL = 'bdanarrow=1 against bdanarrow=0 of build 1678d3f4, forced OLD (GC trigger -1024 MiB), main estimator'
NEW_LABEL = 'titleasync=1 against titleasync=0 of build 916f6489, main estimator'


def dash(text, n):
    """a comment header: `text` followed by exactly n dashes (the sealed headers' dash runs differ) and a newline"""
    return text + '-' * n + '\n'


def head(text):
    """a new comment header, padded with dashes to 119 characters"""
    return dash(text, 119 - len(text))


def load(name):
    s = (SRC / name).read_bytes().decode('utf-8').replace('\r\n', '\n')
    assert hashlib.sha256(s.encode('utf-8')).hexdigest().startswith(PINS[name]), name
    return s


def derive(src, pairs, forbidden=()):
    s = load(src)
    for a, b in pairs:
        assert a.endswith('\n') and b.endswith('\n'), (src, 'not whole lines', a[:80])
        assert s.startswith(a) or ('\n' + a) in s, (src, 'anchor not at a line start', a[:80])
        assert s.count(a) == 1, (src, a[:80], s.count(a))
        s = s.replace(a, b)
    for word in forbidden:
        assert word not in s, (src, 'left over', word)
    compile(s, NAMES[src], 'exec')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / NAMES[src]).write_bytes(s.encode('utf-8'))
    print(NAMES[src], hashlib.sha256(s.encode('utf-8')).hexdigest(), len(s.encode('utf-8')))


# =====================================================================================================================
# the scorer
# =====================================================================================================================
derive('shn113.py', [
    (r'''"""Session 113, the ABBA `shn113`: knob `bdanarrow` (KYTY_BDA_NARROW_STAMPS) - a buffer registration marks only its own
BDA region stamps stale (1) instead of invalidating every region stamp (0, today: in the OLD regime, a start state of
most runs in which the buffer GC evicts and re-creates buffers ~1.2 times a frame, PrepareBda re-walks ~1 016 extra
4-MiB regions a frame).  Arm 0 = today `dawalk=1 dawalklead=1 bdanarrow=0`; arm 1 = the candidate `dawalk=1
dawalklead=1 bdanarrow=1`.  Shipping configuration otherwise (compute precache on; knobs cspfree=1, daslot=1 and
daguard=1 by default in BOTH arms), sealed to pred/02_shn113.md.  Derived from session 112's net112.py (copied, not
imported; make_shn113.py; re-pinned by make_shn113b.py to the build 1678d3f4 and a forced OLD regime,
KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024 in both arms and the video), whose FrameTrace-x rows add bda_ginv_reg,
bda_ginv_map, bda_rinv, (then bda_nrace, prio_unsub, prio_stall, gw_idle_prio after bgc_evict: information)
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
"""
''',
     r'''"""Session 114, the ABBA `ttl114`: knob `titleasync` (KYTY_TITLE_ASYNC) - once the SDL main loop runs,
WindowContext::UpdateTitle on the present thread posts the window title to the SDL main thread without waiting (1)
instead of waiting for it on every present inside VideoOutConfig::mutex (0, today).  Arm 0 = today `dawalk=1
dawalklead=1 titleasync=0`; arm 1 = the candidate `dawalk=1 dawalklead=1 titleasync=1`.  Shipping configuration
otherwise (compute precache on; knobs cspfree=1, daslot=1 and daguard=1 by default in BOTH arms), build 916f6489, no
GC trigger shift, sealed to pred/02_ttl114.md.  Derived from session 113's sealed shn113.py by make_ttl114.py
(whole-line anchored replacements; copied, not imported), whose FrameTrace-x rows add, after gw_idle_prio,
pres_title_ns and pres_title_n (the wall of UpdateTitle on the present thread including its wait, and its calls;
counted only after the SDL main loop started), flip_rsv_wait_ns and flip_rsv_wait_n (blocking waits of GuestGpu for
VideoOutConfig::mutex in ReserveFlipRequest after a failed TryLock), flip_hold_ns and flip_hold_n (the hold of that
mutex in FlipQueue::Flip) and mt_age_ns and mt_n (the queue-to-run age of the SDL main thread's tasks) - raw ns and
counts a flip, all in the schema; predictions P1-P7, report only, each printed with HIT / MISS.

    python C:/kyty/s114/ttl114.py ttl114 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s114/ttl114.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Estimator (as in shn113.py; the executor's decision after session 110, ROADMAP s0.1 item 1): the MAIN estimator is
rows 10..89 of each 90-frame block (KEEP_LO, KEEP_HI = 10, 90).  The rule S1/S2, the pair statistics, BANDS,
WORK_SPLIT, AREA_SELECTED, the arm levels, the arming totals, the quoted size and the predictions read it.  The
session-110 window, rows 60..88 (SECONDARY_LO, SECONDARY_HI = 60, 89), is computed with its own selection and printed
as `secondary` (pair statistics and the S1/S2 values it would give); no admission or decision term reads it.  Pairing:
whole ABBA quartets, the others excluded as edge blocks.

Rule (ROADMAP s0.1, the session-114 records, items 2 and 5; a correctness fix, so the bar is "not slower"): d = arm 1
- arm 0 (candidate minus today).  SHIP titleasync=1 as the new default only if the run is ADMITTED - including
SYNC_COMPILE: over all rows from frame 2100, sum cs_sync_new of arm 1 <= that of arm 0 + 2 - and S1 d mean dt_us (main
estimator) <= SHIP_US = +50 and S2 d mean + 2SE <= S2_US = +200 (a guard against a noisy run hiding a slowdown), and
the video pass vtt114 (gate file gates_title1.txt = gates_base.txt + titleasync=1, pinned, >= 3000 frames, 0
one-frame glitches) reads PASS; otherwise KEEP titleasync=0.  The control ctl114 (pred/01) must read PASS as well:
its own scorer reads it, this one does not.  Whenever a pair exists, the quoted size - d mean dt_us (arm 1 - arm 0)
with its 2SE on the main estimator, labelled SIZE_LABEL - is reported (out['reported']['quoted_size'] and the
summary); it decides nothing.  Arming (under control ARMING): the walk checks (unchanged); TITLE_COUNTED (the
pres_title_n level >= 1 in both arms: UpdateTitle ran on the present thread after the SDL main loop started);
TITLE_ARMED (the arm-1 per-call wall level(pres_title_ns) / level(pres_title_n) <= TITLE_WALL_MAX_NS = 20 000 ns and
strictly below arm 0's per-call wall; a missing level fails); DEFAULTS_ON (cspfree_hit and da_q_free levels >= 1 in
both arms, sum cspfree_bad = 0 and sum da_slot_bad = 0 over all rows); INSTRUMENTS_DARK.  d cpu_net_us is reported,
never deciding: no admission or decision term reads it (derived(), block_means(), pair stats and the summary only).
"""
'''),
    (r'''PRODUCTION_ROOT = 'C:/kyty/s113'
PRED = 'C:/kyty/s113/pred/02_shn113.md'
PRED_SHA = '75f34c692954ab127f78a923831566224cc3b17b7f4c99d2a10a15281356d271'   # pred/02_shn113.md sealed
PRED_BYTES = 5452        # pred/02_shn113.md sealed
BINARY_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'
''',
     r'''PRODUCTION_ROOT = 'C:/kyty/s114'
PRED = 'C:/kyty/s114/pred/02_ttl114.md'
PRED_SHA = None          # filled by the executor when pred/02 is sealed
PRED_BYTES = None        # filled by the executor when pred/02 is sealed
BINARY_SHA = '916f64898a5a31c697ad0d823f0795850acc160cf56271b566e8ae330c7c3b2c'
'''),
    ("GATES_FILE = 'C:/kyty/s113/gates_base.txt'\n", "GATES_FILE = 'C:/kyty/s114/gates_base.txt'\n"),
    ("ARMS = ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=1')\n",
     "ARMS = ('dawalk=1 dawalklead=1 titleasync=0', 'dawalk=1 dawalklead=1 titleasync=1')\n"),
    ("TAG_RE = r'shn113b?(?:_entry1)?'\n", "TAG_RE = r'ttl114b?(?:_entry1)?'\n"),
    (r'''SHIP_US = -100.0          # on d mean dt_us = arm 1 - arm 0 (ROADMAP, decision after session 104; s113 item 3)
SIZE_LABEL = 'bdanarrow=1 against bdanarrow=0 of build 1678d3f4, forced OLD (GC trigger -1024 MiB), main estimator'
REGIME_OLD_SCAN = 500     # arm-0 level of bda_scan at or above it: the run is in the OLD regime (s113 item 3)
NARROW_SCAN_MAX = 200     # arm-1 level of bda_scan at or below it: the narrow stamps took (s113 item 3)
''',
     r'''SHIP_US = 50.0            # S1 on d mean dt_us = arm 1 - arm 0: not slower (s114 items 2 and 5, a correctness fix)
S2_US = 200.0             # S2 on d mean dt_us + 2SE: the guard against a noisy run hiding a slowdown (s114 item 5)
SIZE_LABEL = 'titleasync=1 against titleasync=0 of build 916f6489, main estimator'
TITLE_WALL_MAX_NS = 20000  # the arm-1 per-call wall of UpdateTitle at or below it, ns a call (s114 item 5)
'''),
    ("    'bda_nxthr': 'x', 'bgc_evict': 'x', 'bda_nrace': 'x', 'prio_unsub': 'x', 'prio_stall': 'x', 'gw_idle_prio': 'x',\n",
     "    'bda_nxthr': 'x', 'bgc_evict': 'x', 'bda_nrace': 'x', 'prio_unsub': 'x', 'prio_stall': 'x', 'gw_idle_prio': 'x',\n"
     "    'pres_title_ns': 'x', 'pres_title_n': 'x', 'flip_rsv_wait_ns': 'x', 'flip_rsv_wait_n': 'x', 'flip_hold_ns': 'x',\n"
     "    'flip_hold_n': 'x', 'mt_age_ns': 'x', 'mt_n': 'x',\n"),
    ("                'KYTY_GPU_MARKERS': '0', 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '1024'}\n",
     "                'KYTY_GPU_MARKERS': '0'}\n"),
    ("             'da_walks', 'da_qcall')\n", "             'da_walks', 'da_qcall', 'flip_rsv_wait_ns')\n"),
    ("                        'size into shn113.py (only --draft runs without a seal)' % path)\n",
     "                        'size into ttl114.py (only --draft runs without a seal)' % path)\n"),
    (r'''def arming(rows, sel, arms, lev):
    """pred/02 (the lead105 walk arming plus REGIME_OLD_ARM0, NARROW_ARMED_ARM1, NARROW_DARK_ARM0, NARROW_SCAN_ARM1,
    NO_CHECK, NO_XTHR and DEFAULTS_ON)."""
''',
     r'''def title_wall_ns(level):
    """The per-call wall of UpdateTitle on the present thread in one arm, ns a call: level(pres_title_ns) /
    level(pres_title_n); None when either level is missing or the call level is not positive."""
    ns, calls = level.get('pres_title_ns'), level.get('pres_title_n')
    if ns is None or calls is None or calls <= 0:
        return None
    return ns / calls


def arming(rows, sel, arms, lev):
    """pred/02 (the lead105 walk arming plus TITLE_COUNTED, TITLE_ARMED and DEFAULTS_ON)."""
'''),
    (r'''    # Session 113: the run is in the OLD regime (arm-0 level of bda_scan >= REGIME_OLD_SCAN; a NEW run is not
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
''',
     r'''    # Session 114: UpdateTitle ran on the present thread in both arms (pres_title_n level >= 1: counted only after the
    # SDL main loop started), and the candidate does not wait there - its per-call wall level(pres_title_ns) /
    # level(pres_title_n) is at most TITLE_WALL_MAX_NS ns and strictly below today's.  A missing level fails its check.
    tn = [lev[a].get('pres_title_n') for a in (0, 1)]
    checks['TITLE_COUNTED'] = bool((tn[0] or 0) >= 1 and (tn[1] or 0) >= 1)
    walls = [title_wall_ns(lev[a]) for a in (0, 1)]
    checks['TITLE_ARMED'] = (walls[0] is not None and walls[1] is not None and walls[1] <= TITLE_WALL_MAX_NS
                             and walls[1] < walls[0])
'''),
    (r'''            'bda_scan_levels': scan, 'narrow_arm0_kept': {'bda_nskip': nskip0},
            'bda_nwould_all_rows': would, 'bda_nmiss_all_rows': miss, 'bda_nxthr_all_rows': xthr,
''',
     r'''            'title_n_levels': tn, 'title_wall_per_call_ns': walls,
'''),
    ("    \"\"\"pred/02 video pass vsn113 (pinned; gate file gates_narrow1.txt = gates_base.txt + bdanarrow=1).  Returns\n",
     "    \"\"\"pred/02 video pass vtt114 (pinned; gate file gates_title1.txt = gates_base.txt + titleasync=1).  Returns\n"),
    (r'''        'bdanarrow_1_in_gate_text': ' dawalk=1 ' in gates and ' bdanarrow=1 ' in gates,
        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',
        'shifted': env.get('KYTY_BUFFER_GC_TRIGGER_SHIFT_MB') == '1024',
''',
     r'''        'titleasync_1_in_gate_text': ' dawalk=1 ' in gates and ' titleasync=1 ' in gates,
        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',
'''),
    (r'''def ship_rules(dt):
    """S1 / S2 of the ship rule on one estimator's d dt_us statistics."""
    return {
        'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,
        'S2_dt_2se_excludes_0': (dt['mean'] is not None and dt['se'] is not None
                                 and dt['mean'] + 2 * dt['se'] < 0),
    }
''',
     r'''def ship_rules(dt):
    """S1 / S2 of the ship rule on one estimator's d dt_us statistics (s114: S1 not slower than SHIP_US, S2 the
    noisy-run guard d mean + 2SE <= S2_US)."""
    return {
        'S1_dt_le_+50': dt['mean'] is not None and dt['mean'] <= SHIP_US,
        'S2_dt_2se_le_+200': (dt['mean'] is not None and dt['se'] is not None
                              and dt['mean'] + 2 * dt['se'] <= S2_US),
    }
'''),
    ("    (us a flip; negative: bdanarrow=1 faster), labelled SIZE_LABEL.  Report only: no admission or decision term reads\n",
     "    (us a flip; negative: titleasync=1 faster), labelled SIZE_LABEL.  Report only: no admission or decision term reads\n"),
    ("    out = {'scorer': 'shn113.py', 'scorer_sha256': sha256_file(__file__), 'tag': tag, 'pred': PRED, 'draft': bool(draft),\n",
     "    out = {'scorer': 'ttl114.py', 'scorer_sha256': sha256_file(__file__), 'tag': tag, 'pred': PRED, 'draft': bool(draft),\n"),
    ("                                             'gpu_busy_us', 'draws')}\n",
     "                                             'gpu_busy_us', 'draws', 'flip_rsv_wait_ns')}\n"),
    (r'''    for k in ('bda_scan', 'bda_nskip', 'bda_ginv_reg', 'bda_ginv_map', 'bda_rinv', 'bgc_evict', 'da_q_free',
              'da_q_noguard', 'da_guard_busy', 'da_guard_yield'):
''',
     r'''    for k in ('pres_title_ns', 'pres_title_n', 'flip_rsv_wait_ns', 'flip_rsv_wait_n', 'flip_hold_ns', 'flip_hold_n',
              'mt_age_ns', 'mt_n', 'bda_scan', 'bgc_evict', 'da_q_free', 'da_q_noguard', 'da_guard_busy',
              'da_guard_yield'):
'''),
    (r'''    add('P1', 'arm-0 bda_scan level in [800, 1400] a flip (the OLD regime: every region walked again once a frame)',
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
''',
     r'''    us = [None if w is None else w / 1000.0 for w in (title_wall_ns(lev[0]), title_wall_ns(lev[1]))]
    add('P1', 'arm-0 per-call wall of UpdateTitle, level(pres_title_ns) / level(pres_title_n) / 1000, in [20, 5000] us '
        'a call (titleasync=0 waits for the SDL main thread)', us[0], 20, 5000)
    add('P2', 'arm-1 per-call wall of UpdateTitle <= 20 us a call (titleasync=1 posts without waiting)',
        us[1], None, 20)
    add('P3', 'd mean dt_us (arm 1 - arm 0, main estimator, rows 10..89) in [-500, +100] us',
        stats['dt_us']['mean'], -500, 100)
    add('P4', 'd mean dt_us (main estimator) <= 0 us (titleasync=1 not slower at all)',
        stats['dt_us']['mean'], None, 0)
    add('P5', 'd gpu_busy_us in [-150, +150] a flip', stats['gpu_busy_us']['mean'], -150, 150)
    add('P6', 'd flip_rsv_wait_ns (arm 1 - arm 0, main estimator) <= 0 raw ns a flip (the per-row counter: the '
        'blocking wait of GuestGpu for VideoOutConfig::mutex in ReserveFlipRequest after a failed TryLock)',
        stats['flip_rsv_wait_ns']['mean'], None, 0)
'''),
    ("        v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP bdanarrow=0 (run not admitted)'\n",
     "        v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP titleasync=0 (run not admitted)'\n"),
    ("        v = 'KEEP bdanarrow=0 (ship rule S1-S2 on mean dt not met)'\n",
     "        v = 'KEEP titleasync=0 (ship rule S1-S2 on mean dt not met)'\n"),
    ("        v = 'SHIP bdanarrow=1 as the new default (a new build: its video pass is owed)'\n",
     "        v = 'SHIP titleasync=1 as the new default (a new build: its video pass is owed; ctl114 must read PASS)'\n"),
    ("        v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vsn113 is read)'\n",
     "        v = 'SHIP_PENDING_VIDEO (titleasync=1: S1-S2 met; nothing ships until vtt114 is read)'\n"),
    ("        v = 'KEEP bdanarrow=0 (video pass failed)'\n", "        v = 'KEEP titleasync=0 (video pass failed)'\n"),
    (r'''    out['must_not_be_claimed'] = ('60 FPS; a game-speed figure on the unpinned default setup; any '
                                  'gain from d cpu_net_us alone; that route A is licensed by this run; a size '
                                  'read from the secondary 60-88 window; a gain in the NEW regime or in scenes not '
                                  'measured (the size is an OLD-regime size); that bdanarrow=1 is safe beyond this '
                                  'run; additivity')
''',
     r'''    out['must_not_be_claimed'] = ('60 FPS; a game-speed figure on the unpinned default setup; a speed gain from '
                                  'd cpu_net_us alone; that the 3-s stall of session 113 was the title wait (the '
                                  'control proves the knob, not the event); additivity')
'''),
    ("    lines = ['shn113.py %s status=%s seal=%s' % (out['tag'], out['status'], out.get('pred_sha256'))]\n",
     "    lines = ['ttl114.py %s status=%s seal=%s' % (out['tag'], out['status'], out.get('pred_sha256'))]\n"),
    (r'''        lines.append('  bdanarrow: bda_scan levels %s  bda_nskip arm-0 kept totals %s  bda_nwould / bda_nmiss / '
                     'bda_nxthr over all rows %s / %s / %s'
                     % (a.get('bda_scan_levels'), a.get('narrow_arm0_kept'), a.get('bda_nwould_all_rows'),
                        a.get('bda_nmiss_all_rows'), a.get('bda_nxthr_all_rows')))
''',
     r'''        lines.append('  titleasync: pres_title_n levels %s  per-call wall %s ns (arm-1 cap %d ns)'
                     % (a.get('title_n_levels'), a.get('title_wall_per_call_ns'), TITLE_WALL_MAX_NS))
'''),
    (r'''                  'cspf_have', 'cspf_new', 'bda_scan', 'bda_nskip', 'bda_ginv_reg', 'bda_ginv_map', 'bda_rinv',
                  'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict'):
''',
     r'''                  'cspf_have', 'cspf_new', 'pres_title_ns', 'pres_title_n', 'flip_rsv_wait_ns', 'flip_rsv_wait_n',
                  'flip_hold_ns', 'flip_hold_n', 'mt_age_ns', 'mt_n', 'bda_scan', 'bgc_evict'):
'''),
    ("              'da_walk_us', 'gpu_busy_us'):\n", "              'da_walk_us', 'gpu_busy_us', 'flip_rsv_wait_ns'):\n"),
    ("            print('tag %r is not a pred/02 tag (shn113, shn113b, optional _entry1)' % o.tag)\n",
     "            print('tag %r is not a pred/02 tag (ttl114, ttl114b, optional _entry1)' % o.tag)\n"),
], forbidden=('bdanarrow', 'shn113b', 'vsn113', 'REGIME_OLD', 'NARROW_', "'NO_CHECK'", 'NO_XTHR', "lev[1].get('bda_nskip')",
              'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB', 'S1_dt_le_-100', 'excludes_0', OLD_SHA, "'shifted'", 's113/'))


# =====================================================================================================================
# the fixtures
# =====================================================================================================================
derive('test_shn113.py', [
    (r'''"""Session 113: fixtures for shn113.py (the ABBA of knob bdanarrow: today's bdanarrow=0 against the candidate
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
"""
''',
     r'''"""Session 114: fixtures for ttl114.py (the ABBA of knob titleasync: today's titleasync=0 against the candidate
titleasync=1, build 916f6489) in NON-draft mode, derived from session 113's sealed test_shn113.py by make_ttl114.py
(whole-line anchored replacements; the same coverage wherever a term is kept): tag ttl114, video vtt114, the arms,
the 916f6489 counters pres_title_ns / pres_title_n / flip_rsv_wait_ns / flip_rsv_wait_n / flip_hold_ns / flip_hold_n
/ mt_age_ns / mt_n (FrameTrace-x, each alone in SCHEMA_*), the launch without session 113's GC trigger shift, arming
TITLE_COUNTED / TITLE_ARMED (session 113's REGIME_OLD_ARM0 / NARROW_* / NO_CHECK / NO_XTHR and their fixtures
removed) and DEFAULTS_ON with its daslot=1 parts, the rule S1 d mean <= +50 / S2 d mean + 2SE <= +200, the quoted size,
predictions P1-P7.  Rule (decision after 107, item 2): every decision term and every admission term gets a fixture
where ONLY it fails, plus every verdict branch.  Each case asserts the exact failing set (failed_controls) AND the
exact failing sub-lists: rules, video checks, arming sub-checks (by name, under control:ARMING), area-mirror criteria
where relevant, and the exact protocol error list.  Terms that cannot fail alone by construction are asserted as exact
sets, with the scorer lines that couple them cited at the case.  The seal check is pointed at a throwaway file and
GATES_FILE at a sha-checked copy of gates_base.txt (from C:/kyty/s114, else C:/kyty/s113 - the same bytes, GATES_SHA
asserted); everything else is the scorer's own code.  IDENTITY exists only in main(): main() is driven in-process with
EXE / PRODUCTION_ROOT pointed at fixtures.  CONSTANTS compares every sealed constant except PRED_SHA / PRED_BYTES,
which it only requires to be both None (the draft) or a 64-hex sha256 and a positive size (the sealed copy), so the
sealed scorer stays green on this suite (audit111 MINOR-5).

The window rows the fixtures edit are HARD-CODED here (MAIN = 10..89, SEC = 60..88), never read from the scorer, so a
mutant of the scorer's window cannot move its own fixtures.  The estimator cases (all noise-free, exact values):
  KEEP_edge        arm-1 row 9 +29 000, rows 10 and 89 -8 000: main -350 exactly, secondary -150 exactly (kills
                   KEEP_LO 9 / 11, KEEP_HI 89, the slice shifted down one row).
  SEC_edge         arm-1 rows 59 and 89 +29 000, rows 60 and 88 -2 900: secondary -350 exactly, main +502.5 exactly
                   (KEEP by the main estimator; the secondary would pass - it never decides).
  EST_rows0_9      arm-1 rows 0..9 +29 000 (the audit110 hitch shape): main and secondary -150 exactly (a full-block
                   estimator would read +3 072).
  EST_rows10_59    arm-1 rows 10..59 +800: main +350 exactly (KEEP), secondary -150 exactly (would pass).
  EST_rows10_59_ship  d +300, arm-1 rows 10..59 -480: main 0 exactly (SHIP pending), secondary +300 (would fail both).
  PENDING          the noisy base fixture: main and secondary d mean / SE recounted from the log here, independently
                   of the scorer (1e-9 relative), and they differ; the quoted size is the main d mean with 2 x its SE.
Killers of the session-109 survivors kept: SE_exact (sample SD, now straddling the S2 bar +200), LEVEL_median (median
block levels: dt, pres_title_ns in both arms, pres_title_n), FATAL_waitslow_log / _so.  Plus CONSTANTS (the sealed
identity and the two windows), full-text refusals / pending verdict, tag acceptance (ttl114b, ttl114_entry1,
ttl114b_entry1 reach evaluate()) and refusal of the others (session 113's tags, the control's and the video's
included), the draft-only --secondary.  Threshold edges (audit111 MINOR-10: a fixture on each side of every
tolerance): S1 (S1_edge +50 and S1_edge_in +49.5 pending; S1_only +50.5: S1 fails alone, S2 holds), S2 (S2_edge +200
with SE 0: S2 holds, S1 fails; S2_edge_out +200.5: both fail; S2_only and SE_exact: S2 fails alone through its 2SE),
TITLE_COUNTED (level 1 passes in both arms, 0.9875 fails in either; the main window only; level 0; missing),
TITLE_ARMED (20 000 ns a call passes, 20 001 fails; equal walls fail, 1 ns below passes, arm 0 faster fails; per call,
not per flip; the main window only; missing in either arm), the defaults' levels (cspfree_hit and da_q_free level 1
pass in both arms, 0.9875 fails in either), the all-rows totals (DEFAULTS_slot_bad*, DEFAULTS_bad*: a total of 1
fails, the good run's 0 passes), each per-arm term's lag case (values outside rows 10..89 do not count) and missing
level, the attempt hold (595 s passes, 594 fails), the area mirror's minimum block (8 flips count, 7 do not), the walk
identity (0.9 % passes, 1.1 % fails), the video floor (3 000 frames pass, 2 999 fail), and the P1-P7 bands with exact
values at and just outside every edge.
    python test_ttl114.py <ttl114.py> [<fixture dir>]
"""
'''),
    ("BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s106_stage/shn113/fx')\n",
     "BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s114/ttl114_draft/fx')\n"),
    ("spec = importlib.util.spec_from_file_location('shn113', SRC)\n",
     "spec = importlib.util.spec_from_file_location('ttl114', SRC)\n"),
    ("seal.write_text('fixture seal 113 shn', encoding='utf-8')\n",
     "seal.write_text('fixture seal 114 ttl', encoding='utf-8')\n"),
    ("GATES_SRC = Path(ORIG['GATES_FILE']) if Path(ORIG['GATES_FILE']).is_file() else Path('C:/kyty/s112/gates_base.txt')\n",
     "GATES_SRC = Path(ORIG['GATES_FILE']) if Path(ORIG['GATES_FILE']).is_file() else Path('C:/kyty/s113/gates_base.txt')\n"),
    ("TAG = 'shn113'\n", "TAG = 'ttl114'\n"),
    (r'''def make(name, d_dt=-150, noise=300, cpu_noise=None, blocks=224, hit0=262, hit1=262, look0=266, look1=266,
         qfree0=1080, qfree1=1080, scan0=1068, scan1=52, nskip0=0, nskip1=1, gpu1=12700, gb0=1, gb1=2, sync0=1,
         sync1=1, pins=1, pin_mode=1, recs=2, fatal=None,
         dt_base=31000, draws1=5000, kpx1=201600, spin1=30, arm_text=None, prereg=None, binary=None, extra_env=None,
         block_noise=0.0, pattern=(0, 1, 1, 0), abba=1, gate=None, pre_dt=None, row=None, tail=()):
    """row(n, blk, arm, idx, tok): edit the three token dicts of frame n in place (idx = in-block index from
    frame 1801, None before); set tok[kind] = None to drop that line.  gate(b, fields): edit (or drop, by returning
    None) the GateArm line of block b.  pre_dt: dt_us of the rows before 1800.  cpu_noise: the SD of cpu_gpu_us
    (default noise; the same random draws are taken either way).  The shipping configuration in BOTH arms: cspfree
    on (look/hit per arm), daslot=1 (da_q_free qfree0 / qfree1 = da_qcall 1080: every call off m_mutex), daguard=1
    (da_q_noguard 0).  The OLD regime: bda_scan scan0 (arm 0, today: every region walked again once a frame) / scan1
    (arm 1, bdanarrow=1); bda_nskip nskip0 / nskip1 (the registration invalidations knob 1 skipped: 0 in arm 0, 1 a
    flip in arm 1); bda_ginv_reg 1 / 0 a flip, bda_rinv 3 and bgc_evict 1 in both arms; knob 2 off (bda_nwould =
    bda_nmiss = 0), bda_nxthr 0.  gpu_busy_us 12 700 (arm 0) / gpu1 (arm 1); the rows before the schedule are arm 0;
    da_guard_busy gb0 / gb1."""
''',
     r'''def make(name, d_dt=-150, noise=300, cpu_noise=None, blocks=224, hit0=262, hit1=262, look0=266, look1=266,
         qfree0=1080, qfree1=1080, tns0=400000, tns1=3000, tn0=1, tn1=1, rsv1=1000, gpu1=12700, gb0=1, gb1=2,
         sync0=1, sync1=1, pins=1, pin_mode=1, recs=2, fatal=None,
         dt_base=31000, draws1=5000, kpx1=201600, spin1=30, arm_text=None, prereg=None, binary=None, extra_env=None,
         block_noise=0.0, pattern=(0, 1, 1, 0), abba=1, gate=None, pre_dt=None, row=None, tail=()):
    """row(n, blk, arm, idx, tok): edit the three token dicts of frame n in place (idx = in-block index from
    frame 1801, None before); set tok[kind] = None to drop that line.  gate(b, fields): edit (or drop, by returning
    None) the GateArm line of block b.  pre_dt: dt_us of the rows before 1800.  cpu_noise: the SD of cpu_gpu_us
    (default noise; the same random draws are taken either way).  The shipping configuration in BOTH arms: cspfree
    on (look/hit per arm), daslot=1 (da_q_free qfree0 / qfree1 = da_qcall 1080: every call off m_mutex), daguard=1
    (da_q_noguard 0).  The title instrument: pres_title_ns tns0 (arm 0, today: UpdateTitle waits for the SDL main
    thread, 400 000 ns) / tns1 (arm 1, titleasync=1: 3 000 ns) over pres_title_n tn0 / tn1 calls a flip (400 / 3 us a
    call); flip_rsv_wait_ns 5 000 (arm 0) / rsv1 (arm 1) raw ns a flip over 2 / 3 waits; flip_hold_ns 100 000 /
    100 500 over 1; mt_age_ns 30 000 / 40 000 over 1.  bdanarrow=0 in both arms: bda_scan 52, bda_ginv_reg 1,
    bda_nskip 0, bda_rinv 3, bgc_evict 1, the knob-2 counters 0.  gpu_busy_us 12 700 (arm 0) / gpu1 (arm 1); the rows
    before the schedule are arm 0; da_guard_busy gb0 / gb1."""
'''),
    ("                     'da_stale': 0, 'da_stale_old': 0, 'da_busy': 0, 'bda_scan': scan1 if arm else scan0},\n",
     "                     'da_stale': 0, 'da_stale_old': 0, 'da_busy': 0, 'bda_scan': 52},\n"),
    (r'''                  'da_q_noguard': 0, 'da_guard_yield': 0, 'bda_ginv_reg': 0 if arm else 1, 'bda_ginv_map': 0,
                  'bda_rinv': 3, 'bda_nskip': nskip1 if arm else nskip0, 'bda_nwould': 0, 'bda_nmiss': 0,
                  'bda_nxthr': 0, 'bgc_evict': 1, 'bda_nrace': 0, 'prio_unsub': 5, 'prio_stall': 0,
                  'gw_idle_prio': 0},
''',
     r'''                  'da_q_noguard': 0, 'da_guard_yield': 0, 'bda_ginv_reg': 1, 'bda_ginv_map': 0,
                  'bda_rinv': 3, 'bda_nskip': 0, 'bda_nwould': 0, 'bda_nmiss': 0,
                  'bda_nxthr': 0, 'bgc_evict': 1, 'bda_nrace': 0, 'prio_unsub': 5, 'prio_stall': 0,
                  'gw_idle_prio': 0, 'pres_title_ns': tns1 if arm else tns0, 'pres_title_n': tn1 if arm else tn0,
                  'flip_rsv_wait_ns': rsv1 if arm else 5000, 'flip_rsv_wait_n': 3 if arm else 2,
                  'flip_hold_ns': 100500 if arm else 100000, 'flip_hold_n': 1,
                  'mt_age_ns': 40000 if arm else 30000, 'mt_n': 1},
'''),
    (r'''def video(d, frames=3990, glitches=0, gate='bdanarrow=1', pin='1', binary=None, tag='v', rec=True, env_extra=None,
          attempts=None, gates=None, shift='1024'):
    vm = d / ('vsn113_%s.json' % tag)
    vr = d / ('vsn113_%s_glitch.txt' % tag)
    env = {'KYTY_REC': 'x.mp4'} if rec else {}
    if pin:
        env['KYTY_GPU_CLOCK_PIN'] = pin
    if shift:
        env['KYTY_BUFFER_GC_TRIGGER_SHIFT_MB'] = shift
''',
     r'''def video(d, frames=3990, glitches=0, gate='titleasync=1', pin='1', binary=None, tag='v', rec=True, env_extra=None,
          attempts=None, gates=None):
    vm = d / ('vtt114_%s.json' % tag)
    vr = d / ('vtt114_%s_glitch.txt' % tag)
    env = {'KYTY_REC': 'x.mp4'} if rec else {}
    if pin:
        env['KYTY_GPU_CLOCK_PIN'] = pin
'''),
    ('    """Drive shn113.main() in-process; returns (rc, the result dict evaluate() built and main() finished, stdout)."""\n',
     '    """Drive ttl114.main() in-process; returns (rc, the result dict evaluate() built and main() finished, stdout)."""\n'),
    (r'''KEEP_NA = 'KEEP bdanarrow=0 (run not admitted)'
KEEP_BAR = 'KEEP bdanarrow=0 (ship rule S1-S2 on mean dt not met)'
KEEP_VID = 'KEEP bdanarrow=0 (video pass failed)'
SHIP = 'SHIP bdanarrow=1 as the new default (a new build: its video pass is owed)'
PENDING = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vsn113 is read)'
ARMING = {'control:ARMING'}
BOTH_RULES = ['S1_dt_le_-100', 'S2_dt_2se_excludes_0']
PRED_BANDS = {'P1': [800, 1400], 'P2': [30, 200], 'P3': [-1500, 200], 'P4': [None, -100], 'P5': [-150, 150],
              'P6': [0.5, 3], 'P7': [-40, 40]}
''',
     r'''KEEP_NA = 'KEEP titleasync=0 (run not admitted)'
KEEP_BAR = 'KEEP titleasync=0 (ship rule S1-S2 on mean dt not met)'
KEEP_VID = 'KEEP titleasync=0 (video pass failed)'
SHIP = 'SHIP titleasync=1 as the new default (a new build: its video pass is owed; ctl114 must read PASS)'
PENDING = 'SHIP_PENDING_VIDEO (titleasync=1: S1-S2 met; nothing ships until vtt114 is read)'
ARMING = {'control:ARMING'}
S1 = 'S1_dt_le_+50'
S2 = 'S2_dt_2se_le_+200'
BOTH_RULES = [S1, S2]
PRED_BANDS = {'P1': [20, 5000], 'P2': [None, 20], 'P3': [-500, 100], 'P4': [None, 0], 'P5': [-150, 150],
              'P6': [None, 0], 'P7': [-40, 40]}
# the video checks, by name (a check added to or dropped from read_video must fail the SHIP case)
VIDEO_CHECKS = sorted(['binary', 'titleasync_1_in_gate_text', 'pinned', 'recorded', 'no_schedule', 'no_checkpoints',
                       'one_ok_attempt', 'frames', 'no_glitch'])
# the claims, written out here (not read from the scorer: a dropped or changed claim must fail)
CLAIMS = ('60 FPS; a game-speed figure on the unpinned default setup; a speed gain from d cpu_net_us alone; that the '
          '3-s stall of session 113 was the title wait (the control proves the knob, not the event); additivity')
'''),
    ("SIZE_LABEL = '%s'\n" % OLD_LABEL, "SIZE_LABEL = '%s'\n" % NEW_LABEL),
    ("            'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '1024'}\n",
     "            'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}\n"),
    ('TAG_MSG = "tag %r is not a pred/02 tag (shn113, shn113b, optional _entry1)"\n',
     'TAG_MSG = "tag %r is not a pred/02 tag (ttl114, ttl114b, optional _entry1)"\n'),
    (r'''                'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict', 'bda_nrace', 'prio_unsub',
                'prio_stall', 'gw_idle_prio')
''',
     r'''                'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict', 'bda_nrace', 'prio_unsub',
                'prio_stall', 'gw_idle_prio', 'pres_title_ns', 'pres_title_n', 'flip_rsv_wait_ns', 'flip_rsv_wait_n',
                'flip_hold_ns', 'flip_hold_n', 'mt_age_ns', 'mt_n')
'''),
    (r'''def pred_good(o):
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
''',
     r'''def pred_good(o):
    """P1-P7 of the good fixture: the seven keys, their sealed bands, the fixture's exact values (P1 400 us a call, P2 3,
    P5 0, P6 -4 000 ns a flip, P7 0; P3 / P4 the main d mean, a SHIP here), all seven hit, P6's text stating its unit;
    the scorer's name in the result and in the summary header; both estimators recounted from the log here (1e-9
    relative), the secondary's own selection (block 3 excluded as an edge block there, nothing excluded in the main
    one), and the two summary lines naming the windows; the quoted size = the main d mean with 2 x its SE (result and
    summary line); the reported title / reserve-wait / hold / main-task levels and d flip_rsv_wait_ns; the arming title
    levels and per-call walls and their summary line; the area mirror's 110 block pairs; the claims, word for word."""
    dt = main_dt(o)
    m_main, se_main, n_main = recount(good, MAIN)
    m_sec, se_sec, n_sec = recount(good, SEC)
    lines = mod.summary(o).split(NL)
    rep = o['reported']
    return (pred_values(o, P1=400.0, P2=3.0, P3=dt, P4=dt, P5=0.0, P6=-4000.0, P7=0.0, hits=list(PRED_BANDS))
            and o['scorer'] == 'ttl114.py' and lines[0].startswith('ttl114.py ttl114 status=ADMITTED')
'''),
    (r'''            and size_exact(o, dt, 2 * o['pair_stats']['dt_us']['se']) and dt < -100
            and o['reported']['bda_scan_levels'] == [1068.0, 52.0] and o['reported']['bda_nskip_levels'] == [0.0, 1.0]
            and o['arming']['bda_scan_levels'] == [1068.0, 52.0] and o['arming']['da_q_free_levels'] == [1080.0, 1080.0]
            and o['area_verdict_mirror']['pairs'] == 110
            and 'a gain in the NEW regime' in o['must_not_be_claimed']
            and o['predictions']['P4']['text'].endswith('the discriminating prediction, low confidence'))
''',
     r'''            and size_exact(o, dt, 2 * o['pair_stats']['dt_us']['se']) and dt < 0
            and rep['pres_title_ns_levels'] == [400000.0, 3000.0] and rep['pres_title_n_levels'] == [1.0, 1.0]
            and rep['flip_rsv_wait_ns_levels'] == [5000.0, 1000.0] and rep['flip_rsv_wait_n_levels'] == [2.0, 3.0]
            and rep['flip_hold_ns_levels'] == [100000.0, 100500.0] and rep['flip_hold_n_levels'] == [1.0, 1.0]
            and rep['mt_age_ns_levels'] == [30000.0, 40000.0] and rep['mt_n_levels'] == [1.0, 1.0]
            and rep['flip_rsv_wait_ns']['mean'] == -4000.0 and rep['flip_rsv_wait_ns']['n'] == 110
            and o['arming']['title_n_levels'] == [1.0, 1.0]
            and o['arming']['title_wall_per_call_ns'] == [400000.0, 3000.0]
            and ('  titleasync: pres_title_n levels [1.0, 1.0]  per-call wall [400000.0, 3000.0] ns (arm-1 cap '
                 '20000 ns)') in lines
            and o['arming']['da_q_free_levels'] == [1080.0, 1080.0]
            and o['area_verdict_mirror']['pairs'] == 110
            and o['must_not_be_claimed'] == CLAIMS
            and 'raw ns a flip' in o['predictions']['P6']['text'])
'''),
    (r'''    want = {'PRODUCTION_ROOT': 'C:/kyty/s113', 'PRED': 'C:/kyty/s113/pred/02_shn113.md',
            'BINARY_SHA': '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373',
            'GATES_FILE': 'C:/kyty/s113/gates_base.txt',
            'GATES_SHA': '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf',
            'ARMS': ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=1'),
            'SCHEDULE': '90+1800:dawalk=1 dawalklead=1 bdanarrow=0|dawalk=1 dawalklead=1 bdanarrow=1',
            'TAG_RE': r'shn113b?(?:_entry1)?', 'KEEP_LO': 10, 'KEEP_HI': 90, 'SECONDARY_LO': 60,
''',
     r'''    want = {'PRODUCTION_ROOT': 'C:/kyty/s114', 'PRED': 'C:/kyty/s114/pred/02_ttl114.md',
            'BINARY_SHA': '916f64898a5a31c697ad0d823f0795850acc160cf56271b566e8ae330c7c3b2c',
            'GATES_FILE': 'C:/kyty/s114/gates_base.txt',
            'GATES_SHA': '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf',
            'ARMS': ('dawalk=1 dawalklead=1 titleasync=0', 'dawalk=1 dawalklead=1 titleasync=1'),
            'SCHEDULE': '90+1800:dawalk=1 dawalklead=1 titleasync=0|dawalk=1 dawalklead=1 titleasync=1',
            'TAG_RE': r'ttl114b?(?:_entry1)?', 'KEEP_LO': 10, 'KEEP_HI': 90, 'SECONDARY_LO': 60,
'''),
    ("case('SHIP', run_eval(good, *video(good, tag='ok')), SHIP)\n",
     "case('SHIP', run_eval(good, *video(good, tag='ok')), SHIP,\n"
     "     check=lambda o: sorted(o['video']['checks']) == VIDEO_CHECKS and o['video']['frames'] == 3990)\n"),
    (r'''# KEEP by the bar = S1_S2_positive / S2_only / S1_only / SE_exact / SEC_edge / EST_rows10_59 / PRED_*; KEEP by a
# failed video = V_*; KEEP not admitted = every admission case
''',
     r'''# KEEP by the bar = S1_S2_positive / S2_only / S1_only / S2_edge* / SE_exact / SEC_edge / EST_rows10_59 / PRED_*;
# KEEP by a failed video = V_*; KEEP not admitted = every admission case
'''),
    (r'''# A positive d mean fails both S1 (d mean <= SHIP_US = -100) and S2 (d mean + 2 SE < 0): ship_rules() returns the
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
''',
     r'''# A d mean above both bars fails both S1 (d mean <= SHIP_US = +50) and S2 (d mean + 2 SE <= S2_US = +200):
# ship_rules() returns the two terms of one dict; both listed.  P3 (up to +100) and P4 (up to 0) miss.
case('S1_S2_positive', run_eval(make('s1', d_dt=260, noise=80)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: (200 < main_dt(o) < 320 and not o['predictions']['P3']['hit']
                      and not o['predictions']['P4']['hit']))
# S2 alone: the d mean below the S1 bar (about -196), d mean + 2SE above +200 (SE about 239) - and d mean + 1 SE below
# it (kills S2 read with 1 SE, S2 dropped and a verdict on S1 alone)
case('S2_only', run_eval(make('s2', d_dt=-150, noise=300, block_noise=2500)), KEEP_BAR,
     rules=[S2], check=lambda o: (main_dt(o) <= 50
                                  and main_dt(o) + o['pair_stats']['dt_us']['se'] <= 200
                                  < main_dt(o) + 2 * o['pair_stats']['dt_us']['se']))
# S1's edge, noise-free (every pair delta equal, SE 0): d mean dt exactly +50 - S1 holds (<= +50), S2 holds: pending
# (kills S1 strict and a bar moved to +49.5); P3 hits, P4 misses ...
case('S1_edge', run_eval(make('s1edge', d_dt=50, noise=0)), PENDING,
     check=lambda o: (main_dt(o) == 50.0 and o['pair_stats']['dt_us']['sd'] == 0.0
                      and pred_values(o, P3=50.0, P4=50.0, hits=['P1', 'P2', 'P3', 'P5', 'P6', 'P7'])))
# ... +49.5 (arm-1 frames with an even number -1 us: 40 of the 80 main-window rows of each block): both hold,
# pending ...
case('S1_edge_in', run_eval(make('s1edgein', d_dt=50, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and n % 2 == 0, edits={'main': {'dt_us': 31050 - 1}}))), PENDING,
    check=lambda o: main_dt(o) == 49.5 and o['pair_stats']['dt_us']['sd'] == 0.0)
# ... and +50.5 (+1 us on those rows): S1 fails ALONE - S2 still holds (+50.5 + 2 * 0 <= +200) (kills a bar moved to
# +50.5 or +100, S1 dropped and a verdict on S2 alone)
case('S1_only', run_eval(make('s1only', d_dt=50, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and n % 2 == 0, edits={'main': {'dt_us': 31050 + 1}}))), KEEP_BAR,
    rules=[S1],
    check=lambda o: (main_dt(o) == 50.5 and o['pair_stats']['dt_us']['sd'] == 0.0
                     and pred_values(o, P3=50.5, P4=50.5, hits=['P1', 'P2', 'P3', 'P5', 'P6', 'P7'])))
# S2's edge, noise-free: d mean + 2 SE exactly +200 (d +200, SE 0) - S2 holds (<= +200) while S1 fails (kills S2
# strict, S2 on the S1 bar and a bar moved to +199.5) ...
case('S2_edge', run_eval(make('s2edge', d_dt=200, noise=0)), KEEP_BAR, rules=[S1],
     check=lambda o: (main_dt(o) == 200.0 and o['pair_stats']['dt_us']['sd'] == 0.0
                      and pred_values(o, P3=200.0, P4=200.0, hits=['P1', 'P2', 'P5', 'P6', 'P7'])))
# ... and +200.5 (+1 us on the even arm-1 rows): S2 fails too (kills a bar moved to +200.5 or +201)
case('S2_edge_out', run_eval(make('s2edgeout', d_dt=200, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and n % 2 == 0, edits={'main': {'dt_us': 31200 + 1}}))), KEEP_BAR,
    rules=BOTH_RULES, check=lambda o: main_dt(o) == 200.5 and o['pair_stats']['dt_us']['sd'] == 0.0)
'''),
    (r'''# the other direction: d 0, arm-1 rows 10..59 -400 us: main -250 exactly (SHIP pending); the secondary reads 0
# exactly and would FAIL both rules (0 > -100; 0 + 2 * 0 is not < 0).
case('EST_rows10_59_ship', run_eval(make('estrows10s', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None and 10 <= i < 60,
    edits={'main': {'dt_us': 31000 - 400}}))), PENDING,
    check=lambda o: (main_dt(o) == -250.0 and sec_dt(o) == 0.0 and sec_rules(o) == BOTH_RULES
                     and '  secondary would FAIL S1_dt_le_-100 (not deciding)' in mod.summary(o).split(NL)
                     and '  secondary would FAIL S2_dt_2se_excludes_0 (not deciding)' in mod.summary(o).split(NL)))
''',
     r'''# the other direction: d +300, arm-1 rows 10..59 -480 us: main 0 exactly (SHIP pending); the secondary reads +300
# exactly and would FAIL both rules (+300 > +50; +300 + 2 * 0 > +200).
case('EST_rows10_59_ship', run_eval(make('estrows10s', d_dt=300, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None and 10 <= i < 60,
    edits={'main': {'dt_us': 31300 - 480}}))), PENDING,
    check=lambda o: (main_dt(o) == 0.0 and sec_dt(o) == 300.0 and sec_rules(o) == BOTH_RULES
                     and '  secondary would FAIL S1_dt_le_+50 (not deciding)' in mod.summary(o).split(NL)
                     and '  secondary would FAIL S2_dt_2se_le_+200 (not deciding)' in mod.summary(o).split(NL)))
'''),
    (r'''# noise-free; arm-1 blocks 31 000 - 150 +- 867 (+ when blk // 4 is even).  Paired quartets 1..55 (blocks 0-3 lie
# before frame 2100): 2 pairs each, delta -150 + 867 (even quartet) or -150 - 867 (odd).  mean -165.7636,
# sample SE 83.0298 -> mean + 2 SE = +0.296 (S2 fails: KEEP by the bar); population SE -> -0.461 (S2 would pass).
SE_B = 867
''',
     r'''# noise-free; arm-1 blocks 31 000 - 150 +- 2 024 (+ when blk // 4 is even).  Paired quartets 1..55 (blocks 0-3 lie
# before frame 2100): 2 pairs each, delta -150 + 2 024 (even quartet) or -150 - 2 024 (odd).  mean -186.8, sample SE
# 193.832 -> mean + 2 SE = +200.864 (S2 fails: KEEP by the bar); population SE -> +199.098 (S2 would pass).
SE_B = 2024
'''),
    ("assert SE_MEAN + 2 * SE_SAMPLE > 0 > SE_MEAN + 2 * SE_POP, 'SE_exact no longer straddles the S2 edge'\n",
     "assert SE_MEAN + 2 * SE_SAMPLE > 200 > SE_MEAN + 2 * SE_POP, 'SE_exact no longer straddles the S2 edge'\n"),
    ("case('SE_exact', run_eval(make('seexact', noise=0, block_noise=SE_B)), KEEP_BAR, rules=['S2_dt_2se_excludes_0'],\n",
     "case('SE_exact', run_eval(make('seexact', noise=0, block_noise=SE_B)), KEEP_BAR, rules=[S2],\n"),
    (r'''# noise-free; block 12 (arm 0) and block 9 (arm 1) +2 900 us on every row, block 16 (arm 0) and block 17 (arm 1)
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
''',
     r'''# noise-free; block 12 (arm 0) and block 9 (arm 1) +2 900 us on every row, block 16 (arm 0) pres_title_ns 600 000 000
# and block 17 (arm 1) 2 000 000, block 21 (arm 1) pres_title_n 0: medians 31 000 / 30 850 / 400 000 / 3 000 / 1
# exactly (means: 31 026.4 / 30 876.4 / 5 850 909.1 / 21 154.5 / 0.991 - P1 and P2 would miss, TITLE_ARMED and
# TITLE_COUNTED would fail); the two dt outliers sit in different pairs with opposite signs, so d mean dt stays -150.
case('LEVEL_median', run_eval(make('levmed', noise=0, row=both(
    setter(pick=lambda n, b, a, i: i is not None and b in (9, 12),
           edits={'main': {'dt_us': lambda n, b, a, i: 31000 - 150 * a + 2900}}),
    setter(pick=lambda n, b, a, i: i is not None and b in (16, 17),
           edits={'x': {'pres_title_ns': lambda n, b, a, i: 2000000 if a else 600000000}}),
    setter(pick=lambda n, b, a, i: i is not None and b == 21, edits={'x': {'pres_title_n': 0}})))), PENDING,
    check=lambda o: (o['levels']['arm0']['dt_us'] == 31000.0 and o['levels']['arm1']['dt_us'] == 30850.0
                     and o['levels']['arm0']['pres_title_ns'] == 400000.0
                     and o['levels']['arm1']['pres_title_ns'] == 3000.0
                     and o['levels']['arm1']['pres_title_n'] == 1.0 and main_dt(o) == -150.0
                     and pred_values(o, P1=400.0, P2=3.0, hits=list(PRED_BANDS))))
'''),
    (r'''case('PRED_inside', run_eval(make('predin', d_dt=-300, noise=0)), PENDING,
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
''',
     r'''case('PRED_inside', run_eval(make('predin', d_dt=-300, noise=0)), PENDING,
     check=lambda o: (pred_values(o, P1=400.0, P2=3.0, P3=-300.0, P4=-300.0, P5=0.0, P6=-4000.0, P7=0.0,
                                  hits=list(PRED_BANDS)) and size_exact(o, -300.0, 0.0)))
# on the lower edges: P1 20 (arm-0 wall 20 000 ns a call), P3 -500 (P4 holds), P5 -150, P7 -40; P2 0.5 (500 ns a
# call: P2 has no lower bound) and P6 -4 000 (nor has P6) - all hit
case('PRED_edges_lo', run_eval(make('prededgelo', d_dt=-500, noise=0, tns0=20000, tns1=500, gpu1=12550,
                                    row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_miss': 260}}))),
     PENDING, check=lambda o: pred_values(o, P1=20.0, P2=0.5, P3=-500.0, P4=-500.0, P5=-150.0, P6=-4000.0,
                                          P7=-40.0, hits=list(PRED_BANDS)))
# just below them: 19.999, -501, -151, -41 - all miss but P2, P4 and P6
case('PRED_misses_lo', run_eval(make('predmisslo', d_dt=-501, noise=0, tns0=19999, tns1=500, gpu1=12549,
                                     row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_miss': 259}}))),
     PENDING, check=lambda o: pred_values(o, P1=19.999, P2=0.5, P3=-501.0, P4=-501.0, P5=-151.0, P6=-4000.0,
                                          P7=-41.0, hits=['P2', 'P4', 'P6']))
# on the upper edges: P1 5 000 (5 000 000 ns a call), P2 20 (20 000 ns = TITLE_WALL_MAX_NS: admitted), P3 +100, P5
# +150, P6 0 (arm-1 reserve wait 5 000 ns a flip, as arm 0's), P7 +40 - all hit but P4 (d +100 fails S1 alone)
case('PRED_edges_hi', run_eval(make('prededgehi', d_dt=100, noise=0, tns0=5000000, tns1=20000, gpu1=12850, rsv1=5000,
                                    row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_miss': 340}}))),
     KEEP_BAR, rules=[S1],
     check=lambda o: pred_values(o, P1=5000.0, P2=20.0, P3=100.0, P4=100.0, P5=150.0, P6=0.0, P7=40.0,
                                 hits=['P1', 'P2', 'P3', 'P5', 'P6', 'P7']))
# just above them: 5 000.001, 20.001 (above TITLE_WALL_MAX_NS: not admitted, TITLE_ARMED alone - the predictions are
# still computed), +101, +151, +1 ns a flip, +41 - all miss
case('PRED_misses_hi', run_eval(make('predmisshi', d_dt=101, noise=0, tns0=5000001, tns1=20001, gpu1=12851,
                                     rsv1=5001,
                                     row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_miss': 341}}))),
     KEEP_NA, fails=ARMING, arming=['TITLE_ARMED'], rules=[S1],
     check=lambda o: pred_values(o, P1=5000.001, P2=20.001, P3=101.0, P4=101.0, P5=151.0, P6=1.0, P7=41.0,
                                 hits=[]))
# P4's only bound: d mean exactly 0 hits, +1 misses (both pending: S1 holds)
case('PRED_P4_edge', run_eval(make('predp4edge', d_dt=0, noise=0)), PENDING,
     check=lambda o: pred_values(o, P3=0.0, P4=0.0, hits=list(PRED_BANDS)))
case('PRED_P4_out', run_eval(make('predp4out', d_dt=1, noise=0)), PENDING,
     check=lambda o: pred_values(o, P3=1.0, P4=1.0, hits=['P1', 'P2', 'P3', 'P5', 'P6', 'P7']))
'''),
    (r'''# the gate text: today's value (the arm-0 text) instead of the candidate, knob 2, no bdanarrow at all, dawalk=0
case('V_gate', run_eval(good, *video(good, gate='bdanarrow=0', tag='gt')), KEEP_VID,
     vfail=['bdanarrow_1_in_gate_text'])
case('V_gate_mode2', run_eval(good, *video(good, gate='bdanarrow=2', tag='g2')), KEEP_VID,
     vfail=['bdanarrow_1_in_gate_text'])
case('V_gate_none', run_eval(good, *video(good, gate='daslot=1', tag='gn')), KEEP_VID,
     vfail=['bdanarrow_1_in_gate_text'])
case('V_gate_dawalk', run_eval(good, *video(good, gates=gates_text.replace('dawalk=1', 'dawalk=0'), tag='gd')),
     KEEP_VID, vfail=['bdanarrow_1_in_gate_text'])
case('V_pin', run_eval(good, *video(good, pin=None, tag='pn')), KEEP_VID, vfail=['pinned'])
case('V_shift', run_eval(good, *video(good, shift=None, tag='sh')), KEEP_VID, vfail=['shifted'])
case('V_shift_wrong', run_eval(good, *video(good, shift='512', tag='s5')), KEEP_VID, vfail=['shifted'])
''',
     r'''# the gate text: today's value (the arm-0 text) instead of the candidate, a value outside the knob's 0..1, no
# titleasync at all (session 113's candidate instead), dawalk=0
case('V_gate', run_eval(good, *video(good, gate='titleasync=0', tag='gt')), KEEP_VID,
     vfail=['titleasync_1_in_gate_text'])
case('V_gate_mode2', run_eval(good, *video(good, gate='titleasync=2', tag='g2')), KEEP_VID,
     vfail=['titleasync_1_in_gate_text'])
case('V_gate_none', run_eval(good, *video(good, gate='bdanarrow=1', tag='gn')), KEEP_VID,
     vfail=['titleasync_1_in_gate_text'])
case('V_gate_dawalk', run_eval(good, *video(good, gates=gates_text.replace('dawalk=1', 'dawalk=0'), tag='gd')),
     KEEP_VID, vfail=['titleasync_1_in_gate_text'])
case('V_pin', run_eval(good, *video(good, pin=None, tag='pn')), KEEP_VID, vfail=['pinned'])
'''),
    ("case('V_missing', run_eval(good, str(good / 'no_such_vsn113.json'), str(good / 'no_such_glitch.txt')), PENDING,\n",
     "case('V_missing', run_eval(good, str(good / 'no_such_vtt114.json'), str(good / 'no_such_glitch.txt')), PENDING,\n"),
    (r'''# ... and the 94362eae build's eighteen x counters (session 111's eight daslot, session 112's two daguard, session
# 113's eight bdanarrow), each alone
''',
     r'''# ... and the x counters since session 111 (eight daslot, two daguard, eight bdanarrow, bda_nrace and the three
# priority counters of session 113, the eight title / reserve-wait / hold / main-task counters of 916f6489), each alone
'''),
    ("     check=lambda o: o['field_origin_defects'] == {'bda_scan': ['draw', 'x']})\n",
     "     check=lambda o: o['field_origin_defects'] == {'bda_scan': ['draw', 'x']})\n"
     "# the title wall printed on the draw row too\n"
     "case('FIELD_ORIGIN_title', run_eval(make('origintitle', row=setter(pick=lambda n, b, a, i: n == 1750,\n"
     "                                                                   edits={'draw': {'pres_title_ns': 0}}))),\n"
     "     KEEP_NA, fails={'integrity:FIELD_ORIGIN'},\n"
     "     check=lambda o: o['field_origin_defects'] == {'pres_title_ns': ['draw', 'x']})\n"),
    ("case('NO_RECORDING', run_eval(variant(good, 'recording', append=['Recording: C:/kyty/s113/rec_shn113.mp4 960x540'])),\n",
     "case('NO_RECORDING', run_eval(variant(good, 'recording', append=['Recording: C:/kyty/s114/rec_ttl114.mp4 960x540'])),\n"),
    ("     check=lambda o: o['markers']['fatal'] == {} and o['markers']['hang'] == 0)\n",
     "     check=lambda o: o['markers']['fatal'] == {} and o['markers']['hang'] == 0)\n"
     "# the 916f6489 build's title / hold / main-task lines (and session 113's priority lines) are not markers either\n"
     "TITLE_LINES = ['MainThreadWait: us=2975123', 'MainTaskLate: us=2975000',\n"
     "               'FlipHold: us=3001000 present_us=900 poll_us=100 other_us=3000000',\n"
     "               'PriorityStall: us=2975000 site=sync', 'GpuIdlePrio: ops=1']\n"
     "case('TITLE_LINES_not_marker', run_eval(variant(good, 'titlelines', append=TITLE_LINES, stdout=TITLE_LINES)),\n"
     "     PENDING, check=lambda o: o['markers']['fatal'] == {} and o['markers']['hang'] == 0)\n"),
    (r'''# REGIME_OLD_ARM0: the run in the NEW regime (arm-0 bda_scan level 52, as arm 1's; P1 misses) ...
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
''',
     r'''# TITLE_COUNTED: UpdateTitle counted on the present thread in both arms (pres_title_n level >= 1).  The good run's
# level 1 in both arms passes; 1 on 79 of the 80 main-window rows of each block of one arm (row 50 0) - level 0.9875
# - fails alone (the per-call wall stays defined, 400 000 or 3 000 ns / 0.9875: TITLE_ARMED holds) ...
for a in (0, 1):
    case('TITLE_COUNTED_out%d' % a, run_eval(make('tcountout%d' % a, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a and i == 50, edits={'x': {'pres_title_n': 0}}))),
        KEEP_NA, fails=ARMING, arming=['TITLE_COUNTED'],
        check=lambda o, a=a: (o['arming']['title_n_levels'][a] == 79 / 80
                              and o['arming']['title_wall_per_call_ns'][a] == (400000.0, 3000.0)[a] / (79 / 80)))
    # ... counted only outside the main window (rows 0..9 9 calls, rows 10..89 1 on the odd rows and 0 on the even
    # ones: level 0.5, a full-block level would read 1.44): the level reads the main window only ...
    case('TITLE_COUNTED_lag%d' % a, run_eval(make('tcountlag%d' % a, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a and i is not None,
        edits={'x': {'pres_title_n': lambda n, b, arm, i: 9 if i < 10 else i % 2}}))),
        KEEP_NA, fails=ARMING, arming=['TITLE_COUNTED'],
        check=lambda o, a=a: o['arming']['title_n_levels'][a] == 0.5)
    # ... and a missing level (pres_title_n dropped on one main-window row of every block of the arm: no block mean
    # of it carries it) fails too, with SCHEMA - and with TITLE_ARMED BY CONSTRUCTION (title_wall_ns() has no per-call
    # wall without a call level)
    case('TITLE_COUNTED_none%d' % a, run_eval(make('tcountnone%d' % a, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a and i == 50, edits={'x': {'pres_title_n': None}}))),
        KEEP_NA, fails={'integrity:SCHEMA', 'control:ARMING'}, arming=['TITLE_ARMED', 'TITLE_COUNTED'],
        check=lambda o, a=a: (o['arming']['title_n_levels'][a] is None
                              and o['arming']['title_wall_per_call_ns'][a] is None
                              and o['schema_missing_fields'] == ['pres_title_n']))
# ... no call counted in arm 1 (level 0): TITLE_ARMED fails with it BY CONSTRUCTION - title_wall_ns() returns no
# per-call wall for a call level that is not positive (and must not divide by it); P2 has no value and misses
case('TITLE_COUNTED_zero1', run_eval(make('tcountzero1', tn1=0)), KEEP_NA, fails=ARMING,
     arming=['TITLE_ARMED', 'TITLE_COUNTED'],
     check=lambda o: (o['arming']['title_n_levels'] == [1.0, 0.0]
                      and o['arming']['title_wall_per_call_ns'] == [400000.0, None]
                      and o['predictions']['P2']['value'] is None and not o['predictions']['P2']['hit']))
# TITLE_ARMED: the candidate does not wait - its per-call wall at most TITLE_WALL_MAX_NS = 20 000 ns and strictly below
# today's.  The cap's edge: 20 000 ns a call passes (P2 20 us hits) ...
case('TITLE_ARMED_edge', run_eval(make('tarmededge', tns1=20000)), PENDING,
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [400000.0, 20000.0]
                      and pred_values(o, P2=20.0, hits=list(PRED_BANDS))))
# ... 20 001 fails alone (P2 20.001 misses) ...
case('TITLE_ARMED_out', run_eval(make('tarmedout', tns1=20001)), KEEP_NA, fails=ARMING, arming=['TITLE_ARMED'],
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [400000.0, 20001.0]
                      and pred_values(o, P2=20.001, hits=['P1', 'P3', 'P4', 'P5', 'P6', 'P7'])))
# ... strictly below today's: equal walls under the cap (15 000 ns a call in both arms) fail alone ...
case('TITLE_ARMED_equal', run_eval(make('tarmedeq', tns0=15000, tns1=15000)), KEEP_NA, fails=ARMING,
     arming=['TITLE_ARMED'], check=lambda o: o['arming']['title_wall_per_call_ns'] == [15000.0, 15000.0])
# ... 1 ns below today's passes (P1 15.001 us misses its band - report only) ...
case('TITLE_ARMED_below', run_eval(make('tarmedbelow', tns0=15001, tns1=15000)), PENDING,
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [15001.0, 15000.0]
                      and pred_values(o, P1=15.001, P2=15.0, hits=['P2', 'P3', 'P4', 'P5', 'P6', 'P7'])))
# ... and today's arm faster than the candidate (3 000 against 15 000 ns a call, both under the cap) fails alone
case('TITLE_ARMED_arm0_faster', run_eval(make('tarmedfast0', tns0=3000, tns1=15000)), KEEP_NA, fails=ARMING,
     arming=['TITLE_ARMED'], check=lambda o: o['arming']['title_wall_per_call_ns'] == [3000.0, 15000.0])
# the wall is PER CALL: two calls a flip in both arms, arm 0 800 000 ns (400 000 a call), arm 1 30 000 ns (15 000 a
# call, the raw level above the cap) - passes; P1 400, P2 15 ...
case('TITLE_ARMED_percall', run_eval(make('tarmedpc', tn0=2, tn1=2, tns0=800000, tns1=30000)), PENDING,
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [400000.0, 15000.0]
                      and o['arming']['title_n_levels'] == [2.0, 2.0]
                      and pred_values(o, P1=400.0, P2=15.0, hits=list(PRED_BANDS))))
# ... and 40 002 ns over two calls (20 001 a call) fails alone
case('TITLE_ARMED_percall_out', run_eval(make('tarmedpcout', tn0=2, tn1=2, tns0=800000, tns1=40002)), KEEP_NA,
     fails=ARMING, arming=['TITLE_ARMED'],
     check=lambda o: o['arming']['title_wall_per_call_ns'] == [400000.0, 20001.0])
# the main window only: arm-1 rows 0..9 (the flips that straddle the arm change) 2 000 000 ns, rows 10..89 3 000 (a
# full-block level would read 224 889: above the cap) - pending ...
case('TITLE_ARMED_lag1', run_eval(make('tarmedlag1', row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None,
    edits={'x': {'pres_title_ns': lambda n, b, a, i: 3000 if i in MAIN else 2000000}}))), PENDING,
    check=lambda o: o['arming']['title_wall_per_call_ns'] == [400000.0, 3000.0])
# ... arm-0 rows 0..9 0 ns, rows 10..89 3 100 (a full-block level would read 2 756: below arm 1's 3 000) - pending
case('TITLE_ARMED_lag0', run_eval(make('tarmedlag0', row=setter(
    pick=lambda n, b, a, i: a == 0 and i is not None,
    edits={'x': {'pres_title_ns': lambda n, b, a, i: 3100 if i in MAIN else 0}}))), PENDING,
    check=lambda o: o['arming']['title_wall_per_call_ns'] == [3100.0, 3000.0])
# a missing level (pres_title_ns dropped on one main-window row of every block of one arm) fails alone, with SCHEMA
for a in (0, 1):
    case('TITLE_ARMED_none%d' % a, run_eval(make('tarmednone%d' % a, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a and i == 50, edits={'x': {'pres_title_ns': None}}))),
        KEEP_NA, fails={'integrity:SCHEMA', 'control:ARMING'}, arming=['TITLE_ARMED'],
        check=lambda o, a=a: (o['arming']['title_wall_per_call_ns'][a] is None
                              and o['arming']['title_n_levels'] == [1.0, 1.0]
                              and o['schema_missing_fields'] == ['pres_title_ns']))
# the level edges: pres_title_n 1 (the good run's), da_q_free 1 and cspfree_hit 1 in both arms - every arming check
# holds
case('ARMED_edge', run_eval(make('armededge', qfree0=1, qfree1=1, hit0=1, hit1=1)), PENDING,
     check=lambda o: (o['arming']['title_n_levels'] == [1.0, 1.0] and o['arming']['da_q_free_levels'] == [1.0, 1.0]
                      and o['arming']['cspfree_hit_levels'] == [1.0, 1.0]
                      and pred_values(o, hits=list(PRED_BANDS))))
'''),
    (r'''case('ENV_EXTRA', run_eval(make('envx', extra_env={'KYTY_SOMETHING_ELSE': '1'})), KEEP_NA, fails={'protocol'},
     errors=['env carries KYTY_* variables outside'])
''',
     r'''case('ENV_EXTRA', run_eval(make('envx', extra_env={'KYTY_SOMETHING_ELSE': '1'})), KEEP_NA, fails={'protocol'},
     errors=['env carries KYTY_* variables outside'])
# the knob, the stall test of pred/01 and session 113's GC trigger shift are all outside the sealed launch (the knob
# belongs to the schedule, the stall test to ctl114, the shift to shn113)
for key, value in (('KYTY_TITLE_ASYNC', '1'), ('KYTY_MAIN_STALL_TEST', '3000:3000'),
                   ('KYTY_BUFFER_GC_TRIGGER_SHIFT_MB', '1024')):
    case('ENV_EXTRA_%s' % key[5:].lower(), run_eval(variant(good, 'envx_%s' % key.lower(), env_set(key, value))),
         KEEP_NA, fails={'protocol'}, errors=['env carries KYTY_* variables outside'])
'''),
    ("fake_exe.write_bytes(b'not the 94362eae build')\n", "fake_exe.write_bytes(b'not the 916f6489 build')\n"),
    ("     'PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and size into shn113.py (only --draft runs '\n",
     "     'PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and size into ttl114.py (only --draft runs '\n"),
    (r'''# the tag pattern: shn113 with the optional b and _entry1 reaches evaluate() (no files under that tag here: INPUTS,
# protocol and IDENTITY fail, rc 1 - not the refusal's rc 2) ...
for t in ('shn113b', 'shn113_entry1', 'shn113b_entry1'):
''',
     r'''# the tag pattern: ttl114 with the optional b and _entry1 reaches evaluate() (no files under that tag here: INPUTS,
# protocol and IDENTITY fail, rc 1 - not the refusal's rc 2) ...
for t in ('ttl114b', 'ttl114_entry1', 'ttl114b_entry1'):
'''),
    (r'''# ... and every other tag is refused with the full message, session 112's tags and the video tags included
for t in ('shn114', 'shn112', 'net112', 'net112b', 'net112_entry1', 'vsn113', 'vbn113', 'vnet112', 'shn113c',
          'xshn113'):
''',
     r'''# ... and every other tag is refused with the full message, session 113's tags, the control's and the video's included
for t in ('ttl115', 'ttl113', 'shn113', 'shn113b', 'shn113_entry1', 'ctl114a', 'ctl114b', 'vtt114', 'ttl114c',
          'xttl114'):
'''),
    (r'''    if c['name'] in ('PENDING', 'S2_only', 'S1_edge', 'S1_edge_in', 'S1_only', 'SE_exact', 'KEEP_edge',
                     'SEC_edge', 'EST_rows0_9', 'EST_rows10_59', 'EST_rows10_59_ship', 'LEVEL_median'):
''',
     r'''    if c['name'] in ('PENDING', 'S2_only', 'S1_edge', 'S1_edge_in', 'S1_only', 'S2_edge', 'S2_edge_out', 'SE_exact',
                     'KEEP_edge', 'SEC_edge', 'EST_rows0_9', 'EST_rows10_59', 'EST_rows10_59_ship', 'LEVEL_median'):
'''),
    (r'''        print('   LEVEL case: dt arm0 %s arm1 %s, bda_scan arm0 %s arm1 %s, bda_nskip arm1 %s'
              % ((lv.get('arm0') or {}).get('dt_us'), (lv.get('arm1') or {}).get('dt_us'),
                 (lv.get('arm0') or {}).get('bda_scan'), (lv.get('arm1') or {}).get('bda_scan'),
                 (lv.get('arm1') or {}).get('bda_nskip')))
''',
     r'''        print('   LEVEL case: dt arm0 %s arm1 %s, pres_title_ns arm0 %s arm1 %s, pres_title_n arm1 %s'
              % ((lv.get('arm0') or {}).get('dt_us'), (lv.get('arm1') or {}).get('dt_us'),
                 (lv.get('arm0') or {}).get('pres_title_ns'), (lv.get('arm1') or {}).get('pres_title_ns'),
                 (lv.get('arm1') or {}).get('pres_title_n')))
'''),
], forbidden=('bdanarrow_1', 'vsn113', "case('REGIME", "case('NARROW", "case('NO_CHECK", "case('NO_XTHR",
              'S1_dt_le_-100', 'excludes_0', 'shift=', 's106_stage', "'shifted'", 'scan0', 'nskip1'))


# =====================================================================================================================
# the mutants
# =====================================================================================================================
TITLE_MUTANTS = (
    head('# ---- arming: TITLE_COUNTED (session 114; the pres_title_n level in both arms) ') +
    r'''TC = "checks['TITLE_COUNTED'] = bool((tn[0] or 0) >= 1 and (tn[1] or 0) >= 1)"
mutant('TITLE_COUNTED_off', TC, "checks['TITLE_COUNTED'] = True")
mutant('TITLE_COUNTED_arm0_unchecked', TC, "checks['TITLE_COUNTED'] = bool((tn[1] or 0) >= 1)")
mutant('TITLE_COUNTED_arm1_unchecked', TC, "checks['TITLE_COUNTED'] = bool((tn[0] or 0) >= 1)")
mutant('TITLE_COUNTED_gt1', TC, "checks['TITLE_COUNTED'] = bool((tn[0] or 0) > 1 and (tn[1] or 0) > 1)")
mutant('TITLE_COUNTED_gt0', TC, "checks['TITLE_COUNTED'] = bool((tn[0] or 0) > 0 and (tn[1] or 0) > 0)")
mutant('TITLE_COUNTED_ge_half', TC, "checks['TITLE_COUNTED'] = bool((tn[0] or 0) >= 0.5 and (tn[1] or 0) >= 0.5)")
mutant('TITLE_COUNTED_none_passes', TC,
       "checks['TITLE_COUNTED'] = (tn[0] is None or tn[0] >= 1) and (tn[1] is None or tn[1] >= 1)")
mutant('TITLE_COUNTED_all_rows', TC, "checks['TITLE_COUNTED'] = all(sum(r.get('pres_title_n', 0) for r in "
       "rows.values() if r.get('arm') == a) >= 1 for a in (0, 1))")
TL = "tn = [lev[a].get('pres_title_n') for a in (0, 1)]"
mutant('TITLE_COUNTED_reads_ns', TL, "tn = [lev[a].get('pres_title_ns') for a in (0, 1)]")
mutant('TITLE_COUNTED_reads_mt', TL, "tn = [lev[a].get('mt_n') for a in (0, 1)]")
mutant('TITLE_COUNTED_reads_rsv', TL, "tn = [lev[a].get('flip_rsv_wait_n') for a in (0, 1)]")
mutant('TITLE_n_arms_swapped', TL, "tn = [lev[a].get('pres_title_n') for a in (1, 0)]")
''' +
    head('# ---- arming: TITLE_ARMED (session 114; the per-call wall of UpdateTitle: cap and strictly below arm 0) ') +
    r'''mutant('TITLE_ARMED_off', "    checks['TITLE_ARMED'] = (walls[0]", "    checks['TITLE_ARMED'] = True or (walls[0]")
mutant('TITLE_ARMED_cap_unchecked', "walls[1] is not None and walls[1] <= TITLE_WALL_MAX_NS", "walls[1] is not None")
mutant('TITLE_ARMED_cap_strict', "walls[1] <= TITLE_WALL_MAX_NS", "walls[1] < TITLE_WALL_MAX_NS")
mutant('TITLE_ARMED_cap_on_arm0', "walls[1] <= TITLE_WALL_MAX_NS", "walls[0] <= TITLE_WALL_MAX_NS")
mutant('TITLE_ARMED_below_unchecked', "and walls[1] < walls[0])", "and True)")
mutant('TITLE_ARMED_below_le', "and walls[1] < walls[0])", "and walls[1] <= walls[0])")
mutant('TITLE_ARMED_below_ne', "and walls[1] < walls[0])", "and walls[1] != walls[0])")
mutant('TITLE_ARMED_none_passes',
       "checks['TITLE_ARMED'] = (walls[0] is not None and walls[1] is not None and walls[1]",
       "checks['TITLE_ARMED'] = walls[0] is None or walls[1] is None or (walls[1]")
mutant('TITLE_ARMED_all_rows', "    walls = [title_wall_ns(lev[a]) for a in (0, 1)]",
       "    walls = [sum(r.get('pres_title_ns', 0) for r in rows.values() if r.get('arm') == a) / max(1, sum("
       "r.get('pres_title_n', 0) for r in rows.values() if r.get('arm') == a)) for a in (0, 1)]")
mutant('TITLE_walls_swapped', "    walls = [title_wall_ns(lev[a]) for a in (0, 1)]",
       "    walls = [title_wall_ns(lev[a]) for a in (1, 0)]")
mutant('TITLE_WALL_MAX_19999', NL + 'TITLE_WALL_MAX_NS = 20000', NL + 'TITLE_WALL_MAX_NS = 19999')
mutant('TITLE_WALL_MAX_20001', NL + 'TITLE_WALL_MAX_NS = 20000', NL + 'TITLE_WALL_MAX_NS = 20001')
mutant('TITLE_WALL_MAX_in_us', NL + 'TITLE_WALL_MAX_NS = 20000', NL + 'TITLE_WALL_MAX_NS = 20')
mutant('TITLE_WALL_raw_ns', "    return ns / calls", "    return ns")
mutant('TITLE_WALL_zero_calls', "    if ns is None or calls is None or calls <= 0:", "    if ns is None or calls is None:")
mutant('TITLE_WALL_ns_unchecked', "    if ns is None or calls is None or calls <= 0:", "    if calls is None or calls <= 0:")
WN = "    ns, calls = level.get('pres_title_ns'), level.get('pres_title_n')"
mutant('TITLE_WALL_reads_mt', WN, "    ns, calls = level.get('mt_age_ns'), level.get('mt_n')")
mutant('TITLE_WALL_reads_hold', WN, "    ns, calls = level.get('flip_hold_ns'), level.get('flip_hold_n')")
mutant('TITLE_WALL_reads_rsv', WN, "    ns, calls = level.get('flip_rsv_wait_ns'), level.get('flip_rsv_wait_n')")
''')

derive('mut_shn113.py', [
    (r'''"""Session 113: mutation check of shn113.py against test_shn113.py, derived from session 112's mut_net112.py by
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
"""
''',
     r'''"""Session 114: mutation check of ttl114.py against test_ttl114.py, derived from session 113's sealed mut_shn113.py by
make_ttl114.py (whole-line anchored replacements).  Each mutant disables or weakens ONE admission / decision term,
verdict branch, prediction, schema entry, marker, sealed constant, estimator window, threshold or refusal of main()
(anchored replace, asserted to match exactly once).  Included: every mutant of mut_shn113.py that still applies
(re-anchored where the text changed: the rule S1 d mean <= +50 / S2 d mean + 2SE <= +200 with its edges, the video
gate text, the sealed constants, tags and texts on ttl114, P1-P7, the quoted size and the claims), and the session-114
changes: TITLE_COUNTED and TITLE_ARMED (off, one arm or one clause dropped, arms swapped, threshold and constant edges,
strict against non-strict, per call against per flip, the main window against all rows, missing levels, other
counters read), the eight new FrameTrace-x counters in the schema (each out, two moved to another line), the GC
trigger shift and the knob out of the launch and the video, S2's own bar, d flip_rsv_wait_ns in the pair keys and the
report, the title / hold / main-task lines as non-markers.  Dropped with the code they mutated (no anchor left):
session 113's REGIME_* / SCAN_arms_swapped, NARROW_*, NO_CHECK_*, NO_XTHR_*, VIDEO_shift_off, ENV_shift_*, the
bda_scan / bda_nskip P1 / P2 / P6 mutants (P2 has no lower bound now), PRED_P4_text_medium and CLAIM_dropped.  The two
draft-only seal mutants (CONST_pred_sha_prefilled, CONST_pred_bytes_prefilled) apply to this draft.  Run by the frozen
mutlib v2 (docs/session-113/mutlib/v2/mutlib.py --control --no-memo); the loop below is the legacy harness: each
mutant runs the full fixture suite in its own fixture directory (C:/kyty/s114/ttl114_draft/ttl114/fx_mut/w<k>, removed
at the end); a mutant is KILLED when the suite does not print ALL OK.  The unmutated scorer runs first in the same
harness and must print ALL OK.
    python mut_ttl114.py [<workers>]
"""
'''),
    (r'''HERE = Path('C:/kyty/s106_stage')
SCORER = HERE / 'shn113.py'
TEST = HERE / 'test_shn113.py'
MUT = HERE / 'shn113' / 'mutants'
FX = HERE / 'shn113' / 'fx_mut'
''',
     r'''HERE = Path('C:/kyty/s114/ttl114_draft')
SCORER = HERE / 'ttl114.py'
TEST = HERE / 'test_ttl114.py'
MUT = HERE / 'ttl114' / 'mutants'
FX = HERE / 'ttl114' / 'fx_mut'
'''),
    (r'''mutant('S1_off', "'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,", "'S1_dt_le_-100': True,")
mutant('S1_bar_+50', "dt['mean'] <= SHIP_US,", "dt['mean'] <= SHIP_US + 50,")
mutant('S2_off', "'S2_dt_2se_excludes_0': (dt['mean'] is not None and dt['se'] is not None" + NL
       + "                                 and dt['mean'] + 2 * dt['se'] < 0),", "'S2_dt_2se_excludes_0': True,")
mutant('S2_1se', "and dt['mean'] + 2 * dt['se'] < 0)", "and dt['mean'] + 1 * dt['se'] < 0)")
''',
     r'''mutant('S1_off', "'S1_dt_le_+50': dt['mean'] is not None and dt['mean'] <= SHIP_US,", "'S1_dt_le_+50': True,")
mutant('S1_bar_+50', "dt['mean'] <= SHIP_US,", "dt['mean'] <= SHIP_US + 50,")
mutant('S2_off', "'S2_dt_2se_le_+200': (dt['mean']", "'S2_dt_2se_le_+200': True or (dt['mean']")
mutant('S2_1se', "and dt['mean'] + 2 * dt['se'] <= S2_US)", "and dt['mean'] + 1 * dt['se'] <= S2_US)")
'''),
    (r'''GATE = "' dawalk=1 ' in gates and ' bdanarrow=1 ' in gates,"
mutant('VIDEO_gate_narrow_off', GATE, "' dawalk=1 ' in gates,")
mutant('VIDEO_gate_dawalk_off', GATE, "' bdanarrow=1 ' in gates,")
mutant('VIDEO_gate_is_arm0', GATE, "' dawalk=1 ' in gates and ' bdanarrow=0 ' in gates,")
mutant('VIDEO_gate_any_mode', GATE, "' dawalk=1 ' in gates and ' bdanarrow=' in gates,")
mutant('VIDEO_gate_is_net112', GATE, "' dawalk=1 ' in gates and ' daslot=0 ' in gates and ' daguard=0 ' in gates,")
''',
     r'''GATE = "' dawalk=1 ' in gates and ' titleasync=1 ' in gates,"
mutant('VIDEO_gate_title_off', GATE, "' dawalk=1 ' in gates,")
mutant('VIDEO_gate_dawalk_off', GATE, "' titleasync=1 ' in gates,")
mutant('VIDEO_gate_is_arm0', GATE, "' dawalk=1 ' in gates and ' titleasync=0 ' in gates,")
mutant('VIDEO_gate_any_mode', GATE, "' dawalk=1 ' in gates and ' titleasync=' in gates,")
mutant('VIDEO_gate_is_shn113', GATE, "' dawalk=1 ' in gates and ' bdanarrow=1 ' in gates,")
'''),
    (r'''mutant('VIDEO_shift_off', "'shifted': env.get('KYTY_BUFFER_GC_TRIGGER_SHIFT_MB') == '1024',", "'shifted': True,")
mutant('ENV_shift_drop', ", 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '1024'}", "}")
mutant('ENV_shift_value', "'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '1024'}", "'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '512'}")
''',
     r'''mutant('VIDEO_shift_required', "        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1'," + NL,
       "        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1'," + NL
       + "        'shifted': env.get('KYTY_BUFFER_GC_TRIGGER_SHIFT_MB') == '1024'," + NL)
mutant('ENV_shift_readded', "'KYTY_GPU_MARKERS': '0'}", "'KYTY_GPU_MARKERS': '0', 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '1024'}")
mutant('ENV_title_in_launch', "'KYTY_GPU_MARKERS': '0'}", "'KYTY_GPU_MARKERS': '0', 'KYTY_TITLE_ASYNC': '1'}")
'''),
    (r'''mutant('SHIP_bar_-99', 'SHIP_US = -100.0', 'SHIP_US = -99.0')
mutant('SHIP_bar_-101', 'SHIP_US = -100.0', 'SHIP_US = -101.0')
''',
     r'''mutant('SHIP_bar_+50.5', 'SHIP_US = 50.0', 'SHIP_US = 50.5')
mutant('SHIP_bar_+49.5', 'SHIP_US = 50.0', 'SHIP_US = 49.5')
mutant('SHIP_bar_-100', 'SHIP_US = 50.0', 'SHIP_US = -100.0')             # session 113's bar
mutant('S2_bar_+200.5', 'S2_US = 200.0', 'S2_US = 200.5')
mutant('S2_bar_+199.5', 'S2_US = 200.0', 'S2_US = 199.5')
mutant('S2_bar_0', 'S2_US = 200.0', 'S2_US = 0.0')                        # session 113's S2 edge
mutant('S2_reads_ship_bar', "and dt['mean'] + 2 * dt['se'] <= S2_US)", "and dt['mean'] + 2 * dt['se'] <= SHIP_US)")
'''),
    (dash('# ---- arming: REGIME_OLD_ARM0 (session 113; the arm-0 level of bda_scan) ', 45) +
     r'''RG = "checks['REGIME_OLD_ARM0'] = scan[0] is not None and scan[0] >= REGIME_OLD_SCAN"
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
''' + dash('# ---- arming: NARROW_ARMED_ARM1 / NARROW_DARK_ARM0 (bda_nskip) ', 58) +
     r'''NA = "checks['NARROW_ARMED_ARM1'] = bool((lev[1].get('bda_nskip') or 0) >= 1)"
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
''' + dash('# ---- arming: NARROW_SCAN_ARM1 (the arm-1 level of bda_scan) ', 60) +
     r'''NS = "checks['NARROW_SCAN_ARM1'] = scan[1] is not None and scan[1] <= NARROW_SCAN_MAX"
mutant('NARROW_SCAN_off', NS, "checks['NARROW_SCAN_ARM1'] = True")
mutant('NARROW_SCAN_arm0', NS, "checks['NARROW_SCAN_ARM1'] = scan[0] is not None and scan[0] <= NARROW_SCAN_MAX")
mutant('NARROW_SCAN_lt', NS, "checks['NARROW_SCAN_ARM1'] = scan[1] is not None and scan[1] < NARROW_SCAN_MAX")
mutant('NARROW_SCAN_none_passes', NS, "checks['NARROW_SCAN_ARM1'] = scan[1] is None or scan[1] <= NARROW_SCAN_MAX")
mutant('NARROW_SCAN_all_arm1_rows', NS, "checks['NARROW_SCAN_ARM1'] = statistics.fmean(r['bda_scan'] for r in "
       "rows.values() if r.get('arm') == 1 and 'bda_scan' in r) <= NARROW_SCAN_MAX")
mutant('NARROW_SCAN_199', NL + 'NARROW_SCAN_MAX = 200', NL + 'NARROW_SCAN_MAX = 199')
mutant('NARROW_SCAN_201', NL + 'NARROW_SCAN_MAX = 200', NL + 'NARROW_SCAN_MAX = 201')
''' + dash('# ---- arming: NO_CHECK / NO_XTHR (sums over ALL rows) ', 67) +
     r'''NC = "checks['NO_CHECK'] = would == 0 and miss == 0"
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
''',
     TITLE_MUTANTS),
    (r'''            'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict', 'bda_nrace', 'prio_unsub', 'prio_stall',
            'gw_idle_prio'):
''',
     r'''            'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict', 'bda_nrace', 'prio_unsub', 'prio_stall',
            'gw_idle_prio', 'pres_title_ns', 'pres_title_n', 'flip_rsv_wait_ns', 'flip_rsv_wait_n', 'flip_hold_ns',
            'flip_hold_n', 'mt_age_ns', 'mt_n'):
'''),
    ("mutant('SCHEMA_scan_on_x', \"'bda_scan': 'draw',\", \"'bda_scan': 'x',\")\n",
     "mutant('SCHEMA_scan_on_x', \"'bda_scan': 'draw',\", \"'bda_scan': 'x',\")\n"
     "mutant('SCHEMA_title_ns_on_draw', \"'pres_title_ns': 'x',\", \"'pres_title_ns': 'draw',\")\n"
     "mutant('SCHEMA_title_n_on_main', \"'pres_title_n': 'x',\", \"'pres_title_n': 'main',\")\n"),
    (r'''mutant('CONST_root_s112', "PRODUCTION_ROOT = 'C:/kyty/s113'", "PRODUCTION_ROOT = 'C:/kyty/s112'")
mutant('CONST_pred_net112', "PRED = 'C:/kyty/s113/pred/02_shn113.md'", "PRED = 'C:/kyty/s112/pred/02_net112.md'")
''',
     r'''mutant('CONST_root_s113', "PRODUCTION_ROOT = 'C:/kyty/s114'", "PRODUCTION_ROOT = 'C:/kyty/s113'")
mutant('CONST_pred_shn113', "PRED = 'C:/kyty/s114/pred/02_ttl114.md'", "PRED = 'C:/kyty/s113/pred/02_shn113.md'")
mutant('CONST_pred_ctl114', "PRED = 'C:/kyty/s114/pred/02_ttl114.md'", "PRED = 'C:/kyty/s114/pred/01_ctl114.md'")
'''),
    (r'''mutant('CONST_binary_b47b58a9', "BINARY_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'",
       "BINARY_SHA = 'b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7'")
mutant('CONST_gates_s112', "GATES_FILE = 'C:/kyty/s113/gates_base.txt'", "GATES_FILE = 'C:/kyty/s112/gates_base.txt'")
ARMS_NOW = "ARMS = ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=1')"
mutant('CONST_arms_swapped', ARMS_NOW, "ARMS = ('dawalk=1 dawalklead=1 bdanarrow=1', 'dawalk=1 dawalklead=1 bdanarrow=0')")
mutant('CONST_arms_net112', ARMS_NOW,
       "ARMS = ('dawalk=1 dawalklead=1 daslot=1 daguard=1', 'dawalk=1 dawalklead=1 daslot=0 daguard=0')")
mutant('CONST_arms_mode2', ARMS_NOW, "ARMS = ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=2')")
''',
     r'''mutant('CONST_binary_1678d3f4', "BINARY_SHA = '916f64898a5a31c697ad0d823f0795850acc160cf56271b566e8ae330c7c3b2c'",
       "BINARY_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'")
mutant('CONST_gates_s113', "GATES_FILE = 'C:/kyty/s114/gates_base.txt'", "GATES_FILE = 'C:/kyty/s113/gates_base.txt'")
ARMS_NOW = "ARMS = ('dawalk=1 dawalklead=1 titleasync=0', 'dawalk=1 dawalklead=1 titleasync=1')"
mutant('CONST_arms_swapped', ARMS_NOW, "ARMS = ('dawalk=1 dawalklead=1 titleasync=1', 'dawalk=1 dawalklead=1 titleasync=0')")
mutant('CONST_arms_shn113', ARMS_NOW,
       "ARMS = ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=1')")
mutant('CONST_arms_mode2', ARMS_NOW, "ARMS = ('dawalk=1 dawalklead=1 titleasync=0', 'dawalk=1 dawalklead=1 titleasync=2')")
'''),
    (r'''TAG_NOW = "TAG_RE = r'shn113b?(?:_entry1)?'"
mutant('TAG_accepts_net112', TAG_NOW, "TAG_RE = r'(?:shn113|net112)b?(?:_entry1)?'")
mutant('TAG_accepts_vsn113', TAG_NOW, "TAG_RE = r'(?:shn113|vsn113)b?(?:_entry1)?'")
mutant('TAG_no_b', TAG_NOW, "TAG_RE = r'shn113(?:_entry1)?'")
mutant('TAG_no_entry1', TAG_NOW, "TAG_RE = r'shn113b?'")
''',
     r'''TAG_NOW = "TAG_RE = r'ttl114b?(?:_entry1)?'"
mutant('TAG_accepts_shn113', TAG_NOW, "TAG_RE = r'(?:ttl114|shn113)b?(?:_entry1)?'")
mutant('TAG_accepts_vtt114', TAG_NOW, "TAG_RE = r'(?:ttl114|vtt114)b?(?:_entry1)?'")
mutant('TAG_accepts_ctl114', TAG_NOW, "TAG_RE = r'(?:ttl114|ctl114)[ab]?(?:_entry1)?'")
mutant('TAG_no_b', TAG_NOW, "TAG_RE = r'ttl114(?:_entry1)?'")
mutant('TAG_no_entry1', TAG_NOW, "TAG_RE = r'ttl114b?'")
'''),
    (r'''mutant('TAG_msg_old', "(shn113, shn113b, optional _entry1)", "(net112, net112b, optional _entry1)")
''',
     r'''mutant('TAG_msg_old', "(ttl114, ttl114b, optional _entry1)", "(shn113, shn113b, optional _entry1)")
'''),
    (r'''mutant('SEAL_msg_old', "size into shn113.py (only --draft", "size into net112.py (only --draft")
mutant('PENDING_text_old', "nothing ships until vsn113 is read", "nothing changes until vnet112 is read")
mutant('PENDING_name_old', "'SHIP_PENDING_VIDEO (", "'REVERT_PENDING_VIDEO (")
mutant('VERDICT_na_old', "'KEEP bdanarrow=0 (run not admitted)'", "'KEEP daslot=1 (run not admitted)'")
mutant('VERDICT_bar_old', "'KEEP bdanarrow=0 (ship rule S1-S2 on mean dt not met)'",
       "'KEEP daslot=1 (revert rule S1-S2 on mean dt not met)'")
mutant('VERDICT_ship_old', "'SHIP bdanarrow=1 as the new default", "'REVERT to daslot=0 daguard=0 as the new default")
mutant('VERDICT_video_old', "'KEEP bdanarrow=0 (video pass failed)'", "'KEEP daslot=1 (video pass failed)'")
mutant('SCORER_name_old', "out = {'scorer': 'shn113.py',", "out = {'scorer': 'net112.py',")
mutant('SUMMARY_name_old', "lines = ['shn113.py %s status=%s seal=%s'", "lines = ['net112.py %s status=%s seal=%s'")
''',
     r'''mutant('SEAL_msg_old', "size into ttl114.py (only --draft", "size into shn113.py (only --draft")
mutant('PENDING_text_old', "nothing ships until vtt114 is read", "nothing ships until vsn113 is read")
mutant('PENDING_name_old', "'SHIP_PENDING_VIDEO (", "'REVERT_PENDING_VIDEO (")
mutant('PENDING_knob_dropped', "(titleasync=1: S1-S2 met;", "(S1-S2 met;")
mutant('VERDICT_na_old', "'KEEP titleasync=0 (run not admitted)'", "'KEEP bdanarrow=0 (run not admitted)'")
mutant('VERDICT_bar_old', "'KEEP titleasync=0 (ship rule S1-S2 on mean dt not met)'",
       "'KEEP bdanarrow=0 (ship rule S1-S2 on mean dt not met)'")
mutant('VERDICT_ship_old', "'SHIP titleasync=1 as the new default", "'SHIP bdanarrow=1 as the new default")
mutant('VERDICT_ship_ctl_dropped', "its video pass is owed; ctl114 must read PASS)'", "its video pass is owed)'")
mutant('VERDICT_video_old', "'KEEP titleasync=0 (video pass failed)'", "'KEEP bdanarrow=0 (video pass failed)'")
mutant('SCORER_name_old', "out = {'scorer': 'ttl114.py',", "out = {'scorer': 'shn113.py',")
mutant('SUMMARY_name_old', "lines = ['ttl114.py %s status=%s seal=%s'", "lines = ['shn113.py %s status=%s seal=%s'")
'''),
    (r'''P1 = "lev[0].get('bda_scan'), 800, 1400)"
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
''',
     r'''P1 = "us[0], 20, 5000)"
P2 = "us[1], None, 20)"
P3 = "stats['dt_us']['mean'], -500, 100)"
P4 = "stats['dt_us']['mean'], None, 0)"
P5 = "stats['gpu_busy_us']['mean'], -150, 150)"
P6 = "stats['flip_rsv_wait_ns']['mean'], None, 0)"
P7 = "stats['da_miss']['mean'], -40, 40)"
mutant('PRED_P1_named_N1', "add('P1',", "add('N1',")
mutant('PRED_P1_arm1', P1, "us[1], 20, 5000)")
mutant('PRED_P1_lo_19', P1, "us[0], 19, 5000)")
mutant('PRED_P1_lo_21', P1, "us[0], 21, 5000)")
mutant('PRED_P1_hi_4999', P1, "us[0], 20, 4999)")
mutant('PRED_P1_hi_5001', P1, "us[0], 20, 5001)")
mutant('PRED_P1_unbounded_hi', P1, "us[0], 20, None)")
mutant('PRED_P2_arm0', P2, "us[0], None, 20)")
mutant('PRED_P2_hi_19', P2, "us[1], None, 19)")
mutant('PRED_P2_hi_21', P2, "us[1], None, 21)")
mutant('PRED_P2_bounded', P2, "us[1], 1, 20)")
mutant('PRED_wall_in_ns', "w / 1000.0 for w in", "w for w in")
mutant('PRED_wall_raw_level', "(title_wall_ns(lev[0]), title_wall_ns(lev[1]))",
       "(lev[0].get('pres_title_ns'), lev[1].get('pres_title_ns'))")
mutant('PRED_wall_arms_swapped', "(title_wall_ns(lev[0]), title_wall_ns(lev[1]))",
       "(title_wall_ns(lev[1]), title_wall_ns(lev[0]))")
mutant('PRED_P3_lo_-501', P3, "stats['dt_us']['mean'], -501, 100)")
mutant('PRED_P3_lo_-499', P3, "stats['dt_us']['mean'], -499, 100)")
mutant('PRED_P3_hi_99', P3, "stats['dt_us']['mean'], -500, 99)")
mutant('PRED_P3_hi_101', P3, "stats['dt_us']['mean'], -500, 101)")
mutant('PRED_P3_hi_200', P3, "stats['dt_us']['mean'], -500, 200)")      # session 113's upper edge
mutant('PRED_P4_hi_-1', P4, "stats['dt_us']['mean'], None, -1)")
mutant('PRED_P4_hi_1', P4, "stats['dt_us']['mean'], None, 1)")
mutant('PRED_P4_hi_-100', P4, "stats['dt_us']['mean'], None, -100)")    # session 113's bar
mutant('PRED_P4_bounded', P4, "stats['dt_us']['mean'], -500, 0)")
mutant('PRED_P4_sign', P4, "-stats['dt_us']['mean'], None, 0)")
mutant('PRED_P5_reads_draws', P5, "stats['draws']['mean'], -150, 150)")
mutant('PRED_P5_lo_-151', P5, "stats['gpu_busy_us']['mean'], -151, 150)")
mutant('PRED_P5_lo_-149', P5, "stats['gpu_busy_us']['mean'], -149, 150)")
mutant('PRED_P5_hi_149', P5, "stats['gpu_busy_us']['mean'], -150, 149)")
mutant('PRED_P5_hi_151', P5, "stats['gpu_busy_us']['mean'], -150, 151)")
mutant('PRED_P6_level_arm1', P6, "lev[1].get('flip_rsv_wait_ns'), None, 0)")
mutant('PRED_P6_hi_-1', P6, "stats['flip_rsv_wait_ns']['mean'], None, -1)")
mutant('PRED_P6_hi_1', P6, "stats['flip_rsv_wait_ns']['mean'], None, 1)")
mutant('PRED_P6_bounded', P6, "stats['flip_rsv_wait_ns']['mean'], -1000, 0)")
mutant('PRED_P6_sign', P6, "-stats['flip_rsv_wait_ns']['mean'], None, 0)")
mutant('PRED_P6_in_us', P6, "stats['flip_rsv_wait_ns']['mean'] / 1000.0, None, 0)")
mutant('PRED_P6_text_unit', "<= 0 raw ns a flip (the per-row counter", "<= 0 us a flip (the per-row counter")
mutant('PRED_P7_reads_late', P7, "stats['da_late']['mean'], -40, 40)")
mutant('PRED_P7_lo_-41', P7, "stats['da_miss']['mean'], -41, 40)")
mutant('PRED_P7_lo_-39', P7, "stats['da_miss']['mean'], -39, 40)")
mutant('PRED_P7_hi_39', P7, "stats['da_miss']['mean'], -40, 39)")
mutant('PRED_P7_hi_41', P7, "stats['da_miss']['mean'], -40, 41)")
'''),
    (r'''mutant('SIZE_label', "SIZE_LABEL = 'bdanarrow=1 against bdanarrow=0 of build 1678d3f4, forced OLD (GC trigger -1024 MiB), main estimator'",
       "SIZE_LABEL = 'bdanarrow=1 against bdanarrow=0, main estimator'")
mutant('CLAIM_dropped', "a gain in the NEW regime or", "a gain or")
''',
     r'''mutant('SIZE_label', "SIZE_LABEL = 'titleasync=1 against titleasync=0 of build 916f6489, main estimator'",
       "SIZE_LABEL = 'titleasync=1 against titleasync=0, main estimator'")
mutant('CLAIM_stall_dropped', "'d cpu_net_us alone; that the 3-s stall of session 113 was the title wait (the '",
       "'d cpu_net_us alone; (the '")
mutant('CLAIM_additivity_dropped', "'control proves the knob, not the event); additivity')",
       "'control proves the knob, not the event)')")
mutant('CLAIM_60fps_dropped', "('60 FPS; a game-speed", "('a game-speed")
'''),
    ("mutant('S2_le0', \"and dt['mean'] + 2 * dt['se'] < 0)\", \"and dt['mean'] + 2 * dt['se'] <= 0)\")\n",
     "mutant('S2_strict', \"and dt['mean'] + 2 * dt['se'] <= S2_US)\", \"and dt['mean'] + 2 * dt['se'] < S2_US)\")\n"),
    ("mutant('VIDEO_frames_3001', 'VIDEO_MIN_FRAMES = 3000', 'VIDEO_MIN_FRAMES = 3001')\n",
     "mutant('VIDEO_frames_3001', 'VIDEO_MIN_FRAMES = 3000', 'VIDEO_MIN_FRAMES = 3001')\n"
     "\n"
     "# ==== session 114 " + '=' * 101 + "\n" +
     head('# ---- the title / hold / main-task lines are not markers ') +
     "mutant('FATAL_mainthreadwait', \"b'AsyncPipelines: skipped draw')\",\n"
     "       \"b'AsyncPipelines: skipped draw', b'MainThreadWait:')\")\n"
     "mutant('FATAL_maintasklate', \"b'AsyncPipelines: skipped draw')\", \"b'AsyncPipelines: skipped draw', b'MainTaskLate:')\")\n"
     "mutant('FATAL_fliphold', \"b'AsyncPipelines: skipped draw')\", \"b'AsyncPipelines: skipped draw', b'FlipHold:')\")\n" +
     head('# ---- d flip_rsv_wait_ns (P6) in the pair keys and the report; the title levels in the report and the summary ') +
     "mutant('PAIR_no_rsv', \"'da_walks', 'da_qcall', 'flip_rsv_wait_ns')\", \"'da_walks', 'da_qcall')\")\n"
     "mutant('REPORTED_rsv_d_dropped', \"'gpu_busy_us', 'draws', 'flip_rsv_wait_ns')}\", \"'gpu_busy_us', 'draws')}\")\n"
     "mutant('REPORTED_title_levels_dropped', \"    for k in ('pres_title_ns', 'pres_title_n', 'flip_rsv_wait_ns',\",\n"
     "       \"    for k in ('flip_rsv_wait_ns',\")\n"
     "mutant('SUMMARY_title_line', \"'  titleasync: pres_title_n levels %s  per-call wall %s ns\",\n"
     "       \"'  titleasync: levels %s  per-call wall %s ns\")\n"),
    ("        path = MUT / ('shn113_%s.py' % name)\n", "        path = MUT / ('ttl114_%s.py' % name)\n"),
], forbidden=('s106_stage', "'S1_dt_le_-100'", "mutant('REGIME_", "mutant('NARROW_", "mutant('NO_CHECK",
                 "mutant('NO_XTHR", "'shn113_%s.py'"))
