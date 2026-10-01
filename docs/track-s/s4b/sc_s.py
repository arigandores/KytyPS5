#!/usr/bin/env python3
"""sc_s.py - the scorer of track S, second wave (link S3, HPP-313; ROADMAP "SESSION 122" item 241 (v)-(z), item 229 (g)(3),
(d), (e); S0 docs/track-s/s0-design.md sections 3-4 with the S1 corrections RC2-RC17).

INHERITANCE (item 241 (v)(11)): C:/kyty/s142/sc142.py is loaded UNCHANGED from its own path after a sha256 check (SHA142
below); its scan(), derive(), markers(), validation(), opcode_diff(), read_glitch(), idx_count(), outcome() are used as
they are, and its 217 fixtures (C:/kyty/s142/test_sc142.py) keep running against that very file.  This file only adds.

ONE ARM = one process of the emulator (item 241 (g)): tag -> link directory (S4 C:/kyty/s288/s4, S6 C:/kyty/s288/s6), level,
environment class M / T / G (item 241 (g)(5), S0 section 3.4), restore mode, hold.  Files of an arm in its link directory:
<tag>.json (enter_scene.py), log_<tag>.txt, stdout_<tag>.txt, <tag>.stdout.txt, glitch_<tag>.txt, rec_<tag>.mp4[.idx],
runs_s/<tag>.cache.json (go_s.sh: manifests and restores of item 241 (g)(1)-(3)); the score goes to runs_s/<tag>.score.json.

READING (item 241 (v)); groups: the group of row i = the log lines after main FrameTrace row i-1 and before row i (the event
lines a flip's threads wrote before that flip's row).  Event lines carry the index of the NEXT main row.
  (1) unit of "frames with a skip" = held flips, sum skc_held_inc; T-6: = the number of distinct frame= of the
      "AsyncPipelines: skipped draw" lines.  Rows with a skip and skipped draws are printed beside.  Reading 1 (the
      letter): a held series counts WITH the first scene frame when that frame is held; reading 2: from the next row.
  (2) freeze, three measures: dt of a presented row; the visible gap of a held series (sum dt of the series rows + dt of the
      next row); gap_pipe = gap - sum dt of the series rows (the closing row included) with dt >= 100 ms of class PRIO ONLY
      (item 250 (g)(2): PCW counts "to the shaders"); the former letter of (v)(2) (minus PCW and PRIO) is printed as the second
      reading "(v)(2) before item 250" (gap_pipe_old).  Thresholds 100 ms and 1 s on each.  "Attributed >= X" (item 250 (g)(1))
      = a presented row with dt >= X of attribution SHADER or of class PCW, or a series with gap_pipe >= X; the rows of
      class PCW are printed apart ("of them PCW n"), and beside it the not attributed presented rows >= X by class (RC8).
  (3) classes of a row with dt >= 100 ms in this order: PCW (a "Vulkan pipeline cache: saved" or "PipelinePrecache: saved"
      line in group i or i+1) -> SHADER ((4)) -> PRIO (sum "PriorityStall: us" >= dt/2 and cpu_gpu_us < dt/2 under BOTH
      conventions: the stall lines of group i (S0) and of group i+1; both printed) -> GPUTHR (cpu_gpu_us >= dt/2) -> WAIT.
  (4) attribution only on a T arm with T-3 and T-4 holding, else "undetermined" (never PASS).  PREP(i) = sum over the
      AvTrace lines assigned to row i of translate_us + compile_us (AvTrace: shader), us of a synchronous "pipeline gfx"
      (no suffix), us of "pipeline cs ... sync", waited_us, us of "shader-cache load"; a line of group g is assigned to ONE
      row: the largest dt among rows g-1 .. g+2 (its row windows i-2 .. i+1), the earliest on a tie.  SHADER if
      dt - PREP < 100 000 or a skipped-draw line or an "AvTrace: pipeline gfx ... async" line lies in groups i-2 .. i+1;
      "partly" when PREP >= dt/2; TR and PL printed apart.
  (5) identities: T-1 sum skc_ap_skip = skipped-draw lines (below 200 000 lines); T-2 min(64, sum skc_held_inc) = "flip N
      held" lines; T-5 series gaps + dt of presented rows outside the series = sum dt of the domain (per reading); T-6 (the
      main one); sum skc_held = 0; skc_bad printed (no control); T arm: T-3 "AvTrace: shader" lines = stdout "Shaders:"
      lines, T-4 "AvTrace: pipeline ... precache" lines = G + C of the "queued" line; M arm: 0 AvTrace / ShaderRegister /
      ShaderFirstUse lines (the null control of S0 4.1); 0 rows without FrameTrace-x, 0 torn rows, 0 gaps of n.  A broken
      identity is FAIL of the arm.
  (6) the KYTY_* environment of the json against the seal: a difference in KYTY_ASYNC_*, KYTY_PIPELINE_*, KYTY_SHADER_*,
      KYTY_CACHE_MODE, KYTY_S_*, KYTY_DUMP_*, KYTY_CS_PRETRANSLATE is FAIL (letter); the executor's stricter row - every
      KYTY_* key equal (the three path keys only present) - is printed and is also an admission row (variant).
  (7) cold gate (C and T2 arms): after the entry line >= 1 new permutation (AvTrace: shader lines), >= 1 new recipe and
      >= 1 skipped draw - else "level not cold", out of the count; the gate is False also when T-3/T-4 are broken - that is
      printed "undetermined (T-3/T-4)", apart from "level not cold" (item 250 (d)); C1-C4 count only with the gate (RC4); a C1
      "level not cold" sends L0 to the next reserve like "< 10 creations".  The share of skipped pairs whose both shaders
      are in snap0 is printed.  Warm gate (S-warm arms): 0 stdout "Shaders:" lines and recipes end - start = 0, else "not warm".
  (8) creation cold: median us of the in-game creations (AvTrace: pipeline gfx async / no suffix, cs async / sync) >=
      20 000 cold, <= 5 000 warm, < 10 creations "nothing to classify".  Letter: every in-game creation of the run; the
      executor's variant (printed): only after the entry line.
  (9) video checks the picture, not freezes; no identity "video frames = presented rows".
  (10) the foreign-CPU row of the harness (times.txt) is not read here.
  (11) S3b (HPP-325, item 250): the installed binary is copied before the arm and returned from that copy - the admission
      row is installed_after = installed_before (RC1); return_prev_ok and the continuity of the live manifests with the
      returns of the previous arm of S ("foreign chain between arms" - a data row, not FAIL; RC2); man_launch_glc =
      restore_glc.got (RC10); pcw_int is a T arm and its "AvTrace: pcw overlap" / "AvTrace: pcw recipes" lines are read
      (RC5); "save failed (Incomplete" is counted apart - ARM1_CODE_DEFECT (RC6); KYTY_FIX_ is a family (RC7); a pcw_val
      stopped before the entry line by validation is VALIDATION_STOP_PRE_LEVEL, member (d) undetermined (RC11).
  (12) item 254 (e) (form W until B35 ships): a validation arm runs with KYTY_PIPELINE_PRECACHE=0 (a family key of the
      seal) and its admission row is the positive control - no "PipelinePrecache: N recipes ->" line in its log.
  (13) item 265 (S4b, HPP-349): RX_SHADER reads a label with a space - the emulator writes "AvTrace: shader
      ShaderRecompiler VS hash=..." (4fc501f4 pipelineCache.cpp:3916); the S4 seal is pred/03_s.md for the arms after
      c1_0; the arms made under seal 02 (SEAL02_TAGS) are admitted against seal 02 (its pinned sha256 SHA_02, the row
      "prereg = the seal of its run 02_s.md"); the S6 seal is pred/04_s.md (item 265 (e)); --json-out writes the score
      json elsewhere (the files of seal 02 are not rewritten, item 265 (v)(7)).
READINGS: --read-c (item 241 (d)), --read-warm ((e)), --read-t2 ((zh)), --read-pcw ((z)(5)), with "undetermined" instead
of PASS on every empty denominator.  Output is ASCII only.  Logs are read in binary, streaming, line by line.
    python sc_s.py --tag <tag> [--json-out <path>]   score one arm (rc 0 = arm PASS); json default runs_s/<tag>.score.json
    python sc_s.py --read-c | --read-warm | --read-t2 | --read-pcw | --summary
    python sc_s.py --allowed <tag>      rc 0 when the order and conditions of item 241 allow the arm now, else rc 1/6
    python sc_s.py --check-seal         every sha line of the seal
    python sc_s.py --regress            the 12 sc142 logs against S0 1.3, class_s0.txt and S1 section 0
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys

SC142_PATH = 'C:/kyty/s142/sc142.py'
SHA142 = '1ce612cdd036e2382ce5c5aae6bd25836062830dc0952da8512a9f2a74bb38c3'


def load142(path=SC142_PATH, want=SHA142):
    """The inherited scorer, unchanged: refuse when its sha256 is not the pinned one."""
    got = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if got != want:
        raise SystemExit('sc_s.py: %s sha256 %s != pinned %s - the inheritance is broken' % (path, got, want))
    spec = importlib.util.spec_from_file_location('sc142_inherited', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


B = load142()

ROOT = 'C:/kyty/s288'
PRED_PATH = 'C:/kyty/s288/pred/03_s.md'   # S4: seal 03 of S4b (item 265) for the arms after c1_0; 01 and 02 no longer hold
PRED_02 = 'C:/kyty/s288/pred/02_s.md'     # seal 02 of S3b: the arms made under it are admitted against it (item 265 (g))
SHA_02 = '829ac684f2de5311cda035b5135d6bb262448bf282f5a2e803a2e73e447c6515'
SEAL02_TAGS = ('sw_m1', 'sw_m2', 'sw_m3', 'sw_t1', 'c1_0')   # the S4 arms made under seal 02 (S4 times.txt, item 265)
SEAL_PREV = (PRED_02, SHA_02, SEAL02_TAGS)
PRED_S6 = 'C:/kyty/s288/pred/04_s.md'     # S6: item 265 (e) - a later seal with the line "pcw binary: <sha> <path>"
INDEX_PATH = 'C:/kyty/s288/s3/snap0_index.json'
BUILD_SHA = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
SNAP_APP = 'd8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4'   # item 241 (g)(1)
SNAP_DRV = '1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028'   # item 241 (g)(1), item 238 (b)
LINKS = {'s4': 'C:/kyty/s288/s4', 's6': 'C:/kyty/s288/s6'}
SKY = 'underwater_aerial_garden'
L0S = ('shuriken_ninja_castle', 'jack_in_the_box', 'cymbal_party_land')      # item 241 (d): L0, reserves in order
WARM = (('sw_m1', 'big_hand_pirate_island', 'c142_02'), ('sw_m2', 'voxel_world', 'c142_09'),
        ('sw_m3', 'ice_iceberg', 'c142_05'))                                   # item 241 (e)
T2_LEVELS = ('small_pot_lava', 'spin_drill_natural_cave', 'light_gadget_graveyard', 'enemy_taco', 'hero_kratos',
             'picup_light', 'enemy_snake', 'mini_rocket_chain', 'hero_drake', 'bonus_path_maker_mix')  # item 241 (zh)
T2_NEED = 5
G_LEVELS = (SKY, 'big_hand_pirate_island')                                     # item 241 (zh): + L0
SCENE_DRAWS = B.SCENE_DRAWS
ENTRY_WIN = B.ENTRY_WIN
K3_US = B.K3_US
K2_US = B.K2_US
SKIP_LINES_MAX = 200000          # renderDraw.cpp: the skipped-draw lines stop at 200 000 per process
HELD_LINES_MAX = 64              # videoOut.cpp: "flip N held" only for the first 64 per process
COLD_US = 20000                  # item 241 (v)(8)
WARM_US = 5000
MIN_CREATE = 10
RET_LO = 0.5                     # item 241 (d)
RET_HI = 2.0
GLC_WARM = 0.25
SALT_PREP_MS = 6760              # 10 x 676
WARM_KEEP = 0.5                  # item 241 (e)
WARM_BASE_MIN = 5
PCW_MIN_WRITES = 15              # item 241 (z)(5)
PCW_POS_FRAC = 0.5
PCW_FORCE_MS = '15000'
HOLD_C_S = 120                   # item 241 (g)(5)
HOLD_PCW_US = 300000000          # item 241 (z)(5): hold >= 300 s
FRAMES_VIDEO = 3000
PREP_LEVELS = 114                # item 241 (b)(2): the band of the preparation screen over 114 levels [I]
PREP_ENTERED = 19
PREP_PER_LEVEL = (6, 28, 83)     # S1 RC10: recipes per level, low / mid / high [I]
PREP_LIMIT_S = 180
FAMILIES = ('KYTY_ASYNC_', 'KYTY_PIPELINE_', 'KYTY_SHADER_', 'KYTY_S_', 'KYTY_DUMP_', 'KYTY_FIX_')   # FIX_: item 245 (a)
FAMILY_KEYS = ('KYTY_CACHE_MODE', 'KYTY_CS_PRETRANSLATE')
PATH_KEYS = ('KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE', 'KYTY_REC')


def arms():
    """Every arm of S4 and S6 in the order of the chains (item 241 (l)): tag -> spec."""
    a = []

    def add(tag, link, level, cls, mode='full', hold=HOLD_C_S, salt=False, pcw=None, val=False, glc_from=None,
            app_from=None, group='', k=None):
        a.append(dict(tag=tag, link=link, level=level, cls=cls, mode=mode, hold=hold, salt=salt, pcw=pcw, val=val,
                      glc_from=glc_from, app_from=app_from, group=group, k=k))
    for tag, lv, _ in WARM:
        add(tag, 's4', lv, 'M', group='warm')
    add('sw_t1', 's4', WARM[0][1], 'T', group='warm')
    for k, lv in enumerate(L0S):
        add('c1_%d' % k, 's4', lv, 'T', group='c', k=k)
        add('c2_%d' % k, 's4', lv, 'T', mode='glc_from', glc_from='c1_%d' % k, group='c', k=k)
        add('c3_%d' % k, 's4', lv, 'T', group='c', k=k)
        add('c4_%d' % k, 's4', lv, 'T', mode='glc_from', glc_from='c3_%d' % k, salt=True, group='c', k=k)
    for j, lv in enumerate(T2_LEVELS):
        add('t2_%02d' % (j + 1), 's4', lv, 'T', group='t2', k=j)
    add('g_1', 's4', G_LEVELS[0], 'G', group='g')
    add('g_2', 's4', G_LEVELS[1], 'G', group='g')
    for k, lv in enumerate(L0S):
        add('g_3_%d' % k, 's4', lv, 'G', group='g', k=k)
    add('pcw_1', 's6', SKY, 'M', hold=330, pcw='0', group='pcw')
    add('pcw_2', 's6', SKY, 'M', hold=330, pcw='1', group='pcw')
    add('pcw_3', 's6', SKY, 'M', hold=330, pcw='1', group='pcw')
    add('pcw_int', 's6', SKY, 'T', mode='integrity', pcw='1', glc_from='pcw_3', app_from='pcw_3', group='pcw')
    add('pcw_4', 's6', SKY, 'M', hold=330, pcw='0', group='pcw')
    add('pcw_val', 's6', SKY, 'M', hold=310, pcw='1', val=True, group='pcw')
    return a


ARMS = arms()
SPEC = dict((x['tag'], x) for x in ARMS)


def expected_env(spec):
    """The KYTY_* environment of an arm by the seal (item 241 (g)(4)-(5), (z)(5)); the path keys are checked apart."""
    e = dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1',
             KYTY_GUEST_ARGS='-lvl %s' % spec['level'], KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')
    if spec['cls'] in ('T', 'G'):
        e.update(KYTY_AV_TRACE='1', KYTY_SHADER_REGISTER_TRACE='1')
    if spec['cls'] == 'G':
        e.update(KYTY_DUMP_GCN='1')
    if spec['salt']:
        e.update(KYTY_PIPELINE_SALT=spec['tag'])
    if spec['pcw'] is not None:
        e.update(KYTY_S_PCW=spec['pcw'], KYTY_S_PCW_FORCE_MS=PCW_FORCE_MS)
    if spec['val']:
        e.update(KYTY_PIPELINE_PRECACHE='0')      # form W of a validation arm, item 254 (e)
    return e


def in_family(k):
    return k.startswith(FAMILIES) or k in FAMILY_KEYS


def env_rows(spec, env):
    """(letter family row, strict row) of item 241 (v)(6)."""
    want = expected_env(spec)
    have = dict((k, v) for k, v in (env or {}).items() if k.startswith('KYTY_'))
    fam_w = dict((k, v) for k, v in want.items() if in_family(k))
    fam_h = dict((k, v) for k, v in have.items() if in_family(k))
    fam_ok = fam_w == fam_h
    rest_h = dict((k, v) for k, v in have.items() if k not in PATH_KEYS)
    strict_ok = rest_h == want and all(k in have for k in PATH_KEYS)
    diff = sorted(set(k for k in set(fam_w) | set(fam_h) if fam_w.get(k) != fam_h.get(k)))
    sdiff = sorted(set(k for k in set(want) | set(rest_h) if want.get(k) != rest_h.get(k)) |
                   set(k for k in PATH_KEYS if k not in have))
    return (fam_ok, ','.join(diff) or '-'), (strict_ok, ','.join(sdiff) or '-')


# ---------------------------------------------------------------------------------------------------------- the scan
RX_SKIP = re.compile(rb'frame=(\d+) vs=0x([0-9a-fA-F]+) ps=0x([0-9a-fA-F]+) pending=(\d+)')
RX_HASH = re.compile(rb' hash=(?:0x)?([0-9a-fA-F]+)')
RX_DSAVE = re.compile(rb'saved (\d+) bytes .*\((\d+) us\)')
RX_RSAVE = re.compile(rb'PipelinePrecache: saved (\d+) recipes')
RX_QUEUED = re.compile(rb'PipelinePrecache: (\d+) recipes -> (\d+) graphics \+ (\d+) compute pipelines queued, (\d+) skipped')
RX_CREATED = re.compile(rb'PipelinePrecache: all pipelines created, (\d+) ms')
RX_READY = re.compile(rb'ShaderPreparation: ready completed=(\d+) total=(\d+) skipped=(\d+)')
RX_WAITED = re.compile(rb'ShaderPreparation: startup wait finished in (\d+) ms')
RX_LOADED = re.compile(rb'Vulkan pipeline cache: loaded (\d+) bytes')
# item 265: the label may hold a space ('ShaderRecompiler VS', 4fc501f4 pipelineCache.cpp:3916 - "AvTrace: shader %s hash=")
RX_SHADER = re.compile(rb'AvTrace: shader (.+?) hash=0x([0-9a-fA-F]+) translate_us=(\d+) compile_us=(\d+)')
RX_VSPS = re.compile(rb' vs=(\d+) ps=(\d+)')
RX_PCWOV = re.compile(rb'AvTrace: pcw overlap (.+?) id0=')
RX_QUEUED_ANY = re.compile(rb'PipelinePrecache: \d+ recipes ->')     # item 254 (e): the start precache ran


def field(line, name):
    key = b' ' + name + b'='
    i = line.find(key)
    if i < 0:
        return None
    j = i + len(key)
    k = j
    n = len(line)
    while k < n and 48 <= line[k] <= 57:
        k += 1
    return int(line[j:k]) if k > j else None


def new_scan():
    return dict(rows=[], x={}, up={}, skips=[], held_lines=0, prio=[], dsave=[], rsave=[], savefail=0, savefail_inc=0,
                dload=[], disabled=0, coldns=0, sh=[], pipe=[], load=[], reg=[], first=[], queued=None, created_ms=None,
                ready=None, waited_ms=None, starts=[], avtrace=0, torn=0, seed_installed=0, seed_ignored=0, sha256=None,
                lines=0, pcw_ov=[], pcw_rec=[], queued_n=0)


def scan_s(path):
    """One streaming pass: rows and every event line with its group index (the index of the next main row)."""
    s = new_scan()
    h = hashlib.sha256()
    rows = s['rows']
    with open(path, 'rb') as f:
        for line in f:
            h.update(line)
            s['lines'] += 1
            g = len(rows)
            c0 = line[:1]
            if c0 == b'F':
                if line.startswith(b'FrameTrace: n='):
                    n = int(line[14:line.find(b' ', 14)]) if line.find(b' ', 14) > 14 else None
                    dt = field(line, b'dt_us')
                    if n is None or dt is None:
                        s['torn'] += 1
                        continue
                    d = field(line, b'draws')
                    cg = field(line, b'cpu_gpu_us')
                    rows.append((n, dt, d if d is not None else -1, cg if cg is not None else 0, s['lines']))
                    continue
                if line.startswith(b'FrameTrace-x: n='):
                    j = line.find(b' ', 16)
                    n = int(line[16:j]) if j > 16 else None
                    if n is not None:
                        s['x'][n] = (field(line, b'skc_ap_skip'), field(line, b'skc_held_inc'), field(line, b'skc_held'),
                                     field(line, b'skc_bad'))
                    continue
                if line.startswith(b'FrameTrace-draw: n='):
                    j = line.find(b' ', 19)
                    if j > 19:
                        s['up'][int(line[19:j])] = field(line, b'img_up_kb') or 0
                    continue
                if b'FrameTrace: n=' in line:
                    s['torn'] += 1
                continue
            if b'FrameTrace: n=' in line:
                s['torn'] += 1
            if c0 == b'A':
                if line.startswith(b'AsyncPipelines: skipped draw'):
                    m = RX_SKIP.search(line)
                    if m:
                        s['skips'].append((g, int(m.group(1)), m.group(2).decode().lower().zfill(16),
                                           m.group(3).decode().lower().zfill(16), int(m.group(4)), s['lines']))
                    else:
                        s['skips'].append((g, None, None, None, 0, s['lines']))
                elif line.startswith(b'AsyncPipelines: flip') and b' held' in line:
                    s['held_lines'] += 1
                elif line.startswith(b'AvTrace:'):
                    s['avtrace'] += 1
                    if line.startswith(b'AvTrace: shader '):
                        m = RX_SHADER.search(line)
                        if m:
                            s['sh'].append((g, m.group(1).decode('latin1'), m.group(2).decode().lower().zfill(16),
                                            int(m.group(3)), int(m.group(4)), s['lines']))
                    elif line.startswith(b'AvTrace: shader-cache load'):
                        s['load'].append((g, field(line, b'us') or 0))
                    elif line.startswith(b'AvTrace: pcw overlap '):
                        # S5c 2ce6326e PcwNoteOverlap: "AvTrace: pcw overlap <kind> id0= id1= wait_us= gen0= gen1=" (RC5);
                        # never PREP (item 245 (b): wait_us is the creation time, an upper bound, not additive)
                        m = RX_PCWOV.search(line)
                        s['pcw_ov'].append((g, m.group(1).decode('latin1') if m else None, field(line, b'wait_us'),
                                            field(line, b'gen0'), field(line, b'gen1')))
                    elif line.startswith(b'AvTrace: pcw recipes'):
                        s['pcw_rec'].append((g, field(line, b'copied'), field(line, b'count'), field(line, b'lock_us'),
                                             field(line, b'hold_us')))
                    elif line.startswith(b'AvTrace: pipeline '):
                        kind = 'gfx' if line.startswith(b'AvTrace: pipeline gfx') else 'cs'
                        body = line.rstrip()
                        if b' waited_us=' in body:
                            sub = 'waited'
                            us = field(body, b'waited_us') or 0
                        else:
                            us = field(body, b'us') or 0
                            if b' async ' in body or body.endswith(b' async'):
                                sub = 'async'
                            elif body.endswith(b' precache'):
                                sub = 'precache'
                            elif b' sync ' in body or body.endswith(b' sync'):
                                sub = 'sync'
                            else:
                                sub = 'none'
                        vp = RX_VSPS.search(body)
                        s['pipe'].append((g, kind, sub, us, field(body, b'wait_us') or 0,
                                          (int(vp.group(1)), int(vp.group(2))) if vp else None))
            elif c0 == b'P':
                if line.startswith(b'PriorityStall:'):
                    u = field(line, b'us')
                    s['prio'].append((g, u if u is not None else -1))
                elif line.startswith(b'PipelinePrecache: saved'):
                    m = RX_RSAVE.search(line)
                    s['rsave'].append((g, int(m.group(1)) if m else -1, s['lines']))
                elif line.startswith(b'PipelinePrecache: failed to write'):
                    s['savefail'] += 1
                elif line.startswith(b'PipelinePrecache: all pipelines created'):
                    m = RX_CREATED.search(line)
                    if m and s['created_ms'] is None:
                        s['created_ms'] = int(m.group(1))
                elif line.startswith(b'PipelinePrecache: '):
                    if RX_QUEUED_ANY.match(line):
                        s['queued_n'] += 1
                    m = RX_QUEUED.search(line)
                    if m and s['queued'] is None:
                        s['queued'] = tuple(int(m.group(i)) for i in (1, 2, 3, 4))
                elif line.startswith(b'Pipeline cold-test namespace'):
                    s['coldns'] += 1
            elif c0 == b'V':
                if line.startswith(b'Vulkan pipeline cache: saved'):
                    m = RX_DSAVE.search(line)
                    s['dsave'].append((g, int(m.group(1)) if m else -1, int(m.group(2)) if m else -1,
                                       b'forced' in line, s['lines']))
                elif line.startswith(b'Vulkan pipeline cache: loaded'):
                    m = RX_LOADED.search(line)
                    s['dload'].append(int(m.group(1)) if m else -1)
                elif line.startswith(b'Vulkan pipeline cache: disabled'):
                    s['disabled'] += 1
                elif line.startswith(b'Vulkan pipeline cache: save failed (Incomplete'):
                    s['savefail_inc'] += 1        # RC6, item 245 (v): a defect of the iteration code, counted apart
                elif line.startswith(b'Vulkan pipeline cache: save failed') or \
                        line.startswith(b'Vulkan pipeline cache: failed to write'):
                    s['savefail'] += 1
            elif c0 == b'S':
                if line.startswith(b'ShaderRegister:'):
                    m = RX_HASH.search(line)
                    s['reg'].append((m.group(1).decode().lower().zfill(16) if m else None, field(line, b'host_us')))
                elif line.startswith(b'ShaderFirstUse:'):
                    m = RX_HASH.search(line)
                    s['first'].append((g, m.group(1).decode().lower().zfill(16) if m else None, field(line, b'host_us')))
                elif line.startswith(b'ShaderPreparation: ready'):
                    m = RX_READY.search(line)
                    if m and s['ready'] is None:
                        s['ready'] = tuple(int(m.group(i)) for i in (1, 2, 3))
                elif line.startswith(b'ShaderPreparation: startup wait finished'):
                    m = RX_WAITED.search(line)
                    if m and s['waited_ms'] is None:
                        s['waited_ms'] = int(m.group(1))
                elif line.startswith(b'ShaderSeed: installed'):
                    s['seed_installed'] += 1
                elif line.startswith(b'ShaderSeed:') and b'ignored' in line:
                    s['seed_ignored'] += 1
            elif c0 == b'G':
                if line.startswith(b'GuestOut: Level has started:'):
                    s['starts'].append((g, line[len(b'GuestOut: Level has started:'):].strip().decode('latin1'),
                                        s['lines']))
    s['sha256'] = h.hexdigest()
    return s


def scan_stdout(path):
    """stdout of the emulator: the "Shaders:" lines (one per new translated permutation) and "Cache test mode:"."""
    r = dict(present=os.path.isfile(path), shaders=0, cache_test=0)
    if r['present']:
        with open(path, 'rb') as f:
            for line in f:
                if line.startswith(b'Shaders: VS'):
                    r['shaders'] += 1
                elif line.startswith(b'Cache test mode:'):
                    r['cache_test'] += 1
    return r


# ---------------------------------------------------------------------------------------------------------- derivation
def med(xs):
    if not xs:
        return None
    v = sorted(xs)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def cold_class(us):
    """Item 241 (v)(8)."""
    m = med(us)
    if len(us) < MIN_CREATE:
        return 'NOTHING', m
    if m >= COLD_US:
        return 'COLD', m
    if m <= WARM_US:
        return 'WARM', m
    return 'MID', m


def locate(s, level):
    """(entry group, end row index, first row index) - the reading of sc142.derive on group indices."""
    ent = [x[0] for x in s['starts'] if x[1] == level]
    if not ent:
        return None, None, None
    eg = ent[0]
    # every start line after the entry line (another level, the same level again, an empty name) is a scene change
    idx = [i for i, x in enumerate(s['starts']) if x[1] == level][0]
    nxt = s['starts'][idx + 1:]
    end = nxt[0][0] if nxt else len(s['rows'])
    fi = None
    for i in range(eg, end):
        if s['rows'][i][2] >= SCENE_DRAWS:
            fi = i
            break
    return eg, end, fi


def xget(s, i, k):
    """k: 0 skc_ap_skip, 1 skc_held_inc, 2 skc_held, 3 skc_bad; None when the row has no FrameTrace-x or no field."""
    t = s['x'].get(s['rows'][i][0])
    return None if t is None else t[k]


def held(s, i):
    return (xget(s, i, 1) or 0) > 0


def series(s, lo, hi):
    """Maximal runs of held rows in [lo, hi): (start, stop, closing index or None, gap)."""
    out = []
    i = lo
    rows = s['rows']
    while i < hi:
        if held(s, i):
            j = i
            while j < hi and held(s, j):
                j += 1
            close = j if j < hi else None
            gap = sum(rows[k][1] for k in range(i, j)) + (rows[close][1] if close is not None else 0)
            out.append((i, j, close, gap))
            i = j
        else:
            i += 1
    return out


def groups_of(events, lo, hi):
    return [e for e in events if lo <= e[0] <= hi]


def prio_sum(s, g):
    return sum(u for gg, u in s['prio'] if gg == g and u > 0)


def assign_prep(s):
    """Item 241 (v)(4): every AvTrace line of PREP to one row - the largest dt among rows g-1 .. g+2, earliest on a tie.
    Returns per row index: [TR, PL]."""
    rows = s['rows']
    n = len(rows)
    out = {}

    def put(g, tr, pl):
        best = None
        for i in range(g - 1, g + 3):
            if 0 <= i < n and (best is None or rows[i][1] > rows[best][1]):
                best = i
        if best is None:
            return
        v = out.setdefault(best, [0, 0])
        v[0] += tr
        v[1] += pl
    for g, _, _, tr, comp, _ in s['sh']:
        put(g, tr + comp, 0)
    for g, kind, sub, us, _, _ in s['pipe']:
        if (kind == 'gfx' and sub == 'none') or (kind == 'cs' and sub == 'sync') or sub == 'waited':
            put(g, 0, us)
    for g, us in s['load']:
        put(g, 0, us)
    return out


def classify(s, i, prep, attr_ok):
    """Item 241 (v)(3)-(4): (class, attribution word, PREP, TR, PL, prio next, prio prev)."""
    rows = s['rows']
    dt = rows[i][1]
    cg = rows[i][3]
    tr, pl = prep.get(i, (0, 0))
    p = tr + pl
    pn = prio_sum(s, i)
    pp = prio_sum(s, i + 1)
    pcw = any(e[0] in (i, i + 1) for e in s['dsave']) or any(e[0] in (i, i + 1) for e in s['rsave'])
    if attr_ok:
        near_skip = any(i - 2 <= e[0] <= i + 1 for e in s['skips'])
        near_async = any(i - 2 <= e[0] <= i + 1 and e[1] == 'gfx' and e[2] == 'async' for e in s['pipe'])
        shader = dt - p < K3_US or near_skip or near_async
        attr = 'SHADER' if shader else 'not'
        if shader and p * 2 >= dt:
            attr = 'SHADER-partly'
    else:
        shader = False
        attr = 'undetermined'
    idle = cg * 2 < dt
    prio_n = pn * 2 >= dt and idle
    prio_p = pp * 2 >= dt and idle
    if pcw:
        cls = 'PCW'
    elif shader:
        cls = 'SHADER'
    elif prio_n and prio_p:
        cls = 'PRIO'
    elif cg * 2 >= dt:
        cls = 'GPUTHR'
    else:
        cls = 'WAIT'
    return cls, attr, p, tr, pl, pn, pp


def s0_class(s, i):
    """The S0 rule of class_s0.py (stall lines of group i, no PCW) - only to reproduce class_s0.txt in --regress."""
    rows = s['rows']
    dt, cg = rows[i][1], rows[i][3]
    pn = prio_sum(s, i)
    if pn * 2 >= dt and cg * 2 < dt:
        return 'PRIO'
    if cg * 2 >= dt:
        return 'GPUTHR'
    return 'WAIT'


def creations(s, after_g=None):
    return [us for g, kind, sub, us, _, _ in s['pipe']
            if sub in ('async', 'sync', 'none') and (after_g is None or g >= after_g)]


def identities(s, std, cls):
    """Item 241 (v)(5): (name, ok or None for 'not applicable', detail)."""
    rows = s['rows']
    xs = [s['x'].get(r[0]) for r in rows]
    sk = sum((t[0] or 0) for t in xs if t)
    hi = sum((t[1] or 0) for t in xs if t)
    hk = sum((t[2] or 0) for t in xs if t)
    bad = sum((t[3] or 0) for t in xs if t)
    nskip = len(s['skips'])
    frames = set(e[1] for e in s['skips'] if e[1] is not None)
    out = []
    out.append(('T-1 sum skc_ap_skip = skipped-draw lines', (sk == nskip) if nskip < SKIP_LINES_MAX else None,
                '%d / %d' % (sk, nskip)))
    out.append(('T-2 min(64, sum skc_held_inc) = flip held lines', min(HELD_LINES_MAX, hi) == s['held_lines'],
                '%d / %d' % (min(HELD_LINES_MAX, hi), s['held_lines'])))
    out.append(('T-6 distinct frame= of skipped draws = sum skc_held_inc (main)',
                (len(frames) == hi) if nskip < SKIP_LINES_MAX else None, '%d / %d' % (len(frames), hi)))
    out.append(('sum skc_held (skip-ceil holds) = 0', hk == 0, hk))
    missing = sum(1 for t in xs if t is None or any(v is None for v in t[:3]))
    out.append(('rows without FrameTrace-x or a field = 0', missing == 0, missing))
    out.append(('torn FrameTrace rows = 0', s['torn'] == 0, s['torn']))
    gaps = sum(1 for a, b in zip(rows, rows[1:]) if b[0] != a[0] + 1)
    out.append(('gaps of n = 0', gaps == 0, gaps))
    if cls in ('T', 'G'):
        sh = len(s['sh'])
        out.append(('T-3 AvTrace: shader lines = stdout Shaders: lines', std['present'] and sh == std['shaders'],
                    '%d / %s' % (sh, std['shaders'] if std['present'] else 'no stdout')))
        pre = sum(1 for e in s['pipe'] if e[2] == 'precache')
        q = s['queued']
        out.append(('T-4 AvTrace pipeline precache lines = G + C queued', q is not None and pre == q[1] + q[2],
                    '%d / %s' % (pre, (q[1] + q[2]) if q else 'no queued line')))
    else:
        nul = s['avtrace'] + len(s['reg']) + len(s['first'])
        out.append(('null control M: 0 AvTrace / ShaderRegister / ShaderFirstUse lines', nul == 0, nul))
    out.append(('info skc_bad (unreachable by code, RC5; printed, no control)', None, bad))
    shown = sum(1 for i in range(len(rows)) if (xget(s, i, 0) or 0) > 0 and not held(s, i)
                and not any(held(s, j) for j in (i + 1, i + 2) if j < len(rows)))
    out.append(('info shown_skip by the +-2 rows rule (secondary to T-6, RC5)', None, shown))
    return out


def domain(s, fi, end, reading):
    return (fi if reading == 1 and held(s, fi) else fi + 1), end


def freeze(s, fi, end, prep, attr_ok, reading):
    """Item 241 (v)(1)-(2) on one reading: series, three measures, counts by window / hold."""
    rows = s['rows']
    lo, hi = domain(s, fi, end, reading)
    wend = fi + 1 + ENTRY_WIN
    ser = series(s, lo, hi)
    out = dict(lo=lo, hi=hi, series=[])
    cache = {}

    def cl(i):
        if i not in cache:
            cache[i] = classify(s, i, prep, attr_ok)
        return cache[i]
    in_series = set()
    closing = set()
    for a, b, close, gap in ser:
        idx = list(range(a, b)) + ([close] if close is not None else [])
        in_series.update(range(a, b))
        if close is not None:
            closing.add(close)
        sub = sum(rows[k][1] for k in idx if rows[k][1] >= K3_US and cl(k)[0] == 'PRIO')       # item 250 (g)(2)
        sub_old = sum(rows[k][1] for k in idx if rows[k][1] >= K3_US and cl(k)[0] in ('PCW', 'PRIO'))   # (v)(2) before 250
        asyn = [e for e in s['pipe'] if idx[0] <= e[0] <= idx[-1] and e[1] == 'gfx' and e[2] == 'async']
        out['series'].append(dict(n0=rows[a][0], n1=rows[b - 1][0], flips=b - a, gap_us=gap, gap_pipe_us=gap - sub,
                                  gap_pipe_old_us=gap - sub_old,
                                  part='window' if a < wend else 'hold', closed=close is not None, a=a, b=b,
                                  async_us=sum(e[3] for e in asyn), async_n=len(asyn),
                                  async_cold=sum(1 for e in asyn if e[3] >= COLD_US)))
    total = sum(rows[k][1] for k in range(lo, hi))
    rest = sum(rows[k][1] for k in range(lo, hi) if k not in in_series and k not in closing)
    out['T5'] = (sum(x['gap_us'] for x in out['series']) + rest, total)
    for part, a, b in (('window', fi + 1, min(hi, wend)), ('hold', max(fi + 1, wend), hi)):
        rr = range(a, b)
        out[part] = dict(rows=len(rr), skip_rows=sum(1 for i in rr if (xget(s, i, 0) or 0) > 0),
                         skip_draws=sum((xget(s, i, 0) or 0) for i in rr),
                         held=sum((xget(s, i, 1) or 0) for i in rr),
                         dt100=sum(1 for i in rr if rows[i][1] >= K3_US),
                         dt1s=sum(1 for i in rr if rows[i][1] >= K2_US),
                         shown100=sum(1 for i in rr if rows[i][1] >= K3_US and not held(s, i)),
                         shown1s=sum(1 for i in rr if rows[i][1] >= K2_US and not held(s, i)))
    # the held flips counted by reading: reading 1 adds the first scene frame when it is held
    first_add = (xget(s, fi, 1) or 0) if (reading == 1 and held(s, fi)) else 0
    out['window']['held'] += first_add
    for part in ('window', 'hold'):
        ss = [x for x in out['series'] if x['part'] == part]
        out[part].update(gap100=sum(1 for x in ss if x['gap_us'] >= K3_US), gap1s=sum(1 for x in ss if x['gap_us'] >= K2_US),
                         pipe100=sum(1 for x in ss if x['gap_pipe_us'] >= K3_US),
                         pipe1s=sum(1 for x in ss if x['gap_pipe_us'] >= K2_US),
                         pipe100_old=sum(1 for x in ss if x['gap_pipe_old_us'] >= K3_US),
                         pipe1s_old=sum(1 for x in ss if x['gap_pipe_old_us'] >= K2_US))
    long_rows = []
    for i in range(fi + 1, end):
        if rows[i][1] >= K3_US:
            c = cl(i)
            long_rows.append(dict(n=rows[i][0], dt=rows[i][1], part='window' if i < wend else 'hold', cls=c[0], attr=c[1],
                                  prep=c[2], tr=c[3], pl=c[4], prio_next=c[5], prio_prev=c[6], cpu_gpu=rows[i][3],
                                  held=held(s, i), i=i, line=rows[i][4]))
    out['long'] = long_rows
    return out


def counted_row(x):
    """Item 250 (g)(1): a presented row counts as attributed when its attribution is SHADER or its class is PCW."""
    return x['attr'].startswith('SHADER') or x['cls'] == 'PCW'


def attributed(fz, attr_ok, x_us):
    """'0 attributed frames >= X' of item 241 (v)(2) with item 250 (g): presented rows with dt >= X of attribution SHADER
    or of class PCW + series with gap_pipe (minus PRIO only) >= X."""
    if not attr_ok:
        return None
    r = sum(1 for x in fz['long'] if counted_row(x) and x['dt'] >= x_us and not x['held'])
    return r + sum(1 for x in fz['series'] if x['gap_pipe_us'] >= x_us)


def attributed_pcw(fz, attr_ok, x_us):
    """'of them PCW n' (item 250 (g)(1)): the presented rows of class PCW among the attributed rows >= X."""
    if not attr_ok:
        return None
    return sum(1 for x in fz['long'] if x['cls'] == 'PCW' and x['dt'] >= x_us and not x['held'])


def attributed_old(fz, attr_ok, x_us):
    """The second reading '(v)(2) before item 250': SHADER rows + series with gap_pipe_old (minus PCW and PRIO) >= X."""
    if not attr_ok:
        return None
    r = sum(1 for x in fz['long'] if x['attr'].startswith('SHADER') and x['dt'] >= x_us and not x['held'])
    return r + sum(1 for x in fz['series'] if x['gap_pipe_old_us'] >= x_us)


def unattributed(fz, attr_ok, x_us):
    """RC8: presented rows dt >= X that are not attributed, by class (WAIT / GPUTHR / PRIO; their attribution is 'not'),
    and the series with gap >= X whose gap_pipe < X (a PRIO row subtracted)."""
    if not attr_ok:
        return None
    rows = [x for x in fz['long'] if x['dt'] >= x_us and not x['held'] and not counted_row(x)]
    by = dict((c, sum(1 for x in rows if x['cls'] == c)) for c in ('WAIT', 'GPUTHR', 'PRIO'))
    ser = sum(1 for x in fz['series'] if x['gap_us'] >= x_us and x['gap_pipe_us'] < x_us)
    return dict(n=len(rows), series=ser, **by)


def fmt_unattr(u):
    if u is None:
        return 'undetermined'
    return '%d (WAIT %d, GPUTHR %d, PRIO %d; attribution "not" on all); series gap >= X with gap_pipe < X %d' % (
        u['n'], u['WAIT'], u['GPUTHR'], u['PRIO'], u['series'])


def early(s, fz, fi, attr_ok):
    """S-early data (item 241 (b)(4), (zh)): per event lead = min over its hashes of FirstUse - min Register; cost =
    PREP of an attributed frame >= 100 ms, or the async us of a series with gap_pipe >= 100 ms."""
    if not attr_ok:
        return None
    reg = {}
    for h, us in s['reg']:
        if h is not None and us is not None:
            reg[h] = min(reg.get(h, us), us)
    fu = {}
    for g, h, us in s['first']:
        if h is not None and us is not None and h not in fu:
            fu[h] = us
    lead = dict((h, fu[h] - reg[h]) for h in fu if h in reg)
    ev = []
    for x in fz['long']:
        if x['attr'].startswith('SHADER'):
            i = x['i']
            hs = set(e[2] for e in s['sh'] if i - 2 <= e[0] <= i + 1)
            ls = [lead[h] for h in hs if h in lead]
            ev.append(dict(kind='frame', n=x['n'], cost=x['prep'], lead=min(ls) if ls else None))
    for x in fz['series']:
        if x['gap_pipe_us'] >= K3_US:
            hs = set()
            for e in s['skips']:
                if x['a'] <= e[0] <= (x['b']) and e[2]:
                    hs.update((e[2], e[3]))
            ls = [lead[h] for h in hs if h in lead]
            ev.append(dict(kind='series', n=x['n0'], cost=x['async_us'], lead=min(ls) if ls else None))
    known = [e for e in ev if e['lead'] is not None]
    short = sum(1 for e in known if e['lead'] < e['cost'])
    return dict(events=ev, known=len(known), short=short, regs=len(reg), firsts=len(fu), leads=len(lead),
                share=(short / float(len(known))) if known else None)


def load_index(path=INDEX_PATH):
    if not os.path.isfile(path):
        return None
    ix = json.load(open(path, encoding='ascii'))
    return dict(any=set(x['hash'] for x in ix['shaders']), cur=set(x['hash'] for x in ix['shaders'] if x['current']),
                pairs=set(ix['pairs']))


def pairs_in_snap(s, after_line, ix):
    ps = sorted(set((e[2], e[3]) for e in s['skips'] if e[5] > after_line and e[2]))
    if ix is None:
        return dict(pairs=len(ps), both_any=None, both_cur=None, recipe=None)
    return dict(pairs=len(ps), both_any=sum(1 for a, b in ps if a in ix['any'] and b in ix['any']),
                both_cur=sum(1 for a, b in ps if a in ix['cur'] and b in ix['cur']),
                recipe=sum(1 for a, b in ps if '%s/%s' % (a, b) in ix['pairs']))


def entry_line(s, level):
    """The log line number of the entry line (the first start line of the level)."""
    x = [e[2] for e in s['starts'] if e[1] == level]
    return x[0] if x else None


def gates(s, std, eg, spec, attr_ok):
    """Item 241 (v)(7): "after the entry line" by the line number in the log."""
    el = entry_line(s, spec['level'])
    rec_end = max([e[1] for e in s['rsave']] + [s['queued'][0] if s['queued'] else 0])
    before = [e[1] for e in s['rsave'] if e[2] < el] + [s['queued'][0] if s['queued'] else 0]
    rec_new_after = rec_end - max(before)
    perm_after = sum(1 for e in s['sh'] if e[5] > el)
    skip_after = sum(1 for e in s['skips'] if e[5] > el)
    level_cold = perm_after >= 1 and rec_new_after >= 1 and skip_after >= 1
    cold = attr_ok and level_cold
    # item 250 (d): "undetermined (T-3/T-4)" is apart from "level not cold" (they lead to different L0 reserves)
    word = 'cold' if cold else ('undetermined (T-3/T-4)' if not attr_ok else 'level not cold')
    warm = std['present'] and std['shaders'] == 0 and rec_end - (s['queued'][0] if s['queued'] else 0) == 0
    return dict(cold=cold, cold_word=word, perm_after=perm_after, rec_new_after=rec_new_after, skip_after=skip_after, warm=warm,
                stdout_shaders=std['shaders'], rec_start=s['queued'][0] if s['queued'] else None, rec_end=rec_end)


# ---------------------------------------------------------------------------------------------------------- one arm
def link_dir(spec, root_map=None):
    return (root_map or LINKS)[spec['link']]


def pred_for(spec, preds=None):
    return (preds or {'s4': PRED_PATH, 's6': PRED_S6})[spec['link']]


def plan(spec):
    """One line for go_s.sh: link level class mode hold salt pcw val glc_from app_from stable-draws timeout.
    Stable draws and timeouts are the harness's (S4: as the census c142 - 100 / 480 s; C4 with the salt 900 s for the cold
    preparation screen, executor's variant; S6: as v142 / w142 - 300 / 480 s, validation 600 s)."""
    if spec['link'] == 's4':
        sd, to = 100, (900 if spec['salt'] else 480)
    else:
        sd, to = 300, (600 if spec['val'] else 480)
    return '%s %s %s %s %d %d %s %d %s %s %d %d' % (
        spec['link'], spec['level'], spec['cls'], spec['mode'], spec['hold'], 1 if spec['salt'] else 0,
        spec['pcw'] if spec['pcw'] is not None else '-', 1 if spec['val'] else 0, spec['glc_from'] or '-',
        spec['app_from'] or '-', sd, to)


