#!/bin/bash
# Track S link S18c2 (HPP-654; ROADMAP s122 item 586 (g)-(d)): the one extra tag s18_w2 of the S-replay shipment series - W Sky Garden
# with the rebuild under the validation layer on the S18a2 binary b3cee576.  Derived from the S18c harness go_s18c.sh by mk_s18c2.py:
# the same lock, gate, guard of the user game (item 534, general rule 33), copy and return of the caches with the manifest equality
# line (the manifest covers _ShaderCache with replay/, _PipelineCache, _SaveData, GLCache and _ShaderSeeds); changed: the tag s18_w2
# only, the root C:/kyty/s288/s18c2, the seal pred/s18c2_seal.md, the input cat_full from the catalogue C:/kyty/s288/s18c/replay_known
# (exactly the 3 files of the manifest c644e3ad by sha256, else exit 2 before the lock), KYTY_SHADER_SEED=0 (the seeds of _ShaderSeeds
# are not installed - the model of a signature change, item 586 (g)), KYTY_S_REPLAY and KYTY_S_REPLAY_TEST never passed (the latter
# refused in the calling environment, item 576 (e)(3)).  ONE TAG = ONE LOCK.
# INPUT STATE cat_full (in the live _ShaderCache/PPSA21564 after the copy): variant_fixb26_fixb1b_fixf10_fixf19 and replay removed,
#   replay <- C:/kyty/s288/s18c/replay_known.
# FORM w: enter_scene.py s18_w2 --level underwater_aerial_garden --attempts 1 --stable-draws 100 --no-install --require-idle
#   --gates-file gates_default.txt --pred <seal> --timeout 900 --emu-arg=--vulkan-validation --emu-arg=true --hold 310
#   KYTY_SHADER_SEED=0 VK_LAYER_PATH VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (KYTY_* and
#   VK_LAYER_* unset before the call; precache at the default, no message filter).
# usage: bash C:/kyty/s288/s18c2/go_s18c2.sh s18_w2      ASCII only.
# S18C2_GO_ROOT / S18C2_GO_SRC (fixtures of test_tools_s18c2.py only) move the roots; every fixture call ends before the seal check.
# EXIT: 0 tag made (read it with post_s18c2.sh); 1 hard refusal / return failed; 2 usage / the tag exists / input state / catalogue
#   differs from the manifest; 3 lock / user process; 4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=${S18C2_GO_ROOT:-C:/kyty/s288/s18c2}; SRCG=${S18C2_GO_SRC:-C:/kyty/s288/s18c}; S=C:/kyty/s288; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/s288/bin/kyty_emulator_b3cee576.exe
BIN_EXPECT=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a
FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b
FS8_PIN=C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe
SEAL=$G/pred/s18c2_seal.md
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
  s18_w2) LV=$SKY; IN=cat_full; FORM=w; H=310; KV="KYTY_SHADER_SEED=0"; VK="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000";;
  *) echo "usage: go_s18c2.sh s18_w2"; exit 2;;
esac
SRCD=$SRCG/replay_known
KNOWN="replay.45.bin:12cb378741308d1a82133be521311882881d1bbf04aff649cccc6d8e6607fee1 replay.46.bin:332a2f2d6aef0e8b64ccfe366d87df3476117abaf3b6aaf736ffbec2befc7c9a replay.cur:a5331f18877e9e1543361e44b4cb0a1f5f0ed5f8297d850bf1fcc68bd7a3ab5f"
OUT=$G/runs/$T; TIMES=$G/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) S18c2 go_s18c2 $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR" "_ShaderSeeds=$EMU/_ShaderSeeds")
[ -e $S/STOP ] && { log "STOP file: $(head -1 $S/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
case "$T" in s18_w2)
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
[ -d $SRCD ] || { echo "input state cat_full: $SRCD missing"; exit 2; }
[ "$(ls $SRCD | tr '\n' ' ')" = "replay.45.bin replay.46.bin replay.cur " ] || { log "input state cat_full: the files of $SRCD differ from the manifest c644e3ad - not starting"; exit 2; }
for f in $KNOWN; do
  [ "$(sha $SRCD/${f%%:*})" = "${f#*:}" ] || { log "input state cat_full: $SRCD/${f%%:*} sha256 differs from the manifest c644e3ad - not starting"; exit 2; }
done
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
GS=$(python $G/guard_s18c2.py scan) || { python $G/guard_s18c2.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "S18c2 HPP-654 go_s18c2.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_s18c2.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_s18c2.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
INSTALLED=0; COPIED=""; SAVED=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_s18c2.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS=$(python $G/guard_s18c2.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_s18c2.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
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
      UF=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_s18c2.py close user_found > /dev/null
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
  cat_full) rm -rf "$F19" "$RP"; cp -a $SRCD "$RP" || { log "input state $IN: copy of $SRCD failed - not starting"; exit 1; };;
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
python $G/guard_s18c2.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
S17C_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T $COMMON $FA $KV $VK KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_s18c2.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
