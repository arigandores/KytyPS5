#!/bin/bash
# Track M link M3a (HPP-842; ROADMAP s122 item 756 (g)(3)-(7), 760 (b), 761 (d)-(e), 763 (v)): ONE tag of the series M3 under the lock.
# Port of C:/kyty/f287/fs15c/go_fs15c.sh (FS15c, HPP-822: the form of item 634 / 660 / 661 - one guard scan + hold check right after
# the lock, before any manifest; the caches copied before and returned after EVERY tag; the tag binary installed for the tag only and
# the installed FS15 bfac84be returned from its pinned copy).  New in M3a (seal C:/kyty/m657/m3a/pred.md, section 5):
#   - two binaries: MS1 ea35b679 (C:/kyty/m657/bin, item 763) and FS15 bfac84be (C:/kyty/f287/bin, the installed one);
#   - six levels (sg hb mg ac f1 f2) and the tag table of the seal (section 3);
#   - the cache states: K0 = the user caches before the first tag (copied once by m3_i into $G/k0, its manifest k0/k0.tsv); between
#     tags the live caches are K0 (gate: the four emulator labels of the live manifest = k0.tsv, kset_m3a.py cmp4); K1 = the MS1 state
#     after m3_i, kept in $G/k1 and grown by the MS1 tags with SAVE=K1; KT = the scratch state of a translator theme arm (warm-up 'p').
#     BASE=K1/KT: the live caches are replaced by a copy of k1/kt before the run (manifest = k1.tsv / kt.tsv, else stop); SAVE=K1/KT:
#     the live caches after the run are moved into k1/kt (the previous one to *.prev); then the K0 copy of the tag is returned (RC-M1 of
#     item 761 (d)(1): every FS15 arm and FS15 sheet runs on K0);
#   - a tag that reset the driver (ErrorDeviceLost / device lost in the log or stdout) writes SERIES_STOP (item 760 (b)(2) analogue).
# usage: bash C:/kyty/m657/m3a/go_m3a.sh <tag>
# EXIT: 0 tag made (read it with post_m3a.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process / run
#   gone; 4 stop file; 5 procload busy; 6 display not ON before the lock; 10 form linter FAILED (item 661 (b)(1)).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/m657/m3a || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/m657/m3a; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${M3A_LOCK:-C:/kyty/SEALED_RUN.lock}
GAME="$EMU/kyty_emulator.exe"
FS15=bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c
MS1=ea35b679b0bcfe83767093204f348b189384cab1a7b273f89b164b64cba4d4df
PINNED=C:/kyty/f287/bin/kyty_emulator_bfac84be.exe
MS1BIN=C:/kyty/m657/bin/kyty_emulator_ea35b679.exe
SEAL=$G/pred.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
VKLAYER=C:/VulkanSDK/1.4.357.0/Bin
POKELOG=27e46c:909090909090
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
B=${T%_r[1-3]}
LS=${B#m3_}; LS=${LS%%_*}
case "$LS" in
  sg) LV=underwater_aerial_garden;; hb) LV=hoover_beach;; mg) LV=mini_giants_garden;; ac) LV=armadillo_challenge_1;;
  f1) LV=fragile_battle_1;; f2) LV=fragile_battle_2;; i|g5|g6) LV=underwater_aerial_garden;; *) LV="";;
