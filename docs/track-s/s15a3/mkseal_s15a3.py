"""mkseal_s15a3.py - track S, link S15a3 (HPP-617; ROADMAP "SESSION 122" item 529 (b)(4)): writes the seal C:/kyty/s288/pred/16_s.md
from the seal C:/kyty/s288/pred/15_s.md (pinned by sha256) by exact replacements: the title, the line "Written by", the names of the
seal in force pred/14_s.md / pred/14b_s.md -> pred/16_s.md / pred/16b_s.md (45 lines: section 1, the 39 plans of section 3, section
6 V1; the 39 plans are checked against the DRY=2 plans of the new go_s15.sh), the sha256 lines of the five changed files (read now)
and one bullet of section 6 (S15a3).  Every other line of seal 15 is kept byte for byte.  Refuses (rc 5) when the lock exists, (rc 1)
when the seal 16 exists (a seal is never rewritten), when seal 15 is not the pinned one, when a file that does not change is not the
one of seal 15, or when an input is not the expected outcome.  LF, ASCII.
    python mkseal_s15a3.py
"""
import concurrent.futures
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
ROOT = 'C:/kyty/s288'
L = ROOT + '/s15a3'
OLD = ROOT + '/pred/15_s.md'
OLD_SHA = 'a2ffca701e3db0829742eed4c57e65f36d189f5945201cb61a0838ccff10fbab'
SEAL = ROOT + '/pred/16_s.md'
CHANGED = ('s15/go_s15.sh', 's15/sc_s15.py', 's15/test_sc_s15.py', 's15/mut_sc_s15.py', 's15/test_go_s15.py')
ORIG = {'s15/go_s15.sh': 'f5c1b67ce6449c85a7af18a3df897c0e882ae8ddee2f02b3aa1e568ab6a8687a',
        's15/sc_s15.py': '6b3ad9c411f7053053278bf00579076d902d0c6796bcd650a6b5ddac896438b4'}
NL = chr(10)
NAME_LINES = 45


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def rd(p):
    return open(p, 'rb').read().decode('ascii', 'replace')


def fails(p):
    return [x.split(' ')[1] for x in rd(p).splitlines() if x.startswith('FAIL ')]


def checks(p):
    c = [x for x in rd(p).splitlines() if x.startswith('checks: ')]
    return c[-1] if c else '?'


