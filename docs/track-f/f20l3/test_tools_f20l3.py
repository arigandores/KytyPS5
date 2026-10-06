"""F20l3 (HPP-655): fixtures of the harness tools - the <app> mask of enter_scene.py and of the procload line of go_f20l3.sh (no input process
name in the output, item 324 (i)), the M6 sampler m6_f20l3.py (fake snapshots: names only in the local file, <app> in the git file, game
and loader apart, threshold 0.5, top 3), reserve_f20l3.py (the cold form of item 591 (v)(1) on a fake emulator folder: the moved set, what
stays, reserve.tsv = pre-tag manifest lines, COLD OK / COLD NOT, RESERVE IN AFTER / NOT, refusals), the cheap refusals of go_f20l3.sh,
launch_f20l3.sh and post_f20l3.sh, the knobs and the cold flag of every tag (dry run 1), the S18 constants, queue_f20l3.py and
runchk_f20l3.py reading, ASCII and strict cp1250 output of every script.
usage: python test_tools_f20l3.py   (ASCII only; the last line is ALL OK)"""
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


print('suite test_tools_f20l3.py sha256 %s target enter_scene.py sha256 %s go_f20l3.sh sha256 %s queue_f20l3.py sha256 %s reserve_f20l3.py '
      'sha256 %s m6_f20l3.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'enter_scene.py')),
                                          sha(os.path.join(HERE, 'go_f20l3.sh')), sha(os.path.join(HERE, 'queue_f20l3.py')),
                                          sha(os.path.join(HERE, 'reserve_f20l3.py')), sha(os.path.join(HERE, 'm6_f20l3.py'))))
import enter_scene as ES  # noqa: E402
import queue_f20l3 as Q  # noqa: E402

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
check('enter_scene ROOT is f20l3', str(ES.ROOT).replace('\\', '/') == 'C:/kyty/f287/f20l3')
# --- procload mask of go_f20l3.sh
line = "procload: busy [('Zoomish', 1234, 0.91), ('chromeX', 99, 0.6)]"
go = open(os.path.join(HERE, 'go_f20l3.sh'), encoding='ascii').read()
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
p = subprocess.run([sys.executable, os.path.join(HERE, 'm6_f20l3.py'), '--pidfile', pf, '--local', loc, '--out', out, '--loadpids', lpf,
                    '--fake', fk], capture_output=True, env=env0)
L = open(loc, encoding='utf-8').read()
O = open(out, encoding='ascii').read()
check('M6 rc 0, end line', p.returncode == 0 and 'M6 end samples=1' in O)
check('M6 game 8, loader 3, foreign 2 + 0.5 + 0.49 + 1 = 3.99', 'game=8.00 loader=3.00 foreign=3.99' in O)
check('M6 top: >= 0.5 only, by rate, at most 3 (Zoomish 2, Secret 1, chromeX 0.5; svchost 0.49 out)',
      'top=Zoomish.exe:200:2.00,SecretTool.exe:600:1.00,chromeX:300:0.50' in L)
check('M6 git file: no input name, <app> written', not any(x.lower() in O.lower() for x in NAMES) and O.count('<app>') == 3)
check('M6 Idle out of foreign', 'Idle' not in L.split('top=')[1])
# --- reserve_f20l3.py: the cold form of b32_pa / b32_pa2 (item 591 (v)(1)) on a fake emulator folder
import reserve_f20l3 as RV  # noqa: E402
import manifest_fs4c as MF  # noqa: E402
EMU = os.path.join(TD, 'emu')


