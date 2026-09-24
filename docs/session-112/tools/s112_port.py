"""Fresh source-side s111 -> s112 harness port; never run a carried *_port.py.

Written in the SOURCE folder (C:/kyty/s111) as docs/next-session-112.md 1 requires, modelled on
C:/kyty/s110/s111_port.py (sha256 060f9348...).  Only Python root literals change globally.  Five root
constructs, the live sealed-path repair of bare quoted literals (r6: now 37 files / 48 constants) and the
repair of sealed paths written as ROOT/Path expressions (r7: still 10 expression paths in 8 files) are
recorded separately in the ledger.  No scorer, game, build or GPU work is run.  The destination must not
exist.  New session documents/scorers belong to their authors; inherited session documents are archived
under prev111 only.

    python C:/kyty/s111/s112_port.py [--plan-only]

--plan-only runs every precondition and the whole in-memory plan (including the preflight ledger and the
dangling-path census) and writes nothing.

Advances over s111_port.py, each asserted in preconditions():
  * COMMA chain 37 -> 38 roots (s112 ... s75); r1 splices s111 back in.
  * area_verdict.py range(112, 70, -1); shift91.py range(112, 66, -1).
  * s94lib.py 21 roots, bda93.py 22, stg92.py 23; regime94.py 20 roots + s112.
  * SEALED grows 62 -> 67 (the five session-111 seals pred/01_obs111.md, 02_vds111.md, 02b_vds111b.md, 03_shp111.md
    and the audit addendum 04_audit111.md, each checked against SEALS111.txt).  65 land in prev111/pred; two stay where
    the walk carries them (the two older audit addenda, as before).  No session-111 basename is taken anywhere in the
    source outside its pred/ (all 31 earlier pred/ folders and every other directory, re-verified below).
  * SEALS111.txt pins 5 texts (pred/ prefix) and 21 TOOLS (no prefix); three of the tools (check111.py,
    make_check111.py, go111v.sh) carry the trailing note '(post-run: published after go111v, audit MINOR-3)', which
    seal_record() now parses and returns separately.  The SEALS111 tools match the source byte for byte; eight SEALS110
    .py tools were rewritten by the 111 port (the sealed originals stay in C:/kyty/s110), as were nine SEALS109 and three
    SEALS108 .py tools by earlier ports.
  * r6 grows 33 -> 37 files and 44 -> 48 constants: the PRED of obs111.py, vds111.py, vds111b.py and shp111.py (each a
    BARE quoted literal 'C:/kyty/s111/pred/<seal>' with PRED_SHA and PRED_BYTES, checked against SEALS111.txt).  The
    thirty-three inherited r6 files now read from s111/prev110/pred.  check111.py names no seal.
  * r7 unchanged in count: 10 expression paths in 8 files, all now reading s111/prev110/pred.  No session-111 file
    writes a seal as an expression.
  * gates_base.txt unchanged: 1092 B / 99 names, sha256 303a7849... (dawalk=1); gates_base.json unchanged
    (3343 B, 2b79c3cf...).  None of dabatch, ctxtick, cspmemo, cspfam, cspfree, daslot, daguard is in gates_base.txt.
  * gates.cpp 141 entries (111 gates + 30 knobs), asserted on the tree AS IT IS when the port runs: session 111 shipped
    the knob daslot with default 1 (0..2), and the concurrent session-112 executor appended the knob daguard
    (KYTY_DRAW_AHEAD_GUARD, default 1, 0..1) as the LAST row of KNOB_DEFINITIONS while this port was written (the
    brief's rule: +1 entry, +1 ABSENT).  ABSENT 41 -> 42.
  * Session-111 gate files: gates_obs111.txt (+ plkstat=1), gates_slot1.txt (+ daslot=1), gates_slot2.txt
    (+ daslot=2 smemocheck=1: the appended smemocheck=1 is IGNORED by the loader, which takes the first assignment -
    session 111's vds111 defect) are gates_base.txt plus appended tokens; gates_slot2b.txt replaces the base's
    smemocheck=0 IN PLACE and appends daslot=2.  All four are archive data, pinned by SEALS111.txt.
  * Session-111 tools: scorers obs111.py / vds111.py / vds111b.py / shp111.py (pinned to their seals and builds; logs
    stay in s111), their fixture suites test_obs111.py (HERE-relative: fixtures under <its dir>/fx/<stem>),
    test_vds111.py / test_vds111b.py (staging fixture folders) and test_shp111.py (CONSTANTS table and a synthetic line
    name the root), plus check111.py (the vid111 video check, BUILD_SHA 0c8a13f2) are archive; make_shp111.py (pinned
    staging source), make_vds111b.py (staging derive) and make_check111.py (reads C:/kyty/s110/check110.py, writes
    <root>/check111.py) are one-shot generators; mut_obs111.py is a HERE-relative mutation script (byte-identical);
    mut_shp111.py mutates the staging scorer and three of its sealed-constant mutants name the root (moved by the
    rewrite); go111.sh, go111b.sh, go111v.sh are carried shells.  audit111/ is carried and classed file by file,
    except its parse dumps audit111/*.pkl (next-session-112.md 1: not carried).  None is ever re-run.  seal111.py,
    close111.py and patch_s111.py are NOT in the source: asserted absent, nothing to class.
  * NEW_SESSION names the session-112 files the executor places later; none may exist in SRC or arrive in DST.

Changes of SHAPE, forced by the sources:
  * The inherited seals now live in ELEVEN carried folders.  prev110/pred holds 60 texts (every text an inherited
    live constant names); prev109/pred holds 56, all byte-identical twins of prev110/pred texts; prev108/pred 50;
    prev107/pred 48; prev106/pred 45; prev105/pred 42; prev104/pred 38; prev103/pred 34, thirty-three twins plus
    session 103's 04_audit_addendum.md; prev102/pred 29; prev101/pred 20; prev100/pred 18, seventeen twins plus
    session 100's 03_audit_addendum.md.
  * Session docs archived under prev111/ only: FACTS.md (README.md, PLAN.md absent; design109.md stays archived in the
    carried prev109/).
  * Not carried (they stay in C:/kyty/s111): the scored binaries kyty_emulator_*.exe (.exe, as before; the session-111
    builds c8235c90 and 0c8a13f2 and any session-112 build the concurrent executor copies in), the session-111 audit's
    parse dumps audit111/*.pkl (next-session-112.md 1; nine files, 0.1-7.4 MB), the run logs/stdout/videos (model
    rules; .map included) and any session-112 build log build_s112*.log the concurrent executor writes into the SOURCE
    root.  The source holds no fx_* fixture folder (the 111 port left the session-108 audit's audit108/fx_w* in s110).
  * The session-110 texts moved out of the source's pred/ into prev110/pred, so every session-110 file that named
    <root>/pred/<seal110> (the 110 generators, mut_shp110.py, test_shp110.py, close110.py, the twenty audit110 mutants)
    names a path absent in the source too and drops out of the dangling census, which only flags paths that exist in
    the source; likewise the nineteen audit108 worker copies (their fx_w<i> stayed in s110).
  * Session-111 files the naive s111 -> s112 rewrite breaks are classed explicitly: the twenty audit mutants
    audit111/mut/<name>/{shp111,vds111b}.py (CRLF, frozen evidence; bare pred literal left dangling) and the eight
    vds mutants' test copies, the seven frozen rerun copies audit111/rerun/*.py (their PRED / CONSTANTS name the root),
    the audit readers of the NON-carried dumps (abba.py and five sys.path importers), the parser (it would write a dump
    into s112/audit111), the log readers (runsum.py, clocks_arm.py, allfields.py, recount_misc.py), the mutant runner
    (it would rebuild the mutants from the s112 rerun copies), make_shp111.py (its staging pin still holds: a re-run
    WOULD overwrite the staging scorer mut_shp111.py mutates - WARNING), make_vds111b.py (stops), make_check111.py (a
    re-run WOULD rewrite s112/check111.py - checked for byte identity), mut_shp111.py (stops at its first root-named
    anchor), test_obs111.py / test_shp111.py (their CONSTANTS tables name the root), check111.py and the four scorers
    (roots moved).
  * The ledger is written as bytes with LF line ends.
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
SRC = Path('C:/kyty/s111')
DST = Path('C:/kyty/s112')
OLD, NEW = SRC.as_posix(), DST.as_posix()
PREV_OLD = 'C:/kyty/s110'  # the previous port's source root (session-110 originals were rewritten from it)
ROOT110 = Path('C:/kyty/s110')  # session-110 outputs' tool hashes, SEALS110 originals, session-110 binaries
ROOT109 = Path('C:/kyty/s109')  # session-109 outputs' tool hashes, SEALS109 originals, session-109 binaries
ROOT108 = Path('C:/kyty/s108')  # session-108 outputs' tool hashes, SEALS108 originals, session-108 binaries
ROOT107 = Path('C:/kyty/s107')  # session-107 outputs' scorer hashes
PREV106_ROOT = Path('C:/kyty/s106')  # the root session 106's audit read its scorers from
EXT_DAB107 = Path('C:/kyty/s107/dab107.py')  # the file make_fam108.py was run on (outside the harness)
REAL_STAGE = 'C:/kyty/s106_stage'
STAGE_ENT109 = Path('C:/kyty/s106_stage/ent109.py')  # the file make_ent109b.py derives from (outside the harness)
# Session-110 generator sources and mutation targets in the staging folder (outside the harness).
STAGE_ENT109B = Path('C:/kyty/s106_stage/ent109b.py')            # make_stl110.py (sha pinned)
STAGE_TEST_ENT109B = Path('C:/kyty/s106_stage/test_ent109b.py')  # make_test_stl110.py (sha pinned)
STAGE_STL110 = Path('C:/kyty/s106_stage/stl110.py')              # make_stl110b.py, first derive (sha pinned)
STAGE_FRF109 = Path('C:/kyty/s106_stage/frf109/frf109.py')       # make_shp110.py (sha pinned)
STAGE_SHP110 = Path('C:/kyty/s106_stage/shp110/shp110.py')       # mut_shp110.py's scorer; make_shp111.py's source
# Session-111 generator sources and mutation targets in the staging folder (outside the harness).
STAGE_SHP111 = Path('C:/kyty/s106_stage/shp111/shp111.py')       # mut_shp111.py's scorer; make_shp111.py's target
STAGE_VDS111 = Path('C:/kyty/s106_stage/vds111.py')              # make_vds111b.py, first derive
STAGE_TEST_VDS111 = Path('C:/kyty/s106_stage/test_vds111.py')    # make_vds111b.py, second derive
CHECK110_ORIG = Path('C:/kyty/s110/check110.py')                 # make_check111.py's source (the s110 original)
GATES = Path('C:/kyty/KytyPS5/src/common/gates.cpp')
ROADMAP = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
NEXT110 = Path('C:/kyty/KytyPS5/docs/next-session-110.md')  # ctx109.py's first target
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
FREE0_SHA = '274b01211407d36d311de998c61c91e63749d8d2de750d354b175d04e53e6a03'  # gates_base + cspfree=0
FREE1_SHA = 'e18dcf71e79392b0cad3eef33a7b9ced018999587f8c26779b3360d3658583d6'  # gates_base + cspfree=1
FREE2_SHA = '0d982f81104ca66f8df9592a0757b49ddd883d8de93e1f120e1b5487a1e66d10'  # gates_base + cspfree=2
OBS111_SHA = '9974ad5a436b65e9f529b7bf3861bf600cd980aae31e4cd58861d51d38880203'  # gates_base + plkstat=1
SLOT1_SHA = 'ca29a9e3b4587da8ca52041ed428821fe36c37c5f9dc935a2ecf0625472caea2'   # gates_base + daslot=1
SLOT2_SHA = 'e6f15ff7ee81f2eccb30de8a8e2d19c77cb650047bfb39724cc54765a88653fc'   # gates_base + daslot=2 smemocheck=1
SLOT2B_SHA = 'ad4e72e650889dac2ce39ca47942bcd8796d85b259a740d72096157f155ef7f8'  # smemocheck=1 in place + daslot=2
# Archive data (sessions 104..111): carried byte-exact, never a baseline.  Session 111 added four gate files (its
# obs111 run, the vds111/vds111b verify runs and the shp111 ABBA arm 1 / vss111 video).
ARCHIVE_DATA = (('gates_base.pre104ship.txt', 1092, PRESHIP_SHA),
                ('gates_base.pre104ship.json', 3581, '6d256a31d8e817103bf3db2b2af19c89597ebddf9dc7a94678809caa122f2a5b'),
                ('gates_dawalk1.txt', 1493, 'cdc6568e7a347a7e834c11372e5f30eae2ae91f6f52bbec57d6e0aa51cfa0e7e'),
                ('gates_nodawalk.txt', 1082, '0931a79a8f1f6de21a81a8876d68d68d713f87bd5ddf20319f520228577c4f3b'),
                ('gates_ctx1.txt', 1102, CTX1_SHA),
                ('gates_ctx2.txt', 1102, CTX2_SHA),
                ('gates_dab8.txt', 1102, DAB8_SHA),
                ('gates_obs.txt', 1112, OBS_SHA),
                ('gates_dab2.txt', 1102, DAB2_SHA),
                ('gates_fam4.txt', 1101, FAM4_SHA),
                ('gates_fam0.txt', 1101, FAM0_SHA),
                ('gates_free0.txt', 1102, FREE0_SHA),
                ('gates_free1.txt', 1102, FREE1_SHA),
                ('gates_free2.txt', 1102, FREE2_SHA),
                ('gates_obs111.txt', 1102, OBS111_SHA),
                ('gates_slot1.txt', 1101, SLOT1_SHA),
                ('gates_slot2.txt', 1114, SLOT2_SHA),
                ('gates_slot2b.txt', 1101, SLOT2B_SHA))
# Archive gate files that are gates_base.txt plus appended tokens, one line, the single trailing CRLF kept.
PLUS_FILES = (('gates_ctx1.txt', ('ctxtick=1',)), ('gates_ctx2.txt', ('ctxtick=2',)),
              ('gates_dab8.txt', ('dabatch=8',)), ('gates_obs.txt', ('plkstat=1', 'cspmemo=3')),
              ('gates_dab2.txt', ('dabatch=2',)), ('gates_fam4.txt', ('cspfam=4',)),
              ('gates_fam0.txt', ('cspfam=0',)), ('gates_free0.txt', ('cspfree=0',)),
              ('gates_free1.txt', ('cspfree=1',)), ('gates_free2.txt', ('cspfree=2',)),
              ('gates_obs111.txt', ('plkstat=1',)), ('gates_slot1.txt', ('daslot=1',)),
              # the appended smemocheck=1 is IGNORED by the loader (first assignment wins): session 111's vds111 defect
              ('gates_slot2.txt', ('daslot=2', 'smemocheck=1')))
# Archive gate files that replace a base assignment IN PLACE and append tokens: (file, in-place (old, new) tokens,
# appended tokens).  Session 111's vds111b fix.
IN_PLACE_FILES = (('gates_slot2b.txt', (('smemocheck=0', 'smemocheck=1'),), ('daslot=2',)),)
# The tree AS IT IS when the port runs: session 111's daslot (default 1 since session 111's ship), then the concurrent
# session-112 executor's knob daguard (KYTY_DRAW_AHEAD_GUARD, default 1, 0..1), appended as the LAST row of
# KNOB_DEFINITIONS while this port was written - +1 entry, +1 ABSENT (the brief's rule for a new knob row appended last
# before the port).
GATES_CPP_ENTRIES = 141  # 99 pinned in gates_base.txt + 42 ABSENT
GATES_CPP_SPLIT = (111, 30)  # DEFINITIONS rows, KNOB_DEFINITIONS rows
DABATCH_ROW = '{"KYTY_DRAW_AHEAD_BATCH", "dabatch", 8, 65536}'  # session 106 shipped default 8 (was 64)
CTXTICK_ROW = '{"KYTY_CTX_TICK", "ctxtick", 1, 3}'
CSPMEMO_ROW = '{"KYTY_CS_PREFETCH_MEMO", "cspmemo", 0, 3}'
CSPFAM_ROW = '{"KYTY_CS_PREFETCH_FAMILY", "cspfam", 0, 1024}'
CSPFREE_ROW = '{"KYTY_CS_PREFETCH_FREE", "cspfree", 1, 2}'  # session 110 (0776f6a): default 1
DASLOT_ROW = '{"KYTY_DRAW_AHEAD_SLOT", "daslot", 1, 2}'  # session 111: default now 1 (was 0)
DAGUARD_ROW = '{"KYTY_DRAW_AHEAD_GUARD", "daguard", 1, 1}'  # session 112 (concurrent executor), LAST knob row
BIG = 5 * 1024 * 1024
SKIP_PREFIX = ('log_', 'stdout_', 'rec_', 'a80z_', 'hfx_')
SKIP_EXT = ('.mp4', '.idx', '.pyc', '.map', '.etl', '.exe')
SKIP_DIR = {'__pycache__', 'video99_comparison', 'video99_preview', 'video99_full',
            'video99_base_full'}
# next-session-112.md 1: fixture folders fx_* are not carried (any depth).  The source holds none (asserted).
FIXTURE_DIRS = ()
# next-session-112.md 1: the session-111 audit's parse dumps audit111/*.pkl are not carried (they stay in s111).
AUDIT111_PKL_RX = re.compile(r'^audit111/[^/]+\.pkl$')
AUDIT111_DUMPS = tuple('audit111/%s.pkl' % t for t in ('allfields_shp110_shp111', 'obs111', 'shp110', 'shp111', 'vds111',
                                                        'vds111b', 'vid110', 'vid111', 'vss111'))
# Session-112 build logs a concurrent session-112 executor may write into the SOURCE root: never carried (a session-112
# artifact, possibly still growing); they stay in s111.
CONCURRENT_RX = re.compile(r'^build_s112[a-z0-9]*\.log$')
# Scored binaries of session 111 (kept in s111, skipped as .exe): the scorers' build.
BINARIES111 = {'kyty_emulator_c8235c90.exe': 'c8235c902e08d00782d0cff23528361d194a501ad1899344ca8302c742372a86'}
# check111.py's build (the vid111 video, daslot default 1): in the source root, skipped as .exe.
BUILD111 = ('check111.py', 'kyty_emulator_0c8a13f2.exe',
            '0c8a13f28245ea879c25725ebf4258a944308d24f7c6c11fd4bee95ec3814c8c')
# Scored binaries of session 110 (the scorers' build and check110's build, which obs111.py is pinned to as well):
# never carried; they stay in C:/kyty/s110.
BINARIES110 = {'kyty_emulator_b3f7a2c9.exe': 'b3f7a2c957dd344bfd140fe6d04eb2b95ac9387d01dabf5b7dde42b6765b6a82',
               'kyty_emulator_072861c8.exe': '072861c89193c3726232e44e78be4f36172254af826394b56c8bf671ef609c21'}
BUILD110 = ('check110.py', 'kyty_emulator_072861c8.exe',
            '072861c89193c3726232e44e78be4f36172254af826394b56c8bf671ef609c21')
# Scored binaries of sessions 109 and 108: never carried; they stay in C:/kyty/s109 and C:/kyty/s108.
BINARIES109 = {'kyty_emulator_2f593229.exe': '2f5932296d564b1098831b75a7fc6c8796d3a9ac7e871ea0c3a1c6b0610a4b77',
               'kyty_emulator_e90f5543.exe': 'e90f55438d95b3b673cde11275965f9ec8a342db40dd4063c4ea8d6836443d40'}
BINARIES108 = {'kyty_emulator_fd1d0bd7.exe': 'fd1d0bd7f68280e97680bc68dfe56fdf57a134429a49bc9223ece6254b7b1e72',
               'kyty_emulator_fc78c564.exe': 'fc78c56417815a0ebdea1c5a5aa94306720c3307d07a6feadf3c8e37f43aae43',
               'kyty_emulator_379777bb.exe': '379777bba4271847b1b805c403944e4a6552acd0aac0b5cd3af12be36c489107'}
# Root documents archived under prev111/ only (never at the destination root).
DOCS = ('README.md', 'FACTS.md', 'PLAN.md')
DOCS_PRESENT = ('FACTS.md',)  # session 111 wrote no README.md and no PLAN.md at its root
DESIGN109 = 'prev109/design109.md'  # archived by the 110 port; stays in the carried prev109/
# Names a session-112 author may create (port brief, docs/next-session-112.md 3: the verify run vdg112, the ABBA
# net112, the video check); none may exist in SRC or arrive in DST.
NEW_SESSION = ('vdg112.py', 'make_vdg112.py', 'test_vdg112.py', 'mut_vdg112.py',
               'net112.py', 'make_net112.py', 'test_net112.py', 'mut_net112.py',
               'check112.py', 'make_check112.py', 'test_check112.py', 'SEALS112.txt',
               'go112.sh', 'go112b.sh', 'go112c.sh', 'go112v.sh',
               'gates_vdg112.txt', 'gates_net112.txt', 'gates_guard0.txt', 'gates_slot0.txt')
LEDGER_NAME = 'port112_ledger.json'
PREV_LEDGER = 'port111_ledger.json'  # the previous port's ledger: carried as plain data (LF)
PREV_LEDGERS_DATA = ('port110_ledger.json', 'port109_ledger.json', 'port108_ledger.json')  # older ledgers: plain data
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
          # Session 105, knob KYTY_CTX_TICK (default 1, 0..3), the 37th.
          'ctxtick',
          # Session 107, knob KYTY_CS_PREFETCH_MEMO (default 0, 0..3), the 38th.
          'cspmemo',
          # Session 108, knob KYTY_CS_PREFETCH_FAMILY (default 0, 0..1024), the 39th (v2 since session 109).
          'cspfam',
          # Session 109, knob KYTY_CS_PREFETCH_FREE (0..2): the 40th (default 1 since session 110).
          'cspfree',
          # Session 111, knob KYTY_DRAW_AHEAD_SLOT (0..2): the 41st (default 1 since session 111's ship).
          'daslot',
          # Session 112 (concurrent executor), knob KYTY_DRAW_AHEAD_GUARD (default 1, 0..1), LAST row of
          # KNOB_DEFINITIONS: the 42nd.
          'daguard')
LAND = 'prev111/pred'
INHERITED = 'prev110/pred'
CARRIED109 = 'prev109/pred'
CARRIED108 = 'prev108/pred'
CARRIED107 = 'prev107/pred'
CARRIED106 = 'prev106/pred'
CARRIED105 = 'prev105/pred'
CARRIED104 = 'prev104/pred'
CARRIED103 = 'prev103/pred'
CARRIED102 = 'prev102/pred'
CARRIED101 = 'prev101/pred'
OLDER = 'prev100/pred'
CARRIED = (INHERITED, CARRIED109, CARRIED108, CARRIED107, CARRIED106, CARRIED105, CARRIED104, CARRIED103,
           CARRIED102, CARRIED101, OLDER)
# (source folder in SRC, name, bytes, sha256, landing folder in DST)
SEALED = (
    # Sessions 96..101 (twenty texts; prev108..prev101/pred hold byte-identical twins).
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
    # Session 102 (nine texts, as in SEALS102.txt); prev109..prev102/pred.
    (INHERITED, '01_m5_bench.md', 14288, 'cf3c353f7aaa4a2a16d7b59a61461cf26bef11ddbfffd59206ae95a8b6b33e0a', LAND),
    (INHERITED, '02_m5_addendum.md', 8007, 'ced6d4103c64b9e5b7c81a3a730cac6d2b04a08486f82cf43642b04a8701f4d3', LAND),
    (INHERITED, '03_dabatch.md', 6909, 'f828e2578a1e68e2dbf99e976be7ce49f4041e6631d96c4773f0d23642b6135e', LAND),
    (INHERITED, '04_checkpoints_fix.md', 4221, 'c131852e4b3a5c979ce93d2c4182849b641bcc53ce1f217373926de369e8fe87', LAND),
    (INHERITED, '05_dabatch_addendum.md', 2347, 'b889c57a6f8c0f56eaa3ac43f68e9ea168dfef32b4a7122cb0b918fee5e7686d', LAND),
    (INHERITED, '06_ckpt_entry_addendum.md', 1595, '7562c26f1b7d6432eef3bf5ff4c4d3a4d1901d4a351ff0c74961e735cb6434ab', LAND),
    (INHERITED, '07_m5_capture_retry.md', 1870, '55aabe82e9c347a6d5e92bb7b7f7f327d632e5b045877e9237794850ca63c3b8', LAND),
    (INHERITED, '08_audit_addendum.md', 6464, 'ee7e3397609f31ec96a307aed53f0daa9362909b1bcb7ec4f2e383cdc2d8385f', LAND),
    (INHERITED, '09_audit_tally_addendum.md', 2029, 'e205aeb6a3d815dbb5c30f8cc9f5aab8259b59b4a9660d17fd03b258923679f4', LAND),
    # Session 103 (five texts, as in SEALS103.txt).  Four are in prev109/pred and land again.
    (INHERITED, '01_bvh_cap_series.md', 5057, '788f679c0676e47714e154aca86a3336e3f31274d7492113d0a1f8b11c071541', LAND),
    (INHERITED, '02_m5p_bench.md', 6183, '4035a9b0cc6ae89a671706a12731b3e0f21f29c2caa90763f61c0fab4b688a67', LAND),
    (INHERITED, '03_m5p_addendum.md', 1435, '73a7be0d895979b9d458e44c9251ad48d2be9d94c5f6b03d28d7d290b49bb894', LAND),
    (INHERITED, '05_claims_addendum.md', 2141, '7b313d96fefe9379eee5816ca824f94d6000cb4be055b3ae13c72fd19f31a607', LAND),
    # Session 103's four-lens audit addendum.  Its basename is taken in prev104..prev110/pred by session
    # 104's addendum; it stays in the carried prev103/pred.  No live constant names it.
    (CARRIED103, '04_audit_addendum.md', 4345, 'cdc9bab4e9f9ab4d2088a740dcb82c1a0c95a0032e44db23a3007f0e97ec45b0', CARRIED103),
    # Session 100's addendum, which WITHDREW the CLOSE of its pred/02.  Its basename is taken in
    # prev101..prev110/pred by session 101's addendum; it stays in the carried prev100/pred.
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
    # Session 107 (three texts, as in SEALS107.txt).
    (INHERITED, '01_obs107.md', 3138, '85a65121dce86e65c442becf2f5859ef4c215f1848ad4439902e616872ac1db6', LAND),
    (INHERITED, '02_dabatch2.md', 3077, '3a0d4043e983cda2f9ae19aff4da1ad7cb15861639fe95bd921c6fb61c1027bb', LAND),
    (INHERITED, '03_audit107.md', 4542, '7b6a65316ca562c3a4bda33037b02d1b755c2e7ddfc2616624bb82636158f969', LAND),
    # Session 108 (two texts, as in SEALS108.txt).
    (INHERITED, '01_cspfam.md', 6890, 'a40cf056d83fd2ed5b31b1c84e1674f0968803ad481d8831213617c623caa945', LAND),
    (INHERITED, '02_audit108.md', 4989, '401a76cc9a69d02e7eca10b57d801a3bc0b3e1e85fd8bc0cd59e5679c1fdb885', LAND),
    # Session 109 (six texts, as in SEALS109.txt); now in prev109/pred.
    (INHERITED, '01_ent109.md', 4222, 'e2627de0052fedd22db9e3910d77b1fd7b4f4c51815ba80f11b8f3bec76e52b0', LAND),
    (INHERITED, '01b_vfy109.md', 2743, 'f626da410e534afb858e7c95b8a41ee152690870ad572123575dcdc04d133768', LAND),
    (INHERITED, '02_ent109b.md', 2242, 'bf8adcd190075de4699c27b11bae8fdb9804577fa05c3fbf9c9c55a9f371f1a6', LAND),
    (INHERITED, '03_frf109.md', 3778, '8f44107fa1367c2bab64025ef6d025a70ef4654d1b74786eda7d283fee60f310', LAND),
    (INHERITED, '04_frm109.md', 2550, '50fbc61b0915169059258d34d119c72deec58043b47c6276bc7b52dd993bd864', LAND),
    (INHERITED, '05_audit109.md', 4827, 'fd27a2f8787cf2bf58b71c852a8d8c4ee791b8d38c6aee311b5315cf6acb0b1b', LAND),
    # Session 110 (four texts, as in SEALS110.txt); now in prev110/pred.  01 seals stl110.py, 02 stl110b.py,
    # 03 shp110.py; 04 is the audit addendum.
    (INHERITED, '01_stl110.md', 3961, 'e20551068e7cd70e20141980f58bde06e03445316992a6c26421916a1e42c11f', LAND),
    (INHERITED, '02_stl110b.md', 2978, '0299b403a1744560199b046f4ed6d53df1108089f52b3d687c64d90d043cc198', LAND),
    (INHERITED, '03_shp110.md', 3385, '4f02d2848cbcd87202a9dbb525fbef8adf8f315610be21a39e008d67b3a66103', LAND),
    (INHERITED, '04_audit110.md', 4150, '983b97edb0502c20a2d7b29aec007cd132c3a046a88deefeff63555e4fb8ac2d', LAND),
    # Session 111 (five texts, as in SEALS111.txt).  pred/01 seals obs111.py, 02 vds111.py, 02b vds111b.py,
    # 03 shp111.py; 04 is the audit addendum.
    ('pred', '01_obs111.md', 2952, '985318280ea6c461abb25acfbf171ce98b28873677ee0c39c808c6bf54e1272d', LAND),
    ('pred', '02_vds111.md', 2809, '0dadb4f7f5c57adc9db0e484a66285c1ed0ce162120eb7fb9651b8f50a7f7994', LAND),
    ('pred', '02b_vds111b.md', 3491, 'a404307329c32b3489cd8d9c4950a0823f0e9f3b8dcbcb60a08776f57e541e39', LAND),
    ('pred', '03_shp111.md', 3604, '594e2402c8022dcd0a71ab111cb58f355400b51a261600a48c74eea044125f3f', LAND),
    ('pred', '04_audit111.md', 4162, '83358a9c83f43874e6aef4030be2d063f179d9e78618ac826e04c695c856461c', LAND),
)
N_SEALED = 67
N_LAND = 65
SEALS_FILE = 'SEALS111.txt'
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
S109_NAMES = ('01_ent109.md', '01b_vfy109.md', '02_ent109b.md', '03_frf109.md', '04_frm109.md', '05_audit109.md')
S110_NAMES = ('01_stl110.md', '02_stl110b.md', '03_shp110.md', '04_audit110.md')
S111_NAMES = ('01_obs111.md', '02_vds111.md', '02b_vds111b.md', '03_shp111.md', '04_audit111.md')
# Every session's own seal record, re-read against SEALED: (record, names, folder of each text).
SEAL_RECORDS = (('SEALS111.txt', S111_NAMES, {}),
                ('SEALS110.txt', S110_NAMES, {}),
                ('SEALS109.txt', S109_NAMES, {}),
                ('SEALS108.txt', S108_NAMES, {}),
                ('SEALS107.txt', S107_NAMES, {}),
                ('SEALS106.txt', S106_NAMES, {}),
                ('SEALS105.txt', S105_NAMES, {}),
                ('SEALS104.txt', S104_NAMES, {}),
                ('SEALS103.txt', S103_NAMES, {'04_audit_addendum.md': CARRIED103}),
                ('SEALS102.txt', S102_NAMES, {}))
# SEALS108.txt pins five TOOLS (entries without the pred/ prefix): name -> sha256 at seal time.  Its three .py tools
# were rewritten by the 109 port (the sealed originals stay in C:/kyty/s108).
SEALS108_TOOLS = {'gates_fam4.txt': FAM4_SHA,
                  'fam108.py': '550d1517191a87dd49de46123fbcb547842744d801720ce7ae47c0545a73cbab',
                  'make_fam108.py': 'b1683b4849212b1a80457d2da8fa0a942e255d4bbff8ff675cd230362f66b215',
                  'test_fam108.py': 'efe01310b399033de8eba25c4fa8504a8476d9b84e610e3960f2bfc0fead4a89',
                  'go108.sh': '5404c59bb21ecfbe3a936a75ca0f55e4a4e56f17e48be82a77e9b8a089da8705'}
SEALS108_REWRITTEN = ('fam108.py', 'make_fam108.py', 'test_fam108.py')
# SEALS109.txt pins twenty TOOLS; the 110 port rewrote nine .py tools (the sealed originals stay in C:/kyty/s109).
SEALS109_TOOLS = {'ent109.py': '96a6fa4e89f4b6ca191c06f70acca772c55960f6a317551587b6190a081d564e',
                  'test_ent109.py': '630e197ae006a1dfb25792b09355a88178f01bde6901374822f158a9c1a21d4c',
                  'go109.sh': 'b331e01b8fd69747f64d6827d48f0d8654a50726d4182dc810918d580cfba047',
                  'gates_fam0.txt': FAM0_SHA,
                  'gates_fam4.txt': FAM4_SHA,
                  'vfy109.py': '44af344b3d9479e70a5e3603356bae861b77ed4d00961301f91adf2b8a367c34',
                  'test_vfy109.py': '884d2f33ba18226897d19d6dde2feda21ea755b66e86f0a0d5f12af139e0b6f7',
                  'ent109b.py': '98903f77cdec3dda8dab07b1860b97dd21cd7b45dd5f3d0d5e8a5f7b6cc5f3f0',
                  'make_ent109b.py': '90bc29ccef65ac657bdd3e5de4df9a17515761b8767fa19624f1468fa47d312f',
                  'test_ent109b.py': '4b97143d43257ff91aebd2d1b5690421d6909f33e53b15dc1eb732f7c36f4545',
                  'frf109.py': 'a9a93a53d5ba3b4868bc6e54418fbd8abfc4cf6cd764bc7f698501d69d7db6d3',
                  'make_frf109.py': 'b2bab5d48240fe42571d21167cb7deadb7460cbfb5cfe50675e2bae3fe2ad365',
                  'test_frf109.py': '9d209c366600d24ef2d0cd7913467abbe25ee13403e8ad1a59c1447067117f59',
                  'go109b.sh': '66a608535d84ee18f8c4fd795de173a8909719e9baa4a5beaff1d8cbd04f5832',
                  'gates_free0.txt': FREE0_SHA,
                  'gates_free1.txt': FREE1_SHA,
                  'gates_free2.txt': FREE2_SHA,
                  'frm109.py': '0cc20d511bbaac9f66eff7a228020d5a7a7009153403adcdedde643c492a0e18',
                  'make_frm109.py': '156dc5238b991e68ab5a8ea3445d0137be69914f884300e48f02afc37ec231de',
                  'go109c.sh': 'a5de47c40e027107e0eae02108511fb25eb48a34825d6a88f96cf04a0f6fb22b'}
SEALS109_REWRITTEN = ('ent109.py', 'vfy109.py', 'ent109b.py', 'make_ent109b.py', 'frf109.py', 'make_frf109.py',
                      'test_frf109.py', 'frm109.py', 'make_frm109.py')
# SEALS110.txt pins eighteen TOOLS; the 111 port rewrote eight .py tools (the sealed originals stay in C:/kyty/s110).
SEALS110_TOOLS = {'stl110.py': 'a04a7abf7ea4e0fb07ea4ddac590e35903defcce8c2ebc372a35c579304870ad',
                  'make_stl110.py': '94486c7ac8a3bd8be56aa21f6df45f6acf6eec1d4a61869ded427661a83f76a8',
                  'test_stl110.py': 'e48b06acff06f9741211a3caf0a382f58472c0c72e6d4c5498dd5c8f4ca6d0cf',
                  'make_test_stl110.py': 'eb5ae3208b659d292a7386becaca16b1ec66871e7a7425d79c6e12cd04bec183',
                  'mut_stl110.py': '389741239609fd13ba42a0cddf8b4c19879c26b4dd08b7b0b032564ed9db8908',
                  'go110.sh': '8fbd7053a704da4d12d4a002bbe04bcd6aca622348e45b4ef6f12c0b7e63be2f',
                  'gates_free0.txt': FREE0_SHA,
                  'gates_free1.txt': FREE1_SHA,
                  'stl110b.py': '83f3236f43ab2581e968d6f0b89b18620dadc817036e9ae339c571841c027cb6',
                  'make_stl110b.py': 'f396608a79b24186b7070a23a8b213d27d938c26d37512122e0b3c8a5336b271',
                  'test_stl110b.py': 'd681bfa18f837fd0fa93d43dfdfef69312851b32f95dbcb72f243a726ffc8ec3',
                  'mut_stl110b.py': 'f2e7f523140f165cb8d86023474f9c9eb54616187fae476acd3470da771c8c7e',
                  'go110b.sh': 'b187000d6d2535e6681b86be4201e13c731b87fae58ca8d56ccd1339aaca8e83',
                  'shp110.py': '5d30402b3a77fb2a393d233f7fec5ea43caf9d44adbf15f6d72c0aaf456aa3a5',
                  'make_shp110.py': '6246d0869121aef92718eca83c33fa114b6ef36dbfd08ebd884e8d49ae44c9ae',
                  'test_shp110.py': '8e99510d066f67d5c6ca759af6097109971cb73afa51a081a09c4bf1d633d589',
                  'mut_shp110.py': '1566bc13b4b2d40450cb366797c2ff498701861124862b6c7259f7ea375a0208',
                  'go110c.sh': '2e912c0f0915c7f74405d0a6495ad31997fc0fea96bb618403d1f03aa533bbc7'}
SEALS110_REWRITTEN = ('stl110.py', 'make_stl110.py', 'stl110b.py', 'make_stl110b.py', 'shp110.py', 'make_shp110.py',
                      'test_shp110.py', 'mut_shp110.py')
# SEALS111.txt pins twenty-one TOOLS; every one matches the source byte for byte.  The last three carry the trailing
# note POSTRUN_NOTE (published after go111v, audit MINOR-3).
SEALS111_TOOLS = {'obs111.py': '927b1721763964a49ba66f7f38bf6747af63e74f053177af91aa0c67ddd58a29',
                  'test_obs111.py': '7b8a7a7392f1e4b4e65cd3c8ad1433fa6eece635ba421b1728d039bf46bf89a0',
                  'mut_obs111.py': '4ee544720586b609954eb0dfc1090c93d33bede1bb6ee974e669631bd9d37a58',
                  'vds111.py': 'a8718039955cfc6a34665bf1a72afd07fb0f7c13c5f7d1076566e97f204c6b94',
                  'test_vds111.py': '2d5065813075da9286224f240ab033ae75dad5111c97727a4275b579c033e359',
                  'gates_obs111.txt': OBS111_SHA,
                  'gates_slot1.txt': SLOT1_SHA,
                  'gates_slot2.txt': SLOT2_SHA,
                  'shp111.py': '79dd24e60a3d93d44aa87a43b54eeac1f57de415bd8871746e4614ad934b248f',
                  'make_shp111.py': '8b9bd9a352e0d7fef1e77258a55a8f302985f1793baac9d52b00ed3f4a41700b',
                  'test_shp111.py': '4b0b7aebc81e33b314a615ebe95a742f3d8a4c012ae38d01008729423688b370',
                  'mut_shp111.py': 'afd6147e4592124e00d44f109c699c1b54b694066ef672fc2dc125e88de551b2',
                  'go111.sh': 'b702dc73ac8a2f8738e955f69591cd50f8c879bc5509e7ae5738b82bcd8fd966',
                  'vds111b.py': 'd106af506acf0bb8aafb94111babfacc9445bd5d010d664b0610cd3e82661232',
                  'test_vds111b.py': 'b73afd64f4e0267da50afd429b050de20c1dadf23d10b1dea6fb637ec042d18a',
                  'make_vds111b.py': '31a7ee194c70133e0889d7bed3751988114a1ad760dce4a4f78902cf35a3382a',
                  'go111b.sh': '5d48ce368d649a4054c207523eb1fadf887cd30dec9dff9212ddf804bfe53195',
                  'gates_slot2b.txt': SLOT2B_SHA,
                  'check111.py': '1f740594faaebf6a18373e691e241409ca68790e0b36de0c7d409a16bc9fe2c7',
                  'make_check111.py': '2a0c3aa7898731650d77c38419ef48bfdcdf6dc0e0cd4ae6ec5aa2d6edab1285',
                  'go111v.sh': 'cd45141879a36d1b1c6119cd6af6529870827c3e50ddc5d68f8e710744f35fa7'}
POSTRUN_NOTE = '(post-run: published after go111v, audit MINOR-3)'
SEALS111_POSTRUN = ('check111.py', 'make_check111.py', 'go111v.sh')
TOOL_RECORDS = {'SEALS108.txt': SEALS108_TOOLS, 'SEALS109.txt': SEALS109_TOOLS, 'SEALS110.txt': SEALS110_TOOLS,
                'SEALS111.txt': SEALS111_TOOLS}
# Records whose tool lines may carry a trailing note: {record: {tool: note}}.
TOOL_NOTES = {'SEALS111.txt': {n: POSTRUN_NOTE for n in SEALS111_POSTRUN}}
# Where each record's sealed originals live, and which of its tools earlier ports already rewrote in the source.
RECORD_ROOT = {'SEALS108.txt': ROOT108, 'SEALS109.txt': ROOT109, 'SEALS110.txt': ROOT110, 'SEALS111.txt': SRC}
RECORD_REWRITTEN = {'SEALS108.txt': SEALS108_REWRITTEN, 'SEALS109.txt': SEALS109_REWRITTEN,
                    'SEALS110.txt': SEALS110_REWRITTEN, 'SEALS111.txt': ()}
# Session 101's texts that prev100/pred never held (prev101/pred holds all twenty sessions 96..101 texts).
PREV101_ONLY = ('01_two_directional.md', '02_regime_addendum.md', '03_audit_addendum.md')
# A draft folder (not a seal folder, never a landing) whose one basename equals a session-106 seal's:
# session 102's draft of its dabatch pre-registration.  (folder, name, bytes, sha256)
DRAFT_SHARED = (('pred_drafts', '02_dabatch.md', 6486, '4b85efd047af1a0ccfaa00fa3a38b61fe8d06dd43b12117f9ab125692e1f8f2d'),)
# r6: scorers whose PRED* (and m5_102.py's ADDENDUM) are bare quoted literals const() can read.
# Thirty-three point into s111/prev110/pred, the four session-111 scorers into s111/pred; all land in s112/prev111/pred.
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
    'fam108.py': ('PRED',),
    'ent109.py': ('PRED',), 'vfy109.py': ('PRED',), 'ent109b.py': ('PRED',),
    'frf109.py': ('PRED',), 'frm109.py': ('PRED',),
    'stl110.py': ('PRED',), 'stl110b.py': ('PRED',), 'shp110.py': ('PRED',),
    # Session 111 (next-session-112.md 1): bare literals with PRED_SHA / PRED_BYTES.
    'obs111.py': ('PRED',), 'vds111.py': ('PRED',), 'vds111b.py': ('PRED',), 'shp111.py': ('PRED',),
}
REPOINT_FOLDER = {'obs111.py': 'pred', 'vds111.py': 'pred', 'vds111b.py': 'pred', 'shp111.py': 'pred'}  # default INHERITED
N_R6_FILES, N_R6_CONSTS = 37, 48
# r6 files that also pin PRED_BYTES (checked against the landed text after the port).
PRED_BYTES_FILES = ('a104.py', 'cen100.py', 'ckpt102.py', 'cm101.py', 'ctx105.py', 'dab102.py', 'dab106.py',
                    'dab107.py', 'dwk104.py', 'fam108.py', 'gw106.py', 'lead105.py', 'mov100.py', 'obs107.py',
                    'ent109.py', 'vfy109.py', 'ent109b.py', 'frf109.py', 'frm109.py',
                    'stl110.py', 'stl110b.py', 'shp110.py',
                    'obs111.py', 'vds111.py', 'vds111b.py', 'shp111.py')
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
# Fixtures of sessions 107..111: they load the scorer named on argv, replace its PRED with a throwaway seal
# and write their synthetic logs under the staging folder C:/kyty/s106_stage (outside the harness; the naive
# rewrite does not touch it).  (file, loader text, override text, staging text)
FIXTURE_TESTS = (('test_obs107.py', "spec_from_file_location('obs107', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_obs')"),
                 ('test_dab107.py', "spec_from_file_location('dab107', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_dab107')"),
                 ('test_fam108.py', "spec_from_file_location('fam108', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_fam108')"),
                 ('test_ent109.py', "spec_from_file_location('ent109', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_ent109')"),
                 ('test_vfy109.py', "spec_from_file_location('vfy109', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_vfy109')"),
                 ('test_ent109b.py', "spec_from_file_location('ent109b', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_ent109b')"),
                 # Session 110: the stl110/stl110b fixtures (no root literal at all).
                 ('test_stl110.py', "spec_from_file_location('stl110', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_stl110')"),
                 ('test_stl110b.py', "spec_from_file_location('stl110b', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_stl110b')"),
                 # Session 111: the vds111/vds111b fixtures (no root literal at all).
                 ('test_vds111.py', "spec_from_file_location('vds111', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_vds111')"),
                 ('test_vds111b.py', "spec_from_file_location('vds111b', SRC)", 'mod.PRED = str(seal)',
                  "BASE = Path('C:/kyty/s106_stage/fx_vds111b')"))
# Session 109's frf109 fixtures: the same pattern, the fixture folder optional on argv, plus one synthetic log line
# that names the root (moved by the naive rewrite; it is fixture data, compared by the scorer's regex only).
FIXTURE_TEST_FRF = ('test_frf109.py', "spec_from_file_location('frf109', SRC)", 'mod.PRED = str(seal)',
                    "else Path('C:/kyty/s106_stage/fx_frf109')", "'Recording: %s/rec_frf109.mp4 960x540'")
# Session 110's shp110 fixtures: the frf109 pattern, plus a CONSTANTS table that names the root three times (report
# line; on the sealed copy it already read CONSTANTS DIFFER by design, PRED_SHA pinned).  (file, loader, override,
# stage, synthetic line with %s = root, constants texts with %s = root)
FIXTURE_TEST_SHP = ('test_shp110.py', "spec_from_file_location('shp110', SRC)", 'mod.PRED = str(seal)',
                    "else Path('C:/kyty/s106_stage/fx_shp110')", "'Recording: %s/rec_shp110.mp4 960x540'",
                    ("want = {'PRODUCTION_ROOT': '%s', 'PRED': '%s/pred/03_shp110.md', 'PRED_SHA': None,",
                     "'GATES_FILE': '%s/gates_base.txt',"))
# Session 111's shp111 fixtures: the shp110 pattern (CONSTANTS table naming the root three times, a synthetic line, and
# a docstring mention), plus a gates_base.txt fallback that names C:/kyty/s110 (unchanged by the rewrite).
FIXTURE_TEST_SHP111 = ('test_shp111.py', "spec_from_file_location('shp111', SRC)", 'mod.PRED = str(seal)',
                       "else Path('C:/kyty/s106_stage/shp111/fx')", "'Recording: %s/rec_shp111.mp4 960x540'",
                       ("want = {'PRODUCTION_ROOT': '%s', 'PRED': '%s/pred/03_shp111.md', 'PRED_SHA': None,",
                        "'GATES_FILE': '%s/gates_base.txt',"),
                       "else Path('C:/kyty/s110/gates_base.txt')", 5)
# Session 111's obs111 fixtures: HERE-relative (scorer default <its dir>/obs111.py, fixtures under <its dir>/fx/<stem>,
# removed at the end), a CONSTANTS check naming the root three times and two fixture env values naming it (one in the
# escaped-backslash form).  (file, loader, override, base, constants texts with %s = root, env texts with %s = root in
# forward-slash form / escaped-backslash form)
FIXTURE_TEST_OBS111 = ('test_obs111.py', "spec_from_file_location('obs111_under_test', SRC)", 'mod.PRED = str(seal)',
                       "BASE = HERE / 'fx' / SRC.stem",
                       ("mod.PRODUCTION_ROOT == '%s'", "and mod.PRED == '%s/pred/01_obs111.md'",
                        "and mod.GATES_FILE == '%s/gates_obs111.txt'"),
                       ("dict(env={'KYTY_REC': '%s/rec.mp4'})", "'KYTY_GATE_FILE': '%s\\\\gates.req'"))
# Mutation scripts of sessions 109..110: they mutate the C:/kyty/s106_stage copies and write there; no root literal.
MUTATION_SCRIPTS = ('mut_ent109.py', 'mut_ent109b.py', 'mut_frf109.py', 'mut_stl110.py', 'mut_stl110b.py')
# Session 111's mut_obs111.py: HERE-relative (mutates <its dir>/obs111.py into <its dir>/mutants and runs <its
# dir>/test_obs111.py; fixture folders <its dir>/fx/<stem>); no root literal.  (file, texts)
MUTATION_HERE = ('mut_obs111.py', ("HERE = Path(__file__).resolve().parent",
                                   "SCORER = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'obs111.py'",
                                   "MUT_DIR = HERE / 'mutants'"))
# Session 110's mut_shp110.py: its scorer is the staging copy; three sealed-constant mutants anchor on root texts.
# (file, scorer line, mutant anchors with %s = root)
MUTATION_SHP = ('mut_shp110.py', "HERE = Path('C:/kyty/s106_stage/shp110')",
                ("mutant('CONST_root_s109', \"PRODUCTION_ROOT = '%s'\"",
                 "mutant('CONST_pred_frf109', \"PRED = '%s/pred/03_shp110.md'\"",
                 "mutant('CONST_gates_s109', \"GATES_FILE = '%s/gates_base.txt'\""))
# Session 111's mut_shp111.py: the same shape (scorer = the staging copy C:/kyty/s106_stage/shp111/shp111.py).
MUTATION_SHP111 = ('mut_shp111.py', "HERE = Path('C:/kyty/s106_stage/shp111')",
                   ("mutant('CONST_root_s110', \"PRODUCTION_ROOT = '%s'\"",
                    "mutant('CONST_pred_shp110', \"PRED = '%s/pred/03_shp111.md'\"",
                    "mutant('CONST_gates_s110', \"GATES_FILE = '%s/gates_base.txt'\""))
# Session-110 generators (one-shots) that derive from pinned staging copies.
GENERATORS_110 = ('make_stl110.py', 'make_test_stl110.py', 'make_stl110b.py', 'make_shp110.py')
# Session-111 generators (one-shots): make_shp111.py (pinned staging source, staging target), make_vds111b.py (staging
# derive, no pin) and make_check111.py (reads C:/kyty/s110/check110.py, writes <root>/check111.py).
GENERATORS_111 = ('make_shp111.py', 'make_vds111b.py', 'make_check111.py')
# Every top-level file that names the real staging folder (checked as a set).
STAGE_READERS = tuple(f for f, _, _, _ in FIXTURE_TESTS) + (FIXTURE_TEST_FRF[0], FIXTURE_TEST_SHP[0],
                                                            FIXTURE_TEST_SHP111[0]) + \
    MUTATION_SCRIPTS + (MUTATION_SHP[0], MUTATION_SHP111[0]) + ('make_ent109b.py', 'make_frf109.py') + \
    GENERATORS_110 + ('make_shp111.py', 'make_vds111b.py')
# Scorers/tools whose seal path is a Path()/ROOT-relative expression, not the bare quoted literal
# const() can read (port repair 7).  It rewrites the relative part only, so the shape of each
# line, any trailing comment and its neighbouring hash constant (if any) are untouched.
# (file, constant, source form, repaired form, sealed basename, sealed folder in SRC, hash constant)
REPOINT2 = (
    ('bf99.py', 'PRED', "PRED = Path('%s/prev110/pred/01_bindings_only.md')",
     "PRED = Path('%s/prev111/pred/01_bindings_only.md')", '01_bindings_only.md', INHERITED, 'PRED_SHA'),
    ('settled99.py', 'PRED', "PRED = ROOT / 'prev110/pred/02_settled_bindings.md'",
     "PRED = ROOT / 'prev111/pred/02_settled_bindings.md'", '02_settled_bindings.md', INHERITED, 'PRED_SHA'),
    ('settled99_gc.py', 'PRED', "PRED = ROOT / 'prev110/pred/04_gc_audit.md'",
     "PRED = ROOT / 'prev111/pred/04_gc_audit.md'", '04_gc_audit.md', INHERITED, 'PRED_SHA'),
    ('settled99_norec.py', 'PRED', "PRED = ROOT / 'prev110/pred/05_observer_separation.md'",
     "PRED = ROOT / 'prev111/pred/05_observer_separation.md'", '05_observer_separation.md', INHERITED, 'PRED_SHA'),
    ('m5_recompile.py', 'PRED', "PRED = ROOT + '/prev110/pred/01_m5_bench.md'",
     "PRED = ROOT + '/prev111/pred/01_m5_bench.md'", '01_m5_bench.md', INHERITED, None),
    ('bvh103.py', 'PRED', "PRED = ROOT + '/prev110/pred/01_bvh_cap_series.md'",
     "PRED = ROOT + '/prev111/pred/01_bvh_cap_series.md'", '01_bvh_cap_series.md', INHERITED, None),
    ('m5p_103.py', 'PRED', "PRED = ROOT + '/prev110/pred/02_m5p_bench.md'",
     "PRED = ROOT + '/prev111/pred/02_m5p_bench.md'", '02_m5p_bench.md', INHERITED, 'PRED_SHA'),
    ('m5p_103.py', 'PARENT01', "PARENT01 = ROOT + '/prev110/pred/01_m5_bench.md'",
     "PARENT01 = ROOT + '/prev111/pred/01_m5_bench.md'", '01_m5_bench.md', INHERITED, 'PARENT01_SHA'),
    ('m5p_103.py', 'PARENT02', "PARENT02 = ROOT + '/prev110/pred/02_m5_addendum.md'",
     "PARENT02 = ROOT + '/prev111/pred/02_m5_addendum.md'", '02_m5_addendum.md', INHERITED, 'PARENT02_SHA'),
    ('check105.py', 'PRED', "PRED = ROOT + '/prev110/pred/02_m31.md'",
     "PRED = ROOT + '/prev111/pred/02_m31.md'", '02_m31.md', INHERITED, None),
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
                   'fam108.py', 'test_fam108.py', 'check108.py', 'check108r.py',
                   'ent109.py', 'vfy109.py', 'ent109b.py', 'frf109.py', 'frm109.py',
                   'test_ent109.py', 'test_vfy109.py', 'test_ent109b.py', 'test_frf109.py',
                   # Session 110 (next-session-111.md 1): the three scorers, pinned to their seals and build (logs
                   # stay in s110), their three fixture suites (scorer on argv, seal overridden) and the video check.
                   'stl110.py', 'stl110b.py', 'shp110.py', 'test_stl110.py', 'test_stl110b.py', 'test_shp110.py',
                   'check110.py',
                   # Session 111 (next-session-112.md 1): the four scorers, pinned to their seals and builds (logs stay
                   # in s111), their four fixture suites (seal overridden) and the video check.
                   'obs111.py', 'vds111.py', 'vds111b.py', 'shp111.py', 'test_obs111.py', 'test_vds111.py',
                   'test_vds111b.py', 'test_shp111.py', 'check111.py'}
# Archive tools whose run root the naive rewrite moves to s112, where none of their inputs live.
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
              ('fam108.py', 'PRODUCTION_ROOT', 'log_fam108.txt (in s108)'),
              ('check108.py', 'ROOT', 'log_vid108.txt (in s108); vid108.json and vid108_glitch.txt are carried'),
              ('check108r.py', 'ROOT', 'log_vid108r.txt (in s108); vid108r.json and vid108r_glitch.txt are carried'),
              ('ent109.py', 'ROOT', 'log_ent109_1..8.txt (in s109)'),
              ('vfy109.py', 'ROOT', 'log_vfy109.txt (in s109)'),
              ('ent109b.py', 'ROOT', 'log_ent109b_1..8.txt (in s109)'),
              ('frf109.py', 'PRODUCTION_ROOT', 'log_frf109.txt (never produced: frf109 was not run)'),
              ('frm109.py', 'PRODUCTION_ROOT', 'log_frm109.txt (in s109)'),
              # Session 110 (next-session-111.md 1): the three scorers and the video check (logs stay in s110).
              ('stl110.py', 'ROOT', 'log_stl110_1..8.txt (in s110)'),
              ('stl110b.py', 'ROOT', 'log_stl110b_1..8.txt (in s110)'),
              ('shp110.py', 'PRODUCTION_ROOT', 'log_shp110.txt (in s110)'),
              ('check110.py', 'ROOT', 'log_vid110.txt (in s110); vid110.json and vid110_glitch.txt are carried'),
              # Session 111 (next-session-112.md 1): the four scorers and the video check (logs stay in s111).
              ('obs111.py', 'PRODUCTION_ROOT', 'log_obs111.txt (in s111); gates_obs111.txt is carried'),
              ('vds111.py', 'ROOT', 'log_vds111.txt (in s111)'),
              ('vds111b.py', 'ROOT', 'log_vds111b.txt (in s111)'),
              ('shp111.py', 'PRODUCTION_ROOT', 'log_shp111.txt, log_vss111.txt (in s111)'),
              ('check111.py', 'ROOT', 'log_vid111.txt (in s111); vid111.json and vid111_glitch.txt are carried'))
# Scorers whose default run root is an inline literal (not a module constant): obs107.py's main() and its
# audit mutant.  (file, text with %s = root, what it would miss)
INLINE_ROOT_MOVED = (('obs107.py', "if '--root' in sys.argv else '%s'", 'log_obs107.txt (in s107)'),
                     ('audit107/obs107_mutPIN.py', "if '--root' in sys.argv else '%s'",
                      'log_obs107.txt (in s107); audit mutant, never run'))
# check110.py and check111.py also put their root on sys.path (for run_safety99, carried): (file, text with %s = root)
SYS_PATHS = (('check110.py', "sys.path.insert(0, '%s')"), ('check111.py', "sys.path.insert(0, '%s')"))
# Audit evidence that opens a log by a root literal: session 106's inline opens and session 107's LOG
# constants; session 109's rp_reasons.py (its frm109 root; the fam108 root names s108 and is unchanged).
# (file, text with %s = root, what it would miss)
AUDIT_INLINE_MOVED = (('audit106/recount_protocol/drop_pairs.py', "open('%s/log_dab106.txt', 'rb')",
                       'log_dab106.txt (in s106)'),
                      ('audit106/recount_protocol/qcall.py', "open('%s/log_%%s.txt' %% t, 'rb')",
                       'log_vdb106.txt, log_vid106.txt (in s106)'),
                      ('audit107/recount_dab.py', "LOG = '%s/log_dab107.txt'", 'log_dab107.txt (in s107)'),
                      ('audit107/recount_obs.py', "LOG = '%s/log_obs107.txt'", 'log_obs107.txt (in s107)'),
                      ('audit107/dab_mech.py', "LOG = '%s/log_dab107.txt'", 'log_dab107.txt (in s107)'),
                      ('audit109/rp_reasons.py', "(('frm109', '%s'), ('fam108', 'C:/kyty/s108'))",
                       'log_frm109.txt (in s109); pairs_*.pkl are carried'))
# Audit evidence that reads parse dumps that are NOT carried: session 108's p_<tag>.json (never carried past s108)
# and session 109's audit109/parsed/<tag>.pkl (never carried past s109).  (file, text with %s = root, note)
AUDIT_READS_DUMPS = (('audit108/guards108.py', "open('%s/audit108/p_%%s.json' %% tag)",
                      ' (the dumps stay in C:/kyty/s108/audit108)'),
                     ('audit108/profile108.py', "'%s/audit108/p_%%s.json' %% TAG",
                      ' (default; a path on argv wins; the dumps stay in C:/kyty/s108/audit108)'),
                     ('audit108/recount108.py', "open('%s/audit108/p_%%s.json' %% TAG)",
                      ' (the dumps stay in C:/kyty/s108/audit108); it would also overwrite the carried '
                      'audit108/recount108.json'),
                     ('audit109/allfields.py', "open('%s/audit109/parsed/%%s.pkl' %% tag, 'rb')",
                      ' (the dumps stay in C:/kyty/s109/audit109/parsed)'),
                     ('audit109/load_phase.py', "P = '%s/audit109/parsed/%%s.pkl'",
                      ' (the dumps stay in C:/kyty/s109/audit109/parsed)'),
                     ('audit109/recount_ent.py', "P = Path('%s/audit109/parsed')",
                      ' (the dumps stay in C:/kyty/s109/audit109/parsed); it would also overwrite the carried '
                      'audit109/recount_ent.json'),
                     ('audit109/recount_frm.py', "open('%s/audit109/parsed/%%s.pkl' %% tag, 'rb')",
                      ' (the dumps stay in C:/kyty/s109/audit109/parsed); it would also overwrite the carried '
                      'audit109/recount_<tag>.json and pairs_<tag>.pkl'))
# Session-109 audit parser (CRLF): reads the logs (not carried) and writes the dumps.  (file, texts with %s = root)
AUDIT_PARSER_109 = ('audit109/parse_log.py', ("root = Path(sys.argv[2] if len(sys.argv) > 2 else '%s')",
                                              "out_dir = Path('%s/audit109/parsed')"))
# Session-109 audit protocol check: reads gates_*.txt and <tag>.json (carried) and stdout_<tag>.txt (NOT carried).
AUDIT_PROTOCOL_109 = ('audit109/protocol_checks.py', "R = Path('%s')")
# Session-109 audit mutant runner: builds 30 mutants of the scorers in R into R/audit109/mut and runs the tests
# in R on them.  (file, root text, mutant folder)
AUDIT_MUTRUN_109 = ('audit109/newmut.py', "R = Path('%s')", 'audit109/mut')
# Session-109 audit helpers with no root literal (argv only or C:/kyty-wide): byte-identical copies.
AUDIT_PLAIN_109 = ('audit109/show.py', 'audit109/srch.py', 'audit109/mtime_scan.py')
# Session-108 audit parser: log and output both on argv, no root literal.
AUDIT_ARGV = ('audit108/parse108.py',)
# Session-108 mutant table: data only (no root literal); mutants108.py holds an identical copy.
MUTANTS_DEF = 'audit108/mutants_def.py'
# Audit evidence that reads the scorers and fixtures it audited by path; after the naive rewrite it names the
# s112 copies, which differ from the audited files (naive + r6).  (file, names read, root audited)
AUDIT_READS_COPIES = (('audit106/recount_protocol/fields_cov.py',
                       ('gw106.py', 'fixture_gw106.py', 'dab106.py', 'fixture_dab106.py'), PREV106_ROOT),
                      ('audit108/mutants108.py', ('fam108.py', 'test_fam108.py'), ROOT108),
                      ('audit108/mutants108p.py', ('fam108.py', 'test_fam108.py'), ROOT108))
# ---- Session 110's audit (audit110/), classed file by file -------------------------------------------------------
# Readers of the carried parse dumps audit110/<tag>.pkl (all under 5 MB, carried): abba_stats.py opens them by a root
# literal; eight helpers put <root>/audit110 on sys.path and import abba_stats.  After the rewrite they read the s112
# copies (byte-identical).  (file, text with %s = root)
AUDIT110_DUMP_READERS = (('audit110/abba_stats.py', "pickle.load(open('%s/audit110/%%s.pkl'%%tag,'rb'))"),) + \
    tuple(('audit110/%s.py' % n, "sys.path.insert(0,'%s/audit110')")
          for n in ('dist', 'estimators', 'hetero', 'hitches', 'levels', 'profile', 'robust', 'windows'))
# Reader of the carried clock CSVs (cpuclk_/gpuclk_shp110.csv at the root; frm109's in C:/kyty/s109, unchanged).
AUDIT110_CLOCKS = ('audit110/clocks.py', "(('shp110','%s/'),('frm109','C:/kyty/s109/'))")
# Parser: the log on argv, the dump written to <root>/audit110/<tag>.pkl (it would overwrite a carried dump).
AUDIT110_PARSER = ('audit110/parse_abba.py', "pickle.dump((rows,gates),open('%s/audit110/%%s.pkl'%%tag,'wb'))")
# Readers of the NON-carried logs: parse_stall.py (log_<tag>.txt; writes <root>/audit110/stall_parse.json, the
# carried copy) and protocol.py (log_/stdout_<tag>.txt and <root>/pred/0N_*.md, absent in s112).
AUDIT110_LOG_READERS = (('audit110/parse_stall.py', ("R='%s/'", "json.dump(out,open('%s/audit110/stall_parse.json','w'),indent=1)"),
                         'log_<tag>.txt (in s110); it would also overwrite the carried audit110/stall_parse.json'),
                        ('audit110/protocol.py', ("R='%s/'",),
                         "log_/stdout_<tag>.txt (in s110) and R+'pred/0N_*.md' (absent in s112: the session-110 seals "
                         "are in prev111/pred) - FileNotFoundError at its first hash"))
# Mutant runner: builds twenty mutants of <root>/stl110b.py and <root>/shp110.py into <root>/audit110/mut/<name>/ and
# runs <root>/test_*.py on them.  (file, texts with %s = root, mutant folder)
AUDIT110_MUTRUN = ('audit110/newmut.py', ("A='%s/audit110/mut/'", "src=Path('%s/'+scorer).read_text(encoding='utf-8')",
                                          "p=subprocess.run([sys.executable,'%s/'+test,d+scorer]"), 'audit110/mut')
# Helpers with no root literal (argv only, the session transcript or C:/kyty-wide): byte-identical copies.
AUDIT110_PLAIN = ('audit110/mtime_scan.py', 'audit110/transcript_order.py', 'audit110/transcript_scan.py')
# The twenty mutants: (table in newmut.py, scorer, test).
AUDIT110_TABLES = (('STL', 'stl110b.py', 'test_stl110b.py'), ('SHP', 'shp110.py', 'test_shp110.py'))
MUTANT_DIR_110 = 'audit110/mut'
N_MUTANTS_110 = 20
# The eight carried parse dumps of the session-110 audit.
AUDIT110_DUMPS = tuple('audit110/%s.pkl' % t for t in ('dab106', 'dab107', 'dwk104', 'fam108', 'frm109', 'shp110',
                                                        'vid110', 'vsh110'))
# ---- Session 111's audit (audit111/), classed file by file -------------------------------------------------------
# Readers of the parse dumps audit111/<tag>.pkl, which are NOT carried (next-session-112.md 1): abba.py opens them by a
# root literal; five helpers put <root>/audit111 on sys.path and import abba.  After the rewrite they would look in
# s112/audit111, where no dump exists (the dumps stay in C:/kyty/s111/audit111).  (file, text with %s = root)
AUDIT111_DUMP_READERS = (('audit111/abba.py', "pickle.load(open('%s/audit111/%%s.pkl' %% tag, 'rb'))"),) + \
    tuple(('audit111/%s.py' % n, "sys.path.insert(0, '%s/audit111')")
          for n in ('allfields', 'between', 'recount_misc', 'recount_shp', 'robust'))
# Two of those also read other NON-carried inputs by root literals: allfields.py (the shp111 log; it writes its dump
# <root>/audit111/allfields_<A>_<B>.pkl) and recount_misc.py (stdout_<tag>.txt and rec_vid111.mp4.idx; its vid111.json
# and the two glitch reports are carried).  (file, texts with %s = root, note)
AUDIT111_EXTRA_READS = (('audit111/allfields.py',
                         ("LOGS = {'shp111': '%s/log_shp111.txt', 'shp110': 'C:/kyty/s110/log_shp110.txt'}",
                          "pickle.dump(res, open('%s/audit111/allfields_%%s_%%s.pkl' %% (tA, tB), 'wb'))"),
                         'log_shp111.txt (in s111; the shp110 log stays in s110) and would write a dump into '
                         's112/audit111'),
                        ('audit111/recount_misc.py',
                         ("stdout_marks('%s/stdout_%%s.txt' %% tag)", "open('%s/rec_vid111.mp4.idx', 'rb')",
                          "json.load(open('%s/vid111.json'))"),
                         'stdout_<tag>.txt and rec_vid111.mp4.idx (in s111; vid111.json and the glitch reports are '
                         'carried)'))
# Parser: the log on argv, the dump written to <root>/audit111/<tag>.pkl (s112/audit111 holds none).
AUDIT111_PARSER = ('audit111/parse.py', "pickle.dump(P, open('%s/audit111/%%s.pkl' %% tag, 'wb'))")
# Readers of the NON-carried logs by root literals: runsum.py (the six session-111 logs; the two session-110 logs name
# s110 and are unchanged) and clocks_arm.py (log_<tag>.txt; its <tag>.json and clock CSVs are carried).
# (file, texts with %s = root, note)
AUDIT111_LOG_READERS = (('audit111/runsum.py', ("'obs111': '%s/log_obs111.txt'", "'shp111': '%s/log_shp111.txt'"),
                         'log_obs111/vds111/vds111b/shp111/vss111/vid111.txt (in s111)'),
                        ('audit111/clocks_arm.py', ("root = '%s/'",),
                         'log_<tag>.txt (in s111); <tag>.json and {cpu,gpu}clk_<tag>.csv are carried'))
# Reader of a carried output: guardcost.py reads <root>/audit111/runsum.txt.  (file, text with %s = root)
AUDIT111_CARRIED_READER = ('audit111/guardcost.py', "open('%s/audit111/runsum.txt', encoding='utf-8')")
# Mutant runner: builds twenty mutants of <root>/audit111/rerun/{shp111,vds111b}.py into <root>/audit111/mut/<name>/
# and runs the rerun fixture suites on them.  (file, texts with %s = root, mutant folder)
AUDIT111_MUTRUN = ('audit111/newmut.py', ("A = Path('%s/audit111'); R = A / 'rerun'; M = A / 'mut'",
                                          "\"Path('%s/audit111/rerun/fx_vds111b')\""), 'audit111/mut')
# Helpers with no root literal (argv only, the session transcript or C:/kyty-wide): byte-identical copies.
AUDIT111_PLAIN = ('audit111/grep_src.py', 'audit111/mtime_scan.py', 'audit111/subagent_scan.py',
                  'audit111/transcript_dump.py', 'audit111/transcript_scan.py')
# The audit's frozen re-run copies (audit111/rerun/): byte copies of the sealed top-level files, except test_vds111b.py
# whose BASE names <root>/audit111/rerun/fx_vds111b.  r6 is keyed by the top-level name, so their PRED / CONSTANTS stay
# naive-only.  (copy, top-level original, (original text, copy text) or None)
AUDIT111_RERUN = (('audit111/rerun/obs111.py', 'obs111.py', None),
                  ('audit111/rerun/shp111.py', 'shp111.py', None),
                  ('audit111/rerun/vds111b.py', 'vds111b.py', None),
                  ('audit111/rerun/test_obs111.py', 'test_obs111.py', None),
                  ('audit111/rerun/test_shp111.py', 'test_shp111.py', None),
                  ('audit111/rerun/test_vds111b.py', 'test_vds111b.py',
                   ("BASE = Path('C:/kyty/s106_stage/fx_vds111b')", "BASE = Path('%s/audit111/rerun/fx_vds111b')")),
                  ('audit111/rerun/run_safety99.py', 'run_safety99.py', None))
# The twenty mutants: module-level mut(target, name, old, new) calls of newmut.py; target 'shp' -> <name>/shp111.py,
# 'vds' -> <name>/vds111b.py plus <name>/test_vds111b.py (BASE -> <root>/audit111/mut/<name>/fx).  All CRLF
# (write_text).
MUTANT_DIR_111 = 'audit111/mut'
N_MUTANTS_111 = 20
AUDIT111_TARGETS = {'shp': 'shp111.py', 'vds': 'vds111b.py'}
# Session-104 archive scorers pin the PRE-SHIP gates baseline; after the naive rewrite their
# GATES_FILE names the s112 copy, which holds the shipped dawalk=1 text.  Report only.
GATES_PINNED = ('a104.py', 'dwk104.py')
# Session-105..111 archive scorers pin the CURRENT baseline (303a7849...); the pin still holds in s112.
GATES_CURRENT = ('lead105.py', 'ctx105.py', 'gw106.py', 'dab106.py', 'dab107.py', 'fam108.py', 'frf109.py',
                 'frm109.py', 'shp110.py', 'shp111.py')
# obs111.py names its gate file for information only (no GATES_SHA): (file, gate file, sha pinned by SEALS111)
GATES_INFO = (('obs111.py', 'gates_obs111.txt', OBS111_SHA),)
BINARY_PINNED = ('a104.py', 'dwk104.py', 'lead105.py', 'ctx105.py', 'gw106.py', 'dab106.py', 'dab107.py',
                 'fam108.py', 'ent109.py', 'vfy109.py', 'ent109b.py', 'frf109.py', 'frm109.py',
                 'stl110.py', 'stl110b.py', 'shp110.py', 'obs111.py', 'vds111.py', 'vds111b.py', 'shp111.py')
# Session-109 scorers pinned to the session-109 binaries (kept in s109, never carried).
BINARY109 = (('ent109.py', 'kyty_emulator_e90f5543.exe'), ('vfy109.py', 'kyty_emulator_2f593229.exe'),
             ('ent109b.py', 'kyty_emulator_2f593229.exe'), ('frf109.py', 'kyty_emulator_2f593229.exe'),
             ('frm109.py', 'kyty_emulator_2f593229.exe'))
# Session-110 scorers pinned to the session-110 binary, and obs111.py pinned to check110's build (both kept in s110,
# never carried).
BINARY110 = (('stl110.py', 'kyty_emulator_b3f7a2c9.exe'), ('stl110b.py', 'kyty_emulator_b3f7a2c9.exe'),
             ('shp110.py', 'kyty_emulator_b3f7a2c9.exe'), ('obs111.py', 'kyty_emulator_072861c8.exe'))
# Session-111 scorers pinned to the session-111 binary (kept in s111, not carried).
BINARY111 = (('vds111.py', 'kyty_emulator_c8235c90.exe'), ('vds111b.py', 'kyty_emulator_c8235c90.exe'),
             ('shp111.py', 'kyty_emulator_c8235c90.exe'))
# Session-108 video checks pinned to their builds by BUILD_SHA; the scored binaries stay in s108.
BUILD_PINNED = (('check108.py', 'kyty_emulator_fc78c564.exe'), ('check108r.py', 'kyty_emulator_379777bb.exe'))
# Session-111 outputs that hash their own tool into the output = the s111 files.
# (tool, output, key, the output's 'scorer' field: None = absent)
SELF_HASHED = (('obs111.py', 'runs111/obs111_score.json', 'scorer_sha256', 'obs111.py'),
               ('vds111.py', 'runs111/vds111_score.json', 'scorer_sha256', None),
               ('vds111b.py', 'runs111/vds111b_score.json', 'scorer_sha256', None),
               ('shp111.py', 'runs111/shp111_score.json', 'scorer_sha256', 'shp111.py'),
               ('shp111.py', 'runs111/shp111_score_video.json', 'scorer_sha256', 'shp111.py'),
               ('check111.py', 'runs111/check111.json', 'check_sha256', None))
# Earlier run outputs record the ORIGINAL tools' sha256 (the s111 copies already differ).
# (tool, output, key, root, the output's 'scorer' field or None when absent/not checked)
SELF_HASHED_PRIOR = (('stl110.py', 'runs110/stl110_score.json', 'scorer_sha256', ROOT110, None),
                     ('stl110b.py', 'runs110/stl110b_score.json', 'scorer_sha256', ROOT110, None),
                     ('shp110.py', 'runs110/shp110_score.json', 'scorer_sha256', ROOT110, 'shp110.py'),
                     ('shp110.py', 'runs110/shp110_score_video.json', 'scorer_sha256', ROOT110, 'shp110.py'),
                     ('check110.py', 'runs110/check110.json', 'check_sha256', ROOT110, None),
                     ('ent109.py', 'runs109/ent109_score.json', 'scorer_sha256', ROOT109, None),
                     ('vfy109.py', 'runs109/vfy109_score.json', 'scorer_sha256', ROOT109, None),
                     ('ent109b.py', 'runs109/ent109b_score.json', 'scorer_sha256', ROOT109, None),
                     # frm109.py is frf109.py with a new seal: it writes scorer 'frf109.py' but hashes itself.
                     ('frm109.py', 'runs109/frm109_score.json', 'scorer_sha256', ROOT109, 'frf109.py'),
                     ('fam108.py', 'runs108/fam108_score.json', 'scorer_sha256', ROOT108, 'fam108.py'),
                     ('fam108.py', 'runs108/fam108_score_video.json', 'scorer_sha256', ROOT108, 'fam108.py'),
                     ('check108.py', 'runs108/check108.json', 'check_sha256', ROOT108, None),
                     ('check108r.py', 'runs108/check108r.json', 'check_sha256', ROOT108, None),
                     ('obs107.py', 'runs107/obs107_score.json', 'scorer_sha256', ROOT107, 'obs107.py'),
                     ('dab107.py', 'runs107/dab107_score.json', 'scorer_sha256', ROOT107, 'dab107.py'))
# Offline tests whose optional real-log case reads a log the port never carries.  Report only.
TEST_LOG_MOVED = (('test_a104.py', "'%s/log_reg104.txt'"), ('test_dwk104.py', "'%s/log_reg104.txt'"))
# One-shot scripts of sessions 103..111 (patches of the source tree, of the session documents and of the game
# contexts, and the generators).  Carried by naive rewrite, never run.
ONE_SHOT = ('patch_s103_bdalean.py', 'patch_s103_envflag.py', 'patch_s103_loopcap.py',
            'patch_s103_loopcap_host.py', 'facts_audit_fix.py', 'claims_fix.py', 'roadmap_s103.py',
            'claude_md_s103.py', 'handoff_s103.py',
            'claims_fix104.py', 'claude_md_s104.py',
            'make_ctx105.py',
            'make_gw106.py', 'make_dab106.py', 'roadmap106_close.py',
            'make_dab107.py', 'roadmap107_close.py',
            'make_fam108.py', 'roadmap108_close.py', 'facts108_fix.py', 'ctx108.py', 'handoff108.py',
            'make_ent109b.py', 'make_frf109.py', 'make_frm109.py', 'close109.py', 'ctx109.py',
            'make_stl110.py', 'make_test_stl110.py', 'make_stl110b.py', 'make_shp110.py', 'close110.py',
            'make_shp111.py', 'make_vds111b.py', 'make_check111.py')
# target <root>/FACTS.md -> s112 after the naive rewrite
ONE_SHOT_MOVED = ('facts_audit_fix.py', 'claims_fix.py', 'claims_fix104.py', 'facts108_fix.py')
# Session-108..110 one-shots that patch the game folder's contexts (targets not moved by the rewrite).
# (file, target text)
GAME_ONE_SHOTS = (('ctx108.py', "root = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')"),
                  ('handoff108.py', "p = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em/HANDOFF.md')"),
                  ('ctx109.py', "GAME = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')"),
                  ('close110.py', "GAME = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')"))
# One-shot ROADMAP patches, simulated in memory against the current ROADMAP.  (file, inserted text, target line)
ROADMAP_PATCHES = (('roadmap106_close.py', 'pred/03_audit106.md', "p = 'C:/kyty/KytyPS5/docs/ROADMAP.md'"),
                   ('roadmap107_close.py', 'pred/03_audit107.md', "p = 'C:/kyty/KytyPS5/docs/ROADMAP.md'"),
                   ('roadmap108_close.py', 'pred/02_audit108.md', "p = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')"))
# Session closes: append to <root>/SEALSnnn.txt, hash <root>/pred/<audit> (absent at the destination), edit
# <root>/FACTS.md, then edit the ROADMAP with edit(RM, [(anchor, replacement), ...]).
# (file, root line with %s = root, root variable, ROADMAP line, audit line, audit basename, seal record)
CLOSES = (('close109.py', "S109 = Path('%s')", 'S109', "RM = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')",
           "audit = S109 / 'pred' / '05_audit109.md'", '05_audit109.md', 'SEALS109.txt'),
          ('close110.py', "S110 = Path('%s')", 'S110', "RM = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')",
           "audit = S110 / 'pred' / '04_audit110.md'", '04_audit110.md', 'SEALS110.txt'))
# Usage docstrings that name the staging folder the earlier ports moved (now C:/kyty/s111_stage, absent); the naive
# rewrite moves them once more.
STAGE_MENTIONS = ('fixture_dab106.py', 'fixture_gw106.py', 'make_gw106.py')
STAGE = 'C:/kyty/s111_stage'
STAGE_NEXT = 'C:/kyty/s112_stage'
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
# (audit108/mutants/test_fam108_w<i>.py, BASE in audit108/fx_w<i>, left in C:/kyty/s110 by the 111 port; mutants108p.py).
MUTANT_DIR = 'audit108/mutants'
N_MUTANTS_108 = 22
N_TEST_COPIES_108 = 19
TEST_BASE_108 = "BASE = Path('C:/kyty/s106_stage/fx_fam108')"
# fam108.py's PRED as r6 left it at each root, and as the mutants carry it (naive only).
FAM_PRED_R6 = "PRED = '%s/%s/01_cspfam.md'"
FAM_PRED_MUT = "PRED = '%s/pred/01_cspfam.md'"
# Session 109's audit: 30 mutants of ent109/ent109b/vfy109/frm109 (audit109/mut/<name>__<scorer>.py, CRLF, written
# with write_text by newmut.py from its table M).
MUTANT_DIR_109 = 'audit109/mut'
N_MUTANTS_109 = 30
SEAL_OF = {'ent109.py': '01_ent109.md', 'vfy109.py': '01b_vfy109.md', 'ent109b.py': '02_ent109b.md',
           'frf109.py': '03_frf109.md', 'frm109.py': '04_frm109.md'}
SEAL_OF_110 = {'stl110.py': '01_stl110.md', 'stl110b.py': '02_stl110b.md', 'shp110.py': '03_shp110.md'}
SEAL_OF_111 = {'obs111.py': '01_obs111.md', 'vds111.py': '02_vds111.md', 'vds111b.py': '02b_vds111b.md',
               'shp111.py': '03_shp111.md'}
# Frozen evidence with a BARE literal that r6 (keyed by the top-level name) deliberately does not
# reach: the session-105 audit's copy of the committed, pre-fix ctx105.py, session 107's audit mutants of
# obs107.py and dab107.py, and (added in frozen_bare()) session 108's 22, session 109's 30, session 110's 20 and
# session 111's 20 audit mutants and session 111's three rerun scorer copies.  (file, line, basename)
FROZEN_DANGLING_BARE = (('audit105/recount_protocol/ctx105_git.py', "PRED = '%s/pred/02_m31.md'", '02_m31.md'),
                        ('audit107/obs107_mutPIN.py', "PRED = '%s/pred/01_obs107.md'", '01_obs107.md'),
                        ('audit107/dab107_mutS2.py', "PRED = '%s/pred/02_dabatch2.md'", '02_dabatch2.md'))
# The two session-107 mutants differ from their scorers in the mutated lines plus the PRED line (r6 reached the
# scorer, not the mutant): (mutant, scorer, mutated lines).
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
                  ('go108.sh', 'cd /c/kyty/s108'), ('go108v.sh', 'cd /c/kyty/s108'),
                  ('go108s.sh', 'cd /c/kyty/s108'), ('go108p.sh', 'cd /c/kyty/s108'),
                  ('go108r.sh', 'cd /c/kyty/s108'),
                  ('go109.sh', 'cd /c/kyty/s109'), ('go109b.sh', 'cd /c/kyty/s109'),
                  ('go109c.sh', 'cd /c/kyty/s109'),
                  # Session 110's run chains (they ENTER THE GAME and hold C:/kyty/SEALED_RUN.lock; never run).
                  ('go110.sh', 'cd /c/kyty/s110'), ('go110b.sh', 'cd /c/kyty/s110'),
                  ('go110c.sh', 'cd /c/kyty/s110'), ('go110v.sh', 'cd /c/kyty/s110'),
                  # Session 111's run chains (they ENTER THE GAME and hold C:/kyty/SEALED_RUN.lock; never run).
                  ('go111.sh', 'cd /c/kyty/s111'), ('go111b.sh', 'cd /c/kyty/s111'),
                  ('go111v.sh', 'cd /c/kyty/s111'))
# Dangling-path census: carried Python files that, after repair, name <DST>/<path> where <SRC>/<path>
# exists but <DST>/<path> does not.  Every hit must be one of these (file -> paths); the twenty session-111 audit
# mutants (their seal each) are added in census_want().  The session-110 files that named <root>/pred/<seal110> and
# the session-108 worker copies no longer hit (their source paths are gone from s111: the seals moved to prev110/pred,
# the fx_w<i> folders stayed in s110).
CENSUS = {
    'close110.py': ('FACTS.md',),                                    # FACTS / ROADMAP / context texts
    'make_shp111.py': ('pred/03_shp111.md',),                        # the replacement text of its PRED rep()
    'make_vds111b.py': ('pred/02_vds111.md', 'pred/02b_vds111b.md'),  # its PRED anchor and replacement texts
    'mut_shp111.py': ('pred/03_shp111.md',),                         # its CONST_pred_shp110 mutant anchor
    'test_obs111.py': ('pred/01_obs111.md',),                        # its CONSTANTS check
    'test_shp111.py': ('pred/03_shp111.md',),                        # its CONSTANTS table
    'audit111/rerun/obs111.py': ('pred/01_obs111.md',),              # frozen rerun copies (r6 is keyed by the
    'audit111/rerun/shp111.py': ('pred/03_shp111.md',),              # top-level name)
    'audit111/rerun/vds111b.py': ('pred/02b_vds111b.md',),
    'audit111/rerun/test_obs111.py': ('pred/01_obs111.md',),
    'audit111/rerun/test_shp111.py': ('pred/03_shp111.md',),
    'audit111/allfields.py': ('log_shp111.txt',),                    # logs / stdout / video index: not carried
    'audit111/runsum.py': ('log_obs111.txt', 'log_shp111.txt', 'log_vds111.txt', 'log_vds111b.txt', 'log_vid111.txt',
                           'log_vss111.txt'),
    'audit111/recount_misc.py': ('rec_vid111.mp4.idx', 'stdout_obs111.txt', 'stdout_vid111.txt', 'stdout_vss111.txt'),
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
                  'facts108_fix.py', 'ctx108.py', 'handoff108.py', 'ctx109.py')
N_FACTS_MENTIONS = 45
# Tag -> session whose root holds log_<tag>.txt (logs are never carried).
ROOT_TESTS = ((('obs111', 111), ('vds111', 111), ('vds111b', 111), ('shp111', 111), ('vid111', 111),
               ('vss111', 111)) +
              tuple(('stl110_%d' % i, 110) for i in range(1, 9)) +
              tuple(('stl110b_%d' % i, 110) for i in range(1, 9)) +
              (('shp110', 110), ('vid110', 110), ('vsh110', 110)) +
              tuple(('ent109_%d' % i, 109) for i in range(1, 9)) +
              tuple(('ent109b_%d' % i, 109) for i in range(1, 9)) +
              (('vfy109', 109), ('frm109', 109),
               ('fam108', 108), ('sf108a', 108), ('sf108b', 108), ('sf108c', 108), ('sf108d', 108),
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
               ('bl93a', 93), ('stg92a', 92)))


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
                          ('/c/kyty/s111', '/c/kyty/s112')):
        t = t.replace(before, after)
    return t


def naive_prev(t):
    """The previous port's naive rewrite (s110 -> s111), used to re-derive the carried session-110 audit mutants."""
    for before, after in ((PREV_OLD, OLD), (PREV_OLD.replace('/', '\\\\'), OLD.replace('/', '\\\\')),
                          (PREV_OLD.replace('/', '\\'), OLD.replace('/', '\\')),
                          ('/c/kyty/s110', '/c/kyty/s111')):
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
    """The root-relative part of an r7 line: 'prev1NN/pred/<name>' or 'pred/<name>'."""
    m = re.search(r"((?:prev\d+/)?pred/[^']+)'", line)
    assert m, line
    return m.group(1)


