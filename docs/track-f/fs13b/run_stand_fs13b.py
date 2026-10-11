# FS13b (HPP-788, Red Team): copy of run_stand_fs13a.py (FS13a HPP-787) with WT and EXE set to fs13b; nothing else changed.
"""FS13a (HPP-787, ROADMAP s122 item 697(g)(1)): driver of the F25 stand edition 3 built from the FS13 worktree - one
process per call. Port of the F38a2 run_stand_f38a2.py: paths fs13a, the form 'd' (KYTY_FIX_F25 not set - the default),
all other KYTY_* removed from the environment, the identity against the FS13 worktree HEAD and the base FS12 730ed40a.

    python run_stand_fs13a.py <run dir> <seed> <fix d|0|1> <nA> <nK> <nZ> <nE> <nT> <nG>

Writes <run dir>/rows_<seed>_f<fix>.tsv (+ .log - the emulator log), stdout_<seed>_f<fix>.txt, identity_<seed>_f<fix>.txt.
FS13A_EXE overrides the stand exe (the negative control of the form 'd' on the F38a2 stand, default 0)."""
import hashlib
import os
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/f287/fs13b/wt'
MAIN = 'C:/kyty/KytyPS5'
EXE = os.environ.get('FS13A_EXE', 'C:/kyty/f287/fs13b/build/f25_read_fail_stand.exe')


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def git(*args, cwd=MAIN):
    return subprocess.run([G, '-C', cwd] + list(args), capture_output=True).stdout.decode('utf-8').strip()


def main():
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
        print('LOCK or STOP')
        sys.exit(3)
    run, seed, fix = sys.argv[1], sys.argv[2], sys.argv[3]
    counts = sys.argv[4:10]
    assert fix in ('d', '0', '1') and len(counts) == 6
    os.makedirs(run, exist_ok=True)
    tag = '%s_f%s' % (seed, fix)
    ident = []
    ident.append('worktree HEAD %s' % git('rev-parse', 'HEAD', cwd=WT))
    ident.append('worktree src/ diff vs 730ed40a (files): %s' % git('diff', '--name-only', '730ed40a', '--', 'src',
                                                                    cwd=WT).replace('\n', ', '))
    ident.append('worktree status lines %d' % len([l for l in git('status', '--short', '--ignore-submodules=all',
                                                                  cwd=WT).split('\n') if l.strip()]))
    ident.append('stand source sha256 worktree %s main %s equal %s' % (
        sha(WT + '/tests/F25ReadFailStand.cpp'), sha(MAIN + '/tests/F25ReadFailStand.cpp'),
        sha(WT + '/tests/F25ReadFailStand.cpp') == sha(MAIN + '/tests/F25ReadFailStand.cpp')))
    ident.append('stand exe %s sha256 %s' % (EXE, sha(EXE)))
    ident.append('args seed %s KYTY_FIX_F25=%s nA %s nK %s nZ %s nE %s nT %s nG %s' % tuple(
        [seed, '(not set)' if fix == 'd' else fix] + counts))
    rows = os.path.abspath(os.path.join(run, 'rows_%s.tsv' % tag))
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    if fix != 'd':
        env['KYTY_FIX_F25'] = fix
    ident.append('KYTY_* in the stand environment: %s' % (sorted(k for k in env if k.startswith('KYTY_')) or 'none'))
    open(os.path.join(run, 'identity_%s.txt' % tag), 'w', encoding='utf-8', newline='\n').write('\n'.join(ident) + '\n')
    print('\n'.join(ident))
    with open(os.path.join(run, 'stdout_%s.txt' % tag), 'wb') as out:
        rc = subprocess.run([EXE, seed] + counts + [rows], stdout=out, stderr=subprocess.STDOUT, cwd=run, env=env,
                            timeout=900).returncode
    print('stand rc %d' % rc)
    tail = open(os.path.join(run, 'stdout_%s.txt' % tag), 'rb').read().decode('utf-8', 'replace').split('\n')
    print('\n'.join(l for l in tail if l.startswith(('FIXF25', 'NID', 'HOOK', 'SHA256', 'FINAL', 'DONE', 'RESTORE'))))
    sys.exit(rc)


if __name__ == '__main__':
    main()