esac
VF="SD=300; TO=480; H=330; KIND=v"
WF="SD=100; TO=900; H=310; KIND=w"
PF="SD=300; TO=480; H=150; KIND=p"
KNOB=""; PATCH=0
case "$B" in
  m3_i) BK=ms1; eval "$VF"; BASE=K0; SAVE=K1;;
  m3_sg_w|m3_hb_w|m3_mg_w|m3_ac_w|m3_f1_w|m3_f2_w) BK=ms1; eval "$WF"; BASE=K1; SAVE=K1;;
  m3_sg_v|m3_hb_v|m3_mg_v|m3_ac_v|m3_f1_v|m3_f2_v) BK=ms1; eval "$VF"; BASE=K1; SAVE=K1;;
  m3_sg_f|m3_hb_f|m3_mg_f|m3_ac_f|m3_f1_f|m3_f2_f) BK=fs15; eval "$VF"; BASE=K0; SAVE=none;;
  m3_g5_a1|m3_g5_a2) BK=fs15; eval "$VF"; BASE=K0; SAVE=none;;
  m3_g5_b1|m3_g5_b2) BK=ms1; eval "$VF"; BASE=K1; SAVE=K1;;
  m3_g6) BK=ms1; eval "$VF"; BASE=K1; SAVE=none; PATCH=1;;
  m3_g5_t2330p) BK=ms1; eval "$PF"; BASE=K1; SAVE=KT; KNOB=KYTY_M_T233=0;;
  m3_g5_t2330) BK=ms1; eval "$VF"; BASE=KT; SAVE=none; KNOB=KYTY_M_T233=0;;
  m3_*_t2340p|m3_*_t2330p|m3_*_t0320p|m3_*_t2030p)
    TH=${B%0p}; TH=${TH##*_t}; BK=ms1; eval "$PF"; BASE=K1; SAVE=KT; KNOB=KYTY_M_T$TH=0;;
  m3_*_t2340|m3_*_t2330|m3_*_t0320|m3_*_t2030)
    TH=${B%0}; TH=${TH##*_t}; BK=ms1; eval "$VF"; BASE=KT; SAVE=none; KNOB=KYTY_M_T$TH=0;;
  m3_*_t2340w|m3_*_t2330w|m3_*_t0320w|m3_*_t2030w)
    TH=${B%0w}; TH=${TH##*_t}; BK=ms1; eval "$WF"; BASE=KT; SAVE=none; KNOB=KYTY_M_T$TH=0;;
  m3_*_t2650|m3_*_t2720|m3_*_t2310)
    TH=${B%0}; TH=${TH##*_t}; BK=ms1; eval "$VF"; BASE=K1; SAVE=none; KNOB=KYTY_M_T$TH=0;;
  m3_*_t2650w|m3_*_t2720w|m3_*_t2310w)
    TH=${B%0w}; TH=${TH##*_t}; BK=ms1; eval "$WF"; BASE=K1; SAVE=none; KNOB=KYTY_M_T$TH=0;;
  *) BK="";;
esac
case "$LS" in sg|hb|mg|ac|f1|f2) ;; *) case "$B" in m3_i|m3_g5_a1|m3_g5_a2|m3_g5_b1|m3_g5_b2|m3_g5_t2330p|m3_g5_t2330|m3_g6) ;; *) BK="";; esac;; esac
if [ -z "$BK" ] || [ -z "$LV" ]; then echo "usage: go_m3a.sh <tag of the seal section 3>[_r1..3]"; exit 2; fi
case "$KIND" in
  v) REC="--rec";;
  w) REC="--emu-arg=--vulkan-validation --emu-arg=true";;
  p) REC="";;
