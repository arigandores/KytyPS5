#!/bin/bash
# Track F link FS8c (HPP-573; ROADMAP s122 item 471 (g)(3), item 530 (g)(d)): the tags fs8_v, fs8_w, fs8_ef of the FS8 ship binary 2c9b69b9
# (worktree 302347b4 = FS7a d6ee2dc8 + fcaf141b + 082d1612 + tests part of ff953d4f + f98e842c + FS8a e46f55d4 + 7719d0f2; items 523, 527;
# version ...-1889-g302347b4) at the defaults of the binary (KYTY_FIX_F19 = 1 by default).  ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).
# Port of C:/kyty/f287/fs7c/go_fs7c.sh (FS7c HPP-567: stop file, lock, live emulator, procload through the <app> mask, runs/lock.log UTC,
# caches _ShaderCache with PPSA21564/pipelines.bin, _PipelineCache, _SaveData and the driver GLCache copied before and returned after,
# manifest sha256 before the tag, of the run state and after the return with the equality line; RETURN_FAILED keeps the lock; the installed
# FS6 9325446c checked before, inside the lock and after the return from its pinned copy) with the tag forms of F14g go_f14g.sh (f19_v1,
# f19_w1, f19_ef) WITHOUT KYTY_FIX_F19: the directory variant_fixb26_fixb1b_fixf10_fixf19 must be absent before every tag (cold form,
# item 471 (g)(3)); the FS8 copy 2c9b69b9 is installed for the tag only, known by sha256 (item 530 (g) N1).  No reference manifest of a
# first tag (the F14g RC6 form) - the member is before = after the return of every tag (item 471 (g)(3)).  Nothing is removed by this
# script except the live cache dirs replaced by their copies at the return.
# usage: bash C:/kyty/f287/fs8c/go_fs8c.sh <fs8_v|fs8_w|fs8_ef>
#   FORMS (seal docs/track-f/fs8c.md section 3 = pred/fs8c_seal.md): enter_scene.py <tag> --level <L> --attempts 1 --no-install
#   --require-idle --gates-file gates_default.txt --pred <seal> plus:
#     fs8_v:  underwater_aerial_garden --stable-draws 300 --timeout 480 --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#     fs8_w:  underwater_aerial_garden --stable-draws 300 --timeout 600 --emu-arg=--vulkan-validation --emu-arg=true --hold 310
#             VK_LAYER_PATH VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#             (W of item 295 (b): precache by default, no VK_LAYER_MESSAGE_ID_FILTER, no video)
#     fs8_ef: enemy_final --stable-draws 100 --timeout 480 --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
#   No KYTY_FIX_* at all, no KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS (enter_scene.py builds the env from the positional pairs; this script
#   unsets KYTY_* and VK_LAYER_* before the call).  Exit: WM_CLOSE at the end of the hold, CLOSE_WAIT_S 40 s.  ASCII only.
# EXIT: 0 tag made (read it with post_fs8c.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/fs8c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe
BIN_EXPECT=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b
PINNED=C:/kyty/f287/bin/kyty_emulator_9325446c.exe
WANT=9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2
SEAL=$G/pred/fs8c_seal.md
VKLAYER="C:/VulkanSDK/1.4.357.0/Bin"
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
FIXDIR="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19"
SKY=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  fs8_v|fs8_w) LV=$SKY; SD=300;;
  fs8_ef) LV=enemy_final; SD=100;;
  *) echo "usage: go_fs8c.sh <fs8_v|fs8_w|fs8_ef>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) FS8c go_fs8c $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not 9325446c before the tag - not starting"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "FS8 copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ -e "$FIXDIR" ] && { log "$FIXDIR exists before the tag - not starting (cold form)"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "FS8c HPP-573 go_fs8c.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/runs/lock.log
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
INSTALLED=0; COPIED=""
finish() {
  RCX=$?
  OK=1
  if tasklist //FI "IMAGENAME eq kyty_emulator.exe" 2>/dev/null | grep -qi kyty_emulator; then
    taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; log "kyty_emulator.exe killed at the exit (taskkill)"; sleep 5
  fi
  if [ "$INSTALLED" = "1" ] || [ "$(sha "$GAME")" != "$WANT" ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$WANT" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$WANT" ]; then log "installed binary returned from the pinned copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary after the tag: $(cat $OUT/installed_after.txt)"
  [ "$(cat $OUT/installed_after.txt)" = "$WANT" ] || OK=0
  if [ -f $OUT/manifest_before.tsv ] && [ -n "$COPIED" ]; then
    ls "$EMU/_ShaderCache/PPSA21564" > $OUT/variant_dirs_run.txt 2>&1
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
    [ -e "$FIXDIR" ] && { OK=0; log "$FIXDIR still exists after the return"; }
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
ls "$EMU/_ShaderCache/PPSA21564" > $OUT/variant_dirs.txt 2>&1
if [ -e "$FIXDIR" ]; then W=present; else W=absent; fi
echo "cold form: $FIXDIR $W at $(u); entries of _ShaderCache/PPSA21564: $(ls "$EMU/_ShaderCache/PPSA21564" | wc -l)" > $OUT/cold.txt
log "$(cat $OUT/cold.txt)"
[ "$W" = "absent" ] || { log "not cold - not starting"; exit 1; }
INSTALLED=1
cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "install of the FS8 copy failed - not starting"; exit 1; }
sha "$GAME" > $OUT/installed_sha.txt
log "installed the FS8 copy: $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
case "$T" in
  fs8_v|fs8_ef)
    log "enter_scene start (level $LV, SD $SD, --rec, hold 330, defaults of FS8 - no KYTY_FIX_*)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  fs8_w)
    log "enter_scene start (level $LV, W of item 295 (b), hold 310, defaults of FS8 - no KYTY_FIX_*)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws $SD --timeout 600 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --emu-arg=--vulkan-validation --emu-arg=true --hold 310 \
      VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
esac
log "run: $(grep '^VERDICT: ' $OUT/run.txt | tail -1 | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
exit 0
