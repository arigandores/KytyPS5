#!/bin/bash
# F9a (HPP-410, ROADMAP s122 item 344 (v)(2)-(4)): one attempt = one lock. usage: go_f9.sh <tag> <seconds> [--rd] [KEY=VALUE ...]
# Stop file, lock, live emulator and procload first; then the lock (lock.log UTC), the installed binary must be 4aa62e95;
# _ShaderCache, _PipelineCache, _SaveData copied before and returned after (form of play_patched.sh); run_f9.py; return;
# the lock stays (RETURN_FAILED) when a return fails. ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
F9=C:/kyty/f287/f9; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=C:/kyty/SEALED_RUN.lock
T=$1; SECS=$2; shift 2
OUT=$F9/runs/$T; TIMES=$F9/times.txt; DIRS="_ShaderCache _PipelineCache _SaveData"
WANT=4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(u) go_f9 $T $*" | tee -a $TIMES; }
[ -e $F9/STOP ] && { log "STOP file: $(head -1 $F9/STOP)"; exit 4; }
[ -e $F9/RETURN_FAILED ] && { echo "RETURN_FAILED exists"; exit 1; }
[ -e $LOCK ] && { echo "lock held: $(head -1 $LOCK)"; exit 3; }
[ -e $OUT ] && { echo "$OUT exists - a tag runs once"; exit 2; }
tasklist //FI "IMAGENAME eq kyty_emulator.exe" | grep -qi kyty_emulator && { log "an emulator lives - not starting"; exit 3; }
mkdir -p $OUT
python C:/kyty/s288/procload.py --wait-s 120 > $OUT/procload.txt 2>&1 || { log "procload busy: $(tail -1 $OUT/procload.txt | cut -c1-200)"; exit 5; }
[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; exit 3; }
echo "F9d HPP-421 go_f9.sh $T pid $$ $(u)" > $LOCK
echo "lock taken $T $(u)" >> $F9/lock.log
log "lock taken; procload: $(tail -1 $OUT/procload.txt | cut -c1-120)"
SHA=$(sha256sum "$EMU/kyty_emulator.exe" | cut -c1-64)
if [ "$SHA" != "$WANT" ]; then log "installed binary $SHA is not 4aa62e95 - not starting"; rm -f $LOCK; echo "lock released $T $(u)" >> $F9/lock.log; exit 1; fi
log "installed binary $SHA; args: $*"
for d in $DIRS; do cp -a "$EMU/$d" "$OUT/before$d" || { log "copy of $d failed - not starting"; rm -rf $OUT/before_*; rm -f $LOCK; echo "lock released $T $(u)" >> $F9/lock.log; exit 1; }; done
log "caches and saves copied: $DIRS ($(du -sm $OUT/before_ShaderCache $OUT/before_PipelineCache $OUT/before_SaveData | awk '{print $1}' | tr '\n' '/') MB)"
RDB=$(ls "$EMU/_RenderDoc"/*.rdc 2>/dev/null | sort | tr '\n' ';')
python $F9/run_f9.py $OUT $SECS "$@" > $OUT/run.txt 2>&1
for X in "$EMU/_RenderDoc"/*.rdc; do [ -e "$X" ] || continue; case ";$RDB" in *";$X;"*) ;; *) mv "$X" $OUT/ && log "capture moved: $(basename "$X") bytes $(stat -c %s $OUT/$(basename "$X"))";; esac; done
log "run: $(tail -1 $OUT/run.txt)"
OK=1
for d in $DIRS; do rm -rf "$EMU/$d" && mv "$OUT/before$d" "$EMU/$d" || { OK=0; log "return of $d FAILED"; }; done
if [ $OK = 1 ] && [ -d "$EMU/_ShaderCache" ] && [ -d "$EMU/_PipelineCache" ] && [ -d "$EMU/_SaveData" ] && [ ! -e "$OUT/before_ShaderCache" ]; then
  log "caches and saves returned"
  SHA2=$(sha256sum "$EMU/kyty_emulator.exe" | cut -c1-64); log "installed binary after: $SHA2"
  rm -f $LOCK; echo "lock released $T $(u)" >> $F9/lock.log; log "lock released"
else
  echo "$(u) $T" > $F9/RETURN_FAILED; log "return incomplete - the lock stays"
fi
