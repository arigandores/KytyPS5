"""Offline tests of dwk104.py (Stage 2 of route A, pred/03_dawalk) on SYNTHETIC logs generated
here, then (unless --no-real) on OLD real logs.

    python C:/kyty/s104/test_dwk104.py [--no-real]

No game, no build.  A reference fixture must be ADMITTED under a temporary seal, meet S1-S3, and
say SHIP_PENDING_VIDEO without a video report and SHIP with a passing one; the ship rule's edges and
every arming check get a MUTATION that must flip them.  Real logs: dab102a (s102: the ABBA machinery
equals dab102.py's, and the arming FAILS there because dawalk was never on - a negative control),
log_sky60.txt (s60: the skip/post identity the arming uses holds on a real dawalk=1 phase and is
exactly zero on the dawalk=0 phases) and reg104 (s104: every field is printed where the scorer
expects it on the CURRENT binary).
"""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import sys
import tempfile

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dwk104 as S  # noqa: E402

PERIOD, START = 90, 1800
ARM_OF = lambda b: (0, 1, 1, 0)[b % 4]
GATES_TEXT = ' '.join(Path(S.GATES_FILE).read_text(encoding='utf-8').split())
TMP = Path(tempfile.mkdtemp(prefix='dwk104_test_', dir=os.environ.get('KYTY_TEST_TMP') or None))
failures = []
passes = [0]

SEAL = TMP / 'seal_03.md'
SEAL.write_text('test seal for dwk104.py\n', encoding='utf-8')
S.PRED = str(SEAL)
S.PRED_SHA = hashlib.sha256(SEAL.read_bytes()).hexdigest()
S.PRED_BYTES = len(SEAL.read_bytes())


def check(name, cond, detail=''):
    if cond:
        passes[0] += 1
        print('  ok   %s' % name)
    else:
        failures.append(name)
        print('  FAIL %s %s' % (name, detail))


def generate(n_pairs=64, seed=1, mod=None, cpu=-300.0, dt=-280.0, noise=300.0):
    quartets = (n_pairs + 1) // 2
    nblocks = 4 + 4 * quartets
    last = START + PERIOD * nblocks + 5
    pre_dt = int((S.HOLD_S + 20) * 1e6 / 1800)
    rng = random.Random(seed)
    rows = {}
    for n in range(2, last + 1):
        if n <= START:
            arm, blk, idx = 0, 0, None
        else:
            blk = (n - START - 1) // PERIOD
            arm, idx = ARM_OF(blk), (n - START - 1) % PERIOD
        att = 12000 + rng.randint(-5, 5)
        d = {'dt_us': (int(31100 + (dt if arm else 0)) + rng.randint(-300, 300)) if n > START
             else pre_dt,
             'draws': int(5000 + 8 * math.sin(n / 41.0)) + rng.randint(-5, 5), 'dispatches': 268,
             'cpu_gpu_us': int(round(30500 + (cpu if arm else 0) + rng.gauss(0, noise))),
             'gpu_busy_us': 12700 + rng.randint(-300, 300), 'arm': arm, 'blk': blk,
             'spin_gpu_us': rng.randint(0, 3), 'rec_n': 10800 + rng.randint(-200, 200),
             'da_walks': 5, 'da_walk_us': 1840 + (600 if arm else 0) + rng.randint(-20, 20),
             'da_queue_us': 760 + (300 if arm else 0) + rng.randint(-8, 8),
             'da_take_us': 2400 + (300 if arm else 0) + rng.randint(-50, 50),
             'da_hit': 8500 - (100 if arm else 0) + rng.randint(-30, 30),
             'da_miss': 73 + (100 if arm else 0) + rng.randint(-3, 3),
             'da_late': 5 if arm else 0, 'da_stale': 0, 'da_stale_old': 0,
             'da_busy': 19 + rng.randint(-1, 1),
             'rt_att': att, 'rt_kpx': att * 2000 + rng.randint(-50, 50),
             'bf_n': 0, 'bf_disp': 0, 'bf_skip': 0, 'bf_clr_skip': 0, 'bf_skip_drop': 0,
             'gm_ops': 0, 'da_wjobs': 8 if arm else 0, 'da_wskip': 8 if arm else 0,
             'da_wdrop': 0, 'da_wlag_us': 900 if arm else 0, 'da_wdepth': 3 if arm else 0,
             'da_qcall': 134, 'mw_n': 0, 'a_hold_us': 0, 'a_mut_us': 0, 'pl_em_n': 0,
             'pl_proc_n': 0, 'sh_jobs': 0}
        if mod is not None:
            mod(n, arm, blk, idx, d)
        rows[n] = d
    return rows


