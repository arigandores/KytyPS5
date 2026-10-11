#!/bin/bash
# Track F link F40c (HPP-772; ROADMAP s122 item 692 (g)(1), (g)(3), (g)(4), item 696 (b)(1)-(3), item 700 (b)-(v)): the tags of the stand
# KYTY_TEST_HIDLOSS edition 2 (F24), the mutant tags and f24_n1 "no harm".  ONE CALL = ONE LOCK.  Port of C:/kyty/f287/f38c/go_f38c.sh
# (F38c, HPP-765: the form of item 634 / 660 / 661 - no guard or hold check before the lock, no block of tags, no window; ONE guard scan +
# hold check right after the lock, before any manifest; the binary install / return; the harness exit: WM_CLOSE at the end of the hold,
# CLOSE_WAIT_S = 40 s) with a table of tags.  The tag binary is installed for the tag only, known by its full sha256; the installed FS13
# abab2196 (item 703 (v), (d)) is checked before and returned from its pinned copy after.  Caches (_ShaderCache with PPSA21564/pipelines.bin,
# the variant catalog and replay/, _ShaderSeeds, _PipelineCache, _SaveData) and the driver GLCache are copied before every tag and
# returned after it with the manifest cmp EQUAL.
#   tag       binary            KYTY_FIX_F24  KYTY_TEST_HIDLOSS  hold  video
#   f24_u0    F40a2 ddf0ca91    0             60:upd             150   no
#   f24_u1    F40a2 ddf0ca91    1             60:upd             150   no    (after f24_u0)
#   f24_p0    F40a2 ddf0ca91    0             60:pad             150   no
#   f24_p1    F40a2 ddf0ca91    1             60:pad             150   no    (after f24_p0)
#   f24_f0    F40a2 ddf0ca91    0             60:flap            150   no
#   f24_f1    F40a2 ddf0ca91    1             60:flap            150   no
#   f24_x1    F40a2 ddf0ca91    1             60:exit            150   no    (enter_scene --mark-quit)
#   f24_d1    F40a2 ddf0ca91    1             60:detach          150   no
#   f24_m1    m1 c164a6d3       1             60:flap            150   no
#   f24_m2    m2 fcf462d8       1             60:exit            150   no    (enter_scene --mark-quit)
#   f24_m4    m4 ea84198d       1             60:detach          150   no
#   f24_m5    m5 bec75cc2       1             60:upd             150   no
#   f24_m6    m6 bd6dcc81       1             60:upd             150   no
#   f24_n1    F40a2 ddf0ca91    1             (none)             330   yes   (the form fs12_v)
#   f24_u0b / f24_u1b, f24_p0b / f24_p1b - the repeat pair of item 692 (g)(1) (a failure by the pad probe members only), same forms;
#   <tag>_r1, <tag>_r2 - a repeat after an interference (item 273 (z); the flap admission of item 696 (b)(2)); launch_f40c.sh needs
#   F40C_REPEAT_OK=1 for every repeat name.
# Common: --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file
# gates_default.txt --pred pred/f40c_seal.md --hold <H> [--rec] KYTY_FIX_F24=<0|1> [KYTY_TEST_HIDLOSS=60:<mode>] KYTY_GPU_CLOCK_PIN=1
# KYTY_GPU_MARKERS=0.  No RenderDoc, no KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH, no KYTY_DIAG_*, no other KYTY_FIX_* (KYTY_FIX_B24 is the
# FS12 default 1), no other KYTY_TEST_*; KYTY_* and VK_LAYER_* of the shell are unset before the call; the knobs go to enter_scene.py
# positionally.
# usage: bash C:/kyty/f287/f40c/go_f40c.sh <tag>
# EXIT: 0 tag made (read it with post_f40c.sh); 1 hard refusal / return failed; 2 usage / the tag exists / order; 3 lock / user process /
#   run gone; 4 stop file; 5 procload busy; 6 display not ON before the lock; 10 form linter FAILED (item 661 (b)(1)).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f40c || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f40c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F40C_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
INST=abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73
PINNED=$F/bin/kyty_emulator_abab2196.exe
SEAL=$G/pred/f40c_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
LV=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f24_u0|f24_u1|f24_p0|f24_p1|f24_f0|f24_f1|f24_x1|f24_d1|f24_m1|f24_m2|f24_m4|f24_m5|f24_m6|f24_n1|f24_u0b|f24_u1b|f24_p0b|f24_p1b) ;;
  f24_*_r[1-2]) ;;
  *) echo "usage: go_f40c.sh <tag> (f24_u0 f24_u1 f24_p0 f24_p1 f24_f0 f24_f1 f24_x1 f24_d1 f24_m1 f24_m2 f24_m4 f24_m5 f24_m6 f24_n1, pair b, _r1/_r2)"; exit 2;;
