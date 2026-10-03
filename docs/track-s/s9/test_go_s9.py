"""Offline fixtures of go_s9.sh (track S, link S9, HPP-431; ROADMAP "SESSION 122" item 355 (k)) WITHOUT the game - the port of
C:/kyty/s288/test_go_s.py.  Part 1: a copy of the harness with ROOT, the lock and the stop file moved into a fixture directory
runs its cheap refusals and its DRY plans (usage, stop file, lock, PLWAIT, the seal call line, the binary lines, an attempt
already made, the plan of every arm kind: environment M / T, the knob and the stand on pi arms, the integrity sources of pi_r1 /
pi_r0, the salt and PRECACHE=0 of c5_0, the T2 form C5 / APP, KYTY_CS_PRETRANSLATE=0 of t2_cs0, the form U of u arms, video on
every arm, holds and timeouts; a T2 tag before C5 -> rc 6).  Part 2: a second copy runs its whole path INSIDE a fixture lock
with stubs (the game, procload, idle142, fgcpu143, powershell; sc_s9.py real for --plan, a stub for the rest; cachex_s.py real):
the full return of pi_w1 and its post copies, the integrity restore of pi_r1 from them, the form U of u_1 (the app caches empty
for the game, GLCache untouched before, both returned after, the catalogue checked), the binary copy and return, the lock rows,
the GamePatch interference.  S9b (item 371 (g), RC1 of S9r): the guard s10/IN_ARM written before the install (the game sees
it with the tag, the installed sha and the pre manifests) and removed by the successful return; a hanging IN_ARM (a hard kill)
refuses the next arm rc 1 before the lock; an installed binary other than INST_WANT -> rc 1 inside the lock, nothing installed,
no IN_ARM, no attempt.  S9b rework 1 (item 377 (b)(2)): INST_WANT = 540c035a (item 374 (g)) apart from the u binary - the
fixture installed build differs from the pinned u stand-in; an arm with the installed = INST_WANT runs (the game sees the s / u
binary, the installed build back after); the installed = the u stand-in (the 4aa62e95 of item 342) -> rc 1 inside the lock,
nothing installed.  The first output line names this suite and the harness by sha256; the output ends with ALL OK.
    python C:/kyty/s288/s9/test_go_s9.py
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'go_s9.sh')
print('suite test_go_s9.py sha256 %s target go_s9.sh sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
BASE = Path('C:/kyty/s288/s9/fx_go_s9')
shutil.rmtree(BASE, ignore_errors=True)
(BASE / 'pred').mkdir(parents=True)
(BASE / 's9').mkdir()
FXLOCK = (BASE / 'LOCK').as_posix()
FXSTOP = (BASE / 'STOP').as_posix()
text = Path(SRC).read_text(encoding='ascii')
for a, b in (('ROOT=C:/kyty/s288\n', 'ROOT=%s\n' % BASE.as_posix()), ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s\n' % FXLOCK),
             ('STOPF=/c/kyty/s288/STOP\n', 'STOPF=%s\n' % FXSTOP)):
    assert text.count(a) == 1, a
    text = text.replace(a, b)
(BASE / 's9' / 'go_s9.sh').write_bytes(text.encode('ascii'))
SC9 = os.path.join(HERE, 'sc_s9.py').replace('\\', '/')
# the real scorer for --plan, with its link directory (the C5 reading) moved into the fixture
(BASE / 's9' / 'sc_s9.py').write_bytes(("import importlib.util, sys\n"
                                        "s = importlib.util.spec_from_file_location('sc9', %r)\nm = importlib.util.module_from_spec(s)\n"
                                        "s.loader.exec_module(m)\nsys.exit(m.main(sys.argv[1:], %r, %r))\n" % (
                                            SC9, (BASE / 's10').as_posix(), (BASE / 'pred' / '06b_s.md').as_posix())
                                        ).encode('ascii'))
BASH = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
N = [0]
BS = 'f3b3aa3bef3f0ceadf668d0fc8bd68230ab1e3158d87bbc0b4c66b92a6651ca3'
BU = '4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac'


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def go(tag, dry='1', plwait='540', form=None, base=BASE):
    env = dict(os.environ)
    env['DRY'] = dry
    env['PLWAIT'] = plwait
    if form:
        env['FORM'] = form
    env['PATH'] = '/usr/bin:/mingw64/bin:' + env.get('PATH', '')
    p = subprocess.run([BASH, (base / 's9' / 'go_s9.sh').as_posix(), tag], capture_output=True, text=True, env=env, timeout=180)
    return p.returncode, (p.stdout + p.stderr).replace('bash.exe: warning: could not find /tmp, please create!\n', '')


def seal(lines):
    (BASE / 'pred' / '06b_s.md').write_text('\n'.join(lines) + '\n', encoding='ascii')


ok = True
try:
    Path(SRC).read_bytes().decode('ascii')
    asc = True
except UnicodeError:
    asc = False
ok &= case('G1 go_s9.sh is ASCII only (item 175 (v))', asc)
rc, o = go('Bad-Tag')
ok &= case('G2 a tag with other characters -> rc 2 usage', rc == 2 and 'usage' in o)
Path(FXSTOP).write_text('355 test\n')
rc, o = go('pi_w1')
ok &= case('G3 the stop file -> rc 4 BUSY before anything', rc == 4 and 'stop file' in o)
Path(FXSTOP).unlink()
Path(FXLOCK).write_text('gop31.sh hx_sha pid 1\n')
rc, o = go('pi_w1')
ok &= case('G4 a foreign lock -> rc 4 BUSY (lock held) before any process', rc == 4 and 'lock held: gop31.sh hx_sha' in o)
Path(FXLOCK).unlink()
rc, o = go('pi_w1', plwait='x')
ok &= case('G5 PLWAIT not a number -> rc 2', rc == 2 and 'bad PLWAIT' in o)
rc, o = go('pi_w1', plwait='541')
ok &= case('G6 PLWAIT above 540 -> rc 2', rc == 2)
rc, o = go('zz_9')
ok &= case('G7 an unknown tag -> rc 2', rc == 2 and 'unknown tag' in o)
rc, o = go('t2_1')
ok &= case('G8 a T2 tag before c5_0 (no C5 reading) -> rc 6 before any seal check', rc == 6 and 'undetermined' in o)
seal(['x'])
rc, o = go('pi_w1')
ok &= case('G9 no seal call line -> rc 1', rc == 1 and 'PLWAIT differs from the seal' in o)
seal(['go_s9 call: PLWAIT=300 bash C:/kyty/s288/s9/go_s9.sh pi_w1'])
rc, o = go('pi_w1')
ok &= case('G10 the call line with another PLWAIT -> rc 1', rc == 1 and 'PLWAIT differs' in o)
seal(['go_s9 call: PLWAIT=540 bash C:/kyty/s288/s9/go_s9.sh pi_w1'] * 2)
rc, o = go('pi_w1')
ok &= case('G11 two call lines -> rc 1', rc == 1)
tags = ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0', 'c5_0', 'u_1', 'u_5')
seal(['go_s9 call: PLWAIT=540 bash C:/kyty/s288/s9/go_s9.sh %s' % t for t in tags])
rc, o = go('pi_w1')
ok &= case('G12 a call line but no "s binary:" line -> rc 1', rc == 1 and 'no s binary' in o)
seal(['go_s9 call: PLWAIT=540 bash C:/kyty/s288/s9/go_s9.sh %s' % t for t in tags] +
     ['s binary: %s C:/x/s.exe' % BS, 'u binary: %s C:/x/u.exe' % BU])
out = dict((t, go(t)) for t in tags)
ok &= case('G13 DRY=1 of every arm kind -> rc 0 with a DRY line', all(v[0] == 0 and v[1].startswith('DRY %s:' % k)
                                                                      for k, v in out.items()))
m = out['pi_w1'][1]
ok &= case('G14 pi_w1: binary s, snap0 + snap0_drv, M (no trace), the knob 1 + the stand, hold 330, stable 300, video',
           'install C:/x/s.exe (%s)' % BS in m and 'restore app <- C:/kyty/s288/snap0;' in m and
           'restore glc <- C:/kyty/s288/snap0_drv;' in m and 'KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=15000' in m and
           'KYTY_AV_TRACE' not in m and '--hold 330 ' in m and '--stable-draws 300 --timeout 480' in m and ' --rec ' in m and
           'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in m and '--root %s/s10' % BASE.as_posix() in m and
           '%s/s9/enter_scene_s9.py pi_w1' % BASE.as_posix() in m and '--level underwater_aerial_garden' in m)
r1 = out['pi_r1'][1]
ok &= case('G15 pi_r1: T, the app and GLCache from the post copies of pi_w1, hold 120; pi_r0 from pi_w0 with the knob 0',
           'restore app <- %s/s10/app_post/pi_w1;' % BASE.as_posix() in r1 and 'restore glc <- %s/s10/glc_post/pi_w1;' %
           BASE.as_posix() in r1 and 'KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1' in r1 and '--hold 120 ' in r1 and
           'restore app <- %s/s10/app_post/pi_w0;' % BASE.as_posix() in out['pi_r0'][1] and
           'KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=15000' in out['pi_r0'][1])
c5 = out['c5_0'][1]
ok &= case('G16 c5_0: T, shuriken_ninja_castle, KYTY_PIPELINE_SALT=c5_0 KYTY_PIPELINE_PRECACHE=0, snap0 + snap0_drv, stable 100',
           '--level shuriken_ninja_castle' in c5 and 'KYTY_PIPELINE_SALT=c5_0 KYTY_PIPELINE_PRECACHE=0' in c5 and
           'restore glc <- C:/kyty/s288/snap0_drv;' in c5 and '--stable-draws 100 --timeout 480' in c5 and 'KYTY_S_PCW' not in c5)
u1 = out['u_1'][1]
ok &= case('G17 u_1: binary u, the app caches from the empty set, no GLCache restore, the seed path and prepare-cold, '
           'timeout 600; u_5 on fragile_battle_1', 'install C:/x/u.exe (%s)' % BU in u1 and
           'restore app <- %s/s10/empty_app;' % BASE.as_posix() in u1 and 'restore glc <- -;' in u1 and
           'KYTY_SHADER_SEED_PATH=C:/kyty/s288/s9/seeds KYTY_CACHE_MODE=prepare-cold' in u1 and '--timeout 600' in u1 and
           'KYTY_PIPELINE' not in u1 and '--level fragile_battle_1' in out['u_5'][1])
rc, o = go('t2_cs0', dry='2', form='c5')
rc2, o2 = go('t2_cs0', dry='2', form='app')
ok &= case('G18 DRY=2 FORM=c5 / app of t2_cs0: the salt of its tag + PRECACHE=0 or neither, + KYTY_CS_PRETRANSLATE=0, hero_kratos',
           rc == 0 and 'KYTY_PIPELINE_SALT=t2_cs0 KYTY_PIPELINE_PRECACHE=0 KYTY_CS_PRETRANSLATE=0' in o and 'form c5' in o and
           rc2 == 0 and 'KYTY_PIPELINE' not in o2 and 'KYTY_CS_PRETRANSLATE=0' in o2 and '--level hero_kratos' in o2)
ok &= case('G19 no arm runs validation; no arm names KYTY_GAME_PATCH', all('--vulkan-validation' not in v[1] and 'GAME_PATCH'
                                                                           not in v[1] for v in out.values()))
(BASE / 's10').mkdir(exist_ok=True)
Path(BASE / 's10' / 'attempt_pi_w1.txt').write_text('x')
rc, o = go('pi_w1')
ok &= case('G20 an attempt already made -> rc 1, no repeat', rc == 1 and 'attempt already made' in o)
ok &= case('G21 no lock file was created by any DRY call', not Path(FXLOCK).exists())
src_t = Path(SRC).read_text(encoding='ascii')
ok &= case('G22 the shipped harness unsets KYTY_GAME_PATCH, guards s4 / s6 / s10, writes the lock line "go_s.sh <tag> " for '
           'cachex_s.py', 'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA VK_LAYER_MESSAGE_ID_FILTER KYTY_GAME_PATCH\n' in src_t
           and '$ROOT/s4/RETURN_FAILED $ROOT/s6/RETURN_FAILED $ROOT/s10/RETURN_FAILED' in src_t and
           'echo "go_s.sh $T pid $$ started' in src_t)
ok &= case('G23 item 371 (g), item 377 (b): the shipped harness guards s10/IN_ARM with the RETURN_FAILED guards and pins '
           'INST_WANT = 540c035a (item 374 (g)), not 4aa62e95; the seal is pred/06b_s.md',
           '$ROOT/s10/RETURN_FAILED $ROOT/s10/IN_ARM; do' in src_t and
           'INST_WANT="540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1"\n' in src_t and 'INST_WANT="4aa62e95' not in src_t and
           'PRED=pred/06b_s.md\n' in src_t and src_t.count('guardfiles\n') == 2)

# ============================================================== part 2: the path INSIDE the lock, stubbed
B2 = Path('C:/kyty/s288/s9/fx_go_lock9')
shutil.rmtree(B2, ignore_errors=True)
for d in ('pred', 'bin', 'game', 'emu', 'lad/NVIDIA/GLCache', 's9', 's9/seeds'):
    (B2 / d).mkdir(parents=True)
EMU2, LAD2, GLC2 = B2 / 'emu', B2 / 'lad', B2 / 'lad' / 'NVIDIA' / 'GLCache'
LOCK2, STOP2, GAME2 = (B2 / 'LOCK').as_posix(), (B2 / 'STOP').as_posix(), B2 / 'game' / 'kyty_emulator.exe'
ENV2 = dict(CACHEX_EMU=str(EMU2), CACHEX_GLC=str(GLC2), CACHEX_LOCK=LOCK2, CACHEX_KNOWN_LAD=str(LAD2), LOCALAPPDATA=str(LAD2),
            FX_GAME=str(GAME2))
os.environ.update(ENV2)
_cs = importlib.util.spec_from_file_location('cachex_fx9', 'C:/kyty/s288/cachex_s.py')
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
PINS, PINU = B2 / 'bin' / 's.exe', B2 / 'bin' / 'u.exe'
put2(PINS, b'f3b3aa3b stand-in')
put2(PINU, b'4aa62e95 stand-in')
INSTX = hashlib.sha256(b'installed build X').hexdigest()
put2(GAME2, b'installed build X')
put2(B2 / 'gates_default.txt', b'')
for name, body in (('procload.py', 'import sys\nsys.exit(0)\n'), ('idle142.py', 'import sys\nsys.exit(0)\n'),
                   ('fgcpu143.py', "print('fgcpu stub')\n"), ('sheet142.py', "print('sheet stub')\n")):
    put2(B2 / name, body.encode('ascii'))
put2(B2 / 'bin' / 'powershell', b'#!/bin/sh\necho 0\n')
shutil.copy2('C:/kyty/s288/cachex_s.py', B2 / 'cachex_s.py')
put2(B2 / 's9' / 'sc_s9.py', ("import importlib.util, sys, os\na = sys.argv[1:]\n"
                              "if a[:1] == ['--plan']:\n"
                              "    s = importlib.util.spec_from_file_location('sc9', %r)\n    m = importlib.util.module_from_spec(s)\n"
                              "    s.loader.exec_module(m)\n    sys.exit(m.main(a))\n"
                              "if '--check-seal' in a:\n    print('SEAL: PASS (fixture stub)')\n    sys.exit(0)\n"
                              "if a[:1] == ['--allowed']:\n    print('ALLOWED %%s: yes (fixture stub)' %% a[1])\n    sys.exit(0)\n"
                              "if '--seeds-check' in a:\n    x = os.environ.get('FX_SEEDS', 'ab' * 32)\n"
                              "    print('seeds sha %%s files 3 (sealed x) %%s' %% (x, 'MATCH' if x == 'ab' * 32 else 'DIFF'))\n"
                              "    sys.exit(0 if x == 'ab' * 32 else 1)\n"
                              "print('ARM stub')\nsys.exit(0)\n" % SC9).encode('ascii'))
put2(B2 / 's9' / 'enter_scene_s9.py', (
    "import hashlib, json, os, sys\ntag = sys.argv[1]\nroot = sys.argv[sys.argv.index('--root') + 1]\n"
    "emu, glc = os.environ['CACHEX_EMU'], os.environ['CACHEX_GLC']\n"
    "seen = sorted(os.path.relpath(os.path.join(d, f), emu).replace(os.sep, '/') for d, _, fs in os.walk(emu) for f in fs)\n"
    "open(os.path.join(root, 'log_%s.txt' % tag), 'w').write('log of the stub')\n"
    "ia = open(os.path.join(root, 'IN_ARM')).read() if os.path.exists(os.path.join(root, 'IN_ARM')) else None\n"
    "json.dump({'tag': tag, 'gp': os.environ.get('KYTY_GAME_PATCH'), 'seen': seen, 'in_arm': ia, "
    "'game': hashlib.sha256(open(os.environ['FX_GAME'], 'rb').read()).hexdigest(), "
    "'glc': sorted(os.listdir(os.path.join(glc, 'x')))}, open(os.path.join(root, '%s.json' % tag), 'w'))\n"
    "os.makedirs(os.path.join(emu, '_PipelineCache'), exist_ok=True)\n"
    "open(os.path.join(emu, '_PipelineCache', 'PPSA21564.bin'), 'wb').write(b'the game wrote the driver cache')\n"
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
             ('INST_WANT="540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1"\n', 'INST_WANT="%s"\n' % INSTX)):
    assert text2.count(a) == 1, a
    text2 = text2.replace(a, b)
(B2 / 's9' / 'go_s9.sh').write_bytes(text2.encode('ascii'))
TAGS2 = ('pi_w1', 'pi_r1', 'u_1', 'c5_0', 'pi_w0')
(B2 / 'pred' / '06b_s.md').write_bytes((''.join('go_s9 call: PLWAIT=540 bash C:/kyty/s288/s9/go_s9.sh %s\n' % t for t in TAGS2) +
                                       's binary: %s %s\nu binary: %s %s\n' % (sha2(PINS), PINS.as_posix(), sha2(PINU),
                                                                               PINU.as_posix())).encode('ascii'))
BINP = '/' + B2.as_posix()[0].lower() + B2.as_posix()[2:] + '/bin'


def go2(tag, mode='', **env_over):
    env = dict(os.environ)
    env.update(ENV2)
    env.update(DRY='0', PLWAIT='540', FX_MODE=mode, PATH=BINP + ':/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    env.update(env_over)
    p = subprocess.run([BASH, (B2 / 's9' / 'go_s9.sh').as_posix(), tag], capture_output=True, text=True, env=env, timeout=300)
    return p.returncode, (p.stdout + p.stderr).replace('bash.exe: warning: could not find /tmp, please create!\n', '')


def cj2(tag):
    p = B2 / 's10' / 'runs_s' / ('%s.cache.json' % tag)
    return json.loads(p.read_text()) if p.exists() else {}


def js2(tag):
    p = B2 / 's10' / ('%s.json' % tag)
    return json.loads(p.read_text()) if p.exists() else {}


def lockrows():
    p = B2 / 's10' / 'runs_s' / 'lock.log'
    return p.read_text().splitlines() if p.exists() else []


rc, o = go2('pi_w1')
c = cj2('pi_w1')
j = js2('pi_w1')
ok &= case('GL1 pi_w1 inside the lock: the binary s installed for the game and the installed build back after it',
           rc == 0 and GAME2.read_bytes() == b'installed build X' and c.get('installed_before', {}).get('sha') == INSTX
           and c.get('installed_after', {}).get('sha') == INSTX and j.get('game') == sha2(PINS))
ok &= case('GL2 pi_w1: the game saw snap0 (not the installed variant file), restore rows snap0 / snap0_drv, the caches and '
           'GLCache back to the state before the arm', j.get('seen') == ['_PipelineCache/PPSA21564.bin',
                                                                       '_ShaderCache/PPSA21564/vs.bin'] and
           c.get('restore_app', {}).get('got') == SNAPA and c.get('restore_glc', {}).get('got') == SNAPD and
           CX.app_manifest(None)[1] == PRE_APP and CX.glc_manifest(str(GLC2))[1] == PRE_GLC)
ok &= case('GL3 pi_w1: the post copies app_post/pi_w1 and glc_post/pi_w1 hold what the game left (its driver cache file)',
           (B2 / 's10' / 'app_post' / 'pi_w1' / 'PipelineCache' / 'PPSA21564.bin').read_bytes() == b'the game wrote the driver cache'
           and (B2 / 's10' / 'glc_post' / 'pi_w1' / 'x' / 'game.bin').exists() and
           c.get('app_post_copy', {}).get('sha') and c.get('glc_post_copy', {}).get('sha'))
rc, o = go2('pi_r1')
c = cj2('pi_r1')
j = js2('pi_r1')
ok &= case('GL4 pi_r1: the game saw the app caches pi_w1 left (no snapshot) and GLCache of pi_w1; restore = the post copies; '
           'everything back after', rc == 0 and 'game.bin' in j.get('glc', []) and
           c.get('restore_app', {}).get('got') == cj2('pi_w1').get('app_post_copy', {}).get('sha') and
           c.get('restore_glc', {}).get('got') == cj2('pi_w1').get('glc_post_copy', {}).get('sha') and
           CX.app_manifest(None)[1] == PRE_APP and CX.glc_manifest(str(GLC2))[1] == PRE_GLC)
rc, o = go2('u_1')
c = cj2('u_1')
j = js2('u_1')
ok &= case('GL5 u_1 form U: the game saw NO app cache file, GLCache as found (no restore before), the catalogue sha noted; the '
           'installed caches and GLCache back after', rc == 0 and j.get('seen') == [] and 'other.bin' in j.get('glc', []) and
           c.get('restore_app', {}).get('got') == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' and
           'restore_glc' not in c and c.get('seeds', {}).get('sha') == 'ab' * 32 and c.get('man_launch_glc', {}).get('sha') ==
           c.get('man_pre_glc', {}).get('sha') and CX.app_manifest(None)[1] == PRE_APP and
           CX.glc_manifest(str(GLC2))[1] == PRE_GLC)
ok &= case('GL5b item 377 (b)(1): INST_WANT (the installed) is not the u binary - the game of u_1 ran the pinned u stand-in, '
           'installed_before = the installed build, the installed build back after', j.get('game') == sha2(PINU) and
           sha2(PINU) != INSTX and c.get('installed_before', {}).get('sha') == INSTX and
           c.get('installed_after', {}).get('sha') == INSTX and GAME2.read_bytes() == b'installed build X')
lr = lockrows()
ok &= case('GL6 three arms - three taken / released pairs in lock.log, no lock file, no guard', len(lr) == 6 and
           lr[0].startswith('lock taken pi_w1 ') and lr[-1].startswith('lock released u_1 ') and not Path(LOCK2).exists()
           and not (B2 / 's10' / 'RETURN_FAILED').exists())
rc, o = go2('c5_0', FX_SEEDS='cd' * 32)
ok &= case('GL7 the catalogue check runs only for u arms (c5_0 with a bad catalogue sha still runs)', rc == 0 and
           js2('c5_0').get('tag') == 'c5_0')
shutil.rmtree(B2 / 's10' / 'attempt_u_1.txt', ignore_errors=True)
for f in ('attempt_u_1.txt', 'u_1.json'):
    p = B2 / 's10' / f
    if p.exists():
        os.replace(str(p), str(B2 / 's10' / ('old_' + f)))
n_lock = len(lockrows())
rc, o = go2('u_1', FX_SEEDS='cd' * 32)
ok &= case('GL8 a u arm with a catalogue sha other than the sealed one -> rc 1 "seeds bad" before the lock', rc == 1 and
           'seeds bad' in o and len(lockrows()) == n_lock)
rc, o = go2('u_1', mode='gamepatch', KYTY_GAME_PATCH='C:/x/p.txt')
t3 = (B2 / 's10' / 'times.txt').read_text()
ok &= case('GL9 KYTY_GAME_PATCH of the caller not seen by the game; a GamePatch: log line -> rc 7, the caches returned',
           rc == 7 and js2('u_1').get('gp') is None and 'GAMEPATCH interference: 1 lines' in o and
           'item 342 (e): lines beginning GamePatch: in log_u_1.txt: 1' in t3 and CX.app_manifest(None)[1] == PRE_APP and
           GAME2.read_bytes() == b'installed build X' and not Path(LOCK2).exists())
ia1 = js2('pi_w1').get('in_arm') or ''
t4 = (B2 / 's10' / 'times.txt').read_text()
ok &= case('GL10 IN_ARM (item 371 (g)): the game saw it - the tag, the installed sha, man_pre_app / man_pre_glc of the arm - and '
           'the successful return removed it', ia1.startswith('IN_ARM pi_w1 ') and ('installed: %s (copy' % INSTX) in ia1
           and ('man_pre_app: %s ' % cj2('pi_w1').get('man_pre_app', {}).get('sha', 'x')) in ia1 and
           ('man_pre_glc: %s ' % cj2('pi_w1').get('man_pre_glc', {}).get('sha', 'x')) in ia1 and
           len(cj2('pi_w1').get('man_pre_app', {}).get('sha', '')) == 64 and
           not (B2 / 's10' / 'IN_ARM').exists() and t4.count('guard ') >= 2 and 'removed after the successful return' in t4)
(B2 / 's10' / 'IN_ARM').write_text('IN_ARM pi_w0 2026-10-03T00:00:00Z pid 1 - a hard kill left it\n')
n_lock = len(lockrows())
rc, o = go2('pi_w0')
ok &= case('GL11 a hanging IN_ARM (a hard kill of an earlier arm) -> rc 1 "return failed guard" before the lock: no lock row, '
           'no attempt, the installed binary untouched, the guard kept', rc == 1 and 'return failed guard' in o and 'IN_ARM' in o
           and len(lockrows()) == n_lock and not (B2 / 's10' / 'attempt_pi_w0.txt').exists() and
           GAME2.read_bytes() == b'installed build X' and (B2 / 's10' / 'IN_ARM').exists())
(B2 / 's10' / 'IN_ARM').unlink()
put2(GAME2, b'another installed build')
n_lock = len(lockrows())
rc, o = go2('pi_w0')
t5 = (B2 / 's10' / 'times.txt').read_text()
ok &= case('GL12 an installed binary other than INST_WANT -> rc 1 inside the lock: nothing installed, no IN_ARM, no attempt, the '
           'lock taken and released, the row in times.txt', rc == 1 and 'installed binary not' in o and
           GAME2.read_bytes() == b'another installed build' and not (B2 / 's10' / 'IN_ARM').exists() and
           not (B2 / 's10' / 'attempt_pi_w0.txt').exists() and len(lockrows()) == n_lock + 2 and not Path(LOCK2).exists() and
           ('!= %s (item 374 (g)) - no arm' % INSTX) in t5)
put2(GAME2, b'4aa62e95 stand-in')
n_lock = len(lockrows())
rc, o = go2('pi_w0')
t6 = (B2 / 's10' / 'times.txt').read_text()
ok &= case('GL12b item 377 (b)(2): the installed = 4aa62e95 (the pinned u stand-in, the installed of item 342) -> rc 1 inside '
           'the lock: nothing installed, no IN_ARM, no attempt, the lock taken and released', rc == 1 and
           ('installed binary not %s' % INSTX) in o and GAME2.read_bytes() == b'4aa62e95 stand-in' and
           not (B2 / 's10' / 'IN_ARM').exists() and not (B2 / 's10' / 'attempt_pi_w0.txt').exists() and
           len(lockrows()) == n_lock + 2 and not Path(LOCK2).exists() and
           ('installed binary before the arm %s != %s (item 374 (g)) - no arm' % (sha2(PINU), INSTX)) in t6)
put2(GAME2, b'installed build X')
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