MAIN_KEYS = [k for k, v in S.EXPECTED_LINE.items() if v == 'main']
DRAW_KEYS = [k for k, v in S.EXPECTED_LINE.items() if v == 'draw']
X_KEYS = [k for k, v in S.EXPECTED_LINE.items() if v == 'x']
HEADER = ['GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)',
          'RecordThread: started recorder=0x1000695f2c0 arena=65536KiB gpu=0',
          'RecordThread: started recorder=0x100c7e97ac0 arena=65536KiB gpu=1']


def write_run(root, tag, rows, header=None, extra_log=(), extra_stdout=(), env_over=None,
              meta_over=None, line_hook=None, gate_hook=None):
    root.mkdir(parents=True, exist_ok=True)
    lines = list(HEADER if header is None else header) + list(extra_log)
    for n in sorted(rows):
        d = rows[n]
        if n > START and (n - START - 1) % PERIOD == 0:
            blk = (n - START - 1) // PERIOD
            g = 'GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s' % (
                ARM_OF(blk), blk, START + PERIOD * blk, S.ARMS[ARM_OF(blk)])
            if gate_hook is not None:
                g = gate_hook(blk, g)
            if g is not None:
                lines.append(g)
        group = ['FrameTrace: n=%d lat_us=1 ' % n + ' '.join('%s=%d' % (k, d[k]) for k in MAIN_KEYS),
                 'FrameTrace-draw: n=%d ' % n + ' '.join('%s=%d' % (k, d[k]) for k in DRAW_KEYS),
                 'FrameTrace-rp: n=%d ends=182' % n,
                 'FrameTrace-x: n=%d bda_walk_us=3 ' % n + ' '.join('%s=%d' % (k, d[k])
                                                                   for k in X_KEYS)]
        if line_hook is not None:
            group = line_hook(n, group)
        lines.extend(group)
    (root / ('log_%s.txt' % tag)).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (root / ('stdout_%s.txt' % tag)).write_text('\n'.join(['emulator stdout'] + list(extra_stdout))
                                                + '\n', encoding='utf-8')
    env = {'VK_SDK_PATH': 'C:\\VulkanSDK', 'KYTY_FRAME_TRACE': 'lite',
           'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s104\\gates.req',
           'KYTY_SAMPLE_GATE': 'C:\\kyty\\s104\\sample.req', 'KYTY_QUEUE_TRACE': '1',
           'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_GATE_SCHEDULE': S.SCHEDULE,
           'KYTY_GATE_SCHEDULE_ABBA': '1', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
    env.update(env_over or {})
    meta = {'tag': tag, 'binary_sha256': S.BINARY_SHA, 'env': env, 'schedule': S.SCHEDULE,
            'gates': GATES_TEXT, 'prereg': {'sha256': S.PRED_SHA, 'bytes': S.PRED_BYTES},
            'attempts': [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None,
                          'hold_s': S.HOLD_S + 0.3, 'stable_frame': 300}],
            'hold_s': S.HOLD_S}
    meta.update(meta_over or {})
    (root / ('%s.json' % tag)).write_text(json.dumps(meta, indent=1), encoding='utf-8')


