#!/bin/bash
# Track S, link S12c (HPP-496; ROADMAP "SESSION 122" item 408 (l) S12c, item 414 (g)(2), item 419 (v)): the shipping arms of S-pcw on
# the S12 copy adb0c82f - s12_w, s12_v, the blob growth pair s12_gw / s12_gr, the reference s12_v0.  Port of s9/go_s9.sh (seal 07):
# stop file, lock first, RETURN_FAILED / IN_ARM guards, procload, idle, one attempt, the seal call line, the copy and the return of
# the installed binary and of the caches by sha, the foreign-CPU row (fgcpu143.py, <app> mask), GamePatch -> rc 7.  ASCII only
# (item 175 (v)).  No emulator code, no build.  One tag per lock.
#   TAGS and their arm (s12/sc_s12.py --plan <tag>; order and conditions sc_s12.py --allowed <tag>):
#     s12_w   M, caches as found (copied before, returned after), W of item 295 (b): --vulkan-validation true, VK_LAYER_PATH,
#             VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, no video, hold 310, timeout 600
#     s12_v   M, caches as found, video, hold 330
#     s12_gw  T, full return (snap0 + snap0_drv, the form APP), hero_kratos, video, hold 330; after the arm the app caches and GLCache
#             are copied to s12/app_post/s12_gw and s12/glc_post/s12_gw (their MANIFEST.txt is the Z2 manifest of item 419 (v))
#     s12_gr  T, integrity (the form pcw_int): app and GLCache restored from the post copies of s12_gw, hero_kratos, video, hold 120
#     s12_v0  M, caches as found, video, hold 330, KYTY_S_PCW=0 (reference)
#   Every arm names KYTY_S_PCW explicitly (item 419 (v) Z3): s12_v0 0, the others 1.  No KYTY_S_PCW_FORCE_MS, no KYTY_GAME_PATCH,
#   no KYTY_GPU_CHECKPOINTS; every KYTY_* and VK_LAYER_* variable of the shell is unset before the call.
#   BINARY: the seal line "s12 binary: <sha> <path>" of pred/08_s.md (the S12 copy adb0c82f, item 419).
#   GUARD s12/IN_ARM: written before the install, removed only by a successful return; while it (or a RETURN_FAILED / IN_ARM guard of
#     s4, s6, s10, s12) exists go_s12.sh refuses rc 1.  ADMISSION: the installed binary before the arm is FS4 31cbfee8 or FS5 631ff987
#     (INST_OK; the executor variant of section 6 of the seal), else no arm (rc 1).
#   THE LOCK line begins "go_s.sh <tag> " (cachex_s.py, unchanged, admits a write only from that prefix) and names go_s12.sh.
# EXIT CODES: 0 run done; 1 hard refusal / failed run / failed return; 2 usage; 4 BUSY (lock, stop file, idle) - no run;
#   6 a condition is not met (sc_s12.py --allowed rc 6) - no run, report to the lead; 7 a "GamePatch:" line in the log (item 342 (e)).
#   DRY=1 prints the plan after the cheap refusals; DRY=2 prints the plan right after the lock check.
#   usage: go_s12.sh <tag>
T=${1:-}
ROOT=C:/kyty/s288
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s288/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
SNAP_APP="d8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4"
SNAP_DRV="1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SNAPDIR="C:/kyty/s288/snap0"
SNAPDRVDIR="C:/kyty/s288/snap0_drv"
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
S9=$ROOT/s9
S12=$ROOT/s12
SC=$S12/sc_s12.py
PRED=pred/08_s.md
INST_FS4="31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5"
INST_FS5="631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17"
RSLEEP=5
PLMAX=540
PLWAIT=${PLWAIT:-$PLMAX}
case "$T" in
  ''|*[!a-z0-9_]*) echo "usage: go_s12.sh <tag>  (see the header)"; exit 2;;
