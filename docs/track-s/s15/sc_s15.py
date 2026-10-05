#!/usr/bin/env python3
"""sc_s15.py - the scorer of track S, fifth wave S15 (link S15a, HPP-601; ROADMAP "SESSION 122" item 511 (z)): the port of
s13/sc_s13.py (seal 13, sha256 a0c66cc9ae2efe53272724d05dbb9a3f72e22cc000af2945d10029d559b06237) into C:/kyty/s288/s15 for the
arms of link S15b on the installed FS8 after FS8e (the seal pred/14_s.md says "installed: PENDING"; the edition pred/14b_s.md is a
lead item).  The changes against sc_s13.py (every other rule unchanged - item 511 (z)(6): the attribution, the members (e)(1),
(e)(3), RC1-RC7 of item 436, the answers of items 446, 452):
  (z)(3)  the collection arms k_01 .. k_19 hold HOLD_K = 300 s (was 180 s).
  (z)(4)  a U arm is held by enter_scene_s15.py --hold-u U_RULE ("120:3000:300"): while the presented time after the first scene
          frame is < 120 s or the video holds < 3 000 frames, but not longer than 300 s of presented time after the first scene
          frame (HOLD_U = 300 is the --hold of the arm; the wall cap is 300 + 60 s).  Admission row "before the run": the json
          carries the hold rule of the arm (hold_rule = HOLD_RULE_U on a U arm, absent on k / w13).  A video below 3 000 frames
          at the end of the hold is E3-video FAIL by the letter (unchanged member).  The hold end of the attempt (cause, anchor,
          presented time, video frames) is a data line per U arm.
  (z)(5)  an arm with the entry line of its level and WITHOUT a first scene frame (ps_logo): the E1 domain is every FrameTrace row
          after the entry line (the rows i >= eg, eg = the rows before the entry line) to the end of the hold - a scene change does
          not cut it (item 436 (b)(1)); the reading 2 of sc_s (no held first frame to add - there is no first scene frame); its
          presented time < 120 s without a death marker -> the E1 members UNDETERMINED (DOMAIN_MIN_US unchanged).  The domain line
          names the anchor ("first scene frame" / "entry line (item 511 (z)(5))").
  (z)(i)  the identities T-1, T-2, T-6 on the domain by the ROW that counts a line, not by frame=: T-1 - the "AsyncPipelines:
          skipped draw" lines of the groups g >= lo (a line of group g is logged after the row g-1 and counted by the row g) = the
          sum of skc_ap_skip of the rows i >= lo; T-6 - the distinct frame= of the same lines = the sum of skc_held_inc of the
          same rows; T-2 - the "AsyncPipelines: flip N held" lines with N >= the n of the row lo, capped as the emulator caps
          them (min(64 - the held lines before, the sum of skc_held_inc of the rows i >= lo)); lo = the first scene frame, else
          the entry row eg (z)(5), else the whole log - and never below row 1 (lines before the first FrameTrace row are counted by
          no row).  The cause [c, S13b logs]: k_01 - the line "flip 1 held" comes before the first FrameTrace row (n = 2), no row
          counts it (T-2 2 / 3); k_02 - a line "skipped draw frame=240" is logged after the row n = 235 and counted by the row
          n = 236 < the first scene frame 238 (frame= runs 2-4 ahead of n), so the cut by frame= >= 238 takes it and the cut by
          n >= 238 does not (T-1 325 / 326).  By the row: 39 of 39 S13b logs equal on T-1, T-2, T-6 (s15/ident_s15.out.txt).  The
          rows of item 404 (sc_s9.ident_domain, by frame=) are printed beside as one data row, no outcome reads them.
The S13 text below is kept (its "S13b" reads "S15b" for the arms of this seal).
Port header of sc_s13.py:  the scorer of track S, fourth wave, the catalogue of the 19 known levels (link S13a, HPP-498; ROADMAP "SESSION
122" item 408 (e), (l), item 229 (e)(1), (3), item 355 (e), item 371 (v), item 410 (g)(6)(iii), item 414 (b), (g)(1), (g)(5)-(7),
(d)(2), item 419 (v) Z3, item 428 (v), (g)); the arms run in link S13b under the lock, files in C:/kyty/s288/s15.

INHERITANCE: C:/kyty/s288/s9/sc_s9.py (the scorer of seal 07, sha256 SHA_SC_S9) is loaded UNCHANGED from its own path after a
sha256 check; it loads sc_s.py (seal 04) and sc142.py the same way.  Used as they are: sc_s scan_s(), scan_stdout(), locate(),
identities(), assign_prep(), freeze(), attributed*(), unattributed(), gates(), entry_line(), w_form_rows(); sc_s9 scan_x(),
scan_stdout_x(), ident_domain() (item 404), ident_t4(), early9(), bvh_col(); sc142 scan(), build(), last_value().  This file adds
the arms of S13b, their admission, the members of item 229 (e)(1), (3) and the data rows of item 414 (g)(5)-(7).

ARMS (S13b, in this order; the binary of every arm is the INSTALLED one, named by the seal line "installed: <sha256> <signature>
<variant>" - no install; item 414 (b): the arm binary is read from the field binary_sha256 of <tag>.json; item 419 (v) Z3,
item 428 (v)(1): every arm names KYTY_S_PCW=1 in its environment, every S-pcw: line of its log = that value):
  k_01 .. k_19  collection (item 408 (l), item 228 (v)): class M, the level K<NN> of lvl_s13.out.txt, hold HOLD_K; the app caches
                (_ShaderCache/PPSA21564, _PipelineCache) mirrored before the arm from the post copy of the previous k arm
                (k_01: from the empty set, MANIFEST sha EMPTY_SHA) - the catalogue grows in C:/kyty/s288/s15/cat/<tag>, never in
                the installed caches; GLCache as found (copied before, returned after); after the arm the app caches are copied
                to cat/<tag>; then the installed caches return by sha (cachex_s.py).  No video.
  (export)      seedexp_s15.py (no game, no lock): tools/shader_seed.py from cat/k_19/ShaderCache_PPSA21564/<variant> into
                s15/seeds/PPSA21564; the removed duplicates (F17) printed by a line (item 408 (z)).
  u_01 .. u_19  form U (item 355 (e), item 229 (e)(1) "first run of the user"): class T, the app caches empty for the arm, GLCache
                as found, KYTY_SHADER_SEED_PATH=C:/kyty/s288/s15/seeds KYTY_CACHE_MODE=prepare-cold, hold HOLD_U, video.
  w13           W of Sky Garden (item 229 (e)(3)) in form U + validation of item 295 (b): --vulkan-validation true, VK_LAYER_PATH,
                VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, no VK_LAYER_MESSAGE_ID_FILTER, class M, hold HOLD_W, no video.
MEMBERS (item 229 (e)(1), (3); after the first scene frame = the FrameTrace rows fi < i < end of the domain and the event lines of
groups fi < g < end of the domain; fi of sc_s.locate; the end of the domain = the last row of the log (item 436 (b)(1), RC1 below):
  E1-skip    0 frames with a skipped draw: rows with skc_ap_skip > 0 = 0 AND "AsyncPipelines: skipped draw" lines = 0
  E1-held    0 held flips: the sum of skc_held_inc of the rows = 0 (reading 1 of sc_s, with a held first scene frame, beside)
  E1-attr    0 attributed frames >= 100 ms (sc_s.attributed, reading 1; undetermined when the attribution is undetermined)
  E1-screen  the preparation screen <= 180 s (item 355 (e), item 371 (v): measured = the later of the two lines from the Popen;
             a lower bound > 180 s fails; else undetermined)
  E3-video   the video >= 3 000 frames, 0 one-frame glitches (s51_vidglitch.py 4 6), the sheet made (the lead reads it)
  E3-death   0 death markers (sc142: log, stdout, hold_exit / ENDED / exited)
  W          w13: entered, >= 300 s presented after the first scene frame, 0 [Vulkan][E] (log + stdout), the rows of item 295
             (b)(1)-(3), "DualSrcBlend: supported=1 enabled=1" before the first GuestOut line, 0 death markers
  An arm FAILS on a determined failing member, is UNDETERMINED on an undetermined one (not entered, admission by RC2 / identity
  broken, catalogue not installed, the domain < 120 s, no attribution, no screen measure, no video), else PASSES.  The word KNOWN_SCENES (item 229 (e)(1)
  with (3)): PASS - 19 of 19 U arms and w13 pass; FAIL - any determined failing member; else UNDETERMINED.  The words of (e)(1)
  alone and of (e)(3) alone are printed beside.  ENTRY (item 428 (g), V7): a level of the 19 is "not enterable by -lvl" when
  NEITHER its k arm NOR its u arm carries the line "Level has started: <level>" in an attempt without a death marker (nor
  hold_exit / ENDED / exited) and without a window event (minimized / Recovering Vulkan swapchain) - entry_state 'no' on both;
  the word KNOWN_SCENES_ENTERED over the U arms of the levels outside "not enterable": PASS - every one PASS and w13 PASS with
  a denominator >= 1; FAIL - any FAIL; else UNDETERMINED; printed beside KNOWN_SCENES (unchanged) with the list "not
  enterable".  Decisions are the lead's (S13c).
DATA ROWS (item 414 (g)(5)-(7), AUDIT_S3 section 6 p. 2): per arm the skipped-draw lines after the entry line whose frame= is below
  the first scene frame, and the lines without frame=; the S-early events with the series cost named "async creation us" (no
  "PREP-only" column for an event of kind series); the S-early count over DISTINCT events (item 414 (g)(1): a frame event whose n is
  the first frame of a series event of the same arm is the same event); the held frames >= 100 ms with their class.
S9r2 observations (item 382 (b), item 408 (k)(4)): (3) --check-seal reads the admission line "installed:" of the seal itself (the
  one source of the arm binary) and checks its form; (1) and (2) are in go_s15.sh.
S13a3 (link HPP-537, item 436 (b), (v); the review S13r c4d4a7e9:docs/track-s/s13r-review.md; the seal pred/14_s.md replaces 11):
  RC1  the domain of the members of (e)(1) (E1-skip, E1-held, E1-attr) on a U arm and on w13 is the LETTER: every row after the
       first scene frame fi to the end of the hold of the arm (the hold exit or the end of the log) - a scene change does not cut
       it (domain_of); the first scene frame is found as before (sc_s.locate).  Minimum: the presented time of the domain (the sum
       of dt_us of its rows) < DOMAIN_MIN_US (120 s, item 229 (g)(3)) without a death marker -> the E1 members UNDETERMINED.  The
       variant of Red Team (the domain to the first scene change, >= 120 s, else UNDETERMINED) is printed per arm as a REFERENCE
       with its word beside - no decision rides on it.  Printed per U arm and w13: the end of the domain and its cause, every
       scene change inside it (name, log line), its rows and presented time, the skips / held flips / attributed frames >= 100 ms
       before and after the first scene change.
  RC2  the admission rows are split: "before the run" (json, env, binary, prereg, the cache protocol) and "by the log" (S-pcw:,
       GamePatch:, the compatibility line, the variant directory, the window event).  A failing row before the run -> every member
       UNDETERMINED (the data beside).  A row by the log that is present and not the form, or a window event -> every member
       UNDETERMINED.  A row by the log that is missing with a death marker -> E3-death counted, the rest UNDETERMINED; missing
       without a death marker -> every member UNDETERMINED (executor's variant, a question to the lead).  The same on w13.
  RC3  entry_state: a failing admission or identity row -> 'void' (item 434 (b) in the code).
  RC4  entry_state 'no' only when the log carries both lines of the end of the preparation screen ("ShaderPreparation: ready",
       "PipelinePrecache: all pipelines created") and >= 1 FrameTrace row after the later one; else 'void' ("the preparation
       screen not passed").
  RC6  the edition pred/12b_s.md carries one line "edition: base pred/14_s.md sha256 <64 hex>" = the sha256 of the seal 12.
  RC7  the sha of the manifest man_launch_glc is printed per U arm and w13 (a data line).
S13a4 (link HPP-553, item 452 (b)-(d); the review S13r2 ffae6160:docs/track-s/s13r2-review.md section 2; the seal pred/14_s.md
replaces 12, which is not in force):
  RC1  item 452 (b): the data of the reading of item 446 (b), per arm (U, w13, k_NN), a data line - entry_state, the members and
       the words do not read it: (i) the log line number and the text (ASCII, the path whole) of the first line
       "PipelinePrecache: no <path> yet", or "none"; (ii) the FrameTrace rows (the form the scorer counts frames by, the rows of
       RC4) after max(ready_line, nopb_line) when the line "PipelinePrecache: all pipelines created" is absent and both
       "ShaderPreparation: ready" and "no ... yet" are present; else "not counted" with the reason.  Beside them (executor's
       addition, data): whether the parent directory of the path is the variant of the seal line "installed:".
  RC2  item 452 (c): the admission rows fall into three classes by an EXPLICIT LIST OF NAMES (ADMIT_PRE, ADMIT_LOG, ADMIT_POST;
       not by position): "before the run" (json, environment, binary, prereg, the cache protocol before the arm), "by the log"
       (item 436 (b)(2) unchanged), "after the arm" (return_app, return_glc, the installed binary after the arm, the manifests
       man_post_app and man_post_glc, app_post_copy of k_NN).  A failing row after the arm is printed beside the arm and makes
       entry_state 'void' (item 436 (b)(3) unchanged) but does not gate the members of the arm - they count as without it.  A
       row of no list (or of two) is UNCLASSED: printed so and read as "before the run"; the suite fails on any such row of
       any arm kind (a new admission row without a class does not pass ALL OK).
Output is ASCII only.  Logs are read in binary, streaming.
    python sc_s15.py --tag <tag> | --read | --summary | --allowed <tag> | --plan <tag> | --check-seal [--seal <p>] |
                     --seeds-check | --export-state
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys

SC_S9_PATH = 'C:/kyty/s288/s9/sc_s9.py'
SHA_SC_S9 = 'db65fdc89ba728e1d5e01ac2f393389dc69ef7b9d4e7936a75cfa0347f8fd670'


def load_sc_s9(path=SC_S9_PATH, want=SHA_SC_S9):
    """The inherited scorer of seal 07, unchanged: refuse when its sha256 is not the pinned one."""
    got = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if got != want:
        raise SystemExit('sc_s15.py: %s sha256 %s != pinned %s - the inheritance is broken' % (path, got, want))
    spec = importlib.util.spec_from_file_location('sc_s9_inherited', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S9 = load_sc_s9()
A = S9.A
B = S9.B

ROOT = 'C:/kyty/s288'
LINK_DIR = 'C:/kyty/s288/s15'
SEAL_BASE = 'C:/kyty/s288/pred/14_s.md'       # the seal of S15a: "installed: PENDING" (item 511 (z)(1))
SEAL_B = 'C:/kyty/s288/pred/14b_s.md'         # its edition: the same lines, the line "installed:" named, the line "edition:"
SEAL_BASE_REL = 'pred/14_s.md'                # the name of the seal in the line "edition: base <name> sha256 <sha>" (RC6)
EMPTY_SHA = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
SEEDS_PATH = 'C:/kyty/s288/s15/seeds'
SEEDS_MANI = 'C:/kyty/s288/s15/seeds_manifest.txt'
EXPORT_OUT = 'C:/kyty/s288/s15/seedexp_s15.out.txt'
SKY = 'underwater_aerial_garden'
LIST13 = ('title_controller_ship', 'intro_next', 'worldmap', 'ps_logo', 'hub_crashsite', 'underwater_aerial_garden',
          'penguin_atlantis', 'time_stopper_ghost_world', 'rotating_level_day_and_night', 'bumper_enemy_snowy_canyon',
          'big_hand_pirate_island', 'timestop_casino', 'mini_giants_garden', 'ice_iceberg', 'sponge_dirty_bath', 'hoover_beach',
          'volcano_mountain', 'voxel_world', 'enemy_gorilla')        # lvl_s13.out.txt LIST13 (item 229 (e)(1))
N_KNOWN = 19
HOLD_K = 300                     # item 511 (z)(3): the collection holds 300 s (was 180 s)
HOLD_U = 300                     # item 511 (z)(4): the --hold of a U arm = the cap of its hold rule, 300 s
U_MIN_S = 120                    # item 511 (z)(4): presented after the first scene frame (or the entry line, (z)(5))
U_CAP_S = 300                    # item 511 (z)(4): not longer than 300 s presented after the first scene frame
U_WALL_EXTRA_S = 60              # enter_scene_s15.py: the wall cap of a U hold is U_CAP_S + 60 s (executor's variant)
U_SCENE_DRAWS = 100              # enter_scene_s15.py SCENE_DRAWS_U = sc_s.SCENE_DRAWS (the first scene frame)
HOLD_W = 330                     # item 229 (e)(3): >= 300 s presented
HOLD_W_US = 300000000
FRAMES_VIDEO = 3000              # item 229 (e)(3); item 511 (z)(4): the video frames of the U hold rule
U_RULE = '%d:%d:%d' % (U_MIN_S, FRAMES_VIDEO, U_CAP_S)        # enter_scene_s15.py --hold-u
HOLD_RULE_U = dict(min_shown_s=U_MIN_S, video_frames=FRAMES_VIDEO, cap_s=U_CAP_S, wall_extra_s=U_WALL_EXTRA_S,
                   scene_draws=U_SCENE_DRAWS)                   # the json field hold_rule of a U arm
HELD_LINES_MAX = 64              # sc_s.HELD_LINES_MAX: the emulator prints at most 64 lines "flip N held" per process
PREP_LIMIT_S = 180               # item 229 (e)(1)
DOMAIN_MIN_US = 120000000        # item 436 (b)(1), item 229 (g)(3): the E1 domain presents >= 120 s, else UNDETERMINED
SPCW_ENV = '1'                   # item 419 (v) Z3, item 428 (v)(1): every arm names KYTY_S_PCW=1 (absent means 1 after S12)
SPCW_FMT = 'S-pcw: KYTY_S_PCW=%s KYTY_S_PCW_FORCE_MS=0'           # the form of sc_s9.py: the log line = the env of the arm
W_FORM_LINE = 'W form: limit=100000000 filter=none'
DUAL_LINE = b'DualSrcBlend: supported=1 enabled=1'
M_GUEST = b'GuestOut'
M_COMPAT = b'ShaderSeed: compatibility='
M_TCACHE = b'Shader translation cache: '
M_VKE = b'[Vulkan][E]'
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
M_RECOVER = b'Recovering Vulkan swapchain'
M_READY = b'ShaderPreparation: ready'                       # item 436 (b)(4), item 229 (g)(3): the end of the preparation screen
M_CREATED = b'PipelinePrecache: all pipelines created'
M_NOPB = b'PipelinePrecache: no '                           # "... pipelines.bin yet" (the empty set, s12_gw) - data only
M_NOPB_END = b' yet'                                         # item 452 (b): the path is between M_NOPB and this
RX_HELDF = re.compile(rb'^AsyncPipelines: flip (\d+) held')    # item 511 (z)(i): T-2 by the flip number
NL = chr(10)
FAMILIES = A.FAMILIES
FAMILY_KEYS = A.FAMILY_KEYS
PATH_KEYS = A.PATH_KEYS


def arms():
    """Every arm of S13b in the order of item 408 (l): tag -> spec."""
    a = []

    def add(tag, level, cls, group, mode, hold, src=None, k=None, rec=False, val=False):
        a.append(dict(tag=tag, level=level, cls=cls, group=group, mode=mode, hold=hold, src=src, k=k, rec=rec, val=val))
    for j, lv in enumerate(LIST13):
        add('k_%02d' % (j + 1), lv, 'M', 'k', 'cat', HOLD_K, src='empty' if j == 0 else 'k_%02d' % j, k=j)
    for j, lv in enumerate(LIST13):
        add('u_%02d' % (j + 1), lv, 'T', 'u', 'u', HOLD_U, k=j, rec=True)
    add('w13', SKY, 'M', 'w', 'u', HOLD_W, val=True)
    return a


ARMS = arms()
SPEC = dict((x['tag'], x) for x in ARMS)
SEQ = [x['tag'] for x in ARMS]
K_TAGS = [x['tag'] for x in ARMS if x['group'] == 'k']
U_TAGS = [x['tag'] for x in ARMS if x['group'] == 'u']


def expected_env(spec):
    e = dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1',
             KYTY_GUEST_ARGS='-lvl %s' % spec['level'], KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0',
             KYTY_S_PCW=SPCW_ENV)
    if spec['cls'] == 'T':
        e.update(KYTY_AV_TRACE='1', KYTY_SHADER_REGISTER_TRACE='1')
    if spec['mode'] == 'u':
        e.update(KYTY_SHADER_SEED_PATH=SEEDS_PATH, KYTY_CACHE_MODE='prepare-cold')
    return e


def in_family(k):
    return k.startswith(FAMILIES) or k in FAMILY_KEYS


def env_rows(spec, env):
    """(letter family row, strict row) of item 241 (v)(6) on the S13b environment (the logic of sc_s9.env_rows)."""
    want = expected_env(spec)
    have = dict((k, v) for k, v in (env or {}).items() if k.startswith('KYTY_'))
    fam_w = dict((k, v) for k, v in want.items() if in_family(k))
    fam_h = dict((k, v) for k, v in have.items() if in_family(k))
    rest_h = dict((k, v) for k, v in have.items() if k not in PATH_KEYS)
    diff = sorted(k for k in set(fam_w) | set(fam_h) if fam_w.get(k) != fam_h.get(k))
    sdiff = sorted(set(k for k in set(want) | set(rest_h) if want.get(k) != rest_h.get(k)) |
                   set(k for k in PATH_KEYS if k not in have and (k != 'KYTY_REC' or spec['rec'])))
    path_ok = all(k in have for k in PATH_KEYS if k != 'KYTY_REC') and (('KYTY_REC' in have) == spec['rec'])
    return (fam_w == fam_h, ','.join(diff) or '-'), (rest_h == want and path_ok, ','.join(sdiff) or '-')


def stable_timeout(spec):
    """(stable draws, --timeout s): W 300 / 600 (item 295 (b)); k and u 100 / 600 (the U form of S10)."""
    return (300, 600) if spec['val'] else (100, 600)


def hold_rule(spec):
    """Item 511 (z)(4): the hold rule of an arm - U_RULE on a U arm, None on k_NN and w13 (a fixed hold)."""
    return U_RULE if spec['group'] == 'u' else None


def plan(spec):
    """One line for go_s15.sh: link level cls mode hold src sdraws timeout rec val holdrule ('-' without a rule)."""
    sd, to = stable_timeout(spec)
    return 's15 %s %s %s %d %s %d %d %d %d %s' % (spec['level'], spec['cls'], spec['mode'], spec['hold'], spec['src'] or '-', sd,
                                                  to, 1 if spec['rec'] else 0, 1 if spec['val'] else 0, hold_rule(spec) or '-')


# ---------------------------------------------------------------------------------------------------------- seal lines
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')
RX_INST = re.compile(r'^installed: (\S+)(?: (\S+) (\S+))?$')
RX_HEX64 = re.compile(r'^[0-9a-f]{64}$')


def current_seal():
    """The seal in force: the edition 13b when it exists, else 13."""
    return SEAL_B if os.path.isfile(SEAL_B) else SEAL_BASE


def seal_installed(pred=None):
    """The admission line of the seal: ('PENDING', None, None) | (sha256, signature, variant) | None when the line is missing,
    repeated or malformed (S9r2 observation 3: the one source of the arm binary is this line)."""
    pred = pred or current_seal()
    if not os.path.isfile(pred):
        return None
    got = []
    for line in open(pred, encoding='utf-8'):
        m = RX_INST.match(line.rstrip('\n'))
        if m:
            got.append(m.groups())
    if len(got) != 1:
        return None
    sh, sig, var = got[0]
    if sh == 'PENDING' and sig is None:
        return ('PENDING', None, None)
    if RX_HEX64.match(sh or '') and sig and sig.startswith('KytySC3:') and var and var.startswith('variant_'):
        return (sh, sig, var)
    return None


# ---------------------------------------------------------------------------------------------------------- extra scan
def scan_y(path):
    """The lines neither sc_s.scan_s nor sc_s9.scan_x keep: the compatibility line and the translation cache line (first),
    "DualSrcBlend: supported=1 enabled=1" before the first line carrying GuestOut, [Vulkan][E] lines, the window events of item
    273 (z) by kind and the lines "Recovering Vulkan swapchain"; item 436 (b)(4): the log line numbers of the first
    "ShaderPreparation: ready", the first "PipelinePrecache: all pipelines created" and the first "PipelinePrecache: no ...
    pipelines.bin yet" (data); item 452 (b): the text of that line, ASCII (bytes above 127 as backslash escapes)."""
    r = dict(compat=None, tcache=None, dual_before=False, guest_seen=False, vke=0, win={}, recover=0, ready_line=None,
             created_line=None, nopb_line=None, nopb_text=None, held_flips=[])
    n = 0
    with open(path, 'rb') as f:
        for line in f:
            n += 1
            if r['ready_line'] is None and line.startswith(M_READY):
                r['ready_line'] = n
            if r['created_line'] is None and line.startswith(M_CREATED):
                r['created_line'] = n
            if r['nopb_line'] is None and line.startswith(M_NOPB) and line.rstrip().endswith(b'pipelines.bin yet'):
                r['nopb_line'] = n
                r['nopb_text'] = line.rstrip().decode('ascii', 'backslashreplace')
            if not r['guest_seen'] and M_GUEST in line:
                r['guest_seen'] = True
            if line.startswith(DUAL_LINE) and not r['guest_seen']:
                r['dual_before'] = True
            if r['compat'] is None and line.startswith(M_COMPAT):
                r['compat'] = line[len(M_COMPAT):].strip().decode('latin1')
            if r['tcache'] is None and line.startswith(M_TCACHE):
                r['tcache'] = line[len(M_TCACHE):].strip().decode('latin1').replace(chr(92), '/')
            if M_VKE in line:
                r['vke'] += 1
            if line.startswith(b'Window '):
                m = RX_WIN.match(line)
                if m:
                    k = m.group(1).decode('ascii')
                    r['win'][k] = r['win'].get(k, 0) + 1
            if M_RECOVER in line:
                r['recover'] += 1
            if line.startswith(b'AsyncPipelines: flip'):
                m = RX_HELDF.match(line)
                if m and b' held' in line:
                    r['held_flips'].append(int(m.group(1)))      # item 511 (z)(i): T-2 by the flip number
    return r


