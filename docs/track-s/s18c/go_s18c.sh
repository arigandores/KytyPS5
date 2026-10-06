#!/bin/bash
# Track S link S18c (HPP-644; ROADMAP s122 item 569 (d)(3)-(4), item 571 (g)(3), item 576 (e), item 579 (v)): ONE tag of the S-replay shipment
# series on the S18a2 binary b3cee576 (code 0005e11f).  Port of the S17c2 harness go_s17c2.sh (C:/kyty/s288/s17c2): the same lock, gate,
# guard of the user game (item 534, general rule 33: no kill by image name, the own emulator tree by pid only), copy and return of the
# caches with the manifest equality line; changed: the 25 tags of the seal docs/track-s/s18c.md, the input states below, the save of the
# whole run state of the caches (SAVE=all) and its restore (chain) - s18_r -> s18_e1 -> s18_e2 see the caches of the previous tag with no
# return between them (item 569 (d)(4)), while the installed caches are returned after every tag; the gate of the next capture tag on
# the line 'ACCUMULATION <prev> OK' of the reading of the previous one (item 569 (d)(3): a breach stops the series - question to the lead)
# and of s18_c02 / s18_r on 'SIGNATURE_571G3 <tag> OK' (item 571 (g)(3)); KYTY_S_REPLAY_TEST refused in the calling environment of the
# shipment tags (item 576 (e)(3)).  ONE TAG = ONE LOCK.
# INPUT STATES (seal section 3) in the live _ShaderCache/PPSA21564 after the copy (IN), runs/<tag>/state_in.txt:
#   cap0      f10 and replay removed (s18_c01);
#   cap_acc   f10 and replay removed, replay <- state/<previous capture tag>/replay (accumulation, the folder is never cleared);
#   cat_full  f19 and replay removed, replay <- state/s18_c19/replay (s18_ks, s18_r, s18_w);
#   chain     the live _ShaderCache, _PipelineCache, _SaveData and GLCache replaced by state/<previous>/all/* (the run state of the previous
#             tag; runs/<tag>/chain_cmp.txt = manifest of the input vs runs/<previous>/manifest_run.tsv);
#   inst_cat  the installed caches as they are, replay <- state/s18_c19/replay (s18_v)
#   (f10 = variant_fixb26_fixb1b_fixf10, f19 = variant_fixb26_fixb1b_fixf10_fixf19 - under _ShaderCache/PPSA21564)
# FORMS (enter_scene.py <tag> --level <LV> --attempts 1 --stable-draws 100 --no-install --require-idle --gates-file gates_default.txt
#   --pred <seal> ... KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 + the pairs KV):
#   c: --timeout 600 --hold 330;  v: --timeout 600 --rec --hold 330;  p: --timeout 900 --until-prep;
#   w: --timeout 900 --emu-arg=--vulkan-validation --emu-arg=true --hold 310 + VK_LAYER_PATH VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000.
#   KYTY_SHADER_PREPARE, KYTY_GPU_CHECKPOINTS, KYTY_GAME_PATCH, KYTY_PIPELINE_PRECACHE and every other KYTY_FIX_* are never passed (KYTY_* and
#   VK_LAYER_* unset before the call).
# usage: bash C:/kyty/s288/s18c/go_s18c.sh <tag>   tags and order: s18_c01 .. s18_c19 s18_ks s18_r s18_e1 s18_e2 s18_v s18_w
#   (a tag starts only when runs/<previous> exists).  ASCII only.
# S18C_GO_ROOT (fixtures of test_tools_s18c.py only) moves the root; every fixture call ends before the seal check (no seal there).
# EXIT: 0 tag made (read it with post_s18c.sh); 1 hard refusal / return failed; 2 usage / the tag exists / order / input state missing /
#   gate line missing; 3 lock / user process; 4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=${S18C_GO_ROOT:-C:/kyty/s288/s18c}; S=C:/kyty/s288; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/s288/bin/kyty_emulator_b3cee576.exe
BIN_EXPECT=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a
FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b
FS8_PIN=C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe
SEAL=$G/pred/s18c_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
TC="$EMU/_ShaderCache/PPSA21564"
F10="$TC/variant_fixb26_fixb1b_fixf10"; F19="$TC/variant_fixb26_fixb1b_fixf10_fixf19"; RP="$TC/replay"
SKY=underwater_aerial_garden; MGG=mini_giants_garden
LEVELS=(title_controller_ship intro_next worldmap ps_logo hub_crashsite underwater_aerial_garden penguin_atlantis time_stopper_ghost_world
  rotating_level_day_and_night bumper_enemy_snowy_canyon big_hand_pirate_island timestop_casino mini_giants_garden ice_iceberg
  sponge_dirty_bath hoover_beach volcano_mountain voxel_world enemy_gorilla)
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
SAVE=""; H=0; PREV=""; GATE=""; VK=""; SRCD=""
CAPV="KYTY_S_REPLAY=2 KYTY_FIX_F19=0 KYTY_SHADER_SEED=0"
case "$T" in
  s18_c0[1-9]|s18_c1[0-9])
    K=$((10#${T#s18_c})); [ $K -ge 1 ] && [ $K -le 19 ] || { echo "usage: bad capture tag $T"; exit 2; }
    LV=${LEVELS[$((K-1))]}; FORM=c; H=330; KV="$CAPV"; SAVE="replay"
    if [ $K = 1 ]; then IN=cap0; else PREV=$(printf 's18_c%02d' $((K-1))); IN=cap_acc; SRCD=$G/state/$PREV; GATE="ACCUMULATION $PREV OK"; fi
    [ $K = 2 ] && GATE="$GATE|SIGNATURE_571G3 s18_c01 OK";;
  s18_ks) LV=$SKY; PREV=s18_c19; IN=cat_full; FORM=p; KV="KYTY_S_REPLAY=3 KYTY_FIX_F19=1 KYTY_AV_TRACE=1 KYTY_SHADER_SEED=0 KYTY_S_REPLAY_TEST=stop"
    SAVE="f19 replay"; GATE="ACCUMULATION s18_c19 OK";;
  s18_r)  LV=$SKY; PREV=s18_ks;  IN=cat_full; FORM=p; KV="KYTY_SHADER_SEED=0"; SAVE="all"; GATE="SIGNATURE_571G3 s18_ks OK";;
  s18_e1) LV=$SKY; PREV=s18_r;   IN=chain;    FORM=v; H=330; KV="KYTY_SHADER_SEED=0 KYTY_AV_TRACE=1"; SAVE="all"; SRCD=$G/state/s18_r;;
  s18_e2) LV=$MGG; PREV=s18_e1;  IN=chain;    FORM=v; H=330; KV="KYTY_SHADER_SEED=0 KYTY_AV_TRACE=1"; SRCD=$G/state/s18_e1;;
  s18_v)  LV=$SKY; PREV=s18_e2;  IN=inst_cat; FORM=v; H=330; KV="";;
  s18_w)  LV=$SKY; PREV=s18_v;   IN=cat_full; FORM=w; H=310; KV=""; VK="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000";;
  *) echo "usage: go_s18c.sh s18_c01..s18_c19|s18_ks|s18_r|s18_e1|s18_e2|s18_v|s18_w"; exit 2;;
