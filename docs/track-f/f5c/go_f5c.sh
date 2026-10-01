#!/bin/bash
# Track F link F5c (HPP-357; ROADMAP "SESSION 122" item 273 (e)(3)(a)-(g), window of item 278 (v), RC3 of item 280 (e),
# binary and N1/N2 of item 285 (v); lock queue item 228 (v)): the four runs of item 273 (e)(3) on the binary of the B37 fix
# (F5a2, 6f495a65, accepted by F5b2 PASS) as ONE series under ONE lock - the fix binary is installed once and the installed
# build 9235a7ac and the caches come back in the same command (EXIT trap), so no other run can meet the fix binary or the
# caches written by it.
# Port of C:/kyty/f287/f4c/go_f4c2.sh (itself a port of C:/kyty/s143/go143a.sh): lock first, guards, one attempt, seal call
# line, stop file, lock.log UTC, times lines, cache copy/return by content lists, GLCache copy/return, idle wait before every
# tag with one retry of a BUSY refusal.  The recipe pre-check of F4c is dropped (B35 is not the subject here).
# ASCII only (item 175 (v)).  No emulator code, no build.
#   TAGS (item 273 (e)(3); one attempt each, a failure is data, no repeat); stand KYTY_TEST_MINIMIZE=60:10 in every tag;
#   level -lvl underwater_aerial_garden; order SEQ (variant of the executor, the seal names it): (a) -> (b) -> (v) -> (g):
#     f5c_a  (a) W, KYTY_FIX_MINIMIZE=1, form W of item 273 (k)(2): --vulkan-validation true, KYTY_PIPELINE_PRECACHE=0,
#            VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER (one message), VK_LAYER_DUPLICATE_MESSAGE_LIMIT; hold WHOLD s, no video
#     f5c_b  (b) control KYTY_FIX_MINIMIZE=0, the same stand and form: the stop with VUID 01689 is expected (the emulator ends)
#     f5c_v  (v) V, =1, no validation, video (KYTY_REC); hold VHOLD s; precache by default (shipped defaults)
#     f5c_g  (g) V, =0, no validation, no video; hold VHOLD s; the outcome is data
#   WINDOW EVENTS (item 280 (e)(2)): 'Window 1 minimized' / 'Recovering Vulkan swapchain' are expected here and stop nothing.
#   SERIES STOP (f5c_read.py --stop-check): a tag not admitted or without a log; NOT EVALUABLE (controls of the stand and of
#     the arm); a death marker without a [Vulkan][E] line in (a) or (v) (question to the lead).  The letters' FAIL, NO STOP of
#     (b) and the DATA of (g) are data: the series goes on.
#   CACHES (item 228 (v)): inside the lock, before the install: _ShaderCache/PPSA21564 copied to cache_snap/PPSA21564, the two
#     content lists equal (shalist_f2c.py); GLCache manifest (cachemf143.py) before and after and a copy glcache_snap/; EXIT
#     trap: the run's cache MOVED to cache_run/<UTC>/, the snapshot copied back, its list must equal the list before (else
#     RESTORE FAILED, rc 1); GLCache back from its copy (GLRESTORE=1).  A failed return writes the stop file C:/kyty/f287/STOP.
#   BINARY: BIN_F5C / BIN_EXPECT - item 285 (v); KYTY_FIX_DUALSRC/B26/B1B, KYTY_S_PCW, KYTY_PVAR never passed (the binary
#     4fc501f4 + F5 does not read them); before the lock and the install the binary must hold the translation signature
#     699c1e4b... and the strings "SwapchainZeroExtent: begin" and "TestMinimize: armed"; else rc 1.
#   LOCK WINDOW (win_f5c.py, a times line with the answer): HPP-367, HPP-342, HPP-337 done without a run; HPP-350 (s145 step 0),
#     HPP-352 (s145 series), HPP-364 (P17), HPP-370 (FSc) neither todo nor in_progress and without a run; else BUSY rc 4.
#   STOP FILE (general rule 26): C:/kyty/f287/STOP -> rc 4 before anything, before the lock and before every tag.
#   THE SEAL'S CALL (item 105 (v)): the seal carries exactly one line "go_f5c call: PLWAIT=<n> bash
#     C:/kyty/f287/f5c/go_f5c.sh series"; f5c_read.py --check-seal checks every "seal:" line before the lock.
#   THE LOCK: checked before any process and before every guard stage; "lock taken|released series <UTC>" -> lock.log;
#     every event -> one UTC line of C:/kyty/f287/times.txt at the moment of the event.
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, --pred of the seal; KYTY_GPU_CHECKPOINTS never passed.
# EXIT CODES: 0 series done (read score_<tag>.txt); 1 hard refusal / series stopped / restore failed;
#   2 usage / not configured; 4 BUSY (lock, stop file, guards, idle) - no run.
#   DRY=1 go_f5c.sh series prints the plan and exits 0 after the cheap refusals, before any guard, lock or install.
T=${1:-}
ROOT=C:/kyty/f287/f5c
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/f287/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"
BIN_F5C="C:/kyty/f287/bin/kyty_emulator_6f495a65.exe"
BIN_EXPECT="6f495a65388a90a0381c9170f224777e84cb07d657115ad2a8662fa0bae168dd"
SIGSTR="699c1e4b7db359067b461e029b913c4b6e78dc90"
GLRESTORE="1"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
VKDUP="1000000"
VKFILTER="Undefined-Value-ShaderOutputNotConsumed-DynamicRendering"
STANDV="60:10"
PRED="pred/f5c.md"
CACHE="/c/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564"
SNAP=$ROOT/cache_snap/PPSA21564
GLSNAP=$ROOT/glcache_snap
SKY=underwater_aerial_garden
VHOLD="330"
WHOLD="310"
SEQ="f5c_a f5c_b f5c_v f5c_g"
RSLEEP=5
PLMAX=540
PLWAIT=${PLWAIT:-$PLMAX}
if [ "$T" != "series" ]; then echo "usage: go_f5c.sh series  (see the header)"; exit 2; fi
L=$ROOT/go_f5c.log
TIMES=/c/kyty/f287/times.txt
LOCKLOG=$ROOT/lock.log
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
tl() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F5c go_f5c $*" >> $TIMES; }
busy() { log "go_f5c.sh refused BUSY (rc 4): $* - no run made"; echo "busy: $*"; exit 4; }
if [ -e $STOPF ]; then
  STOPTXT=""
  read -r STOPTXT < $STOPF 2>/dev/null
  busy "stop file $STOPF: $STOPTXT"
