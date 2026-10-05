"""mkseal_s15.py - track S, link S15a (HPP-601; ROADMAP "SESSION 122" item 511 (z)): writes the seal C:/kyty/s288/pred/14_s.md
(the seal of S15b; seal 13 stays the seal of the S13b arms) from s15/seal14_body.md and s15/seal14_tail.md, the DRY=2 plan of
every tag (go_s15.sh, no lock taken, no process of the game), the call lines, the line "installed: PENDING" and the sha256 line of
every sealed file (sc_s15.SEALED_NAMES).  Refuses (rc 5) when C:/kyty/SEALED_RUN.lock exists; refuses (rc 1) when the seal exists
(a seal is never rewritten) or when a plan does not name KYTY_S_PCW=1 once (item 428 (v)(1)).  LF, ASCII.
    python mkseal_s15.py
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
S13 = ROOT + '/s15'
SEAL = ROOT + '/pred/14_s.md'
OLD = ROOT + '/pred/13_s.md'
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
    spec = importlib.util.spec_from_file_location('sc13', S13 + '/sc_s15.py')
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)
    if S.SEAL_BASE != SEAL:
        print('STOP: sc_s15.SEAL_BASE %s is not %s' % (S.SEAL_BASE, SEAL))
        return 1
    bash = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
    env = dict(os.environ, DRY='2', PATH='/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    plans = []
    import concurrent.futures

    def dry(t):
        return subprocess.run([bash, S13 + '/go_s15.sh', t], capture_output=True, text=True, env=env, timeout=300)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:     # S15a: the 39 DRY=2 plans in parallel, in order
        runs = list(ex.map(dry, S.SEQ))
    for t, p in zip(S.SEQ, runs):
        out = p.stdout.replace('bash.exe: warning: could not find /tmp, please create!' + NL, '').strip()
        hu = ' --hold-u %s ' % S.U_RULE
        if out.count(hu) != (1 if S.SPEC[t]['group'] == 'u' else 0) or out.count('--hold-u') != out.count(hu):
            print('STOP: the plan of %s does not carry the hold rule of item 511 (z)(4) as sealed: %s' % (t, out))
            return 1
        if p.returncode != 0 or not out.startswith('PLAN %s: ' % t):
            print('STOP: the DRY=2 plan of %s failed (rc %d): %s %s' % (t, p.returncode, out, p.stderr.strip()[-300:]))
            return 1
        if out.count(' KYTY_S_PCW=1') != 1 or out.count('KYTY_S_PCW') != 1:
            print('STOP: the plan of %s does not name KYTY_S_PCW=1 exactly once (item 428 (v)(1)): %s' % (t, out))
            return 1
        plans.append(' '.join(out.split()))
    lvl = [x for x in open(ROOT + '/s13/lvl_s13.out.txt', encoding='ascii').read().split(NL)
           if x.startswith(('LIST13 ', 'IN_FS4 ', 'PLAN_FS4 ', 'IN_FS5 ', 'PLAN_FS5 ', 'COMPAT ', 'never entered'))]
    now = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    head = ['# Seal 14_s - track S link S15b (HPP-603): the fifth wave S-cat - the collection of the catalogue of the 19 known levels '
            'k_01 .. k_19 (hold 300 s), the export, the U arms u_01 .. u_19 (the hold rule 120:3000:300) and the W of Sky Garden w13 on '
            'the installed FS8 after FS8e (ROADMAP "SESSION 122" item 511 (z); item 229 (e)(1), (3), item 355 (e), item 408 (l), '
            'item 428, item 436, item 446, item 452, item 464 (d))', '',
            'Written by C:/kyty/s288/s15/mkseal_s15.py (sha256 %s) at %s by link S15a (HPP-601), before any arm of S15b.  The '
            'port of seal 13 (pred/13_s.md sha256 %s, the seal of the S13b arms, closed by S13c item 511) by item 511 (z)(3)-(5), '
            '(z)(i) and N2 of item 464 (d).  After this seal the scorer, the fixtures, the mutants, the harness, enter_scene_s15.py, '
            'the export and the list do not change (a change = a new seal); the only later document is the edition pred/14b_s.md '
            'of section 1 (the lines "installed:" and "edition: base pred/14_s.md sha256 <sha>").  S15b runs only after the review '
            'S15r (HPP-602) and the lead line accepting this seal, and after FS8e (HPP-575) and the edition.  ASCII only.' % (
                sha(os.path.abspath(__file__)), now, sha(OLD) if os.path.isfile(OLD) else 'missing'), '']
    body = open(S13 + '/seal14_body.md', encoding='ascii').read().rstrip(NL).split(NL)
    tail = open(S13 + '/seal14_tail.md', encoding='ascii').read().rstrip(NL).split(NL)
    sec2 = ['', '## 2. The list (s13/lvl_s13.out.txt, sha256 %s)' % sha(ROOT + '/s13/lvl_s13.out.txt'), ''] + \
           ['    ' + x for x in lvl]
    sec3 = ['', '## 3. The plan of every tag (go_s15.sh with DRY=2, the seal path of this seal; runs of blanks folded)', ''] + \
           ['    ' + x for x in plans]
    sec4 = ['', '## 4. The call lines (one per tag; go_s15.sh refuses a call whose PLWAIT is not its line)', ''] + \
           ['go_s15 call: PLWAIT=540 bash C:/kyty/s288/s15/go_s15.sh %s' % t for t in S.SEQ]
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
