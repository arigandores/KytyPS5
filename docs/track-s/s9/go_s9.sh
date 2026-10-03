#!/bin/bash
# Track S, link S9 (HPP-431; ROADMAP "SESSION 122" item 355 (g)-(e), (k)): the game chain of link S10 - the repeat of integrity
# pi_w1 pi_r1 pi_w0 pi_r0, C5 (c5_0), the T2 base t2_1 .. t2_10 with t2_cs0, the S-cat probe u_1 .. u_5.  Port of
# C:/kyty/s288/go_s.sh (seal 04): stop file, lock first, RETURN_FAILED guards, procload, idle, one attempt, the seal call line,
# the foreign-CPU row, the copy and return of the installed binary and of the caches by sha (item 250 (b), (v)), the GamePatch
# interference (item 342 (e)).  ASCII only (item 175 (v)).  No emulator code, no build.  One tag per lock.
#   TAGS and their arm (s9/sc_s9.py --plan <tag>; order and conditions sc_s9.py --allowed <tag>):
#     pi_w1 / pi_w0  M, full return (snap0 + snap0_drv), KYTY_S_PCW=1 / 0 + KYTY_S_PCW_FORCE_MS=15000, hold 330, binary s;
#                    after the arm the app caches and GLCache are copied to s10/app_post/<tag>, s10/glc_post/<tag>
#     pi_r1 / pi_r0  T, integrity: app and GLCache restored from the post copies of pi_w1 / pi_w0 (no snapshot), hold 120
#     c5_0           T, full return, shuriken_ninja_castle, KYTY_PIPELINE_SALT=c5_0 KYTY_PIPELINE_PRECACHE=0, hold 120
#     t2_k, t2_cs0   T, full return, the level of lvl_s9.py, the form of the C5 reading (C5: salt of the tag + PRECACHE=0;
#                    APP: nothing more; the plan is UNDETERMINED before c5_0 - rc 6); t2_cs0 + KYTY_CS_PRETRANSLATE=0
#     u_k            T, form U: the app caches mirrored from s10/empty_app (empty, MANIFEST sha EMPTY_SHA), GLCache NOT
#                    restored (copied before, returned after), KYTY_SHADER_SEED_PATH=C:/kyty/s288/s9/seeds
#                    KYTY_CACHE_MODE=prepare-cold, binary u (the installed 4aa62e95), the catalogue checked by sha before
#   BINARIES: the seal lines "s binary: <sha> <path>" (f3b3aa3b) and "u binary: <sha> <path>" (4aa62e95) of pred/05b_s.md (item 362 (d)).
#   THE LOCK line begins "go_s.sh <tag> " (cachex_s.py, unchanged, admits a write only from that prefix) and names go_s9.sh.
# EXIT CODES: 0 run done; 1 hard refusal / failed run / failed return; 2 usage; 4 BUSY (lock, stop file, idle) - no run;
#   6 a condition of item 355 is not met (sc_s9.py --allowed rc 6 or the plan UNDETERMINED) - no run, report to the lead;
#   7 a "GamePatch:" line in the log (item 342 (e)) - the tag is not counted.
#   DRY=1 prints the plan after the cheap refusals; DRY=2 prints the plan right after the lock check (FORM=c5|app for a T2 tag).
#   usage: go_s9.sh <tag>
T=${1:-}
ROOT=C:/kyty/s288
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s288/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
SNAP_APP="d8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4"
SNAP_DRV="1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028"
EMPTY_SHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SEEDS="C:/kyty/s288/s9/seeds"
SNAPDIR="C:/kyty/s288/snap0"
SNAPDRVDIR="C:/kyty/s288/snap0_drv"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
S9=$ROOT/s9
SC=$S9/sc_s9.py
PRED=pred/05b_s.md
RSLEEP=5
PLMAX=540
PLWAIT=${PLWAIT:-$PLMAX}
case "$T" in
  ''|*[!a-z0-9_]*) echo "usage: go_s9.sh <tag>  (see the header)"; exit 2;;
esac
log0() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $ROOT/go_s9.log; }
busy0() { log0 "go_s9.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
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
for G in $ROOT/s4/RETURN_FAILED $ROOT/s6/RETURN_FAILED $ROOT/s10/RETURN_FAILED; do
  if [ -e $G ]; then
    GT=""
    read -r GT < $G 2>/dev/null
    log0 "go_s9.sh $T refused (rc 1): the guard $G exists ($GT) - the lead removes it after the return by hand"
    echo "return failed guard $G: $GT"; exit 1
  fi
done
# item 342 (e): no S10 arm names a patch file
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA VK_LAYER_MESSAGE_ID_FILTER KYTY_GAME_PATCH
case "$PLWAIT" in
  ''|*[!0-9]*) log0 "go_s9.sh $T refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then
  log0 "go_s9.sh $T refused: PLWAIT $PLWAIT > $PLMAX"; echo "PLWAIT above $PLMAX"; exit 2
