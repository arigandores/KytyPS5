#!/bin/bash
# Session 145 step 0 (HPP-350; ROADMAP s.0.1 "SESSION 122" item 273 (k)(1)-(7); brief docs/next-session-145.md): the
# game chain of the SCENE_OK series sc145 on the INSTALLED build 9235a7ac with its shipped defaults (an EMPTY gate file).
# Port of C:/kyty/s144/go144a.sh (pred/01_sc144.md): the same lock, guards, one attempt, order, seal call line, stop file,
# cache count and manifests, foreign-CPU row, winpid lock line - with the 34 tags of item 273 (k)(1), the W form of item
# 273 (k)(2) (validation, KYTY_PIPELINE_PRECACHE=0 and the filter of ONE message) and the stop rules of item 273 (k)(4).
# ASCII only.  No emulator code, no build.
#   TAGS AND ORDER (item 273 (k)(1); one call each, exactly this order):
#     w145_00            the control W on Sky Garden (underwater_aerial_garden)
#     w145_01            the W repeat of rocket_hourglass (its V is v144_09 of session 144 - the cross-session pair of
#                        item 254 (e), read by sc145.py; "Process" 1: a disturbance of the run, not an attempt of the level)
#     v145_NN, w145_NN   NN = 02..17, V then W per level, COLD first entries: small_pot_lava spin_drill_natural_cave
#                        enemy_taco jack_in_the_box final_shooting picup_light enemy_snake light_gadget_graveyard
#                        shuriken_ninja_castle final_stage mini_rocket_chain enemy_chameleon bonus_path_maker_mix enemy_bird
#                        cymbal_party_land enemy_final (last)
#   V (item 273 (k)(2)): -lvl entry, shipped defaults, video KYTY_REC, hold VHOLD=330 s, --stable-draws 300 --timeout 480,
#     --attempts 1 (the first entry of a never-entered level: the census of sc145.py goes into the cold pools).
#   W (item 254 (e), 273 (k)(2)): --vulkan-validation true with VK_LAYER_PATH and VK_LAYER_DUPLICATE_MESSAGE_LIMIT,
#     KYTY_PIPELINE_PRECACHE=0 AND VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER (the VUID string of the F6 warning, the one message
#     on which 13 W of s144 reached the duplicate limit; no other id) - positional, so enter_scene.py puts them into the env
#     and the json; no video, hold WHOLD=310 s, --stable-draws 300 --timeout 600, --attempts 1.
#   STOP RULES (item 273 (k)(4)): every call refuses rc 5 ("stop, question to the lead") when sc145.py --stop-check finds
#     the control W stopped (incl. its layer limit lines), two W in a row stopped before the first GuestOut line with one
#     key, three V in a row not entered with one marker, or a window event on the made tag right before.
#   The API check row of step 2 is written by step2/next_one.sh (step2/apichk145.py) before it starts this script; the
#     gate step2/gate145.py runs in step2/pre_one.sh; this script is called only through step2/next_one.sh.
# Session 144 header (carried):
# Session 144 step 0 (HPP-330; ROADMAP s.0.1 "SESSION 122" item 254 (e), (k)(1)-(7); brief docs/next-session-144.md): the
# game chain of the SCENE_OK series sc144 on the INSTALLED build 9235a7ac with its shipped defaults (an EMPTY gate file).
# Port of C:/kyty/s143/go143a.sh (pred/02_sc143.md, link 1b HPP-321): the same lock, guards, one attempt, order, seal call
# line, stop file, cache count and manifests, foreign-CPU row, winpid lock line - with the 33 tags of item 254 (k)(1), the
# W form of item 254 (e) and the stop rules of item 254 (k)(4).  ASCII only.  No emulator code, no build.
#   TAGS AND ORDER (item 254 (k)(1); one call each, exactly this order):
#     w144_00            the control W on Sky Garden (underwater_aerial_garden)
#     w144_01..w144_08   W only: spring_punch_sky_aztec booster_construction mini_astro_clock_tower path_maker_mana_tree
#                        spring_punch_monster_cave gulliver_island booster_magic_lamp rocket_space_station (their V is
#                        v143_NN of session 143 - the cross-session pair of item 254 (e), read by sc144.py)
#     v144_NN, w144_NN   NN = 09..20, V then W per level: rocket_hourglass pot_treasure_cave bumper_enemy_snowy_canyon
#                        big_hand_pirate_island timestop_casino ice_iceberg sponge_dirty_bath hoover_beach volcano_mountain
#                        voxel_world enemy_gorilla mini_giants_garden (last)
#   V (item 254 (k)(2)): -lvl entry, shipped defaults, video KYTY_REC, hold VHOLD=330 s, --stable-draws 300 --timeout 480,
#     --attempts 1 (a repeated entry of the level: sc144.py marks its map row).
#   W (item 254 (e), (k)(2)): --vulkan-validation true with VK_LAYER_PATH and VK_LAYER_DUPLICATE_MESSAGE_LIMIT AND
#     KYTY_PIPELINE_PRECACHE=0 (positional, so enter_scene.py puts it into the env and the json), no video, hold WHOLD=310 s,
#     --stable-draws 300 --timeout 600, --attempts 1.
#   STOP RULES (item 254 (k)(4)): every call refuses rc 5 ("stop, question to the lead") when sc144.py --stop-check finds
#     the control W stopped, two W in a row stopped before the first GuestOut line with one key, or three V in a row not
#     entered with one marker before it.
#   The API check row of step 2 (MINOR-4 of audit 143) is written by step2/next_one.sh (step2/apichk144.py) before it
#     starts this script; this script is called only through step2/next_one.sh.
# Session 143 header (carried):
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
# LINK 1b (HPP-321, item 242): the seal is pred/02_sc143.md; the lock line carries the Windows pid of this shell
#   (winpid, for lockcheck143.py - the dangling-lock rule of the seal); cachemf143.py writes the manifest of the caches
#   (_ShaderCache/PPSA21564, _PipelineCache, %LOCALAPPDATA%/NVIDIA/GLCache: name, size, mtime, sha256) into
#   runs143/cache_<tag>.before.json before the lock and runs143/cache_<tag>.after.json after the run, each with a
#   step2/times.txt line (sc143.py --summary prints the continuity per adjacent pair of tags); the foreign-CPU row
#   gets --chain-pid <winpid> (the chain and its descendants are out of the foreign terms; item 242 (a)).  Step 2
#   calls this script only through step2/next_one.sh (detached call + foreground wait, item 242 (d)).
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, --pred of the seal; KYTY_GPU_CHECKPOINTS never passed.
# EXIT CODES: 0 run done (read score_<tag>.txt);  1 hard refusal or failed run;  2 usage / not configured;  4 BUSY (lock,
#   stop file, guards, idle) - no run;  5 the stop rule of item 231 (i)(4) - no run, question to the lead.
#   DRY=1 go143a.sh <tag> prints the plan and exits 0 after the cheap refusals, before any guard, lock or install.
#   usage: go143a.sh <tag>
T=${1:-}
ROOT=C:/kyty/s145
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s145/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
VKDUP="1000000"
VKFILTER="Undefined-Value-ShaderOutputNotConsumed-DynamicRendering"
PRED="pred/01_sc145.md"
CACHE="/c/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564"
SC="sc145.py"
VHOLD="330"
WHOLD="310"
SEQ="w145_00 w145_01 v145_02 w145_02 v145_03 w145_03 v145_04 w145_04 v145_05 w145_05 v145_06 w145_06 v145_07 w145_07 v145_08 w145_08 v145_09 w145_09 v145_10 w145_10 v145_11 w145_11 v145_12 w145_12 v145_13 w145_13 v145_14 w145_14 v145_15 w145_15 v145_16 w145_16 v145_17 w145_17"
RSLEEP=5
PLMAX=540
PLWAIT=${PLWAIT:-$PLMAX}
case "$T" in
  w145_00) LEVEL=underwater_aerial_garden;;
  w145_01) LEVEL=rocket_hourglass;;
  v145_02|w145_02) LEVEL=small_pot_lava;;
  v145_03|w145_03) LEVEL=spin_drill_natural_cave;;
  v145_04|w145_04) LEVEL=enemy_taco;;
  v145_05|w145_05) LEVEL=jack_in_the_box;;
  v145_06|w145_06) LEVEL=final_shooting;;
  v145_07|w145_07) LEVEL=picup_light;;
  v145_08|w145_08) LEVEL=enemy_snake;;
  v145_09|w145_09) LEVEL=light_gadget_graveyard;;
  v145_10|w145_10) LEVEL=shuriken_ninja_castle;;
  v145_11|w145_11) LEVEL=final_stage;;
  v145_12|w145_12) LEVEL=mini_rocket_chain;;
  v145_13|w145_13) LEVEL=enemy_chameleon;;
  v145_14|w145_14) LEVEL=bonus_path_maker_mix;;
  v145_15|w145_15) LEVEL=enemy_bird;;
  v145_16|w145_16) LEVEL=cymbal_party_land;;
  v145_17|w145_17) LEVEL=enemy_final;;
  *) echo "usage: go145a.sh w145_00 | w145_01 | v145_02|w145_02 .. v145_17|w145_17  (see the header)"; exit 2;;
