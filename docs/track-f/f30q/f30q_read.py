"""Track F link F30q (HPP-727; ROADMAP s122 item 664 (z)(1)-(5); item 665 (v) RC1-RC5 of F30p, (g)): the reader of the series =6 on the
binary T3 50596951 (F30o HPP-725, worktree ea38426b = T2 6fbdcf67 + d25a78bc): f30_s1_w6 (Sky Garden, KYTY_RT_SKIP=6, form W of item
295 (b), hold 150 s from the entry line) first, then f30_s<k>_c6 (k = 1..9, scenes of F30f, s9 - Sky Garden with the water keys of FS3c;
=6, 150 s, no video).  Port of C:/kyty/f287/f30m/f30m_read.py (F30m, HPP-723; the port base of item 664 (z)(5)).  Rows and members only;
the reading of the series is F30r (HPP-728) by item 664 (i) with item 665 (g).  ASCII only.

    python f30q_read.py <tag> [--json <out>]                       one tag (files of C:/kyty/f287/f30q)
    python f30q_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, installed_before.txt, installed_after.txt, installed_sha.txt, level.txt, seal.md,
        bin.exe (or bin.txt with a path), kref.tsv
    python f30q_read.py --table [--runs <dir>]                     the table and the scene rows over every runs/<tag>/read.json

TAGS  f30_s1_w6; f30_s<k>_c6 (k = 1..9); suffix _r1.._r3 - repeat after an interference by the lead's item (item 664 (z)(5)).
WINDOW  from the line 'GuestOut: Level has started: <level>' (the first with the level of the scene) to the end of the log; PROCESS -
      every line of the log.  A FrameTrace-x line = a line starting 'FrameTrace-x: n='; its fields are the ' rts_<name>=<int>' tokens,
      the name taken whole up to '=' (rts_inj is a prefix of rts_inj_s, rts_inj_race, rts_inj_nos, rts_inj_none - never matched as one).
CLOSING POINT T (item 662 (v), unchanged): the last FrameTrace-x line with every prefix deviation 0 and rx <= b <= bad without tolerance,
      at most CLOSE_MAX = 3 FrameTrace-x lines from the last one; SUMS AT T = the sums of the FrameTrace-x lines up to T inclusive.  Every
      member of item 665 (v) is read on the sums at T (item 665 (v): 'all - at the closing point of item 662').
ADMISSION (any member NO - NOT_ADMITTED with the reason; the first failed harness member of an interference kind - INTERFERENCE):
  harness  as F30m with: json binary_sha256 = T3; installed during the tag = T3; installed before = after = FS11 ea51ae80 (item 664 (z)(1));
           env = the form of the tag (c6: as F30m with KYTY_RT_SKIP=6; w6: plus VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000);
           last --vulkan-validation true at w6, false at c6.
  c6       (D1)-(D7) of item 643 (d)(3) as at =4 (item 664 (z)(3)): (D1) exactly one 'RtSkip: mode 6 ctx_slots=<n> groups=<n>
           rec_bytes=<n>' line (the text of the print place LOGF("RtSkip: mode %u ctx_slots=%u groups=%u rec_bytes=%u\n") of
           renderDraw.cpp at ea38426b, item 665 (v)(5), item 414 (d)(2)), no other value; (D5) >= 1500 FrameTrace-x lines in the window
           and >= 0.95 x FrameTrace-draw.
  w6       the same rows; (D1) and (D7) are members (item 665 (v)(5) 'at every tag'), (D2)-(D6) are reference rows (item 664 (z)(2) names
           the members of w6; executor variant printed: (D2)-(D6) as members).
  (D7) = RC5 of F30p (item 665 (v)(5)): launch_sha256 (sha256 of the started file) = T3 505969510fb20f7c...; binary_sha256 =
           launch_sha256; exactly one log line 'version: Fork build arigandores/KytyPS5 ea38426'; the version string -1908-gea38426b in the
           pinned copy of sha T3; every log line carrying a version string 'KytyPS5-20..' carries exactly
           KytyPS5-2026-09-15-6a2987a-1908-gea38426b (none - vacuous).
  fields   RC4 (F30f) / RC2 (F30l) / RC2 (F30p): every FrameTrace-x line carries every field of REQ incl. the 8 bit counters and the 5
           names rts_inj, rts_inj_s, rts_inj_race, rts_inj_nos, rts_inj_none - else NOT_ADMITTED 'missing field' (not 0).
  parse    item 651 (b) with items 659 (v), 662 (v) as F30m (closing point T, prefix tolerance 4, exact identities at T).
  RC1 (F30l), RC2 (F30l) as F30m; RC4 (F30l): process rts_bad_noreg = rts_bad (value 6 != 3).
  reconciliation (item 644 (g) extended to the bits, as F30m c5 / c4) with the lines MISMATCH mode=6.
  RC1 (F30p, item 665 (v)(1)): sum at T of rts_inj_nos = 0 (w6 and c6) - broken: NOT_ADMITTED 'code or instrument', STOP row.
  RC2 (F30p, item 665 (v)(2)): at T |rts_inj_s + rts_inj_race + rts_inj_nos - rts_inj| <= 1 (exact, tolerance 1 on the tail).
  RC3 (F30p, item 665 (v)(3)): at T rts_bad_s >= rts_inj_s - 1, rts_bad >= rts_inj_s - 1, rts_race >= rts_inj_race - 1 (tolerance 1 on
           the tail, the lead's amendment); reference - the lines 'RtSkipVerify: MISMATCH ... mode=6' with bit 0x040.
  RC4 (F30p, item 665 (v)(4)): at T floor(rts_pb / 4096) - 1 <= rts_inj + rts_inj_none <= floor(rts_pb / 4096) + 1 (lower -1 - the lead's
           amendment); reference - process rts_xb_ser.
  (inj)    c6 (item 664 (z)(3) with item 665 (v)(4)): sum at T rts_inj >= 1 - YES; rts_inj = 0 and rts_inj_none >= 1 - YES with the row
           'the form found no target, K_S of the scene not live (data)'; rts_inj = 0 and rts_inj_none = 0 - NO and a STOP row ('code defect';
           with rts_pb >= 4096 - also RC4 broken).  w6 (item 664 (z)(2)): sum at T rts_inj >= 1 - a member of w6.
  w6 members (item 664 (z)(2), form W of item 295 (b)): lived to the end of the hold; 0 '[Vulkan][E]'; '[Vulkan][W]' > 0 (positive
           control); 'DualSrcBlend: supported=1 enabled=1' before the first GuestOut line; 0 death markers; 0 limit lines of the layer
           ('this will be the last time reporting it') - member of form 295 (b) as at b12_w.
ROWS FOR F30r (item 664 (z)(4), (i)(1); no verdict): rts_inj, rts_inj_s, rts_inj_race, rts_inj_nos, rts_inj_none (at T and process),
  process rts_bad, the 8 bit counters, natural S = rts_bad_s - rts_inj_s (reference, item 664 (i)(5)), rts_chk_b, every rts_xb_* (H1 of
  F30p: the extra rts_xb_ser at =6 - reference, not a basis), rts_race, the number of 'RtSkipVerify:' lines; K_S row (item 664 (i)(1) with
  item 665 (g)): at T rts_inj >= 1 and rts_inj_s >= 1 and rts_inj_nos = 0.
STOP rows: 'RtSkip: refused'; (D4) != 0; parse identity broken; reconciliation failed with the lines not exhausted; RC1 (F30p); rts_inj = 0
  with rts_inj_none = 0 (c6); RC1 / RC2 / RC4 of F30l, RC2 / RC3 / RC4 of F30p or (D7) broken (executor variant: a broken instrument member -
  the next tag of the same binary and form gives the same defect); at w6: [Vulkan][E] > 0 or a stop by the validation (item 664 (z)(2)).
"""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/f30q'
SEAL_PATH = G + '/pred/f30q_seal.md'
KREF_PATH = G + '/kref_f30q.tsv'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_50596951.exe'
BIN_T = '505969510fb20f7ce56a5195b3b6d2209af812bc0c2c85eccb6368a712b1bf34'   # T3, item 665 (v)(5)
BIN_INST = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'   # FS11, item 657
VERSION = b'KytyPS5-2026-09-15-6a2987a-1908-gea38426b'
VERSION_ANY = re.compile(rb'KytyPS5-20\d\d-\d\d-\d\d-[0-9a-f]+-\d+-g[0-9a-f]+')
FORK = b'version: Fork build arigandores/KytyPS5 '
FORK_T = 'ea38426'
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
    's9': ('underwater_aerial_garden', 300, KEYS_S9)}
