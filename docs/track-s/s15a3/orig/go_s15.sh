#!/bin/bash
# Track S, link S15a (HPP-601; ROADMAP "SESSION 122" item 511 (z)): the port of s13/go_s13.sh (seal 13) for link S15b - the
# directory C:/kyty/s288/s15, the seal pred/14_s.md or its edition pred/14b_s.md (pred/13_s.md and pred/13b_s.md are not in force
# for these arms); item 511 (z)(3): the collection arms hold 300 s (sc_s15.py HOLD_K); item 511 (z)(4)-(5): a U arm runs
# s15/enter_scene_s15.py with --hold-u <the 11th field of its plan> (120:3000:300 - held while the presented time after the first
# scene frame (or the entry line) is < 120 s or the video < 3 000 frames, at most 300 s); k_NN and w13 carry "-" (a fixed hold).
# Everything else is the S13 harness unchanged; its header follows.
# Port header: Track S, link S13a (HPP-498; ROADMAP "SESSION 122" item 408 (e), (l), item 229 (e)(1), (3), item 410 (g)(6)(iii), item 414, item 419 (v) Z3, item 428 (v)),
# reworked by S13a3 (HPP-537, item 436 (b)(5), (v)): the guards are ANY C:/kyty/s288/*/RETURN_FAILED and */IN_ARM (RC5 of S13r);
# S13a4 (HPP-553, item 452 (d)(2)): the seal in force was pred/13_s.md or its edition pred/13b_s.md (pred/12_s.md and
# pred/11_s.md were not in force); S15a: pred/14_s.md or pred/14b_s.md.
# the game chain of link S13b - the collection arms k_01 .. k_19 into C:/kyty/s288/s15/cat, the U arms u_01 .. u_19 on the
# exported catalogue C:/kyty/s288/s15/seeds, the W of Sky Garden w13.  Port of C:/kyty/s288/s9/go_s9.sh (seal 07): stop file,
# lock first, RETURN_FAILED / IN_ARM guards, procload, idle, one attempt, the seal call line, the foreign-CPU row, the return of
# the caches by sha (item 228 (v)), the GamePatch interference (item 342 (e)).  ASCII only.  No emulator code, no build.  One
# tag per lock.
#   TAGS and their arm (s15/sc_s15.py --plan <tag>; order and conditions sc_s15.py --allowed <tag>):
#     k_NN  M, mode cat: the app caches mirrored from s15/empty_app (k_01) or from the post copy s15/cat/<k_NN-1> of the previous
#           arm; GLCache as found (copied before, returned after); after the arm the app caches are copied to s15/cat/<tag>;
#           hold 180, no video
#     u_NN  T, mode u (form U): the app caches mirrored from s15/empty_app, GLCache as found, KYTY_SHADER_SEED_PATH=
#           C:/kyty/s288/s15/seeds KYTY_CACHE_MODE=prepare-cold, the catalogue checked by sha before; hold 120, video
#     w13   M, mode u + validation (item 295 (b)): --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=
#           100000000, no VK_LAYER_MESSAGE_ID_FILTER; hold 330, no video
#   BINARY: the INSTALLED one - no install.  The seal line "installed: <sha256> <signature> <variant>" (sc_s15.py --installed)
#     names it; "installed: PENDING" (seal 13, until its edition) refuses rc 6 before the lock - an edition
#     of the seal by a lead item names it.  Inside the lock the installed binary must be that sha, else no arm (rc 1).
#   KNOB (item 419 (v) Z3, item 428 (v)(1)): every arm names KYTY_S_PCW=1 positionally (SPCW, after S12 an absent knob means 1);
#     the caller's KYTY_S_PCW, KYTY_S_PCW_FORCE_MS, KYTY_GAME_PATCH and every KYTY_FIX_* are unset before the arm.
#   GUARDS (item 436 (b)(5)): any $ROOT/*/RETURN_FAILED or $ROOT/*/IN_ARM (s4, s6, s10, s12, s13 or any later link directory)
#     refuses rc 1 before the lock and again right before it; the own s15/IN_ARM falls under the same rule before the arm writes it.
#   GUARD s15/IN_ARM: written before TOUCHED=1 (the tag, the installed sha, man_pre_app, man_pre_glc), removed only by a
#     successful return; S9r2 observation 1 (item 382 (b)): after a failed return (RETURN_FAILED written) no later return of the
#     same run removes it.  THE LOCK line begins "go_s.sh <tag> " (cachex_s.py admits a write only from that prefix) and names
#     go_s15.sh and the seal file of $PRED (S9r2 observation 2).
# EXIT CODES: 0 run done; 1 hard refusal / failed run / failed return; 2 usage; 4 BUSY (lock, stop file, idle) - no run;
#   6 a condition of item 408 (l) is not met (sc_s15.py --allowed rc 6, the seal line PENDING) - no run, report to the lead;
#   7 a "GamePatch:" line in the log (item 342 (e)) - the tag is not counted.
#   DRY=1 prints the plan after the cheap refusals; DRY=2 prints the plan right after the lock check.
#   usage: go_s15.sh <tag>
T=${1:-}
ROOT=C:/kyty/s288
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s288/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
EMPTY_SHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SEEDS="C:/kyty/s288/s15/seeds"
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
VKDUP="100000000"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
S13=$ROOT/s15
SC=$S13/sc_s15.py
ENTERPY=$ROOT/s15/enter_scene_s15.py
RSLEEP=5
PLMAX=540
PLWAIT=${PLWAIT:-$PLMAX}
case "$T" in
  ''|*[!a-z0-9_]*) echo "usage: go_s15.sh <tag>  (see the header)"; exit 2;;