# ---------------------------------------------------------------------------------------------------------- the export
def manifest_sha(root):
    """(sha256, files) of the manifest of seedexp: "<name> <bytes> <sha256>" lines sorted over the files of root."""
    if not os.path.isdir(root):
        return None, 0
    lines = sorted('%s %d %s' % (n, os.path.getsize(os.path.join(root, n)), A.sha_file(os.path.join(root, n)))
                   for n in os.listdir(root) if os.path.isfile(os.path.join(root, n)))
    return hashlib.sha256(''.join(x + NL for x in lines).encode('ascii')).hexdigest(), len(lines)


RX_EXP_MANI = re.compile(r'^SEEDS manifest \S+ files (\d+) sha256 ([0-9a-f]{64})')
RX_EXP_SRC = re.compile(r'^source arm (k_\d\d) app_post_copy ([0-9a-f]{64})')
RX_EXP_COMPAT = re.compile(r'^compatibility\.txt: (\S+)$')
RX_EXP_DUP = re.compile(r'^removed duplicates \(F17\): (\S+)')


def export_state(root=LINK_DIR, out=EXPORT_OUT, mani=SEEDS_MANI, seeds=SEEDS_PATH):
    """The export of S13b: EXPORT: OK in its output, its manifest line = the file seeds_manifest.txt = the live catalogue, its
    source = the post copy of the last k arm (k_19) by the sha the harness noted.  Returns (ok, rows, dict)."""
    rows = []
    d = dict(mani=None, src=None, compat=None, dup=None)
    if not os.path.isfile(out):
        return False, [('export output %s' % out, False, 'missing')], d
    txt = open(out, encoding='ascii', errors='replace').read().split(NL)
    for line in txt:
        m = RX_EXP_MANI.match(line)
        if m:
            d['mani'] = m.group(2)
        m = RX_EXP_SRC.match(line)
        if m:
            d['src'] = (m.group(1), m.group(2))
        m = RX_EXP_COMPAT.match(line)
        if m:
            d['compat'] = m.group(1)
        m = RX_EXP_DUP.match(line)
        if m:
            d['dup'] = m.group(1)
    rows.append(('export output ends EXPORT: OK', 'EXPORT: OK' in txt, txt[-2] if len(txt) > 1 else '-'))
    fsha = A.sha_file(mani) if os.path.isfile(mani) else None
    rows.append(('the manifest line of the export = sha256 of seeds_manifest.txt', d['mani'] is not None and d['mani'] == fsha,
                 '%s / %s' % ((d['mani'] or '-')[:16], (fsha or '-')[:16])))
    live, n = manifest_sha(seeds + '/PPSA21564')
    rows.append(('the live catalogue s15/seeds/PPSA21564 = seeds_manifest.txt', live is not None and live == fsha,
                 '%s files %d' % ((live or '-')[:16], n)))
    last = K_TAGS[-1]
    cj = read_json(os.path.join(root, 'runs_s', '%s.cache.json' % last))
    pc = jget(cj, 'app_post_copy', 'sha')
    rows.append(('the export source = app_post_copy of %s' % last, d['src'] is not None and d['src'][0] == last and
                 pc is not None and d['src'][1] == pc, '%s / %s' % (d['src'], (pc or '-')[:16])))
    return all(r[1] for r in rows), rows, d


