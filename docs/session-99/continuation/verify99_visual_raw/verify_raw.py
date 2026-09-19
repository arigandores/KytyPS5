import collections, hashlib, json, pathlib, re
ROOT=pathlib.Path('C:/kyty/s99'); OUT=ROOT/'verify99_visual_raw'
result={}
for tag in ['vis99base','bf99e']:
    ix=[]
    for ln,line in enumerate((ROOT/f'rec_{tag}.mp4.idx').open(),1):
        a=line.split(); ix.append((int(a[0]),int(a[1]),float(a[2])))
    rows={}; gates=[]; bindvals=collections.Counter(); matches=[]; activity=collections.Counter(); activity_nonzero=collections.Counter(); fatal=[]; markers=[]; trace_x_n=[]
    log=ROOT/f'log_{tag}.txt'
    for ln,line in enumerate(log.open(errors='replace'),1):
        if line.startswith('FrameTrace: '):
            d=dict(re.findall(r'(\w+)=(-?\d+)',line)); n=int(d['n']); rows[n]={'line':ln,'arm':int(d['arm']),'blk':int(d['blk']),'dt_us':int(d['dt_us'])}
        if line.startswith('FrameTrace-x: '):
            m=re.search(r'\bn=(\d+)',line); trace_x_n.append(int(m[1]))
            for k,v in re.findall(r'\b(bf_n|bf_disp|bf_burn_ns|bf_burn_cpu_n|bf_skip|bf_reuse|bf_edge|bf_gc_hold|bf_bgc_hold|bf_clr_skip)=(-?\d+)',line):
                activity[k]+=1
                if int(v): activity_nonzero[k]+=1
        for val in re.findall(r'\bbindfloor\s*=\s*(-?\d+)',line):
            bindvals[val]+=1
            if int(val)>0: matches.append({'line':ln,'value':int(val),'text':line.strip()[:500]})
        if 'GateArm:' in line or 'GateSchedule:' in line: gates.append({'line':ln,'text':line.strip()})
        if any(s in line for s in ['GpuHangAbort','--- std::terminate ---','--- abort() ---','VK_ERROR_DEVICE_LOST','Window 1 closed','Event: quit','Recording:']): markers.append({'line':ln,'text':line.strip()})
    gaps=lambda vals:[(a,b) for a,b in zip(vals,vals[1:]) if b!=a+1]
    idx_info={'rows':len(ix),'first':ix[0],'last':ix[-1],'frame_gaps':gaps([x[0] for x in ix]),'present_gaps':gaps([x[1] for x in ix]),'time_backwards':sum(b[2]<a[2] for a,b in zip(ix,ix[1:])),'time_equal':sum(b[2]==a[2] for a,b in zip(ix,ix[1:]))}
    meta=json.loads((ROOT/f'{tag}.json').read_text())
    attempt=meta['attempts'][-1]; stable=int(attempt['stable_frame']); stableix=next((x for x in ix if x[1]==stable),None)
    info={'idx':idx_info,'attempt':attempt,'idx_stable_frame':stableix,'idx_span_after_stable_s':ix[-1][2]-stableix[2] if stableix else None,'log_lines':ln,'frame_rows':len(rows),'frame_first_last':[min(rows),max(rows)],'frame_gaps':gaps(list(rows)),'x_rows':len(trace_x_n),'x_gaps':gaps(trace_x_n),'bindfloor_occurrences':dict(bindvals),'bindfloor_positive':matches if tag=='vis99base' else len(matches),'floor_counter_rows':dict(activity),'floor_counter_nonzero':dict(activity_nonzero),'gates':gates,'markers':markers}
    reportpath=ROOT/('video99_base_full' if tag=='vis99base' else 'video99_full')/'report.json'
    if reportpath.exists():
        report=json.loads(reportpath.read_text()); ev=[]
        for event in report['events']:
            p=event['present'][0] if event['present'] else None
            ev.append(dict(event,trace=rows.get(p),idx_line=event['frame']+1))
        info['detector']={'frames':report['frames'],'events_count':len(ev),'events':ev,'event_arm_counts':dict(collections.Counter(str(e['trace']['arm']) if e['trace'] else 'missing' for e in ev))}
    result[tag]=info
(OUT/'raw_summary.json').write_text(json.dumps(result,indent=2))
for tag,r in result.items():
    print(tag,json.dumps({k:v for k,v in r.items() if k not in ['gates','markers','detector']}))
    if 'detector' in r: print('detector',r['detector']['frames'],r['detector']['events_count'],r['detector']['event_arm_counts'])
    print('gates',len(r['gates']),r['gates'][:2],r['gates'][-2:]); print('markers',r['markers'])
