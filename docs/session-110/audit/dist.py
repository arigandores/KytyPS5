import pickle, statistics as st, math, sys
sys.path.insert(0,'C:/kyty/s110/audit110')
from abba_stats import load, blocks_of, val
def vb(dt):
    return int(round(dt/16667.0))
for tag in sys.argv[1:]:
    rows,gates=load(tag)
    garm,elig,pairs,mism=blocks_of(rows,gates)
    used=sorted({b for p in pairs for b in p})
    print('==',tag)
    for arm in (0,1):
        ns=[n for b in used if garm[b]==arm for n in elig[b]]
        dts=[rows[n]['dt_us'] for n in ns]
        h={}
        for d in dts: h[vb(d)]=h.get(vb(d),0)+1
        tot=len(dts)
        cn=[val(rows[n],'cpu_net_us') for n in ns]
        gb=[rows[n]['gpu_busy_us'] for n in ns]
        print('  arm',arm,'frames',tot,'mean dt %.1f'%(sum(dts)/tot),'median dt',st.median(dts),
              ' vblank hist', {k:'%.2f%%'%(100*v/tot) for k,v in sorted(h.items())},
              ' cpu_net mean %.1f med %.1f p90 %.1f'%(sum(cn)/tot, st.median(cn), sorted(cn)[int(.9*tot)]),
              ' gpu_busy %.1f'%(sum(gb)/tot))
    # all frames (incl. non-kept) after 2100
    for arm in (0,1):
        ns=[n for n in rows if n>2100 and rows[n].get('arm')==arm and 'dt_us' in rows[n]]
        dts=[rows[n]['dt_us'] for n in ns]
        h={}
        for d in dts: h[vb(d)]=h.get(vb(d),0)+1
        tot=len(dts)
        print('  ALLROWS arm',arm,'frames',tot,'mean dt %.1f'%(sum(dts)/tot),{k:'%.2f%%'%(100*v/tot) for k,v in sorted(h.items())})
