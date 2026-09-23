"""Fresh source-side s105 -> s106 harness port; never run a carried *_port.py.

Written in the SOURCE folder (C:/kyty/s105) as docs/next-session-106.md 1 requires, modelled on
C:/kyty/s104/s105_port.py.  Only Python root literals change globally.  Five root constructs,
the live sealed-path repair of bare quoted literals (r6: now 20 files / 31 constants) and the
repair of sealed paths written as ROOT/Path expressions (r7: now 10 expression paths in 8 files)
are recorded separately in the ledger.  No scorer, game, build or GPU work is run.  The
destination must not exist.  New session documents/scorers belong to their authors; inherited
session documents are archived under prev105 only.

Advances over s105_port.py, each asserted in preconditions():
  * COMMA chain 31 -> 32 roots (s106 ... s75); r1 splices s105 back in.
  * area_verdict.py range(106, 70, -1); shift91.py range(106, 66, -1).
  * s94lib.py 15 roots, bda93.py 16, stg92.py 17; regime94.py 14 roots + s106.
  * SEALED grows 40 -> 44 (the four session-105 seals pred/01..04, SEALS105.txt).  42 land in
    prev105/pred; two stay where the walk carries them (the two older audit addenda, as before).
    No session-105 basename is taken in any carried seal folder (re-verified below).
  * r6 grows 18 -> 20 files and 29 -> 31 constants: lead105.PRED (lead105.py:28) and ctx105.PRED
    (ctx105.py:23, the FIXED scorer) are BARE quoted literals 'C:/kyty/s105/pred/...', which const()
    reads.  Both carry PRED_SHA and PRED_BYTES, checked against SEALS105.txt.  The eighteen
    inherited r6 files now read from s105/prev104/pred (a104/dwk104 included).
  * r7 grows 9 -> 10 expression paths in 7 -> 8 files: check105.py writes its seal as
    ROOT + '/pred/02_m31.md' (ROOT = 'C:/kyty/s105'), so it is r7, not r6.  It has no PRED_SHA
    (it records the seal hash at run time).  The nine inherited r7 paths now read from
    s105/prev104/pred.
  * gates_base.txt unchanged: 1092 B / 99 names, sha256 303a7849... (dawalk=1); gates_base.json
    unchanged (3343 B, 2b79c3cf...).  ctxtick is NOT in gates_base.txt (it takes its compiled
    default 1).  Session 105's gates_ctx1.txt / gates_ctx2.txt are carried as archive data: each
    is gates_base.txt plus one appended token, ctxtick=1 / ctxtick=2.
  * gates.cpp 136 entries (111 gates + 25 knobs; ctxtick is the LAST knob row); ABSENT 36 -> 37.
  * Session-105 tools lead105.py, ctx105.py, check105.py are archive scorers (pinned to their
    seals, tags, binary and gates baseline); make_ctx105.py is a one-shot generator; go105.sh and
    go105b.sh are carried shells.  None is ever re-run.
  * NEW_SESSION names session-106 files.

Changes of SHAPE, forced by the sources:
  * The inherited seals now live in FIVE carried folders.  prev104/pred holds 38 texts (every
    text an inherited live constant names); prev103/pred holds 34, thirty-three byte-identical
    twins of prev104/pred texts plus session 103's 04_audit_addendum.md (4345 B, cdc9bab4...);
    prev102/pred holds 29 twins; prev101/pred 20 twins; prev100/pred 18, seventeen twins plus
    session 100's 03_audit_addendum.md (10653 B, f3c2104b...).  Twins are verified byte-identical
    instead of being listed twice.
  * The two basename collisions are inherited unchanged: prev105/pred/04_audit_addendum.md is
    session 104's (as in prev104/pred), session 103's stays in the carried prev103/pred;
    prev105/pred/03_audit_addendum.md is session 101's, session 100's stays in prev100/pred.
    SEALED lists the two older texts from their carried folders with landing = that folder.
  * Frozen evidence of the session-105 audit, audit105/recount_protocol/ctx105_git.py (the
    committed, pre-fix ctx105.py), carries a bare PRED literal; r6 is keyed by the top-level file
    name, so its PRED is left dangling by design (report only), like verify_gc99_scorer/frozen/.
  * The source root has FACTS.md but no README.md / PLAN.md: only FACTS.md goes to prev105/.
    Session 105's build notes m31_notes.md are carried at the root like every other working
    document (M1_RESULT.md, M5P_RUNBOOK.md, ...); only README/FACTS/PLAN are prev-only.
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
SRC = Path('C:/kyty/s105')
DST = Path('C:/kyty/s106')
OLD, NEW = SRC.as_posix(), DST.as_posix()
GATES = Path('C:/kyty/KytyPS5/src/common/gates.cpp')
GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'  # dawalk=1 (shipped s104)
GATES_JSON = (3343, '2b79c3cf9240ab9f43e2430f3dacd290c48ca71f32bab78730515f2864efd8d0')
PRESHIP_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'  # dawalk=0
CTX1_SHA = 'b7c89fae21292ecb414e7fdd5dffe3ad7d78020eba200b0e9f665c17c5dbfb61'  # gates_base + ctxtick=1
CTX2_SHA = '207ae3016740f7ff1ebffe83623dd20c6759795ec8f1c217229da4a3b96562c2'  # gates_base + ctxtick=2
# Archive data (sessions 104 and 105): carried byte-exact, never a baseline.
ARCHIVE_DATA = (('gates_base.pre104ship.txt', 1092, PRESHIP_SHA),
                ('gates_base.pre104ship.json', 3581, '6d256a31d8e817103bf3db2b2af19c89597ebddf9dc7a94678809caa122f2a5b'),
                ('gates_dawalk1.txt', 1493, 'cdc6568e7a347a7e834c11372e5f30eae2ae91f6f52bbec57d6e0aa51cfa0e7e'),
                ('gates_nodawalk.txt', 1082, '0931a79a8f1f6de21a81a8876d68d68d713f87bd5ddf20319f520228577c4f3b'),
                # Session 105 (next-session-106.md 1): the P1/P4 and video gate files of pred/02_m31.md.
                ('gates_ctx1.txt', 1102, CTX1_SHA),
                ('gates_ctx2.txt', 1102, CTX2_SHA))
CTX_FILES = (('gates_ctx1.txt', 'ctxtick=1'), ('gates_ctx2.txt', 'ctxtick=2'))
GATES_CPP_ENTRIES = 136  # 99 pinned in gates_base.txt + 37 ABSENT
GATES_CPP_SPLIT = (111, 25)  # DEFINITIONS rows, KNOB_DEFINITIONS rows
BIG = 5 * 1024 * 1024
SKIP_PREFIX = ('log_', 'stdout_', 'rec_', 'a80z_', 'hfx_')
SKIP_EXT = ('.mp4', '.idx', '.pyc', '.map', '.etl', '.exe')
SKIP_DIR = {'__pycache__', 'video99_comparison', 'video99_preview', 'video99_full',
            'video99_base_full'}
DOCS = ('README.md', 'FACTS.md', 'PLAN.md')
DOCS_PRESENT = ('FACTS.md',)  # session 105 wrote no README.md and no PLAN.md at its root
# Names a session-106 author may create; none may exist in SRC or arrive in DST.
NEW_SESSION = ('accept106.sh', 'go106.sh', 'go106b.sh', 'SEALS106.txt', 'm32_notes.md')
LEDGER_NAME = 'port106_ledger.json'
PREV_LEDGER = 'port105_ledger.json'  # the previous port's ledger: carried as plain data
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
          # Session 102, knob KYTY_DRAW_AHEAD_BATCH (closed at its pilot): the 36th.  Sessions 103
          # and 104 added no gate or knob.
          'dabatch',
          # Session 105, knob KYTY_CTX_TICK (default 1, 0..3), LAST row of KNOB_DEFINITIONS: the 37th.
          'ctxtick')
LAND = 'prev105/pred'
INHERITED = 'prev104/pred'
CARRIED103 = 'prev103/pred'
CARRIED102 = 'prev102/pred'
CARRIED101 = 'prev101/pred'
OLDER = 'prev100/pred'
CARRIED = (INHERITED, CARRIED103, CARRIED102, CARRIED101, OLDER)
# (source folder in SRC, name, bytes, sha256, landing folder in DST)
SEALED = (
    # Sessions 96..101 (twenty texts; prev103/prev102/prev101/pred hold byte-identical twins).
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
    # Session 102 (nine texts, as in SEALS102.txt); prev104, prev103 and prev102/pred.
    (INHERITED, '01_m5_bench.md', 14288, 'cf3c353f7aaa4a2a16d7b59a61461cf26bef11ddbfffd59206ae95a8b6b33e0a', LAND),
    (INHERITED, '02_m5_addendum.md', 8007, 'ced6d4103c64b9e5b7c81a3a730cac6d2b04a08486f82cf43642b04a8701f4d3', LAND),
    (INHERITED, '03_dabatch.md', 6909, 'f828e2578a1e68e2dbf99e976be7ce49f4041e6631d96c4773f0d23642b6135e', LAND),
    (INHERITED, '04_checkpoints_fix.md', 4221, 'c131852e4b3a5c979ce93d2c4182849b641bcc53ce1f217373926de369e8fe87', LAND),
    (INHERITED, '05_dabatch_addendum.md', 2347, 'b889c57a6f8c0f56eaa3ac43f68e9ea168dfef32b4a7122cb0b918fee5e7686d', LAND),
    (INHERITED, '06_ckpt_entry_addendum.md', 1595, '7562c26f1b7d6432eef3bf5ff4c4d3a4d1901d4a351ff0c74961e735cb6434ab', LAND),
    (INHERITED, '07_m5_capture_retry.md', 1870, '55aabe82e9c347a6d5e92bb7b7f7f327d632e5b045877e9237794850ca63c3b8', LAND),
    (INHERITED, '08_audit_addendum.md', 6464, 'ee7e3397609f31ec96a307aed53f0daa9362909b1bcb7ec4f2e383cdc2d8385f', LAND),
    (INHERITED, '09_audit_tally_addendum.md', 2029, 'e205aeb6a3d815dbb5c30f8cc9f5aab8259b59b4a9660d17fd03b258923679f4', LAND),
    # Session 103 (five texts, as in SEALS103.txt).  Four are in prev104/pred and land again.
    (INHERITED, '01_bvh_cap_series.md', 5057, '788f679c0676e47714e154aca86a3336e3f31274d7492113d0a1f8b11c071541', LAND),
    (INHERITED, '02_m5p_bench.md', 6183, '4035a9b0cc6ae89a671706a12731b3e0f21f29c2caa90763f61c0fab4b688a67', LAND),
    (INHERITED, '03_m5p_addendum.md', 1435, '73a7be0d895979b9d458e44c9251ad48d2be9d94c5f6b03d28d7d290b49bb894', LAND),
    (INHERITED, '05_claims_addendum.md', 2141, '7b313d96fefe9379eee5816ca824f94d6000cb4be055b3ae13c72fd19f31a607', LAND),
    # Session 103's four-lens audit addendum.  Its basename is taken in prev104/pred and prev105/pred
    # by session 104's addendum; it stays in the carried prev103/pred.  No live constant names it.
    (CARRIED103, '04_audit_addendum.md', 4345, 'cdc9bab4e9f9ab4d2088a740dcb82c1a0c95a0032e44db23a3007f0e97ec45b0', CARRIED103),
    # Session 100's addendum, which WITHDREW the CLOSE of its pred/02.  Its basename is taken in
    # prev101..prev105/pred by session 101's addendum; it stays in the carried prev100/pred.
    (OLDER, '03_audit_addendum.md', 10653, 'f3c2104b7a27b448a6c46a9526531c22e3d809546be5c51d90cca4e333ecad75', OLDER),
    # Session 104 (five texts, as in SEALS104.txt); now in prev104/pred.
    (INHERITED, '01_reg104.md', 1277, 'd0cdbae98131b5a4d3d8ac782ef23aca3153d6388d43fd05f5dc77df8530cd08', LAND),
    (INHERITED, '02_a_stage1.md', 16476, '29324c0c29603250255b5879d48ae2e9d8574672ef7291ceb27ebc44de2fbb8a', LAND),
    (INHERITED, '03_dawalk.md', 8515, '5f088c02c55b185e8f591ce403b0363b70c61a53bcd088b13354fec78e1d4a13', LAND),
    (INHERITED, '04_audit_addendum.md', 4243, 'd44b59750d09bd9fb605af3339d49f3acc301477a715e4a08415fe2227f435b8', LAND),
    (INHERITED, '05_claims104_addendum.md', 2296, 'd2aea285ac9aaf3e365a9781ba3fc65311a846eb96b247d7eee7869a78b61809', LAND),
    # Session 105 (hashes as in SEALS105.txt).  pred/01 seals lead105.py (dawalklead ABBA), pred/02
    # the M3.1 acceptance (ctx105.py P2, check105.py P1/P3/P4), pred/03 the ctx105 scorer fix,
    # pred/04 the audit.
    ('pred', '01_dawalklead.md', 3715, '7dca62cf623edf98782f0642f40432f460ffaa32237193d449c55bc3fd637e27', LAND),
    ('pred', '02_m31.md', 3927, 'c731a5477daf0a01bae83d04b1b962a2f768f37c9b940f8bb257a3b4b30b9449', LAND),
    ('pred', '03_scorer_fix.md', 1457, '66cd90e5def18120cbdfd362fef39309898b236fa959f664c64d5b9a5411e656', LAND),
    ('pred', '04_audit105.md', 5412, '2853aa9c8847c8777456e3cc1236f9753d0e338680b043615471fff95d05459e', LAND),
)
SEALS_FILE = 'SEALS105.txt'
S102_NAMES = ('01_m5_bench.md', '02_m5_addendum.md', '03_dabatch.md', '04_checkpoints_fix.md',
              '05_dabatch_addendum.md', '06_ckpt_entry_addendum.md', '07_m5_capture_retry.md',
              '08_audit_addendum.md', '09_audit_tally_addendum.md')
S103_NAMES = ('01_bvh_cap_series.md', '02_m5p_bench.md', '03_m5p_addendum.md', '04_audit_addendum.md',
              '05_claims_addendum.md')
S104_NAMES = ('01_reg104.md', '02_a_stage1.md', '03_dawalk.md', '04_audit_addendum.md',
              '05_claims104_addendum.md')
S105_NAMES = ('01_dawalklead.md', '02_m31.md', '03_scorer_fix.md', '04_audit105.md')
# Every session's own seal record, re-read against SEALED: (record, names, folder of each text).
SEAL_RECORDS = (('SEALS105.txt', S105_NAMES, {}),
                ('SEALS104.txt', S104_NAMES, {}),
                ('SEALS103.txt', S103_NAMES, {'04_audit_addendum.md': CARRIED103}),
                ('SEALS102.txt', S102_NAMES, {}))
# Session 101's texts that prev100/pred never held (prev101/pred holds all twenty sessions 96..101 texts).
PREV101_ONLY = ('01_two_directional.md', '02_regime_addendum.md', '03_audit_addendum.md')
# r6: scorers whose PRED* (and m5_102.py's ADDENDUM) are bare quoted literals const() can read.
# Eighteen point into s105/prev104/pred, the two session-105 scorers into s105/pred; all land in
# s106/prev105/pred.
REPOINT = {
    'pl96.py': ('PRED',), 'bf96.py': ('PRED', 'PRED97', 'PRED97B'),
    'bd96.py': ('PRED', 'PRED5'), 'check_s96_counters.py': ('PRED1', 'PRED4'),
    'rv97.py': ('PRED', 'PRED2'), 'm3_97.py': ('PRED',),
    'trig98.py': ('PRED',), 'rv98.py': ('PRED', 'PRED98', 'PRED01B', 'PRED2'),
    'bf98.py': ('PRED98_2',), 'm3_98.py': ('PRED',),
    'cen100.py': ('PRED',), 'mov100.py': ('PRED',),
    'cm101.py': ('PRED', 'PRED2'),
    'm5_102.py': ('PRED', 'ADDENDUM'), 'dab102.py': ('PRED', 'PRED05'), 'ckpt102.py': ('PRED',),
    'a104.py': ('PRED',), 'dwk104.py': ('PRED',),
    # Session 105 (next-session-106.md 1): lead105.py:28 and ctx105.py:23, bare literals.
    'lead105.py': ('PRED',), 'ctx105.py': ('PRED',),
}
REPOINT_FOLDER = {'lead105.py': 'pred', 'ctx105.py': 'pred'}  # default INHERITED
# Files that read a repaired seal by import rather than by literal: (file, required text).
IMPORTERS = (('m5_plan.py', 'm5_102.ADDENDUM'), ('m5_rdlib.py', 'm5_102.ADDENDUM'),
             ('m5p_recompile.py', 'm5p_103.PRED'), ('m5p_recompile.py', 'm5p_103.PARENT01'),
             ('m5p_plan.py', 'm5p_103.PRED'), ('m5p_plan.py', 'm5p_103.PARENT01'),
             ('m5p_plan.py', 'm5p_103.PARENT02'), ('rd_m5p_equal.py', 'import m5p_103'),
             ('rd_m5p_bench.py', 'import m5p_103'), ('m5p_run.py', 'm5p_103.seal_hashes()'),
             ('test_m5p_103.py', 'import m5p_103'), ('series103.py', 'bvh103.PRED'))
# Offline tests that import a session-104 scorer but REPLACE its seal with a temporary one
# (S.PRED = str(SEAL)); they never read the sealed text.  Report only.
SEAL_OVERRIDE_TESTS = (('test_a104.py', 'import a104 as S', 'S.PRED = str(SEAL)'),
                       ('test_dwk104.py', 'import dwk104 as S', 'S.PRED = str(SEAL)'))
# Scorers/tools whose seal path is a Path()/ROOT-relative expression, not the bare quoted literal
# const() can read (port repair 7).  It rewrites the relative part only, so the shape of each
# line, any trailing comment and its neighbouring hash constant (if any) are untouched.
# (file, constant, source form, repaired form, sealed basename, sealed folder in SRC, hash constant)
REPOINT2 = (
    ('bf99.py', 'PRED', "PRED = Path('%s/prev104/pred/01_bindings_only.md')",
     "PRED = Path('%s/prev105/pred/01_bindings_only.md')", '01_bindings_only.md', INHERITED, 'PRED_SHA'),
    ('settled99.py', 'PRED', "PRED = ROOT / 'prev104/pred/02_settled_bindings.md'",
     "PRED = ROOT / 'prev105/pred/02_settled_bindings.md'", '02_settled_bindings.md', INHERITED, 'PRED_SHA'),
    ('settled99_gc.py', 'PRED', "PRED = ROOT / 'prev104/pred/04_gc_audit.md'",
     "PRED = ROOT / 'prev105/pred/04_gc_audit.md'", '04_gc_audit.md', INHERITED, 'PRED_SHA'),
    ('settled99_norec.py', 'PRED', "PRED = ROOT / 'prev104/pred/05_observer_separation.md'",
     "PRED = ROOT / 'prev105/pred/05_observer_separation.md'", '05_observer_separation.md', INHERITED, 'PRED_SHA'),
    ('m5_recompile.py', 'PRED', "PRED = ROOT + '/prev104/pred/01_m5_bench.md'",
     "PRED = ROOT + '/prev105/pred/01_m5_bench.md'", '01_m5_bench.md', INHERITED, None),
    ('bvh103.py', 'PRED', "PRED = ROOT + '/prev104/pred/01_bvh_cap_series.md'",
     "PRED = ROOT + '/prev105/pred/01_bvh_cap_series.md'", '01_bvh_cap_series.md', INHERITED, None),
    ('m5p_103.py', 'PRED', "PRED = ROOT + '/prev104/pred/02_m5p_bench.md'",
     "PRED = ROOT + '/prev105/pred/02_m5p_bench.md'", '02_m5p_bench.md', INHERITED, 'PRED_SHA'),
    ('m5p_103.py', 'PARENT01', "PARENT01 = ROOT + '/prev104/pred/01_m5_bench.md'",
     "PARENT01 = ROOT + '/prev105/pred/01_m5_bench.md'", '01_m5_bench.md', INHERITED, 'PARENT01_SHA'),
    ('m5p_103.py', 'PARENT02', "PARENT02 = ROOT + '/prev104/pred/02_m5_addendum.md'",
     "PARENT02 = ROOT + '/prev105/pred/02_m5_addendum.md'", '02_m5_addendum.md', INHERITED, 'PARENT02_SHA'),
    # Session 105 (next-session-106.md 1): check105.py:18, ROOT = 'C:/kyty/s105' at :17.
    ('check105.py', 'PRED', "PRED = ROOT + '/pred/02_m31.md'",
     "PRED = ROOT + '/prev105/pred/02_m31.md'", '02_m31.md', 'pred', None),
)
# How each r7 file names its root (so the relative part resolves against the port root).
R7_ROOT_LINE = {'bf99.py': None, 'settled99.py': "ROOT = Path('%s')", 'settled99_gc.py': "ROOT = Path('%s')",
                'settled99_norec.py': "ROOT = Path('%s')", 'm5_recompile.py': "ROOT = '%s'",
                'bvh103.py': "ROOT = '%s'", 'm5p_103.py': "ROOT = '%s'", 'check105.py': "ROOT = '%s'"}
ARCHIVE_SCORERS = {'bf98_v1.py', 'bf98_v2.py', 'm3_98_v1.py', 'design98/rv98_before_N3.py',
                   'settled99.py', 'settled99_gc.py', 'settled99_norec.py', 'bf99.py',
                   'finalize99.py', 'finalize_cal99a.py',
                   'cen100.py', 'mov100.py', 'parent_recount100.py',
                   'parent_recount100_mov.py',
                   'cm101.py', 'parent_recount101.py',
                   'm5_102.py', 'dab102.py', 'ckpt102.py',
                   'bvh103.py', 'series103.py', 'identity_sweep.py', 'm5p_103.py', 'm5p_recompile.py',
                   'm5p_plan.py', 'm5p_run.py', 'rd_m5p_equal.py', 'rd_m5p_bench.py', 'test_m5p_103.py',
                   'a104.py', 'dwk104.py', 'test_a104.py', 'test_dwk104.py',
                   # Session 105 (next-session-106.md 1): pinned to their own seals, tags, binary and
                   # gates baseline.  ctx105.py is the FIXED scorer (pred/03).  Carry, never re-run.
                   'lead105.py', 'ctx105.py', 'check105.py'}
# Archive tools whose run root the naive rewrite moves to s106, where none of their inputs live.
# (file, constant, what it would miss there)
ROOT_MOVED = (('dab102.py', 'PRODUCTION_ROOT', 'log_dab102a.txt (in s102)'),
              ('ckpt102.py', 'PRODUCTION_ROOT', 'log_ckpt102*.txt (in s102)'),
              ('bvh103.py', 'ROOT', 'log_ent103_NN.txt (in s103)'),
              ('series103.py', 'ROOT', 'nothing - it LAUNCHES THE GAME; never run'),
              ('m5p_103.py', 'ROOT', 'its seals are repaired by r7; m5p/real outputs are the carried copies'),
              ('m5p_recompile.py', 'ROOT', 'writes into the carried m5p/; never run'),
              ('a104.py', 'PRODUCTION_ROOT', 'log_mut104.txt, log_mut104b.txt, log_sh104.txt (in s104)'),
              ('dwk104.py', 'PRODUCTION_ROOT', 'log_dwk104.txt, vwk104 video files (in s104)'),
              ('lead105.py', 'PRODUCTION_ROOT', 'log_lead105.txt (in s105)'),
              ('ctx105.py', 'PRODUCTION_ROOT', 'log_abb105.txt (in s105)'),
              ('check105.py', 'ROOT', 'log_ctx105/vct105/ect105_NN/reg105a/reg105b.txt (in s105); its seal is repaired by r7'),
              ('audit105/recount_protocol/p1p4.py', 'R', 'the session-105 logs (in s105); audit evidence, never run'),
              ('audit105/recount_protocol/recount.py', 'root', 'the session-105 logs (in s105); audit evidence, never run'))
# Session-104 archive scorers pin the PRE-SHIP gates baseline; after the naive rewrite their
# GATES_FILE names the s106 copy, which holds the shipped dawalk=1 text.  Report only.
GATES_PINNED = ('a104.py', 'dwk104.py')
# Session-105 archive scorers pin the CURRENT baseline (303a7849...); the pin still holds in s106.
GATES_CURRENT = ('lead105.py', 'ctx105.py')
BINARY_PINNED = ('a104.py', 'dwk104.py', 'lead105.py', 'ctx105.py')
# Offline tests whose optional real-log case reads a log the port never carries.  Report only.
TEST_LOG_MOVED = (('test_a104.py', "'%s/log_reg104.txt'"), ('test_dwk104.py', "'%s/log_reg104.txt'"))
# One-shot scripts of sessions 103..105 (patches of the source tree and of the session documents,
# and session 105's generator of ctx105.py).  Carried by naive rewrite, never run.
ONE_SHOT = ('patch_s103_bdalean.py', 'patch_s103_envflag.py', 'patch_s103_loopcap.py',
            'patch_s103_loopcap_host.py', 'facts_audit_fix.py', 'claims_fix.py', 'roadmap_s103.py',
            'claude_md_s103.py', 'handoff_s103.py',
            'claims_fix104.py', 'claude_md_s104.py',
            'make_ctx105.py')
# target <root>/FACTS.md -> s106 after the naive rewrite
ONE_SHOT_MOVED = ('facts_audit_fix.py', 'claims_fix.py', 'claims_fix104.py')
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
FROZEN_DANGLING_EXPR = (('m5/before_v2s/m5_recompile.py', "ROOT = '%s'", "PRED = ROOT + '/pred/01_m5_bench.md'"),)
# Frozen evidence with a BARE literal that r6 (keyed by the top-level name) deliberately does not
# reach: the session-105 audit's copy of the committed, pre-fix ctx105.py.  (file, line, basename)
FROZEN_DANGLING_BARE = (('audit105/recount_protocol/ctx105_git.py', "PRED = '%s/pred/02_m31.md'", '02_m31.md'),)
# Offline tests that read their seal as HERE / 'pred/...'; report only, never repaired.
HERE_DANGLING = (('test_cen100.py', "pred = HERE / 'pred/01_addend_census.md'"),
                 ('test_mov100.py', "pred = HERE / 'pred/02_moved_mark.md'"),
                 ('test_cm101.py', "pred = HERE / 'pred/02_regime_addendum.md'"))
# Seal reads inside a function body (not a module constant); report only, never repaired.
# (file, exact text in DST, seal basenames it names under <root>/pred/)
ROOT_DANGLING = (
    ('m5_run.py', "seal_sha256={p.name: sha(p) for p in (ROOT / 'pred/01_m5_bench.md', "
     "ROOT / 'pred/02_m5_addendum.md')},", ('01_m5_bench.md', '02_m5_addendum.md')),
    # Session 103's audit recount scripts (evidence of the four-lens audit, prev103/pred/04).
    ('audit103/recount/ent_recount.py', "open(ROOT + '/pred/01_bvh_cap_series.md', 'rb')",
     ('01_bvh_cap_series.md',)),
    ('audit103/recount/m5p_recount.py', "sha('%s/pred/02_m5p_bench.md')" % NEW, ('02_m5p_bench.md',)),
    ('audit103/recount/m5p_recount.py', "sha('%s/pred/03_m5p_addendum.md')" % NEW, ('03_m5p_addendum.md',)),
)
CARRIED_SHELLS = (('accept102.sh', 'R=C:/kyty/s102'), ('accept101.sh', 'R=C:/kyty/s101'),
                  ('accept100.sh', 'R=C:/kyty/s100'), ('accept99.sh', 'R=C:/kyty/s99'),
                  ('m5p_go.sh', 'OUT=C:/kyty/s103/m5p/real'),
                  ('audit103/fidelity/run_var.sh', 'cd /c/kyty/s103/audit103/fidelity'),
                  ('go104.sh', 'cd /c/kyty/s104'), ('go104b.sh', 'cd /c/kyty/s104'),
                  # Session 105's run chains (they ENTER THE GAME; never run).
                  ('go105.sh', 'cd /c/kyty/s105'), ('go105b.sh', 'cd /c/kyty/s105'))
# Tag -> session whose root holds log_<tag>.txt (logs are never carried).
ROOT_TESTS = (('lead105', 105), ('abb105', 105), ('ctx105', 105), ('reg105a', 105), ('reg105b', 105),
              ('vct105', 105), ('vid105', 105), ('ect105_01', 105), ('ect105_10', 105),
              ('reg104', 104), ('sh104', 104), ('mut104', 104), ('mut104b', 104), ('dwk104', 104),
              ('vwk104', 104), ('vid104', 104), ('seed104', 104), ('seedcheck', 104),
              ('ent103_01', 103), ('ent103_42', 103), ('ent103_67', 103), ('ent103_warm', 103),
              ('vid103', 103),
              ('dab102a', 102), ('ckpt102_entry1', 102), ('m5cap102b', 102),
              ('cm101a', 101), ('cm101c', 101), ('cm101d', 101),
              ('cen100a', 100), ('cen100b', 100), ('mov100a', 100), ('mov100b_entry1', 100),
              ('bf99g', 99), ('bf99h', 99), ('aa99plain', 99), ('eng99a4', 99), ('eng99c2', 99),
              ('cal99a', 99), ('life99a', 99), ('vis99base', 99), ('bf99e', 99),
              ('bf98a', 98), ('bf98c', 98), ('rv98a', 98), ('trig98a', 98),
              ('rv97a', 97), ('bd96b', 97), ('pl96a', 96), ('fr95a', 95), ('mc94a', 94),
              ('bl93a', 93), ('stg92a', 92))


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
                          ('/c/kyty/s105', '/c/kyty/s106')):
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


def rel_of(line):
    """The root-relative part of an r7 line: 'prev10N/pred/<name>' or 'pred/<name>'."""
    m = re.search(r"((?:prev\d+/)?pred/[^']+)'", line)
    assert m, line
    return m.group(1)


def r7_files():
    return sorted({f for f, _, _, _, _, _, _ in REPOINT2})


def repair(t, key):
    out, fired = naive(t), set()
    def replace(tag, before, after, exact=True):
        nonlocal out
        if exact:
            assert out.count(before) == 1, (key, tag, 'anchor count', out.count(before))
        if before in out:
            out = out.replace(before, after)
            fired.add(tag)
    # Historically global: only these LIVE files may fire; archive ports may fire too.
    replace('r1', 'C:/kyty/s106,C:/kyty/s104', 'C:/kyty/s106,C:/kyty/s105,C:/kyty/s104', False)
    if key in ARITH:
        floor, tag = ARITH[key]
        replace(tag, 'range(105, %d, -1)' % floor, 'range(106, %d, -1)' % floor)
    if key in TUPLES:
        replace('r4', naive(chain(105, TUPLES[key])), chain(106, TUPLES[key]))
    if key == 'regime94.py':
        replace('r5', naive(regime(105)), regime(106))
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
            'r4': sorted(TUPLES), 'r5': ['regime94.py'], 'r6': sorted(REPOINT), 'r7': r7_files()}


def check_ledger(fired_by_key, stage):
    live = {k: v for k, v in fired_by_key.items() if not k.endswith('_port.py')}
    for tag, want in expected_ledger().items():
        got = sorted(k for k, v in live.items() if tag in v)
        assert got == want, (stage, tag, got, want)
        if tag != 'r1':
            assert not any(tag in v for k, v in fired_by_key.items() if k.endswith('_port.py')), (stage, tag)
    return live


def gate_tokens(p):
    return rd(p).split()


def seal_record(name):
    """{basename: sha256} of a session's SEALSnnn.txt ('<sha> *[pred/]<name>' per line)."""
    rec = {}
    for line in rd(SRC / name).splitlines():
        if line.strip():
            h, n = line.split()
            n = n.lstrip('*')
            n = n[len('pred/'):] if n.startswith('pred/') else n
            assert '/' not in n and n not in rec, (name, line)
            rec[n] = h
    return rec