esac
case "$IN" in cat_full|inst_cat) SRCD=$G/state/s18_c19;; esac
OUT=$G/runs/$T; TIMES=$G/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) S18c go_s18c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR" "_ShaderSeeds=$EMU/_ShaderSeeds")
[ -e $S/STOP ] && { log "STOP file: $(head -1 $S/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
case "$T" in s18_r|s18_e1|s18_e2|s18_v|s18_w)
  [ -n "${KYTY_S_REPLAY_TEST+x}" ] && { log "KYTY_S_REPLAY_TEST is set in the calling environment - refused (item 576 (e)(3))"; exit 2; };;
esac
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -e $G/state/$T ] && { echo "state/$T exists - a tag runs once"; exit 2; }
[ -z "$PREV" ] || [ -d $G/runs/$PREV ] || { echo "order: $PREV is not made"; exit 2; }
if [ -n "$GATE" ]; then
  IFS='|' read -ra GL <<< "$GATE"
  for g in "${GL[@]}"; do
    set -- $g
    grep -qx "  $g" $G/runs/$2/read.txt 2>/dev/null || { log "gate: line '$g' not in runs/$2/read.txt - not starting (item 569 (d)(3) / 571 (g)(3): question to the lead)"; exit 2; }
  done
fi
case "$IN" in
  cap_acc|cat_full|inst_cat) [ -f $SRCD/replay/replay.cur ] || { echo "input state $IN: $SRCD/replay/replay.cur missing"; exit 2; };;
  chain) [ -d $SRCD/all/_ShaderCache ] && [ -d $SRCD/all/GLCache ] && [ -f $G/runs/$PREV/manifest_run.tsv ] || { echo "input state chain: $SRCD/all or runs/$PREV/manifest_run.tsv missing"; exit 2; };;
