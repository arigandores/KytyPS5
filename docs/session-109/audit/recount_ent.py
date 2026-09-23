import json
import pickle
import sys
from math import comb
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
P = Path('C:/kyty/s109/audit109/parsed')
ROOT = Path('C:/kyty/s109')
ORDER = 'ABBAABBA'
out = {}


def load(tag):
    return pickle.load(open(P / ('%s.pkl' % tag), 'rb'))


def per_entry(tag, fields):
    d = load(tag)
    x = d['x']
    s = {f: sum(r.get(f, 0) for r in x.values()) for f in fields}
    missing = {f: sum(1 for r in x.values() if f not in r) for f in fields}
    ns = sorted(x)
    contiguous = ns == list(range(ns[0], ns[-1] + 1))
    ev_rows = [(n, r.get('cs_sync_new', 0), r.get('cs_sync_wait', 0)) for n, r in sorted(x.items())
               if r.get('cs_sync_new', 0) or r.get('cs_sync_wait', 0)]
    return d, s, missing, len(x), contiguous, ev_rows


for series, fields, armkeys in (
        ('ent109', ['cs_sync_new', 'cs_sync_wait', 'cspfam_look', 'cspfam_skip', 'cspf_new', 'cspfam_clr', 'cspf_have'],
         ('cspfam_look', 'cspfam_skip')),
        ('ent109b', ['cs_sync_new', 'cs_sync_wait', 'cspfam_look', 'cspfam_skip', 'cspf_new', 'cspfam_clr', 'cspf_have',
                     'cspfree_look', 'cspfree_hit', 'cspfree_bad', 'cspfree_src_miss', 'cspfree_spec_miss',
                     'cspfree_mat_fail', 'cspfree_clr', 'cspfree_store', 'cspfree_moved'],
         ('cspfree_look', 'cspfree_hit'))):
    SA = SB = 0
    print('==', series)
    rows = []
    for i in range(8):
        tag = '%s_%d' % (series, i + 1)
        arm = ORDER[i]
        d, s, missing, nrows, contig, ev = per_entry(tag, fields)
        S = s['cs_sync_new'] + s['cs_sync_wait']
        if arm == 'A':
            SA += S
        else:
            SB += S
        meta = json.load(open(ROOT / ('%s.json' % tag), encoding='utf-8'))
        env = meta.get('env', {})
        att = meta.get('attempts', [])
        pins = [e for e in d['events'] if 'GpuClockPin' in e[2]]
        pre = [e for e in d['events'] if 'PipelinePrecache' in e[2]]
        fatal = [e for e in d['events'] if any(k in e[2] for k in ('--- ', 'ErrorDeviceLost', 'Unhandled', 'GpuWaitSlow', 'GpuHangAbort', 'skipped draw'))]
        gates = meta.get('gates', '')
        row = dict(tag=tag, arm=arm, rows=nrows, contiguous=contig, S=S, **s,
                   missing_any=sum(missing.values()), events=ev, binary=meta.get('binary_sha256', '')[:8],
                   prereg=meta.get('prereg', {}).get('sha256', '')[:8], precache=env.get('KYTY_PIPELINE_PRECACHE'),
                   pin=env.get('KYTY_GPU_CLOCK_PIN'), sched='KYTY_GATE_SCHEDULE' in env, ckpt='KYTY_GPU_CHECKPOINTS' in env,
                   rec='KYTY_REC' in env, gates_tail=gates[-30:], attempts=[(a.get('outcome'), a.get('hold_exit'), a.get('hold_s')) for a in att],
                   pin_lines=len(pins), precache_line=pre[0][2][:110] if pre else None, fatal=len(fatal),
                   launched=meta.get('launched'), finished=meta.get('finished'))
        rows.append(row)
        print('%-10s %s rows %5d contig %s S %2d new %2d wait %2d cspf_new %3d fam_look %8d fam_skip %8d clr %4d %s' % (
            tag, arm, nrows, contig, S, s['cs_sync_new'], s['cs_sync_wait'], s['cspf_new'], s['cspfam_look'],
            s['cspfam_skip'], s['cspfam_clr'],
            ('free_look %d hit %d bad %d' % (s['cspfree_look'], s['cspfree_hit'], s['cspfree_bad'])) if 'cspfree_look' in s else ''))
        print('    events(n,new,wait):', ev)
        print('    bin %s prereg %s precache %s pin %s sched %s ckpt %s rec %s gates..%r att %s pinlines %d fatal %d missing %d' % (
            row['binary'], row['prereg'], row['precache'], row['pin'], row['sched'], row['ckpt'], row['rec'], row['gates_tail'],
            row['attempts'], row['pin_lines'], row['fatal'], row['missing_any']))
        print('    ', row['precache_line'])
    print('S_A', SA, 'S_B', SB)
    out[series] = {'rows': rows, 'S_A': SA, 'S_B': SB}

json.dump(out, open('C:/kyty/s109/audit109/recount_ent.json', 'w'), indent=1, default=str)
