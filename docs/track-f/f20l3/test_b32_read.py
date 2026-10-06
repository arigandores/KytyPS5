"""F20l3 (HPP-655): fixtures of b32_read.py - item 591: the PK-A domain of the cold form (v)(2), the member and 'not called' (v)(3)-(4),
U5(3) not computable (v)(6), the U5(1) rule of item 555 (b)(2) with the base of (d)(2) (exact Mann-Whitney against a brute force), the
series stop rule of item 550 (e)(2)-(3), cold / warm admission and the installed S18 (g)(3); and as in F20l2: the rule of item 574 (d) and the kinds / classes of item 581 (v)(5) (one fixture per kind,
emu_join included), the record peer of item 581 (v)(2), theta_load from the seal, ring_hold_w, the gpusleep stand member of item 574 (v)(2);
and as in F20l: every class and edge of item 550 (g), RC6, RC7, RC13, INSTR_MADE, K_I, the members of
item 552 (g), 553 (v), 554 (g), the _w invariants (event in window k, clean window k+1), the report of n between the FrameTrace lines
of n+1 and n+2 (item 551 (b)(5)), the stand and load windows, U5, admission, strict cp1250 output.  ASCII only; ends with ALL OK.
usage: python test_b32_read.py"""
import hashlib
import json
import os
import shutil
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b32_read as R  # noqa: E402

TMP = os.path.join(HERE, 'fx_tmp')
print('suite test_b32_read.py sha256 %s target b32_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
    hashlib.sha256(open(os.path.join(HERE, 'b32_read.py'), 'rb').read()).hexdigest()))

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


def thr(slot, name, role, R=0, r=0, Sr=0, Sw=0, S=0, W=None, H=None, peer=-1, X=0):
    return dict(slot=slot, name=name, role=role, R=R, r=r, Sr=Sr, Sw=Sw, S=S, W=W or {}, H=H or {}, peer=peer, X=X)


def klist(d):
    return ','.join('%s:%d' % (k, v) for k, v in d.items()) if d else '-'


def diag_block(n, dt, samples=40, instr=1000, sgap=5000, i2=1, kstate=1, kq_n=1, kq_us=900, m5r=0, other=0, ncpu=32, vo=0, gpu=1,
               flip=2, threads=None, waits=None, xw=None, x=True, hdr=True, cum=None, ring_hold=0, ring_hold_c=None):
    out = []
    if hdr:
        out.append('DiagB32: n=%d dt_us=%d instr_us=%d samples=%d sgap_max_us=%d gap3p=0 i2=%d kstate=%d kq=1 kq_n=%d kq_us=%d m5r_us=%d '
                   'proc_us=100000 sys_busy_us=%d sys_idle_us=0 other_us=%d ncpu=%d snap_ok=1 snap_lag_us=10 flip_slot=%d flip_tid=7 '
                   'flip_src=cpu lat_us=12000 vo_slot=%d gpu_slot=%d t_lines=3 w_lines=0 c_lines=0' % (
                       n, dt, instr, samples, sgap, i2, kstate, kq_n, kq_us, m5r, 100000 + other, other, ncpu, flip, vo, gpu))
    if threads is None:
        threads = [thr(0, 'Present', 'Present', S=samples), thr(1, 'Gpu', 'Gpu', r=samples), thr(2, 'DrawThread', 'guest', S=samples)]
    for t in threads:
        out.append('DiagB32-t: n=%d slot=%d tid=0 os_tid=1 name=%s role=%s must=1 X=%d R=%d r=%d Sr=%d Sw=%d S=%d W=%s H=%s SwR=- cpu_us=0 '
                   'top=- last=- obj=0x0 since_us=0 peer=%d' % (n, t['slot'], t['name'], t['role'], t['X'], t['R'], t['r'], t['Sr'],
                                                               t['Sw'], t['S'], klist(t['W']), klist(t['H']), t['peer']))
    for w in waits or []:
        out.append('DiagB32-w: n=%d slot=%d tid=0 kind=%s obj=0x1 start_us=0 wait_us=%d overlap_us=%d waker=%d waker_tid=0 req_us=%d to=%d '
                   'open=0 peer=%d peer_tid=0' % (n, w['slot'], w['kind'], w.get('wait', 50000), w.get('overlap', 50000), w.get('waker', -1),
                                                w.get('req', 0), w.get('to', 0), w.get('peer', -1)))
    if x:
        z = dict((k, 0) for k in R.ZERO_W)
        z.update(xw or {})
        c = dict((k[:-2], 0) for k in R.ZERO_W)
        c.update(cum or {})
        out.append('DiagB32-x: n=%d slots=10 slot_full=%d slot_full_w=%d torn=%d torn_w=%d ring_drop=%d ring_drop_w=%d sgap_bad=%d '
                   'sgap_bad_w=%d lines_cut=%d lines_cut_w=%d req_miss=%d req_miss_w=%d sub_miss=%d sub_miss_w=%d short_stalls=0 '
                   'others_cut=0 w_cut=0 rep_drop=%d kq_fail=0 print_us=10 gap3p=0 ring_hold=%d ring_hold_w=%d' % (
                       n, c['slot_full'], z['slot_full_w'], c['torn'], z['torn_w'], c['ring_drop'], z['ring_drop_w'], c['sgap_bad'],
                       z['sgap_bad_w'], c['lines_cut'], z['lines_cut_w'], c['req_miss'], z['req_miss_w'], c['sub_miss'], z['sub_miss_w'],
                       (cum or {}).get('rep_drop', 0), ring_hold if ring_hold_c is None else ring_hold_c, ring_hold))
    return out


SEED_LINES = ['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\n',
              'ShaderSeed: compatibility=KytySeed1:PPSA21564:01.007.000:KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz\n']


def build(targets=None, nframes=9200, extra_after=None, b5_idx=(), pre=None, recovering=False, test_fire_idx=None, dump_line_after=None,
          dt_by_idx=None, seed=None, stand_mode='present', pre_scene=None):
    """targets: idx -> dict(dt, lat, gb, diag (list of lines or None)); the diag block of frame n goes after the FrameTrace of n+1."""
    targets = targets or {}
    dt_by_idx = dict(dt_by_idx or {})
    lines = ['loading\n'] + (SEED_LINES if seed is None else seed) + ['GuestOut: Level has started: \n'] + (pre or []) + \
        ['GuestOut: Level has started: underwater_aerial_garden\n'] + [x + '\n' for x in (pre_scene or [])]
    lines.append('FrameTrace: n=%d dt_us=40000 lat_us=12000 gpu_proc=0 draws=4000 gpu_busy_us=15000 cpu_gpu_us=30000\n' % FIRST)
    pending = {}
    for idx in range(1, nframes + 1):
        n = FIRST + idx
        if idx in b5_idx:
            lines.append('%_1 = OpTypeVoid\n')
        if test_fire_idx is not None and idx == test_fire_idx:
            lines.append('TestB32: armed delay_s=60 mode=%s ms=200\n' % stand_mode)
            lines.append('TestB32: fire mode=%s ms=200\n' % stand_mode)
            lines.append('TestB32: done mode=%s slept_us=200000\n' % stand_mode)
        t = targets.get(idx)
        dt = t['dt'] if t else dt_by_idx.get(idx, BASE_DT)
        lat = t.get('lat', BASE_LAT) if t else BASE_LAT
        gb = t.get('gb', BASE_GB) if t else BASE_GB
        lines.append('FrameTrace: n=%d dt_us=%d lat_us=%d gpu_proc=0 draws=4000 gpu_busy_us=%d cpu_gpu_us=30000\n' % (n, dt, lat, gb))
        if t and t.get('diag') is not None:
            pending[idx + 1] = t['diag']
        if idx in pending:
            for l in pending.pop(idx):
                lines.append(l + '\n')
        if extra_after and idx in extra_after:
            for l in extra_after[idx]:
                lines.append(l + '\n')
    if recovering:
        lines.append('Recovering Vulkan swapchain\n')
    lines.append('Event: quit\n')
    return ''.join(lines)


def write_log(name, text):
    d = os.path.join(TMP, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'log.txt'), 'w', encoding='ascii', newline='\n') as f:
        f.write(text)
    return d


def read(name, text, theta=None, load=None):
    d = write_log(name, text)
    return R.read_log(os.path.join(d, 'log.txt'), theta, load, d)


def frame(res, idx):
    n = FIRST + idx
    for x in res['frames']:
        if x['n'] == n:
            return x
    return None


def one(name, dt, diag_kw, theta=None, lat=BASE_LAT, gb=BASE_GB, diag=True):
    n = FIRST + T0
    blk = diag_block(n, dt, **diag_kw) if diag else None
    res = read(name, build({T0: dict(dt=dt, lat=lat, gb=gb, diag=blk)}), theta)
    return frame(res, T0), res