# ---------------------------------------------------------------------------------------------------------- one arm
def jget(d, key, sub):
    v = (d or {}).get(key)
    return v.get(sub) if isinstance(v, dict) else None


def read_json(p):
    return json.load(open(p, encoding='utf-8')) if os.path.isfile(p) else None


def cache_rows(spec, cj, cjs_of, inst):
    """Admission rows of the arm protocol from runs_s/<tag>.cache.json (item 228 (v), item 241 (g)(1)-(3), item 355 (e))."""
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    if cj is None:
        add('cache protocol json present', False, 'missing')
        return rows
    ra, rg = cj.get('restore_app') or {}, cj.get('restore_glc') or {}
    if spec['mode'] == 'cat' and spec['src'] != 'empty':
        want_app = jget(cjs_of(spec['src']), 'app_post_copy', 'sha')
        name = 'app_post_copy of %s (cat/%s)' % (spec['src'], spec['src'])
    else:
        want_app = EMPTY_SHA
        name = 'the empty set (%s)' % ('form U, item 355 (e)' if spec['mode'] == 'u' else 'the first collection arm')
    add('restore of the app caches = %s' % name, want_app is not None and ra.get('got') == want_app and
        ra.get('expected') == want_app, '%s / %s' % ((ra.get('got') or '-')[:16], (want_app or '-')[:16]))
    add('GLCache not restored before the arm (as found)', not rg, 'none' if not rg else 'restored')
    ml, mp = jget(cj, 'man_launch_glc', 'sha'), jget(cj, 'man_pre_glc', 'sha')
    add('man_launch_glc right before the game = man_pre_glc (GLCache as found)', ml is not None and ml == mp,
        '%s / %s' % ((ml or '-')[:16], (mp or '-')[:16]))
    if spec['mode'] == 'u':
        sd = jget(cj, 'seeds', 'sha')
        fsha = A.sha_file(SEEDS_MANI) if os.path.isfile(SEEDS_MANI) else None
        add('the catalogue before the arm = seeds_manifest.txt of the export', sd is not None and sd == fsha,
            '%s / %s' % ((sd or '-')[:16], (fsha or '-')[:16]))
    if spec['mode'] == 'cat':
        add('app_post_copy recorded (cat/%s, the next arm restores it)' % spec['tag'], bool(jget(cj, 'app_post_copy', 'sha')),
            (jget(cj, 'app_post_copy', 'sha') or '-')[:16])
    for key in ('return_app', 'return_glc'):
        r = cj.get(key) or {}
        add('%s after the arm = its copy' % key, r.get('got') is not None and r.get('got') == r.get('expected'),
            '%s / %s' % ((r.get('got') or '-')[:16], (r.get('expected') or '-')[:16]))
    ib, ia = jget(cj, 'installed_before', 'sha'), jget(cj, 'installed_after', 'sha')
    add('installed binary after the arm = before the arm (item 250 (b))', ib is not None and len(ib) == 64 and ia == ib,
        '%s / %s' % ((ia or '-')[:16], (ib or '-')[:16]))
    add('installed binary before the arm = the seal line "installed:" (S9r2 observation 3)',
        inst is not None and ib == inst[0], '%s / %s' % ((ib or '-')[:16], (inst[0] if inst else '-')[:16]))
    add('return_prev_ok (no RETURN_FAILED / IN_ARM guard before the arm)', jget(cj, 'return_prev', 'ok') == '1',
        jget(cj, 'return_prev', 'ok') or '-')
    for key in ('man_pre_app', 'man_pre_glc', 'man_post_app', 'man_post_glc', 'glc_pre_copy'):
        add('manifest %s recorded' % key, bool(jget(cj, key, 'sha')), (jget(cj, key, 'sha') or '-')[:16])
    return rows


def _rx(name):
    """An explicit row name; '{}' stands for the part that names the arm (tag, level, hold, source)."""
    return re.compile('^' + '.+?'.join(re.escape(p) for p in name.split('{}')) + '$')


# item 452 (c), RC2: the admission rows by an explicit list of names (not by position)
ADMIT_PRE = ('one attempt (--attempts 1, no warmup)',
             'arm binary = binary_sha256 of the json = the seal line "installed:" (item 414 (b))',
             'guest args -lvl {}', 'gates empty (shipped defaults)', 'no KYTY_GPU_CHECKPOINTS', 'no KYTY_GATE_SCHEDULE',
             'no KYTY_GAME_PATCH (item 342 (e))', 'KYTY_S_PCW=%s named in the env (item 419 (v) Z3, item 428 (v)(2))' % SPCW_ENV,
             'no KYTY_S_PCW_FORCE_MS / KYTY_FIX_* in the env (item 428 (v)(1))', 'video KYTY_REC rec_{}.mp4',
             'no video (KYTY_REC absent)', '--vulkan-validation {}',
             'W form line "%s" (item 295 (b)(4)), no VK_LAYER_MESSAGE_ID_FILTER' % W_FORM_LINE, 'VK_LAYER_PATH in the W env',
             'KYTY_* families = the seal (item 241 (v)(6), letter)', 'every KYTY_* key = the seal (executor variant, stricter)',
             'hold --hold {}', 'hold rule {} in the json (item 511 (z)(4))', 'prereg = the seal', 'no pipeline-cache retry',
             'cache protocol json present', 'restore of the app caches = {}', 'GLCache not restored before the arm (as found)',
             'man_launch_glc right before the game = man_pre_glc (GLCache as found)',
             'the catalogue before the arm = seeds_manifest.txt of the export',
             'installed binary before the arm = the seal line "installed:" (S9r2 observation 3)',
             'return_prev_ok (no RETURN_FAILED / IN_ARM guard before the arm)',
             'manifest man_pre_app recorded', 'manifest man_pre_glc recorded', 'manifest glc_pre_copy recorded')
ADMIT_LOG = ('every S-pcw: line (>= 1) = "%s" with the KYTY_S_PCW of the env of the arm (item 419 (v) Z3)' % SPCW_FMT,
             '0 lines GamePatch: in the log (item 342 (e))',
             'the compatibility line carries the signature of the seal line "installed:"',
             'the translation cache line ends with the variant of the seal line "installed:"',
             'no window event minimized / Recovering Vulkan swapchain (item 273 (z))')
ADMIT_POST = ('return_app after the arm = its copy', 'return_glc after the arm = its copy',
              'installed binary after the arm = before the arm (item 250 (b))',
              'manifest man_post_app recorded', 'manifest man_post_glc recorded',
              'app_post_copy recorded (cat/{}, the next arm restores it)')
C_PRE, C_LOG, C_POST = 'before the run', 'by the log', 'after the arm'


def row_class(name):
    """Item 452 (c): the class of one admission row by its name - C_PRE, C_LOG, C_POST; None (UNCLASSED) when the name is in no
    list or in more than one."""
    hits = [c for c, names in ((C_PRE, ADMIT_PRE), (C_LOG, ADMIT_LOG), (C_POST, ADMIT_POST))
            if any(_rx(x).match(name) for x in names)]
    return hits[0] if len(hits) == 1 else None


