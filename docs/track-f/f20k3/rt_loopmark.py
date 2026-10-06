# Red Team F20k3: for every F20j3 W mark (BeginWReg / BeginW with an F20j3 kind) find the loops that ENCLOSE the mark
# inside the same function. A mark begun inside a loop body ends every iteration - if that loop is a retry of the wait,
# the -w record (>= 10 ms) is per slice, not per loop (item 574(g)(1)).
import os, re, sys

root = sys.argv[1]
mark_rx = re.compile(r'\b(BeginWReg|BeginW)\s*\(\s*(Common::)?(DiagB32::)?Wait::(\w+)')
loop_rx = re.compile(r'^\s*(for\s*\(|while\s*\(|do\b)')
fn_rx = re.compile(r'^[A-Za-z_].*\)\s*(const\s*)?(noexcept\s*)?\{\s*$|^[A-Za-z_][\w:<>,\s\*&]*\([^;]*$')
old = {'Cond', 'Mutex', 'Sem', 'PSem', 'Evf', 'Eq', 'Sleep', 'GpuIdle', 'GpuRegmem'}
for dp, dn, fn in os.walk(root):
    for f in fn:
        if not f.endswith(('.cpp', '.h', '.inc')):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, root).replace(os.sep, '/')
        if rel.startswith('common/diagB32'):
            continue
        L = open(p, encoding='utf-8', errors='replace').read().split('\n')
        for i, l in enumerate(L):
            m = mark_rx.search(l)
            if not m:
                continue
            kind = m.group(4)
            # walk backwards tracking brace depth; every '{' that opens an enclosing block is recorded with its line
            depth = 0
            encl = []
            for j in range(i - 1, max(-1, i - 400), -1):
                s = L[j].split('//')[0]
                depth += s.count('}') - s.count('{')
                if depth < 0:
                    depth = 0
                    txt = L[j].strip()
                    if loop_rx.match(L[j]) or re.match(r'^\}?\s*(for|while)\b', txt) or txt.startswith('do'):
                        encl.append((j + 1, txt[:100]))
                    if re.match(r'^[A-Za-z_]', L[j]) and '(' in L[j]:
                        break  # function start at column 0
                    if L[j].startswith('\t') and not L[j].startswith('\t\t') and ('(' in L[j]) and ')' in L[j] and txt.endswith('{') and not loop_rx.match(L[j]) and not txt.startswith(('if', 'else', 'switch', 'case')):
                        # a method defined inside a class at one tab
                        break
            if encl:
                print(f'{rel}:{i+1}\t{kind}\t{"OLD" if kind in old else "NEW"}\t' + ' | '.join(f'L{a}: {t}' for a, t in encl))
