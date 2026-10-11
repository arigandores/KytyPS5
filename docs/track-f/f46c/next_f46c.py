"""Track F link F46c (HPP-800; ROADMAP s122 item 702 (g)(2), (g)(4), (g)(6); item 711 (b)(1); item 716): the machine rules of the series
- which tag may be called next, the event rule of the tint tags and the lock budget.  Reads only runs/<tag>/read.json of f46c_read.py and
runs/lock.log.  No verdict.  ASCII only.

    python next_f46c.py --plan [--runs D]           the table of S1..S4 by f26s_1 and the order of the series
    python next_f46c.py --may <tag> [--runs D]      exit 0 MAY; 7 NOT YET (an earlier tag is not settled); 8 EVENT RULE (the tint tags of
                                                    the event are not called); 11 REPEAT RULE; 12 BUDGET (lock sum > limit); 2 usage
    python next_f46c.py --key <k> [--runs D]        prints the key 0x<hex> of S<k> from the admitted f26s_1 attempt; exit 8 when the
                                                    event rule says no
    python next_f46c.py --budget [--runs D] [--extra-s N]   the lock sum of runs/lock.log, exit 12 when > limit

ORDER (item 702 (g)(2)): f26s_0, f26s_1, f26s_1b, then for k = 1..4: f26s_t<k>, f26s_c<k> (only for the events the rule allows).  A tag is
  SETTLED when its read.json says ADMITTED, or its _r1 has a read.json (any status: a second NOT_ADMITTED - the events of the tag are
  'undetermined', item 702 (g)(4)).  A tag may be called when every earlier tag of the order is settled and the tag itself has no runs dir.
REPEAT (item 702 (g)(4), 273 (z)): <tag>_r1 may be called when <tag> has read.json with NOT_ADMITTED and no <tag>_r1 dir; _r2 / _r3 only
  with F46C_REPEAT_OK=1 (an item of the lead; the launcher checks it).  An interference renames the runs dir (go_f46c.sh) and does not
  spend the attempt - the same name runs again.
EVENT RULE (item 702 (g)(2), (d)(2); item 711 (b)(1)): the event S<k> of the SETTLED f26s_1 attempt (the admitted one of f26s_1 /
  f26s_1_r1; none admitted - every event 'undetermined', no tint tag).  The tint tags of S<k> are called only when: the event was found
  after the entry, its class is in {kept_applied, kept why=decode, kept why=deferred}, and it is not NO_APPLY (a mark class without a
  cleared line).  Otherwise the event is 'undetermined' - 'no mark by construction' (class) or 'not distinguishable by construction'
  (NO_APPLY) - and f26s_t<k> / f26s_c<k> are not called.  The key of the tint tags is the dcc of the event in that attempt.
BUDGET (item 716): the sum over runs/lock.log of (released - taken) per 'lock taken <tag> <UTC>' / 'lock released <tag> <UTC>' pair (every
  tag of the series, repeats too); a taken line without a released line counts to now.  > 150 min (9 000 s) - the next tag is not called,
  stop of the series and a question to the lead; 149 min 59 s - goes, 150 min 1 s - stop.
"""
import datetime
import json
import os
import re
import sys

G = 'C:/kyty/f287/f46c'
ALLOWED = ('kept_applied', 'kept why=decode', 'kept why=deferred')
BUDGET_S = 150 * 60
ORDER0 = ['f26s_0', 'f26s_1', 'f26s_1b']
RX_LOCK = re.compile(r'^lock (taken|released) (\S+) (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\s*$')


def load(rd, tag):
    p = os.path.join(rd, tag, 'read.json')
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding='ascii'))


def settled(rd, tag):
    r = load(rd, tag)
    if r is not None and r.get('status') == 'ADMITTED':
        return True, tag
    if r is not None and load(rd, tag + '_r1') is not None:
        r1 = load(rd, tag + '_r1')
        return True, (tag + '_r1') if r1.get('status') == 'ADMITTED' else None
    return False, None


def f26s_1_attempt(rd):
    ok, att = settled(rd, 'f26s_1')
    if not ok:
        return False, None, None
    return True, att, (load(rd, att) if att else None)


def event_rule(rd):
    """[(k, call, key, reason)] for k = 1..4, or None when f26s_1 is not settled."""
    ok, att, r = f26s_1_attempt(rd)
    if not ok:
        return None
    out = []
    evs = dict((e['k'], e) for e in ((r or {}).get('events') or []))
    for k in (1, 2, 3, 4):
        e = evs.get(k)
        if r is None:
            out.append((k, False, None, 'undetermined: f26s_1 not admitted in two attempts (item 702 (g)(4))'))
        elif e is None or not e.get('found'):
            out.append((k, False, None, 'undetermined: event not found after the entry'))
        elif e.get('cls') not in ALLOWED:
            out.append((k, False, None, 'undetermined, no mark by construction: class "%s" (item 711 (b)(1))' % e.get('cls')))
        elif e.get('no_apply'):
            out.append((k, False, None, 'undetermined, not distinguishable by construction: NO_APPLY (item 702 (d)(2))'))
        else:
            out.append((k, True, '0x%x' % int(e['dcc'], 16), 'call: class "%s" (attempt %s)' % (e['cls'], att)))
    return out


