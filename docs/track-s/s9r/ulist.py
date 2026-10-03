"""ulist.py - S9r: the U rule of item 355 (e) recomputed from the own scan (lvl_rest.tsv, lvl_s144.tsv, lvl_s14x.tsv; p283 and
f287 are return roots by item 362 (g) V4 and were not needed for U) and the T2 names over the same scan."""
import sys

SIG = 'KytySC3:56189185f9e9f9a0ea5174f3f85206e6d099db3d:robust:ftz:cbank:fixb26:fixb1b:'
RET = ('C:/kyty/s288/', 'C:/kyty/f287/', 'C:/kyty/p283/', 'C:/kyty/play/', 'C:/kyty/KytyPS5/ps5 em/')
T2 = ('hero_kratos', 'hero_drake', 'voxel_challenge_3', 'armadillo_challenge_2', 'fragile_battle_4', 'voxel_challenge_4',
      'fragile_battle_5', 'voxel_challenge_5', 'miniboss_challenge_genie', 'symbol_triangle')
U = ('underwater_aerial_garden', 'hoover_beach', 'mini_giants_garden', 'robot_builder_next', 'interactive_credit_00',
     'non_interactive_credit', 'ending_boss_after_credit', 'collectible_viewer', 'fragile_battle_1')


def parse(names):
    nm = {}
    if not names or names.startswith('UNREADABLE'):
        return nm
    for x in names.split(';'):
        if '=' in x:
            k, v = x.rsplit('=', 1)
            nm[k] = v
        elif x:
            nm[x] = '?'
    return nm


rows = []
for f in sys.argv[1:]:
    for line in open(f, encoding='utf-8'):
        if line.startswith('#'):
            print(f, line.strip())
            continue
        parts = line.rstrip('\n').split('\t')
        p, size, names, cmp_ = parts[0], parts[1], parts[2], (parts[3] if len(parts) > 3 else '')
        rows.append((p, int(size), parse(names), cmp_))
print('files with a hit', len(rows))
print('T2 names (any file, any extension):')
for lv in T2:
    hit = [p for p, s, nm, c in rows if lv in nm]
    print('  %-26s %d %s' % (lv, len(hit), hit[:4]))
print('compat strings with the signature seen:', sorted(set(c for p, s, nm, c in rows if SIG in c))[:6])
print('U rule (log with the signature, not under a return root, carries the entry line):')
for lv in U:
    q = [p for p, s, nm, c in rows if lv in nm and SIG in c and not p.startswith(RET)]
    allsig = [p for p, s, nm, c in rows if lv in nm and SIG in c]
    print('  %-26s qualifying %d %s; with the signature in any root %d' % (lv, len(q), q[:3], len(allsig)))
