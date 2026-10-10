# Fixtures for census_f32a.py (F32a, HPP-733): parser edges (sections, header detection, multi-id first cell, letters a-g,
# id not in the first cell, prose lines), outcome words, adjudication checks (missing adjudication, missing citation,
# lead list not covered). Last line ALL OK.
import os, sys, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('census_f32a', os.path.join(HERE, 'census_f32a.py'))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
ok = True


def check(name, cond):
    global ok
    print(('OK   ' if cond else 'FAIL ') + name)
    ok &= bool(cond)


B, F = 'Б', 'Ф'
NED = '`НЕ ДЕФЕКТ`'
T = '\n'.join([
    '# title',
    '## 4. Реестр',
    '',
    '| № | класс | статус на сегодня |',
    '|---|---|---|',
    '| ' + B + '1 | K4 | open |',
    '| ' + B + '12 | K3 | open, see ' + B + '1 |',
    '| ' + F + '4а (new) | K4 | open |',
    '',
    '## 9. later',
    '',
    '| № | класс | статус на сегодня |',
    '|---|---|---|',
    '| ' + B + '1, ' + B + '12 (поправка) | K4 | ' + B + '1 **`FIXED`** |',
    'prose: ' + F + '4а → ' + NED + ' here',
    '',
    '### 48.2 queue',
    '',
    '| № | x |',
    '|---|---|',
    '| ' + B + '12 | FIXED in summary only |',
])
occ = C.parse(T)
check('ids parsed: B1, B12, F4a', set(occ) == {B + '1', B + '12', F + '4а'})
check('B12 not taken from a non-first cell of the B1 row', len(occ[B + '1']) == 2)
check('multi-id first cell gives both ids', occ[B + '12'][1]['multi'] and occ[B + '12'][1]['sec'] == '9')
check('section 48.2 row recorded with its section', occ[B + '12'][-1]['sec'] == '48.2')
check('header row not taken as data', all(x['first'] != '№' for v in occ.values() for x in v))
check('outcome words FIXED in last B1 row', 'FIXED' in C.outcome_words(occ[B + '1'][-1]['row']))
check('F4a letter kept (not F4)', F + '4' not in occ)
# adjudication with a test table
C.ADJ = {B + '1': ('FIXED', C.W_FIXED), B + '12': ('OPEN', None), F + '4а': ('NE_DEFEKT', C.W_NED)}
C.LEAD_OPEN = {B + '12'}
C.LEAD_REM = set()
good, rows = C.adjudicate(T, occ)
r = {x[0]: x for x in rows}
check('adjudication passes', good)
check('FIXED cited on the section 9 line (15th line is prose, 14th is the row)', r[B + '1'][4] == 14)
check('B12 outcome line ignores the 48.2 summary row', r[B + '12'][4] is None and r[B + '12'][2] == '9')
check('NE DEFEKT cited from prose line', r[F + '4а'][4] == 15)
C.ADJ = {B + '1': ('FIXED', C.W_FIXED), B + '12': ('OPEN', None)}
good2, _ = C.adjudicate(T, occ)
check('missing adjudication fails', not good2)
C.ADJ = {B + '1': ('OPEN', None), B + '12': ('TUPIK', C.W_TUPIK), F + '4а': ('OPEN', None)}
good3, _ = C.adjudicate(T, occ)
check('missing citation fails', not good3)
C.ADJ = {B + '1': ('FIXED', C.W_FIXED), B + '12': ('FIXED', C.W_FIXED), F + '4а': ('NE_DEFEKT', C.W_NED)}
C.LEAD_OPEN = {B + '12'}
good4, _ = C.adjudicate(T, occ)
check('lead open row not open in census fails', not good4)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
