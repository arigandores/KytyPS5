#!/bin/bash
# Track F link F42c (HPP-781; ROADMAP s122 item 694 (g)(6), item 705 (b)(5) and (v) N1, item 713, item 719): the tags f20_v (the FIRST run
# of KYTY_FIX_F20=1 on the caches of the user), f20_hb (right after it on the same caches, -lvl hoover_beach) and f20_w (=1 with
# --vulkan-validation true, the form fs12_w) of the F42a2 binary 1994a0ce (worktree 730ed40a + F42a + F42a2, HEAD 5ccb1d31, version
# KytyPS5-2026-09-15-6a2987a-1917-g5ccb1d31) - 1994a0ce is installed for the tag only, known by its full sha256; the installed FS13
# abab2196 (item 703-704) is checked before and returned from its pinned copy after.  ONE CALL = ONE LOCK.  Port of
# C:/kyty/f287/f44c/go_f44c.sh (F44c, HPP-793: the form of item 634 / 660 / 661 - no guard or hold check before the lock, no block of tags,
# no window; ONE guard scan + hold check right after the lock, before any manifest; the binary install / return; the V form fs12_v and the
# harness exit of b4_v) with the W form fs12_w of C:/kyty/f287/fs13c/go_fs13c.sh and THE SERIES FORM OF THE CACHES (item 694 (g)(6):
# "the manifest sha256 and the copy of _ShaderCache/PPSA21564 (with pipelines.bin, the variant catalog and replay/) and of the driver
# cache before the first tag, the return with cmp EQUAL after the last"; f20_hb "right after f20_v on the same caches"):
#   series caches  _ShaderCache, _ShaderSeeds, _PipelineCache and GLCache: copied ONCE inside the lock of f20_v (series/before_<d>,
#                  series/manifest_before.tsv) before the install, NOT returned after f20_v / f20_hb / f20_w; returned ONCE by the call
#                  f42c_ret (its own lock, no game) with 'manifest cmp EQUAL' against series/manifest_before.tsv - after the last tag or
#                  after a stop of the series; f20_hb / f20_w start only when the emulator caches (_ShaderCache, _ShaderSeeds,
#                  _PipelineCache) before the tag equal the state after the previous tag (series_f42c.py same; differ - SERIES_STOP,
#                  not started, exit 7; GLCache - a row).
#   _SaveData      copied and returned at every tag (manifest cmp EQUAL - admission), as in F44c.
#   f20_v    -lvl underwater_aerial_garden --stable-draws 300 --timeout 480, hold 330 s, video
#   f20_hb   -lvl hoover_beach --stable-draws 300 --timeout 480, hold 330 s, video (the form fs4_hb)
#   f20_w    -lvl underwater_aerial_garden --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000,
#            --stable-draws 100 --timeout 900, hold 310 s, no video
#   all tags: KYTY_FIX_F20=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 + the constants of enter_scene.py (KYTY_FRAME_TRACE=lite,
#            KYTY_GPU_HANG_ABORT_S=8, gate files, KYTY_QUEUE_TRACE=1, KYTY_GUEST_ARGS=-lvl <level>); the exit is the harness exit of b4_v
#            (WM_CLOSE at the end of the hold - log 'Event: quit' - CLOSE_WAIT_S = 40 s, else killed).
#   f42c_ret the series return (no game, no binary install).
#   <name>_r1..r3   a repeat only by the lead's item (an interference does not spend the attempt, item 273 (z)); F42C_REPEAT_OK=1 needed
# Order: f20_v needs no series snapshot (a repeat of f20_v - f42c_ret first); f20_hb needs a made f20_v* in series/tags.txt; f20_w needs a
# made f20_hb*; f42c_ret needs a snapshot.  No RenderDoc, no KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH, no KYTY_DIAG_*, no KYTY_TEST_*, no
# KYTY_FIX_* except KYTY_FIX_F20=1; KYTY_* and VK_LAYER_* of the shell are unset before the call; the knobs go to enter_scene.py
# positionally.
# usage: bash C:/kyty/f287/f42c/go_f42c.sh f20_v|f20_hb|f20_w|f42c_ret   (F42C_DRYRUN=1 prints the plan; F42C_DRYRUN=3 stops after
#   the series order checks - fixtures only, with F42C_SERIES / F42C_TIMES)
# EXIT: 0 made (read it with post_f42c.sh); 1 hard refusal / return failed; 2 usage / the tag exists / the series order; 3 lock / user
#   process / run gone; 4 stop file; 5 procload busy; 6 display not ON before the lock; 7 caches differ from the previous tag (SERIES_STOP);
#   10 form linter FAILED (item 661 (b)(1)).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f42c || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f42c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F42C_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
INST13=abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73
INST14=013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd
TB=1994a0ced45c8135f17c8d2aa568278c66375250f1667430c83ba4d0b1a93f29
BIN=$F/bin/kyty_emulator_1994a0ce.exe
PIN13=$F/bin/kyty_emulator_abab2196.exe
PIN14=$F/bin/kyty_emulator_013e1974.exe
SEAL=$G/pred/f42c_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
VKLAYER=C:/VulkanSDK/1.4.357.0/Bin
S=${F42C_SERIES:-$G/series}
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f20_v|f20_hb|f20_w|f42c_ret|f20_v_r[1-3]|f20_hb_r[1-3]|f20_w_r[1-3]|f42c_ret_r[1-3]) ;;
  *) echo "usage: go_f42c.sh f20_v|f20_hb|f20_w|f42c_ret[_r1..3]"; exit 2;;
