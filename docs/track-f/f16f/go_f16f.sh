#!/bin/bash
# Track F link F16f (HPP-523; ROADMAP s122 items 421 (g), 427, 433 (v)-(g), 458, 470 (g), 480, 482): the tags of the diagnostics KYTY_DIAG_F5
# / KYTY_DIAG_F6 on the F16d2 binary 4ad735ad (= FS6a 3904522d + 381aa80a + 56b04817, worktree 4950557a; item 482: a copy by sha256 before
# each tag).  ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).  Port of C:/kyty/f287/fs6c/go_fs6c.sh (FS6c HPP-557): stop file, FS6b
# window file (item 473 (b)(2), items 477, 481), lock, live emulator, procload through the <app> mask, lock.log UTC, caches (_ShaderCache
# with PPSA21564/pipelines.bin, _PipelineCache, _SaveData) and the driver GLCache copied before and returned after, manifest sha256 before
# the tag, of the run state (after the tag, before the return) and after the return with the equality line; RETURN_FAILED keeps the lock.
# The installed S12 adb0c82f (items 437-438) is checked before the tag, written inside the lock (installed_before.txt) and after the
# return from its pinned copy (installed_after.txt).  The F16d2 copy is installed for the tag only, known by sha256 (and the version string,
# read by the reader).  The diagnostics sit outside the translation signature set (items 427 (zh) RC11, 480 (a)(6)): signature 26ce5fc7 =
# the installed one, the directory variant_fixb26_fixb1b_fixf10 is warm - its presence is written to warm.txt (a reference).
# Nothing is removed by this script.  The seal copy pred/f16f_seal.md is checked by its sha256 (pred/f16f_seal.sha256) before the tag.
# usage: bash C:/kyty/f287/f16f/go_f16f.sh <f5_sg|f5_ef|f5_bh|f5_eb|f5_sg0>
#   FORM (seal docs/track-f/f16f.md section 3 = pred/f16f_seal.md; form d11_* of F11f: -lvl entry, no video, no Vulkan validation, no
#   input): enter_scene.py <tag> --level <L> --attempts 1 --stable-draws <SD> --timeout 600 --no-install --require-idle
#     --gates-file gates_default.txt --pred <seal> --hold <H> --emu-arg=--shader-validation --emu-arg=false <pairs>
#     f5_sg  underwater_aerial_garden SD 300 H 330  KYTY_DIAG_F5=1 KYTY_DIAG_F6=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#     f5_ef  enemy_final              SD 300 H 330  (same pairs)
#     f5_bh  big_hand_pirate_island   SD 100 H 330  (same pairs)
#     f5_eb  ending_boss_after_credit SD 300 H 330  (same pairs)
#     f5_sg0 underwater_aerial_garden SD 300 H 90   KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0   (null control: neither knob)
#   KYTY_FIX_*, KYTY_GAME_PATCH and KYTY_GPU_CHECKPOINTS are never passed (enter_scene.py builds the env from the positional pairs; this
#   script unsets KYTY_* and VK_LAYER_* before the call).  ASCII only.
# EXIT: 0 tag made (read it with post_f16f.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy; 6 FS6b window file younger than 900 s (item 473 (b)(2)).
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f16f; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_4ad735ad.exe
BIN_EXPECT=4ad735ad70b7504df85560dc6b6c2e3520f0256aa655a4ff4db03f71122b09f6
PINNED=C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe
WANT=adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421
SEAL=$G/pred/f16f_seal.md
SEAL_SHA=$(cut -c1-64 $G/pred/f16f_seal.sha256 2>/dev/null)
WINF=$F/FS6B_WINDOW
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
FIXDIR="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10"
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
DIAG="KYTY_DIAG_F5=1 KYTY_DIAG_F6=1"
case "$T" in
  f5_sg) LV=underwater_aerial_garden; SD=300; H=330;;
  f5_ef) LV=enemy_final; SD=300; H=330;;
  f5_bh) LV=big_hand_pirate_island; SD=100; H=330;;
  f5_eb) LV=ending_boss_after_credit; SD=300; H=330;;
  f5_sg0) LV=underwater_aerial_garden; SD=300; H=90; DIAG="";;
  *) echo "usage: go_f16f.sh <f5_sg|f5_ef|f5_bh|f5_eb|f5_sg0>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F16f go_f16f $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
if [ -e $WINF ]; then
  AGE=$(( $(date +%s) - $(stat -c %Y $WINF) ))
  if [ $AGE -lt 900 ]; then log "FS6B_WINDOW age ${AGE} s < 900 s - tag not launched (item 473 (b)(2))"; exit 6; fi
  log "FS6B_WINDOW age ${AGE} s >= 900 s - the window expired, the tag goes (file not removed)"
fi
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ -n "$SEAL_SHA" ] && [ "$(sha $SEAL)" = "$SEAL_SHA" ] || { log "seal copy sha != pred/f16f_seal.sha256 - not starting"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not adb0c82f before the tag - not starting (question to the lead)"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "F16d2 copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F16f HPP-523 go_f16f.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
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
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the F16d2 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the F16d2 copy: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, hold $H, pairs: ${DIAG:-none} KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0)"
python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --hold $H --emu-arg=--shader-validation --emu-arg=false \
  $DIAG KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
log "enter_scene rc $?"
log "run: $(grep '^close: ' $OUT/run.txt | tail -1 | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
