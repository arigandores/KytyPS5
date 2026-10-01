#!/bin/bash
# Session 143 step 0 (HPP-297; ROADMAP s.0.1 "SESSION 122" item 231 (i)(1)-(6); brief docs/next-session-143.md):
# the game chain of the SCENE_OK series sc143 on ten never-entered main levels, on the INSTALLED build 9235a7ac with its
# shipped defaults (an EMPTY gate file: every gate and knob keeps the build's own default, the rule of session 63).
# Port of C:/kyty/s142/go142a.sh (lock first, guards, one attempt, order, seal call line, stop rule, shader cache count)
# with the tag pairs of item 231 (i)(2) and the foreign-CPU row of debt D-4 (item 231 (i)(4), (l)).
# ASCII only (item 175 (v)).  No emulator code, no build (item 231 (i)).
#   TAGS AND ORDER (item 231 (i)(1)-(2): per level V then W, the levels in the order of (i)(1); one call each):
#     v143_NN   the level NN, video (KYTY_REC), hold VHOLD s from "stable" (as v142: the presented time after the first
#               scene frame must reach >= 300 s - the scorer measures it by the sum of dt_us, item 221 (g)(3)); the
#               first entry of the level, so it is also the census entry of the level (map row (A), forms B5/B5a/B33)
#     w143_NN   the same entry with --vulkan-validation true (VK_LAYER_PATH), no video, hold WHOLD s
#     NN = 01..10: spring_punch_sky_aztec booster_construction mini_astro_clock_tower path_maker_mana_tree
#               spring_punch_monster_cave gulliver_island rocket_hourglass pot_treasure_cave booster_magic_lamp
#               rocket_space_station
#     --stable-draws 300 for V and W (item 223 (a)(6): "300 for V and W"; on the ten s142 census logs 90 frames of
#     draws >= 300 come at the same frame as with 100, +-2 frames - step 0 data)
#   ONE ATTEMPT (item 231 (i)(2): --attempts 1, a failure is data, no repeat): attempt_<tag>.txt is written inside the lock
#     right before enter_scene.py; while it or <tag>.json exists every later call of the tag refuses rc 1.  The only
#     exception: the idle refusal inside enter_scene.py (rc 3 without <tag>.json) moves the marker to old/ and ends rc 4.
#   ORDER: a call refuses rc 1 while the call before it in SEQ has neither its marker nor its <tag>.json.
#   STOP RULE (item 231 (i)(4)): every call refuses rc 5 ("stop, question to the lead") when sc143.py --stop-check finds
#     three V in a row "not entered" with one marker before it.
#   STOP FILE (general rule 26): C:/kyty/s143/STOP present -> rc 4 before anything else and again right before the lock.
#   THE SEAL'S CALL (item 105 (v)): the seal carries exactly one line "go143a call: PLWAIT=<n> bash C:/kyty/s143/go143a.sh
#     <tag>" per tag; another PLWAIT (or no line, or two) refuses rc 1.  sc143.py --check-seal checks every sha line of the
#     seal (this file, the scorer, fixtures, mutants, enter_scene.py, s51_vidglitch.py, sheet142.py, ...) before the lock.
#   THE LOCK is checked before any process in every call (DRY included) and again before every guard stage; the take and
#     the release are written "lock taken|released <tag> <UTC>" into runs143/lock.log; every step event goes as one UTC
#     line into step2/times.txt by this script at the moment of the event (general rule 23).
#   After the run (inside the lock): the log sha256 line, s51_vidglitch.py 4 6 and sheet142.py for a video tag, the scorer
#     sc143.py --tag <tag> into score_<tag>.txt; the EXIT trap copies the pinned 9235a7ac back, writes the foreign-CPU
#     row (fgcpu143.py: the run average of the processes alive at the lock and at the end, and a 10 s sample now) into
#     step2/times.txt, and removes the lock.  The count of files of the shared translation cache _ShaderCache/PPSA21564
#     goes into step2/times.txt before the lock and after the run (item 224 (a)(10)).
#   BUSY (rc 4) lines carry the process name of the "procload: busy" line of go143a.log (item 231 (z)(5)).
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, --pred of the seal; KYTY_GPU_CHECKPOINTS never passed.
# EXIT CODES: 0 run done (read score_<tag>.txt);  1 hard refusal or failed run;  2 usage / not configured;  4 BUSY (lock,
#   stop file, guards, idle) - no run;  5 the stop rule of item 231 (i)(4) - no run, question to the lead.
#   DRY=1 go143a.sh <tag> prints the plan and exits 0 after the cheap refusals, before any guard, lock or install.
#   usage: go143a.sh <tag>
T=${1:-}
ROOT=C:/kyty/s143
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s143/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
VKDUP="1000000"
PRED="pred/01_sc143.md"
CACHE="/c/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564"
SC="sc143.py"
VHOLD="330"
WHOLD="310"
SEQ="v143_01 w143_01 v143_02 w143_02 v143_03 w143_03 v143_04 w143_04 v143_05 w143_05 v143_06 w143_06 v143_07 w143_07 v143_08 w143_08 v143_09 w143_09 v143_10 w143_10"
RSLEEP=5
PLMAX=540
PLWAIT=${PLWAIT:-$PLMAX}
case "$T" in
  v143_01|w143_01) LEVEL=spring_punch_sky_aztec;;
  v143_02|w143_02) LEVEL=booster_construction;;
  v143_03|w143_03) LEVEL=mini_astro_clock_tower;;
  v143_04|w143_04) LEVEL=path_maker_mana_tree;;
  v143_05|w143_05) LEVEL=spring_punch_monster_cave;;
  v143_06|w143_06) LEVEL=gulliver_island;;
  v143_07|w143_07) LEVEL=rocket_hourglass;;
  v143_08|w143_08) LEVEL=pot_treasure_cave;;
  v143_09|w143_09) LEVEL=booster_magic_lamp;;
  v143_10|w143_10) LEVEL=rocket_space_station;;
  *) echo "usage: go143a.sh v143_01|w143_01 .. v143_10|w143_10  (see the header)"; exit 2;;
