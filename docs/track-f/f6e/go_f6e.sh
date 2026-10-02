#!/bin/bash
# Track F link F6e (HPP-377; ROADMAP "SESSION 122" item 287 (v)(5)-(7), (d); item 290 (b)(1)-(2); item 294 (b)-(g)): the runs of
# item 287 (v)(5) on the copy of the F6c binary (B9a V1, d8756dce, PASS_WITH_FIXES of F6d without a code change) as ONE series
# under ONE lock - the fix binary is installed once and the installed build 9235a7ac and the caches come back in the same
# command (EXIT trap), so no other run can meet the fix binary or the caches written by it.
# Port of C:/kyty/f287/f3d/go_f3d.sh: lock first, guards, one attempt, seal call line, stop file, lock.log UTC, times lines,
# cache copy/return by content lists and the variant directory list, GLCache copy/return, idle wait before every tag with one
# retry of a BUSY refusal of enter_scene.py.  ASCII only (item 175 (v)).  No emulator code, no build.
# SEAL 02 (ROADMAP item 306 (g), (d)): series 1 (lock 2026-10-01 17:11:39-17:15:31Z, f6e_a1 NOT ADMITTED by I10) is kept in
#   series1/ as information (item 306 (g) B2 (1)); this series first makes TWO WARM-UP entries on the F6c copy at
#   KYTY_FIX_B9A=0 - f6e_w1 timestop_casino, f6e_w2 mini_astro_clock_tower, hold HOLDW s wall, no video, NOT READ (B2 (2)) -
#   so the variant directory of the translation cache (cold on this binary) is warm before f6e_a1; the variant directory is
#   held to the end of the series and returned with the caches (B2 (3)).  A warm-up stops the series only on enter_scene
#   rc != 0 or a death marker / window line in its log or stdout [I12].  I10 of the reader by B1.  The lock window also
#   needs HPP-353 (audit of session 145) done (item 306 (d)).
#   TAGS AND ORDER (item 287 (v)(5); one attempt each, a failure is data): form V of sc144 - no validation, precache by
#     default (KYTY_PIPELINE_PRECACHE not passed, item 281 (g)), video (KYTY_REC), FrameTrace, hold HOLD s wall from "stable"
#     (the reader: sum dt_us after the first scene frame >= 120 s):
#     f6e_a1, f6e_a2  timestop_casino         KYTY_FIX_B9A=1
#     f6e_b1          mini_astro_clock_tower  KYTY_FIX_B9A=1
#     f6e_c1          timestop_casino         KYTY_FIX_B9A=0  (control, item 287 (v)(6))
#     f6e_c2          mini_astro_clock_tower  KYTY_FIX_B9A=0  (control)
#   REPEATS: (1) form (item 290 (b)(2)): a tag whose 'FixB9a: on' count is not 1 (=1) / 0 (=0) is INVALID - one repeat
#     <tag>f right after it (the reader's stop check says "repeat-form"); INVALID again - series stop.  (2) K3 (item 287
#     (v)(5)): after the controls, f6e_read.py --repeats names the =1 tags whose K3 hold exceeds max(base, control) - one
#     repeat <tag>r each, by a times line of the executor; the repeat decides.  A repeat never lifts the ASSERT member (294 (b)).
#   KNOB: exactly KYTY_FIX_B9A=1 or =0; KYTY_FIX_B26/B1B/DUALSRC/MINIMIZE never passed (defaults of the binary); KYTY_PRINT_NAMES
#     never passed and unset (item 294 (g) N4); KYTY_GPU_CHECKPOINTS never passed.
#   BINARY (item 287 (v)(5)): only the copy BIN_F6E, its sha256 checked before the lock, after the install and before EVERY
#     tag (the copy and the installed file); it must hold the strings "FixB9a: on", "AudioPropagation: calls" and the
#     translation signature 56189185...; no rebuild.
#   SERIES STOP (f6e_read.py --stop-check, and enter_scene rc != 0): no reading, NOT ADMITTED, WINDOW EVENT, a death marker,
#     INVALID twice, a failed enter_scene - later tags not run, the question goes to the lead.  FAIL of a member is data.
#   CACHES (item 287 (d), item 228 (v)): inside the lock, before the install: _ShaderCache/PPSA21564 (root files, every variant
#     directory, the recipes pipelines.bin) copied to cache_snap/PPSA21564, the two content lists equal (shalist_f2c.py); the list
#     of the variant directories and the signature manifest (cachesig_f6e.py, item 290 (b)(1)) are times lines before and
#     after; EXIT trap: the run's cache MOVED to cache_run/<UTC>/, the snapshot copied back, its content list and its directory
#     list must equal the lists before (a directory absent before is absent after), else RESTORE FAILED rc 1; GLCache
#     (cachemf143.py manifest before / after, copy glcache_snap/) back from its copy (GLRESTORE=1).  A failed return writes the
#     stop file C:/kyty/f287/STOP.
#   LOCK WINDOW (item 287 (d)): right before the lock - no lock file, no stop file, by the API answer (win_f6e.py, a times line
#     with the answer): HPP-376 done, HPP-357 (F5c) and HPP-370 (FSc) done or in_review, HPP-352 (session run step) and HPP-364
#     (P17) neither todo nor in_progress, all without a run; else BUSY rc 4.
#   STOP FILE (general rule 26): C:/kyty/f287/STOP -> rc 4 before anything, before the lock and before every tag.
#   THE SEAL'S CALL (item 105 (v)): the seal carries exactly one line "go_f6e call: PLWAIT=<n> bash
#     C:/kyty/f287/f6e/go_f6e.sh series"; f6e_read.py --check-seal checks every "seal:" line before the lock.
#   THE LOCK: checked before any process and before every guard stage; "lock taken|released series <UTC>" -> lock.log;
#     every event -> one UTC line of C:/kyty/f287/times.txt at the moment of the event.
# Every run: KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, --pred of the seal; KYTY_GPU_CHECKPOINTS never passed.
# EXIT CODES: 0 series done (read score_<tag>.txt, f6e_read.py --summary); 1 hard refusal / series stopped / restore failed;
#   2 usage / not configured; 4 BUSY (lock, stop file, guards, idle) - no run.
#   DRY=1 go_f6e.sh series prints the plan and exits 0 after the cheap refusals, before any guard, lock or install.
T=${1:-}
ROOT=C:/kyty/f287/f6e
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/f287/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"
BIN_F6E="C:/kyty/f287/bin/kyty_emulator_d8756dce.exe"
BIN_EXPECT="d8756dce0662fb318a24a3fb52a3260d31ea84628372fa9a438ca46ed6a6e43d"
SIGSTR="56189185f9e9f9a0ea5174f3f85206e6d099db3d"
GLRESTORE="1"
GATESHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIDGLITCH=C:/kyty/scripts/s51_vidglitch.py
PRED="pred/02_f6e.md"
CACHE="/c/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564"
SNAP=$ROOT/cache_snap/PPSA21564
GLSNAP=$ROOT/glcache_snap
TC=timestop_casino
MA=mini_astro_clock_tower
HOLD="125"
HOLDW="60"
WARM="f6e_w1 f6e_w2"
SEQ="f6e_a1 f6e_a2 f6e_b1 f6e_c1 f6e_c2"
ALLT="f6e_w1 f6e_w2 f6e_a1 f6e_a2 f6e_b1 f6e_c1 f6e_c2 f6e_a1f f6e_a2f f6e_b1f f6e_c1f f6e_c2f f6e_a1r f6e_a2r f6e_b1r"
RSLEEP=5
PLMAX=540
IDLEMAX=300
IDLESTEP=15
PLWAIT=${PLWAIT:-$PLMAX}
if [ "$T" != "series" ]; then echo "usage: go_f6e.sh series  (see the header)"; exit 2; fi
L=$ROOT/go_f6e.log
TIMES=/c/kyty/f287/times.txt
LOCKLOG=$ROOT/lock.log
cd "$ROOT" || exit 1
log() { printf '[%(%H:%M:%S)T] %s\n' -1 "$*" >> $L; }
tl() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F6e go_f6e $*" >> $TIMES; }
busy() { log "go_f6e.sh refused BUSY (rc 4): $* - no run made"; echo "busy: $*"; exit 4; }
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
unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_B1B KYTY_FIX_DUALSRC KYTY_FIX_MINIMIZE KYTY_FIX_B9A KYTY_PRINT_NAMES KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW KYTY_PVAR KYTY_TEST_MINIMIZE KYTY_BVH_NATIVE KYTY_BVH_STUB KYTY_BVH_LOOP_CAP KYTY_SHADER_CACHE KYTY_REC
if [ -z "$BIN_F6E" ] || [ -z "$BIN_EXPECT" ] || [ -z "$GLRESTORE" ]; then
  log "go_f6e.sh refused: not configured (BIN_F6E/BIN_EXPECT/GLRESTORE)"
  echo "not configured"; exit 2
