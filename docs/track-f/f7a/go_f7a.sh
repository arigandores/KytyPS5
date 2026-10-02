#!/bin/bash
# Track F link F7a (HPP-397; ROADMAP "SESSION 122" item 327 (e)): ONE RenderDoc capture of the enemy_final arena (diagnosis of B39)
# under ONE lock.  Port of C:/kyty/f287/f6e/go_f6e.sh: lock first, guards (procload output masked, item 324 (i)), one attempt per
# call, plan call line, stop file, lock.log UTC, times lines, cache copy/return by content lists and the variant directory list,
# GLCache copy/return, idle wait before the tag with one retry of a BUSY refusal of enter_scene.py (item 279 (v)).
# ASCII only (item 175 (v)).  No emulator code, no build, NO INSTALL: the installed build dac02fb9 runs as it is (sha256 checked
# before the lock, as a times line inside, and at the end; the pinned copy C:/kyty/s146/kyty_emulator_dac02fb9.exe restores it
# only if the installed file changed).
# FORM (item 327 (e)): defaults (no KYTY_FIX_* in the environment - enter_scene.py passes no KYTY_* of the shell, only the pairs
#   below), no validation, precache by default (KYTY_PIPELINE_PRECACHE not passed), -lvl enemy_final, --rd (RenderDoc 1.46),
#   KYTY_RD_FLIPS=2, FrameTrace (KYTY_FRAME_TRACE=lite of enter_scene.py); no video.  The capture is armed by the level line:
#   KYTY_RD_LEVEL=enemy_final KYTY_RD_LEVEL_FRAME=<N> - N guest frames after "Level has started: enemy_final"
#   (graphicsRun.cpp DebugAutoRenderDocCapture); N is the second argument and must equal the plan line of the attempt.
#   KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0; KYTY_GPU_CHECKPOINTS never passed.
# ATTEMPTS (item 327 (e)): <= 2; attempt 2 only after attempt 1 (its attempt file) and with its own plan file pred/02_f7a.md
#   (written before the call: the thumbnail shows no arena floor or rd_list.py gives <= 1 draw).
# AFTER THE RUN, INSIDE THE LOCK (before the cache returns, so the replay's driver cache writes are returned too): the new
#   _RenderDoc/*.rdc of this run (exactly one) is MOVED to C:/kyty/f287/f7a/enemy_final_<N>.rdc, sha256; renderdoccmd thumb ->
#   enemy_final_<N>.png; qrenderdoc --python C:/kyty/scripts/rd_list.py (RD_CAP = the moved capture) with a watchdog of RDMAX s,
#   then taskkill qrenderdoc.exe if it still lives; C:/kyty/rd_list.txt copied to rd_list_<N>.txt; rdsum_f7a.py.
# usage: bash C:/kyty/f287/f7a/go_f7a.sh <attempt 1|2> <N>
# EXIT CODES: 0 done (read f7a_read line and RDSUM line); 1 hard refusal / failure / restore failed; 2 usage; 4 BUSY - no run.
K=${1:-}
N=${2:-}
ROOT=C:/kyty/f287/f7a
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/f287/STOP
EMUD="/c/kyty/KytyPS5/ps5 em"
GAME="$EMUD/kyty_emulator.exe"
RDDIR="$EMUD/_RenderDoc"
BUILD_EXPECT="dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e"
BUILD_PINNED="/c/kyty/s146/kyty_emulator_dac02fb9.exe"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
RDHOME="/c/Program Files/RenderDoc"
RDLIST=C:/kyty/scripts/rd_list.py
CACHE="$EMUD/_ShaderCache/PPSA21564"
SNAP=$ROOT/cache_snap/PPSA21564
GLSNAP=$ROOT/glcache_snap
LV=enemy_final
HOLD=180
RDMAX=1800
IDLEMAX=300
IDLESTEP=15
PLWAIT=540
case "$K" in 1|2) ;; *) echo "usage: go_f7a.sh <attempt 1|2> <N>"; exit 2;; esac
case "$N" in ''|*[!0-9]*) echo "usage: go_f7a.sh <attempt 1|2> <N>"; exit 2;; esac
C=f7a_$K
PRED="pred/0${K}_f7a.md"
L=$ROOT/go_f7a.log
TIMES=/c/kyty/f287/times.txt
LOCKLOG=$ROOT/lock.log
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
tl() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F7a go_f7a $*" >> $TIMES; }
busy() { log "go_f7a.sh refused BUSY (rc 4): $* - no run made"; tl "$C refused BUSY (rc 4): $*"; echo "busy: $*"; exit 4; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
if [ -e $STOPF ]; then STOPTXT=""; read -r STOPTXT < $STOPF 2>/dev/null; busy "stop file $STOPF: $STOPTXT"; fi
lockheld() {
  if [ -e $LOCK ]; then LOCKTXT=""; read -r LOCKTXT < $LOCK 2>/dev/null; busy "lock held: $LOCKTXT"; fi
}
lockheld
WINPID=""
read -r WINPID < /proc/$$/winpid 2>/dev/null
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_B1B KYTY_FIX_DUALSRC KYTY_FIX_MINIMIZE KYTY_FIX_B9A KYTY_PRINT_NAMES KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW KYTY_PVAR KYTY_TEST_MINIMIZE KYTY_REC KYTY_RD_FRAME KYTY_RD_TIME
if [ -e "attempt_$C.txt" ] || [ -e "$C.json" ]; then log "refused: attempt_$C.txt or $C.json exists (one attempt)"; echo "attempt already made"; exit 1; fi
if [ "$K" = "2" ] && [ ! -e attempt_f7a_1.txt ]; then log "refused: attempt 2 before attempt 1"; echo "attempt 2 before attempt 1"; exit 1; fi
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in "go_f7a call: bash C:/kyty/f287/f7a/go_f7a.sh "*) NL=$((NL+1)); PL="$PLINE";; esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$PL" != "go_f7a call: bash C:/kyty/f287/f7a/go_f7a.sh $K $N" ]; then
  log "refused: the call '$K $N' is not the one call line of the plan $PRED (lines $NL)"; echo "call differs from the plan"; exit 1
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then log "refused: pinned copy bad"; echo "pinned build bad"; exit 1; fi
if [ "$(sha "$GAME")" != "$BUILD_EXPECT" ]; then log "refused: installed build is not $BUILD_EXPECT"; echo "installed build bad"; exit 1; fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then log "refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1; fi
for F in "$RDHOME/renderdoc.dll" "$RDHOME/qrenderdoc.exe" "$RDHOME/renderdoccmd.exe" "$RDLIST"; do
  [ -f "$F" ] || { log "refused: $F missing"; echo "renderdoc file missing"; exit 1; }
