#!/bin/bash
# Track F link F13a (HPP-479; ROADMAP s122 item 391 (z)): B41 - the black screen of ending_boss_after_credit after the "THE END" card.
# ONE TAG = ONE LOCK (queue P > F > S, item 322 (g)).  Port of C:/kyty/f287/fs4c/go_fs4c.sh (stop file, lock, live emulator, procload
# through the <app> mask, lock.log UTC, caches, _SaveData and GLCache copied before and returned after, manifest sha256 of all caches
# before the tag and after their return with the equality line, RETURN_FAILED keeps the lock) and of C:/kyty/f287/f7a/go_f7a.sh (the
# RenderDoc capture moved out of _RenderDoc, thumbnail, rd_list.py replay with a watchdog INSIDE the lock, before the cache return).
# NO INSTALL: the installed 540c035a runs as it is (item 374; sha256 before the lock, inside, and at the end; the pinned copy
# C:/kyty/f287/bin/kyty_emulator_540c035a.exe puts it back only if the installed file changed).  Nothing is removed from the caches
# (the form as it is installed; whether the scene translated new programs is the manifest row 'run vs before').
# usage: bash C:/kyty/f287/f13a/go_f13a.sh <f13_rd|f13_k>
#   FORMS (seal docs/track-f/f13a.md section 3 = pred/f13a_seal.md):
#     f13_rd: enter_scene.py <tag> --level ending_boss_after_credit --attempts 1 --stable-draws 300 --timeout 480 --no-install
#        --require-idle --gates-file gates_default.txt --pred <seal> --emu-arg=--rd --hold 240 KYTY_RD_LEVEL=ending_boss_after_credit
#        KYTY_RD_LEVEL_FRAME=2400 KYTY_RD_FLIPS=2 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (no video, no input, no validation)
#     f13_k: enter_scene.py <tag> --level ending_boss_after_credit --attempts 1 --stable-draws 300 --timeout 480 --no-install
#        --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 240
#        KYTY_KEYS=75:J,90:J,105:J,120:L,135:L,150:L KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (video, no validation)
#   KYTY_GPU_CHECKPOINTS, KYTY_GAME_PATCH, KYTY_FIX_* and every other KYTY_* are never passed (enter_scene.py builds the env from the
#   positional pairs; this script unsets KYTY_* and VK_LAYER_* before the call).  ASCII only.
# EXIT: 0 tag made (read it with f13a_read.py); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / live emulator;
#   4 stop file; 5 procload busy.
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f13a; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
PINNED=C:/kyty/f287/bin/kyty_emulator_540c035a.exe
WANT=540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1
SEAL=$G/pred/f13a_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
RDDIR="$EMU/_RenderDoc"
RDHOME="/c/Program Files/RenderDoc"
RDLIST=C:/kyty/scripts/rd_list.py
RDMAX=1800
LV=ending_boss_after_credit
NRD=2400
KEYS="75:J,90:J,105:J,120:L,135:L,150:L"
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
case "$T" in
  f13_rd|f13_k) ;;
  *) echo "usage: go_f13a.sh <f13_rd|f13_k>"; exit 2;;
esac
OUT=$G/runs/$T; TIMES=$F/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) F13a go_f13a $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
[ "$(sha $PINNED)" = "$WANT" ] || { log "pinned copy $PINNED sha != $WANT - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$WANT" ] || { log "installed binary is not 540c035a before the tag - not starting"; exit 1; }
[ -d "$GLDIR" ] || { log "no GLCache dir - not starting"; exit 1; }
if [ "$T" = "f13_rd" ]; then
  for X in "$RDHOME/renderdoc.dll" "$RDHOME/qrenderdoc.exe" "$RDHOME/renderdoccmd.exe" "$RDLIST"; do
    [ -f "$X" ] || { log "renderdoc file $X missing - not starting"; exit 1; }
  done
  [ -e $G/$T.rdc ] && { log "$G/$T.rdc exists - not starting"; exit 2; }
