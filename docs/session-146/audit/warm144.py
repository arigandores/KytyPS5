# warm144.py - Session Auditor s146 step 3 (HPP-389): were the V of s144 that gave SCENE_OK to the three re-check levels warm entries?
# New translation-cache files per tag (runs144 manifests) against the re-check tags of s146 (runs146 manifests). READ ONLY.
import json, os
def load(p):
    if not os.path.isfile(p):
        return None
    return {(x[0], x[1]): x[4] for x in json.load(open(p, encoding='utf-8'))['files']}
for root, runs, tag, lv in (('C:/kyty/s144', 'runs144', 'v144_13', 'timestop_casino'), ('C:/kyty/s144', 'runs144', 'v144_15', 'sponge_dirty_bath'), ('C:/kyty/s144', 'runs144', 'v144_16', 'hoover_beach'),
                            ('C:/kyty/s146', 'runs146', 'r146_03', 'timestop_casino'), ('C:/kyty/s146', 'runs146', 'r146_02', 'sponge_dirty_bath'), ('C:/kyty/s146', 'runs146', 'r146_01', 'hoover_beach'),
                            ('C:/kyty/s145', 'runs145', 'v145_14', 'bonus_path_maker_mix'), ('C:/kyty/s146', 'runs146', 'r146_04', 'bonus_path_maker_mix')):
    b, a = load('%s/%s/cache_%s.before.json' % (root, runs, tag)), load('%s/%s/cache_%s.after.json' % (root, runs, tag))
    if b is None or a is None:
        print('MANIFEST %s %s: missing' % (tag, lv))
        continue
    new = [k for k in a if k not in b and k[0] == 'shader']
    try:
        S = json.load(open('%s/%s/%s.score.json' % (root, runs, tag), encoding='utf-8'))
        d = S['derive']
        extra = 'K2 %s; K3 entry window %d; skipped-draw lines %s / frames %s; outcome %s' % (d.get('k2'), len(d.get('k3w') or []), S['skip']['lines'], S['skip']['frames'], S['outcome'])
    except (OSError, ValueError, KeyError) as e:
        extra = 'score json: %r' % (e,)
    print('MANIFEST %s %s: new translation-cache files in the run %d; %s' % (tag, lv, len(new), extra))
print('ALL DONE')
