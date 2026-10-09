"""Track F link F30m (HPP-723; ROADMAP s122 item 655 (e)(1)-(5), (zh); item 658 (b) RC1-RC4 of F30l, (v) Q1): the reader of the series
on the binary T2 bba692c6 (F30k, worktree 6fbdcf67 = T a1d1d863 + 11236f5a): part (epsilon) - one tag f30_s<k>_c5 per scene s1..s9 of
F30f (KYTY_RT_SKIP=5, 150 s, no video); part (gamma) - cymbal_party_land: f30_cy_v (=2, 300 s, video; the admission member (gamma)),
then f30_cy_c3 (=3, 150 s) -> f30_cy_c4 (=4, 150 s).  Port of C:/kyty/f287/f30f/f30f_read.py (F30f, HPP-711).  Rows and members only;
the reading of the series is F30n (HPP-724) by item 655 (zh).  ASCII only.

    python f30m_read.py <tag> [--json <out>]                       one tag (files of C:/kyty/f287/f30m)
    python f30m_read.py --dir <fixture dir> --tag <tag> [--json <out>] [--legacy-fields]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, installed_before.txt, installed_after.txt, installed_sha.txt,
        level.txt, seal.md, bin.exe (or bin.txt with a path), v_read.json (cy_c4 only: the read.json of f30_cy_v), kref.tsv
    python f30m_read.py --table [--runs <dir>]                     the table and the scene rows over every runs/<tag>/read.json

TAGS  f30_s<k>_c5 (k = 1..9, scenes of F30f, s9 - Sky Garden with the water keys of FS3c); f30_cy_v / f30_cy_c3 / f30_cy_c4
      (cymbal_party_land); suffix _r1.._r3 - repeat after an interference by the lead's item (item 655 (e)(5)).
WINDOW  from the line 'GuestOut: Level has started: <level>' (the first with the level of the scene) to the end of the log; PROCESS -
      every line of the log.  A FrameTrace-x line = a line starting 'FrameTrace-x: n='; its fields are the ' rts_<name>=<int>' tokens,
      the name taken whole up to '=' (rts_bad_r is not a prefix match of rts_bad_rx).
ADMISSION (any member NO - NOT_ADMITTED with the reason; the first failed harness member of an interference kind - INTERFERENCE):
  harness  as F30f with: json binary_sha256 = T2; installed during the tag = T2; installed before = after = FS11 ea51ae80 (item 657, 658 (b)).
  (D1)-(D6) as F30f (item 643 (d)(3)); (D5) >= 3000 FrameTrace-x lines at =2, >= 1500 at =3 / =4 / =5 (item 655 (e)(2)).
  (D7) = RC3 of F30l (item 658 (b)): launch_sha256 (sha256 of the started file) = T2 bba692c6; binary_sha256 = launch_sha256; exactly one log
           line 'version: Fork build arigandores/KytyPS5 6fbdcf6'; the version string -1907-g6fbdcf67 in the pinned copy of sha T2; every log
           line carrying a version string 'KytyPS5-20..' carries exactly KytyPS5-2026-09-15-6a2987a-1907-g6fbdcf67 (none - vacuous).
  RC4 (F30f) / RC2 (F30l): every FrameTrace-x line carries every field of REQ incl. the 8 bit counters - else NOT_ADMITTED 'missing field'.
  parse    item 651 (b) as F30f with item 662 (v): the closing point T = the last FrameTrace-x line with every prefix deviation 0 and
           rx <= b <= bad without tolerance, at most CLOSE_MAX = 3 FrameTrace-x lines from the last one (none or farther - NO); at T
           rts_chk = rts_pa, rts_chk_b = rts_pb, rts_bad_rx <= rts_bad_b <= rts_bad exactly; prefix sums within PRE_TOL = 4 events at
           every line incl. the tail after T (item 659 (v), was 1); reference - lines with deviation >= 2 per pair, T, distance, tail.
  RC1 (F30l, every tag): at T rts_skip = 0 and rts_chk >= rts_chk_b = rts_pb >= 1 (item 662 (v)(3)); process rts_skip = 0 and
           rts_chk >= rts_chk_b (item 662 (b)).
  RC2 (F30l, every tag), process sums: exact - each of the 8 <= rts_bad_b <= rts_bad; rts_bad_r <= rts_bad_rx; rts_bad_xr, _xc, _xe <=
           rts_bad_rx; with 1 of tolerance - rts_bad_rx <= r + xr + xc + xe + 1; rts_bad_b <= sum of the 8 + 1.  Per line - reference.
  RC4 (F30l): at =5, =2, =4 (c5, cy_v, cy_c4) process rts_bad_noreg = rts_bad.
  c5       'PB item 6 dropped' (item 655 (e)(4)): process rts_xb_pass = 0.
  S9       last FrameTrace n >= 1650 (item 649 (d)).
  c5, c4   reconciliation (item 644 (g) extended to the bits): lines MISMATCH mode=<knob> = process rts_bad <= 40 (exact) => rts_bad_rx =
           lines with bits & 0x030, rts_bad_b = lines & 0x3f0, rts_bad_r = lines & 0x010, rts_bad_s / p / m / l = lines & 0x040 / 0x080 /
           0x100 / 0x200, each of xr / xc / xe <= lines & 0x020 <= xr + xc + xe; lines exhausted => every counter >= its lines.
  cy_c4    RC2 (a) of F30f (item 644 (v)): process rts_xb_meta = rts_xb_ser = 0; RC2 (b): for each of rts_xb_ids, rts_xb_live,
           rts_xb_bound, rts_xb_pass - when the process sum of the admitted f30_cy_v is >= 100, the cy_c4 process sum >= 1, else 'not
           checked'; no read f30_cy_v yet - status WAITS_V.
MEMBERS (rows for F30n; no verdict):
  c5, cy_c4  K_B'' (item 655 (zh)(1)): process rts_bad_r + rts_bad_xr + rts_bad_xc + rts_bad_xe + rts_bad_s + rts_bad_p + rts_bad_m >= 1;
           the live sources (item 658 (v)): R, X:xr, X:xc, X:xe, S, P, M - each its counter >= 1; L - reference; A-only reports - reference.
  cy_v     (gamma) admission (item 655 (e)(3)): process rts_xb_ser >= 100 - else (gamma) is not reachable on T2, cy_c3 / cy_c4 are not made;
           (C1) window rts_chk_b >= 10^6; (V) process rts_bad = 0 and 0 'RtSkipVerify:' lines; race process rts_race = 0; (O) as F30f.
  cy_c3    (K) >= 1 line MISMATCH mode=3 with bit 0x001 and process rts_bad >= 1; (K') process rts_bad_noreg = 0; race = 0.
STOP rows (item 643 (d)(11) as F30f; executor variant: a broken member of the instrument): 'RtSkip: refused'; (D4) != 0; (K') != 0 at
  cy_c3; rts_race > 0 at cy_c3 / cy_v; (V) != 0 at cy_v with (D1)-(D4), (D7) met (outcome 640 (e)(4), item 655 (zh)(2)); parse identity
  broken; reconciliation failed with the lines not exhausted; RC1 / RC2 / RC4 of F30l or 'PB item 6 dropped' broken; (D7) broken.
"""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/f30m'
SEAL_PATH = G + '/pred/f30m_seal.md'
KREF_PATH = G + '/kref_f30m.tsv'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_bba692c6.exe'
BIN_T = 'bba692c6c161afc0cd2bd3245cea574f7fb82e7a4aae4c065826898403107163'
BIN_INST = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'   # FS11, item 657
VERSION = b'KytyPS5-2026-09-15-6a2987a-1907-g6fbdcf67'
VERSION_ANY = re.compile(rb'KytyPS5-20\d\d-\d\d-\d\d-[0-9a-f]+-\d+-g[0-9a-f]+')
FORK = b'version: Fork build arigandores/KytyPS5 '
FORK_T = '6fbdcf6'
S9_N_MIN = 1650
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
    's9': ('underwater_aerial_garden', 300, KEYS_S9), 'cy': ('cymbal_party_land', 300, None)}
