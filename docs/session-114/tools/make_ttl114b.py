"""Session 114, ROADMAP s0.1 "СЕССИЯ 114 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 8: the seal-02b scorer ttl114b derived from the
SEALED ttl114 files of seal 02 by WHOLE-LINE anchored replacements (each anchor asserted to end with a newline, to start
at a line start, to occur exactly once and to differ from its replacement; every new line at most 120 characters or no
longer than the line it replaces; the inputs pinned by their full sha256).
Inputs, read only: C:/kyty/s114/{ttl114.py, test_ttl114.py, mut_ttl114.py} - the sealed scorer and suite of seal 02
and the draft mutant list (mut_ttl114.py = mut_ttl114_sealed.py plus the two draft-only seal mutants
CONST_pred_sha_prefilled / CONST_pred_bytes_prefilled, which apply again because ttl114b is a draft with PRED_SHA /
PRED_BYTES None).  Outputs: C:/kyty/s114/ttl114b_draft/{ttl114b.py, test_ttl114b.py, mut_ttl114b.py}.
Byte-reproducible (LF, UTF-8).

Changes to the scorer, and nothing else: the docstring (a seal-02b header; the pre-registration, the usage lines and
the cap in ttl114's description); PRED C:/kyty/s114/pred/02b_ttl114b.md with PRED_SHA / PRED_BYTES back to None and
the draft comment '# filled by the executor when pred/02 is sealed'; TITLE_WALL_MAX_NS = 60000 (was 20000; comment s114
item 8); P2 'arm-1 per-call wall of UpdateTitle <= 60 us a call' with the band [None, 60] (was 20).  The rule S1 +50 /
S2 +200, the arming otherwise, the schema, the launch, the video pass, SIZE_LABEL, must_not_be_claimed, TAG_RE and the
messages (out['scorer'], the summary header, the seal and tag refusals: ttl114's names) are untouched.
Fixtures: every one tied to the 20 000-ns cap or to P2's 20-us band moved with its intent kept (see the suite's
docstring); CONSTANTS compares PRED = pred/02b_ttl114b.md.  Mutants: the ones on the cap / on P2 / on PRED re-anchored
(TITLE_WALL_MAX_19999 / _20001 / _in_us -> _59999 / _60001 / _in_us 60, PRED_P2_arm0 / _hi_19 / _hi_21 / _bounded ->
on 60 with _hi_59 / _hi_61, CONST_pred_shn113 / CONST_pred_ctl114 on the new PRED), three added with ttl114's own
values (TITLE_WALL_MAX_20000, PRED_P2_hi_20, CONST_pred_ttl114); every other mutant is checked to be byte-equal to
mut_ttl114.py's, and every anchor to occur exactly once in ttl114b.py.

    python C:/kyty/s114/ttl114b_draft/make_ttl114b.py
"""
import hashlib
from pathlib import Path

SRC = Path('C:/kyty/s114')
OUT = Path('C:/kyty/s114/ttl114b_draft')
PINS = {'ttl114.py': 'b8459c3df8a7fe87ff3198f2d45a24731505b8d539caa68372e755b480b45d2f',
        'test_ttl114.py': '0edede85ddb2b2cc0bc2d4681449af2c3a016f70a688918045ca3e68bb14731e',
        'mut_ttl114.py': '951783ba3025a990562e20afc7f56d999f5ef1e804a39b8247d8799c362454e8'}
NAMES = {'ttl114.py': 'ttl114b.py', 'test_ttl114.py': 'test_ttl114b.py', 'mut_ttl114.py': 'mut_ttl114b.py'}
WIDTH = 120


def load(name):
    raw = (SRC / name).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    assert got == PINS[name], (name, got)
    s = raw.decode('utf-8')
    assert '\r' not in s, (name, 'CR in the input')
    return s