S = 40
E200 = 200000 - BASE_DT          # E of a 200 ms frame

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

# ---- (ii) NO_SAMPLES members
f, _ = one('nos_nodiag', 200000, {}, diag=False)
check('NO_SAMPLES: no DiagB32 line', f['cls'] == 'NO_SAMPLES' and not f['diag'], (f['cls'], f['note']))
f, _ = one('nos_i2', 200000, dict(i2=0))
check('NO_SAMPLES: i2 = 0', f['cls'] == 'NO_SAMPLES', f['cls'])
f, _ = one('nos_s0', 200000, dict(samples=0, sgap=1000))
check('NO_SAMPLES: samples = 0', f['cls'] == 'NO_SAMPLES', f['cls'])
f, _ = one('nos_nox', 200000, dict(x=False))
check('NO_SAMPLES: no -x line', f['cls'] == 'NO_SAMPLES', f['cls'])
for k in R.ZERO_W:
    f, _ = one('nos_' + k, 200000, dict(xw={k: 1}, cum={k[:-2]: 1}))
    check('NO_SAMPLES: %s = 1' % k, f['cls'] == 'NO_SAMPLES' and k in f['note'], (f['cls'], f['note']))
f, _ = one('nos_cum_only', 200000, dict(cum={'torn': 5}))
check('cumulative torn without torn_w is not NO_SAMPLES', f['cls'] != 'NO_SAMPLES', f['cls'])
# event in window k, clean window k+1 (item 552 (v)(3))
n1, n2 = FIRST + T0, FIRST + T0 + 40
res = read('w_k_k1', build({T0: dict(dt=200000, diag=diag_block(n1, 200000, xw={'torn_w': 1}, cum={'torn': 1})),
                            T0 + 40: dict(dt=200000, diag=diag_block(n2, 200000, cum={'torn': 1}))}))
check('window k with torn_w = 1 -> NO_SAMPLES', frame(res, T0)['cls'] == 'NO_SAMPLES', frame(res, T0)['cls'])
check('window k+1 clean (torn 1 cumulative, torn_w 0) -> classified', frame(res, T0 + 40)['cls'] != 'NO_SAMPLES', frame(res, T0 + 40)['cls'])
check('U5(4) sum of _w = 1 (torn_w)', res['zero_w_sum']['torn_w'] == 1 and sum(res['zero_w_sum'].values()) == 1, res['zero_w_sum'])
check('freeze is checked before NO_SAMPLES', one('freeze_first', 200000, dict(sgap=E200, i2=0))[0]['cls'] == 'HOST_FREEZE')

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
# the kind names against the enum of the reviewed code (WaitName of 4371ff4b, = f2307b02 byte for byte)
_src = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', '4371ff4b:src/common/diagB32.cpp'],
                      capture_output=True).stdout.decode('utf-8', 'replace')
_i = _src.find('const char* WaitName(uint8_t kind) {')
_blk = _src[_i:_src.find('static_assert', _i)]
import re as _re  # noqa: E402
_names = _re.findall(r'"([a-z_]+|-)"', _blk)
check('WAITS = WaitName of 4371ff4b in order (45 kinds)', _names[1:] == list(R.WAITS) and len(R.WAITS) == 45, (_names[1:4], len(_names)))
_h = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', '4371ff4b:src/common/diagB32.h'],
                    capture_output=True).stdout.decode('utf-8', 'replace')
_j = _h.find('constexpr bool IsEmuWait(uint8_t kind) {')
_emu = _h[_j:_h.find('}', _j)]
check('IsEmuWait of 4371ff4b: EmuMutex .. Av plus Vblank, Audio, Aio, Net, EmuJoin', all('Wait::%s)' % k in _emu for k in
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

# ---- the count: INSTR_MADE, edges of item 550 (g)(1), K_I, K
f, res = one('instr_edge', 200000, dict(instr=100001))
check('INSTR_MADE at dt - instr = 99 999', f['instr_made'] and not f['in_count'], f)
check('K_I 1, K 0 when the only frame is INSTR_MADE', res['K_I'] == 1 and res['K'] == 0 and res['instr_share'] == 1.0,
      (res['K_I'], res['K'], res['instr_share']))
f, res = one('instr_ok', 200000, dict(instr=100000))
check('in count at dt - instr = 100 000', f['in_count'] and not f['instr_made'], f)
check('K 1 on a hold', res['K'] == 1 and res['hold'], (res['K'], res['hold']))
res = read('dt_edge', build({T0: dict(dt=99999, diag=None), T0 + 40: dict(dt=100000, diag=diag_block(FIRST + T0 + 40, 100000, instr=0))}))
check('dt 99 999 is not a hold frame', frame(res, T0) is None)
check('dt 100 000 is a hold frame in count', frame(res, T0 + 40) is not None and frame(res, T0 + 40)['in_count'])
# start at exactly 10 s: idx k starts at 33 333 x (k - 1) us; build a scene where the target starts at 10 000 000 / 9 999 999
pre = {}
k_on = 301            # 300 frames x 33 333 = 9 999 900 -> pad the first frame
dts = {1: BASE_DT + 100}  # t_before(idx 301) = 33 433 + 299 x 33 333 = 10 000 000
res = read('t10', build({k_on: dict(dt=150000, diag=diag_block(FIRST + k_on, 150000, instr=0))}, dt_by_idx=dts))
check('a frame that starts at exactly 10 s is a hold frame', frame(res, k_on) is not None and frame(res, k_on)['t_s'] == 10.0,
      frame(res, k_on) and frame(res, k_on)['t_s'])
res = read('t10m', build({k_on: dict(dt=150000, diag=diag_block(FIRST + k_on, 150000, instr=0))}, dt_by_idx={1: BASE_DT + 99}))
check('a frame that starts at 9.999 999 s is not', frame(res, k_on) is None)
res = read('noholdscene', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, instr=0))}, nframes=2000))
check('no hold (scene < 300 s): K and K_I 0, frame still classified', res['K'] == 0 and res['K_I'] == 0 and frame(res, T0)['in_count'],
      (res['K'], res['K_I']))
res = read('empty', build({}))
check('empty P_I: shares NOT EVALUABLE', res['instr_share'] == 'NOT EVALUABLE' and res['kq0_share'] == 'NOT EVALUABLE',
      (res['instr_share'], res['kq0_share']))

# ---- B5 frame: not in P_I, PK-A
res = read('b5', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, threads=[
    thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', R=S), thr(2, 'DrawThread', 'guest', W={'eq': S})],
    waits=[dict(slot=2, kind='eq', waker=1)]))}, b5_idx=(T0,)))
f = frame(res, T0)
check('B5 frame not in P_I', f['attr'] == 'B5' and not f['p_i'] and res['P_I'] == 0, (f['attr'], res['P_I']))
check('PK-A: B5 frame EMU_RUN:Gpu armed', res['pk_a_armed'] == 1 and res['pk_a'][0]['cls'] == 'EMU_RUN:Gpu', res['pk_a'])
res = read('b5_call', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, threads=[
    thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', H={'semwait': S}), thr(2, 'DrawThread', 'guest', W={'eq': S})],
    waits=[dict(slot=2, kind='eq', waker=1)]))}, b5_idx=(T0,)))
check('PK-A: EMU_CALL on GuestGpu armed', res['pk_a_armed'] == 1, res['pk_a'])
res = read('b5_no', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000))}, b5_idx=(T0,)))
check('PK-A: UNMARKED on a guest thread not armed', res['pk_a_armed'] == 0, res['pk_a'])
res = read('b5_present', build({T0: dict(dt=200000, lat=LAT_OUT, diag=diag_block(FIRST + T0, 200000, threads=thr_out_present))},
                               b5_idx=(T0,)))
check('PK-A: EMU_CALL on the output thread not armed', res['pk_a_armed'] == 0 and res['pk_a'][0]['cls'].startswith('EMU_CALL:present'),
      res['pk_a'])
res = read('b5_record', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, threads=[
    thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', W={'eq': S}), thr(3, 'Record', 'Record', R=S)],
    waits=[dict(slot=2, kind='eq', waker=3)]))}, b5_idx=(T0,)))
check('PK-A: EMU_RUN:Record not armed', res['pk_a_armed'] == 0 and res['pk_a'][0]['cls'] == 'EMU_RUN:Record', res['pk_a'])

