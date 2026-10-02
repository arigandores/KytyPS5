"""test_go_fs2.py - fixtures of go_fs2.sh (FS2c, HPP-383): the static form of the script (item 298 (g)(1)-(4): tags, order, levels,
stand, form W of item 295 (b) - no message filter, limit 100000000; defaults - no KYTY_FIX_* except fs2_w0; precache by default; video
on fs2_v / fs2_t / fs2_tr; the binary check before every tag; binary strings; the installed build dac02fb9 returned; cache, directory,
GLCache and _PipelineCache returns; lock window; seal call; warm-up; K3 repeat; procload output through the <app> mask, item 324 (i))
and the cheap refusals: usage, seal call line, one attempt, lock held, stop file, DRY plan, missing FS2 binary.  A copy of the script
with LOCK, STOPF, TIMES and ROOT moved into fx/go - no real lock, no guard, no install, no game.  The win_fs2.py decide() table.
Last line: ALL OK."""
import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import win_fs2  # noqa: E402

FX = os.path.join(HERE, 'fx', 'go').replace('\\', '/')
BASH = 'C:/Program Files/Git/bin/bash.exe'
N = [0]
FAIL = []


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond, detail=''):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL %s %s' % (name, detail))


def unix(p):
    return '/' + p[0].lower() + p[2:] if p[1] == ':' else p


def case_body(s, pat):
    i = s.index('    %s) ' % pat)
    return s[i:s.index(';;', i)]


