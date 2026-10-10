# F32a (HPP-733, ROADMAP p.672(b)(1)): census of register rows. Parses every markdown table of docs/track-f/register.md,
# takes every row whose first cell names row ids (B<n>[letter] / F<n>[letter] in Cyrillic), records every occurrence
# (section, file line, class cell, status cells) and the LAST occurrence of each id; detects outcome words in the last row.
# Usage: python census_f32a.py <register.md> <out.tsv> [--all <all.tsv>]
import re, sys, collections

NL = chr(10)
TAB = chr(9)
ID = re.compile('(?<![0-9A-Za-zЀ-ӿ])([БФ])(\\d+)([а-г]?)(?![0-9])')
OUTCOMES = [('FIXED', re.compile(r'`FIXED`|\bFIXED\b')),
            ('TUPIK', re.compile('`ТУПИК`|ТУПИК')),
            ('NE_DEFEKT', re.compile('`НЕ ДЕФЕКТ`|НЕ ДЕФЕКТ')),
            ('DUBL', re.compile('дубль|слита с')),
            ('NE_OPR', re.compile('не определено')),
            ('PARK', re.compile('паркуется|парковк')),
            ('K5', re.compile(r'\bK5\b'))]


def ids_of(cell):
    out = []
    for m in ID.finditer(cell):
        k = m.group(1) + m.group(2) + m.group(3)
        if k not in out:
            out.append(k)
    return out


def split_row(line):
    s = line.strip()
    if not (s.startswith('|') and s.endswith('|')):
        return None
    # cells; backquoted pipes are not used in the register tables
    return [c.strip() for c in s[1:-1].split('|')]


def parse(text):
    sec = '0'
    occ = collections.defaultdict(list)
    header = None
    lines = text.split(NL)
    for i, line in enumerate(lines, 1):
        if line.startswith('## ') or line.startswith('### '):
            m = re.match(r'#+\s+([0-9]+(?:\.[0-9]+)?)', line)
            sec = m.group(1) if m else line[3:20]
            header = None
            continue
        cells = split_row(line)
        if cells is None:
            header = None
            continue
        if all(set(c) <= set('-: ') for c in cells):
            continue
        if header is None:
            header = cells
            continue
        first = cells[0]
        ids = ids_of(first)
        if not ids:
            continue
        hk = [h.lower() for h in header]

        def col(name):
            for j, h in enumerate(hk):
                if name in h and j < len(cells):
                    return cells[j]
            return ''
        status = col('статус')
        kind = col('дефект / наблюдение')
        klass = col('класс')
        for k in ids:
            occ[k].append({'sec': sec, 'line': i, 'first': first, 'klass': klass, 'kind': kind, 'status': status,
                           'row': line.strip(), 'multi': len(ids) > 1})
    return occ


def outcome_words(text):
    return [n for n, rx in OUTCOMES if rx.search(text)]


def key(k):
    return (k[0], int(re.sub(r'\D', '', k)), k[-1] if not k[-1].isdigit() else '')


# ---------------------------------------------------------------- adjudication (F32a): outcome of every id, verified on the text
W_FIXED = re.compile(r'FIXED')
W_TUPIK = re.compile('ТУПИК')
W_NED = re.compile('НЕ ДЕФЕКТ')
W_DUBL = re.compile('дубль|слита')
W_K5 = re.compile(r'\bK5\b')
B, F = 'Б', 'Ф'
ADJ = {}
for k in ('1а', '1б', '4', '9а', '12', '13', '24', '26б', '35', '37', '42'):
    ADJ[B + k] = ('FIXED', W_FIXED)
for k in ('8', '9', '10', '16', '19', '27'):
    ADJ[F + k] = ('FIXED', W_FIXED)
ADJ[B + '33'] = ('FIXED+REM', W_FIXED)
for k in ('9б', '25', '26а'):
    ADJ[B + k] = ('TUPIK', W_TUPIK)
for k in ('2', '3б', '7', '9', '11', '27', '30', '41'):
    ADJ[B + k] = ('NE_DEFEKT', W_NED)
for k in ('8', '14', '28', '29', '39'):
    ADJ[B + k] = ('NE_DEFEKT+REM', W_NED)
for k in ('4', '6', '7'):
    ADJ[F + k] = ('NE_DEFEKT', W_NED)
ADJ[F + '5'] = ('NE_DEFEKT+REM', W_NED)
ADJ[B + '10'] = ('DUBL', W_DUBL)
ADJ[B + '31'] = ('DUBL', W_DUBL)
for k in ('15', '16', '17', '18', '19', '20', '22', '38'):
    ADJ[B + k] = ('K5', W_K5)
for k in ('12', '13', '14', '15', '17', '23'):
    ADJ[F + k] = ('K5', W_K5)
ADJ[B + '26'] = ('SPLIT', re.compile('Б26а'))
for k in ('5', '5а', '6', '32', '34', '36', '40', '26в', '26г'):
    ADJ[B + k] = ('OPEN', None)
