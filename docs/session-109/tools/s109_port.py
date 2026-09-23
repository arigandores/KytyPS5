"""Fresh source-side s108 -> s109 harness port; never run a carried *_port.py.

Written in the SOURCE folder (C:/kyty/s108) as docs/next-session-109.md 1 requires, modelled on
C:/kyty/s107/s108_port.py (sha256 cb104f40...).  Only Python root literals change globally.  Five root
constructs, the live sealed-path repair of bare quoted literals (r6: now 25 files / 36 constants) and the
repair of sealed paths written as ROOT/Path expressions (r7: still 10 expression paths in 8 files) are
recorded separately in the ledger.  No scorer, game, build or GPU work is run.  The destination must not
exist.  New session documents/scorers belong to their authors; inherited session documents are archived
under prev108 only.

    python C:/kyty/s108/s109_port.py [--plan-only]

--plan-only runs every precondition and the whole in-memory plan (including the preflight ledger and the
dangling-path census) and writes nothing.

Advances over s108_port.py, each asserted in preconditions():
  * COMMA chain 34 -> 35 roots (s109 ... s75); r1 splices s108 back in.
  * area_verdict.py range(109, 70, -1); shift91.py range(109, 66, -1).
  * s94lib.py 18 roots, bda93.py 19, stg92.py 20; regime94.py 17 roots + s109.
  * SEALED grows 50 -> 52 (the two session-108 seals pred/01_cspfam.md and pred/02_audit108.md, each checked
    against SEALS108.txt).  50 land in prev108/pred; two stay where the walk carries them (the two older audit
    addenda, as before).  No session-108 basename is taken anywhere in the source outside its pred/ (all 28
    earlier pred/ folders and every other directory, re-verified below).
  * SEALS108.txt is the first seal record that also pins TOOLS (gates_fam4.txt, fam108.py, make_fam108.py,
    test_fam108.py, go108.sh, without the pred/ prefix): texts and tools are separated; the tools are checked
    against the source files and reported after the port (the three .py copies are rewritten, the .txt/.sh
    copies are byte-exact).
  * r6 grows 24 -> 25 files and 35 -> 36 constants: fam108.PRED (fam108.py:31) is a BARE quoted literal
    'C:/kyty/s108/pred/01_cspfam.md' with PRED_SHA and PRED_BYTES, checked against SEALS108.txt.  The
    twenty-four inherited r6 files now read from s108/prev107/pred (obs107/dab107 included).
  * r7 unchanged in count: 10 expression paths in 8 files, all now reading s108/prev107/pred.  No session-108
    file writes a seal as an expression.
  * gates_base.txt unchanged: 1092 B / 99 names, sha256 303a7849... (dawalk=1); gates_base.json unchanged
    (3343 B, 2b79c3cf...).  None of dabatch, ctxtick, cspmemo, cspfam is in gates_base.txt.  Session 108's
    gates_fam4.txt (gates_base.txt + cspfam=4: the vfm108 video gate text) and gates_fam0.txt (gates_base.txt +
    cspfam=0: the sf108a/sf108c gate text) are archive data.
  * gates.cpp stays at 138 entries (111 gates + 27 knobs): session 109's cspfam v2 (bc7d66f) changed the meaning
    of the existing LAST knob row (default 0, 0..1024) and added no row.  ABSENT stays 39.
  * Session-108 tools fam108.py (pinned to its seal, binary fd1d0bd7... and the gates baseline), test_fam108.py
    (fixtures; loads the scorer on argv), check108.py / check108r.py (pinned to builds fc78c564... / 379777bb...,
    read C:/kyty/s108 logs) are archive; make_fam108.py (generator anchored on C:/kyty/s107/dab107.py),
    roadmap108_close.py (ROADMAP patch), facts108_fix.py (FACTS patch), ctx108.py and handoff108.py (game-folder
    context patches) are one-shots; go108.sh, go108v.sh, go108s.sh, go108p.sh, go108r.sh are carried shells.
    None is ever re-run.  seal108.py is NOT in the source (it lives in C:/kyty/s106_stage and
    docs/session-108/tools): asserted absent, nothing to class.
  * NEW_SESSION names the session-109 files the executor places later; none may exist in SRC or arrive in DST.
    gates_fam4.txt is also a session-109 name, already carried as archive data.

Changes of SHAPE, forced by the sources:
  * The inherited seals now live in EIGHT carried folders.  prev107/pred holds 48 texts (every text an
    inherited live constant names); prev106/pred holds 45, all byte-identical twins of prev107/pred texts;
    prev105/pred 42 twins; prev104/pred 38; prev103/pred 34, thirty-three twins plus session 103's
    04_audit_addendum.md; prev102/pred 29; prev101/pred 20; prev100/pred 18, seventeen twins plus session 100's
    03_audit_addendum.md.  Twins are verified byte-identical instead of being listed twice.
  * Not carried (they stay in C:/kyty/s108): the scored binaries kyty_emulator_*.exe (.exe, as before), the
    audit's parse dumps audit108/p_*.json (five files; two are under 5 MiB, so an explicit rule), and session-109
    build logs build_s109*.log that the concurrent session-109 executor writes into the SOURCE root.
  * Session-108 files the naive s108 -> s109 rewrite breaks are classed explicitly: the 22 audit mutants
    audit108/mutants/fam108_*.py (frozen evidence; bare pred literal left dangling, roots moved), the 19 worker
    copies audit108/mutants/test_fam108_w*.py (BASE moved to s109/audit108/fx_wN), the audit readers of the
    non-carried parse dumps (guards108.py, profile108.py, recount108.py), the audit mutant runners
    (mutants108.py, mutants108p.py: they read the s109 copies of fam108.py/test_fam108.py), make_fam108.py,
    roadmap108_close.py, facts108_fix.py, ctx108.py, handoff108.py, check108.py, check108r.py, fam108.py.
  * roadmap108_close.py passes names and concatenations to rep(): the ROADMAP simulation now evaluates
    module-level string assignments and '+' of strings (still in memory only, never the file).
  * The ledger is written as bytes with LF line ends (the 108 ledger went through write_text and carries CRLF).
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
SRC = Path('C:/kyty/s108')
DST = Path('C:/kyty/s109')
OLD, NEW = SRC.as_posix(), DST.as_posix()
PREV_ROOT = Path('C:/kyty/s107')  # the root the session-107 run outputs' scorer hashes were taken in
PREV106_ROOT = Path('C:/kyty/s106')  # the root session 106's audit read its scorers from
EXT_DAB107 = Path('C:/kyty/s107/dab107.py')  # the file make_fam108.py was run on (outside the harness)
GATES = Path('C:/kyty/KytyPS5/src/common/gates.cpp')
ROADMAP = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'  # dawalk=1 (shipped s104)
GATES_JSON = (3343, '2b79c3cf9240ab9f43e2430f3dacd290c48ca71f32bab78730515f2864efd8d0')
PRESHIP_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'  # dawalk=0
CTX1_SHA = 'b7c89fae21292ecb414e7fdd5dffe3ad7d78020eba200b0e9f665c17c5dbfb61'  # gates_base + ctxtick=1
CTX2_SHA = '207ae3016740f7ff1ebffe83623dd20c6759795ec8f1c217229da4a3b96562c2'  # gates_base + ctxtick=2
DAB8_SHA = 'dcf0e870b6040680c7acb79da4859e12120a593ccfce4ae8542e24ec7df0c1cc'  # gates_base + dabatch=8
OBS_SHA = 'ea91bcee4937bc716918201e01e31a45dfcecae84626e6c2322a2cad60a2c35a'   # gates_base + plkstat=1 cspmemo=3
DAB2_SHA = 'c462d2270e89024eabbf4b910d210ad74c6c04cbf9cf2a5cfdbb0f3e0243d4a2'  # gates_base + dabatch=2
FAM4_SHA = '59e018303a73f1641ba012838cd2fd0c54d524139820422d44314113c5619a6b'  # gates_base + cspfam=4
FAM0_SHA = '014667197963944c69ba68ba4ff95da35366c348425f54c382ee024f9219879e'  # gates_base + cspfam=0
# Archive data (sessions 104..108): carried byte-exact, never a baseline.
ARCHIVE_DATA = (('gates_base.pre104ship.txt', 1092, PRESHIP_SHA),
                ('gates_base.pre104ship.json', 3581, '6d256a31d8e817103bf3db2b2af19c89597ebddf9dc7a94678809caa122f2a5b'),
                ('gates_dawalk1.txt', 1493, 'cdc6568e7a347a7e834c11372e5f30eae2ae91f6f52bbec57d6e0aa51cfa0e7e'),
                ('gates_nodawalk.txt', 1082, '0931a79a8f1f6de21a81a8876d68d68d713f87bd5ddf20319f520228577c4f3b'),
                # Session 105: the P1/P4 and video gate files of pred/02_m31.md.
                ('gates_ctx1.txt', 1102, CTX1_SHA),
                ('gates_ctx2.txt', 1102, CTX2_SHA),
                # Session 106: the vdb106 video gate file of pred/02_dabatch.md.
                ('gates_dab8.txt', 1102, DAB8_SHA),
                # Session 107: the obs107 gate file and the (unused) vdb107 video gate file.
                ('gates_obs.txt', 1112, OBS_SHA),
                ('gates_dab2.txt', 1102, DAB2_SHA),
                # Session 108 (next-session-109.md 1): the vfm108 video gate file of pred/01_cspfam.md (sealed in
                # SEALS108.txt) and the sf108a/sf108c gate file (cspfam=0 while the default was 4).
                ('gates_fam4.txt', 1101, FAM4_SHA),
                ('gates_fam0.txt', 1101, FAM0_SHA))
# Archive gate files that are gates_base.txt plus appended tokens, one line, the single trailing CRLF kept.
PLUS_FILES = (('gates_ctx1.txt', ('ctxtick=1',)), ('gates_ctx2.txt', ('ctxtick=2',)),
              ('gates_dab8.txt', ('dabatch=8',)), ('gates_obs.txt', ('plkstat=1', 'cspmemo=3')),
              ('gates_dab2.txt', ('dabatch=2',)), ('gates_fam4.txt', ('cspfam=4',)),
              ('gates_fam0.txt', ('cspfam=0',)))
GATES_CPP_ENTRIES = 138  # 99 pinned in gates_base.txt + 39 ABSENT
GATES_CPP_SPLIT = (111, 27)  # DEFINITIONS rows, KNOB_DEFINITIONS rows
DABATCH_ROW = '{"KYTY_DRAW_AHEAD_BATCH", "dabatch", 8, 65536}'  # session 106 shipped default 8 (was 64)
CTXTICK_ROW = '{"KYTY_CTX_TICK", "ctxtick", 1, 3}'
CSPMEMO_ROW = '{"KYTY_CS_PREFETCH_MEMO", "cspmemo", 0, 3}'
# Session 108 (f9e19f7), default 4 between eed387b and 01f0c79, 0 again since; session 109's v2 (bc7d66f) kept
# the row: the LAST row of KNOB_DEFINITIONS, default 0, 0..1024.
CSPFAM_ROW = '{"KYTY_CS_PREFETCH_FAMILY", "cspfam", 0, 1024}'
BIG = 5 * 1024 * 1024
SKIP_PREFIX = ('log_', 'stdout_', 'rec_', 'a80z_', 'hfx_')
SKIP_EXT = ('.mp4', '.idx', '.pyc', '.map', '.etl', '.exe')
SKIP_DIR = {'__pycache__', 'video99_comparison', 'video99_preview', 'video99_full',
            'video99_base_full'}
# Session 108's audit parse dumps (next-session-109.md 1: 9.5 MB each, left in s108).  Two are under 5 MiB, so
# the size rule alone would carry them.
AUDIT_DUMP_RX = re.compile(r'^audit108/p_[a-z0-9]+\.json$')
AUDIT_DUMPS = ('audit108/p_fam108.json', 'audit108/p_sf108a.json', 'audit108/p_sf108b.json',
               'audit108/p_vfm108.json', 'audit108/p_vid108.json')
# Session-109 build logs the concurrent session-109 executor writes into the SOURCE root: never carried (a
# session-109 artifact, possibly still growing); they stay in s108.
CONCURRENT_RX = re.compile(r'^build_s109[a-z0-9]*\.log$')
# Scored binaries of session 108 (kept in s108, skipped as .exe): name -> the sha256 its pins name.
BINARIES108 = {'kyty_emulator_fd1d0bd7.exe': 'fd1d0bd7f68280e97680bc68dfe56fdf57a134429a49bc9223ece6254b7b1e72',
               'kyty_emulator_fc78c564.exe': 'fc78c56417815a0ebdea1c5a5aa94306720c3307d07a6feadf3c8e37f43aae43',
               'kyty_emulator_379777bb.exe': '379777bba4271847b1b805c403944e4a6552acd0aac0b5cd3af12be36c489107'}
DOCS = ('README.md', 'FACTS.md', 'PLAN.md')
DOCS_PRESENT = ('FACTS.md',)  # session 108 wrote no README.md and no PLAN.md at its root
# Names a session-109 author may create (docs/next-session-109.md 1); none may exist in SRC or arrive in DST.
NEW_SESSION = ('fam109.py', 'make_fam109.py', 'test_fam109.py', 'ent109.py', 'make_ent109.py', 'test_ent109.py',
               'obs109.py', 'make_obs109.py', 'test_obs109.py', 'SEALS109.txt', 'go109.sh', 'go109b.sh',
               'go109c.sh', 'check109.py')
# ... and one session-109 name that already exists as carried session-108 archive data.
NEW_SESSION_CARRIED = ('gates_fam4.txt',)
LEDGER_NAME = 'port109_ledger.json'
PREV_LEDGER = 'port108_ledger.json'  # the previous port's ledger: carried as plain data (it has CRLF line ends)
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
          # Session 102, knob KYTY_DRAW_AHEAD_BATCH: the 36th (compiled default 8 since session 106).
          'dabatch',
          # Session 105, knob KYTY_CTX_TICK (default 1, 0..3), the 37th (the third-to-last knob row).
          'ctxtick',
          # Session 107, knob KYTY_CS_PREFETCH_MEMO (default 0, 0..3), the 38th (the second-to-last).
          'cspmemo',
          # Session 108, knob KYTY_CS_PREFETCH_FAMILY (default 0, 0..1024), LAST row of KNOB_DEFINITIONS: the
          # 39th.  Session 109's v2 changed its meaning, not its row.
          'cspfam')
LAND = 'prev108/pred'
INHERITED = 'prev107/pred'
CARRIED106 = 'prev106/pred'
CARRIED105 = 'prev105/pred'
CARRIED104 = 'prev104/pred'
CARRIED103 = 'prev103/pred'
CARRIED102 = 'prev102/pred'
CARRIED101 = 'prev101/pred'
OLDER = 'prev100/pred'
CARRIED = (INHERITED, CARRIED106, CARRIED105, CARRIED104, CARRIED103, CARRIED102, CARRIED101, OLDER)
# (source folder in SRC, name, bytes, sha256, landing folder in DST)
SEALED = (
    # Sessions 96..101 (twenty texts; prev106..prev101/pred hold byte-identical twins).
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
    # Session 102 (nine texts, as in SEALS102.txt); prev107..prev102/pred.
    (INHERITED, '01_m5_bench.md', 14288, 'cf3c353f7aaa4a2a16d7b59a61461cf26bef11ddbfffd59206ae95a8b6b33e0a', LAND),
    (INHERITED, '02_m5_addendum.md', 8007, 'ced6d4103c64b9e5b7c81a3a730cac6d2b04a08486f82cf43642b04a8701f4d3', LAND),
    (INHERITED, '03_dabatch.md', 6909, 'f828e2578a1e68e2dbf99e976be7ce49f4041e6631d96c4773f0d23642b6135e', LAND),
    (INHERITED, '04_checkpoints_fix.md', 4221, 'c131852e4b3a5c979ce93d2c4182849b641bcc53ce1f217373926de369e8fe87', LAND),
    (INHERITED, '05_dabatch_addendum.md', 2347, 'b889c57a6f8c0f56eaa3ac43f68e9ea168dfef32b4a7122cb0b918fee5e7686d', LAND),
    (INHERITED, '06_ckpt_entry_addendum.md', 1595, '7562c26f1b7d6432eef3bf5ff4c4d3a4d1901d4a351ff0c74961e735cb6434ab', LAND),
    (INHERITED, '07_m5_capture_retry.md', 1870, '55aabe82e9c347a6d5e92bb7b7f7f327d632e5b045877e9237794850ca63c3b8', LAND),
    (INHERITED, '08_audit_addendum.md', 6464, 'ee7e3397609f31ec96a307aed53f0daa9362909b1bcb7ec4f2e383cdc2d8385f', LAND),
    (INHERITED, '09_audit_tally_addendum.md', 2029, 'e205aeb6a3d815dbb5c30f8cc9f5aab8259b59b4a9660d17fd03b258923679f4', LAND),
    # Session 103 (five texts, as in SEALS103.txt).  Four are in prev107/pred and land again.
    (INHERITED, '01_bvh_cap_series.md', 5057, '788f679c0676e47714e154aca86a3336e3f31274d7492113d0a1f8b11c071541', LAND),
    (INHERITED, '02_m5p_bench.md', 6183, '4035a9b0cc6ae89a671706a12731b3e0f21f29c2caa90763f61c0fab4b688a67', LAND),
    (INHERITED, '03_m5p_addendum.md', 1435, '73a7be0d895979b9d458e44c9251ad48d2be9d94c5f6b03d28d7d290b49bb894', LAND),
    (INHERITED, '05_claims_addendum.md', 2141, '7b313d96fefe9379eee5816ca824f94d6000cb4be055b3ae13c72fd19f31a607', LAND),
    # Session 103's four-lens audit addendum.  Its basename is taken in prev104..prev108/pred by session
    # 104's addendum; it stays in the carried prev103/pred.  No live constant names it.
    (CARRIED103, '04_audit_addendum.md', 4345, 'cdc9bab4e9f9ab4d2088a740dcb82c1a0c95a0032e44db23a3007f0e97ec45b0', CARRIED103),
    # Session 100's addendum, which WITHDREW the CLOSE of its pred/02.  Its basename is taken in
    # prev101..prev108/pred by session 101's addendum; it stays in the carried prev100/pred.
    (OLDER, '03_audit_addendum.md', 10653, 'f3c2104b7a27b448a6c46a9526531c22e3d809546be5c51d90cca4e333ecad75', OLDER),
    # Session 104 (five texts, as in SEALS104.txt).
    (INHERITED, '01_reg104.md', 1277, 'd0cdbae98131b5a4d3d8ac782ef23aca3153d6388d43fd05f5dc77df8530cd08', LAND),
    (INHERITED, '02_a_stage1.md', 16476, '29324c0c29603250255b5879d48ae2e9d8574672ef7291ceb27ebc44de2fbb8a', LAND),
    (INHERITED, '03_dawalk.md', 8515, '5f088c02c55b185e8f591ce403b0363b70c61a53bcd088b13354fec78e1d4a13', LAND),
    (INHERITED, '04_audit_addendum.md', 4243, 'd44b59750d09bd9fb605af3339d49f3acc301477a715e4a08415fe2227f435b8', LAND),
    (INHERITED, '05_claims104_addendum.md', 2296, 'd2aea285ac9aaf3e365a9781ba3fc65311a846eb96b247d7eee7869a78b61809', LAND),
    # Session 105 (four texts, as in SEALS105.txt).
    (INHERITED, '01_dawalklead.md', 3715, '7dca62cf623edf98782f0642f40432f460ffaa32237193d449c55bc3fd637e27', LAND),
    (INHERITED, '02_m31.md', 3927, 'c731a5477daf0a01bae83d04b1b962a2f768f37c9b940f8bb257a3b4b30b9449', LAND),
    (INHERITED, '03_scorer_fix.md', 1457, '66cd90e5def18120cbdfd362fef39309898b236fa959f664c64d5b9a5411e656', LAND),
    (INHERITED, '04_audit105.md', 5412, '2853aa9c8847c8777456e3cc1236f9753d0e338680b043615471fff95d05459e', LAND),
    # Session 106 (three texts, as in SEALS106.txt).
    (INHERITED, '01_gwall.md', 4004, '432e3c5bb0fde029b1bebdb85dade4147f59c2f9ab863934269bf3e02100c8c4', LAND),
    (INHERITED, '02_dabatch.md', 3442, 'bde73d27fe761a5cc29d0e54e6afaa33e466f3519f5cf9036b862e57cafd962b', LAND),
    (INHERITED, '03_audit106.md', 5540, 'b5b9695f7e9d8c8e0568f128a9c97361676a8256cdb62980bbb875204ce08ee7', LAND),
    # Session 107 (three texts, as in SEALS107.txt); now in prev107/pred.
    (INHERITED, '01_obs107.md', 3138, '85a65121dce86e65c442becf2f5859ef4c215f1848ad4439902e616872ac1db6', LAND),
    (INHERITED, '02_dabatch2.md', 3077, '3a0d4043e983cda2f9ae19aff4da1ad7cb15861639fe95bd921c6fb61c1027bb', LAND),
    (INHERITED, '03_audit107.md', 4542, '7b6a65316ca562c3a4bda33037b02d1b755c2e7ddfc2616624bb82636158f969', LAND),
    # Session 108 (texts as in SEALS108.txt).  pred/01 seals fam108.py (ABBA cspfam=0|4), pred/02 the audit.
    ('pred', '01_cspfam.md', 6890, 'a40cf056d83fd2ed5b31b1c84e1674f0968803ad481d8831213617c623caa945', LAND),
    ('pred', '02_audit108.md', 4989, '401a76cc9a69d02e7eca10b57d801a3bc0b3e1e85fd8bc0cd59e5679c1fdb885', LAND),
)
SEALS_FILE = 'SEALS108.txt'
S102_NAMES = ('01_m5_bench.md', '02_m5_addendum.md', '03_dabatch.md', '04_checkpoints_fix.md',
              '05_dabatch_addendum.md', '06_ckpt_entry_addendum.md', '07_m5_capture_retry.md',
              '08_audit_addendum.md', '09_audit_tally_addendum.md')
S103_NAMES = ('01_bvh_cap_series.md', '02_m5p_bench.md', '03_m5p_addendum.md', '04_audit_addendum.md',
              '05_claims_addendum.md')
S104_NAMES = ('01_reg104.md', '02_a_stage1.md', '03_dawalk.md', '04_audit_addendum.md',
              '05_claims104_addendum.md')
S105_NAMES = ('01_dawalklead.md', '02_m31.md', '03_scorer_fix.md', '04_audit105.md')
S106_NAMES = ('01_gwall.md', '02_dabatch.md', '03_audit106.md')
S107_NAMES = ('01_obs107.md', '02_dabatch2.md', '03_audit107.md')
S108_NAMES = ('01_cspfam.md', '02_audit108.md')
# Every session's own seal record, re-read against SEALED: (record, names, folder of each text).
SEAL_RECORDS = (('SEALS108.txt', S108_NAMES, {}),
                ('SEALS107.txt', S107_NAMES, {}),
                ('SEALS106.txt', S106_NAMES, {}),
                ('SEALS105.txt', S105_NAMES, {}),
                ('SEALS104.txt', S104_NAMES, {}),
                ('SEALS103.txt', S103_NAMES, {'04_audit_addendum.md': CARRIED103}),
                ('SEALS102.txt', S102_NAMES, {}))
# SEALS108.txt also pins five TOOLS (entries without the pred/ prefix): name -> sha256 at seal time.
SEALS108_TOOLS = {'gates_fam4.txt': FAM4_SHA,
                  'fam108.py': '550d1517191a87dd49de46123fbcb547842744d801720ce7ae47c0545a73cbab',
                  'make_fam108.py': 'b1683b4849212b1a80457d2da8fa0a942e255d4bbff8ff675cd230362f66b215',
                  'test_fam108.py': 'efe01310b399033de8eba25c4fa8504a8476d9b84e610e3960f2bfc0fead4a89',
                  'go108.sh': '5404c59bb21ecfbe3a936a75ca0f55e4a4e56f17e48be82a77e9b8a089da8705'}
# Session 101's texts that prev100/pred never held (prev101/pred holds all twenty sessions 96..101 texts).
PREV101_ONLY = ('01_two_directional.md', '02_regime_addendum.md', '03_audit_addendum.md')
# A draft folder (not a seal folder, never a landing) whose one basename equals a session-106 seal's:
# session 102's draft of its dabatch pre-registration.  (folder, name, bytes, sha256)
DRAFT_SHARED = (('pred_drafts', '02_dabatch.md', 6486, '4b85efd047af1a0ccfaa00fa3a38b61fe8d06dd43b12117f9ab125692e1f8f2d'),)
# r6: scorers whose PRED* (and m5_102.py's ADDENDUM) are bare quoted literals const() can read.
# Twenty-four point into s108/prev107/pred, the session-108 scorer into s108/pred; all land in s109/prev108/pred.
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
    'lead105.py': ('PRED',), 'ctx105.py': ('PRED',),
    'gw106.py': ('PRED',), 'dab106.py': ('PRED',),
    'obs107.py': ('PRED',), 'dab107.py': ('PRED',),
    # Session 108 (next-session-109.md 1): fam108.py:31, a bare literal with PRED_SHA / PRED_BYTES.
    'fam108.py': ('PRED',),
}
REPOINT_FOLDER = {'fam108.py': 'pred'}  # default INHERITED
# r6 files that also pin PRED_BYTES (checked against the landed text after the port).
PRED_BYTES_FILES = ('a104.py', 'cen100.py', 'ckpt102.py', 'cm101.py', 'ctx105.py', 'dab102.py', 'dab106.py',
                    'dab107.py', 'dwk104.py', 'fam108.py', 'gw106.py', 'lead105.py', 'mov100.py', 'obs107.py')
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
# Fixtures of sessions 107 and 108: they load the scorer named on argv, replace its PRED with a throwaway seal
# and write their synthetic logs under the staging folder C:/kyty/s106_stage (outside the harness; the naive
# rewrite does not touch it).  (file, loader text, override text, staging text)
FIXTURE_TESTS = (('test_obs107.py', "spec_from_file_location('obs107', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_obs')"),
                 ('test_dab107.py', "spec_from_file_location('dab107', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_dab107')"),
                 ('test_fam108.py', "spec_from_file_location('fam108', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_fam108')"))
REAL_STAGE = 'C:/kyty/s106_stage'
# Scorers/tools whose seal path is a Path()/ROOT-relative expression, not the bare quoted literal
# const() can read (port repair 7).  It rewrites the relative part only, so the shape of each
# line, any trailing comment and its neighbouring hash constant (if any) are untouched.
# (file, constant, source form, repaired form, sealed basename, sealed folder in SRC, hash constant)
REPOINT2 = (
    ('bf99.py', 'PRED', "PRED = Path('%s/prev107/pred/01_bindings_only.md')",
     "PRED = Path('%s/prev108/pred/01_bindings_only.md')", '01_bindings_only.md', INHERITED, 'PRED_SHA'),
    ('settled99.py', 'PRED', "PRED = ROOT / 'prev107/pred/02_settled_bindings.md'",
     "PRED = ROOT / 'prev108/pred/02_settled_bindings.md'", '02_settled_bindings.md', INHERITED, 'PRED_SHA'),
    ('settled99_gc.py', 'PRED', "PRED = ROOT / 'prev107/pred/04_gc_audit.md'",
     "PRED = ROOT / 'prev108/pred/04_gc_audit.md'", '04_gc_audit.md', INHERITED, 'PRED_SHA'),
    ('settled99_norec.py', 'PRED', "PRED = ROOT / 'prev107/pred/05_observer_separation.md'",
     "PRED = ROOT / 'prev108/pred/05_observer_separation.md'", '05_observer_separation.md', INHERITED, 'PRED_SHA'),
    ('m5_recompile.py', 'PRED', "PRED = ROOT + '/prev107/pred/01_m5_bench.md'",
     "PRED = ROOT + '/prev108/pred/01_m5_bench.md'", '01_m5_bench.md', INHERITED, None),
    ('bvh103.py', 'PRED', "PRED = ROOT + '/prev107/pred/01_bvh_cap_series.md'",
     "PRED = ROOT + '/prev108/pred/01_bvh_cap_series.md'", '01_bvh_cap_series.md', INHERITED, None),
    ('m5p_103.py', 'PRED', "PRED = ROOT + '/prev107/pred/02_m5p_bench.md'",
     "PRED = ROOT + '/prev108/pred/02_m5p_bench.md'", '02_m5p_bench.md', INHERITED, 'PRED_SHA'),
    ('m5p_103.py', 'PARENT01', "PARENT01 = ROOT + '/prev107/pred/01_m5_bench.md'",
     "PARENT01 = ROOT + '/prev108/pred/01_m5_bench.md'", '01_m5_bench.md', INHERITED, 'PARENT01_SHA'),
    ('m5p_103.py', 'PARENT02', "PARENT02 = ROOT + '/prev107/pred/02_m5_addendum.md'",
     "PARENT02 = ROOT + '/prev108/pred/02_m5_addendum.md'", '02_m5_addendum.md', INHERITED, 'PARENT02_SHA'),
    ('check105.py', 'PRED', "PRED = ROOT + '/prev107/pred/02_m31.md'",
     "PRED = ROOT + '/prev108/pred/02_m31.md'", '02_m31.md', INHERITED, None),
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
                   'lead105.py', 'ctx105.py', 'check105.py',
                   'gw106.py', 'dab106.py', 'fixture_gw106.py', 'fixture_dab106.py',
                   'obs107.py', 'dab107.py', 'test_obs107.py', 'test_dab107.py',
                   # Session 108 (next-session-109.md 1): fam108.py pinned to its seal, binary and the gates
                   # baseline; its fixtures load the scorer named on argv; the two video checks are pinned to
                   # their builds and read C:/kyty/s108 logs.
                   'fam108.py', 'test_fam108.py', 'check108.py', 'check108r.py'}
# Archive tools whose run root the naive rewrite moves to s109, where none of their inputs live.
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
              ('audit105/recount_protocol/recount.py', 'root', 'the session-105 logs (in s105); audit evidence, never run'),
              ('gw106.py', 'PRODUCTION_ROOT', 'log_gw106.txt (in s106)'),
              ('dab106.py', 'PRODUCTION_ROOT', 'log_dab106.txt (in s106)'),
              ('dab107.py', 'PRODUCTION_ROOT', 'log_dab107.txt (in s107)'),
              ('audit107/dab107_mutS2.py', 'PRODUCTION_ROOT', 'log_dab107.txt (in s107); audit mutant, never run'),
              # Session 108 (next-session-109.md 1): the scorer and the two video checks (logs stay in s108).
              ('fam108.py', 'PRODUCTION_ROOT', 'log_fam108.txt (in s108)'),
              ('check108.py', 'ROOT', 'log_vid108.txt (in s108); vid108.json and vid108_glitch.txt are carried'),
              ('check108r.py', 'ROOT', 'log_vid108r.txt (in s108); vid108r.json and vid108r_glitch.txt are carried'))
# Scorers whose default run root is an inline literal (not a module constant): obs107.py's main() and its
# audit mutant.  (file, text with %s = root, what it would miss)
INLINE_ROOT_MOVED = (('obs107.py', "if '--root' in sys.argv else '%s'", 'log_obs107.txt (in s107)'),
                     ('audit107/obs107_mutPIN.py', "if '--root' in sys.argv else '%s'",
                      'log_obs107.txt (in s107); audit mutant, never run'))
# Audit evidence that opens a log by a root literal: session 106's inline opens and session 107's LOG
# constants.  (file, text with %s = root, what it would miss)
AUDIT_INLINE_MOVED = (('audit106/recount_protocol/drop_pairs.py', "open('%s/log_dab106.txt', 'rb')",
                       'log_dab106.txt (in s106)'),
                      ('audit106/recount_protocol/qcall.py', "open('%s/log_%%s.txt' %% t, 'rb')",
                       'log_vdb106.txt, log_vid106.txt (in s106)'),
                      ('audit107/recount_dab.py', "LOG = '%s/log_dab107.txt'", 'log_dab107.txt (in s107)'),
                      ('audit107/recount_obs.py', "LOG = '%s/log_obs107.txt'", 'log_obs107.txt (in s107)'),
                      ('audit107/dab_mech.py', "LOG = '%s/log_dab107.txt'", 'log_dab107.txt (in s107)'))
# Session-108 audit evidence that reads the parse dumps audit108/p_<tag>.json (made by parse108.py from the
# C:/kyty/s108 logs); the dumps are NOT carried.  (file, text with %s = root, note)
AUDIT_READS_DUMPS = (('audit108/guards108.py', "open('%s/audit108/p_%%s.json' %% tag)", ''),
                     ('audit108/profile108.py', "'%s/audit108/p_%%s.json' %% TAG", ' (default; a path on argv wins)'),
                     ('audit108/recount108.py', "open('%s/audit108/p_%%s.json' %% TAG)",
                      '; it would also overwrite the carried audit108/recount108.json'))
# Session-108 audit parser: log and output both on argv, no root literal.
AUDIT_ARGV = ('audit108/parse108.py',)
# Session-108 mutant table: data only (no root literal); mutants108.py holds an identical copy.
MUTANTS_DEF = 'audit108/mutants_def.py'
# Audit evidence that reads the scorers and fixtures it audited by path; after the naive rewrite it names the
# s109 copies, which differ from the audited files (naive + r6).  (file, names read, root audited)
AUDIT_READS_COPIES = (('audit106/recount_protocol/fields_cov.py',
                       ('gw106.py', 'fixture_gw106.py', 'dab106.py', 'fixture_dab106.py'), PREV106_ROOT),
                      # Session 108's mutant runners: they build mutants of fam108.py and run test_fam108.py.
                      ('audit108/mutants108.py', ('fam108.py', 'test_fam108.py'), SRC),
                      ('audit108/mutants108p.py', ('fam108.py', 'test_fam108.py'), SRC))
# Session-104 archive scorers pin the PRE-SHIP gates baseline; after the naive rewrite their
# GATES_FILE names the s109 copy, which holds the shipped dawalk=1 text.  Report only.
GATES_PINNED = ('a104.py', 'dwk104.py')
# Session-105..108 archive scorers pin the CURRENT baseline (303a7849...); the pin still holds in s109.
GATES_CURRENT = ('lead105.py', 'ctx105.py', 'gw106.py', 'dab106.py', 'dab107.py', 'fam108.py')
BINARY_PINNED = ('a104.py', 'dwk104.py', 'lead105.py', 'ctx105.py', 'gw106.py', 'dab106.py', 'dab107.py',
                 'fam108.py')
# Session-108 video checks pinned to their builds by BUILD_SHA; the scored binaries stay in s108.
BUILD_PINNED = (('check108.py', 'kyty_emulator_fc78c564.exe'), ('check108r.py', 'kyty_emulator_379777bb.exe'))
# Session-108 outputs that hash their own tool into the output = the s108 files.  (tool, output, key)
SELF_HASHED = (('fam108.py', 'runs108/fam108_score.json', 'scorer_sha256'),
               ('fam108.py', 'runs108/fam108_score_video.json', 'scorer_sha256'),
               ('check108.py', 'runs108/check108.json', 'check_sha256'),
               ('check108r.py', 'runs108/check108r.json', 'check_sha256'))
# Session-107 run outputs record the ORIGINAL C:/kyty/s107 scorers' sha256 (the s108 copies already differ).
SELF_HASHED_PRIOR = (('obs107.py', 'runs107/obs107_score.json'), ('dab107.py', 'runs107/dab107_score.json'))
# Offline tests whose optional real-log case reads a log the port never carries.  Report only.
TEST_LOG_MOVED = (('test_a104.py', "'%s/log_reg104.txt'"), ('test_dwk104.py', "'%s/log_reg104.txt'"))
# One-shot scripts of sessions 103..108 (patches of the source tree, of the session documents and of the game
# contexts, and the generators of ctx105.py, gw106.py, dab106.py, dab107.py, fam108.py).  Carried by naive
# rewrite, never run.
ONE_SHOT = ('patch_s103_bdalean.py', 'patch_s103_envflag.py', 'patch_s103_loopcap.py',
            'patch_s103_loopcap_host.py', 'facts_audit_fix.py', 'claims_fix.py', 'roadmap_s103.py',
            'claude_md_s103.py', 'handoff_s103.py',
            'claims_fix104.py', 'claude_md_s104.py',
            'make_ctx105.py',
            'make_gw106.py', 'make_dab106.py', 'roadmap106_close.py',
            'make_dab107.py', 'roadmap107_close.py',
            'make_fam108.py', 'roadmap108_close.py', 'facts108_fix.py', 'ctx108.py', 'handoff108.py')
# target <root>/FACTS.md -> s109 after the naive rewrite
ONE_SHOT_MOVED = ('facts_audit_fix.py', 'claims_fix.py', 'claims_fix104.py', 'facts108_fix.py')
# Session-108 one-shots that patch the game folder's contexts (targets not moved by the rewrite).
# (file, target text)
GAME_ONE_SHOTS = (('ctx108.py', "root = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')"),
                  ('handoff108.py', "p = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em/HANDOFF.md')"))
# One-shot ROADMAP patches, simulated in memory against the current ROADMAP.  (file, inserted text, target line)
ROADMAP_PATCHES = (('roadmap106_close.py', 'pred/03_audit106.md', "p = 'C:/kyty/KytyPS5/docs/ROADMAP.md'"),
                   ('roadmap107_close.py', 'pred/03_audit107.md', "p = 'C:/kyty/KytyPS5/docs/ROADMAP.md'"),
                   ('roadmap108_close.py', 'pred/02_audit108.md', "p = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')"))
# Usage docstrings that name the staging folder the 107 port had already moved (C:/kyty/s107_stage) and the
# 108 port moved again (C:/kyty/s108_stage, absent); the naive rewrite moves them once more.
STAGE_MENTIONS = ('fixture_dab106.py', 'fixture_gw106.py', 'make_gw106.py')
STAGE = 'C:/kyty/s108_stage'
STAGE_NEXT = 'C:/kyty/s109_stage'
# Exploratory session-106 analysis: no seal; default log in s104 (unchanged by the rewrite).
EXPLORATORY = (('explore106_dwk104.py', "'C:/kyty/s104/log_dwk104.txt'"),)
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
# Session 108's audit: 22 mutants of fam108.py (audit108/mutants/fam108_<name>.py, CRLF, written by
# mutants108.py from the table in mutants_def.py) and 19 worker copies of test_fam108.py
# (audit108/mutants/test_fam108_w<i>.py, BASE in audit108/fx_w<i>; mutants108p.py).
MUTANT_DIR = 'audit108/mutants'
N_MUTANTS_108 = 22
N_TEST_COPIES_108 = 19
TEST_BASE_108 = "BASE = Path('C:/kyty/s106_stage/fx_fam108')"
# Frozen evidence with a BARE literal that r6 (keyed by the top-level name) deliberately does not
# reach: the session-105 audit's copy of the committed, pre-fix ctx105.py, session 107's audit mutants of
# obs107.py and dab107.py, and (added in mutant_names()) session 108's 22 audit mutants of fam108.py.
# (file, line, basename)
FROZEN_DANGLING_BARE = (('audit105/recount_protocol/ctx105_git.py', "PRED = '%s/pred/02_m31.md'", '02_m31.md'),
                        ('audit107/obs107_mutPIN.py', "PRED = '%s/pred/01_obs107.md'", '01_obs107.md'),
                        ('audit107/dab107_mutS2.py', "PRED = '%s/pred/02_dabatch2.md'", '02_dabatch2.md'))
# The two session-107 mutants differ from their scorers in the mutated lines plus the PRED line (r6 reached the
# scorer in the 108 port, not the mutant): (mutant, scorer, mutated lines).
MUTANTS_107 = (('audit107/obs107_mutPIN.py', 'obs107.py', 2), ('audit107/dab107_mutS2.py', 'dab107.py', 1))
# Offline tests that read their seal as HERE / 'pred/...'; report only, never repaired.
HERE_DANGLING = (('test_cen100.py', "pred = HERE / 'pred/01_addend_census.md'"),
                 ('test_mov100.py', "pred = HERE / 'pred/02_moved_mark.md'"),
                 ('test_cm101.py', "pred = HERE / 'pred/02_regime_addendum.md'"))
# Seal reads inside a function body (not a module constant); report only, never repaired.
# (file, exact text in DST, seal basenames it names under <root>/pred/)
ROOT_DANGLING = (
    ('m5_run.py', "seal_sha256={p.name: sha(p) for p in (ROOT / 'pred/01_m5_bench.md', "
     "ROOT / 'pred/02_m5_addendum.md')},", ('01_m5_bench.md', '02_m5_addendum.md')),
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
                  ('go105.sh', 'cd /c/kyty/s105'), ('go105b.sh', 'cd /c/kyty/s105'),
                  ('go106.sh', 'cd /c/kyty/s106'), ('go106b.sh', 'cd /c/kyty/s106'),
                  ('go107.sh', 'cd /c/kyty/s107'), ('go107b.sh', 'cd /c/kyty/s107'),
                  # Session 108's run chains (they ENTER THE GAME and hold C:/kyty/SEALED_RUN.lock; never run).
                  ('go108.sh', 'cd /c/kyty/s108'), ('go108v.sh', 'cd /c/kyty/s108'),
                  ('go108s.sh', 'cd /c/kyty/s108'), ('go108p.sh', 'cd /c/kyty/s108'),
                  ('go108r.sh', 'cd /c/kyty/s108'))
# Dangling-path census: carried Python files that, after repair, name <DST>/<path> where <SRC>/<path>
# exists but <DST>/<path> does not.  Every hit must be one of these (file -> paths); the 22 session-108
# audit mutants (pred/01_cspfam.md each) are added in census_want().
CENSUS = {
    'make_fam108.py': ('pred/01_cspfam.md',),         # the replacement text of its second rep()
    'roadmap108_close.py': ('pred/02_audit108.md',),  # the text it would insert into the ROADMAP
    'handoff108.py': ('FACTS.md', 'pred/02_audit108.md'),  # the text it would write into HANDOFF.md
}
# ... or one of these files that mention (or, for ONE_SHOT_MOVED, target) <root>/FACTS.md: session FACTS.md
# files are archived under prev<N>/ by rule, so every port leaves these pointing at a FACTS.md the
# destination does not hold yet.  Report only; never run.
FACTS_MENTIONS = ('check_block_numbers.py', 'claims_fix.py', 'claims_fix104.py', 'claude_md_s103.py',
                  'claude_md_s104.py', 'design98/apply_roadmap98.py', 'facts_audit_fix.py', 'finalize99.py',
                  'finalize_cal99a.py', 'fix_binary_hash.py', 'handoff_s103.py', 'patch_audit88.py',
                  'patch_claude87.py', 'patch_claude90.py', 'patch_commit_hash.py', 'patch_context.py',
                  'patch_context100.py', 'patch_context100b.py', 'patch_context101.py', 'patch_context102.py',
                  'patch_context84.py', 'patch_context85.py', 'patch_context86.py', 'patch_docs94.py',
                  'patch_facts_0.py', 'patch_facts_1415.py', 'patch_facts_16.py', 'patch_facts_exploit.py',
                  'patch_facts_rest.py', 'patch_roadmap100.py', 'patch_roadmap100b.py', 'patch_roadmap101.py',
                  'patch_roadmap102.py', 'patch_roadmap91.py', 'patch_roadmap94.py', 'patch_roadmap94e.py',
                  's76_entry.py', 's76_entry_fix.py', 'stamp_commit.py', 'update_context.py', 'wire_roadmap.py',
                  # Session 108's close: the FACTS patch (targets it) and the game-context patch (names it).
                  'facts108_fix.py', 'ctx108.py')
N_FACTS_MENTIONS = 43
# Tag -> session whose root holds log_<tag>.txt (logs are never carried).
ROOT_TESTS = (('fam108', 108), ('sf108a', 108), ('sf108b', 108), ('sf108c', 108), ('sf108d', 108),
              ('vfm108', 108), ('vid108', 108), ('vid108r', 108),
              ('obs107', 107), ('dab107', 107),
              ('gw106', 106), ('dab106', 106), ('vdb106', 106), ('vid106', 106),
              ('lead105', 105), ('abb105', 105), ('ctx105', 105), ('reg105a', 105), ('reg105b', 105),
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


def lf(t):
    return t.replace('\r\n', '\n')


def chain(hi, lo, comma=False):
    values = ['C:/kyty/s%d' % i for i in range(hi, lo - 1, -1)]
    return ','.join(values) if comma else '(' + ', '.join(repr(v) for v in values) + ')'


def naive(t):
    for before, after in ((OLD, NEW), (OLD.replace('/', '\\\\'), NEW.replace('/', '\\\\')),
                          (OLD.replace('/', '\\'), NEW.replace('/', '\\')),
                          ('/c/kyty/s108', '/c/kyty/s109')):
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


def mutant_table():
    """{name: (old, new)} of session 108's audit mutants, read from mutants_def.py by AST (never imported)."""
    tree = ast.parse(rd(SRC / MUTANTS_DEF))
    found = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'MUTANTS']
    assert len(found) == 1
    table = ast.literal_eval(found[0].value)
    assert len(table) == N_MUTANTS_108, len(table)
    return table


