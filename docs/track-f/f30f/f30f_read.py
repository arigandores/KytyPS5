"""Track F link F30f (HPP-711; ROADMAP s122 item 643 (d)(1)-(14), (g) RC2-RC7, item 644 (b)-(d) RC1-RC4): the reader of the rtskip
self-check series on the binary T 3bc7ada7 (F30d, worktree a1d1d863): per scene k three tags f30_<k>_c3 (KYTY_RT_SKIP=3, 150 s, no video)
-> f30_<k>_c4 (=4, 150 s, no video) -> f30_<k>_v (=2, 300 s, video).  Rows and members only; the reading of the series is F30g (HPP-712).
ASCII only.

    python f30f_read.py <tag> [--json <out>]                       one tag (files of C:/kyty/f287/f30f)
    python f30f_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, installed_before.txt, installed_after.txt, installed_sha.txt,
        level.txt, seal.md, bin.exe, v_read.json (c4 only: the read.json of the v tag of the scene)
    python f30f_read.py --table [--runs <dir>]                     the table and the scene rows over every runs/<tag>/read.json

TAGS  f30_<k>_<kind>[_r1.._r3]: k = s1..s9 (seal section 3), in (reserve intro_next); kind c3 / c4 / v, v2 (the reserve repeat of v at
      s6..s8, item 643 (d)(11)); _rN - repeat after an interference by the lead's item (item 643 (d)(12)).
WINDOW  from the line 'GuestOut: Level has started: <level>' (the first with the level of the scene) to the end of the log; PROCESS -
      every line of the log.  A FrameTrace-x line = a line starting 'FrameTrace-x: n='; its rts_* fields are the ' rts_<name>=<int>' tokens.
ADMISSION (any member NO - NOT_ADMITTED with the reason; the first failed harness member of an interference kind - INTERFERENCE):
  harness  json; launch_sha256 (sha of kyty_emulator.exe right before the launch) = T; json binary_sha256 = T; installed during the tag =
           T; installed before = after = FS10 abfded5e; prereg = seal sha256; env = the form exactly; gate text and schedule empty;
           --vulkan-validation false, --shader-validation false, no --rd, no --graphics-debug-dump true; -lvl <level> and the harness
           level file; hold option = form, outcome ok, hold_exit none, hold_s >= form; log; entry line; window events (minimized,
           Recovering Vulkan swapchain) 0 [interference]; signature 9177b426 and catalog variant_fixb26_fixb1b_fixf10_fixf19; GamePatch,
           DiagB32, TestLogStall 0; the summary 'LogAsync: full_waits=' once with all fields (absent - interference 'run').
  (D1)     exactly one 'RtSkip: mode <v>' with the knob of the tag and no 'RtSkip: mode' with another value.
  (D2)     'RtSkip: refused' lines 0 and process sum rts_refuse 0.
  (D3)     'Gate: rtskip=' lines none or all with the knob of the tag.
  (D4)     process sums rts_xthr = rts_acqw = 0.
  (D5)     FrameTrace-x lines in the window >= 0.95 x FrameTrace-draw lines in the window and >= 3000 (=2) / 1500 (=3, =4).
  (D6)     window sum rts_ovf = 0.
  (D7)     binary T and catalog: see D7_RULE (letter: the version string '-ga1d1d863' in the log; variant: launch_sha256 = T and exactly one
           log line 'Fork build arigandores/KytyPS5 a1d1d86' and the version string in the pinned copy of sha T).
  RC4      every FrameTrace-x line carries every field of REQ - else NOT_ADMITTED 'missing field' (not 0).
  parse    per FrameTrace-x line rts_chk = rts_pa, rts_chk_b = rts_pb (RC7: identity of the parse) and rts_bad_rx <= rts_bad_b <= rts_bad
           (item 644 (g)); sums rts_chk_b <= rts_chk <= rts_n, rts_bad_noreg <= rts_bad; MISMATCH lines <= min(40, process rts_bad).
  c4 only  RC1 (item 644 (b)): process rts_skip = 0 and rts_chk >= rts_chk_b >= 1; RC2 (a) (item 644 (v)): process rts_xb_meta =
           rts_xb_ser = 0 (with (D1) - 'RtSkip: mode 4' once, no mode 2 / 3); RC2 (b): for each of rts_xb_ids, rts_xb_live, rts_xb_bound,
           rts_xb_pass - when the process sum at the v tag of the scene is >= 100, the c4 process sum >= 1, else 'not checked' with the
           number; no read v tag yet - status WAITS_V (not admitted yet, the series does not stop); RC3 reconciliation (item 644 (g)):
           MISMATCH mode=4 lines = process rts_bad (<= 40) => rts_bad_rx = lines with bits & 0x030 and rts_bad_b = lines with bits &
           0x3f0 exactly; lines fewer (exhausted) => rts_bad_rx >= lines with bits & 0x030 and rts_bad_b >= lines with bits & 0x3f0.
MEMBERS (rows for F30g; no verdict):
  c3   (K) >= 1 line 'RtSkipVerify: MISMATCH ... mode=3' with bit 0x001 and process rts_bad >= 1;  (K') process rts_bad_noreg = 0 (else
       STOP);  race: process rts_race = 0 (else STOP, RC2).
  c4   K_B (item 643 (d)(5), 644 (g)): (i) process rts_bad_rx >= 1 - the reading; (ii) lines mode=4 with bits & 0x030 - reconciliation
       row; rts_bad_b at c4 - reference; race - reference.
  v    (C1) window rts_chk_b >= 10^6; (V) process rts_bad = 0 and 0 'RtSkipVerify:' lines (else, with (D1)-(D4), (D7) - the outcome
       640 (e)(4), STOP, RC3 of item 643 (g)); race: process rts_race = 0 (else STOP); (O): the entry is OLD (>= 90 % of the read 90-frame
       blocks of bda_scan >= 600, first 2 blocks skipped, >= 3 read blocks) and window rts_chk_b in OLD blocks >= 10^6.
  every tag, reference: kappa (window rts_chk_b / rts_n over the skip share of value 1 by level and by level x own mode, kref_f30f.tsv;
       outside [0.80; 1.25] - a row for the lead, RC6), rts_skip, FixB42 increments hit / applied / drawn over the window (per extent,
       FixB42 and FixB42Ext lines), window rts_lost (RC4 of item 643 (g)), death markers, video index and glitches (v).
STOP rows (item 643 (d)(11)): 'RtSkip: refused' line; (D4) != 0; (K') != 0 at c3; process rts_race > 0 at c3 / v; (V) != 0 at v with
  (D1)-(D4), (D7) met.
"""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/f30f'
SEAL_PATH = G + '/pred/f30f_seal.md'
KREF_PATH = G + '/kref_f30f.tsv'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_3bc7ada7.exe'
BIN_T = '3bc7ada7980a89fee30b17780f8dfbee0b3921332d81f1f63984d6252a811347'
BIN_FS10 = 'abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1906-ga1d1d863'
VERSION_LOG = b'-ga1d1d863'
FORK = b'version: Fork build arigandores/KytyPS5 '
FORK_T = 'a1d1d86'
D7_RULE = 'variant'   # item 649 (b): the triple decides; the letter of item 644 (d) is a reference row ('NO' at every tag)
S9_N_MIN = 1650      # item 649 (d): the frame of the window end at the tags of S9 (keys into the water, presents 1300-1650)
RX_FT = re.compile(rb'^FrameTrace: n=(\d+)')
RX_INPUT = re.compile(rb'InputScript: (?:press|release) \S+ at [0-9.]+ s \(present (\d+)\)')
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
KEYS_S9 = ('@1300:a/@45 @1380:w/@45 @1500:w/@96 @1650:h/@975 @2600:f/@1003 @3550:w/@18 @3600:d/@30 @3650:s/@31 @3700:a/@31 '
           '@3750:w/@49 @3800:w/@90 @3900:h/@966 @4850:f/@984 @5800:w/@17 @5830:d/@25 @5860:s/@25 @5890:a/@25 @5920:w/@25')
