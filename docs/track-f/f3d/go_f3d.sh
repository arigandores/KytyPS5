#!/bin/bash
# Track F link F3d (HPP-342; ROADMAP s.0.1 "SESSION 122" item 259 (e)(4)-(6), item 277 (b) (RC1 of F3c), item 228 (v),
# item 254 (e), item 256 (v)): the runs of item 259 (e)(5) on the binary of the B1b + F9 fix (F3b, copy 2e6df8f0), as ONE series
# under ONE lock - the fix binary is installed once and the installed build 9235a7ac and the caches come back in the same
# command (EXIT trap), so no other run can meet the fix binary or the caches written by it.
# Port of C:/kyty/f287/f4c/go_f4c2.sh (itself a port of f2c/go_f2c.sh and s143/go143a.sh): lock first, guards, one attempt,
# seal call line, stop file, lock.log UTC, times lines, cache copy/return by content lists, GLCache copy/return, idle wait
# before every tag with one retry of a BUSY refusal of enter_scene.py.
# ASCII only (item 175 (v)).  No emulator code, no build.
#   TAGS AND ORDER (item 259 (e)(5); one attempt each, a failure is data, no repeat; a repeat only by a lead line):
#     f3d_a1  (a) big_hand_pirate_island -lvl, KYTY_FIX_B1B=1, first entry (cold: new translation signature) - hold HOLDA s
#             from "stable" (variant of the executor [I]: the cold entry is held as the census, so (4) sees the scene);
#             only (4) and deaths / K2 count
#     f3d_a2  (a) the same level again, =1, second entry: hold HOLDA s, video (KYTY_REC), s51_vidglitch.py 4 6, sheet142 sheet
#     f3d_a3  (a) voxel_world, =1, first entry (as f3d_a1)
#     f3d_a4  (a) voxel_world, =1, second entry (as f3d_a2)
#     f3d_bv  (b) Sky Garden V -lvl underwater_aerial_garden, =1, video, hold VHOLD s (the reader: sum dt_us after the first
#             scene frame >= 300 s), glitches, pair sheet "v142 / F3d" (sheetpair_f3d.py, the same frame positions)
#     f3d_bw  (b) Sky Garden W, =1, form of item 254 (e): --vulkan-validation true + KYTY_PIPELINE_PRECACHE=0 (VK_LAYER_PATH,
#             VK_LAYER_DUPLICATE_MESSAGE_LIMIT as F2c), no video, hold WHOLD s
#     f3d_c1  (v) control big_hand_pirate_island KYTY_FIX_B1B=0, hold HOLDA s, no video
#     f3d_c2  (v) control voxel_world KYTY_FIX_B1B=0, hold HOLDA s, no video
#   KNOB (item 277 (b)(1), (3)): exactly KYTY_FIX_B1B=1 or =0; KYTY_FIX_B26 never passed (default); the reader checks the line
#     "Shader translation cache:" (variant_fixb26_fixb1b / variant_fixb26) - otherwise the tag is INVALID and the series stops.
#   BINARY (item 277 (b)(4)): only the copy BIN_F3D, its sha256 checked before the lock, after the install and before EVERY
#     tag (the copy and the installed file); no rebuild.
#   SERIES STOP (f3d_read.py --stop-check, and enter_scene rc != 0): no reading, NOT ADMITTED, INVALID, WINDOW EVENT, a death
#     marker, a failed enter_scene - later tags not run, the question goes to the lead.  FAIL of a member is data: go on.
#   CACHES (item 228 (v), item 277 (b)(2)): inside the lock, before the install: _ShaderCache/PPSA21564 (root files, every
#     variant directory - variant_fixb26, variant_fixb26_fixb1b if present - and the recipes) copied to cache_snap/PPSA21564,
#     the two content lists equal (shalist_f2c.py); the list of the variant directories (and its sha) is a times line before
#     and after; EXIT trap: the run's cache MOVED to cache_run/<UTC>/, the snapshot copied back, its content list and its
#     directory list must equal the lists before (a directory absent before is absent after), else RESTORE FAILED rc 1;
#     GLCache (cachemf143.py manifest before / after, copy glcache_snap/) back from its copy (GLRESTORE=1, item 256 (v)).
#     A failed return writes the stop file C:/kyty/f287/STOP.
#   LOCK WINDOW (item 259 (e)(5), 277 (z)): right before the lock - no lock file, no stop file, HPP-333 and HPP-341 done
#     without a run, HPP-337 (F4c, first inside F), HPP-352 (session run step) and HPP-364 (P17) neither todo nor in_progress
#     and without a run, by the API answer (win_f3d.py, a times line with the answer); else BUSY rc 4.
#   STOP FILE (general rule 26): C:/kyty/f287/STOP -> rc 4 before anything, before the lock and before every tag.
#   THE SEAL'S CALL (item 105 (v)): the seal carries exactly one line "go_f3d call: PLWAIT=<n> bash
#     C:/kyty/f287/f3d/go_f3d.sh series"; f3d_read.py --check-seal checks every "seal:" line before the lock.
#   THE LOCK: checked before any process and before every guard stage; "lock taken|released series <UTC>" -> lock.log;
#     every event -> one UTC line of C:/kyty/f287/times.txt at the moment of the event.
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, --pred of the seal; KYTY_GPU_CHECKPOINTS never passed.
# EXIT CODES: 0 series done (read score_<tag>.txt, f3d_read.py --summary); 1 hard refusal / series stopped / restore failed;
#   2 usage / not configured; 4 BUSY (lock, stop file, guards, idle) - no run.
#   DRY=1 go_f3d.sh series prints the plan and exits 0 after the cheap refusals, before any guard, lock or install.
T=${1:-}
ROOT=C:/kyty/f287/f3d
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/f287/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"
BIN_F3D="C:/kyty/f287/bin/kyty_emulator_2e6df8f0.exe"
BIN_EXPECT="2e6df8f09f006ef8d49173bd4abccea074da94769c5c31b9caeeaadc3eaf74ae"
GLRESTORE="1"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
REFV=C:/kyty/s142/rec_v142.mp4
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
VKDUP="1000000"
PRED="pred/01_f3d.md"
CACHE="/c/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564"
SNAP=$ROOT/cache_snap/PPSA21564
GLSNAP=$ROOT/glcache_snap
BH=big_hand_pirate_island
VW=voxel_world
SKY=underwater_aerial_garden
HOLDA="120"
VHOLD="330"
WHOLD="310"
SEQ="f3d_a1 f3d_a2 f3d_a3 f3d_a4 f3d_bv f3d_bw f3d_c1 f3d_c2"
RSLEEP=5
PLMAX=540
IDLEMAX=300
IDLESTEP=15
PLWAIT=${PLWAIT:-$PLMAX}
if [ "$T" != "series" ]; then echo "usage: go_f3d.sh series  (see the header)"; exit 2; fi
L=$ROOT/go_f3d.log
TIMES=/c/kyty/f287/times.txt
LOCKLOG=$ROOT/lock.log
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
tl() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F3d go_f3d $*" >> $TIMES; }
busy() { log "go_f3d.sh refused BUSY (rc 4): $* - no run made"; echo "busy: $*"; exit 4; }
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
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_B1B KYTY_FIX_DUALSRC KYTY_FIX_MINIMIZE KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW KYTY_BVH_NATIVE KYTY_BVH_STUB
if [ -z "$BIN_F3D" ] || [ -z "$BIN_EXPECT" ] || [ -z "$GLRESTORE" ]; then
  log "go_f3d.sh refused: not configured (BIN_F3D/BIN_EXPECT - item 277 (b)(4); GLRESTORE - item 256 (v))"
  echo "not configured"; exit 2