fi
case "$PLWAIT" in
  ''|*[!0-9]*) log "go_f6e.sh refused: PLWAIT '$PLWAIT' is not a number of seconds"; echo "bad PLWAIT"; exit 2;;
esac
if [ "$PLWAIT" -gt "$PLMAX" ]; then log "go_f6e.sh refused: PLWAIT $PLWAIT > $PLMAX"; echo "PLWAIT above $PLMAX"; exit 2; fi
for C in $ALLT; do
  if [ -e "attempt_$C.txt" ] || [ -e "$C.json" ]; then
    log "go_f6e.sh refused: attempt_$C.txt or $C.json exists - the one attempt of the series was made (no repeat)"
    echo "attempt already made"; exit 1
  fi
done
SEALPL=""
NL=0
if [ -f "$PRED" ]; then
  while IFS= read -r PLINE || [ -n "$PLINE" ]; do
    PLINE=${PLINE%$'\r'}
    case "$PLINE" in
      "go_f6e call: PLWAIT="*" bash C:/kyty/f287/f6e/go_f6e.sh series")
        V=${PLINE#go_f6e call: PLWAIT=}; V=${V%% *}; SEALPL=$V; NL=$((NL+1));;
    esac
  done < "$PRED"
fi
if [ "$NL" != "1" ] || [ "$SEALPL" != "$PLWAIT" ]; then
  log "go_f6e.sh refused: PLWAIT=$PLWAIT is not the one call line of the seal $PRED (lines $NL, seal '$SEALPL')"
  echo "PLWAIT differs from the seal"; exit 1
fi
if [ "${DRY:-0}" = "1" ]; then
  echo "DRY series: tags $SEQ (+ one form repeat <tag>f on INVALID, + K3 repeats <tag>r by f6e_read --repeats after the controls); stop file?; lock?; PLWAIT=$PLWAIT; binary copy sha ($BIN_EXPECT) + strings FixB9a/AudioPropagation/$SIGSTR; procload --wait-s $PLWAIT; f6e_read --check-seal; cpu < 15; idle142 wait up to $IDLEMAX s; procload --wait-s 0; stop file?; window HPP-376 and HPP-353 done, HPP-357/HPP-370 done or in_review, HPP-352/HPP-364 not waiting (win_f6e); lock (lock.log UTC); shader cache content list + variant directory list + signature manifest (cachesig_f6e) + copy to $SNAP (lists equal); GLCache manifest + copy (GLRESTORE=$GLRESTORE); fgcpu143 --save; install $BIN_F6E; warm-up f6e_w1 ($TC) and f6e_w2 ($MA) KYTY_FIX_B9A=0 hold $HOLDW no video NOT READ (stop on rc != 0, death or window lines; p.306(g) B2); per tag: stop file?, binary copy and installed sha = $BIN_EXPECT, idle142 wait (one retry of a BUSY refusal), enter_scene.py <tag> --level <L> --attempts 1 --stable-draws 100 --timeout 480 --no-install --require-idle --pred $ROOT/$PRED --rec --hold $HOLD (a1,a2: $TC KYTY_FIX_B9A=1; b1: $MA KYTY_FIX_B9A=1; c1: $TC KYTY_FIX_B9A=0; c2: $MA KYTY_FIX_B9A=0) KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, log sha, s51_vidglitch 4 6 + sheet142, f6e_read --tag, f6e_read --stop-check; EXIT: restore $BUILD_PINNED ($BUILD_EXPECT), move run cache to cache_run/, copy snapshot back (content list and directory list = before), GLCache manifest after + restore (GLRESTORE=$GLRESTORE), fgcpu143 row, unlock; f6e_read --summary"
  exit 0
fi
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
if [ ! -f "$BUILD_PINNED" ] || [ "$(sha "$BUILD_PINNED")" != "$BUILD_EXPECT" ]; then
  log "go_f6e.sh refused: pinned copy $BUILD_PINNED missing or its sha != $BUILD_EXPECT"; echo "pinned build bad"; exit 1
fi
if [ ! -f "$BIN_F6E" ] || [ "$(sha "$BIN_F6E")" != "$BIN_EXPECT" ]; then
  log "go_f6e.sh refused: fix binary $BIN_F6E missing or its sha != $BIN_EXPECT"; echo "fix binary bad"; exit 1
fi
for S in "FixB9a: on" "AudioPropagation: calls" "$SIGSTR"; do
  if [ "$(grep -c -a "$S" "$BIN_F6E")" = "0" ]; then
    log "go_f6e.sh refused: fix binary lacks the string '$S'"; echo "fix binary strings bad"; exit 1
  fi
done
if [ "$(sha "$GAME")" != "$BUILD_EXPECT" ]; then
  log "go_f6e.sh refused: the installed $GAME is not $BUILD_EXPECT before the series - not starting"; echo "installed build bad"; exit 1
fi
if [ ! -f gates_default.txt ] || [ "$(sha gates_default.txt)" != "$GATESHA" ]; then
  log "go_f6e.sh refused: gates_default.txt is not the empty file"; echo "gate file bad"; exit 1
fi
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
GLDIR="$LOCALAPPDATA/NVIDIA/GLCache"
mkdir -p runs
names_alive() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\$_.CommandLine -match 'mut_[a-z0-9_]*|test_[a-z0-9_]*f6e|mutlib' -or \$_.Name -eq 'kyty_emulator.exe') -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r'
}
busyname() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F6e go_f6e BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)" >> $TIMES
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
log "go_f6e.sh series requested (fix binary $BIN_EXPECT, installed $BUILD_EXPECT, PLWAIT=$PLWAIT, seq $SEQ)"
lockheld
guards $PLWAIT || busy "procload / name guard not clean within $PLWAIT s"
lockheld
if ! python $ROOT/f6e_read.py --check-seal $ROOT/$PRED >> $L 2>&1; then
  log "f6e_read.py --check-seal refused (see above) - not starting"; echo "seal check failed"; exit 1
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
WIN=$(python $ROOT/win_f6e.py 2>&1 | tail -1 | tr -d '\r')
tl "lock window (p.287(d)): $WIN"
case "$WIN" in
  *"-> open") ;;
  *) busy "lock window closed or unknown: $WIN";;
