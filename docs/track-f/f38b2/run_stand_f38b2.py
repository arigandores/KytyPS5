# F38b2 (HPP-778, Red Team): copy of the F38b run_stand_f38b.py for the stand edition 3 (six counts, nG added; worktree
# f38b2; src/ diff vs 531d6488 and 730ed40a in the identity). Was: F38b copy of the F38a run_stand_f38a.py.
"""F38b2 (HPP-778): driver of the F25 stand edition 3 (ROADMAP s122 item 693(b)(3), (5)) - one process per call.

    python run_stand_f38b2.py <run dir> <seed> <fix 0|1> <nA> <nK> <nZ> <nE> <nT> <nG>

Sets KYTY_FIX_F25=<fix> in the environment of the stand process, prints the identity (worktree HEAD, src/ diff vs
531d6488 and 730ed40a, stand source = 49aba6a4 by blob, stand exe sha256) and writes <run dir>/rows_<seed>_f<fix>.tsv
(+ .log - the emulator log), stdout_<seed>_f<fix>.txt, identity_<seed>_f<fix>.txt. F38B2_EXE overrides the stand exe."""
import hashlib
import os
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/f287/f38b2/wt'
MAIN = 'C:/kyty/KytyPS5'
EXE = os.environ.get('F38B2_EXE', 'C:/kyty/f287/f38b2/build/f25_read_fail_stand.exe')


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def git(*args, cwd=MAIN):
    return subprocess.run([G, '-C', cwd] + list(args), capture_output=True).stdout.decode('utf-8').strip()


def main():
    run, seed, fix = sys.argv[1], sys.argv[2], sys.argv[3]
    counts = sys.argv[4:10]
    assert fix in ('0', '1') and len(counts) == 6
    os.makedirs(run, exist_ok=True)
    tag = '%s_f%s' % (seed, fix)
    ident = []
    ident.append('worktree HEAD %s' % git('rev-parse', 'HEAD', cwd=WT))
    ident.append('worktree status lines %d' % len([l for l in git('status', '--short', '--ignore-submodules=all',
                                                                  cwd=WT).split('\n') if l]))
    ident.append('worktree src/ diff (files, working tree) vs 531d6488: [%s]; vs 730ed40a: [%s]' % (
        git('diff', '--name-only', '531d6488', '--', 'src', cwd=WT).replace('\n', ', '),
        git('diff', '--name-only', '730ed40a', '--', 'src', cwd=WT).replace('\n', ', ')))
    ident.append('stand source blob worktree %s 49aba6a4 %s' % (
        git('hash-object', 'tests/F25ReadFailStand.cpp', cwd=WT), git('rev-parse', '49aba6a4:tests/F25ReadFailStand.cpp')))
    ident.append('stand exe %s sha256 %s' % (EXE, sha(EXE)))
    ident.append('args seed %s KYTY_FIX_F25=%s nA %s nK %s nZ %s nE %s nT %s nG %s' % tuple([seed, fix] + counts))
    open(os.path.join(run, 'identity_%s.txt' % tag), 'w', encoding='utf-8').write('\n'.join(ident) + '\n')
    print('\n'.join(ident))
    rows = os.path.abspath(os.path.join(run, 'rows_%s.tsv' % tag))
    env = dict(os.environ)
    env['KYTY_FIX_F25'] = fix
    with open(os.path.join(run, 'stdout_%s.txt' % tag), 'wb') as out:
        rc = subprocess.run([EXE, seed] + counts + [rows], stdout=out, stderr=subprocess.STDOUT, cwd=run, env=env,
                            timeout=900).returncode
    print('stand rc %d' % rc)
    tail = open(os.path.join(run, 'stdout_%s.txt' % tag), 'rb').read().decode('utf-8', 'replace').split('\n')
    print('\n'.join(l for l in tail if l.startswith(('FIXF25', 'NID', 'HOOK', 'SHA256', 'FINAL', 'DONE', 'RESTORE'))))
    sys.exit(rc)


if __name__ == '__main__':
    main()
