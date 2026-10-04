#!/bin/bash
# rule 30: one line - the in_progress issues with a run (identifier, assignee, run)
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/companies/$PAPERCLIP_COMPANY_ID/issues?status=in_progress" | python -c "
import json,sys
d=json.load(sys.stdin)
d=d if isinstance(d,list) else d.get('issues',d.get('items',[]))
names={'2f5a0935':'HarnessEng','8e98843f':'ProbeDesigner','eb15eb75':'EmuEng','dc34de0a':'RedTeam','f1276629':'Lead','aabc0a15':'Auditor'}
r=[]
for i in d:
    a=(i.get('assigneeAgentId') or '')[:8]
    r.append('%s/%s/%s' % (i.get('identifier'), names.get(a,a), 'run' if i.get('executionRunId') else '-'))
he=[x for x in r if '/HarnessEng/run' in x and not x.startswith('HPP-537/')]
print('api in_progress: %s; run links of another track with a run: %s' % (' '.join(r), ' '.join(he) or 'none'))
"