def jget(d, key, sub):
    """d[key][sub] of a cache json entry; None when the entry is missing or is not a {k: v} note."""
    v = (d or {}).get(key)
    return v.get(sub) if isinstance(v, dict) else None


def cache_rows(spec, cj, cjs_of):
    """Admission rows of the cache protocol (item 241 (g)(1)-(3)) from runs_s/<tag>.cache.json."""
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    if cj is None:
        add('cache protocol json present', False, 'missing')
        return rows
    ra, rg = cj.get('restore_app') or {}, cj.get('restore_glc') or {}
    if spec['mode'] == 'integrity':
        src = cjs_of(spec['app_from']) or {}
        want_app = (src.get('app_post_copy') or {}).get('sha')
    else:
        want_app = SNAP_APP
    if spec['mode'] == 'full':
        want_glc = SNAP_DRV
    else:
        src = cjs_of(spec['glc_from']) or {}
        want_glc = (src.get('glc_post_copy') or {}).get('sha')
    add('restore of the app caches = %s' % ('snap0 d8ca8c8e' if spec['mode'] != 'integrity' else
                                            'app_post of %s' % spec['app_from']),
        want_app is not None and ra.get('got') == want_app and ra.get('expected') == want_app,
        '%s / %s' % ((ra.get('got') or '-')[:16], (want_app or '-')[:16]))
    add('restore of GLCache = %s' % ('snap0_drv 1767ca0a' if spec['mode'] == 'full' else 'glc_post of %s' % spec['glc_from']),
        want_glc is not None and rg.get('got') == want_glc and rg.get('expected') == want_glc,
        '%s / %s' % ((rg.get('got') or '-')[:16], (want_glc or '-')[:16]))
    for key in ('return_app', 'return_glc'):
        r = cj.get(key) or {}
        add('%s after the arm = its copy' % key, r.get('got') is not None and r.get('got') == r.get('expected'),
            '%s / %s' % ((r.get('got') or '-')[:16], (r.get('expected') or '-')[:16]))
    # RC1 (item 250 (b)): the binary installed before the arm is copied and returned; the constant 9235a7ac is gone
    ib = jget(cj, 'installed_before', 'sha')
    ia = jget(cj, 'installed_after', 'sha')     # go_s.sh notes it as {"sha": ...} (S3 compared the dict to a string)
    add('installed binary after the arm = installed before the arm (copy and return, item 250 (b))',
        ib is not None and len(ib) == 64 and ia == ib, '%s / %s' % ((ia or '-')[:16], (ib or '-')[:16]))
    # RC2 (item 250 (v)): no RETURN_FAILED guard was there when the arm started
    add('return_prev_ok (no RETURN_FAILED guard before the arm, item 250 (v))',
        jget(cj, 'return_prev', 'ok') == '1', jget(cj, 'return_prev', 'ok') or '-')
    # RC10 (item 250 (zh)): the GLCache manifest right before the game = the result of the restore before the arm
    ml = jget(cj, 'man_launch_glc', 'sha')
    add('man_launch_glc right before the game = restore_glc.got (item 250 (zh))', ml is not None and ml == rg.get('got'),
        '%s / %s' % ((ml or '-')[:16], (rg.get('got') or '-')[:16]))
    for key in ('man_pre_app', 'man_pre_glc', 'man_post_app', 'man_post_glc', 'glc_pre_copy'):
        add('manifest %s recorded' % key, bool((cj.get(key) or {}).get('sha')), ((cj.get(key) or {}).get('sha') or '-')[:16])
    if spec['tag'] in [x['glc_from'] for x in ARMS if x['glc_from']]:
        add('glc_post copy recorded (a later arm restores it)', bool((cj.get('glc_post_copy') or {}).get('sha')),
            ((cj.get('glc_post_copy') or {}).get('sha') or '-')[:16])
    if spec['tag'] in [x['app_from'] for x in ARMS if x['app_from']]:
        add('app_post copy recorded (a later arm restores it)', bool((cj.get('app_post_copy') or {}).get('sha')),
            ((cj.get('app_post_copy') or {}).get('sha') or '-')[:16])
    return rows