fi
cd "$ROOT" || exit 1
FORMX=""
if [ "${DRY:-0}" = "2" ] && [ -n "${FORM:-}" ]; then FORMX="--form $FORM"; fi
PLAN=$(python $SC --plan "$T" $FORMX 2>&1 | tr -d '\r')
case "$PLAN" in
  UNDETERMINED) log0 "go_s9.sh $T refused (rc 6): the T2 form is undetermined (no C5 reading) - report to the lead"
                echo "plan undetermined (rc 6)"; exit 6;;
  s10\ *) ;;
  *) log0 "go_s9.sh $T refused: unknown tag ($PLAN)"; echo "usage: unknown tag $T"; exit 2;;
esac
set -- $PLAN
LEVEL=$2; CLS=$3; MODE=$4; HOLD=$5; SALT=$6; PCW=$7; SRC=$8; SDRAWS=$9; TOUT=${10}; PRE0=${11}; CS0=${12}; UU=${13}; BINK=${14}; FORMV=${15}
LD=$ROOT/s10
CLSX=""; [ "$CLS" = "T" ] && CLSX="KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1"
SALTX=""; [ "$SALT" = "1" ] && SALTX="KYTY_PIPELINE_SALT=$T"
PRE0X=""; [ "$PRE0" = "1" ] && PRE0X="KYTY_PIPELINE_PRECACHE=0"
CS0X=""; [ "$CS0" = "1" ] && CS0X="KYTY_CS_PRETRANSLATE=0"
PCWX=""; [ "$PCW" != "-" ] && PCWX="KYTY_S_PCW=$PCW KYTY_S_PCW_FORCE_MS=15000"
UX=""; [ "$UU" = "1" ] && UX="KYTY_SHADER_SEED_PATH=$SEEDS KYTY_CACHE_MODE=prepare-cold"
case "$MODE" in
  full) RSRC_APP="$SNAPDIR"; RSRC_GLC="$SNAPDRVDIR";;
  integrity) RSRC_APP="$LD/app_post/$SRC"; RSRC_GLC="$LD/glc_post/$SRC";;
  u) RSRC_APP="$LD/empty_app"; RSRC_GLC="-";;
  *) echo "usage: bad mode $MODE"; exit 2;;
esac
ENTER="python $S9/enter_scene_s9.py $T --root $LD --level $LEVEL --attempts 1 --stable-draws $SDRAWS --timeout $TOUT --no-install --require-idle --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED --rec --hold $HOLD KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 $CLSX $SALTX $PRE0X $CS0X $PCWX $UX"
if [ "${DRY:-0}" = "2" ]; then
  echo "PLAN $T: link s10, seal $PRED, binary the '$BINK binary:' line of $PRED; form $FORMV; restore app <- $RSRC_APP; restore glc <- $RSRC_GLC; $ENTER"
  exit 0
fi
L=$LD/go_s9.log
OUT=$LD/runs_s
TIMES=$LD/times.txt
MARK=$LD/attempt_$T.txt
mkdir -p $OUT
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
busy() { log "go_s9.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
if [ -e "$MARK" ] || [ -e "$LD/$T.json" ]; then
  log "go_s9.sh $T refused: attempt_$T.txt or $T.json exists - the one attempt of $T was made (no repeat)"
  echo "attempt already made"; exit 1
fi
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go_s9 call: PLWAIT="*" bash C:/kyty/s288/s9/go_s9.sh $T")
        V=${PLINE#go_s9 call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go_s9.sh $T refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL')"
  echo "PLWAIT differs from the seal"; exit 1
fi
RUNSHA=""; RUNBIN=""
while IFS= read -r PLINE || [ -n "$PLINE" ]; do
  PLINE=${PLINE%$'\r'}
  case "$PLINE" in
    "$BINK binary: "*) V=${PLINE#$BINK binary: }; RUNSHA=${V%% *}; RUNBIN=${V#* };;
  esac
done < "$PRED"
if [ -z "$RUNSHA" ]; then
  log "go_s9.sh $T refused: the seal $PRED has no line '$BINK binary: <sha256> <path>'"; echo "no $BINK binary"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY $T: level $LEVEL class $CLS mode $MODE form $FORMV; install $RUNBIN ($RUNSHA); restore app <- $RSRC_APP; restore glc <- $RSRC_GLC; $ENTER"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$RUNBIN" ] || [ "$(sha "$RUNBIN")" != "$RUNSHA" ]; then
  log "go_s9.sh $T refused: the arm binary $RUNBIN missing or its sha != $RUNSHA"; echo "arm binary bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go_s9.sh $T refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1
fi
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
X=$(python $ROOT/cachex_s.py where glc 2>&1); WRC=$?
log "$X"
if [ "$WRC" != "0" ]; then
  log "go_s9.sh $T refused (rc 1): the GLCache path of the environment is not the known folder (RC9)"; echo "glcache path: $X"; exit 1
fi
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*_s|test_[a-z0-9_]*_s|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s9 $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | sed -E "s/\('[^']*'/('<app>'/g" | cut -c1-300)" >> $TIMES
}
guards() {
  python $ROOT/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
  return 0
}
log "go_s9.sh $T requested (level $LEVEL, class $CLS, mode $MODE, form $FORMV, binary $RUNSHA, hold $HOLD, PLWAIT=$PLWAIT)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $SC --check-seal --seal $ROOT/$PRED >> $L 2>&1; then
  log "sc_s9.py --check-seal refused - not starting"; echo "seal check failed"; exit 1