def mk_emu(seeds=True, variant=True):
    shutil.rmtree(EMU, ignore_errors=True)
    root = os.path.join(EMU, '_ShaderCache', 'PPSA21564')
    os.makedirs(os.path.join(root, 'replay'))
    os.makedirs(os.path.join(root, 'variant_fixb26_fixb1b'))
    open(os.path.join(root, 'replay', 'replay.cur'), 'w').write('r')
    open(os.path.join(root, 'variant_fixb26_fixb1b', 'pipelines.bin'), 'w').write('other variant')
    for fn in ('cs_0011223344556677_8899aabbccddeeff.bin', 'ps_0011223344556677_8899aabbccddee00.bin',
               'vs_0011223344556677_8899aabbccddee11.bin', 'pipelines.bin', 'notes.txt', 'ps_short.bin'):
        open(os.path.join(root, fn), 'w').write(fn)
    if variant:
        v = os.path.join(root, 'variant_fixb26_fixb1b_fixf10_fixf19')
        os.makedirs(os.path.join(v, 'sub'))
        open(os.path.join(v, 'pipelines.bin'), 'w').write('recipes')
        open(os.path.join(v, 'vs_1111111111111111_2222222222222222.bin'), 'w').write('vs')
        open(os.path.join(v, 'sub', 'x.bin'), 'w').write('x')
    if seeds:
        s = os.path.join(EMU, '_ShaderSeeds', 'PPSA21564')
        os.makedirs(s)
        open(os.path.join(s, 'compatibility.txt'), 'w').write('KytySeed1')
        open(os.path.join(s, 'pipelines.bin'), 'w').write('seed recipes')
    os.makedirs(os.path.join(EMU, '_ShaderSeeds', 'OTHER'), exist_ok=True)


def man(path):
    lines = MF.manifest(['_ShaderCache=' + os.path.join(EMU, '_ShaderCache'), '_ShaderSeeds=' + os.path.join(EMU, '_ShaderSeeds')])
    open(path, 'wb').write(('\n'.join(lines) + '\n').encode('utf-8'))
    return set(lines)


mk_emu()
before = man(os.path.join(TD, 'm_before.tsv'))
RES = os.path.join(TD, 'reserve')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = RV.move(EMU, RES)
check('reserve move: rc 0, RESERVE MOVED, 9 files (3 root programs + root pipelines.bin + 3 variant files + 2 seeds)', rc == 0 and
      buf.getvalue().startswith('RESERVE MOVED files 9 '))
root = os.path.join(EMU, '_ShaderCache', 'PPSA21564')
left = sorted(os.listdir(root))
check('reserve move: root keeps replay/, other variant, notes.txt, ps_short.bin (not a program name)', left == [
    'notes.txt', 'ps_short.bin', 'replay', 'variant_fixb26_fixb1b'])
check('reserve move: _ShaderSeeds/PPSA21564 moved, _ShaderSeeds/OTHER stays', not os.path.exists(os.path.join(EMU, '_ShaderSeeds', 'PPSA21564'))
      and os.path.isdir(os.path.join(EMU, '_ShaderSeeds', 'OTHER')))
rlines = [x for x in open(os.path.join(RES, 'reserve.tsv'), 'rb').read().decode('utf-8').split('\n') if x]
check('reserve.tsv lines are manifest lines of the pre-tag manifest (9 of 9)', len(rlines) == 9 and all(x in before for x in rlines))
check('reserve.tsv: labels and paths', any(x.startswith('_ShaderSeeds\tPPSA21564/compatibility.txt\t') for x in rlines) and
      any(x.startswith('_ShaderCache\tPPSA21564/variant_fixb26_fixb1b_fixf10_fixf19/sub/x.bin\t') for x in rlines) and
      any(x.startswith('_ShaderCache\tPPSA21564/pipelines.bin\t') for x in rlines))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = RV.cold(EMU)
check('cold: COLD OK after the move', rc == 0 and buf.getvalue().startswith('COLD OK'))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = RV.check(os.path.join(RES, 'reserve.tsv'), os.path.join(TD, 'm_before.tsv'))
check('check: the reserve against the pre-tag manifest -> RESERVE IN AFTER 9 of 9', rc == 0 and buf.getvalue().startswith('RESERVE IN AFTER 9 of 9'))
mk_emu()
open(os.path.join(EMU, '_ShaderCache', 'PPSA21564', 'pipelines.bin'), 'w').write('changed')
man(os.path.join(TD, 'm_changed.tsv'))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = RV.check(os.path.join(RES, 'reserve.tsv'), os.path.join(TD, 'm_changed.tsv'))
check('check: a changed file -> RESERVE NOT IN AFTER, rc 1', rc == 1 and buf.getvalue().startswith('RESERVE NOT IN AFTER missing 1 of 9'))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = RV.cold(EMU)
check('cold: a full live folder -> COLD NOT, rc 1', rc == 1 and buf.getvalue().startswith('COLD NOT'))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = RV.move(EMU, RES)
check('move: the reserve dir exists -> RESERVE FAILED, nothing moved', rc == 1 and 'reserve dir exists' in buf.getvalue() and
      os.path.isdir(os.path.join(EMU, '_ShaderSeeds', 'PPSA21564')))
