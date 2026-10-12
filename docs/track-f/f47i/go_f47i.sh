#!/bin/bash
# Track F link F47i (HPP-826; ROADMAP s122 item 740 (v)(3), item 742 (e), item 744 (g)-(d)): the ONE tag f47_dt of the measurement-only
# code KYTY_DIAG_F47DT (B34) on the F47g2 binary 86e42e36 (accepted by F47h2, item 744) - installed for the tag only, known by its full
# sha256; the installed FS15 bfac84be (item 738) is checked before the lock, inside the lock before the tag and returned from its pinned
# copy after the tag, checked by sha256.  ONE CALL = ONE LOCK.  Port of C:/kyty/f287/f47d/go_f47d.sh (F47d, HPP-809: the form of item
# 634 / 660 / 661 - no guard or hold check before the lock, no block of tags, no window; ONE guard scan + hold check right after the lock,
# before any manifest; manifest sha256 and copy of _ShaderCache (with pipelines.bin, the variant catalog and replay/), _ShaderSeeds,
# _PipelineCache, _SaveData and the driver cache GLCache before the tag, the return with 'manifest cmp EQUAL' after it) with the binary
# install / return of C:/kyty/f287/f42c/go_f42c.sh (F42c, HPP-781).
# FORM (seal docs/track-f/f47i.md = pred/f47i_seal.md):
#   f47_dt   enter_scene.py <tag> --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install
#            --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 120 KYTY_DIAG_F47DT=1
#            KYTY_DIAG_F47DT_FRAMES=<WIN> KYTY_STREAM_TRACE=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#            (KYTY_FRAME_TRACE=lite and the other constants are enter_scene.py's; no validation, no --rd)
#   <tag>_r1.._r3  a repeat only by the lead's item (item 740 (v)(3): one attempt, an interference is repeated by the lead's item);
#            F47I_REPEAT_OK=1 is set by the executor after the times.txt line with the item.
# WIN - the show window by the field q (item 742 (v)(1)): the one line 'a-b' of pred/window.txt, a sealed file (SHA256SUMS of the seal),
#   written from the lead's item (question of 2026-10-12T03:32Z: 700-1000 by q does not cover the block shows).  Empty or not 'a-b' - no tag.
# _f47dt/ (the files of KYTY_DIAG_F47DT, relative to the working dir of the emulator): absent in the emulator folder before the tag
#   (else not starting); after the run, inside the lock, moved to C:/kyty/f287/f47i/_f47dt (repeat: _f47dt_<tag>) with a sha256 manifest.
# No KYTY_FIX_*, no KYTY_TEST_*, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS: KYTY_* and VK_LAYER_* of the shell are unset before the
# call; the knobs go to enter_scene.py positionally.
# usage: bash C:/kyty/f287/f47i/go_f47i.sh f47_dt[_r1..3]   (F47I_DRYRUN=1 prints the plan)
# EXIT: 0 tag made (read it with post_f47i.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process / run
#   gone; 4 stop file; 5 procload busy; 6 display not ON; 10 form linter FAILED; 11 repeat without the lead's item.  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f47i || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f47i; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F47I_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
INST=bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c
PINNED=$F/bin/kyty_emulator_bfac84be.exe
TB=86e42e36440ac5b7ac7a420c12d7a6aaadc4ffc483145ae9c6d18be046075e82
BIN=$F/bin/kyty_emulator_86e42e36.exe
SEAL=$G/pred/f47i_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
VARIANT="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19"
LV=underwater_aerial_garden
WIN=$(head -1 $G/pred/window.txt 2>/dev/null | tr -cd '0-9-')
FREE_MIN_GIB=40
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f47_dt) REP=0;;
  f47_dt_r[1-3]) REP=1;;
  *) echo "usage: go_f47i.sh f47_dt[_r1..3]"; exit 2;;
esac
echo "$WIN" | grep -qE '^[0-9]+-[0-9]+$' || { echo "window WIN not set by the lead's item - no tag"; exit 1; }
SD=300; TO=480; H=120
KX="KYTY_DIAG_F47DT=1 KYTY_DIAG_F47DT_FRAMES=$WIN KYTY_STREAM_TRACE=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0"
[ "${F47I_DRYRUN:-}" = 1 ] && { echo "dryrun $T level $LV sd $SD timeout $TO hold $H rec knobs $KX"; exit 0; }
RUNS=$G/runs; OUT=$RUNS/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
if [ $T = f47_dt ]; then DTD=$G/_f47dt; else DTD=$G/_f47dt_$T; fi
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F47i go_f47i $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
if [ $REP = 1 ]; then
  [ "${F47I_REPEAT_OK:-}" = 1 ] || { log "a repeat needs the lead's item and its times.txt line first (item 740 (v)(3)) - not starting"; exit 11; }
