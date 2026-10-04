"""hmut3.py - S13a3 (HPP-537, ROADMAP item 436 (b)(5), (v)(3)): hand mutants of s13/go_s13.sh for RC5 and the seal 12, each must
be killed by s13/test_go_s13.py (rc != 0 and every expected case FAILS).  h8 - the old guard list without s12; h9 - no */IN_ARM;
h10 - one level deeper is a guard too; h11 - the edition 12b not accepted as the seal path; h12 - no guard check right before the
lock.  Output: s13/hmut3/hmut_<id>.txt and one line per mutant; ASCII.
    python hmut3.py [h8 h9 ...]      (no id: all mutants)
"""
import os
import subprocess
import sys

S13 = 'C:/kyty/s288/s13'
OUT = S13 + '/hmut3'
NL = chr(10)
GLOB = '  for G in $ROOT/*/RETURN_FAILED $ROOT/*/IN_ARM; do' + NL
MUT = [
    ('h8', GLOB, '  for G in $ROOT/s4/RETURN_FAILED $ROOT/s6/RETURN_FAILED $ROOT/s10/RETURN_FAILED $ROOT/s10/IN_ARM '
                 '$ROOT/s13/RETURN_FAILED $ROOT/s13/IN_ARM; do' + NL, ('G5', 'G22', 'GL15', 'GL16', 'GL17')),
    ('h9', GLOB, '  for G in $ROOT/*/RETURN_FAILED; do' + NL, ('G5', 'G22', 'GL12')),     # GL12: the hanging s13/IN_ARM is not a guard; the suite stops there (the arm ran)
    ('h10', GLOB, '  for G in $ROOT/*/RETURN_FAILED $ROOT/*/IN_ARM $ROOT/*/*/RETURN_FAILED $ROOT/*/*/IN_ARM; do' + NL,
     ('G5b', 'G22')),
    ('h11', '  pred/12_s.md|pred/12b_s.md) ;;' + NL, '  pred/12_s.md) ;;' + NL, ('G13', 'G19')),
    ('h12', 'if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi' + NL + 'guardfiles' + NL,
     'if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi' + NL, ('G22',)),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    src = open(S13 + '/go_s13.sh', 'rb').read().decode('ascii')
    ok = True
    pick = sys.argv[1:]
    for mid, a, b, want in MUT:
        if pick and mid not in pick:
            continue
        if src.count(a) != 1:
            print('%s: the target occurs %d times - not applied' % (mid, src.count(a)))
            ok = False
            continue
        p = '%s/go_%s.sh' % (OUT, mid)
        open(p, 'wb').write(src.replace(a, b).encode('ascii'))
        r = subprocess.run([sys.executable, S13 + '/test_go_s13.py', p], capture_output=True, text=True, timeout=900)
        open('%s/hmut_%s.txt' % (OUT, mid), 'w', encoding='ascii', newline=NL).write(r.stdout + r.stderr)
        fails = [x.split()[1] for x in r.stdout.split(NL) if x.startswith('FAIL ')]
        killed = r.returncode != 0 and all(w in fails for w in want)
        ok &= killed
        print('%s %s rc %d; failing cases %s; expected %s' % (mid, 'KILLED' if killed else 'SURVIVED', r.returncode,
                                                             ' '.join(fails) or 'none', ' '.join(want)))
    print('HMUT3: %s' % ('ALL KILLED' if ok else 'NOT ALL KILLED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