def mutant_names():
    return ['%s/fam108_%s.py' % (MUTANT_DIR, n) for n in sorted(mutant_table())]


def test_copy_names():
    return ['%s/test_fam108_w%d.py' % (MUTANT_DIR, i) for i in range(N_TEST_COPIES_108)]


def frozen_bare():
    return FROZEN_DANGLING_BARE + tuple((f, "PRED = '%s/pred/01_cspfam.md'", '01_cspfam.md') for f in mutant_names())


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
    replace('r1', 'C:/kyty/s109,C:/kyty/s107', 'C:/kyty/s109,C:/kyty/s108,C:/kyty/s107', False)
    if key in ARITH:
        floor, tag = ARITH[key]
        replace(tag, 'range(108, %d, -1)' % floor, 'range(109, %d, -1)' % floor)
    if key in TUPLES:
        replace('r4', naive(chain(108, TUPLES[key])), chain(109, TUPLES[key]))
    if key == 'regime94.py':
        replace('r5', naive(regime(108)), regime(109))
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
    """({text basename: sha256}, {tool name: sha256}) of a session's SEALSnnn.txt ('<sha> *[pred/]<name>' per
    line).  SEALS108.txt pins tools too: there only the pred/-prefixed entries are texts."""
    texts, tools = {}, {}
    for line in rd(SRC / name).splitlines():
        if line.strip():
            h, n = line.split()
            n = n.lstrip('*')
            prefixed = n.startswith('pred/')
            n = n[len('pred/'):] if prefixed else n
            assert '/' not in n and n not in texts and n not in tools, (name, line)
            if name == 'SEALS108.txt' and not prefixed:
                tools[n] = h
            else:
                texts[n] = h
    return texts, tools


