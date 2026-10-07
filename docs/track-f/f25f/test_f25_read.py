"""F25f (HPP-669): fixtures of f25_read.py - item 596 (d)-(z) with item 599 (b)(1)-(7), (10), (11), (v) RC13-RC14, item 600 (b)(4) and
item 602 (v)(2): the key window (branches n / n + 1, the larger, the 0.5 edge, NO_SAMPLES:key, SHARED_WIN, the b32_pa frames 8796-8798
with the values of their log), the K2 count (1 s edges, INSTR_MADE_K2, K_I, precursor), the attribution B5 / B1b / B33 (B33 on a binary
before S12 by the letter of F20c), the member (0) (envelope, hist_exh_w, the agreement and its edge), NO_SAMPLES:trunc (each field and
line), the zero invariants, NO_SAMPLES:abort and the death markers, the form, M6_BURST with the offset calibration, U5 windows with the
rule of item 602 (v)(2) (both branches), the warm member and the program hashes, admission, controls, the stop rule of item 596 (e), the
NOT WARM layer, the cold layer, the budget; and, ported unchanged from e8ea0a57 test_b32_read.py: every class and edge of the chain of
item 550 (g)(2) (i)-(iv), RC6, RC7, item 574 (d), item 581 (v)(5).  ASCII only; ends with ALL OK.
usage: python test_f25_read.py"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f25_read as R  # noqa: E402

TMP = os.path.join(HERE, 'fx_tmp')
print('suite test_f25_read.py sha256 %s target f25_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
    hashlib.sha256(open(os.path.join(HERE, 'f25_read.py'), 'rb').read()).hexdigest()))

ok = True
nchk = 0


def check(name, cond, got=None):
    global ok, nchk
    nchk += 1
    if not cond:
        ok = False
        print('FAIL %s (got %s)' % (name, got))


BASE_DT, BASE_LAT, BASE_GB = 33333, 12000, 15000
FIRST = 100          # first scene frame n
T0 = 400             # first target idx (t ~ 13.3 s)
LV = R.POT


def thr(slot, name, role, R=0, r=0, Sr=0, Sw=0, S=0, W=None, H=None, peer=-1, X=0):
    return dict(slot=slot, name=name, role=role, R=R, r=r, Sr=Sr, Sw=Sw, S=S, W=W or {}, H=H or {}, peer=peer, X=X)


def klist(d):
    return ','.join('%s:%d' % (k, v) for k, v in d.items()) if d else '-'


XF = ('slot_full', 'torn', 'ring_drop', 'sgap_bad', 'lines_cut', 'req_miss', 'sub_miss')


def diag_block(n, dt, samples=40, instr=1000, sgap=5000, i2=1, kstate=1, kq_n=1, kq_us=900, m5r=0, other=0, ncpu=32, vo=0, gpu=1,
               flip=2, threads=None, waits=None, xw=None, x=True, hdr=True, cum=None, ring_hold=0, ring_hold_c=None, cover=None,
               flip_ns=None, hist_exh_w=0, w_cut_w=0, others_cut_w=0, drop=(), w_lines=None, t_trunc=False, w_trunc=False):
    """The block of binary B (35b454c6 Format): header ... cover_us flip_ns; -t ... peer; -w ... peer_tid; -x ... hist_exh hist_exh_w
    w_cut_w others_cut_w.  cover default dt - sgap (the agreement holds); drop - field names removed from the header or -x."""
    out = []
    cov = dt - sgap if cover is None else cover
    fns = 10 ** 12 + n * 10 ** 6 if flip_ns is None else flip_ns
    if threads is None:
        threads = [thr(0, 'Present', 'Present', S=samples), thr(1, 'Gpu', 'Gpu', r=samples), thr(2, 'DrawThread', 'guest', S=samples)]
    if hdr:
        out.append('DiagB32: n=%d dt_us=%d instr_us=%d samples=%d sgap_max_us=%d gap3p=0 i2=%d kstate=%d kq=1 kq_n=%d kq_us=%d m5r_us=%d '
                   'proc_us=100000 sys_busy_us=%d sys_idle_us=0 other_us=%d ncpu=%d snap_ok=1 snap_lag_us=10 flip_slot=%d flip_tid=7 '
                   'flip_src=cpu lat_us=12000 vo_slot=%d gpu_slot=%d t_lines=%d w_lines=%d c_lines=0 cover_us=%d flip_ns=%d' % (
                       n, dt, instr, samples, sgap, i2, kstate, kq_n, kq_us, m5r, 100000 + other, other, ncpu, flip, vo, gpu, len(threads),
                       len(waits or []) if w_lines is None else w_lines, cov, fns))
    for t in threads:
        out.append('DiagB32-t: n=%d slot=%d tid=0 os_tid=1 name=%s role=%s must=1 X=%d R=%d r=%d Sr=%d Sw=%d S=%d W=%s H=%s SwR=- cpu_us=0 '
                   'top=- last=- obj=0x0 since_us=0%s' % (n, t['slot'], t['name'], t['role'], t['X'], t['R'], t['r'], t['Sr'],
                                                         t['Sw'], t['S'], klist(t['W']), klist(t['H']), '' if t_trunc else ' peer=%d' % t['peer']))
    for w in waits or []:
        out.append('DiagB32-w: n=%d slot=%d tid=0 kind=%s obj=0x1 start_us=0 wait_us=%d overlap_us=%d waker=%d waker_tid=0 req_us=%d to=%d '
                   'open=0 peer=%d%s' % (n, w['slot'], w['kind'], w.get('wait', 50000), w.get('overlap', 50000), w.get('waker', -1),
                                         w.get('req', 0), w.get('to', 0), w.get('peer', -1), '' if w_trunc else ' peer_tid=0'))
    if x:
        z = dict((k, 0) for k in R.ZERO_W)
        z.update(xw or {})
        c = dict((k, 0) for k in XF)
        c.update(cum or {})
        out.append('DiagB32-x: n=%d slots=10 slot_full=%d slot_full_w=%d torn=%d torn_w=%d ring_drop=%d ring_drop_w=%d sgap_bad=%d '
                   'sgap_bad_w=%d lines_cut=%d lines_cut_w=%d req_miss=%d req_miss_w=%d sub_miss=%d sub_miss_w=%d short_stalls=0 '
                   'others_cut=0 w_cut=0 rep_drop=%d kq_fail=0 print_us=10 gap3p=0 ring_hold=%d ring_hold_w=%d hist_exh=%d hist_exh_w=%d '
                   'w_cut_w=%d others_cut_w=%d' % (
                       n, c['slot_full'], z['slot_full_w'], c['torn'], z['torn_w'], c['ring_drop'], z['ring_drop_w'], c['sgap_bad'],
                       z['sgap_bad_w'], c['lines_cut'], z['lines_cut_w'], c['req_miss'], z['req_miss_w'], c['sub_miss'], z['sub_miss_w'],
                       (cum or {}).get('rep_drop', 0), ring_hold if ring_hold_c is None else ring_hold_c, ring_hold, hist_exh_w, hist_exh_w,
                       w_cut_w, others_cut_w))
    res = []
    for l in out:
        for f in drop:
            l = ' '.join(tok for tok in l.split(' ') if not tok.startswith(f + '='))
        res.append(l)
    return res


SEED_LINES = ['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\n',
              'ShaderSeed: compatibility=KytySeed1:PPSA21564:01.007.000:KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz\n']


def build(targets=None, nframes=9200, extra_after=None, b5_idx=(), pre=None, recovering=False, test_fire_idx=None, dt_by_idx=None,
          seed=None, stand_mode='present', pre_scene=None, level=None, before=None, quit=True, stop_idx=None):
    """targets: idx -> dict(dt, lat, gb, sem, diag (list of lines or None), key_at (idx after which the block goes; default idx + 1));
    before: idx -> lines in the interval of frame idx (before its FrameTrace line)."""
    targets = targets or {}
    dt_by_idx = dict(dt_by_idx or {})
    lv = LV if level is None else level
    lines = ['loading\n'] + (SEED_LINES if seed is None else seed) + ['GuestOut: Level has started: \n'] + (pre or []) + \
        ['GuestOut: Level has started: %s\n' % lv] + [x + '\n' for x in (pre_scene or [])]
    lines.append('FrameTrace: n=%d dt_us=40000 lat_us=12000 gpu_proc=0 draws=4000 semwait_us=0 gpu_busy_us=15000 cpu_gpu_us=30000\n' % FIRST)
    pending = {}
    for idx in range(1, nframes + 1):
        if stop_idx is not None and idx > stop_idx:
            break
        n = FIRST + idx
        if idx in b5_idx:
            lines.append('%_1 = OpTypeVoid\n')
        for l in (before or {}).get(idx, []):
            lines.append(l + '\n')
        if test_fire_idx is not None and idx == test_fire_idx:
            lines.append('TestB32: armed delay_s=60 mode=%s ms=200\n' % stand_mode)
            lines.append('TestB32: fire mode=%s ms=200\n' % stand_mode)
            lines.append('TestB32: done mode=%s slept_us=200000\n' % stand_mode)
        t = targets.get(idx)
        dt = t['dt'] if t else dt_by_idx.get(idx, BASE_DT)
        lat = t.get('lat', BASE_LAT) if t else BASE_LAT
        gb = t.get('gb', BASE_GB) if t else BASE_GB
        sem = t.get('sem', 0) if t else 0
        lines.append('FrameTrace: n=%d dt_us=%d lat_us=%d gpu_proc=0 draws=4000 semwait_us=%d gpu_busy_us=%d cpu_gpu_us=30000\n' % (
            n, dt, lat, sem, gb))
        if t and t.get('diag') is not None:
            pending.setdefault(t.get('key_at', idx + 1), []).extend(t['diag'])
        if idx in pending:
            for l in pending.pop(idx):
                lines.append(l + '\n')
        if extra_after and idx in extra_after:
            for l in extra_after[idx]:
                lines.append(l + '\n')
    if recovering:
        lines.append('Recovering Vulkan swapchain\n')
    if quit:
        lines.append('Event: quit\n')
    return ''.join(lines)


def write_log(name, text):
    d = os.path.join(TMP, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'log.txt'), 'w', encoding='ascii', newline='\n') as f:
        f.write(text)
    return d


def read(name, text, theta=None, level=None, m6=None, cal=None):
    d = write_log(name, text)
    return R.read_log(os.path.join(d, 'log.txt'), theta, LV if level is None else level, d, m6, cal)


def frame(res, idx):
    n = FIRST + idx
    for x in res['frames']:
        if x['n'] == n:
            return x
    return None


def mem(cm, prefix):
    return [b for a, b in cm['members'] if a.startswith(prefix)]


def one(name, dt, diag_kw, theta=None, lat=BASE_LAT, gb=BASE_GB, diag=True):
    n = FIRST + T0
    blk = diag_block(n, dt, **diag_kw) if diag else None
    res = read(name, build({T0: dict(dt=dt, lat=lat, gb=gb, diag=blk)}), theta)
    return frame(res, T0), res


if os.path.isdir(TMP):
    shutil.rmtree(TMP)
os.makedirs(TMP)
S = 40
E200 = 200000 - BASE_DT          # E of a 200 ms frame

# ==== ported unchanged from e8ea0a57:docs/track-f/f20l3/test_b32_read.py (the chain of item 550 (g)(2); 200 ms frames - reference rows
# classified by the same rule, item 596 (d)(1))
# ---- (i) HOST_FREEZE and its edge
f, _ = one('freeze', 200000, dict(sgap=E200 // 2 + (E200 % 2)))
check('HOST_FREEZE at sgap = 0.5 E', f['cls'] == 'HOST_FREEZE', f['cls'])
f, _ = one('freeze_edge', 200000, dict(sgap=E200 // 2 - 1))
check('not HOST_FREEZE at sgap < 0.5 E', f['cls'] != 'HOST_FREEZE', f['cls'])
check('E = dt - median of the neighbours', f['E'] == E200, f['E'])

E2 = 200001 - BASE_DT            # even E: the 0.5 x E edges are integers
f, _ = one('freeze_eq', 200001, dict(sgap=E2 // 2))
check('HOST_FREEZE at sgap = 0.5 E exactly (even E)', f['cls'] == 'HOST_FREEZE', f['cls'])
# base: 10 + 10 neighbours, slow frames skipped
dts = dict((T0 - k, 30000) for k in range(1, 11))
dts.update(dict((T0 + k, 40000) for k in range(1, 10)))
dts[T0 + 10] = 30000
res = read('base20', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000))}, dt_by_idx=dts))
check('base = median of 10 + 10 neighbours (30 000)', frame(res, T0)['base']['dt'] == 30000 and frame(res, T0)['base']['k'] == 20,
      frame(res, T0)['base'])
dts2 = dict(dts)
res = read('base_skip', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000)), T0 - 3: dict(dt=150000, diag=None)},
                              dt_by_idx=dts2))
check('base skips frames >= 100 ms (31 666.5)', frame(res, T0)['base']['dt'] == 31666.5, frame(res, T0)['base'])

# ---- (iii) HOST_LOAD
win = 200000
f, _ = one('load_eq', win, dict(other=int(0.5 * 32 * win)), theta=0.5)
check('HOST_LOAD at other = theta x ncpu x window', f['cls'] == 'HOST_LOAD', f['cls'])
f, _ = one('load_lt', win, dict(other=int(0.5 * 32 * win) - 1), theta=0.5)
check('not HOST_LOAD below', f['cls'] != 'HOST_LOAD', f['cls'])
f, _ = one('load_notheta', win, dict(other=32 * win))
check('no theta: HOST_LOAD skipped, ratio printed', f['cls'] != 'HOST_LOAD' and f['load_ratio'] == 1.0, (f['cls'], f['load_ratio']))

# ---- holder
thr_out_present = [thr(0, 'Present', 'Present', H={'present': S}), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', R=S)]
f, _ = one('holder_out', 200000, dict(threads=thr_out_present), lat=BASE_LAT + E200 // 2 + (E200 % 2))
check('holder = output thread at lat - base = 0.5 E', f['holder'] == 'output' and f['cls'].startswith('EMU_CALL:present'), (f['holder'], f['cls']))
f, _ = one('holder_flip', 200000, dict(threads=thr_out_present), lat=BASE_LAT + E200 // 2 - 1)
check('holder = flip thread below 0.5 E', f['holder'] == 'flip' and f['cls'] == 'GUEST_RUN:DrawThread', (f['holder'], f['cls']))

# ---- H calls and RC7
LAT_OUT = BASE_LAT + E200


def h_case(name, call, others=None, gb=BASE_GB, cnt=S):
    th = [thr(0, 'Present', 'Present', H={call: cnt}, S=S - cnt), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', S=S)] + (others or [])
    return one(name, 200000, dict(threads=th), lat=LAT_OUT, gb=gb)[0]


for c in ('protect', 'fault', 'drain', 'qlock'):
    f = h_case('h_' + c, c)
    check('EMU_CALL:%s without split' % c, f['cls'] == 'EMU_CALL:' + c and f['family'] == 'EMU_CALL', f['cls'])
for c in R.DRIVER:
    f = h_case('hd_' + c, c)
    check('EMU_CALL:%s>DRV_HOST' % c, f['cls'] == 'EMU_CALL:%s>DRV_HOST' % c and f['family'] == 'DRV_HOST', f['cls'])
f = h_case('h_lock', 'present', [thr(3, 'ASubmit', 'ASubmit', H={'qlock': S // 2}, S=S // 2)])
check('RC7 EMU_LOCK: another thread H:qlock = 0.5 samples', f['cls'] == 'EMU_CALL:present>EMU_LOCK', f['cls'])
f = h_case('h_lock_lt', 'present', [thr(3, 'ASubmit', 'ASubmit', H={'qlock': S // 2 - 1}, S=S // 2 + 1)])
check('RC7 not EMU_LOCK below 0.5', f['cls'] == 'EMU_CALL:present>DRV_HOST', f['cls'])
f = h_case('h_gpu', 'present', gb=BASE_GB + E200 // 2 + (E200 % 2))
check('RC7 DRV_GPU at gpu_busy = base + 0.5 E', f['cls'] == 'EMU_CALL:present>DRV_GPU', f['cls'])
f = h_case('h_gpu_lt', 'present', gb=BASE_GB + E200 // 2 - 1)
check('RC7 DRV_HOST below', f['cls'] == 'EMU_CALL:present>DRV_HOST', f['cls'])
th = [thr(0, 'Present', 'Present', H={'present': S}), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', S=S)]
f = one('h_gpu_eq', 200001, dict(threads=th), lat=BASE_LAT + E2, gb=BASE_GB + E2 // 2)[0]
check('RC7 DRV_GPU at gpu_busy = base + 0.5 E exactly (even E)', f['cls'] == 'EMU_CALL:present>DRV_GPU', f['cls'])
f = one('holder_eq', 200001, dict(threads=th), lat=BASE_LAT + E2 // 2)[0]
check('holder = output at lat - base = 0.5 E exactly (even E)', f['holder'] == 'output', f['holder'])
th = [thr(0, 'Present', 'Present', H={'present': S // 2, 'qlock': S // 2}), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', S=S)]
f = one('h_self_lock', 200000, dict(threads=th), lat=LAT_OUT)[0]
check('RC7: the holder own H:qlock is not EMU_LOCK (tie present / qlock -> present)', f['cls'] == 'EMU_CALL:present>DRV_HOST', f['cls'])
f = h_case('h_half', 'protect', cnt=S // 2)
check('H share exactly 50 % counts', f['cls'] == 'EMU_CALL:protect', f['cls'])
f = h_case('h_lthalf', 'protect', cnt=S // 2 - 1)
check('H share below 50 % does not count', f['cls'] != 'EMU_CALL:protect', f['cls'])
th = [thr(0, 'Present', 'Present', H={'protect': S // 2}, W={'cond': S // 2}), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', S=S)]
f = one('tie_hw', 200000, dict(threads=th), lat=LAT_OUT)[0]
check('tie H 50 % / W 50 % -> H', f['cls'] == 'EMU_CALL:protect', f['cls'])

# ---- W, wakers, RC5, RC6
GPU_OK = thr(1, 'Gpu', 'Gpu', r=S)


def w_case(name, holder_row, others=None, waits=None, gpu=GPU_OK):
    th = [thr(0, 'Present', 'Present', S=S), gpu, holder_row] + (others or [])
    return one(name, 200000, dict(threads=th, waits=waits or []))[0]


f = w_case('w_step', thr(2, 'DrawThread', 'guest', W={'cond': S}),
           [thr(3, 'Physics', 'guest', R=S)], [dict(slot=2, kind='cond', waker=3, overlap=150000)])
check('W:cond -> step to the waker -> GUEST_RUN:Physics', f['cls'] == 'GUEST_RUN:Physics' and len(f['path']) == 2, (f['cls'], f['path']))
f = w_case('w_best', thr(2, 'DrawThread', 'guest', W={'cond': S}),
           [thr(3, 'Physics', 'guest', R=S), thr(4, 'Audio', 'guest', Sr=S)],
           [dict(slot=2, kind='cond', waker=3, overlap=50000), dict(slot=2, kind='cond', waker=4, overlap=150000)])
check('W: the record with the largest overlap', f['cls'] == 'HOST_PREEMPT', f['cls'])
f = w_case('w_emu', thr(2, 'DrawThread', 'guest', W={'eq': S}), [], [dict(slot=2, kind='eq', waker=1)], gpu=thr(1, 'Gpu', 'Gpu', R=S))
check('W:eq -> waker GuestGpu in R -> EMU_RUN:Gpu', f['cls'] == 'EMU_RUN:Gpu' and f['term_role'] == 'Gpu', f['cls'])
f = w_case('w_to', thr(2, 'DrawThread', 'guest', W={'cond': S}), [thr(3, 'Physics', 'guest', R=S)],
           [dict(slot=2, kind='cond', waker=3, to=1)])
check('W timeout record -> GUEST_SLEEP:cond', f['cls'] == 'GUEST_SLEEP:cond', f['cls'])
f = w_case('w_nowaker', thr(2, 'DrawThread', 'guest', W={'sem': S}))
check('W without a record -> GUEST_SLEEP:sem', f['cls'] == 'GUEST_SLEEP:sem', f['cls'])
f = w_case('w_waker_neg', thr(2, 'DrawThread', 'guest', W={'sem': S}), [], [dict(slot=2, kind='sem', waker=-1)])
check('W record waker -1 -> GUEST_SLEEP:sem', f['cls'] == 'GUEST_SLEEP:sem', f['cls'])

# ---- item 574 (d), item 581 (v)(2), (v)(5): waker, record peer, EMU_WAIT / GUEST_SLEEP by kind
GPU_SW = thr(1, 'Gpu', 'Gpu', Sw=S)
f = w_case('d_waker', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=1)], gpu=GPU_SW)
check('(d) EMU kind with a waker -> step to the waker -> UNMARKED:Gpu', f['cls'] == 'UNMARKED:Gpu' and f['path'][0].endswith('->waker'),
      (f['cls'], f['path']))
f = w_case('d_peer', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=-1, peer=1)], gpu=GPU_SW)
check('(d) EMU kind without a waker, record peer 1 -> step to the peer -> UNMARKED:Gpu', f['cls'] == 'UNMARKED:Gpu' and
      f['path'][0].endswith('->peer') and len(f['path']) == 2, (f['cls'], f['path']))
f = w_case('d_peer0', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=-1, peer=0)])
check('(d) record peer 0 is a slot (>= 0) -> step to slot 0 (Present S) -> UNMARKED:Present', f['cls'] == 'UNMARKED:Present', f['cls'])
f = w_case('d_both', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [thr(3, 'Physics', 'guest', R=S)],
           [dict(slot=2, kind='gpu_wait', waker=3, peer=1)], gpu=GPU_SW)
check('(d) the waker goes before the record peer', f['cls'] == 'GUEST_RUN:Physics', f['cls'])
f = w_case('d_cond_peer', thr(2, 'DrawThread', 'guest', W={'cond': S}), [thr(3, 'Physics', 'guest', R=S)],
           [dict(slot=2, kind='cond', waker=-1, peer=3)])
check('(d) the record peer step is general (GUEST kind cond) -> GUEST_RUN:Physics', f['cls'] == 'GUEST_RUN:Physics', f['cls'])
f = w_case('d_emu_none', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=-1, peer=-1)],
           gpu=thr(1, 'Gpu', 'Gpu', R=S))
check('(d) EMU kind without waker and peer -> EMU_WAIT:gpu_wait (no RC6 with GuestGpu R)', f['cls'] == 'EMU_WAIT:gpu_wait' and
      f['family'] == 'EMU_WAIT', (f['cls'], f['family']))
f = w_case('d_emu_norec', thr(2, 'DrawThread', 'guest', W={'flip_done': S}))
check('(d) EMU kind without a record -> EMU_WAIT:flip_done', f['cls'] == 'EMU_WAIT:flip_done', f['cls'])
f = w_case('d_emu_tpeer', thr(2, 'DrawThread', 'guest', W={'emu_mutex': S}, peer=5), [thr(5, 'Loader', 'guest', R=S)])
check('(d) emu_mutex without a record: -t peer only as the executor variant -> EMU_WAIT:emu_mutex',
      f['cls'] == 'EMU_WAIT:emu_mutex' and 'executor variant (the -t peer for any kind): step to slot 5' in f['note'], (f['cls'], f['note']))
f = w_case('d_mutex_tpeer', thr(2, 'DrawThread', 'guest', W={'mutex': S}, peer=5), [thr(5, 'Loader', 'guest', R=S)],
           [dict(slot=2, kind='mutex', waker=-1, peer=-1)])
check('(d) mutex record without waker and peer -> the -t peer as before -> GUEST_RUN:Loader', f['cls'] == 'GUEST_RUN:Loader' and
      f['path'][0].endswith('->tpeer'), (f['cls'], f['path']))
f = w_case('d_emu_to0', thr(2, 'DrawThread', 'guest', W={'vo_pace': S}), [], [dict(slot=2, kind='vo_pace', waker=-1, to=1, req=0)])
check('RC5 (v): EMU kind timeout without a guest deadline (req_us 0) -> EMU_WAIT, the other reading printed',
      f['cls'] == 'EMU_WAIT:vo_pace' and 'GUEST_SLEEP:vo_pace' in f['note'], (f['cls'], f['note']))
f = w_case('d_emu_to1', thr(2, 'DrawThread', 'guest', W={'net': S}), [thr(3, 'X', 'guest', R=S)],
           [dict(slot=2, kind='net', waker=3, to=1, req=16000)])
check('RC5 (v): EMU kind timeout with a guest deadline (req_us > 0) -> GUEST_SLEEP:net', f['cls'] == 'GUEST_SLEEP:net', f['cls'])
f = w_case('d_emu_to_wk', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [thr(3, 'X', 'guest', R=S)],
           [dict(slot=2, kind='gpu_wait', waker=3, to=1, req=0)])
check('RC5 (v): EMU kind timeout, req_us 0, waker 3 -> step -> GUEST_RUN:X', f['cls'] == 'GUEST_RUN:X', f['cls'])
f = w_case('d_vblank_peer', thr(2, 'DrawThread', 'guest', W={'vblank': S}), [], [dict(slot=2, kind='vblank', waker=-1, peer=0)])
check('vblank with peer = Present -> step to Present (S) -> UNMARKED:Present', f['cls'] == 'UNMARKED:Present', f['cls'])
f = w_case('d_selfpeer', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=-1, peer=2)])
check('a record peer equal to its own slot -> cycle -> UNDETERMINED', f['cls'] == 'UNDETERMINED' and 'cycle' in f['note'], (f['cls'], f['note']))
EMU_KINDS = ('emu_mutex', 'gpu_wait', 'gpu_cmd', 'flip_slot', 'flip_done', 'flip_cancel', 'flip_req', 'vo_pace', 'relay', 'frame_pool',
             'rec_wait', 'rec_idle', 'asub_idle', 'asub_drain', 'ops_wait', 'ops_idle', 'pipe_wait', 'pcopy', 'pm_drain', 'vma_flush',
             'rec_queue', 'main_task', 'main_idle', 'spin', 'av', 'vblank', 'audio', 'aio', 'net', 'emu_join')
GUEST_KINDS = ('cond', 'mutex', 'sem', 'psem', 'evf', 'eq', 'once', 'join', 'addr', 'fiber', 'ult', 'rwlock')
check('EMU_WAITS = the list of item 574 (d) and 581 (v)(5) (30 kinds)', set(R.EMU_WAITS) == set(EMU_KINDS) and len(R.EMU_WAITS) == 30,
      sorted(set(R.EMU_WAITS) ^ set(EMU_KINDS)))
check('GUEST_WAITS = the older kinds + once, join, addr, fiber, ult, rwlock', set(R.GUEST_WAITS) == set(GUEST_KINDS) | {'sleep', 'gpu_idle',
      'gpu_regmem'}, sorted(R.GUEST_WAITS))
check('every kind is EMU or GUEST, not both', set(R.WAITS) == set(R.EMU_WAITS) | set(R.GUEST_WAITS) and not set(R.EMU_WAITS) & set(R.GUEST_WAITS))
for k in EMU_KINDS:
    f = w_case('k_' + k, thr(2, 'DrawThread', 'guest', W={k: S}), [], [dict(slot=2, kind=k, waker=-1, peer=-1)])
    check('kind %s without waker and peer -> EMU_WAIT:%s' % (k, k), f['cls'] == 'EMU_WAIT:' + k and f['family'] == 'EMU_WAIT', f['cls'])
for k in GUEST_KINDS:
    f = w_case('k_' + k, thr(2, 'DrawThread', 'guest', W={k: S}), [], [dict(slot=2, kind=k, waker=-1, peer=-1)])
    check('kind %s without waker and peer -> GUEST_SLEEP:%s' % (k, k), f['cls'] == 'GUEST_SLEEP:' + k and f['family'] == 'GUEST_SLEEP', f['cls'])
    f = w_case('kp_' + k, thr(2, 'DrawThread', 'guest', W={k: S}), [thr(3, 'Physics', 'guest', R=S)], [dict(slot=2, kind=k, waker=-1, peer=3)])
    check('kind %s with a record peer -> step -> GUEST_RUN:Physics' % k, f['cls'] == 'GUEST_RUN:Physics', f['cls'])
f = w_case('k_join_rc6', thr(2, 'DrawThread', 'guest', W={'join': S}), [], [dict(slot=2, kind='join', waker=-1)], gpu=thr(1, 'Gpu', 'Gpu', R=S))
check('GUEST kind join keeps RC6 -> GUEST_POLL', f['cls'] == 'GUEST_POLL', f['cls'])
# the kind names against the enum of the reviewed code (WaitName of 35b454c6, = f2307b02 byte for byte)
_src = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', '35b454c6:src/common/diagB32.cpp'],
                      capture_output=True).stdout.decode('utf-8', 'replace')
_i = _src.find('const char* WaitName(uint8_t kind) {')
_blk = _src[_i:_src.find('static_assert', _i)]
import re as _re  # noqa: E402
_names = _re.findall(r'"([a-z_]+|-)"', _blk)
check('WAITS = WaitName of 35b454c6 (binary B) in order (45 kinds)', _names[1:] == list(R.WAITS) and len(R.WAITS) == 45, (_names[1:4], len(_names)))
_h = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', '35b454c6:src/common/diagB32.h'],
                    capture_output=True).stdout.decode('utf-8', 'replace')
_j = _h.find('constexpr bool IsEmuWait(uint8_t kind) {')
_emu = _h[_j:_h.find('}', _j)]
check('IsEmuWait of 35b454c6: EmuMutex .. Av plus Vblank, Audio, Aio, Net, EmuJoin', all('Wait::%s)' % k in _emu for k in
      ('Vblank', 'Audio', 'Aio', 'Net', 'EmuJoin')) and 'kind >= kFirstEmuWait && kind < kFirstGuestHleWait' in _emu and
      _emu.count('Wait::') == 5, _emu[:200])
f = w_case('w_sleep', thr(2, 'DrawThread', 'guest', W={'sleep': S}), [thr(3, 'X', 'guest', R=S)], [dict(slot=2, kind='sleep', waker=3)])
check('W:sleep -> GUEST_SLEEP:sleep', f['cls'] == 'GUEST_SLEEP:sleep', f['cls'])
f = w_case('w_mutex', thr(2, 'DrawThread', 'guest', W={'mutex': S}, peer=5), [thr(5, 'Loader', 'guest', R=S)])
check('W:mutex without a record -> step to the -t peer', f['cls'] == 'GUEST_RUN:Loader', f['cls'])
f = w_case('w_mutex_rec', thr(2, 'DrawThread', 'guest', W={'mutex': S}, peer=-1), [thr(5, 'Loader', 'guest', Sw=S)],
           [dict(slot=2, kind='mutex', waker=5)])
check('W:mutex record waker (= peer) -> UNMARKED:Loader', f['cls'] == 'UNMARKED:Loader', f['cls'])
f = w_case('w_kind', thr(2, 'DrawThread', 'guest', W={'cond': S}), [thr(3, 'Physics', 'guest', R=S)],
           [dict(slot=2, kind='sem', waker=3)])
check('W: a record of another kind is not used', f['cls'] == 'GUEST_SLEEP:cond', f['cls'])
f = w_case('rc6_busy', thr(2, 'DrawThread', 'guest', R=S), gpu=thr(1, 'Gpu', 'Gpu', R=S // 4, H={'qsubmit': S // 4}, S=S // 2))
check('RC6: GuestGpu R + H = 50 % -> GUEST_POLL', f['cls'] == 'GUEST_POLL', f['cls'])
f = w_case('rc6_busy_lt', thr(2, 'DrawThread', 'guest', R=S), gpu=thr(1, 'Gpu', 'Gpu', R=S // 4, H={'qsubmit': S // 4 - 1}, S=S // 2 + 1))
check('RC6: GuestGpu R + H < 50 % -> GUEST_RUN', f['cls'] == 'GUEST_RUN:DrawThread', f['cls'])
f = w_case('rc6_regmem', thr(2, 'DrawThread', 'guest', W={'sem': S}), gpu=thr(1, 'Gpu', 'Gpu', W={'gpu_regmem': S // 2}, S=S // 2))
check('RC6: GuestGpu W:gpu_regmem = 50 % -> GUEST_POLL (from GUEST_SLEEP)', f['cls'] == 'GUEST_POLL', f['cls'])
th = [thr(0, 'Present', 'Present', S=S), thr(2, 'DrawThread', 'guest', R=S)]
f = one('rc6_nogpu', 200000, dict(threads=th, gpu=1))[0]
check('RC6: no GuestGpu row -> UNDETERMINED', f['cls'] == 'UNDETERMINED', f['cls'])
f = w_case('gpu_regmem_chain', thr(2, 'DrawThread', 'guest', W={'eq': S}), [], [dict(slot=2, kind='eq', waker=1)],
           gpu=thr(1, 'Gpu', 'Gpu', W={'gpu_regmem': S}))
check('chain to GuestGpu in W:gpu_regmem (no waker) -> GUEST_POLL', f['cls'] == 'GUEST_POLL', f['cls'])

# ---- R, Sr, Sw, S, none
f = w_case('r_emu', thr(2, 'Record', 'Record', R=S))
check('R on an emulator thread -> EMU_RUN:Record', f['cls'] == 'EMU_RUN:Record', f['cls'])
f = w_case('sr', thr(2, 'DrawThread', 'guest', Sr=S))
check('Sr -> HOST_PREEMPT', f['cls'] == 'HOST_PREEMPT', f['cls'])
f = w_case('sw', thr(2, 'DrawThread', 'guest', Sw=S))
check('Sw -> UNMARKED:DrawThread', f['cls'] == 'UNMARKED:DrawThread', f['cls'])
f = w_case('s', thr(2, 'DrawThread', 'guest', S=S))
check('S -> UNMARKED:DrawThread', f['cls'] == 'UNMARKED:DrawThread', f['cls'])
f, _ = one('kstate0', 200000, dict(kstate=0))
check('kstate = 0: UNMARKED with the note', f['cls'] == 'UNMARKED:DrawThread' and 'kstate=0' in f['note'], (f['cls'], f['note']))
f = w_case('swS', thr(2, 'DrawThread', 'guest', Sw=S // 2 - 1, S=S // 2 - 1, r=2))
check('Sw 19 + S 19 of 40: UNDETERMINED by the letter, executor variant UNMARKED printed',
      f['cls'] == 'UNDETERMINED' and 'executor variant (Sw + S >= 50 %): UNMARKED:DrawThread' in f['note'], (f['cls'], f['note']))
f = w_case('swS_lt', thr(2, 'DrawThread', 'guest', Sw=S // 2 - 1, S=0, r=S // 2 + 1))
check('Sw + S < 50 %: no variant', f['cls'] == 'UNDETERMINED' and 'variant' not in f['note'], f['note'])
f = w_case('none', thr(2, 'DrawThread', 'guest', R=S // 2 - 1, r=S // 2 + 1))
check('no state >= 50 % (r not RUN) -> UNDETERMINED', f['cls'] == 'UNDETERMINED', f['cls'])
f = w_case('r_only', thr(2, 'DrawThread', 'guest', r=S))
check('r = 100 % is not R -> UNDETERMINED', f['cls'] == 'UNDETERMINED', f['cls'])

# ---- chain length, cycle, missing row
th = [thr(0, 'Present', 'Present', S=S), GPU_OK, thr(2, 'A', 'guest', W={'cond': S}), thr(3, 'B', 'guest', W={'cond': S}),
      thr(4, 'C', 'guest', W={'cond': S}), thr(5, 'D', 'guest', R=S)]
ws = [dict(slot=2, kind='cond', waker=3), dict(slot=3, kind='cond', waker=4), dict(slot=4, kind='cond', waker=5)]
f = one('chain3', 200000, dict(threads=th, waits=ws))[0]
check('chain holder + 3 steps ending in R -> GUEST_RUN:D', f['cls'] == 'GUEST_RUN:D' and len(f['path']) == 4, (f['cls'], f['path']))
th2 = th[:-1] + [thr(5, 'D', 'guest', W={'cond': S}), thr(6, 'E', 'guest', R=S)]
f = one('chain4', 200000, dict(threads=th2, waits=ws + [dict(slot=5, kind='cond', waker=6)]))[0]
check('a 4th step -> UNDETERMINED', f['cls'] == 'UNDETERMINED' and '> 3' in f['note'], (f['cls'], f['note']))
f = one('cycle', 200000, dict(threads=th[:4], waits=[dict(slot=2, kind='cond', waker=3), dict(slot=3, kind='cond', waker=2)]))[0]
check('cycle -> UNDETERMINED', f['cls'] == 'UNDETERMINED' and 'cycle' in f['note'], (f['cls'], f['note']))
f = one('missing', 200000, dict(threads=th[:3], waits=[dict(slot=2, kind='cond', waker=9)]))[0]
check('waker without a -t row -> UNDETERMINED', f['cls'] == 'UNDETERMINED' and 'no -t row' in f['note'], (f['cls'], f['note']))
f = one('noflip', 200000, dict(flip=-1))[0]
check('no holder slot -> UNDETERMINED', f['cls'] == 'UNDETERMINED' and 'holder' in f['note'], (f['cls'], f['note']))

# ==== F25 members (item 596 (d) with item 599 (b), item 600 (b)(4), item 602 (v)(2))
GUEST_R = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', R=S)]
K2 = 2000000
E_K2 = K2 - BASE_DT


def k2_one(name, dt=K2, kw=None, extra=None, **bk):
    n = FIRST + T0
    blk = diag_block(n, dt, threads=GUEST_R, **(kw or {}))
    t = {T0: dict(dt=dt, diag=blk)}
    t.update(extra or {})
    res = read(name, build(t, **bk))
    return frame(res, T0), res


# ---- (d)(2) the key window
f, res = k2_one('key_n')
check('key: window n with dt >= 0.5 x frame -> branch n', f['key'] == FIRST + T0 and f['key_branch'] == 'n', (f['key'], f['key_branch']))
n = FIRST + T0
res = read('key_n1', build({T0: dict(dt=K2, diag=None), T0 + 1: dict(dt=BASE_DT, diag=diag_block(n + 1, K2 + 10, threads=GUEST_R))}))
f = frame(res, T0)
check('key: no window n, window n + 1 qualifies -> branch n + 1', f['key'] == n + 1 and f['key_branch'] == 'n+1' and
      f['cls'] == 'GUEST_RUN:DrawThread', (f['key'], f['cls']))
res = read('key_small_n', build({T0: dict(dt=K2, diag=diag_block(n, K2 // 2 - 1, threads=GUEST_R)),
                                 T0 + 1: dict(dt=BASE_DT, diag=diag_block(n + 1, K2 // 2, threads=GUEST_R))}))
f = frame(res, T0)
check('key: window n at 0.5 x dt - 1 does not qualify, n + 1 at exactly 0.5 x dt does', f['key'] == n + 1, f['key'])
res = read('key_both', build({T0: dict(dt=K2, diag=diag_block(n, K2, threads=GUEST_R)),
                              T0 + 1: dict(dt=BASE_DT, diag=diag_block(n + 1, K2 + 1, threads=GUEST_R))}))
check('key: both qualify -> the larger dt_us (n + 1)', frame(res, T0)['key'] == n + 1, frame(res, T0)['key'])
res = read('key_both_eq', build({T0: dict(dt=K2, diag=diag_block(n, K2, threads=GUEST_R)),
                                 T0 + 1: dict(dt=BASE_DT, diag=diag_block(n + 1, K2, threads=GUEST_R))}))
check('key: both qualify with equal dt_us -> n (the tie keeps n)', frame(res, T0)['key'] == n, frame(res, T0)['key'])
res = read('key_none', build({T0: dict(dt=K2, diag=diag_block(n, K2 // 2 - 1, threads=GUEST_R)),
                              T0 + 1: dict(dt=BASE_DT, diag=diag_block(n + 1, K2 // 2 - 1, threads=GUEST_R))}))
f = frame(res, T0)
check('key: none qualifies -> NO_SAMPLES:key, in K (RC11)', f['cls'] == 'NO_SAMPLES:key' and f['family'] == 'NO_SAMPLES' and f['in_count'] and
      res['K'] == 1 and res['K_I'] == 1 and res['hold_class'] == 'NO_SAMPLES:key', (f['cls'], f['in_count'], res['K']))
res = read('key_nodiag', build({T0: dict(dt=K2, diag=None)}))
f = frame(res, T0)
check('key: no DiagB32 line at all -> NO_SAMPLES:key in count', f['cls'] == 'NO_SAMPLES:key' and f['in_count'] and f['key'] is None, f)
# the b32_pa frames 8796-8798 (log of b32_pa F20l3: FrameTrace dt 977 768 / 860 521 / 1 478 862, windows 8797 945 170 instr 129 247,
# 8798 2 333 729 instr 313 835; no window 8796), RC13 of F25c
PA = {T0: 977768, T0 + 1: 860521, T0 + 2: 1478862}
blk97 = diag_block(n + 1, 945170, instr=129247, threads=GUEST_R, sgap=10605)
blk98 = diag_block(n + 2, 2333729, instr=313835, threads=GUEST_R, sgap=14086)
res = read('key_pa', build({T0: dict(dt=PA[T0], diag=None), T0 + 1: dict(dt=PA[T0 + 1], diag=blk97, key_at=T0 + 1),
                            T0 + 2: dict(dt=PA[T0 + 2], diag=blk98, key_at=T0 + 3)}))
f6, f7, f8 = frame(res, T0), frame(res, T0 + 1), frame(res, T0 + 2)
check('b32_pa: frame 8796 -> window 8797 (branch n + 1)', f6['key'] == n + 1 and f6['key_branch'] == 'n+1', (f6['key'], f6['key_branch']))
check('b32_pa: frame 8797 -> window 8798 (both qualify, the larger)', f7['key'] == n + 2 and f7['key_branch'] == 'n+1', f7['key'])
check('b32_pa: frame 8798 -> window 8798 (branch n)', f8['key'] == n + 2 and f8['key_branch'] == 'n', f8['key'])
check('b32_pa: SHARED_WIN on 8797 and 8798, not on 8796', f7['shared'] and f8['shared'] and not f6['shared'], (f6['shared'], f7['shared'], f8['shared']))
check('b32_pa: 8796 and 8797 (< 1 s) are reference, 8798 (1 478 862 - 313 835 >= 1 s) in count, K 1',
      not f6['k2'] and not f7['k2'] and f8['in_count'] and res['K'] == 1 and res['in_count'] == 1, (f6['k2'], f8['in_count'], res['K']))
check('b32_pa: the reference frames before the counted one are precursors (within 5 s)', f6['precursor'] and f7['precursor'], (f6['precursor'], f7['precursor']))
check('b32_pa: SHARED_WIN - instr_us of the shared window for both frames (RC11)', f7['instr_us'] == f8['instr_us'] == 313835, (f7['instr_us'], f8['instr_us']))
check('key_window(): n 0.5 edge as a function', R.key_window(5, 10, {5: dict(hdr=dict(dt_us=5))}) == 5 and
      R.key_window(5, 11, {5: dict(hdr=dict(dt_us=5))}) is None and R.key_window(5, 10, {6: dict(hdr=dict(dt_us=5))}) == 6)

# ---- (d)(1) the K2 count: edges, INSTR_MADE_K2, K_I
f, res = k2_one('k2_edge_lo', dt=999999)
check('dt 999 999 is a reference frame (not K2), K 0', not f['k2'] and not f['in_count'] and res['K'] == 0 and res['K_I'] == 0, (f['k2'], res['K']))
f, res = k2_one('k2_edge', dt=1000000, kw=dict(instr=0))
check('dt 1 000 000, instr 0 -> in count, K 1', f['k2'] and f['in_count'] and res['K'] == 1, (f['k2'], f['in_count']))
f, res = k2_one('instr_k2', kw=dict(instr=K2 - 999999))
check('dt - instr = 999 999 -> INSTR_MADE_K2: K_I 1, K 0', f['instr_made_k2'] and not f['in_count'] and res['K_I'] == 1 and res['K'] == 0 and
      res['instr_made_k2'] == 1, (f['instr_made_k2'], res['K_I'], res['K']))
f, res = k2_one('instr_k2_ok', kw=dict(instr=K2 - 1000000))
check('dt - instr = 1 000 000 -> in count', f['in_count'] and not f['instr_made_k2'], f)
f, res = k2_one('t10_k2', dt=K2, dt_by_idx={1: BASE_DT + 100})
res = read('k2_t10', build({301: dict(dt=K2, diag=diag_block(FIRST + 301, K2, threads=GUEST_R))}, dt_by_idx={1: BASE_DT + 100}))
check('K2 frame starting at exactly 10 s counts', frame(res, 301) is not None and frame(res, 301)['in_count'], frame(res, 301))
res = read('k2_t10m', build({301: dict(dt=K2, diag=diag_block(FIRST + 301, K2, threads=GUEST_R))}, dt_by_idx={1: BASE_DT + 99}))
check('K2 frame starting at 9.999 999 s is not a hold frame', frame(res, 301) is None and res['K'] == 0)
res = read('k2_nohold', build({T0: dict(dt=K2, diag=diag_block(FIRST + T0, K2, threads=GUEST_R))}, nframes=2000))
check('no hold (scene < 300 s, no abort): K and K_I 0, frame still in count', res['K'] == 0 and res['K_I'] == 0 and frame(res, T0)['in_count'],
      (res['K'], res['hold_any']))
res = read('k2_two', build({T0: dict(dt=K2, diag=diag_block(FIRST + T0, K2, threads=GUEST_R)),
                            T0 + 400: dict(dt=K2 + 1000000, diag=diag_block(FIRST + T0 + 400, K2 + 1000000, sgap=K2))}))
check('hold class = class of the longest frame in count (HOST_FREEZE 3 s over GUEST_RUN 2 s)', res['hold_class'] == 'HOST_FREEZE' and
      res['in_count'] == 2, (res['hold_class'], res['in_count']))
# precursor edges (item 596 (d)(1)): a 200 ms reference frame starting exactly 5 000 000 us / 5 000 001 us before the counted frame
for last, want in ((33381, True), (33382, False)):
    dts = dict((T0 + k, BASE_DT) for k in range(1, 144))
    dts[T0 + 144] = last
    res = read('precursor_%d' % last, build({T0: dict(dt=200000, diag=None), T0 + 145: dict(dt=K2, diag=diag_block(FIRST + T0 + 145, K2,
                                                                                                                 threads=GUEST_R))},
                                            dt_by_idx=dts))
    dist = frame(res, T0 + 145)['t_us'] - frame(res, T0)['t_us']
    check('precursor: reference frame starting %d us before the counted frame -> %s' % (dist, want), frame(res, T0)['precursor'] == want and
          dist == 200000 + 143 * BASE_DT + last, (dist, frame(res, T0)['precursor']))

# ---- (d)(1), RC14: attribution B5 / B1b / B33 is reference
res = read('att_b5', build({T0: dict(dt=K2, diag=diag_block(FIRST + T0, K2, threads=GUEST_R))}, b5_idx=(T0,)))
check('B5 K2 frame (dump line) is reference: not P_I, K 0, K_I 0', frame(res, T0)['attr'] == 'B5' and not frame(res, T0)['in_count'] and
      res['K'] == 0 and res['K_I'] == 0, (frame(res, T0)['attr'], res['K']))
res = read('att_b1b', build({T0: dict(dt=K2, diag=diag_block(FIRST + T0, K2, threads=GUEST_R))}, before={T0: ['BvhLoopCapTrip: x']}))
check('B1b K2 frame is reference', frame(res, T0)['attr'] == 'B1b' and res['K'] == 0, frame(res, T0)['attr'])
_pcs = build({T0: dict(dt=K2, diag=diag_block(FIRST + T0, K2, threads=GUEST_R))}, before={T0: ['Vulkan pipeline cache: saved 1 KB']})
res = read('att_pcs_b', _pcs)
check('binary B: a cache save is no attribution (F20c letter after S12) -> the K2 frame counts', frame(res, T0)['attr'] == 'nothing' and
      res['K'] == 1, frame(res, T0)['attr'])
_save = R.BIN_B
R.BIN_B = '9235a7ac' + 'f' * 56
try:
    res = read('att_b33', _pcs)
finally:
    R.BIN_B = _save
check('RC14: a frame the F20c reader attributes to B33 (binary before S12) is reference: K 0, K_I 0', frame(res, T0)['attr'] == 'B33' and
      not frame(res, T0)['p_i'] and res['K'] == 0 and res['K_I'] == 0, (frame(res, T0)['attr'], res['K']))

# ---- (d)(3) member (0) and NO_SAMPLES:trunc (item 599 (b)(1), (3), (4))
EDGE = R.ENV_US
f, _ = k2_one('env_in', dt=EDGE, kw=dict(sgap=5000))
check('window dt_us = 20 475 000 is inside the envelope (classified on)', f['cls'] == 'GUEST_RUN:DrawThread', f['cls'])
f, _ = k2_one('env_out', dt=EDGE + 1, kw=dict(sgap=5000))
check('window dt_us = 20 475 001 -> NO_SAMPLES:cover (envelope)', f['cls'] == 'NO_SAMPLES:cover' and 'envelope' not in f['note'] or
      f['cls'] == 'NO_SAMPLES:cover', (f['cls'], f['note']))
f, _ = k2_one('env_out_inv', dt=EDGE + 1, kw=dict(sgap=5000, xw={'torn_w': 1}, w_cut_w=3))
check('outside the envelope the invariants are reference: still NO_SAMPLES:cover', f['cls'] == 'NO_SAMPLES:cover', f['cls'])
f, _ = k2_one('hexh1', kw=dict(hist_exh_w=1))
check('hist_exh_w 1 -> NO_SAMPLES:cover', f['cls'] == 'NO_SAMPLES:cover' and 'hist_exh_w' in f['note'], (f['cls'], f['note']))
f, _ = k2_one('hexh1_agree', kw=dict(hist_exh_w=1, cover=1000))
check('hist_exh_w 1 with a broken agreement -> NO_SAMPLES:cover (the agreement only at hist_exh_w 0)', f['cls'] == 'NO_SAMPLES:cover', f['cls'])
f, _ = k2_one('agree_edge', kw=dict(sgap=5000, cover=K2 - 5001))
check('agreement: dt - cover = sgap + 1 -> holds', f['cls'] == 'GUEST_RUN:DrawThread', f['cls'])
f, _ = k2_one('agree_bad', kw=dict(sgap=5000, cover=K2 - 5002))
check('agreement: dt - cover = sgap + 2 -> NO_SAMPLES:trunc', f['cls'] == 'NO_SAMPLES:trunc' and 'agreement' in f['note'], (f['cls'], f['note']))
f, _ = k2_one('agree_before_freeze', kw=dict(sgap=E_K2, cover=0))
check('member (0) goes before (i): broken agreement with sgap >= 0.5 E -> NO_SAMPLES:trunc', f['cls'] == 'NO_SAMPLES:trunc', f['cls'])
f, _ = k2_one('freeze_k2', kw=dict(sgap=E_K2 // 2 + 1))
check('(i) HOST_FREEZE on a K2 window (cover = dt - sgap)', f['cls'] == 'HOST_FREEZE', f['cls'])
f, _ = k2_one('freeze_k2_lt', kw=dict(sgap=E_K2 // 2 - 1))
check('(i) not HOST_FREEZE below 0.5 E', f['cls'] != 'HOST_FREEZE', f['cls'])
for fld in R.ZERO_F25:
    f, _ = k2_one('drop_' + fld, kw=dict(drop=(fld,)))
    check('NO_SAMPLES:trunc when the -x field %s is absent' % fld, f['cls'] == 'NO_SAMPLES:trunc' and fld in f['note'], (f['cls'], f['note']))
for fld in ('flip_ns', 'cover_us', 'sgap_max_us'):
    f, _ = k2_one('droph_' + fld, kw=dict(drop=(fld,)))
    check('NO_SAMPLES:trunc when the header field %s is absent' % fld, f['cls'] == 'NO_SAMPLES:trunc' and fld in f['note'], (f['cls'], f['note']))
f, _ = k2_one('drop_x', kw=dict(x=False))
check('NO_SAMPLES:trunc when the -x line is absent', f['cls'] == 'NO_SAMPLES:trunc' and 'no -x line' in f['note'], (f['cls'], f['note']))
f, _ = k2_one('t_trunc', kw=dict(t_trunc=True))
check('NO_SAMPLES:trunc: a -t line without peer=', f['cls'] == 'NO_SAMPLES:trunc' and 'peer=' in f['note'], (f['cls'], f['note']))
f, _ = k2_one('w_trunc', kw=dict(w_trunc=True, waits=[dict(slot=2, kind='cond', waker=-1)]))
check('NO_SAMPLES:trunc: a -w line without peer_tid=', f['cls'] == 'NO_SAMPLES:trunc' and 'peer_tid=' in f['note'], (f['cls'], f['note']))
f, _ = k2_one('trunc_hdr_last', kw=dict(drop=('flip_ns',)))
check('the header last field not flip_ns is a trunc item too', 'header last field' in f['note'], f['note'])
for fld in R.ZERO_W:
    f, _ = k2_one('zw_' + fld, kw=dict(xw={fld: 1}, cum={fld[:-2]: 1}))
    check('(ii) NO_SAMPLES: %s = 1' % fld, f['cls'] == 'NO_SAMPLES' and fld in f['note'], (f['cls'], f['note']))
for fld, kw in (('w_cut_w', dict(w_cut_w=1)), ('others_cut_w', dict(others_cut_w=1))):
    f, _ = k2_one('zw_' + fld, kw=kw)
    check('(ii) NO_SAMPLES: %s = 1 (zero invariant, items 596 (d)(4), 599 (b)(9))' % fld, f['cls'] == 'NO_SAMPLES' and fld in f['note'],
          (f['cls'], f['note']))
f, _ = k2_one('zw_i2', kw=dict(i2=0))
check('(ii) NO_SAMPLES: i2 = 0', f['cls'] == 'NO_SAMPLES', f['cls'])
f, _ = k2_one('zw_s0', kw=dict(samples=0, sgap=1000))
check('(ii) NO_SAMPLES: samples = 0', f['cls'] == 'NO_SAMPLES', f['cls'])
f, _ = k2_one('cum_only', kw=dict(cum={'torn': 5}))
check('cumulative torn without torn_w is not NO_SAMPLES', f['cls'] == 'GUEST_RUN:DrawThread', f['cls'])
f, _ = k2_one('load_k2', kw=dict(other=int(0.4562 * 32 * K2)))
f2, _ = (None, None)
res = read('load_k2t', build({T0: dict(dt=K2, diag=diag_block(FIRST + T0, K2, threads=GUEST_R, other=int(0.4562 * 32 * K2) + 1))}), theta=0.4562)
check('(iii) HOST_LOAD on the whole window with theta 0.4562', frame(res, T0)['cls'] == 'HOST_LOAD', frame(res, T0)['cls'])

# ---- abort (item 599 (b)(2))
res = read('abort', build({}, stop_idx=T0, quit=False, extra_after={T0: ['GpuHangAbort: role=4 requested=1 known=0 current=0 after=22s',
                                                                        '--- Error ---']}))
check('GpuHangAbort after 13 s of the scene: abort hold, K 1, K_I 1, class NO_SAMPLES:abort, in count 1', res['abort_hold'] and
      res['hold_any'] and not res['hold'] and res['K'] == 1 and res['K_I'] == 1 and res['hold_class'] == 'NO_SAMPLES:abort' and
      res['in_count'] == 1 and res['hold_family'] == 'NO_SAMPLES', (res['abort'], res['K'], res['hold_class']))
res = read('abort_early', build({}, stop_idx=200, quit=False, extra_after={200: ['GpuHangAbort: role=4 after=22s']}))
check('GpuHangAbort at 6.7 s of the scene: no abort hold (interference by admission), K 0', res['abort'] is not None and
      not res['abort_hold'] and not res['hold_any'] and res['K'] == 0, res['abort'])
res = read('abort_10', build({}, stop_idx=300, quit=False, extra_after={300: ['GpuHangAbort: x']}, dt_by_idx={1: BASE_DT + 100}))
check('GpuHangAbort right after the frame ending at exactly 10 s -> abort hold', res['abort_hold'] and res['abort']['scene_t_s'] == 10.0,
      res['abort'])
res = read('abort_pre', build({}, stop_idx=0, quit=False, pre_scene=['GpuHangAbort: x']))
check('GpuHangAbort before the first scene frame -> no abort hold', res['abort'] is not None and not res['abort_hold'], res['abort'])

# ---- (d)(5) form
for nm, sem, fh, want in (('sem', K2 // 2, 0, 'FORM_SEM'), ('sem_lt', K2 // 2 - 1, 0, 'FORM_OTHER'), ('noflip', 0, K2 // 2, 'FORM_NOFLIP'),
                          ('noflip_lt', 0, K2 // 2 - 1, 'FORM_OTHER'), ('both', K2, K2, 'FORM_SEM')):
    res = read('form_' + nm, build({T0: dict(dt=K2, sem=sem, diag=diag_block(FIRST + T0, K2, threads=GUEST_R))},
                                   before={T0: ['FlipHold: us=%d present_us=1 poll_us=1 other_us=%d flip=%d' % (fh, fh, FIRST + T0 - 1)]}))
    check('form %s: semwait %d, FlipHold other_us %d -> %s' % (nm, sem, fh, want), frame(res, T0)['form'] == want and res['hold_form'] == want,
          frame(res, T0)['form'])
check('form_sig(): FlipHold of another interval is not read', R.form_sig(K2, 0, None) == 'FORM_OTHER')

# ---- (d)(5) M6_BURST and the offset calibration (item 600 (b)(4))
FN = 5 * 10 ** 12           # flip_ns of window n (FrameStats scale)
OFF = 123456789             # QPC = flip scale + OFF
blk = diag_block(FIRST + T0, K2, threads=GUEST_R, flip_ns=FN)
blk_e = diag_block(FIRST + 50, 150000, threads=GUEST_R, flip_ns=FN - 400 * 33333 * 1000)
txt = build({T0: dict(dt=K2, diag=blk), 50: dict(dt=150000, diag=blk_e)})
cal = {FIRST + T0: FN + OFF + 2000000, FIRST + 50: FN - 400 * 33333 * 1000 + OFF + 7000, FIRST + 51: 1}
m6_in = [dict(t=1.0, emu_t=1.0, qpc=FN + OFF - K2 * 1000 - 1500000000, foreign=8.0)]
res = read('m6_edge_lo', txt, m6=m6_in, cal=cal)
check('calibration: offset = min over windows of (first sight - flip_ns) = OFF + 7 000 ns (2 pairs)', res['cal']['offset'] == OFF + 7000 and
      res['cal']['pairs'] == 2 and res['cal']['n'] == FIRST + 50, res['cal'])
check('M6_BURST: a sample foreign 8.0 at window start - 1.5 s - 7 us (offset applied) -> False (outside)', frame(res, T0)['m6_burst'] is False,
      frame(res, T0)['m6_burst'])
m6_in = [dict(t=1.0, emu_t=1.0, qpc=FN + OFF + 7000 - K2 * 1000 - 1500000000, foreign=8.0)]
res = read('m6_edge_in', txt, m6=m6_in, cal=cal)
check('M6_BURST: foreign 8.0 exactly at window start - 1.5 s -> True', frame(res, T0)['m6_burst'] is True and res['hold_burst'] is True,
      frame(res, T0)['m6_burst'])
m6_in = [dict(t=1.0, emu_t=1.0, qpc=FN + OFF + 7000 + 1500000000, foreign=8.0)]
res = read('m6_edge_hi', txt, m6=m6_in, cal=cal)
check('M6_BURST: foreign 8.0 exactly at window end + 1.5 s -> True', frame(res, T0)['m6_burst'] is True, frame(res, T0)['m6_burst'])
m6_in = [dict(t=1.0, emu_t=1.0, qpc=FN + OFF + 7000 + 1500000001, foreign=9.0)]
res = read('m6_edge_hi1', txt, m6=m6_in, cal=cal)
check('M6_BURST: at window end + 1.5 s + 1 ns -> False', frame(res, T0)['m6_burst'] is False, frame(res, T0)['m6_burst'])
m6_in = [dict(t=1.0, emu_t=1.0, qpc=FN + OFF + 7000 - 1000, foreign=7.99)]
res = read('m6_low', txt, m6=m6_in, cal=cal)
check('M6_BURST: foreign 7.99 inside the window -> False', frame(res, T0)['m6_burst'] is False, frame(res, T0)['m6_burst'])
res = read('m6_nocal', txt, m6=m6_in, cal=None)
check('M6_BURST: no CAL lines -> NOT_DETERMINED', frame(res, T0)['m6_burst'] == 'NOT_DETERMINED' and res['cal']['offset'] is None,
      frame(res, T0)['m6_burst'])
res = read('m6_nopair', txt, m6=m6_in, cal={FIRST + 7: 5})
check('M6_BURST: CAL lines but no window seen -> NOT_DETERMINED', frame(res, T0)['m6_burst'] == 'NOT_DETERMINED' and res['cal']['pairs'] == 0,
      res['cal'])
res = read('m6_nom6', txt, m6=None, cal=cal)
check('M6_BURST: no M6 file -> NOT_DETERMINED', frame(res, T0)['m6_burst'] == 'NOT_DETERMINED', frame(res, T0)['m6_burst'])
check('calibrate(): one pair -> offset of that pair, second_minus_min None', R.calibrate({7: 100}, {7: dict(hdr=dict(flip_ns=40))})['offset'] == 60)
_d = os.path.join(TMP, 'm6files')
os.makedirs(_d, exist_ok=True)
open(os.path.join(_d, 'm6.txt'), 'w').write('2026-10-07T00:00:00Z t=1.0 emu_t=3.250 qpc_ns=77 game=1.00 loader=0.00 foreign=8.50 top=-\n'
                                           '2026-10-07T00:00:01Z t=2.0 emu_t=- qpc_ns=78 game=1.00 loader=0.00 foreign=0.10 top=-\nM6 end x\n')
open(os.path.join(_d, 'cal.txt'), 'w').write('CAL qpc_ns=10 n=5\nCAL qpc_ns=20 n=5\nCAL qpc_ns=30 n=6\n')
m6r = R.read_m6(os.path.join(_d, 'm6.txt'))
check('read_m6: two samples, emu_t 3.25 / None, qpc, foreign', len(m6r) == 2 and m6r[0]['emu_t'] == 3.25 and m6r[1]['emu_t'] is None and
      m6r[0]['qpc'] == 77 and m6r[0]['foreign'] == 8.5, m6r)
check('read_cal: the first sight of n kept', R.read_cal(os.path.join(_d, 'cal.txt')) == {5: 10, 6: 30})

# ---- U5 windows (item 596 (z), 599 (b)(3), 602 (v)(2))
res = read('u5_clean', build({T0: dict(dt=K2, diag=diag_block(FIRST + T0, K2, threads=GUEST_R))}))
check('U5: a clean window -> no bad windows', res['u5_bad_n'] == 0 and not res['u5_tag'], res['u5_bad'])
res = read('u5_torn', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, xw={'torn_w': 1}))}))
check('U5: torn_w 1 in a window -> bad', res['u5_tag'] and res['u5_bad'][0][1] == ['torn_w'], res['u5_bad'])
res = read('u5_trunc', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, t_trunc=True))}))
check('U5: a trunc item -> bad', res['u5_tag'], res['u5_bad'])
res = read('u5_agree', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, cover=0))}))
check('U5: a broken agreement -> bad', res['u5_tag'] and 'agreement' in res['u5_bad'][0][1], res['u5_bad'])
res = read('u5_env', build({T0: dict(dt=EDGE + 1, diag=diag_block(FIRST + T0, EDGE + 1, hist_exh_w=1, w_cut_w=2))}))
check('U5: a window > 20 475 000 is excluded (not bad)', not res['u5_tag'] and res['u5_excl'] == [(FIRST + T0, EDGE + 1)] or
      not res['u5_tag'] and res['u5_excl'] == [[FIRST + T0, EDGE + 1]], (res['u5_bad'], res['u5_excl']))
res = read('u5_hexh', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, hist_exh_w=1))}))
check('U5: hist_exh_w 1 inside the envelope -> bad', res['u5_tag'], res['u5_bad'])
for prev, want_bad in ((20000, False), (19999, True)):
    res = read('u5_h2_%d' % prev, build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, w_lines=prev)),
                                         T0 + 1: dict(dt=200000, diag=diag_block(FIRST + T0 + 1, 200000, xw={'sgap_bad_w': 1}))}))
    check('item 602 (v)(2): sgap_bad_w 1 after a window with %d -w lines -> %s' % (prev, 'bad' if want_bad else 'reference'),
          res['u5_tag'] == want_bad and (want_bad or res['u5_h2'] == [(FIRST + T0 + 1, 1, 20000)] or res['u5_h2'] == [[FIRST + T0 + 1, 1, 20000]]),
          (res['u5_bad'], res['u5_h2']))
res = read('u5_h2_other', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, w_lines=30000)),
                                 T0 + 1: dict(dt=200000, diag=diag_block(FIRST + T0 + 1, 200000, xw={'sgap_bad_w': 1, 'torn_w': 1}))}))
check('item 602 (v)(2): the exception is only for sgap_bad_w (torn_w of the same window stays bad)', res['u5_tag'] and
      res['u5_bad'][0][1] == ['torn_w'], res['u5_bad'])
res = read('u5_h2_gap', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, w_lines=30000)),
                               T0 + 2: dict(dt=200000, diag=diag_block(FIRST + T0 + 2, 200000, xw={'sgap_bad_w': 1}))}))
check('item 602 (v)(2): the window two flips later is not "right after" -> bad', res['u5_tag'], res['u5_bad'])

# ---- warm member and program hashes (item 596 (g), 599 (b)(7))
res = read('warm_ok', build({}, b5_idx=(5,), before={5: ['ShaderRecompiler VS phase begin: stage=VS hash=0x00000000000000aa code_words=1']}))
check('warm: a dump line at 0.1 s (< 10 s) -> warm', res['warm'] and res['warm_dump_n'] == 0, res['warm_dump_frames'])
res = read('warm_no', build({}, b5_idx=(T0,), before={T0: ['ShaderRecompiler PS phase begin: stage=PS hash=0x67955B311DF997BB code_words=2']}))
check('warm: a dump line at >= 10 s -> not warm, the program hash read', not res['warm'] and res['warm_dump_n'] == 1 and
      res['warm_dump_hashes'] == ['67955b311df997bb'], (res['warm'], res['warm_dump_hashes']))
check('the B5 frame list (reference) carries the dump frame only when >= 100 ms (33 ms here)', res['b5'] == [], res['b5'])

# ---- stand (pb / pc) rows are keyed too
THR_PB = [thr(0, 'Present', 'Present', H={'present': S}), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', R=S)]
res = read('stand_pb', build({T0 + 1: dict(dt=3200000, lat=BASE_LAT + 3200000, diag=diag_block(FIRST + T0 + 1, 3200000, instr=0,
                                                                                               threads=THR_PB))}, test_fire_idx=T0 + 1))
st = res['stand']
check('stand pb: 3 frames, the stand frame keyed (branch n) and EMU_CALL:present via the output thread', st and len(st) == 3 and
      st[0]['key'] == FIRST + T0 + 1 and st[0]['cls'].startswith('EMU_CALL:present') and st[0]['holder'] == 'output', st and st[0])
cm = R.control_members('f25_pb', res)
check('control pb: all members PASS', cm['ok'], [a for a, b in cm['members'] if not b])
res2 = read('stand_pb_short', build({T0 + 1: dict(dt=2999999, lat=BASE_LAT + 2999999, diag=diag_block(FIRST + T0 + 1, 2999999, instr=0,
                                                                                                     threads=THR_PB))}, test_fire_idx=T0 + 1))
cm = R.control_members('f25_pb', res2)
check('control pb: stand frame 2 999 999 < 3 s -> FAIL', not cm['ok'], cm['members'])
res2 = read('stand_pb_wcut', build({T0 + 1: dict(dt=3200000, lat=BASE_LAT + 3200000, diag=diag_block(FIRST + T0 + 1, 3200000, instr=0,
                                                                                                    threads=THR_PB, w_cut_w=1))},
                                   test_fire_idx=T0 + 1))
cm = R.control_members('f25_pb', res2)
check('control pb: w_cut_w 1 -> FAIL, the member lines_cut_w / w_cut_w / others_cut_w itself False', not cm['ok'] and
      mem(cm, 'lines_cut_w 0, w_cut_w 0') == [False], cm['members'])
res2 = read('stand_pb_cut', build({T0 + 1: dict(dt=3200000, lat=BASE_LAT + 3200000, diag=diag_block(FIRST + T0 + 1, 3200000, instr=0,
                                                                                                   threads=THR_PB, others_cut_w=1))},
                                  test_fire_idx=T0 + 1))
cm = R.control_members('f25_pb', res2)
check('control pb: others_cut_w 1 -> FAIL, the member itself False', not cm['ok'] and mem(cm, 'lines_cut_w 0, w_cut_w 0') == [False],
      cm['members'])
res2 = read('stand_pb_trunc', build({T0 + 1: dict(dt=3200000, lat=BASE_LAT + 3200000, diag=diag_block(FIRST + T0 + 1, 3200000, instr=0,
                                                                                                     threads=THR_PB)),
                                     T0 + 50: dict(dt=200000, diag=diag_block(FIRST + T0 + 50, 200000, w_trunc=True,
                                                                              waits=[dict(slot=2, kind='cond')]))}, test_fire_idx=T0 + 1))
check('control pb: a window of the tag with a -w line without peer_tid= -> FAIL (0 lines without the last field)',
      not R.control_members('f25_pb', res2)['ok'])
res2 = read('stand_pb_drv', build({T0 + 1: dict(dt=3200000, lat=BASE_LAT, diag=diag_block(FIRST + T0 + 1, 3200000, instr=0,
                                                                                         threads=THR_PB))}, test_fire_idx=T0 + 1))
check('control pb: holder = flip thread (DrawThread R) -> class GUEST_RUN -> FAIL', not R.control_members('f25_pb', res2)['ok'],
      res2['stand'][0]['cls'])
THR_PC = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', Sw=S), thr(2, 'DrawThread', 'guest', W={'gpu_wait': S})]
res = read('stand_pc', build({T0 + 1: dict(dt=6200000, diag=diag_block(FIRST + T0 + 1, 6200000, instr=0, threads=THR_PC,
                                                                     waits=[dict(slot=2, kind='gpu_wait', waker=-1, peer=1)]))},
                             test_fire_idx=T0 + 1, stand_mode='gpusleep'))
cm = R.control_members('f25_pc', res)
check('control pc: UNMARKED:Gpu, 6.2 s, all members PASS', cm['ok'] and res['stand'][0]['cls'] == 'UNMARKED:Gpu', [a for a, b in cm['members'] if not b])
res2 = read('stand_pc_freeze', build({T0 + 1: dict(dt=6200000, diag=diag_block(FIRST + T0 + 1, 6200000, instr=0, threads=THR_PC,
                                                                             sgap=4000000, waits=[dict(slot=2, kind='gpu_wait', peer=1)]))},
                                     test_fire_idx=T0 + 1, stand_mode='gpusleep'))
cm = R.control_members('f25_pc', res2)
check('control pc: HOST_FREEZE -> FAIL, the class member itself False', res2['stand'][0]['cls'] == 'HOST_FREEZE' and not cm['ok'] and
      mem(cm, 'class UNMARKED:Gpu') == [False], res2['stand'][0]['cls'])
res2 = read('stand_pc_guest', build({T0 + 1: dict(dt=6200000, diag=diag_block(FIRST + T0 + 1, 6200000, instr=0, threads=[
    thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', Sw=S), thr(2, 'DrawThread', 'guest', R=S)]))}, test_fire_idx=T0 + 1,
    stand_mode='gpusleep'))
cm = R.control_members('f25_pc', res2)
check('control pc: GUEST_RUN:DrawThread (GuestGpu not in the chain) -> the class member False', res2['stand'][0]['cls'] == 'GUEST_RUN:DrawThread'
      and mem(cm, 'class UNMARKED:Gpu') == [False] and not cm['ok'], (res2['stand'][0]['cls'], cm['members']))
res2 = read('stand_pc_short', build({T0 + 1: dict(dt=5999999, diag=diag_block(FIRST + T0 + 1, 5999999, instr=0, threads=THR_PC,
                                                                            waits=[dict(slot=2, kind='gpu_wait', peer=1)]))},
                                    test_fire_idx=T0 + 1, stand_mode='gpusleep'))
check('control pc: 5 999 999 < 6 s -> FAIL', not R.control_members('f25_pc', res2)['ok'])
res2 = read('stand_pc_hexh', build({T0 + 1: dict(dt=6200000, diag=diag_block(FIRST + T0 + 1, 6200000, instr=0, threads=THR_PC, hist_exh_w=1,
                                                                           waits=[dict(slot=2, kind='gpu_wait', peer=1)]))},
                                   test_fire_idx=T0 + 1, stand_mode='gpusleep'))
cm = R.control_members('f25_pc', res2)
check('control pc: hist_exh_w 1 -> FAIL, the member hist_exh_w 0 itself False', not cm['ok'] and mem(cm, 'hist_exh_w 0') == [False],
      cm['members'])
res2 = read('stand_pc_nokey', build({T0 + 1: dict(dt=6200000, diag=None)}, test_fire_idx=T0 + 1, stand_mode='gpusleep'))
cm = R.control_members('f25_pc', res2)
check('control pc: no key window -> FAIL, the member key reduced itself False', not cm['ok'] and mem(cm, 'key reduced') == [False],
      cm['members'])
res2 = dict(diag_lines=0, mode=[], med_dt=1, slow70=0)
check('control z: 0 DiagB32 lines, no mode line -> PASS', R.control_members('f25_z1', res2)['ok'])
check('control z: 1 DiagB32 line -> FAIL', not R.control_members('f25_z2', dict(res2, diag_lines=1))['ok'])

# ---- admission (--dir form)
S18 = R.BIN_INST
MODE = 'DiagB32: mode=1 period_us=5000 print_us=100000 ncpu=32 kstate=1'
PC_YES = 'PipelinePrecache: 1856 recipes -> 1713 graphics + 143 compute pipelines queued, 0 skipped\n'


def adm_dir(name, tag, env_extra, log_text, binary=None, inst_b=S18, inst_a=S18, mcmp='manifest cmp EQUAL files 9', scmp='manifest cmp EQUAL files 9',
            noret=None, level=LV, hlevel=None, hold=330, seal_text='seal\ntheta_load: 0.4562\n', abort='22', load=None):
    d = os.path.join(TMP, 'adm_' + name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'log.txt'), 'w', encoding='ascii', newline='\n') as f:
        f.write(log_text)
    with open(os.path.join(d, 'seal.md'), 'w', encoding='ascii', newline='\n') as f:
        f.write(seal_text)
    env = dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S=abort, KYTY_GUEST_ARGS='-lvl ' + level, KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')
    env.update(env_extra)
    js = dict(binary_sha256=R.BIN_B if binary is None else binary, prereg=dict(sha256=R.sha_file(os.path.join(d, 'seal.md'))), env=env,
              cmdline=['x', '--vulkan-validation', 'false', '--shader-validation', 'false'], guest_args='-lvl ' + level, hold_s=hold,
              attempts=[dict(outcome='ok')])
    with open(os.path.join(d, 'es.json'), 'w', encoding='ascii') as f:
        json.dump(js, f)
    for nm, v in (('installed_before', inst_b), ('installed_after', inst_a), ('manifest_cmp', mcmp), ('snap_cmp', scmp), ('noreturn', noret),
                  ('level', level if hlevel is None else hlevel)):
        p = os.path.join(d, nm + '.txt')
        if v is None:
            if os.path.exists(p):
                os.remove(p)
            continue
        with open(p, 'w', encoding='ascii') as f:
            f.write(v + '\n')
    lp = os.path.join(d, 'load.json')
    if load is not None:
        with open(lp, 'w', encoding='ascii') as f:
            json.dump(load, f)
    elif os.path.exists(lp):
        os.remove(lp)
    return R.read_tag(tag, R.paths(tag, d))


def fails(r):
    return [a[0][:70] for a in r['admission'] if not a[1]]


F1 = R.form_of('f25_s01')
F0 = R.form_of('f25_z1')
FB = R.form_of('f25_pb')
FC = R.form_of('f25_pc')
check('form_of: =1 for c, s, k; =0 for z; the stands for pb / pc; GPU_WALL=1 always',
      F1 == R.form_of('f25_c1') == R.form_of('f25_k10') == dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1') and
      F0 == R.form_of('f25_z2') == dict(KYTY_DIAG_B32='0', KYTY_GPU_WALL='1') and FB == dict(F1, KYTY_TEST_B32='60:present:3000') and
      FC == dict(F1, KYTY_TEST_B32='60:gpusleep:6000'), (F1, F0, FB, FC))
log_on = build({}, pre=[MODE + '\n', PC_YES])
log_off = build({}, pre=[PC_YES])
log_bon = build({}, pre=[MODE + '\n', PC_YES], level=R.BONUS)
r = adm_dir('s01', 'f25_s01', F1, log_on)
check('admission s01 (pot, warm) PASS, status ADMITTED', r['admitted'] and r['status'] == 'ADMITTED' and r['level'] == R.POT, fails(r))
r = adm_dir('s02b', 'f25_s02', F1, log_bon, level=R.BONUS)
check('admission s02 (bonus) PASS', r['admitted'] and r['level'] == R.BONUS, fails(r))
r = adm_dir('s01_lvlh', 'f25_s01', F1, log_on, hlevel=R.BONUS)
check('admission: harness level file differs from the guest args FAIL', not r['admitted'], fails(r))
r = adm_dir('z1', 'f25_z1', F0, log_off)
check('admission z1 (=0) PASS', r['admitted'], fails(r))
r = adm_dir('z1_bonus', 'f25_z1', F0, build({}, pre=[PC_YES], level=R.BONUS), level=R.BONUS)
check('admission z1 on bonus (fixed level pot) FAIL', not r['admitted'], fails(r))
r = adm_dir('z1_diag', 'f25_z1', F0, log_on)
check('admission z1 with a DiagB32 mode line FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_off', 'f25_s01', F1, log_off)
check('admission s01 without the mode line FAIL', not r['admitted'], fails(r))
r = adm_dir('abort8', 'f25_s01', F1, log_on, abort='8')
check('admission: KYTY_GPU_HANG_ABORT_S 8 (not 22) FAIL', not r['admitted'], fails(r))
r = adm_dir('bin_s18', 'f25_s01', F1, log_on, binary=S18)
check('admission: json binary S18 (not binary B) FAIL', not r['admitted'], fails(r))
r = adm_dir('inst_after', 'f25_s01', F1, log_on, inst_a=R.BIN_B)
check('admission: installed after = binary B FAIL', not r['admitted'], fails(r))
r = adm_dir('env_extra', 'f25_s01', dict(F1, KYTY_X='1'), log_on)
check('admission: extra env FAIL', not r['admitted'], fails(r))
r = adm_dir('snap', 'f25_s01', F1, log_on, scmp='manifest cmp DIFFER only-before 1 only-after 1')
check('admission: caches before not the snapshot of the form FAIL', not r['admitted'], fails(r))
r = adm_dir('nosnap', 'f25_s01', F1, log_on, scmp=None)
check('admission: no snap_cmp FAIL', not r['admitted'], fails(r))
r = adm_dir('ret', 'f25_s01', F1, log_on, mcmp='manifest cmp DIFFER only-before 1 only-after 0')
check('admission: caches not returned FAIL', not r['admitted'], fails(r))
r = adm_dir('ret_nr', 'f25_s01', F1, log_on, noret='NO RETURN (prewarm)')
check('admission: a warm tag with a noreturn file FAIL', not r['admitted'], fails(r))
r = adm_dir('c1', 'f25_c1', F1, log_on, mcmp='manifest cmp DIFFER only-before 3 only-after 9', noret='NO RETURN (prewarm, item 596 (g)): snapshot C1 SNAP TAKEN')
check('admission c1 (prewarm, no return) PASS', r['admitted'] and r['kind'] == 'prewarm', fails(r))
r = adm_dir('c1_ret', 'f25_c1', F1, log_on)
check('admission c1 without the noreturn line FAIL', not r['admitted'], fails(r))
r = adm_dir('c2_pot', 'f25_c2', F1, log_on, noret='NO RETURN x')
check('admission c2 on pot (fixed bonus) FAIL', not r['admitted'], fails(r))
r = adm_dir('pb', 'f25_pb', FB, build({}, pre=[MODE + '\n', PC_YES], test_fire_idx=T0))
check('admission pb with the stand lines PASS', r['admitted'], fails(r))
r = adm_dir('pb_nostand', 'f25_pb', FB, log_on)
check('admission pb without stand lines FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_stand', 'f25_s01', F1, build({}, pre=[MODE + '\n', PC_YES], test_fire_idx=T0))
check('admission s01 with stand lines FAIL', not r['admitted'], fails(r))
r = adm_dir('load', 'f25_s01', F1, log_on, load=dict(status='done'))
check('admission with a loader json FAIL', not r['admitted'], fails(r))
r = adm_dir('hold300', 'f25_s01', F1, log_on, hold=300)
check('admission: hold option 300 FAIL', not r['admitted'], fails(r))
r = adm_dir('short', 'f25_s01', F1, build({}, pre=[MODE + '\n', PC_YES], nframes=2000))
check('admission: scene < 300 s without abort FAIL (hold member)', not r['admitted'], fails(r))
r = adm_dir('abort_ok', 'f25_s01', F1, build({}, pre=[MODE + '\n', PC_YES], stop_idx=T0, quit=False,
                                             extra_after={T0: ['GpuHangAbort: role=4 after=22s', '--- Error ---']}))
check('admission: GpuHangAbort after >= 10 s with the EXIT error line after it PASS (not interference), K 1 abort', r['admitted'] and
      r['log']['hold_class'] == 'NO_SAMPLES:abort', fails(r))
r = adm_dir('abort_early', 'f25_s01', F1, build({}, pre=[MODE + '\n', PC_YES], stop_idx=200, quit=False,
                                                extra_after={200: ['GpuHangAbort: role=4 after=22s']}))
check('admission: GpuHangAbort before 10 s of the scene FAIL (interference)', not r['admitted'] and r['status'] == 'INTERFERENCE', fails(r))
r = adm_dir('err_before', 'f25_s01', F1, build({}, pre=[MODE + '\n', PC_YES, '--- Error ---\n'], stop_idx=T0, quit=False,
                                               extra_after={T0: ['GpuHangAbort: x']}))
check('admission: an error line BEFORE GpuHangAbort FAIL (other death marker)', not r['admitted'], fails(r))
r = adm_dir('death', 'f25_s01', F1, build({}, pre=[MODE + '\n', PC_YES], extra_after={T0: ['Unhandled exception: x']}))
check('admission: an Unhandled exception line FAIL', not r['admitted'], fails(r))
r = adm_dir('notwarm', 'f25_s01', F1, build({}, pre=[MODE + '\n', PC_YES], b5_idx=(T0,)))
check('a dump line at >= 10 s in a series tag -> status NOT_WARM (not INTERFERENCE), read in the layer', r['status'] == 'NOT_WARM' and
      not r['admitted'] and all(b for _, b in r['admission']), (r['status'], fails(r)))
r = adm_dir('notwarm_c1', 'f25_c1', F1, build({}, pre=[MODE + '\n', PC_YES], b5_idx=(T0,)), noret='NO RETURN x', mcmp='manifest cmp DIFFER')
check('a prewarm tag is not checked for warmth (ADMITTED)', r['status'] == 'ADMITTED', (r['status'], fails(r)))
r = adm_dir('notwarm_k', 'f25_k01', F1, build({}, pre=[MODE + '\n', PC_YES], b5_idx=(T0,)))
check('a cold tag is not checked for warmth (ADMITTED)', r['status'] == 'ADMITTED', (r['status'], fails(r)))
r = adm_dir('sig', 'f25_s01', F1, build({}, pre=[MODE + '\n', PC_YES], seed=[SEED_LINES[0], SEED_LINES[1].replace('9177b426', '9177b427')]))
check('admission: translation signature not 9177b426 FAIL', not r['admitted'], fails(r))
r = adm_dir('nothe', 'f25_s01', F1, log_on, seal_text='seal\n')
check('admission: no theta_load line in the seal FAIL, the log is not read', not r['admitted'] and r['log'] is None)
rd = build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, cum={'rep_drop': 1}))}, pre=[MODE + '\n', PC_YES])
r = adm_dir('repdrop', 'f25_s01', F1, rd)
check('admission: rep_drop != 0 FAIL', not r['admitted'] and r['log']['rep_drop'] == 1, fails(r))
r = adm_dir('recov', 'f25_s01', F1, build({}, pre=[MODE + '\n', PC_YES], recovering=True))
check('admission: Recovering Vulkan swapchain FAIL', not r['admitted'], fails(r))
r = adm_dir('repeat', 'f25_s07_r1', F1, log_on)
check('a repeat name f25_s07_r1 reads with the form of f25_s07', r['admitted'] and r['form'] == 'f25_s07', fails(r))
for good in ('f25_c1', 'f25_c2', 'f25_z1', 'f25_z2', 'f25_pb', 'f25_pc', 'f25_s01', 'f25_s09', 'f25_s10', 'f25_s39', 'f25_s40', 'f25_k01',
             'f25_k10', 'f25_s40_r6', 'f25_c2_r1', 'f25_k03_r4'):
    check('tag name %s accepted' % good, R.TAG_RX.match(good) is not None)
for bad in ('f25_s00', 'f25_s41', 'f25_s1', 'f25_c3', 'f25_z0', 'f25_pa', 'f25_k00', 'f25_k11', 'f25_s01_r7', 'f25_s01_r0', 'b32_s01', '',
            'f25_s01_r'):
    check('tag name %r refused' % bad, R.TAG_RX.match(bad) is None)
_p = R.paths('f25_s07')
check('paths f25_s07: F25f files and seal', _p['log'].replace('\\', '/') == 'C:/kyty/f287/f25f/log_f25_s07.txt' and _p['seal'] == R.SEAL_PATH
      and _p['cal'].replace('\\', '/').endswith('f25f/runs/f25_s07/cal.txt'), _p)
check('constants: binary B, installed S18, envelope, abort 22', R.BIN_B == 'e342b839d74d5689bc4f66ee0ed04a37e9a640e60a199a2882c8e83ecf19cfa4'
      and R.BIN_INST == 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a' and R.ENV_US == 4095 * 5000 and R.HANG_ABORT == '22')

# ---- the stop rule of item 596 (e) with item 552 (g)
for n_, k_, ki_, want in ((4, 3, 3, 'CONTINUE'), (5, 3, 3, 'STOP_READ'), (5, 0, 0, 'CONTINUE'), (13, 0, 0, 'CONTINUE'), (14, 0, 0, 'STOP_U2'),
                          (14, 0, 1, 'STOP_552G'), (5, 1, 1, 'CONTINUE'), (19, 2, 2, 'CONTINUE'), (20, 2, 2, 'STOP_U2PRIME'),
                          (20, 1, 3, 'STOP_U2PRIME'), (12, 3, 4, 'STOP_READ'), (6, 2, 2, 'CONTINUE'), (4, 0, 0, 'CONTINUE')):
    check('stop_rule(N %d, K %d, K_I %d) = %s' % (n_, k_, ki_, want), R.stop_rule(n_, k_, ki_)[0] == want, R.stop_rule(n_, k_, ki_))

# ---- series summary: controls, levels, NOT WARM same hash, cold layer, budget (synthetic read.json)
SR = os.path.join(TMP, 'series_runs')


def put(tag, status='ADMITTED', level=R.POT, K=0, K_I=0, cls=None, u5=False, hashes=(), ctl=None, kind=None):
    d = os.path.join(SR, tag)
    os.makedirs(d, exist_ok=True)
    js = dict(tag=tag, status=status, level=level, admitted=status == 'ADMITTED', control=ctl, kind=kind, binary_sha256=R.BIN_B,
              ref=dict(signature=R.SIG_B, glitches=0),
              log=dict(K=K, K_I=K_I, hold_class=cls, hold_family=None if cls is None else cls.split(':')[0], hold_form=None, hold_burst=None,
                       u5_tag=u5, u5_bad_n=1 if u5 else 0, warm_dump_hashes=list(hashes), P_I_K2=K_I, in_count=K, b5=[], b5_armed=0, frames=[]))
    with open(os.path.join(d, 'read.json'), 'w', encoding='ascii') as f:
        json.dump(js, f)
    with open(os.path.join(d, 'read.txt'), 'w', encoding='ascii') as f:
        f.write('x\n')


if os.path.isdir(SR):
    shutil.rmtree(SR)
for c in ('f25_z1', 'f25_z2', 'f25_pb', 'f25_pc'):
    put(c, ctl=dict(ok=True, members=[], ref=None))
for k in range(1, 6):
    put('f25_s%02d' % (2 * k - 1), level=R.POT, K=1 if k <= 3 else 0, K_I=1 if k <= 3 else 0, cls='EMU_WAIT:flip_req' if k <= 3 else None)
    put('f25_s%02d' % (2 * k), level=R.BONUS)
out = R.series(SR)
txt = '\n'.join(out)
check('series: controls PASS', 'CONTROLS PASS' in txt, [l for l in out if l.startswith('CONTROL')])
check('series: pot N 5 K 3 -> STOP_READ', 'LEVEL pot_treasure_cave N 5 K 3 K_I 3; N_nw 0 K_nw 0; STOP RULE STOP_READ' in txt,
      [l for l in out if l.startswith('LEVEL')])
check('series: bonus N 5 K 0 -> CONTINUE', 'LEVEL bonus_path_maker_mix N 5 K 0 K_I 0; N_nw 0 K_nw 0; STOP RULE CONTINUE' in txt,
      [l for l in out if l.startswith('LEVEL')])
check('series: classes of pot printed (EMU_WAIT 3)', "CLASSES [('EMU_WAIT', 3)]" in txt, [l for l in out if 'CLASSES' in l])
put('f25_s11', status='NOT_WARM', level=R.BONUS, hashes=('aa', 'bb'))
put('f25_s12', status='NOT_WARM', level=R.BONUS, hashes=('cc', 'aa'), K=1, K_I=1, cls='UNMARKED:Gpu')
out = R.series(SR)
txt = '\n'.join(out)
check('series: two NOT WARM bonus tags with one program hash -> STOP_LEVEL_Q, layer N_nw 2 K_nw 1, not in N / K',
      'LEVEL bonus_path_maker_mix N 5 K 0 K_I 0; N_nw 2 K_nw 1; STOP RULE STOP_LEVEL_Q' in txt and "['aa']" in txt,
      [l for l in out if l.startswith('LEVEL')])
check('series: NOT WARM counts in the interference budget (2 of 6)', 'interference + NOT WARM 2 of 6' in txt, [l for l in out if 'BUDGET' in l])
put('f25_s13', level=R.POT, u5=True)
out = R.series(SR)
check('series: U5(4) with 1 tag -> no', 'U5(4) series tags with a bad window 1' in chr(10).join(out) and 'NEXT STOP (U5(4))' not in chr(10).join(out),
      [l for l in out if l.startswith('U5')])
put('f25_s14', level=R.BONUS, u5=True)
out = R.series(SR)
txt = '\n'.join(out)
check('series: U5(4) with 2 tags -> FIRES, NEXT STOP (U5(4))', 'U5(4) series tags with a bad window 2' in txt and 'FIRES' in txt and
      'NEXT STOP (U5(4))' in txt, [l for l in out if l.startswith('U5') or l.startswith('NEXT')])
for k in range(1, 6):
    put('f25_k%02d' % k, level=R.POT)
put('f25_k06', level=R.BONUS, K=1, K_I=1, cls='EMU_WAIT:flip_req')
out = R.series(SR)
txt = '\n'.join(out)
check('cold layer: pot 0 of 5 -> STOP_NO_REPRO; bonus first tag with K -> STOP_REPRO',
      'STOP_NO_REPRO (0 of 5)' in txt and 'STOP_REPRO (first f25_k06)' in txt, [l for l in out if l.startswith('COLD')])
put('f25_s15', status='INTERFERENCE')
put('f25_s16', status='INTERFERENCE')
put('f25_s17', status='INTERFERENCE')
put('f25_s18', status='INTERFERENCE')
out = R.series(SR)
check('budget: interference + NOT WARM 6 of 6 -> no stop', 'interference + NOT WARM 6 of 6' in chr(10).join(out) and
      'STOP_INTERFERENCE' not in chr(10).join(out), [l for l in out if 'BUDGET' in l])
put('f25_s19', status='INTERFERENCE')
out = R.series(SR)
txt = '\n'.join(out)
check('budget: interference + NOT WARM 7 > 6 -> STOP_INTERFERENCE', 'STOP_INTERFERENCE' in txt and 'NEXT STOP (interference)' in txt,
      [l for l in out if 'BUDGET' in l or 'NEXT' in l])
put('f25_s15_r1', level=R.POT, K=1, K_I=1, cls='HOST_FREEZE')
out = R.series(SR)
check('series: a repeat f25_s15_r1 stands for f25_s15', any('f25_s15 (f25_s15_r1)' in l for l in out), [l for l in out if 's15' in l])
shutil.rmtree(SR)
put('f25_z1', ctl=dict(ok=True, members=[], ref=None))
put('f25_z2', ctl=dict(ok=False, members=[], ref=None))
out = R.series(SR)
check('controls: one FAIL with two PENDING -> CONTROLS PENDING; all four read with a FAIL -> FAIL', 'CONTROLS PENDING' in '\n'.join(out))
put('f25_pb', ctl=dict(ok=True, members=[], ref=None))
put('f25_pc', ctl=dict(ok=True, members=[], ref=None))
out = R.series(SR)
check('controls: z2 FAIL -> CONTROLS FAIL and NEXT STOP (controls)', 'CONTROLS FAIL' in '\n'.join(out) and 'NEXT STOP (controls)' in '\n'.join(out),
      out)
shutil.rmtree(SR)

# ---- theta from the seal; the WaitName list of binary B
_td = os.path.join(TMP, 'theta')
os.makedirs(_td, exist_ok=True)
for t_, want in (('x\ntheta_load: 0.4562\ny\n', 0.4562), ('no line\n', None), ('theta_load: 0.4562\ntheta_load: 0.5\n', None)):
    open(os.path.join(_td, 's.md'), 'wb').write(t_.encode('ascii'))
    check('read_theta %r -> %s' % (t_[:30], want), R.read_theta(os.path.join(_td, 's.md')) == want)
_body = os.path.join(HERE, 'f25f_seal_body.md')
check('the seal body carries theta_load 0.4562', R.read_theta(_body) == 0.4562, R.read_theta(_body))

# ---- strict cp1250 output of the reader (no PYTHONIOENCODING)
_fd = os.path.join(TMP, 'adm_s01')
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
env['PYTHONUTF8'] = '0'
p = subprocess.run([sys.executable, os.path.join(HERE, 'f25_read.py'), '--dir', _fd, '--tag', 'f25_s01'], capture_output=True, env=env)
out_b = p.stdout
check('reader output in strict cp1250 without PYTHONIOENCODING: rc 0 and ASCII', p.returncode == 0 and all(b < 128 for b in out_b) and
      b'READING' in out_b, (p.returncode, p.stderr[-300:]))

shutil.rmtree(TMP)
print('checks %d' % nchk)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
