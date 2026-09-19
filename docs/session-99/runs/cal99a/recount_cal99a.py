"""Parent's raw admission-number check. Never computes B/F or a burn candidate."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import re
import statistics

root=Path('C:/kyty/s99')
rows, gates = {}, {}
sha=hashlib.sha256()
tokens=re.compile(rb'\b(n|arm|blk|draws|dt_us|bf_edge)=(\d+)\b')
gate=re.compile(rb'GateArm: arm=(\d+).*?block=(\d+) frame=(\d+)')
with (root/'log_cal99a.txt').open('rb') as stream:
    for line in stream:
        sha.update(line)
        m=gate.search(line)
        if m:
            a,b,n=map(int,m.groups()); gates[b]=(a,n)
        if line.startswith((b'FrameTrace:',b'FrameTrace-draw:',b'FrameTrace-x:')):
            v={k.decode():int(x) for k,x in tokens.findall(line)}
            if 'n' in v:
                rows.setdefault(v.pop('n'),{}).update(v)
groups=defaultdict(list)
for n,r in sorted(rows.items()):
    if 'blk' in r and 'arm' in r:
        groups[r['blk']].append(n)
changes=[b for b in gates if b-1 in gates and gates[b][0]!=gates[b-1][0]]
falls=[b for b in changes if gates[b][0]==0 and len(groups[b])>=3]
trim=set()
for b in changes:
    trim.update(groups[b-1][-1:]); trim.update(groups[b][:2])
window=[n for n,r in rows.items() if n>=2100 and r.get('blk',0)>=1 and 'arm' in r]
data={}
for arm in (0,1):
    full=[n for n in window if rows[n]['arm']==arm]
    kept=[n for n in full if n not in trim]
    data[str(arm)]={
        'full_rows':len(full),'Tstar_retained':len(kept),
        'draws_mean_full':statistics.mean(rows[n]['draws'] for n in full),
        'dt_us_mean_Tstar':statistics.mean(rows[n]['dt_us'] for n in kept),
    }
draw_pct=100*(data['1']['draws_mean_full']/data['0']['draws_mean_full']-1)
result={
    'log_sha256':sha.hexdigest(),'last_frame':max(rows),
    'arms':data,'draw_change_pct':draw_pct,
    'C5_limit_pct':2,'C5_PASS':abs(draw_pct)<=2,
    'completed_falling_edges':len(falls),'R2_required':30,'R2_PASS':len(falls)>=30,
    'changes':len(changes),'bf_edge_total':sum(r.get('bf_edge',0) for r in rows.values()),
    'Tstar_rows_in_window':sum(n in trim for n in window),
    'scope':'Admission diagnostics only; no B/F, burn candidate or architecture verdict',
}
assert round(draw_pct,3)==-4.097
assert len(falls)==17
assert abs(data['0']['dt_us_mean_Tstar']-50501.825)<0.001
assert abs(data['1']['dt_us_mean_Tstar']-42516.671)<0.001
(root/'recount_cal99a.json').write_bytes((json.dumps(result,indent=2)+'\n').encode('utf8'))
print(json.dumps(result,indent=2))
