# Independent parser for ABBA frame-time runs (audit 110). Does not import session scorers.
import re, sys, json, pickle
MAIN=('dt_us','draws','dispatches','cpu_gpu_us','gpu_busy_us','arm','blk','cpu_main_us','cpu_present_us','semwait_us','faults','fault_us','submits','lat_us')
DRAW=('spin_gpu_us','rec_n','da_walk_us','da_take_us','da_queue_us','da_hit','da_miss','da_late','da_walks','sync_ups','img_up','img_up_kb','prot_us','rp_begin','cb_copy','srt_miss','da_work_us','spin_us','faults_main','fault_main_us','prot_gpu_us')
X=('cspfree_hit','cspfree_look','cspf_have','cspf_new','cs_sync_new','cs_sync_wait','cs_sync_new_us','cs_sync_wait_us','cspfree_bad','da_wjobs','da_wlag_us','sync_up_kb','rt_kpx','rt_att','da_qcall')
tok=re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
def parse(path):
    rows={}; gates=[]
    with open(path,'rb') as f:
        for raw in f:
            if raw.startswith(b'GateArm:'):
                m=re.match(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+)',raw)
                gates.append((int(m.group(3)),int(m.group(1)),int(m.group(4))))
                continue
            if not raw.startswith(b'FrameTrace'): continue
            if raw.startswith(b'FrameTrace: '): want=MAIN
            elif raw.startswith(b'FrameTrace-draw: '): want=DRAW
            elif raw.startswith(b'FrameTrace-x: '): want=X
            else: continue
            d=dict(tok.findall(raw))
            if b'n' not in d: continue
            n=int(d[b'n']); r=rows.setdefault(n,{})
            for k in want:
                v=d.get(k.encode())
                if v is not None: r[k]=int(v)
    return rows,gates
if __name__=='__main__':
    tag,path=sys.argv[1],sys.argv[2]
    rows,gates=parse(path)
    pickle.dump((rows,gates),open('C:/kyty/s110/audit110/%s.pkl'%tag,'wb'))
    print(tag,len(rows),len(gates))
