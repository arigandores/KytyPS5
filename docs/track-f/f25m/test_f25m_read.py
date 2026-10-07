"""F25m (HPP-680): fixtures of f25m_read.py - item 613 (g)(3)-(5), (z)(2) with item 615 (b)(1), (2), (6), item 616 (b)(1), (2), (4),
item 618 (b)(5), item 619 (b)(1): the parsers of LongFrame / LogAsync / TestLogStall (field line= present, absent, several values, a
value holding 'line='), the LogAsync members (mode=1 once, the summary, KYTY_FIX_B36=0 without lines, RC3 drain_timeouts 0 / 1), the stand
admission (config, three sleeps, on=caller / writer, slept_us edge), the window [t0_ms - 2 000; t1_ms + 2 000] on both edges, the dt
edges 2 500 000 / 1 000 000, the stall edges 2 900 000 / 1 000 000, full_waits, the exit window 250 ms on both sides, the frame end from
LongFrame and from flip_ns, INSTR_POLL (poll_us 100 000 edge, the interval mapping, the FlipHold cap 32 -> POLL_UNKNOWN, INSTR_MADE_K2
first), S with flush=1, the stall overlap of a frame, the admission of every kind (env exact / extra / missing, binaries, prereg,
validation flag, hold option, snapshots, window events, signature, GamePatch, TestLogStall outside the stands, the user form without
FrameTrace), no harm v / w (each member and edge), table and series, the f25_read.py sha guard, ASCII output in strict cp1250.
The fixture builders build / diag_block / thr / klist are copied from C:/kyty/f287/f25f/test_f25_read.py (F25f).  ASCII only; ends
with ALL OK.
usage: python test_f25m_read.py"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f25m_read as M  # noqa: E402

R = M.R
TMP = os.path.join(HERE, 'fx_m_tmp')
print('suite test_f25m_read.py sha256 %s target f25m_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
    hashlib.sha256(open(os.path.join(HERE, 'f25m_read.py'), 'rb').read()).hexdigest()))

ok = True
nchk = 0


def check(name, cond, got=None):
    global ok, nchk
    nchk += 1
    if not cond:
        ok = False
        print('FAIL %s (got %s)' % (name, str(got)[:300]))


# ---- builders copied from F25f test_f25_read.py
BASE_DT, BASE_LAT, BASE_GB = 33333, 12000, 15000
FIRST = 100
T0 = 400
LV = M.POT


def thr(slot, name, role, R=0, r=0, Sr=0, Sw=0, S=0, W=None, H=None, peer=-1, X=0):
    return dict(slot=slot, name=name, role=role, R=R, r=r, Sr=Sr, Sw=Sw, S=S, W=W or {}, H=H or {}, peer=peer, X=X)


def klist(d):
    return ','.join('%s:%d' % (k, v) for k, v in d.items()) if d else '-'


XF = ('slot_full', 'torn', 'ring_drop', 'sgap_bad', 'lines_cut', 'req_miss', 'sub_miss')


def diag_block(n, dt, samples=40, instr=1000, sgap=5000, threads=None, flip_ns=None):
    out = []
    cov = dt - sgap
    fns = 10 ** 12 + n * 10 ** 6 if flip_ns is None else flip_ns
    if threads is None:
        threads = [thr(0, 'Present', 'Present', S=samples), thr(1, 'Gpu', 'Gpu', r=samples), thr(2, 'DrawThread', 'guest', S=samples)]
    out.append('DiagB32: n=%d dt_us=%d instr_us=%d samples=%d sgap_max_us=%d gap3p=0 i2=1 kstate=1 kq=1 kq_n=1 kq_us=900 m5r_us=0 '
               'proc_us=100000 sys_busy_us=100000 sys_idle_us=0 other_us=0 ncpu=32 snap_ok=1 snap_lag_us=10 flip_slot=2 flip_tid=7 '
               'flip_src=cpu lat_us=12000 vo_slot=0 gpu_slot=1 t_lines=%d w_lines=0 c_lines=0 cover_us=%d flip_ns=%d' % (
                   n, dt, instr, samples, sgap, len(threads), cov, fns))
    for t in threads:
        out.append('DiagB32-t: n=%d slot=%d tid=0 os_tid=1 name=%s role=%s must=1 X=%d R=%d r=%d Sr=%d Sw=%d S=%d W=%s H=%s SwR=- cpu_us=0 '
                   'top=- last=- obj=0x0 since_us=0 peer=%d' % (n, t['slot'], t['name'], t['role'], t['X'], t['R'], t['r'], t['Sr'],
                                                               t['Sw'], t['S'], klist(t['W']), klist(t['H']), t['peer']))
    z = dict((k, 0) for k in R.ZERO_W)
    out.append('DiagB32-x: n=%d slots=10 slot_full=0 slot_full_w=%d torn=0 torn_w=%d ring_drop=0 ring_drop_w=%d sgap_bad=0 '
               'sgap_bad_w=%d lines_cut=0 lines_cut_w=%d req_miss=0 req_miss_w=%d sub_miss=0 sub_miss_w=%d short_stalls=0 '
               'others_cut=0 w_cut=0 rep_drop=0 kq_fail=0 print_us=10 gap3p=0 ring_hold=0 ring_hold_w=0 hist_exh=0 hist_exh_w=0 '
               'w_cut_w=0 others_cut_w=0' % (n, z['slot_full_w'], z['torn_w'], z['ring_drop_w'], z['sgap_bad_w'], z['lines_cut_w'],
                                              z['req_miss_w'], z['sub_miss_w']))
    return out


SEED_LINES = ['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\n',
              'ShaderSeed: compatibility=KytySeed1:PPSA21564:01.007.000:KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz\n']
MODE = 'DiagB32: mode=1 period_us=5000 print_us=100000 ncpu=32 kstate=1'


def build(targets=None, nframes=9200, before=None, after=None, level=None, head=None, pre=None, draws=4000, tail=None):
    """targets: idx -> dict(dt, diag (lines) ); before: idx -> lines before FrameTrace idx; after: idx -> lines right after it."""
    targets = targets or {}
    lv = LV if level is None else level
    lines = list(head or []) + ['loading\n'] + SEED_LINES + ['GuestOut: Level has started: \n'] + [x + '\n' for x in (pre or [])] + \
        ['GuestOut: Level has started: %s\n' % lv]
    lines.append('FrameTrace: n=%d dt_us=40000 lat_us=12000 gpu_proc=0 draws=%d semwait_us=0 gpu_busy_us=15000 cpu_gpu_us=30000\n' % (
        FIRST, draws))
    pending = {}
    for idx in range(1, nframes + 1):
        n = FIRST + idx
        for l in (before or {}).get(idx, []):
            lines.append(l + '\n')
        t = targets.get(idx)
        dt = t['dt'] if t else BASE_DT
        lines.append('FrameTrace: n=%d dt_us=%d lat_us=%d gpu_proc=0 draws=%d semwait_us=0 gpu_busy_us=%d cpu_gpu_us=30000\n' % (
            n, dt, BASE_LAT, draws, BASE_GB))
        if t and t.get('diag') is not None:
            pending.setdefault(idx + 1, []).extend(t['diag'])
        if idx in pending:
            for l in pending.pop(idx):
                lines.append(l + '\n')
        for l in (after or {}).get(idx, []):
            lines.append(l + '\n')
    lines += [x + '\n' for x in (tail or [])]
    lines.append('Event: quit\n')
    return ''.join(lines)


if os.path.isdir(TMP):
    shutil.rmtree(TMP)
os.makedirs(TMP)


def wfile(d, name, text):
    with open(os.path.join(d, name), 'w', encoding='ascii', newline='\n') as f:
        f.write(text)


def scan_text(name, text, level=LV):
    d = os.path.join(TMP, 'sc_' + name)
    os.makedirs(d, exist_ok=True)
    wfile(d, 'log.txt', text)
    return M.scan_extra(os.path.join(d, 'log.txt'), level)


CFG0 = 'TestLogStall: config at_ms=160000 sleep_ms=3000 k=3 gap_ms=5000 on=caller'
CFG1 = 'TestLogStall: config at_ms=160000 sleep_ms=3000 k=3 gap_ms=5000 on=writer'
SUM0 = 'LogAsync: full_waits=0 full_wait_us=0 stalls=3 stall_cut=0 lines=100 bytes=1000 max_queued_bytes=500 sync_lines=0 drain_timeouts=0'
MODE1 = 'LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100'


def sleep(i, t0, on='caller', role='Present', line='FrameTrace-lite x', slept=3000100):
    s = 'TestLogStall: i=%d sleep_ms=3000 slept_us=%d t0_ms=%d t1_ms=%d on=%s tid=77 role=%s' % (i, slept, t0, t0 + 3000, on, role)
    return s + ('' if line is None else ' line="%s"' % line)


def lf(n, dt, t, a=0):
    return 'LongFrame: n=%d dt_us=%d log_async=%d t_ms=%d' % (n, dt, a, t)


def stall(us, t, flush=False):
    return 'LogAsync: stall us=%d queued_bytes=10 t_ms=%d%s' % (us, t, ' flush=1' if flush else '')


SL3 = [sleep(1, 160000), sleep(2, 168000), sleep(3, 176000)]

# ---- parsers
x = scan_text('parse', '\n'.join(['GuestOut: Level has started: ' + LV, lf(5, 2600000, 163100), 'LongFrame: n=6 dt_us=x',
                                  stall(3000000, 163000), stall(1000000, 170000, True), 'LogAsync: stall us=5', CFG0] + SL3 +
                                 ['TestLogStall: i=4 junk', SUM0, 'LogAsync: full_waits=1 full_wait_us=2', 'LogAsync: weird']) + '\n')
check('LongFrame parsed and the malformed one counted', len(x['lf']) == 1 and x['lf'][0] == dict(n=5, dt_us=2600000, log_async=0, t_ms=163100,
                                                                                               ln=2) and x['lf_bad'] == 1, (x['lf'], x['lf_bad']))
check('stall parsed (flush flag) and the malformed one counted', [(s['us'], s['flush']) for s in x['stall']] == [(3000000, False), (1000000, True)]
      and x['stall_bad'] == 1, (x['stall'], x['stall_bad']))
check('config parsed', x['cfg'] == [dict(at_ms=160000, sleep_ms=3000, k=3, gap_ms=5000, on='caller')], x['cfg'])
check('three sleeps parsed with line=, the malformed counted', [(s['i'], s['line'], s['role']) for s in x['sleep']] ==
      [(1, 'FrameTrace-lite x', 'Present')] * 1 + [(2, 'FrameTrace-lite x', 'Present'), (3, 'FrameTrace-lite x', 'Present')] and
      x['sleep_bad'] == 1, (x['sleep'], x['sleep_bad']))
check('summary: full one parsed, a partial one and an unknown LogAsync line are bad', len(x['summary']) == 1 and x['summary'][0]['lines'] == 100
      and x['summary_bad'] == 2, (x['summary'], x['summary_bad']))
x = scan_text('line_abs', sleep(1, 1000, line=None) + '\n')
check('line= absent -> None', x['sleep'][0]['line'] is None and x['sleep_bad'] == 0, x['sleep'])
x = scan_text('line_many', '\n'.join([sleep(1, 1000, line='LongFrame: n=1'), sleep(2, 9000, role='Gpu', line='FaultTrace-gpu ?'),
                                      sleep(3, 17000, role='other', line='a line=b c')]) + '\n')
check('line= several values per sleep, a value holding line= read whole', [(s['line'], s['role']) for s in x['sleep']] ==
      [('LongFrame: n=1', 'Present'), ('FaultTrace-gpu ?', 'Gpu'), ('a line=b c', 'other')], x['sleep'])
x = scan_text('line_empty', sleep(1, 1000, line='') + '\n')
check('line="" -> empty string, not absent', x['sleep'][0]['line'] == '', x['sleep'])

# ---- LogAsync members
x = scan_text('la1', '\n'.join([MODE1, SUM0]) + '\n')
mem, why, rc3, summ = M.logasync(x, '1')
check('=1: mode once + summary -> members ok, no interference, no RC3', all(b for _, b in mem) and why is None and rc3 is None, (mem, why, rc3))
x = scan_text('la1_nomode', SUM0 + '\n')
mem, why, rc3, summ = M.logasync(x, '1')
check('=1 without mode=1 -> interference tag (item 615 (b)(2))', why is not None and why.startswith('tag'), why)
x = scan_text('la1_mode0', 'LogAsync: mode=0 requested=1 reason=direction\n' + SUM0 + '\n')
check('=1 with mode=0 requested=1 -> interference tag', M.logasync(x, '1')[1].startswith('tag'), M.logasync(x, '1')[1])
x = scan_text('la1_mode2', '\n'.join([MODE1, MODE1, SUM0]) + '\n')
check('=1 with mode=1 twice -> member fails', not all(b for _, b in M.logasync(x, '1')[0]), M.logasync(x, '1')[0])
x = scan_text('la1_nosum', MODE1 + '\n')
mem, why, rc3, summ = M.logasync(x, '1')
check('=1 without the summary -> interference run (item 615 (b)(6))', why is not None and why.startswith('run'), why)
x = scan_text('la1_rc3', '\n'.join([MODE1, SUM0.replace('drain_timeouts=0', 'drain_timeouts=1')]) + '\n')
mem, why, rc3, summ = M.logasync(x, '1')
check('RC3: drain_timeouts 1 -> row, still admitted', why is None and rc3 is not None and 'drain_timeouts 1' in rc3, (why, rc3))
x = scan_text('la0', 'nothing\n')
check('=0 without LogAsync lines -> ok', M.logasync(x, '0')[1] is None and all(b for _, b in M.logasync(x, '0')[0]))
x = scan_text('la0_stall', stall(200000, 5) + '\n')
check('=0 with a LogAsync line -> interference', M.logasync(x, '0')[1] is not None)

# ---- stand admission
x = scan_text('sa0', '\n'.join([CFG0] + SL3) + '\n')
check('stand admission =0 caller: PASS', all(b for _, b in M.stand_admission(x, '0')), M.stand_admission(x, '0'))
check('stand admission: =1 wants writer -> FAIL on caller lines', not all(b for _, b in M.stand_admission(x, '1')))
x = scan_text('sa1', '\n'.join([CFG1] + [sleep(i, 1000 * i, on='writer', role='other') for i in (1, 2, 3)]) + '\n')
check('stand admission =1 writer: PASS', all(b for _, b in M.stand_admission(x, '1')), M.stand_admission(x, '1'))
x = scan_text('sa_two', '\n'.join([CFG0] + SL3[:2]) + '\n')
check('stand admission: two sleeps -> FAIL', not all(b for _, b in M.stand_admission(x, '0')))
x = scan_text('sa_edge', '\n'.join([CFG0, sleep(1, 1, slept=2900000), sleep(2, 9000, slept=2900000), sleep(3, 17000, slept=2900000)]) + '\n')
check('stand admission: slept_us 2 900 000 edge -> PASS', all(b for _, b in M.stand_admission(x, '0')))
x = scan_text('sa_low', '\n'.join([CFG0, sleep(1, 1, slept=2899999)] + SL3[1:]) + '\n')
check('stand admission: slept_us 2 899 999 -> FAIL', not all(b for _, b in M.stand_admission(x, '0')))
x = scan_text('sa_cfg', '\n'.join([CFG0.replace('sleep_ms=3000', 'sleep_ms=2000')] + SL3) + '\n')
check('stand admission: config sleep_ms 2000 -> FAIL', not all(b for _, b in M.stand_admission(x, '0')))
x = scan_text('sa_cfgon', '\n'.join([CFG1] + SL3) + '\n')
check('stand admission: config on=writer with caller sleeps at =0 -> FAIL', not all(b for _, b in M.stand_admission(x, '0')))

# ---- exit window
x = scan_text('ex', '\n'.join([CFG0] + SL3) + '\n')
# exit = 160000 - 60000 + 1000 x (stable + hold); last t1 = 179000; need exit >= 181250
a, b, gap = M.exit_member(x, dict(stable_s=50.0, hold_s=31.25))
check('exit window: gap 250 -> member ok', b and gap == 250, (a, gap))
a, b, gap = M.exit_member(x, dict(stable_s=50.0, hold_s=31.249))
check('exit window: gap 249 -> member fails', not b and gap == 249, (a, gap))
a, b, gap = M.exit_member(x, dict(stable_s=None, hold_s=150))
check('exit window: no stable_s -> not computable, fails', not b and gap is None, a)

ATT = dict(stable_s=14.0, hold_s=150.0, outcome='ok', hold_exit=None)
# sleeps at 160000..163000, 168000..171000, 176000..179000; windows [158000; 165000], [166000; 173000], [174000; 181000]


def s0(lines, base='b36_s0'):
    x = scan_text('st_' + base + str(abs(hash(tuple(lines))) % 100000), '\n'.join(['GuestOut: Level has started: ' + LV, CFG0] + SL3 + lines) + '\n')
    return M.read_stand(base, x, None, ATT)


st = s0([lf(1, 2500000, 158000), lf(2, 2600000, 173000), lf(3, 3000000, 174000)])
check('s0: hits at t0 - 2 000 and t1 + 2 000 edges (in), dt 2 500 000 edge -> every sleep, PASS', st['ok'], st['members'])
st = s0([lf(1, 2500000, 157999), lf(2, 2600000, 173000), lf(3, 3000000, 174000)])
check('s0: t0 - 2 001 (out) -> sleep 1 without a hit, FAIL', not st['ok'] and not st['per_sleep'][0]['hits'], st['per_sleep'])
st = s0([lf(1, 2500000, 165001), lf(2, 2600000, 173000), lf(3, 3000000, 174000)])
check('s0: t1 + 2 001 (out of window 1, also out of window 2) -> FAIL', not st['ok'] and not st['per_sleep'][0]['hits'], st['per_sleep'])
st = s0([lf(1, 2499999, 160500), lf(2, 2600000, 173000), lf(3, 3000000, 174000)])
check('s0: dt 2 499 999 -> not a hit, FAIL', not st['ok'], st['per_sleep'])
st = s0([lf(2, 2600000, 170000), lf(3, 3000000, 178000)])
check('s0: 2 of 3 sleeps -> FAIL (letter every sleep)', not st['ok'] and sum(1 for p in st['per_sleep'] if p['hits']) == 2, st['members'])
check('s0: sleep rows carry role, tid, line (item 616 (b)(1))', st['sleeps'][0]['role'] == 'Present' and st['sleeps'][0]['line'] ==
      'FrameTrace-lite x' and st['sleeps'][0]['tid'] == 77, st['sleeps'])
x = scan_text('st_exit', '\n'.join(['GuestOut: Level has started: ' + LV, CFG0] + SL3 + [lf(1, 2500000, 158000), lf(2, 2600000, 173000),
                                                                                          lf(3, 3000000, 174000)]) + '\n')
st = M.read_stand('b36_s0', x, None, dict(stable_s=50.0, hold_s=31.249))
check('s0: every sleep hit but the exit gap 249 ms -> stand FAIL (item 618 (b)(5))', not st['ok'] and st['exit'] == 249, st['members'])


def s1(lines, summ=SUM0, extra_head=()):
    body = ['LongFrame: n=1 dt_us=999999 log_async=1 t_ms=100'] if 'pre' in extra_head else []
    x = scan_text('st1_%d' % (abs(hash((tuple(lines), summ, extra_head))) % 1000000),
                  '\n'.join([MODE1, CFG1] + body + ['GuestOut: Level has started: ' + LV] +
                            [sleep(i, t, on='writer', role='other') for i, t in ((1, 160000), (2, 168000), (3, 176000))] + lines +
                            ([summ] if summ else [])) + '\n')
    return M.read_stand('b36_s1', x, None, ATT)


ST3 = [stall(2900000, 163000), stall(3000000, 171000), stall(3000100, 179000)]
st = s1(ST3 + [lf(9, 999999, 163000, 1)])
check('s1: stalls 2 900 000 x 3, LongFrame 999 999, full_waits 0 -> PASS', st['ok'], st['members'])
st = s1(ST3 + [lf(9, 1000000, 163000, 1)])
check('s1: LongFrame 1 000 000 -> FAIL', not st['ok'] and st['lf_ge1s'] == 1, st['members'])
st = s1(ST3[:2] + [stall(2899999, 179000)])
check('s1: third stall 2 899 999 -> only 2, FAIL', not st['ok'] and st['stall_ge29'] == 2, st['members'])
st = s1(ST3, summ=SUM0.replace('full_waits=0', 'full_waits=1'))
check('s1: full_waits 1 -> FAIL', not st['ok'] and st['full_waits'] == 1, st['members'])
st = s1(ST3, summ=None)
check('s1: no summary -> full_waits member fails', not st['ok'] and st['full_waits'] is None, st['members'])
x = scan_text('st1_before', '\n'.join([MODE1, CFG1, lf(1, 1500000, 100, 1), 'GuestOut: Level has started: ' + LV] +
                                      [sleep(i, t, on='writer', role='other') for i, t in ((1, 160000), (2, 168000), (3, 176000))] + ST3 +
                                      [SUM0]) + '\n')
st = M.read_stand('b36_s1', x, None, ATT)
check('s1: a LongFrame >= 1 s before the level line -> letter FAIL, executor variant counts 0 after the level line',
      not st['ok'] and st['lf_ge1s'] == 1 and st['lf_ge1s_after_level'] == 0, st)

# ---- f-stands and cold through read_tag (--dir form)
INST = M.BIN_FS9


def es_env(base):
    e = {}
    for k, v in M.expected_env(base).items():
        e[k] = v if v is not None else 'C:/x/' + k
    return e


def tag_dir(name, tag, log_text, env=None, binary=None, inst_b=INST, inst_a=INST, inst=None, mcmp='manifest cmp EQUAL files 9',
            scmp='manifest cmp EQUAL files 9', hold=None, att=None, vv=None, hlevel=None, seal_text='seal\ntheta_load: 0.4562\n',
            idx=None, glitch=None, sheet=None, stdout_text='', guest=None):
    base = M.base_of(tag)
    d = os.path.join(TMP, 'tg_' + name)
    os.makedirs(d, exist_ok=True)
    wfile(d, 'log.txt', log_text)
    wfile(d, 'seal.md', seal_text)
    wfile(d, 'stdout.txt', stdout_text)
    lv = M.level_of(base)
    kind = M.kind_of(base)
    vflag = vv if vv is not None else ('true' if base == 'b36_w' else 'false')
    js = dict(binary_sha256=M.BIN_T2 if binary is None else binary, prereg=dict(sha256=M.sha_file(os.path.join(d, 'seal.md'))),
              env=es_env(base) if env is None else env, cmdline=['x', '--vulkan-validation', vflag, '--shader-validation', 'false'],
              guest_args=guest or ('-lvl ' + lv),
              hold_s={'stand_user': 150, 'stand_harness': 150, 'cold': 330, 'v': 330, 'w': 310}[kind] if hold is None else hold,
              attempts=[att or dict(outcome='ok', hold_exit=None, hold_s=150.0 if kind.startswith('stand') else 331.0, stable_s=14.0)])
    with open(os.path.join(d, 'es.json'), 'w', encoding='ascii') as f:
        json.dump(js, f)
    for nm, v in (('installed_before', inst_b), ('installed_after', inst_a), ('installed_sha', M.BIN_T2 if inst is None else inst),
                  ('manifest_cmp', mcmp), ('snap_cmp', scmp), ('level', lv if hlevel is None else hlevel),
                  ('glitch', glitch), ('sheet', sheet)):
        if v is not None:
            wfile(d, nm + '.txt', v + '\n')
    if idx is not None:
        wfile(d, 'rec.idx', ''.join('%d\n' % i for i in range(idx)))
    return M.read_tag(tag, M.paths(tag, d))


def fails(r):
    return [a[0][:80] for a in r['admission'] if not a[1]]


# user form log
UF0 = '\n'.join(SEED_LINES[i].rstrip('\n') for i in range(2)) + '\n' + '\n'.join(
    [CFG0, 'LevelDocument Loaded: ' + LV, 'GuestOut: Level has started: ' + LV] + SL3 +
    [lf(1, 2600000, 162000), lf(2, 2600000, 170000), lf(3, 2600000, 178000)]) + '\n'
r = tag_dir('s0ok', 'b36_s0', UF0)
check('read_tag b36_s0: ADMITTED, stand PASS', r['admitted'] and r['stand']['ok'], (fails(r), r['stand'] and r['stand']['members']))
r = tag_dir('s0env', 'b36_s0', UF0, env=dict(es_env('b36_s0'), KYTY_FRAME_TRACE='lite'))
check('read_tag b36_s0: extra KYTY_FRAME_TRACE in env -> INTERFERENCE', not r['admitted'] and any('env' in a for a in fails(r)), fails(r))
e = es_env('b36_s0')
e.pop('KYTY_LONGFRAME', None)
r = tag_dir('s0envm', 'b36_s0', UF0, env=e)
check('read_tag b36_s0: missing KYTY_LONGFRAME -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0env2', 'b36_s0', UF0, env=dict(es_env('b36_s0'), KYTY_FIX_B36='1'))
check('read_tag b36_s0: KYTY_FIX_B36=1 value -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0ft', 'b36_s0', UF0 + 'FrameTrace: n=5 dt_us=33000 lat_us=1 draws=5\n')
check('read_tag b36_s0: a FrameTrace line in the user form -> INTERFERENCE', not r['admitted'] and any('user form' in a for a in fails(r)), fails(r))
r = tag_dir('s0hold', 'b36_s0', UF0, att=dict(outcome='ok', hold_exit=None, hold_s=119.9, stable_s=14.0))
check('read_tag b36_s0: hold_s 119.9 -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0hold2', 'b36_s0', UF0, att=dict(outcome='ok', hold_exit=None, hold_s=120.0, stable_s=14.0))
check('read_tag b36_s0: hold_s 120.0 edge -> ADMITTED', r['admitted'], fails(r))
r = tag_dir('s0death', 'b36_s0', UF0 + '--- Fatal Error ---\n')
check('read_tag b36_s0: death marker -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0dstd', 'b36_s0', UF0, stdout_text='Unhandled exception: x\n')
check('read_tag b36_s0: death marker in stdout -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0min', 'b36_s0', UF0 + 'Window 1 minimized\n')
check('read_tag b36_s0: window minimized -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0rec', 'b36_s0', UF0 + 'Recovering Vulkan swapchain\n')
check('read_tag b36_s0: Recovering Vulkan swapchain -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0gp', 'b36_s0', UF0 + 'GamePatch: loaded x\n')
check('read_tag b36_s0: GamePatch line -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0sig', 'b36_s0', UF0.replace('9177b4267de1fb8bac7d1113afd8733210addfac', '0' * 40))
check('read_tag b36_s0: other signature -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0bin', 'b36_s0', UF0, binary='45fff4a3d54194217e9d0eb46d0e3ed9b9cc1995571e0e537b564213cd0fdf75')
check('read_tag b36_s0: json binary T (45fff4a3) -> INTERFERENCE (item 616 (v))', not r['admitted'], fails(r))
r = tag_dir('s0inst', 'b36_s0', UF0, inst='45fff4a3d54194217e9d0eb46d0e3ed9b9cc1995571e0e537b564213cd0fdf75')
check('read_tag b36_s0: installed during the tag not T2 -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0ib', 'b36_s0', UF0, inst_b='b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a')
check('read_tag b36_s0: installed before S18 not FS9 -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0ia', 'b36_s0', UF0, inst_a='0' * 64)
check('read_tag b36_s0: installed after not FS9 -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0snap', 'b36_s0', UF0, scmp='manifest cmp DIFFER 3')
check('read_tag b36_s0: caches before not the snapshot -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0mc', 'b36_s0', UF0, mcmp='manifest cmp DIFFER 3')
check('read_tag b36_s0: caches not returned -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0vv', 'b36_s0', UF0, vv='true')
check('read_tag b36_s0: --vulkan-validation true -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0ho', 'b36_s0', UF0, hold=330)
check('read_tag b36_s0: hold option 330 -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0lv', 'b36_s0', UF0, hlevel=M.BONUS)
check('read_tag b36_s0: harness level differs -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('s0pre', 'b36_s0', UF0, seal_text='seal\ntheta_load: 0.4562\n')
check('read_tag b36_s0: prereg = seal (self) -> ADMITTED', r['admitted'], fails(r))
r = tag_dir('s0la', 'b36_s0', UF0 + MODE1 + '\n')
check('read_tag b36_s0: LogAsync line at =0 -> INTERFERENCE', not r['admitted'], r['interference'])
r = tag_dir('s0nost', 'b36_s0', UF0.replace(SL3[2] + '\n', ''))
check('read_tag b36_s0: two sleeps -> INTERFERENCE (stand)', not r['admitted'], fails(r))
r = tag_dir('s0ent', 'b36_s0', UF0, att=dict(outcome='timeout', hold_exit=None, hold_s=None, stable_s=None))
check('read_tag b36_s0: outcome timeout -> INTERFERENCE', not r['admitted'], fails(r))

UF1 = '\n'.join(SEED_LINES[i].rstrip('\n') for i in range(2)) + '\n' + '\n'.join(
    [MODE1, CFG1, 'GuestOut: Level has started: ' + LV] + [sleep(i, t, on='writer', role='other') for i, t in ((1, 160000), (2, 168000),
                                                                                                            (3, 176000))] + ST3 + [SUM0]) + '\n'
r = tag_dir('s1ok', 'b36_s1', UF1)
check('read_tag b36_s1: ADMITTED, stand PASS, S 3', r['admitted'] and r['stand']['ok'] and r['S'] == 3, (fails(r), r['stand']['members']))
r = tag_dir('s1nosum', 'b36_s1', UF1.replace(SUM0 + '\n', ''))
check('read_tag b36_s1: no summary -> INTERFERENCE run (item 615 (b)(6))', not r['admitted'] and r['interference'].startswith('run'), r['interference'])
r = tag_dir('s1nomode', 'b36_s1', UF1.replace(MODE1 + '\n', ''))
check('read_tag b36_s1: no mode=1 -> INTERFERENCE tag', not r['admitted'] and r['interference'].startswith('tag'), r['interference'])
r = tag_dir('s1rc3', 'b36_s1', UF1.replace('drain_timeouts=0', 'drain_timeouts=2'))
check('read_tag b36_s1: drain_timeouts 2 -> ADMITTED with the RC3 row', r['admitted'] and r['rc3'] and 'drain_timeouts 2' in r['rc3'], r.get('rc3'))
txt = '\n'.join(M.rows_out(r))
check('rows_out prints RC3, SLEEP rows with line= and the LongFramePrinter row', 'RC3 (item 616 (b)(4))' in txt and 'line="FrameTrace-lite x"' in txt
      and 'LONGFRAMEPRINTER (item 619 (b)(1))' in txt, txt[-600:])
r = tag_dir('s1abs', 'b36_s1', UF1.replace(' line="FrameTrace-lite x"', ''))
check('rows_out: line= absent printed <absent>', 'line="<absent>"' in '\n'.join(M.rows_out(r)))

# S count: 1 000 000 counted, 999 999 not, flush=1 counted and split
r = tag_dir('s1S', 'b36_s1', UF1.replace(SUM0, '\n'.join([stall(1000000, 1), stall(999999, 2), stall(1500000, 3, True), SUM0])))
check('S: us 1 000 000 counted, 999 999 not, flush=1 counted (S 5, flush 1)', r['S'] == 5 and r['S_flush'] == 1, (r['S'], r['S_flush']))

# harness forms: f0 / f1 / cold
LV_F = 1000 * 1000      # t_ms of frame n end = n x 33 ms base (fixture clock)


def flog(targets, after=None, before=None, fix='0', stalls=(), mode=True, summary=True, cfg=True, sleeps=None, level=LV, head=None,
         tail=None, nframes=9200):
    pre = [MODE] + ([MODE1] if fix == '1' else []) + ([CFG1 if fix == '1' else CFG0] if cfg else [])
    on = 'writer' if fix == '1' else 'caller'
    sl = sleeps if sleeps is not None else [sleep(i, t, on=on) for i, t in ((1, 160000), (2, 168000), (3, 176000))]
    tl = list(sl) + [stall(*s) for s in stalls] + (list(tail or [])) + ([SUM0] if (fix == '1' and summary) else [])
    return build(targets, before=before, after=after, level=level, pre=pre if mode else pre[1:], head=head, tail=tl, nframes=nframes)


# frame idx 5000 (n 5100) of 2.6 s; its LongFrame line t_ms 163000 (inside window 1)
TGT = {5000: dict(dt=2600000, diag=diag_block(FIRST + 5000, 2600000))}
AFT = {5001: [lf(FIRST + 5000, 2600000, 163000)]}
r = tag_dir('f0ok', 'b36_f0', flog(TGT, after=AFT))
check('read_tag b36_f0: ADMITTED, stand PASS (frame 2.6 s matched by its LongFrame t_ms)', r['admitted'] and r['stand']['ok'],
      (fails(r), r['stand'] and r['stand']['members']))
check('b36_f0: LongFrame / FrameTrace cross-check 1 pair, diff 0', r['stand']['lf_ft_cross'] == dict(pairs=1, max_abs_diff_us=0), r['stand']['lf_ft_cross'])
r = tag_dir('f0far', 'b36_f0', flog(TGT, after={5001: [lf(FIRST + 5000, 2600000, 150000)]}))
check('read_tag b36_f0: frame end outside every window -> stand FAIL', r['admitted'] and not r['stand']['ok'], r['stand']['per_sleep'])
TGT_FN = {5000: dict(dt=2600000, diag=diag_block(FIRST + 5000, 2600000, flip_ns=164000 * 10 ** 6))}
r = tag_dir('f0fns', 'b36_f0', flog(TGT_FN))
check('read_tag b36_f0: no LongFrame line -> end from flip_ns of window n (164 000 ms) -> PASS', r['stand']['ok'] and
      r['stand']['per_sleep'][0]['hits'][0][3] == 'flip_ns', r['stand']['per_sleep'])
TGT_LOW = {5000: dict(dt=2499999, diag=diag_block(FIRST + 5000, 2499999))}
r = tag_dir('f0low', 'b36_f0', flog(TGT_LOW, after={5001: [lf(FIRST + 5000, 2499999, 163000)]}))
check('read_tag b36_f0: frame 2 499 999 -> stand FAIL', not r['stand']['ok'], r['stand']['members'])
r = tag_dir('f1ok', 'b36_f1', flog({5000: dict(dt=999999, diag=diag_block(FIRST + 5000, 999999))}, fix='1', stalls=[(3000000, 163000)]))
check('read_tag b36_f1: ADMITTED, 0 scene frames >= 1 s (999 999) -> PASS', r['admitted'] and r['stand']['ok'], (fails(r), r['stand']['members']))
r = tag_dir('f1k2', 'b36_f1', flog({5000: dict(dt=1000000, diag=diag_block(FIRST + 5000, 1000000))}, fix='1'))
check('read_tag b36_f1: a scene frame 1 000 000 -> FAIL', r['admitted'] and not r['stand']['ok'], r['stand']['members'])
r = tag_dir('f1early', 'b36_f1', flog({3: dict(dt=1200000, diag=None)}, fix='1'))
check('read_tag b36_f1: a scene frame >= 1 s before 10 s of the scene also counts -> FAIL', not r['stand']['ok'] and r['stand']['scene_ge1s'] == 1,
      r['stand']['members'])
r = tag_dir('f1nosum', 'b36_f1', flog({}, fix='1', summary=False))
check('read_tag b36_f1: no summary -> INTERFERENCE run', not r['admitted'] and r['interference'].startswith('run'), r['interference'])
r = tag_dir('f0short', 'b36_f0', flog(TGT, after=AFT, nframes=3500))
check('read_tag b36_f0: scene 116.7 s < 120 -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('f0nomode', 'b36_f0', flog(TGT, after=AFT, mode=False))
check('read_tag b36_f0: no DiagB32 mode line -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('f0env', 'b36_f0', flog(TGT, after=AFT), env=dict(es_env('b36_f0'), KYTY_GPU_HANG_ABORT_S='8'))
check('read_tag b36_f0: KYTY_GPU_HANG_ABORT_S 8 -> INTERFERENCE', not r['admitted'], fails(r))

# cold: INSTR_POLL, POLL_UNKNOWN, INSTR_MADE_K2 first, stall overlap, admission
K2T = {5000: dict(dt=1500000, diag=diag_block(FIRST + 5000, 1500000, instr=1000))}
FHL = lambda poll, flip: 'FlipHold: us=%d present_us=10 poll_us=%d other_us=10 flip=%d' % (poll + 20, poll, flip)  # noqa: E731
r = tag_dir('k_cnt', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[]))
check('cold: a K2 frame -> K 1, in count 1, ADMITTED', r['admitted'] and r['log']['K'] == 1 and r['log']['in_count'] == 1, (fails(r), r['log']['K']))
r = tag_dir('k_poll', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], after={4999: [FHL(100000, FIRST + 4999)]}))
fr = [z for z in r['log']['frames'] if z['n'] == FIRST + 5000][0]
check('cold: FlipHold poll_us 100 000 after FrameTrace n-1 -> frame n INSTR_POLL, K 0, K_I 1', fr['instr_poll'] and fr['cls'] == 'INSTR_POLL'
      and r['log']['K'] == 0 and r['log']['K_I'] == 1 and r['log']['instr_poll_n'] == 1, (fr['cls'], r['log']['K'], r['log']['K_I']))
r = tag_dir('k_poll_early', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], after={4990: [FHL(500000, FIRST + 4990)]}))
check('cold: a FlipHold poll of an earlier interval does not reach a later frame -> in count', r['log']['K'] == 1 and r['log']['instr_poll_n'] == 0,
      (r['log']['K'], r['log']['instr_poll_n']))
r = tag_dir('k_poll_lt', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], after={4999: [FHL(99999, FIRST + 4999)]}))
check('cold: poll_us 99 999 -> in count', r['log']['K'] == 1 and r['log']['instr_poll_n'] == 0, r['log']['K'])
r = tag_dir('k_poll_late', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], after={5000: [FHL(500000, FIRST + 5000)]}))
check('cold: FlipHold after FrameTrace n maps to n + 1, frame n stays in count', r['log']['K'] == 1 and r['log']['instr_poll_n'] == 0,
      r['log']['K'])
cap = dict((i, [FHL(0, FIRST + i)]) for i in range(1, 33))
r = tag_dir('k_cap', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], after=cap))
fr = [z for z in r['log']['frames'] if z['n'] == FIRST + 5000][0]
check('cold: FlipHold cap 32 reached at flip 132 -> frame 5100 POLL_UNKNOWN, still in count', fr['poll_unknown'] and r['log']['K'] == 1 and
      r['log']['poll_unknown_n'] == 1 and r['log']['fliphold_cap_flip'] == FIRST + 32, (fr['poll_unknown'], r['log']['fliphold_cap_flip']))
cap31 = dict((i, [FHL(0, FIRST + i)]) for i in range(1, 32))
r = tag_dir('k_cap31', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], after=cap31))
check('cold: 31 FlipHold lines -> no POLL_UNKNOWN', r['log']['poll_unknown_n'] == 0 and r['log']['fliphold_cap_flip'] is None, r['log']['poll_unknown_n'])
cap_e = dict((i, [FHL(0, FIRST + i)]) for i in range(4968, 5000))
r = tag_dir('k_cap_e', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], after=cap_e))
check('cold: the 32nd FlipHold line at flip 5099 maps to frame 5100 -> poll known (0), not POLL_UNKNOWN', r['log']['fliphold_cap_flip'] ==
      FIRST + 4999 and r['log']['poll_unknown_n'] == 0 and r['log']['K'] == 1, (r['log']['fliphold_cap_flip'], r['log']['poll_unknown_n']))
cap_e2 = dict((i, [FHL(0, FIRST + i)]) for i in range(4967, 4999))
r = tag_dir('k_cap_e2', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], after=cap_e2))
check('cold: the 32nd FlipHold line at flip 5098 -> frame 5100 POLL_UNKNOWN', r['log']['fliphold_cap_flip'] == FIRST + 4998 and
      r['log']['poll_unknown_n'] == 1, (r['log']['fliphold_cap_flip'], r['log']['poll_unknown_n']))
r = tag_dir('k_poll_max', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], after={4999: [FHL(150000, FIRST + 4999), FHL(0, FIRST + 4999)]}))
check('cold: two FlipHold lines in one interval -> the max poll_us (150 000) -> INSTR_POLL', r['log']['instr_poll_n'] == 1 and r['log']['K'] == 0,
      r['log']['instr_poll_n'])
K2I = {5000: dict(dt=1500000, diag=diag_block(FIRST + 5000, 1500000, instr=600000))}
r = tag_dir('k_imk', 'b36_k01', flog(K2I, fix='1', cfg=False, sleeps=[], after={4999: [FHL(200000, FIRST + 4999)]}))
fr = [z for z in r['log']['frames'] if z['n'] == FIRST + 5000][0]
check('cold: INSTR_MADE_K2 keeps its class before INSTR_POLL', fr['instr_made_k2'] and not fr['instr_poll'] and r['log']['instr_poll_n'] == 0,
      (fr['instr_made_k2'], fr['instr_poll']))
# stall overlap: frame end = flip_ns of window n = 10^12 + n x 10^6 ns -> 10^6 + n ms; frame n 5100 ends 1 005 100 ms, starts 1 003 600
END = 10 ** 6 + FIRST + 5000
r = tag_dir('k_ov', 'b36_k01', flog(K2T, fix='1', cfg=False, sleeps=[], stalls=[(1000000, END - 1500), (1000000, END - 1501),
                                                                                 (1000000, END + 1000), (1000000, END + 1001), (200000, END)]))
fr = [z for z in r['log']['frames'] if z['n'] == FIRST + 5000][0]
check('cold: stall overlap edges - ends at the frame start (in), 1 ms before (out), starts at the frame end (in), 1 ms after (out), inside',
      fr['stall_overlap'] == [(1000000, END - 1500), (1000000, END + 1000), (200000, END)], fr['stall_overlap'])
check('cold: S counts 4 stall lines >= 1 s', r['S'] == 4, r['S'])
r = tag_dir('k_bon', 'b36_k02', flog({}, fix='1', cfg=False, sleeps=[], level=M.BONUS))
check('cold b36_k02 is bonus, ADMITTED', r['admitted'] and r['level'] == M.BONUS, fails(r))
r = tag_dir('k_lvl', 'b36_k02', flog({}, fix='1', cfg=False, sleeps=[]), guest='-lvl ' + M.POT)
check('cold b36_k02 run on pot -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('k_stand', 'b36_k03', flog({}, fix='1'))
check('cold: TestLogStall lines in a cold tag -> INTERFERENCE', not r['admitted'], fails(r))
r = tag_dir('k_abort', 'b36_k05', flog({}, fix='1', cfg=False, sleeps=[], tail=['GpuHangAbort: x', '--- Error ---']))
check('cold: GpuHangAbort after 10 s then --- Error --- -> ADMITTED, K 1 (NO_SAMPLES:abort)', r['admitted'] and r['log']['K'] == 1 and
      r['log']['hold_class'] == 'NO_SAMPLES:abort', (fails(r), r['log']['hold_class']))
r = tag_dir('k_fatal', 'b36_k05', flog({}, fix='1', cfg=False, sleeps=[], tail=['--- Fatal Error ---']))
check('cold: --- Fatal Error --- -> INTERFERENCE', not r['admitted'], fails(r))

# ---- no harm v / w
B13 = 'FixB13: mode=1 x'
DUAL = 'DualSrcBlend: supported=1 enabled=1'


def vlog(targets=None, nframes=9200, head=(B13,), draws=4000):
    return build(targets or {}, nframes=nframes, level=M.SKY, head=[h + '\n' for h in head], pre=[MODE1], draws=draws, tail=[SUM0])


ATT_V = dict(outcome='ok', hold_exit=None, hold_s=330.0, stable_s=20.0)
r = tag_dir('v_ok', 'b36_v', vlog(), idx=3000, glitch='one-frame glitches: 0', sheet='sheet ok', att=ATT_V)
check('b36_v: ADMITTED, no harm PASS (index 3000 edge, hold 306.6 s)', r['admitted'] and r['vw']['ok'], (fails(r), r['vw']['members']))
r = tag_dir('v_idx', 'b36_v', vlog(), idx=2999, glitch='one-frame glitches: 0', sheet='sheet ok', att=ATT_V)
check('b36_v: index 2999 -> FAIL', not r['vw']['ok'], r['vw']['members'])
r = tag_dir('v_gl', 'b36_v', vlog(), idx=3000, glitch='one-frame glitches: 1', sheet='sheet ok', att=ATT_V)
check('b36_v: 1 glitch -> FAIL', not r['vw']['ok'])
r = tag_dir('v_sheet', 'b36_v', vlog(), idx=3000, glitch='one-frame glitches: 0', att=ATT_V)
check('b36_v: no sheet -> FAIL', not r['vw']['ok'])
r = tag_dir('v_k2', 'b36_v', vlog({4000: dict(dt=1000000)}), idx=3000, glitch='one-frame glitches: 0', sheet='s', att=ATT_V)
check('b36_v: a frame 1 000 000 after the first scene frame -> FAIL', not r['vw']['ok'] and r['vw']['info']['frames_ge1s'] == 1, r['vw']['info'])
r = tag_dir('v_k2lt', 'b36_v', vlog({4000: dict(dt=999999)}), idx=3000, glitch='one-frame glitches: 0', sheet='s', att=ATT_V)
check('b36_v: a frame 999 999 -> PASS', r['vw']['ok'], r['vw']['members'])
r = tag_dir('v_hold', 'b36_v', vlog(nframes=9000), idx=3000, glitch='one-frame glitches: 0', sheet='s', att=ATT_V)
check('b36_v: hold 299.997 s < 300 -> FAIL', not r['vw']['ok'], r['vw']['info'])
r = tag_dir('v_hold2', 'b36_v', vlog(nframes=9001), idx=3000, glitch='one-frame glitches: 0', sheet='s', att=ATT_V)
check('b36_v: hold 300.030 s >= 300 -> PASS', r['vw']['ok'], r['vw']['info'])
r = tag_dir('v_b13', 'b36_v', vlog(head=()), idx=3000, glitch='one-frame glitches: 0', sheet='s', att=ATT_V)
check('b36_v: no FixB13 line -> FAIL', not r['vw']['ok'])
r = tag_dir('v_exit', 'b36_v', vlog(), idx=3000, glitch='one-frame glitches: 0', sheet='s', att=dict(ATT_V, hold_exit=3221225477))
check('b36_v: ended inside the hold -> FAIL', not r['vw']['ok'])
r = tag_dir('v_draws', 'b36_v', vlog(draws=50), idx=3000, glitch='one-frame glitches: 0', sheet='s', att=ATT_V)
check('b36_v: no frame with draws >= 100 -> first scene frame None -> FAIL', not r['vw']['ok'] and r['vw']['info']['first_scene_n'] is None,
      r['vw']['info'])
r = tag_dir('v_draws100', 'b36_v', vlog(draws=100), idx=3000, glitch='one-frame glitches: 0', sheet='s', att=ATT_V)
check('b36_v: draws 100 edge -> first scene frame found, PASS', r['vw']['ok'] and r['vw']['info']['first_scene_n'] == FIRST, r['vw']['info'])
r = tag_dir('v_b13late', 'b36_v', vlog(head=()) + B13 + '\n', idx=3000, glitch='one-frame glitches: 0', sheet='s', att=ATT_V)
check('b36_v: FixB13 only after the first GuestOut -> FAIL', not r['vw']['ok'])
ATT_W = dict(outcome='ok', hold_exit=None, hold_s=310.0, stable_s=30.0)
WL = vlog(head=(B13, DUAL, '[Vulkan][W] w1'))
r = tag_dir('w_ok', 'b36_w', WL, att=ATT_W)
check('b36_w: ADMITTED, no harm PASS', r['admitted'] and r['vw']['ok'], (fails(r), r['vw']['members']))
r = tag_dir('w_e', 'b36_w', WL + '[Vulkan][E] e\n', att=ATT_W)
check('b36_w: one [Vulkan][E] -> FAIL', not r['vw']['ok'])
r = tag_dir('w_lim', 'b36_w', WL + 'this will be the last time reporting it\n', att=ATT_W)
check('b36_w: a limit line -> FAIL', not r['vw']['ok'])
r = tag_dir('w_now', 'b36_w', vlog(head=(B13, DUAL)), att=ATT_W)
check('b36_w: no [Vulkan][W] -> positive control FAIL', not r['vw']['ok'])
r = tag_dir('w_dual', 'b36_w', vlog(head=(B13, '[Vulkan][W] w')) + DUAL + '\n', att=ATT_W)
check('b36_w: DualSrcBlend after the first GuestOut -> FAIL', not r['vw']['ok'])
r = tag_dir('w_hold', 'b36_w', WL, att=dict(ATT_W, hold_s=309.9))
check('b36_w: hold_s 309.9 -> FAIL', not r['vw']['ok'])
r = tag_dir('w_vv', 'b36_w', WL, att=ATT_W, vv='false')
check('b36_w: --vulkan-validation false -> INTERFERENCE', not r['admitted'], fails(r))
e = es_env('b36_w')
e['VK_LAYER_MESSAGE_ID_FILTER'] = 'x'
r = tag_dir('w_filter', 'b36_w', WL, att=ATT_W, env=e)
check('b36_w: VK_LAYER_MESSAGE_ID_FILTER in env -> INTERFERENCE', not r['admitted'], fails(r))

# ---- expected env shapes
check('env s0: guest args, longframe, stand, fix 0 only', M.expected_env('b36_s0') == dict(
    KYTY_GUEST_ARGS='-lvl ' + M.POT, KYTY_FIX_B36='0', KYTY_LONGFRAME='1', KYTY_TEST_LOGSTALL='60:3000:3'), M.expected_env('b36_s0'))
check('env k: harness + DIAG_B32 1 + FIX_B36 1 + HANG_ABORT 22, no stand, no longframe',
      M.expected_env('b36_k13')['KYTY_FIX_B36'] == '1' and M.expected_env('b36_k13')['KYTY_GPU_HANG_ABORT_S'] == '22' and
      'KYTY_LONGFRAME' not in M.expected_env('b36_k13') and 'KYTY_TEST_LOGSTALL' not in M.expected_env('b36_k13') and
      M.expected_env('b36_k13')['KYTY_DIAG_B32'] == '1', M.expected_env('b36_k13'))
check('levels: pot k01 k03 k05 k07 k09 k11 k12 k13, bonus k02 k04 k06 k08 k10 (8 + 5)',
      [M.level_of('b36_k%02d' % i) for i in range(1, 14)].count(M.POT) == 8 and
      [M.level_of('b36_k%02d' % i) for i in range(1, 14)].count(M.BONUS) == 5 and M.level_of('b36_k12') == M.POT, None)
check('tag names: repeats _r1.._r3 accepted, _r4 and b36_k14 refused', M.TAG_RX.match('b36_k13_r3') and not M.TAG_RX.match('b36_k13_r4')
      and not M.TAG_RX.match('b36_k14') and not M.TAG_RX.match('b36_s2'))

# ---- table / series
RUNS = os.path.join(TMP, 'runs')
for nm, tag in (('s0ok', 'b36_s0'), ('s1ok', 'b36_s1'), ('f0ok', 'b36_f0'), ('f1k2', 'b36_f1'), ('k_cnt', 'b36_k01'), ('k_poll', 'b36_k03'),
                ('k_bon', 'b36_k02'), ('v_ok', 'b36_v'), ('w_e', 'b36_w'), ('s0env', 'b36_s0_r1')):
    os.makedirs(os.path.join(RUNS, tag), exist_ok=True)
    d = os.path.join(TMP, 'tg_' + nm)
    res = M.read_tag(tag, M.paths(tag, d))
    with open(os.path.join(RUNS, tag, 'read.json'), 'w', encoding='ascii') as f:
        json.dump(res, f, default=list)
sr = '\n'.join(M.series(RUNS))
check('series: stands, cold K by level (pot K 1 of 2 tags read, bonus K 0), no harm, interference row',
      'STAND b36_s0 PASS' in sr and 'STAND b36_f1 FAIL' in sr and 'COLD pot_treasure_cave admitted 2 of 8: K 1' in sr and
      'COLD bonus_path_maker_mix admitted 1 of 5: K 0' in sr and 'NO HARM b36_v PASS' in sr and 'NO HARM b36_w FAIL' in sr and
      'INTERFERENCE 1' in sr, sr)
tb = '\n'.join(M.table(RUNS))
check('table: one row per read tag + 2 header rows', len(tb.splitlines()) == 12 and '| b36_k03 |' in tb, tb[:300])

# ---- f25_read sha guard and strict cp1250 ASCII output
check('F25_SHA pinned = sha256 of f25_read.py', M.F25_SHA == M.sha_file(R.__file__), (M.F25_SHA, M.sha_file(R.__file__)))
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
env['PYTHONUTF8'] = '0'
code = ('import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="cp1250", errors="strict"); sys.argv = ["f25m_read.py", '
        '"--dir", sys.argv[1], "--tag", "b36_s1"]; import runpy; runpy.run_path(sys.argv[0] if False else %r, run_name="__main__")'
        % os.path.join(HERE, 'f25m_read.py'))
p = subprocess.run([sys.executable, '-c', code, os.path.join(TMP, 'tg_s1rc3')], capture_output=True, env=env)
check('reader output in strict cp1250 without PYTHONIOENCODING: rc 0, ASCII', p.returncode == 0 and all(b < 128 for b in p.stdout),
      (p.returncode, p.stderr[-300:]))
code2 = code.replace('"b36_s1"', '"b36_k01"')
p = subprocess.run([sys.executable, '-c', code2, os.path.join(TMP, 'tg_k_poll')], capture_output=True, env=env)
check('reader output (cold) in strict cp1250: rc 0, ASCII', p.returncode == 0 and all(b < 128 for b in p.stdout), (p.returncode, p.stderr[-300:]))
p = subprocess.run([sys.executable, os.path.join(HERE, 'f25m_read.py'), '--series', '--runs', RUNS], capture_output=True, env=env)
check('series output ASCII, rc 0', p.returncode == 0 and all(b < 128 for b in p.stdout), p.stderr[-200:])
# sha guard: a reader copy with a wrong pin refuses
gd = os.path.join(TMP, 'guard')
os.makedirs(gd, exist_ok=True)
for fn in ('f25_read.py', 'f20e_read.py'):
    shutil.copy2(os.path.join(HERE, fn), os.path.join(gd, fn))
src = open(os.path.join(HERE, 'f25m_read.py'), 'rb').read().replace(M.F25_SHA.encode(), b'0' * 64)
open(os.path.join(gd, 'f25m_read.py'), 'wb').write(src)
p = subprocess.run([sys.executable, os.path.join(gd, 'f25m_read.py'), 'b36_s0'], capture_output=True, env=env)
check('sha guard: a wrong pin of f25_read.py -> refused, rc 1', p.returncode == 1 and b'refused' in p.stdout, (p.returncode, p.stdout[-200:]))

print('checks %d' % nchk)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
