"""test_go_f4c.py - fixtures of the cheap refusals of go_f4c.sh (F4c, HPP-337): usage, not configured, seal call line, one
attempt, lock held, stop file, DRY plan, binary strings (p.262(v)), stand A/Bp, window win_f4c (p.268(d), 270(d)).  A copy of the script with LOCK, STOPF and ROOT moved into fx/go - no real lock,
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
      and 'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_DUALSRC KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW\n' in src)
check('KYTY_FIX_B26 and KYTY_S_PCW never passed', 'KYTY_FIX_B26=' not in src and 'KYTY_S_PCW=' not in src and 'B26X' not in src)
check('p.262(e) hold W 310 / V 330', 'VHOLD="330"\nWHOLD="310"\n' in src)
check('p.262(g) pre-check before b and a, stop before the tag', 'f4c_read.py --pre-check $C' in src
      and src.index('--pre-check $C') < src.index('python $ROOT/enter_scene.py') and 'series stop before the tag' in src
      and '    f4c_b|f4c_a)\n      PC=' in src)
check('p.262(v) binary strings before the lock', 'SIGSTR="699c1e4b7db359067b461e029b913c4b6e78dc90"' in src
      and src.index('fix binary strings bad') < src.index('set -o noclobber'))
check('exact knob values', 'WX="KYTY_FIX_DUALSRC=1"' in src and '[ "$C" = "f4c_b" ] && WX="KYTY_FIX_DUALSRC=0"' in src)
check('W tags with validation, g with video only', 'f4c_b|f4c_a|f4c_v)' in src and 'f4c_g) SD=' in src
      and src.count('REC="--rec"') == 1 and src.count('--emu-arg=--vulkan-validation --emu-arg=true') == 1)
check('recipe file parsed before every tag', 'recipes143.py runs/recipes_$C.json' in src)
check('stop check after every tag', 'f4c_read.py --stop-check runs/$C.read.json' in src and '"continue"*) ;;' in src)
check('stand A order (b) (a) (v) (g), Bp (g) (b) (a) (v), stand constant A', 'STAND="A"\n' in src
      and '  A) SEQ="f4c_b f4c_a f4c_v f4c_g";;' in src and '  Bp) SEQ="f4c_g f4c_b f4c_a f4c_v";;' in src)
check('no mutlib word in a command', 'mutlib ' not in src.replace("'mut_[a-z0-9_]*|test_[a-z0-9_]*f4c|mutlib'", ''))
check('no tail -F', 'tail -F' not in src)
check('restore in the EXIT trap', 'trap finish EXIT' in src and 'restore_bin' in src)
check('binary constants of p.268(v)', 'BIN_F4C="C:/kyty/f287/bin/kyty_emulator_c9a5e198.exe"\n' in src
      and 'BIN_EXPECT="c9a5e1986e254132f776f0c7f1c9446d0bdc862e199bbbc1d57aedf17d4c9f9b"\n' in src)
check('p.256(v) GLRESTORE=1', 'GLRESTORE="1"\n' in src)
check('failed binary or cache return writes the stop file', src.count('RETFAIL=1') == 5 and '> $STOPF' in src)
check('p.268(d) window right before the lock', src.index('win_f4c.py 2>&1') < src.index('set -o noclobber')
      and src.index('busy "stop file $STOPF appeared before the lock"') < src.index('win_f4c.py 2>&1') and 'win332' not in src)
check('p.256(e) window closed or unknown -> busy', '*"-> open") ;;' in src and 'busy "lock window closed or unknown' in src)
sys.path.insert(0, HERE)
import win_f4c as W  # noqa: E402
OPEN = {'HPP-333': ('done', None), 'HPP-347': ('done', None), 'HPP-328': ('blocked', None)}
check('win open: audit and F4b2 done, P10 blocked', W.decide(OPEN) == (0, 'open'))
check('win open: P10 done', W.decide(dict(OPEN, **{'HPP-328': ('done', None)})) == (0, 'open'))
check('win closed: audit blocked', W.decide(dict(OPEN, **{'HPP-333': ('blocked', None)})) == (5, 'closed'))
check('win closed: audit in_progress', W.decide(dict(OPEN, **{'HPP-333': ('in_progress', 'r1')})) == (5, 'closed'))
check('win closed: audit done but a run alive', W.decide(dict(OPEN, **{'HPP-333': ('done', 'r1')})) == (5, 'closed'))
check('win closed: F4b2 in_review', W.decide(dict(OPEN, **{'HPP-347': ('in_review', None)})) == (5, 'closed'))
check('win closed: P10 todo (P before F)', W.decide(dict(OPEN, **{'HPP-328': ('todo', None)})) == (5, 'closed'))
check('win closed: P10 in_progress', W.decide(dict(OPEN, **{'HPP-328': ('in_progress', None)})) == (5, 'closed'))
check('win closed: P10 blocked with a run', W.decide(dict(OPEN, **{'HPP-328': ('blocked', 'r2')})) == (5, 'closed'))
check('win error: one answer missing', W.decide(dict(OPEN, **{'HPP-347': (None, None)})) == (6, 'error')
      and W.decide({}) == (6, 'error') and W.decide(dict(OPEN, **{'HPP-328': ('', None)})) == (6, 'error'))
pw = subprocess.run([sys.executable, os.path.join(HERE, 'win_f4c.py')], capture_output=True,
                    env={k: v for k, v in os.environ.items() if not k.startswith('PAPERCLIP_') and k != 'PYTHONIOENCODING'})
check('win_f4c without API env refuses rc 6, ASCII line (cp1250)', pw.returncode == 6 and pw.stdout.decode('cp1250').startswith('win_f4c HPP-333 None'), pw)
check('cache is moved, never rm -rf on the game cache', 'rm -rf "$CACHE"' not in src and 'mv "$CACHE" "$KEEP/"' in src)


def make(binf='', bexp='', glr='', pred=None, stand='A'):
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    s = src.replace('ROOT=C:/kyty/f287/f4c', 'ROOT=%s' % FX)
    s = s.replace('LOCK=/c/kyty/SEALED_RUN.lock', 'LOCK=%s/LOCK' % unix(FX))
    s = s.replace('STOPF=/c/kyty/f287/STOP', 'STOPF=%s/STOP' % unix(FX))
    s = s.replace('TIMES=/c/kyty/f287/times.txt', 'TIMES=%s/times.txt' % unix(FX))
    s = re.sub(r'(?m)^BIN_F4C=".*"$', 'BIN_F4C="%s"' % binf, s, count=1)
    s = re.sub(r'(?m)^BIN_EXPECT=".*"$', 'BIN_EXPECT="%s"' % bexp, s, count=1)
    s = re.sub(r'(?m)^GLRESTORE=".*"$', 'GLRESTORE="%s"' % glr, s, count=1)
    s = re.sub(r'(?m)^STAND=".*"$', 'STAND="%s"' % stand, s, count=1)
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
check('DRY plan names stand A, its order, win_f4c and the pre-check', 'stand A tags f4c_b f4c_a f4c_v f4c_g' in out
      and 'win_f4c' in out and 'pre-check' in out, out)
make('x.exe', 'ab', '0', pred='# seal\n' + CALL, stand='Bp')
rc, out = run('series', env_add=dict(DRY='1'))
check('DRY stand Bp order (g) (b) (a) (v)', rc == 0 and 'stand Bp tags f4c_g f4c_b f4c_a f4c_v' in out, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL, stand='X')
rc, out = run('series', env_add=dict(DRY='1'))
check('unknown stand -> not configured rc 2', rc == 2 and 'not configured' in out, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL)
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
SIG = b'699c1e4b7db359067b461e029b913c4b6e78dc90'
PAT = b'DualSrcBlend: patched ps=%016'
for nm, body, stand, want in (('strings: patched only, stand A -> rc 1 strings bad', b'x' + PAT + b'x', 'A', 'fix binary strings bad'),
                              ('strings: signature only -> rc 1 strings bad', b'x' + SIG + b'x', 'A', 'fix binary strings bad'),
                              ('strings: both, stand A -> passes the strings (gate file next)', SIG + b'\x00' + PAT, 'A', 'gate file bad'),
                              ('strings: patched only, stand Bp -> passes the strings', b'x' + PAT, 'Bp', 'gate file bad')):
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    fb = os.path.join(FX, 'fake.exe')
    open(fb, 'wb').write(body)
    hb = sha(fb)
    make(fb.replace('\\', '/'), hb, '1', pred='# seal\n' + CALL, stand=stand)
    open(fb, 'wb').write(body)
    rc, out = run('series')
    check(nm, rc == 1 and want in out and not os.path.exists(os.path.join(FX, 'LOCK')), (rc, out))
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)
