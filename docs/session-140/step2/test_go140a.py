"""Offline fixtures of the session-140 game chain go140a.sh (step 2, HPP-268; port of the session-137 suite of this role onto
the tags of ROADMAP s122 items 210 (e)(3)-(4), 212 (i), 213 (d)): ONE build 05431dad for every tag (item 210 (e)(3)), the smoke
pm4s140 (KYTY_PM4_TRACE=1, hold 120) and the REGISTERED census as 4 calls pm4c140a..pm4c140d (KYTY_PM4_TRACE 0, 1, 1, 0, hold
300, item 210 (e)(4)) - every tag and every call one attempt; the 4 calls in order (a call refuses while the call before it was
not made); every tag on gates_base.txt itself with no KYTY_GATE_SCHEDULE (item 212 (i): the chain unsets the schedule of its
shell); item 76 (b) - the lock BEFORE any process in every call; the lock log runs140/lock.log with "lock taken|released <tag>
<UTC>" (audit 137, Process 1); item 105 (v) - the seal's PLWAIT on every pm4c140 call; item 93 (b) - protceil only 0; item 66
(a) one attempt; item 41 (a) exit codes; item 40 (e)(4) PLWAIT cap; item 40 (e)(6) the scorer's --out; the pre-seal check is
the scorer's --check-seal; item 175 (v), process 3 - the chain is ASCII only (c0a).  No game, no GPU, no nvidia-smi, no
powershell, no real build: the chain runs as a COPY whose ROOT, lock, game path, restore copy, name guard and CPU check point
into a fixture directory where procload.py, idle140.py, hostdev140.py, enter_scene.py, the CPU sampler and the scorer are
stubs that log their arguments and answer what the fixture wrote; envchk140.py is the real file copied in; gates_base.txt of
the fixture is the real gates_base.txt (its sha is the chain's BASESHA); the pinned build, the restore copy and the installed
emulator are small fixture files.  The lock edge is checked with a SPY: a PATH directory whose wrappers (python, sha256sum,
powershell, date, cat, cut, tr, grep, cp, mv, mkdir, rm, tail, head, sleep) log every external command before running the
real one - under the lock the spy log must stay EMPTY (no process), and the same spy on an unlocked call must log them (the
spy's positive control).  The real go140a.log, the real lock and the real installed emulator are never touched.  Run order
(cheap refusals before every full path - ROADMAP s122 items 112 (a), 123 (g)(1)): static, not configured, lock, the seal's
call, the order, hard refusals, busy, pre-seal, protceil, the full path of pm4c140a, the failures after the install, the full
paths of the other tags, untouched.
The first output line names the suite and the chain with their sha256 (item 150 (v), process 4).  Ends with ALL OK.

    python C:/kyty/s140/test_go140a.py [<go140a.sh under test>]
    FX140=<dir> overrides the fixture directory.
"""
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
CHAIN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'go140a.sh')
print('suite %s sha256 %s target %s sha256 %s' % (
    os.path.basename(__file__), hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(), os.path.basename(CHAIN),
    hashlib.sha256(pathlib.Path(CHAIN).read_bytes()).hexdigest()), flush=True)
BASE = pathlib.Path(os.environ.get('FX140') or 'C:/kyty/s140/fx_go140a')
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
REAL_LOCK = pathlib.Path('C:/kyty/SEALED_RUN.lock')
REAL_LOG = pathlib.Path(HERE, 'go140a.log')
REAL_GAME = pathlib.Path('C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe')
SHIPSHA = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
BSHA_REAL = '573ae9d2f24944c4fa92a14070645e3fe5b21bd6ee3365502e6ba768c0087fbc'   # C:/kyty/s136/gates_base.txt
BUILD = '05431dad252676b05128828a42169de0c1f84aff799838a513a0d80b32afcd84'     # item 210 (e)(3)
real_log_before = REAL_LOG.read_bytes() if REAL_LOG.exists() else None
real_lock_before = REAL_LOCK.exists()
real_game_stat = REAL_GAME.stat().st_mtime_ns if REAL_GAME.exists() else None

fails = []
count = [0]


def check(name, cond):
    count[0] += 1
    if not cond:
        fails.append(name)


def fsha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


sh = pathlib.Path(CHAIN).read_bytes()
chain_real = sh.decode('utf-8')
PINKEYS = ('BASESHA', 'BUILD_EXPECT', 'BUILD_PINNED', 'PRED', 'SC', 'SEQ')
PINVALS = {k: re.search(r'^%s="([^"]*)"$' % k, chain_real, re.M) for k in PINKEYS}
chain = re.sub(r'^(BUILD_EXPECT|BUILD_PINNED|PRED|SC)="[^"]*"$', r'\1=""', chain_real, flags=re.M)
code = [l for l in chain.splitlines() if l.strip() and not l.lstrip().startswith('#')]
text = '\n'.join(code)
PV = {k: (m.group(1) if m else None) for k, m in PINVALS.items()}
SMOKES = ('pm4s140',)
REGS = tuple('pm4c140' + c for c in 'abcd')
TAGS = SMOKES + REGS
GARDEN = 'underwater_aerial_garden'
TRACE = {'pm4s140': '1', 'pm4c140a': '0', 'pm4c140b': '1', 'pm4c140c': '1', 'pm4c140d': '0'}
HOLDS = {'pm4s140': 120, 'pm4c140a': 300, 'pm4c140b': 300, 'pm4c140c': 300, 'pm4c140d': 300}
BR = {'pm4s140': '    HOLD=$SHOLD; EXTRA="KYTY_PM4_TRACE=1";;',
      'pm4c140a': '    REG=1; HOLD=$PHOLD; EXTRA="KYTY_PM4_TRACE=0";;',
      'pm4c140b': '    REG=1; HOLD=$PHOLD; EXTRA="KYTY_PM4_TRACE=1";;',
      'pm4c140c': '    REG=1; HOLD=$PHOLD; EXTRA="KYTY_PM4_TRACE=1";;',
      'pm4c140d': '    REG=1; HOLD=$PHOLD; EXTRA="KYTY_PM4_TRACE=0";;'}
GB = pathlib.Path(HERE, 'gates_base.txt').read_bytes()
GBW = GB.decode('utf-8').split()
BSHA = hashlib.sha256(GB).hexdigest()
GB136 = pathlib.Path('C:/kyty/s136/gates_base.txt').read_bytes()
UTC = r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ'

# --- 1. static checks ------------------------------------------------------------------------------------------
check('c0 LF only', b'\r' not in sh)
bn = subprocess.run([shutil.which('bash') or 'bash', '-n', CHAIN], capture_output=True, text=True)
check('c1 bash -n', bn.returncode == 0)
check('c0a item 175 (v), process 3: the chain is ASCII only (every log and echo line)', all(c < 128 for c in sh))
check('c2 BASESHA is the sha of gates_base.txt here', PV['BASESHA'] == BSHA)
check('c2e item 210 (e)(3): BUILD_EXPECT is 05431dad (full sha) and BUILD_PINNED its pinned copy in s136 with that sha - '
      'the one build of every tag', PV['BUILD_EXPECT'] == BUILD
      and PV['BUILD_PINNED'] == '/c/kyty/s136/kyty_emulator_05431dad.exe'
      and fsha('C:/kyty/s136/kyty_emulator_05431dad.exe') == BUILD)
check('c2f no second build pair (no BUILD_EXPECT_/BUILD_PINNED_ suffix, no override line)',
      not re.search(r'BUILD_(EXPECT|PINNED)_', chain_real) and text.count('BUILD_EXPECT=') == 1
      and text.count('BUILD_PINNED=') == 1)


def seal_view():
    _sc = pathlib.Path(HERE, PV['SC'])
    _pr = pathlib.Path(HERE, PV['PRED'])
    if not _sc.is_file() or not _pr.is_file():
        return False
    _ps = re.search(r"^PRED_SHA = '([0-9a-f]{64})'", _sc.read_text(encoding='utf-8'), re.M)
    lines = [ln for ln in _pr.read_text(encoding='utf-8').split(chr(10))
             if re.fullmatch(r'go140a call: PLWAIT=[0-9]+ bash C:/kyty/s140/go140a\.sh [a-z0-9]+', ln)]
    return (_ps is not None and _ps.group(1) == fsha(_pr)
            and sorted(ln.rsplit(' ', 1)[1] for ln in lines) == sorted(REGS))


check('c2p the seal: PRED/SC both empty, or PRED = pred/01_pm4c140.md, SC = pm4c140.py with the scorer PRED_SHA = sha256 of '
      'PRED and exactly one call line for each of pm4c140a..pm4c140d (item 105 (v))',
      (PV['PRED'] == '' and PV['SC'] == '') or (
          PV['PRED'] == 'pred/01_pm4c140.md' and PV['SC'] == 'pm4c140.py' and seal_view()))
check('c2b the holds of items 210 (e)(4), (8): SHOLD 120 (pm4s140), PHOLD 300 (every pm4c140 call); no other hold constant',
      'SHOLD="120"' in code and 'PHOLD="300"' in code and not re.search(r'KHOLD|S1HOLD|VHOLD|OLDSHIFT|STOPF|CHK=', text))
