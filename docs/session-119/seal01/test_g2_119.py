"""Session 119: fixtures for g2_119.py (the G2 re-measure of route A at W = 2, pred/01_g2_119.md) on SYNTHETIC logs
generated here, derived from the session-104 suite test_a104.py.
    python test_g2_119.py <g2_119.py> [--real]
A reference pair (one mut119 run, one sh119 run) must be ADMITTED under a temporary seal and give a G2 that the
independent recount here (no scorer code; constants typed from ROADMAP 118 item 6 / 119 item 1) reproduces; the spine
takes max(proxy, 959) from the MUT run; f2 = 0.555; one shadow worker; every control and arming check then gets a
mutation that must make it fail.  --real adds the real logs (dab102a: the ABBA machinery equals dab102.py; obs116: the
installed binary d3a981a2 prints every field where the scorer expects it) - run once at the seal, not under mutlib.
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import shutil
import statistics
import sys

sys.dont_write_bytecode = True
SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s119/fx_g2_119')
spec = importlib.util.spec_from_file_location('g2_119', SRC)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)

PERIOD, START = 90, 1800
ARM_OF = lambda b: (0, 1, 1, 0)[b % 4]
GATES_TEXT = ' '.join(Path('C:/kyty/s119/gates_base.txt').read_text(encoding='utf-8').split())
RESULTS = []

SEAL = BASE / 'seal_01.md'
SEAL.write_bytes(b'test seal for g2_119.py\n')
S.PRED = str(SEAL)
S.PRED_SHA = hashlib.sha256(SEAL.read_bytes()).hexdigest()
S.PRED_BYTES = len(SEAL.read_bytes())

# constants typed from ROADMAP 118 item 6 / 119 item 1, NOT read from the scorer (independent recount)
F, BAR, C_TS, W_E, SPINE_DIRECT = 0.555, 3000.0, 3.96, 675.455 + 440.120, 959.0
BUILD = 'd3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64'
MUT_ARMS = ('mutwide=0 mutsite=1 amut=1 plkstat=1 pathlap=1', 'mutwide=15 mutsite=1 amut=1 plkstat=1 pathlap=1')
SH_ARMS = ('shadowresolve=0 shadowmask=3', 'shadowresolve=1 shadowmask=3')
ARMS = {'mut': MUT_ARMS, 'sh': SH_ARMS}
SCHED = {k: '90+1800:%s|%s' % v for k, v in ARMS.items()}


def check(name, cond, detail=''):
    RESULTS.append((name, bool(cond), '' if cond else str(detail)[:300]))


MUT = {'P': 150.0, 'S0': 13400, 'S1': 20500}
SH = {'T4': 1300.0, 'T4dt': 1350.0, 'push': 480}
EM = {'pl_em_vtx_ns': 1300000, 'pl_em_rt_ns': 1500000, 'pl_em_pipe_ns': 750000,
      'pl_em_com_ns': 2250000, 'pl_em_rec_ns': 1220000, 'pl_em_rest_ns': 72000}


def generate(kind, n_pairs=32, seed=1, mod=None, P=None, T4=None, T4dt=None, area=2000, walk=2600, queue=1300):
    quartets = (n_pairs + 1) // 2
    nblocks = 4 + 4 * quartets
    last = START + PERIOD * nblocks + 5
    pre_dt = int((S.HOLD_S + 20) * 1e6 / 1800)
    rng = random.Random(seed)
    P = MUT['P'] if P is None else P
    T4 = SH['T4'] if T4 is None else T4
    T4dt = SH['T4dt'] if T4dt is None else T4dt
    rows = {}
    for n in range(2, last + 1):
        if n <= START:
            arm, blk, idx = 0, 0, None
        else:
            blk = (n - START - 1) // PERIOD
            arm, idx = ARM_OF(blk), (n - START - 1) % PERIOD
        draws = int(5000 + 8 * math.sin(n / 41.0)) + rng.randint(-5, 5)
        att = 12000 + rng.randint(-5, 5)
        d = {'dt_us': (32500 + rng.randint(-300, 300)) if n > START else pre_dt,
             'draws': draws, 'dispatches': 268, 'gpu_busy_us': 12700 + rng.randint(-300, 300),
             'arm': arm, 'blk': blk, 'spin_gpu_us': rng.randint(0, 3),
             'rec_n': 10800 + rng.randint(-200, 200), 'bda_n': 176, 'da_walks': 5,
             'da_walk_us': walk + rng.randint(-20, 20), 'da_queue_us': queue + rng.randint(-8, 8),
             'da_take_us': 2400 + rng.randint(-50, 50), 'da_hit': 8500 + rng.randint(-30, 30),
             'da_miss': 73 + rng.randint(-3, 3), 'da_late': 0,
             'rt_att': att, 'rt_kpx': att * area + rng.randint(-50, 50),
             'bf_n': 0, 'bf_disp': 0, 'bf_skip': 0, 'bf_clr_skip': 0, 'bf_skip_drop': 0,
             'gm_ops': 0, 'da_wjobs': 8, 'da_wskip': 8, 'da_wdrop': 0}
        zero_mut = {k: 0 for k in ('mw_n', 'a_mut_us', 'a_mut_n', 'a_hold_us', 'a_hold_n',
                                   'a_wait_us', 'mh_n', 'mh_draws', 'mh_disp_n', 'mh_pro_us',
                                   'mh_rt_us', 'mh_prog_us', 'mh_bind_us', 'mh_emit_us',
                                   'mh_tail_us', 'mh_disp_us', 'pl_prog_wait_us',
                                   'pl_prog_hold_us', 'pl_prog_n', 'pl_pipe_wait_us',
                                   'pl_pipe_hold_us', 'pl_pipe_n', 'pl_cs_wait_us',
                                   'pl_cs_hold_us', 'pl_cs_n', 'pl_em_n', 'pl_proc_ns',
                                   'pl_proc_n', 'pl_pref_ns', 'pl_pref_n')}
        zero_mut.update({k: 0 for k in EM})
        zero_sh = {k: 0 for k in ('sh_jobs', 'sh_drop', 'sh_over', 'sh_us', 'sh_push_us',
                                  'sh_lock_us', 'sh_trk_us', 'sh_wake', 'sh_img', 'sh_buf')}
        d.update(zero_mut)
        d.update(zero_sh)
        if kind == 'mut':
            d['cpu_gpu_us'] = int(round(31700 + (P if arm else 0) + rng.gauss(0, 300)))
            d.update(mh_n=draws, mh_draws=draws, mh_disp_n=268, a_hold_n=draws + 268,
                     a_hold_us=26500 + rng.randint(-200, 200), a_wait_us=150,
                     a_mut_us=(MUT['S1'] if arm else MUT['S0']) + rng.randint(-100, 100),
                     a_mut_n=70000 if arm else 61000,
                     mw_n=(2 * draws + 268 + 176) if arm else 0,
                     mh_pro_us=600, mh_rt_us=870, mh_prog_us=5900, mh_bind_us=11000,
                     mh_emit_us=7200, mh_tail_us=300, mh_disp_us=2200,
                     pl_prog_wait_us=40, pl_prog_hold_us=4100, pl_prog_n=draws,
                     pl_pipe_wait_us=45, pl_pipe_hold_us=650, pl_pipe_n=draws,
                     pl_cs_wait_us=2, pl_cs_hold_us=237, pl_cs_n=268, pl_em_n=draws,
                     pl_proc_ns=31000000, pl_proc_n=13, pl_pref_ns=1000, pl_pref_n=8)
            d.update(EM)
        else:
            d['cpu_gpu_us'] = int(round(30500 + (T4 if arm else 0) + rng.gauss(0, 300)))
            if n > START:
                d['dt_us'] = 31100 + (int(T4dt) if arm else 0) + rng.randint(-300, 300)
            if arm:
                d.update(sh_jobs=int(round(0.99 * draws)), sh_drop=0, sh_over=1, sh_us=4000,
                         sh_push_us=SH['push'], sh_lock_us=100, sh_trk_us=160, sh_wake=80,
                         sh_img=44000, sh_buf=43000)
        if mod is not None:
            mod(n, arm, blk, idx, d)
        rows[n] = d
    return rows, nblocks


MAIN_KEYS = [k for k, v in S.EXPECTED_LINE.items() if v == 'main']
DRAW_KEYS = [k for k, v in S.EXPECTED_LINE.items() if v == 'draw']
X_KEYS = [k for k, v in S.EXPECTED_LINE.items() if v == 'x']
HEADER = ['GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)',
          'RecordThread: started recorder=0x1000695f2c0 arena=65536KiB gpu=0',
          'RecordThread: started recorder=0x100c7e97ac0 arena=65536KiB gpu=1']
SH_HEADER = HEADER + ['ShadowResolve: worker 0 started']


def write_run(root, tag, kind, rows, header=None, extra_log=(), extra_stdout=(), env_over=None,
              env_drop=(), meta_over=None, line_hook=None, gate_hook=None):
    root.mkdir(parents=True, exist_ok=True)
    texts = ARMS[kind]
    lines = list((SH_HEADER if kind == 'sh' else HEADER) if header is None else header)
    lines += list(extra_log)
    for n in sorted(rows):
        d = rows[n]
        if n > START and (n - START - 1) % PERIOD == 0:
            blk = (n - START - 1) // PERIOD
            g = 'GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s' % (
                ARM_OF(blk), blk, START + PERIOD * blk, texts[ARM_OF(blk)])
            if gate_hook is not None:
                g = gate_hook(blk, g)
            if g is not None:
                lines.append(g)
        main = 'FrameTrace: n=%d lat_us=1 ' % n + ' '.join('%s=%d' % (k, d[k]) for k in MAIN_KEYS
                                                           if k in d) + ' rt_w=3840 rt_h=2160'
        draw = 'FrameTrace-draw: n=%d ' % n + ' '.join('%s=%d' % (k, d[k]) for k in DRAW_KEYS if k in d)
        x = 'FrameTrace-x: n=%d prot_spin_gpu_us=153 bda_walk_us=9 ' % n + ' '.join(
            '%s=%d' % (k, d[k]) for k in X_KEYS if k in d)
        group = [main, draw, 'FrameTrace-rp: n=%d ends=182' % n, x]
        if line_hook is not None:
            group = line_hook(n, group)
        lines.extend(group)
    (root / ('log_%s.txt' % tag)).write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    (root / ('stdout_%s.txt' % tag)).write_bytes(('\n'.join(['emulator stdout'] + list(extra_stdout))
                                                  + '\n').encode('utf-8'))
    sched = SCHED[kind]
    env = {'VK_SDK_PATH': 'C:\\VulkanSDK', 'KYTY_FRAME_TRACE': 'lite',
           'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s119\\gates.req',
           'KYTY_SAMPLE_GATE': 'C:\\kyty\\s119\\sample.req', 'KYTY_QUEUE_TRACE': '1',
           'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_GATE_SCHEDULE': sched,
           'KYTY_GATE_SCHEDULE_ABBA': '1', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
    env.update(env_over or {})
    for k in env_drop:
        env.pop(k, None)
    meta = {'tag': tag, 'binary_sha256': BUILD, 'env': env, 'schedule': sched,
            'gates': GATES_TEXT, 'prereg': {'sha256': S.PRED_SHA, 'bytes': S.PRED_BYTES},
            'attempts': [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None,
                          'hold_s': 300.3, 'stable_frame': 300}],
            'hold_s': 300}
    meta.update(meta_over or {})
    (root / ('%s.json' % tag)).write_bytes(json.dumps(meta, indent=1).encode('utf-8'))


COUNTER = [0]


def run_one(kind, gen=None, write=None, draft=False):
    COUNTER[0] += 1
    root = BASE / ('r%03d' % COUNTER[0])
    tag = {'mut': 'mut119', 'sh': 'sh119'}[kind]
    rows, _ = generate(kind, **(gen or {}))
    write_run(root, tag, kind, rows, **(write or {}))
    return S.evaluate_run(str(root), tag, kind, draft=draft, gates_file='C:/kyty/s119/gates_base.txt'), rows


def run_pair(mut_gen=None, sh_gen=None, draft=False):
    COUNTER[0] += 1
    root = BASE / ('p%03d' % COUNTER[0])
    rm, _ = generate('mut', **(mut_gen or {}))
    rs, _ = generate('sh', **(sh_gen or {}))
    write_run(root, 'mut119', 'mut', rm)
    write_run(root, 'sh119', 'sh', rs)
    return S.evaluate(str(root), 'mut119', 'sh119', draft=draft,
                      gates_file='C:/kyty/s119/gates_base.txt'), rm, rs


# ------------------------------------------------------------------ independent recount
def recount(rows):
    blocks, b = {}, 0
    while True:
        ns = list(range(START + 1 + PERIOD * b, START + 1 + PERIOD * (b + 1)))
        if not all(n in rows for n in ns):
            break
        blocks[b] = ns[60:89]
        b += 1
    usable = {k: v for k, v in blocks.items() if v[0] >= 2100}
    pairs = []
    for q in range(0, max(blocks) + 1, 4):
        if all(k in usable for k in range(q, q + 4)):
            pairs += [(q, q + 1), (q + 2, q + 3)]
    mean = lambda ns, f: sum(f(rows[n]) for n in ns) / len(ns)
    used = sorted({b for p in pairs for b in p})
    lev = lambda arm, f: statistics.median(mean(usable[b], f) for b in used if ARM_OF(b) == arm)
    d = lambda f: [mean(usable[r if ARM_OF(r) == 1 else l], f) - mean(usable[l if ARM_OF(l) == 0 else r], f)
                   for l, r in pairs]
    return lev, d, len(pairs)


def recount_g(rm, rs):
    lm, dm, _ = recount(rm)
    ls, ds, _ = recount(rs)
    cn = lambda x: x['cpu_gpu_us'] - x['spin_gpu_us']
    cpu_net = ls(0, cn)
    s_raw = lm(1, lambda x: x['a_mut_us'])
    dp = dm(cn)
    p = statistics.fmean(dp)
    p2 = 2 * statistics.stdev(dp) / math.sqrt(len(dp))
    t_in = lm(1, lambda x: 5 * x['pl_em_n'] + 3 * (x['pl_prog_n'] + x['pl_pipe_n'] + x['pl_cs_n']) + x['a_mut_n'])
    di = C_TS * t_in / 1000.0
    rec = lm(1, lambda x: x['pl_em_rec_ns'] / 1000.0)
    com = lm(1, lambda x: x['pl_em_com_ns'] / 1000.0)
    proxy = lm(0, lambda x: x['da_walk_us'] - x['da_queue_us'])
    spine = max(proxy, SPINE_DIRECT)
    dt4 = ds(cn)
    t4 = statistics.fmean(dt4)
    t42 = 2 * statistics.stdev(dt4) / math.sqrt(len(dt4))
    push = ls(1, lambda x: x['sh_push_us'])
    s_ctx = s_raw - max(p, 0) - di - (rec + W_E)
    s_ctx_h = s_raw - max(p + p2, 0) - 2 * di - (rec + com)
    t4h = max(0.0, t4 - t42 - push)
    g = cpu_net - (s_ctx + F * (cpu_net - s_ctx)) - spine - t4
    gh = cpu_net - (s_ctx_h + F * (cpu_net - s_ctx_h)) - spine - t4h
    return {'cpu_net': cpu_net, 'S_raw': s_raw, 'P': p, 'G': g, 'G_ceiling': gh, 'T4': t4,
            'spine': spine, 'proxy': proxy, 'kill': (1 - F) * (cpu_net - s_ctx) - spine - BAR}


def failed(out, name):
    return name in out['failed_controls']


def arming_failed(out, name):
    return not ((out.get('arming') or {}).get('checks') or {}).get(name, True)


# ------------------------------------------------------------ the reference pair
out, rm, rs = run_pair()
mut, sh = out['mut'], out['sh']
check('reference mut119 ADMITTED', mut['status'] == 'ADMITTED', mut['failed_controls'])
check('reference sh119 ADMITTED', sh['status'] == 'ADMITTED', sh['failed_controls'])
check('reference pairs 32', mut['selection']['pairs'] == 32 and sh['selection']['pairs'] == 32,
      (mut['selection'], sh['selection']))
rc = recount_g(rm, rs)
g = out['G']
check('G2 central equals the independent recount', abs(g['central']['G'] - rc['G']) < 1e-6,
      (g['central']['G'], rc['G']))
check('G2 ceiling equals the independent recount', abs(g['ceiling']['G'] - rc['G_ceiling']) < 1e-6,
      (g['ceiling']['G'], rc['G_ceiling']))
check('cpu_net / S_raw / P / T2 / spine recounted',
      all(abs(a - b) < 1e-6 for a, b in ((g['terms']['cpu_net'], rc['cpu_net']), (g['terms']['S_raw'], rc['S_raw']),
                                         (g['terms']['P_mw'], rc['P']), (g['terms']['T4'], rc['T4']),
                                         (g['terms']['spine'], rc['spine']))), rc)
check('reference spine is the mut proxy (1 300 > 959)', abs(rc['spine'] - rc['proxy']) < 1e-9 and rc['proxy'] > 959)
check('kill T2 equals the recount', abs(g['kill_T4_central_us'] - rc['kill']) < 1e-6, (g['kill_T4_central_us'], rc['kill']))
check('ceiling >= central (every term A-favourable)', g['ceiling']['G'] >= g['central']['G'])
check('reference verdict follows the recount',
      out['verdict']['verdict'] == ('A_CLOSED_FOR_MAX_FPS' if rc['G'] < BAR else 'A_PROCEEDS_BY_STAGES'),
      (out['verdict'], rc['G']))
check('predictions scored', len(out['predictions']) >= 15)
check('f and bar reported', g['F'] == 0.555 and g['bar_us'] == 3000.0, (g['F'], g['bar_us']))

# the spine floor: a mut proxy below 959 gives spine 959
o2, rm2, rs2 = run_pair(mut_gen={'walk': 2000, 'queue': 1300})
rc2 = recount_g(rm2, rs2)
check('proxy 700 -> spine 959', abs(o2['G']['terms']['spine'] - 959.0) < 1e-9 and rc2['proxy'] < 959,
      (o2['G']['terms']['spine'], rc2['proxy']))
check('proxy 700: G2 equals the recount', abs(o2['G']['central']['G'] - rc2['G']) < 1e-6)
# the sh run's walk does not enter the spine
o2b, rm2b, rs2b = run_pair(sh_gen={'walk': 9000, 'queue': 1000})
check('the sh run walk does not enter the spine', abs(o2b['G']['terms']['spine'] - recount_g(rm2b, rs2b)['spine']) < 1e-9
      and o2b['G']['terms']['spine'] < 2000, o2b['G']['terms'])

# the bar on the arithmetic: exactly at and just below 3000
for delta, want in ((0.0, 'A_PROCEEDS_BY_STAGES'), (-0.001, 'A_CLOSED_FOR_MAX_FPS')):
    fake = json.loads(json.dumps(g))
    fake['central']['G'] = BAR + delta
    v = S.verdict(fake, mut, sh)['verdict']
    check('bar %.3f -> %s' % (BAR + delta, want), v == want, v)
# the ceiling decides nothing: central below the bar, ceiling far above -> closed
fake = json.loads(json.dumps(g))
fake['central']['G'] = 2999.0
fake['ceiling']['G'] = 9000.0
check('the ceiling decides nothing', S.verdict(fake, mut, sh)['verdict'] == 'A_CLOSED_FOR_MAX_FPS')

# a tax large enough closes A; a small one lets it proceed (same mut run)
o3, rm3, rs3 = run_pair(sh_gen={'T4': SH['T4'] + 3000})
check('large T2 closes A (central G2 < 3000)', o3['verdict']['verdict'] == 'A_CLOSED_FOR_MAX_FPS'
      and o3['G']['central']['G'] < BAR, (o3['verdict'], o3['G']['central']['G']))
o3b, rm3b, rs3b = run_pair(sh_gen={'T4': 0.0, 'T4dt': 0.0})
check('no tax: A proceeds, G2 equals the recount', o3b['verdict']['verdict'] == 'A_PROCEEDS_BY_STAGES'
      and abs(o3b['G']['central']['G'] - recount_g(rm3b, rs3b)['G']) < 1e-6, o3b['G']['central'])

# cross-run area check
o4, _, _ = run_pair(sh_gen={'area': 2080})
check('cross-run area 4 % -> NOT_EVALUABLE', o4['verdict']['verdict'] == 'NOT_EVALUABLE', o4['verdict'])
o4b, _, _ = run_pair(sh_gen={'area': 2040})
check('cross-run area 2 % -> evaluable', o4b['verdict']['verdict'] != 'NOT_EVALUABLE', o4b['verdict'])

o4c, _, _ = run_pair(sh_gen={'area': 2062})
check('cross-run area 3.1 % -> NOT_EVALUABLE', o4c['verdict']['verdict'] == 'NOT_EVALUABLE', o4c['verdict'])
o4d, _, _ = run_pair(sh_gen={'area': 2058})
check('cross-run area 2.9 % -> evaluable', o4d['verdict']['verdict'] != 'NOT_EVALUABLE', o4d['verdict'])
o4e, _, _ = run_pair(sh_gen={'area': 1938})
check('cross-run area -3.1 % -> NOT_EVALUABLE', o4e['verdict']['verdict'] == 'NOT_EVALUABLE', o4e['verdict'])
o4f, _, _ = run_pair(sh_gen={'area': 1942})
check('cross-run area -2.9 % -> evaluable', o4f['verdict']['verdict'] != 'NOT_EVALUABLE', o4f['verdict'])
a11 = out['predictions']['A11b']
check('A11b is the one-sided G2 < 3000 prediction', a11['band'][0] is None and 2999.0 < a11['band'][1] < 3000.0
      and a11['hit'] == (out['G']['central']['G'] < 3000.0), a11)
# the sensitivity f = 0.564 (reported only)
cs = g['central']
x = rc['cpu_net'] - (g['central']['S_ctx'])
check('G2 at f = 0.564 recounted', abs(cs['G_fsens'] - (rc['cpu_net'] - (cs['S_ctx'] + 0.564 * x) - rc['spine'] - rc['T4']))
      < 1e-6, cs['G_fsens'])
# 30 pairs is enough
o6, _ = run_one('mut', {'n_pairs': 30})
check('30 pairs -> ADMITTED', o6['status'] == 'ADMITTED' and o6['selection']['pairs'] == 30,
      (o6['failed_controls'], o6['selection']['pairs']))
o6b, _ = run_one('mut', {'n_pairs': 28})
check('28 pairs -> PAIRS', failed(o6b, 'control:PAIRS'))

# draft never admits
o5, _, _ = run_pair(draft=True)
check('draft status DRAFT and no verdict', o5['status'] == 'DRAFT' and o5['verdict']['verdict'].startswith('DRAFT'),
      o5['verdict'])


# ------------------------------------------------------------ mutations: mut arming
def at(idx_want, arm_want, f):
    def mod(n, arm, blk, idx, d):
        if idx == idx_want and arm == arm_want and blk >= 8:
            f(d)
    return mod


o, _ = run_one('mut', {'mod': at(70, 0, lambda d: d.update(mw_n=500))})
check('mw_n leak in arm-0 kept rows -> MW_DARK_ARM0', arming_failed(o, 'MW_DARK_ARM0') and o['status'] == 'INVALID')
o, _ = run_one('mut', {'mod': at(5, 0, lambda d: d.update(mw_n=500))})
check('mw_n leak OUTSIDE kept rows is ignored', o['status'] == 'ADMITTED', o['failed_controls'])


def mw_low(n, arm, blk, idx, d):
    if arm == 1:
        d['mw_n'] = int(0.95 * d['mw_n'])


o, _ = run_one('mut', {'mod': mw_low})
check('mw_n 5 % below identity -> MW_IDENTITY_ARM1', arming_failed(o, 'MW_IDENTITY_ARM1'))


def pl_low(n, arm, blk, idx, d):
    d['pl_em_n'] = int(0.9 * d['pl_em_n'])


o, _ = run_one('mut', {'mod': pl_low})
check('pl_em_n 10 % short -> PATHLAP_ARMED', arming_failed(o, 'PATHLAP_ARMED'))


def pref_zero(n, arm, blk, idx, d):
    d['pl_pref_n'] = 0


o, _ = run_one('mut', {'mod': pref_zero})
check('pl_pref_n 0 -> PATHLAP_ARMED', arming_failed(o, 'PATHLAP_ARMED'))


def chain_low(n, arm, blk, idx, d):
    d['mh_emit_us'] = 8000


o, _ = run_one('mut', {'mod': chain_low})
check('emit chain 0.887 -> PATHLAP_ARMED', arming_failed(o, 'PATHLAP_ARMED'))


def plk_low(n, arm, blk, idx, d):
    d['pl_prog_n'] = int(0.9 * d['pl_prog_n'])


o, _ = run_one('mut', {'mod': plk_low})
check('pl_prog_n 10 % short -> PLKSTAT_IDENTITIES', arming_failed(o, 'PLKSTAT_IDENTITIES'))


def hold_off(n, arm, blk, idx, d):
    d['a_hold_n'] = d['a_hold_n'] + 300


o, _ = run_one('mut', {'mod': hold_off})
check('a_hold_n off identity -> MUTSITE_HOLD_IDENTITY', arming_failed(o, 'MUTSITE_HOLD_IDENTITY'))


def amut_off(n, arm, blk, idx, d):
    if arm == 0:
        d['a_mut_us'] = 0


o, _ = run_one('mut', {'mod': amut_off})
check('amut dark in arm 0 -> AMUT_ARMED', arming_failed(o, 'AMUT_ARMED'))
o, _ = run_one('mut', {'mod': at(70, 1, lambda d: d.update(sh_jobs=10))})
check('shadow jobs in the mut run -> OTHER_INSTRUMENTS_DARK', arming_failed(o, 'OTHER_INSTRUMENTS_DARK'))
o, _ = run_one('mut')
check('the production walker (da_wjobs 8) does not fail the mut darkness', o['status'] == 'ADMITTED',
      o['failed_controls'])

# ------------------------------------------------------------ mutations: sh arming
o, _ = run_one('sh', write={'header': HEADER + ['ShadowResolve: worker %d started' % i for i in range(2)]})
check('two shadow workers -> SH_ONE_WORKER', arming_failed(o, 'SH_ONE_WORKER'))
o, _ = run_one('sh', write={'header': HEADER})
check('no shadow worker line -> SH_ONE_WORKER', arming_failed(o, 'SH_ONE_WORKER'))
o, _ = run_one('sh', write={'header': HEADER + ['ShadowResolve: worker 1 started']})
check('worker 1 only -> SH_ONE_WORKER', arming_failed(o, 'SH_ONE_WORKER'))


def jobs_low(n, arm, blk, idx, d):
    if arm == 1:
        d['sh_jobs'] = int(0.8 * d['draws'])


o, _ = run_one('sh', {'mod': jobs_low})
check('sh_jobs 0.8 a draw -> SH_JOBS_PER_DRAW', arming_failed(o, 'SH_JOBS_PER_DRAW'))


def drops(n, arm, blk, idx, d):
    if arm == 1:
        d['sh_drop'] = int(0.05 * d['sh_jobs'])


o, _ = run_one('sh', {'mod': drops})
check('5 % dropped jobs -> SH_NO_DROP', arming_failed(o, 'SH_NO_DROP'))
o, _ = run_one('sh', {'mod': at(70, 1, lambda d: d.update(a_hold_us=1))})
check('an instrument live in the sh run -> INSTRUMENTS_DARK', arming_failed(o, 'INSTRUMENTS_DARK'))
o, _ = run_one('sh', {'mod': at(70, 0, lambda d: d.update(sh_jobs=5000))})
check('sh_jobs leak in arm-0 kept rows -> SH_DARK_ARM0', arming_failed(o, 'SH_DARK_ARM0'))
o, _ = run_one('sh', {'mod': at(70, 1, lambda d: d.update(mw_n=1))})
check('mw_n live in the sh run -> INSTRUMENTS_DARK', arming_failed(o, 'INSTRUMENTS_DARK'))
o, _ = run_one('sh', {'mod': at(70, 0, lambda d: d.update(a_mut_us=1))})
check('a_mut_us live in the sh run -> INSTRUMENTS_DARK', arming_failed(o, 'INSTRUMENTS_DARK'))
o, _ = run_one('sh', write={'header': SH_HEADER + ['ShadowResolve: worker 0 started']})
check('worker 0 twice -> SH_ONE_WORKER', arming_failed(o, 'SH_ONE_WORKER'))
o, _ = run_one('sh')
check('the production walker (da_wjobs 8) does not fail the sh darkness', o['status'] == 'ADMITTED',
      o['failed_controls'])

# ------------------------------------------------------------ mutations: common controls
o, _ = run_one('mut', write={'gate_hook': lambda blk, gl: gl.replace('mutwide=15', 'mutwide=14') if blk == 9 else gl})
check('wrong arm text -> GATEARM', failed(o, 'integrity:GATEARM'))
o, _ = run_one('sh', write={'gate_hook': lambda blk, gl: gl.replace('shadowresolve=1', 'shadowresolve=4') if blk == 9 else gl})
check('sh arm text shadowresolve=4 -> GATEARM', failed(o, 'integrity:GATEARM'))
o, _ = run_one('sh', write={'env_over': {'KYTY_REC': 'x.mp4'}})
check('KYTY_REC in env -> protocol', failed(o, 'protocol'))
o, _ = run_one('sh', write={'env_over': {'KYTY_GPU_CHECKPOINTS': '0'},
                            'extra_log': ['Vulkan: GPU checkpoints off (KYTY_GPU_CHECKPOINTS=0)']})
check('KYTY_GPU_CHECKPOINTS=0 -> ENV_NO_CHECKPOINTS and NO_CHECKPOINT_LINE',
      failed(o, 'control:ENV_NO_CHECKPOINTS') and failed(o, 'control:NO_CHECKPOINT_LINE'))
o, _ = run_one('mut', write={'extra_stdout': ['Unhandled exception: 0xc0000005']})
check('fatal marker in stdout -> NO_FATAL_MARKER', failed(o, 'control:NO_FATAL_MARKER'))
o, _ = run_one('mut', write={'extra_log': ['AsyncPipelines: skipped draw 0x1']})
check('skipped draw -> NO_FATAL_MARKER', failed(o, 'control:NO_FATAL_MARKER'))
o, _ = run_one('mut', write={'extra_log': ['GpuHangAbort: role=4']})
check('GpuHangAbort -> NO_GPUHANGABORT', failed(o, 'control:NO_GPUHANGABORT'))
o, _ = run_one('mut', write={'extra_log': ['GpuClockPin: mode 1 again']})
check('two pin lines -> PIN_ONCE', failed(o, 'control:PIN_ONCE'))
o, _ = run_one('mut', write={'header': HEADER[:2]})
check('one record thread -> RECORD_THREAD_TWO', failed(o, 'control:RECORD_THREAD_TWO'))
o, _ = run_one('mut', write={'line_hook': lambda n, gr: [gr[0], gr[1], gr[2], gr[3].replace(' mw_n=', ' mw_nX=')]
                             if n == 5000 else gr})
check('field missing on one x line -> SCHEMA', failed(o, 'integrity:SCHEMA'))
o, _ = run_one('mut', write={'line_hook': lambda n, gr: [gr[0], gr[1] + ' mw_n=0', gr[2], gr[3]] if n == 5000 else gr})
check('field on the wrong line -> FIELD_ORIGIN', failed(o, 'integrity:FIELD_ORIGIN'))


def work(n, arm, blk, idx, d):
    if arm == 1:
        d['draws'] = int(d['draws'] * 1.01)
        for k in ('mh_n', 'mh_draws', 'pl_em_n', 'pl_prog_n', 'pl_pipe_n'):
            d[k] = d['draws']
        d['a_hold_n'] = d['draws'] + 268
        d['mw_n'] = 2 * d['draws'] + 268 + 176


o, _ = run_one('mut', {'mod': work})
check('arm 1 does 1 % more draws -> WORK_SPLIT', failed(o, 'control:WORK_SPLIT'))


def area(n, arm, blk, idx, d):
    if arm == 1:
        d['rt_kpx'] = int(d['rt_kpx'] * 1.02)


o, _ = run_one('sh', {'mod': area})
check('arm 1 renders 2 % more area -> AREA_*', failed(o, 'control:AREA_SELECTED') and failed(o, 'control:AREA_VERDICT'))


def dt_band(n, arm, blk, idx, d):
    if n > START:
        d['dt_us'] = 45000


o, _ = run_one('mut', {'mod': dt_band})
check('dt 45 ms -> BANDS', failed(o, 'control:BANDS'))


def rec_band(n, arm, blk, idx, d):
    d['rec_n'] = 8000


o, _ = run_one('mut', {'mod': rec_band})
check('rec_n 8 000 -> BANDS', failed(o, 'control:BANDS'))
o, _ = run_one('mut', {'n_pairs': 10})
check('10 pairs -> PAIRS', failed(o, 'control:PAIRS'))
o, _ = run_one('mut', write={'line_hook': lambda n, gr: [] if n == 4000 else gr})
check('a frame missing -> RAW_CONTIGUITY', failed(o, 'integrity:RAW_CONTIGUITY'))
o, _ = run_one('mut', write={'meta_over': {'attempts': [{'label': 'attempt 1', 'outcome': 'ok',
                                                         'hold_exit': 3, 'hold_s': 300.2}]}})
check('game ended inside the hold -> protocol', failed(o, 'protocol'))
o, _ = run_one('mut', write={'meta_over': {'prereg': {'sha256': '0' * 64, 'bytes': 1}}})
check('prereg hash mismatch -> PREREG_PINNED', failed(o, 'integrity:PREREG_PINNED'))
o, _ = run_one('mut', write={'meta_over': {'binary_sha256': 'f' * 64}})
check('other binary -> BINARY_SEALED', failed(o, 'integrity:BINARY_SEALED'))
o, _ = run_one('mut', write={'meta_over': {'binary_sha256': '16ef56b69c4a99fa6ad613d0dbf57d7f59e0d5443bd6509c55442d83c4780352'}})
check('the session-104 binary -> BINARY_SEALED', failed(o, 'integrity:BINARY_SEALED'))
o, _ = run_one('mut', write={'meta_over': {'schedule': '90+1800:mutwide=0|mutwide=15'}})
check('other schedule -> protocol', failed(o, 'protocol'))
o, _ = run_one('sh', write={'env_over': {'KYTY_GATE_SCHEDULE': '90+1800:shadowresolve=0 shadowmask=3|'
                                                            'shadowresolve=4 shadowmask=3'},
                            'meta_over': {'schedule': '90+1800:shadowresolve=0 shadowmask=3|shadowresolve=4 shadowmask=3'}})
check('the session-104 sh schedule (4 readers) -> protocol', failed(o, 'protocol'))

# ------------------------------------------------------------ the seal and the CLI
saved = (S.PRED_SHA, S.PRED_BYTES)
S.PRED_SHA, S.PRED_BYTES = None, None
try:
    rcode = S.main(['--mut', 'mut119', '--sh', 'sh119', '--root', S.PRODUCTION_ROOT])
    check('unsealed: production scoring refused (exit 2)', rcode == 2, rcode)
    try:
        S.check_seal()
        check('unsealed check_seal raises', False)
    except S.SealError:
        check('unsealed check_seal raises', True)
finally:
    S.PRED_SHA, S.PRED_BYTES = saved
S.PRED_SHA = '0' * 64
try:
    S.check_seal()
    check('changed seal raises', False)
except S.SealError:
    check('changed seal raises', True)
S.PRED_SHA = saved[0]
root = BASE / ('p%03d' % COUNTER[0])
exist = BASE / 'exists.json'
exist.write_bytes(b'{}')
rcode = S.main(['--mut', 'mut119', '--sh', 'sh119', '--root', str(root), '--draft', '--out', str(exist)])
check('--out never overwrites (exit 2)', rcode == 2, rcode)
rcode = S.main(['--mut', 'mut119', '--root', str(root), '--period', '30'])
check('geometry outside --draft refused', rcode == 2, rcode)
rcode = S.main(['--mut', 'mut104', '--root', S.PRODUCTION_ROOT])
check('the session-104 tag is refused (exit 2)', rcode == 2, rcode)
rcode = S.main(['--sh', 'sh104', '--root', S.PRODUCTION_ROOT])
check('the session-104 sh tag is refused (exit 2)', rcode == 2, rcode)
check('the session-104 tag is refused (exit 2)', rcode == 2, rcode)

# ------------------------------------------------------------ real logs (once at the seal, not under mutlib)
if '--real' in sys.argv:
    r = S.evaluate_run('C:/kyty/s102', 'dab102a', 'sh', draft=True)
    st = r['pair_stats']['cpu_net_us']
    check('dab102a: 42 pairs, d cpu_net == dab102.py (113.52463054187207, sd 529.8987787583336)',
          st['n'] == 42 and abs(st['mean'] - 113.52463054187207) < 1e-9 and abs(st['sd'] - 529.8987787583336) < 1e-9, st)
    check('dab102a: levels equal dab102.py arm medians (cpu_net 30668.086, dt 31062.034)',
          abs(r['levels']['arm0']['cpu_net_us'] - 30668.08620689655) < 1e-6
          and abs(r['levels']['arm0']['dt_us'] - 31062.034482758623) < 1e-6)
    check('dab102a: the sh arming FAILS (negative control: no shadow workers)',
          arming_failed(r, 'SH_ONE_WORKER') and arming_failed(r, 'SH_JOBS_PER_DRAW'))
    run = S.read_run('C:/kyty/s116/log_obs116.txt', 'C:/kyty/s116/stdout_obs116.txt')
    check('obs116 (installed binary d3a981a2): every field printed, on its expected line',
          not run['missing_fields']
          and not {f: v for f, v in run['origin'].items() if v and v != [S.EXPECTED_LINE[f]]}
          and all(run['origin'][f] for f in S.FIELDS),
          (run['missing_fields'], [f for f in S.FIELDS if not run['origin'][f]]))
    check('obs116: no checkpoint line, two record threads, one pin line',
          run['counts']['ckpt_off_lines'] == 0 and run['counts']['ckpt_lines'] == 0
          and run['counts']['rec_started'] == 2 and run['counts']['pin'] == {'1': 1}, run['counts'])

fails = [r for r in RESULTS if not r[1]]
for name, ok, why in RESULTS:
    print('%-72s %s %s' % (name, 'ok' if ok else 'FAIL', why))
print('%d fixtures, %d failed' % (len(RESULTS), len(fails)))
print('ALL OK' if not fails else 'FIXTURE FAILURES')
sys.exit(0 if not fails else 1)