esac
KX="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0"
[ "$KIND" = w ] && KX="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 $KX"
[ -n "$KNOB" ] && KX="$KX $KNOB"
KEYS=""; PFILE=""; PFSHA=""
if [ $PATCH = 1 ]; then
  KEYS=$(grep -m1 '^keys: ' "$SEAL" 2>/dev/null | cut -c7- | tr -d '\r')
  PL=$(grep -m1 '^patch file: ' "$SEAL" 2>/dev/null | cut -c13- | tr -d '\r'); PFSHA=${PL%% *}; PFILE=${PL#* }
  KX="$KX KYTY_GAME_PATCH=$PFILE KYTY_POKE=$POKELOG KYTY_KEYS=$KEYS"
fi
if [ "$BK" = ms1 ]; then TB=$MS1; BIN=$MS1BIN; else TB=$FS15; BIN=$PINNED; fi
[ "${M3A_DRYRUN:-}" = 1 ] && { echo "dryrun $T base $B bin $BK level $LV kind $KIND sd $SD timeout $TO hold $H rec $REC cache $BASE save $SAVE knobs ${KX//KYTY_KEYS=*/KYTY_KEYS=<keys of the seal, ${#KEYS} chars>}"; exit 0; }
OUT=$G/runs/$T; TIMES=$G/times.txt; DIRS="_ShaderCache _ShaderSeeds _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) M3a go_m3a $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
live_of() { if [ "$1" = GLCache ]; then echo "$GLDIR"; else echo "$EMU/$1"; fi; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
kmf() { K=$1; echo "_ShaderCache=$G/$K/_ShaderCache" "_ShaderSeeds=$G/$K/_ShaderSeeds" "_PipelineCache=$G/$K/_PipelineCache" "_SaveData=$G/$K/_SaveData" "GLCache=$G/$K/GLCache"; }
[ -e C:/kyty/m657/STOP ] && { log "STOP file: $(head -1 C:/kyty/m657/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $G/SERIES_STOP ] && { echo "SERIES_STOP exists: $(head -1 $G/SERIES_STOP)"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha "$BIN")" = "$TB" ] || { log "tag binary $BIN is not $TB - not starting"; exit 1; }
[ "$(sha "$PINNED")" = "$FS15" ] || { log "pinned FS15 copy $PINNED is not bfac84be - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$FS15" ] || { log "installed binary $(sha "$GAME") is not FS15 bfac84be - not starting (question to the lead)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
if [ "$B" = m3_i ]; then
  [ -e $G/k0 ] && { log "k0 exists - m3_i runs once (the copy K0 is taken by it)"; exit 1; }
else
  [ -f $G/k0/k0.tsv ] || { log "no K0 manifest $G/k0/k0.tsv - m3_i first"; exit 1; }
fi
case "$BASE" in
  K1) [ -f $G/k1/k1.tsv ] || { log "no K1 manifest $G/k1/k1.tsv - not starting"; exit 1; };;
  KT) [ -f $G/kt/kt.tsv ] || { log "no KT manifest $G/kt/kt.tsv (the warm-up arm p first) - not starting"; exit 1; };;
esac
if [ $PATCH = 1 ]; then
  [ -f "$PFILE" ] && [ "$(sha "$PFILE")" = "$PFSHA" ] && [ ${#PFSHA} = 64 ] || { log "patch file of the seal missing or its sha differs - not starting"; exit 1; }
  case "$KEYS" in ''|*' '*) log "keys line of the seal bad - not starting"; exit 1;; esac
fi
mkdir -p $OUT
echo "$LV" > $OUT/level.txt
echo "$BK $TB $BASE $SAVE $KIND $KNOB" > $OUT/plan.txt
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
RS=$(python $G/runchk_m3a.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }
log "run check (item 587 (g)): $RS"
python $G/hostload_m3a.py --json $OUT/hostload_before.json > $OUT/hostload_before.txt 2>&1
log "host load before the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_before.txt | cut -c1-200)"
DS=$(python $G/dispstate.py); DSRC=$?
if [ $DSRC != 0 ]; then
  WS=$(python $G/dispstate.py --wake | tr '\n' ';')
  log "display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-200)"
  DS=$(python $G/dispstate.py); DSRC=$?
fi
echo "$DS" > $OUT/disp_before.txt
[ $DSRC = 0 ] || { log "display not ON before the lock after the wake (item 620 (g)(1), 623 (v)(1)): $DS - not starting, files untouched, not an attempt"; mv $OUT $OUT.dispoff_$(date -u +%H%M%S); exit 6; }
log "display before the lock (item 620 (g)(1)): $DS"
python $G/dispstate.py --hold-until $OUT/disp.stop --max $((TO + H + 1500)) > $OUT/disp_hold.txt 2>&1 &
DPID=$!
stop_disp() { touch $OUT/disp.stop 2>/dev/null; wait $DPID 2>/dev/null; }
set -o noclobber
if ! { echo "M3a HPP-842 go_m3a.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; stop_disp; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_m3a.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.user_$(date -u +%H%M%S); log "user emulator or launcher found right after the lock - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2)): $GS"; exit 3; }
HS=$(python $G/hold_m3a.py check) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; stop_disp; mv $OUT $OUT.session_$(date -u +%H%M%S); log "user session right after the lock (item 606 (v)(1)): $HS - lock released, files untouched, interference, repeat by the next command (item 660 (d)(2))"; exit 3; }
log "lock taken; guard: $GS; hold: $HS; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
COPIED=""
INSTALLED=0
SAVED=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_m3a.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS2=$(python $G/guard_m3a.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS2) - binary, caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_m3a.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ -e $OUT/VM_FOUND ]; then
    log "user VM during the tag ($(head -1 $OUT/VM_FOUND | cut -c1-120)) - caches wait for its exit, poll 10 s, the lock stays (item 606 (v)(1))"
    log "$(python $G/hold_m3a.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
  fi
  if [ $INSTALLED = 1 ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$FS15" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$FS15" ]; then log "installed binary returned from the pinned FS15 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$FS15" ] || { OK=0; log "INSTALLED BINARY IS NOT FS15 after the tag"; }
  if [ -f $OUT/manifest_before.tsv ] && [ -n "$COPIED" ] && [ $SAVED = 0 ]; then
    python $G/manifest_fs4c.py $OUT/manifest_run.tsv "${MF[@]}" > $OUT/manifest_run.txt 2>&1
    log "manifest of the run state (before the return): $(head -1 $OUT/manifest_run.txt | cut -c1-200)"
  fi
  for d in $COPIED; do
    LIVE=$(live_of $d)
    if [ "$d" = "GLCache" ] && [ -e $OUT/VM_FOUND ]; then
      MR=$(python $G/snap_m3a.py merge-return GLCache "$OUT/before_$d" "$LIVE") || { OK=0; log "merge return of GLCache FAILED"; }
      log "GLCache returned by merge (item 606 (v)(3)): $MR"; continue
    fi
    rm -rf "$LIVE" && mv "$OUT/before_$d" "$LIVE" || { OK=0; log "return of $d FAILED"; }
  done
  if [ -n "$COPIED" ]; then
    for d in $COPIED; do
      LIVE=$(live_of $d)
      [ -d "$LIVE" ] || OK=0
      [ "$d" = "GLCache" ] && [ -e $OUT/VM_FOUND ] && continue
      [ ! -e "$OUT/before_$d" ] || OK=0
    done
    for d in $DIRS; do
      case " $COPIED " in *" $d "*) ;; *) [ -e "$EMU/$d" ] && { rm -rf "$EMU/$d" || OK=0; log "$d was absent before the tag - removed at the return";};; esac
    done
    [ $OK = 1 ] && log "caches, seeds, saves and GLCache returned (K0)"
  fi
  if [ -f $OUT/manifest_before.tsv ]; then
    python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1
    python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
    MC=$?
    log "manifest after: $(head -1 $OUT/manifest_after.txt | cut -c1-200); cmp: $(head -1 $OUT/manifest_cmp.txt)"
    if [ $MC != 0 ] && [ -e $OUT/VM_FOUND ]; then
      python $G/mfsub_m3a.py $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_sub.txt 2>&1 && MC=0
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
    python $G/hostload_m3a.py --json $OUT/hostload_after.json > $OUT/hostload_after.txt 2>&1
    log "host load after the tag (item 632 (v)(2)): $(head -1 $OUT/hostload_after.txt | cut -c1-200)"
    [ -e $OUT/VM_FOUND ] && [ ! -e $OUT/USER_FOUND ] && cp $OUT/VM_FOUND $OUT/USER_FOUND
    if [ $DARC != 0 ] && [ -f $OUT/run.txt ]; then
      mv $OUT $OUT.display_$(date -u +%H%M%S)
      log "display not ON after the tag - the tag is the interference DISPLAY_OFF (item 620 (g)(1)), not read; repeat by the lead's item"
    elif [ -e $OUT/USER_FOUND ]; then
      UF2=$(head -1 $OUT/USER_FOUND | cut -c1-160)
      mv $OUT $OUT.user_$(date -u +%H%M%S); log "user process during the tag ($UF2) - interference, repeat by the lead's item (item 534, 273 (z))"
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
if [ "$B" != m3_i ]; then
  K0C=$(python $G/kset_m3a.py cmp4 $G/k0/k0.tsv $OUT/manifest_before.tsv | head -1)
  echo "$K0C" > $OUT/k0_cmp.txt
  log "live caches before the tag against K0 (seal section 5): $K0C"
  case "$K0C" in "KSET EQUAL4"*) ;; *) echo "$(u) $T live caches are not K0: $K0C" > $G/SERIES_STOP; log "live caches are not K0 - not starting, SERIES_STOP, question to the lead"; rm -f $OUT/manifest_before.tsv; exit 1;; esac
