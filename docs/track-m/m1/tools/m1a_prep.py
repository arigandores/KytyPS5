import collections, json
D = 'C:/kyty/m657/m1a/'
subj = {}
order = []
for l in open(D + 'subjects.tsv', encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    subj[p[0]] = p
    order.append(p[0])
files = collections.OrderedDict()
cur = None
for l in open(D + 'files_raw.txt', encoding='utf-8'):
    l = l.rstrip('\n')
    if not l:
        continue
    if l.startswith('@@'):
        cur = l[2:]
        files[cur] = []
        continue
    parts = l.split('\t')
    st = parts[0]
    path = parts[-1]
    files[cur].append((st, path, parts[1] if len(parts) > 2 else ''))
knob = set(x.strip() for x in open(D + 'knobfiles.txt', encoding='utf-8') if x.strip())
ours = set(x.strip() for x in open(D + 'ourtree.txt', encoding='utf-8'))
SIGX = {'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 'src/graphics/guest_gpu/gpu_format.h',
        'src/graphics/guest_gpu/gpu_defs.h', 'src/graphics/host_gpu/renderer/image/imageInfo.h'}
def is_sig(p):
    return (p.startswith('src/graphics/shader/') and p.rsplit('.', 1)[-1] in ('cpp', 'h', 'inc')) or p in SIGX
out = {}
for h in order:
    fl = files[h]
    paths = [p for _, p, _ in fl]
    out[h] = dict(sha=h, date=subj[h][1], author=subj[h][2], subject=subj[h][3], files=paths,
                  knob=sorted(set(p for p in paths if p in knob)),
                  sig=any(is_sig(p) for p in paths),
                  missing=sorted(set(p for st, p, _ in fl if p not in ours and not st.startswith('A'))),
                  added=[p for st, p, _ in fl if st.startswith('A')])
json.dump(out, open(D + 'commits.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(out), 'commits;', sum(1 for v in out.values() if v['knob']), 'touch knob files;',
      sum(1 for v in out.values() if v['sig']), 'touch signature set;',
      sum(1 for v in out.values() if v['missing']), 'touch paths missing in ours')
top = collections.Counter()
for v in out.values():
    for p in v['files']:
        top['/'.join(p.split('/')[:3])] += 1
for k, n in top.most_common(40):
    print(n, k)
miss = collections.Counter(p for v in out.values() for p in v['missing'])
print('missing paths:', len(miss))
for k, n in miss.most_common(30):
    print(' ', n, k)
