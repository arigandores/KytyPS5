"""M1a (HPP-835): build docs/track-m/m1/ from the worker tables (C:/kyty/m657/m1a/agents/*.tsv, merged_raw.json),
commits.json, overlap.tsv. Output to C:/kyty/m657/m1a/out/ (copied into the repo by a separate command)."""
import json, csv, collections, os, re, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
D = 'C:/kyty/m657/m1a/'
O = D + 'out/'
os.makedirs(O, exist_ok=True)
C = json.load(open(D + 'commits.json', encoding='utf-8'))
R = json.load(open(D + 'merged_raw.json', encoding='utf-8'))
order = list(C.keys())
ov = collections.defaultdict(list)
for r in csv.DictReader(open(D + 'overlap.tsv', encoding='utf-8'), delimiter='\t'):
    ov[r['sha']].append(r)
SIGX = {'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 'src/graphics/guest_gpu/gpu_format.h',
        'src/graphics/guest_gpu/gpu_defs.h', 'src/graphics/host_gpu/renderer/image/imageInfo.h'}
def is_sig(p):
    return (p.startswith('src/graphics/shader/') and p.rsplit('.', 1)[-1] in ('cpp', 'h', 'inc')) or p in SIGX
LINE = re.compile(r'b3dc9c67:([^:\s]+):(\d+)')
CLS_ORDER = ['А', 'В′', 'В', 'Б', 'Д', 'Г']
# theme numbering by first appearance in upstream order
tid = collections.OrderedDict()
for h in order:
    k = R[h]['theme']
    if k not in tid:
        tid[k] = 'T%03d' % (len(tid) + 1)
themes = collections.OrderedDict((k, []) for k in tid)
for h in order:
    themes[R[h]['theme']].append(h)
def clean(s):
    return s.replace('|', '/').replace('\t', ' ').strip()
def knob_hits(h):
    out = []
    for r in ov.get(h, []):
        if r['file'].startswith('tests/'):
            continue
        if r['our_knob_hunks_hit'] not in ('0', 'file_not_in_base'):
            out.append('%s: %s' % (r['file'].rsplit('/', 1)[-1], r['our_knob_hunks_hit']))
    return out
def knob_files(h):
    return sorted(set(r['file'] for r in ov.get(h, []) if not r['file'].startswith('tests/')))
# ---- upstream.tsv (machine table: sha, тема, класс, файлы)
with open(O + 'upstream.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('sha\tтема\tкласс\tфайлы\n')
    for h in order:
        f.write('%s\t%s\t%s\t%s\n' % (h, tid[R[h]['theme']], R[h]['class'], ';'.join(C[h]['files'])))
# ---- upstream_detail.tsv
cols = ['sha', 'тема', 'ключ', 'класс', 'подпись', 'файлы_ручек', 'наши_ханки_ручек_задеты', 'заголовок', 'суть', 'основание',
        'якорь', 'якорь_плюс1', 'наша_правка', 'довод_ASTRO', 'увер', 'корзина']
with open(O + 'upstream_detail.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\t'.join(cols) + '\n')
    for h in order:
        v = R[h]
        row = [h, tid[v['theme']], v['theme'], v['class'], 'да' if any(is_sig(p) for p in C[h]['files']) else 'нет',
               ';'.join(knob_files(h)) or '-', ';'.join(knob_hits(h)) or '-', C[h]['subject'], v['essence'], v['basis'],
               v['anchor'], v['anchor_plus1'], v['knob_note'], v['relevance'], v['conf'], v['bucket']]
        f.write('\t'.join(x.replace('\t', ' ').replace('\n', ' ') for x in row) + '\n')
# ---- theme summaries
TS = collections.OrderedDict()
for k, hs in themes.items():
    vs = [R[h] for h in hs]
    cls = vs[0]['class']
    sig = any(is_sig(p) for h in hs for p in C[h]['files'])
    base = next((v for v in vs if LINE.search(v['basis'])), None) or next((v for v in vs if v['basis'].strip() not in ('-', '')), None)
    confs = set(v['conf'] for v in vs)
    conf = 'U' if 'U' in confs else ('I' if 'I' in confs else 'c')
    kf = sorted(set(f for h in hs for f in knob_files(h)))
    kh = sorted(set(x for h in hs for x in knob_hits(h)))
    notes = []
    for v in vs:
        n = v['knob_note'].strip()
        if n not in ('-', '') and n not in notes:
            notes.append(n)
    TS[k] = dict(id=tid[k], key=k, title=vs[0]['theme_title'], cls=cls, hs=hs, sig=sig, base=base, conf=conf, kf=kf, kh=kh,
                 notes=notes, rel=vs[0]['relevance'], ess=[v['essence'] for v in vs])
cnt_c = collections.Counter(R[h]['class'] for h in order)
cnt_t = collections.Counter(t['cls'] for t in TS.values())
json.dump({k: dict(t, base=(t['base']['basis'] if t['base'] else '-')) for k, t in TS.items()},
          open(D + 'themes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('themes', len(TS), dict(cnt_t), 'commits', dict(cnt_c))
print('sig themes', sum(1 for t in TS.values() if t['sig']), 'sig commits', sum(1 for h in order if any(is_sig(p) for p in C[h]['files'])))
print('knob themes', sum(1 for t in TS.values() if t['kf']), 'knob-hunk themes', sum(1 for t in TS.values() if t['kh']))
