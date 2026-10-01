"""Offline fixtures of go_s.sh (track S, link S3, HPP-313; ROADMAP "SESSION 122" item 241 (g)-(z)) WITHOUT the game: a copy
of the harness with ROOT, the lock and the stop file moved into a fixture directory runs only its cheap refusals and its
DRY plans (DRY=1 after the seal call check, DRY=2 before it).  Checked: usage; the stop file and the lock before any process
(rc 4); PLWAIT not a number / above 540 (rc 2); the seal call line missing or with another PLWAIT (rc 1); an attempt already
made (rc 1); S6 without the "pcw binary:" line of its seal (rc 1); the plan of every arm kind: environment M / T / G, the
salt only on C4, the GLCache source of C2 / C4 / pcw_int, the snapshot source, validation only on pcw_val, video on every
arm, hold and timeouts; the script is ASCII.  The first output line names this suite and the harness by sha256; the output
ends with ALL OK.
    python C:/kyty/s288/test_go_s.py
"""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'go_s.sh')
print('suite test_go_s.py sha256 %s target go_s.sh sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
BASE = Path('C:/kyty/s288/s3/fx_go_s')
shutil.rmtree(BASE, ignore_errors=True)
(BASE / 'pred').mkdir(parents=True)
FXLOCK = (BASE / 'LOCK').as_posix()
FXSTOP = (BASE / 'STOP').as_posix()
text = Path(SRC).read_text(encoding='ascii')
for a, b in (('ROOT=C:/kyty/s288\n', 'ROOT=%s\n' % BASE.as_posix()), ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s\n' % FXLOCK),
             ('STOPF=/c/kyty/s288/STOP\n', 'STOPF=%s\n' % FXSTOP)):
    assert text.count(a) == 1, a
    text = text.replace(a, b)
(BASE / 'go_s.sh').write_bytes(text.encode('ascii'))
shutil.copy2(os.path.join(HERE, 'sc_s.py'), BASE / 'sc_s.py')
BASH = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
N = [0]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def go(tag, dry='1', plwait='540'):
    env = dict(os.environ)
    env['DRY'] = dry
    env['PLWAIT'] = plwait
    env['PATH'] = '/usr/bin:/mingw64/bin:' + env.get('PATH', '')
    p = subprocess.run([BASH, (BASE / 'go_s.sh').as_posix(), tag], capture_output=True, text=True, env=env, timeout=120)
    return p.returncode, (p.stdout + p.stderr).replace('bash.exe: warning: could not find /tmp, please create!\n', '')


def seal(lines, name='03_s.md'):
    (BASE / 'pred' / name).write_text('\n'.join(lines) + '\n', encoding='ascii')


ok = True
try:
    Path(SRC).read_bytes().decode('ascii')
    asc = True
except UnicodeError:
    asc = False
ok &= case('G1 go_s.sh is ASCII only (item 175 (v))', asc)
rc, o = go('Bad-Tag')
ok &= case('G2 a tag with other characters -> rc 2 usage', rc == 2 and 'usage' in o)
Path(FXSTOP).write_text('241 test\n')
rc, o = go('sw_m1')
ok &= case('G3 the stop file -> rc 4 BUSY before anything', rc == 4 and 'stop file' in o)
Path(FXSTOP).unlink()
Path(FXLOCK).write_text('go143a.sh v143_01 pid 1\n')
rc, o = go('sw_m1')
ok &= case('G4 a foreign lock -> rc 4 BUSY (lock held) before any process', rc == 4 and 'lock held: go143a.sh v143_01' in o)
Path(FXLOCK).unlink()
rc, o = go('sw_m1', plwait='x')
ok &= case('G5 PLWAIT not a number -> rc 2', rc == 2 and 'bad PLWAIT' in o)
rc, o = go('sw_m1', plwait='541')
ok &= case('G6 PLWAIT above 540 -> rc 2', rc == 2)
rc, o = go('zz_9')
ok &= case('G7 an unknown tag (sc_s.py --plan) -> rc 2', rc == 2 and 'unknown tag' in o)
seal(['x'])
rc, o = go('sw_m1')
ok &= case('G8 no seal call line -> rc 1', rc == 1 and 'PLWAIT differs from the seal' in o)
seal(['go_s call: PLWAIT=300 bash C:/kyty/s288/go_s.sh sw_m1'])
rc, o = go('sw_m1')
ok &= case('G9 the seal call line with another PLWAIT -> rc 1', rc == 1)
seal(['go_s call: PLWAIT=540 bash C:/kyty/s288/go_s.sh sw_m1'] * 2)
rc, o = go('sw_m1')
ok &= case('G10 two call lines -> rc 1', rc == 1)
tags = ('sw_m1', 'sw_t1', 'c1_0', 'c2_0', 'c3_0', 'c4_0', 't2_01', 'g_1', 'g_3_2')
seal(['go_s call: PLWAIT=540 bash C:/kyty/s288/go_s.sh %s' % t for t in tags])
out = {}
for t in tags:
    rc, o = go(t)
    out[t] = (rc, o)
ok &= case('G11 DRY=1 of every S4 arm kind -> rc 0 with a DRY line', all(v[0] == 0 and v[1].startswith('DRY %s:' % k)
                                                                     for k, v in out.items()))
m = out['sw_m1'][1]
ok &= case('G12 M arm: the pinned 9235a7ac, restore snap0 and snap0_drv, video, hold 120, no trace, no salt',
           'install /c/kyty/s128/kyty_emulator_9235a7ac.exe (9235a7ac' in m and 'restore app <- C:/kyty/s288/snap0;' in m
           and 'restore glc <- C:/kyty/s288/snap0_drv;' in m and ' --rec ' in m and '--hold 120 ' in m and
           'KYTY_AV_TRACE' not in m and 'SALT' not in m and '--stable-draws 100 --timeout 480' in m and
           'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in m and '--root %s/s4' % BASE.as_posix() in m)
ok &= case('G13 T arm: KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1, no KYTY_DUMP_GCN', 'KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1'
           in out['sw_t1'][1] and 'DUMP_GCN' not in out['sw_t1'][1] and 'KYTY_AV_TRACE=1' in out['t2_01'][1])
ok &= case('G14 G arm: + KYTY_DUMP_GCN=1; g_3_2 on cymbal_party_land', 'KYTY_DUMP_GCN=1' in out['g_1'][1] and
           '--level cymbal_party_land' in out['g_3_2'][1])
ok &= case('G15 C2 restores GLCache from glc_post/c1_0, C4 from glc_post/c3_0; C1 and C3 from snap0_drv',
           'restore glc <- %s/s4/glc_post/c1_0;' % BASE.as_posix() in out['c2_0'][1] and
           'restore glc <- %s/s4/glc_post/c3_0;' % BASE.as_posix() in out['c4_0'][1] and
           'restore glc <- C:/kyty/s288/snap0_drv;' in out['c1_0'][1] and 'restore glc <- C:/kyty/s288/snap0_drv;' in out['c3_0'][1])
ok &= case('G16 the salt only on C4 (KYTY_PIPELINE_SALT=c4_0), timeout 900 there', 'KYTY_PIPELINE_SALT=c4_0' in out['c4_0'][1]
           and '--timeout 900' in out['c4_0'][1] and all('SALT' not in out[t][1] for t in tags if t != 'c4_0'))
ok &= case('G17 every arm restores the app caches from snap0 (S4)', all('restore app <- C:/kyty/s288/snap0;' in out[t][1]
                                                                       for t in tags))
ok &= case('G18 no validation on S4 arms', all('--vulkan-validation' not in out[t][1] for t in tags))
Path(BASE / 's4' / 'attempt_sw_m1.txt').write_text('x')
rc, o = go('sw_m1')
ok &= case('G19 an attempt already made -> rc 1, no repeat', rc == 1 and 'attempt already made' in o)
s6 = ('pcw_1', 'pcw_3', 'pcw_int', 'pcw_val')
seal(['go_s call: PLWAIT=540 bash C:/kyty/s288/go_s.sh %s' % t for t in s6], '04_s.md')
rc, o = go('pcw_1')
ok &= case('G20 S6 without the "pcw binary:" line of pred/04_s.md -> rc 1', rc == 1 and 'no pcw binary' in o)
seal(['go_s call: PLWAIT=540 bash C:/kyty/s288/go_s.sh %s' % t for t in s6] + ['pcw binary: %s C:/x/kyty.exe' % ('cd' * 32)],
     '04_s.md')
o6 = dict((t, go(t)) for t in s6)
ok &= case('G21 S6 DRY: the pcw binary installed, KYTY_S_PCW and the stand 15000, Sky Garden, stable 300',
           all(v[0] == 0 for v in o6.values()) and 'install C:/x/kyty.exe (%s)' % ('cd' * 32) in o6['pcw_1'][1] and
           'KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=15000' in o6['pcw_1'][1] and 'KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=15000' in
           o6['pcw_3'][1] and '--level underwater_aerial_garden' in o6['pcw_1'][1] and '--stable-draws 300' in o6['pcw_1'][1]
           and '--hold 330' in o6['pcw_1'][1])
ok &= case('G22 pcw_int: no snapshot - app and GLCache from pcw_3 post copies, hold 120',
           'restore app <- %s/s6/app_post/pcw_3;' % BASE.as_posix() in o6['pcw_int'][1] and
           'restore glc <- %s/s6/glc_post/pcw_3;' % BASE.as_posix() in o6['pcw_int'][1] and '--hold 120' in o6['pcw_int'][1])
ok &= case('G23b form W (item 254 (e)): pcw_val runs with KYTY_PIPELINE_PRECACHE=0; no other arm of S4 / S6 does',
           ' KYTY_PIPELINE_PRECACHE=0 ' in o6['pcw_val'][1] and all('KYTY_PIPELINE_PRECACHE' not in o6[t][1] for t in s6
                                                              if t != 'pcw_val') and
           all('KYTY_PIPELINE_PRECACHE' not in out[t][1] for t in tags))
ok &= case('G23 pcw_val: --vulkan-validation true with VK_LAYER_PATH, hold 310, timeout 600, video too',
           '--emu-arg=--vulkan-validation --emu-arg=true' in o6['pcw_val'][1] and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin'
           in o6['pcw_val'][1] and '--hold 310' in o6['pcw_val'][1] and '--timeout 600' in o6['pcw_val'][1] and ' --rec ' in
           o6['pcw_val'][1])
rc, o = go('pcw_4', dry='2')
ok &= case('G24 DRY=2 prints the plan before any seal check (pcw_4 has no call line)', rc == 0 and o.startswith('PLAN pcw_4:')
           and "the 'pcw binary:' line of pred/04_s.md" in o and 'KYTY_S_PCW=0' in o)
ok &= case('G25 no lock file was created by any DRY call', not Path(FXLOCK).exists())

# ============================================================== S3b (HPP-325, item 250): the path INSIDE the lock, stubbed
# A second copy of the harness runs its whole path inside a fixture lock: the game, the pinned binary, the snapshots, the
# live caches and GLCache are fixture files; enter_scene.py, procload.py, idle142.py, fgcpu143.py and powershell are stubs;
# sc_s.py is the real one for --plan and a stub for --check-seal / --allowed / --tag; cachex_s.py is the real one.
import importlib.util  # noqa: E402
import json  # noqa: E402
B2 = Path('C:/kyty/s288/s3b/fx_go_lock')
shutil.rmtree(B2, ignore_errors=True)
for d in ('pred', 'bin', 'game', 'emu', 'lad/NVIDIA/GLCache'):
    (B2 / d).mkdir(parents=True)
EMU2, LAD2, GLC2 = B2 / 'emu', B2 / 'lad', B2 / 'lad' / 'NVIDIA' / 'GLCache'
LOCK2, STOP2, GAME2, PIN2 = (B2 / 'LOCK').as_posix(), (B2 / 'STOP').as_posix(), B2 / 'game' / 'kyty_emulator.exe', B2 / 'pin.exe'
ENV2 = dict(CACHEX_EMU=str(EMU2), CACHEX_GLC=str(GLC2), CACHEX_LOCK=LOCK2, CACHEX_KNOWN_LAD=str(LAD2), LOCALAPPDATA=str(LAD2))
os.environ.update(ENV2)
_cs = importlib.util.spec_from_file_location('cachex_fx', os.path.join(HERE, 'cachex_s.py'))
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
put2(GLC2 / 'x' / 'y.toc', b'glc toc')
SNAPA = CX.copy_set('app', str(B2 / 'snap0'))[1].split()[-1]
SNAPD = CX.copy_set('glc', str(B2 / 'snap0_drv'))[1].split()[-1]
put2(EMU2 / '_ShaderCache' / 'PPSA21564' / 'installed.bin', b'installed state')      # the installed caches differ from snap0
put2(GLC2 / 'x' / 'other.bin', b'a foreign driver file')
PRE_APP, PRE_GLC = CX.app_manifest(None)[1], CX.glc_manifest(str(GLC2))[1]
put2(PIN2, b'pinned 9235a7ac stand-in')
put2(GAME2, b'installed build X')                                                  # installed != pinned (RC1)
put2(B2 / 'gates_default.txt', b'')
for name, body in (('procload.py', 'import sys\nsys.exit(0)\n'), ('idle142.py', 'import sys\nsys.exit(0)\n'),
                   ('fgcpu143.py', "print('fgcpu stub')\n")):
    put2(B2 / name, body.encode('ascii'))
put2(B2 / 'bin' / 'powershell', b'#!/bin/sh\necho 0\n')
shutil.copy2(os.path.join(HERE, 'cachex_s.py'), B2 / 'cachex_s.py')
put2(B2 / 'sc_s.py', ("import importlib.util, sys\na = sys.argv[1:]\nif a[:1] == ['--plan']:\n"
                      "    s = importlib.util.spec_from_file_location('scs', %r)\n    m = importlib.util.module_from_spec(s)\n"
                      "    s.loader.exec_module(m)\n    sys.exit(m.main(a))\n"
                      "if '--check-seal' in a:\n    print('SEAL: PASS (fixture stub)')\n    sys.exit(0)\n"
                      "if a[:1] == ['--allowed']:\n    print('ALLOWED %%s: yes (fixture stub)' %% a[1])\n    sys.exit(0)\n"
                      "print('ARM stub')\nsys.exit(0)\n" % os.path.join(HERE, 'sc_s.py').replace('\\', '/')).encode('ascii'))
put2(B2 / 'enter_scene.py', (
    "import json, os, sys\ntag = sys.argv[1]\nroot = sys.argv[sys.argv.index('--root') + 1]\n"
    "emu, glc = os.environ['CACHEX_EMU'], os.environ['CACHEX_GLC']\n"
    "open(os.path.join(root, 'log_%s.txt' % tag), 'w').write('log of the stub')\n"
    "json.dump({'tag': tag}, open(os.path.join(root, '%s.json' % tag), 'w'))\n"
    "open(os.path.join(emu, '_PipelineCache', 'PPSA21564.bin'), 'wb').write(b'the game wrote the driver cache')\n"
    "open(os.path.join(glc, 'x', 'game.bin'), 'wb').write(b'the game wrote GLCache')\n"
    "m = os.environ.get('FX_MODE', '')\n"
    "if m == 'breakret':\n    open(os.path.join(root, 'glc_pre', 'x', 'y.bin'), 'wb').write(b'a corrupted copy')\n"
    "if m == 'breakbin':\n    open(os.path.join(root, 'installed_bin_pre.exe'), 'wb').write(b'a corrupted binary copy')\n"
    "print('VERDICT: stub')\n").encode('ascii'))
text2 = Path(SRC).read_text(encoding='ascii')
for a, b in (('ROOT=C:/kyty/s288\n', 'ROOT=%s\n' % B2.as_posix()), ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s\n' % LOCK2),
             ('STOPF=/c/kyty/s288/STOP\n', 'STOPF=%s\n' % STOP2),
             ('GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"\n', 'GAME="%s"\n' % GAME2.as_posix()),
             ('BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"\n',
              'BUILD_EXPECT="%s"\n' % sha2(PIN2)),
             ('BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"\n', 'BUILD_PINNED="%s"\n' % PIN2.as_posix()),
             ('SNAP_APP="d8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4"\n', 'SNAP_APP="%s"\n' % SNAPA),
             ('SNAP_DRV="1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028"\n', 'SNAP_DRV="%s"\n' % SNAPD),
             ('RSRC_APP="C:/kyty/s288/snap0"', 'RSRC_APP="%s"' % (B2 / 'snap0').as_posix()),
             ('RSRC_GLC="C:/kyty/s288/snap0_drv"', 'RSRC_GLC="%s"' % (B2 / 'snap0_drv').as_posix()),
             ('RSLEEP=5\n', 'RSLEEP=0\n')):
    assert text2.count(a) == 1, a
    text2 = text2.replace(a, b)
(B2 / 'go_s.sh').write_bytes(text2.encode('ascii'))
TAGS2 = ('sw_m1', 'sw_m2', 'sw_m3', 'sw_t1')
(B2 / 'pred' / '03_s.md').write_bytes(''.join('go_s call: PLWAIT=540 bash C:/kyty/s288/go_s.sh %s\n' % t
                                              for t in TAGS2).encode('ascii'))
BINP = '/' + B2.as_posix()[0].lower() + B2.as_posix()[2:] + '/bin'


def go2(tag, mode='', dry='0', **env_over):
    env = dict(os.environ)
    env.update(ENV2)
    env.update(DRY=dry, PLWAIT='540', FX_MODE=mode, PATH=BINP + ':/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    env.update(env_over)
    p = subprocess.run([BASH, (B2 / 'go_s.sh').as_posix(), tag], capture_output=True, text=True, env=env, timeout=300)
    return p.returncode, (p.stdout + p.stderr).replace('bash.exe: warning: could not find /tmp, please create!\n', '')


def cj2(tag):
    p = B2 / 's4' / 'runs_s' / ('%s.cache.json' % tag)
    return json.loads(p.read_text()) if p.exists() else {}


def lockrows():
    p = B2 / 's4' / 'runs_s' / 'lock.log'
    return p.read_text().splitlines() if p.exists() else []


rc, o = go2('sw_m1')
c = cj2('sw_m1')
INST = sha2(GAME2)
ok &= case('GL1 RC1: installed != pinned -> after the arm the INSTALLED build is back (not the pinned one); json '
           'installed_before = installed_after = its sha; the copy installed_bin_pre.exe kept', rc == 0 and
           GAME2.read_bytes() == b'installed build X' and c.get('installed_before', {}).get('sha') == INST and
           c.get('installed_after', {}).get('sha') == INST and INST != sha2(PIN2) and
           sha2(B2 / 's4' / 'installed_bin_pre.exe') == INST)
ok &= case('GL2 the arm restored snap0 and snap0_drv, the caches and GLCache came back to the state before the arm',
           c.get('restore_app', {}).get('got') == SNAPA and c.get('restore_glc', {}).get('got') == SNAPD and
           CX.app_manifest(None)[1] == PRE_APP and CX.glc_manifest(str(GLC2))[1] == PRE_GLC and
           c.get('return_app', {}).get('got') == c.get('return_app', {}).get('expected') and
           c.get('return_glc', {}).get('got') == c.get('return_glc', {}).get('expected'))
ok &= case('GL3 RC10 / RC2 rows in the json: man_launch_glc = restore_glc.got, glc_launch.txt / glc_post.txt written, '
           'return_prev ok 1, arm_start utc', c.get('man_launch_glc', {}).get('sha') == SNAPD and
           (B2 / 's4' / 'runs_s' / 'sw_m1.glc_launch.txt').exists() and (B2 / 's4' / 'runs_s' / 'sw_m1.glc_post.txt').exists()
           and c.get('return_prev', {}).get('ok') == '1' and c.get('arm_start', {}).get('utc', '').endswith('Z'))
lr = lockrows()
ok &= case('GL4 the lock taken and released (lock.log UTC rows), no lock file left, no RETURN_FAILED guard',
           len(lr) == 2 and lr[0].startswith('lock taken sw_m1 ') and lr[1].startswith('lock released sw_m1 ')
           and not Path(LOCK2).exists() and not (B2 / 's4' / 'RETURN_FAILED').exists())
rc, o = go2('sw_m2', mode='breakret')
g = (B2 / 's4' / 'RETURN_FAILED')
times2 = (B2 / 's4' / 'times.txt').read_text() if (B2 / 's4' / 'times.txt').exists() else ''
ok &= case('GL5 RC2: a failed GLCache return -> the guard RETURN_FAILED (tag, both manifests, the binary) written before '
           'the unlock, a times.txt line, a stdout line for the comment; rc 1; the lock released; the binary still back',
           rc == 1 and g.exists() and g.read_text().startswith('RETURN_FAILED sw_m2 ') and 'glc: restore by hand' in
           g.read_text() and 'RETURN FAILED rc 1: guard' in times2 and 'RETURN FAILED: guard' in o and
           lockrows()[-1].startswith('lock released sw_m2 ') and not Path(LOCK2).exists() and
           GAME2.read_bytes() == b'installed build X')
n_lock = len(lockrows())
rc, o = go2('sw_m3')
rc_d, o_d = go2('sw_m3', dry='1')
ok &= case('GL6 RC2: the next call refuses rc 1 while the guard exists - before any process (no lock taken), DRY too',
           rc == 1 and 'return failed guard' in o and rc_d == 1 and len(lockrows()) == n_lock and
           not (B2 / 's4' / 'attempt_sw_m3.txt').exists())
g.unlink()                                                    # the lead, after the return by hand
CX.restore_set('glc', str(B2 / 's4' / 'glc_pre'), sha2(B2 / 's4' / 'glc_pre' / 'MANIFEST.txt'))
rc, o = go2('sw_m3', LOCALAPPDATA=str(B2 / 'elsewhere'))
ok &= case('GL7 RC9: %LOCALAPPDATA% of the environment != the known folder -> rc 1 before the lock, nothing installed',
           rc == 1 and 'glcache path' in o and 'MISMATCH' in o and len(lockrows()) == n_lock and
           GAME2.read_bytes() == b'installed build X')
rc, o = go2('sw_t1', mode='breakbin')
ok &= case('GL8 RC1 + RC2: the copy of the installed binary corrupted during the arm -> the return refuses it (sha), '
           'RETURN_FAILED names the binary, rc 1', rc == 1 and g.exists() and 'binary: ' in g.read_text() and
           ('must be %s' % INST) in g.read_text())
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
