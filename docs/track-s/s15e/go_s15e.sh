#!/bin/bash
# Track S link S15e (HPP-636; ROADMAP s122 item 557 (d), item 560): the tag s15_i - the FIRST launch of the installed state "known scenes"
# (catalogue s15/seeds in _ShaderSeeds/PPSA21564 and the variant pipelines.bin of FS8 moved to backup by S15d at 2026-10-06 03:25:03Z).
# Port of C:/kyty/f287/fs8e/go_fs8e.sh (FS8e HPP-575, tag fs8_i) without a change of the form, except what item 557 (d) names:
#   - the caches (_ShaderCache, _PipelineCache, _SaveData, GLCache) are NOT copied, NOT returned and NOT removed; the manifests before the
#     tag and after the run and their cmp are rows (reference);
#   - no rollback inside the lock: the acceptance or the rollback is the lead's (S15f, HPP-637; item 557 (d)); the script never writes
#     into kyty_emulator.exe, _ShaderSeeds or _ShaderCache;
#   - the pre-state of S15d is checked inside the lock before the tag (s15e_read.py --pre: _ShaderSeeds/PPSA21564 = seeds_manifest.txt,
#     its compatibility first line = the catalogue's, the variant pipelines.bin absent) - otherwise no start (the first launch is spent once);
#   - the state of member (2) is written inside the lock right after the run (s15e_read.py --after), before anything else starts;
#   - the environment: KYTY_* and VK_LAYER_* unset (so no KYTY_SHADER_SEED, KYTY_SHADER_SEED_PATH, KYTY_CACHE_MODE); positional only
#     KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (form fs8_i);
#   - the pair sheet: left s15_i, right the sheet of fs8_i (FS8e).
# Stop file C:/kyty/s288/STOP, lock, live emulator, procload through the <app> mask, lock.log UTC, times.txt UTC rows at the moment of
# each event.  The seal's sha256 lines are checked before the lock.  ASCII only.
# usage: bash C:/kyty/s288/s15e/go_s15e.sh s15_i
# EXIT: 0 reader word printed; 1 hard refusal / no reader word; 2 usage / the tag exists; 3 lock / live emulator; 4 stop file;
#   5 procload busy; 9 the pre-state is not the S15d state (inside the lock, before the emulator; nothing started).
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/s288/s15e; S=C:/kyty/s288; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
GAME="$EMU/kyty_emulator.exe"
BIN_EXPECT=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b
SEAL=$S/pred/17_s.md
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
FIXDIR="$EMU/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19"
VREF=C:/kyty/f287/fs8e/runs/fs8_i/sheet_fs8_i.png
SKY=underwater_aerial_garden
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
T=${1:-}
[ "$T" = "s15_i" ] || { echo "usage: go_s15e.sh s15_i"; exit 2; }
OUT=$G/runs/$T; TIMES=$G/times.txt
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) S15e go_s15e $T $*" | tee -a $TIMES; }
mask() { sed -E "s/\('[^']*'/('<app>'/g"; }
sha() { sha256sum "$1" 2>/dev/null | cut -c1-64; }
MF=("_ShaderCache=$EMU/_ShaderCache" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "_ShaderSeeds=$EMU/_ShaderSeeds" "GLCache=$GLDIR")
[ -e $S/STOP ] && { log "STOP file: $(head -1 $S/STOP)"; exit 4; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - the tag runs once"; exit 2; }
[ -f "$SEAL" ] || { echo "no seal $SEAL"; exit 1; }
NS=0
while IFS= read -r L || [ -n "$L" ]; do
  L=${L%$'\r'}
  case "$L" in
    "seal: "*) SL=${L#seal: }; WANTS=${SL%% *}; P=${SL#* }; NS=$((NS+1))
      case "$P" in /*|C:/*) ;; *) P=$G/$P;; esac
      [ "$(sha "$P")" = "$WANTS" ] || { log "seal line differs: $P (want $WANTS, is $(sha "$P")) - not starting"; exit 1; };;
  esac
done < "$SEAL"
[ $NS -ge 10 ] || { log "seal has $NS sha256 lines (< 10) - not starting"; exit 1; }
[ "$(sha "$GAME")" = "$BIN_EXPECT" ] || { log "installed binary is not FS8 2c9b69b9 before the tag ($(sha "$GAME")) - not starting"; exit 1; }
[ -f $VREF ] || { log "no reference sheet $VREF - not starting"; exit 1; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python $G/procload.py --wait-s ${PLWAIT:-120} 2>&1 | mask > $OUT/procload.txt
[ "${PIPESTATUS[0]}" = "0" ] || { log "procload busy: $(grep 'procload: busy' $OUT/procload.txt | tail -1 | cut -c1-200)"; mv $OUT $OUT.busy_$(date -u +%H%M%S); exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }
set -o noclobber
if ! { echo "S15e HPP-636 go_s15e.sh $T pid $$ $(u)" > $LOCK; } 2>/dev/null; then
  set +o noclobber; echo "lock taken by someone else"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3
fi
set +o noclobber
echo "lock taken $T $(u)" >> $G/lock.log
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120); seal lines checked $NS"
sha "$GAME" > $OUT/installed_before.txt
log "installed binary inside the lock before the tag: $(cat $OUT/installed_before.txt)"
WORD=""
finish() {
  RCX=$?
  if tasklist //FI "IMAGENAME eq kyty_emulator.exe" 2>/dev/null | grep -qi kyty_emulator; then
    taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; log "kyty_emulator.exe killed at the exit (taskkill)"; sleep 5
  fi
  sha "$GAME" > $OUT/installed_after.txt
  log "installed binary at the end: $(cat $OUT/installed_after.txt)"
  if [ -n "$WORD" ]; then
    RCX=0; log "READING $T: $WORD - no rollback by this script (S15f, lead); caches not returned"
  else
    [ "$RCX" = "0" ] && RCX=1; log "no reader word (rc $RCX) - nothing returned, nothing rolled back; question to the lead"
  fi
  rm -f $LOCK; echo "lock released $T $(u)" >> $G/lock.log; log "lock released (rc $RCX)"
  exit $RCX
}
trap finish EXIT
python $G/s15e_read.py --pre $OUT/pre.txt > $OUT/pre_run.txt 2>&1
PRC=$?
log "pre-state rc $PRC: $(tail -1 $OUT/pre.txt 2>/dev/null); $(grep -h 'seeds dir\|absent:' $OUT/pre.txt 2>/dev/null | tr '\n' ';' | cut -c1-300)"
[ "$PRC" = "0" ] || { log "pre-state is not the S15d state - not starting (the first launch is not spent)"; exit 9; }
python $G/manifest_fs4c.py $OUT/manifest_before.tsv "${MF[@]}" > $OUT/manifest_before.txt 2>&1
log "manifest before: $(head -1 $OUT/manifest_before.txt | cut -c1-200)"
ls "$EMU/_ShaderCache/PPSA21564" > $OUT/variant_dirs_before.txt 2>&1
echo "variant before: $FIXDIR files $(ls "$FIXDIR" 2>/dev/null | wc -l); pipelines.bin $( [ -e "$FIXDIR/pipelines.bin" ] && echo present || echo absent)" > $OUT/variant_before.txt
log "$(cat $OUT/variant_before.txt)"
sha "$GAME" > $OUT/installed_sha.txt
[ "$(cat $OUT/installed_sha.txt)" = "$BIN_EXPECT" ] || { log "installed binary changed inside the lock - not starting"; exit 1; }
log "binary of the tag (installed, not copied): $(cat $OUT/installed_sha.txt)"
cd "$EMU" || exit 1
for v in $(env | grep -o '^\(KYTY\|VK_LAYER\)_[A-Z0-9_]*'); do unset $v; done
echo "S15e go_s15e.sh $T attempt started $(u) installed $BIN_EXPECT" > $OUT/attempt.txt
log "enter_scene start (level $SKY, SD 300, --rec, hold 330, defaults of FS8, installed binary, no KYTY_SHADER_SEED / _PATH / KYTY_CACHE_MODE)"
python $G/enter_scene.py $T --level $SKY --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle \
  --gates-file $G/gates_default.txt --pred $SEAL --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $OUT/run.txt 2>&1
log "enter_scene rc $?"
log "run: $(tail -1 $OUT/run.txt | cut -c1-200)"
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator still lives after the run - taskkill"; taskkill //F //IM kyty_emulator.exe > /dev/null 2>&1; sleep 5; }
[ -f $G/log_$T.txt ] && log "log_$T.txt sha256 $(sha $G/log_$T.txt)"
python $G/s15e_read.py --after $OUT/after.json > $OUT/after.txt 2>&1
log "after state rc $?: $(tail -1 $OUT/after.txt | cut -c1-200); after.json sha256 $(sha $OUT/after.json)"
ls "$EMU/_ShaderCache/PPSA21564" > $OUT/variant_dirs_after.txt 2>&1
python $G/manifest_fs4c.py $OUT/manifest_after.tsv "${MF[@]}" > $OUT/manifest_after.txt 2>&1
python $G/manifest_fs4c.py --cmp $OUT/manifest_before.tsv $OUT/manifest_after.tsv > $OUT/manifest_cmp.txt 2>&1
log "manifest after (caches not returned): $(head -1 $OUT/manifest_after.txt | cut -c1-200); vs before: $(head -1 $OUT/manifest_cmp.txt | cut -c1-120)"
cd $G || exit 1
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $OUT/vidframes > $OUT/glitch.txt 2>&1
  log "s51_vidglitch rc $?: $(grep -h 'one-frame glitches' $OUT/glitch.txt | head -1); rec sha256 $(sha $REC)"
  python sheet142.py $REC $OUT/sheet_$T.png > $OUT/sheet.txt 2>&1
  log "sheet142 rc $?: $(grep -h '^sheet: ' $OUT/sheet.txt | head -1 | cut -c1-160)"
  if [ -f $OUT/sheet_$T.png ]; then
    ffmpeg -hide_banner -loglevel error -y -i $OUT/sheet_$T.png -i $VREF -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" \
      $OUT/pair_s15_i_fs8_i.png > $OUT/pair.txt 2>&1 && echo "pair: $OUT/pair_s15_i_fs8_i.png (left s15_i, right fs8_i)" >> $OUT/pair.txt
    log "pair sheet: $(tail -1 $OUT/pair.txt | cut -c1-160)"
  fi
else
  log "no video $REC"
fi
sha "$GAME" > $OUT/installed_after.txt
python $G/s15e_read.py $T --json $OUT/read.json > $OUT/read.txt 2>&1
RRC=$?
W=$(grep '^READING s15_i: ' $OUT/read.txt | tr -d '\r')
log "reader variant line: $(grep '^READING VARIANT s15_i: ' $OUT/read.txt | tr -d '\r' | cut -c1-160)"
log "reader rc $RRC read.txt sha256 $(sha $OUT/read.txt): $W; MEMBER NO/NOT_DETERMINED: $(grep -c '  MEMBER .*: \(NO\|NOT_DETERMINED\)$' $OUT/read.txt)"
[ "$RRC" = "0" ] && [ -n "$W" ] && WORD=${W#READING s15_i: }
exit 0
