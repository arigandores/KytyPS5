"""test_go_f2c.py - fixtures of the cheap refusals of go_f2c.sh (F2c, HPP-310): usage, not configured, seal call line, one
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


src = open(os.path.join(HERE, 'go_f2c.sh'), 'rb').read().decode('ascii')
print('suite test_go_f2c.py sha256 %s target go_f2c.sh sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                  sha(os.path.join(HERE, 'go_f2c.sh'))))
check('script is ASCII', all(ord(c) < 128 for c in src))
check('script is LF', '\r' not in src)
check('KYTY_GPU_CHECKPOINTS never set', 'KYTY_GPU_CHECKPOINTS=' not in src)
check('every run KYTY_GPU_CLOCK_PIN=1', src.count('KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 >') == 1)
check('W form KYTY_PIPELINE_PRECACHE=0 on f2c_b only', src.count('EXTRA="KYTY_FIX_B26=1 KYTY_PIPELINE_PRECACHE=0 VK_LAYER_PATH=') == 1 and 'KYTY_PIPELINE_PRECACHE=0' not in src.split('f2c_b)')[1].split(';;')[1])
check('RC6 exact knob values', 'EXTRA="KYTY_FIX_B26=1"' in src and 'EXTRA="KYTY_FIX_B26=0"' in src)
check('no mutlib word in a command', 'mutlib ' not in src.replace("'mut_[a-z0-9_]*|test_[a-z0-9_]*f2c|mutlib'", ''))
check('no tail -F', 'tail -F' not in src)
check('restore in the EXIT trap', 'trap finish EXIT' in src and 'restore_bin' in src)
check('p.256(b) binary constant', 'BIN_F2C="/c/kyty/f287/bin/kyty_emulator_5821482a.exe"\n' in src
      and 'BIN_EXPECT="5821482a13a38bb9e42719b75fbd7b6e308a08c8e98caab02afb5398aac368dd"\n' in src)
check('p.256(v) GLRESTORE=1', 'GLRESTORE="1"\n' in src)
check('p.256(v) failed return writes the stop file', src.count('RETFAIL=1') == 4 and '> $STOPF' in src)
check('p.256(e) HPP-332 window right before the lock', src.index('win332_f2c.py 2>&1') < src.index('set -o noclobber')
      and src.index('busy "stop file $STOPF appeared before the lock"') < src.index('win332_f2c.py 2>&1'))
check('p.256(e) window closed or unknown -> busy', '*"-> open") ;;' in src and 'busy "lock window p.256(e) closed or unknown' in src)
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
    s = src.replace('ROOT=C:/kyty/f287/f2c', 'ROOT=%s' % FX)
    s = s.replace('LOCK=/c/kyty/SEALED_RUN.lock', 'LOCK=%s/LOCK' % unix(FX))
    s = s.replace('STOPF=/c/kyty/f287/STOP', 'STOPF=%s/STOP' % unix(FX))
    s = s.replace('TIMES=/c/kyty/f287/times.txt', 'TIMES=%s/times.txt' % unix(FX))
    s = re.sub(r'(?m)^BIN_F2C=".*"$', 'BIN_F2C="%s"' % binf, s, count=1)
    s = re.sub(r'(?m)^BIN_EXPECT=".*"$', 'BIN_EXPECT="%s"' % bexp, s, count=1)
    s = re.sub(r'(?m)^GLRESTORE=".*"$', 'GLRESTORE="%s"' % glr, s, count=1)
    open(os.path.join(FX, 'go_f2c.sh'), 'wb').write(s.encode('ascii'))
    if pred is not None:
        os.makedirs(os.path.join(FX, 'pred'))
        open(os.path.join(FX, 'pred', '01_f2c.md'), 'wb').write(pred.encode('ascii'))


def run(*args, env_add=None):
    env = dict(os.environ)
    env.pop('PLWAIT', None)
    env.pop('DRY', None)
    env.update(env_add or {})
    p = subprocess.run([BASH, FX + '/go_f2c.sh'] + list(args), capture_output=True, env=env)
    return p.returncode, p.stdout.decode('ascii', 'replace')


CALL = 'go_f2c call: PLWAIT=540 bash C:/kyty/f287/f2c/go_f2c.sh series\n'
make()
rc, out = run()
check('usage rc 2', rc == 2 and 'usage' in out, (rc, out))
rc, out = run('f2c_a')
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
check('DRY plan names the W form', 'KYTY_PIPELINE_PRECACHE=0' in out and 'KYTY_FIX_B26=0' in out)
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
open(os.path.join(FX, 'attempt_f2c_b.txt'), 'w').write('x')
rc, out = run('series', env_add=dict(DRY='1'))
check('an attempt marker -> rc 1 (one attempt)', rc == 1 and 'attempt' in out, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL)
open(os.path.join(FX, 'f2c_c.json'), 'w').write('{}')
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
