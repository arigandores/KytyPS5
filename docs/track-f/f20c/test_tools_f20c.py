"""F20c (HPP-561): fixtures of the harness tools - the <app> mask of enter_scene.py (item 463 (2); process rule of item 324 (i): no input
process name in the output), the procload mask of go_f20c.sh, the cheap refusals of go_f20c.sh and launch_f20c.sh, queue_f20c.py
reading, ASCII of every script.  usage: python test_tools_f20c.py   (ASCII only; the last line is ALL OK)"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
BASH = shutil.which('bash') or 'bash'   # not the WSL bash of System32 (CreateProcess search order)
sys.path.insert(0, HERE)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_f20c.py sha256 %s target enter_scene.py sha256 %s go_f20c.sh sha256 %s queue_f20c.py sha256 %s' % (
    sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'enter_scene.py')), sha(os.path.join(HERE, 'go_f20c.sh')),
    sha(os.path.join(HERE, 'queue_f20c.py'))))
import enter_scene as ES  # noqa: E402
import queue_f20c as Q  # noqa: E402

fails = []
n = [0]


def check(name, cond):
    n[0] += 1
    if not cond:
        fails.append(name)
        print('FAIL', name)


NAMES = ['Zoomish', 'chromeX', 'SecretTool.exe', 'svchost']
# --- sample_host: the printed line and the returned dict carry no input name but the emulator
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
check('host census: the emulator kept', 'kyty_emulator' in json.dumps(host['top_names']))
check('host census: count kept', host['process_count'] == 57)
# --- sample_machine: GPU app names masked
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
check('GPU apps: emulator kept', 'kyty_emulator.exe' in txt)
check('mask_name edge: empty and None', ES.mask_name(None) == '<app>' and ES.mask_name('') == '<app>')
check('mask_name: emulator by base name', ES.mask_name('KYTY_EMULATOR') == 'KYTY_EMULATOR')
# --- procload mask of go_f20c.sh (the sed of the mask() function)
line = "procload: busy [('Zoomish', 1234, 0.91), ('chromeX', 99, 0.6)]"
go = open(os.path.join(HERE, 'go_f20c.sh'), encoding='ascii').read()
sed = [l for l in go.splitlines() if l.startswith('mask()')][0]
check('go mask() is the sed of F18e', "sed -E \"s/\\('[^']*'/('<app>'/g\"" in sed)
p = subprocess.run([BASH, '-c', sed + '; echo "$0" | mask', line], capture_output=True, text=True)
check('procload mask: no input name', 'Zoomish' not in p.stdout and 'chromeX' not in p.stdout and p.stdout.count('<app>') == 2)
# --- cheap refusals (no lock taken, no process started): usage and order
p = subprocess.run([BASH, os.path.join(HERE, 'go_f20c.sh'), 'f20_v31'], capture_output=True, text=True)
check('go: f20_v31 refused (usage)', p.returncode == 2)
p = subprocess.run([BASH, os.path.join(HERE, 'go_f20c.sh'), 'f20_v1'], capture_output=True, text=True)
check('go: f20_v1 refused (usage)', p.returncode == 2)
if not os.path.isdir(os.path.join(HERE, 'runs', 'f20_v01')):
    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20c.sh'), 'f20_v02'], capture_output=True, text=True)
    check('go: f20_v02 before f20_v01 refused (order, or lock rc 3)', p.returncode in (2, 3) and ('order' in p.stdout or p.returncode == 3))
p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20c.sh'), 'f20_v31'], capture_output=True, text=True)
check('launch: f20_v31 refused', p.returncode == 2)
for nm in ('post_f20c.sh', 'wait_f20c.sh', 'launch_f20c.sh', 'go_f20c.sh'):
    s = open(os.path.join(HERE, nm), encoding='ascii').read()
    check('%s: tags f20_v01..f20_v30 only' % nm, nm == 'wait_f20c.sh' or 'f20_v0[1-9]|f20_v[12][0-9]|f20_v30' in s)
# --- queue_f20c.py reading on a fake API answer
ISS = [dict(identifier='HPP-561', status='in_progress', executionRunId='r'), dict(identifier='HPP-557', status='blocked', executionRunId=None),
       dict(identifier='HPP-549', status='blocked', executionRunId='x'), dict(identifier='HPP-500', status='in_progress', executionRunId=None),
       dict(identifier='HPP-1', status='done', executionRunId='y'), dict(identifier='HPP-2', status='todo', executionRunId=None)]


def fake_open(data):
    class R(io.BytesIO):
        pass
    return lambda req, timeout=30: R(json.dumps(data).encode())


os.environ.setdefault('PAPERCLIP_API_URL', 'http://x/api')
os.environ.setdefault('PAPERCLIP_COMPANY_ID', 'c')
os.environ.setdefault('PAPERCLIP_AGENT_ID', 'a')
os.environ.setdefault('PAPERCLIP_API_KEY', 'k')
keep_open = Q.urllib.request.urlopen
for data, want_rc, want in ((ISS, 1, 'QUEUE BUSY: HPP-549 HPP-500 HPP-2'), ([ISS[0], ISS[1], ISS[4]], 0, 'QUEUE FREE'),
                            (dict(issues=[ISS[1]]), 0, 'QUEUE FREE')):
    Q.urllib.request.urlopen = fake_open(data)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = Q.main()
    check('queue %s' % want, rc == want_rc and buf.getvalue().strip().splitlines()[-1] == want)


def boom(req, timeout=30):
    raise OSError('x')


Q.urllib.request.urlopen = boom
with contextlib.redirect_stdout(io.StringIO()):
    check('queue: API error -> 2', Q.main() == 2)
Q.urllib.request.urlopen = keep_open
for nm in ('f20c_read.py', 'test_f20c_read.py', 'sens_f20c.py', 'go_f20c.sh', 'launch_f20c.sh', 'wait_f20c.sh', 'post_f20c.sh', 'queue_f20c.py',
           'watch_f20c.py', 'enter_scene.py', 'test_tools_f20c.py'):
    check('%s ASCII only' % nm, all(b < 128 for b in open(os.path.join(HERE, nm), 'rb').read()))
print('checks %d, failed %d' % (n[0], len(fails)))
if fails:
    print('FAILED:', fails)
    sys.exit(1)
print('ALL OK')
