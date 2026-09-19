import re,json,csv,hashlib,bisect,statistics as S
from pathlib import Path
from collections import Counter,defaultdict
R=Path('C:/kyty/s99');O=R/'r6_raw/life_analysis';P=R/'log_life99a.txt'
kv=re.compile(r'(\w+)=([^\s]+)'); sigkeys='guest bytes w h d mips layers fmt tile pitch bpp'.split()
events=[];rows={};gates={};lastfree={};seen=Counter();live=Counter();seenaddr=Counter();lastaddr={};h=hashlib.sha256()
for ln,raw in enumerate(P.open('rb'),1):
 h.update(raw)
 if raw.startswith(b'ImageLife:'):
  d=dict(kv.findall(raw.decode()));d={k:(v if k in ['event','reason'] else int(v,0)) for k,v in d.items()};d['logline']=ln
  d['reported_reason']=d['reason']
  if d['event']=='free' and d['reason']=='operator()' and d['line']==3402:d['reason']='RunGarbageCollector'
  sig=tuple(d[k] for k in sigkeys);d['signature']='|'.join(str(x) for x in sig)
  if d['event']=='create':
   d['prior_seen']=seen[sig];d['prior_live']=live[sig];prev=lastfree.get(sig)
   d['address_seen']=seenaddr[d['guest']]
   if d['guest'] in lastaddr:d['previous_address_signature']=lastaddr[d['guest']]
   if not seen[sig]:cause='first_observed_signature'
   elif live[sig]>0:cause='ambiguous_live_signature'
   elif prev:cause='prior_free_'+prev['reason']
   else:cause='ambiguous_no_prior_free'
   if prev:d.update(prior_free_frame=prev['frame'],prior_free_line=prev['logline'],prior_free_reason=prev['reason'])
   d['candidate_cause']=cause;d['class']='undefined_bookkeeping' if d['fmt']==0 else cause
   seen[sig]+=1;live[sig]+=1;seenaddr[d['guest']]+=1;lastaddr[d['guest']]=d['signature']
  else:
   d['prior_live']=live[sig];live[sig]-=1;lastfree[sig]=d
  events.append(d)
 elif raw.startswith((b'FrameTrace:',b'FrameTrace-draw:',b'FrameTrace-x:')):
  d={k:int(v) for k,v in re.findall(rb' (\w+)=(-?\d+)',raw)};d={k.decode():v for k,v in d.items()};n=d['n'];r=rows.setdefault(n,{'n':n});r.update({k:d[k] for k in ['img_new','img_free','draws','dt_us','blk','arm','bf_gc_hold'] if k in d});r[raw.split(b':')[0].decode()+'_line']=ln
 elif raw.startswith(b'GateArm:'):
  d={k.decode():int(v) for k,v in re.findall(rb' (\w+)=(-?\d+)',raw)};gates[d['block']]=d
starts=sorted((g['frame'],b) for b,g in gates.items());startnums=[x[0] for x in starts]
def phase(frame):
 i=bisect.bisect_right(startnums,frame)-1
 if i<0:return 'pregate',None,None
 b=starts[i][1];idx=frame-gates[b]['frame'];arm=gates[b]['arm']
 # +/-1 boundary allowance: only idx2..87 is called definitely interior.
 return ('armed_interior' if arm==1 and 2<=idx<=87 else 'armed_boundary' if arm==1 else 'unarmed'),b,idx
for e in events:
 e['phase'],e['block'],e['event_idx']=phase(e['frame'])
 if 'prior_free_frame'in e:e['prior_free_phase'],e['prior_free_block'],_=phase(e['prior_free_frame'])
 if e['event']=='create' and e['candidate_cause']=='prior_free_RunGarbageCollector':e['gc_candidate_phase']=e['prior_free_phase']
blocks=defaultdict(list)
for n,r in rows.items():
 b=r.get('blk')
 if b in gates:r['idx']=n-gates[b]['frame']-1;blocks[b].append(r)
fallblocks=[b for b in sorted(gates) if b-1 in gates and gates[b]['arm']==0 and gates[b-1]['arm']==1]
byframe=defaultdict(list)
for e in events:byframe[e['frame']].append(e)
def window(b,idxs,shift=0):
 rr=[r for r in blocks.get(b,[]) if r['idx'] in idxs];ns={r['n'] for r in rr};ee=[e for n in ns for e in byframe[n+shift]]
 cc=[e for e in ee if e['event']=='create'];ff=[e for e in ee if e['event']=='free']
 return dict(block=b,rows=len(rr),n=[r['n'] for r in rr],img_new=sum(r['img_new'] for r in rr),img_free=sum(r['img_free'] for r in rr),event_creates=len(cc),event_frees=len(ff),classes=dict(Counter(e['class'] for e in cc)),candidate_causes=dict(Counter(e['candidate_cause'] for e in cc)),gc_prior_phases=dict(Counter(e.get('gc_candidate_phase') for e in cc if 'gc_candidate_phase'in e)),free_reasons=dict(Counter(e['reason'] for e in ff)),event_lines=[e['logline'] for e in cc],creates=cc)
