"""F20l (HPP-631): fixtures of b32_read.py - every class and edge of item 550 (g), RC6, RC7, RC13, INSTR_MADE, K_I, the members of
item 552 (g), 553 (v), 554 (g), the _w invariants (event in window k, clean window k+1), the report of n between the FrameTrace lines
of n+1 and n+2 (item 551 (b)(5)), the stand and load windows, U5, admission, strict cp1250 output.  ASCII only; ends with ALL OK.
usage: python test_b32_read.py"""
import hashlib
import json
import os
import shutil
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
               flip=2, threads=None, waits=None, xw=None, x=True, hdr=True, cum=None):
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
        out.append('DiagB32-w: n=%d slot=%d tid=0 kind=%s obj=0x1 start_us=0 wait_us=%d overlap_us=%d waker=%d waker_tid=0 req_us=0 to=%d '
                   'open=0' % (n, w['slot'], w['kind'], w.get('wait', 50000), w.get('overlap', 50000), w.get('waker', -1), w.get('to', 0)))
    if x:
        z = dict((k, 0) for k in R.ZERO_W)
        z.update(xw or {})
        c = dict((k[:-2], 0) for k in R.ZERO_W)
        c.update(cum or {})
        out.append('DiagB32-x: n=%d slots=10 slot_full=%d slot_full_w=%d torn=%d torn_w=%d ring_drop=%d ring_drop_w=%d sgap_bad=%d '
                   'sgap_bad_w=%d lines_cut=%d lines_cut_w=%d req_miss=%d req_miss_w=%d sub_miss=%d sub_miss_w=%d short_stalls=0 '
                   'others_cut=0 w_cut=0 rep_drop=%d kq_fail=0 print_us=10 gap3p=0' % (
                       n, c['slot_full'], z['slot_full_w'], c['torn'], z['torn_w'], c['ring_drop'], z['ring_drop_w'], c['sgap_bad'],
                       z['sgap_bad_w'], c['lines_cut'], z['lines_cut_w'], c['req_miss'], z['req_miss_w'], c['sub_miss'], z['sub_miss_w'],
                       (cum or {}).get('rep_drop', 0)))
    return out


SEED_LINES = ['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\n',
              'ShaderSeed: compatibility=KytySeed1:PPSA21564:01.007.000:KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz\n']


def build(targets=None, nframes=9200, extra_after=None, b5_idx=(), pre=None, recovering=False, test_fire_idx=None, dump_line_after=None,
          dt_by_idx=None, seed=None):
    """targets: idx -> dict(dt, lat, gb, diag (list of lines or None)); the diag block of frame n goes after the FrameTrace of n+1."""
    targets = targets or {}
    dt_by_idx = dict(dt_by_idx or {})
    lines = ['loading\n'] + (SEED_LINES if seed is None else seed) + ['GuestOut: Level has started: \n'] + (pre or []) + \
        ['GuestOut: Level has started: underwater_aerial_garden\n']
    lines.append('FrameTrace: n=%d dt_us=40000 lat_us=12000 gpu_proc=0 draws=4000 gpu_busy_us=15000 cpu_gpu_us=30000\n' % FIRST)
    pending = {}
    for idx in range(1, nframes + 1):
        n = FIRST + idx
        if idx in b5_idx:
            lines.append('%_1 = OpTypeVoid\n')
        if test_fire_idx is not None and idx == test_fire_idx:
            lines.append('TestB32: armed delay_s=60 mode=present ms=200\n')
            lines.append('TestB32: fire mode=present ms=200\n')
            lines.append('TestB32: done mode=present slept_us=200000\n')
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

# ---- admission (--dir form)
FS8, TB = R.BIN_FS8, R.BIN_TEST


def adm_dir(name, tag, env_extra, log_text, binary=TB, inst_b=FS8, inst_a=FS8, mcmp='manifest cmp EQUAL', load=None, hold=330,
            seal_text='seal\n'):
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
    lp = os.path.join(d, 'load.json')
    if load is not None:
        with open(lp, 'w', encoding='ascii') as f:
            json.dump(load, f)
    elif os.path.exists(lp):
        os.remove(lp)
    return R.read_tag(tag, R.paths(tag, d), None)


