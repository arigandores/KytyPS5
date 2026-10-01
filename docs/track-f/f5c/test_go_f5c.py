"""test_go_f5c.py - fixtures of go_f5c.sh (F5c, HPP-357); port of C:/kyty/f287/f4c/test_go_f4c2.py: the constants of the
letter (p.273(e)(3), 285(v)), the cheap refusals (usage, not configured, seal call line, one attempt, lock held, stop file, DRY
plan, binary strings), the window win_f5c, the wrappers.  A copy of the script with LOCK, STOPF, ROOT and TIMES moved into fx/go -
no real lock, no guard, no install, no game.  Last line: ALL OK."""
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
    print('%-4s %s' % ('ok' if cond else 'FAIL', name))
    if not cond:
        FAIL.append(name)
        print('     detail %s' % (detail,))


def unix(p):
    return '/' + p[0].lower() + p[2:] if p[1] == ':' else p


src = open(os.path.join(HERE, 'go_f5c.sh'), 'rb').read().decode('ascii')
print('suite test_go_f5c.py sha256 %s target go_f5c.sh sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                 sha(os.path.join(HERE, 'go_f5c.sh'))))
for nm in ('go_f5c.sh', 'win_f5c.py', 'next_f5c.sh', 'wait_f5c.sh', 'f5c_read.py', 'test_f5c_read.py'):
    b = open(os.path.join(HERE, nm), 'rb').read()
    check('%s is ASCII and LF' % nm, all(c < 128 for c in b) and b'\r' not in b)
check('KYTY_GPU_CHECKPOINTS never set', 'KYTY_GPU_CHECKPOINTS=' not in src)
check('every run stand + KYTY_GPU_CLOCK_PIN=1', src.count('KYTY_TEST_MINIMIZE=$STANDV KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 >') == 1
      and 'STANDV="60:10"\n' in src)
check('unset at start: fix knobs, precache, stand, filter', 'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_DUALSRC '
      'KYTY_FIX_B1B KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW KYTY_PVAR KYTY_FIX_MINIMIZE KYTY_TEST_MINIMIZE KYTY_REC '
      'VK_LAYER_MESSAGE_ID_FILTER\n' in src)
check('other fix knobs never passed', all(('%s=' % k) not in src for k in ('KYTY_FIX_B26', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_B1B', 'KYTY_S_PCW', 'KYTY_PVAR')))
check('hold W 310 / V 330 (p.273(e)(3)(a), (v))', 'VHOLD="330"\nWHOLD="310"\n' in src)
check('order (a) (b) (v) (g)', 'SEQ="f5c_a f5c_b f5c_v f5c_g"\n' in src)
check('form W p.273(k)(2): validation + precache 0 + one filter', src.count('--emu-arg=--vulkan-validation --emu-arg=true') == 1
      and 'EXTRA="$WX KYTY_PIPELINE_PRECACHE=0 VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER";;' in src
      and 'VKFILTER="Undefined-Value-ShaderOutputNotConsumed-DynamicRendering"\n' in src and '    f5c_a|f5c_b)\n' in src)
check('exact knob values', 'WX="KYTY_FIX_MINIMIZE=1"; [ "$C" = "f5c_b" ] && WX="KYTY_FIX_MINIMIZE=0"' in src
      and 'f5c_v) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec"; EXTRA="KYTY_FIX_MINIMIZE=1";;' in src
      and 'f5c_g) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; EXTRA="KYTY_FIX_MINIMIZE=0";;' in src)
check('video only in (v)', src.count('REC="--rec"') == 1)
NODRY = ''.join(l for l in src.splitlines(True) if not l.startswith('  echo "DRY series') and not l.startswith('#'))
check('V tags without precache knob and filter (outside the DRY text)', NODRY.count('KYTY_PIPELINE_PRECACHE=0') == 1
      and NODRY.count('VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER') == 1)
check('binary constants of p.285(v)', 'BIN_F5C="C:/kyty/f287/bin/kyty_emulator_6f495a65.exe"\n' in src
      and 'BIN_EXPECT="6f495a65388a90a0381c9170f224777e84cb07d657115ad2a8662fa0bae168dd"\n' in src)
check('binary strings before the lock', 'SIGSTR="699c1e4b7db359067b461e029b913c4b6e78dc90"' in src
      and src.index('fix binary strings bad') < src.index('set -o noclobber') and '"SwapchainZeroExtent: begin" "$BIN_F5C"' in src
      and '"TestMinimize: armed" "$BIN_F5C"' in src)
check('stop check after every tag', 'f5c_read.py --stop-check runs/$C.read.json' in src and '"continue"*) ;;' in src)
check('glitch, idx sha and sheet after the video tag', 'python $VIDGLITCH rec_$C.mp4 4 6' in src and 'idx sha256 $(sha rec_$C.mp4.idx)' in src
      and 'sheet142.py rec_$C.mp4 sheet_$C.png' in src)
check('no mutlib word in a command', 'mutlib ' not in src.replace("'mut_[a-z0-9_]*|test_[a-z0-9_]*f5c|mutlib'", ''))
check('no tail -F', 'tail -F' not in src)
check('restore in the EXIT trap', 'trap finish EXIT' in src and 'restore_bin' in src)
check('GLRESTORE=1', 'GLRESTORE="1"\n' in src)
check('failed binary or cache return writes the stop file', src.count('RETFAIL=1') == 5 and '> $STOPF' in src)
check('window right before the lock', src.index('win_f5c.py 2>&1') < src.index('set -o noclobber')
      and src.index('busy "stop file $STOPF appeared before the lock"') < src.index('win_f5c.py 2>&1'))
check('window closed or unknown -> busy', '*"-> open") ;;' in src and 'busy "lock window closed or unknown' in src)
check('cache is moved, never rm -rf on the game cache', 'rm -rf "$CACHE"' not in src and 'mv "$CACHE" "$KEEP/"' in src)
check('idle wait before every tag, one retry of a BUSY refusal', src.index('if ! idlewait $C; then') < src.index('  runtag ""')
      and src.count('runtag "') == 2 and src.count('if refused $RC; then') == 2 and 'second BUSY refusal' in src)
check('lock.log UTC lines', '"lock taken series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src
      and '"lock released series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src)
nx = open(os.path.join(HERE, 'next_f5c.sh'), 'rb').read().decode('ascii')
check('next_f5c: stop file and lock first, the seal call verbatim', nx.index('C:/kyty/f287/STOP') < nx.index('nohup')
      and nx.index('SEALED_RUN.lock') < nx.index('nohup') and "PLWAIT=540 bash C:/kyty/f287/f5c/go_f5c.sh series >" in nx)
sys.path.insert(0, HERE)
import win_f5c as W  # noqa: E402
OPEN = {'HPP-367': ('done', None), 'HPP-342': ('done', None), 'HPP-337': ('done', None), 'HPP-350': ('done', None),
        'HPP-352': ('blocked', None), 'HPP-364': ('blocked', None), 'HPP-370': ('blocked', None)}
check('win open', W.decide(OPEN) == (0, 'open'))
check('win open: s145 step 0 in_review without a run', W.decide(dict(OPEN, **{'HPP-350': ('in_review', None)})) == (0, 'open'))
check('win closed: s145 step 0 in_progress', W.decide(dict(OPEN, **{'HPP-350': ('in_progress', 'r')})) == (5, 'closed'))
check('win closed: s145 step 0 blocked with a run', W.decide(dict(OPEN, **{'HPP-350': ('blocked', 'r')})) == (5, 'closed'))
check('win closed: s145 series todo', W.decide(dict(OPEN, **{'HPP-352': ('todo', None)})) == (5, 'closed'))
check('win closed: s145 series in_progress', W.decide(dict(OPEN, **{'HPP-352': ('in_progress', 'r')})) == (5, 'closed'))
check('win open: s145 series done', W.decide(dict(OPEN, **{'HPP-352': ('done', None)})) == (0, 'open'))
check('win closed: P17 todo (P before F)', W.decide(dict(OPEN, **{'HPP-364': ('todo', None)})) == (5, 'closed'))
check('win closed: FSc in_progress', W.decide(dict(OPEN, **{'HPP-370': ('in_progress', None)})) == (5, 'closed'))
check('win closed: F5b2 in_review', W.decide(dict(OPEN, **{'HPP-367': ('in_review', None)})) == (5, 'closed'))
check('win closed: F3d done with a run', W.decide(dict(OPEN, **{'HPP-342': ('done', 'r')})) == (5, 'closed'))
check('win error: an answer missing', W.decide(dict(OPEN, **{'HPP-337': (None, None)})) == (6, 'error') and W.decide({}) == (6, 'error'))
pw = subprocess.run([sys.executable, os.path.join(HERE, 'win_f5c.py')], capture_output=True,
                    env={k: v for k, v in os.environ.items() if not k.startswith('PAPERCLIP_') and k != 'PYTHONIOENCODING'})
check('win_f5c without API env refuses rc 6, ASCII line (cp1250)', pw.returncode == 6 and pw.stdout.decode('cp1250').startswith('win_f5c HPP-367 None'), pw)


def make(binf='', bexp='', glr='', pred=None):
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    s = src.replace('ROOT=C:/kyty/f287/f5c', 'ROOT=%s' % FX)
    s = s.replace('LOCK=/c/kyty/SEALED_RUN.lock', 'LOCK=%s/LOCK' % unix(FX))
    s = s.replace('STOPF=/c/kyty/f287/STOP', 'STOPF=%s/STOP' % unix(FX))
    s = s.replace('TIMES=/c/kyty/f287/times.txt', 'TIMES=%s/times.txt' % unix(FX))
    s = re.sub(r'(?m)^BIN_F5C=".*"$', 'BIN_F5C="%s"' % binf, s, count=1)
    s = re.sub(r'(?m)^BIN_EXPECT=".*"$', 'BIN_EXPECT="%s"' % bexp, s, count=1)
    s = re.sub(r'(?m)^GLRESTORE=".*"$', 'GLRESTORE="%s"' % glr, s, count=1)
    open(os.path.join(FX, 'go_f5c.sh'), 'wb').write(s.encode('ascii'))
    if pred is not None:
        os.makedirs(os.path.join(FX, 'pred'))
        open(os.path.join(FX, 'pred', 'f5c.md'), 'wb').write(pred.encode('ascii'))


def run(*args, env_add=None):
    env = dict(os.environ)
    env.pop('PLWAIT', None)
    env.pop('DRY', None)
    env.update(env_add or {})
    p = subprocess.run([BASH, FX + '/go_f5c.sh'] + list(args), capture_output=True, env=env)
    return p.returncode, p.stdout.decode('ascii', 'replace')


CALL = 'go_f5c call: PLWAIT=540 bash C:/kyty/f287/f5c/go_f5c.sh series\n'
make()
rc, out = run()
check('usage rc 2', rc == 2 and 'usage' in out, (rc, out))
rc, out = run('f5c_a')
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
check('DRY plan names the tags, the stand, the filter and win_f5c', 'tags f5c_a f5c_b f5c_v f5c_g' in out and 'KYTY_TEST_MINIMIZE=60:10' in out
      and 'VK_LAYER_MESSAGE_ID_FILTER=Undefined-Value-ShaderOutputNotConsumed-DynamicRendering' in out and 'win_f5c' in out, out)
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='100'))
check('PLWAIT other than the seal rc 1', rc == 1, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='600'))
check('PLWAIT above 540 rc 2', rc == 2, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='x'))
check('PLWAIT not a number rc 2', rc == 2, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('two seal call lines rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', '0', pred='# seal\n' + CALL.replace('go_f5c call', 'go_f4c2 call'))
rc, out = run('series', env_add=dict(DRY='1'))
check('a foreign call line rc 1', rc == 1, (rc, out))
for fn in ('attempt_f5c_v.txt', 'f5c_g.json'):
    make('x.exe', 'ab', '0', pred='# seal\n' + CALL)
    open(os.path.join(FX, fn), 'w').write('x')
    rc, out = run('series', env_add=dict(DRY='1'))
    check('%s -> rc 1 (one attempt)' % fn, rc == 1 and 'attempt' in out, (rc, out))
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
check('real path: missing fix binary -> rc 1 before any lock', rc == 1 and 'fix binary bad' in out
      and not os.path.exists(os.path.join(FX, 'LOCK')), (rc, out))
SIG = b'699c1e4b7db359067b461e029b913c4b6e78dc90'
ZE = b'SwapchainZeroExtent: begin'
AR = b'TestMinimize: armed'
for nm, body, want in (('strings: signature missing -> rc 1', ZE + b'\x00' + AR, 'fix binary strings bad'),
                       ('strings: zero-extent missing -> rc 1', SIG + b'\x00' + AR, 'fix binary strings bad'),
                       ('strings: armed missing -> rc 1', SIG + b'\x00' + ZE, 'fix binary strings bad'),
                       ('strings: all three -> passes the strings (gate file next)', SIG + b'\x00' + ZE + b'\x00' + AR, 'gate file bad')):
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    fb = os.path.join(FX, 'fake.exe')
    open(fb, 'wb').write(body)
    hb = sha(fb)
    make(fb.replace('\\', '/'), hb, '1', pred='# seal\n' + CALL)
    open(fb, 'wb').write(body)
    rc, out = run('series')
    check(nm, rc == 1 and want in out and not os.path.exists(os.path.join(FX, 'LOCK')), (rc, out))
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)
