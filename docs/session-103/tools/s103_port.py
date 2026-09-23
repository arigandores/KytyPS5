"""Fresh source-side s102 -> s103 harness port; never run a carried *_port.py.

Written in the SOURCE folder (C:/kyty/s102) as docs/next-session-103.md 2 requires.
Only Python root literals change globally.  Five root constructs, the live
sealed-path repair (r6, now 16 files / 27 constants: the thirteen inherited scorers plus
the three session-102 scorers m5_102.py (PRED and ADDENDUM - the second is not a PRED*
name; m5_plan.py and m5_rdlib.py import it), dab102.py (PRED, PRED05) and ckpt102.py
(PRED)) and the five scorers/tools whose PRED escapes const() (r7: the four session-99
scorers plus m5_recompile.py:41, a live tool M5' needs) are recorded separately in the
ledger.  No scorer, game or build is run.  The destination must not exist.
New session documents/scorers belong to their authors; inherited session
documents are archived under prev102 only.

Advances over s102_port.py, each asserted in preconditions():
  * COMMA chain 28 -> 29 roots (s103 ... s75); r1 splices s102 back in.
  * area_verdict.py range(103, 70, -1); shift91.py range(103, 66, -1).
  * s94lib.py 12 roots, bda93.py 13, stg92.py 14; regime94.py 11 roots + s103.
  * r6 grows 13 -> 16 files and 22 -> 27 constants.
  * r7 grows 4 -> 5 expression paths (m5_recompile.py PRED = ROOT + '/pred/...'); it has no
    PRED_SHA constant (the tool records sha256(PRED) at run time), so r7 entries now name
    their hash constant or None.
  * SEALED grows 21 -> 30 (the nine session-102 seals, pred/01..09, SEALS102.txt).
  * ABSENT grows 35 -> 36 ("dabatch", LAST row of KNOB_DEFINITIONS); gates.cpp must yield
    135 = 99 + 36 entries (111 gates + 24 knobs).
  * NEW_SESSION names session-103 files (m5_102.py and accept102.sh now exist in SRC).

Two changes of SHAPE, forced by the sources:
  * The inherited seals now live in TWO carried folders.  prev101/pred holds the twenty texts
    every live constant names; prev100/pred holds eighteen, seventeen of which are byte-identical
    duplicates of prev101/pred texts and one of which - session 100's 03_audit_addendum.md
    (10653 B, f3c2104b...) - exists nowhere else (its basename is taken in prev101/pred by
    session 101's addendum).  SEALED lists that one from prev100/pred, where it stays; the
    seventeen duplicates are verified byte-identical to their prev101/pred twins instead of
    being listed twice.  No session-102 name collides with any inherited name.
  * The ledger expectations (which files each repair fires on) are checked on the planned
    output BEFORE the destination is created, not only after it is written.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
SRC = Path('C:/kyty/s102')
DST = Path('C:/kyty/s103')
OLD, NEW = SRC.as_posix(), DST.as_posix()
GATES = Path('C:/kyty/KytyPS5/src/common/gates.cpp')
GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'
GATES_CPP_ENTRIES = 135  # 99 pinned in gates_base.txt + 36 ABSENT
GATES_CPP_SPLIT = (111, 24)  # DEFINITIONS rows, KNOB_DEFINITIONS rows
BIG = 5 * 1024 * 1024
SKIP_PREFIX = ('log_', 'stdout_', 'rec_', 'a80z_', 'hfx_')
SKIP_EXT = ('.mp4', '.idx', '.pyc', '.map', '.etl', '.exe')
SKIP_DIR = {'__pycache__', 'video99_comparison', 'video99_preview', 'video99_full',
            'video99_base_full'}
DOCS = ('README.md', 'FACTS.md', 'PLAN.md')
# Names a session-103 author may create; none may exist in SRC or arrive in DST.
NEW_SESSION = ('accept103.sh', 'fp103.py', 'm3_103.py', 'm5_103.py')
LEDGER_NAME = 'port103_ledger.json'
COMMA = {'arms.py': '--roots', 'baseline.py': '--roots', 'effect.py': '--extra-roots'}
ARITH = {'area_verdict.py': (70, 'r2'), 'shift91.py': (66, 'r3')}
TUPLES = {'stg92.py': 90, 'bda93.py': 91, 's94lib.py': 92}
DEGENERATE = ('area71_extract.py', 'clock_extract.py', 'area.py', 'area_band_check.py',
              'area_mix.py', 'area_summary.py', 'gputime.py', 'scene_point.py',
              'scene_clock.py', 'scene_drift.py', 'a80_statistics.py', 'cond80.py')
ABSENT = ('mutwide', 'bindpack', 'bindpackcheck', 'slotstat', 'slotstatcheck',
          'bdalap', 'plkstat', 'bindlap', 'bdasplit', 'bindpack2', 'bindpack2check',
          'bindkey', 'bdabits', 'bdabitscheck', 'proglap', 'drawmerge', 'drawmergecheck',
          'bindalt', 'bindwit', 'takelap', 'bufimp', 'bufimpcheck', 'stglap', 'copywake',
          'bdacap', 'mergecost', 'bdaall', 'framerep', 'pathlap', 'bindfloor', 'bfmode',
          'bfburn', 'bdaevery',
          # Session 100, measurement only: the 34th absent name.
          'blmove',
          # Session 101, measurement only, LAST row of gates.cpp DEFINITIONS: the 35th.
          'cbmove',
          # Session 102, knob KYTY_DRAW_AHEAD_BATCH (closed at its pilot), LAST row of
          # KNOB_DEFINITIONS: the 36th.
          'dabatch')
LAND = 'prev102/pred'
INHERITED = 'prev101/pred'
OLDER = 'prev100/pred'
# (source folder in SRC, name, bytes, sha256, landing folder in DST)
SEALED = (
    (INHERITED, '01_bindings_only.md', 10848, '8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d', LAND),
    (INHERITED, '01_floor_reversible.md', 15422, '7df5beb55cd964f58cd79a6b0caa697089cd3b20ea546e80ab2b10644f7d43af', LAND),
    (INHERITED, '01_hang_trigger.md', 19391, 'aca036c1a094c18176ad5ac04f69f9ed8a926bf81ac1d6f63760f8493c071cd3', LAND),
    (INHERITED, '01_pathlap.md', 12987, '94ea04b05e247f0bc7d13612cd27a0c46ea04907ac3d7aaf032f0df45696b212', LAND),
    (INHERITED, '01b_entry_hang.md', 4202, '3884109387e44f520b63fe5684340fc1828111dda30a7b99bdb9098ac41d49b6', LAND),
    (INHERITED, '02_bindfloor.md', 13039, 'e6c56dfcab222adac3e7541db1e2ae179d2c3b49f439dc5a53276d6aa39398c8', LAND),
    (INHERITED, '02_floor_walk.md', 12151, '9a88ab87a60789a2702bea4fb55939c6e578f25b4230482537361ee717f85519', LAND),
    (INHERITED, '02_m3_frame.md', 11825, '83144a3dfeff531eccd1da0bef91cdf882e4fcf4d6a70d8545f1ed9a53354389', LAND),
    (INHERITED, '02_settled_bindings.md', 13461, '1d1ebf286869ab59944fe135fc5c69d1315d4c61667b6c3dd2ab3ca14839724c', LAND),
    (INHERITED, '03_bdaevery.md', 8584, 'ada5682860cfd5ac5b61aefeeab1ea82eec29d4a80227974b84fb7b654c6dd0e', LAND),
    (INHERITED, '03_image_lifetime_diagnostic.md', 4724, 'd17745315149f0caad27f4c4764350f3e255fc9949a5b0287d9ea2a5e2c42c90', LAND),
    (INHERITED, '04_gc_audit.md', 7835, 'a93f4b6b1068cb34b06d02301d5c35f09483ef60f546f7669b03e193aeee611b', LAND),
    (INHERITED, '04_pathlap_identity.md', 6618, '584a13afcf07055086cb8b724695007d919846221bf096bab1407a64eaeb58f5', LAND),
    (INHERITED, '05_bdaevery_controls.md', 9087, '352448acaacd9b40fd0f01b77bdcf0b17a2cf708e7a928f3487db82f3d87c624', LAND),
    (INHERITED, '05_observer_separation.md', 8583, 'fb376ee63ce8fb19c7151e37c34ddc340fbecafc6aa648a27a9c160e7bc20af0', LAND),
    (INHERITED, '01_addend_census.md', 19152, '4c90060f91c21052238e0395abe2229e316012849c6bd54623d858edc5cf8c65', LAND),
    (INHERITED, '02_moved_mark.md', 11043, 'b1930f69f83a77d3bba359d4d18f0653f7fea6a331232dc9edaaf46c2a82e137', LAND),
    (INHERITED, '01_two_directional.md', 29915, '091ecf76b85ff828fae298375bc5db0cbf85f92e1ee3c6e943d7e40114daeff2', LAND),
    (INHERITED, '02_regime_addendum.md', 9735, 'b4ef078beeeaa08b89a9d0fc969adbcaa959941d5694d040dbec3194271f0b29', LAND),
    (INHERITED, '03_audit_addendum.md', 20259, '688b7be482402049a36913112eb022582a884b9c104453e77c7891c739fa974e', LAND),
    # Session 100's addendum, which WITHDREW the CLOSE of its pred/02.  Its basename is taken
    # in prev101/pred (and so in prev102/pred) by session 101's addendum; it stays in the
    # carried prev100/pred, where the walk carries it and FACTS of sessions 101-102 cite it.
    (OLDER, '03_audit_addendum.md', 10653, 'f3c2104b7a27b448a6c46a9526531c22e3d809546be5c51d90cca4e333ecad75', OLDER),
    # Session 102 (hashes as in SEALS102.txt).  pred/08 WITHDREW "M5 closes G"; pred/09 corrects
    # its lens tally.  All nine are immutable and travel byte-exact.
    ('pred', '01_m5_bench.md', 14288, 'cf3c353f7aaa4a2a16d7b59a61461cf26bef11ddbfffd59206ae95a8b6b33e0a', LAND),
    ('pred', '02_m5_addendum.md', 8007, 'ced6d4103c64b9e5b7c81a3a730cac6d2b04a08486f82cf43642b04a8701f4d3', LAND),
    ('pred', '03_dabatch.md', 6909, 'f828e2578a1e68e2dbf99e976be7ce49f4041e6631d96c4773f0d23642b6135e', LAND),
    ('pred', '04_checkpoints_fix.md', 4221, 'c131852e4b3a5c979ce93d2c4182849b641bcc53ce1f217373926de369e8fe87', LAND),
    ('pred', '05_dabatch_addendum.md', 2347, 'b889c57a6f8c0f56eaa3ac43f68e9ea168dfef32b4a7122cb0b918fee5e7686d', LAND),
    ('pred', '06_ckpt_entry_addendum.md', 1595, '7562c26f1b7d6432eef3bf5ff4c4d3a4d1901d4a351ff0c74961e735cb6434ab', LAND),
    ('pred', '07_m5_capture_retry.md', 1870, '55aabe82e9c347a6d5e92bb7b7f7f327d632e5b045877e9237794850ca63c3b8', LAND),
    ('pred', '08_audit_addendum.md', 6464, 'ee7e3397609f31ec96a307aed53f0daa9362909b1bcb7ec4f2e383cdc2d8385f', LAND),
    ('pred', '09_audit_tally_addendum.md', 2029, 'e205aeb6a3d815dbb5c30f8cc9f5aab8259b59b4a9660d17fd03b258923679f4', LAND),
)
SEALS_FILE = 'SEALS102.txt'
# Session 101's two texts that prev100/pred never held; every other prev101/pred text has a
# byte-identical twin in prev100/pred (and session 100's addendum is the one prev100/pred adds).
PREV101_ONLY = ('01_two_directional.md', '02_regime_addendum.md', '03_audit_addendum.md')
# r6: scorers whose PRED* (and m5_102.py's ADDENDUM) are bare quoted literals const() can read.
# The thirteen inherited ones now point into s102/prev101/pred; the three session-102 scorers
# point into s102/pred.  All land in s103/prev102/pred.
REPOINT = {
    'pl96.py': ('PRED',), 'bf96.py': ('PRED', 'PRED97', 'PRED97B'),
    'bd96.py': ('PRED', 'PRED5'), 'check_s96_counters.py': ('PRED1', 'PRED4'),
    'rv97.py': ('PRED', 'PRED2'), 'm3_97.py': ('PRED',),
    'trig98.py': ('PRED',), 'rv98.py': ('PRED', 'PRED98', 'PRED01B', 'PRED2'),
    'bf98.py': ('PRED98_2',), 'm3_98.py': ('PRED',),
    'cen100.py': ('PRED',), 'mov100.py': ('PRED',),
    'cm101.py': ('PRED', 'PRED2'),
    'm5_102.py': ('PRED', 'ADDENDUM'), 'dab102.py': ('PRED', 'PRED05'), 'ckpt102.py': ('PRED',),
}
# Files that read m5_102.ADDENDUM (and PRED) by import rather than by literal.
ADDENDUM_IMPORTERS = ('m5_plan.py', 'm5_rdlib.py')
# Scorers/tools whose PRED is a Path()/ROOT-relative expression, not the bare quoted literal
# const() can read (port repair 7).  It rewrites the relative part only, so the shape of each
# line and its neighbouring hash constant (if any) are untouched.
# (file, constant, source form, repaired form, sealed basename, sealed folder in SRC, hash constant)
REPOINT2 = (
    ('bf99.py', 'PRED', "PRED = Path('%s/prev101/pred/01_bindings_only.md')",
     "PRED = Path('%s/prev102/pred/01_bindings_only.md')", '01_bindings_only.md', INHERITED, 'PRED_SHA'),
    ('settled99.py', 'PRED', "PRED = ROOT / 'prev101/pred/02_settled_bindings.md'",
     "PRED = ROOT / 'prev102/pred/02_settled_bindings.md'", '02_settled_bindings.md', INHERITED, 'PRED_SHA'),
    ('settled99_gc.py', 'PRED', "PRED = ROOT / 'prev101/pred/04_gc_audit.md'",
     "PRED = ROOT / 'prev102/pred/04_gc_audit.md'", '04_gc_audit.md', INHERITED, 'PRED_SHA'),
    ('settled99_norec.py', 'PRED', "PRED = ROOT / 'prev101/pred/05_observer_separation.md'",
     "PRED = ROOT / 'prev102/pred/05_observer_separation.md'", '05_observer_separation.md', INHERITED, 'PRED_SHA'),
    # Session 102: the offline recompile/SASS tool M5' reuses.  ROOT = 'C:/kyty/s102' becomes
    # 'C:/kyty/s103' by the naive rewrite; pred/ is empty in every fresh root, so the relative
    # part must follow the text into prev102/pred.  No PRED_SHA: sha256(PRED) is recorded at run time.
    ('m5_recompile.py', 'PRED', "PRED = ROOT + '/pred/01_m5_bench.md'",
     "PRED = ROOT + '/prev102/pred/01_m5_bench.md'", '01_m5_bench.md', 'pred', None),
)
M5_RECOMPILE_ROOT = "ROOT = '%s'"
ARCHIVE_SCORERS = {'bf98_v1.py', 'bf98_v2.py', 'm3_98_v1.py', 'design98/rv98_before_N3.py',
                   'settled99.py', 'settled99_gc.py', 'settled99_norec.py', 'bf99.py',
                   'finalize99.py', 'finalize_cal99a.py',
                   'cen100.py', 'mov100.py', 'parent_recount100.py',
                   'parent_recount100_mov.py',
                   'cm101.py', 'parent_recount101.py',
                   # Session 102: pinned to their own seals, tags and binary 346ba4f6...; dab102.py and
                   # ckpt102.py also carry PRODUCTION_ROOT = 'C:/kyty/s102', which the naive rewrite
                   # moves to s103 where none of their logs live.  Carry, never run.
                   'm5_102.py', 'dab102.py', 'ckpt102.py'}
OLDER_SCORERS = ('fr95.py', 'fr95b.py', 'mc94.py', 'bda94.py', 'stg92.py', 'bda93.py', 'shift91.py')
# Archive verifier of an earlier port: it carries a literal copy of the comma chain at
# verify_port99/verify.py:39, so r1 legitimately fires on it as well as on the three
# live files.  It is evidence of the s98 -> s99 port and is never run here.
R1_ARCHIVE = ('verify_port99/verify.py',)
# Frozen evidence copies of const()-escaping scorers that repair 7 deliberately does
# NOT reach (repair is keyed by the top-level file name).  Their PRED is left dangling.
FROZEN_DANGLING = ('verify_gc99_scorer/frozen/settled99.py',
                   'verify_gc99_scorer/frozen/settled99_gc.py',
                   'verify_gc99_scorer/frozen/settled99_gc_original_failed.py')
# Session 102's pre-V2s copy of m5_recompile.py, kept as evidence in a subfolder: r7 is keyed by
# the top-level name, so its PRED (same ROOT + '/pred/...' form) is left dangling by design.
FROZEN_DANGLING_EXPR = (('m5/before_v2s/m5_recompile.py', "ROOT = '%s'", "PRED = ROOT + '/pred/01_m5_bench.md'"),)
# Offline tests that read their seal as HERE / 'pred/...'.  pred/ is empty in every
# freshly ported root, so these dangle; report only, never repaired: the port rewrites root
# literals, not test fixtures.
HERE_DANGLING = (('test_cen100.py', "pred = HERE / 'pred/01_addend_census.md'"),
                 ('test_mov100.py', "pred = HERE / 'pred/02_moved_mark.md'"),
                 ('test_cm101.py', "pred = HERE / 'pred/02_regime_addendum.md'"))
# Session 102's RenderDoc driver records the M5 seal hashes from ROOT / 'pred/...' INSIDE main()
# (not a module constant, not named by the plan's r7).  It is pinned to M5's seals, which M5'
# replaces anyway; report only, never repaired.  Run from s103 as is, it stops with
# FileNotFoundError before launching anything.
ROOT_DANGLING = (('m5_run.py', "seal_sha256={p.name: sha(p) for p in (ROOT / 'pred/01_m5_bench.md', "
                  "ROOT / 'pred/02_m5_addendum.md')},", ('01_m5_bench.md', '02_m5_addendum.md')),)
CARRIED_SHELLS = (('accept102.sh', 'R=C:/kyty/s102'), ('accept101.sh', 'R=C:/kyty/s101'),
                  ('accept100.sh', 'R=C:/kyty/s100'), ('accept99.sh', 'R=C:/kyty/s99'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rd(p):
    return p.read_bytes().decode('utf-8')


def chain(hi, lo, comma=False):
    values = ['C:/kyty/s%d' % i for i in range(hi, lo - 1, -1)]
    return ','.join(values) if comma else '(' + ', '.join(repr(v) for v in values) + ')'


def naive(t):
    for before, after in ((OLD, NEW), (OLD.replace('/', '\\\\'), NEW.replace('/', '\\\\')),
                          (OLD.replace('/', '\\'), NEW.replace('/', '\\')),
                          ('/c/kyty/s102', '/c/kyty/s103')):
        t = t.replace(before, after)
    return t


def const(t, name):
    m = re.search(r'^' + re.escape(name) + r"\s*=\s*'([^']*)'", t, re.M)
    assert m, ('missing string constant', name)
    return m.group(1)


def regime(hi):
    return "    root = next((r for r in %s if os.path.isfile('%%s/log_%%s.txt' %% (r, tag))), 'C:/kyty/s%d')" % (chain(hi, 93), hi)


def sealed_index():
    return {(d, n): (size, h, land) for d, n, size, h, land in SEALED}


def repair(t, key):
    out, fired = naive(t), set()
    def replace(tag, before, after, exact=True):
        nonlocal out
        if exact:
            assert out.count(before) == 1, (key, tag, 'anchor count', out.count(before))
        if before in out:
            out = out.replace(before, after)
            fired.add(tag)
    # Historically global: only these three LIVE files may fire; archive ports may fire too.
    replace('r1', 'C:/kyty/s103,C:/kyty/s101', 'C:/kyty/s103,C:/kyty/s102,C:/kyty/s101', False)
    if key in ARITH:
        floor, tag = ARITH[key]
        replace(tag, 'range(102, %d, -1)' % floor, 'range(103, %d, -1)' % floor)
    if key in TUPLES:
        replace('r4', naive(chain(102, TUPLES[key])), chain(103, TUPLES[key]))
    if key == 'regime94.py':
        replace('r5', naive(regime(102)), regime(103))
    for name in REPOINT.get(key, ()):
        path = const(t, name)
        old_line = "%s = '%s'" % (name, naive(path))
        new_line = "%s = '%s/%s/%s'" % (name, NEW, LAND, path.rsplit('/', 1)[1])
        replace('r6', old_line, new_line)
    for f, _name, before, after, _basename, _folder, _hash in REPOINT2:
        if key == f:
            replace('r7', naive(before % OLD) if '%s' in before else before,
                    after % NEW if '%s' in after else after)
    return out, sorted(fired)


def expected_ledger():
    return {'r1': sorted(list(COMMA) + list(R1_ARCHIVE)), 'r2': ['area_verdict.py'], 'r3': ['shift91.py'],
            'r4': sorted(TUPLES), 'r5': ['regime94.py'], 'r6': sorted(REPOINT),
            'r7': sorted(f for f, _, _, _, _, _, _ in REPOINT2)}


def check_ledger(fired_by_key, stage):
    live = {k: v for k, v in fired_by_key.items() if not k.endswith('_port.py')}
    for tag, want in expected_ledger().items():
        got = sorted(k for k, v in live.items() if tag in v)
        assert got == want, (stage, tag, got, want)
        if tag != 'r1':
            assert not any(tag in v for k, v in fired_by_key.items() if k.endswith('_port.py')), (stage, tag)
    return live


def preconditions():
    assert SRC.resolve() != DST.resolve()
    assert not DST.exists(), 'destination exists: do not rerun a completed port'
    assert not (SRC / 'prev102').exists()
    assert not (SRC / LEDGER_NAME).exists()
    for f, opt in COMMA.items():
        t = rd(SRC / f)
        m = re.search(r"add_argument\('" + re.escape(opt) + r"', default='([^']*)'", t)
        assert m and m.group(1) == chain(102, 75, True), f
        assert len(m.group(1).split(',')) == 28, f
    for f, (floor, _) in ARITH.items():
        assert rd(SRC / f).count('range(102, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(SRC / f).count(chain(102, floor)) == 1, f
    assert rd(SRC / 'regime94.py').count(regime(102)) == 1
    assert rd(SRC / 'regime94.py').splitlines()[2] == 'import os, re, sys, statistics'
    sealed = sealed_index()
    assert len(sealed) == len(SEALED) == 30
    # No two texts may land on one path, no text is renamed, and the only shared basename
    # is the pair of audit addenda of sessions 100 and 101 (session 102's is 08_audit_addendum.md).
    assert len({(land, n) for _, n, _, _, land in SEALED}) == 30
    names_all = [n for _, n, _, _, _ in SEALED]
    assert sorted({n for n in names_all if names_all.count(n) > 1}) == ['03_audit_addendum.md']
    s102_names = {n for d, n, _, _, _ in SEALED if d == 'pred'}
    assert len(s102_names) == 9 and not s102_names & {n for d, n, _, _, _ in SEALED if d != 'pred'}
    assert all(land in (LAND, d) for d, _, _, _, land in SEALED)
    assert sum(1 for _, _, _, _, land in SEALED if land == LAND) == 29
    assert [(d, n) for d, n, _, _, land in SEALED if land != LAND] == [(OLDER, '03_audit_addendum.md')]
    for folder in ('pred', INHERITED):
        assert sorted(p.name for p in (SRC / folder).iterdir()) == sorted(n for d, n, _, _, _ in SEALED if d == folder), folder
    # prev100/pred: session 100's addendum plus seventeen byte-identical twins of prev101/pred texts.
    older = sorted(p.name for p in (SRC / OLDER).iterdir())
    twins = sorted(n for d, n, _, _, _ in SEALED if d == INHERITED and n not in PREV101_ONLY)
    assert len(twins) == 17 and older == sorted(twins + ['03_audit_addendum.md']), older
    for n in twins:
        assert sha(SRC / OLDER / n) == sealed[(INHERITED, n)][1] == sha(SRC / INHERITED / n), ('twin', n)
    for d, n, size, h, _ in SEALED:
        assert (SRC / d / n).stat().st_size == size and sha(SRC / d / n) == h, (d, n)
    # The session's own seal record names exactly the nine session-102 texts, with these hashes.
    seals_rec = set()
    for line in rd(SRC / SEALS_FILE).splitlines():
        if line.strip():
            h, n = line.split()
            seals_rec.add((h, n.lstrip('*')))
    assert seals_rec == {(h, n) for d, n, _, h, _ in SEALED if d == 'pred'}, seals_rec
    live_paths = 0
    for f, names in REPOINT.items():
        t = rd(SRC / f)
        for name in names:
            p = Path(const(t, name))
            assert p.parent in (SRC / 'pred', SRC / INHERITED), (f, name, p)
            key = ('pred' if p.parent == SRC / 'pred' else INHERITED, p.name)
            assert const(t, name + '_SHA') == sealed[key][1] == sha(p), (f, name)
            assert sealed[key][2] == LAND, ('live constant names a text outside prev102/pred', f, name)
            live_paths += 1
    assert len(REPOINT) == 16 and live_paths == 27, (len(REPOINT), live_paths)
    for f in ADDENDUM_IMPORTERS:
        assert 'm5_102.ADDENDUM' in rd(SRC / f), f
    for f, name, before, _after, basename, folder, hash_const in REPOINT2:
        t = rd(SRC / f)
        anchor = before % OLD if '%s' in before else before
        assert t.count(anchor) == 1, ('r7 anchor', f, t.count(anchor))
        if hash_const is not None:
            assert const(t, hash_const) == sealed[(folder, basename)][1], f
        else:
            assert not re.search(r'^' + name + r'_SHA\s*=', t, re.M), f
        assert sealed[(folder, basename)][1] == sha(SRC / folder / basename), f
        assert sealed[(folder, basename)][2] == LAND, f
    assert len(REPOINT2) == 5
    assert rd(SRC / 'm5_recompile.py').count(M5_RECOMPILE_ROOT % OLD) == 1
    g = SRC / 'gates_base.txt'
    assert g.stat().st_size == 1092 and sha(g) == GATES_SHA
    names = [x.split('=')[0] for x in rd(g).split() if '=' in x]
    assert len(names) == len(set(names)) == 99
    text = rd(GATES)
    entry = r'\{\s*"KYTY_\w+",\s*"([a-z0-9]+)"'
    cpp = re.findall(entry, text)
    assert len(cpp) == len(set(cpp)) == GATES_CPP_ENTRIES, len(cpp)
    cut = text.index('KNOB_DEFINITIONS')
    split = (len(re.findall(entry, text[:cut])), len(re.findall(entry, text[cut:])))
    assert split == GATES_CPP_SPLIT, split
    assert re.findall(entry, text[cut:])[-1] == 'dabatch'
    assert len(ABSENT) == len(set(ABSENT)) == 36 == GATES_CPP_ENTRIES - 99
    assert set(ABSENT) == set(cpp) - set(names)
    assert not set(ABSENT) & set(names)
    assert all(not (SRC / f).exists() for f in NEW_SESSION)
    print('PRECONDITIONS PASS: 5 root constructs; 30 sealed texts (29 land in prev102/pred, 1 stays '
          'in carried prev100/pred); 27 live paths (16 files) + 5 expression paths; gates 1092 B / 99 names; '
          'gates.cpp 135 entries (111 gates + 24 knobs); ABSENT 36')


def main():
    preconditions()
    carried, ledger, skipped = [], {}, []
    planned = []
    # Preflight ALL decoding and repair anchors before writing the destination.
    for root, dirs, files in os.walk(SRC):
        rel = Path(root).relative_to(SRC)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIR and not (rel == Path('.') and (d == 'pred' or d.startswith('design103'))))
        for f in sorted(files):
            sp = Path(root) / f
            key = sp.relative_to(SRC).as_posix()
            if (f.startswith(SKIP_PREFIX) or f.endswith(SKIP_EXT) or sp.stat().st_size >= BIG
                    or (rel == Path('.') and f in DOCS)):
                skipped.append(key)
                continue
            output, fired = (repair(rd(sp), key) if f.endswith('.py') else (None, []))
            planned.append((key, output, fired, sha(sp)))
    # The ledger expectations hold on the PLAN, before anything is written.
    check_ledger({key: fired for key, _, fired, _ in planned if fired}, 'preflight')
    assert not any(key == LEDGER_NAME or key in NEW_SESSION for key, _, _, _ in planned)
    DST.mkdir()
    for key, output, fired, src_sha in planned:
        sp, dp = SRC / key, DST / key
        dp.parent.mkdir(parents=True, exist_ok=True)
        if output is None:
            shutil.copy2(sp, dp)
        else:
            dp.write_bytes(output.encode('utf-8'))
        carried.append((key, src_sha, sha(dp)))
        if fired:
            a, b = naive(rd(sp)).splitlines(), rd(dp).splitlines()
            assert len(a) == len(b), key
            ledger[key] = {'repairs': fired, 'lines': [i for i, (x, y) in enumerate(zip(a, b), 1) if x != y]}
    prev = DST / 'prev102'
    (prev / 'pred').mkdir(parents=True)
    (DST / 'pred').mkdir()
    for f in DOCS:
        if (SRC / f).is_file():
            shutil.copy2(SRC / f, prev / f)
    for d, n, _, _, land in SEALED:
        if land == LAND:
            shutil.copy2(SRC / d / n, DST / LAND / n)
    diagnostics(carried, ledger)
    (DST / LEDGER_NAME).write_text(json.dumps({'source': OLD, 'destination': NEW, 'files': ledger,
        'carried_count': len(carried), 'skipped_count': len(skipped), 'archive_scorers': sorted(ARCHIVE_SCORERS),
        'sealed_landing': ['%s/%s -> %s/%s' % (d, n, land, n) for d, n, _, _, land in SEALED]}, indent=2) + '\n', encoding='utf-8')
    print('PORT DIAGNOSTIC: clean; carried=%d ledger=%d skipped=%d' % (len(carried), len(ledger), len(skipped)))


def diagnostics(carried, ledger):
    live = check_ledger({k: v['repairs'] for k, v in ledger.items()}, 'written')
    for tag, want in expected_ledger().items():
        print('LEDGER %s PASS: %s' % (tag, ', '.join(want)))
    live = {k: ledger[k] for k in live}
    naive_regime = naive(rd(SRC / 'regime94.py'))
    blind = naive_regime.replace("'C:/kyty/s103', 'C:/kyty/s101'", "'C:/kyty/s103', 'C:/kyty/s102', 'C:/kyty/s101'")
    assert blind == naive_regime.replace(naive(regime(102)), regime(103))
    assert 'r4' not in live['regime94.py']['repairs']
    for key, src_sha, dst_sha in carried:
        assert sha(SRC / key) == src_sha, ('source changed during port', key)
        if not key.endswith('.py'):
            assert src_sha == dst_sha, ('non-Python drift', key)
        else:
            expected_text, _ = repair(rd(SRC / key), key)
            assert rd(DST / key) == expected_text, key
            if key not in ledger:
                assert rd(DST / key) == naive(rd(SRC / key)), key
    for f in DEGENERATE:
        assert f not in ledger and rd(DST / f) == naive(rd(SRC / f))
    print('INTEGRITY PASS: every carried file verified; 12 degenerate chains unchanged beyond naive rewrite')
    for f, opt in COMMA.items():
        m = re.search(r"add_argument\('" + re.escape(opt) + r"', default='([^']*)'", rd(DST / f))
        assert m and m.group(1) == chain(103, 75, True) and len(m.group(1).split(',')) == 29, f
    for f, (floor, _) in ARITH.items():
        assert rd(DST / f).count('range(103, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(DST / f).count(chain(103, floor)) == 1, f
    print('ADVANCE PASS: COMMA 29 roots; range(103, 70/66, -1); stg92 14, bda93 13, s94lib 12 roots')
    sealed = sealed_index()
    for f, names in REPOINT.items():
        t = rd(DST / f)
        for name in names:
            p = Path(const(t, name))
            assert p.parent == DST / LAND, (f, name, p)
            assert sha(p) == const(t, name + '_SHA') == const(rd(SRC / f), name + '_SHA')
    print('R6 PASS: %d constants in %d files -> %s' % (sum(len(v) for v in REPOINT.values()), len(REPOINT), LAND))
    for f in ADDENDUM_IMPORTERS:
        assert 'm5_102.ADDENDUM' in rd(DST / f), f
    print('IMPORTED SEAL PASS: %s read m5_102.PRED/ADDENDUM -> %s' % (', '.join(ADDENDUM_IMPORTERS), LAND))
    for f, name, _before, after, basename, folder, hash_const in REPOINT2:
        t = rd(DST / f)
        anchor = after % NEW if '%s' in after else after
        assert t.count(anchor) == 1, ('r7 result', f)
        p = DST / LAND / basename
        assert p.is_file() and sha(p) == sealed[(folder, basename)][1], f
        if hash_const is not None:
            assert sha(p) == const(t, hash_const), f
        print('R7 PASS: %s %s -> %s/%s%s' % (f, name, LAND, basename,
                                            '' if hash_const else ' (no hash constant; recorded at run time)'))
    t = rd(DST / 'm5_recompile.py')
    assert t.count(M5_RECOMPILE_ROOT % NEW) == 1
    assert (Path(NEW + '/prev102/pred/01_m5_bench.md')).is_file()
    assert len(list((DST / LAND).iterdir())) == 29
    for d, n, size, h, land in SEALED:
        p = DST / land / n
        assert p.stat().st_size == size and sha(p) == h == sha(SRC / d / n), (d, n)
        print('SEALED PASS: %s/%s %d B %s' % (land, n, size, h))
    inherited = sorted(p.name for p in (DST / INHERITED).iterdir())
    assert inherited == sorted(n for d, n, _, _, _ in SEALED if d == INHERITED)
    for d, n, _, h, _ in SEALED:
        if d == INHERITED:
            assert sha(DST / INHERITED / n) == h, n
    older = sorted(p.name for p in (DST / OLDER).iterdir())
    assert older == sorted(p.name for p in (SRC / OLDER).iterdir()) and len(older) == 18
    for n in older:
        assert sha(DST / OLDER / n) == sha(SRC / OLDER / n), n
    assert sha(DST / OLDER / '03_audit_addendum.md') == sealed[(OLDER, '03_audit_addendum.md')][1]
    print('CARRIED SEALED PASS: %s holds all %d session-99..101 texts byte-exact; %s holds %d byte-exact '
          '(session 100 addendum + 17 twins) (walk carry)' % (INHERITED, len(inherited), OLDER, len(older)))
    assert not list((DST / 'pred').iterdir())
    assert all(not (DST / f).exists() for f in DOCS + NEW_SESSION)
    for f in DOCS:
        if (SRC / f).is_file():
            assert sha(SRC / f) == sha(DST / 'prev102' / f)
    for f in sorted(ARCHIVE_SCORERS):
        assert (DST / f).is_file(), ('archive scorer missing', f)
        # r6/r7 only repoint a sealed path; they never make an archive scorer runnable.
        assert f not in live or set(live[f]['repairs']) <= {'r6', 'r7'}, ('archive scorer entered live repair', f)
        print('ARCHIVE, DO NOT RUN: %s; carried by naive rewrite (plus r6/r7 where listed)' % f)
    for f in ('dab102.py', 'ckpt102.py'):
        assert const(rd(DST / f), 'PRODUCTION_ROOT') == NEW, f
        print('ARCHIVE PRODUCTION_ROOT MOVED BY NAIVE REWRITE, REPORT ONLY: %s PRODUCTION_ROOT = %s (no %s log there)'
              % (f, NEW, f[:-3]))
    for name, root in CARRIED_SHELLS:
        assert root in rd(DST / name), ('%s no longer carries its own root' % name)
        print('CARRIED SHELL, DO NOT RUN: %s still sets %s (the port rewrites .py only)' % (name, root))
    for f in FROZEN_DANGLING:
        t = rd(DST / f)
        assert "ROOT = Path('%s')" % NEW in t and "PRED = ROOT / 'pred/" in t, f
        print('FROZEN EVIDENCE, PRED LEFT DANGLING BY DESIGN: %s' % f)
    for f, root_line, pred_line in FROZEN_DANGLING_EXPR:
        t = rd(DST / f)
        assert t.count(root_line % NEW) == 1 and t.count(pred_line) == 1, f
        assert f not in ledger, f
        print('FROZEN EVIDENCE, PRED LEFT DANGLING BY DESIGN: %s' % f)
    for f, line in HERE_DANGLING:
        assert rd(DST / f).count(line) == 1, f
        target = DST / 'pred' / line.rsplit('/', 1)[1].rstrip("'")
        assert not target.exists(), f
        print('HERE-RELATIVE TEST SEAL, DANGLING, REPORT ONLY: %s reads %s' % (f, target.relative_to(DST).as_posix()))
    for f, line, basenames in ROOT_DANGLING:
        t = rd(DST / f)
        assert t.count(line) == 1 and "ROOT = Path('%s')" % NEW in t, f
        for b in basenames:
            assert not (DST / 'pred' / b).exists() and (DST / LAND / b).is_file(), (f, b)
        print('ROOT-RELATIVE SEAL IN FUNCTION, DANGLING, REPORT ONLY: %s reads %s' %
              (f, ', '.join('pred/' + b for b in basenames)))
    for f in OLDER_SCORERS:
        for line in rd(DST / f).splitlines():
            if re.match(r'^PRED\w*\s*=', line) and '_SHA' not in line.split('=')[0]:
                print('OLDER PRED, REPORT ONLY: %s %s' % (f, line))
    roots = ast.literal_eval(re.search(r'^ROOTS = (.+)$', rd(DST / 's94lib.py'), re.M).group(1))
    assert roots == tuple('C:/kyty/s%d' % i for i in range(103, 91, -1))
    tests = [('dab102a', 102), ('ckpt102_entry1', 102), ('m5cap102b', 102),
             ('cm101a', 101), ('cm101c', 101), ('cm101d', 101),
             ('cen100a', 100), ('cen100b', 100), ('mov100a', 100), ('mov100b_entry1', 100),
             ('bf99g', 99), ('bf99h', 99), ('aa99plain', 99), ('eng99a4', 99), ('eng99c2', 99),
             ('cal99a', 99), ('life99a', 99), ('vis99base', 99), ('bf99e', 99),
             ('bf98a', 98), ('bf98c', 98), ('rv98a', 98), ('trig98a', 98),
             ('rv97a', 97), ('bd96b', 97), ('pl96a', 96), ('fr95a', 95), ('mc94a', 94),
             ('bl93a', 93), ('stg92a', 92)]
    for tag, n in tests:
        found = next((r for r in roots if (Path(r) / ('log_%s.txt' % tag)).is_file()), None)
        assert found == 'C:/kyty/s%d' % n, (tag, found)
        print('ROOT PASS: %s -> %s' % (tag, found))
    assert rd(DST / 'regime94.py').count(regime(103)) == 1
    for tag, n in tests:
        if n < 93:
            continue
        found = next((r for r in roots[:-1] if (Path(r) / ('log_%s.txt' % tag)).is_file()), NEW)
        assert found == 'C:/kyty/s%d' % n
    assert next((r for r in roots[:-1] if (Path(r) / 'log_nosuch103.txt').is_file()), NEW) == NEW
    stale = []
    for p in DST.glob('*.py'):
        if p.name.endswith('_port.py'):
            continue
        hits = [i for i, line in enumerate(rd(p).splitlines(), 1) if OLD in line]
        if hits:
            stale.append(p.name)
            assert len(hits) == 1, (p.name, hits)
    assert sorted(stale) == sorted(list(COMMA) + list(TUPLES) + ['regime94.py']), stale
    leaked = [p.relative_to(DST).as_posix() for p in DST.rglob('*') if p.is_file() and
              (p.name.startswith(('log_', 'stdout_', 'rec_')) or p.name.endswith(SKIP_EXT) or p.stat().st_size >= BIG)]
    assert not leaked, leaked
    g = DST / 'gates_base.txt'
    assert sha(g) == GATES_SHA and g.stat().st_size == 1092
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    result = subprocess.run([sys.executable, '-B', str(DST / 'gen_gates.py'), '--check'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    print('gen_gates.py --check exit=%d (expected out-of-date for deliberately pinned baseline)' % result.returncode)
    print(result.stdout.decode('utf-8', 'replace').strip())
    assert result.returncode in (0, 1), result.returncode
    assert sha(g) == GATES_SHA and sha(SRC / 'gates_base.txt') == GATES_SHA
    print('GATES PASS: check-only, unchanged SHA; no scorer/game/build invoked')


if __name__ == '__main__':
    main()
