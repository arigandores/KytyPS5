#!/bin/bash
# F47e (HPP-810; copy of f36a/rdw_f36a.sh, paths f36a -> f47e; ROADMAP s122 item 708(d), item 431(v)(1)): run one qrenderdoc --python
# script under the watchdog watch_f47e.py (poll 1.5 s, kills the tree on the lock, STOP or a procload.py process), form of F12g / F36a:
# the driver GLCache is copied before, its manifest (path, size, sha256) is compared after; on any difference the copy is returned and
# compared again; the replay's own driver shader cache goes to C:/kyty/f287/f47e/nvcache (__GL_SHADER_DISK_CACHE_PATH); the listing sha
# of GLCache (form F7b, glsha.py) is written to times.txt before and after.
# usage: bash rdw_f47e.sh <tag> <script.py> <limit_s>   (RD_* variables are taken from the caller's environment)
# EXIT: the watchdog's code (0 ok; 3 lock; 4 STOP; 6 limit; 7 procload); 5 GLCache not returned; 2 usage.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
TAG=${1:-}; SCR=${2:-}; LIM=${3:-540}
[ -n "$TAG" ] && [ -n "$SCR" ] || { echo "usage: rdw_f47e.sh <tag> <script.py> <limit_s>"; exit 2; }
G=C:/kyty/f287/f47e
GLDIR="$USERPROFILE/AppData/Local/NVIDIA/GLCache"
RDHOME="/c/Program Files/RenderDoc"
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $G/rdw.log; }
tl() { echo "$(date -u +%FT%TZ) F47e $*" >> C:/kyty/f287/times.txt; }
mf() { python C:/kyty/f287/f12g/mf_f12g.py "$GLDIR" "$1" > /dev/null; }
mkdir -p $G/nvcache $G/runs
bash $G/api_chk.sh "rdw $TAG" > /dev/null || exit $?
log "start $TAG script $SCR limit $LIM"
tl "GLCache before replay $TAG: $(python $G/glsha.py)"
rm -rf $G/glcache_before; cp -a "$GLDIR" $G/glcache_before || { log "GLCache copy failed - not starting"; exit 1; }
mf $G/runs/glcache_mf_before_$TAG.txt
cd $G
WD_MARK='qrenderdoc.exe' __GL_SHADER_DISK_CACHE_PATH='C:\kyty\f287\f47e\nvcache' python $G/watch_f47e.py --limit $LIM --tag "$TAG" -- \
  "$RDHOME/qrenderdoc.exe" --python "$SCR" > $G/runs/watch_$TAG.txt 2>&1
RC=$?
log "$TAG watchdog rc=$RC: $(tail -2 $G/runs/watch_$TAG.txt | tr '\n' ' ')"
taskkill //F //IM qrenderdoc.exe > /dev/null 2>&1
if [ -e C:/kyty/SEALED_RUN.lock ]; then log "lock present after the run - GLCache check deferred"; exit $RC; fi
mf $G/runs/glcache_mf_after_$TAG.txt
if cmp -s $G/runs/glcache_mf_before_$TAG.txt $G/runs/glcache_mf_after_$TAG.txt; then
  log "$TAG GLCache after = before (cmp EQUAL)"
  tl "GLCache after replay $TAG (cmp EQUAL with before): $(python $G/glsha.py)"
else
  log "$TAG GLCache changed: $(diff $G/runs/glcache_mf_before_$TAG.txt $G/runs/glcache_mf_after_$TAG.txt | grep -c '^[<>]') lines - returning the copy"
  tl "GLCache after replay $TAG (changed, before return): $(python $G/glsha.py)"
  rm -rf "$GLDIR"/* && cp -a $G/glcache_before/. "$GLDIR"/ && mf $G/runs/glcache_mf_ret_$TAG.txt
  if cmp -s $G/runs/glcache_mf_before_$TAG.txt $G/runs/glcache_mf_ret_$TAG.txt; then
    log "$TAG GLCache returned (cmp EQUAL)"; tl "GLCache returned after replay $TAG (cmp EQUAL): $(python $G/glsha.py)"
  else log "$TAG GLCache NOT returned"; tl "GLCache NOT returned after replay $TAG"; exit 5; fi
fi
exit $RC