def pred_folders(root):
    """Every directory named 'pred' below root except root/pred itself (the seal folders of the walk)."""
    out = []
    for d, dirs, _files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIR)
        for x in dirs:
            p = Path(d) / x
            if x == 'pred' and p != root / 'pred':
                out.append(p)
    return out


def generator_facts(root):
    """The anchors of the five one-shot generators, as they read under <root>:
    (generator, line it holds, source file it edits, anchor it needs in that source, its first anchored
    edit, its only write)."""
    r = root.as_posix()
    return (('make_ctx105.py', "PRED = '%s/pred/02_m31.md'" % r, 'lead105.py',
             "PRED = '%s/pred/01_dawalklead.md'" % r, "data = open(PRED, 'rb')", "open(DST, 'w'"),
            ('make_gw106.py', 'rep("PRODUCTION_ROOT = \'C:/kyty/s105\'", "PRODUCTION_ROOT = \'%s\'")' % r,
             'dwk104.py', "PRODUCTION_ROOT = 'C:/kyty/s105'", 'rep("PRODUCTION_ROOT', "open(DST, 'w'"),
            ('make_dab106.py', 'rep("PRED = \'%s/prev105/pred/01_dawalklead.md\'", "PRED = \'%s/pred/02_dabatch.md\'")'
             % (r, r), 'lead105.py', "PRED = '%s/prev105/pred/01_dawalklead.md'" % r,
             'rep("PRED = \'%s/prev105/pred/01_dawalklead.md\'"' % r, "open(DST, 'w'"),
            ('make_dab107.py', 'rep("PRED = \'%s/prev106/pred/02_dabatch.md\'", "PRED = \'%s/pred/02_dabatch2.md\'")'
             % (r, r), 'dab106.py', "PRED = '%s/prev106/pred/02_dabatch.md'" % r,
             'rep("PRED = \'%s/prev106/pred/02_dabatch.md\'"' % r, "open(DST, 'w'"),
            # Session 108: its anchors name C:/kyty/s107 (the dab107.py it was run on, given on argv); only its
            # replacement texts name the root.
            ('make_fam108.py', 'rep("PRED = \'C:/kyty/s107/pred/02_dabatch2.md\'", "PRED = \'%s/pred/01_cspfam.md\'")'
             % r, 'dab107.py', "PRODUCTION_ROOT = 'C:/kyty/s107'", 'rep("PRODUCTION_ROOT', "open(DST, 'w'"))


