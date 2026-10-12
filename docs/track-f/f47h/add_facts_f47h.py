"""add_facts_f47h.py - appends the F47h section (template facts_f47h.md, __NOW__ = UTC now) to C:/kyty/f287/FACTS.md once."""
import os
import sys
import time

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('LOCK or STOP')
    sys.exit(3)
facts = 'C:/kyty/f287/FACTS.md'
tpl = open(sys.argv[1], encoding='utf-8').read()
text = open(facts, encoding='utf-8').read()
if '## F47h (`HPP-825`' in text:
    print('already there')
    sys.exit(0)
now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
sec = tpl.replace('__NOW__', now)
if not text.endswith(chr(10)):
    text += chr(10)
open(facts, 'w', encoding='utf-8', newline=chr(10)).write(text + sec)
print('appended', now)
