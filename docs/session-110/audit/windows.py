import sys
sys.path.insert(0,'C:/kyty/s110/audit110')
from abba_stats import load, blocks_of, pair_diffs, summ, fmt
for tag in sys.argv[1:]:
    rows,gates=load(tag)
    print('==',tag)
    for lo,hi in ((60,89),(0,90),(10,90),(30,90),(0,30),(30,60),(60,90),(45,90)):
        garm,elig,pairs,mism=blocks_of(rows,gates,lo=lo,hi=hi,first=1801 if lo<60 else 2100)
        # keep the same pair set as sealed: require block start>=2100-60 => same blocks
        garm2,elig2,pairs2,_=blocks_of(rows,gates)
        pairs=[p for p in pairs if p in pairs2]
        for key in ('dt_us','cpu_net_us'):
            d=pair_diffs(rows,garm,elig,pairs,key)
            print('  [%d:%d]'%(lo,hi), key.ljust(10), fmt(summ(d)))
    # split halves (sealed window)
    garm,elig,pairs,_=blocks_of(rows,gates)
    d=pair_diffs(rows,garm,elig,pairs,'dt_us')
    h=len(d)//2
    print('  first half ',fmt(summ(d[:h])))
    print('  second half',fmt(summ(d[h:])))
    q=len(d)//4
    for i in range(4): print('  quarter',i,fmt(summ(d[i*q:(i+1)*q])))
