import re,json,pickle,statistics as st
from pathlib import Path
P=Path('C:/kyty/s99'); O=P/'work99_raw'
keys='n dt_us draws dispatches submits gpu_n cpu_main_us cpu_gpu_us cpu_present_us cpu_proc_us arm blk da_flip da_present rec_n rec_work_us cpu_record_us bf_burn_cpu_n fbp_n bf_igc_checks rt_att rt_kpx bf_edge lat_us'.split()
pat=re.compile(rb'\b('+b'|'.join(x.encode() for x in keys)+rb')=(-?\d+)\b')
for tag in ['bf99e','eng99a4']:
 rows={}; t=0
 with (P/('log_'+tag+'.txt')).open('rb') as f:
  for ln,line in enumerate(f,1):
   if not line.startswith((b'FrameTrace:',b'FrameTrace-draw:',b'FrameTrace-x:')):continue
   d={k.decode():int(v) for k,v in pat.findall(line)}
   if 'n' not in d:continue
   n=d['n']; r=rows.setdefault(n,{})
   if line.startswith(b'FrameTrace:'):
    t+=d['dt_us']/1e6;d.update(time=t,line=ln)
   r.update(d)
 score=json.loads((P/'settled_runs'/(tag+'_score.json')).read_text())
 bs={int(b):list(range(ns[0],ns[1]+1)) for b,ns in score['selection']['row_ranges'].items()}
 with (O/(tag+'.pkl')).open('wb') as f:pickle.dump((rows,bs),f)
 print(tag,len(rows),len(bs),min(bs),max(bs),rows[min(rows)].keys())
