"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 14: vbn113d.py / test_vbn113d.py / mut_vbn113d.py from the vbn113c files
(draft copies, sha pinned) by anchored replacements: the exact check (build 5ba0e188 reads the region stamp under the lock
of the collect) makes bda_nrace information again - GO = sum(bda_nmiss) == 0 and sum(bda_nxthr) == 0; tags vbn113g..j
(relaunch until OLD, up to 4 entries); a B1 fixture with races (the mutlib survivor `bad_race` of vbn113c).
Byte-reproducible.

    python C:/kyty/s106_stage/make_vbn113d.py
"""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
PINS = {'vbn113c.py': 'b53f5e66', 'test_vbn113c.py': '8f6f24e2', 'mut_vbn113c.py': '6c9b0651'}


def load(name):
    s = (STAGE / name).read_bytes().decode('utf-8').replace('\r\n', '\n')
    assert hashlib.sha256(s.encode('utf-8')).hexdigest().startswith(PINS[name]), name
    return s


def derive(src, dst, pairs):
    s = load(src)
    for a, b in pairs:
        assert s.count(a) == 1, (src, a[:80], s.count(a))
        s = s.replace(a, b)
    (STAGE / dst).write_bytes(s.encode('utf-8'))
    print(dst, hashlib.sha256(s.encode('utf-8')).hexdigest())


derive('vbn113c.py', 'vbn113d.py', [
    ('"""Session 113, pred/01c_vbn113c.md (from vbn113b.py by make_vbn113c.py - ROADMAP item 10: relaunch until OLD, a race\n'
     'is investigated, not forgiven; vbn113b.py itself came from vbn113.py by make_vbn113b.py): the verify run',
     '"""Session 113, pred/01d_vbn113d.md (from vbn113c.py by make_vbn113d.py - ROADMAP item 14: the build reads the region\n'
     'stamp under the lock of the collect, so bda_nmiss is exact and bda_nrace is information; vbn113c.py came from\n'
     'vbn113b.py by make_vbn113c.py): the verify run'),
    ("""    GO             admitted, BAD == 0 and sum(bda_nrace) == 0""",
     """    GO             admitted, BAD == 0 (bda_nrace is information)"""),
    ("""    INVESTIGATE    admitted, sum(bda_nmiss) == 0 and (sum(bda_nxthr) > 0 or sum(bda_nrace) > 0) (an unknown off-thread
                   registrar, or a race that may hide a real miss: neither GO nor a closing verdict)""",
     """    INVESTIGATE    admitted, sum(bda_nmiss) == 0 and sum(bda_nxthr) > 0 (an unknown off-thread registrar: neither GO
                   nor a closing verdict)"""),
    ("    python C:/kyty/s113/vbn113c.py [--tag vbn113c|vbn113d|vbn113e|vbn113f] [--root C:/kyty/s113] [--out <json>]",
     "    python C:/kyty/s113/vbn113d.py [--tag vbn113g|vbn113h|vbn113i|vbn113j] [--root C:/kyty/s113] [--out <json>]"),
    ("TAGS = ('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f')", "TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j')"),
    ("PRED = 'C:/kyty/s113/pred/01c_vbn113c.md'", "PRED = 'C:/kyty/s113/pred/01d_vbn113d.md'"),
    ("PRED_SHA = None     # pred/01c_vbn113c.md sealed", "PRED_SHA = None     # pred/01d_vbn113d.md sealed"),
    ("PRED_BYTES = None   # pred/01c_vbn113c.md sealed", "PRED_BYTES = None   # pred/01d_vbn113d.md sealed"),
    ("BINARY_SHA = '7d9fa0288099204f16974292a0d474afee80e58df43770612e11b8d5db5d6e5f'",
     "BINARY_SHA = '5ba0e1881565dc922651cb15e3df0fb9ddec39a33d117428cb6faf27a4948ba3'"),
    ("""    ('B6', 'sum bda_nrace <= 40 (races the check separated; the audit estimated 0.4-40 in 300 s)',""",
     """    ('B6', 'sum bda_nrace <= 40 (information: a write between the unlocked and the locked stamp read)',"""),
    ("""    elif bad == 0 and tot['bda_nrace'] == 0:
        out['verdict'] = 'GO'""",
     """    elif bad == 0:
        out['verdict'] = 'GO'"""),
])