esac
L=$ROOT/go143a.log
OUT=$ROOT/runs143
TIMES=$ROOT/step2/times.txt
MARK=attempt_$T.txt
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
busy() { log "go143a.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
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
  ''|*[!0-9]*) log "go143a.sh $T refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then
  log "go143a.sh $T refused: PLWAIT $PLWAIT > $PLMAX (ROADMAP s122 item 40 (e)(4))"; echo "PLWAIT above $PLMAX"; exit 2
fi
if [ -e "$MARK" ] || [ -e "$T.json" ]; then
  log "go143a.sh $T refused: $MARK or $T.json exists - the one attempt of $T was made (item 231 (i)(2): no repeat)"
  echo "attempt already made"; exit 1
fi
PREV=""
P=""
for C in $SEQ; do
  if [ "$C" = "$T" ]; then PREV=$P; fi
  P=$C
done
if [ -n "$PREV" ] && [ ! -e "attempt_$PREV.txt" ] && [ ! -e "$PREV.json" ]; then
  log "go143a.sh $T refused: the call $PREV before it was not made (item 231 (i)(1)-(2): per level V then W, the levels in order)"
  echo "previous call not made"; exit 1
fi
SD=""
HOLD=""
REC=""
EMUX=""
EXTRA=""
case "$T" in
  v143_*) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec";;
  w143_*) SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD
          EMUX="--emu-arg=--vulkan-validation --emu-arg=true"
          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP";;
esac
# ROADMAP s122 item 105 (v): the call is verbatim from the seal - its PLWAIT line, exactly one.
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go143a call: PLWAIT="*" bash C:/kyty/s143/go143a.sh $T")
        V=${PLINE#go143a call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go143a.sh $T refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL', ROADMAP s122 item 105 (v))"
  echo "PLWAIT differs from the seal"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY $T: level $LEVEL; stop file?; lock?; PLWAIT=$PLWAIT; procload --wait-s $PLWAIT; $SC --check-seal; $SC --stop-check $T; cpu < 15; idle142; procload --wait-s 0; stop file?; shader cache count; lock (runs143/lock.log UTC); fgcpu143 --save; install $BUILD_PINNED ($BUILD_EXPECT); enter_scene.py $T --level $LEVEL --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0; log sha; glitch+sheet ${REC:-none}; $SC --tag $T; restore $BUILD_PINNED; fgcpu143 --since (times.txt row); unlock"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then
  log "go143a.sh $T refused: pinned copy $BUILD_PINNED missing or its sha != $BUILD_EXPECT - not starting"; echo "pinned build bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go143a.sh $T refused: gates_default.txt is not the empty file - not starting"; echo "gate file bad"; exit 1
fi
# 2026-09-26: the agent shell inherits an environment WITHOUT %ProgramFiles%; nvml.dll then fails to initialise while
# Vulkan keeps working.  Exported here so nvidia-smi (idle142.py, the clock logger) inherits it.
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
mkdir -p $OUT step2
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*143|test_[a-z0-9_]*143|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  # item 231 (z)(5): the BUSY row of step2/times.txt names the process of the last "procload: busy" line of go143a.log,
  # read by the same command that writes the row.
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)" >> $TIMES
}
guards() {
  python $ROOT/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy (or the mutation harness lives) after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
  return 0
}
log "go143a.sh $T requested (level $LEVEL, build $BUILD_EXPECT, empty gate file, hold $HOLD, PLWAIT=$PLWAIT)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $ROOT/$SC --check-seal >> $L 2>&1; then
  log "$SC --check-seal refused (see above) - not starting"; echo "seal check failed"; exit 1
