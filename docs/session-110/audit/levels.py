import sys
sys.path.insert(0,'C:/kyty/s110/audit110')
from abba_stats import load, blocks_of, val, pair_diffs, summ, fmt
keys=('dt_us','cpu_net_us','cpu_gpu_us','spin_gpu_us','gpu_busy_us','draws','dispatches','cpu_main_us','semwait_us','da_walk_us','da_take_us','da_queue_us','da_hit','da_miss','rec_n','sync_ups','sync_up_kb','prot_us','rp_begin','cspfree_hit','cspf_have','cspf_new','cs_sync_new','cs_sync_wait','da_wlag_us','fault_us','faults_main','img_up_kb','srt_miss')
L={}
for tag in sys.argv[1:]:
    rows,gates=load(tag)
    garm,elig,pairs,_=blocks_of(rows,gates,lo=0,hi=90,first=1801)
    garm2,elig2,pairs2,_=blocks_of(rows,gates)
    pairs=[p for p in pairs if p in pairs2]
    used=sorted({b for p in pairs for b in p})
    L[tag]={}
    for arm in (0,1):
        ns=[n for b in used if garm[b]==arm for n in elig[b]]
        L[tag][arm]={}
        for k in keys:
            v=[val(rows[n],k) for n in ns]; v=[x for x in v if x is not None]
            L[tag][arm][k]=sum(v)/len(v) if v else None
    L[tag]['d']={}
    for k in keys:
        d=pair_diffs(rows,garm,elig,pairs,k)
        if len(d)>2:
            import statistics as _s, math as _m
            m=sum(d)/len(d); sd=_s.stdev(d); L[tag]["d"][k]=(m, m/(sd/_m.sqrt(len(d))) if sd>0 else 0.0)
tags=sys.argv[1:]
print('key'.ljust(14),''.join(('%s a0'%t).rjust(12)+('%s a1'%t).rjust(12)+'   d(t)'.rjust(16) for t in tags))
for k in keys:
    line=k.ljust(14)
    for t in tags:
        a0=L[t][0][k]; a1=L[t][1][k]; d=L[t]['d'].get(k)
        line+=('%12.1f'%a0 if a0 is not None else ' '*12)+('%12.1f'%a1 if a1 is not None else ' '*12)+(('%9.1f(%5.2f)'%d) if d else ' '*16)
    print(line)