fi
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
tasklist //FI "IMAGENAME eq qrenderdoc.exe" | grep -qi qrenderdoc && { log "a qrenderdoc lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "F13a HPP-479 go_f13a.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/lock.log
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
sha "$GAME" > $OUT/installed_sha.txt
log "installed binary inside the lock: $(cat $OUT/installed_sha.txt) (no install in F13a)"
COPIED=""
finish() {
  RCX=$?
  OK=1
  if tasklist //FI "IMAGENAME eq qrenderdoc.exe" 2>/dev/null | grep -qi qrenderdoc; then
    taskkill //F //IM qrenderdoc.exe > /dev/null 2>&1; log "qrenderdoc.exe killed at the exit (taskkill)"; sleep 3
  fi
  if [ "$(sha "$GAME")" != "$WANT" ]; then
    for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$WANT" ] && break; sleep 5; done
    if [ "$(sha "$GAME")" = "$WANT" ]; then log "installed binary had changed - returned from the pinned copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi
  else
    log "installed binary at the end: $WANT (unchanged)"
  fi
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
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/lock.log; log "lock released (rc $RCX)"
  else
    echo "$(u) $T" > $G/RETURN_FAILED; log "return incomplete or manifest differs - the lock stays"; RCX=1
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
log "variant entries of _ShaderCache/PPSA21564: $(tr '\n' ' ' < $OUT/variant_dirs.txt | cut -c1-300)"
RDB=$(ls "$RDDIR"/*.rdc 2>/dev/null | sort | tr '\n' ';')
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
case "$T" in
  f13_rd)
    log "enter_scene start (level $LV, --rd, KYTY_RD_LEVEL_FRAME=$NRD, KYTY_RD_FLIPS=2, hold 240)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --emu-arg=--rd --hold 240 \
      KYTY_RD_LEVEL=$LV KYTY_RD_LEVEL_FRAME=$NRD KYTY_RD_FLIPS=2 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
  f13_k)
    log "enter_scene start (level $LV, --rec, KYTY_KEYS=$KEYS, hold 240)"
    python $G/enter_scene.py $T --level $LV --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
      --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 240 \
      KYTY_KEYS=$KEYS KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
    log "enter_scene rc $?";;
esac
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
if [ "$T" = "f13_rd" ]; then
  RDA=$(ls "$RDDIR"/*.rdc 2>/dev/null | sort | tr '\n' ';')
  NEW=""; NNEW=0
  IFS=';' read -ra AFTER <<< "$RDA"
  for X in "${AFTER[@]}"; do
    [ -n "$X" ] || continue
    case ";$RDB" in *";$X;"*) ;; *) NEW="$X"; NNEW=$((NNEW+1));; esac
  done
  log "new captures in _RenderDoc: $NNEW ($(basename "$NEW" 2>/dev/null))"
  if [ "$NNEW" != "1" ]; then log "no single new capture - no thumbnail, no listing"; exit 0; fi
  CAPF=$G/$T.rdc
  mv "$NEW" "$CAPF" || { log "move of the capture failed"; exit 0; }
  log "capture moved to $CAPF bytes $(stat -c %s "$CAPF") sha256 $(sha "$CAPF")"
  "$RDHOME/renderdoccmd.exe" thumb --out="C:/kyty/f287/f13a/$T.png" "C:/kyty/f287/f13a/$T.rdc" > $OUT/thumb.txt 2>&1
  log "thumbnail rc $? $T.png sha256 $(sha $G/$T.png)"
  rm -f C:/kyty/rd_list.txt
  log "rd_list.py start (qrenderdoc --python, watchdog $RDMAX s)"
  RD_CAP="C:/kyty/f287/f13a/$T.rdc" "$RDHOME/qrenderdoc.exe" --python $RDLIST > $OUT/qrd.txt 2>&1 &
  QP=$!
  WS=0
  while kill -0 $QP 2>/dev/null; do
    if grep -q '^done' C:/kyty/rd_list.txt 2>/dev/null; then sleep 20; break; fi
    if [ $WS -ge $RDMAX ]; then log "rd_list.py watchdog $RDMAX s expired"; break; fi
    sleep 10; WS=$((WS+10))
  done
  if kill -0 $QP 2>/dev/null; then taskkill //F //IM qrenderdoc.exe > /dev/null 2>&1; log "qrenderdoc.exe still alive after the listing - taskkill"; fi
  wait $QP 2>/dev/null
  cp C:/kyty/rd_list.txt $G/rd_list_$T.txt 2>/dev/null
  log "rd_list end after ~$WS s: rd_list_$T.txt lines $(wc -l < $G/rd_list_$T.txt 2>/dev/null) sha256 $(sha $G/rd_list_$T.txt)"
  python $G/rdsum_f7a.py $G/rd_list_$T.txt --out $G/rdsum_$T.txt > $OUT/rdsum.out.txt 2>&1
  log "rdsum rc $?: $(tail -1 $OUT/rdsum.out.txt | cut -c1-300); rdsum_$T.txt sha256 $(sha $G/rdsum_$T.txt)"
fi
exit 0
