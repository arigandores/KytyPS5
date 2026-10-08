#!/bin/bash
# Track F link F26c (HPP-692; ROADMAP s122 item 630 (g)-(d)): one call of the B25 series on the INSTALLED FS10 abfded5e - one tag
# b25_NN (entry 'intro_next' by -lvl, hold 120 s from the line 'Level has started: intro_next'), or the series modes 'base' (manifest
# and copy of the series caches before the first tag) and 'return' (return of the copies after the last tag, manifest EQUAL to base).
# ONE CALL = ONE LOCK.  Port of C:/kyty/f287/fs10c/go_fs10c.sh: the binary is NOT installed by the chain (FS10 is installed since
# 2026-10-08 04:58:12Z, item 628) - its full sha256 is a member before and after every tag; the caches are NOT copied / returned per tag
# (item 630 (g)(4): inside the series they are not returned) - instead the manifest before every tag must be EQUAL to the state after
# the previous call (state_last.tsv; a difference = someone else changed the caches between tags => SERIES_STOP, question to the lead);
# GLCache of the driver is not copied, not returned and not in the manifest (executor variant: item 630 (g)(4) names two folders; a
# return across blocks with the lock released would overwrite files of a user session, item 534 (a), 606).  Kept from FS10c: the user
# guard of item 534 (guard_f26c.py, kill by own pid only), the user session guard of item 606 (v)(1) (hold_f26c.py), the display member
# (dispstate.py, item 623 (v)), the run check (runchk_f26c.py), procload.py.
#   b25_NN   harness form of enter_scene.py (KYTY_FRAME_TRACE=lite, KYTY_GPU_HANG_ABORT_S=8, gate files, KYTY_QUEUE_TRACE=1,
#            KYTY_GUEST_ARGS=-lvl intro_next) + KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (= the env of fs10_v), no KYTY_REC, no
#            validation, no KYTY_GAME_PATCH, no stand, no KYTY_FIX_*; --entry-at-level --timeout 60 --hold 120
# Series folders (manifest and return): _ShaderCache/PPSA21564 (pipelines.bin, the variant catalog, replay/), _ShaderSeeds/PPSA21564
# (item 630 (g)(4)) and _PipelineCache, _SaveData (executor variant: the driver blob and the saves of the user, as the five folders of FS10c
# minus GLCache).
# usage: bash C:/kyty/f287/f26c/go_f26c.sh base | b25_01..b25_55 | return
# EXIT: 0 done; 1 hard refusal / series stop / return failed; 2 usage / tag exists; 3 lock / user process / run gone; 4 stop file;
#   5 procload busy; 6 display not ON before the lock.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f26c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F26C_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
TB=abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe
SEAL=$G/pred/f26c_seal.md
LV=intro_next
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  base|return) MODE=$T;;
  b25_0[1-9]|b25_[1-4][0-9]|b25_5[0-5]) MODE=tag;;
  *) echo "usage: go_f26c.sh base | b25_01..b25_55 | return"; exit 2;;