fi
for d in $DIRS GLCache; do
  SRC=$(live_of $d)
  [ -d "$SRC" ] || { log "$d absent - not copied (manifest line MISSING)"; continue; }
  cp -a "$SRC" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
  COPIED="$COPIED $d"
done
log "caches, seeds, saves and GLCache copied:$COPIED ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
if [ "$B" = m3_i ]; then
  mkdir -p $G/k0
  for d in $COPIED; do cp -a "$OUT/before_$d" "$G/k0/$d" || { log "copy K0 of $d failed - not starting"; exit 1; }; done
  python $G/manifest_fs4c.py $G/k0/k0.tsv $(kmf k0) > $G/k0/k0.txt 2>&1
  K0E=$(python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $G/k0/k0.tsv | head -1)
  log "K0 taken: $(head -1 $G/k0/k0.txt | cut -c1-160); K0 = live before: $K0E"
  case "$K0E" in "manifest cmp EQUAL"*) ;; *) log "K0 copy differs from the live caches - not starting"; exit 1;; esac
fi
if [ "$BASE" = K1 ] || [ "$BASE" = KT ]; then
  KB=$(echo $BASE | tr 'A-Z' 'a-z')
  for d in $DIRS GLCache; do
    LIVE=$(live_of $d)
    rm -rf "$LIVE"
    [ -d "$G/$KB/$d" ] && { cp -a "$G/$KB/$d" "$LIVE" || { log "copy of $KB/$d to the live dir failed"; exit 1; }; }
  done
  python $G/manifest_fs4c.py $OUT/manifest_base.tsv "${MF[@]}" > $OUT/manifest_base.txt 2>&1
  KBE=$(python $G/manifest_fs4c.py --cmp $G/$KB/$KB.tsv $OUT/manifest_base.tsv | head -1)
  echo "$KBE" > $OUT/base_cmp.txt
  log "live caches set to $BASE: $(head -1 $OUT/manifest_base.txt | cut -c1-160); = $KB.tsv: $KBE"
  case "$KBE" in "manifest cmp EQUAL"*) ;; *) echo "$(u) $T base $BASE copy differs" > $G/SERIES_STOP; log "the $BASE copy in the live dirs differs from $KB.tsv - not starting, SERIES_STOP"; exit 1;; esac
