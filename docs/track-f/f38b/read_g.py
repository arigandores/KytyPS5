"""F38b probe G reader: rows of arm G - ret 0, no error (POSIX errno not written, AIO COMPLETED), the growth happened
(trunc_done 1, size_at_c2 = offset + 8192), file restored; per entry. usage: read_g.py <rows.tsv>"""
import sys
EIO = -2147352571
rows = []
with open(sys.argv[1], encoding='utf-8') as f:
    head = f.readline().rstrip('\n').split('\t')
    for line in f:
        v = dict(zip(head, line.rstrip('\n').split('\t')))
        rows.append({k: (v[k] if k in ('entry_name', 'arm') else int(v[k])) for k in head})
g = [r for r in rows if r['arm'] == 'G']
for e in range(6):
    rs = [r for r in g if r['entry'] == e]
    if not rs:
        continue
    quiet = lambda r: (r['err'] == 12345 if r['entry'] in (1, 2, 4) else (r['aio_rc'] == 0 and r['aio_state'] == 3 if r['entry'] == 5 else True))
    ok = sum(1 for r in rs if r['ret'] == 0 and quiet(r) and r['trunc_done'] == 1 and r['size_at_c2'] == r['offset'] + 8192 and r['restore_ok'] == 1)
    eio = sum(1 for r in rs if r['ret'] < 0)
    pos = sum(1 for r in rs if r['ret'] > 0)
    print('%s G n %d ok %d error %d positive %d grown %d' % (rs[0]['entry_name'], len(rs), ok, eio, pos, sum(r['trunc_done'] for r in rs)))
print('G ALL OK' if g and all(r['ret'] == 0 and r['trunc_done'] == 1 and r['restore_ok'] == 1 for r in g) else 'G NOT OK (n %d)' % len(g))
