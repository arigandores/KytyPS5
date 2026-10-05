#!/bin/bash
# S15a3 (copy of s15/apichk.sh): one line of times.txt with the API state of the series (general rule 30) before a command longer than 60 s
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
R=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/companies/$PAPERCLIP_COMPANY_ID/issues?status=in_progress&limit=50" | python -c "
import json,sys
d=json.load(sys.stdin); d=d if isinstance(d,list) else d.get('items',d)
print('; '.join('%s exec %s' % (i.get('identifier'), (i.get('executionRunId') or '-')[:8]) for i in d))")
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) API in_progress: $R; lock $( [ -e C:/kyty/SEALED_RUN.lock ] && echo PRESENT || echo none) - before: $1" >> C:/kyty/s288/s15a3/times.txt
tail -1 C:/kyty/s288/s15a3/times.txt
