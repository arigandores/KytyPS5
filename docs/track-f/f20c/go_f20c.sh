#!/bin/bash
# Track F link F20c (HPP-561; ROADMAP s122 item 462 (g)): one V Sky Garden tag f20_vNN of the B2 / B32 series on the INSTALLED binary
# (S12 adb0c82f, or FS6 9325446c after the install by FS6d HPP-558) - nothing is installed.  ONE TAG = ONE LOCK.  Port of
# C:/kyty/f287/f18e/go_f18e.sh (F18e HPP-541): stop file, lock, live emulator, procload through the <app> mask, lock.log UTC, caches
# (_ShaderCache with PPSA21564/pipelines.bin, _PipelineCache, _SaveData) and the driver GLCache copied before and returned after, manifest
# sha256 before the tag, of the run state and after the return with the equality line; RETURN_FAILED keeps the lock.  The installed
# binary is read before the lock, inside the lock (installed_before.txt) and after the tag (installed_after.txt); it must be one of the
# two allowed and the same before and after.  Order: f20_vNN starts only when runs/f20_v(NN-1) exists; at most 30 tags (item 462 (g)).
# usage: bash C:/kyty/f287/f20c/go_f20c.sh f20_v01 ... f20_v30
#   FORM (seal docs/track-f/f20c.md = pred/f20c_seal.md; the form of the V of s12_v, item 462 (g)): enter_scene.py <tag> --level
#     underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt
#     --pred <seal> --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0.  No knob, no stand, no KYTY_GAME_PATCH, no validation, no
#     --shader-validation true, no RenderDoc, no KYTY_GPU_CHECKPOINTS (enter_scene.py builds the env from the positional pairs; this
#     script unsets KYTY_* and VK_LAYER_* before the call).  Exit: WM_CLOSE at the end of the hold, CLOSE_WAIT_S 40 s.  ASCII only.
# EXIT: 0 tag made (read it with post_f20c.sh); 1 hard refusal / return failed; 2 usage / the tag exists / order; 3 lock / live emulator;
#   4 stop file; 5 procload busy.
# ITEM 534 (general rule 33, incident f20_v11): no kill by image name - only the own emulator tree by its pid (guard_f20c.py kill-own, pid
#   file runs/<tag>/game_pid.txt written by enter_scene.py); a user emulator or launcher (guard_f20c.py scan) before the lock => not
#   starting; right after the lock, before the manifest => lock released, files untouched, runs/<tag> -> <tag>.user_*, interference;
#   during the tag (guard_f20c.py watch) => the own emulator killed by pid, the user process untouched, caches and GLCache returned only
#   after the user process is gone (wait-gone, poll 10 s, the lock stays), runs/<tag> -> <tag>.user_*, interference; a tag that never
#   started enter_scene => runs/<tag> -> <tag>.nostart_* (interference, repeat by the same name).
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f20c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
ADB=adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421
FS6=9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2
SEAL=$G/pred/f20c_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
LV=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f20_v0[1-9]|f20_v[12][0-9]|f20_v30) ;;
  *) echo "usage: go_f20c.sh f20_v01..f20_v30"; exit 2;;
esac
NN=$((10#${T#f20_v}))
if [ $NN -gt 1 ]; then PREV=$(printf 'f20_v%02d' $((NN - 1))); else PREV=""; fi
SD=300; H=330
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F20c go_f20c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -z "$PREV" ] || [ -d $G/runs/$PREV ] || { echo "order: $PREV is not made"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$ADB" ] || [ "$WANT" = "$FS6" ] || { log "installed binary $WANT is neither adb0c82f nor FS6 9325446c - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
GS=$(python $G/guard_f20c.py scan) || { python $G/guard_f20c.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F20c HPP-561 go_f20c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f20c.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_f20c.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f20c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS=$(python $G/guard_f20c.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f20c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$WANT" ] || { OK=0; log "INSTALLED BINARY CHANGED during the tag"; }
  if [ -f $OUT/manifest_before.tsv ] && [ -n "$COPIED" ]; then
    python $G/manifest_fs4c.py $OUT/manifest_run.tsv "${MF[@]}" > $OUT/manifest_run.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_run.tsv > $OUT/manifest_cmp_run.txt 2>&1
    log "manifest of the run state (before the return): $(head -1 $OUT/manifest_run.txt | cut -c1-200); run vs before: $(head -1 $OUT/manifest_cmp_run.txt | cut -c1-200)"
  fi
  for d in $COPIED; do
    if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
    rm -rf "$LIVE" && mv "$OUT/before_$d" "$LIVE" || { OK=0; log "return of $d FAILED"; }
  done
  if [ -n "$COPIED" ]; then
    for d in $COPIED; do
      if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
      [ -d "$LIVE" ] && [ ! -e "$OUT/before_$d" ] || OK=0
    done
    [ $OK = 1 ] && log "caches, saves and GLCache returned"
  fi
  if [ -f $OUT/manifest_before.tsv ]; then
    python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
    MC=$?
    log "manifest after: $(head -1 $OUT/manifest_after.txt | cut -c1-200); cmp: $(head -1 $OUT/manifest_cmp.txt)"
    [ $MC = 0 ] || OK=0
  fi
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; log "lock released (rc $RCX)"
    if [ -e $OUT/USER_FOUND ]; then
      UF=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_f20c.py close user_found > /dev/null
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF) - block closed, interference, repeat by the same name (item 534)"
    elif [ ! -f $OUT/run.txt ]; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never started - interference, repeat by the same name (item 534)"
    fi
  else
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete, installed binary or manifest differs - the lock stays"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
for d in $DIRS GLCache; do
  if [ "$d" = "GLCache" ]; then SRC="$GLDIR"; else SRC="$EMU/$d"; fi
  [ -d "$SRC" ] || { log "$d absent - not copied (manifest line MISSING)"; continue; }
  cp -a "$SRC" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
  COPIED="$COPIED $d"
done
log "caches, saves and GLCache copied:$COPIED ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, --rec, hold $H, defaults of the installed binary $(echo $WANT | cut -c1-8))"
python $G/guard_f20c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
F20C_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --rec --hold $H KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f20c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