shutil.rmtree(RES)
mk_emu(seeds=False)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = RV.move(EMU, RES)
check('move: no seeds -> RESERVE FAILED (incomplete), nothing moved', rc == 1 and 'incomplete' in buf.getvalue() and not os.path.exists(RES) and
      os.path.isdir(os.path.join(EMU, '_ShaderCache', 'PPSA21564', 'variant_fixb26_fixb1b_fixf10_fixf19')))
mk_emu(variant=False)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = RV.move(EMU, RES)
check('move: no variant dir -> RESERVE FAILED (incomplete)', rc == 1 and 'incomplete' in buf.getvalue() and not os.path.exists(RES))
p = subprocess.run([sys.executable, os.path.join(HERE, 'reserve_f20l3.py')], capture_output=True, env=env0)
check('reserve_f20l3.py without arguments: usage rc 2, ASCII', p.returncode == 2 and all(b < 128 for b in p.stdout))
mk_emu()
p = subprocess.run([sys.executable, os.path.join(HERE, 'reserve_f20l3.py'), 'move', EMU, os.path.join(TD, 'reserve2')], capture_output=True,
                   env=env0)
check('reserve_f20l3.py move as a child with strict cp1250 (no PYTHONIOENCODING): rc 0, ASCII', p.returncode == 0 and
      all(b < 128 for b in p.stdout) and p.stdout.startswith(b'RESERVE MOVED'))
# --- go / launch / post refusals and dry runs
for bad in ('b32_s00', 'b32_s61', 'b32_s1', 'b32_pa3', 'b32_z0c0', 'b32_z0c6', 'b32_s01_r7', 'f20_v25', '', 'b32_z0b', 'b32_ppb', 'b32_pcb',
            'b32_pd', 'b32_pd2', 'b32_z0'):
    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l3.sh'), bad], capture_output=True, text=True)
    check('go: %r refused (usage)' % bad, p.returncode == 2)
    p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20l3.sh'), bad], capture_output=True, text=True)
    check('launch: %r refused (usage)' % bad, p.returncode == 2)
    p = subprocess.run([BASH, os.path.join(HERE, 'post_f20l3.sh'), bad], capture_output=True, text=True)
    check('post: %r refused (usage)' % bad, p.returncode == 2)
WANT = {'b32_pa': ('KYTY_DIAG_B32=1', '1'), 'b32_pa2': ('KYTY_DIAG_B32=1', '1'), 'b32_pa_r2': ('KYTY_DIAG_B32=1', '1'),
        'b32_s01': ('KYTY_DIAG_B32=1', '0'), 'b32_s60': ('KYTY_DIAG_B32=1', '0'), 'b32_s17_r3': ('KYTY_DIAG_B32=1', '0'),
        'b32_z0c1': ('KYTY_DIAG_B32=0', '0'), 'b32_z0c5_r1': ('KYTY_DIAG_B32=0', '0')}
for t, (kn, cold) in WANT.items():
    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l3.sh'), t], capture_output=True, text=True, env=dict(os.environ, F20L3_DRYRUN='1'))
    check('go dry run %s: knobs %s cold %s' % (t, kn, cold), p.returncode == 0 and ('knobs %s cold %s' % (kn, cold)) in p.stdout)
check('go: enter_scene gets KYTY_GPU_WALL=1 and the knobs positionally',
      'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 $KN > $OUT/run.txt' in go)
check('go: hold 330, stable 300, rec, attempts 1', 'SD=300; H=330' in go and '--rec --hold $H' in go and '--attempts 1' in go)
check('go: test binary and the installed S18 by the full sha256, pinned S18 copy',
      'TB=2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7' in go and
      'S18=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a' in go and
      'PINNED=C:/kyty/s288/bin/kyty_emulator_b3cee576.exe' in go and 'FS8' not in go)
check('go: manifest and copies include _ShaderSeeds (and _ShaderCache with replay/)', 'DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"' in go
      and '"_ShaderSeeds=$EMU/_ShaderSeeds"' in go)
