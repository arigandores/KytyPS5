#!/bin/bash
# Track F link F14g (HPP-507; ROADMAP s122 item 409 (g)(4)-(5), item 443 (d)): the capture f19_rd and the runs f19_v1, f19_w1, f19_ef.
# ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).  Port of C:/kyty/f287/f12f/go_f12f.sh (edition 2, 4ccfa541): stop file, lock,
# live emulator / qrenderdoc, procload through the <app> mask, lock.log UTC, caches (_ShaderCache with PPSA21564/pipelines.bin,
# _PipelineCache, _SaveData) and the driver GLCache copied before and returned after, manifest sha256 before the tag, of the run state,
# and after the return with the equality line, RETURN_FAILED keeps the lock; the FIRST tag writes the reference manifest
# runs/ref_manifest.tsv and a standing copy cache_ref/; every tag compares its manifest after the return with the reference too; a tag
# whose caches before the start differ from the reference does not start (exit 6).  Changes: EVERY tag installs the F14e copy c01bde0c
# (KYTY_FIX_F19=1) and the return is from the pinned S12 copy adb0c82f (item 443 (d)(1)); the directory
# variant_fixb26_fixb1b_fixf10_fixf19 must be absent before every tag (cold form); f19_rd moves its captures to f19_rd_kNN.rdc inside the
# lock and does NOT read them (the structured read without replay, rd_cmp_f14c.py, runs after the release in post_f14g.sh).
# usage: bash C:/kyty/f287/f14g/go_f14g.sh <f19_rd|f19_v1|f19_w1|f19_ef>
#   FORMS (seal docs/track-f/f14g.md section 3 = pred/f14g_seal.md); enter_scene.py <tag> --level <L> --attempts 1 --no-install
#   --require-idle --gates-file gates_default.txt --pred <seal> plus:
#     f19_rd: underwater_aerial_garden --stable-draws 300 --timeout 600 --emu-arg=--rd --hold 120 KYTY_FIX_F19=1
#        KYTY_RD_LEVEL=underwater_aerial_garden KYTY_RD_LEVEL_FRAME=9,300 KYTY_RD_FLIPS=2 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#        (no video, no input, no validation)
#     f19_v1: underwater_aerial_garden --stable-draws 300 --timeout 480 --rec --hold 330 KYTY_FIX_F19=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#     f19_w1: underwater_aerial_garden --stable-draws 300 --timeout 600 --emu-arg=--vulkan-validation --emu-arg=true --hold 310
#        VK_LAYER_PATH VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_FIX_F19=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#        (W of item 295 (b): precache by default, no VK_LAYER_MESSAGE_ID_FILTER, no video)
#     f19_ef: enemy_final --stable-draws 100 --timeout 480 --rec --hold 330 KYTY_FIX_F19=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#   KYTY_GPU_CHECKPOINTS, KYTY_GAME_PATCH and every other KYTY_* are never passed (enter_scene.py builds the env from the positional
#   pairs; this script unsets KYTY_* and VK_LAYER_* before the call).  ASCII only.
# EXIT: 0 tag made (read it with post_f14g.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy; 6 caches before the tag differ from the reference of the first tag.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f14g; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_c01bde0c.exe
BIN_EXPECT=c01bde0cbe61b94599b1aabdc1bcb03c883f49fe6fa8a23b161adb3f0afbe2d7
PINNED=C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe
WANT=adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421
SEAL=$G/pred/f14g_seal.md
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
FIXDIR="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19"
RDDIR="$EMU/_RenderDoc"
RDHOME="/c/Program Files/RenderDoc"
SKY=underwater_aerial_garden
NRD="9,300"
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f19_rd|f19_v1|f19_w1) LV=$SKY; SD=300;;
  f19_ef) LV=enemy_final; SD=100;;
  *) echo "usage: go_f14g.sh <f19_rd|f19_v1|f19_w1|f19_ef>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"; REF=$G/runs/ref_manifest.tsv
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F14g go_f14g $T $*" | tee -a $TIMES; }
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
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "F14e copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ -e "$FIXDIR" ] && { log "$FIXDIR exists before the tag - not starting"; exit 1; }
if [ "$T" = "f19_rd" ]; then
  [ -f "$RDHOME/qrenderdoc.exe" ] && [ -f "$RDHOME/renderdoc.dll" ] || { log "renderdoc missing - not starting"; exit 1; }
  ls $G/f19_rd_k*.rdc > /dev/null 2>&1 && { log "f19_rd captures exist - not starting"; exit 2; }
fi
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
tasklist //FI "IMAGENAME eq qrenderdoc.exe" | grep -qi qrenderdoc && { log "a qrenderdoc lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F14g HPP-507 go_f14g.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
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
echo "cold form: $FIXDIR absent at $(u); entries of _ShaderCache/PPSA21564: $(ls "$EMU/_ShaderCache/PPSA21564" | wc -l)" > $OUT/cold.txt
log "$(cat $OUT/cold.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the F14e copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the F14e copy: $(cat $OUT/installed_sha.txt)"
RDB=$(ls "$RDDIR"/*.rdc 2>/dev/null | sort | tr '\n' ';')
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
case "$T" in
  f19_rd)
    log "enter_scene start (level $LV, --rd, KYTY_RD_LEVEL_FRAME=$NRD, KYTY_RD_FLIPS=2, hold 120, KYTY_FIX_F19=1)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --emu-arg=--rd --hold 120 KYTY_FIX_F19=1 \
      KYTY_RD_LEVEL=$LV KYTY_RD_LEVEL_FRAME=$NRD KYTY_RD_FLIPS=2 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  f19_v1|f19_ef)
    log "enter_scene start (level $LV, SD $SD, --rec, hold 330, KYTY_FIX_F19=1)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_FIX_F19=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  f19_w1)
    log "enter_scene start (level $LV, W of item 295 (b), hold 310, KYTY_FIX_F19=1)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --emu-arg=--vulkan-validation --emu-arg=true --hold 310 \
      VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_FIX_F19=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
esac
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
if [ "$T" = "f19_rd" ]; then
  NEW=$(ls -tr "$RDDIR"/*.rdc 2>/dev/null | while read -r X; do case ";$RDB" in *";$X;"*) ;; *) echo "$X";; esac; done)
  NNEW=$(printf '%s\n' "$NEW" | grep -c . )
  log "new captures in _RenderDoc: $NNEW"
  K=0
  printf '%s\n' "$NEW" | grep . > $OUT/new_captures.txt
  while read -r X; do
    K=$((K+1)); KK=$(printf '%02d' $K)
    CAPF=$G/f19_rd_k$KK.rdc
    mv "$X" "$CAPF" || { log "move of $(basename "$X") failed"; continue; }
    log "capture k$KK $(basename "$X") moved to $(basename $CAPF) bytes $(stat -c %s "$CAPF")"
  done < $OUT/new_captures.txt
  for C in $G/f19_rd_k*.rdc; do [ -f "$C" ] && echo "$(sha "$C")  $(basename $C)"; done > $OUT/rdc_sha.txt
  log "capture sha256 list runs/f19_rd/rdc_sha.txt lines $(wc -l < $OUT/rdc_sha.txt)"
fi
exit 0
