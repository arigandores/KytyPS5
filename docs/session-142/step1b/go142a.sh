#!/bin/bash
# Session 142 step 0 (HPP-277; ROADMAP s.0.1 "SESSION 122" item 221 (g)(1)-(5), (v); brief docs/next-session-142.md):
# the game chain of the scene census sc142 and of the SCENE_OK attempt on Sky Garden, on the INSTALLED build 9235a7ac with
# its shipped defaults (an EMPTY gate file: every gate and knob keeps the build's own default, the rule of session 63).
# Port of C:/kyty/s140/go140a.sh (lock first, guards, one attempt, order, seal call line) with the tag set of item 221 (g).
# ASCII only (item 175 (v)).  No emulator code, no build (item 221).
#   TAGS AND ORDER (item 221 (g)(4): V, W, then the ten levels of (g)(1) in that order; one call each; none skipped):
#     v142      Sky Garden underwater_aerial_garden, video (KYTY_REC), hold VHOLD s from "stable" so that the presented
#               time after the first scene frame reaches >= 300 s (the scorer measures it by the sum of dt_us, item 221
#               (g)(3); enter_scene.py counts its hold from its "stable", not from the first scene frame)
#     w142      the same entry with --vulkan-validation true (VK_LAYER_PATH), no video, hold WHOLD s (>= 300)
#     c142_01..c142_10  bumper_enemy_snowy_canyon big_hand_pirate_island timestop_casino mini_giants_garden ice_iceberg
#               sponge_dirty_bath hoover_beach volcano_mountain voxel_world enemy_gorilla - video, hold CHOLD s after
#               "stable" (>= 120 s after the entry line), stable-draws 100 (the draws threshold of the first scene frame,
#               item 218 (g)), no validation
#   ONE ATTEMPT (item 221 (g)(1): --attempts 1, a failure is data, no repeat): attempt_<tag>.txt is written inside the lock
#     right before enter_scene.py; while it or <tag>.json exists every later call of the tag refuses rc 1.  The only
#     exception: the idle refusal inside enter_scene.py (rc 3 without <tag>.json) moves the marker to old/ and ends rc 4.
#   ORDER: a call refuses rc 1 while the call before it in SEQ has neither its marker nor its <tag>.json.
#   STOP RULE (item 221 (g)(4)): a census call refuses rc 5 ("stop, question to the lead") when sc142.py --stop-check finds
#     three census levels in a row "not entered" with one marker.
#   STOP FILE (general rule 26): C:/kyty/s142/STOP present -> rc 4 before anything else and again right before the lock.
#   THE SEAL'S CALL (item 105 (v)): the seal carries exactly one line "go142a call: PLWAIT=<n> bash C:/kyty/s142/go142a.sh
#     <tag>" per tag; another PLWAIT (or no line, or two) refuses rc 1.  sc142.py --check-seal checks every sha line of the
#     seal (this file, the scorer, fixtures, mutants, enter_scene.py, s51_vidglitch.py, ...) before the lock.
#   THE LOCK is checked before any process in every call (DRY included) and again before every guard stage; the take and
#     the release are written "lock taken|released <tag> <UTC>" into runs142/lock.log; every step event goes as one UTC
#     line into step2/times.txt by this script at the moment of the event (general rule 23).
#   After the run (inside the lock): the log sha256 line, s51_vidglitch.py 4 6 and sheet142.py for a video tag, the scorer
#     sc142.py --tag <tag> into score_<tag>.txt; the EXIT trap copies the pinned 9235a7ac back and removes the lock.
#   Link 1b (HPP-282, item 224 (a)(10)): the seal is pred/02_sc142.md (01 replaced); the count of files of the shared
#     translation cache _ShaderCache/PPSA21564 goes into step2/times.txt before the lock and after the run (the caches
#     are shared and warm from earlier runs, V and W included - the census is the first entry of each level, not a
#     cold cache).
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, --pred of the seal; KYTY_GPU_CHECKPOINTS never passed.
# EXIT CODES: 0 run done (read score_<tag>.txt);  1 hard refusal or failed run;  2 usage / not configured;  4 BUSY (lock,
#   stop file, guards, idle) - no run;  5 the stop rule of item 221 (g)(4) - no run, question to the lead.
#   DRY=1 go142a.sh <tag> prints the plan and exits 0 after the cheap refusals, before any guard, lock or install.
#   usage: go142a.sh <tag>
T=${1:-}
ROOT=C:/kyty/s142
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s142/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
VKDUP="1000000"
PRED="pred/02_sc142.md"
CACHE="/c/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564"
SC="sc142.py"
VHOLD="330"
WHOLD="310"
CHOLD="120"
SEQ="v142 w142 c142_01 c142_02 c142_03 c142_04 c142_05 c142_06 c142_07 c142_08 c142_09 c142_10"
RSLEEP=5
PLMAX=540
PLWAIT=${PLWAIT:-$PLMAX}
case "$T" in
  v142|w142) LEVEL=underwater_aerial_garden;;
  c142_01) LEVEL=bumper_enemy_snowy_canyon;;
  c142_02) LEVEL=big_hand_pirate_island;;
  c142_03) LEVEL=timestop_casino;;
  c142_04) LEVEL=mini_giants_garden;;
  c142_05) LEVEL=ice_iceberg;;
  c142_06) LEVEL=sponge_dirty_bath;;
  c142_07) LEVEL=hoover_beach;;
  c142_08) LEVEL=volcano_mountain;;
  c142_09) LEVEL=voxel_world;;
  c142_10) LEVEL=enemy_gorilla;;
  *) echo "usage: go142a.sh v142|w142|c142_01..c142_10  (see the header)"; exit 2;;
