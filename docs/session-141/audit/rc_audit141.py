# Session Auditor s141 step 2: independent recount of the inventory141 rev.2 log numbers (own code, no shared code with step0/1/1b scripts).
# Part A: census.csv (s53-113). Part B: one streaming pass (binary) over "real" logs of C:/kyty/s113..s140.
# Real log = file named log_*.txt (or _kyty*.txt) > 1 MB, no path component starting with fx_/work_/mut/test_; dedup by sha256.
import csv, hashlib, os, re, sys, json, collections
OUT = 'C:/kyty/s141/step2/rc_audit141.json'
LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    sys.exit('LOCK PRESENT - abort')
res = {}
# ---------------- Part A: census
C = 'C:/kyty/s106_stage/bda113/census.csv'
cb = open(C, 'rb').read()
res['census_sha'] = hashlib.sha256(cb).hexdigest()
rows = list(csv.DictReader(open(C, encoding='utf-8', newline='')))
res['census_rows'] = len(rows)
lv = collections.Counter()
for r in rows:
    for x in set(filter(None, r['levels'].split('/'))):
        lv[x] += 1
res['census_levels'] = dict(lv)
res['census_scene_transition_next'] = sorted((r['session'], r['tag']) for r in rows if r['scene'] == 'transition_next')
fat = [(r['session'], r['tag'], r['fatal'][:60], r['scene'], r['levels']) for r in rows if r['fatal']]
res['census_fatal'] = fat
kinds = collections.Counter('FATAL' if f[2].startswith('--- Fatal Error') else 'ERROR' if f[2].startswith('--- Error') else
                            'HANG' if f[2].startswith('GpuHangAbort') else 'OTHER' for f in fat)
res['census_fatal_kinds'] = dict(kinds)
# intro_next runs s59..113 and --- Error --- among them
intro = [r for r in rows if 'intro_next' in r['levels'].split('/') and 59 <= int(r['session']) <= 113]
res['census_intro_59_113'] = [len(intro), sum(1 for r in intro if r['fatal'].startswith('--- Error'))]
# Sky Garden entries by session band and GpuHangAbort with requested < 6000
def req(f):
    m = re.search(r'requested=(\d+)', f)
    return int(m.group(1)) if m else None
sg = [r for r in rows if 'underwater_aerial_garden' in r['levels'].split('/')]
def band(a, b):
    xs = [r for r in sg if a <= int(r['session']) <= b]
    h = [(r['session'], r['tag'], req(r['fatal'])) for r in xs if r['fatal'].startswith('GpuHangAbort') and (req(r['fatal']) or 10**9) < 6000]
    return len(xs), h
res['census_sg_76_102'] = band(76, 102)
res['census_sg_103_113'] = band(103, 113)
# all hang rows with requested (to see double attribution)
res['census_hang_all'] = [(r['session'], r['tag'], req(r['fatal']), r['scene']) for r in rows if r['fatal'].startswith('GpuHangAbort')]
# ---------------- Part B: logs
def skip_path(p):
    parts = p.replace('\\', '/').split('/')
    return any(x.startswith(('fx_', 'work_', 'mut', 'test_')) for x in parts)
files = []
for s in range(113, 141):
    root = 'C:/kyty/s%d' % s
    if not os.path.isdir(root):
        continue
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith(('fx_', 'work_', 'mut', 'test_'))]
        for f in fn:
            if f.startswith('log_') and f.endswith('.txt'):
                p = os.path.join(dp, f).replace('\\', '/')
                try:
                    if os.path.getsize(p) > 1_000_000 and not skip_path(p):
                        files.append((s, p))
                except OSError:
                    pass
res['n_files'] = len(files)
FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) .*?\bdraws=(\d+)')
LV = re.compile(rb'GuestOut: Level has started: (\S+)')
OP = re.compile(rb'family=(\w+) opcode=(0x[0-9a-fA-F]+)')
MTL = re.compile(rb'MainTaskLate: us=(\d+)')
PS = re.compile(rb'^PriorityStall: .*?\bus=(\d+)')
AP = re.compile(rb'AsyncPipelines: skipped draw .*?frame=(\d+)')
logs = {}
seen = {}
for s, p in files:
    if os.path.exists(LOCK):
        sys.exit('LOCK APPEARED - abort')
    h = hashlib.sha256()
    d = dict(s=s, p=p, lv=[], ft=[], op=collections.Counter(), mtl=[], ps=[], ap=0, apf=set(), fatal=0, error=0, hang=0, dl=0,
             vke=0, vkw=0, trip=0, lvl_arg=None)
    with open(p, 'rb') as f:
        for line in f:
            h.update(line)
            if line.startswith(b'FrameTrace: '):
                m = FT.match(line)
                if m:
                    d['ft'].append((int(m.group(1)), int(m.group(2)), int(m.group(3)), len(d['lv'])))
                continue
            if b'Level has started' in line:
                m = LV.search(line)
                if m:
                    d['lv'].append((m.group(1).decode('utf-8', 'replace'), len(d['ft'])))
                continue
            if b'opcode is not implemented' in line:
                m = OP.search(line)
                d['op'][(m.group(1).decode(), m.group(2).decode().lower()) if m else ('?', '?')] += 1
                continue
            if line.startswith(b'MainTaskLate'):
                m = MTL.search(line)
                if m and int(m.group(1)) >= 1_000_000:
                    d['mtl'].append(int(m.group(1)))
                continue
            if line.startswith(b'PriorityStall:'):
                m = PS.match(line)
                if m:
                    d['ps'].append(int(m.group(1)))
                continue
            if b'AsyncPipelines: skipped draw' in line:
                d['ap'] += 1
                m = AP.search(line)
                if m:
                    d['apf'].add(int(m.group(1)))
                continue
            if b'--- Fatal Error ---' in line:
                d['fatal'] += 1
            elif b'--- Error ---' in line:
                d['error'] += 1
            if line.startswith(b'GpuHangAbort:'):
                d['hang'] += 1
            if b'ErrorDeviceLost' in line:
                d['dl'] += 1
            if b'[Vulkan][E]' in line:
                d['vke'] += 1
            elif b'[Vulkan][W]' in line:
                d['vkw'] += 1
            if line.startswith(b'BvhLoopCapTrip:'):
                d['trip'] += 1
    sha = h.hexdigest()
    d['sha'] = sha
    d['apf'] = len(d['apf'])
    d['op'] = {'%s %s' % k: v for k, v in d['op'].items()}
    if sha in seen:
        seen[sha].append(p)
        continue
    seen[sha] = [p]
    logs[sha] = d
res['n_unique'] = len(logs)
res['dups'] = {k[:8]: v for k, v in seen.items() if len(v) > 1}
json.dump(res, open(OUT.replace('.json', '_census.json'), 'w'), indent=0)
# compact per-log dump (ft kept for the analysis step)
json.dump({k: v for k, v in logs.items()}, open(OUT, 'w'))
print('files', len(files), 'unique', len(logs), 'census rows', len(rows))