check('c2q item 210 (e)(4): SEQ names the 4 calls pm4c140a..pm4c140d in order', PV['SEQ'] == ' '.join(REGS))
check('c3 THE INSTALLED BUILD: RESTORE = the pinned copy of 9235a7ac in s128 and its full sha',
      'RESTORE="/c/kyty/s128/kyty_emulator_9235a7ac.exe"' in code and ('RESTORE_SHA="%s"' % SHIPSHA) in code)
check('c3 the restore copy on disk has that sha', fsha('C:/kyty/s128/kyty_emulator_9235a7ac.exe') == SHIPSHA)
check('c4 gates_base.txt = the base of session 136 byte for byte (573ae9d2; item 210 (e)(3) the arm-0 knob string of kp137)',
      hashlib.sha256(GB136).hexdigest() == BSHA_REAL and GB == GB136 and BSHA == BSHA_REAL)
check('c4a item 210 (e)(3): the base names bindlean=0, rtskip=1, rbcen=1, rbslow=0, bindlap=1, pathlap=1, mutsite=1, '
      'plkstat=1, protceil=0 exactly once each',
      all([w for w in GBW if w.startswith(n + '=')] == [n + '=' + v] for n, v in
          (('bindlean', '0'), ('rtskip', '1'), ('rbcen', '1'), ('rbslow', '0'), ('bindlap', '1'), ('pathlap', '1'),
           ('mutsite', '1'), ('plkstat', '1'), ('protceil', '0'))))
check('c5 ROOT, log, lock, game, helpers, --out dir of session 140',
      'ROOT=C:/kyty/s140' in code and 'L=$ROOT/go140a.log' in code and 'LOCK=/c/kyty/SEALED_RUN.lock' in code
      and 'GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"' in code and 'PROCLOAD=$ROOT/procload.py' in code
      and 'IDLE=$ROOT/idle140.py' in code and 'HOSTDEV=$ROOT/hostdev140.py' in code
      and 'ENVCHK=$ROOT/envchk140.py' in code and 'BASEGATES=$ROOT/gates_base.txt' in code and 'OUT=$ROOT/runs140' in code)
check('c6 the tags: every tag on Sky Garden, one level line; the branch order pm4s140, pm4c140a..d',
      '  pm4s140|pm4c140a|pm4c140b|pm4c140c|pm4c140d) LEVEL=underwater_aerial_garden;;' in code and 'intro_next' not in text
      and [l.strip() for l in code if re.match(r'^\s+[a-z0-9|]+\)$', l)] == [t + ')' for t in TAGS])
check('c7 name guard pattern of s140 plus the emulator',
      "'mut_[a-z0-9]*140|test_[a-z0-9]*140|mutlib'" in text and "$_.Name -eq 'kyty_emulator.exe'" in text)
check('c8 no mutlib on a command line of the chain (only in the guard pattern)',
      all('mutlib' not in l or "-match 'mut_" in l for l in code))
check('c9 the busy exit is 4 and only there', text.count('exit 4') == 1 and 'busy() {' in text)
check('c10 never KYTY_GPU_CHECKPOINTS, KYTY_GPU_WALL, KYTY_REC, --rec; no own nvidia-smi; no KYTY_GATE_SCHEDULE passed',
      'KYTY_GPU_CHECKPOINTS' not in text and 'KYTY_REC' not in text and 'KYTY_GPU_WALL' not in text
      and '--rec"' not in text and 'nvidia-smi' not in text and 'utilization' not in text
      and 'KYTY_GATE_SCHEDULE=' not in text and not re.search(r'SCHED=|\$SCHED|ENVSCHED', text) and 'GSPEC' not in text)
check('c10b item 212 (i): the chain unsets KYTY_GATE_SCHEDULE and KYTY_GATE_SCHEDULE_ABBA right after the first lock check',
      'lockheld\nunset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA\n' in text)
check('c11 no session-137 name left in the code; s136 only in the pinned build path; s128 only in the restore path',
      not re.search(r'go13[0-9]a|idle13[0-9]|hostdev13[0-9]|envchk13[0-9]|runs13[0-9]|03ce7a92|kp137|s4cs|kk137|s6s137|'
                    r'bindlean|KNOB|rtskip=|protceil=1|bindlap=|pathlap=|rbcen', text)
      and [l for l in code if 's128' in l] == ['RESTORE="/c/kyty/s128/kyty_emulator_9235a7ac.exe"']
      and [l for l in chain_real.splitlines() if 's136' in l and not l.startswith('#')]
      == ['BUILD_PINNED="/c/kyty/s136/kyty_emulator_05431dad.exe"'])
run_i = [k for k, l in enumerate(code) if 'python $ROOT/enter_scene.py $T' in l]
run_line = (code[run_i[0]] + code[run_i[0] + 1]) if len(run_i) == 1 else ''
check('c12 the run: --attempts 1, --no-install --require-idle, the base gate file, the seal, the hold, EXTRA (the trace), pin, '
      'markers 0', '--no-install' in run_line and '--require-idle' in run_line and 'KYTY_GPU_CLOCK_PIN=1' in run_line
      and 'KYTY_GPU_MARKERS=0' in run_line and '--attempts 1 $SD' in run_line
      and '--gates-file $GATES $PREDARG' in run_line and '--hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1' in run_line)
check('c13 PLMAX 540, PLWAIT defaults to PLMAX', 'PLMAX=540' in code and 'PLWAIT=${PLWAIT:-$PLMAX}' in code)
check('c14 the scorer --out into runs140, hostdev unpadded, envchk --census --no-rec --base-is the base; the pre-seal check is '
      'the scorer --check-seal', 'python $ROOT/$SC --tag $T --out $OUT/$T.score.json > score_$T.txt 2>&1' in text
      and 'python $HOSTDEV $T --pad 0 > hostdev_$T.txt 2>&1' in text
      and 'python $ENVCHK $T.json $ENVX > envchk_$T.txt 2>&1' in text
      and 'ENVX="--census --no-rec --base-is $BASEGATES"' in text and 'python $ROOT/$SC --check-seal --tag $T' in text
      and 'vidglitch' not in text.lower())
check('c15 the EXIT trap restores and unlocks', 'trap finish EXIT' in code and 'finish() {' in text)
check('c15b the lock log: taken after the noclobber take, released after the lock is removed, UTC by date -u, into runs140',
      'echo "lock taken $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log' in text
      and '  rm -f $LOCK\n  echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log' in text
      and text.find('set +o noclobber\necho "lock taken') > text.find('busy "lock taken by someone else'))
first_lh = [k for k, l in enumerate(code) if l.strip() == 'lockheld']
head = '\n'.join(code[:first_lh[0]]) if first_lh else '$(python'
check('c16 item 76 (b): the first lockheld call comes before any command substitution or external command '
      '(only builtins before it: case, cd, function definitions)',
      bool(first_lh) and '$(' not in head and not re.search(r'\b(python|sha256sum|powershell|date|cat|grep|cp|mv|mkdir)\b',
                                                           head.replace('go140a.sh', '')))
check('c16b lockheld reads the lock with the builtin read (no cat, no $())',
      'read -r LOCKTXT < $LOCK 2>/dev/null' in text and 'busy "lock held: $LOCKTXT"' in text
      and "log() { printf '[%(%H:%M:%S)T] %s\\n' -1 \"$*\" >> $L; }" in text)
check('c16c lockheld before each later stage: 6 calls (first, before guards PLWAIT, after them, before CPU, before idle, '
      'before guards 0)', len(first_lh) == 6)


def branch(label):
    i = [k for k, l in enumerate(code) if l.strip() == label + ')']
    if len(i) != 1:
        return ''
    j = i[0] + 1
    while j < len(code) and not code[j].rstrip().endswith(';;'):
        j += 1
    return '\n'.join(code[i[0] + 1:j + 1])


for tag in TAGS:
    check('c17 the branch of %s verbatim (trace %s, hold %d)' % (tag, TRACE[tag], HOLDS[tag]), branch(tag) == BR[tag])
check('c18 REG (the seal) exactly on the pm4c140 branches; ONE (one attempt, item 66 (a)) is the default of every tag and no '
      'branch changes it', text.count('REG=1;') == 4 and all('REG=1;' in branch(t) for t in REGS)
      and 'REG' not in branch('pm4s140') and code.count('ONE=1') == 1 and 'ONE=0' not in text and code.count('REG=0') == 1)
C20 = [text.find(s) for s in ('\nlockheld\nunset KYTY_GATE_SCHEDULE', 'if [ -z "$BUILD_EXPECT" ] || [ -z "$BUILD_PINNED" ]; then',
                               'echo "not pinned yet"; exit 2',
                               'if ! [[ $BASESHA =~ ^[0-9a-f]{64}$ ]] || ! [[ $BUILD_EXPECT =~ ^[0-9a-f]{64}$ ]]; then',
                               'echo "bad EXPECT"; exit 2')]
check('c20 the refusals of the configuration: the build first ("not pinned yet"), then a non-hex BASESHA/EXPECT ("bad '
      'EXPECT") - each line present exactly as written, in this order', min(C20) >= 0 and C20 == sorted(C20))
PCBLOCK = ('PC=0\nGW=()\nif [ -f "$BASEGATES" ]; then IFS=$\' \\t\\r\\n\' read -r -d \'\' -a GW < "$BASEGATES"; fi\n'
           'for PWORD in "${GW[@]}"; do\n'
           '  case "$PWORD" in protceil=0) ;; protceil=*) PC=1;; esac\ndone\n'
           'if [ "$PC" = "1" ]; then\n'
           '  log "go140a.sh $T refused: protceil other than 0 in the base $BASEGATES (ROADMAP s122 item 93 (b))"\n'
           '  echo "protceil refused"; exit 1\nfi')
