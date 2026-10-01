#!/usr/bin/env python3
"""sc144.py - the scorer of the SCENE_OK series sc144 (session 144 step 0, HPP-330; ROADMAP "SESSION 122" item 254 (e),
(k)(1)-(7); brief docs/next-session-144.md): the port of sc143.py (session 143 step 0 HPP-297, link 1b HPP-321) with the
reading of sc143.py after items 242, 246 and NO change of its constants.  Profiles: 144 (the default), 143 (P143: prints
exactly what sc143.py printed - the regression on the 20 logs of s143, --regress143) and 142 (P142: --regress142).
Session 144 (item 254 (k)(1)-(2)), 33 tags in this order, one call each:
  w144_00          the control W on Sky Garden (underwater_aerial_garden); it is no SCENE_OK pair (Sky Garden has its
                   SCENE_OK of s142) - its rows decide the control stop of item 254 (k)(4);
  w144_01..w144_08 the W of the eight sc143 levels whose V rows passed (spring_punch_sky_aztec, booster_construction,
                   mini_astro_clock_tower, path_maker_mana_tree, spring_punch_monster_cave, gulliver_island,
                   booster_magic_lamp, rocket_space_station); the V of each pair is v143_NN of SESSION 143 (v143_01..06,
                   v143_09, v143_10), read from C:/kyty/s143 with the chain name go143a, the seal pred/02_sc143.md (its
                   sha256 now) and the log sha256 against C:/kyty/s143/step2/times.txt (item 254 (e): the cross-session
                   pair); its sheet row is "viewed" by item 254 (a) whatever --sheet says;
  v144_NN/w144_NN  NN = 09..20, V then W per level: rocket_hourglass, pot_treasure_cave, bumper_enemy_snowy_canyon,
                   big_hand_pirate_island, timestop_casino, ice_iceberg, sponge_dirty_bath, hoover_beach,
                   volcano_mountain, voxel_world, enemy_gorilla, mini_giants_garden (last).  These V are REPEATED
                   entries (item 254 (k)(2)): the census (map rows, forms B5 / B5a / B33) of this profile reads them only
                   and is printed with the mark "repeated entry", apart from the cold entries of s142 / s143.
The W form (item 254 (e)): every W runs with --vulkan-validation true AND KYTY_PIPELINE_PRECACHE=0.  The scorer checks it
by a positive control in the admission of every tag of profile 144: a W needs KYTY_PIPELINE_PRECACHE=0 in its json env
and NO line "PipelinePrecache: <N> recipes ->" in its log and emulator stdout (the stdout is the executor's addition);
a V needs no KYTY_PIPELINE_PRECACHE in its env and >= 1 such line in its log.  A violation fails the admission of the tag
(the tag FAILs: rc 1 of --tag, its SCENE_OK NO).  Note: a W stopped DURING the startup precache has no such line either
(the w143 logs) - the env term is what tells the form there.
Stop rules (item 254 (k)(4)), --stop-check <tag> rc 5:
  control  the control W w144_00 was made and stopped: by the letter a death marker (log, stdout, hold_exit / ENDED /
           exited) or a [Vulkan][E] line; the executor's reading stops on ANY failing W row of SCENE_OK or of its
           admission (the W form is item 254 (k)(7): "the cost of a form error is a stop after one tag"), on a missing
           log and on an attempt without json - both readings are printed, the gate uses the executor's (a stop is a
           question to the lead, never a run);
  W        two W in a row (the made W tags of SEQ, control included, V in between ignored) with the same stop key: the
           key of a W stopped before the first line carrying "GuestOut" = "<class> <kind>" of its first death marker in
           the order of item 224 (a)(1) among the log markers before that line (no such line in the log: every marker,
           then hold_exit / ENDED / exited); a W without such a stop (it reached the game, or stopped without a marker)
           has no key and breaks the run;
  V        three census V in a row NOT_ENTERED with one marker (item 221 (g)(4), as sc143).
  --stop-check reads the control W, the last two made W and the last three made census V before the tag (an earlier
  stop refused the call right after it, and the order rule of go144a.sh refuses every later call).
"Frame with a skipped draw" = the number of DISTINCT frame= ids of the "AsyncPipelines: skipped draw" lines (debt D-7).
Usage (profile 144; ASCII output; logs read in binary chunks):
    python sc144.py --tag <tag>                                 score one run (json in runs144/<tag>.score.json)
    python sc144.py --summary [--sheet viewed|not-viewed] [--sheet-tags v144_09,...]
    python sc144.py --stop-check <tag>                          rc 5 when a stop rule of item 254 (k)(4) stands
    python sc144.py --check-seal                                every sha line of pred/01_sc144.md against its file
    python sc144.py --calib | --check1b                         as sc143.py
    python sc144.py --regress143                                profile 143 on the 20 s143 logs against summary143_viewed.txt
    python sc144.py --regress142                                profile 142 on the 12 s142 logs against summary142_viewed.txt
Session 143 header (carried; profile 143):
sc143.py - the scorer of the SCENE_OK series sc143 (session 143 step 0, HPP-297; ROADMAP "SESSION 122" item 231 (i)(1)-(6);
brief docs/next-session-143.md): the port of sc142.py (session 142, HPP-277, link 1b HPP-282) with the reading of sc142.py
after item 224 and NO change of its constants; the one generalisation is SCENE_OK per level over the V/W pair of that level.
Session 143: ten never-entered main levels in the order of item 231 (i)(1), two tags per level, V then W (item 231 (i)(2)):
  v143_NN - -lvl entry on the installed 9235a7ac with the shipped defaults, the first entry of the level, video, hold 330 s
            wall; it is BOTH the census entry of the level (map row (A), forms B5 / B5a / B33, item 231 (i)(3)) and the V of
            its SCENE_OK;
  w143_NN - the same entry with --vulkan-validation true, hold 310 s, no video; the W of its SCENE_OK.
SCENE_OK of a level reads ONLY its own V and W (the tags of PAIRS; a json whose guest args name another level is not
admitted and the pair row fails); a level with a missing V or W, or a W stopped early, is NO.
Profile 142 (--regress142): the same code with the tags, seal, chain name and roots of session 142 must print exactly
C:/kyty/s142/step4/summary142_viewed.txt from the 12 logs of session 142 (the regression of item 231 (i)(4)); the lines
new in session 143 (the pair row, the W 310 s info, B33, the levels line, the K3 hold of 120 s) are printed in profile 143
only.
Session 142 reading (unchanged):
Reading of one entry (item 221 (g)(2), item 223 (a), item 224 (a)):
  entry            - the line "GuestOut: Level has started: <level>" of the target level (exact name, first such line).
  scene change     - any later "GuestOut: Level has started:" line (another level, the same level again, an empty name)
                     (item 224 (a)(7)): the rows after it are printed apart and not classified for the scene of -lvl.
  first scene frame- the first FrameTrace row after the entry line with draws >= 100 (item 218 (g)).  Its dt is the tail
                     of the load: it is NOT in K2, NOT in K3 and NOT in the entry window (item 221 (v)).
  entry window     - the 599 presented frames (FrameTrace rows) after the first scene frame (item 221 (v));
  hold             - every later row (before a scene change).
  K2               - a row after the first scene frame with dt_us >= 1 000 000 (item 217 (b)); also a hang marker
                     (GpuHangAbort:, ErrorDeviceLost) and a hold whose last 5 s had no FrameTrace row (ft_tail = 0 of
                     <tag>.json, item 223 (a)(2)).
  K3               - a row with 100 000 <= dt_us < 1 000 000 after the first scene frame: in the entry window with the
                     note "no warm base" (a never-entered level has no warm log, item 218 (g)), and on the hold.
  death markers    - item 128 (g) / 89 (g): GpuHangAbort:, ErrorDeviceLost (class K2), Unhandled exception:, and item
                     218 (d)(2): "--- Fatal Error ---", "--- Error ---" (class K1) - in the emulator log and in its stdout;
                     the attempt markers hold_exit / the ENDED line / exited (class K1).
  ORDER (item 224 (a)(1)): the log markers by their position in the log, then the markers of the emulator stdout by their
                     position there, then the attempt markers.  The outcome class is the class of the FIRST marker in
                     that order (a hang before a crash is K2: the crash is its consequence); the stop key is its kind.
  outcome (census) - NOT_ENTERED (no entry line) / K1 or K2 (the first death marker; else hold_exit, ENDED, exited -> K1;
                     else a frame dt >= 1 s or the tail stall -> K2) / HOLDS_120 (entered, attempt ok, hold_s >= 120,
                     sum dt_us of the rows after the entry line >= 120 s, item 224 (a)(4)) / NOT_EVALUABLE with a reason
                     (no first scene frame; no stable (<attempt outcome>); hold_s < 120; presented < 120 s; scene change).
                     With a scene change only the log markers and K2 frames BEFORE it decide; otherwise NOT_EVALUABLE.
  per-entry prints - "AsyncPipelines: skipped draw" lines and frames (counted, NOT fatal here: form B5 under measurement);
                     "opcode is not implemented" by family/opcode minus the base profile 96/1/4 (B26, B7);
                     "=== Stubbed function" with the name (B9); PriorityStall: us > 50 000 (B3b); BvhLoopCapTrip: (B1b);
                     one-frame glitches of s51_vidglitch.py 4 6 (glitch_<tag>.txt), video frames, .idx records, FrameTrace
                     rows in all and after the first scene frame, the coverage "video frames >= FrameTrace rows - 100"
                     (item 224 (a)(3); census: a failed coverage prints "glitches not conclusive"), torn FrameTrace
                     lines, the validation-layer lines, the emulator stdout present or not (item 224 (a)(8)).
SCENE_OK of a level (item 221 (g)(3), item 224 (a); session 143: per level over its pair): V = v143_NN (video), W = w143_NN
  (--vulkan-validation true).  YES only if every machine row holds, the sheet file sheet_<V>.png exists, is not empty and
  both its sha256 and the sha256 of rec_<V>.mp4 equal the lines of step2/times.txt, AND the lead's sheet row says viewed;
  every machine row true and the sheet row unfilled -> PENDING_SHEET; anything else -> NO.
Where the rule leaves an edge open the scorer prints both readings: the letter (every row / every marker of the log) and
the variant "vx" of the executor (rows and markers before the first "Event: quit" line and without the last row of the
log); verdicts use the letter.
B33 (item 231 (g)(1), session 143 print): a census entry with a K3 frame on the hold (the letter: every hold row of sc142, as
in the s142 census); beside it the executor variant "K3 on the hold within 120 s of presented time after the entry line"
(the length of the s142 census hold) - the V hold of session 143 is 330 s.
Link 1b of session 143 (HPP-321, ROADMAP item 242 (b)-(e); profile 143 only - profile 142 prints what it printed):
  (c) B5a by the letter on the whole V (as before) and beside it the variant 120 s (K2 frames within 120 s of presented
      time after the entry line, the same "within" as B33), K2 by place (entry / hold), the V tags with K2 only after 120 s
      (a separate row (B), form edes122); the map (A) row carries the outcome on 120 s (outcome120) and on the whole V.
  (d) W tags: no dt rule in the outcome (frames >= 1 s are an info line); a "--- Error ---" whose report carries a
      [Vulkan][E] line is the class VALIDATION_STOP, not K1 (the W fails SCENE_OK by its death-marker and [Vulkan][E] rows).
  (e) the pair row: guest args and json attempts[0].level = the level of the pair, and the sha256 of the log read = the
      last "enter_scene end" line of step2/times.txt, for V and W.
  (b) the cache manifests runs143/cache_<tag>.before|after.json (cachemf143.py) -> one continuity line per adjacent pair of
      made tags; a break -> "cache changed between tags" and the forms without the tags after the first break.
Output is ASCII only (item 175 (v)).  Logs are read in binary, streaming, in chunks - never whole.
    python sc143.py --tag <tag>                                 score one run (json in runs143/<tag>.score.json)
    python sc143.py --summary [--sheet viewed|not-viewed] [--sheet-tags v143_01,...]
                                                                every made tag, SCENE_OK per level, census table, k/10 rows
                                                                (--sheet-tags: the sheet row applies to these V tags only)
    python sc143.py --stop-check <tag>                          rc 5 when the stop rule of item 231 (i)(4) stands
    python sc143.py --check-seal                                every sha line of the seal against its file
    python sc143.py --calib                                     the calibration on the s122 logs (item 221 (g)(4))
    python sc143.py --check1b                                   s1s128, s2s128 -> K2; s6s137 validation active (item 224 (b)(2))
    python sc143.py --regress142                                profile 142 on the 12 s142 logs against summary142_viewed.txt
"""
import argparse
import hashlib
import json
import os
import re
import sys