def preconditions():
    assert SRC.resolve() != DST.resolve()
    assert not DST.exists(), 'destination exists: do not rerun a completed port'
    assert not (SRC / 'prev105').exists()
    assert not (SRC / LEDGER_NAME).exists()
    assert (SRC / PREV_LEDGER).is_file()
    for f, opt in COMMA.items():
        t = rd(SRC / f)
        m = re.search(r"add_argument\('" + re.escape(opt) + r"', default='([^']*)'", t)
        assert m and m.group(1) == chain(105, 75, True), f
        assert len(m.group(1).split(',')) == 31, f
    for f, (floor, _) in ARITH.items():
        assert rd(SRC / f).count('range(105, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(SRC / f).count(chain(105, floor)) == 1, f
    assert {f: 105 - floor + 1 for f, floor in TUPLES.items()} == {'stg92.py': 16, 'bda93.py': 15, 's94lib.py': 14}
    assert rd(SRC / 'regime94.py').count(regime(105)) == 1 and 105 - 93 + 1 == 13
    assert rd(SRC / 'regime94.py').splitlines()[2] == 'import os, re, sys, statistics'
    assert tuple(f for f in DOCS if (SRC / f).is_file()) == DOCS_PRESENT, [f for f in DOCS if (SRC / f).is_file()]
    sealed = sealed_index()
    assert len(sealed) == len(SEALED) == 44
    # No two texts may land on one path and no text is renamed.  The only shared basenames are
    # the two inherited pairs of audit addenda: sessions 100/101 (03_) and sessions 103/104 (04_).
    assert len({(land, n) for _, n, _, _, land in SEALED}) == 44
    names_all = [n for _, n, _, _, _ in SEALED]
    assert sorted({n for n in names_all if names_all.count(n) > 1}) == ['03_audit_addendum.md', '04_audit_addendum.md']
    s105_names = {n for d, n, _, _, _ in SEALED if d == 'pred'}
    assert s105_names == set(S105_NAMES) and len(s105_names) == 4
    # Collision check over every carried seal folder (not only the listed texts): no session-105
    # basename is taken anywhere.
    carried_names = set()
    for folder in CARRIED:
        carried_names |= {p.name for p in (SRC / folder).iterdir()}
    assert not s105_names & carried_names, s105_names & carried_names
    assert all(land in (LAND, d) for d, _, _, _, land in SEALED)
    assert sum(1 for _, _, _, _, land in SEALED if land == LAND) == 42
    assert [(d, n) for d, n, _, _, land in SEALED if land != LAND] == [
        (CARRIED103, '04_audit_addendum.md'), (OLDER, '03_audit_addendum.md')]
    for folder in ('pred', INHERITED):
        assert sorted(p.name for p in (SRC / folder).iterdir()) == sorted(n for d, n, _, _, _ in SEALED if d == folder), folder
    inherited_names = [n for d, n, _, _, _ in SEALED if d == INHERITED]
    assert len(inherited_names) == 38
    assert set(S102_NAMES) | set(S103_NAMES) | set(S104_NAMES) <= set(inherited_names)
    # prev103/pred: thirty-three byte-identical twins of prev104/pred texts (sessions 96..103) plus
    # session 103's own 04_audit_addendum.md, which differs from session 104's.
    twins103 = sorted(n for n in inherited_names if n not in S104_NAMES)
    assert len(twins103) == 33
    assert sorted(p.name for p in (SRC / CARRIED103).iterdir()) == sorted(twins103 + ['04_audit_addendum.md'])
    assert sha(SRC / CARRIED103 / '04_audit_addendum.md') != sha(SRC / INHERITED / '04_audit_addendum.md')
    # prev102/pred: twenty-nine twins (sessions 96..102).
    twins102 = sorted(n for n in twins103 if n not in S103_NAMES)
    assert len(twins102) == 29 and sorted(p.name for p in (SRC / CARRIED102).iterdir()) == twins102
    # prev101/pred: twenty twins (sessions 96..101).
    twins101 = sorted(n for n in twins102 if n not in S102_NAMES)
    assert len(twins101) == 20 and sorted(p.name for p in (SRC / CARRIED101).iterdir()) == twins101
    # prev100/pred: session 100's addendum plus seventeen byte-identical twins.
    twins100 = sorted(n for n in twins101 if n not in PREV101_ONLY)
    older = sorted(p.name for p in (SRC / OLDER).iterdir())
    assert len(twins100) == 17 and older == sorted(twins100 + ['03_audit_addendum.md']), older
    for folder, twins in ((CARRIED103, twins103), (CARRIED102, twins102), (CARRIED101, twins101), (OLDER, twins100)):
        for n in twins:
            assert sha(SRC / folder / n) == sealed[(INHERITED, n)][1] == sha(SRC / INHERITED / n), ('twin', folder, n)
    for d, n, size, h, _ in SEALED:
        assert (SRC / d / n).stat().st_size == size and sha(SRC / d / n) == h, (d, n)
    # The sessions' own seal records: SEALS105.txt names exactly the four session-105 texts (in
    # pred/); SEALS104/103/102.txt still name theirs, now read from the carried folders.
    for record, names, where in SEAL_RECORDS:
        rec = seal_record(record)
        want = {n: sealed[(where.get(n, 'pred' if record == SEALS_FILE else INHERITED), n)][1] for n in names}
        assert rec == want, (record, rec)
    live_paths = 0
    for f, names in REPOINT.items():
        t = rd(SRC / f)
        folder = REPOINT_FOLDER.get(f, INHERITED)
        for name in names:
            p = Path(const(t, name))
            assert p.parent == SRC / folder, (f, name, p)
            key = (folder, p.name)
            assert const(t, name + '_SHA') == sealed[key][1] == sha(p), (f, name)
            assert sealed[key][2] == LAND, ('live constant names a text outside prev105/pred', f, name)
            live_paths += 1
        m = re.search(r'^PRED_BYTES\s*=\s*(\d+)', t, re.M)
        if m:
            assert int(m.group(1)) == sealed[(folder, Path(const(t, 'PRED')).name)][0], f
    assert len(REPOINT) == 20 and live_paths == 31, (len(REPOINT), live_paths)
    assert all(re.search(r'^PRED_BYTES\s*=', rd(SRC / f), re.M) for f in REPOINT_FOLDER)
    for f, text in IMPORTERS:
        assert text in rd(SRC / f), (f, text)
    for f, imp, override in SEAL_OVERRIDE_TESTS:
        t = rd(SRC / f)
        assert imp in t and override in t, f
    for f, name, before, _after, basename, folder, hash_const in REPOINT2:
        t = rd(SRC / f)
        anchor = before % OLD if '%s' in before else before
        assert t.count(anchor) == 1, ('r7 anchor', f, t.count(anchor))
        if hash_const is not None:
            assert const(t, hash_const) == sealed[(folder, basename)][1], f
        else:
            assert not re.search(r'^' + name + r'_SHA\s*=', t, re.M), f
        root_line = R7_ROOT_LINE[f]
        if root_line is not None:
            assert t.count(root_line % OLD) == 1, ('r7 root', f)
        rel = rel_of(anchor)
        assert rel == '%s/%s' % (folder, basename), (f, rel)
        assert sha(SRC / rel) == sealed[(folder, basename)][1], f
        assert sealed[(folder, basename)][2] == LAND, f
    assert len(REPOINT2) == 10 and len(r7_files()) == 8
    # No other top-level Python file names a session-105 seal as a module constant (a quoted
    # literal, a ROOT +/ROOT / expression or a Path(...) whose text names pred/<session-105 name>).
    seal_rx = (r"^(\w+)\s*=\s*((?:ROOT\s*[+/]\s*|Path\()?['\"][^'\"\n]*pred/(?:%s)['\"].*)$"
               % '|'.join(re.escape(n) for n in S105_NAMES))
    for p in sorted(SRC.glob('*.py')):
        for m in re.finditer(seal_rx, rd(p), re.M):
            assert (p.name in REPOINT and m.group(1) in REPOINT[p.name]) or \
                (p.name, m.group(1)) in {(f, c) for f, c, _, _, _, _, _ in REPOINT2} or \
                p.name in ONE_SHOT or p.name.endswith('_port.py'), (p.name, m.group(0))
    for f in ARCHIVE_SCORERS | set(ONE_SHOT):
        assert (SRC / f).is_file(), f
    for f, text_, basename in FROZEN_DANGLING_BARE:
        assert rd(SRC / f).count(text_ % OLD) == 1 and basename in S105_NAMES, f
    # Gates baseline: 1092 B / 99 names, dawalk=1 (shipped by session 104); ctxtick absent.
    g = SRC / 'gates_base.txt'
    assert g.stat().st_size == 1092 and sha(g) == GATES_SHA
    names = [x.split('=')[0] for x in rd(g).split() if '=' in x]
    assert len(names) == len(set(names)) == 99
    assert 'dawalk=1' in gate_tokens(g) and 'ctxtick' not in names
    for f, size, h in ARCHIVE_DATA:
        assert (SRC / f).stat().st_size == size and sha(SRC / f) == h, f
    pre = gate_tokens(SRC / 'gates_base.pre104ship.txt')
    assert [x if x != 'dawalk=0' else 'dawalk=1' for x in pre] == gate_tokens(g), 'pre-ship differs beyond dawalk'
    for f, extra in CTX_FILES:
        assert gate_tokens(SRC / f) == gate_tokens(g) + [extra], f
    gj = SRC / 'gates_base.json'
    assert (gj.stat().st_size, sha(gj)) == GATES_JSON
    new_j = json.loads(rd(gj))
    old_j = json.loads(rd(SRC / 'gates_base.pre104ship.json'))
    assert new_j['gates']['dawalk'] == 1 and old_j['gates']['dawalk'] == 0
    assert {k: v for k, v in new_j.items() if k not in ('gates', 'text')} == \
        {k: v for k, v in old_j.items() if k not in ('gates', 'text')}
    assert dict(new_j['gates'], dawalk=0) == old_j['gates']
    for j, t in ((new_j, g), (old_j, SRC / 'gates_base.pre104ship.txt')):
        # inherited (s103's json too): the json text says dapin=1 where the pinned .txt says dapin=3
        assert [x if x != 'dapin=1' else 'dapin=3' for x in j['text'].split()] == gate_tokens(t)
    for f in GATES_PINNED:
        t = rd(SRC / f)
        assert const(t, 'GATES_SHA') == PRESHIP_SHA and const(t, 'GATES_FILE') == OLD + '/gates_base.txt', f
    for f in GATES_CURRENT:
        t = rd(SRC / f)
        assert const(t, 'GATES_SHA') == GATES_SHA and const(t, 'GATES_FILE') == OLD + '/gates_base.txt', f
    for f in BINARY_PINNED:
        assert re.fullmatch(r'[0-9a-f]{64}', const(rd(SRC / f), 'BINARY_SHA')), f
    text = rd(GATES)
    entry = r'\{\s*"KYTY_\w+",\s*"([a-z0-9]+)"'
    cpp = re.findall(entry, text)
    assert len(cpp) == len(set(cpp)) == GATES_CPP_ENTRIES, len(cpp)
    cut = text.index('KNOB_DEFINITIONS')
    split = (len(re.findall(entry, text[:cut])), len(re.findall(entry, text[cut:])))
    assert split == GATES_CPP_SPLIT, split
    assert re.findall(entry, text[:cut])[-1] == 'cbmove' and re.findall(entry, text[cut:])[-1] == 'ctxtick'
    assert text.count('{"KYTY_CTX_TICK", "ctxtick", 1, 3}') == 1
    assert len(ABSENT) == len(set(ABSENT)) == 37 == GATES_CPP_ENTRIES - 99
    assert set(ABSENT) == set(cpp) - set(names)
    assert not set(ABSENT) & set(names)
    assert all(not (SRC / f).exists() for f in NEW_SESSION)
    assert not any(d.is_dir() and d.name.startswith('design106') for d in SRC.iterdir())
    for tag, n in ROOT_TESTS:
        assert (Path('C:/kyty/s%d' % n) / ('log_%s.txt' % tag)).is_file(), tag
    for f, text_ in TEST_LOG_MOVED:
        assert rd(SRC / f).count(text_ % OLD) == 1, f
    for f in ONE_SHOT_MOVED:
        assert "'%s/FACTS.md'" % OLD in rd(SRC / f), f
    print('PRECONDITIONS PASS: 5 root constructs; 44 sealed texts (42 land in prev105/pred, 2 stay '
          'in carried prev103/pred and prev100/pred); 31 live paths (20 files) + 10 expression paths '
          '(8 files); gates 1092 B / 99 names (sha 303a7849..., dawalk=1, no ctxtick); gates.cpp 136 '
          'entries (111 gates + 25 knobs); ABSENT 37')


def main():
    preconditions()
    carried, ledger, skipped = [], {}, []
    planned = []
    # Preflight ALL decoding and repair anchors before writing the destination.
    for root, dirs, files in os.walk(SRC):
        rel = Path(root).relative_to(SRC)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIR and not (rel == Path('.') and (d == 'pred' or d.startswith('design106'))))
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
    # Stale s105 root literals may remain only in the seven chain files (one line each).
    stale = sorted(key for key, output, _, _ in planned if output is not None and '/' not in key
                   and not key.endswith('_port.py') and OLD in output)
    assert stale == sorted(list(COMMA) + list(TUPLES) + ['regime94.py']), stale
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
    prev = DST / 'prev105'
    (prev / 'pred').mkdir(parents=True)
    (DST / 'pred').mkdir()
    for f in DOCS:
        if (SRC / f).is_file():
            shutil.copy2(SRC / f, prev / f)
    for d, n, _, _, land in SEALED:
        if land == LAND:
            assert not (DST / LAND / n).exists(), ('landing collision', d, n)
            shutil.copy2(SRC / d / n, DST / LAND / n)
    diagnostics(carried, ledger, skipped)
    (DST / LEDGER_NAME).write_text(json.dumps({'source': OLD, 'destination': NEW, 'files': ledger,
        'carried_count': len(carried), 'skipped_count': len(skipped), 'archive_scorers': sorted(ARCHIVE_SCORERS),
        'sealed_landing': ['%s/%s -> %s/%s' % (d, n, land, n) for d, n, _, _, land in SEALED]}, indent=2) + '\n', encoding='utf-8')
    print('PORT DIAGNOSTIC: clean; carried=%d ledger=%d skipped=%d' % (len(carried), len(ledger), len(skipped)))


