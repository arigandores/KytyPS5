#!/bin/bash
# FS4c (HPP-472, ROADMAP s122 item 378 (g)(3); item 383 (c) = Z2 of FS4b): ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).
# usage: bash C:/kyty/f287/fs4c/go_fs4c.sh <tag>      tags: fs4_r0 fs4_r1 fs4_hb fs4_w fs4_v, the one repeat of item 378 (g)(3) fs4_r0r
# Port of C:/kyty/f287/f10e/go_f10e.sh (F10e HPP-453: stop file, lock, live emulator, procload through the <app> mask, lock.log UTC,
# caches, _SaveData and GLCache copied before and returned after, the manifest sha256 of all caches before the tag and after their
# return with the equality line, RETURN_FAILED keeps the lock, the installed 540c035a put back from its pinned copy by sha in the EXIT
# trap, the COLD FORM of the translation - the live variant directory _ShaderCache/PPSA21564/variant_fixb26_fixb1b removed after the
# copy and before the start) with: the FS4 copy 31cbfee8 (FS4a HPP-470, review FS4b HPP-471 PASS, item 383) installed; the binary is
# known ONLY by the sha256 of the copy (and the KYTY_GIT_REVISION text, where the log has it - a reader row); the cold form in fs4_r0,
# fs4_r0r, fs4_r1, fs4_hb (each its own removal - the caches of the tag before are returned, so fs4_r0 runs on a new translation in any
# order, Z2); the WARM form in fs4_w, fs4_v (the variant dir must exist, nothing removed, cold.txt says 'warm form ... present').
# KYTY_FIX_SVAL is passed ONLY in fs4_r0 / fs4_r0r (=0); the other tags run the FS4 default.  ASCII only.
#   FORMS (seal docs/track-f/fs4c.md section 3):
#     fs4_r0 (fs4_r0r): run_fs4c.py 300 s --sval, KYTY_GUEST_ARGS=-lvl underwater_aerial_garden, KYTY_FIX_SVAL=0, KYTY_FRAME_TRACE=lite,
#        KYTY_GPU_CLOCK_PIN=1, no video, no input, no Vulkan validation (form R0 of F10e)
#     fs4_r1: enter_scene.py --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle
#        --gates-file gates_default.txt --pred <seal> --rec --hold 330 --emu-arg=--shader-validation --emu-arg=true KYTY_GPU_CLOCK_PIN=1
#        KYTY_GPU_MARKERS=0 (form R1 of F10e without KYTY_FIX_SVAL)
#     fs4_hb: the same with --level hoover_beach (reference, not a gate)
#     fs4_w: enter_scene.py --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 600 --no-install --require-idle
#        --gates-file gates_default.txt --pred <seal> --emu-arg=--vulkan-validation --emu-arg=true --hold 310 VK_LAYER_PATH
#        VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (W of item 295 (b) = fs3_w of FS3c: the harness
#        --shader-validation false, warm, no VK_LAYER_MESSAGE_ID_FILTER, precache by default, no video)
#     fs4_v: enter_scene.py --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle
#        --gates-file gates_default.txt --pred <seal> --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (V of the SCENE_OK form =
#        fs3_v of FS3c, warm)
#   KYTY_GPU_CHECKPOINTS, KYTY_GAME_PATCH and every other KYTY_* are never passed (the env of run_fs4c.py and enter_scene.py is built from
#   the positional pairs; go_fs4c.sh unsets KYTY_* and VK_LAYER_* before the call).
# EXIT: 0 tag made (read it with fs4c_read.py); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/fs4c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe
BIN_EXPECT=31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5
PINNED=C:/kyty/f287/bin/kyty_emulator_540c035a.exe
WANT=540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1
SEAL=$G/pred/fs4c_seal.md
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
COLD="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b"
# nvidia-smi of enter_scene.py needs these in the env (platform trap 7; form of go_fs3.sh)
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  fs4_r0|fs4_r0r|fs4_r1|fs4_hb) FORM=cold;;
  fs4_w|fs4_v) FORM=warm;;
  *) echo "usage: go_fs4c.sh <fs4_r0|fs4_r1|fs4_hb|fs4_w|fs4_v|fs4_r0r>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) FS4c go_fs4c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
# the cache dirs of the manifest as an array (the emulator path has a space; F10e seal edition 3)
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "FS4 copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not 540c035a before the tag - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
[ -d "$COLD" ] || { log "no live variant dir $COLD - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "FS4c HPP-472 go_fs4c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/lock.log
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
INSTALLED=0; COPIED=""
finish() {
  RCX=$?
  OK=1
  if [ "$INSTALLED" = "1" ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$WANT" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$WANT" ]; then log "installed binary returned: $(sha "$GAME")"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
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
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/lock.log; log "lock released (rc $RCX)"
  else
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete or manifest differs - the lock stays"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
for d in $DIRS GLCache; do
  if [ "$d" = "GLCache" ]; then SRC="$GLDIR"; else SRC="$EMU/$d"; fi
  cp -a "$SRC" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
  COPIED="$COPIED $d"
done
log "caches, saves and GLCache copied: $DIRS GLCache ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
if [ "$FORM" = "cold" ]; then
  rm -rf "$COLD"
  if [ -e "$COLD" ]; then log "cold form FAILED: $COLD still exists - not starting"; exit 1; fi
  echo "cold form: $COLD absent at $(u); the other entries of _ShaderCache/PPSA21564: $(ls "$EMU/_ShaderCache/PPSA21564" | wc -l)" > $OUT/cold.txt
else
  [ -f "$COLD/pipelines.bin" ] || { log "warm form FAILED: no $COLD/pipelines.bin - not starting"; exit 1; }
  echo "warm form: $COLD present at $(u); files $(ls "$COLD" | wc -l); pipelines.bin $(stat -c %s "$COLD/pipelines.bin") bytes" > $OUT/cold.txt
fi
log "$(cat $OUT/cold.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the FS4 copy failed - not starting"; exit 1; }
log "installed the FS4 copy: $(sha "$GAME")"
echo "$(sha "$GAME")" > $OUT/installed_sha.txt
GA="KYTY_GUEST_ARGS=-lvl underwater_aerial_garden"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
case "$T" in
  fs4_r0|fs4_r0r)
    python $G/run_fs4c.py $OUT 300 --sval "$GA" KYTY_FIX_SVAL=0 KYTY_FRAME_TRACE=lite KYTY_GPU_CLOCK_PIN=1 > $OUT/run.txt 2>&1;;
  fs4_r1)
    python $G/enter_scene.py $T --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 --emu-arg=--shader-validation --emu-arg=true \
      KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  fs4_hb)
    python $G/enter_scene.py $T --level hoover_beach --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 --emu-arg=--shader-validation --emu-arg=true \
      KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  fs4_w)
    python $G/enter_scene.py $T --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 600 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --emu-arg=--vulkan-validation --emu-arg=true --hold 310 \
      VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  fs4_v)
    python $G/enter_scene.py $T --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
esac
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
exit 0
