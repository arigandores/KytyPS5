# sens137.py - Session Auditor, s.137 step 5: sensitivity rows of the pooled kp137 (never a reading): Delta of pair 1 (k = 2) by
# call, Delta without pairs 0 and 1, Delta of the first / second half of the read pairs of every call.  Reads the json of recount137.
import sys
sys.path.insert(0, 'C:/kyty/s137/audit137')
import json
import recount137 as R

beta = None
allp = []
bb = []
for c in R.CALLS:
    C = json.load(open(R.OUT + c + '.json', encoding='utf-8'))
    allp += R.pairs_of(C)
    bb += [(b['lv']['sxy'], b['lv']['sxx']) for b in C['abba']['blocks'] if b['complete'] and b['arm'] == 0]
beta = sum(a for a, _ in bb) / sum(b for _, b in bb)


def d(p, adj):
    x = p['b1']['dt_us'] - p['b0']['dt_us']
    return x - beta * (p['b1']['draws'] - p['b0']['draws']) if adj else x


new = [p for p in allp if p['mode'] == 'NEW']
print('beta %.4f' % beta)
p1 = [p for p in new if p['k'] == 2]
print('pair 1 (k = 2, order (1,0)) by call: ' + ', '.join('%s %.1f' % (p['call'], d(p, False)) for p in p1) +
      '; mean simple %s adjusted %s' % (R.fmt(R.ms([d(p, False) for p in p1])), R.fmt(R.ms([d(p, True) for p in p1]))))
q = [p for p in new if p['k'] >= 4]
print('without pairs 0 and 1: simple %s adjusted %s' % (R.fmt(R.ms([d(p, False) for p in q])), R.fmt(R.ms([d(p, True) for p in q]))))
h1, h2 = [], []
for c in R.CALLS:
    r = sorted([p for p in new if p['call'] == c and p['k'] != 0], key=lambda p: p['k'])
    h1 += r[:len(r) // 2]
    h2 += r[len(r) // 2:]
for name, h in (('first half', h1), ('second half', h2)):
    print('%s of every call: simple %s adjusted %s' % (name, R.fmt(R.ms([d(p, False) for p in h])), R.fmt(R.ms([d(p, True) for p in h]))))
dh = R.ms([d(p, True) for p in h1])[0] - R.ms([d(p, True) for p in h2])[0]
se = (R.ms([d(p, True) for p in h1])[1] ** 2 + R.ms([d(p, True) for p in h2])[1] ** 2) ** 0.5
print('first - second half adjusted %.1f +- %.1f (2SE)' % (dh, 2 * se))