esac
log0() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $ROOT/go_s15.log; }
busy0() { log0 "go_s15.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
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
  # item 436 (b)(5), RC5: every link directory of track S - a guard left by any harness (S12c's s12 among them) stops the arm
  for G in $ROOT/*/RETURN_FAILED $ROOT/*/IN_ARM; do
    if [ -e "$G" ]; then
      GT=""
      read -r GT < $G 2>/dev/null
      log0 "go_s15.sh $T refused (rc 1): the guard $G exists ($GT) - the lead removes it after the return by hand"
      echo "return failed guard $G: $GT"; exit 1
    fi
  done
}
guardfiles
# item 342 (e): no S13b arm names a patch file; item 428 (v)(1): the caller's S knobs and KYTY_FIX_* never reach an arm
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA VK_LAYER_MESSAGE_ID_FILTER KYTY_GAME_PATCH KYTY_S_PCW KYTY_S_PCW_FORCE_MS
for V in $(compgen -e); do case "$V" in KYTY_FIX_*) unset "$V";; esac; done
SPCW=1   # item 419 (v) Z3, item 428 (v)(1): every arm names KYTY_S_PCW=1 itself (after S12 an absent knob means 1, not 0)
case "$PLWAIT" in
  ''|*[!0-9]*) log0 "go_s15.sh $T refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then
  log0 "go_s15.sh $T refused: PLWAIT $PLWAIT > $PLMAX"; echo "PLWAIT above $PLMAX"; exit 2
fi
cd "$ROOT" || exit 1
# the seal in force: the edition pred/14b_s.md (13 with the line "installed:" named and the line "edition: base pred/14_s.md
# sha256 <sha>", a lead item) when it exists, else 13
PRED=$(python $SC --seal-path 2>&1 | tr -d '\r')
case "$PRED" in
  pred/14_s.md|pred/14b_s.md) ;;
  *) log0 "go_s15.sh $T refused: the seal path is not pred/14_s.md or pred/14b_s.md ($PRED)"; echo "seal path bad"; exit 1;;
esac
PLAN=$(python $SC --plan "$T" 2>&1 | tr -d '\r')
case "$PLAN" in
  s15\ *) ;;
  *) log0 "go_s15.sh $T refused: unknown tag ($PLAN)"; echo "usage: unknown tag $T"; exit 2;;
