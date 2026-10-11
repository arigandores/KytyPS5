"""F42a2 (HPP-805, ROADMAP s122 item 705(b)(1), (3)): recount of the stand edition 2 from the TSV rows (not from the
F20Stand: sum lines) and the members of item 694(g)(1) with 705(b)(1) - no verdict of the row. Copy of sum_stand_f42a.py
extended by the arms E-W, E-X (the module from the emulator's CreateCachedModule) and the FixF20 counters of the process.
Per row: lost = expected_bits - seen_bits (identity); per mode and arm: rounds, sums.
Members: =0 - W lost > 0 (positive control), S lost = 0 (zero control), E-W lost > 0 summed over R (positive control of
arm E), calls = 0 (emu lines and emu_stat); X, E-X - reading lines.
=1 - W, X, S, E-W, E-X lost = 0 in every round; N unmatched >= 1 (form line); calls >= 1, rewritten >= 1 (emu_stat).
Everywhere: extra = 0, out_nonzero = 0, rounds = R; emu_mode of every emu line = mode (FixF20::Mode() of the process =
the TSV mode). Form line of each arm: wave 32, subgroup 32, local 64x1x1, returns_main 1, valid 1; arms other than N
named 1, sites 1, rewritten 1, unmatched 0 (the words of E are the translation - the form line counts the triple the
emulator's Apply rewrites); N named 0, unmatched >= 1. The sum lines of the .out.txt must equal the recount.
Also printed (not members, for the mutants of F42b2): m1b caught = (=1 E-W or E-X lost > 0); m6 caught = (=0 calls > 0
or E-W lost = 0).
Usage: python sum_stand_f42a2.py <dir with m0.tsv m1.tsv m0.out.txt m1.out.txt> <seed> [R]. Prints ALL OK / FAIL."""
import re
import sys
from collections import defaultdict

D = sys.argv[1]
SEED = sys.argv[2]
R = int(sys.argv[3]) if len(sys.argv) > 3 else 200
ARMS = ('W', 'X', 'S', 'N', 'E-W', 'E-X')
ok = True
sums = {}
emu = {}
for m in ('0', '1'):
    rows = [l.rstrip('\n').split('\t') for l in open('%s/m%s.tsv' % (D, m), encoding='utf-8')]
    hdr, rows = rows[0], rows[1:]
    ix = {k: i for i, k in enumerate(hdr)}
    acc = defaultdict(lambda: defaultdict(int))
    bad = 0
    for r in rows:
        a = r[ix['arm']]
        e, s, lo = int(r[ix['expected_bits']]), int(r[ix['seen_bits']]), int(r[ix['lost']])
        bad += (lo != e - s)
        bad += r[ix['mode']] != m or r[ix['seed']] != SEED or a not in ARMS
        acc[a]['rounds'] += 1
        acc[a]['rounds_with_loss'] += lo > 0
        for k in ('expected_bits', 'seen_bits', 'lost', 'extra', 'words_lost', 'out_nonzero'):
            acc[a][k] += int(r[ix[k]])
    print('mode=%s rows %d (expected %d) identity/mode/seed/arm violations %d' % (m, len(rows), R * len(ARMS), bad))
    ok &= bad == 0 and len(rows) == R * len(ARMS)
    for a in ARMS:
        v = acc[a]
        print('  arm %-3s rounds %d expected %d seen %d lost %d rounds_with_loss %d extra %d words_lost %d out_nonzero %d'
              % (a, v['rounds'], v['expected_bits'], v['seen_bits'], v['lost'], v['rounds_with_loss'], v['extra'],
                 v['words_lost'], v['out_nonzero']))
        ok &= v['rounds'] == R and v['extra'] == 0 and v['out_nonzero'] == 0
    sums[m] = acc
    out = open('%s/m%s.out.txt' % (D, m), encoding='utf-8', errors='replace').read()
    seen_sum, seen_form, ev = set(), set(), {}
    stat = None
    for line in out.splitlines():
        g = re.search(r'F20Stand: sum mode=(\d) seed=(\d+) arm=(\S+) rounds=(\d+) expected_bits=(\d+) lost=(\d+) '
                      r'rounds_with_loss=(\d+) extra=(\d+) words_lost=(\d+) out_nonzero=(\d+)', line)
        if g:
            a = g.group(3)
            same = (int(g.group(4)), int(g.group(5)), int(g.group(6)), int(g.group(7)), int(g.group(8)),
                    int(g.group(9)), int(g.group(10))) == (acc[a]['rounds'], acc[a]['expected_bits'], acc[a]['lost'],
                                                         acc[a]['rounds_with_loss'], acc[a]['extra'],
                                                         acc[a]['words_lost'], acc[a]['out_nonzero'])
            print('  sum line arm %s seed %s = recount: %s' % (a, g.group(2), same))
            ok &= same and g.group(1) == m and g.group(2) == SEED
            seen_sum.add(a)
        f = re.search(r'F20Stand: form mode=(\d) arm=(\S+) wave=(\d+) subgroup=(\d+) .* local=(\S+) .* returns_main=(\d+) '
                      r'bound=(\d) named=(\d) sites=(\d+) rewritten=(\d+) unmatched=(\d+) malformed=(\d) valid=(\d)', line)
        if f:
            a = f.group(2)
            good = f.group(1) == m and f.group(3) == '32' and f.group(4) == '32' and f.group(5) == '64x1x1' \
                and f.group(6) == '1' and f.group(12) == '0' and f.group(13) == '1'
            if a == 'N':
                good &= f.group(8) == '0' and int(f.group(11)) >= 1
            else:
                good &= f.group(8) == '1' and f.group(9) == '1' and f.group(10) == '1' and f.group(11) == '0'
            print('  form arm %-3s: wave %s subgroup %s local %s returns_main %s bound %s named %s sites %s rewritten %s '
                  'unmatched %s valid %s -> %s' % (a, f.group(3), f.group(4), f.group(5), f.group(6), f.group(7),
                                                   f.group(8), f.group(9), f.group(10), f.group(11), f.group(13),
                                                   'ok' if good else 'BAD'))
            ok &= good
            seen_form.add(a)
        e = re.search(r'F20Stand: emu mode=(\d) emu_mode=(\d) arm=(\S+) bound_flag=1 calls=(\d+) rewritten=(\d+) '
                      r'module=(\d)', line)
        if e:
            a = e.group(3)
            ev[a] = (int(e.group(4)), int(e.group(5)))
            good = e.group(1) == m and e.group(2) == m and e.group(6) == '1' and a in ('E-W', 'E-X')
            print('  emu line arm %s: emu_mode %s calls %s rewritten %s module %s -> %s' % (
                a, e.group(2), e.group(4), e.group(5), e.group(6), 'ok' if good else 'BAD'))
            ok &= good
        s = re.search(r'F20Stand: emu_stat mode=(\d) emu_mode=(\d) calls=(\d+) rewritten=(\d+)', line)
        if s:
            stat = (int(s.group(3)), int(s.group(4)))
            print('  emu_stat: emu_mode %s calls %s rewritten %s' % (s.group(2), s.group(3), s.group(4)))
            ok &= s.group(1) == m and s.group(2) == m
    done = 'F20Stand: done' in out
    complete = seen_sum == set(ARMS) and seen_form == set(ARMS) and set(ev) == {'E-W', 'E-X'} and stat is not None
    print('  lines complete (sum, form 6 arms; emu E-W, E-X; emu_stat; done): %s' % (complete and done))
    ok &= complete and done
    emu[m] = (ev, stat)