def diagnostics(carried, ledger, skipped):
    live = check_ledger({k: v['repairs'] for k, v in ledger.items()}, 'written')
    for tag, want in expected_ledger().items():
        print('LEDGER %s PASS: %s' % (tag, ', '.join(want)))
    ports = sorted(k for k in ledger if k.endswith('_port.py'))
    print('LEDGER r1 ARCHIVE PORTS (carried, never run): %d files: %s' % (len(ports), ', '.join(ports)))
    live = {k: ledger[k] for k in live}
    naive_regime = naive(rd(SRC / 'regime94.py'))
    blind = naive_regime.replace("'C:/kyty/s106', 'C:/kyty/s104'", "'C:/kyty/s106', 'C:/kyty/s105', 'C:/kyty/s104'")
    assert blind == naive_regime.replace(naive(regime(105)), regime(106))
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
        assert m and m.group(1) == chain(106, 75, True) and len(m.group(1).split(',')) == 32, f
    for f, (floor, _) in ARITH.items():
        assert rd(DST / f).count('range(106, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(DST / f).count(chain(106, floor)) == 1, f
    print('ADVANCE PASS: COMMA 32 roots; range(106, 70/66, -1); stg92 17, bda93 16, s94lib 15 roots; '
          'regime94 14 roots + s106')
    sealed = sealed_index()
    for f, names in REPOINT.items():
        t = rd(DST / f)
        for name in names:
            p = Path(const(t, name))
            assert p.parent == DST / LAND, (f, name, p)
            assert sha(p) == const(t, name + '_SHA') == const(rd(SRC / f), name + '_SHA')
    print('R6 PASS: %d constants in %d files -> %s (incl. lead105.PRED -> 01_dawalklead.md, ctx105.PRED -> 02_m31.md)'
          % (sum(len(v) for v in REPOINT.values()), len(REPOINT), LAND))
    for f, name, _before, after, basename, folder, hash_const in REPOINT2:
        t = rd(DST / f)
        anchor = after % NEW if '%s' in after else after
        assert t.count(anchor) == 1, ('r7 result', f, name)
        root_line = R7_ROOT_LINE[f]
        if root_line is not None:
            assert t.count(root_line % NEW) == 1, ('r7 root', f)
        rel = rel_of(anchor)
        assert rel == '%s/%s' % (LAND, basename), (f, rel)
        p = DST / rel
        assert p.is_file() and sha(p) == sealed[(folder, basename)][1], f
        if hash_const is not None:
            assert sha(p) == const(t, hash_const), f
        print('R7 PASS: %s %s -> %s%s' % (f, name, p.as_posix(),
                                          '' if hash_const else ' (no hash constant; recorded at run time)'))
    for f, text in IMPORTERS:
        assert text in rd(DST / f), (f, text)
    print('IMPORTED SEAL PASS: %d reads in %d files follow m5_102 / m5p_103 / bvh103 into %s'
          % (len(IMPORTERS), len({f for f, _ in IMPORTERS}), LAND))
    for f, imp, override in SEAL_OVERRIDE_TESTS:
        t = rd(DST / f)
        assert imp in t and override in t, f
        print('TEST SEAL OVERRIDE, REPORT ONLY: %s imports its scorer and replaces PRED with a temporary seal' % f)
    assert len(list((DST / LAND).iterdir())) == 42
    for d, n, size, h, land in SEALED:
        p = DST / land / n
        assert p.stat().st_size == size and sha(p) == h == sha(SRC / d / n), (d, n)
        print('SEALED PASS: %s/%s %d B %s' % (land, n, size, h))
    for folder, want in ((INHERITED, 38), (CARRIED103, 34), (CARRIED102, 29), (CARRIED101, 20), (OLDER, 18)):
        got = sorted(p.name for p in (DST / folder).iterdir())
        assert got == sorted(p.name for p in (SRC / folder).iterdir()) and len(got) == want, folder
        for n in got:
            assert sha(DST / folder / n) == sha(SRC / folder / n), (folder, n)
            seal = sealed.get((folder, n), sealed.get((INHERITED, n)))
            assert seal is not None and sha(DST / folder / n) == seal[1], (folder, n)
        print('CARRIED SEALED PASS: %s holds %d texts byte-exact (walk carry)' % (folder, len(got)))
    a100 = sha(DST / OLDER / '03_audit_addendum.md')
    a101 = sha(DST / LAND / '03_audit_addendum.md')
    assert a100 == sealed[(OLDER, '03_audit_addendum.md')][1] and a101 == sealed[(INHERITED, '03_audit_addendum.md')][1]
    assert a100 != a101
    a103 = sha(DST / CARRIED103 / '04_audit_addendum.md')
    a104 = sha(DST / LAND / '04_audit_addendum.md')
    assert a103 == sealed[(CARRIED103, '04_audit_addendum.md')][1] and a104 == sealed[(INHERITED, '04_audit_addendum.md')][1]
    assert a103 != a104
    print('COLLISION PASS: %s/03_audit_addendum.md = session 100 (%s...), %s/03_audit_addendum.md = session 101 (%s...)'
          % (OLDER, a100[:8], LAND, a101[:8]))
    print('COLLISION PASS: %s/04_audit_addendum.md = session 103 (%s...), %s/04_audit_addendum.md = session 104 (%s...)'
          % (CARRIED103, a103[:8], LAND, a104[:8]))
    for n in S105_NAMES:
        assert all(not (DST / folder / n).exists() for folder in CARRIED) and (DST / LAND / n).is_file(), n
    print('NO COLLISION PASS: the four session-105 basenames exist only in %s' % LAND)
    assert not list((DST / 'pred').iterdir())
    assert all(not (DST / f).exists() for f in DOCS + NEW_SESSION)
    for f in DOCS:
        if (SRC / f).is_file():
            assert sha(SRC / f) == sha(DST / 'prev105' / f)
        else:
            assert not (DST / 'prev105' / f).exists()
    assert sorted(p.name for p in (DST / 'prev105').iterdir()) == sorted(list(DOCS_PRESENT) + ['pred'])
    print('PREV105 PASS: %s + pred/ (42 texts); no README.md or PLAN.md in the source root' % ', '.join(DOCS_PRESENT))
    assert (DST / 'm31_notes.md').is_file() and sha(DST / 'm31_notes.md') == sha(SRC / 'm31_notes.md')
    print('SESSION-105 WORKING NOTE CARRIED AT ROOT, REPORT ONLY: m31_notes.md (only README/FACTS/PLAN are prev-only)')
    assert sha(DST / PREV_LEDGER) == sha(SRC / PREV_LEDGER)
    print('PREVIOUS LEDGER CARRIED AS DATA: %s byte-exact' % PREV_LEDGER)
    for f in sorted(ARCHIVE_SCORERS):
        assert (DST / f).is_file(), ('archive scorer missing', f)
        # r6/r7 only repoint a sealed path; they never make an archive scorer runnable.
        assert f not in live or set(live[f]['repairs']) <= {'r6', 'r7'}, ('archive scorer entered live repair', f)
        print('ARCHIVE, DO NOT RUN: %s; carried by naive rewrite (plus r6/r7 where listed)' % f)
    for f, size, h in ARCHIVE_DATA:
        assert (DST / f).stat().st_size == size and sha(DST / f) == h, f
        print('ARCHIVE DATA, NOT A BASELINE: %s %d B %s... byte-exact' % (f, size, h[:8]))
    for f, name, miss in ROOT_MOVED:
        assert const(rd(DST / f), name) == NEW and const(rd(SRC / f), name) == OLD, f
        print('ARCHIVE ROOT MOVED BY NAIVE REWRITE, REPORT ONLY: %s %s = %s (%s)' % (f, name, NEW, miss))
    for f in GATES_PINNED:
        t = rd(DST / f)
        assert const(t, 'GATES_SHA') == PRESHIP_SHA and const(t, 'GATES_FILE') == NEW + '/gates_base.txt', f
        print('ARCHIVE GATES PIN, REPORT ONLY: %s GATES_SHA = %s... (the pre-ship baseline, carried as '
              'gates_base.pre104ship.txt); GATES_FILE = %s/gates_base.txt holds %s... (dawalk=1)'
              % (f, PRESHIP_SHA[:8], NEW, GATES_SHA[:8]))
    for f in GATES_CURRENT:
        t = rd(DST / f)
        assert const(t, 'GATES_SHA') == GATES_SHA == sha(DST / 'gates_base.txt')
        assert const(t, 'GATES_FILE') == NEW + '/gates_base.txt', f
        print('ARCHIVE GATES PIN HOLDS: %s GATES_SHA = %s... = %s/gates_base.txt' % (f, GATES_SHA[:8], NEW))
    for f in BINARY_PINNED:
        b = const(rd(DST / f), 'BINARY_SHA')
        assert b == const(rd(SRC / f), 'BINARY_SHA'), f
        print('ARCHIVE BINARY PIN, REPORT ONLY: %s BINARY_SHA = %s... (its own run\'s build; never re-run)' % (f, b[:8]))
    for f, text_ in TEST_LOG_MOVED:
        assert rd(DST / f).count(text_ % NEW) == 1 and not (DST / 'log_reg104.txt').exists(), f
        print('TEST REAL-LOG PATH MOVED BY NAIVE REWRITE, REPORT ONLY: %s reads %s/log_reg104.txt (log stays in s104)'
              % (f, NEW))
    assert not list(DST.glob('log_*10[45]*.txt'))
    assert (SRC / 'log_abb105.txt').is_file() and Path('C:/kyty/s104/log_reg104.txt').is_file()
    for f in ONE_SHOT:
        assert (DST / f).is_file() and f not in ledger, f
        moved = ' (target %s/FACTS.md after naive rewrite; anchors assert before any write)' % NEW \
            if f in ONE_SHOT_MOVED else ''
        if f in ONE_SHOT_MOVED:
            assert "'%s/FACTS.md'" % NEW in rd(DST / f), f
        print('ONE-SHOT, DO NOT RUN: %s%s' % (f, moved))
    # make_ctx105.py after the naive rewrite: it would read s106/lead105.py and write s106/ctx105.py,
    # but its PRED names s106/pred/02_m31.md, which does not exist, and it opens PRED before it
    # writes anything; its re.sub anchor names the pre-r6 lead105 PRED line, gone from s106/lead105.py.
    t = rd(DST / 'make_ctx105.py')
    assert "PRED = '%s/pred/02_m31.md'" % NEW in t and "DST = '%s/ctx105.py'" % NEW in t
    assert t.index("data = open(PRED, 'rb')") < t.index("open(DST, 'w'")
    assert not (DST / 'pred' / '02_m31.md').exists()
    assert "PRED = '%s/pred/01_dawalklead.md'" % NEW not in rd(DST / 'lead105.py')
    print('ONE-SHOT GENERATOR, PRED LEFT DANGLING, REPORT ONLY: make_ctx105.py reads %s/pred/02_m31.md '
          '(absent) before it would write %s/ctx105.py; its lead105 anchor no longer matches after r6' % (NEW, NEW))
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
    for f, line, basename in FROZEN_DANGLING_BARE:
        t = rd(DST / f)
        assert t.count(line % NEW) == 1 and f not in ledger, f
        assert not (DST / 'pred' / basename).exists() and (DST / LAND / basename).is_file(), f
        print('FROZEN EVIDENCE, PRED LEFT DANGLING BY DESIGN: %s (bare literal pred/%s)' % (f, basename))
    for f, line in HERE_DANGLING:
        assert rd(DST / f).count(line) == 1, f
        target = DST / 'pred' / line.rsplit('/', 1)[1].rstrip("'")
        assert not target.exists(), f
        print('HERE-RELATIVE TEST SEAL, DANGLING, REPORT ONLY: %s reads %s' % (f, target.relative_to(DST).as_posix()))
    for f, line, basenames in ROOT_DANGLING:
        t = rd(DST / f)
        assert t.count(line) == 1 and f not in ledger, f
        if 'ROOT' in line:
            assert ("ROOT = Path('%s')" % NEW in t) or ("ROOT = '%s'" % NEW in t), f
        for b in basenames:
            assert not (DST / 'pred' / b).exists() and (DST / LAND / b).is_file(), (f, b)
        print('SEAL READ IN FUNCTION, DANGLING, REPORT ONLY: %s reads %s' %
              (f, ', '.join('pred/' + b for b in basenames)))
    for f in OLDER_SCORERS:
        for line in rd(DST / f).splitlines():
            if re.match(r'^PRED\w*\s*=', line) and '_SHA' not in line.split('=')[0]:
                print('OLDER PRED, REPORT ONLY: %s %s' % (f, line))
    roots = ast.literal_eval(re.search(r'^ROOTS = (.+)$', rd(DST / 's94lib.py'), re.M).group(1))
    assert roots == tuple('C:/kyty/s%d' % i for i in range(106, 91, -1))
    for tag, n in ROOT_TESTS:
        found = next((r for r in roots if (Path(r) / ('log_%s.txt' % tag)).is_file()), None)
        assert found == 'C:/kyty/s%d' % n, (tag, found)
        print('ROOT PASS: %s -> %s' % (tag, found))
    assert rd(DST / 'regime94.py').count(regime(106)) == 1
    for tag, n in ROOT_TESTS:
        if n < 93:
            continue
        found = next((r for r in roots[:-1] if (Path(r) / ('log_%s.txt' % tag)).is_file()), NEW)
        assert found == 'C:/kyty/s%d' % n
    assert next((r for r in roots[:-1] if (Path(r) / 'log_nosuch106.txt').is_file()), NEW) == NEW
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
    big_in_dirs = sorted(k for k in skipped if '/' in k and (SRC / k).stat().st_size >= BIG)
    print('SKIPPED >= 5 MiB INSIDE CARRIED FOLDERS, REPORT ONLY: %d files: %s' % (len(big_in_dirs), ', '.join(big_in_dirs)))
    g = DST / 'gates_base.txt'
    assert sha(g) == GATES_SHA and g.stat().st_size == 1092
    assert (sha(DST / 'gates_base.json'), (DST / 'gates_base.json').stat().st_size) == (GATES_JSON[1], GATES_JSON[0])
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    result = subprocess.run([sys.executable, '-B', str(DST / 'gen_gates.py'), '--check'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    print('gen_gates.py --check exit=%d (expected out-of-date for deliberately pinned baseline)' % result.returncode)
    print(result.stdout.decode('utf-8', 'replace').strip())
    assert result.returncode in (0, 1), result.returncode
    assert sha(g) == GATES_SHA and sha(SRC / 'gates_base.txt') == GATES_SHA
    assert sha(DST / 'gates_base.json') == GATES_JSON[1] == sha(SRC / 'gates_base.json')
    print('GATES PASS: check-only, unchanged SHA (txt 303a7849..., json 2b79c3cf...); no scorer/game/build invoked')


if __name__ == '__main__':
    main()