# ---- item 552 (g), 553 (v), 554 (g) members
GUEST_R = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', R=S)]
res = read('members', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, kq_n=0, m5r=12000, threads=GUEST_R)),
                            T0 + 1: dict(dt=150000, diag=diag_block(FIRST + T0 + 1, 150000, kq_n=2, instr=0)),
                            T0 + 40: dict(dt=150000, diag=diag_block(FIRST + T0 + 40, 150000, instr=60000, kq_n=0)),
                            T0 + 41: dict(dt=150000, diag=diag_block(FIRST + T0 + 41, 150000, instr=60000)),
                            T0 + 80: dict(dt=100000, diag=diag_block(FIRST + T0 + 80, 100000, instr=0)),
                            T0 + 81: dict(dt=120000, diag=diag_block(FIRST + T0 + 81, 120000, instr=0))}))
check('kq_n = 0 frames 2 of 6 in P_I (INSTR_MADE included)', res['kq0'] == 2 and res['kq0_share'] == 0.3333, (res['kq0'], res['kq0_share']))
check('m5r_us > 0 frames 1', res['m5r'] == 1, res['m5r'])
check('INSTR_MADE 2 of 6', res['instr_made'] == 2 and res['instr_share'] == 0.3333, (res['instr_made'], res['instr_share']))
check('in count with the previous frame >= 100 ms: 2 (prev exactly 100 ms counts; INSTR_MADE frame not)', res['prev_slow_in_count'] == 2,
      res['prev_slow_in_count'])
check('hold class = GUEST_RUN of the longest frame (others UNMARKED)', res['hold_class'] == 'GUEST_RUN:DrawThread', res['hold_class'])
check('K_I = K = 1', res['K_I'] == 1 and res['K'] == 1)
check('hold class = class of the longest frame in count', res['hold_class'] == frame(res, T0)['cls'], res['hold_class'])
res = read('prev99', build({T0: dict(dt=99999, diag=None), T0 + 1: dict(dt=150000, diag=diag_block(FIRST + T0 + 1, 150000, instr=0))}))
check('previous frame 99 999 does not count', res['prev_slow_in_count'] == 0, res['prev_slow_in_count'])
res = read('recov', build({}, recovering=True))
check('Recovering Vulkan swapchain counted', res['recovering'] == 1, res['recovering'])

# ---- item 551 (b)(5): the report of n between the FrameTrace lines of n+1 and n+2 is keyed by n=
res = read('key_n', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, instr=0))}))
f = frame(res, T0)
check('report keyed by n= (printed after n+1)', f['diag'] and f['instr_us'] == 0, f)
check('frame n+1 has no report', not any(x['n'] == FIRST + T0 + 1 for x in res['frames']))

# ---- RC13: attribution with and without DiagB32 lines; negative control
res = read('rc13', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000))}))
check('RC13: equal on a DiagB32 log', res['rc13_equal'] and res['rc13_stripped'] > 0, (res['rc13_equal'], res['rc13_stripped']))
bad = diag_block(FIRST + T0, 200000)
bad[1] = bad[1].replace('top=-', 'top=Vulkan pipeline cache: saved')
res = read('rc13_neg', build({T0: dict(dt=200000, diag=bad)}))
check('RC13 negative control: a DiagB32 line the F20c reader would count -> DIFFERENT', not res['rc13_equal'], res['rc13_equal'])
res = read('rc13_pre', build({T0: dict(dt=200000, diag=None)}, extra_after={T0 + 1: ['  DiagB32: n=1 dt_us=1']}))
check('a DiagB32 text not in the first column is counted (bad prefix)', res['diag_bad_prefix'] == 1, res['diag_bad_prefix'])

# ---- ring_hold_w (Z1): reference, not a member of NO_SAMPLES
res = read('ring', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, ring_hold=3, ring_hold_c=7, threads=GUEST_R)),
                          T0 + 40: dict(dt=200000, diag=diag_block(FIRST + T0 + 40, 200000, threads=GUEST_R))}))
check('ring_hold_w 3 is not NO_SAMPLES', frame(res, T0)['cls'] == 'GUEST_RUN:DrawThread' and frame(res, T0)['ring_hold_w'] == 3,
      (frame(res, T0)['cls'], frame(res, T0).get('ring_hold_w')))
check('ring_hold_w sum 3 (cumulative ring_hold 7 not summed), frames 1, -x lines with the field 2', res['ring_hold_w_sum'] == 3 and res['ring_hold_w_frames'] == 1 and
      res['ring_hold_w_field'] == 2, (res['ring_hold_w_sum'], res['ring_hold_w_frames'], res['ring_hold_w_field']))
# ---- theta_load from the seal
_td = os.path.join(TMP, 'theta')
os.makedirs(_td, exist_ok=True)
for txt, want in (('x\ntheta_load: 0.4562\ny\n', 0.4562), ('theta_load: 0.4562\r\n', 0.4562), ('no line\n', None),
                  ('theta_load: 0.4562\ntheta_load: 0.5\n', None), ('theta_load: 0,4562\n', None), (' theta_load: 0.4562\n', None)):
    open(os.path.join(_td, 's.md'), 'wb').write(txt.encode('ascii'))
    check('read_theta %r -> %s' % (txt[:30], want), R.read_theta(os.path.join(_td, 's.md')) == want, R.read_theta(os.path.join(_td, 's.md')))
check('read_theta of a missing file -> None', R.read_theta(os.path.join(_td, 'none.md')) is None)
_body = os.path.join(HERE, 'f20l3_seal_body.md')
check('the seal body carries theta_load 0.4562 (item 574 (b)(6))', R.read_theta(_body) == 0.4562, R.read_theta(_body))
# ---- the gpusleep stand member of item 574 (v)(2): GuestGpu step with Sw or S >= 50 %
THR_PC = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', Sw=S), thr(2, 'DrawThread', 'guest', W={'gpu_wait': S})]
res = read('stand_pc', build({T0 + 1: dict(dt=230000, diag=diag_block(FIRST + T0 + 1, 230000, instr=0, threads=THR_PC,
                                                                     waits=[dict(slot=2, kind='gpu_wait', waker=-1, peer=1)]))},
                             test_fire_idx=T0 + 1, stand_mode='gpusleep'))
st = res['stand'][0]
check('stand pc: flip holder W:gpu_wait -> peer GuestGpu Sw -> UNMARKED:Gpu, member yes', st['cls'] == 'UNMARKED:Gpu' and
      st['holder'] == 'flip' and st['gpu_in_chain'] and st['gpu_sw_or_s50'] and [s['how'] for s in st['steps']] == ['holder', 'peer'], st)
check('stand pc: -w records printed with peer', st['w'] and st['w'][0]['peer'] == 1 and st['w'][0]['kind'] == 'gpu_wait', st['w'])
THR_PC2 = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', Sw=S // 2 - 1, S=S // 2 - 1, r=2),
           thr(2, 'DrawThread', 'guest', W={'gpu_wait': S})]
res = read('stand_pc2', build({T0 + 1: dict(dt=230000, diag=diag_block(FIRST + T0 + 1, 230000, instr=0, threads=THR_PC2,
                                                                      waits=[dict(slot=2, kind='gpu_wait', waker=1)]))},
                              test_fire_idx=T0 + 1, stand_mode='gpusleep'))
st = res['stand'][0]
check('stand pc: GuestGpu Sw 19 + S 19 of 40 -> member no by the letter, variant Sw + S yes', st['gpu_in_chain'] and
      not st['gpu_sw_or_s50'] and st['gpu_sw_plus_s50'], st)
res = read('stand_pc3', build({T0 + 1: dict(dt=230000, diag=diag_block(FIRST + T0 + 1, 230000, instr=0,
                                                                      threads=[thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', Sw=S),
                                                                               thr(2, 'DrawThread', 'guest', W={'gpu_wait': S})]))},
                              test_fire_idx=T0 + 1, stand_mode='gpusleep'))
st = res['stand'][0]
THR_PC4 = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', S=S), thr(2, 'DrawThread', 'guest', W={'gpu_wait': S})]
_res4 = read('stand_pc4', build({T0 + 1: dict(dt=230000, diag=diag_block(FIRST + T0 + 1, 230000, instr=0, threads=THR_PC4,
                                                                        waits=[dict(slot=2, kind='gpu_wait', waker=-1, peer=1)]))},
                                test_fire_idx=T0 + 1, stand_mode='gpusleep'))
_st4 = _res4['stand'][0]
check('stand pc: GuestGpu S 40 of 40 (not Sw) in the chain -> member yes', _st4['gpu_in_chain'] and _st4['gpu_sw_or_s50'], _st4)
check('stand pc: no waker, no peer -> EMU_WAIT:gpu_wait, GuestGpu not in the chain', st['cls'] == 'EMU_WAIT:gpu_wait' and
      not st['gpu_in_chain'] and not st['gpu_sw_or_s50'], st)

