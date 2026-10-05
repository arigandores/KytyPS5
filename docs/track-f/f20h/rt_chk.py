import sys, os, re, json, statistics
# Red Team F20h: independent recount of F20g census fields for chosen frames.
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
path, targets, out = sys.argv[1], [int(x) for x in sys.argv[2].split(',')], sys.argv[3]
FTN = re.compile(rb'^FrameTrace: n=(\d+) ')
KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(\d+)')
TAB = re.compile(rb'([A-Za-z0-9_+.-]+)=(\d+)/(\d+)')
TH = re.compile(rb'^\[(\d+)\]\[(\d\d):(\d\d):(\d\d)\.(\d+)\] (\S+)')
scene = False
dts = {}          # n -> dt_us (scene only)
order = []
recs = {}
cur = None        # n of the last FrameTrace: n= line (sub-lines attach to it)
iv = []           # lines since last FrameTrace: n=
last = max(targets) + 12
ln = 0
with open(path, 'rb') as f:
    for line in f:
        ln += 1
        if (ln & 0xfffff) == 0 and (os.path.exists(LOCK) or os.path.exists(STOP)):
            print('ABORT', ln); sys.exit(3)
        if not scene:
            if b'Level has started: underwater_aerial_garden' in line:
                scene = True
            continue
        m = FTN.match(line)
        if m:
            n = int(m.group(1))
            d = dict((k.decode(), int(v)) for k, v in KV.findall(line))
            dts[n] = d['dt_us']; order.append(n)
            if n in targets:
                th = []
                ps = []
                for l in iv:
                    t = TH.match(l)
                    if t:
                        th.append('%s %s:%s.%s %s' % (t.group(1).decode(), t.group(3).decode(), t.group(4).decode(), t.group(5).decode(), t.group(6).decode()))
                    if l.startswith(b'PriorityStall:'):
                        ps.append(l.strip().decode('ascii', 'replace'))
                recs[n] = dict(ln=ln, ft=d, th=th, ps=ps, ivlines=len(iv))
            cur = n
            iv = []
            if n > last:
                break
            continue
        if line.startswith(b'FrameTrace-'):
            if cur in recs:
                c = line.find(b':')
                tp = line[11:c].decode('ascii', 'replace')
                if tp in ('wait', 'submit', 'pm4', 'pops', 'direct'):
                    for k, a, b in TAB.findall(line):
                        recs[cur]['ft'][tp + '.' + k.decode()] = '%d/%d' % (int(a), int(b))
                else:
                    for k, v in KV.findall(line):
                        recs[cur]['ft'][tp + '.' + k.decode()] = int(v)
            continue
        iv.append(line)
pos = dict((n, i) for i, n in enumerate(order))
res = {}
for t in targets:
    i = pos[t]
    before = [n for n in order[:i][::-1] if dts[n] < 100000 and n not in targets][:10]
    after = [n for n in order[i + 1:] if dts[n] < 100000 and n not in targets][:10]
    res[t] = dict(rec=recs[t], nb=before + after)
# medians need neighbour records: second pass is too costly; recompute medians of FrameTrace core only from dts here
json.dump(dict(res=res, dts=dict((str(k), v) for k, v in dts.items())), open(out, 'w'))
for t in targets:
    r = res[t]['rec']
    ft = r['ft']
    print('n', t, 'ln', r['ln'], 'ivlines', r['ivlines'], 'dt', ft['dt_us'], 'lat', ft['lat_us'], 'semwait', ft['semwait_us'], 'submit_us', ft['submit_us'],
          'cpu_gpu', ft['cpu_gpu_us'], 'cpu_main', ft['cpu_main_us'], 'cpu_proc', ft['cpu_proc_us'], 'draws', ft['draws'])
    for k in ('x.skc_pres_ns', 'x.prot_gpu_ro_ns', 'draw.prot_gpu_us', 'draw.prot_us', 'draw.rec_direct_us', 'draw.da_take_us', 'draw.da_work_us', 'x.mt_age_ns', 'submit.other', 'wait.other', 'x.pb_wait_us'):
        kk=[x for x in ft if x.endswith(k.split('.',1)[1]) ]
        print('   ', k, [(x, ft[x]) for x in kk])
    print('   nb_med_dt', statistics.median([dts[n] for n in res[t]['nb']]), 'nb', res[t]['nb'])
    print('   PS', r['ps'])
    print('   TH', r['th'][:40])