ROOT = 'C:/kyty/s144'
PRED_PATH = 'C:/kyty/s144/pred/01_sc144.md'
CHAIN = 'go144a'
RUNS = 'runs144'
SCORER = 'sc144.py'
EXTRA = True
FORM144 = True
BUILD_SHA = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
SKY = 'underwater_aerial_garden'
LEVELS143 = ('spring_punch_sky_aztec', 'booster_construction', 'mini_astro_clock_tower', 'path_maker_mana_tree',
             'spring_punch_monster_cave', 'gulliver_island', 'rocket_hourglass', 'pot_treasure_cave', 'booster_magic_lamp',
             'rocket_space_station')
OLD143 = (('v143_01', 'spring_punch_sky_aztec'), ('v143_02', 'booster_construction'), ('v143_03', 'mini_astro_clock_tower'),
          ('v143_04', 'path_maker_mana_tree'), ('v143_05', 'spring_punch_monster_cave'), ('v143_06', 'gulliver_island'),
          ('v143_09', 'booster_magic_lamp'), ('v143_10', 'rocket_space_station'))
NEW144 = ('rocket_hourglass', 'pot_treasure_cave', 'bumper_enemy_snowy_canyon', 'big_hand_pirate_island', 'timestop_casino',
          'ice_iceberg', 'sponge_dirty_bath', 'hoover_beach', 'volcano_mountain', 'voxel_world', 'enemy_gorilla',
          'mini_giants_garden')
CONTROL = ('w144_00', SKY)
PAIRS = tuple((v, 'w144_%02d' % (i + 1), lv) for i, (v, lv) in enumerate(OLD143)) + tuple(
    ('v144_%02d' % (i + 9), 'w144_%02d' % (i + 9), lv) for i, lv in enumerate(NEW144))
LEVELS = tuple(lv for _, _, lv in PAIRS)
CENSUS = tuple((v, lv) for v, _, lv in PAIRS[len(OLD143):])
SEQ = (CONTROL[0],) + tuple(w for _, w, _ in PAIRS[:len(OLD143)]) + tuple(
    t for v, w, _ in PAIRS[len(OLD143):] for t in (v, w))
V_TAGS = tuple(v for v, _, _ in PAIRS)
W_TAGS = (CONTROL[0],) + tuple(w for _, w, _ in PAIRS)
ROOT143 = 'C:/kyty/s143'
PRED143 = 'C:/kyty/s143/pred/02_sc143.md'
XSRC = dict((v, dict(root=ROOT143, chain='go143a', pred=PRED143)) for v, _ in OLD143)
XSHEET = tuple(v for v, _ in OLD143)
SEALED_NAMES = ('go144a.sh', 'sc144.py', 'test_sc144.py', 'mut_sc144.py', 'enter_scene.py',
                'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py',
                'test_go144a.py', 'fgcpu144.py', 'test_fgcpu144.py', 'C:/kyty/scripts/s51_vidglitch.py',
                'cachemf144.py', 'lockcheck144.py', 'test_tools144.py', 'step2/next_one.sh', 'step2/call_one.sh',
                'step2/wait_one.sh', 'step2/apichk144.py', 'C:/kyty/s143/step2/times.txt', 'C:/kyty/s143/pred/02_sc143.md')
SEALED143 = ('go143a.sh', 'sc143.py', 'test_sc143.py', 'mut_sc143.py', 'enter_scene.py',
             'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py',
             'test_go143a.py', 'fgcpu143.py', 'test_fgcpu143.py', 'C:/kyty/scripts/s51_vidglitch.py',
             'cachemf143.py', 'lockcheck143.py', 'test_tools143.py', 'step2/next_one.sh', 'step2/call_one.sh',
             'step2/wait_one.sh')
CACHE_ROOTS = ('shader', 'pipeline', 'glcache')
VSTOP = 'VALIDATION_STOP'
W_STOP_RUN = 2
NUMW = {5: 'five', 6: 'six'}
PAIRS143 = tuple(('v143_%02d' % (i + 1), 'w143_%02d' % (i + 1), lv) for i, lv in enumerate(LEVELS143))
P143 = dict(ROOT=ROOT143, PRED_PATH=PRED143, CHAIN='go143a', RUNS='runs143', SCORER='sc143.py', EXTRA=True, FORM144=False,
            LEVELS=LEVELS143, PAIRS=PAIRS143, CENSUS=tuple((v, lv) for v, _, lv in PAIRS143),
            SEQ=tuple(t for v, w, _ in PAIRS143 for t in (v, w)), V_TAGS=tuple(v for v, _, _ in PAIRS143),
            W_TAGS=tuple(w for _, w, _ in PAIRS143), SEALED_NAMES=SEALED143, CONTROL=None, XSRC={}, XSHEET=(), HALF=5)
REGRESS143_FILE = 'C:/kyty/s143/step4/summary143_viewed.txt'
REGRESS143_B33 = ('v143_02', 'v143_07', 'v143_08', 'v143_09')
CENSUS142 = (('c142_01', 'bumper_enemy_snowy_canyon'), ('c142_02', 'big_hand_pirate_island'), ('c142_03', 'timestop_casino'),
             ('c142_04', 'mini_giants_garden'), ('c142_05', 'ice_iceberg'), ('c142_06', 'sponge_dirty_bath'),
             ('c142_07', 'hoover_beach'), ('c142_08', 'volcano_mountain'), ('c142_09', 'voxel_world'),
             ('c142_10', 'enemy_gorilla'))
P142 = dict(ROOT='C:/kyty/s142', PRED_PATH='C:/kyty/s142/pred/02_sc142.md', CHAIN='go142a', RUNS='runs142',
            SCORER='sc142.py', EXTRA=False, PAIRS=(('v142', 'w142', SKY),), CENSUS=CENSUS142,
            SEQ=('v142', 'w142') + tuple(t for t, _ in CENSUS142), V_TAGS=('v142',), W_TAGS=('w142',),
            SEALED_NAMES=('go142a.sh', 'sc142.py', 'test_sc142.py', 'mut_sc142.py', 'enter_scene.py',
                          'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt',
                          'sheet142.py', 'test_go142a.py', 'C:/kyty/scripts/s51_vidglitch.py'),
            FORM144=False, LEVELS=tuple(lv for _, lv in CENSUS142), CONTROL=None, XSRC={}, XSHEET=(), HALF=5)
