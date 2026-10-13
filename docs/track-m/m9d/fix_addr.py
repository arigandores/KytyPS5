import os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
for p in sys.argv[1:]:
    t = open(p, encoding='utf-8').read()
    a = '          info.data = {0, offset};\n'
    b = '      info.data = {0, 256};\n'
    assert t.count(a) == 1 and t.count(b) == 1, (p, t.count(a), t.count(b))
    t = t.replace(a, '          info.data = {0x205000000ull, offset}; // a valid guest range (no memory behind it is read)\n')
    t = t.replace(b, '      info.data = {0x205100000ull, 256};\n')
    open(p, 'w', encoding='utf-8', newline='\n').write(t)
    print('ok', p)
