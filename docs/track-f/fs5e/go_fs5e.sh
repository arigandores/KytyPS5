#!/bin/bash
# Track F link FS5e (HPP-513; ROADMAP s122 item 410 (g)(5), items 424 (zh), 426): the warm-up tag fs5_i - V Sky Garden of the form fs5_v
# on the INSTALLED FS5 631ff987 (installed by FS5d at 2026-10-04 08:34:30Z); the caches are NOT copied and NOT returned (item 410 (g)(5):
# the directory variant_fixb26_fixb1b_fixf10 of the user is warm on Sky Garden after the tag; form of item 300 (b)).  ONE TAG = ONE LOCK.
# Port of C:/kyty/f287/fs5/fs5c/go_fs5c.sh (FS5c HPP-511) without the install / return of the binary and of the caches, with the reading
# INSIDE the lock (s51_vidglitch.py, sheet142.py, the pair sheet fs5_i | fs5_v, fs5e_read.py) because the verdict decides the rollback:
#   WARMUP VERDICT fs5_i: PASS          -> the install stays, rc 0.
#   WARMUP VERDICT fs5_i: INTERFERENCE  -> the install stays, rc 7, question to the lead (variant of the executor, seal section 2).
#   WARMUP VERDICT fs5_i: FAIL          -> ROLLBACK inside the lock: the pinned C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe copied over
#                                          kyty_emulator.exe, sha256 checked (item 424 (e)); rc 6, question to the lead.
#   no verdict (reader error, an exit before the reading)  -> the install stays (nothing was changed), rc 1, question to the lead.
# Manifests of the caches before the tag and after the run - reference only (the caches grow by design).  Stop file, lock, live emulator,
# procload through the <app> mask, lock.log UTC, times.txt UTC rows at the moment of each event.  The seal's sha256 lines are checked
# before the lock.  ASCII only.
# usage: bash C:/kyty/f287/fs5/fs5e/go_fs5e.sh fs5_i
#   FORM (= fs5_v of the seal of FS5c, docs/track-f/fs5c.md section 3): enter_scene.py fs5_i --level underwater_aerial_garden --attempts 1
#     --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred <seal> --rec --hold 330
#     KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0; the defaults of FS5 (KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS never passed; this
#     script unsets KYTY_* and VK_LAYER_* before the call).
# EXIT: 0 PASS; 1 hard refusal / no verdict; 2 usage / the tag exists; 3 lock / live emulator; 4 stop file; 5 procload busy;
#   6 FAIL - rolled back; 7 INTERFERENCE; 8 FAIL and the ROLLBACK FAILED (the lock stays, file RETURN_FAILED).
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/fs5/fs5e; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN=C:/kyty/f287/bin/kyty_emulator_631ff987.exe
BIN_EXPECT=631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17
PINNED=C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe
OLD=31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5
SEAL=$G/pred/fs5e_seal.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
FIXDIR="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10"
VREF=C:/kyty/f287/fs5/fs5c/runs/fs5_v/sheet_fs5_v.png
SKY=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
[ "$T" = "fs5_i" ] || { echo "usage: go_fs5e.sh fs5_i"; exit 2; }
OUT=$G/runs/$T; TIMES=$F/times.txt
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) FS5e go_fs5e $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")
[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }
[ -e $G/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - the tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
NS=0
while IFS= read -r L || [ -n "$L" ]; do
  L=${L%$'\r'}
  case "$L" in
    "seal: "*) S=${L#seal: }; WANTS=${S%% *}; P=${S#* }; NS=$((NS+1))
      case "$P" in /*|C:/*) ;; *) P=$G/$P;; esac
      [ "$(sha "$P")" = "$WANTS" ] || { log "seal line differs: $P (want $WANTS, is $(sha "$P")) - not starting"; exit 1; };;
  esac
done < "$SEAL"
[ $NS -ge 10 ] || { log "seal has $NS sha256 lines (< 10) - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "installed binary is not FS5 631ff987 before the tag ($(sha "$GAME")) - not starting"; exit 1; }
[ "$(sha $PINNED)" = "$OLD" ] || { log "rollback copy $PINNED sha != $OLD - not starting"; exit 1; }
[ "$(sha $BIN)" = "$BIN_EXPECT" ] || { log "FS5 copy $BIN sha != $BIN_EXPECT - not starting"; exit 1; }
[ -f $VREF ] || { log "no reference sheet $VREF - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "FS5e HPP-513 go_fs5e.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/lock.log
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120); seal lines checked $NS"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
VERDICT=""; ROLLED=0
finish() {
  RCX=$?
  KEEPLOCK=0
  if tasklist //FI "IMAGENAME eq kyty_emulator.exe" 2>/dev/null | grep -qi kyty_emulator; then
    taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; log "kyty_emulator.exe killed at the exit (taskkill)"; sleep 5
  fi
  case "$VERDICT" in
    PASS) RCX=0; log "WARM-UP PASS - the install stays: kyty_emulator.exe sha256 $(sha "$GAME")";;
    INTERFERENCE) RCX=7; log "WARM-UP INTERFERENCE - not read as an outcome; the install stays ($(sha "$GAME")); question to the lead";;
    FAIL)
      for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$OLD" ] && break; sleep 5; done
      if [ "$(sha "$GAME")" = "$OLD" ]; then
        RCX=6; log "WARM-UP FAIL - ROLLBACK done: kyty_emulator.exe sha256 $(sha "$GAME") = 31cbfee8 (copy $PINNED); question to the lead"
      else
        RCX=8; KEEPLOCK=1; echo "$(u) $T rollback failed" > $G/RETURN_FAILED
        log "WARM-UP FAIL - ROLLBACK FAILED: kyty_emulator.exe sha256 $(sha "$GAME") - the lock stays, restore by hand"
      fi;;
    *) [ "$RCX" = "0" ] && RCX=1; log "no warm-up verdict (rc $RCX) - the install stays ($(sha "$GAME")), nothing changed; question to the lead";;
  esac
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary at the end: $(cat $OUT/installed_after.txt)"
  if [ $KEEPLOCK = 0 ]; then
    rm -f $LOCK; echo "lock released $T $(u)" >> $G/lock.log; log "lock released (rc $RCX)"
  fi
  exit $RCX
}
trap finish EXIT
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1
log "manifest before (reference): $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
ls "$EMU/_ShaderCache/PPSA21564" > $OUT/variant_dirs_before.txt 2>&1
if [ -e "$FIXDIR" ]; then
  echo "warm form before: $FIXDIR present at $(u) ($(ls "$FIXDIR" | wc -l) entries); entries of _ShaderCache/PPSA21564: $(ls "$EMU/_ShaderCache/PPSA21564" | wc -l)" > $OUT/cold.txt
else
  echo "cold form: $FIXDIR absent at $(u); entries of _ShaderCache/PPSA21564: $(ls "$EMU/_ShaderCache/PPSA21564" | wc -l)" > $OUT/cold.txt
fi
log "$(cat $OUT/cold.txt)"
sha "$GAME" > $OUT/installed_sha.txt
[ "$(cat $OUT/installed_sha.txt)" = "$BIN_EXPECT" ] || { log "installed binary changed inside the lock - not starting"; exit 1; }
log "binary of the tag (installed, not copied): $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
echo "FS5e go_fs5e.sh $T attempt started $(u) installed $BIN_EXPECT" > $OUT/attempt.txt
log "enter_scene start (level $SKY, SD 300, --rec, hold 330, defaults of FS5, installed binary)"
python $G/enter_scene.py $T --level $SKY --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
log "enter_scene rc $?"
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
PB="$FIXDIR/pipelines.bin"
if [ -f "$PB" ]; then
  echo "warm form after the tag: $FIXDIR files $(ls "$FIXDIR" | wc -l); pipelines.bin present size $(stat -c %s "$PB") sha256 $(sha "$PB")" > $OUT/warm.txt
else
  echo "warm form after the tag: $FIXDIR files $(ls "$FIXDIR" 2>/dev/null | wc -l); pipelines.bin ABSENT" > $OUT/warm.txt
fi
log "$(cat $OUT/warm.txt)"
ls "$EMU/_ShaderCache/PPSA21564" > $OUT/variant_dirs_after.txt 2>&1
python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1
python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
log "manifest after (reference, caches not returned): $(head -1 $OUT/manifest_after.txt | cut -c1-200); vs before: $(head -1 $OUT/manifest_cmp.txt | cut -c1-120)"
cd $G || exit 1
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $OUT/vidframes > $OUT/glitch.txt 2>&1
  log "s51_vidglitch rc $?: $(grep -h 'one-frame glitches' $OUT/glitch.txt | head -1); rec sha256 $(sha $REC)"
  python sheet142.py $REC $OUT/sheet_$T.png > $OUT/sheet.txt 2>&1
  log "sheet142 rc $?: $(grep -h '^sheet: ' $OUT/sheet.txt | head -1 | cut -c1-160)"
  if [ -f $OUT/sheet_$T.png ]; then
    ffmpeg -hide_banner -loglevel error -y -i $OUT/sheet_$T.png -i $VREF -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" \
      $OUT/pair_fs5_i_fs5_v.png > $OUT/pair.txt 2>&1 && echo "pair: $OUT/pair_fs5_i_fs5_v.png (left fs5_i, right fs5_v)" >> $OUT/pair.txt
    log "pair sheet: $(tail -1 $OUT/pair.txt | cut -c1-160)"
  fi
else
  log "no video $REC"
fi
python $G/fs5e_read.py $T --json $OUT/read.json > $OUT/read.txt 2>&1
RRC=$?
V=$(grep '^WARMUP VERDICT fs5_i: ' $OUT/read.txt | tr -d '\r')
log "reader rc $RRC read.txt sha256 $(sha $OUT/read.txt): $V; MEMBER NO/NOT_READ: $(grep -c 'MEMBER .*: \(NO\|NOT_READ\)$' $OUT/read.txt)"
if [ "$RRC" = "0" ]; then
  case "$V" in
    "WARMUP VERDICT fs5_i: PASS") VERDICT=PASS;;
    "WARMUP VERDICT fs5_i: INTERFERENCE") VERDICT=INTERFERENCE;;
    "WARMUP VERDICT fs5_i: FAIL") VERDICT=FAIL;;
  esac
fi
exit 0
