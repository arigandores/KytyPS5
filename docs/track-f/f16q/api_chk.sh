#!/bin/bash
# Track F link F16q (HPP-597): the API check before a command longer than 60 s (item 371 (e)(2), 400 (z), general rule 30) and before each
# tag (item 254 (i)); appends one line to C:/kyty/f287/times.txt.  usage: bash api_chk.sh "<what follows>"   ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
[ -e C:/kyty/f287/STOP ] && { echo "STOP file"; exit 4; }
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
S=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/companies/$PAPERCLIP_COMPANY_ID/issues?status=in_progress" | python -c "
import json, sys
d = json.load(sys.stdin)
d = d if isinstance(d, list) else d.get('issues', [])
out = []
for i in d:
    if i.get('assigneeAgentId') == '2f5a0935-2e1a-4a76-8d98-67897fca3b8b':
        out.append('%s(run=%s)' % (i.get('identifier'), 'y' if i.get('executionRunId') else 'n'))
print(','.join(out) or 'none')
")
G=$(tasklist //FI "IMAGENAME eq kyty_emulator.exe" 2>/dev/null | grep -ci kyty_emulator)
L="$(date -u +%Y-%m-%dT%H:%M:%SZ) F16q API check before '$1': in_progress Harness Engineer links: [$S]; lock absent, STOP absent, kyty_emulator processes $G"
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock appeared"; exit 3; }
echo "$L" >> C:/kyty/f287/times.txt
echo "$L"