fi
python $SC --allowed $T >> $L 2>&1
ARC=$?
if [ "$ARC" = "6" ]; then
  log "go_s9.sh $T refused (rc 6): a condition of item 355 is not met (see the ALLOWED line above) - report to the lead"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s9 $T refused rc 6: $(grep "ALLOWED $T" $L | tail -1)" >> $TIMES
  echo "condition not met"; exit 6
fi
if [ "$ARC" != "0" ]; then log "go_s9.sh $T refused: order (rc $ARC)"; echo "order"; exit 1; fi
if [ "$UU" = "1" ]; then
  X=$(python $SC --seeds-check 2>&1); SRC_RC=$?
  X=$(echo "$X" | tr -d '\r')
  log "$X"
  if [ "$SRC_RC" != "0" ]; then log "go_s9.sh $T refused (rc 1): the S-cat catalogue is not the sealed one"; echo "seeds bad"; exit 1; fi
fi
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
set -o noclobber
if ! { echo "go_s.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S) (go_s9.sh seal 05b)" > $LOCK; } 2>/dev/null; then
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
tline() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s9 $T $*" >> $TIMES; }
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
INSTALLED=1
cp "$RUNBIN" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$RUNSHA" ] || { log "installed sha != $RUNSHA - stop"; exit 1; }
log "files: $(sha256sum $SC $S9/test_sc_s9.py $S9/mut_sc_s9.py $S9/enter_scene_s9.py $S9/go_s9.sh cachex_s.py sc_s.py $PRED gates_default.txt idle142.py procload.py sheet142.py fgcpu143.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
X=$($CX man app 2>&1); log "$X"; $CX note $CJ man_pre_app sha=$(shaof "$X") >> $L 2>&1
X=$($CX man glc 2>&1); log "$X"; $CX note $CJ man_pre_glc sha=$(shaof "$X") >> $L 2>&1
X=$($CX copy app $LD/installed_pre --replace 2>&1) || { log "$X"; exit 1; }; log "$X"
X=$($CX copy glc $LD/glc_pre --replace 2>&1) || { log "$X"; exit 1; }; log "$X"
$CX note $CJ glc_pre_copy sha=$(mansha $LD/glc_pre) path=$LD/glc_pre >> $L 2>&1
$CX note $CJ installed_pre_copy sha=$(mansha $LD/installed_pre) >> $L 2>&1
if [ "$MODE" = "u" ]; then
  mkdir -p $LD/empty_app && : > $LD/empty_app/MANIFEST.txt
  WANT_APP=$EMPTY_SHA
  X=$(python $SC --seeds-check 2>&1 | tr -d '\r'); log "$X"
  $CX note $CJ seeds sha=$(echo "$X" | sed -n 's/^seeds sha \([0-9a-f]\{64\}\).*/\1/p') >> $L 2>&1