_SEP = r'(?:/|\\\\|\\)'
CENSUS_RX = re.compile(r"(?:C:" + _SEP + r"kyty" + _SEP + r"s109|/c/kyty/s109)(" + _SEP + r"[^'\"\s,)%*<>`]+)")


def census(texts, exists):
    """{file: sorted paths} over texts ({key: repaired text}, ports excluded): every <DST>/<path> named in a
    text whose <SRC>/<path> exists while exists(<path>) is false."""
    hits = {}
    for key, t in texts.items():
        if key.endswith('_port.py'):
            continue
        for m in CENSUS_RX.finditer(t):
            tail = re.sub(r'(?:\\\\|\\|/)+', '/', m.group(1)).strip('/').rstrip('.:;')
            if not tail or not tail.replace('.', '').replace('/', ''):
                continue
            if (SRC / tail).exists() and not exists(tail):
                hits.setdefault(key, set()).add(tail)
    return {k: tuple(sorted(v)) for k, v in hits.items()}


def census_want():
    want = dict(CENSUS)
    for f in mutant_names():
        assert f not in want, f
        want[f] = ('pred/01_cspfam.md',)
    for f in FACTS_MENTIONS:
        assert f not in want, f
        want[f] = ('FACTS.md',)
    return want


def check_census(hits, stage):
    assert len(FACTS_MENTIONS) == len(set(FACTS_MENTIONS)) == N_FACTS_MENTIONS
    assert set(ONE_SHOT_MOVED) <= set(FACTS_MENTIONS)
    want = census_want()
    assert hits == want, (stage, sorted(set(hits.items()) ^ set(want.items())))


def skip_reason(key, f, sp, rel):
    """Why a source file is not carried (None: carried)."""
    if AUDIT_DUMP_RX.match(key):
        return 'audit-dump'
    if rel == Path('.') and CONCURRENT_RX.match(f):
        return 'concurrent-109'
    if f.startswith(SKIP_PREFIX) or f.endswith(SKIP_EXT) or sp.stat().st_size >= BIG:
        return 'model'
    if rel == Path('.') and f in DOCS:
        return 'doc'
    return None


