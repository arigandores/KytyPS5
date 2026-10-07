"""Fixtures of the FS9c (HPP-673) chain tools: order_fs9c.py (item 604 (d)(3): lock, 20 s after a foreign release, the non-breakable block
f25_c1 -> f25_c2 of F25f), the dry runs of go_fs9c.sh (FS9C_DRYRUN=1: the form of each tag) and the syntax of the shell scripts.
Synthetic files only, no game, no lock.  mutlib early-exit form (`ok = True`, `ok &= ...`, last `sys.exit(0 if ok else 1)`).
The first line names the suite and the target with sha256; the output ends with ALL OK.  ASCII only.
usage: python test_tools_fs9c.py"""
import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'order_fs9c.py')
FX = os.path.join(HERE, 'fx_tools')
NL = chr(10)
BASH = 'C:/Program Files/Git/usr/bin/bash.exe' if os.path.exists('C:/Program Files/Git/usr/bin/bash.exe') else 'bash'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


_spec = importlib.util.spec_from_file_location('order_under_test', SRC)
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)
print('suite test_tools_fs9c.py sha256 %s target order_fs9c.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0]


def check(name, cond):
    N[0] += 1
    print(('ok   ' if cond else 'FAIL ') + name)
    return bool(cond)


shutil.rmtree(FX, ignore_errors=True)
os.makedirs(FX)
T0 = 1791352000   # 2026-10-07T05:46:40Z
TS = lambda dt: __import__('time').strftime('%Y-%m-%dT%H:%M:%SZ', __import__('time').gmtime(T0 + dt))  # noqa: E731


def wlog(name, lines):
    p = os.path.join(FX, name)
    with open(p, 'wb') as f:
        f.write((NL.join(lines) + NL).encode('ascii'))
    return p


F25 = wlog('f25f.log', ['lock taken f25_s01 %s' % TS(-400), 'lock released f25_s01 %s' % TS(-30)])
OTHER = wlog('other.log', ['lock taken x %s' % TS(-900), 'lock released x %s' % TS(-800)])
NOLOCK = os.path.join(FX, 'nolock')
LOCK = wlog('lock', ['someone'])


def st(logs, now, lock=NOLOCK, f25=F25):
    return M.state(logs, lock, T0 + now, f25)


ok = True
ok &= check('constants: gap 20 s, lock path, F25f log, own log', M.GAP_S == 20 and M.LOCK == 'C:/kyty/SEALED_RUN.lock'
            and M.F25F == 'C:/kyty/f287/f25f/runs/lock.log' and M.OWN == 'C:/kyty/f287/fs9c/runs/lock.log')
rc, ln = st([F25, OTHER], 0)
ok &= check('released 30 s ago -> FREE (%s)' % ln, rc == 0 and ln.startswith('ORDER FREE'))
rc, ln = st([F25, OTHER], -11)
ok &= check('released 19 s ago -> WAIT (%s)' % ln, rc == 1 and ln.startswith('ORDER WAIT'))
rc, ln = st([F25, OTHER], -10)
ok &= check('released exactly 20 s ago -> FREE (%s)' % ln, rc == 0 and ln.startswith('ORDER FREE'))
rc, ln = st([F25, OTHER], 0, lock=LOCK)
ok &= check('lock file -> LOCK rc 3 (%s)' % ln, rc == 3 and ln.startswith('ORDER LOCK'))
C1 = wlog('f25c1.log', ['lock taken f25_c1 %s' % TS(-900), 'lock released f25_c1 %s' % TS(-600)])
rc, ln = st([C1], 0, f25=C1)
ok &= check('F25f last line released f25_c1 -> BLOCK even 600 s later (%s)' % ln, rc == 1 and ln.startswith('ORDER BLOCK'))
C1R = wlog('f25c1r.log', ['lock released f25_c1_r1 %s' % TS(-600)])
rc, ln = st([C1R], 0, f25=C1R)
ok &= check('released f25_c1_r1 -> BLOCK', rc == 1 and ln.startswith('ORDER BLOCK'))
C2 = wlog('f25c2.log', ['lock released f25_c1 %s' % TS(-900), 'lock taken f25_c2 %s' % TS(-800), 'lock released f25_c2 %s' % TS(-400)])
rc, ln = st([C2], 0, f25=C2)
ok &= check('after f25_c2 released -> FREE', rc == 0 and ln.startswith('ORDER FREE'))
C10 = wlog('f25c10.log', ['lock released f25_c10 %s' % TS(-400)])
rc, ln = st([C10], 0, f25=C10)
ok &= check('f25_c10 is not f25_c1 -> FREE', rc == 0)
rc, ln = st([C1], 0, f25=F25)
ok &= check('released f25_c1 in a log that is not the F25f log -> not BLOCK', rc == 0)
rc, ln = st([F25, wlog('new.log', ['lock released y %s' % TS(-5)])], 0)
ok &= check('the newest foreign release decides (5 s ago -> WAIT)', rc == 1 and ln.startswith('ORDER WAIT') and ' y ' in ln)
rc, ln = st([wlog('taken.log', ['lock taken z %s' % TS(-5)])], 0)
ok &= check('last line taken (no release line) -> FREE when no lock file', rc == 0 and 'no foreign release' in ln)
rc, ln = st([os.path.join(FX, 'missing.log'), wlog('junk.log', ['garbage'])], 0)
ok &= check('missing and junk logs -> FREE', rc == 0)
rc, ln = st([], 0)
ok &= check('no logs -> FREE', rc == 0)
ok &= check('the own log is never read by default', all(M.norm(p) != M.norm(M.OWN) for p in M.logs_default(T0 + 0)))
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        r1 = M.main(['--logs', F25 + ',' + OTHER, '--lock', NOLOCK, '--f25f', F25, '--now', str(T0 - 11)])
        r2 = M.main(['--logs', C1, '--lock', NOLOCK, '--f25f', C1, '--now', str(T0)])
        r3 = M.main(['--logs', F25, '--lock', LOCK, '--f25f', F25, '--now', str(T0)])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
ok &= check('main rc: WAIT 1, BLOCK 1, LOCK 3', cp_ok and (r1, r2, r3) == (1, 1, 3))
ok &= check('output in strict cp1250, ASCII only', cp_ok and all(b < 128 for b in raw.getvalue()) and raw.getvalue().count(b'ORDER') == 3)
# go_fs9c.sh dry runs: the form of each tag and the refusal of other tags
env = dict(os.environ, FS9C_DRYRUN='1', PATH='/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))


def go(tag):
    r = subprocess.run([BASH, os.path.join(HERE, 'go_fs9c.sh'), tag], capture_output=True, env=env)
    return r.returncode, r.stdout.decode('ascii', 'replace').strip()


rc, o = go('fs9_v')
ok &= check('go fs9_v dry: form v, SD 300, hold 330, --rec, no layer (%s)' % o, rc == 0 and 'form v sd 300 hold 330' in o
            and '--rec' in o and 'vulkan' not in o and o.endswith('vk'))
rc, o = go('fs9_w')
ok &= check('go fs9_w dry: form w, SD 100, hold 310, validation, layer limit 100000000 (%s)' % o, rc == 0 and 'form w sd 100 hold 310' in o
            and '--emu-arg=--vulkan-validation --emu-arg=true' in o and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000' in o and '--rec' not in o)
rc, o = go('fs9_w_r2')
ok &= check('go fs9_w_r2 dry: base fs9_w', rc == 0 and 'base fs9_w form w' in o)
rc, o = go('b13_v')
ok &= check('go b13_v refused (usage, rc 2)', rc == 2)
gsrc = open(os.path.join(HERE, 'go_fs9c.sh'), 'rb').read()
ok &= check('go: no KYTY_FIX_ on the enter_scene line, FS9 sha and copy, S18 pinned, order before the lock',
            b'KYTY_FIX_' not in gsrc[gsrc.index(b'python $G/enter_scene.py $T'):gsrc.index(b'> $OUT/run.txt 2>&1')] and b'TB=3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5' in gsrc
            and b'BIN=$F/bin/kyty_emulator_3861eeea.exe' in gsrc
            and b'S18=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a' in gsrc
            and gsrc.index(b'order_fs9c.py --wait') < gsrc.index(b'set -o noclobber'))
for s in ('go_fs9c.sh', 'launch_fs9c.sh', 'wait_fs9c.sh', 'post_fs9c.sh'):
    r = subprocess.run([BASH, '-n', os.path.join(HERE, s)], capture_output=True, env=env)
    b = open(os.path.join(HERE, s), 'rb').read()
    ok &= check('%s: bash -n clean, ASCII only, LF only' % s, r.returncode == 0 and all(c < 128 for c in b) and b'\r' not in b)
psrc = open(os.path.join(HERE, 'post_fs9c.sh'), 'rb').read()
ok &= check('post: pair.txt read only in the form v, ends with exit 0, pair with b13_v sheet',
            b'if [ $FORM = v ]; then head -3 $D/glitch.txt 2>/dev/null; cat $D/pair.txt 2>/dev/null; fi' in psrc
            and psrc.rstrip().endswith(b'exit 0') and b'f24e/runs/b13_v/sheet_b13_v.png' in psrc)
lsrc = open(os.path.join(HERE, 'launch_fs9c.sh'), 'rb').read()
ok &= check('launch: order check before the queue and the detached call, exit 10',
            lsrc.index(b'order_fs9c.py') < lsrc.index(b'queue_fs9c.py') < lsrc.index(b'nohup') and b'exit 10' in lsrc)
shutil.rmtree(FX, ignore_errors=True)
print('checks %d' % N[0])
print('ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