def continuity(tag, cj, cjs_of):
    """RC2 (item 250 (v)): the live manifests before installed_pre (man_pre_app / man_pre_glc) against return_*.got of the
    previous arm of S (by arm_start.utc over both links).  A difference is the data row "foreign chain between arms", not
    FAIL (V1, item 247 (b)).  Returns (word, detail)."""
    me = ((cj or {}).get('arm_start') or {}).get('utc')
    if not me:
        return 'undetermined', 'no arm_start of this arm'
    prev = None
    for t in SPEC:
        if t == tag:
            continue
        o = cjs_of(t)
        u = ((o or {}).get('arm_start') or {}).get('utc')
        if u and u < me and (prev is None or u > prev[0]):
            prev = (u, t, o)
    if prev is None:
        return 'no previous arm of S', '-'
    _, pt, po = prev
    diff = [k for k, m, r in (('app', 'man_pre_app', 'return_app'), ('glc', 'man_pre_glc', 'return_glc'))
            if ((cj.get(m) or {}).get('sha') or 'x') != ((po.get(r) or {}).get('got') or 'y')]
    return ('foreign chain between arms (%s)' % '+'.join(diff) if diff else 'same as the return of %s' % pt), pt


def admit(spec, js, pred_sha, bin_sha, cj, cjs_of, pred_path=PRED_PATH, prev_run=False):
    env = js.get('env') or {}
    at = js.get('attempts') or []
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    add('one attempt (--attempts 1, no warmup)', len(at) == 1 and at[0].get('label') == 'attempt 1', len(at))
    add('binary %s' % (bin_sha or '-')[:8], bin_sha is not None and js.get('binary_sha256') == bin_sha,
        (js.get('binary_sha256') or '')[:8])
    add('guest args -lvl %s' % spec['level'], js.get('guest_args') == '-lvl %s' % spec['level'], js.get('guest_args'))
    add('gates empty (shipped defaults)', js.get('gates') == '', repr(js.get('gates'))[:40])
    add('no KYTY_GPU_CHECKPOINTS', 'KYTY_GPU_CHECKPOINTS' not in env, '')
    add('no KYTY_GATE_SCHEDULE', 'KYTY_GATE_SCHEDULE' not in env and 'KYTY_GATE_SCHEDULE_ABBA' not in env, '')
    rec = env.get('KYTY_REC')
    add('video KYTY_REC rec_%s.mp4' % spec['tag'],
        rec is not None and rec.replace('\\', '/').endswith('/rec_%s.mp4' % spec['tag']), rec)
    val = B.last_value(js.get('cmdline') or [], '--vulkan-validation')
    want = 'true' if spec['val'] else 'false'
    add('--vulkan-validation %s' % want, val == want, val)
    if spec['val']:
        add('VK_LAYER_PATH in the validation arm', bool(env.get('VK_LAYER_PATH')), env.get('VK_LAYER_PATH'))
    (fo, fd), (so, sd) = env_rows(spec, env)
    add('KYTY_* families = the seal (item 241 (v)(6), letter)', fo, fd)
    add('every KYTY_* key = the seal (executor variant, stricter)', so, sd)
    add('hold --hold %d' % spec['hold'], js.get('hold_s') == spec['hold'], js.get('hold_s'))
    pr = js.get('prereg') or {}
    # item 265 (g): an arm made under seal 02 is admitted against seal 02 (the seal of its run), by name
    pname = ('prereg = the seal of its run %s (item 265 (g))' % os.path.basename(pred_path)) if prev_run else \
        'prereg = the seal now'
    add(pname, pred_sha is not None and pr.get('sha256') == pred_sha
        and (pr.get('path') or '').replace('\\', '/') == pred_path, (pr.get('sha256') or '')[:8])
    add('no pipeline-cache retry', not any(a.get('pipeline_cache_off') for a in at), '')
    rows.extend(cache_rows(spec, cj, cjs_of))
    return rows


