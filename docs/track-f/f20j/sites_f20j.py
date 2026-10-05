"""F20j (HPP-629, ROADMAP s122 item 550(z)(3)): inventory of every KYTY_DIAG_B32 / KYTY_TEST_B32 site in the binary's
source commit and the check of each reference (anchor in the line, the next line as +1).

  python sites_f20j.py inventory <commit>   - every line of the changed source files (outside src/common/diagB32.*,
                                              tests/) that names Common::DiagB32, as <commit>:<path>:<line>, the line
                                              (anchor) and the next line (+1); written to sites_<commit>.txt
  python sites_f20j.py check <file>         - re-reads every reference of a sites file with git show and compares the
                                              anchor and +1; prints ALL OK
"""
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'


def show(commit, path):
    return subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout.decode(
        'utf-8').replace('\r\n', '\n').split('\n')


def changed(commit):
    out = subprocess.run([G, '-C', REPO, 'diff', '--name-only', '302347b4', commit], capture_output=True, text=True,
                         check=True).stdout.split()
    return [p for p in out if p.startswith('src/') and not p.startswith('src/common/diagB32')]


def inventory(commit):
    rows = []
    for path in changed(commit):
        lines = show(commit, path)
        for i, l in enumerate(lines):
            if 'DiagB32' in l and not l.strip().startswith('//') and '#include' not in l:
                nxt = lines[i + 1] if i + 1 < len(lines) else ''
                rows.append('%s:%s:%d\t%s\t%s' % (commit, path, i + 1, l.strip(), nxt.strip()))
    name = 'sites_%s.txt' % commit[:8]
    open(name, 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    for r in rows:
        print(r)
    print('rows %d -> %s' % (len(rows), name))


def check(name):
    bad = 0
    n = 0
    cache = {}
    for row in open(name, encoding='utf-8').read().split('\n'):
        if not row:
            continue
        ref, anchor, nxt = row.split('\t')
        commit, path, line = ref.split(':')
        if (commit, path) not in cache:
            cache[(commit, path)] = show(commit, path)
        lines = cache[(commit, path)]
        i = int(line) - 1
        ok = lines[i].strip() == anchor and (lines[i + 1].strip() if i + 1 < len(lines) else '') == nxt
        n += 1
        if not ok:
            bad += 1
            print('BAD', ref)
    print('refs %d bad %d' % (n, bad))
    print('ALL OK' if bad == 0 else 'FAILED')


if __name__ == '__main__':
    if sys.argv[1] == 'inventory':
        inventory(sys.argv[2])
    else:
        check(sys.argv[2])
