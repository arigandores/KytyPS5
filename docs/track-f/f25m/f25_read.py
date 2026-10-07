"""Track F link F25f (HPP-669; ROADMAP s122 item 596 (g)-(z) with the amendments of item 599 (b)(1)-(7), (10), (11), (v) RC13-RC14,
item 600 (b)(4) and item 602 (v)(2)): the reader of the B36 / B40 series on the test binary B e342b839 (S18 0005e11f + 5 KYTY_DIAG_B32
commits + F25 C1-C6, 35b454c6) - prewarms f25_c1 / f25_c2, controls f25_z1 / f25_z2 / f25_pb / f25_pc, the warm series f25_s01..f25_s40
(levels pot_treasure_cave and bonus_path_maker_mix) and the cold layer f25_k01..f25_k10.  Port of e8ea0a57:docs/track-f/f20l3/b32_read.py.
NO VERDICT - the reading is F25g (lead).  theta_load is read from the seal (line 'theta_load: <x>', 0.4562).  ASCII only.

    python f25_read.py <tag> [--json <out>]                        one tag (files of C:/kyty/f287/f25f)
    python f25_read.py --dir <fixture dir> --tag <tag> [--json <out>]
                                                                    fixture form: log.txt, es.json, rec.idx, glitch.txt, m6.txt, cal.txt,
                                                                    installed_before.txt, installed_after.txt, manifest_cmp.txt,
                                                                    snap_cmp.txt, noreturn.txt, seal.md
    python f25_read.py --table [--runs <dir>]                       the table over every runs/<tag>/read.json
    python f25_read.py --series [--runs <dir>]                      controls, the series by level (stop rule of item 596 (e)), the
                                                                    cold layer (zh), U5 (z), the budget
    python f25_read.py --check-seal [--seal <md>]                   every 'seal: <sha256> <path>' line against the file

ATTRIBUTION of a frame (B5 / B33 / B1b / 'prio only' / 'nothing') - the F20c reader as is: f20e_read.py (copy, sha256 F20E_SHA, checked),
functions scan, attr, evaluate, with the level name as the parameter (the module constant SG is set to the level of the tag before scan;
item 596 (d)(1) 'the F20e definitions, the level name a parameter').  On binary B (not a binary before S12) the letter of F20c gives no B33
(a cache save is no attribution after S12) - the member 'not B5 / B33 / B1b' is kept by the letter (RC14) and has its own fixture.

THE RULE (item 596 (d) with item 599 (b)):
  hold frame      a scene frame with dt_us >= 100 000 that starts at >= 10 s of the scene (F20e definitions).
  key (d)(2)      the window of frame n: the DiagB32: line with n if its dt_us >= 0.5 x frame dt_us; else n + 1 under the same condition;
                  both qualify - the larger dt_us; none - NO_SAMPLES:key.  One window keyed by two adjacent hold frames - flag SHARED_WIN
                  (reference; K counts the hold, not the frame).  The key comes FIRST (RC11).
  K2 frame        dt_us >= 1 000 000; F20c attribution not B5 / B33 / B1b (those - reference).  dt_us - instr_us(key window) < 1 000 000
                  -> INSTR_MADE_K2 (in K_I, not in K).  NO_SAMPLES:key -> in K with that class.  Frames 100 ms - 1 s - reference, the
                  same rule; 'precursor' - such a frame (not B5 / B33 / B1b) starting within 5 s before a frame in count.
  class (first match), of the key window:
   (0a)  NO_SAMPLES:cover   window dt_us > 20 475 000 ((kHist - 1) x P, item 599 (b)(3)); its invariants are reference
   (0b)  NO_SAMPLES:trunc   a field or line is absent (item 599 (b)(4)): no -x line; a field of ZERO_W, hist_exh_w, w_cut_w, others_cut_w
                            absent; the last field of DiagB32: is not flip_ns / of -x is not others_cut_w; a -t line without peer=, a -w
                            line without peer_tid= (the buffer of 1 024 B); a header field dt_us, cover_us, sgap_max_us absent
   (0c)  NO_SAMPLES:cover   hist_exh_w >= 1 (item 599 (b)(1))
   (0d)  NO_SAMPLES:trunc   hist_exh_w = 0 and dt_us - cover_us > sgap_max_us + 1 (the agreement, item 599 (b)(1))
   (i)   HOST_FREEZE        sgap_max_us >= 0.5 x E (E = frame dt - median dt of the 20 nearest scene frames < 100 ms)
   (ii)  NO_SAMPLES         i2 != 1, samples = 0, or a zero invariant of the window != 0: ZERO_W + hist_exh_w + w_cut_w + others_cut_w
                            (others_cut_w - item 599 (b)(9))
   (iii) HOST_LOAD          other_us >= theta_load x ncpu x window
   (iv)  the chain of item 550 (g)(2)(iv) with RC6, RC7, items 574 (d), 581 (v)(5) - unchanged from b32_read.py
   abort                    a tag with 'GpuHangAbort:' after >= 10 s of the scene: the hold is in N_L with one frame in count of
                            class NO_SAMPLES:abort (item 599 (b)(2)); before 10 s - interference.
  M6_BURST (d)(5)  an M6 sample with foreign >= 8.0 CPU s/s in [window start - 1.5 s; window end + 1.5 s]; the window is put on the M6
                  QPC scale by an offset calibrated per tag (item 600 (b)(4)): offset = min over the printed windows n of (QPC of the
                  first sight of the line 'FrameTrace: n=<n>' in the live log by the harness poller - flip_ns of window n); the line is
                  printed after OnFlip(n) in the same flip call, so every pair is >= the offset.  No pair - NOT_DETERMINED.  A flag.
  FORM (d)(5)     FORM_SEM: FrameTrace semwait_us >= 0.5 x dt_us; FORM_NOFLIP: FlipHold other_us (interval of the frame) >= 0.5 x dt_us
                  and not FORM_SEM; else FORM_OTHER.  A label.
SERIES (e) per level L over the admitted warm series tags: N_L holds, K_L holds with a frame in count, K_I_L holds with a K2 frame not
  attributed (in count or INSTR_MADE_K2).  N_L < 5 - CONTINUE; K_L >= 3 - STOP_READ; K_L = 0: N_L < 14 - CONTINUE, N_L >= 14 - STOP_U2
  (K_I_L = 0) or STOP_552G (K_I_L >= 1); K_L 1..2: CONTINUE up to K_L 3 (STOP_READ) or N_L 20 (STOP_U2PRIME).  Class of a hold - class of
  its longest frame in count.  NOT WARM (item 599 (b)(7)): a tag failing only the warm member is read in the layer N_nw_L / K_nw_L (not in
  N_L, K_L) and spends one of the 6 interference places; two NOT WARM tags of a level with one program hash -> STOP_LEVEL_Q (question).
COLD LAYER (zh) per level after both warm series: f25_kNN admitted cold tags; stop at the first tag with a frame in count or at 5 tags.
U5 (z, item 599 (b)(3), item 602 (v)(2)): over the printed windows of a tag with dt_us <= 20 475 000: a nonzero zero invariant, a trunc
  item or a broken agreement; sgap_bad_w of the window right after (n - 1) a window with >= 20 000 closed wait records (no such field in
  the -x line of 35b454c6 - the number of -w lines of window n - 1 is taken) is a reference line, not U5.  U5(4): >= 2 series tags.
INTERFERENCE: a failed admission member; budget 66 tags, interference (with NOT WARM) <= 6, the 7th - STOP_INTERFERENCE.
"""
import hashlib
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f20e_read as F  # noqa: E402  (the F20c reader of F20e, unchanged)

F20E_SHA = '5a986c03d161b9a5c52d589ad1da87e4676ceb9bac61acaeaa8f2131525400fa'
G = 'C:/kyty/f287/f25f'
SEAL_PATH = G + '/pred/f25f_seal.md'
THETA_RX = re.compile(r'^theta_load: ([0-9]+\.[0-9]+)[ \t]*$', re.M)
SLOW_US = 100000
K2_US = 1000000
SHORT_US = 70000
WIN_US = 10000000
ENV_US = 20475000            # (kHist - 1) x P = 4 095 x 5 000, item 599 (b)(3)
PRE_US = 5000000             # precursor window, item 596 (d)(1)
NEIGH = 10
HOLD_S = 330
HANG_ABORT = '22'            # item 599 (b)(2)
M6_FOREIGN = 8.0
M6_PAD_NS = 1500000000
H2_REC = 20000               # item 602 (v)(2)
N_MIN, N_MID, N_MAX, K_STOP = 5, 14, 20, 3
COLD_MAX = 5
BUDGET_TAGS, BUDGET_INTERF = 66, 6
BIN_B = 'e342b839d74d5689bc4f66ee0ed04a37e9a640e60a199a2882c8e83ecf19cfa4'     # binary B of F25d, items 600, 602
BIN_INST = 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a'   # installed S18 (item 590), before = after
SIG_B = '9177b4267de1fb8bac7d1113afd8733210addfac'                               # = S18 (item 600 (a))
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
HARN = {'KYTY_FRAME_TRACE', 'KYTY_GPU_HANG_ABORT_S', 'KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE', 'KYTY_QUEUE_TRACE', 'KYTY_GPU_CLOCK_PIN',
        'KYTY_GPU_MARKERS', 'KYTY_GUEST_ARGS', 'KYTY_REC'}
