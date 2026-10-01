#!/bin/bash
# Track S, link S3 (HPP-313; ROADMAP s.0.1 "SESSION 122" item 241 (g)-(z), item 229 (v), (g)(2); S0 sections 3.2-3.4 with the
# S1 corrections RC1-RC3, RC12, RC13): the game chain of the links S4 (S-warm, C1-C4, base T2, G) and S6 (A/B of S-pcw).
# Port of C:/kyty/s143/go143a.sh (stop file, lock first, guards, procload, idle, one attempt, seal call line, foreign-CPU
# row D-4, binary restore) plus the arm protocol of item 241 (g) through cachex_s.py.  ASCII only (item 175 (v)).
# No emulator code, no build.  One tag per lock (item 241 (l)).
#   TAGS (item 241 (d)-(zh), (z)(5); the order and the conditions are sc_s.py --allowed <tag>, the arm spec sc_s.py --plan):
#     S4  sw_m1 sw_m2 sw_m3 (M: big_hand_pirate_island voxel_world ice_iceberg), sw_t1 (T: big_hand_pirate_island);
#         c1_K c2_K c3_K c4_K (T; K = 0 shuriken_ninja_castle, 1 jack_in_the_box, 2 cymbal_party_land - the L0 and its
#         reserves in order; C2 and C4 keep GLCache as C1 / C3 left it, C4 adds KYTY_PIPELINE_SALT=<tag>);
#         t2_01..t2_05 (T: small_pot_lava spin_drill_natural_cave light_gadget_graveyard enemy_taco hero_kratos), reserves
#         t2_06..t2_10 (picup_light enemy_snake mini_rocket_chain hero_drake bonus_path_maker_mix) - only with "return
#         neutralises" of C1-C4; g_1 g_2 g_3_K (G: underwater_aerial_garden big_hand_pirate_island L0)
#     S6  pcw_1 (KYTY_S_PCW=0) pcw_2 (1) pcw_3 (1) pcw_int (1; integrity: the app caches and GLCache as pcw_3 left them,
#         no snapshot) pcw_4 (0) pcw_val (1, --vulkan-validation true); all with KYTY_S_PCW_FORCE_MS=15000 on
#         underwater_aerial_garden; the binary of S5a - the line "pcw binary: <sha256> <path>" of the seal pred/02_s.md
#   ENVIRONMENT (item 241 (g)(5), S0 3.4): M = the sc142 base of enter_scene.py + KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0;
#     T = M + KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1; G = T + KYTY_DUMP_GCN=1.  Video on every arm.
#   THE ARM PROTOCOL (item 241 (g)(1)-(3)), inside the lock, every step a cachex_s.py call (rc != 0 = no run / loud):
#     before: manifests of the app caches and of GLCache; the copy of the installed app caches before the FIRST arm of the
#       link (installed_caches/, the letter) and before EVERY arm (installed_pre/ - the return source, executor's variant:
#       another chain may run between two arms); the copy of GLCache "before the arm" (glc_pre/); the mirror restore of
#       snap0 (expected d8ca8c8e...) or, for pcw_int, of app_post/pcw_3; the mirror restore of GLCache to snap0_drv
#       (1767ca0a...) or, for c2_K / c4_K / pcw_int, to glc_post/<c1_K | c3_K | pcw_3>; a times.txt line with both
#     after: log, stdout, json, video; manifests "after"; glc_post/<tag> for c1_K, c3_K, pcw_3 and app_post/pcw_3; the
#       GCN dumps of a G arm into gcn/<tag>; the return of installed_pre/ and glc_pre/ with their manifests; the binary
#       9235a7ac back and its sha; DXCache is never touched.  Every value goes into runs_s/<tag>.cache.json (the scorer
#       admits the arm by it).
#   ONE ATTEMPT: attempt_<tag>.txt inside the lock right before enter_scene.py; while it or <tag>.json exists the tag
#     refuses rc 1 (the idle refusal inside enter_scene.py moves the marker to old/ and ends rc 4).
#   STOP FILE (general rule 26): C:/kyty/s288/STOP -> rc 4 before anything and again right before the lock.
#   THE SEAL'S CALL (item 105 (v)): exactly one line "go_s call: PLWAIT=<n> bash C:/kyty/s288/go_s.sh <tag>" in the seal of
#     the link (S4 pred/01_s.md, S6 pred/02_s.md); sc_s.py --check-seal --seal <seal> before the lock.
#   THE LOCK is checked before any process (DRY included) and before every guard stage; "lock taken|released <tag> <UTC>"
#     into <link>/runs_s/lock.log; every event one UTC line into <link>/times.txt at its moment (general rule 23).
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, --pred of the seal; KYTY_GPU_CHECKPOINTS never passed.
# EXIT CODES: 0 run done (read score_<tag>.txt); 1 hard refusal or failed run; 2 usage; 4 BUSY (lock, stop file, guards,
#   idle) - no run; 6 a condition of item 241 is not met (sc_s.py --allowed rc 6) - no run, report to the lead.
#   DRY=1 go_s.sh <tag> prints the plan and exits 0 after the cheap refusals, before any guard, lock or install;
#   DRY=2 prints the plan of the arm right after the lock check, before the seal checks (for the seal text itself).
#   usage: go_s.sh <tag>
T=${1:-}
ROOT=C:/kyty/s288
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s288/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"
SNAP_APP="d8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4"
SNAP_DRV="1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
VKDUP="1000000"
SC="sc_s.py"
RSLEEP=5
PLMAX=540
PLWAIT=${PLWAIT:-$PLMAX}
case "$T" in
  ''|*[!a-z0-9_]*) echo "usage: go_s.sh <tag>  (see the header)"; exit 2;;
