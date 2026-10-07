#!/bin/bash
# Track F link F25f (HPP-669; ROADMAP s122 item 596 (g)-(z) with item 599 (b)(2), (5)-(7), item 600 (b)(4), item 602): one tag of the
# B36 / B40 series - V of the level 330 s (-lvl pot_treasure_cave / -lvl bonus_path_maker_mix), KYTY_REC, harness constants,
# KYTY_GPU_HANG_ABORT_S=22, KYTY_DIAG_B32=<1|0>, KYTY_GPU_WALL=1, M6 of the harness with emu_t and the calibration poller, on the TEST binary
# B e342b839 (installed for the tag only, known by sha256; the installed S18 b3cee576 (item 590) is checked by its full sha256 before and
# returned from its pinned copy after).  ONE TAG = ONE LOCK.  Port of C:/kyty/f287/f20l3/go_f20l3.sh (stop file, lock, procload through the
# <app> mask, lock.log UTC, the five folders of the cache manifest copied before and returned after, RETURN_FAILED keeps the lock, guard of
# the user game item 534 - kill by pid) with the snapshots of item 596 (g), 599 (b)(6) (snap_f25f.py, under this lock):
#   f25_c1          snapshot A is taken before it (first call) or restored (a repeat); NO return; snapshot C1 taken after it
#   f25_c2          snapshot C1 restored before it; NO return; snapshot B taken after it
#   f25_z1/z2/pb/pc, f25_sNN   caches before = B (snap_cmp); copy before, return after (= B)
#   f25_kNN         snapshot A restored before it (cold = A with GLCache); caches before = A; copy before, return after (= A)
#   restoreA        (not a tag) the end of the series: snapshot A restored, live manifest = A (EQUAL), item 596 (g)
# usage: bash C:/kyty/f287/f25f/go_f25f.sh <tag> [pot|bonus]   (the level is fixed for c1 z1 pb = pot, c2 z2 pc = bonus; required for s, k)
#        bash C:/kyty/f287/f25f/go_f25f.sh restoreA
# EXIT: 0 tag made (read it with post_f25f.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process; 4 stop
#   file; 5 procload busy.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f25f; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F25F_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
S18=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a
TB=e342b839d74d5689bc4f66ee0ed04a37e9a640e60a199a2882c8e83ecf19cfa4
BIN=$F/f25d/kyty_emulator_e342b839.exe
PINNED=C:/kyty/s288/bin/kyty_emulator_b3cee576.exe
SEAL=$G/pred/f25f_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}; LA=${2:-}
TIMES=$F/times.txt
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
if [ "$T" = restoreA ]; then
  log() { echo "$(u) F25f go_f25f restoreA $*" | tee -a $TIMES; }
  [ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
  [ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
  [ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
  [ -d $G/snap/A ] || { log "no snapshot A - nothing to restore"; exit 1; }
  [ "$(sha "$GAME")" = "$S18" ] || { log "installed binary is not S18 - not restoring (question to the lead)"; exit 1; }
  GS=$(python $G/guard_f25f.py scan) || { log "user emulator or launcher lives - not restoring: $GS"; exit 3; }
  set -o noclobber
  if ! { echo "F25f HPP-669 go_f25f.sh restoreA pid $$ $(u)" > $LOCK; } 2>/dev/null; then set +o noclobber; echo "lock taken by someone else"; exit 3; fi
  set +o noclobber
  echo "lock taken restoreA $(u)" >> $G/runs/lock.log
  mkdir -p $G/runs/restoreA
  python $G/snap_f25f.py restore A > $G/runs/restoreA/restore.txt 2>&1; RC=$?
  log "restore A: $(head -1 $G/runs/restoreA/restore.txt)"
  python $G/manifest_fs4c.py $G/runs/restoreA/manifest_after.tsv "${MF[@]}" > $G/runs/restoreA/manifest_after.txt 2>&1
  python $G/manifest_fs4c.py --cmp $G/snap/A.tsv $G/runs/restoreA/manifest_after.tsv > $G/runs/restoreA/manifest_cmp.txt 2>&1; MC=$?
  log "live manifest against A: $(head -1 $G/runs/restoreA/manifest_cmp.txt)"
  sha "$GAME" > $G/runs/restoreA/installed_after.txt
  if [ $RC = 0 ] && [ $MC = 0 ] && [ "$(cat $G/runs/restoreA/installed_after.txt)" = "$S18" ]; then
    rm -f $LOCK; echo "lock released restoreA $(u)" >> $G/runs/lock.log; log "lock released - caches = A, installed S18"; exit 0
  fi
  echo "$(u) restoreA" > $G/RETURN_FAILED; log "restore A incomplete - the lock stays"; exit 1
fi
case "$T" in
  f25_c[12]|f25_z[12]|f25_p[bc]|f25_s0[1-9]|f25_s[1-3][0-9]|f25_s40|f25_k0[1-9]|f25_k10) ;;
  f25_c[12]_r[1-6]|f25_z[12]_r[1-6]|f25_p[bc]_r[1-6]|f25_s0[1-9]_r[1-6]|f25_s[1-3][0-9]_r[1-6]|f25_s40_r[1-6]|f25_k0[1-9]_r[1-6]|f25_k10_r[1-6]) ;;
  *) echo "usage: go_f25f.sh f25_c1|f25_c2|f25_z1|f25_z2|f25_pb|f25_pc|f25_s01..f25_s40|f25_k01..f25_k10[_r1..6] [pot|bonus] | restoreA"; exit 2;;