def read_json(p):
    return json.load(open(p, encoding='utf-8')) if os.path.isfile(p) else None


def score_arm(tag, root_map=None, pred_sha=None, bin_sha=None, ix=None, pred_path=None, prev_run=False):
    """Everything about one arm; None when it was not made (no <tag>.json)."""
    spec = SPEC[tag]
    d = link_dir(spec, root_map)
    js = read_json(os.path.join(d, '%s.json' % tag))
    if js is None:
        return None
    lp = os.path.join(d, 'log_%s.txt' % tag)
    sp = os.path.join(d, 'stdout_%s.txt' % tag)
    ep = os.path.join(d, '%s.stdout.txt' % tag)

    def cjs_of(t):
        return read_json(os.path.join(link_dir(SPEC[t], root_map), 'runs_s', '%s.cache.json' % t))
    cj = cjs_of(tag)
    log142 = B.scan(lp) if os.path.isfile(lp) else None
    std142 = B.scan(sp) if os.path.isfile(sp) else None
    es142 = B.scan(ep) if os.path.isfile(ep) else None
    base = B.build(tag, spec['level'], js, log142, std142, es142, d, None)
    r = dict(tag=tag, level=spec['level'], cls=spec['cls'], link=spec['link'], group=spec['group'],
             outcome142=base['outcome'], reason142=base['reason'], marks=base.get('marks') or [],
             ended=base['ended'], exited=base['exited'], attempt=base['attempt_outcome'], hold_s=base['hold_s'],
             val=base['val'], vke=base.get('vke'), glitch=base['glitch'], cover=base['cover'],
             derive142=base['derive'], log_sha=base.get('log_sha'))
    r['admit'] = admit(spec, js, pred_sha, bin_sha, cj, cjs_of, pred_path or pred_for(spec), prev_run)
    r['cache'] = cj
    r['continuity'] = continuity(tag, cj or {}, cjs_of)
    if log142 is None:
        r.update(entered=False, ident=[], fail=['no log'])
        return r
    s = scan_s(lp)
    std = scan_stdout(sp)
    if spec['val']:
        # item 254 (e): form W - the positive control of KYTY_PIPELINE_PRECACHE=0 is no "recipes ->" line in the log
        r['admit'].append(('form W positive control: no "PipelinePrecache: N recipes ->" line (item 254 (e))',
                           s['queued_n'] == 0, s['queued_n']))
    eg, end, fi = locate(s, spec['level'])
    r['entered'] = eg is not None
    r['first'] = None if fi is None else (s['rows'][fi][0], s['rows'][fi][1], s['rows'][fi][2])
    ident = identities(s, std, spec['cls'])
    attr_ok = spec['cls'] in ('T', 'G') and all(ok for name, ok, _ in ident if name.startswith(('T-3', 'T-4')))
    r['attr_ok'] = attr_ok
    d142 = base['derive']
    agree = (d142['first'] is None and fi is None) or (
        d142['first'] is not None and fi is not None and d142['first'][0] == s['rows'][fi][0]
        and d142['frames_after_first'] == end - fi - 1)
    ident.append(('first scene frame and rows after it = the inherited sc142.derive', agree,
                  '%s / %s' % (d142['first'], r['first'])))
    r['prep'] = dict(queued=s['queued'], created_ms=s['created_ms'], ready=s['ready'], waited_ms=s['waited_ms'],
                     dload=s['dload'], disabled=s['disabled'], coldns=s['coldns'], seed_installed=s['seed_installed'],
                     seed_ignored=s['seed_ignored'], cache_test=std['cache_test'])
    allc = creations(s)
    r['create'] = dict(all=cold_class(allc), all_n=len(allc), after=cold_class(creations(s, eg)) if eg is not None else None,
                       after_n=len(creations(s, eg)) if eg is not None else 0)
    r['saves'] = dict(driver=len(s['dsave']), recipes=len(s['rsave']), fail=s['savefail'], incomplete=s['savefail_inc'],
                      last_bytes=s['dsave'][-1][1] if s['dsave'] else None, forced=sum(1 for e in s['dsave'] if e[3]))
    r['pcw_trace'] = pcw_trace(s)
    if fi is not None:
        prep = assign_prep(s)
        r['f1'] = freeze(s, fi, end, prep, attr_ok, 1)
        r['f2'] = freeze(s, fi, end, prep, attr_ok, 2)
        t5a, t5b = r['f1']['T5']
        ident.append(('T-5 partition (reading 1)', t5a == t5b, '%d / %d' % (t5a, t5b)))
        t5a, t5b = r['f2']['T5']
        ident.append(('T-5 partition (reading 2)', t5a == t5b, '%d / %d' % (t5a, t5b)))
        r['att100'] = attributed(r['f1'], attr_ok, K3_US)
        r['att1s'] = attributed(r['f1'], attr_ok, K2_US)
        r['att_pcw100'] = attributed_pcw(r['f1'], attr_ok, K3_US)
        r['att_pcw1s'] = attributed_pcw(r['f1'], attr_ok, K2_US)
        r['att100_old'] = attributed_old(r['f1'], attr_ok, K3_US)
        r['att1s_old'] = attributed_old(r['f1'], attr_ok, K2_US)
        r['unatt100'] = unattributed(r['f1'], attr_ok, K3_US)
        r['unatt1s'] = unattributed(r['f1'], attr_ok, K2_US)
        r['gates'] = gates(s, std, eg, spec, attr_ok)
        r['snap_pairs'] = pairs_in_snap(s, entry_line(s, spec['level']), ix)
        r['early'] = early(s, r['f1'], fi, attr_ok)
        r['pcw'] = pcw_arm(s, fi, end)
    r['ident'] = ident
    fail = ['admission: %s' % a[0] for a in r['admit'] if not a[1]]
    fail += ['identity: %s' % name for name, ok, _ in ident if ok is False]
    r['fail'] = fail
    return r