fi
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
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_DUALSRC KYTY_FIX_B1B KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW KYTY_PVAR KYTY_FIX_MINIMIZE KYTY_TEST_MINIMIZE KYTY_REC VK_LAYER_MESSAGE_ID_FILTER
if [ -z "$BIN_F5C" ] || [ -z "$BIN_EXPECT" ] || [ -z "$GLRESTORE" ] || [ -z "$SEQ" ]; then
  log "go_f5c.sh refused: not configured (BIN_F5C/BIN_EXPECT/GLRESTORE/SEQ - item 285 (v))"
  echo "not configured"; exit 2
fi
case "$PLWAIT" in
  ''|*[!0-9]*) log "go_f5c.sh refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then log "go_f5c.sh refused: PLWAIT $PLWAIT > $PLMAX"; echo "PLWAIT above $PLMAX"; exit 2; fi
for C in $SEQ; do
  if [ -e "attempt_$C.txt" ] || [ -e "$C.json" ]; then
    log "go_f5c.sh refused: attempt_$C.txt or $C.json exists - the one attempt of the series was made (no repeat)"
    echo "attempt already made"; exit 1
  fi
done
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go_f5c call: PLWAIT="*" bash C:/kyty/f287/f5c/go_f5c.sh series")
        V=${PLINE#go_f5c call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go_f5c.sh refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL')"
  echo "PLWAIT differs from the seal"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY series: tags $SEQ; stop file?; lock?; PLWAIT=$PLWAIT; binary sha + strings (signature $SIGSTR, SwapchainZeroExtent: begin, TestMinimize: armed); procload --wait-s $PLWAIT; f5c_read --check-seal; cpu < 15; idle142; procload --wait-s 0; stop file?; window win_f5c (HPP-367/HPP-342/HPP-337 done; HPP-350/HPP-352/HPP-364/HPP-370 not waiting); lock (lock.log UTC); shader cache list + copy to $SNAP (lists equal); GLCache manifest + copy (GLRESTORE=$GLRESTORE); fgcpu143 --save; install $BIN_F5C ($BIN_EXPECT); per tag: stop file?, idle142 wait up to 300 s, enter_scene.py <tag> --level $SKY --attempts 1 --no-install --require-idle --pred $ROOT/$PRED (a: W =1; b: W =0; W: --emu-arg=--vulkan-validation true --hold $WHOLD KYTY_PIPELINE_PRECACHE=0 VK_LAYER_PATH VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER; v: V =1 --rec --hold $VHOLD; g: V =0 --hold $VHOLD) KYTY_TEST_MINIMIZE=$STANDV KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, one retry of a BUSY refusal, log sha, glitch+sheet (v), f5c_read --tag, f5c_read --stop-check; EXIT: restore $BUILD_PINNED ($BUILD_EXPECT), move run cache to cache_run/, copy snapshot back (list = before), GLCache manifest after + restore, fgcpu143 row, unlock"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then
  log "go_f5c.sh refused: pinned copy $BUILD_PINNED missing or its sha != $BUILD_EXPECT"; echo "pinned build bad"; exit 1
fi
if [ ! -f "$BIN_F5C" ] || [ "$(sha "$BIN_F5C")" != "$BIN_EXPECT" ]; then
  log "go_f5c.sh refused: fix binary $BIN_F5C missing or its sha != $BIN_EXPECT"; echo "fix binary bad"; exit 1
fi
NSIG=$(LC_ALL=C grep -a -F -c "$SIGSTR" "$BIN_F5C")
NZE=$(LC_ALL=C grep -a -F -c "SwapchainZeroExtent: begin" "$BIN_F5C")
NARM=$(LC_ALL=C grep -a -F -c "TestMinimize: armed" "$BIN_F5C")
if [ "$NSIG" = "0" ] || [ "$NZE" = "0" ] || [ "$NARM" = "0" ]; then
  log "go_f5c.sh refused: fix binary strings - signature $SIGSTR lines $NSIG, SwapchainZeroExtent: begin $NZE, TestMinimize: armed $NARM"
  echo "fix binary strings bad"; exit 1
fi
if [ "$(sha "$GAME")" != "$BUILD_EXPECT" ]; then
  log "go_f5c.sh refused: the installed $GAME is not $BUILD_EXPECT before the series - not starting"; echo "installed build bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go_f5c.sh refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1
fi
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
GLDIR="$LOCALAPPDATA/NVIDIA/GLCache"
mkdir -p runs
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*|test_[a-z0-9_]*f5c|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F5c go_f5c BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)" >> $TIMES
}
guards() {
  python $ROOT/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
  return 0
}
log "go_f5c.sh series requested (fix binary $BIN_EXPECT, installed $BUILD_EXPECT, PLWAIT=$PLWAIT, seq $SEQ)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $ROOT/f5c_read.py --check-seal $ROOT/$PRED >> $L 2>&1; then
  log "f5c_read.py --check-seal refused (see above) - not starting"; echo "seal check failed"; exit 1
