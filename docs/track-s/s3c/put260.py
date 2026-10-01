import subprocess, sys
REPO = 'C:/kyty/KytyPS5'
P = REPO + '/docs/ROADMAP.md'
GIT = 'C:/Program Files/Git/cmd/git.exe'
NEW = open('C:/kyty/s288/lead/s3c/item260.txt', 'rb').read().decode('utf-8')
ANCH = '\n**ИТОГ ЦИКЛА СЕССИЙ 103–108 (пауза 2026-09-23).**'


def ins(t):
    t = t.replace('\r\n', '\n')
    assert t.count(ANCH) == 1, 'anchor'
    assert '\n260. ' not in t, '260 exists'
    if not NEW.endswith('\n'):
        raise SystemExit('item text')
    return t.replace(ANCH, '\n' + NEW + ANCH, 1)


# working tree (keeps the concurrent uncommitted item 259 as it is)
w = ins(open(P, 'rb').read().decode('utf-8'))
open(P, 'wb').write(w.encode('utf-8'))
# index: HEAD + this item only
head = subprocess.run([GIT, '-C', REPO, 'show', 'HEAD:docs/ROADMAP.md'], capture_output=True, check=True).stdout.decode('utf-8')
h = ins(head)
blob = subprocess.run([GIT, '-C', REPO, 'hash-object', '-w', '--stdin'], input=h.encode('utf-8'), capture_output=True,
                      check=True).stdout.decode().strip()
mode = subprocess.run([GIT, '-C', REPO, 'ls-files', '-s', 'docs/ROADMAP.md'], capture_output=True, check=True).stdout.decode().split()[0]
subprocess.run([GIT, '-C', REPO, 'update-index', '--cacheinfo', '%s,%s,docs/ROADMAP.md' % (mode, blob)], check=True)
print('ok blob', blob)
