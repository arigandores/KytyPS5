#!/bin/bash
# Track F link FS10c (HPP-686; ROADMAP s122 item 624 (e)(3), item 626 (b), item 623 (v)): one tag of the ship binary FS10 abfded5e (FS9
# 11164d72 + a8ee1b05, b4ee756a, 0e4b2f5a, 5064c5bb + FS10a 7f34b1e2, worktree dc5d4712; default KYTY_FIX_B36=1) - FS10 is installed for
# the tag only, known by its full sha256; the installed FS9 3861eeea (item 610) is checked before and returned from its pinned copy after.
# ONE TAG = ONE LOCK.  Port of C:/kyty/f287/fs9c/go_fs9c.sh (per-tag manifest and copy of the five folders before, return after, cmp EQUAL)
# with from C:/kyty/f287/f25m/go_f25m.sh: the display member (dispstate.py ON before the lock and after 'lock released', the request
# 'dispstate.py --hold-until' from before the lock to after 'lock released'; item 620 (g)(1), item 623 (v)), the user session guard of
# item 606 (v)(1) (hold_fs10c.py; a VM during the tag - the GLCache return by merge, user files kept, the tag is interference), the user
# form of enter_scene.py (--user-form) and the stand knobs.  No snapshots A / B (the live caches are A' of F25m restoreA; item 624 (e)(3):
# the catalog variant_fixb26_fixb1b_fixf10_fixf19 is warm, the signature = the base).  Level of every tag: underwater_aerial_garden.
#   fs10_s1  user form (--user-form: no KYTY_FRAME_TRACE, no KYTY_DIAG_B32, no gate files, no KYTY_QUEUE_TRACE, no KYTY_GPU_HANG_ABORT_S,
#            no video), KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3, default KYTY_FIX_B36 (not in the env), hold 150 s
#   fs10_s0  the same + KYTY_FIX_B36=0 (the rollback control)
#   fs10_f1  harness form (enter_scene constants: KYTY_FRAME_TRACE=lite, gate files, KYTY_QUEUE_TRACE=1, video) KYTY_GPU_CLOCK_PIN=1
#            KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22 KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3, no KYTY_DIAG_B32,
#            default KYTY_FIX_B36, hold 150 s (item 626 (b))
#   fs10_v   form fs9_v: KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, video, --stable-draws 300 --timeout 480, hold 330 s
#   fs10_w   form fs9_w: --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, no VK_LAYER_MESSAGE_ID_FILTER,
#            precache at the default, KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, --stable-draws 100 --timeout 900, hold 310 s
# No RenderDoc, no KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH, no KYTY_FIX_* except KYTY_FIX_B36=0 of fs10_s0; KYTY_* and VK_LAYER_* of the
# shell are unset before the call; the knobs go to enter_scene.py positionally.
# usage: bash C:/kyty/f287/fs10c/go_fs10c.sh fs10_s1|fs10_s0|fs10_f1|fs10_v|fs10_w      (repeats: <tag>_r1.._r3 by the lead's item)
# EXIT: 0 tag made (read it with post_fs10c.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process / run gone;
#   4 stop file; 5 procload busy; 6 display not ON before the lock.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/fs10c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${FS10C_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
FS9=3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5
TB=abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe
BIN=$F/bin/kyty_emulator_abfded5e.exe
PINNED=$F/bin/kyty_emulator_3861eeea.exe
SEAL=$G/pred/fs10c_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
LV=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  fs10_s[01]|fs10_f1|fs10_v|fs10_w|fs10_s[01]_r[1-3]|fs10_f1_r[1-3]|fs10_v_r[1-3]|fs10_w_r[1-3]) ;;
  *) echo "usage: go_fs10c.sh fs10_s1|fs10_s0|fs10_f1|fs10_v|fs10_w[_r1..3]"; exit 2;;
esac
B=${T%_r[1-3]}
STAND="KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3"
case "$B" in
  fs10_s1) UF="--user-form"; SD=300; H=150; TO=480; REC=""; KN="$STAND";;
  fs10_s0) UF="--user-form"; SD=300; H=150; TO=480; REC=""; KN="$STAND KYTY_FIX_B36=0";;
  fs10_f1) UF=""; SD=300; H=150; TO=480; REC="--rec"; KN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22 $STAND";;
  fs10_v) UF=""; SD=300; H=330; TO=480; REC="--rec"; KN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;
  fs10_w) UF=""; SD=100; H=310; TO=900; REC="--emu-arg=--vulkan-validation --emu-arg=true"
          KN="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;