def pcw_arm(s, fi, end):
    """Item 241 (z)(5) on one arm: writes on the hold after the window, frames >= 100 ms with a write in groups i-1..i+1."""
    hs = fi + 1 + ENTRY_WIN
    w = [e for e in s['dsave'] if hs <= e[0] <= end]
    fr = [i for i in range(hs, end) if s['rows'][i][1] >= K3_US and any(i - 1 <= e[0] <= i + 1 for e in s['dsave'])]
    return dict(writes=len(w), forced=sum(1 for e in w if e[3]), frames=len(fr), frames_n=[s['rows'][i][0] for i in fr],
                last_bytes=s['dsave'][-1][1] if s['dsave'] else None, fail=s['savefail'], incomplete=s['savefail_inc'],
                loaded=s['dload'][0] if s['dload'] else None, disabled=s['disabled'])


def pcw_trace(s):
    """RC5 (item 247 (b) V3/V6, item 245 (b)): the "AvTrace: pcw overlap <kind>" and "AvTrace: pcw recipes" lines of the
    whole log by number; wait_us is the creation time - an upper bound, never added as a wait (max only); None when the log
    has neither kind (undetermined, never PASS)."""
    ov, rc = s['pcw_ov'], s['pcw_rec']
    if not ov and not rc:
        return None
    kinds = {}
    for e in ov:
        kinds[e[1]] = kinds.get(e[1], 0) + 1
    waits = [e[2] for e in ov if e[2] is not None]
    lk = [e[3] for e in rc if e[3] is not None]
    hd = [e[4] for e in rc if e[4] is not None]
    return dict(overlap=len(ov), kinds=kinds, wait_us_max=max(waits) if waits else None, recipes=len(rc),
                lock_us_max=max(lk) if lk else None, hold_us_max=max(hd) if hd else None,
                hold_us_med=med(hd))


# ---------------------------------------------------------------------------------------------------------- readings
def ok_arm(r):
    return r is not None and not r['fail']


def ratio(a, b):
    return None if a is None or b in (None, 0) else a / float(b)


def cold_word(r):
    """Item 250 (d): the cold gate word of a C / T2 arm - 'cold', 'level not cold', 'undetermined (T-3/T-4)' or
    'undetermined (no scene frame)' when the arm has no first scene frame (no gate)."""
    g = r.get('gates')
    if not g:
        return 'undetermined (no scene frame)'
    return g.get('cold_word') or ('cold' if g.get('cold') else 'level not cold')


def l0_choice(get):
    """Item 241 (d) with the lead's addition of item 250 (d): L0 and reserves in order; a candidate fails when its C1 did
    not enter, had < 10 creations (letter: every in-game creation) or is "level not cold" (by the level, not by
    T-3/T-4).  Returns (k or None, rows)."""
    rows = []
    for k in range(len(L0S)):
        r = get('c1_%d' % k)
        if r is None:
            rows.append('L0 %d %s: C1 not made' % (k, L0S[k]))
            return k, rows
        n = r['create']['all_n'] if r.get('create') else 0
        if r.get('entered') and n >= MIN_CREATE:
            cw = cold_word(r)
            if cw == 'level not cold':
                rows.append('L0 %d %s: C1 entered, %d creations, level not cold -> reserve (item 250 (d))' % (k, L0S[k], n))
                continue
            rows.append('L0 %d %s: C1 entered, %d creations, gate %s -> L0' % (k, L0S[k], n, cw))
            return k, rows
        rows.append('L0 %d %s: C1 entered %s, %d creations -> reserve' % (k, L0S[k], r.get('entered'), n))
    return None, rows


def read_c(get):
    """Item 241 (d) and (b)(2)."""
    k, rows = l0_choice(get)
    out = list(rows)
    res = dict(k=k, neutral=None, glc_warm=None, salt=None, ms_per_recipe=None)
    if k is None:
        out.append('C reading: L0 exhausted - undetermined')
        return res, out
    c = [get('c%d_%d' % (j, k)) for j in (1, 2, 3, 4)]
    meds = []
    good = []
    words = []
    for j, r in enumerate(c):
        if r is None:
            out.append('C%d (%s): not made' % (j + 1, L0S[k]))
            meds.append(None)
            good.append(False)
            words.append('not made')
            continue
        cc = r['create']['all']
        meds.append(cc[1] if cc[0] != 'NOTHING' else None)
        cw = cold_word(r)
        # RC4 (item 250 (d)): a C arm counts only with its cold gate; else "out of the count", the reading "undetermined"
        g = ok_arm(r) and cw == 'cold'
        good.append(g)
        words.append('counted' if g else ('arm FAIL' if not ok_arm(r) else 'out of the count: %s' % cw))
        out.append('C%d %s: arm %s; cold gate %s -> %s; creations %d median %s -> %s; after entry: %s; prep_ms %s; '
                   'recipes %s; T-4 %s' % (
                       j + 1, r['tag'], 'PASS' if ok_arm(r) else 'FAIL', cw, words[-1], r['create']['all_n'], cc[1], cc[0],
                       r['create']['after'], r['prep']['created_ms'], r['prep']['queued'],
                       [x[1] for x in r['ident'] if x[0].startswith('T-4')]))
    m1, m2, m3, m4 = meds

    def why(*js):
        return '; '.join('C%d %s' % (j + 1, words[j]) for j in js if words[j] != 'counted') or \
            'fewer than %d creations' % MIN_CREATE
    if good[0] and good[2] and m1 is not None and m3 is not None:
        q = ratio(m3, m1)
        res['neutral'] = m1 >= COLD_US and m3 >= COLD_US and RET_LO <= q <= RET_HI
        out.append('return neutralises: median C1 %s >= %d, C3 %s >= %d, C3/C1 %.3f in [%.1f; %.1f] -> %s' % (
            m1, COLD_US, m3, COLD_US, q, RET_LO, RET_HI, 'YES' if res['neutral'] else 'NO'))
    else:
        out.append('return neutralises: undetermined (%s)' % why(0, 2))
    if good[0] and good[1] and m1 is not None and m2 is not None:
        res['glc_warm'] = m2 <= GLC_WARM * m1
        out.append('GLCache keeps warmth: median C2 %s <= %.2f x C1 %s -> %s' % (m2, GLC_WARM, m1,
                                                                                 'YES' if res['glc_warm'] else 'NO'))
    else:
        out.append('GLCache keeps warmth: undetermined (%s)' % why(0, 1))
    r4 = c[3]
    if good[0] and good[3] and m1 is not None and m4 is not None and r4['prep']['created_ms'] is not None:
        q = ratio(m4, m1)
        pm = r4['prep']['created_ms']
        res['salt'] = pm >= SALT_PREP_MS and m4 >= COLD_US and RET_LO <= q <= RET_HI
        out.append('salt neutralises: prep_ms C4 %d >= %d, median C4 %s >= %d, C4/C1 %.3f in [%.1f; %.1f] -> %s' % (
            pm, SALT_PREP_MS, m4, COLD_US, q, RET_LO, RET_HI, 'YES' if res['salt'] else 'NO'))
    else:
        out.append('salt neutralises: undetermined (%s)' % why(0, 3))
    if r4 is not None and r4['prep']['created_ms'] is not None and r4['prep']['queued']:
        rec = r4['prep']['queued'][0]
        mpr = r4['prep']['created_ms'] / float(rec) if rec else None
        res['ms_per_recipe'] = mpr
        if mpr is not None:
            band = [(rec + (PREP_LEVELS - PREP_ENTERED) * p) * mpr / 1000.0 for p in PREP_PER_LEVEL]
            out.append('ms per recipe (C4) = %d / %d = %.2f; preparation screen over %d levels [I, band]: %.0f / %.0f / '
                       '%.0f s at %d / %d / %d recipes per level for %d levels (limit %d s); C4 waited_ms %s' % (
                           r4['prep']['created_ms'], rec, mpr, PREP_LEVELS, band[0], band[1], band[2],
                           PREP_PER_LEVEL[0], PREP_PER_LEVEL[1], PREP_PER_LEVEL[2], PREP_LEVELS - PREP_ENTERED,
                           PREP_LIMIT_S, r4['prep']['waited_ms']))
    else:
        out.append('ms per recipe: undetermined (no C4 preparation line)')
    out.append('T2 base may go: %s (item 241 (d): only with "return neutralises"; item 250 (e): the stop holds the T2 base '
               'only - S-warm and the G arms go)' % ('YES' if res['neutral'] else 'NO'))
    out.append('GLCache during the arm: not protected (item 250 (zh)) - files of glc_post whose base did not change in the S '
               'arms (the "game bases" rule of item 246 (v)): %s' % glc_foreign(getattr(get, 'root_map', None), k))
    return res, out


def glc_lines(p):
    """The relative paths of a GLCache manifest file (lines '<rel>\\t<size>\\t<mtime>\\t<sha>'); None when missing."""
    if not os.path.isfile(p):
        return None
    with open(p, 'rb') as f:
        return set(x.decode('utf-8', 'replace') for x in f.read().split(b'\n') if x.strip())


def glc_base(line):
    rel = line.split('\t', 1)[0]
    return rel.rsplit('.', 1)[0] if '.' in rel.rsplit('/', 1)[-1] else rel


