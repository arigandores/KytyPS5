#!/bin/bash
# Track F link F15e (HPP-516; ROADMAP s122 item 412 (g)(5), item 445 (g)): the tag b4_v of the F15c binary 907569f6 (= S12a 4d9e8ab7 +
# a86a5ad0) at KYTY_FIX_B4=1.  ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).  Port of C:/kyty/f287/fs5/fs5c/go_fs5c.sh (FS5c
# HPP-511) for one tag: stop file, lock, live emulator, procload through the <app> mask, lock.log UTC, caches (_ShaderCache with
# PPSA21564/pipelines.bin, _PipelineCache, _SaveData) and the driver GLCache copied before and returned after, manifest sha256 before the
# tag, of the run state (after the tag, before the return - the _SaveData row of item 412 (g)(5) reads it) and after the return with the
# equality line; RETURN_FAILED keeps the lock.  No reference copy cache_ref (RC6 of FS5c was for a series; here one tag, the return is
# proven by cmp before/after).  The installed S12 adb0c82f (items 437-438, 445 (g)) is checked before the tag, written inside the lock
# (installed_before.txt) and after the return from its pinned copy (installed_after.txt).  The F15c copy 907569f6 is installed for the tag
# only, known by sha256 (and the version string of the binary - the reader, item 445 (v) N1).  The translation signature of the tag
# binary = the installed one (26ce5fc7, F15d section 1): the directory variant_fixb26_fixb1b_fixf10 is warm; its presence is written to
# warm.txt (a reference, not a refusal).  Nothing is removed by this script.
# usage: bash C:/kyty/f287/f15e/go_f15e.sh b4_v
#   FORM (seal docs/track-f/f15e.md section 3 = pred/f15e_seal.md): enter_scene.py b4_v --level underwater_aerial_garden --attempts 1
#     --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 330
#     KYTY_FIX_B4=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#   Every other KYTY_FIX_* (defaults of the binary), KYTY_GAME_PATCH and KYTY_GPU_CHECKPOINTS are never passed (enter_scene.py builds the
#   env from the positional pairs; this script unsets KYTY_* and VK_LAYER_* before the call).  The exit: enter_scene posts WM_CLOSE at
#   the end of the hold (log 'Event: quit') and waits CLOSE_WAIT_S = 40 s (the harness timeout of the exit), else kills; the attempt
#   record carries close_rc / close_killed / close_s.  ASCII only.
# EXIT: 0 tag made (read it with post_f15e.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f15e; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_907569f6.exe
BIN_EXPECT=907569f641bfea9fb9881213b77588a2c8365a084512e5ef734baf5aae82aff1
PINNED=C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe
WANT=adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421
SEAL=$G/pred/f15e_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
FIXDIR="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10"
SKY=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  b4_v) LV=$SKY;;
  *) echo "usage: go_f15e.sh b4_v"; exit 2;;
esac
SD=300
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F15e go_f15e $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not adb0c82f before the tag - not starting"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "F15c copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F15e HPP-516 go_f15e.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
INSTALLED=0; COPIED=""
finish() {
  RCX=$?
  OK=1
  if tasklist //FI "IMAGENAME eq kyty_emulator.exe" 2>/dev/null | grep -qi kyty_emulator; then
    taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; log "kyty_emulator.exe killed at the exit (taskkill)"; sleep 5
  fi
  if [ "$INSTALLED" = "1" ] || [ "$(sha "$GAME")" != "$WANT" ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$WANT" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$WANT" ]; then log "installed binary returned from the pinned copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$WANT" ] || OK=0
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
if [ -d "$FIXDIR" ]; then W=present; else W=absent; fi
echo "warm form: $FIXDIR $W at $(u); entries of _ShaderCache/PPSA21564: $(ls "$EMU/_ShaderCache/PPSA21564" | wc -l)" > $OUT/warm.txt
log "$(cat $OUT/warm.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the F15c copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the F15c copy: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, --rec, hold 330, KYTY_FIX_B4=1, other defaults of the binary)"
python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_FIX_B4=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
log "enter_scene rc $?"
log "run: $(grep '^close: ' $OUT/run.txt | tail -1 | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
