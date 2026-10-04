# S14d: offline check RC5(b) of ROADMAP s122 item 423(v)(4) - the hashes of the new shaders of S10 (new_modules_s14d.tsv, written by
# c0_s14d.py) against the index of a translation cache directory (file names <stage>_<hash>_<keyhash>.bin) or of its MANIFEST.txt.
# Usage: rc5b_s14d.py <cache dir | manifest file>.  No game, no code; reads names only.
import sys, os, re, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
src = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(src):
    names = os.listdir(src)
else:
    names = [l.split(' ')[0].split('/')[-1] for l in open(src, encoding='utf-8', errors='replace')]
idx = collections.defaultdict(set)
for n in names:
    m = re.match(r'^(cs|ps|vs)_([0-9a-f]{16})_([0-9a-f]{16})\.bin$', n.strip())
    if m: idx[m.group(1).upper()].add(m.group(2))
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(here, 'new_modules_s14d.tsv'), encoding='utf-8')][1:]
print('index %s: distinct hashes VS %d PS %d' % (src, len(idx['VS']), len(idx['PS'])))
lv = collections.OrderedDict()
for tag, level, st, h, in0, ser in rows:
    d = lv.setdefault((tag, level), dict(new=0, hit=0, base=0, base_hit=0))
    if in0 == '0':
        d['new'] += 1; d['hit'] += 1 if h in idx[st] else 0
    else:
        d['base'] += 1; d['base_hit'] += 1 if h in idx[st] else 0
for (tag, level), d in lv.items():
    letter = 'OUT' if d['hit'] + d['base_hit'] > 0 else 'IN'          # letter of item 423(v)(4): any match drops the level
    var = 'OUT' if d['new'] > 0 and d['hit'] == d['new'] else 'IN'    # executor variant: every hash that was absent from snap0 matches
    print('%s %s: hashes absent from snap0 %d, of them in the index %d; hashes present in snap0 under another key %d, of them in the '
          'index %d -> letter (any match) %s; executor variant (all the absent ones match) %s'
          % (tag, level, d['new'], d['hit'], d['base'], d['base_hit'], letter, var))
tot = sum(d['base'] for d in lv.values()); tot_hit = sum(d['base_hit'] for d in lv.values())
print('control row: hashes known to be in snap0 %d, found in this index %d (on the snap0 index the two are equal - positive control '
      'of the matcher)' % (tot, tot_hit))
