import json, re, statistics, hashlib, sys
from pathlib import Path
from collections import defaultdict, Counter

root=Path('C:/kyty/s99'); out=root/'verify99_c_raw'
def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def audit(tag):
    raw=root/f'log_{tag}.txt'; rows=defaultdict(dict); seq=defaultdict(list); gates={}; refs={}; errors=[]; markers={}; fatal=[]
    families=(b'FrameTrace:',b'FrameTrace-draw:',b'FrameTrace-x:')
    with raw.open('rb') as f:
        for line_no,line in enumerate(f,1):
            if line.startswith((b'BindFloorCpu:', b'BindFloorGcAudit:', b'Recording:', b'ImageLife:')): markers[line.split(b':')[0].decode()]=line_no
            if any(s in line.lower() for s in (b'gpuhangabort',b'gpuwaitslow',b'gpumarkerhung',b'gpucheckpointhang',b'errordevicelost',b'std::terminate',b'abort()',b'fatal',b'unhandled exception')): fatal.append(line_no)
            if line.startswith(b'GateArm:'):
                g={k.decode():int(v) for k,v in re.findall(rb'(arm|block|frame|period|abba)=(\d+)',line)}
                b=g['block']
                if b in gates: errors.append(f'duplicate GateArm {b}')
                g['line']=line_no; gates[b]=g
            if not line.startswith(families): continue
            kind=line.split(b':')[0].decode()
            d={k.decode():int(v) for k,v in re.findall(rb'\b([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)(?=\s|$)',line)}
            n=d['n']; seq[kind].append(n); rows[n].update(d); refs.setdefault(n,{})[kind]=line_no
    first,last=min(rows),max(rows); schedule=(0,1,1,0)
    for kind in ('FrameTrace','FrameTrace-draw','FrameTrace-x'):
        if seq[kind]!=list(range(first,last+1)): errors.append(f'noncontinuous/duplicate/out-of-order {kind}')
    if list(gates)!=list(range(len(gates))): errors.append('GateArm continuity/order')
    for b,g in gates.items():
        if (g['frame'],g['arm'],g['period'],g['abba'])!=(1800+b*90,schedule[b%4],90,1): errors.append(f'GateArm identity {b}')
    for n,d in rows.items():
        b=max(0,(n-1801)//90)
        if (d['blk'],d['arm'])!=(b,schedule[b%4]): errors.append(f'row arm/block {n}')
    required='draws dt_us rt_kpx rt_att cpu_gpu_us spin_gpu_us img_new buf_new bf_edge bf_burn_ns bf_burn_cpu_ns bf_burn_cpu_n bf_burn_cpu_bad bf_burn_probe_ns bf_igc_checks bf_igc_hold bf_igc_bad bf_igc_critical bf_igc_evict'.split()
    for n,d in rows.items():
        if any(k not in d for k in required): errors.append(f'fields {n}')
        if any(v<0 for k,v in d.items() if k.startswith(('bf_','gm_'))): errors.append(f'negative counter {n}')
    complete={b for b,g in gates.items() if all(n in rows for n in range(g['frame']+1,g['frame']+91))}
    keeps={b:list(range(1861+90*b,1890+90*b)) for b in complete if 1861+90*b>=2100}
    pairs=[]; excluded={}
    for start in range(0,len(gates),4):
        if all(b in keeps for b in range(start,start+4)):
            pairs.extend([(start,start+1),(start+2,start+3)])
        else: excluded[start]=[b for b in range(start,start+4) if b not in keeps]
    chosen=sorted(b for p in pairs for b in p)
    sample=[[rows[n] for b in chosen if schedule[b%4]==a for n in keeps[b]] for a in (0,1)]
    mean=lambda a,k:statistics.fmean(d[k] for d in sample[a])
    area=lambda data:sum(d['rt_kpx'] for d in data)/sum(d['rt_att'] for d in data)
    draw=[mean(a,'draws') for a in (0,1)]; dt=[mean(a,'dt_us') for a in (0,1)]; ar=list(map(area,sample)); match=[]
    for p in pairs:
        u,a=sorted(p,key=lambda b:schedule[b%4]); au=area([rows[n] for n in keeps[u]]); aa=area([rows[n] for n in keeps[a]])
        match.append(100*(aa/au-1))
    work=100*(draw[1]/draw[0]-1); split=100*(ar[1]/ar[0]-1); c9=100*abs(dt[1]-dt[0])/dt[0]
    real_falls=[g for b,g in gates.items() if b and schedule[b%4]==0 and schedule[(b-1)%4]==1 and g['frame']+3<=last]
    totals={k:sum(d[k] for d in rows.values()) for k in rows[first] if k.startswith(('bf_','gm_'))}
    edge_rows=[(n,d['bf_edge']) for n,d in rows.items() if d['bf_edge']]
    zeros='bf_burn_cpu_bad bf_igc_bad bf_igc_critical bf_igc_evict bf_mixed bf_defer_force bf_trig_fire bf_trig_wait bf_trig_fb bf_dlskip bf_clr_skip bf_skip_drop gm_ops'.split()
    bands={'work':abs(work)<.5,'C5':abs(work)<=2,'area':abs(split)<1,'pairmatch':sum(abs(x)<=.5 for x in match)/len(match)>=.9,'C9':c9<=3,'pair_count':len(pairs)>=(30 if tag=='bf99h' else 10),'falls':len(real_falls)>=(30 if tag=='bf99h' else 8)}
    result={'tag':tag,'errors':errors,'fatal':fatal,'markers':markers,'raw_sha256':{p.name:digest(p) for p in (raw,root/f'stdout_{tag}.txt',root/f'{tag}.json')},'stream_counts':{k:len(v) for k,v in seq.items()},'n_range':[first,last],'gate_count':len(gates),'raw_duration_s':sum(d['dt_us'] for d in rows.values())/1e6,'completed_falls':len(real_falls),'edge_sum':sum(c for n,c in edge_rows),'edge_indices':dict(Counter((n-1801)%90 for n,c in edge_rows)),'pairs':pairs,'excluded_quartets':excluded,'selected_block_range':[min(chosen),max(chosen)],'selected_boundary_refs':{str(n):refs[n] for n in (keeps[min(chosen)][0],keeps[max(chosen)][-1])},'row_counts_U_A':list(map(len,sample)),'draws_U_A':draw,'work_pct':work,'area_U_A':ar,'area_pct':split,'dt_U_A_us':dt,'C9_pct':c9,'area_pair_match':[sum(abs(x)<=.5 for x in match),len(match)],'pair_area_pct':match,'strict':bands,'totals':totals,'zero_invariants':{k:totals[k]==0 for k in zeros},'min_armed_gc_hold':min(sum(rows[n]['bf_igc_hold'] for n in keeps[b]) for b in chosen if schedule[b%4]),'recovery':{f'{k}_{size}':statistics.median(sum(rows[n][k] for n in range(g['frame']+1,g['frame']+size+1)) for g in real_falls) for k in ('img_new','buf_new') for size in (2,3)},'armed_means':{k:mean(1,k) for k in ('cpu_gpu_us','spin_gpu_us','bf_burn_cpu_ns','bf_burn_ns','bf_burn_probe_ns')},'hold_attempts':json.loads((root/f'{tag}.json').read_text())['attempts']}
    if '--admitted' in sys.argv and tag=='bf99h':
        replay=json.loads((out/'replay_bf99h.json').read_text())
        assert replay['status']=='ADMITTED_SETTLED_MEASUREMENT' and not replay['errors'] and all(replay['technical'].values()) and all(replay['strict'].values())
        assert not errors and not fatal and all(bands.values()) and all(result['zero_invariants'].values())
        result['endpoints']={label:statistics.median(statistics.fmean((rows[n]['cpu_gpu_us']-rows[n]['spin_gpu_us']-rows[n][key]/1000)/1000 for n in keeps[b]) for b in chosen if schedule[b%4]) for label,key in [('B_cpu_ms','bf_burn_cpu_ns'),('B_wall_ms','bf_burn_ns')]}
    target=out/(tag+('_admitted' if '--admitted' in sys.argv else '_raw')+'.json')
    with target.open('x') as f: json.dump(result,f,indent=2); f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('pairs','totals','pair_area_pct','hold_attempts')},indent=2))
for tag in sys.argv[1:]:
    if not tag.startswith('--'): audit(tag)