for k in ('3', '4а', '11', '18', '20', '21', '22', '24', '25', '26'):
    ADJ[F + k] = ('OPEN', None)
# list (a) of ROADMAP item 672 (lead's lower bound): open rows and remainders
LEAD_OPEN = {B + '34', B + '6', B + '32', B + '36', B + '40', B + '5', B + '5а', F + '3', B + '26в', B + '26г', F + '4а',
             F + '11', F + '18', F + '20', F + '21', F + '22', F + '24', F + '25', F + '26'}
LEAD_REM = {F + '5', B + '8', B + '14', B + '28', B + '33'}


def tokens_line(line, k):
    return any(m.group(1) + m.group(2) + m.group(3) == k for m in ID.finditer(line))


def adjudicate(text, occ):
    lines = text.split(NL)
    sec_of = {}
    sec = '0'
    for i, l in enumerate(lines, 1):
        if l.startswith('## ') or l.startswith('### '):
            m = re.match(r'#+\s+([0-9]+(?:\.[0-9]+)?)', l)
            sec = m.group(1) if m else sec
        sec_of[i] = sec
    ok = True
    rows = []
    for k in sorted(set(occ) | set(ADJ), key=key):
        if k not in ADJ:
            print('NOT ADJUDICATED', k)
            ok = False
            continue
        if k not in occ:
            print('ADJUDICATED BUT NOT A ROW', k)
            ok = False
            continue
        code, word = ADJ[k]
        tab = [x for x in occ[k] if x['sec'] not in ('103', '48.2')]
        last = tab[-1]
        cite = None
        if word is not None:
            for i in range(len(lines), 0, -1):
                if sec_of[i] in ('103', '48.2'):
                    continue
                if tokens_line(lines[i - 1], k) and word.search(lines[i - 1]):
                    cite = i
                    break
            if cite is None:
                print('NO LINE WITH', k, code)
                ok = False
        rows.append((k, code, last['sec'], last['line'], cite, sec_of.get(cite, '-') if cite else '-', last['klass'][:50]))
    open_ids = {r[0] for r in rows if r[1] == 'OPEN'}
    rem_ids = {r[0] for r in rows if r[1].endswith('+REM')}
    print('ids', len(rows), 'by code', dict(collections.Counter(r[1] for r in rows)))
    print('OPEN', len(open_ids), ' '.join(sorted(open_ids, key=key)))
    print('REMAINDERS', len(rem_ids), ' '.join(sorted(rem_ids, key=key)))
    miss = LEAD_OPEN - open_ids
    extra = open_ids - LEAD_OPEN
    print('lead list (a) open rows missing in census:', sorted(miss) or 0, '; census open rows beyond list (a):', sorted(extra) or 0)
    print('lead remainders missing in census:', sorted(LEAD_REM - rem_ids) or 0, '; census remainders beyond list (a):', sorted(rem_ids - LEAD_REM) or 0)
    if miss or (LEAD_REM - rem_ids):
        ok = False
    return ok, rows


def main():
    reg, out = sys.argv[1], sys.argv[2]
    text = open(reg, encoding='utf-8').read().replace(chr(13), '')
    occ = parse(text)
    with open(out, 'w', encoding='utf-8', newline=NL) as o:
        o.write(TAB.join(['id', 'n_occ', 'last_sec', 'last_line', 'last_first_cell', 'last_class', 'last_kind_words', 'last_status_words',
                          'last_row_words', 'sections']) + NL)
        for k in sorted(occ, key=key):
            v = occ[k]
            last = v[-1]
            o.write(TAB.join([k, str(len(v)), last['sec'], str(last['line']), last['first'][:60], last['klass'][:60],
                              ','.join(outcome_words(last['kind'])) or '-', ','.join(outcome_words(last['status'])) or '-',
                              ','.join(outcome_words(last['row'])) or '-', ' '.join(sorted(set(x['sec'] for x in v), key=lambda s: float(s) if re.match(r'^[0-9.]+$', s) else 0))]) + NL)
    if '--all' in sys.argv:
        with open(sys.argv[sys.argv.index('--all') + 1], 'w', encoding='utf-8', newline=NL) as o:
            for k in sorted(occ, key=key):
                for x in occ[k]:
                    o.write(TAB.join([k, x['sec'], str(x['line']), x['first'][:80], x['klass'][:80]]) + NL)
    print('ids', len(occ), 'occurrences', sum(len(v) for v in occ.values()))
    ok, rows = adjudicate(text, occ)
    if '--adj' in sys.argv:
        with open(sys.argv[sys.argv.index('--adj') + 1], 'w', encoding='utf-8', newline=NL) as o:
            o.write(TAB.join(['id', 'outcome', 'last_row_sec', 'last_row_line', 'outcome_line', 'outcome_sec', 'class']) + NL)
            for r in rows:
                o.write(TAB.join(str(x) for x in r) + NL)
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