SCENES = {
    's1': ('underwater_aerial_garden', 300, None), 's2': ('hoover_beach', 300, None), 's3': ('mini_giants_garden', 300, None),
    's4': ('timestop_casino', 300, None), 's5': ('rotating_level_day_and_night', 300, None), 's6': ('sponge_dirty_bath', 300, None),
    's7': ('time_stopper_ghost_world', 300, None), 's8': ('big_hand_pirate_island', 300, None),
    's9': ('underwater_aerial_garden', 300, KEYS_S9), 'in': ('intro_next', 500, None)}
KNOB = {'c3': 3, 'c4': 4, 'v': 2, 'v2': 2}
HOLD = {'c3': 150, 'c4': 150, 'v': 300, 'v2': 300}
TAG_RX = re.compile(r'^f30_(s[1-9]|in)_(c3|c4|v|v2)(_r[1-3])?$')
X_MIN = {2: 3000, 3: 1500, 4: 1500}
X_SHARE = 0.95
C1_MIN = 1000000
O_MIN = 1000000
RC2_MIN = 100
KAPPA = (0.80, 1.25)
BLOCK = 90
BLK_SKIP = 2
MIN_BLOCKS = 3
OLD_SHARE = 0.9
LINES_MAX = 40
PRE_TOL = 1   # item 651 (b)(2): one event carried to a neighbour line (the flip publishes the counters one by one)
REQ = ('rts_n', 'rts_skip', 'rts_pa', 'rts_pb', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx', 'rts_race',
       'rts_refuse', 'rts_xthr', 'rts_acqw', 'rts_ovf', 'rts_lost', 'rts_xb_ids', 'rts_xb_live', 'rts_xb_meta', 'rts_xb_ser',
       'rts_xb_bound', 'rts_xb_pass')