esac
B=${T%_r[1-3]}
case "$B" in
  f20_v)  LV=underwater_aerial_garden; SD=300; H=330; TO=480; REC="--rec"; KX="KYTY_FIX_F20=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;
  f20_hb) LV=hoover_beach; SD=300; H=330; TO=480; REC="--rec"; KX="KYTY_FIX_F20=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;
  f20_w)  LV=underwater_aerial_garden; SD=100; H=310; TO=900; REC="--emu-arg=--vulkan-validation --emu-arg=true"
          KX="KYTY_FIX_F20=1 VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;
  f42c_ret) LV=none; SD=none; H=0; TO=0; REC=none; KX=none;;
esac
[ "${F42C_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B level $LV sd $SD timeout $TO hold $H rec $REC knobs $KX"; exit 0; }
OUT=$G/runs/$T; TIMES=${F42C_TIMES:-$F/times.txt}
SERDIRS="_ShaderCache _ShaderSeeds _PipelineCache GLCache"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F42c go_f42c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
live_of() { if [ "$1" = "GLCache" ]; then echo "$GLDIR"; else echo "$EMU/$1"; fi; }
MF_SER=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "GLCache=$GLDIR")
MF_TAG=("_SaveData=$EMU/_SaveData")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
if [ "$B" != f42c_ret ]; then
  [ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
fi
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a call runs once"; exit 2; }
case "$B" in
  f20_v) [ -e $S ] && { echo "series snapshot $S exists - f42c_ret first (seal section 2)"; exit 2; };;
  f20_hb) { [ -f $S/manifest_before.tsv ] && [ -f $S/last_after.tsv ] && grep -q '^f20_v' $S/tags.txt 2>/dev/null; } \
            || { echo "no series with a made f20_v - not starting (seal section 3)"; exit 2; };;
  f20_w) { [ -f $S/manifest_before.tsv ] && [ -f $S/last_after.tsv ] && grep -q '^f20_hb' $S/tags.txt 2>/dev/null; } \
            || { echo "no series with a made f20_hb - not starting (seal section 3)"; exit 2; };;
  f42c_ret) [ -f $S/manifest_before.tsv ] || { echo "no series snapshot to return"; exit 2; };;
esac
[ "${F42C_DRYRUN:-}" = 3 ] && { echo "dryrun3 order ok $T"; exit 0; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ -f $G/base/base.tsv ] || { echo "no base manifest $G/base/base.tsv"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "F42a2 copy $BIN is not 1994a0ce - not starting"; exit 1; }
WANT=$(sha "$GAME")
# installed before the call: FS13 abab2196 or FS14 013e1974 (item 710(g)(4) - FS14d may install FS14 between the tags); after = before
case "$WANT" in
  "$INST13") INST=$INST13; PINNED=$PIN13; INAME=FS13;;
  "$INST14") INST=$INST14; PINNED=$PIN14; INAME=FS14;;
  *) log "installed binary $WANT is neither FS13 abab2196 nor FS14 013e1974 - not starting (question to the lead)"; exit 1;;
