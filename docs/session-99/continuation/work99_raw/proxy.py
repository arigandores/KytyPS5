import pickle,statistics as st,math
from pathlib import Path
P=Path('C:/kyty/s99/work99_raw')
for tag in ['bf99e','eng99a4']:
 R,B=pickle.load((P/(tag+'.pkl')).open('rb'))
 for lo,hi in [(0,89),(15,88),(30,88),(60,88)]:
  g=[[R[1801+90*b+i] for b in B for i in range(lo,hi+1) if R[1801+90*b+i]['arm']==a] for a in [0,1]]
  print(tag,lo,hi,'GC checks means',[st.fmean(r['bf_igc_checks'] for r in x) for x in g], 'draws/GC calls', [sum(r['draws'] for r in x)/sum(r['bf_igc_checks'] for r in x) for x in g], 'draw/fbp U',sum(r['draws'] for r in g[0])/sum(r['fbp_n'] for r in g[0]))
 def corr(rs,x,y):
  mx=st.fmean(r[x] for r in rs);my=st.fmean(r[y] for r in rs)
  return sum((r[x]-mx)*(r[y]-my) for r in rs)/math.sqrt(sum((r[x]-mx)**2 for r in rs)*sum((r[y]-my)**2 for r in rs))
 for a in [0,1]:
  rs=[R[n] for ns in B.values() for n in ns if R[n]['arm']==a]
  print('corr draws GC dt',a,corr(rs,'draws','bf_igc_checks'),corr(rs,'draws','dt_us'))