esac
log0() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $S12/go_s12.log; }
busy0() { log0 "go_s12.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
if [ -e $STOPF ]; then
  STOPTXT=""
  read -r STOPTXT < $STOPF 2>/dev/null
  busy0 "stop file $STOPF: $STOPTXT"
fi
lockheld() {
  if [ -e $LOCK ]; then
    LOCKTXT=""
    read -r LOCKTXT < $LOCK 2>/dev/null
    busy0 "lock held: $LOCKTXT"
  fi
}
lockheld
guardfiles() {
  for G in $ROOT/s4/RETURN_FAILED $ROOT/s6/RETURN_FAILED $ROOT/s10/RETURN_FAILED $ROOT/s10/IN_ARM $S12/RETURN_FAILED $S12/IN_ARM; do
    if [ -e $G ]; then
      GT=""
      read -r GT < $G 2>/dev/null
      log0 "go_s12.sh $T refused (rc 1): the guard $G exists ($GT) - the lead removes it after the return by hand"
      echo "return failed guard $G: $GT"; exit 1
    fi
  done
}
guardfiles
for V in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Za-z0-9_]*'); do unset $V; done
case "$PLWAIT" in
  ''|*[!0-9]*) log0 "go_s12.sh $T refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then
  log0 "go_s12.sh $T refused: PLWAIT $PLWAIT > $PLMAX"; echo "PLWAIT above $PLMAX"; exit 2
fi
cd "$ROOT" || exit 1
PLAN=$(python $SC --plan "$T" 2>&1 | tr -d '\r')
case "$PLAN" in
  s12\ *) ;;
  *) log0 "go_s12.sh $T refused: unknown tag ($PLAN)"; echo "usage: unknown tag $T"; exit 2;;
esac
set -- $PLAN
LEVEL=$2; CLS=$3; MODE=$4; HOLD=$5; PCW=$6; SRC=$7; SDRAWS=$8; TOUT=$9; REC=${10}; VAL=${11}; KIND=${12}
LD=$S12
CLSX=""; [ "$CLS" = "T" ] && CLSX="KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1"
RECX=""; [ "$REC" = "1" ] && RECX="--rec"
VALX=""; [ "$VAL" = "1" ] && VALX="--emu-arg=--vulkan-validation --emu-arg=true VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000"
case "$PCW" in
  0|1) PCWX="KYTY_S_PCW=$PCW";;
  *) echo "usage: bad KYTY_S_PCW $PCW"; exit 2;;
esac
case "$MODE" in
  full) RSRC_APP="$SNAPDIR"; RSRC_GLC="$SNAPDRVDIR";;
  integrity) RSRC_APP="$LD/app_post/$SRC"; RSRC_GLC="$LD/glc_post/$SRC";;
  asis) RSRC_APP="-"; RSRC_GLC="-";;
  *) echo "usage: bad mode $MODE"; exit 2;;
esac
ENTER="python $S9/enter_scene_s9.py $T --root $LD --level $LEVEL --attempts 1 --stable-draws $SDRAWS --timeout $TOUT --no-install --require-idle --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED $RECX --hold $HOLD $VALX KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 $CLSX $PCWX"
if [ "${DRY:-0}" = "2" ]; then
  echo "PLAN $T: link s12, seal $PRED, binary the 's12 binary:' line of $PRED; kind $KIND; restore app <- $RSRC_APP; restore glc <- $RSRC_GLC; $ENTER"
  exit 0
