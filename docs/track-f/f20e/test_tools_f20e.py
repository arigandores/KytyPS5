"""F20e (HPP-624): fixtures of the harness tools - the <app> mask of enter_scene.py (item 463 (2); process rule of item 324 (i): no input
process name in the output), the procload mask of go_f20e.sh, the cheap refusals of go_f20e.sh and launch_f20e.sh, queue_f20e.py
reading, ASCII of every script.  usage: python test_tools_f20e.py   (ASCII only; the last line is ALL OK)"""
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


print('suite test_tools_f20e.py sha256 %s target enter_scene.py sha256 %s go_f20e.sh sha256 %s queue_f20e.py sha256 %s' % (
    sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'enter_scene.py')), sha(os.path.join(HERE, 'go_f20e.sh')),
    sha(os.path.join(HERE, 'queue_f20e.py'))))
import enter_scene as ES  # noqa: E402
import queue_f20e as Q  # noqa: E402

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
# --- procload mask of go_f20e.sh (the sed of the mask() function)
line = "procload: busy [('Zoomish', 1234, 0.91), ('chromeX', 99, 0.6)]"
go = open(os.path.join(HERE, 'go_f20e.sh'), encoding='ascii').read()
sed = [l for l in go.splitlines() if l.startswith('mask()')][0]
check('go mask() is the sed of F18e', "sed -E \"s/\\('[^']*'/('<app>'/g\"" in sed)
p = subprocess.run([BASH, '-c', sed + '; echo "$0" | mask', line], capture_output=True, text=True)
check('procload mask: no input name', 'Zoomish' not in p.stdout and 'chromeX' not in p.stdout and p.stdout.count('<app>') == 2)
# --- cheap refusals (no lock taken, no process started): usage and order
p = subprocess.run([BASH, os.path.join(HERE, 'go_f20e.sh'), 'f20_v55'], capture_output=True, text=True)
check('go: f20_v55 refused (usage)', p.returncode == 2)
p = subprocess.run([BASH, os.path.join(HERE, 'go_f20e.sh'), 'f20_v1'], capture_output=True, text=True)
check('go: f20_v1 refused (usage)', p.returncode == 2)
for bad in ('f20_v24', 'f20_v01', 'f20_v30x'):
    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20e.sh'), bad], capture_output=True, text=True)
    check('go: %s refused (usage)' % bad, p.returncode == 2)
go_src = open(os.path.join(HERE, 'go_f20e.sh'), encoding='ascii').read()
check('go: only FS8 admitted', 'FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b' in go_src
      and '[ "$WANT" = "$FS8" ] ||' in go_src and 'ADB=' not in go_src and 'FS6=' not in go_src)
check('go: order from f20_v25', 'if [ $NN -gt 25 ]; then' in go_src)
if not os.path.isdir(os.path.join(HERE, 'runs', 'f20_v25')):
    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20e.sh'), 'f20_v26'], capture_output=True, text=True)
    check('go: f20_v26 before f20_v25 refused (order, or lock rc 3)', p.returncode in (2, 3) and ('order' in p.stdout or p.returncode == 3))
p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20e.sh'), 'f20_v55'], capture_output=True, text=True)
check('launch: f20_v55 refused', p.returncode == 2)
# --- FS6b window of item 473: fresh file -> rc 6 + times line, no launch; expired -> times line and on (dry run); absent -> on, no line
import tempfile  # noqa: E402
import time  # noqa: E402
TD = tempfile.mkdtemp()
WF, TF = os.path.join(TD, 'FS6B_WINDOW'), os.path.join(TD, 'times.txt')
ENV = dict(os.environ, F20E_FS6B_WINDOW=WF, F20E_TIMES=TF, F20E_DRYRUN='1')


def launch_w(age):
    if os.path.exists(TF):
        os.remove(TF)
    if age is None:
        if os.path.exists(WF):
            os.remove(WF)
    else:
        open(WF, 'w').close()
        t = time.time() - age
        os.utime(WF, (t, t))
    p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20e.sh'), 'f20_v54'], capture_output=True, text=True, env=ENV)
    tl = open(TF).read() if os.path.exists(TF) else ''
    return p.returncode, p.stdout, tl


rc, out, tl = launch_w(0)
check('window: fresh 0 s -> rc 6, not launched, times active', rc == 6 and 'launched' not in out and 'window active' in tl and 'f20_v54' in tl)
rc, out, tl = launch_w(890)
check('window: 890 s -> rc 6', rc == 6 and 'window active' in tl)
rc, out, tl = launch_w(910)
check('window: 910 s -> expired line, goes (dry run), file kept', rc == 0 and 'dryrun' in out and 'window expired' in tl and os.path.exists(WF))
rc, out, tl = launch_w(None)
check('window: absent -> goes (dry run), no window line', rc == 0 and 'dryrun' in out and 'window' not in tl)
shutil.rmtree(TD, ignore_errors=True)
for nm in ('post_f20e.sh', 'wait_f20e.sh', 'launch_f20e.sh', 'go_f20e.sh'):
    s = open(os.path.join(HERE, nm), encoding='ascii').read()
    check('%s: tags f20_v25..f20_v54 only' % nm, nm == 'wait_f20e.sh' or 'f20_v2[5-9]|f20_v[34][0-9]|f20_v5[0-4]' in s)
# --- queue_f20e.py reading on a fake API answer
ISS = [dict(identifier='HPP-624', status='in_progress', executionRunId='r'), dict(identifier='HPP-557', status='blocked', executionRunId=None),
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
for nm in ('f20e_read.py', 'test_f20e_read.py', 'sens_f20e.py', 'go_f20e.sh', 'launch_f20e.sh', 'wait_f20e.sh', 'post_f20e.sh', 'queue_f20e.py',
           'watch_f20e.py', 'enter_scene.py', 'test_tools_f20e.py'):
    check('%s ASCII only' % nm, all(b < 128 for b in open(os.path.join(HERE, nm), 'rb').read()))
print('checks %d, failed %d' % (n[0], len(fails)))
if fails:
    print('FAILED:', fails)
    sys.exit(1)
print('ALL OK')