# ---- stand and load windows
res = read('stand', build({T0 + 1: dict(dt=230000, lat=BASE_LAT + 200000, diag=diag_block(FIRST + T0 + 1, 230000, instr=0,
                                                                                      threads=thr_out_present))}, test_fire_idx=T0 + 1))
st = res['stand']
check('stand: 3 frames after the fire line, the first is the stand frame', st is not None and len(st) == 3 and st[0]['n'] == FIRST + T0 + 1,
      st)
check('stand frame EMU_CALL:present via the output thread', st[0]['cls'].startswith('EMU_CALL:present') and st[0]['holder'] == 'output', st[0])
load = dict(status='done', mode='all', n_start=FIRST + T0 - 2, n_end=FIRST + T0 - 1)
res = read('load', build({T0 + 2: dict(dt=150000, diag=diag_block(FIRST + T0 + 2, 150000, instr=0, other=int(0.8 * 32 * 150000)))}),
           load=load)
L = res['load']
check('load frames n_start..n_end+3 (5 frames)', len(L['frames']) == 5 and L['frames'][0]['n'] == FIRST + T0 - 2, [x['n'] for x in L['frames']])
check('load: stretched frame found with ratio 0.8', L['called'] and L['stretched'][0]['ratio'] == 0.8, L['stretched'])
res = read('load_none', build({T0 + 6: dict(dt=150000, diag=diag_block(FIRST + T0 + 6, 150000, instr=0))}), load=load)
check('load: a stretched frame outside n_end+3 does not call PK-D', not res['load']['called'], res['load']['stretched'])

# ---- U5 members
res = read('u5', build({}, dt_by_idx=dict((i, 40000) for i in range(723, 829))))
check('U5(1) median of idx 723..828', res['u5_med_dt'] == 40000, res['u5_med_dt'])
res = read('u5b', build({}, dt_by_idx={722: 99999, 829: 99999}))
check('U5(1) window edges 723 and 828 (722, 829 outside)', res['u5_med_dt'] == BASE_DT, res['u5_med_dt'])
half = dict((i, 40000) for i in range(723, 776))
half.update(dict((i, 30000) for i in range(776, 829)))
res = read('u5c', build({}, dt_by_idx=half))
check('U5(1) 106 frames 723..828: 53 x 40 000 + 53 x 30 000 -> 35 000', res['u5_med_dt'] == 35000, res['u5_med_dt'])
res = read('u5_70', build({T0: dict(dt=70000, diag=None), T0 + 40: dict(dt=69999, diag=None), T0 + 80: dict(dt=150000, diag=diag_block(
    FIRST + T0 + 80, 150000, instr=60000)), T0 + 120: dict(dt=120000, diag=None)}, b5_idx=(T0 + 120,)))
check('U5(2) frames >= 70 ms: 70 000 counts, 69 999 not, INSTR_MADE and B5 not', res['u5_slow70'] == 1, res['u5_slow70'])
check('U5(3) mean dt of B5 frames', res['u5_b5_mean'] == 120000.0 and res['u5_b5_n'] == 1, res['u5_b5_mean'])

# ---- PK-A of the cold form (item 591 (v)(2)-(4)): domain, member, 'not called'
EARLY = 5            # idx 5 starts at ~0.13 s of the scene (below the old 10 s threshold)
GPU_RUN = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', R=S), thr(2, 'DrawThread', 'guest', W={'eq': S})]
res = read('pk3_early', build({EARLY: dict(dt=200000, diag=diag_block(FIRST + EARLY, 200000, instr=0, threads=GPU_RUN,
                                                                     waits=[dict(slot=2, kind='eq', waker=1)]))}, b5_idx=(EARLY,)))
check('PK-A cold: a B5 frame at 0.13 s is in the domain and armed (EMU_RUN:Gpu); not in the >= 10 s pk_a',
      [x['n'] for x in res['pk_a3']] == [FIRST + EARLY] and res['pk_a3'][0]['armed'] and res['pk_a3'][0]['cls'] == 'EMU_RUN:Gpu' and
      res['pk_a'] == [], (res['pk_a3'], res['pk_a']))
check('PK-A cold: one frame -> member NOT_CALLED', res['pk_a3_member'] == 'NOT_CALLED' and res['pk_a3_armed'] == 1, res['pk_a3_member'])
res = read('pk3_late', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, instr=0, threads=GPU_RUN,
                                                                 waits=[dict(slot=2, kind='eq', waker=1)]))}, b5_idx=(T0,)))
check('PK-A cold: a B5 frame after 10 s is in both domains', len(res['pk_a3']) == 1 and len(res['pk_a']) == 1, (res['pk_a3'], res['pk_a']))
res = read('pk3_instr', build({EARLY: dict(dt=200000, diag=diag_block(FIRST + EARLY, 200000, instr=100001, threads=GPU_RUN)),
                               EARLY + 30: dict(dt=200000, diag=diag_block(FIRST + EARLY + 30, 200000, instr=100000, threads=GPU_RUN))},
                              b5_idx=(EARLY, EARLY + 30)))
check('PK-A cold: dt - instr 99 999 out of the domain, 100 000 in it', [x['n'] for x in res['pk_a3']] == [FIRST + EARLY + 30] and
      [x['n'] for x in res['pk_a3_instr']] == [FIRST + EARLY], (res['pk_a3'], res['pk_a3_instr']))
res = read('pk3_slow', build({EARLY: dict(dt=99999, diag=None), EARLY + 30: dict(dt=100000, diag=None)}, b5_idx=(EARLY, EARLY + 30)))
check('PK-A cold: dt 99 999 not in the domain, 100 000 in it (no DiagB32 line: instr 0, NO_SAMPLES, not armed)',
      [x['n'] for x in res['pk_a3']] == [FIRST + EARLY + 30] and res['pk_a3'][0]['cls'] == 'NO_SAMPLES' and not res['pk_a3'][0]['armed'] and
      res['pk_a3'][0]['instr_us'] is None, res['pk_a3'])