KNOB = {'c6': 6, 'w6': 6}
HOLD = {'c6': 150, 'w6': 150}
TAG_RX = re.compile(r'^f30_(?:(s1)_(w6)|(s[1-9])_(c6))(_r[1-3])?$')
X_MIN = {6: 1500}
X_SHARE = 0.95
O_MIN = 1000000
KAPPA = (0.80, 1.25)
BLOCK = 90
BLK_SKIP = 2
MIN_BLOCKS = 3
OLD_SHARE = 0.9
LINES_MAX = 40
PRE_TOL = 4   # item 659 (v): prefix sums within 4 events (was 1, item 651 (b)(2))
CLOSE_MAX = 3   # item 662 (v)(2): the closing point T at most 3 FrameTrace-x lines from the last one
TOL8 = 1     # RC2 of F30l: a report torn by the last flip of the process
TOL_INJ = 1  # item 665 (v)(2)-(4): tolerance 1 on the tail
INJ_EVERY = 4096   # item 664 (e)(1): N = 4 096
VKLAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
LIMIT = '100000000'
BITS8 = ('rts_bad_r', 'rts_bad_xr', 'rts_bad_xc', 'rts_bad_xe', 'rts_bad_s', 'rts_bad_p', 'rts_bad_m', 'rts_bad_l')
INJ5 = ('rts_inj', 'rts_inj_s', 'rts_inj_race', 'rts_inj_nos', 'rts_inj_none')
SRC_NAME = dict(rts_bad_r='R', rts_bad_xr='X:xr', rts_bad_xc='X:xc', rts_bad_xe='X:xe', rts_bad_s='S', rts_bad_p='P', rts_bad_m='M',
                rts_bad_l='L')