fi
case "$PLWAIT" in
  ''|*[!0-9]*) log "go_f3d.sh refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then log "go_f3d.sh refused: PLWAIT $PLWAIT > $PLMAX"; echo "PLWAIT above $PLMAX"; exit 2; fi
for C in $SEQ; do
  if [ -e "attempt_$C.txt" ] || [ -e "$C.json" ]; then
    log "go_f3d.sh refused: attempt_$C.txt or $C.json exists - the one attempt of the series was made (no repeat)"
    echo "attempt already made"; exit 1
  fi
done
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go_f3d call: PLWAIT="*" bash C:/kyty/f287/f3d/go_f3d.sh series")
        V=${PLINE#go_f3d call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go_f3d.sh refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL')"
  echo "PLWAIT differs from the seal"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY series: tags $SEQ; stop file?; lock?; PLWAIT=$PLWAIT; binary copy sha ($BIN_EXPECT); procload --wait-s $PLWAIT; f3d_read --check-seal; cpu < 15; idle142 wait up to $IDLEMAX s; procload --wait-s 0; stop file?; window HPP-333/HPP-341 done, HPP-337/HPP-352/HPP-364 not waiting (win_f3d); lock (lock.log UTC); shader cache content list + variant directory list + copy to $SNAP (lists equal); GLCache manifest + copy (GLRESTORE=$GLRESTORE); fgcpu143 --save; install $BIN_F3D; per tag: stop file?, binary copy and installed sha = $BIN_EXPECT, idle142 wait (one retry of a BUSY refusal), enter_scene.py <tag> --level <L> --attempts 1 --no-install --require-idle --pred $ROOT/$PRED (a1,a3 cold: $BH/$VW --stable-draws 100 --hold $HOLDA KYTY_FIX_B1B=1; a2,a4: the same + --rec; bv: $SKY --stable-draws 300 --rec --hold $VHOLD KYTY_FIX_B1B=1; bw: $SKY --emu-arg=--vulkan-validation true --hold $WHOLD KYTY_FIX_B1B=1 KYTY_PIPELINE_PRECACHE=0 VK_LAYER_PATH; c1,c2: $BH/$VW --hold $HOLDA KYTY_FIX_B1B=0) KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, log sha, s51_vidglitch 4 6 + sheet142 (a2, a4) / sheetpair_f3d vs $REFV (bv), f3d_read --tag, f3d_read --stop-check; EXIT: restore $BUILD_PINNED ($BUILD_EXPECT), move run cache to cache_run/, copy snapshot back (content list and directory list = before), GLCache manifest after + restore (GLRESTORE=$GLRESTORE), fgcpu143 row, unlock; f3d_read --summary"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then
  log "go_f3d.sh refused: pinned copy $BUILD_PINNED missing or its sha != $BUILD_EXPECT"; echo "pinned build bad"; exit 1
fi
if [ ! -f "$BIN_F3D" ] || [ "$(sha "$BIN_F3D")" != "$BIN_EXPECT" ]; then
  log "go_f3d.sh refused: fix binary $BIN_F3D missing or its sha != $BIN_EXPECT"; echo "fix binary bad"; exit 1
fi
if [ "$(sha "$GAME")" != "$BUILD_EXPECT" ]; then
  log "go_f3d.sh refused: the installed $GAME is not $BUILD_EXPECT before the series - not starting"; echo "installed build bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go_f3d.sh refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1
fi
if [ ! -f "$REFV" ]; then
  log "go_f3d.sh refused: the reference video $REFV is missing (pair sheet of item 259 (e)(5)(b))"; echo "reference video missing"; exit 1
fi
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
GLDIR="$LOCALAPPDATA/NVIDIA/GLCache"
mkdir -p runs
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*|test_[a-z0-9_]*f3d|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F3d go_f3d BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)" >> $TIMES
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
  # the variant directories of the translation cache (one level under PPSA21564), sorted, and the sha of that list
  local D
  D=$(cd "$1" 2>/dev/null && for x in */; do [ -d "$x" ] && echo "${x%/}"; done | sort | tr '\n' ',')
  echo "dirs [${D}] sha $(printf '%s' "$D" | sha256sum | cut -c1-16)"
}
log "go_f3d.sh series requested (fix binary $BIN_EXPECT, installed $BUILD_EXPECT, PLWAIT=$PLWAIT, seq $SEQ)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $ROOT/f3d_read.py --check-seal $ROOT/$PRED >> $L 2>&1; then
  log "f3d_read.py --check-seal refused (see above) - not starting"; echo "seal check failed"; exit 1
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
WIN=$(python $ROOT/win_f3d.py 2>&1 | tail -1 | tr -d '\r')
tl "lock window (p.259(e)(5), 277(z)): $WIN"
case "$WIN" in
  *"-> open") ;;
  *) busy "lock window closed or unknown: $WIN";;