def glc_foreign(root_map, k):
    """RC10 (item 250 (zh)): the files of glc_post/<C1|C3> whose base (rel path without .bin/.toc) never changed inside a
    S arm - "changed inside" = a line that differs between runs_s/<tag>.glc_launch.txt (right before the game) and
    runs_s/<tag>.glc_post.txt (after it) of any arm (the "game bases" rule of item 246 (v)); printed by number."""
    seen = set()
    for t in SPEC:
        d = os.path.join(link_dir(SPEC[t], root_map), 'runs_s')
        a, b = glc_lines(os.path.join(d, '%s.glc_launch.txt' % t)), glc_lines(os.path.join(d, '%s.glc_post.txt' % t))
        if a is not None and b is not None:
            seen.update(glc_base(x) for x in a ^ b)
    out = []
    for t in ('c1_%d' % k, 'c3_%d' % k):
        m = glc_lines(os.path.join(link_dir(SPEC[t], root_map), 'glc_post', t, 'MANIFEST.txt'))
        if m is not None:
            out.append('%s %d of %d files' % (t, sum(1 for x in m if glc_base(x) not in seen), len(m)))
    return '; '.join(out) or 'undetermined (no glc_post copy)'


def window_comp(r):
    """(i) held flips of the window (reading 1), (ii) window rows dt >= 100 ms, their classes."""
    f = r['f1']
    cls = {}
    for x in f['long']:
        if x['part'] == 'window':
            cls[x['cls']] = cls.get(x['cls'], 0) + 1
    return f['window']['held'], f['window']['dt100'], cls


def base_of(tag142, log=None):
    """The c142 base of S-warm: the same reading on the sc142 log of that level (M class, attribution undetermined)."""
    lv = B.level_of(tag142)
    s = scan_s(log or 'C:/kyty/s142/log_%s.txt' % tag142)
    eg, end, fi = locate(s, lv)
    f = freeze(s, fi, end, assign_prep(s), False, 1)
    return dict(f1=f, sha=s['sha256'])


def read_warm(get, base):
    """Item 241 (e)."""
    out = []
    keep_i = keep_ii = det_ii = n_det_i = 0
    for tag, lv, t142 in WARM:
        r = get(tag)
        b = base(t142)
        bi, bii, bcls = window_comp(b)
        if r is None:
            out.append('%s %s: not made' % (tag, lv))
            continue
        if not ok_arm(r) or not r.get('gates', {}).get('warm'):
            out.append('%s %s: %s - out of the count' % (tag, lv, 'arm FAIL' if not ok_arm(r) else 'not warm (%s)' % (
                r.get('gates'))))
            continue
        wi, wii, wcls = window_comp(r)
        si = 'undetermined' if bi < WARM_BASE_MIN else ('STAYS' if wi >= WARM_KEEP * bi else 'goes')
        sii = 'undetermined' if bii < WARM_BASE_MIN else ('STAYS' if wii >= WARM_KEEP * bii else 'goes')
        n_det_i += si != 'undetermined'
        keep_i += si == 'STAYS'
        det_ii += sii != 'undetermined'
        keep_ii += sii == 'STAYS'
        sp = r.get('snap_pairs') or {}
        out.append('%s %s vs %s: (i) held flips warm %d base %d -> %s; (ii) window dt >= 100 ms warm %d %s base %d %s -> %s; '
                   'skipped pairs %s (in snap0 recipes %s, both shaders current %s)' % (
                       tag, lv, t142, wi, bi, si, wii, wcls, bii, bcls, sii, sp.get('pairs'), sp.get('recipe'),
                       sp.get('both_cur')))
    out.append('(i) stays in %d of %d determined (>= 2 of 3 -> an argument against S-cat, not against the track)'
               % (keep_i, n_det_i))
    if det_ii == 0:
        out.append('(ii) undetermined on every level')
    else:
        out.append('(ii) stays in %d of %d determined -> %s' % (keep_ii, det_ii, 'ALL DETERMINED STAY: frames >= 100 ms of '
                   'the window are not from shader preparation (rows to register F; the track narrows to (i) and PCW)'
                   if keep_ii == det_ii else 'not all stay'))
    out.append('note: levels chosen by signal - regression to the mean (RC9(g))')
    m, t = get('sw_m1'), get('sw_t1')
    if m is not None and t is not None and m.get('f1') and t.get('f1'):
        fm, ft = m['f1']['window'], t['f1']['window']
        out.append('trace cost T - M on %s (RC7 null control): held %+d, skip rows %+d, dt >= 100 ms %+d; T attribution: %s'
                   % (WARM[0][1], ft['held'] - fm['held'], ft['skip_rows'] - fm['skip_rows'], ft['dt100'] - fm['dt100'],
                      [(x['n'], x['cls'], x['attr']) for x in t['f1']['long'] if x['part'] == 'window']))
    return out


def read_t2(get):
    """Item 241 (zh): cold-gated T arms, base of item 229 (e)(2) and S-early data."""
    out = []
    counted = []
    for j, lv in enumerate(T2_LEVELS):
        tag = 't2_%02d' % (j + 1)
        r = get(tag)
        if r is None:
            continue
        g = r.get('gates') or {}
        word = 'COUNTED' if ok_arm(r) and r.get('entered') and g.get('cold') else 'OUT'
        if word == 'COUNTED':
            counted.append(r)
        f = r.get('f1') or {}
        sp = r.get('snap_pairs') or {}
        e = r.get('early')
        out.append('%s %s: %s (%s); gate %s; held (reading 1) %s; skip rows %s; attributed >= 100 ms %s (of them PCW %s), '
                   '>= 1 s %s (of them PCW %s) [(v)(2) before item 250: %s, %s]; not attributed >= 100 ms %s, >= 1 s %s; '
                   'sc142 outcome %s (%s); pairs %s (both shaders in snap0: any %s, current %s); S-early lead<cost %s of %s'
                   % (tag, lv, word, cold_word(r), g, (f.get('window') or {}).get('held'),
                      (f.get('window') or {}).get('skip_rows'), r.get('att100'), r.get('att_pcw100'), r.get('att1s'),
                      r.get('att_pcw1s'), r.get('att100_old'), r.get('att1s_old'), fmt_unattr(r.get('unatt100')),
                      fmt_unattr(r.get('unatt1s')), r.get('outcome142'), r.get('reason142'), sp.get('pairs'),
                      sp.get('both_any'), sp.get('both_cur'), e['short'] if e else None, e['known'] if e else None))
    out.append('T2 counted %d of %d needed' % (len(counted), T2_NEED))
    kn = sum(r['early']['known'] for r in counted if r.get('early'))
    sh = sum(r['early']['short'] for r in counted if r.get('early'))
    out.append('S-early first half: lead < cost in %s of %d events -> %s; second half (FastLinking true, p95 of linking) - '
               'undetermined until measured' % (sh, kn, 'undetermined (denominator 0)' if kn == 0 else (
                   '>= 50 %' if sh * 2 >= kn else '< 50 %')))
    return out


def read_pcw(get):
    """Item 241 (z)(5): (a) positive control, (b) arms 1, (c) integrity, (d) validation, (e) video and markers."""
    out = []
    word = None
    zero, one = ('pcw_1', 'pcw_4'), ('pcw_2', 'pcw_3')
    rs = dict((t, get(t)) for t in zero + one + ('pcw_int', 'pcw_val'))
    if any(v is None for v in rs.values()):
        out.append('S-pcw: not every arm made - NOT_EVALUABLE')
        return 'NOT_EVALUABLE', out
    v = rs['pcw_val']
    # RC11 (item 250 (z)): pcw_val stopped by validation before the entry line -> VALIDATION_STOP_PRE_LEVEL: member (d)
    # undetermined, not FAIL, not counted toward the kill rule (z)(7); the arm leaves the admission / hold / video checks
    vstop = not v.get('entered') and (v.get('vke') or 0) >= 1
    chk = zero + one + ('pcw_int',) + (() if vstop else ('pcw_val',))
    bad = [t for t in chk if not ok_arm(rs[t])]
    held300 = dict((t, rs[t]['derive142']['dt_after_first_us'] >= HOLD_PCW_US) for t in zero + one +
                   (() if vstop else ('pcw_val',)))
    a = all(rs[t]['pcw']['writes'] >= PCW_MIN_WRITES and rs[t]['pcw']['frames'] >= PCW_POS_FRAC * rs[t]['pcw']['writes']
            for t in zero)
    b = all(rs[t]['pcw']['writes'] >= PCW_MIN_WRITES and rs[t]['pcw']['frames'] == 0 and rs[t]['pcw']['fail'] == 0
            for t in one)
    inc = dict((t, rs[t]['saves']['incomplete']) for t in one)          # RC6: arms 1 (item 245 (v))
    last = rs['pcw_3']['saves']['last_bytes']
    c = rs['pcw_int']['pcw']['loaded'] is not None and rs['pcw_int']['pcw']['loaded'] == last and \
        rs['pcw_int']['pcw']['disabled'] == 0
    d = None if vstop else bool(v['val']['ok'] and v.get('vke') == 0 and v.get('entered'))
    e = all((rs[t]['glitch'] or {}).get('video_frames', 0) >= FRAMES_VIDEO and (rs[t]['glitch'] or {}).get('glitches') == 0
            and not rs[t]['marks'] and not rs[t]['ended'] and not rs[t]['exited'] for t in chk)
    z1 = rs['pcw_int'].get('pcw_trace')                                  # RC5: (z)(1) on pcw_int (environment T)
    for t in zero + one:
        p = rs[t]['pcw']
        out.append('%s KYTY_S_PCW=%s: writes on the hold %d (forced %d), frames >= 100 ms with a write in i-1..i+1 %d %s, '
                   'save failures %d, Incomplete %d, presented >= 300 s %s' % (
                       t, SPEC[t]['pcw'], p['writes'], p['forced'], p['frames'], p['frames_n'][:8], p['fail'],
                       rs[t]['saves']['incomplete'], held300[t]))
    out.append('(a) positive control (arms 0: writes >= %d and frames >= %.0f %% of writes): %s' % (
        PCW_MIN_WRITES, 100 * PCW_POS_FRAC, 'PASS' if a else 'FAIL'))
    out.append('(b) arms 1 (writes >= %d, 0 frames, 0 save failures): %s' % (PCW_MIN_WRITES, 'PASS' if b else 'FAIL'))
    out.append('(c) integrity: loaded %s = last write of pcw_3 %s, disabled %d: %s' % (
        rs['pcw_int']['pcw']['loaded'], last, rs['pcw_int']['pcw']['disabled'], 'PASS' if c else 'FAIL'))
    if vstop:
        out.append('(d) validation: VALIDATION_STOP_PRE_LEVEL - pcw_val stopped by validation before the entry line '
                   '([Vulkan][E] %s, entered %s): member (d) undetermined, not FAIL, not counted toward the kill rule (z)(7) '
                   '(item 250 (z))' % (v.get('vke'), v.get('entered')))
    else:
        out.append('(d) validation: active %s, entered %s, [Vulkan][E] %s: %s (PASS only with the entry, the hold >= 300 s '
                   'and 0 [Vulkan][E])' % (v['val']['ok'], v.get('entered'), v.get('vke'), 'PASS' if d else 'FAIL'))
    out.append('(e) video >= %d frames, 0 glitches, 0 death markers on every arm%s: %s; the lead sheet - filled by S8' % (
        FRAMES_VIDEO, ' but the stopped pcw_val' if vstop else '', 'PASS' if e else 'FAIL'))
    if z1 is None:
        out.append('(z)(1) waits of GuestGpu on pcw_int: undetermined - 0 "AvTrace: pcw overlap" and 0 "AvTrace: pcw recipes" '
                   'lines (item 247 (b) V3/V6: never PASS)')
    else:
        out.append('(z)(1) waits of GuestGpu on pcw_int: overlap lines %d %s, wait_us max %s (the creation time - an upper '
                   'bound, not added as a wait, item 245 (b)); recipes lines %d, lock_us max %s, hold_us max %s median %s' % (
                       z1['overlap'], sorted(z1['kinds'].items()), z1['wait_us_max'], z1['recipes'], z1['lock_us_max'],
                       z1['hold_us_max'], z1['hold_us_med']))
    out.append('save failed (Incomplete on arms 1: %s%s' % (
        inc, ' - a defect of the iteration code (item 245 (v)): (5)(b) not met, the arm is repeated after the fix, not '
             'counted toward the kill rule (z)(7) - once per route' if any(inc.values()) else ''))
    out.append('arms failing admission or an identity: %s; hold >= 300 s on arms 0/1/validation: %s' % (
        bad or 'none', all(held300.values())))
    if bad or not all(held300.values()):
        word = 'NOT_EVALUABLE'
    elif not a:
        word = 'POSCTRL_FAIL'
    elif any(inc.values()):
        word = 'ARM1_CODE_DEFECT'
    elif not (b and c and e) or d is False:
        word = 'ARM1_FAIL'
    elif d is None or z1 is None:
        word = 'MACHINE_UNDETERMINED'
    else:
        word = 'MACHINE_PASS_PENDING_SHEET'
    out.append('S-pcw A/B: %s (FIXED only by the lead after (1)-(5) and the sheet; killed by rule (z)(7))' % word)
    return word, out