def write_video(root, frames=3842, glitches=0, gates=None, binary=None, env_over=None):
    gates = GATES_TEXT.replace('dawalk=0', 'dawalk=1') if gates is None else gates
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_REC': 'C:\\kyty\\s104\\rec_vwk104.mp4',
           'KYTY_GPU_CLOCK_PIN': '1'}
    env.update(env_over or {})
    meta = {'tag': 'vwk104', 'binary_sha256': binary or S.BINARY_SHA, 'env': env, 'gates': gates,
            'attempts': [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None}]}
    mp, rp = root / 'vwk104.json', root / 'vwk104_glitch.txt'
    mp.write_text(json.dumps(meta), encoding='utf-8')
    rp.write_text('rec_vwk104.mp4: %d frames 960x540, index entries %d\none-frame glitches: %d\n'
                  % (frames, frames, glitches), encoding='utf-8')
    return str(mp), str(rp)


COUNTER = [0]


def run(gen=None, write=None, video=None, draft=False):
    COUNTER[0] += 1
    root = TMP / ('r%03d' % COUNTER[0])
    rows = generate(**(gen or {}))
    write_run(root, 'dwk104', rows, **(write or {}))
    vm = vr = None
    if video is not None:
        vm, vr = write_video(root, **video)
    return S.evaluate(root, 'dwk104', draft=draft, video_meta=vm, video_report=vr), rows


def recount_dcpu(rows):
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
    cn = lambda x: x['cpu_gpu_us'] - x['spin_gpu_us']
    mean = lambda ns: sum(cn(rows[n]) for n in ns) / len(ns)
    d = []
    for l, r in pairs:
        a0, a1 = (l, r) if ARM_OF(l) == 0 else (r, l)
        d.append(mean(usable[a1]) - mean(usable[a0]))
    return statistics.fmean(d), statistics.stdev(d) / math.sqrt(len(d)), len(d)


def failed(out, name):
    return name in out['failed_controls']


def arming_failed(out, name):
    return not ((out.get('arming') or {}).get('checks') or {}).get(name, True)