derive('test_vbn113c.py', 'test_vbn113d.py', [
    ('"""Session 113: fixtures for vbn113c.py (from test_vbn113b.py by make_vbn113c.py)',
     '"""Session 113: fixtures for vbn113d.py (from test_vbn113c.py by make_vbn113d.py; that from test_vbn113b.py)'),
    ("    python test_vbn113c.py <vbn113c.py>", "    python test_vbn113d.py <vbn113d.py>"),
    ("BASE = Path('C:/kyty/s106_stage/fx_vbn113c')", "BASE = Path('C:/kyty/s106_stage/fx_vbn113d')"),
    ("spec = importlib.util.spec_from_file_location('vbn113c', SRC)", "spec = importlib.util.spec_from_file_location('vbn113d', SRC)"),
    ("seal.write_bytes(b'fixture seal 113 vbn c')", "seal.write_bytes(b'fixture seal 113 vbn d')"),
    ("         evict=1, race=0, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113c', gpu_util=0.0,",
     "         evict=1, race=0, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113g', gpu_util=0.0,"),
    ("    ('GO_tag_d', dict(tag='vbn113d'), 'GO', []),\n    ('GO_tag_e', dict(tag='vbn113e'), 'GO', []),\n"
     "    ('GO_tag_f', dict(tag='vbn113f'), 'GO', []),",
     "    ('GO_tag_h', dict(tag='vbn113h'), 'GO', []),\n    ('GO_tag_i', dict(tag='vbn113i'), 'GO', []),\n"
     "    ('GO_tag_j', dict(tag='vbn113j'), 'GO', []),"),
    ("    ('INVESTIGATE_race', dict(race=1), 'INVESTIGATE', []),                     # a race may hide a real miss\n",
     "    ('GO_race', dict(race=1), 'GO', []),                                       # races are information (exact check)\n"),
    ("    ('TAG', dict(tag='vbn113g'), 'NOT_ADMITTED', ['TAG']),\n    ('TAG_old', dict(tag='vbn113b'), 'NOT_ADMITTED', ['TAG']),",
     "    ('TAG', dict(tag='vbn113k'), 'NOT_ADMITTED', ['TAG']),\n    ('TAG_old', dict(tag='vbn113c'), 'NOT_ADMITTED', ['TAG']),"),
    ("CONSTANTS = dict(TAGS=('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f'),",
     "CONSTANTS = dict(TAGS=('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j'),"),
    ("                 BINARY_SHA='7d9fa0288099204f16974292a0d474afee80e58df43770612e11b8d5db5d6e5f')",
     "                 BINARY_SHA='5ba0e1881565dc922651cb15e3df0fb9ddec39a33d117428cb6faf27a4948ba3')"),
    ("    (dict(race=40), 'B6', True), (dict(race=41), 'B6', False), (dict(race=0), 'B6', True),",
     "    (dict(race=40), 'B6', True), (dict(race=41), 'B6', False), (dict(race=0), 'B6', True),\n"
     "    (dict(race=1), 'B1', True),                           # B1 reads BAD, which races never enter (bad_race)"),
])

derive('mut_vbn113c.py', 'mut_vbn113d.py', [
    ('"""Session 113: mutants of vbn113c.py (from mut_vbn113b.py by make_vbn113c.py) - each must be killed by test_vbn113c.py.\n'
     'Run on the SEALED copy (decision items 5, 10):\n    python mut_vbn113c.py C:/kyty/s113/vbn113c.py > mut_vbn113c.out.txt',
     '"""Session 113: mutants of vbn113d.py (from mut_vbn113c.py by make_vbn113d.py) - each must be killed by test_vbn113d.py.\n'
     'Run through mutlib on the SEALED copy (items 7, 13, 14).'),
    ("TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/vbn113c.py')",
     "TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/vbn113d.py')"),
    ("TEST = Path('C:/kyty/s106_stage/test_vbn113c.py')", "TEST = Path('C:/kyty/s106_stage/test_vbn113d.py')"),
    ("    ('tags', \"TAGS = ('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f')\", \"TAGS = ('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f', 'vbn113g')\"),\n"
     "    ('tags_drop', \"TAGS = ('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f')\", \"TAGS = ('vbn113c', 'vbn113d', 'vbn113e')\"),\n"
     "    ('race_forgiven', \"    elif bad == 0 and tot['bda_nrace'] == 0:\", \"    elif bad == 0:\"),",
     "    ('tags', \"TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j')\", \"TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j', 'vbn113k')\"),\n"
     "    ('tags_drop', \"TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j')\", \"TAGS = ('vbn113g', 'vbn113h', 'vbn113i')\"),\n"
     "    ('race_blocks', \"    elif bad == 0:\\n        out['verdict'] = 'GO'\", \"    elif bad == 0 and tot['bda_nrace'] == 0:\\n        out['verdict'] = 'GO'\"),"),
    ("    path = WORK / ('mut_vbn113c_%s.py' % name)", "    path = WORK / ('mut_vbn113d_%s.py' % name)"),
])