esac
set -- $PLAN
LEVEL=$2; CLS=$3; MODE=$4; HOLD=$5; SRC=$6; SDRAWS=$7; TOUT=$8; REC=$9; VAL=${10}; HU=${11:-}
if [ "$HU" = "-" ]; then HUX=""
elif [[ "$HU" =~ ^[0-9]+:[0-9]+:[0-9]+$ ]]; then HUX="--hold-u $HU"
else log0 "go_s15.sh $T refused: the hold rule field of the plan is not N:N:N or - ($PLAN)"; echo "bad hold rule"; exit 2
fi
LD=$ROOT/s15
CLSX=""; [ "$CLS" = "T" ] && CLSX="KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1"
UX=""; [ "$MODE" = "u" ] && UX="KYTY_SHADER_SEED_PATH=$SEEDS KYTY_CACHE_MODE=prepare-cold"
RECX=""; [ "$REC" = "1" ] && RECX="--rec"
VALX=""; VALE=""
if [ "$VAL" = "1" ]; then VALX="--emu-arg=--vulkan-validation --emu-arg=true"; VALE="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP"; fi
case "$MODE" in
  cat) if [ "$SRC" = "empty" ]; then RSRC_APP="$LD/empty_app"; else RSRC_APP="$LD/cat/$SRC"; fi;;
  u) RSRC_APP="$LD/empty_app";;
  *) echo "usage: bad mode $MODE"; exit 2;;
esac
ENTER="python $ENTERPY $T --root $LD --level $LEVEL --attempts 1 --stable-draws $SDRAWS --timeout $TOUT --no-install --require-idle --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED $RECX --hold $HOLD $HUX $VALX KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_S_PCW=$SPCW $CLSX $UX $VALE"
if [ "${DRY:-0}" = "2" ]; then
  echo "PLAN $T: link s15, seal $PRED, binary the installed one named by the line 'installed:' of $PRED; mode $MODE; restore app <- $RSRC_APP; glc as found; $ENTER"
  exit 0
fi
INSTL=$(python $SC --installed --seal $ROOT/$PRED 2>&1 | tr -d '\r')
set -- $INSTL
if [ "$1" != "installed" ] || [ -z "${2:-}" ] || [ "$2" = "MALFORMED" ]; then
  log0 "go_s15.sh $T refused: the seal $PRED has no well-formed line 'installed:' ($INSTL)"; echo "no installed line"; exit 1
fi
if [ "$2" = "PENDING" ]; then
  log0 "go_s15.sh $T refused (rc 6): the seal line 'installed: PENDING' - an edition of the seal by a lead item names the installed binary"
  echo "installed PENDING (rc 6)"; exit 6
fi
INST_WANT=$2; SIGW=${3:-}; VARW=${4:-}
L=$LD/go_s15.log
OUT=$LD/runs_s
TIMES=$LD/times.txt
MARK=$LD/attempt_$T.txt
mkdir -p $OUT
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
busy() { log "go_s15.sh $T refused BUSY (rc 4): $* - no run made, retry with a new call"; echo "busy: $*"; exit 4; }
if [ -e "$MARK" ] || [ -e "$LD/$T.json" ]; then
  log "go_s15.sh $T refused: attempt_$T.txt or $T.json exists - the one attempt of $T was made (no repeat)"
  echo "attempt already made"; exit 1
fi
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go_s15 call: PLWAIT="*" bash C:/kyty/s288/s15/go_s15.sh $T")
        V=${PLINE#go_s15 call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go_s15.sh $T refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL')"
  echo "PLWAIT differs from the seal"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY $T: level $LEVEL class $CLS mode $MODE; installed $INST_WANT $SIGW $VARW; restore app <- $RSRC_APP; glc as found; $ENTER"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go_s15.sh $T refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1
fi
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
X=$(python $ROOT/cachex_s.py where glc 2>&1); WRC=$?
log "$X"
if [ "$WRC" != "0" ]; then
  log "go_s15.sh $T refused (rc 1): the GLCache path of the environment is not the known folder (RC9)"; echo "glcache path: $X"; exit 1
fi
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*_s|test_[a-z0-9_]*_s|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s15 $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | sed -E "s/\('[^']*'/('<app>'/g" | cut -c1-300)" >> $TIMES
}
guards() {
  python $ROOT/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
  return 0
}
log "go_s15.sh $T requested (level $LEVEL, class $CLS, mode $MODE, installed $INST_WANT, hold $HOLD, PLWAIT=$PLWAIT)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $SC --check-seal --seal $ROOT/$PRED --game "$GAME" >> $L 2>&1; then
  log "sc_s15.py --check-seal refused - not starting"; echo "seal check failed"; exit 1