esac
L=$ROOT/go145a.log
OUT=$ROOT/runs145
TIMES=$ROOT/step2/times.txt
MARK=attempt_$T.txt
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
busy() { log "go145a.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
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
WINPID=""
read -r WINPID < /proc/$$/winpid 2>/dev/null
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA
case "$PLWAIT" in
  ''|*[!0-9]*) log "go145a.sh $T refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then
  log "go145a.sh $T refused: PLWAIT $PLWAIT > $PLMAX (ROADMAP s122 item 40 (e)(4))"; echo "PLWAIT above $PLMAX"; exit 2
fi
if [ -e "$MARK" ] || [ -e "$T.json" ]; then
  log "go145a.sh $T refused: $MARK or $T.json exists - the one attempt of $T was made (item 273 (k)(2): --attempts 1, no repeat)"
  echo "attempt already made"; exit 1
fi
PREV=""
P=""
for C in $SEQ; do
  if [ "$C" = "$T" ]; then PREV=$P; fi
  P=$C
done
if [ -n "$PREV" ] && [ ! -e "attempt_$PREV.txt" ] && [ ! -e "$PREV.json" ]; then
  log "go145a.sh $T refused: the call $PREV before it was not made (item 273 (k)(1): the sealed order)"
  echo "previous call not made"; exit 1
