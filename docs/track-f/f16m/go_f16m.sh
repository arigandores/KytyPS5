#!/bin/bash
# Track F link F16m (HPP-585; ROADMAP s122 items 492 (e)-(zh), 495 (g), 496 (b)(3)-(5), 500 (b), 501 (b)-(v)): the pair of witness f5cmu_0 /
# f5cmu_1 and the diagnostic tags f5id_* on the F16k2 test binary d4328b0c (code ed4f96d8, accepted by F16l2, item 501; a copy by sha256
# before each tag, item 501 (b)(4)).  ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).  Port of C:/kyty/f287/f16f/go_f16f.sh (F16f
# HPP-523): stop file, lock, live emulator, procload through the <app> mask, lock.log UTC, caches (_ShaderCache with PPSA21564/pipelines.bin,
# _PipelineCache, _SaveData) and the driver GLCache copied before and returned after, manifest sha256 before the tag, of the run state (after
# the tag, before the return) and after the return with the equality line; RETURN_FAILED keeps the lock.  The installed S12 adb0c82f (items
# 437-438) is checked before the tag, written inside the lock (installed_before.txt) and after the return from its pinned copy
# (installed_after.txt).  The F16k2 copy is installed for the tag only, known by sha256.  The test binary is built from main (ed4f96d8):
# its source hash a54ae4bd differs from the installed S12 (the string is absent from adb0c82f) - the translation of the tag is cold by
# signature on the same variant directory variant_fixb26_fixb1b_fixf10 (its presence is written to warm.txt, a reference); frames >= 1 s
# and K2 on the entry are REPORT rows (interference of a cold entry, item 427 (zh)), not members.  Nothing is removed by this script.
# The seal copy pred/f16m_seal.md is checked by its sha256 (pred/f16m_seal.sha256) before the tag.
# usage: bash C:/kyty/f287/f16m/go_f16m.sh <f5cmu_0|f5cmu_1|f5id_sg|f5id_ef|f5id_bh|f5id_eb>
#   FORMS (seal docs/track-f/f16m.md section 3 = pred/f16m_seal.md):
#   pair (form V of track F: -lvl entry, hold, video, no Vulkan validation, no input; item 492 (e)(1)):
#     enter_scene.py <tag> --level enemy_final --attempts 1 --stable-draws 300 --timeout 600 --no-install --require-idle
#       --gates-file gates_default.txt --pred <seal> --rec --hold 330 KYTY_DIAG_F5=1 KYTY_FIX_F5CMU=<0|1> KYTY_GPU_CLOCK_PIN=1
#       KYTY_GPU_MARKERS=0
#   id (form F16f: -lvl entry, hold, no video, no Vulkan validation; item 492 (zh)):
#     enter_scene.py <tag> --level <L> --attempts 1 --stable-draws <SD> --timeout 600 --no-install --require-idle
#       --gates-file gates_default.txt --pred <seal> --hold 330 --emu-arg=--shader-validation --emu-arg=false
#       KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#     f5id_sg underwater_aerial_garden SD 300; f5id_ef enemy_final SD 300; f5id_bh big_hand_pirate_island SD 100;
#     f5id_eb ending_boss_after_credit SD 300
#   Every other KYTY_* (defaults of the binary), KYTY_GAME_PATCH and KYTY_GPU_CHECKPOINTS are never passed (enter_scene.py builds the env
#   from the positional pairs; this script unsets KYTY_* and VK_LAYER_* before the call).  ASCII only.
# EXIT: 0 tag made (read it with post_f16m.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f16m; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_d4328b0c.exe
BIN_EXPECT=d4328b0c8053d7deae0ef34691462af3e244dd3a6be07722146505b642ca203c
PINNED=C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe
WANT=adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421
SEAL=$G/pred/f16m_seal.md
SEAL_SHA=$(cut -c1-64 $G/pred/f16m_seal.sha256 2>/dev/null)
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
FIXDIR="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10"
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
REC=""; VAL=""
case "$T" in
  f5cmu_0) LV=enemy_final; SD=300; PAIRS="KYTY_DIAG_F5=1 KYTY_FIX_F5CMU=0"; REC="--rec";;
  f5cmu_1) LV=enemy_final; SD=300; PAIRS="KYTY_DIAG_F5=1 KYTY_FIX_F5CMU=1"; REC="--rec";;
  f5id_sg) LV=underwater_aerial_garden; SD=300; PAIRS="KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1"; VAL=1;;
  f5id_ef) LV=enemy_final; SD=300; PAIRS="KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1"; VAL=1;;
  f5id_bh) LV=big_hand_pirate_island; SD=100; PAIRS="KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1"; VAL=1;;
  f5id_eb) LV=ending_boss_after_credit; SD=300; PAIRS="KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1"; VAL=1;;
  *) echo "usage: go_f16m.sh <f5cmu_0|f5cmu_1|f5id_sg|f5id_ef|f5id_bh|f5id_eb>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F16m go_f16m $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ -n "$SEAL_SHA" ] && [ "$(sha $SEAL)" = "$SEAL_SHA" ] || { log "seal copy sha != pred/f16m_seal.sha256 - not starting"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not adb0c82f before the tag - not starting (question to the lead)"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "F16k2 copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F16m HPP-585 go_f16m.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
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
echo "variant form: $FIXDIR $W at $(u); entries of _ShaderCache/PPSA21564: $(ls "$EMU/_ShaderCache/PPSA21564" | wc -l); source hash of the tag binary a54ae4bd != installed (cold by signature, reference)" > $OUT/warm.txt
log "$(cat $OUT/warm.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the F16k2 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the F16k2 copy: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, hold 330, ${REC:-no video}, pairs: $PAIRS KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0)"
if [ -n "$VAL" ]; then
  python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
    --gates-file $G/gates_default.txt --pred $SEAL --hold 330 --emu-arg=--shader-validation --emu-arg=false \
    $PAIRS KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
else
  python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
    --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 $PAIRS KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
fi
log "enter_scene rc $?"
log "run: $(grep '^close: ' $OUT/run.txt | tail -1 | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
