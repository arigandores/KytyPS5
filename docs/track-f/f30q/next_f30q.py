"""Track F link F30q (HPP-727; ROADMAP s122 item 664 (z)(2), (3), (5); item 665 (v); seal section 5): the planner of the series - reads
runs/<tag>/read.json of every made tag and runs/lock.log, prints the next tag to launch, or WAIT / STOP / HOLD / DONE / BUDGET / LIMIT.
Read only; not a member.  Port of next_f30m.py (F30m).  ASCII only.

Rules (in this order):
  STOP     the file SERIES_STOP or RETURN_FAILED exists -> 'STOP <reason>'.
  READ     a made tag without read.json -> 'READ <tag>' (post_f30q.sh first).
  (W)      first f30_s1_w6 (item 664 (z)(2)).  ADMITTED with every member YES -> the c6 tags; INTERFERENCE -> waits for the lead's repeat
           item; any other outcome (NOT_ADMITTED, a member NO - [Vulkan][E] > 0, a stop by the validation, sum rts_inj = 0, RC1-RC4 of item
           665 (v)) -> 'HOLD' - series stop and the lead's item (item 664 (z)(2), 665 (v)(1)); no c6 tag before it.
  (c6)     s1..s9 in order, one tag f30_s<k>_c6 each (item 664 (z)(3)); any read status but INTERFERENCE -> the next scene (a NOT_ADMITTED
           c6 without a STOP row is a question to the lead, the series goes on; the STOP rows of the reader - post_f30q.sh writes
           SERIES_STOP); INTERFERENCE -> waits for the lead's repeat item (item 664 (z)(5)).  A repeat _r<n> made by the lead's item replaces
           the interfered tag (the latest made attempt counts).
  limit    10 made tags that are not interferences -> 'LIMIT' (item 664 (z)(5): 10 tags, one attempt each).
  budget   item 664 (z)(5): the lock time of the series (pairs of runs/lock.log) + the estimate of the next tag (480 s at w6, 420 s at c6 -
           the F30m c5 tags took 373-426 s of lock) > 5400 s -> 'BUDGET'.
  DONE     nothing left; 'WAIT <tags>' when only interfered tags wait for the lead.
usage: python next_f30q.py [--runs <dir>]"""
import datetime
import json
import os
import re
import sys

G = 'C:/kyty/f287/f30q'
SCENES = ['s%d' % i for i in range(1, 10)]
TAG_RX = re.compile(r'^f30_(?:(s1)_(w6)|(s[1-9])_(c6))(_r([1-3]))?$')
LIMIT = 10
BUDGET_S = 5400
EST = {'w6': 480, 'c6': 420}


def load(rd):
    made = {}
    for t in os.listdir(rd) if os.path.isdir(rd) else []:
        m = TAG_RX.match(t)
        if not m or not os.path.isdir(os.path.join(rd, t)):
            continue
        js = os.path.join(rd, t, 'read.json')
        r = json.load(open(js, encoding='utf-8')) if os.path.exists(js) else None
        made[t] = r
    return made


def lock_seconds(rd):
    """Sum of the 'lock taken' -> 'lock released' pairs of runs/lock.log (an open pair counts nothing)."""
    p = os.path.join(rd, 'lock.log')
    total = 0.0
    taken = {}
    if os.path.exists(p):
        for line in open(p, encoding='ascii', errors='replace').read().splitlines():
            f = line.split()
            if len(f) != 4 or f[0] != 'lock':
                continue
            try:
                ts = datetime.datetime.strptime(f[3], '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                continue
            if f[1] == 'taken':
                taken[f[2]] = ts
            elif f[1] == 'released' and f[2] in taken:
                total += (ts - taken.pop(f[2])).total_seconds()
    return total


def latest(made, base):
    best = None
    for rep in ('', '_r1', '_r2', '_r3'):
        t = base + rep
        if t in made:
            best = t
    return (best, made[best]) if best else (None, None)


def member(r, i):
    return r is not None and r.get('members') is not None and len(r['members']) > i and r['members'][i][1]


def plan(rd, stop_dir=None):
    sd = stop_dir or os.path.dirname(rd.rstrip('/\\'))
    for f in ('SERIES_STOP', 'RETURN_FAILED'):
        p = os.path.join(sd, f)
        if os.path.exists(p):
            return 'STOP %s: %s' % (f, open(p, encoding='ascii', errors='replace').readline().strip()[:200])
    made = load(rd)
    for t, r in sorted(made.items()):
        if r is None:
            return 'READ %s' % t
    used = sum(1 for r in made.values() if r.get('status') != 'INTERFERENCE')
    lock_s = lock_seconds(rd)
    waits = []
    notes = []

    def nxt(t, kind):
        if used >= LIMIT:
            return 'LIMIT %d made tags' % used
        if lock_s + EST[kind] > BUDGET_S:
            return 'BUDGET lock %d s + estimate %d s of %s > %d s (item 664 (z)(5))' % (lock_s, EST[kind], t, BUDGET_S)
        return 'NEXT %s' % t

    tw, rw = latest(made, 'f30_s1_w6')
    if tw is None:
        return nxt('f30_s1_w6', 'w6')
    if rw['status'] == 'INTERFERENCE':
        return 'WAIT lead repeat item for %s (item 664 (z)(5))' % tw
    if rw['status'] != 'ADMITTED' or not all(b for a, b in (rw.get('members') or [['none', False]])):
        return 'HOLD %s %s members %s - series stop and the lead item (item 664 (z)(2), 665 (v)(1))' % (
            tw, rw['status'], [a[:60] for a, b in (rw.get('members') or []) if not b][:3])
    for sc in SCENES:
        t6, r6 = latest(made, 'f30_%s_c6' % sc)
        if t6 is None:
            return nxt('f30_%s_c6' % sc, 'c6')
        if r6['status'] == 'INTERFERENCE':
            waits.append(t6)
        elif r6['status'] != 'ADMITTED':
            notes.append('%s %s' % (t6, r6['status']))
    if waits:
        return 'WAIT lead repeat item for %s (%s)' % (' '.join(waits), '; '.join(notes) or '-')
    return 'DONE made %d, lock %d s (%s)' % (used, lock_s, '; '.join(notes) or '-')


def main(argv):
    rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
    print(plan(rd))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
