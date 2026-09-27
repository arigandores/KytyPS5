"""design125 rev 2 (HPP-79), section 3.4/3.7 rows: arm-0 rows of the g2_119 population, window idx 10..88 of each
block (ROADMAP s122 p.55(b)), blocks excluded as the g2_119 scorer (sh119: 3, 84, 85; mut119: 3, 84). Read-only,
draft arithmetic for [I] rows; decides nothing.  python rows125.py"""
import re,statistics,sys,collections
TOK=re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
F=['dt_us','cpu_gpu_us','spin_gpu_us','lat_us','draws','dispatches','da_wjobs','da_wdrop','da_wskip','da_wdepth','da_wlag_us','slc_total','slc_resume','bda_scan','gw_idle_ns']
def run(path, excl):
    rows={}
    with open(path,'rb') as f:
        for l in f:
            if not l.startswith(b'FrameTrace'): continue
            if not (l.startswith(b'FrameTrace: ') or l.startswith(b'FrameTrace-x: ') or l.startswith(b'FrameTrace-draw: ')): continue
            t=dict(TOK.findall(l[10:]))
            if b'n' not in t: continue
            r=rows.setdefault(int(t[b'n']),{})
            for k in F+['arm','blk']:
                kb=k.encode()
                if kb in t and k not in r: r[k]=int(t[kb])
    byblk=collections.defaultdict(list)
    for n,r in rows.items():
        if 'blk' in r and 'arm' in r: byblk[r['blk']].append(n)
    sel=[]
    for b,ns in byblk.items():
        if b in excl: continue
        ns.sort()
        for i,n in enumerate(ns):
            r=rows[n]
            if r['arm']==0 and 10<=i<=88 and all(k in r for k in F): sel.append(r)
    print(path,'rows',len(sel),'blocks',len(set(r['blk'] for r in sel)))
    def m(fn):
        v=[fn(r) for r in sel]; return statistics.fmean(v), statistics.median(v), min(v), max(v)
    for name,fn in [('dt_us',lambda r:r['dt_us']),('cpu_net',lambda r:r['cpu_gpu_us']-r['spin_gpu_us']),('busy_frac',lambda r:r['cpu_gpu_us']/r['dt_us']),
                    ('lat_us',lambda r:r['lat_us']),('wjobs',lambda r:r['da_wjobs']),('wdrop',lambda r:r['da_wdrop']),('wskip',lambda r:r['da_wskip']),
                    ('wdepth_sum',lambda r:r['da_wdepth']),('wlag_us',lambda r:r['da_wlag_us']),('slc_total',lambda r:r['slc_total']),('bda_scan',lambda r:r['bda_scan']),('gw_idle_ns',lambda r:r['gw_idle_ns'])]:
        print('  %-11s mean %.3f med %.1f min %.1f max %.1f'%((name,)+m(fn)))
    J=sum(r['da_wjobs'] for r in sel)
    print('  ratio depth/jobs %.3f  lag/jobs us %.1f'%(sum(r['da_wdepth'] for r in sel)/J, sum(r['da_wlag_us'] for r in sel)/J))
run('C:/kyty/s119/log_sh119.txt',{3,84,85})
run('C:/kyty/s119/log_mut119.txt',{3,84})
