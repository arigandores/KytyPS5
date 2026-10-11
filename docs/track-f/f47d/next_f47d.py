"""Track F link F47d (HPP-809; ROADMAP s122 item 708 (b)(6), (g)(1)-(4)): the machine rules of the snapshot series, checked by
launch_f47d.sh and go_f47d.sh BEFORE the lock (constants named in the seal before the data).  ASCII only.

  --may <tag>   may this tag start now?  exit 0 (prints 'MAY ...'), 2 the tag exists, 7 not yet / order, 11 repeat rule, 12 lock budget
  --grid        the grid of f47_rd2: R = floor(713.0 + 0.1075 * n0 + 0.5) of the ADMITTED f47_rd attempt; R-16, R-13, ..., R+17 (12 values);
                exit 7 when there is no admitted f47_rd attempt or its n0 is missing
  --budget      the lock time spent (sum of 'lock taken' / 'lock released' pairs of runs/lock.log)
  --runs <dir>  the runs folder (default C:/kyty/f287/f47d/runs; fixtures use their own)

RULES
  attempts of a base B (f47_rd, f47_rd2, f47_hi): B, B_r1, B_r2, B_r3 in this order; a made attempt is a folder runs/<name> (folders moved
    aside by go_f47d.sh with a suffix .busy_ / .lock_ / .gone_ / .user_ / .session_ / .dispoff_ / .nostart_ / .binchg_ are not attempts);
    every made attempt must be read (runs/<name>/read.json) before the next one.  Status ADMITTED ends the base; NOT_ADMITTED counts
    (one repeat: a second NOT_ADMITTED - no more attempts, question to the lead, item 708 (g)(3)); INTERFERENCE does not count (item 273
    (z)); at most 4 attempts.
  order: f47_rd first.  f47_rd2 - only when f47_rd is ADMITTED and its detector G on the thumbnails gives 0 black captures, or with
    F47D_RD2_OK=1 set after the times.txt line of the lead's item (F47e found no capture with G', item 708 (g)(1)); f47_rd2 runs once
    per series.  f47_hi - when f47_rd is ADMITTED and, if f47_rd2 is due by G (0 black), after f47_rd2 is ADMITTED or exhausted.
  budget (item 708 (g)(4)): spent + estimate <= 2 700 s, the estimate of a tag = the longest lock span of the same kind (rd: f47_rd*,
    hi: f47_hi*) made in this series, else 1 200 s (rd) / 720 s (hi); a 'lock taken' without its 'released' - refusal (exit 12).
  lead admission (item 731 (v), KytyPS5 72cf927e): F47D_RD_ADMIT_LEAD=f47_rd, set only after the times.txt line of item 731, makes the
    NOT_ADMITTED attempt f47_rd count as admitted (read.json is not rewritten): the base f47_rd ends (f47_rd_r1 refused 11), f47_hi and
    --grid use it; any other value of the variable does nothing.
  lead admission (item 734 (v), KytyPS5 a3fea4dd): F47D_HI_ADMIT_LEAD=f47_hi, set only after the times.txt line of item 734, makes the
    INTERFERENCE attempt f47_hi count as admitted (read.json is not rewritten): the base f47_hi ends (f47_hi_r1 refused 11), the series
    F47d ends; any other value of the variable, or the variable on another tag or status, does nothing.  f47_rd2 keeps its own rule
    (F47D_RD2_OK=1 only by a lead's item).
"""
import json
import math
import os
import re
import sys
from datetime import datetime

G = 'C:/kyty/f287/f47d'
BUDGET_S = 2700
EST = {'rd': 1200, 'hi': 720}
P_A, P_B = 713.0, 0.1075
BASES = ('f47_rd', 'f47_rd2', 'f47_hi')


def kind(b):
    return 'hi' if b == 'f47_hi' else 'rd'


def names(b):
    return [b] + ['%s_r%d' % (b, i) for i in (1, 2, 3)]


def status(runs, name):
    d = os.path.join(runs, name)
    if not os.path.isdir(d):
        return None
    js = os.path.join(d, 'read.json')
    if not os.path.exists(js):
        return 'UNREAD'
    try:
        return json.load(open(js, encoding='ascii')).get('status') or 'UNREAD'
    except (ValueError, OSError):
        return 'UNREAD'


def chain(runs, b):
    out = []
    for n in names(b):
        s = status(runs, n)
        if s is None:
            break
        out.append((n, s))
    return out


# the only attempts the lead admitted: base -> (variable, the status it admits, item)
LEAD_ADMIT = {'f47_rd': ('F47D_RD_ADMIT_LEAD', 'NOT_ADMITTED', '731'),
              'f47_hi': ('F47D_HI_ADMIT_LEAD', 'INTERFERENCE', '734')}


def lead_admitted(runs, b):
    if b not in LEAD_ADMIT:
        return False
    var, st, _ = LEAD_ADMIT[b]
    return os.environ.get(var) == b and status(runs, b) == st


def admitted(runs, b):
    for n, s in chain(runs, b):
        if s == 'ADMITTED':
            return n
    if lead_admitted(runs, b):
        return b
    return None


