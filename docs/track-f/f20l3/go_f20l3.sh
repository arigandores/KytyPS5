#!/bin/bash
# Track F link F20l3 (HPP-655; ROADMAP s122 item 591 (v), (g), (d), (zh)): one tag of the KYTY_DIAG_B32 series form - F20e (V Sky Garden,
# 330 s, KYTY_REC, caches returned) + KYTY_DIAG_B32 + KYTY_GPU_WALL=1 + M6 of the harness, on the F20j4 TEST binary 2d0c8815 (installed for
# the tag only, known by sha256; the installed S18 b3cee576 (item 590) is checked by its full sha256 before and returned from its pinned copy
# after).  ONE TAG = ONE LOCK.  Port of C:/kyty/f287/f20l2/go_f20l2.sh (stop file, lock, procload through the <app> mask, lock.log UTC,
# caches _ShaderCache (with replay/) / _ShaderSeeds / _PipelineCache / _SaveData and the driver GLCache copied before and returned after,
# manifest sha256 before / run / after with the equality line, RETURN_FAILED keeps the lock, guard of the user game item 534 - kill by pid).
# usage: bash C:/kyty/f287/f20l3/go_f20l3.sh <tag>
#   tags: b32_pa, b32_pa2 (PK-A, cold translation, item 591 (v)(1)-(3)); b32_s01..b32_s60 (series, item 591 (g)); b32_z0c1..b32_z0c5
#   (U5(1) base, KYTY_DIAG_B32=0, item 591 (d)(2)); repeats <tag>_r1.._r6 (interference, item 273 (z)).
#   FORM (seal pred/f20l3_seal.md): enter_scene.py <tag> --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480
#     --no-install --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#     KYTY_GPU_WALL=1 KYTY_DIAG_B32=<1|0>.  COLD (b32_pa, b32_pa2 only): after the copy of the caches reserve_f20l3.py moves the set of item
#     591 (v)(1) into runs/<tag>/reserve; the return of the whole _ShaderCache / _ShaderSeeds from the copy brings it back; the reserve is
#     checked against manifest_after and removed.  M6: m6_f20l3.py (foreign CPU once per 1 s; names only in m6_local.txt, the <app> form in
#     m6.txt).  No validation, no RenderDoc, no KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH, no stand, no loader; this script unsets KYTY_* and
#     VK_LAYER_* before the call.  ASCII only.
# EXIT: 0 tag made (read it with post_f20l3.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process; 4 stop file;
#   5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f20l3; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F20L3_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
S18=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a
TB=2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7
BIN=$F/bin/kyty_emulator_2d0c8815.exe
PINNED=C:/kyty/s288/bin/kyty_emulator_b3cee576.exe
SEAL=$G/pred/f20l3_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
LV=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  b32_pa|b32_pa2|b32_s[0-5][0-9]|b32_s60|b32_z0c[1-5]) ;;
  b32_pa_r[1-6]|b32_pa2_r[1-6]|b32_s[0-5][0-9]_r[1-6]|b32_s60_r[1-6]|b32_z0c[1-5]_r[1-6]) ;;
  *) echo "usage: go_f20l3.sh b32_pa|b32_pa2|b32_s01..b32_s60|b32_z0c1..b32_z0c5[_r1..6]"; exit 2;;
esac
B=${T%_r[1-6]}
[ "$B" = b32_s00 ] && { echo "usage: b32_s00 is not a tag"; exit 2; }
COLD=0
case "$B" in
  b32_pa|b32_pa2) KN="KYTY_DIAG_B32=1"; COLD=1;;
  b32_s*) KN="KYTY_DIAG_B32=1";;
  b32_z0c*) KN="KYTY_DIAG_B32=0";;
esac
[ "${F20L3_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B knobs $KN cold $COLD"; exit 0; }
SD=300; H=330
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F20l3 go_f20l3 $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "test binary copy $BIN is not 2d0c8815 - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$S18" ] || { log "pinned S18 copy $PINNED is not b3cee576 - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$S18" ] || { log "installed binary $WANT is not S18 b3cee576 - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
GS=$(python $G/guard_f20l3.py scan) || { python $G/guard_f20l3.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
# item 587 (g) debt: the run that launched this detached call must still be going (a cancelled run does not stop its detached children)
RS=$(python $G/runchk_f20l3.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
set -o noclobber
if ! { echo "F20l3 HPP-655 go_f20l3.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f20l3.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_f20l3.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
finish() {
  RCX=$?
  OK=1
  touch $OUT/m6.stop 2>/dev/null
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f20l3.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS=$(python $G/guard_f20l3.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f20l3.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
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
    [ $MC = 0 ] || OK=0
  fi
  if [ -f $OUT/reserve/reserve.tsv ]; then
    python $G/reserve_f20l3.py check $OUT/reserve/reserve.tsv $OUT/manifest_after.tsv > $OUT/reserve_check.txt 2>&1
    RC=$?
    log "cold reserve against manifest after: $(head -1 $OUT/reserve_check.txt)"
    if [ $RC = 0 ] && [ $OK = 1 ]; then
      cp $OUT/reserve/reserve.tsv $OUT/reserve.tsv && rm -rf $OUT/reserve && log "cold reserve removed (its list kept as runs/$T/reserve.tsv)"
    else
      OK=0
    fi
  fi
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; log "lock released (rc $RCX)"
    if [ -e $OUT/USER_FOUND ]; then
      UF=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_f20l3.py close user_found > /dev/null
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF) - block closed, interference, repeat by the same name (item 534)"
    elif [ ! -f $OUT/run.txt ]; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never started - interference, repeat by the same name (item 534)"
    fi
  else
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete, installed binary, manifest or cold reserve differs - the lock stays"; RCX=1
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
if [ $COLD = 1 ]; then
  case " $COPIED " in *" _ShaderCache "*) ;; *) log "cold form: _ShaderCache was not copied - not starting"; exit 1;; esac
  case " $COPIED " in *" _ShaderSeeds "*) ;; *) log "cold form: _ShaderSeeds was not copied - not starting"; exit 1;; esac
  python $G/reserve_f20l3.py move "$EMU" $OUT/reserve > $OUT/reserve_move.txt 2>&1 || { log "cold form: $(head -1 $OUT/reserve_move.txt) - not starting"; exit 1; }
  log "cold form (item 591 (v)(1)): $(head -1 $OUT/reserve_move.txt | cut -c1-200)"
  python $G/reserve_f20l3.py cold "$EMU" > $OUT/reserve_cold.txt 2>&1 || { log "cold form: $(head -1 $OUT/reserve_cold.txt) - not starting"; exit 1; }
  log "cold form: $(head -1 $OUT/reserve_cold.txt)"
fi
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the F20j4 test copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the F20j4 test copy for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, --rec, hold $H, $KN, KYTY_GPU_WALL=1, cold $COLD, M6)"
python $G/guard_f20l3.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/m6_f20l3.py --pidfile $OUT/game_pid.txt --local $OUT/m6_local.txt --out $OUT/m6.txt --stop $OUT/m6.stop --loadpids $OUT/load_pids.txt > $OUT/m6_run.txt 2>&1 &
MPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --rec --hold $H KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 $KN > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop $OUT/m6.stop; wait $WPID; wait $MPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); M6: $(tail -1 $OUT/m6.txt 2>/dev/null | cut -c1-160)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f20l3.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
