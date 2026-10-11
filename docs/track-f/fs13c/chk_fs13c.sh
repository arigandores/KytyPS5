#!/bin/bash
# Track F link FS13c (HPP-789; ROADMAP s122 item 697 (g)(3)): copy of the FS12c (HPP-752) file chk_fs12c.sh with the names moved (fs12c -> fs13c, FS12C -> FS13C, FS12c -> FS13c, HPP-752 -> HPP-789); no change of meaning.
# Track F link FS13c (HPP-789; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file chk_f33e.sh with the names moved (f33e -> fs13c, F33E -> FS13C, F33e -> FS13c, HPP-746 -> HPP-789); no change of meaning.
# Track F link FS13c (HPP-789; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file chk_f34c.sh with the names moved (f34c -> fs13c, F34C -> FS13C, F34c -> FS13c, HPP-740 -> HPP-789); no change of meaning.
# FS13c (HPP-789; port of F26c chk_f26c.sh): the check before a call (general rules 26, 27, 30; item 254 (i) MINOR-4): stop file, lock,
# new comments of HPP-789 (after the last seen id kept in last_comment.txt), the lock queue - one times.txt line with the answer.  Not a
# member of the seal (process helper).  exit 0 clear; 3 lock; 4 stop file; 6 new comments (read them before the call); 9 queue busy.
# usage: bash C:/kyty/f287/fs13c/chk_fs13c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/fs13c
[ -e C:/kyty/f287/STOP ] && { echo "STOP file: $(head -1 C:/kyty/f287/STOP)"; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
LAST=$(cat $G/last_comment.txt 2>/dev/null)
NEW=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/issues/HPP-789/comments" | python -c "
import json, sys
d = json.load(sys.stdin)
d = d if isinstance(d, list) else d.get('comments', [])
d = sorted(d, key=lambda c: c.get('createdAt') or '')
last = sys.argv[1]
ids = [c.get('id') for c in d]
new = d[ids.index(last) + 1:] if last in ids else d
own = '$PAPERCLIP_AGENT_ID'
foreign = [c for c in new if c.get('authorAgentId') != own]
print('%d %d %s' % (len(new), len(foreign), ids[-1] if ids else '-'))
for c in foreign:
    sys.stderr.write('NEW COMMENT %s %s: %s\n' % (c.get('id'), c.get('createdAt'), (c.get('body') or '')[:400].encode('ascii', 'replace').decode()))
" "$LAST")
NN=$(echo "$NEW" | cut -d' ' -f2); LID=$(echo "$NEW" | cut -d' ' -f3)
QS=$(python $G/queue_fs13c.py 2>&1 | tr '\n' ';' | cut -c1-200)
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS13c API check before $T: comments new (not own) ${NN:-?}; queue: $QS" >> C:/kyty/f287/times.txt
echo "comments new (not own) ${NN:-?}; queue: $QS"
[ "${NN:-x}" = 0 ] || { echo "new comments or API error - read before the call"; [ -n "$LID" ] && [ "$LID" != "-" ] && echo "$LID" > $G/last_comment.txt; exit 6; }
[ -n "$LID" ] && [ "$LID" != "-" ] && echo "$LID" > $G/last_comment.txt
echo "$QS" | grep -q 'QUEUE FREE' || exit 9
exit 0
