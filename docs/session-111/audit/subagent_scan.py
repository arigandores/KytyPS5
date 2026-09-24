# Protocol lens (audit 111): tool calls of every subagent transcript, first/last time, and any call that falls
# inside a sealed-run window (local time = UTC + 2).
import json, glob, os, sys, datetime as dt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
D = 'C:/Users/<user>/.claude/projects/C--Users-<user>-OneDrive-Desktop-ps5-em/314bf4dc-f9bb-42ec-a084-04f00b8e50d0/subagents'
WIN = [('go111', '2026-09-24T04:33:23', '2026-09-24T04:44:26'), ('go111b', '2026-09-24T04:46:51', '2026-09-24T05:05:41'),
       ('go111v', '2026-09-24T05:08:04', '2026-09-24T05:10:41')]
for p in sorted(glob.glob(D + '/*.jsonl')):
    meta = {}
    mp = p[:-6] + '.meta.json'
    if os.path.exists(mp): meta = json.load(open(mp, encoding='utf-8'))
    first = last = None; calls = 0; inwin = []
    for raw in open(p, 'rb'):
        try: e = json.loads(raw)
        except Exception: continue
        ts = e.get('timestamp')
        if not ts: continue
        t = (dt.datetime.fromisoformat(ts.replace('Z', '+00:00')) + dt.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S')
        first = first or t; last = t
        content = (e.get('message') or {}).get('content')
        if isinstance(content, list):
            for c in content:
                if c.get('type') == 'tool_use':
                    calls += 1
                    for name, a, b in WIN:
                        if a <= t <= b:
                            inp = c.get('input') or {}
                            inwin.append((name, t, c.get('name'), str(inp.get('command') or inp.get('file_path') or inp)[:150]))
    print(os.path.basename(p), meta.get('description') or meta, first, last, 'calls', calls, 'IN-WINDOW', len(inwin))
    for x in inwin[:20]: print('    ', x)