KNOB = {'c5': 5, 'v': 2, 'c3': 3, 'c4': 4}
HOLD = {'c5': 150, 'v': 300, 'c3': 150, 'c4': 150}
TAG_RX = re.compile(r'^f30_(?:(s[1-9])_(c5)|(cy)_(v|c3|c4))(_r[1-3])?$')
X_MIN = {2: 3000, 3: 1500, 4: 1500, 5: 1500}
X_SHARE = 0.95
C1_MIN = 1000000
O_MIN = 1000000
RC2_MIN = 100
GAMMA_MIN = 100
KAPPA = (0.80, 1.25)
BLOCK = 90
BLK_SKIP = 2
MIN_BLOCKS = 3
OLD_SHARE = 0.9
LINES_MAX = 40
PRE_TOL = 4   # item 659 (v): prefix sums within 4 events (was 1, item 651 (b)(2))
CLOSE_MAX = 3   # item 662 (v)(2): the closing point T at most 3 FrameTrace-x lines from the last one
TOL8 = 1     # RC2 of F30l: a report torn by the last flip of the process
BITS8 = ('rts_bad_r', 'rts_bad_xr', 'rts_bad_xc', 'rts_bad_xe', 'rts_bad_s', 'rts_bad_p', 'rts_bad_m', 'rts_bad_l')
KB7 = BITS8[:7]   # item 655 (zh)(1): L is a reference
SRC_NAME = dict(rts_bad_r='R', rts_bad_xr='X:xr', rts_bad_xc='X:xc', rts_bad_xe='X:xe', rts_bad_s='S', rts_bad_p='P', rts_bad_m='M',
                rts_bad_l='L')
BIT_OF = dict(rts_bad_r=0x010, rts_bad_s=0x040, rts_bad_p=0x080, rts_bad_m=0x100, rts_bad_l=0x200)
REQ = ('rts_n', 'rts_skip', 'rts_pa', 'rts_pb', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx', 'rts_race',
       'rts_refuse', 'rts_xthr', 'rts_acqw', 'rts_ovf', 'rts_lost', 'rts_xb_ids', 'rts_xb_live', 'rts_xb_meta', 'rts_xb_ser',
       'rts_xb_bound', 'rts_xb_pass') + BITS8