res = read('pk3_notb5', build({EARLY: dict(dt=200000, diag=diag_block(FIRST + EARLY, 200000, instr=0, threads=GPU_RUN))}))
check('PK-A cold: a frame without dump lines (not B5) is not in the domain', res['pk_a3'] == [], res['pk_a3'])
_t = {}
for k in range(4):
    _t[EARLY + 30 * k] = dict(dt=200000, diag=diag_block(FIRST + EARLY + 30 * k, 200000, instr=0, threads=GPU_RUN if k < 2 else [
        thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', S=S)],
        waits=[dict(slot=2, kind='eq', waker=1)] if k < 2 else None))
res = read('pk3_fail', build(_t, b5_idx=tuple(_t)))
check('PK-A cold: 4 frames, 2 armed (EMU_RUN:Gpu) and 2 UNMARKED:DrawThread -> FAIL (2/4 < 2/3)', len(res['pk_a3']) == 4 and
      res['pk_a3_armed'] == 2 and res['pk_a3_member'] == 'FAIL', (res['pk_a3_armed'], res['pk_a3_member']))
_t = {}
for k in range(3):
    _t[EARLY + 30 * k] = dict(dt=200000, diag=diag_block(FIRST + EARLY + 30 * k, 200000, instr=0, threads=GPU_RUN if k < 2 else [
        thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', S=S)],
        waits=[dict(slot=2, kind='eq', waker=1)] if k < 2 else None))
res = read('pk3_arm', build(_t, b5_idx=tuple(_t)))
check('PK-A cold: 3 frames, 2 armed -> ARMED (2/3 exactly)', res['pk_a3_armed'] == 2 and res['pk_a3_member'] == 'ARMED',
      (res['pk_a3_armed'], res['pk_a3_member']))
_t = {}
for k in range(3):
    _t[EARLY + 30 * k] = dict(dt=200000, diag=diag_block(FIRST + EARLY + 30 * k, 200000, instr=0, threads=[
        thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', H={'qsubmit': S}), thr(2, 'DrawThread', 'guest', W={'eq': S})],
        waits=[dict(slot=2, kind='eq', waker=1)]))
res = read('pk3_call', build(_t, b5_idx=tuple(_t)))
check('PK-A cold: EMU_CALL ending on GuestGpu armed, 3 of 3 -> ARMED', res['pk_a3_armed'] == 3 and res['pk_a3_member'] == 'ARMED' and
      res['pk_a3'][0]['cls'].startswith('EMU_CALL:qsubmit'), res['pk_a3'])
for n, a, want in ((0, 0, 'NOT_CALLED'), (2, 2, 'NOT_CALLED'), (3, 2, 'ARMED'), (3, 1, 'FAIL'), (6, 4, 'ARMED'), (6, 3, 'FAIL'),
                   (9, 6, 'ARMED'), (9, 5, 'FAIL'), (3, 3, 'ARMED')):
    check('pka_member(%d, %d) = %s' % (n, a, want), R.pka_member(n, a) == want, R.pka_member(n, a))
_pre = ['FrameTrace: n=%d dt_us=300000 lat_us=12000 gpu_proc=0 draws=10 gpu_busy_us=15000 cpu_gpu_us=30000' % (FIRST - 2),
        'FrameTrace: n=%d dt_us=99999 lat_us=12000 gpu_proc=0 draws=10 gpu_busy_us=15000 cpu_gpu_us=30000' % (FIRST - 1)]
res = read('pk3_pre', build({}, pre_scene=_pre))
check('reference: frames >= 100 ms between the level line and the first scene frame (300 000 yes, 99 999 no)',
      res['pre_scene_slow'] == [(FIRST - 2, 300000)] or res['pre_scene_slow'] == [[FIRST - 2, 300000]], res['pre_scene_slow'])
check('the first scene frame is still n=FIRST with pre-scene frames', res['first_n'] == FIRST, res['first_n'])
res = read('pk3_cold_lines', build({}, pre=['PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\\pipelines.bin yet\n',
                                            'ShaderSeed: installed (730 shaders)\n']))
check('precache and seed lines counted (no 1, recipes 0, other seed 1)', res['precache_no'] == 1 and res['precache_recipes'] == 0 and
      res['seed_other'] == ['ShaderSeed: installed (730 shaders)'], (res['precache_no'], res['precache_recipes'], res['seed_other']))
res = read('pk3_warm_lines', build({}, pre=['PipelinePrecache: 1856 recipes -> 1713 graphics + 143 compute pipelines queued\n',
                                            'PipelinePrecache: all pipelines created, 546 ms\n']))
check('warm precache line counted as recipes (the "all pipelines created" line is neither)', res['precache_no'] == 0 and
      res['precache_recipes'] == 1 and res['seed_other'] == [], (res['precache_no'], res['precache_recipes']))

# ---- admission (--dir form)
S18, TB = R.BIN_INST, R.BIN_TEST
FS8_OLD = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'
COLD_OK = dict(reserve_move='RESERVE MOVED files 1460 bytes 600000000 (dirs 2, root files 1345) listsha ab', reserve_cold='COLD OK',
               reserve_check='RESERVE IN AFTER 1460 of 1460')


def adm_dir(name, tag, env_extra, log_text, binary=TB, inst_b=S18, inst_a=S18, mcmp='manifest cmp EQUAL', load=None, hold=330,
            seal_text='seal\ntheta_load: 0.4562\n', reserve=None):
    d = os.path.join(TMP, 'adm_' + name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'log.txt'), 'w', encoding='ascii', newline='\n') as f:
        f.write(log_text)
    with open(os.path.join(d, 'seal.md'), 'w', encoding='ascii', newline='\n') as f:
        f.write(seal_text)
    env = dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_GUEST_ARGS='-lvl underwater_aerial_garden', KYTY_GPU_CLOCK_PIN='1',
               KYTY_GPU_MARKERS='0')
    env.update(env_extra)
    js = dict(binary_sha256=binary, prereg=dict(sha256=R.sha_file(os.path.join(d, 'seal.md'))), env=env,
              cmdline=['x', '--vulkan-validation', 'false', '--shader-validation', 'false'], guest_args='-lvl underwater_aerial_garden',
              hold_s=hold, attempts=[dict(outcome='STABLE')])
    with open(os.path.join(d, 'es.json'), 'w', encoding='ascii') as f:
        json.dump(js, f)
    for nm, v in (('installed_before', inst_b), ('installed_after', inst_a), ('manifest_cmp', mcmp)):
        with open(os.path.join(d, nm + '.txt'), 'w', encoding='ascii') as f:
            f.write(v + '\n')
    for nm in ('reserve_move', 'reserve_cold', 'reserve_check'):
        p = os.path.join(d, nm + '.txt')
        if reserve is not None and reserve.get(nm) is not None:
            with open(p, 'w', encoding='ascii') as f:
                f.write(reserve[nm] + '\n')
        elif os.path.exists(p):
            os.remove(p)
    lp = os.path.join(d, 'load.json')
    if load is not None:
        with open(lp, 'w', encoding='ascii') as f:
            json.dump(load, f)
    elif os.path.exists(lp):
        os.remove(lp)
    return R.read_tag(tag, R.paths(tag, d))


def fails(r):
    return [a[0][:60] for a in r['admission'] if not a[1]]


MODE = 'DiagB32: mode=1 period_us=5000 print_us=100000 ncpu=32 kstate=1'
PC_NO = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\\pipelines.bin yet\n'
PC_YES = 'PipelinePrecache: 1856 recipes -> 1713 graphics + 143 compute pipelines queued, 0 skipped\n'
log_on = build({}, pre=[MODE + '\n', PC_YES])
log_off = build({}, pre=[PC_YES])
log_cold = build({}, pre=[MODE + '\n', PC_NO])
F1 = R.form_of('b32_s01')
F0 = R.form_of('b32_z0c1')
check('form_of: =1 for b32_pa, b32_pa2, b32_sNN; =0 for b32_z0c1..5; GPU_WALL=1 always',
      R.form_of('b32_pa') == F1 == R.form_of('b32_pa2') == R.form_of('b32_s60') == dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1') and
      F0 == R.form_of('b32_z0c5') == dict(KYTY_DIAG_B32='0', KYTY_GPU_WALL='1'), (F1, F0))
r = adm_dir('pa', 'b32_pa', F1, log_cold, reserve=COLD_OK)
check('admission pa (cold) PASS', r['admitted'], fails(r))
check('theta in the reading = 0.4562 from the seal', r['theta'] == 0.4562, r['theta'])
r = adm_dir('pa2', 'b32_pa2', F1, log_cold, reserve=COLD_OK)
check('admission pa2 (cold) PASS', r['admitted'], fails(r))
r = adm_dir('pa_warmlog', 'b32_pa', F1, log_on, reserve=COLD_OK)
check('admission pa with a warm log (recipes loaded, no "no recipes yet") FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_both', 'b32_pa', F1, build({}, pre=[MODE + '\n', PC_NO, PC_YES]), reserve=COLD_OK)
check('admission pa with both precache lines FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_seed', 'b32_pa', F1, build({}, pre=[MODE + '\n', PC_NO, 'ShaderSeed: installed (730 shaders)\n']), reserve=COLD_OK)
check('admission pa with a ShaderSeed install line FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_nomove', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_move=None))
check('admission pa without reserve_move FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_movefail', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_move='RESERVE FAILED the live set is incomplete'))
check('admission pa with RESERVE FAILED FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_notcold', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_cold='COLD NOT 1 items: _ShaderSeeds/PPSA21564'))
check('admission pa with COLD NOT FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_noback', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_check='RESERVE NOT IN AFTER missing 3 of 1460'))
check('admission pa with the reserve not back FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_nocheck', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_check=None))
check('admission pa without reserve_check FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_off', 'b32_pa', F0, build({}, pre=[PC_NO]), reserve=COLD_OK)
check('admission pa with KYTY_DIAG_B32=0 FAIL', not r['admitted'], fails(r))
r = adm_dir('s01', 'b32_s01', F1, log_on)
check('admission s01 (warm) PASS', r['admitted'], fails(r))
r = adm_dir('s01_res', 'b32_s01', F1, log_on, reserve=COLD_OK)
check('admission s01 with cold reserve files FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_res1', 'b32_s01', F1, log_on, reserve=dict(reserve_move=None, reserve_cold=None, reserve_check='RESERVE IN AFTER 1 of 1'))
check('admission s01 with one reserve file FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_cold', 'b32_s01', F1, log_cold)
check('admission s01 with a cold log (warm form: precache line is reference) PASS', r['admitted'], fails(r))
r = adm_dir('s60', 'b32_s60', F1, log_on)
check('admission s60 PASS', r['admitted'], fails(r))
r = adm_dir('z0c', 'b32_z0c1', F0, log_off)
check('admission z0c1 (=0) PASS', r['admitted'], fails(r))
r = adm_dir('z0c_diag', 'b32_z0c1', F0, log_on)
check('admission z0c1 with a DiagB32 mode line FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_off', 'b32_s01', F1, log_off)
check('admission s01 without the DiagB32 mode line FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_f0', 'b32_s01', F0, log_on)
check('admission s01 with the env KYTY_DIAG_B32=0 FAIL', not r['admitted'], fails(r))
r = adm_dir('nothe', 'b32_s01', F1, log_on, seal_text='seal\n')
check('admission: no theta_load line in the seal FAIL, the log is not read', not r['admitted'] and r['log'] is None)
check('admission: the theta_load row itself FAIL when the seal has no line',
      [a[1] for a in r['admission'] if a[0].startswith('theta_load from the seal')] == [False], fails(r))
