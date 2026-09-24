"""Audit 113 final: for each session-113 ROADMAP item 14..21, the first commit whose tree holds it, whether the action
commits' trees hold it, and whether the item text at its commit equals the text at HEAD (read-only git show)."""
import re, subprocess
def show(c):
    return subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', '%s:docs/ROADMAP.md' % c], capture_output=True).stdout.decode('utf-8').replace('\r\n', '\n')
def item(text, n):
    i = text.find('СЕССИЯ 113 — ЗАПИСИ ДО ДЕЙСТВИЙ')
    if i < 0: return None
    m = re.search(r'\n%d\. ' % n, text[i:])
    if not m: return None
    a = i + m.start() + 1
    m2 = re.search(r'\n(%d\. |\n)' % (n + 1), text[a:])
    return text[a:a + m2.start()] if m2 else text[a:a + 4000]
log = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'log', '--format=%h %ad', '--date=format:%H:%M:%S', '-40'], capture_output=True).stdout.decode().split('\n')
commits = [l.split() for l in log if l.strip()][::-1]
head = show('HEAD')
ACTIONS = {14: ['56a4b4f', '6ccd896'], 15: ['37aa33f'], 16: ['d93e814'], 17: ['967d1aa', '04ccab5'],
           18: ['623009f', '6ce3e0d'], 19: ['43c1633'], 20: ['ade1cb6'], 21: ['0dea739']}
cache = {}
for n in range(11, 22):
    first = None
    for c, t in commits:
        if c not in cache: cache[c] = show(c)
        if item(cache[c], n):
            first = (c, t); break
    it_first = item(cache[first[0]], n) if first else None
    same = (it_first == item(head, n))
    acts = ['%s:%s' % (a, 'has' if item(cache.get(a) or show(a), n) else 'MISSING') for a in ACTIONS.get(n, [])]
    print('item %d first in %s at %s; text at HEAD identical: %s; action trees %s' % (n, first[0] if first else None,
          first[1] if first else None, same, acts))
