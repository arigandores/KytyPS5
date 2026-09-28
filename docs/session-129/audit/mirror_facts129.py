# -*- coding: utf-8 -*-
"""Mirror C:/kyty/s129/FACTS.md into C:/kyty/KytyPS5/docs/local-session-129.md with personal identifiers and the names
of foreign applications removed (same substitution file as sync_agent_docs.py). Fails if an identifier survives.
Port of audit128/mirror_facts128.py."""
import re
from pathlib import Path

SRC = Path('C:/kyty/s129/FACTS.md')
DST = Path('C:/kyty/KytyPS5/docs/local-session-129.md')
rules = []
for line in Path('C:/kyty/scrub/exprs.txt').read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    assert line.startswith('regex:'), line
    pat, rep = line[len('regex:'):].split('==>', 1)
    rules.append((re.compile(pat), rep))
rules.append((re.compile(r'[A-Za-z0-9._%+-]+@(?!anthropic\.com)(?!users\.noreply\.github\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
              '<e-mail>'))
checks = [re.compile(p) for p in (r'(?i)<user>', r'(?i)Player', r'(?i)<surname>', r'(?i)\bseva\b', r'(?i)<foreign app>',
                                  r'(?i)<account>', r'(?i)<mail>', r'(?i)<foreign app>', r'(?i)<foreign app>', r'(?i)<foreign app>',
                                  r'(?i)<foreign app>', r'(?i)<foreign app>')]

text = SRC.read_bytes().decode('utf-8').replace('\r\n', '\n')
for rx, rep in rules:
    text = rx.sub(rep, text)
bad = [c.pattern for c in checks if c.search(text)]
assert not bad, 'identifiers survive: %s' % bad
head = ('<!-- Mirror of C:/kyty/s129/FACTS.md (source of truth), personal identifiers and foreign application names '
        'removed by audit129/mirror_facts129.py. -->\n')
DST.write_bytes((head + text).encode('utf-8'))
print('mirrored', len(text), 'chars ->', DST)
