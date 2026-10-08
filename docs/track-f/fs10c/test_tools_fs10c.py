"""FS10c (HPP-686): fixtures of the harness tools - the dry run of go_fs10c.sh for every tag (form, knobs, hold, video), refusals of
go / launch / post (usage, stop file names), the launcher checks in fixture mode (FS10C_DRYRUN=2 with a fake process list and a fake block),
mfsub_fs10c.py (subset after the merge return), enter_scene.py (ROOT, user form), the copies of the F25m tools (only names moved), and
strict cp1250 output of each tool without PYTHONIOENCODING.  The last line is ALL OK.  ASCII only.
usage: python test_tools_fs10c.py"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
M = 'C:/kyty/f287/f25m'
BASH = 'C:/Program Files/Git/usr/bin/bash.exe' if os.path.exists('C:/Program Files/Git/usr/bin/bash.exe') else 'bash'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_fs10c.py sha256 %s target go_fs10c.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'go_fs10c.sh'))))
N = [0, 0]


def check(name, cond, got=None):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s %s' % (name, '' if got is None else repr(got)[:300]))


def env_cp():
    e = dict(os.environ)
    e.pop('PYTHONIOENCODING', None)
    e['PYTHONUTF8'] = '0'
    e['PATH'] = '/usr/bin:/mingw64/bin:' + e.get('PATH', '')
    return e


def sh(args, extra=None):
    e = env_cp()
    e.update(extra or {})
    p = subprocess.run([BASH] + args, capture_output=True, env=e)
    return p.returncode, p.stdout.decode('cp1250', 'strict'), p.stdout


def ascii_ok(b):
    return all(c < 128 for c in b)


SKY = 'underwater_aerial_garden'
STAND = 'KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3'
HARN = 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22'
CASES = [('fs10_s1', 'dryrun fs10_s1 base fs10_s1 level %s uf --user-form sd 300 hold 150 timeout 480 rec - knobs %s' % (SKY, STAND)),
         ('fs10_s0', 'dryrun fs10_s0 base fs10_s0 level %s uf --user-form sd 300 hold 150 timeout 480 rec - knobs %s KYTY_FIX_B36=0' % (SKY, STAND)),
         ('fs10_f1', 'dryrun fs10_f1 base fs10_f1 level %s uf - sd 300 hold 150 timeout 480 rec --rec knobs %s %s' % (SKY, HARN, STAND)),
         ('fs10_v', 'dryrun fs10_v base fs10_v level %s uf - sd 300 hold 330 timeout 480 rec --rec knobs KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' % SKY),
         ('fs10_w', 'dryrun fs10_w base fs10_w level %s uf - sd 100 hold 310 timeout 900 rec --emu-arg=--vulkan-validation --emu-arg=true knobs '
                    'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' % SKY),
         ('fs10_v_r1', 'dryrun fs10_v_r1 base fs10_v level %s uf - sd 300 hold 330 timeout 480 rec --rec knobs KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' % SKY)]
GO = os.path.join(HERE, 'go_fs10c.sh').replace('\\', '/')
for tag, want in CASES:
    rc, out, raw = sh([GO, tag], {'FS10C_DRYRUN': '1'})
    check('go dry run %s' % tag, rc == 0 and out.strip() == want, out)
    check('go dry run %s ASCII' % tag, ascii_ok(raw))
    check('go dry run %s: no KYTY_DIAG_B32, no KYTY_FIX_B36=1, no KYTY_GAME_PATCH' % tag,
          'KYTY_DIAG_B32' not in out and 'KYTY_FIX_B36=1' not in out and 'GAME_PATCH' not in out)
for bad in ('fs10_s2', 'b36_v', 'fs10_v_r4', ''):
    rc, out, raw = sh([GO, bad], {'FS10C_DRYRUN': '1'})
    check('go usage %r rc 2' % bad, rc == 2, out)
GOT = open(GO, encoding='ascii').read()
check('go: FS10 full sha', 'TB=abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe' in GOT)
check('go: FS9 full sha', 'FS9=3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5' in GOT)
check('go: binary copy and pinned copy', 'BIN=$F/bin/kyty_emulator_abfded5e.exe' in GOT and 'PINNED=$F/bin/kyty_emulator_3861eeea.exe' in GOT)
check('go: lock with noclobber, lock.log lines', 'set -o noclobber' in GOT and 'echo "lock taken $T $(u)" >> $G/runs/lock.log' in GOT
      and 'echo "lock released $T $(u)" >> $G/runs/lock.log' in GOT)
check('go: procload through the mask', 'python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt' in GOT)
check('go: display wake and check before the lock, hold, after', 'dispstate.py --wake' in GOT and '--hold-until $OUT/disp.stop' in GOT
      and 'DA=$(python $G/dispstate.py)' in GOT)
check('go: unsets KYTY_ and VK_LAYER_ before the call', "for v in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'); do unset $v; done" in GOT)
check('go: the knobs after the options of enter_scene', '--pred $SEAL $UF $REC --hold $H $KN > $OUT/run.txt' in GOT)
check('go: five folders in the manifest', GOT.count('_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" '
                                              '"_SaveData=$EMU/_SaveData" "GLCache=$GLDIR"') == 1)
check('go: return checks the binary and the manifest, RETURN_FAILED keeps the lock', 'RETURN_FAILED' in GOT and '[ $MC = 0 ] || OK=0' in GOT)
check('go: merge return only for a VM tag', 'snap_fs10c.py merge-return GLCache' in GOT and 'mfsub_fs10c.py' in GOT)
check('go: SERIES_STOP refuses', '[ -e $G/SERIES_STOP ]' in GOT)
check('go: stop file', '[ -e $F/STOP ]' in GOT)
CODE = '\n'.join(l for l in GOT.split('\n') if not l.lstrip().startswith('#'))
check('go: no KYTY_GPU_CHECKPOINTS, no --rd in the code lines', 'GPU_CHECKPOINTS' not in CODE and '--rd' not in CODE)

# launcher in fixture mode
TMP = tempfile.mkdtemp(prefix='fs10c_tt_')
blk = os.path.join(TMP, 'block.txt').replace('\\', '/')
fake = os.path.join(TMP, 'fake.json').replace('\\', '/')
tms = os.path.join(TMP, 'times.txt').replace('\\', '/')
json.dump([], open(fake, 'w'))
LA = os.path.join(HERE, 'launch_fs10c.sh').replace('\\', '/')
X = {'FS10C_GUARD_BLOCK': blk, 'FS10C_GUARD_FAKE': fake, 'FS10C_TIMES': tms, 'FS10C_QUEUE_SKIP': '1', 'FS10C_DISP_SKIP': '1',
     'FS10C_DRYRUN': '2'}
rc, out, raw = sh([LA, 'fs10_v'], X)
check('launch: block not open -> exit 8', rc == 8, out)
now = 1791431788
open(blk, 'w').write('2026-10-08T03:00:00Z %d CLEAN\n2026-10-08T03:11:00Z %d CLEAN\n2026-10-08T03:11:00Z %d OPEN\n' % (now, now + 660, now + 660))
rc, out, raw = sh([LA, 'fs10_v'], X)
check('launch: open block -> dryrun2', rc == 0 and out.startswith('dryrun2'), out)
json.dump([dict(pid=4242, name='kyty_emulator.exe', path='C:/x/kyty_emulator.exe', start=now)], open(fake, 'w'))
rc, out, raw = sh([LA, 'fs10_v'], X)
check('launch: user emulator -> exit 7, name masked', rc == 7 and 'kyty_emulator' not in out and '<app>' in out, out)
check('launch: times line written ASCII', os.path.exists(tms) and ascii_ok(open(tms, 'rb').read()))
rc, out, raw = sh([LA, 'nope'], X)
check('launch usage rc 2', rc == 2)
rc, out, raw = sh([os.path.join(HERE, 'post_fs10c.sh').replace('\\', '/'), 'nope'])
check('post usage rc 2', rc == 2)
WT = open(os.path.join(HERE, 'wait_fs10c.sh'), encoding='ascii').read()
check('wait: at most 54 x 10 s, reads rc=, stop file ends the wait', 'seq 1 54' in WT and 'sleep 10' in WT and "grep -q '^rc='" in WT
      and 'C:/kyty/f287/STOP' in WT)

# mfsub
a = os.path.join(TMP, 'a.tsv')
b = os.path.join(TMP, 'b.tsv')
open(a, 'wb').write(b'GLCache\tx\t1\taa\n_ShaderCache\ty\t2\tbb\n')
open(b, 'wb').write(b'GLCache\tx\t1\taa\nGLCache\tz\t3\tcc\n_ShaderCache\ty\t2\tbb\n')
p = subprocess.run([sys.executable, os.path.join(HERE, 'mfsub_fs10c.py'), a, b], capture_output=True, env=env_cp())
check('mfsub: extra GLCache only -> OK', p.returncode == 0 and p.stdout.startswith(b'SUBSET OK extra 1'), p.stdout)
open(b, 'wb').write(b'GLCache\tx\t1\taa\n_ShaderCache\ty\t2\tbX\n')
p = subprocess.run([sys.executable, os.path.join(HERE, 'mfsub_fs10c.py'), a, b], capture_output=True, env=env_cp())
check('mfsub: changed file -> FAIL', p.returncode == 1, p.stdout)
open(b, 'wb').write(b'GLCache\tx\t1\taa\n_ShaderCache\ty\t2\tbb\n_SaveData\tq\t1\tdd\n')
p = subprocess.run([sys.executable, os.path.join(HERE, 'mfsub_fs10c.py'), a, b], capture_output=True, env=env_cp())
check('mfsub: extra outside GLCache -> FAIL', p.returncode == 1, p.stdout)

# enter_scene and the copies
ES = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
check('enter_scene: ROOT moved to fs10c', "ROOT = pathlib.Path('C:/kyty/f287/fs10c')" in ES)
check('enter_scene: user form branch kept', "    if options.user_form:   # F25m (item 613 (g)(3)): the user form - only the guest arguments of the entry" in ES)
ESM = open(os.path.join(M, 'enter_scene.py'), encoding='utf-8').read()
check('enter_scene: = the F25m file except ROOT and the header line',
      ES.split('\n', 1)[1].replace("f287/fs10c')", "f287/f25m')") == ESM)
for nm in ('dispstate.py', 'manifest_fs4c.py', 'procload.py', 'idle142.py', 'sheet142.py', 'gates_default.txt'):
    check('copy %s = F25m' % nm, sha(os.path.join(HERE, nm)) == sha(os.path.join(M, nm)))
for nm in ('guard', 'hold', 'runchk', 'queue'):
    t = open(os.path.join(HERE, '%s_fs10c.py' % nm), encoding='utf-8').read()
    o = open(os.path.join(M, '%s_f25m.py' % nm), encoding='utf-8').read()
    back = t.replace('f287/fs10c', 'f287/f25m').replace('guard_fs10c', 'guard_f25m').replace('hold_fs10c', 'hold_f25m').replace(
        'go_fs10c', 'go_f25m').replace('HPP-686', 'HPP-680').replace('FS10C_RUN_ID', 'F25M_RUN_ID').replace('post_fs10c', 'post_f25m')
    check('copy %s_fs10c.py = F25m with names moved' % nm, back == o)
    check('%s_fs10c.py has no f25m path' % nm, 'f287/f25m' not in t)
q = open(os.path.join(HERE, 'queue_fs10c.py'), encoding='utf-8').read()
check('queue: own link HPP-686', "OWN = 'HPP-686'" in q)
r = open(os.path.join(HERE, 'runchk_fs10c.py'), encoding='utf-8').read()
check('runchk: own link HPP-686 and FS10C_RUN_ID', "OWN = 'HPP-686'" in r and 'FS10C_RUN_ID' in r)
for tool, args in (('guard_fs10c.py', ['status', '--block', blk]), ('mfsub_fs10c.py', [a, a])):
    p = subprocess.run([sys.executable, os.path.join(HERE, tool)] + args, capture_output=True, env=env_cp())
    check('%s output ASCII / cp1250' % tool, ascii_ok(p.stdout) and p.returncode in (0, 8))
print('checks %d failed %d' % (N[0], N[1]))
if N[1] == 0:
    print('ALL OK')
sys.exit(0 if N[1] == 0 else 1)
