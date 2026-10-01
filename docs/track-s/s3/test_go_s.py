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


def seal(lines, name='01_s.md'):
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
seal(['go_s call: PLWAIT=540 bash C:/kyty/s288/go_s.sh %s' % t for t in s6], '02_s.md')
rc, o = go('pcw_1')
ok &= case('G20 S6 without the "pcw binary:" line of pred/02_s.md -> rc 1', rc == 1 and 'no pcw binary' in o)
seal(['go_s call: PLWAIT=540 bash C:/kyty/s288/go_s.sh %s' % t for t in s6] + ['pcw binary: %s C:/x/kyty.exe' % ('cd' * 32)],
     '02_s.md')
o6 = dict((t, go(t)) for t in s6)
ok &= case('G21 S6 DRY: the pcw binary installed, KYTY_S_PCW and the stand 15000, Sky Garden, stable 300',
           all(v[0] == 0 for v in o6.values()) and 'install C:/x/kyty.exe (%s)' % ('cd' * 32) in o6['pcw_1'][1] and
           'KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=15000' in o6['pcw_1'][1] and 'KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=15000' in
           o6['pcw_3'][1] and '--level underwater_aerial_garden' in o6['pcw_1'][1] and '--stable-draws 300' in o6['pcw_1'][1]
           and '--hold 330' in o6['pcw_1'][1])
ok &= case('G22 pcw_int: no snapshot - app and GLCache from pcw_3 post copies, hold 120',
           'restore app <- %s/s6/app_post/pcw_3;' % BASE.as_posix() in o6['pcw_int'][1] and
           'restore glc <- %s/s6/glc_post/pcw_3;' % BASE.as_posix() in o6['pcw_int'][1] and '--hold 120' in o6['pcw_int'][1])
ok &= case('G23 pcw_val: --vulkan-validation true with VK_LAYER_PATH, hold 310, timeout 600, video too',
           '--emu-arg=--vulkan-validation --emu-arg=true' in o6['pcw_val'][1] and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin'
           in o6['pcw_val'][1] and '--hold 310' in o6['pcw_val'][1] and '--timeout 600' in o6['pcw_val'][1] and ' --rec ' in
           o6['pcw_val'][1])
rc, o = go('pcw_4', dry='2')
ok &= case('G24 DRY=2 prints the plan before any seal check (pcw_4 has no call line)', rc == 0 and o.startswith('PLAN pcw_4:')
           and "the 'pcw binary:' line of pred/02_s.md" in o and 'KYTY_S_PCW=0' in o)
ok &= case('G25 no lock file was created by any DRY call', not Path(FXLOCK).exists())
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