fi
L=$LD/go_s12.log
OUT=$LD/runs_s
TIMES=$LD/times.txt
MARK=$LD/attempt_$T.txt
mkdir -p $OUT
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
busy() { log "go_s12.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
if [ -e "$MARK" ] || [ -e "$LD/$T.json" ]; then
  log "go_s12.sh $T refused: attempt_$T.txt or $T.json exists - the one attempt of $T was made (no repeat)"
  echo "attempt already made"; exit 1
fi
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go_s12 call: PLWAIT="*" bash C:/kyty/s288/s12/go_s12.sh $T")
        V=${PLINE#go_s12 call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go_s12.sh $T refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL')"
  echo "PLWAIT differs from the seal"; exit 1
fi
RUNSHA=""; RUNBIN=""
while IFS= read -r PLINE || [ -n "$PLINE" ]; do
  PLINE=${PLINE%$'\r'}
  case "$PLINE" in
    "s12 binary: "*) V=${PLINE#s12 binary: }; RUNSHA=${V%% *}; RUNBIN=${V#* };;
  esac
done < "$PRED"
if [ -z "$RUNSHA" ]; then
  log "go_s12.sh $T refused: the seal $PRED has no line 's12 binary: <sha256> <path>'"; echo "no s12 binary"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY $T: level $LEVEL class $CLS mode $MODE kind $KIND; install $RUNBIN ($RUNSHA); restore app <- $RSRC_APP; restore glc <- $RSRC_GLC; $ENTER"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$RUNBIN" ] || [ "$(sha "$RUNBIN")" != "$RUNSHA" ]; then
  log "go_s12.sh $T refused: the arm binary $RUNBIN missing or its sha != $RUNSHA"; echo "arm binary bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go_s12.sh $T refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1
fi
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
X=$(python $ROOT/cachex_s.py where glc 2>&1); WRC=$?
log "$X"
if [ "$WRC" != "0" ]; then
  log "go_s12.sh $T refused (rc 1): the GLCache path of the environment is not the known folder (RC9)"; echo "glcache path: $X"; exit 1
fi
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*_s|test_[a-z0-9_]*_s|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s12 $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | sed -E "s/\('[^']*'/('<app>'/g" | cut -c1-300)" >> $TIMES
}
guards() {
  python $ROOT/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
  return 0
}
log "go_s12.sh $T requested (level $LEVEL, class $CLS, mode $MODE, kind $KIND, KYTY_S_PCW=$PCW, binary $RUNSHA, hold $HOLD, PLWAIT=$PLWAIT)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $SC --check-seal --seal $ROOT/$PRED >> $L 2>&1; then
  log "sc_s12.py --check-seal refused - not starting"; echo "seal check failed"; exit 1
fi
python $SC --allowed $T >> $L 2>&1
ARC=$?
if [ "$ARC" = "6" ]; then
  log "go_s12.sh $T refused (rc 6): a condition is not met (see the ALLOWED line above) - report to the lead"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s12 $T refused rc 6: $(grep "ALLOWED $T" $L | tail -1)" >> $TIMES
  echo "condition not met"; exit 6