def post_fail(r):
    """Item 452 (c): the failing admission rows of the class "after the arm"."""
    return [a[0] for a in r['admit'] if not a[1] and row_class(a[0]) == C_POST]


def gating_fail(r):
    """Item 452 (c): the failures that gate the members - every failing row but those after the arm."""
    post = set('admission: %s' % n for n in post_fail(r))
    return [x for x in r['fail'] if x not in post]


def admit(spec, js, pred_sha, pred_path, cj, cjs_of, inst):
    env = js.get('env') or {}
    at = js.get('attempts') or []
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    add('one attempt (--attempts 1, no warmup)', len(at) == 1 and at[0].get('label') == 'attempt 1', len(at))
    add('arm binary = binary_sha256 of the json = the seal line "installed:" (item 414 (b))',
        inst is not None and js.get('binary_sha256') == inst[0], (js.get('binary_sha256') or '')[:16])
    add('guest args -lvl %s' % spec['level'], js.get('guest_args') == '-lvl %s' % spec['level'], js.get('guest_args'))
    add('gates empty (shipped defaults)', js.get('gates') == '', repr(js.get('gates'))[:40])
    add('no KYTY_GPU_CHECKPOINTS', 'KYTY_GPU_CHECKPOINTS' not in env, '')
    add('no KYTY_GATE_SCHEDULE', 'KYTY_GATE_SCHEDULE' not in env and 'KYTY_GATE_SCHEDULE_ABBA' not in env, '')
    add('no KYTY_GAME_PATCH (item 342 (e))', 'KYTY_GAME_PATCH' not in env, env.get('KYTY_GAME_PATCH') or '')
    add('KYTY_S_PCW=%s named in the env (item 419 (v) Z3, item 428 (v)(2))' % SPCW_ENV, env.get('KYTY_S_PCW') == SPCW_ENV,
        env.get('KYTY_S_PCW') or 'absent')
    add('no KYTY_S_PCW_FORCE_MS / KYTY_FIX_* in the env (item 428 (v)(1))',
        not any(k == 'KYTY_S_PCW_FORCE_MS' or k.startswith('KYTY_FIX_') for k in env),
        ','.join(k for k in env if k == 'KYTY_S_PCW_FORCE_MS' or k.startswith('KYTY_FIX_')))
    rec = env.get('KYTY_REC')
    if spec['rec']:
        add('video KYTY_REC rec_%s.mp4' % spec['tag'], rec is not None and
            rec.replace(chr(92), '/').endswith('/rec_%s.mp4' % spec['tag']), rec)
    else:
        add('no video (KYTY_REC absent)', rec is None, rec)
    val = B.last_value(js.get('cmdline') or [], '--vulkan-validation')
    add('--vulkan-validation %s' % ('true' if spec['val'] else 'false'), val == ('true' if spec['val'] else 'false'), val)
    if spec['val']:
        fl = env.get('VK_LAYER_MESSAGE_ID_FILTER')
        fm = 'W form: limit=%s filter=%s' % (env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'), 'none' if fl is None else fl)
        add('W form line "%s" (item 295 (b)(4)), no VK_LAYER_MESSAGE_ID_FILTER' % W_FORM_LINE,
            fm == W_FORM_LINE and fl is None, fm)
        add('VK_LAYER_PATH in the W env', bool(env.get('VK_LAYER_PATH')), env.get('VK_LAYER_PATH'))
    (fo, fd), (so, sd) = env_rows(spec, env)
    add('KYTY_* families = the seal (item 241 (v)(6), letter)', fo, fd)
    add('every KYTY_* key = the seal (executor variant, stricter)', so, sd)
    add('hold --hold %d' % spec['hold'], js.get('hold_s') == spec['hold'], js.get('hold_s'))
    want_rule = HOLD_RULE_U if hold_rule(spec) else None
    add('hold rule %s in the json (item 511 (z)(4))' % (hold_rule(spec) or 'none (a fixed hold)'), js.get('hold_rule') == want_rule,
        js.get('hold_rule'))
    pr = js.get('prereg') or {}
    add('prereg = the seal', pred_sha is not None and pr.get('sha256') == pred_sha and
        (pr.get('path') or '').replace(chr(92), '/') == pred_path, (pr.get('sha256') or '')[:8])
    add('no pipeline-cache retry', not any(a.get('pipeline_cache_off') for a in at), '')
    rows.extend(cache_rows(spec, cj, cjs_of, inst))
    return rows


def nopb_data(s, sy, inst):
    """Item 452 (b), RC1 (data only): (i) the log line number and the text of the first "PipelinePrecache: no <path> yet" (None
    when absent); (ii) the FrameTrace rows after max(ready_line, nopb_line) when "PipelinePrecache: all pipelines created" is
    absent and both "ShaderPreparation: ready" and "no ... yet" are present, else None with the reason why it is not counted;
    the parent directory of the path against the variant of the seal line "installed:" (True / False; None when there is no
    line or the seal is PENDING)."""
    rd, nb, cr = sy['ready_line'], sy['nopb_line'], sy['created_line']
    if cr is not None:
        why = 'not counted: the line "PipelinePrecache: all pipelines created" is present (line %d)' % cr
    elif rd is None:
        why = 'not counted: no line "ShaderPreparation: ready"'
    elif nb is None:
        why = 'not counted: no line "PipelinePrecache: no ... yet"'
    else:
        why = None
    later = None if why is not None else max(rd, nb)
    rows = None if later is None else sum(1 for x in s['rows'] if x[4] > later)
    tx = sy['nopb_text']
    var = None
    if tx is not None and inst is not None and inst[2]:
        path = tx[len(M_NOPB):]
        path = path[:-len(M_NOPB_END)] if path.endswith(M_NOPB_END.decode('ascii')) else path
        parts = path.replace('/', chr(92)).split(chr(92))
        var = len(parts) >= 2 and parts[-2] == inst[2]
    return dict(line=nb, text=tx, later=later, rows_after=rows, why=why, variant=var)


def fmt_nopb(r):
    """Item 452 (b): the data line of the reading of item 446 (b) for one arm."""
    d = (r or {}).get('nopb')
    if d is None:
        return 'not made or no log'
    i = 'line %d "%s"' % (d['line'], d['text']) if d['line'] is not None else 'none'
    ii = '%d' % d['rows_after'] if d['why'] is None else d['why']
    return ('(i) "PipelinePrecache: no <path> yet": %s; (ii) FrameTrace rows after max(ShaderPreparation: ready line %s, '
            '"no ... yet" line %s): %s; the parent directory of the path = the variant of the seal line "installed:" '
            '(executor\'s addition): %s' % (i, (r.get('prep_end') or {}).get('ready_line'), d['line'], ii,
                                             {True: 'yes', False: 'NO', None: 'n/a'}[d['variant']]))


def fmt_post(r):
    """Item 452 (c): the rows after the arm of one arm - ok or FAIL with the names."""
    if r is None:
        return 'not made'
    pf = post_fail(r)
    return 'ok' if not pf else 'FAIL %s - entry_state void, the members not gated' % '; '.join(pf)


def ident_lo(s, fi, eg):
    """Item 511 (z)(i): the first row of the identity domain - the first scene frame fi, else the entry row eg (z)(5), else the
    whole log; never below row 1 (a line logged before the first FrameTrace row is counted by no row)."""
    lo = fi if fi is not None else (eg if eg is not None else 0)
    return max(lo, 1)


def ident_rows(ident, s, sy, lo):
    """Item 511 (z)(i): T-1, T-2 and T-6 of sc_s.identities() on the rows i >= lo by the row that counts a line (see the header);
    the rows of item 404 (sc_s9.ident_domain, by frame=) arrive in ident and are kept as ONE data row (ok None).  A domain past
    the last row (lo >= rows) compares 0 with 0.  SKIP_LINES_MAX of sc_s unchanged (T-1, T-6 undetermined at the cap)."""
    rows = s['rows']
    xs = [s['x'].get(r[0]) for r in rows[lo:]]
    sk = sum((t[0] or 0) for t in xs if t)
    hi = sum((t[1] or 0) for t in xs if t)
    dom = [e for e in s['skips'] if e[0] >= lo]
    frames = set(e[1] for e in dom if e[1] is not None)
    under = len(s['skips']) < A.SKIP_LINES_MAX
    n_lo = rows[lo][0] if lo < len(rows) else None
    hf = sy['held_flips']
    before = sum(1 for f in hf if n_lo is None or f < n_lo)
    inside = sum(1 for f in hf if n_lo is not None and f >= n_lo)
    cap = max(0, HELD_LINES_MAX - before)
    old = [('%s %s' % (name.split(' ')[0], det)) for name, ok, det in ident
           if name.startswith(('T-1 ', 'T-2 ', 'T-6 ', 'T-1 / T-6 whole log'))]
    out = [x for x in ident if not x[0].startswith(('T-1 ', 'T-2 ', 'T-6 ', 'T-1 / T-6 whole log'))]
    where = 'the rows i >= %d (n >= %s; item 511 (z)(i))' % (lo, n_lo)
    out.append(('T-1 sum skc_ap_skip = skipped-draw lines of the groups g >= lo, on %s' % where, (sk == len(dom)) if under else None,
                '%d / %d (lines without frame= %d)' % (sk, len(dom), sum(1 for e in dom if e[1] is None))))
    out.append(('T-2 min(64 - held lines before, sum skc_held_inc) = "flip N held" lines with N >= n, on %s' % where,
                min(cap, hi) == inside, '%d / %d (lines before %d)' % (min(cap, hi), inside, before)))
    out.append(('T-6 distinct frame= of the skipped-draw lines of the groups g >= lo = sum skc_held_inc, on %s' % where,
                (len(frames) == hi) if under else None, '%d / %d' % (len(frames), hi)))
    out.append(('T-1 / T-2 / T-6 by frame= of item 404 and whole log (data, item 511 (z)(i))', None, '; '.join(old) or '-'))
    return out


def frame_rows(s, fi, end):
    """Item 229 (e)(1) after the first scene frame: rows i in (fi, end) with skc_ap_skip > 0, the skipped-draw lines of the groups
    fi < g < end, the sum of skc_held_inc of the rows, and the data rows of item 414 (g)(5)-(7)."""
    rr = range(fi + 1, end)
    skip_rows = sum(1 for i in rr if (A.xget(s, i, 0) or 0) > 0)
    skip_lines = sum(1 for e in s['skips'] if fi < e[0] < end)
    held = sum((A.xget(s, i, 1) or 0) for i in rr)
    return dict(skip_rows=skip_rows, skip_lines=skip_lines, held=held)


def shown_us(s, lo, hi):
    """The presented time of the rows lo .. hi-1 (the sum of their dt_us)."""
    return sum(s['rows'][i][1] for i in range(lo, hi))


def domain_of(s, level, fi, sc_end, attempt, ended, exited, anchor='first scene frame'):
    """Item 436 (b)(1), RC1 - the letter: the domain of the members of (e)(1) is every row after the first scene frame fi to the
    end of the hold of the arm (the last row of the log); a scene change does not cut it.  Returns the end (row index, exclusive),
    its cause ('hold' - the attempt ended by its hold without hold_exit / ENDED / exited; 'end of log' otherwise), the scene changes
    inside the domain [(row index, name, log line)], its rows and presented time, and the reference domain of Red Team (to the
    first scene change sc_end of sc_s.locate) with its rows and presented time."""
    nrows = len(s['rows'])
    ent = [j for j, x in enumerate(s['starts']) if x[1] == level]
    ch = [(x[0], x[1], x[2]) for x in s['starts'][ent[0] + 1:]] if ent else []
    cause = 'hold' if attempt == 'ok' and not ended and not exited else 'end of log'
    return dict(end=nrows, cause=cause, changes=ch, rows=max(0, nrows - fi - 1), shown_us=shown_us(s, fi + 1, nrows),
                ref_end=sc_end, ref_rows=max(0, sc_end - fi - 1), ref_shown_us=shown_us(s, fi + 1, sc_end), anchor=anchor)


def split_at(s, fi, end, cut, fz, attr_ok):
    """Item 436 (b)(1): the skips, held flips and attributed frames >= 100 ms of the domain (fi, end) before the row cut (the
    first scene change) and from it on: dict(before=..., after=...); attributed None when the attribution is undetermined."""
    out = {}
    for part, lo, hi in (('before', fi + 1, min(cut, end)), ('after', max(cut, fi + 1), end)):
        rr = range(lo, hi)
        d = dict(rows=len(rr), skip_rows=sum(1 for i in rr if (A.xget(s, i, 0) or 0) > 0),
                 skip_lines=sum(1 for e in s['skips'] if lo - 1 < e[0] < hi and e[0] > fi),
                 held=sum((A.xget(s, i, 1) or 0) for i in rr))
        if attr_ok:
            d['attr100'] = sum(1 for x in fz['long'] if lo <= x['i'] < hi and A.counted_row(x) and x['dt'] >= A.K3_US and
                               not x['held']) + sum(1 for x in fz['series'] if lo <= x['a'] < hi and x['gap_pipe_us'] >= A.K3_US)
        else:
            d['attr100'] = None
        out[part] = d
    return out


def pre_domain_lines(s, level, f0):
    """Item 414 (g)(5)-(7): (skipped-draw lines after the entry line with frame= below the first scene frame n f0, skipped-draw
    lines without frame=)."""
    el = A.entry_line(s, level)
    below = sum(1 for e in s['skips'] if el is not None and e[5] > el and e[1] is not None and e[1] < f0)
    nof = sum(1 for e in s['skips'] if e[1] is None)
    return below, nof


def early_distinct(e):
    """Item 414 (g)(1): the S-early events counted as distinct events - a frame event whose n is the n of a series event of the
    same arm is one event with it (the series kept); returns (distinct events, known, lead < cost)."""
    if e is None:
        return None
    sn = set(x['n'] for x in e['events'] if x['kind'] == 'series')
    ev = [x for x in e['events'] if x['kind'] == 'series' or x['n'] not in sn]
    known = [x for x in ev if x['lead'] is not None]
    return dict(events=ev, known=len(known), short=sum(1 for x in known if x['lead'] < x['cost']))


def screen(r):
    """Item 355 (e), item 371 (v): (seconds, kind) of the preparation screen: 'measured' - both lines seen, the later from the Popen;
    'lower bound' - a line missing: max(elapsed_ms of ShaderPreparation: progress, --timeout when the attempt ended by timeout);
    'none'."""
    xs = [x for x in (r.get('prep_created_s'), r.get('prep_ready_s')) if x is not None]
    if len(xs) == 2:
        return max(xs), 'measured'
    lb = []
    pm = (r.get('prep') or {}).get('prog_ms')
    if pm is not None:
        lb.append(pm / 1000.0)
    if r.get('attempt') == 'timeout':
        lb.append(float(stable_timeout(SPEC[r['tag']])[1]))
    return (max(lb), 'lower bound') if lb else (None, 'none')


def score_arm(tag, root=LINK_DIR, pred_sha=None, pred_path=None, inst=None):
    """Everything about one arm of S13b; None when it was not made (no <tag>.json)."""
    spec = SPEC[tag]
    js = read_json(os.path.join(root, '%s.json' % tag))
    if js is None:
        return None
    lp = os.path.join(root, 'log_%s.txt' % tag)
    sp = os.path.join(root, 'stdout_%s.txt' % tag)
    ep = os.path.join(root, '%s.stdout.txt' % tag)

    def cjs_of(t):
        return read_json(os.path.join(root, 'runs_s', '%s.cache.json' % t))
    cj = cjs_of(tag)
    log142 = B.scan(lp) if os.path.isfile(lp) else None
    std142 = B.scan(sp) if os.path.isfile(sp) else None
    es142 = B.scan(ep) if os.path.isfile(ep) else None
    base = B.build(tag, spec['level'], js, log142, std142, es142, root, None)
    at = (js.get('attempts') or [{}])[0]
    r = dict(tag=tag, level=spec['level'], cls=spec['cls'], group=spec['group'], outcome142=base['outcome'],
             reason142=base['reason'], marks=base.get('marks') or [], ended=base['ended'], exited=base['exited'],
             attempt=base['attempt_outcome'], hold_s=base['hold_s'], vke=base.get('vke'), glitch=base['glitch'],
             derive142=base['derive'], log_sha=base.get('log_sha'), sheet_file=base.get('sheet_file'),
             prep_created_s=at.get('prep_created_s'), prep_ready_s=at.get('prep_ready_s'), binary=js.get('binary_sha256'))
    r['admit'] = admit(spec, js, pred_sha, pred_path, cj, cjs_of, inst)     # item 452 (c): classed by row_class
    r['log_rows'] = {}                      # name -> 'ok' | 'missing' | 'differs' (item 436 (b)(2))
    r['glc_launch'] = jget(cj, 'man_launch_glc', 'sha')     # item 436 (b)(7), RC7: a data line
    r['video'] = os.path.isfile(os.path.join(root, 'rec_%s.mp4' % tag))
    r['hold_end'] = at.get('hold_end')          # item 511 (z)(4): data - the end of the U hold (enter_scene_s15.py)
    if log142 is None:
        r.update(entered=False, ident=[], fail=['no log'], log_rows={'the log': 'missing'}, nopb=None)
        return r
    s = A.scan_s(lp)
    std = A.scan_stdout(sp)
    sx = S9.scan_x(lp)
    sox = S9.scan_stdout_x(sp)
    sy = scan_y(lp)
    eg, end, fi = A.locate(s, spec['level'])
    r['entry_row'] = eg
    r['entered'] = eg is not None
    r['present_rows'] = len(s['rows'])
    r['first'] = None if fi is None else (s['rows'][fi][0], s['rows'][fi][1], s['rows'][fi][2])
    ident = [x for x in A.identities(s, std, spec['cls']) if not x[0].startswith('T-4')]
    ident = S9.ident_domain(ident, s, fi)                                # item 404 (v) - kept as one data row below
    r['ident_lo'] = ident_lo(s, fi, eg)
    ident = ident_rows(ident, s, sy, r['ident_lo'])                         # item 511 (z)(i): by the row that counts a line
    if spec['cls'] == 'T':
        ok4, d4 = S9.ident_t4(s, dict(pre0=False))
        ident.append(('T-4 AvTrace pipeline precache lines = G + C queued', ok4, d4))
    ident.append(('scan_x rows = scan_s rows', sx['rows'] == len(s['rows']), '%d / %d' % (sx['rows'], len(s['rows']))))
    ident.append(('scan_x lines = scan_s lines', sx['lines'] == s['lines'], '%d / %d' % (sx['lines'], s['lines'])))
    attr_ok = spec['cls'] == 'T' and all(ok for name, ok, _ in ident if name.startswith(('T-3', 'T-4')))
    r['attr_ok'] = attr_ok
    d142 = base['derive']
    agree = (d142['first'] is None and fi is None) or (
        d142['first'] is not None and fi is not None and d142['first'][0] == s['rows'][fi][0]
        and d142['frames_after_first'] == end - fi - 1)
    ident.append(('first scene frame and rows after it = the inherited sc142.derive', agree, '%s / %s' % (d142['first'],
                                                                                                          r['first'])))
    pv = (js.get('env') or {}).get('KYTY_S_PCW')

    def by_log(name, present, ok, detail):
        """Item 436 (b)(2): an admission row read from the log - 'missing' (the line is not in the log), 'differs' (present and
        not the form) or 'ok'."""
        r['admit'].append((name, bool(present and ok), str(detail)))
        r['log_rows'][name] = 'ok' if present and ok else ('missing' if not present else 'differs')
    by_log('every S-pcw: line (>= 1) = "%s" with the KYTY_S_PCW of the env of the arm (item 419 (v) Z3)' % SPCW_FMT,
           len(s['spcw']) >= 1, all(x == SPCW_FMT % pv for x in s['spcw']),
           '%s / env %s' % (';'.join(s['spcw'][:2]) or 'none', pv))
    by_log('0 lines GamePatch: in the log (item 342 (e))', True, sx['gamepatch'] == 0, sx['gamepatch'])
    by_log('the compatibility line carries the signature of the seal line "installed:"', sy['compat'] is not None,
           inst is not None and sy['compat'] is not None and (':' + inst[1] + ':') in (':' + sy['compat'] + ':'),
           (sy['compat'] or 'none')[:120])
    by_log('the translation cache line ends with the variant of the seal line "installed:"', sy['tcache'] is not None,
           inst is not None and sy['tcache'] is not None and sy['tcache'].endswith('/' + inst[2]), sy['tcache'] or 'none')
    r['window'] = dict(sy['win'], recover=sy['recover'])
    by_log('no window event minimized / Recovering Vulkan swapchain (item 273 (z))', True,
           sy['win'].get('minimized', 0) == 0 and sy['recover'] == 0,
           ' '.join('%s %d' % kv for kv in sorted(r['window'].items())) or 'none')
    # item 436 (b)(4), RC4: the end of the preparation screen - both lines and >= 1 FrameTrace row after the later one
    later = max(sy['ready_line'], sy['created_line']) if sy['ready_line'] and sy['created_line'] else None
    r['prep_end'] = dict(ready_line=sy['ready_line'], created_line=sy['created_line'], nopb_line=sy['nopb_line'],
                         later=later, rows_after=None if later is None else sum(1 for x in s['rows'] if x[4] > later))
    r['nopb'] = nopb_data(s, sy, inst)       # item 452 (b), RC1: data only, no outcome reads it
    r['compat'] = sy['compat']
    r['tcache'] = sy['tcache']
    r['dual_before'] = sy['dual_before']
    r['vke_log'] = sy['vke']
    r['prep'] = dict(queued=s['queued'], created_ms=s['created_ms'], ready=s['ready'], waited_ms=s['waited_ms'],
                     dload=s['dload'], disabled=s['disabled'], seed_installed=s['seed_installed'],
                     seed_ignored=s['seed_ignored'], cache_test=sox['any'], prepare_cold=sox['prepare_cold'],
                     prog_ms=sx['prog_ms'], prog_n=sx['prog_n'], rsave=len(s['rsave']),
                     rec_last=s['rsave'][-1][1] if s['rsave'] else None)
    r['screen'] = screen(r)
    if spec['val']:
        r['w295'] = A.w_form_rows(dict(entered=r['entered'], vke=r['vke']), s, std, eg, end)
    if fi is not None or eg is not None:
        prep = A.assign_prep(s)
        # item 511 (z)(5): an entered arm without a first scene frame - the anchor is the row before the entry row (the domain is
        # every row i >= eg), the reading 2 of sc_s for both readings (no first scene frame to add)
        if fi is not None:
            anc, rd1, akind = fi, 1, 'first scene frame'
        else:
            anc, rd1, akind = eg - 1, 2, 'entry line (item 511 (z)(5))'
        # item 436 (b)(1), RC1 - the letter: the domain is every row after the anchor to the end of the hold (the last row of the log)
        dom = domain_of(s, spec['level'], anc, end, r['attempt'], r['ended'], r['exited'], akind)
        r['dom'] = dom
        dend = dom['end']
        r['f1'] = A.freeze(s, anc, dend, prep, attr_ok, rd1)
        r['f2'] = A.freeze(s, anc, dend, prep, attr_ok, 2)
        r['split'] = split_at(s, anc, dend, end, r['f1'], attr_ok)
        # the reference of Red Team (no decision): the domain to the first scene change, as sealed in pred/11_s.md
        fr = A.freeze(s, anc, end, prep, attr_ok, rd1)
        r['ref'] = dict(after=frame_rows(s, anc, end), att100=A.attributed(fr, attr_ok, A.K3_US))
        for k, f in (('1', r['f1']), ('2', r['f2'])):
            t5a, t5b = f['T5']
            ident.append(('T-5 partition (reading %s)' % k, t5a == t5b, '%d / %d' % (t5a, t5b)))
        r['att100'] = A.attributed(r['f1'], attr_ok, A.K3_US)
        r['att1s'] = A.attributed(r['f1'], attr_ok, A.K2_US)
        r['att_pcw100'] = A.attributed_pcw(r['f1'], attr_ok, A.K3_US)
        r['unatt100'] = A.unattributed(r['f1'], attr_ok, A.K3_US)
        r['gates'] = A.gates(s, std, eg, spec, attr_ok)
        r['bvh'] = S9.bvh_col(sx, r['f1']['long'])
        r['early'] = S9.early9(s, r['f1'], attr_ok)
        r['early_d'] = early_distinct(r['early'])
        r['after'] = frame_rows(s, anc, dend)
        r['held_r1'] = r['f1']['window']['held'] + r['f1']['hold']['held']
        if fi is not None:
            r['pre_dom'], r['nof'] = pre_domain_lines(s, spec['level'], s['rows'][fi][0])
        else:
            r['pre_dom'], r['nof'] = None, sum(1 for e in s['skips'] if e[1] is None)    # (z)(5): no first scene frame
        r['held_long'] = [(x['n'], x['dt'], x['cls']) for x in r['f1']['long'] if x['held']]
        r['dt_after_first_us'] = d142.get('dt_after_first_us')
    r['ident'] = ident
    fail = ['admission: %s' % a[0] for a in r['admit'] if not a[1]]
    fail += ['identity: %s' % name for name, ok, _ in ident if ok is False]
    r['fail'] = fail
    return r


def ok_arm(r):
    return r is not None and not r['fail']


# ---------------------------------------------------------------------------------------------------------- members
def gate_word(r):
    """Item 355 (e): the catalogue installed - "ShaderSeed: installed" (log) and "Cache test mode: prepare-cold" (stdout)."""
    p = (r or {}).get('prep') or {}
    ok = p.get('seed_installed', 0) >= 1 and p.get('prepare_cold', 0) >= 1
    return ok, 'gates ok' if ok else 'CATALOGUE NOT INSTALLED (ShaderSeed: installed %d, Cache test mode: prepare-cold %d) - ' \
        'not an attempt of item 229 (e)(1), stop of the U series, a question to the lead' % (p.get('seed_installed', 0),
                                                                                              p.get('prepare_cold', 0))


def admission_gate(r):
    """Item 436 (b)(2), RC2: ('pre', rows) - a failing admission row before the run (json, env, binary, prereg, the cache
    protocol before the arm) or an UNCLASSED one; ('differs', rows) - a row by the log present and not the form, or a window
    event; ('missing', rows) - a row by the log whose line is not in the log; ('ok', []).  Item 452 (c): a row after the arm
    does not gate."""
    pre = [a[0] for a in r['admit'] if not a[1] and row_class(a[0]) in (C_PRE, None)]
    if pre:
        return 'pre', pre
    lr = r.get('log_rows') or {}
    dif = [k for k, v in lr.items() if v == 'differs']
    if dif:
        return 'differs', dif
    mis = [k for k, v in lr.items() if v == 'missing']
    if mis:
        return 'missing', mis
    return 'ok', []


def gated(ms, r):
    """Item 436 (b)(2): the members ms of one arm after the admission gate - every member UNDETERMINED on 'pre' and 'differs'
    and on 'missing' without a death marker (executor's variant); on 'missing' with a death marker E3-death is counted and the
    rest UNDETERMINED; the computed value is kept beside as data."""
    kind, rows = admission_gate(r)
    if kind == 'ok':
        return ms
    keep = ('E3-death',) if kind == 'missing' and death(r) else ()
    why = {'pre': 'an admission row before the run FAILS', 'differs': 'an admission row by the log is not the form',
           'missing': 'an admission row by the log is missing'}[kind]
    out = []
    for name, ok, det in ms:
        if name in keep:
            out.append((name, ok, det))
        else:
            out.append((name, None, 'undetermined: %s (%s); data: %s (%s)' % (
                why, '; '.join(rows[:3]), {True: 'ok', False: 'FAILS', None: 'undetermined'}[ok], det)))
    return out


def ident_fail(r):
    return [x for x in r['fail'] if x.startswith('identity: ')]


def e1_gate(r, shown_us):
    """Why the E1 members of a U arm are undetermined before their values (None when they are read): an identity row fails, the
    arm is not entered, no first scene frame, the catalogue not installed, or the domain presents < 120 s without a death marker
    (item 436 (b)(1))."""
    g, _ = gate_word(r)
    if ident_fail(r) or not r.get('entered') or 'f1' not in r or not g:
        return 'identity %s; entered %s; first scene frame %s; catalogue %s' % (ident_fail(r)[:3] or 'ok', r.get('entered'),
                                                                                r.get('first'), 'ok' if g else 'not installed')
    if shown_us < DOMAIN_MIN_US and not death(r):
        return 'the domain presents %.3f s < %d s without a death marker (item 436 (b)(1))' % (shown_us / 1e6,
                                                                                              DOMAIN_MIN_US // 1000000)
    return None


def e1_members(r, a, att100, shown_us):
    why = e1_gate(r, shown_us)
    if why is not None:
        return [(m, None, 'undetermined: %s' % why) for m in ('E1-skip', 'E1-held', 'E1-attr')]
    return [('E1-skip', a['skip_rows'] == 0 and a['skip_lines'] == 0,
             'rows with a skip %d, skipped-draw lines %d' % (a['skip_rows'], a['skip_lines'])),
            ('E1-held', a['held'] == 0, 'held flips %d (reading 1 with the first scene frame %d)' % (a['held'], r['held_r1'])),
            ('E1-attr', None if att100 is None else att100 == 0,
             'attributed >= 100 ms %s (PCW %s)' % (att100, r.get('att_pcw100')))]


def ref_members(r):
    """Item 436 (b)(1): the REFERENCE of Red Team - E1 on the domain to the first scene change, >= 120 s presented else
    UNDETERMINED; the admission gate as for the letter.  No decision rides on it."""
    if r is None:
        return [('arm made', None, 'not made')]
    if 'f1' not in r:
        return gated(e1_members(r, None, None, 0), r)
    ms = e1_members(r, r['ref']['after'], r['ref']['att100'], r['dom']['ref_shown_us'])
    if r['dom']['ref_shown_us'] < DOMAIN_MIN_US and e1_gate(r, DOMAIN_MIN_US) is None:
        ms = [(m, None, 'undetermined: the reference domain presents %.3f s < %d s (item 436 (b)(1), Red Team)' % (
            r['dom']['ref_shown_us'] / 1e6, DOMAIN_MIN_US // 1000000)) for m, _, _ in ms]
    return gated(ms, r)


def members_u(r):
    """Item 229 (e)(1), (3) on one U arm: [(member, True / False / None, detail)]; E1 on the domain of item 436 (b)(1) (the
    letter), the admission gate of item 436 (b)(2)."""
    if r is None:
        return [('arm made', None, 'not made')]
    g, gw = gate_word(r)
    out = [('catalogue installed (gates)', True if g else None, gw)]
    if 'f1' not in r:
        out += e1_members(r, None, None, 0)
    else:
        out += e1_members(r, r['after'], r['att100'], r['dom']['shown_us'])
    sec, kind = r.get('screen') or (None, 'none')
    if kind == 'measured':
        out.append(('E1-screen', sec <= PREP_LIMIT_S, '%.1f s' % sec))
    elif kind == 'lower bound' and sec > PREP_LIMIT_S:
        out.append(('E1-screen', False, '> %.1f s (lower bound)' % sec))
    else:
        out.append(('E1-screen', None, 'undetermined (%s%s)' % (kind, '' if sec is None else ' %.1f s' % sec)))
    gl = r.get('glitch')
    if not r.get('video') or gl is None:
        out.append(('E3-video', None, 'no video or no glitch file'))
    else:
        out.append(('E3-video', gl['video_frames'] >= FRAMES_VIDEO and gl['glitches'] == 0 and bool(r.get('sheet_file')),
                    '%d frames, %d glitches, sheet %s' % (gl['video_frames'], gl['glitches'], bool(r.get('sheet_file')))))
    out.append(('E3-death', not r['marks'] and not r['ended'] and not r['exited'],
                ';'.join(m['kind'] for m in r['marks']) or ('hold_exit / ENDED / exited' if r['ended'] or r['exited']
                                                              else 'none')))
    return gated(out, r)


def members_w(r):
    """Item 229 (e)(3): the W of Sky Garden."""
    if r is None:
        return [('arm made', None, 'not made')]
    g, gw = gate_word(r)
    out = [('catalogue installed (gates)', True if g else None, gw)]
    if gating_fail(r) or not r.get('entered') or not g:
        out.append(('W admitted and entered', None, 'admission / identity %s; entered %s' % (gating_fail(r)[:3] or 'ok',
                                                                                             r.get('entered'))))
    held = r['derive142'].get('dt_after_first_us') or 0
    out.append(('W >= 300 s presented after the first scene frame', held >= HOLD_W_US if r.get('first') else None,
                '%d us' % held))
    out.append(('W 0 [Vulkan][E] (log + stdout)', (r.get('vke') or 0) == 0, r.get('vke')))
    for name, ok, det in r.get('w295') or []:
        out.append((name, ok, det))
    out.append(('W "DualSrcBlend: supported=1 enabled=1" before the first GuestOut line (item 300 (b)(4))',
                bool(r['dual_before']) if 'dual_before' in r else None, r.get('dual_before')))
    out.append(('E3-death', not r['marks'] and not r['ended'] and not r['exited'],
                ';'.join(m['kind'] for m in r['marks']) or ('hold_exit / ENDED / exited' if r['ended'] or r['exited']
                                                              else 'none')))
    return gated(out, r)


def death(r):
    """A death marker of sc142 or hold_exit / ENDED / exited (the predicate of E3-death)."""
    return bool(r.get('marks')) or bool(r.get('ended')) or bool(r.get('exited'))


def entry_state(r):
    """Item 428 (g), V7: the field "entered" of one arm - ('yes', why) the log carries "Level has started: <level>"; ('no', why)
    an attempt with a log, without the line, without a death marker (nor hold_exit / ENDED / exited) and without a window event
    (minimized / Recovering Vulkan swapchain); ('void', why) otherwise (not made, no log, a death marker or a window event
    without the line) - not evidence that -lvl does not enter the level.  Item 436 (b)(3), RC3 (item 434 (b)): a failing
    admission or identity row -> 'void'.  Item 436 (b)(4), RC4: 'no' only when the log carries both lines of the end of the
    preparation screen and >= 1 FrameTrace row after the later one; else 'void' ("the preparation screen not passed")."""
    if r is None:
        return 'void', 'not made'
    if 'window' not in r:
        return 'void', 'no log'
    if r.get('fail'):
        return 'void', 'an admission / identity row FAILS (item 434 (b)): %s' % '; '.join(r['fail'][:2])
    if r.get('entered'):
        return 'yes', 'Level has started'
    if death(r):
        return 'void', 'a death marker without the entry line'
    w = r.get('window') or {}
    if w.get('minimized', 0) or w.get('recover', 0):
        return 'void', 'a window event without the entry line'
    pe = r.get('prep_end') or {}
    if pe.get('later') is None or not pe.get('rows_after'):
        return 'void', 'the preparation screen not passed (ShaderPreparation: ready line %s, PipelinePrecache: all pipelines ' \
            'created line %s, FrameTrace rows after the later %s; "no pipelines.bin yet" line %s)' % (
                pe.get('ready_line'), pe.get('created_line'), pe.get('rows_after'), pe.get('nopb_line'))
    return 'no', 'no entry line in a clean attempt after the preparation screen'


def not_enterable(get):
    """Item 428 (g): per level of the 19 (level, entry of k_NN, entry of u_NN, not enterable) - not enterable by -lvl when both
    arms are 'no' [c of two logs]."""
    rows = []
    for lv, kt, ut in zip(LIST13, K_TAGS, U_TAGS):
        ks, us = entry_state(get(kt)), entry_state(get(ut))
        rows.append((lv, ks, us, ks[0] == 'no' and us[0] == 'no'))
    return rows


def entered_word(excl, wall, ww):
    """Item 428 (g): (word, words of the U arms in the denominator) - the U arms of the levels outside "not enterable": PASS
    when every one and w13 PASS with a denominator >= 1; FAIL on any FAIL (w13 included); else UNDETERMINED."""
    den = [w for w, x in zip(wall, excl) if not x]
    word = sub_word(den + [ww])
    if word == 'PASS' and not den:
        word = 'UNDETERMINED'
    return word, den


def arm_word(ms):
    if any(ok is False for _, ok, _ in ms):
        return 'FAIL'
    if any(ok is None for _, ok, _ in ms):
        return 'UNDETERMINED'
    return 'PASS'


def sub_word(words):
    if 'FAIL' in words:
        return 'FAIL'
    if 'UNDETERMINED' in words:
        return 'UNDETERMINED'
    return 'PASS'


def read_known(get):
    """Item 229 (e)(1), (3): the word KNOWN_SCENES and the words of (e)(1) alone and (e)(3) alone."""
    out = []
    w1, w3, wall, wref = [], [], [], []
    count = {}
    for t in U_TAGS:
        r = get(t)
        ms = members_u(r)
        e1 = [m for m in ms if not m[0].startswith('E3-')]
        e3 = [m for m in ms if m[0].startswith('E3-') or m[0] == 'catalogue installed (gates)']
        w1.append(arm_word(e1))
        w3.append(arm_word(e3))
        wall.append(arm_word(ms))
        rm = ref_members(r)
        wref.append(arm_word([m for m in ms if m[0] in ('catalogue installed (gates)', 'E1-screen')] + rm))
        for name, ok, _ in ms:
            c = count.setdefault(name, [0, 0, 0])
            c[0 if ok is True else (1 if ok is False else 2)] += 1
        out.append('%s %-30s %s; %s' % (t, SPEC[t]['level'], wall[-1], '; '.join('%s %s (%s)' % (
            n, {True: 'ok', False: 'FAILS', None: 'undetermined'}[ok], d) for n, ok, d in ms)))
        out.append('%s domain (item 436 (b)(1)): %s; reference (Red Team, to the scene change, no decision): (e)(1) %s (%s)' % (
            t, fmt_dom(r), wref[-1], '; '.join('%s %s' % (n, {True: 'ok', False: 'FAILS', None: 'undetermined'}[ok])
                                               for n, ok, _ in rm)))
        out.append('%s GLCache at the launch man_launch_glc sha256 %s (item 436 (b)(7); not the driver cache of a first run of '
                   'the user)' % (t, (r or {}).get('glc_launch') or '-'))
        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))
        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))
        out.append('%s hold end (item 511 (z)(4), data): %s' % (t, fmt_hold(r)))
    rw = get('w13')
    mw = members_w(rw)
    ww = arm_word(mw)
    out.append('w13 %-30s %s; %s' % (SKY, ww, '; '.join('%s %s (%s)' % (n, {True: 'ok', False: 'FAILS', None: 'undetermined'}[ok], d)
                                                       for n, ok, d in mw)))
    out.append('w13 domain (item 436 (b)(1), data; w13 carries no E1 member): %s' % fmt_dom(rw))
    out.append('w13 GLCache at the launch man_launch_glc sha256 %s (item 436 (b)(7))' % ((rw or {}).get('glc_launch') or '-'))
    out.append('w13 data of item 446 (b) (item 452 (b), no outcome reads it): %s' % fmt_nopb(rw))
    out.append('w13 rows after the arm (item 452 (c)): %s' % fmt_post(rw))
    for name, (p, f, u) in count.items():
        out.append('member %s: ok %d, fails %d, undetermined %d of %d' % (name, p, f, u, len(U_TAGS)))
    word1 = sub_word(w1)
    word3 = sub_word(w3 + [ww])
    word = sub_word(wall + [ww])
    out.append('(e)(1) alone (19 U arms, members skip / held / attr / screen): %s; PASS %d of %d' % (word1, w1.count('PASS'),
                                                                                                    N_KNOWN))
    out.append('(e)(1) REFERENCE of Red Team (item 436 (b)(1): the E1 domain to the first scene change, >= 120 s; no decision): '
               '%s; PASS %d / FAIL %d / UNDETERMINED %d of %d' % (sub_word(wref), wref.count('PASS'), wref.count('FAIL'),
                                                                  wref.count('UNDETERMINED'), N_KNOWN))
    out.append('(e)(3) alone (video, death markers, W of Sky Garden): %s; W %s' % (word3, ww))
    out.append('KNOWN_SCENES (item 229 (e)(1) with (3)): %s - arms PASS %d / FAIL %d / UNDETERMINED %d of %d, W %s; the lead '
               'sheets and the decision - S13c' % (word, wall.count('PASS'), wall.count('FAIL'), wall.count('UNDETERMINED'),
                                                   N_KNOWN, ww))
    ent = not_enterable(get)
    for (lv, ks, us, x), t in zip(ent, U_TAGS):
        out.append('entry %s %-30s k %s (%s), u %s (%s) -> %s' % (t, lv, ks[0], ks[1], us[0], us[1],
                                                                 'NOT ENTERABLE by -lvl' if x else 'in the denominator'))
    wE, den = entered_word([x for _, _, _, x in ent], wall, ww)
    out.append('KNOWN_SCENES_ENTERED (item 428 (g), V7: the levels outside "not enterable"): %s - denominator %d of %d, arms '
               'PASS %d / FAIL %d / UNDETERMINED %d, W %s; not enterable by -lvl: %s' % (
                   wE, len(den), N_KNOWN, den.count('PASS'), den.count('FAIL'), den.count('UNDETERMINED'), ww,
                   ' '.join(lv for lv, _, _, x in ent if x) or 'none'))
    return word, out


def read_k(get):
    """The collection arms: data per arm (entered, recipes written, the post copy, death markers, window events)."""
    out = []
    for t in K_TAGS:
        r = get(t)
        if r is None:
            out.append('%s %-30s not made' % (t, SPEC[t]['level']))
            continue
        p = r.get('prep') or {}
        out.append('%s %-30s arm %s; entered %s first %s; recipes saved lines %s last %s; created %s ms; death markers %s; '
                   'window %s; entry %s' % (t, r['level'], 'PASS' if ok_arm(r) else 'FAIL %s' % r['fail'][:3], r.get('entered'),
                                  r.get('first'), p.get('rsave'), p.get('rec_last'), p.get('created_ms'),
                                  ';'.join(m['kind'] for m in r['marks']) or 'none', r.get('window'), entry_state(r)))
        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))
        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))
    return out


