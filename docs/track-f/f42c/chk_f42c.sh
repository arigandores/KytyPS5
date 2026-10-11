#!/bin/bash
# Track F link F42c (HPP-781; ROADMAP s122 item 694 (g)(6), 719 (d)): copy of the F44c (HPP-793) file chk_f44c.sh with the names moved
# (f44c -> f42c, F44C -> F42C, F44c -> F42c, HPP-793 -> HPP-781) and one check added: the end of the F46c series (HPP-800 done / cancelled / in_review without a run,
# item 719 (d) - F42c waits for it by general rule 27).  The check before a call (general rules 26, 27, 30; item 254 (i) MINOR-4): stop
# file, lock, new comments of HPP-781 (after the last seen id kept in last_comment.txt), the lock queue, HPP-800 - times.txt lines with the
# answers.  Not a member of the seal (process helper).  exit 0 clear; 3 lock; 4 stop file; 6 new comments (read them before the call);
# 9 queue busy or F46c not ended.
# usage: bash C:/kyty/f287/f42c/chk_f42c.sh <name>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f42c
[ -e C:/kyty/f287/STOP ] && { echo "STOP file: $(head -1 C:/kyty/f287/STOP)"; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
LAST=$(cat $G/last_comment.txt 2>/dev/null)
NEW=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/issues/HPP-781/comments" | python -c "
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
QS=$(python $G/queue_f42c.py 2>&1 | tr '\n' ';' | cut -c1-200)
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F42c API check before $T: comments new (not own) ${NN:-?}; queue: $QS" >> C:/kyty/f287/times.txt
echo "comments new (not own) ${NN:-?}; queue: $QS"
[ "${NN:-x}" = 0 ] || { echo "new comments or API error - read before the call"; [ -n "$LID" ] && [ "$LID" != "-" ] && echo "$LID" > $G/last_comment.txt; exit 6; }
[ -n "$LID" ] && [ "$LID" != "-" ] && echo "$LID" > $G/last_comment.txt
echo "$QS" | grep -q 'QUEUE FREE' || exit 9
# item 719 (d): F42c waits for the end of the F46c series (HPP-800) by general rule 27 - the call goes only when HPP-800 is done,
# cancelled or in_review without a going run; any other status - exit 9 with a times.txt line (no lock is taken)
ST8=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/issues/HPP-800" | python -c "
import json, sys
d = json.load(sys.stdin)
print('%s run=%s' % (d.get('status'), 'y' if d.get('executionRunId') else 'n'))
" 2>/dev/null)
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F42c check before $T: F46c HPP-800 ${ST8:-API error} (item 719 (d): F42c after the end of the F46c series)" >> C:/kyty/f287/times.txt
echo "F46c HPP-800 ${ST8:-API error}"
case "$ST8" in done\ *|cancelled\ *|in_review\ run=n) ;; *) exit 9;; esac
exit 0
