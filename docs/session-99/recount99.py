"""Parent's independent arithmetic check of raw session-98 baselines; no scorer imports."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import re
import statistics

TOKEN = re.compile(rb'\b(n|arm|blk|cpu_gpu_us|spin_gpu_us|bf_burn_ns|bf_edge)=(-?\d+)\b')
GATE = re.compile(rb'GateArm: arm=(\d+).*?block=(\d+) frame=(\d+)')

def read(tag):
    rows, gates, sha = {}, {}, hashlib.sha256()
    with (Path('C:/kyty/s98') / ('log_' + tag + '.txt')).open('rb') as f:
        for line in f:
            sha.update(line)
            g = GATE.search(line)
            if g:
                arm, block, frame = map(int, g.groups())
                gates[block] = (arm, frame)
            if line.startswith((b'FrameTrace:', b'FrameTrace-draw:', b'FrameTrace-x:')):
                vals = {k.decode(): int(v) for k,v in TOKEN.findall(line)}
                if 'n' in vals:
                    rows.setdefault(vals.pop('n'), {}).update(vals)
    return rows, gates, sha.hexdigest()

def floor(tag):
    rows, gates, sha = read(tag)
    grouped = defaultdict(list)
    for n, row in sorted(rows.items()):
        if 'arm' in row and 'blk' in row:
            grouped[row['blk']].append(n)
    trim = set()
    for b,(arm,_) in gates.items():
        if b-1 in gates and gates[b-1][0] != arm:
            trim.update(grouped[b][:2])
            trim.update(grouped[b-1][-1:])
    blocks = []
    for b,ns in sorted(grouped.items()):
        ns = [n for n in ns if n >= 2100 and b>=1 and 'cpu_gpu_us' in rows[n]]
        if not ns:
            continue
        keep = [n for n in ns if n not in trim]
        assert keep, 'unexpected empty trimmed block'
        val = statistics.mean(rows[n]['cpu_gpu_us']-rows[n]['spin_gpu_us']-rows[n]['bf_burn_ns']/1000 for n in keep)
        blocks.append((b,rows[ns[0]]['arm'],val))
    selected, pairs = set(), 0
    for i in range(len(blocks)-1):
        if blocks[i][1] != blocks[i+1][1]:
            selected.update((i,i+1)); pairs += 1
    values = [blocks[i][2]/1000 for i in selected if blocks[i][1]==1]
    return {'tag':tag,'sha256':sha,'pairs':pairs,'armed_blocks':len(values),'F_ms':statistics.median(values)}

def edges(tag):
    rows,gates,sha = read(tag)
    falling = [(b,frame) for b,(arm,frame) in gates.items() if b-1 in gates and gates[b-1][0]==1 and arm==0]
    complete = [(b,n) for b,n in falling if len([f for f,r in rows.items() if r.get('blk')==b and f>=n])>=3]
    return {'tag':tag,'sha256':sha,'falling_edges':len(falling),'completed':len(complete),'bf_edge_sum':sum(r.get('bf_edge',0) for r in rows.values())}

if __name__=='__main__':
    a,c = floor('bf98a'),floor('bf98c')
    rv,warm = edges('rv98a'),edges('rv98a_warmup')
    assert round(a['F_ms'],3)==14.274 and round(c['F_ms'],3)==12.825
    assert rv['completed']+warm['completed']==857
    result = {'a':a,'c':c,'proof':rv,'warmup':warm,'global_low':min(a['F_ms'],c['F_ms'])+2.2535,'global_high':max(a['F_ms'],c['F_ms'])+2.2535}
    Path('C:/kyty/s99/recount99.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