# ---------------------------------------------------------------------------------------------------------- order
def made_fn(root=LINK_DIR):
    def made(t):
        return os.path.isfile(os.path.join(root, '%s.json' % t)) or os.path.isfile(os.path.join(root, 'attempt_%s.txt' % t))
    return made


def allowed(tag, made, get, export_ok):
    """Order and conditions of item 408 (l): (rc, reason) - rc 0 allowed, 1 order, 6 a condition not met (a question to the
    lead)."""
    if tag not in SPEC:
        return 2, 'unknown tag'
    if made(tag):
        return 1, 'already made'
    i = SEQ.index(tag)
    for t in SEQ[:i]:
        r = get(t) if made(t) else None
        if r is not None and r['marks']:
            return 6, 'the series stops at the first death marker (%s)' % t
        if r is not None and ((r.get('window') or {}).get('minimized', 0) or (r.get('window') or {}).get('recover', 0)):
            return 6, 'a window event in %s (item 273 (z)) - a question to the lead about a repeat' % t
    prev = SEQ[i - 1] if i > 0 else None
    if prev and not made(prev):
        return 1, '%s not made' % prev
    spec = SPEC[tag]
    if spec['group'] == 'u' and spec['k'] == 0 and not export_ok():
        return 6, 'the export of the collected catalogue is not done or does not verify (seedexp_s15.py)'
    if spec['group'] in ('u', 'w'):
        for t in U_TAGS:
            if t == tag:
                break
            g, gw = gate_word(get(t))
            if not g:
                return 6, '%s: %s' % (t, gw)
    return 0, 'ok'


