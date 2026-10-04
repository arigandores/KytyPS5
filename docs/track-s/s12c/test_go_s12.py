"""Offline fixtures of go_s12.sh (track S, link S12c, HPP-496; ROADMAP "SESSION 122" item 408 (l), item 419 (v)) WITHOUT the game -
the port of s9/test_go_s9.py.  Part 1: a copy of the harness with ROOT, the lock and the stop file moved into a fixture directory runs
its cheap refusals and its DRY plans (usage, stop file, lock, PLWAIT, the seal call line, the s12 binary line, an attempt already
made, the plan of every arm: W with validation and the VK keys and no video, V / v0 with video, KYTY_S_PCW named on every arm - 1 or
0 for s12_v0 (Z3) - and never the stand KYTY_S_PCW_FORCE_MS, T on s12_gw / s12_gr, snap0 for s12_gw, the post copies of s12_gw for
s12_gr, caches as found for the others, holds and timeouts).  Part 2: a second copy runs its whole path INSIDE a fixture lock with
stubs (the game, procload, idle142, fgcpu143, powershell; sc_s12.py real for --plan, a stub for the rest; cachex_s.py real): the arm
s12_w with the caches as found (no restore, both returned after), s12_gw from snap0 with its post copies (the Z2 manifest row in
times.txt), s12_gr restored from them, the binary copy and return, the installed FS5 admitted, another installed binary refused
inside the lock, IN_ARM, the GamePatch interference, the shell's KYTY_* / VK_LAYER_* not seen by the game.  The first output line
names this suite and the harness by sha256; the output ends with ALL OK.
    python C:/kyty/s288/s12/test_go_s12.py [<go_s12.sh under test>]
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'go_s12.sh')
print('suite test_go_s12.py sha256 %s target go_s12.sh sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
BASE = Path('C:/kyty/s288/s12/fx_go_s12')
shutil.rmtree(BASE, ignore_errors=True)
(BASE / 'pred').mkdir(parents=True)
(BASE / 's12').mkdir()
FXLOCK = (BASE / 'LOCK').as_posix()
FXSTOP = (BASE / 'STOP').as_posix()
text = Path(SRC).read_text(encoding='ascii')
for a, b in (('ROOT=C:/kyty/s288\n', 'ROOT=%s\n' % BASE.as_posix()), ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s\n' % FXLOCK),
             ('STOPF=/c/kyty/s288/STOP\n', 'STOPF=%s\n' % FXSTOP)):
    assert text.count(a) == 1, a
    text = text.replace(a, b)
(BASE / 's12' / 'go_s12.sh').write_bytes(text.encode('ascii'))
SC12 = os.path.join(HERE, 'sc_s12.py').replace('\\', '/')
(BASE / 's12' / 'sc_s12.py').write_bytes(("import importlib.util, sys\n"
                                          "s = importlib.util.spec_from_file_location('sc12', %r)\nm = importlib.util.module_from_spec(s)\n"
                                          "s.loader.exec_module(m)\nsys.exit(m.main(sys.argv[1:]))\n" % SC12).encode('ascii'))
BASH = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
N = [0]
BS = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
TAGS = ('s12_w', 's12_v', 's12_gw', 's12_gr', 's12_v0')


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def go(tag, dry='1', plwait='540', base=BASE, extra=None):
    env = dict(os.environ)
    env['DRY'] = dry
    env['PLWAIT'] = plwait
    env.update(extra or {})
    env['PATH'] = '/usr/bin:/mingw64/bin:' + env.get('PATH', '')
    p = subprocess.run([BASH, (base / 's12' / 'go_s12.sh').as_posix(), tag], capture_output=True, text=True, env=env, timeout=180)
    return p.returncode, (p.stdout + p.stderr).replace('bash.exe: warning: could not find /tmp, please create!\n', '')


def seal(lines):
    (BASE / 'pred' / '08_s.md').write_text('\n'.join(lines) + '\n', encoding='ascii')


def tokens(plan):
    """the KYTY_* / VK_* pairs after --hold of a plan line"""
    return sorted(x for x in plan.split() if x.startswith(('KYTY_', 'VK_')))


ok = True
try:
    Path(SRC).read_bytes().decode('ascii')
    asc = True
except UnicodeError:
    asc = False
ok &= case('G1 go_s12.sh is ASCII only (item 175 (v))', asc)
rc, o = go('Bad-Tag')
ok &= case('G2 a tag with other characters -> rc 2 usage', rc == 2 and 'usage' in o)
rc, o = go('')
ok &= case('G2b no tag -> rc 2 usage', rc == 2 and 'usage' in o)
Path(FXSTOP).write_text('419 test\n')
rc, o = go('s12_w')
ok &= case('G3 the stop file -> rc 4 BUSY before anything', rc == 4 and 'stop file' in o)
Path(FXSTOP).unlink()
Path(FXLOCK).write_text('go_fs5c.sh fs5_i pid 1\n')
rc, o = go('s12_w')
ok &= case('G4 a foreign lock -> rc 4 BUSY (lock held) before any process', rc == 4 and 'lock held: go_fs5c.sh fs5_i' in o)
Path(FXLOCK).unlink()
rc, o = go('s12_w', plwait='x')
ok &= case('G5 PLWAIT not a number -> rc 2', rc == 2 and 'bad PLWAIT' in o)
rc, o = go('s12_w', plwait='541')
ok &= case('G6 PLWAIT above 540 -> rc 2', rc == 2)
rc, o = go('zz_9')
ok &= case('G7 an unknown tag -> rc 2', rc == 2 and 'unknown tag' in o)
seal(['x'])
rc, o = go('s12_w')
ok &= case('G8 no seal call line -> rc 1', rc == 1 and 'PLWAIT differs from the seal' in o)
seal(['go_s12 call: PLWAIT=300 bash C:/kyty/s288/s12/go_s12.sh s12_w'])
rc, o = go('s12_w')
ok &= case('G9 the call line with another PLWAIT -> rc 1', rc == 1 and 'PLWAIT differs' in o)
seal(['go_s12 call: PLWAIT=540 bash C:/kyty/s288/s12/go_s12.sh s12_w'] * 2)
rc, o = go('s12_w')
ok &= case('G10 two call lines -> rc 1', rc == 1)
seal(['go_s12 call: PLWAIT=540 bash C:/kyty/s288/s12/go_s12.sh %s' % t for t in TAGS])
rc, o = go('s12_w')
ok &= case('G11 a call line but no "s12 binary:" line -> rc 1', rc == 1 and 'no s12 binary' in o)
seal(['go_s12 call: PLWAIT=540 bash C:/kyty/s288/s12/go_s12.sh %s' % t for t in TAGS] + ['s12 binary: %s C:/x/s12.exe' % BS])
out = dict((t, go(t)) for t in TAGS)
ok &= case('G12 DRY=1 of every arm -> rc 0 with a DRY line naming the S12 copy', all(
    v[0] == 0 and v[1].startswith('DRY %s:' % k) and 'install C:/x/s12.exe (%s)' % BS in v[1] for k, v in out.items()))
dry2 = dict((t, go(t, dry='2')) for t in TAGS)
ok &= case('G13 DRY=2 of every arm -> rc 0 with a PLAN line', all(v[0] == 0 and v[1].startswith('PLAN %s:' % k) for k, v in dry2.items()))
B = BASE.as_posix()
w = out['s12_w'][1]
ok &= case('G14 s12_w: W of item 295 (b) - validation, VK_LAYER_PATH, the limit, no video, hold 310, timeout 600, caches as found',
           '--emu-arg=--vulkan-validation --emu-arg=true' in w and '--hold 310 ' in w and '--timeout 600' in w and
           '--rec' not in w and 'restore app <- -; restore glc <- -;' in w and '--level underwater_aerial_garden' in w and
           tokens(w) == ['KYTY_GPU_CLOCK_PIN=1', 'KYTY_GPU_MARKERS=0', 'KYTY_S_PCW=1', 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000',
                         'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin'])
v = out['s12_v'][1]
ok &= case('G15 s12_v: M, video, hold 330, timeout 480, stable 300, KYTY_S_PCW=1, no validation, caches as found',
           ' --rec --hold 330 ' in v and '--stable-draws 300 --timeout 480' in v and '--vulkan-validation' not in v and
           'restore app <- -; restore glc <- -;' in v and tokens(v) == ['KYTY_GPU_CLOCK_PIN=1', 'KYTY_GPU_MARKERS=0', 'KYTY_S_PCW=1'])
v0 = out['s12_v0'][1]
ok &= case('G16 s12_v0: as s12_v with KYTY_S_PCW=0 named (Z3)', ' --rec --hold 330 ' in v0 and
           tokens(v0) == ['KYTY_GPU_CLOCK_PIN=1', 'KYTY_GPU_MARKERS=0', 'KYTY_S_PCW=0'])
gw = out['s12_gw'][1]
ok &= case('G17 s12_gw: T, hero_kratos, snap0 + snap0_drv, video, hold 330, stable 100', '--level hero_kratos' in gw and
           'restore app <- C:/kyty/s288/snap0; restore glc <- C:/kyty/s288/snap0_drv;' in gw and ' --rec --hold 330 ' in gw and
           '--stable-draws 100 --timeout 480' in gw and tokens(gw) == ['KYTY_AV_TRACE=1', 'KYTY_GPU_CLOCK_PIN=1', 'KYTY_GPU_MARKERS=0',
                                                                       'KYTY_SHADER_REGISTER_TRACE=1', 'KYTY_S_PCW=1'])
gr = out['s12_gr'][1]
ok &= case('G18 s12_gr: T, the post copies of s12_gw, video, hold 120', 'restore app <- %s/s12/app_post/s12_gw; restore glc <- '
           '%s/s12/glc_post/s12_gw;' % (B, B) in gr and ' --rec --hold 120 ' in gr and tokens(gr) == tokens(gw))
ok &= case('G19 no arm names the stand, a patch file, the checkpoints, a salt or PRECACHE', all(
    'FORCE_MS' not in x[1] and 'GAME_PATCH' not in x[1] and 'CHECKPOINTS' not in x[1] and 'KYTY_PIPELINE' not in x[1]
    for x in list(out.values()) + list(dry2.values())))
ok &= case('G20 the enter_scene line: the s9 driver, the s12 root, one attempt, no install, require idle, the seal 08',
           all('%s/s9/enter_scene_s9.py %s --root %s/s12 ' % (B, t, B) in out[t][1] and '--attempts 1' in out[t][1] and
               '--no-install --require-idle' in out[t][1] and '--pred %s/pred/08_s.md' % B in out[t][1] for t in TAGS))
(BASE / 's12' / 'attempt_s12_w.txt').write_text('x')
rc, o = go('s12_w')
ok &= case('G21 an attempt already made -> rc 1, no repeat', rc == 1 and 'attempt already made' in o)
ok &= case('G22 no lock file was created by any DRY call', not Path(FXLOCK).exists())
src_t = Path(SRC).read_text(encoding='ascii')
ok &= case('G23 the shipped harness unsets every KYTY_* / VK_LAYER_* of the shell, guards s4 / s6 / s10 / s12, writes the lock line '
           '"go_s.sh <tag> " for cachex_s.py, the seal is pred/08_s.md, INST_FS4 31cbfee8 and INST_FS5 631ff987',
           "for V in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Za-z0-9_]*'); do unset $V; done\n" in src_t and
           '$ROOT/s4/RETURN_FAILED $ROOT/s6/RETURN_FAILED $ROOT/s10/RETURN_FAILED $ROOT/s10/IN_ARM $S12/RETURN_FAILED $S12/IN_ARM; do'
           in src_t and 'echo "go_s.sh $T pid $$ started' in src_t and 'PRED=pred/08_s.md\n' in src_t and
           'INST_FS4="31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5"\n' in src_t and
           'INST_FS5="631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17"\n' in src_t and src_t.count('guardfiles\n') == 2)

# ============================================================== part 2: the path INSIDE the lock, stubbed
B2 = Path('C:/kyty/s288/s12/fx_go_lock12')
shutil.rmtree(B2, ignore_errors=True)
for d in ('pred', 'bin', 'game', 'emu', 'lad/NVIDIA/GLCache', 's9', 's12'):
    (B2 / d).mkdir(parents=True)
EMU2, LAD2, GLC2 = B2 / 'emu', B2 / 'lad', B2 / 'lad' / 'NVIDIA' / 'GLCache'
LOCK2, STOP2, GAME2 = (B2 / 'LOCK').as_posix(), (B2 / 'STOP').as_posix(), B2 / 'game' / 'kyty_emulator.exe'
ENV2 = dict(CACHEX_EMU=str(EMU2), CACHEX_GLC=str(GLC2), CACHEX_LOCK=LOCK2, CACHEX_KNOWN_LAD=str(LAD2), LOCALAPPDATA=str(LAD2),
            FX_GAME=str(GAME2))
os.environ.update(ENV2)
_cs = importlib.util.spec_from_file_location('cachex_fx12', 'C:/kyty/s288/cachex_s.py')
CX = importlib.util.module_from_spec(_cs)
_cs.loader.exec_module(CX)


def put2(p, data):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def sha2(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


put2(EMU2 / '_PipelineCache' / 'PPSA21564.bin', b'snap drv')
put2(EMU2 / '_ShaderCache' / 'PPSA21564' / 'vs.bin', b'snap vs')
put2(GLC2 / 'x' / 'y.bin', b'glc snap')
SNAPA = CX.copy_set('app', str(B2 / 'snap0'))[1].split()[-1]
SNAPD = CX.copy_set('glc', str(B2 / 'snap0_drv'))[1].split()[-1]
put2(EMU2 / '_ShaderCache' / 'PPSA21564' / 'variant_x' / 'installed.bin', b'installed state')
put2(GLC2 / 'x' / 'other.bin', b'a foreign driver file')
PRE_APP, PRE_GLC = CX.app_manifest(None)[1], CX.glc_manifest(str(GLC2))[1]
PINS = B2 / 'bin' / 's12.exe'
put2(PINS, b'adb0c82f stand-in')
INSTX = hashlib.sha256(b'installed build X').hexdigest()
INSTY = hashlib.sha256(b'installed build Y').hexdigest()
put2(GAME2, b'installed build X')
put2(B2 / 'gates_default.txt', b'')
for name, body in (('procload.py', 'import sys\nsys.exit(0)\n'), ('idle142.py', 'import sys\nsys.exit(0)\n'),
                   ('fgcpu143.py', "print('fgcpu stub')\n"), ('sheet142.py', "print('sheet stub')\n")):
    put2(B2 / name, body.encode('ascii'))
put2(B2 / 'bin' / 'powershell', b'#!/bin/sh\necho 0\n')
shutil.copy2('C:/kyty/s288/cachex_s.py', B2 / 'cachex_s.py')
put2(B2 / 's12' / 'sc_s12.py', ("import importlib.util, sys, os\na = sys.argv[1:]\n"
                                "if a[:1] == ['--plan']:\n"
                                "    s = importlib.util.spec_from_file_location('sc12', %r)\n    m = importlib.util.module_from_spec(s)\n"
                                "    s.loader.exec_module(m)\n    sys.exit(m.main(a))\n"
                                "if '--check-seal' in a:\n    print('SEAL: PASS (fixture stub)')\n    sys.exit(0)\n"
                                "if a[:1] == ['--allowed']:\n    print('ALLOWED %%s: yes (fixture stub)' %% a[1])\n    sys.exit(0)\n"
                                "print('ARM stub')\nsys.exit(0)\n" % SC12).encode('ascii'))
put2(B2 / 's9' / 'enter_scene_s9.py', (
    "import hashlib, json, os, sys\ntag = sys.argv[1]\nroot = sys.argv[sys.argv.index('--root') + 1]\n"
    "emu, glc = os.environ['CACHEX_EMU'], os.environ['CACHEX_GLC']\n"
    "seen = sorted(os.path.relpath(os.path.join(d, f), emu).replace(os.sep, '/') for d, _, fs in os.walk(emu) for f in fs)\n"
    "open(os.path.join(root, 'log_%s.txt' % tag), 'w').write('log of the stub')\n"
    "ia = open(os.path.join(root, 'IN_ARM')).read() if os.path.exists(os.path.join(root, 'IN_ARM')) else None\n"
    "json.dump({'tag': tag, 'argv': sys.argv[1:], 'shell': sorted(k for k in os.environ if k.startswith(('KYTY_', 'VK_LAYER_'))), "
    "'seen': seen, 'in_arm': ia, "
    "'game': hashlib.sha256(open(os.environ['FX_GAME'], 'rb').read()).hexdigest(), "
    "'glc': sorted(os.listdir(os.path.join(glc, 'x')))}, open(os.path.join(root, '%s.json' % tag), 'w'))\n"
    "os.makedirs(os.path.join(emu, '_PipelineCache'), exist_ok=True)\n"
    "open(os.path.join(emu, '_PipelineCache', 'PPSA21564.bin'), 'wb').write(b'the game wrote the driver cache ' + tag.encode())\n"
    "if os.environ.get('FX_MODE') == 'tmp':\n"
    "    open(os.path.join(emu, '_PipelineCache', 'PPSA21564.bin.tmp'), 'wb').write(b'tmp')\n"
    "open(os.path.join(glc, 'x', 'game.bin'), 'wb').write(b'the game wrote GLCache')\n"
    "if os.environ.get('FX_MODE') == 'gamepatch':\n"
    "    open(os.path.join(root, 'log_%s.txt' % tag), 'wb').write(b'x\\nGamePatch: applied 4 pokes\\n')\n"
    "print('VERDICT: stub')\n").encode('ascii'))
text2 = Path(SRC).read_text(encoding='ascii')
for a, b in (('ROOT=C:/kyty/s288\n', 'ROOT=%s\n' % B2.as_posix()), ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s\n' % LOCK2),
             ('STOPF=/c/kyty/s288/STOP\n', 'STOPF=%s\n' % STOP2),
             ('GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"\n', 'GAME="%s"\n' % GAME2.as_posix()),
             ('SNAP_APP="d8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4"\n', 'SNAP_APP="%s"\n' % SNAPA),
             ('SNAP_DRV="1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028"\n', 'SNAP_DRV="%s"\n' % SNAPD),
             ('SNAPDIR="C:/kyty/s288/snap0"\n', 'SNAPDIR="%s"\n' % (B2 / 'snap0').as_posix()),
             ('SNAPDRVDIR="C:/kyty/s288/snap0_drv"\n', 'SNAPDRVDIR="%s"\n' % (B2 / 'snap0_drv').as_posix()),
             ('RSLEEP=5\n', 'RSLEEP=0\n'),
             ('INST_FS4="31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5"\n', 'INST_FS4="%s"\n' % INSTX),
             ('INST_FS5="631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17"\n', 'INST_FS5="%s"\n' % INSTY)):
    assert text2.count(a) == 1, a
    text2 = text2.replace(a, b)
(B2 / 's12' / 'go_s12.sh').write_bytes(text2.encode('ascii'))
(B2 / 'pred' / '08_s.md').write_bytes((''.join('go_s12 call: PLWAIT=540 bash C:/kyty/s288/s12/go_s12.sh %s\n' % t for t in TAGS) +
                                       's12 binary: %s %s\n' % (sha2(PINS), PINS.as_posix())).encode('ascii'))
BINP = '/' + B2.as_posix()[0].lower() + B2.as_posix()[2:] + '/bin'


def go2(tag, mode='', **env_over):
    env = dict(os.environ)
    env.update(ENV2)
    env.update(DRY='0', PLWAIT='540', FX_MODE=mode, PATH=BINP + ':/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    env.update(env_over)
    p = subprocess.run([BASH, (B2 / 's12' / 'go_s12.sh').as_posix(), tag], capture_output=True, text=True, env=env, timeout=300)
    return p.returncode, (p.stdout + p.stderr).replace('bash.exe: warning: could not find /tmp, please create!\n', '')


def cj2(tag):
    p = B2 / 's12' / 'runs_s' / ('%s.cache.json' % tag)
    return json.loads(p.read_text()) if p.exists() else {}


def js2(tag):
    p = B2 / 's12' / ('%s.json' % tag)
    return json.loads(p.read_text()) if p.exists() else {}


def lockrows():
    p = B2 / 's12' / 'runs_s' / 'lock.log'
    return p.read_text().splitlines() if p.exists() else []


def times():
    p = B2 / 's12' / 'times.txt'
    return p.read_text() if p.exists() else ''


rc, o = go2('s12_w', KYTY_GAME_PATCH='C:/x/p.txt', KYTY_S_PCW_FORCE_MS='15000', VK_LAYER_MESSAGE_ID_FILTER='x')
c = cj2('s12_w')
j = js2('s12_w')
ok &= case('GL1 s12_w inside the lock: the S12 stand-in installed for the game and the installed build back after it',
           rc == 0 and GAME2.read_bytes() == b'installed build X' and c.get('installed_before', {}).get('sha') == INSTX
           and c.get('installed_after', {}).get('sha') == INSTX and j.get('game') == sha2(PINS))
ok &= case('GL2 s12_w caches as found: the game saw the installed variant file and GLCache as found, no restore rows, '
           'man_launch_glc = man_pre_glc, both back after', '_ShaderCache/PPSA21564/variant_x/installed.bin' in j.get('seen', [])
           and 'other.bin' in j.get('glc', []) and 'restore_app' not in c and 'restore_glc' not in c and
           c.get('man_launch_glc', {}).get('sha') == c.get('man_pre_glc', {}).get('sha') and
           CX.app_manifest(None)[1] == PRE_APP and CX.glc_manifest(str(GLC2))[1] == PRE_GLC and
           c.get('return_app', {}).get('got') == c.get('return_app', {}).get('expected'))
ok &= case('GL3 the shell KYTY_GAME_PATCH / KYTY_S_PCW_FORCE_MS / VK_LAYER_MESSAGE_ID_FILTER not seen by the game; the validation '
           'arguments passed', not [k for k in j.get('shell', []) if k in ('KYTY_GAME_PATCH', 'KYTY_S_PCW_FORCE_MS',
                                                                           'VK_LAYER_MESSAGE_ID_FILTER')]
           and '--emu-arg=--vulkan-validation' in j.get('argv', []) and 'KYTY_S_PCW=1' in j.get('argv', []))
rc, o = go2('s12_gw')
c = cj2('s12_gw')
j = js2('s12_gw')
ok &= case('GL4 s12_gw: the game saw snap0 (not the installed variant file), restore rows snap0 / snap0_drv, everything back after',
           rc == 0 and j.get('seen') == ['_PipelineCache/PPSA21564.bin', '_ShaderCache/PPSA21564/vs.bin'] and
           c.get('restore_app', {}).get('got') == SNAPA and c.get('restore_glc', {}).get('got') == SNAPD and
           CX.app_manifest(None)[1] == PRE_APP and CX.glc_manifest(str(GLC2))[1] == PRE_GLC)
man = (B2 / 's12' / 'app_post' / 's12_gw' / 'MANIFEST.txt').read_text()
ok &= case('GL5 s12_gw post copies hold what the game left; the Z2 row in times.txt names PPSA21564.bin',
           (B2 / 's12' / 'app_post' / 's12_gw' / 'PipelineCache' / 'PPSA21564.bin').read_bytes() ==
           b'the game wrote the driver cache s12_gw' and (B2 / 's12' / 'glc_post' / 's12_gw' / 'x' / 'game.bin').exists() and
           c.get('app_post_copy', {}).get('sha') and c.get('glc_post_copy', {}).get('sha') and
           'PipelineCache/PPSA21564.bin ' in man and 'Z2 manifest after s12_gw: PipelineCache/PPSA21564.bin ' in times())
rc, o = go2('s12_gr')
c = cj2('s12_gr')
j = js2('s12_gr')
ok &= case('GL6 s12_gr: the game saw the driver cache s12_gw left and its GLCache; restore = the post copies; everything back after',
           rc == 0 and 'game.bin' in j.get('glc', []) and
           c.get('restore_app', {}).get('got') == cj2('s12_gw').get('app_post_copy', {}).get('sha') and
           c.get('restore_glc', {}).get('got') == cj2('s12_gw').get('glc_post_copy', {}).get('sha') and
           CX.app_manifest(None)[1] == PRE_APP and CX.glc_manifest(str(GLC2))[1] == PRE_GLC)
ok &= case('GL7 s12_v0 is not run by the gw / gr copies: s12_gr app_post not made (only s12_gw has post copies)',
           not (B2 / 's12' / 'app_post' / 's12_gr').exists())
lr = lockrows()
ok &= case('GL8 three arms - three taken / released pairs in lock.log, no lock file, no guard', len(lr) == 6 and
           lr[0].startswith('lock taken s12_w ') and lr[-1].startswith('lock released s12_gr ') and not Path(LOCK2).exists()
           and not (B2 / 's12' / 'RETURN_FAILED').exists() and not (B2 / 's12' / 'IN_ARM').exists())
ia1 = js2('s12_w').get('in_arm') or ''
ok &= case('GL9 IN_ARM: the game saw it (the tag, the installed sha) and the successful return removed it',
           ia1.startswith('IN_ARM s12_w ') and ('installed: %s (copy' % INSTX) in ia1 and 'removed after the successful return'
           in times())
put2(GAME2, b'installed build Y')
rc, o = go2('s12_v')
c = cj2('s12_v')
ok &= case('GL10 the installed FS5 stand-in (INST_FS5) admitted: the arm runs, installed_before = Y, Y back after',
           rc == 0 and c.get('installed_before', {}).get('sha') == INSTY and GAME2.read_bytes() == b'installed build Y')
put2(GAME2, b'another installed build')
n_lock = len(lockrows())
rc, o = go2('s12_v0')
ok &= case('GL11 an installed binary other than FS4 / FS5 -> rc 1 inside the lock: nothing installed, no IN_ARM, no attempt, the '
           'lock taken and released, the row in times.txt', rc == 1 and 'installed binary not FS4 / FS5' in o and
           GAME2.read_bytes() == b'another installed build' and not (B2 / 's12' / 'IN_ARM').exists() and
           not (B2 / 's12' / 'attempt_s12_v0.txt').exists() and len(lockrows()) == n_lock + 2 and not Path(LOCK2).exists() and
           'not in {FS4, FS5} - no arm' in times())
put2(GAME2, b'installed build X')
(B2 / 's12' / 'IN_ARM').write_text('IN_ARM s12_v0 2026-10-04T00:00:00Z pid 1 - a hard kill left it\n')
n_lock = len(lockrows())
rc, o = go2('s12_v0')
ok &= case('GL12 a hanging IN_ARM -> rc 1 "return failed guard" before the lock: no lock row, no attempt, the guard kept',
           rc == 1 and 'return failed guard' in o and len(lockrows()) == n_lock and
           not (B2 / 's12' / 'attempt_s12_v0.txt').exists() and (B2 / 's12' / 'IN_ARM').exists())
(B2 / 's12' / 'IN_ARM').unlink()
rc, o = go2('s12_v0', mode='gamepatch')
ok &= case('GL13 a GamePatch: log line -> rc 7, the caches and the binary returned', rc == 7 and
           'GAMEPATCH interference: 1 lines' in o and 'lines beginning GamePatch: in log_s12_v0.txt: 1' in times() and
           CX.app_manifest(None)[1] == PRE_APP and GAME2.read_bytes() == b'installed build X' and not Path(LOCK2).exists())
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