check('c21d item 93 (b): the protceil refusal block, exactly once, after the branches and before DRY',
      text.count(PCBLOCK) == 1 and text.find('    REG=1; HOLD=$PHOLD; EXTRA="KYTY_PM4_TRACE=0";;') < text.find(PCBLOCK)
      < text.find('if [ "${DRY:-0}" = "1" ]'))
ORDBLOCK = ('if [ "$REG" = "1" ]; then\n'
            '  PREV=""\n  P=""\n  for C in $SEQ; do\n    if [ "$C" = "$T" ]; then PREV=$P; fi\n    P=$C\n  done\n'
            '  if [ -n "$PREV" ] && [ ! -e "attempt_$PREV.txt" ] && [ ! -e "$PREV.json" ]; then\n'
            '    log "go140a.sh $T refused: the call $PREV before it was not made (ROADMAP s122 item 210 (e)(4): the 4 calls '
            'in order)"\n'
            '    echo "previous call not made"; exit 1\n  fi\nfi')
check('c21o item 210 (e)(4): the order block of the pm4c140 calls, exactly once, bash builtins only, after the one-attempt '
      'refusal and before the sha checks', text.count(ORDBLOCK) == 1
      and text.find('echo "attempt already made"; exit 1') < text.find(ORDBLOCK) < text.find('sha() {'))
ORDER = ('\nlockheld\nunset KYTY_GATE', 'if [ -z "$BUILD_EXPECT" ]', 'echo "protceil refused"; exit 1',
         'if [ "${DRY:-0}" = "1" ]', 'if [ "$REG" = "1" ] && { [ -z "$PRED" ]', 'SEALPL=$(grep -x', 'case "$HOLD" in',
         'if [ "$ONE" = "1" ] && { [ -e "$MARK" ]', 'for C in $SEQ; do',
         'if [ ! -f "$BUILD_PINNED" ]', 'if [ ! -f "$RESTORE" ]', 'if [ "$(sha "$BASEGATES")"',
         '\nlockheld\nguards $PLWAIT', 'guards $PLWAIT || busy ', 'NSHA=$(sha $PRED)',
         'python $ROOT/$SC --check-seal --tag $T', '\nlockheld\nCPU=$(powershell', '\nlockheld\npython $IDLE',
         '\nlockheld\nguards 0', 'mkdir -p $OUT\n', '> $LOCK; } 2>/dev/null', 'echo "lock taken', 'trap finish EXIT',
         'INSTALLED=1\n', 'cp "$BUILD_PINNED" "$GAME"', '> $MARK\n', 'python $ROOT/enter_scene.py',
         'python $HOSTDEV $T', 'python $ENVCHK $T.json', 'python $ROOT/$SC --tag $T')
order = [text.find(s) for s in ORDER]
check('c22 order: LOCK? unset -> config -> protceil refusal -> DRY -> seal -> PLWAIT of the seal -> hold -> attempt? -> previous '
      'call? -> pinned/restore/base sha -> lock? -> guards -> pred -> check-seal -> lock? cpu -> lock? idle -> lock? guards 0 '
      '-> mkdir runs140 -> lock -> lock log -> trap -> install -> marker -> run -> hostdev -> envchk -> scorer',
      min(order) >= 0 and order == sorted(order))

# --- 2. the fixture directory: stubs ----------------------------------------------------------------------------
fx = str(BASE).replace('\\', '/')


def w(name, body, raw=False):
    p = BASE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(body if raw else body.encode('utf-8'))
    return p


STUB_HEAD = 'import hashlib, json, os, sys, time\nD = os.path.dirname(os.path.abspath(__file__))\n' \
            'def rd(n, d=""):\n    p = os.path.join(D, n)\n    return open(p).read().strip() if os.path.exists(p) else d\n' \
            'def log(n):\n    open(os.path.join(D, n), "a").write(" ".join(sys.argv[1:]) + chr(10))\n' \
            'def act(n):\n    if rd(n) == "lock":\n        open(os.path.join(D, "SEALED.lock"), "w").write("intruder")\n'
w('procload.py', STUB_HEAD +
  'log("procload_args.txt")\nk = len(open(os.path.join(D, "procload_args.txt")).read().splitlines()) - 1\n'
  'if k == int(rd("procload_lock_at.txt", "-1")):\n    open(os.path.join(D, "SEALED.lock"), "w").write("intruder")\n'
  'seq = rd("procload_rc.txt", "0").split(",")\nsys.exit(int(seq[min(k, len(seq) - 1)]))\n')
w('idle140.py', STUB_HEAD +
  'log("idle_args.txt")\nrc = int(rd("idle_rc.txt", "0"))\nact("idle_action.txt")\n'
  'if rd("idle_action.txt") == "touchpinned":\n'
  '    open(os.path.join(D, "pin.exe"), "ab").write(b"x")\n'
  'print("idle140: fake rc %d" % rc)\nsys.exit(rc)\n')
w('cpu.py', STUB_HEAD + 'log("cpu_args.txt")\nact("cpu_action.txt")\nprint(rd("cpu.txt", ""))\n')
w('hostdev140.py', STUB_HEAD + 'log("hostdev_args.txt")\nprint("VERDICT: RUN_CLEAN - fake")\n')
w('enter_scene.py', STUB_HEAD + '''log("es_args.txt")
a = sys.argv[1:]
tag = a[0]
game = rd("game_path.txt")
gsha = hashlib.sha256(open(game, "rb").read()).hexdigest() if os.path.exists(game) else "NONE"
seen = dict(lock=rd("SEALED.lock", "NONE"), game_sha=gsha, marker=rd("attempt_%s.txt" % tag, "NONE"),
            shell_schedule=os.environ.get("KYTY_GATE_SCHEDULE", "UNSET"),
            shell_abba=os.environ.get("KYTY_GATE_SCHEDULE_ABBA", "UNSET"),
            locklog=rd("runs140/lock.log", "NONE"))
json.dump(seen, open(os.path.join(D, "es_seen.json"), "w"))
act = rd("es_action.txt")
if act == "refuse":
    json.dump(dict(tag=tag, refused="idle"), open(os.path.join(D, tag + ".refused.json"), "w"))
    if rd("es_json_too.txt"):
        json.dump(dict(tag=tag), open(os.path.join(D, tag + ".json"), "w"))
    print("pre_run: REFUSED (BUSY)")
    sys.exit(3)
if act == "rc3bare":
    sys.exit(3)
if act == "killrestore":
    os.remove(os.path.join(D, "restore.exe"))
env = dict(x.split("=", 1) for x in a[1:] if "=" in x and not x.startswith("--"))
env.update(dict((k, v) for k, v in os.environ.items() if k in ("KYTY_GATE_SCHEDULE", "KYTY_GATE_SCHEDULE_ABBA")))
gf = a[a.index("--gates-file") + 1] if "--gates-file" in a else ""
gates = " ".join(open(gf, encoding="utf-8").read().split()) if gf and os.path.exists(gf) else None
json.dump(dict(tag=tag, env=env, gates=gates, binary_sha256=gsha), open(os.path.join(D, tag + ".json"), "w"))
open(os.path.join(D, "log_%s.txt" % tag), "w").write(rd("es_log.txt", "Kyty stub log") + chr(10))
print("hold_gpu: fake row")
print("enter_scene stub done")
sys.exit(int(rd("es_rc.txt", "0")))
''')
CALL = 'go140a call: PLWAIT=%s bash C:/kyty/s140/go140a.sh %s\n'
PRED_TEXT = 'fixture seal of the stub scorer\n' + ''.join(CALL % ('540', t) for t in REGS)
PRED_SHA = hashlib.sha256(PRED_TEXT.encode()).hexdigest()


def scorer(pred_sha):
    return STUB_HEAD + ("PRED_SHA = '%s'\n" % pred_sha) + \
        'if "--check-seal" in sys.argv:\n    log("chk_args.txt")\n    act("chk_action.txt")\n' \
        '    sys.exit(int(rd("chk_rc.txt", "0")))\n' \
        'log("score_args.txt")\nout = sys.argv[sys.argv.index("--out") + 1]\n' \
        'json.dump(dict(verdict="FAKE"), open(out, "w"))\nprint("VERDICT FAKE")\n'


SCORER = scorer(PRED_SHA)
ENVCHK_REAL = pathlib.Path(HERE, 'envchk140.py').read_bytes()

PIN_BYTES = b'PINNED BUILD 05431DAD OF SESSION 140\n'
RES_BYTES = b'RESTORE INSTALLED 9235A7AC\n'
OTHER_BYTES = b'SOMETHING ELSE INSTALLED\n'
PIN_SHA = hashlib.sha256(PIN_BYTES).hexdigest()
RES_SHA = hashlib.sha256(RES_BYTES).hexdigest()
OTHER_SHA = hashlib.sha256(OTHER_BYTES).hexdigest()
GAMEP = BASE / 'game' / 'kyty_emulator.exe'
w('game_path.txt', str(GAMEP).replace('\\', '/'))