# ---------------------------------------------------------------------------------------------------------- printing
def fmt_dom(r):
    """Item 436 (b)(1): the end of the domain and its cause, the scene changes inside it (name, log line), its rows and
    presented time, the skips / held flips / attributed >= 100 ms before and after the first scene change, the reference."""
    if r is None:
        return 'not made'
    d = r.get('dom')
    if d is None:
        return 'no domain (entered %s, first scene frame %s)' % (r.get('entered'), r.get('first'))
    sp = r['split']

    def part(x):
        return 'rows %d, rows with a skip %d, skipped-draw lines %d, held flips %d, attributed >= 100 ms %s' % (
            x['rows'], x['skip_rows'], x['skip_lines'], x['held'], x['attr100'])
    return ('anchor %s; end row %d (cause: %s), rows %d, presented %.3f s (minimum %d s); scene changes inside: %s; before the '
            'first scene change: %s; after it: %s; reference to the first scene change: rows %d, presented %.3f s' % (
                d.get('anchor', 'first scene frame'), d['end'], d['cause'], d['rows'], d['shown_us'] / 1e6, DOMAIN_MIN_US // 1000000,
                ', '.join('%s (row %d, log line %d)' % (nm or '<empty name>', g, ln) for g, nm, ln in d['changes']) or 'none',
                part(sp['before']), part(sp['after']), d['ref_rows'], d['ref_shown_us'] / 1e6))


