#!/bin/bash
# Track F link F25m (HPP-680; ROADMAP s122 item 613 (g)(3)-(5), (e), (z)(2) with items 615 (b)(1), (2), (6), 616 (b)(1), (2), (4), (g),
# 618 (b)(5), (v), 619 (b)(1), (g)): one tag of the KYTY_FIX_B36 series on the TEST binary T2 9745eb78 (FS9 11164d72 + 6 F25 commits + 3 F25k
# + F25k2 5064c5bb, worktree 0c8fcba2; installed for the tag only, known by sha256); the installed FS9 3861eeea (item 610) is checked by its
# full sha256 before and returned from its pinned copy after.  ONE TAG = ONE LOCK.  Port of C:/kyty/f287/f25f/go_f25f.sh (stop file, lock,
# procload through the <app> mask, lock.log UTC, the five folders of the cache manifest copied before and returned after, RETURN_FAILED keeps
# the lock, guard of the user game item 534 - kill by pid, the user session item 606 - hold_f25m.py, reconcile of the snapshots A' / B').
# The snapshots A and B are the F25f ones (copied into C:/kyty/f287/f25m/snap before the first tag; B = warm pot / bonus / Sky Garden, A =
# cold with GLCache, item 596 (g)); here every tag restores its snapshot before when snap/STATE differs (a cold tag - always, item 613 (g)(4)
# 'the return of snapshot A before every tag'), copies the five folders, returns them after (= the snapshot), so the state stays.
#   b36_s0 / b36_s1   user form (--user-form: no KYTY_FRAME_TRACE, no KYTY_DIAG_B32, no gate files, no KYTY_QUEUE_TRACE, no
#                     KYTY_GPU_HANG_ABORT_S, no video), pot_treasure_cave, KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3
#                     KYTY_FIX_B36=0 / 1, hold 150 s, warm (B)
#   b36_f0 / b36_f1   harness form (KYTY_FRAME_TRACE=lite of enter_scene, KYTY_DIAG_B32=1, KYTY_GPU_WALL=1, KYTY_GPU_HANG_ABORT_S=22, video,
#                     clock pin, M6), pot, KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3 KYTY_FIX_B36=0 / 1, hold 150 s, warm (B)
#   b36_k01..b36_k13  cold form f25_k: KYTY_DIAG_B32=1 KYTY_FIX_B36=1, KYTY_GPU_WALL=1, KYTY_GPU_HANG_ABORT_S=22, video, hold 330 s,
#                     snapshot A restored before; level fixed by the name: pot k01 k03 k05 k07 k09 k11 k12 k13, bonus k02 k04 k06 k08 k10
#   b36_v             V Sky Garden (form fs9_v of FS9c) + KYTY_FIX_B36=1, hold 330 s, video, warm (B)
#   b36_w             W Sky Garden (form fs9_w of FS9c, item 295 (b)) + KYTY_FIX_B36=1, hold 310 s, warm (B)
#   restoreA          (not a tag) the end of the series: snapshot A restored, live manifest = A' (EQUAL), installed FS9 (item 613 (g)(5))
# usage: bash C:/kyty/f287/f25m/go_f25m.sh <tag>[_r1.._r3] | restoreA
# EXIT: 0 tag made (read it with post_f25m.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process; 4 stop
#   file; 5 procload busy.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f25m; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F25M_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
FS9=3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5
TB=9745eb7851d541740ce9730b86258f7bb26cab270f0d35434d43037c5cefd885
BIN=$F/f25k2/kyty_emulator_9745eb78.exe
PINNED=$F/bin/kyty_emulator_3861eeea.exe
SEAL=$G/pred/f25m_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
TIMES=$F/times.txt
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
if [ "$T" = restoreA ]; then
  log() { echo "$(u) F25m go_f25m restoreA $*" | tee -a $TIMES; }
  [ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
  [ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
  [ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
  [ -d $G/snap/A ] || { log "no snapshot A - nothing to restore"; exit 1; }
  [ -e $G/runs/restoreA ] && { echo "$G/runs/restoreA exists - restoreA runs once (a repeat by the lead)"; exit 2; }
  [ "$(sha "$GAME")" = "$FS9" ] || { log "installed binary is not FS9 - not restoring (question to the lead)"; exit 1; }
  GS=$(python $G/guard_f25m.py scan) || { log "user emulator or launcher lives - not restoring: $GS"; exit 3; }
  HS=$(python $G/hold_f25m.py check) || { python $G/guard_f25m.py close user_session > /dev/null; log "user session (item 606 (v)(1)): $HS - not restoring, block closed"; exit 3; }
  set -o noclobber
  if ! { echo "F25m HPP-680 go_f25m.sh restoreA pid $$ $(u)" > $LOCK; } 2>/dev/null; then set +o noclobber; echo "lock taken by someone else"; exit 3; fi
  set +o noclobber
  echo "lock taken restoreA $(u)" >> $G/runs/lock.log
  mkdir -p $G/runs/restoreA
  HS=$(python $G/hold_f25m.py check) || { rm -f $LOCK; echo "lock released restoreA $(u)" >> $G/runs/lock.log; log "user session right after the lock: $HS - lock released, nothing touched"; exit 3; }
  python $G/snap_f25m.py reconcile > $G/runs/restoreA/reconcile.txt 2>&1; RR=$?
  log "reconcile before restore A' (item 606): $(head -1 $G/runs/restoreA/reconcile.txt)"
  if [ $RR != 0 ]; then rm -f $LOCK; echo "lock released restoreA $(u)" >> $G/runs/lock.log; echo "$(u) restoreA reconcile rc $RR" > $G/SERIES_STOP; log "reconcile rc $RR - nothing restored, lock released, SERIES_STOP (question to the lead)"; exit 1; fi
  python $G/snap_f25m.py restore A > $G/runs/restoreA/restore.txt 2>&1; RC=$?
  python $G/snap_f25m.py state A > /dev/null
  log "restore A: $(head -1 $G/runs/restoreA/restore.txt)"
  python $G/manifest_fs4c.py $G/runs/restoreA/manifest_after.tsv "${MF[@]}" > $G/runs/restoreA/manifest_after.txt 2>&1
  python $G/manifest_fs4c.py --cmp $G/snap/A.tsv $G/runs/restoreA/manifest_after.tsv > $G/runs/restoreA/manifest_cmp.txt 2>&1; MC=$?
  log "live manifest against A': $(head -1 $G/runs/restoreA/manifest_cmp.txt)"
  sha "$GAME" > $G/runs/restoreA/installed_after.txt
  if [ $RC = 0 ] && [ $MC = 0 ] && [ "$(cat $G/runs/restoreA/installed_after.txt)" = "$FS9" ]; then
    rm -f $LOCK; echo "lock released restoreA $(u)" >> $G/runs/lock.log; log "lock released - caches = A', installed FS9"; exit 0
  fi
  echo "$(u) restoreA" > $G/RETURN_FAILED; log "restore A incomplete - the lock stays"; exit 1
fi
case "$T" in
  b36_s[01]|b36_f[01]|b36_k0[1-9]|b36_k1[0-3]|b36_v|b36_w) ;;
  b36_s[01]_r[1-3]|b36_f[01]_r[1-3]|b36_k0[1-9]_r[1-3]|b36_k1[0-3]_r[1-3]|b36_v_r[1-3]|b36_w_r[1-3]) ;;
  *) echo "usage: go_f25m.sh b36_s0|b36_s1|b36_f0|b36_f1|b36_k01..b36_k13|b36_v|b36_w[_r1..3] | restoreA"; exit 2;;