def preconditions():
    assert SRC.resolve() != DST.resolve()
    assert not DST.exists(), 'destination exists: do not rerun a completed port'
    assert not (SRC / 'prev108').exists()
    assert not (SRC / LEDGER_NAME).exists()
    assert (SRC / PREV_LEDGER).is_file()
    for f, opt in COMMA.items():
        t = rd(SRC / f)
        m = re.search(r"add_argument\('" + re.escape(opt) + r"', default='([^']*)'", t)
        assert m and m.group(1) == chain(108, 75, True), f
        assert len(m.group(1).split(',')) == 34, f
    for f, (floor, _) in ARITH.items():
        assert rd(SRC / f).count('range(108, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(SRC / f).count(chain(108, floor)) == 1, f
    assert {f: 108 - floor + 1 for f, floor in TUPLES.items()} == {'stg92.py': 19, 'bda93.py': 18, 's94lib.py': 17}
    assert rd(SRC / 'regime94.py').count(regime(108)) == 1 and 108 - 93 + 1 == 16
    assert rd(SRC / 'regime94.py').splitlines()[2] == 'import os, re, sys, statistics'
    assert tuple(f for f in DOCS if (SRC / f).is_file()) == DOCS_PRESENT, [f for f in DOCS if (SRC / f).is_file()]
    sealed = sealed_index()
    assert len(sealed) == len(SEALED) == 52
    # No two texts may land on one path and no text is renamed.  The only shared basenames are
    # the two inherited pairs of audit addenda: sessions 100/101 (03_) and sessions 103/104 (04_).
    assert len({(land, n) for _, n, _, _, land in SEALED}) == 52
    names_all = [n for _, n, _, _, _ in SEALED]
    assert sorted({n for n in names_all if names_all.count(n) > 1}) == ['03_audit_addendum.md', '04_audit_addendum.md']
    s108_names = {n for d, n, _, _, _ in SEALED if d == 'pred'}
    assert s108_names == set(S108_NAMES) and len(s108_names) == 2
    # Collision check over EVERY earlier pred/ folder of the source (prev78..prev107, all of them, not
    # only the listed texts and not only the eight carried ones): no session-108 basename is taken.
    folders = pred_folders(SRC)
    assert {p.relative_to(SRC).as_posix() for p in folders} >= set(CARRIED), folders
    assert len(folders) == 28, [p.relative_to(SRC).as_posix() for p in folders]
    every_name = set()
    for p in folders:
        every_name |= {q.name for q in p.iterdir()}
    assert not s108_names & every_name, s108_names & every_name
    # ... nor anywhere else in the source outside its pred/.
    elsewhere108 = sorted(q.relative_to(SRC).as_posix() for q in SRC.rglob('*')
                          if q.name in s108_names and q.parent != SRC / 'pred')
    assert elsewhere108 == [], elsewhere108
    # Session-107 basenames live only in prev107/pred (the 108 port landed them there).
    elsewhere107 = sorted(q.relative_to(SRC).as_posix() for q in SRC.rglob('*')
                          if q.name in S107_NAMES and q.parent != SRC / INHERITED)
    assert elsewhere107 == [], elsewhere107
    # A draft folder shares one basename with a session-106 seal (in prev107/pred and prev106/pred); it is not
    # a seal folder and differs.  No other copy of a session-106 basename exists outside those two folders.
    for folder, n, size, h in DRAFT_SHARED:
        p = SRC / folder / n
        assert n in S106_NAMES and p.stat().st_size == size and sha(p) == h, (folder, n)
        assert h != sealed[(INHERITED, n)][1]
    shared106 = sorted(q.relative_to(SRC).as_posix() for q in SRC.rglob('*')
                       if q.name in S106_NAMES and q.parent not in (SRC / INHERITED, SRC / CARRIED106))
    assert shared106 == ['%s/%s' % (f, n) for f, n, _, _ in DRAFT_SHARED], shared106
    assert all(land in (LAND, d) for d, _, _, _, land in SEALED)
    assert sum(1 for _, _, _, _, land in SEALED if land == LAND) == 50
    assert [(d, n) for d, n, _, _, land in SEALED if land != LAND] == [
        (CARRIED103, '04_audit_addendum.md'), (OLDER, '03_audit_addendum.md')]
    for folder in ('pred', INHERITED):
        assert sorted(p.name for p in (SRC / folder).iterdir()) == sorted(n for d, n, _, _, _ in SEALED if d == folder), folder
    inherited_names = [n for d, n, _, _, _ in SEALED if d == INHERITED]
    assert len(inherited_names) == 48
    assert set(S102_NAMES) | set(S104_NAMES) | set(S105_NAMES) | set(S106_NAMES) | set(S107_NAMES) | \
        (set(S103_NAMES) - {'04_audit_addendum.md'}) <= set(inherited_names)
    # prev106/pred: forty-five byte-identical twins of prev107/pred texts (sessions 96..106).
    twins106 = sorted(n for n in inherited_names if n not in S107_NAMES)
    assert len(twins106) == 45 and sorted(p.name for p in (SRC / CARRIED106).iterdir()) == twins106
    # prev105/pred: forty-two twins (sessions 96..105).
    twins105 = sorted(n for n in twins106 if n not in S106_NAMES)
    assert len(twins105) == 42 and sorted(p.name for p in (SRC / CARRIED105).iterdir()) == twins105
    # prev104/pred: thirty-eight twins (sessions 96..104; its 04_audit_addendum.md is session 104's).
    twins104 = sorted(n for n in twins105 if n not in S105_NAMES)
    assert len(twins104) == 38 and sorted(p.name for p in (SRC / CARRIED104).iterdir()) == twins104
    # prev103/pred: thirty-three twins (sessions 96..103) plus session 103's own 04_audit_addendum.md,
    # which differs from session 104's.
    twins103 = sorted(n for n in twins104 if n not in S104_NAMES)
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
    for folder, twins in ((CARRIED106, twins106), (CARRIED105, twins105), (CARRIED104, twins104),
                          (CARRIED103, twins103), (CARRIED102, twins102), (CARRIED101, twins101), (OLDER, twins100)):
        for n in twins:
            assert sha(SRC / folder / n) == sealed[(INHERITED, n)][1] == sha(SRC / INHERITED / n), ('twin', folder, n)
    for d, n, size, h, _ in SEALED:
        assert (SRC / d / n).stat().st_size == size and sha(SRC / d / n) == h, (d, n)
    # The sessions' own seal records: SEALS108.txt names exactly the two session-108 texts (in pred/) plus five
    # tools; SEALS107/106/105/104/103/102.txt still name theirs, now read from prev107/pred.
    for record, names, where in SEAL_RECORDS:
        texts, tools = seal_record(record)
        want = {n: sealed[(where.get(n, 'pred' if record == SEALS_FILE else INHERITED), n)][1] for n in names}
        assert texts == want, (record, texts)
        assert tools == (SEALS108_TOOLS if record == SEALS_FILE else {}), (record, tools)
    for n, h in SEALS108_TOOLS.items():
        assert sha(SRC / n) == h, ('sealed tool changed since SEALS108.txt', n)
    live_paths = 0
    for f, names in REPOINT.items():
        t = rd(SRC / f)
        folder = REPOINT_FOLDER.get(f, INHERITED)
        for name in names:
            p = Path(const(t, name))
            assert p.parent == SRC / folder, (f, name, p)
            key = (folder, p.name)
            assert const(t, name + '_SHA') == sealed[key][1] == sha(p), (f, name)
            assert sealed[key][2] == LAND, ('live constant names a text outside prev108/pred', f, name)
            live_paths += 1
        m = re.search(r'^PRED_BYTES\s*=\s*(\d+)', t, re.M)
        if m:
            assert int(m.group(1)) == sealed[(folder, Path(const(t, 'PRED')).name)][0], f
    assert len(REPOINT) == 25 and live_paths == 36, (len(REPOINT), live_paths)
    assert sorted(f for f in REPOINT if re.search(r'^PRED_BYTES\s*=', rd(SRC / f), re.M)) == sorted(PRED_BYTES_FILES)
    assert set(REPOINT_FOLDER) <= set(PRED_BYTES_FILES)
    for f, text in IMPORTERS:
        assert text in rd(SRC / f), (f, text)
    for f, imp, override in SEAL_OVERRIDE_TESTS:
        t = rd(SRC / f)
        assert imp in t and override in t, f
    for f, loader, override, stage in FIXTURE_TESTS:
        t = rd(SRC / f)
        assert loader in t and override in t and stage in t and 'pred/' not in t, f
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
    # No other top-level Python file names a session-105..108 seal as a module constant (a quoted literal,
    # a ROOT +/ROOT / expression or a Path(...) whose text names pred/<name>).
    seal_rx = (r"^(\w+)\s*=\s*((?:ROOT\s*[+/]\s*|Path\()?['\"][^'\"\n]*pred/(?:%s)['\"].*)$"
               % '|'.join(re.escape(n) for n in S105_NAMES + S106_NAMES + S107_NAMES + S108_NAMES))
    r7_pairs = {(f, c) for f, c, _, _, _, _, _ in REPOINT2}
    for p in sorted(SRC.glob('*.py')):
        for m in re.finditer(seal_rx, rd(p), re.M):
            assert (p.name in REPOINT and m.group(1) in REPOINT[p.name]) or (p.name, m.group(1)) in r7_pairs or \
                p.name in ONE_SHOT or p.name.endswith('_port.py'), (p.name, m.group(0))
    for f in ARCHIVE_SCORERS | set(ONE_SHOT):
        assert (SRC / f).is_file(), f
    # seal108.py (named in next-session-109.md 1) is not in the source: nothing to class.
    assert not [q for q in SRC.rglob('seal108*')], 'seal108 found in the source'
    for f, text_, basename in frozen_bare():
        assert rd(SRC / f).count(text_ % OLD) == 1 and basename in S105_NAMES + S107_NAMES + S108_NAMES, f
    for mutant, scorer, n_lines in MUTANTS_107:
        a, b = rd(SRC / scorer).splitlines(), rd(SRC / mutant).splitlines()
        diff = [i for i, (x, y) in enumerate(zip(a, b), 1) if x != y]
        assert len(a) == len(b) and len(diff) == n_lines + 1, (mutant, diff)
        assert sum(1 for i in diff if a[i - 1].startswith('PRED = ') and b[i - 1].startswith('PRED = ')) == 1, mutant
    # Session 108's audit mutants: each is fam108.py with exactly its mutants_def.py replacement (CRLF);
    # the worker copies are test_fam108.py with BASE moved into audit108/fx_w<i>.
    fam = rd(SRC / 'fam108.py')
    assert '\r' not in fam
    table = mutant_table()
    for name, (old, new) in table.items():
        p = SRC / MUTANT_DIR / ('fam108_%s.py' % name)
        assert fam.count(old) == 1 and lf(rd(p)) == fam.replace(old, new), name
    got = sorted(p.relative_to(SRC).as_posix() for p in (SRC / MUTANT_DIR).glob('*.py'))
    assert got == sorted(mutant_names() + test_copy_names()), got
    test = rd(SRC / 'test_fam108.py')
    assert test.count(TEST_BASE_108) == 1 and '\r' not in test
    for i, f in enumerate(test_copy_names()):
        assert lf(rd(SRC / f)) == test.replace(TEST_BASE_108, "BASE = Path('%s/audit108/fx_w%d')" % (OLD, i)), f
        assert (SRC / 'audit108' / ('fx_w%d' % i)).is_dir(), i
    mt108 = [n for n in ast.parse(rd(SRC / 'audit108/mutants108.py')).body if isinstance(n, ast.Assign)
             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'MUTANTS']
    assert len(mt108) == 1 and ast.literal_eval(mt108[0].value) == table
    assert 'C:/kyty' not in rd(SRC / MUTANTS_DEF)
    for f in AUDIT_ARGV:
        t = rd(SRC / f)
        assert 'C:/kyty' not in t and 'sys.argv[1], sys.argv[2]' in t, f
    for f, text_, _note in AUDIT_READS_DUMPS:
        assert rd(SRC / f).count(text_ % OLD) == 1, f
    dumps = sorted(p.relative_to(SRC).as_posix() for p in (SRC / 'audit108').glob('p_*.json'))
    assert dumps == sorted(AUDIT_DUMPS), dumps
    for n, h in BINARIES108.items():
        assert (SRC / n).is_file() and n.endswith(SKIP_EXT) and n[len('kyty_emulator_'):-4] == h[:8], n
    # Gates baseline: 1092 B / 99 names, dawalk=1 (shipped by session 104); dabatch, ctxtick, cspmemo,
    # cspfam absent.
    g = SRC / 'gates_base.txt'
    assert g.stat().st_size == 1092 and sha(g) == GATES_SHA
    names = [x.split('=')[0] for x in rd(g).split() if '=' in x]
    assert len(names) == len(set(names)) == 99
    assert 'dawalk=1' in gate_tokens(g) and not {'ctxtick', 'dabatch', 'cspmemo', 'cspfam'} & set(names)
    assert g.read_bytes().count(b'\r\n') == 1 and g.read_bytes().endswith(b'\r\n')
    for f, size, h in ARCHIVE_DATA:
        assert (SRC / f).stat().st_size == size and sha(SRC / f) == h, f
    pre = gate_tokens(SRC / 'gates_base.pre104ship.txt')
    assert [x if x != 'dawalk=0' else 'dawalk=1' for x in pre] == gate_tokens(g), 'pre-ship differs beyond dawalk'
    for f, extra in PLUS_FILES:
        assert gate_tokens(SRC / f) == gate_tokens(g) + list(extra), f
        assert (SRC / f).read_bytes() == g.read_bytes()[:-2] + (' ' + ' '.join(extra)).encode() + b'\r\n', f
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
    assert const(rd(SRC / 'fam108.py'), 'BINARY_SHA') == BINARIES108['kyty_emulator_fd1d0bd7.exe']
    for f, exe in BUILD_PINNED:
        assert const(rd(SRC / f), 'BUILD_SHA') == BINARIES108[exe], f
    text = rd(GATES)
    entry = r'\{\s*"KYTY_\w+",\s*"([a-z0-9]+)"'
    cpp = re.findall(entry, text)
    assert len(cpp) == len(set(cpp)) == GATES_CPP_ENTRIES, ('gates.cpp entry count changed: STOP and report', len(cpp))
    cut = text.index('KNOB_DEFINITIONS')
    split = (len(re.findall(entry, text[:cut])), len(re.findall(entry, text[cut:])))
    assert split == GATES_CPP_SPLIT, split
    assert re.findall(entry, text[:cut])[-1] == 'cbmove'
    assert re.findall(entry, text[cut:])[-3:] == ['ctxtick', 'cspmemo', 'cspfam']
    assert text.count(CTXTICK_ROW) == 1 and text.count(CSPMEMO_ROW) == 1 and text.count(CSPFAM_ROW) == 1
    assert text.count(DABATCH_ROW) == 1 and text.index(DABATCH_ROW) > cut, 'dabatch default is not 8'
    assert len(ABSENT) == len(set(ABSENT)) == 39 == GATES_CPP_ENTRIES - 99
    assert set(ABSENT) == set(cpp) - set(names)
    assert not set(ABSENT) & set(names)
    assert all(not (SRC / f).exists() for f in NEW_SESSION)
    assert not [q for q in SRC.rglob('*') if q.name in NEW_SESSION]
    assert all((SRC / f).is_file() for f in NEW_SESSION_CARRIED)
    assert not any(d.is_dir() and d.name.startswith('design109') for d in SRC.iterdir())
    # Root-level names with a session-109 tag: only the concurrent executor's build logs.
    s109_named = sorted(p.name for p in SRC.iterdir() if 's109' in p.name and p.name != 's109_port.py')
    assert all(CONCURRENT_RX.match(n) for n in s109_named), s109_named
    for tag, n in ROOT_TESTS:
        assert (Path('C:/kyty/s%d' % n) / ('log_%s.txt' % tag)).is_file(), tag
    for f, text_ in TEST_LOG_MOVED:
        assert rd(SRC / f).count(text_ % OLD) == 1, f
    for f in ONE_SHOT_MOVED:
        assert "'%s/FACTS.md'" % OLD in rd(SRC / f), f
    for f, target in GAME_ONE_SHOTS:
        assert target in rd(SRC / f), f
    # Generators: under the SOURCE root each still holds its line and anchors before its only write; no anchor
    # matches its source file's carried copy any more.  make_fam108.py's anchors match only the file it was
    # run on, C:/kyty/s107/dab107.py (outside the harness).
    for f, line, source, anchor, first, write in generator_facts(SRC):
        t = rd(SRC / f)
        assert line in t and t.index(first) < t.index(write), f
        assert anchor not in rd(SRC / source), (f, anchor)
    assert "PRODUCTION_ROOT = 'C:/kyty/s107'" in rd(EXT_DAB107)
    assert "PRED = 'C:/kyty/s107/pred/02_dabatch2.md'" in rd(EXT_DAB107)
    assert "PRED = '%s/%s/01_dawalklead.md'" % (OLD, INHERITED) in rd(SRC / 'lead105.py')
    assert "PRODUCTION_ROOT = 'C:/kyty/s105'" not in rd(SRC / 'dwk104.py')
    for f, out, key in SELF_HASHED:
        j = json.loads(rd(SRC / out))
        assert j[key] == sha(SRC / f), (f, out)
        if key == 'scorer_sha256':
            assert j['scorer'] == f, (f, out)
    for f, out in SELF_HASHED_PRIOR:
        j = json.loads(rd(SRC / out))
        assert j['scorer'] == f and j['scorer_sha256'] == sha(PREV_ROOT / f) != sha(SRC / f), (f, out)
    stage = sorted(p.name for p in SRC.glob('*.py') if STAGE in rd(p) and not p.name.endswith('_port.py'))
    assert stage == sorted(STAGE_MENTIONS), stage
    real_stage = sorted(p.name for p in SRC.glob('*.py') if REAL_STAGE in rd(p) and not p.name.endswith('_port.py'))
    assert real_stage == sorted(f for f, _, _, _ in FIXTURE_TESTS), real_stage
    for f, text_ in EXPLORATORY:
        t = rd(SRC / f)
        assert text_ in t and 'pred/' not in t, f
    for f in ('fixture_gw106.py', 'fixture_dab106.py'):
        assert 'pred/' not in rd(SRC / f), f
    for f, _name, _miss in ROOT_MOVED:
        assert const(rd(SRC / f), _name) == OLD, f
    for f, text_, _miss in INLINE_ROOT_MOVED + AUDIT_INLINE_MOVED:
        assert rd(SRC / f).count(text_ % OLD) == 1, f
    for f, names_read, _root in AUDIT_READS_COPIES:
        t = rd(SRC / f)
        assert all("'%s/%s'" % (OLD, n) in t for n in names_read), f
    for f, _, target in ROADMAP_PATCHES:
        assert target in rd(SRC / f), f
    for name, root in CARRIED_SHELLS:
        assert root in rd(SRC / name), name
    assert not Path(STAGE_NEXT).exists() and not Path(STAGE).exists() and Path(REAL_STAGE).is_dir()
    print('PRECONDITIONS PASS: 5 root constructs; 52 sealed texts (50 land in prev108/pred, 2 stay '
          'in carried prev103/pred and prev100/pred); SEALS108.txt 2 texts + 5 tools; 36 live paths (25 files) + '
          '10 expression paths (8 files); gates 1092 B / 99 names (sha 303a7849..., dawalk=1, no '
          'dabatch/ctxtick/cspmemo/cspfam); gates.cpp 138 entries (111 gates + 27 knobs; dabatch default 8; '
          'cspfam last knob row, default 0); ABSENT 39')


def predicted_exists(planned):
    """Paths (lower case, '/'-separated, relative to DST) that exist once main() has written the plan."""
    keys = [key for key, _, _, _ in planned] + [LEDGER_NAME]
    keys += ['prev108/%s' % f for f in DOCS_PRESENT]
    keys += ['%s/%s' % (land, n) for _, n, _, _, land in SEALED if land == LAND]
    keys += ['pred']
    out = set()
    for k in keys:
        parts = k.split('/')
        for i in range(1, len(parts) + 1):
            out.add('/'.join(parts[:i]).lower())
    return out


def plan():
    """Walk SRC, decode and repair every file in memory; nothing is written."""
    planned, skipped = [], {}
    empty_dirs = []
    for root, dirs, files in os.walk(SRC):
        rel = Path(root).relative_to(SRC)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIR and not (rel == Path('.') and (d == 'pred' or d.startswith('design109'))))
        if not dirs and not files and rel != Path('.'):
            empty_dirs.append(rel.as_posix())
        for f in sorted(files):
            sp = Path(root) / f
            key = sp.relative_to(SRC).as_posix()
            why = skip_reason(key, f, sp, rel)
            if why is not None:
                skipped.setdefault(why, []).append(key)
                continue
            output, fired = (repair(rd(sp), key) if f.endswith('.py') else (None, []))
            planned.append((key, output, fired, sha(sp)))
    # The ledger expectations hold on the PLAN, before anything is written.
    check_ledger({key: fired for key, _, fired, _ in planned if fired}, 'preflight')
    assert not any(key == LEDGER_NAME or key in NEW_SESSION for key, _, _, _ in planned)
    assert sorted(skipped.get('audit-dump', [])) == sorted(AUDIT_DUMPS)
    assert set(BINARIES108) <= set(skipped.get('model', []))
    assert all(CONCURRENT_RX.match(k) for k in skipped.get('concurrent-109', []))
    assert skipped.get('doc', []) == list(DOCS_PRESENT)
    # Stale s108 root literals may remain only in the seven chain files (one line each) and in the archive
    # verifier r1 also splices (any folder depth; archive ports excluded).
    stale = sorted(key for key, output, _, _ in planned if output is not None
                   and not key.endswith('_port.py') and OLD in output)
    assert stale == sorted(list(COMMA) + list(TUPLES) + ['regime94.py'] + list(R1_ARCHIVE)), stale
    # The dangling-path census on the plan: exactly the classed files.
    pred = predicted_exists(planned)
    hits = census({key: output for key, output, _, _ in planned if output is not None},
                  lambda tail: tail.lower() in pred)
    check_census(hits, 'preflight')
    return planned, skipped, empty_dirs