POT, BONUS = 'pot_treasure_cave', 'bonus_path_maker_mix'
LEVELS = (POT, BONUS)
FIXED_LEVEL = {'f25_c1': POT, 'f25_c2': BONUS, 'f25_z1': POT, 'f25_z2': BONUS, 'f25_pb': POT, 'f25_pc': BONUS}
TAG_RX = re.compile(r'^(f25_c[12]|f25_z[12]|f25_p[bc]|f25_s(?:0[1-9]|[1-3][0-9]|40)|f25_k(?:0[1-9]|10))(_r[1-6])?$')
STAND = {'f25_pb': '60:present:3000', 'f25_pc': '60:gpusleep:6000'}
STAND_MIN_US = {'f25_pb': 3000000, 'f25_pc': 6000000}
ZERO_W = ('slot_full_w', 'torn_w', 'ring_drop_w', 'sgap_bad_w', 'lines_cut_w', 'req_miss_w', 'sub_miss_w')
ZERO_F25 = ZERO_W + ('hist_exh_w', 'w_cut_w', 'others_cut_w')
DRIVER = ('present', 'acquire', 'qsubmit', 'semwait')
CALLS = ('present', 'acquire', 'qsubmit', 'qlock', 'drain', 'semwait', 'protect', 'fault')
# enum Wait of f2307b02 / 35b454c6 src/common/diagB32.h in order (WaitName), item 574 (g)(1), 581 (v)(5)
WAITS = ('cond', 'mutex', 'sem', 'psem', 'evf', 'eq', 'sleep', 'gpu_idle', 'gpu_regmem',
         'emu_mutex', 'gpu_wait', 'gpu_cmd', 'flip_slot', 'flip_done', 'flip_cancel', 'flip_req', 'vo_pace', 'relay', 'frame_pool',
         'rec_wait', 'rec_idle', 'asub_idle', 'asub_drain', 'ops_wait', 'ops_idle', 'pipe_wait', 'pcopy', 'pm_drain', 'vma_flush',
         'rec_queue', 'main_task', 'main_idle', 'spin', 'av',
         'vblank', 'once', 'join', 'addr', 'aio', 'fiber', 'audio', 'ult', 'net', 'rwlock', 'emu_join')
EMU_WAITS = WAITS[9:34] + ('vblank', 'audio', 'aio', 'net', 'emu_join')
GUEST_WAITS = WAITS[:9] + ('once', 'join', 'addr', 'fiber', 'ult', 'rwlock')
NAME_OK = re.compile(r'^[A-Za-z0-9_.-]{1,31}$')
FTX = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) lat_us=(\d+)')
GBUSY = re.compile(rb' gpu_busy_us=(\d+)')
CPUG = re.compile(rb' cpu_gpu_us=(\d+)')
SEMW = re.compile(rb' semwait_us=(\d+)')
FHOLD = re.compile(rb'^FlipHold: .*? other_us=(\d+)')
RHASH = re.compile(rb'^ShaderRecompiler \S+ phase begin: .*?hash=0x([0-9a-fA-F]+)')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
PRECACHE_RECIPES = re.compile(rb'^PipelinePrecache: \d+ recipes ')
GCN = re.compile(rb'[0-9a-fA-F]+: [A-Z]_')
LAST_KEY = {'hdr': 'flip_ns', 't': 'peer', 'w': 'peer_tid', 'x': 'others_cut_w'}
HDR_NEED = ('dt_us', 'cover_us', 'sgap_max_us', 'flip_ns')
GROUP_I = ('NO_SAMPLES', 'UNMARKED', 'UNDETERMINED')
GROUP_III = ('HOST_FREEZE', 'HOST_LOAD', 'HOST_PREEMPT', 'DRV_HOST')
RX_M6 = re.compile(r' t=([0-9.]+) emu_t=(-?[0-9.]+|-) qpc_ns=(\d+) game=([0-9.]+) loader=([0-9.]+) foreign=([0-9.]+)')
RX_CAL = re.compile(r'^CAL qpc_ns=(\d+) n=(\d+)')


def sha_file(path):
    return F.sha_file(path)


def kv(line):
    """'DiagB32-t: n=1 a=2 ...' -> (dict of str, last key); the first token (prefix) is skipped."""
    d = {}
    last = None
    for tok in line.split(' ')[1:]:
        k, s, v = tok.partition('=')
        if s:
            d[k] = v
            last = k
    return d, last


def num(v, default=None):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def klist(v):
    out = {}
    if not v or v == '-':
        return out
    for part in v.split(','):
        k, _, c = part.rpartition(':')
        out[k] = out.get(k, 0) + (num(c, 0) or 0)
    return out


def parse_diag(raw):
    """raw: list of (kind, text) of one n -> dict hdr / t / w / c / x / last (kind -> list of last keys)."""
    d = dict(hdr=None, t=[], w=[], c=[], x=None, dup=0, last=dict(hdr=[], t=[], w=[], x=[]))
    for kind, text in raw:
        f, last = kv(text)
        if kind in d['last']:
            d['last'][kind].append(last)
        if kind == 'hdr':
            if d['hdr'] is not None:
                d['dup'] += 1
                continue
            d['hdr'] = dict((k, num(v, v)) for k, v in f.items())
        elif kind == 't':
            r = dict((k, num(v, v)) for k, v in f.items())
            r['W'] = klist(f.get('W'))
            r['H'] = klist(f.get('H'))
            r['SwR'] = klist(f.get('SwR'))
            d['t'].append(r)
        elif kind == 'w':
            d['w'].append(dict((k, num(v, v)) for k, v in f.items()))
        elif kind == 'c':
            d['c'].append(dict((k, num(v, v)) for k, v in f.items()))
        elif kind == 'x':
            if d['x'] is not None:
                d['dup'] += 1
                continue
            d['x'] = dict((k, num(v, v)) for k, v in f.items())
    return d


def scan_b32(path, level):
    """One pass: FrameTrace fields, the interval data of every FrameTrace line (FlipHold other_us, dump program hashes), DiagB32* lines
    keyed by n, stand / death / window / seed / precache lines."""
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    ft = {}
    ivl = {}
    diag = {}
    lvl = ('Level has started: %s' % level).encode()
    r = dict(ft=ft, ivl=ivl, diag=diag, mode=[], invalid=[], test=[], recovering=0, minimized=0, diag_lines=0, diag_bad_prefix=0,
             ft_order=[], sig=[], variant_dir=[], precache_no=0, precache_recipes=0, seed_other=[], lvl_after_n=None, abort_after_n=None,
             abort_line=None, death=[], replay_skipped=0)
    last_n = None
    cur = dict(fh=0, hashes=[])
    for line in fh:
        if line.startswith(b'FrameTrace: n='):
            m = FTX.match(line)
            if m:
                n = int(m.group(1))
                g = GBUSY.search(line)
                c = CPUG.search(line)
                s = SEMW.search(line)
                ft[n] = (int(m.group(2)), int(m.group(3)), int(g.group(1)) if g else None, int(c.group(1)) if c else None,
                         int(s.group(1)) if s else None)
                ivl[n] = cur
                cur = dict(fh=0, hashes=[])
                r['ft_order'].append(n)
                last_n = n
            continue
        if line.startswith(b'DiagB32'):
            r['diag_lines'] += 1
            t = line.decode('ascii', 'replace').rstrip('\r\n')
            if t.startswith('DiagB32: mode='):
                r['mode'].append(t[:300])
                continue
            if t.startswith('DiagB32: config'):
                r['invalid'].append(t[:200])
                continue
            kind = {'DiagB32: ': 'hdr', 'DiagB32-t: ': 't', 'DiagB32-w: ': 'w', 'DiagB32-c: ': 'c', 'DiagB32-x: ': 'x'}
            k = None
            for p, kk in kind.items():
                if t.startswith(p):
                    k = kk
                    break
            n = num(kv(t)[0].get('n')) if k else None
            if k is None or n is None:
                r['diag_bad_prefix'] += 1
                continue
            diag.setdefault(n, []).append((k, t))
            continue
        if b'DiagB32' in line:
            r['diag_bad_prefix'] += 1
        if line.startswith(b'FlipHold: '):
            m = FHOLD.match(line)
            if m:
                cur['fh'] = max(cur['fh'], int(m.group(1)))
            continue
        if line.startswith(b'ShaderRecompiler '):
            m = RHASH.match(line)
            if m and len(cur['hashes']) < 64:
                cur['hashes'].append(m.group(1).decode('ascii').lower())
            continue
        if line.startswith(b'ShaderSeed: compatibility=') and len(r['sig']) < 4:
            m = SEED.search(line)
            r['sig'].append(m.group(1).decode('ascii') if m else '?')
            continue
        if line.startswith(b'Shader translation cache: ') and len(r['variant_dir']) < 4:
            r['variant_dir'].append(line.decode('ascii', 'replace').strip().replace('\\', '/').rsplit('/', 1)[-1])
            continue
        if line.startswith(b'TestB32:'):
            r['test'].append(dict(text=line.decode('ascii', 'replace').strip()[:160], after_n=last_n))
            continue
        if line.startswith(b'PipelinePrecache: '):
            if line.startswith(b'PipelinePrecache: no '):
                r['precache_no'] += 1
            elif PRECACHE_RECIPES.match(line):
                r['precache_recipes'] += 1
            continue
        if line.startswith(b'ShaderSeed: ') and not line.startswith(b'ShaderSeed: compatibility='):
            if len(r['seed_other']) < 4:
                r['seed_other'].append(line.decode('ascii', 'replace').strip()[:120])
            continue
        if b'rebuild skipped reason=recipes_current' in line:
            r['replay_skipped'] += 1
        if r['lvl_after_n'] is None and lvl in line and line.rstrip(b'\r\n').endswith(lvl):
            r['lvl_after_n'] = last_n if last_n is not None else -1
        for dm in F.DEATH:
            if dm in line and len(r['death']) < 20:
                r['death'].append(dm.decode())
                if dm == b'GpuHangAbort:' and r['abort_after_n'] is None:
                    r['abort_after_n'] = last_n if last_n is not None else -1
                    r['abort_line'] = line[:160].decode('ascii', 'replace').strip()
        if b'Recovering Vulkan swapchain' in line:
            r['recovering'] += 1
        if b'Window ' in line and F.MINI.search(line):
            r['minimized'] += 1
    fh.close()
    r['diag'] = dict((n, parse_diag(v)) for n, v in diag.items())
    return r


