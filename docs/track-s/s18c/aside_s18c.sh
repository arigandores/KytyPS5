# Track S link S18c (HPP-644): port of S17c2 aside_s17c2.sh - only the reason rep (a NOT_ADMITTED tag of S18c, one repeat by the same
# name, item 273 (z)); the ed2 branch is unreachable (the reason is refused before it).
#!/bin/bash
# Track S link S17c (HPP-613; ROADMAP s122 item 537 (e), 548 (b)): moves the files of a made tag aside so that the tag runs again by the
# same name (go_s17c.sh refuses when runs/<tag> or state/<tag> exists).  Two reasons only:
#   ed2 - s17c_c2 made on S17a2 2b5e2ce6 under seal edition 2 (item 537 (v): not repeated on that binary; the capture tag runs again on the
#         seal edition 3 binary); allowed only for s17c_c2 whose runs/s17c_c2/installed_sha.txt is 2b5e2ce6, once;
#   rep - one repeat by the same name after an interference (item 537 (e), named beforehand): allowed only when runs/<tag>/read.txt reads
#         'READING NOT_ADMITTED', the tag is a seal edition 3 tag, and no earlier rep of the tag exists (a second interference of the same
#         tag is a question to the lead).
# Moves runs/<tag> -> runs/<tag>.<reason>_<UTC>, state/<tag> -> state/<tag>.<reason>_<UTC>, and the tag files of the root (log, stdout,
# json, rec, rec idx, gpuclk, go output) into aside/<tag>.<reason>_<UTC>/; writes the moved list and a times.txt line.  Never deletes.
# Refuses under any lock, with the stop file, while go_<tag>.out.txt has no rc line, for the carried K2(2) tags.  ASCII only.
# usage: bash aside_s17c.sh <tag> ed2|rep          (S17C_ROOT overrides the root for the fixtures)
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; WHY=$2
G=${S18C_ROOT:-C:/kyty/s288/s18c}
ED2=2b5e2ce677c557bb0dd28ccc114588aea5c4b6f56c10ab1450faadd81328d544
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
case "$T" in s18_c01|s18_c02|s18_c03|s18_c04|s18_c05|s18_c06|s18_c07|s18_c08|s18_c09|s18_c10|s18_c11|s18_c12|s18_c13|s18_c14|s18_c15|s18_c16|s18_c17|s18_c18|s18_c19|s18_ks|s18_r|s18_e1|s18_e2|s18_v|s18_w) ;;
  *) echo "usage: aside_s18c.sh <tag> rep"; exit 2;; esac
case "$WHY" in rep) ;; *) echo "usage: aside_s18c.sh <tag> rep"; exit 2;; esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "ASIDE REFUSED lock held"; exit 3; }
[ -e C:/kyty/s288/STOP ] && { echo "ASIDE REFUSED stop file"; exit 4; }
[ -d $G/runs/$T ] || { echo "ASIDE REFUSED no runs/$T"; exit 2; }
if [ -e $G/go_$T.out.txt ] && ! grep -q '^rc=' $G/go_$T.out.txt; then echo "ASIDE REFUSED go_$T.out.txt has no rc line"; exit 2; fi
if [ "$WHY" = ed2 ]; then
  [ "$T" = s17c_c2 ] || { echo "ASIDE REFUSED ed2 is for s17c_c2 only"; exit 2; }
  [ "$(head -1 $G/runs/$T/installed_sha.txt 2>/dev/null | cut -c1-64)" = "$ED2" ] || { echo "ASIDE REFUSED runs/$T is not an S17a2 2b5e2ce6 run"; exit 2; }
  ls -d $G/runs/$T.ed2_* > /dev/null 2>&1 && { echo "ASIDE REFUSED $T was already set aside as ed2"; exit 2; }
else
  [ "$(head -1 $G/runs/$T/installed_sha.txt 2>/dev/null | cut -c1-64)" = "$ED2" ] && { echo "ASIDE REFUSED runs/$T is an edition 2 run (use ed2)"; exit 2; }
  grep -q '^  READING NOT_ADMITTED' $G/runs/$T/read.txt 2>/dev/null || { echo "ASIDE REFUSED runs/$T/read.txt does not read NOT_ADMITTED"; exit 2; }
  ls -d $G/runs/$T.rep_* > /dev/null 2>&1 && { echo "ASIDE REFUSED second interference of $T - question to the lead (item 537 (e))"; exit 6; }
fi
S=$(date -u +%Y%m%dT%H%M%SZ)
A=$G/aside/$T.${WHY}_$S
mkdir -p $A || exit 1
MOVED="runs/$T.${WHY}_$S"
mv $G/runs/$T $G/runs/$T.${WHY}_$S || exit 1
if [ -e $G/state/$T ]; then mv $G/state/$T $G/state/$T.${WHY}_$S || exit 1; MOVED="$MOVED state/$T.${WHY}_$S"; fi
for f in log_$T.txt stdout_$T.txt $T.json rec_$T.mp4 rec_$T.mp4.idx gpuclk_$T.csv go_$T.out.txt; do
  if [ -e $G/$f ]; then mv $G/$f $A/ || exit 1; MOVED="$MOVED aside/$T.${WHY}_$S/$f"; fi
done
echo "$MOVED" | tr ' ' '\n' > $A/moved.txt
echo "$(u) S18c aside_s18c $T $WHY: moved $MOVED" >> $G/times.txt
echo "ASIDE OK $T $WHY $S"
