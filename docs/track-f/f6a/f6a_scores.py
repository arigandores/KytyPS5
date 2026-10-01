# F6a (HPP-372): field 'stubs' of the score json of sessions 142-144 (written by the session scorers) - which levels call
# unresolved import stubs. No logs are read.
import json, glob, os, hashlib
tot = 0; hit = []
for d in ('C:/kyty/s142/runs142', 'C:/kyty/s143/runs143', 'C:/kyty/s144/runs144'):
    fs = sorted(glob.glob(d + '/*.score.json'))
    for f in fs:
        j = json.load(open(f, encoding='utf-8'))
        tot += 1
        st = j.get('stubs')
        nz = st if not isinstance(st, dict) else {k: v for k, v in st.items() if v}
        if nz: hit.append((os.path.basename(f), j.get('level'), json.dumps(nz, ensure_ascii=False)[:300]))
    print('%s: %d score files' % (d, len(fs)))
print('score files %d, with non-empty stubs %d' % (tot, len(hit)))
for h in hit: print('  %s %s %s' % h)
