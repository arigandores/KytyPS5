# Session Auditor s141 step 2: analysis of rc_audit141.json / rc_audit141_census.json (own code). Prints numbers to compare with inventory141 rev.2.
import json, os, collections, sys
L = json.load(open('C:/kyty/s141/step2/rc_audit141.json'))
C = json.load(open('C:/kyty/s141/step2/rc_audit141_census.json'))
def P(*a):
    print(*a)
P('== census', C['census_sha'][:16], 'rows', C['census_rows'])
lv = C['census_levels']
P('census levels:', {k: lv.get(k) for k in ['underwater_aerial_garden', 'ps_logo', 'title_controller_ship', 'intro_next', 'worldmap', 'penguin_atlantis', 'transition_next']})
P('census other level names:', sorted(k for k in lv if k not in ('underwater_aerial_garden', 'ps_logo', 'title_controller_ship', 'intro_next', 'worldmap')))
P('census scene=transition_next:', len(C['census_scene_transition_next']), C['census_scene_transition_next'])
P('census fatal kinds:', C['census_fatal_kinds'], 'total', len(C['census_fatal']))
P('census intro_next s59-113 [runs, --- Error ---]:', C['census_intro_59_113'])
n76, h76 = C['census_sg_76_102']; n103, h103 = C['census_sg_103_113']
P('census SG s76-102 entries', n76, 'hang req<6000', len(h76), [t for s, t, r in h76])
P('census SG s103-113 entries', n103, 'hang req<6000', len(h103))
P('census all GpuHangAbort rows', len(C['census_hang_all']))
for s, t, r, sc in C['census_hang_all']:
    P('   hang', s, t, r, sc)
for s, t, f, sc, l in C['census_fatal']:
    if not f.startswith('GpuHang'):
        P('   fatal', s, t, f[:22], sc)
P('== logs: files', len(L), '(unique by sha)')
def tag(d):
    return os.path.basename(d['p'])[4:-4]
def levels(d):
    return [x for x, _ in d['lv'] if x]
def isval(d):
    return d['vkw'] > 0 or d['vke'] > 0 or tag(d).startswith('s6s')
cnt = collections.Counter()
for d in L.values():
    for x in set(levels(d)):
        cnt[x] += 1
P('logs per started level:', dict(cnt))
P('logs with any started level:', sum(1 for d in L.values() if levels(d)))
# entry analysis per log (target level = last non-empty started level)
def entry(d):
    lvn = levels(d)
    if not lvn:
        return None
    target = lvn[-1]
    idx = max(i for i, (x, _) in enumerate(d['lv']) if x == target)
    ftpos = d['lv'][idx][1]
    ft = d['ft']
    first = None
    for j in range(ftpos, len(ft)):
        if ft[j][2] >= 100:
            first = j
            break
    if first is None:
        return dict(target=target, first=None)
    win = ft[first:first + 600]
    hold = ft[first + 600:]
    mx = max(win, key=lambda r: r[1])
    mx_after = max(win[1:], key=lambda r: r[1]) if len(win) > 1 else None
    return dict(target=target, first=ft[first][0], first_draws=ft[first][2], first_dt=ft[first][1], win_max=(mx[0], mx[1]),
                win_max_excl_first=(mx_after[0], mx_after[1]) if mx_after else None,
                win_ge1s=[(r[0], r[1]) for r in win[1:] if r[1] >= 1_000_000],
                hold_ge100=[(r[0], r[1]) for r in hold if r[1] >= 100_000], hold_ge1s=[(r[0], r[1]) for r in hold if r[1] >= 1_000_000],
                hold_max=max((r[1] for r in hold), default=None), last_n=ft[-1][0], nframes=len(ft))
E = {}
for k, d in L.items():
    E[k] = entry(d)
NAMED = ['eatl122', 'atl122', 'eght122', 'ght122', 'ght123', 'ednn122', 'dnn122', 'edes122', 'des122', 's6s136', 's6s137', 'kp137h']
bytag = {}
for k, d in L.items():
    bytag.setdefault(tag(d), []).append(k)
P('== 12 named logs: first scene frame (draws>=100 after GuestOut target), window-600 max, max excluding the first frame itself')
for t in NAMED:
    for k in bytag.get(t, []):
        e = E[k]; d = L[k]
        P('  %-8s %s s%d %s first n %s draws %s first_dt %s | win max %s | win max excl first %s | win>=1s %s | hold>=1s %s | hold max %s | last n %s | AP %d lines %d frames | MTL>=1s %s' % (
            t, k[:8], d['s'], e and e['target'], e and e['first'], e and e.get('first_draws'), e and e.get('first_dt'), e and e.get('win_max'),
            e and e.get('win_max_excl_first'), e and e.get('win_ge1s'), e and e.get('hold_ge1s'), e and e.get('hold_max'), e and e.get('last_n'),
            d['ap'], d['apf'], d['mtl']))