esac
B=${T%_r[1-6]}
case "$B" in
  f25_c1|f25_z1|f25_pb) LV=pot_treasure_cave;;
  f25_c2|f25_z2|f25_pc) LV=bonus_path_maker_mix;;
  *) case "$LA" in pot) LV=pot_treasure_cave;; bonus) LV=bonus_path_maker_mix;; *) echo "usage: $B needs the level pot|bonus"; exit 2;; esac;;
esac
case "$B" in
  f25_c1) KN="KYTY_DIAG_B32=1"; PRE=A; EXP=A; NORET=1; TAKE=C1;;
  f25_c2) KN="KYTY_DIAG_B32=1"; PRE=C1; EXP=C1; NORET=1; TAKE=B;;
  f25_z*) KN="KYTY_DIAG_B32=0"; PRE=; EXP=B; NORET=0; TAKE=;;
  f25_pb) KN="KYTY_DIAG_B32=1 KYTY_TEST_B32=60:present:3000"; PRE=; EXP=B; NORET=0; TAKE=;;
  f25_pc) KN="KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:6000"; PRE=; EXP=B; NORET=0; TAKE=;;
  f25_s*) KN="KYTY_DIAG_B32=1"; PRE=; EXP=B; NORET=0; TAKE=;;
  f25_k*) KN="KYTY_DIAG_B32=1"; PRE=A; EXP=A; NORET=0; TAKE=;;