z, o = sums['0'], sums['1']
zs, os_ = emu['0'][1] or (-1, -1), emu['1'][1] or (-1, -1)
zev, oev = emu['0'][0], emu['1'][0]
mem = [
    ('=0 W lost > 0 (positive control)', z['W']['lost'] > 0),
    ('=0 S lost = 0 (zero control)', z['S']['lost'] == 0),
    ('=0 E-W lost > 0 summed over R (positive control E)', z['E-W']['lost'] > 0),
    ('=0 calls = 0 (emu_stat and emu lines)', zs[0] == 0 and all(v[0] == 0 for v in zev.values())),
    ('=1 W lost = 0 in every round', o['W']['rounds_with_loss'] == 0),
    ('=1 X lost = 0 in every round', o['X']['rounds_with_loss'] == 0),
    ('=1 S lost = 0 in every round', o['S']['rounds_with_loss'] == 0),
    ('=1 E-W lost = 0 in every round', o['E-W']['rounds_with_loss'] == 0),
    ('=1 E-X lost = 0 in every round', o['E-X']['rounds_with_loss'] == 0),
    ('=1 calls >= 1 (emu_stat)', os_[0] >= 1),
    ('=1 rewritten >= 1 (emu_stat)', os_[1] >= 1),
    ('extra = 0 everywhere', all(sums[m][a]['extra'] == 0 for m in sums for a in ARMS)),
]
for name, v in mem:
    print('member %-52s %s' % (name, 'yes' if v else 'NO'))
    ok &= v
print('reading line: =0 X lost %d of %d (%d rounds with loss); =0 E-X lost %d of %d (%d rounds); '
      '=1 N lost %d of %d (not rewritten, unmatched >= 1)' % (
          z['X']['lost'], z['X']['expected_bits'], z['X']['rounds_with_loss'], z['E-X']['lost'],
          z['E-X']['expected_bits'], z['E-X']['rounds_with_loss'], o['N']['lost'], o['N']['expected_bits']))
print('mutant reading (not members): m1b caught %s; m6 caught %s' % (
    o['E-W']['lost'] > 0 or o['E-X']['lost'] > 0, zs[0] > 0 or z['E-W']['lost'] == 0))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
