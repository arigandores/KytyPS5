"""test_go_f6e.py - fixtures of go_f6e.sh (F6e, HPP-377): the static form of the script (constants of p.287(v)(5), (d), p.290(b),
p.294(g) N4: knob values, no KYTY_PRINT_NAMES, no validation, precache by default, video on every tag, binary check before every
tag, binary strings, cache and directory lists, the signature manifest, GLCache return, lock window, seal call, form repeat, K3
repeats) and the cheap refusals: usage, not configured, seal call line, one attempt, lock held, stop file, DRY plan, missing fix
binary.  A copy of the script with LOCK, STOPF, TIMES and ROOT moved into fx/go - no real lock, no guard, no install, no game.
Last line: ALL OK."""
import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
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


src = open(os.path.join(HERE, 'go_f6e.sh'), 'rb').read().decode('ascii')
print('suite test_go_f6e.py sha256 %s target go_f6e.sh sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                  sha(os.path.join(HERE, 'go_f6e.sh'))))
body = '\n'.join(l for l in src.split('\n') if not l.startswith('#') and not l.startswith('  echo "DRY'))
check('script is ASCII', all(ord(c) < 128 for c in src))
check('script is LF', '\r' not in src)
check('KYTY_GPU_CHECKPOINTS never set', 'KYTY_GPU_CHECKPOINTS=' not in src)
check('KYTY_PRINT_NAMES never set, unset at the start (p.294(g) N4)', 'KYTY_PRINT_NAMES=' not in src and
      re.search(r'(?m)^unset .*\bKYTY_PRINT_NAMES\b', src) is not None)
check('KYTY_PIPELINE_PRECACHE never passed (p.281(g)), unset', 'KYTY_PIPELINE_PRECACHE=' not in src and
      re.search(r'(?m)^unset .*\bKYTY_PIPELINE_PRECACHE\b', src) is not None)
check('no validation anywhere', 'vulkan-validation' not in body and 'VK_LAYER' not in body)
check('KYTY_FIX_B26/B1B/DUALSRC/MINIMIZE never passed, all unset', all('%s=' % k not in src for k in
      ('KYTY_FIX_B26', 'KYTY_FIX_B1B', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_MINIMIZE')) and
      all(re.search(r'(?m)^unset .*\b%s\b' % k, src) for k in ('KYTY_FIX_B26', 'KYTY_FIX_B1B', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_MINIMIZE', 'KYTY_FIX_B9A')))
check('every run KYTY_GPU_CLOCK_PIN=1 and --rec', src.count('KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 >') == 1 and
      '--pred $ROOT/$PRED $RECF --hold $HH $EXTRA' in src and '  WU=0; RECF="--rec"; HH=$HOLD\n' in src)
check('no mutlib word in a command', 'mutlib ' not in src.replace("'mut_[a-z0-9_]*|test_[a-z0-9_]*f6e|mutlib'", ''))
check('no tail -F, no nohup in the series script', 'tail -F' not in src and 'nohup' not in src)
check('restore in the EXIT trap', 'trap finish EXIT' in src and 'restore_bin' in src)
check('binary constant = F6c copy d8756dce', 'BIN_F6E="C:/kyty/f287/bin/kyty_emulator_d8756dce.exe"\n' in src
      and 'BIN_EXPECT="d8756dce0662fb318a24a3fb52a3260d31ea84628372fa9a438ca46ed6a6e43d"\n' in src)
check('binary strings FixB9a / AudioPropagation / signature 56189185 before the lock', 'SIGSTR="56189185f9e9f9a0ea5174f3f85206e6d099db3d"\n' in src
      and 'for S in "FixB9a: on" "AudioPropagation: calls" "$SIGSTR"; do' in src and src.index('for S in "FixB9a: on"') < src.index('set -o noclobber'))
check('binary check before every tag (inside onetag, before the run)', src.index('binary check failed:') > src.index('onetag() {')
      and src.index('binary check failed:') < src.index('  runtag ""') and
      '[ "$(sha "$BIN_F6E")" != "$BIN_EXPECT" ] || [ "$(sha "$GAME")" != "$BIN_EXPECT" ]' in src)
check('no build command', 'build_local' not in src and 'cmake' not in src and 'ninja' not in src)
check('GLRESTORE=1', 'GLRESTORE="1"\n' in src)
check('failed return writes the stop file', src.count('RETFAIL=1') == 5 and '> $STOPF' in src and 'HPP-377' in src)
check('directory list before and after', 'DIRS_BEFORE=$(dirlist "$CACHE")' in src and
      '[ "$DIRS_BACK" = "$DIRS_BEFORE" ]' in src and '[ "$DIRS_SNAP" = "$DIRS_BEFORE" ]' in src)
check('signature manifest before and after (p.290(b)(1))', src.count('cachesig_f6e.py "$CACHE"') == 2)
check('cache is moved, never rm -rf on the game cache', 'rm -rf "$CACHE"' not in src and 'mv "$CACHE" "$KEEP/"' in src)
check('GLCache is moved, never rm -rf', 'rm -rf "$GLDIR"' not in src and 'mv "$GLDIR" "$GLKEEP/"' in src)
check('lock window right before the lock', src.index('win_f6e.py 2>&1') < src.index('set -o noclobber')
      and src.index('busy "stop file $STOPF appeared before the lock"') < src.index('win_f6e.py 2>&1'))
check('window closed or unknown -> busy', '*"-> open") ;;' in src and 'busy "lock window closed or unknown' in src)
check('seq of p.287(v)(5)', 'SEQ="f6e_a1 f6e_a2 f6e_b1 f6e_c1 f6e_c2"\n' in src)
check('every possible tag guarded by the one-attempt rule', 'ALLT="f6e_w1 f6e_w2 f6e_a1 f6e_a2 f6e_b1 f6e_c1 f6e_c2 f6e_a1f f6e_a2f f6e_b1f f6e_c1f f6e_c2f f6e_a1r f6e_a2r f6e_b1r"\n' in src
      and 'for C in $ALLT; do' in src)
check('seal 03 (p.309(l)(5))', 'PRED="pred/03_f6e.md"\n' in src and 'pred/01_f6e.md' not in src and 'pred/02_f6e.md' not in src)
check('installed build to return = dac02fb9 shipment binary, pinned copy of session 146 (p.309(l)(5), p.300(b))',
      'BUILD_EXPECT="dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e"\n' in src
      and 'BUILD_PINNED="/c/kyty/s146/kyty_emulator_dac02fb9.exe"\n' in src and '9235a7ac' not in body)
check('installed sha checked before the lock and written inside the lock', src.index('the installed $GAME is not $BUILD_EXPECT before the series')
      < src.index('set -o noclobber') < src.index('tl "installed build at the start of the series sha256 $(sha "$GAME")')
      < src.index('trap finish EXIT'))
check('restore compares to BUILD_EXPECT', 'cp "$BUILD_PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$BUILD_EXPECT" ]' in src)
check('warm-up tags and hold (p.306(g) B2)', 'WARM="f6e_w1 f6e_w2"\n' in src and 'HOLDW="60"\n' in src)
b = case_body(src, 'f6e_w1')
check('w1: timestop_casino =0, no video, hold HOLDW', 'LV=$TC; EXTRA="KYTY_FIX_B9A=0"; WU=1; RECF=""; HH=$HOLDW' in b, b)
b = case_body(src, 'f6e_w2')
check('w2: mini_astro_clock_tower =0, no video, hold HOLDW', 'LV=$MA; EXTRA="KYTY_FIX_B9A=0"; WU=1; RECF=""; HH=$HOLDW' in b, b)
i_w = src.index('  if [ "$WU" = "1" ]; then')
check('warm-up returns after the run, before video and reader (not read)', src.index('  runtag ""') < i_w
      < src.index('python $VIDGLITCH') and src.index('    return 0', i_w) < src.index('python $VIDGLITCH')
      and src.index('    return 0', i_w) < src.index('f6e_read.py --tag $C'))
check('warm-up stop on death or window lines [I12]', "Unhandled exception:|--- Fatal Error ---|--- Error ---|GpuHangAbort:|ErrorDeviceLost|Window [0-9]+ minimized|Recovering Vulkan swapchain" in src
      and 'SC="continue: warm-up $C not read (p.306(g) B2)"' in src and 'SC="stop: warm-up $C death or window lines $WD [I12]"' in src)
check('warm-ups first, then the tags of p.287(v)(5)', 'for B in $WARM $SEQ; do' in src)
check('levels', 'TC=timestop_casino\n' in src and 'MA=mini_astro_clock_tower\n' in src)
check('hold 125 s wall [I] (reader: sum dt >= 120 s)', 'HOLD="125"\n' in src)
b = case_body(src, 'f6e_a1|f6e_a1f|f6e_a1r|f6e_a2|f6e_a2f|f6e_a2r')
check('a1, a2 (+f, r): timestop_casino KYTY_FIX_B9A=1', 'LV=$TC; EXTRA="KYTY_FIX_B9A=1"' in b, b)
b = case_body(src, 'f6e_b1|f6e_b1f|f6e_b1r')
check('b1 (+f, r): mini_astro_clock_tower KYTY_FIX_B9A=1', 'LV=$MA; EXTRA="KYTY_FIX_B9A=1"' in b, b)
b = case_body(src, 'f6e_c1|f6e_c1f')
check('c1 (+f): timestop_casino KYTY_FIX_B9A=0', 'LV=$TC; EXTRA="KYTY_FIX_B9A=0"' in b, b)
b = case_body(src, 'f6e_c2|f6e_c2f')
check('c2 (+f): mini_astro_clock_tower KYTY_FIX_B9A=0', 'LV=$MA; EXTRA="KYTY_FIX_B9A=0"' in b, b)
check('unknown tag stops', '*) tl "$C unknown tag - series stop"; return 1;;' in src)
check('glitch 4 6 and sheet for every video', 'python $VIDGLITCH rec_$C.mp4 4 6' in src and 'sheet142.py rec_$C.mp4 sheet_$C.png' in src)
check('stop check after every tag', 'f6e_read.py --stop-check runs/$C.read.json' in src)
check('form repeat once, then the stop check of the repeat (p.290(b)(2))', '"repeat-form: "*)' in src and 'C=${B}f' in src
      and src.count('onetag ||') == 3)
check('K3 repeats only after the series, by f6e_read --repeats with a times line', src.index('python $ROOT/f6e_read.py --repeats') > src.index('for B in $WARM $SEQ; do')
      and 'tl "K3 repeats (p.287(v)(5), executor line): $REP"' in src)
check('enter_scene rc != 0 stops', 'series stop: enter_scene rc $RC' in src)
check('summary at the end', 'f6e_read.py --summary > summary_f6e.txt' in src)
check('one retry of a BUSY refusal', src.count('runtag ""' + chr(10)) == 1 and src.count('runtag " (retry after a BUSY refusal)"') == 1)
check('lock.log UTC lines', 'echo "lock taken series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src and
      'echo "lock released series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src)


def make(binf='', bexp='', glr='', pred=None):
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    s = src.replace('ROOT=C:/kyty/f287/f6e', 'ROOT=%s' % FX)
    s = s.replace('LOCK=/c/kyty/SEALED_RUN.lock', 'LOCK=%s/LOCK' % unix(FX))
    s = s.replace('STOPF=/c/kyty/f287/STOP', 'STOPF=%s/STOP' % unix(FX))
    s = s.replace('TIMES=/c/kyty/f287/times.txt', 'TIMES=%s/times.txt' % unix(FX))
    s = re.sub(r'(?m)^BIN_F6E=".*"$', 'BIN_F6E="%s"' % binf, s, count=1)
    s = re.sub(r'(?m)^BIN_EXPECT=".*"$', 'BIN_EXPECT="%s"' % bexp, s, count=1)
    s = re.sub(r'(?m)^GLRESTORE=".*"$', 'GLRESTORE="%s"' % glr, s, count=1)
    open(os.path.join(FX, 'go_f6e.sh'), 'wb').write(s.encode('ascii'))
    if pred is not None:
        os.makedirs(os.path.join(FX, 'pred'))
        open(os.path.join(FX, 'pred', '03_f6e.md'), 'wb').write(pred.encode('ascii'))


def run(*args, env_add=None):
    env = dict(os.environ)
    env.pop('PLWAIT', None)
    env.pop('DRY', None)
    env.update(env_add or {})
    p = subprocess.run([BASH, FX + '/go_f6e.sh'] + list(args), capture_output=True, env=env)
    return p.returncode, p.stdout.decode('ascii', 'replace')


CALL = 'go_f6e call: PLWAIT=540 bash C:/kyty/f287/f6e/go_f6e.sh series\n'
make()
rc, out = run()
check('usage rc 2', rc == 2 and 'usage' in out, (rc, out))
rc, out = run('f6e_a1')
check('a tag instead of series rc 2', rc == 2, (rc, out))
rc, out = run('series')
check('not configured rc 2', rc == 2 and 'not configured' in out, (rc, out))
make('x.exe', 'ab', '')
rc, out = run('series')
check('GLRESTORE empty -> not configured rc 2', rc == 2, (rc, out))
make('x.exe', 'ab', '1')
rc, out = run('series')
check('configured, no seal -> rc 1', rc == 1 and 'seal' in out, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('DRY with the seal line rc 0', rc == 0 and out.startswith('DRY series'), (rc, out))
check('DRY plan names the knob values, precache default and the window', 'KYTY_FIX_B9A=1' in out and 'KYTY_FIX_B9A=0' in out and
      'win_f6e' in out and 'cachesig_f6e' in out and '--repeats' in out, out)
check('DRY plan names the warm-ups and HPP-353 (p.306(d), (g))', 'warm-up f6e_w1' in out and 'f6e_w2' in out and 'HPP-353' in out, out)
check('DRY plan names HPP-388, HPP-389, HPP-393 and the installed build check (seal 03)', 'HPP-388' in out and 'HPP-389' in out
      and 'HPP-393' in out and 'installed build sha' in out, out)
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='100'))
check('PLWAIT other than the seal rc 1', rc == 1, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='600'))
check('PLWAIT above 540 rc 2', rc == 2, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='x'))
check('PLWAIT not a number rc 2', rc == 2, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('two seal call lines rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL.replace('f6e/go_f6e.sh', 'f3d/go_f3d.sh'))
rc, out = run('series', env_add=dict(DRY='1'))
check('another call line rc 1', rc == 1, (rc, out))
for t in ('f6e_w1', 'f6e_w2', 'f6e_a1', 'f6e_c2', 'f6e_b1r', 'f6e_c1f'):
    make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
    open(os.path.join(FX, 'attempt_%s.txt' % t), 'w').write('x')
    rc, out = run('series', env_add=dict(DRY='1'))
    check('attempt marker %s -> rc 1 (one attempt)' % t, rc == 1 and 'attempt' in out, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
open(os.path.join(FX, 'f6e_a2r.json'), 'w').write('{}')
rc, out = run('series', env_add=dict(DRY='1'))
check('a repeat json -> rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
open(os.path.join(FX, 'LOCK'), 'w').write('someone')
rc, out = run('series', env_add=dict(DRY='1'))
check('lock held -> rc 4 before anything', rc == 4 and 'lock held' in out, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
open(os.path.join(FX, 'STOP'), 'w').write('p.999')
rc, out = run('series', env_add=dict(DRY='1'))
check('stop file -> rc 4', rc == 4 and 'stop file' in out and 'p.999' in out, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
rc, out = run('series')
check('configured, real path: missing fix binary -> rc 1 before any lock', rc == 1 and 'fix binary bad' in out
      and not os.path.exists(os.path.join(FX, 'LOCK')), (rc, out))
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)
