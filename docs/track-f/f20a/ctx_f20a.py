# F20a (HPP-551): context table - the B2 game moment (idx 770..782 after the first scene frame of Sky Garden) in every
# unique log without validation and RenderDoc, by binary: entries that reach idx 782, entries with a frame >= 100 ms
# there, the interval marks of those frames and the gate schedule of the tag json.
# Usage: python ctx_f20a.py [dir]
import collections, json, re, sys
D = (sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f20a').rstrip('/') + '/'
COURSE = ('9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987', 'adb0c82f')
FX = re.compile(r'/[^/]*fx[^/]*/')
meta = {}
for l in open(D + 'meta_f20a.jsonl', encoding='utf-8'):
    r = json.loads(l)
    meta[r['path']] = r
recs = [json.loads(l) for l in open(D + 'sweep_all.jsonl', encoding='utf-8')]
seen = set()
tab = collections.OrderedDict()
for r in sorted(recs, key=lambda r: r['path']):
    if r['sha256'] in seen or FX.search(r['path']):
        continue
    seen.add(r['sha256'])
    m = meta[r['path']]
    b = (m['binary_sha256'] or 'none')[:8]
    if m['validation'] != 'false' or m['rd'] or r['cnt']['vk'] >= 100:
        continue
    for i, s in enumerate(r['scenes']):
        if s['level'] != 'underwater_aerial_garden' or s['first_n'] is None or s['frames'] < 782:
            continue
        hits = [x for x in r['slow'] if x['scene'] == i and x['q'] == 0 and 770 <= x['idx'] <= 782]
        e = tab.setdefault(b, {'n': 0, 'k': 0, 'rows': [], 'sess': set()})
        e['n'] += 1
        e['k'] += bool(hits)
        e['sess'].add(r['path'].split('/')[2])
        for x in hits:
            env = m['env'] or {}
            e['rows'].append('%s idx %d n %d dt_us %d prio %d/%d ir %d pcs %d sched %s' % (r['path'].replace('C:/kyty/', ''), x['idx'], x['n'], x['dt_us'], x['prio'], x['prio_us'], x['ir'], x['pcs'],
                                                                                 env.get('KYTY_GATE_SCHEDULE', '-')))
print('binary | course | roots | Sky Garden entries that reach idx 782 | with a frame >= 100 ms at idx 770..782')
tn = tk = 0
for b, e in sorted(tab.items(), key=lambda kv: (kv[0] not in COURSE, -kv[1]['k'], kv[0])):
    print('%s | %s | %s | %d | %d' % (b, 'yes' if b in COURSE else 'no', ','.join(sorted(e['sess'])), e['n'], e['k']))
    for x in e['rows']:
        print('      ' + x)
    if b not in COURSE:
        tn += e['n']
        tk += e['k']
print('other binaries together: entries %d, with the frame %d' % (tn, tk))