esac
B=${T%_r[1-3]}
POT=pot_treasure_cave; BON=bonus_path_maker_mix; SKY=underwater_aerial_garden
STAND="KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3"
HARN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22"
case "$B" in
  b36_s0) LV=$POT; PRE=B; UF="--user-form"; SD=300; H=150; TO=480; REC=""; KN="$STAND KYTY_FIX_B36=0";;
  b36_s1) LV=$POT; PRE=B; UF="--user-form"; SD=300; H=150; TO=480; REC=""; KN="$STAND KYTY_FIX_B36=1";;
  b36_f0) LV=$POT; PRE=B; UF=""; SD=300; H=150; TO=480; REC="--rec"; KN="$HARN KYTY_DIAG_B32=1 $STAND KYTY_FIX_B36=0";;
  b36_f1) LV=$POT; PRE=B; UF=""; SD=300; H=150; TO=480; REC="--rec"; KN="$HARN KYTY_DIAG_B32=1 $STAND KYTY_FIX_B36=1";;
  b36_k01|b36_k03|b36_k05|b36_k07|b36_k09|b36_k11|b36_k12|b36_k13) LV=$POT; PRE=A; UF=""; SD=300; H=330; TO=480; REC="--rec"; KN="$HARN KYTY_DIAG_B32=1 KYTY_FIX_B36=1";;
  b36_k02|b36_k04|b36_k06|b36_k08|b36_k10) LV=$BON; PRE=A; UF=""; SD=300; H=330; TO=480; REC="--rec"; KN="$HARN KYTY_DIAG_B32=1 KYTY_FIX_B36=1";;
  b36_v) LV=$SKY; PRE=B; UF=""; SD=300; H=330; TO=480; REC="--rec"; KN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_FIX_B36=1";;
  b36_w) LV=$SKY; PRE=B; UF=""; SD=100; H=310; TO=900; REC="--emu-arg=--vulkan-validation --emu-arg=true"
         KN="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_FIX_B36=1";;
