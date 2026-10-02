#!/bin/bash
# Session 146 step 0 (HPP-386; ROADMAP s.0.1 "SESSION 122" item 300 (b)(1)-(3), item 309 (l)(1); brief docs/next-session-146.md):
# the INSTALL of the track F shipment binary dac02fb9 and its warm-up tag i146_v, as ONE call under ONE lock.
# Port of C:/kyty/f287/fsc/go_fs.sh (lock first, guards, idle wait with one retry of a BUSY refusal, one attempt, seal call line,
# stop file, lock.log UTC, times lines) and of C:/kyty/s145/go145a.sh (cache manifests, foreign-CPU row) - with the install of
# item 300 (b)(1) instead of the copy/return of FSc: the binary is NOT returned at the end when the warm-up passes.
# ASCII only (item 175 (v)).  No emulator code, no build.
#   (1) INSTALL: copy BIN (C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe, sha256 BIN_EXPECT) -> the emulator's kyty_emulator.exe;
#       the sha256 of kyty_emulator.exe before (must be OLD_EXPECT = 9235a7ac) and after (must be BIN_EXPECT) - step0/times.txt
#       rows; the pinned copy PINNED (C:/kyty/s146/kyty_emulator_dac02fb9.exe) written and its sha256 checked - a times row.
#   (2) CACHES ARE NOT TOUCHED: no copy, no return, no deletion.  Read only: the file count of _ShaderCache/PPSA21564, the
#       manifest of the three caches (cachemf146.py: shader, _PipelineCache, GLCache), the content list of GLCache
#       (shalist_f2c.py) and the list of the variant directories of PPSA21564 - before the lock and after the run, times rows.
#       The root PPSA21564 (9235a7ac) stays for a rollback; the variant directory is made by the first run (item 300 (b)(2)).
#   (3) WARM-UP i146_v: V Sky Garden -lvl underwater_aerial_garden on the installed binary at its shipped defaults (no KYTY_FIX_*,
#       no KYTY_PIPELINE_PRECACHE, no validation), video KYTY_REC, wall hold VHOLD=330 s, --stable-draws 300 --timeout 480,
#       --attempts 1; then s51_vidglitch.py 4 6, the pair sheet against fs_b (sheetpair_f3d.py, rec_fs_b.mp4 of FSc on top),
#       the whole-video sheet sheet142.py, and i146_read.py (the letter of item 221 (g)(3), V half).
#   WARM-UP FAIL (verdict not PASS, or enter_scene rc != 0, or no reading): ROLLBACK inside the lock - the pinned
#       C:/kyty/s128/kyty_emulator_9235a7ac.exe copied back, its sha256 checked (times row), rc 6: question to the lead.
#       Any exit after the install and before the PASS reading (an error, a BUSY refusal twice) also rolls back (EXIT trap).
#   ONE ATTEMPT: attempt_i146_v.txt is written inside the lock right before enter_scene.py; while it or i146_v.json exists the
#       call refuses rc 1.  A BUSY refusal of enter_scene.py before the emulator start (rc 3, no log, no json) is not an
#       attempt: one retry after the idle wait; a second refusal - rollback, rc 4.
#   STOP FILE (general rule 26): C:/kyty/s146/STOP -> rc 4 before anything, before the lock and before the install.
#   THE SEAL'S CALL (item 105 (v)): pred/00_i146.md carries exactly one line "go146i call: PLWAIT=<n> bash
#       C:/kyty/s146/go146i.sh install"; i146_read.py --check-seal checks every "seal:" line before the lock.
#   THE LOCK: checked before any process and before every guard stage; "lock taken|released i146_v <UTC>" -> runs146/lock.log;
#       every event -> one UTC line of step0/times.txt at the moment of the event, written by the command that makes it.
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, --pred of the seal; KYTY_GPU_CHECKPOINTS never passed.
# EXIT CODES: 0 installed and warm-up PASS (read score_i146_v.txt); 1 hard refusal / failed step (rolled back when installed);
#   2 usage / not configured; 4 BUSY (lock, stop file, guards, idle) - no run; 6 warm-up FAIL - rolled back, question to the lead.
#   DRY=1 go146i.sh install prints the plan and exits 0 after the cheap refusals, before any guard, lock or install.
T=${1:-}
ROOT=C:/kyty/s146
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s146/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BIN="C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe"
BIN_EXPECT="dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e"
PINNED="C:/kyty/s146/kyty_emulator_dac02fb9.exe"
OLD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"
OLD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
REF=C:/kyty/f287/fsc/rec_fs_b.mp4
PRED="pred/00_i146.md"
CACHE="/c/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564"
C=i146_v
SKY=underwater_aerial_garden
VHOLD="330"
RSLEEP=5
PLMAX=540
IDLEMAX=300
IDLESTEP=15
PLWAIT=${PLWAIT:-$PLMAX}
if [ "$T" != "install" ]; then echo "usage: go146i.sh install  (see the header)"; exit 2; fi
L=$ROOT/go146i.log
TIMES=$ROOT/step0/times.txt
OUT=$ROOT/runs146
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
tl() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go146i $*" >> $TIMES; }
busy() { log "go146i.sh refused BUSY (rc 4): $* - no run made"; echo "busy: $*"; exit 4; }
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
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_B1B KYTY_FIX_DUALSRC KYTY_FIX_MINIMIZE KYTY_TEST_MINIMIZE KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW KYTY_PVAR KYTY_BVH_NATIVE KYTY_BVH_STUB KYTY_BVH_LOOP_CAP KYTY_SHADER_CACHE VK_LAYER_MESSAGE_ID_FILTER VK_LAYER_DUPLICATE_MESSAGE_LIMIT KYTY_REC
case "$PLWAIT" in
  ''|*[!0-9]*) log "go146i.sh refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then log "go146i.sh refused: PLWAIT $PLWAIT > $PLMAX"; echo "PLWAIT above $PLMAX"; exit 2; fi
