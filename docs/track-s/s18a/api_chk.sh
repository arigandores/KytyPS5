#!/bin/bash
# S18a (HPP-642): copy of the FS8a api_chk.sh, paths and names changed (rule 30 with item 535(g)). One API check before a
# step longer than 60 s - lists the in_progress links of Harness Engineer (executionRunId y/n, "no-game" if the title or
# description says so), the lock, STOP and processes whose argv ends with procload.py; appends one line to
# C:/kyty/s288/s18a/times.txt. Exit 0 unless lock (3) / STOP (4). Usage: api_chk.sh <step name>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/s288/STOP ] && { echo STOP; exit 4; }
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
L=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/companies/$PAPERCLIP_COMPANY_ID/issues?status=in_progress" | python -c "
import json,sys
d=json.load(sys.stdin)
d=d if isinstance(d,list) else d.get('issues',[])
out=[]
for i in d:
    if i.get('assigneeAgentId')!='2f5a0935-2e1a-4a76-8d98-67897fca3b8b':
        continue
    t=(i.get('title') or '')+' '+(i.get('description') or '')
    out.append('%s(run=%s,%s)'%(i['identifier'],'y' if i.get('executionRunId') else 'n','no-game' if 'без игры' in t.lower() else 'series'))
print(','.join(out))")
P=$(python -c "
import psutil
import os
print(len([p for p in psutil.process_iter(['pid','cmdline']) if p.info['pid']!=os.getpid() and any(a.replace(chr(92),'/').endswith('/procload'+'.py') or a=='procload'+'.py' for a in (p.info['cmdline'] or []))]))")
LINE="$(date -u +%FT%TZ) rule30 S18a API check before '$1': in_progress Harness Engineer links: [$L]; lock absent, STOP absent, gate processes (argv ends with procload.py) $P"
echo "$LINE" >> C:/kyty/s288/s18a/times.txt
echo "$LINE"