def derive(src, pairs, forbidden=(), required=(), width=WIDTH):
    s = load(src)
    for a, b in pairs:
        assert a.endswith('\n') and b.endswith('\n'), (src, 'not whole lines', a[:80])
        assert s.startswith(a) or ('\n' + a) in s, (src, 'anchor not at a line start', a[:80])
        assert s.count(a) == 1, (src, a[:80], s.count(a))
        assert a != b, (src, 'changes nothing', a[:80])
        if width:
            limit = max([width] + [len(x) for x in a.splitlines()])
            for x in b.splitlines():
                assert len(x) <= limit, (src, 'line too long', x[:80])
        s = s.replace(a, b)
    for word in forbidden:
        assert word not in s, (src, 'left over', word)
    for word in required:
        assert s.count(word) == 1, (src, 'required once', word, s.count(word))
    compile(s, NAMES[src], 'exec')
    OUT.mkdir(parents=True, exist_ok=True)
    data = s.encode('utf-8')
    (OUT / NAMES[src]).write_bytes(data)
    print(NAMES[src], hashlib.sha256(data).hexdigest(), len(data))
    return s


# =====================================================================================================================
# the scorer
# =====================================================================================================================
SCORER = derive('ttl114.py', [
    ('"""Session 114, the ABBA `ttl114`: knob `titleasync` (KYTY_TITLE_ASYNC) - once the SDL main loop runs,\n',
     r'''"""Session 114, seal 02b (ROADMAP s0.1, the session-114 records, item 8): the ABBA `ttl114b` - the sealed ttl114.py
with its arming cap moved: TITLE_WALL_MAX_NS = 60 000 ns (was 20 000) in TITLE_ARMED and prediction P2 <= 60 us (was
20).  ttl114 read NOT_ADMITTED on TITLE_ARMED alone: the arm-1 per-call wall of UpdateTitle, 21 421 ns, above a cap
set without a measurement (arm 0's 168 468 ns).  60 000 ns - about 3x the one and 2.8x below the other - separates
"posts without waiting" from "waits for the SDL main thread"; "strictly below arm 0" stays.  The cap was chosen after
ttl114's walls and size were seen; the rule does not move, and the new independent run ttl114b decides.  The
protocol, the rule S1 / S2, the rest of the arming, the schema, the launch, the video pass, SIZE_LABEL and the claims
are ttl114's; the run tag is ttl114b (TAG_RE unchanged) and the messages keep ttl114's names.  Derived from the sealed
ttl114.py by make_ttl114b.py (whole-line anchored replacements; copied, not imported).  ttl114's description follows,
its pre-registration and its cap updated.

Session 114, the ABBA `ttl114`: knob `titleasync` (KYTY_TITLE_ASYNC) - once the SDL main loop runs,
'''),
    ("GC trigger shift, sealed to pred/02_ttl114.md.  Derived from session 113's sealed shn113.py by make_ttl114.py\n",
     "GC trigger shift, sealed to pred/02b_ttl114b.md.  Derived from session 113's sealed shn113.py by make_ttl114.py\n"),
    (r'''    python C:/kyty/s114/ttl114.py ttl114 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s114/ttl114.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)
''',
     r'''    python C:/kyty/s114/ttl114b.py ttl114b [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s114/ttl114b.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)
'''),
    ("TITLE_ARMED (the arm-1 per-call wall level(pres_title_ns) / level(pres_title_n) <= TITLE_WALL_MAX_NS = 20 000 ns "
     "and\n",
     "TITLE_ARMED (the arm-1 per-call wall level(pres_title_ns) / level(pres_title_n) <= TITLE_WALL_MAX_NS = 60 000 ns "
     "and\n"),
    (r'''PRED = 'C:/kyty/s114/pred/02_ttl114.md'
PRED_SHA = '02b11e8704e714296ebd6456fc84fe01c0603c18e83d65365f29667a4529286e'   # pred/02_ttl114.md sealed
PRED_BYTES = 4701        # pred/02_ttl114.md sealed
''',
     r'''PRED = 'C:/kyty/s114/pred/02b_ttl114b.md'
PRED_SHA = None          # filled by the executor when pred/02 is sealed
PRED_BYTES = None        # filled by the executor when pred/02 is sealed
'''),
    ("TITLE_WALL_MAX_NS = 20000  # the arm-1 per-call wall of UpdateTitle at or below it, ns a call (s114 item 5)\n",
     "TITLE_WALL_MAX_NS = 60000  # the arm-1 per-call wall of UpdateTitle at or below it, ns a call (s114 item 8)\n"),
    (r'''    add('P2', 'arm-1 per-call wall of UpdateTitle <= 20 us a call (titleasync=1 posts without waiting)',
        us[1], None, 20)
''',
     r'''    add('P2', 'arm-1 per-call wall of UpdateTitle <= 60 us a call (titleasync=1 posts without waiting)',
        us[1], None, 60)
'''),
], forbidden=('TITLE_WALL_MAX_NS = 20000', 'MAX_NS = 20 000 ns', 'UpdateTitle <= 20 us', 'us[1], None, 20)',
              'pred/02_ttl114.md', '02b11e8704e714296ebd', 'PRED_BYTES = 4701', 'ttl114.py ttl114 [',
              'ns a call (s114 item 5)'),
   required=("\nPRED = 'C:/kyty/s114/pred/02b_ttl114b.md'\n",
             '\nPRED_SHA = None          # filled by the executor when pred/02 is sealed\n',
             '\nPRED_BYTES = None        # filled by the executor when pred/02 is sealed\n',
             '\nTITLE_WALL_MAX_NS = 60000  # ', '\n        us[1], None, 60)\n', 'TITLE_WALL_MAX_NS = 60 000 ns and\n'))

