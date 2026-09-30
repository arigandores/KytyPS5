#!/bin/bash
# Session 140 (ROADMAP s.0.1 "SESSION 122" items 210 (e)(3)-(4), (8), 212 (i), 213 (d), (zh); brief docs/next-session-140.md):
# the game chain of the PM4 per-opcode census on ONE pinned build 05431dad (item 210 (e)(3)) - the smoke pm4s140 (step 2)
# and the REGISTERED census pm4c140a..pm4c140d (step 3; 4 x 300 s, KYTY_PM4_TRACE = 0, 1, 1, 0 - item 210 (e)(4)).
# Step 2, HPP-268: port of C:/kyty/s137/go137a.sh by hand (the tag set replaced; no schedule, no GSPEC gate file, no stop
# file; the pre-seal check is the scorer's own --check-seal).  ASCII only (item 175 (v), process 3).  Kept from 127-137:
# THE LOCK IS CHECKED BEFORE ANY PROCESS OF THE CHAIN IN EVERY CALL - DRY included - and again before every later guard
# stage (first procload, pre-seal check, CPU, idle, second procload); under the lock the call refuses BUSY (rc 4) having
# started no process (only bash builtins run before the first check: the log line is written with printf, the lock text
# read with read; item 76 (b)).  New in s140 (audit 137, Process 1): the take and the release of the lock are written as
# "lock taken|released <tag> <UTC by date -u>" into runs140/lock.log (go140a.log keeps the local time).
#   BASESHA - the sha256 of gates_base.txt (the base of s136/s137, byte copy): the knob string of arm 0 of kp137 (item 210
#            (e)(3): bindlean=0, rtskip=1, rbcen=1 rbslow=0 bindlap=1 pathlap=1 mutsite=1 plkstat=1 named once each).
#   BUILD_EXPECT/BUILD_PINNED - item 210 (e)(3): the ONE build of every tag of session 140, 05431dad (tree a2849aec),
#            its pinned copy C:/kyty/s136/kyty_emulator_05431dad.exe.  No other build.
#   PRED/SC - the seal of step 2 (pred/01_pm4c140.md, the scorer pm4c140.py carrying PRED_SHA; its --check-seal is the
#            pre-seal check); empty = every pm4c140 call refuses (rc 2 "not sealed yet").
#   SHOLD 120 (pm4s140, the smoke of step 2), PHOLD 300 (every pm4c140 call) - items 210 (e)(4), (8).
# THE GATE FILE: every tag runs on gates_base.txt itself (item 212 (i): the arm-0 knob string through the gate file, NO
#   KYTY_GATE_SCHEDULE); the chain unsets KYTY_GATE_SCHEDULE and KYTY_GATE_SCHEDULE_ABBA of its shell (enter_scene.py
#   passes a KYTY_GATE_SCHEDULE of the shell through); envchk140.py --census --no-rec --base-is checks <tag>.json after.
#   THE TRACE (item 212 (i)): KYTY_PM4_TRACE is an environment variable of the call, passed POSITIONALLY to enter_scene.py
#             (a KYTY_* of the shell is dropped there): pm4s140 1; pm4c140a 0; pm4c140b 1; pm4c140c 1; pm4c140d 0.
#   THE SMOKE (step 2; unregistered): pm4s140 - Sky Garden, KYTY_PM4_TRACE=1, hold SHOLD; read by the scorer's --smoke
#             (masked levels, RC7 of review140) by hand after the call.
#   THE REGISTERED CALLS (step 3; REG=1): pm4c140a..pm4c140d - each Sky Garden, hold PHOLD, NO video, NO KYTY_GPU_WALL.
#   THE ORDER OF THE CALLS (item 210 (e)(4): 4 calls, one attempt each, all 4 at any interim outcome - no call skipped
#             or added by a result): pm4c140<x> refuses (rc 1 "previous call not made") before any guard and before the
#             lock while the attempt of the call before it in SEQ (its attempt marker or its <tag>.json) does not exist.
#   ONE ATTEMPT (item 66 (a); every tag of session 140): right before enter_scene.py starts (inside the lock, after the
#             install) the chain writes attempt_<tag>.txt; while the marker or <tag>.json exists every later call of
#             that tag refuses rc 1 ("attempt already made") before any guard, lock or install.  The only exception:
#             the idle refusal INSIDE enter_scene.py (rc 3, <tag>.refused.json, no <tag>.json) moves the marker to
#             old/<ts>_<tag>/ and ends BUSY (rc 4).  rc 3 WITH <tag>.json is an attempt made: the marker stays, the
#             checks (and for REG the scorer) run, the call ends rc 1.
#   THE SEAL'S CALL (item 105 (v)): a pm4c140 call is verbatim from the seal.  PRED carries exactly one line
#             "go140a call: PLWAIT=<n> bash C:/kyty/s140/go140a.sh <tag>" per pm4c140 call; the chain logs its PLWAIT in
#             every call and a REG call whose PLWAIT differs from that line (or finds no such line, or two) refuses rc 1
#             ("PLWAIT differs from the seal") before any guard and before the lock.
#   PROTCEIL ONLY 0 (item 93 (b)): a word protceil=<v> other than protceil=0 in the base refuses the call (rc 1,
#             "protceil refused") before DRY and any guard.
# INSTALL AND RESTORE: the build is installed inside the lock (its sha checked before the lock, inside the lock and after
#   the copy); on EVERY exit after the install the EXIT trap copies back RESTORE - the pinned copy of the INSTALLED build
#   9235a7ac - checks the sha and removes the lock.  A failed restore (3 tries RSLEEP s apart) logs "RESTORE FAILED" and
#   ends rc 1.
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0; KYTY_GPU_CHECKPOINTS, KYTY_GPU_WALL and KYTY_REC are never passed
#   (enter_scene.py drops every KYTY_* of the shell; envchk140.py checks <tag>.json afterwards).
# ONE IDLE CRITERION (item 25 (zh)): idle140.py; enter_scene.py --require-idle refuses inside (rc 3, no emulator).  The CPU
#   check is the chain's own extra.  A live emulator process counts as busy (the name guard).
# EXIT CODES (item 41 (a), kept): 0 run done (hostdev, envchk and - REG - the scorer ran; read their files);  1 hard refusal
#   or failed run (attempt already made, previous call not made, PLWAIT of the seal, protceil, build/restore copy or its
#   sha, base sha, pred sha, pre-seal check, install, enter_scene failure, failed restore);  2 not configured / usage;
#   4 BUSY - lock held (checked first, in every call), procload/name guard not clean within PLWAIT, CPU >= 15, idle140 not
#   IDLE, the lock taken between the check and the take, or the idle refusal inside enter_scene.py: no run.
# PLWAIT (seconds, default and maximum 540 = PLMAX, item 40 (e)(4)): the procload wait of the first guard; above PLMAX or
#   not a number refuses (rc 2).  The second guard (right before the lock and the install) waits 0.
# After the run: hostdev140.py (unpadded), envchk140.py, and for REG the scorer with --tag <call> --out
#   C:/kyty/s140/runs140/<tag>.score.json (item 40 (e)(6); the per-call form prints no level, RC7 of review140).
#   Stale artefacts move to old/<ts>_<tag>/.
#   DRY=1 go140a.sh <tag> prints the plan and exits 0 (after the lock check, before any other check, lock or install).
#   usage: go140a.sh <tag>
T=${1:-}
BASESHA="573ae9d2f24944c4fa92a14070645e3fe5b21bd6ee3365502e6ba768c0087fbc"
BUILD_EXPECT="05431dad252676b05128828a42169de0c1f84aff799838a513a0d80b32afcd84"
BUILD_PINNED="/c/kyty/s136/kyty_emulator_05431dad.exe"
PRED=""
SC=""
SHOLD="120"
PHOLD="300"
SEQ="pm4c140a pm4c140b pm4c140c pm4c140d"
RESTORE="/c/kyty/s128/kyty_emulator_9235a7ac.exe"
RESTORE_SHA="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
RSLEEP=5
PLMAX=540
PLWAIT=${PLWAIT:-$PLMAX}
case "$T" in
  pm4s140|pm4c140a|pm4c140b|pm4c140c|pm4c140d) LEVEL=underwater_aerial_garden;;
  *) echo "usage: go140a.sh pm4s140|pm4c140a|pm4c140b|pm4c140c|pm4c140d  (see the header)"; exit 2;;
