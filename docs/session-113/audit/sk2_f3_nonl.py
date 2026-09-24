import os, re
ROOT = 'C:/kyty/KytyPS5/src'
CALL = re.compile(r'\b(LOGF|LOGF_COLOR|LOGV|LOGV_COLOR)\s*\(')
LIT = re.compile(r'\s*(?:PRI[a-zA-Z0-9]+\s*)?"((?:[^"\\]|\\.)*)"')
NL = chr(92) + 'n'
hits = []
total = 0
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if not f.endswith(('.cpp', '.h', '.inc')):
            continue
        p = os.path.join(dp, f).replace(os.sep, '/')
        src = open(p, 'rb').read().decode('utf8', 'replace')
        for m in CALL.finditer(src):
            i = m.end()
            if m.group(1).endswith('_COLOR'):
                # skip the style argument
                depth = 0
                while i < len(src):
                    c = src[i]
                    if c == '(':
                        depth += 1
                    elif c == ')':
                        depth -= 1
                    elif c == ',' and depth == 0:
                        i += 1
                        break
                    i += 1
            lits = []
            while True:
                mm = re.compile(r'\s*("((?:[^"\\]|\\.)*)"|PRI[a-zA-Z0-9]+)').match(src, i)
                if not mm:
                    break
                if mm.group(2) is not None or mm.group(1).startswith('"'):
                    lits.append(mm.group(2) or '')
                i = mm.end()
            if not lits:
                continue
            total += 1
            if not lits[-1].endswith(NL):
                line = src.count(chr(10), 0, m.start()) + 1
                hits.append((p[len(ROOT) + 1:], line, (lits[-1])[-50:]))
print('calls', total, 'without trailing newline', len(hits))
for h in hits[:80]:
    print('%s:%d  ...%r' % h)
