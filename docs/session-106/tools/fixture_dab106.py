"""Session 106: synthetic ABBA fixture for gw106.py - every field the scorer parses, planted effects.
Planted (arm 1 - arm 0, us a flip): dt -266, cpu_gpu -462, spin -4 => D +192; idle +20, blk 0, flip 0,
lock +30 => R +142 (>= D/2 = 96): expected verdict "NAMED R_us" in a non-draft reading, and every
arming / control check PASS except the seal / protocol ones a fixture cannot carry.
    python C:/kyty/s106_stage/fixture_gw106.py <dir> [--flip-effect]
"""
import json
import random
import sys
from pathlib import Path

D = Path(sys.argv[1])
D.mkdir(parents=True, exist_ok=True)
FLIP = '--flip-effect' in sys.argv          # second fixture: the effect planted in gw_flip instead of R
NL = chr(10)
rnd = random.Random(106)
ARMS = ('dawalk=1 dawalklead=1 dabatch=64', 'dawalk=1 dawalklead=1 dabatch=8')
BLOCKS = 140
lines = ['GpuClockPin: mode 1', 'RecordThread: started gpu', 'RecordThread: started present',
         'GpuWall: mode 1']
first, last = 1700, 1800 + 90 * BLOCKS
for n in range(first, last + 1):
    blk = (n - 1801) // 90 if n >= 1801 else -1
    if n >= 1800 and (n - 1800) % 90 == 0 and (n - 1800) // 90 < BLOCKS:
        b = (n - 1800) // 90
        arm = (0, 1, 1, 0)[b % 4]
        lines.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s' % (arm, b, n, ARMS[arm]))
    arm = (0, 1, 1, 0)[blk % 4] if blk >= 0 else 0
    e = lambda s: rnd.gauss(0, s)
    dt = 32000 - 150 * arm + e(300)
    cpu = 31200 - 300 * arm + e(300)
    spin = 37 - 4 * arm
    idle = 200 + 20 * arm + e(20)
    flip = 100 + (96 * arm if FLIP else 0) + e(10)
    lock = 40 + 30 * arm
    cmd = 50
    proc = dt - idle - cmd - 200
    main = ('FrameTrace: n=%d dt_us=%d lat_us=11000 gpu_proc=0 draws=5000 dispatches=268 gpu_busy_us=12400 '
            'cpu_gpu_us=%d arm=%d blk=%d rt_w=3840 rt_h=2160' % (n, dt, cpu, arm, max(blk, 0)))
    draw = ('FrameTrace-draw: n=%d spin_gpu_us=%d rec_n=11000 da_walks=8 da_walk_us=1900 da_queue_us=780 '
            'da_take_us=2450 da_hit=5000 da_miss=300 da_late=8 da_stale=0 da_stale_old=0 da_busy=0' % (n, spin))
    x = ('FrameTrace-x: n=%d rt_att=100 rt_kpx=201600 bf_n=0 bf_disp=0 bf_skip=0 bf_clr_skip=0 bf_skip_drop=0 '
         'gm_ops=0 da_wjobs=%d da_wskip=%d da_wdrop=0 da_wlag_us=%d da_wdepth=0 da_qcall=%d mw_n=0 '
         'a_hold_us=0 a_mut_us=0 pl_em_n=0 pl_proc_n=0 sh_jobs=0 gw_idle_ns=%d gw_idle_n=30 gw_blk_ns=0 '
         'gw_blk_n=0 gw_flip_ns=%d gw_flip_n=1 gw_proc_ns=%d gw_proc_n=38 gw_cmd_ns=%d gw_cmd_n=4 '
         'pl_prog_wait_us=%d pl_pipe_wait_us=0 pl_cs_wait_us=0 pl_prog_n=5000 pl_pipe_n=5000 pl_cs_n=268 '
         'pl_prog_hold_us=4000'
         % (n, 8, 8, 74000, 134 + 938 * arm, idle * 1000, flip * 1000, proc * 1000, cmd * 1000, lock))
    lines += [main, draw, x]
(D / 'log_fx106.txt').write_text(NL.join(lines) + NL, encoding='utf-8')
meta = {'binary_sha256': 'd23094dfe42478f8a40907741120837c4cf952ff16b830c1e6e55697dc177db3',
        'hold_s': 600, 'env': {}, 'attempts': [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None,
                                                 'hold_s': 600}]}
(D / 'fx106.json').write_text(json.dumps(meta), encoding='utf-8')
print('dab fixture', D, 'frames', last - first + 1, 'flip-effect' if FLIP else 'R-effect')
