# Dump full tool_use inputs (and matching tool_result heads) at given local times (audit 111).
import json, sys, datetime as dt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
PATH = 'C:/Users/<user>/.claude/projects/C--Users-<user>-OneDrive-Desktop-ps5-em/314bf4dc-f9bb-42ec-a084-04f00b8e50d0.jsonl'
want = sys.argv[1:]
ids = {}
with open(PATH, 'rb') as f:
    for raw in f:
        try: e = json.loads(raw)
        except Exception: continue
        ts = e.get('timestamp')
        if not ts: continue
        t = (dt.datetime.fromisoformat(ts.replace('Z', '+00:00')) + dt.timedelta(hours=2)).strftime('%H:%M:%S')
        content = (e.get('message') or {}).get('content')
        if not isinstance(content, list): continue
        for c in content:
            if c.get('type') == 'tool_use' and any(t.startswith(w) for w in want):
                print('=== %s %s' % (t, c.get('name')))
                print(json.dumps(c.get('input'), ensure_ascii=False)[:6000])
                ids[c.get('id')] = t
            elif c.get('type') == 'tool_result' and c.get('tool_use_id') in ids:
                cc = c.get('content')
                if isinstance(cc, list): cc = ' '.join(x.get('text', '') for x in cc if isinstance(x, dict))
                print('--- result of %s: %s' % (ids[c.get('tool_use_id')], str(cc)[:3000]))
