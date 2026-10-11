"""Fixtures of the F38c chain (Track F link F38c, HPP-765; ROADMAP s122 item 691 (d)(4), 634 / 660 / 661): the dry-run plan of go_f38c.sh
for f25_v (level, stable draws, timeout, hold, video, knobs: KYTY_FIX_F25=1 the only KYTY_FIX_ value, no KYTY_TEST_*), refusals of
go_f38c.sh, launch_f38c.sh and post_f38c.sh (usage; a repeat without the lead's item - F38C_REPEAT_OK), the form linter --series = ALL OK,
the first executable line of go / launch = the linter, the install / return of the binary (the F38a copy 5a14a111 installed after the copies
of the caches, the pinned FS12 46892c20 copy returned in finish; the sha256 of both copies on disk = the literals), the own issue of queue /
runchk / chk = HPP-765, the tempo tool = the FS12c one with the names moved, the enter_scene.py ROOT and CLOSE_WAIT_S, ASCII of every
script; the F33e debt (item 683 (d)): post_f38c.sh takes the plan by the line starting 'dryrun ' (checked with F38C_POST_PLANONLY=1); the
pair with the fs12_v sheet of FS12c; strict cp1250 output; the last line is ALL OK.  Port of C:/kyty/f287/fs12c/test_tools_fs12c.py.
Early-exit form (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
usage: python test_tools_f38c.py"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GO = os.path.join(HERE, 'go_f38c.sh')
LA = os.path.join(HERE, 'launch_f38c.sh')
PO = os.path.join(HERE, 'post_f38c.sh')
BASH = 'C:/Program Files/Git/bin/bash.exe'
N = [0, 0]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='cp1250', errors='strict', line_buffering=True)
TB = '5a14a1118e041c85257d7fd6faa8c8c98cea5c1c5a17ae7a4eff6707ec204754'
FS12 = '46892c20080819ae090598511748265dfbac31f303a02f1804e5b10db8acae26'
LINT = 'python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f38c'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


print('suite test_tools_f38c.py sha256 %s target go_f38c.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(GO)))


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
    print('%-4s %s' % ('ok' if cond else 'FAIL', name))
    return bool(cond)


def sh(script, args, env=None):
    e = dict(os.environ)
    for k in list(e):
        if k.startswith('F38C_'):
            del e[k]
    e.update(env or {})
    r = subprocess.run([BASH, script] + args, capture_output=True, text=True, env=e)
    return r.returncode, (r.stdout + r.stderr)


ok = True
WANT = {'f25_v': 'level underwater_aerial_garden sd 300 timeout 480 hold 330 rec --rec knobs KYTY_FIX_F25=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'}
for b, w in sorted(WANT.items()):
    for t in (b, b + '_r1', b + '_r3'):
        rc, out = sh(GO, [t], {'F38C_DRYRUN': '1'})
        line = [l for l in out.splitlines() if l.startswith('dryrun ')]
        ok &= check('go plan %s' % t, rc == 0 and line and line[0] == 'dryrun %s base %s %s' % (t, b, w))
    ok &= check('plan %s: no KYTY_TEST_' % b, 'KYTY_TEST_' not in w)
    ok &= check('plan %s: KYTY_FIX_ only KYTY_FIX_F25=1' % b, w.count('KYTY_FIX_') == 1 and 'KYTY_FIX_F25=1' in w)
    ok &= check('plan %s: no KYTY_GAME_PATCH, no validation' % b, 'KYTY_GAME_PATCH' not in w and 'vulkan-validation' not in w)
rc, out = sh(GO, ['f25_v'], {'F38C_DRYRUN': '1'})
ok &= check('go dry-run output: first line is the linter line ALL OK, the plan is a later line (the F33e trap)',
            out.splitlines()[0].strip() == 'ALL OK' and out.splitlines()[1].startswith('dryrun f25_v '))
for b in ('f25_v', 'f25_v_r2'):
    rc, out = sh(PO, [b], {'F38C_POST_PLANONLY': '1'})
    lines = out.splitlines()
    ok &= check('post plan of %s is the dryrun line (not the linter line), plan-w no (rc %d: %s)' % (b, rc, out.strip()[-60:]),
                rc == 0 and len(lines) == 2 and lines[0].startswith('plan dryrun %s base ' % b) and lines[1] == 'plan-w no')
po = open(PO, encoding='ascii').read()
ok &= check("post: the plan is taken by grep '^dryrun ', not by the first line",
            "bash $G/go_f38c.sh $T 2>&1 | grep '^dryrun ' | head -1)" in po and 'go_f38c.sh $T 2>&1 | head -1' not in po)
ok &= check('post: the plan-only exit is before the lock check (reads nothing)',
            po.index('F38C_POST_PLANONLY') < po.index('[ -e C:/kyty/SEALED_RUN.lock ]') < po.index('f38c_read.py $T'))
ok &= check('post: pair of f25_v with the fs12_v sheet of FS12c', 'C:/kyty/f287/fs12c/runs/fs12_v/sheet_fs12_v.png' in po and 'pair_${T}_fs12_v.png' in po)
ok &= check('on disk: the fs12_v sheet exists', os.path.exists('C:/kyty/f287/fs12c/runs/fs12_v/sheet_fs12_v.png'))
for bad in ('f25_x', 'f25_v_r4', 'f25_v_r0', 'fs12_v', 'f21_v', ''):
    rc, out = sh(GO, [bad] if bad else [], {'F38C_DRYRUN': '1'})
    ok &= check('go usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(LA, [bad] if bad else [], {'F38C_DRYRUN': '2'})
    ok &= check('launch usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(PO, [bad] if bad else [], {'F38C_POST_PLANONLY': '1'})
    ok &= check('post usage rc 2 for %r' % bad, rc == 2)
tmp = tempfile.mkdtemp(prefix='f38ct_')
tm = os.path.join(tmp, 'times.txt')
envq = {'F38C_DRYRUN': '2', 'F38C_QUEUE_SKIP': '1', 'F38C_DISP_SKIP': '1', 'F38C_TIMES': tm}
for t in ('f25_v',):
    rc, out = sh(LA, [t], envq)
    ok &= check('launch %s dry-run 2 passes (rc %d %s)' % (t, rc, out.strip()[-40:]), rc == 0 and 'dryrun2 rep 0' in out)
    rc, out = sh(LA, [t + '_r1'], envq)
    ok &= check('launch repeat %s_r1 without F38C_REPEAT_OK -> rc 11' % t, rc == 11)
    rc, out = sh(LA, [t + '_r1'], dict(envq, F38C_REPEAT_OK='1'))
    ok &= check('launch repeat %s_r1 with F38C_REPEAT_OK -> passes' % t, rc == 0 and 'dryrun2 rep 1' in out)
shutil.rmtree(tmp, ignore_errors=True)
r = subprocess.run([sys.executable, 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py', '--series', HERE], capture_output=True, text=True)
ok &= check('form634_check.py --series %s: %s' % (HERE, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '-'),
            r.returncode == 0 and r.stdout.strip().endswith('ALL OK'))
for p in (GO, LA):
    first = [l for l in open(p, encoding='ascii').read().splitlines() if l.strip() and not l.startswith('#')][0]
    ok &= check('%s first executable line is the form linter' % os.path.basename(p), first.startswith(LINT))
src = open(GO, encoding='ascii').read()
body = src.split('# usage')[1]
ok &= check('go: TB literal = 5a14a111', 'TB=' + TB in src)
ok &= check('go: FS12 literal = 46892c20', 'FS12=' + FS12 in src)
ok &= check('go: BIN and PINNED paths', 'BIN=$F/bin/kyty_emulator_5a14a111.exe' in src and 'PINNED=$F/bin/kyty_emulator_46892c20.exe' in src)
ok &= check('on disk: sha256 of the F38a copy = 5a14a111', sha('C:/kyty/f287/bin/kyty_emulator_5a14a111.exe') == TB)
ok &= check('on disk: sha256 of the pinned FS12 copy = 46892c20', sha('C:/kyty/f287/bin/kyty_emulator_46892c20.exe') == FS12)
ok &= check('on disk: the F38a copy = the F38a build output (binary_f38a.out.txt)',
            sha('C:/kyty/f287/f38a/build/install/kyty_emulator.exe') == TB)
ok &= check('go: the guard scan right after the lock line, before the manifest',
            src.index('lock taken $T') < src.index('guard_f38c.py scan)') < src.index('hold_f38c.py check)')
            < src.index('manifest_fs4c.py $OUT/manifest_before.tsv'))
ok &= check('go: no guard scan / hold check before the lock (item 660 (d)(1))',
            src.index('guard_f38c.py scan)') > src.index('set -o noclobber') and src.index('hold_f38c.py check)') > src.index('set -o noclobber'))
ok &= check('go: install of the F38a copy after the copies of the caches and after INSTALLED=1',
            src.index('cp -a "$SRC" "$OUT/before_$d"') < src.index('INSTALLED=1\ncp "$BIN" "$GAME"') < src.index('enter_scene.py $T'))
ok &= check('go: the return of the pinned FS12 copy in finish, before installed_after',
            src.index('cp "$PINNED" "$GAME"') < src.index('sha "$GAME" > $OUT/installed_after.txt') < src.index('trap finish EXIT'))
ok &= check('go: installed_after must be FS12', '[ "$(cat $OUT/installed_after.txt)" = "$FS12" ] || { OK=0;' in src)
ok &= check('go: installed before the tag must be FS12', '[ "$WANT" = "$FS12" ] ||' in src)
ok &= check('go: KYTY_FIX_ in the knobs only KYTY_FIX_F25=1',
            body.count('KYTY_FIX_') == body.count('KYTY_FIX_F25=1') + body.count('KYTY_FIX_* except'))
ok &= check('go: no KYTY_GPU_CHECKPOINTS=, KYTY_GAME_PATCH=, KYTY_TEST_*= in the body',
            all(k not in body for k in ('KYTY_GPU_CHECKPOINTS=', 'KYTY_GAME_PATCH=', 'KYTY_TEST_')))
ok &= check('go: shell KYTY_* and VK_LAYER_* unset before the call', "for v in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'); do unset $v; done" in src)
ok &= check('go: the env after the unset is written', 'env_shell_after_unset.txt' in src)
ok &= check('go: lock line names HPP-765', 'echo "F38c HPP-765 go_f38c.sh $T pid $$ $(u)" > $LOCK' in src)
for nm in ('queue_f38c.py', 'runchk_f38c.py'):
    ok &= check('%s own issue HPP-765' % nm, "OWN = 'HPP-765'" in open(os.path.join(HERE, nm), encoding='ascii').read())
ok &= check('chk_f38c.sh comments of HPP-765', '/api/issues/HPP-765/comments' in open(os.path.join(HERE, 'chk_f38c.sh'), encoding='ascii').read())
es = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
ok &= check('enter_scene: ROOT = f287/f38c', "ROOT = pathlib.Path('C:/kyty/f287/f38c')" in es)
ok &= check('enter_scene: CLOSE_WAIT_S = 40 (the harness timeout of the exit, form b4_v)', 'CLOSE_WAIT_S = 40 ' in es)
a = open('C:/kyty/f287/fs12c/tempo_fs12c.py', 'rb').read().replace(b'\r\n', b'\n')
for x, y in ((b'fs12c', b'f38c'), (b'FS12C', b'F38C'), (b'FS12c', b'F38c'), (b'HPP-752', b'HPP-765')):
    a = a.replace(x, y)
b = open(os.path.join(HERE, 'tempo_f38c.py'), 'rb').read()
ok &= check('tempo_f38c.py = tempo_fs12c.py with the names moved (+ one header line)', b.split(b'\n', 1)[1] == a)
for nm in sorted(os.listdir(HERE)):
    if nm.endswith(('.sh', '.py')) and not nm.startswith('fx_'):
        raw = open(os.path.join(HERE, nm), 'rb').read()
        if nm in ('enter_scene.py',):
            continue
        ok &= check('ASCII only: %s' % nm, all(c < 128 for c in raw))
print('checks %d failed %d' % (N[0], N[1]))
print('ALL OK' if ok and N[1] == 0 else 'FAILED')
sys.exit(0 if ok and N[1] == 0 else 1)