LEGACY_NEW = ('rts_bad_b', 'rts_bad_rx')
XB_LIVE = ('rts_xb_ids', 'rts_xb_live', 'rts_xb_bound', 'rts_xb_pass')
VKLAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
RX_SUM = re.compile(rb'^LogAsync: full_waits=\d+ ')
RX_RTS = re.compile(rb' (rts_[a-z0-9_]+)=(\d+)')
RX_N = re.compile(rb'^FrameTrace-(?:x|draw): n=(\d+)')
RX_BDA = re.compile(rb' bda_scan=(\d+)')
RX_MODE = re.compile(rb'RtSkip: mode (\d+) ')
RX_GATE = re.compile(rb'Gate: rtskip=(\d+)')
RX_MM = re.compile(rb'RtSkipVerify: MISMATCH frame=(-?\d+) bits=0x([0-9a-fA-F]+) reg=(\d+) .*\bmode=(\d+)')
RX_B42 = re.compile(rb'FixB42(?:Ext)?: mode=(\d+) (?:extent=(\d+)x(\d+) )?hit=(\d+) applied=(\d+) drawn=(\d+)')
RX_B42_EXT = re.compile(rb' extent=(\d+)x(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
SUM_KEYS = ('full_waits', 'full_wait_us', 'stalls', 'stall_cut', 'lines', 'bytes', 'max_queued_bytes', 'sync_lines', 'drain_timeouts')


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def last_flag(cmd, flag):
    v = None
    for i, a in enumerate(cmd or []):
        if a == flag:
            v = cmd[i + 1] if i + 1 < len(cmd) else ''
    return v


def num(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def parts(tag):
    m = TAG_RX.match(tag)
    return m.group(1), m.group(2), m.group(3) or ''


def expected_env(scene, kind):
    lv, sd, keys = SCENES[scene]
    e = dict(KYTY_GUEST_ARGS='-lvl ' + lv, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1',
             KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_RT_SKIP=str(KNOB[kind]))
    if kind in ('v', 'v2'):
        e.update(KYTY_REC=None)
    if keys is not None:
        e.update(KYTY_KEYS=keys)
    return e


def env_diff(env, want):
    bad = []
    for key in sorted(set(env) | set(want)):
        if key not in env:
            bad.append('missing %s' % key)
        elif key not in want:
            bad.append('extra %s=%s' % (key, env[key]))
        elif want[key] is not None and env[key] != want[key]:
            bad.append('%s=%s (want %s)' % (key, env[key], want[key]))
    return bad


def new_sums():
    return dict((k, 0) for k in REQ)


def scan(path, level, legacy=False):
    """One pass over the log.  legacy=True (regression on the session 127 logs only, never a tag): the two F30d fields
    rts_bad_b / rts_bad_rx may be absent and count 0."""
    req = tuple(k for k in REQ if not (legacy and k in LEGACY_NEW))
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(entry_ln=None, first_guest_ln=None, modes=[], refused=0, gates=[], mm=[], mm_bad=0, verify=0, proc=new_sums(),
             win=new_sums(), x_lines=0, x_win=0, x_missing=0, x_missing_names=[], x_dup=0, x_prefixed=0, draw_win=0, draw_lines=0,
             bda_win=[], bda_missing=0, chkb_by_n={}, id_pa=0, id_pb=0, id_rx=0, ineq_lines=0, pre_viol=0, pre_first=None, pre_viol_rx=0, maxdev=dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0), ft_last_n=None, input_max=None, input_lines=0, b42=[], death=[], minimized=0,
             recovering=0, winev={}, sig=[], variant_dir=[], gamepatch=0, diagb32=0, stall_lines=0, fork=[], ver_log=0, summary=[],
             summary_bad=0, lines=0)
    lvl = ('GuestOut: Level has started: %s' % level).encode()
    ln = 0
    pre = dict(c=0, a=0, cb=0, b=0, rx=0, bb=0, bad=0)
    for line in fh:
        ln += 1
        after = r['entry_ln'] is not None
        if line.startswith(b'FrameTrace-x: n='):
            r['x_lines'] += 1
            if after:
                r['x_win'] += 1
            pos = line.find(b' rts_')
            got = {}
            dup = False
            if pos >= 0:
                for name, val in RX_RTS.findall(line, pos):
                    nm = name.decode()
                    if nm in got:
                        dup = True
                    got[nm] = int(val)
            if dup:
                r['x_dup'] += 1
            miss = [k for k in req if k not in got]
            for k in REQ:
                got.setdefault(k, 0)
            if miss:
                r['x_missing'] += 1
                if len(r['x_missing_names']) < 8:
                    r['x_missing_names'].append((ln, miss[:4]))
                continue
            for k in REQ:
                r['proc'][k] += got[k]
                if after:
                    r['win'][k] += got[k]
            pre['c'] += got['rts_chk']
            pre['a'] += got['rts_pa']
            pre['cb'] += got['rts_chk_b']
            pre['b'] += got['rts_pb']
            pre['rx'] += got['rts_bad_rx']
            pre['bb'] += got['rts_bad_b']
            pre['bad'] += got['rts_bad']
            md = r['maxdev']
            md['chk_pa'] = max(md['chk_pa'], abs(pre['c'] - pre['a']))
            md['chkb_pb'] = max(md['chkb_pb'], abs(pre['cb'] - pre['b']))
            md['rx_b'] = max(md['rx_b'], pre['rx'] - pre['bb'])
            md['b_bad'] = max(md['b_bad'], pre['bb'] - pre['bad'])
            if abs(pre['c'] - pre['a']) > PRE_TOL or abs(pre['cb'] - pre['b']) > PRE_TOL:
                r['pre_viol'] += 1
                if r['pre_first'] is None:
                    r['pre_first'] = ln
            if pre['rx'] > pre['bb'] + PRE_TOL or pre['bb'] > pre['bad'] + PRE_TOL:
                r['pre_viol_rx'] += 1
                if r['pre_first'] is None:
                    r['pre_first'] = ln
            if got['rts_chk'] != got['rts_pa']:
                r['id_pa'] += 1
            if got['rts_chk_b'] != got['rts_pb']:
                r['id_pb'] += 1
            if not (got['rts_bad_rx'] <= got['rts_bad_b'] <= got['rts_bad']):
                r['id_rx'] += 1
            if not (got['rts_chk_b'] <= got['rts_chk'] <= got['rts_n']) or got['rts_bad_noreg'] > got['rts_bad']:
                r['ineq_lines'] += 1
            if after:
                mn = RX_N.match(line)
                if mn:
                    n = int(mn.group(1))
                    r['chkb_by_n'][n] = r['chkb_by_n'].get(n, 0) + got['rts_chk_b']
            continue
        if line.startswith(b'FrameTrace-draw: n='):
            r['draw_lines'] += 1
            if after:
                r['draw_win'] += 1
                mn = RX_N.match(line)
                mb = RX_BDA.search(line)
                if mn and mb:
                    r['bda_win'].append((int(mn.group(1)), int(mb.group(1))))
                else:
                    r['bda_missing'] += 1
            continue
        if line.startswith(b'FrameTrace: n='):
            mf = RX_FT.match(line)
            if mf:
                r['ft_last_n'] = int(mf.group(1))
            continue
        if line.startswith(b'FrameTrace'):
            if b'FrameTrace-x:' in line[:16]:
                r['x_prefixed'] += 1
            continue
        if b'FrameTrace-x: n=' in line:
            r['x_prefixed'] += 1
        if line.startswith(b'DiagB32'):
            r['diagb32'] += 1
            continue
        if line.startswith(b'TestLogStall:'):
            r['stall_lines'] += 1
            continue
        if line.startswith(b'LogAsync:'):
            if RX_SUM.match(line):
                f = dict(tok.split('=', 1) for tok in line.decode('ascii', 'replace').strip().split(' ')[1:] if '=' in tok)
                if all(k in f for k in SUM_KEYS):
                    r['summary'].append(dict((k, num(f[k])) for k in SUM_KEYS))
                else:
                    r['summary_bad'] += 1
            continue
        if b'RtSkip' in line:
            if b'RtSkipVerify:' in line:
                r['verify'] += 1
                mm = RX_MM.search(line)
                if mm:
                    r['mm'].append(dict(frame=int(mm.group(1)), bits=int(mm.group(2), 16), reg=int(mm.group(3)), mode=int(mm.group(4)),
                                        ln=ln))
                else:
                    r['mm_bad'] += 1
                continue
            mo = RX_MODE.search(line)
            if mo:
                r['modes'].append((int(mo.group(1)), ln))
            if b'RtSkip: refused' in line:
                r['refused'] += 1
        if b'InputScript:' in line:
            mi = RX_INPUT.search(line)
            if mi:
                r['input_lines'] += 1
                r['input_max'] = max(r['input_max'] or 0, int(mi.group(1)))
        mg = RX_GATE.search(line)
        if mg:
            r['gates'].append((int(mg.group(1)), ln))
        if b'FixB42' in line:
            mb = RX_B42.search(line)
            if mb:
                if mb.group(2) is not None:
                    ext = (int(mb.group(2)), int(mb.group(3)))
                else:
                    me = RX_B42_EXT.search(line)
                    ext = (int(me.group(1)), int(me.group(2))) if me else (0, 0)
                r['b42'].append(dict(ext=ext, hit=int(mb.group(4)), applied=int(mb.group(5)), drawn=int(mb.group(6)), ln=ln,
                                     mode=int(mb.group(1))))
        if r['entry_ln'] is None and line.rstrip(b'\r\n').endswith(lvl):
            r['entry_ln'] = ln
        if r['first_guest_ln'] is None and b'GuestOut' in line:
            r['first_guest_ln'] = ln
        if line.startswith(b'GamePatch:'):
            r['gamepatch'] += 1
        if FORK in line and len(r['fork']) < 4:
            r['fork'].append(line.split(FORK, 1)[1].strip().decode('ascii', 'replace')[:40])
        if VERSION_LOG in line:
            r['ver_log'] += 1
        if line.startswith(b'ShaderSeed: compatibility=') and len(r['sig']) < 4:
            mm = SEED.search(line)
            r['sig'].append(mm.group(1).decode('ascii') if mm else '?')
        if line.startswith(b'Shader translation cache: ') and len(r['variant_dir']) < 4:
            r['variant_dir'].append(line.decode('ascii', 'replace').strip().replace('\\', '/').rsplit('/', 1)[-1])
        for dm in DEATH:
            if dm in line and len(r['death']) < 20:
                r['death'].append(dm.decode())
        if b'Recovering Vulkan swapchain' in line:
            r['recovering'] += 1
        mw = RX_WIN.search(line)
        if mw:
            k = mw.group(1).decode()
            r['winev'][k] = r['winev'].get(k, 0) + 1
            if k == 'minimized':
                r['minimized'] += 1
    r['lines'] = ln
    fh.close()
    return r


def b42_window(x):
    """Per extent: max hit / applied / drawn at or before the entry line (baseline, 0 if none) and over the log; increments summed."""
    ent = x['entry_ln']
    base, fin = {}, {}
    for b in x['b42']:
        for d in ([fin] + ([base] if ent is not None and b['ln'] <= ent else [])):
            cur = d.setdefault(b['ext'], dict(hit=0, applied=0, drawn=0))
            for k in ('hit', 'applied', 'drawn'):
                cur[k] = max(cur[k], b[k])
    inc = dict(hit=0, applied=0, drawn=0)
    per = {}
    for ext, f in fin.items():
        bb = base.get(ext, dict(hit=0, applied=0, drawn=0))
        per['%dx%d' % ext] = dict((k, f[k] - bb[k]) for k in inc)
        for k in inc:
            inc[k] += f[k] - bb[k]
    return dict(lines=len(x['b42']), inc=inc, per_extent=per, modes=sorted(set(b['mode'] for b in x['b42'])))


def bda_blocks(x):
    """90-frame blocks of the window FrameTrace-draw lines: [(mean bda_scan, [n...])]; a last partial block of >= 30 frames kept."""
    out = []
    cur = []
    for n, v in x['bda_win']:
        cur.append((n, v))
        if len(cur) == BLOCK:
            out.append((sum(v for _, v in cur) / BLOCK, [n for n, _ in cur]))
            cur = []
    if len(cur) >= BLOCK // 3:
        out.append((sum(v for _, v in cur) / len(cur), [n for n, _ in cur]))
    return out


def mode_member(x):
    blocks = bda_blocks(x)
    rb = blocks[BLK_SKIP:]
    if len(rb) < MIN_BLOCKS:
        mode = 'SHORT'
    elif sum(b >= 600 for b, _ in rb) >= OLD_SHARE * len(rb):
        mode = 'OLD'
    elif sum(b <= 300 for b, _ in rb) >= OLD_SHARE * len(rb):
        mode = 'NEW'
    else:
        mode = 'MIXED'
    old_n = set()
    for b, ns in rb:
        if b >= 600:
            old_n.update(ns)
    chkb_old = sum(v for n, v in x['chkb_by_n'].items() if n in old_n)
    return dict(mode=mode, blocks=len(blocks), read_blocks=len(rb), old_blocks=sum(b >= 600 for b, _ in rb),
                new_blocks=sum(b <= 300 for b, _ in rb), mean_read=(round(sum(b for b, _ in rb) / len(rb), 1) if rb else None),
                chkb_old=chkb_old, bda_missing=x['bda_missing'])


_BIN_MEMO = {}


def bin_has_version(path):
    """True when the file has the sha256 of T and carries VERSION; memo per (path, size, mtime) - one read per process."""
    st = os.stat(path)
    key = (os.path.abspath(path), st.st_size, st.st_mtime)
    if key not in _BIN_MEMO:
        data = open(path, 'rb').read()
        _BIN_MEMO[key] = (hashlib.sha256(data).hexdigest(), VERSION in data)
    h, v = _BIN_MEMO[key]
    return h == BIN_T and v


def kref(path):
    t = {}
    if path and os.path.exists(path):
        for line in open(path, encoding='ascii').read().splitlines()[1:]:
            f = line.split('\t')
            if len(f) == 7:
                try:
                    t[(f[0], f[1])] = float(f[6])
                except ValueError:
                    pass
    return t


def kappa_rows(x, level, mode, table):
    w = x['win']
    share2 = (w['rts_chk_b'] / w['rts_n']) if w['rts_n'] else None
    out = {}
    for key in ('ALL', mode):
        ref = table.get((level, key))
        k = (share2 / ref) if (share2 is not None and ref) else None
        out[key] = dict(ref=ref, kappa=(round(k, 4) if k is not None else None),
                        inside=(k is not None and KAPPA[0] <= k <= KAPPA[1]))
    return dict(share_v2=(round(share2, 4) if share2 is not None else None), by=out)


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'glitch', 'installed_sha', 'level')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        lg = os.path.join(base, 'log.txt')
        p.update(log=lg if os.path.exists(lg) or not os.path.exists(lg + '.xz') else lg + '.xz', stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), bin=(text(os.path.join(base, 'bin.txt')) or '').strip() or os.path.join(base, 'bin.exe'),
                 vread=os.path.join(base, 'v_read.json'), kref=os.path.join(base, 'kref.tsv'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    scene, kind, rep = parts(tag)
    vread = None
    if kind == 'c4':
        for vt in ['f30_%s_v%s' % (scene, s) for s in ('', '_r1', '_r2', '_r3')]:
            js = os.path.join(G, 'runs', vt, 'read.json')
            if os.path.exists(js):
                try:
                    if json.load(open(js, encoding='utf-8')).get('admitted'):
                        vread = js
                        break
                except ValueError:
                    pass
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH, bin=BIN_PATH, vread=vread, kref=KREF_PATH)
    return p