def neighbours(frames, i):
    out = []
    j = i - 1
    while j >= 0 and len(out) < NEIGH:
        if frames[j][2] < SLOW_US:
            out.append(frames[j][1])
        j -= 1
    k = 0
    j = i + 1
    while j < len(frames) and k < NEIGH:
        if frames[j][2] < SLOW_US:
            out.append(frames[j][1])
            k += 1
        j += 1
    return out


def base_of(ft, ns):
    vals = [ft[n] for n in ns if n in ft]
    if not vals:
        return None
    gb = [v[2] for v in vals if v[2] is not None]
    return dict(dt=statistics.median(v[0] for v in vals), lat=statistics.median(v[1] for v in vals),
                gbusy=statistics.median(gb) if gb else None, k=len(vals))


def dominant(row, samples):
    half = 0.5 * samples
    hs = [(row['H'].get(c, 0), -i, c) for i, c in enumerate(CALLS) if row['H'].get(c, 0) >= half]
    if hs:
        return 'H', max(hs)[2]
    ws = [(row['W'].get(k, 0), -i, k) for i, k in enumerate(WAITS) if row['W'].get(k, 0) >= half]
    if ws:
        return 'W', max(ws)[2]
    for st in ('R', 'Sr', 'Sw', 'S'):
        if (num(row.get(st), 0) or 0) >= half:
            return st, None
    return None, None


def key_window(n, dt, diag):
    """Item 596 (d)(2): window n if its dt_us >= 0.5 x dt, else n + 1 under the same condition; both - the larger dt_us; none - None."""
    cand = []
    for k in (n, n + 1):
        d = diag.get(k)
        h = d['hdr'] if d else None
        if h is None:
            continue
        w = num(h.get('dt_us'))
        if w is not None and 2 * w >= dt:
            cand.append((w, -k, k))
    if not cand:
        return None
    return max(cand)[2]


def trunc_of(d):
    """Item 599 (b)(4): the absent fields and lines of a window (each one a NO_SAMPLES:trunc item)."""
    out = []
    h, x = d['hdr'], d['x']
    if h is None:
        return ['no DiagB32: line']
    for k in HDR_NEED:
        if k not in h:
            out.append('header without %s' % k)
    if d['last']['hdr'] and d['last']['hdr'][0] != LAST_KEY['hdr']:
        out.append('header last field %s' % d['last']['hdr'][0])
    if x is None:
        out.append('no -x line')
    else:
        for k in ZERO_F25:
            if k not in x:
                out.append('-x without %s' % k)
        if d['last']['x'] and d['last']['x'][0] != LAST_KEY['x']:
            out.append('-x last field %s' % d['last']['x'][0])
    nt = sum(1 for v in d['last']['t'] if v != LAST_KEY['t'])
    nw = sum(1 for v in d['last']['w'] if v != LAST_KEY['w'])
    if nt:
        out.append('%d -t lines without peer=' % nt)
    if nw:
        out.append('%d -w lines without peer_tid=' % nw)
    return out


def agreement_bad(h, x):
    """Item 599 (b)(1): hist_exh_w = 0 and dt_us - cover_us > sgap_max_us + 1."""
    if x is None or num(x.get('hist_exh_w'), 0) != 0:
        return False
    return (num(h.get('dt_us'), 0) or 0) - (num(h.get('cover_us'), 0) or 0) > (num(h.get('sgap_max_us'), 0) or 0) + 1


def zero_bad(x):
    return [k for k in ZERO_F25 if num(x.get(k), 0) != 0] if x is not None else []


def chain(d, holder, fr, b, e_us, steps=None):
    """Item 550 (g)(2)(iv) with RC6, RC7 and the amendment of item 574 (d) / 581 (v)(5) (b32_read.py of F20l3, unchanged)."""
    steps = [] if steps is None else steps
    how = 'holder'
    h = d['hdr']
    samples = h['samples']
    rows = dict((t['slot'], t) for t in d['t'])
    gpu = rows.get(h.get('gpu_slot'))
    path = []

    def guest_check(cls):
        if gpu is None:
            return 'UNDETERMINED', 'UNDETERMINED', 'no GuestGpu -t row for RC6'
        busy = (num(gpu.get('R'), 0) or 0) + sum(gpu['H'].values())
        reg = gpu['W'].get('gpu_regmem', 0)
        if busy < 0.5 * samples and reg < 0.5 * samples:
            return cls, cls.split(':')[0], ''
        return 'GUEST_POLL', 'GUEST_POLL', 'RC6: GuestGpu R+H %d, W:gpu_regmem %d of %d' % (busy, reg, samples)

    cur = holder
    visited = []
    for step in range(4):
        row = rows.get(cur)
        if row is None:
            return 'UNDETERMINED', 'UNDETERMINED', path, None, 'no -t row for slot %s' % cur
        visited.append(cur)
        steps.append(dict(slot=cur, name=row.get('name'), role=row.get('role'), R=num(row.get('R'), 0), Sw=num(row.get('Sw'), 0),
                          S=num(row.get('S'), 0), samples=samples, how=how))
        st, x = dominant(row, samples)
        path.append('%s(%s)%s' % (row.get('name'), row.get('role'), ('=' + st + (':' + x if x else '')) if st else '=none'))
        role = row.get('role')
        if st == 'H':
            if x in DRIVER:
                others = [t for t in d['t'] if t['slot'] != cur and t['H'].get('qlock', 0) >= 0.5 * samples]
                if others:
                    sp = 'EMU_LOCK'
                elif fr['gbusy'] is not None and b['gbusy'] is not None and fr['gbusy'] >= b['gbusy'] + 0.5 * e_us:
                    sp = 'DRV_GPU'
                else:
                    sp = 'DRV_HOST'
                return 'EMU_CALL:%s>%s' % (x, sp), sp, path, role, ''
            return 'EMU_CALL:%s' % x, 'EMU_CALL', path, role, ''
        if st == 'W':
            if x == 'sleep':
                c, fam, note = guest_check('GUEST_SLEEP:sleep')
                return c, fam, path, role, note
            emu = x in EMU_WAITS
            recs = [w for w in d['w'] if w.get('slot') == cur and w.get('kind') == x]
            best = max(recs, key=lambda w: (num(w.get('overlap_us'), 0) or 0)) if recs else None
            target = None
            to = best is not None and best.get('to') == 1
            if to and (not emu or (num(best.get('req_us'), 0) or 0) > 0):
                c, fam, note = guest_check('GUEST_SLEEP:%s' % x)
                return c, fam, path, role, (note + ' timeout record').strip()
            wk = num(best.get('waker'), -1) if best is not None else -1
            rp = num(best.get('peer'), -1) if best is not None else -1
            pr = num(row.get('peer'), -1)
            if wk is not None and wk >= 0:
                target, how = wk, 'waker'
            elif rp is not None and rp >= 0:
                target, how = rp, 'peer'
            elif x == 'mutex' and pr is not None and pr >= 0:
                target, how = pr, 'tpeer'
            if target is None:
                var = ('; executor variant (the -t peer for any kind): step to slot %d' % pr) if pr is not None and pr >= 0 else ''
                if to:
                    var += '; executor variant (RC5 (v) to = 1 for every kind): GUEST_SLEEP:%s' % x
                if emu:
                    return 'EMU_WAIT:%s' % x, 'EMU_WAIT', path, role, ('no waker, no peer' + (' (timeout record, req_us 0)' if to else '')
                                                                        + var)
                c, fam, note = guest_check('GUEST_SLEEP:%s' % x)
                return c, fam, path, role, (note + ' no waker, no peer' + var).strip()
            path[-1] += '->' + how
            if step == 3:
                return 'UNDETERMINED', 'UNDETERMINED', path, role, '> 3 steps'
            if target in visited:
                return 'UNDETERMINED', 'UNDETERMINED', path, role, 'cycle at slot %s' % target
            cur = target
            continue
        if st == 'R':
            if role != 'guest':
                return 'EMU_RUN:%s' % role, 'EMU_RUN', path, role, ''
            c, fam, note = guest_check('GUEST_RUN:%s' % row.get('name'))
            return c, fam, path, role, note
        if st == 'Sr':
            return 'HOST_PREEMPT', 'HOST_PREEMPT', path, role, ''
        if st in ('Sw', 'S'):
            note = 'kstate=0: preempted or waiting outside the marks (not distinguishable)' if h.get('kstate') == 0 else ''
            return 'UNMARKED:%s' % row.get('name'), 'UNMARKED', path, role, note
        sws = (num(row.get('Sw'), 0) or 0) + (num(row.get('S'), 0) or 0)
        var = ('; executor variant (Sw + S >= 50 %%): UNMARKED:%s' % row.get('name')) if sws >= 0.5 * samples else ''
        return 'UNDETERMINED', 'UNDETERMINED', path, role, 'no state >= 50 %' + var
    return 'UNDETERMINED', 'UNDETERMINED', path, None, '> 3 steps'


