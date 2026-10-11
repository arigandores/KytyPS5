#!/bin/bash
# Track F link F42a (HPP-779): run rd_f42a.py on f12_rd_k03 offline (no game) - copy of the F12g rdg_f12g.sh with the
# replay script, output and arguments changed. usage: bash rdg_f42a.sh <name> <eid> <N> <seed> <mods|-> [dump path] [watchdog_s]
# Guards: exits 3 on C:/kyty/SEALED_RUN.lock, 4 on C:/kyty/f287/STOP before the start; during the replay a lock or STOP
# that appears kills qrenderdoc. The driver GLCache is copied before; its manifest (path, size, sha256) is compared after
# and on any difference the copy is returned and compared again (the replay runs with __GL_SHADER_DISK_CACHE_PATH on
# its own folder). EXIT: 0 'done'; 1 no 'done'; 2 usage; 3 lock; 4 STOP; 5 GLCache not returned. ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
NAME=${1:-}; EID=${2:-}; N=${3:-}; SEED=${4:-}; MODS=${5:--}; DUMP=${6:-}; WMAX=${7:-520}
[ -n "$NAME" ] && [ -n "$EID" ] && [ -n "$N" ] && [ -n "$SEED" ] || { echo "usage"; exit 2; }
[ "$MODS" = "-" ] && MODS=""
G=C:/kyty/f287/f42a/replay
CAP=C:/kyty/f287/f12f/f12_rd_k03.rdc
OUTF=$G/rd_$NAME.txt
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
RDHOME="/c/Program Files/RenderDoc"
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $G/rdg.log; }
mf() { python C:/kyty/f287/f12g/mf_f12g.py "$GLDIR" "$1" > /dev/null; }
mkdir -p $G/nvcache
log "start $NAME eid $EID N $N seed $SEED dump '$DUMP' watchdog $WMAX"
rm -rf $G/glcache_before; cp -a "$GLDIR" $G/glcache_before || { log "GLCache copy failed - not starting"; exit 1; }
mf $G/glcache_mf_before_$NAME.txt
log "GLCache copied, manifest $(sha256sum < $G/glcache_mf_before_$NAME.txt | cut -c1-16) files $(wc -l < $G/glcache_mf_before_$NAME.txt)"
rm -f "$OUTF"
cd $G
__GL_SHADER_DISK_CACHE_PATH='C:\kyty\f287\f42a\replay\nvcache' RD_CAP="$CAP" RD_OUT="$OUTF" RD_EID="$EID" RD_N="$N" RD_SEED="$SEED" \
  RD_MODS="$MODS" RD_DUMP="$DUMP" "$RDHOME/qrenderdoc.exe" --python $G/rd_f42a.py > "$OUTF.qrd.txt" 2>&1 &
QP=$!
WS=0; WHY=""
while kill -0 $QP 2>/dev/null; do
  if grep -q '\] done$' "$OUTF" 2>/dev/null; then sleep 10; break; fi
  if [ -e C:/kyty/SEALED_RUN.lock ]; then WHY="lock appeared"; break; fi
  if [ -e C:/kyty/f287/STOP ]; then WHY="STOP appeared"; break; fi
  if [ $WS -ge $WMAX ]; then WHY="watchdog $WMAX s expired"; break; fi
  sleep 5; WS=$((WS+5))
done
if kill -0 $QP 2>/dev/null; then taskkill //F //IM qrenderdoc.exe > /dev/null 2>&1; log "qrenderdoc still alive ($WHY) - taskkill"; fi
wait $QP 2>/dev/null
log "replay end after ~$WS s ($WHY): $(grep -c ' arm ' "$OUTF" 2>/dev/null) replays"
mf $G/glcache_mf_after_$NAME.txt
if cmp -s $G/glcache_mf_before_$NAME.txt $G/glcache_mf_after_$NAME.txt; then
  log "GLCache after = before (cmp EQUAL)"
else
  log "GLCache changed: $(diff $G/glcache_mf_before_$NAME.txt $G/glcache_mf_after_$NAME.txt | grep -c '^[<>]') lines - returning the copy"
  diff $G/glcache_mf_before_$NAME.txt $G/glcache_mf_after_$NAME.txt > $G/glcache_diff_$NAME.txt
  rm -rf "$GLDIR"/* && cp -a $G/glcache_before/. "$GLDIR"/ && mf $G/glcache_mf_ret_$NAME.txt
  if cmp -s $G/glcache_mf_before_$NAME.txt $G/glcache_mf_ret_$NAME.txt; then log "GLCache returned (cmp EQUAL)"; else log "GLCache NOT returned"; exit 5; fi
fi
grep -q '\] done$' "$OUTF" 2>/dev/null || exit 1
exit 0