fi
if [ "$ARC" != "0" ]; then log "go_s12.sh $T refused: order (rc $ARC)"; echo "order"; exit 1; fi
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
if [ "$IDLE_RC" -ne 0 ]; then busy "machine not idle by idle142 (rc $IDLE_RC)"; fi
lockheld
guards 0 || busy "procload / name guard not clean before the lock"
if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi
guardfiles
set -o noclobber
if ! { echo "go_s.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S) (go_s12.sh seal 08)" > $LOCK; } 2>/dev/null; then
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
INARM_MINE=0
tline() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s12 $T $*" >> $TIMES; }
shaof() { echo "$1" | sed -n 's/.* sha \([0-9a-f]\{64\}\).*/\1/p' | tail -1; }
mansha() { sha "$1/MANIFEST.txt"; }
BINPRE=$LD/installed_bin_pre.exe
INST_SHA=""
restore_bin() {
  for i in 1 2 3; do
    if [ -n "$INST_SHA" ] && [ "$(sha "$BINPRE")" = "$INST_SHA" ] && cp "$BINPRE" "$GAME" 2>/dev/null && \
       [ "$(sha "$GAME")" = "$INST_SHA" ]; then return 0; fi
    sleep $RSLEEP
  done
  return 1
}
return_failed() {
  {
    echo "RETURN_FAILED $T $(date -u +%Y-%m-%dT%H:%M:%SZ) rc $1"
    echo "app: restore by hand from $LD/installed_pre (MANIFEST.txt sha $(mansha $LD/installed_pre))"
    echo "glc: restore by hand from $LD/glc_pre (MANIFEST.txt sha $(mansha $LD/glc_pre))"
    echo "binary: $GAME must be $INST_SHA (copy $BINPRE), now $(sha "$GAME")"
  } > $LD/RETURN_FAILED
  tline "RETURN FAILED rc $1: guard $LD/RETURN_FAILED written before the unlock - comment the link"
  echo "RETURN FAILED: guard $LD/RETURN_FAILED - comment the link (item 250 (v))"
}
do_return() {
  local rc=0 X
  if [ "$TOUCHED" = "1" ] && [ "$RETURNED" = "0" ]; then
    X=$($CX restore app $LD/installed_pre $(mansha $LD/installed_pre) 2>&1); rc=$((rc|$?)); log "$X"
    $CX note $CJ return_app expected=$(mansha $LD/installed_pre) got=$(shaof "$X") >> $L 2>&1
    X=$($CX restore glc $LD/glc_pre $(mansha $LD/glc_pre) 2>&1); rc=$((rc|$?)); log "$X"
    $CX note $CJ return_glc expected=$(mansha $LD/glc_pre) got=$(shaof "$X") >> $L 2>&1
    RETURNED=1
    tline "return of the caches rc $rc: app $(mansha $LD/installed_pre) glc $(mansha $LD/glc_pre)"
  fi
  if [ "$INSTALLED" = "1" ]; then
    if restore_bin; then log "returned the installed binary $INST_SHA"; INSTALLED=0
    else log "RESTORE FAILED: $GAME sha $(sha "$GAME") != $INST_SHA"; rc=1; fi
    $CX note $CJ installed_after sha=$(sha "$GAME") >> $L 2>&1
  fi
  [ "$rc" = "0" ] || return_failed $rc
  if [ "$rc" = "0" ] && [ "$INARM_MINE" = "1" ] && [ "$INSTALLED" = "0" ] && { [ "$TOUCHED" = "0" ] || [ "$RETURNED" = "1" ]; }; then
    rm -f $LD/IN_ARM && INARM_MINE=0 && tline "guard $LD/IN_ARM removed after the successful return"
  fi
  return $rc
}
finish() {
  RCX=$?
  do_return || { echo "return failed"; RCX=1; }
  FG=$(python $ROOT/fgcpu143.py --since $OUT/fgcpu_$T.a.json 2>&1 | tail -1 | tr -d '\r')
  tline "foreign cpu at the end inside the lock: $FG"
  rm -f $LOCK
  echo "lock released $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
  exit $RCX
}
trap finish EXIT
$CX note $CJ arm_start utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) >> $L 2>&1
$CX note $CJ return_prev ok=1 >> $L 2>&1
python $ROOT/fgcpu143.py --save $OUT/fgcpu_$T.a.json >> $L 2>&1
INST_SHA=$(sha "$GAME")
if [ -z "$INST_SHA" ]; then log "no installed binary $GAME - stop"; INST_SHA=""; exit 1; fi
rm -f "$BINPRE"
if ! cp "$GAME" "$BINPRE" 2>/dev/null || [ "$(sha "$BINPRE")" != "$INST_SHA" ]; then
  log "copy of the installed binary into $BINPRE failed - stop"; INST_SHA=""; exit 1
fi
$CX note $CJ installed_before sha=$INST_SHA path=$BINPRE >> $L 2>&1
tline "installed binary before the arm: $INST_SHA copied to $BINPRE"
if [ "$INST_SHA" != "$INST_FS4" ] && [ "$INST_SHA" != "$INST_FS5" ]; then
  log "the installed binary before the arm $INST_SHA is neither FS4 $INST_FS4 nor FS5 $INST_FS5 - no arm"
  tline "installed binary before the arm $INST_SHA not in {FS4, FS5} - no arm; a new installation needs a lead item"
  INST_SHA=""; echo "installed binary not FS4 / FS5"; exit 1
