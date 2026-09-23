"""Session 107: fixtures for dab107.py in NON-draft mode - every verdict branch (SHIP, SHIP_PENDING_VIDEO, KEEP by
the bar, KEEP by a failed video, INVALID by the batch arming), with full protocol metadata.  The seal check is
pointed at a throwaway file; everything else is the scorer's own code.
    python C:/kyty/s107/test_dab107.py C:/kyty/s107/dab107.py
"""
import hashlib
import importlib.util
import json
import random
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_dab107')
NL = chr(10)
spec = importlib.util.spec_from_file_location('dab107', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
BASE.mkdir(parents=True, exist_ok=True)
seal = BASE / 'seal.md'
seal.write_text('fixture seal 107', encoding='utf-8')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
gates_text = ' '.join(Path(mod.GATES_FILE).read_text(encoding='utf-8').split())


def make(name, d_dt, qratio=4):
    d = BASE / name
    d.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(107)
    blocks = 224
    lines = ['GpuClockPin: mode 1', 'RecordThread: started gpu', 'RecordThread: started present']
    last = 1800 + 90 * blocks
    for n in range(1700, last + 1):
        if n >= 1800 and (n - 1800) % 90 == 0 and (n - 1800) // 90 < blocks:
            b = (n - 1800) // 90
            arm = (0, 1, 1, 0)[b % 4]
            lines.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                         % (arm, b, n, mod.ARMS[arm]))
        blk = (n - 1801) // 90 if n >= 1801 else 0
        arm = (0, 1, 1, 0)[blk % 4] if n >= 1801 else 0
        dt = 31000 + d_dt * arm + rnd.gauss(0, 300)
        cpu = 30000 + d_dt * arm + rnd.gauss(0, 300)
        q = 1080 * (qratio if arm else 1)
        lines.append('FrameTrace: n=%d dt_us=%d draws=5000 dispatches=268 gpu_busy_us=12700 cpu_gpu_us=%d arm=%d blk=%d'
                     % (n, dt, cpu, arm, blk))
        lines.append('FrameTrace-draw: n=%d spin_gpu_us=30 rec_n=10900 da_walks=8 da_walk_us=2000 da_queue_us=%d '
                     'da_take_us=2800 da_hit=8350 da_miss=300 da_late=6 da_stale=0 da_stale_old=0 da_busy=0'
                     % (n, 840 + 200 * arm))
        lines.append('FrameTrace-x: n=%d rt_att=100 rt_kpx=201600 bf_n=0 bf_disp=0 bf_skip=0 bf_clr_skip=0 '
                     'bf_skip_drop=0 gm_ops=0 da_wjobs=8 da_wskip=8 da_wdrop=0 da_wlag_us=72000 da_wdepth=17 '
                     'da_qcall=%d mw_n=0 a_hold_us=0 a_mut_us=0 pl_em_n=0 pl_proc_n=0 sh_jobs=0' % (n, q))
    (d / 'log_dab107.txt').write_text(NL.join(lines) + NL, encoding='utf-8')
    env = dict(mod.ENV_EXPECTED)
    env.update({'KYTY_GATE_FILE': mod.GATES_FILE, 'KYTY_SAMPLE_GATE': '1', 'KYTY_GATE_SCHEDULE': mod.SCHEDULE})
    meta = {'binary_sha256': mod.BINARY_SHA, 'env': env, 'schedule': mod.SCHEDULE, 'gates': gates_text,
            'hold_s': mod.HOLD_S, 'prereg': {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES},
            'attempts': [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': mod.HOLD_S}]}
    (d / 'dab107.json').write_text(json.dumps(meta), encoding='utf-8')
    return d


def video(d, glitches):
    vm = d / 'vdb107.json'
    vr = d / 'vdb107_glitch.txt'
    vm.write_text(json.dumps({'binary_sha256': mod.BINARY_SHA, 'gates': gates_text + ' dabatch=2',
                              'env': {'KYTY_REC': 'x.mp4', 'KYTY_GPU_CLOCK_PIN': '1'},
                              'attempts': [{'outcome': 'ok', 'hold_exit': None}]}), encoding='utf-8')
    vr.write_text('rec: 3990 frames 960x540' + NL + 'one-frame glitches: %d' % glitches + NL, encoding='utf-8')
    return str(vm), str(vr)


cases = []
d = make('ship', -150)
cases.append(('ship', d, video(d, 0), 'SHIP dabatch=2'))
cases.append(('pending', d, (None, None), 'SHIP_PENDING_VIDEO'))
cases.append(('video_fail', d, video(make('ship_vf', -150), 1), 'KEEP dabatch=8 (video pass failed)'))
d2 = make('keep', -40)
cases.append(('keep_bar', d2, (None, None), 'KEEP dabatch=8 (ship rule'))
d3 = make('unarmed', -150, qratio=1)
cases.append(('unarmed', d3, (None, None), 'KEEP dabatch=8 (run not admitted)'))
ok = True
for name, root, (vm, vr), want in cases:
    out = mod.evaluate(root, 'dab107', False, None, mod.GATES_FILE, vm, vr)
    got = out['verdict']
    fails = out.get('failed_controls')
    passed = got.startswith(want)
    ok &= passed
    dt = (out.get('pair_stats') or {}).get('dt_us', {}).get('mean')
    print('%-10s want %-38s got %-60s %s dt=%s failed=%s' % (name, want[:38], got[:60], 'OK' if passed else 'FAIL',
                                                             None if dt is None else round(dt, 1), fails))
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
