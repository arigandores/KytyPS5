import json, os, sys
base=os.path.expanduser('~/.claude/projects/C--Users-<user>-OneDrive-Desktop-ps5-em/')
f=base+'314bf4dc-f9bb-42ec-a084-04f00b8e50d0.jsonl'
lo,hi=sys.argv[1],sys.argv[2]
keys=sys.argv[3:]
for line in open(f,encoding='utf-8',errors='replace'):
    try: o=json.loads(line)
    except: continue
    ts=o.get('timestamp') or ''
    if not (lo<=ts[:19]<=hi): continue
    c=(o.get('message') or {}).get('content')
    if isinstance(c,list):
        for part in c:
            if isinstance(part,dict) and part.get('type')=='tool_use':
                s=json.dumps(part.get('input'),ensure_ascii=False)
                if any(k in s for k in keys):
                    print(ts, part.get('name'), s[:230].replace('\n',' '))