elif [ "$MODE" = "integrity" ]; then WANT_APP=$(mansha "$RSRC_APP"); else WANT_APP=$SNAP_APP; fi
if [ "$MODE" = "full" ]; then WANT_GLC=$SNAP_DRV; elif [ "$MODE" = "integrity" ]; then WANT_GLC=$(mansha "$RSRC_GLC"); else WANT_GLC="-"; fi
X=$($CX verify app "$RSRC_APP" "$WANT_APP" 2>&1); VA=$?; log "$X"
VG=0
if [ "$MODE" != "u" ]; then X=$($CX verify glc "$RSRC_GLC" "$WANT_GLC" 2>&1); VG=$?; log "$X"; fi
tline "verify the restore sources before the arm: app rc $VA ($RSRC_APP) glc rc $VG ($RSRC_GLC)"
if [ "$VA" != "0" ] || [ "$VG" != "0" ]; then log "a restore source does not verify - no run"; echo "verify failed"; exit 1; fi
TOUCHED=1
X=$($CX restore app "$RSRC_APP" "$WANT_APP" 2>&1); RA=$?; log "$X"
$CX note $CJ restore_app expected=$WANT_APP got=$(shaof "$X") source=$RSRC_APP >> $L 2>&1
RG=0
if [ "$MODE" != "u" ]; then
  X=$($CX restore glc "$RSRC_GLC" "$WANT_GLC" 2>&1); RG=$?; log "$X"
  $CX note $CJ restore_glc expected=$WANT_GLC got=$(shaof "$X") source=$RSRC_GLC >> $L 2>&1
fi
tline "restore before the arm: app rc $RA ($RSRC_APP, $WANT_APP) glc rc $RG ($RSRC_GLC, $WANT_GLC)"
if [ "$RA" != "0" ] || [ "$RG" != "0" ]; then log "restore before the arm failed - no run"; echo "restore failed"; exit 1; fi
OLD=$LD/old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "$T.refused.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" \
         "rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt"; do
  if [ -f "$LD/$F" ]; then mkdir -p "$OLD"; mv "$LD/$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
echo "go_s9.sh $T pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) binary $RUNSHA" > $MARK
tline "enter_scene start (level $LEVEL, class $CLS, mode $MODE, form $FORMV, hold $HOLD)"
log "$T start: $ENTER"
X=$($CX man glc --save $OUT/$T.glc_launch.txt 2>&1); $CX note $CJ man_launch_glc sha=$(shaof "$X") >> $L 2>&1
RECIPES="$(dirname "$GAME")/_ShaderCache/PPSA21564/pipelines.bin"
$CX note $CJ recipes_launch sha=$(sha "$RECIPES") >> $L 2>&1
$ENTER > $LD/$T.stdout.txt 2>&1
RC=$?
$CX note $CJ recipes_post sha=$(sha "$RECIPES") >> $L 2>&1
tline "enter_scene end rc $RC log_$T.txt sha256 $(sha $LD/log_$T.txt)"
log "$T rc=$RC $(tail -1 $LD/$T.stdout.txt)"
if [ "$RC" = "3" ] && [ ! -e "$LD/$T.json" ]; then
  if [ -f "$LD/$T.refused.json" ]; then
    mkdir -p "$OLD"; mv "$MARK" "$OLD/" && log "idle refusal inside enter_scene: no attempt made, marker moved to $OLD/"
  fi
  busy "the idle criterion inside enter_scene_s9.py refused (see $T.refused.json) - no run"
fi
X=$($CX man app 2>&1); log "$X"; $CX note $CJ man_post_app sha=$(shaof "$X") >> $L 2>&1
X=$($CX man glc --save $OUT/$T.glc_post.txt 2>&1); log "$X"; $CX note $CJ man_post_glc sha=$(shaof "$X") >> $L 2>&1
tline "manifests after the arm: app $(grep 'man app' $L | tail -1 | sed 's/.*sha //') glc $(grep 'man glc' $L | tail -1 | sed 's/.*sha //')"
case "$T" in
  pi_w1|pi_w0)
    X=$($CX copy glc $LD/glc_post/$T --replace 2>&1); log "$X"
    $CX note $CJ glc_post_copy sha=$(mansha $LD/glc_post/$T) path=$LD/glc_post/$T >> $L 2>&1
    X=$($CX copy app $LD/app_post/$T --replace 2>&1); log "$X"
    $CX note $CJ app_post_copy sha=$(mansha $LD/app_post/$T) path=$LD/app_post/$T >> $L 2>&1;;
esac
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
tline "scorer rc $SCRC score_$T.txt sha256 $(sha $LD/score_$T.txt)"
case "$T" in
  pi_*) python $SC --haze-sheet $T > $LD/haze_sheet_$T.txt 2>&1
        tline "haze sheet rc $? haze_sheet_$T.txt sha256 $(sha $LD/haze_sheet_$T.txt)";;
esac
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
  *) log "go_s9.sh $T: $GP lines GamePatch: - an interference of item 342 (e) (rc 7)"
     echo "GAMEPATCH interference: $GP lines (item 342 (e))"; exit 7;;
esac
if [ "$RC" != "0" ]; then exit 1; fi
exit 0