esac
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
WANT=$(sha "$GAME")
case "$WANT" in
  $FS8) PINNED=$FS8_PIN;;
  *) log "installed binary $WANT is not FS8 2c9b69b9 - not starting"; exit 1;;
esac
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != installed $WANT - not starting"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "S18a2 copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
[ -e "$RP" ] && { log "the installed caches carry a replay folder $RP - not starting (the installed state has none)"; exit 1; }
GS=$(python $G/guard_s18c.py scan) || { python $G/guard_s18c.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "S18c HPP-644 go_s18c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_s18c.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_s18c.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
INSTALLED=0; COPIED=""; SAVED=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_s18c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS=$(python $G/guard_s18c.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_s18c.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
    fi
  fi
  if [ -n "$COPIED" ] && [ "$SAVED" = 0 ]; then
    SAVED=1
    python $G/state_s17c.py > $OUT/state_out.txt 2>&1
    log "state after the run (before the return): $(tr '\n' ';' < $OUT/state_out.txt | cut -c1-300)"
    python $G/manifest_fs4c.py $OUT/mf_out.tsv "f19=$F19" "replay=$RP" > $OUT/mf_out.txt 2>&1
    log "S-replay folders after the run (mf_out.tsv): $(head -1 $OUT/mf_out.txt | cut -c1-200)"
    if [ -n "$SAVE" ] && [ -f $OUT/run.txt ]; then
      mkdir -p $G/state/$T
      for x in $SAVE; do
        case $x in
          replay) if [ -d "$RP" ]; then cp -a "$RP" $G/state/$T/replay || OK=0; fi;;
          f19) if [ -d "$F19" ]; then cp -a "$F19" $G/state/$T/f19 || OK=0; fi;;
          all) mkdir -p $G/state/$T/all
               for d in $DIRS GLCache; do
                 if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
                 if [ -d "$LIVE" ]; then cp -a "$LIVE" $G/state/$T/all/$d || OK=0; fi
               done
               if [ -d "$RP" ]; then cp -a "$RP" $G/state/$T/replay || OK=0; fi;;
        esac
      done
      log "state saved to state/$T: $(ls $G/state/$T | tr '\n' ' ') ($(du -sm $G/state/$T | awk '{print $1}') MB)"
    fi
  fi
  if [ "$INSTALLED" = "1" ] || [ "$(sha "$GAME")" != "$WANT" ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$WANT" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$WANT" ]; then log "installed binary returned from the pinned copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$WANT" ] || { OK=0; log "INSTALLED BINARY differs after the tag"; }
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
    for d in $DIRS; do
      case " $COPIED " in *" $d "*) ;; *) [ -e "$EMU/$d" ] && { rm -rf "$EMU/$d" || OK=0; log "$d was absent before the tag - removed at the return";};; esac
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
      UF=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_s18c.py close user_found > /dev/null
      STAMP=$(date -u +%H%M%S); mv $OUT $OUT.user_$STAMP; [ -e $G/state/$T ] && mv $G/state/$T $G/state/$T.user_$STAMP
      log "user process during the tag ($UF) - block closed, interference, repeat by the same name (item 534)"
    elif [ ! -f $OUT/run.txt ]; then
      STAMP=$(date -u +%H%M%S); mv $OUT $OUT.nostart_$STAMP; [ -e $G/state/$T ] && mv $G/state/$T $G/state/$T.nostart_$STAMP
      log "enter_scene never started - interference, repeat by the same name (item 534)"
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
  if [ "$d" = "GLCache" ]; then SRCDIR="$GLDIR"; else SRCDIR="$EMU/$d"; fi
  [ -d "$SRCDIR" ] || { log "$d absent - not copied (manifest line MISSING)"; continue; }
  cp -a "$SRCDIR" "$OUT/before_$d" || { log "copy of $d failed - not starting"; rm -rf "$OUT/before_$d"; exit 1; }
  COPIED="$COPIED $d"