esac
ROOT=C:/kyty/s140
L=$ROOT/go140a.log
LOCK=/c/kyty/SEALED_RUN.lock
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
PROCLOAD=$ROOT/procload.py
IDLE=$ROOT/idle140.py
HOSTDEV=$ROOT/hostdev140.py
ENVCHK=$ROOT/envchk140.py
BASEGATES=$ROOT/gates_base.txt
OUT=$ROOT/runs140
MARK=attempt_$T.txt
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
busy() { log "go140a.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
# ROADMAP s122 item 76 (b): the lock before any process - bash builtins only ([ -e ], read, printf, echo, exit).
lockheld() {
  if [ -e $LOCK ]; then
    LOCKTXT=""
    read -r LOCKTXT < $LOCK 2>/dev/null
    busy "lock held: $LOCKTXT"
  fi
}
lockheld
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA
if [ -z "$BUILD_EXPECT" ] || [ -z "$BUILD_PINNED" ]; then
  log "go140a.sh $T refused: the build not set (item 210 (e)(3))"; echo "not pinned yet"; exit 2
fi
if ! [[ $BASESHA =~ ^[0-9a-f]{64}$ ]] || ! [[ $BUILD_EXPECT =~ ^[0-9a-f]{64}$ ]]; then
  log "go140a.sh $T refused: BASESHA or the build sha is not 64 hex digits"; echo "bad EXPECT"; exit 2
fi
case "$PLWAIT" in
  ''|*[!0-9]*) log "go140a.sh $T refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then
  log "go140a.sh $T refused: PLWAIT $PLWAIT > $PLMAX (ROADMAP s122 item 40 (e)(4))"; echo "PLWAIT above $PLMAX"; exit 2
