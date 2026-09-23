import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
R = Path('C:/kyty/s109')
base = ' '.join((R / 'gates_base.txt').read_text(encoding='utf-8').split())
print('gates_base sha', hashlib.sha256((R / 'gates_base.txt').read_bytes()).hexdigest()[:12])
for f in ['gates_fam0.txt', 'gates_fam4.txt', 'gates_free0.txt', 'gates_free1.txt', 'gates_free2.txt']:
    t = ' '.join((R / f).read_text(encoding='utf-8').split())
    print(f, 'extends base:', t.startswith(base), 'tail:', repr(t[len(base):]))
tags = ['ent109_%d' % i for i in range(1, 9)] + ['vfy109'] + ['ent109b_%d' % i for i in range(1, 9)] + ['frm109']
MK = [b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'errordevicelost', b'std::terminate', b'abort()', b'fatal',
      b'unhandled exception', b'--- error ---', b'asyncpipelines: skipped draw', b'exception']
envs = {}
SUS = ('python', 'cmake', 'ninja', 'clang', 'kyty', 'renderdoc', 'ffmpeg', 'node', 'git', 'msbuild', 'link', 'steam',
       'game', 'obs', 'chrome', 'msedge', 'code')
for t in tags:
    m = json.loads((R / (t + '.json')).read_text(encoding='utf-8'))
    g = ' '.join((m.get('gates') or '').split())
    tail = g[len(base):] if g.startswith(base) else 'NOT BASE'
    so = (R / ('stdout_%s.txt' % t)).read_bytes().lower()
    hits = [k.decode() for k in MK if k in so]
    env = m['env']
    key = tuple(sorted((k, v) for k, v in env.items() if k not in ('KYTY_GATE_SCHEDULE', 'VK_SDK_PATH')))
    envs.setdefault(key, []).append(t)
    pr = m.get('pre_run', {})
    host = pr.get('host', {})
    top = host.get('top', [])
    names = [x['name'].lower() for x in top]
    susp = [n for n in names if any(s in n for s in SUS)]
    apps = [a['name'].replace('/', '\\').split('\\')[-1].lower() for a in pr.get('gpu_apps', [])]
    susp_apps = [a for a in apps if any(s in a for s in SUS)]
    print('%-10s tail %-16r stdout-mk %s util %s gpumem %s nproc %s susp_top %s susp_gpu %s launched %s sched %r' % (
        t, tail, hits, pr.get('gpu_util_median'), pr.get('gpu_memory_used_mib'), host.get('process_count'), susp,
        susp_apps, m['launched'], env.get('KYTY_GATE_SCHEDULE')))
print('distinct env sets (no schedule, no VK_SDK_PATH):', len(envs))
for e, ts in envs.items():
    print('  ', ts[0], '..', ts[-1], len(ts), e)