done
log "caches, saves and GLCache copied:$COPIED ($(du -sm $OUT/before_* | awk '{print $1}' | tr '\n' '/') MB)"
case "$IN" in
  cap0) rm -rf "$F10" "$RP";;
  cap_acc) rm -rf "$F10" "$RP"; cp -a $SRCD/replay "$RP" || { log "input state $IN: copy of $SRCD/replay failed - not starting"; exit 1; };;
  cat_full) rm -rf "$F19" "$RP"; cp -a $SRCD/replay "$RP" || { log "input state $IN: copy of $SRCD/replay failed - not starting"; exit 1; };;
  inst_cat) rm -rf "$RP"; cp -a $SRCD/replay "$RP" || { log "input state $IN: copy of $SRCD/replay failed - not starting"; exit 1; };;
  chain)
    for d in $DIRS GLCache; do
      if [ "$d" = "GLCache" ]; then LIVE="$GLDIR"; else LIVE="$EMU/$d"; fi
      rm -rf "$LIVE"
      if [ -d $SRCD/all/$d ]; then cp -a $SRCD/all/$d "$LIVE" || { log "input state chain: copy of $SRCD/all/$d failed - not starting"; exit 1; }; fi
    done;;
esac
python $G/state_s17c.py > $OUT/state_in.txt 2>&1 || { log "state_s17c.py failed - not starting"; exit 1; }
echo "$IN" > $OUT/state_in_name.txt
python $G/manifest_fs4c.py $OUT/mf_in.tsv "f19=$F19" "replay=$RP" > $OUT/mf_in.txt 2>&1 || { log "manifest of the S-replay folders failed - not starting"; exit 1; }
if [ "$IN" = chain ]; then
  python $G/manifest_fs4c.py $OUT/manifest_in.tsv "${MF[@]}" > $OUT/manifest_in.txt 2>&1
  python $G/manifest_fs4c.py --cmp $G/runs/$PREV/manifest_run.tsv $OUT/manifest_in.tsv > $OUT/chain_cmp.txt 2>&1
  log "chain input vs run state of $PREV: $(head -1 $OUT/chain_cmp.txt | cut -c1-200)"
fi
log "input state $IN: $(tr '\n' ';' < $OUT/state_in.txt | cut -c1-300); mf_in: $(head -1 $OUT/mf_in.txt | cut -c1-160)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the S18a2 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the S18a2 copy for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
COMMON="--level $LV --attempts 1 --stable-draws 100 --no-install --require-idle --gates-file $G/gates_default.txt --pred $SEAL"
case "$FORM" in
  c) FA="--timeout 600 --hold $H";;
  v) FA="--timeout 600 --rec --hold $H";;
  p) FA="--timeout 900 --until-prep";;
  w) FA="--timeout 900 --emu-arg=--vulkan-validation --emu-arg=true --hold $H";;
esac
log "enter_scene start (level $LV, form $FORM, $FA, $KV $VK)"
python $G/guard_s18c.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
S17C_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T $COMMON $FA $KV $VK KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_s18c.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