if [ -e "attempt_$C.txt" ] || [ -e "$C.json" ]; then
  log "go146i.sh refused: attempt_$C.txt or $C.json exists - the one attempt was made (no repeat)"
  echo "attempt already made"; exit 1
fi
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go146i call: PLWAIT="*" bash C:/kyty/s146/go146i.sh install")
        V=${PLINE#go146i call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go146i.sh refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL')"
  echo "PLWAIT differs from the seal"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY install: stop file?; lock?; PLWAIT=$PLWAIT; BIN sha ($BIN_EXPECT); installed = $OLD_EXPECT; rollback copy $OLD_PINNED; procload --wait-s $PLWAIT; i146_read --check-seal; cpu < 15; idle142 wait up to $IDLEMAX s; procload --wait-s 0; stop file?; shader cache count + cachemf146 + GLCache list + variant dirs (before); lock (runs146/lock.log UTC); fgcpu146 --save; sha before; install $BIN; sha after; pinned copy $PINNED; enter_scene.py $C --level $SKY --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED --rec --hold $VHOLD KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (one retry of a BUSY refusal); log sha; caches after (count, cachemf146, GLCache list, variant dirs); s51_vidglitch 4 6; sheetpair_f3d vs $REF; sheet142; i146_read --tag $C; not PASS -> rollback $OLD_PINNED (sha check), rc 6; EXIT: rollback unless PASS, fgcpu146 row, unlock"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BIN" ] || [ "$(sha "$BIN")" != "$BIN_EXPECT" ]; then
  log "go146i.sh refused: shipment binary $BIN missing or its sha != $BIN_EXPECT"; echo "shipment binary bad"; exit 1
fi
if [ ! -f "$OLD_PINNED" ] || [ "$(sha "$OLD_PINNED")" != "$OLD_EXPECT" ]; then
  log "go146i.sh refused: rollback copy $OLD_PINNED missing or its sha != $OLD_EXPECT"; echo "rollback copy bad"; exit 1
fi
if [ "$(sha "$GAME")" != "$OLD_EXPECT" ]; then
  log "go146i.sh refused: the installed $GAME is not $OLD_EXPECT before the install - not starting"; echo "installed build bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go146i.sh refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1
