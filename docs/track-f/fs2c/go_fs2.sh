#!/bin/bash
# Track F link FS2c (HPP-383; ROADMAP "SESSION 122" item 298 (g)(1)-(4), (e); item 327 (g)(1)-(3); item 329 (a); item 295 (b);
# item 296 (b), (d); item 273 (e)(3), (z); item 228 (v); item 322 (g)): the regression of the second track F shipment binary FS2
# (FS2a, copy bbad499c) at the defaults, as ONE series under ONE lock - the FS2 copy is installed once and the installed build
# (dac02fb9, installed at step 0 of session 146) and the caches come back in the same command (EXIT trap), so no other run can meet
# the FS2 binary or the caches written by it.
# Port of C:/kyty/f287/f6e/go_f6e.sh (series, warm-up, K3 repeat, cache copy/return) and C:/kyty/f287/f7a/go_f7a.sh (procload output
# through the <app> mask, item 324 (i)), with the stand tags of C:/kyty/f287/f5c/go_f5c.sh and the _PipelineCache return of
# C:/kyty/f287/fsc/go_fs.sh [I].  ASCII only (item 175 (v)).  No emulator code, no build.
#   TAGS AND ORDER (item 298 (g), item 327 (g)(2); one attempt each, a failure is data; the only repeat is fs2_tr):
#     fs2_w   W Sky Garden -lvl underwater_aerial_garden at the defaults (no KYTY_FIX_*), precache by default, form W of item
#             295 (b): --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, NO
#             VK_LAYER_MESSAGE_ID_FILTER; stand KYTY_TEST_MINIMIZE=60:10; wall hold WHOLD s; no video
#     fs2_w0  the same with KYTY_FIX_MINIMIZE=0 (the stop with VUID 01689 is expected - the emulator ends)
#     fs2_v   V Sky Garden at the defaults with the stand, no validation, video (KYTY_REC), wall hold VHOLD s; s51_vidglitch 4 6,
#             sheet142 -> sheet_fs2_v.png for the lead
#     fs2_tw  warm-up timestop_casino at the defaults, hold HOLDW s, no video, NOT READ: stop on rc != 0, a death or a window line
#     fs2_t   timestop_casino at the defaults, form V of F6e: video, hold HOLDT s from "stable" (the reader: sum dt >= 120 s)
#     fs2_tr  only when the reader says "repeat-k3: fs2_tr" after fs2_t (K3 hold over the limit 1, item 327 (g)(2))
#   BINARY (item 298 (g), item 286 (b), item 329 (a)): only the copy BIN, its sha256 checked before the lock, after the install and
#     before EVERY tag (the copy and the installed file); it must hold the strings FixMinimize: on, FixB9a: on, TestMinimize: armed,
#     SwapchainZeroExtent: begin, AudioPropagation: calls and the translation signature 56189185...; no rebuild.
#   SERIES STOP (fs2_read.py --stop-check, enter_scene rc): no reading, NOT ADMITTED, NOT EVALUABLE (stand / arm controls, a window
#     event outside the stand - item 273 (z)), INVALID (FixB9a: on count), WINDOW EVENT, a death marker without [Vulkan][E], an
#     enter_scene rc != 0 outside fs2_w0 and outside a validation stop - later tags not run, the question goes to the lead.  FAIL of a
#     member, NO STOP of fs2_w0 - data: go on.
#   CACHES (item 228 (v), item 298 (g)): inside the lock, before the install: _ShaderCache/PPSA21564 (root files, every variant
#     directory, the recipes pipelines.bin) copied to cache_snap/PPSA21564, the content lists equal (shalist_f2c.py); the variant
#     directory list and the signature manifest (cachesig_f6e.py) are times lines before and after; GLCache (cachemf146.py manifest
#     before / after, copy glcache_snap/); _PipelineCache (member of the executor [I], as FSc) - content list, copy pcache_snap/.
#     EXIT trap: each run cache MOVED to *_run/<UTC>/, the snapshot copied back, its lists must equal the lists before, else RESTORE
#     FAILED rc 1 and the stop file C:/kyty/f287/STOP.
#   LOCK WINDOW (win_fs2.py, a times line with the answer): HPP-382, HPP-381 done; HPP-370, HPP-377 done or in_review; HPP-393 (P21)
#     not waiting; all without a run; else BUSY rc 4.  Disk C: free >= 60 GB (item 295 (v) of s145 as a member of the executor [I]).
#   STOP FILE (general rule 26): C:/kyty/f287/STOP -> rc 4 before anything, before the lock and before every tag.
#   THE SEAL'S CALL (item 105 (v)): the seal carries exactly one line "go_fs2 call: PLWAIT=<n> bash C:/kyty/f287/fs2c/go_fs2.sh
#     series"; fs2_read.py --check-seal checks every "seal:" line before the lock.
#   THE LOCK: checked before any process and before every guard stage; "lock taken|released series <UTC>" -> lock.log; every event
#     -> one UTC line of C:/kyty/f287/times.txt at the moment of the event.
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, --pred of the seal; KYTY_GPU_CHECKPOINTS never passed.
# EXIT CODES: 0 series done (read score_<tag>.txt, summary_fs2.txt); 1 hard refusal / series stopped / restore failed;
#   2 usage / not configured; 4 BUSY (lock, stop file, guards, idle) - no run.
#   DRY=1 go_fs2.sh series prints the plan and exits 0 after the cheap refusals, before any guard, lock or install.
T=${1:-}
ROOT=C:/kyty/f287/fs2c
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/f287/STOP
EMUD="/c/kyty/KytyPS5/ps5 em"
GAME="$EMUD/kyty_emulator.exe"
BUILD_EXPECT="dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e"
BUILD_PINNED="/c/kyty/s146/kyty_emulator_dac02fb9.exe"
BIN="C:/kyty/f287/bin/kyty_emulator_bbad499c.exe"
BIN_EXPECT="bbad499c56b744dfcef85b7556735c025ebb3db185b6bb9b02e7a0b3a228eb55"
SIGSTR="56189185f9e9f9a0ea5174f3f85206e6d099db3d"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
VKDUP="100000000"
STANDV="60:10"
PRED="pred/01_fs2.md"
CACHE="$EMUD/_ShaderCache/PPSA21564"
SNAP=$ROOT/cache_snap/PPSA21564
GLSNAP=$ROOT/glcache_snap
PCDIR="$EMUD/_PipelineCache"
PCSNAP=$ROOT/pcache_snap
SKY=underwater_aerial_garden
TC=timestop_casino
WHOLD="310"
VHOLD="330"
HOLDW="60"
HOLDT="125"
DISKMIN_GB=60
SEQ="fs2_w fs2_w0 fs2_v fs2_tw fs2_t"
ALLT="fs2_w fs2_w0 fs2_v fs2_tw fs2_t fs2_tr"
RSLEEP=5
PLMAX=540
IDLEMAX=300
IDLESTEP=15
PLWAIT=${PLWAIT:-$PLMAX}
if [ "$T" != "series" ]; then echo "usage: go_fs2.sh series  (see the header)"; exit 2; fi
L=$ROOT/go_fs2.log
TIMES=/c/kyty/f287/times.txt
LOCKLOG=$ROOT/lock.log
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
tl() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS2c go_fs2 $*" >> $TIMES; }
busy() { log "go_fs2.sh refused BUSY (rc 4): $* - no run made"; echo "busy: $*"; exit 4; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
if [ -e $STOPF ]; then STOPTXT=""; read -r STOPTXT < $STOPF 2>/dev/null; busy "stop file $STOPF: $STOPTXT"; fi
lockheld() {
  if [ -e $LOCK ]; then LOCKTXT=""; read -r LOCKTXT < $LOCK 2>/dev/null; busy "lock held: $LOCKTXT"; fi
}
lockheld
WINPID=""
read -r WINPID < /proc/$$/winpid 2>/dev/null
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_B1B KYTY_FIX_DUALSRC KYTY_FIX_MINIMIZE KYTY_FIX_B9A KYTY_PRINT_NAMES KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW KYTY_PVAR KYTY_TEST_MINIMIZE KYTY_BVH_NATIVE KYTY_BVH_STUB KYTY_BVH_LOOP_CAP KYTY_SHADER_CACHE KYTY_REC VK_LAYER_MESSAGE_ID_FILTER VK_LAYER_DUPLICATE_MESSAGE_LIMIT
if [ -z "$BIN" ] || [ -z "$BIN_EXPECT" ]; then log "go_fs2.sh refused: not configured (BIN/BIN_EXPECT)"; echo "not configured"; exit 2; fi
case "$PLWAIT" in
  ''|*[!0-9]*) log "go_fs2.sh refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then log "go_fs2.sh refused: PLWAIT $PLWAIT > $PLMAX"; echo "PLWAIT above $PLMAX"; exit 2; fi
