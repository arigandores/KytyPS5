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
    for arm in (0,1):
        hl=[]; one=[0]*9; cnt=[0]*9
        for b in used:
            if garm[b]!=arm: continue
            for i in range(90):
                n=gfr[b]+1+i; dt=rows[n]['dt_us']
                if dt>41700: hl.append((b,i,dt))
                one[i//10]+= dt<25000; cnt[i//10]+=1
        print(' arm',arm,'hitches(>41.7ms)',len(hl),'in tail[60:89]',sum(1 for x in hl if 60<=x[1]<89))
        print('   hitch list', [(b,i,round(dt/1000,1)) for b,i,dt in hl][:60])
        print('   1-vblank share by bin', ['%.1f'%(100*o/c) for o,c in zip(one,cnt)])
