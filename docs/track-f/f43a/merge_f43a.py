# F43a (HPP-783): merge of the four parts of faults_f43a.py (out_p0..3.tsv) into faults_f43a.tsv; distinct logs by
# sha256 (copies such as _kyty.txt / log_<tag>.txt are counted once); per-build table and the logs with the largest pass.
# Usage: python merge_f43a.py <out.tsv> <part.tsv> [<part.tsv> ...]   (last line ALL OK)
import os, sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
TAB, NL = chr(9), chr(10)
hdr, rows = None, []
for p in sys.argv[2:]:
    for i, l in enumerate(open(p, encoding='utf-8')):
        c = l.rstrip(NL).split(TAB)
        if i == 0:
            hdr = c
            continue
        rows.append(c)
rows.sort()
ix = {k: i for i, k in enumerate(hdr)}
I = lambda r, k: int(r[ix[k]]) if r[ix[k]] not in ('None', '') else 0
with open(sys.argv[1], 'w', encoding='utf-8', newline=NL) as o:
    o.write(TAB.join(hdr) + NL)
    for r in rows:
        o.write(TAB.join(r) + NL)
uniq = {}
for r in rows:
    uniq.setdefault(r[ix['sha256']], r)
u = list(uniq.values())
print('rows', len(rows), 'distinct_sha256', len(u), 'with_fault_lines', sum(1 for r in u if I(r, 'fault_lines') > 0))
print('fault_lines_total', sum(I(r, 'fault_lines') for r in u), 'max_total_per_log', max(I(r, 'fault_lines') for r in u),
      'logs_total_gt_1023', sum(1 for r in u if I(r, 'fault_lines') > 1023))
print('max_pass_gap20', max(I(r, 'max20') for r in u), 'max_pass_gap200', max(I(r, 'max200') for r in u),
      'passes_gt_1023_gap20', sum(I(r, 'over20') for r in u), 'passes_gt_1023_gap200', sum(I(r, 'over200') for r in u))
print('passes_gap20_total', sum(I(r, 'passes20') for r in u), 'witness_zero', sum(I(r, 'wit_zero') for r in u),
      'witness_unaligned', sum(I(r, 'wit_unaligned') for r in u), 'witness_top', sum(I(r, 'wit_top') for r in u))
order = ['9235a7ac', 'dac02fb9', 'FS2', 'P23', 'FS3', 'FS4', 'FS5', 'S12', 'FS6', 'FS7', 'FS8', 'S18', 'FS9', 'FS10', 'FS11',
         'FS12']
print('build | logs | distinct | with_faults | passes20 | max_pass20 | max_pass200 | max_total')
for b in order:
    rb = [r for r in rows if r[ix['build']] == b]
    ub = [r for r in u if r[ix['build']] == b]
    if not rb:
        print(b, '| 0')
        continue
    print(b, '|', len(rb), '|', len(ub), '|', sum(1 for r in ub if I(r, 'fault_lines') > 0), '|',
          sum(I(r, 'passes20') for r in ub), '|', max(I(r, 'max20') for r in ub), '|', max(I(r, 'max200') for r in ub), '|',
          max(I(r, 'fault_lines') for r in ub))
for key in ('max20', 'max200', 'fault_lines'):
    r = max(u, key=lambda r: (I(r, key), r[0]))
    print('top', key, I(r, key), r[ix['path']], r[ix['build']], r[ix['sha256']][:16])
ok = len(rows) == 539 and hdr is not None
print('ALL OK' if ok else 'FAIL')
