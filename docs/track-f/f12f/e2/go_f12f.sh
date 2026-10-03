#!/bin/bash
# Track F link F12f (HPP-480; ROADMAP s122 item 391 (g)(4)-(5), item 393 (v)): the capture f12_rd and the runs f12_v, f12_w, f12_vw,
# f12_bh.  ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).  Port of C:/kyty/f287/f13a/go_f13a.sh (capture, no install) and of
# C:/kyty/f287/fs4c/go_fs4c.sh (install of a pinned copy by sha256, return from the pinned 540c035a in the EXIT trap): stop file, lock,
# live emulator / qrenderdoc, procload through the <app> mask, lock.log UTC, caches (_ShaderCache with PPSA21564/pipelines.bin,
# _PipelineCache, _SaveData) and the driver GLCache copied before and returned after, manifest sha256 before the tag, of the run state,
# and after the return with the equality line, RETURN_FAILED keeps the lock.  RC6 (item 391 (g)(5)): the FIRST tag also writes the
# reference manifest runs/ref_manifest.tsv and a standing copy cache_ref/ of the caches; every tag compares its manifest after the
# return with the reference too (manifest_cmp_ref.txt); the installed sha256 is written before (installed_before.txt) and after the
# return (installed_after.txt) of every tag.
# usage: bash C:/kyty/f287/f12f/go_f12f.sh <f12_rd|f12_v|f12_w|f12_vw|f12_bh>
#   FORMS (seal docs/track-f/f12f.md section 3 = pred/f12f_seal.md):
#     f12_rd: NO install - the installed 540c035a; enter_scene.py <tag> --level underwater_aerial_garden --attempts 1 --stable-draws 300
#        --timeout 600 --no-install --require-idle --gates-file gates_default.txt --pred <seal> --emu-arg=--rd --hold 120
#        KYTY_RD_LEVEL=underwater_aerial_garden KYTY_RD_LEVEL_FRAME=<NRD> KYTY_RD_FLIPS=2 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#        (no video, no input, no validation); after the run, inside the lock: every new capture moved to f12_rd_kNN.rdc (oldest first)
#        and read by rdcs_f12f.sh (CS SPIR-V sha256 of every dispatch, mark of the =0 SPIR-V of 380bb9d636390bae, data only)
#     f12_v / f12_vw / f12_bh: the F12d copy b714f5c4 installed; enter_scene.py <tag> --level <L> --attempts 1 --stable-draws <SD>
#        --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 330 KYTY_FIX_F10=1
#        KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0; f12_v underwater_aerial_garden SD 300, f12_vw voxel_world SD 100, f12_bh
#        big_hand_pirate_island SD 100
#     f12_w: the F12d copy b714f5c4 installed; enter_scene.py <tag> --level underwater_aerial_garden --attempts 1 --stable-draws 300
#        --timeout 600 --no-install --require-idle --gates-file gates_default.txt --pred <seal> --emu-arg=--vulkan-validation
#        --emu-arg=true --hold 310 VK_LAYER_PATH VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_FIX_F10=1 KYTY_GPU_CLOCK_PIN=1
#        KYTY_GPU_MARKERS=0 (W of item 295 (b): precache by default, no VK_LAYER_MESSAGE_ID_FILTER, no video)
#   The binary of the fix runs ONLY with KYTY_FIX_F10=1 (item 391 (g)(5)).  KYTY_GPU_CHECKPOINTS, KYTY_GAME_PATCH and every other KYTY_*
#   are never passed (enter_scene.py builds the env from the positional pairs; this script unsets KYTY_* and VK_LAYER_* before the call).
#   ASCII only.
# EXIT: 0 tag made (read it with f12f_read.py); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy; 6 caches before the tag differ from the reference of the first tag (edition 2, seal section 8).
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f12f; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_b714f5c4.exe
BIN_EXPECT=b714f5c4af578928243c1f1028e7b2acd65b733fce90f2e3cda5b6ae46d5eb5e
PINNED=C:/kyty/f287/bin/kyty_emulator_540c035a.exe
WANT=540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1
SEAL=$G/pred/f12f_seal.md
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
FIXDIR="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10"
RDDIR="$EMU/_RenderDoc"
RDHOME="/c/Program Files/RenderDoc"
SKY=underwater_aerial_garden
NRD="3,6,9,12,15,18,21,24,27,33,40,50"
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f12_rd) LV=$SKY; SD=300;;
  f12_v|f12_w) LV=$SKY; SD=300;;
  f12_vw) LV=voxel_world; SD=100;;
  f12_bh) LV=big_hand_pirate_island; SD=100;;
  *) echo "usage: go_f12f.sh <f12_rd|f12_v|f12_w|f12_vw|f12_bh>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"; REF=$G/runs/ref_manifest.tsv
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F12f go_f12f $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not 540c035a before the tag - not starting"; exit 1; }
if [ "$T" != "f12_rd" ]; then
  [ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "F12d copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
  [ -e "$FIXDIR" ] && { log "$FIXDIR exists before the tag - not starting"; exit 1; }
else
  [ -f "$RDHOME/qrenderdoc.exe" ] && [ -f "$RDHOME/renderdoc.dll" ] || { log "renderdoc missing - not starting"; exit 1; }
  [ -f $G/rd_cs_f12f.py ] && [ -f $G/rdcs_f12f.sh ] || { log "rd_cs_f12f.py / rdcs_f12f.sh missing - not starting"; exit 1; }
  ls $G/f12_rd_k*.rdc > /dev/null 2>&1 && { log "f12_rd captures exist - not starting"; exit 2; }
fi
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
tasklist //FI "IMAGENAME eq qrenderdoc.exe" | grep -qi qrenderdoc && { log "a qrenderdoc lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F12f HPP-480 go_f12f.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
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
  if tasklist //FI "IMAGENAME eq qrenderdoc.exe" 2>/dev/null | grep -qi qrenderdoc; then
    taskkill //F //IM qrenderdoc.exe > /dev/null 2>&1; log "qrenderdoc.exe killed at the exit (taskkill)"; sleep 3
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
if [ "$T" != "f12_rd" ]; then
  echo "cold form: $FIXDIR absent at $(u); entries of _ShaderCache/PPSA21564: $(ls "$EMU/_ShaderCache/PPSA21564" | wc -l)" > $OUT/cold.txt
  log "$(cat $OUT/cold.txt)"
  INSTALLED=1
  cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the F12d copy failed - not starting"; exit 1; }
  sha "$GAME" > $OUT/installed_sha.txt
  log "installed the F12d copy: $(cat $OUT/installed_sha.txt)"
else
  sha "$GAME" > $OUT/installed_sha.txt
  echo "installed form: $(ls "$EMU/_ShaderCache/PPSA21564" | grep variant | tr '\n' ' ')" > $OUT/cold.txt
fi
RDB=$(ls "$RDDIR"/*.rdc 2>/dev/null | sort | tr '\n' ';')
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
case "$T" in
  f12_rd)
    log "enter_scene start (level $LV, --rd, KYTY_RD_LEVEL_FRAME=$NRD, KYTY_RD_FLIPS=2, hold 120)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --emu-arg=--rd --hold 120 \
      KYTY_RD_LEVEL=$LV KYTY_RD_LEVEL_FRAME=$NRD KYTY_RD_FLIPS=2 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  f12_v|f12_vw|f12_bh)
    log "enter_scene start (level $LV, SD $SD, --rec, hold 330, KYTY_FIX_F10=1)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_FIX_F10=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  f12_w)
    log "enter_scene start (level $LV, W of item 295 (b), hold 310, KYTY_FIX_F10=1)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --emu-arg=--vulkan-validation --emu-arg=true --hold 310 \
      VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_FIX_F10=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
esac
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
if [ "$T" = "f12_rd" ]; then
  NEW=$(ls -tr "$RDDIR"/*.rdc 2>/dev/null | while read -r X; do case ";$RDB" in *";$X;"*) ;; *) echo "$X";; esac; done)
  NNEW=$(printf '%s\n' "$NEW" | grep -c . )
  log "new captures in _RenderDoc: $NNEW"
  K=0
  printf '%s\n' "$NEW" | grep . > $OUT/new_captures.txt
  while read -r X; do
    K=$((K+1)); KK=$(printf '%02d' $K)
    CAPF=$G/f12_rd_k$KK.rdc
    mv "$X" "$CAPF" || { log "move of $(basename "$X") failed"; continue; }
    log "capture k$KK $(basename "$X") moved to $(basename $CAPF) bytes $(stat -c %s "$CAPF")"
    [ -e $F/STOP ] && { log "STOP file before the read of k$KK: $(head -1 $F/STOP)"; break; }
    bash $G/rdcs_f12f.sh "C:/kyty/f287/f12f/f12_rd_k$KK.rdc" "$G/rdcs_f12_rd_k$KK.txt" 900 > $OUT/rdcs_k$KK.out.txt 2>&1
    log "rdcs k$KK rc $?: $(grep '^SUMMARY' $G/rdcs_f12_rd_k$KK.txt 2>/dev/null | cut -c1-200)"
  done < $OUT/new_captures.txt
  for C in $G/f12_rd_k*.rdc; do echo "$(sha "$C")  $(basename $C)"; done > $OUT/rdc_sha.txt
  log "capture sha256 list runs/f12_rd/rdc_sha.txt lines $(wc -l < $OUT/rdc_sha.txt)"
fi
exit 0