SPY = BASE / 'spybin'
SPY.mkdir()
SPYLOG = fx + '/spy.txt'
PY_REAL = (shutil.which('python') or sys.executable).replace('\\', '/')
PS_REAL = (shutil.which('powershell') or 'powershell').replace('\\', '/')
for name in ('python', 'sha256sum', 'powershell', 'date', 'cat', 'cut', 'tr', 'grep', 'cp', 'mv', 'mkdir', 'rm', 'tail',
             'head', 'sleep'):
    real = PY_REAL if name == 'python' else PS_REAL if name == 'powershell' else '/usr/bin/' + name
    (SPY / name).write_bytes(('#!/bin/bash\necho "${0##*/} $*" >> %s\nexec "%s" "$@"\n' % (SPYLOG, real)).encode('utf-8'))
    os.chmod(SPY / name, 0o755)


def line_of(prefix):
    found = [l for l in chain.splitlines() if l.startswith(prefix)]
    return found[0] if len(found) == 1 else None


NAMES_LINE = line_of('  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process')
CPU_LINE = line_of('CPU=$(powershell ')
REPL = [('ROOT=C:/kyty/s140\n', 'ROOT=%s\n' % fx), ('LOCK=/c/kyty/SEALED_RUN.lock\n', 'LOCK=%s/SEALED.lock\n' % fx),
        ('GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"\n', 'GAME="%s/game/kyty_emulator.exe"\n' % fx),
        ('RESTORE="/c/kyty/s128/kyty_emulator_9235a7ac.exe"\n', 'RESTORE="%s/restore.exe"\n' % fx),
        ('RESTORE_SHA="%s"\n' % SHIPSHA, 'RESTORE_SHA="%s"\n' % RES_SHA), ('RSLEEP=5\n', 'RSLEEP=0\n'),
        ((NAMES_LINE or '<none>') + '\n', "  cat %s/names.txt | tr -d '\\r'\n" % fx),
        ((CPU_LINE or '<none>') + '\n', 'CPU=$(python %s/cpu.py)\n' % fx)]


def consts(bsha=None, build=True, exp=None, sealed=True, drop=()):
    out = []
    if bsha is not None:
        out += [('BASESHA="%s"\n' % BSHA, 'BASESHA="%s"\n' % bsha)]
    if build:
        out += [('BUILD_EXPECT=""\n', 'BUILD_EXPECT="%s"\n' % (exp or PIN_SHA)),
                ('BUILD_PINNED=""\n', 'BUILD_PINNED="%s/pin.exe"\n' % fx)]
    if sealed:
        out += [('PRED=""\n', 'PRED="pred/01_x140.md"\n'), ('SC=""\n', 'SC="x140.py"\n')]
    return [e for e in out if e[0].split('=')[0] not in drop]


def variant(name, edits):
    t = chain
    for old, new in REPL + edits:
        if t.count(old) != 1:
            return None
        t = t.replace(old, new)
    path = BASE / name
    path.write_bytes(t.encode('utf-8'))
    return str(path)


def reset(names='0', cpu='3'):
    keep = {'procload.py', 'idle140.py', 'hostdev140.py', 'enter_scene.py', 'cpu.py', 'game_path.txt', 'spybin'}
    for p in list(BASE.iterdir()):
        if p.name in keep or p.suffix == '.sh':
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    w('names.txt', names + '\n')
    w('cpu.txt', cpu + '\n')
    w('pin.exe', PIN_BYTES, raw=True)
    w('restore.exe', RES_BYTES, raw=True)
    w('game/kyty_emulator.exe', OTHER_BYTES, raw=True)
    w('gates_base.txt', GB, raw=True)
    w('envchk140.py', ENVCHK_REAL, raw=True)
    w('x140.py', SCORER)
    w('pred/01_x140.md', PRED_TEXT)


def made(*tags):
    """The attempt markers of earlier pm4c140 calls (the order rule of item 210 (e)(4))."""
    for t in tags:
        w('attempt_%s.txt' % t, 'go140a.sh %s pid 1 attempt started (fixture)' % t)


def prev_of(tag):
    return REGS[REGS.index(tag) - 1] if tag in REGS and tag != REGS[0] else None


def rdf(n):
    p = BASE / n
    return p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''


def jl(n):
    try:
        v = json.loads(rdf(n))
    except ValueError:
        return {}
    return v if isinstance(v, dict) else {}


def game_sha():
    return fsha(GAMEP) if GAMEP.exists() else 'NONE'


def untouched():
    return game_sha() == OTHER_SHA


def nothing_called():
    return not any(rdf(n) for n in ('procload_args.txt', 'idle_args.txt', 'cpu_args.txt', 'chk_args.txt', 'es_args.txt',
                                    'hostdev_args.txt', 'score_args.txt'))


bash = shutil.which('bash') or 'bash'


def go(path, tag='pm4c140a', spy=False, **env):
    if path is None:
        return -1, 'variant anchor missing'
    e = dict(os.environ)
    e.pop('PLWAIT', None)
    e.pop('DRY', None)
    e.pop('KYTY_GATE_SCHEDULE', None)
    e.pop('KYTY_GATE_SCHEDULE_ABBA', None)
    e.update(env)
    if spy:
        e['PATH'] = str(SPY) + os.pathsep + e.get('PATH', '')
    try:
        r = subprocess.run([bash, path, tag], capture_output=True, text=True, env=e, timeout=300)
    except subprocess.TimeoutExpired:
        return -2, 'timeout'
    return r.returncode, r.stdout


check('d0 the fixture anchors exist exactly once (name guard line, CPU line)', NAMES_LINE is not None and CPU_LINE is not None)

reset()
v2 = variant('go_sealed.sh', consts())
v1 = variant('go_pinned.sh', consts(sealed=False))
v0 = variant('go_empty.sh', [])
# --- 3. not configured / usage (rc 2) ---------------------------------------------------------------------------
reset()
for tag in TAGS:
    check('d1 %s: empty build constants -> rc 2 "not pinned yet" (DRY too), nothing called' % tag,
          go(v0, tag) == (2, 'not pinned yet\n') and go(v0, tag, DRY='1')[0] == 2 and nothing_called())
check('d1 the refusal is logged with the item', 'the build not set (item 210 (e)(3))' in rdf('go140a.log'))
for bad in ('', 'pm4s141', 'pm4c140', 'pm4c140e', 'PM4C140A', 'pm4c140a ', 'pm4c140ab', 'kp137a', 's4cs137', 'pm4c139a'):
    rc, out = go(v0, bad)
    check('d2 tag %r -> rc 2 usage' % bad, rc == 2 and out.startswith('usage'))
for k in ('BUILD_EXPECT', 'BUILD_PINNED'):
    vk = variant('go_part.sh', consts(sealed=False, drop=(k,)))
    check('d1c without %s alone -> rc 2 not pinned yet' % k, go(vk, 'pm4s140') == (2, 'not pinned yet\n')
          and go(vk, 'pm4c140a') == (2, 'not pinned yet\n'))
for exp in (PIN_SHA[:63], 'A' + PIN_SHA[1:], PIN_SHA + '0'):
    ve = variant('go_e.sh', consts(exp=exp))
    vb = variant('go_b.sh', consts(bsha=exp.replace(PIN_SHA[:6], BSHA[:6])))
    check('d3e BUILD_EXPECT / BASESHA %r... -> rc 2 bad EXPECT (DRY too)' % exp[:6],
          go(ve, 'pm4s140') == (2, 'bad EXPECT\n') and go(ve, 'pm4c140a', DRY='1')[0] == 2
          and go(vb, 'pm4s140') == (2, 'bad EXPECT\n'))
reset()
for tag in REGS:
    check('d5 %s pinned, seal empty -> rc 2 not sealed yet' % tag, go(v1, tag) == (2, 'not sealed yet\n'))
for k in ('PRED', 'SC'):
    vk = variant('go_part.sh', consts(drop=(k,)))
    check('d5b pm4c140a/pm4c140d: seal without %s alone -> rc 2 not sealed yet' % k,
          go(vk, 'pm4c140a') == (2, 'not sealed yet\n') and go(vk, 'pm4c140d') == (2, 'not sealed yet\n'))
for key, tags in (('SHOLD', ('pm4s140',)), ('PHOLD', ('pm4c140a', 'pm4c140d'))):
    old = re.search(r'^%s="(\d+)"$' % key, chain, re.M)
    for bad in ('0', '5m'):
        vh = variant('go_h.sh', consts() + [('%s="%s"\n' % (key, old.group(1) if old else '?'), '%s="%s"\n' % (key, bad))])
        check('d8 %s %s -> %s rc 2 bad hold, nothing called' % (key, bad, '/'.join(tags)),
              vh is not None and all(go(vh, t) == (2, 'bad hold\n') for t in tags) and nothing_called())
reset()
w('procload_rc.txt', '1')
check('d5e pm4s140 does not need the seal (reaches the guards, BUSY rc 4)',
      go(v1, 'pm4s140')[0] == 4 and rdf('procload_args.txt') == '--wait-s 540\n')