def stdout_death(path):
    out = []
    if path and os.path.exists(path):
        data = open(path, 'rb').read()
        for dm in DEATH:
            if dm in data:
                out.append(dm.decode())
    return out


def read_tag(tag, p, legacy=False):
    scene, kind, rep = parts(tag)
    level, sd, keys = SCENES[scene]
    knob = KNOB[kind]
    res = dict(tag=tag, scene=scene, kind=kind, knob=knob, level=level, reader_sha256=sha_file(os.path.abspath(__file__)), d7_rule=D7_RULE)
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    att = ((run or {}).get('attempts') or [{}])[-1]
    jbin = (run or {}).get('binary_sha256')
    lsha = att.get('launch_sha256')
    res['binary_sha256'] = jbin
    res['launch_sha256'] = lsha
    inst_b = (text(p['installed_before']) or '').strip() or None
    inst_a = (text(p['installed_after']) or '').strip() or None
    inst_t = (text(p['installed_sha']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    hlev = (text(p['level']) or '').strip() or None
    ga = (run or {}).get('guest_args') or ''
    have_log = os.path.exists(p['log'])
    x = scan(p['log'], level, legacy) if have_log else None
    res['legacy'] = legacy
    ebad = env_diff(dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_'))), expected_env(scene, kind))
    hold = HOLD[kind]
    sdth = stdout_death(p['stdout'])
    bin_ver = None
    if p['bin'] and os.path.exists(p['bin']):
        bin_ver = bin_has_version(p['bin'])
    try:
        win_s = round(float(att.get('stable_s')) - float(att.get('started_s')) + float(att.get('hold_s')), 1)
    except (TypeError, ValueError):
        win_s = None
    lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None and win_s is not None and win_s >= hold
    X = x or {}
    harness = [
        ('tag json present', run is not None, 'harness'),
        ('json binary_sha256 = T 3bc7ada7 (%s)' % (jbin or '-')[:16], jbin == BIN_T, 'harness'),
        ('installed during the tag = T 3bc7ada7 (%s)' % (inst_t or '-')[:16], inst_t == BIN_T, 'harness'),
        ('installed before = after = FS10 abfded5e (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_FS10 and inst_a == BIN_FS10, 'harness'),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha,
         'harness'),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad, 'harness'),
        ('gate text and schedule empty - no rtskip, no census gate (%r / %r)' % (((run or {}).get('gates') or '')[:40],
                                                                            ((run or {}).get('schedule') or '')[:40]),
         run is not None and not (run.get('gates') or '').strip() and not (run.get('schedule') or '').strip(), 'harness'),
        ('last --vulkan-validation false (%s)' % last_flag(cmd, '--vulkan-validation'), last_flag(cmd, '--vulkan-validation') == 'false',
         'harness'),
        ('last --shader-validation false (%s)' % last_flag(cmd, '--shader-validation'), last_flag(cmd, '--shader-validation') == 'false',
         'harness'),
        ('no --rd, no --graphics-debug-dump true (%s)' % last_flag(cmd, '--graphics-debug-dump'),
         run is not None and '--rd' not in cmd and last_flag(cmd, '--graphics-debug-dump') in (None, 'false'), 'harness'),
        ('guest args -lvl %s (%s; harness %s)' % (level, ga, hlev), ga == '-lvl ' + level and hlev == level, 'harness'),
        ('hold option %d s (%s)' % (hold, (run or {}).get('hold_s')), (run or {}).get('hold_s') == hold, 'harness'),
        ('window from the entry line >= %d s and the process alive at its end (item 649 (e)): stable_s %s - started_s %s + hold_s %s = %s; '
         'outcome %s, hold_exit %s' % (hold, att.get('stable_s'), att.get('started_s'), att.get('hold_s'), win_s, att.get('outcome'),
                                       att.get('hold_exit')), lived, 'harness'),
        ('log present', have_log, 'harness'),
        ('entry line present (%s)' % X.get('entry_ln'), x is not None and x['entry_ln'] is not None, 'harness'),
        ('window events: minimized %s, Recovering Vulkan swapchain %s (all %s)' % (X.get('minimized'), X.get('recovering'), X.get('winev')),
         x is not None and x['minimized'] == 0 and x['recovering'] == 0, 'interference' if x is not None else 'harness'),
        ('signature 9177b426 and catalog %s (D7) (%s / %s)' % (VARIANT_DIR, [z[:8] for z in X.get('sig') or []], X.get('variant_dir')),
         x is not None and x['sig'] == [SIG] and x['variant_dir'] == [VARIANT_DIR], 'harness'),
        ('no GamePatch:, DiagB32, TestLogStall lines (%s / %s / %s)' % (X.get('gamepatch'), X.get('diagb32'), X.get('stall_lines')),
         x is not None and x['gamepatch'] == 0 and x['diagb32'] == 0 and x['stall_lines'] == 0, 'harness'),
    ]
    if x is not None:
        ok = len(x['summary']) == 1 and x['summary_bad'] == 0
        harness.append(('summary LogAsync: full_waits= once, all fields (%d, bad %d) - absent: killed (item 615 (b)(6))' % (
            len(x['summary']), x['summary_bad']), ok, 'interference' if not x['summary'] else 'harness'))
    d = []
    stop = []
    if x is not None:
        P, W = x['proc'], x['win']
        mv = [v for v, l in x['modes']]
        d1 = mv.count(knob) == 1 and all(v == knob for v in mv)
        d2 = x['refused'] == 0 and P['rts_refuse'] == 0
        d3 = all(v == knob for v, l in x['gates'])
        d4 = P['rts_xthr'] == 0 and P['rts_acqw'] == 0
        d5 = x['x_win'] >= X_SHARE * x['draw_win'] and x['x_win'] >= X_MIN[knob]
        d6 = W['rts_ovf'] == 0
        fork_ok = len(x['fork']) == 1 and x['fork'][0] == FORK_T
        d7_letter = x['ver_log'] >= 1
        d7_variant = lsha == BIN_T and jbin == lsha and fork_ok and bin_ver is True
        d7 = d7_letter if D7_RULE == 'letter' else d7_variant
        d += [('(D1) exactly one RtSkip: mode %d, no other value (%s)' % (knob, x['modes'][:4]), d1),
              ('(D2) RtSkip: refused lines %d, process rts_refuse %d' % (x['refused'], P['rts_refuse']), d2),
              ('(D3) Gate: rtskip= lines none or all %d (%s)' % (knob, x['gates'][:4]), d3),
              ('(D4) process rts_xthr %d, rts_acqw %d' % (P['rts_xthr'], P['rts_acqw']), d4),
              ('(D5) FrameTrace-x in the window %d >= 0.95 x FrameTrace-draw %d and >= %d' % (x['x_win'], x['draw_win'], X_MIN[knob]), d5),
              ('(D6) window rts_ovf %d' % W['rts_ovf'], d6),
              ('(D7) item 649 (b): launch_sha256 %s = T, binary_sha256 = launch_sha256 (%s), one log line version: Fork build ... a1d1d86 '
               '(%s), version string in the pinned copy of sha T (%s) - %s; letter of item 644 (d) (reference): version string -ga1d1d863 '
               'in the log (%d lines) %s' % ((lsha or '-')[:16], (jbin or '-')[:16], x['fork'], bin_ver, 'YES' if d7_variant else 'NO',
                                             x['ver_log'], 'YES' if d7_letter else 'NO'), d7),
              ('RC4 every FrameTrace-x line carries every field of REQ (lines %d, missing %d %s) - else missing field' % (
                  x['x_lines'], x['x_missing'], x['x_missing_names'][:3]), x['x_missing'] == 0 and x['x_lines'] > 0)]
        nmm = len(x['mm'])
        ident_ok = (P['rts_chk'] == P['rts_pa'] and P['rts_chk_b'] == P['rts_pb'] and P['rts_bad_rx'] <= P['rts_bad_b'] <= P['rts_bad']
                    and x['pre_viol'] == 0 and x['pre_viol_rx'] == 0)
        if not ident_ok:
            stop.append('parse identity of item 651 (b) broken (sums chk %d / pa %d, chk_b %d / pb %d, rx %d <= b %d <= bad %d; prefix '
                        'violations %d / %d; max deviation %s) - NOT_ADMITTED and series stop, item 651 (v)' % (
                            P['rts_chk'], P['rts_pa'], P['rts_chk_b'], P['rts_pb'], P['rts_bad_rx'], P['rts_bad_b'], P['rts_bad'],
                            x['pre_viol'], x['pre_viol_rx'], x['maxdev']))
        parse_ok = (ident_ok and P['rts_chk_b'] <= P['rts_chk'] <= P['rts_n']
                    and P['rts_bad_noreg'] <= P['rts_bad']
                    and x['verify'] <= min(LINES_MAX, P['rts_bad']) and x['mm_bad'] == 0 and x['x_dup'] == 0)
        d.append(('parse [identity of the parse, RC7]: process rts_chk %d = rts_pa %d, rts_chk_b %d = rts_pb %d, rts_bad_rx %d <= rts_bad_b '
                  '%d <= rts_bad %d; prefix sums within %d event at every line (chk/pa, chk_b/pb %d; rx/b/bad %d; first line %s); chk_b <= chk <= n %d, '
                  'noreg %d <= bad; RtSkipVerify lines %d <= min(40, bad); unparsable %d; duplicate fields %d; letter rows (per line, '
                  'reference - the flip tears one event): chk!=pa %d, chk_b!=pb %d, rx<=b<=bad broken %d; max prefix deviation %s' % (
                      P['rts_chk'], P['rts_pa'], P['rts_chk_b'], P['rts_pb'], P['rts_bad_rx'], P['rts_bad_b'], P['rts_bad'], PRE_TOL,
                      x['pre_viol'], x['pre_viol_rx'], x['pre_first'], P['rts_n'], P['rts_bad_noreg'], x['verify'], x['mm_bad'], x['x_dup'], x['id_pa'],
                      x['id_pb'], x['id_rx'], json.dumps(x['maxdev'], sort_keys=True)), parse_ok))
        if scene == 's9':
            d.append(('S9 window end: last FrameTrace n %s >= %d (item 649 (d); presents of the InputScript lines - max %s, lines %d)' % (
                x['ft_last_n'], S9_N_MIN, x['input_max'], x['input_lines']), (x['ft_last_n'] or 0) >= S9_N_MIN))
        if kind == 'c4':
            rc1 = P['rts_skip'] == 0 and P['rts_chk'] >= P['rts_chk_b'] >= 1
            d.append(('RC1 c4: process rts_skip %d = 0 and rts_chk %d >= rts_chk_b %d >= 1' % (P['rts_skip'], P['rts_chk'], P['rts_chk_b']),
                      rc1))
            d.append(('RC2 (a) c4: armed - RtSkip: mode 4 once, no mode 2 / 3 (D1) and process rts_xb_meta %d = rts_xb_ser %d = 0' % (
                P['rts_xb_meta'], P['rts_xb_ser']), d1 and P['rts_xb_meta'] == 0 and P['rts_xb_ser'] == 0))
            m4 = [m for m in x['mm'] if m['mode'] == 4]
            rx_l = sum(1 for m in m4 if m['bits'] & 0x030)
            b_l = sum(1 for m in m4 if m['bits'] & 0x3f0)
            exact = len(m4) == P['rts_bad'] and P['rts_bad'] <= LINES_MAX
            if exact:
                rc3 = P['rts_bad_rx'] == rx_l and P['rts_bad_b'] == b_l
            else:
                rc3 = P['rts_bad_rx'] >= rx_l and P['rts_bad_b'] >= b_l
            res['kb'] = dict(i=P['rts_bad_rx'], ii=rx_l, lines_mode4=len(m4), lines_b=b_l, bad=P['rts_bad'], bad_b=P['rts_bad_b'],
                             exact=exact)
            if exact and not rc3:
                stop.append('RC3 reconciliation failed with the lines not exhausted - item 649 (v)')
            d.append(('RC3 reconciliation c4 (%s): lines mode=4 %d, process rts_bad %d; rts_bad_rx %d vs lines bits&0x030 %d; rts_bad_b %d vs '
                      'lines bits&0x3f0 %d' % ('exact' if exact else 'lines exhausted - >=', len(m4), P['rts_bad'], P['rts_bad_rx'], rx_l,
                                               P['rts_bad_b'], b_l), rc3))
            vr = json.load(open(p['vread'], encoding='utf-8')) if p.get('vread') and os.path.exists(p['vread']) else None
            vs = (vr or {}).get('proc')
            rows = []
            rc2b = True
            if vs is None:
                res['waits_v'] = True
            else:
                res['waits_v'] = False
                for k in XB_LIVE:
                    if vs.get(k) is None:
                        rows.append('%s v missing' % k)
                        rc2b = False
                    elif vs[k] >= RC2_MIN:
                        okk = P[k] >= 1
                        rc2b = rc2b and okk
                        rows.append('%s v %d c4 %d %s' % (k, vs[k], P[k], 'ok' if okk else 'NO'))
                    else:
                        rows.append('%s v %d < %d - not checked (c4 %d)' % (k, vs[k], RC2_MIN, P[k]))
            res['rc2b'] = rows
            if vs is not None:
                d.append(('RC2 (b) c4: other PB reasons alive vs v of the scene (%s; threshold %d): %s' % ((vr or {}).get('tag'), RC2_MIN,
                                                                                                         '; '.join(rows)), rc2b))
        if x['refused'] > 0:
            stop.append('RtSkip: refused line (%d)' % x['refused'])
        if not d4:
            stop.append('(D4) != 0: rts_xthr %d rts_acqw %d' % (P['rts_xthr'], P['rts_acqw']))
    adm_rows = [(a, bool(b)) for a, b, k in harness] + [(a, bool(b)) for a, b in d]
    res['admission'] = [[a, b] for a, b in adm_rows]
    failed_h = [(a, k) for a, b, k in harness if not b]
    failed_d = [a for a, b in d if not b]
    interference = [a for a, k in failed_h if k == 'interference']
    binary_bad = [a for a in failed_d if a.startswith(('RC4 ', '(D7) '))]
    if binary_bad:
        status = 'NOT_ADMITTED'   # a wrong binary or a lost field is not a run disturbance (item 644 (d))
    elif interference:
        status = 'INTERFERENCE'
    elif failed_h or failed_d:
        status = 'NOT_ADMITTED'
    elif kind == 'c4' and res.get('waits_v'):
        status = 'WAITS_V'
    else:
        status = 'ADMITTED'
    res['status'] = status
    res['admitted'] = status == 'ADMITTED'
    res['why'] = None if status in ('ADMITTED', 'WAITS_V') else (binary_bad + [a for a, k in failed_h] + failed_d)[:4]
    idx_n = None
    if p.get('idx') and os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as fi:
            idx_n = sum(1 for _ in fi)
    gl = None
    gt = text(p['glitch'])
    if gt:
        mg = RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    res['members'] = None
    res['ref'] = dict(outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'), stable_s=att.get('stable_s'),
                      lines=X.get('lines'), death=(X.get('death') or []) + sdth, video_index=idx_n, glitches=gl, fork=X.get('fork'),
                      x_prefixed=X.get('x_prefixed'), ineq_lines=X.get('ineq_lines'))
    if x is not None:
        P, W = x['proc'], x['win']
        res['proc'] = dict(P)
        res['win'] = dict(W)
        res['verify_lines'] = x['verify']
        res['d5'] = [x['x_win'], x['draw_win']]
        res['mm_bits'] = sorted(set('0x%03x' % m['bits'] for m in x['mm']))
        md = mode_member(x)
        res['bda'] = md
        res['kappa'] = kappa_rows(x, level, md['mode'], kref(p['kref']))
        res['b42'] = b42_window(x)
        m = []
        dset_ok = all(b for a, b in d[:4]) and d[6][1]   # (D1)-(D4), (D7)
        if kind == 'c3':
            k_lines = [mm for mm in x['mm'] if mm['mode'] == 3 and mm['bits'] & 0x001]
            m += [('(K) >= 1 line MISMATCH mode=3 with bit 0x001 (%d) and process rts_bad %d >= 1' % (len(k_lines), P['rts_bad']),
                   bool(k_lines) and P['rts_bad'] >= 1),
                  ("(K') process rts_bad_noreg %d = 0" % P['rts_bad_noreg'], P['rts_bad_noreg'] == 0),
                  ('race: process rts_race %d = 0 (RC2)' % P['rts_race'], P['rts_race'] == 0)]
            if P['rts_bad_noreg'] > 0:
                stop.append("(K') != 0 at c3: rts_bad_noreg %d" % P['rts_bad_noreg'])
            if P['rts_race'] > 0:
                stop.append('rts_race %d > 0 at c3 (RC2)' % P['rts_race'])
        elif kind == 'c4':
            m += [('K_B (i) process rts_bad_rx %d >= 1 - the reading (item 643 (d)(5), 644 (g))' % P['rts_bad_rx'], P['rts_bad_rx'] >= 1),
                  ('K_B (ii) lines MISMATCH mode=4 with bits & 0x030: %d - reconciliation row, not a gate' % res['kb']['ii'],
                   res['kb']['ii'] >= 1)]
        else:
            o_ok = md['mode'] == 'OLD' and md['chkb_old'] >= O_MIN
            m += [('(C1) window rts_chk_b %d >= 10^6' % W['rts_chk_b'], W['rts_chk_b'] >= C1_MIN),
                  ('(V) process rts_bad %d = 0 and RtSkipVerify lines %d = 0' % (P['rts_bad'], x['verify']), P['rts_bad'] == 0 and x['verify'] == 0),
                  ('race: process rts_race %d = 0 (RC2)' % P['rts_race'], P['rts_race'] == 0),
                  ('(O) entry %s (read blocks %d, OLD %d, NEW %d, mean %s) and window rts_chk_b in OLD blocks %d >= 10^6' % (
                      md['mode'], md['read_blocks'], md['old_blocks'], md['new_blocks'], md['mean_read'], md['chkb_old']), o_ok)]
            if P['rts_race'] > 0:
                stop.append('rts_race %d > 0 at v (RC2)' % P['rts_race'])
            if (P['rts_bad'] > 0 or x['verify'] > 0) and dset_ok:
                stop.append('(V) != 0 at v with (D1)-(D4), (D7) met: rts_bad %d, RtSkipVerify lines %d - outcome 640 (e)(4) (RC3)' % (
                    P['rts_bad'], x['verify']))
        res['members'] = [[a, bool(b)] for a, b in m]
    res['stop'] = stop
    return res


def rows_out(res):
    out = ['tag %s (scene %s, kind %s, knob %d, level %s)  reader sha256 %s' % (res['tag'], res['scene'], res['kind'], res['knob'],
                                                                                 res['level'], res['reader_sha256'])]
    out.append('  STATUS %s%s' % (res['status'], '' if not res['why'] else ' - %s' % res['why']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    out.append('  launch_sha256 %s; binary_sha256 %s' % (res['launch_sha256'], res['binary_sha256']))
    if res['members'] is not None:
        out.append('  MEMBERS %s' % res['kind'])
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
    if res.get('proc') is not None:
        keys = ('rts_n', 'rts_skip', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx', 'rts_race', 'rts_lost')
        out.append('  PROCESS %s' % ' '.join('%s=%d' % (k, res['proc'][k]) for k in keys))
        out.append('  WINDOW  %s' % ' '.join('%s=%d' % (k, res['win'][k]) for k in keys))
        out.append('  XB process %s' % ' '.join('%s=%d' % (k, res['proc'][k]) for k in ('rts_xb_ids', 'rts_xb_live', 'rts_xb_meta',
                                                                                         'rts_xb_ser', 'rts_xb_bound', 'rts_xb_pass')))
        out.append('  RtSkipVerify lines %d, bits %s' % (res['verify_lines'], res['mm_bits']))
        out.append('  RC1 reference: process rts_skip %d (0 at 2-4), rts_chk %d >= rts_chk_b %d' % (
            res['proc']['rts_skip'], res['proc']['rts_chk'], res['proc']['rts_chk_b']))
        out.append('  BDA %s' % json.dumps(res['bda'], sort_keys=True))
        out.append('  KAPPA (reference, RC6; [0.80; 1.25]) %s' % json.dumps(res['kappa'], sort_keys=True))
        out.append('  FIXB42 window increments (RC4 of item 643 (g)) %s; window rts_lost %d' % (
            json.dumps(res['b42'], sort_keys=True)[:600], res['win']['rts_lost']))
    if res.get('kb') is not None:
        out.append('  K_B %s' % json.dumps(res['kb'], sort_keys=True))
    out.append('  REFERENCE %s' % json.dumps(res['ref'], sort_keys=True))
    out.append('  STOP %s' % ('none' if not res['stop'] else '; '.join(res['stop'])))
    return out


def scene_rows(reads):
    """reads: {tag: read.json} -> rows per scene for F30g (counts of item 643 (d)(9)-(10); not a verdict)."""
    def first(scene, kinds):
        for kd in kinds:
            for rep in ('', '_r1', '_r2', '_r3'):
                r = reads.get('f30_%s_%s%s' % (scene, kd, rep))
                if r is not None and r.get('status') == 'ADMITTED':
                    return r
        return None
    out = []
    counted = []
    for sc in sorted(SCENES):
        c3, c4 = first(sc, ['c3']), first(sc, ['c4'])
        vs = [first(sc, ['v']), first(sc, ['v2'])]
        def mem(r, i):
            return r is not None and r.get('members') is not None and r['members'][i][1]
        k_ok = mem(c3, 0)
        kb = mem(c4, 0)
        v_ok = [v for v in vs if v is not None and mem(v, 0) and mem(v, 1)]
        cnt = bool(k_ok and v_ok)
        old = any(mem(v, 3) for v in v_ok)
        a42 = sum(((v.get('b42') or {}).get('inc') or {}).get('applied', 0) for v in v_ok)
        if cnt:
            counted.append((sc, kb, old))
        out.append('%s %s: c3 %s K %s | c4 %s K_B(i) %s | v %s counted %s OLD %s | FixB42 applied in counted v %d' % (
            sc, SCENES[sc][0], (c3 or {}).get('status', '-'), k_ok, (c4 or {}).get('status', '-'),
            kb if c4 is not None else 'not checked (no admitted c4, item 649 (v))',
            [(v or {}).get('tag') for v in vs if v], cnt, old, a42))
    n = len(counted)
    nkb = sum(1 for s, kb, o in counted if kb)
    out.append('counted %d of 9 (S1 %s); with live K_B %d (S1 or S9 %s); OLD with live K_B %d, OLD %d - rows for F30g by item 643 (d)(9)-(10)' % (
        n, any(s == 's1' for s, kb, o in counted), nkb, any(s in ('s1', 's9') and kb for s, kb, o in counted),
        sum(1 for s, kb, o in counted if kb and o), sum(1 for s, kb, o in counted if o)))
    return out


def table(rd):
    out = ['| tag | status | knob | launch sha | (D5) x/draw | proc rts_bad | rts_bad_rx | race | win rts_chk_b | mode | OLD chk_b | stop |',
           '|' + '---|' * 12]
    reads = {}
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                reads[t] = r
                pr = r.get('proc') or {}
                wn = r.get('win') or {}
                bd = r.get('bda') or {}
                out.append('| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                    t, r['status'], r['knob'], (r.get('launch_sha256') or '-')[:8], '%s/%s' % tuple(r.get('d5') or ['-', '-']), pr.get('rts_bad', '-'), pr.get('rts_bad_rx', '-'),
                    pr.get('rts_race', '-'), wn.get('rts_chk_b', '-'), bd.get('mode', '-'), bd.get('chkb_old', '-'),
                    '; '.join(r.get('stop') or []) or '-'))
    out += [''] + scene_rows(reads)
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader f30f_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        if not TAG_RX.match(tag):
            print('usage: f30f_read.py <tag> | --dir D --tag T | --table')
            return 2
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        if not TAG_RX.match(tag):
            print('usage: f30f_read.py <tag> | --dir D --tag T | --table')
            return 2
        p = paths(tag)
    res = read_tag(tag, p, '--legacy-fields' in argv)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