def exhausted(runs, b):
    c = chain(runs, b)
    return sum(1 for n, s in c if s == 'NOT_ADMITTED') >= 2 or len(c) >= 4


def read_json(runs, name):
    try:
        return json.load(open(os.path.join(runs, name, 'read.json'), encoding='ascii'))
    except (ValueError, OSError):
        return None


def g_black(runs, name):
    r = read_json(runs, name) or {}
    return (r.get('rows') or {}).get('G_black')


def lock_spans(runs):
    spans, open_ = [], {}
    p = os.path.join(runs, 'lock.log')
    if not os.path.exists(p):
        return spans, None
    for ln in open(p, encoding='ascii', errors='replace'):
        m = re.match(r'^lock (taken|released) (\S+) (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\s*$', ln.strip())
        if not m:
            continue
        t = datetime.strptime(m.group(3), '%Y-%m-%dT%H:%M:%SZ')
        if m.group(1) == 'taken':
            open_[m.group(2)] = t
        elif m.group(2) in open_:
            spans.append((m.group(2), (t - open_.pop(m.group(2))).total_seconds()))
    return spans, (sorted(open_) or None)


def budget(runs, b):
    spans, op = lock_spans(runs)
    spent = sum(s for _, s in spans)
    same = [s for n, s in spans if kind(re.sub(r'_r[1-3]$', '', n)) == kind(b)]
    est = max(same) if same else EST[kind(b)]
    return spent, est, op


def rd2_due(runs):
    a = admitted(runs, 'f47_rd')
    if a is None:
        return False
    return g_black(runs, a) == 0 or os.environ.get('F47D_RD2_OK') == '1'


def may(runs, tag):
    b = re.sub(r'_r[1-3]$', '', tag)
    if b not in BASES:
        return 2, 'usage'
    if os.path.isdir(os.path.join(runs, tag)):
        return 2, '%s exists - a tag runs once' % tag
    c = chain(runs, b)
    if any(s == 'UNREAD' for n, s in c):
        return 7, 'an attempt of %s is not read yet (%s)' % (b, c)
    if any(s == 'ADMITTED' for n, s in c):
        return 11, '%s already ADMITTED (%s)' % (b, c)
    if lead_admitted(runs, b):
        var, _, item = LEAD_ADMIT[b]
        end = '; series F47d ends' if b == 'f47_hi' else ''
        return 11, '%s admitted by the lead (%s, item %s)%s (%s)' % (b, var, item, end, c)
    if sum(1 for n, s in c if s == 'NOT_ADMITTED') >= 2:
        return 11, '%s: two NOT_ADMITTED - no more attempts, question to the lead (item 708 (g)(3)) (%s)' % (b, c)
    want = names(b)[len(c)] if len(c) < 4 else None
    if want != tag:
        return 11, 'the next attempt of %s is %s, not %s (%s)' % (b, want, tag, c)
    if b == 'f47_rd2':
        a = admitted(runs, 'f47_rd')
        if a is None:
            return 7, 'f47_rd2 needs an ADMITTED f47_rd'
        if not rd2_due(runs):
            return 7, 'f47_rd2 is not due: G black of %s = %s and F47D_RD2_OK is not 1 (item 708 (g)(1))' % (a, g_black(runs, a))
    if b == 'f47_hi':
        a = admitted(runs, 'f47_rd')
        if a is None:
            return 7, 'f47_hi waits for an ADMITTED f47_rd'
        if g_black(runs, a) == 0 and admitted(runs, 'f47_rd2') is None and not exhausted(runs, 'f47_rd2'):
            return 7, 'f47_hi waits for f47_rd2 (G black of %s = 0)' % a
    spent, est, op = budget(runs, b)
    if op:
        return 12, 'lock taken without released in lock.log: %s - question to the lead' % op
    if spent + est > BUDGET_S:
        return 12, 'lock budget: spent %d s + estimate %d s > %d s (item 708 (g)(4)) - stop, question to the lead' % (spent, est, BUDGET_S)
    return 0, 'MAY %s (attempts %s; lock spent %d s, estimate %d s, budget %d s)' % (tag, c, spent, est, BUDGET_S)


def grid(runs):
    a = admitted(runs, 'f47_rd')
    if a is None:
        return 7, 'no ADMITTED f47_rd attempt'
    n0 = ((read_json(runs, a) or {}).get('rows') or {}).get('n0')
    if n0 is None:
        return 7, 'n0 of %s missing' % a
    r = int(math.floor(P_A + P_B * n0 + 0.5))
    return 0, ','.join(str(r - 16 + 3 * k) for k in range(12))


def main(argv):
    runs = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
    if '--may' in argv:
        rc, msg = may(runs, argv[argv.index('--may') + 1])
    elif '--grid' in argv:
        rc, msg = grid(runs)
    elif '--budget' in argv:
        spans, op = lock_spans(runs)
        rc, msg = 0, 'lock spent %d s over %d tags; open %s; spans %s' % (sum(s for _, s in spans), len(spans), op, spans)
    else:
        print(__doc__)
        return 2
    print(msg)
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