reset()
for tag in TAGS:
    rc, out = go(v2, tag, DRY='1')
    check('d6 DRY %s: the plan - PLWAIT, procload 540, the lock log, install of the build, level, draws, the base gate file, '
          'hold, the trace, pin, markers, no schedule, restore of the installed build' % tag,
          rc == 0 and out.startswith('DRY %s:' % tag) and 'PLWAIT=540; procload --wait-s 540;' in out
          and 'lock (runs140/lock.log UTC);' in out and ('install %s/pin.exe (%s)' % (fx, PIN_SHA)) in out
          and ('--level %s --attempts 1 --stable-draws 300 ' % GARDEN) in out
          and ('--gates-file %s/gates_base.txt --hold %d KYTY_PM4_TRACE=%s KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (no '
               'KYTY_GATE_SCHEDULE);' % (fx, HOLDS[tag], TRACE[tag])) in out
          and ('(registered %d, one attempt 1)' % (tag in REGS)) in out
          and ('--out %s/runs140/%s.score.json' % (fx, tag)) in out and ('restore %s/restore.exe (%s)' % (fx, RES_SHA)) in out
          and 'KYTY_REC' not in out and 'KYTY_GPU_WALL' not in out and '--rec' not in out)
rc, out = go(v2, 'pm4c140a', DRY='1', PLWAIT='7')
check('d6b DRY prints the PLWAIT of the call (7) and does not judge it against the seal', rc == 0 and 'PLWAIT=7;' in out)
rc, out = go(v2, 'pm4c140c', DRY='1')
check('d6c DRY of pm4c140c without the earlier calls is still the plan (the order is judged only on a real call)',
      rc == 0 and out.startswith('DRY pm4c140c:'))
check('d6 DRY calls nothing and installs nothing', nothing_called() and untouched())
for pw in ('541', '5m', '-1', '1e3'):
    check('d7 PLWAIT %r -> rc 2 before any guard' % pw, go(v2, 'pm4s140', PLWAIT=pw)[0] == 2 and nothing_called())

# --- 5. THE LOCK FIRST (item 76 (b)): no process under the lock, in every call ---------------------------------------
for tag, dry in [(t, '0') for t in TAGS] + [('pm4c140a', '1'), ('pm4s140', '1')]:
    reset()
    w('SEALED.lock', 'someone')
    rc, out = go(v2, tag, spy=True, DRY=dry)
    check('L1 %s (DRY %s) under the lock -> BUSY rc 4 "lock held: someone", no process started (spy empty), no '
          'stub called, lock kept, nothing installed, no lock log, log line written' % (tag, dry),
          rc == 4 and out == 'busy: lock held: someone\n' and not rdf('spy.txt') and nothing_called()
          and rdf('SEALED.lock') == 'someone' and untouched() and not rdf('runs140/lock.log')
          and 'refused BUSY (rc 4): lock held: someone' in rdf('go140a.log'))
reset()
w('SEALED.lock', 'someone')
rc, out = go(v0, 'pm4c140a', spy=True)
check('L2 the lock is checked before the configuration: unconfigured chain under the lock -> rc 4, spy empty',
      rc == 4 and out.startswith('busy: lock held') and not rdf('spy.txt'))
reset()
w('SEALED.lock', '')
rc, out = go(v2, 'pm4s140', spy=True)
check('L2b an empty lock file is a lock: rc 4, spy empty', rc == 4 and out == 'busy: lock held: \n' and not rdf('spy.txt'))
reset()
w('SEALED.lock', 'someone')
rc, out = go(v2, 'pm4c140a', spy=True, PLWAIT='0')
check('L2c the lock wins over the PLWAIT rule of the seal (rc 4, spy empty)',
      rc == 4 and out == 'busy: lock held: someone\n' and not rdf('spy.txt'))
reset()
w('SEALED.lock', 'someone')
rc, out = go(v2, 'pm4c140d', spy=True)
check('L2d the lock wins over the order refusal (pm4c140d, no earlier call: rc 4, spy empty)',
      rc == 4 and out == 'busy: lock held: someone\n' and not rdf('spy.txt'))
reset()
w('procload_rc.txt', '1')
rc, out = go(v2, 'pm4s140', spy=True)
spy = rdf('spy.txt')
check('L0 spy control: the unlocked call logs sha256sum and python (procload) - the empty spy above is not a dead spy',
      rc == 4 and 'sha256sum ' in spy and 'python %s/procload.py --wait-s 540' % fx in spy)

# --- 11. THE SEAL'S CALL (item 105 (v)): PLWAIT of a pm4c140 call = its one call line of the seal -----------------------
for tag, pw in (('pm4c140a', '0'), ('pm4c140a', '539'), ('pm4c140c', '0'), ('pm4c140d', '539')):
    reset()
    rc, out = go(v2, tag, spy=True, PLWAIT=pw)
    spy = rdf('spy.txt')
    check('p1 %s PLWAIT=%s against the seal line PLWAIT=540 -> rc 1 "PLWAIT differs from the seal" before any guard and '
          'the lock: no procload, no install, no lock, no marker, logged with the item' % (tag, pw),
          (rc, out) == (1, 'PLWAIT differs from the seal\n') and nothing_called() and untouched()
          and not (BASE / 'SEALED.lock').exists() and not (BASE / ('attempt_%s.txt' % tag)).exists()
          and ('PLWAIT=%s is not the one call line of the seal' % pw) in rdf('go140a.log')
          and 'item 105 (v)' in rdf('go140a.log') and 'procload' not in spy and 'cp ' not in spy)
for body, tag, pw, ok_ in (
        (CALL % ('0', 'pm4c140a'), 'pm4c140a', '0', True),
        (CALL % ('0', 'pm4c140a'), 'pm4c140a', '540', False),
        (CALL % ('60', 'pm4c140a') + CALL % ('0', 'pm4c140a'), 'pm4c140a', '0', False),
        (CALL % ('0', 'pm4c140a') * 2, 'pm4c140a', '0', False),
        ('', 'pm4c140a', '540', False),
        (CALL % ('540', 'pm4s140'), 'pm4c140a', '540', False),
        (CALL % ('540', 'pm4c140ab'), 'pm4c140a', '540', False),
        (CALL % ('540', 'pm4c140'), 'pm4c140a', '540', False),
        ('x ' + CALL % ('540', 'pm4c140a'), 'pm4c140a', '540', False),
        (CALL % ('00', 'pm4c140a'), 'pm4c140a', '0', False),
        (CALL % ('', 'pm4c140a') + CALL % ('540', 'pm4c140a'), 'pm4c140a', '540', True),
        ((CALL % ('540', 'pm4c140a')).replace('go140a', 'go137a'), 'pm4c140a', '540', False),
        ((CALL % ('540', 'pm4c140a')).replace('s140', 's137'), 'pm4c140a', '540', False),
        (CALL % ('540', 'pm4c140a'), 'pm4c140b', '540', False),
        (CALL % ('540', 'pm4c140a') + CALL % ('0', 'pm4c140b'), 'pm4c140b', '0', True),
        (CALL % ('540', 'pm4c140a') + CALL % ('0', 'pm4c140b'), 'pm4c140a', '0', False)):
    reset()
    text_pred = 'fixture seal\n' + body
    w('pred/01_x140.md', text_pred)
    w('x140.py', scorer(hashlib.sha256(text_pred.encode()).hexdigest()))
    w('procload_rc.txt', '1')
    if prev_of(tag):
        made(*REGS[:REGS.index(tag)])
    rc, out = go(v2, tag, PLWAIT=pw)
    check('p2 seal line %r, call %s PLWAIT=%s -> %s' % (body.strip()[:70], tag, pw,
                                                        'passes to the guards' if ok_ else 'refused'),
          (rc == 4 and rdf('procload_args.txt') == '--wait-s %s\n' % pw) if ok_
          else ((rc, out) == (1, 'PLWAIT differs from the seal\n') and not rdf('procload_args.txt')))
reset()
(BASE / 'pred' / '01_x140.md').unlink()
rc, out = go(v2, 'pm4c140a')
check('p3 the seal file missing -> refused by the PLWAIT rule (rc 1) before the pred sha',
      (rc, out) == (1, 'PLWAIT differs from the seal\n') and nothing_called())
reset()
rc, out = go(v1, 'pm4c140a', PLWAIT='0')
check('p4 the unsealed chain answers "not sealed yet" (rc 2) before the PLWAIT rule', (rc, out) == (2, 'not sealed yet\n'))
reset()
(BASE / 'pred' / '01_x140.md').unlink()
w('x140.py', scorer('1' * 64))
w('chk_rc.txt', '1')
w('procload_rc.txt', '1')
rc, out = go(v2, 'pm4s140', PLWAIT='0')
check('p5 pm4s140 (not registered) ignores the seal, the pred sha and the pre-seal check: PLWAIT=0 reaches the guards, logged',
      rc == 4 and rdf('procload_args.txt') == '--wait-s 0\n' and 'PLWAIT=0)' in rdf('go140a.log') and not rdf('chk_args.txt'))
reset()
w('attempt_pm4c140a.txt', 'x')
rc, out = go(v2, 'pm4c140a', PLWAIT='0')
check('p6 the PLWAIT rule comes before the one-attempt refusal (rc 1 PLWAIT, not attempt)',
      (rc, out) == (1, 'PLWAIT differs from the seal\n'))
reset()
rc, out = go(v2, 'pm4c140c', PLWAIT='0')
check('p7 the PLWAIT rule comes before the order refusal (pm4c140c without earlier calls, PLWAIT=0 -> rc 1 PLWAIT)',
      (rc, out) == (1, 'PLWAIT differs from the seal\n'))