fi
TC="$EMU/_ShaderCache/PPSA21564"
echo "state before the start ($BASE): pipelines.bin $( [ -f "$TC/pipelines.bin" ] && echo present || echo absent ), replay $( [ -d "$TC/replay" ] && echo present || echo absent ), variant_fixb26_fixb1b_fixf10_fixf19 $( [ -d "$TC/variant_fixb26_fixb1b_fixf10_fixf19" ] && echo present || echo absent ), variant_fixb26_fixb1b_fixf10_fixf19_mw1_33 $( [ -d "$TC/variant_fixb26_fixb1b_fixf10_fixf19_mw1_33" ] && echo present || echo absent ) at $(u)" > $OUT/warm.txt
log "$(cat $OUT/warm.txt)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the tag binary failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the $BK copy for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*' > $OUT/env_shell_after_unset.txt
log "enter_scene start (level $LV, bin $BK, kind $KIND, sd $SD, timeout $TO, hold $H, $REC, cache $BASE save $SAVE, knobs ${KX//KYTY_KEYS=*/KYTY_KEYS=<seal>}); shell KYTY_*/VK_LAYER_* after unset: $(wc -l < $OUT/env_shell_after_unset.txt)"
python $G/guard_m3a.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
python $G/hold_m3a.py watch --pidfile $OUT/game_pid.txt --flag $OUT/VM_FOUND --stop $OUT/watch.stop > $OUT/hold_watch.txt 2>&1 &
HPID=$!
F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout $TO --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL $REC --hold $H $KX > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID; wait $HPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200); hold watch: $(tail -1 $OUT/hold_watch.txt | cut -c1-120)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_m3a.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
DL=$(cat $G/log_$T.txt $G/stdout_$T.txt 2>/dev/null | grep -a -c -i 'ErrorDeviceLost\|device lost')
if [ "${DL:-0}" != 0 ]; then
  echo "$(u) $T device lost lines $DL (item 760 (b)(2) analogue)" > $G/SERIES_STOP
  log "DEVICE LOST lines $DL in the log/stdout - SERIES_STOP, no repeat, question to the lead (item 760 (b)(2))"
fi
if [ "$SAVE" != none ] && [ ! -e $OUT/USER_FOUND ] && [ ! -e $OUT/VM_FOUND ] && grep -q -- '--- attempt 1: launching' $OUT/run.txt; then
  KS=$(echo $SAVE | tr 'A-Z' 'a-z')
  rm -rf $G/$KS.new; mkdir -p $G/$KS.new
  for d in $DIRS GLCache; do LIVE=$(live_of $d); [ -d "$LIVE" ] && { mv "$LIVE" "$G/$KS.new/$d" || { log "move of live $d into $KS.new failed"; exit 1; }; }; done
  python $G/manifest_fs4c.py $G/$KS.new/$KS.tsv $(kmf $KS.new) > $G/$KS.new/$KS.txt 2>&1
  cp $G/$KS.new/$KS.tsv $OUT/manifest_run.tsv
  rm -rf $G/$KS.prev; [ -d $G/$KS ] && mv $G/$KS $G/$KS.prev; mv $G/$KS.new $G/$KS && SAVED=1
  log "the run state saved as $SAVE: $(head -1 $G/$KS/$KS.txt | cut -c1-160) (previous in $KS.prev)"
fi
exit 0