src = open(os.path.join(HERE, 'go_fs2.sh'), 'rb').read().decode('ascii')
print('suite test_go_fs2.py sha256 %s target go_fs2.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'go_fs2.sh'))))
body = '\n'.join(l for l in src.split('\n') if not l.startswith('#') and not l.startswith('  echo "DRY'))
check('script is ASCII', all(ord(c) < 128 for c in src))
check('script is LF', '\r' not in src)
check('KYTY_GPU_CHECKPOINTS never set', 'KYTY_GPU_CHECKPOINTS=' not in src)
check('KYTY_PIPELINE_PRECACHE never passed (precache by default, p.281(g), p.300(b)(4)), unset', 'KYTY_PIPELINE_PRECACHE=' not in src
      and re.search(r'(?m)^unset .*\bKYTY_PIPELINE_PRECACHE\b', src) is not None)
check('no VK_LAYER_MESSAGE_ID_FILTER passed (p.295(b)), unset at the start', 'VK_LAYER_MESSAGE_ID_FILTER=' not in src
      and re.search(r'(?m)^unset .*\bVK_LAYER_MESSAGE_ID_FILTER\b', src) is not None)
check('duplicate limit 100000000 (p.295(b))', 'VKDUP="100000000"\n' in src and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP' in src)
check('KYTY_FIX_* never passed except KYTY_FIX_MINIMIZE=0 of fs2_w0; all unset', [m for m in re.findall(r'KYTY_FIX_\w+=\S*', body)] ==
      ['KYTY_FIX_MINIMIZE=0";;'] and all(re.search(r'(?m)^unset .*\b%s\b' % k, src) for k in
                                       ('KYTY_FIX_B26', 'KYTY_FIX_B1B', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_MINIMIZE', 'KYTY_FIX_B9A')),
      re.findall(r'KYTY_FIX_\w+=\S*', body))
check('every run KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0', src.count('KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 >') == 1)
check('no mutlib word in a command', 'mutlib ' not in src.replace("'mut_[a-z0-9_]*|test_[a-z0-9_]*fs2|mutlib'", ''))
check('no tail -F, no nohup, no background & in the series script', 'tail -F' not in src and 'nohup' not in src and ' &\n' not in src)
check('restore in the EXIT trap', 'trap finish EXIT' in src and 'restore_bin' in src)
check('binary constant = FS2 copy bbad499c', 'BIN="C:/kyty/f287/bin/kyty_emulator_bbad499c.exe"\n' in src
      and 'BIN_EXPECT="bbad499c56b744dfcef85b7556735c025ebb3db185b6bb9b02e7a0b3a228eb55"\n' in src)
check('binary strings before the lock', 'for S in "FixMinimize: on" "FixB9a: on" "TestMinimize: armed" "SwapchainZeroExtent: begin" '
      '"AudioPropagation: calls" "$SIGSTR"; do' in src and 'SIGSTR="56189185f9e9f9a0ea5174f3f85206e6d099db3d"\n' in src
      and src.index('for S in "FixMinimize: on"') < src.index('set -o noclobber'))
check('binary check before every tag (inside onetag, before the run)', src.index('binary check failed (p.286(b))') > src.index('onetag() {')
      and src.index('binary check failed (p.286(b))') < src.index('  runtag ""') and
      '[ "$(sha "$BIN")" != "$BIN_EXPECT" ] || [ "$(sha "$GAME")" != "$BIN_EXPECT" ]' in src)
check('no build command', 'build_local' not in src and 'cmake' not in src and 'ninja' not in src)
check('failed return writes the stop file', src.count('RETFAIL=1') == 7 and '> $STOPF' in src and 'HPP-383' in src, src.count('RETFAIL=1'))
check('directory list before and after', 'DIRS_BEFORE=$(dirlist "$CACHE")' in src and '[ "$DIRS_BACK" = "$DIRS_BEFORE" ]' in src
      and '[ "$DIRS_SNAP" = "$DIRS_BEFORE" ]' in src)
check('signature manifest before and after', src.count('cachesig_f6e.py "$CACHE"') == 2)
check('caches are moved, never rm -rf on the game caches', 'rm -rf "$CACHE"' not in src and 'mv "$CACHE" "$KEEP/"' in src
      and 'rm -rf "$GLDIR"' not in src and 'mv "$GLDIR" "$GLKEEP/"' in src and 'rm -rf "$PCDIR"' not in src and 'mv "$PCDIR" "$PCKEEP/"' in src)
check('_PipelineCache content list before, copy, return = before', '[ "$PC_SNAP" = "$PC_BEFORE" ]' in src and '[ "$PCB" = "$PC_BEFORE" ]' in src)
check('lock window right before the lock', src.index('win_fs2.py 2>&1') < src.index('set -o noclobber')
      and src.index('busy "stop file $STOPF appeared before the lock"') < src.index('win_fs2.py 2>&1'))
check('window closed or unknown -> busy', '*"-> open") ;;' in src and 'busy "lock window closed or unknown' in src)
check('seq of p.298(g) + p.327(g)(2)', 'SEQ="fs2_w fs2_w0 fs2_v fs2_tw fs2_t"\n' in src)
check('every possible tag guarded by the one-attempt rule', 'ALLT="fs2_w fs2_w0 fs2_v fs2_tw fs2_t fs2_tr"\n' in src and 'for C in $ALLT; do' in src)
check('seal 01', 'PRED="pred/01_fs2.md"\n' in src)
check('installed build to return = dac02fb9, pinned copy of session 146', 'BUILD_EXPECT="dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e"\n'
      in src and 'BUILD_PINNED="/c/kyty/s146/kyty_emulator_dac02fb9.exe"\n' in src and '9235a7ac' not in body)
check('installed sha checked before the lock and written inside the lock', src.index('the installed $GAME is not $BUILD_EXPECT before the series')
      < src.index('set -o noclobber') < src.index('tl "installed build at the start of the series sha256 $(sha "$GAME")') < src.index('trap finish EXIT'))
check('restore compares to BUILD_EXPECT', 'cp "$BUILD_PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$BUILD_EXPECT" ]' in src)
check('levels and holds', 'SKY=underwater_aerial_garden\n' in src and 'TC=timestop_casino\n' in src and 'WHOLD="310"\n' in src
      and 'VHOLD="330"\n' in src and 'HOLDW="60"\n' in src and 'HOLDT="125"\n' in src)
check('stand 60:10 and the W extras', 'STANDV="60:10"\n' in src and
      'WX="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_TEST_MINIMIZE=$STANDV"' in src)
b = case_body(src, 'fs2_w')
check('fs2_w: Sky Garden, W, validation true, WX, no video', 'LV=$SKY;' in b and 'HH=$WHOLD' in b and
      'EMUX="--emu-arg=--vulkan-validation --emu-arg=true"' in b and 'EXTRA="$WX"' in b and 'RECF' not in b, b)
b = case_body(src, 'fs2_w0')
check('fs2_w0: as fs2_w + KYTY_FIX_MINIMIZE=0', 'LV=$SKY;' in b and 'EMUX="--emu-arg=--vulkan-validation --emu-arg=true"' in b
      and 'EXTRA="$WX KYTY_FIX_MINIMIZE=0"' in b and 'RECF' not in b, b)
b = case_body(src, 'fs2_v')
check('fs2_v: Sky Garden, no validation, video, stand, hold 330', 'LV=$SKY;' in b and 'HH=$VHOLD' in b and 'RECF="--rec"' in b
      and 'EXTRA="KYTY_TEST_MINIMIZE=$STANDV"' in b and 'EMUX' not in b, b)
b = case_body(src, 'fs2_tw')
check('fs2_tw: timestop_casino warm-up, no video, no extra, hold 60', 'LV=$TC;' in b and 'HH=$HOLDW' in b and 'WU=1' in b
      and 'RECF' not in b and 'EXTRA' not in b, b)
b = case_body(src, 'fs2_t|fs2_tr')
check('fs2_t / fs2_tr: timestop_casino, video, hold 125, stable 100', 'LV=$TC;' in b and 'HH=$HOLDT' in b and 'RECF="--rec"' in b
      and '--stable-draws 100 --timeout 480' in b and 'EXTRA' not in b, b)
check('defaults of a tag reset before the case', '  WU=0; RECF=""; EMUX=""; EXTRA=""\n' in src)
check('unknown tag stops', '*) tl "$C unknown tag - series stop"; return 1;;' in src)
i_w = src.index('  if [ "$WU" = "1" ]; then')
check('warm-up returns after the run, before video and reader (not read)', src.index('  runtag ""') < i_w < src.index('python $VIDGLITCH')
      and src.index('    return 0', i_w) < src.index('python $VIDGLITCH') and src.index('    return 0', i_w) < src.index('fs2_read.py --tag $C'))
check('warm-up stop on rc != 0, death or window lines (p.327(g)(2))', "Unhandled exception:|--- Fatal Error ---|--- Error ---|GpuHangAbort:|ErrorDeviceLost|Window [0-9]+ minimized|Recovering Vulkan swapchain"
      in src and '[ "$WD" = "0" ] && [ "$RC" = "0" ]' in src)
check('glitch 4 6 and sheet for every video tag', 'python $VIDGLITCH rec_$C.mp4 4 6' in src and 'sheet142.py rec_$C.mp4 sheet_$C.png' in src
      and 'if [ -n "$RECF" ]; then' in src)
check('stop check after every read tag', 'fs2_read.py --stop-check runs/$C.read.json' in src)
check('K3 repeat fs2_tr once on "repeat-k3: fs2_tr"', '"repeat-k3: fs2_tr"*)' in src and 'C=fs2_tr' in src and src.count('onetag ||') == 2)
check('enter_scene rc != 0 stops except fs2_w0 and a validation stop', 'if [ "$RC" != "0" ] && [ "$C" != "fs2_w0" ]; then' in src
      and '"continue: validation"*)' in src and 'series stop: enter_scene rc $RC' in src)
check('W form line of p.295(b)(4) as a times line from the harness env', 'W form (p.295(b)(4)) from the env the harness writes: W form: limit=$VKDUP filter=none' in src)
check('summary at the end', 'fs2_read.py --summary > summary_fs2.txt' in src)
check('one retry of a BUSY refusal', src.count('runtag ""' + chr(10)) == 1 and src.count('runtag " (retry after a BUSY refusal)"') == 1)
check('lock.log UTC lines', 'echo "lock taken series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src and
      'echo "lock released series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src)
check('disk check before the lock (>= 60 GB)', 'DISKMIN_GB=60\n' in src and src.index('free disk C:') < src.index('set -o noclobber'))
check('procload output through the mask (p.324(i))', 'python $ROOT/procload.py --wait-s "$1" 2>&1 | mask >> $L' in src)
check('mask in go_fs2.sh is the F7a text', 'mask() { sed -E "s/\\(\'[^\']*\'/(\'<app>\'/g"; }' in src)
check('fgcpu146 (masked names) is used, not fgcpu143', 'fgcpu146.py' in src and 'fgcpu143' not in src)

# the mask, run by the real sed over procload lines with process names (the definition line of go_fs2.sh itself)
names = ['someappname', 'Other.App', 'x-y_z']
lines = "procload: busy ('%s', 1234, 55.0) ('%s', 99, 20.1)\nprocload: busy ('%s', 7, 30.0)\nprocload: idle\n" % tuple(names)
mline = [x for x in src.splitlines() if x.startswith('mask() {')]
check('mask one definition', len(mline) == 1)
os.makedirs(os.path.join(HERE, 'runs'), exist_ok=True)
fxm = os.path.join(HERE, 'runs', '_fx_mask.sh')
with open(fxm, 'w', encoding='ascii', newline='\n') as f:
    f.write(mline[0] + '\nmask\n')
p = subprocess.run([BASH, fxm], input=lines.encode('ascii'), capture_output=True)
sed = p.stdout.decode('ascii').replace('\r', '')
os.remove(fxm)
check('mask: no input name in the output', not any(n in sed for n in names), sed)
check('mask keeps the rest', sed.count("('<app>'") == 3 and 'procload: idle' in sed, sed)

# win_fs2 decide()
ok = {'HPP-382': ('done', None), 'HPP-381': ('done', None), 'HPP-370': ('done', None), 'HPP-377': ('in_review', None),
      'HPP-393': ('blocked', None)}
check('win open', win_fs2.decide(ok) == (0, 'open'))
check('win members', win_fs2.ALL == ('HPP-382', 'HPP-381', 'HPP-370', 'HPP-377', 'HPP-393'))
for i, st in (('HPP-382', ('in_review', None)), ('HPP-382', ('done', 'run1')), ('HPP-381', ('blocked', None)), ('HPP-370', ('in_progress', None)),
              ('HPP-377', ('done', 'run2')), ('HPP-393', ('todo', None)), ('HPP-393', ('in_progress', None)), ('HPP-393', ('blocked', 'run3'))):
    d = dict(ok)
    d[i] = st
    check('win closed %s %s' % (i, st), win_fs2.decide(d) == (5, 'closed'))
for i in ok:
    d = dict(ok)
    d[i] = (None, 'exception URLError')
    check('win error %s' % i, win_fs2.decide(d) == (6, 'error'))


def make(binf='', bexp='', pred=None):
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    s = src.replace('ROOT=C:/kyty/f287/fs2c', 'ROOT=%s' % FX)
    s = s.replace('LOCK=/c/kyty/SEALED_RUN.lock', 'LOCK=%s/LOCK' % unix(FX))
    s = s.replace('STOPF=/c/kyty/f287/STOP', 'STOPF=%s/STOP' % unix(FX))
    s = s.replace('TIMES=/c/kyty/f287/times.txt', 'TIMES=%s/times.txt' % unix(FX))
    s = re.sub(r'(?m)^BIN=".*"$', 'BIN="%s"' % binf, s, count=1)
    s = re.sub(r'(?m)^BIN_EXPECT=".*"$', 'BIN_EXPECT="%s"' % bexp, s, count=1)
    open(os.path.join(FX, 'go_fs2.sh'), 'wb').write(s.encode('ascii'))
    if pred is not None:
        os.makedirs(os.path.join(FX, 'pred'))
        open(os.path.join(FX, 'pred', '01_fs2.md'), 'wb').write(pred.encode('ascii'))


def run(*args, env_add=None):
    env = dict(os.environ)
    env.pop('PLWAIT', None)
    env.pop('DRY', None)
    env.update(env_add or {})
    pr = subprocess.run([BASH, FX + '/go_fs2.sh'] + list(args), capture_output=True, env=env)
    return pr.returncode, pr.stdout.decode('ascii', 'replace')


CALL = 'go_fs2 call: PLWAIT=540 bash C:/kyty/f287/fs2c/go_fs2.sh series\n'
make()
rc, out = run()
check('usage rc 2', rc == 2 and 'usage' in out, (rc, out))
rc, out = run('fs2_w')
check('a tag instead of series rc 2', rc == 2, (rc, out))
rc, out = run('series')
check('not configured rc 2', rc == 2 and 'not configured' in out, (rc, out))
make('x.exe', 'ab')
rc, out = run('series')
check('configured, no seal -> rc 1', rc == 1 and 'seal' in out, (rc, out))
make('x.exe', 'ab', pred='# seal\n' + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('DRY with the seal line rc 0', rc == 0 and out.startswith('DRY series'), (rc, out))
check('DRY plan names the tags, the form W, the stand, the window and the returns', 'fs2_w0' in out and 'KYTY_FIX_MINIMIZE=0' in out
      and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000' in out and 'KYTY_TEST_MINIMIZE=60:10' in out and 'win_fs2' in out
      and 'HPP-393' in out and '_PipelineCache' in out and 'fs2_tr' in out and 'masked' in out, out)
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='100'))
check('PLWAIT other than the seal rc 1', rc == 1, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='600'))
check('PLWAIT above 540 rc 2', rc == 2, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='x'))
check('PLWAIT not a number rc 2', rc == 2, (rc, out))
make('x.exe', 'ab', pred='# seal\n' + CALL + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('two seal call lines rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', pred='# seal\n' + CALL.replace('fs2c/go_fs2.sh', 'f6e/go_f6e.sh'))
rc, out = run('series', env_add=dict(DRY='1'))
check('another call line rc 1', rc == 1, (rc, out))
for t in ('fs2_w', 'fs2_w0', 'fs2_v', 'fs2_tw', 'fs2_t', 'fs2_tr'):
    make('x.exe', 'ab', pred='# seal\n' + CALL)
    open(os.path.join(FX, 'attempt_%s.txt' % t), 'w').write('x')
    rc, out = run('series', env_add=dict(DRY='1'))
    check('attempt marker %s -> rc 1 (one attempt)' % t, rc == 1 and 'attempt' in out, (rc, out))
make('x.exe', 'ab', pred='# seal\n' + CALL)
open(os.path.join(FX, 'fs2_tr.json'), 'w').write('{}')
rc, out = run('series', env_add=dict(DRY='1'))
check('a repeat json -> rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', pred='# seal\n' + CALL)
open(os.path.join(FX, 'LOCK'), 'w').write('someone')
rc, out = run('series', env_add=dict(DRY='1'))
check('lock held -> rc 4 before anything', rc == 4 and 'lock held' in out, (rc, out))
make('x.exe', 'ab', pred='# seal\n' + CALL)
open(os.path.join(FX, 'STOP'), 'w').write('p.999')
rc, out = run('series', env_add=dict(DRY='1'))
check('stop file -> rc 4', rc == 4 and 'stop file' in out and 'p.999' in out, (rc, out))
make('x.exe', 'ab', pred='# seal\n' + CALL)
rc, out = run('series')
check('configured, real path: missing FS2 binary -> rc 1 before any lock', rc == 1 and 'FS2 binary bad' in out
      and not os.path.exists(os.path.join(FX, 'LOCK')), (rc, out))
shutil.rmtree(os.path.join(HERE, 'fx'), ignore_errors=True)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)