fi
GATES=$BASEGATES
EXTRA=""
REG=0
ONE=1
SD="--stable-draws 300 --timeout 480"
ENVX="--census --no-rec --base-is $BASEGATES"
case "$T" in
  pm4s140)
    HOLD=$SHOLD; EXTRA="KYTY_PM4_TRACE=1";;
  pm4c140a)
    REG=1; HOLD=$PHOLD; EXTRA="KYTY_PM4_TRACE=0";;
  pm4c140b)
    REG=1; HOLD=$PHOLD; EXTRA="KYTY_PM4_TRACE=1";;
  pm4c140c)
    REG=1; HOLD=$PHOLD; EXTRA="KYTY_PM4_TRACE=1";;
  pm4c140d)
    REG=1; HOLD=$PHOLD; EXTRA="KYTY_PM4_TRACE=0";;
esac
# ROADMAP s122 item 93 (b): protceil is 0 (its value 1 hangs the GPU) - a word protceil=<v> other than protceil=0 in the
# base is refused (rc 1) before DRY and any guard; bash builtins only (the lock was checked above).
PC=0
GW=()
if [ -f "$BASEGATES" ]; then IFS=$' \t\r\n' read -r -d '' -a GW < "$BASEGATES"; fi
for PWORD in "${GW[@]}"; do
  case "$PWORD" in protceil=0) ;; protceil=*) PC=1;; esac
done
if [ "$PC" = "1" ]; then
  log "go140a.sh $T refused: protceil other than 0 in the base $BASEGATES (ROADMAP s122 item 93 (b))"
  echo "protceil refused"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY $T: lock?; PLWAIT=$PLWAIT; procload --wait-s $PLWAIT; cpu < 15; idle140; procload --wait-s 0; lock (runs140/lock.log UTC); install $BUILD_PINNED ($BUILD_EXPECT); enter_scene.py $T --level $LEVEL --attempts 1 $SD --no-install --require-idle --gates-file $GATES --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (no KYTY_GATE_SCHEDULE); hostdev140 $T --pad 0; envchk140 $ENVX (registered $REG, one attempt $ONE); scorer ${SC:-<seal>} --tag $T --out $OUT/$T.score.json (registered only); restore $RESTORE ($RESTORE_SHA)"
  exit 0
fi
if [ "$REG" = "1" ] && { [ -z "$PRED" ] || [ -z "$SC" ]; }; then
  log "go140a.sh $T refused: registered tag without PRED/SC (the seal of step 2 sets them)"; echo "not sealed yet"; exit 2
