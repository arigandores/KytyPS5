#!/bin/bash
# Track S link S17c2 (HPP-640; ROADMAP s122 item 561 (d), items 565 (g), 566 (v)(g)): ONE tag of the S-replay series, seal edition 4, on the
# S17a5 binary 43ef1cc1 (code c0057ccb).  Port of the S17c harness go_s17c.sh edition 3 (C:/kyty/s288/s17c): the same lock, gate, guard of the
# user game (item 534, general rule 33: no kill by image name, the own emulator tree by pid only), copy and return of the caches with the
# manifest equality line; changed: the eight tags of item 561 (d)(2) on two levels, KYTY_SHADER_SEED=0 at every tag (item 561 (d)(3)), the
# manifests of the S-replay folders (f19, replay) before the tag (runs/<tag>/mf_in.tsv) and after the run before the return
# (runs/<tag>/mf_out.tsv) - the identity admission of item 566 (g); _ShaderSeeds is in the manifest of the caches (read only, not copied).
# ONE TAG = ONE LOCK.
# S-REPLAY STATE (seal section 3) in the live _ShaderCache/PPSA21564 after the copy (IN), runs/<tag>/state_in.txt; after the exit, before the
# return, runs/<tag>/state_out.txt and the directories of SAVE copied to state/<tag>/:
#   empty_f10  f10 and replay removed;  empty_f19  f19 and replay removed;
#   cat_c2     f19 and replay removed, replay <- s17c/state/s17c_c2/replay (edition 3 capture, Sky Garden);
#   k_ks2      f19 <- state/s17c_ks2/f19 (absent allowed), replay <- state/s17c_ks2/replay;
#   cat_c2h    f19 and replay removed, replay <- state/s17c_c2h/replay;  rb_r3h  f19 <- state/s17c_r3h/f19, replay <- state/s17c_r3h/replay
#   (f10 = variant_fixb26_fixb1b_fixf10, f19 = variant_fixb26_fixb1b_fixf10_fixf19 - under _ShaderCache/PPSA21564)
# FORMS (enter_scene.py <tag> --level <LV> --attempts 1 --stable-draws 300 --no-install --require-idle --gates-file gates_default.txt
#   --pred <seal> ... KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 + the pairs KV):
#   v: --timeout 480 --rec --hold H;  n: --timeout 480 --hold H;  p: --timeout 900 --until-prep.  KYTY_SHADER_PREPARE, KYTY_GPU_CHECKPOINTS,
#   KYTY_GAME_PATCH, KYTY_PIPELINE_PRECACHE and every other KYTY_FIX_* are never passed (KYTY_* and VK_LAYER_* unset before the call).
# usage: bash C:/kyty/s288/s17c2/go_s17c2.sh <tag>   tags and order: s17c_r3b s17c_rsb s17c_ks2 s17c_kn2 s17c_c2h s17c_n0h s17c_r3h s17c_e3h
#   (a tag starts only when runs/<previous> exists).  ASCII only.
# EXIT: 0 tag made (read it with post_s17c2.sh); 1 hard refusal / return failed; 2 usage / the tag exists / order / input state missing;
#   3 lock / user process; 4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/s288/s17c2; E3=C:/kyty/s288/s17c; S=C:/kyty/s288; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/s288/bin/kyty_emulator_43ef1cc1.exe
BIN_EXPECT=43ef1cc14ec2c116fdcce9ac71f9d854d0ec6498bd6e538fa479b1ecdf57fbb3
FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b
FS8_PIN=C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe
SEAL=$G/pred/s17c2_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
TC="$EMU/_ShaderCache/PPSA21564"
F10="$TC/variant_fixb26_fixb1b_fixf10"; F19="$TC/variant_fixb26_fixb1b_fixf10_fixf19"; RP="$TC/replay"
SKY=underwater_aerial_garden; HB=hoover_beach
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
SAVE=""; H=0; PREV=""
R3="KYTY_S_REPLAY=3 KYTY_FIX_F19=1 KYTY_AV_TRACE=1 KYTY_SHADER_SEED=0"
case "$T" in
  s17c_r3b) LV=$SKY;                IN=cat_c2;    FORM=p;        KV="$R3"; SAVE="f19 replay";;
  s17c_rsb) LV=$SKY; PREV=s17c_r3b; IN=cat_c2;    FORM=p;        KV="$R3 KYTY_S_REPLAY_TEST=spec"; SAVE="f19 replay";;
  s17c_ks2) LV=$SKY; PREV=s17c_rsb; IN=cat_c2;    FORM=p;        KV="$R3 KYTY_S_REPLAY_TEST=stop"; SAVE="f19 replay";;
  s17c_kn2) LV=$SKY; PREV=s17c_ks2; IN=k_ks2;     FORM=n; H=60;  KV="$R3";;
  s17c_c2h) LV=$HB;  PREV=s17c_kn2; IN=empty_f10; FORM=v; H=330; KV="KYTY_S_REPLAY=2 KYTY_FIX_F19=0 KYTY_SHADER_SEED=0"; SAVE="replay f10";;
  s17c_n0h) LV=$HB;  PREV=s17c_c2h; IN=empty_f19; FORM=v; H=330; KV="KYTY_S_REPLAY=0 KYTY_FIX_F19=1 KYTY_AV_TRACE=1 KYTY_SHADER_SEED=0"; SAVE="f19";;
  s17c_r3h) LV=$HB;  PREV=s17c_n0h; IN=cat_c2h;   FORM=p;        KV="$R3"; SAVE="f19 replay";;
  s17c_e3h) LV=$HB;  PREV=s17c_r3h; IN=rb_r3h;    FORM=v; H=330; KV="$R3";;
  *) echo "usage: go_s17c2.sh s17c_r3b|s17c_rsb|s17c_ks2|s17c_kn2|s17c_c2h|s17c_n0h|s17c_r3h|s17c_e3h"; exit 2;;
