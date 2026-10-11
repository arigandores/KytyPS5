"""F42a (HPP-779, ROADMAP s122 item 694(g)(1)): recount of the counted stand from the TSV rows (not from the F20Stand:
sum lines) and the members of (g)(1) - no verdict of the row. Per row: lost = expected_bits - seen_bits (identity);
per mode and arm: rounds, sums. Members: =0 W lost > 0 (positive control), S lost = 0 (zero control), X - reading line;
=1 W, X, S lost = 0 in every round; N - unmatched >= 1 at =1 (form line); extra = 0 everywhere; out_nonzero = 0
everywhere; form line of each arm: wave 32, subgroup 32, local 64x1x1, returns_main 1, valid 1, and at =1 the rewritten
arms sites = rewritten = 1. Also the sum lines of the .out.txt must equal the recount.
Usage: python sum_stand_f42a.py <dir with m0.tsv m1.tsv m0.out.txt m1.out.txt>. Prints ALL OK / FAIL."""
import re
import sys
from collections import defaultdict

D = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f42a/stand/c42001'
ok = True
sums = {}
for m in ('0', '1'):
    rows = [l.rstrip('\n').split('\t') for l in open('%s/m%s.tsv' % (D, m), encoding='utf-8')]
    hdr, rows = rows[0], rows[1:]
    ix = {k: i for i, k in enumerate(hdr)}
    acc = defaultdict(lambda: defaultdict(int))
    ident_bad = 0
    for r in rows:
        a = r[ix['arm']]
        e, s, lo = int(r[ix['expected_bits']]), int(r[ix['seen_bits']]), int(r[ix['lost']])
        ident_bad += (lo != e - s)
        acc[a]['rounds'] += 1
        acc[a]['rounds_with_loss'] += lo > 0
        for k in ('expected_bits', 'seen_bits', 'lost', 'extra', 'words_lost', 'out_nonzero'):
            acc[a][k] += int(r[ix[k]])
        if r[ix['mode']] != m:
            ident_bad += 1
    print('mode=%s rows %d identity lost=expected-seen violated %d' % (m, len(rows), ident_bad))
    ok &= ident_bad == 0
    for a in ('W', 'X', 'S', 'N'):
        v = acc[a]
        print('  arm %s rounds %d expected %d seen %d lost %d rounds_with_loss %d extra %d words_lost %d out_nonzero %d' % (
            a, v['rounds'], v['expected_bits'], v['seen_bits'], v['lost'], v['rounds_with_loss'], v['extra'],
            v['words_lost'], v['out_nonzero']))
        ok &= v['rounds'] == 200 and v['extra'] == 0 and v['out_nonzero'] == 0
    sums[m] = acc
    # sum lines and form lines of the process output
    out = open('%s/m%s.out.txt' % (D, m), encoding='utf-8', errors='replace').read()
    for line in out.splitlines():
        g = re.search(r'F20Stand: sum mode=(\d) seed=(\d+) arm=(\w) rounds=(\d+) expected_bits=(\d+) lost=(\d+) '
                      r'rounds_with_loss=(\d+) extra=(\d+) words_lost=(\d+) out_nonzero=(\d+)', line)
        if g:
            a = g.group(3)
            same = (int(g.group(4)), int(g.group(5)), int(g.group(6)), int(g.group(7)), int(g.group(8)),
                    int(g.group(9)), int(g.group(10))) == (acc[a]['rounds'], acc[a]['expected_bits'], acc[a]['lost'],
                                                         acc[a]['rounds_with_loss'], acc[a]['extra'],
                                                         acc[a]['words_lost'], acc[a]['out_nonzero'])
            print('  sum line arm %s seed %s = recount: %s' % (a, g.group(2), same))
            ok &= same and g.group(2) == '42001'
        f = re.search(r'F20Stand: form mode=(\d) arm=(\w) wave=(\d+) subgroup=(\d+) .* local=(\S+) .* returns_main=(\d+) '
                      r'bound=(\d) named=(\d) sites=(\d+) rewritten=(\d+) unmatched=(\d+) malformed=(\d) valid=(\d)', line)
        if f:
            a = f.group(2)
            good = f.group(3) == '32' and f.group(4) == '32' and f.group(5) == '64x1x1' and f.group(6) == '1' \
                and f.group(12) == '0' and f.group(13) == '1'
            if a == 'N':
                good &= f.group(8) == '0' and int(f.group(11)) >= 1
            else:
                good &= f.group(8) == '1' and f.group(9) == '1' and f.group(10) == '1' and f.group(11) == '0'
            print('  form arm %s: wave %s subgroup %s local %s returns_main %s named %s sites %s rewritten %s unmatched %s '
                  'valid %s -> %s' % (a, f.group(3), f.group(4), f.group(5), f.group(6), f.group(8), f.group(9),
                                      f.group(10), f.group(11), f.group(13), 'ok' if good else 'BAD'))
            ok &= good
z, o = sums['0'], sums['1']
mem = [
    ('=0 W lost > 0 (positive control)', z['W']['lost'] > 0),
    ('=0 S lost = 0 (zero control)', z['S']['lost'] == 0),
    ('=1 W lost = 0 in every round', o['W']['rounds_with_loss'] == 0),
    ('=1 X lost = 0 in every round', o['X']['rounds_with_loss'] == 0),
    ('=1 S lost = 0 in every round', o['S']['rounds_with_loss'] == 0),
]
for name, v in mem:
    print('member %-36s %s' % (name, 'yes' if v else 'NO'))
print('reading line: =0 X lost %d of %d (%d rounds with loss); =1 N lost %d of %d (not rewritten, unmatched >= 1)' % (
    z['X']['lost'], z['X']['expected_bits'], z['X']['rounds_with_loss'], o['N']['lost'], o['N']['expected_bits']))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
