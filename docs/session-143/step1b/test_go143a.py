"""Fixtures of the chain go143a.sh (session 143 step 0, HPP-297; ROADMAP s122 item 231 (i)(1)-(4), item 105 (v), general
rule 26, item 231 (z)(5)).  Port of test_go142a.py.  The script is copied into a fixture directory with its ROOT, LOCK, STOPF
and GAME lines replaced (each replacement must hit exactly one line), then run through bash for the refusals that stop before
any guard (usage, stop file, lock, PLWAIT, one attempt, order V then W per level, the seal's call line) and for DRY=1 plans
of every tag; plus static checks of the real script (constants, tag -> level = sc143 PAIRS, SEQ = sc143.SEQ, holds, the
stop rule for every call, the foreign-CPU row of debt D-4 inside the lock, the BUSY row with the procload name, ASCII, the
stop file and the lock before any process).  No game, no guard, no lock of the machine is touched.  The first output line
names the suite and the target by sha256; the output ends with ALL OK.
    python C:/kyty/s143/test_go143a.py [<go143a.sh under test>]
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'go143a.sh')
print('suite test_go143a.py sha256 %s target go143a.sh sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc143_for_chain', os.path.join(HERE, 'sc143.py'))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
BASH = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
FX = Path('C:/kyty/s143/fx_go143a')
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
    for old, new in (('ROOT=C:/kyty/s143\n', 'ROOT=%s\n' % root.as_posix()),
                     ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s/LOCKFILE\n' % root.as_posix()),
                     ('STOPF=/c/kyty/s143/STOP\n', 'STOPF=%s/STOP\n' % root.as_posix()),
                     ('GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"\n', 'GAME="%s/game.exe"\n' % root.as_posix())):
        assert t.count(old) == 1, old
        t = t.replace(old, new)
    (root / 'go.sh').write_bytes(t.encode('utf-8'))
    return root


def seal(root, lines):
    (root / 'pred' / '02_sc143.md').write_text('fixture seal\n' + ''.join(l + '\n' for l in lines), encoding='utf-8')


def call(root, tag, **env):
    e = dict((k, v) for k, v in os.environ.items() if not k.startswith('KYTY_') and k not in ('DRY', 'PLWAIT'))
    e.update(env)
    done = subprocess.run([BASH, str(root / 'go.sh'), tag], capture_output=True, text=True, env=e, timeout=60)
    return done.returncode, done.stdout.strip()


def line(tag, pl=540):
    return 'go143a call: PLWAIT=%d bash C:/kyty/s143/go143a.sh %s' % (pl, tag)


ok = True
ALL = [line(t) for t in S.SEQ]
r = fixture('g1')
ok &= case('g1 an unknown tag (and a tag of session 142) -> rc 2 usage', call(r, 'x143')[0] == 2 and
           call(r, 'x143')[1].startswith('usage') and call(r, 'v142')[0] == 2 and call(r, 'v143_11')[0] == 2)
r = fixture('g2')
seal(r, ALL)
(r / 'STOP').write_text('p.999\n')
rc, out = call(r, 'v143_01', DRY='1')
ok &= case('g2 the stop file -> rc 4 before DRY', rc == 4 and 'stop file' in out and 'DRY' not in out)
r = fixture('g3')
seal(r, ALL)
(r / 'LOCKFILE').write_text('someone\n')
rc, out = call(r, 'v143_01', DRY='1')
ok &= case('g3 a held lock -> rc 4 before DRY', rc == 4 and 'lock held: someone' in out)
r = fixture('g4')
seal(r, ALL)
ok &= case('g4 PLWAIT not a number -> rc 2; PLWAIT 541 -> rc 2',
           call(r, 'v143_01', DRY='1', PLWAIT='x')[0] == 2 and call(r, 'v143_01', DRY='1', PLWAIT='541')[0] == 2)
r = fixture('g5')
seal(r, ALL)
(r / 'attempt_v143_01.txt').write_text('made\n')
rc, out = call(r, 'v143_01', DRY='1')
(r / 'attempt_v143_01.txt').unlink()
(r / 'v143_01.json').write_text('{}')
rc2, out2 = call(r, 'v143_01', DRY='1')
ok &= case('g5 one attempt: the marker or <tag>.json -> rc 1', rc == 1 and rc2 == 1 and 'attempt already made' in out + out2)
r = fixture('g6')
seal(r, ALL)
rc, out = call(r, 'w143_01', DRY='1')
(r / 'attempt_v143_01.txt').write_text('made\n')
rc2, out2 = call(r, 'w143_01', DRY='1')
rc3, out3 = call(r, 'v143_02', DRY='1')
(r / 'w143_01.json').write_text('{}')
rc4, out4 = call(r, 'v143_02', DRY='1')
rc5, out5 = call(r, 'v143_03', DRY='1')
rc6, out6 = call(r, 'w143_02', DRY='1')
ok &= case('g6 order: w143_01 before v143_01 -> rc 1; after the v143_01 marker -> DRY rc 0; v143_02 before w143_01 -> rc 1, '
           'after w143_01.json -> rc 0; v143_03 before w143_02 -> rc 1; w143_02 before v143_02 -> rc 1',
           rc == 1 and 'previous call not made' in out and rc2 == 0 and rc3 == 1 and rc4 == 0 and rc5 == 1 and rc6 == 1)
r = fixture('g7')
rc, out = call(r, 'v143_01', DRY='1')
seal(r, [line('v143_01', 0)])
rc2, out2 = call(r, 'v143_01', DRY='1')
seal(r, [line('v143_01'), line('v143_01')])
rc3, out3 = call(r, 'v143_01', DRY='1')
seal(r, [line('v143_01') + ' ', line('w143_01')])
rc4, out4 = call(r, 'v143_01', DRY='1')
seal(r, [line('v143_01', 0)])
rc5, out5 = call(r, 'v143_01', DRY='1', PLWAIT='0')
seal(r, ['go142a call: PLWAIT=540 bash C:/kyty/s142/go142a.sh v143_01'])
rc6, out6 = call(r, 'v143_01', DRY='1')
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
ok &= case('g8 DRY rc 0 for every one of the 20 tags once its previous call is made', len(plans) == 20 and
           all(v[0] == 0 for v in plans.values()))
common = all(('--attempts 1' in o and 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in o and '--no-install --require-idle' in o
              and '--gates-file %s/gates_default.txt' % rp in o and '--pred %s/pred/02_sc143.md' % rp in o
              and 'KYTY_GPU_CHECKPOINTS' not in o and 'KYTY_GATE_SCHEDULE' not in o and 'sc143.py --stop-check %s;' % t in o
              and 'fgcpu143 --save' in o and 'fgcpu143 --since' in o) for t, (_, o) in plans.items())
ok &= case('g9 every plan: one attempt, clock pin, markers 0, the empty gate file, the seal 02_sc143, no checkpoints/schedule, '
           'the stop check of its tag, the foreign-CPU snapshot at the lock and its row at the end', common)
vv = all(('level %s;' % lv in plans[v][1] and '--level %s ' % lv in plans[v][1] and '--rec' in plans[v][1]
          and '--hold 330' in plans[v][1] and '--stable-draws 300 --timeout 480' in plans[v][1]
          and 'vulkan-validation' not in plans[v][1] and 'VK_LAYER_PATH' not in plans[v][1]) for v, _, lv in S.PAIRS)
ok &= case('g10 every V: its level of item 231 (i)(1), video, hold 330, stable-draws 300, timeout 480, no validation', vv)
ww = all(('level %s;' % lv in plans[w][1] and '--level %s ' % lv in plans[w][1] and '--rec' not in plans[w][1]
          and '--emu-arg=--vulkan-validation --emu-arg=true' in plans[w][1] and '--hold 310' in plans[w][1]
          and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000' in plans[w][1]
          and '--stable-draws 300 --timeout 600' in plans[w][1]) for _, w, lv in S.PAIRS)
ok &= case('g11 every W: the level of its V, validation true with the layer path and the duplicate limit, hold 310, '
           'stable-draws 300, timeout 600, no video', ww)
m = re.search(r'\nSEQ="([^"]*)"\n', TEXT)
ok &= case('g13 SEQ of the chain = sc143.SEQ (V then W per level, item 231 (i)(1) order)', m is not None and
           tuple(m.group(1).split()) == S.SEQ)
lv = re.findall(r'\n  (v143_\d\d)\|(w143_\d\d)\) LEVEL=(\w+);;', TEXT)
ok &= case('g14 the chain tag -> level map = sc143.PAIRS (ten pairs)', tuple(lv) == S.PAIRS)
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
ok &= case('g19 the stop rule: EVERY call (V and W) refuses rc 5 on sc143.py --stop-check rc 5, before the lock',
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
ok &= case('g25 the chain reads the seal pred/02_sc143.md and the scorer sc143.py', 'PRED="pred/02_sc143.md"' in TEXT
           and 'SC="sc143.py"' in TEXT and 'sc142' not in TEXT and '02_sc142' not in TEXT)
fin = TEXT[TEXT.find('\nfinish() {'):TEXT.find('\ntrap finish EXIT\n')]
ok &= case('g26 debt D-4 (item 231 (i)(4)): the snapshot fgcpu143.py --save is taken after the lock and the EXIT trap and '
           'before the install; the trap writes the foreign-CPU row (--since, date -u) into step2/times.txt after the '
           'restore and BEFORE the lock is removed',
           TEXT.find('echo "lock taken $T') < TEXT.find('\ntrap finish EXIT\n') <
           TEXT.find('\npython $ROOT/fgcpu143.py --save $OUT/fgcpu_$T.a.json >> $L 2>&1\n') < TEXT.find('\nINSTALLED=1\n')
           and fin.find('if restore; then') < fin.find('fgcpu143.py --since $OUT/fgcpu_$T.a.json') <
           fin.find('foreign cpu at the end inside the lock: $FG" >> $TIMES') < fin.find('rm -f $LOCK') and
           'echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T foreign cpu at the end inside the lock: $FG" >> $TIMES' in fin)
ok &= case('g27 item 231 (z)(5): a procload refusal writes a BUSY row of step2/times.txt whose process name comes from the '
           'last "procload: busy" line of go143a.log, read by the same command',
           "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | "
           "cut -c1-300)\" >> $TIMES" in TEXT and 'busyname "procload --wait-s $1"; return 1;' in TEXT and
           TEXT.find('python $ROOT/procload.py --wait-s "$1" >> $L 2>&1') < TEXT.find('busyname "procload --wait-s $1"'))
ok &= case('g28 the name guard pattern watches the mutants and fixtures of 143 and the emulator',
           "'mut_[a-z0-9_]*143|test_[a-z0-9_]*143|mutlib'" in TEXT and "\\$_.Name -eq 'kyty_emulator.exe'" in TEXT)
ok &= case('g29 the levels of the chain are exactly sc143.LEVELS', [x[2] for x in lv] == list(S.LEVELS))
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
           TEXT.find("CMB=$(python $ROOT/cachemf143.py $OUT/cache_$T.before.json 2>&1 | tail -1 | tr -d '\\r')") <
           TEXT.find('go143a $T cache manifest before the lock: $CMB" >> $TIMES') < nc and
           TEXT.find('enter_scene end rc $RC') <
           TEXT.find("CMA=$(python $ROOT/cachemf143.py $OUT/cache_$T.after.json 2>&1 | tail -1 | tr -d '\\r')") <
           TEXT.find('go143a $T cache manifest after the run: $CMA" >> $TIMES') < TEXT.find('if [ "$RC" = "3" ]') and
           '"runs143/cache_$T.after.json"' in TEXT and 'cache_$T.before.json"' not in TEXT and
           TEXT.count('cachemf143.py $OUT/cache_$T.') == 2)
ok &= case('g32 the lock line carries the Windows pid of the shell (read by the builtin read from /proc/$$/winpid before any '
           'process); the foreign-CPU row gets --chain-pid $WINPID (item 242 (a), (d))',
           TEXT.find('\nWINPID=""\nread -r WINPID < /proc/$$/winpid 2>/dev/null\n') < first_proc and
           'echo "go143a.sh $T pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK' in TEXT and
           'fgcpu143.py --since $OUT/fgcpu_$T.a.json --chain-pid $WINPID 2>&1' in fin)
ok &= case('g33 every DRY plan names both manifests and the chain pid of the CPU row',
           all('cache manifest before (cachemf143); lock with winpid' in o and 'cache manifest after (cachemf143)' in o
               and 'fgcpu143 --since --chain-pid' in o for _, o in plans.values()))
r = fixture('g34')
seal(r, ALL)
(r / 'LOCKFILE').write_text('go143a.sh v143_01 pid 7 winpid 123 started x\n')
rc, out = call(r, 'v143_01', DRY='1')
ok &= case('g34 a held lock of the new form is printed whole in the BUSY line', rc == 4 and
           'lock held: go143a.sh v143_01 pid 7 winpid 123 started x' in out)
WR = dict((n, Path(HERE, 'step2', n).read_bytes().decode('utf-8')) for n in ('next_one.sh', 'call_one.sh', 'wait_one.sh'))
nx, cl, wt = WR['next_one.sh'], WR['call_one.sh'], WR['wait_one.sh']
ok &= case('g35 the step 2 wrappers (item 242 (d)): ASCII and LF; next_one checks the tag, the stop file and the lock before '
           'anything else, writes its call row, starts call_one detached (nohup ... & disown) and waits in the foreground '
           'with wait_one; call_one runs exactly the seal call "PLWAIT=540 bash C:/kyty/s143/go143a.sh $T" and writes the rc; '
           'wait_one waits at most 56 x 10 s = 560 s (< 600 s of a tool command)',
           all(all(ord(c) < 128 for c in x) and '\r' not in x for x in WR.values()) and
           nx.find('case "$T" in') < nx.find('[ -e C:/kyty/s143/STOP ]') < nx.find('[ -e C:/kyty/SEALED_RUN.lock ]') <
           nx.find('nohup bash C:/kyty/s143/step2/call_one.sh $T > /dev/null 2>&1 & disown') <
           nx.find('bash C:/kyty/s143/step2/wait_one.sh $T') and
           '\nPLWAIT=540 bash C:/kyty/s143/go143a.sh $T > step2/go_$T.out.txt 2>&1\nRC=$?\n' in cl and
           cl.count('go143a.sh') == 2 and 'for i in $(seq 1 56); do' in wt and 'sleep 10' in wt and
           'mutlib' not in nx + cl + wt and all(line(t).split('call: ')[1].replace(t, '$T') in cl for t in S.SEQ))
e = dict((k, v) for k, v in os.environ.items() if not k.startswith('KYTY_'))
done = subprocess.run([BASH, str(Path(HERE, 'step2', 'next_one.sh')), 'x143'], capture_output=True, text=True, env=e,
                      timeout=60)
ok &= case('g36 next_one.sh refuses an unknown tag rc 2 before the stop file, the lock or any call',
           done.returncode == 2 and done.stdout.startswith('usage'))
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