def r7_files():
    return sorted({f for f, _, _, _, _, _, _ in REPOINT2})


def module_list(path, name):
    """A module-level list/dict literal <name> of path, by AST (never imported)."""
    tree = ast.parse(rd(path))
    found = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
    assert len(found) == 1, (path, name)
    return ast.literal_eval(found[0].value)


def mutant_table():
    """{name: (old, new)} of session 108's audit mutants, read from mutants_def.py by AST (never imported)."""
    table = module_list(SRC / MUTANTS_DEF, 'MUTANTS')
    assert len(table) == N_MUTANTS_108, len(table)
    return table


def mutant_names():
    return ['%s/fam108_%s.py' % (MUTANT_DIR, n) for n in sorted(mutant_table())]


def test_copy_names():
    return ['%s/test_fam108_w%d.py' % (MUTANT_DIR, i) for i in range(N_TEST_COPIES_108)]


def mutant_table_109():
    """[(scorer, test, name, old, new)] of session 109's audit mutants, from newmut.py's M by AST."""
    table = module_list(SRC / AUDIT_MUTRUN_109[0], 'M')
    assert len(table) == N_MUTANTS_109 and len({n for _, _, n, _, _ in table}) == N_MUTANTS_109, len(table)
    return table


def mutant_names_109():
    return ['%s/%s__%s' % (MUTANT_DIR_109, name, scorer) for scorer, _, name, _, _ in mutant_table_109()]