esac
L=$ROOT/go142a.log
OUT=$ROOT/runs142
TIMES=$ROOT/step2/times.txt
MARK=attempt_$T.txt
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
busy() { log "go142a.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
# general rule 26: the stop file first (bash builtins only).
if [ -e $STOPF ]; then
  STOPTXT=""
  read -r STOPTXT < $STOPF 2>/dev/null
  busy "stop file $STOPF: $STOPTXT"
fi
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
case "$PLWAIT" in
  ''|*[!0-9]*) log "go142a.sh $T refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then
  log "go142a.sh $T refused: PLWAIT $PLWAIT > $PLMAX (ROADMAP s122 item 40 (e)(4))"; echo "PLWAIT above $PLMAX"; exit 2
fi
if [ -e "$MARK" ] || [ -e "$T.json" ]; then
  log "go142a.sh $T refused: $MARK or $T.json exists - the one attempt of $T was made (item 221 (g)(1): no repeat)"
  echo "attempt already made"; exit 1
fi
PREV=""
P=""
for C in $SEQ; do
  if [ "$C" = "$T" ]; then PREV=$P; fi
  P=$C
done
if [ -n "$PREV" ] && [ ! -e "attempt_$PREV.txt" ] && [ ! -e "$PREV.json" ]; then
  log "go142a.sh $T refused: the call $PREV before it was not made (item 221 (g)(4): V, W, then the ten levels in order)"
  echo "previous call not made"; exit 1
fi
SD=""
HOLD=""
REC=""
EMUX=""
EXTRA=""
case "$T" in
  v142) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec";;
  w142) SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD
        EMUX="--emu-arg=--vulkan-validation --emu-arg=true"
        EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP";;
  *) SD="--stable-draws 100 --timeout 480"; HOLD=$CHOLD; REC="--rec";;
esac
# ROADMAP s122 item 105 (v): the call is verbatim from the seal - its PLWAIT line, exactly one.
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go142a call: PLWAIT="*" bash C:/kyty/s142/go142a.sh $T")
        V=${PLINE#go142a call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go142a.sh $T refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL', ROADMAP s122 item 105 (v))"
  echo "PLWAIT differs from the seal"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY $T: level $LEVEL; stop file?; lock?; PLWAIT=$PLWAIT; procload --wait-s $PLWAIT; $SC --check-seal; stop-check (census); cpu < 15; idle142; procload --wait-s 0; stop file?; shader cache count; lock (runs142/lock.log UTC); install $BUILD_PINNED ($BUILD_EXPECT); enter_scene.py $T --level $LEVEL --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0; log sha; glitch+sheet ${REC:-none}; $SC --tag $T; restore $BUILD_PINNED"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then
  log "go142a.sh $T refused: pinned copy $BUILD_PINNED missing or its sha != $BUILD_EXPECT - not starting"; echo "pinned build bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go142a.sh $T refused: gates_default.txt is not the empty file - not starting"; echo "gate file bad"; exit 1
fi
# 2026-09-26: the agent shell inherits an environment WITHOUT %ProgramFiles%; nvml.dll then fails to initialise while
# Vulkan keeps working.  Exported here so nvidia-smi (idle142.py, the clock logger) inherits it.
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*142|test_[a-z0-9_]*142|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
guards() {
  python $ROOT/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy (or the mutation harness lives) after $1 s"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
  return 0
}
log "go142a.sh $T requested (level $LEVEL, build $BUILD_EXPECT, empty gate file, hold $HOLD, PLWAIT=$PLWAIT)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $ROOT/$SC --check-seal >> $L 2>&1; then
  log "$SC --check-seal refused (see above) - not starting"; echo "seal check failed"; exit 1
fi
case "$T" in
  c142_*)
    python $ROOT/$SC --stop-check $T >> $L 2>&1
    SRC=$?
    if [ "$SRC" = "5" ]; then
      log "go142a.sh $T refused (rc 5): the stop rule of item 221 (g)(4) - three levels in a row not entered with one marker; question to the lead"
      echo "stop rule"; exit 5
    fi
    if [ "$SRC" != "0" ]; then log "stop-check rc $SRC - not starting"; echo "stop-check failed"; exit 1; fi;;
