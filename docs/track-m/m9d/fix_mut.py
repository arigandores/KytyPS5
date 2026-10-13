import sys
p = sys.argv[1]
t = open(p, encoding='utf-8').read()
old = '''    after = {f: sha(f) for f in FILES}
    restored = after == before
    print('sources restored (sha256 of %d files): %s' % (len(FILES), restored))
    if blocked():
'''
new = '''    after = {f: sha(f) for f in FILES}
    restored = after == before
    print('sources restored (sha256 of %d files): %s' % (len(FILES), restored))
    if only - {'control'}:
        print('mutants %d of %d CAUGHT (batch, no control)' % (sum(results), len(results)))
        print('BATCH OK' if all(results) and restored else 'BATCH FAIL')
        return 0
    if '--check' in only:
        return 0
    if blocked():
'''
assert t.count(old) == 1
t = t.replace(old, new)
old2 = '''        if only and name not in only:
            continue
'''
new2 = '''        if only and name not in only:
            continue
        if '--check' in only:
            text = open(os.path.join(WT, rel), 'rb').read().decode('utf-8')
            print(name, 'anchors', [text.count(o) for o, _ in subs])
            continue
'''
assert t.count(old2) == 1
t = t.replace(old2, new2)
t = t.replace("Usage: python mut_m9d.py [name ...].", "Usage: python mut_m9d.py [name ...] (a batch, no control) | control (the control alone) | (nothing: all + control).")
open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('ok')
