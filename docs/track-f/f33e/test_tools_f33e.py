"""Fixtures of the F33e chain (Track F link F33e, HPP-746; ROADMAP s122 item 675 (d)(4), 682, 634 / 660 / 661): the dry-run plan of
go_f33e.sh (level, stable draws, timeout, hold, video, knobs: KYTY_FIX_F21=1 and nothing else of KYTY_FIX_*), refusals of go_f33e.sh and
launch_f33e.sh (usage; a repeat without the lead's item - F33E_REPEAT_OK), the form linter --series = ALL OK, the install / return of the
binary in go_f33e.sh (the F33c copy 2b393af8 installed after the copies of the caches, the pinned FS11 ea51ae80 copy returned in finish;
the sha256 of both copies on disk = the literals), the own issue of queue / runchk = HPP-746, the tempo tool = the FS11c one with the names
moved, the enter_scene.py ROOT, ASCII of every script; strict cp1250 output; the last line is ALL OK.  Port of
C:/kyty/f287/f34c/test_tools_f34c.py.  Early-exit form (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
usage: python test_tools_f33e.py"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GO = os.path.join(HERE, 'go_f33e.sh')
LA = os.path.join(HERE, 'launch_f33e.sh')
BASH = 'C:/Program Files/Git/bin/bash.exe'
N = [0, 0]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='cp1250', errors='strict', line_buffering=True)
TB = '2b393af8e9c1a85ad6d24bc47a3bc08f5cad2dcdd59b8f6a1ed7293859d0c612'
FS11 = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


print('suite test_tools_f33e.py sha256 %s target go_f33e.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(GO)))


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
WANT = 'level underwater_aerial_garden sd 300 timeout 480 hold 330 rec --rec knobs KYTY_FIX_F21=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'
for t in ('f21_v', 'f21_v_r1', 'f21_v_r3'):
    rc, out = sh(GO, [t], {'F33E_DRYRUN': '1'})
    line = [l for l in out.splitlines() if l.startswith('dryrun ')]
    ok &= check('go plan %s' % t, rc == 0 and line and line[0] == 'dryrun %s base f21_v %s' % (t, WANT))
for bad in ('f21_x', 'f21_v_r4', 'f21_v_r0', 'fs11_v', 'b4_v', ''):
    rc, out = sh(GO, [bad] if bad else [], {'F33E_DRYRUN': '1'})
    ok &= check('go usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(LA, [bad] if bad else [], {'F33E_DRYRUN': '2'})
    ok &= check('launch usage rc 2 for %r' % bad, rc == 2)
tmp = tempfile.mkdtemp(prefix='f33et_')
tm = os.path.join(tmp, 'times.txt')
envq = {'F33E_DRYRUN': '2', 'F33E_QUEUE_SKIP': '1', 'F33E_DISP_SKIP': '1', 'F33E_TIMES': tm}
rc, out = sh(LA, ['f21_v'], envq)
ok &= check('launch f21_v dry-run 2 passes (rc %d %s)' % (rc, out.strip()[-40:]), rc == 0 and 'dryrun2 rep 0' in out)
rc, out = sh(LA, ['f21_v_r1'], envq)
ok &= check('launch repeat without F33E_REPEAT_OK -> rc 11', rc == 11)
rc, out = sh(LA, ['f21_v_r1'], dict(envq, F33E_REPEAT_OK='1'))
ok &= check('launch repeat with F33E_REPEAT_OK -> passes', rc == 0 and 'dryrun2 rep 1' in out)
shutil.rmtree(tmp, ignore_errors=True)
r = subprocess.run([sys.executable, 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py', '--series', HERE], capture_output=True, text=True)
ok &= check('form634_check.py --series %s: %s' % (HERE, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '-'),
            r.returncode == 0 and r.stdout.strip().endswith('ALL OK'))
for p in (GO, LA):
    first = [l for l in open(p, encoding='ascii').read().splitlines() if l.strip() and not l.startswith('#')][0]
    ok &= check('%s first executable line is the form linter' % os.path.basename(p),
                first.startswith('python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f33e'))
src = open(GO, encoding='ascii').read()
body = src.split('# usage')[1]
ok &= check('go: TB literal = 2b393af8', 'TB=' + TB in src)
ok &= check('go: FS11 literal = ea51ae80', 'FS11=' + FS11 in src)
ok &= check('go: BIN and PINNED paths', 'BIN=$F/bin/kyty_emulator_2b393af8.exe' in src and 'PINNED=$F/bin/kyty_emulator_ea51ae80.exe' in src)
ok &= check('on disk: sha256 of the F33c copy = 2b393af8', sha('C:/kyty/f287/bin/kyty_emulator_2b393af8.exe') == TB)
ok &= check('on disk: sha256 of the pinned FS11 copy = ea51ae80', sha('C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe') == FS11)
ok &= check('go: the guard scan right after the lock line, before the manifest',
            src.index('lock taken $T') < src.index('guard_f33e.py scan)') < src.index('manifest_fs4c.py $OUT/manifest_before.tsv'))
ok &= check('go: install of the F33c copy after the copies of the caches and after INSTALLED=1',
            src.index('cp -a "$SRC" "$OUT/before_$d"') < src.index('INSTALLED=1\ncp "$BIN" "$GAME"') < src.index('enter_scene.py $T'))
ok &= check('go: the return of the pinned FS11 copy in finish, before installed_after',
            src.index('cp "$PINNED" "$GAME"') < src.index('sha "$GAME" > $OUT/installed_after.txt') < src.index('trap finish EXIT'))
ok &= check('go: installed_after must be FS11', '[ "$(cat $OUT/installed_after.txt)" = "$FS11" ] || { OK=0;' in src)
ok &= check('go: installed before the tag must be FS11', '[ "$WANT" = "$FS11" ] ||' in src)
ok &= check('go: knobs - KYTY_FIX_F21=1 is the only KYTY_FIX_ value',
            'KX="KYTY_FIX_F21=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0"' in src
            and body.count('KYTY_FIX_') == body.count('KYTY_FIX_F21=1') + body.count('KYTY_FIX_* except'))
ok &= check('go: no KYTY_GPU_CHECKPOINTS=, KYTY_GAME_PATCH=, KYTY_TEST_ in the body',
            all(k not in body for k in ('KYTY_GPU_CHECKPOINTS=', 'KYTY_GAME_PATCH=', 'KYTY_TEST_EXITFATAL=')))
ok &= check('go: shell KYTY_* and VK_LAYER_* unset before the call', "for v in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'); do unset $v; done" in src)
ok &= check('go: lock line names HPP-746', 'echo "F33e HPP-746 go_f33e.sh $T pid $$ $(u)" > $LOCK' in src)
for nm, own in (('queue_f33e.py', "OWN = 'HPP-746'"), ('runchk_f33e.py', "OWN = 'HPP-746'")):
    ok &= check('%s own issue HPP-746' % nm, own in open(os.path.join(HERE, nm), encoding='ascii').read())
es = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
ok &= check('enter_scene: ROOT = f287/f33e', "ROOT = pathlib.Path('C:/kyty/f287/f33e')" in es)
ok &= check('enter_scene: CLOSE_WAIT_S = 40 (the harness timeout of the exit, form b4_v)', 'CLOSE_WAIT_S = 40 ' in es)
a = open('C:/kyty/f287/fs11c/tempo_fs11c.py', 'rb').read().replace(b'\r\n', b'\n')
for x, y in ((b'fs11c', b'f33e'), (b'FS11C', b'F33E'), (b'FS11c', b'F33e'), (b'HPP-716', b'HPP-746')):
    a = a.replace(x, y)
b = open(os.path.join(HERE, 'tempo_f33e.py'), 'rb').read()
ok &= check('tempo_f33e.py = tempo_fs11c.py with the names moved (+ one header line)', b.split(b'\n', 1)[1] == a)
for nm in sorted(os.listdir(HERE)):
    if nm.endswith(('.sh', '.py')) and not nm.startswith('fx_'):
        raw = open(os.path.join(HERE, nm), 'rb').read()
        if nm in ('enter_scene.py',):
            continue
        ok &= check('ASCII only: %s' % nm, all(c < 128 for c in raw))
print('checks %d failed %d' % (N[0], N[1]))
print('ALL OK' if ok and N[1] == 0 else 'FAILED')
sys.exit(0 if ok and N[1] == 0 else 1)
