"""test_go_f3d.py - fixtures of go_f3d.sh (F3d, HPP-342): the static form of the script (constants of p.259(e)(5) and p.277(b),
knob values, W form, binary check before every tag, cache and directory lists, GLCache return, lock window, seal call) and
the cheap refusals: usage, not configured, seal call line, one attempt, lock held, stop file, DRY plan, missing fix binary.
A copy of the script with LOCK, STOPF, TIMES and ROOT moved into fx/go - no real lock, no guard, no install, no game.
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


def case_body(s, tag):
    i = s.index('    %s) ' % tag)
    return s[i:s.index(';;', i)]


src = open(os.path.join(HERE, 'go_f3d.sh'), 'rb').read().decode('ascii')
print('suite test_go_f3d.py sha256 %s target go_f3d.sh sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                  sha(os.path.join(HERE, 'go_f3d.sh'))))
check('script is ASCII', all(ord(c) < 128 for c in src))
check('script is LF', '\r' not in src)
check('KYTY_GPU_CHECKPOINTS never set', 'KYTY_GPU_CHECKPOINTS=' not in src)
check('every run KYTY_GPU_CLOCK_PIN=1', src.count('KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 >') == 1)
check('no mutlib word in a command', 'mutlib ' not in src.replace("'mut_[a-z0-9_]*|test_[a-z0-9_]*f3d|mutlib'", ''))
check('no tail -F', 'tail -F' not in src)
check('restore in the EXIT trap', 'trap finish EXIT' in src and 'restore_bin' in src)
check('p.277(b)(4) binary constant = F3b copy 2e6df8f0', 'BIN_F3D="C:/kyty/f287/bin/kyty_emulator_2e6df8f0.exe"\n' in src
      and 'BIN_EXPECT="2e6df8f09f006ef8d49173bd4abccea074da94769c5c31b9caeeaadc3eaf74ae"\n' in src)
check('p.277(b)(4) binary check before every tag', src.index('binary check failed (p.277(b)(4))') > src.index('for C in $SEQ; do\n  if [ -e $STOPF ]')
      and '[ "$(sha "$BIN_F3D")" != "$BIN_EXPECT" ] || [ "$(sha "$GAME")" != "$BIN_EXPECT" ]' in src)
check('no build command', 'build_local' not in src and 'cmake' not in src and 'ninja' not in src)
check('p.256(v) GLRESTORE=1', 'GLRESTORE="1"\n' in src)
check('failed return writes the stop file', src.count('RETFAIL=1') == 5 and '> $STOPF' in src)
check('p.277(b)(2) directory list before and after', 'DIRS_BEFORE=$(dirlist "$CACHE")' in src and
      '[ "$DIRS_BACK" = "$DIRS_BEFORE" ]' in src and '[ "$DIRS_SNAP" = "$DIRS_BEFORE" ]' in src)
check('cache is moved, never rm -rf on the game cache', 'rm -rf "$CACHE"' not in src and 'mv "$CACHE" "$KEEP/"' in src)
check('GLCache is moved, never rm -rf', 'rm -rf "$GLDIR"' not in src and 'mv "$GLDIR" "$GLKEEP/"' in src)
check('lock window right before the lock', src.index('win_f3d.py 2>&1') < src.index('set -o noclobber')
      and src.index('busy "stop file $STOPF appeared before the lock"') < src.index('win_f3d.py 2>&1'))
check('window closed or unknown -> busy', '*"-> open") ;;' in src and 'busy "lock window closed or unknown' in src)
check('seq of p.259(e)(5)', 'SEQ="f3d_a1 f3d_a2 f3d_a3 f3d_a4 f3d_bv f3d_bw f3d_c1 f3d_c2"\n' in src)
check('levels', 'BH=big_hand_pirate_island\n' in src and 'VW=voxel_world\n' in src and 'SKY=underwater_aerial_garden\n' in src)
check('holds 120 / 330 / 310', 'HOLDA="120"\n' in src and 'VHOLD="330"\n' in src and 'WHOLD="310"\n' in src)
for t, lv, fx, rec in (('f3d_a1', '$BH', '1', False), ('f3d_a2', '$BH', '1', True), ('f3d_a3', '$VW', '1', False),
                       ('f3d_a4', '$VW', '1', True), ('f3d_c1', '$BH', '0', False), ('f3d_c2', '$VW', '0', False)):
    b = case_body(src, t)
    check('%s level %s, KYTY_FIX_B1B=%s exactly, video %s' % (t, lv, fx, rec),
          'LV=%s;' % lv in b and 'EXTRA="KYTY_FIX_B1B=%s"' % fx in b and (('REC="--rec"' in b) == rec), b)
b = case_body(src, 'f3d_bv')
check('bv Sky V =1 video hold 330 stable 300', 'LV=$SKY' in b and 'EXTRA="KYTY_FIX_B1B=1"' in b and 'REC="--rec"' in b
      and 'HOLD=$VHOLD' in b and '--stable-draws 300' in b and 'vulkan' not in b, b)
b = case_body(src, 'f3d_bw')
check('bw Sky W =1, p.254(e) form, hold 310, no video', 'LV=$SKY' in b and 'HOLD=$WHOLD' in b and
      '--emu-arg=--vulkan-validation --emu-arg=true' in b and 'KYTY_FIX_B1B=1 KYTY_PIPELINE_PRECACHE=0 VK_LAYER_PATH=$VKLAYER' in b
      and 'REC=' not in b, b)
check('KYTY_PIPELINE_PRECACHE=0 only in bw (outside the header and the DRY plan line)', sum(l.count('KYTY_PIPELINE_PRECACHE=0') for l in src.split(chr(10)) if not l.startswith('  echo "DRY') and not l.startswith('#')) == 1)
check('KYTY_FIX_B26 never passed', 'KYTY_FIX_B26=' not in src)
check('knob variables unset at the start', 'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_B1B' in src)
check('pair sheet for bv against v142', 'sheetpair_f3d.py $REFV rec_$C.mp4 sheetpair_$C.png' in src and 'REFV=C:/kyty/s142/rec_v142.mp4\n' in src)
check('glitch 4 6 for every video', 'python $VIDGLITCH rec_$C.mp4 4 6' in src)
check('stop check after every tag', 'f3d_read.py --stop-check runs/$C.read.json' in src)
check('enter_scene rc != 0 stops', 'series stop: enter_scene rc $RC' in src)
check('summary at the end', 'f3d_read.py --summary > summary_f3d.txt' in src)
check('one retry of a BUSY refusal', src.count('runtag ""' + chr(10)) == 1 and src.count('runtag " (retry after a BUSY refusal)"') == 1)
check('lock.log UTC lines', 'echo "lock taken series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src and
      'echo "lock released series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src)
sys.path.insert(0, HERE)


def make(binf='', bexp='', glr='', pred=None):
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    s = src.replace('ROOT=C:/kyty/f287/f3d', 'ROOT=%s' % FX)
    s = s.replace('LOCK=/c/kyty/SEALED_RUN.lock', 'LOCK=%s/LOCK' % unix(FX))
    s = s.replace('STOPF=/c/kyty/f287/STOP', 'STOPF=%s/STOP' % unix(FX))
    s = s.replace('TIMES=/c/kyty/f287/times.txt', 'TIMES=%s/times.txt' % unix(FX))
    s = re.sub(r'(?m)^BIN_F3D=".*"$', 'BIN_F3D="%s"' % binf, s, count=1)
    s = re.sub(r'(?m)^BIN_EXPECT=".*"$', 'BIN_EXPECT="%s"' % bexp, s, count=1)
    s = re.sub(r'(?m)^GLRESTORE=".*"$', 'GLRESTORE="%s"' % glr, s, count=1)
    open(os.path.join(FX, 'go_f3d.sh'), 'wb').write(s.encode('ascii'))
    if pred is not None:
        os.makedirs(os.path.join(FX, 'pred'))
        open(os.path.join(FX, 'pred', '01_f3d.md'), 'wb').write(pred.encode('ascii'))


def run(*args, env_add=None):
    env = dict(os.environ)
    env.pop('PLWAIT', None)
    env.pop('DRY', None)
    env.update(env_add or {})
    p = subprocess.run([BASH, FX + '/go_f3d.sh'] + list(args), capture_output=True, env=env)
    return p.returncode, p.stdout.decode('ascii', 'replace')


CALL = 'go_f3d call: PLWAIT=540 bash C:/kyty/f287/f3d/go_f3d.sh series\n'
make()
rc, out = run()
check('usage rc 2', rc == 2 and 'usage' in out, (rc, out))
rc, out = run('f3d_a1')
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
check('DRY plan names the knob values and the W form', 'KYTY_FIX_B1B=1' in out and 'KYTY_FIX_B1B=0' in out and
      'KYTY_PIPELINE_PRECACHE=0' in out and 'win_f3d' in out, out)
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='100'))
check('PLWAIT other than the seal rc 1', rc == 1, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='600'))
check('PLWAIT above 540 rc 2', rc == 2, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='x'))
check('PLWAIT not a number rc 2', rc == 2, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('two seal call lines rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL.replace('f3d/go_f3d.sh', 'f2c/go_f2c.sh'))
rc, out = run('series', env_add=dict(DRY='1'))
check('another call line rc 1', rc == 1, (rc, out))
for t in ('f3d_a1', 'f3d_c2'):
    make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
    open(os.path.join(FX, 'attempt_%s.txt' % t), 'w').write('x')
    rc, out = run('series', env_add=dict(DRY='1'))
    check('attempt marker %s -> rc 1 (one attempt)' % t, rc == 1 and 'attempt' in out, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
open(os.path.join(FX, 'f3d_bw.json'), 'w').write('{}')
rc, out = run('series', env_add=dict(DRY='1'))
check('a tag json -> rc 1', rc == 1, (rc, out))
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
