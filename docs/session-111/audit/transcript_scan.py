# Protocol lens (audit 111): every tool_use in the session transcript with local time (+02:00), plus
# the sealed-run windows from the chain logs. Streams the JSONL.
import json, sys, datetime as dt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
PATH = 'C:/Users/<user>/.claude/projects/C--Users-<user>-OneDrive-Desktop-ps5-em/314bf4dc-f9bb-42ec-a084-04f00b8e50d0.jsonl'
LOCAL = dt.timedelta(hours=2)
lo = sys.argv[1] if len(sys.argv) > 1 else '2026-09-24T02:50'
hi = sys.argv[2] if len(sys.argv) > 2 else '2026-09-24T05:20'
WINDOWS = [('go111 obs111+vds111', '04:33:20', '04:44:26'), ('go111b vds111b+shp111+vss111', '04:46:49', '05:05:41'),
           ('go111v vid111', '05:08:00', '05:10:41')]


def in_window(t):
    hm = t.strftime('%H:%M:%S')
    for name, a, b in WINDOWS:
        if a <= hm <= b: return name
    return ''


out = []
with open(PATH, 'rb') as f:
    for raw in f:
        try:
            e = json.loads(raw)
        except Exception:
            continue
        ts = e.get('timestamp')
        if not ts: continue
        t = dt.datetime.fromisoformat(ts.replace('Z', '+00:00')) + LOCAL
        tl = t.strftime('%Y-%m-%dT%H:%M:%S')
        if not (lo <= tl <= hi): continue
        msg = e.get('message') or {}
        content = msg.get('content')
        side = e.get('isSidechain')
        if isinstance(content, list):
            for c in content:
                if c.get('type') == 'tool_use':
                    inp = c.get('input') or {}
                    s = inp.get('command') or inp.get('file_path') or inp.get('description') or inp.get('prompt') or json.dumps(inp)
                    s = str(s).replace('\n', ' | ')[:260]
                    out.append('%s %s%s %-14s %s' % (tl, 'SIDE ' if side else '', ('[' + in_window(t) + ']') if in_window(t) else '',
                                                     c.get('name'), s))
                elif c.get('type') == 'text' and e.get('type') == 'user' and not side:
                    s = c.get('text', '').replace('\n', ' | ')[:200]
                    out.append('%s %sUSER-TEXT %s' % (tl, ('[' + in_window(t) + '] ') if in_window(t) else '', s))
        elif isinstance(content, str) and e.get('type') == 'user':
            out.append('%s %sUSER %s' % (tl, ('[' + in_window(t) + '] ') if in_window(t) else '', content.replace('\n', ' | ')[:200]))
for l in out: print(l)