fi
SD=""
HOLD=""
REC=""
EMUX=""
EXTRA=""
case "$T" in
  v145_*) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec";;
  w145_*) SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD
          EMUX="--emu-arg=--vulkan-validation --emu-arg=true"
          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0 VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER";;
esac
# ROADMAP s122 item 105 (v): the call is verbatim from the seal - its PLWAIT line, exactly one.
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go145a call: PLWAIT="*" bash C:/kyty/s145/go145a.sh $T")
        V=${PLINE#go145a call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go145a.sh $T refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL', ROADMAP s122 item 105 (v))"
  echo "PLWAIT differs from the seal"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY $T: level $LEVEL; stop file?; lock?; PLWAIT=$PLWAIT; procload --wait-s $PLWAIT; $SC --check-seal; $SC --stop-check $T; cpu < 15; idle142; procload --wait-s 0; stop file?; shader cache count; cache manifest before (cachemf145); lock with winpid (runs145/lock.log UTC); fgcpu145 --save; install $BUILD_PINNED ($BUILD_EXPECT); enter_scene.py $T --level $LEVEL --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0; log sha; cache manifest after (cachemf145); glitch+sheet ${REC:-none}; $SC --tag $T; restore $BUILD_PINNED; fgcpu145 --since --chain-pid (times.txt row); unlock"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then
  log "go145a.sh $T refused: pinned copy $BUILD_PINNED missing or its sha != $BUILD_EXPECT - not starting"; echo "pinned build bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go145a.sh $T refused: gates_default.txt is not the empty file - not starting"; echo "gate file bad"; exit 1
fi
# 2026-09-26: the agent shell inherits an environment WITHOUT %ProgramFiles%; nvml.dll then fails to initialise while
# Vulkan keeps working.  Exported here so nvidia-smi (idle142.py, the clock logger) inherits it.
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
mkdir -p $OUT step2
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*145|test_[a-z0-9_]*145|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  # item 231 (z)(5): the BUSY row of step2/times.txt names the process of the last "procload: busy" line of go145a.log,
  # read by the same command that writes the row.
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)" >> $TIMES
}
guards() {
  python $ROOT/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy (or the mutation harness lives) after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
  return 0
}
log "go145a.sh $T requested (level $LEVEL, build $BUILD_EXPECT, empty gate file, hold $HOLD, PLWAIT=$PLWAIT)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $ROOT/$SC --check-seal >> $L 2>&1; then
  log "$SC --check-seal refused (see above) - not starting"; echo "seal check failed"; exit 1
