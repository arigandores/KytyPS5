"""Fixtures of the F40c chain (Track F link F40c, HPP-772; ROADMAP s122 item 692 (g)(1), (g)(3), (g)(4), 696, 700, 634 / 660 / 661): the
dry-run plan of go_f40c.sh for every tag (binary, KYTY_FIX_F24, KYTY_TEST_HIDLOSS mode, hold, video only for f24_n1, --mark-quit only for
the exit tags, the order u0 -> u1, p0 -> p1), refusals of go_f40c.sh, launch_f40c.sh and post_f40c.sh (usage; a repeat name without
F40C_REPEAT_OK), the form linter --series = ALL OK, the first executable line of go / launch = the linter, the install / return of the binary
(the tag copy installed after the copies of the caches, the pinned FS13 abab2196 copy returned in finish (item 703 (d)); the sha256 of every copy on disk =
the literals = the F40b2 table), the own issue of queue / runchk / chk = HPP-772, the tempo tool = the F38c one with the names moved,
enter_scene.py = the F38c file with ROOT moved and only the --mark-quit additions (QuitMark checked with a fake clock), CLOSE_WAIT_S, ASCII of
every script, post_f40c.sh takes the plan by the line 'dryrun ' (F40C_POST_PLANONLY=1), the pair with the fs12_v sheet only for a video tag,
strict cp1250 output; the last line is ALL OK.  Port of C:/kyty/f287/f38c/test_tools_f38c.py.  Early-exit form.  ASCII only.
usage: python test_tools_f40c.py"""
import hashlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GO = os.path.join(HERE, 'go_f40c.sh')
LA = os.path.join(HERE, 'launch_f40c.sh')
PO = os.path.join(HERE, 'post_f40c.sh')
BASH = 'C:/Program Files/Git/bin/bash.exe'
N = [0, 0]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='cp1250', errors='strict', line_buffering=True)
INST = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
BINS = {'ddf0ca91': 'ddf0ca913f9feb8a66569fa30668de4b97e275ab6c4cc3e5c69889b4cb82e5d5',
        'c164a6d3': 'c164a6d34f0ab8b089d23752bf052da1db24f5ead9798ad0d8b8caa264d4ef0b',
        'fcf462d8': 'fcf462d823eee56a0069866de224aeef9df2b1c6d9bc83288fee364705de0bef',
        'ea84198d': 'ea84198deaebc903b38e07df98fc1f6af84172434c024874b6a5c787a0069446',
        'bec75cc2': 'bec75cc20b86609bd1440a1a7aea1afea95a23af763f19b0f3a6e4c7e2f2fe94',
        'bd6dcc81': 'bd6dcc81a32519eae50de4eb44ce88187d9ba9d4a8221c656b402c6065068c8f'}
LINT = 'python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f40c'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