fi
X=$($CX man app 2>&1); log "$X"; MPA=$(shaof "$X"); $CX note $CJ man_pre_app sha=$MPA >> $L 2>&1
X=$($CX man glc 2>&1); log "$X"; MPG=$(shaof "$X"); $CX note $CJ man_pre_glc sha=$MPG >> $L 2>&1
if ! { echo "IN_ARM $T $(date -u +%Y-%m-%dT%H:%M:%SZ) pid $$ - an arm is inside the lock; a successful return removes this file"
       echo "installed: $INST_SHA (copy $BINPRE)"
       echo "man_pre_app: $MPA (copy $LD/installed_pre after this line)"
       echo "man_pre_glc: $MPG (copy $LD/glc_pre after this line)"; } > $LD/IN_ARM; then
  log "the guard $LD/IN_ARM not written - no arm"; echo "IN_ARM not written"; exit 1
fi
INARM_MINE=1
tline "guard $LD/IN_ARM written (installed $INST_SHA, man_pre_app $MPA, man_pre_glc $MPG) before the install"
INSTALLED=1
cp "$RUNBIN" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$RUNSHA" ] || { log "installed sha != $RUNSHA - stop"; exit 1; }
log "files: $(sha256sum $SC $S12/test_sc_s12.py $S12/mut_sc_s12.py $S12/go_s12.sh $S9/enter_scene_s9.py cachex_s.py sc_s.py $PRED gates_default.txt idle142.py procload.py sheet142.py fgcpu143.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
X=$($CX copy app $LD/installed_pre --replace 2>&1) || { log "$X"; exit 1; }; log "$X"
X=$($CX copy glc $LD/glc_pre --replace 2>&1) || { log "$X"; exit 1; }; log "$X"
$CX note $CJ glc_pre_copy sha=$(mansha $LD/glc_pre) path=$LD/glc_pre >> $L 2>&1
$CX note $CJ installed_pre_copy sha=$(mansha $LD/installed_pre) >> $L 2>&1
TOUCHED=1
if [ "$MODE" != "asis" ]; then
  if [ "$MODE" = "integrity" ]; then WANT_APP=$(mansha "$RSRC_APP"); WANT_GLC=$(mansha "$RSRC_GLC"); else WANT_APP=$SNAP_APP; WANT_GLC=$SNAP_DRV; fi
  X=$($CX verify app "$RSRC_APP" "$WANT_APP" 2>&1); VA=$?; log "$X"
  X=$($CX verify glc "$RSRC_GLC" "$WANT_GLC" 2>&1); VG=$?; log "$X"
  tline "verify the restore sources before the arm: app rc $VA ($RSRC_APP) glc rc $VG ($RSRC_GLC)"
  if [ "$VA" != "0" ] || [ "$VG" != "0" ]; then log "a restore source does not verify - no run"; echo "verify failed"; exit 1; fi
  X=$($CX restore app "$RSRC_APP" "$WANT_APP" 2>&1); RA=$?; log "$X"
  $CX note $CJ restore_app expected=$WANT_APP got=$(shaof "$X") source=$RSRC_APP >> $L 2>&1
  X=$($CX restore glc "$RSRC_GLC" "$WANT_GLC" 2>&1); RG=$?; log "$X"
  $CX note $CJ restore_glc expected=$WANT_GLC got=$(shaof "$X") source=$RSRC_GLC >> $L 2>&1
  tline "restore before the arm: app rc $RA ($RSRC_APP, $WANT_APP) glc rc $RG ($RSRC_GLC, $WANT_GLC)"
  if [ "$RA" != "0" ] || [ "$RG" != "0" ]; then log "restore before the arm failed - no run"; echo "restore failed"; exit 1; fi
else
  tline "caches as found (mode asis): no restore before the arm; app $MPA glc $MPG"
fi
OLD=$LD/old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "$T.refused.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" \
         "rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt"; do
  if [ -f "$LD/$F" ]; then mkdir -p "$OLD"; mv "$LD/$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
