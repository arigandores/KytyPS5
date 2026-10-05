"""F20l (HPP-631): fixtures of the harness tools - the <app> mask of enter_scene.py and of the procload line of go_f20l.sh (no input process
name in the output, item 324 (i)), the M6 sampler m6_f20l.py (fake snapshots: names only in the local file, <app> in the git file, game
and loader apart, threshold 0.5, top 3), the loader b32_load.py on a fake growing log (arm on the level line, n_start / n_end, worker count
all / half, ABOVE_NORMAL class read back, stop file, no arm), the cheap refusals of go_f20l.sh and launch_f20l.sh, the knobs of every tag
(dry run 1), queue_f20l.py reading, ASCII and strict cp1250 output of every script.
usage: python test_tools_f20l.py   (ASCII only; the last line is ALL OK)"""
import contextlib
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import threading
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
BASH = shutil.which('bash') or 'bash'
sys.path.insert(0, HERE)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_f20l.py sha256 %s target enter_scene.py sha256 %s go_f20l.sh sha256 %s queue_f20l.py sha256 %s b32_load.py sha256 %s '
      'm6_f20l.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'enter_scene.py')), sha(os.path.join(HERE, 'go_f20l.sh')),
                                sha(os.path.join(HERE, 'queue_f20l.py')), sha(os.path.join(HERE, 'b32_load.py')),
                                sha(os.path.join(HERE, 'm6_f20l.py'))))
import enter_scene as ES  # noqa: E402
import queue_f20l as Q  # noqa: E402

fails = []
n = [0]
TD = os.path.join(HERE, 'fx_tools')
shutil.rmtree(TD, ignore_errors=True)
os.makedirs(TD)


def check(name, cond):
    n[0] += 1
    if not cond:
        fails.append(name)
        print('FAIL', name)


NAMES = ['Zoomish', 'chromeX', 'SecretTool.exe', 'svchost']
# --- enter_scene host census and GPU apps (the F20e members, file of this role)
top = [dict(Name=x, Id=i, CPU=100.0 - i, WS=1048576) for i, x in enumerate(NAMES + ['kyty_emulator'])]


def fake_run(args, **kw):
    cmd = args[-1]
    out = '57' if 'Count' in cmd else json.dumps(top)
    return types.SimpleNamespace(stdout=out, stderr='', returncode=0)


ES.subprocess.run, keep = fake_run, ES.subprocess.run
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    host = ES.sample_host()
ES.subprocess.run = keep
txt = buf.getvalue() + json.dumps(host)
check('host census: no input name in the output', not any(x.lower() in txt.lower() for x in NAMES))
check('host census: <app> written', '<app>' in buf.getvalue() and host['top'][0]['name'] == '<app>')
keep_gpu = ES.idle142.sample_gpu
ES.idle142.sample_gpu = lambda log=print: dict(gpu_util_median=0.0, gpu_power_median=10.0, gpu_memory_used_mib=100, gpu_sm_mhz_median=300,
                                               gpu_util_samples=[0.0], gpu_apps=[dict(pid=1, name='C:/x/SecretGpu.exe'),
                                                                                 dict(pid=2, name='C:/kyty/kyty_emulator.exe')])
ES.subprocess.run = fake_run
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    sec = ES.sample_machine()
ES.idle142.sample_gpu = keep_gpu
ES.subprocess.run = keep
txt = buf.getvalue() + json.dumps(sec)
check('GPU apps and host: no input name in the output', 'secretgpu' not in txt.lower() and not any(x.lower() in txt.lower() for x in NAMES))
check('enter_scene ROOT is f20l', str(ES.ROOT).replace('\\', '/') == 'C:/kyty/f287/f20l')
# --- procload mask of go_f20l.sh
line = "procload: busy [('Zoomish', 1234, 0.91), ('chromeX', 99, 0.6)]"
go = open(os.path.join(HERE, 'go_f20l.sh'), encoding='ascii').read()
sed = [l for l in go.splitlines() if l.startswith('mask()')][0]
p = subprocess.run([BASH, '-c', sed + '; echo "$0" | mask', line], capture_output=True, text=True)
check('procload mask: no input name', 'Zoomish' not in p.stdout and 'chromeX' not in p.stdout and p.stdout.count('<app>') == 2)
check('go: procload output through the mask', 'python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt' in go)
# --- M6 on fake snapshots
snaps = [[[100, 'kyty_emulator.exe', 0.0], [200, 'Zoomish.exe', 0.0], [300, 'chromeX', 0.0], [400, 'svchost', 0.0], [500, 'python.exe', 0.0],
          [600, 'SecretTool.exe', 0.0], [700, 'Idle', 0.0]],
         [[100, 'kyty_emulator.exe', 8.0], [200, 'Zoomish.exe', 2.0], [300, 'chromeX', 0.5], [400, 'svchost', 0.49], [500, 'python.exe', 3.0],
          [600, 'SecretTool.exe', 1.0], [700, 'Idle', 20.0]]]
