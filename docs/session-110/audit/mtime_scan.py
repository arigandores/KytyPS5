import os, datetime, sys
W=[('go110','2026-09-24 00:30:54','2026-09-24 00:54:32'),('go110b','2026-09-24 01:00:16','2026-09-24 01:23:56'),('go110c','2026-09-24 02:11:45','2026-09-24 02:25:03'),('go110v','2026-09-24 02:26:29','2026-09-24 02:29:05')]
W=[(n,datetime.datetime.fromisoformat(a).timestamp(),datetime.datetime.fromisoformat(b).timestamp()) for n,a,b in W]
hits={n:[] for n,_,_ in W}
cnt=0
for root in sys.argv[1:]:
    for dp,dn,fn in os.walk(root):
        if 'audit110' in dp or '.git' in dp.split(os.sep)[-1:]: 
            pass
        for f in fn:
            p=os.path.join(dp,f); cnt+=1
            try: t=os.stat(p).st_mtime
            except: continue
            for n,a,b in W:
                if a<=t<=b: hits[n].append((datetime.datetime.fromtimestamp(t).strftime('%H:%M:%S'),p))
print('files',cnt)
for n in hits:
    print('==',n,len(hits[n]))
    for t,p in sorted(hits[n])[:400]: print('  ',t,p)
