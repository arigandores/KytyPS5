#!/bin/bash
# Track F link F24e (HPP-664; ROADMAP s122 item 595 (e)(4), (zh); item 603 (v)): one tag "no harm" of KYTY_FIX_B13=1 on the F24c TEST binary
# 91f155b7 (= S18a2 0005e11f + 1570d110 + 21f8ca76 by cherry-pick, item 601; installed for the tag only, known by sha256); the installed S18
# b3cee576 (item 590) is checked by its full sha256 before and returned from its pinned copy after.  ONE TAG = ONE LOCK.  Port of
# C:/kyty/f287/f20l3/go_f20l3.sh (stop file, lock, procload through the <app> mask, lock.log UTC, the run check of item 587 (g), caches
# _ShaderCache (with PPSA21564/pipelines.bin and replay/) / _ShaderSeeds / _PipelineCache / _SaveData and the driver GLCache copied before
# and returned after, manifest sha256 before / run / after with the equality line, RETURN_FAILED keeps the lock, guard of the user game
# item 534 - kill by pid only) without M6, the cold form, KYTY_GPU_WALL and KYTY_DIAG_B32; the W form is the one of S18c2 go_s18c2.sh
# (s18_w2, item 587) without its input state (no cat_full, no KYTY_SHADER_SEED=0: the defaults of the binary, item 595 (e)(4)).
# usage: bash C:/kyty/f287/f24e/go_f24e.sh b13_v|b13_w      (repeats after an interference: <tag>_r1.._r3, item 273 (z), by the lead)
#   FORM v (seal pred/f24e_seal.md): enter_scene.py b13_v --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480
#     --no-install --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 330 KYTY_FIX_B13=1 KYTY_GPU_CLOCK_PIN=1
#     KYTY_GPU_MARKERS=0
#   FORM w: enter_scene.py b13_w --level underwater_aerial_garden --attempts 1 --stable-draws 100 --timeout 900 --no-install --require-idle
#     --gates-file gates_default.txt --pred <seal> --emu-arg=--vulkan-validation --emu-arg=true --hold 310 KYTY_FIX_B13=1
#     VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#     (precache at the default, no VK_LAYER_MESSAGE_ID_FILTER)
#   No RenderDoc, no KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH, no other KYTY_FIX_*; this script unsets KYTY_* and VK_LAYER_* before the call.
#   ASCII only.
# EXIT: 0 tag made (read it with post_f24e.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process / run gone;
#   4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f24e; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F24E_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
S18=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a
TB=91f155b70f867124781a687b0d86442f45abed90e33d4b9e749d296ccfa63e2f
BIN=$F/bin/kyty_emulator_91f155b7.exe
PINNED=C:/kyty/s288/bin/kyty_emulator_b3cee576.exe
SEAL=$G/pred/f24e_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
LV=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  b13_v|b13_w|b13_v_r[1-3]|b13_w_r[1-3]) ;;
  *) echo "usage: go_f24e.sh b13_v|b13_w[_r1..3]"; exit 2;;
esac
B=${T%_r[1-3]}
case "$B" in
  b13_v) FORM=v; SD=300; H=330; FA="--timeout 480 --rec --hold $H"; VK="";;
  b13_w) FORM=w; SD=100; H=310; FA="--timeout 900 --emu-arg=--vulkan-validation --emu-arg=true --hold $H"
         VK="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000";;
esac
[ "${F24E_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B form $FORM sd $SD hold $H args $FA vk $VK"; exit 0; }
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F24e go_f24e $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "F24c test binary copy $BIN is not 91f155b7 - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$S18" ] || { log "pinned S18 copy $PINNED is not b3cee576 - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$S18" ] || { log "installed binary $WANT is not S18 b3cee576 - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
GS=$(python $G/guard_f24e.py scan) || { python $G/guard_f24e.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
# item 587 (g) debt: the run that launched this detached call must still be going (a cancelled run does not stop its detached children)
RS=$(python $G/runchk_f24e.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
set -o noclobber
if ! { echo "F24e HPP-664 go_f24e.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f24e.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_f24e.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f24e.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS=$(python $G/guard_f24e.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f24e.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ $INSTALLED = 1 ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$S18" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$S18" ]; then log "installed binary returned from the pinned S18 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$S18" ] || { OK=0; log "INSTALLED BINARY IS NOT S18 after the tag"; }
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
    for d in $DIRS; do
      case " $COPIED " in *" $d "*) ;; *) [ -e "$EMU/$d" ] && { rm -rf "$EMU/$d" || OK=0; log "$d was absent before the tag - removed at the return";};; esac
    done
    [ $OK = 1 ] && log "caches, seeds, saves and GLCache returned"
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
    if [ -e $OUT/USER_FOUND ]; then
      UF=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_f24e.py close user_found > /dev/null
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF) - block closed, interference, repeat by the same name (item 534)"
    elif [ ! -f $OUT/run.txt ]; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never started - interference, repeat by the same name (item 534)"
    fi
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
log "caches, seeds, saves and GLCache copied:$COPIED ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
TC="$EMU/_ShaderCache/PPSA21564"
echo "state before the start: pipelines.bin $( [ -f "$TC/pipelines.bin" ] && echo present || echo absent ), replay $( [ -d "$TC/replay" ] && echo present || echo absent ), variant_fixb26_fixb1b_fixf10_fixf19 $( [ -d "$TC/variant_fixb26_fixb1b_fixf10_fixf19" ] && echo present || echo absent ) at $(u)" > $OUT/warm.txt
log "$(cat $OUT/warm.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the F24c test copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the F24c test copy for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, form $FORM, SD $SD, $FA, KYTY_FIX_B13=1 $VK)"
python $G/guard_f24e.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
F24E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL $FA KYTY_FIX_B13=1 $VK KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f24e.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
