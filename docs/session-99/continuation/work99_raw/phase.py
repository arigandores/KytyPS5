import pickle,statistics as st,math,json
from pathlib import Path
P=Path('C:/kyty/s99/work99_raw')
for tag in ['bf99e','eng99a4']:
 R,B=pickle.load((P/(tag+'.pkl')).open('rb'));Q=[]
 for q in range(min(B),max(B)+1,4):
  means=[st.fmean(R[n]['draws'] for b in range(q,q+4) for n in B[b] if R[n]['arm']==a) for a in [0,1]];Q.append(means[1]-means[0])
 print(tag,'quartet draw delta mean sd se min max neg',st.fmean(Q),st.stdev(Q),st.stdev(Q)/math.sqrt(len(Q)),min(Q),max(Q),sum(x<0 for x in Q),len(Q))
 print('first_quartets',Q[:12])
 # coefficients for fixed global n modulo distribution; actual U/A phase fractions identical when m divides4*90
 for m in [2,3,4,5,6]:
  g=[[R[n] for ns in B.values() for n in ns if R[n]['arm']==a] for a in [0,1]]
  probs=[[sum(r['n']%m==i for r in x)/len(x) for i in range(m)] for x in g]
  print('phasepop',m,probs)
 print('record first300 and total rows <10draw by U A',[[sum(r['draws']<10 for r in R.values() if r['n']>=2100 and r['arm']==a and (lim is None or r['time']-R[1801]['time']<lim)) for a in [0,1]] for lim in [300,None]])
 print('example around3682', [{k:R[n][k] for k in ['n','draws','dt_us','arm','blk','fbp_n','line']} for n in range(3679,3688)])