esac
B=${T%_r[1-2]}
case "$B" in
  f24_u0|f24_u0b) BIN8=ddf0ca91; FIX=0; MODE=upd; PREV="";;
  f24_u1) BIN8=ddf0ca91; FIX=1; MODE=upd; PREV=f24_u0;;
  f24_u1b) BIN8=ddf0ca91; FIX=1; MODE=upd; PREV=f24_u0b;;
  f24_p0|f24_p0b) BIN8=ddf0ca91; FIX=0; MODE=pad; PREV="";;
  f24_p1) BIN8=ddf0ca91; FIX=1; MODE=pad; PREV=f24_p0;;
  f24_p1b) BIN8=ddf0ca91; FIX=1; MODE=pad; PREV=f24_p0b;;
  f24_f0) BIN8=ddf0ca91; FIX=0; MODE=flap; PREV="";;
  f24_f1) BIN8=ddf0ca91; FIX=1; MODE=flap; PREV="";;
  f24_x1) BIN8=ddf0ca91; FIX=1; MODE=exit; PREV="";;
  f24_d1) BIN8=ddf0ca91; FIX=1; MODE=detach; PREV="";;
  f24_m1) BIN8=c164a6d3; FIX=1; MODE=flap; PREV="";;
  f24_m2) BIN8=fcf462d8; FIX=1; MODE=exit; PREV="";;
  f24_m4) BIN8=ea84198d; FIX=1; MODE=detach; PREV="";;
  f24_m5) BIN8=bec75cc2; FIX=1; MODE=upd; PREV="";;
  f24_m6) BIN8=bd6dcc81; FIX=1; MODE=upd; PREV="";;
  f24_n1) BIN8=ddf0ca91; FIX=1; MODE=""; PREV="";;
  *) echo "usage: unknown base $B"; exit 2;;
esac
case "$BIN8" in
  ddf0ca91) TB=ddf0ca913f9feb8a66569fa30668de4b97e275ab6c4cc3e5c69889b4cb82e5d5;;
  c164a6d3) TB=c164a6d34f0ab8b089d23752bf052da1db24f5ead9798ad0d8b8caa264d4ef0b;;
  fcf462d8) TB=fcf462d823eee56a0069866de224aeef9df2b1c6d9bc83288fee364705de0bef;;
  ea84198d) TB=ea84198deaebc903b38e07df98fc1f6af84172434c024874b6a5c787a0069446;;
  bec75cc2) TB=bec75cc20b86609bd1440a1a7aea1afea95a23af763f19b0f3a6e4c7e2f2fe94;;
  bd6dcc81) TB=bd6dcc81a32519eae50de4eb44ce88187d9ba9d4a8221c656b402c6065068c8f;;
esac
BIN=$F/bin/kyty_emulator_$BIN8.exe
SD=300; TO=480
if [ -z "$MODE" ]; then
  H=330; REC="--rec"; KX="KYTY_FIX_F24=$FIX KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0"; MQ=""
else
  H=150; REC=""; KX="KYTY_FIX_F24=$FIX KYTY_TEST_HIDLOSS=60:$MODE KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0"; MQ=""
  [ "$MODE" = exit ] && MQ="--mark-quit"