def classify(fr, d, b, theta):
    """fr: dict n, dt, lat, gbusy; d: parsed diag of the KEY window or None; b: base.  Item 596 (d)(3) with item 599 (b)(1), (3), (4)."""
    e_us = fr['dt'] - b['dt'] if b else None
    out = dict(E=e_us, holder=None, path=[], role=None, note='', steps=None)

    def done(cls, note=''):
        out.update(cls=cls, family=cls.split(':')[0], note=note)
        return out
    if d is None or d['hdr'] is None:
        return done('NO_SAMPLES:key', 'no window n / n + 1 with dt_us >= 0.5 x frame dt_us')
    h, x = d['hdr'], d['x']
    win = num(h.get('dt_us'), 0) or 0
    if win > ENV_US:
        return done('NO_SAMPLES:cover', 'window dt_us %d > %d (item 599 (b)(3))' % (win, ENV_US))
    tr = trunc_of(d)
    if tr:
        return done('NO_SAMPLES:trunc', ', '.join(tr))
    if num(x.get('hist_exh_w'), 0) >= 1:
        return done('NO_SAMPLES:cover', 'hist_exh_w %s' % x.get('hist_exh_w'))
    if agreement_bad(h, x):
        return done('NO_SAMPLES:trunc', 'agreement dt_us %s - cover_us %s > sgap_max_us %s + 1' % (h.get('dt_us'), h.get('cover_us'),
                                                                                                  h.get('sgap_max_us')))
    if e_us is not None and (num(h.get('sgap_max_us'), 0) or 0) >= 0.5 * e_us:
        return done('HOST_FREEZE')
    bad = []
    if h.get('i2') != 1:
        bad.append('i2=%s' % h.get('i2'))
    if not h.get('samples'):
        bad.append('samples=0')
    bad += zero_bad(x)
    if bad:
        return done('NO_SAMPLES', ', '.join(bad))
    ncpu = num(h.get('ncpu'), 0) or 0
    other = num(h.get('other_us'), 0) or 0
    out['load_ratio'] = round(other / (ncpu * win), 4) if ncpu and win else None
    if theta is not None and ncpu and win and other >= theta * ncpu * win:
        return done('HOST_LOAD')
    if b is None:
        return done('UNDETERMINED', 'no base')
    vo, fl = num(h.get('vo_slot'), -1), num(h.get('flip_slot'), -1)
    out_holder = fr['lat'] is not None and fr['lat'] - b['lat'] >= 0.5 * e_us
    holder = vo if out_holder else fl
    out['holder'] = 'output' if out_holder else 'flip'
    if holder is None or holder < 0:
        return done('UNDETERMINED', 'no holder slot')
    steps = []
    cls, fam, path, role, note = chain(d, holder, fr, b, e_us, steps)
    gs = num(h.get('gpu_slot'), -1)
    gpu_steps = [s for s in steps if s['slot'] == gs]
    out.update(cls=cls, family=fam, path=path, role=role, note=note, steps=steps, gpu_in_chain=bool(gpu_steps),
               gpu_sw_or_s50=any(s['Sw'] >= 0.5 * s['samples'] or s['S'] >= 0.5 * s['samples'] for s in gpu_steps),
               gpu_sw_plus_s50=any(s['Sw'] + s['S'] >= 0.5 * s['samples'] for s in gpu_steps))
    return out


def form_sig(dt, semwait, fh_other):
    """Item 596 (d)(5): FORM_SEM / FORM_NOFLIP / FORM_OTHER."""
    if semwait is not None and 2 * semwait >= dt:
        return 'FORM_SEM'
    if fh_other is not None and 2 * fh_other >= dt:
        return 'FORM_NOFLIP'
    return 'FORM_OTHER'


def read_m6(path):
    out = []
    if not path or not os.path.exists(path):
        return None
    for l in open(path, 'rb').read().decode('ascii', 'replace').splitlines():
        m = RX_M6.search(l)
        if m:
            out.append(dict(t=float(m.group(1)), emu_t=None if m.group(2) == '-' else float(m.group(2)), qpc=int(m.group(3)),
                            foreign=float(m.group(6))))
    return out


def read_cal(path):
    """CAL lines of the harness poller -> n -> QPC ns of the first sight of 'FrameTrace: n=<n>' in the live log."""
    out = {}
    if not path or not os.path.exists(path):
        return None
    for l in open(path, 'rb').read().decode('ascii', 'replace').splitlines():
        m = RX_CAL.match(l)
        if m:
            n = int(m.group(2))
            if n not in out:
                out[n] = int(m.group(1))
    return out


def calibrate(cal, diag):
    """Item 600 (b)(4): offset = min over printed windows n (flip_ns, first sight QPC of FrameTrace n) of qpc - flip_ns."""
    if not cal:
        return dict(offset=None, pairs=0, note='no CAL lines')
    pairs = []
    for n, d in diag.items():
        h = d['hdr']
        if h is None or n not in cal:
            continue
        fn = num(h.get('flip_ns'))
        if fn is None:
            continue
        pairs.append((cal[n] - fn, n))
    if not pairs:
        return dict(offset=None, pairs=0, note='no window with flip_ns seen by the poller')
    pairs.sort()
    return dict(offset=pairs[0][0], n=pairs[0][1], pairs=len(pairs), second_minus_min_ms=round((pairs[1][0] - pairs[0][0]) / 1e6, 3)
                if len(pairs) > 1 else None, note='')


def m6_burst(h, cal_res, m6):
    """Item 596 (d)(5) with item 600 (b)(4): True / False / 'NOT_DETERMINED'."""
    if h is None or m6 is None or cal_res is None or cal_res.get('offset') is None:
        return 'NOT_DETERMINED'
    fn, dt = num(h.get('flip_ns')), num(h.get('dt_us'))
    if fn is None or dt is None:
        return 'NOT_DETERMINED'
    end = fn + cal_res['offset']
    start = end - dt * 1000
    return any(s['foreign'] >= M6_FOREIGN and start - M6_PAD_NS <= s['qpc'] <= end + M6_PAD_NS for s in m6)


def window_u5(diag):
    """Item 596 (z) U5(4) with item 599 (b)(3), (4) and item 602 (v)(2): bad windows of the tag (dt_us <= envelope), the excluded ones and
    the reference lines 'sgap_bad after a long close'."""
    bad, excl, h2 = [], [], []
    for n in sorted(diag):
        d = diag[n]
        h, x = d['hdr'], d['x']
        if h is None:
            bad.append((n, ['-x / -t / -w lines without a DiagB32: line']))
            continue
        win = num(h.get('dt_us'), 0) or 0
        if win > ENV_US:
            excl.append((n, win))
            continue
        items = trunc_of(d)
        if x is not None:
            if agreement_bad(h, x):
                items.append('agreement')
            zb = zero_bad(x)
            if 'sgap_bad_w' in zb:
                p = diag.get(n - 1)
                prev = num((p['hdr'] or {}).get('w_lines'), 0) if p and p['hdr'] else 0
                if prev >= H2_REC:
                    zb.remove('sgap_bad_w')
                    h2.append((n, num(x.get('sgap_bad_w'), 0), prev))
            items += zb
        if items:
            bad.append((n, items))
    return bad, excl, h2


def rc13_equal(log_path, tmp_dir):
    tmp = os.path.join(tmp_dir, '_rc13_stripped.txt')
    n_out = 0
    with open(log_path, 'rb') as fi, open(tmp, 'wb') as fo:
        for line in fi:
            if line.startswith(b'DiagB32'):
                n_out += 1
                continue
            fo.write(line)
    try:
        a = F.scan(log_path)
        s = F.scan(tmp)
    finally:
        os.remove(tmp)
    ea, es = F.evaluate(a, BIN_B), F.evaluate(s, BIN_B)
    same = a['frames'] == s['frames'] and ea['hold_frames'] == es['hold_frames']
    return same, n_out, a


