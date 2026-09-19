import pickle,json,statistics as st,math
from pathlib import Path
O=Path('C:/kyty/s99/work99_raw')
for tag in ['bf99e','eng99a4']:
 rows,bs=pickle.load((O/(tag+'.pkl')).open('rb'));s=[rows[n] for ns in bs.values() for n in ns]
 def work(rs):
  mu=[st.fmean(r['draws'] for r in rs if r['arm']==a) for a in [0,1]];return [round(x,5) for x in mu]+[round(100*(mu[1]/mu[0]-1),6)]
 print('\n',tag)
 quartets=list(range(min(bs),max(bs)+1,4));print('balanced quarter',[(qs[0],qs[-1]+3,work([r for r in s if r['blk']//4 in [q//4 for q in qs]])) for qs in [quartets[len(quartets)*i//4:len(quartets)*(i+1)//4] for i in range(4)]])
 print('byidx bands',[(i,work([rows[1801+90*b+j] for b in bs for j in range(i,i+5)])) for i in range(15,90,5)])
 print('modn', {m:[work([r for r in s if r['n']%m==k]) for k in range(m)] for m in [2,3,4,5,6]})
 print('tailcounts U,A',[(cut,[sum(r['draws']<cut for r in s if r['arm']==a) for a in [0,1]]) for cut in [1000,2000,3000,4000,4500,5500,6000,7000]])
 print('low examples',[(r['n'],r['blk'],(r['n']-1801)%90,r['draws'],r['dt_us'],r['fbp_n'],r['line']) for r in s if r['arm']==0 and r['draws']<3000][:30])
 print('record totals',[(key,sum(r[key] for r in rows.values())) for key in ['rec_n','cpu_record_us','rec_work_us']])
 print('by10idx U draw,dt,fbp',[(i,st.fmean(rows[1801+90*b+i]['draws'] for b in bs if b%4 in [0,3])) for i in range(50,65)])
