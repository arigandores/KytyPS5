import re,json,csv,statistics as S,hashlib
from pathlib import Path
from collections import defaultdict
ROOT=Path('C:/kyty/s99'); OUT=ROOT/'r6_raw'
KEYS='dt_us draws dispatches submits img_new img_free img_rec_hit img_rec_put img_up img_up_kb img_init_us img_free_us img_ins_us rec_n rec_kb texlru_n texlru_rep bf_n bf_gc_hold bf_bgc_hold bf_edge bf_xover gclk_n gclk_adv gclk_sadv fr_n fbp_n rt_att rt_kpx buf_new'.split()
token=re.compile(rb' ([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
def parse(tag):
    rows={}; gates={}
    p=ROOT/f'log_{tag}.txt'
    for ln,line in enumerate(p.open('rb'),1):
        if line.startswith(b'GateArm:'):
            d={k.decode():int(v) for k,v in token.findall(line)}; gates[d['block']]=dict(d,line=ln)
        elif line.startswith((b'FrameTrace:',b'FrameTrace-draw:',b'FrameTrace-x:')):
            d={k.decode():int(v) for k,v in token.findall(line)}; n=d['n']; row=rows.setdefault(n,{'n':n})
            typ=line.split(b':',1)[0].decode(); row[typ+'_line']=ln
            for k,v in d.items():
                if k in KEYS+['arm','blk']: row[k]=v
    for r in rows.values():
        if r.get('blk') in gates:r['idx']=r['n']-gates[r['blk']]['frame']-1
    return rows,gates
def stats(rr):
    d={k:sum(r[k] for r in rr) if all(k in r for r in rr) else None for k in KEYS}
    d.update(n0=rr[0]['n'],n1=rr[-1]['n'],line=rr[0]['FrameTrace-draw_line'])
    d['img_per_10k_draws']=d['img_new']/d['draws']*10000 if d['draws'] else None
    d['img_per_guestsecond']=d['img_new']/d['gclk_sadv']*1e9 if d['gclk_sadv'] else None
    return d
report=['# Exploratory R6 raw analysis', '', 'No changed admission, no pilot B values. All windows below are exploratory and do not rescore eng99a3.','']
allout={}
for tag in ['eng99a1','eng99a2','eng99a3']:
    rows,gates=parse(tag); blocks=defaultdict(list)
    for r in rows.values():
        if r.get('blk',-1)>=1 and 'idx' in r: blocks[r['blk']].append(r)
    falls=[]; controls=[]; rowout=[]
    for b,rr in sorted(blocks.items()):
        rr.sort(key=lambda r:r['n'])
        if gates[b]['arm']==0:
            for idx in range(3,87,3):
                win=[r for r in rr if idx<=r['idx']<idx+3]
                if len(win)==3:controls.append(dict(block=b,idx=idx,**stats(win)))
        if b-1 in gates and gates[b-1]['arm']==1 and gates[b]['arm']==0:
            win=[r for r in rr if 0<=r['idx']<3]
            if len(win)!=3:continue
            local=[w for w in controls if w['block']==b]
            prior=[w for w in controls if w['block'] in [b-3,b-4]]
            ent=dict(block=b,**stats(win),img_rows=[r['img_new'] for r in win],draw_rows=[r['draws'] for r in win],dt_rows=[r['dt_us'] for r in win],free_rows=[r['img_free'] for r in win],rec_hit_rows=[r['img_rec_hit'] for r in win],rec_put_rows=[r['img_rec_put'] for r in win])
            for name,cc in [('local',local),('prior',prior)]:
                ent[name+'_median3']=S.median(w['img_new'] for w in cc) if cc else None
                ent[name+'_per_10k_draws']=sum(w['img_new'] for w in cc)/sum(w['draws'] for w in cc)*10000 if cc else None
                ent[name+'_draw_expected']=ent['draws']*ent[name+'_per_10k_draws']/10000 if cc else None
                ent[name+'_excess']=ent['img_new']-ent[name+'_draw_expected'] if cc else None
            falls.append(ent)
            rowout.extend(dict(block=b,**r) for r in rr if r['idx']<=20)
    allout[tag]=dict(falls=falls,controls=controls)
    with (OUT/f'{tag}_fall_rows.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=sorted(set().union(*(r.keys() for r in rowout))));writer.writeheader();writer.writerows(rowout)
    report+=['## '+tag,'',f"{len(falls)} falls; raw median first2={S.median(sum(x['img_rows'][:2]) for x in falls)}; median first3={S.median(x['img_new'] for x in falls)}.",f"Clean nonoverlapping idx3..86 width3 windows: N={len(controls)}, median births={S.median(x['img_new'] for x in controls)}, mean births={S.mean(x['img_new'] for x in controls):.3f}, mean draws={S.mean(x['draws'] for x in controls):.1f}.",'','|block|raw draw line|n0|img_new rows|draws rows|dt_us rows|img_free rows|recycle hit/put sums|clean3 local median|draw-normalized local expected|excess estimate|','|---|---|---|---|---|---|---|---|---|---|---|']
    for e in falls:
        report.append(f"|{e['block']}|{e['line']}|{e['n0']}|{e['img_rows']}|{e['draw_rows']}|{e['dt_rows']}|{e['free_rows']}|{e['img_rec_hit']}/{e['img_rec_put']}|{e['local_median3']}|{e['local_draw_expected']:.2f}|{e['local_excess']:.2f}|")
    report+=['',f"Aggregate falling img/10kdraw={sum(x['img_new'] for x in falls)/sum(x['draws'] for x in falls)*10000:.3f}, clean={sum(x['img_new'] for x in controls)/sum(x['draws'] for x in controls)*10000:.3f}.",f"Falling median raw excess over local draw-normalized expectation={S.median(x['local_excess'] for x in falls):.3f} images (statistical reference; object identities not observed).",'']
    for half,ff in [('first',falls[:len(falls)//2]),('second',falls[len(falls)//2:])]:
        report+=[f"{half} half: falling median3={S.median(x['img_new'] for x in ff)}, local clean3 median={S.median(x['local_median3'] for x in ff)}, falling aggregate img/10kdraw={sum(x['img_new'] for x in ff)/sum(x['draws'] for x in ff)*10000:.3f}."]
    report+=['']
(OUT/'analysis.json').write_text(json.dumps(allout,indent=2))
(OUT/'REPORT.md').write_text('\n'.join(report))
print('\n'.join(report))
