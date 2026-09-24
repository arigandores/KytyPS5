import sys, math, statistics as st
sys.path.insert(0,'C:/kyty/s110/audit110')
from abba_stats import load, blocks_of
print('run      sealed[60:89] (2SE)     full[0:90] (2SE)    capped-sealed   gap(sealed-full) z_within')
for tag in sys.argv[1:]:
    rows,gates=load(tag)
    garm,elig,pairs,_=blocks_of(rows,gates,lo=0,hi=90,first=1801)
    garm2,elig2,pairs2,_=blocks_of(rows,gates)
    pairs=[p for p in pairs if p in pairs2]
    gfr={b:f for b,a,f in gates}
    def d(a,b,idxs,cap=False):
        f=lambda x: min(x,34500) if cap else x
        ma=sum(f(rows[gfr[a]+1+i]['dt_us']) for i in idxs)/len(idxs); mb=sum(f(rows[gfr[b]+1+i]['dt_us']) for i in idxs)/len(idxs)
        return (ma-mb) if garm[a]==1 else (mb-ma)
    S=[d(a,b,range(60,89)) for a,b in pairs]; F=[d(a,b,range(90)) for a,b in pairs]; C=[d(a,b,range(60,89),True) for a,b in pairs]
    G=[s-f for s,f in zip(S,F)]
    ms=lambda v:(sum(v)/len(v), 2*st.stdev(v)/math.sqrt(len(v)))
    s,f,c,g=ms(S),ms(F),ms(C),ms(G)
    print('%-7s %4d %8.1f (%5.1f)   %8.1f (%5.1f)   %8.1f (%5.1f)  %8.1f  %5.2f'%(tag,len(pairs),s[0],s[1],f[0],f[1],c[0],c[1],g[0],g[0]/(g[1]/2)))