r = adm_dir('s01_stand', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], test_fire_idx=T0))
check('admission s01 with stand lines FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_load', 'b32_s01', F1, log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission s01 with a loader json FAIL', not r['admitted'], fails(r))
r = adm_dir('bin_s18', 'b32_s01', F1, log_on, binary=S18)
check('admission: json binary S18 (not the test binary) FAIL', not r['admitted'], fails(r))
r = adm_dir('inst_fs8', 'b32_s01', F1, log_on, inst_b=FS8_OLD, inst_a=FS8_OLD)
check('admission: installed FS8 (not S18) before and after FAIL', not r['admitted'], fails(r))
r = adm_dir('inst_after', 'b32_s01', F1, log_on, inst_a=TB)
check('admission: installed after = test binary FAIL', not r['admitted'], fails(r))
r = adm_dir('inst_before', 'b32_s01', F1, log_on, inst_b=S18[:63] + '0')
check('admission: installed before differs in the last hex digit FAIL', not r['admitted'], fails(r))
r = adm_dir('env_extra', 'b32_s01', dict(F1, KYTY_X='1'), log_on)
check('admission: extra env FAIL', not r['admitted'], fails(r))
r = adm_dir('env_nowall', 'b32_s01', dict(KYTY_DIAG_B32='1'), log_on)
check('admission: no KYTY_GPU_WALL FAIL', not r['admitted'], fails(r))
r = adm_dir('sig', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], seed=[SEED_LINES[0], SEED_LINES[1].replace('9177b426', '9177b427')]))
check('admission: translation signature not FS8 FAIL', not r['admitted'] and r['ref']['signature'].startswith('9177b427'))
r = adm_dir('vdir', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], seed=[SEED_LINES[0].replace('fixf19', 'fixf18'), SEED_LINES[1]]))
check('admission: cache variant dir not _fixf19 FAIL', not r['admitted'], fails(r))
r = adm_dir('noseed', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], seed=[]))
check('admission: no ShaderSeed line FAIL', not r['admitted'], fails(r))
r = adm_dir('recov', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], recovering=True))
check('admission: Recovering Vulkan swapchain FAIL', not r['admitted'], fails(r))
r = adm_dir('cache', 'b32_s01', F1, log_on, mcmp='manifest cmp DIFFER only-before 1 only-after 1')
check('admission: caches not returned FAIL', not r['admitted'], fails(r))
r = adm_dir('hold', 'b32_s01', F1, log_on, hold=300)
check('admission: hold 300 FAIL', not r['admitted'], fails(r))
rd = build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, cum={'rep_drop': 1}))}, pre=[MODE + '\n', PC_YES])
r = adm_dir('repdrop', 'b32_s01', F1, rd)
check('admission: rep_drop != 0 FAIL', not r['admitted'] and r['log']['rep_drop'] == 1, fails(r))
r = adm_dir('repeat', 'b32_s07_r1', F1, log_on)
check('a repeat name b32_s07_r1 reads with the form of b32_s07', r['admitted'] and r['form'] == 'b32_s07', fails(r))
r = adm_dir('repeat_pa', 'b32_pa_r2', F1, log_cold, reserve=COLD_OK)
check('a repeat name b32_pa_r2 is cold too', r['admitted'] and r['form'] == 'b32_pa' and
      any(a[0].startswith('cold form: reserve moved') for a in r['admission']), fails(r))
for good in ('b32_pa', 'b32_pa2', 'b32_s01', 'b32_s09', 'b32_s10', 'b32_s59', 'b32_s60', 'b32_z0c1', 'b32_z0c5', 'b32_s60_r6', 'b32_pa2_r1',
             'b32_z0c3_r4'):
    check('tag name %s accepted' % good, R.TAG_RX.match(good) is not None)
for bad in ('b32_s00', 'b32_s61', 'b32_s1', 'b32_s100', 'b32_pa3', 'b32_z0c0', 'b32_z0c6', 'b32_s01_r7', 'b32_s01_r0', 'b32_z0b', 'b32_ppb',
            'b32_pcb', 'b32_pd', 'b32_z0', 'f20_v25', '', 'b32_pa_r'):
    check('tag name %r refused' % bad, R.TAG_RX.match(bad) is None)
_p = R.paths('b32_s07')
check('paths b32_s07: F20l3 files and seal', _p['log'].replace('\\', '/') == 'C:/kyty/f287/f20l3/log_b32_s07.txt' and
      _p['seal'] == R.SEAL_PATH and _p['theta_src'] == R.SEAL_PATH and _p['reserve_move'].replace('\\', '/').endswith(
          'f20l3/runs/b32_s07/reserve_move.txt'), _p)
