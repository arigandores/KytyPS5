# Red Team s142 step 1: ft_tail / attempt outcome / hold_s over every enter_scene json of s122-s140 (cheap, json only).
import glob, json, os, collections
rows = []
for p in sorted(glob.glob('C:/kyty/s1[2-4][0-9]/*.json')):
    try:
        js = json.load(open(p, encoding='utf-8'))
    except Exception:
        continue
    if not isinstance(js, dict) or 'attempts' not in js:
        continue
    for a in js.get('attempts') or []:
        if a.get('hold_s') is None:
            continue
        rows.append((p, a.get('outcome'), a.get('hold_s'), a.get('ft_tail'), a.get('hold_exit'), a.get('ft_total'),
                     js.get('guest_args')))
print('attempts with a hold:', len(rows))
c = collections.Counter()
for p, oc, hs, ft, he, tot, ga in rows:
    c[('ft_tail None' if ft is None else ('ft_tail 0' if ft == 0 else 'ft_tail>0'), 'hold_exit' if he is not None else 'no hold_exit')] += 1
for k, v in sorted(c.items()):
    print(k, v)
print('ft_tail == 0 or <= 10 rows:')
for p, oc, hs, ft, he, tot, ga in rows:
    if ft is not None and ft <= 10:
        print(' ', p, oc, hs, ft, he, tot, ga)
fts = sorted(ft for _, _, _, ft, he, _, _ in rows if ft is not None and he is None)
print('ft_tail without hold_exit: n %d min %s p1 %s median %s' % (len(fts), fts[0] if fts else None,
      fts[len(fts)//100] if fts else None, fts[len(fts)//2] if fts else None))