fi
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "F47g2 copy $BIN is not 86e42e36 - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$INST" ] || { log "pinned FS15 copy $PINNED is not bfac84be - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$INST" ] || { log "installed binary $WANT is not FS15 bfac84be - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
[ -d "$VARIANT" ] || { log "no variant catalog $VARIANT - not starting"; exit 1; }
[ -e "$EMU/_f47dt" ] && { log "_f47dt exists in the emulator folder before the tag - not starting, not an attempt, question to the lead"; exit 1; }
[ -e "$DTD" ] && { log "$DTD exists - not starting"; exit 2; }
FREE=$(df -BG /c | tail -1 | awk '{print $4}' | tr -d 'G')
[ -n "$FREE" ] && [ "$FREE" -ge $FREE_MIN_GIB ] || { log "free on C: ${FREE:-?} GiB < $FREE_MIN_GIB (item 740 (v)(3)) - not starting, not an attempt"; exit 1; }
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
echo "$WIN" > $OUT/window.txt
echo "$WANT FS15" > $OUT/installed_pre.txt
echo "$FREE" > $OUT/free_gib_before.txt
log "installed binary before the lock: FS15 $WANT; free on C: $FREE GiB; window q $WIN"
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_f47i.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
python $G/hostload_f47i.py --json $OUT/hostload_before.json > $OUT/hostload_before.txt 2>&1
log "host load before the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_before.txt | cut -c1-200)"
DS=$(python $G/dispstate.py); DSRC=$?
if [ $DSRC != 0 ]; then
  WS=$(python $G/dispstate.py --wake | tr '\n' ';')
  log "display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-200)"
  DS=$(python $G/dispstate.py); DSRC=$?
fi
echo "$DS" > $OUT/disp_before.txt
[ $DSRC = 0 ] || { log "display not ON before the lock after the wake (item 623 (v)(1)): $DS - not starting, files untouched, not an attempt"; mv $OUT $OUT.dispoff_$(date -u +%H%M%S); exit 6; }
log "display before the lock: $DS"
python $G/dispstate.py --hold-until $OUT/disp.stop --max $((TO + H + 1500)) > $OUT/disp_hold.txt 2>&1 &
DPID=$!
stop_disp() { touch $OUT/disp.stop 2>/dev/null; wait $DPID 2>/dev/null; }
set -o noclobber
if ! { echo "F47i HPP-826 go_f47i.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $RUNS/lock.log
GS=$(python $G/guard_f47i.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $RUNS/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); log "user emulator or launcher found right after the lock - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2)): $GS"; exit 3; }
HS=$(python $G/hold_f47i.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $RUNS/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2))"; exit 3; }
log "lock taken; guard: $GS; hold: $HS; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
[ "$(cat $OUT/installed_before.txt)" = "$INST" ] || { rm -f $LOCK; echo "lock released $T $(u)" >> $RUNS/lock.log; stop_disp; mv $OUT $OUT.binchg_$(date -u +%H%M%S); log "installed binary changed between the check and the lock - lock released, not an attempt, question to the lead"; exit 1; }
COPIED=""
INSTALLED=0
move_dt() {
  if [ -e "$EMU/_f47dt" ]; then
    mv "$EMU/_f47dt" "$DTD" && log "_f47dt moved to $DTD: files $(find "$DTD" -type f | wc -l), bytes $(du -sb "$DTD" | cut -f1)" || { OK=0; log "move of _f47dt FAILED"; }
    python $G/manifest_fs4c.py $OUT/f47dt_files.tsv "f47dt=$DTD" > $OUT/f47dt_files.txt 2>&1
    log "_f47dt manifest: $(head -1 $OUT/f47dt_files.txt | cut -c1-160); f47dt_files.tsv sha256 $(sha $OUT/f47dt_files.tsv)"
  else
    log "no _f47dt in the emulator folder after the run"
  fi
}
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f47i.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS2=$(python $G/guard_f47i.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS2) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f47i.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ -e $OUT/VM_FOUND ]; then
    log "user VM during the tag ($(head -1 $OUT/VM_FOUND | cut -c1-120)) - caches wait for its exit, poll 10 s, the lock stays (item 606 (v)(1))"
    log "$(python $G/hold_f47i.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
  fi
  move_dt
  if [ $INSTALLED = 1 ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$INST" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$INST" ]; then log "installed binary returned from the pinned FS15 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$INST" ] || { OK=0; log "INSTALLED BINARY IS NOT FS15 bfac84be after the tag"; }
  if [ -f $OUT/manifest_before.tsv ] && [ -n "$COPIED" ]; then
    python $G/manifest_fs4c.py $OUT/manifest_run.tsv "${MF[@]}" > $OUT/manifest_run.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_run.tsv > $OUT/manifest_cmp_run.txt 2>&1
    log "manifest of the run state (before the return): $(head -1 $OUT/manifest_run.txt | cut -c1-200); run vs before: $(head -1 $OUT/manifest_cmp_run.txt | cut -c1-200)"
  fi
  for d in $COPIED; do
    if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
    if [ "$d" = "GLCache" ] && [ -e $OUT/VM_FOUND ]; then
      MR2=$(python $G/snap_f47i.py merge-return GLCache "$OUT/before_$d" "$LIVE") || { OK=0; log "merge return of GLCache FAILED"; }
      log "GLCache returned by merge (item 606 (v)(3)): $MR2"; continue
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
      python $G/mfsub_f47i.py $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_sub.txt 2>&1 && MC=0
      log "VM tag: before is a subset of after, extra only GLCache user files: $(head -1 $OUT/manifest_sub.txt)"
    fi
    [ $MC = 0 ] || OK=0
  fi
  [ -e "$EMU/_f47dt" ] && { OK=0; log "_f47dt still in the emulator folder after the return"; }
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $RUNS/lock.log; log "lock released (rc $RCX)"
    DA=$(python $G/dispstate.py); DARC=$?
    echo "$DA" > $OUT/disp_after.txt
    stop_disp
    log "display after lock released: $DA; hold: $(grep -c '^event ' $OUT/disp_hold.txt) display events, $(grep -c '^event .* OFF' $OUT/disp_hold.txt) OFF"
    python $G/hostload_f47i.py --json $OUT/hostload_after.json > $OUT/hostload_after.txt 2>&1
    log "host load after the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_after.txt | cut -c1-200)"
    df -BG /c | tail -1 | awk '{print $4}' | tr -d 'G' > $OUT/free_gib_after.txt
    [ -e $OUT/VM_FOUND ] && [ ! -e $OUT/USER_FOUND ] && cp $OUT/VM_FOUND $OUT/USER_FOUND
    if [ $DARC != 0 ] && [ -f $OUT/run.txt ]; then
      echo "display not ON after the tag: $DA" > $OUT/INTERFERENCE
      log "display not ON after the tag - interference DISPLAY_OFF (item 620 (g)(1)), the tag is not read; repeat by the lead's item"
    elif [ -e $OUT/USER_FOUND ]; then
      echo "user process during the tag: $(head -1 $OUT/USER_FOUND | cut -c1-160)" > $OUT/INTERFERENCE
      log "user process during the tag - interference (item 534, 273 (z)); repeat by the lead's item"
    elif [ ! -f $OUT/run.txt ] || ! grep -q -- '--- attempt 1: launching' $OUT/run.txt; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never launched the emulator - not a tag, repeat by the same name"
    fi
  else
    stop_disp
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete, installed binary, _f47dt or manifest differs - the lock stays, question to the lead"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
[ -f $G/base/base.tsv ] && { python $G/manifest_fs4c.py --cmp $G/base/base.tsv $OUT/manifest_before.tsv > $OUT/base_cmp.txt 2>&1; log "caches before against the base manifest of the seal (row): $(head -1 $OUT/base_cmp.txt | cut -c1-160)"; }
for d in $DIRS GLCache; do
  if [ "$d" = "GLCache" ]; then SRC="$GLDIR"; else SRC="$EMU/$d"; fi
  [ -d "$SRC" ] || { log "$d absent - not copied (manifest line MISSING)"; continue; }
  cp -a "$SRC" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
  COPIED="$COPIED $d"
done
log "caches, seeds, saves and GLCache copied:$COPIED ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
TC="$EMU/_ShaderCache/PPSA21564"
echo "state before the start: pipelines.bin $( [ -f "$TC/pipelines.bin" ] && echo present || echo absent ), replay $( [ -d "$TC/replay" ] && echo present || echo absent ), variant_fixb26_fixb1b_fixf10_fixf19 $( [ -d "$VARIANT" ] && echo present || echo absent ) at $(u)" > $OUT/warm.txt
log "$(cat $OUT/warm.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the F47g2 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the F47g2 copy 86e42e36 for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*' > $OUT/env_shell_after_unset.txt
log "enter_scene start (level $LV, sd $SD, timeout $TO, hold $H, --rec, $KX); shell KYTY_*/VK_LAYER_* after unset: $(wc -l < $OUT/env_shell_after_unset.txt)"
python $G/guard_f47i.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_f47i.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --rec --hold $H $KX > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f47i.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