def read_log(path, theta, level, tmp_dir, m6=None, cal=None):
    """All members of one log (no admission): returns dict."""
    F.SG = level.encode()
    same, stripped, r = rc13_equal(path, tmp_dir)
    e = F.evaluate(r, BIN_B)
    s = scan_b32(path, level)
    ft, diag, ivl = s['ft'], s['diag'], s['ivl']
    frames = r['frames']                      # (idx, n, dt, t_before, ir, gcn, pcs, trip, prio, prio_us)
    pos = dict((x[1], i) for i, x in enumerate(frames))
    cal_res = calibrate(cal, diag)
    res = dict(level=level, rc13_equal=same, rc13_stripped=stripped, hold=e['hold'], scene_s=e['scene_s'], first_n=e['first_n'],
               frames_n=len(frames), sig=s['sig'], variant_dir=s['variant_dir'], mode=s['mode'][:2], invalid=s['invalid'][:2],
               diag_lines=s['diag_lines'], diag_bad_prefix=s['diag_bad_prefix'], diag_n=len(diag), recovering=s['recovering'],
               minimized=s['minimized'], test=s['test'][:6], dup=sum(d['dup'] for d in diag.values()), death=s['death'],
               replay_skipped=s['replay_skipped'], cal=cal_res, m6_samples=None if m6 is None else len(m6),
               m6_foreign_max=max([x['foreign'] for x in m6] or [0.0]) if m6 else None)
    # abort (item 599 (b)(2)): scene time at the GpuHangAbort line = end of the last scene frame before it
    ab = None
    if s['abort_after_n'] is not None:
        if s['abort_after_n'] in pos:
            x = frames[pos[s['abort_after_n']]]
            ab = round((x[3] + x[2]) / 1e6, 3)
        elif r['first_n'] is not None and s['abort_after_n'] == r['first_n']:
            ab = 0.0
    res['abort'] = None if s['abort_after_n'] is None else dict(after_n=s['abort_after_n'], scene_t_s=ab, line=s['abort_line'],
                                                                 hold=ab is not None and ab >= WIN_US / 1e6)
    rows = []
    for x in frames:
        if not (x[2] >= SLOW_US and x[3] >= WIN_US):
            continue
        n = x[1]
        att = F.attr(x, BIN_B, 'letter')
        rows.append(frame_row(x, att, ft, diag, ivl, frames, pos, theta, cal_res, m6))
    # SHARED_WIN: one key window of two adjacent hold frames (reference)
    for a, b in zip(rows, rows[1:]):
        if a['key'] is not None and a['key'] == b['key'] and b['n'] == a['n'] + 1:
            a['shared'] = b['shared'] = True
    k2 = [x for x in rows if x['k2'] and x['p_i']]
    cnt = [x for x in rows if x['in_count']]
    for x in rows:
        if not x['k2'] and x['p_i']:
            x['precursor'] = any(0 <= c['t_us'] - x['t_us'] <= PRE_US and c['n'] != x['n'] for c in cnt)
    res['frames'] = rows
    abort_hold = bool(res['abort'] and res['abort']['hold'])
    res['abort_hold'] = abort_hold
    res['hold_any'] = bool(e['hold'] or abort_hold)
    res['K_I'] = 1 if res['hold_any'] and (k2 or abort_hold) else 0
    res['K'] = 1 if res['hold_any'] and (cnt or abort_hold) else 0
    res['P_I_K2'] = len(k2)
    res['in_count'] = len(cnt) + (1 if abort_hold else 0)
    res['instr_made_k2'] = sum(1 for x in k2 if x['instr_made_k2'])
    if abort_hold:
        res['hold_class'], res['hold_family'] = 'NO_SAMPLES:abort', 'NO_SAMPLES'
    elif cnt and res['hold_any']:
        big = max(cnt, key=lambda x: x['dt_us'])
        res['hold_class'], res['hold_family'] = big['cls'], big['family']
    else:
        res['hold_class'] = res['hold_family'] = None
    res['hold_form'] = max(cnt, key=lambda x: x['dt_us'])['form'] if cnt else None
    res['hold_burst'] = (all(x['m6_burst'] is True for x in cnt) if cnt else None)
    # warm member (item 596 (g)): dump lines in the intervals of the frames with start >= 10 s of the scene
    warm_dump = [(x[1], x[4] + x[5]) for x in frames if x[3] >= WIN_US and x[4] + x[5] > 0]
    res['warm_dump_frames'] = warm_dump[:20]
    res['warm_dump_n'] = len(warm_dump)
    res['warm'] = not warm_dump
    hs = []
    for n, _ in warm_dump:
        for hh in (ivl.get(n) or {}).get('hashes', []):
            if hh not in hs:
                hs.append(hh)
    res['warm_dump_hashes'] = hs[:40]
    # B5 frames (reference: PK-A form of item 591 (v)(2), prewarms)
    b5 = []
    for x in frames:
        if x[2] < SLOW_US or F.attr(x, BIN_B, 'letter') != 'B5':
            continue
        rw = frame_row(x, 'B5', ft, diag, ivl, frames, pos, theta, cal_res, m6)
        rw['armed'] = rw['cls'] == 'EMU_RUN:Gpu' or (rw['cls'].startswith('EMU_CALL:') and rw.get('term_role') == 'Gpu')
        b5.append(rw)
    res['b5'] = [dict(n=x['n'], dt_us=x['dt_us'], t_s=x['t_s'], cls=x['cls'], armed=x['armed']) for x in b5]
    res['b5_armed'] = sum(1 for x in b5 if x['armed'])
    # U5 windows
    bad, excl, h2 = window_u5(diag)
    res['u5_bad'] = bad[:40]
    res['u5_bad_n'] = len(bad)
    res['u5_excl'] = excl[:20]
    res['u5_h2'] = h2
    res['u5_tag'] = bool(bad)
    lastx = None
    for n in sorted(diag):
        if diag[n]['x'] is not None:
            lastx = diag[n]['x']
    res['x_last'] = lastx
    res['rep_drop'] = num((lastx or {}).get('rep_drop'), 0) or 0
    res['bad_names'] = sorted(set(t.get('name') for d in diag.values() for t in d['t'] if not NAME_OK.match(str(t.get('name')))))
    # reference: median dt of the scene frames, frames >= 70 ms with start >= 10 s (base of U5 of the level, item 596 (z))
    res['med_dt'] = statistics.median(x[2] for x in frames) if frames else None
    res['slow70'] = sum(1 for x in frames if x[2] >= SHORT_US and x[3] >= WIN_US)
    # stand: the 3 frames after 'TestB32: fire'; the stand frame - the longest of them
    fires = [t for t in s['test'] if t['text'].startswith('TestB32: fire')]
    res['stand'] = None
    if fires and fires[0]['after_n'] is not None:
        order = s['ft_order']
        k = order.index(fires[0]['after_n']) if fires[0]['after_n'] in order else None
        nxt = order[k + 1:k + 4] if k is not None else []
        st = []
        for n in nxt:
            if n in pos:
                st.append(frame_row(frames[pos[n]], F.attr(frames[pos[n]], BIN_B, 'letter'), ft, diag, ivl, frames, pos, theta, cal_res,
                                    m6))
            else:
                st.append(dict(n=n, dt_us=ft[n][0], cls='UNDETERMINED', note='not a scene frame', key=None))
        res['stand'] = st
    return res


