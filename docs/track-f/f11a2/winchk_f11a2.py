# F11a2 (HPP-460): window check of ROADMAP p.277(g) / p.372(b) before the RenderDoc replay (a process with a Vulkan device).
# Open only if: no C:/kyty/SEALED_RUN.lock, no C:/kyty/f287/STOP, no kyty_emulator.exe process, and none of the run links
# (named list p.277(g)/p.372(b) + every company issue whose title has the word of runs), in_progress or with an executionRunId is in_progress or has a run.
# Appends one line to C:/kyty/f287/times.txt (UTC from the clock). Exit 0 = open, 5 = closed, 3 = lock, 4 = STOP.
import os
import sys
import json
import subprocess
import datetime
import urllib.request

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
if os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(4)
BASE = os.environ['PAPERCLIP_API_URL'].rstrip('/')
if BASE.endswith('/api'):
    BASE = BASE[:-4]
KEY = os.environ['PAPERCLIP_API_KEY']
CO = os.environ['PAPERCLIP_COMPANY_ID']
SELF = 'HPP-460'
NAMED = ['HPP-337', 'HPP-342', 'HPP-357', 'HPP-315', 'HPP-318', 'HPP-352', 'HPP-364', 'HPP-393', 'HPP-383', 'HPP-397', 'HPP-388',
         'HPP-410', 'HPP-418', 'HPP-421', 'HPP-424', 'HPP-449', 'HPP-441', 'HPP-453', 'HPP-433']


def get(path):
    rq = urllib.request.Request(BASE + path, headers={'Authorization': 'Bearer ' + KEY})
    return json.loads(urllib.request.urlopen(rq, timeout=60).read().decode('utf-8'))


def items(x):
    if isinstance(x, list):
        return x
    for k in ('issues', 'items', 'data'):
        if isinstance(x, dict) and isinstance(x.get(k), list):
            return x[k]
    return []


rows = {}
for st in ('in_progress', 'in_review', 'todo', 'blocked'):
    for it in items(get('/api/companies/%s/issues?status=%s&limit=500' % (CO, st))):
        rows[it.get('identifier')] = it
for ident in NAMED:
    if ident not in rows:
        rows[ident] = get('/api/issues/%s' % ident)
busy = []
other = []
named = []
for ident, it in sorted(rows.items(), key=lambda kv: str(kv[0])):
    st = it.get('status')
    run = it.get('executionRunId')
    if ident in NAMED:
        named.append('%s %s run=%s' % (ident, st, run or '-'))
    if ident == SELF:
        continue
    if st == 'in_progress' or run:
        other.append('%s %s' % (ident, st))
    title = (it.get('title') or '').lower()
    runlink = ident in NAMED or ('прогон' in title)
    if (st == 'in_progress' or run) and runlink:
        busy.append('%s %s run=%s [%s]' % (ident, st, run or '-', (it.get('title') or '')[:70]))
tl = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq kyty_emulator.exe', '/NH'], capture_output=True, text=True).stdout
emu = 'kyty_emulator.exe' in tl
openw = (not busy) and (not emu)
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
line = '%s F11a2 HPP-460 window p.277(g)/p.372(b) before replay: lock no, STOP no, emulator %s; named: %s; busy run links (named or title with the word of runs, in_progress or executionRunId): %s; other active (not run links): %s -> %s' % (
    now, 'yes' if emu else 'no', '; '.join(named), '; '.join(busy) if busy else 'none', '; '.join(other) or 'none', 'OPEN' if openw else 'CLOSED')
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
with open('C:/kyty/f287/times.txt', 'ab') as f:
    f.write((line + chr(10)).encode('utf-8'))
print(line)
sys.exit(0 if openw else 5)