esac
lockheld
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
log "idle check cpu=$CPU (chain-only, < 15)"
case "$CPU" in
  ''|*[!0-9]*) busy "machine not idle (cpu='$CPU')";;
esac
if [ "$CPU" -ge 15 ]; then busy "machine not idle (cpu='$CPU')"; fi
lockheld
python $ROOT/idle142.py >> $L 2>&1
IDLE_RC=$?
if [ "$IDLE_RC" -ne 0 ]; then busy "machine not idle by idle142 (rc $IDLE_RC; is ProgramFiles exported?)"; fi
lockheld
guards 0 || busy "procload / name guard not clean before the lock"
if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi
mkdir -p $OUT step2
cachen() { local n=0 f; for f in "$CACHE"/*; do [ -e "$f" ] && n=$((n+1)); done; echo $n; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go142a $T shader cache files before the lock $(cachen) ($CACHE)" >> $TIMES
set -o noclobber
if ! { echo "go142a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  busy "lock taken by someone else: $(cat $LOCK 2>/dev/null)"
fi
set +o noclobber
echo "lock taken $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
INSTALLED=0
restore() {
  for i in 1 2 3; do
    if cp "$BUILD_PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$BUILD_EXPECT" ]; then return 0; fi
    sleep $RSLEEP
  done
  return 1
}
finish() {
  RCX=$?
  if [ "$INSTALLED" = "1" ]; then
    if restore; then
      log "restored $BUILD_PINNED ($BUILD_EXPECT) into $GAME"
    else
      log "RESTORE FAILED: $GAME sha $(sha "$GAME") != $BUILD_EXPECT - restore it by hand before any run"
      echo "restore failed"
      RCX=1
    fi
  fi
  rm -f $LOCK
  echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
  exit $RCX
}
trap finish EXIT
log "installed before: $(sha "$GAME")"
INSTALLED=1
cp "$BUILD_PINNED" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$BUILD_EXPECT" ] || { log "installed sha != $BUILD_EXPECT - stop"; exit 1; }
log "files: $(sha256sum $SC test_$SC mut_$SC $PRED gates_default.txt enter_scene.py idle142.py procload.py go142a.sh sheet142.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "$T.refused.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" \
         "rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt" "runs142/$T.score.json" \
         log_${T}_a*.txt stdout_${T}_a*.txt; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
echo "go142a.sh $T pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) build $BUILD_EXPECT" > $MARK
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go142a $T enter_scene start (level $LEVEL, hold $HOLD)" >> $TIMES
log "$T start (level $LEVEL, hold $HOLD, empty gate file, emu '$EMUX', extra '$EXTRA')"
python $ROOT/enter_scene.py $T --level $LEVEL --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt \
  --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
RC=$?
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go142a $T enter_scene end rc $RC log_$T.txt sha256 $(sha log_$T.txt)" >> $TIMES
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go142a $T shader cache files after the run $(cachen) ($CACHE)" >> $TIMES
log "$T rc=$RC $(tail -1 $T.stdout.txt)"
if [ "$RC" = "3" ] && [ ! -e "$T.json" ]; then
  if [ -f "$T.refused.json" ]; then
    mkdir -p "$OLD"; mv "$MARK" "$OLD/" && log "idle refusal inside enter_scene: no attempt made, marker moved to $OLD/"
  fi
  busy "the idle criterion inside enter_scene.py refused (see $T.refused.json) - no run"
fi
if [ -n "$REC" ]; then
  if [ -f "rec_$T.mp4" ]; then
    python $VIDGLITCH rec_$T.mp4 4 6 $ROOT/vidframes_$T > glitch_$T.txt 2>&1
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go142a $T s51_vidglitch rc $? glitch_$T.txt sha256 $(sha glitch_$T.txt) rec_$T.mp4 sha256 $(sha rec_$T.mp4)" >> $TIMES
    python $ROOT/sheet142.py rec_$T.mp4 sheet_$T.png > sheet_$T.txt 2>&1
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go142a $T sheet rc $? sheet_$T.png sha256 $(sha sheet_$T.png)" >> $TIMES
  else
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go142a $T no video rec_$T.mp4" >> $TIMES
  fi
fi
python $ROOT/$SC --tag $T > score_$T.txt 2>&1
SCRC=$?
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go142a $T scorer rc $SCRC score_$T.txt sha256 $(sha score_$T.txt)" >> $TIMES
log "scorer $T rc=$SCRC $(head -1 score_$T.txt)"
if [ "$RC" != "0" ]; then exit 1; fi
exit 0
