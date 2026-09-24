"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 10 (a): vbn113c.py / test_vbn113c.py / mut_vbn113c.py from the vbn113b
files (draft copies, sha pinned) by anchored replacements: tags vbn113c..vbn113f (relaunch until OLD, up to 4 entries),
and bda_nrace > 0 leads to INVESTIGATE instead of GO (a real miss can hide in a race - audit 113 m2).  Byte-reproducible.

    python C:/kyty/s106_stage/make_vbn113c.py
"""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
PINS = {'vbn113b.py': '042e4d5c', 'test_vbn113b.py': None, 'mut_vbn113b.py': None}
NL = chr(10)


def load(name):
    s = (STAGE / name).read_bytes().decode('utf-8').replace('\r\n', '\n')
    pin = PINS.get(name)
    if pin:
        assert hashlib.sha256(s.encode('utf-8')).hexdigest().startswith(pin), name
    return s


def derive(src, dst, pairs):
    s = load(src)
    for a, b in pairs:
        assert s.count(a) == 1, (src, a[:80], s.count(a))
        s = s.replace(a, b)
    (STAGE / dst).write_bytes(s.encode('utf-8'))
    print(dst, hashlib.sha256(s.encode('utf-8')).hexdigest())


derive('vbn113b.py', 'vbn113c.py', [
    ('"""Session 113, pred/01b_vbn113b.md (from vbn113.py by make_vbn113b.py - seal 01 superseded before any run by the\n'
     'pre-run audit, ROADMAP item 5): the verify run',
     '"""Session 113, pred/01c_vbn113c.md (from vbn113b.py by make_vbn113c.py - ROADMAP item 10: relaunch until OLD, a race\n'
     'is investigated, not forgiven; vbn113b.py itself came from vbn113.py by make_vbn113b.py): the verify run'),
    ("""    GO             admitted, BAD == 0""",
     """    GO             admitted, BAD == 0 and sum(bda_nrace) == 0"""),
    ("""    INVESTIGATE    admitted, sum(bda_nmiss) == 0 and sum(bda_nxthr) > 0 (an unknown off-thread registrar: neither
                   GO nor a closing verdict)""",
     """    INVESTIGATE    admitted, sum(bda_nmiss) == 0 and (sum(bda_nxthr) > 0 or sum(bda_nrace) > 0) (an unknown off-thread
                   registrar, or a race that may hide a real miss: neither GO nor a closing verdict)"""),
    ("    python C:/kyty/s113/vbn113b.py [--tag vbn113|vbn113b] [--root C:/kyty/s113] [--out <json>]",
     "    python C:/kyty/s113/vbn113c.py [--tag vbn113c|vbn113d|vbn113e|vbn113f] [--root C:/kyty/s113] [--out <json>]"),
    ("TAGS = ('vbn113', 'vbn113b')", "TAGS = ('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f')"),
    ("PRED = 'C:/kyty/s113/pred/01b_vbn113b.md'", "PRED = 'C:/kyty/s113/pred/01c_vbn113c.md'"),
    ("PRED_SHA = None     # pred/01b_vbn113b.md sealed", "PRED_SHA = None     # pred/01c_vbn113c.md sealed"),
    ("PRED_BYTES = None   # pred/01b_vbn113b.md sealed", "PRED_BYTES = None   # pred/01c_vbn113c.md sealed"),
    ("""    elif bad == 0:
        out['verdict'] = 'GO'""",
     """    elif bad == 0 and tot['bda_nrace'] == 0:
        out['verdict'] = 'GO'"""),
])

