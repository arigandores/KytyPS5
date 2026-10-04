"""mkseal_s07.py - track S, link S10 (HPP-433; ROADMAP "SESSION 122" item 404 (g)): writes the seal C:/kyty/s288/pred/07_s.md of
link S10.  It replaces pred/06b_s.md (not changed) after the arms pi_w1, pi_r1, pi_w0, pi_r0, c5_0 and before the first T2 arm.
Reads: the sha256 of every sealed file (sc_s9.SEALED_NAMES and the files of item 404), the last output of each suite (first
line, checks, last line, sha256), the plans of every tag by go_s9.sh DRY=2 (the T2 tags in the form chosen by the scorer from
c5_0, no FORM), the rescore of the five made arms, the C5 reading and the answer of --allowed t2_1.  Refuses (rc 5) under the
lock.  ASCII, LF.
    python C:/kyty/s288/s9/mkseal_s07.py
"""
import hashlib
import importlib.util
import os
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
R = 'C:/kyty/s288'
OUT = R + '/pred/07_s.md'
BASH = 'C:/Program Files/Git/bin/bash.exe'
NL = chr(10)
WARN = 'bash.exe: warning: could not find /tmp, please create!'
EXTRA = ('s10/r404/test_r404.py', 's10/r404/orig/sc_s9.py', 's9/mkseal_s07.py', 's9/seal07_body.md', 's9/seal07_tail.md')


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


def run(args, env=None):
    p = subprocess.run(args, capture_output=True, text=True, env=env, timeout=300)
    return p.returncode, (p.stdout + p.stderr).replace(WARN + NL, '').replace(WARN, '').strip()