esac
log0() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $ROOT/go_s.log; }
busy0() { log0 "go_s.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
# general rule 26: the stop file first (bash builtins only).
if [ -e $STOPF ]; then
  STOPTXT=""
  read -r STOPTXT < $STOPF 2>/dev/null
  busy0 "stop file $STOPF: $STOPTXT"
fi
# ROADMAP s122 item 76 (b): the lock before any process - bash builtins only.
lockheld() {
  if [ -e $LOCK ]; then
    LOCKTXT=""
    read -r LOCKTXT < $LOCK 2>/dev/null
    busy0 "lock held: $LOCKTXT"
  fi
}
lockheld
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA
case "$PLWAIT" in
  ''|*[!0-9]*) log0 "go_s.sh $T refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then
  log0 "go_s.sh $T refused: PLWAIT $PLWAIT > $PLMAX (ROADMAP s122 item 40 (e)(4))"; echo "PLWAIT above $PLMAX"; exit 2
fi
cd "$ROOT" || exit 1
PLAN=$(python $ROOT/$SC --plan "$T" 2>&1 | tr -d '\r')
set -- $PLAN
LINK=$1; LEVEL=$2; CLS=$3; MODE=$4; HOLD=$5; SALT=$6; PCW=$7; VAL=$8; GLCFROM=$9; APPFROM=${10}; SDRAWS=${11}; TOUT=${12}
case "$LINK" in
  s4) PRED="pred/01_s.md";;
  s6) PRED="pred/02_s.md";;
  *) log0 "go_s.sh $T refused: unknown tag ($PLAN)"; echo "usage: unknown tag $T"; exit 2;;
esac
LD=$ROOT/$LINK
SALTX=""; [ "$SALT" = "1" ] && SALTX="KYTY_PIPELINE_SALT=$T"
CLSX=""
[ "$CLS" = "T" ] && CLSX="KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1"
[ "$CLS" = "G" ] && CLSX="KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1 KYTY_DUMP_GCN=1"
PCWX=""; [ "$PCW" != "-" ] && PCWX="KYTY_S_PCW=$PCW KYTY_S_PCW_FORCE_MS=15000"
EMUX=""; EXTRA=""
if [ "$VAL" = "1" ]; then
  EMUX="--emu-arg=--vulkan-validation --emu-arg=true"
  EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP"
fi
if [ "$MODE" = "integrity" ]; then RSRC_APP="$LD/app_post/$APPFROM"; else RSRC_APP="C:/kyty/s288/snap0"; fi
if [ "$MODE" = "full" ]; then RSRC_GLC="C:/kyty/s288/snap0_drv"; else RSRC_GLC="$LD/glc_post/$GLCFROM"; fi
ENTER="python $ROOT/enter_scene.py $T --root $LD --level $LEVEL --attempts 1 --stable-draws $SDRAWS --timeout $TOUT --no-install --require-idle --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED --rec $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 $CLSX $SALTX $PCWX"
if [ "${DRY:-0}" = "2" ]; then
  # the plan of one arm for the seal, before any seal of the link exists (S6 before pred/02_s.md): no file is read or written
  echo "PLAN $T: link $LINK, seal $PRED, binary $([ "$LINK" = "s4" ] && echo "$BUILD_PINNED ($BUILD_EXPECT)" || echo "the 'pcw binary:' line of $PRED"); restore app <- $RSRC_APP; restore glc <- $RSRC_GLC; $ENTER"
  exit 0