fi
lockheld
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
log "idle check cpu=$CPU (< 15)"
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
WIN=$(python $ROOT/win_f5c.py 2>&1 | tail -1 | tr -d '\r')
tl "lock window (win_f5c, p.228(v), 285(v)): $WIN"
case "$WIN" in
  *"-> open") ;;
  *) busy "lock window closed or unknown: $WIN";;
esac
lockheld
set -o noclobber
if ! { echo "go_f5c.sh series pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  busy "lock taken by someone else: $(cat $LOCK 2>/dev/null)"
fi
set +o noclobber
echo "lock taken series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG
tl "lock taken (winpid $WINPID)"
INSTALLED=0
RETFAIL=0
SNAPPED=0
GLSNAPPED=0
LIST_BEFORE=""
restore_bin() {
  for i in 1 2 3; do
    if cp "$BUILD_PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$BUILD_EXPECT" ]; then return 0; fi
    sleep $RSLEEP
  done
  return 1
}
finish() {
  RCX=$?
  if [ "$INSTALLED" = "1" ]; then
    if restore_bin; then
      log "restored $BUILD_PINNED ($BUILD_EXPECT) into $GAME"; tl "restore binary ok sha256 $(sha "$GAME")"
    else
      log "RESTORE FAILED: $GAME sha $(sha "$GAME") != $BUILD_EXPECT"; tl "RESTORE BINARY FAILED sha256 $(sha "$GAME")"
      echo "restore failed"; RCX=1; RETFAIL=1
    fi
  fi
  if [ "$SNAPPED" = "1" ]; then
    LIST_RUN=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_run.txt 2>&1 | tail -1 | tr -d '\r')
    tl "shader cache at the end of the series (before the return): $LIST_RUN"
    KEEP=$ROOT/cache_run/$(date -u +%Y%m%dT%H%M%SZ)
    mkdir -p "$KEEP"
    if mv "$CACHE" "$KEEP/" && cp -a "$SNAP" "$CACHE"; then
      LIST_BACK=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_back.txt 2>&1 | tail -1 | tr -d '\r')
      if [ "$LIST_BACK" = "$LIST_BEFORE" ]; then
        tl "shader cache returned: $LIST_BACK = before; run cache kept in $KEEP"
      else
        tl "SHADER CACHE RESTORE FAILED: back '$LIST_BACK' != before '$LIST_BEFORE'"; echo "cache restore failed"; RCX=1; RETFAIL=1
      fi
    else
      tl "SHADER CACHE RESTORE FAILED: move/copy error ($CACHE, $KEEP, $SNAP)"; echo "cache restore failed"; RCX=1; RETFAIL=1
    fi
  fi
  if [ "$GLSNAPPED" = "1" ]; then
    CMA=$(python $ROOT/cachemf143.py runs/cache_series.after.json 2>&1 | tail -1 | tr -d '\r')
    tl "cache manifest after the series (before any GLCache return): $CMA"
    if [ "$GLRESTORE" = "1" ]; then
      GLKEEP=$ROOT/glcache_run/$(date -u +%Y%m%dT%H%M%SZ)
      mkdir -p "$GLKEEP"
      if mv "$GLDIR" "$GLKEEP/" && cp -a "$GLSNAP/GLCache" "$GLDIR"; then
        GLB=$(python $ROOT/shalist_f2c.py "$GLDIR" 2>&1 | tail -1 | tr -d '\r')
        if [ "$GLB" = "$GL_BEFORE" ]; then tl "GLCache returned: $GLB = before"; else tl "GLCACHE RESTORE FAILED: '$GLB' != '$GL_BEFORE'"; RCX=1; RETFAIL=1; fi
      else
        tl "GLCACHE RESTORE FAILED: move/copy error"; RCX=1; RETFAIL=1
      fi
    fi
  fi
  if [ "$RETFAIL" = "1" ]; then
    echo "F5c binary or cache return failed $(date -u +%Y-%m-%dT%H:%M:%SZ) - track F stopped, comment in HPP-357" > $STOPF
    tl "stop file written: binary or cache return failed"
  fi
  FG=$(python $ROOT/fgcpu143.py --since runs/fgcpu_series.a.json --chain-pid $WINPID 2>&1 | tail -1 | tr -d '\r')
  tl "foreign cpu at the end inside the lock: $FG"
  rm -f $LOCK
  echo "lock released series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG
  tl "lock released (rc $RCX)"
  exit $RCX
}
trap finish EXIT
# caches before the install (item 228 (v))
LIST_BEFORE=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_before.txt 2>&1 | tail -1 | tr -d '\r')
tl "shader cache before the series: $LIST_BEFORE"
rm -rf "$ROOT/cache_snap"
mkdir -p "$ROOT/cache_snap"
cp -a "$CACHE" "$SNAP" || { tl "shader cache copy failed - stop"; exit 1; }
LIST_SNAP=$(python $ROOT/shalist_f2c.py "$SNAP" 2>&1 | tail -1 | tr -d '\r')
[ "$LIST_SNAP" = "$LIST_BEFORE" ] || { tl "shader cache copy differs: '$LIST_SNAP' != '$LIST_BEFORE' - stop"; exit 1; }
SNAPPED=1
tl "shader cache copy = before ($ROOT/cache_snap)"
CMB=$(python $ROOT/cachemf143.py runs/cache_series.before.json 2>&1 | tail -1 | tr -d '\r')
tl "cache manifest before the series: $CMB"
GL_BEFORE=$(python $ROOT/shalist_f2c.py "$GLDIR" 2>&1 | tail -1 | tr -d '\r')
rm -rf "$GLSNAP"
mkdir -p "$GLSNAP"
cp -a "$GLDIR" "$GLSNAP/GLCache" || { tl "GLCache copy failed - stop"; exit 1; }
GL_SNAP=$(python $ROOT/shalist_f2c.py "$GLSNAP/GLCache" 2>&1 | tail -1 | tr -d '\r')
[ "$GL_SNAP" = "$GL_BEFORE" ] || { tl "GLCache copy differs: '$GL_SNAP' != '$GL_BEFORE' - stop"; exit 1; }
GLSNAPPED=1
tl "GLCache before the series: $GL_BEFORE (copy equal, GLRESTORE=$GLRESTORE)"
python $ROOT/fgcpu143.py --save runs/fgcpu_series.a.json >> $L 2>&1
INSTALLED=1
cp "$BIN_F5C" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "installed sha != $BIN_EXPECT - stop"; tl "install failed"; exit 1; }
tl "installed fix binary sha256 $BIN_EXPECT"
log "files: $(sha256sum f5c_read.py shalist_f2c.py win_f5c.py $PRED gates_default.txt enter_scene.py idle142.py procload.py go_f5c.sh sheet142.py fgcpu143.py cachemf143.py C:/kyty/s142/sc142.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
IDLEMAX=300
IDLESTEP=15
idlewait() {
  WS=0
  while :; do
    if [ -e $STOPF ]; then tl "$1 stop file during the idle wait: $(head -1 $STOPF)"; return 1; fi
    if python $ROOT/idle142.py >> $L 2>&1; then tl "$1 idle142 IDLE after $WS s of wait"; return 0; fi
    WS=$((WS+IDLESTEP))
    if [ $WS -gt $IDLEMAX ]; then tl "$1 idle142 still BUSY after $IDLEMAX s of wait"; return 1; fi
    sleep $IDLESTEP
  done
}
runtag() {
  echo "go_f5c.sh $C pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) fix binary $BIN_EXPECT" > attempt_$C.txt
  tl "$C enter_scene start$1 (level $SKY, hold $HOLD, extra '$EXTRA', emu '$EMUX')"
  python $ROOT/enter_scene.py $C --level $SKY --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt \
    --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_TEST_MINIMIZE=$STANDV KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $C.stdout.txt 2>&1
}
refused() { [ "$1" = "3" ] && [ -e $C.refused.json ] && [ ! -e log_$C.txt ] && [ ! -e $C.json ]; }
SERIES_RC=0
for C in $SEQ; do
  if [ -e $STOPF ]; then tl "stop file before $C: $(head -1 $STOPF) - series stopped"; SERIES_RC=1; break; fi
  REC=""; EMUX=""; EXTRA=""
  case "$C" in
    f5c_a|f5c_b)
      SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD
      EMUX="--emu-arg=--vulkan-validation --emu-arg=true"
      WX="KYTY_FIX_MINIMIZE=1"; [ "$C" = "f5c_b" ] && WX="KYTY_FIX_MINIMIZE=0"
      EXTRA="$WX KYTY_PIPELINE_PRECACHE=0 VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER";;
    f5c_v) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec"; EXTRA="KYTY_FIX_MINIMIZE=1";;
    f5c_g) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; EXTRA="KYTY_FIX_MINIMIZE=0";;
  esac
  if ! idlewait $C; then tl "$C series stop BUSY before the tag (not an attempt) - question to the lead"; SERIES_RC=1; break; fi
  runtag ""
  RC=$?
  if refused $RC; then
    for F in attempt_$C.txt $C.refused.json $C.stdout.txt; do mv "$F" "${F/$C/$C.busyr1}"; done
    tl "$C enter_scene refused BUSY before the emulator start (not an attempt): $(grep -o 'REFUSED.*' $C.busyr1.stdout.txt | head -1 | cut -c1-160)"
    if ! idlewait $C; then tl "$C series stop BUSY before the retry (not an attempt) - question to the lead"; SERIES_RC=1; break; fi
    runtag " (retry after a BUSY refusal)"
    RC=$?
    if refused $RC; then tl "$C second BUSY refusal before the emulator start (not an attempt) - series stop, question to the lead"; SERIES_RC=1; break; fi
  fi
  tl "$C enter_scene end rc $RC log_$C.txt sha256 $(sha log_$C.txt)"
  if [ -n "$REC" ]; then
    if [ -f "rec_$C.mp4" ]; then
      python $VIDGLITCH rec_$C.mp4 4 6 $ROOT/vidframes_$C > glitch_$C.txt 2>&1
      tl "$C s51_vidglitch rc $? glitch_$C.txt sha256 $(sha glitch_$C.txt) rec_$C.mp4 sha256 $(sha rec_$C.mp4) idx sha256 $(sha rec_$C.mp4.idx)"
      python $ROOT/sheet142.py rec_$C.mp4 sheet_$C.png > sheet_$C.txt 2>&1
      tl "$C sheet rc $? sheet_$C.png sha256 $(sha sheet_$C.png)"
    else
      tl "$C no video rec_$C.mp4"
    fi
  fi
  python $ROOT/f5c_read.py --tag $C --json runs/$C.read.json > score_$C.txt 2>&1
  tl "$C reader rc $? score_$C.txt sha256 $(sha score_$C.txt): $(grep '^F5C VERDICT' score_$C.txt | tr '\n' ';')"
  SC=$(python $ROOT/f5c_read.py --stop-check runs/$C.read.json 2>&1 | tail -1 | tr -d '\r')
  tl "$C stop check (enter_scene rc $RC): $SC"
  case "$SC" in
    "continue"*) ;;
    *) tl "$C series stop: $SC - later tags not run, question to the lead"; SERIES_RC=1; break;;
  esac
done
exit $SERIES_RC
