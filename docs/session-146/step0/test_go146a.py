"""Fixtures of the chain go146a.sh (session 146 step 0, HPP-386; ROADMAP s122 item 309 (k), (l)(1)-(7), item 300 (b)(4)).
Port of C:/kyty/s146/test_go146a.py (names moved 145 -> 146; the order of the 35 tags, the W form without
KYTY_PIPELINE_PRECACHE, the levels, the build dac02fb9 and its pinned copy, the BUSY row with <app>, the bad tags - g1, g5, g6,
g8, g10, g11, g14, g15, g20, g27, g29, g38, g46, g47, g49 changed; g51-g55 new: the skip of item 309 (k)(1), the tiles row,
D-9 of next_one.sh).
Session 145 text (carried): Fixtures of the chain go146a.sh (session 145 step 0, HPP-350; ROADMAP s122 item 273 (k)(1)-(4), item 105 (v), general
rule 26, item 231 (z)(5)).  Port of C:/kyty/s144/test_go144a.py (names moved 144 -> 145; the order of the 34 tags (the control
W, the W repeat w145_01, then V then W per level), the W form of item 273 (k)(2), the levels of the control W, of the W
repeat and of the pairs, the bad tags and the step 2 wrappers with the gate are the cases changed or added - g1, g6, g8,
g10, g11, g14, g38, g46-g50).  Link 1b (HPP-379, item 295 (b)): the W form without the message filter and with the
duplicate limit 100000000, the seal pred/01_sc146.md - g9, g11, g25, g46, g47 changed.
Session 144 text (carried): port of C:/kyty/s143/test_go143a.py (names moved 143 -> 144; the order, the 33 tags, the W form
KYTY_PIPELINE_PRECACHE=0 of item 254 (e), the levels of the control W and of the pairs, the API check row of the step 2
wrapper and step2/apichk146.py are the cases changed or added - g1, g6, g8, g10, g11, g13, g14, g16, g29, g35, g37-g45).
Session 143 text (carried): port of test_go142a.py.  The script is copied into a fixture directory with its ROOT, LOCK, STOPF
and GAME lines replaced (each replacement must hit exactly one line), then run through bash for the refusals that stop before
any guard (usage, stop file, lock, PLWAIT, one attempt, order V then W per level, the seal's call line) and for DRY=1 plans
of every tag; plus static checks of the real script (constants, tag -> level = sc146 PAIRS, SEQ = sc146.SEQ, holds, the
stop rule for every call, the foreign-CPU row of debt D-4 inside the lock, the BUSY row with the procload name, ASCII, the
stop file and the lock before any process).  No game, no guard, no lock of the machine is touched.  The first output line
names the suite and the target by sha256; the output ends with ALL OK.
    python C:/kyty/s146/test_go146a.py [<go146a.sh under test>]
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'go146a.sh')
print('suite test_go146a.py sha256 %s target go146a.sh sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc146_for_chain', os.path.join(HERE, 'sc146.py'))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
BASH = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
FX = Path('C:/kyty/s146/fx_go146a')
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
    for old, new in (('ROOT=C:/kyty/s146\n', 'ROOT=%s\n' % root.as_posix()),
                     ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s/LOCKFILE\n' % root.as_posix()),
                     ('STOPF=/c/kyty/s146/STOP\n', 'STOPF=%s/STOP\n' % root.as_posix()),
                     ('GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"\n', 'GAME="%s/game.exe"\n' % root.as_posix())):
        assert t.count(old) == 1, old
        t = t.replace(old, new)
    (root / 'go.sh').write_bytes(t.encode('utf-8'))
    return root


def seal(root, lines):
    (root / 'pred' / '01_sc146.md').write_text('fixture seal\n' + ''.join(l + '\n' for l in lines), encoding='utf-8')


def call(root, tag, **env):
    e = dict((k, v) for k, v in os.environ.items() if not k.startswith('KYTY_') and k not in ('DRY', 'PLWAIT'))
    e.update(env)
    done = subprocess.run([BASH, str(root / 'go.sh'), tag], capture_output=True, text=True, env=e, timeout=60)
    return done.returncode, done.stdout.strip()


def line(tag, pl=540):
    return 'go146a call: PLWAIT=%d bash C:/kyty/s146/go146a.sh %s' % (pl, tag)


ok = True
ALL = [line(t) for t in S.SEQ]
r = fixture('g1')
ok &= case('g1 an unknown tag (a tag of session 142-145, a V of the control, a W of a re-check, a tag past 19, the warm-up '
           'i146_v) -> rc 2 usage',
           call(r, 'x146')[0] == 2 and call(r, 'x146')[1].startswith('usage') and call(r, 'v142')[0] == 2 and
           call(r, 'v143_01')[0] == 2 and call(r, 'v144_09')[0] == 2 and call(r, 'w145_17')[0] == 2 and
           call(r, 'v146_00')[0] == 2 and call(r, 'w146_01')[0] == 2 and call(r, 'v146_04')[0] == 2 and
           call(r, 'w146_20')[0] == 2 and call(r, 'v146_20')[0] == 2 and call(r, 'r146_05')[0] == 2 and
           call(r, 'i146_v')[0] == 2)
r = fixture('g2')
seal(r, ALL)
(r / 'STOP').write_text('p.999\n')
rc, out = call(r, 'w146_00', DRY='1')
ok &= case('g2 the stop file -> rc 4 before DRY', rc == 4 and 'stop file' in out and 'DRY' not in out)
r = fixture('g3')
seal(r, ALL)
(r / 'LOCKFILE').write_text('someone\n')
rc, out = call(r, 'w146_00', DRY='1')
ok &= case('g3 a held lock -> rc 4 before DRY', rc == 4 and 'lock held: someone' in out)
r = fixture('g4')
seal(r, ALL)
ok &= case('g4 PLWAIT not a number -> rc 2; PLWAIT 541 -> rc 2',
           call(r, 'w146_00', DRY='1', PLWAIT='x')[0] == 2 and call(r, 'w146_00', DRY='1', PLWAIT='541')[0] == 2)
r = fixture('g5')
seal(r, ALL)
(r / 'attempt_w146_00.txt').write_text('made\n')
rc, out = call(r, 'w146_00', DRY='1')
(r / 'attempt_w146_00.txt').unlink()
(r / 'w146_00.json').write_text('{}')
rc2, out2 = call(r, 'w146_00', DRY='1')
(r / 'w146_00.json').unlink()
(r / 'skipped_w146_00.txt').write_text('SKIPPED_V_NOT_ENTERED x\n')
rc3, out3 = call(r, 'w146_00', DRY='1')
ok &= case('g5 one call: the marker, <tag>.json or the skipped marker of item 309 (k)(1) -> rc 1',
           rc == 1 and rc2 == 1 and rc3 == 1 and 'attempt already made' in out + out2 + out3)
r = fixture('g6')
seal(r, ALL)
rc, out = call(r, 'r146_01', DRY='1')
(r / 'attempt_w146_00.txt').write_text('made\n')
rc2, out2 = call(r, 'r146_01', DRY='1')
rc3, out3 = call(r, 'r146_02', DRY='1')
for x in ('r146_01', 'r146_02', 'r146_03'):
    (r / ('%s.json' % x)).write_text('{}')
rc4, out4 = call(r, 'v146_05', DRY='1')
(r / 'r146_04.json').write_text('{}')
rc4b, out4b = call(r, 'v146_05', DRY='1')
rc5, out5 = call(r, 'w146_05', DRY='1')
rc6, out6 = call(r, 'v146_06', DRY='1')
(r / 'attempt_v146_05.txt').write_text('made\n')
(r / 'skipped_w146_05.txt').write_text('SKIPPED_V_NOT_ENTERED x\n')
rc7, out7 = call(r, 'v146_06', DRY='1')
ok &= case('g6 order: r146_01 before w146_00 -> rc 1; after the w146_00 marker -> DRY rc 0; r146_02 before r146_01 -> rc 1; '
           'v146_05 before r146_04 -> rc 1, after it -> rc 0; w146_05 before v146_05 -> rc 1; v146_06 before w146_05 -> rc 1; '
           'after the skipped marker of w146_05 (item 309 (k)(1)) -> rc 0',
           rc == 1 and 'previous call not made' in out and rc2 == 0 and rc3 == 1 and rc4 == 1 and rc4b == 0 and rc5 == 1
           and rc6 == 1 and rc7 == 0)
r = fixture('g7')
rc, out = call(r, 'w146_00', DRY='1')
seal(r, [line('w146_00', 0)])
rc2, out2 = call(r, 'w146_00', DRY='1')
seal(r, [line('w146_00'), line('w146_00')])
rc3, out3 = call(r, 'w146_00', DRY='1')
seal(r, [line('w146_00') + ' ', line('r146_01')])
rc4, out4 = call(r, 'w146_00', DRY='1')
seal(r, [line('w146_00', 0)])
rc5, out5 = call(r, 'w146_00', DRY='1', PLWAIT='0')
seal(r, ['go142a call: PLWAIT=540 bash C:/kyty/s142/go142a.sh w146_00'])
rc6, out6 = call(r, 'w146_00', DRY='1')
ok &= case('g7 the seal call line: no seal, another PLWAIT, two lines, a trailing blank, a go142a line -> rc 1; PLWAIT=0 as '
           'sealed -> DRY rc 0', rc == 1 and rc2 == 1 and rc3 == 1 and rc4 == 1 and rc5 == 0 and rc6 == 1
           and 'PLWAIT differs from the seal' in out + out2 + out3)
r = fixture('g8')
seal(r, ALL)
plans = {}
for t in S.SEQ:
    rc, out = call(r, t, DRY='1')
    plans[t] = (rc, out)
    (r / ('attempt_%s.txt' % t)).write_text('made\n')     # the call is made: the next one may plan
rp = r.as_posix()
ok &= case('g8 DRY rc 0 for every one of the 35 tags once its previous call is made', len(plans) == 35 and
           all(v[0] == 0 for v in plans.values()))
common = all(('--attempts 1' in o and 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in o and '--no-install --require-idle' in o
              and '--gates-file %s/gates_default.txt' % rp in o and '--pred %s/pred/01_sc146.md' % rp in o
              and 'KYTY_GPU_CHECKPOINTS' not in o and 'KYTY_GATE_SCHEDULE' not in o and 'sc146.py --stop-check %s;' % t in o
              and 'fgcpu146 --save' in o and 'fgcpu146 --since' in o) for t, (_, o) in plans.items())
ok &= case('g9 every plan: one attempt, clock pin, markers 0, the empty gate file, the seal 03_sc146, no checkpoints/schedule, '
           'the stop check of its tag, the foreign-CPU snapshot at the lock and its row at the end', common)
vv = all(('level %s;' % lv in plans[v][1] and '--level %s ' % lv in plans[v][1] and '--rec' in plans[v][1]
          and '--hold 330' in plans[v][1] and '--stable-draws 300 --timeout 480' in plans[v][1]
          and 'vulkan-validation' not in plans[v][1] and 'VK_LAYER_PATH' not in plans[v][1]
          and 'KYTY_PIPELINE_PRECACHE' not in plans[v][1] and 'VK_LAYER_MESSAGE_ID_FILTER' not in plans[v][1])
         for v, lv in [(x, S.level_of(x)) for x in S.V_TAGS])
ok &= case('g10 every V (the 4 re-check / second-hold V and the 15 of the census): its level of item 309 (l)(2), video, hold 330, '
           'stable-draws 300, timeout 480, no validation, no KYTY_PIPELINE_PRECACHE, no message filter (shipped defaults)',
           vv and len(S.V_TAGS) == 19 and len(S.CENSUS) == 15)
ww = all(('level %s;' % lv in plans[w][1] and '--level %s ' % lv in plans[w][1] and '--rec' not in plans[w][1]
          and '--emu-arg=--vulkan-validation --emu-arg=true' in plans[w][1] and '--hold 310' in plans[w][1]
          and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 '
              'KYTY_GPU_CLOCK_PIN=1' in plans[w][1] and 'VK_LAYER_MESSAGE_ID_FILTER' not in plans[w][1]
          and 'KYTY_PIPELINE_PRECACHE' not in plans[w][1]
          and '--stable-draws 300 --timeout 600' in plans[w][1]) for w, lv in [(x, S.level_of(x)) for x in S.W_TAGS])
ok &= case('g11 every W (the control and the 15 of the pairs): its level, validation true with the layer path and the '
           'duplicate limit 100000000 positional before the clock pin, precache by default (no KYTY_PIPELINE_PRECACHE, item 300 '
           '(b)(4)), no message filter (item 295 (b)), hold 310, stable-draws 300, timeout 600, no video',
           ww and len(S.W_TAGS) == 16)
m = re.search(r'\nSEQ="([^"]*)"\n', TEXT)
ok &= case('g13 SEQ of the chain = sc146.SEQ (the control W, the four V-only tags, then V then W per level, item 309 (l)(2))',
           m is not None and
           tuple(m.group(1).split()) == S.SEQ)
lv = re.findall(r'\n  (v146_\d\d)\|(w146_\d\d)\) LEVEL=(\w+);;', TEXT)
lw = re.findall(r'\n  ([wr]146_\d\d)\) LEVEL=(\w+);;', TEXT)
ok &= case('g14 the chain tag -> level map: the control W and the four V-only tags = sc146 (CONTROL, RECHECK), the fifteen V/W '
           'pairs = sc146.PAIRS', tuple(lv) == S.PAIRS and tuple(lw) == ((S.CONTROL[0], S.CONTROL[1]),) + tuple(S.RECHECK))
ok &= case('g15 constants: the installed build dac02fb9 and its pinned copy of step 0, the empty-file sha, s51_vidglitch.py',
           'BUILD_EXPECT="dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e"' in TEXT and
           'BUILD_PINNED="/c/kyty/s146/kyty_emulator_dac02fb9.exe"' in TEXT and
           'GATESHA="%s"' % hashlib.sha256(b'').hexdigest() in TEXT and 'VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py' in TEXT
           and 'python $VIDGLITCH rec_$T.mp4 4 6 ' in TEXT)
ok &= case('g16 holds: V 330 (as v142), W 310 (item 231 (i)(2)); no census hold of 120', 'VHOLD="330"' in TEXT and
           'WHOLD="310"' in TEXT and 'CHOLD' not in TEXT)
first_proc = min(TEXT.find(x) for x in ('\nguards ', '\npython ', '\nCPU=$(powershell', 'sha256sum', '\nmkdir ')
                 if TEXT.find(x) >= 0)
ok &= case('g17 the stop file and the lock are checked before any process', 0 < TEXT.find('\nif [ -e $STOPF ]; then')
           < TEXT.find('\nlockheld\n') < first_proc)
ok &= case('g18 the stop file is checked again right before the lock is taken',
           TEXT.find('if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi') <
           TEXT.find('set -o noclobber') and TEXT.count('if [ -e $STOPF ]') == 2)
ok &= case('g19 the stop rule: EVERY call (V and W) refuses rc 5 on sc146.py --stop-check rc 5, before the lock',
           '\npython $ROOT/$SC --stop-check $T >> $L 2>&1\n' in TEXT and 'exit 5' in TEXT and
           TEXT.find('--stop-check $T') < TEXT.find('set -o noclobber') and 'c142_*)' not in TEXT and
           TEXT.count('--stop-check $T') == 2)
ok &= case('g20 the lock log lines are UTC; every event line of step2/times.txt is written with date -u',
           'echo "lock taken $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log' in TEXT and
           'echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log' in TEXT and
           all('date -u' in l for l in TEXT.split('\n') if '>> $TIMES' in l) and TEXT.count('>> $TIMES') == 14)
ok &= case('g21 the seal check runs before the lock', TEXT.find('--check-seal') < TEXT.find('set -o noclobber'))
ok &= case('g22 the script is ASCII and LF only', all(ord(c) < 128 for c in TEXT) and '\r' not in TEXT)
ok &= case('g23 the word of the mutation harness is not a command of the chain (only its guard pattern)',
           all('mutlib' not in l or "-match 'mut_" in l for l in TEXT.split('\n')))
ok &= case('g24 item 224 (a)(10): the shader cache count goes into step2/times.txt before the lock and after the run',
           'CACHE="/c/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564"' in TEXT and
           TEXT.find('shader cache files before the lock $(cachen)') < TEXT.find('set -o noclobber') and
           TEXT.find('enter_scene end rc $RC') < TEXT.find('shader cache files after the run $(cachen)')
           < TEXT.find('if [ "$RC" = "3" ]'))
ok &= case('g25 the chain reads the seal pred/01_sc146.md and the scorer sc146.py', 'PRED="pred/01_sc146.md"' in TEXT
           and 'SC="sc146.py"' in TEXT and 'sc142' not in TEXT and '02_sc142' not in TEXT)
fin = TEXT[TEXT.find('\nfinish() {'):TEXT.find('\ntrap finish EXIT\n')]
ok &= case('g26 debt D-4 (item 231 (i)(4)): the snapshot fgcpu146.py --save is taken after the lock and the EXIT trap and '
           'before the install; the trap writes the foreign-CPU row (--since, date -u) into step2/times.txt after the '
           'restore and BEFORE the lock is removed',
           TEXT.find('echo "lock taken $T') < TEXT.find('\ntrap finish EXIT\n') <
           TEXT.find('\npython $ROOT/fgcpu146.py --save $OUT/fgcpu_$T.a.json >> $L 2>&1\n') < TEXT.find('\nINSTALLED=1\n')
           and fin.find('if restore; then') < fin.find('fgcpu146.py --since $OUT/fgcpu_$T.a.json') <
           fin.find('foreign cpu at the end inside the lock: $FG" >> $TIMES') < fin.find('rm -f $LOCK') and
           'echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go146a $T foreign cpu at the end inside the lock: $FG" >> $TIMES' in fin)
ok &= case('g27 item 231 (z)(5) and "Process" 5 of s145: a procload refusal writes a BUSY row of step2/times.txt from the last '
           '"procload: busy" line of go146a.log with every process name replaced by <app> (sed), read by the same command',
           "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) go146a $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | "
           "sed -E \"s/\\('[^']*'/('<app>'/g\" | cut -c1-300)\" >> $TIMES" in TEXT and 'busyname "procload --wait-s $1"; return 1;' in TEXT and
           TEXT.find('python $ROOT/procload.py --wait-s "$1" >> $L 2>&1') < TEXT.find('busyname "procload --wait-s $1"'))
ok &= case('g28 the name guard pattern watches the mutants and fixtures of 146 and the emulator',
           "'mut_[a-z0-9_]*146|test_[a-z0-9_]*146|mutlib'" in TEXT and "\\$_.Name -eq 'kyty_emulator.exe'" in TEXT)
ok &= case('g29 the levels of the chain are exactly the control level, the RECHECK levels and sc146.LEVELS',
           [x[1] for x in lw] + [x[2] for x in lv] == [S.SKY] + [x[1] for x in S.RECHECK] + list(S.LEVELS))
ok &= case('g30 no times.txt row prints "rc $?" after a $(date ...) substitution (it would print the rc of date): the rc of '
           's51_vidglitch.py and sheet142.py is captured on the next line (GRC, SHRC) and printed',
           not any('rc $?' in l for l in TEXT.split('\n') if '$(date' in l) and
           'rec_$T.mp4 4 6 $ROOT/vidframes_$T > glitch_$T.txt 2>&1\n    GRC=$?\n' in TEXT and ' s51_vidglitch rc $GRC ' in TEXT
           and 'sheet_$T.png > sheet_$T.txt 2>&1\n    SHRC=$?\n' in TEXT and ' sheet rc $SHRC ' in TEXT)
nc = TEXT.find('set -o noclobber')
ok &= case('g31 item 242 (b): the cache manifest before the lock (after the shader cache count, before noclobber) and after '
           'the run (after the enter_scene end row, before the idle-refusal branch), each with a date -u row of times.txt; '
           'the stale list moves an old after-manifest, never the fresh before-manifest',
           TEXT.find('shader cache files before the lock $(cachen)') <
           TEXT.find("CMB=$(python $ROOT/cachemf146.py $OUT/cache_$T.before.json 2>&1 | tail -1 | tr -d '\\r')") <
           TEXT.find('go146a $T cache manifest before the lock: $CMB" >> $TIMES') < nc and
           TEXT.find('enter_scene end rc $RC') <
           TEXT.find("CMA=$(python $ROOT/cachemf146.py $OUT/cache_$T.after.json 2>&1 | tail -1 | tr -d '\\r')") <
           TEXT.find('go146a $T cache manifest after the run: $CMA" >> $TIMES') < TEXT.find('if [ "$RC" = "3" ]') and
           '"runs146/cache_$T.after.json"' in TEXT and 'cache_$T.before.json"' not in TEXT and
           TEXT.count('cachemf146.py $OUT/cache_$T.') == 2)
ok &= case('g32 the lock line carries the Windows pid of the shell (read by the builtin read from /proc/$$/winpid before any '
           'process); the foreign-CPU row gets --chain-pid $WINPID (item 242 (a), (d))',
           TEXT.find('\nWINPID=""\nread -r WINPID < /proc/$$/winpid 2>/dev/null\n') < first_proc and
           'echo "go146a.sh $T pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK' in TEXT and
           'fgcpu146.py --since $OUT/fgcpu_$T.a.json --chain-pid $WINPID 2>&1' in fin)
ok &= case('g33 every DRY plan names both manifests and the chain pid of the CPU row',
           all('cache manifest before (cachemf146); lock with winpid' in o and 'cache manifest after (cachemf146)' in o
               and 'fgcpu146 --since --chain-pid' in o for _, o in plans.values()))
r = fixture('g34')
seal(r, ALL)
(r / 'LOCKFILE').write_text('go146a.sh w145_00 pid 7 winpid 123 started x\n')
rc, out = call(r, 'w146_00', DRY='1')
ok &= case('g34 a held lock of the new form is printed whole in the BUSY line', rc == 4 and
           'lock held: go146a.sh w145_00 pid 7 winpid 123 started x' in out)
WR = dict((n, Path(HERE, 'step2', n).read_bytes().decode('utf-8')) for n in ('next_one.sh', 'call_one.sh', 'wait_one.sh'))
nx, cl, wt = WR['next_one.sh'], WR['call_one.sh'], WR['wait_one.sh']
ok &= case('g35 the step 2 wrappers (item 242 (d)): ASCII and LF; next_one checks the tag, the stop file and the lock before '
           'anything else, writes its call row, starts call_one detached (nohup ... & disown) and waits in the foreground '
           'with wait_one; call_one runs exactly the seal call "PLWAIT=540 bash C:/kyty/s146/go146a.sh $T" and writes the rc; '
           'wait_one waits at most 56 x 10 s = 560 s (< 600 s of a tool command)',
           all(all(ord(c) < 128 for c in x) and '\r' not in x for x in WR.values()) and
           nx.find('case "$T" in') < nx.find('[ -e C:/kyty/s146/STOP ]') < nx.find('[ -e C:/kyty/SEALED_RUN.lock ]') <
           nx.find('nohup bash C:/kyty/s146/step2/call_one.sh $T > /dev/null 2>&1 & disown') <
           nx.find('bash C:/kyty/s146/step2/wait_one.sh $T') and
           '\nPLWAIT=540 bash C:/kyty/s146/go146a.sh $T > step2/go_$T.out.txt 2>&1\nRC=$?\n' in cl and
           cl.count('go146a.sh') == 2 and 'for i in $(seq 1 56); do' in wt and 'sleep 10' in wt and
           'mutlib' not in nx + cl + wt and all(line(t).split('call: ')[1].replace(t, '$T') in cl for t in S.SEQ))
e = dict((k, v) for k, v in os.environ.items() if not k.startswith('KYTY_'))
done = subprocess.run([BASH, str(Path(HERE, 'step2', 'next_one.sh')), 'x145'], capture_output=True, text=True, env=e,
                      timeout=60)
ok &= case('g36 next_one.sh refuses an unknown tag rc 2 before the stop file, the lock or any call',
           done.returncode == 2 and done.stdout.startswith('usage'))
ok &= case('g37 next_one.sh (MINOR-4 of audit 143): the API check apichk146.py runs after the tag, the stop file and the lock '
           'and before the call row and the detached call; its NO GO exits rc 4 without a call; the call row says "api GO"',
           nx.find('[ -e C:/kyty/SEALED_RUN.lock ]') < nx.find('python C:/kyty/s146/step2/apichk146.py --tag $T') <
           nx.find('api GO; call: PLWAIT=540 bash C:/kyty/s146/go146a.sh $T" >> $TIMES') <
           nx.find('nohup bash C:/kyty/s146/step2/call_one.sh $T') and nx.count('apichk146.py --tag $T') == 2 and
           nx.count('|| { echo "api check NO GO before $T (row in times.txt)"; exit 4; }') == 2)
for bad in ('v146_04', 'w146_04', 'w146_20', 'r146_05', 'w146_01', 'v145_02', 'w145_00', 'i146_v'):
    done = subprocess.run([BASH, str(Path(HERE, 'step2', 'next_one.sh')), bad], capture_output=True, text=True, env=e,
                          timeout=60)
    ok &= case('g38 next_one.sh refuses %s rc 2 (no tag outside the 35 of the chain)' % bad,
               done.returncode == 2 and done.stdout.startswith('usage'))
_spa = importlib.util.spec_from_file_location('apichk_under_test', os.path.join(HERE, 'step2', 'apichk146.py'))
A = importlib.util.module_from_spec(_spa)
_spa.loader.exec_module(A)
ME = 'agent-me'
ISS = dict(id='i1', identifier='HPP-332', status='in_progress', executionRunId='run1')
C1 = dict(id='c1', authorAgentId=ME, createdAt='2026-10-01T06:00:00Z')
C2 = dict(id='c2', authorAgentId='lead', createdAt='2026-10-01T06:01:00Z')
C3 = dict(id='c3', authorUserId='user', createdAt='2026-10-01T06:02:00Z')
rc, row = A.judge('w145_00', ISS, [C1], None, ME)
ok &= case('g39 apichk: in progress, only own comments -> GO rc 0 with the issue, status, run, count and the last comment',
           rc == 0 and row == 'apichk146 w145_00 issue HPP-332 status in_progress executionRunId run1 comments 1 after start '
           'new-foreign 0 last c1 agent-me 2026-10-01T06:00:00Z -> GO')
rc, row = A.judge('w145_00', ISS, [C2, C1], None, ME)
rc2, row2 = A.judge('w145_00', ISS, [C2, C1], 'c2', ME)
rc3, row3 = A.judge('w145_00', ISS, [C1, C2, C3], 'c2', ME)
ok &= case('g40 apichk: an unread comment of another author -> NO GO rc 4 naming the id to pass; after it is read (--after c2) '
           '-> GO; a newer one of a user -> NO GO again (sorted by time, not by the order of the answer)',
           rc == 4 and 'NO GO (1 unread comment(s) of another author since start - read them, then call with --after c2)' in row
           and rc2 == 0 and row2.endswith('-> GO') and rc3 == 4 and '--after c3' in row3)
rc, row = A.judge('w145_00', dict(ISS, status='cancelled'), [], None, ME)
rc2, row2 = A.judge('w145_00', dict(ISS, status='done'), [], None, ME)
rc3, row3 = A.judge('w145_00', dict(ISS, status='blocked'), [], None, ME)
ok &= case('g41 apichk: the issue cancelled or done -> NO GO; blocked alone (a status, not the state of a run) -> GO',
           rc == 4 and 'issue cancelled' in row and rc2 == 4 and 'issue done' in row2 and rc3 == 0)
rc, row = A.judge('w145_00', None, None, None, ME)
rc2, row2 = A.judge('w145_00', ISS, None, None, ME)
rc3, row3 = A.judge('w145_00', ISS, [C1], 'cX', ME)
ok &= case('g42 apichk: no answer (issue or comments) -> NO GO; an --after id not among the comments -> NO GO',
           rc == 4 and rc2 == 4 and 'no answer' in row and rc3 == 4 and 'comment cX not found' in row3)
TM = FX / 'api_times.txt'
calls = []


def fake(url):
    calls.append(url)
    return dict(ISS) if not url.endswith('/comments') else [C1]


old_env = dict(os.environ)
os.environ.update(PAPERCLIP_API_URL='http://h:1/api', PAPERCLIP_API_KEY='k', PAPERCLIP_AGENT_ID=ME)
import contextlib as _cl
import io as _io
_b = _io.StringIO()
with _cl.redirect_stdout(_b):
    rm = A.main(['--tag', 'v145_09', '--issue', 'HPP-332'], fetch=fake, times=str(TM))


def boom(url):
    raise OSError('down')


with _cl.redirect_stdout(_b):
    rm2 = A.main(['--tag', 'v145_09', '--issue', 'HPP-332'], fetch=boom, times=str(TM))
os.environ.clear()
os.environ.update(old_env)
tl = TM.read_text(encoding='ascii').split('\n')
ok &= case('g43 apichk main: two GETs (issue, comments) on the base without /api doubled; one UTC row per call appended to '
           'the times file; a failing GET -> rc 4 and a "no answer" row',
           rm == 0 and calls == ['http://h:1/api/issues/HPP-332', 'http://h:1/api/issues/HPP-332/comments'] and
           re.match(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ apichk146 v145_09 issue HPP-332 status in_progress ', tl[0]) is not None
           and rm2 == 4 and 'no answer' in tl[1] and len([x for x in tl if x]) == 2)
dr = FX / 'api_drv.py'
dr.write_text('import sys, importlib.util\n'
              's = importlib.util.spec_from_file_location("a", %r)\nA = importlib.util.module_from_spec(s)\n'
              's.loader.exec_module(A)\n'
              'def f(u):\n    return {"identifier": "HPP-332", "status": "in_progress"} if not u.endswith("/comments") else '
              '[{"id": "c9", "authorUserId": "u", "createdAt": "x", "body": "\\u0421\\u0442\\u043e\\u043f"}]\n'
              'sys.exit(A.main(["--tag", "w145_00", "--issue", "HPP-332"], fetch=f, times=%r))\n'
              % (os.path.join(HERE, 'step2', 'apichk146.py'), (FX / 'api_t2.txt').as_posix()), encoding='utf-8')
env2 = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
env2['PYTHONUTF8'] = '0'
pp = subprocess.run([sys.executable, str(dr)], capture_output=True, env=env2, timeout=60)
try:
    pp.stdout.decode('cp1250', errors='strict')
    encp = pp.returncode == 4 and b'apichk146 w145_00' in pp.stdout and not pp.stderr and \
        all(b < 128 for b in (FX / 'api_t2.txt').read_bytes())
except UnicodeError:
    encp = False
ok &= case('g44 apichk in a child without PYTHONIOENCODING (console cp1250): ASCII line and row, rc 4 on a foreign comment '
           'with a Cyrillic body (the body is never printed)', encp)
ATEXT = Path(HERE, 'step2', 'apichk146.py').read_bytes().decode('utf-8')
ok &= case('g45 apichk146.py is ASCII and LF, starts no process and is in the seal list of sc146',
           all(ord(c) < 128 for c in ATEXT) and '\r' not in ATEXT and 'subprocess' not in ATEXT.split(chr(34) * 3, 2)[2]
           and 'step2/apichk146.py' in S.SEALED_NAMES)
CODE = '\n'.join(x for x in TEXT.split('\n') if not x.lstrip().startswith('#'))
ok &= case('g46 the W form of item 295 (b): one constant VKDUP="100000000" used once, in the W EXTRA; no VKFILTER and no '
           'VK_LAYER_MESSAGE_ID_FILTER in the code lines (comments aside); no plan carries the filter; the scorer reads the '
           'form line "W form: limit=100000000 filter=none"',
           'VKDUP="100000000"\n' in CODE and CODE.count('$VKDUP') == 1 and 'VKFILTER' not in CODE and
           'VK_LAYER_MESSAGE_ID_FILTER' not in CODE and
           'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP";;\n' in CODE and 'KYTY_PIPELINE_PRECACHE' not in CODE.split('\nunset ')[1].split('\n', 1)[1] and
           not any('VK_LAYER_MESSAGE_ID_FILTER' in o for t, (_, o) in plans.items()) and
           all(o.count('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 ') == 1 for t, (_, o) in plans.items() if t in S.W_TAGS)
           and S.W_FORM_LINE == 'W form: limit=100000000 filter=none')
ok &= case('g47 the W EXTRA case is the w146_* branch, the V branch (v146_* and r146_*) has no EXTRA (shipped defaults)',
           0 < CODE.find('  w146_*) SD=') < CODE.find('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP') and
           0 < CODE.find('  v146_*|r146_*) SD=') < CODE.find('  w146_*) SD=') and
           'EXTRA=' not in CODE[CODE.find('  v146_*|r146_*) SD='):CODE.find('  w146_*) SD=')])
PR = Path(HERE, 'step2', 'pre_one.sh').read_bytes().decode('utf-8')
ok &= case('g48 pre_one.sh: ASCII and LF; the stop file and the lock first, then sc146.py --stop-check <tag> (its output and a '
           'times row with rc and sha), rc 5 on a stop, the lock again, then step2/gate146.py --before <tag>, rc 5 on its STOP',
           all(ord(c) < 128 for c in PR) and '\r' not in PR and
           PR.find('[ -e C:/kyty/s146/STOP ]') < PR.find('[ -e C:/kyty/SEALED_RUN.lock ]') <
           PR.find('python sc146.py --stop-check $T > step2/stopcheck_$T.txt 2>&1') <
           PR.find('pre_one sc146.py --stop-check $T rc $SRC') < PR.find('[ "$SRC" != "0" ] && exit 5') <
           PR.find('python step2/gate146.py --before $T || exit 5') and 'mutlib' not in PR and
           'sc144' not in PR and 'gate144' not in PR)
PATS = re.search(r'\n  ([^)]*)\) ;;\n', nx).group(1).split('|')
FM = __import__('fnmatch').fnmatchcase
ok &= case('g49 next_one.sh accepts exactly the 35 tags of the chain (its case pattern matches every SEQ tag and none of the bad '
           'tags)', all(any(FM(t, p) for p in PATS) for t in S.SEQ) and
           not any(FM(t, p) for t in ('v146_04', 'w146_04', 'w146_01', 'w146_20', 'v146_20', 'r146_05', 'r146_00', 'v145_02',
                                      'w146_1x', 'v146_00', 'i146_v') for p in PATS))
ok &= case('g50 the command lines of the wrappers name only session 146 (no 145 or 144 outside the comment lines); apichk146 '
           'writes the s146 times', all('145' not in l and '144' not in l for x in (nx, cl, wt) for l in x.split('\n')
                                       if not l.startswith('#')) and
           "TIMES = 'C:/kyty/s146/step2/times.txt'" in ATEXT and 'C:/kyty/s145' not in ATEXT)
sk0 = CODE.find('  w146_00) ;;\n  w146_*)\n    SKL=$(python $ROOT/$SC --skip-w $T 2>&1')
ok &= case('g51 item 309 (k)(1): the skip block runs after the stop-check and before the CPU check, the lock and any install; '
           'the control W is outside it; a W of a pair asks sc146.py --skip-w; SKIPPED_V_NOT_ENTERED writes skipped_<tag>.txt '
           'and a date -u row and exits rc 0; RUN goes on; any other answer refuses rc 1',
           CODE.find('python $ROOT/$SC --stop-check $T >> $L 2>&1') < sk0 < CODE.find('CPU=$(powershell') <
           CODE.find('set -o noclobber') and
           '        echo "$SKL $(date -u +%Y-%m-%dT%H:%M:%SZ)" > skipped_$T.txt\n' in CODE and
           'go146a $T SKIPPED_V_NOT_ENTERED (item 309 (k)(1); no lock, not an attempt): $SKL" >> $TIMES' in CODE and
           'log "go146a.sh $T skipped: $SKL"; echo "$SKL"; exit 0;;' in CODE and 'RUN*) log "go146a.sh $T runs: $SKL";;' in CODE
           and "*) log \"go146a.sh $T refused: --skip-w answered '$SKL'\"; echo \"skip-w failed\"; exit 1;;" in CODE)
ok &= case('g52 every DRY plan names the skip of a W of a pair', all('--skip-w' in o for _, o in plans.values()))
ok &= case('g53 the tiles row of item 309 (l)(4): after the sheet of a V video, tiles146.py writes tiles_<tag>.txt and its '
           'triples sheet; a date -u row with its rc (TLRC) and sha; the stale list moves old tiles files',
           CODE.find(' sheet rc $SHRC ') < CODE.find('python $ROOT/tiles146.py rec_$T.mp4 tiles_$T.txt --sheet tiles_$T.png') <
           CODE.find('    TLRC=$?\n') < CODE.find(' tiles rc $TLRC tiles_$T.txt sha256 $(sha tiles_$T.txt)') and
           '"tiles_$T.txt" "tiles_$T.png"' in CODE)
ok &= case('g54 D-9 (item 309 (i)): next_one.sh moves the previous output of the tag to step2/old/ (a date -u row) after the API '
           'check and before the call row; an output without its rc= line (a call still running) refuses rc 1 without a call',
           nx.find('apichk146.py --tag $T') < nx.find('GO=C:/kyty/s146/step2/go_$T.out.txt') <
           nx.find("grep -q '^rc=' $GO || {") < nx.find('mv $GO $NEWN') <
           nx.find('api GO; call: PLWAIT=540 bash C:/kyty/s146/go146a.sh $T') and
           'no new call"; exit 1; }' in nx and 'previous output of $T moved to step2/old/' in nx)
ok &= case('g55 the chain names the files of the seal: tiles146.py and lockcheck146.py in the files line; the W hold 310 and V '
           'hold 330 unchanged', 'tiles146.py $VIDGLITCH' in CODE and 'lockcheck146.py' in CODE and 'VHOLD="330"' in CODE and
           'WHOLD="310"' in CODE)
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
