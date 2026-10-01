"""test_go_f4c.py - fixtures of the cheap refusals of go_f4c.sh (F4c, HPP-337): usage, not configured, seal call line, one
attempt, lock held, stop file, DRY plan.  A copy of the script with LOCK, STOPF and ROOT moved into fx/go - no real lock,
no guard, no install, no game.  Last line: ALL OK."""
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


src = open(os.path.join(HERE, 'go_f4c.sh'), 'rb').read().decode('ascii')
print('suite test_go_f4c.py sha256 %s target go_f4c.sh sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                  sha(os.path.join(HERE, 'go_f4c.sh'))))
check('script is ASCII', all(ord(c) < 128 for c in src))
check('script is LF', '\r' not in src)
check('KYTY_GPU_CHECKPOINTS never set', 'KYTY_GPU_CHECKPOINTS=' not in src)
check('every run KYTY_GPU_CLOCK_PIN=1', src.count('KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 >') == 1)
check('precache by default: KYTY_PIPELINE_PRECACHE never set, unset at start', 'KYTY_PIPELINE_PRECACHE=' not in src
      and 'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_DUALSRC KYTY_PIPELINE_PRECACHE' in src)
check('exact knob values', 'WX="KYTY_FIX_DUALSRC=1"' in src and '[ "$C" = "f4c_b" ] && WX="KYTY_FIX_DUALSRC=0"' in src)
check('W tags with validation, g with video only', 'f4c_b|f4c_a|f4c_v)' in src and 'f4c_g) SD=' in src
      and src.count('REC="--rec"') == 1 and src.count('--emu-arg=--vulkan-validation --emu-arg=true') == 1)
check('recipe file parsed before every tag', 'recipes143.py runs/recipes_$C.json' in src)
check('stop check after every tag', 'f4c_read.py --stop-check runs/$C.read.json' in src and '"continue"*) ;;' in src)
check('executor order B4', 'SEQ="f4c_b f4c_a f4c_v f4c_g"' in src)
check('no mutlib word in a command', 'mutlib ' not in src.replace("'mut_[a-z0-9_]*|test_[a-z0-9_]*f4c|mutlib'", ''))
check('no tail -F', 'tail -F' not in src)
check('restore in the EXIT trap', 'trap finish EXIT' in src and 'restore_bin' in src)
check('binary constant empty until the lead answers B1', 'BIN_F4C=""\n' in src and 'BIN_EXPECT=""\n' in src)
check('p.256(v) GLRESTORE=1', 'GLRESTORE="1"\n' in src)
check('failed binary or cache return writes the stop file', src.count('RETFAIL=1') == 5 and '> $STOPF' in src)
check('p.256(e) HPP-332 window right before the lock', src.index('win332_f2c.py 2>&1') < src.index('set -o noclobber')
      and src.index('busy "stop file $STOPF appeared before the lock"') < src.index('win332_f2c.py 2>&1'))
check('p.256(e) window closed or unknown -> busy', '*"-> open") ;;' in src and 'busy "lock window closed or unknown' in src)
sys.path.insert(0, HERE)
import win332_f2c as W  # noqa: E402
check('win332 in_progress closed rc 5', W.decide('in_progress') == (5, 'closed'))
check('win332 done closed rc 5', W.decide('done') == (5, 'closed'))
check('win332 blocked open rc 0', W.decide('blocked') == (0, 'open'))
check('win332 todo open rc 0', W.decide('todo') == (0, 'open'))
check('win332 no answer rc 6', W.decide(None) == (6, 'error') and W.decide('') == (6, 'error'))
pw = subprocess.run([sys.executable, os.path.join(HERE, 'win332_f2c.py')], capture_output=True,
                    env={k: v for k, v in os.environ.items() if not k.startswith('PAPERCLIP_') and k != 'PYTHONIOENCODING'})
check('win332 without API env refuses rc 6, ASCII line (cp1250)', pw.returncode == 6 and pw.stdout.decode('cp1250').startswith('win332 HPP-332 status None'), pw)
check('cache is moved, never rm -rf on the game cache', 'rm -rf "$CACHE"' not in src and 'mv "$CACHE" "$KEEP/"' in src)


def make(binf='', bexp='', glr='', pred=None):
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    s = src.replace('ROOT=C:/kyty/f287/f4c', 'ROOT=%s' % FX)
    s = s.replace('LOCK=/c/kyty/SEALED_RUN.lock', 'LOCK=%s/LOCK' % unix(FX))
    s = s.replace('STOPF=/c/kyty/f287/STOP', 'STOPF=%s/STOP' % unix(FX))
    s = s.replace('TIMES=/c/kyty/f287/times.txt', 'TIMES=%s/times.txt' % unix(FX))
    s = re.sub(r'(?m)^BIN_F4C=".*"$', 'BIN_F4C="%s"' % binf, s, count=1)
    s = re.sub(r'(?m)^BIN_EXPECT=".*"$', 'BIN_EXPECT="%s"' % bexp, s, count=1)
    s = re.sub(r'(?m)^GLRESTORE=".*"$', 'GLRESTORE="%s"' % glr, s, count=1)
    open(os.path.join(FX, 'go_f4c.sh'), 'wb').write(s.encode('ascii'))
    if pred is not None:
        os.makedirs(os.path.join(FX, 'pred'))
        open(os.path.join(FX, 'pred', 'f4c.md'), 'wb').write(pred.encode('ascii'))


def run(*args, env_add=None):
    env = dict(os.environ)
    env.pop('PLWAIT', None)
    env.pop('DRY', None)
    env.update(env_add or {})
    p = subprocess.run([BASH, FX + '/go_f4c.sh'] + list(args), capture_output=True, env=env)
    return p.returncode, p.stdout.decode('ascii', 'replace')


CALL = 'go_f4c call: PLWAIT=540 bash C:/kyty/f287/f4c/go_f4c.sh series\n'
make()
rc, out = run()
check('usage rc 2', rc == 2 and 'usage' in out, (rc, out))
rc, out = run('f4c_a')
check('a tag instead of series rc 2', rc == 2, (rc, out))
rc, out = run('series')
check('not configured rc 2', rc == 2 and 'not configured' in out, (rc, out))
make('x.exe', 'ab', '')
rc, out = run('series')
check('GLRESTORE empty -> not configured rc 2', rc == 2, (rc, out))
make('x.exe', 'ab', '0')
rc, out = run('series')
check('configured, no seal -> rc 1', rc == 1 and 'seal' in out, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('DRY with the seal line rc 0', rc == 0 and out.startswith('DRY series'), (rc, out))
check('DRY plan names the knob values and precache by default', 'KYTY_FIX_DUALSRC=0' in out and '=1' in out and 'precache by default' in out)
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='100'))
check('PLWAIT other than the seal rc 1', rc == 1, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='600'))
check('PLWAIT above 540 rc 2', rc == 2, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='x'))
check('PLWAIT not a number rc 2', rc == 2, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('two seal call lines rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL)
open(os.path.join(FX, 'attempt_f4c_v.txt'), 'w').write('x')
rc, out = run('series', env_add=dict(DRY='1'))
check('an attempt marker -> rc 1 (one attempt)', rc == 1 and 'attempt' in out, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL)
open(os.path.join(FX, 'f4c_g.json'), 'w').write('{}')
rc, out = run('series', env_add=dict(DRY='1'))
check('a tag json -> rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL)
open(os.path.join(FX, 'LOCK'), 'w').write('someone')
rc, out = run('series', env_add=dict(DRY='1'))
check('lock held -> rc 4 before anything', rc == 4 and 'lock held' in out, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL)
open(os.path.join(FX, 'STOP'), 'w').write('p.999')
rc, out = run('series', env_add=dict(DRY='1'))
check('stop file -> rc 4', rc == 4 and 'stop file' in out and 'p.999' in out, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL)
rc, out = run('series')
check('configured, real path: missing fix binary -> rc 1 before any lock', rc == 1 and 'fix binary bad' in out
      and not os.path.exists(os.path.join(FX, 'LOCK')), (rc, out))
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)
