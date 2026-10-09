"""Track F link F30f (HPP-711; ROADMAP s122 item 643 (d)(2), (9), (11), (12), (14); seal sections 3, 5): the planner of the series - reads
runs/<tag>/read.json of every made tag and prints the next tag to launch, or WAIT / STOP / DONE.  Read only; not a member.  ASCII only.

Rules (in this order):
  STOP     the file SERIES_STOP or RETURN_FAILED exists -> 'STOP <reason>'.
  READ     a made tag without read.json -> 'READ <tag>' (post_f30f.sh first).
  scene    s1..s9 in order; per scene c3 -> c4 -> v (item 643 (d)(2)).  c3: ADMITTED with (K) YES -> c4; ADMITTED with (K) NO (dead) or
           NOT_ADMITTED (executor variant B3) -> the scene drops (c4 and v are not launched); INTERFERENCE -> the scene waits for the lead's
           repeat item (item 643 (d)(12)), the series goes on with the next scene.  c4: any read status -> v (a c4 NOT_ADMITTED is a question
           to the lead, not a stop - variant B2; '=4 dead' does not stop the series, item 643 (d)(14)).  v: INTERFERENCE -> waits for the lead.
           A repeat _r<n> made by the lead's item replaces the interfered tag (the latest made attempt counts).
  reserve  after s1..s9: (a) v2 for s6, s7, s8 whose v is ADMITTED and not OLD by (O) (at most 3); (b) intro_next (in_c3 -> in_c4 ->
           in_v) once, when a scene dropped (item 643 (d)(11)).
  limit    33 made tags that are not interferences (item 643 (d)(11)) -> 'LIMIT'.
  DONE     nothing left; 'WAIT <tags>' when only interfered tags wait for the lead.
usage: python next_f30f.py [--runs <dir>]"""
import json
import os
import re
import sys

G = 'C:/kyty/f287/f30f'
SCENES = ['s%d' % i for i in range(1, 10)]
TAG_RX = re.compile(r'^f30_(s[1-9]|in)_(c3|c4|v|v2)(_r([1-3]))?$')
LIMIT = 33


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


def latest(made, scene, kind):
    """(tag, read) of the latest made attempt of scene/kind, or (None, None)."""
    best = None
    for rep in ('', '_r1', '_r2', '_r3'):
        t = 'f30_%s_%s%s' % (scene, kind, rep)
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
    waits = []
    dropped = []
    v2_want = []

    def nxt(t):
        if used >= LIMIT:
            return 'LIMIT %d made tags' % used
        return 'NEXT %s' % t

    for sc in SCENES:
        t3, r3 = latest(made, sc, 'c3')
        if t3 is None:
            return nxt('f30_%s_c3' % sc)
        if r3['status'] == 'INTERFERENCE':
            waits.append(t3)
            continue
        if r3['status'] != 'ADMITTED' or not member(r3, 0):
            dropped.append(sc)
            continue
        t4, r4 = latest(made, sc, 'c4')
        if t4 is None:
            return nxt('f30_%s_c4' % sc)
        if r4['status'] == 'INTERFERENCE':
            waits.append(t4)
        tv, rv = latest(made, sc, 'v')
        if tv is None:
            return nxt('f30_%s_v' % sc)
        if rv['status'] == 'INTERFERENCE':
            waits.append(tv)
            continue
        if sc in ('s6', 's7', 's8') and rv['status'] == 'ADMITTED' and not member(rv, 3):
            v2_want.append(sc)
    for sc in v2_want[:3]:
        t2, r2 = latest(made, sc, 'v2')
        if t2 is None:
            return nxt('f30_%s_v2' % sc)
        if r2['status'] == 'INTERFERENCE':
            waits.append(t2)
    if dropped:
        t3, r3 = latest(made, 'in', 'c3')
        if t3 is None:
            return nxt('f30_in_c3')
        if r3['status'] == 'INTERFERENCE':
            waits.append(t3)
        elif r3['status'] == 'ADMITTED' and member(r3, 0):
            t4, r4 = latest(made, 'in', 'c4')
            if t4 is None:
                return nxt('f30_in_c4')
            if r4['status'] == 'INTERFERENCE':
                waits.append(t4)
            tv, rv = latest(made, 'in', 'v')
            if tv is None:
                return nxt('f30_in_v')
            if rv['status'] == 'INTERFERENCE':
                waits.append(tv)
    if waits:
        return 'WAIT lead repeat item for %s (dropped %s)' % (' '.join(waits), ' '.join(dropped) or '-')
    return 'DONE made %d (dropped %s, v2 %s)' % (used, ' '.join(dropped) or '-', ' '.join(v2_want) or '-')


def main(argv):
    rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
    print(plan(rd))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
