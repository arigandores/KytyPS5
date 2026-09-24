import csv, statistics as st
def gpu(path):
    rows=list(csv.reader(open(path)))
    h=[x.strip() for x in rows[0]]; data=rows[1:]
    out={}
    for i,name in enumerate(h[1:],1):
        vals=[]
        for r in data:
            try: vals.append(float(r[i].strip().split()[0]))
            except: pass
        if vals: out[name]=(st.median(vals), sum(vals)/len(vals), min(vals), max(vals))
    reasons={}
    for r in data:
        k=r[-1].strip(); reasons[k]=reasons.get(k,0)+1
    return out, reasons, len(data)
def cpu(path):
    rd=list(csv.DictReader(open(path)))
    out={}
    for k in rd[0]:
        try:
            vals=[float(r[k]) for r in rd if r[k] not in ('',None)]
        except: continue
        if vals: out[k]=(st.median(vals), sum(vals)/len(vals))
    return out,len(rd)
for tag,base in (('shp110','C:/kyty/s110/'),('frm109','C:/kyty/s109/')):
    g,reas,n=gpu(base+'gpuclk_%s.csv'%tag)
    print('==',tag,'gpu samples',n)
    for k,v in g.items(): print('   %s med %.1f mean %.1f min %.1f max %.1f'%((k,)+v))
    print('   reasons', reas)
    c,n=cpu(base+'cpuclk_%s.csv'%tag)
    print('  cpu samples',n)
    for k in ('perf_all','perf_ccd0','perf_ccd1','mhz_ccd0','mhz_ccd1','busy_all','busy_ccd0','busy_ccd1','c3_ccd0','c3_ccd1','dpc_ms_ccd0','dpc_ms_ccd1','irq_ms_ccd0','irq_ms_ccd1','q_len'):
        if k in c: print('   %s med %.2f mean %.2f'%(k,c[k][0],c[k][1]))