print('suite test_tools_f40c.py sha256 %s target go_f40c.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(GO)))


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
    print('%-4s %s' % ('ok' if cond else 'FAIL', name))
    return bool(cond)


def sh(script, args, env=None):
    e = dict(os.environ)
    for k in list(e):
        if k.startswith('F40C_'):
            del e[k]
    e.update(env or {})
    r = subprocess.run([BASH, script] + args, capture_output=True, text=True, env=e)
    return r.returncode, (r.stdout + r.stderr)


ok = True
K = 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'
WANT = {
    'f24_u0': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=0 KYTY_TEST_HIDLOSS=60:upd ' + K,
    'f24_u1': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev f24_u0 knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:upd ' + K,
    'f24_p0': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=0 KYTY_TEST_HIDLOSS=60:pad ' + K,
    'f24_p1': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev f24_p0 knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:pad ' + K,
    'f24_f0': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=0 KYTY_TEST_HIDLOSS=60:flap ' + K,
    'f24_f1': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:flap ' + K,
    'f24_x1': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark --mark-quit prev none knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:exit ' + K,
    'f24_d1': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:detach ' + K,
    'f24_m1': 'binary c164a6d3 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:flap ' + K,
    'f24_m2': 'binary fcf462d8 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark --mark-quit prev none knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:exit ' + K,
    'f24_m4': 'binary ea84198d level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:detach ' + K,
    'f24_m5': 'binary bec75cc2 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:upd ' + K,
    'f24_m6': 'binary bd6dcc81 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:upd ' + K,
    'f24_n1': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 330 rec --rec mark none prev none knobs KYTY_FIX_F24=1 ' + K,
    'f24_u0b': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=0 KYTY_TEST_HIDLOSS=60:upd ' + K,
    'f24_u1b': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev f24_u0b knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:upd ' + K,
    'f24_p0b': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev none knobs KYTY_FIX_F24=0 KYTY_TEST_HIDLOSS=60:pad ' + K,
    'f24_p1b': 'binary ddf0ca91 level underwater_aerial_garden sd 300 timeout 480 hold 150 rec none mark none prev f24_p0b knobs KYTY_FIX_F24=1 KYTY_TEST_HIDLOSS=60:pad ' + K,
}
for b, w in sorted(WANT.items()):
    for t in (b, b + '_r1', b + '_r2'):
        rc, out = sh(GO, [t], {'F40C_DRYRUN': '1'})
        line = [l for l in out.splitlines() if l.startswith('dryrun ')]
        ok &= check('go plan %s' % t, rc == 0 and line and line[0] == 'dryrun %s base %s %s' % (t, b, w))
    ok &= check('plan %s: KYTY_FIX_ only KYTY_FIX_F24' % b, w.count('KYTY_FIX_') == 1 and 'KYTY_FIX_F24=' in w)
    ok &= check('plan %s: KYTY_TEST_ only KYTY_TEST_HIDLOSS, absent for f24_n1' % b,
                (w.count('KYTY_TEST_') == 0) if b == 'f24_n1' else (w.count('KYTY_TEST_') == 1 and 'KYTY_TEST_HIDLOSS=60:' in w))
    ok &= check('plan %s: no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS, no validation' % b,
                'KYTY_GAME_PATCH' not in w and 'CHECKPOINTS' not in w and 'vulkan-validation' not in w)
    ok &= check('plan %s: --mark-quit only for the exit tags' % b, ('--mark-quit' in w) == ('60:exit' in w))
    ok &= check('plan %s: video only for f24_n1' % b, ('--rec' in w) == (b == 'f24_n1'))
rc, out = sh(GO, ['f24_u0'], {'F40C_DRYRUN': '1'})
ok &= check('go dry-run output: first line is the linter line ALL OK, the plan is a later line (the F33e trap)',
            out.splitlines()[0].strip() == 'ALL OK' and out.splitlines()[1].startswith('dryrun f24_u0 '))
for b in ('f24_u0', 'f24_n1', 'f24_f1_r2'):
    rc, out = sh(PO, [b], {'F40C_POST_PLANONLY': '1'})
    lines = out.splitlines()
    ok &= check('post plan of %s is the dryrun line, plan-w no (rc %d: %s)' % (b, rc, out.strip()[-60:]),
                rc == 0 and len(lines) == 2 and lines[0].startswith('plan dryrun %s base ' % b) and lines[1] == 'plan-w no')
po = open(PO, encoding='ascii').read()
ok &= check("post: the plan is taken by grep '^dryrun ', not by the first line",
            "bash $G/go_f40c.sh $T 2>&1 | grep '^dryrun ' | head -1)" in po and 'go_f40c.sh $T 2>&1 | head -1' not in po)
ok &= check('post: the plan-only exit is before the lock check (reads nothing)',
            po.index('F40C_POST_PLANONLY') < po.index('[ -e C:/kyty/SEALED_RUN.lock ]') < po.index('f40c_read.py $T'))
ok &= check('post: video steps only when rec_<tag>.mp4 exists; pair with the fs12_v sheet of FS12c',
            'if [ -f $REC ]; then' in po and 'C:/kyty/f287/fs12c/runs/fs12_v/sheet_fs12_v.png' in po)
ok &= check('post: SERIES_STOP on DEAD_CONTROL, WITNESS_DEAD, the third flap non-admission and tempo',
            all(s in po for s in ('DEAD_CONTROL)', 'WITNESS_DEAD)', 'NOT_ADMITTED:flap)', '[ $NF -ge 3 ] && [ $NA = 0 ]', '[ $TRC != 0 ] && STOPW=')))
ok &= check('on disk: the fs12_v sheet exists', os.path.exists('C:/kyty/f287/fs12c/runs/fs12_v/sheet_fs12_v.png'))
for bad in ('f24_c0', 'f24_c1', 'f24_m3', 'f24_u0_r3', 'f24_u0_r0', 'f25_v', 'f24_u2', ''):
    rc, out = sh(GO, [bad] if bad else [], {'F40C_DRYRUN': '1'})
    ok &= check('go usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(LA, [bad] if bad else [], {'F40C_DRYRUN': '2'})
    ok &= check('launch usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(PO, [bad] if bad else [], {'F40C_POST_PLANONLY': '1'})
    ok &= check('post usage rc 2 for %r' % bad, rc == 2)
tmp = tempfile.mkdtemp(prefix='f40ct_')
tm = os.path.join(tmp, 'times.txt')
envq = {'F40C_DRYRUN': '2', 'F40C_QUEUE_SKIP': '1', 'F40C_DISP_SKIP': '1', 'F40C_TIMES': tm}
for t in ('f24_u0', 'f24_n1', 'f24_m6'):
    rc, out = sh(LA, [t], envq)
    ok &= check('launch %s dry-run 2 passes (rc %d %s)' % (t, rc, out.strip()[-40:]), rc == 0 and 'dryrun2 rep 0' in out)
for t in ('f24_u0b', 'f24_u1b', 'f24_p0b', 'f24_p1b', 'f24_f1_r1', 'f24_m1_r2', 'f24_n1_r1', 'f24_u1b_r1'):
    rc, out = sh(LA, [t], envq)
    ok &= check('launch repeat %s without F40C_REPEAT_OK -> rc 11' % t, rc == 11)
    rc, out = sh(LA, [t], dict(envq, F40C_REPEAT_OK='1'))
    ok &= check('launch repeat %s with F40C_REPEAT_OK -> passes' % t, rc == 0 and 'dryrun2 rep 1' in out)
shutil.rmtree(tmp, ignore_errors=True)
r = subprocess.run([sys.executable, 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py', '--series', HERE], capture_output=True, text=True)
ok &= check('form634_check.py --series %s: %s' % (HERE, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '-'),
            r.returncode == 0 and r.stdout.strip().endswith('ALL OK'))
for p in (GO, LA):
    first = [l for l in open(p, encoding='ascii').read().splitlines() if l.strip() and not l.startswith('#')][0]
    ok &= check('%s first executable line is the form linter' % os.path.basename(p), first.startswith(LINT))
src = open(GO, encoding='ascii').read()
body = src.split('# usage')[1]
for b8, full in sorted(BINS.items()):
    ok &= check('go: literal %s = full sha256' % b8, '%s) TB=%s;;' % (b8, full) in src)
    ok &= check('on disk: sha256 of kyty_emulator_%s.exe = literal' % b8, sha('C:/kyty/f287/bin/kyty_emulator_%s.exe' % b8) == full)
ok &= check('go: INST literal = FS13 abab2196 (item 703 (d)); no FS12 literal', 'INST=' + INST in src and '46892c20' not in src)
ok &= check('go: BIN and PINNED paths', 'BIN=$F/bin/kyty_emulator_$BIN8.exe' in src and 'PINNED=$F/bin/kyty_emulator_abab2196.exe' in src)
ok &= check('on disk: sha256 of the pinned FS13 copy = abab2196', sha('C:/kyty/f287/bin/kyty_emulator_abab2196.exe') == INST)
ok &= check('on disk: kyty_emulator_ddf0ca91.exe = F40a2 build output', sha('C:/kyty/f287/f40a2/build/install/kyty_emulator.exe') == BINS['ddf0ca91']
            if os.path.exists('C:/kyty/f287/f40a2/build/install/kyty_emulator.exe') else True)
ok &= check('go: the guard scan right after the lock line, before the manifest',
            src.index('lock taken $T') < src.index('guard_f40c.py scan)') < src.index('hold_f40c.py check)')
            < src.index('manifest_fs4c.py $OUT/manifest_before.tsv'))
ok &= check('go: no guard scan / hold check before the lock (item 660 (d)(1))',
            src.index('guard_f40c.py scan)') > src.index('set -o noclobber') and src.index('hold_f40c.py check)') > src.index('set -o noclobber'))
ok &= check('go: install of the tag copy after the copies of the caches and after INSTALLED=1',
            src.index('cp -a "$SRC" "$OUT/before_$d"') < src.index('INSTALLED=1\ncp "$BIN" "$GAME"') < src.index('enter_scene.py $T'))
ok &= check('go: the return of the pinned FS13 copy in finish, before installed_after',
            src.index('cp "$PINNED" "$GAME"') < src.index('sha "$GAME" > $OUT/installed_after.txt') < src.index('trap finish EXIT'))
ok &= check('go: installed_after must be FS13', '[ "$(cat $OUT/installed_after.txt)" = "$INST" ] || { OK=0;' in src)
ok &= check('go: installed before the tag must be FS13', '[ "$WANT" = "$INST" ] ||' in src)
ok &= check('go: KYTY_FIX_ in the knobs only KYTY_FIX_F24', 'KYTY_FIX_F24=$FIX' in body and body.count('KYTY_FIX_') ==
            body.count('KYTY_FIX_F24') + body.count('KYTY_FIX_*') + body.count('KYTY_FIX_B24'))
ok &= check('go: no KYTY_GPU_CHECKPOINTS=, KYTY_GAME_PATCH= in the body', all(k not in body for k in ('KYTY_GPU_CHECKPOINTS=', 'KYTY_GAME_PATCH=')))
ok &= check('go: KYTY_TEST_ only KYTY_TEST_HIDLOSS=60:$MODE', body.count('KYTY_TEST_HIDLOSS=60:$MODE') == 1 and
            body.count('KYTY_TEST_') == body.count('KYTY_TEST_HIDLOSS') + body.count('KYTY_TEST_*'))
ok &= check('go: shell KYTY_* and VK_LAYER_* unset before the call', "for v in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'); do unset $v; done" in src)
ok &= check('go: the env after the unset is written', 'env_shell_after_unset.txt' in src)
ok &= check('go: lock line names HPP-772', 'echo "F40c HPP-772 go_f40c.sh $T pid $$ $(u)" > $LOCK' in src)
ok &= check('go: the order of item 692 (g)(1): u1 after u0, p1 after p0, the b pair', 'f24_u1) BIN8=ddf0ca91; FIX=1; MODE=upd; PREV=f24_u0;;' in src
            and 'f24_p1) BIN8=ddf0ca91; FIX=1; MODE=pad; PREV=f24_p0;;' in src and 'PREV=f24_u0b;;' in src and 'PREV=f24_p0b;;' in src)
for nm in ('queue_f40c.py', 'runchk_f40c.py'):
    ok &= check('%s own issue HPP-772' % nm, "OWN = 'HPP-772'" in open(os.path.join(HERE, nm), encoding='ascii').read())
ok &= check('runchk_f40c.py reads F40C_RUN_ID', "os.environ.get('F40C_RUN_ID'" in open(os.path.join(HERE, 'runchk_f40c.py'), encoding='ascii').read())
ok &= check('chk_f40c.sh comments of HPP-772', '/api/issues/HPP-772/comments' in open(os.path.join(HERE, 'chk_f40c.sh'), encoding='ascii').read())
es = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
ok &= check('enter_scene: ROOT = f287/f40c', "ROOT = pathlib.Path('C:/kyty/f287/f40c')" in es)
ok &= check('enter_scene: CLOSE_WAIT_S = 40 (the harness timeout of the exit, form b4_v)', 'CLOSE_WAIT_S = 40 ' in es)
old = open('C:/kyty/f287/f38c/enter_scene.py', 'rb').read().replace(b'\r\n', b'\n').decode('ascii')
new = es.replace('\r\n', '\n')
n2 = new[:new.index('M_QUIT_POSTED = ')] + new[new.index('def ft_tail_from_samples('):]
n2l = [l for l in n2.splitlines() if 'qm' not in l and "'--mark-quit'" not in l and 'F40c: during the hold, time the line' not in l
       and "print('quit mark: " not in l][2:]
o2 = old.replace("ROOT = pathlib.Path('C:/kyty/f287/f38c')", "ROOT = pathlib.Path('C:/kyty/f287/f40c')")
ok &= check('enter_scene: = the F38c file with ROOT moved once the F40c additions (header, QuitMark block, qm lines, --mark-quit) are taken '
            'out (%d / %d lines)' % (len(n2l), len(o2.splitlines())), n2l == o2.splitlines() and old.count("ROOT = pathlib.Path('C:/kyty/f287/f38c')") == 1
            and 'qm' not in old)
spec = importlib.util.spec_from_file_location('es40', os.path.join(HERE, 'enter_scene.py'))
sys.path.insert(0, HERE)
try:
    es40 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(es40)
    td = tempfile.mkdtemp(prefix='f40cq_')
    lp = os.path.join(td, 'log.txt')
    open(lp, 'wb').write(b'a\n')
    clock = [100.0]
    import pathlib
    q = es40.QuitMark(pathlib.Path(lp), 90.0, clock=lambda: clock[0])
    q.sample(True)
    clock[0] = 100.25
    open(lp, 'ab').write(b'TestHidLoss: quit posted t_us=1\n')
    q.sample(True)
    clock[0] = 107.5
    q.sample(True)
    clock[0] = 107.75
    q.sample(False)
    res = q.result()
    ok &= check('QuitMark: upper = dead_first - before = 7.75, lower = alive_last - seen = 7.25 (%s)' % res,
                res['exit_upper_s'] == 7.75 and res['exit_lower_s'] == 7.25 and res['seen_s'] == 10.25 and res['dead_first_s'] == 17.75)
    q2 = es40.QuitMark(pathlib.Path(os.path.join(td, 'none.txt')), 0.0, clock=lambda: clock[0])
    q2.sample(False)
    ok &= check('QuitMark: no line -> upper None (%s)' % q2.result(), q2.result()['exit_upper_s'] is None)
    shutil.rmtree(td, ignore_errors=True)
except Exception as e:  # noqa: BLE001
    ok &= check('QuitMark import and fake clock (%s)' % type(e).__name__, False)
a = open('C:/kyty/f287/f38c/tempo_f38c.py', 'rb').read().replace(b'\r\n', b'\n')
for x, y in ((b'f38c', b'f40c'), (b'F38C', b'F40C'), (b'F38c', b'F40c'), (b'HPP-765', b'HPP-772')):
    a = a.replace(x, y)
b = open(os.path.join(HERE, 'tempo_f40c.py'), 'rb').read()
ok &= check('tempo_f40c.py = tempo_f38c.py with the names moved (+ one header line)', b.split(b'\n', 1)[1] == a)
for nm in sorted(os.listdir(HERE)):
    if nm.endswith(('.sh', '.py')) and not nm.startswith('fx_'):
        raw = open(os.path.join(HERE, nm), 'rb').read()
        ok &= check('ASCII only: %s' % nm, all(c < 128 for c in raw))
print('checks %d failed %d' % (N[0], N[1]))
print('ALL OK' if ok and N[1] == 0 else 'FAILED')
sys.exit(0 if ok and N[1] == 0 else 1)