def main():
    preconditions()
    planned, skipped, empty_dirs = plan()
    n_skipped = sum(len(v) for v in skipped.values())
    if '--plan-only' in sys.argv[1:]:
        print('PLAN ONLY: %d files would be carried (%d repaired), %d skipped (%s); census %d files; %d empty '
              'source folders not recreated; nothing written'
              % (len(planned), sum(1 for _, _, fired, _ in planned if fired), n_skipped,
                 ', '.join('%s %d' % (k, len(v)) for k, v in sorted(skipped.items())),
                 len(census_want()), len(empty_dirs)))
        return
    carried, ledger = [], {}
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
    prev = DST / 'prev108'
    (prev / 'pred').mkdir(parents=True)
    (DST / 'pred').mkdir()
    for f in DOCS:
        if (SRC / f).is_file():
            shutil.copy2(SRC / f, prev / f)
    for d, n, _, _, land in SEALED:
        if land == LAND:
            assert not (DST / LAND / n).exists(), ('landing collision', d, n)
            shutil.copy2(SRC / d / n, DST / LAND / n)
    diagnostics(carried, ledger, skipped, empty_dirs)
    payload = json.dumps({'source': OLD, 'destination': NEW, 'files': ledger,
        'carried_count': len(carried), 'skipped_count': n_skipped,
        'skipped_by_rule': {k: len(v) for k, v in sorted(skipped.items())},
        'not_carried_named': {'binaries': sorted(BINARIES108), 'audit_dumps': sorted(AUDIT_DUMPS),
                              'concurrent_109': sorted(skipped.get('concurrent-109', []))},
        'empty_source_folders': sorted(empty_dirs),
        'archive_scorers': sorted(ARCHIVE_SCORERS),
        'sealed_landing': ['%s/%s -> %s/%s' % (d, n, land, n) for d, n, _, _, land in SEALED],
        'seals108_tools': dict(sorted(SEALS108_TOOLS.items())),
        'census': {k: list(v) for k, v in sorted(census_want().items()) if k not in FACTS_MENTIONS},
        'facts_mentions': sorted(FACTS_MENTIONS),
        'one_shot': sorted(ONE_SHOT),
        'new_session_allowed': sorted(NEW_SESSION + NEW_SESSION_CARRIED)}, indent=2) + '\n'
    # Bytes with LF line ends (Path.write_text on Windows would translate every newline to CRLF).
    (DST / LEDGER_NAME).write_bytes(payload.encode('utf-8'))
    assert b'\r' not in (DST / LEDGER_NAME).read_bytes()
    print('PORT DIAGNOSTIC: clean; carried=%d ledger=%d skipped=%d' % (len(carried), len(ledger), n_skipped))


