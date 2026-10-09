"""F29e (HPP-704): fixtures of the harness tools - the dry run of go_f29e.sh for both tags (form, knobs, hold, video), refusals of
go / launch / post (usage), the launcher checks in fixture mode (F29E_DRYRUN=2 with a fake process list and a fake block), mfsub_f29e.py,
enter_scene.py (ROOT), the copies of the FS10c tools (only names moved), and strict cp1250 output of each tool without PYTHONIOENCODING.
Port of C:/kyty/f287/fs10c/test_tools_fs10c.py.  The last line is ALL OK.  ASCII only.
usage: python test_tools_f29e.py"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
M = 'C:/kyty/f287/fs10c'
BASH = 'C:/Program Files/Git/usr/bin/bash.exe' if os.path.exists('C:/Program Files/Git/usr/bin/bash.exe') else 'bash'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_f29e.py sha256 %s target go_f29e.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'go_f29e.sh'))))
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
V = 'dryrun %s base b12_v level %s uf - sd 300 hold 330 timeout 480 rec --rec knobs KYTY_FIX_B12=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'
W = ('dryrun %s base b12_w level %s uf - sd 100 hold 310 timeout 900 rec --emu-arg=--vulkan-validation --emu-arg=true knobs KYTY_FIX_B12=1 '
     'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0')
CASES = [('b12_v', V % ('b12_v', SKY)), ('b12_w', W % ('b12_w', SKY)), ('b12_v_r1', V % ('b12_v_r1', SKY)), ('b12_w_r3', W % ('b12_w_r3', SKY))]
GO = os.path.join(HERE, 'go_f29e.sh').replace('\\', '/')
for tag, want in CASES:
    rc, out, raw = sh([GO, tag], {'F29E_DRYRUN': '1'})
    check('go dry run %s' % tag, rc == 0 and out.strip() == want, out)
    check('go dry run %s ASCII' % tag, ascii_ok(raw))
    check('go dry run %s: no KYTY_DIAG_B32, no other KYTY_FIX_, no KYTY_GAME_PATCH' % tag,
          'KYTY_DIAG_B32' not in out and out.count('KYTY_FIX_') == 1 and 'GAME_PATCH' not in out)
for bad in ('fs10_v', 'b13_v', 'b12_v_r4', 'b12_x', ''):
    rc, out, raw = sh([GO, bad], {'F29E_DRYRUN': '1'})
    check('go usage %r rc 2' % bad, rc == 2, out)
GOT = open(GO, encoding='ascii').read()
check('go: F29c full sha', 'TB=cabbd818397a8a299e7e64cf2d153197ad7e69e310015b5d473bb66f37802e95' in GOT)
check('go: FS10 full sha', 'FS10=abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe' in GOT)
check('go: binary copy and pinned copy', 'BIN=$F/bin/kyty_emulator_cabbd818.exe' in GOT and 'PINNED=$F/bin/kyty_emulator_abfded5e.exe' in GOT)
check('go: installed checked against FS10 before and after', '[ "$WANT" = "$FS10" ]' in GOT and '[ "$(cat $OUT/installed_after.txt)" = "$FS10" ]' in GOT)
check('go: seal path', 'SEAL=$G/pred/f29e_seal.md' in GOT)
check('go: lock with noclobber, lock.log lines', 'set -o noclobber' in GOT and 'echo "lock taken $T $(u)" >> $G/runs/lock.log' in GOT
      and 'echo "lock released $T $(u)" >> $G/runs/lock.log' in GOT and 'F29e HPP-704 go_f29e.sh' in GOT)
check('go: procload through the mask', 'python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt' in GOT)
check('go: display wake and check before the lock, hold, after', 'dispstate.py --wake' in GOT and '--hold-until $OUT/disp.stop' in GOT
      and 'DA=$(python $G/dispstate.py)' in GOT)
check('go: unsets KYTY_ and VK_LAYER_ before the call', "for v in $(env | grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'); do unset $v; done" in GOT)
check('go: the knobs after the options of enter_scene', '--pred $SEAL $UF $REC --hold $H $KN > $OUT/run.txt' in GOT)
check('go: five folders in the manifest', GOT.count('_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" '
                                              '"_SaveData=$EMU/_SaveData" "GLCache=$GLDIR"') == 1)
check('go: return checks the binary and the manifest, RETURN_FAILED keeps the lock', 'RETURN_FAILED' in GOT and '[ $MC = 0 ] || OK=0' in GOT)
check('go: merge return only for a VM tag', 'snap_f29e.py merge-return GLCache' in GOT and 'mfsub_f29e.py' in GOT)
check('go: base manifest of this seal', '$G/base/base.tsv' in GOT)
check('go: SERIES_STOP refuses', '[ -e $G/SERIES_STOP ]' in GOT)
check('go: stop file', '[ -e $F/STOP ]' in GOT)
CODE = '\n'.join(l for l in GOT.split('\n') if not l.lstrip().startswith('#'))
check('go: no KYTY_GPU_CHECKPOINTS, no --rd, no fs10c path in the code lines', 'GPU_CHECKPOINTS' not in CODE and '--rd' not in CODE
      and 'fs10c' not in CODE and '3861eeea' not in CODE)
# go = the FS10c chain with the binaries, the tags and the knob moved (the code lines after the header)
GS = open(os.path.join(M, 'go_fs10c.sh'), encoding='ascii').read()
body_new = GOT[GOT.index('export PATH=/usr/bin:/mingw64/bin:$PATH'):]
body_old = GS[GS.index('export PATH=/usr/bin:/mingw64/bin:$PATH'):]
kept = [l for l in body_old.split('\n') if 'fs10' not in l and 'FS10' not in l and 'FS9' not in l and 'STAND' not in l
        and not l.startswith(('TB=', 'BIN=', 'PINNED=')) and not l.lstrip().startswith('KN=')]
check('go: every FS10c code line without fs10 / FS9 / STAND is kept verbatim (%d lines)' % len(kept),
      all(l in body_new.split('\n') for l in kept), [l for l in kept if l not in body_new.split('\n')][:3])

# launcher in fixture mode
TMP = tempfile.mkdtemp(prefix='f29e_tt_')
blk = os.path.join(TMP, 'block.txt').replace('\\', '/')
fake = os.path.join(TMP, 'fake.json').replace('\\', '/')
tms = os.path.join(TMP, 'times.txt').replace('\\', '/')
json.dump([], open(fake, 'w'))
LA = os.path.join(HERE, 'launch_f29e.sh').replace('\\', '/')
X = {'F29E_GUARD_BLOCK': blk, 'F29E_GUARD_FAKE': fake, 'F29E_TIMES': tms, 'F29E_QUEUE_SKIP': '1', 'F29E_DISP_SKIP': '1',
     'F29E_DRYRUN': '2'}
rc, out, raw = sh([LA, 'b12_v'], X)
check('launch: block not open -> exit 8', rc == 8, out)
now = 1791431788
open(blk, 'w').write('2026-10-08T03:00:00Z %d CLEAN\n2026-10-08T03:11:00Z %d CLEAN\n2026-10-08T03:11:00Z %d OPEN\n' % (now, now + 660, now + 660))
rc, out, raw = sh([LA, 'b12_v'], X)
check('launch: open block -> dryrun2', rc == 0 and out.startswith('dryrun2'), out)
json.dump([dict(pid=4242, name='kyty_emulator.exe', path='C:/x/kyty_emulator.exe', start=now)], open(fake, 'w'))
rc, out, raw = sh([LA, 'b12_v'], X)
check('launch: user emulator -> exit 7, name masked', rc == 7 and 'kyty_emulator' not in out and '<app>' in out, out)
check('launch: times line written ASCII', os.path.exists(tms) and ascii_ok(open(tms, 'rb').read()))
for bad in ('nope', 'fs10_v', 'b12_v_r4'):
    rc, out, raw = sh([LA, bad], X)
    check('launch usage %s rc 2' % bad, rc == 2)
LAT = open(LA, encoding='ascii').read()
check('launch: detached call of go_f29e.sh with F29E_RUN_ID', 'nohup bash -c "bash $G/go_f29e.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\\$? >> $G/go_$T.out.txt"' in LAT
      and 'F29E_RUN_ID="${PAPERCLIP_RUN_ID:-}"' in LAT)
rc, out, raw = sh([os.path.join(HERE, 'post_f29e.sh').replace('\\', '/'), 'nope'])
check('post usage rc 2', rc == 2)
PT = open(os.path.join(HERE, 'post_f29e.sh'), encoding='ascii').read()
check('post: reader f29e_read.py, tempo, pair with fs10_v, lock refusal', 'python f29e_read.py $T --json $D/read.json' in PT
      and 'python tempo_f29e.py' in PT and 'C:/kyty/f287/fs10c/runs/fs10_v/sheet_fs10_v.png' in PT
      and '[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }' in PT)
WT = open(os.path.join(HERE, 'wait_f29e.sh'), encoding='ascii').read()
check('wait: at most 54 x 10 s, reads rc=, stop file ends the wait', 'seq 1 54' in WT and 'sleep 10' in WT and "grep -q '^rc='" in WT
      and 'C:/kyty/f287/STOP' in WT and 'C:/kyty/f287/f29e/go_$T.out.txt' in WT)
CT = open(os.path.join(HERE, 'chk_f29e.sh'), encoding='ascii').read()
check('chk: comments of HPP-704, queue_f29e.py', '/api/issues/HPP-704/comments' in CT and 'queue_f29e.py' in CT)

# mfsub
a = os.path.join(TMP, 'a.tsv')
b = os.path.join(TMP, 'b.tsv')
open(a, 'wb').write(b'GLCache\tx\t1\taa\n_ShaderCache\ty\t2\tbb\n')
open(b, 'wb').write(b'GLCache\tx\t1\taa\nGLCache\tz\t3\tcc\n_ShaderCache\ty\t2\tbb\n')
p = subprocess.run([sys.executable, os.path.join(HERE, 'mfsub_f29e.py'), a, b], capture_output=True, env=env_cp())
check('mfsub: extra GLCache only -> OK', p.returncode == 0 and p.stdout.startswith(b'SUBSET OK extra 1'), p.stdout)
open(b, 'wb').write(b'GLCache\tx\t1\taa\n_ShaderCache\ty\t2\tbX\n')
p = subprocess.run([sys.executable, os.path.join(HERE, 'mfsub_f29e.py'), a, b], capture_output=True, env=env_cp())
check('mfsub: changed file -> FAIL', p.returncode == 1, p.stdout)
open(b, 'wb').write(b'GLCache\tx\t1\taa\n_ShaderCache\ty\t2\tbb\n_SaveData\tq\t1\tdd\n')
p = subprocess.run([sys.executable, os.path.join(HERE, 'mfsub_f29e.py'), a, b], capture_output=True, env=env_cp())
check('mfsub: extra outside GLCache -> FAIL', p.returncode == 1, p.stdout)

# enter_scene and the copies
ES = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
check('enter_scene: ROOT moved to f29e', "ROOT = pathlib.Path('C:/kyty/f287/f29e')" in ES)
ESM = open(os.path.join(M, 'enter_scene.py'), encoding='utf-8').read()
check('enter_scene: = the FS10c file with names moved', ES == ESM.replace('fs10c', 'f29e').replace('FS10C', 'F29E').replace('FS10c', 'F29e')
      .replace('HPP-686', 'HPP-704'))
for nm in ('dispstate.py', 'manifest_fs4c.py', 'procload.py', 'idle142.py', 'sheet142.py', 'gates_default.txt', 'launch_run.py', 'run_safety99.py'):
    check('copy %s = FS10c' % nm, sha(os.path.join(HERE, nm)) == sha(os.path.join(M, nm)))
for nm in ('guard', 'hold', 'runchk', 'queue', 'tempo', 'snap', 'mfsub'):
    t = open(os.path.join(HERE, '%s_f29e.py' % nm), encoding='utf-8').read()
    o = open(os.path.join(M, '%s_fs10c.py' % nm), encoding='utf-8').read()
    check('copy %s_f29e.py = FS10c with names moved' % nm,
          t == o.replace('fs10c', 'f29e').replace('FS10C', 'F29E').replace('FS10c', 'F29e').replace('HPP-686', 'HPP-704'))
    check('%s_f29e.py has no fs10c path' % nm, 'f287/fs10c' not in t)
q = open(os.path.join(HERE, 'queue_f29e.py'), encoding='utf-8').read()
check('queue: own link HPP-704', "OWN = 'HPP-704'" in q)
r = open(os.path.join(HERE, 'runchk_f29e.py'), encoding='utf-8').read()
check('runchk: own link HPP-704 and F29E_RUN_ID', "OWN = 'HPP-704'" in r and 'F29E_RUN_ID' in r)
for tool, args in (('guard_f29e.py', ['status', '--block', blk]), ('mfsub_f29e.py', [a, a])):
    p = subprocess.run([sys.executable, os.path.join(HERE, tool)] + args, capture_output=True, env=env_cp())
    check('%s output ASCII / cp1250' % tool, ascii_ok(p.stdout) and p.returncode in (0, 8))
print('checks %d failed %d' % (N[0], N[1]))
if N[1] == 0:
    print('ALL OK')
sys.exit(0 if N[1] == 0 else 1)
