#!/bin/bash
# Track F link F27c (HPP-694; ROADMAP s122 item 631 (v)-(d), item 634): one call of the series "B33 holds on FS10" - one tag of Day and
# Night (rotating_level_day_and_night) in the salted cold form on the INSTALLED FS10 abfded5e, or the series modes 'base' (manifest and
# copy of the user caches and the snapshot of the NVIDIA driver disk cache before the first tag) and 'return' (after the last tag).
# ONE CALL = ONE LOCK.  Port of C:/kyty/f287/f26c/go_f26c.sh (FS10 not installed by the chain, sha256 a member before and after; procload;
# runchk; display member item 623 (v); kill by own pid item 534 (v)(1); a user emulator during the tag item 534 (v)(4)) with the form of
# fs10_v of C:/kyty/f287/fs10c/go_fs10c.sh (video, KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, --stable-draws 300 --timeout 480) and
# ITEM 634: the guard check (guard_f27c.py scan + hold_f27c.py check) runs ONCE per call, right after the lock is taken, before any
# manifest - a finding releases the lock, no file is touched, the call is interference, the repeat is the next command; no check before the
# lock, no blocks of tags, no window between tags.
#   f27_v0, f27_v0b            KYTY_PIPELINE_PRECACHE=0 KYTY_PIPELINE_SALT=<tag> KYTY_S_PCW=0      (positive control of the form)
#   f27_v1a, f27_v1b, f27_v1c  KYTY_PIPELINE_PRECACHE=0 KYTY_PIPELINE_SALT=<tag>  (KYTY_S_PCW at the default 1)
#   (+ _r1/_r2: a repeat of an interference tag by the same form; salt = the full tag name)
#   all: the harness form of enter_scene.py (KYTY_FRAME_TRACE=lite, KYTY_GPU_HANG_ABORT_S=8, gate files, KYTY_QUEUE_TRACE=1) +
#   KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, --rec (KYTY_REC), --level rotating_level_day_and_night, --stable-draws 300 --timeout 480
#   --hold 120 (from 'stable'); no validation, no KYTY_GAME_PATCH, no stand, no KYTY_FIX_*.
# Before the tag: the user blob _PipelineCache/PPSA21564.bin copied to the salted name _PipelineCache/PPSA21564.<xxh3(salt)>.bin (size >=
# 80 000 000, sha256 of the copy = of the source; the salted name must not exist).  After the tag: the salted file (and its .tmp) moved to
# runs/<tag>/.  User caches U (ShaderCache_PPSA21564, ShaderSeeds_PPSA21564, _PipelineCache, _SaveData): manifest before the tag = the
# base (else SERIES_STOP - someone changed them between calls); after the tag the P5 labels against the base (p5.txt); a difference =>
# return from the base copy with the manifest check, the tag is interference (INTERFERENCE_P5).
# usage: bash C:/kyty/f287/f27c/go_f27c.sh base | f27_v0|f27_v0b|f27_v1a|f27_v1b|f27_v1c[_r1|_r2] | return
# EXIT: 0 done; 1 hard refusal / series stop / return failed; 2 usage / tag exists; 3 lock / user process / run gone; 4 stop file;
#   5 procload busy; 6 display not ON before the lock.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f27c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F27C_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
TB=abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe
SEAL=$G/pred/f27c_seal.md
LV=rotating_level_day_and_night
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  base|return) MODE=$T;;
  f27_v0|f27_v0b|f27_v1a|f27_v1b|f27_v1c|f27_v0_r[12]|f27_v0b_r[12]|f27_v1[abc]_r[12]) MODE=tag;;
  *) echo "usage: go_f27c.sh base | f27_v0|f27_v0b|f27_v1a|f27_v1b|f27_v1c[_r1|_r2] | return"; exit 2;;
