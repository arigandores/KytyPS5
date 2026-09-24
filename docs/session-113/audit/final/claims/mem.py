import re,sys
MiB=1048576
for tag in sys.argv[1:]:
    p=f'C:/kyty/s113/log_{tag}.txt'
    us=[]; bud=set(); gc=[]
    with open(p,'rb') as f:
        for l in f:
            if l.startswith(b'MemStats: heap=0'):
                m=re.search(rb'usage=(\d+) budget=(\d+)',l)
                us.append(int(m.group(1))/MiB); bud.add(round(int(m.group(2))/MiB,1))
            elif l.startswith(b'BufferGc:'):
                gc.append(l.strip()[:200].decode())
    # skip the startup entries (usage < 2 GiB)
    post=[u for u in us if u>4000]
    print(tag,'n',len(us),'budget',sorted(bud),'post-load range',round(min(post)) if post else None, round(max(post)) if post else None,'first3',[round(x) for x in post[:3]],'last',round(post[-1]) if post else None, gc)
