"""fin_s9b.py - track S link S9b (HPP-458; ROADMAP "SESSION 122" item 371 (g)): writes the seal pred/06_s.md (s9/mkseal_s06.py),
checks it (sc_s9.py --check-seal -> s9/checkseal_s06.out.txt), appends the section S9b to C:/kyty/s288/FACTS.md, writes the git
mirror docs/track-s/s9b-harness.md and copies the files into docs/track-s/s9/ and docs/track-s/s9b/.  Refuses under the lock.
    python C:/kyty/s288/s9b/fin_s9b.py
"""
import hashlib
import os
import shutil
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
R = 'C:/kyty/s288'
S9 = R + '/s9/'
S9B = R + '/s9b/'
G = 'C:/kyty/KytyPS5/docs/track-s/'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def last(p, prefix=None):
    lines = open(p, encoding='ascii', errors='replace').read().splitlines()
    if prefix:
        x = [l for l in lines if l.startswith(prefix)]
        return x[-1] if x else '-'
    return lines[-1] if lines else '-'


def main():
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    p = subprocess.run([sys.executable, S9 + 'mkseal_s06.py'], capture_output=True, text=True)
    print(p.stdout.strip(), p.stderr.strip())
    if p.returncode != 0:
        return 1
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    seal = R + '/pred/06_s.md'
    c = subprocess.run([sys.executable, S9 + 'sc_s9.py', '--check-seal', '--seal', seal], capture_output=True, text=True)
    open(S9 + 'checkseal_s06.out.txt', 'w', encoding='ascii', newline='\n').write(c.stdout)
    print('check-seal rc %d %s' % (c.returncode, c.stdout.strip().splitlines()[-1]))
    if c.returncode != 0:
        return 1
    nseal = sum(1 for l in open(seal, encoding='ascii') if l.startswith('seal: '))
    v = dict(
        sc=sha(S9 + 'sc_s9.py'), go=sha(S9 + 'go_s9.sh'), tsc=sha(S9 + 'test_sc_s9.py'), tgo=sha(S9 + 'test_go_s9.py'),
        mut=sha(S9 + 'mut_sc_s9.py'), mk=sha(S9 + 'mkseal_s06.py'), seal=sha(seal), nseal=nseal,
        cs=sha(S9 + 'checkseal_s06.out.txt'), tsco=sha(S9 + 'test_sc_s9.out.txt'), tgoo=sha(S9 + 'test_go_s9.out.txt'),
        tscn=last(S9 + 'test_sc_s9.out.txt', 'checks:'), tgon=last(S9 + 'test_go_s9.out.txt', 'checks:'),
        tscl=last(S9 + 'test_sc_s9.out.txt'), tgol=last(S9 + 'test_go_s9.out.txt'),
        tscf=open(S9 + 'test_sc_s9.out.txt', encoding='ascii').readline().strip(),
        tgof=open(S9 + 'test_go_s9.out.txt', encoding='ascii').readline().strip(),
        mc=sha(S9 + 'mut_sc_s9c.txt'), mcl=last(S9 + 'mut_sc_s9c.txt'), m5=sha(S9B + 'mut_screen5.txt'),
        m5l=last(S9B + 'mut_screen5.txt'), m6=sha(S9B + 'mut_screen6.txt'), m6l=last(S9B + 'mut_screen6.txt'),
        rg=sha(S9 + 'regress_s9.out.txt'), rgl=last(S9 + 'regress_s9.out.txt', 'REGRESSION:'),
        body=sha(S9 + 'seal06_body.md'), tail=sha(S9 + 'seal06_tail.md'), p371=sha(S9B + 'patch371.py'), mk06=sha(S9B + 'mk06.py'))
    txt = open(S9B + 'facts_s9b.md', encoding='utf-8').read().format(**v)
    f = open(R + '/FACTS.md', 'rb').read()
    if '\n## S9b '.encode('utf-8') in f:
        print('FACTS already has the section S9b')
        return 1
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    if not f.endswith(b'\n'):
        f += b'\n'
    open(R + '/FACTS.md', 'wb').write(f + b'\n' + txt.encode('utf-8'))
    head = ('# S9b трека S — правки харнесса и скорера по RC1–RC6 S9r и п. 371, печать 06 (HPP-458)\n\n'
            'Зеркало раздела `## S9b` файла `C:/kyty/s288/FACTS.md`; копии файлов — `docs/track-s/s9/` (харнесс, скорер, наборы, '
            'мутанты, печать `06_s.md` = `C:/kyty/s288/pred/06_s.md`) и `docs/track-s/s9b/` (скрипты правок, время, отсевы мутантов).\n\n')
    open(G + 's9b-harness.md', 'wb').write((head + txt).encode('utf-8'))
    os.makedirs(G + 's9b', exist_ok=True)
    for n in ('sc_s9.py', 'go_s9.sh', 'test_sc_s9.py', 'test_go_s9.py', 'mut_sc_s9.py', 'mkseal_s06.py', 'seal06_body.md',
              'seal06_tail.md', 'checkseal_s06.out.txt', 'mut_sc_s9c.txt', 'test_sc_s9.out.txt', 'test_go_s9.out.txt',
              'regress_s9.out.txt'):
        shutil.copyfile(S9 + n, G + 's9/' + n)
    shutil.copyfile(seal, G + 's9/06_s.md')
    for n in ('patch371.py', 'mk06.py', 'fin_s9b.py', 'facts_s9b.md', 'times.txt', 'mut_screen5.txt', 'mut_screen6.txt',
              'mutwalls.txt'):
        shutil.copyfile(S9B + n, G + 's9b/' + n)
    print('FACTS section S9b appended; mirror and copies written; seal %s' % v['seal'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
