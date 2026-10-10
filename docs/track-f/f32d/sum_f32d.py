# F32d (HPP-742): summary of table_f32d.tsv with the self-checks against rep_f32a.py (3) on the merged input.
#   I2: rows = K3 hold + K2 hold of rep TOTAL;  I3: per level K3 hold / K2 hold = rep per-level row;  I4: sum over classes = rows;
#   I5: rows from logs of the F32a set + rows from the 36 out-of-mask logs = rows, and the F32a part has K3 = 239 (rep_f32a.out.txt).
# Prints the class x level table, the class split for the F32a part and for the out-of-mask part, every NONE / B32 / B33 / PAUSE
# row, and the input of the F32e rule p.673(z)(3)(i)-(iii) (counts only - the reading is the lead's).
# Usage: python sum_f32d.py <table_f32d.tsv> <rep_mrg.out.txt> <f32a agg_f32a.json>
import re, sys, json, collections
TAB = chr(9)
ok = True
rows = [l.rstrip(chr(10)).split(TAB) for l in open(sys.argv[1], encoding='utf-8')]
hdr, rows = rows[0], rows[1:]
H = {k: i for i, k in enumerate(hdr)}
rep = open(sys.argv[2], encoding='utf-8').read()
tot = re.search(r"TOTAL \{'entries': (\d+), 'k2w': (\d+), 'k2h': (\d+), 'k3h': (\d+)", rep)
per = {m.group(1): (int(m.group(3)), int(m.group(2))) for m in
       re.finditer(r'^  (\S+)\s+entries\s+\d+\s+K2 window\s+\d+\s+K2 hold\s+(\d+)\s+K3 hold\s+(\d+)', rep, re.M)}
f32a_paths = set(r['path'] for r in json.load(open(sys.argv[3], encoding='utf-8')))


def chk(name, cond, detail=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + (' ' + detail if detail else ''))
    ok = ok and cond


k3 = sum(1 for r in rows if r[H['cls']] == 'K3')
k2 = sum(1 for r in rows if r[H['cls']] == 'K2')
chk('I2 rows = rep K3 hold + K2 hold', k3 == int(tot.group(4)) and k2 == int(tot.group(3)),
    'K3 %d/%s K2 %d/%s' % (k3, tot.group(4), k2, tot.group(3)))
lv3 = collections.Counter(r[H['level']] for r in rows if r[H['cls']] == 'K3')
lv2 = collections.Counter(r[H['level']] for r in rows if r[H['cls']] == 'K2')
bad = [lv for lv in set(per) | set(lv3) | set(lv2) if per.get(lv, (0, 0)) != (lv3.get(lv, 0), lv2.get(lv, 0))]
chk('I3 per level = rep (3)', not bad, str(bad))
cls = collections.Counter(r[H['attr']] for r in rows)
chk('I4 sum over classes = rows', sum(cls.values()) == len(rows), str(dict(cls)))
part = lambda r: 'F32a' if r[H['path:line']].rsplit(':', 1)[0] in f32a_paths else 'out-of-mask'
pc = collections.Counter(part(r) for r in rows)
k3a = sum(1 for r in rows if part(r) == 'F32a' and r[H['cls']] == 'K3')
chk('I5 F32a part + out-of-mask part = rows; F32a part K3 = 239', pc['F32a'] + pc['out-of-mask'] == len(rows) and k3a == 239,
    '%s, F32a K3 %d' % (dict(pc), k3a))
print()
print('class x part x cls:')
for (a, p, c), n in sorted(collections.Counter((r[H['attr']], part(r), r[H['cls']]) for r in rows).items()):
    print('  %-6s %-12s %s %4d' % (a, p, c, n))
print()
print('class x level (K3+K2):')
lvls = sorted(set(r[H['level']] for r in rows))
for lv in lvls:
    c = collections.Counter(r[H['attr']] for r in rows if r[H['level']] == lv)
    print('  %-30s %s' % (lv, ' '.join('%s %d' % kv for kv in sorted(c.items()))))
print()
print('class x build:')
for b in sorted(set(r[H['build']] for r in rows)):
    c = collections.Counter(r[H['attr']] for r in rows if r[H['build']] == b)
    print('  %-14s %s' % (b, ' '.join('%s %d' % kv for kv in sorted(c.items()))))
print()
for a in ('NONE', 'B32', 'B33', 'PAUSE'):
    sel = [r for r in rows if r[H['attr']] == a]
    print('%s rows: %d' % (a, len(sel)))
    for r in sel:
        print('  %s | %s | %s | n %s | %s us | %s | %s | %s | also %s | %s' % (r[H['level']], r[H['build']], r[H['tag']], r[H['n']],
              r[H['dt_us']], r[H['cls']], r[H['warm']], r[H['basis']][:70], r[H['also']] or '-', r[H['patch']] or '-'))
print()
b5 = collections.Counter(r[H['basis']].split(':')[0] for r in rows if r[H['attr']] == 'B5')
print('B5 sub-forms:', dict(b5))
print('B5 hold sub-form by level/build/tag:', dict(collections.Counter((r[H['level']], r[H['build']], r[H['tag']]) for r in rows
                                                                     if r[H['attr']] == 'B5' and r[H['basis']].startswith('hold'))))
print('INSTR by tag:', dict(collections.Counter((r[H['tag']], r[H['basis']][:48]) for r in rows if r[H['attr']] == 'INSTR')))
print('B5F by tag:', dict(collections.Counter((r[H['tag']], r[H['basis']][:48]) for r in rows if r[H['attr']] == 'B5F')))
reopen = [r for r in rows if r[H['attr']] == 'B33' and 'reopen' in r[H['basis']]]
print('B33 reopen (p.637 condition) rows:', len(reopen))
print()
none = [r for r in rows if r[H['attr']] == 'NONE']
print('F32e input: NONE rows %d; on a warm hold outside Sky Garden / intro_next %d; on Sky Garden %d; on intro_next %d' % (
    len(none), sum(1 for r in none if r[H['warm']] == 'warm' and r[H['level']] not in ('underwater_aerial_garden', 'intro_next')),
    sum(1 for r in none if r[H['level']] == 'underwater_aerial_garden'), sum(1 for r in none if r[H['level']] == 'intro_next')))
print('ALL OK' if ok else 'FAILED')
