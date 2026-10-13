"""M9d: the change on main (staged in wtmain, or a main commit) against the worktree commit d490f648 - per file the multiset
of '+' lines and of '-' lines; and git patch-id --stable of both with -U0 (no context) and with the default context.
Usage: python main_vs_wt.py <repo> <rev-or-STAGED>. Prints a line per file and ALL OK / FAIL."""
import collections
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/m657/m9d/wt'
WT_COMMIT = 'd490f648c6645c3d39d0623adbe8a108c35695b5'


def diff(repo, args):
    return subprocess.run([G, '-C', repo] + args, capture_output=True).stdout.decode('utf-8', 'replace')


def per_file(text):
    files = collections.defaultdict(lambda: (collections.Counter(), collections.Counter()))
    cur = None
    for line in text.split('\n'):
        if line.startswith('diff --git '):
            cur = line.split(' b/', 1)[1]
            continue
        if cur is None or line.startswith('+++') or line.startswith('---'):
            continue
        if line.startswith('+'):
            files[cur][0][line] += 1
        elif line.startswith('-'):
            files[cur][1][line] += 1
    return files


def patch_id(text):
    r = subprocess.run([G, 'patch-id', '--stable'], input=text.encode('utf-8'), capture_output=True)
    out = r.stdout.decode().split()
    return out[0] if out else 'none'


repo, rev = sys.argv[1], sys.argv[2]
wt_args = ['show', '--format=', WT_COMMIT]
if rev == 'STAGED':
    m_args = ['diff', '--cached']
else:
    m_args = ['show', '--format=', rev]
a = per_file(diff(WT, wt_args))
b = per_file(diff(repo, m_args))
ok = set(a) == set(b)
for f in sorted(set(a) | set(b)):
    pa, ma = a.get(f, (collections.Counter(), collections.Counter()))
    pb, mb = b.get(f, (collections.Counter(), collections.Counter()))
    eq = pa == pb and ma == mb
    ok = ok and eq
    print('%-70s +%d/-%d vs +%d/-%d %s' % (f, sum(pa.values()), sum(ma.values()), sum(pb.values()), sum(mb.values()),
                                          'EQUAL' if eq else 'DIFF'))
pid_wt0 = patch_id(diff(WT, ['show', '-U0', '--format=', WT_COMMIT]))
pid_m0 = patch_id(diff(repo, (['diff', '--cached', '-U0'] if rev == 'STAGED' else ['show', '-U0', '--format=', rev])))
pid_wt = patch_id(diff(WT, wt_args))
pid_m = patch_id(diff(repo, m_args))
print('patch-id -U0: wt %s main %s %s' % (pid_wt0[:8], pid_m0[:8], 'EQUAL' if pid_wt0 == pid_m0 else 'DIFF'))
print('patch-id default context: wt %s main %s %s' % (pid_wt[:8], pid_m[:8], 'EQUAL' if pid_wt == pid_m else 'DIFF'))
ok = ok and pid_wt0 == pid_m0
print('ALL OK' if ok else 'FAIL')
