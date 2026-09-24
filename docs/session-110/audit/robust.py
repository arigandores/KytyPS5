import sys
sys.path.insert(0,'C:/kyty/s110/audit110')
from abba_stats import load, blocks_of, summ, fmt
for tag in sys.argv[1:]:
    rows,gates=load(tag)
    garm,elig,pairs,_=blocks_of(rows,gates,lo=0,hi=90,first=1801)
    garm2,elig2,pairs2,_=blocks_of(rows,gates)
    pairs=[p for p in pairs if p in pairs2]
    gfr={b:f for b,a,f in gates}
    def m(b,idxs,cap):
        v=[rows[gfr[b]+1+i]['dt_us'] for i in idxs]
        if cap: v=[min(x,34500) for x in v]
        return sum(v)/len(v)
    def d(a,b,idxs,cap):
        return (m(a,idxs,cap)-m(b,idxs,cap)) if garm[a]==1 else (m(b,idxs,cap)-m(a,idxs,cap))
    tail=list(range(60,89)); rest=list(range(0,60)); full=list(range(90))
    for cap in (False,True):
        print(tag,'cap3vbl' if cap else 'raw   ','sealed',fmt(summ([d(a,b,tail,cap) for a,b in pairs])))
        print(tag,'cap3vbl' if cap else 'raw   ','full  ',fmt(summ([d(a,b,full,cap) for a,b in pairs])))
        print(tag,'cap3vbl' if cap else 'raw   ','tail-rest',fmt(summ([d(a,b,tail,cap)-d(a,b,rest,cap) for a,b in pairs])))
