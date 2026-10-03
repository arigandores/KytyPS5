"""mkseal_s05.py - track S, link S9 (HPP-431): writes the seal C:/kyty/s288/pred/05_s.md of link S10 (ROADMAP "SESSION 122" item
355 (k)).  Reads: the sha256 of every sealed file (sc_s9.SEALED_NAMES), the last output of each suite (first line, checks, last
line, sha256), the plans of every tag by go_s9.sh DRY=2 (T2 tags in both forms), the lists of lvl_s9.out.txt, the export of
seedexp_s9.out.txt.  Refuses (rc 5) under the lock.  ASCII, LF.
    python C:/kyty/s288/s9/mkseal_s05.py
"""
import hashlib
import importlib.util
import os
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
R = 'C:/kyty/s288'
OUT = R + '/pred/05_s.md'
BASH = 'C:/Program Files/Git/bin/bash.exe'
NL = chr(10)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def suite(p):
    lines = open(p, encoding='ascii', errors='replace').read().splitlines()
    checks = [x for x in lines if x.startswith('checks:')]
    return lines[0] if lines else '', checks[-1] if checks else '-', lines[-1] if lines else '', sha(p)


def main():
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    spec = importlib.util.spec_from_file_location('sc9', R + '/s9/sc_s9.py')
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)
    env = dict(os.environ, DRY='2', PLWAIT='540', PATH='/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    plans = []
    for t in S.SEQ:
        forms = ('c5', 'app') if S.SPEC[t]['t2form'] else (None,)
        for f in forms:
            e = dict(env)
            if f:
                e['FORM'] = f
            p = subprocess.run([BASH, R + '/s9/go_s9.sh', t], capture_output=True, text=True, env=e, timeout=120)
            o = p.stdout.replace('bash.exe: warning: could not find /tmp, please create!' + NL, '').strip()
            plans.append(o if p.returncode == 0 else 'PLAN %s (form %s): rc %d %s' % (t, f, p.returncode, o))
    o = []
    w = o.append
    w('# Seal 05_s - track S link S9 (HPP-431) for link S10: the repeat of integrity, C5, the T2 base with t2_cs0, the S-cat probe '
      '(ROADMAP "SESSION 122" item 355 (g)-(zh), (k))')
    w('')
    w('Written by C:/kyty/s288/s9/mkseal_s05.py (sha256 %s) at %s UTC, before any S10 arm.  After this seal the scorer, the '
      'fixtures, the mutants, the harness and the lists do not change (a change = a new seal).  The S10 arms are scored by '
      's9/sc_s9.py, which loads C:/kyty/s288/sc_s.py (seal 04, sha256 %s) unchanged.  ASCII only.' % (
          sha(R + '/s9/mkseal_s05.py'), time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), S.SHA_SC_S))
    w('')
    w('## 1. The arms and the readings (item 355; constants of s9/sc_s9.py)')
    w('')
    for line in open(R + '/s9/seal05_body.md', encoding='ascii').read().splitlines():
        w(line)
    w('')
    w('## 2. The binaries and the call lines (one per tag; PLWAIT=540, item 105 (v); the call form: env -u KYTY_GAME_PATCH '
      'PLWAIT=540 bash C:/kyty/s288/s9/go_s9.sh <tag> - go_s9.sh unsets KYTY_GAME_PATCH itself)')
    w('')
    w('s binary: %s C:/kyty/s288/bin/kyty_emulator_f3b3aa3b.exe' % S.BIN_S)
    w('u binary: %s C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe' % S.BIN_U)
    w('')
    for t in S.SEQ:
        w('go_s9 call: PLWAIT=540 bash C:/kyty/s288/s9/go_s9.sh %s' % t)
    w('')
    w('Order (sc_s9.py --allowed): %s; one tag per lock; the lock queue P > F > S (item 322 (g)); the series stops at the first '
      'death marker; T2 reserves t2_6 .. t2_10 only while fewer than five T2 arms count; u_1 after the T2 base and t2_cs0; the U '
      'series stops at an arm without the catalogue gates.' % ' '.join(S.SEQ))
    w('')
    w('## 3. The plan of every arm (go_s9.sh DRY=2, verbatim; a T2 tag in both forms - the form is chosen by the C5 reading)')
    w('')
    w('```')
    for p in plans:
        w(p)
    w('```')
    w('')
    w('## 4. Seal lines (sc_s9.py --check-seal checks each before every lock)')
    w('')
    for n in S.SEALED_NAMES:
        p = n if n.startswith('C:/') else R + '/' + n
        w('seal: %s %s' % (sha(p), n))
    w('')
    w('## 5. Evidence (the last output of each suite and tool)')
    w('')
    for name, p in (('fixtures sc_s9', R + '/s9/test_sc_s9.out.txt'), ('fixtures go_s9', R + '/s9/test_go_s9.out.txt')):
        first, checks, last, sh = suite(p)
        w('- %s: %s sha256 %s; %s / %s; first line: %s' % (name, p, sh, checks, last, first))
    for name, p, key in (('mutants (counted full run)', R + '/s9/mut_sc_s9.txt', None),
                         ('regression on the logs of S4 and S6 and the six videos', R + '/s9/regress_s9.out.txt', 'REGRESSION:'),
                         ('the level lists', R + '/s9/lvl_s9.out.txt', 'ALL DONE'),
                         ('the export of the S-cat catalogue', R + '/s9/seedexp_s9.out.txt', 'EXPORT:'),
                         ('the provenance of the detector fixtures (a fresh ffmpeg run = the cached saturations)',
                          R + '/s9/fx/provenance.out.txt', None)):
        lines = open(p, encoding='ascii', errors='replace').read().splitlines()
        tail = [x for x in lines if key and x.startswith(key)] or lines[-1:]
        w('- %s: %s sha256 %s; %s' % (name, p, sha(p), tail[-1] if tail else '-'))
    w('- mutant runs of the link (wall, s9/times.txt): screening full 181 s (mut_screen1.txt: 208 of 211, survivors cr_glc, ad_gp, '
      'tc_fail - fixtures F2, G3, K2 added), a refused --only run (the suite failed F2 before any mutant, ~10 s), screening --only '
      'of the three 41 s (mut_screen3.txt: 3 of 3), the counted full run 179 s (mut_sc_s9.txt) - in all about 411 s')
    w('')
    for line in open(R + '/s9/seal05_tail.md', encoding='ascii').read().splitlines():
        w(line)
    text = NL.join(o) + NL
    text.encode('ascii')
    with open(OUT, 'wb') as f:
        f.write(text.encode('ascii'))
    print('seal written %s sha256 %s' % (OUT, sha(OUT)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
