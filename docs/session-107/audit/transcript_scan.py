"""List tool calls (and their timestamps) in the main transcript and subagents during the sealed run windows."""
import json, os, sys, glob
from datetime import datetime, timezone, timedelta

ROOT = 'C:/Users/<user>/.claude/projects/C--Users-<user>-OneDrive-Desktop-ps5-em'
SID = 'd7017072-4de0-4aed-b17c-a31303802358'
files = [os.path.join(ROOT, SID + '.jsonl')] + glob.glob(os.path.join(ROOT, SID, 'subagents', '*.jsonl'))
LOCAL = timedelta(hours=2)
W = [('obs107', '08:10:20', '08:16:05'), ('dab107', '08:18:58', '08:29:40')]
def hms(ts):
    t = datetime.fromisoformat(ts.replace('Z', '+00:00')) + LOCAL
    return t.strftime('%H:%M:%S')
for f in files:
    try:
        lines = open(f, encoding='utf-8').read().splitlines()
    except Exception as e:
        print('ERR', f, e); continue
    first = last = None
    hits = []
    for ln in lines:
        try:
            d = json.loads(ln)
        except Exception:
            continue
        ts = d.get('timestamp')
        if not ts:
            continue
        h = hms(ts)
        first = first or h; last = h
        msg = d.get('message') or {}
        content = msg.get('content') if isinstance(msg, dict) else None
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get('type') in ('tool_use', 'tool_result'):
                for name, a, b in W:
                    if a <= h <= b:
                        if c.get('type') == 'tool_use':
                            desc = json.dumps(c.get('input'))[:260]
                            hits.append((h, name, 'USE', c.get('name'), desc))
                        else:
                            txt = c.get('content')
                            txt = json.dumps(txt)[:160] if txt is not None else ''
                            hits.append((h, name, 'RESULT', '', txt))
    print('==', os.path.basename(f), first, last, 'hits in windows', len(hits))
    for x in hits:
        print('   ', *x)