esac
[ "$(sha "$PINNED")" = "$INST" ] || { log "pinned $INAME copy $PINNED is not ${INST:0:8} - not starting"; exit 1; }
log "installed before the call: $INAME ${INST:0:8} (pinned copy $PINNED)"
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_f42c.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
python $G/hostload_f42c.py --json $OUT/hostload_before.json > $OUT/hostload_before.txt 2>&1
log "host load before the call (item 632 (v)(2)): $(head -1 $OUT/hostload_before.txt | cut -c1-200)"
# item 623 (v)(1): a display OFF before the call is woken by the harness itself, then checked again
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
if ! { echo "F42c HPP-781 go_f42c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f42c.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); log "user emulator or launcher found right after the lock - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2)): $GS"; exit 3; }
HS=$(python $G/hold_f42c.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2))"; exit 3; }
log "lock taken; guard: $GS; hold: $HS; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the call: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
launched() { [ -f $OUT/run.txt ] && grep -q -- '--- attempt 1: launching' $OUT/run.txt; }
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f42c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS2=$(python $G/guard_f42c.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS2) - binary and _SaveData wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f42c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ -e $OUT/VM_FOUND ]; then
    log "user VM during the tag ($(head -1 $OUT/VM_FOUND | cut -c1-120)) - the return waits for its exit, poll 10 s, the lock stays (item 606 (v)(1))"
    log "$(python $G/hold_f42c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
  fi
  if [ $INSTALLED = 1 ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$INST" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$INST" ]; then log "installed binary returned from the pinned $INAME copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the call: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$INST" ] || { OK=0; log "INSTALLED BINARY IS NOT $INAME (= before) after the call"; }
  if [ "$B" = f42c_ret ]; then
    if [ -f $OUT/ret_started ]; then
      python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF_SER[@]}" > $OUT/manifest_after.txt 2>&1
      python $G/manifest_fs4c.py --cmp $S/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
      MC=$?
      log "series return: manifest after: $(head -1 $OUT/manifest_after.txt | cut -c1-200); cmp against the series snapshot: $(head -1 $OUT/manifest_cmp.txt)"
      if [ $MC = 0 ]; then
        RD=$G/series.returned_$(date -u +%Y%m%dT%H%M%SZ)
        mv $S $RD && log "series snapshot dir moved to $RD (the next series may start)" || { OK=0; log "move of the series dir FAILED"; }
      else
        OK=0
      fi
    fi
  else
    if [ -n "$COPIED" ]; then
      python $G/manifest_fs4c.py $OUT/manifest_run.tsv "${MF_TAG[@]}" > $OUT/manifest_run.txt 2>&1
      LIVE="$EMU/_SaveData"
      rm -rf "$LIVE" && mv "$OUT/before__SaveData" "$LIVE" || { OK=0; log "return of _SaveData FAILED"; }
      [ -d "$LIVE" ] || OK=0
      [ ! -e "$OUT/before__SaveData" ] || OK=0
    fi
    if [ -f $OUT/manifest_before.tsv ]; then
      [ -n "$COPIED" ] || { [ -e "$EMU/_SaveData" ] && { rm -rf "$EMU/_SaveData" || OK=0; log "_SaveData was absent before the tag - removed at the return"; }; }
      python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF_TAG[@]}" > $OUT/manifest_after.txt 2>&1
      python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
      MC=$?
      log "_SaveData manifest after: $(head -1 $OUT/manifest_after.txt | cut -c1-200); cmp: $(head -1 $OUT/manifest_cmp.txt)"
      [ $MC = 0 ] || OK=0
    fi
    if [ -f $OUT/cache_before.tsv ] && launched; then
      python $G/manifest_fs4c.py $OUT/cache_after.tsv "${MF_SER[@]}" > $OUT/cache_after.txt 2>&1
      cp $OUT/cache_after.tsv $S/last_after.tsv || OK=0
      echo "$T $(u)" >> $S/tags.txt || OK=0
      log "series caches after the tag (not returned, seal section 2): $(head -1 $OUT/cache_after.txt | cut -c1-200); $(python $G/series_f42c.py sizes $OUT/cache_before.tsv | sed 's/^sizes /before /') ; $(python $G/series_f42c.py sizes $OUT/cache_after.tsv | sed 's/^sizes /after /')"
    fi
  fi
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; log "lock released (rc $RCX)"
    DA=$(python $G/dispstate.py); DARC=$?
    echo "$DA" > $OUT/disp_after.txt
    stop_disp
    log "display after lock released (item 620 (g)(1)): $DA; hold: $(grep -c '^event ' $OUT/disp_hold.txt) display events, $(grep -c '^event .* OFF' $OUT/disp_hold.txt) OFF; $(tail -1 $OUT/disp_hold.txt | cut -c1-120)"
    python $G/hostload_f42c.py --json $OUT/hostload_after.json > $OUT/hostload_after.txt 2>&1
    log "host load after the call (item 632 (v)(2)): $(head -1 $OUT/hostload_after.txt | cut -c1-200)"
    [ -e $OUT/VM_FOUND ] && [ ! -e $OUT/USER_FOUND ] && cp $OUT/VM_FOUND $OUT/USER_FOUND
    if [ "$B" = f42c_ret ]; then
      [ -f $OUT/ret_started ] || { mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "the series return did not start - repeat by the same name"; }
    elif [ $DARC != 0 ] && [ -f $OUT/run.txt ]; then
      mv $OUT $OUT.display_$(date -u +%H%M%S)
      log "display not ON after the tag - the tag is the interference DISPLAY_OFF (item 620 (g)(1)), not read; repeat by the lead's item"
    elif [ -e $OUT/USER_FOUND ]; then
      UF2=$(head -1 $OUT/USER_FOUND | cut -c1-160)
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF2) - interference, repeat by the lead's item (item 534, 273 (z))"
    elif ! launched; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never launched the emulator - not a tag, repeat by the same name"
    fi
  else
    stop_disp
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete, installed binary or manifest differs - the lock stays, question to the lead"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
if [ "$B" = f42c_ret ]; then
  python $G/manifest_fs4c.py $OUT/manifest_run.tsv "${MF_SER[@]}" > $OUT/manifest_run.txt 2>&1
  log "series return: state before the return: $(head -1 $OUT/manifest_run.txt | cut -c1-200)"
  touch $OUT/ret_started
  for d in $SERDIRS; do
    LIVE=$(live_of $d)
    if [ -d "$S/before_$d" ]; then
      rm -rf "$LIVE" && mv "$S/before_$d" "$LIVE" || { log "series return of $d FAILED"; exit 1; }
    else
      [ -e "$LIVE" ] && { rm -rf "$LIVE"; log "$d was absent at the snapshot - removed at the series return"; }
    fi
  done
  log "series caches returned from the snapshot: $SERDIRS"
  exit 0
