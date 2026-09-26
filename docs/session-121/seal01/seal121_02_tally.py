"""Session 121 seal 02 tally: replace ONLY the test_shp121.py line of the seal-02 block (repaired suite, ROADMAP s121
item 7), assert every other line unchanged, and append the mutlib tally.  LF out."""
import hashlib
from pathlib import Path

R = Path('C:/kyty/s121')
p = R / 'SEALS121.txt'
lines = p.read_bytes().decode('utf-8').split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('# Session 121 seal 02'))
new_sha = hashlib.sha256((R / 'test_shp121.py').read_bytes()).hexdigest()
changed = 0
out = []
for i, l in enumerate(lines):
    if i > start and l.endswith('  test_shp121.py') and len(l.split('  ')[0]) == 64:
        out.append('%s  test_shp121.py' % new_sha)
        changed += 1
    else:
        out.append(l)
assert changed == 1
before = [l for i, l in enumerate(lines) if not (i > start and l.endswith('  test_shp121.py'))]
after = [l for i, l in enumerate(out) if not (i > start and l.endswith('  test_shp121.py'))]
assert before == after
text = '\n'.join(out).rstrip('\n') + '\n'
text += ('\nshp121: first FULL mutlib on the sealed copy: 342/344 (vfy_unsealed_ok, cli_rc survived: branches left without a\n'
         'killing fixture by the filled constants); suite repaired by three direct fixtures (ROADMAP s121 item 7), the\n'
         'scorer and pred unchanged; second FULL run: 344 mutants, 344 killed, 0 survived; controls 3 of 3 survived;\n'
         'report mut_shp121.sealed.txt; test_shp121.py (306 fixtures) ALL OK; test_shp121.py sha above is the repaired one.\n')
p.write_bytes(text.encode('utf-8'))
print('ok', new_sha)