def allowed(tag, made, get):
    """Order and conditions of item 241 for the harness: (rc, reason).  rc 0 allowed, 1 order, 6 condition not met."""
    seq = [x['tag'] for x in ARMS]
    spec = SPEC[tag]
    if made(tag):
        return 1, 'already made'
    grp = spec['group']
    if grp == 'warm':
        prev = seq[seq.index(tag) - 1] if seq.index(tag) > 0 else None
        if prev and not made(prev):
            return 1, 'previous arm %s not made' % prev
        return 0, 'ok'
    if grp == 'c':
        if not made('sw_t1'):
            return 1, 'S-warm not finished (sw_t1)'
        k, _ = l0_choice(get)
        if k != spec['k']:
            return 6, 'L0 is %s, not %d' % (k, spec['k'])
        j = int(tag[1])
        if j > 1 and not made('c%d_%d' % (j - 1, spec['k'])):
            return 1, 'c%d_%d not made' % (j - 1, spec['k'])
        return 0, 'ok'
    if grp == 't2':
        k, _ = l0_choice(get)
        if k is None or not made('c4_%d' % k):
            return 1, 'C1-C4 not finished'
        res, _ = read_c(get)
        if not res['neutral']:
            return 6, 'no "return neutralises" (item 241 (d)): T2 does not go - report and stop'
        j = spec['k']
        if j > 0 and not made('t2_%02d' % j):
            return 1, 't2_%02d not made' % j
        counted = sum(1 for i in range(j) if made('t2_%02d' % (i + 1)) and ok_arm(get('t2_%02d' % (i + 1)))
                      and get('t2_%02d' % (i + 1)).get('entered') and (get('t2_%02d' % (i + 1)).get('gates') or {}).get('cold'))
        if j >= T2_NEED and counted >= T2_NEED:
            return 6, 'five counted already - no reserve needed'
        return 0, 'ok'
    if grp == 'g':
        k, _ = l0_choice(get)
        c_done = k is not None and made('c4_%d' % k)
        if not c_done:
            return 1, 'C1-C4 not finished'
        if tag == 'g_1':
            res, _ = read_c(get)
            if res['neutral'] and not allowed_t2_done(get, made)[0]:
                return 1, 'T2 base not finished'
            return 0, 'ok'
        if tag == 'g_2':
            return (0, 'ok') if made('g_1') else (1, 'g_1 not made')
        if spec['k'] != k:
            return 6, 'L0 is %s' % k
        return (0, 'ok') if made('g_2') else (1, 'g_2 not made')
    if grp == 'pcw':
        order = ('pcw_1', 'pcw_2', 'pcw_3', 'pcw_int', 'pcw_4', 'pcw_val')
        i = order.index(tag)
        if i > 0 and not made(order[i - 1]):
            return 1, '%s not made' % order[i - 1]
        return 0, 'ok'
    return 1, 'unknown group'


def allowed_t2_done(get, made):
    """T2 finished: five counted, or every listed level made."""
    counted = 0
    for i in range(len(T2_LEVELS)):
        t = 't2_%02d' % (i + 1)
        r = get(t) if made(t) else None
        if r is not None and ok_arm(r) and r.get('entered') and (r.get('gates') or {}).get('cold'):
            counted += 1
    allmade = all(made('t2_%02d' % (i + 1)) for i in range(len(T2_LEVELS)))
    return counted >= T2_NEED or allmade, counted


# ---------------------------------------------------------------------------------------------------------- printing
def fmt_arm(r):
    o = []
    o.append('ARM %s level %s class %s link %s: %s; sc142 outcome %s (%s); log %s' % (
        r['tag'], r['level'], r['cls'], r['link'], 'PASS' if not r['fail'] else 'FAIL', r['outcome142'], r['reason142'],
        (r.get('log_sha') or 'MISSING')[:16]))
    for name, ok, det in r['admit']:
        o.append('  %-4s admit %s (%s)' % ('PASS' if ok else 'FAIL', name, det))
    o.append('  data  continuity of the live caches with the previous arm of S (item 250 (v), not an admission row): %s (%s)'
             % r.get('continuity', ('undetermined', '-')))
    for name, ok, det in r.get('ident', []):
        o.append('  %-4s ident %s (%s)' % ('n/a' if ok is None else ('PASS' if ok else 'FAIL'), name, det))
    if 'f1' not in r:
        o.append('  entered %s, first scene frame %s - no freeze reading' % (r.get('entered'), r.get('first')))
        return o
    o.append('  entered yes; first scene frame (n, dt, draws) %s; attribution %s' % (
        r['first'], 'DETERMINED (T arm, T-3 and T-4 hold)' if r['attr_ok'] else 'UNDETERMINED (not a T arm or T-3/T-4 broken)'))
    for rd in ('f1', 'f2'):
        f = r[rd]
        o.append('  reading %s (%s):' % (rd[1], 'letter: series WITH a held first scene frame' if rd == 'f1' else
                                         'from the row after the first scene frame'))
        for part in ('window', 'hold'):
            p = f[part]
            o.append('    %s: rows %d, held flips %d, skip rows %d, skipped draws %d; dt >= 100 ms %d (presented %d), '
                     '>= 1 s %d (presented %d); series gap >= 100 ms %d, >= 1 s %d; gap_pipe (minus PRIO, item 250) >= 100 ms '
                     '%d, >= 1 s %d; gap_pipe (v)(2) before item 250 (minus PCW and PRIO) >= 100 ms %d, >= 1 s %d' % (
                         part, p['rows'], p['held'], p['skip_rows'], p['skip_draws'], p['dt100'], p['shown100'], p['dt1s'],
                         p['shown1s'], p['gap100'], p['gap1s'], p['pipe100'], p['pipe1s'], p['pipe100_old'], p['pipe1s_old']))
        o.append('    series (n0-n1 flips gap_ms gap_pipe_ms gap_pipe_old_ms part async_n async_cold): %s' % (
            '; '.join('%d-%d %d %.1f %.1f %.1f %s %d %d' % (
                x['n0'], x['n1'], x['flips'], x['gap_us'] / 1e3, x['gap_pipe_us'] / 1e3, x['gap_pipe_old_us'] / 1e3,
                x['part'], x['async_n'], x['async_cold']) for x in f['series']) or 'none'))
    o.append('  frames dt >= 100 ms (n dt part class attribution PREP TR PL prio_next prio_prev cpu_gpu held): %s' % (
        '; '.join('%d %d %s %s %s %d %d %d %d %d %d %s' % (x['n'], x['dt'], x['part'], x['cls'], x['attr'], x['prep'],
                                                          x['tr'], x['pl'], x['prio_next'], x['prio_prev'], x['cpu_gpu'],
                                                          'h' if x['held'] else '-') for x in r['f1']['long']) or 'none'))
    def u(v):
        return 'undetermined' if v is None else v
    o.append('  attributed frames (item 241 (v)(2), item 250 (g)): >= 100 ms %s (of them PCW %s), >= 1 s %s (of them PCW %s); '
             '(v)(2) before item 250: >= 100 ms %s, >= 1 s %s' % (
                 u(r['att100']), u(r['att_pcw100']), u(r['att1s']), u(r['att_pcw1s']), u(r['att100_old']),
                 u(r['att1s_old'])))
    o.append('  not attributed (RC8): >= 100 ms %s; >= 1 s %s; sc142 outcome %s' % (
        fmt_unattr(r['unatt100']), fmt_unattr(r['unatt1s']), r['outcome142']))
    o.append('  gates: %s; cold gate word: %s; skipped pairs %s' % (r['gates'], cold_word(r), r['snap_pairs']))
    o.append('  creations (in game, letter): %s of %d; after the entry line (variant): %s of %d' % (
        r['create']['all'], r['create']['all_n'], r['create']['after'], r['create']['after_n']))
    p = r['prep']
    o.append('  preparation: queued %s, all pipelines created %s ms, ready %s, startup wait %s ms, driver cache loaded %s '
             'disabled %d, cold-test namespace %d, seed installed %d ignored %d, Cache test mode %d' % (
                 p['queued'], p['created_ms'], p['ready'], p['waited_ms'], p['dload'], p['disabled'], p['coldns'],
                 p['seed_installed'], p['seed_ignored'], p['cache_test']))
    o.append('  cache writes: driver %d (forced %d, last %s bytes), recipes %d, failures %d, Incomplete %d; S-pcw hold: %s' % (
        r['saves']['driver'], r['saves']['forced'], r['saves']['last_bytes'], r['saves']['recipes'], r['saves']['fail'],
        r['saves']['incomplete'], dict((k, v) for k, v in r['pcw'].items() if k != 'frames_n')))
    o.append('  AvTrace pcw lines (RC5): %s' % ('none' if r['pcw_trace'] is None else r['pcw_trace']))
    e = r['early']
    o.append('  S-early: %s' % ('undetermined' if e is None else 'registers %d, first uses %d, leads %d; events %d, known %d, '
                                'lead < cost %d' % (e['regs'], e['firsts'], e['leads'], len(e['events']), e['known'],
                                                    e['short'])))
    g = r['glitch']
    o.append('  video (picture, not freezes - RC17): %s; death markers %s; validation active %s, [Vulkan][E] %s' % (
        'n/a' if g is None else '%d frames, %d glitches' % (g['video_frames'], g['glitches']),
        ';'.join(m['kind'] for m in r['marks']) or 'none', r['val']['ok'], r['vke']))
    return o


# ---------------------------------------------------------------------------------------------------------- regression
REG_TAGS = ('v142', 'w142') + tuple('c142_%02d' % i for i in range(1, 11))
REG_S0 = {   # S0 1.3: first n, first held, window skip/held/>=100, hold skip/held/>=100, skipped draws, pairs, series,
             # max gap ms (reading 2), gaps >=100 / >=1s, stdout Shaders lines, recipes start -> end
    'v142': (380, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0, 1013, 1013),
    'w142': (187, 0, 0, 0, 594, 0, 0, 1846, 0, 0, 0, 0.0, 0, 0, 0, 1013, 1013),
    'c142_01': (203, 1, 2, 2, 2, 0, 0, 0, 28, 14, 1, 1018.3, 1, 1, 110, 1013, 1200),
    'c142_02': (328, 0, 11, 10, 14, 4, 3, 2, 41, 17, 6, 266.3, 6, 0, 84, 1200, 1416),
    'c142_03': (263, 0, 24, 24, 3, 44, 44, 1, 2203, 16, 6, 1535.8, 4, 1, 50, 1416, 1563),
    'c142_04': (260, 1, 11, 11, 0, 0, 0, 0, 11, 2, 2, 235.8, 1, 0, 20, 1563, 1604),
    'c142_05': (231, 0, 45, 45, 3, 4, 4, 1, 239, 28, 5, 1802.7, 3, 1, 49, 1604, 1701),
    'c142_06': (261, 0, 6, 6, 2, 0, 0, 0, 56, 18, 2, 771.4, 1, 0, 50, 1701, 1793),
    'c142_07': (229, 0, 10, 10, 0, 0, 0, 0, 19, 3, 1, 298.7, 1, 0, 4, 1793, 1807),
    'c142_08': (201, 1, 24, 29, 0, 0, 0, 0, 56, 1, 1, 655.4, 1, 0, 14, 1807, 1825),
    'c142_09': (178, 0, 3, 5, 7, 0, 0, 0, 87, 2, 1, 1282.3, 1, 1, 7, 1825, 1831),
    'c142_10': (223, 0, 5, 6, 1, 0, 0, 0, 77, 6, 1, 355.0, 1, 0, 8, 1831, 1842)}
REG_T6 = {'v142': 0, 'w142': 0, 'c142_01': 3, 'c142_02': 13, 'c142_03': 68, 'c142_04': 12, 'c142_05': 49, 'c142_06': 6,
          'c142_07': 10, 'c142_08': 30, 'c142_09': 5, 'c142_10': 6}                                   # S1 section 0
REG_WITH_FIRST = {'c142_01': 1804.1, 'c142_04': 705.2, 'c142_08': 984.4}                              # S1 / item 235 (a)
REG_DRV_PCW = {('c142_02', 795), ('c142_02', 1358), ('c142_02', 2557), ('c142_03', 1042), ('c142_05', 1002)}  # S1 RC3
CLASS_S0 = 'C:/kyty/s288/s0/out/class_s0.txt'
CLASS_S0_SHA = '1cd726fb53f70b0fc7eef2fe22b2e80b91656cb7aa048e6505c07bda6a6ac36a'


def regress_one(tag):
    lp = 'C:/kyty/s142/log_%s.txt' % tag
    s = scan_s(lp)
    std = scan_stdout('C:/kyty/s142/stdout_%s.txt' % tag)
    lv = B.level_of(tag)
    eg, end, fi = locate(s, lv)
    prep = assign_prep(s)
    f1 = freeze(s, fi, end, prep, False, 1)
    f2 = freeze(s, fi, end, prep, False, 2)
    ident = identities(s, std, 'M')
    post = range(fi + 1, end)
    pairs = len(set((e[2], e[3]) for e in s['skips'] if e[0] > fi and e[2]))
    rec = [e[1] for e in s['rsave']]
    got = (s['rows'][fi][0], 1 if held(s, fi) else 0, f2['window']['skip_rows'], f2['window']['held'], f2['window']['dt100'],
           f2['hold']['skip_rows'], f2['hold']['held'], f2['hold']['dt100'], sum((xget(s, i, 0) or 0) for i in post), pairs,
           len(f2['series']), round(max([x['gap_us'] for x in f2['series']] or [0]) / 1e3, 1),
           sum(1 for x in f2['series'] if x['gap_us'] >= K3_US), sum(1 for x in f2['series'] if x['gap_us'] >= K2_US),
           std['shaders'], s['queued'][0] if s['queued'] else None, max(rec) if rec else (s['queued'][0] if s['queued'] else None))
    return dict(tag=tag, sha=s['sha256'], got=got, ident=ident, f1=f1, f2=f2, s=s, fi=fi, end=end)


