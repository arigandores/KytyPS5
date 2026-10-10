"""Fixtures of the F34c chain (Track F link F34c, HPP-740; ROADMAP s122 item 673 (z)(2), 674, 676, 634 / 660 / 661): the dry-run plan of
go_f34c.sh for every tag (level, entry option, end, validation, knobs), refusals of go_f34c.sh and launch_f34c.sh (usage, repeat without its
times.txt line, the repeat cap of item 676 (l) = 4), the form linter --series = ALL OK, the SubTracker of enter_scene.py on a synthetic log,
the option defaults of enter_scene.py (old forms unchanged), ASCII of every script; strict cp1250 output; the last line is ALL OK.
Early-exit form (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
usage: python test_tools_f34c.py"""
import hashlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GO = os.path.join(HERE, 'go_f34c.sh')
LA = os.path.join(HERE, 'launch_f34c.sh')
BASH = 'C:/Program Files/Git/bin/bash.exe'
N = [0, 0]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='cp1250', errors='strict', line_buffering=True)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_f34c.py sha256 %s target go_f34c.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(GO)))


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
    print('%-4s %s' % ('ok' if cond else 'FAIL', name))
    return bool(cond)


def sh(script, args, env=None):
    e = dict(os.environ)
    e.update(env or {})
    r = subprocess.run([BASH, script] + args, capture_output=True, text=True, env=e)
    return r.returncode, (r.stdout + r.stderr)


ok = True
VKL = 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000'
KN = 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'
KK = 'KYTY_KEYS=@2170:j,@2460:j'
WV = '--emu-arg=--vulkan-validation --emu-arg=true'
plans = {
    'b6_w0': 'level underwater_aerial_garden entry --stable-draws 100 timeout 900 hold 310 end - rec %s knobs %s %s' % (WV, VKL, KN),
    'b6_v': 'level intro_next entry --natural --stable-draws 500 timeout 600 hold 600 end --proc-limit 600 --until-sublevel 600 rec --rec knobs %s %s' % (KK, KN),
    'b6_v2': 'level intro_next entry --natural --stable-draws 500 timeout 600 hold 600 end --proc-limit 600 --until-sublevel 600 rec --rec knobs %s %s' % (KK, KN),
    'b6_vl': 'level intro_next entry --entry-at-level --stable-draws 500 timeout 600 hold 600 end --proc-limit 600 --until-sublevel 600 rec --rec knobs %s' % KN,
    'b6_w': 'level intro_next entry --natural --stable-draws 500 timeout 1800 hold 1800 end --proc-limit 1800 --until-sublevel 300 rec %s knobs %s %s %s' % (WV, KK, VKL, KN),
    'b6_wl': 'level intro_next entry --entry-at-level --stable-draws 500 timeout 1800 hold 1800 end --proc-limit 1800 --until-sublevel 300 rec %s knobs %s %s' % (WV, VKL, KN),
}
for tag, want in plans.items():
    for t in (tag, tag + '_r1', tag + '_r4'):
        rc, out = sh(GO, [t], {'F34C_DRYRUN': '1'})
        line = [l for l in out.splitlines() if l.startswith('dryrun ')]
        base = tag
        ok &= check('go plan %s' % t, rc == 0 and line and line[0] == 'dryrun %s base %s %s' % (t, base, want))
for bad in ('b6_x', 'b6_v_r5', 'b6_v_r0', 'fs11_w', 'b6_v3', ''):
    rc, out = sh(GO, [bad] if bad else [], {'F34C_DRYRUN': '1'})
    ok &= check('go usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(LA, [bad] if bad else [], {'F34C_DRYRUN': '2'})
    ok &= check('launch usage rc 2 for %r' % bad, rc == 2)
tmp = tempfile.mkdtemp(prefix='f34ct_')
tm = os.path.join(tmp, 'times.txt')
envq = {'F34C_DRYRUN': '2', 'F34C_QUEUE_SKIP': '1', 'F34C_DISP_SKIP': '1', 'F34C_TIMES': tm, 'F34C_RUNS': os.path.join(tmp, 'runs')}
rc, out = sh(LA, ['b6_v'], envq)
ok &= check('launch b6_v dry-run 2 passes (rc %d %s)' % (rc, out.strip()[-40:]), rc == 0 and 'dryrun2 rep 0' in out)
rc, out = sh(LA, ['b6_v_r1'], envq)
ok &= check('launch repeat without F34C_REPEAT_OK -> rc 11', rc == 11)
e2 = dict(envq, F34C_REPEAT_OK='1')
rc, out = sh(LA, ['b6_v_r1'], e2)
ok &= check('launch repeat with F34C_REPEAT_OK and 0 repeats -> passes', rc == 0 and 'dryrun2 rep 1' in out)


def mkrun(name, launched=True):
    d = os.path.join(tmp, 'runs', name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'run.txt'), 'w') as f:
        f.write('--- attempt 1: launching\n' if launched else 'refused idle\n')


for nm in ('b6_v_r1', 'b6_w_r1.user_101010', 'b6_vl_r1'):
    mkrun(nm)
