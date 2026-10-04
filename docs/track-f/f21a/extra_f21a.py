# F21a (HPP-563): extra numbers for the report from sweep_all.jsonl / meta_f21a.jsonl (same classes as ana_f21a.py):
# levels by binary group, the context logs with stub lines, the user's play log, the logs with input, the position
# of the saturation, the kinds of the other 'CsPretranslate: ' lines.  Usage: python extra_f21a.py [dir]
import collections, json, re, sys

D = (sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f21a').rstrip('/') + '/'
COURSE = ['9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987', 'adb0c82f']
ON = COURSE[2:]
FXC = re.compile('/[^/]*fx[^/]*/')
recs = {}
for l in open(D + 'sweep_all.jsonl', encoding='utf-8'):
    r = json.loads(l)
    recs[r['path']] = r
meta = {}
for l in open(D + 'meta_f21a.jsonl', encoding='utf-8'):
    m = json.loads(l)
    meta[m['path']] = m
groups = collections.OrderedDict()
for p in sorted(recs):
    groups.setdefault(recs[p].get('sha256_text') or recs[p]['sha256'], []).append(p)
S, O = [], []
for sha, paths in groups.items():
    m = next((meta[p] for p in paths if meta[p].get('binary_sha256')), None)
    b = m['binary_sha256'][:8] if m else '-'
    L = {'paths': paths, 'rec': recs[paths[0]], 'bin': b, 'env': (m.get('env') or {}) if m else {}, 'meta': m}
    if m and b in COURSE and not all(FXC.search(p) for p in paths) and L['env'].get('KYTY_FIX_B9A') != '0':
        S.append(L)
    else:
        O.append(L)
print('sample logs', len(S))
for b in COURSE:
    G = [L for L in S if L['bin'] == b]
    lv = set(x['level'] for L in G for x in L['rec']['levels'])
    print('  %s logs %d levels %d frame hours %.2f stub lines %d' % (b, len(G), len(lv), sum(L['rec']['ft_us'] for L in G) / 3.6e9, sum(L['rec']['stub_lines'] for L in G)))
on = [L for L in S if L['bin'] in ON]
lv_on = sorted(set(x['level'] for L in on for x in L['rec']['levels']))
print('binaries with the default KYTY_FIX_B9A=1: logs %d, levels %d %s, frame hours %.2f, stub lines %d' % (len(on), len(lv_on), lv_on,
      sum(L['rec']['ft_us'] for L in on) / 3.6e9, sum(L['rec']['stub_lines'] for L in on)))
off = [L for L in S if L['bin'] not in ON]
lv_off = set(x['level'] for L in off for x in L['rec']['levels'])
print('binaries without the B9a fix (9235a7ac, dac02fb9): logs %d, levels %d, frame hours %.2f, stub lines %d' % (len(off), len(lv_off),
      sum(L['rec']['ft_us'] for L in off) / 3.6e9, sum(L['rec']['stub_lines'] for L in off)))
print('sample logs with >= 1 named level', sum(1 for L in S if L['rec']['levels']), '; with >= 2 named levels', sum(1 for L in S if len(L['rec']['levels']) >= 2),
      '; logs by number of named levels', dict(collections.Counter(len(L['rec']['levels']) for L in S)))
print('sample logs with KYTY_KEYS:', [(L['bin'], L['paths'][0].replace('C:/kyty/', ''), [x['level'] for x in L['rec']['levels']]) for L in S if 'KYTY_KEYS' in L['env']])
print('saturated sample logs: line of the level / first stub line / last stub index / lines of the log / frames after the level line')
for L in S:
    r = L['rec']
    if r['stub_lines'] >= 1024:
        print('  ', L['bin'], L['paths'][0].replace('C:/kyty/', ''), r['levels'][0]['line'], min(s['first_line'] for s in r['stub']),
              r['stub_max_idx'], r['lines'], r['levels'][0]['frames'], ' '.join('%s:%d' % (s['nid'], s['n']) for s in r['stub']))
print('context logs (outside the sample) with stub lines:')
for L in O:
    r = L['rec']
    if r['stub_lines']:
        print('  ', L['bin'], L['paths'][0].replace('C:/kyty/', ''), r['stub_lines'], [x['level'] for x in r['levels']],
              'KYTY_FIX_B9A', L['env'].get('KYTY_FIX_B9A'), ' '.join('%s:%d' % (s['nid'], s['n']) for s in r['stub']))
print('context logs with KYTY_FIX_B9A in env:', collections.Counter((L['bin'], L['env'].get('KYTY_FIX_B9A')) for L in O if 'KYTY_FIX_B9A' in L['env']))
for L in O:
    if '/play/' in L['paths'][0]:
        r = L['rec']
        print('play log:', L['paths'][0].replace('C:/kyty/', ''), 'lines', r['lines'], 'ft', r['ft_n'], 'frame s %.1f' % (r['ft_us'] / 1e6), 'stub', r['stub_lines'],
              'levels', [(x['level'], round(x['sum_us'] / 1e6, 1)) for x in r['levels']], 'rel_plt', r['rel_plt'], 'b9a', r['b9a_first'],
              'cs_req', len(r['cs_req']), 'cfg_out', r['cfg_out'], 'skipped', len(r['cs_skipped']))
print('cs_other lines (sample):', sum(L['rec']['cs_other'] for L in S), '; cs_enq', sum(L['rec']['cs_enq'] for L in S), '; logs with a summary line',
      sum(1 for L in S if L['rec']['cs_summary']))
print('miss reasons (sample, first reason per hash per log):', dict(collections.Counter(v[3] for L in S for v in L['rec']['cs_req'].values() if v[0])))
print('sample logs with miss|hit by binary and validation:', dict(collections.Counter((L['bin'], L['meta'].get('validation')) for L in S if L['rec']['cs_req'])))
print('all-level union over ALL distinct logs:', len(set(x['level'] for L in S + O for x in L['rec']['levels'])))
