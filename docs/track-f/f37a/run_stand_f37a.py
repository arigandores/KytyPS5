"""F37a (HPP-761): driver of the F25 double read failure stand (ROADMAP s122 item 688(e)(1)).

    python run_stand_f37a.py <run dir> <seed> <nA> <nK> <nZ>

Prints the identity (fileSystem.cpp of the stand worktree = ee9632be by blob hash, the worktree src/ diff against
ee9632be, the stand source = main by sha256, the stand exe sha256), runs the stand once (one process, all six entries)
and writes <run dir>/rows_<seed>.tsv, stdout_<seed>.txt, identity_<seed>.txt."""
import hashlib
import os
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/f287/f37a/wt'
MAIN = 'C:/kyty/KytyPS5'
EXE = 'C:/kyty/f287/f37a/build/f25_read_fail_stand.exe'


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def git(*args, cwd=MAIN):
    return subprocess.run([G, '-C', cwd] + list(args), capture_output=True).stdout.decode('utf-8').strip()


def main():
    run, seed, na, nk, nz = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    os.makedirs(run, exist_ok=True)
    ident = []
    ident.append('worktree HEAD %s' % git('rev-parse', 'HEAD', cwd=WT))
    blob_c = git('rev-parse', 'ee9632be:src/kernel/fileSystem.cpp')
    blob_wt = git('hash-object', 'src/kernel/fileSystem.cpp', cwd=WT)
    blob_main = git('rev-parse', 'HEAD:src/kernel/fileSystem.cpp')
    ident.append('fileSystem.cpp blob ee9632be %s worktree %s equal %s; main HEAD %s blob %s equal %s' % (
        blob_c, blob_wt, blob_c == blob_wt, git('rev-parse', '--short', 'HEAD'), blob_main, blob_main == blob_c))
    diff_src = subprocess.run([G, '-C', WT, 'diff', '--quiet', 'ee9632be', '--', 'src'], capture_output=True).returncode
    untracked = git('ls-files', '--others', '--exclude-standard', '--', 'src', cwd=WT)
    ident.append('worktree src/ vs ee9632be: git diff --quiet rc %d (0 = equal), untracked in src/: %d' % (
        diff_src, len([x for x in untracked.split('\n') if x])))
    ident.append('stand source sha256 worktree %s main %s equal %s' % (
        sha(WT + '/tests/F25ReadFailStand.cpp'), sha(MAIN + '/tests/F25ReadFailStand.cpp'),
        sha(WT + '/tests/F25ReadFailStand.cpp') == sha(MAIN + '/tests/F25ReadFailStand.cpp')))
    ident.append('stand exe %s sha256 %s' % (EXE, sha(EXE)))
    ident.append('args seed %s nA %s nK %s nZ %s' % (seed, na, nk, nz))
    open(os.path.join(run, 'identity_%s.txt' % seed), 'w', encoding='utf-8').write('\n'.join(ident) + '\n')
    print('\n'.join(ident))
    rows = os.path.abspath(os.path.join(run, 'rows_%s.tsv' % seed))  # the stand runs with cwd = run
    with open(os.path.join(run, 'stdout_%s.txt' % seed), 'wb') as out:
        rc = subprocess.run([EXE, seed, na, nk, nz, rows], stdout=out, stderr=subprocess.STDOUT, cwd=run,
                            timeout=900).returncode
    print('stand rc %d' % rc)
    tail = open(os.path.join(run, 'stdout_%s.txt' % seed), 'rb').read().decode('utf-8', 'replace').split('\n')
    print('\n'.join(l for l in tail if l.startswith(('NID', 'HOOK', 'DONE'))))
    sys.exit(rc)


if __name__ == '__main__':
    main()
