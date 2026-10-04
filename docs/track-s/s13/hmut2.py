"""hmut2.py - S13a2 (HPP-498, ROADMAP item 428 (v)): hand mutants of s13/go_s13.sh, each must be killed by s13/test_go_s13.py
(rc != 0 and every expected case FAILS).  h1-h3 repeat the mutants of S13a (S9r2 observations 1-3) on the new text; h4-h7 are the
knob of item 419 (v) Z3 / item 428 (v)(1).  Output: s13/hmut2/hmut_<id>.txt and one line per mutant; ASCII.
    python hmut2.py [h1 h2 ...]      (no id: all mutants)
"""
import os
import subprocess
import sys

S13 = 'C:/kyty/s288/s13'
OUT = S13 + '/hmut2'
NL = chr(10)
MUT = [
    ('h1', 'return_failed() {' + NL + '  RETFAIL=1' + NL, 'return_failed() {' + NL + '  RETFAIL=0' + NL, ('G23', 'GL14')),
    ('h2', '(go_s13.sh seal $PRED)" > $LOCK', '(go_s13.sh)" > $LOCK', ('GL11',)),
    ('h3', 'if [ "$INST_SHA" != "$INST_WANT" ]; then', 'if false; then', ('GL13',)),
    ('h4', 'KYTY_GPU_MARKERS=0 KYTY_S_PCW=$SPCW $CLSX', 'KYTY_GPU_MARKERS=0 $CLSX', ('G18', 'G18b', 'G22', 'GL2')),
    ('h5', 'for V in $(compgen -e); do case "$V" in KYTY_FIX_*) unset "$V";; esac; done' + NL, '', ('G22', 'GL2')),
    ('h6', 'SPCW=1   #', 'SPCW=0   #', ('G18', 'G18b', 'G22', 'GL2')),
    ('h7', 'KYTY_GAME_PATCH KYTY_S_PCW KYTY_S_PCW_FORCE_MS' + NL, 'KYTY_GAME_PATCH' + NL, ('G22', 'GL2')),
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
    print('HMUT2: %s' % ('ALL KILLED' if ok else 'NOT ALL KILLED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