for C in $ALLT; do
  if [ -e "attempt_$C.txt" ] || [ -e "$C.json" ]; then
    log "go_fs2.sh refused: attempt_$C.txt or $C.json exists - the one attempt of the series was made (no repeat)"
    echo "attempt already made"; exit 1
  fi
done
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go_fs2 call: PLWAIT="*" bash C:/kyty/f287/fs2c/go_fs2.sh series")
        V=${PLINE#go_fs2 call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go_fs2.sh refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL')"
  echo "PLWAIT differs from the seal"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY series: tags $SEQ (+ fs2_tr when fs2_t says repeat-k3); stop file?; lock?; PLWAIT=$PLWAIT; binary copy sha ($BIN_EXPECT) + strings FixMinimize/FixB9a/TestMinimize: armed/SwapchainZeroExtent: begin/AudioPropagation: calls/$SIGSTR; installed = $BUILD_EXPECT; disk >= $DISKMIN_GB GB; procload --wait-s $PLWAIT (masked); fs2_read --check-seal; cpu < 15; idle142 wait up to $IDLEMAX s; procload --wait-s 0; stop file?; window win_fs2 (HPP-382, HPP-381 done; HPP-370, HPP-377 done or in_review; HPP-393 not waiting); lock (lock.log UTC); shader cache content list + variant directory list + signature manifest + copy to $SNAP; GLCache manifest + copy; _PipelineCache list + copy; fgcpu146 --save; install $BIN; per tag: stop file?, binary copy and installed sha = $BIN_EXPECT, idle142 wait (one retry of a BUSY refusal), enter_scene.py <tag> --level <L> --attempts 1 --no-install --require-idle --pred $ROOT/$PRED (fs2_w: $SKY --stable-draws 300 --timeout 600 --emu-arg=--vulkan-validation true --hold $WHOLD VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_TEST_MINIMIZE=$STANDV; fs2_w0: as fs2_w + KYTY_FIX_MINIMIZE=0; fs2_v: $SKY --stable-draws 300 --timeout 480 --rec --hold $VHOLD KYTY_TEST_MINIMIZE=$STANDV; fs2_tw: $TC --stable-draws 100 --timeout 480 --hold $HOLDW; fs2_t/fs2_tr: $TC --stable-draws 100 --timeout 480 --rec --hold $HOLDT) KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, log sha, s51_vidglitch 4 6 + sheet142 (fs2_v, fs2_t, fs2_tr), fs2_read --tag, fs2_read --stop-check; EXIT: restore $BUILD_PINNED ($BUILD_EXPECT), shader cache / GLCache / _PipelineCache returned (lists = before), fgcpu146 row, unlock; fs2_read --summary"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then
  log "go_fs2.sh refused: pinned copy $BUILD_PINNED missing or its sha != $BUILD_EXPECT"; echo "pinned build bad"; exit 1
fi
if [ ! -f "$BIN" ] || [ "$(sha "$BIN")" != "$BIN_EXPECT" ]; then
  log "go_fs2.sh refused: FS2 binary $BIN missing or its sha != $BIN_EXPECT"; echo "FS2 binary bad"; exit 1
fi
for S in "FixMinimize: on" "FixB9a: on" "TestMinimize: armed" "SwapchainZeroExtent: begin" "AudioPropagation: calls" "$SIGSTR"; do
  if [ "$(grep -c -a -F "$S" "$BIN")" = "0" ]; then log "go_fs2.sh refused: FS2 binary lacks the string '$S'"; echo "FS2 binary strings bad"; exit 1; fi
done
if [ "$(sha "$GAME")" != "$BUILD_EXPECT" ]; then
  log "go_fs2.sh refused: the installed $GAME is not $BUILD_EXPECT before the series - not starting"; echo "installed build bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go_fs2.sh refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1
fi
FREE_GB=$(df -BG /c 2>/dev/null | tail -1 | awk '{print $4}' | tr -d 'G')
case "$FREE_GB" in ''|*[!0-9]*) log "go_fs2.sh refused: free disk unknown ('$FREE_GB')"; echo "disk unknown"; exit 1;; esac
if [ "$FREE_GB" -lt "$DISKMIN_GB" ]; then log "go_fs2.sh refused: free disk C: $FREE_GB GB < $DISKMIN_GB GB"; echo "disk low"; exit 1; fi
[ -d "$PCDIR" ] || { log "go_fs2.sh refused: _PipelineCache absent (the harness returns an existing directory)"; echo "no _PipelineCache"; exit 1; }
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
GLDIR="$LOCALAPPDATA/NVIDIA/GLCache"
mkdir -p runs
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*|test_[a-z0-9_]*fs2|mutlib' -or \$_.Name -eq 'kyty_emulator.exe' -or \$_.Name -eq 'qrenderdoc.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS2c go_fs2 BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)" >> $TIMES
}
guards() {
  python $ROOT/procload.py --wait-s "$1" 2>&1 | mask >> $L
  [ "${PIPESTATUS[0]}" = "0" ] || { log "a process stays busy after $1 s"; busyname "procload --wait-s $1"; return 1; }
  NAMES=$(names_alive)
  if [ -z "$NAMES" ] || [ "$NAMES" != "0" ]; then log "a mutant/fixture/emulator/qrenderdoc process lives ($NAMES)"; return 1; fi
  return 0
}
idlewait() {
  WS=0
  while :; do
    if [ -e $STOPF ]; then tl "$1 stop file during the idle wait: $(head -1 $STOPF)"; return 1; fi
    if python $ROOT/idle142.py 2>&1 | mask >> $L && [ "${PIPESTATUS[0]}" = "0" ]; then tl "$1 idle142 IDLE after $WS s of wait"; return 0; fi
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
log "go_fs2.sh series requested (FS2 binary $BIN_EXPECT, installed $BUILD_EXPECT, PLWAIT=$PLWAIT, seq $SEQ, free disk $FREE_GB GB)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $ROOT/fs2_read.py --check-seal $ROOT/$PRED >> $L 2>&1; then
  log "fs2_read.py --check-seal refused (see above) - not starting"; echo "seal check failed"; exit 1
fi
lockheld
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
log "idle check cpu=$CPU (< 15)"
case "$CPU" in ''|*[!0-9]*) busy "machine not idle (cpu='$CPU')";; esac
if [ "$CPU" -ge 15 ]; then busy "machine not idle (cpu='$CPU')"; fi
lockheld
idlewait "pre-lock" || busy "machine not idle by idle142 within $IDLEMAX s"
lockheld
guards 0 || busy "procload / name guard not clean before the lock"
if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi
WIN=$(python $ROOT/win_fs2.py 2>&1 | tail -1 | tr -d '\r')
tl "lock window (p.298(e), p.322(g)): $WIN"
case "$WIN" in *"-> open") ;; *) busy "lock window closed or unknown: $WIN";; esac
lockheld
set -o noclobber
if ! { echo "go_fs2.sh series pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  busy "lock taken by someone else: $(cat $LOCK 2>/dev/null)"
fi
set +o noclobber
echo "lock taken series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG
tl "lock taken (winpid $WINPID)"
tl "installed build at the start of the series sha256 $(sha "$GAME") (BUILD_EXPECT $BUILD_EXPECT; returned to it by sha)"
INSTALLED=0
RETFAIL=0
SNAPPED=0
GLSNAPPED=0
PCSNAPPED=0
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
    tl "shader cache at the end of the series (before the return): $LIST_RUN; $(dirlist "$CACHE"); $(python $ROOT/cachesig_f6e.py "$CACHE" 2>&1 | tail -1 | tr -d '\r')"
    KEEP=$ROOT/cache_run/$(date -u +%Y%m%dT%H%M%SZ)
    mkdir -p "$KEEP"
    if mv "$CACHE" "$KEEP/" && cp -a "$SNAP" "$CACHE"; then
      LIST_BACK=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_back.txt 2>&1 | tail -1 | tr -d '\r')
      DIRS_BACK=$(dirlist "$CACHE")
      if [ "$LIST_BACK" = "$LIST_BEFORE" ] && [ "$DIRS_BACK" = "$DIRS_BEFORE" ]; then
        tl "shader cache returned: $LIST_BACK = before; $DIRS_BACK = before; run cache kept in $KEEP"
      else
        tl "SHADER CACHE RESTORE FAILED: back '$LIST_BACK' / '$DIRS_BACK' != before '$LIST_BEFORE' / '$DIRS_BEFORE'"; echo "cache restore failed"; RCX=1; RETFAIL=1
      fi
    else
      tl "SHADER CACHE RESTORE FAILED: move/copy error ($CACHE, $KEEP, $SNAP)"; echo "cache restore failed"; RCX=1; RETFAIL=1
    fi
  fi
  if [ "$GLSNAPPED" = "1" ]; then
    CMA=$(python $ROOT/cachemf146.py runs/cache_series.after.json 2>&1 | tail -1 | tr -d '\r')
    tl "cache manifest after the series (before the GLCache return): $CMA"
    GLKEEP=$ROOT/glcache_run/$(date -u +%Y%m%dT%H%M%SZ)
    mkdir -p "$GLKEEP"
    if mv "$GLDIR" "$GLKEEP/" && cp -a "$GLSNAP/GLCache" "$GLDIR"; then
      GLB=$(python $ROOT/shalist_f2c.py "$GLDIR" 2>&1 | tail -1 | tr -d '\r')
      if [ "$GLB" = "$GL_BEFORE" ]; then tl "GLCache returned: $GLB = before"; else tl "GLCACHE RESTORE FAILED: '$GLB' != '$GL_BEFORE'"; RCX=1; RETFAIL=1; fi
    else
      tl "GLCACHE RESTORE FAILED: move/copy error"; RCX=1; RETFAIL=1
    fi
  fi
  if [ "$PCSNAPPED" = "1" ]; then
    PCKEEP=$ROOT/pcache_run/$(date -u +%Y%m%dT%H%M%SZ)
    mkdir -p "$PCKEEP"
    PCR=$(python $ROOT/shalist_f2c.py "$PCDIR" 2>&1 | tail -1 | tr -d '\r')
    tl "_PipelineCache at the end of the series (before the return): $PCR"
    if mv "$PCDIR" "$PCKEEP/" && cp -a "$PCSNAP/_PipelineCache" "$PCDIR"; then
      PCB=$(python $ROOT/shalist_f2c.py "$PCDIR" 2>&1 | tail -1 | tr -d '\r')
      if [ "$PCB" = "$PC_BEFORE" ]; then tl "_PipelineCache returned: $PCB = before"; else tl "PIPELINECACHE RESTORE FAILED: '$PCB' != '$PC_BEFORE'"; RCX=1; RETFAIL=1; fi
    else
      tl "PIPELINECACHE RESTORE FAILED: move/copy error"; RCX=1; RETFAIL=1
    fi
  fi
  if [ "$RETFAIL" = "1" ]; then
    echo "FS2c binary or cache return failed $(date -u +%Y-%m-%dT%H:%M:%SZ) - track F stopped, comment in HPP-383" > $STOPF
    tl "stop file written: binary or cache return failed"
  fi
  FG=$(python $ROOT/fgcpu146.py --since runs/fgcpu_series.a.json --chain-pid $WINPID 2>&1 | tail -1 | tr -d '\r')
  tl "foreign cpu at the end inside the lock: $FG"
  rm -f $LOCK
  echo "lock released series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG
  tl "lock released (rc $RCX)"
  exit $RCX
}
trap finish EXIT
LIST_BEFORE=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_before.txt 2>&1 | tail -1 | tr -d '\r')
DIRS_BEFORE=$(dirlist "$CACHE")
tl "shader cache before the series: $LIST_BEFORE; $DIRS_BEFORE; $(python $ROOT/cachesig_f6e.py "$CACHE" 2>&1 | tail -1 | tr -d '\r')"
rm -rf "$ROOT/cache_snap"
mkdir -p "$ROOT/cache_snap"
cp -a "$CACHE" "$SNAP" || { tl "shader cache copy failed - stop"; exit 1; }
LIST_SNAP=$(python $ROOT/shalist_f2c.py "$SNAP" 2>&1 | tail -1 | tr -d '\r')
DIRS_SNAP=$(dirlist "$SNAP")
[ "$LIST_SNAP" = "$LIST_BEFORE" ] && [ "$DIRS_SNAP" = "$DIRS_BEFORE" ] || { tl "shader cache copy differs: '$LIST_SNAP' / '$DIRS_SNAP' != '$LIST_BEFORE' / '$DIRS_BEFORE' - stop"; exit 1; }
SNAPPED=1
tl "shader cache copy = before ($ROOT/cache_snap)"
CMB=$(python $ROOT/cachemf146.py runs/cache_series.before.json 2>&1 | tail -1 | tr -d '\r')
tl "cache manifest before the series: $CMB"
GL_BEFORE=$(python $ROOT/shalist_f2c.py "$GLDIR" 2>&1 | tail -1 | tr -d '\r')
rm -rf "$GLSNAP"
mkdir -p "$GLSNAP"
cp -a "$GLDIR" "$GLSNAP/GLCache" || { tl "GLCache copy failed - stop"; exit 1; }
GL_SNAP=$(python $ROOT/shalist_f2c.py "$GLSNAP/GLCache" 2>&1 | tail -1 | tr -d '\r')
[ "$GL_SNAP" = "$GL_BEFORE" ] || { tl "GLCache copy differs: '$GL_SNAP' != '$GL_BEFORE' - stop"; exit 1; }
GLSNAPPED=1
tl "GLCache before the series: $GL_BEFORE (copy equal)"
PC_BEFORE=$(python $ROOT/shalist_f2c.py "$PCDIR" 2>&1 | tail -1 | tr -d '\r')
rm -rf "$PCSNAP"
mkdir -p "$PCSNAP"
cp -a "$PCDIR" "$PCSNAP/_PipelineCache" || { tl "_PipelineCache copy failed - stop"; exit 1; }
PC_SNAP=$(python $ROOT/shalist_f2c.py "$PCSNAP/_PipelineCache" 2>&1 | tail -1 | tr -d '\r')
[ "$PC_SNAP" = "$PC_BEFORE" ] || { tl "_PipelineCache copy differs: '$PC_SNAP' != '$PC_BEFORE' - stop"; exit 1; }
PCSNAPPED=1
tl "_PipelineCache before the series: $PC_BEFORE (copy equal)"
python $ROOT/fgcpu146.py --save runs/fgcpu_series.a.json >> $L 2>&1
INSTALLED=1
cp "$BIN" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "installed sha != $BIN_EXPECT - stop"; tl "install failed"; exit 1; }
tl "installed FS2 binary sha256 $BIN_EXPECT"
log "files: $(sha256sum fs2_read.py test_fs2_read.py test_go_fs2.py win_fs2.py cachesig_f6e.py shalist_f2c.py $PRED gates_default.txt enter_scene.py launch_run.py run_safety99.py idle142.py procload.py go_fs2.sh sheet142.py fgcpu146.py cachemf146.py C:/kyty/s142/sc142.py C:/kyty/f287/f5c/f5c_read.py C:/kyty/f287/f6e/f6e_read.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
runtag() {
  echo "go_fs2.sh $C pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) FS2 binary $BIN_EXPECT" > attempt_$C.txt
  tl "$C enter_scene start$1 (level $LV, hold $HH, sd '$SD', extra '$EXTRA', emu '$EMUX', rec '$RECF')"
  python $ROOT/enter_scene.py $C --level $LV --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt \
    --pred $ROOT/$PRED $RECF $EMUX --hold $HH $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $C.stdout.txt 2>&1
}
refused() { [ "$1" = "3" ] && [ -e $C.refused.json ] && [ ! -e log_$C.txt ] && [ ! -e $C.json ]; }
# one tag: binary check, idle wait, enter_scene (one retry of a BUSY refusal), video, reader; sets SC (stop check line) and RC
onetag() {
  SC="stop: not run"
  RC=9
  if [ -e $STOPF ]; then tl "stop file before $C: $(head -1 $STOPF) - series stopped"; return 1; fi
  if [ "$(sha "$BIN")" != "$BIN_EXPECT" ] || [ "$(sha "$GAME")" != "$BIN_EXPECT" ]; then
    tl "$C binary check failed (p.286(b)): copy $(sha "$BIN" | cut -c1-16) installed $(sha "$GAME" | cut -c1-16) - series stop"
    return 1
  fi
  tl "$C binary check ok (p.286(b)): copy and installed sha256 $BIN_EXPECT"
  WU=0; RECF=""; EMUX=""; EXTRA=""
  WX="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_TEST_MINIMIZE=$STANDV"
  case "$C" in
    fs2_w)  LV=$SKY; SD="--stable-draws 300 --timeout 600"; HH=$WHOLD; EMUX="--emu-arg=--vulkan-validation --emu-arg=true"; EXTRA="$WX";;
    fs2_w0) LV=$SKY; SD="--stable-draws 300 --timeout 600"; HH=$WHOLD; EMUX="--emu-arg=--vulkan-validation --emu-arg=true"; EXTRA="$WX KYTY_FIX_MINIMIZE=0";;
    fs2_v)  LV=$SKY; SD="--stable-draws 300 --timeout 480"; HH=$VHOLD; RECF="--rec"; EXTRA="KYTY_TEST_MINIMIZE=$STANDV";;
    fs2_tw) LV=$TC; SD="--stable-draws 100 --timeout 480"; HH=$HOLDW; WU=1;;
    fs2_t|fs2_tr) LV=$TC; SD="--stable-draws 100 --timeout 480"; HH=$HOLDT; RECF="--rec";;
    *) tl "$C unknown tag - series stop"; return 1;;
  esac
  if [ -n "$EMUX" ]; then tl "$C W form (p.295(b)(4)) from the env the harness writes: W form: limit=$VKDUP filter=none"; fi
  if ! idlewait $C; then tl "$C series stop BUSY before the tag (not an attempt) - question to the lead"; return 1; fi
  runtag ""
  RC=$?
  if refused $RC; then
    for F in attempt_$C.txt $C.refused.json $C.stdout.txt; do mv "$F" "${F/$C/$C.busyr1}"; done
    tl "$C enter_scene refused BUSY before the emulator start (not an attempt): $(grep -o 'REFUSED.*' $C.busyr1.stdout.txt | head -1 | cut -c1-160)"
    if ! idlewait $C; then tl "$C series stop BUSY before the retry (not an attempt) - question to the lead"; return 1; fi
    runtag " (retry after a BUSY refusal)"
    RC=$?
    if refused $RC; then tl "$C second BUSY refusal before the emulator start (not an attempt) - series stop, question to the lead"; return 1; fi
  fi
  tl "$C enter_scene end rc $RC log_$C.txt sha256 $(sha log_$C.txt) bytes $(stat -c %s log_$C.txt 2>/dev/null)"
  if [ "$WU" = "1" ]; then
    WD=$(cat log_$C.txt stdout_$C.txt 2>/dev/null | grep -a -c -E 'Unhandled exception:|--- Fatal Error ---|--- Error ---|GpuHangAbort:|ErrorDeviceLost|Window [0-9]+ minimized|Recovering Vulkan swapchain')
    if [ "$WD" = "0" ] && [ "$RC" = "0" ]; then SC="continue: warm-up $C not read (p.327(g)(2))"; else SC="stop: warm-up $C rc $RC death or window lines $WD"; fi
    tl "$C warm-up (not read, p.327(g)(2)): rc $RC, death/window lines $WD -> $SC"
    return 0
  fi
  if [ -n "$RECF" ]; then
    if [ -f "rec_$C.mp4" ]; then
      python $VIDGLITCH rec_$C.mp4 4 6 $ROOT/vidframes_$C > glitch_$C.txt 2>&1
      tl "$C s51_vidglitch rc $? glitch_$C.txt sha256 $(sha glitch_$C.txt) rec_$C.mp4 sha256 $(sha rec_$C.mp4) idx sha256 $(sha rec_$C.mp4.idx)"
      python $ROOT/sheet142.py rec_$C.mp4 sheet_$C.png > sheet_$C.txt 2>&1
      tl "$C sheet rc $? sheet_$C.png sha256 $(sha sheet_$C.png)"
    else
      tl "$C no video rec_$C.mp4"
    fi
  fi
  python $ROOT/fs2_read.py --tag $C --json runs/$C.read.json > score_$C.txt 2>&1
  tl "$C reader rc $? score_$C.txt sha256 $(sha score_$C.txt): $(grep '^FS2 VERDICT' score_$C.txt | tr '\n' ';' | cut -c1-300)"
  SC=$(python $ROOT/fs2_read.py --stop-check runs/$C.read.json 2>&1 | tail -1 | tr -d '\r')
  tl "$C stop check (enter_scene rc $RC): $SC"
  return 0
}
SERIES_RC=0
for C in $SEQ; do
  onetag || { SERIES_RC=1; break; }
  case "$SC" in
    "continue"*|"repeat-k3: "*) ;;
    *) tl "$C series stop: $SC - later tags not run, question to the lead"; SERIES_RC=1; break;;
  esac
  if [ "$RC" != "0" ] && [ "$C" != "fs2_w0" ]; then
    case "$SC" in
      "continue: validation"*) tl "$C enter_scene rc $RC with a validation stop - data, the series goes on";;
      *) tl "$C series stop: enter_scene rc $RC - later tags not run, question to the lead"; SERIES_RC=1; break;;
    esac
  fi
  case "$SC" in
    "repeat-k3: fs2_tr"*)
      C=fs2_tr
      tl "fs2_t K3 hold over the limit - one repeat fs2_tr (p.287(v)(5), p.327(g)(2))"
      onetag || { SERIES_RC=1; break; }
      case "$SC" in
        "continue"*) ;;
        *) tl "$C series stop: $SC - question to the lead"; SERIES_RC=1; break;;
      esac
      if [ "$RC" != "0" ]; then tl "$C series stop: enter_scene rc $RC - question to the lead"; SERIES_RC=1; break; fi
      ;;
  esac
done
python $ROOT/fs2_read.py --summary > summary_fs2.txt 2>&1
tl "summary rc $? summary_fs2.txt sha256 $(sha summary_fs2.txt): $(grep '^FS2 SERIES VERDICT' summary_fs2.txt | cut -c1-300)"
exit $SERIES_RC