REGRESS_FILE = 'C:/kyty/s142/step4/summary142_viewed.txt'
REGRESS_B33 = ('c142_02', 'c142_03', 'c142_05')
SCENE_DRAWS = 100
ENTRY_WIN = 599
K2_US = 1000000
K3_US = 100000
HOLD_CENSUS_US = 120000000
HOLD_CENSUS_S = 120
HOLD_SCENE_US = 300000000
HOLD_W_S = 300
HOLD_W_HARNESS_S = 310
HOLD_V_S = 330
FRAMES_V = 3000
COVER_SLACK = 100
PRIO_US = 50000
STOP_RUN = 3
HALF = 6
OPCODE_BASE = {('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1, ('VOPC', '0xe3'): 4}
CRASH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---')
HANG = (b'GpuHangAbort:', b'ErrorDeviceLost')
M_START = b'GuestOut: Level has started: '
M_FT = b'FrameTrace: n='
M_SKIP = b'AsyncPipelines: skipped draw'
M_OPC = b'opcode is not implemented'
M_STUB = b'=== Stubbed function'
M_PRIO = b'PriorityStall:'
M_BVH = b'BvhLoopCapTrip:'
M_VKE = b'[Vulkan][E]'
M_VKANY = b'[Vulkan]['
M_NOVAL = b'no validation layer:'
M_VALFEAT = b'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features'
M_QUIT = b'Event: quit'
M_ENDED = b'WARNING: the game ENDED inside the hold'
M_GUEST = b'GuestOut'
M_PRECACHE = b'PipelinePrecache:'
RX_PRECACHE = re.compile(rb'PipelinePrecache: \d+ recipes ->')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_OP = re.compile(rb'family=(\w+) opcode=(0x[0-9a-fA-F]+)')
RX_PRIO = re.compile(rb' us=(\d+)')
RX_SKIPF = re.compile(rb' frame=(\d+)')
RX_GLITCH = re.compile(r'^one-frame glitches: (\d+)\s*$')
RX_VFRAMES = re.compile(r': (\d+) frames \d+x\d+')
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')
M_BUILD = b'--- Build ---'
RX_LOC = re.compile(rb' in \S+:\d+\s*$')
REPORT_LINES = 50
REPORT_BYTES = 1 << 16
CHUNK = 1 << 26
CALIB = (('eatl122', 'C:/kyty/s122/log_eatl122.txt', 'penguin_atlantis'),
         ('edes122', 'C:/kyty/s122/log_edes122.txt', 'intro_next'),
         ('atl122', 'C:/kyty/s122/log_atl122.txt', 'penguin_atlantis'),
         ('ednn122', 'C:/kyty/s122/log_ednn122.txt', 'rotating_level_day_and_night'),
         ('eght122', 'C:/kyty/s122/log_eght122.txt', 'time_stopper_ghost_world'))
CHECK_K2 = (('s1s128', 'C:/kyty/s128'), ('s2s128', 'C:/kyty/s128'))
CHECK_VAL = ('s6s137', 'C:/kyty/s137/log_s6s137.txt', 'C:/kyty/s137/stdout_s6s137.txt')


def profile(values):
    """Set the module constants of a profile (P142 for the regression); returns the old values for the restore."""
    g = globals()
    old = dict((k, g[k]) for k in values)
    g.update(values)
    return old


def level_of(tag):
    if CONTROL is not None and tag == CONTROL[0]:
        return CONTROL[1]
    for v, w, lv in PAIRS:
        if tag in (v, w):
            return lv
    for t, lv in CENSUS:
        if t == tag:
            return lv
    return None


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _line(whole, i):
    s = whole.rfind(b'\n', 0, i) + 1
    e = whole.find(b'\n', i)
    if e < 0:
        e = len(whole)
    return s, e


def scan(path):
    """One streaming pass over a log (or an emulator stdout): rows, starts, markers - each with its byte position."""
    res = dict(path=path, rows=[], starts=[], crash=[], hang=[], skip_lines=0, skip_frames=set(), ops=[], stubs=[],
               prio=[], bvh=[], vke=[], quit=None, ended=[], bytes=0, torn=0, noval=0, valfeat=0, vkany=0,
               guestout=None, precache=0, precache_any=0)
    h = hashlib.sha256()
    off = 0
    tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            h.update(b)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                if cut == 0:
                    tail = buf
                    continue
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            if not whole:
                break
            base = off
            off += len(whole)
            nft = 0
            for m in RX_FT.finditer(whole):
                d = RX_DRAWS.search(m.group(3))
                res['rows'].append((int(m.group(1)), int(m.group(2)), int(d.group(1)) if d else -1, base + m.start()))
                nft += 1
            res['torn'] += whole.count(M_FT) - nft
            res['noval'] += whole.count(M_NOVAL)
            res['valfeat'] += whole.count(M_VALFEAT)
            res['vkany'] += whole.count(M_VKANY)
            res['precache'] += len(RX_PRECACHE.findall(whole))
            res['precache_any'] += whole.count(M_PRECACHE)
            if res['guestout'] is None:
                gi = whole.find(M_GUEST)
                if gi >= 0:
                    res['guestout'] = base + _line(whole, gi)[0]
            for marker, key in ((M_START, 'starts'), (M_SKIP, 'skip'), (M_OPC, 'ops'), (M_STUB, 'stubs'),
                                (M_PRIO, 'prio'), (M_BVH, 'bvh'), (M_VKE, 'vke'), (M_QUIT, 'quit'), (M_ENDED, 'ended')) \
                    + tuple((m, 'crash') for m in CRASH) + tuple((m, 'hang') for m in HANG):
                i = whole.find(marker)
                while i >= 0:
                    s, e = _line(whole, i)
                    line = whole[s:e]
                    pos = base + s
                    if key == 'starts':
                        res['starts'].append((line[line.find(marker) + len(marker):].strip().decode('latin1'), pos))
                    elif key == 'skip':
                        res['skip_lines'] += 1
                        x = RX_SKIPF.search(line)
                        if x:
                            res['skip_frames'].add(int(x.group(1)))
                    elif key == 'ops':
                        y = RX_OP.search(line)
                        res['ops'].append(((y.group(1).decode(), y.group(2).decode().lower()) if y else ('?', '?'), pos))
                    elif key == 'stubs':
                        e2 = whole.find(b'\n', e + 1)
                        nxt = whole[e + 1:e2 if e2 >= 0 else len(whole)]
                        res['stubs'].append((nxt.split(b'\t')[-1].strip().decode('latin1')[:120], pos))
                    elif key == 'prio':
                        z = RX_PRIO.search(line)
                        res['prio'].append((int(z.group(1)) if z else -1, pos))
                    elif key == 'quit':
                        if res['quit'] is None or pos < res['quit']:
                            res['quit'] = pos
                    else:
                        res[key].append((marker.decode(), pos, line[:200].decode('latin1')))
                    i = whole.find(marker, e)
            if not b:
                break
    res['sha256'] = h.hexdigest()
    res['bytes'] = off
    res['rows'].sort(key=lambda r: r[3])
    for k in ('starts', 'ops', 'stubs', 'prio'):
        res[k].sort(key=lambda r: r[1])
    for k in ('crash', 'hang', 'bvh', 'vke', 'ended'):
        res[k].sort(key=lambda r: r[1])
    res['err_vk'] = err_reports(path, [pos for kind, pos, _ in res['crash'] if kind == '--- Error ---'])
    return res


def err_reports(path, positions):
    """Item 242 (d): the positions of the "--- Error ---" lines whose report carries a [Vulkan][E] line - the report is
    the lines after the title up to the next "--- Build ---" line, the location line " in <file>:<line>" (its end) or
    REPORT_LINES lines, whichever comes first (common/assert.cpp BuildFatalReport)."""
    out = set()
    if not positions:
        return out
    with open(path, 'rb') as f:
        for pos in positions:
            f.seek(pos)
            lines = f.read(REPORT_BYTES).split(b'\n')[1:REPORT_LINES + 1]
            for line in lines:
                if M_BUILD in line:
                    break
                if M_VKE in line:
                    out.add(pos)
                    break
                if RX_LOC.search(line):
                    break
    return out


def derive(sc, level, quit_pos=None):
    """The reading of item 221 (g)(2) with the first-frame rule of item 221 (v) and the scene change of item 224 (a)(7)
    on one scan (letter and variant vx)."""
    out = dict(level=level, entered=False, entry_pos=None, first=None, window=0, hold=0, k2=[], k3w=[], k3h=[],
               k3h120=[], dt_after_entry_us=0, dt_after_first_us=0, frames_after_first=0, n_gaps=0, other_starts=[],
               change_pos=None, after_change=dict(rows=0, dt_us=0, k2=0), dt_median_us=None, dt_max_us=None,
               vx=dict(k2=[], k3w=[], k3h=[], dt_after_first_us=0, frames_after_first=0), k2_120=[], cut120_pos=None)
    ent = [p for name, p in sc['starts'] if name == level]
    if not ent:
        return out
    out['entered'] = True
    epos = ent[0]
    out['entry_pos'] = epos
    later = [(name, p) for name, p in sc['starts'] if p > epos]
    cpos = later[0][1] if later else None
    out['change_pos'] = cpos
    rows_after = [r for r in sc['rows'] if r[3] > epos]
    for name, p in later:
        prev = [r[0] for r in rows_after if r[3] < p]
        out['other_starts'].append((name, prev[-1] if prev else None))
    after = [r for r in rows_after if cpos is None or r[3] < cpos]
    beyond = [r for r in rows_after if cpos is not None and r[3] > cpos]
    out['after_change'] = dict(rows=len(beyond), dt_us=sum(r[1] for r in beyond),
                               k2=sum(1 for r in beyond if r[1] >= K2_US))
    out['dt_after_entry_us'] = sum(r[1] for r in after)
    fi = None
    for i, r in enumerate(after):
        if r[2] >= SCENE_DRAWS:
            fi = i
            break
    if fi is None:
        return out
    out['first'] = (after[fi][0], after[fi][1], after[fi][2])
    post = after[fi + 1:]

    def classes(rows):
        win, hold = rows[:ENTRY_WIN], rows[ENTRY_WIN:]
        k2 = [(r[0], r[1], 'entry' if j < ENTRY_WIN else 'hold') for j, r in enumerate(rows) if r[1] >= K2_US]
        k3w = [(r[0], r[1]) for r in win if K3_US <= r[1] < K2_US]
        k3h = [(r[0], r[1]) for r in hold if K3_US <= r[1] < K2_US]
        return k2, k3w, k3h, len(win), len(hold)
    out['k2'], out['k3w'], out['k3h'], out['window'], out['hold'] = classes(post)
    cum = 0
    within = set()
    for r in after:
        cum += r[1]
        if cum > HOLD_CENSUS_US:
            out['cut120_pos'] = r[3]
            break
        within.add(r[3])
    out['k3h120'] = [(r[0], r[1]) for r in post[ENTRY_WIN:] if r[3] in within and K3_US <= r[1] < K2_US]
    out['k2_120'] = [(r[0], r[1], 'entry' if j < ENTRY_WIN else 'hold') for j, r in enumerate(post)
                     if r[1] >= K2_US and r[3] in within]
    out['dt_after_first_us'] = sum(r[1] for r in post)
    out['frames_after_first'] = len(post)
    out['n_gaps'] = sum(1 for a, b in zip(post, post[1:]) if b[0] != a[0] + 1)
    ds = sorted(r[1] for r in post)
    if ds:
        out['dt_median_us'] = ds[len(ds) // 2]
        out['dt_max_us'] = ds[-1]
    q = quit_pos if quit_pos is not None else sc.get('quit')
    vpost = [r for r in post if q is None or r[3] < q]
    all_rows_end = sc['rows'][-1][3] if sc['rows'] else None
    vpost = [r for r in vpost if r[3] != all_rows_end]
    k2, k3w, k3h, _, _ = classes(vpost)
    out['vx'] = dict(k2=k2, k3w=k3w, k3h=k3h, dt_after_first_us=sum(r[1] for r in vpost), frames_after_first=len(vpost))
    return out


def markers(log, std, entry_pos, quit_pos):
    """Death markers of the log and the emulator stdout in the order of item 224 (a)(1): the log ones by position, then the
    stdout ones by position; kind, class, source, position, before/after the first Event: quit."""
    res = []
    for src, sc in (('log', log), ('stdout', std)):
        if sc is None:
            continue
        got = []
        for key in ('crash', 'hang'):
            for kind, pos, line in sc[key]:
                at_exit = src == 'log' and quit_pos is not None and pos > quit_pos
                got.append(dict(kind=kind, cls='K1' if key == 'crash' else 'K2', src=src, pos=pos, at_exit=at_exit,
                                line=line))
        got.sort(key=lambda m: m['pos'])
        res.extend(got)
    return res


def validation(log, std):
    """Item 224 (a)(2): the layer is active = 0 lines "no validation layer:" AND >= 1 line of the layer's extension
    VK_EXT_validation_features AND >= 1 "[Vulkan][" line (any level) - log and emulator stdout together."""
    n = dict(noval=0, valfeat=0, vkany=0)
    for sc in (log, std):
        if sc is not None:
            for k in ('noval', 'valfeat', 'vkany'):
                n[k] += sc[k]
    n['ok'] = log is not None and n['noval'] == 0 and n['valfeat'] >= 1 and n['vkany'] >= 1
    return n


def opcode_diff(ops, entry_pos):
    cnt = {}
    after = {}
    for k, pos in ops:
        cnt[k] = cnt.get(k, 0) + 1
        if entry_pos is not None and pos > entry_pos:
            after[k] = after.get(k, 0) + 1
    keys = sorted(set(cnt) | set(OPCODE_BASE))
    diff = [(k[0], k[1], cnt.get(k, 0), OPCODE_BASE.get(k, 0), cnt.get(k, 0) - OPCODE_BASE.get(k, 0), after.get(k, 0))
            for k in keys if cnt.get(k, 0) != OPCODE_BASE.get(k, 0)]
    return dict(total=sum(cnt.values()), diff=diff, profile_equal=not diff)


def read_glitch(path):
    """glitch_<tag>.txt of s51_vidglitch.py 4 6: (video frames, glitches) or None when the file or a line is missing."""
    if not os.path.isfile(path):
        return None
    frames = glitches = None
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = RX_GLITCH.match(line.rstrip('\n'))
            if m:
                glitches = int(m.group(1))
            v = RX_VFRAMES.search(line)
            if v and frames is None:
                frames = int(v.group(1))
    if frames is None or glitches is None:
        return None
    return dict(video_frames=frames, glitches=glitches)


def idx_count(path):
    """Records of rec_<tag>.mp4.idx (lines of >= 3 fields, as s51_vidglitch.py reads them); None without the file."""
    if not os.path.isfile(path):
        return None
    n = 0
    with open(path, 'rb') as f:
        for line in f:
            if len(line.split()) >= 3:
                n += 1
    return n


def sheet_state(root, tag, chain=None):
    """Item 224 (a)(5): the sheet file, its sha256 and the sha256 of the video against the lines of step2/times.txt."""
    png = os.path.join(root, 'sheet_%s.png' % tag)
    mp4 = os.path.join(root, 'rec_%s.mp4' % tag)
    size = os.path.getsize(png) if os.path.isfile(png) else 0
    sha = sha_file(png) if size > 0 else None
    rec = sha_file(mp4) if os.path.isfile(mp4) else None
    t_sheet = t_rec = None
    tp = os.path.join(root, 'step2', 'times.txt')
    if os.path.isfile(tp):
        rs = re.compile(r'%s %s sheet rc \S+ sheet_%s\.png sha256 ([0-9a-f]{64})' % (chain or CHAIN, tag, tag))
        rr = re.compile(r'%s %s s51_vidglitch rc \S+ glitch_%s\.txt sha256 \S* rec_%s\.mp4 sha256 ([0-9a-f]{64})'
                        % (chain or CHAIN, tag, tag, tag))
        with open(tp, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                a = rs.search(line)
                if a:
                    t_sheet = a.group(1)
                b = rr.search(line)
                if b:
                    t_rec = b.group(1)
    ok = size > 0 and sha == t_sheet and rec is not None and rec == t_rec
    return dict(size=size, sha=sha, times_sha=t_sheet, rec_sha=rec, times_rec_sha=t_rec, ok=ok)


def last_value(seq, name):
    val = None
    for i, a in enumerate(seq):
        if a == name and i + 1 < len(seq):
            val = seq[i + 1]
    return val


def admit(tag, js, pred_sha, pred_path=None):
    """Admission of one run by its json: (check, ok, detail) rows."""
    lv = level_of(tag)
    env = js.get('env') or {}
    at = js.get('attempts') or []
    rows = []
    is_w = tag in W_TAGS

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    add('one attempt (--attempts 1, no warmup)', len(at) == 1 and at[0].get('label') == 'attempt 1', len(at))
    add('build %s' % BUILD_SHA[:8], js.get('binary_sha256') == BUILD_SHA, (js.get('binary_sha256') or '')[:8])
    add('guest args -lvl %s' % lv, js.get('guest_args') == '-lvl %s' % lv, js.get('guest_args'))
    add('gates empty (shipped defaults)', js.get('gates') == '', repr(js.get('gates'))[:40])
    add('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1', env.get('KYTY_GPU_CLOCK_PIN'))
    add('KYTY_GPU_MARKERS=0', env.get('KYTY_GPU_MARKERS') == '0', env.get('KYTY_GPU_MARKERS'))
    add('no KYTY_GPU_CHECKPOINTS', 'KYTY_GPU_CHECKPOINTS' not in env, '')
    add('no KYTY_GATE_SCHEDULE', 'KYTY_GATE_SCHEDULE' not in env and 'KYTY_GATE_SCHEDULE_ABBA' not in env, '')
    rec = env.get('KYTY_REC')
    if is_w:
        add('no video in W', rec is None, rec)
    else:
        add('video KYTY_REC rec_%s.mp4' % tag, rec is not None and rec.replace('\\', '/').endswith('/rec_%s.mp4' % tag), rec)
    val = last_value(js.get('cmdline') or [], '--vulkan-validation')
    want = 'true' if is_w else 'false'
    add('--vulkan-validation %s' % want, val == want, val)
    if is_w:
        add('VK_LAYER_PATH in W', bool(env.get('VK_LAYER_PATH')), env.get('VK_LAYER_PATH'))
    pr = js.get('prereg') or {}
    add('prereg = the seal now', pred_sha is not None and pr.get('sha256') == pred_sha
        and (pr.get('path') or '').replace('\\', '/') == (pred_path or PRED_PATH), (pr.get('sha256') or '')[:8])
    add('no pipeline-cache retry', not any(a.get('pipeline_cache_off') for a in at), '')
    if FORM144:
        pc = env.get('KYTY_PIPELINE_PRECACHE')
        if is_w:
            add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc == '0', pc)
        else:
            add('V shipped defaults: no KYTY_PIPELINE_PRECACHE in the env (item 254 (k)(2))', pc is None, pc)
    return rows


def build(tag, lv, js, log, std, es, root, pred_sha, pred_path=None, chain=None):
    """Everything the scorer reads about one run from its json and the scans of its log, stdout and enter_scene stdout."""
    at = (js.get('attempts') or [{}])[0]
    r = dict(tag=tag, level=lv, made=True, log_present=log is not None, stdout_present=std is not None,
             admit=admit(tag, js, pred_sha, pred_path), guest_args=js.get('guest_args'))
    if log is None:
        r.update(derive=derive(dict(rows=[], starts=[], quit=None), lv), marks=[], log_sha=None)
    else:
        r['log_sha'] = log['sha256']
        r['derive'] = derive(log, lv)
        r['marks'] = markers(log, std, r['derive']['entry_pos'], log['quit'])
        if EXTRA:
            for m in r['marks']:
                src = log if m['src'] == 'log' else std
                if m['kind'] == '--- Error ---' and m['pos'] in src.get('err_vk', ()):
                    m['cls'] = VSTOP
    d = r['derive']
    r['att_level'] = at.get('level')
    r['times_log_sha'] = times_log_sha(root, tag, chain) if EXTRA else None
    ended = at.get('hold_exit') is not None or (es is not None and bool(es['ended']))
    exited = at.get('outcome') == 'exited'
    r['hold_exit'] = at.get('hold_exit')
    r['ended'] = ended
    r['exited'] = exited
    r['attempt_outcome'] = at.get('outcome')
    r['hold_s'] = at.get('hold_s')
    r['ft_tail'] = at.get('ft_tail')
    r['tail_stall'] = at.get('ft_tail') == 0 and at.get('hold_s') is not None
    r['val'] = validation(log, std)
    if tag in W_TAGS:
        r['admit'].append(('validation active (0 no validation layer, >= 1 VK_EXT_validation_features, >= 1 [Vulkan][)',
                           r['val']['ok'], '%d/%d/%d' % (r['val']['noval'], r['val']['valfeat'], r['val']['vkany'])))
    if FORM144:
        pl = log['precache'] if log is not None else None
        ps = std['precache'] if std is not None else 0
        r['precache'] = dict(log=pl, stdout=ps, any=None if log is None else log['precache_any'] + (
            std['precache_any'] if std is not None else 0))
        if tag in W_TAGS:
            r['admit'].append(('W form: no "PipelinePrecache: N recipes ->" line in the log (item 254 (e))', pl == 0,
                               'log %s' % pl))
        else:
            r['admit'].append(('V positive control: >= 1 "PipelinePrecache: N recipes ->" line in the log (item 254 (e))',
                               pl is not None and pl >= 1, 'log %s' % pl))
        r['guestout'] = log['guestout'] if log is not None else None
        r['wkey'] = None
    r['rows_total'] = len(log['rows']) if log is not None else 0
    r['torn'] = log['torn'] if log is not None else 0
    if log is not None:
        r['skip'] = dict(lines=log['skip_lines'], frames=len(log['skip_frames']))
        r['ops'] = opcode_diff(log['ops'], d['entry_pos'])
        r['stubs'] = [n for n, _ in log['stubs']]
        pr = [u for u, _ in log['prio']]
        r['prio'] = dict(over=sum(1 for u in pr if u > PRIO_US), max=max(pr) if pr else 0, lines=len(pr))
        r['bvh'] = len(log['bvh'])
        r['vke'] = len(log['vke']) + (len(std['vke']) if std else 0)
        r['vke_first'] = [x[2] for x in (log['vke'] + (std['vke'] if std else []))[:3]]
    r['glitch'] = read_glitch(os.path.join(root, 'glitch_%s.txt' % tag))
    r['idx'] = idx_count(os.path.join(root, 'rec_%s.mp4.idx' % tag))
    g = r['glitch']
    r['cover'] = g is not None and g['video_frames'] >= r['rows_total'] - COVER_SLACK
    r['sheet_file'] = os.path.isfile(os.path.join(root, 'sheet_%s.png' % tag))
    r['sheet'] = sheet_state(root, tag, chain) if tag in V_TAGS else None
    r['outcome'], r['outcome_vx'], r['key'], r['reason'] = outcome(r)
    r['outcome120'] = outcome120(r) if EXTRA and tag not in W_TAGS else None
    if FORM144 and tag in W_TAGS:
        r['wkey'] = w_stop_key(r)
    return r


def times_log_sha(root, tag, chain=None):
    """Item 242 (e): the sha256 of log_<tag>.txt in the last "<chain> <tag> enter_scene end ..." line of step2/times.txt
    (written by the chain at the moment the run ended); None without the file or the line."""
    tp = os.path.join(root, 'step2', 'times.txt')
    if not os.path.isfile(tp):
        return None
    rx = re.compile(r'%s %s enter_scene end rc \S+ log_%s\.txt sha256 ([0-9a-f]{64})' % (chain or CHAIN, tag, tag))
    got = None
    with open(tp, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = rx.search(line)
            if m:
                got = m.group(1)
    return got


def entry_of(tag, root=ROOT, pred_sha=None):
    """Everything the scorer reads about one run; None when the run was not made (no <tag>.json).  A V of another
    session (XSRC, profile 144: the v143_NN of the cross-session pairs, item 254 (e)) is read from ITS root with ITS seal
    (the sha256 of that seal now) and ITS chain name (the log and sheet sha lines of its step2/times.txt)."""
    lv = level_of(tag)
    x = XSRC.get(tag)
    pred_path = chain = None
    if x is not None:
        root, pred_path, chain = x['root'], x['pred'], x['chain']
        pred_sha = sha_file(pred_path) if os.path.isfile(pred_path) else None
    jp = os.path.join(root, '%s.json' % tag)
    if not os.path.isfile(jp):
        return None
    js = json.load(open(jp, encoding='utf-8'))
    lp = os.path.join(root, 'log_%s.txt' % tag)
    sp = os.path.join(root, 'stdout_%s.txt' % tag)
    ep = os.path.join(root, '%s.stdout.txt' % tag)
    log = scan(lp) if os.path.isfile(lp) else None
    std = scan(sp) if os.path.isfile(sp) else None
    es = scan(ep) if os.path.isfile(ep) else None
    return build(tag, lv, js, log, std, es, root, pred_sha, pred_path, chain)


def attempt_marker(tag, root=ROOT):
    """Item 224 (a)(8): the chain's marker attempt_<tag>.txt of a made attempt."""
    return os.path.isfile(os.path.join(root, 'attempt_%s.txt' % tag))


def outcome(r):
    """(letter outcome, variant-vx outcome, stop key, reason) of one census entry (items 221 (g)(2), 223 (a), 224 (a))."""
    d = r['derive']
    ms = r.get('marks') or []

    def one(marks, k2):
        if not d['entered']:
            return 'NOT_ENTERED', 'no entry line'
        cpos = d['change_pos']
        if cpos is not None:
            pre = [m for m in marks if m['src'] == 'log' and m['pos'] < cpos]
            if pre:
                return pre[0]['cls'], 'first death marker %s before the scene change' % pre[0]['kind']
            if k2:
                return 'K2', 'frame dt >= 1 s before the scene change'
            return 'NOT_EVALUABLE', 'scene change'
        if marks:
            return marks[0]['cls'], 'first death marker %s (%s)' % (marks[0]['kind'], marks[0]['src'])
        if r['ended'] or r['exited']:
            return 'K1', 'hold_exit / ENDED / exited'
        if k2 or r['tail_stall']:
            return 'K2', 'frame dt >= 1 s or tail stall'
        if d['first'] is None:
            return 'NOT_EVALUABLE', 'no first scene frame'
        if r['attempt_outcome'] != 'ok':
            return 'NOT_EVALUABLE', 'no stable (%s)' % r['attempt_outcome']
        if (r['hold_s'] or 0) < HOLD_CENSUS_S:
            return 'NOT_EVALUABLE', 'hold_s %s < %d' % (r['hold_s'], HOLD_CENSUS_S)
        if d['dt_after_entry_us'] >= HOLD_CENSUS_US:
            return 'HOLDS_120', 'held'
        return 'NOT_EVALUABLE', 'presented time after the entry line < 120 s'
    nodt = EXTRA and r['tag'] in W_TAGS
    letter, reason = one(ms, [] if nodt else d['k2'])
    vx = one([m for m in ms if not m['at_exit']], [] if nodt else d['vx']['k2'])[0]
    key = None
    if letter == 'NOT_ENTERED':
        key = ms[0]['kind'] if ms else ('attempt:%s' % r.get('attempt_outcome'))
    return letter, vx, key, reason


def outcome120(r):
    """Item 242 (c): (outcome, reason) of a V read as the s142 census read it - on the first 120 s of presented time after
    the entry line.  The cut is the first row whose cumulative dt after the entry line passes 120 s (None: the log never
    passes it - then the whole V is read); with a cut only log markers before it count (the stdout ones carry no time),
    the K2 frames are those within 120 s, and hold_exit / ENDED / the tail stall (at the end of the hold) do not count."""
    d = r['derive']
    if not d['entered']:
        return 'NOT_ENTERED', 'no entry line'
    cut = d['cut120_pos']
    ms = [m for m in (r.get('marks') or []) if cut is None or (m['src'] == 'log' and m['pos'] < cut)]
    cpos = d['change_pos'] if d['change_pos'] is not None and (cut is None or d['change_pos'] < cut) else None
    if cpos is not None:
        pre = [m for m in ms if m['src'] == 'log' and m['pos'] < cpos]
        if pre:
            return pre[0]['cls'], 'first death marker %s before the scene change' % pre[0]['kind']
        if d['k2_120']:
            return 'K2', 'frame dt >= 1 s before the scene change'
        return 'NOT_EVALUABLE', 'scene change'
    if ms:
        return ms[0]['cls'], 'first death marker %s (%s)' % (ms[0]['kind'], ms[0]['src'])
    if r['exited'] or (cut is None and r['ended']):
        return 'K1', 'hold_exit / ENDED / exited'
    if d['k2_120'] or (cut is None and r['tail_stall']):
        return 'K2', 'frame dt >= 1 s within 120 s' if d['k2_120'] else 'tail stall'
    if d['first'] is None:
        return 'NOT_EVALUABLE', 'no first scene frame'
    if r['attempt_outcome'] != 'ok':
        return 'NOT_EVALUABLE', 'no stable (%s)' % r['attempt_outcome']
    if (r['hold_s'] or 0) < HOLD_CENSUS_S:
        return 'NOT_EVALUABLE', 'hold_s %s < %d' % (r['hold_s'], HOLD_CENSUS_S)
    if d['dt_after_entry_us'] >= HOLD_CENSUS_US:
        return 'HOLDS_120', 'held'
    return 'NOT_EVALUABLE', 'presented time after the entry line < 120 s'


def scene_ok(v, w, sheet, pair=None):
    """SCENE_OK of one level by item 221 (g)(3) and item 224 (a) over its V/W pair: (word, rows)."""
    vt, wt, lv = pair if pair is not None else PAIRS[0]
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    add('V made', v is not None, '')
    add('W made', w is not None, '')
    if v is not None:
        dv = v['derive']
        g = v['glitch']
        add('V admitted', all(a[1] for a in v['admit']), ';'.join(a[0] for a in v['admit'] if not a[1]))
        add('V entered', dv['entered'], '')
        add('V first scene frame', dv['first'] is not None, dv['first'])
        add('V no scene change after the entry line', dv['change_pos'] is None, dv['other_starts'])
        add('V emulator stdout present', v['stdout_present'], '')
        add('V attempt ok, hold_s >= 330, no hold_exit / ENDED', v['attempt_outcome'] == 'ok'
            and (v['hold_s'] or 0) >= HOLD_V_S and v['hold_exit'] is None and not v['ended'], v['hold_s'])
        add('V 0 death markers (incl. hold_exit, exited)', not v['marks'] and not v['ended'] and not v['exited'],
            ';'.join(m['kind'] for m in v['marks']))
        add('V no frame dt >= 1 s after the first scene frame', not dv['k2'] and not v['tail_stall'],
            dv['k2'][:3])
        add('V n gaps after the first scene frame = 0', dv['n_gaps'] == 0, dv['n_gaps'])
        add('V sum dt_us after the first scene frame >= 300 s', dv['dt_after_first_us'] >= HOLD_SCENE_US,
            dv['dt_after_first_us'])
        add('V >= 3000 presented frames after the first scene frame', dv['frames_after_first'] >= FRAMES_V,
            dv['frames_after_first'])
        add('V video >= 3000 frames', g is not None and g['video_frames'] >= FRAMES_V,
            'missing' if g is None else g['video_frames'])
        add('V video frames >= FrameTrace rows in all - 100', v['cover'],
            '%s vs %d' % ('missing' if g is None else g['video_frames'], v['rows_total']))
        add('V 0 one-frame glitches (s51_vidglitch.py 4 6)', g is not None and g['glitches'] == 0,
            'missing' if g is None else g['glitches'])
    if w is not None:
        dw = w['derive']
        add('W admitted', all(a[1] for a in w['admit']), ';'.join(a[0] for a in w['admit'] if not a[1]))
        add('W entered', dw['entered'], '')
        add('W no scene change after the entry line', dw['change_pos'] is None, dw['other_starts'])
        add('W emulator stdout present', w['stdout_present'], '')
        add('W 0 death markers (incl. hold_exit, exited)', not w['marks'] and not w['ended'] and not w['exited'],
            ';'.join(m['kind'] for m in w['marks']))
        add('W 0 [Vulkan][E] lines', w.get('vke', 1) == 0 and w['log_present'], w.get('vke'))
        add('W ft_tail > 0', (w['ft_tail'] or 0) > 0, w['ft_tail'])
        add('W hold reached its end (ok, hold_s >= 300, no hold_exit)', w['attempt_outcome'] == 'ok'
            and (w['hold_s'] or 0) >= HOLD_W_S and w['hold_exit'] is None and not w['ended'], w['hold_s'])
    if EXTRA:
        want = '-lvl %s' % lv

        def same(e):
            return (e is not None and e['guest_args'] == want and e['att_level'] == lv and e['log_sha'] is not None
                    and e['log_sha'] == e['times_log_sha'])

        def show(e):
            return 'none' if e is None else '%s, level %s, log %s, times.txt %s' % (
                e['guest_args'], e['att_level'], (e['log_sha'] or '-')[:16], (e['times_log_sha'] or '-')[:16])
        add('V %s and W %s are the pair of one level (guest args %s and json level in both; sha256 of the log read = the '
            'enter_scene end line of step2/times.txt%s)' % (vt, wt, want, ' of its own session; item 254 (e)' if FORM144
                                                             else ''),
            v is not None and w is not None and v['tag'] == vt and w['tag'] == wt and same(v) and same(w),
            'V %s / W %s' % (show(v), show(w)))
    machine = all(x[1] for x in rows) and v is not None and w is not None
    sh = v['sheet'] if v is not None else None
    file_ok = sh is not None and sh['ok']
    rows.append(('V sheet file sheet_%s.png present, non-empty; its sha256 and the sha256 of rec_%s.mp4 = step2/times.txt'
                 % (vt, vt), file_ok, 'missing' if sh is None else 'size %d sha %s times %s rec %s times %s' % (
                     sh['size'], (sh['sha'] or '-')[:16], (sh['times_sha'] or '-')[:16], (sh['rec_sha'] or '-')[:16],
                     (sh['times_rec_sha'] or '-')[:16])))
    if not machine:
        word = 'NO'
    elif sheet == 'viewed':
        word = 'YES' if file_ok else 'NO'
    elif sheet == 'not-viewed':
        word = 'NO'
    else:
        word = 'PENDING_SHEET'
    rows.append(('sheet of V viewed by the lead (filled by the close)', sheet == 'viewed', (sheet or 'UNSET') + (
        ' (item 254 (a): viewed at the close of s143)' if vt in XSHEET else '')))
    return word, rows


def stop_check(outcomes):
    """Item 221 (g)(4) / 231 (i)(4): three census entries (V) in a row NOT_ENTERED with one marker -> stop.  outcomes:
    [(tag, outcome, key)] in the census order, made ones only; returns (stop, tags)."""
    run = []
    for tag, oc, key in outcomes:
        if oc == 'NOT_ENTERED':
            if run and run[-1][2] != key:
                run = []
            run.append((tag, oc, key))
        else:
            run = []
        if len(run) >= STOP_RUN:
            return True, [t for t, _, _ in run[-STOP_RUN:]]
    return False, []


def w_stop_key(r):
    """Item 254 (k)(4): the stop key of a W stopped before the first line carrying "GuestOut" - "<class> <kind>" of its
    first death marker in the order of item 224 (a)(1) among the log markers before that line (no such line in the log:
    every marker of the log and the stdout, then hold_exit / ENDED / exited); None when the W did not stop there (it
    reached the game, or stopped without a marker) or has no log."""
    if not r['log_present']:
        return None
    g = r.get('guestout')
    ms = [m for m in r['marks'] if g is None or (m['src'] == 'log' and m['pos'] < g)]
    if ms:
        return '%s %s' % (ms[0]['cls'], ms[0]['kind'])
    if g is None and (r['ended'] or r['exited']):
        return 'K1 hold_exit / ENDED / exited'
    return None


def stop_check_w(keys):
    """Item 254 (k)(4): two W in a row (the made W tags of SEQ in order) with one stop key -> stop.  keys: [(tag, key)];
    a W without a key (or an attempt without json) breaks the run; returns (stop, tags)."""
    run = []
    for tag, key in keys:
        if key is None:
            run = []
            continue
        if run and run[-1][1] != key:
            run = []
        run.append((tag, key))
        if len(run) >= W_STOP_RUN:
            return True, [t for t, _ in run[-W_STOP_RUN:]]
    return False, []


def control_state(e, no_json=False):
    """Item 254 (k)(4): the control W.  Returns (gate stop, letter stop, reasons of the letter, reasons of the executor).
    The letter: a death marker (log, stdout, hold_exit / ENDED / exited) or a [Vulkan][E] line.  The executor's reading
    (the gate): the letter, or any failing W row of SCENE_OK or of its admission (the W form: item 254 (k)(7)), or a
    missing log, or an attempt made without json."""
    if e is None:
        if no_json:
            return True, False, [], ['attempt made without json (instrument)']
        return False, False, [], []
    letter = []
    if e['marks']:
        letter.append('death marker %s' % ';'.join('%s %s' % (m['cls'], m['kind']) for m in e['marks']))
    if e['ended'] or e['exited']:
        letter.append('hold_exit / ENDED / exited')
    if e.get('vke'):
        letter.append('[Vulkan][E] %d' % e['vke'])
    rows = [x for x in scene_ok(None, e, None, (None, e['tag'], e['level']))[1] if x[0].startswith('W ')]
    execu = ['%s (%s)' % (x[0], x[2]) for x in rows if not x[1]]
    if not e['log_present']:
        execu.append('log missing')
    return bool(letter) or bool(execu), bool(letter), letter, execu


def made(t, root):
    """A call of the tag was made: its json or its attempt marker exists."""
    return os.path.isfile(os.path.join(root, '%s.json' % t)) or attempt_marker(t, root)


def stop_check144(tag, root, pred_sha):
    """Item 254 (k)(4) before the call of tag: (stop, lines).  Reads the control W, the last W_STOP_RUN made W and the
    last STOP_RUN made census V before the tag."""
    before = list(SEQ[:SEQ.index(tag)])
    lines = []
    stop = False
    c = CONTROL[0]
    if c in before:
        e = entry_of(c, root, pred_sha)
        gate, let, lr, xr = control_state(e, e is None and attempt_marker(c, root))
        lines.append('STOP RULE CONTROL before %s: %s; letter %s (%s); executor reading [I] (the gate) %s (%s)' % (
            tag, 'STOP' if gate else ('not made' if e is None else 'not met'), 'stop' if let else 'pass',
            '; '.join(lr) or 'none',
            'stop' if gate else 'pass', '; '.join(xr) or 'none'))
        stop = stop or gate
    ws = [t for t in before if t in W_TAGS and made(t, root)]
    keys = []
    for t in ws[-W_STOP_RUN:]:
        e = entry_of(t, root, pred_sha)
        keys.append((t, e['wkey'] if e is not None else None))
    sw, tw = stop_check_w(keys)
    lines.append('STOP RULE W before %s (two W in a row stopped before the first GuestOut line with one key): %s; keys %s'
                 % (tag, ('STOP ' + ','.join(tw)) if sw else 'not met', ', '.join('%s %s' % k for k in keys) or 'none'))
    stop = stop or sw
    vs = [t for t, _ in CENSUS if t in before and made(t, root)]
    oc = []
    for t in vs[-STOP_RUN:]:
        e = entry_of(t, root, pred_sha)
        oc.append((t, e['outcome'], e['key']) if e is not None else (t, 'ATTEMPT_NO_JSON', None))
    sv, tv = stop_check(oc)
    lines.append('STOP RULE before %s: %s' % (tag, ('STOP ' + ','.join(tv)) if sv else 'not met'))
    stop = stop or sv
    return stop, lines


def fmt_entry(r):
    d = r['derive']
    o = []
    o.append('TAG %s level %s outcome %s (variant vx: %s) reason: %s; log %s' % (
        r['tag'], r['level'], r['outcome'], r['outcome_vx'], r['reason'], (r.get('log_sha') or 'MISSING')[:16]))
    bad = [a for a in r['admit'] if not a[1]]
    o.append('  admission: %s' % ('PASS' if not bad else 'FAIL ' + '; '.join('%s (%s)' % (a[0], a[2]) for a in bad)))
    o.append('  attempt: outcome %s hold_s %s hold_exit %s ft_tail %s' % (r['attempt_outcome'], r['hold_s'],
                                                                         r['hold_exit'], r['ft_tail']))
    o.append('  emulator stdout: %s' % ('present' if r['stdout_present'] else 'MISSING (its markers are not read)'))
    o.append('  entry line: %s; first scene frame (n, dt_us, draws): %s; window %d rows, hold %d rows; n gaps %d; '
             'torn FrameTrace lines %d' % ('yes' if d['entered'] else 'NO', d['first'], d['window'], d['hold'],
                                           d['n_gaps'], r['torn']))
    o.append('  scene change (Level has started after the entry line; name, last n before it): %s; rows after it %d '
             '(%.1f s, dt >= 1 s %d; not classified)' % (d['other_starts'] or 'none', d['after_change']['rows'],
                                                          d['after_change']['dt_us'] / 1e6, d['after_change']['k2']))
    o.append('  presented time: after the entry line %.1f s; after the first scene frame %.1f s over %d frames; dt_us '
             'median %s max %s' % (d['dt_after_entry_us'] / 1e6, d['dt_after_first_us'] / 1e6, d['frames_after_first'],
                                   d['dt_median_us'], d['dt_max_us']))
    if EXTRA and r['tag'] in W_TAGS:
        o.append('  frames dt >= 1 s after the first scene frame: %s (info, under validation, not classified - item 224 (a)(6), '
                 '242 (d)); tail stall (ft_tail 0): %s' % (d['k2'] or 'none', 'yes' if r['tail_stall'] else 'no'))
    else:
        o.append('  K2 frames (dt >= 1 s after the first scene frame): %s; tail stall (ft_tail 0): %s'
                 % (d['k2'] or 'none', 'yes' if r['tail_stall'] else 'no'))
    if r.get('outcome120') is not None:
        o.append('  K2 frames within 120 s of presented time after the entry line (item 242 (c)): %s; outcome on 120 s: %s '
                 '(%s); outcome on the whole V: %s' % (d['k2_120'] or 'none', r['outcome120'][0], r['outcome120'][1],
                                                       r['outcome']))
    o.append('  K3 entry window (no warm base): %s' % (d['k3w'] or 'none'))
    o.append('  K3 hold: %s' % (d['k3h'] or 'none'))
    if EXTRA:
        o.append('  K3 hold within 120 s of presented time after the entry line (executor variant, the s142 census hold): %s'
                 % (d['k3h120'] or 'none'))
    vx = d['vx']
    o.append('  variant vx (before Event: quit, last row out): K2 %s; K3 window %s; K3 hold %s; %.1f s over %d frames'
             % (vx['k2'] or 'none', vx['k3w'] or 'none', vx['k3h'] or 'none', vx['dt_after_first_us'] / 1e6,
                vx['frames_after_first']))
    o.append('  death markers (in order): %s' % ('; '.join('%s %s %s@%d%s' % (m['cls'], m['kind'], m['src'], m['pos'],
                                                            ' at-exit' if m['at_exit'] else '') for m in r['marks'])
                                                 or 'none'))
    o.append('  hold_exit / game ended: %s; exited before stable: %s' % ('yes' if r['ended'] else 'no',
                                                                       'yes' if r['exited'] else 'no'))
    vl = r['val']
    o.append('  validation layer lines: no validation layer %d, VK_EXT_validation_features %d, [Vulkan][ %d -> active %s'
             % (vl['noval'], vl['valfeat'], vl['vkany'], 'yes' if vl['ok'] else 'no'))
    if FORM144:
        pc = r.get('precache') or {}
        o.append('  precache form (item 254 (e)): "PipelinePrecache: N recipes ->" lines log %s; executor member [I] (item '
                 '258 (d), not in the verdict): the same line in the emulator stdout %s, any "PipelinePrecache:" line %s' % (
                     pc.get('log'), pc.get('stdout'), pc.get('any')))
        if r['tag'] in W_TAGS:
            o.append('  W stop before the first GuestOut line (item 254 (k)(4)): first GuestOut at %s; stop key %s' % (
                r.get('guestout'), r.get('wkey') or 'none'))
    if r['log_present']:
        op = r['ops']
        o.append('  AsyncPipelines skipped draw: %d lines, %d frames (%scounted, not fatal)' % (
            r['skip']['lines'], r['skip']['frames'], 'distinct frame= ids, debt D-7; ' if FORM144 else ''))
        o.append('  opcode not implemented: %d lines; against 96/1/4: %s' % (op['total'], 'equal' if op['profile_equal']
                 else ', '.join('%s %s %d (base %d, %+d, after entry %d)' % x for x in op['diff'])))
        o.append('  Stubbed function: %d%s' % (len(r['stubs']), (' ' + ', '.join(r['stubs'][:10])) if r['stubs'] else ''))
        o.append('  PriorityStall > 50 ms: %d (lines %d, max %d us)' % (r['prio']['over'], r['prio']['lines'],
                                                                      r['prio']['max']))
        o.append('  BvhLoopCapTrip: %d' % r['bvh'])
        o.append('  [Vulkan][E]: %d%s' % (r['vke'], (' first: ' + ' | '.join(r['vke_first'])) if r['vke'] else ''))
    g = r['glitch']
    o.append('  video: frames %s, .idx records %s, FrameTrace rows in all %d, after the first scene frame %d; coverage '
             '(video >= rows - 100): %s' % ('n/a' if g is None else g['video_frames'], r['idx'], r['rows_total'],
                                             d['frames_after_first'],
                                             'yes' if r['cover'] else 'NO - glitches not conclusive'))
    o.append('  glitches s51_vidglitch.py 4 6: %s; sheet file: %s (viewed by the lead at the close)'
             % ('n/a' if g is None else '%d of %d video frames' % (g['glitches'], g['video_frames']),
                'yes' if r['sheet_file'] else 'no'))
    if r['sheet'] is not None:
        sh = r['sheet']
        o.append('  sheet and video sha256 (item 224 (a)(5)): sheet size %d sha %s (times.txt %s); rec sha %s (times.txt %s); '
                 'match %s' % (sh['size'], sh['sha'], sh['times_sha'], sh['rec_sha'], sh['times_rec_sha'],
                               'yes' if sh['ok'] else 'NO'))
    return o


def check_seal(pred=PRED_PATH, root=ROOT, me=None):
    """Every "seal: <sha> <name>" line of the seal against its file; the scorer itself and every SEALED_NAMES name must
    be there.  Returns (ok, rows)."""
    rows = []
    if not os.path.isfile(pred):
        return False, [('seal file', False, pred)]
    seen = {}
    for line in open(pred, encoding='utf-8'):
        m = RX_SEAL.match(line.rstrip('\n'))
        if m:
            seen[m.group(2)] = m.group(1)
    for name in SEALED_NAMES:
        if name not in seen:
            rows.append((name, False, 'no seal line'))
    for name, sh in sorted(seen.items()):
        p = name if (name.startswith('C:/') or name.startswith('/')) else os.path.join(root, name)
        now = sha_file(p) if os.path.isfile(p) else None
        rows.append((name, now == sh, (now or 'missing')[:16]))
    mine = sha_file(me or os.path.abspath(__file__))
    rows.append(('this scorer in the seal', seen.get(SCORER) == mine, mine[:16]))
    return all(r[1] for r in rows), rows


def forms(ents):
    """(B5a, B5) counts over admitted entries (item 221 (v))."""
    b5a = sum(1 for e in ents if e['derive']['k2'])
    b5 = sum(1 for e in ents if any(x[2] == 'entry' for x in e['derive']['k2']) or e['derive']['k3w'])
    return b5a, b5


def form_b33(ents):
    """(B33 letter, B33 executor variant, tags of the letter) over admitted entries (item 231 (g)(1)): a K3 frame on the
    hold; the variant counts only the hold within 120 s of presented time after the entry line."""
    tags = [e['tag'] for e in ents if e['derive']['k3h']]
    var = sum(1 for e in ents if e['derive']['k3h120'])
    return len(tags), var, tags


def summary(root, pred_sha, sheet, sheet_tags=None):
    out = []
    ents = {t: entry_of(t, root, pred_sha) for t in SEQ}
    nojs = [t for t in SEQ if ents[t] is None and attempt_marker(t, root)]
    for t in SEQ:
        if ents[t] is not None:
            out.extend(fmt_entry(ents[t]))
        elif t in nojs:
            out.append('TAG %s: ATTEMPT MADE, NO JSON (instrument)' % t)
        else:
            out.append('TAG %s: not made' % t)
    for t in XSRC:
        ents[t] = entry_of(t, root, pred_sha)
        x = XSRC[t]
        if ents[t] is not None:
            out.append('V OF ANOTHER SESSION %s (the pair of item 254 (e); root %s, chain %s, seal %s):' % (
                t, x['root'], x['chain'], x['pred']))
            out.extend(fmt_entry(ents[t]))
        else:
            out.append('TAG %s (V of another session, root %s): NO JSON' % (t, x['root']))
    words = []
    for vt, wt, lv in PAIRS:
        sh = 'viewed' if vt in XSHEET else (sheet if (sheet_tags is None or vt in sheet_tags) else None)
        word, rows = scene_ok(ents[vt], ents[wt], sh, (vt, wt, lv))
        words.append(word)
        out.append('SCENE_OK %s: %s' % (lv, word))
        for name, ok, det in rows:
            out.append('  %-4s %s (%s)' % ('PASS' if ok else 'FAIL', name, det))
        v, w = ents[vt], ents[wt]
        out.append('  info dt_us after the first scene frame: V median %s max %s; W median %s max %s; W presented %s s over %s '
                   'frames' % (v['derive']['dt_median_us'] if v else None, v['derive']['dt_max_us'] if v else None,
                               w['derive']['dt_median_us'] if w else None, w['derive']['dt_max_us'] if w else None,
                               '%.1f' % (w['derive']['dt_after_first_us'] / 1e6) if w else None,
                               w['derive']['frames_after_first'] if w else None))
        if EXTRA:
            out.append('  info W hold_s >= %d (item 231 (i)(2), the harness hold; executor reading, not in the verdict): %s'
                       % (HOLD_W_HARNESS_S, ('yes' if (w['hold_s'] or 0) >= HOLD_W_HARNESS_S else 'NO (%s)' % w['hold_s'])
                          if w else 'W not made'))
    if EXTRA:
        out.append('SCENE_OK LEVELS: YES %d, PENDING_SHEET %d, NO %d of %d' % (
            words.count('YES'), words.count('PENDING_SHEET'), words.count('NO'), len(PAIRS)))
    if FORM144:
        c = CONTROL[0]
        gate, let, lr, xr = control_state(ents[c], c in nojs)
        out.append('CONTROL W %s (%s, item 254 (k)(4)): %s; letter (death marker or [Vulkan][E]) %s (%s); executor '
                   'reading [I] (any W row or admission row failing; the gate) %s (%s)' % (
                       c, CONTROL[1], 'not made' if ents[c] is None and c not in nojs else ('STOP' if gate else 'PASS'),
                       'stop' if let else 'pass', '; '.join(lr) or 'none', 'stop' if gate else 'pass',
                       '; '.join(xr) or 'none'))
        vm = [t for t in V_TAGS if ents.get(t) is not None]
        wm = [t for t in W_TAGS if ents.get(t) is not None]
        vbad = [t for t in vm if not all(a[1] for a in ents[t]['admit'] if a[0].startswith(('V positive', 'V shipped')))]
        wbad = [t for t in wm if not all(a[1] for a in ents[t]['admit'] if a[0].startswith('W form'))]
        wstd = [t for t in wm if (ents[t].get('precache') or {}).get('stdout')]
        out.append('W FORM (item 254 (e)): V with the "PipelinePrecache: N recipes ->" line and no KYTY_PIPELINE_PRECACHE '
                   '%d of %d made; W with KYTY_PIPELINE_PRECACHE=0 and no such line in the log %d of %d made; violated: %s; '
                   'executor member [I] (item 258 (d), not in the verdict; a hit is a question to the lead): W with the line '
                   'in the emulator stdout: %s' % (len(vm) - len(vbad), len(vm), len(wm) - len(wbad), len(wm),
                                                    ','.join(vbad + wbad) or 'none', ','.join(wstd) or 'none'))
    made = [ents[t] for t, _ in CENSUS if ents[t] is not None]
    adm = [e for e in made if all(a[1] for a in e['admit'])]
    adm_tags = set(e['tag'] for e in adm)
    if FORM144:
        out.append('CENSUS = the V tags %s..%s, REPEATED entries (item 254 (k)(2)): the map rows and the forms B5 / B5a / B33 '
                   'below are of repeated entries, apart from the cold entries of s142 / s143' % (CENSUS[0][0],
                                                                                                   CENSUS[-1][0]))
    out.append('CENSUS made %d of %d (of them attempt made without json %d), admitted %d' % (
        len(made) + sum(1 for t, _ in CENSUS if t in nojs), len(CENSUS), sum(1 for t, _ in CENSUS if t in nojs), len(adm)))
    for t, lv in CENSUS:
        e = ents[t]
        if e is not None:
            out.append('  %s %-28s %-13s vx %-13s first %s K2 %d K3w %d K3h %d admitted %s reason %s' % (
                e['tag'], e['level'], e['outcome'], e['outcome_vx'], e['derive']['first'], len(e['derive']['k2']),
                len(e['derive']['k3w']), len(e['derive']['k3h']), 'yes' if e['tag'] in adm_tags else 'NO', e['reason']))
            if EXTRA:
                out.append('    map (A) row %s%s: outcome on 120 s %s (%s); outcome on the whole V %s (%s)' % (
                    e['level'], ' (repeated entry)' if FORM144 else '', e['outcome120'][0], e['outcome120'][1],
                    e['outcome'], e['reason']))
        elif t in nojs:
            out.append('  %s %-28s ATTEMPT MADE, NO JSON (instrument) - not admitted' % (t, lv))
    b5a, b5 = forms(adm)
    ent = sum(1 for e in adm if e['derive']['entered'])
    out.append('FORM B5a (a frame dt >= 1 s after the first scene frame): %d/%d [c] (admitted and entered %d)'
               % (b5a, len(CENSUS), ent))
    out.append('FORM B5 (a frame dt >= 100 ms in the entry window, no warm base): %d/%d [c] (admitted and entered %d)'
               % (b5, len(CENSUS), ent))
    if EXTRA:
        v120, k2e, k2h, late = forms120(adm)
        out.append('FORM B5a variant 120 s (a frame dt >= 1 s within 120 s of presented time after the entry line; the class '
                   'decision and pooling with s142 use this one, item 242 (c)): %d/%d [c] %s; K2 by place on the whole V: '
                   'entry %d %s, hold %d %s' % (len(v120), len(CENSUS), ','.join(v120) or 'none', len(k2e),
                                                 ','.join(k2e) or 'none', len(k2h), ','.join(k2h) or 'none'))
        out.append('K2 ON THE HOLD AFTER 120 s ONLY (a separate row (B) of register F per level, form edes122, not B5a; item '
                   '242 (c)): %s' % (','.join(late) or 'none'))
        b33, b33v, b33t = form_b33(adm)
        out.append('FORM B33 (a frame 100 ms <= dt < 1 s on the hold after the window): %d/%d [c] (admitted and entered %d)'
                   ' %s; executor variant (the hold within 120 s of presented time after the entry line): %d/%d'
                   % (b33, len(CENSUS), ent, ','.join(b33t) or 'none', b33v, len(CENSUS)))
    first5 = [t for t, _ in CENSUS[:HALF]]
    fa, fb = forms([e for e in adm if e['tag'] in first5])
    la, lb = forms([e for e in adm if e['tag'] not in first5])
    nf, nl = HALF, len(CENSUS) - HALF
    out.append('FORMS second reading by the order (shared caches warm from earlier runs): first %s B5a %d/%d B5 %d/%d; '
               'last %s B5a %d/%d B5 %d/%d' % (NUMW.get(nf, nf), fa, nf, fb, nf, NUMW.get(nl, nl), la, nl, lb, nl))
    oc = []
    for t, _ in CENSUS:
        if ents[t] is not None:
            oc.append((t, ents[t]['outcome'], ents[t]['key']))
        elif t in nojs:
            oc.append((t, 'ATTEMPT_NO_JSON', None))
    stop, tags = stop_check(oc)
    if FORM144:
        keys = [(t, ents[t]['wkey'] if ents[t] is not None else None) for t in SEQ
                if t in W_TAGS and (ents[t] is not None or t in nojs)]
        sw, tw = stop_check_w(keys)
        out.append('STOP RULE W (item 254 (k)(4): two W in a row stopped before the first GuestOut line with one key): %s; '
                   'keys %s' % (('STOP ' + ','.join(tw)) if sw else 'not met',
                                ', '.join('%s %s' % k for k in keys if k[1] is not None) or 'none'))
    out.append('STOP RULE (item 221 (g)(4)): %s' % (('STOP ' + ','.join(tags)) if stop else 'not met'))
    if EXTRA:
        made_tags = [t for t in SEQ if ents[t] is not None or t in nojs]
        lines, brk = continuity(root, made_tags)
        out.extend(lines)
        if brk is None:
            out.append('FORMS without the tags after the first cache break (item 242 (b)): no break - the forms above stand')
        else:
            keep = [e for e in adm if SEQ.index(e['tag']) < SEQ.index(brk)]
            ka, kb = forms(keep)
            k120 = forms120(keep)[0]
            k33, k33v, _ = form_b33(keep)
            out.append('FORMS without the tags after the first cache break (before %s; item 242 (b)): over V %s: B5a %d/%d, '
                       'B5a variant 120 s %d/%d, B5 %d/%d, B33 %d/%d (variant 120 s %d/%d)' % (
                           brk, ','.join(e['tag'] for e in keep) or 'none', ka, len(CENSUS), len(k120), len(CENSUS), kb,
                           len(CENSUS), k33, len(CENSUS), k33v, len(CENSUS)))
    return out, ents, words


def forms120(ents):
    """Item 242 (c) over admitted V: (tags with a K2 frame within 120 s of presented time after the entry line - the B5a
    variant 120 s; tags with a K2 frame in the entry window; tags with a K2 frame on the hold; tags with K2 frames only
    after 120 s)."""
    v120 = [e['tag'] for e in ents if e['derive']['k2_120']]
    k2e = [e['tag'] for e in ents if any(x[2] == 'entry' for x in e['derive']['k2'])]
    k2h = [e['tag'] for e in ents if any(x[2] == 'hold' for x in e['derive']['k2'])]
    late = [e['tag'] for e in ents if e['derive']['k2'] and not e['derive']['k2_120']]
    return v120, k2e, k2h, late


def cache_manifest(root, tag, when):
    """Item 242 (b): the manifest runs143/cache_<tag>.<before|after>.json of cachemf143.py: {roots: {name: present},
    files: {(root name, relative path): (size, mtime_ns, sha256)}}; None when the file is missing or broken."""
    p = os.path.join(root, RUNS, 'cache_%s.%s.json' % (tag, when))
    if not os.path.isfile(p):
        return None
    try:
        js = json.load(open(p, encoding='utf-8'))
        roots = dict((x[0], bool(x[2])) for x in js['roots'])
        files = dict(((x[0], x[1]), (x[2], x[3], x[4])) for x in js['files'])
    except (ValueError, KeyError, TypeError, IndexError):
        return None
    return dict(roots=roots, files=files)


def cache_diff(a, b):
    """{root: (added, removed, changed, presence changed)} from manifest a to manifest b over CACHE_ROOTS."""
    out = {}
    for name in CACHE_ROOTS:
        fa = dict((k[1], v) for k, v in a['files'].items() if k[0] == name)
        fb = dict((k[1], v) for k, v in b['files'].items() if k[0] == name)
        out[name] = (len(set(fb) - set(fa)), len(set(fa) - set(fb)), sum(1 for k in set(fa) & set(fb) if fa[k] != fb[k]),
                     a['roots'].get(name) != b['roots'].get(name))
    return out


def fmt_diff(dd):
    return '; '.join('%s +%d -%d ~%d%s' % (n, x[0], x[1], x[2], ' presence changed' if x[3] else '') for n, x in sorted(
        dd.items(), key=lambda kv: CACHE_ROOTS.index(kv[0])))


def continuity(root, made):
    """Item 242 (b): one line per adjacent pair of made tags of SEQ (the manifest after N = the manifest before N+1) and one
    line per tag for the changes within its run; returns (lines, the tag right after the first break or None).  A missing
    manifest of a pair is NOT EVALUABLE and counted as a break (executor variant)."""
    lines = ['CACHE CONTINUITY (item 242 (b): manifest after N = manifest before N+1; roots %s)' % ', '.join(CACHE_ROOTS)]
    brk = None
    for t in made:
        a, b = cache_manifest(root, t, 'before'), cache_manifest(root, t, 'after')
        if a is not None and b is not None:
            lines.append('  within %s (before the lock -> after the run): %s' % (t, fmt_diff(cache_diff(a, b))))
    for i in range(len(SEQ) - 1):
        n, m = SEQ[i], SEQ[i + 1]
        if n not in made or m not in made:
            continue
        a, b = cache_manifest(root, n, 'after'), cache_manifest(root, m, 'before')
        if a is None or b is None:
            lines.append('  %s -> %s: NOT EVALUABLE (manifest missing:%s%s) - counted as a break (executor variant)' % (
                n, m, ' after %s' % n if a is None else '', ' before %s' % m if b is None else ''))
            brk = brk or m
            continue
        dd = cache_diff(a, b)
        if all(x == (0, 0, 0, False) for x in dd.values()):
            lines.append('  %s -> %s: same (%s)' % (n, m, ', '.join('%s %d files' % (r, sum(
                1 for k in b['files'] if k[0] == r)) for r in CACHE_ROOTS)))
        else:
            lines.append('  %s -> %s: cache changed between tags (%s)' % (n, m, fmt_diff(dd)))
            brk = brk or m
    return lines, brk


def regress142(expect=REGRESS_FILE):
    """Item 231 (i)(4): profile 142 on the s142 logs; the summary with the sheet row viewed must equal the lead's file
    byte for byte (CRLF, the form the scorer of s142 printed into it), and B33 of the s142 census must be the three levels
    of item 231 (g)(1).  Returns (ok, lines)."""
    old = profile(P142)
    try:
        pred_sha = sha_file(PRED_PATH) if os.path.isfile(PRED_PATH) else None
        out, ents, _ = summary(ROOT, pred_sha, 'viewed')
        adm = [ents[t] for t, _ in CENSUS if ents[t] is not None and all(a[1] for a in ents[t]['admit'])]
        b33, b33v, b33t = form_b33(adm)
    finally:
        profile(old)
    lines = []
    raw = open(expect, 'rb').read() if os.path.isfile(expect) else b''
    new = ('\r\n'.join(out) + '\r\n').encode('ascii', 'replace')
    a = raw.decode('ascii', 'replace').replace('\r\n', '\n').split('\n')
    if a and a[-1] == '':
        a = a[:-1]
    diff = [(i + 1, a[i] if i < len(a) else '<none>', out[i] if i < len(out) else '<none>')
            for i in range(max(len(a), len(out))) if (a[i] if i < len(a) else None) != (out[i] if i < len(out) else None)]
    same = raw == new and bool(raw)
    lines.append('REGRESS142 expected %s sha256 %s lines %d; new lines %d sha256 %s; byte-identical %s; differing lines %d'
                 % (expect, hashlib.sha256(raw).hexdigest(), len(a), len(out), hashlib.sha256(new).hexdigest(),
                    'yes' if same else 'NO', len(diff)))
    for i, x, y in diff[:40]:
        lines.append('DIFF line %d expected: %s' % (i, x))
        lines.append('DIFF line %d new:      %s' % (i, y))
    b33ok = tuple(b33t) == REGRESS_B33
    lines.append('REGRESS142 B33 (K3 on the hold, item 231 (g)(1)): %d/10 %s (expected %s) -> %s; executor variant 120 s: '
                 '%d/10' % (b33, ','.join(b33t) or 'none', ','.join(REGRESS_B33), 'PASS' if b33ok else 'FAIL', b33v))
    ok = same and not diff and b33ok
    lines.append('REGRESS142: %s' % ('PASS' if ok else 'FAIL'))
    return ok, lines


def regress143(expect=REGRESS143_FILE):
    """Item 254 (k)(5): profile 143 on the 20 logs of s143; the summary with the sheet row viewed must equal the lead's
    file byte for byte (CRLF, the form the scorer of s143 printed into it), and B33 by the letter must be the four V of
    item 254 (g)(4).  Returns (ok, lines)."""
    old = profile(P143)
    try:
        pred_sha = sha_file(PRED_PATH) if os.path.isfile(PRED_PATH) else None
        out, ents, _ = summary(ROOT, pred_sha, 'viewed')
        adm = [ents[t] for t, _ in CENSUS if ents[t] is not None and all(a[1] for a in ents[t]['admit'])]
        b33, b33v, b33t = form_b33(adm)
    finally:
        profile(old)
    lines = []
    raw = open(expect, 'rb').read() if os.path.isfile(expect) else b''
    new = ('\r\n'.join(out) + '\r\n').encode('ascii', 'replace')
    a = raw.decode('ascii', 'replace').replace('\r\n', '\n').split('\n')
    if a and a[-1] == '':
        a = a[:-1]
    diff = [(i + 1, a[i] if i < len(a) else '<none>', out[i] if i < len(out) else '<none>')
            for i in range(max(len(a), len(out))) if (a[i] if i < len(a) else None) != (out[i] if i < len(out) else None)]
    same = raw == new and bool(raw)
    lines.append('REGRESS143 expected %s sha256 %s lines %d; new lines %d sha256 %s; byte-identical %s; differing lines %d'
                 % (expect, hashlib.sha256(raw).hexdigest(), len(a), len(out), hashlib.sha256(new).hexdigest(),
                    'yes' if same else 'NO', len(diff)))
    for i, x, y in diff[:40]:
        lines.append('DIFF line %d expected: %s' % (i, x))
        lines.append('DIFF line %d new:      %s' % (i, y))
    b33ok = tuple(b33t) == REGRESS143_B33
    lines.append('REGRESS143 B33 (K3 on the hold, item 254 (g)(4)): %d/10 %s (expected %s) -> %s; executor variant 120 s: '
                 '%d/10' % (b33, ','.join(b33t) or 'none', ','.join(REGRESS143_B33), 'PASS' if b33ok else 'FAIL', b33v))
    ok = same and b33ok
    lines.append('REGRESS143: %s' % ('PASS' if ok else 'FAIL'))
    return ok, lines


def calib():
    """Item 221 (g)(4): the five s122 logs; returns (passed, lines)."""
    lines = []
    passed = 0
    for tag, path, level in CALIB:
        sc = scan(path)
        d = derive(sc, level)
        k2 = [x[0] for x in d['k2']]
        k2loc = [x[2] for x in d['k2']]
        k3w = [x[0] for x in d['k3w']]
        k3h = [x[0] for x in d['k3h']]
        if tag == 'eatl122':
            ok = k2 == [191] and k2loc == ['entry']
        elif tag == 'edes122':
            ok = k2 == [4945] and k2loc == ['hold']
        elif tag == 'atl122':
            ok = not k2 and not k3w and not k3h
        elif tag == 'ednn122':
            ok = not k2 and not k3w and 1826 in k3h
        else:
            ok = not k2 and 389 in k3w
        passed += ok
        lines.append('CALIB %s %s sha %s level %s first %s K2 %s K3w %s K3h %s -> %s' % (
            tag, path, sc['sha256'][:16], level, d['first'], list(zip(k2, k2loc)) or 'none', k3w or 'none',
            k3h or 'none', 'PASS' if ok else 'FAIL'))
    lines.append('CALIB %d of %d' % (passed, len(CALIB)))
    return passed, lines


def checks1b():
    """Item 224 (b)(2): the device-lost logs s1s128, s2s128 -> outcome K2; s6s137 -> validation active by its three
    terms.  Returns (passed, total, lines)."""
    lines = []
    passed = 0
    for tag, root in CHECK_K2:
        js = json.load(open(os.path.join(root, '%s.json' % tag), encoding='utf-8'))
        lv = (js.get('guest_args') or '').split()[-1]
        paths = [os.path.join(root, x % tag) for x in ('log_%s.txt', 'stdout_%s.txt', '%s.stdout.txt')]
        scans = [scan(p) if os.path.isfile(p) else None for p in paths]
        r = build(tag, lv, js, scans[0], scans[1], scans[2], root, None)
        ok = r['outcome'] == 'K2'
        passed += ok
        lines.append('CHECK1B %s log sha %s level %s outcome %s key %s reason %s markers %s -> %s' % (
            tag, (r['log_sha'] or 'MISSING')[:16], lv, r['outcome'], r['key'], r['reason'],
            ';'.join('%s %s@%d' % (m['kind'], m['src'], m['pos']) for m in r['marks']), 'PASS' if ok else 'FAIL'))
    tag, lp, sp = CHECK_VAL
    log = scan(lp)
    std = scan(sp) if os.path.isfile(sp) else None
    vl = validation(log, std)
    passed += vl['ok']
    lines.append('CHECK1B %s log sha %s validation: no validation layer %d, VK_EXT_validation_features %d, [Vulkan][ %d '
                 '-> active %s -> %s' % (tag, log['sha256'][:16], vl['noval'], vl['valfeat'], vl['vkany'],
                                         'yes' if vl['ok'] else 'no', 'PASS' if vl['ok'] else 'FAIL'))
    total = len(CHECK_K2) + 1
    lines.append('CHECK1B %d of %d' % (passed, total))
    return passed, total, lines


def main(argv=None, root=ROOT, pred=PRED_PATH):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--tag')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--stop-check')
    ap.add_argument('--check-seal', action='store_true')
    ap.add_argument('--calib', action='store_true')
    ap.add_argument('--check1b', action='store_true')
    ap.add_argument('--regress142', action='store_true')
    ap.add_argument('--regress143', action='store_true')
    ap.add_argument('--sheet', choices=('viewed', 'not-viewed'), default=None)
    ap.add_argument('--sheet-tags', default=None)
    a = ap.parse_args(argv)
    if a.check_seal:
        ok, rows = check_seal(pred, root)
        for name, good, det in rows:
            print('%-4s %s %s' % ('OK' if good else 'BAD', name, det))
        print('SEAL: %s' % ('PASS' if ok else 'FAIL'))
        return 0 if ok else 1
    if a.calib:
        n, lines = calib()
        print('\n'.join(lines))
        return 0 if n == len(CALIB) else 1
    if a.check1b:
        n, total, lines = checks1b()
        print('\n'.join(lines))
        return 0 if n == total else 1
    if a.regress142:
        ok, lines = regress142()
        print('\n'.join(lines))
        return 0 if ok else 1
    if a.regress143:
        ok, lines = regress143()
        print('\n'.join(lines))
        return 0 if ok else 1
    pred_sha = sha_file(pred) if os.path.isfile(pred) else None
    if a.stop_check:
        if a.stop_check not in SEQ:
            print('usage: unknown tag %s' % a.stop_check)
            return 2
        if FORM144:
            stop, lines = stop_check144(a.stop_check, root, pred_sha)
            print('\n'.join(lines))
            return 5 if stop else 0
        before = [t for t, _ in CENSUS if SEQ.index(t) < SEQ.index(a.stop_check)]
        oc = []
        for t in before:
            e = entry_of(t, root, pred_sha)
            if e is not None:
                oc.append((t, e['outcome'], e['key']))
            elif attempt_marker(t, root):
                oc.append((t, 'ATTEMPT_NO_JSON', None))
        stop, tags = stop_check(oc)
        print('STOP RULE before %s: %s' % (a.stop_check, ('STOP ' + ','.join(tags)) if stop else 'not met'))
        return 5 if stop else 0
    if a.tag:
        if a.tag not in SEQ:
            print('usage: unknown tag %s' % a.tag)
            return 2
        e = entry_of(a.tag, root, pred_sha)
        if e is None:
            if attempt_marker(a.tag, root):
                print('TAG %s: ATTEMPT MADE, NO JSON (instrument)' % a.tag)
            else:
                print('TAG %s: NO_RUN (no %s.json)' % (a.tag, a.tag))
            return 1
        print('\n'.join(fmt_entry(e)))
        os.makedirs(os.path.join(root, RUNS), exist_ok=True)
        dump = dict((k, v) for k, v in e.items() if k != 'derive')
        dump['derive'] = e['derive']
        json.dump(dump, open(os.path.join(root, RUNS, '%s.score.json' % a.tag), 'w', encoding='utf-8'),
                  indent=1, default=list)
        return 0 if all(x[1] for x in e['admit']) else 1
    if a.summary:
        tags = None
        if a.sheet_tags is not None:
            tags = [t for t in a.sheet_tags.split(',') if t]
            bad = [t for t in tags if t not in V_TAGS]
            if bad:
                print('usage: --sheet-tags takes V tags only: %s' % ','.join(bad))
                return 2
        out, _, _ = summary(root, pred_sha, a.sheet, tags)
        print('\n'.join(out))
        return 0
    print('usage: sc144.py --tag T | --summary | --stop-check T | --check-seal | --calib | --check1b | --regress142 | '
          '--regress143')
    return 2


if __name__ == '__main__':
    sys.exit(main())
