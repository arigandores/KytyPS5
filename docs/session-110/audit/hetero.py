import sys, math, statistics as st
sys.path.insert(0,'C:/kyty/s110/audit110')
from abba_stats import load, blocks_of, summ, fmt
res={}
for tag in sys.argv[1:]:
    rows,gates=load(tag)
    garm,elig,pairs,_=blocks_of(rows,gates,lo=0,hi=90,first=1801)
    garm2,elig2,pairs2,_=blocks_of(rows,gates)
    pairs=[p for p in pairs if p in pairs2]
    gfr={b:f for b,a,f in gates}
    def d(a,b,idxs,key='dt_us'):
        ma=sum(rows[gfr[a]+1+i][key] for i in idxs)/len(idxs)
        mb=sum(rows[gfr[b]+1+i][key] for i in idxs)/len(idxs)
        return (ma-mb) if garm[a]==1 else (mb-ma)
    tail=list(range(60,89)); rest=list(range(0,60)); full=list(range(90))
    dd=[d(a,b,tail)-d(a,b,rest) for a,b in pairs]
    print(tag,'tail-minus-rest', fmt(summ(dd)))
    res[tag]=[d(a,b,full) for a,b in pairs]
    # vblank-share decomposition (full block)
a=res.get('shp110'); b=res.get('frm109')
if a and b:
    ma=sum(a)/len(a); mb=sum(b)/len(b); se=math.sqrt(st.variance(a)/len(a)+st.variance(b)/len(b))
    print('full-block shp110 %.1f frm109 %.1f diff %.1f SE %.1f z %.2f pooled %.1f'%(ma,mb,ma-mb,se,(ma-mb)/se,(ma+mb)/2))
    pooled=a+b
    print('pooled full-block', fmt(summ(pooled)))
