# И-L7 row check per row / per block / per log for every L tag (row of the design lw131.md s.7.3; not a term of the reading)
import sys
sys.argv = ['x']
exec(open('C:/kyty/s131/audit131/recount131.py', encoding='utf-8').read().split("if __name__ == '__main__':")[0])
for t in ('lw1s131', 'lw2s131', 'lw3s131', 'lw4s131', 'lw5s131', 'lw6s131'):
    L = read_log(ROOT + 'log_%s.txt' % t)
    rows = L['rows']
    bad = [(n, g(r, 'lw_mark_pages') + g(r, 'lw_sync_pages') - g(r, 'lw_stamp_pages')) for n, r in sorted(rows.items())
           if g(r, 'lw_stamp_pages') < g(r, 'lw_mark_pages') + g(r, 'lw_sync_pages')]
    nb = None
    if L['arms']:
        B = blocks_of(L)
        nb = sum(1 for b in B if sum(g(r, 'lw_stamp_pages') - g(r, 'lw_mark_pages') - g(r, 'lw_sync_pages') for r in b['pos'].values()) < 0)
        nb = '%d of %d' % (nb, len(B))
    mult16 = all(d % 16 == 0 for n, d in bad)
    print(t, 'rows', len(rows), 'rows bad', len(bad), 'sum deficit', sum(d for n, d in bad), 'all multiples of 16', mult16,
          'blocks bad', nb, 'first', bad[:3])
