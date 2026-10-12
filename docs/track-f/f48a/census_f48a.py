# F48a (HPP-830, ROADMAP p.748(d)(1)): census of every register row (s4-s128) by its LAST table row.
# Table parsing = docs/track-f/f32a/census_f32a.py parse() (imported unchanged) with two changes named here:
#   (1) the id token also takes the suffix '-H' (row B8-H, opened in s104 from the remainder of B8);
#   (2) a row whose first cell is a reference ('справка') to another id is not a row of that id (s106:1522 - the K5 harness
#       observation 'справка Ф28' is not row F28).
# Summary sections s48.2 and s103 (queue / iteration headers) are not 'last rows' (F32a rule).
# Adjudication ADJ48 below is the census proposal; every entry is verified on the text: (a) a register line outside s48.2 /
# s103 carries the id token and the outcome word; (b) when the last row of the id has a bold outcome word ('**`FIXED`',
# '**`ТУПИК`', '**`НЕ ДЕФЕКТ`', bold or backquoted at the start of the status cell), it must agree with the code;
# (c) every id of the tables is adjudicated and every adjudicated id is a row; (d) the lead's count of p.748(d) is a lower
# bound - each of its ids must have the outcome named there.
# Usage: python census_f48a.py <register.md> <out.tsv> [--rem <rem.txt>]     prints counts, open rows, remainders, ALL OK
import os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'f32a'))
import census_f32a as C  # noqa: E402

NL = chr(10)
TAB = chr(9)
B, F = 'Б', 'Ф'
C.ID = re.compile('(?<![0-9A-Za-zЀ-ӿ])([БФ])(\\d+)([а-г]?)(-H)?(?![0-9])')
REF = re.compile('справка')
SUMMARY = ('48.2', '103')


def ids_of(cell):
    out = []
    if REF.search(cell):
        return out
    for m in C.ID.finditer(cell):
        k = m.group(1) + m.group(2) + m.group(3) + (m.group(4) or '')
        if k not in out:
            out.append(k)
    return out


C.ids_of = ids_of


def tokens_line(line, k):
    return any(m.group(1) + m.group(2) + m.group(3) + (m.group(4) or '') == k for m in C.ID.finditer(line))


def key(k):
    m = re.match('([БФ])(\\d+)(.*)$', k)
    return (m.group(1), int(m.group(2)), m.group(3))


W_FIXED = re.compile(r'FIXED')
W_TUPIK = re.compile('ТУПИК')
W_NED = re.compile('НЕ ДЕФЕКТ')
W_DUBL = re.compile('дубль|слита')
W_K5 = re.compile(r'\bK5\b')
ADJ = {}
for k in ('1а', '1б', '4', '9а', '12', '13', '24', '26б', '35', '37', '42'):
    ADJ[B + k] = ('FIXED', W_FIXED)
for k in ('8', '9', '10', '16', '19', '20', '21', '24', '25', '27', '29'):
    ADJ[F + k] = ('FIXED', W_FIXED)
ADJ[B + '33'] = ('FIXED+REM', W_FIXED)
for k in ('9б', '25', '26а', '32', '34', '36', '40'):
    ADJ[B + k] = ('TUPIK', W_TUPIK)
for k in ('18', '26', '28'):
    ADJ[F + k] = ('TUPIK', W_TUPIK)
for k in ('5', '5а'):
    ADJ[B + k] = ('TRACK_S', W_TUPIK)
for k in ('2', '3б', '6', '7', '8', '8-H', '9', '11', '26в', '26г', '27', '30'):
    ADJ[B + k] = ('NE_DEFEKT', W_NED)
for k in ('3', '4', '4а', '6', '7', '11', '22'):
    ADJ[F + k] = ('NE_DEFEKT', W_NED)
for k in ('14', '28', '29', '39', '41'):
    ADJ[B + k] = ('NE_DEFEKT+REM', W_NED)
ADJ[F + '5'] = ('NE_DEFEKT+REM', W_NED)
ADJ[B + '10'] = ('DUBL', W_DUBL)
ADJ[B + '31'] = ('DUBL', W_DUBL)
for k in ('15', '16', '17', '18', '19', '20', '22', '38'):
    ADJ[B + k] = ('K5', W_K5)
for k in ('12', '13', '14', '15', '17', '23'):
    ADJ[F + k] = ('K5', W_K5)
ADJ[B + '26'] = ('SPLIT', re.compile('Б26а'))
# remainders of rows with an outcome (p.673(d)): register line of the parking condition
REM_COND = {F + '5': 1093, B + '14': 1458, B + '28': 1458, B + '29': 1459, B + '33': 1352, B + '39': 598, B + '41': 677}
# lead's count of p.748(d) (outcomes after F32c by items 675-748): lower bound, not the source
LEAD = {F + '22': 'NE_DEFEKT', B + '8-H': 'NE_DEFEKT', F + '25': 'FIXED', F + '24': 'FIXED', F + '20': 'FIXED',
        F + '26': 'TUPIK', B + '34': 'TUPIK', F + '21': 'FIXED', B + '6': 'NE_DEFEKT', F + '28': 'TUPIK', F + '29': 'FIXED'}
BOLD = re.compile(r'^\W*\*\*`?(FIXED|ТУПИК|НЕ ДЕФЕКТ)')
BOLD_WORD = {'FIXED': 'FIXED', 'ТУПИК': 'TUPIK', 'НЕ ДЕФЕКТ': 'NE_DEFEKT'}


