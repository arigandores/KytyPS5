# -*- coding: utf-8 -*-
"""HPP-153: keep the old trap line of CLAUDE.md/AGENTS.md verbatim (doc_split_check) and put traps 8-9 on their own lines."""
from pathlib import Path

D = Path('C:/kyty/KytyPS5/ps5 em')
OLD = '  (п. 16); перед `git commit` агента выставить `GIT_AUTHOR_*`/`GIT_COMMITTER_*` в том же вызове шелла;\n'
NEW = '  (п. 16); перед `git commit` агента выставить `GIT_AUTHOR_*`/`GIT_COMMITTER_*` в том же вызове шелла.\n'
L8 = ('  (8) третье «Доработать» одного звена эскалирует review на доску — доработка сверх второй новым звеном '
      '(п. 115);\n')
L8N = ('  Новые (с. 130): (8) третье «Доработать» одного звена эскалирует review на доску — доработка сверх второй новым '
       'звеном (п. 115);\n')
for n in ('CLAUDE.md', 'AGENTS.md'):
    p = D / n
    t = p.read_bytes().decode('utf-8')
    assert t.count(OLD) == 1 and t.count(L8) == 1, n
    t = t.replace(OLD, NEW).replace(L8, L8N)
    p.write_bytes(t.encode('utf-8'))
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()
print('ok')
