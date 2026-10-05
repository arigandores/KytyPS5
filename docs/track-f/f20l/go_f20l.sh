#!/bin/bash
# Track F link F20l (HPP-631; ROADMAP s122 item 550 (d), (z); item 552 (d), item 554 (d)): one KYTY_DIAG_B32 control tag of the form of
# F20e (V Sky Garden, 330 s, KYTY_REC, caches returned) + KYTY_GPU_WALL=1 + M6 of the harness, on the F20j2 TEST binary b9e0ee00
# (installed for the tag only, known by sha256; the installed FS8 2c9b69b9 is checked before and returned from its pinned copy after,
# the form of F19e go_f19e.sh).  ONE TAG = ONE LOCK.  Port of C:/kyty/f287/f20e/go_f20e.sh (stop file, lock, procload through the <app>
# mask, lock.log UTC, caches _ShaderCache / _PipelineCache / _SaveData and the driver GLCache copied before and returned after, manifest
# sha256 before / run / after with the equality line, RETURN_FAILED keeps the lock, guard of the user game item 534 - kill by pid only).
# usage: bash C:/kyty/f287/f20l/go_f20l.sh <tag>   tags: b32_z0 b32_pp b32_pc b32_pd b32_pd2, repeats <tag>_r1.._r6 (item 550 (z)(4))
#   FORM (seal pred/f20l_seal.md): enter_scene.py <tag> --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480
#     --no-install --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#     KYTY_GPU_WALL=1 KYTY_DIAG_B32=<0|1> [KYTY_TEST_B32=60:present:200 | 60:gpusleep:200].  b32_pd / b32_pd2: the harness loader
#     b32_load.py (all / ceil(ncpu/2) busy processes, ABOVE_NORMAL priority class, 400 ms at 60 s after the first level line).  M6: m6_f20l.py
#     (foreign CPU once per 1 s; names only in the local file m6_local.txt, the <app> form in m6.txt).  No validation, no RenderDoc, no
#     KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH; this script unsets KYTY_* and VK_LAYER_* before the call.  ASCII only.
# EXIT: 0 tag made (read it with post_f20l.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process; 4 stop file;
#   5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f20l; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F20L_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b
TB=b9e0ee0092ca1504979ebd674abb21c8d67015fd030bc33615eb2c87acb90f91
BIN=$F/bin/kyty_emulator_b9e0ee00.exe
PINNED=$F/bin/kyty_emulator_2c9b69b9.exe
SEAL=$G/pred/f20l_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
LV=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  b32_z0|b32_pp|b32_pc|b32_pd|b32_pd2|b32_z0_r[1-6]|b32_pp_r[1-6]|b32_pc_r[1-6]|b32_pd_r[1-6]|b32_pd2_r[1-6]) ;;
  *) echo "usage: go_f20l.sh b32_z0|b32_pp|b32_pc|b32_pd|b32_pd2[_r1..6]"; exit 2;;
esac
B=${T%_r[1-6]}
LOADMODE=""
case "$B" in
  b32_z0) KN="KYTY_DIAG_B32=0";;
  b32_pp) KN="KYTY_DIAG_B32=1 KYTY_TEST_B32=60:present:200";;
  b32_pc) KN="KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:200";;
  b32_pd) KN="KYTY_DIAG_B32=1"; LOADMODE=all;;
  b32_pd2) KN="KYTY_DIAG_B32=1"; LOADMODE=half;;
esac
[ "${F20L_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B knobs $KN loader ${LOADMODE:-none}"; exit 0; }
SD=300; H=330
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F20l go_f20l $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "test binary copy $BIN is not b9e0ee00 - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$FS8" ] || { log "pinned FS8 copy $PINNED is not 2c9b69b9 - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$FS8" ] || { log "installed binary $WANT is not FS8 2c9b69b9 - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
GS=$(python $G/guard_f20l.py scan) || { python $G/guard_f20l.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F20l HPP-631 go_f20l.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f20l.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_f20l.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
finish() {
  RCX=$?
  OK=1
  touch $OUT/m6.stop $OUT/load.stop 2>/dev/null
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f20l.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS=$(python $G/guard_f20l.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f20l.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ $INSTALLED = 1 ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$FS8" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$FS8" ]; then log "installed binary returned from the pinned FS8 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$FS8" ] || { OK=0; log "INSTALLED BINARY IS NOT FS8 after the tag"; }
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
    [ $OK = 1 ] && log "caches, saves and GLCache returned"
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
      UF=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_f20l.py close user_found > /dev/null
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
log "caches, saves and GLCache copied:$COPIED ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the F20j2 test copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the F20j2 test copy for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, --rec, hold $H, $KN, KYTY_GPU_WALL=1, loader ${LOADMODE:-none}, M6)"
python $G/guard_f20l.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/m6_f20l.py --pidfile $OUT/game_pid.txt --local $OUT/m6_local.txt --out $OUT/m6.txt --stop $OUT/m6.stop --loadpids $OUT/load_pids.txt > $OUT/m6_run.txt 2>&1 &
MPID=$!
LPID=""
if [ -n "$LOADMODE" ]; then
  python $G/b32_load.py --mode $LOADMODE --pidfile $OUT/game_pid.txt --log "$EMU/_kyty.txt" --out $OUT/load.json --pids $OUT/load_pids.txt --stop $OUT/load.stop > $OUT/load_run.txt 2>&1 &
  LPID=$!
fi
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --rec --hold $H KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 $KN > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop $OUT/m6.stop $OUT/load.stop; wait $WPID; wait $MPID; [ -n "$LPID" ] && wait $LPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); M6: $(tail -1 $OUT/m6.txt 2>/dev/null | cut -c1-160); loader: $(tail -1 $OUT/load_run.txt 2>/dev/null | cut -c1-160)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f20l.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