esac
KN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0"
H=120; TO=60
[ "${F26C_DRYRUN:-}" = 1 ] && { echo "dryrun $T mode $MODE level $LV entry-at-level timeout $TO hold $H knobs $KN"; exit 0; }
OUT=$G/runs/$T; TIMES=$F/times.txt; BASE=$G/base
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F26c go_f26c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("ShaderCache_PPSA21564=$EMU/_ShaderCache/PPSA21564" "ShaderSeeds_PPSA21564=$EMU/_ShaderSeeds/PPSA21564" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
if [ $MODE = tag ]; then
  [ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
  [ -f $BASE/base.tsv ] && [ -f $G/state_last.tsv ] || { echo "no series base - run 'go_f26c.sh base' first"; exit 1; }
  [ -e $G/RETURNED ] && { echo "the series caches were returned - no more tags"; exit 1; }
fi
[ $MODE = base ] && [ -e $BASE/base.tsv ] && { echo "base exists"; exit 2; }
[ $MODE = return ] && { [ -f $BASE/base.tsv ] || { echo "no base"; exit 1; }; [ -e $G/RETURNED ] && { echo "already returned"; exit 2; }; [ -e $G/RETURN_HELD ] && { echo "RETURN_HELD exists - the lead decides"; exit 1; }; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a call runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$TB" ] || { log "installed binary $WANT is not FS10 abfded5e - not starting (question to the lead)"; exit 1; }
GS=$(python $G/guard_f26c.py scan) || { python $G/guard_f26c.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
HS=$(python $G/hold_f26c.py check) || { python $G/guard_f26c.py close user_session > /dev/null; log "user session (item 606 (v)(1)): $HS - not starting, block closed"; exit 3; }
mkdir -p $OUT
if [ $MODE = tag ]; then
  echo "$LV" > $OUT/level.txt
  # item 632 (v)(1): the gate of the functional seals (item 115 #7) - 1.5 CPU s/s per process, 4 in total
  python $G/procload.py --wait-s ${PLWAIT:-120} --max-rate 1.5 --max-total 4 2>&1 | mask > $OUT/procload.txt
  [ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
  [ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
  RS=$(python $G/runchk_f26c.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
  log "run check (item 587 (g)): $RS"
  python $G/hostload_f26c.py --json $OUT/hostload_before.json > $OUT/hostload_before.txt 2>&1
  log "host load before the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_before.txt | cut -c1-200)"
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
else
  DPID=""
fi
stop_disp() { [ -n "$DPID" ] && { touch $OUT/disp.stop 2>/dev/null; wait $DPID 2>/dev/null; }; }
set -o noclobber
if ! { echo "F26c HPP-692 go_f26c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f26c.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_f26c.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
HS=$(python $G/hold_f26c.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); python $G/guard_f26c.py close user_session > /dev/null; log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, block closed"; exit 3; }
log "lock taken"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before: $(cat $OUT/installed_before.txt)"
release() { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; log "lock released ($1)"; }

# ---- mode base: manifest and copy of the series folders (item 630 (g)(4)) ----
if [ $MODE = base ]; then
  OK=1
  python $G/manifest_fs4c.py $BASE/base.tsv "${MF[@]}" > $OUT/manifest_base.txt 2>&1 || OK=0
  log "series base manifest: $(head -1 $OUT/manifest_base.txt | cut -c1-200)"
  TC="$EMU/_ShaderCache/PPSA21564"
  log "state of the base: pipelines.bin $( [ -f "$TC/pipelines.bin" ] && echo present || echo absent ), replay $( [ -d "$TC/replay" ] && echo present || echo absent ), variant_fixb26_fixb1b_fixf10_fixf19 $( [ -d "$TC/variant_fixb26_fixb1b_fixf10_fixf19" ] && echo present || echo absent )"
  for pair in "${MF[@]}"; do
    lab=${pair%%=*}; src=${pair#*=}
    [ -d "$src" ] || { log "$lab absent at the base (manifest line MISSING) - not copied"; continue; }
    cp -a "$src" "$BASE/copy_$lab" || { OK=0; log "copy of $lab failed"; }
  done
  python $G/manifest_fs4c.py $OUT/copy.tsv $(for pair in "${MF[@]}"; do lab=${pair%%=*}; echo "$lab=$BASE/copy_$lab"; done) > $OUT/manifest_copy.txt 2>&1
  python $G/manifest_fs4c.py --cmp $BASE/base.tsv $OUT/copy.tsv > $OUT/cmp_copy.txt 2>&1 || OK=0
  log "copy against the base manifest: $(head -1 $OUT/cmp_copy.txt)"
  sha "$GAME" > $OUT/installed_after.txt
  [ "$(cat $OUT/installed_after.txt)" = "$TB" ] || OK=0
  if [ $OK = 1 ]; then
    cp $BASE/base.tsv $G/state_last.tsv
    release "base ok"; exit 0
  fi
  rm -f $BASE/base.tsv; log "BASE FAILED - base manifest removed, the lock released"; release "base failed"; exit 1
fi

# ---- mode return: the copies back, manifest EQUAL to the base ----
if [ $MODE = return ]; then
  OK=1
  python $G/manifest_fs4c.py $OUT/manifest_end.tsv "${MF[@]}" > $OUT/manifest_end.txt 2>&1
  python $G/manifest_fs4c.py --cmp $BASE/base.tsv $OUT/manifest_end.tsv > $OUT/cmp_end_base.txt 2>&1
  log "end of the series against the base (row): $(head -3 $OUT/cmp_end_base.txt | tr '\n' ';' | cut -c1-300)"
  if ! python $G/manifest_fs4c.py --cmp $G/state_last.tsv $OUT/manifest_end.tsv > $OUT/cmp_end_last.txt 2>&1; then
    echo "$(u) the caches differ from the state after the last tag: $(head -1 $OUT/cmp_end_last.txt)" > $G/RETURN_HELD
    log "the caches differ from the state after the last tag (someone else changed them) - nothing returned, RETURN_HELD, question to the lead: $(head -1 $OUT/cmp_end_last.txt)"
    release "return held"; exit 1
  fi
  if [ $OK = 1 ]; then
    for pair in "${MF[@]}"; do
      lab=${pair%%=*}; live=${pair#*=}
      if [ -d "$BASE/copy_$lab" ]; then
        rm -rf "$live" && cp -a "$BASE/copy_$lab" "$live" || { OK=0; log "return of $lab FAILED"; }
      else
        [ -e "$live" ] && { rm -rf "$live" || OK=0; log "$lab was absent at the base - removed"; }
      fi
    done
    python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1
    python $G/manifest_fs4c.py --cmp $BASE/base.tsv $OUT/manifest_after.tsv > $OUT/cmp_after_base.txt 2>&1 || OK=0
    log "manifest after the return: $(head -1 $OUT/manifest_after.txt | cut -c1-200); against the base: $(head -1 $OUT/cmp_after_base.txt)"
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the series: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$TB" ] || OK=0
  if [ $OK = 1 ]; then echo "$(u)" > $G/RETURNED; release "return ok"; exit 0; fi
  echo "$(u) return" > $G/RETURN_FAILED; log "RETURN INCOMPLETE - the lock stays, question to the lead"; exit 1
fi

# ---- mode tag ----
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f26c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$TB" ] || { OK=0; log "INSTALLED BINARY IS NOT FS10 after the tag"; }
  if [ -e $OUT/USER_FOUND ] || [ -e $OUT/VM_FOUND ]; then
    log "user process or session during the tag - waiting for its exit, poll 10 s, the lock stays (item 534, 606)"
    python $G/guard_f26c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1 >> $OUT/wait_gone.txt
    python $G/hold_f26c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1 >> $OUT/wait_gone.txt
    echo "$(u) $T user process or session during the tag - the series caches may hold user files; question to the lead before the next tag and the return" > $G/SERIES_STOP
  fi
  if [ -f $OUT/manifest_before.tsv ]; then
    python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1 || OK=0
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
    log "manifest after: $(head -1 $OUT/manifest_after.txt | cut -c1-200); before vs after (row): $(head -1 $OUT/manifest_cmp.txt)"
    [ $OK = 1 ] && cp $OUT/manifest_after.tsv $G/state_last.tsv
  fi
  if [ $OK = 1 ]; then
    release "rc $RCX"
    DA=$(python $G/dispstate.py); DARC=$?
    echo "$DA" > $OUT/disp_after.txt
    stop_disp
    log "display after lock released (item 620 (g)(1)): $DA; hold: $(grep -c '^event ' $OUT/disp_hold.txt) display events, $(grep -c '^event .* OFF' $OUT/disp_hold.txt) OFF"
    python $G/hostload_f26c.py --json $OUT/hostload_after.json > $OUT/hostload_after.txt 2>&1
    log "host load after the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_after.txt | cut -c1-200)"
    [ -f $G/$T.json ] && python $G/f26c_read.py --set-load $G/$T.json $OUT > $OUT/set_load.txt 2>&1 && log "$(head -1 $OUT/set_load.txt)"
    if [ -e $OUT/USER_FOUND ] || [ -e $OUT/VM_FOUND ]; then
      python $G/guard_f26c.py close user_found > /dev/null
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag - block closed, interference (item 534), SERIES_STOP"
    elif [ ! -f $OUT/run.txt ] || ! grep -q -- '--- attempt 1: launching' $OUT/run.txt; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never launched the emulator - not a tag, repeat by the same name (item 534; seal 2)"
    fi
  else
    stop_disp
    echo "$(u) $T" > $G/RETURN_FAILED; log "installed binary or manifest after failed - the lock stays"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
python $G/manifest_fs4c.py --cmp $G/state_last.tsv $OUT/manifest_before.tsv > $OUT/state_cmp.txt 2>&1
SC=$?
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200); against the state after the previous call: $(head -1 $OUT/state_cmp.txt)"
if [ $SC != 0 ]; then
  echo "$(u) $T the caches changed between calls ($(head -1 $OUT/state_cmp.txt)) - question to the lead" > $G/SERIES_STOP
  log "the caches changed between calls - not starting, SERIES_STOP, question to the lead"
  rm -f $OUT/manifest_before.tsv; mv $OUT/run.txt $OUT/run.none 2>/dev/null; exit 1
fi
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, entry-at-level, timeout $TO, hold $H, harness form, no video, $KN)"
python $G/guard_f26c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_f26c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws 500 --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --entry-at-level --hold $H $KN > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f26c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