def fmt_hold(r):
    """Item 511 (z)(4): the end of the hold of the attempt (enter_scene_s15.py hold_end) - data."""
    h = (r or {}).get('hold_end')
    if not h:
        return 'none (a fixed hold or no U hold record)'
    return 'cause %s, anchor %s, presented after the anchor %.3f s, video frames %s, rows %s' % (
        h.get('cause'), h.get('anchor'), (h.get('shown_us') or 0) / 1e6, h.get('video_frames'), h.get('rows'))


def fmt_arm(r):
    o = ['ARM %s level %s class %s: %s; sc142 outcome %s (%s); log %s; binary %s' % (
        r['tag'], r['level'], r['cls'], 'PASS' if not r['fail'] else 'FAIL', r['outcome142'], r['reason142'],
        (r.get('log_sha') or 'MISSING')[:16], (r.get('binary') or '-')[:16])]
    for name, ok, det in r['admit']:
        o.append('  %-4s admit %s %s (%s)' % ('PASS' if ok else 'FAIL', row_class(name) or 'UNCLASSED', name, det))
    kind, rows = admission_gate(r)
    o.append('  admission gate (item 436 (b)(2)): %s%s' % (kind, (' - ' + '; '.join(rows)) if rows else ''))
    o.append('  rows after the arm (item 452 (c)): %s' % fmt_post(r))
    for name, ok, det in r.get('ident', []):
        o.append('  %-4s ident %s (%s)' % ('n/a' if ok is None else ('PASS' if ok else 'FAIL'), name, det))
    p = r.get('prep') or {}
    if p:
        o.append('  preparation: queued %s created %s ms ready %s wait %s ms; driver cache loaded %s disabled %d; seed installed %d '
                 'ignored %d; Cache test mode %d (prepare-cold %d); recipes saved lines %d; screen %s' % (
                     p['queued'], p['created_ms'], p['ready'], p['waited_ms'], p['dload'], p['disabled'], p['seed_installed'],
                     p['seed_ignored'], p['cache_test'], p['prepare_cold'], p['rsave'], r.get('screen')))
    o.append('  hold end (item 511 (z)(4), data): %s' % fmt_hold(r))
    if 'f1' not in r:
        o.append('  entered %s, first scene frame %s - no freeze reading' % (r.get('entered'), r.get('first')))
    else:
        o.append('  entered yes; first scene frame (n, dt, draws) %s; anchor of the domain %s; attribution %s' % (
            r['first'], r['dom'].get('anchor'), 'DETERMINED' if r['attr_ok'] else 'UNDETERMINED'))
        a = r['after']
        o.append('  after the first scene frame, domain of item 436 (b)(1): rows with a skip %d, skipped-draw lines %d, held flips '
                 '%d (reading 1 %d)' % (a['skip_rows'], a['skip_lines'], a['held'], r['held_r1']))
        o.append('  domain: %s' % fmt_dom(r))
        o.append('  data (item 414 (g)(5)-(7)): skipped-draw lines after the entry line with frame= below the first scene frame %s; '
                 'skipped-draw lines without frame= %d' % (r['pre_dom'], r['nof']))
        f = r['f1']
        bv = dict(r['bvh'])
        o.append('  frames dt >= 100 ms (n dt part class attribution PREP held BvhLoopCapTrip(i-1..i)): %s' % (
            '; '.join('%d %d %s %s %s %d %s %d' % (x['n'], x['dt'], x['part'], x['cls'], x['attr'], x['prep'],
                                                  'h' if x['held'] else '-', bv.get(x['n'], 0)) for x in f['long']) or 'none'))
        o.append('  held frames >= 100 ms with their class (data): %s' % (r['held_long'] or 'none'))
        o.append('  attributed >= 100 ms %s (PCW %s), >= 1 s %s; not attributed %s' % (
            r['att100'], r['att_pcw100'], r['att1s'], A.fmt_unattr(r['unatt100'])))
        e = r['early']
        ed = r['early_d']
        if e is None:
            o.append('  S-early: undetermined')
        else:
            for x in ed['events']:
                if x['kind'] == 'series':
                    o.append('  S-early event series n %s lead %s async creation us %s' % (x['n'], x['lead'], x['cost']))
                else:
                    o.append('  S-early event frame n %s lead %s cost (PREP + async creation us of i-2..i+1) %s, PREP %s' % (
                        x['n'], x['lead'], x['cost'], x['cost_prep']))
            o.append('  S-early: distinct events %d (item 414 (g)(1)), known %d, lead < cost %d' % (
                len(ed['events']), ed['known'], ed['short']))
    o.append('  entered (item 428 (g), item 436 (b)(3)-(4)): %s (%s)' % entry_state(r))
    pe = r.get('prep_end') or {}
    o.append('  end of the preparation screen (item 436 (b)(4)): ShaderPreparation: ready line %s; PipelinePrecache: all '
             'pipelines created line %s; FrameTrace rows after the later %s; "no pipelines.bin yet" line %s' % (
                 pe.get('ready_line'), pe.get('created_line'), pe.get('rows_after'), pe.get('nopb_line')))
    o.append('  data of item 446 (b) (item 452 (b), no outcome reads it): %s' % fmt_nopb(r))
    o.append('  GLCache at the launch man_launch_glc sha256 %s (item 436 (b)(7))' % (r.get('glc_launch') or '-'))
    g = r['glitch']
    o.append('  video: %s; sheet %s; death markers %s; [Vulkan][E] %s; window %s; compatibility %s; translation cache %s' % (
        'n/a' if g is None else '%d frames, %d glitches' % (g['video_frames'], g['glitches']), r.get('sheet_file'),
        ';'.join(m['kind'] for m in r['marks']) or 'none', r['vke'], r.get('window'), (r.get('compat') or '-')[:100],
        r.get('tcache')))
    if r['group'] == 'u':
        o.append('  members: %s' % '; '.join('%s %s' % (n, {True: 'ok', False: 'FAILS', None: 'undetermined'}[ok])
                                              for n, ok, _ in members_u(r)))
        o.append('  reference of Red Team (item 436 (b)(1), no decision): %s' % '; '.join(
            '%s %s' % (n, {True: 'ok', False: 'FAILS', None: 'undetermined'}[ok]) for n, ok, _ in ref_members(r)))
    elif r['group'] == 'w':
        o.append('  members: %s' % '; '.join('%s %s' % (n, {True: 'ok', False: 'FAILS', None: 'undetermined'}[ok])
                                              for n, ok, _ in members_w(r)))
    return o


