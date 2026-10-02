"""test_i146.py - fixtures of the warm-up reader i146_read.py and of go146i.sh (DRY and the cheap refusals) - session 146 step 0
(HPP-386).  The positive fixture is the FSc tag fs_b (V Sky Garden on dac02fb9, FS VERDICT PASS) renamed to i146_v; every member of
the letter of item 221 (g)(3) gets a failing edge.  ASCII only; the last line is ALL OK."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = 'C:/kyty/s146'
FX = HERE + '/fx_i146'
POS = FX + '/pos'
PY = sys.executable
GO = HERE + '/go146i.sh'
READ = HERE + '/i146_read.py'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_i146.py sha256 %s target i146_read.py sha256 %s go146i.sh sha256 %s' % (
    sha(os.path.abspath(__file__)), sha(READ), sha(GO)))
ok = True
n = 0


def check(name, cond):
    global ok, n
    n += 1
    ok &= bool(cond)
    print('%s %s' % ('ok  ' if cond else 'FAIL', name))


def read(root):
    p = subprocess.run([PY, READ, '--tag', 'i146_v', '--root', root], capture_output=True, text=True)
    return p.returncode, p.stdout


def variant(name, edit):
    d = FX + '/' + name
    if os.path.isdir(d):
        shutil.rmtree(d)
    shutil.copytree(POS, d)
    edit(d)
    return read(d)


rc, out = read(POS)
check('positive fs_b as i146_v: rc 0 and WARMUP VERDICT PASS', rc == 0 and 'WARMUP VERDICT i146_v: PASS' in out)
check('positive: six letter lines ok', out.count('letter p.221(g)(3) V ok') == 6)
check('positive: admission binary dac02fb9 ok', 'admit ok   binary sha256 = FSa copy dac02fb9' in out)


def glitch1(d):
    p = d + '/glitch_i146_v.txt'
    t = open(p).read().replace('one-frame glitches: 0', 'one-frame glitches: 1')
    open(p, 'w').write(t)


rc, out = variant('neg_glitch', glitch1)
check('edge: 1 glitch -> FAIL', 'WARMUP VERDICT i146_v: FAIL' in out and 'glitches' in out.split('WARMUP VERDICT')[1])


def nosheet(d):
    os.remove(d + '/sheetpair_i146_v.png')


rc, out = variant('neg_sheet', nosheet)
check('edge: no pair sheet -> FAIL', 'WARMUP VERDICT i146_v: FAIL' in out)


def wrongbin(d):
    p = d + '/i146_v.json'
    j = json.load(open(p))
    j['binary_sha256'] = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
    json.dump(j, open(p, 'w'))


rc, out = variant('neg_bin', wrongbin)
check('edge: binary 9235a7ac -> NOT ADMITTED', 'WARMUP VERDICT i146_v: NOT ADMITTED' in out)


def fixset(d):
    p = d + '/i146_v.json'
    j = json.load(open(p))
    j['env']['KYTY_PIPELINE_PRECACHE'] = '0'
    json.dump(j, open(p, 'w'))


rc, out = variant('neg_precache', fixset)
check('edge: KYTY_PIPELINE_PRECACHE=0 -> NOT ADMITTED', 'WARMUP VERDICT i146_v: NOT ADMITTED' in out)


def k2(d):
    # one FrameTrace row after the first scene frame gets dt_us 1000000 (the K2 edge) - by the reader's own parser: replace the
    # dt of the row with the largest dt (183385) by 1000000 in the log
    p = d + '/log_i146_v.txt'
    b = open(p, 'rb').read()
    i = b.find(b'183385')
    open(p, 'wb').write(b[:i] + b'1000000' + b[i + 6:])


rc, out = variant('neg_k2', k2)
check('edge: a frame dt 1000000 us after the first scene frame -> FAIL', 'WARMUP VERDICT i146_v: FAIL' in out
      and '0 frames dt >= 1 s' in out.split('WARMUP VERDICT')[1])


def nolog(d):
    os.remove(d + '/log_i146_v.txt')


rc, out = variant('neg_nolog', nolog)
check('edge: no log -> rc 1', rc == 1)
p = subprocess.run([PY, READ, '--tag', 'v146_05'], capture_output=True, text=True)
check('edge: another tag -> usage rc 2', p.returncode == 2)
# cp1250 output without PYTHONIOENCODING (item 175 (v))
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([PY, READ, '--tag', 'i146_v', '--root', POS], capture_output=True, env=env)
check('cp1250 strict output: rc 0', p.returncode == 0 and b'PASS' in p.stdout)
bad = [ln for ln in open(READ, 'rb').read().split(b'\n') if any(c > 127 for c in ln)]
check('i146_read.py is ASCII', not bad)
bad = [ln for ln in open(GO, 'rb').read().split(b'\n') if any(c > 127 for c in ln)]
check('go146i.sh is ASCII', not bad)
# go146i.sh cheap refusals
BASH = 'C:/Program Files/Git/bin/bash.exe'
p = subprocess.run([BASH, GO, 'x'], capture_output=True, text=True)
check('go146i.sh usage -> rc 2', p.returncode == 2)
if not os.path.exists('C:/kyty/SEALED_RUN.lock') and not os.path.exists('C:/kyty/s146/STOP'):
    e2 = dict(os.environ, DRY='1', PLWAIT='539')
    p = subprocess.run([BASH, GO, 'install'], capture_output=True, text=True, env=e2)
    check('go146i.sh PLWAIT not the seal line -> rc 1', p.returncode == 1)
    e2 = dict(os.environ, DRY='1', PLWAIT='541')
    p = subprocess.run([BASH, GO, 'install'], capture_output=True, text=True, env=e2)
    check('go146i.sh PLWAIT above 540 -> rc 2', p.returncode == 2)
    if os.path.isfile(HERE + '/pred/00_i146.md'):
        e2 = dict(os.environ, DRY='1', PLWAIT='540')
        p = subprocess.run([BASH, GO, 'install'], capture_output=True, text=True, env=e2)
        check('go146i.sh DRY with the seal line -> rc 0 and the plan', p.returncode == 0 and p.stdout.startswith('DRY install'))
        p = subprocess.run([PY, READ, '--check-seal', HERE + '/pred/00_i146.md'], capture_output=True, text=True)
        check('i146_read.py --check-seal of the seal -> OK', p.returncode == 0 and 'check-seal OK' in p.stdout)
else:
    print('skip: go146i.sh DRY cases (lock or stop file present)')
print('checks %d' % n)
print('ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
