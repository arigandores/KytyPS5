#!/bin/bash
# F29c3 (HPP-713): copy of f29c/api_chk.sh, times path changed. Was: F29c: rule 30 - one times.txt line with the API answer: Harness Engineer links in_progress with a live run.
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
R=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/companies/$PAPERCLIP_COMPANY_ID/issues?status=in_progress" | python -c "
import json,sys
d=json.load(sys.stdin)
d=d if isinstance(d,list) else d.get('issues',d.get('items',[]))
print(' '.join('%s:%s:%s'%(i.get('identifier'),(i.get('assigneeAgentId') or '')[:8],'run' if i.get('executionRunId') else '-') for i in d))
")
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) rule 30 API check before: $1 | in_progress: $R" >> C:/kyty/f287/f29c3/times.txt
echo "$R"
