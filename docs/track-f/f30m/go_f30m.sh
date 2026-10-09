#!/bin/bash
# Track F link F30m (HPP-723; ROADMAP s122 item 655 (e)(1)-(5), item 658 (b)-(v)): one tag of the series c5 (9 scenes of F30f) and the
# form (gamma) on cymbal_party_land on the binary T2 bba692c6 (F30k HPP-721: T a1d1d863 + 11236f5a = 6fbdcf67) - T2 is installed for the
# tag only, known by its full sha256; the installed FS11 ea51ae80 (item 656-657) is checked before and returned from its pinned copy after
# (item 655 (e)(1): returned after the last tag and before any foreign tag - here after every tag).  ONE TAG = ONE LOCK.
# Port of C:/kyty/f287/f30f/go_f30f.sh (F30f, HPP-711) with: the binary T2, the installed FS11, the tags f30_s<k>_c5 / f30_cy_v / f30_cy_c3 /
# f30_cy_c4 (item 655 (e)(2)-(3)), the scene cy = cymbal_party_land (entry form V of session 145: --stable-draws 300 --timeout 480);
# the caches NOT copied and NOT returned (manifest before and after, a row); the display member (item 620 (g)(1), 623 (v)); the user game
# guard (item 534) and the user session guard (item 606 (v)(1)) - a user process or session during the tag kills the own emulator, the tag
# is an interference.
#   c5  KYTY_RT_SKIP=5, hold 150 s, no video   cy_v  =2, hold 300 s, video   cy_c3  =3, hold 150 s, no video   cy_c4  =4, hold 150 s, no video
#   every tag: --stable-draws 300 --timeout 480, KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0; s9 also KYTY_KEYS of FS3c (keys_a2_presents.txt
#   verbatim, item 643 (g) RC4, as F30f).  Constants of enter_scene.py: KYTY_FRAME_TRACE=lite, KYTY_GPU_HANG_ABORT_S=8,
#   KYTY_GATE_FILE (gates_default.txt - empty), KYTY_SAMPLE_GATE, KYTY_QUEUE_TRACE=1, KYTY_GUEST_ARGS=-lvl <level>, KYTY_REC (cy_v).
# No RenderDoc, no validation, no --graphics-debug-dump, no KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH, none of the 11 refusal knobs;
# KYTY_* and VK_LAYER_* of the shell are unset before the call; the knobs go to enter_scene.py positionally.
# usage: bash C:/kyty/f287/f30m/go_f30m.sh <f30_s<1..9>_c5 | f30_cy_v | f30_cy_c3 | f30_cy_c4>[_r1.._r3]
# EXIT: 0 tag made (read it with post_f30m.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process / run gone;
#   4 stop file; 5 procload busy; 6 display not ON before the lock; 10 form linter FAILED (item 661 (b)(1)).  ASCII only.
# ITEM 660 (d)(2) (form of item 634): no guard / hold check before the lock; ONE guard scan + hold check right after the lock, before
# the manifest; a finding releases the lock, the tag is an interference, the repeat goes by the next command without a window.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f30m || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f30m; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F30M_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
FS11=ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce
TB=bba692c6c161afc0cd2bd3245cea574f7fb82e7a4aae4c065826898403107163
BIN=$F/bin/kyty_emulator_bba692c6.exe
PINNED=$F/bin/kyty_emulator_ea51ae80.exe
SEAL=$G/pred/f30m_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
KEYS="@1300:a/@45 @1380:w/@45 @1500:w/@96 @1650:h/@975 @2600:f/@1003 @3550:w/@18 @3600:d/@30 @3650:s/@31 @3700:a/@31 @3750:w/@49 @3800:w/@90 @3900:h/@966 @4850:f/@984 @5800:w/@17 @5830:d/@25 @5860:s/@25 @5890:a/@25 @5920:w/@25"
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f30_s[1-9]_c5|f30_cy_v|f30_cy_c3|f30_cy_c4) ;;
  f30_s[1-9]_c5_r[1-3]|f30_cy_v_r[1-3]|f30_cy_c3_r[1-3]|f30_cy_c4_r[1-3]) ;;
  *) echo "usage: go_f30m.sh <f30_s<1..9>_c5 | f30_cy_v | f30_cy_c3 | f30_cy_c4>[_r1..3]"; exit 2;;
esac
B=${T%_r[1-3]}
SC=$(echo $B | cut -d_ -f2); KD=$(echo $B | cut -d_ -f3)
case "$SC" in
  s1) LV=underwater_aerial_garden;; s2) LV=hoover_beach;; s3) LV=mini_giants_garden;; s4) LV=timestop_casino;;
  s5) LV=rotating_level_day_and_night;; s6) LV=sponge_dirty_bath;; s7) LV=time_stopper_ghost_world;; s8) LV=big_hand_pirate_island;;
  s9) LV=underwater_aerial_garden;; cy) LV=cymbal_party_land;;
