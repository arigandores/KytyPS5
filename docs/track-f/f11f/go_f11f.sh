#!/bin/bash
# F11f (HPP-468, ROADMAP s122 items 376 (z), 381, 384): ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).
# usage: bash C:/kyty/f287/f11f/go_f11f.sh <tag>      tags: d11_sg d11_ef d11_vw d11_bh  (d11_sx is not assigned, item 376 (z))
# Port of C:/kyty/f287/f10e/go_f10e.sh (stop file, lock, live emulator, procload through the <app> mask, lock.log UTC, caches, _SaveData
# and GLCache copied before and returned after, the manifest sha256 of all caches before the tag and after their return with the equality
# line, RETURN_FAILED keeps the lock, the installed binary put back from its pinned copy by sha in the EXIT trap) with:
#   - the F11d copy b97efad4 (F11d HPP-466, item 381; review F11e HPP-467 PASS, item 384) installed for the tag; the binary is known ONLY
#     by the sha256 of the copy; the installed 540c035a (item 374) is checked by sha before the tag and after its return;
#   - NO cold form of the live variant: KYTY_DIAG_BVHNODES=1 adds ':diagbvh' to the translation-cache variant, so the run writes a NEW
#     directory _ShaderCache/PPSA21564/variant_*diagbvh*; it is NOT cleaned between the tags (item 376 (z)): after the tag it is moved out
#     of the live cache into $KEEP before the caches of the installed binary are returned, and before the next tag it is moved back in
#     after their copy - the manifest of the installed caches (before / after) never contains it; its own file list and sha256 manifest
#     are written after each tag (diagbvh_after.tsv);  after F11g it is compressed with xz into the manifest of the form of item 328.
#   FORM (seal docs/track-f/f11f.md section 3): enter_scene.py <tag> --level <L> --attempts 1 --stable-draws <SD> --timeout 600
#     --no-install --require-idle --gates-file gates_default.txt --pred <seal copy> --hold 330 --emu-arg=--shader-validation
#     --emu-arg=false KYTY_DIAG_BVHNODES=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0   (no video, no Vulkan validation, no input)
#     d11_sg underwater_aerial_garden SD 300; d11_ef enemy_final SD 300; d11_vw voxel_world SD 100; d11_bh big_hand_pirate_island SD 100
#   KYTY_GPU_CHECKPOINTS, KYTY_GAME_PATCH and every other KYTY_* are never passed (the env of enter_scene.py is built from the positional
#   pairs; go_f11f.sh unsets KYTY_* and VK_LAYER_* before the call).
# EXIT: 0 tag made (read it with post_f11f.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f11f; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_b97efad4.exe
BIN_EXPECT=b97efad46a27b66b9999d9b788d3cf09f2d817a29592ea73060fd91744d2a359
PINNED=C:/kyty/f287/bin/kyty_emulator_540c035a.exe
WANT=540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1
SEAL=$G/pred/f11f_seal.md
SEAL_SHA=$(cut -c1-64 $G/pred/f11f_seal.sha256 2>/dev/null)
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
SCDIR="$EMU/_ShaderCache/PPSA21564"
KEEP=$G/keep_diagbvh
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  d11_sg) LV=underwater_aerial_garden; SD=300;;
  d11_ef) LV=enemy_final; SD=300;;
  d11_vw) LV=voxel_world; SD=100;;
  d11_bh) LV=big_hand_pirate_island; SD=100;;
  *) echo "usage: go_f11f.sh <d11_sg|d11_ef|d11_vw|d11_bh>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F11f go_f11f $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ -n "$SEAL_SHA" ] && [ "$(sha $SEAL)" = "$SEAL_SHA" ] || { log "seal copy sha != pred/f11f_seal.sha256 - not starting"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "F11d copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not 540c035a before the tag - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
