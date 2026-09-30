"""Fixtures of the chain go142a.sh (session 142 step 0, HPP-277; ROADMAP s122 item 221 (g)(1)-(4), item 105 (v), general
rule 26).  The script is copied into a fixture directory with its ROOT, LOCK, STOPF and GAME lines replaced (each replacement
must hit exactly one line), then run through bash for the refusals that stop before any guard (usage, stop file, lock,
PLWAIT, one attempt, order, the seal's call line) and for DRY=1 plans of every tag; plus static checks of the real script
(constants, tag -> level = sc142.level_of, SEQ = sc142.SEQ, holds, ASCII, the stop file and the lock before any process).
No game, no guard, no lock of the machine is touched.  The first output line names the suite and the target by sha256; the
output ends with ALL OK.
    python C:/kyty/s142/test_go142a.py [<go142a.sh under test>]
"""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'go142a.sh')
print('suite test_go142a.py sha256 %s target go142a.sh sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc142_for_chain', os.path.join(HERE, 'sc142.py'))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
BASH = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
FX = Path('C:/kyty/s142/fx_go142a')
shutil.rmtree(FX, ignore_errors=True)
FX.mkdir(parents=True)
TEXT = Path(SRC).read_bytes().decode('utf-8')
N = [0]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def fixture(name):
    root = FX / name
    root.mkdir()
    (root / 'pred').mkdir()
    t = TEXT
    for old, new in (('ROOT=C:/kyty/s142\n', 'ROOT=%s\n' % root.as_posix()),
                     ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s/LOCKFILE\n' % root.as_posix()),
                     ('STOPF=/c/kyty/s142/STOP\n', 'STOPF=%s/STOP\n' % root.as_posix()),
                     ('GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"\n', 'GAME="%s/game.exe"\n' % root.as_posix())):
        assert t.count(old) == 1, old
        t = t.replace(old, new)
    (root / 'go.sh').write_bytes(t.encode('utf-8'))
    return root


def seal(root, lines):
    (root / 'pred' / '01_sc142.md').write_text('fixture seal\n' + ''.join(l + '\n' for l in lines), encoding='utf-8')


def call(root, tag, **env):
    e = dict((k, v) for k, v in os.environ.items() if not k.startswith('KYTY_') and k not in ('DRY', 'PLWAIT'))
    e.update(env)
    done = subprocess.run([BASH, str(root / 'go.sh'), tag], capture_output=True, text=True, env=e, timeout=60)
    return done.returncode, done.stdout.strip()


def line(tag, pl=540):
    return 'go142a call: PLWAIT=%d bash C:/kyty/s142/go142a.sh %s' % (pl, tag)


ok = True
ALL = [line(t) for t in S.SEQ]
r = fixture('g1')
ok &= case('g1 an unknown tag -> rc 2 usage', call(r, 'x142')[0] == 2 and call(r, 'x142')[1].startswith('usage'))
r = fixture('g2')
seal(r, ALL)
(r / 'STOP').write_text('p.999\n')
rc, out = call(r, 'v142', DRY='1')
ok &= case('g2 the stop file -> rc 4 before DRY', rc == 4 and 'stop file' in out and 'DRY' not in out)
r = fixture('g3')
seal(r, ALL)
(r / 'LOCKFILE').write_text('someone\n')
rc, out = call(r, 'v142', DRY='1')
ok &= case('g3 a held lock -> rc 4 before DRY', rc == 4 and 'lock held: someone' in out)
r = fixture('g4')
seal(r, ALL)
ok &= case('g4 PLWAIT not a number -> rc 2; PLWAIT 541 -> rc 2',
           call(r, 'v142', DRY='1', PLWAIT='x')[0] == 2 and call(r, 'v142', DRY='1', PLWAIT='541')[0] == 2)
r = fixture('g5')
seal(r, ALL)
(r / 'attempt_v142.txt').write_text('made\n')
rc, out = call(r, 'v142', DRY='1')
(r / 'attempt_v142.txt').unlink()
(r / 'v142.json').write_text('{}')
rc2, out2 = call(r, 'v142', DRY='1')
ok &= case('g5 one attempt: the marker or <tag>.json -> rc 1', rc == 1 and rc2 == 1 and 'attempt already made' in out + out2)
r = fixture('g6')
seal(r, ALL)
rc, out = call(r, 'w142', DRY='1')
(r / 'attempt_v142.txt').write_text('made\n')
rc2, out2 = call(r, 'w142', DRY='1')
rc3, out3 = call(r, 'c142_01', DRY='1')
(r / 'w142.json').write_text('{}')
rc4, out4 = call(r, 'c142_01', DRY='1')
rc5, out5 = call(r, 'c142_03', DRY='1')
ok &= case('g6 order: w142 before v142 -> rc 1; after the v142 marker -> DRY rc 0; c142_01 before w142 -> rc 1, after '
           'w142.json -> rc 0; c142_03 before c142_02 -> rc 1', rc == 1 and 'previous call not made' in out and rc2 == 0
           and rc3 == 1 and rc4 == 0 and rc5 == 1)
