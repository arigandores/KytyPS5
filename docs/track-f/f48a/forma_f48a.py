# F48a (HPP-830): parking condition of the F5 remainder (register s67:1093: 'остаток ветви 2 паркуется до ключа формы (А) в
# сцене при KYTY_DIAG_F5ID=1') checked on every delta log that carries 'DiagF5Id: mode=1'.  Form (A) of branch 2 =
# ROADMAP p.492(d)(1): key (base, dcc, reason) with entry in {PendingDcc, Dcc}, clear_mask != 0, dcc_en = 1 and the next
# consumer 'fce_next' kind in {texture, target} with cleared = 0.  'In the scene' = after the first 'Level has started' line.
# Two readings are printed (the event lines are deduplicated - first 4 events of a key in full, p.492(g)(1)):
#   (E) full event lines 'DiagF5Id: fce' in the scene with the form-(A) fields, paired with the next 'fce_next' of the same
#       base after the event (the line order of the log);
#   (K) key counters 'DiagF5Id: key site=fce ...': per key, n of the last key line against the full event lines of the key
#       (printed before / after the scene line).  A key has no event in the scene when n_last = printed_before (every event
#       printed in full and all before the scene); 'unplaced' = n_last - printed events (events 5.. of a key are not printed,
#       their time is unknown) - such a key is 'not determined' unless the growth of n after the scene is 0.  Key lines are
#       printed by the summary ('sum') at most once per 600 frames, so a first key line after the scene line does not
#       place its events in the scene.
# Usage: python forma_f48a.py <log> [<log> ...]   (exit 3 lock, 4 STOP; read-only)
import os, re, sys

LOCK = os.environ.get('F48A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F48A_STOP', 'C:/kyty/f287/STOP')
KV = re.compile(rb'(\w+)=(\S+)')


def gate():
    if os.path.exists(STOP):
        sys.exit(4)
    if os.path.exists(LOCK):
        sys.exit(3)


def scan(path):
    gate()
    lvl = None
    armed = False
    ev = []      # (line, base, key, fields)
    nxt = []     # (line, base, kind, cleared)
    keys_pre, keys_last = {}, {}
    with open(path, 'rb') as f:
        for i, l in enumerate(f, 1):
            if i % 2000000 == 0:
                gate()
            if lvl is None and b'Level has started' in l:
                lvl = i
            if not l.startswith(b'DiagF5Id: '):
                continue
            kind = l.split()[1]
            d = dict((k.decode(), v.decode('utf-8', 'replace')) for k, v in KV.findall(l))
            if kind == b'mode=1':
                armed = True
            elif kind == b'fce':
                ev.append((i, d.get('base'), (d.get('base'), d.get('dcc'), d.get('reason')), d))
            elif kind == b'fce_next':
                nxt.append((i, d.get('base'), d.get('kind'), d.get('cleared')))
            elif kind == b'key' and d.get('site') == 'fce':
                k = (d.get('base'), d.get('dcc'), d.get('reason'))
                v = (int(d.get('n', 0)), int(d.get('texture', 0)) + int(d.get('target', 0)) - int(d.get('cleared', 0)))
                if lvl is None:
                    keys_pre[k] = v
                keys_last[k] = v
    return lvl, armed, ev, nxt, keys_pre, keys_last


def form_a(d, nx):
    return (d.get('entry') in ('PendingDcc', 'Dcc') and d.get('clear_mask', '0x0') not in ('0x0', '0x00000000', '0')
            and d.get('dcc_en') == '1' and nx is not None and nx[2] in ('texture', 'target') and nx[3] == '0')


def main():
    tot_e = tot_k = 0
    for p in sys.argv[1:]:
        lvl, armed, ev, nxt, kp, kl = scan(p)
        if not armed:
            print(p, 'not armed (no DiagF5Id: mode=1)')
            continue
        scene_ev = [e for e in ev if lvl is not None and e[0] > lvl]
        a_e = []
        for e in scene_ev:
            nx = next((x for x in nxt if x[0] > e[0] and x[1] == e[1]), None)
            if form_a(e[3], nx):
                a_e.append((e[0], e[2], nx[0]))
        a_k = []
        grow = 0
        und = 0
        for k, v in kl.items():
            pb = sum(1 for e in ev if e[2] == k and (lvl is None or e[0] <= lvl))
            pa = sum(1 for e in ev if e[2] == k and lvl is not None and e[0] > lvl)
            if pa:
                grow += 1
            elif v[0] > pb:
                v0 = kp.get(k, (pb, 0))
                if v[0] > max(v0[0], pb):
                    und += 1
                    a_k.append((k, pb, v))
        tot_e += len(a_e)
        tot_k += und
        print('%s level_line %s | fce events printed %d (in scene %d) | form (A) by events %d %s | keys %d, with printed events in '
              'scene %d, with unplaced events (n_last > printed before, growth unknown) %d %s' % (p, lvl, len(ev), len(scene_ev), len(a_e),
              a_e[:2], len(kl), grow, und, a_k[:3]))
    print('TOTAL form (A) in scene by full event lines', tot_e, '| keys with unplaced events (not determined)', tot_k)
    print('ALL OK')


if __name__ == '__main__':
    main()
