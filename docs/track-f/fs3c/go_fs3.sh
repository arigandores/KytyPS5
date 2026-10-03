#!/bin/bash
# FS3c (HPP-449, ROADMAP s122 item 367 (g)(3)): ONE TAG = ONE LOCK (queue P > F > S, item 322 (g); the tags run only while the lock
# is free between the tags of track P).
# usage: bash C:/kyty/f287/fs3/fs3c/go_fs3.sh <tag>      tags: fs3_w fs3_v fs3_u fs3_u0 fs3_hb fs3_pu, the one repeat fs3_u0r
# Port of C:/kyty/f287/f9/f9g/go_f9g.sh (F9g: stop file, lock, live emulator, procload through the <app> mask, lock.log UTC, caches,
# _SaveData and GLCache copied before and returned after, RETURN_FAILED keeps the lock, the installed 4aa62e95 put back from its pinned
# copy by sha in the EXIT trap) with: the FS3 copy 540c035a (FS3a HPP-447, review FS3b HPP-448 PASS) installed instead of the F9e2c
# copy, the tag set of item 367 (g)(3), no KYTY_FIX_B42 except fs3_u0/fs3_u0r, KYTY_GAME_PATCH only in fs3_pu.  ASCII only.
#   FORMS (seal docs/track-f/fs3c.md):
#     fs3_u: form V1 of F9g (f9g_v1) at the defaults: run_fs3.py 215 s, KYTY_GUEST_ARGS=-lvl underwater_aerial_garden,
#        KYTY_KEYS=$(cat keys_a2_presents.txt), KYTY_REC, KYTY_FRAME_TRACE=lite, KYTY_GPU_CLOCK_PIN=1, no validation
#     fs3_u0 (and fs3_u0r): the same + KYTY_FIX_B42=0
#     fs3_pu: the same + KYTY_GAME_PATCH=C:/kyty/KytyPS5/patches/PPSA21564_pvar.txt (reference, not a gate)
#     fs3_w: W Sky Garden of item 295 (b) (form fs2_w of FS2c without the stand KYTY_TEST_MINIMIZE): enter_scene.py --level
#        underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 600 --no-install --require-idle --gates-file
#        gates_default.txt --pred <seal> --emu-arg=--vulkan-validation --emu-arg=true --hold 310 VK_LAYER_PATH VK_LAYER_DUPLICATE_
#        MESSAGE_LIMIT=100000000 (no VK_LAYER_MESSAGE_ID_FILTER, precache by default), no video
#     fs3_v / fs3_hb: V of SCENE_OK form (f9g_sg / f9g_hb without KYTY_FIX_B42): enter_scene.py --level underwater_aerial_garden /
#        hoover_beach --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred
#        <seal> --rec --hold 330 (no input)
#     every tag: KYTY_GPU_CLOCK_PIN=1; enter_scene tags also KYTY_GPU_MARKERS=0.
#   KYTY_GPU_CHECKPOINTS, KYTY_CMASK_CLEAR and every other KYTY_* are never passed (the env of run_fs3.py and enter_scene.py is built
#   from the positional pairs; go_fs3.sh unsets KYTY_* and VK_LAYER_* before enter_scene).
# EXIT: 0 tag made (read it with fs3_read.py); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/fs3/fs3c; FS3=C:/kyty/f287/fs3; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_540c035a.exe
BIN_EXPECT=540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1
PINNED=C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe
WANT=4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac
PATCHF=C:/kyty/KytyPS5/patches/PPSA21564_pvar.txt
SEAL=$G/pred/fs3c_seal.md
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
# nvidia-smi of enter_scene.py needs these in the env (platform trap 7; form of go_f9g.sh after its deviation 1)
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  fs3_w|fs3_v|fs3_u|fs3_u0|fs3_u0r|fs3_hb|fs3_pu) ;;
  *) echo "usage: go_fs3.sh <fs3_w|fs3_v|fs3_u|fs3_u0|fs3_hb|fs3_pu|fs3_u0r>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$FS3/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) go_fs3 $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
[ -e C:/kyty/f287/STOP ] && { log "STOP file: $(head -1 C:/kyty/f287/STOP)"; exit 4; }
[ -e $FS3/STOP ] && { log "STOP file: $(head -1 $FS3/STOP)"; exit 4; }
[ -e $FS3/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "FS3 copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not 4aa62e95 before the tag - not starting"; exit 1; }
[ -f "$PATCHF" ] || { log "no patch file $PATCHF - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "FS3c HPP-449 go_fs3.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
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
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/lock.log; log "lock released (rc $RCX)"
  else
    echo "$(u) $T" > $FS3/RETURN_FAILED; log "return incomplete - the lock stays"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
for d in $DIRS GLCache; do
  if [ "$d" = "GLCache" ]; then SRC="$GLDIR"; else SRC="$EMU/$d"; fi
  cp -a "$SRC" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
  COPIED="$COPIED $d"
done
log "caches, saves and GLCache copied: $DIRS GLCache ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the FS3 copy failed - not starting"; exit 1; }
log "installed the FS3 copy: $(sha "$GAME")"
KEYS=$(cat $G/keys_a2_presents.txt)
GA="KYTY_GUEST_ARGS=-lvl underwater_aerial_garden"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
case "$T" in
  fs3_u)
    python $G/run_fs3.py $OUT 215 "$GA" "KYTY_KEYS=$KEYS" KYTY_REC=$OUT/rec.mp4 KYTY_FRAME_TRACE=lite KYTY_GPU_CLOCK_PIN=1 > $OUT/run.txt 2>&1;;
  fs3_u0|fs3_u0r)
    python $G/run_fs3.py $OUT 215 "$GA" "KYTY_KEYS=$KEYS" KYTY_REC=$OUT/rec.mp4 KYTY_FRAME_TRACE=lite KYTY_GPU_CLOCK_PIN=1 KYTY_FIX_B42=0 > $OUT/run.txt 2>&1;;
  fs3_pu)
    python $G/run_fs3.py $OUT 215 "$GA" "KYTY_KEYS=$KEYS" KYTY_REC=$OUT/rec.mp4 KYTY_FRAME_TRACE=lite KYTY_GPU_CLOCK_PIN=1 KYTY_GAME_PATCH=$PATCHF > $OUT/run.txt 2>&1;;
  fs3_w)
    python $G/enter_scene.py $T --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 600 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --emu-arg=--vulkan-validation --emu-arg=true --hold 310 \
      VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  fs3_v|fs3_hb)
    if [ "$T" = "fs3_v" ]; then LV=underwater_aerial_garden; else LV=hoover_beach; fi
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
esac
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
exit 0