MODE = 'DiagB32: mode=1 period_us=5000 print_us=100000 ncpu=32 kstate=1'
log_on = build({}, pre=[MODE + '\n'])
log_off = build({})
log_pp = build({}, pre=[MODE + '\n'], test_fire_idx=T0)
r = adm_dir('z0', 'b32_z0', R.FORM['b32_z0'], log_off)
check('admission z0 PASS', r['admitted'], [a for a in r['admission'] if not a[1]])
r = adm_dir('z0_diag', 'b32_z0', R.FORM['b32_z0'], log_on)
check('admission z0 with a DiagB32 mode line FAIL', not r['admitted'])
r = adm_dir('pd', 'b32_pd', R.FORM['b32_pd'], log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission pd PASS', r['admitted'], [a for a in r['admission'] if not a[1]])
r = adm_dir('pd_noload', 'b32_pd', R.FORM['b32_pd'], log_on)
check('admission pd without the loader FAIL', not r['admitted'])
r = adm_dir('pd2_wrongmode', 'b32_pd2', R.FORM['b32_pd2'], log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission pd2 with the loader mode all FAIL', not r['admitted'])
r = adm_dir('pp', 'b32_pp', R.FORM['b32_pp'], log_pp)
check('admission pp PASS', r['admitted'], [a for a in r['admission'] if not a[1]])
r = adm_dir('pp_nostand', 'b32_pp', R.FORM['b32_pp'], log_on)
check('admission pp without stand lines FAIL', not r['admitted'])
r = adm_dir('pc_as_pp', 'b32_pc', R.FORM['b32_pc'], log_pp)
check('admission pc with present stand lines FAIL', not r['admitted'])
r = adm_dir('pd_stand', 'b32_pd', R.FORM['b32_pd'], log_pp, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission pd with stand lines FAIL', not r['admitted'])
r = adm_dir('bin_fs8', 'b32_pd', R.FORM['b32_pd'], log_on, binary=FS8, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission: json binary FS8 (not the test binary) FAIL', not r['admitted'])
r = adm_dir('inst_after', 'b32_pd', R.FORM['b32_pd'], log_on, inst_a=TB, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission: installed after = test binary FAIL', not r['admitted'])
r = adm_dir('env_extra', 'b32_pd', dict(R.FORM['b32_pd'], KYTY_X='1'), log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission: extra env FAIL', not r['admitted'])
r = adm_dir('env_nowall', 'b32_pd', dict(KYTY_DIAG_B32='1'), log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission: no KYTY_GPU_WALL FAIL', not r['admitted'])
r = adm_dir('sig', 'b32_z0', R.FORM['b32_z0'], build({}, seed=[SEED_LINES[0], SEED_LINES[1].replace('9177b426', '9177b427')]))
check('admission: translation signature not FS8 FAIL', not r['admitted'] and r['ref']['signature'].startswith('9177b427'))
r = adm_dir('vdir', 'b32_z0', R.FORM['b32_z0'], build({}, seed=[SEED_LINES[0].replace('fixf19', 'fixf18'), SEED_LINES[1]]))
check('admission: cache variant dir not _fixf19 FAIL', not r['admitted'])
r = adm_dir('noseed', 'b32_z0', R.FORM['b32_z0'], build({}, seed=[]))
check('admission: no ShaderSeed line FAIL', not r['admitted'])
r = adm_dir('recov', 'b32_z0', R.FORM['b32_z0'], build({}, recovering=True))
check('admission: Recovering Vulkan swapchain FAIL', not r['admitted'])
r = adm_dir('cache', 'b32_z0', R.FORM['b32_z0'], log_off, mcmp='manifest cmp DIFFERENT')
check('admission: caches not returned FAIL', not r['admitted'])
r = adm_dir('hold', 'b32_z0', R.FORM['b32_z0'], log_off, hold=300)
check('admission: hold 300 FAIL', not r['admitted'])
rd = build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, cum={'rep_drop': 1}))}, pre=[MODE + '\n'])
r = adm_dir('repdrop', 'b32_pd', R.FORM['b32_pd'], rd, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission: rep_drop != 0 FAIL', not r['admitted'] and r['log']['rep_drop'] == 1)
r = adm_dir('repeat', 'b32_pd_r1', R.FORM['b32_pd'], log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('a repeat name b32_pd_r1 reads with the form of b32_pd', r['admitted'] and r['form'] == 'b32_pd')
check('tag name b32_pd_r7 refused', R.TAG_RX.match('b32_pd_r7') is None and R.TAG_RX.match('b32_px') is None)

# ---- strict cp1250 output without PYTHONIOENCODING (ASCII only)
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
env.pop('PYTHONUTF8', None)
p = subprocess.run([sys.executable, '-c', 'import sys; sys.stdout.reconfigure(encoding="cp1250", errors="strict"); import runpy; '
                    'sys.argv=["b32_read.py","--dir",%r,"--tag","b32_pp"]; runpy.run_path(%r, run_name="__main__")' % (
                        os.path.join(TMP, 'adm_pp'), os.path.join(HERE, 'b32_read.py'))], env=env, capture_output=True, cwd=HERE)
check('reader output in strict cp1250, rc 0, ASCII', p.returncode == 0 and all(b < 128 for b in p.stdout) and b'ADMISSION PASS' in p.stdout,
      (p.returncode, p.stderr[-300:]))

# ---- sha guard of the F20c reader copy
check('f20e_read.py sha256 = F20E_SHA', R.sha_file(R.F.__file__) == R.F20E_SHA)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d' % nchk)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
