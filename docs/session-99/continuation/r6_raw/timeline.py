exec(open('C:/kyty/s99/r6_raw/analyze.py').read().split('report=')[0])
out=['# Exploratory timelines', '', 'img_new-rec_hit is shown arithmetically; semantics require source verification. fbp_n = FaultProcN, ProcessFaultBuffer calls from GC (frameStats.h:1503), NOT guest frame work. gclk_sadv is scaled clock advance over sampled reads (frameStats.h:1323), not guest frame count. No admission changes.','']
for tag in ['eng99a1','eng99a2','eng99a3']:
    rows,gates=parse(tag); blocks=defaultdict(list)
    for r in rows.values():
        if r.get('blk',-1)>=1 and 'idx' in r:blocks[r['blk']].append(r)
    falls=[b for b in sorted(blocks) if b-1 in gates and gates[b-1]['arm']==1 and gates[b]['arm']==0 and len(blocks[b])>=90]
    out+=['## '+tag,'','|idx|rows|img_new mean|free mean|rec_hit mean|rec_put mean|draws mean|dt_us mean|fbp_n mean|','|---|---|---|---|---|---|---|---|---|']
    for idx in list(range(16))+[30,60,88]:
        rr=[r for b in falls for r in blocks[b] if r['idx']==idx]
        out.append('|'+str(idx)+'|'+str(len(rr))+'|'+'|'.join(f'{S.mean(r[k] for r in rr):.3f}' for k in ['img_new','img_free','img_rec_hit','img_rec_put','draws','dt_us','fbp_n'])+'|')
    out+=['','|fall block|prior floor180 img_new/free/hit/put|fall3 img_new/free/hit/put|later U177 img_new/free/hit/put|','|---|---|---|---|']
    for b in falls:
        wins=[[r for bb in [b-2,b-1] for r in blocks.get(bb,[])],[r for r in blocks[b] if 0<=r['idx']<3],[r for bb in [b,b+1] for r in blocks.get(bb,[]) if bb>b or r['idx']>=3]]
        out.append('|'+str(b)+'|'+'|'.join('/'.join(str(sum(r[k] for r in rr)) for k in ['img_new','img_free','img_rec_hit','img_rec_put']) for rr in wins)+'|')
    for name,rr in [('fall3',[r for b in falls for r in blocks[b] if r['idx']<3]),('samearm U idx0..2',[r for b in falls if b+1 in blocks for r in blocks[b+1] if r['idx']<3]),('settled U idx60..88',[r for b in blocks if gates[b]['arm']==0 for r in blocks[b] if 60<=r['idx']<=88])]:
        d=stats(rr)
        out+=['',f"{name}: Nrows{len(rr)}, img_new/10kdraw={d['img_new']/d['draws']*1e4:.3f}, img_new/fbp={d['img_new']/d['fbp_n']:.3f}, img_new/gclk_sadv_second={d['img_new']/d['gclk_sadv']*1e9:.3f}, new minus rechit/row={(d['img_new']-d['img_rec_hit'])/len(rr):.3f}."]
    out+=['']
(OUT/'TIMELINE.md').write_text('\n'.join(out))
print('\n'.join(out))
