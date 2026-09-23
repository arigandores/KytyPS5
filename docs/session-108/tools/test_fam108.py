"""Session 108: fixtures for fam108.py in NON-draft mode.  Rule (decision after 107, item 2): every decision term
and every admission term the candidate depends on gets a fixture where ONLY it fails, plus every verdict branch.
The seal check is pointed at a throwaway file; everything else is the scorer's own code.
    python test_fam108.py <fam108.py>
"""
import hashlib
import importlib.util
import json
import random
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_fam108')
NL = chr(10)
spec = importlib.util.spec_from_file_location('fam108', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
BASE.mkdir(parents=True, exist_ok=True)
seal = BASE / 'seal.md'
seal.write_text('fixture seal 108', encoding='utf-8')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
if not Path(mod.GATES_FILE).is_file():  # before the s108 port exists: the same pinned file of s107
    mod.GATES_FILE = 'C:/kyty/s107/gates_base.txt'
gates_text = ' '.join(Path(mod.GATES_FILE).read_text(encoding='utf-8').split())


def make(name, d_dt=-150, noise=300, blocks=224, skip1=200, look0=0, sync0=1, sync1=1, pins=1, recs=2,
         fatal=None, dt_base=31000, draws1=5000, kpx1=201600, arm_text=None, prereg=None, binary=None,
         extra_env=None, block_noise=0.0):
    d = BASE / name
    d.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(108)
    lines = ['GpuClockPin: mode 1'] * pins + ['RecordThread: started'] * recs
    if fatal:
        lines.append(fatal)
    last = 1800 + 90 * blocks
    sync_left = {0: sync0, 1: sync1}
    for n in range(1700, last + 1):
        if n >= 1800 and (n - 1800) % 90 == 0 and (n - 1800) // 90 < blocks:
            b = (n - 1800) // 90
            arm = (0, 1, 1, 0)[b % 4]
            text = mod.ARMS[arm] if arm_text is None or b != 7 else arm_text
            lines.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s' % (arm, b, n, text))
        blk = (n - 1801) // 90 if n >= 1801 else 0
        arm = (0, 1, 1, 0)[blk % 4] if n >= 1801 else 0
        if n >= 1801 and (n - 1801) % 90 == 0:
            # deterministic spread: arm-1 blocks alternate +A / -A by quartet, so the mean keeps d_dt and the
            # pair SD is ~A
            boff = (block_noise if (blk // 4) % 2 == 0 else -block_noise) if arm else 0.0
        elif n < 1801:
            boff = 0.0
        dt = dt_base + d_dt * arm + boff + rnd.gauss(0, noise)
        cpu = dt_base - 1000 + d_dt * arm + rnd.gauss(0, noise)
        draws = draws1 if arm else 5000
        kpx = kpx1 if arm else 201600
        sn = 0
        if n >= 2200 and sync_left[arm] > 0 and n % 997 == 0:
            sn = 1
            sync_left[arm] -= 1
        lines.append('FrameTrace: n=%d dt_us=%d draws=%d dispatches=268 gpu_busy_us=12700 cpu_gpu_us=%d arm=%d blk=%d'
                     % (n, dt, draws, cpu, arm, blk))
        lines.append('FrameTrace-draw: n=%d spin_gpu_us=30 rec_n=10900 da_walks=8 da_walk_us=2000 da_queue_us=1100 '
                     'da_take_us=2800 da_hit=8350 da_miss=300 da_late=6 da_stale=0 da_stale_old=0 da_busy=0' % n)
        lines.append('FrameTrace-x: n=%d rt_att=100 rt_kpx=%d bf_n=0 bf_disp=0 bf_skip=0 bf_clr_skip=0 '
                     'bf_skip_drop=0 gm_ops=0 da_wjobs=8 da_wskip=8 da_wdrop=0 da_wlag_us=72000 da_wdepth=17 '
                     'da_qcall=1080 mw_n=0 a_hold_us=0 a_mut_us=0 pl_em_n=0 pl_proc_n=0 sh_jobs=0 '
                     'cspfam_look=%d cspfam_skip=%d cs_sync_new=%d cs_sync_wait=0 cspf_have=%d cspf_new=0'
                     % (n, kpx, (266 if arm else look0), (skip1 if arm else 0), sn, (266 - skip1) if arm else 266))
    (d / 'log_fam108.txt').write_text(NL.join(lines) + NL, encoding='utf-8')
    env = dict(mod.ENV_EXPECTED)
    env.update({'KYTY_GATE_FILE': mod.GATES_FILE, 'KYTY_SAMPLE_GATE': '1', 'KYTY_GATE_SCHEDULE': mod.SCHEDULE})
    if extra_env:
        env.update(extra_env)
    meta = {'binary_sha256': binary or mod.BINARY_SHA, 'env': env, 'schedule': mod.SCHEDULE, 'gates': gates_text,
            'hold_s': mod.HOLD_S, 'prereg': prereg or {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES},
            'attempts': [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': mod.HOLD_S}]}
    (d / 'fam108.json').write_text(json.dumps(meta), encoding='utf-8')
    return d


def video(d, frames=3990, glitches=0, gate='cspfam=4', pin='1', binary=None, tag='v'):
    vm = d / ('vfm108_%s.json' % tag)
    vr = d / ('vfm108_%s_glitch.txt' % tag)
    env = {'KYTY_REC': 'x.mp4'}
    if pin:
        env['KYTY_GPU_CLOCK_PIN'] = pin
    vm.write_text(json.dumps({'binary_sha256': binary or mod.BINARY_SHA, 'gates': gates_text + ' ' + gate,
                              'env': env, 'attempts': [{'outcome': 'ok', 'hold_exit': None}]}), encoding='utf-8')
    vr.write_text('rec: %d frames 960x540' % frames + NL + 'one-frame glitches: %d' % glitches + NL, encoding='utf-8')
    return str(vm), str(vr)


good = make('good')
cases = [
    # verdict branches
    ('SHIP', good, video(good, tag='ok'), 'SHIP cspfam=4', None),
    ('PENDING', good, (None, None), 'SHIP_PENDING_VIDEO', None),
    # decision terms, each alone
    ('S1_only', make('s1', d_dt=-60, noise=80), (None, None), 'KEEP cspfam=0 (ship rule', 'S1'),
    ('S2_only', make('s2', d_dt=-150, noise=300, block_noise=1500), (None, None), 'KEEP cspfam=0 (ship rule', 'S2'),
    # video terms, each alone
    ('V_frames', good, video(good, frames=2000, tag='fr'), 'KEEP cspfam=0 (video pass failed)', 'frames'),
    ('V_glitch', good, video(good, glitches=1, tag='gl'), 'KEEP cspfam=0 (video pass failed)', 'no_glitch'),
    ('V_gate', good, video(good, gate='cspfam=0', tag='gt'), 'KEEP cspfam=0 (video pass failed)', 'cspfam_4_in_gate_text'),
    ('V_pin', good, video(good, pin=None, tag='pn'), 'KEEP cspfam=0 (video pass failed)', 'pinned'),
    ('V_binary', good, video(good, binary='0' * 64, tag='bn'), 'KEEP cspfam=0 (video pass failed)', 'binary'),
    # admission terms, each alone
    ('FAM_DARK0', make('dark0', look0=5), (None, None), 'KEEP cspfam=0 (run not admitted)', 'control:ARMING'),
    ('FAM_ARMED1', make('armed1', skip1=0), (None, None), 'KEEP cspfam=0 (run not admitted)', 'control:ARMING'),
    ('SYNC', make('sync', sync0=1, sync1=4), (None, None), 'KEEP cspfam=0 (run not admitted)', 'control:SYNC_COMPILE'),
    ('PIN_ONCE', make('pin', pins=2), (None, None), 'KEEP cspfam=0 (run not admitted)', 'control:PIN_ONCE'),
    ('REC_TWO', make('rec', recs=1), (None, None), 'KEEP cspfam=0 (run not admitted)', 'control:RECORD_THREAD_TWO'),
    ('FATAL', make('fatal', fatal='AsyncPipelines: skipped draw'), (None, None), 'KEEP cspfam=0 (run not admitted)',
     'control:NO_FATAL_MARKER'),
    ('BANDS', make('bands', dt_base=45000), (None, None), 'KEEP cspfam=0 (run not admitted)', 'control:BANDS'),
    # coupled by construction: the area-verdict mirror also checks the work split; area split fails both area
    # controls; fewer blocks shorten the run - each case asserts its exact expected set
    ('WORK', make('work', draws1=5100), (None, None), 'KEEP cspfam=0 (run not admitted)',
     {'control:WORK_SPLIT', 'control:AREA_VERDICT'}),
    ('AREA', make('area', kpx1=206000), (None, None), 'KEEP cspfam=0 (run not admitted)',
     {'control:AREA_SELECTED', 'control:AREA_VERDICT'}),
    ('PAIRS', make('pairs', blocks=100), (None, None), 'KEEP cspfam=0 (run not admitted)',
     {'control:PAIRS', 'integrity:DURATION'}),
    ('GATEARM', make('gatearm', arm_text='dawalk=1 cspfam=9'), (None, None), 'KEEP cspfam=0 (run not admitted)',
     'integrity:GATEARM'),
    ('PREREG', make('prereg', prereg={'sha256': '0' * 64, 'bytes': 1}), (None, None), 'KEEP cspfam=0 (run not admitted)',
     'integrity:PREREG_PINNED'),
    ('BINARY', make('binary', binary='1' * 64), (None, None), 'KEEP cspfam=0 (run not admitted)',
     'integrity:BINARY_SEALED'),
    ('ENV_EXTRA', make('envx', extra_env={'KYTY_SOMETHING_ELSE': '1'}), (None, None), 'KEEP cspfam=0 (run not admitted)',
     'protocol'),
    ('ENV_CKPT', make('envc', extra_env={'KYTY_GPU_CHECKPOINTS': '1'}), (None, None), 'KEEP cspfam=0 (run not admitted)',
     {'control:ENV_NO_CHECKPOINTS', 'protocol'}),
]
ok = True
for name, root, (vm, vr), want, term in cases:
    out = mod.evaluate(root, 'fam108', False, None, mod.GATES_FILE, vm, vr)
    got = out['verdict']
    fails = out.get('failed_controls') or []
    rules = ((out.get('decision') or {}).get('rules') or {})
    vchecks = ((out.get('video') or {}).get('checks') or {})
    only = True
    if term in ('S1', 'S2'):
        failing = [k for k, v in rules.items() if not v]
        only = len(failing) == 1 and failing[0].startswith(term) and not fails
    elif isinstance(term, str) and term in vchecks:
        failing = [k for k, v in vchecks.items() if not v]
        only = failing == [term] and not fails
    elif isinstance(term, set):
        only = set(fails) == term
    elif term is not None:
        only = fails == [term]
    passed = got.startswith(want) and only
    if name == 'S2_only':
        st = (out.get('pair_stats') or {}).get('dt_us') or {}
        print('   S2 case: mean %s se %s rules %s' % (st.get('mean'), st.get('se'), rules))
    ok &= passed
    print('%-10s want %-36s got %-44s only=%s %s  failed=%s' % (name, want[:36], got[:44], only, 'OK' if passed else 'FAIL',
                                                              fails))
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