def mutant_table_110():
    """[(scorer, test, name, old, new)] of session 110's audit mutants, from audit110/newmut.py's STL and SHP by AST."""
    out = []
    for table, scorer, test in AUDIT110_TABLES:
        for name, old, new in module_list(SRC / AUDIT110_MUTRUN[0], table):
            out.append((scorer, test, name, old, new))
    assert len(out) == N_MUTANTS_110 and len({n for _, _, n, _, _ in out}) == N_MUTANTS_110, len(out)
    return out


def mutant_names_110():
    return ['%s/%s/%s' % (MUTANT_DIR_110, name, scorer) for scorer, _, name, _, _ in mutant_table_110()]


def mutant_table_111():
    """[(target, name, old, new)] of session 111's audit mutants, from audit111/newmut.py's module-level
    mut(target, name, old, new) calls by AST (never imported)."""
    tree = ast.parse(rd(SRC / AUDIT111_MUTRUN[0]))
    out = []
    for n in tree.body:
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) \
                and n.value.func.id == 'mut':
            assert len(n.value.args) == 4 and not n.value.keywords, ast.dump(n)[:80]
            out.append(tuple(ast.literal_eval(a) for a in n.value.args))
    assert len(out) == N_MUTANTS_111 and len({x[1] for x in out}) == N_MUTANTS_111, len(out)
    assert {x[0] for x in out} == set(AUDIT111_TARGETS), {x[0] for x in out}
    return out


