"""mkseal_s11.py - track S, link S13a2 (HPP-498; ROADMAP "SESSION 122" item 408 (l), item 428 (v)(4)): writes the seal
C:/kyty/s288/pred/11_s.md (it replaces pred/09_s.md, not in force) from s13/seal11_body.md and s13/seal11_tail.md, the DRY=2 plan of
every tag (go_s13.sh, no lock taken, no process of the game), the call lines, the line "installed: PENDING" and the sha256 line of
every sealed file (sc_s13.SEALED_NAMES).  Refuses (rc 5) when C:/kyty/SEALED_RUN.lock exists; refuses (rc 1) when the seal exists
(a seal is never rewritten) or when a plan does not name KYTY_S_PCW=1 once (item 428 (v)(1)).  LF, ASCII.
    python mkseal_s11.py
"""
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
ROOT = 'C:/kyty/s288'
S13 = ROOT + '/s13'
SEAL = ROOT + '/pred/11_s.md'
OLD = ROOT + '/pred/09_s.md'
NL = chr(10)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    if os.path.exists(LOCK):
        print('LOCKED - nothing written')
        return 5
    if os.path.exists(SEAL):
        print('STOP: %s exists - a seal is never rewritten' % SEAL)
        return 1
    spec = importlib.util.spec_from_file_location('sc13', S13 + '/sc_s13.py')
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)
    if S.SEAL_BASE != SEAL:
        print('STOP: sc_s13.SEAL_BASE %s is not %s' % (S.SEAL_BASE, SEAL))
        return 1
    bash = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
    env = dict(os.environ, DRY='2', PATH='/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    plans = []
    for t in S.SEQ:
        p = subprocess.run([bash, S13 + '/go_s13.sh', t], capture_output=True, text=True, env=env, timeout=120)
        out = p.stdout.replace('bash.exe: warning: could not find /tmp, please create!' + NL, '').strip()
        if p.returncode != 0 or not out.startswith('PLAN %s: ' % t):
            print('STOP: the DRY=2 plan of %s failed (rc %d): %s %s' % (t, p.returncode, out, p.stderr.strip()[-300:]))
            return 1
        if out.count(' KYTY_S_PCW=1') != 1 or out.count('KYTY_S_PCW') != 1:
            print('STOP: the plan of %s does not name KYTY_S_PCW=1 exactly once (item 428 (v)(1)): %s' % (t, out))
            return 1
        plans.append(' '.join(out.split()))
    lvl = [x for x in open(S13 + '/lvl_s13.out.txt', encoding='ascii').read().split(NL)
           if x.startswith(('LIST13 ', 'IN_FS4 ', 'PLAN_FS4 ', 'IN_FS5 ', 'PLAN_FS5 ', 'COMPAT ', 'never entered'))]
    now = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    head = ['# Seal 11_s - track S link S13b (HPP-500): the collection of the catalogue of the 19 known levels k_01 .. k_19, the '
            'export, the U arms u_01 .. u_19 and the W of Sky Garden w13 (ROADMAP "SESSION 122" item 408 (e), (l), item 229 (e)(1), '
            '(3), item 355 (e), item 371 (v), item 410 (g)(6)(iii), item 414, item 419 (v) Z3, item 428)', '',
            'Written by C:/kyty/s288/s13/mkseal_s11.py (sha256 %s) at %s by link S13a2 (HPP-498, the rework of item 428 (v)), '
            'before any arm of S13b.  It replaces pred/09_s.md (sha256 %s), which is not in force (item 428 (v)(4)).  After this '
            'seal the scorer, the fixtures, the mutants, the harness, the export and the list do not change (a change = a new '
            'seal); the only later document is the edition pred/11b_s.md of section 1 (the line "installed:").  S13b runs only '
            'after the review S13r (HPP-499) and the lead line accepting this seal, and after S12d (HPP-497) and FS5e (HPP-513) '
            '(item 410 (g)(6)(iii)).  ASCII only.' % (sha(os.path.abspath(__file__)), now,
                                                     sha(OLD) if os.path.isfile(OLD) else 'missing'), '']
    body = open(S13 + '/seal11_body.md', encoding='ascii').read().rstrip(NL).split(NL)
    tail = open(S13 + '/seal11_tail.md', encoding='ascii').read().rstrip(NL).split(NL)
    sec2 = ['', '## 2. The list (s13/lvl_s13.out.txt, sha256 %s)' % sha(S13 + '/lvl_s13.out.txt'), ''] + \
           ['    ' + x for x in lvl]
    sec3 = ['', '## 3. The plan of every tag (go_s13.sh with DRY=2, the seal path of this seal; runs of blanks folded)', ''] + \
           ['    ' + x for x in plans]
    sec4 = ['', '## 4. The call lines (one per tag; go_s13.sh refuses a call whose PLWAIT is not its line)', ''] + \
           ['go_s13 call: PLWAIT=540 bash C:/kyty/s288/s13/go_s13.sh %s' % t for t in S.SEQ]
    seals = []
    for n in S.SEALED_NAMES:
        p = n if n.startswith('C:/') else ROOT + '/' + n
        seals.append('seal: %s %s' % (sha(p), n))
    sec5 = ['', '## 5. The installed binary and the sealed files', '', 'installed: PENDING', ''] + seals
    text = NL.join(head + body + sec2 + sec3 + sec4 + sec5 + [''] + tail) + NL
    text.encode('ascii')
    if os.path.exists(LOCK):
        print('LOCKED before the write - nothing written')
        return 5
    with open(SEAL, 'w', encoding='ascii', newline=NL) as f:
        f.write(text)
    print('SEAL %s sha256 %s lines %d; seal lines %d; call lines %d; plans %d (each naming KYTY_S_PCW=1 once)' % (
        SEAL, sha(SEAL), text.count(NL), len(seals), len(S.SEQ), len(plans)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