# =====================================================================================================================
# the fixtures
# =====================================================================================================================
derive('test_ttl114.py', [
    ('"""Session 114: fixtures for ttl114.py (the ABBA of knob titleasync: today\'s titleasync=0 against the candidate\n',
     r'''"""Session 114, seal 02b (ROADMAP s0.1, the session-114 records, item 8): the fixtures of ttl114b.py, derived from the
sealed test_ttl114.py by make_ttl114b.py (whole-line anchored replacements).  ttl114b is ttl114 with the arm-1 cap
TITLE_WALL_MAX_NS = 60 000 ns (was 20 000) and P2 <= 60 us (was 20).  Every fixture tied to the cap or to P2's band
moved, its intent kept: PRED_BANDS P2 [None, 60]; TITLE_ARMED_edge / TITLE_ARMED_out 60 000 / 60 001 ns a call (P2 60
hits / 60.001 misses); TITLE_ARMED_percall 90 000 ns over two calls (45 000 a call: the raw level still above the
cap) and TITLE_ARMED_percall_out 120 002 (60 001 a call); PRED_edges_hi / PRED_misses_hi arm-1 walls 60 000 / 60 001
(P2 60 / 60.001); LEVEL_median's arm-1 outlier block 7 000 000 ns (a mean level would read 66 609.1 ns over 0.991
calls: above the cap, P2 missed); the summary's cap line (60000 ns); CONSTANTS' PRED (pred/02b_ttl114b.md).  The
fixture tag stays ttl114 (TAG_RE accepts ttl114b: TAG_ok_ttl114b).  test_ttl114.py's description follows, its cap
edges updated.

Session 114: fixtures for ttl114.py (the ABBA of knob titleasync: today's titleasync=0 against the candidate
'''),
    ('TITLE_ARMED (20 000 ns a call passes, 20 001 fails; equal walls fail, 1 ns below passes, arm 0 faster fails; per '
     'call,\n',
     'TITLE_ARMED (60 000 ns a call passes, 60 001 fails; equal walls fail, 1 ns below passes, arm 0 faster fails; per '
     'call,\n'),
    ('    python test_ttl114.py <ttl114.py> [<fixture dir>]\n',
     '    python test_ttl114b.py <ttl114b.py> [<fixture dir>]\n'),
    ("BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s114/ttl114_draft/fx')\n",
     "BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s114/ttl114b_draft/fx')\n"),
    ("PRED_BANDS = {'P1': [20, 5000], 'P2': [None, 20], 'P3': [-500, 100], 'P4': [None, 0], 'P5': [-150, 150],\n",
     "PRED_BANDS = {'P1': [20, 5000], 'P2': [None, 60], 'P3': [-500, 100], 'P4': [None, 0], 'P5': [-150, 150],\n"),
    (r'''            and ('  titleasync: pres_title_n levels [1.0, 1.0]  per-call wall [400000.0, 3000.0] ns (arm-1 cap '
                 '20000 ns)') in lines
''',
     r'''            and ('  titleasync: pres_title_n levels [1.0, 1.0]  per-call wall [400000.0, 3000.0] ns (arm-1 cap '
                 '60000 ns)') in lines
'''),
    ("    want = {'PRODUCTION_ROOT': 'C:/kyty/s114', 'PRED': 'C:/kyty/s114/pred/02_ttl114.md',\n",
     "    want = {'PRODUCTION_ROOT': 'C:/kyty/s114', 'PRED': 'C:/kyty/s114/pred/02b_ttl114b.md',\n"),
    # LEVEL_median: the arm-1 outlier block stays an outlier for a mean level under the new cap (66 609.1 ns over
    # 0.991 calls = 67 220 ns a call > 60 000; P2 67.2 > 60), as 2 000 000 was under the old one (21 349 > 20 000)
    (r'''# and block 17 (arm 1) 2 000 000, block 21 (arm 1) pres_title_n 0: medians 31 000 / 30 850 / 400 000 / 3 000 / 1
# exactly (means: 31 026.4 / 30 876.4 / 5 850 909.1 / 21 154.5 / 0.991 - P1 and P2 would miss, TITLE_ARMED and
''',
     r'''# and block 17 (arm 1) 7 000 000, block 21 (arm 1) pres_title_n 0: medians 31 000 / 30 850 / 400 000 / 3 000 / 1
# exactly (means: 31 026.4 / 30 876.4 / 5 850 909.1 / 66 609.1 / 0.991 - P1 and P2 would miss, TITLE_ARMED and
'''),
    ("           edits={'x': {'pres_title_ns': lambda n, b, a, i: 2000000 if a else 600000000}}),\n",
     "           edits={'x': {'pres_title_ns': lambda n, b, a, i: 7000000 if a else 600000000}}),\n"),
    # PRED_edges_hi / PRED_misses_hi: P2's upper edge and just above it (= the cap and 1 ns above it)
    (r'''# on the upper edges: P1 5 000 (5 000 000 ns a call), P2 20 (20 000 ns = TITLE_WALL_MAX_NS: admitted), P3 +100, P5
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
''',
     r'''# on the upper edges: P1 5 000 (5 000 000 ns a call), P2 60 (60 000 ns = TITLE_WALL_MAX_NS: admitted), P3 +100, P5
# +150, P6 0 (arm-1 reserve wait 5 000 ns a flip, as arm 0's), P7 +40 - all hit but P4 (d +100 fails S1 alone)
case('PRED_edges_hi', run_eval(make('prededgehi', d_dt=100, noise=0, tns0=5000000, tns1=60000, gpu1=12850, rsv1=5000,
                                    row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_miss': 340}}))),
     KEEP_BAR, rules=[S1],
     check=lambda o: pred_values(o, P1=5000.0, P2=60.0, P3=100.0, P4=100.0, P5=150.0, P6=0.0, P7=40.0,
                                 hits=['P1', 'P2', 'P3', 'P5', 'P6', 'P7']))
# just above them: 5 000.001, 60.001 (above TITLE_WALL_MAX_NS: not admitted, TITLE_ARMED alone - the predictions are
# still computed), +101, +151, +1 ns a flip, +41 - all miss
case('PRED_misses_hi', run_eval(make('predmisshi', d_dt=101, noise=0, tns0=5000001, tns1=60001, gpu1=12851,
                                     rsv1=5001,
                                     row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_miss': 341}}))),
     KEEP_NA, fails=ARMING, arming=['TITLE_ARMED'], rules=[S1],
     check=lambda o: pred_values(o, P1=5000.001, P2=60.001, P3=101.0, P4=101.0, P5=151.0, P6=1.0, P7=41.0,
'''),
    # TITLE_ARMED: the cap's edge and 1 ns above it
    (r'''# TITLE_ARMED: the candidate does not wait - its per-call wall at most TITLE_WALL_MAX_NS = 20 000 ns and strictly below
# today's.  The cap's edge: 20 000 ns a call passes (P2 20 us hits) ...
case('TITLE_ARMED_edge', run_eval(make('tarmededge', tns1=20000)), PENDING,
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [400000.0, 20000.0]
                      and pred_values(o, P2=20.0, hits=list(PRED_BANDS))))
# ... 20 001 fails alone (P2 20.001 misses) ...
case('TITLE_ARMED_out', run_eval(make('tarmedout', tns1=20001)), KEEP_NA, fails=ARMING, arming=['TITLE_ARMED'],
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [400000.0, 20001.0]
                      and pred_values(o, P2=20.001, hits=['P1', 'P3', 'P4', 'P5', 'P6', 'P7'])))
''',
     r'''# TITLE_ARMED: the candidate does not wait - its per-call wall at most TITLE_WALL_MAX_NS = 60 000 ns and strictly below
# today's.  The cap's edge: 60 000 ns a call passes (P2 60 us hits) ...
case('TITLE_ARMED_edge', run_eval(make('tarmededge', tns1=60000)), PENDING,
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [400000.0, 60000.0]
                      and pred_values(o, P2=60.0, hits=list(PRED_BANDS))))
# ... 60 001 fails alone (P2 60.001 misses) ...
case('TITLE_ARMED_out', run_eval(make('tarmedout', tns1=60001)), KEEP_NA, fails=ARMING, arming=['TITLE_ARMED'],
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [400000.0, 60001.0]
                      and pred_values(o, P2=60.001, hits=['P1', 'P3', 'P4', 'P5', 'P6', 'P7'])))
'''),
    # TITLE_ARMED per call: the raw level above the cap, the per-call wall under it (3/4 of the cap, 1.5x the cap raw,
    # as 15 000 / 30 000 were under 20 000), then 1 ns a call above the cap
    (r'''# the wall is PER CALL: two calls a flip in both arms, arm 0 800 000 ns (400 000 a call), arm 1 30 000 ns (15 000 a
# call, the raw level above the cap) - passes; P1 400, P2 15 ...
case('TITLE_ARMED_percall', run_eval(make('tarmedpc', tn0=2, tn1=2, tns0=800000, tns1=30000)), PENDING,
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [400000.0, 15000.0]
                      and o['arming']['title_n_levels'] == [2.0, 2.0]
                      and pred_values(o, P1=400.0, P2=15.0, hits=list(PRED_BANDS))))
# ... and 40 002 ns over two calls (20 001 a call) fails alone
case('TITLE_ARMED_percall_out', run_eval(make('tarmedpcout', tn0=2, tn1=2, tns0=800000, tns1=40002)), KEEP_NA,
     fails=ARMING, arming=['TITLE_ARMED'],
     check=lambda o: o['arming']['title_wall_per_call_ns'] == [400000.0, 20001.0])
''',
     r'''# the wall is PER CALL: two calls a flip in both arms, arm 0 800 000 ns (400 000 a call), arm 1 90 000 ns (45 000 a
# call, the raw level above the cap) - passes; P1 400, P2 45 ...
case('TITLE_ARMED_percall', run_eval(make('tarmedpc', tn0=2, tn1=2, tns0=800000, tns1=90000)), PENDING,
     check=lambda o: (o['arming']['title_wall_per_call_ns'] == [400000.0, 45000.0]
                      and o['arming']['title_n_levels'] == [2.0, 2.0]
                      and pred_values(o, P1=400.0, P2=45.0, hits=list(PRED_BANDS))))
# ... and 120 002 ns over two calls (60 001 a call) fails alone
case('TITLE_ARMED_percall_out', run_eval(make('tarmedpcout', tn0=2, tn1=2, tns0=800000, tns1=120002)), KEEP_NA,
     fails=ARMING, arming=['TITLE_ARMED'],
     check=lambda o: o['arming']['title_wall_per_call_ns'] == [400000.0, 60001.0])
'''),
], forbidden=('tns1=20000', 'tns1=20001', 'tns1=30000', 'tns1=40002', "'P2': [None, 20]", 'P2=20.', "'20000 ns)'",
              '2000000 if a else', '21 154.5', 'pred/02_ttl114.md', 'ttl114_draft', '20 000 ns a call passes'),
   required=("'P2': [None, 60]", "'PRED': 'C:/kyty/s114/pred/02b_ttl114b.md'", "'60000 ns)') in lines\n",
             "make('tarmededge', tns1=60000)", "make('tarmedout', tns1=60001)", 'tns1=90000)', 'tns1=120002)',
             'lambda n, b, a, i: 7000000 if a else 600000000'))