# ---------------------------------------------------------------------------------------------------------- seal
SEALED_NAMES = ('s15/go_s15.sh', 's15/sc_s15.py', 's15/test_sc_s15.py', 's15/mut_sc_s15.py', 's15/test_go_s15.py',
                's15/seedexp_s15.py', 's15/test_seedexp_s15.py', 's15/enter_scene_s15.py', 's15/mk_enter_s15.py',
                's15/test_enter_scene_s15.py', 's15/hmut_s15.py', 's15/ident_s15.py', 's15/sg_s15.py',
                's13/lvl_s13.py', 's13/lvl_s13.out.txt', 's9/sc_s9.py',
                's9/enter_scene_s9.py', 'sc_s.py', 'cachex_s.py', 'idle142.py', 'procload.py', 'run_safety99.py',
                'launch_run.py', 'gates_default.txt', 'sheet142.py', 'fgcpu143.py', 'C:/kyty/s142/sc142.py',
                'C:/kyty/scripts/s51_vidglitch.py', 'C:/kyty/KytyPS5/tools/shader_seed.py', 's7/recipes_s7.py')


RX_EDITION = re.compile(r'^(installed|edition): ')


RX_EDBASE = re.compile(r'^edition: base (\S+) sha256 ([0-9a-f]{64})$')


def edition_rows(base=None, ed=None, base_rel=None):
    """The edition 13b (when it exists): every line of 13 except the lines "installed:" / "edition:" is in 13b in the same order
    and nothing else; 13 says "installed: PENDING" and carries no line "edition:"; 13b names the installed binary; item 436
    (b)(6), RC6: 13b carries exactly one line "edition: base pred/14_s.md sha256 <64 hex>" and its sha256 = the sha256 of the
    file of the seal 13.  Returns [(name, ok, detail)]."""
    base = base or SEAL_BASE
    ed = ed or SEAL_B
    base_rel = base_rel or SEAL_BASE_REL
    if not os.path.isfile(ed):
        return []
    rows = []
    a = [x.rstrip(NL) for x in open(base, encoding='utf-8')] if os.path.isfile(base) else None
    b = [x.rstrip(NL) for x in open(ed, encoding='utf-8')]
    if a is None:
        return [('edition 13b: the seal 13 exists', False, base)]
    ka = [x for x in a if not RX_EDITION.match(x)]
    kb = [x for x in b if not RX_EDITION.match(x)]
    rows.append(('edition 13b: every line of 13 but "installed:" / "edition:" is in 13b, in order, nothing else', ka == kb,
                 '%d / %d lines' % (len(ka), len(kb))))
    ia, ib = seal_installed(base), seal_installed(ed)
    rows.append(('edition 13b: 13 says "installed: PENDING", 13b names the installed binary', ia is not None and
                 ia[0] == 'PENDING' and ib is not None and ib[0] != 'PENDING', '%s / %s' % (ia and ia[0][:16], ib and ib[0][:16])))
    rows.append(('edition 13b: the seal 13 carries no line "edition:"', not any(x.startswith('edition:') for x in a),
                 sum(1 for x in a if x.startswith('edition:'))))
    eb = [x for x in b if x.startswith('edition:')]
    m = RX_EDBASE.match(eb[0]) if len(eb) == 1 else None
    bsha = hashlib.sha256(open(base, 'rb').read()).hexdigest()
    rows.append(('edition 13b: one line "edition: base %s sha256 <64 hex>" = the sha256 of the seal 13 (item 436 (b)(6))' % base_rel,
                 m is not None and m.group(1) == base_rel and m.group(2) == bsha,
                 '%d lines "edition:"; %s / %s' % (len(eb), (m.group(2)[:16] if m else '-'), bsha[:16])))
    return rows


def check_seal(pred=None, root=ROOT, me=None, game=None):
    pred = pred or current_seal()
    rows = []
    if not os.path.isfile(pred):
        return False, [('seal file', False, pred)], None
    seen = {}
    for line in open(pred, encoding='utf-8'):
        m = RX_SEAL.match(line.rstrip('\n'))
        if m:
            seen[m.group(2)] = m.group(1)
    for name in SEALED_NAMES:
        if name not in seen:
            rows.append((name, False, 'no seal line'))
    for name, sh in sorted(seen.items()):
        p = name if name.startswith('C:/') else os.path.join(root, name)
        now = A.sha_file(p) if os.path.isfile(p) else None
        rows.append((name, now == sh, (now or 'missing')[:16]))
    mine = A.sha_file(me or os.path.abspath(__file__))
    rows.append(('this scorer in the seal', seen.get('s15/sc_s15.py') == mine, mine[:16]))
    inst = seal_installed(pred)
    rows.append(('one line "installed: PENDING" or "installed: <sha256> <signature> <variant>" (S9r2 observation 3)',
                 inst is not None, 'malformed or not one line' if inst is None else ' '.join(x or '' for x in inst).strip()))
    if pred == current_seal():
        rows.extend(edition_rows())
    if inst is not None and inst[0] != 'PENDING' and game is not None:
        now = A.sha_file(game) if os.path.isfile(game) else None
        rows.append(('the installed binary now = the line "installed:"', now == inst[0], (now or 'missing')[:16]))
    return all(r[1] for r in rows), rows, inst


# ---------------------------------------------------------------------------------------------------------- main
def make_get(root=LINK_DIR, pred=None):
    pred = pred or current_seal()
    memo = {}
    psha = A.sha_file(pred) if os.path.isfile(pred) else None
    inst = seal_installed(pred)

    def get(t):
        if t not in memo:
            memo[t] = score_arm(t, root, psha, pred, inst)
        return memo[t]
    return get


GAME = 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'


def main(argv=None, root=LINK_DIR, pred=None):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--tag')
    ap.add_argument('--read', action='store_true')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--allowed')
    ap.add_argument('--plan')
    ap.add_argument('--check-seal', action='store_true')
    ap.add_argument('--seal', default=None)
    ap.add_argument('--game', default=None)
    ap.add_argument('--json-out', default=None)
    ap.add_argument('--seeds-check', action='store_true')
    ap.add_argument('--export-state', action='store_true')
    ap.add_argument('--installed', action='store_true')
    ap.add_argument('--seal-path', action='store_true')
    a = ap.parse_args(argv)
    pred = pred or current_seal()
    if a.seal_path:
        print(os.path.relpath(pred, ROOT).replace(chr(92), '/'))
        return 0
    if a.installed:
        inst = seal_installed(a.seal or pred)
        print('installed %s' % ('MALFORMED' if inst is None else ' '.join(x for x in inst if x)))
        return 0 if inst is not None else 1
    if a.seeds_check:
        live, n = manifest_sha(SEEDS_PATH + '/PPSA21564')
        fsha = A.sha_file(SEEDS_MANI) if os.path.isfile(SEEDS_MANI) else None
        print('seeds sha %s files %d (seeds_manifest.txt %s) %s' % (live, n, fsha, 'MATCH' if live and live == fsha else 'DIFF'))
        return 0 if live and live == fsha else 1
    if a.export_state:
        ok, rows, d = export_state(root)
        for name, good, det in rows:
            print('%-4s %s %s' % ('OK' if good else 'BAD', name, det))
        print('removed duplicates (F17) of the export: %s; compatibility %s' % (d['dup'], d['compat']))
        print('EXPORT STATE: %s' % ('OK' if ok else 'NOT OK'))
        return 0 if ok else 1
    if a.plan:
        if a.plan not in SPEC:
            print('usage: unknown tag %s' % a.plan)
            return 2
        print(plan(SPEC[a.plan]))
        return 0
    if a.check_seal:
        ok, rows, inst = check_seal(a.seal or pred, game=a.game)
        for name, good, det in rows:
            print('%-4s %s %s' % ('OK' if good else 'BAD', name, det))
        print('SEAL: %s' % ('PASS' if ok else 'FAIL'))
        return 0 if ok else 1
    get = make_get(root, pred)
    made = made_fn(root)
    if a.allowed:
        rc, why = allowed(a.allowed, made, get, lambda: export_state(root)[0])
        print('ALLOWED %s: %s (%s)' % (a.allowed, 'yes' if rc == 0 else 'no', why))
        return rc
    if a.tag:
        if a.tag not in SPEC:
            print('usage: unknown tag %s' % a.tag)
            return 2
        r = get(a.tag)
        if r is None:
            print('ARM %s: %s' % (a.tag, 'ATTEMPT MADE, NO JSON (instrument)' if made(a.tag) else 'NO_RUN'))
            return 1
        print(NL.join(fmt_arm(r)))
        jp = a.json_out or os.path.join(root, 'runs_s', '%s.score.json' % a.tag)
        os.makedirs(os.path.dirname(os.path.abspath(jp)), exist_ok=True)
        json.dump(dict((k, v) for k, v in r.items()), open(jp, 'w', encoding='utf-8'), indent=1, default=list)
        return 0 if not r['fail'] else 1
    if a.read or a.summary:
        print(NL.join(['READ collection arms (item 408 (l))'] + read_k(get)))
        ok, rows, d = export_state(root)
        print('READ export: %s; %s; removed duplicates (F17) %s' % ('OK' if ok else 'NOT OK', '; '.join(
            '%s %s' % (n, 'ok' if g else 'BAD') for n, g, _ in rows), d['dup']))
        _, lines = read_known(get)
        print(NL.join(['READ known scenes (item 229 (e)(1), (3))'] + lines))
        return 0
    print('usage: sc_s15.py --tag T | --read | --summary | --allowed T | --plan T | --check-seal | --seeds-check | '
          '--export-state | --installed')
    return 2


if __name__ == '__main__':
    sys.exit(main())
