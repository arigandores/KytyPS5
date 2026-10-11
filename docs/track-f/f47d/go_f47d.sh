#!/bin/bash
# Track F link F47d (HPP-809; ROADMAP s122 item 708 (g), item 715 (v), (d), item 718 (v)(3), item 722 (g), item 724 (e)(2)): ONE tag of
# the snapshot series of the Sky Garden title (B34) on the INSTALLED binary - FS13 abab2196, or FS14 013e1974 if FS14d installed it
# before the tag (item 715 (d); then the checks of item 724 (e)(2) are a precondition: fs14_checks.txt with two ALL OK lines).  The
# binary is NOT installed or changed: its sha256 is checked before the lock, inside the lock before the tag and after the tag.
# ONE CALL = ONE LOCK.  Port of C:/kyty/f287/f46c/go_f46c.sh (form of item 634 / 660 / 661: no guard or hold check before the lock, ONE
# guard scan + hold check right after the lock, before any manifest; caches copied and returned with cmp EQUAL) with the capture part of
# C:/kyty/f287/f12f/go_f12f.sh (new .rdc of _RenderDoc moved out inside the lock, oldest first) and without the binary install.
# FORMS (seal docs/track-f/f47d.md = pred/f47d_seal.md):
#   f47_rd   enter_scene.py <tag> --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 600 --no-install
#            --require-idle --gates-file gates_default.txt --pred <seal> --emu-arg=--rd --hold 120 KYTY_RD_LEVEL=underwater_aerial_garden
#            KYTY_RD_LEVEL_FRAME=729,732,735,738,741,744,747,750,753,756,759,762 KYTY_RD_FLIPS=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#            (KYTY_FRAME_TRACE=lite is a constant of enter_scene.py; no video, no validation)
#   f47_rd2  the same with KYTY_RD_LEVEL_FRAME = R-16, R-13, ..., R+17, R = round(713.0 + 0.1075 * n0) of the admitted f47_rd tag
#            (item 708 (b)(6)); the grid is computed by next_f47d.py --grid
#   f47_hi   enter_scene.py <tag> --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install
#            --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 120 KYTY_HOST_IMPORT_MIN_KB=4194304
#            KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#   <tag>_r1.._r3  a repeat by the machine rule of next_f47d.py (one repeat after NOT_ADMITTED; an interference does not spend it)
# No KYTY_FIX_*, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS, no KYTY_TEST_*: KYTY_* and VK_LAYER_* of the shell are unset before the call;
# the knobs go to enter_scene.py positionally.
# After the run, inside the lock, before the cache return: the variant catalog of the run state is copied to runs/<tag>/variant_copy
# with a sha256 manifest (item 718 (v)(3)); for f47_rd*: every new capture -> f47_rd*_kNN.rdc (oldest first), sha256 list,
# renderdoccmd thumb -> kNN.png, detector G (thumb_f47d.py: 480x270, band y < 81, K max<=16, Wt min>=240) - one row per capture.
# usage: bash C:/kyty/f287/f47d/go_f47d.sh <tag>
# EXIT: 0 tag made (read it with post_f47d.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process / run
#   gone; 4 stop file; 5 procload busy; 6 display not ON; 7 machine rule (order / repeat / grid); 10 form linter FAILED; 12 lock budget.
#   ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f47d || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f47d; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F47D_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
INST13=abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73
INST14=013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd
SEAL=$G/pred/f47d_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
RDDIR="$EMU/_RenderDoc"
RDHOME="C:/Program Files/RenderDoc"
VARIANT="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19"
LV=underwater_aerial_garden
GRID1="729,732,735,738,741,744,747,750,753,756,759,762"
FREE_MIN_GIB=80
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f47_rd|f47_rd2|f47_hi|f47_rd_r[1-3]|f47_rd2_r[1-3]|f47_hi_r[1-3]) ;;
  *) echo "usage: go_f47d.sh f47_rd|f47_rd2|f47_hi[_r1..3]"; exit 2;;
esac
B=${T%_r[1-3]}
RUNS=${F47D_RUNS:-$G/runs}
KC="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0"
case "$B" in
  f47_rd) GRID=$GRID1;;
  f47_rd2)
    if [ "${F47D_DRYRUN:-}" = 1 ] && [ -n "${F47D_DRYGRID:-}" ]; then GRID=$F47D_DRYGRID; else
      GRID=$(python $G/next_f47d.py --grid --runs $RUNS); GR=$?
      [ $GR = 0 ] || { echo "no grid for f47_rd2 (next_f47d.py rc $GR): $GRID"; exit 7; }
    fi;;
esac
case "$B" in
  f47_rd|f47_rd2) SD=300; TO=600; H=120; MODE="--emu-arg=--rd"; KX="KYTY_RD_LEVEL=$LV KYTY_RD_LEVEL_FRAME=$GRID KYTY_RD_FLIPS=1 $KC";;
  f47_hi) SD=300; TO=480; H=120; MODE="--rec"; KX="KYTY_HOST_IMPORT_MIN_KB=4194304 $KC";;
