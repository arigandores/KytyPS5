"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 18: vbn113f.py / test_vbn113f.py / mut_vbn113f.py from the vbn113e files
(draft copies, sha pinned) by WHOLE-LINE anchored replacements (asserted).  Changes: the build 1678d3f4 (the exact check,
the GC-trigger measurement env and the priority-stall instrument); tags vbn113m, vbn113n; the stall counters prio_unsub,
prio_stall, gw_idle_prio in FIELDS_X (information, their presence is part of ROWS); prediction B7 (no stall).
Byte-reproducible.

    python C:/kyty/s106_stage/make_vbn113f.py
"""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
PINS = {'vbn113e.py': 'f432ce6a', 'test_vbn113e.py': '9c5d713c', 'mut_vbn113e.py': 'd8ecaa1a'}
NEW_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'
OLD_SHA = 'cf22e2236613556f046107804e6545d09fba7833fc23c72cde010e06ca395121'


def load(name):
    s = (STAGE / name).read_bytes().decode('utf-8').replace('\r\n', '\n')
    assert hashlib.sha256(s.encode('utf-8')).hexdigest().startswith(PINS[name]), name
    return s


def derive(src, dst, pairs):
    s = load(src)
    for a, b in pairs:
        assert a.endswith('\n') and b.endswith('\n'), (src, 'not whole lines', a[:80])
        assert s.startswith(a) or ('\n' + a) in s, (src, 'anchor not at a line start', a[:80])
        assert s.count(a) == 1, (src, a[:80], s.count(a))
        s = s.replace(a, b)
    (STAGE / dst).write_bytes(s.encode('utf-8'))
    print(dst, hashlib.sha256(s.encode('utf-8')).hexdigest())


derive('vbn113e.py', 'vbn113f.py', [
    ('"""Session 113, pred/01e_vbn113e.md (from vbn113d.py by make_vbn113e.py - ROADMAP item 17: the same verify run with the\n'
     'buffer-GC trigger lowered by KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024, a forced OLD regime; vbn113d.py came from vbn113c.py\n'
     'by make_vbn113d.py): the verify run of knob `bdanarrow` in mode 2 (today\'s global invalidation of the BDA\n',
     '"""Session 113, pred/01f_vbn113f.md (from vbn113e.py by make_vbn113f.py - ROADMAP item 18: 01e again, on the build with\n'
     'the priority-stall instrument, whose counters are information; vbn113e.py added the forced OLD regime,\n'
     'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024): the verify run of knob `bdanarrow` in mode 2 (today\'s global invalidation of the BDA\n'),
    ('    python C:/kyty/s113/vbn113e.py [--tag vbn113k|vbn113l] [--root C:/kyty/s113] [--out <json>]\n',
     '    python C:/kyty/s113/vbn113f.py [--tag vbn113m|vbn113n] [--root C:/kyty/s113] [--out <json>]\n'),
    ("TAGS = ('vbn113k', 'vbn113l')\n", "TAGS = ('vbn113m', 'vbn113n')\n"),
    ("PRED = 'C:/kyty/s113/pred/01e_vbn113e.md'\n", "PRED = 'C:/kyty/s113/pred/01f_vbn113f.md'\n"),
    ("PRED_SHA = None     # pred/01e_vbn113e.md sealed\n", "PRED_SHA = None     # pred/01f_vbn113f.md sealed\n"),
    ("PRED_BYTES = None   # pred/01e_vbn113e.md sealed\n", "PRED_BYTES = None   # pred/01f_vbn113f.md sealed\n"),
    ("BINARY_SHA = '%s'\n" % OLD_SHA, "BINARY_SHA = '%s'\n" % NEW_SHA),
    ("            'bgc_evict', 'bda_nrace', 'da_q_free', 'cspfree_hit', 'cspfree_bad')\n",
     "            'bgc_evict', 'bda_nrace', 'da_q_free', 'cspfree_hit', 'cspfree_bad', 'prio_unsub', 'prio_stall',\n"
     "            'gw_idle_prio')\n"),
    ("     lambda r: r['total']['bda_nrace'], None, 40),\n)\n",
     "     lambda r: r['total']['bda_nrace'], None, 40),\n"
     "    ('B7', 'sum prio_stall == 0 (no priority wait longer than 50 ms: the 01e stall did not recur)',\n"
     "     lambda r: r['total']['prio_stall'], 0, 0),\n)\n"),
])

