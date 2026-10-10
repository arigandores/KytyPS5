"""F33a: summary of the stand TSVs (runs/stand_<arm>.tsv) - per arm and per position; prints ALL OK at the end if every
row has the arm's expected count of seeds and the per-row invariants hold (k1 = crash|hang|second; no leftover)."""
import csv
import collections
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f33a/runs'
EXPECT = {'P': 600, 'R': 600, 'C': 50, 'N': 50}
ok = True
for arm in ['P', 'R', 'C', 'N']:
    rows = list(csv.DictReader(open('%s/stand_%s.tsv' % (BASE, arm), encoding='utf-8'), delimiter='\t'))
    seeds = sorted(int(r['seed']) for r in rows)
    if seeds != list(range(1, EXPECT[arm] + 1)):
        print('arm', arm, 'seeds mismatch', len(seeds))
        ok = False
    c = collections.Counter()
    rcs = collections.Counter()
    for r in rows:
        for k in ['control', 'hang', 'crash', 'second', 'k1', 'fatal_text', 'abort', 'leftover']:
            c[k] += int(r[k])
        c['ctrl0_k1'] += int(r['control'] == '0' and r['k1'] == '1')
        rcs[r['rc_hex'] or 'timeout'] += 1
        if int(r['k1']) != int(int(r['crash']) or int(r['hang']) or int(r['second'])):
            ok = False
            print('k1 invariant broken', arm, r['seed'])
        if int(r['leftover']) != 0:
            ok = False
    dur = sorted(float(r['dur_s']) for r in rows)
    print('arm %s N=%d control=%d k1=%d second=%d crash=%d hang=%d abort=%d fatal_text=%d leftover=%d k1_with_control0=%d '
          'rc=%s dur_med=%.3f dur_max=%.3f' % (arm, len(rows), c['control'], c['k1'], c['second'], c['crash'], c['hang'],
                                               c['abort'], c['fatal_text'], c['leftover'], c['ctrl0_k1'],
                                               dict(rcs), dur[len(dur) // 2], dur[-1]))
    if arm in ('P', 'R'):
        bypos = collections.defaultdict(collections.Counter)
        for r in rows:
            p = int(r['pos'])
            bypos[p]['n'] += 1
            bypos[p]['control'] += int(r['control'])
            bypos[p]['second'] += int(r['second'])
            bypos[p]['crash'] += int(r['crash'])
            bypos[p]['hang'] += int(r['hang'])
            bypos[p]['rc321'] += int(r['rc_hex'] == '0x00000141')
            bypos[p]['guest_full'] += int(r['guest_cbs'] == '5')
        for p in sorted(bypos):
            b = bypos[p]
            print('   pos %2d n=%d control=%d second=%d crash=%d hang=%d rc321=%d guest_cbs5=%d' %
                  (p, b['n'], b['control'], b['second'], b['crash'], b['hang'], b['rc321'], b['guest_full']))
print('ALL OK' if ok else 'NOT OK')