def order(rd):
    """The full order of the series as far as it is known (the tint tags only after f26s_1 is settled)."""
    o = list(ORDER0)
    er = event_rule(rd)
    if er is not None:
        for k, call, key, why in er:
            if call:
                o += ['f26s_t%d' % k, 'f26s_c%d' % k]
    return o, er


def lock_sum(rd, now=None):
    pairs = {}
    total = 0
    open_tags = []
    p = os.path.join(rd, 'lock.log')
    lines = open(p, encoding='ascii').read().splitlines() if os.path.exists(p) else []
    cur = {}
    for l in lines:
        m = RX_LOCK.match(l)
        if not m:
            continue
        t = datetime.datetime.strptime(m.group(3), '%Y-%m-%dT%H:%M:%SZ')
        if m.group(1) == 'taken':
            cur[m.group(2)] = t
        elif m.group(2) in cur:
            total += (t - cur.pop(m.group(2))).total_seconds()
            pairs[m.group(2)] = pairs.get(m.group(2), 0) + 1
    now = now or datetime.datetime.utcnow().replace(microsecond=0)
    for tag, t in cur.items():
        total += (now - t).total_seconds()
        open_tags.append(tag)
    return int(total), open_tags


def may(rd, tag, now=None):
    m = re.match(r'^(f26s_0|f26s_1|f26s_1b|f26s_t[1-4]|f26s_c[1-4])(_r([1-3]))?$', tag)
    if not m:
        return 2, 'usage: unknown tag %s' % tag
    s, opn = lock_sum(rd, now)
    if s > BUDGET_S:
        return 12, 'BUDGET: lock sum %d s > %d s (item 716) - stop of the series, question to the lead' % (s, BUDGET_S)
    if opn:
        return 7, 'NOT YET: a lock of %s is open in lock.log' % opn
    base, rep = m.group(1), m.group(3)
    if os.path.isdir(os.path.join(rd, tag)):
        return 7, 'NOT YET: runs/%s exists - a tag runs once' % tag
    if rep is not None:
        prev = base if rep == '1' else '%s_r%d' % (base, int(rep) - 1)
        r = load(rd, prev)
        if r is None or r.get('status') != 'NOT_ADMITTED':
            return 11, 'REPEAT RULE: %s is not NOT_ADMITTED (%s)' % (prev, None if r is None else r.get('status'))
        if rep != '1' and os.environ.get('F46C_REPEAT_OK') != '1':
            return 11, 'REPEAT RULE: %s needs an item of the lead (F46C_REPEAT_OK=1)' % tag
    o, er = order(rd)
    if base.startswith(('f26s_t', 'f26s_c')):
        if er is None:
            return 7, 'NOT YET: f26s_1 is not settled'
        k = int(base[-1])
        call = [x for x in er if x[0] == k][0]
        if not call[1]:
            return 8, 'EVENT RULE: S%d - %s' % (k, call[3])
    if base not in o:
        return 7, 'NOT YET: %s not in the known order %s' % (base, o)
    for t in o[:o.index(base)]:
        if not settled(rd, t)[0]:
            return 7, 'NOT YET: %s is not settled' % t
    if rep is None:
        return 0, 'MAY %s (lock sum %d s of %d)' % (tag, s, BUDGET_S)
    return 0, 'MAY %s repeat (lock sum %d s of %d)' % (tag, s, BUDGET_S)


def main(argv):
    rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
    now = None
    if '--now' in argv:
        now = datetime.datetime.strptime(argv[argv.index('--now') + 1], '%Y-%m-%dT%H:%M:%SZ')
    if '--budget' in argv:
        s, opn = lock_sum(rd, now)
        print('lock sum %d s (%d min %d s) of %d s; open %s; %s' % (s, s // 60, s % 60, BUDGET_S, opn, 'BUDGET OK' if s <= BUDGET_S
                                                                                                   else 'BUDGET EXCEEDED'))
        return 0 if s <= BUDGET_S else 12
    if '--may' in argv:
        rc, msg = may(rd, argv[argv.index('--may') + 1], now)
        print(msg)
        return rc
    if '--key' in argv:
        k = int(argv[argv.index('--key') + 1])
        er = event_rule(rd)
        if er is None:
            print('NOT YET: f26s_1 is not settled')
            return 7
        x = [e for e in er if e[0] == k]
        if not x or not x[0][1]:
            print('EVENT RULE: S%d - %s' % (k, x[0][3] if x else 'no such k'))
            return 8
        print(x[0][2])
        return 0
    if '--plan' in argv:
        o, er = order(rd)
        print('order %s' % o)
        for k, call, key, why in er or []:
            print('S%d %s key %s - %s' % (k, 'CALL' if call else 'NO_CALL', key, why))
        s, opn = lock_sum(rd, now)
        print('lock sum %d s of %d s; open %s' % (s, BUDGET_S, opn))
        return 0
    print(__doc__.split('\n\n')[1])
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