ls -d "$SCDIR"/variant_*diagbvh* > /dev/null 2>&1 && { log "a diagbvh variant dir is in the LIVE cache before the tag - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F11f HPP-468 go_f11f.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/lock.log
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
INSTALLED=0; COPIED=""; DIAGIN=0
finish() {
  RCX=$?
  OK=1
  tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives in finish - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
  if [ "$INSTALLED" = "1" ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$WANT" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$WANT" ]; then log "installed binary returned: $(sha "$GAME")"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
    echo "$(sha "$GAME")" > $OUT/installed_after.txt
  fi
  # the diagbvh variant dir leaves the live cache BEFORE the caches of the installed binary come back
  if [ -n "$COPIED" ]; then
    N=$(ls -d "$SCDIR"/variant_*diagbvh* 2>/dev/null | wc -l)
    if [ "$N" -gt 1 ]; then OK=0; log "more than one diagbvh variant dir in the live cache: $N"; fi
    if [ "$N" = "1" ]; then
      DV=$(ls -d "$SCDIR"/variant_*diagbvh*); B=$(basename "$DV")
      mkdir -p $KEEP && rm -rf "$KEEP/$B.prev" && { [ ! -e "$KEEP/$B" ] || mv "$KEEP/$B" "$KEEP/$B.prev"; } && mv "$DV" "$KEEP/$B" \
        && rm -rf "$KEEP/$B.prev" || { OK=0; log "move of $B out of the live cache FAILED"; }
      python $G/manifest_f11f.py $OUT/diagbvh_after.tsv "diagbvh=$KEEP/$B" > $OUT/diagbvh_after.txt 2>&1
      log "diagbvh dir $B kept in keep_diagbvh: $(head -1 $OUT/diagbvh_after.txt | cut -c1-160)"
    else
      [ "$DIAGIN" = "1" ] && { OK=0; log "the diagbvh dir put in before the tag is gone from the live cache"; }
      log "no diagbvh variant dir in the live cache after the tag"
    fi
  fi
  if [ $OK = 1 ]; then
    for d in $COPIED; do
      if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
      rm -rf "$LIVE" && mv "$OUT/before_$d" "$LIVE" || { OK=0; log "return of $d FAILED"; }
    done
  else
    log "the diagbvh step failed - caches NOT returned (the live _ShaderCache still holds the diagbvh dir); the lock stays"
  fi
  if [ -n "$COPIED" ]; then
    for d in $COPIED; do
      if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
      [ -d "$LIVE" ] && [ ! -e "$OUT/before_$d" ] || OK=0
    done
    [ $OK = 1 ] && log "caches, saves and GLCache returned"
  fi
  if [ -f $OUT/manifest_before.tsv ]; then
    python $G/manifest_f11f.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1
    python $G/manifest_f11f.py --cmp $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
    MC=$?
    log "manifest after: $(head -1 $OUT/manifest_after.txt | cut -c1-200); cmp: $(head -1 $OUT/manifest_cmp.txt)"
    [ $MC = 0 ] || OK=0
  fi
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/lock.log; log "lock released (rc $RCX)"
  else
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete or manifest differs - the lock stays"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
echo "$(sha "$GAME")" > $OUT/installed_before.txt
python $G/manifest_f11f.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
for d in $DIRS GLCache; do
  if [ "$d" = "GLCache" ]; then SRC="$GLDIR"; else SRC="$EMU/$d"; fi
  cp -a "$SRC" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
  COPIED="$COPIED $d"
done
log "caches, saves and GLCache copied: $DIRS GLCache ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
NK=$(ls -d $KEEP/variant_*diagbvh* 2>/dev/null | wc -l)
if [ "$NK" = "1" ]; then
  KD=$(ls -d $KEEP/variant_*diagbvh*); B=$(basename "$KD")
  python $G/manifest_f11f.py $OUT/diagbvh_before.tsv "diagbvh=$KD" > $OUT/diagbvh_before.txt 2>&1
  mv "$KD" "$SCDIR/$B" || { log "move of the kept $B into the live cache FAILED - not starting"; exit 1; }
  DIAGIN=1
  log "kept diagbvh dir $B moved into the live cache: $(head -1 $OUT/diagbvh_before.txt | cut -c1-160)"
elif [ "$NK" = "0" ]; then
  log "no kept diagbvh dir: the run makes it new (first tag)"
else
  log "more than one kept diagbvh dir - not starting"; exit 1
fi
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the F11d copy failed - not starting"; exit 1; }
log "installed the F11d copy: $(sha "$GAME")"
echo "$(sha "$GAME")" > $OUT/installed_sha.txt
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --hold 330 --emu-arg=--shader-validation --emu-arg=false \
  KYTY_DIAG_BVHNODES=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
log "enter_scene rc $? log_$T.txt sha256 $(sha $G/log_$T.txt)"
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
exit 0