BIT_OF = dict(rts_bad_r=0x010, rts_bad_s=0x040, rts_bad_p=0x080, rts_bad_m=0x100, rts_bad_l=0x200)
REQ = ('rts_n', 'rts_skip', 'rts_pa', 'rts_pb', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx', 'rts_race',
       'rts_refuse', 'rts_xthr', 'rts_acqw', 'rts_ovf', 'rts_lost', 'rts_xb_ids', 'rts_xb_live', 'rts_xb_meta', 'rts_xb_ser',
       'rts_xb_bound', 'rts_xb_pass') + BITS8 + INJ5
XB_ALL = ('rts_xb_ids', 'rts_xb_live', 'rts_xb_meta', 'rts_xb_ser', 'rts_xb_bound', 'rts_xb_pass')
RX_SUM = re.compile(rb'^LogAsync: full_waits=\d+ ')
RX_RTS = re.compile(rb' (rts_[a-z0-9_]+)=(\d+)')
RX_N = re.compile(rb'^FrameTrace-(?:x|draw): n=(\d+)')
RX_BDA = re.compile(rb' bda_scan=(\d+)')
RX_MODE_ANY = re.compile(rb'RtSkip: mode (\d+)')
RX_MODE = re.compile(rb'RtSkip: mode (\d+) ctx_slots=\d+ groups=\d+ rec_bytes=\d+\s*$')   # item 665 (v)(5): the text of the print place
RX_GATE = re.compile(rb'Gate: rtskip=(\d+)')
RX_MM = re.compile(rb'RtSkipVerify: MISMATCH frame=(-?\d+) bits=0x([0-9a-fA-F]+) reg=(\d+) .*\bmode=(\d+)')
RX_B42 = re.compile(rb'FixB42(?:Ext)?: mode=(\d+) (?:extent=(\d+)x(\d+) )?hit=(\d+) applied=(\d+) drawn=(\d+)')
RX_B42_EXT = re.compile(rb' extent=(\d+)x(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d) enabled=(\d)')
M_LIMIT = b'this will be the last time reporting it'
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
    if kind == 'w6':
        e.update(VK_LAYER_PATH=VKLAYER, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=LIMIT)
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


