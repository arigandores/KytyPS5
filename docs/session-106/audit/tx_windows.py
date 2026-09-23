"""Auditor: transcript entries (main + subagents) whose timestamp falls in the sealed-run windows."""
import json, glob, os
base = 'C:/Users/<user>/.claude/projects/C--Users-<user>-OneDrive-Desktop-ps5-em/d7017072-4de0-4aed-b17c-a31303802358'
files = [base + '.jsonl'] + glob.glob(base + '/subagents/*.jsonl')
W = [('2026-09-23T05:11:06', '2026-09-23T05:21:39', 'gw106'), ('2026-09-23T05:24:51', '2026-09-23T05:38:07', 'dab106+vdb106'),
     ('2026-09-23T05:38:50', '2026-09-23T05:41:22', 'vid106')]
for f in files:
    for line in open(f, encoding='utf-8', errors='replace'):
        try:
            e = json.loads(line)
        except Exception:
            continue
        ts = e.get('timestamp')
        if not ts:
            continue
        for a, b, name in W:
            if a <= ts[:19] <= b:
                msg = e.get('message') or {}
                content = msg.get('content') if isinstance(msg, dict) else None
                desc = ''
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict):
                            if c.get('type') == 'tool_use':
                                desc += ' TOOL_USE ' + c.get('name', '') + ' ' + json.dumps(c.get('input', {}))[:300]
                            elif c.get('type') == 'tool_result':
                                cc = c.get('content')
                                desc += ' TOOL_RESULT ' + (json.dumps(cc)[:200] if cc else '')
                            elif c.get('type') == 'text':
                                desc += ' TEXT ' + c.get('text', '')[:200]
                elif isinstance(content, str):
                    desc = ' STR ' + content[:200]
                print(name, ts, os.path.basename(f), e.get('type'), desc.replace('\n', ' ')[:600])
