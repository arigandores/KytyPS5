# FS13b (HPP-788, Red Team, ROADMAP s122 item 697(g)(2)): copy of the FS12b file with fs12b->fs13b, FS12b->FS13b, fs12n->fs13n in ALL lines (older header lines that say FS13b mean earlier links).
# FS13b (HPP-751, Red Team, ROADMAP s122 item 683(g)(2)): copy of the FS11b file with fs11b->fs13b, fs11n->fs13n, FS11b->FS13b in ALL lines (older header lines below that say FS13b mean FS11b HPP-715); default commits 730ed40a (FS12) / 9aaea58c (FS12 without FS12a).
# FS10b (HPP-685, Red Team, ROADMAP s122 item 624(e)(2)): copy of the FS9b file; fs9b -> fs10b in code lines only (paths, names, times label).
# FS13b (HPP-715, Red Team, ROADMAP s122 item 647(d)(2)): copy of the FS10b file; fs10b -> fs13b, fs10n -> fs13n (paths, names, times label), default commits ee9632be / eded064e.
# FS9b (HPP-672, Red Team, ROADMAP s122 item 604(d)(2)): copy of the FS8b file with fs8b -> fs9b (paths, names, times label).
#!/bin/bash
# FS8b (HPP-556, Red Team, ROADMAP s122 item 454(g)(2)): copy of the F15d file with f15d -> fs8b (paths, names).
# FS8b (HPP-515, Red Team): copy of the F15c file with f15c -> fs8b (paths, names); the stand driver stays docs/track-f/f15c/run_stand_f15c.py.
# FS8b (HPP-514, ROADMAP s122 item 412): copy of the F14e api_chk.sh, names changed. Was:
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
LINE="$(date -u +%FT%TZ) FS13b API check before '$1': in_progress Harness Engineer links: [$L]; lock absent, STOP absent, gate processes (argv ends with procload.py) $P; step runs under watchdog watch_fs13b.py (p.431(v))"
echo "$LINE" >> C:/kyty/f287/times.txt
echo "$LINE"