check('go: the cold move after the copy and before the test binary install', go.index('COPIED="$COPIED $d"') <
      go.index('python $G/reserve_f20l3.py move') < go.index('INSTALLED=1\ncp "$BIN" "$GAME"'))
check('go: the reserve check after the manifest after, before the lock release in finish', go.index('manifest_fs4c.py $OUT/manifest_after.tsv') <
      go.index('python $G/reserve_f20l3.py check') < go.rindex('rm -f $LOCK; echo "lock released'))
check('go: no loader', 'b32_load.py' not in go and 'LOADMODE' not in go)
check('go: lock.log lines', 'echo "lock taken $T $(u)" >> $G/runs/lock.log' in go and go.count('echo "lock released $T $(u)" >> $G/runs/lock.log') == 2)
check('go: unsets KYTY_* and VK_LAYER_*', "for v in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'); do unset $v; done" in go)
# --- queue_f20l3.py reading
ISS = [dict(identifier='HPP-655', status='in_progress', executionRunId='r'), dict(identifier='HPP-557', status='blocked', executionRunId=None),
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
    check('queue %s (own HPP-655 out)' % want, rc == want_rc and buf.getvalue().strip().splitlines()[-1] == want)
Q.urllib.request.urlopen = keep_open
# --- runchk_f20l3.py (item 587 (g) debt)
_rf = os.path.join(TD, 'runchk.json')
for iss, rid, want_rc, want in ((dict(executionRunId='run-a', status='in_progress'), 'run-a', 0, 'RUN ALIVE'),
                                (dict(executionRunId=None, status='in_progress'), 'run-a', 1, 'RUN GONE'),
                                (dict(executionRunId='run-b', status='in_progress'), 'run-a', 1, 'RUN GONE'),
                                (dict(executionRunId='run-a', status='blocked'), 'run-a', 1, 'RUN GONE'),
                                (dict(executionRunId='run-a', status='in_progress'), '', 1, 'RUN GONE')):
    with open(_rf, 'w', encoding='ascii') as f:
        json.dump(iss, f)
    p = subprocess.run([sys.executable, os.path.join(HERE, 'runchk_f20l3.py'), '--fake', _rf], capture_output=True, text=True,
                       env=dict(os.environ, F20L3_RUN_ID=rid))
    check('runchk %s run %r want %r -> %s' % (iss['status'], iss['executionRunId'], rid, want), p.returncode == want_rc and p.stdout.startswith(want))
p = subprocess.run([sys.executable, os.path.join(HERE, 'runchk_f20l3.py'), '--fake', os.path.join(TD, 'none.json')], capture_output=True, text=True)
check('runchk: unreadable answer -> API ERROR rc 2', p.returncode == 2 and p.stdout.startswith('API ERROR'))
_ga = go.index('RS=$(python $G/runchk_f20l3.py)')
check('go: run check after procload and before the lock', go.index('procload.py --wait-s') < _ga < go.index('set -o noclobber'))
check('launch: passes F20L3_RUN_ID from PAPERCLIP_RUN_ID', 'F20L3_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup' in
      open(os.path.join(HERE, 'launch_f20l3.sh'), encoding='ascii').read())
for nm in ('b32_read.py', 'test_b32_read.py', 'sens_b32.py', 'm6_f20l3.py', 'go_f20l3.sh', 'launch_f20l3.sh', 'reserve_f20l3.py',
           'wait_f20l3.sh', 'post_f20l3.sh', 'queue_f20l3.py', 'guard_f20l3.py', 'watch_f20l3.py', 'enter_scene.py', 'test_tools_f20l3.py',
           'test_guard_f20l3.py', 'port_f20l3.py', 'edit_f20l3.py', 'edit_test_f20l3.py', 'edit_sens_f20l3.py', 'test_new_section.py',
           'test_add_section.py', 'refs_f20l3.py', 'runchk_f20l3.py', 'mk_seal_f20l3.py'):
    check('%s ASCII only' % nm, all(b < 128 for b in open(os.path.join(HERE, nm), 'rb').read()))
shutil.rmtree(TD, ignore_errors=True)
print('checks %d, failed %d' % (n[0], len(fails)))
if fails:
    print('FAILED:', fails)
    sys.exit(1)
print('ALL OK')