def mutant_scorers_111():
    """The twenty mutated scorer files audit111/mut/<name>/{shp111,vds111b}.py."""
    return ['%s/%s/%s' % (MUTANT_DIR_111, name, AUDIT111_TARGETS[target]) for target, name, _, _ in mutant_table_111()]


def mutant_tests_111():
    """The eight vds mutants' fixture copies audit111/mut/<name>/test_vds111b.py."""
    return ['%s/%s/test_vds111b.py' % (MUTANT_DIR_111, name) for target, name, _, _ in mutant_table_111()
            if target == 'vds']


def pred_r6(scorer, root):
    """The r6'd PRED line of an inherited (session-109) scorer at <root>, and the naive-only form its mutants carry."""
    return ("PRED = '%s/%s/%s'" % (root, INHERITED, SEAL_OF[scorer]), "PRED = '%s/pred/%s'" % (root, SEAL_OF[scorer]))


def frozen_bare():
    return FROZEN_DANGLING_BARE + \
        tuple((f, FAM_PRED_MUT, '01_cspfam.md') for f in mutant_names()) + \
        tuple(('%s/%s__%s' % (MUTANT_DIR_109, name, scorer), "PRED = '%s/pred/" + SEAL_OF[scorer] + "'",
               SEAL_OF[scorer]) for scorer, _, name, _, _ in mutant_table_109()) + \
        tuple(('%s/%s/%s' % (MUTANT_DIR_110, name, scorer), "PRED = '%s/pred/" + SEAL_OF_110[scorer] + "'",
               SEAL_OF_110[scorer]) for scorer, _, name, _, _ in mutant_table_110()) + \
        tuple((f, "PRED = '%s/pred/" + SEAL_OF_111[f.rsplit('/', 1)[1]] + "'", SEAL_OF_111[f.rsplit('/', 1)[1]])
              for f in mutant_scorers_111()) + \
        tuple((f, "PRED = '%s/pred/" + SEAL_OF_111[orig] + "'", SEAL_OF_111[orig])
              for f, orig, _ in AUDIT111_RERUN if orig in SEAL_OF_111)


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
    replace('r1', 'C:/kyty/s112,C:/kyty/s110', 'C:/kyty/s112,C:/kyty/s111,C:/kyty/s110', False)
    if key in ARITH:
        floor, tag = ARITH[key]
        replace(tag, 'range(111, %d, -1)' % floor, 'range(112, %d, -1)' % floor)
    if key in TUPLES:
        replace('r4', naive(chain(111, TUPLES[key])), chain(112, TUPLES[key]))
    if key == 'regime94.py':
        replace('r5', naive(regime(111)), regime(112))
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
    """({text basename: sha256}, {tool name: sha256}, {tool name: note}) of a session's SEALSnnn.txt
    ('<sha> *[pred/]<name>[ <note>]' per line).  SEALS108/109/110/111.txt pin tools too: there only the pred/-prefixed
    entries are texts.  SEALS111.txt's last three tool lines carry a trailing parenthetical note ('(post-run: ...)');
    a note is accepted only on a tool line, only in a record listed in TOOL_NOTES, and only as '(...)'."""
    texts, tools, notes = {}, {}, {}
    for line in rd(SRC / name).splitlines():
        if line.strip():
            parts = line.split(' ', 2)
            h, n = parts[0], parts[1]
            note = parts[2] if len(parts) == 3 else None
            assert re.fullmatch(r'[0-9a-f]{64}', h) and n.startswith('*'), (name, line)
            n = n.lstrip('*')
            prefixed = n.startswith('pred/')
            n = n[len('pred/'):] if prefixed else n
            assert '/' not in n and n not in texts and n not in tools, (name, line)
            if note is not None:
                assert name in TOOL_NOTES and not prefixed and note.startswith('(') and note.endswith(')'), (name, line)
                notes[n] = note
            if name in TOOL_RECORDS and not prefixed:
                tools[n] = h
            else:
                texts[n] = h
    return texts, tools, notes


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
    """The anchors of the five older one-shot generators, as they read under <root>:
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
CENSUS_RX = re.compile(r"(?:C:" + _SEP + r"kyty" + _SEP + r"s112|/c/kyty/s112)(" + _SEP + r"[^'\"\s,)%*<>`]+)")


def census(texts, exists):
    """{file: sorted paths} over texts ({key: repaired text}, ports excluded): every <DST>/<path> named in a
    text whose <SRC>/<path> exists while exists(<path>) is false."""
    hits = {}
    for key, t in texts.items():
        if key.endswith('_port.py'):
            continue
        for m in CENSUS_RX.finditer(t):
            tail = re.sub(r'(?:\\\\|\\|/)+', '/', m.group(1)).strip('/').rstrip('.:;').rstrip('/')
            if not tail or not tail.replace('.', '').replace('/', ''):
                continue
            if (SRC / tail).exists() and not exists(tail):
                hits.setdefault(key, set()).add(tail)
    return {k: tuple(sorted(v)) for k, v in hits.items()}


def census_want():
    want = dict(CENSUS)
    for f in mutant_scorers_111():
        assert f not in want, f
        want[f] = ('pred/' + SEAL_OF_111[f.rsplit('/', 1)[1]],)
    for f in FACTS_MENTIONS:
        assert f not in want, f
        want[f] = ('FACTS.md',)
    return want


def check_census(hits, stage):
    assert len(FACTS_MENTIONS) == len(set(FACTS_MENTIONS)) == N_FACTS_MENTIONS
    assert set(ONE_SHOT_MOVED) <= set(FACTS_MENTIONS)
    want = census_want()
    assert hits == want, (stage, sorted(set(hits.items()) ^ set(want.items())))


def fixture_dir_of(key):
    """The fx_* folder a source path lies in (None: not in one)."""
    parts = key.split('/')[:-1]
    for i, part in enumerate(parts):
        if part.startswith('fx_'):
            return '/'.join(parts[:i + 1])
    return None


def skip_reason(key, f, sp, rel):
    """Why a source file is not carried (None: carried)."""
    if fixture_dir_of(key) is not None:
        return 'fixture-dir'
    if rel == Path('.') and CONCURRENT_RX.match(f):
        return 'concurrent-112'
    if AUDIT111_PKL_RX.match(key):
        return 'audit111-pkl'
    if f.startswith(SKIP_PREFIX) or f.endswith(SKIP_EXT) or sp.stat().st_size >= BIG:
        return 'model'
    if rel == Path('.') and f in DOCS:
        return 'doc'
    return None


def _lit(node, env):
    """A string literal, a module-level name bound to one, a '+' of those, or <literal>.replace(<lit>, <lit>)
    (anything else: ValueError)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id in env:
        return env[node.id]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _lit(node.left, env) + _lit(node.right, env)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'replace' \
            and len(node.args) == 2 and not node.keywords:
        return _lit(node.func.value, env).replace(_lit(node.args[0], env), _lit(node.args[1], env))
    raise ValueError(ast.dump(node)[:80])


def module_env(tree):
    env = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                env[node.targets[0].id] = _lit(node.value, env)
            except ValueError:
                pass
    return env


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


def edit_stop(name, target='RM'):
    """Simulate <name>'s edit(<target>, [(anchor, replacement), ...]) against the CURRENT ROADMAP, in memory only.
    Returns (index of the first anchor not found exactly once, None if all match, or 'undetermined' when a
    replacement cannot be evaluated before any stop; number of pairs)."""
    tree = ast.parse(rd(DST / name))
    env = module_env(tree)
    calls = [n.value for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
             and isinstance(n.value.func, ast.Name) and n.value.func.id == 'edit'
             and isinstance(n.value.args[0], ast.Name) and n.value.args[0].id == target]
    assert len(calls) == 1, (name, len(calls))
    pairs = calls[0].args[1].elts
    s = rd(ROADMAP).replace('\r\n', '\n')
    for i, tup in enumerate(pairs, 1):
        a = _lit(tup.elts[0], env)
        if s.count(a) != 1:
            return i, len(pairs)
        try:
            b = _lit(tup.elts[1], env)
        except ValueError:
            return 'undetermined', len(pairs)
        s = s.replace(a, b)
    return None, len(pairs)


def derive_stop(name, stage_text, root=DST, which=0):
    """Simulate the <which>-th derive(src, dst, pairs) of <root>/<name> (make_ent109b.py, make_vds111b.py) on
    stage_text, in memory only.  Returns (index of the first anchor not found exactly once or None, number of pairs)."""
    tree = ast.parse(rd(root / name))
    env = module_env(tree)
    calls = [n.value for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
             and isinstance(n.value.func, ast.Name) and n.value.func.id == 'derive']
    assert len(calls) > which and len(calls[which].args) == 3 and not calls[which].keywords, name
    pairs = calls[which].args[2].elts
    s = stage_text.replace('\r\n', '\n')
    for i, tup in enumerate(pairs, 1):
        a, b = _lit(tup.elts[0], env), _lit(tup.elts[1], env)
        if s.count(a) != 1:
            return i, len(pairs)
        s = s.replace(a, b)
    return None, len(pairs)


def derive4_stop(name):
    """Simulate the first derive(src, src_sha, dst, pairs[, counts]) of <name> (make_stl110b.py) on the staging file it
    reads, in memory only.  Returns (('sha', got) when the sha pin fails, or the index of the first anchor not found the
    wanted number of times, or None; number of pairs, src, dst)."""
    tree = ast.parse(rd(DST / name))
    env = module_env(tree)
    calls = [n.value for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
             and isinstance(n.value.func, ast.Name) and n.value.func.id == 'derive']
    assert calls and len(calls[0].args) in (4, 5) and not calls[0].keywords, name
    args = calls[0].args
    src, src_sha, dst = _lit(args[0], env), _lit(args[1], env), _lit(args[2], env)
    counts = ast.literal_eval(args[4]) if len(args) == 5 else {}
    pairs = args[3].elts
    b = (Path(REAL_STAGE) / src).read_bytes()
    if hashlib.sha256(b).hexdigest() != src_sha:
        return ('sha', hashlib.sha256(b).hexdigest()), len(pairs), src, dst
    s = b.decode('utf-8')
    for i, tup in enumerate(pairs, 1):
        a, r = _lit(tup.elts[0], env), _lit(tup.elts[1], env)
        want = counts.get(a, 1)
        if not ((s.count(a) >= 1) if want is None else (s.count(a) == want)):
            return i, len(pairs), src, dst
        s = s.replace(a, r)
    return None, len(pairs), src, dst


