"""F23f (HPP-592, ROADMAP s122 item 498(g)(2)-(3)): replay plans (selection rule fixed before any replay data):
  every event of every CS program and of the PS programs whose draws meet RC3(g) by pipeline state (be4c35a2031fd3f4,
  f47c0c097c598a36: blend off and write mask f on every target); for the PS programs that fail RC3(g) by pipeline state
  (255ce6193a9e7938, 2e2ae33a4d374e8f, 74bb8628d64f534c, e14edf4a78d1a517 - blend on; 52276fe1ba080bea - write mask 7) only the
  first event, as data (not valid by (g)). Events and their modules - the replay surveys runs/survey_k05.txt (replay chunk
  indices) and runs/survey_f13.txt (module checked at every event).  Output: plan_k05.json, plan_f13.json."""
import json

D = 'C:/kyty/f287/f23f/'
INVALID_G = {'255ce6193a9e7938', '2e2ae33a4d374e8f', '74bb8628d64f534c', 'e14edf4a78d1a517', '52276fe1ba080bea'}


def events(path):
    ev = []
    for l in open(path):
        if ' EVENT eid' in l:
            f = l.split()
            ev.append(dict(eid=int(f[f.index('eid') + 1]), prog=f[f.index('prog') + 1].split('_')[1], stage=f[f.index('stage') + 1],
                           cap_sha=f[f.index('module_sha') + 1]))
    return ev


def main():
    arms = json.load(open(D + 'arms_f23f.json'))
    sites = json.load(open(D + 'sites_f23f.json'))
    mp = json.load(open(D + 'map_f23f.json'))
    A = {}
    for h, v in arms.items():
        A[h] = {k: D + 'arms/%s_%s_%s.spv' % (v['stage'], h, k) for k in ('def', 'mask', 'mem', 'blend', 'sens')}
        A[h]['sites'] = [[s['sid'], s['cid'], s['nid'], s['oid']] for s in sites[h]['sites']]
        A[h]['diag_var'] = v['diag_var']
        A[h]['diag_var_id'] = v['diag_var_id']
    for cap, path in (('k05', 'runs/survey_k05.txt'), ('f13', 'runs/survey_f13.txt')):
        ev = events(D + path)
        sel, first = [], set()
        for e in ev:
            exp = set(x['sha'] for l in mp[e['prog']]['captures'].values() for x in l)
            assert e['cap_sha'] in exp, e
            if e['prog'] in INVALID_G:
                if e['prog'] in first:
                    continue
                first.add(e['prog'])
                e['valid_g_by_state'] = False
            else:
                e['valid_g_by_state'] = True
            sel.append(e)
        json.dump({'events': sel, 'arms': A}, open(D + 'plan_%s.json' % cap, 'w'), indent=1, sort_keys=True)
        print(cap, 'events', len(sel), 'programs', sorted(set(e['prog'] for e in sel)))


if __name__ == '__main__':
    main()