def scan(path, level):
    """One pass over the log."""
    req = REQ
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(entry_ln=None, first_guest_ln=None, modes=[], refused=0, gates=[], mm=[], mm_bad=0, verify=0, proc=new_sums(),
             win=new_sums(), x_lines=0, x_win=0, x_missing=0, x_missing_names=[], x_dup=0, x_prefixed=0, draw_win=0, draw_lines=0,
             bda_win=[], bda_missing=0, chkb_by_n={}, id_pa=0, id_pb=0, id_rx=0, id8_lines=0, ineq_lines=0, pre_viol=0, pre_first=None,
             pre_viol_rx=0, maxdev=dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0), dev2=dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0),
             x_full=0, close_idx=None, close_ln=None, close_sums=None, close_dist=None, tail_dev=dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0),
             ft_last_n=None, input_max=None, input_lines=0, b42=[],
             death=[], minimized=0, recovering=0, winev={}, sig=[], variant_dir=[], gamepatch=0, diagb32=0, stall_lines=0, fork=[],
             ver_any=0, ver_bad=0, summary=[], summary_bad=0, lines=0, mode_any=0, vke=0, vkw=0, vk_limit=0, dual=[])
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
            if RX_MODE_ANY.search(line):
                r['mode_any'] += 1
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
        mdu = RX_DUAL.search(line)
        if mdu:
            r['dual'].append((mdu.group(1) == b'1' and mdu.group(2) == b'1', ln))
        if b'[Vulkan][E]' in line:
            r['vke'] += 1
        if b'[Vulkan][W]' in line:
            r['vkw'] += 1
        if M_LIMIT in line:
            r['vk_limit'] += 1
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
    """True when the file has the sha256 of T3 and carries VERSION; memo per (path, size, mtime) - one read per process."""
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
    names = ('installed_before', 'installed_after', 'installed_sha', 'level')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        lg = os.path.join(base, 'log.txt')
        p.update(log=lg if os.path.exists(lg) or not os.path.exists(lg + '.xz') else lg + '.xz', stdout=os.path.join(base, 'stdout.txt'),
                 run=os.path.join(base, 'es.json'), seal=os.path.join(base, 'seal.md'),
                 bin=(text(os.path.join(base, 'bin.txt')) or '').strip() or os.path.join(base, 'bin.exe'),
                 kref=os.path.join(base, 'kref.tsv'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             seal=SEAL_PATH, bin=BIN_PATH, kref=KREF_PATH)
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


def inj_members(PT, kind):
    """The members of item 665 (v)(1)-(4) and the (inj) member on the sums at T: list of (name, ok, stop text or None)."""
    inj, s, race, nos, none = (PT[k] for k in INJ5)
    out = []
    rc1 = nos == 0
    out.append(('RC1 (F30p, item 665 (v)(1)): at T rts_inj_nos %d = 0' % nos, rc1,
                None if rc1 else 'RC1 (F30p): rts_inj_nos %d > 0 at T - code or instrument, NOT_ADMITTED, series stop, the lead item '
                                 '(item 665 (g))' % nos))
    dev = s + race + nos - inj
    rc2 = abs(dev) <= TOL_INJ
    out.append(('RC2 (F30p, item 665 (v)(2)): at T rts_inj_s %d + rts_inj_race %d + rts_inj_nos %d = rts_inj %d (difference %+d, '
                'tolerance %d on the tail)' % (s, race, nos, inj, dev, TOL_INJ), rc2, None))
    rc3 = (PT['rts_bad_s'] >= s - TOL_INJ and PT['rts_bad'] >= s - TOL_INJ and PT['rts_race'] >= race - TOL_INJ)
    out.append(('RC3 (F30p, item 665 (v)(3)): at T rts_bad_s %d >= rts_inj_s %d, rts_bad %d >= rts_inj_s, rts_race %d >= rts_inj_race %d '
                '(tolerance %d on the tail)' % (PT['rts_bad_s'], s, PT['rts_bad'], PT['rts_race'], race, TOL_INJ), rc3, None))
    q = PT['rts_pb'] // INJ_EVERY
    rc4 = q - TOL_INJ <= inj + none <= q + TOL_INJ
    out.append(('RC4 (F30p, item 665 (v)(4)): at T floor(rts_pb %d / %d) = %d; %d - 1 <= rts_inj %d + rts_inj_none %d = %d <= %d + 1' % (
        PT['rts_pb'], INJ_EVERY, q, q, inj, none, inj + none, q), rc4, None))
    if kind == 'c6':
        if inj >= 1:
            okm, row, st = True, 'rts_inj %d >= 1' % inj, None
        elif none >= 1:
            okm, row, st = True, 'rts_inj 0 and rts_inj_none %d >= 1 - the form found no target, K_S of the scene not live (data, item 665 ' \
                                 '(v)(4))' % none, None
        else:
            okm, row = False, 'rts_inj 0 and rts_inj_none 0 (rts_pb %d) - code defect' % PT['rts_pb']
            st = 'rts_inj = 0 with rts_inj_none = 0 at T (rts_pb %d) - code defect, series stop, the lead item (item 664 (z)(3), 665 ' \
                 '(v)(4))' % PT['rts_pb']
        out.append(('(inj) form member c6 (item 664 (z)(3), 665 (v)(4)): at T %s' % row, okm, st))
    return out


def read_tag(tag, p):
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
    x = scan(p['log'], level) if have_log else None
    ebad = env_diff(dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_'))), expected_env(scene, kind))
    hold = HOLD[kind]
    sdth = stdout_death(p['stdout'])
    vv = 'true' if kind == 'w6' else 'false'
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
        ('json binary_sha256 = T3 50596951 (%s)' % (jbin or '-')[:16], jbin == BIN_T, 'harness'),
        ('installed during the tag = T3 50596951 (%s)' % (inst_t or '-')[:16], inst_t == BIN_T, 'harness'),
        ('installed before = after = FS11 ea51ae80 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_INST and inst_a == BIN_INST, 'harness'),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha,
         'harness'),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad, 'harness'),
        ('gate text and schedule empty - no rtskip, no census gate (%r / %r)' % (((run or {}).get('gates') or '')[:40],
                                                                            ((run or {}).get('schedule') or '')[:40]),
         run is not None and not (run.get('gates') or '').strip() and not (run.get('schedule') or '').strip(), 'harness'),
        ('last --vulkan-validation %s (%s)' % (vv, last_flag(cmd, '--vulkan-validation')), last_flag(cmd, '--vulkan-validation') == vv,
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
    dref = []
    stop = []
    rec = None
    PTs = new_sums()
    if x is not None:
        P, W = x['proc'], x['win']
        mv = [v for v, l in x['modes']]
        d1 = mv.count(knob) == 1 and all(v == knob for v in mv) and x['mode_any'] == len(mv)
        d2 = x['refused'] == 0 and P['rts_refuse'] == 0
        d3 = all(v == knob for v, l in x['gates'])
        d4 = P['rts_xthr'] == 0 and P['rts_acqw'] == 0
        d5 = x['x_win'] >= X_SHARE * x['draw_win'] and x['x_win'] >= X_MIN[knob]
        d6 = W['rts_ovf'] == 0
        fork_ok = len(x['fork']) == 1 and x['fork'][0] == FORK_T
        ver_ok = x['ver_bad'] == 0
        d7 = lsha == BIN_T and jbin == lsha and fork_ok and bin_ver is True and ver_ok
        rows_d = [('(D1) exactly one line RtSkip: mode 6 ctx_slots=<n> groups=<n> rec_bytes=<n> (the text of the print place, item 665 (v)(5)), '
                   'no other value, no other text (%s; lines with the prefix %d)' % (x['modes'][:4], x['mode_any']), d1, True),
                  ('(D2) RtSkip: refused lines %d, process rts_refuse %d' % (x['refused'], P['rts_refuse']), d2, kind == 'c6'),
                  ('(D3) Gate: rtskip= lines none or all %d (%s)' % (knob, x['gates'][:4]), d3, kind == 'c6'),
                  ('(D4) process rts_xthr %d, rts_acqw %d' % (P['rts_xthr'], P['rts_acqw']), d4, kind == 'c6'),
                  ('(D5) FrameTrace-x in the window %d >= 0.95 x FrameTrace-draw %d and >= %d' % (x['x_win'], x['draw_win'], X_MIN[knob]), d5,
                   kind == 'c6'),
                  ('(D6) window rts_ovf %d' % W['rts_ovf'], d6, kind == 'c6'),
                  ('(D7) RC5 of F30p (item 665 (v)(5)): launch_sha256 %s = T3, binary_sha256 = launch_sha256 (%s), one log line version: Fork '
                   'build ... ea38426 (%s), version string -1908-gea38426b in the pinned copy of sha T3 (%s), log version strings %d of them '
                   'other than -1908-gea38426b %d' % ((lsha or '-')[:16], (jbin or '-')[:16], x['fork'], bin_ver, x['ver_any'], x['ver_bad']),
                   d7, True),
                  ('RC4 (F30f) / RC2 (F30l) / RC2 (F30p) every FrameTrace-x line carries every field of REQ incl. the 8 bit counters and the 5 '
                   'rts_inj names (lines %d, missing %d %s) - else missing field' % (x['x_lines'], x['x_missing'], x['x_missing_names'][:3]),
                   x['x_missing'] == 0 and x['x_lines'] > 0, True)]
        for a, b, is_member in rows_d:
            (d if is_member else dref).append((a, b))
        if kind == 'w6':
            res['w6_variant_d2_d6'] = all(b for a, b in dref)
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
                  '%d / rts_bad %d; prefix sums within %d events at every line incl. the tail (item 659 (v), 662 (v)(4)) (chk/pa, chk_b/pb %d; '
                  'rx/b/bad %d; first line %s); chk_b <= chk <= n %d, noreg %d <= bad; RtSkipVerify lines %d <= min(40, bad); unparsable %d; '
                  'duplicate fields %d; letter rows (per line, reference - the flip tears one event): chk!=pa %d, chk_b!=pb %d, rx<=b<=bad '
                  'broken %d; max prefix deviation %s; lines with prefix deviation >= 2 (item 659 (v), reference) %s' % (
                      close_txt, 'ok' if close_ok else 'NO',
                      P['rts_chk'], P['rts_pa'], P['rts_chk_b'], P['rts_pb'], P['rts_bad_rx'], P['rts_bad_b'], P['rts_bad'], PRE_TOL,
                      x['pre_viol'], x['pre_viol_rx'], x['pre_first'], P['rts_n'], P['rts_bad_noreg'], x['verify'], x['mm_bad'], x['x_dup'],
                      x['id_pa'], x['id_pb'], x['id_rx'], json.dumps(x['maxdev'], sort_keys=True),
                      json.dumps(x['dev2'], sort_keys=True)), parse_ok))
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
        rc4 = P['rts_bad_noreg'] == P['rts_bad']
        d.append(('RC4 (F30l): value 6 != 3 - process rts_bad_noreg %d = rts_bad %d' % (P['rts_bad_noreg'], P['rts_bad']), rc4))
        if scene == 's9':
            d.append(('S9 window end: last FrameTrace n %s >= %d (item 649 (d); presents of the InputScript lines - max %s, lines %d)' % (
                x['ft_last_n'], S9_N_MIN, x['input_max'], x['input_lines']), (x['ft_last_n'] or 0) >= S9_N_MIN))
        rec = reconcile(x, P, knob)
        res['rec'] = rec
        d.append(('reconciliation (%s): lines MISMATCH mode=%d %d, process rts_bad %d; lines %s against rts_bad_rx %d, rts_bad_b %d, r %d, s %d, '
                  'p %d, m %d, l %d, xr+xc+xe %d' % ('exact' if rec['exact'] else 'lines exhausted - >=', knob, rec['n'], P['rts_bad'],
                                                     json.dumps(rec['lines'], sort_keys=True), P['rts_bad_rx'], P['rts_bad_b'],
                                                     P['rts_bad_r'], P['rts_bad_s'], P['rts_bad_p'], P['rts_bad_m'], P['rts_bad_l'],
                                                     rec['x3']), rec['ok']))
        if rec['exact'] and not rec['ok']:
            stop.append('reconciliation failed with the lines not exhausted - item 649 (v)')
        im = inj_members(PTs, kind) if close_ok else [('RC1-RC4 (F30p): no closing point T within %d lines - not read' % CLOSE_MAX, False, None)]
        okv = {}
        for a, b, st in im:
            d.append((a, b))
            okv[a.split(' (')[0] if a.startswith('RC') else a.split(' ')[0]] = b
            if st:
                stop.append(st)
        if x['refused'] > 0:
            stop.append('RtSkip: refused line (%d)' % x['refused'])
        if not d4:
            stop.append('(D4) != 0: rts_xthr %d rts_acqw %d' % (P['rts_xthr'], P['rts_acqw']))
        p_rc = dict((a.split(':')[0], b) for a, b, st in im)
        inst = [nm for nm, v in (('RC1 (F30l)', rc1), ('RC2 (F30l)', r2), ('RC4 (F30l)', rc4), ('(D7)', d7),
                                 ('RC2 (F30p, item 665 (v)(2))', p_rc.get('RC2 (F30p, item 665 (v)(2))')),
                                 ('RC3 (F30p, item 665 (v)(3))', p_rc.get('RC3 (F30p, item 665 (v)(3))')),
                                 ('RC4 (F30p, item 665 (v)(4))', p_rc.get('RC4 (F30p, item 665 (v)(4))')))
                if v is False]
        if inst:
            stop.append('instrument member broken: %s - NOT_ADMITTED and series stop (executor variant: the next tag of the same binary and '
                        'form gives the same defect; the lead item)' % ', '.join(inst))
    adm_rows = [(a, bool(b)) for a, b, k in harness] + [(a, bool(b)) for a, b in d]
    res['admission'] = [[a, b] for a, b in adm_rows]
    res['reference_rows'] = [[a, bool(b)] for a, b in dref]
    failed_h = [(a, k) for a, b, k in harness if not b]
    failed_d = [a for a, b in d if not b]
    interference = [a for a, k in failed_h if k == 'interference']
    binary_bad = [a for a in failed_d if a.startswith(('RC4 (F30f)', '(D7) ', 'RC1 (F30l)', 'RC2 (F30l)', 'RC4 (F30l)', 'RC1 (F30p',
                                                         'RC2 (F30p', 'RC3 (F30p', 'RC4 (F30p', '(inj)', '(D1) '))]
    if binary_bad:
        status = 'NOT_ADMITTED'   # a wrong binary, a lost field or a broken instrument member is not a run disturbance
    elif interference:
        status = 'INTERFERENCE'
    elif failed_h or failed_d:
        status = 'NOT_ADMITTED'
    else:
        status = 'ADMITTED'
    res['status'] = status
    res['admitted'] = status == 'ADMITTED'
    res['why'] = None if status == 'ADMITTED' else (binary_bad + [a for a, k in failed_h] + failed_d)[:4]
    res['members'] = None
    res['ref'] = dict(outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'), stable_s=att.get('stable_s'),
                      win_s=win_s, lines=X.get('lines'), death=(X.get('death') or []) + sdth,
                      fork=X.get('fork'), x_prefixed=X.get('x_prefixed'), ineq_lines=X.get('ineq_lines'), ft_last_n=X.get('ft_last_n'),
                      input_lines=X.get('input_lines'), input_max=X.get('input_max'), prefix_maxdev=X.get('maxdev'),
                      prefix_dev2=X.get('dev2'), close_idx=X.get('close_idx'), close_ln=X.get('close_ln'), close_dist=X.get('close_dist'),
                      x_full=X.get('x_full'), tail_dev=X.get('tail_dev'))
    if x is not None:
        P, W = x['proc'], x['win']
        res['proc'] = dict(P)
        res['win'] = dict(W)
        res['at_t'] = dict(PTs)
        res['verify_lines'] = x['verify']
        bits_cnt = {}
        for m in x['mm']:
            kk = '0x%03x' % m['bits']
            bits_cnt[kk] = bits_cnt.get(kk, 0) + 1
        res['mm_bits'] = bits_cnt
        res['mm6_s_lines'] = sum(1 for m in x['mm'] if m['mode'] == 6 and m['bits'] & 0x040)
        res['d5'] = [x['x_win'], x['draw_win']]
        md = mode_member(x)
        res['bda'] = md
        res['kappa'] = kappa_rows(x, level, md['mode'], kref(p['kref']))
        res['b42'] = b42_window(x)
        res['b_minus_rx'] = P['rts_bad_b'] - P['rts_bad_rx']
        res['inj'] = dict(at_t=dict((k, PTs[k]) for k in INJ5), proc=dict((k, P[k]) for k in INJ5),
                          natural_s_at_t=PTs['rts_bad_s'] - PTs['rts_inj_s'], natural_s_proc=P['rts_bad_s'] - P['rts_inj_s'],
                          others_proc=dict((SRC_NAME[k], P[k]) for k in BITS8 if k != 'rts_bad_s'))
        ks = PTs['rts_inj'] >= 1 and PTs['rts_inj_s'] >= 1 and PTs['rts_inj_nos'] == 0
        res['ks_row'] = ("K_S row (item 664 (i)(1) with item 665 (g)): at T rts_inj %d >= 1, rts_inj_s %d >= 1, rts_inj_nos %d = 0 - %s (row "
                         "for F30r, not a verdict)" % (PTs['rts_inj'], PTs['rts_inj_s'], PTs['rts_inj_nos'], 'YES' if ks else 'NO'))
        res['ks'] = ks
        m = []
        if kind == 'w6':
            g = x['first_guest_ln']
            dual = [dd for dd in x['dual'] if dd[0] and g is not None and dd[1] < g]
            death = (x['death'] or []) + sdth
            m += [('lived to the end of the hold from the entry line (outcome %s, hold_exit %s, window %s >= %d)' % (
                       att.get('outcome'), att.get('hold_exit'), win_s, hold), lived),
                  ('0 death markers (log and stdout) %s' % death[:3], not death),
                  ('0 [Vulkan][E] (%d)' % x['vke'], x['vke'] == 0),
                  ('positive control: [Vulkan][W] %d > 0' % x['vkw'], x['vkw'] > 0),
                  ('DualSrcBlend: supported=1 enabled=1 before the first GuestOut (%d)' % len(dual), bool(dual)),
                  ('0 limit lines of the layer (%d) - form 295 (b)' % x['vk_limit'], x['vk_limit'] == 0),
                  ('sum at T rts_inj %d >= 1 (item 664 (z)(2))' % PTs['rts_inj'], PTs['rts_inj'] >= 1)]
            if x['vke'] > 0 or not lived:
                stop.append('w6: [Vulkan][E] %d or the process did not live to the end of the hold (%s) - series stop and the lead item (item '
                            '664 (z)(2))' % (x['vke'], att.get('outcome')))
        res['members'] = [[a, bool(b)] for a, b in m]
    res['stop'] = stop
    if res['members'] and not all(b for a, b in res['members']) and res['status'] == 'ADMITTED':
        res['status'] = 'NOT_ADMITTED'
        res['admitted'] = False
        res['why'] = [a for a, b in res['members'] if not b][:4]
    return res