fi
if [ "$REG" = "1" ]; then
  # ROADMAP s122 item 105 (v): the call of a registered tag is verbatim from the seal - its PLWAIT line, exactly one.
  SEALPL=$(grep -x "go140a call: PLWAIT=[0-9][0-9]* bash C:/kyty/s140/go140a.sh $T" "$PRED" 2>/dev/null | cut -d= -f2 | cut -d' ' -f1)
  if [ -z "$SEALPL" ] || [ "$SEALPL" != "$PLWAIT" ]; then
    log "go140a.sh $T refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (seal: '${SEALPL//$'\n'/,}', ROADMAP s122 item 105 (v))"
    echo "PLWAIT differs from the seal"; exit 1
  fi
  log "go140a.sh $T PLWAIT=$PLWAIT = the call line of the seal $PRED (ROADMAP s122 item 105 (v))"
fi
case "$HOLD" in
  ''|0|*[!0-9]*) log "go140a.sh $T refused: hold '$HOLD' is not a number of seconds"; echo "bad hold"; exit 2;;
esac
if [ "$ONE" = "1" ] && { [ -e "$MARK" ] || [ -e "$T.json" ]; }; then
  log "go140a.sh $T refused: $MARK or $T.json exists - the one attempt of $T was made (a repeat needs a ROADMAP line)"
  echo "attempt already made"; exit 1
fi
if [ "$REG" = "1" ]; then
  # ROADMAP s122 item 210 (e)(4): the 4 calls in the order of SEQ, none skipped.
  PREV=""
  P=""
  for C in $SEQ; do
    if [ "$C" = "$T" ]; then PREV=$P; fi
    P=$C
  done
  if [ -n "$PREV" ] && [ ! -e "attempt_$PREV.txt" ] && [ ! -e "$PREV.json" ]; then
    log "go140a.sh $T refused: the call $PREV before it was not made (ROADMAP s122 item 210 (e)(4): the 4 calls in order)"
    echo "previous call not made"; exit 1
  fi
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then
  log "go140a.sh $T refused: pinned copy $BUILD_PINNED missing or its sha != $BUILD_EXPECT - not starting"; echo "pinned build bad"; exit 1
fi
if [ ! -f "$RESTORE" ] || [ "$(sha "$RESTORE")" != "$RESTORE_SHA" ]; then
  log "go140a.sh $T refused: restore copy $RESTORE missing or its sha != $RESTORE_SHA - not starting"; echo "restore build bad"; exit 1
fi
if [ "$(sha "$BASEGATES")" != "$BASESHA" ]; then
  log "go140a.sh $T refused: $BASEGATES sha != $BASESHA - not starting"; echo "base gate file bad"; exit 1
fi
# 2026-09-26: the agent shell inherits an environment WITHOUT %ProgramFiles%; nvml.dll then fails to
# initialise ("Failed to initialize NVML: Unknown Error") while Vulkan keeps working.  Restoring the
# variable is the whole fix.  Exported here so nvidia-smi (idle140.py, the clock logger) inherits it.
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9]*140|test_[a-z0-9]*140|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
guards() {
  python $PROCLOAD --wait-s "$1" >> $L 2>&1 || { log "a process stays busy (or the mutation harness lives) after $1 s"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
  return 0
}
log "go140a.sh $T requested (level $LEVEL, registered $REG, one attempt $ONE, build $BUILD_EXPECT, gates $GATES, extra '$EXTRA', PLWAIT=$PLWAIT)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
PREDARG=""
if [ "$REG" = "1" ]; then
  NSHA=$(sha $PRED)
  PSHA=$(grep -o "^PRED_SHA = '[0-9a-f]*'" $SC | cut -d"'" -f2)
  if [ -z "$PSHA" ] || [ "$PSHA" != "$NSHA" ]; then log "pred sha $NSHA != $SC PRED_SHA '$PSHA' - not starting"; exit 1; fi
  PREDARG="--pred $ROOT/$PRED"
  if ! python $ROOT/$SC --check-seal --tag $T >> $L 2>&1; then
    log "$SC --check-seal refused the pre-seal check (see above) - not starting"; exit 1
  fi
fi
lockheld
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
log "idle check cpu=$CPU (chain-only, < 15)"
case "$CPU" in
  ''|*[!0-9]*) busy "machine not idle (cpu='$CPU')";;