fk = os.path.join(TD, 'm6fake.json')
json.dump(snaps, open(fk, 'w'))
pf = os.path.join(TD, 'game_pid.txt')
open(pf, 'w').write('100 0\n')
lpf = os.path.join(TD, 'load_pids.txt')
open(lpf, 'w').write('500\n')
loc, out = os.path.join(TD, 'm6_local.txt'), os.path.join(TD, 'm6.txt')
env0 = dict(os.environ)
env0.pop('PYTHONIOENCODING', None)
env0.pop('PYTHONUTF8', None)
p = subprocess.run([sys.executable, os.path.join(HERE, 'm6_f20l.py'), '--pidfile', pf, '--local', loc, '--out', out, '--loadpids', lpf,
                    '--fake', fk], capture_output=True, env=env0)
L = open(loc, encoding='utf-8').read()
O = open(out, encoding='ascii').read()
check('M6 rc 0, end line', p.returncode == 0 and 'M6 end samples=1' in O)
check('M6 game 8, loader 3, foreign 2 + 0.5 + 0.49 + 1 = 3.99', 'game=8.00 loader=3.00 foreign=3.99' in O)
check('M6 top: >= 0.5 only, by rate, at most 3 (Zoomish 2, Secret 1, chromeX 0.5; svchost 0.49 out)',
      'top=Zoomish.exe:200:2.00,SecretTool.exe:600:1.00,chromeX:300:0.50' in L)
check('M6 git file: no input name, <app> written', not any(x.lower() in O.lower() for x in NAMES) and O.count('<app>') == 3)
check('M6 Idle out of foreign', 'Idle' not in L.split('top=')[1])
# --- loader on a fake growing log
LOG = os.path.join(TD, '_kyty.txt')
LPID = os.path.join(TD, 'lpid.txt')


def run_loader(mode, write_level=True, stop_after=None, delay='4', wait_s='20'):
    for f in (LOG, LPID, os.path.join(TD, 'load.json'), os.path.join(TD, 'stop')):
        if os.path.exists(f):
            os.remove(f)
    stopf = os.path.join(TD, 'stop')

    def writer():
        time.sleep(0.3)
        open(LPID, 'w').write('1 0\n')
        with open(LOG, 'w', encoding='ascii', newline='\n') as f:
            for k in range(1, 80):
                f.write('FrameTrace: n=%d dt_us=33333 lat_us=1\n' % k)
                f.flush()
                if k == 5 and write_level:
                    f.write('GuestOut: Level has started: underwater_aerial_garden\n')
                    f.flush()
                if stop_after is not None and k == stop_after:
                    open(stopf, 'w').write('x')
                time.sleep(0.1)
    th = threading.Thread(target=writer)
    th.start()
    p = subprocess.run([sys.executable, os.path.join(HERE, 'b32_load.py'), '--mode', mode, '--pidfile', LPID, '--log', LOG, '--out',
                        os.path.join(TD, 'load.json'), '--pids', os.path.join(TD, 'pids.txt'), '--stop', stopf, '--delay-s', delay,
                        '--wait-s', wait_s], capture_output=True, env=env0, timeout=120)
    th.join()
    return p, json.load(open(os.path.join(TD, 'load.json')))


ncpu = os.cpu_count()
p, j = run_loader('half')
check('loader half: rc 0, done', p.returncode == 0 and j['status'] == 'done')
check('loader half: ceil(ncpu / 2) workers', j['workers'] == int(math.ceil(ncpu / 2.0)) and j['worker_cpu_n'] == j['workers'])
check('loader: ABOVE_NORMAL class read back (0x8000)', j['priority_class'] == [0x8000])
check('loader: n_start after the arm, n_end >= n_start', j['n_start'] is not None and j['n_start'] >= 5 and j['n_end'] >= j['n_start'])
check('loader: burst ~ 400 ms, workers burned CPU', 0.39 <= j['burst_s'] <= 0.9 and j['worker_cpu_s'] > 0.3 * j['workers'] * 0.4)
check('loader: arm to burst = delay 4 s (workers spawned at the arm)', 3.95 <= j['arm_to_burst_s'] <= 4.6)
check('loader output ASCII (strict cp1250 child)', all(b < 128 for b in p.stdout))
p, j = run_loader('all')
check('loader all: ncpu workers', j['status'] == 'done' and j['workers'] == ncpu)
p, j = run_loader('all', write_level=False, wait_s='4')
check('loader: no level line -> no_arm, no burst', j['status'] == 'no_arm' and 'n_start' not in j)
p, j = run_loader('half', stop_after=8, delay='6')
check('loader: stop file before the burst -> stopped', j['status'] == 'stopped' and 'n_start' not in j)
p = subprocess.run([sys.executable, os.path.join(HERE, 'b32_load.py'), '--mode', 'x'], capture_output=True)
check('loader: bad mode refused', p.returncode == 2)
# --- go / launch refusals and dry runs
for bad in ('b32_z1', 'b32_pd3', 'b32_pp_r7', 'f20_v25', ''):
    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l.sh'), bad], capture_output=True, text=True)
    check('go: %r refused (usage)' % bad, p.returncode == 2)
    p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20l.sh'), bad], capture_output=True, text=True)
    check('launch: %r refused (usage)' % bad, p.returncode == 2)
