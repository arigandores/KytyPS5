import sys
sys.path.insert(0,'C:/kyty/s110/audit110')
from abba_stats import load, blocks_of
for tag in sys.argv[1:]:
    rows,gates=load(tag)
    garm,elig,pairs,_=blocks_of(rows,gates,lo=0,hi=90,first=1801)
    garm2,elig2,pairs2,_=blocks_of(rows,gates)
    pairs=[p for p in pairs if p in pairs2]
    used=sorted({b for p in pairs for b in p})
    gfr={b:f for b,a,f in gates}
    print('==',tag)
    # per-index paired diff, grouped by 10-frame bins, plus last 3 individually
    def diff_idx(idxs):
        tot=0;c=0
        for a,b in pairs:
            ma=sum(rows[gfr[a]+1+i]['dt_us'] for i in idxs)/len(idxs)
            mb=sum(rows[gfr[b]+1+i]['dt_us'] for i in idxs)/len(idxs)
            d = (ma-mb) if garm[a]==1 else (mb-ma)
            tot+=d;c+=1
        return tot/c
    for s in range(0,90,10):
        print('  idx %2d-%2d  d dt %.1f'%(s,s+9,diff_idx(list(range(s,s+10)))))
    for i in (0,1,2,86,87,88,89):
        print('  idx %2d  d dt %.1f'%(i,diff_idx([i])))
    # boundary kind: does block b switch from previous arm?
    for arm in (0,1):
        for i in (0,89):
            v=[rows[gfr[b]+1+i]['dt_us'] for b in used if garm[b]==arm]
            print('  arm',arm,'idx',i,'mean dt %.1f'%(sum(v)/len(v)), 'n',len(v))