# --- 11b. THE ORDER OF THE 4 CALLS (item 210 (e)(4)) ------------------------------------------------------------------
for tag in REGS[1:]:
    reset()
    made(*[t for t in REGS[:REGS.index(tag)] if t != prev_of(tag)])
    rc, out = go(v2, tag, spy=True)
    check('q1 %s with every earlier call but %s made -> rc 1 "previous call not made" before any guard and the lock: no '
          'stub, no install, no lock, no marker, no sha256sum, logged with the item' % (tag, prev_of(tag)),
          (rc, out) == (1, 'previous call not made\n') and nothing_called() and untouched()
          and not (BASE / 'SEALED.lock').exists() and not (BASE / ('attempt_%s.txt' % tag)).exists()
          and ('the call %s before it was not made' % prev_of(tag)) in rdf('go140a.log')
          and 'item 210 (e)(4)' in rdf('go140a.log') and 'sha256sum' not in rdf('spy.txt'))
for tag in ('pm4c140b', 'pm4c140d'):
    reset()
    made(prev_of(tag))
    w('procload_rc.txt', '1')
    check('q2 %s with the marker of %s alone -> passes to the guards (BUSY rc 4)' % (tag, prev_of(tag)),
          go(v2, tag)[0] == 4 and rdf('procload_args.txt') == '--wait-s 540\n')
reset()
w('pm4c140b.json', '{}')
w('procload_rc.txt', '1')
check('q3 pm4c140c with pm4c140b.json alone (the attempt made, the marker gone) -> passes to the guards',
      go(v2, 'pm4c140c')[0] == 4)
reset()
w('procload_rc.txt', '1')
check('q4 pm4c140a needs no earlier call -> passes to the guards', go(v2, 'pm4c140a')[0] == 4)
reset()
made('pm4c140a', 'pm4c140b')
w('pm4c140c.refused.json', '{}')
w('old/x_pm4c140c/attempt_pm4c140c.txt', 'moved by an idle refusal')
check('q5 an idle-refused call (marker moved to old/, only <tag>.refused.json) is not made: pm4c140d refuses',
      go(v2, 'pm4c140d') == (1, 'previous call not made\n'))
reset()
made('pm4c140a')
w('attempt_pm4c140b.txt', 'x')
check('q6 the one-attempt refusal comes before the order refusal (pm4c140b made -> rc 1 attempt already made)',
      go(v2, 'pm4c140b') == (1, 'attempt already made\n'))
reset()
made('pm4c140a')
check('q7 the marker of another earlier call does not count: pm4c140c with pm4c140a made refuses',
      go(v2, 'pm4c140c') == (1, 'previous call not made\n'))
reset()
w('procload_rc.txt', '1')
check('q8 the smoke needs no call before it (reaches the guards)', go(v2, 'pm4s140')[0] == 4)

# --- 4. hard refusals before the guards (rc 1) ---------------------------------------------------------------------
for tag in ('pm4c140a', 'pm4s140'):
    reset()
    w('attempt_%s.txt' % tag, 'earlier attempt')
    check('d9 %s: attempt marker present -> rc 1 attempt already made, nothing called' % tag,
          go(v2, tag) == (1, 'attempt already made\n') and nothing_called())
    reset()
    w('%s.json' % tag, '{}')
    check('d9 %s: <tag>.json present -> rc 1 attempt already made' % tag, go(v2, tag) == (1, 'attempt already made\n'))
reset()
w('attempt_pm4s140.txt', 'earlier attempt')
w('procload_rc.txt', '1')
check('d9b the marker of one tag does not refuse another tag', go(v2, 'pm4c140a')[0] == 4)
reset()
(BASE / 'pin.exe').unlink()
check('d10 pm4c140a: the pinned copy missing -> rc 1, procload never called',
      go(v2, 'pm4c140a') == (1, 'pinned build bad\n') and nothing_called())
reset()
w('pin.exe', b'other bytes', raw=True)
check('d10 pm4s140: the pinned copy sha differs -> rc 1 (one build for every tag)', go(v2, 'pm4s140') == (1, 'pinned build bad\n'))
reset()
(BASE / 'restore.exe').unlink()
check('d11 restore copy missing -> rc 1 before the lock', go(v2) == (1, 'restore build bad\n') and nothing_called())
reset()
w('restore.exe', b'other bytes', raw=True)
check('d11 restore copy sha differs -> rc 1', go(v2, 'pm4s140') == (1, 'restore build bad\n'))
for tag, base in (('pm4s140', GB + b' extra=1'), ('pm4c140a', GB.replace(b'bindlean=0\r\n', b''))):
    reset()
    w('gates_base.txt', base, raw=True)
    check('d12 %s: gates_base.txt sha differs (%r) -> rc 1' % (tag, base[-12:]),
          go(v2, tag) == (1, 'base gate file bad\n') and nothing_called())

# --- 7. BUSY (rc 4): no run --------------------------------------------------------------------------------------
reset()
w('procload_rc.txt', '1')
rc, out = go(v2)
check('d15 procload not clean -> BUSY rc 4, waited 540 (the default = PLMAX)',
      rc == 4 and out.startswith('busy: procload') and rdf('procload_args.txt') == '--wait-s 540\n')
check('d15 no lock, no install, no marker, no lock log', not (BASE / 'SEALED.lock').exists() and untouched()
      and not (BASE / 'attempt_pm4c140a.txt').exists() and not rdf('runs140/lock.log'))
reset()
w('procload_rc.txt', '1')
check('d15 PLWAIT 0 accepted for an unregistered tag', go(v2, 'pm4s140', PLWAIT='0')[0] == 4
      and rdf('procload_args.txt') == '--wait-s 0\n')
for names in ('1', ''):
    reset(names=names)
    rc, out = go(v2)
    check('d16 name guard %r -> BUSY rc 4' % names, rc == 4 and out.startswith('busy: procload / name guard')
          and not rdf('chk_args.txt'))
for cpu in ('15', 'x'):
    reset(cpu=cpu)
    rc, out = go(v2)
    check('d17 cpu %r -> BUSY rc 4, idle not called' % cpu, rc == 4 and out.startswith('busy: machine not idle')
          and not rdf('idle_args.txt'))
reset(cpu='14')
w('idle_rc.txt', '1')
rc, out = go(v2)
check('d18 cpu 14 passes to idle; idle BUSY -> rc 4', rdf('idle_args.txt') == '\n' and rc == 4
      and out.startswith('busy: machine not idle by idle140'))
reset()
w('idle_rc.txt', '2')
check('d18 idle UNAVAILABLE -> rc 4, no lock', go(v2)[0] == 4 and not (BASE / 'SEALED.lock').exists())
reset()
w('procload_rc.txt', '0,1')
rc, out = go(v2)
check('d19 second guard not clean -> rc 4; no lock, no install, no marker, no run, no lock log',
      rc == 4 and out.startswith('busy: procload / name guard not clean before the lock')
      and rdf('procload_args.txt') == '--wait-s 540\n--wait-s 0\n' and not (BASE / 'SEALED.lock').exists()
      and untouched() and not (BASE / 'attempt_pm4c140a.txt').exists() and not rdf('es_args.txt')
      and not rdf('runs140/lock.log'))
reset()
w('procload_lock_at.txt', '0')
rc, out = go(v2)
check('L3 the lock appears during the first procload wait -> rc 4 lock held; pre-seal check, CPU, idle and the second '
      'procload never called, the intruder lock kept, nothing installed',
      rc == 4 and out == 'busy: lock held: intruder\n' and rdf('procload_args.txt') == '--wait-s 540\n'
      and not rdf('chk_args.txt') and not rdf('cpu_args.txt') and not rdf('idle_args.txt')
      and rdf('SEALED.lock') == 'intruder' and untouched())
reset()
w('chk_action.txt', 'lock')
rc, out = go(v2)
check('L4 the lock appears during the pre-seal check -> rc 4; CPU, idle, second procload not called',
      rc == 4 and out == 'busy: lock held: intruder\n' and rdf('chk_args.txt') == '--check-seal --tag pm4c140a\n'
      and not rdf('cpu_args.txt') and not rdf('idle_args.txt') and rdf('procload_args.txt') == '--wait-s 540\n')
reset()
w('cpu_action.txt', 'lock')
rc, out = go(v2, 'pm4s140')
check('L5 the lock appears during the CPU check -> rc 4; idle and the second procload not called',
      rc == 4 and out == 'busy: lock held: intruder\n' and rdf('cpu_args.txt') != '' and not rdf('idle_args.txt')
      and rdf('procload_args.txt') == '--wait-s 540\n')
reset()
w('idle_action.txt', 'lock')
rc, out = go(v2, 'pm4s140')
check('L6 the lock appears during idle -> rc 4 lock held; the second procload never called, no install',
      rc == 4 and out == 'busy: lock held: intruder\n' and rdf('procload_args.txt') == '--wait-s 540\n' and untouched()
      and not rdf('es_args.txt'))
reset()
w('procload_lock_at.txt', '1')
rc, out = go(v2)
check('L7 the lock appears during the second procload -> the noclobber take fails: rc 4 "lock taken by someone else", '
      'the intruder lock kept, no install, no marker, no run, no lock log line',
      rc == 4 and out.startswith('busy: lock taken by someone else') and rdf('SEALED.lock') == 'intruder' and untouched()
      and not (BASE / 'attempt_pm4c140a.txt').exists() and not rdf('es_args.txt') and not rdf('runs140/lock.log'))

