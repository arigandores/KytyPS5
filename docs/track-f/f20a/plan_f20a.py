# F20a (HPP-551): the sweep plan from meta_f20a.jsonl -> plan_sweep.tsv ('path <TAB> size <TAB> sweep') and
# plan_hash.tsv ('path <TAB> size <TAB> hash').
# 'sweep' - a candidate of the sample: the binary of the tag json is one of the eight of item 451(e), no validation, no
# RenderDoc, and the guest command line is '-lvl underwater_aerial_garden', '-lvl intro_next' or carries no '-lvl' (the
# default boot passes intro_next).  Every other log is only hashed (the count by distinct sha256).
# Usage: python plan_f20a.py <meta.jsonl> <plan_sweep.tsv> <plan_hash.tsv>
import collections, json, sys

meta, ps, ph = sys.argv[1], sys.argv[2], sys.argv[3]
COURSE = ('9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987', 'adb0c82f')
TAB = chr(9)
recs = [json.loads(l) for l in open(meta, encoding='utf-8') if l.startswith('{')]
sw, hs = [], []
why = collections.Counter()
for r in recs:
    b = (r['binary_sha256'] or '')[:8]
    ga = r['guest_args'] or ''
    lvl = ga.split('-lvl', 1)[1].split()[0] if '-lvl' in ga and ga.split('-lvl', 1)[1].split() else None
    if not b:
        k = 'no json / no binary'
    elif b not in COURSE:
        k = 'binary not of the course line'
    elif r['validation'] != 'false':
        k = 'validation'
    elif r['rd']:
        k = 'RenderDoc'
    elif lvl not in (None, 'underwater_aerial_garden', 'intro_next'):
        k = 'other level by -lvl'
    else:
        k = 'sweep'
    why[k] += 1
    (sw if k == 'sweep' else hs).append(r)
for name, rows, mode in ((ps, sw, 'sweep'), (ph, hs, 'hash')):
    rows.sort(key=lambda r: (r['path'].endswith('.xz'), r['size'], r['path']))
    with open(name, 'w', encoding='utf-8', newline=chr(10)) as f:
        for r in rows:
            f.write('%s%s%d%s%s%s' % (r['path'], TAB, r['size'], TAB, mode, chr(10)))
print('logs', len(recs), dict(why))
print('sweep', len(sw), 'GiB %.1f' % (sum(r['size'] for r in sw) / 2.0 ** 30), 'hash', len(hs), 'GiB %.1f' % (sum(r['size'] for r in hs) / 2.0 ** 30))
print('sweep by binary', collections.Counter((r['binary_sha256'] or '')[:8] for r in sw).most_common())
