import json, glob, os, datetime
base=os.path.expanduser('~/.claude/projects/C--Users-<user>-OneDrive-Desktop-ps5-em/')
files=[base+'314bf4dc-f9bb-42ec-a084-04f00b8e50d0.jsonl']+glob.glob(base+'314bf4dc-f9bb-42ec-a084-04f00b8e50d0/**/*.jsonl',recursive=True)
W=[('go110','2026-09-23T22:30:54','2026-09-23T22:54:32'),('go110b','2026-09-23T23:00:16','2026-09-23T23:23:56'),('go110c','2026-09-24T00:11:45','2026-09-24T00:25:03'),('go110v','2026-09-24T00:26:29','2026-09-24T00:29:05')]
for f in files:
    for line in open(f,encoding='utf-8',errors='replace'):
        try: o=json.loads(line)
        except: continue
        ts=o.get('timestamp')
        if not ts: continue
        t=ts[:19]
        for n,a,b in W:
            if a<=t<=b:
                msg=o.get('message') or {}
                c=msg.get('content')
                if isinstance(c,list):
                    for part in c:
                        if isinstance(part,dict) and part.get('type')=='tool_use':
                            inp=json.dumps(part.get('input'))[:200]
                            print(n,ts,os.path.basename(f)[:20],part.get('name'),inp)
