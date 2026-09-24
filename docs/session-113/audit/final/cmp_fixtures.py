"""Audit 113 final (protocol lens): compare the fixture case lists of test_vbn113c/d/e/f.py statically (AST, no run)."""
import ast, sys, re
from pathlib import Path

def collect(path):
    src = Path(path).read_text(encoding='utf-8')
    tree = ast.parse(src)
    cases, edges, named = [], [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            nm = node.targets[0].id
            if nm in ('cases', 'EDGES') and isinstance(node.value, ast.List):
                for el in node.value.elts:
                    seg = ast.get_source_segment(src, el)
                    seg = re.sub(r'\s+', ' ', seg)
                    (cases if nm == 'cases' else edges).append(seg)
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id in ('cases', 'EDGES'):
            seg = re.sub(r'\s+', ' ', ast.get_source_segment(src, node.value))
            (cases if node.target.id == 'cases' else edges).append('+= ' + seg)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ('make', 'armed_edge'):
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                named.append(node.args[0].value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ('append', 'extend', 'insert'):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ('cases', 'EDGES'):
                seg = re.sub(r'\s+', ' ', ast.get_source_segment(src, node))
                (cases if node.func.value.id == 'cases' else edges).append('CALL ' + seg)
    comments = [l.strip() for l in src.splitlines() if l.strip().startswith('#') and ('dict(' in l or "'B" in l)]
    inline = [l for l in src.splitlines() if '#' in l and ('dict(' in l.split('#', 1)[1])]
    return cases, edges, named, comments, inline

def case_name(seg):
    m = re.match(r"\(\s*'([^']+)'", seg)
    return m.group(1) if m else seg

versions = ['c', 'd', 'e', 'f']
data = {v: collect('C:/kyty/s113/test_vbn113%s.py' % v) for v in versions}
for v in versions:
    c, e, n, com, inl = data[v]
    print('test_vbn113%s: cases %d, EDGES %d, named make() %d' % (v, len(c), len(e), len(n)))
    for x in inl:
        print('   inline comment holding a fixture:', x.strip()[:160])
    for x in com:
        print('   comment line holding a fixture:', x[:160])
print()
for a, b in [('c', 'd'), ('d', 'e'), ('e', 'f'), ('c', 'f')]:
    ca, ea, na = data[a][0], data[a][1], data[a][2]
    cb, eb, nb = data[b][0], data[b][1], data[b][2]
    sa, sb = {case_name(x) for x in ca}, {case_name(x) for x in cb}
    print('== %s -> %s' % (a, b))
    print('  cases lost  :', sorted(sa - sb))
    print('  cases added :', sorted(sb - sa))
    changed = sorted(case_name(x) for x in ca if case_name(x) in sb and x not in cb)
    print('  cases changed (same name, other text):', changed)
    ea_s, eb_s = set(ea), set(eb)
    print('  EDGES lost  :', sorted(ea_s - eb_s))
    print('  EDGES added :', sorted(eb_s - ea_s))
    print('  named lost  :', sorted(set(na) - set(nb)))
    print('  named added :', sorted(set(nb) - set(na)))