fi
python $ROOT/$SC --stop-check $T >> $L 2>&1
SRC=$?
if [ "$SRC" = "5" ]; then
  log "go143a.sh $T refused (rc 5): the stop rule of item 231 (i)(4) - three V in a row not entered with one marker; question to the lead"
  echo "stop rule"; exit 5
fi
if [ "$SRC" != "0" ]; then log "stop-check rc $SRC - not starting"; echo "stop-check failed"; exit 1; fi
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
cachen() { local n=0 f; for f in "$CACHE"/*; do [ -e "$f" ] && n=$((n+1)); done; echo $n; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T shader cache files before the lock $(cachen) ($CACHE)" >> $TIMES
set -o noclobber
if ! { echo "go143a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
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
  # item 231 (i)(4), debt D-4: the foreign-CPU row at the end of every run, still inside the lock.
  FG=$(python $ROOT/fgcpu143.py --since $OUT/fgcpu_$T.a.json 2>&1 | tail -1 | tr -d '\r')
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T foreign cpu at the end inside the lock: $FG" >> $TIMES
  rm -f $LOCK
  echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
  exit $RCX
}
trap finish EXIT
python $ROOT/fgcpu143.py --save $OUT/fgcpu_$T.a.json >> $L 2>&1
log "installed before: $(sha "$GAME")"
INSTALLED=1
cp "$BUILD_PINNED" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$BUILD_EXPECT" ] || { log "installed sha != $BUILD_EXPECT - stop"; exit 1; }
log "files: $(sha256sum $SC test_$SC mut_$SC $PRED gates_default.txt enter_scene.py idle142.py procload.py go143a.sh sheet142.py fgcpu143.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "$T.refused.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" \
         "rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt" "runs143/$T.score.json" \
         log_${T}_a*.txt stdout_${T}_a*.txt; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
echo "go143a.sh $T pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) build $BUILD_EXPECT" > $MARK
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T enter_scene start (level $LEVEL, hold $HOLD)" >> $TIMES
log "$T start (level $LEVEL, hold $HOLD, empty gate file, emu '$EMUX', extra '$EXTRA')"
python $ROOT/enter_scene.py $T --level $LEVEL --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt \
  --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
RC=$?
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T enter_scene end rc $RC log_$T.txt sha256 $(sha log_$T.txt)" >> $TIMES
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T shader cache files after the run $(cachen) ($CACHE)" >> $TIMES
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
    GRC=$?
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T s51_vidglitch rc $GRC glitch_$T.txt sha256 $(sha glitch_$T.txt) rec_$T.mp4 sha256 $(sha rec_$T.mp4)" >> $TIMES
    python $ROOT/sheet142.py rec_$T.mp4 sheet_$T.png > sheet_$T.txt 2>&1
    SHRC=$?
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T sheet rc $SHRC sheet_$T.png sha256 $(sha sheet_$T.png)" >> $TIMES
  else
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T no video rec_$T.mp4" >> $TIMES
  fi
fi
python $ROOT/$SC --tag $T > score_$T.txt 2>&1
SCRC=$?
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T scorer rc $SCRC score_$T.txt sha256 $(sha score_$T.txt)" >> $TIMES
log "scorer $T rc=$SCRC $(head -1 score_$T.txt)"
if [ "$RC" != "0" ]; then exit 1; fi
exit 0
