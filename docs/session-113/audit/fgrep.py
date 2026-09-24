import re, sys
pat = re.compile(sys.argv[1])
for p in sys.argv[2:]:
    with open(p, 'rb') as fh:
        lines = fh.read().decode('utf8', 'replace').split(chr(10))
    for i, l in enumerate(lines, 1):
        if pat.search(l):
            print(p.split('/')[-1] + ':' + str(i) + ': ' + l.rstrip()[:170])