fi
L=$LD/go_s.log
OUT=$LD/runs_s
TIMES=$LD/times.txt
MARK=$LD/attempt_$T.txt
mkdir -p $OUT
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
busy() { log "go_s.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
if [ -e "$MARK" ] || [ -e "$LD/$T.json" ]; then
  log "go_s.sh $T refused: attempt_$T.txt or $T.json exists - the one attempt of $T was made (no repeat)"
  echo "attempt already made"; exit 1
fi
# ROADMAP s122 item 105 (v): the call is verbatim from the seal - its PLWAIT line, exactly one.
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go_s call: PLWAIT="*" bash C:/kyty/s288/go_s.sh $T")
        V=${PLINE#go_s call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go_s.sh $T refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL', ROADMAP s122 item 105 (v))"
  echo "PLWAIT differs from the seal"; exit 1
fi
# the binary of the arm: S4 the pinned 9235a7ac; S6 the "pcw binary:" line of its seal (item 228 (v): copy before, restore after)
if [ "$LINK" = "s4" ]; then
  RUNBIN="$BUILD_PINNED"; RUNSHA="$BUILD_EXPECT"
else
  RUNSHA=""; RUNBIN=""
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "pcw binary: "*) V=${PLINE#pcw binary: }; RUNSHA=${V%% *}; RUNBIN=${V#* };;
    esac
  done < "$PRED"
  if [ -z "$RUNSHA" ]; then
    log "go_s.sh $T refused: the seal $PRED has no line 'pcw binary: <sha256> <path>' (S5a not sealed)"; echo "no pcw binary"; exit 1
  fi
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY $T: link $LINK level $LEVEL class $CLS mode $MODE; stop file?; lock?; PLWAIT=$PLWAIT; procload --wait-s $PLWAIT; $SC --check-seal --seal $PRED; $SC --allowed $T; cpu < 15; idle142; procload --wait-s 0; stop file?; lock ($LINK/runs_s/lock.log UTC); fgcpu143 --save; install $RUNBIN ($RUNSHA); manifests app+glc; installed_caches (first arm) + installed_pre; glc_pre; restore app <- $RSRC_APP; restore glc <- $RSRC_GLC; $ENTER; manifests after; post copies; return installed_pre + glc_pre; restore $BUILD_PINNED; glitch+sheet; $SC --tag $T; fgcpu143 --since; unlock"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then
  log "go_s.sh $T refused: pinned copy $BUILD_PINNED missing or its sha != $BUILD_EXPECT"; echo "pinned build bad"; exit 1
fi
if [ ! -f "$RUNBIN" ] || [ "$(sha "$RUNBIN")" != "$RUNSHA" ]; then
  log "go_s.sh $T refused: the arm binary $RUNBIN missing or its sha != $RUNSHA"; echo "arm binary bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go_s.sh $T refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1
fi
# 2026-09-26: the agent shell inherits an environment WITHOUT %ProgramFiles% / %LOCALAPPDATA%; exported here so nvidia-smi
# and cachex_s.py (GLCache lives under %LOCALAPPDATA%) inherit them.
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*_s|test_[a-z0-9_]*_s|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  # item 231 (z)(5): the BUSY row names the process of the last "procload: busy" line of go_s.log, same command.
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)" >> $TIMES
}
guards() {
  python $ROOT/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy (or the mutation harness lives) after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
  return 0
}
log "go_s.sh $T requested (link $LINK, level $LEVEL, class $CLS, mode $MODE, binary $RUNSHA, hold $HOLD, PLWAIT=$PLWAIT)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $ROOT/$SC --check-seal --seal $ROOT/$PRED >> $L 2>&1; then
  log "$SC --check-seal refused (see above) - not starting"; echo "seal check failed"; exit 1
fi
python $ROOT/$SC --allowed $T >> $L 2>&1
ARC=$?
if [ "$ARC" = "6" ]; then
  log "go_s.sh $T refused (rc 6): a condition of item 241 is not met (see the ALLOWED line above) - report to the lead"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s $T refused rc 6: $(grep "ALLOWED $T" $L | tail -1)" >> $TIMES
  echo "condition not met"; exit 6
