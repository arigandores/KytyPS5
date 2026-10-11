"""Fixtures of the F42c chain (Track F link F42c, HPP-781; ROADMAP s122 item 694 (g)(6), 705, 713, 719, 634 / 660 / 661): the dry-run
plans of go_f42c.sh for f20_v / f20_hb / f20_w / f42c_ret (level, stable draws, timeout, hold, video / validation, knobs: KYTY_FIX_F20=1
the only KYTY_FIX_ value, no KYTY_TEST_*), refusals of go_f42c.sh, launch_f42c.sh and post_f42c.sh (usage; a repeat without the lead's
item - F42C_REPEAT_OK), THE SERIES ORDER of go_f42c.sh (F42C_DRYRUN=3 on a temporary F42C_SERIES: f20_v only without a snapshot, f20_hb
only after a made f20_v, f20_w only after a made f20_hb, f42c_ret only with a snapshot), the series form of the caches in the code (the
snapshot copied once inside the lock of f20_v before the install; tags return only _SaveData; the series dirs are moved back only by
f42c_ret; the 'same caches' check before f20_hb / f20_w - SERIES_STOP and exit 7; series/tags.txt and last_after.tsv only after a launch),
series_f42c.py (same EQUAL / DIFFER / MISSING, GLCache a row, sizes), the form linter --series = ALL OK, the first executable line of go /
launch = the linter, the guard scan right after the lock and before any manifest, the install / return of the binary (the F42a2 copy
1994a0ce installed after the copies, the pinned FS13 abab2196 returned in finish; sha256 of both copies on disk = the literals; the F42a2
copy = the F42a2 build output), the own issue of queue / runchk / chk = HPP-781 and the HPP-800 check of chk (item 719 (d)), the tempo tool
= the FS12c one with the names moved, the enter_scene.py ROOT and CLOSE_WAIT_S, post: the plan by the line 'dryrun ', the pairs (fs13_v,
fs4_hb sheets on disk), N1 -> SERIES_STOP; ASCII of every script; strict cp1250 output; the last line is ALL OK.  Port of
C:/kyty/f287/f44c/test_tools_f44c.py.  Early-exit form (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
usage: python test_tools_f42c.py"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GO = os.path.join(HERE, 'go_f42c.sh')
LA = os.path.join(HERE, 'launch_f42c.sh')
PO = os.path.join(HERE, 'post_f42c.sh')
SER = os.path.join(HERE, 'series_f42c.py')
BASH = 'C:/Program Files/Git/bin/bash.exe'
N = [0, 0]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='cp1250', errors='strict', line_buffering=True)
TB = '1994a0ced45c8135f17c8d2aa568278c66375250f1667430c83ba4d0b1a93f29'
FS13 = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
FS14 = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'
LINT = 'python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f42c'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


print('suite test_tools_f42c.py sha256 %s target go_f42c.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(GO)))


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
    print('%-4s %s' % ('ok' if cond else 'FAIL', name))
    return bool(cond)


def sh(script, args, env=None):
    e = dict(os.environ)
    for k in list(e):
        if k.startswith('F42C_'):
            del e[k]
    e.update(env or {})
    r = subprocess.run([BASH, script] + args, capture_output=True, text=True, env=e)
    return r.returncode, (r.stdout + r.stderr)


ok = True
KN = 'KYTY_FIX_F20=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'
WANT = {'f20_v': 'level underwater_aerial_garden sd 300 timeout 480 hold 330 rec --rec knobs ' + KN,
        'f20_hb': 'level hoover_beach sd 300 timeout 480 hold 330 rec --rec knobs ' + KN,
        'f20_w': 'level underwater_aerial_garden sd 100 timeout 900 hold 310 rec --emu-arg=--vulkan-validation --emu-arg=true knobs '
                 'KYTY_FIX_F20=1 VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 '
                 'KYTY_GPU_MARKERS=0',
        'f42c_ret': 'level none sd none timeout 0 hold 0 rec none knobs none'}
for b, w in sorted(WANT.items()):
    for t in (b, b + '_r1', b + '_r3'):
        rc, out = sh(GO, [t], {'F42C_DRYRUN': '1'})
        line = [l for l in out.splitlines() if l.startswith('dryrun ')]
        ok &= check('go plan %s' % t, rc == 0 and line and line[0] == 'dryrun %s base %s %s' % (t, b, w))
    ok &= check('plan %s: no KYTY_TEST_, no KYTY_GAME_PATCH' % b, 'KYTY_TEST_' not in w and 'KYTY_GAME_PATCH' not in w)
    if b != 'f42c_ret':
        ok &= check('plan %s: KYTY_FIX_ only KYTY_FIX_F20=1' % b, w.count('KYTY_FIX_') == 1 and 'KYTY_FIX_F20=1' in w)
        ok &= check('plan %s: validation only at f20_w' % b, ('vulkan-validation' in w) == (b == 'f20_w'))
rc, out = sh(GO, ['f20_v'], {'F42C_DRYRUN': '1'})
ok &= check('go dry-run output: first line is the linter line ALL OK, the plan is a later line (the F33e trap)',
            out.splitlines()[0].strip() == 'ALL OK' and out.splitlines()[1].startswith('dryrun f20_v '))
for b, pw in (('f20_v', 'no'), ('f20_hb_r2', 'no'), ('f20_w', 'yes'), ('f42c_ret', 'no')):
    rc, out = sh(PO, [b], {'F42C_POST_PLANONLY': '1'})
    lines = out.splitlines()
    ok &= check('post plan of %s is the dryrun line, plan-w %s (rc %d: %s)' % (b, pw, rc, out.strip()[-60:]),
                rc == 0 and len(lines) == 2 and lines[0].startswith('plan dryrun %s base ' % b) and lines[1] == 'plan-w ' + pw)
po = open(PO, encoding='ascii').read()
ok &= check("post: the plan is taken by grep '^dryrun '", "bash $G/go_f42c.sh $T 2>&1 | grep '^dryrun ' | head -1)" in po)
ok &= check('post: the plan-only exit is before the lock check (reads nothing)',
            po.index('F42C_POST_PLANONLY') < po.index('[ -e C:/kyty/SEALED_RUN.lock ]') < po.index('f42c_read.py $T'))
ok &= check('post: pairs with fs13_v and fs4_hb sheets', 'C:/kyty/f287/fs13c/runs/fs13_v/sheet_fs13_v.png' in po
            and 'C:/kyty/f287/fs4c/runs/fs4_hb/sheet_fs4_hb.png' in po)
ok &= check('on disk: the fs13_v and fs4_hb sheets exist', os.path.exists('C:/kyty/f287/fs13c/runs/fs13_v/sheet_fs13_v.png')
            and os.path.exists('C:/kyty/f287/fs4c/runs/fs4_hb/sheet_fs4_hb.png'))
ok &= check('post: N1 -> SERIES_STOP', "grep -q '^  N1 STOP:' $D/read.txt; then" in po and '>> $G/SERIES_STOP' in po)
ok &= check('post: tempo not PASS -> SERIES_STOP', 'if [ $TRC != 0 ]; then' in po)
for bad in ('f20_x', 'f20_v_r4', 'f20_v_r0', 'f29_v', 'fs13_v', 'f42c_ret_r0', ''):
    rc, out = sh(GO, [bad] if bad else [], {'F42C_DRYRUN': '1'})
    ok &= check('go usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(LA, [bad] if bad else [], {'F42C_DRYRUN': '2'})
    ok &= check('launch usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(PO, [bad] if bad else [], {'F42C_POST_PLANONLY': '1'})
    ok &= check('post usage rc 2 for %r' % bad, rc == 2)
tmp = tempfile.mkdtemp(prefix='f42ct_')
tm = os.path.join(tmp, 'times.txt')
envq = {'F42C_DRYRUN': '2', 'F42C_QUEUE_SKIP': '1', 'F42C_DISP_SKIP': '1', 'F42C_TIMES': tm}
for t in ('f20_v', 'f20_hb', 'f20_w', 'f42c_ret'):
    rc, out = sh(LA, [t], envq)
    ok &= check('launch %s dry-run 2 passes (rc %d %s)' % (t, rc, out.strip()[-40:]), rc == 0 and 'dryrun2 rep 0' in out)
    rc, out = sh(LA, [t + '_r1'], envq)
    ok &= check('launch repeat %s_r1 without F42C_REPEAT_OK -> rc 11' % t, rc == 11)
    rc, out = sh(LA, [t + '_r1'], dict(envq, F42C_REPEAT_OK='1'))
    ok &= check('launch repeat %s_r1 with F42C_REPEAT_OK -> passes' % t, rc == 0 and 'dryrun2 rep 1' in out)
# --- the series order (F42C_DRYRUN=3 on a temporary series dir) ---
S = os.path.join(tmp, 'series')


def state(snap, tags):
    shutil.rmtree(S, ignore_errors=True)
    if snap is None:
        return
    os.makedirs(S)
    if snap:
        open(os.path.join(S, 'manifest_before.tsv'), 'w').write('x\n')
        open(os.path.join(S, 'last_after.tsv'), 'w').write('x\n')
    if tags:
        open(os.path.join(S, 'tags.txt'), 'w').write(''.join('%s 2026-10-11T13:00:00Z\n' % g for g in tags))


def order(t):
    rc, out = sh(GO, [t], {'F42C_DRYRUN': '3', 'F42C_SERIES': S, 'F42C_TIMES': tm})
    return rc, ('dryrun3 order ok %s' % t) in out


for snap, tags, t, want in (
        (None, [], 'f20_v', True), (False, [], 'f20_v', False), (True, ['f20_v'], 'f20_v', False), (None, [], 'f20_v_r1', True),
        (None, [], 'f20_hb', False), (True, [], 'f20_hb', False), (True, ['f20_v'], 'f20_hb', True), (True, ['f20_v_r1'], 'f20_hb_r1', True),
        (False, ['f20_v'], 'f20_hb', False), (True, ['f20_hb'], 'f20_hb', False),
        (None, [], 'f20_w', False), (True, ['f20_v'], 'f20_w', False), (True, ['f20_v', 'f20_hb'], 'f20_w', True),
        (True, ['f20_v', 'f20_hb', 'f20_w'], 'f20_w_r1', True),
        (None, [], 'f42c_ret', False), (False, [], 'f42c_ret', False), (True, [], 'f42c_ret', True), (True, ['f20_v'], 'f42c_ret', True)):
    state(snap, tags)
    rc, passed = order(t)
    ok &= check('series order: snapshot %s tags %s -> %s %s (rc %d)' % (snap, tags, t, 'ok' if want else 'refused', rc),
                (rc == 0 and passed) if want else (rc == 2 and not passed))
shutil.rmtree(tmp, ignore_errors=True)
# --- series_f42c.py ---
tmp = tempfile.mkdtemp(prefix='f42cs_')
a = os.path.join(tmp, 'a.tsv')
b = os.path.join(tmp, 'b.tsv')
EMU = '_ShaderCache\tP/x\t1\taa\n_ShaderSeeds\tP/y\t2\tbb\n_PipelineCache\tz\t3\tcc\n'
open(a, 'w', newline='\n').write(EMU + 'GLCache\tg\t4\tdd\n_SaveData\ts\t5\tee\n')
open(b, 'w', newline='\n').write(EMU + 'GLCache\tg\t9\tff\n_SaveData\ts\t6\tgg\n')


def ser(args):
    r = subprocess.run([sys.executable, SER] + args, capture_output=True, text=True)
    return r.returncode, r.stdout


rc, out = ser(['same', a, b])
ok &= check('series same: GLCache and _SaveData differ only -> EQUAL rc 0, GLCache row DIFFER', rc == 0
            and out.startswith('same caches EQUAL files 3') and 'GLCache row DIFFER' in out)
open(b, 'w', newline='\n').write(EMU.replace('\t3\tcc', '\t4\tcz') + 'GLCache\tg\t4\tdd\n')
rc, out = ser(['same', a, b])
ok &= check('series same: _PipelineCache differs -> DIFFER rc 1', rc == 1 and out.startswith('same caches DIFFER only-before 1 only-after 1'))
open(b, 'w', newline='\n').write(EMU + '_ShaderCache\tP/new\t1\tzz\n')
rc, out = ser(['same', a, b])
ok &= check('series same: a new _ShaderCache file -> DIFFER rc 1', rc == 1 and 'only-after 1' in out)
rc, out = ser(['same', a, os.path.join(tmp, 'none.tsv')])
ok &= check('series same: missing file -> MISSING rc 2', rc == 2 and out.startswith('same caches MISSING'))
rc, out = ser(['sizes', a])
ok &= check('series sizes', rc == 0 and out.strip() == 'sizes GLCache=4 _PipelineCache=3 _SaveData=5 _ShaderCache=1 _ShaderSeeds=2')
rc, out = ser(['bad'])
ok &= check('series usage rc 9', rc == 9)
shutil.rmtree(tmp, ignore_errors=True)
# --- linter, literals, code order ---
r = subprocess.run([sys.executable, 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py', '--series', HERE], capture_output=True, text=True)
ok &= check('form634_check.py --series %s: %s' % (HERE, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '-'),
            r.returncode == 0 and r.stdout.strip().endswith('ALL OK'))
for p in (GO, LA):
    first = [l for l in open(p, encoding='ascii').read().splitlines() if l.strip() and not l.startswith('#')][0]
    ok &= check('%s first executable line is the form linter' % os.path.basename(p), first.startswith(LINT))
src = open(GO, encoding='ascii').read()
body = src.split('# usage')[1]
ok &= check('go: TB literal = 1994a0ce', 'TB=' + TB in src)
ok &= check('go: INST13 / INST14 literals = FS13 abab2196 / FS14 013e1974', 'INST13=' + FS13 in src and 'INST14=' + FS14 in src)
ok &= check('go: no 46892c20 / d760708d / 6abebc7b literal', all(x not in src for x in ('46892c20', 'd760708d', '6abebc7b')))
ok &= check('go: BIN and PINNED paths', 'BIN=$F/bin/kyty_emulator_1994a0ce.exe' in src and 'PIN13=$F/bin/kyty_emulator_abab2196.exe' in src
            and 'PIN14=$F/bin/kyty_emulator_013e1974.exe' in src)
ok &= check('on disk: sha256 of the F42a2 copy = 1994a0ce', sha('C:/kyty/f287/bin/kyty_emulator_1994a0ce.exe') == TB)
ok &= check('on disk: sha256 of the pinned FS13 copy = abab2196', sha('C:/kyty/f287/bin/kyty_emulator_abab2196.exe') == FS13)
ok &= check('on disk: sha256 of the pinned FS14 copy = 013e1974', sha('C:/kyty/f287/bin/kyty_emulator_013e1974.exe') == FS14)
ok &= check('on disk: the F42a2 copy = the F42a2 build output (f42a2/build/install)',
            sha('C:/kyty/f287/f42a2/build/install/kyty_emulator.exe') == TB)
lk = src.index('echo "lock taken $T $(u)"')
ok &= check('go: the guard scan right after the lock line, before any manifest',
            lk < src.index('guard_f42c.py scan)') < src.index('hold_f42c.py check)') < src.index('manifest_fs4c.py', lk))
ok &= check('go: no guard scan / hold check before the lock (item 660 (d)(1))',
            src.index('guard_f42c.py scan)') > src.index('set -o noclobber') and src.index('hold_f42c.py check)') > src.index('set -o noclobber'))
ok &= check('go: series snapshot inside f20_v, then _SaveData copy, then the install, then enter_scene',
            src.index('cp -a "$SRC" "$S/before_$d"') < src.index('cp -a "$EMU/_SaveData" "$OUT/before__SaveData"')
            < src.index('INSTALLED=1\ncp "$BIN" "$GAME"') < src.index('enter_scene.py $T'))
ok &= check('go: the series dirs are moved back only in the f42c_ret block, which exits before the tag manifest',
            src.count('mv "$S/before_$d"') == 1 and src.index('if [ "$B" = f42c_ret ]; then\n  python $G/manifest_fs4c.py $OUT/manifest_run.tsv')
            < src.index('mv "$S/before_$d"') < src.index('  exit 0\nfi\npython $G/manifest_fs4c.py $OUT/cache_before.tsv'))
ok &= check('go: a tag returns only _SaveData', 'MF_TAG=("_SaveData=$EMU/_SaveData")' in src and 'mv "$OUT/before__SaveData" "$LIVE"' in src
            and src.count('rm -rf "$LIVE" && mv') == 2)
ok &= check('go: series return cmp against series/manifest_before.tsv, EQUAL -> the dir moved to series.returned_',
            'python $G/manifest_fs4c.py --cmp $S/manifest_before.tsv $OUT/manifest_after.tsv' in src and 'RD=$G/series.returned_' in src)
ok &= check('go: same caches before f20_hb / f20_w -> SERIES_STOP and exit 7',
            'python $G/series_f42c.py same $OUT/cache_before.tsv $S/last_after.tsv' in src and '> $G/SERIES_STOP' in src and 'exit 7' in src)
ok &= check('go: tags.txt and last_after.tsv only after a launch', 'if [ -f $OUT/cache_before.tsv ] && launched; then' in src
            and src.index('if [ -f $OUT/cache_before.tsv ] && launched; then') < src.index('cp $OUT/cache_after.tsv $S/last_after.tsv')
            < src.index('echo "$T $(u)" >> $S/tags.txt'))
ok &= check('go: SERIES_STOP blocks tags, not f42c_ret', 'if [ "$B" != f42c_ret ]; then\n  [ -e $G/SERIES_STOP ]' in src)
ok &= check('go: the return of the pinned FS13 copy in finish, before installed_after',
            src.index('cp "$PINNED" "$GAME"') < src.index('sha "$GAME" > $OUT/installed_after.txt') < src.index('trap finish EXIT'))
ok &= check('go: installed_after must be = before (INST)', '[ "$(cat $OUT/installed_after.txt)" = "$INST" ] || { OK=0;' in src)
ok &= check('go: installed before the call must be FS13 or FS14 (case on WANT, other -> exit 1)',
            'case "$WANT" in' in src and '"$INST13") INST=$INST13; PINNED=$PIN13; INAME=FS13;;' in src
            and '"$INST14") INST=$INST14; PINNED=$PIN14; INAME=FS14;;' in src
            and 'nor FS14 013e1974 - not starting (question to the lead)"; exit 1;;' in src
            and src.index('case "$WANT" in') < src.index('[ "$(sha "$PINNED")" = "$INST" ] ||') < src.index('mkdir -p $OUT'))
ok &= check('go: KYTY_FIX_ in the code only KYTY_FIX_F20=1', body.count('KYTY_FIX_') == body.count('KYTY_FIX_F20=1') + body.count('KYTY_FIX_* except'))
ok &= check('go: no KYTY_GPU_CHECKPOINTS=, KYTY_GAME_PATCH=, KYTY_TEST_ in the body',
            all(k not in body for k in ('KYTY_GPU_CHECKPOINTS=', 'KYTY_GAME_PATCH=', 'KYTY_TEST_')))
ok &= check('go: shell KYTY_* and VK_LAYER_* unset before the call', "for v in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'); do unset $v; done" in src)
ok &= check('go: lock line names HPP-781', 'echo "F42c HPP-781 go_f42c.sh $T pid $$ $(u)" > $LOCK' in src)
for nm in ('queue_f42c.py', 'runchk_f42c.py'):
    ok &= check('%s own issue HPP-781' % nm, "OWN = 'HPP-781'" in open(os.path.join(HERE, nm), encoding='ascii').read())
chk = open(os.path.join(HERE, 'chk_f42c.sh'), encoding='ascii').read()
ok &= check('chk_f42c.sh comments of HPP-781 and the F46c end check HPP-800', '/api/issues/HPP-781/comments' in chk and '/api/issues/HPP-800"' in chk
            and 'case "$ST8" in done\\ *|cancelled\\ *|in_review\\ run=n) ;; *) exit 9;; esac' in chk)
ok &= check('runchk_f42c.py reads F42C_RUN_ID, launch sets it', "os.environ.get('F42C_RUN_ID'" in open(os.path.join(HERE, 'runchk_f42c.py'), encoding='ascii').read()
            and 'F42C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup' in open(LA, encoding='ascii').read())
es = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
ok &= check('enter_scene: ROOT = f287/f42c', "ROOT = pathlib.Path('C:/kyty/f287/f42c')" in es)
ok &= check('enter_scene: CLOSE_WAIT_S = 40 (the harness timeout of the exit, form b4_v)', 'CLOSE_WAIT_S = 40 ' in es)
a = open('C:/kyty/f287/fs12c/tempo_fs12c.py', 'rb').read().replace(b'\r\n', b'\n')
for x, y in ((b'fs12c', b'f42c'), (b'FS12C', b'F42C'), (b'FS12c', b'F42c'), (b'HPP-752', b'HPP-781')):
    a = a.replace(x, y)
b = open(os.path.join(HERE, 'tempo_f42c.py'), 'rb').read()
ok &= check('tempo_f42c.py = tempo_fs12c.py with the names moved (+ header lines)', b.split(b'\n', 3)[3] == a)
for nm in sorted(os.listdir(HERE)):
    if nm.endswith(('.sh', '.py')) and not nm.startswith('fx_'):
        raw = open(os.path.join(HERE, nm), 'rb').read()
        if nm in ('enter_scene.py',):
            continue
        ok &= check('ASCII only: %s' % nm, all(c < 128 for c in raw))
print('checks %d failed %d' % (N[0], N[1]))
print('ALL OK' if ok and N[1] == 0 else 'FAILED')
sys.exit(0 if ok and N[1] == 0 else 1)
