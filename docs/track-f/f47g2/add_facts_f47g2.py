"""add_facts_f47g2.py - appends the F47g2 section (template facts_f47g2.md, __NOW__ = UTC now) to C:/kyty/f287/FACTS.md once,
by general rule 34 (ROADMAP s122 item 670(g)): a copy to FACTS.md.prev, the append in mode 'a', size_after = size_before +
the section bytes, else the copy is restored and the script exits 1."""
import os
import shutil
import sys
import time

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('LOCK or STOP')
    sys.exit(3)
facts = 'C:/kyty/f287/FACTS.md'
tpl = open(sys.argv[1], encoding='utf-8').read().replace('\r\n', '\n')
if '## F47g2 (`HPP-828`' in open(facts, encoding='utf-8').read():
    print('already there')
    sys.exit(0)
now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
sec = tpl.replace('__NOW__', now).encode('utf-8')
before = os.path.getsize(facts)
shutil.copyfile(facts, facts + '.prev')
with open(facts, 'ab') as f:
    f.write(sec)
after = os.path.getsize(facts)
if after != before + len(sec):
    shutil.copyfile(facts + '.prev', facts)
    print('SIZE MISMATCH %d != %d + %d - restored' % (after, before, len(sec)))
    sys.exit(1)
print('appended', now, before, '+', len(sec), '=', after)
