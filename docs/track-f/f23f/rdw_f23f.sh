#!/bin/bash
# F23f (HPP-592, ROADMAP s122 item 498(g)): run one qrenderdoc --python script under the watchdog watch_f23f.py (item 431(v)(1):
# poll 1.5 s, kills the tree on the lock, STOP or a procload.py process), form of F12g rdg_f12g.sh: the driver GLCache is copied
# before, its manifest (path, size, sha256) is compared after; on any difference the copy is returned and compared again; the replay's
# own driver shader cache goes to C:/kyty/f287/f23f/nvcache (__GL_SHADER_DISK_CACHE_PATH).
# usage: bash rdw_f23f.sh <tag> <script.py> <limit_s>   (RD_* variables are taken from the caller's environment)
# EXIT: the watchdog's code (0 ok; 3 lock; 4 STOP; 6 limit; 7 procload); 5 GLCache not returned; 2 usage.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
TAG=${1:-}; SCR=${2:-}; LIM=${3:-540}
[ -n "$TAG" ] && [ -n "$SCR" ] || { echo "usage: rdw_f23f.sh <tag> <script.py> <limit_s>"; exit 2; }
G=C:/kyty/f287/f23f
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
RDHOME="/c/Program Files/RenderDoc"
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $G/rdw.log; }
mf() { python C:/kyty/f287/f12g/mf_f12g.py "$GLDIR" "$1" > /dev/null; }
mkdir -p $G/nvcache $G/runs
bash $G/api_chk.sh "rdw $TAG" > /dev/null || exit $?
log "start $TAG script $SCR limit $LIM"
rm -rf $G/glcache_before; cp -a "$GLDIR" $G/glcache_before || { log "GLCache copy failed - not starting"; exit 1; }
mf $G/runs/glcache_mf_before_$TAG.txt
cd $G
# survivors after a kill are looked up by the replay's own command line only (the default mark 'f23f' also matched
# this script's own shells and the calling shell - killed with them at 21:45:03Z, sv3_k05)
WD_MARK='qrenderdoc.exe' __GL_SHADER_DISK_CACHE_PATH='C:\kyty\f287\f23f\nvcache' python $G/watch_f23f.py --limit $LIM --tag "$TAG" -- \
  "$RDHOME/qrenderdoc.exe" --python "$SCR" > $G/runs/watch_$TAG.txt 2>&1
RC=$?
log "$TAG watchdog rc=$RC: $(tail -2 $G/runs/watch_$TAG.txt | tr '\n' ' ')"
taskkill //F //IM qrenderdoc.exe > /dev/null 2>&1
if [ -e C:/kyty/SEALED_RUN.lock ]; then log "lock present after the run - GLCache check deferred"; exit $RC; fi
mf $G/runs/glcache_mf_after_$TAG.txt
if cmp -s $G/runs/glcache_mf_before_$TAG.txt $G/runs/glcache_mf_after_$TAG.txt; then
  log "$TAG GLCache after = before (cmp EQUAL)"
else
  log "$TAG GLCache changed: $(diff $G/runs/glcache_mf_before_$TAG.txt $G/runs/glcache_mf_after_$TAG.txt | grep -c '^[<>]') lines - returning the copy"
  rm -rf "$GLDIR"/* && cp -a $G/glcache_before/. "$GLDIR"/ && mf $G/runs/glcache_mf_ret_$TAG.txt
  if cmp -s $G/runs/glcache_mf_before_$TAG.txt $G/runs/glcache_mf_ret_$TAG.txt; then log "$TAG GLCache returned (cmp EQUAL)"; else log "$TAG GLCache NOT returned"; exit 5; fi
fi
exit $RC