def _lit(node, env):
    """A string literal, a module-level name bound to one, or a '+' of those (anything else: ValueError)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id in env:
        return env[node.id]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _lit(node.left, env) + _lit(node.right, env)
    raise ValueError(ast.dump(node)[:80])


def roadmap_stop(name):
    """Simulate <name>'s rep() chain against the CURRENT ROADMAP, in memory only.
    Returns (index of the first anchor not found exactly once or None, number of reps)."""
    tree = ast.parse(rd(DST / name))
    env, reps = {}, []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                env[node.targets[0].id] = _lit(node.value, env)
            except ValueError:
                pass
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and \
                isinstance(node.value.func, ast.Name) and node.value.func.id == 'rep':
            a, b = node.value.args
            reps.append((_lit(a, env), _lit(b, env)))
    s = rd(ROADMAP).replace('\r\n', '\n')
    for i, (a, b) in enumerate(reps, 1):
        if s.count(a) != 1:
            return i, len(reps)
        s = s.replace(a, b)
    return None, len(reps)


def diagnostics(carried, ledger, skipped, empty_dirs):
    live = check_ledger({k: v['repairs'] for k, v in ledger.items()}, 'written')
    for tag, want in expected_ledger().items():
        print('LEDGER %s PASS: %s' % (tag, ', '.join(want)))
    ports = sorted(k for k in ledger if k.endswith('_port.py'))
    print('LEDGER r1 ARCHIVE PORTS (carried, never run): %d files: %s' % (len(ports), ', '.join(ports)))
    live = {k: ledger[k] for k in live}
    naive_regime = naive(rd(SRC / 'regime94.py'))
    blind = naive_regime.replace("'C:/kyty/s109', 'C:/kyty/s107'", "'C:/kyty/s109', 'C:/kyty/s108', 'C:/kyty/s107'")
    assert blind == naive_regime.replace(naive(regime(108)), regime(109))
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
        assert m and m.group(1) == chain(109, 75, True) and len(m.group(1).split(',')) == 35, f
    for f, (floor, _) in ARITH.items():
        assert rd(DST / f).count('range(109, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(DST / f).count(chain(109, floor)) == 1, f
    print('ADVANCE PASS: COMMA 35 roots; range(109, 70/66, -1); stg92 20, bda93 19, s94lib 18 roots; '
          'regime94 17 roots + s109')
    sealed = sealed_index()
    for f, names in REPOINT.items():
        t = rd(DST / f)
        for name in names:
            p = Path(const(t, name))
            assert p.parent == DST / LAND, (f, name, p)
            assert sha(p) == const(t, name + '_SHA') == const(rd(SRC / f), name + '_SHA')
    print('R6 PASS: %d constants in %d files -> %s (incl. fam108.PRED -> 01_cspfam.md)'
          % (sum(len(v) for v in REPOINT.values()), len(REPOINT), LAND))
    for f in PRED_BYTES_FILES:
        t = rd(DST / f)
        assert int(re.search(r'^PRED_BYTES\s*=\s*(\d+)', t, re.M).group(1)) == Path(const(t, 'PRED')).stat().st_size, f
    print('R6 BYTES PASS: PRED_BYTES of %d files equal the landed texts (fam108 6890 B)' % len(PRED_BYTES_FILES))
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
    for f, loader, override, stage in FIXTURE_TESTS:
        t = rd(DST / f)
        assert loader in t and override in t and stage in t and f not in ledger, f
        print('FIXTURE TEST, SEAL OVERRIDDEN, REPORT ONLY: %s loads the scorer named on argv, replaces PRED with a '
              'throwaway seal and writes under %s (outside the harness; not moved by the rewrite)' % (f, REAL_STAGE))
    assert len(list((DST / LAND).iterdir())) == 50
    for d, n, size, h, land in SEALED:
        p = DST / land / n
        assert p.stat().st_size == size and sha(p) == h == sha(SRC / d / n), (d, n)
        assert p.read_bytes() == (SRC / d / n).read_bytes(), (d, n)
        print('SEALED PASS: %s/%s %d B %s' % (land, n, size, h))
    for folder, want in ((INHERITED, 48), (CARRIED106, 45), (CARRIED105, 42), (CARRIED104, 38), (CARRIED103, 34),
                         (CARRIED102, 29), (CARRIED101, 20), (OLDER, 18)):
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
    dst_folders = [p for p in pred_folders(DST) if p != DST / LAND]
    assert len(dst_folders) == 28
    for n in S108_NAMES:
        assert all(not (p / n).exists() for p in dst_folders) and (DST / LAND / n).is_file(), n
    elsewhere = sorted(q.relative_to(DST).as_posix() for q in DST.rglob('*')
                       if q.name in S108_NAMES and q.parent != DST / LAND)
    assert elsewhere == [], elsewhere
    print('NO COLLISION PASS: the two session-108 basenames exist only in %s (checked against all %d earlier pred/ '
          'folders and the whole destination)' % (LAND, len(dst_folders)))
    for folder, n, size, h in DRAFT_SHARED:
        p = DST / folder / n
        assert p.stat().st_size == size and sha(p) == h != sha(DST / LAND / n), (folder, n)
        print('DRAFT SHARES A SEAL BASENAME, REPORT ONLY: %s/%s (%d B, %s...) is session 102\'s draft, not a seal '
              'folder; %s/%s is session 106\'s seal (%s...)' % (folder, n, size, h[:8], LAND, n, sha(DST / LAND / n)[:8]))
    for n, h in sorted(SEALS108_TOOLS.items()):
        same = sha(DST / n) == h
        assert same == (not n.endswith('.py')), n
        if n.endswith('.py'):
            assert rd(DST / n) != rd(SRC / n) and sha(SRC / n) == h, n
            print('SEALED TOOL REWRITTEN, REPORT ONLY: %s (SEALS108.txt %s...) - the s109 copy hashes %s... '
                  '(naive%s); the sealed original stays in %s' % (n, h[:8], sha(DST / n)[:8],
                                                                 ' + r6' if n in ledger else '', OLD))
        else:
            print('SEALED TOOL PASS: %s byte-exact (%s...)' % (n, h[:8]))
    assert not list((DST / 'pred').iterdir())
    assert all(not (DST / f).exists() for f in DOCS + NEW_SESSION)
    assert not [q for q in DST.rglob('*') if q.name in NEW_SESSION]
    for f in NEW_SESSION_CARRIED:
        assert sha(DST / f) == sha(SRC / f), f
    print('NEW SESSION NAMES PASS: none of %d session-109 names exists in %s or %s; %s is carried archive data'
          % (len(NEW_SESSION), OLD, NEW, ', '.join(NEW_SESSION_CARRIED)))
    for f in DOCS:
        if (SRC / f).is_file():
            assert sha(SRC / f) == sha(DST / 'prev108' / f)
        else:
            assert not (DST / 'prev108' / f).exists()
    assert sorted(p.name for p in (DST / 'prev108').iterdir()) == sorted(list(DOCS_PRESENT) + ['pred'])
    print('PREV108 PASS: %s + pred/ (50 texts); no README.md or PLAN.md in the source root' % ', '.join(DOCS_PRESENT))
    assert (DST / 'm31_notes.md').is_file() and sha(DST / 'm31_notes.md') == sha(SRC / 'm31_notes.md')
    assert not (DST / 'prev108' / 'm31_notes.md').exists()
    print('SESSION-105 WORKING NOTE STAYS AT ROOT, REPORT ONLY: m31_notes.md (only README/FACTS/PLAN are prev-only)')
    assert sha(DST / PREV_LEDGER) == sha(SRC / PREV_LEDGER)
    print('PREVIOUS LEDGER CARRIED AS DATA: %s byte-exact' % PREV_LEDGER)
    for record, _names, _where in SEAL_RECORDS:
        assert sha(DST / record) == sha(SRC / record), record
    print('SEAL RECORDS CARRIED AT ROOT: %s byte-exact (%s names pred/<name>; the texts are in %s)'
          % (', '.join(r for r, _, _ in SEAL_RECORDS), SEALS_FILE, LAND))
    for f in sorted(ARCHIVE_SCORERS):
        assert (DST / f).is_file(), ('archive scorer missing', f)
        # r6/r7 only repoint a sealed path; they never make an archive scorer runnable.
        assert f not in live or set(live[f]['repairs']) <= {'r6', 'r7'}, ('archive scorer entered live repair', f)
        print('ARCHIVE, DO NOT RUN: %s; carried by naive rewrite (plus r6/r7 where listed)' % f)
    for f, size, h in ARCHIVE_DATA:
        assert (DST / f).stat().st_size == size and sha(DST / f) == h, f
        print('ARCHIVE DATA, NOT A BASELINE: %s %d B %s... byte-exact' % (f, size, h[:8]))
    for f, extra in PLUS_FILES:
        assert gate_tokens(DST / f) == gate_tokens(DST / 'gates_base.txt') + list(extra), f
    print('ARCHIVE GATE FILES PASS: %s = gates_base.txt + %s' % (
        ', '.join(f for f, _ in PLUS_FILES), ' / '.join(' '.join(e) for _, e in PLUS_FILES)))
    for f, name, miss in ROOT_MOVED:
        assert const(rd(DST / f), name) == NEW and const(rd(SRC / f), name) == OLD, f
        print('ARCHIVE ROOT MOVED BY NAIVE REWRITE, REPORT ONLY: %s %s = %s (%s)' % (f, name, NEW, miss))
    for f, text_, miss in INLINE_ROOT_MOVED:
        assert rd(DST / f).count(text_ % NEW) == 1, f
        print('ARCHIVE INLINE DEFAULT ROOT MOVED BY NAIVE REWRITE, REPORT ONLY: %s defaults to %s without --root (%s)'
              % (f, NEW, miss))
    for f, text_, miss in AUDIT_INLINE_MOVED:
        assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
        print('AUDIT EVIDENCE ROOT MOVED BY NAIVE REWRITE, REPORT ONLY: %s opens %s (%s); never run'
              % (f, (text_ % NEW).split("'")[1], miss))
    for f, text_, note in AUDIT_READS_DUMPS:
        assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
        assert not list((DST / 'audit108').glob('p_*.json'))
        print('AUDIT EVIDENCE READS NON-CARRIED PARSE DUMPS, REPORT ONLY: %s reads %s/audit108/p_<tag>.json%s; the '
              'dumps stay in %s/audit108 (not carried); never run' % (f, NEW, note, OLD))
    for f in AUDIT_ARGV:
        assert rd(DST / f) == rd(SRC / f) and f not in ledger, f
        print('AUDIT PARSER, ARGV ONLY, REPORT ONLY: %s takes the log and the output on argv (it was run on the %s '
              'logs, which are not carried); byte-identical copy' % (f, OLD))
    assert rd(DST / MUTANTS_DEF) == rd(SRC / MUTANTS_DEF)
    print('AUDIT DATA, REPORT ONLY: %s (the %d-mutant table; no root literal) byte-identical' % (MUTANTS_DEF, N_MUTANTS_108))
    for f, names_read, audited in AUDIT_READS_COPIES:
        t = rd(DST / f)
        assert all("'%s/%s'" % (NEW, n) in t for n in names_read), f
        assert any(sha(DST / n) != sha(audited / n) for n in names_read)
        print('AUDIT EVIDENCE READS CARRIED COPIES, REPORT ONLY: %s names %s/{%s}, which differ from the audited '
              '%s files (naive%s); never run' % (f, NEW, ','.join(names_read), audited.as_posix(),
                                                 ' + r6' if any(n in ledger for n in names_read) else ''))
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
    for f, exe in BUILD_PINNED:
        b = const(rd(DST / f), 'BUILD_SHA')
        assert b == BINARIES108[exe] and not (DST / exe).exists() and sha(SRC / exe) == b, f
        print('ARCHIVE BUILD PIN, REPORT ONLY: %s BUILD_SHA = %s... = %s/%s (the binary stays in s108, not carried)'
              % (f, b[:8], OLD, exe))
    for n, h in sorted(BINARIES108.items()):
        assert not (DST / n).exists() and sha(SRC / n) == h, n
    print('NOT CARRIED, SCORED BINARIES, REPORT ONLY: %s stay in %s (each hashes to the sha in its name)'
          % (', '.join(sorted(BINARIES108)), OLD))
    for f, out, key in SELF_HASHED:
        j = json.loads(rd(DST / out))
        assert j[key] == sha(SRC / f) != sha(DST / f), (f, out)
        print('SELF-HASH, REPORT ONLY: %s records %s %s... = the s108 %s; the s109 copy hashes %s... (naive%s)'
              % (out, key, j[key][:8], f, sha(DST / f)[:8], ' + r6' if f in ledger else ''))
    for f, out in SELF_HASHED_PRIOR:
        j = json.loads(rd(DST / out))
        assert j['scorer_sha256'] == sha(PREV_ROOT / f) and j['scorer_sha256'] not in (sha(SRC / f), sha(DST / f)), (f, out)
        print('SELF-HASH, REPORT ONLY: %s records scorer_sha256 %s... = the ORIGINAL %s/%s; neither the s108 nor the '
              's109 copy matches' % (out, j['scorer_sha256'][:8], PREV_ROOT.as_posix(), f))
    for f, text_ in TEST_LOG_MOVED:
        assert rd(DST / f).count(text_ % NEW) == 1 and not (DST / 'log_reg104.txt').exists(), f
        print('TEST REAL-LOG PATH MOVED BY NAIVE REWRITE, REPORT ONLY: %s reads %s/log_reg104.txt (log stays in s104)'
              % (f, NEW))
    assert not list(DST.glob('log_*10[45678]*.txt'))
    for tag, n in ROOT_TESTS:
        if n == 108:
            assert (SRC / ('log_%s.txt' % tag)).is_file(), tag
    assert Path('C:/kyty/s104/log_reg104.txt').is_file()
    for f in ONE_SHOT:
        assert (DST / f).is_file() and f not in ledger, f
        moved = ' (target %s/FACTS.md after naive rewrite; anchors assert before any write)' % NEW \
            if f in ONE_SHOT_MOVED else ''
        if f in ONE_SHOT_MOVED:
            assert "'%s/FACTS.md'" % NEW in rd(DST / f), f
        print('ONE-SHOT, DO NOT RUN: %s%s' % (f, moved))
    for f, target in GAME_ONE_SHOTS:
        assert target in rd(DST / f) and f not in ledger, f
        print('ONE-SHOT, GAME-FOLDER TARGET NOT MOVED, REPORT ONLY: %s patches %s (not simulated; never run)'
              % (f, target.split("'")[1]))
    # The generators after the naive rewrite: each anchor that names its source file's text does not match the
    # carried source, and each stops there, before its only write.
    for f, line, source, anchor, first, write in generator_facts(DST):
        t = rd(DST / f)
        assert line in t and t.index(first) < t.index(write), f
        assert anchor not in rd(DST / source), (f, anchor)
    assert not (DST / 'pred' / '02_m31.md').exists() and "DST = '%s/ctx105.py'" % NEW in rd(DST / 'make_ctx105.py')
    print('ONE-SHOT GENERATOR, PRED LEFT DANGLING, REPORT ONLY: make_ctx105.py reads %s/pred/02_m31.md '
          '(absent) before it would write %s/ctx105.py; its lead105 anchor no longer matches after r6' % (NEW, NEW))
    print('ONE-SHOT GENERATOR, ANCHOR GONE, REPORT ONLY: make_gw106.py\'s first constant anchor '
          '"PRODUCTION_ROOT = \'C:/kyty/s105\'" is absent from %s/dwk104.py; it would stop before its write' % NEW)
    print('ONE-SHOT GENERATOR, ANCHOR GONE, REPORT ONLY: make_dab106.py\'s PRED anchor names '
          '%s/prev105/pred/01_dawalklead.md, but %s/lead105.py names %s/01_dawalklead.md after r6; it would stop '
          'before its write' % (NEW, NEW, LAND))
    assert "PRED = '%s/%s/02_dabatch.md'" % (NEW, LAND) in rd(DST / 'dab106.py')
    assert 'SRC, DST = sys.argv[1], sys.argv[2]' in rd(DST / 'make_dab107.py')
    print('ONE-SHOT GENERATOR, ANCHOR GONE, REPORT ONLY: make_dab107.py (source and target on argv) edits dab106.py; '
          'its first rep() anchor names %s/prev106/pred/02_dabatch.md, but %s/dab106.py names %s/02_dabatch.md after '
          'r6; it would stop (SystemExit) before its only write' % (NEW, NEW, LAND))
    assert 'SRC, DST = sys.argv[1], sys.argv[2]' in rd(DST / 'make_fam108.py')
    assert "PRODUCTION_ROOT = 'C:/kyty/s107'" in rd(EXT_DAB107)
    print('ONE-SHOT GENERATOR, WARNING, REPORT ONLY: make_fam108.py (source and target on argv) anchors on '
          '"PRODUCTION_ROOT = \'C:/kyty/s107\'" - absent from %s/dab107.py (it would stop, SystemExit, before its only '
          'write) but still present in %s, the file it was run on: a re-run on that file WOULD write a fam108.py '
          'naming %s/pred/01_cspfam.md (absent) - never run it' % (NEW, EXT_DAB107.as_posix(), NEW))
    for f, inserted, target in ROADMAP_PATCHES:
        stop, n_reps = roadmap_stop(f)
        assert target in rd(DST / f)
        if f in ('roadmap107_close.py', 'roadmap108_close.py'):
            assert '%s/%s' % (NEW, inserted) in rd(DST / f) and '%s/%s' % (OLD, inserted) not in rd(DST / f)
        if stop is None:
            print('ONE-SHOT ROADMAP PATCH, WARNING, REPORT ONLY: %s: all %d anchors still match the current '
                  'ROADMAP once; a re-run WOULD write - never run it' % (f, n_reps))
        else:
            print('ONE-SHOT ROADMAP PATCH, REPORT ONLY: %s (target C:/kyty/KytyPS5/docs/ROADMAP.md, not moved) '
                  'would stop at rep %d of %d against the current ROADMAP, before its only write; its inserted text '
                  'names %s/%s' % (f, stop, n_reps, NEW, inserted))
    for f in STAGE_MENTIONS:
        t = rd(DST / f)
        assert STAGE not in t and STAGE_NEXT + '/' in t and f not in ledger, f
    assert not Path(STAGE_NEXT).exists()
    print('STAGING FOLDER MENTION MOVED BY NAIVE REWRITE, REPORT ONLY: %s usage docstrings now name '
          '%s (absent; the real staging folder is %s)' % (', '.join(STAGE_MENTIONS), STAGE_NEXT, REAL_STAGE))
    for f, text_ in EXPLORATORY:
        t = rd(DST / f)
        assert text_ in t and 'pred/' not in t, f
        print('EXPLORATORY, NO SEAL, REPORT ONLY: %s reads %s by default (unchanged)' % (f, text_.strip("'")))
    for f in ('fixture_gw106.py', 'fixture_dab106.py'):
        assert 'pred/' not in rd(DST / f) and f not in ledger, f
        print('FIXTURE, NO SEAL PATH, REPORT ONLY: %s writes a synthetic log into the directory given on argv' % f)
    for name, root in CARRIED_SHELLS:
        assert root in rd(DST / name), ('%s no longer carries its own root' % name)
        assert sha(DST / name) == sha(SRC / name), name
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
    for mutant, scorer, n_lines in MUTANTS_107:
        a, b = rd(DST / scorer).splitlines(), rd(DST / mutant).splitlines()
        diff = [i for i, (x, y) in enumerate(zip(a, b), 1) if x != y]
        assert len(a) == len(b) and len(diff) == n_lines + 1, (mutant, diff)
        print('AUDIT MUTANT, REPORT ONLY: %s differs from the s109 %s in its %d mutated line(s) plus the PRED line '
              '(r6 reaches the scorer, not the mutant); never run' % (mutant, scorer, n_lines))
    # Session 108's audit mutants and worker copies after the port.
    fam_naive = naive(rd(SRC / 'fam108.py'))
    for name, (old, new) in sorted(mutant_table().items()):
        f = '%s/fam108_%s.py' % (MUTANT_DIR, name)
        t = rd(DST / f)
        assert f not in ledger and lf(t) == fam_naive.replace(old, new) and '\r\n' in t, f
        assert t.count("PRED = '%s/pred/01_cspfam.md'" % NEW) == 1 and const(t, 'PRODUCTION_ROOT') == NEW, f
        assert const(t, 'GATES_FILE') == NEW + '/gates_base.txt', f
    assert not (DST / 'pred' / '01_cspfam.md').exists() and (DST / LAND / '01_cspfam.md').is_file()
    print('AUDIT MUTANTS, FROZEN, PRED LEFT DANGLING BY DESIGN, REPORT ONLY: %d files %s/fam108_<name>.py (CRLF kept) = '
          'the naive s109 fam108 text with their one mutation each; bare PRED %s/pred/01_cspfam.md (absent; r6 '
          'reaches fam108.py, not the mutants), PRODUCTION_ROOT %s, GATES_FILE %s/gates_base.txt; never run'
          % (N_MUTANTS_108, MUTANT_DIR, NEW, NEW, NEW))
    test_dst = rd(DST / 'test_fam108.py')
    for i, f in enumerate(test_copy_names()):
        t = rd(DST / f)
        assert f not in ledger and '\r\n' in t, f
        assert lf(t) == test_dst.replace(TEST_BASE_108, "BASE = Path('%s/audit108/fx_w%d')" % (NEW, i)), f
        assert (DST / 'audit108' / ('fx_w%d' % i)).is_dir(), i
        assert not list((DST / 'audit108' / ('fx_w%d' % i)).rglob('log_*')), i
    print('AUDIT WORKER COPIES, REPORT ONLY: %d files %s/test_fam108_w<i>.py (CRLF kept) = the s109 test_fam108.py '
          'with BASE %s/audit108/fx_w<i> (the carried fixture outputs, without their synthetic logs, stdout and fake '
          'exe); never run' % (N_TEST_COPIES_108, MUTANT_DIR, NEW))
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
    # The dangling-path census on the written destination: the same classed files as on the plan.
    texts = {p.relative_to(DST).as_posix(): rd(p) for p in DST.rglob('*.py')}
    hits = census(texts, lambda tail: (DST / tail).exists())
    check_census(hits, 'written')
    for f in sorted(CENSUS):
        assert f not in ledger, f
        print('DANGLING BY REWRITE, CLASSED ABOVE, REPORT ONLY: %s names %s' % (f, ', '.join(
            '%s/%s' % (NEW, x) for x in CENSUS[f])))
    print('DANGLING BY REWRITE, CLASSED ABOVE, REPORT ONLY: the %d audit mutants name %s/pred/01_cspfam.md'
          % (N_MUTANTS_108, NEW))
    for f in FACTS_MENTIONS:
        assert f not in ledger, f
    print('FACTS.md MENTION MOVED BY NAIVE REWRITE, REPORT ONLY: %d files name %s/FACTS.md (the source '
          'root\'s FACTS.md is archived as prev108/FACTS.md; session 109 writes its own): %s'
          % (len(FACTS_MENTIONS), NEW, ', '.join(FACTS_MENTIONS)))
    roots = ast.literal_eval(re.search(r'^ROOTS = (.+)$', rd(DST / 's94lib.py'), re.M).group(1))
    assert roots == tuple('C:/kyty/s%d' % i for i in range(109, 91, -1))
    for tag, n in ROOT_TESTS:
        found = next((r for r in roots if (Path(r) / ('log_%s.txt' % tag)).is_file()), None)
        assert found == 'C:/kyty/s%d' % n, (tag, found)
        print('ROOT PASS: %s -> %s' % (tag, found))
    assert rd(DST / 'regime94.py').count(regime(109)) == 1
    for tag, n in ROOT_TESTS:
        if n < 93:
            continue
        found = next((r for r in roots[:-1] if (Path(r) / ('log_%s.txt' % tag)).is_file()), NEW)
        assert found == 'C:/kyty/s%d' % n
    assert next((r for r in roots[:-1] if (Path(r) / 'log_nosuch109.txt').is_file()), NEW) == NEW
    stale = []
    for p in DST.rglob('*.py'):
        if p.name.endswith('_port.py'):
            continue
        t = rd(p)
        assert 'C:\\kyty\\s108' not in t and 'C:\\\\kyty\\\\s108' not in t and '/c/kyty/s108' not in t, p
        hits_ = [i for i, line in enumerate(t.splitlines(), 1) if OLD in line]
        if hits_:
            stale.append(p.relative_to(DST).as_posix())
            assert len(hits_) == 1, (p.name, hits_)
    assert sorted(stale) == sorted(list(COMMA) + list(TUPLES) + ['regime94.py'] + list(R1_ARCHIVE)), stale
    print('STALE %s PASS: only in the chain files (%s) and the archive verifier %s, one line each'
          % (OLD, ', '.join(sorted(list(COMMA) + list(TUPLES) + ['regime94.py'])), R1_ARCHIVE[0]))
    leaked = [p.relative_to(DST).as_posix() for p in DST.rglob('*') if p.is_file() and
              (p.name.startswith(('log_', 'stdout_', 'rec_')) or p.name.endswith(SKIP_EXT) or p.stat().st_size >= BIG
               or AUDIT_DUMP_RX.match(p.relative_to(DST).as_posix()) or CONCURRENT_RX.match(p.name))]
    assert not leaked, leaked
    big_in_dirs = sorted(k for k in skipped.get('model', []) if '/' in k and (SRC / k).stat().st_size >= BIG
                         and not k.split('/')[-1].startswith(SKIP_PREFIX) and not k.endswith(SKIP_EXT))
    print('SKIPPED >= 5 MiB INSIDE CARRIED FOLDERS (not log/stdout/rec/binary), REPORT ONLY: %d files: %s'
          % (len(big_in_dirs), ', '.join(big_in_dirs)))
    print('NOT CARRIED, AUDIT PARSE DUMPS, REPORT ONLY: %s stay in %s' % (', '.join(AUDIT_DUMPS), OLD))
    print('NOT CARRIED, SESSION-109 FILES THE CONCURRENT EXECUTOR WROTE INTO THE SOURCE ROOT, REPORT ONLY: %s'
          % (', '.join(skipped.get('concurrent-109', [])) or 'none'))
    print('EMPTY SOURCE FOLDERS NOT RECREATED, REPORT ONLY: %s' % (', '.join(sorted(empty_dirs)) or 'none'))
    g = DST / 'gates_base.txt'
    assert sha(g) == GATES_SHA and g.stat().st_size == 1092 and g.read_bytes() == (SRC / 'gates_base.txt').read_bytes()
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