# vbn113k
for t in ['vbn113k', 'ctl114a']:
    for k in bytag.get(t, []):
        d = L[k]; P('  %s %s s%d frames>=1s %s' % (t, k[:8], d['s'], [(n, dt) for n, dt, dr, _ in d['ft'] if dt >= 1_000_000]))
# B2 form: SG logs, sessions 113-137, not validation, FrameTrace reaching n>=1000
b2 = []; b2base = []
for k, d in L.items():
    if 'underwater_aerial_garden' in levels(d) and 113 <= d['s'] <= 137 and not isval(d) and d['ft'] and d['ft'][-1][0] >= 1000:
        b2base.append(k)
        hits = [(n, dt) for n, dt, dr, _ in d['ft'] if 945 <= n <= 960 and dt >= 100_000]
        if hits:
            b2.append((tag(d), d['s'], hits))
P('== B2 (n 945-960, dt>=100ms): base logs', len(b2base), 'with form', len(b2), sorted(b2, key=lambda x: x[1]))
bys = collections.Counter(L[k]['s'] for k in b2base)
P('   base per session', sorted(bys.items()))
b2n = [x for x in b2 if any(951 <= n <= 954 for n, _ in x[2])]
P('   of them in n 951-954:', len(b2n))
# hold frames >= 100 ms after entry window, all -lvl non-validation logs; with and without the "last 5 frames" exclusion
P('== hold frames >=100 ms after entry window (non-validation), with last-5 exclusion flag')
perlvl = collections.Counter(); perlvl_hit = collections.Counter()
for k, d in sorted(L.items(), key=lambda kv: (kv[1]['s'], tag(kv[1]))):
    e = E[k]
    if not e or e.get('first') is None or isval(d):
        continue
    perlvl[e['target']] += 1
    hh = e['hold_ge100']
    if hh:
        last = e['last_n']
        keep = [(n, dt) for n, dt in hh if n <= last - 5]
        if keep:
            perlvl_hit[e['target']] += 1
        P('  s%d %-10s %s %s n=%d max=%s last=%d excl5=%d %s' % (d['s'], tag(d), k[:8], e['target'], len(hh), max(hh, key=lambda x: x[1]), last,
                                                             len(hh) - len(keep), hh[:4]))
P('  entries per level', dict(perlvl), 'with hold>=100ms (excl last 5)', dict(perlvl_hit))
# B3a: dt>=1s on hold, entries s115-137
ent = [(k, E[k]) for k, d in L.items() if E[k] and E[k].get('first') is not None and 115 <= L[k]['s'] <= 137 and not isval(L[k])]
ge = [(tag(L[k]), e['hold_ge1s']) for k, e in ent if e['hold_ge1s']]
P('== B3a: entries s115-137 non-validation', len(ent), 'with hold dt>=1s', ge)
ent_all = [(k, E[k]) for k, d in L.items() if E[k] and E[k].get('first') is not None and 115 <= L[k]['s'] <= 137]
P('   (all incl. validation)', len(ent_all))
ent113 = [(tag(L[k])) for k, d in L.items() if E[k] and E[k].get('first') is not None and L[k]['s'] == 113]
P('   entries s113:', len(ent113), sorted(ent113))
# B1b trips
sg = [k for k, d in L.items() if 'underwater_aerial_garden' in levels(d) and 113 <= d['s'] <= 137]
P('== B1b: SG logs s113-137', len(sg), 'with BvhLoopCapTrip', sorted((tag(L[k]), L[k]['s'], k[:8]) for k in sg if L[k]['trip']))
P('   SG logs s113-126', sum(1 for k in sg if L[k]['s'] <= 126), 's127-137', sum(1 for k in sg if L[k]['s'] >= 127))
P('   SG logs with GpuHangAbort', [tag(L[k]) for k in sg if L[k]['hang']])
# opcode profile
prof = collections.Counter(json.dumps(d['op'], sort_keys=True) for d in L.values())
P('== opcode profiles:', prof.most_common(6))
# death markers
P('== death markers:', [(tag(d), d['s'], d['fatal'], d['error'], d['hang'], d['dl']) for d in L.values() if d['fatal'] or d['error'] or d['hang'] or d['dl']])
P('   [Vulkan][E] logs:', [(tag(d), d['vke']) for d in L.values() if d['vke']])
# PriorityStall
ps_ent = [(k, d) for k, d in L.items() if E[k] and E[k].get('first') is not None and 113 <= d['s'] <= 137]
nv = [(k, d) for k, d in ps_ent if not isval(d)]
P('== PriorityStall>50ms: entries s113-137', len(ps_ent), 'non-val', len(nv), 'with >50ms', sorted((tag(d), max(d['ps'])) for k, d in nv if d['ps'] and max(d['ps']) > 50000),
  'validation with', sum(1 for k, d in ps_ent if isval(d) and d['ps'] and max(d['ps']) > 50000), 'of', sum(1 for k, d in ps_ent if isval(d)))
P('== dups', C.get('dups'))
