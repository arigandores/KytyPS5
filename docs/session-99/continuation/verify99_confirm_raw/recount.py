import json, re, hashlib, statistics as st, sys
from pathlib import Path
from collections import Counter
ROOT=Path('C:/kyty/s99'); OUT=ROOT/'verify99_confirm_raw'
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def recount(tag):
    path=ROOT/f'log_{tag}.txt'; meta=json.loads((ROOT/f'{tag}.json').read_text())
    rows={}; stream={k:[] for k in ('FrameTrace','FrameTrace-draw','FrameTrace-x')}; refs={}; gates=[]; fatal=[]; markers={}
    keys=set('n arm blk dt_us draws cpu_gpu_us spin_gpu_us rt_kpx rt_att img_new buf_new mh_emit_us d_emit'.split())
    with path.open('rb') as f:
        for ln,line in enumerate(f,1):
            if any(t in line.lower() for t in (b'gpuhangabort',b'gpuwaitslow',b'gpumarkerhung',b'gpucheckpointhang',b'errordevicelost',b'std::terminate',b'abort()',b'fatal',b'unhandled exception')): fatal.append(ln)
            if line.startswith((b'BindFloorCpu:',b'BindFloorGcAudit:',b'Recording:',b'ImageLife:')): markers[line.split(b':')[0].decode()]=ln
            kind=line.split(b':',1)[0].decode(errors='replace')
            if kind=='GateArm':
                d={k.decode():int(v) for k,v in re.findall(rb'(arm|arms|block|frame|period|abba)=(\d+)',line)}
                d['line']=ln; gates.append(d)
            if kind not in stream: continue
            vals={}
            for token in line.split()[1:]:
                if b'=' not in token: continue
                kb,v=token.split(b'=',1); k=kb.decode()
                if k in keys or k.startswith(('bf_','gm_','pl_','be_')):
                    vals[k]=int(v)
            n=vals['n']; stream[kind].append(n); refs.setdefault(n,{})[kind]=ln
            row=rows.setdefault(n,{}); row.update(vals)
    ns=sorted(rows); last=ns[-1]; errs=[]
    for kind, seq in stream.items():
        if seq!=list(range(ns[0],last+1)): errs.append('stream continuity/duplicates/order '+kind)
    for b,g in enumerate(gates):
        if (g['block'],g['frame'],g['period'],g['abba'],g['arm']) != (b,1800+90*b,90,1,[0,1,1,0][b%4]): errs.append('GateArm '+str(b))
    for n,r in rows.items():
        b=max(0,(n-1801)//90)
        if r['blk']!=b or r['arm']!=[0,1,1,0][b%4]: errs.append('row identity '+str(n))
    eligible={}; rejected={}
    for g in gates:
        b=g['block']; frame=g['frame']; full=list(range(frame+1,frame+91)); keep=full[60:89]
        if any(n not in rows for n in full): rejected[b]='incomplete'
        elif min(keep)<2100: rejected[b]='initial'
        else: eligible[b]=keep
    pairs=[]
    for b in range(0,len(gates),4):
        if all(j in eligible for j in range(b,b+4)): pairs.extend([(b,b+1),(b+2,b+3)])
    chosen={b:eligible[b] for p in pairs for b in p}; groups=[[rows[n] for b,nn in chosen.items() for n in nn if rows[n]['arm']==a] for a in (0,1)]
    area=lambda g:sum(r['rt_kpx'] for r in g)/sum(r['rt_att'] for r in g)
    means=lambda k:[st.fmean(r[k] for r in g) for g in groups]
    draws=means('draws'); dt=means('dt_us'); areas=[area(g) for g in groups]
    deltas=[]
    for l,r in pairs:
        base,armed=(l,r) if [0,1,1,0][l%4]==0 else (r,l)
        deltas.append(100*(area([rows[n] for n in chosen[armed]])/area([rows[n] for n in chosen[base]])-1))
    totals={k:sum(r[k] for r in rows.values()) for k in rows[ns[0]] if k.startswith(('bf_','gm_','be_'))}
    falls=[g for g in gates[1:] if g['arm']==0 and gates[g['block']-1]['arm']==1 and g['frame']+3<=last]
    label_falls=len(falls)
    if tag=='aa99plain': falls=[]
    edges=[n for n,r in rows.items() if r['bf_edge']]
    m={'draws_U_A':draws,'work_pct':100*(draws[1]/draws[0]-1),'area_U_A':areas,'area_pct':100*(areas[1]/areas[0]-1),'dt_U_A_us':dt,'dt_pct':100*abs(dt[1]-dt[0])/dt[0],'match':[sum(abs(x)<=.5 for x in deltas),len(deltas)],'pairs':len(pairs),'rows_per_arm':[len(g) for g in groups]}
    strict=abs(m['work_pct'])<.5 and abs(m['area_pct'])<1 and m['dt_pct']<=3 and m['match'][0]/m['match'][1]>=.9
    out={'tag':tag,'strict':strict,'errors':errs,'fatal_log_lines':fatal,'markers':markers,'raw_sha256':{p.name:sha(p) for p in [path,ROOT/f'{tag}.json',ROOT/f'stdout_{tag}.txt']},'range':[ns[0],last],'stream_counts':{k:len(v) for k,v in stream.items()},'gates':len(gates),'falls':len(falls),'edge_total':sum(rows[n]['bf_edge'] for n in edges),'edge_indices':dict(Counter((n-1801)%90 for n in edges)),'metrics':m,'totals':totals,'pairs':pairs,'blocks_range':[min(chosen),max(chosen)],'rejected':rejected,'retained_boundary_refs':{n:refs[n] for n in [min(chosen[min(chosen)]),max(chosen[max(chosen)])]},'raw_duration_s':sum(r['dt_us'] for r in rows.values())/1e6,'hold_attempt':meta['attempts'],'min_armed_gc_hold':min((sum(rows[n]['bf_igc_hold'] for n in nn) for b,nn in chosen.items() if [0,1,1,0][b%4]==1),default=0)}
    out['armed_burn']={k:st.fmean(r[k] for r in groups[1]) for k in ('bf_burn_cpu_ns','bf_burn_ns','bf_burn_probe_ns','cpu_gpu_us')}
    out['recovery']={k+str(count):st.median(sum(rows[n][k] for n in range(g['frame']+1,g['frame']+count+1)) for g in falls) if falls else None for k in ('img_new','buf_new') for count in (2,3)}
    out['zero_checks']={k:totals[k]==0 for k in ('bf_burn_cpu_bad','bf_igc_bad','bf_igc_critical','bf_igc_evict','bf_mixed','bf_defer_force','bf_trig_fire','bf_trig_wait','bf_trig_fb','bf_dlskip','bf_clr_skip','bf_skip_drop','gm_ops')}
    # Endpoint extraction only after independent admission flag from completed technical review.
    if '--admitted' in sys.argv and tag=='bf99g' and strict and not errs and not fatal and len(falls)>=30 and len(pairs)>=30:
        out['endpoints']={clock:st.median(st.fmean((rows[n]['cpu_gpu_us']-rows[n]['spin_gpu_us']-rows[n][burn]/1000)/1000 for n in nn) for b,nn in chosen.items() if [0,1,1,0][b%4]==1) for clock,burn in [('B_cpu_ms','bf_burn_cpu_ns'),('B_wall_ms','bf_burn_ns')]}
    (OUT/f'{tag}_independent.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('totals','pairs','raw_sha256','hold_attempt')},indent=2))
for tag in [a for a in sys.argv[1:] if not a.startswith('--')]: recount(tag)
