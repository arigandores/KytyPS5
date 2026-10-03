"""fin_r1.py - track S link S9b, rework 1 (HPP-458; ROADMAP "SESSION 122" item 377 (b)): writes the seal pred/06b_s.md
(s9/mkseal_s06b.py), checks it (sc_s9.py --check-seal -> s9/checkseal_s06b.out.txt), appends the section "S9b - rework 1" to
C:/kyty/s288/FACTS.md, writes the git mirror docs/track-s/s9b-r1-harness.md and copies the files into docs/track-s/s9/ and
docs/track-s/s9b/r1/.  Refuses under the lock or the stop file.
    python C:/kyty/s288/s9b/r1/fin_r1.py
"""
import hashlib
import os
import shutil
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
R = 'C:/kyty/s288'
S9 = R + '/s9/'
R1 = R + '/s9b/r1/'
G = 'C:/kyty/KytyPS5/docs/track-s/'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def last(p, prefix=None):
    lines = open(p, encoding='ascii', errors='replace').read().splitlines()
    if prefix:
        x = [l for l in lines if l.startswith(prefix)]
        return x[-1] if x else '-'
    return lines[-1] if lines else '-'


def blocked():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCKED or STOP')
        return True
    return False


def main():
    if blocked():
        return 5
    p = subprocess.run([sys.executable, S9 + 'mkseal_s06b.py'], capture_output=True, text=True)
    print(p.stdout.strip(), p.stderr.strip())
    if p.returncode != 0:
        return 1
    if blocked():
        return 5
    seal = R + '/pred/06b_s.md'
    c = subprocess.run([sys.executable, S9 + 'sc_s9.py', '--check-seal', '--seal', seal], capture_output=True, text=True)
    open(S9 + 'checkseal_s06b.out.txt', 'w', encoding='ascii', newline='\n').write(c.stdout)
    print('check-seal rc %d %s' % (c.returncode, c.stdout.strip().splitlines()[-1]))
    if c.returncode != 0:
        return 1
    nseal = sum(1 for l in open(seal, encoding='ascii') if l.startswith('seal: '))
    v = dict(
        sc=sha(S9 + 'sc_s9.py'), go=sha(S9 + 'go_s9.sh'), tsc=sha(S9 + 'test_sc_s9.py'), tgo=sha(S9 + 'test_go_s9.py'),
        mut=sha(S9 + 'mut_sc_s9.py'), mk=sha(S9 + 'mkseal_s06b.py'), seal=sha(seal), nseal=nseal,
        cs=sha(S9 + 'checkseal_s06b.out.txt'), csl=last(S9 + 'checkseal_s06b.out.txt'),
        tsco=sha(S9 + 'test_sc_s9.out.txt'), tgoo=sha(S9 + 'test_go_s9.out.txt'),
        tscn=last(S9 + 'test_sc_s9.out.txt', 'checks:'), tgon=last(S9 + 'test_go_s9.out.txt', 'checks:'),
        tscl=last(S9 + 'test_sc_s9.out.txt'), tgol=last(S9 + 'test_go_s9.out.txt'),
        tscf=open(S9 + 'test_sc_s9.out.txt', encoding='ascii').readline().strip(),
        tgof=open(S9 + 'test_go_s9.out.txt', encoding='ascii').readline().strip(),
        m7=sha(R1 + 'mut_screen7.txt'), m7l=last(R1 + 'mut_screen7.txt'), h1=sha(R1 + 'hmut_h1.txt'),
        rg=sha(S9 + 'regress_s9.out.txt'), rgl=last(S9 + 'regress_s9.out.txt', 'REGRESSION:'),
        body=sha(S9 + 'seal06b_body.md'), tail=sha(S9 + 'seal06b_tail.md'), p377=sha(R1 + 'patch377.py'))
    txt = open(R1 + 'facts_r1.md', encoding='utf-8').read().format(**v)
    f = open(R + '/FACTS.md', 'rb').read()
    if '\n## S9b \u2014 \u043f\u0440\u0430\u0432\u043a\u0430 1'.encode('utf-8') in f:
        print('FACTS already has the section S9b rework 1')
        return 1
    if blocked():
        return 5
    if not f.endswith(b'\n'):
        f += b'\n'
    open(R + '/FACTS.md', 'wb').write(f + b'\n' + txt.encode('utf-8'))
    head = ('# S9b \u0442\u0440\u0435\u043a\u0430 S \u2014 \u043f\u0440\u0430\u0432\u043a\u0430 1 (HPP-458, \u043f. 377)\n\n'
            '\u0417\u0435\u0440\u043a\u0430\u043b\u043e \u0440\u0430\u0437\u0434\u0435\u043b\u0430 `## S9b \u2014 \u043f\u0440\u0430\u0432\u043a\u0430 1` '
            '\u0444\u0430\u0439\u043b\u0430 `C:/kyty/s288/FACTS.md`; \u043a\u043e\u043f\u0438\u0438 \u2014 `docs/track-s/s9/` '
            '(`06b_s.md` = `C:/kyty/s288/pred/06b_s.md`) \u0438 `docs/track-s/s9b/r1/`.\n\n')
    open(G + 's9b-r1-harness.md', 'wb').write((head + txt).encode('utf-8'))
    os.makedirs(G + 's9b/r1', exist_ok=True)
    for n in ('sc_s9.py', 'go_s9.sh', 'test_sc_s9.py', 'test_go_s9.py', 'mut_sc_s9.py', 'mkseal_s06b.py', 'seal06b_body.md',
              'seal06b_tail.md', 'checkseal_s06b.out.txt', 'test_sc_s9.out.txt', 'test_go_s9.out.txt', 'regress_s9.out.txt'):
        shutil.copyfile(S9 + n, G + 's9/' + n)
    shutil.copyfile(seal, G + 's9/06b_s.md')
    for n in ('patch377.py', 'fin_r1.py', 'facts_r1.md', 'times.txt', 'mut_screen7.txt', 'hmut_h1.txt', 'mutwalls.txt'):
        shutil.copyfile(R1 + n, G + 's9b/r1/' + n)
    print('FACTS section S9b rework 1 appended; mirror and copies written; seal %s' % v['seal'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