r = fixture('g7')
rc, out = call(r, 'v142', DRY='1')
seal(r, [line('v142', 0)])
rc2, out2 = call(r, 'v142', DRY='1')
seal(r, [line('v142'), line('v142')])
rc3, out3 = call(r, 'v142', DRY='1')
seal(r, [line('v142') + ' ', line('w142')])
rc4, out4 = call(r, 'v142', DRY='1')
seal(r, [line('v142', 0)])
rc5, out5 = call(r, 'v142', DRY='1', PLWAIT='0')
ok &= case('g7 the seal call line: no seal, another PLWAIT, two lines, a trailing blank -> rc 1; PLWAIT=0 as sealed -> DRY rc 0',
           rc == 1 and rc2 == 1 and rc3 == 1 and rc4 == 1 and rc5 == 0 and 'PLWAIT differs from the seal' in out + out2 + out3)
r = fixture('g8')
seal(r, ALL)
plans = {}
for t in S.SEQ:
    rc, out = call(r, t, DRY='1')
    plans[t] = (rc, out)
    (r / ('attempt_%s.txt' % t)).write_text('made\n')     # the call is made: the next one may plan
rp = r.as_posix()
ok &= case('g8 DRY rc 0 for every tag once its previous call is made', all(v[0] == 0 for v in plans.values()))
common = all(('--attempts 1' in o and 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in o and '--no-install --require-idle' in o
              and '--gates-file %s/gates_default.txt' % rp in o and '--pred %s/pred/01_sc142.md' % rp in o
              and 'KYTY_GPU_CHECKPOINTS' not in o and 'KYTY_GATE_SCHEDULE' not in o) for _, o in plans.values())
ok &= case('g9 every plan: one attempt, clock pin, markers 0, the empty gate file, the seal, no checkpoints/schedule', common)
v = plans['v142'][1]
w = plans['w142'][1]
ok &= case('g10 v142: Sky Garden, video, hold 330, stable-draws 300, timeout 480, no validation',
           'level underwater_aerial_garden' in v and '--rec' in v and '--hold 330' in v and
           '--stable-draws 300 --timeout 480' in v and 'vulkan-validation' not in v)
ok &= case('g11 w142: Sky Garden, validation true with the layer path and the duplicate limit, hold 310, no video',
           'level underwater_aerial_garden' in w and '--emu-arg=--vulkan-validation --emu-arg=true' in w and
           'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000' in w and '--hold 310' in w
           and '--rec' not in w)
cen = all(('level %s' % S.level_of(t) in plans[t][1] and '--level %s ' % S.level_of(t) in plans[t][1] and '--rec' in plans[t][1]
           and '--hold 120' in plans[t][1] and '--stable-draws 100 --timeout 480' in plans[t][1]
           and 'vulkan-validation' not in plans[t][1]) for t, _ in S.CENSUS)
ok &= case('g12 every census tag: its level of item 221 (g)(1), video, hold 120, stable-draws 100, no validation', cen)
m = re.search(r'\nSEQ="([^"]*)"\n', TEXT)
ok &= case('g13 SEQ of the chain = sc142.SEQ', m is not None and tuple(m.group(1).split()) == S.SEQ)
lv = dict(re.findall(r'\n  (c142_\d\d)\) LEVEL=(\w+);;', TEXT))
ok &= case('g14 the chain tag -> level map = sc142.level_of for the ten census tags; V and W -> Sky Garden',
           lv == dict(S.CENSUS) and '\n  v142|w142) LEVEL=underwater_aerial_garden;;' in TEXT)
ok &= case('g15 constants: the installed build 9235a7ac and its pinned copy, the empty-file sha, s51_vidglitch.py of scripts',
           'BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"' in TEXT and
           'BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"' in TEXT and
           'GATESHA="%s"' % hashlib.sha256(b'').hexdigest() in TEXT and 'VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py' in TEXT
           and 'python $VIDGLITCH rec_$T.mp4 4 6 ' in TEXT)
ok &= case('g16 holds: V 330 >= 300, W 310 >= 300, census 120 >= 120', 'VHOLD="330"' in TEXT and 'WHOLD="310"' in TEXT
           and 'CHOLD="120"' in TEXT)
first_proc = min(TEXT.find(x) for x in ('\nguards ', '\npython ', '\nCPU=$(powershell', 'sha256sum') if TEXT.find(x) >= 0)
ok &= case('g17 the stop file and the lock are checked before any process', 0 < TEXT.find('\nif [ -e $STOPF ]; then')
           < TEXT.find('\nlockheld\n') < first_proc)
ok &= case('g18 the stop file is checked again right before the lock is taken',
           TEXT.find('if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi') <
           TEXT.find('set -o noclobber') and TEXT.count('if [ -e $STOPF ]') == 2)
ok &= case('g19 the stop rule: a census call refuses rc 5 on sc142.py --stop-check rc 5, before the lock',
           'python $ROOT/$SC --stop-check $T' in TEXT and 'exit 5' in TEXT and
           TEXT.find('--stop-check $T') < TEXT.find('set -o noclobber'))
ok &= case('g20 the lock log lines are UTC; every event line of step2/times.txt is written with date -u',
           'echo "lock taken $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log' in TEXT and
           'echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log' in TEXT and
           all('date -u' in l for l in TEXT.split('\n') if '>> $TIMES' in l) and TEXT.count('>> $TIMES') == 6)
ok &= case('g21 the seal check runs before the lock', TEXT.find('--check-seal') < TEXT.find('set -o noclobber'))
ok &= case('g22 the script is ASCII and LF only', all(ord(c) < 128 for c in TEXT) and '\r' not in TEXT)
ok &= case('g23 the word of the mutation harness is not a command of the chain (only its guard pattern)',
           all('mutlib' not in l or "-match 'mut_" in l for l in TEXT.split('\n')))
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
