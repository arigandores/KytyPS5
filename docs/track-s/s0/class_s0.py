#!/usr/bin/env python3
"""class_s0.py - S0 (HPP-294): the class of every frame >= 100 ms after the first scene frame from out/<tag>.json.
Rule (executor's variant; co-occurrence in the row, not a proven cause):
  PRIO    sum of "PriorityStall: us" of the row >= dt/2 and cpu_gpu_us < dt/2  -> other: priority-operation wait (B3b form)
  GPUTHR  cpu_gpu_us >= dt/2 -> the GuestGpu thread is CPU-busy: translation / synchronous pipeline creation / resource
          upload are NOT separable without AvTrace; flags: +PIPE (skipped draw or held flip in the row), +UP (img_up_kb >= 65536)
  WAIT    otherwise (GuestGpu not CPU-busy, no PriorityStall line >= dt/2) -> [U]
ASCII output."""
import json
OUT = 'C:/kyty/s288/s0/out'
TAGS = ('v142',) + tuple('c142_%02d' % i for i in range(1, 11))
agg = {}
rows = []
for t in TAGS:
    d = json.load(open('%s/%s.json' % (OUT, t)))
    for r in d['long']:
        prio = sum(x for x in r['prio'] if x > 0)
        if prio * 2 >= r['dt'] and r['cpu_gpu'] * 2 < r['dt']:
            cls = 'PRIO'
        elif r['cpu_gpu'] * 2 >= r['dt']:
            cls = 'GPUTHR'
        else:
            cls = 'WAIT'
        fl = ('+PIPE' if (r['skip'] > 0 or r['held'] > 0) else '') + ('+UP' if r['img_up_kb'] >= 65536 else '')
        rows.append((t, r['n'], r['dt'], r['part'], cls, fl, r['cpu_gpu'], prio, r['img_up_kb'], r['skip'], r['held'], r['line']))
        if t != 'v142':
            a = agg.setdefault((r['part'], cls, fl), [0, 0, 0])
            a[0] += 1; a[1] += r['dt']; a[2] += min(r['dt'], r['cpu_gpu'])
print('tag n dt_us part class flags cpu_gpu_us prio_us img_up_kb skip held log_line')
for x in rows:
    print('%s %d %d %s %s %s %d %d %d %d %d %d' % (x[0], x[1], x[2], x[3], x[4], x[5] or '-', x[6], x[7], x[8], x[9], x[10], x[11]))
print('census (10 logs) by part / class / flags: frames, sum dt_us, sum min(dt, cpu_gpu_us)')
tot = [0, 0, 0]
for k in sorted(agg):
    print('  %s %s %s: %d %d %d' % (k[0], k[1], k[2] or '-', agg[k][0], agg[k][1], agg[k][2]))
    for i in range(3):
        tot[i] += agg[k][i]
print('  total: %d %d %d' % tuple(tot))
for part in ('window', 'hold'):
    n = sum(v[0] for k, v in agg.items() if k[0] == part)
    print('  %s: frames %d; PRIO %d; GPUTHR %d (with +PIPE %d, without %d); WAIT %d' % (
        part, n, sum(v[0] for k, v in agg.items() if k[0] == part and k[1] == 'PRIO'),
        sum(v[0] for k, v in agg.items() if k[0] == part and k[1] == 'GPUTHR'),
        sum(v[0] for k, v in agg.items() if k[0] == part and k[1] == 'GPUTHR' and 'PIPE' in k[2]),
        sum(v[0] for k, v in agg.items() if k[0] == part and k[1] == 'GPUTHR' and 'PIPE' not in k[2]),
        sum(v[0] for k, v in agg.items() if k[0] == part and k[1] == 'WAIT')))
print('ALL OK')