def frame_row(x, att, ft, diag, ivl, frames, pos, theta, cal_res, m6):
    n, dt = x[1], x[2]
    f = ft.get(n)
    b = base_of(ft, neighbours(frames, pos[n]))
    fr = dict(n=n, dt=dt, lat=f[1] if f else None, gbusy=f[2] if f else None)
    key = key_window(n, dt, diag)
    d = diag.get(key) if key is not None else None
    h = d['hdr'] if d else None
    row = dict(idx=x[0], n=n, dt_us=dt, t_s=round(x[3] / 1e6, 3), t_us=x[3], attr=att, lat_us=fr['lat'], gbusy_us=fr['gbusy'], base=b, key=key,
               key_dt_us=num(h.get('dt_us')) if h else None, key_branch=None if key is None else ('n' if key == n else 'n+1'),
               instr_us=num(h.get('instr_us')) if h else None, cover_us=num(h.get('cover_us')) if h else None,
               sgap_max_us=num(h.get('sgap_max_us')) if h else None, flip_ns=num(h.get('flip_ns')) if h else None,
               samples=num(h.get('samples')) if h else None, shared=False, precursor=False)
    row['k2'] = dt >= K2_US
    row['p_i'] = att not in ('B5', 'B33', 'B1b')
    row['instr_made_k2'] = bool(row['k2'] and row['p_i'] and h is not None and dt - (row['instr_us'] or 0) < K2_US)
    row['in_count'] = bool(row['k2'] and row['p_i'] and not row['instr_made_k2'])
    if d is not None and d['x'] is not None:
        row['zero_w'] = dict((k, num(d['x'].get(k))) for k in ZERO_F25)
        row['w_lines'] = num(h.get('w_lines')) if h else None
        row['print_us_x'] = num(d['x'].get('print_us'))
    c = classify(fr, d, b, theta)
    row.update(cls=c['cls'], family=c['family'], path=c.get('path'), holder=c.get('holder'), term_role=c.get('role'), note=c.get('note'),
               E=c.get('E'), load_ratio=c.get('load_ratio'), steps=c.get('steps'), gpu_in_chain=c.get('gpu_in_chain'),
               gpu_sw_or_s50=c.get('gpu_sw_or_s50'), gpu_sw_plus_s50=c.get('gpu_sw_plus_s50'))
    row['form'] = form_sig(dt, f[4] if f else None, (ivl.get(n) or {}).get('fh'))
    row['semwait_us'] = f[4] if f else None
    row['fh_other_us'] = (ivl.get(n) or {}).get('fh')
    row['m6_burst'] = m6_burst(h, cal_res, m6)
    # instr_us of the window after the key window (item 599 (b)(8): reference after every frame in count)
    nx = diag.get((key or n) + 1)
    row['instr_next_us'] = num(nx['hdr'].get('instr_us')) if nx and nx['hdr'] else None
    return row


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'snap_cmp', 'noreturn', 'glitch', 'installed_sha', 'level')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), run=os.path.join(base, 'es.json'), idx=os.path.join(base, 'rec.idx'),
                 seal=os.path.join(base, 'seal.md'), load=os.path.join(base, 'load.json'), tmp=base, theta_src=os.path.join(base, 'seal.md'),
                 m6=os.path.join(base, 'm6.txt'), cal=os.path.join(base, 'cal.txt'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag), idx=os.path.join(G, 'rec_%s.mp4.idx' % tag),
             seal=SEAL_PATH, load=os.path.join(d, 'load.json'), tmp=os.path.join(G, 'runs'), theta_src=SEAL_PATH,
             m6=os.path.join(d, 'm6.txt'), cal=os.path.join(d, 'cal.txt'))
    return p


