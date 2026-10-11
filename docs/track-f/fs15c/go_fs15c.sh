#!/bin/bash
# Track F link FS15c (HPP-822; ROADMAP s122 item 730 (g)(3), acceptance FS15a / FS15b item 732, 733): the tags fs15_v / fs15_w /
# fs15_z of the shipping binary FS15 bfac84be (FS14 eb7e8b91 + a6342c98 + a9d6fd1c + 82570fd2 + 38fc76c1, default KYTY_FIX_F20=1, version
# KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73) - FS15 is installed for the tag only, known by its full sha256; the installed FS14 013e1974
# (item 727-728) is checked before and returned from its pinned copy after.  ONE CALL = ONE LOCK.  Port of C:/kyty/f287/fs14c/go_fs14c.sh
# (FS14c, HPP-814: the form of item 634 / 660 / 661 - no guard or hold check before the lock, no block of tags, no window; ONE guard scan
# + hold check right after the lock, before any manifest; the caches copied before and returned after EVERY tag - every tag is the first
# start of FS15 on the caches of the base; the install of the tag binary and the return of the installed one from its pinned copy) by
# gen_fs15c.py (names, binaries, the fs15_z knob).
#   fs15_v  form f20_v / fs14_v: --stable-draws 300 --timeout 480, hold 330 s, video; NO KYTY_FIX_* (the binary defaults)
#   fs15_w  form fs14_w / f20_w: --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, --stable-draws 100
#           --timeout 900, hold 310 s, no video; NO KYTY_FIX_*
#   fs15_z  the rollback control KYTY_FIX_F20=0, V Sky Garden: --stable-draws 300 --timeout 480, hold 150 s (>= 120 s), video
#   all: KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 + the constants of enter_scene.py (KYTY_FRAME_TRACE=lite, KYTY_GPU_HANG_ABORT_S=8, gate
#   files, KYTY_QUEUE_TRACE=1, KYTY_GUEST_ARGS=-lvl underwater_aerial_garden); the exit is the harness exit of b4_v (enter_scene posts
#   WM_CLOSE at the end of the hold - log 'Event: quit' - and waits CLOSE_WAIT_S = 40 s, else kills).
#   <tag>_r1..r3   a repeat only by the lead's item (an interference does not spend the attempt, item 273 (z)); FS15C_REPEAT_OK=1 needed
# No RenderDoc, no KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH, no KYTY_DIAG_*, no KYTY_TEST_*, no KYTY_FIX_* except KYTY_FIX_F20=0 at fs15_z;
# KYTY_* and VK_LAYER_* of the shell are unset before the call; the knobs go to enter_scene.py positionally.
# usage: bash C:/kyty/f287/fs15c/go_fs15c.sh fs15_v|fs15_w|fs15_z
# EXIT: 0 tag made (read it with post_fs15c.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process / run
#   gone; 4 stop file; 5 procload busy; 6 display not ON before the lock; 10 form linter FAILED (item 661 (b)(1)).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/fs15c || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/fs15c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${FS15C_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
FS14=013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd
TB=bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c
BIN=$F/bin/kyty_emulator_bfac84be.exe
PINNED=$F/bin/kyty_emulator_013e1974.exe
SEAL=$G/pred/fs15c_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
VKLAYER=C:/VulkanSDK/1.4.357.0/Bin
LV=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  fs15_v|fs15_w|fs15_z|fs15_v_r[1-3]|fs15_w_r[1-3]|fs15_z_r[1-3]) ;;
  *) echo "usage: go_fs15c.sh fs15_v|fs15_w|fs15_z[_r1..3]"; exit 2;;
esac
B=${T%_r[1-3]}
case "$B" in
  fs15_v) SD=300; H=330; TO=480; REC="--rec"; KX="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;
  fs15_w) SD=100; H=310; TO=900; REC="--emu-arg=--vulkan-validation --emu-arg=true"
          KX="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;
  fs15_z) SD=300; H=150; TO=480; REC="--rec"; KX="KYTY_FIX_F20=0 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;
