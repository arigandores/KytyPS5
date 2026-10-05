import ast, sys
L = 'C:/kyty/s288/s15a3'
def muts(p):
    tree = ast.parse(open(p, encoding='ascii').read())
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Tuple) and len(n.elts) == 3 and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in n.elts):
            out.append(tuple(e.value for e in n.elts))
    return out
mo, mn = muts(L + '/orig/mut_sc_s15.py'), muts('C:/kyty/s288/s15/mut_sc_s15.py')
so = open(L + '/orig/sc_s15.py', encoding='ascii').read()
sn = open('C:/kyty/s288/s15/sc_s15.py', encoding='ascii').read()
print('mutants old %d new %d; ids equal %s' % (len(mo), len(mn), [m[0] for m in mo] == [m[0] for m in mn]))
diff = [(a[0], so.count(a[1]), sn.count(b[1])) for a, b in zip(mo, mn) if so.count(a[1]) != sn.count(b[1]) or a != b]
print('changed or count-changed mutants:', diff)
print('anchors with count 0 on the new code:', [m[0] for m in mn if sn.count(m[1]) == 0])
print('anchors with count 0 on the old code:', [m[0] for m in mo if so.count(m[1]) == 0])