esac
case "$IN" in
  cat_c2) SRCD=$E3/state/s17c_c2;; k_ks2) SRCD=$G/state/s17c_ks2;; cat_c2h) SRCD=$G/state/s17c_c2h;; rb_r3h) SRCD=$G/state/s17c_r3h;;
  *) SRCD="";;
esac
OUT=$G/runs/$T; TIMES=$G/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) S17c2 go_s17c2 $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR" "_ShaderSeeds=$EMU/_ShaderSeeds")
[ -e $S/STOP ] && { log "STOP file: $(head -1 $S/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -e $G/state/$T ] && { echo "state/$T exists - a tag runs once"; exit 2; }
[ -z "$PREV" ] || [ -d $G/runs/$PREV ] || { echo "order: $PREV is not made"; exit 2; }
if [ -n "$SRCD" ]; then
  [ -f $SRCD/replay/replay.cur ] || { echo "input state $IN: $SRCD/replay/replay.cur missing"; exit 2; }
  [ "$IN" != rb_r3h ] || [ -d $SRCD/f19 ] || { echo "input state $IN: $SRCD/f19 missing"; exit 2; }
fi
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
WANT=$(sha "$GAME")
case "$WANT" in
  $FS8) PINNED=$FS8_PIN;;
  *) log "installed binary $WANT is not FS8 2c9b69b9 (seal edition 4) - not starting"; exit 1;;
esac
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != installed $WANT - not starting"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "S17a5 copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
GS=$(python $G/guard_s17c2.py scan) || { python $G/guard_s17c2.py close user_found > /dev/null; log "user emulator or launcher lives - not starting, block closed (item 534): $GS"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "S17c2 HPP-640 go_s17c2.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
GS=$(python $G/guard_s17c2.py scan) || { rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_s17c2.py close user_found > /dev/null; log "user emulator or launcher found right after the lock - lock released, files untouched, block closed, interference (item 534): $GS"; exit 3; }
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
INSTALLED=0; COPIED=""; SAVED=0
finish() {
  RCX=$?
  OK=1
  if [ -f $OUT/game_pid.txt ]; then
    KO=$(python $G/guard_s17c2.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "$KO (at the exit)"; sleep 5;; esac
  fi
  if [ -n "$COPIED" ]; then
    GS=$(python $G/guard_s17c2.py scan --pidfile $OUT/game_pid.txt)
    if [ $? != 0 ] || [ -e $OUT/USER_FOUND ]; then
      log "user process at the return ($GS) - caches and GLCache wait for its exit, poll 10 s, the lock stays (item 534)"
      log "$(python $G/guard_s17c2.py wait-gone --pidfile $OUT/game_pid.txt --poll 10 | tail -1)"
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
          f10) if [ -d "$F10" ]; then cp -a "$F10" $G/state/$T/f10 || OK=0; fi;;
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
      UF=$(head -1 $OUT/USER_FOUND | cut -c1-160); python $G/guard_s17c2.py close user_found > /dev/null
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
  empty_f10) rm -rf "$F10" "$RP";;
  empty_f19) rm -rf "$F19" "$RP";;
  cat_c2|cat_c2h|k_ks2|rb_r3h)
    rm -rf "$F19" "$RP"
    cp -a $SRCD/replay "$RP" || { log "input state $IN: copy of $SRCD/replay failed - not starting"; exit 1; }
    if [ -d $SRCD/f19 ] && { [ "$IN" = k_ks2 ] || [ "$IN" = rb_r3h ]; }; then
      cp -a $SRCD/f19 "$F19" || { log "input state $IN: copy of $SRCD/f19 failed - not starting"; exit 1; }
    fi;;
esac
python $G/state_s17c.py > $OUT/state_in.txt 2>&1 || { log "state_s17c.py failed - not starting"; exit 1; }
echo "$IN" > $OUT/state_in_name.txt
python $G/manifest_fs4c.py $OUT/mf_in.tsv "f19=$F19" "replay=$RP" > $OUT/mf_in.txt 2>&1 || { log "manifest of the S-replay folders failed - not starting"; exit 1; }
log "input state $IN: $(tr '\n' ';' < $OUT/state_in.txt | cut -c1-300); mf_in: $(head -1 $OUT/mf_in.txt | cut -c1-160)"
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the S17a5 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the S17a5 copy for the tag: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
COMMON="--level $LV --attempts 1 --stable-draws 300 --no-install --require-idle --gates-file $G/gates_default.txt --pred $SEAL"
case "$FORM" in
  v) FA="--timeout 480 --rec --hold $H";;
  n) FA="--timeout 480 --hold $H";;
  p) FA="--timeout 900 --until-prep";;
esac
log "enter_scene start (level $LV, form $FORM, $FA, $KV)"
python $G/guard_s17c2.py watch --pidfile $OUT/game_pid.txt --flag $OUT/USER_FOUND --stop $OUT/watch.stop > $OUT/guard_watch.txt 2>&1 &
WPID=$!
S17C_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py $T $COMMON $FA $KV KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
ESRC=$?
touch $OUT/watch.stop; wait $WPID
log "enter_scene rc $ESRC; guard watch: $(tail -1 $OUT/guard_watch.txt | cut -c1-200)"
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
KO=$(python $G/guard_s17c2.py kill-own --pidfile $OUT/game_pid.txt); case "$KO" in *killed*) log "own emulator still lived after the run: $KO"; sleep 5;; esac
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
