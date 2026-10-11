# F38b (HPP-764, Red Team): copy of the F38a run_stand_f38a.py; executable lines f38a -> f38b (paths, names). Was:
"""F38b (HPP-764): driver of the F25 stand edition 2 (ROADMAP s122 item 691(d)(1)) - one process per call.

    python run_stand_f38b.py <run dir> <seed> <fix 0|1> <nA> <nK> <nZ> <nE> <nT>

Sets KYTY_FIX_F25=<fix> in the environment of the stand process (read by FileSystem::Initialize of the linked emulator
code), prints the identity (worktree HEAD, src/ diff vs 730ed40a, stand source = main by sha256, stand exe sha256) and
writes <run dir>/rows_<seed>_f<fix>.tsv (+ .log - the emulator log), stdout_<seed>_f<fix>.txt, identity_<seed>_f<fix>.txt."""
import hashlib
import os
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/f287/f38b/wt'
MAIN = 'C:/kyty/KytyPS5'
EXE = os.environ.get('F38B_EXE', 'C:/kyty/f287/f38b/build/f25_read_fail_stand.exe')  # F38b: override for the F38a copy


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def git(*args, cwd=MAIN):
    return subprocess.run([G, '-C', cwd] + list(args), capture_output=True).stdout.decode('utf-8').strip()


def main():
    run, seed, fix = sys.argv[1], sys.argv[2], sys.argv[3]
    counts = sys.argv[4:9]
    assert fix in ('0', '1') and len(counts) == 5
    os.makedirs(run, exist_ok=True)
    tag = '%s_f%s' % (seed, fix)
    ident = []
    ident.append('worktree HEAD %s' % git('rev-parse', 'HEAD', cwd=WT))
    ident.append('worktree src/ diff vs 730ed40a (files): %s' % git('diff', '--name-only', '730ed40a', '--', 'src',
                                                                    cwd=WT).replace('\n', ', '))
    ident.append('worktree fileSystem.cpp blob %s; main HEAD %s fileSystem.cpp blob %s' % (
        git('hash-object', 'src/kernel/fileSystem.cpp', cwd=WT), git('rev-parse', '--short', 'HEAD'),
        git('rev-parse', 'HEAD:src/kernel/fileSystem.cpp')))
    ident.append('stand source sha256 worktree %s main %s equal %s' % (
        sha(WT + '/tests/F25ReadFailStand.cpp'), sha(MAIN + '/tests/F25ReadFailStand.cpp'),
        sha(WT + '/tests/F25ReadFailStand.cpp') == sha(MAIN + '/tests/F25ReadFailStand.cpp')))
    ident.append('stand exe %s sha256 %s' % (EXE, sha(EXE)))
    ident.append('args seed %s KYTY_FIX_F25=%s nA %s nK %s nZ %s nE %s nT %s' % tuple([seed, fix] + counts))
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