def regress(tags=REG_TAGS, out=print):
    """Item 241 (v)(11): S0 1.3, class_s0.txt (PCW correction and both PRIO conventions named), S1 section 0."""
    ok = True
    names = ('first_n', 'first_held', 'win_skip', 'win_held', 'win_100', 'hold_skip', 'hold_held', 'hold_100',
             'skipped_draws', 'pairs', 'series', 'max_gap_ms', 'gap100', 'gap1s', 'stdout_shaders', 'rec_start', 'rec_end')
    s0rows = {}
    if os.path.isfile(CLASS_S0):
        csha = hashlib.sha256(open(CLASS_S0, 'rb').read()).hexdigest()
        out('class_s0.txt sha256 %s %s' % (csha, 'pinned' if csha == CLASS_S0_SHA else 'NOT PINNED'))
        ok &= csha == CLASS_S0_SHA
        for line in open(CLASS_S0, encoding='ascii'):
            p = line.split()
            if len(p) == 12 and p[1].isdigit():
                s0rows[(p[0], int(p[1]))] = p
    tot = dict(cls_next={}, cls_prev={}, final={}, t6=0, pipe1s=0, pipe1s_old=0, ser=0, g100=0, g1s=0, with1s=0, pipe1s_s1=0, drv=set(),
               rec=set())
    for tag in tags:
        r = regress_one(tag)
        want = REG_S0[tag]
        diffs = [(n, w, g) for n, w, g in zip(names, want, r['got']) if w != g]
        out('REG %s sha %s: S0 1.3 %s' % (tag, r['sha'][:16], 'MATCH' if not diffs else 'DIFF %s' % diffs))
        ok &= not diffs
        idb = [(n, d) for n, o, d in r['ident'] if o is False and not n.startswith('null')]
        t6 = [d for n, o, d in r['ident'] if n.startswith('T-6')][0]
        t6ok = [o for n, o, d in r['ident'] if n.startswith('T-6')][0]
        out('    identities: T-6 %s %s (S1 %d); broken (null control of M not applicable to lite logs): %s' % (
            t6, 'ok' if t6ok else 'BROKEN', REG_T6[tag], idb or 'none'))
        ok &= bool(t6ok) and int(t6.split(' / ')[1]) == REG_T6[tag] and not idb
        tot['t6'] += 1 if t6ok else 0
        s = r['s']
        if tag in REG_WITH_FIRST:
            x = r['f1']['series'][0]
            good = round(x['gap_us'] / 1e3, 1) == REG_WITH_FIRST[tag] and x['n0'] == r['s']['rows'][r['fi']][0]
            out('    series with the held first scene frame: %d-%d %.1f ms (S1 %.1f) %s' % (
                x['n0'], x['n1'], x['gap_us'] / 1e3, REG_WITH_FIRST[tag], 'MATCH' if good else 'DIFF'))
            ok &= good
        if tag.startswith('c142'):
            tot['ser'] += len(r['f2']['series'])
            tot['g100'] += sum(1 for x in r['f2']['series'] if x['gap_us'] >= K3_US)
            tot['g1s'] += sum(1 for x in r['f2']['series'] if x['gap_us'] >= K2_US)
            tot['with1s'] += sum(1 for x in r['f1']['series'] if x['gap_us'] >= K2_US)
            tot['pipe1s'] += 1 if any(x['gap_pipe_us'] >= K2_US for x in r['f1']['series']) else 0
            tot['pipe1s_old'] += 1 if any(x['gap_pipe_old_us'] >= K2_US for x in r['f1']['series']) else 0
            # the S1 RC4 reading: PRIO by the S0 convention (stall lines of group i) only, PCW by any write
            s1 = 0
            for x in r['f1']['series']:
                idx = list(range(x['a'], x['b'])) + ([x['b']] if x['b'] < r['end'] else [])
                sub = sum(s['rows'][k][1] for k in idx if s['rows'][k][1] >= K3_US and (
                    s0_class(s, k) == 'PRIO' or classify(s, k, {}, False)[0] == 'PCW'))
                s1 += 1 if x['gap_us'] - sub >= K2_US else 0
            tot['pipe1s_s1'] += 1 if s1 else 0
        if tag == 'w142':
            continue
        for x in r['f1']['long']:
            i = x['i']
            c0 = s0_class(s, i)
            key = (tag, x['n'])
            sp = s0rows.get(key)
            same = sp is not None and sp[4] == c0 and int(sp[2]) == x['dt'] and sp[3] == x['part']
            ok &= same
            pp = 'PRIO' if (x['prio_prev'] * 2 >= x['dt'] and x['cpu_gpu'] * 2 < x['dt']) else (
                'GPUTHR' if x['cpu_gpu'] * 2 >= x['dt'] else 'WAIT')
            why = []
            if x['cls'] != c0:
                if x['cls'] == 'PCW':
                    kinds = [k for k, ev in (('driver', s['dsave']), ('recipes', s['rsave']))
                             if any(e[0] in (i, i + 1) for e in ev)]
                    why.append('PCW: a %s write in group i or i+1 (RC3)' % '+'.join(kinds))
                    if 'driver' in kinds:
                        tot['drv'].add(key)
                    else:
                        tot['rec'].add(key)
                elif c0 == 'PRIO':
                    why.append('PRIO only under the S0 convention (group i), %s under group i+1 (RC8)' % pp)
                else:
                    why.append('UNEXPLAINED')
                    ok = False
            if tag != 'v142':
                tot['cls_next'][c0] = tot['cls_next'].get(c0, 0) + 1
                tot['cls_prev'][pp] = tot['cls_prev'].get(pp, 0) + 1
                tot['final'][x['cls']] = tot['final'].get(x['cls'], 0) + 1
            out('    frame %s n %d dt %d %s: S0 %s (class_s0 %s) -> sc_s %s%s' % (
                tag, x['n'], x['dt'], x['part'], c0, sp[4] if sp else 'MISSING', x['cls'],
                (' [' + '; '.join(why) + ']') if why else ''))
        out('    gap_pipe series (reading 1): %s' % ['%d-%d %.1f/%.1f' % (x['n0'], x['n1'], x['gap_us'] / 1e3,
                                                                     x['gap_pipe_us'] / 1e3) for x in r['f1']['series']
                                                    if x['gap_us'] >= K2_US])
        out('    gap_pipe series (reading 1), (v)(2) before item 250 (minus PCW and PRIO): %s' % [
            '%d-%d %.1f/%.1f' % (x['n0'], x['n1'], x['gap_us'] / 1e3, x['gap_pipe_old_us'] / 1e3) for x in r['f1']['series']
            if x['gap_us'] >= K2_US])
    out('REG census sums: series (reading 2) %d (S0 26), gap >= 100 ms %d (20), >= 1 s %d (4); with the first frame '
        '>= 1 s %d (4); levels with gap_pipe >= 1 s: S1 RC4 reading (PRIO of group i) %d (S1 2), item 241 letter (PRIO '
        'robust to both groups) %d - c142_01 203-205: n 204 is PRIO only under group i, so it is not subtracted' % (
            tot['ser'], tot['g100'], tot['g1s'], tot['with1s'], tot['pipe1s_s1'], tot['pipe1s_old']))
    out('REG item 250 (g)(2): levels with gap_pipe >= 1 s by the governing reading (minus PRIO only, PCW "to the shaders") '
        '%d; by (v)(2) before item 250 (minus PCW and PRIO) %d' % (tot['pipe1s'], tot['pipe1s_old']))
    ok &= (tot['ser'], tot['g100'], tot['g1s'], tot['with1s'], tot['pipe1s_s1']) == (26, 20, 4, 4, 2)
    out('REG PCW frames: by a driver write %s (S1 RC3 table: 5 frames %s); by a recipe write only %s (the letter of item '
        '241 (v)(3) counts both writes; S1 RC3 listed the driver writes)' % (
            sorted(tot['drv']), 'MATCH' if tot['drv'] == REG_DRV_PCW else 'DIFF', sorted(tot['rec'])))
    ok &= tot['drv'] == REG_DRV_PCW
    out('REG classes of the 36 census frames: S0 convention %s (S0 14/20/2), group i+1 %s (S1 PRIO 10), sc_s final %s' % (
        sorted(tot['cls_next'].items()), sorted(tot['cls_prev'].items()), sorted(tot['final'].items())))
    ok &= tot['cls_next'] == {'PRIO': 14, 'GPUTHR': 20, 'WAIT': 2} and tot['cls_prev'].get('PRIO') == 10
    out('REG T-6 %d of %d' % (tot['t6'], len(tags)))
    out('REGRESSION: %s' % ('ALL OK' if ok else 'DIVERGENCE'))
    return ok


# ---------------------------------------------------------------------------------------------------------- seal
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')
RX_BIN = re.compile(r'^pcw binary: ([0-9a-f]{64}) (\S+)$')
SEALED_NAMES = ('go_s.sh', 'sc_s.py', 'test_sc_s.py', 'mut_sc_s.py', 'cachex_s.py', 'test_cachex_s.py', 'test_go_s.py',
                'snapidx_s.py', 's3/snap0_index.json', 'enter_scene.py', 'idle142.py', 'procload.py', 'run_safety99.py',
                'launch_run.py', 'gates_default.txt', 'sheet142.py', 'fgcpu143.py', 'C:/kyty/s142/sc142.py',
                'C:/kyty/s142/test_sc142.py', 'C:/kyty/scripts/s51_vidglitch.py')


def sha_file(p):
    return B.sha_file(p)


def check_seal(pred=PRED_PATH, root=ROOT, me=None):
    rows = []
    if not os.path.isfile(pred):
        return False, [('seal file', False, pred)], None
    seen = {}
    pbin = None
    for line in open(pred, encoding='utf-8'):
        m = RX_SEAL.match(line.rstrip('\n'))
        if m:
            seen[m.group(2)] = m.group(1)
        b = RX_BIN.match(line.rstrip('\n'))
        if b:
            pbin = (b.group(1), b.group(2))
    for name in SEALED_NAMES:
        if name not in seen:
            rows.append((name, False, 'no seal line'))
    for name, sh in sorted(seen.items()):
        p = name if (name.startswith('C:/') or name.startswith('/')) else os.path.join(root, name)
        now = sha_file(p) if os.path.isfile(p) else None
        rows.append((name, now == sh, (now or 'missing')[:16]))
    mine = sha_file(me or os.path.abspath(__file__))
    rows.append(('this scorer in the seal', seen.get('sc_s.py') == mine, mine[:16]))
    return all(r[1] for r in rows), rows, pbin


# ---------------------------------------------------------------------------------------------------------- main
def make_get(root_map, preds, ix, prev=None):
    """preds: link -> seal path.  The S4 binary is 9235a7ac; the S6 binary is the "pcw binary:" line of its seal."""
    # prev = (path, pinned sha256, tags): the arms made under an earlier seal are admitted against it (item 265 (g));
    # a file whose sha256 is not the pinned one admits none of them
    memo = {}
    info = {}
    for link, p in preds.items():
        sha = sha_file(p) if os.path.isfile(p) else None
        pb = check_seal(p)[2] if sha else None
        info[link] = (sha, BUILD_SHA if link == 's4' else (pb[0] if pb else None), p)

    def get(t):
        if t not in memo:
            sha, bsha, p = info[SPEC[t]['link']]
            if prev is not None and t in prev[2]:
                now = sha_file(prev[0]) if os.path.isfile(prev[0]) else None
                memo[t] = score_arm(t, root_map, now if now == prev[1] else None, bsha, ix, prev[0], True)
            else:
                memo[t] = score_arm(t, root_map, sha, bsha, ix, p)
        return memo[t]
    get.root_map = root_map
    return get


def made_fn(root_map):
    def made(t):
        d = link_dir(SPEC[t], root_map)
        return os.path.isfile(os.path.join(d, '%s.json' % t)) or os.path.isfile(os.path.join(d, 'attempt_%s.txt' % t))
    return made


def main(argv=None, root_map=None, pred=PRED_PATH, index=INDEX_PATH, base_logs=None, pred_s6=PRED_S6, prev=None):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--tag')
    ap.add_argument('--read-c', action='store_true')
    ap.add_argument('--read-warm', action='store_true')
    ap.add_argument('--read-t2', action='store_true')
    ap.add_argument('--read-pcw', action='store_true')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--allowed')
    ap.add_argument('--check-seal', action='store_true')
    ap.add_argument('--seal', default=None)
    ap.add_argument('--plan')
    ap.add_argument('--regress', action='store_true')
    ap.add_argument('--json-out', default=None)
    a = ap.parse_args(argv)
    if a.plan:
        if a.plan not in SPEC:
            print('usage: unknown tag %s' % a.plan)
            return 2
        print(plan(SPEC[a.plan]))
        return 0
    if a.check_seal:
        ok, rows, pbin = check_seal(a.seal or pred)
        for name, good, det in rows:
            print('%-4s %s %s' % ('OK' if good else 'BAD', name, det))
        print('pcw binary line: %s' % (('%s %s' % pbin) if pbin else 'none (S6 refuses until a seal carries it)'))
        print('SEAL: %s' % ('PASS' if ok else 'FAIL'))
        return 0 if ok else 1
    if a.regress:
        return 0 if regress() else 1
    ix = load_index(index)
    if prev is None and pred == PRED_PATH:
        prev = SEAL_PREV                 # item 265 (g): the arms of seal 02 under the production seal 03
    get = make_get(root_map, {'s4': pred, 's6': pred_s6}, ix, prev)
    made = made_fn(root_map)
    if a.allowed:
        if a.allowed not in SPEC:
            print('usage: unknown tag %s' % a.allowed)
            return 2
        rc, why = allowed(a.allowed, made, get)
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
        print('\n'.join(fmt_arm(r)))
        d = os.path.join(link_dir(SPEC[a.tag], root_map), 'runs_s')
        jp = a.json_out or os.path.join(d, '%s.score.json' % a.tag)
        os.makedirs(os.path.dirname(os.path.abspath(jp)), exist_ok=True)
        dump = dict((k, v) for k, v in r.items() if k not in ('f1', 'f2'))
        for k in ('f1', 'f2'):
            if k in r:
                dump[k] = dict((kk, vv) for kk, vv in r[k].items())
        json.dump(dump, open(jp, 'w', encoding='utf-8'), indent=1, default=list)
        return 0 if not r['fail'] else 1

    def base(t142):
        return base_of(t142, (base_logs or {}).get(t142))
    if a.read_c or a.summary:
        _, lines = read_c(get)
        print('\n'.join(['READ C1-C4 (item 241 (d))'] + lines))
    if a.read_warm or a.summary:
        print('\n'.join(['READ S-warm (item 241 (e))'] + read_warm(get, base)))
    if a.read_t2 or a.summary:
        print('\n'.join(['READ T2 (item 241 (zh))'] + read_t2(get)))
    if a.read_pcw or a.summary:
        _, lines = read_pcw(get)
        print('\n'.join(['READ S-pcw (item 241 (z)(5))'] + lines))
    if a.read_c or a.read_warm or a.read_t2 or a.read_pcw or a.summary:
        return 0
    print('usage: sc_s.py --tag T | --read-c | --read-warm | --read-t2 | --read-pcw | --summary | --allowed T | '
          '--check-seal | --regress')
    return 2


if __name__ == '__main__':
    sys.exit(main())