fi
if [ ! -f "$REF" ]; then log "go146i.sh refused: reference video $REF missing"; echo "reference video missing"; exit 1; fi
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
GLDIR="$LOCALAPPDATA/NVIDIA/GLCache"
mkdir -p $OUT step0
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*|test_[a-z0-9_]*146|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  # item 231 (z)(5): the BUSY row names the process of the last "procload: busy" line of go146i.log ("Process" 5 of s145: the
  # row is written as it stands in the log - the reader of times.txt replaces a foreign name by <app> before FACTS / comments).
  tl "BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)"
}
guards() {
  python $ROOT/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator process lives ($NAMES)"; return 1; fi
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
cachen() { local n=0 f; for f in "$CACHE"/*; do [ -e "$f" ] && n=$((n+1)); done; echo $n; }
log "go146i.sh install requested (shipment binary $BIN_EXPECT, installed $OLD_EXPECT, PLWAIT=$PLWAIT)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $ROOT/i146_read.py --check-seal $ROOT/$PRED >> $L 2>&1; then
  log "i146_read.py --check-seal refused (see above) - not starting"; echo "seal check failed"; exit 1
fi
lockheld
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
log "idle check cpu=$CPU (< 15)"
case "$CPU" in
  ''|*[!0-9]*) busy "machine not idle (cpu='$CPU')";;
esac
if [ "$CPU" -ge 15 ]; then busy "machine not idle (cpu='$CPU')"; fi
lockheld
idlewait "pre-lock" || busy "machine not idle by idle142 within $IDLEMAX s"
lockheld
guards 0 || busy "procload / name guard not clean before the lock"
if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi
tl "$C shader cache files before the lock $(cachen) ($CACHE); $(dirlist "$CACHE")"
CMB=$(python $ROOT/cachemf146.py $OUT/cache_$C.before.json 2>&1 | tail -1 | tr -d '\r')
tl "$C cache manifest before the lock: $CMB"
GLB=$(python $ROOT/shalist_f2c.py "$GLDIR" --out $OUT/glcache_$C.before.txt 2>&1 | tail -1 | tr -d '\r')
tl "$C GLCache content list before the lock: $GLB"
lockheld
set -o noclobber
if ! { echo "go146i.sh install pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  busy "lock taken by someone else: $(cat $LOCK 2>/dev/null)"
fi
set +o noclobber
echo "lock taken $C $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
tl "lock taken (winpid $WINPID)"
INSTALLED=0
KEEP=0
rollback() {
  for i in 1 2 3; do
    if cp "$OLD_PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$OLD_EXPECT" ]; then return 0; fi
    sleep $RSLEEP
  done
  return 1
}
finish() {
  RCX=$?
  if [ "$INSTALLED" = "1" ] && [ "$KEEP" != "1" ]; then
    if rollback; then
      tl "ROLLBACK done: kyty_emulator.exe sha256 $(sha "$GAME") = $OLD_EXPECT (copy $OLD_PINNED)"
    else
      tl "ROLLBACK FAILED: kyty_emulator.exe sha256 $(sha "$GAME") != $OLD_EXPECT - restore by hand before any run"
      echo "go146i rollback failed $(date -u +%Y-%m-%dT%H:%M:%SZ) - restore 9235a7ac by hand, comment in HPP-386" > $STOPF
      RCX=1
    fi
  fi
  FG=$(python $ROOT/fgcpu146.py --since $OUT/fgcpu_$C.a.json --chain-pid $WINPID 2>&1 | tail -1 | tr -d '\r')
  tl "$C foreign cpu at the end inside the lock: $FG"
  rm -f $LOCK
  echo "lock released $C $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUT/lock.log
  tl "lock released (rc $RCX)"
  exit $RCX
}
trap finish EXIT
python $ROOT/fgcpu146.py --save $OUT/fgcpu_$C.a.json >> $L 2>&1
tl "install: kyty_emulator.exe sha256 before $(sha "$GAME")"
INSTALLED=1
cp "$BIN" "$GAME" || { tl "install copy failed - stop"; exit 1; }
SA=$(sha "$GAME")
tl "install: kyty_emulator.exe sha256 after $SA (want $BIN_EXPECT)"
[ "$SA" = "$BIN_EXPECT" ] || { tl "install: sha after != $BIN_EXPECT - stop"; exit 1; }
cp "$BIN" "$PINNED" || { tl "pinned copy failed - stop"; exit 1; }
SP=$(sha "$PINNED")
tl "install: pinned copy $PINNED sha256 $SP"
[ "$SP" = "$BIN_EXPECT" ] || { tl "install: pinned copy sha != $BIN_EXPECT - stop"; exit 1; }
log "files: $(sha256sum i146_read.py C:/kyty/f287/fsc/fs_read.py C:/kyty/s142/sc142.py sheetpair_f3d.py shalist_f2c.py $PRED gates_default.txt enter_scene.py idle142.py procload.py go146i.sh sheet142.py fgcpu146.py cachemf146.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
runtag() {
  echo "go146i.sh $C pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) installed $BIN_EXPECT" > attempt_$C.txt
  tl "$C enter_scene start$1 (level $SKY, hold $VHOLD, video)"
  python $ROOT/enter_scene.py $C --level $SKY --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
    --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED --rec --hold $VHOLD KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 \
    > $C.stdout.txt 2>&1
}
refused() { [ "$1" = "3" ] && [ -e $C.refused.json ] && [ ! -e log_$C.txt ] && [ ! -e $C.json ]; }
idlewait $C || { tl "$C BUSY before the tag (not an attempt) - rollback, question to the lead"; exit 4; }
runtag ""
RC=$?
if refused $RC; then
  for F in attempt_$C.txt $C.refused.json $C.stdout.txt; do mv "$F" "${F/$C/$C.busyr1}"; done
  tl "$C enter_scene refused BUSY before the emulator start (not an attempt): $(grep -o 'REFUSED.*' $C.busyr1.stdout.txt | head -1 | cut -c1-160)"
  idlewait $C || { tl "$C BUSY before the retry (not an attempt) - rollback, question to the lead"; exit 4; }
  runtag " (retry after a BUSY refusal)"
  RC=$?
  if refused $RC; then tl "$C second BUSY refusal before the emulator start (not an attempt) - rollback, question to the lead"; exit 4; fi
fi
tl "$C enter_scene end rc $RC log_$C.txt sha256 $(sha log_$C.txt)"
tl "$C shader cache files after the run $(cachen) ($CACHE); $(dirlist "$CACHE")"
CMA=$(python $ROOT/cachemf146.py $OUT/cache_$C.after.json 2>&1 | tail -1 | tr -d '\r')
tl "$C cache manifest after the run: $CMA"
GLA=$(python $ROOT/shalist_f2c.py "$GLDIR" --out $OUT/glcache_$C.after.txt 2>&1 | tail -1 | tr -d '\r')
tl "$C GLCache content list after the run: $GLA"
if [ -f "rec_$C.mp4" ]; then
  python $VIDGLITCH rec_$C.mp4 4 6 $ROOT/vidframes_$C > glitch_$C.txt 2>&1
  tl "$C s51_vidglitch rc $? glitch_$C.txt sha256 $(sha glitch_$C.txt) rec_$C.mp4 sha256 $(sha rec_$C.mp4)"
  python $ROOT/sheetpair_f3d.py $REF rec_$C.mp4 sheetpair_$C.png > sheetpair_$C.txt 2>&1
  tl "$C pair sheet fs_b / i146_v rc $? sheetpair_$C.png sha256 $(sha sheetpair_$C.png): $(head -1 sheetpair_$C.txt | cut -c1-200)"
  python $ROOT/sheet142.py rec_$C.mp4 sheet_$C.png > sheet_$C.txt 2>&1
  tl "$C sheet rc $? sheet_$C.png sha256 $(sha sheet_$C.png)"
else
  tl "$C no video rec_$C.mp4"
fi
python $ROOT/i146_read.py --tag $C --json $OUT/$C.read.json > score_$C.txt 2>&1
RRC=$?
VER=$(grep '^WARMUP VERDICT' score_$C.txt | tr -d '\r')
tl "$C reader rc $RRC score_$C.txt sha256 $(sha score_$C.txt): $VER"
if [ "$RC" = "0" ] && [ "$RRC" = "0" ] && [ "$VER" = "WARMUP VERDICT $C: PASS" ]; then
  KEEP=1
  tl "$C warm-up PASS - the install stays: kyty_emulator.exe sha256 $(sha "$GAME")"
  exit 0
fi
tl "$C WARM-UP FAIL (enter_scene rc $RC, reader rc $RRC, '$VER') - rollback to $OLD_EXPECT, question to the lead (item 300 (b), 309 (l)(1))"
exit 6
