#!/bin/bash
# Track M link M9f (HPP-871; ROADMAP s122 item 785 (v)(5)): copy of the M6c (HPP-850) file chk_m6c.sh with the names moved (m6c -> m9f, M6C -> M9F, M6c -> M9f, HPP-850 -> HPP-871); no change of meaning.
# Track M link M9f (HPP-871; ROADMAP s122 item 767 (i)): copy of the M3a (HPP-842) file chk_m3a.sh with the names moved (m3a -> m9f, M3A -> M9F, M3a -> M9f, HPP-842 -> HPP-871); no change of meaning.
# Track M link M9f (HPP-871): port of FS15c chk_fs15c.sh - the check before a call (general rules 26, 27, 30; item 254 (i) MINOR-4):
# stop file, lock, new comments of HPP-871 (after the last seen id kept in last_comment.txt), the lock queue - one times.txt line with
# the answer.  Not a member of the seal (process helper).  exit 0 clear; 3 lock; 4 stop file; 6 new comments (read them before the
# call); 9 queue busy.  usage: bash C:/kyty/m657/m9f/chk_m9f.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/m657/m9f
[ -e C:/kyty/m657/STOP ] && { echo "STOP file: $(head -1 C:/kyty/m657/STOP)"; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
LAST=$(cat $G/last_comment.txt 2>/dev/null)
NEW=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/issues/HPP-871/comments" | python -c "
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
QF=$(python $G/queue_m9f.py 2>&1 | tr '\n' ';'); QS=$(echo "$QF" | cut -c1-200)
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M9f API check before $T: comments new (not own) ${NN:-?}; queue: $QS" >> $G/times.txt
echo "comments new (not own) ${NN:-?}; queue: $QS"
[ "${NN:-x}" = 0 ] || { echo "new comments or API error - read before the call"; [ -n "$LID" ] && [ "$LID" != "-" ] && echo "$LID" > $G/last_comment.txt; exit 6; }
[ -n "$LID" ] && [ "$LID" != "-" ] && echo "$LID" > $G/last_comment.txt
echo "$QF" | grep -q 'QUEUE FREE' || exit 9
exit 0