esac
[ "${F47D_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B level $LV sd $SD timeout $TO hold $H mode $MODE knobs $KX"; exit 0; }
OUT=$RUNS/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F47d go_f47d $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
MAY=$(python $G/next_f47d.py --may $T --runs $RUNS); MR=$?
[ $MR = 0 ] || { log "machine rule (next_f47d.py, item 708 (g)): $MAY - not starting, not an attempt"; exit $MR; }
log "machine rule: $MAY"
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
WANT=$(sha "$GAME")
case "$WANT" in
  $INST13) BINNAME=FS13;;
  $INST14) BINNAME=FS14;;
  *) log "installed binary $WANT is neither FS13 abab2196 nor FS14 013e1974 - not starting (question to the lead)"; exit 1;;
esac
# item 715 (d), 724 (e)(2), F47a4 section 9: refs_f47a4.py check --code-commit and cls_f47a4.py scccheck --commit on the commit of the
# installed binary (FS13 ea6c6e9e, FS14 eb7e8b91) - two ALL OK lines in checks_<name>.txt before the tag
[ "$(grep -c '^ALL OK' $G/checks_$BINNAME.txt 2>/dev/null)" = 2 ] || { log "checks_$BINNAME.txt has not two ALL OK lines (item 715 (d), 724 (e)(2)) - not starting, question to the lead"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
[ -d "$VARIANT" ] || { log "no variant catalog $VARIANT - not starting"; exit 1; }
case "$B" in
  f47_rd|f47_rd2)
    for X in "$RDHOME/renderdoc.dll" "$RDHOME/renderdoccmd.exe"; do [ -f "$X" ] || { log "renderdoc file $X missing - not starting"; exit 1; }; done
    ls $G/${T}_k*.rdc > /dev/null 2>&1 && { log "$T captures exist - not starting"; exit 2; };;