def base_code(code):
    return {'FIXED+REM': 'FIXED', 'NE_DEFEKT+REM': 'NE_DEFEKT', 'TRACK_S': 'TUPIK'}.get(code, code)


def sections(lines):
    sec_of = {}
    sec = '0'
    for i, l in enumerate(lines, 1):
        if l.startswith('## ') or l.startswith('### '):
            m = re.match(r'#+\s+([0-9]+(?:\.[0-9]+)?)', l)
            sec = m.group(1) if m else sec
        sec_of[i] = sec
    return sec_of


def census(text, adj=None, lead=None, rem=None):
    adj = ADJ if adj is None else adj
    lead = LEAD if lead is None else lead
    rem = REM_COND if rem is None else rem
    occ = C.parse(text)
    lines = text.split(NL)
    sec_of = sections(lines)
    msgs = []
    rows = []
    for k in sorted(set(occ) | set(adj), key=key):
        if k not in adj:
            msgs.append('NOT ADJUDICATED ' + k)
            continue
        if k not in occ:
            msgs.append('ADJUDICATED BUT NOT A ROW ' + k)
            continue
        code, word = adj[k]
        tab = [x for x in occ[k] if x['sec'] not in SUMMARY]
        if not tab:
            msgs.append('ONLY IN SUMMARY ' + k)
            continue
        last = tab[-1]
        cite = None
        for i in range(len(lines), 0, -1):
            if sec_of[i] in SUMMARY:
                continue
            if tokens_line(lines[i - 1], k) and word.search(lines[i - 1]):
                cite = i
                break
        if cite is None:
            msgs.append('NO LINE WITH %s %s' % (k, code))
        cell = last['status'] or last['kind']
        bm = BOLD.match(cell)
        bold = BOLD_WORD[bm.group(1)] if bm else '-'
        if bold != '-' and code not in ('K5', 'DUBL', 'SPLIT') and bold != base_code(code):
            msgs.append('LAST ROW CONTRADICTS %s: last row %s:%d says %s, census %s' % (k, last['sec'], last['line'], bold, code))
        rows.append({'id': k, 'code': code, 'last_sec': last['sec'], 'last_line': last['line'], 'cite_line': cite or 0,
                     'cite_sec': sec_of.get(cite, '-') if cite else '-', 'bold': bold, 'klass': last['klass'][:60],
                     'cell': cell[:160], 'n_occ': len(occ[k])})
    byid = {r['id']: r for r in rows}
    for k, v in lead.items():
        if k not in byid:
            msgs.append('LEAD ID MISSING ' + k)
        elif base_code(byid[k]['code']) != v:
            msgs.append('LEAD DIFFERS %s lead %s census %s' % (k, v, byid[k]['code']))
    for k, ln in rem.items():
        if k not in byid or not byid[k]['code'].endswith('+REM'):
            msgs.append('REMAINDER WITHOUT +REM ' + k)
        if ln > len(lines) or not tokens_line(lines[ln - 1], k):
            msgs.append('REMAINDER LINE %d DOES NOT NAME %s' % (ln, k))
    for r in rows:
        if r['code'].endswith('+REM') and r['id'] not in rem:
            msgs.append('REM CODE WITHOUT CONDITION ' + r['id'])
    return rows, msgs


def main():
    reg, out = sys.argv[1], sys.argv[2]
    text = open(reg, encoding='utf-8').read().replace(chr(13), '')
    rows, msgs = census(text)
    lines = text.split(NL)
    with open(out, 'w', encoding='utf-8', newline=NL) as o:
        o.write(TAB.join(['id', 'code', 'class_last_row', 'last_row', 'outcome_line', 'last_row_bold', 'n_occ', 'last_status_cell']) + NL)
        for r in rows:
            o.write(TAB.join([r['id'], r['code'], r['klass'], 's%s:%d' % (r['last_sec'], r['last_line']),
                              's%s:%d' % (r['cite_sec'], r['cite_line']), r['bold'], str(r['n_occ']), r['cell'].replace(TAB, ' ')]) + NL)
    cnt = collections.Counter(r['code'] for r in rows)
    print('ids', len(rows), 'by code', dict(sorted(cnt.items())))
    k14 = [r for r in rows if r['code'] not in ('K5', 'DUBL', 'SPLIT')]
    print('K1-K4 rows (without K5, duplicates, split parent):', len(k14), dict(sorted(collections.Counter(base_code(r['code']) for r in k14).items())))
    opn = [r['id'] for r in rows if r['code'] == 'OPEN']
    print('OPEN (without outcome):', len(opn), ' '.join(opn) or '-')
    rems = [r['id'] for r in rows if r['code'].endswith('+REM')]
    print('REMAINDERS (parts of rows with an outcome):', len(rems), ' '.join(rems))
    if '--rem' in sys.argv:
        with open(sys.argv[sys.argv.index('--rem') + 1], 'w', encoding='utf-8', newline=NL) as o:
            for k in rems:
                ln = REM_COND[k]
                o.write('%s\tregister.md:%d\t%s%s' % (k, ln, lines[ln - 1].strip(), NL))
    for m in msgs:
        print(m)
    print('ALL OK' if not msgs else 'FAILED')
    return 0 if not msgs else 1


if __name__ == '__main__':
    sys.exit(main())
