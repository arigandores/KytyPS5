#!/bin/bash
# Track F link F30q (HPP-727; ROADMAP s122 item 664 (z)): the F30m (HPP-723) file with the names moved (f30m -> f30q, HPP-723 -> HPP-727,
# F30M_ -> F30Q_) and the tag set of item 664 (z)(2)-(3): f30_s1_w6, f30_s<1..9>_c6 [_r1.._r3].
# Track F link F30q (HPP-727): the F29e file with the names and the tag set moved (f29e -> f30q, HPP-704 -> HPP-727); no change of meaning.
# F30q (HPP-727; port of F25m chk_f25m.sh): the check before a tag call (general rules 26, 27, 30; item 254 (i) MINOR-4): stop file, lock,
# new comments of HPP-727 (after the last seen id kept in last_comment.txt), the lock queue (queue_f30q.py) - one times.txt line with the
# answer.  Not a member of the seal (process helper).  exit 0 clear; 3 lock; 4 stop file; 6 new comments (read them before the tag);
# 9 queue busy.  ASCII only.
# usage: bash C:/kyty/f287/f30q/chk_f30q.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f30q
[ -e C:/kyty/f287/STOP ] && { echo "STOP file: $(head -1 C:/kyty/f287/STOP)"; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
LAST=$(cat $G/last_comment.txt 2>/dev/null)
NEW=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/issues/HPP-727/comments" | python -c "
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
QS=$(python $G/queue_f30q.py 2>&1 | tr '\n' ';' | cut -c1-200)
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30q API check before $T: comments new (not own) ${NN:-?}; queue: $QS" >> C:/kyty/f287/times.txt
echo "comments new (not own) ${NN:-?}; queue: $QS"
[ "${NN:-x}" = 0 ] || { echo "new comments or API error - read before the tag"; exit 6; }
[ -n "$LID" ] && [ "$LID" != "-" ] && echo "$LID" > $G/last_comment.txt
echo "$QS" | grep -q 'QUEUE FREE' || exit 9
exit 0