esac
B=${T%_r[12]}
KN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PIPELINE_PRECACHE=0 KYTY_PIPELINE_SALT=$T"
case "$B" in f27_v0|f27_v0b) KN="$KN KYTY_S_PCW=0";; esac
SD=300; H=120; TO=480
[ "${F27C_DRYRUN:-}" = 1 ] && { echo "dryrun $T mode $MODE level $LV sd $SD hold $H timeout $TO rec yes knobs $KN"; exit 0; }
OUT=$G/runs/$T; TIMES=$F/times.txt; BASE=$G/base
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F27c go_f27c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("ShaderCache_PPSA21564=$EMU/_ShaderCache/PPSA21564" "ShaderSeeds_PPSA21564=$EMU/_ShaderSeeds/PPSA21564" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData")
P5L="ShaderCache_PPSA21564 ShaderSeeds_PPSA21564 _PipelineCache"
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
if [ $MODE = tag ]; then
  [ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
  [ -f $BASE/base.tsv ] && [ -f $BASE/drv_base.tsv ] || { echo "no series base - run 'go_f27c.sh base' first"; exit 1; }
  [ -e $G/RETURNED ] && { echo "the series caches were returned - no more tags"; exit 1; }
fi
[ $MODE = base ] && [ -e $BASE/base.tsv ] && { echo "base exists"; exit 2; }
[ $MODE = return ] && { [ -f $BASE/base.tsv ] || { echo "no base"; exit 1; }; [ -e $G/RETURNED ] && { echo "already returned"; exit 2; }; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a call runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$TB" ] || { log "installed binary $WANT is not FS10 abfded5e - not starting (question to the lead)"; exit 1; }
mkdir -p $OUT
DPID=""
if [ $MODE = tag ]; then
  echo "$LV" > $OUT/level.txt
  python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
  [ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
  [ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
  RS=$(python $G/runchk_f27c.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
  log "run check (item 587 (g)): $RS"
  python $G/hostload_f27c.py --json $OUT/hostload_before.json > $OUT/hostload_before.txt 2>&1
  log "host load before the tag (row): $(head -1 $OUT/hostload_before.txt | cut -c1-200)"
  DS=$(python $G/dispstate.py); DSRC=$?
  if [ $DSRC != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    log "display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-200)"
    DS=$(python $G/dispstate.py); DSRC=$?
  fi
  echo "$DS" > $OUT/disp_before.txt
  [ $DSRC = 0 ] || { log "display not ON before the lock after the wake (item 623 (v)(1)): $DS - not starting, files untouched, not an attempt"; mv $OUT $OUT.dispoff_$(date -u +%H%M%S); exit 6; }
  log "display before the lock (item 620 (g)(1)): $DS"
  python $G/dispstate.py --hold-until $OUT/disp.stop --max $((TO + H + 900)) > $OUT/disp_hold.txt 2>&1 &
  DPID=$!
fi
stop_disp() { [ -n "$DPID" ] && { touch $OUT/disp.stop 2>/dev/null; wait $DPID 2>/dev/null; }; }
set -o noclobber
if ! { echo "F27c HPP-694 go_f27c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
# ITEM 634 (b)(1): the one guard check of the call - right after the lock, before any manifest or cache
GS=$(python $G/guard_f27c.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); log "user emulator or launcher found right after the lock - lock released, files untouched, interference, repeat by the next command (item 634 (b)(1)): $GS"; exit 3; }
HS=$(python $G/hold_f27c.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); log "user session right after the lock (item 606 (v)(1), 634 (b)(1)): $HS - lock released, files untouched, interference, repeat by the next command"; exit 3; }
log "lock taken; guard after the lock (item 634 (b)(1)): $GS; $HS"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before: $(cat $OUT/installed_before.txt)"
release() { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; log "lock released ($1)"; }

# ---- mode base: manifest and copy of U, snapshot of the driver disk cache (item 631 (v)(6)) ----
if [ $MODE = base ]; then
  OK=1
  python $G/manifest_fs4c.py $BASE/base.tsv "${MF[@]}" > $OUT/manifest_base.txt 2>&1 || OK=0
  log "series base manifest: $(head -1 $OUT/manifest_base.txt | cut -c1-200)"
  TC="$EMU/_ShaderCache/PPSA21564"
  log "state of the base: pipelines.bin $( [ -f "$TC/pipelines.bin" ] && echo present || echo absent ), replay $( [ -d "$TC/replay" ] && echo present || echo absent ), variant_fixb26_fixb1b_fixf10_fixf19 $( [ -d "$TC/variant_fixb26_fixb1b_fixf10_fixf19" ] && echo present || echo absent ); user blob $(python $G/f27c_tools.py blob "$EMU/_PipelineCache/PPSA21564.bin")"
  for pair in "${MF[@]}"; do
    lab=${pair%%=*}; src=${pair#*=}
    [ -d "$src" ] || { log "$lab absent at the base (manifest line MISSING) - not copied"; continue; }
    cp -a "$src" "$BASE/copy_$lab" || { OK=0; log "copy of $lab failed"; }
  done
  python $G/manifest_fs4c.py $OUT/copy.tsv $(for pair in "${MF[@]}"; do lab=${pair%%=*}; echo "$lab=$BASE/copy_$lab"; done) > $OUT/manifest_copy.txt 2>&1
  python $G/manifest_fs4c.py --cmp $BASE/base.tsv $OUT/copy.tsv > $OUT/cmp_copy.txt 2>&1 || OK=0
  log "copy of U against the base manifest: $(head -1 $OUT/cmp_copy.txt)"
  python $G/drvsnap_f27c.py take $BASE > $OUT/drvsnap_take.txt 2>&1 || OK=0
  log "driver disk cache snapshot: $(head -1 $OUT/drvsnap_take.txt | cut -c1-200)"
  sha "$GAME" > $OUT/installed_after.txt
  [ "$(cat $OUT/installed_after.txt)" = "$TB" ] || OK=0
  if [ $OK = 1 ]; then cp $BASE/base.tsv $G/state_last.tsv; release "base ok"; exit 0; fi
  rm -f $BASE/base.tsv $BASE/drv_base.tsv; log "BASE FAILED - base manifests removed"; release "base failed"; exit 1
fi

# ---- mode return: U against the base (returned per tag already), the driver disk cache by the merge rule ----
if [ $MODE = return ]; then
  OK=1
  python $G/manifest_fs4c.py $OUT/manifest_end.tsv "${MF[@]}" > $OUT/manifest_end.txt 2>&1
  python $G/manifest_fs4c.py --cmp $BASE/base.tsv $OUT/manifest_end.tsv > $OUT/cmp_end_base.txt 2>&1 || OK=0
  log "U at the end against the base: $(head -1 $OUT/cmp_end_base.txt | cut -c1-200)"
  [ $OK = 1 ] || { echo "$(u) U differs from the base at the return: $(head -1 $OUT/cmp_end_base.txt)" > $G/RETURN_HELD; log "U differs from the base - nothing returned, RETURN_HELD, question to the lead"; release "return held"; exit 1; }
  python $G/drvsnap_f27c.py return $BASE $G/runs/lock.log > $OUT/drvsnap_return.txt 2>&1 || OK=0
  cp $BASE/drv_return.txt $OUT/ 2>/dev/null
  log "driver disk cache return: $(head -1 $OUT/drvsnap_return.txt | cut -c1-200)"
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the series: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$TB" ] || OK=0
  if [ $OK = 1 ]; then echo "$(u)" > $G/RETURNED; release "return ok"; exit 0; fi
  echo "$(u) return" > $G/RETURN_FAILED; log "RETURN INCOMPLETE - lock released, RETURN_FAILED, question to the lead"; release "return incomplete"; exit 1
fi

# ---- mode tag ----
HNAME=$(python $G/f27c_tools.py salt-name $T)
SALTED="$EMU/_PipelineCache/$HNAME"
SALTED_MADE=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f27c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$TB" ] || { OK=0; log "INSTALLED BINARY IS NOT FS10 after the tag"; }
  USER=0
  if [ -e $OUT/USER_FOUND ] || [ -e $OUT/VM_FOUND ]; then
    USER=1
    log "user process or session during the tag - waiting for its exit, poll 10 s, the lock stays (item 534 (v)(4), 606)"
    python $G/guard_f27c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1 >> $OUT/wait_gone.txt
    python $G/hold_f27c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1 >> $OUT/wait_gone.txt
    echo "$(u) $T user process or session during the tag - U may hold user files; question to the lead before the next tag and the return" > $G/SERIES_STOP
  fi
  if [ $SALTED_MADE = 1 ]; then
    for x in "$SALTED" "$SALTED.tmp"; do [ -e "$x" ] && { mv "$x" $OUT/ || { OK=0; log "move of the salted file $(basename "$x") FAILED"; }; }; done
    [ -f "$OUT/$HNAME" ] && log "salted file after the tag moved to the run folder: $(python $G/f27c_tools.py blob "$OUT/$HNAME")"
  fi
  if [ -f $OUT/manifest_before.tsv ]; then
    python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1 || OK=0
    python $G/f27c_tools.py cmp-labels $BASE/base.tsv $OUT/manifest_after.tsv $P5L > $OUT/p5.txt 2>&1; P5RC=$?
    python $G/f27c_tools.py cmp-labels $BASE/base.tsv $OUT/manifest_after.tsv _SaveData > $OUT/savedata.txt 2>&1
    python $G/manifest_fs4c.py --cmp $BASE/base.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1; MC=$?
    log "P5 (item 631 (v)(4)): $(head -1 $OUT/p5.txt | cut -c1-200); _SaveData (row): $(head -1 $OUT/savedata.txt | cut -c1-120)"
    if [ $MC != 0 ] && [ $USER = 0 ]; then
      echo "$(u) $T manifest after the tag differs from the base: $(head -1 $OUT/manifest_cmp.txt)" > $OUT/INTERFERENCE_P5
      for pair in "${MF[@]}"; do
        lab=${pair%%=*}; live=${pair#*=}
        python $G/f27c_tools.py cmp-labels $BASE/base.tsv $OUT/manifest_after.tsv $lab > /dev/null 2>&1 && continue
        if [ -d "$BASE/copy_$lab" ]; then rm -rf "$live" && cp -a "$BASE/copy_$lab" "$live" || { OK=0; log "return of $lab FAILED"; }
        else [ -e "$live" ] && { mkdir -p $OUT/moved_absent && mv "$live" $OUT/moved_absent/ || OK=0; }; fi
        log "$lab returned from the base copy (P5 interference)"
      done
      python $G/manifest_fs4c.py $OUT/manifest_return.tsv "${MF[@]}" > $OUT/manifest_return.txt 2>&1
      python $G/manifest_fs4c.py --cmp $BASE/base.tsv $OUT/manifest_return.tsv > $OUT/cmp_return.txt 2>&1 || OK=0
      log "manifest after the return against the base: $(head -1 $OUT/cmp_return.txt)"
    fi
  fi
  if [ $OK = 1 ]; then
    release "rc $RCX"
    DA=$(python $G/dispstate.py); DARC=$?
    echo "$DA" > $OUT/disp_after.txt
    stop_disp
    log "display after lock released (item 620 (g)(1)): $DA; hold: $(grep -c '^event ' $OUT/disp_hold.txt) display events, $(grep -c '^event .* OFF' $OUT/disp_hold.txt) OFF"
    python $G/hostload_f27c.py --json $OUT/hostload_after.json > $OUT/hostload_after.txt 2>&1
    log "host load after the tag (row): $(head -1 $OUT/hostload_after.txt | cut -c1-200)"
    if [ $USER = 1 ]; then
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag - interference (item 534 (v)(4)), SERIES_STOP"
    elif [ ! -f $OUT/run.txt ] || ! grep -q -- '--- attempt 1: launching' $OUT/run.txt; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never launched the emulator - not a tag, repeat by the same name"
    fi
  else
    stop_disp
    echo "$(u) $T" > $G/RETURN_FAILED; log "installed binary, salted file or U return failed - the lock stays, question to the lead"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
python $G/manifest_fs4c.py --cmp $BASE/base.tsv $OUT/manifest_before.tsv > $OUT/state_cmp.txt 2>&1
SC=$?
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200); against the base: $(head -1 $OUT/state_cmp.txt)"
if [ $SC != 0 ]; then
  echo "$(u) $T U changed between calls ($(head -1 $OUT/state_cmp.txt)) - question to the lead" > $G/SERIES_STOP
  log "U changed between calls - not starting, SERIES_STOP, question to the lead"
  rm -f $OUT/manifest_before.tsv; exit 1
fi
SRC="$EMU/_PipelineCache/PPSA21564.bin"
[ -e "$SALTED" ] && { log "salted name $HNAME exists before the tag - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
SALTED_MADE=1
cp -p "$SRC" "$SALTED" || { log "copy of the user blob to the salted name failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
SS=$(stat -c %s "$SALTED"); SH1=$(sha "$SRC"); SH2=$(sha "$SALTED")
echo "salt $T name $HNAME size $SS sha_src $SH1 sha_copy $SH2 $(python $G/f27c_tools.py blob "$SALTED")" > $OUT/salt.txt
log "salted copy (item 631 (v)(1)): $(cat $OUT/salt.txt | cut -c1-260)"
if [ "$SS" -lt 80000000 ] || [ "$SH1" != "$SH2" ]; then log "salted copy fails size >= 80 000 000 or sha - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; fi
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, timeout $TO, hold $H from stable, video, $KN)"
python $G/guard_f27c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_f27c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --rec --hold $H $KN > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f27c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