mkrun('b6_w_r2.busy_101010', launched=False)
rc, out = sh(LA, ['b6_v_r2'], e2)
ok &= check('launch 3 started repeats (busy one not counted) -> the 4th passes', rc == 0)
rc, out = sh(LA, ['b6_v_r1'], e2)
ok &= check('launch a repeat already counted is not counted twice', rc == 0)
mkrun('b6_wl_r1')
rc, out = sh(LA, ['b6_v_r2'], e2)
ok &= check('launch 4 started repeats -> the 5th refused rc 11', rc == 11)
ok &= check('repeat cap refusal written to times.txt', os.path.exists(tm) and 'repeat cap of the series reached' in open(tm).read())
shutil.rmtree(tmp, ignore_errors=True)
r = subprocess.run([sys.executable, 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py', '--series', HERE], capture_output=True, text=True)
ok &= check('form634_check.py --series %s: %s' % (HERE, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '-'),
            r.returncode == 0 and r.stdout.strip().endswith('ALL OK'))
first = [l for l in open(GO, encoding='ascii').read().splitlines() if l.strip() and not l.startswith('#')][0]
ok &= check('go first executable line is the form linter', first.startswith('python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series'))
first = [l for l in open(LA, encoding='ascii').read().splitlines() if l.strip() and not l.startswith('#')][0]
ok &= check('launch first executable line is the form linter', first.startswith('python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series'))
src = open(GO, encoding='ascii').read()
ok &= check('go: no install of a binary (no cp to kyty_emulator.exe)', 'cp "$BIN"' not in src and 'cp "$PINNED"' not in src)
ok &= check('go: the guard scan right after the lock line, before the manifest',
            src.index('lock taken $T') < src.index('guard_f34c.py scan)') < src.index('manifest_fs4c.py $OUT/manifest_before.tsv'))
ok &= check('go: no KYTY_GPU_CHECKPOINTS, KYTY_GAME_PATCH, KYTY_FIX_ in knobs',
            all(k not in src.split('# usage')[1] for k in ('KYTY_GPU_CHECKPOINTS=', 'KYTY_GAME_PATCH=', 'KYTY_FIX_')))
# enter_scene.py: options and SubTracker
spec = importlib.util.spec_from_file_location('es_under_test', os.path.join(HERE, 'enter_scene.py'))
ES = importlib.util.module_from_spec(spec)
sys.path.insert(0, HERE)
spec.loader.exec_module(ES)
d = tempfile.mkdtemp(prefix='f34cs_')
lp = os.path.join(d, 'log.txt')
with open(lp, 'w', newline='\n') as f:
    for n in range(1, 101):
        f.write('FrameTrace: n=%d dt_us=1\n' % n)
    f.write('GuestOut: SubLevelLocator sublevel_locator_space [x], state changed 6->7\n')
for k, want in ((0, False), (5, False)):
    st = ES.SubTracker(__import__('pathlib').Path(lp), k)
    ok &= check('SubTracker K %d: no 7->6 line -> not done' % k, st.done() is want and st.seen is False)
with open(lp, 'a', newline='\n') as f:
    f.write('GuestOut: SubLevelLocator sublevel_locator_space [x], state changed 7->6\n')
    for n in range(101, 106):
        f.write('FrameTrace: n=%d dt_us=1\n' % n)
st = ES.SubTracker(__import__('pathlib').Path(lp), 4)
ok &= check('SubTracker K 4: n_sw 101, last 105 -> done', st.done() is True and st.n_sw == 101 and st.n_last == 105)
st = ES.SubTracker(__import__('pathlib').Path(lp), 5)
ok &= check('SubTracker K 5: last 105 < 106 -> not done', st.done() is False and st.n_sw == 101)
with open(lp, 'a', newline='\n') as f:
    f.write('FrameTrace: n=106 dt_us=1\n')
ok &= check('SubTracker K 5: the next line n 106 -> done (incremental tail)', st.done() is True)
shutil.rmtree(d, ignore_errors=True)
h = subprocess.run([sys.executable, os.path.join(HERE, 'enter_scene.py'), '--help'], capture_output=True, text=True).stdout
ok &= check('enter_scene --help names --natural, --until-sublevel, --proc-limit',
            all(k in h for k in ('--natural', '--until-sublevel', '--proc-limit')))
es = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
ok &= check('enter_scene: options off by default', "'--until-sublevel', type=int, default=0" in es and "'--proc-limit', type=float, default=0" in es)
ok &= check('enter_scene: natural env has no KYTY_GUEST_ARGS', 'elif options.natural:' in es and
            "KYTY_QUEUE_TRACE='1')\n" in es.split('elif options.natural:')[1][:400])
for nm in sorted(os.listdir(HERE)):
    if nm.endswith(('.sh', '.py')) and not nm.startswith('fx_'):
        raw = open(os.path.join(HERE, nm), 'rb').read()
        if nm in ('enter_scene.py',):
            continue
        ok &= check('ASCII only: %s' % nm, all(c < 128 for c in raw))
print('checks %d failed %d' % (N[0], N[1]))
print('ALL OK' if ok and N[1] == 0 else 'FAILED')
sys.exit(0 if ok and N[1] == 0 else 1)
