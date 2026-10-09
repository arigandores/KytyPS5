# F31a: census of sweep jsonl files by binary - logs, scene entries, hours of scene by guest frames (sum of dt_us after the
# entry), logs with a B25 signature; totals on the line binaries.  Binary: the tag json binary_sha256 (sha8), else the build
# revision mapped by LINE_REV / OTHER_REV, else 'rev:<7>'.  usage: python bybin_f31a.py <sweep.jsonl> [<sweep.jsonl> ...]
import collections, json, sys
LINE_SHA = {'9235a7ac': 'base128', 'dac02fb9': 'FSc', 'bbad499c': 'FS2', '4aa62e95': 'P23', '540c035a': 'FS3', '31cbfee8': 'FS4',
            '631ff987': 'FS5', 'adb0c82f': 'S12', '9325446c': 'FS6', '8df61c00': 'FS7', '2c9b69b9': 'FS8', 'b3cee576': 'S18',
            '3861eeea': 'FS9', 'abfded5e': 'FS10', 'ea51ae80': 'FS11'}
LINE_REV = {'4fc501f': '9235a7ac', '95eec77': 'dac02fb9', '9c9d86a': 'bbad499c', '4414e23': '4aa62e95', '3d0e46d': '31cbfee8',
            '0e72bc1': '631ff987', '4d9e8ab': 'adb0c82f', '3904522': '9325446c', 'd6ee2dc': '8df61c00', '302347b': '2c9b69b9',
            '0005e11': 'b3cee576', '11164d7': '3861eeea', 'dc5d471': 'abfded5e', 'ee9632b': 'ea51ae80'}
OTHER_REV = {'6fbdcf6': 'bba692c6', 'a1d1d86': '3bc7ada7'}
NAMES = {'bba692c6': 'T2 (F30k)', '3bc7ada7': 'T (F30d)'}


def binof(r):
    sha = (r.get('binary_sha256') or '')[:8]
    b = r.get('build') or ''
    rev = b.split('KytyPS5 ', 1)[1].strip()[:7] if 'KytyPS5 ' in b else None
    if sha:
        return sha
    if rev in LINE_REV:
        return LINE_REV[rev]
    if rev in OTHER_REV:
        return OTHER_REV[rev]
    return 'rev:%s' % rev if rev else '?'


recs = []
for p in sys.argv[1:]:
    recs += [json.loads(l) for l in open(p, encoding='utf-8')]
agg = collections.defaultdict(lambda: [0, 0, 0, 0])  # logs, entries, us, logs with sig
for r in recs:
    b = binof(r)
    a = agg[b]
    a[0] += 1
    a[1] += len(r.get('entries') or [])
    a[2] += sum(e['sum_us'] for e in r.get('entries') or [])
    a[3] += 1 if any(r.get('S') or []) else 0
print('%-14s %-10s %6s %8s %8s %5s' % ('binary', 'name', 'logs', 'entries', 'hours', 'sig'))
tl = [0, 0, 0, 0]
for b, a in sorted(agg.items(), key=lambda kv: -kv[1][2]):
    name = LINE_SHA.get(b, NAMES.get(b, ''))
    print('%-14s %-10s %6d %8d %8.2f %5d' % (b, name, a[0], a[1], a[2] / 3.6e9, a[3]))
    if b in LINE_SHA:
        for i in range(4):
            tl[i] += a[i]
print('line binaries total: logs %d entries %d hours %.2f logs with signature %d' % (tl[0], tl[1], tl[2] / 3.6e9, tl[3]))
print('all: logs %d entries %d hours %.2f logs with signature %d' % (len(recs), sum(a[1] for a in agg.values()),
      sum(a[2] for a in agg.values()) / 3.6e9, sum(a[3] for a in agg.values())))