esac
lockheld
set -o noclobber
if ! { echo "go_f3d.sh series pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
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
DIRS_BEFORE=""
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
    tl "shader cache at the end of the series (before the return): $LIST_RUN; $(dirlist "$CACHE")"
    KEEP=$ROOT/cache_run/$(date -u +%Y%m%dT%H%M%SZ)
    mkdir -p "$KEEP"
    if mv "$CACHE" "$KEEP/" && cp -a "$SNAP" "$CACHE"; then
      LIST_BACK=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_back.txt 2>&1 | tail -1 | tr -d '\r')
      DIRS_BACK=$(dirlist "$CACHE")
      if [ "$LIST_BACK" = "$LIST_BEFORE" ] && [ "$DIRS_BACK" = "$DIRS_BEFORE" ]; then
        tl "shader cache returned: $LIST_BACK = before; $DIRS_BACK = before (p.277(b)(2)); run cache kept in $KEEP"
      else
        tl "SHADER CACHE RESTORE FAILED: back '$LIST_BACK' / '$DIRS_BACK' != before '$LIST_BEFORE' / '$DIRS_BEFORE'"; echo "cache restore failed"; RCX=1; RETFAIL=1
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
    echo "F3d binary or cache return failed $(date -u +%Y-%m-%dT%H:%M:%SZ) - track F stopped, comment in HPP-342" > $STOPF
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
# caches before the install (item 228 (v), item 277 (b)(2))
LIST_BEFORE=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_before.txt 2>&1 | tail -1 | tr -d '\r')
DIRS_BEFORE=$(dirlist "$CACHE")
tl "shader cache before the series: $LIST_BEFORE; $DIRS_BEFORE"
rm -rf "$ROOT/cache_snap"
mkdir -p "$ROOT/cache_snap"
cp -a "$CACHE" "$SNAP" || { tl "shader cache copy failed - stop"; exit 1; }
LIST_SNAP=$(python $ROOT/shalist_f2c.py "$SNAP" 2>&1 | tail -1 | tr -d '\r')
DIRS_SNAP=$(dirlist "$SNAP")
[ "$LIST_SNAP" = "$LIST_BEFORE" ] && [ "$DIRS_SNAP" = "$DIRS_BEFORE" ] || { tl "shader cache copy differs: '$LIST_SNAP' / '$DIRS_SNAP' != '$LIST_BEFORE' / '$DIRS_BEFORE' - stop"; exit 1; }
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
cp "$BIN_F3D" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "installed sha != $BIN_EXPECT - stop"; tl "install failed"; exit 1; }
tl "installed fix binary sha256 $BIN_EXPECT"
log "files: $(sha256sum f3d_read.py win_f3d.py sheetpair_f3d.py shalist_f2c.py $PRED gates_default.txt enter_scene.py idle142.py procload.py go_f3d.sh sheet142.py fgcpu143.py cachemf143.py C:/kyty/s142/sc142.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
runtag() {
  echo "go_f3d.sh $C pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) fix binary $BIN_EXPECT" > attempt_$C.txt
  tl "$C enter_scene start$1 (level $LV, hold $HOLD, sd '$SD', extra '$EXTRA', emu '$EMUX', rec '$REC')"
  python $ROOT/enter_scene.py $C --level $LV --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt \
    --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $C.stdout.txt 2>&1
}
refused() { [ "$1" = "3" ] && [ -e $C.refused.json ] && [ ! -e log_$C.txt ] && [ ! -e $C.json ]; }
SERIES_RC=0
for C in $SEQ; do
  if [ -e $STOPF ]; then tl "stop file before $C: $(head -1 $STOPF) - series stopped"; SERIES_RC=1; break; fi
  if [ "$(sha "$BIN_F3D")" != "$BIN_EXPECT" ] || [ "$(sha "$GAME")" != "$BIN_EXPECT" ]; then
    tl "$C binary check failed (p.277(b)(4)): copy $(sha "$BIN_F3D" | cut -c1-16) installed $(sha "$GAME" | cut -c1-16) - series stop"
    SERIES_RC=1; break
  fi
  tl "$C binary check ok (p.277(b)(4)): copy and installed sha256 $BIN_EXPECT"
  REC=""; EMUX=""
  SD="--stable-draws 100 --timeout 480"; HOLD=$HOLDA
  case "$C" in
    f3d_a1) LV=$BH; EXTRA="KYTY_FIX_B1B=1";;
    f3d_a2) LV=$BH; EXTRA="KYTY_FIX_B1B=1"; REC="--rec";;
    f3d_a3) LV=$VW; EXTRA="KYTY_FIX_B1B=1";;
    f3d_a4) LV=$VW; EXTRA="KYTY_FIX_B1B=1"; REC="--rec";;
    f3d_bv) LV=$SKY; SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec"; EXTRA="KYTY_FIX_B1B=1";;
    f3d_bw) LV=$SKY; SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD
            EMUX="--emu-arg=--vulkan-validation --emu-arg=true"
            EXTRA="KYTY_FIX_B1B=1 KYTY_PIPELINE_PRECACHE=0 VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP";;
    f3d_c1) LV=$BH; EXTRA="KYTY_FIX_B1B=0";;
    f3d_c2) LV=$VW; EXTRA="KYTY_FIX_B1B=0";;
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
      tl "$C s51_vidglitch rc $? glitch_$C.txt sha256 $(sha glitch_$C.txt) rec_$C.mp4 sha256 $(sha rec_$C.mp4)"
      if [ "$C" = "f3d_bv" ]; then
        python $ROOT/sheetpair_f3d.py $REFV rec_$C.mp4 sheetpair_$C.png > sheetpair_$C.txt 2>&1
        tl "$C pair sheet v142 / F3d rc $? sheetpair_$C.png sha256 $(sha sheetpair_$C.png): $(head -1 sheetpair_$C.txt | cut -c1-200)"
      else
        python $ROOT/sheet142.py rec_$C.mp4 sheet_$C.png > sheet_$C.txt 2>&1
        tl "$C sheet rc $? sheet_$C.png sha256 $(sha sheet_$C.png)"
      fi
    else
      tl "$C no video rec_$C.mp4"
    fi
  fi
  python $ROOT/f3d_read.py --tag $C --json runs/$C.read.json > score_$C.txt 2>&1
  tl "$C reader rc $? score_$C.txt sha256 $(sha score_$C.txt): $(grep '^F3D VERDICT' score_$C.txt | tr '\n' ';' | cut -c1-300)"
  SC=$(python $ROOT/f3d_read.py --stop-check runs/$C.read.json 2>&1 | tail -1 | tr -d '\r')
  tl "$C stop check (enter_scene rc $RC): $SC"
  case "$SC" in
    "continue"*) ;;
    *) tl "$C series stop: $SC - later tags not run, question to the lead"; SERIES_RC=1; break;;
  esac
  if [ "$RC" != "0" ]; then tl "$C series stop: enter_scene rc $RC - later tags not run, question to the lead"; SERIES_RC=1; break; fi
done
python $ROOT/f3d_read.py --summary > summary_f3d.txt 2>&1
tl "summary rc $? summary_f3d.txt sha256 $(sha summary_f3d.txt): $(grep '^F3D SERIES VERDICT' summary_f3d.txt | cut -c1-300)"
exit $SERIES_RC