fi
[ "${F40C_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B binary $BIN8 level $LV sd $SD timeout $TO hold $H rec ${REC:-none} mark ${MQ:-none} prev ${PREV:-none} knobs $KX"; exit 0; }
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F40c go_f40c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
if [ -n "$PREV" ]; then
  ls -d $G/runs/$PREV $G/runs/${PREV}_r1 $G/runs/${PREV}_r2 2>/dev/null | grep -q . || { echo "order: $PREV is not made"; exit 2; }
fi
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ -f $G/base/base.tsv ] || { echo "no base manifest $G/base/base.tsv"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "tag binary copy $BIN is not $BIN8 - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$INST" ] || { log "pinned FS13 copy $PINNED is not abab2196 - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$INST" ] || { log "installed binary $WANT is not FS13 abab2196 - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_f40c.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
python $G/hostload_f40c.py --json $OUT/hostload_before.json > $OUT/hostload_before.txt 2>&1
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
if ! { echo "F40c HPP-772 go_f40c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f40c.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); log "user emulator or launcher found right after the lock - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2)): $GS"; exit 3; }
HS=$(python $G/hold_f40c.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2))"; exit 3; }
log "lock taken; guard: $GS; hold: $HS; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f40c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS2=$(python $G/guard_f40c.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS2) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f40c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ -e $OUT/VM_FOUND ]; then
    log "user VM during the tag ($(head -1 $OUT/VM_FOUND | cut -c1-120)) - caches wait for its exit, poll 10 s, the lock stays (item 606 (v)(1))"
    log "$(python $G/hold_f40c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
  fi
  if [ $INSTALLED = 1 ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$INST" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$INST" ]; then log "installed binary returned from the pinned FS13 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$INST" ] || { OK=0; log "INSTALLED BINARY IS NOT FS13 after the tag"; }
  if [ -f $OUT/manifest_before.tsv ] && [ -n "$COPIED" ]; then
    python $G/manifest_fs4c.py $OUT/manifest_run.tsv "${MF[@]}" > $OUT/manifest_run.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_run.tsv > $OUT/manifest_cmp_run.txt 2>&1
    log "manifest of the run state (before the return): $(head -1 $OUT/manifest_run.txt | cut -c1-200); run vs before: $(head -1 $OUT/manifest_cmp_run.txt | cut -c1-200)"
  fi
  for d in $COPIED; do
    if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
    if [ "$d" = "GLCache" ] && [ -e $OUT/VM_FOUND ]; then
      MR=$(python $G/snap_f40c.py merge-return GLCache "$OUT/before_$d" "$LIVE") || { OK=0; log "merge return of GLCache FAILED"; }
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
      python $G/mfsub_f40c.py $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_sub.txt 2>&1 && MC=0
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
    python $G/hostload_f40c.py --json $OUT/hostload_after.json > $OUT/hostload_after.txt 2>&1
    log "host load after the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_after.txt | cut -c1-200)"
    [ -e $OUT/VM_FOUND ] && [ ! -e $OUT/USER_FOUND ] && cp $OUT/VM_FOUND $OUT/USER_FOUND
    if [ $DARC != 0 ] && [ -f $OUT/run.txt ]; then
      mv $OUT $OUT.display_$(date -u +%H%M%S)
      log "display not ON after the tag - the tag is the interference DISPLAY_OFF (item 620 (g)(1)), not read; repeat by the next name"
    elif [ -e $OUT/USER_FOUND ]; then
      UF2=$(head -1 $OUT/USER_FOUND | cut -c1-160)
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF2) - interference, repeat by the next name (item 534, 273 (z))"
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
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the tag binary $BIN8 failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the tag binary $BIN8 for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*' > $OUT/env_shell_after_unset.txt
log "enter_scene start (level $LV, sd $SD, timeout $TO, hold $H, ${REC:-no video}, ${MQ:-no mark}, $KX); shell KYTY_*/VK_LAYER_* after unset: $(wc -l < $OUT/env_shell_after_unset.txt)"
python $G/guard_f40c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_f40c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL $REC $MQ --hold $H $KX > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f40c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