# =====================================================================================================================
# the mutants
# =====================================================================================================================
MUT_TEXT = derive('mut_ttl114.py', [
    ('"""Session 114: mutation check of ttl114.py against test_ttl114.py, derived from session 113\'s sealed '
     'mut_shn113.py by\n',
     r'''"""Session 114, seal 02b (ROADMAP s0.1, the session-114 records, item 8): mutation check of ttl114b.py against
test_ttl114b.py, derived from mut_ttl114.py (the draft list: with the two draft-only seal mutants, which apply to this
draft again) by make_ttl114b.py (whole-line anchored replacements).  ttl114b is ttl114 with the arm-1 cap
TITLE_WALL_MAX_NS = 60 000 ns (was 20 000) and P2 <= 60 us (was 20).  Re-anchored on the new values:
TITLE_WALL_MAX_59999 / TITLE_WALL_MAX_60001 / TITLE_WALL_MAX_in_us (60) (were _19999 / _20001 / 20), PRED_P2_arm0,
PRED_P2_hi_59 / PRED_P2_hi_61 (were _hi_19 / _hi_21), PRED_P2_bounded, CONST_pred_shn113 and CONST_pred_ctl114 (on
PRED = pred/02b_ttl114b.md).  Added, ttl114's own values: TITLE_WALL_MAX_20000, PRED_P2_hi_20, CONST_pred_ttl114.
Every other mutant is mut_ttl114.py's, unchanged (347 = 344 + 3).  Paths: C:/kyty/s114/ttl114b_draft.  The
description of mut_ttl114.py follows.

Session 114: mutation check of ttl114.py against test_ttl114.py, derived from session 113's sealed mut_shn113.py by
'''),
    ('mutant runs the full fixture suite in its own fixture directory (C:/kyty/s114/ttl114_draft/ttl114/fx_mut/w<k>, '
     'removed\n',
     'mutant runs the full fixture suite in its own fixture directory (C:/kyty/s114/ttl114b_draft/ttl114b/fx_mut/w<k>, '
     'removed\n'),
    ('    python mut_ttl114.py [<workers>]\n', '    python mut_ttl114b.py [<workers>]\n'),
    (r'''HERE = Path('C:/kyty/s114/ttl114_draft')
SCORER = HERE / 'ttl114.py'
TEST = HERE / 'test_ttl114.py'
MUT = HERE / 'ttl114' / 'mutants'
FX = HERE / 'ttl114' / 'fx_mut'
''',
     r'''HERE = Path('C:/kyty/s114/ttl114b_draft')
SCORER = HERE / 'ttl114b.py'
TEST = HERE / 'test_ttl114b.py'
MUT = HERE / 'ttl114b' / 'mutants'
FX = HERE / 'ttl114b' / 'fx_mut'
'''),
    (r'''mutant('TITLE_WALL_MAX_19999', NL + 'TITLE_WALL_MAX_NS = 20000', NL + 'TITLE_WALL_MAX_NS = 19999')
mutant('TITLE_WALL_MAX_20001', NL + 'TITLE_WALL_MAX_NS = 20000', NL + 'TITLE_WALL_MAX_NS = 20001')
mutant('TITLE_WALL_MAX_in_us', NL + 'TITLE_WALL_MAX_NS = 20000', NL + 'TITLE_WALL_MAX_NS = 20')
''',
     r'''mutant('TITLE_WALL_MAX_59999', NL + 'TITLE_WALL_MAX_NS = 60000', NL + 'TITLE_WALL_MAX_NS = 59999')
mutant('TITLE_WALL_MAX_60001', NL + 'TITLE_WALL_MAX_NS = 60000', NL + 'TITLE_WALL_MAX_NS = 60001')
mutant('TITLE_WALL_MAX_in_us', NL + 'TITLE_WALL_MAX_NS = 60000', NL + 'TITLE_WALL_MAX_NS = 60')
mutant('TITLE_WALL_MAX_20000', NL + 'TITLE_WALL_MAX_NS = 60000', NL + 'TITLE_WALL_MAX_NS = 20000')   # ttl114's cap
'''),
    (r'''mutant('CONST_pred_shn113', "PRED = 'C:/kyty/s114/pred/02_ttl114.md'", "PRED = 'C:/kyty/s113/pred/02_shn113.md'")
mutant('CONST_pred_ctl114', "PRED = 'C:/kyty/s114/pred/02_ttl114.md'", "PRED = 'C:/kyty/s114/pred/01_ctl114.md'")
''',
     r'''mutant('CONST_pred_shn113', "PRED = 'C:/kyty/s114/pred/02b_ttl114b.md'", "PRED = 'C:/kyty/s113/pred/02_shn113.md'")
mutant('CONST_pred_ctl114', "PRED = 'C:/kyty/s114/pred/02b_ttl114b.md'", "PRED = 'C:/kyty/s114/pred/01_ctl114.md'")
mutant('CONST_pred_ttl114', "PRED = 'C:/kyty/s114/pred/02b_ttl114b.md'", "PRED = 'C:/kyty/s114/pred/02_ttl114.md'")
'''),
    ('P2 = "us[1], None, 20)"\n', 'P2 = "us[1], None, 60)"\n'),
    (r'''mutant('PRED_P2_arm0', P2, "us[0], None, 20)")
mutant('PRED_P2_hi_19', P2, "us[1], None, 19)")
mutant('PRED_P2_hi_21', P2, "us[1], None, 21)")
mutant('PRED_P2_bounded', P2, "us[1], 1, 20)")
''',
     r'''mutant('PRED_P2_arm0', P2, "us[0], None, 60)")
mutant('PRED_P2_hi_59', P2, "us[1], None, 59)")
mutant('PRED_P2_hi_61', P2, "us[1], None, 61)")
mutant('PRED_P2_bounded', P2, "us[1], 1, 60)")
mutant('PRED_P2_hi_20', P2, "us[1], None, 20)")      # ttl114's band
'''),
    ("        path = MUT / ('ttl114_%s.py' % name)\n", "        path = MUT / ('ttl114b_%s.py' % name)\n"),
], forbidden=("'ttl114_%s.py'", 'ttl114_draft', "HERE / 'ttl114' /", "'TITLE_WALL_MAX_NS = 20000', NL",
              'P2 = "us[1], None, 20)"', "pred/02_ttl114.md'\", \"PRED", "SCORER = HERE / 'ttl114.py'"),
   width=0)


