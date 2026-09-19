import re,json,statistics as S,csv
from pathlib import Path
from collections import defaultdict,Counter
p=Path('C:/kyty/s99'); out=p/'plan100_raw'; rows={}; gates={}; refs={}
for ln,line in enumerate((p/'log_cal99a.txt').open('rb'),1):
 if line.startswith(b'GateArm:'):
  d={k.decode():int(v) for k,v in re.findall(rb'(\w+)=(-?\d+)',line)}; gates[d['block']]=d
 if line.startswith((b'FrameTrace:',b'FrameTrace-x:',b'FrameTrace-draw:')):
  d={k.decode():int(v) for k,v in re.findall(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)',line)};n=d.pop('n');rows.setdefault(n,{}).update(d)
  if line.startswith(b'FrameTrace:'):refs[n]=ln
bl=defaultdict(list);t=0
for n,r in sorted(rows.items()):
 r['n']=n;r['line']=refs[n];t+=r['dt_us']/1e6;r['t']=t;bl[r['blk']].append(r)
for b,rr in bl.items():
 for i,r in enumerate(rr):r['idx']=i
edges=[b for b in gates if b-1 in gates and gates[b]['arm']!=gates[b-1]['arm']]
trim=set()
for b in edges:trim.update(r['n'] for r in bl[b-1][-1:]+bl[b][:2])
win=[r for n,r in sorted(rows.items()) if n>=2100 and r['blk']>=1]
kept=[r for r in win if r['n'] not in trim]
def stat(rr):
 if not rr:return {}
 return {'N':len(rr),'frames':[rr[0]['n'],rr[-1]['n']],'refs':[rr[0]['line'],rr[-1]['line']],**{k:S.fmean(r[k] for r in rr) for k in ['draws','dispatches','dt_us','cpu_gpu_us','bf_burn_ns','rt_att','rt_kpx','submits','gpu_busy_us']},'draw_quantiles':[sorted(r['draws'] for r in rr)[int((len(rr)-1)*q)] for q in [0,.01,.1,.25,.5,.75,.9,.99,1]],'low3000':sum(r['draws']<3000 for r in rr),'low4000':sum(r['draws']<4000 for r in rr),'high6000':sum(r['draws']>6000 for r in rr)}
def contrast(rr):
 a=[stat([r for r in rr if r['arm']==i]) for i in (0,1)]
 return {'arms':a,'work_pct':100*(a[1]['draws']/a[0]['draws']-1)} if all(a) else {'arms':a}
res={'window':contrast(win),'retained':contrast(kept),'removed':contrast([r for r in win if r['n'] in trim]),'whole_schedule':contrast([r for r in rows.values() if r['n']>=1801]),'complete_blocks':contrast([r for r in win if len([x for x in bl[r['blk']] if x['n']>=2100])==30]),'pre_schedule':stat([r for r in rows.values() if 1000<=r['n']<1800])}
res['block_means']=[{'block':b,'arm':rr[0]['arm'],**stat([r for r in rr if r['n']>=2100])} for b,rr in bl.items() if any(r['n']>=2100 for r in rr)]
res['draw_bins']={f'{lo}:{hi}':contrast([r for r in win if lo<=r['draws']<hi]) for lo,hi in [(0,1000),(1000,3000),(3000,4000),(4000,5000),(5000,6000),(6000,8000),(8000,20000)]}
res['phase']={str(i):contrast([r for r in win if r['idx']==i]) for i in range(30)}
res['quarters']=[contrast(win[int(len(win)*i/4):int(len(win)*(i+1)/4)]) for i in range(4)]
res['cycles']=[{'start_block':b,**contrast([r for k in range(b,b+4) for r in bl[k]])} for b in range(12,64,4)]
res['complete_pairs']=[{'blocks':[b,b+1],**contrast(bl[b]+bl[b+1])} for b in range(10,66,2)]
res['correlation']={str(a):{k:S.correlation([r['draws'] for r in win if r['arm']==a],[r[k] for r in win if r['arm']==a]) for k in ['dt_us','cpu_gpu_us','dispatches','rt_att','submits','gpu_busy_us']} for a in (0,1)}
res['edge_profile']={str(a):{str(i):stat([bl[b][i] for b in edges if gates[b]['arm']==a and i<len(bl[b]) and bl[b][i]['n']>=2100]) for i in range(10)} for a in (0,1)}
for r in rows.values():r['armidx']=r['idx']+(30 if r['blk']%4 in (0,2) else 0)
res['arm_phases']={f'{lo}:{hi}':contrast([r for r in win if lo<=r['armidx']<hi]) for lo,hi in [(0,2),(2,6),(6,15),(15,30),(30,60),(6,60)]}
res['cycle_arm_phases']={f'{lo}:{hi}':contrast([r for r in win if 12<=r['blk']<=63 and lo<=r['armidx']<hi]) for lo,hi in [(0,2),(2,6),(6,15),(15,30),(30,60),(6,60)]}
res['vblank_bins']={f'{lo}:{hi}':contrast([r for r in win if lo<=r['dt_us']<hi]) for lo,hi in [(0,25000),(25000,42000),(42000,58000),(58000,1000000)]}
res['pairs_work']={k:{'mean':S.fmean(x['work_pct'] for x in res[k]),'median':S.median(x['work_pct'] for x in res[k]),'min':min(x['work_pct'] for x in res[k]),'max':max(x['work_pct'] for x in res[k]),'negative':sum(x['work_pct']<0 for x in res[k]),'N':len(res[k])} for k in ['complete_pairs','cycles']}
(out/'analysis.json').write_text(json.dumps(res,indent=2))
fields=['n','line','t','arm','blk','idx','draws','dispatches','dt_us','cpu_gpu_us','bf_burn_ns','rt_att','rt_kpx','submits','bf_edge','gpu_busy_us']
with (out/'rows.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows.values())
print(json.dumps({k:v for k,v in res.items() if k not in ['block_means','phase','edge_profile','draw_bins','cycles','complete_pairs']},indent=2))
