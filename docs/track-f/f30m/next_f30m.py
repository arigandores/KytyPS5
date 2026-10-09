"""Track F link F30m (HPP-723; ROADMAP s122 item 655 (e)(2), (3), (5); seal section 5): the planner of the series - reads
runs/<tag>/read.json of every made tag and runs/lock.log, prints the next tag to launch, or WAIT / STOP / DONE / BUDGET.  Read only; not a
member.  Port of next_f30f.py (F30f).  ASCII only.

Rules (in this order):
  STOP     the file SERIES_STOP or RETURN_FAILED exists -> 'STOP <reason>'.
  READ     a made tag without read.json -> 'READ <tag>' (post_f30m.sh first).
  (eps)    s1..s9 in order, one tag f30_s<k>_c5 each (item 655 (e)(2)); any read status but INTERFERENCE -> the next scene (a NOT_ADMITTED
           c5 is a question to the lead, the series goes on); INTERFERENCE -> waits for the lead's repeat item (item 655 (e)(5)).
  (gamma)  then f30_cy_v (item 655 (e)(3)).  ADMITTED with the member (gamma) YES -> f30_cy_c3; ADMITTED with (gamma) NO -> (gamma) is not
           reachable on T2, cy_c3 / cy_c4 are not made, no repeats; NOT_ADMITTED -> cy_c3 / cy_c4 are not made (question to the lead);
           INTERFERENCE -> waits for the lead.  f30_cy_c3: any read status but INTERFERENCE -> f30_cy_c4 (the letter of item 655
           (e)(3): c3 -> c4; a dead (K) is a note - cy is not counted by item 655 (zh)(2)); INTERFERENCE -> waits.
           A repeat _r<n> made by the lead's item replaces the interfered tag (the latest made attempt counts).
  limit    12 made tags that are not interferences -> 'LIMIT'.
  budget   item 655 (e)(5): the lock time of the series (pairs of runs/lock.log) + the estimate of the next tag (450 s with video, 300 s
           without) > 7200 s -> 'BUDGET'.
  DONE     nothing left; 'WAIT <tags>' when only interfered tags wait for the lead.
usage: python next_f30m.py [--runs <dir>]"""
import datetime
import json
import os
import re
import sys

G = 'C:/kyty/f287/f30m'
SCENES = ['s%d' % i for i in range(1, 10)]
TAG_RX = re.compile(r'^f30_(?:(s[1-9])_(c5)|(cy)_(v|c3|c4))(_r([1-3]))?$')
LIMIT = 12
BUDGET_S = 7200
EST = {'v': 450, 'c3': 300, 'c4': 300, 'c5': 300}


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
            return 'BUDGET lock %d s + estimate %d s of %s > %d s (item 655 (e)(5))' % (lock_s, EST[kind], t, BUDGET_S)
        return 'NEXT %s' % t

    for sc in SCENES:
        t5, r5 = latest(made, 'f30_%s_c5' % sc)
        if t5 is None:
            return nxt('f30_%s_c5' % sc, 'c5')
        if r5['status'] == 'INTERFERENCE':
            waits.append(t5)
    tv, rv = latest(made, 'f30_cy_v')
    if tv is None:
        return nxt('f30_cy_v', 'v')
    if rv['status'] == 'INTERFERENCE':
        waits.append(tv)
    elif rv['status'] != 'ADMITTED':
        notes.append('cy_v %s - cy_c3 / cy_c4 not made' % rv['status'])
    elif not member(rv, 0):
        notes.append('(gamma) not reachable on T2 - cy_c3 / cy_c4 not made')
    else:
        t3, r3 = latest(made, 'f30_cy_c3')
        if t3 is None:
            return nxt('f30_cy_c3', 'c3')
        if r3['status'] == 'INTERFERENCE':
            waits.append(t3)
        else:
            if r3['status'] != 'ADMITTED' or not member(r3, 0):
                notes.append('cy_c3 %s (K) %s - cy not counted by item 655 (zh)(2), cy_c4 still made (letter of item 655 (e)(3))' % (
                    r3['status'], member(r3, 0)))
            t4, r4 = latest(made, 'f30_cy_c4')
            if t4 is None:
                return nxt('f30_cy_c4', 'c4')
            if r4['status'] == 'INTERFERENCE':
                waits.append(t4)
    if waits:
        return 'WAIT lead repeat item for %s (%s)' % (' '.join(waits), '; '.join(notes) or '-')
    return 'DONE made %d, lock %d s (%s)' % (used, lock_s, '; '.join(notes) or '-')


def main(argv):
    rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
    print(plan(rd))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