# =====================================================================================================================
# the mutant list against the new scorer: exactly the renamed / re-anchored / added mutants differ from mut_ttl114.py
# =====================================================================================================================
def mutant_defs(text):
    """The mutant dict of a mutant script: its statements up to the legacy harness, without reading the scorer."""
    cut = 'MUT.mkdir(parents=True, exist_ok=True)\n'
    src_line = "SRC = SCORER.read_bytes().decode('utf-8')\n"
    assert text.count(cut) == 1 and text.count(src_line) == 1
    head_text = text[:text.index(cut)].replace(src_line, '')
    ns = {'__name__': 'mutant_defs'}
    exec(compile(head_text, 'mutant_defs', 'exec'), ns)
    return ns['M']


RENAMED = {'TITLE_WALL_MAX_19999': 'TITLE_WALL_MAX_59999', 'TITLE_WALL_MAX_20001': 'TITLE_WALL_MAX_60001',
           'PRED_P2_hi_19': 'PRED_P2_hi_59', 'PRED_P2_hi_21': 'PRED_P2_hi_61'}
REANCHORED = ('TITLE_WALL_MAX_in_us', 'PRED_P2_arm0', 'PRED_P2_bounded', 'CONST_pred_shn113', 'CONST_pred_ctl114')
ADDED = ('TITLE_WALL_MAX_20000', 'PRED_P2_hi_20', 'CONST_pred_ttl114')
old_m = mutant_defs(load('mut_ttl114.py'))
new_m = mutant_defs(MUT_TEXT)
assert len(old_m) == 344 and len(new_m) == 347, (len(old_m), len(new_m))
assert set(new_m) == (set(old_m) - set(RENAMED)) | set(RENAMED.values()) | set(ADDED)
for name, (old, new) in new_m.items():
    assert SCORER.count(old) == 1, ('anchor not once in ttl114b.py', name, SCORER.count(old))
    assert old != new, ('changes nothing', name)
    if name in REANCHORED:
        assert new_m[name] != old_m[name], name
    elif name in old_m:
        assert new_m[name] == old_m[name], ('changed', name)
    if name in REANCHORED or name in ADDED or name in RENAMED.values():
        compile(SCORER.replace(old, new), name, 'exec')
print('mutants: %d (%d of mut_ttl114.py unchanged, %d renamed, %d re-anchored, %d added); every anchor once in '
      'ttl114b.py' % (len(new_m), sum(1 for n in new_m if n in old_m and n not in REANCHORED), len(RENAMED),
                      len(REANCHORED), len(ADDED)))
