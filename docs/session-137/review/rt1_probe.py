"""Session 137 step 1 (HPP-251, Red Team): offline probe of the IF5 "snapshot tear" form on the 12 logs of session 136.
Reads the logs only (no game, no code change).  For every tag and identity of smk137.identities():
  (1) non-full rows (not _has3) that carry a nonzero d of the identity - count and sum (they are outside S, inside the tag sums);
  (2) the positive control on real data: a persistent accounting defect of net size E injected at the middle full row
      (d += E there, i.e. S shifted by E from that row on) - the smallest E in 1..80 at which tearform() FAILS by (i)/(ii),
      and the same for a defect spread as +1 on each of E rows starting at the middle;
  (3) the sign of every row with |d| > 32 (the reader reads the bln_* counters in enum order, the flush adds them in enum
      order: a reader-slow tear gives d < 0 for IF5a/IF5b and d > 0 for IF5c).
Imports smk137.py (sha printed) from C:/kyty/s137."""
import hashlib
import sys

sys.path.insert(0, 'C:/kyty/s137')
import smk137 as S  # noqa: E402

print('rt1_probe sha256 %s; smk137 sha256 %s' % (hashlib.sha256(open(__file__, 'rb').read()).hexdigest(),
                                                hashlib.sha256(open('C:/kyty/s137/smk137.py', 'rb').read()).hexdigest()))
for tag, value in S.CAL136:
    p = S.parse('C:/kyty/s136/log_' + tag + '.txt')
    rows = p['rows']
    fr = sorted((r for r in rows.values() if r.get('_has3')), key=lambda x: x.get('n', 0))
    nf = [r for r in rows.values() if not r.get('_has3')]
    abba = value is None
    for key, nm, fn in S.identities(value, abba):
        nfd = [(r.get('n'), fn(r)) for r in nf if fn(r)]
        big = [(r.get('n'), fn(r)) for r in fr if abs(fn(r)) > S.K_RUN]
        mid = len(fr) // 2
        e_step = e_spread = None
        for E in range(1, 81):
            if e_step is None:
                def f1(r, E=E, n0=fr[mid].get('n')):
                    return fn(r) + (E if r.get('n') == n0 else 0)
                if fr and not S.tearform(fr, f1)['ok']:
                    e_step = E
            if e_spread is None:
                ns = set(r.get('n') for r in fr[mid:mid + E])
                def f2(r, ns=ns):
                    return fn(r) + (1 if r.get('n') in ns else 0)
                if fr and not S.tearform(fr, f2)['ok']:
                    e_spread = E
        print('%s %s: full rows %d, non-full rows %d (with d != 0: %d, sum d %d); rows |d| > %d: %s; smallest failing '
              'E - step %s, spread %s' % (tag, key, len(fr), len(nf), len(nfd), sum(d for _, d in nfd), S.K_RUN,
                                          big or 'none', e_step, e_spread))
print('ALL DONE')