LEGACY_NEW = ('rts_bad_b', 'rts_bad_rx') + BITS8   # --legacy-fields: regression on logs before T2 only, never a tag
XB_LIVE = ('rts_xb_ids', 'rts_xb_live', 'rts_xb_bound', 'rts_xb_pass')
XB_ALL = ('rts_xb_ids', 'rts_xb_live', 'rts_xb_meta', 'rts_xb_ser', 'rts_xb_bound', 'rts_xb_pass')
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
    if m.group(1):
        return m.group(1), m.group(2), m.group(5) or ''
    return m.group(3), m.group(4), m.group(5) or ''


def expected_env(scene, kind):
    lv, sd, keys = SCENES[scene]
    e = dict(KYTY_GUEST_ARGS='-lvl ' + lv, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1',
             KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_RT_SKIP=str(KNOB[kind]))
    if kind == 'v':
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
    """One pass over the log.  legacy=True (regression on logs before T2 only, never a tag): the fields of LEGACY_NEW may be absent
    and count 0."""
    req = tuple(k for k in REQ if not (legacy and k in LEGACY_NEW))
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(entry_ln=None, first_guest_ln=None, modes=[], refused=0, gates=[], mm=[], mm_bad=0, verify=0, proc=new_sums(),
             win=new_sums(), x_lines=0, x_win=0, x_missing=0, x_missing_names=[], x_dup=0, x_prefixed=0, draw_win=0, draw_lines=0,
             bda_win=[], bda_missing=0, chkb_by_n={}, id_pa=0, id_pb=0, id_rx=0, id8_lines=0, ineq_lines=0, pre_viol=0, pre_first=None,
             pre_viol_rx=0, maxdev=dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0), dev2=dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0),
             x_full=0, close_idx=None, close_ln=None, close_sums=None, close_dist=None, tail_dev=dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0),
             ft_last_n=None, input_max=None, input_lines=0, b42=[],
             death=[], minimized=0, recovering=0, winev={}, sig=[], variant_dir=[], gamepatch=0, diagb32=0, stall_lines=0, fork=[],
             ver_any=0, ver_bad=0, summary=[], summary_bad=0, lines=0)
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
            d2 = r['dev2']
            d2['chk_pa'] += abs(pre['c'] - pre['a']) >= 2
            d2['chkb_pb'] += abs(pre['cb'] - pre['b']) >= 2
            d2['rx_b'] += pre['rx'] - pre['bb'] >= 2
            d2['b_bad'] += pre['bb'] - pre['bad'] >= 2
            if abs(pre['c'] - pre['a']) > PRE_TOL or abs(pre['cb'] - pre['b']) > PRE_TOL:
                r['pre_viol'] += 1
                if r['pre_first'] is None:
                    r['pre_first'] = ln
            if pre['rx'] > pre['bb'] + PRE_TOL or pre['bb'] > pre['bad'] + PRE_TOL:
                r['pre_viol_rx'] += 1
                if r['pre_first'] is None:
                    r['pre_first'] = ln
            r['x_full'] += 1
            if pre['c'] == pre['a'] and pre['cb'] == pre['b'] and pre['rx'] <= pre['bb'] <= pre['bad']:
                # item 662 (v)(1): the closing point T - every prefix deviation 0, rx <= b <= bad without tolerance
                r['close_idx'] = r['x_full']
                r['close_ln'] = ln
                r['close_sums'] = dict(r['proc'])
                r['tail_dev'] = dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0)
            else:
                td = r['tail_dev']
                td['chk_pa'] = max(td['chk_pa'], abs(pre['c'] - pre['a']))
                td['chkb_pb'] = max(td['chkb_pb'], abs(pre['cb'] - pre['b']))
                td['rx_b'] = max(td['rx_b'], pre['rx'] - pre['bb'])
                td['b_bad'] = max(td['b_bad'], pre['bb'] - pre['bad'])
            if got['rts_chk'] != got['rts_pa']:
                r['id_pa'] += 1
            if got['rts_chk_b'] != got['rts_pb']:
                r['id_pb'] += 1
            if not (got['rts_bad_rx'] <= got['rts_bad_b'] <= got['rts_bad']):
                r['id_rx'] += 1
            if not rc2_ok(got)[0]:
                r['id8_lines'] += 1
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
        for mv in VERSION_ANY.findall(line):
            r['ver_any'] += 1
            if mv != VERSION:
                r['ver_bad'] += 1
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
    if r['close_idx'] is not None:
        r['close_dist'] = r['x_full'] - r['close_idx']
    fh.close()
    return r