def pairs_stop(name, stage_path, tag_anchor=None):
    """Simulate <name>'s sha pin on stage_path and its module-level `pairs` loop (make_stl110.py, make_test_stl110.py),
    in memory only.  tag_anchor: the one anchor whose wanted count is its count in the source (make_test_stl110.py's
    n_tag).  Returns (('sha', got) or index of the first anchor not found the wanted number of times or None, number of
    pairs)."""
    tree = ast.parse(rd(DST / name))
    env = module_env(tree)
    found = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'pairs']
    assert len(found) == 1, name
    pairs = found[0].value.elts
    b = stage_path.read_bytes()
    if hashlib.sha256(b).hexdigest() != env['SRC_SHA']:
        return ('sha', hashlib.sha256(b).hexdigest()), len(pairs)
    s = b.decode('utf-8')
    n_tag = s.count(tag_anchor) if tag_anchor else None
    for i, tup in enumerate(pairs, 1):
        a, r = _lit(tup.elts[0], env), _lit(tup.elts[1], env)
        want = n_tag if a == tag_anchor else 1
        if s.count(a) != want:
            return i, len(pairs)
        s = s.replace(a, r)
    return None, len(pairs)


def anchored_stop(name, source_text, root=DST):
    """Simulate <root>/<name>'s module-level rep(old, new[, count]) / keep(old[, count]) chain (make_frf109.py,
    make_shp110.py, make_shp111.py) on source_text, in memory only.  Returns (index of the first anchor not found the
    wanted number of times, None if all match, or 'undetermined' at an unevaluable argument; number of calls, the text
    after the chain)."""
    tree = ast.parse(rd(root / name))
    env = module_env(tree)
    env.setdefault('NL', '\n')
    calls = [n.value for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
             and isinstance(n.value.func, ast.Name) and n.value.func.id in ('rep', 'keep')]
    s = source_text
    for i, c in enumerate(calls, 1):
        try:
            args = [_lit(a, env) if not isinstance(a, ast.Constant) or isinstance(a.value, str) else a.value
                    for a in c.args]
            count = {k.arg: ast.literal_eval(k.value) for k in c.keywords}.get('count', 1)
        except ValueError:
            return 'undetermined', len(calls), None
        if c.func.id == 'rep':
            old, new = args[0], args[1]
            count = args[2] if len(args) > 2 else count
        else:
            old, new = args[0], None
            count = args[1] if len(args) > 1 else count
        if s.count(old) != count:
            return i, len(calls), None
        if new is not None:
            s = s.replace(old, new)
    return None, len(calls), s


def stale_fresh_stop(name, text, root=DST):
    """make_shp110.py's / make_shp111.py's last guards before its write: 'stale' texts must be absent from, 'fresh'
    texts present in, the code after the module docstring.  Returns the first failing (kind, text) or None."""
    tree = ast.parse(rd(root / name))
    body = text.split('"""', 2)[2]
    for node in tree.body:
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id in ('stale', 'fresh'):
            for x in ast.literal_eval(node.iter):
                if (x in body) == (node.target.id == 'stale'):
                    return node.target.id, x
    return None


def pairs_list_stop(name, source_text, root=DST):
    """Simulate <root>/<name>'s (make_check111.py) module-level `pairs` loop on source_text (LF), in memory only.
    Returns (index of the first anchor not found exactly once or None, number of pairs, the text after the loop)."""
    tree = ast.parse(rd(root / name))
    env = module_env(tree)
    found = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'pairs']
    assert len(found) == 1, name
    pairs = found[0].value.elts
    s = lf(source_text)
    for i, tup in enumerate(pairs, 1):
        a, r = _lit(tup.elts[0], env), _lit(tup.elts[1], env)
        if s.count(a) != 1:
            return i, len(pairs), None
        s = s.replace(a, r)
    return None, len(pairs), s


def mutant_anchor_stop(name, scorer_text, root=DST):
    """Simulate <root>/<name>'s (mut_shp110.py) anchor check of its module-level mutant(name, old, new) registrations
    on scorer_text, in memory only.  Returns (first failing mutant name, None if all match, or 'undetermined'; count).
    All of its registrations are module-level calls (its only loop is the check itself)."""
    tree = ast.parse(rd(root / name))
    env = module_env(tree)
    env.setdefault('NL', '\n')
    calls = [n.value for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
             and isinstance(n.value.func, ast.Name) and n.value.func.id == 'mutant']
    for c in calls:
        try:
            mname, old = _lit(c.args[0], env), _lit(c.args[1], env)
        except ValueError:
            return 'undetermined', len(calls)
        if scorer_text.count(old) != 1:
            return mname, len(calls)
    return None, len(calls)


