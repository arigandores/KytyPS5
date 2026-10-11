#!/bin/bash
# Track F link F46c (HPP-800; ROADMAP s122 item 702 (g)): copy of the F44c (HPP-793) file chk_f44c.sh with the names moved (f44c -> f46c, F44C -> F46C, F44c -> F46c, HPP-793 -> HPP-800); no change of meaning.
# Track F link F46c (HPP-800; ROADMAP s122 item 698 (d)(4)): copy of the F38c (HPP-765) file chk_f38c.sh with the names moved (f38c -> f46c, F38C -> F46C, F38c -> F46c, HPP-765 -> HPP-800); no change of meaning.
# Track F link F46c (HPP-800; ROADMAP s122 item 691 (d)(4)): copy of the FS12c (HPP-752) file chk_fs12c.sh with the names moved (fs12c -> f46c, FS12C -> F46C, FS12c -> F46c, HPP-752 -> HPP-800); no change of meaning.
# Track F link F46c (HPP-800; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file chk_f33e.sh with the names moved (f33e -> f46c, F33E -> F46C, F33e -> F46c, HPP-746 -> HPP-800); no change of meaning.
# Track F link F46c (HPP-800; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file chk_f34c.sh with the names moved (f34c -> f46c, F34C -> F46C, F34c -> F46c, HPP-740 -> HPP-800); no change of meaning.
# F46c (HPP-800; port of F26c chk_f26c.sh): the check before a call (general rules 26, 27, 30; item 254 (i) MINOR-4): stop file, lock,
# new comments of HPP-800 (after the last seen id kept in last_comment.txt), the lock queue - one times.txt line with the answer.  Not a
# member of the seal (process helper).  exit 0 clear; 3 lock; 4 stop file; 6 new comments (read them before the call); 9 queue busy.
# usage: bash C:/kyty/f287/f46c/chk_f46c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f46c
[ -e C:/kyty/f287/STOP ] && { echo "STOP file: $(head -1 C:/kyty/f287/STOP)"; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
LAST=$(cat $G/last_comment.txt 2>/dev/null)
NEW=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/issues/HPP-800/comments" | python -c "
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
QS=$(python $G/queue_f46c.py 2>&1 | tr '\n' ';' | cut -c1-200)
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F46c API check before $T: comments new (not own) ${NN:-?}; queue: $QS" >> C:/kyty/f287/times.txt
echo "comments new (not own) ${NN:-?}; queue: $QS"
[ "${NN:-x}" = 0 ] || { echo "new comments or API error - read before the call"; [ -n "$LID" ] && [ "$LID" != "-" ] && echo "$LID" > $G/last_comment.txt; exit 6; }
[ -n "$LID" ] && [ "$LID" != "-" ] && echo "$LID" > $G/last_comment.txt
echo "$QS" | grep -q 'QUEUE FREE' || exit 9
exit 0