check('installed S18 constant = the full sha256 of item 590 / 591 (g)(3)',
      R.BIN_INST == 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a')

# ---- exact two-sided Mann-Whitney (item 555 (b)(2)) against a brute force over every split
import itertools  # noqa: E402


def brute_p(a, b):
    pooled = sorted(a + b)
    n = len(pooled)
    rank = {}
    i = 0
    while i < n:
        j = i
        while j + 1 < n and pooled[j + 1] == pooled[i]:
            j += 1
        rank[pooled[i]] = (i + j + 2) / 2.0
        i = j + 1
    vals = [rank[v] for v in a + b]
    m = len(b)
    mean = m * (n + 1) / 2.0
    obs = abs(sum(rank[v] for v in b) - mean)
    tot = ext = 0
    for comb in itertools.combinations(range(n), m):
        tot += 1
        if abs(sum(vals[k] for k in comb) - mean) >= obs - 1e-9:
            ext += 1
    return ext / float(tot)


for a, b, want in (([1, 2, 3], [4, 5, 6], 0.1), ([1, 2, 3, 4], [5, 6, 7, 8], 2.0 / 70), ([4, 5, 6], [1, 2, 3], 0.1),
                   ([1, 2, 3], [1, 2, 3], 1.0)):
    u, p = R.mw_exact(a, b)
    check('mw_exact %s vs %s p = %.4f' % (a, b, want), abs(p - want) < 1e-12, p)
for a, b in (([1, 1, 2, 5, 7], [2, 3, 3, 9]), ([10, 20, 20, 30, 30, 30], [20, 30, 40, 40]), ([5, 6, 7, 8, 9, 10, 11], [1, 2, 6, 7]),
             ([36000, 36500, 41000, 37000, 35000, 36000], [36171.5, 35115, 46632, 36000, 34904.5]),
             ([1, 2, 3, 4, 5, 6, 7, 8], [2, 4, 6])):
    check('mw_exact = brute force over every split %s / %s' % (a[:3], b[:3]), abs(R.mw_exact(a, b)[1] - brute_p(a, b)) < 1e-12,
          (R.mw_exact(a, b)[1], brute_p(a, b)))
check('mw_exact U of a: [1,2,3] vs [4,5,6] -> 0', R.mw_exact([1, 2, 3], [4, 5, 6])[0] == 0.0, R.mw_exact([1, 2, 3], [4, 5, 6]))
_base = list(R.U5_F20E_MEDS)
check('U5 F20e base: 11 medians, median 36 171.5', len(_base) == 11 and statistics.median(_base) == 36171.5, statistics.median(_base))
u = R.u5_one(_base, _base)
check('u5_one: the base against itself - dev 0, p 1, does not fire', u['dev'] == 0 and abs(u['p'] - 1.0) < 1e-12 and u['fires'] is False, u)
hi = [x * 1.10 for x in _base] + [40000.0]
u = R.u5_one(hi, _base)
check('u5_one: +10 %% on 12 tags - dev > 2 %% and p < 0.05 -> fires', u['fires'] is True and u['p'] < 0.05 and u['dev'] > 0.02, u)
u = R.u5_one([40000.0], _base)
check('u5_one: one tag +10.6 %% - p >= 0.05 -> does not fire (the test, not the 2 %% alone)', u['fires'] is False and u['p'] >= 0.05, u)
near = [36171.5 * 1.019 + k for k in range(12)]
u = R.u5_one(near, _base)
check('u5_one: median +1.9 %% - does not fire even when p is small', u['fires'] is False and abs(u['dev']) <= 0.02, u)
lo = [x * 0.9 for x in _base] + [30000.0]
u = R.u5_one(lo, _base)
check('u5_one: -10 %% two-sided -> fires', u['fires'] is True and u['dev'] < -0.02, u)
check('u5_one: second mode counted > 40 000 (F20e 3 of 11)', R.u5_one(_base, _base)['base_second_mode'] == 3)
check('u5_one: no medians -> fires None', R.u5_one([], _base)['fires'] is None)

# ---- series summary, stop rule, U5 of the series, PK-A over b32_pa / b32_pa2 (fake runs/<tag>/read.json)
RUNS = os.path.join(TMP, 'runs_series')


def put(tag, admitted=True, hold=True, K=0, cls=None, fam=None, med=36000.0, slow70=0, b5=(), zw=0, pk3=None):
    d = os.path.join(RUNS, tag)
    os.makedirs(d, exist_ok=True)
    pk3 = pk3 or []
    log = dict(hold=hold, K=K, hold_class=cls, hold_family=fam, u5_med_dt=med, u5_slow70=slow70, u5_b5_n=len(b5),
               u5_b5_mean=(sum(b5) / float(len(b5))) if b5 else None, zero_w_sum=dict(torn_w=zw),
               pk_a3=[dict(n=k, armed=a) for k, a in enumerate(pk3)], pk_a3_armed=sum(1 for a in pk3 if a),
               pk_a3_member=R.pka_member(len(pk3), sum(1 for a in pk3 if a)))
    with open(os.path.join(d, 'read.json'), 'w', encoding='ascii') as f:
        json.dump(dict(admitted=admitted, log=log), f)
    with open(os.path.join(d, 'read.txt'), 'w', encoding='ascii') as f:
        f.write(tag + '\n')


def series_of(upto=None):
    return R.series(RUNS, upto)


def line(out, key):
    return [x for x in out if x.startswith(key)]


shutil.rmtree(RUNS, ignore_errors=True)
for k in range(1, 29):
    put('b32_s%02d' % k)
out = series_of()
check('series: 28 holds -> CONTINUE', line(out, 'HOLDS 28 K 0') and line(out, 'STOP RULE CONTINUE (holds 28'), out[-12:])
put('b32_s29')
out = series_of()
check('series: 29 holds K 0 -> STOP_U2', line(out, 'STOP RULE STOP_U2 ') or line(out, 'STOP RULE STOP_U2 (K 0'), line(out, 'STOP RULE'))
put('b32_s29', K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
put('b32_s05', K=1, cls='UNMARKED:Gpu', fam='UNMARKED')
out = series_of()
check('series: 29 holds K 2 -> CONTINUE up to K 3 or 60', line(out, 'HOLDS 29 K 2') and line(out, 'STOP RULE CONTINUE (K 2 at 29'),
      line(out, 'STOP RULE'))
put('b32_s12', K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
out = series_of()
check('series: 29 holds K 3 -> STOP_READ', line(out, 'STOP RULE STOP_READ (K 3 >= 3 at 29'), line(out, 'STOP RULE'))
check('series: class shares of K - (iv) top family EMU_RUN 2/3', any('top family EMU_RUN 0.6667' in x for x in out),
      [x for x in out if 'top family' in x])
check('series: (i) UNDETERMINED + UNMARKED + NO_SAMPLES 1/3', any('(i) UNDETERMINED + UNMARKED + NO_SAMPLES 0.3333' in x for x in out),
      [x for x in out if '(i)' in x])
put('b32_s12', K=0)
put('b32_s30', admitted=False, K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
put('b32_s30_r1', K=0)
out = series_of()
check('series: an interfered tag is replaced by its admitted repeat (s30 not admitted, s30_r1 counts once)',
      line(out, 'HOLDS 30 K 2') and line(out, 'SERIES over') and 'admitted series tags 30' in out[0], out[0])
put('b32_s31', hold=False)
out = series_of()
check('series: an admitted tag without a hold is not a hold', line(out, 'HOLDS 30 K 2') and 'admitted series tags 31' in out[0], out[0])
put('b32_pa', K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
put('b32_z0c1', K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
out = series_of()
check('series: b32_pa and b32_z0c tags are not series holds', line(out, 'HOLDS 30 K 2'), line(out, 'HOLDS'))
for k in range(32, 61):
    put('b32_s%02d' % k)
out = series_of()
check('series: 59 holds K 2 -> STOP_U2PRIME only at 60 holds (s31 has no hold)', line(out, 'HOLDS 59 K 2') and
      line(out, 'STOP RULE CONTINUE (K 2 at 59'), line(out, 'STOP RULE'))
put('b32_s31')
out = series_of()
check('series: 60 holds K 2 -> STOP_U2PRIME', line(out, 'HOLDS 60 K 2') and line(out, 'STOP RULE STOP_U2PRIME'), line(out, 'STOP RULE'))
out = series_of(10)
check('series --upto 10: the first 10 admitted series tags', 'admitted series tags 10 (first 10)' in out[0] and line(out, 'HOLDS 10 K 1'),
      (out[0], line(out, 'HOLDS')))
# U5 of the series
shutil.rmtree(RUNS, ignore_errors=True)
for k in range(1, 11):
    put('b32_s%02d' % k, med=36000.0 + 10 * k)
out = series_of()
check('series U5(1) vs F20e: base medians near 36 000 -> does not fire', any(x.startswith('U5(1) vs F20e 11') and "'fires': False" in x
                                                                             for x in out), line(out, 'U5(1)'))
check('series U5(3): no B5 frames -> not computable, not in any of', line(out, 'U5(3) not computable') and line(out, 'U5 ANY no'),
      line(out, 'U5'))
check('series U5(1): 2 of 7 =0 tags without the b32_z0c tags -> not used', line(out, 'U5(1) base of item 591 (d)(2): 2 of 7'),
      line(out, 'U5(1) base'))
for k in range(1, 11):
    put('b32_s%02d' % k, med=47000.0 + 10 * k)
out = series_of()
check('series U5(1) vs F20e: medians 47 000 -> fires, U5 ANY FIRES', any(x.startswith('U5(1) vs F20e 11') and "'fires': True" in x
                                                                        for x in out) and line(out, 'U5 ANY FIRES'), line(out, 'U5'))
for k in range(1, 5):
    put('b32_z0c%d' % k, med=47000.0 + 7 * k)
out = series_of()
check('series U5(1): 4 of 5 b32_z0c -> base not used, F20e base decides', line(out, 'U5(1) base of item 591 (d)(2): 6 of 7') and
      line(out, 'U5 ANY FIRES (U5(1) by F20e 11'), line(out, 'U5'))
put('b32_z0c5', admitted=False, med=47000.0)
out = series_of()
check('series U5(1): a non-admitted b32_z0c5 does not complete the base', line(out, 'U5(1) base of item 591 (d)(2): 6 of 7'), line(out, 'U5(1)'))
put('b32_z0c5_r1', med=47035.0)
out = series_of()
check('series U5(1): 7 =0 tags (b32_z0, b32_z0b, b32_z0c1..5) -> base decides, medians 47 055 vs base 47 014 -> no',
      any(x.startswith('U5(1) vs the 7 =0 tags') and "'fires': False" in x for x in out) and line(out, 'U5 ANY no (U5(1) by 7 =0 tags'),
      line(out, 'U5'))
put('b32_s03', med=47030.0, b5=(200000.0,))
out = series_of()
check('series U5(3): pooled B5 mean 200 000 > 1.25 x 134 767.7 -> yes, U5 ANY FIRES', any(x.startswith('U5(3) mean dt_us of B5 frames 200000.0')
                                                                                        and x.endswith('True') for x in out) and
      line(out, 'U5 ANY FIRES'), line(out, 'U5'))
put('b32_s03', med=47030.0, b5=(160000.0, 170000.0))
out = series_of()
check('series U5(3): pooled B5 mean 165 000 <= 168 459.6 -> no', any(x.startswith('U5(3) mean dt_us of B5 frames 165000.0') and
                                                                    x.endswith('False') for x in out), line(out, 'U5(3)'))
put('b32_s04', med=47040.0, zw=1)
out = series_of()
check('series U5(4): one tag with a nonzero invariant -> no', line(out, 'U5(4) tags with a nonzero _w invariant 1 (member >= 2): False'),
      line(out, 'U5(4)'))
put('b32_s05', med=47050.0, zw=2)
out = series_of()
check('series U5(4): two tags -> FIRES', line(out, 'U5(4) tags with a nonzero _w invariant 2 (member >= 2): True') and line(out, 'U5 ANY FIRES'),
      line(out, 'U5'))
put('b32_s04', med=47040.0)
put('b32_s05', med=47050.0)
put('b32_s06', med=47060.0, slow70=10)
out = series_of()
check('series U5(2): 10 frames >= 70 ms over 10 holds = 1.0 > 0.8415 -> True', line(out, 'U5(2) frames >= 70 ms 10 per hold 1.0') and
      line(out, 'U5 ANY FIRES'), line(out, 'U5(2)'))
put('b32_s06', med=47060.0, slow70=8)
out = series_of()
check('series U5(2): 0.8 per hold <= 0.8415 -> False', any(x.startswith('U5(2) frames >= 70 ms 8 per hold 0.8') and x.endswith('False')
                                                          for x in out), line(out, 'U5(2)'))
# PK-A over b32_pa / b32_pa2
shutil.rmtree(RUNS, ignore_errors=True)
out = R.pka(RUNS)
check('pka: nothing -> PENDING (b32_pa)', out[0] == 'PK-A PENDING (b32_pa)', out[0])
put('b32_pa', pk3=[True, True, False])
check('pka: b32_pa 3 frames 2 armed -> ARMED on b32_pa', R.pka(RUNS)[0] == 'PK-A ARMED on b32_pa', R.pka(RUNS)[0])
put('b32_pa', pk3=[True, False, False])
check('pka: b32_pa 3 frames 1 armed -> FAIL on b32_pa', R.pka(RUNS)[0] == 'PK-A FAIL on b32_pa', R.pka(RUNS)[0])
put('b32_pa', pk3=[True, True])
check('pka: b32_pa 2 frames -> PENDING b32_pa2', R.pka(RUNS)[0].startswith('PK-A PENDING (b32_pa < 3 frames -> b32_pa2'), R.pka(RUNS)[0])
put('b32_pa2', pk3=[True])
out = R.pka(RUNS)
check('pka: b32_pa 2 + b32_pa2 1 -> NOT_CALLED (each < 3), pooled variant printed ARMED', out[0].startswith('PK-A NOT_CALLED') and
      any('pooled): frames 3 armed 3 member ARMED' in x for x in out), out)
put('b32_pa2', pk3=[False, False, False, True])
check('pka: b32_pa2 4 frames 1 armed -> FAIL on b32_pa2', R.pka(RUNS)[0] == 'PK-A FAIL on b32_pa2', R.pka(RUNS)[0])
put('b32_pa2', admitted=False, pk3=[True, True, True])
put('b32_pa2_r1', pk3=[True, True, True])
check('pka: a non-admitted b32_pa2 is replaced by its admitted repeat -> ARMED on b32_pa2', R.pka(RUNS)[0] == 'PK-A ARMED on b32_pa2',
      R.pka(RUNS))
put('b32_pa', admitted=False, pk3=[True, True, True])
check('pka: a non-admitted b32_pa -> PENDING (b32_pa)', R.pka(RUNS)[0] == 'PK-A PENDING (b32_pa)', R.pka(RUNS)[0])
shutil.rmtree(RUNS, ignore_errors=True)

# ---- fixtures added after the first sens_b32.py run (12 edits missed of 172)
r = adm_dir('pa_nolines', 'b32_pa', F1, build({}, pre=[MODE + '\n']), reserve=COLD_OK)
check('admission pa without any PipelinePrecache line FAIL (the "no recipes yet" line is required)', not r['admitted'], fails(r))
_c5 = [SEED_LINES[0]] + [SEED_LINES[1]] * 5
res = read('seed5', build({}, seed=_c5))
check('five compatibility lines: none of them is an "other ShaderSeed line"', res['seed_other'] == [] and len(res['sig']) == 4,
      (res['seed_other'], len(res['sig'])))
res = read('pk3_load', build({EARLY: dict(dt=200000, diag=diag_block(FIRST + EARLY, 200000, instr=0, threads=GPU_RUN,
                                                                    waits=[dict(slot=2, kind='eq', waker=1)], other=int(0.8 * 32 * 200000)))},
                             b5_idx=(EARLY,)), theta=0.4562)
check('PK-A cold domain is classified with theta_load (other_us 0.8 -> HOST_LOAD, not armed)', res['pk_a3'][0]['cls'] == 'HOST_LOAD' and
      not res['pk_a3'][0]['armed'], res['pk_a3'])
_pre = ['FrameTrace: n=%d dt_us=100000 lat_us=12000 gpu_proc=0 draws=10 gpu_busy_us=15000 cpu_gpu_us=30000' % (FIRST - 1)]
res = read('pk3_pre100', build({}, pre_scene=_pre))
check('reference pre-scene frames: dt exactly 100 000 counts', [list(x) for x in res['pre_scene_slow']] == [[FIRST - 1, 100000]],
      res['pre_scene_slow'])
_m = [37000.0] * 11 + [50000.0] * 10
u = R.u5_one(_m, _base)
check('u5_one: median +2.29 %% (between 2 %% and 3 %%) with p < 0.05 -> fires', 0.02 < u['dev'] < 0.03 and u['p'] < 0.05 and u['fires'] is True,
      u)
_m = [41000.0 + 10 * k for k in range(1, 11)]
u = R.u5_one(_m, _base)
check('u5_one: dev > 2 %% and 0.05 <= p < 0.10 -> does not fire', u['dev'] > 0.02 and 0.05 <= u['p'] < 0.10 and u['fires'] is False, u)
check('U5 F20e base: the 11 medians of base_f20l.txt lines 33-43 exactly', tuple(R.U5_F20E_MEDS) == (
    36818.5, 46632.0, 34904.5, 35800.0, 36171.5, 36082.0, 36443.0, 35844.0, 35115.0, 41596.0, 45939.5), R.U5_F20E_MEDS)
_z = []
for _f in ('C:/kyty/f287/f20l/runs/b32_z0/read.json', 'C:/kyty/f287/f20l2/runs/b32_z0b/read.json'):
    _z.append(json.load(open(_f, encoding='utf-8'))['log']['u5_med_dt'] if os.path.exists(_f) else None)
check('U5 =0 base: b32_z0 and b32_z0b medians = the F20l / F20l2 read.json', R.U5_Z0_MEDS == (('b32_z0', _z[0]), ('b32_z0b', _z[1])) and
      _z == [36451.5, 41478.5], (R.U5_Z0_MEDS, _z))
shutil.rmtree(RUNS, ignore_errors=True)
for k in range(1, 30):
    put('b32_s%02d' % k)
put('b32_s07', hold=False, K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
out = series_of()
check('series: a tag without a hold but with K 1 is not in K', line(out, 'HOLDS 28 K 0'), line(out, 'HOLDS'))
put('b32_s07')
put('b32_s08', b5=(170000.0,))
out = series_of()
check('series U5(3): pooled B5 mean 170 000 (between 1.25 x and 1.3 x base) -> True', any(
    x.startswith('U5(3) mean dt_us of B5 frames 170000.0') and x.endswith('True') for x in out), line(out, 'U5(3)'))
shutil.rmtree(RUNS, ignore_errors=True)
put('b32_pa', pk3=[True, True, True])
put('b32_pa2', pk3=[False, False, False])
check('pka: b32_pa ARMED decides, b32_pa2 (not needed) does not override', R.pka(RUNS)[0] == 'PK-A ARMED on b32_pa', R.pka(RUNS))
shutil.rmtree(RUNS, ignore_errors=True)
_tp = [dict(text='TestB32: armed delay_s=60 mode=present ms=200'), dict(text='TestB32: fire mode=present ms=200'),
       dict(text='TestB32: done mode=present slept_us=200000')]
check('stand_ok: present lines do not satisfy a gpusleep stand; they satisfy a present stand',
      not R.stand_ok(_tp, '60:gpusleep:200') and R.stand_ok(_tp, '60:present:200'))

# ---- strict cp1250 output without PYTHONIOENCODING (ASCII only)
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
env.pop('PYTHONUTF8', None)
p = subprocess.run([sys.executable, '-c', 'import sys; sys.stdout.reconfigure(encoding="cp1250", errors="strict"); import runpy; '
                    'sys.argv=["b32_read.py","--dir",%r,"--tag","b32_s01"]; runpy.run_path(%r, run_name="__main__")' % (
                        os.path.join(TMP, 'adm_s01'), os.path.join(HERE, 'b32_read.py'))], env=env, capture_output=True, cwd=HERE)
check('reader output in strict cp1250, rc 0, ASCII', p.returncode == 0 and all(b < 128 for b in p.stdout) and b'ADMISSION PASS' in p.stdout,
      (p.returncode, p.stderr[-300:]))

# ---- sha guard of the F20c reader copy
check('f20e_read.py sha256 = F20E_SHA', R.sha_file(R.F.__file__) == R.F20E_SHA)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d' % nchk)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