esac
lockheld
set -o noclobber
if ! { echo "go_f6e.sh series pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
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
    tl "shader cache at the end of the series (before the return): $LIST_RUN; $(dirlist "$CACHE"); $(python $ROOT/cachesig_f6e.py "$CACHE" 2>&1 | tail -1 | tr -d '\r')"
    KEEP=$ROOT/cache_run/$(date -u +%Y%m%dT%H%M%SZ)
    mkdir -p "$KEEP"
    if mv "$CACHE" "$KEEP/" && cp -a "$SNAP" "$CACHE"; then
      LIST_BACK=$(python $ROOT/shalist_f2c.py "$CACHE" --out runs/shalist_cache_back.txt 2>&1 | tail -1 | tr -d '\r')
      DIRS_BACK=$(dirlist "$CACHE")
      if [ "$LIST_BACK" = "$LIST_BEFORE" ] && [ "$DIRS_BACK" = "$DIRS_BEFORE" ]; then
        tl "shader cache returned: $LIST_BACK = before; $DIRS_BACK = before (p.287(d)); run cache kept in $KEEP"
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
    echo "F6e binary or cache return failed $(date -u +%Y-%m-%dT%H:%M:%SZ) - track F stopped, comment in HPP-377" > $STOPF
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
# caches before the install (item 228 (v), item 287 (d), item 290 (b)(1))
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
cp "$BIN_F6E" "$GAME" || { log "install copy failed - stop"; exit 1; }
[ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "installed sha != $BIN_EXPECT - stop"; tl "install failed"; exit 1; }
tl "installed fix binary sha256 $BIN_EXPECT"
log "files: $(sha256sum f6e_read.py win_f6e.py cachesig_f6e.py shalist_f2c.py $PRED gates_default.txt enter_scene.py idle142.py procload.py go_f6e.sh sheet142.py fgcpu143.py cachemf143.py C:/kyty/s142/sc142.py $VIDGLITCH | cut -c1-16,65- | tr '\n' ';')"
runtag() {
  echo "go_f6e.sh $C pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) fix binary $BIN_EXPECT" > attempt_$C.txt
  tl "$C enter_scene start$1 (level $LV, hold $HH, extra '$EXTRA', rec '$RECF')"
  python $ROOT/enter_scene.py $C --level $LV --attempts 1 --stable-draws 100 --timeout 480 --no-install --require-idle \
    --gates-file $ROOT/gates_default.txt --pred $ROOT/$PRED $RECF --hold $HH $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $C.stdout.txt 2>&1
}
refused() { [ "$1" = "3" ] && [ -e $C.refused.json ] && [ ! -e log_$C.txt ] && [ ! -e $C.json ]; }
# one tag: binary check, idle wait, enter_scene (one retry of a BUSY refusal), video, reader; sets SC (stop check line) and RC
onetag() {
  SC="stop: not run"
  RC=9
  if [ -e $STOPF ]; then tl "stop file before $C: $(head -1 $STOPF) - series stopped"; return 1; fi
  if [ "$(sha "$BIN_F6E")" != "$BIN_EXPECT" ] || [ "$(sha "$GAME")" != "$BIN_EXPECT" ]; then
    tl "$C binary check failed: copy $(sha "$BIN_F6E" | cut -c1-16) installed $(sha "$GAME" | cut -c1-16) - series stop"
    return 1
  fi
  tl "$C binary check ok: copy and installed sha256 $BIN_EXPECT"
  WU=0; RECF="--rec"; HH=$HOLD
  case "$C" in
    f6e_w1) LV=$TC; EXTRA="KYTY_FIX_B9A=0"; WU=1; RECF=""; HH=$HOLDW;;
    f6e_w2) LV=$MA; EXTRA="KYTY_FIX_B9A=0"; WU=1; RECF=""; HH=$HOLDW;;
    f6e_a1|f6e_a1f|f6e_a1r|f6e_a2|f6e_a2f|f6e_a2r) LV=$TC; EXTRA="KYTY_FIX_B9A=1";;
    f6e_b1|f6e_b1f|f6e_b1r) LV=$MA; EXTRA="KYTY_FIX_B9A=1";;
    f6e_c1|f6e_c1f) LV=$TC; EXTRA="KYTY_FIX_B9A=0";;
    f6e_c2|f6e_c2f) LV=$MA; EXTRA="KYTY_FIX_B9A=0";;
    *) tl "$C unknown tag - series stop"; return 1;;
  esac
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
  tl "$C enter_scene end rc $RC log_$C.txt sha256 $(sha log_$C.txt)"
  if [ "$WU" = "1" ]; then
    WD=$(cat log_$C.txt stdout_$C.txt 2>/dev/null | grep -a -c -E 'Unhandled exception:|--- Fatal Error ---|--- Error ---|GpuHangAbort:|ErrorDeviceLost|Window [0-9]+ minimized|Recovering Vulkan swapchain')
    if [ "$WD" = "0" ]; then SC="continue: warm-up $C not read (p.306(g) B2)"; else SC="stop: warm-up $C death or window lines $WD [I12]"; fi
    tl "$C warm-up (not read, p.306(g) B2): death/window lines $WD -> $SC"
    return 0
  fi
  if [ -f "rec_$C.mp4" ]; then
    python $VIDGLITCH rec_$C.mp4 4 6 $ROOT/vidframes_$C > glitch_$C.txt 2>&1
    tl "$C s51_vidglitch rc $? glitch_$C.txt sha256 $(sha glitch_$C.txt) rec_$C.mp4 sha256 $(sha rec_$C.mp4)"
    python $ROOT/sheet142.py rec_$C.mp4 sheet_$C.png > sheet_$C.txt 2>&1
    tl "$C sheet rc $? sheet_$C.png sha256 $(sha sheet_$C.png)"
  else
    tl "$C no video rec_$C.mp4"
  fi
  python $ROOT/f6e_read.py --tag $C --json runs/$C.read.json > score_$C.txt 2>&1
  tl "$C reader rc $? score_$C.txt sha256 $(sha score_$C.txt): $(grep '^F6E VERDICT' score_$C.txt | tr '\n' ';' | cut -c1-300)"
  SC=$(python $ROOT/f6e_read.py --stop-check runs/$C.read.json 2>&1 | tail -1 | tr -d '\r')
  tl "$C stop check (enter_scene rc $RC): $SC"
  return 0
}
SERIES_RC=0
for B in $WARM $SEQ; do
  C=$B
  onetag || { SERIES_RC=1; break; }
  case "$SC" in
    "repeat-form: "*)
      C=${B}f
      tl "$B form repeat $C (p.290(b)(2): FixB9a line count wrong - a form error, not an attempt of the level)"
      onetag || { SERIES_RC=1; break; }
      ;;
  esac
  case "$SC" in
    "continue"*) ;;
    *) tl "$C series stop: $SC - later tags not run, question to the lead"; SERIES_RC=1; break;;
  esac
  if [ "$RC" != "0" ]; then tl "$C series stop: enter_scene rc $RC - later tags not run, question to the lead"; SERIES_RC=1; break; fi
done
if [ "$SERIES_RC" = "0" ]; then
  REP=$(python $ROOT/f6e_read.py --repeats 2>&1 | tail -1 | tr -d '\r')
  tl "K3 repeats (p.287(v)(5), executor line): $REP"
  case "$REP" in
    "repeat: none") ;;
    "repeat: "*)
      for C in ${REP#repeat: }; do
        onetag || { SERIES_RC=1; break; }
        case "$SC" in
          "continue"*) ;;
          *) tl "$C series stop: $SC - question to the lead"; SERIES_RC=1; break;;
        esac
        if [ "$RC" != "0" ]; then tl "$C series stop: enter_scene rc $RC - question to the lead"; SERIES_RC=1; break; fi
      done
      ;;
    *) tl "K3 repeats not read: $REP - question to the lead"; SERIES_RC=1;;
  esac
fi
python $ROOT/f6e_read.py --summary > summary_f6e.txt 2>&1
tl "summary rc $? summary_f6e.txt sha256 $(sha summary_f6e.txt): $(grep '^F6E SERIES VERDICT' summary_f6e.txt | cut -c1-300)"
exit $SERIES_RC