esac
tasklist //FI "IMAGENAME eq qrenderdoc.exe" 2>/dev/null | grep -qi qrenderdoc && { log "a qrenderdoc lives - not starting"; exit 3; }
FREE=$(df -BG /c | tail -1 | awk '{print $4}' | tr -d 'G')
[ -n "$FREE" ] && [ "$FREE" -ge $FREE_MIN_GIB ] || { log "free on C: ${FREE:-?} GiB < $FREE_MIN_GIB (item 708 (g)(1)) - not starting, not an attempt"; exit 1; }
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
echo "$WANT $BINNAME" > $OUT/installed_pre.txt
echo "$FREE" > $OUT/free_gib_before.txt
[ -n "${GRID:-}" ] && echo "$GRID" > $OUT/grid.txt
log "installed binary before the lock: $BINNAME $WANT; free on C: $FREE GiB"
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_f47d.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
python $G/hostload_f47d.py --json $OUT/hostload_before.json > $OUT/hostload_before.txt 2>&1
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
if ! { echo "F47d HPP-809 go_f47d.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $RUNS/lock.log
GS=$(python $G/guard_f47d.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $RUNS/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); log "user emulator or launcher found right after the lock - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2)): $GS"; exit 3; }
HS=$(python $G/hold_f47d.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $RUNS/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2))"; exit 3; }
log "lock taken; guard: $GS; hold: $HS; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
[ "$(cat $OUT/installed_before.txt)" = "$WANT" ] || { rm -f $LOCK; echo "lock released $T $(u)" >> $RUNS/lock.log; stop_disp; mv $OUT $OUT.binchg_$(date -u +%H%M%S); log "installed binary changed between the check and the lock - lock released, not an attempt, question to the lead"; exit 1; }
COPIED=""
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f47d.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if tasklist //FI "IMAGENAME eq renderdoccmd.exe" 2>/dev/null | grep -qi renderdoccmd; then
    taskkill //F //IM renderdoccmd.exe > /dev/null 2>&1; log "renderdoccmd.exe killed at the exit (taskkill)"; sleep 2
  fi
  if [ -n "$COPIED" ]; then
    GS2=$(python $G/guard_f47d.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS2) - caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f47d.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ -e $OUT/VM_FOUND ]; then
    log "user VM during the tag ($(head -1 $OUT/VM_FOUND | cut -c1-120)) - caches wait for its exit, poll 10 s, the lock stays (item 606 (v)(1))"
    log "$(python $G/hold_f47d.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$WANT" ] || { OK=0; log "INSTALLED BINARY CHANGED during the tag"; }
  if [ -f $OUT/manifest_before.tsv ] && [ -n "$COPIED" ]; then
    python $G/manifest_fs4c.py $OUT/manifest_run.tsv "${MF[@]}" > $OUT/manifest_run.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_run.tsv > $OUT/manifest_cmp_run.txt 2>&1
    log "manifest of the run state (before the return): $(head -1 $OUT/manifest_run.txt | cut -c1-200); run vs before: $(head -1 $OUT/manifest_cmp_run.txt | cut -c1-200)"
  fi
  for d in $COPIED; do
    if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
    if [ "$d" = "GLCache" ] && [ -e $OUT/VM_FOUND ]; then
      MR2=$(python $G/snap_f47d.py merge-return GLCache "$OUT/before_$d" "$LIVE") || { OK=0; log "merge return of GLCache FAILED"; }
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
      python $G/mfsub_f47d.py $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_sub.txt 2>&1 && MC=0
      log "VM tag: before is a subset of after, extra only GLCache user files: $(head -1 $OUT/manifest_sub.txt)"
    fi
    [ $MC = 0 ] || OK=0
  fi
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $RUNS/lock.log; log "lock released (rc $RCX)"
    DA=$(python $G/dispstate.py); DARC=$?
    echo "$DA" > $OUT/disp_after.txt
    stop_disp
    log "display after lock released: $DA; hold: $(grep -c '^event ' $OUT/disp_hold.txt) display events, $(grep -c '^event .* OFF' $OUT/disp_hold.txt) OFF"
    python $G/hostload_f47d.py --json $OUT/hostload_after.json > $OUT/hostload_after.txt 2>&1
    log "host load after the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_after.txt | cut -c1-200)"
    [ -e $OUT/VM_FOUND ] && [ ! -e $OUT/USER_FOUND ] && cp $OUT/VM_FOUND $OUT/USER_FOUND
    if [ $DARC != 0 ] && [ -f $OUT/run.txt ]; then
      echo "display not ON after the tag: $DA" > $OUT/INTERFERENCE
      log "display not ON after the tag - interference DISPLAY_OFF (item 620 (g)(1)), the tag is not read; repeat by the machine rule"
    elif [ -e $OUT/USER_FOUND ]; then
      echo "user process during the tag: $(head -1 $OUT/USER_FOUND | cut -c1-160)" > $OUT/INTERFERENCE
      log "user process during the tag - interference (item 534, 273 (z)); repeat by the machine rule"
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
mkdir -p "$RDDIR"
ls "$RDDIR"/*.rdc 2>/dev/null | sort > $OUT/rdc_before.txt
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*' > $OUT/env_shell_after_unset.txt
log "enter_scene start (level $LV, sd $SD, timeout $TO, hold $H, $MODE, $KX); shell KYTY_*/VK_LAYER_* after unset: $(wc -l < $OUT/env_shell_after_unset.txt)"
python $G/guard_f47d.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_f47d.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL $MODE --hold $H $KX > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f47d.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
# item 718 (v)(3), F47a3 section 9: the variant catalog of the run state, before the cache return, into C:/kyty/f287/f47d/catalog_after/
# (replaced by every tag - after the last tag of the series it is the copy of the last tag) with a sha256 manifest, one line per file
rm -rf $G/catalog_after
if [ -d "$VARIANT" ]; then
  cp -a "$VARIANT" $G/catalog_after && python $G/manifest_fs4c.py $OUT/variant_copy.tsv "variant=$G/catalog_after" > $OUT/variant_copy.txt 2>&1
  echo "$T" > $G/catalog_after.tag
  log "variant catalog copied to f47d/catalog_after (run state, item 718 (v)(3)): $(head -1 $OUT/variant_copy.txt | cut -c1-160); files $(find $G/catalog_after -type f | wc -l); variant_copy.tsv sha256 $(sha $OUT/variant_copy.tsv)"
else
  log "variant catalog absent after the run - no copy"
fi
case "$B" in
  f47_rd|f47_rd2)
    ls -tr "$RDDIR"/*.rdc 2>/dev/null | while read -r X; do grep -qxF "$X" $OUT/rdc_before.txt || echo "$X"; done > $OUT/new_captures.txt
    log "new captures in _RenderDoc: $(grep -c . $OUT/new_captures.txt)"
    K=0
    while read -r X; do
      K=$((K+1)); KK=$(printf '%02d' $K)
      CAPF=$G/${T}_k$KK.rdc
      mv "$X" "$CAPF" || { log "move of $(basename "$X") failed"; continue; }
      "$RDHOME/renderdoccmd.exe" thumb --out="C:/kyty/f287/f47d/runs/$T/k$KK.png" "C:/kyty/f287/f47d/${T}_k$KK.rdc" > $OUT/thumb_k$KK.txt 2>&1
      TR=$?
      log "capture k$KK $(basename "$X") -> $(basename $CAPF) bytes $(stat -c %s "$CAPF"); thumb rc $TR sha256 $(sha $OUT/k$KK.png | cut -c1-16)"
    done < $OUT/new_captures.txt
    for C in $G/${T}_k*.rdc; do [ -f "$C" ] && echo "$(sha "$C")  $(basename $C)  $(stat -c %s "$C")"; done > $OUT/rdc_sha.txt
    python $G/thumb_f47d.py $OUT > $OUT/thumbs.txt 2>&1
    log "capture sha256 list lines $(wc -l < $OUT/rdc_sha.txt); detector G: $(grep '^G ' $OUT/thumbs.txt | cut -c1-200)"
    df -BG /c | tail -1 | awk '{print $4}' | tr -d 'G' > $OUT/free_gib_after.txt;;
esac
exit 0