def rc2_ok(P):
    """RC2 of F30l on sums P: (ok, exact ok, tolerant ok, text)."""
    s8 = sum(P[k] for k in BITS8)
    x3 = P['rts_bad_r'] + P['rts_bad_xr'] + P['rts_bad_xc'] + P['rts_bad_xe']
    exact = (all(P[k] <= P['rts_bad_b'] for k in BITS8) and P['rts_bad_b'] <= P['rts_bad'] and P['rts_bad_r'] <= P['rts_bad_rx']
             and P['rts_bad_xr'] <= P['rts_bad_rx'] and P['rts_bad_xc'] <= P['rts_bad_rx'] and P['rts_bad_xe'] <= P['rts_bad_rx'])
    tol = P['rts_bad_rx'] <= x3 + TOL8 and P['rts_bad_b'] <= s8 + TOL8
    return exact and tol, exact, tol, 'sum8 %d, r+xr+xc+xe %d' % (s8, x3)


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
    """True when the file has the sha256 of T2 and carries VERSION; memo per (path, size, mtime) - one read per process."""
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
        p.update(log=lg if os.path.exists(lg) or not os.path.exists(lg + '.xz') else lg + '.xz', stdout=os.path.join(base, 'stdout.txt'),
                 run=os.path.join(base, 'es.json'), idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'),
                 bin=(text(os.path.join(base, 'bin.txt')) or '').strip() or os.path.join(base, 'bin.exe'),
                 vread=os.path.join(base, 'v_read.json'), kref=os.path.join(base, 'kref.tsv'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    scene, kind, rep = parts(tag)
    vread = None
    if kind == 'c4':
        for vt in ['f30_cy_v%s' % s for s in ('', '_r1', '_r2', '_r3')]:
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


def reconcile(x, P, knob):
    """Lines MISMATCH mode=<knob> against the counters (item 644 (g) extended to the bits of T2)."""
    mk = [m for m in x['mm'] if m['mode'] == knob]
    lines = dict(rx=sum(1 for m in mk if m['bits'] & 0x030), b=sum(1 for m in mk if m['bits'] & 0x3f0),
                 x=sum(1 for m in mk if m['bits'] & 0x020))
    for k, bit in BIT_OF.items():
        lines[k] = sum(1 for m in mk if m['bits'] & bit)
    exact = len(mk) == P['rts_bad'] and P['rts_bad'] <= LINES_MAX
    x3 = P['rts_bad_xr'] + P['rts_bad_xc'] + P['rts_bad_xe']
    if exact:
        ok = (P['rts_bad_rx'] == lines['rx'] and P['rts_bad_b'] == lines['b'] and all(P[k] == lines[k] for k in BIT_OF)
              and max(P['rts_bad_xr'], P['rts_bad_xc'], P['rts_bad_xe']) <= lines['x'] <= x3)
    else:
        ok = (P['rts_bad_rx'] >= lines['rx'] and P['rts_bad_b'] >= lines['b'] and all(P[k] >= lines[k] for k in BIT_OF)
              and x3 >= lines['x'])
    a_only = sum(1 for m in mk if (m['bits'] & 0x3f0) == 0)
    return dict(ok=ok, exact=exact, n=len(mk), lines=lines, a_only=a_only, x3=x3)


def read_tag(tag, p, legacy=False):
    scene, kind, rep = parts(tag)
    level, sd, keys = SCENES[scene]
    knob = KNOB[kind]
    res = dict(tag=tag, scene=scene, kind=kind, knob=knob, level=level, reader_sha256=sha_file(os.path.abspath(__file__)))
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
        ('json binary_sha256 = T2 bba692c6 (%s)' % (jbin or '-')[:16], jbin == BIN_T, 'harness'),
        ('installed during the tag = T2 bba692c6 (%s)' % (inst_t or '-')[:16], inst_t == BIN_T, 'harness'),
        ('installed before = after = FS11 ea51ae80 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_INST and inst_a == BIN_INST, 'harness'),
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
    rec = None
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
        ver_ok = x['ver_bad'] == 0
        d7 = lsha == BIN_T and jbin == lsha and fork_ok and bin_ver is True and ver_ok
        d += [('(D1) exactly one RtSkip: mode %d, no other value (%s)' % (knob, x['modes'][:4]), d1),
              ('(D2) RtSkip: refused lines %d, process rts_refuse %d' % (x['refused'], P['rts_refuse']), d2),
              ('(D3) Gate: rtskip= lines none or all %d (%s)' % (knob, x['gates'][:4]), d3),
              ('(D4) process rts_xthr %d, rts_acqw %d' % (P['rts_xthr'], P['rts_acqw']), d4),
              ('(D5) FrameTrace-x in the window %d >= 0.95 x FrameTrace-draw %d and >= %d' % (x['x_win'], x['draw_win'], X_MIN[knob]), d5),
              ('(D6) window rts_ovf %d' % W['rts_ovf'], d6),
              ('(D7) RC3 of F30l (item 658 (b)): launch_sha256 %s = T2, binary_sha256 = launch_sha256 (%s), one log line version: Fork build '
               '... 6fbdcf6 (%s), version string -1907-g6fbdcf67 in the pinned copy of sha T2 (%s), log version strings %d of them other '
               'than -1907-g6fbdcf67 %d' % ((lsha or '-')[:16], (jbin or '-')[:16], x['fork'], bin_ver, x['ver_any'], x['ver_bad']), d7),
              ('RC4 (F30f) / RC2 (F30l) every FrameTrace-x line carries every field of REQ incl. the 8 bit counters (lines %d, missing %d %s) '
               '- else missing field' % (x['x_lines'], x['x_missing'], x['x_missing_names'][:3]), x['x_missing'] == 0 and x['x_lines'] > 0)]
        # item 662 (v): the exact members of item 651 (b)(1) and RC1 of F30l read at the closing point T (sums up to T inclusive);
        # T at most CLOSE_MAX FrameTrace-x lines from the last one; the tail after T - by the prefix tolerance of item 659 (v)
        PT = x['close_sums']
        cdist = x['close_dist']
        close_ok = PT is not None and cdist is not None and cdist <= CLOSE_MAX
        PTs = PT if PT is not None else new_sums()
        ident_ok = (close_ok and PTs['rts_chk'] == PTs['rts_pa'] and PTs['rts_chk_b'] == PTs['rts_pb']
                    and PTs['rts_bad_rx'] <= PTs['rts_bad_b'] <= PTs['rts_bad']
                    and x['pre_viol'] == 0 and x['pre_viol_rx'] == 0)
        close_txt = ('closing point T (item 662): FrameTrace-x line %s of %d (log line %s), distance to the last %s <= %d; sums at T chk %d '
                     '/ pa %d, chk_b %d / pb %d, rx %d <= b %d <= bad %d; tail deviations %s' % (
                         x['close_idx'], x['x_full'], x['close_ln'], cdist, CLOSE_MAX, PTs['rts_chk'], PTs['rts_pa'], PTs['rts_chk_b'],
                         PTs['rts_pb'], PTs['rts_bad_rx'], PTs['rts_bad_b'], PTs['rts_bad'], json.dumps(x['tail_dev'], sort_keys=True)))
        if not ident_ok:
            stop.append('parse identity of item 651 (b) broken (%s%s; process sums chk %d / pa %d, chk_b %d / pb %d, rx %d <= b %d <= bad %d; '
                        'prefix violations %d / %d; max deviation %s) - NOT_ADMITTED and series stop, item 651 (v)' % (
                            close_txt, '' if close_ok else ' - NO T within the distance',
                            P['rts_chk'], P['rts_pa'], P['rts_chk_b'], P['rts_pb'], P['rts_bad_rx'], P['rts_bad_b'], P['rts_bad'],
                            x['pre_viol'], x['pre_viol_rx'], x['maxdev']))
        parse_ok = (ident_ok and P['rts_chk_b'] <= P['rts_chk'] <= P['rts_n']
                    and P['rts_bad_noreg'] <= P['rts_bad']
                    and x['verify'] <= min(LINES_MAX, P['rts_bad']) and x['mm_bad'] == 0 and x['x_dup'] == 0)
        d.append(('parse [identity of the parse, RC7]: %s - %s; at T rts_chk = rts_pa, rts_chk_b = rts_pb, rts_bad_rx <= rts_bad_b <= rts_bad '
                  '(item 662 (v)(3)); process (reference) rts_chk %d / rts_pa %d, rts_chk_b %d / rts_pb %d, rts_bad_rx %d / rts_bad_b '
                  '%d / rts_bad %d; prefix sums within %d events at every line incl. the tail (item 659 (v), 662 (v)(4)) (chk/pa, chk_b/pb %d; rx/b/bad %d; first line %s); chk_b <= chk '
                  '<= n %d, noreg %d <= bad; RtSkipVerify lines %d <= min(40, bad); unparsable %d; duplicate fields %d; letter rows (per line, '
                  'reference - the flip tears one event): chk!=pa %d, chk_b!=pb %d, rx<=b<=bad broken %d; max prefix deviation %s; lines with '
                  'prefix deviation >= 2 (item 659 (v), reference) %s' % (
                      close_txt, 'ok' if close_ok else 'NO',
                      P['rts_chk'], P['rts_pa'], P['rts_chk_b'], P['rts_pb'], P['rts_bad_rx'], P['rts_bad_b'], P['rts_bad'], PRE_TOL,
                      x['pre_viol'], x['pre_viol_rx'], x['pre_first'], P['rts_n'], P['rts_bad_noreg'], x['verify'], x['mm_bad'], x['x_dup'],
                      x['id_pa'], x['id_pb'], x['id_rx'], json.dumps(x['maxdev'], sort_keys=True),
                      json.dumps(x['dev2'], sort_keys=True)), parse_ok))
        # item 662 (v)(3): RC1 at T exactly; item 662 (b): rts_skip = 0 and chk >= chk_b also on the process sums
        rc1 = (close_ok and PTs['rts_skip'] == 0 and PTs['rts_chk'] >= PTs['rts_chk_b'] and PTs['rts_chk_b'] == PTs['rts_pb']
               and PTs['rts_pb'] >= 1 and P['rts_skip'] == 0 and P['rts_chk'] >= P['rts_chk_b'])
        d.append(('RC1 (F30l): at T (item 662: line %s, distance %s <= %d) rts_skip %d = 0 and rts_chk %d >= rts_chk_b %d = rts_pb %d >= 1; '
                  'process rts_skip %d = 0 and rts_chk %d >= rts_chk_b %d (process rts_pb %d - reference)' % (
                      x['close_idx'], cdist, CLOSE_MAX, PTs['rts_skip'], PTs['rts_chk'], PTs['rts_chk_b'], PTs['rts_pb'],
                      P['rts_skip'], P['rts_chk'], P['rts_chk_b'], P['rts_pb']), rc1))
        r2, r2e, r2t, r2s = rc2_ok(P)
        d.append(('RC2 (F30l): exact - each of the 8 <= rts_bad_b %d <= rts_bad %d, rts_bad_r %d <= rts_bad_rx %d, xr %d / xc %d / xe %d <= '
                  'rts_bad_rx (%s); with 1 of tolerance - rts_bad_rx <= r+xr+xc+xe + 1, rts_bad_b <= sum8 + 1 (%s) [%s; per line '
                  'reference: lines out of RC2 %d]' % (P['rts_bad_b'], P['rts_bad'], P['rts_bad_r'], P['rts_bad_rx'], P['rts_bad_xr'],
                                                       P['rts_bad_xc'], P['rts_bad_xe'], 'ok' if r2e else 'NO', 'ok' if r2t else 'NO', r2s,
                                                       x['id8_lines']), r2))
        rc4 = None
        if knob != 3:
            rc4 = P['rts_bad_noreg'] == P['rts_bad']
            d.append(('RC4 (F30l): value %d != 3 - process rts_bad_noreg %d = rts_bad %d' % (knob, P['rts_bad_noreg'], P['rts_bad']), rc4))
        pb6 = None
        if kind == 'c5':
            pb6 = P['rts_xb_pass'] == 0
            d.append(('PB item 6 dropped (item 655 (e)(4)): process rts_xb_pass %d = 0' % P['rts_xb_pass'], pb6))
        if scene == 's9':
            d.append(('S9 window end: last FrameTrace n %s >= %d (item 649 (d); presents of the InputScript lines - max %s, lines %d)' % (
                x['ft_last_n'], S9_N_MIN, x['input_max'], x['input_lines']), (x['ft_last_n'] or 0) >= S9_N_MIN))
        if kind in ('c5', 'c4'):
            rec = reconcile(x, P, knob)
            res['rec'] = rec
            d.append(('reconciliation (%s): lines MISMATCH mode=%d %d, process rts_bad %d; lines %s against rts_bad_rx %d, rts_bad_b %d, r %d, s %d, '
                      'p %d, m %d, l %d, xr+xc+xe %d' % ('exact' if rec['exact'] else 'lines exhausted - >=', knob, rec['n'], P['rts_bad'],
                                                         json.dumps(rec['lines'], sort_keys=True), P['rts_bad_rx'], P['rts_bad_b'],
                                                         P['rts_bad_r'], P['rts_bad_s'], P['rts_bad_p'], P['rts_bad_m'], P['rts_bad_l'],
                                                         rec['x3']), rec['ok']))
            if rec['exact'] and not rec['ok']:
                stop.append('reconciliation failed with the lines not exhausted - item 649 (v)')
        if kind == 'c4':
            d.append(('RC2 (a) c4 (item 644 (v)): armed - (D1) and process rts_xb_meta %d = rts_xb_ser %d = 0' % (
                P['rts_xb_meta'], P['rts_xb_ser']), d1 and P['rts_xb_meta'] == 0 and P['rts_xb_ser'] == 0))
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
                d.append(('RC2 (b) c4: other PB reasons alive vs f30_cy_v (%s; threshold %d): %s' % ((vr or {}).get('tag'), RC2_MIN,
                                                                                                 '; '.join(rows)), rc2b))
        if x['refused'] > 0:
            stop.append('RtSkip: refused line (%d)' % x['refused'])
        if not d4:
            stop.append('(D4) != 0: rts_xthr %d rts_acqw %d' % (P['rts_xthr'], P['rts_acqw']))
        inst = [nm for nm, okv in (('RC1 (F30l)', rc1), ('RC2 (F30l)', r2), ('RC4 (F30l)', rc4), ('PB item 6 dropped', pb6), ('(D7)', d7))
                if okv is False]
        if inst:
            stop.append('instrument member broken: %s - NOT_ADMITTED and series stop (executor variant: the next tag of the same binary and '
                        'form gives the same defect; question to the lead)' % ', '.join(inst))
    adm_rows = [(a, bool(b)) for a, b, k in harness] + [(a, bool(b)) for a, b in d]
    res['admission'] = [[a, b] for a, b in adm_rows]
    failed_h = [(a, k) for a, b, k in harness if not b]
    failed_d = [a for a, b in d if not b]
    interference = [a for a, k in failed_h if k == 'interference']
    binary_bad = [a for a in failed_d if a.startswith(('RC4 (F30f)', '(D7) ', 'RC1 (F30l)', 'RC2 (F30l)', 'RC4 (F30l)', 'PB item 6'))]
    if binary_bad:
        status = 'NOT_ADMITTED'   # a wrong binary, a lost field or a broken instrument member is not a run disturbance
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
                      win_s=win_s, lines=X.get('lines'), death=(X.get('death') or []) + sdth, video_index=idx_n, glitches=gl,
                      fork=X.get('fork'), x_prefixed=X.get('x_prefixed'), ineq_lines=X.get('ineq_lines'), ft_last_n=X.get('ft_last_n'),
                      input_lines=X.get('input_lines'), input_max=X.get('input_max'), prefix_maxdev=X.get('maxdev'),
                      prefix_dev2=X.get('dev2'), close_idx=X.get('close_idx'), close_ln=X.get('close_ln'), close_dist=X.get('close_dist'),
                      x_full=X.get('x_full'), tail_dev=X.get('tail_dev'))
    if x is not None:
        P, W = x['proc'], x['win']
        res['proc'] = dict(P)
        res['win'] = dict(W)
        res['verify_lines'] = x['verify']
        bits_cnt = {}
        for m in x['mm']:
            kk = '0x%03x' % m['bits']
            bits_cnt[kk] = bits_cnt.get(kk, 0) + 1
        res['mm_bits'] = bits_cnt
        res['d5'] = [x['x_win'], x['draw_win']]
        md = mode_member(x)
        res['bda'] = md
        res['kappa'] = kappa_rows(x, level, md['mode'], kref(p['kref']))
        res['b42'] = b42_window(x)
        res['b_minus_rx'] = P['rts_bad_b'] - P['rts_bad_rx']
        m = []
        dset_ok = all(b for a, b in d[:4]) and d[6][1]   # (D1)-(D4), (D7)
        if kind in ('c5', 'c4'):
            s7 = sum(P[k] for k in KB7)
            live = [SRC_NAME[k] for k in KB7 if P[k] >= 1]
            res['kb2'] = dict(sum7=s7, live=live, l_ref=P['rts_bad_l'], a_only_lines=(rec or {}).get('a_only'),
                              per=dict((SRC_NAME[k], P[k]) for k in BITS8), race=P['rts_race'])
            m += [("K_B'' (item 655 (zh)(1)): process r + xr + xc + xe + s + p + m = %d >= 1 (live sources %s; L %d - reference)" % (
                s7, live or '-', P['rts_bad_l']), s7 >= 1)]
            for k in KB7:
                m.append(('source %s (item 658 (v)): process %s %d >= 1' % (SRC_NAME[k], k, P[k]), P[k] >= 1))
        elif kind == 'c3':
            k_lines = [mm for mm in x['mm'] if mm['mode'] == 3 and mm['bits'] & 0x001]
            m += [('(K) >= 1 line MISMATCH mode=3 with bit 0x001 (%d) and process rts_bad %d >= 1' % (len(k_lines), P['rts_bad']),
                   bool(k_lines) and P['rts_bad'] >= 1),
                  ("(K') process rts_bad_noreg %d = 0" % P['rts_bad_noreg'], P['rts_bad_noreg'] == 0),
                  ('race: process rts_race %d = 0 (RC2)' % P['rts_race'], P['rts_race'] == 0)]
            if P['rts_bad_noreg'] > 0:
                stop.append("(K') != 0 at c3: rts_bad_noreg %d" % P['rts_bad_noreg'])
            if P['rts_race'] > 0:
                stop.append('rts_race %d > 0 at c3 (RC2)' % P['rts_race'])
        else:
            o_ok = md['mode'] == 'OLD' and md['chkb_old'] >= O_MIN
            m += [('(gamma) admission (item 655 (e)(3)): process rts_xb_ser %d >= %d' % (P['rts_xb_ser'], GAMMA_MIN), P['rts_xb_ser'] >= GAMMA_MIN),
                  ('(C1) window rts_chk_b %d >= 10^6' % W['rts_chk_b'], W['rts_chk_b'] >= C1_MIN),
                  ('(V) process rts_bad %d = 0 and RtSkipVerify lines %d = 0' % (P['rts_bad'], x['verify']), P['rts_bad'] == 0 and x['verify'] == 0),
                  ('race: process rts_race %d = 0 (RC2)' % P['rts_race'], P['rts_race'] == 0),
                  ('(O) entry %s (read blocks %d, OLD %d, NEW %d, mean %s) and window rts_chk_b in OLD blocks %d >= 10^6' % (
                      md['mode'], md['read_blocks'], md['old_blocks'], md['new_blocks'], md['mean_read'], md['chkb_old']), o_ok)]
            if P['rts_race'] > 0:
                stop.append('rts_race %d > 0 at v (RC2)' % P['rts_race'])
            if (P['rts_bad'] > 0 or x['verify'] > 0) and dset_ok:
                stop.append('(V) != 0 at v with (D1)-(D4), (D7) met: rts_bad %d, RtSkipVerify lines %d - outcome 640 (e)(4) (item 655 (zh)(2))' % (
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
        pr, wn = res['proc'], res['win']
        keys = ('rts_n', 'rts_skip', 'rts_pa', 'rts_pb', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx',
                'rts_race', 'rts_lost')
        out.append('  PROCESS %s' % ' '.join('%s=%d' % (k, pr[k]) for k in keys))
        out.append('  WINDOW  %s' % ' '.join('%s=%d' % (k, wn[k]) for k in keys))
        out.append('  BITS process (item 655 (e)(4)) %s; rts_bad_b - rts_bad_rx = %d (member RC6)' % (
            ' '.join('%s=%d' % (k, pr[k]) for k in BITS8), res['b_minus_rx']))
        out.append('  XB process %s' % ' '.join('%s=%d' % (k, pr[k]) for k in XB_ALL))
        out.append('  RtSkipVerify lines %d, bits %s' % (res['verify_lines'], json.dumps(res['mm_bits'], sort_keys=True)))
        out.append('  BDA %s' % json.dumps(res['bda'], sort_keys=True))
        out.append('  KAPPA (reference, RC6; [0.80; 1.25]) %s' % json.dumps(res['kappa'], sort_keys=True))
        out.append('  FIXB42 window increments %s; window rts_lost %d' % (json.dumps(res['b42'], sort_keys=True)[:600], wn['rts_lost']))
    if res.get('kb2') is not None:
        out.append("  K_B'' %s" % json.dumps(res['kb2'], sort_keys=True))
    if res.get('rec') is not None:
        out.append('  RECONCILIATION %s' % json.dumps(res['rec'], sort_keys=True))
    out.append('  REFERENCE %s' % json.dumps(res['ref'], sort_keys=True))
    out.append('  STOP %s' % ('none' if not res['stop'] else '; '.join(res['stop'])))
    return out


def latest_admitted(reads, base):
    for rep in ('', '_r1', '_r2', '_r3'):
        r = reads.get(base + rep)
        if r is not None and r.get('status') == 'ADMITTED':
            return r
    return None


def mem(r, i):
    return r is not None and r.get('members') is not None and len(r['members']) > i and r['members'][i][1]


def scene_rows(reads):
    """reads: {tag: read.json} -> rows for F30n (item 655 (zh)); not a verdict."""
    out = []
    live_scenes = []
    src_union = set()
    for k in range(1, 10):
        sc = 's%d' % k
        r = latest_admitted(reads, 'f30_%s_c5' % sc)
        kb = mem(r, 0)
        live = (r or {}).get('kb2', {}).get('live') or []
        if kb:
            live_scenes.append(sc)
            src_union.update(live)
        any_r = reads.get('f30_%s_c5' % sc)
        out.append("%s %s: c5 %s K_B'' %s live %s (v of the scene - F30f, transfer by item 658 (a))" % (
            sc, SCENES[sc][0], (any_r or {}).get('status', '-') if r is None else 'ADMITTED', kb if r is not None else 'not checked',
            live or '-'))
    v = latest_admitted(reads, 'f30_cy_v')
    c3 = latest_admitted(reads, 'f30_cy_c3')
    c4 = latest_admitted(reads, 'f30_cy_c4')
    gamma = mem(v, 0)
    cy_counted = bool(v is not None and gamma and mem(v, 1) and mem(v, 2) and c3 is not None and mem(c3, 0))
    cy_kb = mem(c4, 0)
    if cy_counted and cy_kb:
        src_union.update((c4 or {}).get('kb2', {}).get('live') or [])
    out.append("cy cymbal_party_land: v %s (gamma) %s (C1) %s (V)=0 %s (O) %s | c3 %s (K) %s | c4 %s K_B'' %s live %s | counted %s" % (
        (reads.get('f30_cy_v') or {}).get('status', '-'), gamma, mem(v, 1), mem(v, 2), mem(v, 4),
        (reads.get('f30_cy_c3') or {}).get('status', '-'), mem(c3, 0), (reads.get('f30_cy_c4') or {}).get('status', '-'), cy_kb,
        (c4 or {}).get('kb2', {}).get('live') or '-', cy_counted))
    nlive = len(live_scenes) + (1 if cy_counted and cy_kb else 0)
    out.append("scenes with live K_B'' %d (s1..s9: %s; cy %s); S1 or S9 among them %s; live sources over them %s - rows for F30n by item 655 "
               "(zh)(1)-(3), 658 (v)" % (nlive, ' '.join(live_scenes) or '-', cy_counted and cy_kb, any(s in ('s1', 's9') for s in live_scenes),
                                         sorted(src_union) or '-'))
    return out


def table(rd):
    out = ['| tag | status | knob | launch sha | (D5) x/draw | rts_bad | b / rx | r xr xc xe s p m l | xb_ser / xb_pass | race | win chk_b | mode | stop |',
           '|' + '---|' * 13]
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
                out.append('| %s | %s | %d | %s | %s | %s | %s / %s | %s | %s / %s | %s | %s | %s | %s |' % (
                    t, r['status'], r['knob'], (r.get('launch_sha256') or '-')[:8], '%s/%s' % tuple(r.get('d5') or ['-', '-']),
                    pr.get('rts_bad', '-'), pr.get('rts_bad_b', '-'), pr.get('rts_bad_rx', '-'), ' '.join(str(pr.get(k, '-')) for k in BITS8),
                    pr.get('rts_xb_ser', '-'), pr.get('rts_xb_pass', '-'), pr.get('rts_race', '-'), wn.get('rts_chk_b', '-'), bd.get('mode', '-'),
                    '; '.join(r.get('stop') or []) or '-'))
    out += [''] + scene_rows(reads)
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader f30m_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        if not TAG_RX.match(tag):
            print('usage: f30m_read.py <tag> | --dir D --tag T | --table')
            return 2
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        if not TAG_RX.match(tag):
            print('usage: f30m_read.py <tag> | --dir D --tag T | --table')
            return 2
        p = paths(tag)
    if js and p.get('run') and os.path.normcase(os.path.abspath(js)) == os.path.normcase(os.path.abspath(p['run'])):
        # item 662: the json of the run (enter_scene) is evidence of the harness members - never overwritten by the reader
        print('refused: --json %s is the run json of the tag' % js)
        return 2
    res = read_tag(tag, p, '--legacy-fields' in argv)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