derive('test_vbn113e.py', 'test_vbn113f.py', [
    ('"""Session 113: fixtures for vbn113e.py (from test_vbn113d.py by make_vbn113e.py; that from test_vbn113c.py) - every '
     'verdict branch (GO, NO_GO, INVESTIGATE, NOT_EVALUABLE, NOT_ADMITTED),\n',
     '"""Session 113: fixtures for vbn113f.py (from test_vbn113e.py by make_vbn113f.py; that from test_vbn113d.py) - every '
     'verdict branch (GO, NO_GO, INVESTIGATE, NOT_EVALUABLE, NOT_ADMITTED),\n'),
    ("    python test_vbn113e.py <vbn113e.py>\n", "    python test_vbn113f.py <vbn113f.py>\n"),
    ("BASE = Path('C:/kyty/s106_stage/fx_vbn113e')\n", "BASE = Path('C:/kyty/s106_stage/fx_vbn113f')\n"),
    ("spec = importlib.util.spec_from_file_location('vbn113e', SRC)\n",
     "spec = importlib.util.spec_from_file_location('vbn113f', SRC)\n"),
    ("seal.write_bytes(b'fixture seal 113 vbn e')\n", "seal.write_bytes(b'fixture seal 113 vbn f')\n"),
    ("         evict=1, race=0, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113k', gpu_util=0.0,\n",
     "         evict=1, race=0, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113m', gpu_util=0.0,\n"),
    ("         row_edit=None, **bad):\n", "         row_edit=None, stall=0, **bad):\n"),
    ("                    cspfree_bad=free_bad if n == 3500 else 0)\n",
     "                    cspfree_bad=free_bad if n == 3500 else 0, prio_unsub=0, prio_stall=stall if n == 4300 else 0,\n"
     "                    gw_idle_prio=0)\n"),
    ("    ('GO_tag_l', dict(tag='vbn113l'), 'GO', []),\n", "    ('GO_tag_n', dict(tag='vbn113n'), 'GO', []),\n"),
    ("    ('GO_race', dict(race=1), 'GO', []),                                       # races are information (exact check)\n",
     "    ('GO_race', dict(race=1), 'GO', []),                                       # races are information (exact check)\n"
     "    ('GO_stall', dict(stall=1), 'GO', []),                                     # the stall counters are information\n"),
    ("    ('TAG', dict(tag='vbn113m'), 'NOT_ADMITTED', ['TAG']),\n    ('TAG_old', dict(tag='vbn113j'), 'NOT_ADMITTED', ['TAG']),\n",
     "    ('TAG', dict(tag='vbn113o'), 'NOT_ADMITTED', ['TAG']),\n    ('TAG_old', dict(tag='vbn113l'), 'NOT_ADMITTED', ['TAG']),\n"),
    ("    ('ROWS_field', dict(drop_field=True), 'NOT_ADMITTED', ['ROWS']),\n",
     "    ('ROWS_field', dict(drop_field=True), 'NOT_ADMITTED', ['ROWS']),\n"
     "    ('ROWS_field_prio', dict(row_edit=lambda n, vals: vals.pop('prio_stall') if n == 3000 else None), 'NOT_ADMITTED',\n"
     "     ['ROWS']),\n"),
    ("CONSTANTS = dict(TAGS=('vbn113k', 'vbn113l'), TAIL=' bdanarrow=2', HOLD_S=300, MIN_ROWS=5000, REGIME_OLD=500,\n",
     "CONSTANTS = dict(TAGS=('vbn113m', 'vbn113n'), TAIL=' bdanarrow=2', HOLD_S=300, MIN_ROWS=5000, REGIME_OLD=500,\n"),
    ("                 BINARY_SHA='%s')\n" % OLD_SHA, "                 BINARY_SHA='%s')\n" % NEW_SHA),
    ("    (dict(nmiss=1), 'B1', False),                         # restored (ROADMAP item 16: lost by make_vbn113d)\n",
     "    (dict(nmiss=1), 'B1', False),                         # restored (ROADMAP item 16: lost by make_vbn113d)\n"
     "    (dict(stall=0), 'B7', True), (dict(stall=1), 'B7', False),\n"),
])

derive('mut_vbn113e.py', 'mut_vbn113f.py', [
    ('"""Session 113: mutants of vbn113e.py (from mut_vbn113d.py by make_vbn113e.py) - each must be killed by '
     'test_vbn113e.py.\n'
     'Run through mutlib v2 on the SEALED copy, --control --no-memo (items 15, 17).\n',
     '"""Session 113: mutants of vbn113f.py (from mut_vbn113e.py by make_vbn113f.py) - each must be killed by '
     'test_vbn113f.py.\n'
     'Run through mutlib v2 on the SEALED copy, --control --no-memo (items 15, 18).\n'),
    ("TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/vbn113e.py')\n",
     "TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/vbn113f.py')\n"),
    ("TEST = Path('C:/kyty/s106_stage/test_vbn113e.py')\n", "TEST = Path('C:/kyty/s106_stage/test_vbn113f.py')\n"),
    ("    ('tags', \"TAGS = ('vbn113k', 'vbn113l')\", \"TAGS = ('vbn113k', 'vbn113l', 'vbn113m')\"),\n"
     "    ('tags_drop', \"TAGS = ('vbn113k', 'vbn113l')\", \"TAGS = ('vbn113k',)\"),\n",
     "    ('tags', \"TAGS = ('vbn113m', 'vbn113n')\", \"TAGS = ('vbn113m', 'vbn113n', 'vbn113o')\"),\n"
     "    ('tags_drop', \"TAGS = ('vbn113m', 'vbn113n')\", \"TAGS = ('vbn113m',)\"),\n"),
    ("    ('gc_collect', '                gc_lines.append(tuple(int(x) for x in g.groups()))', '                pass'),\n",
     "    ('gc_collect', '                gc_lines.append(tuple(int(x) for x in g.groups()))', '                pass'),\n"
     r"""    ('fields_prio', "'cspfree_bad', 'prio_unsub', 'prio_stall',\n            'gw_idle_prio')", "'cspfree_bad')"),""" + '\n'
     "    ('b7', \"lambda r: r['total']['prio_stall'], 0, 0)\", \"lambda r: r['total']['prio_stall'], 0, 1)\"),\n"
     "    ('b7_field', \"lambda r: r['total']['prio_stall'], 0, 0)\", \"lambda r: r['total']['prio_unsub'], 0, 0)\"),\n"),
    ("    path = WORK / ('mut_vbn113e_%s.py' % name)\n", "    path = WORK / ('mut_vbn113f_%s.py' % name)\n"),
])
