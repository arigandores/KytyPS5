import pickle, statistics as st, random, math, sys, json
def load(tag):
    return pickle.load(open('C:/kyty/s110/audit110/%s.pkl'%tag,'rb'))
def blocks_of(rows,gates,lo=60,hi=89,first=2100):
    garm={b:a for b,a,f in gates}; gfr={b:f for b,a,f in gates}
    elig={}; mism=0
    for b in sorted(garm):
        F=gfr[b]; exp=list(range(F+1,F+91))
        if not all(n in rows and 'dt_us' in rows[n] and 'spin_gpu_us' in rows[n] for n in exp): continue
        for n in exp:
            if rows[n].get('arm')!=garm[b]: mism+=1
        kept=exp[lo:hi]
        if min(kept)<first: continue
        elig[b]=kept
    pairs=[]
    top=max(garm)
    for b in range(0,top+1,4):
        q=[b,b+1,b+2,b+3]
        if all(k in elig for k in q):
            pairs += [(b,b+1),(b+2,b+3)]
    return garm,elig,pairs,mism
def val(r,key):
    if key=='cpu_net_us': return r['cpu_gpu_us']-r['spin_gpu_us']
    return r.get(key)
def bmean(rows,ns,key):
    v=[val(rows[n],key) for n in ns]
    v=[x for x in v if x is not None]
    return sum(v)/len(v) if v else None
def pair_diffs(rows,garm,elig,pairs,key):
    d=[]
    for a,b in pairs:
        ma=bmean(rows,elig[a],key); mb=bmean(rows,elig[b],key)
        if ma is None or mb is None: continue
        # arm1 - arm0
        if garm[a]==1 and garm[b]==0: d.append(ma-mb)
        elif garm[a]==0 and garm[b]==1: d.append(mb-ma)
        else: raise Exception('pair arms %s'%((a,b),))
    return d
def summ(d, seed=1):
    n=len(d); m=sum(d)/n; sd=st.stdev(d); se=sd/math.sqrt(n)
    rnd=random.Random(seed)
    # sign-flip permutation, two-sided
    obs=abs(m); cnt=0; R=20000
    for _ in range(R):
        s=sum(x if rnd.random()<0.5 else -x for x in d)/n
        if abs(s)>=obs-1e-12: cnt+=1
    p=(cnt+1)/(R+1)
    bs=[]
    for _ in range(10000):
        smp=[d[rnd.randrange(n)] for _ in range(n)]
        bs.append(sum(smp)/n)
    bs.sort()
    return dict(n=n,mean=m,se2=2*se,t=m/se,median=st.median(d),perm_p=p,boot=(bs[250],bs[9750]))
def fmt(s):
    return 'n %d mean %.1f 2SE %.1f t %.2f med %.1f p %.4f boot95 [%.1f, %.1f]'%(s['n'],s['mean'],s['se2'],s['t'],s['median'],s['perm_p'],s['boot'][0],s['boot'][1])
if __name__=='__main__':
    for tag in sys.argv[1:]:
        rows,gates=load(tag)
        garm,elig,pairs,mism=blocks_of(rows,gates)
        print('==',tag,'blocks',len(garm),'eligible',len(elig),'pairs',len(pairs),'arm-mismatch rows',mism)
        for key in ('dt_us','cpu_net_us','gpu_busy_us','da_walk_us','da_take_us','draws','spin_gpu_us','cpu_gpu_us','cpu_main_us','semwait_us'):
            d=pair_diffs(rows,garm,elig,pairs,key)
            if len(d)<3: continue
            print('  d',key.ljust(12),fmt(summ(d)))