def read_theta(path):
    if not os.path.exists(path):
        return None
    m = THETA_RX.findall(open(path, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n'))
    return float(m[0]) if len(m) == 1 else None


def kind_of(base):
    return dict(c='prewarm', z='control0', p='stand', s='series', k='cold')[base[4]]


def form_of(base):
    f = dict(KYTY_DIAG_B32='0' if base.startswith('f25_z') else '1', KYTY_GPU_WALL='1')
    if base in STAND:
        f['KYTY_TEST_B32'] = STAND[base]
    return f


def stand_ok(tests, want):
    mode = want.split(':')[1]
    t = [x['text'] for x in tests]
    return (any(x.startswith('TestB32: armed') for x in t) and any(x.startswith('TestB32: fire mode=' + mode) for x in t)
            and any(x.startswith('TestB32: done mode=' + mode) for x in t))


def read_tag(tag, p):
    base_tag = TAG_RX.match(tag).group(1)
    kind = kind_of(base_tag)
    form = form_of(base_tag)
    theta = read_theta(p['theta_src'])
    res = dict(tag=tag, form=base_tag, kind=kind, reader_sha256=sha_file(os.path.abspath(__file__)), f20e_read_sha256=sha_file(F.__file__),
               theta=theta)
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    jbin = (run or {}).get('binary_sha256')
    res['binary_sha256'] = jbin
    inst_b = (F.text(p['installed_before']) or '').strip() or None
    inst_a = (F.text(p['installed_after']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (F.text(p['manifest_cmp']) or '').strip().splitlines()
    scmp = (F.text(p['snap_cmp']) or '').strip().splitlines()
    noret = (F.text(p['noreturn']) or '').strip()
    hlev = (F.text(p['level']) or '').strip() or None
    ga = (run or {}).get('guest_args') or ''
    level = ga[5:] if ga.startswith('-lvl ') else None
    want_level = FIXED_LEVEL.get(base_tag)
    res['level'] = level
    load = json.load(open(p['load'], encoding='utf-8')) if os.path.exists(p['load']) else None
    m6 = read_m6(p['m6'])
    cal = read_cal(p['cal'])
    r = read_log(p['log'], theta, level, p['tmp'], m6, cal) if os.path.exists(p['log']) and theta is not None and level in LEVELS else None
    extra = dict((k, v) for k, v in env.items() if k not in HARN)
    diag_on = form['KYTY_DIAG_B32'] == '1'
    want_test = form.get('KYTY_TEST_B32')
    tests = (r or {}).get('test') or []
    death = (r or {}).get('death') or []
    ab = (r or {}).get('abort')
    # the abort path ends in EXIT -> '--- Error ---' (0005e11f masterSemaphore.cpp, assert.cpp): allowed only after GpuHangAbort:
    ia = death.index('GpuHangAbort:') if 'GpuHangAbort:' in death else None
    other_death = [x for i, x in enumerate(death) if x != 'GpuHangAbort:' and not (ia is not None and i > ia and x == '--- Error ---')]
    adm = [
        ('tag json present', run is not None),
        ('theta_load from the seal %s (%s)' % (p['theta_src'], theta), theta is not None),
        ('json binary_sha256 = binary B e342b839 (%s)' % (jbin or '-')[:16], jbin == BIN_B),
        ('installed before = after = S18 %s (%s / %s)' % (BIN_INST, (inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_INST and inst_a == BIN_INST),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env: harness constants + form %s (extra %s)' % (sorted(form.items()), sorted(extra.items())), run is not None and extra == form),
        ('KYTY_GPU_HANG_ABORT_S = 22 (%s)' % env.get('KYTY_GPU_HANG_ABORT_S'), env.get('KYTY_GPU_HANG_ABORT_S') == HANG_ABORT),
        ('last --vulkan-validation false (%s)' % F.last_flag(cmd, '--vulkan-validation'), F.last_flag(cmd, '--vulkan-validation') == 'false'),
        ('last --shader-validation false (%s)' % F.last_flag(cmd, '--shader-validation'), F.last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl of the tag level (%s; fixed %s; harness %s)' % (ga, want_level, hlev),
         level in LEVELS and (want_level is None or level == want_level) and hlev == level),
        ('hold option %d s (%s)' % (HOLD_S, (run or {}).get('hold_s')), (run or {}).get('hold_s') == HOLD_S),
        ('log present', r is not None),
        ('scene entered (first scene frame %s)' % (r or {}).get('first_n'), r is not None and r['first_n'] is not None),
        ('hold: scene >= 300 s (%s s) or GpuHangAbort after >= 10 s of the scene (%s)' % ((r or {}).get('scene_s'), ab),
         r is not None and r['hold_any']),
        ('no death marker other than GpuHangAbort (%s)' % other_death[:3], r is not None and not other_death),
        ('window events: minimized %s, Recovering Vulkan swapchain %s' % ((r or {}).get('minimized'), (r or {}).get('recovering')),
         r is not None and r['minimized'] == 0 and r['recovering'] == 0),
        ('DiagB32 mode line %s (%d)' % ('present' if diag_on else 'absent', len((r or {}).get('mode') or [])),
         r is not None and (len(r['mode']) == 1 if diag_on else (len(r['mode']) == 0 and r['diag_lines'] == 0))),
        ('no DiagB32 config invalid line', r is not None and not r['invalid']),
        ('translation signature 9177b426 (= S18) and cache dir %s (%s / %s)' % (VARIANT_DIR, [x[:8] for x in (r or {}).get('sig') or []],
                                                                              (r or {}).get('variant_dir')),
         r is not None and r['sig'] == [SIG_B] and r['variant_dir'] == [VARIANT_DIR]),
        ('TestB32 lines %s (%s)' % ('armed, fire, done' if want_test else 'none', [t['text'][:40] for t in tests][:4]),
         r is not None and (stand_ok(tests, want_test) if want_test else not tests)),
        ('rep_drop 0 (%s)' % (r or {}).get('rep_drop'), r is not None and r['rep_drop'] == 0),
        ('no loader (%s)' % (None if load is None else load.get('status')), load is None),
        ('caches before = snapshot of the form (%s)' % (scmp[0][:50] if scmp else '-'), bool(scmp) and scmp[0].startswith('manifest cmp EQUAL')),
    ]
    if kind == 'prewarm':
        adm.append(('prewarm: no return of the caches (%s)' % noret[:40], noret.startswith('NO RETURN')))
    else:
        adm.append(('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'),
                    bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL') and not noret))
    res['admission'] = [[a, bool(b)] for a, b in adm]
    admitted = all(b for _, b in adm)
    warm_need = kind in ('series', 'control0', 'stand')
    warm_ok = r is not None and r['warm']
    res['warm_member'] = None if not warm_need else bool(warm_ok)
    if not admitted:
        res['status'] = 'INTERFERENCE'
    elif warm_need and not warm_ok:
        res['status'] = 'NOT_WARM'
    else:
        res['status'] = 'ADMITTED'
    res['admitted'] = res['status'] == 'ADMITTED'
    res['log'] = r
    idx_n = None
    if os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as fi:
            idx_n = sum(1 for _ in fi)
    gl = None
    gt = F.text(p['glitch'])
    if gt:
        mg = F.RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    res['ref'] = dict(glitches=gl, video_index=idx_n, outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'),
                      installed_sha=(F.text(p['installed_sha']) or '').strip()[:64] or None,
                      signature=','.join((r or {}).get('sig') or []) or None)
    res['control'] = control_members(base_tag, r) if res['admitted'] and kind in ('control0', 'stand') else None
    res['reading'] = {'INTERFERENCE': 'INTERFERENCE (repeat, not counted)', 'NOT_WARM': 'NOT WARM (layer N_nw / K_nw, item 599 (b)(7))',
                      'ADMITTED': 'ADMITTED (no verdict; reading - F25g)'}[res['status']]
    return res


def control_members(base, r):
    """Item 596 (z) with item 599 (b)(1), (9) and F25a s5: members of f25_z1 / f25_z2 / f25_pb / f25_pc."""
    if base in ('f25_z1', 'f25_z2'):
        m = [('DiagB32 lines 0 and no mode=1 line (%d / %d)' % (r['diag_lines'], len(r['mode'])), r['diag_lines'] == 0 and not r['mode'])]
        return dict(members=m, ok=all(b for _, b in m), ref=dict(med_dt=r['med_dt'], slow70=r['slow70']))
    st = r.get('stand') or []
    sf = max(st, key=lambda x: x['dt_us']) if st else None
    m = [('stand frame found (3 frames after TestB32: fire)', sf is not None)]
    if sf is not None:
        key = sf.get('key')
        zw = sf.get('zero_w') or {}
        m += [
            ('stand frame dt_us %s >= %d' % (sf['dt_us'], STAND_MIN_US[base]), sf['dt_us'] >= STAND_MIN_US[base]),
            ('key reduced (window %s, branch %s)' % (key, sf.get('key_branch')), key is not None),
            ('hist_exh_w 0 (%s)' % zw.get('hist_exh_w'), zw.get('hist_exh_w') == 0),
            ('agreement dt_us - cover_us <= sgap_max_us + 1 (%s / %s / %s)' % (sf.get('key_dt_us'), sf.get('cover_us'), sf.get('sgap_max_us')),
             None not in (sf.get('key_dt_us'), sf.get('cover_us'), sf.get('sgap_max_us')) and
             sf['key_dt_us'] - sf['cover_us'] <= sf['sgap_max_us'] + 1),
            ('lines_cut_w 0, w_cut_w 0, others_cut_w 0 (%s / %s / %s)' % (zw.get('lines_cut_w'), zw.get('w_cut_w'), zw.get('others_cut_w')),
             zw.get('lines_cut_w') == 0 and zw.get('w_cut_w') == 0 and zw.get('others_cut_w') == 0),
            ('0 DiagB32 windows of the tag with a trunc item (%d)' % sum(1 for _, it in r['u5_bad'] if any(
                'without' in i or 'last field' in i or 'no -x' in i or 'no DiagB32' in i for i in it)),
             not any(any('without' in i or 'last field' in i or 'no -x' in i or 'no DiagB32' in i for i in it) for _, it in r['u5_bad'])),
        ]
        if base == 'f25_pb':
            m.append(('class EMU_CALL:present (any RC7 split) (%s)' % sf['cls'], str(sf['cls']).startswith('EMU_CALL:present')))
        else:
            m.append(('class UNMARKED:Gpu or a GuestGpu step with Sw or S >= 50 %%; not HOST_FREEZE, not NO_SAMPLES* (%s, step %s)' % (
                sf['cls'], sf.get('gpu_sw_or_s50')),
                (sf['cls'] == 'UNMARKED:Gpu' or bool(sf.get('gpu_sw_or_s50'))) and sf['cls'] != 'HOST_FREEZE' and
                not str(sf['cls']).startswith('NO_SAMPLES')))
    ref = None
    if sf is not None:
        ref = dict(w_lines=sf.get('w_lines'), expect_w='~330' if base == 'f25_pb' else '~630', others_cut_w=(sf.get('zero_w') or {}).get(
            'others_cut_w'), print_us_x=sf.get('print_us_x'), instr_next_us=sf.get('instr_next_us'), key_branch=sf.get('key_branch'))
    return dict(members=m, ok=all(b for _, b in m), ref=ref)


def rows_out(res):
    out = ['tag %s (form %s, kind %s, level %s)  reader sha256 %s  f20e_read sha256 %s  theta %s' % (
        res['tag'], res['form'], res['kind'], res['level'], res['reader_sha256'], res['f20e_read_sha256'], res['theta'])]
    out.append('  ADMISSION %s; STATUS %s; warm member %s' % ('PASS' if all(b for _, b in res['admission']) else 'FAIL', res['status'],
                                                              res['warm_member']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    rf = res['ref']
    out.append('  binary %s; installed during the tag %s; translation signature %s' % (res['binary_sha256'], rf['installed_sha'],
                                                                                      rf['signature']))
    r = res['log']
    if r:
        out.append('  scene: first_n %s, frames %d, scene %.1f s, hold %s (abort hold %s); DiagB32 lines %d (windows %d, bad prefix %d, dup %d)'
                   % (r['first_n'], r['frames_n'], r['scene_s'], r['hold'], r['abort_hold'], r['diag_lines'], r['diag_n'],
                      r['diag_bad_prefix'], r['dup']))
        out.append('  abort %s; death markers %s; replay rebuild skipped lines %d' % (r['abort'], r['death'][:4], r['replay_skipped']))
        out.append('  RC13: F20c attribution with = without DiagB32 lines (%d stripped): %s' % (r['rc13_stripped'],
                                                                                           'EQUAL' if r['rc13_equal'] else 'DIFFERENT'))
        out.append('  warm: dump frames (start >= 10 s) %d %s; program hashes %s' % (r['warm_dump_n'], r['warm_dump_frames'][:6],
                                                                                    r['warm_dump_hashes'][:8]))
        out.append('  K_I %d; K %d; K2 frames not attributed %d; in count %d; INSTR_MADE_K2 %d' % (
            r['K_I'], r['K'], r['P_I_K2'], r['in_count'], r['instr_made_k2']))
        out.append('  hold class (longest frame in count): %s; family %s; form %s; all frames in count M6_BURST %s' % (
            r['hold_class'], r['hold_family'], r['hold_form'], r['hold_burst']))
        out.append('  M6: samples %s, foreign max %s; calibration %s' % (r['m6_samples'], r['m6_foreign_max'], r['cal']))
        for x in r['frames'][:80]:
            tagx = ' IN COUNT' if x['in_count'] else (' INSTR_MADE_K2' if x['instr_made_k2'] else (
                ' K2-ref(%s)' % x['attr'] if x['k2'] else ' ref'))
            out.append('    FRAME n %d dt_us %d t %.1f s attr %s | key %s(%s) win %s instr %s cover %s sgap %s | E %s holder %s | %s%s%s%s'
                       ' | %s | %s | %s | M6_BURST %s | next instr %s%s' % (
                           x['n'], x['dt_us'], x['t_s'], x['attr'], x['key'], x['key_branch'], x['key_dt_us'], x['instr_us'], x['cover_us'],
                           x['sgap_max_us'], x['E'], x['holder'], x['cls'], tagx, ' SHARED_WIN' if x['shared'] else '',
                           ' PRECURSOR' if x.get('precursor') else '', ' > '.join(x['path'] or []), x['note'], x['form'], x['m6_burst'],
                           x['instr_next_us'], (' load %s' % x['load_ratio']) if x.get('load_ratio') is not None else ''))
        out.append('  B5 frames %d, armed (EMU_RUN:Gpu / EMU_CALL on GuestGpu) %d: %s' % (len(r['b5']), r['b5_armed'],
                                                                                        [(x['n'], x['cls']) for x in r['b5']][:10]))
        if r['stand'] is not None:
            out.append('  STAND frames after TestB32 fire: %s' % [(x['n'], x['dt_us'], x['cls'], x.get('key'), x.get('key_branch'))
                                                                  for x in r['stand']])
        out.append('  U5 windows (dt_us <= %d): bad %d %s; excluded (> envelope) %s; sgap_bad after a long close (reference) %s' % (
            ENV_US, r['u5_bad_n'], r['u5_bad'][:6], r['u5_excl'][:6], r['u5_h2']))
        out.append('  reference: median dt of the scene %s, frames >= 70 ms after 10 s %s; unprintable names %s; rep_drop %d' % (
            r['med_dt'], r['slow70'], r['bad_names'], r['rep_drop']))
        out.append('  -x last %s' % r['x_last'])
    if res.get('control') is not None:
        c = res['control']
        out.append('  CONTROL %s %s' % (res['form'], 'PASS' if c['ok'] else 'FAIL'))
        for a, b in c['members']:
            out.append('    [%s] %s' % ('ok' if b else 'NO', a))
        out.append('    reference %s' % c['ref'])
    out.append('  REFERENCE: glitches %s, video index %s, outcome %s, hold_exit %s, hold_s %s' % (
        rf['glitches'], rf['video_index'], rf['outcome'], rf['hold_exit'], rf['hold_s']))
    out.append('  READING %s' % res['reading'])
    return out


def load_runs(rd):
    out = {}
    if not os.path.isdir(rd):
        return out
    for t in os.listdir(rd):
        if TAG_RX.match(t) and os.path.exists(os.path.join(rd, t, 'read.json')):
            out[t] = json.load(open(os.path.join(rd, t, 'read.json'), encoding='utf-8'))
    return out


def first_good(runs, base, want=('ADMITTED',)):
    tags = sorted(t for t in runs if TAG_RX.match(t).group(1) == base and runs[t]['status'] in want)
    return tags[0] if tags else None


def stop_rule(n, k, ki):
    """Item 596 (e) with item 552 (g)."""
    if n < N_MIN:
        return 'CONTINUE', 'N %d < %d' % (n, N_MIN)
    if k >= K_STOP:
        return 'STOP_READ', 'K %d >= 3 at N %d' % (k, n)
    if k == 0:
        if n < N_MID:
            return 'CONTINUE', 'K 0 at N %d - up to %d' % (n, N_MID)
        if ki == 0:
            return 'STOP_U2', 'K 0, K_I 0 at N %d' % n
        return 'STOP_552G', 'K 0, K_I %d at N %d - item 552 (g), not U2' % (ki, n)
    if n >= N_MAX:
        return 'STOP_U2PRIME', 'K %d at N %d' % (k, n)
    return 'CONTINUE', 'K %d at N %d - up to K 3 or N %d' % (k, n, N_MAX)


def groups(fams, k):
    def sh(names):
        return round(sum(v for f, v in fams.items() if f in names) / float(k), 4) if k else None
    return dict(i=sh(GROUP_I), iii=sh(GROUP_III), top=max(fams.items(), key=lambda x: x[1]) if fams else None)


def series(rd):
    runs = load_runs(rd)
    out = ['SERIES over %s (tags read %d)' % (rd, len(runs))]
    made = len(runs)
    interf = sum(1 for t in runs if runs[t]['status'] in ('INTERFERENCE', 'NOT_WARM'))
    out.append('BUDGET tags read %d of %d; interference + NOT WARM %d of %d%s' % (
        made, BUDGET_TAGS, interf, BUDGET_INTERF, ' - STOP_INTERFERENCE' if interf > BUDGET_INTERF else ''))
    # controls
    cres = {}
    for c in ('f25_z1', 'f25_z2', 'f25_pb', 'f25_pc'):
        t = first_good(runs, c)
        cres[c] = None if t is None else runs[t]['control']['ok']
        out.append('CONTROL %s %s%s' % (c, 'PENDING' if t is None else ('PASS' if cres[c] else 'FAIL'), '' if t is None else ' (%s)' % t))
    ctl = 'PENDING' if None in cres.values() else ('PASS' if all(cres.values()) else 'FAIL (U1-prime: stop, one code fix, all 4 again)')
    out.append('CONTROLS %s' % ctl)
    for c in ('f25_c1', 'f25_c2'):
        t = first_good(runs, c)
        if t is None:
            out.append('PREWARM %s PENDING' % c)
            continue
        r = runs[t]['log']
        out.append('PREWARM %s (%s, reference): K2 not attributed %d, in count %d, class %s; B5 frames %d armed %d' % (
            c, t, r['P_I_K2'], r['in_count'], r['hold_class'], len(r['b5']), r['b5_armed']))
    # series per level
    st = {}
    u5_tags = []
    for lv in LEVELS:
        tags = []
        for base in sorted(set(TAG_RX.match(t).group(1) for t in runs if TAG_RX.match(t).group(1).startswith('f25_s'))):
            t = first_good(runs, base)
            if t is not None and runs[t]['level'] == lv:
                tags.append((base, t))
        n = k = ki = 0
        fams = {}
        for base, t in tags:
            r = runs[t]['log']
            n += 1
            k += r['K']
            ki += r['K_I']
            if r['K']:
                fams[r['hold_family']] = fams.get(r['hold_family'], 0) + 1
            if r['u5_tag']:
                u5_tags.append(t)
            out.append('  %s %s (%s) K %d K_I %d class %s form %s burst %s | u5 %s | read %s' % (
                lv[:5], base, t, r['K'], r['K_I'], r['hold_class'], r['hold_form'], r['hold_burst'], 'BAD' if r['u5_tag'] else '0',
                (sha_file(os.path.join(rd, t, 'read.txt')) or '-')[:16]))
        nw = [t for t in runs if TAG_RX.match(t).group(1).startswith('f25_s') and runs[t]['status'] == 'NOT_WARM' and runs[t]['level'] == lv]
        nw_k = sum(runs[t]['log']['K'] for t in nw)
        hs = {}
        for t in nw:
            for hh in runs[t]['log']['warm_dump_hashes']:
                hs.setdefault(hh, set()).add(t)
        same = sorted(hh for hh, ts in hs.items() if len(ts) >= 2)
        rule, why = stop_rule(n, k, ki)
        if same:
            rule, why = 'STOP_LEVEL_Q', 'two NOT WARM tags with one program hash %s - question to the lead (item 599 (b)(7))' % same[:3]
        st[lv] = rule
        out.append('LEVEL %s N %d K %d K_I %d; N_nw %d K_nw %d; STOP RULE %s (%s)' % (lv, n, k, ki, len(nw), nw_k, rule, why))
        if k:
            g = groups(fams, k)
            out.append('  CLASSES %s; (i) NO_SAMPLES* + UNMARKED + UNDETERMINED %s; (iii) host %s; top %s [reference - the reading is F25g]'
                       % (sorted(fams.items(), key=lambda x: (-x[1], str(x[0]))), g['i'], g['iii'], g['top']))
    u4 = len(u5_tags) >= 2
    out.append('U5(4) series tags with a bad window %d %s (member >= 2): %s' % (len(u5_tags), u5_tags[:6], 'FIRES' if u4 else 'no'))
    # cold layer
    for lv in LEVELS:
        tags = []
        for base in sorted(set(TAG_RX.match(t).group(1) for t in runs if TAG_RX.match(t).group(1).startswith('f25_k'))):
            t = first_good(runs, base)
            if t is not None and runs[t]['level'] == lv:
                tags.append(t)
        if not tags:
            out.append('COLD %s: no tag' % lv)
            continue
        hit = [t for t in tags if runs[t]['log']['K']]
        res = ('STOP_REPRO (first %s)' % hit[0]) if hit else ('STOP_NO_REPRO (0 of %d)' % len(tags) if len(tags) >= COLD_MAX else
                                                              'CONTINUE (0 of %d)' % len(tags))
        out.append('COLD %s tags %s: %s' % (lv, tags, res))
    nxt = 'STOP (interference)' if interf > BUDGET_INTERF else ('STOP (U5(4))' if u4 else ('STOP (controls)' if ctl.startswith('FAIL') else (
        'STOP (budget)' if made >= BUDGET_TAGS else 'see the levels')))
    out.append('NEXT %s; levels %s' % (nxt, st))
    return out


def table(rd):
    tags = sorted(t for t in os.listdir(rd) if TAG_RX.match(t) and os.path.exists(os.path.join(rd, t, 'read.json'))) \
        if os.path.isdir(rd) else []
    out = ['| tag | level | status | bin / sig | K_I / K | in count | classes (n: class) | form | M6_BURST | U5 bad | ctl | glitches |',
           '|' + '---|' * 12]
    for t in tags:
        res = json.load(open(os.path.join(rd, t, 'read.json'), encoding='utf-8'))
        r = res['log'] or {}
        cl = ['%d:%s' % (x['n'], x['cls']) for x in r.get('frames', []) if x['in_count']]
        if r.get('abort_hold'):
            cl.append('abort:NO_SAMPLES:abort')
        fm = sorted(set(x['form'] for x in r.get('frames', []) if x['in_count']))
        bu = sorted(set(str(x['m6_burst']) for x in r.get('frames', []) if x['in_count']))
        c = res.get('control')
        out.append('| %s | %s | %s | %s / %s | %s / %s | %s | %s | %s | %s | %s | %s | %s |' % (
            t, (res.get('level') or '-')[:5], res['status'], (res['binary_sha256'] or '-')[:8], (res['ref'].get('signature') or '-')[:8],
            r.get('K_I'), r.get('K'), r.get('in_count'), ' '.join(cl) or '-', ','.join(fm) or '-', ','.join(bu) or '-', r.get('u5_bad_n'),
            '-' if c is None else ('PASS' if c['ok'] else 'FAIL'), res['ref'].get('glitches')))
    return out


def main(argv):
    if '--check-seal' in argv:
        seal = argv[argv.index('--seal') + 1] if '--seal' in argv else SEAL_PATH
        return F.main(['--check-seal', '--seal', seal])
    if '--table' in argv or '--series' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        lines = table(rd) if '--table' in argv else series(rd)
        print('reader f25_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in lines:
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        p = paths(tag)
    if not TAG_RX.match(tag):
        print('usage: f25_read.py f25_c1|f25_c2|f25_z1|f25_z2|f25_pb|f25_pc|f25_s01..40|f25_k01..10[_r1..6] | --dir D --tag T | --table | '
              '--series | --check-seal')
        return 2
    if sha_file(F.__file__) != F20E_SHA:
        print('f20e_read.py sha256 %s != %s - refused' % (sha_file(F.__file__), F20E_SHA))
        return 1
    res = read_tag(tag, p)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