derive('test_vbn113b.py', 'test_vbn113c.py', [
    ('"""Session 113: fixtures for vbn113b.py', '"""Session 113: fixtures for vbn113c.py (from test_vbn113b.py by make_vbn113c.py)'),
    ("    python test_vbn113b.py <vbn113b.py>", "    python test_vbn113c.py <vbn113c.py>"),
    ("BASE = Path('C:/kyty/s106_stage/fx_vbn113b')", "BASE = Path('C:/kyty/s106_stage/fx_vbn113c')"),
    ("spec = importlib.util.spec_from_file_location('vbn113b', SRC)", "spec = importlib.util.spec_from_file_location('vbn113c', SRC)"),
    ("seal.write_bytes(b'fixture seal 113 vbn b')", "seal.write_bytes(b'fixture seal 113 vbn c')"),
    ("         evict=1, race=0, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113', gpu_util=0.0,",
     "         evict=1, race=0, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113c', gpu_util=0.0,"),
    ("    ('GO_tag_b', dict(tag='vbn113b'), 'GO', []),",
     "    ('GO_tag_d', dict(tag='vbn113d'), 'GO', []),\n    ('GO_tag_e', dict(tag='vbn113e'), 'GO', []),\n"
     "    ('GO_tag_f', dict(tag='vbn113f'), 'GO', []),"),
    ("    ('GO_races_only', dict(race=7), 'GO', []),                                   # races never count as misses",
     "    ('INVESTIGATE_race', dict(race=1), 'INVESTIGATE', []),                     # a race may hide a real miss\n"
     "    ('INVESTIGATE_race_xthr', dict(race=1, nxthr=1), 'INVESTIGATE', []),\n"
     "    ('NO_GO_miss_and_race', dict(nmiss=1, race=1), 'NO_GO', []),"),
    ("    ('TAG', dict(tag='vbn113c'), 'NOT_ADMITTED', ['TAG']),",
     "    ('TAG', dict(tag='vbn113g'), 'NOT_ADMITTED', ['TAG']),\n    ('TAG_old', dict(tag='vbn113b'), 'NOT_ADMITTED', ['TAG']),"),
    ("CONSTANTS = dict(TAGS=('vbn113', 'vbn113b'),", "CONSTANTS = dict(TAGS=('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f'),"),
    ("    (dict(race=40), 'B6', True), (dict(race=41), 'B6', False),",
     "    (dict(race=40), 'B6', True), (dict(race=41), 'B6', False), (dict(race=0), 'B6', True),"),
])

derive('mut_vbn113b.py', 'mut_vbn113c.py', [
    ('"""Session 113: mutants of vbn113b.py - each must be killed by test_vbn113b.py.  Run on the SEALED copy (decision item 5):\n'
     '    python mut_vbn113b.py C:/kyty/s113/vbn113b.py > mut_vbn113b.out.txt',
     '"""Session 113: mutants of vbn113c.py (from mut_vbn113b.py by make_vbn113c.py) - each must be killed by test_vbn113c.py.\n'
     'Run on the SEALED copy (decision items 5, 10):\n    python mut_vbn113c.py C:/kyty/s113/vbn113c.py > mut_vbn113c.out.txt'),
    ("TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/vbn113b.py')",
     "TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/vbn113c.py')"),
    ("TEST = Path('C:/kyty/s106_stage/test_vbn113b.py')", "TEST = Path('C:/kyty/s106_stage/test_vbn113c.py')"),
    ("    ('tags', \"TAGS = ('vbn113', 'vbn113b')\", \"TAGS = ('vbn113', 'vbn113b', 'vbn113c')\"),",
     "    ('tags', \"TAGS = ('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f')\", \"TAGS = ('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f', 'vbn113g')\"),\n"
     "    ('tags_drop', \"TAGS = ('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f')\", \"TAGS = ('vbn113c', 'vbn113d', 'vbn113e')\"),\n"
     "    ('race_forgiven', \"    elif bad == 0 and tot['bda_nrace'] == 0:\", \"    elif bad == 0:\"),"),
    ("    path = WORK / ('mut_vbn113b_%s.py' % name)", "    path = WORK / ('mut_vbn113c_%s.py' % name)"),
])
