#!/bin/bash
# Track F link F12g (HPP-481): run rd_f12g.py on one capture of f12_rd with a watchdog, offline (no game).
# usage: bash rdg_f12g.sh <kNN> <chunk,chunk,...> [maxd] [watchdog_s]
# Guards: exits 3 on C:/kyty/SEALED_RUN.lock, 4 on C:/kyty/f287/STOP before the start; during the replay a lock or STOP that appears
# kills qrenderdoc (the link does not run processes under another's lock, general rule 27).  The driver GLCache is copied before;
# its manifest (path, size, sha256) is compared after and on any difference the copy is returned and compared again.
# EXIT: 0 'done' in the report; 1 no 'done'; 2 usage; 3 lock; 4 STOP; 5 GLCache not returned.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
K=${1:-}; CH=${2:-}; MAXD=${3:-0}; WMAX=${4:-1500}
[ -n "$K" ] && [ -n "$CH" ] || { echo "usage: rdg_f12g.sh <kNN> <chunks> [maxd] [watchdog_s]"; exit 2; }
G=C:/kyty/f287/f12g
CAP=C:/kyty/f287/f12f/f12_rd_$K.rdc
OUTF=$G/rd_f12g_$K.txt
SPVD=C:/kyty/f287/f12d/final/corpus/spv380
SPV0=$SPVD/cs_380bb9d636390bae_fe70c334a8301128_0_base.spv
SPV1=$SPVD/cs_380bb9d636390bae_fe70c334a8301128_0_f1.spv
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
RDHOME="/c/Program Files/RenderDoc"
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $G/rdg.log; }
mf() { python $G/mf_f12g.py "$GLDIR" "$1" > /dev/null; }
mkdir -p $G/dump_$K $G/nvcache
log "start $K chunks $CH maxd $MAXD watchdog $WMAX"
rm -rf $G/glcache_before; cp -a "$GLDIR" $G/glcache_before || { log "GLCache copy failed - not starting"; exit 1; }
mf $G/glcache_mf_before_$K.txt
log "GLCache copied, manifest $(sha256sum < $G/glcache_mf_before_$K.txt | cut -c1-16) files $(wc -l < $G/glcache_mf_before_$K.txt)"
rm -f "$OUTF"
cd $G
__GL_SHADER_DISK_CACHE_PATH='C:\kyty\f287\f12g\nvcache' RD_CAP="$CAP" RD_OUT="$OUTF" RD_DIR="$G/dump_$K" RD_CHUNKS="$CH" RD_MAXD="$MAXD" \
  RD_SPV0="$SPV0" RD_SPV1="$SPV1" "$RDHOME/qrenderdoc.exe" --python $G/rd_f12g.py > "$OUTF.qrd.txt" 2>&1 &
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
log "replay end after ~$WS s ($WHY): $(grep -c CONTROL_A "$OUTF" 2>/dev/null) dispatches"
mf $G/glcache_mf_after_$K.txt
if cmp -s $G/glcache_mf_before_$K.txt $G/glcache_mf_after_$K.txt; then
  log "GLCache after = before (cmp EQUAL)"
else
  log "GLCache changed: $(diff $G/glcache_mf_before_$K.txt $G/glcache_mf_after_$K.txt | grep -c '^[<>]') lines - returning the copy"
  diff $G/glcache_mf_before_$K.txt $G/glcache_mf_after_$K.txt > $G/glcache_diff_$K.txt
  rm -rf "$GLDIR"/* && cp -a $G/glcache_before/. "$GLDIR"/ && mf $G/glcache_mf_ret_$K.txt
  if cmp -s $G/glcache_mf_before_$K.txt $G/glcache_mf_ret_$K.txt; then log "GLCache returned (cmp EQUAL)"; else log "GLCache NOT returned"; exit 5; fi
fi
grep -q '\] done$' "$OUTF" 2>/dev/null || exit 1
exit 0
