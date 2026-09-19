import sys, re, json, hashlib, statistics as S
from pathlib import Path
from collections import defaultdict, Counter
sys.dont_write_bytecode=True
root=Path('C:/kyty/s99'); out=root/'verify_cal99a'
sys.path.insert(0,str(root))
import bf99 as B
log=root/'log_cal99a.txt'; meta=json.loads((root/'cal99a.json').read_text())
hashes={str(p):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [log,root/'stdout_cal99a.txt',root/'cal99a.json',root/'gates_base.txt',B.PRED,root/'kyty_emulator_s99.exe']}
rows={}; refs={}; gates={}; gate_refs={}; duplicates=[]
for lineno,line in enumerate(log.open('rb'),1):
 if line.startswith(b'GateArm:'):
  d={k.decode():int(v) for k,v in re.findall(rb'(\w+)=(-?\d+)',line)}
  gates[d['block']]=d['arm']; gate_refs[d['block']]=lineno
 if line.startswith((b'FrameTrace:',b'FrameTrace-x:',b'FrameTrace-draw:')):
  d={k.decode():int(v) for k,v in re.findall(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)',line)}
  n=d.pop('n'); r=rows.setdefault(n,{})
  if line.startswith(b'FrameTrace:'): refs[n]=lineno
  for k,v in d.items():
   if k in r: duplicates.append((n,k))
   r[k]=v
blocks=defaultdict(list)
for n in sorted(rows): blocks[rows[n]['blk']].append(n)
edges=[b for b in gates if b-1 in gates and gates[b]!=gates[b-1]]
trim=set();hist=Counter(); edge_bad=[]
for b in edges:
 w=[('last-old',blocks[b-1][-1])]+[(f'idx{i}',n) for i,n in enumerate(blocks[b][:2])]
 trim.update(n for _,n in w)
 loc=[label for label,n in w if rows[n]['bf_edge']]
 hist.update(loc)
 if sum(rows[n]['bf_edge'] for _,n in w)!=1: edge_bad.append(b)
outside=[n for n,r in rows.items() if n not in trim and r['bf_edge']]
fall=[b for b in edges if gates[b]==0 and len(blocks[b])>=2]
window=[n for n in sorted(rows) if n>=2100 and rows[n]['blk']>=1]
ua=[[n for n in window if rows[n]['arm']==arm] for arm in (0,1)]
keep=[[n for n in ns if n not in trim] for ns in ua]
mean=lambda ns,k:S.fmean(rows[n][k] for n in ns)
dt=[mean(ns,'dt_us') for ns in keep]
draws=[mean(ns,'draws') for ns in ua]
area=[sum(rows[n]['rt_kpx'] for n in ns)/sum(rows[n]['rt_att'] for n in ns) for ns in ua]
split=(area[1]/area[0]-1)*100;work=(draws[1]/draws[0]-1)*100
wb=sorted({rows[n]['blk'] for n in window});pairs=[];apairs=[];unpaired=set(wb)
for a,b in zip(wb,wb[1:]):
 if b!=a+1 or gates[a]==gates[b]:continue
 x=[n for n in blocks[a] if n in window];y=[n for n in blocks[b] if n in window]
 if any(n not in trim for n in x) and any(n not in trim for n in y):pairs.append((a,b));unpaired.difference_update((a,b))
 if min(len(x),len(y))>=8:
  x,y=(x,y) if gates[a]==0 else (y,x)
  f=lambda ns:sum(rows[n]['rt_kpx'] for n in ns)/sum(rows[n]['rt_att'] for n in ns)
  apairs.append((f(y)/f(x)-1)*100)
matched=sum(abs(x)<=.5 for x in apairs)
live={str(arm):{k:sum(rows[n][k] for n in keep[arm]) for k in B.LIVE+('bf_mat','bf_reuse','bf_n','bf_burn_ns')} for arm in (0,1)}
recovery={k:S.median(sum(rows[n][k] for n in blocks[b][:count]) for b in fall) for k,count in [('img_new',2),('buf_new',2)]}
protocol,arms=B.protocol(meta,log,'a',calibration=True)
checks=B.controls(rows,arms,'a')
rc,ex=B.invoke(B.AS,['area_series.py','cal99a','--root',str(root),'--out',str(out/'area_cal99a.csv')])
rc2,av=B.invoke(B.AV,['area_verdict.py','cal99a','--first-frame','2100','--csv-root',str(out)])
(out/'area.txt').write_text(ex+av,encoding='utf-8')
B.fresh_area=lambda tag,root:ex+av
legacy,inherited,criterion=B.legacy('cal99a',root)
# Preserve original control FAIL lines, suppress all architecture/numeric floor sections.
(out/'legacy_controls.txt').write_text('\n'.join(l for l in legacy.splitlines() if re.search(r'\bC(?:\d|RITERION)|\b(?:PASS|FAIL)\b',l) and not any(x in l for x in ('F_st','VERDICT','CLOSED','PROCEED'))),encoding='utf-8')
rv,rvchecks=B.reversibility('cal99a',root);(out/'rv.txt').write_text(rv,encoding='utf-8')
c=dict(checks['checks']);c.pop("C9''_B",None);c.update({'inherited C'+k:v for k,v in inherited.items()});c.update({'R'+k:v for k,v in rvchecks.items()});c['criterion3']=criterion=='VALID'
ind={'raw_frames':len(rows),'first':min(rows),'last':max(rows),'duplicates':duplicates,'window_rows':[len(ns) for ns in ua],'retained_rows':[len(ns) for ns in keep], 'dt_U':dt[0],'dt_A':dt[1],'candidate_b':12000+B.round_100(dt[0]-dt[1]),'draw_means':draws,'C5':abs(draws[1]/draws[0]-1),'areas':area,'area_split_pct':split,'work_pct':work,'area_pairs':len(apairs),'area_matched':matched,'criterion3_independent':abs(split)<1 and abs(work)<.5 and matched/len(apairs)>=.9,'matched_pairs':len(pairs),'unpaired_blocks':sorted(unpaired),'gate_blocks':[min(gates),max(gates)],'edges':len(edges),'completed_falling':len(fall),'edge_hist':dict(hist),'edge_bad':edge_bad,'stray_edges':outside,'Tstar_rows':len(trim),'live':live,'recovery_first2':recovery,'duration_s':sum(r['dt_us'] for r in rows.values())/1e6,'post_stable_duration_s':sum(r['dt_us'] for n,r in rows.items() if n>meta['attempts'][0]['stable_frame'])/1e6,'refs':{'first_window':refs[window[0]],'last_frame':refs[max(rows)],'first_gate':gate_refs[0],'first_fall':gate_refs[fall[0]],'last_fall':gate_refs[fall[-1]]}}
assert dt[0]==checks['dt_u'] and dt[1]==checks['dt_a']
assert len(pairs)==checks['endpoint']['pairs']
ind['recovery_first3']={k:S.median(sum(rows[n][k] for n in blocks[b][:3]) for b in fall if len(blocks[b])>=3) for k in ('img_new','buf_new')}
ind['totals_all']={k:sum(r[k] for r in rows.values()) for k in ('bf_dlskip','bf_clr_skip','bf_skip_drop','bf_mixed','bf_defer_force','bf_trig_fire','bf_trig_wait','bf_trig_fb','bf_xover','bf_xover_acb','bf_defer')}
ind['C9_reported']=abs(dt[1]-dt[0])/dt[0]
ind['burn_valid']=False
ind.pop('candidate_b',None)  # failed calibration: publish means only, never a usable budget
ind['Tstar_removed_in_window']=sum(n in trim for n in window)
ind['pairs_list']=pairs
ind['edge_block_line_refs']={str(b):gate_refs[b] for b in edges}
result={'verdict':'ADMITTED' if not protocol and all(c.values()) else 'NOT ADMITTED','protocol_errors':protocol,'checks':c,'independent':ind,'hashes':hashes}
(out/'VERIFY.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='hashes'},indent=2))