esac
[ "${F25M_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B level $LV pre $PRE uf ${UF:--} sd $SD hold $H timeout $TO rec ${REC:--} knobs $KN"; exit 0; }
OUT=$G/runs/$T; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
log() { echo "$(u) F25m go_f25m $T $*" | tee -a $TIMES; }
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "test binary copy $BIN is not T2 9745eb78 - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$FS9" ] || { log "pinned FS9 copy $PINNED is not 3861eeea - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$FS9" ] || { log "installed binary $WANT is not FS9 3861eeea - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
[ -f $G/snap/$PRE.tsv ] && [ -d $G/snap/$PRE ] || { log "no snapshot $PRE - not starting"; exit 1; }
GS=$(python $G/guard_f25m.py scan) || { python $G/guard_f25m.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
HS=$(python $G/hold_f25m.py check) || { python $G/guard_f25m.py close user_session > /dev/null; log "user session (item 606 (v)(1)): $HS - not starting, block closed"; exit 3; }
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_f25m.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
set -o noclobber
if ! { echo "F25m HPP-680 go_f25m.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f25m.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_f25m.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
HS=$(python $G/hold_f25m.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.session_$(date -u +%H%M%S); python $G/guard_f25m.py close user_session > /dev/null; log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, block closed"; exit 3; }
log "lock taken; level $LV; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
SNAPOK=1
finish() {
  RCX=$?
  OK=1
  touch $OUT/m6.stop 2>/dev/null
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f25m.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS=$(python $G/guard_f25m.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f25m.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ -e $OUT/VM_FOUND ]; then
    log "user VM during the tag ($(head -1 $OUT/VM_FOUND | cut -c1-120)) - caches wait for its exit, poll 10 s, the lock stays (item 606 (v)(1))"
    log "$(python $G/hold_f25m.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
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
      MR=$(python $G/snap_f25m.py merge-return GLCache "$OUT/before_$d" "$LIVE") || { OK=0; log "merge return of GLCache FAILED"; }
      log "GLCache returned by merge (item 606 (v)(3)): $MR"; continue
    fi
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
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; log "lock released (rc $RCX)"
    [ -e $OUT/VM_FOUND ] && [ ! -e $OUT/USER_FOUND ] && cp $OUT/VM_FOUND $OUT/USER_FOUND
    if [ -e $OUT/USER_FOUND ]; then
      UF2=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_f25m.py close user_found > /dev/null
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF2) - block closed, interference, repeat by the lead (item 534)"
    elif [ ! -f $OUT/run.txt ]; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never started - not a tag, repeat by the same name (item 534)"
    fi
  else
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete, installed binary or manifest differs - the lock stays"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
python $G/snap_f25m.py reconcile > $OUT/reconcile.txt 2>&1; RR=$?
log "reconcile (item 606 (v)(2)-(5)): $(head -1 $OUT/reconcile.txt | cut -c1-220)"
if [ $RR != 0 ]; then SNAPOK=0; echo "$(u) $T reconcile rc $RR: $(head -1 $OUT/reconcile.txt | cut -c1-160)" > $G/SERIES_STOP; log "reconcile rc $RR - nothing touched, SERIES_STOP (item 606 (v)(4)-(5)); not starting"; exit 1; fi
ST=$(cat $G/snap/STATE 2>/dev/null | tr -d '\r\n ')
if [ "$PRE" = A ] || [ "$ST" != "$PRE" ]; then
  python $G/snap_f25m.py restore $PRE > $OUT/snap_pre.txt 2>&1 || { SNAPOK=0; python $G/snap_f25m.py state X > /dev/null; log "restore $PRE: $(head -1 $OUT/snap_pre.txt) - not starting, snap/STATE X (question to the lead)"; exit 1; }
  python $G/snap_f25m.py state $PRE > /dev/null
  log "snapshot $PRE restored before the tag (state was $ST): $(head -1 $OUT/snap_pre.txt)"
else
  echo "state $ST = $PRE - no restore" > $OUT/snap_pre.txt
  log "snap/STATE $ST = $PRE - no restore (the return after the last tag gave $PRE)"
fi
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; SNAPOK=0; rm -f $OUT/manifest_before.tsv; exit 1; }
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
python $G/manifest_fs4c.py --cmp $G/snap/$PRE.tsv $OUT/manifest_before.tsv > $OUT/snap_cmp.txt 2>&1 || { SNAPOK=0; log "caches before are not snapshot $PRE: $(head -1 $OUT/snap_cmp.txt) - not starting (question to the lead)"; exit 1; }
log "caches before = snapshot $PRE: $(head -1 $OUT/snap_cmp.txt)"
for d in $DIRS GLCache; do
  if [ "$d" = "GLCache" ]; then SRC="$GLDIR"; else SRC="$EMU/$d"; fi
  [ -d "$SRC" ] || { log "$d absent - not copied (manifest line MISSING)"; continue; }
  cp -a "$SRC" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
  COPIED="$COPIED $d"
done
log "caches, seeds, saves and GLCache copied:$COPIED ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the binary T2 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the binary T2 copy for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, hold $H, ${UF:-harness form} ${REC:-no video}, $KN, M6 + calibration poller)"
python $G/guard_f25m.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_f25m.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
python $G/m6_f25m.py --pidfile $OUT/game_pid.txt --local $OUT/m6_local.txt --out $OUT/m6.txt --cal $OUT/cal.txt --stop $OUT/m6.stop --loadpids $OUT/load_pids.txt > $OUT/m6_run.txt 2>&1 &
MPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL $UF $REC --hold $H $KN > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop $OUT/m6.stop; wait $WPID; wait $HPID; wait $MPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); M6: $(tail -1 $OUT/m6.txt 2>/dev/null | cut -c1-160)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f25m.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