def preconditions():
    assert SRC.resolve() != DST.resolve()
    assert not DST.exists(), 'destination exists: do not rerun a completed port'
    assert not (SRC / 'prev111').exists()
    assert not (SRC / LEDGER_NAME).exists()
    assert (SRC / PREV_LEDGER).is_file() and all((SRC / f).is_file() for f in PREV_LEDGERS_DATA)
    for f, opt in COMMA.items():
        t = rd(SRC / f)
        m = re.search(r"add_argument\('" + re.escape(opt) + r"', default='([^']*)'", t)
        assert m and m.group(1) == chain(111, 75, True), f
        assert len(m.group(1).split(',')) == 37, f
    for f, (floor, _) in ARITH.items():
        assert rd(SRC / f).count('range(111, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(SRC / f).count(chain(111, floor)) == 1, f
    assert {f: 111 - floor + 1 for f, floor in TUPLES.items()} == {'stg92.py': 22, 'bda93.py': 21, 's94lib.py': 20}
    assert rd(SRC / 'regime94.py').count(regime(111)) == 1 and 111 - 93 + 1 == 19
    assert rd(SRC / 'regime94.py').splitlines()[2] == 'import os, re, sys, statistics'
    assert tuple(f for f in DOCS if (SRC / f).is_file()) == DOCS_PRESENT, [f for f in DOCS if (SRC / f).is_file()]
    assert (SRC / DESIGN109).is_file() and not (SRC / 'design109.md').exists()
    sealed = sealed_index()
    assert len(sealed) == len(SEALED) == N_SEALED
    # No two texts may land on one path and no text is renamed.  The only shared basenames are
    # the two inherited pairs of audit addenda: sessions 100/101 (03_) and sessions 103/104 (04_).
    assert len({(land, n) for _, n, _, _, land in SEALED}) == N_SEALED
    names_all = [n for _, n, _, _, _ in SEALED]
    assert sorted({n for n in names_all if names_all.count(n) > 1}) == ['03_audit_addendum.md', '04_audit_addendum.md']
    s111_names = {n for d, n, _, _, _ in SEALED if d == 'pred'}
    assert s111_names == set(S111_NAMES) and len(s111_names) == 5
    # Collision check over EVERY earlier pred/ folder of the source (prev78..prev110, all of them, not
    # only the listed texts and not only the eleven carried ones): no session-111 basename is taken.
    folders = pred_folders(SRC)
    assert {p.relative_to(SRC).as_posix() for p in folders} >= set(CARRIED), folders
    assert len(folders) == 31, [p.relative_to(SRC).as_posix() for p in folders]
    every_name = set()
    for p in folders:
        every_name |= {q.name for q in p.iterdir()}
    assert not s111_names & every_name, s111_names & every_name
    # ... nor anywhere else in the source outside its pred/.
    elsewhere111 = sorted(q.relative_to(SRC).as_posix() for q in SRC.rglob('*')
                          if q.name in s111_names and q.parent != SRC / 'pred')
    assert elsewhere111 == [], elsewhere111
    # Session-110 basenames live only in prev110/pred (the 111 port landed them there).
    elsewhere110 = sorted(q.relative_to(SRC).as_posix() for q in SRC.rglob('*')
                          if q.name in S110_NAMES and q.parent != SRC / INHERITED)
    assert elsewhere110 == [], elsewhere110
    # Session-109 basenames live only in prev110/pred and prev109/pred.
    elsewhere109 = sorted(q.relative_to(SRC).as_posix() for q in SRC.rglob('*')
                          if q.name in S109_NAMES and q.parent not in (SRC / INHERITED, SRC / CARRIED109))
    assert elsewhere109 == [], elsewhere109
    # Session-108 basenames live only in prev110/109/108/pred.
    elsewhere108 = sorted(q.relative_to(SRC).as_posix() for q in SRC.rglob('*')
                          if q.name in S108_NAMES and q.parent not in (SRC / INHERITED, SRC / CARRIED109,
                                                                       SRC / CARRIED108))
    assert elsewhere108 == [], elsewhere108
    # Session-107 basenames live only in prev110/109/108/107/pred.
    elsewhere107 = sorted(q.relative_to(SRC).as_posix() for q in SRC.rglob('*')
                          if q.name in S107_NAMES and q.parent not in (SRC / INHERITED, SRC / CARRIED109,
                                                                       SRC / CARRIED108, SRC / CARRIED107))
    assert elsewhere107 == [], elsewhere107
    # A draft folder shares one basename with a session-106 seal (in prev110..106/pred); it is not a seal folder
    # and differs.  No other copy of a session-106 basename exists outside those five folders.
    for folder, n, size, h in DRAFT_SHARED:
        p = SRC / folder / n
        assert n in S106_NAMES and p.stat().st_size == size and sha(p) == h, (folder, n)
        assert h != sealed[(INHERITED, n)][1]
    shared106 = sorted(q.relative_to(SRC).as_posix() for q in SRC.rglob('*')
                       if q.name in S106_NAMES and q.parent not in (SRC / INHERITED, SRC / CARRIED109, SRC / CARRIED108,
                                                                    SRC / CARRIED107, SRC / CARRIED106))
    assert shared106 == ['%s/%s' % (f, n) for f, n, _, _ in DRAFT_SHARED], shared106
    assert all(land in (LAND, d) for d, _, _, _, land in SEALED)
    assert sum(1 for _, _, _, _, land in SEALED if land == LAND) == N_LAND
    assert [(d, n) for d, n, _, _, land in SEALED if land != LAND] == [
        (CARRIED103, '04_audit_addendum.md'), (OLDER, '03_audit_addendum.md')]
    for folder in ('pred', INHERITED):
        assert sorted(p.name for p in (SRC / folder).iterdir()) == sorted(n for d, n, _, _, _ in SEALED if d == folder), folder
    inherited_names = [n for d, n, _, _, _ in SEALED if d == INHERITED]
    assert len(inherited_names) == 60
    assert set(S102_NAMES) | set(S104_NAMES) | set(S105_NAMES) | set(S106_NAMES) | set(S107_NAMES) | \
        set(S108_NAMES) | set(S109_NAMES) | set(S110_NAMES) | (set(S103_NAMES) - {'04_audit_addendum.md'}) <= \
        set(inherited_names)
    # prev109/pred: fifty-six byte-identical twins of prev110/pred texts (sessions 96..109).
    twins109 = sorted(n for n in inherited_names if n not in S110_NAMES)
    assert len(twins109) == 56 and sorted(p.name for p in (SRC / CARRIED109).iterdir()) == twins109
    # prev108/pred: fifty twins (sessions 96..108).
    twins108 = sorted(n for n in twins109 if n not in S109_NAMES)
    assert len(twins108) == 50 and sorted(p.name for p in (SRC / CARRIED108).iterdir()) == twins108
    # prev107/pred: forty-eight twins (sessions 96..107).
    twins107 = sorted(n for n in twins108 if n not in S108_NAMES)
    assert len(twins107) == 48 and sorted(p.name for p in (SRC / CARRIED107).iterdir()) == twins107
    # prev106/pred: forty-five twins (sessions 96..106).
    twins106 = sorted(n for n in twins107 if n not in S107_NAMES)
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
    for folder, twins in ((CARRIED109, twins109), (CARRIED108, twins108), (CARRIED107, twins107),
                          (CARRIED106, twins106), (CARRIED105, twins105), (CARRIED104, twins104),
                          (CARRIED103, twins103), (CARRIED102, twins102), (CARRIED101, twins101), (OLDER, twins100)):
        for n in twins:
            assert sha(SRC / folder / n) == sealed[(INHERITED, n)][1] == sha(SRC / INHERITED / n), ('twin', folder, n)
    for d, n, size, h, _ in SEALED:
        assert (SRC / d / n).stat().st_size == size and sha(SRC / d / n) == h, (d, n)
    # The sessions' own seal records: SEALS111.txt names exactly the five session-111 texts (in pred/) plus twenty-one
    # tools (three with the post-run note); SEALS110.txt its four texts plus eighteen tools; SEALS109.txt its six texts
    # plus twenty tools; SEALS108.txt its two texts plus five tools; SEALS107..102.txt theirs, now read from
    # prev110/pred.
    for record, names, where in SEAL_RECORDS:
        texts, tools, notes = seal_record(record)
        want = {n: sealed[(where.get(n, 'pred' if record == SEALS_FILE else INHERITED), n)][1] for n in names}
        assert texts == want, (record, texts)
        assert tools == TOOL_RECORDS.get(record, {}), (record, tools)
        assert notes == TOOL_NOTES.get(record, {}), (record, notes)
    assert list(TOOL_NOTES[SEALS_FILE]) == list(SEALS111_POSTRUN)
    last3 = [line.split(' ', 2)[1].lstrip('*') for line in rd(SRC / SEALS_FILE).splitlines() if line.strip()][-3:]
    assert last3 == list(SEALS111_POSTRUN), last3
    for record, tools in TOOL_RECORDS.items():
        for n, h in tools.items():
            # The sealed originals are where the record was written; earlier ports rewrote some .py tools in the source.
            assert sha(RECORD_ROOT[record] / n) == h, ('sealed original moved', record, n)
            assert (sha(SRC / n) == h) == (n not in RECORD_REWRITTEN[record]), ('sealed tool', record, n)
            assert n.endswith('.py') or n not in RECORD_REWRITTEN[record], (record, n)
    live_paths = 0
    for f, names in REPOINT.items():
        t = rd(SRC / f)
        folder = REPOINT_FOLDER.get(f, INHERITED)
        for name in names:
            p = Path(const(t, name))
            assert p.parent == SRC / folder, (f, name, p)
            key = (folder, p.name)
            assert const(t, name + '_SHA') == sealed[key][1] == sha(p), (f, name)
            assert sealed[key][2] == LAND, ('live constant names a text outside prev111/pred', f, name)
            live_paths += 1
        m = re.search(r'^PRED_BYTES\s*=\s*(\d+)', t, re.M)
        if m:
            assert int(m.group(1)) == sealed[(folder, Path(const(t, 'PRED')).name)][0], f
    assert len(REPOINT) == N_R6_FILES and live_paths == N_R6_CONSTS, (len(REPOINT), live_paths)
    assert sorted(f for f in REPOINT if re.search(r'^PRED_BYTES\s*=', rd(SRC / f), re.M)) == sorted(PRED_BYTES_FILES)
    assert set(REPOINT_FOLDER) <= set(PRED_BYTES_FILES)
    assert {f: Path(const(rd(SRC / f), 'PRED')).name for f in REPOINT_FOLDER} == SEAL_OF_111
    for f, seal in list(SEAL_OF.items()) + list(SEAL_OF_110.items()):
        assert const(rd(SRC / f), 'PRED') == '%s/%s/%s' % (OLD, INHERITED, seal), f
    for f, seal in SEAL_OF_111.items():
        assert const(rd(SRC / f), 'PRED') == '%s/pred/%s' % (OLD, seal), f
    for f, text in IMPORTERS:
        assert text in rd(SRC / f), (f, text)
    for f, imp, override in SEAL_OVERRIDE_TESTS:
        t = rd(SRC / f)
        assert imp in t and override in t, f
    for f, loader, override, stage in FIXTURE_TESTS:
        t = rd(SRC / f)
        assert loader in t and override in t and stage in t and 'pred/' not in t, f
        # The session-109..111 fixtures name no root at all; test_dab107.py (usage line) and test_fam108.py (one
        # synthetic 'Recording:' line) do, and the naive rewrite moves them.
        assert (OLD in t) == (f in ('test_dab107.py', 'test_fam108.py')), f
    f, loader, override, stage, synthetic = FIXTURE_TEST_FRF
    t = rd(SRC / f)
    assert loader in t and override in t and stage in t and t.count(synthetic % OLD) == 1, f
    assert t.count(OLD) == 1 and '\r' not in t, f
    f, loader, override, stage, synthetic, consts = FIXTURE_TEST_SHP
    t = rd(SRC / f)
    assert loader in t and override in t and stage in t and t.count(synthetic % OLD) == 1, f
    assert t.count(consts[0] % (OLD, OLD)) == 1 and t.count(consts[1] % OLD) == 1, f
    assert t.count(OLD) == 4 and '\r' not in t, f
    f, loader, override, stage, synthetic, consts, fallback, n_old = FIXTURE_TEST_SHP111
    t = rd(SRC / f)
    assert loader in t and override in t and stage in t and fallback in t and t.count(synthetic % OLD) == 1, f
    assert t.count(consts[0] % (OLD, OLD)) == 1 and t.count(consts[1] % OLD) == 1, f
    assert t.count(OLD) == n_old and '\r' not in t, (f, t.count(OLD))
    f, loader, override, base, consts, envs = FIXTURE_TEST_OBS111
    t = rd(SRC / f)
    assert loader in t and override in t and base in t and all(t.count(c % OLD) == 1 for c in consts), f
    assert t.count(envs[0] % OLD) == 1 and t.count(envs[1] % OLD.replace('/', '\\\\')) == 1, f
    assert t.count(OLD) == 4 and t.count(OLD.replace('/', '\\\\')) == 1 and '\r' not in t, f
    assert "SRC = Path(ARGS[0]) if ARGS else HERE / 'obs111.py'" in t and 'shutil.rmtree(BASE)' in t, f
    for f in MUTATION_SCRIPTS:
        t = rd(SRC / f)
        assert REAL_STAGE in t and naive(t) == t, f
    f, texts = MUTATION_HERE
    t = rd(SRC / f)
    assert all(x in t for x in texts) and naive(t) == t and 'C:/kyty' not in t, f
    f, here, anchors = MUTATION_SHP
    t = rd(SRC / f)
    assert here in t and t.count(OLD) == 3 and all(t.count(a % OLD) == 1 for a in anchors), f
    # The 111 port already moved mut_shp110.py's three root-named anchors to s111, while its staging scorer names s110.
    stop110 = mutant_anchor_stop(f, rd(STAGE_SHP110), SRC)[0]
    assert isinstance(stop110, str) and stop110 != 'undetermined', stop110
    f, here, anchors = MUTATION_SHP111
    t = rd(SRC / f)
    assert here in t and t.count(OLD) == 3 and all(t.count(a % OLD) == 1 for a in anchors), f
    assert mutant_anchor_stop(f, rd(STAGE_SHP111), SRC)[0] is None, \
        'mut_shp111.py no longer matches its staging scorer in the source'
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
    # No other top-level Python file names a session-105..111 seal as a module constant (a quoted literal,
    # a ROOT +/ROOT / expression or a Path(...) whose text names pred/<name>).
    seal_rx = (r"^(\w+)\s*=\s*((?:ROOT\s*[+/]\s*|Path\()?['\"][^'\"\n]*pred/(?:%s)['\"].*)$"
               % '|'.join(re.escape(n) for n in S105_NAMES + S106_NAMES + S107_NAMES + S108_NAMES + S109_NAMES +
                          S110_NAMES + S111_NAMES))
    r7_pairs = {(f, c) for f, c, _, _, _, _, _ in REPOINT2}
    for p in sorted(SRC.glob('*.py')):
        for m in re.finditer(seal_rx, rd(p), re.M):
            assert (p.name in REPOINT and m.group(1) in REPOINT[p.name]) or (p.name, m.group(1)) in r7_pairs or \
                p.name in ONE_SHOT or p.name.endswith('_port.py'), (p.name, m.group(0))
    for f in ARCHIVE_SCORERS | set(ONE_SHOT) | set(MUTATION_SCRIPTS) | {MUTATION_SHP[0], MUTATION_SHP111[0],
                                                                        MUTATION_HERE[0]}:
        assert (SRC / f).is_file(), f
    # seal108.py .. seal111.py, close111.py and patch_s110/s111.py are not in the source (they live in
    # C:/kyty/s106_stage and docs/session-1NN/tools, or were never written): nothing to class.
    assert not [q for q in SRC.rglob('seal1*') if re.match(r'seal1(08|09|10|11)', q.name)], 'seal1NN found in the source'
    assert not list(SRC.rglob('patch_s110*')) and not list(SRC.rglob('patch_s111*')), 'patch_s11N found in the source'
    assert not list(SRC.rglob('close111*')), 'close111 found in the source'
    # Every top-level session-110 and session-111 Python file is classed.
    top110 = sorted(p.name for p in SRC.glob('*110*.py'))
    classed110 = sorted({'stl110.py', 'stl110b.py', 'shp110.py', 'test_stl110.py', 'test_stl110b.py', 'test_shp110.py',
                         'check110.py', 'mut_stl110.py', 'mut_stl110b.py', MUTATION_SHP[0], 'close110.py',
                         's110_port.py'} | set(GENERATORS_110))
    assert top110 == classed110, top110
    top111 = sorted(p.name for p in SRC.glob('*111*.py'))
    classed111 = sorted({'obs111.py', 'vds111.py', 'vds111b.py', 'shp111.py', 'test_obs111.py', 'test_vds111.py',
                         'test_vds111b.py', 'test_shp111.py', 'check111.py', MUTATION_HERE[0], MUTATION_SHP111[0],
                         's111_port.py'} | set(GENERATORS_111))
    assert top111 == classed111, top111
    for f, text_, basename in frozen_bare():
        assert rd(SRC / f).count(text_ % OLD) == 1 and basename in S105_NAMES + S107_NAMES + S108_NAMES + \
            S109_NAMES + S110_NAMES + S111_NAMES, f
    for mutant, scorer, n_lines in MUTANTS_107:
        a, b = rd(SRC / scorer).splitlines(), rd(SRC / mutant).splitlines()
        diff = [i for i, (x, y) in enumerate(zip(a, b), 1) if x != y]
        assert len(a) == len(b) and len(diff) == n_lines + 1, (mutant, diff)
        assert sum(1 for i in diff if a[i - 1].startswith('PRED = ') and b[i - 1].startswith('PRED = ')) == 1, mutant
    # Session 108's audit mutants: each is fam108.py with exactly its mutants_def.py replacement (CRLF) and the PRED
    # line as the mutants carry it (r6 reached fam108.py only); the worker copies are test_fam108.py with BASE moved
    # into audit108/fx_w<i> (the fixture folders stayed in C:/kyty/s110/audit108).
    fam = rd(SRC / 'fam108.py')
    assert '\r' not in fam and fam.count(FAM_PRED_R6 % (OLD, INHERITED)) == 1
    fam_mut = fam.replace(FAM_PRED_R6 % (OLD, INHERITED), FAM_PRED_MUT % OLD)
    table = mutant_table()
    for name, (old, new) in table.items():
        p = SRC / MUTANT_DIR / ('fam108_%s.py' % name)
        assert fam_mut.count(old) == 1 and lf(rd(p)) == fam_mut.replace(old, new), name
    got = sorted(p.relative_to(SRC).as_posix() for p in (SRC / MUTANT_DIR).glob('*.py'))
    assert got == sorted(mutant_names() + test_copy_names()), got
    test = rd(SRC / 'test_fam108.py')
    assert test.count(TEST_BASE_108) == 1 and '\r' not in test
    for i, f in enumerate(test_copy_names()):
        assert lf(rd(SRC / f)) == test.replace(TEST_BASE_108, "BASE = Path('%s/audit108/fx_w%d')" % (OLD, i)), f
        assert not (SRC / 'audit108' / ('fx_w%d' % i)).exists(), i
        assert (ROOT110 / 'audit108' / ('fx_w%d' % i)).is_dir(), i
    assert module_list(SRC / 'audit108/mutants108.py', 'MUTANTS') == table
    assert 'C:/kyty' not in rd(SRC / MUTANTS_DEF)
    # The source holds no fx_* folder at any depth (FIXTURE_DIRS is empty).
    fx = sorted(Path(d, x).relative_to(SRC).as_posix() for d, dirs, _ in os.walk(SRC) for x in dirs
                if x.startswith('fx_'))
    assert fx == sorted(FIXTURE_DIRS), fx
    # Session 109's audit mutants: each is its s111 scorer with the naive-only PRED line (r6 reached the scorer, not
    # the mutant) and exactly its newmut.py replacement, CRLF.
    for scorer, test_, name, old, new in mutant_table_109():
        s = rd(SRC / scorer)
        r6_line, mut_line = pred_r6(scorer, OLD)
        assert '\r' not in s and s.count(r6_line) == 1 and (SRC / test_).is_file(), (scorer, name)
        s_mut = s.replace(r6_line, mut_line)
        assert s_mut.count(old) == 1, (scorer, name)
        p = SRC / MUTANT_DIR_109 / ('%s__%s' % (name, scorer))
        b = p.read_bytes()
        assert b.count(b'\r\n') == b.count(b'\n') > 0 and lf(rd(p)) == s_mut.replace(old, new), name
    got = sorted(p.relative_to(SRC).as_posix() for p in (SRC / MUTANT_DIR_109).glob('*.py'))
    assert got == sorted(mutant_names_109()), got
    t = rd(SRC / AUDIT_MUTRUN_109[0])
    assert t.count(AUDIT_MUTRUN_109[1] % OLD) == 1 and "OUT = R / 'audit109' / 'mut'" in t
    # Session 110's audit mutants: each is the naive s110 -> s111 text of its C:/kyty/s110 original, which is the sealed
    # s110 scorer with exactly its newmut.py replacement (LF, written with newline='').
    for scorer, test_, name, old, new in mutant_table_110():
        s = rd(ROOT110 / scorer)
        assert sha(ROOT110 / scorer) == SEALS110_TOOLS[scorer] and s.count(old) == 1 and (SRC / test_).is_file(), name
        f = '%s/%s/%s' % (MUTANT_DIR_110, name, scorer)
        assert (ROOT110 / f).read_bytes() == s.replace(old, new).encode('utf-8'), name
        assert rd(SRC / f) == naive_prev(rd(ROOT110 / f)), name
        assert rd(SRC / f).count("PRED = '%s/pred/%s'" % (OLD, SEAL_OF_110[scorer])) == 1, name
    got = sorted(p.relative_to(SRC).as_posix() for p in (SRC / MUTANT_DIR_110).rglob('*.py')
                 if '__pycache__' not in p.parts)
    assert got == sorted(mutant_names_110()), got
    # Every audit110 Python file is classed.
    audit110_py = sorted(p.relative_to(SRC).as_posix() for p in (SRC / 'audit110').glob('*.py'))
    classed = sorted([f for f, _ in AUDIT110_DUMP_READERS] + [AUDIT110_CLOCKS[0], AUDIT110_PARSER[0],
                                                               AUDIT110_MUTRUN[0]] +
                     [f for f, _, _ in AUDIT110_LOG_READERS] + list(AUDIT110_PLAIN))
    assert audit110_py == classed, (audit110_py, classed)
    for f, text_ in AUDIT110_DUMP_READERS:
        assert rd(SRC / f).count(text_ % OLD) == 1, f
    for f, text_ in (AUDIT110_CLOCKS, AUDIT110_PARSER):
        assert rd(SRC / f).count(text_ % OLD) == 1, f
    for f, texts, _note in AUDIT110_LOG_READERS:
        assert all(rd(SRC / f).count(x % OLD) == 1 for x in texts), f
    f, texts, _dir = AUDIT110_MUTRUN
    assert all(rd(SRC / f).count(x % OLD) == 1 for x in texts), f
    for f in AUDIT110_PLAIN:
        assert naive(rd(SRC / f)) == rd(SRC / f), f
    # The audit110 parse dumps: all present, all under 5 MB (so carried); no file of audit110 reaches 5 MiB.
    for f in AUDIT110_DUMPS:
        assert (SRC / f).is_file() and (SRC / f).stat().st_size < 5 * 1000 * 1000, f
    assert sorted(p.relative_to(SRC).as_posix() for p in (SRC / 'audit110').glob('*.pkl')) == sorted(AUDIT110_DUMPS)
    assert not [p for p in (SRC / 'audit110').rglob('*') if p.is_file() and p.stat().st_size >= BIG]
    # ---- Session 111's audit ----
    # Every audit111 Python file is classed (top level, rerun/ and mut/).
    audit111_py = sorted(p.relative_to(SRC).as_posix() for p in (SRC / 'audit111').glob('*.py'))
    classed = sorted([f for f, _ in AUDIT111_DUMP_READERS] + [AUDIT111_PARSER[0], AUDIT111_CARRIED_READER[0],
                                                               AUDIT111_MUTRUN[0]] +
                     [f for f, _, _ in AUDIT111_LOG_READERS] + list(AUDIT111_PLAIN))
    assert audit111_py == classed, (audit111_py, classed)
    assert {f for f, _, _ in AUDIT111_EXTRA_READS} <= {f for f, _ in AUDIT111_DUMP_READERS}
    for f, text_ in AUDIT111_DUMP_READERS + (AUDIT111_PARSER, AUDIT111_CARRIED_READER):
        assert rd(SRC / f).count(text_ % OLD) == 1, f
    for f, texts, _note in AUDIT111_EXTRA_READS + AUDIT111_LOG_READERS:
        assert all(rd(SRC / f).count(x % OLD) == 1 for x in texts), f
    f, texts, _dir = AUDIT111_MUTRUN
    assert all(rd(SRC / f).count(x % OLD) == 1 for x in texts), f
    for f in AUDIT111_PLAIN:
        assert naive(rd(SRC / f)) == rd(SRC / f), f
    # The rerun copies: byte copies of the sealed top-level files (test_vds111b.py: BASE moved into rerun/).
    rerun_py = sorted(p.relative_to(SRC).as_posix() for p in (SRC / 'audit111/rerun').glob('*.py'))
    assert rerun_py == sorted(f for f, _, _ in AUDIT111_RERUN), rerun_py
    for f, orig, change in AUDIT111_RERUN:
        want = (SRC / orig).read_bytes()
        if change is not None:
            assert want.count(change[0].encode()) == 1, f
            want = want.replace(change[0].encode(), (change[1] % OLD).encode())
        assert (SRC / f).read_bytes() == want, f
    # The twenty mutants: each is its rerun scorer with exactly its newmut.py replacement, CRLF (write_text); the vds
    # mutants' fixture copies are the rerun test_vds111b.py with BASE moved into <name>/fx.
    rerun_test_vds = rd(SRC / 'audit111/rerun/test_vds111b.py')
    for target, name, old, new in mutant_table_111():
        scorer = AUDIT111_TARGETS[target]
        s = rd(SRC / 'audit111/rerun' / scorer)
        assert s.count(old) == 1, name
        p = SRC / MUTANT_DIR_111 / name / scorer
        b = p.read_bytes()
        assert b.count(b'\r\n') == b.count(b'\n') > 0 and lf(rd(p)) == s.replace(old, new), name
        assert (SRC / MUTANT_DIR_111 / name / 'out.txt').is_file(), name
        if target == 'vds':
            q = SRC / MUTANT_DIR_111 / name / 'test_vds111b.py'
            base = "Path('%s/audit111/rerun/fx_vds111b')" % OLD
            assert rerun_test_vds.count(base) == 1, name
            assert lf(rd(q)) == rerun_test_vds.replace(base, "Path('%s/%s/%s/fx')" % (OLD, MUTANT_DIR_111, name)), name
            assert q.read_bytes().count(b'\r\n') == q.read_bytes().count(b'\n'), name
    got = sorted(p.relative_to(SRC).as_posix() for p in (SRC / MUTANT_DIR_111).rglob('*.py')
                 if '__pycache__' not in p.parts)
    assert got == sorted(mutant_scorers_111() + mutant_tests_111()), got
    assert len(mutant_scorers_111()) == N_MUTANTS_111 and len(mutant_tests_111()) == 8
    # The audit111 parse dumps: exactly AUDIT111_DUMPS, none carried (next-session-112.md 1).
    assert sorted(p.relative_to(SRC).as_posix() for p in (SRC / 'audit111').glob('*.pkl')) == sorted(AUDIT111_DUMPS)
    assert not [p for p in (SRC / 'audit111').rglob('*.pkl') if p.parent != SRC / 'audit111']
    for f in AUDIT_ARGV:
        t = rd(SRC / f)
        assert 'C:/kyty' not in t and 'sys.argv[1], sys.argv[2]' in t, f
    for f, text_, _note in AUDIT_READS_DUMPS:
        assert rd(SRC / f).count(text_ % OLD) == 1, f
    f, texts = AUDIT_PARSER_109
    t = rd(SRC / f)
    assert all(t.count(x % OLD) == 1 for x in texts) and '\r\n' in t, f
    f, text_ = AUDIT_PROTOCOL_109
    t = rd(SRC / f)
    assert t.count(text_ % OLD) == 1 and "(R / ('stdout_%s.txt' % t))" in t, f
    for f in AUDIT_PLAIN_109:
        assert naive(rd(SRC / f)) == rd(SRC / f), f
    assert not list((SRC / 'audit108').glob('p_*.json')), 'session-108 parse dumps reappeared in the source'
    assert not (SRC / 'audit109' / 'parsed').exists(), 'session-109 parse dumps reappeared in the source'
    # Binaries at the source root: session 111's scored build and check111's build (both required) and any other
    # kyty_emulator_*.exe (a concurrent session-112 build).  The session-110 builds stay in C:/kyty/s110.
    for n, h in BINARIES111.items():
        assert (SRC / n).is_file() and n.endswith(SKIP_EXT) and n[len('kyty_emulator_'):-4] == h[:8], n
        assert sha(SRC / n) == h, n
    _f, exe, h = BUILD111
    assert (SRC / exe).is_file() and sha(SRC / exe) == h, exe
    assert not [p for p in SRC.rglob('*.exe') if p.parent != SRC], 'an .exe below the source root'
    for n, h in BINARIES110.items():
        assert not (SRC / n).exists() and (ROOT110 / n).is_file() and sha(ROOT110 / n) == h, n
    for n in BINARIES109:
        assert not (SRC / n).exists() and (ROOT109 / n).is_file() and sha(ROOT109 / n) == BINARIES109[n], n
    for n in BINARIES108:
        assert not (SRC / n).exists() and (ROOT108 / n).is_file(), n
    # Gates baseline: 1092 B / 99 names, dawalk=1 (shipped by session 104); dabatch, ctxtick, cspmemo,
    # cspfam, cspfree, daslot, daguard absent.
    g = SRC / 'gates_base.txt'
    assert g.stat().st_size == 1092 and sha(g) == GATES_SHA
    names = [x.split('=')[0] for x in rd(g).split() if '=' in x]
    assert len(names) == len(set(names)) == 99
    assert 'dawalk=1' in gate_tokens(g) and not {'ctxtick', 'dabatch', 'cspmemo', 'cspfam', 'cspfree', 'daslot',
                                                'daguard'} & set(names)
    assert g.read_bytes().count(b'\r\n') == 1 and g.read_bytes().endswith(b'\r\n')
    for f, size, h in ARCHIVE_DATA:
        assert (SRC / f).stat().st_size == size and sha(SRC / f) == h, f
    pre = gate_tokens(SRC / 'gates_base.pre104ship.txt')
    assert [x if x != 'dawalk=0' else 'dawalk=1' for x in pre] == gate_tokens(g), 'pre-ship differs beyond dawalk'
    for f, extra in PLUS_FILES:
        assert gate_tokens(SRC / f) == gate_tokens(g) + list(extra), f
        assert (SRC / f).read_bytes() == g.read_bytes()[:-2] + (' ' + ' '.join(extra)).encode() + b'\r\n', f
    for f, swaps, extra in IN_PLACE_FILES:
        want = g.read_bytes()[:-2]
        for a, b in swaps:
            assert (b' ' + want + b' ').count((' %s ' % a).encode()) == 1, (f, a)
            want = want.replace(a.encode(), b.encode())
        assert (SRC / f).read_bytes() == want + (' ' + ' '.join(extra)).encode() + b'\r\n', f
    # gates_slot2.txt: the appended smemocheck=1 follows the base's smemocheck=0 (the loader keeps the first).
    slot2 = gate_tokens(SRC / 'gates_slot2.txt')
    assert [x for x in slot2 if x.startswith('smemocheck=')] == ['smemocheck=0', 'smemocheck=1']
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
    for f, gate_file, h in GATES_INFO:
        t = rd(SRC / f)
        assert const(t, 'GATES_FILE') == '%s/%s' % (OLD, gate_file) and sha(SRC / gate_file) == h, f
        assert not re.search(r'^GATES_SHA\s*=', t, re.M), f
    for f in BINARY_PINNED:
        assert re.fullmatch(r'[0-9a-f]{64}', const(rd(SRC / f), 'BINARY_SHA')), f
    assert const(rd(SRC / 'fam108.py'), 'BINARY_SHA') == BINARIES108['kyty_emulator_fd1d0bd7.exe']
    for f, exe in BINARY109:
        assert const(rd(SRC / f), 'BINARY_SHA') == BINARIES109[exe], f
    for f, exe in BINARY110:
        assert const(rd(SRC / f), 'BINARY_SHA') == BINARIES110[exe], f
    for f, exe in BINARY111:
        assert const(rd(SRC / f), 'BINARY_SHA') == BINARIES111[exe], f
    for f, exe in BUILD_PINNED:
        assert const(rd(SRC / f), 'BUILD_SHA') == BINARIES108[exe], f
    assert const(rd(SRC / BUILD110[0]), 'BUILD_SHA') == BUILD110[2]
    assert const(rd(SRC / BUILD111[0]), 'BUILD_SHA') == BUILD111[2]
    for f, text_ in SYS_PATHS:
        assert rd(SRC / f).count(text_ % OLD) == 1, f
    text = rd(GATES)
    entry = r'\{\s*"KYTY_\w+",\s*"([a-z0-9]+)"'
    cpp = re.findall(entry, text)
    assert len(cpp) == len(set(cpp)) == GATES_CPP_ENTRIES, ('gates.cpp entry count changed: STOP and report', len(cpp))
    cut = text.index('KNOB_DEFINITIONS')
    split = (len(re.findall(entry, text[:cut])), len(re.findall(entry, text[cut:])))
    assert split == GATES_CPP_SPLIT, split
    assert re.findall(entry, text[:cut])[-1] == 'cbmove'
    assert re.findall(entry, text[cut:])[-6:] == ['ctxtick', 'cspmemo', 'cspfam', 'cspfree', 'daslot', 'daguard']
    for row in (CTXTICK_ROW, CSPMEMO_ROW, CSPFAM_ROW, CSPFREE_ROW, DASLOT_ROW, DAGUARD_ROW):
        assert text.count(row) == 1, row
    assert text.count(DABATCH_ROW) == 1 and text.index(DABATCH_ROW) > cut, 'dabatch default is not 8'
    assert len(ABSENT) == len(set(ABSENT)) == 42 == GATES_CPP_ENTRIES - 99
    assert set(ABSENT) == set(cpp) - set(names)
    assert not set(ABSENT) & set(names)
    assert all(not (SRC / f).exists() for f in NEW_SESSION)
    assert not [q for q in SRC.rglob('*') if q.name in NEW_SESSION]
    assert not any(d.is_dir() and d.name.startswith('design112') for d in SRC.iterdir())
    # Root-level names with a session-112 tag: only this port and a concurrent executor's build logs.
    s112_named = sorted(p.name for p in SRC.iterdir() if 's112' in p.name and p.name != 's112_port.py')
    assert all(CONCURRENT_RX.match(n) for n in s112_named), s112_named
    for tag, n in ROOT_TESTS:
        assert (Path('C:/kyty/s%d' % n) / ('log_%s.txt' % tag)).is_file(), tag
    assert not (ROOT109 / 'log_frf109.txt').exists()
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
    # Session-109 generators, as they read under the SOURCE root (their SRC_SHA pins name the s109 originals).
    t = rd(SRC / 'make_ent109b.py')
    assert "STAGE = Path('%s')" % REAL_STAGE in t and "(\"PRED = '%s/pred/01_ent109.md'\"" % OLD in t
    assert "PRED = 'C:/kyty/s109/pred/01_ent109.md'" in rd(STAGE_ENT109), 'stage ent109.py lost its anchor'
    t = rd(SRC / 'make_frf109.py')
    assert "else '%s/fam108.py'" % OLD in t and const(t, 'SRC_SHA') == sha(ROOT109 / 'fam108.py') != sha(SRC / 'fam108.py')
    assert "else '%s/frf109/frf109.py'" % REAL_STAGE in t
    t = rd(SRC / 'make_frm109.py')
    assert "ROOT = Path('%s')" % OLD in t and const(t, 'SRC_SHA') == sha(ROOT109 / 'frf109.py') != sha(SRC / 'frf109.py')
    assert t.index("assert sha(src) == SRC_SHA") < t.index('write_bytes')
    # Session-110 generators, as they read under the SOURCE root: their staging pins hold today.
    t = rd(SRC / 'make_stl110.py')
    assert "STAGE = Path('%s')" % REAL_STAGE in t and const(t, 'SRC_SHA') == sha(STAGE_ENT109B)
    assert "(\"ROOT = 'C:/kyty/s109'\", \"ROOT = '%s'\")" % OLD in t
    t = rd(SRC / 'make_test_stl110.py')
    assert naive(t) == t and const(t, 'SRC_SHA') == sha(STAGE_TEST_ENT109B)
    t = rd(SRC / 'make_stl110b.py')
    assert "derive('stl110.py', '%s', 'stl110b.py', [" % sha(STAGE_STL110) in t
    assert "(\"python %s/stl110.py\", \"python %s/stl110b.py\")" % (OLD, OLD) in t
    t = rd(SRC / 'make_shp110.py')
    assert const(t, 'SRC_SHA') == sha(STAGE_FRF109) and "else '%s'" % STAGE_FRF109.as_posix() in t
    assert "rep(\"PRODUCTION_ROOT = 'C:/kyty/s109'\", \"PRODUCTION_ROOT = '%s'\")" % OLD in t
    # Session-111 generators, as they read under the SOURCE root.
    t = rd(SRC / 'make_shp111.py')
    assert const(t, 'SRC_SHA') == sha(STAGE_SHP110) and "else '%s'" % STAGE_SHP110.as_posix() in t
    assert "else '%s'" % STAGE_SHP111.as_posix() in t
    assert "rep(\"PRODUCTION_ROOT = 'C:/kyty/s110'\", \"PRODUCTION_ROOT = '%s'\")" % OLD in t
    stop, _n, after = anchored_stop('make_shp111.py', rd(STAGE_SHP110), SRC)
    assert stop is None and stale_fresh_stop('make_shp111.py', after, SRC) is None, \
        'make_shp111.py no longer runs clean on its pinned staging source in the source'
    t = rd(SRC / 'make_vds111b.py')
    assert "STAGE = Path('%s')" % REAL_STAGE in t and 'SRC_SHA' not in t
    assert derive_stop('make_vds111b.py', rd(STAGE_VDS111), SRC, 0)[0] is None
    assert derive_stop('make_vds111b.py', rd(STAGE_TEST_VDS111), SRC, 1)[0] is None
    t = rd(SRC / 'make_check111.py')
    assert "Path('%s').read_bytes()" % CHECK110_ORIG.as_posix() in t
    assert "Path('%s/check111.py').write_bytes(" % OLD in t
    stop, _n, after = pairs_list_stop('make_check111.py', rd(CHECK110_ORIG), SRC)
    assert stop is None and after.encode('utf-8') == (SRC / 'check111.py').read_bytes(), \
        'make_check111.py no longer reproduces the source check111.py'
    for f, root_line, var, rm_line, audit_line, _basename, record in CLOSES:
        t = rd(SRC / f)
        assert t.count(root_line % OLD) == 1 and rm_line in t and audit_line in t, f
        assert t.index(audit_line) < t.index("\nedit(%s / 'FACTS.md', [" % var) < t.index('\nedit(RM, [')
        assert "open(%s / '%s', 'ab')" % (var, record) in t, f
    t = rd(SRC / 'ctx109.py')
    assert t.count("rd('C:/kyty/KytyPS5/docs/next-session-110.md')") == 1 and "'%s/FACTS.md'" % OLD not in t
    assert '`%s/FACTS.md`' % OLD in t
    for f, out, key, scorer_name in SELF_HASHED:
        j = json.loads(rd(SRC / out))
        assert j[key] == sha(SRC / f) == SEALS111_TOOLS.get(f, sha(SRC / f)), (f, out)
        assert j.get('scorer') == scorer_name, (f, out, j.get('scorer'))
    for f, out, key, root, scorer_name in SELF_HASHED_PRIOR:
        j = json.loads(rd(SRC / out))
        assert j[key] == sha(root / f) != sha(SRC / f), (f, out)
        if key == 'scorer_sha256':
            assert j.get('scorer') == scorer_name, (f, out, j.get('scorer'))
    stage = sorted(p.name for p in SRC.glob('*.py') if STAGE in rd(p) and not p.name.endswith('_port.py'))
    assert stage == sorted(STAGE_MENTIONS), stage
    real_stage = sorted(p.name for p in SRC.glob('*.py') if REAL_STAGE in rd(p) and not p.name.endswith('_port.py'))
    assert real_stage == sorted(STAGE_READERS), real_stage
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
    print('PRECONDITIONS PASS: 5 root constructs; %d sealed texts (%d land in prev111/pred, 2 stay '
          'in carried prev103/pred and prev100/pred); SEALS111.txt 5 texts + 21 tools (3 with the post-run note), '
          'SEALS110.txt 4 texts + 18 tools, SEALS109.txt 6 texts + 20 tools, SEALS108.txt 2 texts + 5 tools; %d live '
          'paths (%d files) + 10 expression paths (8 files); gates 1092 B / 99 names (sha 303a7849..., dawalk=1, no '
          'dabatch/ctxtick/cspmemo/cspfam/cspfree/daslot/daguard); gates.cpp 141 entries (111 gates + 30 knobs; dabatch '
          'default 8; cspfree default 1; daslot default 1; daguard last knob row, default 1); ABSENT 42'
          % (N_SEALED, N_LAND, N_R6_CONSTS, N_R6_FILES))


def predicted_exists(planned):
    """Paths (lower case, '/'-separated, relative to DST) that exist once main() has written the plan."""
    keys = [key for key, _, _, _ in planned] + [LEDGER_NAME]
    keys += ['prev111/%s' % f for f in DOCS_PRESENT]
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
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIR and not (rel == Path('.') and (d == 'pred' or d.startswith('design112'))))
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
    assert sorted({fixture_dir_of(k) for k in skipped.get('fixture-dir', [])}) == sorted(FIXTURE_DIRS)
    assert set(BINARIES111) | {BUILD111[1]} <= set(skipped.get('model', []))
    assert all(CONCURRENT_RX.match(k) for k in skipped.get('concurrent-112', []))
    assert skipped.get('doc', []) == list(DOCS_PRESENT)
    assert sorted(skipped.get('audit111-pkl', [])) == sorted(AUDIT111_DUMPS)
    assert set(AUDIT110_DUMPS) <= {key for key, _, _, _ in planned}
    # Stale s111 root literals may remain only in the seven chain files (one line each) and in the archive
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
    prev = DST / 'prev111'
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
    exes = sorted(p.name for p in SRC.glob('*.exe'))
    classes = {
        'archive_scorers_111': sorted(f for f in ARCHIVE_SCORERS if '111' in f),
        'one_shot_111': list(GENERATORS_111),
        'mutation_script_here_111': [MUTATION_HERE[0]],
        'mutation_script_root_anchors_111': [MUTATION_SHP111[0]],
        'shells_111': ['go111.sh', 'go111b.sh', 'go111v.sh'],
        'gate_files_111_archive': ['gates_obs111.txt', 'gates_slot1.txt', 'gates_slot2.txt', 'gates_slot2b.txt'],
        'audit111_mutants_frozen': mutant_scorers_111(),
        'audit111_mutant_fixture_copies': mutant_tests_111(),
        'audit111_rerun_copies_frozen': [f for f, _, _ in AUDIT111_RERUN],
        'audit111_reads_non_carried_dumps': [f for f, _ in AUDIT111_DUMP_READERS],
        'audit111_extra_non_carried_reads': [f for f, _, _ in AUDIT111_EXTRA_READS],
        'audit111_parser': [AUDIT111_PARSER[0]],
        'audit111_log_readers': [f for f, _, _ in AUDIT111_LOG_READERS],
        'audit111_reads_carried_output': [AUDIT111_CARRIED_READER[0]],
        'audit111_mutant_runner': [AUDIT111_MUTRUN[0]],
        'audit111_plain': list(AUDIT111_PLAIN),
        'audit111_dumps_not_carried': list(AUDIT111_DUMPS),
        'seals111_postrun_tools': list(SEALS111_POSTRUN),
        'absent_from_source': ['seal111.py', 'close111.py', 'patch_s111.py'],
    }
    payload = json.dumps({'source': OLD, 'destination': NEW, 'files': ledger,
        'carried_count': len(carried), 'skipped_count': n_skipped,
        'skipped_by_rule': {k: len(v) for k, v in sorted(skipped.items())},
        'not_carried_named': {'binaries': exes, 'fixture_dirs': sorted(FIXTURE_DIRS),
                              'audit111_dumps': sorted(skipped.get('audit111-pkl', [])),
                              'concurrent_112': sorted(skipped.get('concurrent-112', []))},
        'empty_source_folders': sorted(empty_dirs),
        'archive_scorers': sorted(ARCHIVE_SCORERS),
        'sealed_landing': ['%s/%s -> %s/%s' % (d, n, land, n) for d, n, _, _, land in SEALED],
        'sealed_counts': {'total': N_SEALED, 'landed_in_' + LAND: N_LAND,
                          'stay_in_walk_carried_folders': N_SEALED - N_LAND},
        'seals108_tools': dict(sorted(SEALS108_TOOLS.items())),
        'seals109_tools': dict(sorted(SEALS109_TOOLS.items())),
        'seals110_tools': dict(sorted(SEALS110_TOOLS.items())),
        'seals111_tools': dict(sorted(SEALS111_TOOLS.items())),
        'seals111_tool_notes': dict(sorted(TOOL_NOTES[SEALS_FILE].items())),
        'gates_cpp': {'entries': GATES_CPP_ENTRIES, 'gates': GATES_CPP_SPLIT[0], 'knobs': GATES_CPP_SPLIT[1],
                      'absent_from_gates_base': len(ABSENT), 'last_knob': 'daguard'},
        'prev111_docs': list(DOCS_PRESENT),
        'census': {k: list(v) for k, v in sorted(census_want().items()) if k not in FACTS_MENTIONS},
        'facts_mentions': sorted(FACTS_MENTIONS),
        'one_shot': sorted(ONE_SHOT),
        'classes_111': classes,
        'new_session_allowed': sorted(NEW_SESSION)}, indent=2) + '\n'
    # Bytes with LF line ends (Path.write_text on Windows would translate every newline to CRLF).
    (DST / LEDGER_NAME).write_bytes(payload.encode('utf-8'))
    assert b'\r' not in (DST / LEDGER_NAME).read_bytes()
    print('PORT DIAGNOSTIC: clean; carried=%d ledger=%d skipped=%d' % (len(carried), len(ledger), n_skipped))


