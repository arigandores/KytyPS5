import pickle,json,statistics as st,math
from pathlib import Path
O=Path('C:/kyty/s99/work99_raw')
def pop(rs,fields=('draws','dt_us','dispatches','submits','da_flip','da_present','fbp_n')):
 g=[[r for r in rs if r['arm']==a] for a in (0,1)];out={'N':[len(x) for x in g]}
 if not all(g):return out
 for k in fields:
  v=[st.fmean(r[k] for r in x) for x in g];out[k]=[round(x,7) for x in v]+[round(100*(v[1]/v[0]-1),7) if v[0] else None]
 return out
for tag in ['bf99e','eng99a4']:
 rows,bs=pickle.load((O/(tag+'.pkl')).open('rb'));sel=[rows[n] for ns in bs.values() for n in ns];start=rows[1801]['time'];report={}
 report['sealed']=pop(sel)
 report['quarters']=[pop([r for r in sel if (q/4)*(rows[max(rows)]['time']-start)<=r['time']-start<((q+1)/4)*(rows[max(rows)]['time']-start)]) for q in range(4)]
 report['first300']=pop([r for r in sel if r['time']-start<300]);report['after300']=pop([r for r in sel if r['time']-start>=300])
 report['same_arm_block_first_vs_second']={str(m):pop([r for r in sel if r['blk']%4 in mods]) for m,mods in [('first',[1,3]),('second',[0,2])]}
 report['windows']={f'{lo}..{hi}':pop([rows[1801+90*b+i] for b in bs for i in range(lo,hi+1)]) for lo,hi in [(0,89),(2,88),(15,88),(30,88),(60,88),(60,89),(59,88),(61,87),(60,86),(60,87),(59,87),(58,88),(57,89),(30,59),(0,29)]}
 report['mod']={str(m):[pop([r for r in sel if r['n']%m==v],['draws','dt_us']) for v in range(m)] for m in [2,3,4,5,6]}
 report['autocorrelation']={}
 for a in [0,1]:
  ar=[r for r in sel if r['arm']==a];mu=st.fmean(r['draws'] for r in ar);var=st.fmean((r['draws']-mu)**2 for r in ar)
  report['autocorrelation'][str(a)]={str(lag):round(st.fmean((r['draws']-mu)*(rows[r['n']+lag]['draws']-mu) for r in ar if r['n']+lag in rows and rows[r['n']+lag]['blk']==r['blk'])/var,6) for lag in range(1,13)}
 report['draws_sd']=[st.pstdev(r['draws'] for r in sel if r['arm']==a) for a in [0,1]]
 report['examples']=[{k:r[k] for k in ['n','line','arm','draws','dt_us','fbp_n']} for r in sel[:15]]
 (O/(tag+'_diagnostic.json')).write_text(json.dumps(report,indent=2))
 print(tag,json.dumps({k:report[k] for k in ['sealed','quarters','first300','after300','same_arm_block_first_vs_second','windows','autocorrelation','draws_sd']},indent=2))