esac
[ "${FS15C_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B level $LV sd $SD timeout $TO hold $H rec $REC knobs $KX"; exit 0; }
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) FS15c go_fs15c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ -f $G/base/base.tsv ] || { echo "no base manifest $G/base/base.tsv"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "FS15 copy $BIN is not bfac84be - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$FS14" ] || { log "pinned FS14 copy $PINNED is not 013e1974 - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$FS14" ] || { log "installed binary $WANT is not FS14 013e1974 - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_fs15c.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
python $G/hostload_fs15c.py --json $OUT/hostload_before.json > $OUT/hostload_before.txt 2>&1
log "host load before the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_before.txt | cut -c1-200)"
# item 623 (v)(1): a display OFF before the tag is woken by the harness itself, then checked again
DS=$(python $G/dispstate.py); DSRC=$?
if [ $DSRC != 0 ]; then
  WS=$(python $G/dispstate.py --wake | tr '\n' ';')
  log "display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-200)"
  DS=$(python $G/dispstate.py); DSRC=$?
fi
echo "$DS" > $OUT/disp_before.txt
[ $DSRC = 0 ] || { log "display not ON before the lock after the wake (item 620 (g)(1), 623 (v)(1)): $DS - not starting, files untouched, not an attempt"; mv $OUT $OUT.dispoff_$(date -u +%H%M%S); exit 6; }
log "display before the lock (item 620 (g)(1)): $DS"
python $G/dispstate.py --hold-until $OUT/disp.stop --max $((TO + H + 900)) > $OUT/disp_hold.txt 2>&1 &
DPID=$!
stop_disp() { touch $OUT/disp.stop 2>/dev/null; wait $DPID 2>/dev/null; }
set -o noclobber
if ! { echo "FS15c HPP-822 go_fs15c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_fs15c.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); log "user emulator or launcher found right after the lock - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2)): $GS"; exit 3; }
HS=$(python $G/hold_fs15c.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2))"; exit 3; }
log "lock taken; guard: $GS; hold: $HS; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_fs15c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS2=$(python $G/guard_fs15c.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS2) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_fs15c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ -e $OUT/VM_FOUND ]; then
    log "user VM during the tag ($(head -1 $OUT/VM_FOUND | cut -c1-120)) - caches wait for its exit, poll 10 s, the lock stays (item 606 (v)(1))"
    log "$(python $G/hold_fs15c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
  fi
  if [ $INSTALLED = 1 ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$FS14" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$FS14" ]; then log "installed binary returned from the pinned FS14 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$FS14" ] || { OK=0; log "INSTALLED BINARY IS NOT FS14 after the tag"; }
  if [ -f $OUT/manifest_before.tsv ] && [ -n "$COPIED" ]; then
    python $G/manifest_fs4c.py $OUT/manifest_run.tsv "${MF[@]}" > $OUT/manifest_run.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_run.tsv > $OUT/manifest_cmp_run.txt 2>&1
    log "manifest of the run state (before the return): $(head -1 $OUT/manifest_run.txt | cut -c1-200); run vs before: $(head -1 $OUT/manifest_cmp_run.txt | cut -c1-200)"
  fi
  for d in $COPIED; do
    if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
    if [ "$d" = "GLCache" ] && [ -e $OUT/VM_FOUND ]; then
      MR=$(python $G/snap_fs15c.py merge-return GLCache "$OUT/before_$d" "$LIVE") || { OK=0; log "merge return of GLCache FAILED"; }
      log "GLCache returned by merge (item 606 (v)(3)): $MR"; continue
    fi
    rm -rf "$LIVE" && mv "$OUT/before_$d" "$LIVE" || { OK=0; log "return of $d FAILED"; }
  done
  if [ -n "$COPIED" ]; then
    for d in $COPIED; do
      if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
      [ -d "$LIVE" ] || OK=0
      [ "$d" = "GLCache" ] && [ -e $OUT/VM_FOUND ] && continue
      [ ! -e "$OUT/before_$d" ] || OK=0
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
    if [ $MC != 0 ] && [ -e $OUT/VM_FOUND ]; then
      # item 606 (v)(3): after a merge return only new user files under GLCache may differ - nothing before may be lost or changed
      python $G/mfsub_fs15c.py $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_sub.txt 2>&1 && MC=0
      log "VM tag: before is a subset of after, extra only GLCache user files: $(head -1 $OUT/manifest_sub.txt)"
    fi
    [ $MC = 0 ] || OK=0
  fi
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; log "lock released (rc $RCX)"
    DA=$(python $G/dispstate.py); DARC=$?
    echo "$DA" > $OUT/disp_after.txt
    stop_disp
    log "display after lock released (item 620 (g)(1)): $DA; hold: $(grep -c '^event ' $OUT/disp_hold.txt) display events, $(grep -c '^event .* OFF' $OUT/disp_hold.txt) OFF; $(tail -1 $OUT/disp_hold.txt | cut -c1-120)"
    python $G/hostload_fs15c.py --json $OUT/hostload_after.json > $OUT/hostload_after.txt 2>&1
    log "host load after the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_after.txt | cut -c1-200)"
    [ -e $OUT/VM_FOUND ] && [ ! -e $OUT/USER_FOUND ] && cp $OUT/VM_FOUND $OUT/USER_FOUND
    if [ $DARC != 0 ] && [ -f $OUT/run.txt ]; then
      mv $OUT $OUT.display_$(date -u +%H%M%S)
      log "display not ON after the tag - the tag is the interference DISPLAY_OFF (item 620 (g)(1)), not read; repeat by the lead's item"
    elif [ -e $OUT/USER_FOUND ]; then
      UF2=$(head -1 $OUT/USER_FOUND | cut -c1-160)
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF2) - interference, repeat by the lead's item (item 534, 273 (z))"
    elif [ ! -f $OUT/run.txt ] || ! grep -q -- '--- attempt 1: launching' $OUT/run.txt; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never launched the emulator - not a tag, repeat by the same name"
    fi
  else
    stop_disp
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete, installed binary or manifest differs - the lock stays, question to the lead"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
python $G/manifest_fs4c.py --cmp $G/base/base.tsv $OUT/manifest_before.tsv > $OUT/base_cmp.txt 2>&1
log "caches before against the base manifest of the seal (row): $(head -1 $OUT/base_cmp.txt | cut -c1-160)"
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
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the FS15 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the FS15 copy bfac84be for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*' > $OUT/env_shell_after_unset.txt
log "enter_scene start (level $LV, sd $SD, timeout $TO, hold $H, $REC, $KX); shell KYTY_*/VK_LAYER_* after unset: $(wc -l < $OUT/env_shell_after_unset.txt) (no test knobs)"
python $G/guard_fs15c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_fs15c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL $REC --hold $H $KX > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_fs15c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