def main():
    real = '--no-real' not in sys.argv
    print('fixture root %s' % TMP)

    out, rows = run()
    check('reference ADMITTED', out['status'] == 'ADMITTED', out['failed_controls'])
    m, se, n = recount_dcpu(rows)
    st = out['pair_stats']['cpu_net_us']
    check('reference pairs 64 and d cpu_net recounted', n == 64 and st['n'] == 64
          and abs(st['mean'] - m) < 1e-9 and abs(st['se'] - se) < 1e-9, (st, m, se))
    check('reference S1-S3 met', out['ship_rules_S1_S3_met'], out['decision'])
    check('reference without video -> SHIP_PENDING_VIDEO',
          out['verdict'].startswith('SHIP_PENDING_VIDEO'), out['verdict'])
    out, _ = run(video={})
    check('with a passing video -> SHIP', out['verdict'].startswith('SHIP dawalk=1'), out['verdict'])
    check('predictions scored', len(out['predictions']) == 8)
    out, _ = run(video={'glitches': 1})
    check('video with one glitch -> KEEP', out['verdict'].startswith('KEEP'), out['verdict'])
    out, _ = run(video={'frames': 2900})
    check('video with 2 900 frames -> KEEP', out['verdict'].startswith('KEEP'), out['verdict'])
    out, _ = run(video={'gates': GATES_TEXT})
    check('video taken at dawalk=0 -> KEEP', out['verdict'].startswith('KEEP'), out['verdict'])
    out, _ = run(video={'binary': 'e' * 64})
    check('video of another binary -> KEEP', out['verdict'].startswith('KEEP'), out['verdict'])
    out, _ = run(video={'env_over': {'KYTY_GATE_SCHEDULE': '90+1800:dawalk=0|dawalk=1'}})
    check('video under a schedule -> KEEP', out['verdict'].startswith('KEEP'), out['verdict'])

    # the ship rule's edges
    out, _ = run(gen={'cpu': -100.0}, video={})
    check('d cpu_net -100 -> S1 fails, KEEP', not out['decision']['rules']['S1_cpu_net_le_-150']
          and out['verdict'].startswith('KEEP'), out['decision'])
    out, _ = run(gen={'cpu': -170.0, 'noise': 6000.0, 'seed': 3}, video={})
    s = out['pair_stats']['cpu_net_us']
    s2 = out['decision']['rules']['S2_cpu_net_2se_excludes_0']
    check('noisy run exercises S2 (mean %.0f, 2SE %.0f: the interval covers 0)'
          % (s['mean'], 2 * s['se']), s['mean'] + 2 * s['se'] >= 0)
    check('noisy run: S2 false and no SHIP', not s2 and not out['verdict'].startswith('SHIP'),
          (out['decision'], out['verdict']))
    out, _ = run(gen={'dt': 60.0}, video={})
    check('d dt_us positive -> S3 fails, KEEP', not out['decision']['rules']['S3_dt_same_sign']
          and out['verdict'].startswith('KEEP'), out['decision'])

    # arming
    def at(idx_want, arm_want, f):
        def mod(n, arm, blk, idx, d):
            if idx == idx_want and arm == arm_want and blk >= 8:
                f(d)
        return mod

    out, _ = run(gen={'mod': at(70, 0, lambda d: d.update(da_wjobs=1, da_wskip=1))})
    check('arm-0 walker job in a kept row -> WALK_DARK_ARM0', arming_failed(out, 'WALK_DARK_ARM0')
          and out['status'] == 'INVALID')
    out, _ = run(gen={'mod': at(3, 0, lambda d: d.update(da_wjobs=1, da_wskip=1))})
    check('arm-0 walker job OUTSIDE kept rows is ignored', out['status'] == 'ADMITTED',
          out['failed_controls'])

    def unarmed(n, arm, blk, idx, d):
        d.update(da_wjobs=0, da_wskip=0)
    out, _ = run(gen={'mod': unarmed})
    check('arm 1 never armed -> WALK_ARMED_ARM1', arming_failed(out, 'WALK_ARMED_ARM1'))

    def skew(n, arm, blk, idx, d):
        if arm == 1 and n % 5 == 0:
            d['da_wskip'] = 7
    out, _ = run(gen={'mod': skew})
    check('skips ~2.5 %% short of posts -> WALK_IDENTITY_ARM1 (%s)'
          % out['arming'].get('skip_over_posts_rel'), arming_failed(out, 'WALK_IDENTITY_ARM1'))

    def drops(n, arm, blk, idx, d):
        if arm == 1:
            d.update(da_wjobs=7, da_wdrop=1)
    out, _ = run(gen={'mod': drops})
    check('12.5 % of posts dropped -> WALK_DROPS', arming_failed(out, 'WALK_DROPS')
          and not arming_failed(out, 'WALK_IDENTITY_ARM1'))

    def walks(n, arm, blk, idx, d):
        if arm == 1:
            d['da_walks'] = 4
    out, _ = run(gen={'mod': walks})
    check('arm 1 walks 20 % fewer submissions -> WALKS_SAME', arming_failed(out, 'WALKS_SAME'))
    out, _ = run(gen={'mod': at(70, 1, lambda d: d.update(a_hold_us=5))})
    check('an instrument live -> INSTRUMENTS_DARK', arming_failed(out, 'INSTRUMENTS_DARK'))

    # common controls
    out, _ = run(gen={'n_pairs': 50})
    check('50 pairs -> PAIRS', failed(out, 'control:PAIRS'))
    out, _ = run(write={'env_over': {'KYTY_GPU_CHECKPOINTS': '0'},
                        'extra_log': ['Vulkan: GPU checkpoints off (KYTY_GPU_CHECKPOINTS=0)']})
    check('KYTY_GPU_CHECKPOINTS=0 -> ENV_NO_CHECKPOINTS and NO_CHECKPOINT_LINE',
          failed(out, 'control:ENV_NO_CHECKPOINTS') and failed(out, 'control:NO_CHECKPOINT_LINE'))
    out, _ = run(write={'meta_over': {'hold_s': 300}})
    check('hold 300 instead of 600 -> protocol', failed(out, 'protocol'))
    out, _ = run(write={'gate_hook': lambda blk, g: g.replace('dawalklead=1', 'dawalklead=2')
                        if blk == 11 else g})
    check('arm text with dawalklead=2 -> GATEARM', failed(out, 'integrity:GATEARM'))

    def work(n, arm, blk, idx, d):
        if arm == 1:
            d['draws'] = int(d['draws'] * 1.01)
    out, _ = run(gen={'mod': work})
    check('arm 1 does 1 % more draws -> WORK_SPLIT', failed(out, 'control:WORK_SPLIT'))
    out, _ = run(draft=True, video={})
    check('draft never SHIPs', out['status'] == 'DRAFT' and out['verdict'].startswith('DRAFT'),
          out['verdict'])

    # seal and CLI
    saved = (S.PRED_SHA, S.PRED_BYTES)
    S.PRED_SHA, S.PRED_BYTES = None, None
    try:
        check('unsealed: production scoring refused (exit 2)', S.main(['dwk104']) == 2)
    finally:
        S.PRED_SHA, S.PRED_BYTES = saved
    S.PRED_SHA = '1' * 64
    try:
        S.check_seal()
        check('changed seal raises', False)
    except S.SealError:
        check('changed seal raises', True)
    S.PRED_SHA = saved[0]
    exist = TMP / 'exists.json'
    exist.write_text('{}', encoding='utf-8')
    check('--out never overwrites', S.main(['dwk104', '--root', str(TMP / 'r001'), '--draft',
                                            '--out', str(exist)]) == 2)
    check('bad tag refused', S.main(['dab102a']) == 2)

    if real:
        print('real logs:')
        r = S.evaluate('C:/kyty/s102', 'dab102a', draft=True)
        st = r['pair_stats']['cpu_net_us']
        check('dab102a: 42 pairs, d cpu_net == dab102.py (113.52463054187207)',
              st['n'] == 42 and abs(st['mean'] - 113.52463054187207) < 1e-9, st)
        check('dab102a: arming FAILS (dawalk never on: negative control)',
              arming_failed(r, 'WALK_ARMED_ARM1') and arming_failed(r, 'WALK_IDENTITY_ARM1')
              and not arming_failed(r, 'WALK_DARK_ARM0'))
        check('dab102a: PAIRS fails at 42 < 60 (a 300-s run cannot decide)',
              failed(r, 'control:PAIRS'))

        run_ = S.read_run('C:/kyty/s60/log_sky60.txt', None)
        allr = run_['all_rows']

        def tot(a, b, k):
            return sum(allr[n].get(k, 0) for n in range(a, b + 1) if n in allr)
        for name, (a, b), on in (('base1', (17073, 17512), False), ('lead1', (17574, 18013), True),
                                 ('base2', (18081, 18520), False), ('both', (20666, 21105), True)):
            skip, jobs, drop = tot(a, b, 'da_wskip'), tot(a, b, 'da_wjobs'), tot(a, b, 'da_wdrop')
            if on:
                rel = skip / (jobs + drop) - 1
                check('sky60 %s (dawalk=1): skip/posts - 1 = %.5f within 1 %% (%d / %d)'
                      % (name, rel, skip, jobs + drop), abs(rel) <= 0.01)
            else:
                check('sky60 %s (dawalk=0): walker counters exactly 0' % name,
                      skip == jobs == drop == 0, (skip, jobs, drop))

        run_ = S.read_run('C:/kyty/s104/log_reg104.txt', 'C:/kyty/s104/stdout_reg104.txt')
        check('reg104 (current binary): every field printed, on its expected line',
              not run_['missing_fields']
              and not {f: v for f, v in run_['origin'].items() if v and v != [S.EXPECTED_LINE[f]]}
              and all(run_['origin'][f] for f in S.FIELDS), run_['missing_fields'])

    print()
    print('%d passed, %d failed' % (passes[0], len(failures)))
    for f in failures:
        print('  FAILED: %s' % f)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