# --- 8. pre-seal refusals (rc 1) ----------------------------------------------------------------------------------
reset()
w('x140.py', scorer('1' * 64))
check('d21 pm4c140a: pred sha differs from PRED_SHA -> rc 1, no check-seal, no lock', go(v2, 'pm4c140a')[0] == 1
      and not rdf('chk_args.txt') and not (BASE / 'SEALED.lock').exists())
reset()
w('x140.py', SCORER.replace("PRED_SHA = '%s'\n" % PRED_SHA, ''))
check('d21 scorer without PRED_SHA -> rc 1', go(v2, 'pm4c140a')[0] == 1 and not rdf('chk_args.txt'))
reset()
made('pm4c140a', 'pm4c140b')
w('chk_rc.txt', '1')
rc, _ = go(v2, 'pm4c140c')
check('d22 pm4c140c: the scorer --check-seal refuses -> rc 1, called with --check-seal --tag pm4c140c, no CPU, no idle, no '
      'lock', rc == 1 and rdf('chk_args.txt') == '--check-seal --tag pm4c140c\n' and not rdf('cpu_args.txt')
      and not rdf('idle_args.txt') and not (BASE / 'SEALED.lock').exists())
reset()
w('idle_action.txt', 'touchpinned')
rc, _ = go(v2)
check('d23 pinned copy changed after the pre-lock check -> rc 1 inside the lock; not installed, nothing restored, '
      'lock removed, no marker, no run; the lock log has taken and released',
      rc == 1 and not (BASE / 'SEALED.lock').exists() and untouched()
      and not (BASE / 'attempt_pm4c140a.txt').exists() and not rdf('es_args.txt')
      and 'inside the lock - stop' in rdf('go140a.log') and 'restored' not in rdf('go140a.log')
      and re.fullmatch(r'lock taken pm4c140a %s\nlock released pm4c140a %s\n' % (UTC, UTC), rdf('runs140/lock.log')))

# --- 6. protceil only 0 (item 93 (b)) -------------------------------------------------------------------------------
for tag, dry in (('pm4c140a', '0'), ('pm4c140a', '1'), ('pm4s140', '0'), ('pm4c140d', '0')):
    reset()
    w('gates_base.txt', GB.replace(b'protceil=0', b'protceil=1'), raw=True)
    rc, out = go(v2, tag, spy=True, DRY=dry)
    check('v1 %s (DRY %s): base with protceil=1 in place -> rc 1 "protceil refused", no stub called, nothing '
          'installed, no lock, no python/cp/sha256sum started, logged with the item' % (tag, dry),
          (rc, out) == (1, 'protceil refused\n') and nothing_called() and untouched()
          and not (BASE / 'SEALED.lock').exists() and 'item 93 (b)' in rdf('go140a.log')
          and not rdf('spy.txt'))
for base, refused in ((GB.replace(b'protceil=0', b'protceil=00'), True), (GB + b'protceil=1', True),
                      (GB + b' protceil=', True), (GB.replace(b'protceil=0', b'xprotceil=1'), False),
                      (GB.replace(b'protceil=0', b'protceil'), False)):
    reset()
    w('gates_base.txt', base, raw=True)
    rc, out = go(v2, 'pm4s140')
    check('v2 base %r -> %s' % (base[-26:], 'protceil refused' if refused else 'base gate file bad (sha)'),
          (rc, out) == ((1, 'protceil refused\n') if refused else (1, 'base gate file bad\n')) and nothing_called())
reset()
w('gates_base.txt', GB.replace(b'protceil=0', b'protceil=1'), raw=True)
rc, out = go(v0, 'pm4s140')
check('v6 the configuration check comes first: unconfigured pm4s140 with protceil=1 -> rc 2 not pinned yet',
      (rc, out) == (2, 'not pinned yet\n'))
reset()
(BASE / 'gates_base.txt').unlink()
rc, out = go(v2, 'pm4s140')
check('v7 a missing base is not a protceil refusal (-> base gate file bad, rc 1)', (rc, out) == (1, 'base gate file bad\n'))


# --- 9. the full paths ------------------------------------------------------------------------------------------------
def full_path(tag, shell_sched=False):
    reg = tag in REGS
    reset()
    if reg:
        made(*REGS[:REGS.index(tag)])
    for n, body in (('%s.refused.json' % tag, 'stale'), ('hostdev_%s.txt' % tag, 'stale'), ('log_%s.txt' % tag, 'stale'),
                    ('score_%s.txt' % tag, 'stale'), ('runs140/%s.score.json' % tag, 'stale')):
        w(n, body)
    extra = {'KYTY_GATE_SCHEDULE': '90+1800:bindlean=0|bindlean=1', 'KYTY_GATE_SCHEDULE_ABBA': '1'} if shell_sched else {}
    rc, out = go(v2, tag, **extra)
    es = rdf('es_args.txt')
    seen = jl('es_seen.json')
    log = rdf('go140a.log')
    ev = rdf('envchk_%s.txt' % tag)
    want = ('%s --level %s --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file %s/gates_base.txt'
            '%s --hold %d KYTY_PM4_TRACE=%s KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0\n'
            % (tag, GARDEN, fx, (' --pred %s/pred/01_x140.md' % fx) if reg else '', HOLDS[tag], TRACE[tag]))
    check('e1 %s full run -> rc 0 with exactly these enter_scene arguments (the trace %s positionally)' % (tag, TRACE[tag]),
          rc == 0 and es == want)
    check('e2 %s ran inside the lock on the pinned build, the lock gone after, the INSTALLED build restored' % tag,
          seen.get('lock', '').startswith('go140a.sh %s pid' % tag) and seen.get('game_sha') == PIN_SHA
          and game_sha() == RES_SHA and not (BASE / 'SEALED.lock').exists() and ('restored %s/restore.exe' % fx) in log
          and ('installed before: %s' % OTHER_SHA) in log)
    check('e2b %s: the lock log - one "lock taken" line (UTC) seen during the run, then one "lock released" line (UTC)' % tag,
          re.fullmatch(r'lock taken %s %s' % (tag, UTC), seen.get('locklog', ''))
          and re.fullmatch(r'lock taken %s %s\nlock released %s %s\n' % (tag, UTC, tag, UTC), rdf('runs140/lock.log')))
    check('e2c %s: the enter_scene process saw no KYTY_GATE_SCHEDULE / ABBA of the shell%s' % (
        tag, ' (the shell had both set)' if shell_sched else ''),
          seen.get('shell_schedule') == 'UNSET' and seen.get('shell_abba') == 'UNSET')
    check('e3 %s: the attempt marker written before the run (with the build) and kept' % tag,
          seen.get('marker', '').startswith('go140a.sh %s pid' % tag) and ('build %s' % PIN_SHA) in seen.get('marker', '')
          and rdf('attempt_%s.txt' % tag).startswith('go140a.sh %s pid' % tag))
    rows = ['KYTY_GPU_CLOCK_PIN=1 ok', 'no KYTY_GPU_CHECKPOINTS ok', 'KYTY_GPU_MARKERS=0 ok', 'no KYTY_REC ok',
            'no KYTY_GATE_SCHEDULE ok', 'no KYTY_GATE_SCHEDULE_ABBA ok', 'gates = base ok',
            'm4baton=0 in the gates once (item 168 (v)) ok', 'no KYTY_M4_BATON other than 0 in the env ok',
            'log log_%s.txt readable and no "Gate: m4baton=" line other than 0 (values []) ok' % tag]
    check('e4 %s: the real envchk140 of the run passes with its rows (%s)' % (tag, ', '.join(rows)),
          ev.startswith('envchk140: PASS') and all(r in ev for r in rows) and ('envchk %s rc=0' % tag) in log)
    env = jl('%s.json' % tag).get('env') or {}
    check('e5 %s: the gate text the emulator got = the base words; the env it got carries KYTY_PM4_TRACE=%s, no VK_, no '
          'schedule, no video' % (tag, TRACE[tag]),
          (jl('%s.json' % tag).get('gates') or '').split() == GBW and env.get('KYTY_PM4_TRACE') == TRACE[tag]
          and not any(k.startswith('VK_') for k in env) and 'KYTY_REC' not in env and 'KYTY_GATE_SCHEDULE' not in env)
    check('e6 %s: guards 540 then 0; CPU and idle once; check-seal %s; hostdev unpadded; scorer %s'
          % (tag, '--tag ' + tag if reg else 'not called', '--tag --out runs140' if reg else 'not called'),
          rdf('procload_args.txt') == '--wait-s 540\n--wait-s 0\n' and rdf('idle_args.txt') == '\n'
          and rdf('cpu_args.txt') == '\n' and rdf('hostdev_args.txt') == '%s --pad 0\n' % tag
          and rdf('chk_args.txt') == ('--check-seal --tag %s\n' % tag if reg else '')
          and rdf('score_args.txt') == ('--tag %s --out %s/runs140/%s.score.json\n' % (tag, fx, tag) if reg else '')
          and (jl('runs140/%s.score.json' % tag).get('verdict') == 'FAKE') == reg
          and ('score %s rc=0' % tag in log) == reg and ('hold_gpu %s hold_gpu: fake row' % tag) in log
          and '] done\n' in log and log.index('] done\n') < log.index('restored '))
    flines = [l for l in log.splitlines() if 'files: ' in l]
    check('e8 %s: one files line names the build, the base, the helpers%s' % (tag, ' and the seal files' if reg else ''),
          len(flines) == 1 and 'pin.exe' in flines[0] and 'envchk140.py' in flines[0] and 'gates_base.txt' in flines[0]
          and ('x140.py' in flines[0]) == reg and ('01_x140.md' in flines[0]) == reg)
    olds = list((BASE / 'old').glob('*_%s' % tag)) if (BASE / 'old').exists() else []
    check('e9 %s: stale artefacts (the old score and its json too) moved to old/<ts>_%s/, the stdout of the run beside '
          'it' % (tag, tag), len(olds) == 1
          and {'%s.refused.json' % tag, 'hostdev_%s.txt' % tag, 'log_%s.txt' % tag, 'score_%s.txt' % tag,
               '%s.score.json' % tag} <= {p.name for p in olds[0].rglob('*') if p.is_file()}
          and 'enter_scene stub done' in rdf('%s.stdout.txt' % tag))
    check('e10 %s: the requested line logs the trace and PLWAIT=540 (item 105 (v))%s' % (tag, ' and the seal line '
                                                                                        'match' if reg else ''),
          ("extra 'KYTY_PM4_TRACE=%s'" % TRACE[tag]) in log and ('PLWAIT=540)' in log)
          and (('PLWAIT=540 = the call line of the seal pred/01_x140.md' in log) == reg))
    n_pl = rdf('procload_args.txt')
    rc, out = go(v2, tag)
    check('e11 %s: a second call -> rc 1 attempt already made, nothing called' % tag,
          (rc, out) == (1, 'attempt already made\n') and rdf('procload_args.txt') == n_pl)
    (BASE / ('attempt_%s.txt' % tag)).unlink(missing_ok=True)
    check('e11 %s: <tag>.json alone still refuses the repeat' % tag, go(v2, tag) == (1, 'attempt already made\n'))
    if reg and tag != REGS[-1]:
        nxt = REGS[REGS.index(tag) + 1]
        w('procload_rc.txt', '1')
        check('e12 %s made -> the next call %s passes the order rule (reaches the guards)' % (tag, nxt),
              go(v2, nxt)[0] == 4)


