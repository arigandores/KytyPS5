# F20a (HPP-551): merge of the sweep parts (sweep_f20a.jsonl.p*, sweep_rest.jsonl.p*) into sweep_all.jsonl - one record
# per path, sorted by path.  A path met twice is kept once only when both records are equal member by member (the
# count is printed: two workers of a killed watchdog run outlived the tree kill and wrote the same records again).
# Usage: python merge_f20a.py [dir]
import glob, json, sys

D = (sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f20a').rstrip('/') + '/'
recs = {}
rep = 0
raw = 0
for fn in sorted(glob.glob(D + 'sweep_f20a.jsonl.p*') + glob.glob(D + 'sweep_rest.jsonl.p*')):
    for l in open(fn, encoding='utf-8'):
        if not l.startswith('{'):
            continue
        raw += 1
        r = json.loads(l)
        if r['path'] in recs:
            assert recs[r['path']] == r, r['path']
            rep += 1
        recs[r['path']] = r
with open(D + 'sweep_all.jsonl', 'w', encoding='ascii', newline=chr(10)) as f:
    for p in sorted(recs):
        f.write(json.dumps(recs[p], ensure_ascii=True, sort_keys=True) + chr(10))
print('raw records', raw, 'paths', len(recs), 'repeated equal records', rep)
