"""F20j2 (HPP-633, ROADMAP s122 item 552(d)): inventory of the KYTY_DIAG_B32 sites of the binary's source commit and of
the sites added by F20j2, and the check of each reference (anchor = the line, +1 = the next line). Copy of sites_f20j.py
(F20j) with the mode 'new'.

  python sites_f20j2.py inventory <commit>      - every line of the source files changed since 302347b4 (outside
                                                  src/common/diagB32.*) that names Common::DiagB32 -> sites_<commit>.txt
  python sites_f20j2.py new <base> <commit>     - only the lines ADDED by base..commit that name Common::DiagB32 or
                                                  b32_q (the F20j2 sites) -> sites_new_<commit>.txt
  python sites_f20j2.py check <file>            - re-reads every reference with git show; prints ALL OK
"""
import re
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'


def show(commit, path):
    return subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout.decode(
        'utf-8').replace('\r\n', '\n').split('\n')


def changed(base, commit):
    out = subprocess.run([G, '-C', REPO, 'diff', '--name-only', base, commit], capture_output=True, text=True,
                         check=True).stdout.split()
    return [p for p in out if p.startswith('src/') and not p.startswith('src/common/diagB32')]


def is_site(l):
    s = l.strip()
    return ('DiagB32' in s or 'b32_q' in s) and not s.startswith('//') and '#include' not in s


def write(name, rows):
    open(name, 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    for r in rows:
        print(r)
    print('rows %d -> %s' % (len(rows), name))


def inventory(commit):
    rows = []
    for path in changed('302347b4', commit):
        lines = show(commit, path)
        for i, l in enumerate(lines):
            if 'DiagB32' in l and not l.strip().startswith('//') and '#include' not in l:
                nxt = lines[i + 1] if i + 1 < len(lines) else ''
                rows.append('%s:%s:%d\t%s\t%s' % (commit, path, i + 1, l.strip(), nxt.strip()))
    write('sites_%s.txt' % commit[:8], rows)


def new(base, commit):
    rows = []
    for path in changed(base, commit):
        diff = subprocess.run([G, '-C', REPO, 'diff', '-U0', base, commit, '--', path], capture_output=True,
                              check=True).stdout.decode('utf-8').replace('\r\n', '\n').split('\n')
        lines = show(commit, path)
        added = set()
        cur = 0
        for d in diff:
            m = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', d)
            if m:
                cur = int(m.group(1))
                continue
            if d.startswith('+') and not d.startswith('+++'):
                added.add(cur)
                cur += 1
        for n in sorted(added):
            l = lines[n - 1]
            if is_site(l):
                nxt = lines[n] if n < len(lines) else ''
                rows.append('%s:%s:%d\t%s\t%s' % (commit, path, n, l.strip(), nxt.strip()))
    write('sites_new_%s.txt' % commit[:8], rows)


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
    elif sys.argv[1] == 'new':
        new(sys.argv[2], sys.argv[3])
    else:
        check(sys.argv[2])