def main():
    if os.path.exists(LOCK):
        print('LOCKED - nothing written')
        return 5
    if os.path.exists(SEAL):
        print('STOP: %s exists - a seal is never rewritten' % SEAL)
        return 1
    if sha(OLD) != OLD_SHA:
        print('STOP: %s sha256 %s != %s' % (OLD, sha(OLD), OLD_SHA))
        return 1
    lines = rd(OLD).split(NL)
    sealed = dict((x.split(' ')[2], x.split(' ')[1]) for x in lines if x.startswith('seal: '))
    for n, want in sealed.items():
        if n in CHANGED:
            continue
        p = n if n.startswith('C:/') else ROOT + '/' + n
        if sha(p) != want:
            print('STOP: %s is not the file of seal 15 (%s != %s)' % (n, sha(p), want))
            return 1
    for n in CHANGED:
        if sha(L + '/orig/' + n.split('/')[-1]) != sealed[n]:
            print('STOP: s15a3/orig/%s is not the file of seal 15' % n.split('/')[-1])
            return 1
        if sha(ROOT + '/' + n) == sealed[n]:
            print('STOP: %s did not change' % n)
            return 1
    spec = importlib.util.spec_from_file_location('sc_s15n', ROOT + '/s15/sc_s15.py')
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)
    if (S.SEAL_BASE, S.SEAL_B, S.SEAL_BASE_REL) != (SEAL, ROOT + '/pred/16b_s.md', 'pred/16_s.md'):
        print('STOP: the names of sc_s15.py are %s' % [S.SEAL_BASE, S.SEAL_B, S.SEAL_BASE_REL])
        return 1
    # the inputs: the suites, the negative controls, the hand mutants of go_s15.sh, the anchors of the scorer mutants
    t_sc, t_go, t_en = L + '/test_sc_s15.out.txt', L + '/test_go_s15.out.txt', L + '/test_enter_scene_s15.out.txt'
    n_sc, n_go, h_go = L + '/negctl_sc.out.txt', L + '/negctl_go.out.txt', L + '/hmut_go.out.txt'
    anch, patch_out = L + '/anch_s15a3.out.txt', L + '/patch_names_s15a3.out.txt'
    for p, tgt in ((t_sc, 's15/sc_s15.py'), (t_go, 's15/go_s15.sh'), (t_en, 's15/enter_scene_s15.py')):
        x = rd(p)
        first = x.splitlines()[0] if x else ''
        if not x.rstrip().endswith('ALL OK') or fails(p) or not first.endswith(' sha256 ' + sha(ROOT + '/' + tgt)):
            print('STOP: %s is not ALL OK on the current %s' % (p, tgt))
            return 1
    if 'G18e' not in rd(t_go) or 'PASS G18e ' not in rd(t_go):
        print('STOP: G18e not passed in %s' % t_go)
        return 1
    if 'HMUT go: 6 of 6 killed' not in rd(h_go):
        print('STOP: the hand mutants of go_s15.sh are not 6 of 6 killed')
        return 1
    nsc, ngo = fails(n_sc), fails(n_go)
    if sorted(nsc) != ['E6', 'E6g', 'F4', 'F6b'] or 'G18e' not in ngo or ORIG['s15/sc_s15.py'] not in rd(n_sc).splitlines()[0] or \
            ORIG['s15/go_s15.sh'] not in rd(n_go).splitlines()[0]:
        print('STOP: the negative controls: sc %s, go %s' % (nsc, ngo))
        return 1
    ax = rd(anch)
    if 'mutants old 359 new 359; ids equal True' not in ax or "[('ed6_rel', 1, 1)]" not in ax or \
            'anchors with count 0 on the new code: []' not in ax:
        print('STOP: the anchors of the scorer mutants: %s' % ax)
        return 1
    # the title, the line "Written by"
    title_old = '# Seal 15_s - track S link S15b (HPP-603): '
    if not lines[0].startswith(title_old):
        print('STOP: the title of seal 15')
        return 1
    lines[0] = '# Seal 16_s - track S link S15b (HPP-603): ' + lines[0][len(title_old):]
    w = [k for k, x in enumerate(lines) if x.startswith('Written by C:/kyty/s288/s15a2/mkseal_s15a2.py ')]
    if w != [2]:
        print('STOP: the line "Written by" of seal 15 at %s' % w)
        return 1
    now = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    lines[2] = (
        'Written by C:/kyty/s288/s15a3/mkseal_s15a3.py (sha256 %s) at %s by link S15a3 (HPP-617), before any arm of S15b.  Seal 15 '
        '(pred/15_s.md sha256 %s, link S15a2, HPP-615) with the changes of ROADMAP "SESSION 122" item 529 (b)(1)-(4) only: the title '
        'and this line; the names of the seal in force pred/14_s.md / pred/14b_s.md -> pred/16_s.md / pred/16b_s.md, which the code '
        'now reads (sc_s15.py SEAL_BASE / SEAL_B / SEAL_BASE_REL, the seal-path case of go_s15.sh; item 529 (b)(1)) - section 1, the 39 '
        'plans of section 3 (the DRY=2 plans of the new go_s15.sh), section 6 V1; the sha256 lines of s15/go_s15.sh, s15/sc_s15.py, '
        's15/test_sc_s15.py, s15/mut_sc_s15.py and s15/test_go_s15.py; one bullet of section 6 (S15a3).  Every other line of seal 15 '
        'is kept byte for byte.  Seal 15 stays the document of link S15a2 and is not in force (item 529 (b)).  After this seal the '
        'scorer, the fixtures, the mutants, the harness, enter_scene_s15.py, the export and the list do not change (a change = a new '
        'seal); the only later document is the edition pred/16b_s.md (the lines "installed:" and "edition: base pred/16_s.md sha256 '
        '<sha>", item 529 (c)).  S15b runs only after the narrow review S15r2 (HPP-616) and the lead line accepting this seal, after '
        'FS8e (HPP-575) and the lead line accepting the edition 16b.  ASCII only.' % (sha(os.path.abspath(__file__)), now, OLD_SHA))
    # the names of the seal in force
    nl_idx = [k for k, x in enumerate(lines) if k != 2 and ('pred/14_s.md' in x or 'pred/14b_s.md' in x)]
    if len(nl_idx) != NAME_LINES:
        print('STOP: %d lines name the seal 14, not %d' % (len(nl_idx), NAME_LINES))
        return 1
    for k in nl_idx:
        lines[k] = lines[k].replace('pred/14b_s.md', 'pred/16b_s.md').replace('pred/14_s.md', 'pred/16_s.md')
    # the 39 plans of section 3 = the DRY=2 plans of the new go_s15.sh
    pl_idx = [k for k, x in enumerate(lines) if x.startswith('    PLAN ')]
    if len(pl_idx) != 39 or not set(pl_idx) <= set(nl_idx):
        print('STOP: %d plan lines in section 3' % len(pl_idx))
        return 1
    bash = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
    env = dict(os.environ, DRY='2', PATH='/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))

    def dry(t):
        return subprocess.run([bash, ROOT + '/s15/go_s15.sh', t], capture_output=True, text=True, env=env, timeout=120)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        runs = list(ex.map(dry, S.SEQ))
    plans = []
    for t, p in zip(S.SEQ, runs):
        out = p.stdout.replace('bash.exe: warning: could not find /tmp, please create!' + NL, '').strip()
        if p.returncode != 0 or not out.startswith('PLAN %s: link s15, seal pred/16_s.md, ' % t):
            print('STOP: the DRY=2 plan of %s (rc %d): %s %s' % (t, p.returncode, out[:200], p.stderr.strip()[-300:]))
            return 1
        plans.append('    ' + ' '.join(out.split()))
    if plans != [lines[k] for k in pl_idx]:
        bad = [t for t, a, k in zip(S.SEQ, plans, pl_idx) if a != lines[k]]
        print('STOP: the DRY=2 plans differ from the plans of seal 15 with the names 14 -> 16: %s' % bad)
        return 1
    # the sha256 lines of the changed files
    for n in CHANGED:
        s = [m for m, x in enumerate(lines) if x.startswith('seal: ') and x.endswith(' ' + n)]
        if len(s) != 1:
            print('STOP: the seal line of %s occurs %d times' % (n, len(s)))
            return 1
        lines[s[0]] = 'seal: %s %s' % (sha(ROOT + '/' + n), n)
    # one bullet of section 6
    anchor6 = '  process kyty_emulator.exe is there and the caches, GLCache and the binary are returned by sha and manifest.'
    a6 = [m for m, x in enumerate(lines) if x == anchor6]
    if len(a6) != 1:
        print('STOP: the anchor of section 6 occurs %d times' % len(a6))
        return 1
    sec6 = [
        '- S15a3, item 529 (b)(1)-(3) (HPP-617): the names of the seal in the code -> pred/16_s.md / pred/16b_s.md, written by',
        '  s15a3/patch_names_s15a3.py (sha256 %s; exact anchors with counts; s15a3/patch_names_s15a3.out.txt sha256' % sha(
            L + '/patch_names_s15a3.py'),
        '  %s): sc_s15.py the three constants SEAL_BASE, SEAL_B, SEAL_BASE_REL; go_s15.sh the seal-path case and its' % sha(patch_out),
        '  refusal text; test_sc_s15.py and test_go_s15.py the same names; mut_sc_s15.py the anchor of ed6_rel (pred/16_s.md ->',
        '  pred/15_s.md) and its comment; nothing else (s15a3/diff_names.txt sha256 %s) - the logic, the members' % sha(
            L + '/diff_names.txt'),
        '  and the constants of the rules unchanged; enter_scene_s15.py, mk_enter_s15.py, test_enter_scene_s15.py, hmut_s15.py byte for',
        '  byte of seal 15.  The generator: the port tools s15/port_s15.py + s15/patch_sc_s15.py of S15a do not reproduce sc_s15.py',
        '  (their output sha256 db3dd0794c86c1c... != 6b3ad9c411f70530... of seal 15), so the names are changed in the sealed files;',
        '  the port tools do not change.  Fixtures: test_sc_s15.py %s, ALL OK (s15a3/test_sc_s15.out.txt sha256' % checks(t_sc),
        '  %s); test_go_s15.py %s, ALL OK, with G18e - the edge of item 529 (b)(3): the seal path' % (sha(t_sc), checks(t_go)),
        '  pred/14_s.md, pred/14b_s.md, pred/15_s.md or pred/15b_s.md -> rc 1 "seal path bad" before the lock and no plan, pred/16_s.md',
        '  and pred/16b_s.md -> the DRY=2 plan naming that seal (s15a3/test_go_s15.out.txt sha256 %s);' % sha(t_go),
        '  test_enter_scene_s15.py %s, ALL OK (s15a3/test_enter_scene_s15.out.txt sha256 %s).' % (checks(t_en), sha(t_en)),
        '  Negative controls on the code of seal 15: test_sc_s15.py on sc_s15.py 6b3ad9c4... fails %s (s15a3/negctl_sc.out.txt' % (
            ', '.join(nsc)),
        '  sha256 %s); test_go_s15.py on go_s15.sh f5c1b67c... fails %d cases, G18e among them' % (sha(n_sc), len(ngo)),
        '  (s15a3/negctl_go.out.txt sha256 %s).  The hand mutants s15/hmut_s15.py go: 6 of 6 killed' % sha(n_go),
        '  (s15a3/hmut_go.out.txt sha256 %s).  The scorer mutants s15/mut_sc_s15.py: 359 of 359 anchors found on the' % sha(h_go),
        '  new code, only ed6_rel changed (s15a3/anch_s15a3.out.txt sha256 %s); no full mutant run of the scorer' % sha(anch),
        '  (item 529 (b)(2); items 84, 87 (b)(3)).  The 39 plans of section 3 = the DRY=2 plans of the new go_s15.sh (checked by this',
        '  script before the write).',
    ]
    lines = lines[:a6[0] + 1] + sec6 + lines[a6[0] + 1:]
    text = NL.join(lines)
    text.encode('ascii')
    if os.path.exists(LOCK):
        print('LOCKED before the write - nothing written')
        return 5
    with open(SEAL, 'w', encoding='ascii', newline=NL) as f:
        f.write(text)
    print('SEAL %s sha256 %s lines %d (from %s %s); names %d lines; plans 39 = DRY=2' % (
        SEAL, sha(SEAL), text.count(NL), OLD, OLD_SHA[:16], len(nl_idx)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
