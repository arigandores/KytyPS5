#!/usr/bin/env python3
"""sc_s9.py - the scorer of track S, third wave (link S9, HPP-431; ROADMAP "SESSION 122" item 355 (g)-(zh), (k); the arms run
in link S10 under the lock, files in C:/kyty/s288/s10).

INHERITANCE: C:/kyty/s288/sc_s.py (the scorer of seals 03 / 04, sha256 SHA_SC_S) is loaded UNCHANGED from its own path after a
sha256 check; it loads C:/kyty/s142/sc142.py the same way.  Its scan_s(), scan_stdout(), locate(), identities(), freeze(),
assign_prep(), attributed*(), unattributed(), gates(), early(), pcw_arm(), pcw_trace(), creations(), cold_class(), env_rows
logic are used as they are; this file only adds the arms of S10, their admission and the readings of item 355.

ARMS (item 355 (k), order of S10): pi_w1 pi_r1 pi_w0 pi_r0 (item 355 (g), binary f3b3aa3b), c5_0 (item 355 (d), binary f3b3aa3b),
t2_1 .. t2_10 (t2_6 .. t2_10 reserves) and t2_cs0 (item 355 (d), binary f3b3aa3b), u_1 .. u_5 (item 355 (e), the pinned 4aa62e95
without KYTY_GAME_PATCH).  Environment M = the base of enter_scene.py + KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0; T = M +
KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1 (item 241 (g)(5)).  Video on every arm.
  pi_w1 M full return, KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=15000, hold 330 (>= 300 s presented, the pcw form of seal 04)
  pi_r1 T integrity (app_post / glc_post of pi_w1, no snapshot), =1 + 15000, hold 120 (the form pcw_int of seal 04)
  pi_w0 M full return, KYTY_S_PCW=0 + 15000, hold 330;  pi_r0 T integrity of pi_w0, =0 + 15000, hold 120
  c5_0 T full return, L0 shuriken_ninja_castle, KYTY_PIPELINE_SALT=c5_0 KYTY_PIPELINE_PRECACHE=0, hold 120
  t2_k T full return, the level of lvl_s9.py; form by the C5 reading: C5 -> KYTY_PIPELINE_SALT=<tag> KYTY_PIPELINE_PRECACHE=0,
       APP ("cold of the application") -> nothing more; t2_cs0 = the level of t2_1, its form + KYTY_CS_PRETRANSLATE=0
  u_k  T form U: _ShaderCache/PPSA21564 and _PipelineCache empty for the arm (mirror of s10/empty_app, MANIFEST sha EMPTY_SHA),
       GLCache as found (copy before, return after), KYTY_SHADER_SEED_PATH=C:/kyty/s288/s9/seeds KYTY_CACHE_MODE=prepare-cold
READINGS (words of this scorer; the decisions are the lead's, S11):
  --read-pi  item 355 (g): the haze detector of the lead (C:/kyty/s288/lead/haze_s8.py, ported by the letter: crop 300x60 at
             (660, 60) of the 960x540 frame, scale 60x12, mean saturation (max-min)/(max+1), low = below 0.75 x the median of the
             frames >= 300, gap <= 3, kept when end - start >= 5) on the four videos, the series after frame 1 002; the words
             READ_1 (a series in pi_r1, none in pi_r0), READ_2 (no series in the four, or in both R; both R loaded N bytes = the
             last write of their own W, 0 disabled), READ_3 (a series only in pi_r0 among the R arms, or only in the W arms; AND
             the loaded member of READ_2 on both R - item 362 (v)), READ_OTHER; the executor's reading (READ_3 without the loaded
             member) printed beside.  Item 371 (b): an arm is read with its admission, its entry, no death marker and the video
             member = the video read by the detector (haze not None) with frames after frame 1 002 (0-based: >= 1 004 frames);
             the video frames, the present rows and the one-frame glitches are data per arm; the word of seal 05b (+ >= 3 000
             frames and 0 one-frame glitches as members) is printed beside as the executor variant ("DIFFERS (video rule)").
  --read-c5  item 355 (d): "salt without precache neutralises" = >= 10 in-game creations (lines "AvTrace: pipeline" without
             "precache") and their median us >= 20 000 -> YES -> T2 form C5; NO -> T2 form APP; the arm not admitted / not
             entered -> UNDETERMINED (no T2).
  --read-t2  item 355 (d), (zh), item 362 (b): the cold gate of item 241 (v)(7) - in the form C5 (KYTY_PIPELINE_PRECACHE=0) the
             recipe member is replaced by ">= 1 in-game creation after the entry line", in the form APP by the letter; the letter
             (with the recipe) and the executor's variant (the recipe member dropped) printed beside; the attribution, the S-early
             lead row, the BvhLoopCapTrip column, the data rows of t2_cs0 against t2_1.
  --read-u   item 355 (e): gates "ShaderSeed: installed" (log) and "Cache test mode: prepare-cold" (stdout); per arm a skipped
             draw line after the first scene frame or an attributed frame >= 100 ms; the preparation screen (process start to the
             later of "ShaderPreparation: ready" and "PipelinePrecache: all pipelines created", both printed); S-cat KILLED when
             >= 2 of 5 arms fail or a screen > 180 s, else ALIVE_BY_PROBE_5 (UNDETERMINED while an arm is not evaluable).
             Item 371 (v): a screen without both lines has the lower bound max(elapsed_ms of "ShaderPreparation: progress",
             --timeout when the attempt ended by timeout); a bound > 180 s is the kill member ("screen > N s (lower bound)"); an
             arm with neither both lines nor a bound > 180 s is not an S-cat member: with >= 1 such arm and < 2 failing members
             the word is UNDETERMINED; the letter of item 355 (e) ("else alive") is printed beside ("DIFFERS (screen
             undetermined)"), and the executor variant counting a failing arm without a screen measure ("DIFFERS (a failing arm
             without a screen measure)").  RC4: per U arm stdout Shaders:, rec_new_after, perm_after and the skip lines after the
             first scene frame (data, item 371 (g)).  The lead sheet of a series longer than 20 frames: 24 frames spread evenly
             over [start-2, end+2] (RC5).
Output is ASCII only.  Logs are read in binary, streaming.
    python sc_s9.py --tag <tag> | --read-pi | --read-c5 | --read-t2 | --read-u | --summary | --allowed <tag> | --plan <tag>
             [--form c5|app] | --check-seal [--seal <p>] | --haze <video> | --haze-sheet <tag> | --regress
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

SC_S_PATH = 'C:/kyty/s288/sc_s.py'
SHA_SC_S = '8b0e0aff407cc82ad0a98542676764b5a0c8a867266075aa81a92a09316dc5a4'


def load_sc_s(path=SC_S_PATH, want=SHA_SC_S):
    """The inherited scorer of seals 03 / 04, unchanged: refuse when its sha256 is not the pinned one."""
    got = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if got != want:
        raise SystemExit('sc_s9.py: %s sha256 %s != pinned %s - the inheritance is broken' % (path, got, want))
    spec = importlib.util.spec_from_file_location('sc_s_inherited', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = load_sc_s()
B = A.B

ROOT = 'C:/kyty/s288'
LINK_DIR = 'C:/kyty/s288/s10'
PRED_PATH = 'C:/kyty/s288/pred/06b_s.md'                       # item 371 (g), item 377 (b)(4)
BIN_S = 'f3b3aa3bef3f0ceadf668d0fc8bd68230ab1e3158d87bbc0b4c66b92a6651ca3'   # S5c, item 340 (v), item 355 (g)
BIN_U = '4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac'   # binary u: the pinned copy, item 342, item 355 (e)
INST_WANT = '540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1'   # installed before every arm, item 374 (g), item 377 (b)(1)
SNAP_APP = 'd8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4'   # item 241 (g)(1)
SNAP_DRV = '1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028'
EMPTY_SHA = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'  # the manifest of an empty set (form U)
SEEDS_PATH = 'C:/kyty/s288/s9/seeds'
SEEDS_SHA = '72605a65d15470f8e60a8a4d16c3a4b4d34cd557bbe6e8c17c9ba6441892f098'  # s9/seeds_manifest.txt of seedexp_s9.py
SKY = 'underwater_aerial_garden'
L0 = 'shuriken_ninja_castle'                                                   # item 355 (d): C5 on L0
T2_LIST = ('hero_kratos', 'hero_drake', 'voxel_challenge_3', 'armadillo_challenge_2', 'fragile_battle_4', 'voxel_challenge_4',
           'fragile_battle_5', 'voxel_challenge_5', 'miniboss_challenge_genie', 'symbol_triangle')   # lvl_s9.out.txt T2LIST
U_LIST = ('underwater_aerial_garden', 'hoover_beach', 'robot_builder_next', 'interactive_credit_00', 'fragile_battle_1')
T2_NEED = 5
PCW_FORCE_MS = '15000'
HOLD_W = 330
HOLD_T = 120
HOLD_W_US = 300000000            # item 241 (z)(5): W arms >= 300 s presented after the first scene frame
FRAMES_VIDEO = 3000
C5_MIN = 10                      # item 355 (d): >= 10 in-game creations
C5_US = 20000                    # item 355 (d): median us >= 20 000
PREP_LIMIT_S = 180               # item 229 (d)(2), item 355 (e)
U_KILL = 2                       # item 229 (d)(2): >= 2 of 5
U_N = 5
T2_GATE_READING = 'p362'         # item 362 (b): C5 - the recipe member replaced by an in-game creation; APP - the letter
HAZE_W, HAZE_H = 60, 12          # item 355 (g): the detector of the lead, by the letter
HAZE_CROP = 'crop=300:60:660:60'
HAZE_FROM = 300
HAZE_FRAC = 0.75
HAZE_GAP = 3
HAZE_LEN = 5
HAZE_AFTER = 1002
SHEET_LONG = 20                  # item 371 (g), RC5: a series longer than 20 frames -> 24 frames spread evenly
SHEET_N = 24
FFMPEG = 'ffmpeg'
NL = chr(10)
FAMILIES = A.FAMILIES
FAMILY_KEYS = A.FAMILY_KEYS
PATH_KEYS = A.PATH_KEYS
PI_ORDER = ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0')
PI_W = {'pi_r1': 'pi_w1', 'pi_r0': 'pi_w0'}


def arms():
    """Every arm of S10 in the order of item 355 (k) (t2_cs0 right after t2_1, item 355 (d)): tag -> spec."""
    a = []

    def add(tag, level, cls, group, mode='full', hold=HOLD_T, pcw=None, salt=False, pre0=False, cs0=False, u=False,
            src=None, binkind='s', k=None, t2form=False):
        a.append(dict(tag=tag, level=level, cls=cls, group=group, mode=mode, hold=hold, pcw=pcw, salt=salt, pre0=pre0,
                      cs0=cs0, u=u, src=src, binkind=binkind, k=k, t2form=t2form))
    add('pi_w1', SKY, 'M', 'pi', hold=HOLD_W, pcw='1')
    add('pi_r1', SKY, 'T', 'pi', mode='integrity', pcw='1', src='pi_w1')
    add('pi_w0', SKY, 'M', 'pi', hold=HOLD_W, pcw='0')
    add('pi_r0', SKY, 'T', 'pi', mode='integrity', pcw='0', src='pi_w0')
    add('c5_0', L0, 'T', 'c5', salt=True, pre0=True)
    add('t2_1', T2_LIST[0], 'T', 't2', k=0, t2form=True)
    add('t2_cs0', T2_LIST[0], 'T', 'cs0', cs0=True, k=0, t2form=True)
    for j in range(1, len(T2_LIST)):
        add('t2_%d' % (j + 1), T2_LIST[j], 'T', 't2', k=j, t2form=True)
    for j, lv in enumerate(U_LIST):
        add('u_%d' % (j + 1), lv, 'T', 'u', mode='u', u=True, binkind='u', k=j)
    return a


ARMS = arms()
SPEC = dict((x['tag'], x) for x in ARMS)
SEQ = [x['tag'] for x in ARMS]


def resolved(spec, form):
    """The spec of an arm with the T2 form applied (C5: salt of the tag + KYTY_PIPELINE_PRECACHE=0; APP: none)."""
    s = dict(spec)
    if spec['t2form']:
        s['form'] = form
        if form == 'c5':
            s['salt'] = True
            s['pre0'] = True
    else:
        s['form'] = None
    return s


def expected_env(spec):
    e = dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1',
             KYTY_GUEST_ARGS='-lvl %s' % spec['level'], KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')
    if spec['cls'] == 'T':
        e.update(KYTY_AV_TRACE='1', KYTY_SHADER_REGISTER_TRACE='1')
    if spec['pcw'] is not None:
        e.update(KYTY_S_PCW=spec['pcw'], KYTY_S_PCW_FORCE_MS=PCW_FORCE_MS)
    if spec['salt']:
        e.update(KYTY_PIPELINE_SALT=spec['tag'])
    if spec['pre0']:
        e.update(KYTY_PIPELINE_PRECACHE='0')
    if spec['cs0']:
        e.update(KYTY_CS_PRETRANSLATE='0')
    if spec['u']:
        e.update(KYTY_SHADER_SEED_PATH=SEEDS_PATH, KYTY_CACHE_MODE='prepare-cold')
    return e


def in_family(k):
    return k.startswith(FAMILIES) or k in FAMILY_KEYS


def env_rows(spec, env):
    """(letter family row, strict row) of item 241 (v)(6) - the logic of sc_s.env_rows on the S10 environment."""
    want = expected_env(spec)
    have = dict((k, v) for k, v in (env or {}).items() if k.startswith('KYTY_'))
    fam_w = dict((k, v) for k, v in want.items() if in_family(k))
    fam_h = dict((k, v) for k, v in have.items() if in_family(k))
    rest_h = dict((k, v) for k, v in have.items() if k not in PATH_KEYS)
    diff = sorted(k for k in set(fam_w) | set(fam_h) if fam_w.get(k) != fam_h.get(k))
    sdiff = sorted(set(k for k in set(want) | set(rest_h) if want.get(k) != rest_h.get(k)) |
                   set(k for k in PATH_KEYS if k not in have))
    return (fam_w == fam_h, ','.join(diff) or '-'), (rest_h == want and all(k in have for k in PATH_KEYS), ','.join(sdiff) or '-')


def stable_timeout(spec):
    """(stable draws, --timeout s) of an arm: pi 300 / 480, u 100 / 600, the rest 100 / 480."""
    return (300, 480) if spec['group'] == 'pi' else (100, 600 if spec['u'] else 480)


def plan(spec):
    """One line for go_s9.sh: link level cls mode hold salt pcw src sdraws timeout pre0 cs0 u binkind form."""
    if spec['t2form'] and spec.get('form') not in ('c5', 'app'):
        return 'UNDETERMINED'
    sd, to = stable_timeout(spec)
    return 's10 %s %s %s %d %d %s %s %d %d %d %d %d %s %s' % (
        spec['level'], spec['cls'], spec['mode'], spec['hold'], 1 if spec['salt'] else 0,
        spec['pcw'] if spec['pcw'] is not None else '-', spec['src'] or '-', sd, to, 1 if spec['pre0'] else 0,
        1 if spec['cs0'] else 0, 1 if spec['u'] else 0, spec['binkind'], spec.get('form') or '-')


# ---------------------------------------------------------------------------------------------------------- extra scan
def scan_x(path):
    """The lines sc_s.scan_s does not keep, with the same group index (the number of main FrameTrace rows before the line):
    BvhLoopCapTrip:, CsPretranslate: by kind, GamePatch:, in-game creation lines (AvTrace: pipeline without "precache") with
    their us field and their log line number (counted as sc_s.scan_s counts s['lines'], item 362 (b)), the row count (=
    len(scan_s rows)) and the line count (= scan_s lines) - identities of this scan; the lines "ShaderPreparation: progress":
    their count and the maximum of their elapsed_ms (item 371 (v): the lower bound of the preparation screen)."""
    r = dict(rows=0, lines=0, bvh=[], csp={}, gamepatch=0, create=[], create_nous=0, create_ln=[], prog_ms=None, prog_n=0)
    with open(path, 'rb') as f:
        for line in f:
            r['lines'] += 1
            c0 = line[:1]
            if c0 == b'F':
                if line.startswith(b'FrameTrace: n='):
                    j = line.find(b' ', 14)
                    if j > 14 and A.field(line, b'dt_us') is not None:
                        r['rows'] += 1
            elif c0 == b'B':
                if line.startswith(b'BvhLoopCapTrip:'):
                    r['bvh'].append(r['rows'])
            elif c0 == b'C':
                if line.startswith(b'CsPretranslate: '):
                    w = line[16:].split(b' ', 1)[0].strip().decode('latin1')
                    if w == 'enqueue':
                        w = 'enqueue skipped'
                    r['csp'][w] = r['csp'].get(w, 0) + 1
            elif c0 == b'G':
                if line.startswith(b'GamePatch:'):
                    r['gamepatch'] += 1
            elif c0 == b'S':
                if line.startswith(b'ShaderPreparation: progress '):
                    v = A.field(line.rstrip(), b'elapsed_ms')
                    r['prog_n'] += 1
                    if v is not None and (r['prog_ms'] is None or v > r['prog_ms']):
                        r['prog_ms'] = v
            elif c0 == b'A':
                if line.startswith(b'AvTrace: pipeline ') and b'precache' not in line:
                    us = A.field(line.rstrip(), b'us')
                    if us is None:
                        r['create_nous'] += 1
                    else:
                        r['create'].append(us)
                        r['create_ln'].append(r['lines'])
    return r


def scan_stdout_x(path):
    """stdout: the exact form line "Cache test mode: prepare-cold" (item 355 (e)) and every "Cache test mode:" line."""
    r = dict(present=os.path.isfile(path), prepare_cold=0, any=0)
    if r['present']:
        with open(path, 'rb') as f:
            for line in f:
                if line.startswith(b'Cache test mode:'):
                    r['any'] += 1
                    if line.startswith(b'Cache test mode: prepare-cold'):
                        r['prepare_cold'] += 1
    return r


def bvh_col(sx, long_rows):
    """Item 355 (zh): the number of BvhLoopCapTrip: lines in the groups i-1 .. i of every frame >= 100 ms (data, not a class)."""
    return [(x['n'], sum(1 for g in sx['bvh'] if x['i'] - 1 <= g <= x['i'])) for x in long_rows]


def ident_t4(s, spec):
    """T-4 of sc_s with the form KYTY_PIPELINE_PRECACHE=0: no queued line and 0 precache lines is the identity (0 = 0);
    the letter row of sc_s ("no queued line" -> broken) is printed beside (executor's variant, a question to the lead)."""
    pre = sum(1 for e in s['pipe'] if e[2] == 'precache')
    q = s['queued']
    if spec['pre0']:
        return pre == 0 and q is None, '%d / %s (KYTY_PIPELINE_PRECACHE=0: no queue)' % (pre, 'no queued line' if q is None else
                                                                                        q[1] + q[2])
    return q is not None and pre == q[1] + q[2], '%d / %s' % (pre, (q[1] + q[2]) if q else 'no queued line')


def gate9(g, spec, reading=None):
    """Item 241 (v)(7) cold gate on a C5 / T2 arm, item 362 (b).  p362 (the seal): when the arm runs KYTY_PIPELINE_PRECACHE=0
    (form C5) the recipe member is replaced by >= 1 in-game creation after the entry line (create_after: lines "AvTrace: pipeline "
    without "precache" with a " us=" field whose log line number is above the line "Level has started: L"); new permutation and
    skipped draw by the letter; without PRECACHE=0 (form APP) the letter.  letter: the gate of sc_s (new permutation, new recipe
    and skipped draw after the entry line) - KYTY_PIPELINE_PRECACHE=0 stops the recipe writer (4fc501f4 pipelineCache.cpp:5858),
    so it never holds in the form C5; variant (the executor's, rejected by item 362 (b), printed): under PRECACHE=0 the recipe
    member dropped with no replacement.  Returns (cold, word)."""
    reading = reading or T2_GATE_READING
    if g is None:
        return False, 'undetermined (no scene frame)'
    if not g['attr_ok']:
        return False, 'undetermined (T-3/T-4)'
    if reading == 'p362' and spec['pre0']:
        cold = g['perm_after'] >= 1 and g.get('create_after', 0) >= 1 and g['skip_after'] >= 1
    elif reading == 'variant' and spec['pre0']:
        cold = g['perm_after'] >= 1 and g['skip_after'] >= 1
    else:
        cold = g['perm_after'] >= 1 and g['rec_new_after'] >= 1 and g['skip_after'] >= 1
    return cold, 'cold' if cold else 'level not cold'


def early9(s, fz, attr_ok):
    """Item 241 (b)(4), item 355 (d): per attributed frame >= 100 ms the cost = PREP + the us of the async creations in groups
    i-2 .. i+1, per series with gap_pipe >= 100 ms the cost = the async us ending in the series (sc_s.early); lead = min over
    the hashes of FirstUse - min Register (sc_s.early).  The sc_s cost (PREP only for frames) is the second reading."""
    e = A.early(s, fz, None, attr_ok)
    if e is None:
        return None
    longs = [x for x in fz['long'] if x['attr'].startswith('SHADER')]
    ev = []
    k = 0
    for x in e['events']:
        if x['kind'] == 'frame':
            i = longs[k]['i']
            k += 1
            asy = sum(p[3] for p in s['pipe'] if i - 2 <= p[0] <= i + 1 and p[2] == 'async')
            ev.append(dict(x, cost=x['cost'] + asy, cost_prep=x['cost']))
        else:
            ev.append(dict(x, cost_prep=x['cost']))
    known = [x for x in ev if x['lead'] is not None]
    short = sum(1 for x in known if x['lead'] < x['cost'])
    short_prep = sum(1 for x in known if x['lead'] < x['cost_prep'])
    return dict(events=ev, known=len(known), short=short, short_prep=short_prep, regs=e['regs'], firsts=e['firsts'],
                leads=e['leads'])


# ---------------------------------------------------------------------------------------------------------- haze (item 355 (g))
def haze_cmd(path, ffmpeg=FFMPEG):
    """The ffmpeg command of the lead's detector: crop 300x60 at (660, 60), scale 60x12, raw rgb24 to stdout."""
    return [ffmpeg, '-loglevel', 'error', '-i', path, '-vf', '%s,scale=%d:%d' % (HAZE_CROP, HAZE_W, HAZE_H), '-f', 'rawvideo',
            '-pix_fmt', 'rgb24', '-']


def haze_sat(path, ffmpeg=FFMPEG):
    """The per-frame mean saturation of the lead's detector on a video."""
    return haze_sat_bytes(subprocess.run(haze_cmd(path, ffmpeg), capture_output=True).stdout)


def haze_sat_bytes(d):
    """The mean of (max - min) / (max + 1) over the 60x12 pixels of every whole rgb24 frame of d (haze_s8.py)."""
    fs = HAZE_W * HAZE_H * 3
    n = len(d) // fs
    sat = []
    for i in range(n):
        b = d[i * fs:(i + 1) * fs]
        t = 0
        for j in range(0, len(b), 3):
            r, g, bb = b[j], b[j + 1], b[j + 2]
            mx = max(r, g, bb)
            mn = min(r, g, bb)
            t += (mx - mn) / (mx + 1)
        sat.append(t / (HAZE_W * HAZE_H))
    return sat


def haze_med(sat):
    v = sorted(sat[HAZE_FROM:])
    if len(sat) <= HAZE_FROM:
        return 0
    m = len(v)
    return v[m // 2] if m % 2 else (v[m // 2 - 1] + v[m // 2]) / 2.0


def haze_runs(sat):
    """(median, low frames, kept series [start, end]) by the letter of haze_s8.py."""
    med = haze_med(sat)
    low = [i for i in range(HAZE_FROM, len(sat)) if sat[i] < med * HAZE_FRAC]
    runs = []
    for i in low:
        if runs and i - runs[-1][1] <= HAZE_GAP:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    return med, len(low), [r for r in runs if r[1] - r[0] >= HAZE_LEN]


def haze_after(runs):
    """(letter: series starting after frame 1 002, variant: series with any frame after 1 002)."""
    return [r for r in runs if r[0] > HAZE_AFTER], [r for r in runs if r[1] > HAZE_AFTER]


def haze_of(video, cache=None):
    """The detector on one video; the saturations are cached in <cache> by the video sha256 (a cache of another video is
    ignored)."""
    if not os.path.isfile(video):
        return None
    vsha = A.sha_file(video)
    sat = None
    if cache and os.path.isfile(cache):
        c = json.load(open(cache, encoding='ascii'))
        if c.get('video_sha256') == vsha and c.get('crop') == HAZE_CROP and c.get('scale') == [HAZE_W, HAZE_H]:
            sat = c['sat']
    if sat is None:
        sat = haze_sat(video)
        if cache:
            os.makedirs(os.path.dirname(os.path.abspath(cache)), exist_ok=True)
            json.dump(dict(video=video, video_sha256=vsha, crop=HAZE_CROP, scale=[HAZE_W, HAZE_H], sat=sat),
                      open(cache, 'w', encoding='ascii'))
    med, nlow, runs = haze_runs(sat)
    a, b = haze_after(runs)
    return dict(frames=len(sat), med=med, low=nlow, runs=runs, after=a, after_var=b, video_sha256=vsha)


# ---------------------------------------------------------------------------------------------------------- one arm
def seeds_sha(root=SEEDS_PATH + '/PPSA21564'):
    """(sha256, files) of the manifest of seedexp_s9.py over the catalogue: "<name> <bytes> <sha256>" lines sorted; (None, 0)
    without the directory."""
    if not os.path.isdir(root):
        return None, 0
    lines = sorted('%s %d %s' % (n, os.path.getsize(os.path.join(root, n)), A.sha_file(os.path.join(root, n)))
                   for n in os.listdir(root) if os.path.isfile(os.path.join(root, n)))
    return hashlib.sha256(''.join(x + NL for x in lines).encode('ascii')).hexdigest(), len(lines)


def jget(d, key, sub):
    v = (d or {}).get(key)
    return v.get(sub) if isinstance(v, dict) else None


def read_json(p):
    return json.load(open(p, encoding='utf-8')) if os.path.isfile(p) else None


def cache_rows(spec, cj, cjs_of):
    """Admission rows of the arm protocol (item 241 (g)(1)-(3), item 355 (e) form U) from runs_s/<tag>.cache.json."""
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    if cj is None:
        add('cache protocol json present', False, 'missing')
        return rows
    ra, rg = cj.get('restore_app') or {}, cj.get('restore_glc') or {}
    if spec['mode'] == 'integrity':
        src = cjs_of(spec['src']) or {}
        want_app, want_glc = jget(src, 'app_post_copy', 'sha'), jget(src, 'glc_post_copy', 'sha')
        names = ('app_post of %s' % spec['src'], 'glc_post of %s' % spec['src'])
    elif spec['mode'] == 'u':
        want_app, want_glc = EMPTY_SHA, None
        names = ('empty (form U, item 355 (e))', None)
    else:
        want_app, want_glc = SNAP_APP, SNAP_DRV
        names = ('snap0 d8ca8c8e', 'snap0_drv 1767ca0a')
    add('restore of the app caches = %s' % names[0], want_app is not None and ra.get('got') == want_app and
        ra.get('expected') == want_app, '%s / %s' % ((ra.get('got') or '-')[:16], (want_app or '-')[:16]))
    if spec['mode'] == 'u':
        add('GLCache not restored before the arm (form U)', not rg, 'none' if not rg else 'restored')
        ml = jget(cj, 'man_launch_glc', 'sha')
        mp = jget(cj, 'man_pre_glc', 'sha')
        add('man_launch_glc right before the game = man_pre_glc (form U: GLCache as found)', ml is not None and ml == mp,
            '%s / %s' % ((ml or '-')[:16], (mp or '-')[:16]))
        sd = jget(cj, 'seeds', 'sha')
        add('the S-cat catalogue = seeds_manifest of the seal (%s)' % SEEDS_SHA[:8], sd == SEEDS_SHA, (sd or '-')[:16])
    else:
        add('restore of GLCache = %s' % names[1], want_glc is not None and rg.get('got') == want_glc and
            rg.get('expected') == want_glc, '%s / %s' % ((rg.get('got') or '-')[:16], (want_glc or '-')[:16]))
        ml = jget(cj, 'man_launch_glc', 'sha')
        add('man_launch_glc right before the game = restore_glc.got (item 250 (zh))', ml is not None and ml == rg.get('got'),
            '%s / %s' % ((ml or '-')[:16], (rg.get('got') or '-')[:16]))
    for key in ('return_app', 'return_glc'):
        r = cj.get(key) or {}
        add('%s after the arm = its copy' % key, r.get('got') is not None and r.get('got') == r.get('expected'),
            '%s / %s' % ((r.get('got') or '-')[:16], (r.get('expected') or '-')[:16]))
    ib, ia = jget(cj, 'installed_before', 'sha'), jget(cj, 'installed_after', 'sha')
    add('installed binary after the arm = installed before the arm (item 250 (b))', ib is not None and len(ib) == 64 and ia == ib,
        '%s / %s' % ((ia or '-')[:16], (ib or '-')[:16]))
    add('installed binary before the arm = the installed %s of item 374 (g) (item 371 (g), RC1)' % INST_WANT[:8],
        ib == INST_WANT,
        (ib or '-')[:16])
    add('return_prev_ok (no RETURN_FAILED guard before the arm, item 250 (v))', jget(cj, 'return_prev', 'ok') == '1',
        jget(cj, 'return_prev', 'ok') or '-')
    for key in ('man_pre_app', 'man_pre_glc', 'man_post_app', 'man_post_glc', 'glc_pre_copy'):
        add('manifest %s recorded' % key, bool(jget(cj, key, 'sha')), (jget(cj, key, 'sha') or '-')[:16])
    if spec['tag'] in PI_W.values():
        for key in ('app_post_copy', 'glc_post_copy'):
            add('%s recorded (the R arm restores it)' % key, bool(jget(cj, key, 'sha')), (jget(cj, key, 'sha') or '-')[:16])
    return rows


def admit(spec, js, pred_sha, cj, cjs_of, pred_path):
    env = js.get('env') or {}
    at = js.get('attempts') or []
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    want_bin = BIN_U if spec['binkind'] == 'u' else BIN_S
    add('one attempt (--attempts 1, no warmup)', len(at) == 1 and at[0].get('label') == 'attempt 1', len(at))
    add('binary %s' % want_bin[:8], js.get('binary_sha256') == want_bin, (js.get('binary_sha256') or '')[:8])
    add('guest args -lvl %s' % spec['level'], js.get('guest_args') == '-lvl %s' % spec['level'], js.get('guest_args'))
    add('gates empty (shipped defaults)', js.get('gates') == '', repr(js.get('gates'))[:40])
    add('no KYTY_GPU_CHECKPOINTS', 'KYTY_GPU_CHECKPOINTS' not in env, '')
    add('no KYTY_GATE_SCHEDULE', 'KYTY_GATE_SCHEDULE' not in env and 'KYTY_GATE_SCHEDULE_ABBA' not in env, '')
    add('no KYTY_GAME_PATCH (item 342 (e))', 'KYTY_GAME_PATCH' not in env, env.get('KYTY_GAME_PATCH') or '')
    rec = env.get('KYTY_REC')
    add('video KYTY_REC rec_%s.mp4' % spec['tag'], rec is not None and rec.replace('\\', '/').endswith('/rec_%s.mp4' % spec['tag']),
        rec)
    val = B.last_value(js.get('cmdline') or [], '--vulkan-validation')
    add('--vulkan-validation false', val == 'false', val)
    (fo, fd), (so, sd) = env_rows(spec, env)
    add('KYTY_* families = the seal (item 241 (v)(6), letter)', fo, fd)
    add('every KYTY_* key = the seal (executor variant, stricter)', so, sd)
    add('hold --hold %d' % spec['hold'], js.get('hold_s') == spec['hold'], js.get('hold_s'))
    pr = js.get('prereg') or {}
    add('prereg = the seal now', pred_sha is not None and pr.get('sha256') == pred_sha and
        (pr.get('path') or '').replace('\\', '/') == pred_path, (pr.get('sha256') or '')[:8])
    add('no pipeline-cache retry', not any(a.get('pipeline_cache_off') for a in at), '')
    rows.extend(cache_rows(spec, cj, cjs_of))
    return rows


def score_arm(tag, form=None, root=LINK_DIR, pred_sha=None, pred_path=PRED_PATH, ix=None, haze=True):
    """Everything about one arm of S10; None when it was not made (no <tag>.json)."""
    spec = resolved(SPEC[tag], form)
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
    r = dict(tag=tag, level=spec['level'], cls=spec['cls'], group=spec['group'], form=spec.get('form'),
             outcome142=base['outcome'], reason142=base['reason'], marks=base.get('marks') or [], ended=base['ended'],
             exited=base['exited'], attempt=base['attempt_outcome'], hold_s=base['hold_s'], vke=base.get('vke'),
             glitch=base['glitch'], derive142=base['derive'], log_sha=base.get('log_sha'),
             prep_created_s=at.get('prep_created_s'), prep_ready_s=at.get('prep_ready_s'))
    r['admit'] = admit(spec, js, pred_sha, cj, cjs_of, pred_path)
    vid = os.path.join(root, 'rec_%s.mp4' % tag)
    r['video'] = os.path.isfile(vid)
    if log142 is None:
        r.update(entered=False, ident=[], fail=['no log'])
        return r
    s = A.scan_s(lp)
    std = A.scan_stdout(sp)
    sx = scan_x(lp)
    sox = scan_stdout_x(sp)
    eg, end, fi = A.locate(s, spec['level'])
    r['entered'] = eg is not None
    r['present_rows'] = len(s['rows'])
    r['first'] = None if fi is None else (s['rows'][fi][0], s['rows'][fi][1], s['rows'][fi][2])
    ident = [x for x in A.identities(s, std, spec['cls']) if not x[0].startswith('T-4')]
    if spec['cls'] == 'T':
        ok4, d4 = ident_t4(s, spec)
        ident.append(('T-4 AvTrace pipeline precache lines = G + C queued (KYTY_PIPELINE_PRECACHE=0: 0 = no queue)', ok4, d4))
    ident.append(('scan_x rows = scan_s rows (the group index of BvhLoopCapTrip / CsPretranslate)', sx['rows'] == len(s['rows']),
                  '%d / %d' % (sx['rows'], len(s['rows']))))
    ident.append(('scan_x lines = scan_s lines (the line numbers of the in-game creations, item 362 (b))', sx['lines'] == s['lines'],
                  '%d / %d' % (sx['lines'], s['lines'])))
    attr_ok = spec['cls'] == 'T' and all(ok for name, ok, _ in ident if name.startswith(('T-3', 'T-4')))
    r['attr_ok'] = attr_ok
    d142 = base['derive']
    agree = (d142['first'] is None and fi is None) or (
        d142['first'] is not None and fi is not None and d142['first'][0] == s['rows'][fi][0]
        and d142['frames_after_first'] == end - fi - 1)
    ident.append(('first scene frame and rows after it = the inherited sc142.derive', agree,
                  '%s / %s' % (d142['first'], r['first'])))
    if spec['group'] in ('pi', 'c5', 't2', 'cs0'):
        want = 'S-pcw: KYTY_S_PCW=%s KYTY_S_PCW_FORCE_MS=%s' % (
            (spec['pcw'], PCW_FORCE_MS) if spec['pcw'] is not None else ('0', '0'))
        r['admit'].append(('the knob line "%s" of f3b3aa3b (patch line 96)' % want,
                           len(s['spcw']) >= 1 and all(x == want for x in s['spcw']), ';'.join(s['spcw'][:2]) or 'none'))
    r['admit'].append(('0 lines GamePatch: in the log (item 342 (e))', sx['gamepatch'] == 0, sx['gamepatch']))
    r['prep'] = dict(queued=s['queued'], created_ms=s['created_ms'], ready=s['ready'], waited_ms=s['waited_ms'],
                     dload=s['dload'], disabled=s['disabled'], seed_installed=s['seed_installed'],
                     seed_ignored=s['seed_ignored'], cache_test=sox['any'], prepare_cold=sox['prepare_cold'],
                     prog_ms=sx['prog_ms'], prog_n=sx['prog_n'])
    r['create'] = dict(n=len(sx['create']), med=A.med(sx['create']), nous=sx['create_nous'],
                       all=A.cold_class(A.creations(s)), all_n=len(A.creations(s)))
    r['saves'] = dict(driver=len(s['dsave']), last_bytes=s['dsave'][-1][1] if s['dsave'] else None, fail=s['savefail'],
                      incomplete=s['savefail_inc'], forced=sum(1 for e in s['dsave'] if e[3]))
    r['loaded'] = s['dload'][0] if s['dload'] else None
    r['csp'] = sx['csp']
    r['pcw_trace'] = A.pcw_trace(s)
    if fi is not None:
        prep = A.assign_prep(s)
        r['f1'] = A.freeze(s, fi, end, prep, attr_ok, 1)
        r['f2'] = A.freeze(s, fi, end, prep, attr_ok, 2)
        for k, f in (('1', r['f1']), ('2', r['f2'])):
            t5a, t5b = f['T5']
            ident.append(('T-5 partition (reading %s)' % k, t5a == t5b, '%d / %d' % (t5a, t5b)))
        r['att100'] = A.attributed(r['f1'], attr_ok, A.K3_US)
        r['att1s'] = A.attributed(r['f1'], attr_ok, A.K2_US)
        r['att_pcw100'] = A.attributed_pcw(r['f1'], attr_ok, A.K3_US)
        r['unatt100'] = A.unattributed(r['f1'], attr_ok, A.K3_US)
        g = A.gates(s, std, eg, spec, attr_ok)
        g['attr_ok'] = attr_ok
        el = A.entry_line(s, spec['level'])
        g['create_after'] = sum(1 for ln in sx['create_ln'] if el is not None and ln > el)      # item 362 (b)
        r['gates'] = g
        r['bvh'] = bvh_col(sx, r['f1']['long'])
        r['early'] = early9(s, r['f1'], attr_ok)
        r['pcw'] = A.pcw_arm(s, fi, end)
        r['skips_after'] = sum(1 for e in s['skips'] if e[0] > fi)
        r['skips_after_scene'] = sum(1 for e in s['skips'] if fi < e[0] < end)
        r['held_after'] = sum((A.xget(s, i, 1) or 0) for i in range(fi + 1, end))
        r['dt100'] = r['f1']['window']['shown100'] + r['f1']['hold']['shown100']
        r['skip_rows'] = r['f1']['window']['skip_rows'] + r['f1']['hold']['skip_rows']
        r['held'] = r['f1']['window']['held'] + r['f1']['hold']['held']
    if haze and spec['group'] == 'pi':
        r['haze'] = haze_of(vid, os.path.join(root, 'runs_s', '%s.haze.json' % tag))
    r['ident'] = ident
    fail = ['admission: %s' % a[0] for a in r['admit'] if not a[1]]
    fail += ['identity: %s' % name for name, ok, _ in ident if ok is False]
    r['fail'] = fail
    return r


def ok_arm(r):
    return r is not None and not r['fail']


def clean_arm(r):
    """Item 371 (b): the arm is readable - admitted, entered, the video read by the detector (haze not None) with frames after
    frame 1 002 (0-based), no death marker; the video frames, the present rows and the one-frame glitches are data, not members."""
    h = r.get('haze')
    return ok_arm(r) and r.get('entered') and h is not None and h['frames'] - 1 > HAZE_AFTER and not r['marks'] and \
        not r['ended'] and not r['exited']


def clean_arm_x(r):
    """The executor variant of seal 05b (printed beside, item 371 (b)): admitted, entered, a video of >= 3 000 frames with 0
    one-frame glitches, read by the detector, no death marker."""
    g = r.get('glitch') or {}
    return ok_arm(r) and r.get('entered') and r.get('video') and g.get('video_frames', 0) >= FRAMES_VIDEO and \
        g.get('glitches') == 0 and not r['marks'] and not r['ended'] and not r['exited'] and r.get('haze') is not None


def video_rule_line(word, wordx):
    """Item 371 (b): the word of seal 05b printed beside."""
    return 'executor variant (seal 05b: + video >= %d frames and 0 one-frame glitches as members; not members by item 371 (b)): ' \
           '%s%s' % (FRAMES_VIDEO, wordx, '' if wordx == word else ' - DIFFERS (video rule)')


# ---------------------------------------------------------------------------------------------------------- readings
def read_pi(get):
    """Item 355 (g): the repeat of integrity, the words READ_1 / READ_2 / READ_3 / READ_OTHER / NOT_EVALUABLE."""
    out = []
    rs = dict((t, get(t)) for t in PI_ORDER)
    if any(v is None for v in rs.values()):
        out.append('repeat of integrity: not every arm made - NOT_EVALUABLE')
        return 'NOT_EVALUABLE', out
    bad = [t for t in PI_ORDER if not clean_arm(rs[t])]
    bad_x = [t for t in PI_ORDER if not clean_arm_x(rs[t])]
    hz = {}
    for t in PI_ORDER:
        h = rs[t].get('haze')
        g = rs[t].get('glitch') or {}
        hz[t] = None if h is None else bool(h['after'])
        out.append('%s: %s (executor variant: %s); video frames %s, present rows %s, one-frame glitches %s; haze frames %s median %s '
                   'low %s series %s; after frame %d (letter: start > %d) %s; variant (any frame > %d) %s' % (
                       t, 'readable' if clean_arm(rs[t]) else 'NOT readable (%s)' % (rs[t]['fail'] or 'entry/video/markers'),
                       'readable' if clean_arm_x(rs[t]) else 'NOT readable', g.get('video_frames'), rs[t].get('present_rows'),
                       g.get('glitches'), h and h['frames'], h and round(h['med'], 4), h and h['low'], h and h['runs'],
                       HAZE_AFTER, HAZE_AFTER, h and h['after'], HAZE_AFTER, h and h['after_var']))
    held = dict((t, rs[t]['derive142']['dt_after_first_us'] >= HOLD_W_US) for t in ('pi_w1', 'pi_w0'))
    out.append('W arms presented >= 300 s after the first scene frame: %s' % held)
    loaded = {}
    for rt, wt in PI_W.items():
        lb = rs[rt].get('loaded')
        wb = (rs[wt].get('saves') or {}).get('last_bytes')
        dis = (rs[rt].get('prep') or {}).get('disabled')
        loaded[rt] = lb is not None and lb == wb and dis == 0
        out.append('%s loaded %s bytes = last write of %s %s, disabled %s -> %s' % (
            rt, lb, wt, wb, dis, 'PASS' if loaded[rt] else 'FAIL'))
    z1 = rs['pi_r1'].get('pcw_trace')
    out.append('(z)(1) on pi_r1: %s' % ('undetermined (RC1 S5d: 0 "AvTrace: pcw overlap wait gfx|cs" lines; printed beside '
                                        'FIXED, not a member - item 355 (g))' if z1 is None or z1['waits_n'] == 0 else
                                        '%d wait lines - a lower bound of overlaps, GuestGpu waits only' % z1['waits_n']))
    var = dict((t, bool(rs[t]['haze']['after_var'])) if rs[t].get('haze') else (t, None) for t in PI_ORDER)
    wordx = 'NOT_EVALUABLE' if bad_x or not all(held.values()) else pi_word(hz, loaded)
    if bad or not all(held.values()):
        out.append('arms not readable (admission, identity, entry, the video read by the detector with frames after %d, markers, '
                   'hold - item 371 (b)): %s' % (HAZE_AFTER, bad or 'hold'))
        out.append(video_rule_line('NOT_EVALUABLE', wordx))
        return 'NOT_EVALUABLE', out
    word = pi_word(hz, loaded)
    wv = pi_word(var, loaded)
    wx = pi_word(hz, loaded, False)
    out.append('series after %d: pi_w1 %s pi_r1 %s pi_w0 %s pi_r0 %s; loaded both R %s' % (
        HAZE_AFTER, hz['pi_w1'], hz['pi_r1'], hz['pi_w0'], hz['pi_r0'], all(loaded.values())))
    out.append('reading (variant: a series with any frame after %d): %s%s' % (HAZE_AFTER, wv,
                                                                             '' if wv == word else ' - DIFFERS (edge 1 002)'))
    out.append('reading of the executor (READ_3 without the loaded member of (2), rejected by item 362 (v)): %s%s' % (
        wx, '' if wx == word else ' - DIFFERS (the loaded member)'))
    out.append(video_rule_line(word, wordx))
    if word == 'READ_3' and hz['pi_r0'] and (hz['pi_w1'] or hz['pi_w0']):
        out.append('note: a series in pi_r0 and in a W arm, none in pi_r1 - READ_3 ("only in pi_r0" among the R arms, item 362 (v))')
    meaning = {'READ_1': '(1) the sign with the blob =1 - a defect of S-pcw: iteration 2, B33 not FIXED (decision S11)',
               'READ_2': '(2) the event of pcw_int is not tied to the blob =1 - B33 FIXED by item 355 (g)(2) (decision S11)',
               'READ_3': '(3) an effect of the scene [I], as (2): with the loaded member of (2) on both R (item 362 (v)) '
                         '(decision S11)',
               'READ_OTHER': 'another outcome - decision S11'}
    out.append('repeat of integrity (item 355 (g)): %s - %s; the lead sheet of every series after frame %d' % (
        word, meaning[word], HAZE_AFTER))
    return word, out


def pi_word(hz, loaded, need_load=True):
    """Item 355 (g), item 362 (v): "as (2)" is the consequence and the condition - READ_3 needs the loaded member of (2) on both
    R, else READ_OTHER; need_load False gives the executor's reading (printed beside)."""
    r1, r0 = hz['pi_r1'], hz['pi_r0']
    w = hz['pi_w1'] or hz['pi_w0']
    both_loaded = all(loaded.values())
    if r1 and not r0:
        return 'READ_1'
    if r1 and r0:
        return 'READ_2' if both_loaded else 'READ_OTHER'
    if r0:
        return 'READ_3' if both_loaded or not need_load else 'READ_OTHER'
    if w:
        return 'READ_3' if both_loaded or not need_load else 'READ_OTHER'
    return 'READ_2' if both_loaded else 'READ_OTHER'


def read_c5(get):
    """Item 355 (d): the word "salt without precache neutralises" and the form of T2 chosen by code.
    Returns (form 'c5' | 'app' | None, word, lines)."""
    r = get('c5_0')
    out = []
    if r is None:
        return None, 'NOT_MADE', ['c5_0 not made - the T2 form is undetermined']
    if not ok_arm(r) or not r.get('entered'):
        out.append('c5_0: arm %s, entered %s - the reading is undetermined; T2 does not go (a question to the lead)' % (
            'PASS' if ok_arm(r) else 'FAIL %s' % r['fail'], r.get('entered')))
        return None, 'UNDETERMINED', out
    c = r['create']
    yes = c['n'] >= C5_MIN and c['med'] is not None and c['med'] >= C5_US
    out.append('c5_0 (%s, KYTY_PIPELINE_SALT=c5_0, KYTY_PIPELINE_PRECACHE=0): in-game creations (AvTrace: pipeline without '
               '"precache", with a us field) %d, median us %s; lines without a us field %d; sc_s creations %d %s' % (
                   L0, c['n'], c['med'], c['nous'], c['all_n'], c['all']))
    out.append('salt without precache neutralises (>= %d creations, median >= %d us): %s' % (C5_MIN, C5_US,
                                                                                           'YES' if yes else 'NO'))
    form = 'c5' if yes else 'app'
    out.append('T2 form (item 355 (d)): %s' % ('C5 - full return, KYTY_PIPELINE_SALT=<tag>, KYTY_PIPELINE_PRECACHE=0' if yes else
                                             'APP "cold of the application" - full return, precache by default, no salt; '
                                             'the driver cache is not neutralised [U]; the base reads the application side'))
    return form, 'YES' if yes else 'NO', out


def t2_counted(r, reading=None):
    if r is None or not ok_arm(r) or not r.get('entered'):
        return False
    return gate9(r.get('gates'), resolved(SPEC[r['tag']], r.get('form')), reading)[0]


def read_t2(get):
    """Item 355 (d), (zh): the T2 base, the S-early row, the BvhLoopCapTrip column, t2_cs0."""
    out = []
    form, _, _ = read_c5(get)
    out.append('T2 form: %s; the gate counts by the %s reading (T2_GATE_READING)' % (form, T2_GATE_READING))
    counted = []
    counted_l = 0
    counted_v = 0
    for j in range(len(T2_LIST)):
        tag = 't2_%d' % (j + 1)
        r = get(tag)
        if r is None:
            continue
        spec = resolved(SPEC[tag], r.get('form'))
        gp = gate9(r.get('gates'), spec, 'p362')
        gl = gate9(r.get('gates'), spec, 'letter')
        gv = gate9(r.get('gates'), spec, 'variant')
        c = t2_counted(r)
        counted_l += t2_counted(r, 'letter')
        counted_v += t2_counted(r, 'variant')
        if c:
            counted.append(r)
        e = r.get('early')
        out.append('%s %s: %s; arm %s; gate (item 362 (b)) %s, by the letter (with the recipe) %s, executor variant %s; in-game '
                   'creations after the entry %s; skip rows %s held %s presented >= 100 ms %s; attributed >= 100 '
                   'ms %s (PCW %s), >= 1 s %s; not attributed %s; sc142 %s; BvhLoopCapTrip in i-1..i of frames >= 100 ms %s; '
                   'S-early lead<cost %s (PREP only %s) of %s' % (
                       tag, r['level'], 'COUNTED' if c else 'OUT', 'PASS' if ok_arm(r) else 'FAIL %s' % r['fail'], gp[1], gl[1],
                       gv[1], (r.get('gates') or {}).get('create_after'),
                       r.get('skip_rows'), r.get('held'), r.get('dt100'), r.get('att100'), r.get('att_pcw100'),
                       r.get('att1s'), A.fmt_unattr(r.get('unatt100')), r.get('outcome142'), r.get('bvh'),
                       e['short'] if e else None, e['short_prep'] if e else None, e['known'] if e else None))
    out.append('T2 counted %d of %d needed (item 362 (b)); by the letter (with the recipe) %d; executor variant %d' % (
        len(counted), T2_NEED, counted_l, counted_v))
    kn = sum(r['early']['known'] for r in counted if r.get('early'))
    sh = sum(r['early']['short'] for r in counted if r.get('early'))
    shp = sum(r['early']['short_prep'] for r in counted if r.get('early'))
    for r in counted:
        for x in (r.get('early') or {}).get('events', []):
            out.append('  S-early %s %s n %s lead %s cost %s (PREP-only %s)' % (r['tag'], x['kind'], x['n'], x['lead'],
                                                                              x['cost'], x['cost_prep']))
    out.append('S-early first half (item 241 (b)(4)): lead < cost in %s of %d events -> %s; PREP-only reading %s of %d; the '
               'second half (p95 of linking) - S11' % (sh, kn, 'undetermined (denominator 0)' if kn == 0 else (
                   '>= 50 %' if sh * 2 >= kn else '< 50 %'), shp, kn))
    a, b = get('t2_1'), get('t2_cs0')
    if a is None or b is None or 'f1' not in a or 'f1' not in b:
        out.append('t2_cs0 against t2_1: undetermined (an arm missing or without a scene frame)')
    else:
        out.append('t2_cs0 (KYTY_CS_PRETRANSLATE=0) against t2_1 (data rows, decision S11): skip rows %+d (%d / %d), held flips '
                   '%+d (%d / %d), presented frames >= 100 ms %+d (%d / %d); CsPretranslate lines t2_1 %s, t2_cs0 %s' % (
                       b['skip_rows'] - a['skip_rows'], b['skip_rows'], a['skip_rows'], b['held'] - a['held'], b['held'],
                       a['held'], b['dt100'] - a['dt100'], b['dt100'], a['dt100'], sorted(a['csp'].items()),
                       sorted(b['csp'].items())))
    return out


def u_screen(r):
    """Item 355 (e), item 371 (v): (seconds, kind) of the preparation screen of a U arm.  'measured' - both lines seen: the later of
    prep_created_s and prep_ready_s (from the Popen); 'lower bound' - a line missing: the maximum of elapsed_ms of the lines
    "ShaderPreparation: progress" (the startup wait loop, 4414e235 window.cpp:1015) and, when the attempt ended by timeout, the
    --timeout of the arm; 'none' - neither."""
    if r is None:
        return None, 'none'
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


def u_eval(r):
    """One U arm: (fails S-cat True / False / None undetermined, the gate word, (screen seconds, kind) of u_screen, detail)."""
    if r is None:
        return None, 'not made', (None, 'none'), ''
    p = r.get('prep') or {}
    gates = p.get('seed_installed', 0) >= 1 and p.get('prepare_cold', 0) >= 1
    if not gates:
        return None, 'CATALOGUE NOT INSTALLED (ShaderSeed: installed %d, Cache test mode: prepare-cold %d) - not an S-cat ' \
                     'attempt (a form interference, not counted among the S-cat arms, a repeat only by a lead item, item 371 ' \
                     '(g)), stop of the U series, a question to the lead' % (p.get('seed_installed', 0),
                                                                              p.get('prepare_cold', 0)), (None, 'none'), ''
    screen = u_screen(r)
    if not ok_arm(r) or not r.get('entered') or 'f1' not in r:
        return None, 'gates ok', screen, 'arm %s entered %s' % ('PASS' if ok_arm(r) else 'FAIL', r.get('entered'))
    if r['att100'] is None:
        return (True if r['skips_after'] > 0 else None), 'gates ok', screen, 'attribution undetermined'
    fails = r['skips_after'] > 0 or r['att100'] > 0
    return fails, 'gates ok', screen, 'skip lines after the first scene frame %d (inside the scene %d), attributed >= 100 ms ' \
                                      '%d' % (r['skips_after'], r['skips_after_scene'], r['att100'])


def screen_text(sec, kind):
    if kind == 'measured':
        return '%.1f s' % sec
    if kind == 'lower bound':
        return ('> %.1f s (lower bound)' % sec) if sec > PREP_LIMIT_S else \
            '>= %.1f s (lower bound, not above %d s - the screen undetermined, not an S-cat member)' % (sec, PREP_LIMIT_S)
    return 'undetermined (no line, no progress line, no timeout - not an S-cat member)'


def read_u(get):
    """Item 355 (e), item 371 (v): KILLED / ALIVE_BY_PROBE_5 / UNDETERMINED; the letter of item 355 (e) and the executor variant
    beside."""
    out = []
    nf = 0
    nf_m = 0
    und = 0
    und_scr = 0
    over = False
    for j in range(U_N):
        tag = 'u_%d' % (j + 1)
        r = get(tag)
        f, gw, (sec, kind), det = u_eval(r)
        if sec is not None and sec > PREP_LIMIT_S:
            over = True
        member = kind == 'measured' or (kind == 'lower bound' and sec > PREP_LIMIT_S)
        nf += f is True
        nf_m += f is True and member
        und += f is None
        if not member and f is not None:
            und_scr += 1
        p = (r or {}).get('prep') or {}
        g = (r or {}).get('gates') or {}
        out.append('%s %s: %s; S-cat member %s; stdout Shaders: %s, rec_new_after %s, perm_after %s, skip lines after the first '
                   'scene frame %s; preparation screen %s (PipelinePrecache: all pipelines created %s s, ShaderPreparation: ready '
                   '%s s; progress lines %s, max elapsed_ms %s; attempt %s; log created %s ms, startup wait %s ms); %s' % (
                       tag, U_LIST[j], gw, {True: 'FAILS', False: 'holds', None: 'undetermined'}[f],
                       g.get('stdout_shaders', '-'), g.get('rec_new_after', '-'), g.get('perm_after', '-'),
                       (r or {}).get('skips_after', '-'), screen_text(sec, kind), r and r.get('prep_created_s'),
                       r and r.get('prep_ready_s'), p.get('prog_n'), p.get('prog_ms'), r and r.get('attempt'),
                       p.get('created_ms'), p.get('waited_ms'), det))
    if nf_m >= U_KILL or over:
        word = 'KILLED'
    elif und or und_scr:
        word = 'UNDETERMINED'
    else:
        word = 'ALIVE_BY_PROBE_5'
    letter = 'KILLED' if nf >= U_KILL or over else ('UNDETERMINED' if und else 'ALIVE_BY_PROBE_5')
    varx = 'KILLED' if nf >= U_KILL or over else ('UNDETERMINED' if und or und_scr else 'ALIVE_BY_PROBE_5')
    out.append('S-cat (item 229 (d)(2), item 355 (e), item 371 (v)): failing members %d of %d (kill at >= %d), a screen > %d s %s, '
               'arms without a screen measure %d -> %s' % (nf_m, U_N, U_KILL, PREP_LIMIT_S, over, und_scr, word))
    out.append('by the letter of item 355 (e) ("else alive": an arm without a screen measure is alive, its failure counts): %s%s' % (
        letter, '' if letter == word else ' - DIFFERS (screen undetermined)'))
    out.append('executor variant (a failing arm without a screen measure counts among the failing, %d failing): %s%s' % (
        nf, varx, '' if varx == word else ' - DIFFERS (a failing arm without a screen measure)'))
    return word, out


# ---------------------------------------------------------------------------------------------------------- order
def made_fn(root=LINK_DIR):
    def made(t):
        return os.path.isfile(os.path.join(root, '%s.json' % t)) or os.path.isfile(os.path.join(root, 'attempt_%s.txt' % t))
    return made


def allowed(tag, made, get):
    """Order and conditions of item 355 (k): (rc, reason) - rc 0 allowed, 1 order, 6 a condition not met."""
    if tag not in SPEC:
        return 2, 'unknown tag'
    if made(tag):
        return 1, 'already made'
    i = SEQ.index(tag)
    for t in SEQ[:i]:
        r = get(t) if made(t) else None
        if r is not None and r['marks']:
            return 6, 'the series stops at the first death marker (%s, item 355 (k))' % t
    spec = SPEC[tag]
    grp = spec['group']
    if grp in ('pi', 'c5'):
        prev = SEQ[i - 1] if i > 0 else None
        if prev and not made(prev):
            return 1, '%s not made' % prev
        return 0, 'ok'
    if grp in ('t2', 'cs0'):
        if not made('c5_0'):
            return 1, 'c5_0 not made'
        form, word, _ = read_c5(get)
        if form is None:
            return 6, 'the C5 reading is %s - the T2 form is undetermined (a question to the lead)' % word
        if tag == 't2_1':
            return 0, 'ok'
        if tag == 't2_cs0':
            return (0, 'ok') if made('t2_1') else (1, 't2_1 not made')
        j = spec['k']
        prev = 't2_cs0' if j == 1 else 't2_%d' % j
        if not made(prev):
            return 1, '%s not made' % prev
        counted = sum(1 for x in range(j) if made('t2_%d' % (x + 1)) and t2_counted(get('t2_%d' % (x + 1))))
        if j >= T2_NEED and counted >= T2_NEED:
            return 6, 'five counted already - no reserve needed'
        return 0, 'ok'
    if grp == 'u':
        if not made('t2_cs0') or not t2_done(get, made):
            return 1, 'T2 / t2_cs0 not finished'
        j = spec['k']
        if j > 0:
            prev = 'u_%d' % j
            if not made(prev):
                return 1, '%s not made' % prev
            for x in range(j):
                f, gw, _, _ = u_eval(get('u_%d' % (x + 1)))
                if gw.startswith('CATALOGUE NOT INSTALLED'):
                    return 6, 'u_%d: %s' % (x + 1, gw)
        return 0, 'ok'
    return 1, 'unknown group'


def t2_done(get, made):
    counted = sum(1 for j in range(len(T2_LIST)) if made('t2_%d' % (j + 1)) and t2_counted(get('t2_%d' % (j + 1))))
    return counted >= T2_NEED or all(made('t2_%d' % (j + 1)) for j in range(len(T2_LIST)))


# ---------------------------------------------------------------------------------------------------------- printing
def fmt_arm(r):
    o = ['ARM %s level %s class %s form %s: %s; sc142 outcome %s (%s); log %s' % (
        r['tag'], r['level'], r['cls'], r.get('form'), 'PASS' if not r['fail'] else 'FAIL', r['outcome142'], r['reason142'],
        (r.get('log_sha') or 'MISSING')[:16])]
    for name, ok, det in r['admit']:
        o.append('  %-4s admit %s (%s)' % ('PASS' if ok else 'FAIL', name, det))
    for name, ok, det in r.get('ident', []):
        o.append('  %-4s ident %s (%s)' % ('n/a' if ok is None else ('PASS' if ok else 'FAIL'), name, det))
    if 'f1' not in r:
        o.append('  entered %s, first scene frame %s - no freeze reading' % (r.get('entered'), r.get('first')))
        return o
    o.append('  entered yes; first scene frame (n, dt, draws) %s; attribution %s' % (
        r['first'], 'DETERMINED' if r['attr_ok'] else 'UNDETERMINED'))
    f = r['f1']
    for part in ('window', 'hold'):
        p = f[part]
        o.append('  reading 1 %s: rows %d, held %d, skip rows %d, skipped draws %d, dt >= 100 ms %d (presented %d), >= 1 s %d '
                 '(presented %d); gap_pipe >= 100 ms %d, >= 1 s %d' % (part, p['rows'], p['held'], p['skip_rows'],
                                                                     p['skip_draws'], p['dt100'], p['shown100'], p['dt1s'],
                                                                     p['shown1s'], p['pipe100'], p['pipe1s']))
    bv = dict(r['bvh'])
    o.append('  frames dt >= 100 ms (n dt part class attribution PREP held BvhLoopCapTrip(i-1..i)): %s' % (
        '; '.join('%d %d %s %s %s %d %s %d' % (x['n'], x['dt'], x['part'], x['cls'], x['attr'], x['prep'],
                                              'h' if x['held'] else '-', bv.get(x['n'], 0)) for x in f['long']) or 'none'))
    o.append('  attributed >= 100 ms %s (PCW %s), >= 1 s %s; not attributed %s' % (
        r['att100'], r['att_pcw100'], r['att1s'], A.fmt_unattr(r['unatt100'])))
    sp9 = resolved(SPEC[r['tag']], r.get('form'))
    o.append('  cold gate (item 362 (b)) %s, by the letter (with the recipe) %s, executor variant %s; gates %s' % (
        gate9(r['gates'], sp9, 'p362')[1], gate9(r['gates'], sp9, 'letter')[1], gate9(r['gates'], sp9, 'variant')[1],
        dict((k, v) for k, v in r['gates'].items())))
    o.append('  in-game creations (letter of item 355 (d)) %d median %s, without us %d; sc_s creations %d %s' % (
        r['create']['n'], r['create']['med'], r['create']['nous'], r['create']['all_n'], r['create']['all']))
    p = r['prep']
    o.append('  preparation: queued %s created %s ms ready %s wait %s ms; driver cache loaded %s disabled %d; seed installed %d '
             'ignored %d; Cache test mode %d (prepare-cold %d); screen from the process start: created %s s, ready %s s' % (
                 p['queued'], p['created_ms'], p['ready'], p['waited_ms'], p['dload'], p['disabled'], p['seed_installed'],
                 p['seed_ignored'], p['cache_test'], p['prepare_cold'], r.get('prep_created_s'), r.get('prep_ready_s')))
    o.append('  skip lines after the first scene frame %d (inside the scene %d); held flips after it %d; CsPretranslate %s' % (
        r['skips_after'], r['skips_after_scene'], r['held_after'], sorted(r['csp'].items())))
    o.append('  driver cache writes %d (forced %d, last %s bytes), failures %d, Incomplete %d; S-pcw hold %s' % (
        r['saves']['driver'], r['saves']['forced'], r['saves']['last_bytes'], r['saves']['fail'], r['saves']['incomplete'],
        dict((k, v) for k, v in r['pcw'].items() if k != 'frames_n')))
    e = r['early']
    o.append('  S-early: %s' % ('undetermined' if e is None else 'registers %d, first uses %d, leads %d; events %d, known %d, '
                                'lead < cost %d (PREP-only %d)' % (e['regs'], e['firsts'], e['leads'], len(e['events']),
                                                                   e['known'], e['short'], e['short_prep'])))
    if r.get('haze') is not None:
        h = r['haze']
        o.append('  haze: frames %d median %.4f low %d series %s; after %d: %s (variant %s)' % (
            h['frames'], h['med'], h['low'], h['runs'], HAZE_AFTER, h['after'], h['after_var']))
    g = r['glitch']
    o.append('  video: %s; death markers %s; [Vulkan][E] %s' % (
        'n/a' if g is None else '%d frames, %d glitches' % (g['video_frames'], g['glitches']),
        ';'.join(m['kind'] for m in r['marks']) or 'none', r['vke']))
    return o


# ---------------------------------------------------------------------------------------------------------- seal
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')
RX_BIN = re.compile(r'^(s|u) binary: ([0-9a-f]{64}) (\S+)$')
SEALED_NAMES = ('s9/go_s9.sh', 's9/sc_s9.py', 's9/test_sc_s9.py', 's9/mut_sc_s9.py', 's9/test_go_s9.py', 's9/enter_scene_s9.py',
                's9/lvl_s9.py', 's9/lvl_s9.out.txt', 's9/seedexp_s9.py', 's9/seedexp_s9.out.txt', 's9/seeds_manifest.txt',
                'sc_s.py', 'cachex_s.py', 'test_cachex_s.py', 'snapidx_s.py', 's3/snap0_index.json', 'idle142.py', 'procload.py',
                'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py', 'fgcpu143.py', 'test_mask_s.py',
                'lead/haze_s8.py', 's9/fx/haze_pcw_int.json', 's9/fx/haze_pcw_1.json', 'C:/kyty/s142/sc142.py',
                'C:/kyty/scripts/s51_vidglitch.py')


def check_seal(pred=PRED_PATH, root=ROOT, me=None):
    rows = []
    if not os.path.isfile(pred):
        return False, [('seal file', False, pred)], {}
    seen = {}
    bins = {}
    for line in open(pred, encoding='utf-8'):
        m = RX_SEAL.match(line.rstrip('\n'))
        if m:
            seen[m.group(2)] = m.group(1)
        b = RX_BIN.match(line.rstrip('\n'))
        if b:
            bins[b.group(1)] = (b.group(2), b.group(3))
    for name in SEALED_NAMES:
        if name not in seen:
            rows.append((name, False, 'no seal line'))
    for name, sh in sorted(seen.items()):
        p = name if name.startswith('C:/') else os.path.join(root, name)
        now = A.sha_file(p) if os.path.isfile(p) else None
        rows.append((name, now == sh, (now or 'missing')[:16]))
    mine = A.sha_file(me or os.path.abspath(__file__))
    rows.append(('this scorer in the seal', seen.get('s9/sc_s9.py') == mine, mine[:16]))
    rows.append(('binary lines s = %s, u = %s' % (BIN_S[:8], BIN_U[:8]),
                 (bins.get('s') or ('',))[0] == BIN_S and (bins.get('u') or ('',))[0] == BIN_U,
                 '%s / %s' % ((bins.get('s') or ('-',))[0][:8], (bins.get('u') or ('-',))[0][:8])))
    return all(r[1] for r in rows), rows, bins


# ---------------------------------------------------------------------------------------------------------- regression
REG_C = {'c1_0': (37, 233), 'c2_0': (37, 247), 'c3_0': (37, 230), 'c4_0': (37, 231)}     # item 355 (v): creations, median us
REG_C4 = (33782, 1842, 25318)                                                              # item 335 (g): prep_ms, recipes, wait
REG_PCW = {'pcw_1': (21, 21, 9923), 'pcw_2': (20, 0, 10153), 'pcw_3': (20, 0, 10132), 'pcw_4': (20, 20, 10127)}   # item 354 (b)
REG_INT = (94435637, 0, 3749)                                                              # pcw_int loaded, disabled, frames
REG_HAZE = {'s6/rec_pcw_1.mp4': [], 's6/rec_pcw_2.mp4': [], 's6/rec_pcw_3.mp4': [], 's6/rec_pcw_4.mp4': [],
            's6/rec_pcw_int.mp4': [[1928, 1946]], 's4/rec_g_1.mp4': []}                    # item 355 (g): after frame 1 002


def regress(out=print):
    """Item 355 (k): the numbers of item 335 and item 354 from the logs of S4 and S6 through the inherited readings and the new
    letter of C5; the detector on the six videos of item 355 (g)."""
    ok = True
    for tag, (n, m) in REG_C.items():
        sx = scan_x('C:/kyty/s288/s4/log_%s.txt' % tag)
        med = A.med(sx['create'])
        good = len(sx['create']) == n and round(med) == m and sx['create_nous'] == 0
        out('REG %s in-game creations (item 355 (d) letter) %d median %s (item 355 (v): %d / %d) %s' % (
            tag, len(sx['create']), med, n, m, 'MATCH' if good else 'DIFF'))
        ok &= good
    s4 = A.scan_s('C:/kyty/s288/s4/log_c4_0.txt')
    g4 = (s4['created_ms'], s4['queued'][0] if s4['queued'] else None, s4['waited_ms'])
    good = g4 == REG_C4
    out('REG c4_0 prep_ms / recipes / wait %s (item 335 (g): %s); ms per recipe %.2f %s' % (
        g4, REG_C4, g4[0] / float(g4[1]), 'MATCH' if good else 'DIFF'))
    ok &= good and '%.2f' % (g4[0] / float(g4[1])) == '18.34'
    get = A.make_get(None, {'s4': A.PRED_PATH, 's6': A.PRED_S6}, A.load_index(), None)
    for tag, (w, f, v) in REG_PCW.items():
        r = get(tag)
        got = (r['pcw']['writes'], r['pcw']['frames'], (r['glitch'] or {}).get('video_frames'))
        good = got == (w, f, v) and (r['glitch'] or {}).get('glitches') == 0
        out('REG %s writes / frames >= 100 ms with a write / video frames %s (item 354 (b): %s) %s' % (
            tag, got, (w, f, v), 'MATCH' if good else 'DIFF'))
        ok &= good
    ri, r3 = get('pcw_int'), get('pcw_3')
    got = (ri['pcw']['loaded'], ri['pcw']['disabled'], (ri['glitch'] or {}).get('video_frames'))
    good = got == REG_INT and ri['pcw']['loaded'] == r3['saves']['last_bytes']
    out('REG pcw_int loaded / disabled / video %s = last write of pcw_3 %s (item 354 (b): %s) %s' % (
        got, r3['saves']['last_bytes'], REG_INT, 'MATCH' if good else 'DIFF'))
    ok &= good
    for v, want in REG_HAZE.items():
        h = haze_of('C:/kyty/s288/' + v)
        good = h is not None and h['after'] == want and h['after_var'] == want
        out('REG haze %s sha %s frames %d series %s after %d %s (item 355 (g): %s) %s' % (
            v, h and h['video_sha256'][:16], h and h['frames'], h and h['runs'], HAZE_AFTER, h and h['after'], want,
            'MATCH' if good else 'DIFF'))
        ok &= good
    out('REGRESSION: %s' % ('ALL OK' if ok else 'DIVERGENCE'))
    return ok


# ---------------------------------------------------------------------------------------------------------- main
def make_get(root=LINK_DIR, pred=PRED_PATH, haze=True):
    memo = {}
    psha = A.sha_file(pred) if os.path.isfile(pred) else None

    def form_now():
        if 'c5_0' not in memo:
            memo['c5_0'] = score_arm('c5_0', None, root, psha, pred, None, haze)
        return read_c5(lambda t: memo.get(t))[0]

    def get(t):
        if t not in memo:
            memo[t] = score_arm(t, form_now() if SPEC[t]['t2form'] else None, root, psha, pred, None, haze)
        return memo[t]
    return get


def sheet_frames(a, b, frames):
    """Item 371 (g), RC5: the frames of the lead sheet of the series a .. b - a-2 .. b+2 clipped to the video; a series longer than
    20 frames -> 24 frames spread evenly over [a-2, b+2] (both ends kept)."""
    lo, hi = max(0, a - 2), min(frames - 1, b + 2)
    if b - a + 1 <= SHEET_LONG:
        return list(range(lo, hi + 1))
    return sorted(set(lo + (hi - lo) * k // (SHEET_N - 1) for k in range(SHEET_N)))


def sheet_vf(idx):
    """The ffmpeg filter of the sheet: the frames idx tiled 6 wide at 480 px."""
    return "select='%s',scale=480:-1,tile=6x%d" % ('+'.join('eq(n\\,%d)' % i for i in idx), (len(idx) + 5) // 6)


def haze_sheet(tag, root=LINK_DIR, ffmpeg=FFMPEG):
    """The lead sheet of every series after frame 1 002 of a pi arm: the frames of sheet_frames() tiled 6 wide at 480 px, into
    <root>/haze_<tag>_<start>-<end>.png; prints the files and the frame numbers."""
    vid = os.path.join(root, 'rec_%s.mp4' % tag)
    h = haze_of(vid, os.path.join(root, 'runs_s', '%s.haze.json' % tag))
    if h is None:
        print('HAZE SHEET %s: no video' % tag)
        return 1
    if not h['after_var']:
        print('HAZE SHEET %s: no series after frame %d - no sheet' % (tag, HAZE_AFTER))
        return 0
    for a, b in h['after_var']:
        idx = sheet_frames(a, b, h['frames'])
        outp = os.path.join(root, 'haze_%s_%d-%d.png' % (tag, a, b))
        subprocess.run([ffmpeg, '-loglevel', 'error', '-y', '-i', vid, '-vf', sheet_vf(idx), '-frames:v', '1', '-vsync', '0',
                        outp])
        print('HAZE SHEET %s series %d-%d frames %s -> %s sha256 %s' % (
            tag, a, b, ','.join(str(i) for i in idx), outp, A.sha_file(outp) if os.path.isfile(outp) else 'MISSING'))
    return 0


def main(argv=None, root=LINK_DIR, pred=PRED_PATH):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--tag')
    ap.add_argument('--read-pi', action='store_true')
    ap.add_argument('--read-c5', action='store_true')
    ap.add_argument('--read-t2', action='store_true')
    ap.add_argument('--read-u', action='store_true')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--allowed')
    ap.add_argument('--plan')
    ap.add_argument('--form', choices=('c5', 'app'))
    ap.add_argument('--check-seal', action='store_true')
    ap.add_argument('--seal', default=None)
    ap.add_argument('--haze')
    ap.add_argument('--haze-sheet')
    ap.add_argument('--regress', action='store_true')
    ap.add_argument('--json-out', default=None)
    ap.add_argument('--seeds-check', action='store_true')
    a = ap.parse_args(argv)
    if a.seeds_check:
        sh, n = seeds_sha()
        print('seeds sha %s files %d (sealed %s) %s' % (sh, n, SEEDS_SHA, 'MATCH' if sh == SEEDS_SHA else 'DIFF'))
        return 0 if sh == SEEDS_SHA else 1
    if a.plan:
        if a.plan not in SPEC:
            print('usage: unknown tag %s' % a.plan)
            return 2
        form = a.form
        if form is None and SPEC[a.plan]['t2form']:
            form = read_c5(make_get(root, pred, False))[0]
        print(plan(resolved(SPEC[a.plan], form)))
        return 0
    if a.check_seal:
        ok, rows, bins = check_seal(a.seal or pred)
        for name, good, det in rows:
            print('%-4s %s %s' % ('OK' if good else 'BAD', name, det))
        print('SEAL: %s' % ('PASS' if ok else 'FAIL'))
        return 0 if ok else 1
    if a.regress:
        return 0 if regress() else 1
    if a.haze:
        h = haze_of(a.haze)
        print('HAZE %s: %s' % (a.haze, 'no video' if h is None else 'frames %d median %.4f low %d series %s; after %d %s '
                                                                  '(variant %s)' % (h['frames'], h['med'], h['low'], h['runs'],
                                                                                    HAZE_AFTER, h['after'], h['after_var'])))
        return 0 if h is not None else 1
    if a.haze_sheet:
        return haze_sheet(a.haze_sheet, root)
    get = make_get(root, pred)
    made = made_fn(root)
    if a.allowed:
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
        jp = a.json_out or os.path.join(root, 'runs_s', '%s.score.json' % a.tag)
        os.makedirs(os.path.dirname(os.path.abspath(jp)), exist_ok=True)
        json.dump(dict((k, v) for k, v in r.items()), open(jp, 'w', encoding='utf-8'), indent=1, default=list)
        return 0 if not r['fail'] else 1
    done = False
    if a.read_pi or a.summary:
        _, lines = read_pi(get)
        print('\n'.join(['READ repeat of integrity (item 355 (g))'] + lines))
        done = True
    if a.read_c5 or a.summary:
        _, _, lines = read_c5(get)
        print('\n'.join(['READ C5 (item 355 (d))'] + lines))
        done = True
    if a.read_t2 or a.summary:
        print('\n'.join(['READ T2 (item 355 (d), (zh))'] + read_t2(get)))
        done = True
    if a.read_u or a.summary:
        _, lines = read_u(get)
        print('\n'.join(['READ S-cat probe (item 355 (e))'] + lines))
        done = True
    if done:
        return 0
    print('usage: sc_s9.py --tag T | --read-pi | --read-c5 | --read-t2 | --read-u | --summary | --allowed T | --plan T | '
          '--check-seal | --haze V | --haze-sheet T | --regress')
    return 2


if __name__ == '__main__':
    sys.exit(main())