full_path('pm4c140a', shell_sched=True)   # the registered form first, with a schedule in the shell (the failures reuse it)

# --- 10. failures after the install ------------------------------------------------------------------------------
reset()
w('es_rc.txt', '1')
rc, out = go(v2)
check('f1 enter_scene failure -> rc 1; restored, lock gone, marker stays, hostdev/envchk/scorer still ran, lock log both lines',
      rc == 1 and game_sha() == RES_SHA and not (BASE / 'SEALED.lock').exists()
      and (BASE / 'attempt_pm4c140a.txt').exists() and rdf('hostdev_args.txt') != '' and rdf('score_args.txt') != ''
      and rdf('runs140/lock.log').count('lock released pm4c140a') == 1)
reset()
w('es_rc.txt', '1')
check('f1b the smoke failing -> rc 1, restored, marker stays, no scorer', go(v2, 'pm4s140')[0] == 1
      and game_sha() == RES_SHA and (BASE / 'attempt_pm4s140.txt').exists() and not rdf('score_args.txt'))
for tag in ('pm4c140a', 'pm4s140'):
    reset()
    w('es_action.txt', 'refuse')
    rc, out = go(v2, tag)
    olds = list((BASE / 'old').glob('*_%s' % tag)) if (BASE / 'old').exists() else []
    check('f2 %s: idle refusal inside enter_scene (rc 3) -> BUSY rc 4; restored, lock gone, no hostdev/scorer; the '
          'marker moved to old/<ts>_%s/ (no attempt made); the lock log has both lines' % (tag, tag),
          rc == 4 and out.startswith('busy: the idle criterion inside enter_scene.py refused') and game_sha() == RES_SHA
          and not (BASE / 'SEALED.lock').exists() and not rdf('hostdev_args.txt') and not rdf('score_args.txt')
          and not (BASE / ('attempt_%s.txt' % tag)).exists() and len(olds) == 1
          and (olds[0] / ('attempt_%s.txt' % tag)).exists() and rdf('runs140/lock.log').count('lock released') == 1)
    if tag != 'pm4c140a':
        continue
    w('procload_rc.txt', '1')
    check('f2 pm4c140a refused inside: pm4c140b still refuses by the order rule (no attempt was made)',
          go(v2, 'pm4c140b') == (1, 'previous call not made\n'))
    (BASE / 'es_action.txt').unlink()
    (BASE / 'procload_rc.txt').unlink()
    (BASE / 'procload_args.txt').unlink()
    rc, out = go(v2, tag)
    check('f2 %s: the next call runs (the refused call used no attempt)' % tag,
          rc == 0 and (BASE / ('attempt_%s.txt' % tag)).exists())
for tag in ('pm4c140a', 'pm4s140'):
    reset()
    w('es_rc.txt', '3')
    rc, out = go(v2, tag)
    check('f3 %s: rc 3 WITH a run json (not the idle refusal) -> rc 1 (item 66 (a)): the marker stays, hostdev/envchk ran, '
          'the scorer %s, restored, lock gone, logged' % (tag, 'ran' if tag in REGS else 'not called (unregistered)'),
          rc == 1 and (BASE / ('attempt_%s.txt' % tag)).exists() and game_sha() == RES_SHA
          and not (BASE / 'SEALED.lock').exists() and rdf('hostdev_args.txt') != ''
          and (rdf('score_args.txt') != '') == (tag in REGS)
          and rdf('envchk_%s.txt' % tag) != '' and ('rc 3 with %s.json: the one attempt' % tag) in rdf('go140a.log'))
reset()
w('es_action.txt', 'refuse')
w('es_json_too.txt', '1')
rc, out = go(v2)
check('f3b rc 3 with BOTH pm4c140a.refused.json and pm4c140a.json -> rc 1, the marker stays (the json wins)',
      rc == 1 and (BASE / 'attempt_pm4c140a.txt').exists() and rdf('score_args.txt') != '')
reset()
w('es_action.txt', 'rc3bare')
rc, out = go(v2)
check('f3c rc 3 with neither json -> BUSY rc 4, the marker stays (only the idle refusal file moves it)',
      rc == 4 and (BASE / 'attempt_pm4c140a.txt').exists() and not rdf('score_args.txt') and game_sha() == RES_SHA)
reset()
w('es_action.txt', 'killrestore')
rc, out = go(v2, 'pm4s140')
check('f4 restore copy gone during the run -> rc 1, "restore failed", RESTORE FAILED logged, lock removed, released logged',
      rc == 1 and 'restore failed' in out and 'RESTORE FAILED' in rdf('go140a.log') and not (BASE / 'SEALED.lock').exists()
      and game_sha() == PIN_SHA and 'lock released pm4s140' in rdf('runs140/lock.log'))
reset()
vg = variant('go_nogame.sh', consts() + [('GAME="%s/game/kyty_emulator.exe"\n' % fx, 'GAME="%s/nodir/kyty_emulator.exe"\n' % fx)])
rc, out = go(vg)
check('f5 install copy fails -> rc 1, no run, lock removed, restore attempted and failed loudly',
      rc == 1 and not rdf('es_args.txt') and not (BASE / 'SEALED.lock').exists() and 'install copy failed' in rdf('go140a.log')
      and 'RESTORE FAILED' in rdf('go140a.log') and not (BASE / 'attempt_pm4c140a.txt').exists())

# --- 9 (rest). the full paths of the smoke and of the other calls ---------------------------------------------------
for tag in ('pm4s140', 'pm4c140b', 'pm4c140c', 'pm4c140d'):
    full_path(tag)
# item 168 (v): a log with a m4baton change -> the real envchk140 FAILs (recorded) - on the smoke and on the first and the
# last call
for tag in ('pm4s140', 'pm4c140a', 'pm4c140d'):
    reset()
    made(*(REGS[:REGS.index(tag)] if tag in REGS else ()))
    w('es_log.txt', 'Gate: m4baton=1 frame=5')
    rc, out = go(v2, tag)
    ev = rdf('envchk_%s.txt' % tag)
    check('e4b %s: the run log carries Gate: m4baton=1 -> envchk140 FAIL on the log row, recorded rc=1' % tag,
          ev.startswith('envchk140: FAIL') and '(values [1]) NO' in ev and ('envchk %s rc=1' % tag) in rdf('go140a.log'))

# --- 12. the real log, lock and emulator untouched --------------------------------------------------------------
check('z1 the real go140a.log untouched by the fixtures',
      (REAL_LOG.read_bytes() if REAL_LOG.exists() else None) == real_log_before)
check('z2 the real lock never created by the fixtures', REAL_LOCK.exists() == real_lock_before)
check('z3 the real installed emulator untouched', (REAL_GAME.stat().st_mtime_ns if REAL_GAME.exists() else None)
      == real_game_stat)

print('checks: %d' % count[0])
print('wall %.0f s' % (time.time() - T0))
if fails:
    for f in fails:
        print('FAIL ' + f)
    sys.exit(1)
print('ALL OK')
