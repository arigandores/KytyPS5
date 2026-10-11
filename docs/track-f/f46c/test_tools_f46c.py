"""Fixtures of the F46c chain (Track F link F46c, HPP-800; ROADMAP s122 item 702 (g), 711, 714, 716, 634 / 660 / 661): the dry-run plan
of go_f46c.sh for every tag form (level, stable draws, timeout, hold, video; knobs of item 702 (g)(1)-(2): the common
KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1 KYTY_DCC_TRACE=1, KYTY_FIX_F26 0 / 1, KYTY_F26_TINT 1 / 2 with the key of S<k> taken by next_f46c.py --key
from the f26s_1 json; no KYTY_TEST_*, no KYTY_GAME_PATCH, no other KYTY_FIX_*), a tint tag without a settled f26s_1 is refused (rc 7), a
tint tag of an event of class 'kept why=layers' is refused (rc 8); refusals of go / launch / post (usage); launch: the machine rule of
next_f46c.py (order rc 7, repeat rc 11, budget rc 12 writes SERIES_STOP), dry-run 2 passes for f26s_0 on an empty series; the form linter
--series = ALL OK; the first executable line of go / launch = the linter; the install / return of the binary (the T copy 9c1b268f
installed after the copies of the caches, the pinned FS13 abab2196 copy returned in finish; sha256 of both copies on disk = the literals;
the T copy = the F46a build output); the machine rule is checked before the lock in go; the own issue of queue / runchk / chk = HPP-800;
tempo_f46c.py = tempo_f44c.py with the names moved; the enter_scene.py ROOT and CLOSE_WAIT_S; post_f46c.sh takes the plan by the line
starting 'dryrun ' (F46C_POST_PLANONLY=1), calls f46c_vid.py --frames and next_f46c.py --plan after f26s_1; ASCII of every script;
strict cp1250 output; the last line is ALL OK.  Port of C:/kyty/f287/f44c/test_tools_f44c.py.  Early-exit form.  ASCII only.
usage: python test_tools_f46c.py"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GO = os.path.join(HERE, 'go_f46c.sh')
LA = os.path.join(HERE, 'launch_f46c.sh')
PO = os.path.join(HERE, 'post_f46c.sh')
BASH = 'C:/Program Files/Git/bin/bash.exe'
N = [0, 0]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='cp1250', errors='strict', line_buffering=True)
TB = '9c1b268ffffebcbf26e3ce33de94fb24c9b555fe89441fafcf40b7197d03ae69'
FS13 = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
LINT = 'python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f46c'
KC = 'KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1 KYTY_DCC_TRACE=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'
DCC = ['0000000571006000', '0000000570aee000', '0000000570b24000', '000000056d898000']


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


print('suite test_tools_f46c.py sha256 %s target go_f46c.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(GO)))


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
    print('%-4s %s' % ('ok' if cond else 'FAIL', name))
    return bool(cond)


def sh(script, args, env=None):
    e = dict(os.environ)
    for k in list(e):
        if k.startswith('F46C_'):
            del e[k]
    e.update(env or {})
    r = subprocess.run([BASH, script] + args, capture_output=True, text=True, env=e)
    return r.returncode, (r.stdout + r.stderr)


def runs_dir(classes, statuses=('ADMITTED', 'ADMITTED', 'ADMITTED')):
    d = tempfile.mkdtemp(prefix='f46ct_')
    for t, st in zip(('f26s_0', 'f26s_1', 'f26s_1b'), statuses):
        if st is None:
            continue
        os.makedirs(os.path.join(d, t))
        ev = [dict(k=k + 1, found=True, cls=classes[k], no_apply=False, dcc=DCC[k]) for k in range(4)]
        json.dump(dict(status=st, events=ev), open(os.path.join(d, t, 'read.json'), 'w'))
    return d


ok = True
COMMON = 'level underwater_aerial_garden sd 300 timeout 480 hold 330 rec --rec knobs '
RD = runs_dir(['kept_applied', 'kept why=decode', 'kept_applied', 'kept why=layers'])
WANT = {'f26s_0': 'KYTY_FIX_F26=0 ' + KC, 'f26s_1': 'KYTY_FIX_F26=1 ' + KC, 'f26s_1b': 'KYTY_FIX_F26=1 ' + KC,
        'f26s_t1': 'KYTY_FIX_F26=1 KYTY_F26_TINT=1 KYTY_F26_TINT_DCC=0x571006000 ' + KC,
        'f26s_c1': 'KYTY_FIX_F26=1 KYTY_F26_TINT=2 KYTY_F26_TINT_DCC=0x571006000 ' + KC,
        'f26s_t2': 'KYTY_FIX_F26=1 KYTY_F26_TINT=1 KYTY_F26_TINT_DCC=0x570aee000 ' + KC,
        'f26s_c3': 'KYTY_FIX_F26=1 KYTY_F26_TINT=2 KYTY_F26_TINT_DCC=0x570b24000 ' + KC}
for b, w in sorted(WANT.items()):
    for t in (b, b + '_r1', b + '_r3'):
        rc, out = sh(GO, [t], {'F46C_DRYRUN': '1', 'F46C_RUNS': RD})
        line = [l for l in out.splitlines() if l.startswith('dryrun ')]
        ok &= check('go plan %s (%s)' % (t, line[:1]), rc == 0 and line and line[0] == 'dryrun %s base %s %s%s' % (t, b, COMMON, w))
    ok &= check('plan %s: no KYTY_TEST_, no KYTY_GAME_PATCH, no validation; KYTY_FIX_ only KYTY_FIX_F26' % b,
                'KYTY_TEST_' not in w and 'KYTY_GAME_PATCH' not in w and 'vulkan-validation' not in w and w.count('KYTY_FIX_') == 1 and
                'KYTY_FIX_F26=' in w)
rc, out = sh(GO, ['f26s_t4'], {'F46C_DRYRUN': '1', 'F46C_RUNS': RD})
ok &= check('go t4 of a "kept why=layers" event refused rc 8 (%s)' % out.strip()[-60:], rc == 8)
RD0 = runs_dir(['kept_applied'] * 4, statuses=('ADMITTED', None, None))
rc, out = sh(GO, ['f26s_t1'], {'F46C_DRYRUN': '1', 'F46C_RUNS': RD0})
ok &= check('go t1 before f26s_1 is settled refused rc 7', rc == 7)
rc, out = sh(GO, ['f26s_0'], {'F46C_DRYRUN': '1'})
ok &= check('go dry-run output: first line is the linter line ALL OK, the plan is a later line',
            out.splitlines()[0].strip() == 'ALL OK' and out.splitlines()[1].startswith('dryrun f26s_0 '))
for b in ('f26s_0', 'f26s_c2_r1'):
    rc, out = sh(PO, [b], {'F46C_POST_PLANONLY': '1'})
    lines = out.splitlines()
    ok &= check('post plan of %s is the dryrun line, plan-w no (rc %d: %s)' % (b, rc, out.strip()[-60:]),
                rc == 0 and len(lines) == 2 and lines[0].startswith('plan dryrun %s base ' % b) and lines[1] == 'plan-w no')
po = open(PO, encoding='ascii').read()
ok &= check("post: the plan is taken by grep '^dryrun '", "bash $G/go_f46c.sh $T 2>&1 | grep '^dryrun ' | head -1)" in po)
ok &= check('post: the plan-only exit is before the lock check (reads nothing)',
            po.index('F46C_POST_PLANONLY') < po.index('[ -e C:/kyty/SEALED_RUN.lock ]') < po.index('f46c_read.py $T'))
ok &= check('post: frames table before the reader, next plan after f26s_1',
            po.index('f46c_vid.py --frames $T') < po.index('f46c_read.py $T --json') < po.index('next_f46c.py --plan'))
for bad in ('f26s_2', 'f26s_t5', 'f26s_0_r4', 'f29_v', 'f26s_c0', ''):
    rc, out = sh(GO, [bad] if bad else [], {'F46C_DRYRUN': '1'})
    ok &= check('go usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(LA, [bad] if bad else [], {'F46C_DRYRUN': '2'})
    ok &= check('launch usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(PO, [bad] if bad else [], {'F46C_POST_PLANONLY': '1'})
    ok &= check('post usage rc 2 for %r' % bad, rc == 2)
tmp = tempfile.mkdtemp(prefix='f46ct_')
tm = os.path.join(tmp, 'times.txt')
er = os.path.join(tmp, 'runs')
os.makedirs(er)
envq = {'F46C_DRYRUN': '2', 'F46C_QUEUE_SKIP': '1', 'F46C_DISP_SKIP': '1', 'F46C_TIMES': tm, 'F46C_RUNS': er}
rc, out = sh(LA, ['f26s_0'], envq)
ok &= check('launch f26s_0 on an empty series: dry-run 2 passes (rc %d %s)' % (rc, out.strip()[-50:]), rc == 0 and 'dryrun2 MAY f26s_0' in out)
rc, out = sh(LA, ['f26s_1'], envq)
ok &= check('launch f26s_1 before f26s_0: rc 7, times line', rc == 7 and 'machine rule' in open(tm).read())
rc, out = sh(LA, ['f26s_0_r1'], envq)
ok &= check('launch f26s_0_r1 without NOT_ADMITTED: rc 11', rc == 11)
open(os.path.join(er, 'lock.log'), 'w').write('lock taken f26s_0 2026-10-11T10:00:00Z\nlock released f26s_0 2026-10-11T12:30:01Z\n')
sstop = os.path.join(HERE, 'SERIES_STOP')
had = os.path.exists(sstop)
rc, out = sh(LA, ['f26s_0'], envq)
ok &= check('launch with lock sum 150 min 1 s: rc 12 (budget, item 716)', rc == 12 and 'BUDGET' in out)
if os.path.exists(sstop) and not had:
    ok &= check('budget refusal wrote SERIES_STOP', 'lock budget' in open(sstop).read())
    os.remove(sstop)
shutil.rmtree(tmp, ignore_errors=True)
for d in (RD, RD0):
    shutil.rmtree(d, ignore_errors=True)
r = subprocess.run([sys.executable, 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py', '--series', HERE], capture_output=True, text=True)
ok &= check('form634_check.py --series %s: %s' % (HERE, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '-'),
            r.returncode == 0 and r.stdout.strip().endswith('ALL OK'))
for p in (GO, LA):
    first = [l for l in open(p, encoding='ascii').read().splitlines() if l.strip() and not l.startswith('#')][0]
    ok &= check('%s first executable line is the form linter' % os.path.basename(p), first.startswith(LINT))
src = open(GO, encoding='ascii').read()
body = src.split('# usage')[1]
ok &= check('go: TB literal = 9c1b268f', 'TB=' + TB in src)
ok &= check('go: INST literal = FS13 abab2196', 'INST=' + FS13 in src)
ok &= check('go: no FS12 46892c20 / F44a d760708d literal left', '46892c20' not in src and 'd760708d' not in src)
ok &= check('go: BIN and PINNED paths', 'BIN=$F/bin/kyty_emulator_9c1b268f.exe' in src and 'PINNED=$F/bin/kyty_emulator_abab2196.exe' in src)
ok &= check('on disk: sha256 of the T copy = 9c1b268f', sha('C:/kyty/f287/bin/kyty_emulator_9c1b268f.exe') == TB)
ok &= check('on disk: sha256 of the pinned FS13 copy = abab2196', sha('C:/kyty/f287/bin/kyty_emulator_abab2196.exe') == FS13)
ok &= check('on disk: the T copy = the F46a build output (f46a/build/install)', sha('C:/kyty/f287/f46a/build/install/kyty_emulator.exe') == TB)
ok &= check('go: the machine rule before the lock and before procload',
            src.index('next_f46c.py --may $T') < src.index('procload.py --wait-s') < src.index('set -o noclobber'))
ok &= check('go: the guard scan right after the lock line, before the manifest',
            src.index('lock taken $T') < src.index('guard_f46c.py scan)') < src.index('hold_f46c.py check)')
            < src.index('manifest_fs4c.py $OUT/manifest_before.tsv'))
ok &= check('go: install of the T copy after the copies of the caches',
            src.index('cp -a "$SRC" "$OUT/before_$d"') < src.index('INSTALLED=1\ncp "$BIN" "$GAME"') < src.index('enter_scene.py $T'))
ok &= check('go: the return of the pinned FS13 copy in finish, before installed_after',
            src.index('cp "$PINNED" "$GAME"') < src.index('sha "$GAME" > $OUT/installed_after.txt') < src.index('trap finish EXIT'))
ok &= check('go: installed_after must be FS13; installed before must be FS13',
            '[ "$(cat $OUT/installed_after.txt)" = "$INST" ] || { OK=0;' in src and '[ "$WANT" = "$INST" ] ||' in src)
ok &= check('go: no KYTY_GPU_CHECKPOINTS=, KYTY_GAME_PATCH=, KYTY_TEST_*= in the body',
            all(k not in body for k in ('KYTY_GPU_CHECKPOINTS=', 'KYTY_GAME_PATCH=', 'KYTY_TEST_')))
ok &= check('go: shell KYTY_* and VK_LAYER_* unset before the call', "for v in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'); do unset $v; done" in src)
ok &= check('go: lock line names HPP-800', 'echo "F46c HPP-800 go_f46c.sh $T pid $$ $(u)" > $LOCK' in src)
ok &= check('go: the key file of a tint tag', '[ -n "$KEY" ] && echo "$KEY" > $OUT/key.txt' in src)
for nm in ('queue_f46c.py', 'runchk_f46c.py'):
    ok &= check('%s own issue HPP-800' % nm, "OWN = 'HPP-800'" in open(os.path.join(HERE, nm), encoding='ascii').read())
ok &= check('chk_f46c.sh comments of HPP-800', '/api/issues/HPP-800/comments' in open(os.path.join(HERE, 'chk_f46c.sh'), encoding='ascii').read())
ok &= check('runchk_f46c.py reads F46C_RUN_ID, launch sets it', "os.environ.get('F46C_RUN_ID'" in open(os.path.join(HERE, 'runchk_f46c.py'), encoding='ascii').read()
            and 'F46C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup' in open(LA, encoding='ascii').read())
es = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
ok &= check('enter_scene: ROOT = f287/f46c', "ROOT = pathlib.Path('C:/kyty/f287/f46c')" in es)
ok &= check('enter_scene: CLOSE_WAIT_S = 40', 'CLOSE_WAIT_S = 40 ' in es)
a = open('C:/kyty/f287/f44c/tempo_f44c.py', 'rb').read().replace(b'\r\n', b'\n')
for x, y in ((b'f44c', b'f46c'), (b'F44C', b'F46C'), (b'F44c', b'F46c'), (b'HPP-793', b'HPP-800')):
    a = a.replace(x, y)
b = open(os.path.join(HERE, 'tempo_f46c.py'), 'rb').read()
ok &= check('tempo_f46c.py = tempo_f44c.py with the names moved (+ header line)', b.split(b'\n', 1)[1] == a)
for nm in sorted(os.listdir(HERE)):
    if nm.endswith(('.sh', '.py')) and not nm.startswith('fx_'):
        raw = open(os.path.join(HERE, nm), 'rb').read()
        if nm in ('enter_scene.py',):
            continue
        ok &= check('ASCII only: %s' % nm, all(c < 128 for c in raw))
print('checks %d failed %d' % (N[0], N[1]))
print('ALL OK' if ok and N[1] == 0 else 'FAILED')
sys.exit(0 if ok and N[1] == 0 else 1)