windows=[]
for b in fallblocks:
 for shift in [-1,0,1]:
  for kind,bb in [('fall',b),('sameU',b+1)]:windows.append(dict(kind=kind,shift=shift,**window(bb,range(3),shift)))
profiles=[]
for b in fallblocks:
 for kind,bb in [('fall',b),('sameU',b+1)]:
  for idx in list(range(31))+list(range(60,89)):
   w=window(bb,[idx]);w.pop('creates');profiles.append(dict(kind=kind,idx=idx,**w))
creates=[e for e in events if e['event']=='create'];frees=[e for e in events if e['event']=='free']
summary=dict(raw_sha256=h.hexdigest(),events=len(events),creates=len(creates),frees=len(frees),rows=len(rows),row_img_new=sum(r.get('img_new',0) for r in rows.values()),row_img_free=sum(r.get('img_free',0) for r in rows.values()),free_reasons=dict(Counter(e['reason'] for e in frees)),create_classes=dict(Counter(e['class'] for e in creates)),create_candidate_causes=dict(Counter(e['candidate_cause'] for e in creates)),free_phases=dict(Counter(e['phase'] for e in frees)),gc_frees_by_phase=dict(Counter(e['phase'] for e in frees if e['reason']=='RunGarbageCollector')),negative_live_signatures=sum(v<0 for v in live.values()))
firstline=min(r['FrameTrace-draw_line'] for r in rows.values() if 'FrameTrace-draw_line'in r);lastline=max(r['FrameTrace-draw_line'] for r in rows.values() if 'FrameTrace-draw_line'in r)
summary['create_boundary_counts']=dict(before_first_draw=sum(e['logline']<firstline for e in creates),after_last_draw=sum(e['logline']>lastline for e in creates),first_row=min(rows),last_row=max(rows))
(O/'summary.json').write_text(json.dumps(summary,indent=2));(O/'windows.json').write_text(json.dumps(windows,indent=2));(O/'profiles.json').write_text(json.dumps(profiles,indent=2))
with (O/'events.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=sorted(set().union(*(e.keys() for e in events))));w.writeheader();w.writerows(events)
text=['# Image lifetime diagnostic — fixed exploratory analysis','', 'Printed-signature matches are candidates, not proven object identity: ImageID/samples/full mip layouts are absent. Nominal mapping uses event.frame = row.n. Shifts -1,0,+1 are all printed, never selected for admission. No B or admission computed. Source correction: reported reason=operator(),line=3402 is the GC lambda, mapped to RunGarbageCollector; original reported_reason is preserved.','', '## Global coverage', '',json.dumps(summary,indent=2),'','## Every fixed first3 window','', '|kind|block|shift|rows|img_new|event creates|event frees|classifications|prior GC phase|','|---|---|---|---|---|---|---|---|---|']
for w in windows:text.append('|'+ '|'.join(str(w[k]) for k in ['kind','block','shift','rows','img_new','event_creates','event_frees','classes','gc_prior_phases'])+'|')
text+=['','## Aggregate fixed first3 windows','']
for shift in [-1,0,1]:
 for kind in ['fall','sameU']:
  ww=[w for w in windows if w['kind']==kind and w['shift']==shift];cc=[e for w in ww for e in w['creates']]
  text +=[f'{kind}, shift{shift}: windows={len(ww)}, rows={sum(w["rows"] for w in ww)}, img_new={sum(w["img_new"] for w in ww)}, event creates={len(cc)}, classes={dict(Counter(e["class"] for e in cc))}, candidates={dict(Counter(e["candidate_cause"] for e in cc))}, GC prior phases={dict(Counter(e.get("gc_candidate_phase") for e in cc if "gc_candidate_phase"in e))}.','']
text+=['## Nominal per-index profile (all falls; following same-U controls)','', '|kind|idx|Nrows|img_new|create events|classes|free reasons|','|---|---|---|---|---|---|---|']
for kind in ['fall','sameU']:
 for idx in list(range(31))+list(range(60,89)):
  pp=[p for p in profiles if p['kind']==kind and p['idx']==idx];c=Counter();fr=Counter()
  for p in pp:c.update(p['classes']);fr.update(p['free_reasons'])
  text.append(f'|{kind}|{idx}|{sum(p["rows"] for p in pp)}|{sum(p["img_new"] for p in pp)}|{sum(p["event_creates"] for p in pp)}|{dict(c)}|{dict(fr)}|')
(O/'REPORT.md').write_text('\n'.join(text));print(json.dumps(summary,indent=2));print('\n'.join(x for x in text if x.startswith(('fall,','sameU,'))))
