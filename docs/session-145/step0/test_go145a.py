"""Fixtures of the chain go145a.sh (session 145 step 0, HPP-350; ROADMAP s122 item 273 (k)(1)-(4), item 105 (v), general
rule 26, item 231 (z)(5)).  Port of C:/kyty/s144/test_go144a.py (names moved 144 -> 145; the order of the 34 tags (the control
W, the W repeat w145_01, then V then W per level), the W form with the filter of one message of item 273 (k)(2), the levels
of the control W, of the W repeat and of the pairs, the bad tags and the step 2 wrappers with the gate are the cases changed
or added - g1, g6, g8, g10, g11, g14, g38, g46-g50).
Session 144 text (carried): port of C:/kyty/s143/test_go143a.py (names moved 143 -> 144; the order, the 33 tags, the W form
KYTY_PIPELINE_PRECACHE=0 of item 254 (e), the levels of the control W and of the pairs, the API check row of the step 2
wrapper and step2/apichk145.py are the cases changed or added - g1, g6, g8, g10, g11, g13, g14, g16, g29, g35, g37-g45).
Session 143 text (carried): port of test_go142a.py.  The script is copied into a fixture directory with its ROOT, LOCK, STOPF
and GAME lines replaced (each replacement must hit exactly one line), then run through bash for the refusals that stop before
any guard (usage, stop file, lock, PLWAIT, one attempt, order V then W per level, the seal's call line) and for DRY=1 plans
of every tag; plus static checks of the real script (constants, tag -> level = sc145 PAIRS, SEQ = sc145.SEQ, holds, the
stop rule for every call, the foreign-CPU row of debt D-4 inside the lock, the BUSY row with the procload name, ASCII, the
stop file and the lock before any process).  No game, no guard, no lock of the machine is touched.  The first output line
names the suite and the target by sha256; the output ends with ALL OK.
    python C:/kyty/s145/test_go145a.py [<go145a.sh under test>]
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'go145a.sh')
print('suite test_go145a.py sha256 %s target go145a.sh sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc145_for_chain', os.path.join(HERE, 'sc145.py'))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
BASH = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
FX = Path('C:/kyty/s145/fx_go145a')
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
    for old, new in (('ROOT=C:/kyty/s145\n', 'ROOT=%s\n' % root.as_posix()),
                     ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s/LOCKFILE\n' % root.as_posix()),
                     ('STOPF=/c/kyty/s145/STOP\n', 'STOPF=%s/STOP\n' % root.as_posix()),
                     ('GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"\n', 'GAME="%s/game.exe"\n' % root.as_posix())):
        assert t.count(old) == 1, old
        t = t.replace(old, new)
    (root / 'go.sh').write_bytes(t.encode('utf-8'))
    return root


def seal(root, lines):
    (root / 'pred' / '01_sc145.md').write_text('fixture seal\n' + ''.join(l + '\n' for l in lines), encoding='utf-8')


def call(root, tag, **env):
    e = dict((k, v) for k, v in os.environ.items() if not k.startswith('KYTY_') and k not in ('DRY', 'PLWAIT'))
    e.update(env)
    done = subprocess.run([BASH, str(root / 'go.sh'), tag], capture_output=True, text=True, env=e, timeout=60)
    return done.returncode, done.stdout.strip()


def line(tag, pl=540):
    return 'go145a call: PLWAIT=%d bash C:/kyty/s145/go145a.sh %s' % (pl, tag)


ok = True
ALL = [line(t) for t in S.SEQ]
r = fixture('g1')
ok &= case('g1 an unknown tag (a tag of session 142, 143 or 144 - the V v144_09 of the pair is no chain tag -, a V of the '
           'control or of the W repeat, a tag past 17) -> rc 2 usage',
           call(r, 'x145')[0] == 2 and call(r, 'x145')[1].startswith('usage') and call(r, 'v142')[0] == 2 and
           call(r, 'v143_01')[0] == 2 and call(r, 'v144_09')[0] == 2 and call(r, 'w144_00')[0] == 2 and
           call(r, 'v145_00')[0] == 2 and call(r, 'v145_01')[0] == 2 and call(r, 'w145_18')[0] == 2 and
           call(r, 'v145_18')[0] == 2)
r = fixture('g2')
seal(r, ALL)
(r / 'STOP').write_text('p.999\n')
rc, out = call(r, 'w145_00', DRY='1')
ok &= case('g2 the stop file -> rc 4 before DRY', rc == 4 and 'stop file' in out and 'DRY' not in out)
r = fixture('g3')
seal(r, ALL)
(r / 'LOCKFILE').write_text('someone\n')
rc, out = call(r, 'w145_00', DRY='1')
ok &= case('g3 a held lock -> rc 4 before DRY', rc == 4 and 'lock held: someone' in out)
r = fixture('g4')
seal(r, ALL)
ok &= case('g4 PLWAIT not a number -> rc 2; PLWAIT 541 -> rc 2',
           call(r, 'w145_00', DRY='1', PLWAIT='x')[0] == 2 and call(r, 'w145_00', DRY='1', PLWAIT='541')[0] == 2)
r = fixture('g5')
seal(r, ALL)
(r / 'attempt_w145_00.txt').write_text('made\n')
rc, out = call(r, 'w145_00', DRY='1')
(r / 'attempt_w145_00.txt').unlink()
(r / 'w145_00.json').write_text('{}')
rc2, out2 = call(r, 'w145_00', DRY='1')
ok &= case('g5 one attempt: the marker or <tag>.json -> rc 1', rc == 1 and rc2 == 1 and 'attempt already made' in out + out2)
r = fixture('g6')
seal(r, ALL)
rc, out = call(r, 'w145_01', DRY='1')
(r / 'attempt_w145_00.txt').write_text('made\n')
rc2, out2 = call(r, 'w145_01', DRY='1')
rc3, out3 = call(r, 'v145_02', DRY='1')
(r / 'w145_01.json').write_text('{}')
rc4, out4 = call(r, 'v145_02', DRY='1')
rc5, out5 = call(r, 'w145_02', DRY='1')
rc6, out6 = call(r, 'v145_03', DRY='1')
ok &= case('g6 order: w145_01 before w145_00 -> rc 1; after the w145_00 marker -> DRY rc 0; v145_02 before w145_01 -> rc 1, '
           'after w145_01.json -> rc 0; w145_02 before v145_02 -> rc 1; v145_03 before w145_02 -> rc 1',
           rc == 1 and 'previous call not made' in out and rc2 == 0 and rc3 == 1 and rc4 == 0 and rc5 == 1 and rc6 == 1)
r = fixture('g7')
rc, out = call(r, 'w145_00', DRY='1')
seal(r, [line('w145_00', 0)])
rc2, out2 = call(r, 'w145_00', DRY='1')
seal(r, [line('w145_00'), line('w145_00')])
rc3, out3 = call(r, 'w145_00', DRY='1')
seal(r, [line('w145_00') + ' ', line('w145_01')])
rc4, out4 = call(r, 'w145_00', DRY='1')
seal(r, [line('w145_00', 0)])
rc5, out5 = call(r, 'w145_00', DRY='1', PLWAIT='0')
seal(r, ['go142a call: PLWAIT=540 bash C:/kyty/s142/go142a.sh w145_00'])
rc6, out6 = call(r, 'w145_00', DRY='1')
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
ok &= case('g8 DRY rc 0 for every one of the 34 tags once its previous call is made', len(plans) == 34 and
           all(v[0] == 0 for v in plans.values()))
common = all(('--attempts 1' in o and 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in o and '--no-install --require-idle' in o
              and '--gates-file %s/gates_default.txt' % rp in o and '--pred %s/pred/01_sc145.md' % rp in o
              and 'KYTY_GPU_CHECKPOINTS' not in o and 'KYTY_GATE_SCHEDULE' not in o and 'sc145.py --stop-check %s;' % t in o
              and 'fgcpu145 --save' in o and 'fgcpu145 --since' in o) for t, (_, o) in plans.items())
ok &= case('g9 every plan: one attempt, clock pin, markers 0, the empty gate file, the seal 01_sc145, no checkpoints/schedule, '
           'the stop check of its tag, the foreign-CPU snapshot at the lock and its row at the end', common)
vv = all(('level %s;' % lv in plans[v][1] and '--level %s ' % lv in plans[v][1] and '--rec' in plans[v][1]
          and '--hold 330' in plans[v][1] and '--stable-draws 300 --timeout 480' in plans[v][1]
          and 'vulkan-validation' not in plans[v][1] and 'VK_LAYER_PATH' not in plans[v][1]
          and 'KYTY_PIPELINE_PRECACHE' not in plans[v][1] and 'VK_LAYER_MESSAGE_ID_FILTER' not in plans[v][1])
         for v, lv in S.CENSUS)
ok &= case('g10 every V (the 16 of the census): its level of item 273 (k)(1), video, hold 330, stable-draws 300, timeout 480, '
           'no validation, no KYTY_PIPELINE_PRECACHE, no message filter (shipped defaults)', vv and len(S.CENSUS) == 16)
ww = all(('level %s;' % lv in plans[w][1] and '--level %s ' % lv in plans[w][1] and '--rec' not in plans[w][1]
          and '--emu-arg=--vulkan-validation --emu-arg=true' in plans[w][1] and '--hold 310' in plans[w][1]
          and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000' in plans[w][1]
          and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000 KYTY_PIPELINE_PRECACHE=0 VK_LAYER_MESSAGE_ID_FILTER='
              'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering KYTY_GPU_CLOCK_PIN=1' in plans[w][1]
          and '--stable-draws 300 --timeout 600' in plans[w][1]) for w, lv in [(x, S.level_of(x)) for x in S.W_TAGS])
ok &= case('g11 every W (the control, the W repeat and the 16 of the pairs): its level, validation true with the layer path '
           'and the duplicate limit, the form KYTY_PIPELINE_PRECACHE=0 and the one message filter of item 273 (k)(2) positional '
           'before the clock pin, hold 310, stable-draws 300, timeout 600, no video', ww and len(S.W_TAGS) == 18)
m = re.search(r'\nSEQ="([^"]*)"\n', TEXT)
ok &= case('g13 SEQ of the chain = sc145.SEQ (the control W, the W repeat, then V then W per level, item 273 (k)(1))',
           m is not None and
           tuple(m.group(1).split()) == S.SEQ)
lv = re.findall(r'\n  (v145_\d\d)\|(w145_\d\d)\) LEVEL=(\w+);;', TEXT)
lw = re.findall(r'\n  (w145_\d\d)\) LEVEL=(\w+);;', TEXT)
ok &= case('g14 the chain tag -> level map: the control W and the W repeat = sc145 (CONTROL, the W of the v144_09 pair), the '
           'sixteen V/W pairs = sc145.PAIRS[1:]',
           tuple(lv) == S.PAIRS[1:] and tuple(lw) == ((S.CONTROL[0], S.CONTROL[1]),) + tuple((w, x) for _, w, x in S.PAIRS[:1]))
ok &= case('g15 constants: the installed build 9235a7ac and its pinned copy, the empty-file sha, s51_vidglitch.py of scripts',
           'BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"' in TEXT and
           'BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"' in TEXT and
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
ok &= case('g19 the stop rule: EVERY call (V and W) refuses rc 5 on sc145.py --stop-check rc 5, before the lock',
           '\npython $ROOT/$SC --stop-check $T >> $L 2>&1\n' in TEXT and 'exit 5' in TEXT and
           TEXT.find('--stop-check $T') < TEXT.find('set -o noclobber') and 'c142_*)' not in TEXT and
           TEXT.count('--stop-check $T') == 2)
ok &= case('g20 the lock log lines are UTC; every event line of step2/times.txt is written with date -u',
           'echo "lock taken $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log' in TEXT and
           'echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log' in TEXT and
           all('date -u' in l for l in TEXT.split('\n') if '>> $TIMES' in l) and TEXT.count('>> $TIMES') == 12)
ok &= case('g21 the seal check runs before the lock', TEXT.find('--check-seal') < TEXT.find('set -o noclobber'))
ok &= case('g22 the script is ASCII and LF only', all(ord(c) < 128 for c in TEXT) and '\r' not in TEXT)
ok &= case('g23 the word of the mutation harness is not a command of the chain (only its guard pattern)',
           all('mutlib' not in l or "-match 'mut_" in l for l in TEXT.split('\n')))
ok &= case('g24 item 224 (a)(10): the shader cache count goes into step2/times.txt before the lock and after the run',
           'CACHE="/c/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564"' in TEXT and
           TEXT.find('shader cache files before the lock $(cachen)') < TEXT.find('set -o noclobber') and
           TEXT.find('enter_scene end rc $RC') < TEXT.find('shader cache files after the run $(cachen)')
           < TEXT.find('if [ "$RC" = "3" ]'))
ok &= case('g25 the chain reads the seal pred/01_sc145.md and the scorer sc145.py', 'PRED="pred/01_sc145.md"' in TEXT
           and 'SC="sc145.py"' in TEXT and 'sc142' not in TEXT and '02_sc142' not in TEXT)
fin = TEXT[TEXT.find('\nfinish() {'):TEXT.find('\ntrap finish EXIT\n')]
ok &= case('g26 debt D-4 (item 231 (i)(4)): the snapshot fgcpu145.py --save is taken after the lock and the EXIT trap and '
           'before the install; the trap writes the foreign-CPU row (--since, date -u) into step2/times.txt after the '
           'restore and BEFORE the lock is removed',
           TEXT.find('echo "lock taken $T') < TEXT.find('\ntrap finish EXIT\n') <
           TEXT.find('\npython $ROOT/fgcpu145.py --save $OUT/fgcpu_$T.a.json >> $L 2>&1\n') < TEXT.find('\nINSTALLED=1\n')
           and fin.find('if restore; then') < fin.find('fgcpu145.py --since $OUT/fgcpu_$T.a.json') <
           fin.find('foreign cpu at the end inside the lock: $FG" >> $TIMES') < fin.find('rm -f $LOCK') and
           'echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T foreign cpu at the end inside the lock: $FG" >> $TIMES' in fin)
ok &= case('g27 item 231 (z)(5): a procload refusal writes a BUSY row of step2/times.txt whose process name comes from the '
           'last "procload: busy" line of go145a.log, read by the same command',
           "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | "
           "cut -c1-300)\" >> $TIMES" in TEXT and 'busyname "procload --wait-s $1"; return 1;' in TEXT and
           TEXT.find('python $ROOT/procload.py --wait-s "$1" >> $L 2>&1') < TEXT.find('busyname "procload --wait-s $1"'))
ok &= case('g28 the name guard pattern watches the mutants and fixtures of 145 and the emulator',
           "'mut_[a-z0-9_]*145|test_[a-z0-9_]*145|mutlib'" in TEXT and "\\$_.Name -eq 'kyty_emulator.exe'" in TEXT)
ok &= case('g29 the levels of the chain are exactly sc145.LEVELS after the control level',
           [x[1] for x in lw] + [x[2] for x in lv] == [S.SKY] + list(S.LEVELS))
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
           TEXT.find("CMB=$(python $ROOT/cachemf145.py $OUT/cache_$T.before.json 2>&1 | tail -1 | tr -d '\\r')") <
           TEXT.find('go145a $T cache manifest before the lock: $CMB" >> $TIMES') < nc and
           TEXT.find('enter_scene end rc $RC') <
           TEXT.find("CMA=$(python $ROOT/cachemf145.py $OUT/cache_$T.after.json 2>&1 | tail -1 | tr -d '\\r')") <
           TEXT.find('go145a $T cache manifest after the run: $CMA" >> $TIMES') < TEXT.find('if [ "$RC" = "3" ]') and
           '"runs145/cache_$T.after.json"' in TEXT and 'cache_$T.before.json"' not in TEXT and
           TEXT.count('cachemf145.py $OUT/cache_$T.') == 2)
ok &= case('g32 the lock line carries the Windows pid of the shell (read by the builtin read from /proc/$$/winpid before any '
           'process); the foreign-CPU row gets --chain-pid $WINPID (item 242 (a), (d))',
           TEXT.find('\nWINPID=""\nread -r WINPID < /proc/$$/winpid 2>/dev/null\n') < first_proc and
           'echo "go145a.sh $T pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK' in TEXT and
           'fgcpu145.py --since $OUT/fgcpu_$T.a.json --chain-pid $WINPID 2>&1' in fin)
ok &= case('g33 every DRY plan names both manifests and the chain pid of the CPU row',
           all('cache manifest before (cachemf145); lock with winpid' in o and 'cache manifest after (cachemf145)' in o
               and 'fgcpu145 --since --chain-pid' in o for _, o in plans.values()))
r = fixture('g34')
seal(r, ALL)
(r / 'LOCKFILE').write_text('go145a.sh w145_00 pid 7 winpid 123 started x\n')
rc, out = call(r, 'w145_00', DRY='1')
ok &= case('g34 a held lock of the new form is printed whole in the BUSY line', rc == 4 and
           'lock held: go145a.sh w145_00 pid 7 winpid 123 started x' in out)
WR = dict((n, Path(HERE, 'step2', n).read_bytes().decode('utf-8')) for n in ('next_one.sh', 'call_one.sh', 'wait_one.sh'))
nx, cl, wt = WR['next_one.sh'], WR['call_one.sh'], WR['wait_one.sh']
ok &= case('g35 the step 2 wrappers (item 242 (d)): ASCII and LF; next_one checks the tag, the stop file and the lock before '
           'anything else, writes its call row, starts call_one detached (nohup ... & disown) and waits in the foreground '
           'with wait_one; call_one runs exactly the seal call "PLWAIT=540 bash C:/kyty/s145/go145a.sh $T" and writes the rc; '
           'wait_one waits at most 56 x 10 s = 560 s (< 600 s of a tool command)',
           all(all(ord(c) < 128 for c in x) and '\r' not in x for x in WR.values()) and
           nx.find('case "$T" in') < nx.find('[ -e C:/kyty/s145/STOP ]') < nx.find('[ -e C:/kyty/SEALED_RUN.lock ]') <
           nx.find('nohup bash C:/kyty/s145/step2/call_one.sh $T > /dev/null 2>&1 & disown') <
           nx.find('bash C:/kyty/s145/step2/wait_one.sh $T') and
           '\nPLWAIT=540 bash C:/kyty/s145/go145a.sh $T > step2/go_$T.out.txt 2>&1\nRC=$?\n' in cl and
           cl.count('go145a.sh') == 2 and 'for i in $(seq 1 56); do' in wt and 'sleep 10' in wt and
           'mutlib' not in nx + cl + wt and all(line(t).split('call: ')[1].replace(t, '$T') in cl for t in S.SEQ))
e = dict((k, v) for k, v in os.environ.items() if not k.startswith('KYTY_'))
done = subprocess.run([BASH, str(Path(HERE, 'step2', 'next_one.sh')), 'x145'], capture_output=True, text=True, env=e,
                      timeout=60)
ok &= case('g36 next_one.sh refuses an unknown tag rc 2 before the stop file, the lock or any call',
           done.returncode == 2 and done.stdout.startswith('usage'))
ok &= case('g37 next_one.sh (MINOR-4 of audit 143): the API check apichk145.py runs after the tag, the stop file and the lock '
           'and before the call row and the detached call; its NO GO exits rc 4 without a call; the call row says "api GO"',
           nx.find('[ -e C:/kyty/SEALED_RUN.lock ]') < nx.find('python C:/kyty/s145/step2/apichk145.py --tag $T') <
           nx.find('api GO; call: PLWAIT=540 bash C:/kyty/s145/go145a.sh $T" >> $TIMES') <
           nx.find('nohup bash C:/kyty/s145/step2/call_one.sh $T') and nx.count('apichk145.py --tag $T') == 2 and
           nx.count('|| { echo "api check NO GO before $T (row in times.txt)"; exit 4; }') == 2)
for bad in ('v145_01', 'w145_18', 'v144_09', 'w144_09', 'v143_01', 'w143_01'):
    done = subprocess.run([BASH, str(Path(HERE, 'step2', 'next_one.sh')), bad], capture_output=True, text=True, env=e,
                          timeout=60)
    ok &= case('g38 next_one.sh refuses %s rc 2 (no V of the W repeat, no tag past 17, no tag of 144 or 143)' % bad,
               done.returncode == 2 and done.stdout.startswith('usage'))
_spa = importlib.util.spec_from_file_location('apichk_under_test', os.path.join(HERE, 'step2', 'apichk145.py'))
A = importlib.util.module_from_spec(_spa)
_spa.loader.exec_module(A)
ME = 'agent-me'
ISS = dict(id='i1', identifier='HPP-332', status='in_progress', executionRunId='run1')
C1 = dict(id='c1', authorAgentId=ME, createdAt='2026-10-01T06:00:00Z')
C2 = dict(id='c2', authorAgentId='lead', createdAt='2026-10-01T06:01:00Z')
C3 = dict(id='c3', authorUserId='user', createdAt='2026-10-01T06:02:00Z')
rc, row = A.judge('w145_00', ISS, [C1], None, ME)
ok &= case('g39 apichk: in progress, only own comments -> GO rc 0 with the issue, status, run, count and the last comment',
           rc == 0 and row == 'apichk145 w145_00 issue HPP-332 status in_progress executionRunId run1 comments 1 after start '
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
           re.match(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ apichk145 v145_09 issue HPP-332 status in_progress ', tl[0]) is not None
           and rm2 == 4 and 'no answer' in tl[1] and len([x for x in tl if x]) == 2)
dr = FX / 'api_drv.py'
dr.write_text('import sys, importlib.util\n'
              's = importlib.util.spec_from_file_location("a", %r)\nA = importlib.util.module_from_spec(s)\n'
              's.loader.exec_module(A)\n'
              'def f(u):\n    return {"identifier": "HPP-332", "status": "in_progress"} if not u.endswith("/comments") else '
              '[{"id": "c9", "authorUserId": "u", "createdAt": "x", "body": "\\u0421\\u0442\\u043e\\u043f"}]\n'
              'sys.exit(A.main(["--tag", "w145_00", "--issue", "HPP-332"], fetch=f, times=%r))\n'
              % (os.path.join(HERE, 'step2', 'apichk145.py'), (FX / 'api_t2.txt').as_posix()), encoding='utf-8')
env2 = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
env2['PYTHONUTF8'] = '0'
pp = subprocess.run([sys.executable, str(dr)], capture_output=True, env=env2, timeout=60)
try:
    pp.stdout.decode('cp1250', errors='strict')
    encp = pp.returncode == 4 and b'apichk145 w145_00' in pp.stdout and not pp.stderr and \
        all(b < 128 for b in (FX / 'api_t2.txt').read_bytes())
except UnicodeError:
    encp = False
ok &= case('g44 apichk in a child without PYTHONIOENCODING (console cp1250): ASCII line and row, rc 4 on a foreign comment '
           'with a Cyrillic body (the body is never printed)', encp)
ATEXT = Path(HERE, 'step2', 'apichk145.py').read_bytes().decode('utf-8')
ok &= case('g45 apichk145.py is ASCII and LF, starts no process and is in the seal list of sc145',
           all(ord(c) < 128 for c in ATEXT) and '\r' not in ATEXT and 'subprocess' not in ATEXT.split(chr(34) * 3, 2)[2]
           and 'step2/apichk145.py' in S.SEALED_NAMES)
VKF = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
CODE = '\n'.join(x for x in TEXT.split('\n') if not x.lstrip().startswith('#'))
ok &= case('g46 the filter of item 273 (k)(2): one constant VKFILTER = the VUID string of sc145.VKFILTER, used once, in the W '
           'EXTRA only; no other VK_LAYER_MESSAGE_ID_FILTER in the code lines (comments aside); no V plan carries it, every W '
           'plan exactly once',
           'VKFILTER="%s"\n' % VKF in CODE and S.VKFILTER == VKF and CODE.count('$VKFILTER') == 1 and
           CODE.count('VK_LAYER_MESSAGE_ID_FILTER=') == 1 and 'VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER";;\n' in CODE and
           all(o.count('VK_LAYER_MESSAGE_ID_FILTER=%s ' % VKF) == 1 for t, (_, o) in plans.items() if t in S.W_TAGS) and
           not any('VK_LAYER_MESSAGE_ID_FILTER' in o for t, (_, o) in plans.items() if t not in S.W_TAGS))
ok &= case('g47 the W EXTRA case is the w145_* branch, the V branch has no EXTRA (shipped defaults)',
           0 < CODE.find('  w145_*) SD=') < CODE.find('VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER') and
           0 < CODE.find('  v145_*) SD=') < CODE.find('  w145_*) SD=') and
           'EXTRA=' not in CODE[CODE.find('  v145_*) SD='):CODE.find('  w145_*) SD=')])
PR = Path(HERE, 'step2', 'pre_one.sh').read_bytes().decode('utf-8')
ok &= case('g48 pre_one.sh: ASCII and LF; the stop file and the lock first, then sc145.py --stop-check <tag> (its output and a '
           'times row with rc and sha), rc 5 on a stop, the lock again, then step2/gate145.py --before <tag>, rc 5 on its STOP',
           all(ord(c) < 128 for c in PR) and '\r' not in PR and
           PR.find('[ -e C:/kyty/s145/STOP ]') < PR.find('[ -e C:/kyty/SEALED_RUN.lock ]') <
           PR.find('python sc145.py --stop-check $T > step2/stopcheck_$T.txt 2>&1') <
           PR.find('pre_one sc145.py --stop-check $T rc $SRC') < PR.find('[ "$SRC" != "0" ] && exit 5') <
           PR.find('python step2/gate145.py --before $T || exit 5') and 'mutlib' not in PR and
           'sc144' not in PR and 'gate144' not in PR)
PATS = re.search(r'\n  ([^)]*)\) ;;\n', nx).group(1).split('|')
FM = __import__('fnmatch').fnmatchcase
ok &= case('g49 next_one.sh accepts exactly the 34 tags of the chain (its case pattern matches every SEQ tag and none of the bad '
           'tags)', all(any(FM(t, p) for p in PATS) for t in S.SEQ) and
           not any(FM(t, p) for t in ('v145_01', 'w145_18', 'v145_18', 'v144_09', 'w144_09', 'w145_1x', 'v145_00')
                   for p in PATS))
ok &= case('g50 the command lines of the wrappers name only session 145 (no 144 outside the comment lines); apichk145 writes '
           'the s145 times', all('144' not in l for x in (nx, cl, wt) for l in x.split('\n') if not l.startswith('#')) and
           "TIMES = 'C:/kyty/s145/step2/times.txt'" in ATEXT and 'C:/kyty/s144' not in ATEXT)
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