echo "go_s12.sh $T pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) binary $RUNSHA" > $MARK
tline "enter_scene start (level $LEVEL, class $CLS, mode $MODE, kind $KIND, KYTY_S_PCW=$PCW, hold $HOLD)"
log "$T start: $ENTER"
X=$($CX man glc --save $OUT/$T.glc_launch.txt 2>&1); $CX note $CJ man_launch_glc sha=$(shaof "$X") >> $L 2>&1
$ENTER > $LD/$T.stdout.txt 2>&1
RC=$?
tline "enter_scene end rc $RC log_$T.txt sha256 $(sha $LD/log_$T.txt)"
log "$T rc=$RC $(tail -1 $LD/$T.stdout.txt)"
if [ "$RC" = "3" ] && [ ! -e "$LD/$T.json" ]; then
  if [ -f "$LD/$T.refused.json" ]; then
    mkdir -p "$OLD"; mv "$MARK" "$OLD/" && log "idle refusal inside enter_scene: no attempt made, marker moved to $OLD/"
  fi
  busy "the idle criterion inside enter_scene_s9.py refused (see $T.refused.json) - no run"
fi
X=$($CX man app --save $OUT/$T.app_post.txt 2>&1); log "$X"; $CX note $CJ man_post_app sha=$(shaof "$X") >> $L 2>&1
X=$($CX man glc --save $OUT/$T.glc_post.txt 2>&1); log "$X"; $CX note $CJ man_post_glc sha=$(shaof "$X") >> $L 2>&1
tline "manifests after the arm: app $(grep 'man app' $L | tail -1 | sed 's/.*sha //') glc $(grep 'man glc' $L | tail -1 | sed 's/.*sha //')"
if [ "$T" = "s12_gw" ]; then
  X=$($CX copy glc $LD/glc_post/$T --replace 2>&1); log "$X"
  $CX note $CJ glc_post_copy sha=$(mansha $LD/glc_post/$T) path=$LD/glc_post/$T >> $L 2>&1
  X=$($CX copy app $LD/app_post/$T --replace 2>&1); log "$X"
  $CX note $CJ app_post_copy sha=$(mansha $LD/app_post/$T) path=$LD/app_post/$T >> $L 2>&1
  tline "Z2 manifest after s12_gw: $(grep -E '^PipelineCache/PPSA21564\.bin(\.tmp)? ' $LD/app_post/$T/MANIFEST.txt | tr '\n' ';')"
fi
do_return || { echo "return failed"; exit 1; }
if [ -f "$LD/rec_$T.mp4" ]; then
  python $VIDGLITCH $LD/rec_$T.mp4 4 6 $LD/vidframes_$T > $LD/glitch_$T.txt 2>&1
  GRC=$?
  tline "s51_vidglitch rc $GRC glitch_$T.txt sha256 $(sha $LD/glitch_$T.txt) rec_$T.mp4 sha256 $(sha $LD/rec_$T.mp4)"
  python $ROOT/sheet142.py $LD/rec_$T.mp4 $LD/sheet_$T.png > $LD/sheet_$T.txt 2>&1
  tline "sheet rc $? sheet_$T.png sha256 $(sha $LD/sheet_$T.png)"
else
  tline "no video rec_$T.mp4"
fi
python $SC --tag $T > $LD/score_$T.txt 2>&1
SCRC=$?
tline "scorer rc $SCRC score_$T.txt sha256 $(sha $LD/score_$T.txt): $(head -1 $LD/score_$T.txt | cut -c1-200)"
GP="no log"
if [ -f "$LD/log_$T.txt" ]; then
  GP=$(python -c "import sys
n = 0
for line in open(sys.argv[1], 'rb'):
    n += line.startswith(b'GamePatch:')
print(n)" "$LD/log_$T.txt" 2>&1 | tr -d '\r')
fi
tline "item 342 (e): lines beginning GamePatch: in log_$T.txt: $GP"
case "$GP" in
  0|"no log") ;;
  *) log "go_s12.sh $T: $GP lines GamePatch: - an interference of item 342 (e) (rc 7)"
     echo "GAMEPATCH interference: $GP lines (item 342 (e))"; exit 7;;
esac
if [ "$RC" != "0" ]; then exit 1; fi
exit 0