fi
python $ROOT/$SC --stop-check $T >> $L 2>&1
SRC=$?
if [ "$SRC" = "5" ]; then
  log "go145a.sh $T refused (rc 5): a stop rule of item 273 (k)(4) (the control W, two W, three V, the window event - the stop-check lines above); question to the lead"
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
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T shader cache files before the lock $(cachen) ($CACHE)" >> $TIMES
CMB=$(python $ROOT/cachemf145.py $OUT/cache_$T.before.json 2>&1 | tail -1 | tr -d '\r')
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T cache manifest before the lock: $CMB" >> $TIMES
set -o noclobber
if ! { echo "go145a.sh $T pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
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
  FG=$(python $ROOT/fgcpu145.py --since $OUT/fgcpu_$T.a.json --chain-pid $WINPID 2>&1 | tail -1 | tr -d '\r')
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T foreign cpu at the end inside the lock: $FG" >> $TIMES
  rm -f $LOCK
  echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
  exit $RCX
}
trap finish EXIT
python $ROOT/fgcpu145.py --save $OUT/fgcpu_$T.a.json >> $L 2>&1
log "installed before: $(sha "$GAME")"
INSTALLED=1
cp "$BUILD_PINNED" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$BUILD_EXPECT" ] || { log "installed sha != $BUILD_EXPECT - stop"; exit 1; }
log "files: $(sha256sum $SC test_$SC mut_$SC $PRED gates_default.txt enter_scene.py idle142.py procload.py go145a.sh sheet142.py fgcpu145.py cachemf145.py lockcheck145.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "$T.refused.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" \
         "rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt" "runs145/$T.score.json" \
         "runs145/cache_$T.after.json" \
         log_${T}_a*.txt stdout_${T}_a*.txt; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
echo "go145a.sh $T pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) build $BUILD_EXPECT" > $MARK
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T enter_scene start (level $LEVEL, hold $HOLD)" >> $TIMES
log "$T start (level $LEVEL, hold $HOLD, empty gate file, emu '$EMUX', extra '$EXTRA')"
python $ROOT/enter_scene.py $T --level $LEVEL --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt \
  --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
RC=$?
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T enter_scene end rc $RC log_$T.txt sha256 $(sha log_$T.txt)" >> $TIMES
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T shader cache files after the run $(cachen) ($CACHE)" >> $TIMES
CMA=$(python $ROOT/cachemf145.py $OUT/cache_$T.after.json 2>&1 | tail -1 | tr -d '\r')
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T cache manifest after the run: $CMA" >> $TIMES
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
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T s51_vidglitch rc $GRC glitch_$T.txt sha256 $(sha glitch_$T.txt) rec_$T.mp4 sha256 $(sha rec_$T.mp4)" >> $TIMES
    python $ROOT/sheet142.py rec_$T.mp4 sheet_$T.png > sheet_$T.txt 2>&1
    SHRC=$?
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T sheet rc $SHRC sheet_$T.png sha256 $(sha sheet_$T.png)" >> $TIMES
  else
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T no video rec_$T.mp4" >> $TIMES
  fi
fi
python $ROOT/$SC --tag $T > score_$T.txt 2>&1
SCRC=$?
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T scorer rc $SCRC score_$T.txt sha256 $(sha score_$T.txt)" >> $TIMES
log "scorer $T rc=$SCRC $(head -1 score_$T.txt)"
if [ "$RC" != "0" ]; then exit 1; fi
exit 0