def diagnostics(carried, ledger, skipped, empty_dirs):
    live = check_ledger({k: v['repairs'] for k, v in ledger.items()}, 'written')
    for tag, want in expected_ledger().items():
        print('LEDGER %s PASS: %s' % (tag, ', '.join(want)))
    ports = sorted(k for k in ledger if k.endswith('_port.py'))
    print('LEDGER r1 ARCHIVE PORTS (carried, never run): %d files: %s' % (len(ports), ', '.join(ports)))
    live = {k: ledger[k] for k in live}
    naive_regime = naive(rd(SRC / 'regime94.py'))
    blind = naive_regime.replace("'C:/kyty/s112', 'C:/kyty/s110'", "'C:/kyty/s112', 'C:/kyty/s111', 'C:/kyty/s110'")
    assert blind == naive_regime.replace(naive(regime(111)), regime(112))
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
        assert m and m.group(1) == chain(112, 75, True) and len(m.group(1).split(',')) == 38, f
    for f, (floor, _) in ARITH.items():
        assert rd(DST / f).count('range(112, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(DST / f).count(chain(112, floor)) == 1, f
    print('ADVANCE PASS: COMMA 38 roots; range(112, 70/66, -1); stg92 23, bda93 22, s94lib 21 roots; '
          'regime94 20 roots + s112')
    sealed = sealed_index()
    for f, names in REPOINT.items():
        t = rd(DST / f)
        for name in names:
            p = Path(const(t, name))
            assert p.parent == DST / LAND, (f, name, p)
            assert sha(p) == const(t, name + '_SHA') == const(rd(SRC / f), name + '_SHA')
    print('R6 PASS: %d constants in %d files -> %s (incl. obs111/vds111/vds111b/shp111.PRED -> their seals)'
          % (sum(len(v) for v in REPOINT.values()), len(REPOINT), LAND))
    for f in PRED_BYTES_FILES:
        t = rd(DST / f)
        assert int(re.search(r'^PRED_BYTES\s*=\s*(\d+)', t, re.M).group(1)) == Path(const(t, 'PRED')).stat().st_size, f
    print('R6 BYTES PASS: PRED_BYTES of %d files equal the landed texts' % len(PRED_BYTES_FILES))
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
        moved = sum(1 for x, y in zip(rd(SRC / f).splitlines(), t.splitlines()) if x != y)
        print('FIXTURE TEST, SEAL OVERRIDDEN, REPORT ONLY: %s loads the scorer named on argv, replaces PRED with a '
              'throwaway seal and writes under %s (outside the harness; not moved by the rewrite)%s'
              % (f, REAL_STAGE, '; the naive rewrite moved %d usage/synthetic line(s) to %s' % (moved, NEW)
                 if moved else ''))
    f, loader, override, stage, synthetic = FIXTURE_TEST_FRF
    t = rd(DST / f)
    assert loader in t and override in t and stage in t and t.count(synthetic % NEW) == 1 and f not in ledger, f
    assert rd(SRC / f).count(synthetic % OLD) == 1
    print('FIXTURE TEST, SYNTHETIC ROOT MOVED, REPORT ONLY: %s (scorer on argv, seal overridden, fixtures under '
          '%s/fx_frf109 or argv[2]); its one synthetic log line now reads %s (fixture data); never run'
          % (f, REAL_STAGE, synthetic % NEW))
    f, loader, override, stage, synthetic, consts = FIXTURE_TEST_SHP
    t = rd(DST / f)
    assert loader in t and override in t and stage in t and t.count(synthetic % NEW) == 1 and f not in ledger, f
    assert t.count(consts[0] % (NEW, NEW)) == 1 and t.count(consts[1] % NEW) == 1 and OLD not in t, f
    assert const(rd(DST / 'shp110.py'), 'PRED') == '%s/%s/03_shp110.md' % (NEW, LAND)
    print('FIXTURE TEST, SYNTHETIC ROOT AND CONSTANTS TABLE MOVED, REPORT ONLY: %s (scorer on argv, seal overridden, '
          'fixtures under %s/fx_shp110 or argv[2]); its synthetic line now reads %s and its CONSTANTS table expects '
          "PRODUCTION_ROOT %s, PRED %s/pred/03_shp110.md, GATES_FILE %s/gates_base.txt - the s112 shp110.py names "
          '%s/03_shp110.md after r6 (a report line, not a failing case: on the sealed copy it already read CONSTANTS '
          'DIFFER, PRED_SHA pinned); never run' % (f, REAL_STAGE, synthetic % NEW, NEW, NEW, NEW, LAND))
    f, loader, override, stage, synthetic, consts, fallback, n_old = FIXTURE_TEST_SHP111
    t = rd(DST / f)
    assert loader in t and override in t and stage in t and fallback in t and f not in ledger, f
    assert t.count(synthetic % NEW) == 1 and t.count(consts[0] % (NEW, NEW)) == 1 and t.count(consts[1] % NEW) == 1, f
    assert OLD not in t and t.count(NEW) == n_old, f
    assert const(rd(DST / 'shp111.py'), 'PRED') == '%s/%s/03_shp111.md' % (NEW, LAND)
    print('FIXTURE TEST, SYNTHETIC ROOT AND CONSTANTS TABLE MOVED, REPORT ONLY: %s (scorer on argv, seal overridden, '
          'fixtures under %s/shp111/fx or argv[2]; gates_base.txt copied from GATES_FILE or %s); its synthetic line now '
          'reads %s and its CONSTANTS table expects PRODUCTION_ROOT %s, PRED %s/pred/03_shp111.md, GATES_FILE '
          '%s/gates_base.txt - the s112 shp111.py names %s/03_shp111.md after r6 (the CONSTANTS case, which the audit '
          'recorded as the one by-design failure on the sealed copy, stays a report line); never run'
          % (f, REAL_STAGE, fallback.split("'")[1], synthetic % NEW, NEW, NEW, NEW, LAND))
    f, loader, override, base, consts, envs = FIXTURE_TEST_OBS111
    t = rd(DST / f)
    assert loader in t and override in t and base in t and f not in ledger and OLD not in t, f
    assert all(t.count(c % NEW) == 1 for c in consts) and t.count(envs[0] % NEW) == 1, f
    assert t.count(envs[1] % NEW.replace('/', '\\\\')) == 1, f
    assert const(rd(DST / 'obs111.py'), 'PRED') == '%s/%s/01_obs111.md' % (NEW, LAND)
    print('FIXTURE TEST, HERE-RELATIVE, CONSTANTS CHECK MOVED, REPORT ONLY: %s loads <its dir>/obs111.py (or argv), '
          'overrides its seal and writes fixtures under <its dir>/fx/<stem> (INSIDE the harness, removed at the end '
          'unless --keep); its CONSTANTS check expects PRODUCTION_ROOT %s, PRED %s/pred/01_obs111.md, GATES_FILE '
          '%s/gates_obs111.txt - the s112 obs111.py names %s/01_obs111.md after r6, so on the s112 copies CONSTANTS '
          'would FAIL; two fixture env values now name %s (fixture data); never run' % (f, NEW, NEW, NEW, LAND, NEW))
    for f in MUTATION_SCRIPTS:
        assert rd(DST / f) == rd(SRC / f) and f not in ledger, f
        print('MUTATION SCRIPT ON STAGING COPIES, REPORT ONLY: %s byte-identical (mutates and writes only under %s); '
              'never run' % (f, REAL_STAGE))
    f, texts = MUTATION_HERE
    assert rd(DST / f) == rd(SRC / f) and f not in ledger and all(x in rd(DST / f) for x in texts), f
    print('MUTATION SCRIPT, HERE-RELATIVE, REPORT ONLY: %s byte-identical (no root literal); in %s it would mutate the '
          's112 obs111.py (naive + r6) into %s/mutants and run the s112 test_obs111.py, whose CONSTANTS check already '
          'fails on the unmutated s112 copy (the control run would not read ALL OK); never run' % (f, NEW, NEW))
    for mut, stage_scorer, label in ((MUTATION_SHP, STAGE_SHP110, 'shp110'), (MUTATION_SHP111, STAGE_SHP111, 'shp111')):
        f, here, anchors = mut
        t = rd(DST / f)
        assert here in t and f not in ledger and all(t.count(a % NEW) == 1 for a in anchors) and OLD not in t, f
        stop, n_mut = mutant_anchor_stop(f, rd(stage_scorer))
        assert isinstance(stop, str) and stop != 'undetermined', stop
        print('MUTATION SCRIPT, ROOT-NAMED ANCHORS MOVED, REPORT ONLY: %s (scorer %s/%s/%s.py, not moved): its '
              'three sealed-constant mutants now anchor on %s texts, absent from the staging scorer; its anchor check '
              'would stop (SystemExit) at mutant %s of %d, after creating %s/%s/fx_mut and before any mutant is '
              'written; never run' % (f, REAL_STAGE, label, label, NEW, stop, n_mut, REAL_STAGE, label))
    assert len(list((DST / LAND).iterdir())) == N_LAND
    for d, n, size, h, land in SEALED:
        p = DST / land / n
        assert p.stat().st_size == size and sha(p) == h == sha(SRC / d / n), (d, n)
        assert p.read_bytes() == (SRC / d / n).read_bytes(), (d, n)
        print('SEALED PASS: %s/%s %d B %s' % (land, n, size, h))
    for folder, want in ((INHERITED, 60), (CARRIED109, 56), (CARRIED108, 50), (CARRIED107, 48), (CARRIED106, 45),
                         (CARRIED105, 42), (CARRIED104, 38), (CARRIED103, 34), (CARRIED102, 29), (CARRIED101, 20),
                         (OLDER, 18)):
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
    assert len(dst_folders) == 31
    for n in S111_NAMES:
        assert all(not (p / n).exists() for p in dst_folders) and (DST / LAND / n).is_file(), n
    elsewhere = sorted(q.relative_to(DST).as_posix() for q in DST.rglob('*')
                       if q.name in S111_NAMES and q.parent != DST / LAND)
    assert elsewhere == [], elsewhere
    print('NO COLLISION PASS: the five session-111 basenames exist only in %s (checked against all %d earlier pred/ '
          'folders and the whole destination)' % (LAND, len(dst_folders)))
    for folder, n, size, h in DRAFT_SHARED:
        p = DST / folder / n
        assert p.stat().st_size == size and sha(p) == h != sha(DST / LAND / n), (folder, n)
        print('DRAFT SHARES A SEAL BASENAME, REPORT ONLY: %s/%s (%d B, %s...) is session 102\'s draft, not a seal '
              'folder; %s/%s is session 106\'s seal (%s...)' % (folder, n, size, h[:8], LAND, n, sha(DST / LAND / n)[:8]))
    for record, tools in sorted(TOOL_RECORDS.items()):
        orig = RECORD_ROOT[record]
        for n, h in sorted(tools.items()):
            src_t = (SRC / n).read_bytes()
            rewritten = n.endswith('.py') and (n in ledger or naive(src_t.decode('utf-8')) != src_t.decode('utf-8'))
            assert (sha(DST / n) != sha(SRC / n)) == rewritten, (record, n)
            if not rewritten:
                assert (DST / n).read_bytes() == src_t, n
            assert sha(orig / n) == h, (record, n)
            note = TOOL_NOTES.get(record, {}).get(n)
            note = (' [%s]' % note) if note else ''
            if sha(SRC / n) == h:
                if rewritten:
                    print('SEALED TOOL REWRITTEN, REPORT ONLY: %s (%s %s...%s) - the s112 copy hashes %s... (naive%s); '
                          'the sealed original stays in %s' % (n, record, h[:8], note, sha(DST / n)[:8],
                                                               ' + r6' if n in ledger else '', OLD))
                else:
                    print('SEALED TOOL PASS: %s byte-exact (%s %s...%s)' % (n, record, h[:8], note))
            else:
                assert n in RECORD_REWRITTEN[record], (record, n)
                print('SEALED TOOL REWRITTEN BY AN EARLIER PORT%s, REPORT ONLY: %s (%s %s...) - the s112 copy hashes '
                      '%s...; the sealed original stays in %s' % (' AND AGAIN NOW' if rewritten else '', n, record,
                                                                  h[:8], sha(DST / n)[:8], orig.as_posix()))
    assert not list((DST / 'pred').iterdir())
    assert all(not (DST / f).exists() for f in DOCS + NEW_SESSION)
    assert not [q for q in DST.rglob('*') if q.name in NEW_SESSION]
    print('NEW SESSION NAMES PASS: none of %d session-112 names exists in %s or %s'
          % (len(NEW_SESSION), OLD, NEW))
    for f in DOCS:
        if (SRC / f).is_file():
            assert sha(SRC / f) == sha(DST / 'prev111' / f) and not (DST / f).exists()
        else:
            assert not (DST / 'prev111' / f).exists()
    assert sorted(p.name for p in (DST / 'prev111').iterdir()) == sorted(list(DOCS_PRESENT) + ['pred'])
    assert sha(DST / DESIGN109) == sha(SRC / DESIGN109) and not (DST / 'design109.md').exists()
    assert sha(DST / 'prev110' / 'FACTS.md') == sha(SRC / 'prev110' / 'FACTS.md')
    print('PREV111 PASS: %s + pred/ (%d texts); no README.md or PLAN.md in the source root; design109.md stays '
          'archived in the carried prev109/ and session 110\'s FACTS.md in the carried prev110/ (byte-exact)'
          % (', '.join(DOCS_PRESENT), N_LAND))
    assert (DST / 'm31_notes.md').is_file() and sha(DST / 'm31_notes.md') == sha(SRC / 'm31_notes.md')
    assert not (DST / 'prev111' / 'm31_notes.md').exists()
    print('SESSION-105 WORKING NOTE STAYS AT ROOT, REPORT ONLY: m31_notes.md')
    for f in (PREV_LEDGER,) + PREV_LEDGERS_DATA:
        assert sha(DST / f) == sha(SRC / f)
        print('PREVIOUS LEDGER CARRIED AS DATA: %s byte-exact' % f)
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
    for f, swaps, extra in IN_PLACE_FILES:
        want = gate_tokens(DST / 'gates_base.txt')
        for a, b in swaps:
            want = [b if x == a else x for x in want]
        assert gate_tokens(DST / f) == want + list(extra), f
        print('ARCHIVE GATE FILE, IN-PLACE ASSIGNMENT, PASS: %s = gates_base.txt with %s in place + %s'
              % (f, ', '.join('%s -> %s' % s for s in swaps), ' '.join(extra)))
    print('ARCHIVE GATE FILE, REPORT ONLY: gates_slot2.txt appends smemocheck=1 AFTER the base\'s smemocheck=0; the '
          'loader takes the first assignment, so the check stayed off in vds111 (the defect gates_slot2b.txt fixed)')
    for f, name, miss in ROOT_MOVED:
        assert const(rd(DST / f), name) == NEW and const(rd(SRC / f), name) == OLD, f
        print('ARCHIVE ROOT MOVED BY NAIVE REWRITE, REPORT ONLY: %s %s = %s (%s)' % (f, name, NEW, miss))
    for f, text_ in SYS_PATHS:
        assert rd(DST / f).count(text_ % NEW) == 1 and (DST / 'run_safety99.py').is_file()
        print('ARCHIVE SYS.PATH MOVED BY NAIVE REWRITE, REPORT ONLY: %s imports run_safety99 from %s (carried)' % (f, NEW))
    for f, text_, miss in INLINE_ROOT_MOVED:
        assert rd(DST / f).count(text_ % NEW) == 1, f
        print('ARCHIVE INLINE DEFAULT ROOT MOVED BY NAIVE REWRITE, REPORT ONLY: %s defaults to %s without --root (%s)'
              % (f, NEW, miss))
    for f, text_, miss in AUDIT_INLINE_MOVED:
        assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
        print('AUDIT EVIDENCE ROOT MOVED BY NAIVE REWRITE, REPORT ONLY: %s opens %s (%s); never run'
              % (f, (text_ % NEW).split("'")[1] if not f.endswith('rp_reasons.py') else NEW + '/log_frm109.txt', miss))
    for f, text_, note in AUDIT_READS_DUMPS:
        assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
        print('AUDIT EVIDENCE READS NON-CARRIED PARSE DUMPS, REPORT ONLY: %s reads %s%s; never run'
              % (f, re.search(r"'(C:/kyty/s112/[^']*)'", text_ % NEW).group(1), note))
    assert not list((DST / 'audit108').glob('p_*.json')) and not (DST / 'audit109' / 'parsed').exists()
    f, texts = AUDIT_PARSER_109
    t = rd(DST / f)
    assert all(t.count(x % NEW) == 1 for x in texts) and '\r\n' in t and f not in ledger, f
    print('AUDIT PARSER, REPORT ONLY: %s (CRLF kept) defaults to the logs of %s (not carried) and would write its dumps '
          'into %s/audit109/parsed (the originals stay in C:/kyty/s109/audit109/parsed); never run' % (f, NEW, NEW))
    f, text_ = AUDIT_PROTOCOL_109
    assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger and not list(DST.glob('stdout_*'))
    print('AUDIT PROTOCOL CHECK, REPORT ONLY: %s reads %s/gates_*.txt and <tag>.json (carried) and stdout_<tag>.txt '
          '(NOT carried; the session-109 ones stay in C:/kyty/s109); never run' % (f, NEW))
    f, text_, mut_dir = AUDIT_MUTRUN_109
    assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
    assert any(sha(DST / s) != sha(SRC / s) for s in {x for x, _, _, _, _ in mutant_table_109()})
    print('AUDIT MUTANT RUNNER, REPORT ONLY: %s (R = %s) would build its %d mutants from the s112 scorer copies (naive '
          '+ r6, not the audited s109 files) and OVERWRITE the carried %s/*.py; never run'
          % (f, NEW, N_MUTANTS_109, mut_dir))
    for f in AUDIT_PLAIN_109:
        assert rd(DST / f) == rd(SRC / f) and f not in ledger, f
    print('AUDIT HELPERS, NO ROOT LITERAL, REPORT ONLY: %s byte-identical' % ', '.join(AUDIT_PLAIN_109))
    for f in AUDIT_ARGV:
        assert rd(DST / f) == rd(SRC / f) and f not in ledger, f
        print('AUDIT PARSER, ARGV ONLY, REPORT ONLY: %s takes the log and the output on argv; byte-identical copy' % f)
    assert rd(DST / MUTANTS_DEF) == rd(SRC / MUTANTS_DEF)
    print('AUDIT DATA, REPORT ONLY: %s (the %d-mutant table; no root literal) byte-identical' % (MUTANTS_DEF, N_MUTANTS_108))
    for f, names_read, audited in AUDIT_READS_COPIES:
        t = rd(DST / f)
        assert all("'%s/%s'" % (NEW, n) in t for n in names_read), f
        assert any(sha(DST / n) != sha(audited / n) for n in names_read)
        print('AUDIT EVIDENCE READS CARRIED COPIES, REPORT ONLY: %s names %s/{%s}, which differ from the audited '
              '%s files; never run' % (f, NEW, ','.join(names_read), audited.as_posix()))
    # ---- Session 110's audit ----
    for f, text_ in AUDIT110_DUMP_READERS:
        assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
    for f in AUDIT110_DUMPS:
        assert sha(DST / f) == sha(SRC / f), f
    print('AUDIT110 READERS OF CARRIED DUMPS, REPORT ONLY: %s read %s/audit110/<tag>.pkl (abba_stats.py directly, the '
          'others via sys.path %s/audit110); the eight dumps (%s) are carried byte-exact, all under 5 MB; never run'
          % (', '.join(f for f, _ in AUDIT110_DUMP_READERS), NEW, NEW,
             ', '.join(Path(x).name for x in AUDIT110_DUMPS)))
    f, text_ = AUDIT110_CLOCKS
    assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
    assert (DST / 'cpuclk_shp110.csv').is_file() and (DST / 'gpuclk_shp110.csv').is_file()
    print('AUDIT110 CLOCK READER, REPORT ONLY: %s reads %s/{cpu,gpu}clk_shp110.csv (carried) and the frm109 CSVs in '
          'C:/kyty/s109 (unchanged); never run' % (f, NEW))
    f, text_ = AUDIT110_PARSER
    assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
    print('AUDIT110 PARSER, REPORT ONLY: %s takes the log on argv (logs not carried) and would OVERWRITE the carried '
          '%s/audit110/<tag>.pkl; never run' % (f, NEW))
    for f, texts, note in AUDIT110_LOG_READERS:
        assert all(rd(DST / f).count(x % NEW) == 1 for x in texts) and f not in ledger, f
        print('AUDIT110 LOG READER, REPORT ONLY: %s (R = %s/) reads %s; never run' % (f, NEW, note))
    assert not (DST / 'pred' / '01_stl110.md').exists()
    f, texts, mut_dir = AUDIT110_MUTRUN
    assert all(rd(DST / f).count(x % NEW) == 1 for x in texts) and f not in ledger, f
    assert sha(DST / 'stl110b.py') != sha(ROOT110 / 'stl110b.py') and sha(DST / 'shp110.py') != sha(ROOT110 / 'shp110.py')
    print('AUDIT110 MUTANT RUNNER, REPORT ONLY: %s (A = %s/audit110/mut/) would build its %d mutants from the s112 '
          'stl110b.py/shp110.py copies (naive + r6, not the audited s110 files), run the s112 tests on them and '
          'OVERWRITE the carried %s/<name>/*.py; never run' % (f, NEW, N_MUTANTS_110, mut_dir))
    for f in AUDIT110_PLAIN:
        assert rd(DST / f) == rd(SRC / f) and f not in ledger, f
    print('AUDIT110 HELPERS, NO ROOT LITERAL, REPORT ONLY: %s byte-identical' % ', '.join(AUDIT110_PLAIN))
    for scorer, _test, name, old, new in mutant_table_110():
        f = '%s/%s/%s' % (MUTANT_DIR_110, name, scorer)
        t = rd(DST / f)
        assert f not in ledger and t == naive(rd(SRC / f)) == naive(naive_prev(rd(ROOT110 / f))), f
        assert t.count("PRED = '%s/pred/%s'" % (NEW, SEAL_OF_110[scorer])) == 1, f
        assert not (DST / 'pred' / SEAL_OF_110[scorer]).exists() and (DST / LAND / SEAL_OF_110[scorer]).is_file()
    print('AUDIT MUTANTS 110, FROZEN, PRED LEFT DANGLING BY DESIGN, REPORT ONLY: %d files %s/<name>/<scorer>.py (LF) = '
          'the twice-rewritten text of the C:/kyty/s110 mutants of stl110b.py (12) / shp110.py (8); bare PRED '
          '%s/pred/<seal> (absent; r6 reaches the scorers, not the mutants), roots %s; they no longer hit the dangling '
          'census (the source s111/pred holds no session-110 text); never run' % (N_MUTANTS_110, MUTANT_DIR_110, NEW, NEW))
    # ---- Session 111's audit ----
    for f, text_ in AUDIT111_DUMP_READERS:
        assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
    for f in AUDIT111_DUMPS:
        assert not (DST / f).exists() and (SRC / f).is_file(), f
    assert not list((DST / 'audit111').glob('*.pkl'))
    print('AUDIT111 READERS OF NON-CARRIED DUMPS, REPORT ONLY: %s read %s/audit111/<tag>.pkl (abba.py directly, the '
          'others via sys.path %s/audit111); the nine dumps (%s) are NOT carried (next-session-112.md 1) and stay in '
          '%s/audit111 - FileNotFoundError at the first load; never run'
          % (', '.join(f for f, _ in AUDIT111_DUMP_READERS), NEW, NEW, ', '.join(Path(x).name for x in AUDIT111_DUMPS),
             OLD))
    for f, texts, note in AUDIT111_EXTRA_READS:
        assert all(rd(DST / f).count(x % NEW) == 1 for x in texts) and f not in ledger, f
        print('AUDIT111 READER, ALSO NON-CARRIED INPUTS, REPORT ONLY: %s also reads %s; never run' % (f, note))
    f, text_ = AUDIT111_PARSER
    assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger, f
    print('AUDIT111 PARSER, REPORT ONLY: %s takes the tag and the log on argv (logs not carried) and would write its '
          'dump into %s/audit111 (none carried there); never run' % (f, NEW))
    for f, texts, note in AUDIT111_LOG_READERS:
        assert all(rd(DST / f).count(x % NEW) == 1 for x in texts) and f not in ledger, f
        print('AUDIT111 LOG READER, REPORT ONLY: %s reads %s; never run' % (f, note))
    f, text_ = AUDIT111_CARRIED_READER
    assert rd(DST / f).count(text_ % NEW) == 1 and f not in ledger and (DST / 'audit111/runsum.txt').is_file(), f
    print('AUDIT111 READER OF A CARRIED OUTPUT, REPORT ONLY: %s reads %s/audit111/runsum.txt (carried byte-exact); '
          'never run' % (f, NEW))
    f, texts, mut_dir = AUDIT111_MUTRUN
    assert all(rd(DST / f).count(x % NEW) == 1 for x in texts) and f not in ledger, f
    print('AUDIT111 MUTANT RUNNER, REPORT ONLY: %s (A = %s/audit111) would build its %d mutants from the s112 '
          'audit111/rerun copies (naive rewrite of the sealed s111 files), run the rerun fixture suites on them and '
          'OVERWRITE the carried %s/<name>/; never run' % (f, NEW, N_MUTANTS_111, mut_dir))
    for f in AUDIT111_PLAIN:
        assert rd(DST / f) == rd(SRC / f) and f not in ledger, f
    print('AUDIT111 HELPERS, NO ROOT LITERAL, REPORT ONLY: %s byte-identical' % ', '.join(AUDIT111_PLAIN))
    for f, orig, _change in AUDIT111_RERUN:
        t = rd(DST / f)
        assert f not in ledger and t == naive(rd(SRC / f)), f
        if orig in SEAL_OF_111:
            assert t.count("PRED = '%s/pred/%s'" % (NEW, SEAL_OF_111[orig])) == 1, f
            assert not (DST / 'pred' / SEAL_OF_111[orig]).exists() and (DST / LAND / SEAL_OF_111[orig]).is_file()
    print('AUDIT111 RERUN COPIES, FROZEN, REPORT ONLY: %s = the naive s112 text of the sealed s111 files (r6 is keyed by '
          'the top-level name, so the scorer copies keep a bare PRED %s/pred/<seal> - absent - and the test copies '
          'their root-named CONSTANTS; test_vds111b.py\'s BASE names %s/audit111/rerun/fx_vds111b); never run'
          % (', '.join(Path(f).name for f, _, _ in AUDIT111_RERUN), NEW, NEW))
    rerun_test_vds = rd(DST / 'audit111/rerun/test_vds111b.py')
    for target, name, old, new in mutant_table_111():
        scorer = AUDIT111_TARGETS[target]
        f = '%s/%s/%s' % (MUTANT_DIR_111, name, scorer)
        t = rd(DST / f)
        assert f not in ledger and t == naive(rd(SRC / f)) and '\r\n' in t, f
        assert lf(t) == rd(DST / 'audit111/rerun' / scorer).replace(naive(old), naive(new)), f
        assert t.count("PRED = '%s/pred/%s'" % (NEW, SEAL_OF_111[scorer])) == 1, f
        if target == 'vds':
            q = '%s/%s/test_vds111b.py' % (MUTANT_DIR_111, name)
            tq = rd(DST / q)
            assert q not in ledger and tq == naive(rd(SRC / q)), q
            assert lf(tq) == rerun_test_vds.replace("Path('%s/audit111/rerun/fx_vds111b')" % NEW,
                                                    "Path('%s/%s/%s/fx')" % (NEW, MUTANT_DIR_111, name)), q
    for s, seal in SEAL_OF_111.items():
        assert not (DST / 'pred' / seal).exists() and (DST / LAND / seal).is_file(), s
    print('AUDIT MUTANTS 111, FROZEN, PRED LEFT DANGLING BY DESIGN, REPORT ONLY: %d files %s/<name>/<scorer>.py (CRLF '
          'kept) = the naive s112 text of the rerun shp111.py (12) / vds111b.py (8) with their one mutation each; bare '
          'PRED %s/pred/<seal> (absent; r6 reaches the scorers, not the mutants); the eight vds fixture copies name '
          'BASE %s/%s/<name>/fx; never run' % (N_MUTANTS_111, MUTANT_DIR_111, NEW, NEW, MUTANT_DIR_111))
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
    for f, gate_file, h in GATES_INFO:
        t = rd(DST / f)
        assert const(t, 'GATES_FILE') == '%s/%s' % (NEW, gate_file) and sha(DST / gate_file) == h, f
        print('ARCHIVE GATE FILE (INFORMATION ONLY) HOLDS: %s GATES_FILE = %s/%s (%s..., carried byte-exact)'
              % (f, NEW, gate_file, h[:8]))
    for f in BINARY_PINNED:
        b = const(rd(DST / f), 'BINARY_SHA')
        assert b == const(rd(SRC / f), 'BINARY_SHA'), f
        print('ARCHIVE BINARY PIN, REPORT ONLY: %s BINARY_SHA = %s... (its own run\'s build; never re-run)' % (f, b[:8]))
    for f, exe in BUILD_PINNED:
        b = const(rd(DST / f), 'BUILD_SHA')
        assert b == BINARIES108[exe] and not (DST / exe).exists() and sha(ROOT108 / exe) == b, f
        print('ARCHIVE BUILD PIN, REPORT ONLY: %s BUILD_SHA = %s... = %s/%s (the binary stays in s108, not carried)'
              % (f, b[:8], ROOT108.as_posix(), exe))
    for (f, exe, h), root in ((BUILD110, ROOT110), (BUILD111, SRC)):
        b = const(rd(DST / f), 'BUILD_SHA')
        assert b == h and not (DST / exe).exists() and sha(root / exe) == h, f
        print('ARCHIVE BUILD PIN, REPORT ONLY: %s BUILD_SHA = %s... = %s/%s (not carried)' % (f, b[:8], root.as_posix(),
                                                                                          exe))
    for f, exe in BINARY110:
        assert const(rd(DST / f), 'BINARY_SHA') == BINARIES110[exe] and sha(ROOT110 / exe) == BINARIES110[exe], f
    for f, exe in BINARY111:
        assert const(rd(DST / f), 'BINARY_SHA') == BINARIES111[exe] and sha(SRC / exe) == BINARIES111[exe], f
    for n, h in sorted(BINARIES111.items()):
        assert not (DST / n).exists() and sha(SRC / n) == h, n
    assert not list(DST.rglob('*.exe'))
    exes = sorted(p.name for p in SRC.glob('*.exe'))
    others = [n for n in exes if n not in BINARIES111 and n != BUILD111[1]]
    print('NOT CARRIED, BINARIES, REPORT ONLY: %s stay in %s (session 111\'s scored build %s; check111\'s build %s%s); '
          'the session-110 builds %s stay in %s'
          % (', '.join(exes), OLD, ', '.join(BINARIES111), BUILD111[1],
             ('; concurrent session-112 build(s) %s' % ', '.join(others)) if others else '',
             ', '.join(sorted(BINARIES110)), ROOT110.as_posix()))
    for f, out, key, scorer_name in SELF_HASHED:
        j = json.loads(rd(DST / out))
        assert j[key] == sha(SRC / f) != sha(DST / f), (f, out)
        print('SELF-HASH, REPORT ONLY: %s records %s %s... = the s111 %s%s; the s112 copy hashes %s... (naive%s)'
              % (out, key, j[key][:8], f, (" (its 'scorer' field reads %s)" % scorer_name) if scorer_name else '',
                 sha(DST / f)[:8], ' + r6' if f in ledger else ''))
    for f, out, key, root, _scorer in SELF_HASHED_PRIOR:
        j = json.loads(rd(DST / out))
        assert j[key] == sha(root / f) and j[key] not in (sha(SRC / f), sha(DST / f)), (f, out)
        print('SELF-HASH, REPORT ONLY: %s records %s %s... = the ORIGINAL %s/%s; neither the s111 nor the '
              's112 copy matches' % (out, key, j[key][:8], root.as_posix(), f))
    for f, text_ in TEST_LOG_MOVED:
        assert rd(DST / f).count(text_ % NEW) == 1 and not (DST / 'log_reg104.txt').exists(), f
        print('TEST REAL-LOG PATH MOVED BY NAIVE REWRITE, REPORT ONLY: %s reads %s/log_reg104.txt (log stays in s104)'
              % (f, NEW))
    assert not list(DST.rglob('log_*.txt'))
    for tag, n in ROOT_TESTS:
        if n == 111:
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
    # ctx109.py: its first write is docs/next-session-110.md, after an assert on an anchor it already replaced.
    tree = ast.parse(rd(DST / 'ctx109.py'))
    env = module_env(tree)
    n110 = rd(NEXT110).replace('\r\n', '\n')
    if n110.count(env['a']) != 1:
        assert n110.count(env['b']) == 1
        print('ONE-SHOT, REPORT ONLY: ctx109.py would stop at its first assert (its next-session-110.md anchor is '
              'already replaced) before any write; its texts name %s/FACTS.md' % NEW)
    else:
        print('ONE-SHOT, WARNING, REPORT ONLY: ctx109.py\'s next-session-110.md anchor matches once again; a re-run '
              'WOULD write the docs and the game contexts - never run it')
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
    # Session-109 generators.
    stop, n_pairs = derive_stop('make_ent109b.py', rd(STAGE_ENT109))
    assert isinstance(stop, int), stop
    t = rd(DST / 'make_ent109b.py')
    assert "(\"PRED = '%s/pred/01_ent109.md'\"" % NEW in t and "STAGE = Path('%s')" % REAL_STAGE in t
    print('ONE-SHOT GENERATOR, ANCHOR GONE, REPORT ONLY: make_ent109b.py derives from %s (outside the harness, '
          'not moved); after the naive rewrite its anchors name %s, so its first derive() would stop at pair %d of %d '
          '(AssertionError) before its first write (it writes only under %s)'
          % (STAGE_ENT109.as_posix(), NEW, stop, n_pairs, REAL_STAGE))
    t = rd(DST / 'make_frf109.py')
    pin = const(t, 'SRC_SHA')
    assert "else '%s/fam108.py'" % NEW in t and pin == sha(ROOT109 / 'fam108.py') != sha(DST / 'fam108.py')
    stop, n_calls, _ = anchored_stop('make_frf109.py', rd(ROOT109 / 'fam108.py'))
    assert isinstance(stop, int), stop
    print('ONE-SHOT GENERATOR, SHA PIN FAILS, REPORT ONLY: make_frf109.py defaults to %s/fam108.py (hashes %s..., '
          'pinned %s... = the C:/kyty/s109 copy): SystemExit before any edit; even on the s109 original its anchored '
          'chain would stop at call %d of %d (anchors now name %s) before its only write (default target under %s)'
          % (NEW, sha(DST / 'fam108.py')[:8], pin[:8], stop, n_calls, NEW, REAL_STAGE))
    t = rd(DST / 'make_frm109.py')
    pin = const(t, 'SRC_SHA')
    assert "ROOT = Path('%s')" % NEW in t and pin == sha(ROOT109 / 'frf109.py') != sha(DST / 'frf109.py')
    print('ONE-SHOT GENERATOR, SHA PIN FAILS, REPORT ONLY: make_frm109.py reads %s/frf109.py (hashes %s..., pinned '
          '%s... = the C:/kyty/s109 copy): AssertionError before its only write (%s/frm109.py)'
          % (NEW, sha(DST / 'frf109.py')[:8], pin[:8], NEW))
    # Session-110 generators (staging pins hold today).
    stop, n_pairs = pairs_stop('make_stl110.py', STAGE_ENT109B)
    assert stop is None or isinstance(stop, (int, tuple)), stop
    if stop is None:
        print('ONE-SHOT GENERATOR, WARNING, REPORT ONLY: make_stl110.py pins %s (sha still matches) and all %d anchors '
              '(they name C:/kyty/s109) still match it: a re-run WOULD OVERWRITE %s/stl110.py with a text naming %s '
              '(its replacements were moved by the rewrite) - never run it' % (STAGE_ENT109B.as_posix(), n_pairs,
                                                                             REAL_STAGE, NEW))
    else:
        print('ONE-SHOT GENERATOR, REPORT ONLY: make_stl110.py would stop at %s of %d pairs before its write'
              % (stop, n_pairs))
    stop, n_pairs = pairs_stop('make_test_stl110.py', STAGE_TEST_ENT109B, tag_anchor="'ent109b_")
    assert rd(DST / 'make_test_stl110.py') == rd(SRC / 'make_test_stl110.py')
    if stop is None:
        print('ONE-SHOT GENERATOR, WARNING, REPORT ONLY: make_test_stl110.py is byte-identical (no root literal); its '
              'pin on %s still holds and all %d anchors match: a re-run WOULD rewrite %s/test_stl110.py (the same '
              'bytes, the generator is byte-reproducible) - never run it' % (STAGE_TEST_ENT109B.as_posix(), n_pairs,
                                                                           REAL_STAGE))
    else:
        print('ONE-SHOT GENERATOR, REPORT ONLY: make_test_stl110.py would stop at %s of %d pairs before its write'
              % (stop, n_pairs))
    stop, n_pairs, src_name, dst_name = derive4_stop('make_stl110b.py')
    assert isinstance(stop, int), stop
    print('ONE-SHOT GENERATOR, ANCHOR GONE, REPORT ONLY: make_stl110b.py derives %s/%s from %s/%s (pin holds); after '
          'the naive rewrite its anchors name %s, so its first derive() would stop at pair %d of %d (AssertionError) '
          'before its first write (it writes only under %s)'
          % (REAL_STAGE, dst_name, REAL_STAGE, src_name, NEW, stop, n_pairs, REAL_STAGE))
    for gen, stage_src, stage_dst in (('make_shp110.py', STAGE_FRF109, STAGE_SHP110),
                                      ('make_shp111.py', STAGE_SHP110, STAGE_SHP111)):
        t = rd(DST / gen)
        assert const(t, 'SRC_SHA') == sha(stage_src)
        stop, n_calls, text_after = anchored_stop(gen, rd(stage_src))
        guard = stale_fresh_stop(gen, text_after) if stop is None else None
        if stop is None and guard is None:
            print('ONE-SHOT GENERATOR, WARNING, REPORT ONLY: %s pins %s (sha still matches); all %d rep()/keep() '
                  'anchors still match and its stale/fresh guards pass: a re-run WOULD OVERWRITE %s (the staging '
                  'scorer a mutation script mutates) with a text naming %s - never run it'
                  % (gen, stage_src.as_posix(), n_calls, stage_dst.as_posix(), NEW))
        else:
            print('ONE-SHOT GENERATOR, REPORT ONLY: %s would stop (%s of %d calls; guard %s) before its write'
                  % (gen, stop, n_calls, guard))
    # Session-111 generators without a pin.
    t = rd(DST / 'make_vds111b.py')
    assert "STAGE = Path('%s')" % REAL_STAGE in t and "(\"PRED = '%s/pred/02_vds111.md'\"" % NEW in t
    stop, n_pairs = derive_stop('make_vds111b.py', rd(STAGE_VDS111))
    assert isinstance(stop, int), stop
    print('ONE-SHOT GENERATOR, ANCHOR GONE, REPORT ONLY: make_vds111b.py derives %s/vds111b.py and test_vds111b.py from '
          'the staging vds111.py / test_vds111.py (no sha pin; not moved); after the naive rewrite its anchors name %s, '
          'so its first derive() would stop at pair %d of %d (AssertionError) before its first write (it writes only '
          'under %s)' % (REAL_STAGE, NEW, stop, n_pairs, REAL_STAGE))
    t = rd(DST / 'make_check111.py')
    assert "Path('%s/check111.py').write_bytes(" % NEW in t and "Path('%s').read_bytes()" % CHECK110_ORIG.as_posix() in t
    stop, n_pairs, after = pairs_list_stop('make_check111.py', rd(CHECK110_ORIG))
    if stop is None:
        same = after.encode('utf-8') == (DST / 'check111.py').read_bytes()
        print('ONE-SHOT GENERATOR, WARNING, REPORT ONLY: make_check111.py reads %s (the s110 original, not moved) and '
              'all %d anchors still match: a re-run WOULD REWRITE %s/check111.py - %s - never run it'
              % (CHECK110_ORIG.as_posix(), n_pairs, NEW,
                 'with the same bytes as the carried copy (the generator is byte-reproducible after the rewrite)'
                 if same else 'with bytes that DIFFER from the carried copy'))
    else:
        print('ONE-SHOT GENERATOR, REPORT ONLY: make_check111.py would stop at pair %s of %d before its write'
              % (stop, n_pairs))
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
    for f, root_line, var, rm_line, audit_line, basename, record in CLOSES:
        t = rd(DST / f)
        assert t.count(root_line % NEW) == 1 and rm_line in t and audit_line in t and f not in ledger
        assert not (DST / 'pred' / basename).exists() and not (DST / 'FACTS.md').exists()
        stop, n_pairs = edit_stop(f)
        print('ONE-SHOT CLOSE, REPORT ONLY: %s (%s = %s) opens %s/%s for append and then hashes %s/pred/%s (absent): '
              'FileNotFoundError before a byte is written; its FACTS edit targets %s/FACTS.md (absent; FACTS.md is in '
              'prev111/); its ROADMAP edit %s against the current ROADMAP; never run'
              % (f, var, NEW, NEW, record, NEW, basename, NEW,
                 ('would stop at pair %d of %d' % (stop, n_pairs)) if isinstance(stop, int)
                 else ('WOULD match all %d pairs (WARNING)' % n_pairs if stop is None else 'is undetermined after a '
                       'matching pair (WARNING)')))
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
        print('AUDIT MUTANT, REPORT ONLY: %s differs from the s112 %s in its %d mutated line(s) plus the PRED line '
              '(r6 reaches the scorer, not the mutant); never run' % (mutant, scorer, n_lines))
    # Session 108's audit mutants and worker copies after the port.
    fam_naive = naive(rd(SRC / 'fam108.py'))
    fam_mut = fam_naive.replace(FAM_PRED_R6 % (NEW, INHERITED), FAM_PRED_MUT % NEW)
    assert fam_mut != fam_naive
    for name, (old, new) in sorted(mutant_table().items()):
        f = '%s/fam108_%s.py' % (MUTANT_DIR, name)
        t = rd(DST / f)
        assert f not in ledger and lf(t) == fam_mut.replace(old, new) and '\r\n' in t, f
        assert t.count(FAM_PRED_MUT % NEW) == 1 and const(t, 'PRODUCTION_ROOT') == NEW, f
        assert const(t, 'GATES_FILE') == NEW + '/gates_base.txt', f
    assert not (DST / 'pred' / '01_cspfam.md').exists() and (DST / LAND / '01_cspfam.md').is_file()
    print('AUDIT MUTANTS 108, FROZEN, PRED LEFT DANGLING BY DESIGN, REPORT ONLY: %d files %s/fam108_<name>.py (CRLF '
          'kept) = the naive s112 fam108 text with their one mutation each and the unrepaired bare PRED '
          '%s/pred/01_cspfam.md (absent); never run' % (N_MUTANTS_108, MUTANT_DIR, NEW))
    test_dst = rd(DST / 'test_fam108.py')
    for i, f in enumerate(test_copy_names()):
        t = rd(DST / f)
        assert f not in ledger and '\r\n' in t, f
        assert lf(t) == test_dst.replace(TEST_BASE_108, "BASE = Path('%s/audit108/fx_w%d')" % (NEW, i)), f
        assert not (DST / 'audit108' / ('fx_w%d' % i)).exists() and not (SRC / 'audit108' / ('fx_w%d' % i)).exists(), i
        assert (ROOT110 / 'audit108' / ('fx_w%d' % i)).is_dir(), i
    print('AUDIT WORKER COPIES 108, FIXTURE FOLDER NOT CARRIED, REPORT ONLY: %d files %s/test_fam108_w<i>.py (CRLF '
          'kept) = the s112 test_fam108.py with BASE %s/audit108/fx_w<i>; the fx_w<i> folders stay in '
          '%s/audit108 (left there by the 111 port; a run would recreate them); they no longer hit the dangling '
          'census; never run' % (N_TEST_COPIES_108, MUTANT_DIR, NEW, ROOT110.as_posix()))
    # Session 109's audit mutants after the port (naive only; they already named s111/pred/<seal>, absent in s111).
    for scorer, _test, name, old, new in mutant_table_109():
        f = '%s/%s__%s' % (MUTANT_DIR_109, name, scorer)
        t = rd(DST / f)
        assert f not in ledger and '\r\n' in t and t == naive(rd(SRC / f)), f
        assert t.count("PRED = '%s/pred/%s'" % (NEW, SEAL_OF[scorer])) == 1, f
        r6_line, mut_line = pred_r6(scorer, NEW)
        assert lf(t) == naive(rd(SRC / scorer)).replace(r6_line, mut_line).replace(naive(old), naive(new)), f
    for s in SEAL_OF:
        if s != 'frf109.py':
            assert not (DST / 'pred' / SEAL_OF[s]).exists() and (DST / LAND / SEAL_OF[s]).is_file()
    print('AUDIT MUTANTS 109, FROZEN, PRED LEFT DANGLING BY DESIGN, REPORT ONLY: %d files %s/<name>__<scorer>.py (CRLF '
          'kept) = the naive s112 text of ent109/ent109b/vfy109/frm109 with their one mutation each; bare PRED '
          '%s/pred/<seal> (absent; r6 reaches the scorers, not the mutants), roots %s; never run'
          % (N_MUTANTS_109, MUTANT_DIR_109, NEW, NEW))
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
    print('DANGLING BY REWRITE, CLASSED ABOVE, REPORT ONLY: the %d session-111 audit mutants name %s/pred/<seal>'
          % (N_MUTANTS_111, NEW))
    for f in FACTS_MENTIONS:
        assert f not in ledger, f
    print('FACTS.md MENTION MOVED BY NAIVE REWRITE, REPORT ONLY: %d files name %s/FACTS.md (the source '
          'root\'s FACTS.md is archived as prev111/FACTS.md; session 112 writes its own): %s'
          % (len(FACTS_MENTIONS), NEW, ', '.join(FACTS_MENTIONS)))
    roots = ast.literal_eval(re.search(r'^ROOTS = (.+)$', rd(DST / 's94lib.py'), re.M).group(1))
    assert roots == tuple('C:/kyty/s%d' % i for i in range(112, 91, -1))
    for tag, n in ROOT_TESTS:
        found = next((r for r in roots if (Path(r) / ('log_%s.txt' % tag)).is_file()), None)
        assert found == 'C:/kyty/s%d' % n, (tag, found)
        print('ROOT PASS: %s -> %s' % (tag, found))
    assert rd(DST / 'regime94.py').count(regime(112)) == 1
    for tag, n in ROOT_TESTS:
        if n < 93:
            continue
        found = next((r for r in roots[:-1] if (Path(r) / ('log_%s.txt' % tag)).is_file()), NEW)
        assert found == 'C:/kyty/s%d' % n
    assert next((r for r in roots[:-1] if (Path(r) / 'log_nosuch112.txt').is_file()), NEW) == NEW
    stale = []
    for p in DST.rglob('*.py'):
        if p.name.endswith('_port.py'):
            continue
        t = rd(p)
        assert 'C:\\kyty\\s111' not in t and 'C:\\\\kyty\\\\s111' not in t and '/c/kyty/s111' not in t, p
        hits_ = [i for i, line in enumerate(t.splitlines(), 1) if OLD in line]
        if hits_:
            stale.append(p.relative_to(DST).as_posix())
            assert len(hits_) == 1, (p.name, hits_)
    assert sorted(stale) == sorted(list(COMMA) + list(TUPLES) + ['regime94.py'] + list(R1_ARCHIVE)), stale
    print('STALE %s PASS: only in the chain files (%s) and the archive verifier %s, one line each'
          % (OLD, ', '.join(sorted(list(COMMA) + list(TUPLES) + ['regime94.py'])), R1_ARCHIVE[0]))
    leaked = [p.relative_to(DST).as_posix() for p in DST.rglob('*') if p.is_file() and
              (p.name.startswith(('log_', 'stdout_', 'rec_')) or p.name.endswith(SKIP_EXT) or p.stat().st_size >= BIG
               or fixture_dir_of(p.relative_to(DST).as_posix()) is not None or CONCURRENT_RX.match(p.name)
               or AUDIT111_PKL_RX.match(p.relative_to(DST).as_posix()))]
    assert not leaked, leaked
    assert not [p for p in DST.rglob('fx_*') if p.is_dir()], 'a fixture folder was carried'
    big_in_dirs = sorted(k for k in skipped.get('model', []) if '/' in k and (SRC / k).stat().st_size >= BIG
                         and not k.split('/')[-1].startswith(SKIP_PREFIX) and not k.endswith(SKIP_EXT))
    print('SKIPPED >= 5 MiB INSIDE CARRIED FOLDERS (not log/stdout/rec/binary), REPORT ONLY: %d files: %s'
          % (len(big_in_dirs), ', '.join(big_in_dirs)))
    print('NOT CARRIED, AUDIT111 PARSE DUMPS (next-session-112.md 1), REPORT ONLY: %d files stay in %s/audit111: %s'
          % (len(skipped.get('audit111-pkl', [])), OLD, ', '.join(Path(k).name for k in skipped.get('audit111-pkl', []))))
    print('NOT CARRIED, FIXTURE FOLDERS fx_* (next-session-112.md 1), REPORT ONLY: %d folders in the source%s'
          % (len(FIXTURE_DIRS), (': ' + ', '.join(FIXTURE_DIRS)) if FIXTURE_DIRS else ''))
    print('NOT CARRIED, SESSION-112 FILES A CONCURRENT EXECUTOR WROTE INTO THE SOURCE ROOT, REPORT ONLY: %s'
          % (', '.join(skipped.get('concurrent-112', [])) or 'none'))
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