fi
python $SC --allowed $T >> $L 2>&1
ARC=$?
if [ "$ARC" = "6" ]; then
  log "go_s15.sh $T refused (rc 6): a condition of item 408 (l) is not met (see the ALLOWED line above) - report to the lead"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s15 $T refused rc 6: $(grep "ALLOWED $T" $L | tail -1)" >> $TIMES
  echo "condition not met"; exit 6
fi
if [ "$ARC" != "0" ]; then log "go_s15.sh $T refused: order (rc $ARC)"; echo "order"; exit 1; fi
if [ "$MODE" = "u" ]; then
  X=$(python $SC --seeds-check 2>&1); SRC_RC=$?
  X=$(echo "$X" | tr -d '\r')
  log "$X"
  if [ "$SRC_RC" != "0" ]; then log "go_s15.sh $T refused (rc 1): the catalogue s15/seeds is not seeds_manifest.txt"; echo "seeds bad"; exit 1; fi
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
guardfiles
set -o noclobber
if ! { echo "go_s.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S) (go_s15.sh seal $PRED)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  busy "lock taken by someone else: $(cat $LOCK 2>/dev/null)"
fi
set +o noclobber
echo "lock taken $T $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
CX="python $ROOT/cachex_s.py --tag $T"
CJ=$OUT/$T.cache.json
BINCHK=0
TOUCHED=0
RETURNED=0
RETFAIL=0
INARM_MINE=0
tline() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go_s15 $T $*" >> $TIMES; }
shaof() { echo "$1" | sed -n 's/.* sha \([0-9a-f]\{64\}\).*/\1/p' | tail -1; }
mansha() { sha "$1/MANIFEST.txt"; }
BINPRE=$LD/installed_bin_pre.exe
INST_SHA=""
restore_bin() {
  for i in 1 2 3; do
    if [ -n "$INST_SHA" ] && [ "$(sha "$GAME")" = "$INST_SHA" ]; then return 0; fi
    if [ -n "$INST_SHA" ] && [ "$(sha "$BINPRE")" = "$INST_SHA" ] && cp "$BINPRE" "$GAME" 2>/dev/null && \
       [ "$(sha "$GAME")" = "$INST_SHA" ]; then return 0; fi
    sleep $RSLEEP
  done
  return 1
}
return_failed() {
  RETFAIL=1
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
  if [ "$BINCHK" = "1" ]; then
    if restore_bin; then log "the installed binary is $INST_SHA after the arm"; BINCHK=0
    else log "RESTORE FAILED: $GAME sha $(sha "$GAME") != $INST_SHA"; rc=1; fi
    $CX note $CJ installed_after sha=$(sha "$GAME") >> $L 2>&1
  fi
  [ "$rc" = "0" ] || return_failed $rc
  # S9r2 observation 1 (item 382 (b)): a run with a failed return never removes the guard
  if [ "$rc" = "0" ] && [ "$RETFAIL" = "0" ] && [ "$INARM_MINE" = "1" ] && [ "$BINCHK" = "0" ] && \
     { [ "$TOUCHED" = "0" ] || [ "$RETURNED" = "1" ]; }; then
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
if [ "$INST_SHA" != "$INST_WANT" ]; then
  log "the installed binary before the arm $INST_SHA != the seal line installed: $INST_WANT - no arm"
  tline "installed binary before the arm $INST_SHA != $INST_WANT (seal line installed:) - no arm; a new installation needs a lead item"
  INST_SHA=""; echo "installed binary not $INST_WANT"; exit 1
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
BINCHK=1
tline "guard $LD/IN_ARM written (installed $INST_SHA, man_pre_app $MPA, man_pre_glc $MPG)"
log "files: $(sha256sum $SC $S13/test_sc_s15.py $S13/mut_sc_s15.py $ENTERPY $S13/go_s15.sh $S13/seedexp_s15.py cachex_s.py sc_s.py s9/sc_s9.py $PRED gates_default.txt idle142.py procload.py sheet142.py fgcpu143.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
X=$($CX copy app $LD/installed_pre --replace 2>&1) || { log "$X"; exit 1; }; log "$X"
X=$($CX copy glc $LD/glc_pre --replace 2>&1) || { log "$X"; exit 1; }; log "$X"
$CX note $CJ glc_pre_copy sha=$(mansha $LD/glc_pre) path=$LD/glc_pre >> $L 2>&1
$CX note $CJ installed_pre_copy sha=$(mansha $LD/installed_pre) >> $L 2>&1
mkdir -p $LD/empty_app && [ -f $LD/empty_app/MANIFEST.txt ] || : > $LD/empty_app/MANIFEST.txt
if [ "$MODE" = "u" ]; then
  X=$(python $SC --seeds-check 2>&1 | tr -d '\r'); log "$X"
  $CX note $CJ seeds sha=$(echo "$X" | sed -n 's/^seeds sha \([0-9a-f]\{64\}\).*/\1/p') >> $L 2>&1
fi
if [ "$MODE" = "cat" ] && [ "$SRC" != "empty" ]; then WANT_APP=$(mansha "$RSRC_APP"); else WANT_APP=$EMPTY_SHA; fi
X=$($CX verify app "$RSRC_APP" "$WANT_APP" 2>&1); VA=$?; log "$X"
tline "verify the restore source before the arm: app rc $VA ($RSRC_APP, $WANT_APP)"
if [ "$VA" != "0" ]; then log "the restore source does not verify - no run"; echo "verify failed"; exit 1; fi
TOUCHED=1
X=$($CX restore app "$RSRC_APP" "$WANT_APP" 2>&1); RA=$?; log "$X"
$CX note $CJ restore_app expected=$WANT_APP got=$(shaof "$X") source=$RSRC_APP >> $L 2>&1
tline "restore before the arm: app rc $RA ($RSRC_APP, $WANT_APP); GLCache as found"
if [ "$RA" != "0" ]; then log "restore before the arm failed - no run"; echo "restore failed"; exit 1; fi
OLD=$LD/old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "$T.refused.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" \
         "rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt"; do
  if [ -f "$LD/$F" ]; then mkdir -p "$OLD"; mv "$LD/$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
echo "go_s15.sh $T pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) binary $INST_SHA" > $MARK
tline "enter_scene start (level $LEVEL, class $CLS, mode $MODE, hold $HOLD)"
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
X=$($CX man app 2>&1); log "$X"; $CX note $CJ man_post_app sha=$(shaof "$X") >> $L 2>&1
X=$($CX man glc --save $OUT/$T.glc_post.txt 2>&1); log "$X"; $CX note $CJ man_post_glc sha=$(shaof "$X") >> $L 2>&1
tline "manifests after the arm: app $(grep 'man app' $L | tail -1 | sed 's/.* sha //') glc $(grep 'man glc' $L | tail -1 | sed 's/.* sha //')"
if [ "$MODE" = "cat" ]; then
  X=$($CX copy app $LD/cat/$T --replace 2>&1); log "$X"
  $CX note $CJ app_post_copy sha=$(mansha $LD/cat/$T) path=$LD/cat/$T >> $L 2>&1
  tline "collected catalogue copied to $LD/cat/$T (MANIFEST.txt sha $(mansha $LD/cat/$T))"
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
tline "scorer rc $SCRC score_$T.txt sha256 $(sha $LD/score_$T.txt)"
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
  *) log "go_s15.sh $T: $GP lines GamePatch: - an interference of item 342 (e) (rc 7)"
     echo "GAMEPATCH interference: $GP lines (item 342 (e))"; exit 7;;
esac
if [ "$RC" != "0" ]; then exit 1; fi
exit 0
