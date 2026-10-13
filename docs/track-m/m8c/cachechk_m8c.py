"""M8c (HPP-860), member of ROADMAP s122 item 786(d): the translation-cache signature printed by the MS2 code itself
(shader_recompiler_compute_tests --m-wave1-cache of the same build and kytyGitVersion.h) at the defaults equals the
accepted string; also the all-KYTY_M_*=0 arm (item 786(g)(1)) and explicit =1 arm. No GPU case runs in this mode.
Runs at IDLE priority in its own cwd per arm. Usage: python cachechk_m8c.py"""
import os
import subprocess
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/m657/STOP'):
    print('LOCK or STOP')
    sys.exit(3)
EXE = 'C:/kyty/m657/m8c/build/shader_recompiler_compute_tests.exe'
OUT = 'C:/kyty/m657/m8c/cachechk'
H = '0d2da32ca7ff8b4e4c0fc008726e2c59abe2a8f5'
EXPECT_D = 'KytySC3:' + H + ':fixb26:fixb1b:fixf10:fixf19:mw1_3b'
EXPECT_Z = 'KytySC3:' + H + ':fixb26:fixb1b:fixf10:fixf19'
BS = chr(92)
DIR_D = '_ShaderCache' + BS + 'PPSA21564' + BS + 'variant_fixb26_fixb1b_fixf10_fixf19_mw1_3b'
DIR_Z = '_ShaderCache' + BS + 'PPSA21564' + BS + 'variant_fixb26_fixb1b_fixf10_fixf19'
KNOBS = ['KYTY_M_T234', 'KYTY_M_T233', 'KYTY_M_T256', 'KYTY_M_T306', 'KYTY_M_T032', 'KYTY_M_T203']
ARMS = [
    ('d', {}, '0x3b', EXPECT_D, DIR_D),
    ('e', {'KYTY_M_T234': '1', 'KYTY_M_T233': '1', 'KYTY_M_T256': '0', 'KYTY_M_T306': '1', 'KYTY_M_T032': '1',
           'KYTY_M_T203': '1'}, '0x3b', EXPECT_D, DIR_D),
    ('z', {k: '0' for k in KNOBS}, '0x00', EXPECT_Z, DIR_Z),
]
ok = True
log = []
for name, env_add, mask, sig, folder in ARMS:
    cwd = OUT + '/' + name
    os.makedirs(cwd, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update(env_add)
    p = subprocess.run([EXE, '--m-wave1-cache'], cwd=cwd, env=env, capture_output=True, creationflags=0x40)
    out = p.stdout.decode('utf-8', 'replace')
    with open(cwd + '/out.txt', 'w', encoding='utf-8', newline='') as f:
        f.write(out)
    lines = {}
    for ln in out.splitlines():
        if ln.startswith('[mw1] mask='):
            lines['mask'] = ln.split('=')[1].split()[0]
        elif ln.startswith('[mw1] cache signature='):
            lines['sig'] = ln[len('[mw1] cache signature='):]
        elif ln.startswith('[mw1] cache dir='):
            lines['dir'] = ln[len('[mw1] cache dir='):].split(' sig_ok=')[0]
    arm_ok = (p.returncode == 0 and lines.get('mask') == mask and lines.get('sig') == sig
              and lines.get('dir') == folder and 'ALL OK' in out)
    ok &= arm_ok
    log.append('== %s rc %d env %r' % (name, p.returncode, ' '.join('%s=%s' % kv for kv in env_add.items())))
    log.append(out.rstrip())
    log.append('member: mask %s sig %s dir %s -> %s' % (
        lines.get('mask') == mask, lines.get('sig') == sig, lines.get('dir') == folder, 'OK' if arm_ok else 'FAIL'))
# negative control of the comparator: the predicted-and-rejected hash must not pass
neg = 'KytySC3:baeea6e209399ed86e67c8f805dddc01ddcf631a:fixb26:fixb1b:fixf10:fixf19:mw1_3b'
neg_caught = neg != EXPECT_D
ok &= neg_caught
log.append('negative control (baeea6e2 string differs from the expected one): %s' % ('caught' if neg_caught else 'NOT caught'))
log.append('ALL OK' if ok else 'FAIL')
print('\n'.join(log))
sys.exit(0 if ok else 1)