done
if [ -e "$ROOT/enemy_final_$N.rdc" ]; then log "refused: enemy_final_$N.rdc exists"; echo "capture name taken"; exit 1; fi
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
GLDIR="$LOCALAPPDATA/NVIDIA/GLCache"
mkdir -p runs
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*|mutlib' -or \$_.Name -eq 'kyty_emulator.exe' -or \$_.Name -eq 'qrenderdoc.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() { tl "$C BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)"; }
guards() {
  python $ROOT/procload.py --wait-s "$1" 2>&1 | mask >> $L
  [ "${PIPESTATUS[0]}" = "0" ] || { log "a process stays busy after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/emulator/qrenderdoc process lives ($NAMES)"; return 1; fi
  return 0
}
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
dirlist() {
  local D
  D=$(cd "$1" 2>/dev/null && for x in */; do [ -d "$x" ] && echo "${x%/}"; done | sort | tr '\n' ',')
  echo "dirs [${D}] sha $(printf '%s' "$D" | sha256sum | cut -c1-16)"
}
log "go_f7a.sh $K $N requested (installed $BUILD_EXPECT, level $LV, hold $HOLD)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
log "idle check cpu=$CPU (< 15)"
case "$CPU" in ''|*[!0-9]*) busy "machine not idle (cpu='$CPU')";; esac
if [ "$CPU" -ge 15 ]; then busy "machine not idle (cpu='$CPU')"; fi
lockheld
idlewait "$C pre-lock" || busy "machine not idle by idle142 within $IDLEMAX s"
lockheld
guards 0 || busy "procload / name guard not clean before the lock"
if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi
WIN=$(python $ROOT/win_f7a.py 2>&1 | tail -1 | tr -d '\r')
tl "$C lock window (p.327(e), p.322(g)): $WIN"
case "$WIN" in *"-> open") ;; *) busy "lock window closed or unknown: $WIN";; esac
lockheld
set -o noclobber
if ! { echo "go_f7a.sh $C pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  busy "lock taken by someone else: $(cat $LOCK 2>/dev/null)"
fi
set +o noclobber
echo "lock taken $C $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG
tl "$C lock taken (winpid $WINPID)"
tl "$C installed build sha256 $(sha "$GAME") (BUILD_EXPECT $BUILD_EXPECT; no install in F7a)"
RETFAIL=0
SNAPPED=0
GLSNAPPED=0
LIST_BEFORE=""
DIRS_BEFORE=""
finish() {
  RCX=$?
  if tasklist //FI "IMAGENAME eq qrenderdoc.exe" 2>/dev/null | grep -qi qrenderdoc; then
    taskkill //F //IM qrenderdoc.exe > /dev/null 2>&1; tl "$C qrenderdoc.exe killed at the exit (taskkill)"
  fi
  if [ "$(sha "$GAME")" != "$BUILD_EXPECT" ]; then
    if cp "$BUILD_PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$BUILD_EXPECT" ]; then tl "$C installed build changed - restored from the pinned copy";
    else tl "$C RESTORE BINARY FAILED sha256 $(sha "$GAME")"; RCX=1; RETFAIL=1; fi
  else
    tl "$C installed build at the end sha256 $BUILD_EXPECT (unchanged)"
  fi
  if [ "$SNAPPED" = "1" ]; then
    LIST_RUN=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_run_$C.txt 2>&1 | tail -1 | tr -d '\r')
    tl "$C shader cache at the end (before the return): $LIST_RUN; $(dirlist "$CACHE"); $(python $ROOT/cachesig_f6e.py "$CACHE" 2>&1 | tail -1 | tr -d '\r')"
    KEEP=$ROOT/cache_run/$(date -u +%Y%m%dT%H%M%SZ)
    mkdir -p "$KEEP"
    if mv "$CACHE" "$KEEP/" && cp -a "$SNAP" "$CACHE"; then
      LIST_BACK=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_back_$C.txt 2>&1 | tail -1 | tr -d '\r')
      DIRS_BACK=$(dirlist "$CACHE")
      if [ "$LIST_BACK" = "$LIST_BEFORE" ] && [ "$DIRS_BACK" = "$DIRS_BEFORE" ]; then
        tl "$C shader cache returned: $LIST_BACK = before; $DIRS_BACK = before; run cache kept in $KEEP"
      else
        tl "$C SHADER CACHE RESTORE FAILED: back '$LIST_BACK' / '$DIRS_BACK' != before '$LIST_BEFORE' / '$DIRS_BEFORE'"; RCX=1; RETFAIL=1
      fi
    else
      tl "$C SHADER CACHE RESTORE FAILED: move/copy error"; RCX=1; RETFAIL=1
    fi
  fi
  if [ "$GLSNAPPED" = "1" ]; then
    CMA=$(python $ROOT/cachemf146.py runs/cache_$C.after.json 2>&1 | tail -1 | tr -d '\r')
    tl "$C cache manifest after (before the GLCache return): $CMA"
    GLKEEP=$ROOT/glcache_run/$(date -u +%Y%m%dT%H%M%SZ)
    mkdir -p "$GLKEEP"
    if mv "$GLDIR" "$GLKEEP/" && cp -a "$GLSNAP/GLCache" "$GLDIR"; then
      GLB=$(python $ROOT/shalist_f2c.py "$GLDIR" 2>&1 | tail -1 | tr -d '\r')
      if [ "$GLB" = "$GL_BEFORE" ]; then tl "$C GLCache returned: $GLB = before"; else tl "$C GLCACHE RESTORE FAILED: '$GLB' != '$GL_BEFORE'"; RCX=1; RETFAIL=1; fi
    else
      tl "$C GLCACHE RESTORE FAILED: move/copy error"; RCX=1; RETFAIL=1
    fi
  fi
  if [ "$RETFAIL" = "1" ]; then
    echo "F7a binary or cache return failed $(date -u +%Y-%m-%dT%H:%M:%SZ) - track F stopped, comment in HPP-397" > $STOPF
    tl "$C stop file written: binary or cache return failed"
  fi
  FG=$(python $ROOT/fgcpu146.py --since runs/fgcpu_$C.a.json --chain-pid $WINPID 2>&1 | tail -1 | tr -d '\r')
  tl "$C foreign cpu at the end inside the lock: $FG"
  rm -f $LOCK
  echo "lock released $C $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG
  tl "$C lock released (rc $RCX)"
  exit $RCX
}
trap finish EXIT
LIST_BEFORE=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_before_$C.txt 2>&1 | tail -1 | tr -d '\r')
DIRS_BEFORE=$(dirlist "$CACHE")
tl "$C shader cache before: $LIST_BEFORE; $DIRS_BEFORE; $(python $ROOT/cachesig_f6e.py "$CACHE" 2>&1 | tail -1 | tr -d '\r')"
rm -rf "$ROOT/cache_snap"
mkdir -p "$ROOT/cache_snap"
cp -a "$CACHE" "$SNAP" || { tl "$C shader cache copy failed - stop"; exit 1; }
LIST_SNAP=$(python $ROOT/shalist_f2c.py "$SNAP" 2>&1 | tail -1 | tr -d '\r')
DIRS_SNAP=$(dirlist "$SNAP")
[ "$LIST_SNAP" = "$LIST_BEFORE" ] && [ "$DIRS_SNAP" = "$DIRS_BEFORE" ] || { tl "$C shader cache copy differs - stop"; exit 1; }
SNAPPED=1
tl "$C shader cache copy = before ($ROOT/cache_snap)"
CMB=$(python $ROOT/cachemf146.py runs/cache_$C.before.json 2>&1 | tail -1 | tr -d '\r')
tl "$C cache manifest before: $CMB"
GL_BEFORE=$(python $ROOT/shalist_f2c.py "$GLDIR" 2>&1 | tail -1 | tr -d '\r')
rm -rf "$GLSNAP"
mkdir -p "$GLSNAP"
cp -a "$GLDIR" "$GLSNAP/GLCache" || { tl "$C GLCache copy failed - stop"; exit 1; }
GL_SNAP=$(python $ROOT/shalist_f2c.py "$GLSNAP/GLCache" 2>&1 | tail -1 | tr -d '\r')
[ "$GL_SNAP" = "$GL_BEFORE" ] || { tl "$C GLCache copy differs - stop"; exit 1; }
GLSNAPPED=1
tl "$C GLCache before: $GL_BEFORE (copy equal)"
python $ROOT/fgcpu146.py --save runs/fgcpu_$C.a.json >> $L 2>&1
log "files: $(sha256sum f7a_read.py rdsum_f7a.py win_f7a.py cachesig_f6e.py shalist_f2c.py $PRED gates_default.txt enter_scene.py idle142.py procload.py go_f7a.sh fgcpu146.py cachemf146.py $RDLIST | cut -c1-16,65- | tr '\n' ';')"
RDB=$(ls "$RDDIR"/*.rdc 2>/dev/null | sort | tr '\n' ';')
EXTRA="KYTY_RD_LEVEL=$LV KYTY_RD_LEVEL_FRAME=$N KYTY_RD_FLIPS=2 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0"
runtag() {
  echo "go_f7a.sh $C pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) installed $BUILD_EXPECT N $N" > attempt_$C.txt
  tl "$C enter_scene start$1 (level $LV, --rd, hold $HOLD, extra '$EXTRA')"
  python $ROOT/enter_scene.py $C --level $LV --attempts 1 --stable-draws 100 --timeout 480 --no-install --require-idle \
    --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED --emu-arg=--rd --hold $HOLD $EXTRA > $C.stdout.txt 2>&1
}
refused() { [ "$1" = "3" ] && [ -e $C.refused.json ] && [ ! -e log_$C.txt ] && [ ! -e $C.json ]; }
if [ -e $STOPF ]; then tl "$C stop file before the run: $(head -1 $STOPF)"; exit 1; fi
idlewait $C || { tl "$C stop: BUSY before the run (not an attempt) - question to the lead"; exit 1; }
runtag ""
RC=$?
if refused $RC; then
  for F in attempt_$C.txt $C.refused.json $C.stdout.txt; do mv "$F" "${F/$C/$C.busyr1}"; done
  tl "$C enter_scene refused BUSY before the emulator start (not an attempt): $(grep -o 'REFUSED.*' $C.busyr1.stdout.txt | head -1 | cut -c1-160)"
  idlewait $C || { tl "$C stop: BUSY before the retry (not an attempt) - question to the lead"; exit 1; }
  runtag " (retry after a BUSY refusal)"
  RC=$?
  if refused $RC; then tl "$C second BUSY refusal (not an attempt) - stop, question to the lead"; exit 1; fi
fi
tl "$C enter_scene end rc $RC log_$C.txt sha256 $(sha log_$C.txt)"
python $ROOT/f7a_read.py log_$C.txt > read_$C.txt 2>&1
tl "$C reader: $(tail -1 read_$C.txt | cut -c1-900)"
RDA=$(ls "$RDDIR"/*.rdc 2>/dev/null | sort | tr '\n' ';')
NEW=""
NNEW=0
IFS=';' read -ra AFTER <<< "$RDA"
for X in "${AFTER[@]}"; do
  [ -n "$X" ] || continue
  case ";$RDB" in *";$X;"*) ;; *) NEW="$X"; NNEW=$((NNEW+1));; esac
done
tl "$C new captures in _RenderDoc: $NNEW ($(basename "$NEW" 2>/dev/null))"
if [ "$NNEW" != "1" ]; then tl "$C no single new capture - no thumbnail, no listing"; exit 0; fi
CAPF=$ROOT/enemy_final_$N.rdc
mv "$NEW" "$CAPF" || { tl "$C move of the capture failed"; exit 1; }
tl "$C capture moved to $CAPF bytes $(stat -c %s "$CAPF") sha256 $(sha "$CAPF")"
"$RDHOME/renderdoccmd.exe" thumb --out="C:/kyty/f287/f7a/enemy_final_$N.png" "C:/kyty/f287/f7a/enemy_final_$N.rdc" > runs/thumb_$C.txt 2>&1
tl "$C thumbnail rc $? enemy_final_$N.png sha256 $(sha enemy_final_$N.png)"
rm -f C:/kyty/rd_list.txt
tl "$C rd_list.py start (qrenderdoc --python, watchdog $RDMAX s)"
RD_CAP="C:/kyty/f287/f7a/enemy_final_$N.rdc" "$RDHOME/qrenderdoc.exe" --python $RDLIST > runs/qrd_$C.txt 2>&1 &
QP=$!
WS=0
while kill -0 $QP 2>/dev/null; do
  if grep -q '^done' C:/kyty/rd_list.txt 2>/dev/null; then sleep 20; break; fi
  if [ $WS -ge $RDMAX ]; then tl "$C rd_list.py watchdog $RDMAX s expired"; break; fi
  sleep 10; WS=$((WS+10))
done
if kill -0 $QP 2>/dev/null; then taskkill //F //IM qrenderdoc.exe > /dev/null 2>&1; tl "$C qrenderdoc.exe still alive after the listing - taskkill"; fi
wait $QP 2>/dev/null
cp C:/kyty/rd_list.txt rd_list_$N.txt 2>/dev/null
tl "$C rd_list end after ~$WS s: rd_list_$N.txt lines $(wc -l < rd_list_$N.txt 2>/dev/null) sha256 $(sha rd_list_$N.txt)"
python $ROOT/rdsum_f7a.py rd_list_$N.txt --out rdsum_$N.txt > runs/rdsum_$C.out.txt 2>&1
tl "$C rdsum rc $?: $(tail -1 runs/rdsum_$C.out.txt | cut -c1-300); rdsum_$N.txt sha256 $(sha rdsum_$N.txt)"
exit 0