WANT = {'b32_z0': ('KYTY_DIAG_B32=0', 'none'), 'b32_pp': ('KYTY_DIAG_B32=1 KYTY_TEST_B32=60:present:200', 'none'),
        'b32_pc': ('KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:200', 'none'), 'b32_pd': ('KYTY_DIAG_B32=1', 'all'),
        'b32_pd2': ('KYTY_DIAG_B32=1', 'half'), 'b32_pc_r3': ('KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:200', 'none')}
for t, (kn, lm) in WANT.items():
    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l.sh'), t], capture_output=True, text=True, env=dict(os.environ, F20L_DRYRUN='1'))
    check('go dry run %s: knobs %s loader %s' % (t, kn, lm), p.returncode == 0 and ('knobs %s loader %s' % (kn, lm)) in p.stdout)
check('go: enter_scene gets KYTY_GPU_WALL=1 and the knobs positionally',
      'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 $KN > $OUT/run.txt' in go)
check('go: hold 330, stable 300, rec, attempts 1', 'SD=300; H=330' in go and '--rec --hold $H' in go and '--attempts 1' in go)
check('go: test binary and pinned FS8 by sha256', 'TB=b9e0ee0092ca1504979ebd674abb21c8d67015fd030bc33615eb2c87acb90f91' in go and
      'FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b' in go)
check('go: lock.log lines', 'echo "lock taken $T $(u)" >> $G/runs/lock.log' in go and go.count('echo "lock released $T $(u)" >> $G/runs/lock.log') == 2)
check('go: unsets KYTY_* and VK_LAYER_*', "for v in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'); do unset $v; done" in go)
# --- queue_f20l.py reading
ISS = [dict(identifier='HPP-631', status='in_progress', executionRunId='r'), dict(identifier='HPP-557', status='blocked', executionRunId=None),
       dict(identifier='HPP-549', status='blocked', executionRunId='x'), dict(identifier='HPP-603', status='in_progress', executionRunId=None),
       dict(identifier='HPP-1', status='done', executionRunId='y'), dict(identifier='HPP-2', status='todo', executionRunId=None)]


def fake_open(data):
    return lambda req, timeout=30: io.BytesIO(json.dumps(data).encode())


os.environ.setdefault('PAPERCLIP_API_URL', 'http://x/api')
os.environ.setdefault('PAPERCLIP_COMPANY_ID', 'c')
os.environ.setdefault('PAPERCLIP_AGENT_ID', 'a')
os.environ.setdefault('PAPERCLIP_API_KEY', 'k')
keep_open = Q.urllib.request.urlopen
for data, want_rc, want in ((ISS, 1, 'QUEUE BUSY: HPP-549 HPP-603 HPP-2'), ([ISS[0], ISS[1], ISS[4]], 0, 'QUEUE FREE')):
    Q.urllib.request.urlopen = fake_open(data)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = Q.main()
    check('queue %s (own HPP-631 out)' % want, rc == want_rc and buf.getvalue().strip().splitlines()[-1] == want)
Q.urllib.request.urlopen = keep_open
for nm in ('b32_read.py', 'test_b32_read.py', 'sens_b32.py', 'b32_base.py', 'b32_load.py', 'm6_f20l.py', 'go_f20l.sh', 'launch_f20l.sh',
           'wait_f20l.sh', 'post_f20l.sh', 'queue_f20l.py', 'guard_f20l.py', 'watch_f20l.py', 'enter_scene.py', 'test_tools_f20l.py',
           'test_guard_f20l.py', 'port_f20l.py'):
    check('%s ASCII only' % nm, all(b < 128 for b in open(os.path.join(HERE, nm), 'rb').read()))
shutil.rmtree(TD, ignore_errors=True)
print('checks %d, failed %d' % (n[0], len(fails)))
if fails:
    print('FAILED:', fails)
    sys.exit(1)
print('ALL OK')
