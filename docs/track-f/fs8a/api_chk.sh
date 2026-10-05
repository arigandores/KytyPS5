#!/bin/bash
# FS8a (HPP-571): copy of the FS7a api_chk.sh, paths and names changed. Was:
# FS8a (HPP-571): copy of the FS6a api_chk.sh, names changed. Was:
# FS8a (HPP-571): copy of the F15c api_chk.sh, names changed. Was:
# F15c (HPP-514, ROADMAP s122 item 412): copy of the F14e api_chk.sh, names changed. Was:
# F14e (HPP-505, ROADMAP s122 items 400(z), 425(b), 431(d)): one API check before a step longer than 60 s - lists the
# in_progress links of Harness Engineer (with executionRunId and whether the title says "без игры"), the lock and STOP;
# appends one line to C:/kyty/f287/times.txt. Exit 0 always unless lock (3) / STOP (4). Usage: api_chk.sh <step name>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && { echo STOP; exit 4; }
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
    out.append('%s(run=%s,%s)'%(i['identifier'],'y' if i.get('executionRunId') else 'n','no-game' if 'без игры' in t else 'series'))
print(','.join(out))")
P=$(python -c "
import psutil
import os
print(len([p for p in psutil.process_iter(['pid','cmdline']) if p.info['pid']!=os.getpid() and any(a.replace(chr(92),'/').endswith('/procload'+'.py') or a=='procload'+'.py' for a in (p.info['cmdline'] or []))]))")
LINE="$(date -u +%FT%TZ) FS8a API check before '$1': in_progress Harness Engineer links: [$L]; lock absent, STOP absent, gate processes (argv ends with procload.py) $P; step runs under watchdog watch_fs8a.py (p.431(v))"
echo "$LINE" >> C:/kyty/f287/times.txt
echo "$LINE"
