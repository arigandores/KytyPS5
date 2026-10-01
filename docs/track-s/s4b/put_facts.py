#!/usr/bin/env python3
"""S4b: append s4b/facts_s4b.md to C:/kyty/s288/FACTS.md once (LF, UTF-8)."""
import hashlib

f = 'C:/kyty/s288/FACTS.md'
src = 'C:/kyty/s288/s4b/facts_s4b.md'
b = open(f, 'rb').read()
t = open(src, 'rb').read()
CRLF = bytes([13, 10])
print('FACTS has S4b section:', b'\n## S4b ' in b, 'CRLF in FACTS:', CRLF in b, 'CRLF in section:', CRLF in t)
assert b'\n## S4b ' not in b and CRLF not in t
open(f, 'wb').write(b.rstrip(b'\n') + b'\n' + t)
print('FACTS appended sha256', hashlib.sha256(open(f, 'rb').read()).hexdigest())