def rows_out(res):
    out = ['tag %s (scene %s, kind %s, knob %d, level %s)  reader sha256 %s' % (res['tag'], res['scene'], res['kind'], res['knob'],
                                                                                 res['level'], res['reader_sha256'])]
    out.append('  STATUS %s%s' % (res['status'], '' if not res['why'] else ' - %s' % res['why']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    for a, b in res.get('reference_rows') or []:
        out.append('    [ref %s] %s' % ('ok' if b else 'NO', a))
    if res['kind'] == 'w6' and 'w6_variant_d2_d6' in res:
        out.append('  executor variant (item 664 (z)(2) names the w6 members): (D2)-(D6) as members of w6 - %s' % (
            'all ok' if res['w6_variant_d2_d6'] else 'NO'))
    out.append('  launch_sha256 %s; binary_sha256 %s' % (res['launch_sha256'], res['binary_sha256']))
    if res['members']:
        out.append('  MEMBERS %s' % res['kind'])
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
    if res.get('proc') is not None:
        pr, wn, at = res['proc'], res['win'], res['at_t']
        keys = ('rts_n', 'rts_skip', 'rts_pa', 'rts_pb', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx',
                'rts_race', 'rts_lost')
        out.append('  INJ (item 664 (z)(4)) at T %s | process %s' % (' '.join('%s=%d' % (k, at[k]) for k in INJ5),
                                                                       ' '.join('%s=%d' % (k, pr[k]) for k in INJ5)))
        out.append('  natural S = rts_bad_s - rts_inj_s: at T %d, process %d (reference, item 664 (i)(5))' % (
            res['inj']['natural_s_at_t'], res['inj']['natural_s_proc']))
        out.append('  %s' % res['ks_row'])
        out.append('  PROCESS %s' % ' '.join('%s=%d' % (k, pr[k]) for k in keys))
        out.append('  AT T    %s' % ' '.join('%s=%d' % (k, at[k]) for k in keys))
        out.append('  WINDOW  %s' % ' '.join('%s=%d' % (k, wn[k]) for k in keys))
        out.append('  BITS process %s; rts_bad_b - rts_bad_rx = %d' % (' '.join('%s=%d' % (k, pr[k]) for k in BITS8), res['b_minus_rx']))
        out.append('  XB process %s (H1 of F30p: rts_xb_ser at =6 - reference, not a basis)' % ' '.join('%s=%d' % (k, pr[k]) for k in XB_ALL))
        out.append('  RtSkipVerify lines %d, bits %s; MISMATCH mode=6 with bit 0x040: %d (reference of RC3)' % (
            res['verify_lines'], json.dumps(res['mm_bits'], sort_keys=True), res['mm6_s_lines']))
        out.append('  BDA %s' % json.dumps(res['bda'], sort_keys=True))
        out.append('  KAPPA (reference; [0.80; 1.25]) %s' % json.dumps(res['kappa'], sort_keys=True))
        out.append('  FIXB42 window increments %s; window rts_lost %d' % (json.dumps(res['b42'], sort_keys=True)[:600], wn['rts_lost']))
    if res.get('rec') is not None:
        out.append('  RECONCILIATION %s' % json.dumps(res['rec'], sort_keys=True))
    out.append('  REFERENCE %s' % json.dumps(res['ref'], sort_keys=True))
    out.append('  STOP %s' % ('none' if not res['stop'] else '; '.join(res['stop'])))
    return out


def latest(reads, base):
    """The latest made attempt of a tag base (a repeat _r<n> made by the lead's item replaces the interfered tag)."""
    best = None
    for rep in ('', '_r1', '_r2', '_r3'):
        if base + rep in reads:
            best = reads[base + rep]
    return best


def scene_rows(reads):
    """reads: {tag: read.json} -> rows for F30r (item 664 (i)); not a verdict."""
    out = []
    w = latest(reads, 'f30_s1_w6')
    out.append('w6 f30_s1_w6: %s; members %s' % ((w or {}).get('status', '-'),
                                                ('all YES' if w and w.get('members') and all(b for a, b in w['members'])
                                                 else [a[:50] for a, b in ((w or {}).get('members') or []) if not b][:3] or '-')))
    live = []
    for k in range(1, 10):
        sc = 's%d' % k
        r = latest(reads, 'f30_%s_c6' % sc)
        adm = r is not None and r.get('status') == 'ADMITTED'
        ks = adm and r.get('ks')
        if ks:
            live.append(sc)
        inj = (r or {}).get('inj') or {}
        out.append('%s %s: c6 %s; K_S %s; at T %s; natural S (process) %s' % (
            sc, SCENES[sc][0], (r or {}).get('status', '-'), ks if adm else 'not read', json.dumps(inj.get('at_t'), sort_keys=True),
            inj.get('natural_s_proc')))
    out.append('scenes s1..s9 with K_S YES %d (%s); S1 or S9 among them %s; cymbal_party_land - natural K_B\'\' of F30m (item 664 (b)), '
               'not a tag of this series - rows for F30r by item 664 (i)(2)-(4) with item 665 (g)' % (
                   len(live), ' '.join(live) or '-', any(s in ('s1', 's9') for s in live)))
    return out


def table(rd):
    out = ['| tag | status | launch sha | (D5) x/draw | inj | inj_s | inj_race | inj_nos | inj_none | rts_bad | r xr xc xe s p m l | '
           'xb_ser | race | win chk_b | K_S | stop |', '|' + '---|' * 16]
    reads = {}
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                reads[t] = r
                pr = r.get('proc') or {}
                at = r.get('at_t') or {}
                wn = r.get('win') or {}
                out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                    t, r['status'], (r.get('launch_sha256') or '-')[:8], '%s/%s' % tuple(r.get('d5') or ['-', '-']),
                    at.get('rts_inj', '-'), at.get('rts_inj_s', '-'), at.get('rts_inj_race', '-'), at.get('rts_inj_nos', '-'),
                    at.get('rts_inj_none', '-'), pr.get('rts_bad', '-'), ' '.join(str(pr.get(k, '-')) for k in BITS8),
                    pr.get('rts_xb_ser', '-'), pr.get('rts_race', '-'), wn.get('rts_chk_b', '-'), r.get('ks', '-'),
                    '; '.join(r.get('stop') or []) or '-'))
    out += [''] + scene_rows(reads)
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader f30q_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        if not TAG_RX.match(tag):
            print('usage: f30q_read.py <tag> | --dir D --tag T | --table')
            return 2
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        if not TAG_RX.match(tag):
            print('usage: f30q_read.py <tag> | --dir D --tag T | --table')
            return 2
        p = paths(tag)
    if js and p.get('run') and os.path.normcase(os.path.abspath(js)) == os.path.normcase(os.path.abspath(p['run'])):
        # item 662: the json of the run (enter_scene) is evidence of the harness members - never overwritten by the reader
        print('refused: --json %s is the run json of the tag' % js)
        return 2
    res = read_tag(tag, p)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