esac
SD=300
TO=480
case "$KD" in
  c5) RT=5; H=150; REC="";;
  c3) RT=3; H=150; REC="";;
  c4) RT=4; H=150; REC="";;
  v) RT=2; H=300; REC="--rec";;
esac
KN=(KYTY_RT_SKIP=$RT KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0)
[ "$SC" = s9 ] && KN+=("KYTY_KEYS=$KEYS")
[ "${F30M_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B scene $SC kind $KD level $LV sd $SD hold $H timeout $TO rec ${REC:--} knobs ${KN[*]}"; exit 0; }
OUT=$G/runs/$T; TIMES=$F/times.txt
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F30m go_f30m $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "T2 copy $BIN is not bba692c6 - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$FS11" ] || { log "pinned FS11 copy $PINNED is not ea51ae80 - not starting"; exit 1; }
WANT=$(sha "$GAME")
[ "$WANT" = "$FS11" ] || { log "installed binary $WANT is not FS11 ea51ae80 - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_f30m.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
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
if ! { echo "F30m HPP-723 go_f30m.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_f30m.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); log "user emulator or launcher found right after the lock - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2)): $GS"; exit 3; }
HS=$(python $G/hold_f30m.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2))"; exit 3; }
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
INSTALLED=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_f30m.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -e $OUT/USER_FOUND ] && [ $INSTALLED = 1 ]; then
    GS=$(python $G/guard_f30m.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ]; then
      log "user process at the return ($GS) - the binary waits for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_f30m.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ $INSTALLED = 1 ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$FS11" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$FS11" ]; then log "installed binary returned from the pinned FS11 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$FS11" ] || { OK=0; log "INSTALLED BINARY IS NOT FS11 after the tag"; }
  if [ -f $OUT/manifest_before.tsv ]; then
    # item 655 (e)(1): the caches are not returned - the manifest after and the comparison are rows, not members
    python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
    log "manifest after (caches not returned, item 655 (e)(1)): $(head -1 $OUT/manifest_after.txt | cut -c1-200); before vs after: $(head -1 $OUT/manifest_cmp.txt | cut -c1-160)"
  fi
  if [ $OK = 1 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; log "lock released (rc $RCX)"
    DA=$(python $G/dispstate.py); DARC=$?
    echo "$DA" > $OUT/disp_after.txt
    stop_disp
    log "display after lock released (item 620 (g)(1)): $DA; hold: $(grep -c '^event ' $OUT/disp_hold.txt) display events, $(grep -c '^event .* OFF' $OUT/disp_hold.txt) OFF; $(tail -1 $OUT/disp_hold.txt | cut -c1-120)"
    [ -e $OUT/VM_FOUND ] && [ ! -e $OUT/USER_FOUND ] && cp $OUT/VM_FOUND $OUT/USER_FOUND
    if [ $DARC != 0 ] && [ -f $OUT/run.txt ]; then
      mv $OUT $OUT.display_$(date -u +%H%M%S)
      log "display not ON after the tag - the tag is the interference DISPLAY_OFF (item 620 (g)(1)), not read; repeat by the lead's item"
    elif [ -e $OUT/USER_FOUND ]; then
      UF2=$(head -1 $OUT/USER_FOUND | cut -c1-160)
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process or session during the tag ($UF2) - interference, repeat by the lead (item 534, 606 (v)(1))"
    elif [ ! -f $OUT/run.txt ]; then
      mv $OUT $OUT.nostart_$(date -u +%H%M%S); log "enter_scene never started - not a tag, repeat by the same name (item 534)"
    fi
  else
    stop_disp
    echo "$(u) $T" > $G/RETURN_FAILED; log "return of the binary incomplete - the lock stays"; RCX=1
  fi
  exit $RCX
}
trap finish EXIT
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1 || { log "manifest before failed - not starting"; rm -f $OUT/manifest_before.tsv; exit 1; }
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
python $G/manifest_fs4c.py --cmp $G/base/base.tsv $OUT/manifest_before.tsv > $OUT/base_cmp.txt 2>&1
log "caches before against the base manifest of the seal (row): $(head -1 $OUT/base_cmp.txt | cut -c1-160)"
TC="$EMU/_ShaderCache/PPSA21564"
echo "state before the start: pipelines.bin $( [ -f "$TC/pipelines.bin" ] && echo present || echo absent ), replay $( [ -d "$TC/replay" ] && echo present || echo absent ), variant_fixb26_fixb1b_fixf10_fixf19 $( [ -d "$TC/variant_fixb26_fixb1b_fixf10_fixf19" ] && echo present || echo absent ) at $(u)" > $OUT/warm.txt
log "$(cat $OUT/warm.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the T2 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the T2 copy bba692c6 for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
log "enter_scene start (level $LV, SD $SD, hold $H, ${REC:-no video}, ${KN[*]})"
python $G/guard_f30m.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_f30m.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL $REC --hold $H "${KN[@]}" > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_f30m.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
