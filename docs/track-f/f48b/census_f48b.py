# F48b (HPP-831, ROADMAP p.748(d)): own census of register rows against F48a.
# Own table parser: every table whose header starts with "| № |" or "| id |" (summaries s48.2 and s103 excluded, as F32a/F32b);
# id = every Б/Ф number in the first cell (suffix -H kept); class = "класс" column; status = "статус…"/"вердикт" column,
# else the whole row. For each id: all rows in file order; last row; last row whose STATUS cell carries an outcome word;
# (status = class + verdict + status cells) rows AFTER that last outcome row whose status has no outcome word -> AFTER_OUTCOME (a later row may reopen);
# last class cell seen. Usage: python census_f48b.py <reg.md> <census_f48a.tsv> <out.tsv>
import re, sys, collections
reg, f48a, out = sys.argv[1:4]
L = open(reg, encoding='utf-8').read().split('\n')
IDRE = re.compile(r'(?<![\w`])([БФ]\d+[абвгд]?(?:-H)?)(?![\w])')
W = [('FIXED', re.compile(r'FIXED')), ('NE_DEFEKT', re.compile(r'НЕ ДЕФЕКТ')), ('TUPIK', re.compile(r'ТУПИК')),
     ('DUBL', re.compile(r'[Дд]убль')), ('SPLIT', re.compile(r'[Рр]азделен'))]
REOPEN = re.compile(r'переоткры|открыт|не определено|дефект`|`дефект|итерация|кандидат|паркуется')
sec = None; hdr = None
rows = collections.defaultdict(list)
for i, l in enumerate(L):
    m = re.match(r'^##+ (\d+(?:\.\d+)?)\.', l)
    if m:
        sec = m.group(1); hdr = None
    if sec in ('48.2', '103'):
        continue
    if l.startswith('|') and i + 1 < len(L) and L[i + 1].startswith('|---'):
        hdr = [x.strip() for x in l.strip().strip('|').split('|')]
        continue
    if l.startswith('|---') or not l.startswith('|') or hdr is None:
        if not l.startswith('|'):
            hdr = None if not l.strip() else hdr
        continue
    if hdr[0] not in ('№', 'id'):
        continue
    cells = [x.strip() for x in l.strip().strip('|').split('|')]
    c0 = re.sub(r'\(.*', '', cells[0])
    if 'справка' in cells[0]:
        continue
    ci = next((k for k, h in enumerate(hdr) if h == 'класс'), None)
    si = next((k for k, h in enumerate(hdr) if h.startswith('статус') or h == 'вердикт'), None)
    cls = cells[ci] if ci is not None and ci < len(cells) else ''
    vi = next((k for k, h in enumerate(hdr) if h.startswith('дефект') or h == 'вердикт'), None)
    st = ' | '.join(cells[k] for k in (ci, vi, si) if k is not None and k < len(cells)) if si is not None else ' | '.join(cells[1:])
    for x in IDRE.findall(c0):
        rows[x].append((i + 1, sec, cls, st))

def key(s):
    n = re.match(r'([БФ])(\d+)(.*)', s); return (n.group(1), int(n.group(2)), n.group(3))

A = {}
for l in open(f48a, encoding='utf-8').read().split('\n')[1:]:
    if l.strip():
        c = l.split('\t'); A[c[0]] = c
res = []
for k in sorted(rows, key=key):
    rr = rows[k]
    cls = next((r[2] for r in reversed(rr) if re.search(r'K\d', r[2])), '')
    lastout = None
    for r in rr:
        hit = [w for w, rx in W if rx.search(r[3])]
        if hit:
            lastout = (r, hit)
    after = []
    if lastout:
        idx = rr.index(lastout[0])
        after = [r for r in rr[idx + 1:] if not any(rx.search(r[3]) for _, rx in W)]
    a = A.get(k)
    res.append((k, cls, len(rr), 's%s:%d' % (rr[-1][1], rr[-1][0]),
                ('s%s:%d' % (lastout[0][1], lastout[0][0]) + ' ' + ','.join(lastout[1])) if lastout else 'NONE',
                ';'.join('s%s:%d%s' % (r[1], r[0], '!' if REOPEN.search(r[3]) else '') for r in after),
                a[1] if a else 'ABSENT_IN_F48A', a[3] if a else '', a[4] if a else ''))
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('id\tclass\tn_rows\tlast_row\tlast_outcome_row\tafter_outcome_rows(!=reopen-word)\tf48a_code\tf48a_last\tf48a_outcome_line\n')
    for r in res:
        f.write('\t'.join(str(x) for x in r) + '\n')
mine = {r[0] for r in res}
print('ids own', len(mine), 'f48a', len(A), 'only own', sorted(mine - set(A), key=key), 'only f48a', sorted(set(A) - mine, key=key))
print('no outcome row (own):', [r[0] + '/' + r[1] for r in res if r[4] == 'NONE'])
print('rows after last outcome row with reopen word:', [(r[0], r[5]) for r in res if '!' in r[5]])
diff = [(r[0], r[3], r[7]) for r in res if r[7] and r[3] != r[7]]
print('last row differs from F48a:', diff)
odiff = [(r[0], r[4].split()[0], r[8]) for r in res if r[8] and r[4] != 'NONE' and r[4].split()[0] != r[8]]
print('last outcome row differs from F48a outcome_line:', odiff)
