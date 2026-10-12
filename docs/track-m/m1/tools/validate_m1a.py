import csv, glob, collections, json, os
os.chdir('C:/kyty/m657/m1a')
C = json.load(open('commits.json', encoding='utf-8'))
rows = {}
bad = []
for f in sorted(glob.glob('agents/*.tsv')):
    r = list(csv.reader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    hdr = r[0]; body = r[1:]
    b = os.path.basename(f)[:-4]
    exp = [l.split('\t')[0] for l in open('buckets/' + b + '.tsv', encoding='utf-8')]
    got = [x[0] for x in body]
    print(b, len(body), len(exp), got == exp, set(len(x) for x in body), hdr)
    for x in body:
        if x[0] in rows:
            bad.append(('dup', x[0]))
        rows[x[0]] = dict(zip(hdr, x), bucket=b)
print('total', len(rows), 'missing', [h for h in C if h not in rows][:5], 'bad', bad[:5])
cls = collections.Counter(v['class'] for v in rows.values()); print(cls)
th = collections.defaultdict(set)
for v in rows.values():
    th[v['theme']].add(v['class'])
print('themes', len(th), 'multi-class', {k: s for k, s in th.items() if len(s) > 1})
json.dump(rows, open('merged_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