esac
[ "${F25F_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B level $LV knobs $KN pre ${PRE:--} exp $EXP noret $NORET take ${TAKE:--}"; exit 0; }
SD=300; H=330
OUT=$G/runs/$T; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
log() { echo "$(u) F25f go_f25f $T $*" | tee -a $TIMES; }
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "test binary copy $BIN is not e342b839 - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$S18" ] || { log "pinned S18 copy $PINNED is not b3cee576 - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$S18" ] || { log "installed binary $WANT is not S18 b3cee576 - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
if [ "$PRE" = C1 ] && [ ! -f $G/snap/C1.tsv ]; then log "no snapshot C1 (f25_c1 first) - not starting"; exit 1; fi
if [ "$EXP" = B ] && [ ! -f $G/snap/B.tsv ]; then log "no snapshot B (f25_c2 first) - not starting"; exit 1; fi
if [ "$EXP" = A ] && [ "$B" != f25_c1 ] && [ ! -f $G/snap/A.tsv ]; then log "no snapshot A - not starting"; exit 1; fi
GS=$(python $G/guard_f25f.py scan) || { python $G/guard_f25f.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_f25f.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
set -o noclobber
if ! { echo "F25f HPP-669 go_f25f.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f25f.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_f25f.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
log "lock taken; level $LV; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
SNAPOK=1
BROKEN=0
finish() {
  RCX=$?
  OK=1
  [ $BROKEN = 1 ] && OK=0
  touch $OUT/m6.stop 2>/dev/null
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f25f.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ] || [ $NORET = 1 ]; then
    GS=$(python $G/guard_f25f.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f25f.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
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
    [ $OK = 1 ] && log "caches, seeds, saves and GLCache returned"
  fi
  if [ -f $OUT/manifest_before.tsv ]; then
    python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
    MC=$?
    log "manifest after: $(head -1 $OUT/manifest_after.txt | cut -c1-200); cmp: $(head -1 $OUT/manifest_cmp.txt)"
    if [ $NORET = 1 ]; then
      if [ -f $OUT/run.txt ] && [ $SNAPOK = 1 ]; then
        python $G/snap_f25f.py take $TAKE --replace > $OUT/snap_take.txt 2>&1 || OK=0
        echo "NO RETURN (prewarm, item 596 (g)): snapshot $TAKE $(head -1 $OUT/snap_take.txt)" > $OUT/noreturn.txt
        log "$(cat $OUT/noreturn.txt)"
      fi
    else
      [ $MC = 0 ] || OK=0
    fi
  fi
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; log "lock released (rc $RCX)"
    if [ -e $OUT/USER_FOUND ]; then
      UF=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_f25f.py close user_found > /dev/null
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF) - block closed, interference, repeat by the same name (item 534)"
    elif [ ! -f $OUT/run.txt ]; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never started - not a tag, repeat by the same name (item 534)"
    fi
  else
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete, installed binary, manifest or snapshot differs - the lock stays"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
if [ "$PRE" = A ] && [ ! -d $G/snap/A ]; then
  python $G/snap_f25f.py take A > $OUT/snap_pre.txt 2>&1 || { SNAPOK=0; log "snapshot A: $(head -1 $OUT/snap_pre.txt) - not starting"; exit 1; }
  log "snapshot A taken before the first tag (item 596 (g)): $(head -1 $OUT/snap_pre.txt)"
elif [ -n "$PRE" ]; then
  python $G/snap_f25f.py restore $PRE > $OUT/snap_pre.txt 2>&1 || { SNAPOK=0; BROKEN=1; log "restore $PRE: $(head -1 $OUT/snap_pre.txt) - not starting"; exit 1; }
  log "snapshot $PRE restored before the tag: $(head -1 $OUT/snap_pre.txt)"
fi
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; SNAPOK=0; rm -f $OUT/manifest_before.tsv; exit 1; }
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
python $G/manifest_fs4c.py --cmp $G/snap/$EXP.tsv $OUT/manifest_before.tsv > $OUT/snap_cmp.txt 2>&1 || { SNAPOK=0; log "caches before are not snapshot $EXP: $(head -1 $OUT/snap_cmp.txt) - not starting (question to the lead)"; exit 1; }
log "caches before = snapshot $EXP: $(head -1 $OUT/snap_cmp.txt)"
if [ $NORET = 0 ]; then
  for d in $DIRS GLCache; do
    if [ "$d" = "GLCache" ]; then SRC="$GLDIR"; else SRC="$EMU/$d"; fi
    [ -d "$SRC" ] || { log "$d absent - not copied (manifest line MISSING)"; continue; }
    cp -a "$SRC" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
    COPIED="$COPIED $d"
  done
  log "caches, seeds, saves and GLCache copied:$COPIED ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
fi
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the binary B copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the binary B copy for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, --rec, hold $H, $KN, KYTY_GPU_WALL=1, KYTY_GPU_HANG_ABORT_S=22, M6 + calibration poller)"
python $G/guard_f25f.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/m6_f25f.py --pidfile $OUT/game_pid.txt --local $OUT/m6_local.txt --out $OUT/m6.txt --cal $OUT/cal.txt --stop $OUT/m6.stop --loadpids $OUT/load_pids.txt > $OUT/m6_run.txt 2>&1 &
MPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --rec --hold $H KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22 $KN > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop $OUT/m6.stop; wait $WPID; wait $MPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); M6: $(tail -1 $OUT/m6.txt 2>/dev/null | cut -c1-160)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f25f.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