fi
if [ "$ARC" != "0" ]; then log "go_s.sh $T refused: order (rc $ARC, see the ALLOWED line above)"; echo "order"; exit 1; fi
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
set -o noclobber
if ! { echo "go_s.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  busy "lock taken by someone else: $(cat $LOCK 2>/dev/null)"
fi
set +o noclobber
echo "lock taken $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
CX="python $ROOT/cachex_s.py --tag $T"
CJ=$OUT/$T.cache.json
INSTALLED=0
TOUCHED=0
RETURNED=0
tline() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s $T $*" >> $TIMES; }
shaof() { echo "$1" | sed -n 's/.* sha \([0-9a-f]\{64\}\).*/\1/p' | tail -1; }
mansha() { sha "$1/MANIFEST.txt"; }
restore_bin() {
  for i in 1 2 3; do
    if cp "$BUILD_PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$BUILD_EXPECT" ]; then return 0; fi
    sleep $RSLEEP
  done
  return 1
}
do_return() {
  # item 241 (g)(3): the installed caches and GLCache "before the arm" back, with their manifests; then the binary.
  local rc=0 X
  if [ "$TOUCHED" = "1" ] && [ "$RETURNED" = "0" ]; then
    X=$($CX restore app $LD/installed_pre $(mansha $LD/installed_pre) 2>&1); rc=$((rc|$?)); log "$X"
    $CX note $CJ return_app expected=$(mansha $LD/installed_pre) got=$(shaof "$X") >> $L 2>&1
    X=$($CX restore glc $LD/glc_pre $(mansha $LD/glc_pre) 2>&1); rc=$((rc|$?)); log "$X"
    $CX note $CJ return_glc expected=$(mansha $LD/glc_pre) got=$(shaof "$X") >> $L 2>&1
    RETURNED=1
    tline "return of the caches rc $rc: app $(mansha $LD/installed_pre) glc $(mansha $LD/glc_pre)"
    [ "$rc" = "0" ] || log "RETURN FAILED: restore the caches from $LD/installed_pre and $LD/glc_pre by hand before any run"
  fi
  if [ "$INSTALLED" = "1" ]; then
    if restore_bin; then log "restored $BUILD_PINNED ($BUILD_EXPECT) into $GAME"; INSTALLED=0
    else log "RESTORE FAILED: $GAME sha $(sha "$GAME") != $BUILD_EXPECT - restore it by hand before any run"; rc=1; fi
    $CX note $CJ installed_after sha=$(sha "$GAME") >> $L 2>&1
  fi
  return $rc
}
finish() {
  RCX=$?
  do_return || { echo "return failed"; RCX=1; }
  # item 241 (v)(10), debt D-4: the foreign-CPU row at the end of every arm, still inside the lock.
  FG=$(python $ROOT/fgcpu143.py --since $OUT/fgcpu_$T.a.json 2>&1 | tail -1 | tr -d '\r')
  tline "foreign cpu at the end inside the lock: $FG"
  rm -f $LOCK
  echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
  exit $RCX
}
trap finish EXIT
python $ROOT/fgcpu143.py --save $OUT/fgcpu_$T.a.json >> $L 2>&1
log "installed before: $(sha "$GAME")"
INSTALLED=1
cp "$RUNBIN" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$RUNSHA" ] || { log "installed sha != $RUNSHA - stop"; exit 1; }
log "files: $(sha256sum $SC test_sc_s.py mut_sc_s.py cachex_s.py $PRED gates_default.txt enter_scene.py idle142.py procload.py go_s.sh sheet142.py fgcpu143.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
# ---- before the arm (item 241 (g)(1))
X=$($CX man app 2>&1); log "$X"; $CX note $CJ man_pre_app sha=$(shaof "$X") >> $L 2>&1
X=$($CX man glc 2>&1); log "$X"; $CX note $CJ man_pre_glc sha=$(shaof "$X") >> $L 2>&1
if [ ! -f $LD/installed_caches/MANIFEST.txt ]; then
  X=$($CX copy app $LD/installed_caches 2>&1) || { log "$X"; exit 1; }; log "$X"
  tline "installed caches copied before the first arm of the link: $(mansha $LD/installed_caches)"
