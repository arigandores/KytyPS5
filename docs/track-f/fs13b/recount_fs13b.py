# FS13b (HPP-788, Red Team): own recount of the stand edition 3 rows (independent of sum_f38a2.py / sum_fs13a.py).
# Rules (mine, written before reading the counts; forms from item 691(v)(1) as printed in the F38a rows):
#   A at form d: sceKernelRead / sceKernelPread / AIO: ret == 0x80020005 as int32 (-2147352571); AIO also aio_state == 4;
#                read / _read / pread: ret == -1 and err == 5; all: pos_after == pos_before, untouched == 1, canary_ok == 1,
#                calls == 2, injected == 2.
#   A at form 0: ret == 0 (the old "0 given"), calls == 2, injected == 2.
#   E and G (both forms): ret == 0, calls == 1, injected == 0, canary_ok == 1; G also trunc_done/size_at_c2 printed only.
#   Counts per entry: A, K, Z, E, T, G rows.
# Usage: python recount_fs13b.py <rows_fd.tsv> <rows_f0.tsv>
import csv, collections, sys

ERR = -2147352571
ok = True


def a_d(x):
    e = x['entry_name']
    r = int(x['ret'])
    if e in ('read', '_read', 'pread'):
        form = r == -1 and x['err'] == '5'
    else:
        form = r == ERR and (e != 'sceKernelAioSubmitReadCommands' or x['aio_state'] == '4')
    return form and x['pos_after'] == x['pos_before'] and x['untouched'] == '1' and x['canary_ok'] == '1' and x['calls'] == '2' and x['injected'] == '2'


def a_0(x):
    return x['ret'] == '0' and x['calls'] == '2' and x['injected'] == '2'


def eg(x):
    return x['ret'] == '0' and x['calls'] == '1' and x['injected'] == '0' and x['canary_ok'] == '1'


for path, form in ((sys.argv[1], 'd'), (sys.argv[2], '0')):
    rows = list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t'))
    n = collections.Counter((x['entry_name'], x['arm']) for x in rows)
    good = collections.Counter()
    for x in rows:
        k = (x['entry_name'], x['arm'])
        if x['arm'] == 'A':
            good[k] += (a_d if form == 'd' else a_0)(x)
        elif x['arm'] in 'EG':
            good[k] += eg(x)
    entries = sorted({x['entry_name'] for x in rows}, key=lambda e: [x['entry_name'] for x in rows].index(e))
    print('== %s form %s rows %d entries %d' % (path, form, len(rows), len(entries)))
    for e in entries:
        line = '  %-32s' % e + ' '.join('%s %d' % (a, n[(e, a)]) for a in 'AKZETG')
        line += ' | A ok %d/%d E ok %d/%d G ok %d/%d' % (good[(e, 'A')], n[(e, 'A')], good[(e, 'E')], n[(e, 'E')], good[(e, 'G')], n[(e, 'G')])
        print(line)
        cond = n[(e, 'A')] >= 200 and n[(e, 'E')] >= 50 and n[(e, 'G')] >= 50 and good[(e, 'A')] == n[(e, 'A')] and good[(e, 'E')] == n[(e, 'E')] and good[(e, 'G')] == n[(e, 'G')]
        ok &= cond
    ok &= len(entries) == 6
print('RECOUNT ALL OK' if ok else 'RECOUNT NOT OK')
sys.exit(0 if ok else 1)