fi
python $G/manifest_fs4c.py $OUT/cache_before.tsv "${MF_SER[@]}" > $OUT/cache_before.txt 2>&1 || { log "manifest of the series caches failed - not starting"; rm -f $OUT/cache_before.tsv; exit 1; }
log "series caches before the tag: $(head -1 $OUT/cache_before.txt | cut -c1-200); $(python $G/series_f42c.py sizes $OUT/cache_before.tsv)"
if [ "$B" = f20_v ]; then
  python $G/manifest_fs4c.py --cmp $G/base/base.tsv $OUT/cache_before.tsv > $OUT/base_cmp.txt 2>&1
  log "series caches before f20_v against the base manifest of the seal (row): $(head -1 $OUT/base_cmp.txt | cut -c1-160)"
  mkdir -p $S || { log "mkdir of the series dir failed - not starting"; exit 1; }
  cp $OUT/cache_before.tsv $S/manifest_before.tsv || { log "series manifest copy failed - not starting"; rm -rf $S; exit 1; }
  for d in $SERDIRS; do
    SRC=$(live_of $d)
    [ -d "$SRC" ] || { log "$d absent - not copied (series manifest line MISSING)"; continue; }
    cp -a "$SRC" "$S/before_$d" || { log "series copy of $d failed - not starting"; rm -rf $S; exit 1; }
  done
  echo "series snapshot taken $(head -1 $OUT/cache_before.txt | cut -c1-200) at $(u)" > $OUT/series_taken.txt
  log "$(cat $OUT/series_taken.txt) ($(du -sm $S/before_* | awk '{print $1}' | tr '\n' '/') MB)"
else
  python $G/series_f42c.py same $OUT/cache_before.tsv $S/last_after.tsv > $OUT/same_cmp.txt 2>&1; SC=$?
  log "caches before the tag against the previous tag of the series: $(head -2 $OUT/same_cmp.txt | tr '\n' ';' | cut -c1-240)"
  if [ $SC != 0 ]; then
    echo "$(u) $T caches before the tag differ from the state after the previous tag of the series" > $G/SERIES_STOP
    log "the emulator caches differ from the previous tag - not starting, SERIES_STOP, question to the lead (seal section 2)"; exit 7
  fi
fi
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF_TAG[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest of _SaveData failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
log "_SaveData manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
if [ -d "$EMU/_SaveData" ]; then
  cp -a "$EMU/_SaveData" "$OUT/before__SaveData" || { log "copy of _SaveData failed - not starting"; rm -rf "$OUT/before__SaveData"; exit 1; }
  COPIED="_SaveData"
else
  log "_SaveData absent - not copied (manifest line MISSING)"
fi
TC="$EMU/_ShaderCache/PPSA21564"
echo "state before the start: pipelines.bin $( [ -f "$TC/pipelines.bin" ] && echo present || echo absent ), replay $( [ -d "$TC/replay" ] && echo present || echo absent ), variant_fixb26_fixb1b_fixf10_fixf19 $( [ -d "$TC/variant_fixb26_fixb1b_fixf10_fixf19" ] && echo present || echo absent ) at $(u)" > $OUT/warm.txt
log "$(cat $OUT/warm.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the F42a2 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the F42a2 copy 1994a0ce for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*' > $OUT/env_shell_after_unset.txt
log "enter_scene start (level $LV, sd $SD, timeout $TO, hold $H, $REC, $KX); shell KYTY_*/VK_LAYER_* after unset: $(wc -l < $OUT/env_shell_after_unset.txt)"
python $G/guard_f42c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_f42c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL $REC --hold $H $KX > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f42c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