fi
X=$($CX copy app $LD/installed_pre --replace 2>&1) || { log "$X"; exit 1; }; log "$X"
X=$($CX copy glc $LD/glc_pre --replace 2>&1) || { log "$X"; exit 1; }; log "$X"
$CX note $CJ glc_pre_copy sha=$(mansha $LD/glc_pre) path=$LD/glc_pre >> $L 2>&1
$CX note $CJ installed_pre_copy sha=$(mansha $LD/installed_pre) first=$(mansha $LD/installed_caches) >> $L 2>&1
if [ "$MODE" = "integrity" ]; then WANT_APP=$(mansha "$RSRC_APP"); else WANT_APP=$SNAP_APP; fi
if [ "$MODE" = "full" ]; then WANT_GLC=$SNAP_DRV; else WANT_GLC=$(mansha "$RSRC_GLC"); fi
TOUCHED=1
X=$($CX restore app "$RSRC_APP" "$WANT_APP" 2>&1); RA=$?; log "$X"
$CX note $CJ restore_app expected=$WANT_APP got=$(shaof "$X") source=$RSRC_APP >> $L 2>&1
X=$($CX restore glc "$RSRC_GLC" "$WANT_GLC" 2>&1); RG=$?; log "$X"
$CX note $CJ restore_glc expected=$WANT_GLC got=$(shaof "$X") source=$RSRC_GLC >> $L 2>&1
tline "restore before the arm: app rc $RA ($RSRC_APP, $WANT_APP) glc rc $RG ($RSRC_GLC, $WANT_GLC)"
if [ "$RA" != "0" ] || [ "$RG" != "0" ]; then log "restore before the arm failed - no run"; echo "restore failed"; exit 1; fi
if [ "$CLS" = "G" ]; then X=$($CX man gcn 2>&1); log "$X"; $CX note $CJ man_pre_gcn sha=$(shaof "$X") >> $L 2>&1; fi
# ---- the run
OLD=$LD/old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "$T.refused.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" \
         "rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt"; do
  if [ -f "$LD/$F" ]; then mkdir -p "$OLD"; mv "$LD/$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
echo "go_s.sh $T pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) binary $RUNSHA" > $MARK
tline "enter_scene start (level $LEVEL, class $CLS, mode $MODE, hold $HOLD)"
log "$T start: $ENTER"
$ENTER > $LD/$T.stdout.txt 2>&1
RC=$?
tline "enter_scene end rc $RC log_$T.txt sha256 $(sha $LD/log_$T.txt)"
log "$T rc=$RC $(tail -1 $LD/$T.stdout.txt)"
if [ "$RC" = "3" ] && [ ! -e "$LD/$T.json" ]; then
  if [ -f "$LD/$T.refused.json" ]; then
    mkdir -p "$OLD"; mv "$MARK" "$OLD/" && log "idle refusal inside enter_scene: no attempt made, marker moved to $OLD/"
  fi
  busy "the idle criterion inside enter_scene.py refused (see $T.refused.json) - no run"
fi
# ---- after the arm (item 241 (g)(3))
X=$($CX man app 2>&1); log "$X"; $CX note $CJ man_post_app sha=$(shaof "$X") >> $L 2>&1
X=$($CX man glc 2>&1); log "$X"; $CX note $CJ man_post_glc sha=$(shaof "$X") >> $L 2>&1
tline "manifests after the arm: app $(grep 'man app' $L | tail -1 | sed 's/.*sha //') glc $(grep 'man glc' $L | tail -1 | sed 's/.*sha //')"
case "$T" in
  c1_*|c3_*|pcw_3)
    X=$($CX copy glc $LD/glc_post/$T --replace 2>&1); log "$X"
    $CX note $CJ glc_post_copy sha=$(mansha $LD/glc_post/$T) path=$LD/glc_post/$T >> $L 2>&1;;
esac
if [ "$T" = "pcw_3" ]; then
  X=$($CX copy app $LD/app_post/$T --replace 2>&1); log "$X"
  $CX note $CJ app_post_copy sha=$(mansha $LD/app_post/$T) path=$LD/app_post/$T >> $L 2>&1
fi
if [ "$CLS" = "G" ]; then
  X=$($CX copy gcn $LD/gcn/$T --replace 2>&1); log "$X"
  $CX note $CJ gcn_copy sha=$(mansha $LD/gcn/$T) path=$LD/gcn/$T >> $L 2>&1
fi
do_return || { echo "return failed"; exit 1; }
if [ -f "$LD/rec_$T.mp4" ]; then
  python $VIDGLITCH $LD/rec_$T.mp4 4 6 $LD/vidframes_$T > $LD/glitch_$T.txt 2>&1
  GRC=$?
  tline "s51_vidglitch rc $GRC glitch_$T.txt sha256 $(sha $LD/glitch_$T.txt) rec_$T.mp4 sha256 $(sha $LD/rec_$T.mp4)"
  python $ROOT/sheet142.py $LD/rec_$T.mp4 $LD/sheet_$T.png > $LD/sheet_$T.txt 2>&1
  SHRC=$?
  tline "sheet rc $SHRC sheet_$T.png sha256 $(sha $LD/sheet_$T.png)"
else
  tline "no video rec_$T.mp4"
fi
python $ROOT/$SC --tag $T > $LD/score_$T.txt 2>&1
SCRC=$?
tline "scorer rc $SCRC score_$T.txt sha256 $(sha $LD/score_$T.txt)"
log "scorer $T rc=$SCRC $(head -1 $LD/score_$T.txt)"
if [ "$RC" != "0" ]; then exit 1; fi
exit 0
