#!/bin/bash
# Track F link FS5c (HPP-511; ROADMAP s122 item 410 (g)(3), item 418): the tags fs5_v, fs5_w, fs5_r1 and the reference fs5_hb of the FS5
# binary 631ff987.  ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).  Port of C:/kyty/f287/f12f/go_f12f.sh (F12f HPP-480, edition 2
# 4ccfa541) without the RenderDoc tag: stop file, lock, live emulator, procload through the <app> mask, lock.log UTC, caches (_ShaderCache
# with PPSA21564/pipelines.bin, _PipelineCache, _SaveData) and the driver GLCache copied before and returned after, manifest sha256 before
# the tag, of the run state, and after the return with the equality line, RETURN_FAILED keeps the lock.  RC6 (item 391 (g)(5)): the FIRST
# tag also writes the reference manifest runs/ref_manifest.tsv and a standing copy cache_ref/ of the caches; every tag compares its
# manifest after the return with the reference too (manifest_cmp_ref.txt), and does not start (exit 6) when its caches before differ from
# the reference.  The installed FS4 31cbfee8 (item 407) is checked before the tag, written inside the lock (installed_before.txt) and after
# the return from its pinned copy (installed_after.txt).  The FS5 copy 631ff987 is installed for the tag only, known only by sha256.
# The cold form: variant_fixb26_fixb1b_fixf10 must be absent before the tag (the caches of the tag before are returned, so every tag is a
# cold entry into the new directory); nothing is removed by this script.
# usage: bash C:/kyty/f287/fs5/fs5c/go_fs5c.sh <fs5_v|fs5_w|fs5_r1|fs5_hb>
#   FORMS (seal docs/track-f/fs5c.md section 3 = pred/fs5c_seal.md), every one: enter_scene.py <tag> --level <L> --attempts 1
#     --no-install --require-idle --gates-file gates_default.txt --pred <seal> + :
#     fs5_v:  underwater_aerial_garden --stable-draws 300 --timeout 480 --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#     fs5_w:  underwater_aerial_garden --stable-draws 300 --timeout 600 --emu-arg=--vulkan-validation --emu-arg=true --hold 310
#             VK_LAYER_PATH VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (W of item 295 (b):
#             precache by default, no VK_LAYER_MESSAGE_ID_FILTER, no video)
#     fs5_r1: underwater_aerial_garden --stable-draws 300 --timeout 480 --rec --hold 330 --emu-arg=--shader-validation --emu-arg=true
#             KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (form fs4_r1 of FS4c, item 378 (g)(3))
#     fs5_hb: hoover_beach --stable-draws 300 --timeout 480 --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (reference)
#   The defaults of FS5: KYTY_FIX_F10, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS and every other KYTY_FIX_* / KYTY_* are never passed
#   (enter_scene.py builds the env from the positional pairs; this script unsets KYTY_* and VK_LAYER_* before the call).  ASCII only.
# EXIT: 0 tag made (read it with post_fs5c.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy; 6 caches before the tag differ from the reference of the first tag.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/fs5/fs5c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_631ff987.exe
BIN_EXPECT=631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17
PINNED=C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe
WANT=31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5
SEAL=$G/pred/fs5c_seal.md
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
FIXDIR="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10"
SKY=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  fs5_v|fs5_w|fs5_r1) LV=$SKY;;
  fs5_hb) LV=hoover_beach;;
  *) echo "usage: go_fs5c.sh <fs5_v|fs5_w|fs5_r1|fs5_hb>"; exit 2;;
esac
SD=300
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"; REF=$G/runs/ref_manifest.tsv
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) FS5c go_fs5c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not 31cbfee8 before the tag - not starting"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "FS5 copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ -e "$FIXDIR" ] && { log "$FIXDIR exists before the tag - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "FS5c HPP-511 go_fs5c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/lock.log
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
INSTALLED=0; COPIED=""; REFOK=1
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
    python $G/manifest_fs4c.py --cmp $REF $OUT/manifest_after.tsv > $OUT/manifest_cmp_ref.txt 2>&1
    MR=$?
    log "manifest after: $(head -1 $OUT/manifest_after.txt | cut -c1-200); cmp: $(head -1 $OUT/manifest_cmp.txt); cmp with the reference of the first tag: $(head -1 $OUT/manifest_cmp_ref.txt)"
    [ $MC = 0 ] || OK=0
    [ $MR = 0 ] || [ "$REFOK" != "1" ] || OK=0
  fi
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/lock.log; log "lock released (rc $RCX)"
  else
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete, installed binary or manifest differs - the lock stays"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
if [ ! -f $REF ]; then
  cp $OUT/manifest_before.tsv $REF && cp $OUT/manifest_before.txt $G/runs/ref_manifest.txt
  log "reference manifest of the first tag written: runs/ref_manifest.tsv sha256 $(sha $REF)"
  mkdir -p $G/cache_ref
  cp -a "$EMU/_ShaderCache/PPSA21564" $G/cache_ref/ShaderCache_PPSA21564 && cp -a "$EMU/_PipelineCache" $G/cache_ref/PipelineCache \
    && cp -a "$GLDIR" $G/cache_ref/GLCache || { log "standing copy cache_ref failed - not starting"; exit 1; }
  log "standing copy cache_ref/ made ($(du -sm $G/cache_ref | cut -f1) MB)"
fi
python $G/manifest_fs4c.py --cmp $REF $OUT/manifest_before.tsv > $OUT/manifest_cmp_ref_before.txt 2>&1
log "before vs reference: $(head -1 $OUT/manifest_cmp_ref_before.txt)"
if ! head -1 $OUT/manifest_cmp_ref_before.txt | grep -q '^manifest cmp EQUAL'; then
  REFOK=0; log "caches before the tag differ from the reference - not starting (exit 6)"; exit 6
fi
for d in $DIRS GLCache; do
  if [ "$d" = "GLCache" ]; then SRC="$GLDIR"; else SRC="$EMU/$d"; fi
  [ -d "$SRC" ] || { log "$d absent - not copied (manifest line MISSING)"; continue; }
  cp -a "$SRC" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
  COPIED="$COPIED $d"
done
log "caches, saves and GLCache copied:$COPIED ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
ls "$EMU/_ShaderCache/PPSA21564" > $OUT/variant_dirs.txt 2>&1
echo "cold form: $FIXDIR absent at $(u); entries of _ShaderCache/PPSA21564: $(ls "$EMU/_ShaderCache/PPSA21564" | wc -l)" > $OUT/cold.txt
log "$(cat $OUT/cold.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the FS5 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the FS5 copy: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
case "$T" in
  fs5_v|fs5_hb)
    log "enter_scene start (level $LV, SD $SD, --rec, hold 330, defaults of FS5)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  fs5_w)
    log "enter_scene start (level $LV, W of item 295 (b), hold 310, defaults of FS5)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --emu-arg=--vulkan-validation --emu-arg=true --hold 310 \
      VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  fs5_r1)
    log "enter_scene start (level $LV, form fs4_r1: --shader-validation true, --rec, hold 330, defaults of FS5)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 --emu-arg=--shader-validation --emu-arg=true \
      KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
esac
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