esac
if [ "$CPU" -ge 15 ]; then busy "machine not idle (cpu='$CPU')"; fi
lockheld
# The GPU idle check: the scorer's measurement and threshold (idle140.py); exit 0 IDLE, 1 BUSY, 2 UNAVAILABLE.
python $IDLE >> $L 2>&1
IDLE_RC=$?
if [ "$IDLE_RC" -ne 0 ]; then busy "machine not idle by idle140 (rc $IDLE_RC; is ProgramFiles exported? see s122 FACTS.md 4)"; fi
lockheld
guards 0 || busy "procload / name guard not clean before the lock"
mkdir -p $OUT
set -o noclobber
if ! { echo "go140a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  busy "lock taken by someone else: $(cat $LOCK 2>/dev/null)"
fi
set +o noclobber
echo "lock taken $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
INSTALLED=0
restore() {
  for i in 1 2 3; do
    if cp "$RESTORE" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$RESTORE_SHA" ]; then return 0; fi
    sleep $RSLEEP
  done
  return 1
}
finish() {
  RCX=$?
  if [ "$INSTALLED" = "1" ]; then
    if restore; then
      log "restored $RESTORE ($RESTORE_SHA) into $GAME"
    else
      log "RESTORE FAILED: $GAME sha $(sha "$GAME") != $RESTORE_SHA - restore it by hand before any run"
      echo "restore failed"
      RCX=1
    fi
  fi
  rm -f $LOCK
  echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
  exit $RCX
}
trap finish EXIT
[ "$(sha "$BUILD_PINNED")" = "$BUILD_EXPECT" ] || { log "pinned copy sha != $BUILD_EXPECT inside the lock - stop"; exit 1; }
log "installed before: $(sha "$GAME")"
INSTALLED=1
cp "$BUILD_PINNED" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$BUILD_EXPECT" ] || { log "installed sha != $BUILD_EXPECT - stop"; exit 1; }
SCF=""
if [ "$REG" = "1" ]; then SCF="$SC test_${SC} mut_${SC} $PRED"; fi
log "files: $(sha256sum $SCF gates_base.txt enter_scene.py idle140.py envchk140.py procload.py hostdev140.py go140a.sh "$BUILD_PINNED" | cut -c1-16,65- | tr '\n' ';')"
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "$T.refused.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" "hostdev_$T.txt" "envchk_$T.txt" \
         "score_$T.txt" "runs140/$T.score.json" log_${T}_a*.txt stdout_${T}_a*.txt; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
echo "go140a.sh $T pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) build $BUILD_EXPECT" > $MARK
log "$T start (level $LEVEL, hold $HOLD, gates $GATES, extra '$EXTRA')"
python $ROOT/enter_scene.py $T --level $LEVEL --attempts 1 $SD --no-install --require-idle --gates-file $GATES $PREDARG \
  --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
RC=$?
log "$T rc=$RC $(tail -1 $T.stdout.txt)"
if [ "$RC" = "3" ] && [ -e "$T.json" ]; then
  log "rc 3 with $T.json: the one attempt of $T was made (ROADMAP s122 item 66 (a)) - checked (and scored), rc 1"
elif [ "$RC" = "3" ]; then
  if [ -f "$T.refused.json" ]; then
    mkdir -p "$OLD"; mv "$MARK" "$OLD/" && log "idle refusal inside enter_scene: no attempt made, marker moved to $OLD/"
  fi
  busy "the idle criterion inside enter_scene.py refused (see $T.refused.json) - no run"
fi
# ROADMAP s.122 item 17 (a): the host-event witness over launched .. finished of $T.json, unpadded; a row beside the
# run.  Offline: GPU and build untouched.
python $HOSTDEV $T --pad 0 > hostdev_$T.txt 2>&1
log "hostdev $T rc=$? $(grep '^VERDICT:' hostdev_$T.txt | head -1)"
python $ENVCHK $T.json $ENVX > envchk_$T.txt 2>&1
log "envchk $T rc=$? $(head -1 envchk_$T.txt)"
log "hold_gpu $T $(grep '^hold_gpu:' $T.stdout.txt | tail -1)"
if [ "$REG" = "1" ]; then
  # ROADMAP s.122 item 40 (e)(6): the structured output of the scorer is archived beside the run.
  python $ROOT/$SC --tag $T --out $OUT/$T.score.json > score_$T.txt 2>&1
  log "score $T rc=$? out $OUT/$T.score.json $(grep -m1 '^VERDICT' score_$T.txt)"
fi
log "done"
[ "$RC" = "0" ] || exit 1
exit 0
