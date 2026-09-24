# Extract per-flip fields from the ABBA log into a compact CSV (binary streaming read).
import sys, re, csv
path, outp = sys.argv[1], sys.argv[2]
tok = re.compile(rb' ([A-Za-z0-9_]+)=(-?\d+)')
MF = ['dt_us','cpu_gpu_us','gpu_busy_us','draws','arm','blk','cpu_main_us','cpu_present_us']
DF = ['bda_scan','spin_gpu_us','rec_n','da_miss','da_hit','da_take_us','da_walk_us','da_late']
XF = ['bda_nskip','bda_nwould','bda_nmiss','bda_nxthr','bda_nrace','bda_ginv_reg','bgc_evict','cs_sync_new','cs_sync_wait',
      'prio_unsub','prio_stall','gw_idle_prio','da_wskip','da_wjobs','da_wdrop']
rows = {}; gate = []; cnt = {'M':0,'D':0,'X':0}; dup = {'M':0,'D':0,'X':0}
seen = {'M':set(),'D':set(),'X':set()}
def parse(line, want):
    d = {}
    for m in tok.finditer(line):
        k = m.group(1).decode()
        if k == 'n' or k in want: d.setdefault(k, int(m.group(2)))
    return d
with open(path, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: '): t, want = 'M', MF
        elif line.startswith(b'FrameTrace-draw: '): t, want = 'D', DF
        elif line.startswith(b'FrameTrace-x: '): t, want = 'X', XF
        else:
            if line.startswith(b'GateArm:'): gate.append(line.decode('latin1').strip())
            continue
        d = parse(line, want); n = d['n']; cnt[t] += 1
        if n in seen[t]: dup[t] += 1
        seen[t].add(n)
        r = rows.setdefault(n, {})
        for k, v in d.items():
            if k != 'n': r[t+':'+k] = v
cols = ['M:'+k for k in MF] + ['D:'+k for k in DF] + ['X:'+k for k in XF]
with open(outp, 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(['n'] + cols)
    for n in sorted(rows):
        w.writerow([n] + [rows[n].get(c, '') for c in cols])
with open(outp + '.gatearm.txt', 'w') as fo:
    fo.write('\n'.join(gate) + '\n')
print('counts', cnt, 'dups', dup, 'gatearm', len(gate), 'n range', min(rows), max(rows))
