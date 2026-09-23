import json, sys
base = 'C:/Users/<user>/.claude/projects/C--Users-<user>-OneDrive-Desktop-ps5-em/d7017072-4de0-4aed-b17c-a31303802358.jsonl'
a, b = sys.argv[1], sys.argv[2]
for line in open(base, encoding='utf-8', errors='replace'):
    try: e = json.loads(line)
    except Exception: continue
    ts = e.get('timestamp', '')
    if a <= ts[:19] <= b:
        msg = e.get('message') or {}
        c = msg.get('content') if isinstance(msg, dict) else None
        if isinstance(c, list):
            for x in c:
                if isinstance(x, dict) and x.get('type') in ('tool_use', 'tool_result', 'text'):
                    body = x.get('input') or x.get('content') or x.get('text')
                    print('---', ts, x.get('type'), x.get('name', ''))
                    print(json.dumps(body, ensure_ascii=False)[:3000] if not isinstance(body, str) else body[:3000])
