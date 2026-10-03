#!/bin/bash
# F9g (HPP-424, ROADMAP s122 item 349 (v')(4), (g)(1)-(6); item 351 (g); item 353 (d); item 357 (d); item 359 (b)-(v)): ONE TAG = ONE
# LOCK (queue P > F > S, item 322 (g); the tags wait for a free lock between the tags of track P, item 359 (v)).
# usage: bash C:/kyty/f287/f9/f9g/go_f9g.sh <tag>      tags: f9g_v1 f9g_v2 f9g_c0 f9g_w f9g_sg f9g_hb, repeats f9g_c0r f9g_v1r f9g_v2r f9g_wr
# Port of C:/kyty/f287/f9/go_f9.sh (F9a/F9d: stop file, lock, live emulator, procload, lock.log UTC, caches and _SaveData copied
# before and returned after, RETURN_FAILED keeps the lock) with: the F9e2c copy 24efead3 installed into the emulator folder inside
# the lock and the installed 4aa62e95 put back from its pinned copy by sha in the EXIT trap (form of go_fs2.sh / go_f6e.sh - the
# driver caches stay keyed by the same exe path); GLCache copied and returned as well (form of FS2c); procload output through the
# <app> mask (item 324 (i)).  ASCII only.  No emulator code, no build.
#   FORMS (seal docs/track-f/f9g.md):
#     f9g_v1 f9g_v2 (and f9g_v1r f9g_v2r): form f9a_2 of item 349 (v')(1) without the diagnosis knobs + KYTY_FIX_B42=1, no validation:
#        run_f9g.py 215 s, KYTY_GUEST_ARGS=-lvl underwater_aerial_garden, KYTY_KEYS=$(cat keys_a2_presents.txt), KYTY_REC,
#        KYTY_FRAME_TRACE=lite, KYTY_GPU_CLOCK_PIN=1
#     f9g_c0 (and f9g_c0r): the same with KYTY_FIX_B42=0
#     f9g_w (and f9g_wr): the same input with KYTY_FIX_B42=1, --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=
#        100000000, no VK_LAYER_MESSAGE_ID_FILTER, precache by default (KYTY_PIPELINE_PRECACHE not passed), no video; the run ends
#        30 s after the release line of present 5945 (the last key), at most 590 s (item 349 (g)(4))
#     f9g_sg / f9g_hb: V of SCENE_OK form (s146 V form): enter_scene.py --level underwater_aerial_garden / hoover_beach --attempts 1
#        --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 330
#        KYTY_FIX_B42=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (no input)
#   KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS, KYTY_CMASK_CLEAR and every other KYTY_* are never passed (the env of run_f9g.py and
#   enter_scene.py is built from the positional pairs; go_f9g.sh unsets KYTY_* before enter_scene).
# EXIT: 0 tag made (read it with f9g_read.py); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f9/f9g; F9=C:/kyty/f287/f9; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/f9/bin/kyty_emulator_24efead3.exe
BIN_EXPECT=24efead326a6ddfd8b24b05549228fa165a1876a2c5adf58e2354b9d77270061
PINNED=C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe
WANT=4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac
SEAL=$G/pred/f9g_seal.md
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
# nvidia-smi of enter_scene.py needs these in the env (platform trap 7; form of go_fs2.sh)
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f9g_v1|f9g_v2|f9g_v1r|f9g_v2r|f9g_c0|f9g_c0r|f9g_w|f9g_wr|f9g_sg|f9g_hb) ;;
  *) echo "usage: go_f9g.sh <f9g_v1|f9g_v2|f9g_c0|f9g_w|f9g_sg|f9g_hb|f9g_c0r|f9g_v1r|f9g_v2r|f9g_wr>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$F9/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) go_f9g $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
[ -e C:/kyty/f287/STOP ] && { log "STOP file: $(head -1 C:/kyty/f287/STOP)"; exit 4; }
[ -e $F9/STOP ] && { log "STOP file: $(head -1 $F9/STOP)"; exit 4; }
[ -e $F9/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "fix copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not 4aa62e95 before the tag - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s 120 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F9g HPP-424 go_f9g.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
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
    echo "$(u) $T" > $F9/RETURN_FAILED; log "return incomplete - the lock stays"; RCX=1
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
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the fix copy failed - not starting"; exit 1; }
log "installed the F9e2c copy: $(sha "$GAME")"
KEYS=$(cat $G/keys_a2_presents.txt)
GA="KYTY_GUEST_ARGS=-lvl underwater_aerial_garden"
cd "$EMU" || exit 1
case "$T" in
  f9g_v1|f9g_v2|f9g_v1r|f9g_v2r)
    python $G/run_f9g.py $OUT 215 "$GA" "KYTY_KEYS=$KEYS" KYTY_REC=$OUT/rec.mp4 KYTY_FRAME_TRACE=lite KYTY_GPU_CLOCK_PIN=1 KYTY_FIX_B42=1 > $OUT/run.txt 2>&1;;
  f9g_c0|f9g_c0r)
    python $G/run_f9g.py $OUT 215 "$GA" "KYTY_KEYS=$KEYS" KYTY_REC=$OUT/rec.mp4 KYTY_FRAME_TRACE=lite KYTY_GPU_CLOCK_PIN=1 KYTY_FIX_B42=0 > $OUT/run.txt 2>&1;;
  f9g_w|f9g_wr)
    python $G/run_f9g.py $OUT 590 --val --until-release 5945 30 "$GA" "KYTY_KEYS=$KEYS" KYTY_FRAME_TRACE=lite KYTY_GPU_CLOCK_PIN=1 KYTY_FIX_B42=1 \
      VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 > $OUT/run.txt 2>&1;;
  f9g_sg|f9g_hb)
    if [ "$T" = "f9g_sg" ]; then LV=underwater_aerial_garden; else LV=hoover_beach; fi
    for v in $(env | grep -o '^KYTY_[A-Z0-9_]*'); do unset $v; done
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_FIX_B42=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
esac
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
exit 0
