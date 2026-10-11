"""FS14a (copy of the F38a2 append_facts.py): append a section to C:/kyty/f287/FACTS.md by general rule 34 (copy .prev, mode 'a', size check).
usage: append_facts.py <section file>"""
import os
import shutil
import sys

FACTS = 'C:/kyty/f287/FACTS.md'
sec = open(sys.argv[1], 'rb').read()
before = os.path.getsize(FACTS)
shutil.copyfile(FACTS, FACTS + '.prev')
assert os.path.getsize(FACTS + '.prev') == before
with open(FACTS, 'ab') as f:
    f.write(sec)
after = os.path.getsize(FACTS)
assert after == before + len(sec), (before, len(sec), after)
assert open(FACTS, 'rb').read()[:before] == open(FACTS + '.prev', 'rb').read()
print('FACTS', before, '+', len(sec), '=', after, 'ALL OK')