esac
[ "${FS10C_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B level $LV uf ${UF:--} sd $SD hold $H timeout $TO rec ${REC:--} knobs $KN"; exit 0; }
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) FS10c go_fs10c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "FS10 copy $BIN is not abfded5e - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$FS9" ] || { log "pinned FS9 copy $PINNED is not 3861eeea - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$FS9" ] || { log "installed binary $WANT is not FS9 3861eeea - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
GS=$(python $G/guard_fs10c.py scan) || { python $G/guard_fs10c.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
HS=$(python $G/hold_fs10c.py check) || { python $G/guard_fs10c.py close user_session > /dev/null; log "user session (item 606 (v)(1)): $HS - not starting, block closed"; exit 3; }
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_fs10c.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
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
python $G/dispstate.py --hold-until $OUT/disp.stop --max $((TO + 1500)) > $OUT/disp_hold.txt 2>&1 &
DPID=$!
stop_disp() { touch $OUT/disp.stop 2>/dev/null; wait $DPID 2>/dev/null; }
set -o noclobber
if ! { echo "FS10c HPP-686 go_fs10c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_fs10c.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_fs10c.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
HS=$(python $G/hold_fs10c.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); python $G/guard_fs10c.py close user_session > /dev/null; log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, block closed"; exit 3; }
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_fs10c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS=$(python $G/guard_fs10c.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_fs10c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ -e $OUT/VM_FOUND ]; then
    log "user VM during the tag ($(head -1 $OUT/VM_FOUND | cut -c1-120)) - caches wait for its exit, poll 10 s, the lock stays (item 606 (v)(1))"
    log "$(python $G/hold_fs10c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
  fi
  if [ $INSTALLED = 1 ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$FS9" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$FS9" ]; then log "installed binary returned from the pinned FS9 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$FS9" ] || { OK=0; log "INSTALLED BINARY IS NOT FS9 after the tag"; }
  if [ -f $OUT/manifest_before.tsv ] && [ -n "$COPIED" ]; then
    python $G/manifest_fs4c.py $OUT/manifest_run.tsv "${MF[@]}" > $OUT/manifest_run.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_run.tsv > $OUT/manifest_cmp_run.txt 2>&1
    log "manifest of the run state (before the return): $(head -1 $OUT/manifest_run.txt | cut -c1-200); run vs before: $(head -1 $OUT/manifest_cmp_run.txt | cut -c1-200)"
  fi
  for d in $COPIED; do
    if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
    if [ "$d" = "GLCache" ] && [ -e $OUT/VM_FOUND ]; then
      MR=$(python $G/snap_fs10c.py merge-return GLCache "$OUT/before_$d" "$LIVE") || { OK=0; log "merge return of GLCache FAILED"; }
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
      python $G/mfsub_fs10c.py $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_sub.txt 2>&1 && MC=0
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
    [ -e $OUT/VM_FOUND ] && [ ! -e $OUT/USER_FOUND ] && cp $OUT/VM_FOUND $OUT/USER_FOUND
    if [ $DARC != 0 ] && [ -f $OUT/run.txt ]; then
      mv $OUT $OUT.display_$(date -u +%H%M%S)
      log "display not ON after the tag - the tag is the interference DISPLAY_OFF (item 620 (g)(1)), not read; repeat by the lead's item"
    elif [ -e $OUT/USER_FOUND ]; then
      UF2=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_fs10c.py close user_found > /dev/null
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF2) - block closed, interference, repeat by the lead (item 534)"
    elif [ ! -f $OUT/run.txt ]; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never started - not a tag, repeat by the same name (item 534)"
    fi
  else
    stop_disp
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete, installed binary or manifest differs - the lock stays"; RCX=1
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
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the FS10 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the FS10 copy for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, hold $H, ${UF:-harness form} ${REC:-no video}, $KN)"
python $G/guard_fs10c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_fs10c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL $UF $REC --hold $H $KN > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_fs10c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