def main():
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    spec = importlib.util.spec_from_file_location('sc9', R + '/s9/sc_s9.py')
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)
    env = dict(os.environ, DRY='2', PLWAIT='540', PYTHONIOENCODING='utf-8',
               PATH='/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    env.pop('FORM', None)
    plans = []
    for t in S.SEQ:
        rc, o = run([BASH, R + '/s9/go_s9.sh', t], env)
        plans.append(o if rc == 0 else 'PLAN %s: rc %d %s' % (t, rc, o))
    py = sys.executable
    rc_c5, read_c5 = run([py, R + '/s9/sc_s9.py', '--read-c5'], dict(os.environ, PYTHONIOENCODING='utf-8'))
    rc_al, allowed = run([py, R + '/s9/sc_s9.py', '--allowed', 't2_1'], dict(os.environ, PYTHONIOENCODING='utf-8'))
    rc_pl, plan_t2 = run([py, R + '/s9/sc_s9.py', '--plan', 't2_1'], dict(os.environ, PYTHONIOENCODING='utf-8'))
    o = []
    w = o.append
    w('# Seal 07_s - track S link S10 (HPP-433), item 404: the T-1 / T-6 identities of an entered arm on its domain, the C5 '
      'reading, the T2 base in the form APP with t2_cs0, the S-cat probe (ROADMAP "SESSION 122" item 355 (g)-(zh), (k); items '
      '362, 371, 374 (g), 377, 404)')
    w('')
    w('Written by C:/kyty/s288/s9/mkseal_s07.py (sha256 %s) at %s UTC, after the S10 arms pi_w1, pi_r1, pi_w0, pi_r0, c5_0 and '
      'before the first T2 arm.  It replaces the seal pred/06b_s.md (sha256 '
      '605ebfa5440ea1ac318749250c625b022f873d0237b37294cc97ffb069e3560b, not changed; it replaced pred/06_s.md '
      '0fb11c0e703248bee62ce6f0f9fe40604c8c1526cc36ead8e738398152949c20, pred/05b_s.md '
      '6641154ecb5cec89102c0c4b4af607d7d723f69e294ef7598d08a2d9804dcd81 and pred/05_s.md '
      'd56e2e645ca7f0be60266c25bfa87869e94c4f3e0e9146796625fda000605784): S10 goes by this seal from t2_1 on (item 404 (g)); '
      'no T2 tag runs before the lead line "Seal 07 accepted" in HPP-433.  After this seal the scorer, the fixtures, the '
      'mutants, the harness and the lists do not change (a change = a new seal).  The S10 arms are scored by s9/sc_s9.py, which '
      'loads C:/kyty/s288/sc_s.py (seal 04, sha256 %s) unchanged.  ASCII only.' % (
          sha(R + '/s9/mkseal_s07.py'), time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), S.SHA_SC_S))
    w('')
    w('## 1. The arms and the readings (item 355; constants of s9/sc_s9.py)')
    w('')
    for line in open(R + '/s9/seal07_body.md', encoding='ascii').read().splitlines():
        w(line)
    w('')
    w('## 1a. Item 404: the rescore of the five made arms, the C5 reading, the answer of --allowed t2_1')
    w('')
    w('The five arms ran under the seal 06b; rescored by this scorer from their unchanged logs (s10/r404/score404_<tag>.txt):')
    w('')
    w('```')
    for t in ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0', 'c5_0'):
        p = R + '/s10/r404/score404_%s.txt' % t
        lines = open(p, encoding='ascii').read().splitlines()
        w('%s  (%s sha256 %s)' % (lines[0], p, sha(p)))
        for x in lines:
            if (' ident T-1' in x or ' ident T-6' in x or ' admit prereg' in x) and x not in lines[:1]:
                w(x)
        w('  log %s sha256 %s' % (R + '/s10/log_%s.txt' % t, sha(R + '/s10/log_%s.txt' % t)))
    w('```')
    w('')
    w('sc_s9.py --read-c5 (rc %d), verbatim:' % rc_c5)
    w('')
    w('```')
    for x in read_c5.splitlines():
        w(x)
    w('```')
    w('')
    w('sc_s9.py --allowed t2_1 (rc %d): `%s`; sc_s9.py --plan t2_1 (rc %d): `%s`' % (rc_al, allowed, rc_pl, plan_t2))
    w('')
    w('The repeat of integrity (item 355 (g), item 371 (b)) is computable on the four pi arms; its word is data of the S10 report '
      '(sc_s9.py --read-pi), not of this seal.')
    w('')
    w('## 2. The binaries and the call lines (one per tag; PLWAIT=540, item 105 (v); the call form: env -u KYTY_GAME_PATCH '
      'PLWAIT=540 bash C:/kyty/s288/s9/go_s9.sh <tag> - go_s9.sh unsets KYTY_GAME_PATCH itself)')
    w('')
    w('s binary: %s C:/kyty/s288/bin/kyty_emulator_f3b3aa3b.exe' % S.BIN_S)
    w('u binary: %s C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe' % S.BIN_U)
    w('')
    w('Admission row installed_before (item 374 (g), item 377 (b)(1); INST_WANT of go_s9.sh and of sc_s9.py; not the u binary): '
      'the installed C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe before every arm = %s (FS3, installed 2026-10-03T07:11:12Z; '
      'item 394: FS4 waits for done of S10)' % S.INST_WANT)
    w('')
    for t in S.SEQ:
        w('go_s9 call: PLWAIT=540 bash C:/kyty/s288/s9/go_s9.sh %s' % t)
    w('')
    w('Order (sc_s9.py --allowed): %s; made: pi_w1 pi_r1 pi_w0 pi_r0 c5_0 (refused as made); one tag per lock; the lock queue '
      'P > F > S (item 322 (g)); the series stops at the first death marker; T2 reserves t2_6 .. t2_10 only while fewer than '
      'five T2 arms count; u_1 after the T2 base and t2_cs0; the U series stops at an arm without the catalogue gates.'
      % ' '.join(S.SEQ))
    w('')
    w('## 3. The plan of every arm (go_s9.sh DRY=2, verbatim; the T2 tags in the form chosen by the scorer from c5_0 - APP, no '
      'FORM given)')
    w('')
    w('```')
    for p in plans:
        w(p)
    w('```')
    w('')
    w('## 4. Seal lines (sc_s9.py --check-seal checks each before every lock)')
    w('')
    for n in tuple(S.SEALED_NAMES) + EXTRA:
        if n == 's9/mkseal_s07.py':
            continue
        p = n if n.startswith('C:/') else R + '/' + n
        w('seal: %s %s' % (sha(p), n))
    w('')
    w('## 5. Evidence (the last output of each suite and tool)')
    w('')
    for name, p in (('fixtures sc_s9', R + '/s9/test_sc_s9.out.txt'), ('fixtures go_s9', R + '/s9/test_go_s9.out.txt'),
                    ('fixtures of item 404 on the real logs', R + '/s10/r404/test_r404.out.txt')):
        first, checks, last, sh = suite(p)
        w('- %s: %s sha256 %s; %s / %s; first line: %s' % (name, p, sh, checks, last, first))
    for name, p, key in (('mutants --only of item 404 (ident_domain, its call, the prereg row, PRIOR_*, PRED_PATH)',
                          R + '/s10/r404/mut_r404.txt', None),
                         ('mutants (the counted full run of S9b, carried; its survivor cr_inst killed by --only of rework 1)',
                          R + '/s9/mut_sc_s9c.txt', None),
                         ('mutants --only of S9b rework 1', R + '/s9b/r1/mut_screen7.txt', None),
                         ('regression on the logs of S4 and S6 and the six videos (code paths not changed by item 404)',
                          R + '/s9/regress_s9.out.txt', 'REGRESSION:'),
                         ('the level lists', R + '/s9/lvl_s9.out.txt', 'ALL DONE'),
                         ('the export of the S-cat catalogue', R + '/s9/seedexp_s9.out.txt', 'EXPORT:'),
                         ('the provenance of the detector fixtures (a fresh ffmpeg run = the cached saturations)',
                          R + '/s9/fx/provenance.out.txt', None)):
        lines = open(p, encoding='ascii', errors='replace').read().splitlines()
        tail = [x for x in lines if key and x.startswith(key)] or lines[-1:]
        w('- %s: %s sha256 %s; %s' % (name, p, sha(p), tail[-1] if tail else '-'))
    w('- mutant runs (wall): S9 and S9b about 1 534 s of the 30 min budget (s9b/r1/mutwalls.txt); item 404 --only 77 s '
      '(s10/times.txt 05:26:29Z) - in all about 1 611 s; the counted full run is not repeated (item 404 (g): --only of the '
      'changed functions, <= 10 min)')
    w('')
    for line in open(R + '/s9/seal07_tail.md', encoding='ascii').read().splitlines():
        w(line)
    text = NL.join(o) + NL
    text.encode('ascii')
    with open(OUT, 'wb') as f:
        f.write(text.encode('ascii'))
    print('seal written %s sha256 %s' % (OUT, sha(OUT)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
