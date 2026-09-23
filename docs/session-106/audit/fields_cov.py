"""Auditor: which fields each derived scorer parses vs which the fixture emits (own regex over the source text)."""
import re, ast
def scorer_fields(path):
    src = open(path, encoding='utf-8').read()
    m = re.search(r'^FIELDS\s*=', src, re.M)
    # evaluate the FIELDS-building statements crudely: collect all quoted tokens inside FIELDS-related tuples/lists
    names = set()
    for mm in re.finditer(r"^(\w*FIELDS\w*|\w*_KEYS\w*|CORE\w*|MAIN\w*|DRAW\w*|X_\w*|XF\w*)\s*=\s*(.+?)(?=^\S)", src, re.M | re.S):
        names |= set(re.findall(r"'([a-z][a-z0-9_]+)'", mm.group(2)))
    return names, src
def fixture_fields(path):
    src = open(path, encoding='utf-8').read()
    return set(re.findall(r'([a-z][a-z0-9_]+)=%', src)) | set(re.findall(r' ([a-z][a-z0-9_]+)=\d', src)) | set(re.findall(r"'([a-z][a-z0-9_]+)=\d", src))
for sc, fx in (('C:/kyty/s106/gw106.py', 'C:/kyty/s106/fixture_gw106.py'), ('C:/kyty/s106/dab106.py', 'C:/kyty/s106/fixture_dab106.py')):
    names, src = scorer_fields(sc)
    ff = fixture_fields(fx)
    miss = sorted(n for n in names if n not in ff and ('_us' in n or '_n' in n or '_ns' in n or n.startswith(('gw_', 'pl_', 'da_'))))
    print(sc, 'scorer field-like names', len(names), 'fixture fields', len(ff))
    print('  in scorer tables, absent from fixture:', miss)
    print('  gw/pl names in scorer:', sorted(n for n in names if n.startswith(('gw_', 'pl_'))))
