"""hmut4.py - S13a4 (HPP-553, ROADMAP item 452 (d)(3)): hand mutants of s13/sc_s13.py for RC1 (item 452 (b)) and RC2 (item 452
(c)), each with several edits where the change needs them; each must be killed by s13/test_sc_s13.py (rc != 0 and every expected
case FAILS).  h13 - the class "after the arm" moved to "before the run" (every name of ADMIT_POST into ADMIT_PRE, ADMIT_POST
empty); h14 - only return_glc moved from "after the arm" to "before the run"; h15 - the field (ii) counted while "PipelinePrecache:
all pipelines created" is present; h16 - the field (ii) after the ready line only (not the later of the two); h17 - the text of
the line "no ... yet" not printed; h18 - the rows after the arm gate W again (ok_arm in members_w).  Output:
s13/hmut4/hmut_<id>.txt and one line per mutant; ASCII.
    python hmut4.py [h13 h14 ...]      (no id: all mutants)
"""
import os
import subprocess
import sys

S13 = 'C:/kyty/s288/s13'
OUT = S13 + '/hmut4'
NL = chr(10)
POST = '''ADMIT_POST = ('return_app after the arm = its copy', 'return_glc after the arm = its copy',
              'installed binary after the arm = before the arm (item 250 (b))',
              'manifest man_post_app recorded', 'manifest man_post_glc recorded',
              'app_post_copy recorded (cat/{}, the next arm restores it)')'''
PRE0 = "ADMIT_PRE = ('one attempt (--attempts 1, no warmup)',"
MUT = [
    ('h13', [(POST, 'ADMIT_POST = ()'),
             (PRE0, "ADMIT_PRE = ('return_app after the arm = its copy', 'return_glc after the arm = its copy', "
                    "'installed binary after the arm = before the arm (item 250 (b))', 'manifest man_post_app recorded', "
                    "'manifest man_post_glc recorded', 'app_post_copy recorded (cat/{}, the next arm restores it)', "
                    "'one attempt (--attempts 1, no warmup)',")],
     ('Z1', 'Z2')),
    ('h14', [("ADMIT_POST = ('return_app after the arm = its copy', 'return_glc after the arm = its copy',",
              "ADMIT_POST = ('return_app after the arm = its copy',"),
             (PRE0, "ADMIT_PRE = ('return_glc after the arm = its copy', 'one attempt (--attempts 1, no warmup)',")],
     ('Z1',)),
    ('h15', [("    if cr is not None:\n        why = 'not counted: the line", "    if False:\n        why = 'not counted: the line")],
     ('Y6',)),
    ('h16', [("    later = None if why is not None else max(rd, nb)\n", "    later = None if why is not None else rd\n")],
     ('Y4',)),
    ('h17', [("    i = 'line %d \"%s\"' % (d['line'], d['text']) if d['line'] is not None else 'none'",
              "    i = 'line %d' % d['line'] if d['line'] is not None else 'none'")],
     ('Y1',)),
    ('h18', [("    if gating_fail(r) or not r.get('entered') or not g:", "    if not ok_arm(r) or not r.get('entered') or not g:")],
     ('Z6',)),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    src = open(S13 + '/sc_s13.py', 'rb').read().decode('ascii')
    ok = True
    pick = sys.argv[1:]
    for mid, edits, want in MUT:
        if pick and mid not in pick:
            continue
        m = src
        good = True
        for a, b in edits:
            if m.count(a) != 1:
                print('%s: the target occurs %d times - not applied: %r' % (mid, m.count(a), a[:60]))
                good = False
                break
            m = m.replace(a, b)
        if not good:
            ok = False
            continue
        p = '%s/sc_%s.py' % (OUT, mid)
        open(p, 'wb').write(m.encode('ascii'))
        r = subprocess.run([sys.executable, S13 + '/test_sc_s13.py', p], capture_output=True, text=True, timeout=600)
        open('%s/hmut_%s.txt' % (OUT, mid), 'w', encoding='ascii', errors='backslashreplace', newline=NL).write(r.stdout + r.stderr)
        fails = [x.split()[1] for x in r.stdout.split(NL) if x.startswith('FAIL ')]
        killed = r.returncode != 0 and all(w in fails for w in want)
        ok &= killed
        print('%s %s rc %d; failing cases %s; expected %s' % (mid, 'KILLED' if killed else 'SURVIVED', r.returncode,
                                                             ' '.join(fails) or 'none', ' '.join(want)))
    print('HMUT4: %s' % ('ALL KILLED' if ok else 'NOT ALL KILLED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
